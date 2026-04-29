# Skybit test suite

The first comprehensive test suite for Skybit. All tests run **headless**
(no display required) under `pytest`.

## Running

```bash
# install dev deps
pip install -e .[dev]

# run everything
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy pytest -q

# with coverage
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy pytest --cov=game --cov-report=term-missing

# run a single layer
pytest tests/unit -q          # fast unit tests
pytest tests/integration -q   # World tick-loop tests
pytest tests/scene -q         # App state machine
pytest tests/smoke -q         # imports + 5-second simulated runs
```

`conftest.py` sets the SDL dummy drivers automatically, so the env vars
above are belt-and-braces.

## Layout

| Folder        | What it covers                                       |
|---------------|------------------------------------------------------|
| `unit/`       | Pure functions and isolated entity classes.          |
| `integration/`| `World.update()` integration: collisions, pickups, power-up lifecycle, scoring, magnet, slowmo, grow, triple, surprise box, coin rush, persistence. |
| `scene/`      | `scenes.App` state machine + input routing.          |
| `smoke/`      | Every module imports; headless simulation runs.      |

## What's NOT tested here

- **Browser / JS / WASM**: anything that lives in `inject_theme.py` or
  the Supabase bridge in `game/leaderboard.py` / `game/play_log.py`
  (browser branch). These run only inside pygbag's Pyodide build.
- **Visual / pixel-perfect rendering**: no golden-image diffs. The
  visual layer ships via manual screenshot review.
- **Audio quality**: `audio.play_*` is mocked to no-op. The synthesis
  pipeline lives in `tools/synth_sounds.py` and ships as audited OGGs.
- **Performance / fps budget**: smoke tests time-step at 60 fps but
  don't assert wall-clock budget.

## Determinism

Every test resets `random.seed(42)` via the autouse `_seed_rng` fixture
in `conftest.py`. Spawn order, coin patterns, and surprise-box rolls are
all reproducible run-to-run — flaky tests caused by RNG drift won't
slip in.

## Adding new tests

- Pick the right folder by scope (unit > integration > scene > smoke).
- Reuse the `world` fixture for any test that needs a live `World`
  instance — it comes pre-wired with audio mocked.
- Use the `tmp_scores` fixture for anything that touches the leaderboard
  JSON, so tests don't pollute the repo root.
- Avoid hard-coded score / time expectations that depend on physics
  constants — prefer asserting *invariants* (monotonicity, range,
  signs) over golden numbers, so legitimate balance tweaks don't
  break the suite.
