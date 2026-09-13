# Skybit — Upgrade Brief

> Condensed handoff derived from `REVIEW.md` (same branch). Strategic
> input for the next model tasked with upgrading the game. Points at
> the specific files and constants to touch — no full justifications;
> see `REVIEW.md` for those.

## Verdict

**8.3 / 10 — Great. Ship, then polish.**

## Score snapshot

| #  | Category                          | Score |
|----|-----------------------------------|------:|
| 1  | Gameplay & Core Loop              |  8.5  |
| 2  | Controls & Feel                   |  9.0  |
| 3  | Visuals & Art Direction           |  9.0  |
| 4  | Sound Design                      |  7.5  |
| 5  | Replayability & Hook              |  8.0  |
| 6  | Originality                       |  8.0  |
| 7  | UI / UX & Onboarding              |  8.5  |
| 8  | Accessibility                     |  6.5  |
| 9  | Performance & Technical Execution |  9.0  |
| 10 | Software Craftsmanship            |  8.5  |
| 11 | Anti-cheat & Online Hygiene       |  8.0  |
| 12 | Documentation & Project Hygiene   |  9.0  |

Lowest scores → biggest upgrade opportunities: **Accessibility (6.5),
Sound (7.5), Replayability (8.0), Anti-cheat (8.0), Originality (8.0)**.

---

## Pros — preserve these

- **Procedural-art pipeline.** Everything drawn from code, no PNG
  sprite sheets. Files: `game/draw.py`, `game/parrot.py`,
  `game/pillar_variants.py`, `game/dollar_coin_glyphs.py`,
  `game/dollar_parrot_ghost.py`, `game/dollar_parrot_hat.py`,
  `game/surprise_box_variants.py`, `game/kfc_fries.py`.
  Module-level caches (e.g. `_grow_parrot`, `_surprise_sprite`) keep
  per-frame cost to one blit.
- **Biome day → night cycle** — single biggest variety driver.
  `game/biome.py` interpolates one phase per 5 minutes; pillars and
  clouds re-tint per phase via `game/draw.py`.
- **Power-up system (6 + Surprise Box).** `game/world.py::_on_powerup`
  + `game/config.py::POWERUP_WEIGHTS`. Surprise Box re-rolls at
  pickup. Reverse is intentionally disabled — leave it out.
- **Coin Rush.** Every 15th pillar widens the gap 30 % and packs a
  14-coin formation. `COIN_RUSH_INTERVAL`, `COIN_RUSH_GAP_BOOST`,
  `COIN_RUSH_COINS` in `game/config.py`.
- **Proof-of-play anti-cheat.** SHA-256 chain over event ledger.
  `game/_proof.py`, `game/_plausibility.py`, leaderboard funnels
  through closure-private `window.__sk` in `inject_theme.py`. Covered
  by 7 unit tests in `tests/test_plausibility.py` (all green).
- **Dual-target build (native + pygbag/WASM).** `main.py` branches on
  `sys.platform == "emscripten"`; `netlify.toml` ships the web build;
  `inject_theme.py` injects the JS bridge. Don't regress the
  browser-side audio path (`window.skyPlay`).
- **Fixed-timestep 60 FPS physics + input feel.** `GRAVITY = 1600`,
  `FLAP_V = -520`, `MAX_FALL = 700` in `game/config.py`. Tap cooldown
  gate in `game/scenes.py` deduplicates menu-tap → first-flap cascade.
- **Comments document WHY, not WHAT.** Keep this discipline on any
  new code — rationale paragraphs on non-obvious decisions, no
  line-by-line commentary.

---

## Cons — fix these

- **Flat difficulty.** `GAP_START = 170` and `SCROLL_BASE = 160` in
  `game/config.py` never change during a run. `SCROLL_MAX = 290` and
  `GAP_MIN = 115` are defined but unused — the ramp slot is empty.
- **No music layer.** `game/audio.py` is SFX-only (OGG samples).
  Long runs play against ambient silence + weather.
- **Accessibility thin.** No reduced-motion toggle, no colour-blind
  palette, no visual cue redundancy for thunder, no text scaling. Red
  Pip on green-vines pillars is borderline for deuteranopia.
- **No meta-progression.** No unlockable Pip skins, daily challenge,
  or achievements. `skybit_save.json` only stores high score.
- **Client-only leaderboard validation.** Anon Supabase key ships in
  the bundle; `public.scores` row policy accepts any insert
  (`supabase/schema.sql`). README's "soft leaderboard" caveat is
  honest but trivially bypassed by `curl`.
- **Oversized files.** `game/entities.py` 1,664 LOC, `game/intro.py`
  1,404, `game/hud.py` 1,071, `game/world.py` 823. Hard to navigate.
- **Narrow test coverage.** Only the plausibility module is tested.
  `World._step`, the spawner, biome interpolation, and the HUD state
  machine have zero unit tests.
- **Pause + ready-text overlap** in `03_pause.png` — `TAP TO FLY`
  still renders behind `PAUSED`. Pause-state should suppress the
  ready prompt.

---

## Priority upgrade actions

| # | Action | Files / constants | Lift |
|---|--------|-------------------|------|
| 1 | **Difficulty curve** — ramp `SCROLL_BASE` 160 → 220 over 5 min of `time_alive`; ramp `GAP_START` 170 → 145 over the same window. Update `_plausibility.py` ceilings accordingly. | `game/config.py`, `game/world.py`, `game/_plausibility.py` | Gameplay 8.5 → 9.0 |
| 2 | **Music layer.** One looping ambient pad per biome phase (day / sunset / night / sunrise), crossfade on `biome.phase`. WASM path uses Web Audio via `inject_theme.py`. | `game/audio.py`, `game/biome.py`, `inject_theme.py` | Sound 7.5 → 9.0 |
| 3 | **Accessibility pass.** Pause-menu toggles for reduced-motion (disables shake + sparkle bursts + biome glow pulse) and colour-blind palette (deuteranopia-safe Pip + pillar tints). Thunder cue gets a screen-edge flash. | `game/hud.py`, `game/draw.py`, `game/weather.py` | Accessibility 6.5 → 8.0 |
| 4 | **Meta-progression.** New `game/progression.py` tracks lifetime pillars in `skybit_save.json`. Unlock Pip palette variants at 50 / 200 / 500. No purchase tier. | new `game/progression.py`, `game/parrot.py`, `game/hud.py` | Replayability 8.0 → 9.0 |
| 5 | **Server-side leaderboard validation.** Move `_plausibility.check` into a Supabase Edge Function. Tighten `public.scores` RLS to deny direct insert; route writes through the function with a per-device-id rate limit. | `supabase/schema.sql`, new Edge Function, `game/leaderboard.py` | Anti-cheat 8.0 → 9.0 |
| 6 | **Split giant files.** `game/entities.py` → one module per entity (Bird, Pipe, Coin, PowerUp, Particle, FloatText). `game/intro.py` → per beat. | `game/entities.py`, `game/intro.py` | Craftsmanship 8.5 → 9.0 |
| 7 | **Broaden tests.** Determinism test on `World._step` with a seeded RNG. Phase-interpolation test on `biome`. Spawn-cooldown test on the powerup spawner. | new `tests/test_world_step.py`, `tests/test_biome_phase.py`, `tests/test_powerup_cooldown.py` | Craftsmanship 8.5 → 9.0 |
| 8 | **Pause overlay fix.** Suppress the ready-text prompt when `state == STATE_PAUSE`. | `game/scenes.py`, `game/hud.py` | UI/UX 8.5 → 9.0 |

---

## Constraints for the upgrade agent

- **No PNG sprite assets.** Procedural-only is the project's identity
  — re-skin via code, not by adding artwork files.
- **No grind-gated difficulty.** Meta-progression unlocks cosmetics
  only. Don't lock harder gaps behind playtime.
- **Keep both build targets green at all times** — native Python
  desktop *and* pygbag/WASM browser. Branch on
  `sys.platform == "emscripten"` for audio / leaderboard / storage.
- **Anti-cheat caveat stays honest.** The README's "soft leaderboard"
  paragraph must keep matching reality — if you don't actually move
  validation server-side, don't delete the caveat.
- **Comments stay WHY-only.** Match the existing rationale-style.
- **Don't re-enable the Reverse power-up.** It's intentionally out of
  `POWERUP_WEIGHTS` and out of the surprise-box pick. Keep the
  implementation in place but dormant.

## Out of scope (don't burn tokens here)

- Controller / gamepad support.
- Story / cutscene / narrative layer (wrong genre).
- Multiplayer / co-op.
- Engine port off Pygame.
- Re-enabling Reverse power-up.

---

## Reference

- Full review with justifications: **`REVIEW.md`** (same branch).
- Repo: https://github.com/ytocker/skybit/tree/v3_skybit
