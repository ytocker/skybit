# Developing Skybit

Technical guide for working on the codebase. Player-facing notes are
in [README.md](README.md).

## Local run

```bash
pip install pygame
python main.py
```

Requires Python 3.11+ and Pygame 2.x. Screen is 360 × 640 virtual
pixels (mobile portrait); the window scales up to fit your display.

## Web build

The browser build is driven by [pygbag](https://pypi.org/project/pygbag/),
which packages Pygame as a Pyodide/WASM bundle. The exact command
Netlify runs is in [`netlify.toml`](netlify.toml):

```bash
pip install 'pygbag==0.9.2'
python -m pygbag --build main.py
python inject_theme.py
```

`inject_theme.py` rewrites the generated `build/web/index.html` to
inject a closure-private `window.__sk(action, payload)` dispatcher. All
JS↔Python communication (leaderboard submit/fetch, telemetry, audio)
funnels through that single function — there are no `window.lbSubmit`
or `window.skyPlay` globals exposed for an attacker to wrap.

Live deploy: https://ytocker.github.io/skybit/ (Netlify, with
`Cross-Origin-Opener-Policy: same-origin` and a narrow CSP — see
`netlify.toml` for the full header set).

## Architecture

```
main.py                     Entry — sync + async paths for pygbag
inject_theme.py             JS bridge injected into the WASM bundle

game/
  config.py                 Physics, spawn rates, durations, weights
  scenes.py                 Scene state machine + App + tap cooldown
  world.py                  Simulation: scroll, spawn, collision, FX
  entities.py               Bird, Pipe, Coin, PowerUp, Particle, FloatText

  draw.py                   Gradient surfaces, glow caches, terrain
  parrot.py                 4-frame macaw + KFC/ghost/hat/grow variants
  pillar_variants.py        8 sandstone pillar silhouettes
  pillar_kfc.py             KFC-branded pillar overlay
  ground_variants.py        Ground-texture variants
  ambient.py                Background ambient elements
  biome.py                  Day/night palette interpolation (5-min cycle)
  weather.py                Rain/fog/thunder per biome phase

  hud.py                    Score, timers, name entry, leaderboard UI
  intro.py                  Once-per-launch cinematic
  powerup_help.py           In-game power-up hint overlay

  audio.py                  Procedural SFX + browser AudioContext bridge
  leaderboard.py            Supabase (web) / JSON (native) persistence
  play_log.py               Per-run telemetry POST

  _proof.py                 Tamper-evident SHA-256 chain hash
  _plausibility.py          Score-ceiling check (read + write paths)

  dollar_coin_glyphs.py     Procedural "$" coin glyph
  dollar_parrot_ghost.py    Ghost-parrot variant
  dollar_parrot_hat.py      Top-hat parrot variant (Triple mode)
  dollar_variants.py        $-glyph variant explorations
  kfc_fries.py              Tilted fry sprite for KFC mode
  fries_mountains.py        KFC-themed mountain silhouettes
  surprise_box_variants.py  Procedural gift-box sprites

  assets/                   Vendored fonts + KFC logo + sound OGGs only

supabase/schema.sql         public.scores table + RLS policies
tests/test_plausibility.py  7 unit tests (anti-cheat ceiling)
```

`hud.py`, `entities.py`, and `world.py` are the largest files (~1k+
LOC each); they're split-candidates if you find yourself touching them
often.

## Difficulty model

The onboarding ramp is keyed on pillars passed. The first
`PLATEAU_PIPES` pillars hold the full newbie tuning flat, then the
remaining pillars ease out (`1 - (1 - x)^2`) toward the regular
endpoints — bulk of the tightening lands in the middle pillars and
the last few settle gently rather than slamming into a last-mile
cliff. Linear interpolation was tried first and felt wrong precisely
because its largest deltas landed at the end of the ramp, exactly
where a struggling player is most fragile.

| Constant              | Newbie | Regular |
|-----------------------|-------:|--------:|
| `RAMP_PIPES`          |        |      25 |
| `PLATEAU_PIPES`       |      5 |         |
| `GAP_NEWBIE_START`    |    225 | 170 (`GAP_START`)         |
| `SCROLL_NEWBIE_BASE`  |    125 | 160 (`SCROLL_BASE`)       |
| `PIPE_SPACING_NEWBIE` |    370 | 280 (`PIPE_SPACING`)      |

After `RAMP_PIPES` the game stays at the regular endpoints forever —
`GAP_MIN = 115` and `SCROLL_MAX = 290` are defined but unused. See
`World._ramp_t` and the `_current_gap` / `_current_scroll` /
`_current_spacing` helpers in `game/world.py`.

Two forgiveness gestures live in `World._check_collisions`:

- The **ceiling clamps** Pip's position and zeros upward velocity
  instead of killing him. Bonking the top was a recurring "unfair
  death" complaint. The ground still kills.
- Pipe collision uses `BIRD_R - PIPE_HITBOX_SHRINK` (= 10 px effective,
  vs. the 14 px visible radius). Brushes don't punish you.

## Power-ups

Defined in `game/config.py`:

- `POWERUP_CHANCE = 0.24` per non-rush pillar gate (regular)
- `POWERUP_CHANCE_NEWBIE = 0.10` at the start of the run; ramps to the
  regular value on the same `_ramp_t()` curve as gap/scroll/spacing so
  the opening 25 pillars don't drown in power-ups
- `POWERUP_COOLDOWN = 5.5` seconds between spawns
- Every active kind lasts 8 seconds (`*_DURATION`)
- `POWERUP_WEIGHTS` is equally weighted across the six kinds + surprise
- `surprise` re-rolls at pickup time in `World._on_powerup`
- `reverse` is intentionally excluded; the implementation is intact

`GROW_SCALE = 1.3`, `MAGNET_RADIUS = 82`, `SLOWMO_SCALE = 0.7`,
`KFC_GAP_BOOST = 1.30` (stacks with `COIN_RUSH_GAP_BOOST`).

## Coin Rush

`COIN_RUSH_INTERVAL = 15`, `COIN_RUSH_GAP_BOOST = 1.30`,
`COIN_RUSH_COINS = 14`. Formation (sine / S / chevron / oval /
double-arc) picked randomly per rush. Power-ups are suppressed on
rush pillars.

## Leaderboard & anti-cheat

A global top-10 lives in Supabase (`public.scores`), read and written
from the browser. Native runs persist to a local JSON file
(`skybit_scores.json`).

Client-side hardening layers:

- **One closure-private dispatcher** in `inject_theme.py` —
  `window.__sk(action, payload)`. No globals to wrap.
- **Proof bundle** per submission: per-run UUID, append-only event
  ledger, rolling SHA-256 chain hash, all computed in `game/_proof.py`.
  JS recomputes the chain and refuses any payload that doesn't match.
- **Submitted score is the ledger sum**, not `world.score` — poking
  `world.score = 99999` in the console doesn't change the wire value.
- **Plausibility check** (`game/_plausibility.py`) runs on both the
  write and the read path. Rows above the ceiling are hidden from the
  displayed top-10.
- **Replay rejection**: the dispatcher tracks consumed run UUIDs in a
  closure-private set.

**Known gap**: the Supabase anon key + permissive RLS policy still
ship in the bundle. A motivated attacker can read the bundle and
`curl` rows directly into the table. The next anti-cheat priority is
moving `_plausibility.check` into a Supabase Edge Function with tight
RLS — see `UPGRADE_BRIEF.md`. The README's caveat must stay honest
about this.

## Tests

```bash
SDL_VIDEODRIVER=dummy python -m unittest discover -s tests
```

`tests/test_plausibility.py` is currently the only test file — 7 unit
tests covering the score-ceiling rules. Broader coverage (simulation,
rendering smoke tests, scene transitions) is on the wishlist.

## Build target rules

Both **native desktop** and **pygbag/WASM browser** must stay green.
Branch on `sys.platform == "emscripten"` for audio, leaderboard, and
storage paths.

- Never call `pygame.mixer` on the web path — route through the
  `window.skyPlay` action on the dispatcher (handled in `game/audio.py`).
- Fixed-timestep 60 FPS physics. `GRAVITY = 1600`, `FLAP_V = -520`,
  `MAX_FALL = 700`. Don't switch to variable-step — input feel is
  identical across targets because of this.

## Tech stack

- Python 3.11+ and Pygame 2.x
- [Pygbag](https://pypi.org/project/pygbag/) (Pyodide/WASM) for the
  browser build
- Supabase (Postgres + RLS) for the global leaderboard
- Netlify for static hosting and the build command

## Status & known gaps

Honest version of what `REVIEW.md` and `UPGRADE_BRIEF.md` already
cover internally:

- **No music layer.** `game/audio.py` is procedural SFX only — long
  runs play against ambient silence + weather cues.
- **Test coverage is narrow.** Only the anti-cheat plausibility rules
  are unit-tested.
- **Accessibility is thin.** No reduced-motion toggle, no colourblind
  palette, no thunder visual-cue redundancy, no text scaling.
- **Anti-cheat ceiling.** Supabase anon key + permissive RLS ship in
  the bundle (see Leaderboard section above).
- **No meta-progression.** `skybit_save.json` stores only the high
  score; no skins, no daily challenge, no achievements. Any future
  meta unlocks must be cosmetic-only — never gate harder gameplay
  behind playtime.

## Project docs

- [`CLAUDE.md`](CLAUDE.md) — session memory for Claude Code (project
  identity, hard rules, code map).
- [`REVIEW.md`](REVIEW.md) — full 12-category review with scores.
- [`UPGRADE_BRIEF.md`](UPGRADE_BRIEF.md) — prioritized upgrade actions
  with target files and constants.
- [`docs/`](docs/) — screenshots and asset-exploration galleries.
