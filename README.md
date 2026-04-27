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

Chain coins quickly to build a **combo multiplier** — a bouncing `X4 COMBO!` badge appears near the bottom.

---

## Power-Ups

Five power-ups spawn at equal probability (~14% per pipe, with a cooldown between spawns). Each run picks one at random:

| Power-Up | Icon | Effect | Duration |
|----------|------|--------|----------|
| **Triple** | Red mushroom | Coins worth ×3 | 8 s |
| **Magnet** | Crimson horseshoe | Pulls nearby coins to the bird | 5 s |
| **Slowmo** | Purple clock | World scrolls at half speed | 3 s |
| **KFC** | KFC bucket | Warm amber tint + score boost aura | 8 s |
| **Ghost** | Classic ghost | Bird phases through pipes | 4 s |

Each power-up shows a **floating pick-up text**, a brief particle burst, and an active **buff strip** at the bottom of the HUD with a depleting timer bar.

---

## Coin Rush

Every 15th pipe triggers a **Coin Rush** — a wider gap filled with a dense arc of 14 coins. Each rush picks from 5 layout variants: wave, S-curve, chevron, oval, or double-arc.

---

## Sound

Procedurally-synthesized SFX via the stdlib `wave` module — no audio asset files. Events: flap whoosh, coin tink, combo ping, triple fanfare, magnet hum, ghost wail, slowmo chime, KFC jingle, and a thud on impact.

---

## Evolving Scenery

The sky **and** stone pillars follow a continuous **day → golden hour → sunset → dusk → starry night → pre-dawn → sunrise → day** cycle (one full loop every ~5 minutes, independent of score). Pillars pick from **8 sandstone variants** per spawn (prayer flags, banner poles, terraces, monasteries, hero lanterns, jungle ruins, menhirs). Dynamic **weather** (rain, fog) layers over the world between biomes.

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
├── config.py              All gameplay constants (physics, spawn rates, timings)
├── biome.py               Day/night palette keyframes + phase interpolation
├── draw.py                Low-level drawing helpers: gradients, glows,
│                          mountains, clouds, ground, pillar bodies
├── parrot.py              4-frame scarlet-macaw sprite + ghost tint variant
├── entities.py            Bird, Pipe, Coin, PowerUp, Particle, FloatText
├── pillar_variants.py     8 procedural stone-pillar silhouette variants
├── world.py               Simulation: scroll, spawn, collision, pickups,
│                          difficulty ramp, screen shake, FX
├── weather.py             Rain and fog weather layer
├── hud.py                 Score, HUD pills, buff strip, combo badge,
│                          pause button, all overlay screens
├── scenes.py              State machine (Menu / Play / Pause / Stats /
│                          GameOver) + App run-loop
└── audio.py               Procedural SFX — stdlib wave, no asset files

game/assets/
├── LiberationSans-Bold.ttf     Vendored font (metric-compatible Arial)
├── LiberationSans-Regular.ttf
└── kfc_logo.png                KFC power-up logo sprite

screenshots/               Game screenshots + powerups reference sheet
tools/
├── biome_snapshots.py     Dev utility: render biome palette snapshots
└── take_screenshots.py    Dev utility: capture game state screenshots
docs/screenshots/          Screenshots used in this README
```

---

## Technical Notes

- **Screen**: 360 × 640 virtual pixels (mobile portrait). No integer upscaling.
- **Language**: Python 3, [Pygame 2.x](https://www.pygame.org/). `SRCALPHA` surfaces, `BLEND_ADD` glows, pre-computed gradient/glow caches.
- **Sprites**: all procedurally drawn — parrot, pillars, coins, power-ups, clouds, mountains, UI. Only exceptions: vendored font TTFs and the KFC logo PNG.
- **Physics**: 60 FPS; `GRAVITY = 1600 px/s²`, `FLAP_V = −520 px/s`, `MAX_FALL = 700 px/s`. Downward tilt capped at ≈41°.
- **Power-up rendering**: each power-up is drawn on an `SRCALPHA` scratch surface for clean transparency. No white-circle aura artefacts.
- **HUD polish**: score pill with dark panel + orange border; BEST and coin pills fade when bird climbs into the top 60 px so the sprite never hides behind chrome.
- **Web build**: `inject_theme.py` post-processes the pygbag-generated HTML to inject a themed loading screen and Supabase leaderboard JS bridge (`lbSubmit` / `lbFetch` / `openNameEntry`).
- **Persistence**: session best score kept in memory only; global top-10 via Supabase (browser build).
