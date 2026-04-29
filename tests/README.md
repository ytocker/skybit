# Skybit test suite

The first comprehensive test suite for Skybit. **264 passing test cases**
across 28 files, **80 % line coverage** of `game/`, runs **headless** in
under one second.

```
$ SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m pytest -q
........................................................ss.............. [ 27%]
........................................................................ [ 54%]
........................................................................ [ 81%]
..................................................                       [100%]
264 passed, 2 skipped in 0.74s
```

---

## Quickstart

```bash
# install dev dependencies (pytest + pytest-cov)
pip install -e ".[dev]"

# run everything
python -m pytest -q

# run with coverage
python -m pytest --cov=game --cov-report=term-missing

# run one layer at a time
python -m pytest tests/unit -q
python -m pytest tests/integration -q
python -m pytest tests/scene -q
python -m pytest tests/smoke -q

# run one file
python -m pytest tests/unit/test_bird.py -q

# run one test
python -m pytest tests/integration/test_magnet.py::test_pull_within_radius_moves_coin_toward_bird -v
```

`tests/conftest.py` sets `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy`
before any pygame import, so the env vars are optional in practice — they
are required when invoking pytest in CI on a machine with no display
server.

---

## Layout

```
tests/
├── conftest.py                       # shared fixtures
├── unit/                             # pure functions, isolated classes
│   ├── test_config.py                #   12 cases — constants sanity
│   ├── test_lerp.py                  #    7 cases — _lerp clamping
│   ├── test_bird.py                  #   11 cases — flap, gravity, tilt
│   ├── test_pipe.py                  #   12 cases — collision, gap geom
│   ├── test_coin.py                  #    5 cases — spin, float, wrap
│   ├── test_powerup_entity.py        #    9 cases — every kind builds
│   ├── test_biome.py                 #    9 cases — phase, palette, bucket
│   └── test_coin_patterns.py         #    9 cases — arc/line/cluster + 5 rush variants
├── integration/                      # World.update() tick loop
│   ├── test_world_init.py            #   12 cases — initial state
│   ├── test_world_update.py          #    9 cases — tick, scroll, recycling
│   ├── test_collisions.py            #   10 cases — ground/pipe/ghost/grow
│   ├── test_pickups.py               #    9 cases — coin/powerup pickup
│   ├── test_powerup_lifecycle.py     #   13 cases — activate→tick→expire (×6)
│   ├── test_surprise_box.py          #    5 cases — resolves to 1-of-6
│   ├── test_magnet.py                #    7 cases — falloff, range, no-pull
│   ├── test_slowmo.py                #    3 cases — dt scaling
│   ├── test_grow.py                  #    4 cases — bird_radius() flips
│   ├── test_triple.py                #    4 cases — coin ×1 vs ×3
│   ├── test_score.py                 #    7 cases — pillars, near-misses
│   ├── test_coin_rush.py             #    4 cases — every Nth pipe
│   └── test_persistence.py           #    9 cases — JSON save/load/cap
├── scene/                            # scenes.App state machine
│   ├── conftest.py                   # app fixture w/ play_log stubbed
│   ├── test_state_machine.py         #   13 cases — menu→play→stats→lb
│   └── test_input_routing.py         #   12 cases — keys/mouse/finger
└── smoke/                            # imports + e2e simulation
    ├── test_imports.py               #   ~20 cases — every module imports
    ├── test_headless_run.py          #    5 cases — 5 s simulated gameplay
    └── test_visual_smoke.py          #   32 cases — every draw path runs
```

---

## What each layer guarantees

### `tests/unit/` — pure logic, no World

Fast (<0.1 s), no fixture except `random.seed(42)`. Tests in this
layer fail when math or constants change — exactly the suite you want
green before any non-trivial gameplay PR merges.

**Example invariants:**
- `Bird.flap()` is a no-op on a dead bird (line `entities.py:124`).
- `Bird.update(dt)` clamps `vy` to `MAX_FALL` regardless of input.
- `Pipe.collides_circle` returns `True` inside the top pillar and
  `False` in the gap centre — guarantees that the rect-rect collision
  used at runtime keeps doing what its name says.
- `_lerp(a, b, t)` saturates outside `[0, 1]` rather than extrapolating.
- `phase_for_time(t + CYCLE_SECONDS) == phase_for_time(t)` — biome
  cycle is periodic.

### `tests/integration/` — World tick loop

Spawns a fresh `World` per test (via the `world` fixture) and exercises
the actual `World.update(dt)` integration. The bulk of game-logic
coverage lives here.

**Example invariants:**
- After `_check_pickups()`, every collected coin's `collected` flag is
  `True` and `world.score` increased by 1 (or 3 if `triple_timer > 0`).
- All 6 power-ups: pickup sets `<kind>_timer == DURATION`; ticking the
  world for `DURATION + 0.5 s` (with the bird held alive in mid-air)
  drops the timer to `0` and clears the corresponding `bird.<flag>`.
- The SURPRISE box increments `powerups_picked["surprise"]` AND one of
  the six real-kind counters; over 600 trials the resolved kind is
  uniform within ±20 %.
- Magnet pull: a coin at distance 20 px moves further than one at
  60 px under the same `dt`; coins past `MAGNET_RADIUS` don't move.
- Slowmo: pipe scroll over 1 s at `slowmo_timer > 0` is `0.7 ×` the
  no-slowmo run — bird physics stay at full speed.
- Native JSON leaderboard: corrupt input returns `[]`; submit caps at
  the top 10; sort is descending.

### `tests/scene/` — App state machine

Verifies the input routing and state transitions in `scenes.App`. Stubs
`play_log.log_run` to a no-op coroutine so the asyncio create_task in
`_on_death` doesn't blow up when there's no event loop.

**Example invariants:**
- `STATE_MENU + SPACE → STATE_PLAY`.
- Native (`sys.platform != "emscripten"`) post-stats path: a score of
  `0` short-circuits to `STATE_LEADERBOARD`; a qualifying score routes
  through `STATE_NAMEENTRY`.
- `_qualifies_for_top10`: `score == 0` is always `False`; `score`
  strictly greater than the bottom of a full top-10 qualifies; an
  exact tie does not.
- A `FINGERDOWN` followed by a synthetic `MOUSEBUTTONDOWN` within
  `_finger_dedup_window` (0.5 s) is dropped — touch events don't
  double-fire on mobile.

### `tests/smoke/` — imports + visual paths + sim

The "did anything explode" layer. Imports every module under `game/`,
runs 5 seconds of simulated gameplay, and exercises every `draw_*`
function (HUD scenes, all 7 PowerUp kinds, every Pipe seed-variant,
every Coin spin phase, every parrot variant — fried/ghost/hat/normal).

These tests **don't assert pixel content** — only that `draw()` calls
return without raising. Their job is line-level coverage of the
visual layer that wouldn't otherwise be reachable headlessly.

---

## Coverage map

```
Name                            Stmts   Miss  Cover
---------------------------------------------------
game/world.py                     482     10    98%   ← gameplay heart
game/config.py                     35      0   100%
game/biome.py                      33      1    97%
game/parrot.py                    200      0   100%
game/dollar_variants.py           106      0   100%
game/surprise_box_variants.py     121      0   100%
game/kfc_fries.py                  79      3    96%
game/weather.py                   155     12    92%
game/draw.py                      324     32    90%
game/hud.py                       592     65    89%
game/entities.py                  435     55    87%
game/dollar_parrot_ghost.py       117     36    69%
game/pillar_variants.py           494    168    66%
game/scenes.py                    318    117    63%
game/dollar_parrot_hat.py         132     55    58%
game/dollar_coin_glyphs.py         88     50    43%
game/leaderboard.py               108     74    31%   ← browser-only branch
game/audio.py                     114     81    29%   ← native mixer (dummy mode)
game/play_log.py                   40     33    18%   ← browser-only
---------------------------------------------------
TOTAL                            3973    792    80%
```

Modules below 50 % are dominated by **code paths the tests can't
reach**: the browser/JS branches in `leaderboard.py` and `play_log.py`,
and the real-mixer branches in `audio.py` (gated off when SDL runs in
dummy mode). These ship via manual screenshot / playthrough on the
deployed pygbag build.

CI's `--cov-fail-under=80` gate keeps regressions from sneaking the
overall number down.

---

## Determinism

The `_seed_rng` autouse fixture in `tests/conftest.py` calls
`random.seed(42)` before every test, so:

- Pipe gap-Y values, coin-pattern picks, surprise-box rolls,
  power-up spawn rolls, particle velocities — every random draw — are
  reproducible across runs.
- The "does this test sometimes fail on CI but pass locally?" class of
  bug is engineered out at the suite level.

To verify in your shell:

```bash
for i in 1 2 3; do
  python -m pytest -q | tail -1
done
# 264 passed, 2 skipped in 0.74s
# 264 passed, 2 skipped in 0.73s
# 264 passed, 2 skipped in 0.75s
```

---

## What's NOT in scope

| Area                        | Why not                                            |
|-----------------------------|----------------------------------------------------|
| Browser / JS / WASM         | `inject_theme.py`, `skyPlay()`, the Supabase bridge, the device-UUID localStorage code — only run inside pygbag's Pyodide build. Not exercisable from CPython. |
| Pixel-perfect rendering     | No golden-image diffs. Visual changes ship via manual screenshot review on PRs. The smoke layer asserts that draws don't *crash*, not that they look right. |
| Audio quality               | `audio.play_*` is mocked to no-op. The synthesis pipeline lives in `tools/synth_sounds.py` and is audited by ear, not by spectrum. |
| FPS / wall-clock budget     | Smoke tests run at simulated 60 fps but don't assert real-time performance. |
| Property-based / fuzz tests | A natural next step (the autouse-seed fixture composes well with `hypothesis`), but the parametrized tests already cover the obvious edge cases. |

---

## Adding a new test

Worked example — adding a test that "magnet must not pull a coin past
the bird":

```python
# tests/integration/test_magnet.py
def test_magnet_does_not_overshoot(world):
    """A coin pulled toward the bird should approach but not pass through
    when dt is small enough."""
    world.magnet_timer = 5.0
    coin = Coin(world.bird.x + 30, world.bird.y)
    world.coins.append(coin)
    for _ in range(60):
        world._apply_magnet(1 / 60)
    # Coin should be near (but not past) the bird's x.
    assert coin.x >= world.bird.x - 5
```

Pattern:

1. Pick the right folder. Pure math? `unit/`. Touches `World.update`?
   `integration/`. State transitions? `scene/`. Coverage filler? `smoke/`.
2. Reuse fixtures. The `world` fixture gives you a fresh `World` with
   audio muted. The `tmp_scores` fixture re-routes the leaderboard JSON
   to a temp dir.
3. Assert *invariants*, not magic numbers. Tests that read like "score
   is always non-negative" or "timer monotonically decreases" survive
   balance tweaks. Tests that read like "score is exactly 47 after
   2.3 s" do not.
4. Don't manually `random.seed()` — the autouse fixture already did it.
   Re-seeding inside a test only makes sense for distribution checks
   (see `test_surprise_distribution_roughly_uniform`).

---

## Continuous integration

`.github/workflows/tests.yml` runs on every push and PR to `main`,
`v3_skybit`, and `v3_skybit_testing`. It:

1. Installs SDL2 system libraries (`libsdl2-dev`, `libsdl2-mixer-dev`,
   `libsdl2-ttf-dev`, `libfreetype6-dev`).
2. Installs the project with dev extras: `pip install -e ".[dev]"`.
3. Runs `pytest --cov=game --cov-report=term-missing --cov-fail-under=80 -q`
   under `SDL_VIDEODRIVER=dummy` / `SDL_AUDIODRIVER=dummy`.

A failing build means: tests broke, OR coverage dropped below 80 %.

---

## Troubleshooting

**`pygame.error: font not initialized`** — your test renders text
without `pygame.font.init()`. Use the `surface` fixture in
`tests/smoke/test_visual_smoke.py` (it inits both display + font), or
add `pygame.font.init()` at the top of your test.

**`RuntimeError: There is no current event loop`** — your test
exercises `scenes.App._on_death` without stubbing
`game.play_log.log_run`. Use the `app` fixture in
`tests/scene/conftest.py` — it patches `log_run` to an awaitable
no-op.

**Coin / pipe count off by one or two** — `World()` spawns 3 initial
pipes (and their associated coin patterns) at construction. Either
clear the lists explicitly (`world.pipes.clear(); world.coins.clear()`)
or add to whatever's already there.

**A timer test "fails" but the value looks right** — the bird probably
died mid-loop. Power-up timers only decay while `not world.game_over`.
Hold the bird alive each frame:
```python
world.bird.y = H * 0.5
world.bird.vy = 0
world.update(dt)
```
or use the `_burn_timer` helper in
`tests/integration/test_powerup_lifecycle.py`.
