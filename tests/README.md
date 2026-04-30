# Skybit — merge-safety tests

A small suite (30 cases across 25 functions) whose only job is to
**fail loudly when a merge breaks the game**, and stay green for
legitimate changes like "raise TRIPLE_DURATION from 8 → 10 seconds".

Runs in under a second. No coverage gate. No granular invariants.

```
$ python -m pytest -q
..............................                                        [100%]
30 passed in 0.3s
```

## What it checks

Three layers, each with a different question:

| File                  | Question                                         | Cases |
|-----------------------|--------------------------------------------------|-------|
| `test_boot.py`        | Does the game still **load**?                    | 7     |
| `test_e2e.py`         | Does the game still **play**?                    | 16    |
| `test_contracts.py`   | Did we silently break a **cross-module API**?    | 7     |

### `test_boot.py` — does it load?

- Every `game/*.py` imports without error.
- `main.py` parses (we don't run it — it would block on the event loop).
- `App()` constructs and reaches `STATE_MENU`.
- One render frame on the menu doesn't raise.
- Every sound file referenced by `audio._SOUND_FILES` exists.
- Font + KFC logo files exist.

If any of these fail, the merge has bricked the game before you can
even tap. They run in <100 ms.

### `test_e2e.py` — does it play?

Scripted gameplay sessions, asserting only "no exception" — not
specific scores, durations, or numeric outcomes:

- 30 s of no-input free-fall completes.
- 30 s of random flapping doesn't crash.
- 60 s of regular flapping doesn't crash.
- Full state round-trip: menu → play → death → stats → render.
- Pause toggle mid-play preserves world state.
- All 6 power-ups: pickup, hold the bird mid-air, tick past expiry.
- 50 SURPRISE-box pickups all resolve cleanly.
- A coin-rush triggers correctly when enough pipes spawn.
- Keyboard / mouse / finger inputs each route into the play state.
- Native leaderboard round-trip: write, read, re-read after "restart".
- A corrupt leaderboard JSON does **not** crash the game on next launch.

### `test_contracts.py` — did we silently break an interface?

Cross-module contracts that no single module's tests would catch:

- `play_log._build_payload` reads attributes that still exist on `World`.
- Every `audio.play_X(...)` call in `world.py` resolves to a real
  function in `game.audio`.
- Every kind in `POWERUP_WEIGHTS` has a matching `if kind == "..."`
  handler in `world.py` (and vice-versa, except `surprise`).
- Every `POWERUP_WEIGHTS` kind constructs and draws.
- All 7 `STATE_*` constants are still exported from `game.scenes`.
- Leaderboard JSON schema is still `{"name": str, "score": int}`
  on disk.
- `game.config` still exposes every constant `world.py` imports from it.

## Deliberately NOT in scope

These are **change-detectors**, not breakage-detectors. Including them
trains contributors to ignore CI red:

- Numeric assertions like "score == 9 after 3 coins under triple".
- Timing assertions like "ratio between slowmo and normal scroll == 0.7".
- Specific RNG-derived outcomes ("after seed 42, pipe[0].gap_y == 312").
- Pixel-perfect rendering checks.
- FPS / wall-clock budgets.
- Specific power-up duration values (the whole reason the suite stays
  green when the user tweaks balance).

## Quickstart

```bash
pip install -e ".[dev]"
python -m pytest -q
```

`tests/conftest.py` forces `SDL_VIDEODRIVER=dummy` and
`SDL_AUDIODRIVER=dummy` before any pygame import, so no env vars
required.

## CI

`.github/workflows/tests.yml` runs `pytest` on every push + PR to
`main`, `v3_skybit`, or `v3_skybit_testing`, plus a separate
`pygbag-build` job that compiles the WASM bundle — because if pygbag
won't build, **nothing ships to production**, and that's the most
important "did we break something on merge" check there is.

## Adding a test

Before you write one, ask: **"if a contributor changes a balance
constant by 10 %, will my new test fail?"**

- If yes — it's a granular test. Don't add it here. (Add a doc comment
  next to the constant if you want to record the intent.)
- If no — go for it. Put it in the file that matches your question:
  *load*, *play*, or *contract*.

Reuse `world` (fresh `World`) and `app` (fresh `App` with telemetry
stubbed) fixtures from `conftest.py`.
