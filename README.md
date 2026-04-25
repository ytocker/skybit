# Skybit — Pocket Sky Flyer

A colorful Flappy-style casual arcade game. Fly a **vivid scarlet-macaw parrot** through stone pillars, collect glowing coins, and grab the rare mushroom for a **3× coin multiplier** that lasts 8 seconds. Built in **Python** with Pygame — procedural graphics, smooth gradients, soft glows, no pixel art.

<table>
<tr>
  <td align="center"><img src="docs/screenshots/01_start_between_pillars.png" width="200"><br><sub><b>Start of a run</b><br>day biome, bird approaching the first pillars</sub></td>
  <td align="center"><img src="docs/screenshots/02_coins_run.png"             width="200"><br><sub><b>Golden hour</b><br>bird about to grab a coin trail</sub></td>
</tr>
<tr>
  <td align="center"><img src="docs/screenshots/03_night_powerup.png"         width="200"><br><sub><b>Starry night</b><br>3× mushroom power-up next to the bird</sub></td>
  <td align="center"><img src="docs/screenshots/04_glide_sunrise.png"         width="200"><br><sub><b>Sunrise</b><br>bird gliding past a different pillar</sub></td>
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

Press **Space / Up / W** or click to flap. A pulsing **TAP TO FLY** prompt holds the world still for a moment when a run starts, so you can orient before the first pillar scrolls in.

| Action       | Input                          |
|--------------|--------------------------------|
| Flap         | Space · Up · W · Click         |
| Quit         | Esc                            |

### Sound

Every action has a procedurally-synthesized cue: flap whoosh, coin tink, combo ping, triple-coin arpeggio during 3X, mushroom fanfare, and a descending thud on impact. No asset files — everything is generated with the stdlib `wave` module at startup and falls back silently if the system has no audio device.

### Scoring

| Event                              | Points |
|------------------------------------|--------|
| Pass a pipe                        | +1     |
| Collect a coin                     | +1     |
| Collect a coin while 3× is active  | +3     |

Chain coins quickly to build a **combo multiplier** — a bouncing `X4 COMBO!` badge appears near the bottom of the screen.

### The Mushroom Power-Up

A red-capped mushroom occasionally spawns in the gap between pillars (roughly 1-in-9 chance, with a cooldown). Grab it to:

- Activate **3× POWER** for 8 seconds — coins worth +3 each
- Trigger a radial sparkle burst and a brief time-slow
- See an orange/gold aura glow around the parrot for the duration
- Watch a timer bar below the score drain in real time

### Leaderboard

Cracking the **top 10** pops up an arcade-style name-entry screen after Game Over. Click the on-screen keyboard (or type — A–Z, Backspace, Enter) to pick three initials. Your entry is sorted into the list and persisted to `skybit_scores.json` next to the game.

### Difficulty

- **Score 0–20**: wide gaps, relaxed scroll speed
- **Score 20–35**: gaps tighten, speed ramps up
- **Score 35+**: near-minimum gap, maximum scroll speed

### Evolving scenery

The sky **and** the stone pillars follow a continuous **day → golden hour → sunset → dusk → starry night → pre-dawn → sunrise → day** cycle. One full cycle every **5 minutes of gameplay** (real time, independent of score), interpolated smoothly. Pillars also vary — every pipe spawns one of 8 sandstone-pillar variants picked from its seed, with distinct silhouettes and decorations (prayer flags, banner poles, terraces with cascading vines, monasteries, hero lanterns, jungle-ruin masonry, menhirs).

---

## Project Structure

```
main.py                    Entry point
game/
├── config.py              Gameplay constants (physics, spawn rates, timings)
├── biome.py               Day/night palette keyframes + phase interpolation
├── draw.py                Low-level drawing: gradient surfaces, glow caches,
│                          mountains, clouds, ground, stone-pillar bodies
├── parrot.py              4-frame scarlet-macaw w/ aviator sunglasses
├── entities.py            Bird, Pipe, Coin, Mushroom, Particle, FloatText
├── world.py               Simulation: scroll, spawn, collision, pickups,
│                          difficulty ramp, shake, pickup FX
├── hud.py                 Score, best, coin count, 3X timer, combo badge,
│                          pause button, leaderboard, game-over overlay
├── nameentry.py           Arcade-style 3-letter initials keyboard (top-10)
├── scenes.py              Scene state machine (Menu / Play / NameEntry /
│                          GameOver) + App
├── storage.py             Top-10 leaderboard persistence (JSON file)
└── audio.py               Procedural SFX — stdlib wave module, no asset files
```

---

## Technical Notes

- **Screen**: 360 × 640 virtual pixels (mobile portrait). Smooth graphics, no integer upscaling.
- **Language**: Python 3, [Pygame 2.x](https://www.pygame.org/). Rendered with `SRCALPHA` surfaces, `BLEND_ADD` glows, pre-computed gradient/glow caches for performance.
- **Sprites**: everything — parrot, pillars, coins, mushroom, clouds, mountains, UI — is drawn procedurally (no image files).
- **Graphics polish**: radial glows around coins, soft drop shadows on pillars, antialiased parrot silhouette with 4 wing-cycle frames and a 1-px dark outline, **three-layer parallax mountains** (back / far / near), **five hand-tuned cloud silhouettes** picked per-slot so the sky doesn't repeat, spring-decay screen shake, gravity particles. Per-pillar erosion-crack seed so adjacent columns don't share horizontal seams.
- **HUD polish**: centered score sits on a soft dark-gradient ellipse so digits stay legible against any background. The **BEST** and **coin** pills in the top corners fade out when the bird climbs into the upper 60 px, so the sprite never disappears behind UI chrome.
- **Audio**: procedurally-synthesized SFX via the stdlib `wave` module (no asset files). Events: flap, coin, coin-combo, triple-coin (during 3X), mushroom fanfare, impact thud, game-over sting.
- **Physics**: fixed-timestep update at 60 FPS; `GRAVITY = 1600 px/s²`, `FLAP_V = -520 px/s`, `MAX_FALL = 700 px/s`. Downward tilt capped at ≈41° so fast falls don't read as already-crashing. 1-second "TAP TO FLY" freeze at round start.
- **Coin pickup**: **localized** gold/white sparkle particles + "+1" / "+3" floating text (the "+3" is oversized and offset further from the bird so the 3X aura doesn't swallow it). No full-screen flash.
- **Persistence**: high score saved to `skybit_save.json`, top-10 leaderboard to `skybit_scores.json`.
