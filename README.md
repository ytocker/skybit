# Skybit — Pocket Sky Flyer

A colorful Flappy-style casual arcade game. Fly a **vivid scarlet-macaw parrot** through stone pillars, collect glowing coins, and grab power-ups for wild effects. Built in **Python** with Pygame — procedural graphics, smooth gradients, no pixel art.

<table>
<tr>
  <td align="center"><img src="docs/screenshots/01_start_between_pillars.png" width="200"><br><sub><b>Start of a run</b><br>day biome, bird approaching the first pillars</sub></td>
  <td align="center"><img src="docs/screenshots/02_coins_run.png"             width="200"><br><sub><b>Golden hour</b><br>bird about to grab a coin trail</sub></td>
</tr>
<tr>
  <td align="center"><img src="docs/screenshots/03_night_powerup.png"         width="200"><br><sub><b>Starry night</b><br>3× mushroom power-up next to the bird</sub></td>
  <td align="center"><img src="docs/screenshots/04_glide_sunrise.png"         width="200"><br><sub><b>Sunrise</b><br>bird gliding past a different pillar variant</sub></td>
</tr>
</table>

---

## Run

```bash
pip install pygame
python main.py
```

Requires Python 3.9+ and Pygame 2.x.

---

## How to Play

Press **Space / Up / W** or click/tap to flap. A pulsing **TAP TO FLY** prompt holds the world still for a moment when a run starts.

| Action | Input                  |
|--------|------------------------|
| Flap   | Space · Up · W · Click |
| Pause  | P · Esc                |
| Quit   | Esc (from menu)        |

---

## Scoring

| Event                              | Points |
|------------------------------------|--------|
| Pass a pipe                        | +1     |
| Collect a coin                     | +1     |
| Collect a coin while 3× is active  | +3     |

---

## Power-Ups

Seven power-ups spawn at equal probability (~14% per pipe, with a 5.5 s cooldown between spawns):

| Power-Up | Icon | Effect | Duration |
|----------|------|--------|----------|
| **Triple**   | Red mushroom        | Coins worth ×3                            | 8 s  |
| **Magnet**   | Crimson horseshoe   | Pulls nearby coins to the bird            | 8 s  |
| **Slowmo**   | Purple clock        | World scrolls at 70 % speed               | 8 s  |
| **KFC**      | KFC bucket          | Bird turns into a fried-chicken parrot    | 12 s |
| **Ghost**    | Phantom             | Bird phases through pipes                 | 6 s  |
| **Grow**     | Mario super-mushroom | Bird grows 1.5× (visual + collision)     | 6 s  |
| **Surprise** | Wrapped gift box    | Resolves at pickup to one of the six above | — |

The **Surprise** box is a wrapped red present with a gold cross-ribbon, bow on top, and a cream "?" centred on the front face. On pickup it picks one of the six "real" power-ups uniformly at random and plays that effect's sound — no separate surprise SFX.

Every power-up shows a **floating pick-up text**, a brief particle burst, and an active **buff strip** at the bottom of the HUD with a depleting timer bar.

---

## Coin Rush

Every 15th pipe triggers a **Coin Rush** — a wider gap (×1.30) filled with a dense arc of 14 coins. Each rush picks from 5 layout variants: wave, S-curve, chevron, oval, or double-arc.

---

## Run Summary

After death the game lands on a **Stats screen** (gold-on-red theme) with the run's score, best, and a stack of stat rows: Time alive, Coins, Pillars cleared, Power-ups grabbed, Near misses. The screen waits for a tap before continuing — no auto-advance. Mountain silhouettes layer behind the cards on the same parallax used by the menu.

If the score qualifies for the global top 10, a **WELCOME TO TOP 10!** name-entry screen appears (browser build only) before the leaderboard view. SKIP and SUBMIT both render as clickable buttons.

---

## Sound

Curated CC0 OGG samples played through two backends:

* **Native (desktop / pygbag main thread)** — `pygame.mixer.Sound` loads each OGG once at init and plays through mixer channels. A small voice-limiter caps concurrent plays of high-frequency events (coin / coin_triple / flap) at 2 channels so a 14-coin rush doesn't muddy.
* **Browser (pygbag / Pyodide)** — every `play_X()` routes through `window.skyPlay(name, volume)` (defined in `inject_theme.py`) which fetches the OGG files copied into `build/web/sounds/` at build time and plays them through Web Audio.

Both backends play at neutral pitch and degrade silently when the audio device can't be opened (headless snapshots, missing JS helper, etc.).

Events: flap, coin, coin triple, triple-coin pickup, magnet, slowmo, ghost wail, grow, KFC, thunder, poof, death, gameover.

---

## Leaderboard & Telemetry

Two Supabase tables, both browser-only. Native runs are a silent no-op for
the global path and just keep their session-best score in memory.

* **Leaderboard (`public.scores`)** — global top 10, read + write.
  `inject_theme.py` injects a JS bridge (`lbSubmitStart` / `lbFetchStart` /
  `openNameEntry`) into the pygbag-generated HTML. `game/leaderboard.py`
  resolves the bridge at runtime with a native fallback (local JSON file
  `skybit_scores.json`).
* **Per-run telemetry (`public.plays`)** — write-only from the game; one
  row per *completed* run with score, duration, coins, pillars, near
  misses, and the per-power-up pickup dict. Fired fire-and-forget from
  `scenes._on_death()` via `game/play_log.py` → `window.skyLogPlayStart`.
  Players are identified only by an anonymous **device UUID** generated
  client-side and persisted in `localStorage` (`skybit_device_id`). **No
  IP, no user-agent, no PII.**

The full SQL (table definitions + RLS policies) lives in
[`supabase/schema.sql`](supabase/schema.sql) — paste it into the Supabase
dashboard SQL editor once per environment.

---

## Evolving Scenery

The sky **and** stone pillars follow a continuous **day → golden hour → sunset → dusk → starry night → pre-dawn → sunrise → day** cycle (one full loop every ~5 minutes, independent of score). Pillars pick from **8 sandstone variants** per spawn (prayer flags, banner poles, terraces, monasteries, hero lanterns, jungle ruins, menhirs). Dynamic **weather** (rain, fog, thunder) layers over the world between biomes.

---

## Difficulty Ramp

| Score range | Gap size    | Scroll speed |
|-------------|-------------|--------------|
| 0 – 20      | Wide        | Relaxed      |
| 20 – 35     | Tightening  | Ramping      |
| 35+         | Near-minimum | Maximum     |

---

## Project Structure

```
main.py                    Entry point (native + pygbag/WASM)
inject_theme.py            Post-build script: injects themed loading screen
                           and Supabase leaderboard JS into the pygbag HTML
netlify.toml               Netlify deployment config
pyproject.toml             Project metadata

game/
├── config.py                  All gameplay constants (physics, spawn rates, timings)
├── biome.py                   Day/night palette keyframes + phase interpolation
├── draw.py                    Low-level drawing helpers: gradients, glows,
│                              mountains, clouds, ground, pillar bodies
├── parrot.py                  4-frame scarlet-macaw sprite + ghost/KFC tints
├── entities.py                Bird, Pipe, Coin, PowerUp, Particle, FloatText
├── pillar_variants.py         8 procedural stone-pillar silhouette variants
├── world.py                   Simulation: scroll, spawn, collision, pickups,
│                              difficulty ramp, screen shake, FX
├── weather.py                 Rain, fog, thunder weather layers
├── hud.py                     Score, HUD pills, buff strip, pause button,
│                              mountain silhouette, all overlay screens
├── scenes.py                  State machine (Menu / Play / Pause / Stats /
│                              NameEntry / Leaderboard / GameOver) + run-loop
├── audio.py                   CC0 OGG playback (native mixer + web audio)
├── leaderboard.py             Global top-10 bridge (browser) + native fallback
├── kfc_fries.py               KFC fry-carton sprite
├── dollar_coin_glyphs.py      Bold "$" coin face
├── dollar_variants.py         Coin design auditions (review-only)
├── dollar_parrot_hat.py       Hat-on-parrot auditions (review-only)
├── dollar_parrot_ghost.py     Ghost-tint auditions (review-only)
└── surprise_box_variants.py   Gift-box auditions for the SURPRISE icon
                               (CROSS variant is wired into entities.py)

game/assets/
├── LiberationSans-Bold.ttf       Vendored font (metric-compatible Arial)
├── LiberationSans-Regular.ttf
├── kfc_logo.png / kfc_logo.jpg   KFC power-up logo sprite
└── sounds/                       CC0 OGG samples + CREDITS.md

tools/
├── biome_snapshots.py            Render biome palette snapshots
├── take_screenshots.py           Capture in-game state screenshots
├── kfc_fries_preview.py          Render the KFC fry variants
├── dollar_coin_preview.py        Render the $ coin variants
├── dollar_icon_preview.py        Render dollar-icon comparison sheet
├── dollar_parrot_hat_preview.py  Render hat-on-parrot variants
├── dollar_parrot_ghost_preview.py Render ghost-tint variants
├── render_grow_*.py              Render Mario-mushroom (GROW) variants
├── surprise_box_preview.py       Render the gift-box variants
├── synth_sounds.py               Procedural OGG sample generator
├── build_sound_candidates.py     Curate CC0 sound candidate sets
└── render_sound_demo.py          Render an audible sound walkthrough

docs/
├── screenshots/                  Screenshots used in this README
└── *.png                         Variant-audition reference renders
```

---

## Technical Notes

- **Screen**: 360 × 640 virtual pixels (mobile portrait). No integer upscaling.
- **Language**: Python 3, [Pygame 2.x](https://www.pygame.org/). `SRCALPHA` surfaces, `BLEND_ADD` glows, pre-computed gradient/glow caches.
- **Sprites**: all procedurally drawn — parrot, pillars, coins, power-ups, gift box, clouds, mountains, UI. Only exceptions: vendored font TTFs and the KFC logo bitmap.
- **Physics**: 60 FPS; `GRAVITY = 1600 px/s²`, `FLAP_V = −520 px/s`, `MAX_FALL = 700 px/s`. Downward tilt capped at ≈41°.
- **Power-up rendering**: each power-up is drawn on an `SRCALPHA` scratch surface for clean transparency. The SURPRISE box renders into a 64-px scratch and is `smoothscale`-cached down to the 28-px footprint, so curves and the centre "?" stay crisp.
- **HUD polish**: score pill with dark panel + orange border; BEST and coin pills fade when the bird climbs into the top 60 px so the sprite never hides behind chrome. Symmetric trophy emblem in the HUD.
- **Web build**: `inject_theme.py` post-processes the pygbag-generated HTML to inject a themed loading screen and the Supabase leaderboard JS bridge (`lbSubmit` / `lbFetch` / `openNameEntry`).
- **Persistence**: session best score kept in memory only; global top-10 via Supabase (browser build); native runs use a local JSON fallback.
