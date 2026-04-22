# Skybit — Pocket Sky Flyer

A colorful Flappy-style casual arcade game. Fly a **vivid scarlet-macaw parrot** through Zhangjiajie-style stone pillars, collect glowing coins, and grab the rare mushroom for a **3× coin multiplier** that lasts 8 seconds. Built in **Python** with Pygame — procedural graphics, smooth gradients, soft glows, no pixel art.

<p align="center">
  <img src="docs/screenshots/gameplay.png" width="340" alt="Gameplay">
  <img src="docs/screenshots/mushroom.png"  width="340" alt="3X Power">
</p>

---

## Run

```bash
pip install pygame
python main.py
```

Requires Python 3.9+ and Pygame 2.x.

---

## How to Play

Press **Space / Up / W** or click to flap. Survive as long as possible, rack up points by passing pipes and collecting coins.

| Action       | Input                          |
|--------------|--------------------------------|
| Flap         | Space · Up · W · Click         |
| Quit         | Esc                            |

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

<p align="center">
  <img src="docs/screenshots/nameentry.png" width="280" alt="Name entry">
  <img src="docs/screenshots/gameover.png"  width="280" alt="Leaderboard on Game Over">
</p>

### Difficulty

- **Score 0–20**: wide gaps, relaxed scroll speed
- **Score 20–35**: gaps tighten, speed ramps up
- **Score 35+**: near-minimum gap, maximum scroll speed

### Evolving scenery

The sky and the **Zhangjiajie-style stone pillars** follow a continuous **day → golden hour → sunset → dusk → starry night → predawn → sunrise → day** cycle. One full cycle every **5 minutes of gameplay** (real time, independent of score), interpolated smoothly — long runs cover the whole arc.

| Phase       | Sky tone                | Pillar + canopy                          |
|-------------|-------------------------|------------------------------------------|
| Day         | Bright cyan             | Warm tan sandstone, lush green pines     |
| Sunset      | Pink-orange horizon     | Rose-stone pillars, autumn canopy        |
| Night       | Navy + scattered stars  | Moonlit blue-grey stone, dark teal moss  |
| Sunrise     | Peach + pink bloom      | Peach stone, fresh-green canopy          |

---

## Screenshots

<table>
<tr>
  <td align="center">
    <img src="docs/screenshots/title.png" width="280"><br>
    <sub>Title — day biome</sub>
  </td>
  <td align="center">
    <img src="docs/screenshots/gameplay.png" width="280"><br>
    <sub>Gameplay — coin arc, X4 combo</sub>
  </td>
</tr>
<tr>
  <td align="center">
    <img src="docs/screenshots/sunset.png" width="280"><br>
    <sub>Sunset biome</sub>
  </td>
  <td align="center">
    <img src="docs/screenshots/night.png" width="280"><br>
    <sub>Starry night biome</sub>
  </td>
</tr>
<tr>
  <td align="center">
    <img src="docs/screenshots/mushroom.png" width="280"><br>
    <sub>3X POWER active — timer bar + sparkle</sub>
  </td>
  <td align="center">
    <img src="docs/screenshots/gameover.png" width="280"><br>
    <sub>Game Over + Top 10</sub>
  </td>
</tr>
</table>

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
└── storage.py             Top-10 leaderboard persistence (JSON file)
tools/
└── snapshot.py            Headless screenshot generator
docs/screenshots/          PNG screenshots (regenerate with: python tools/snapshot.py)
```

---

## Technical Notes

- **Screen**: 360 × 640 virtual pixels (mobile portrait). Smooth graphics, no integer upscaling.
- **Language**: Python 3, [Pygame 2.x](https://www.pygame.org/). Rendered with `SRCALPHA` surfaces, `BLEND_ADD` glows, pre-computed gradient/glow caches for performance.
- **Sprites**: everything — parrot, pillars, coins, mushroom, clouds, mountains, UI — is drawn procedurally (no image files).
- **Graphics polish**: radial glows around coins, soft drop shadows on pillars, antialiased parrot silhouette with 4 wing-cycle frames, parallax clouds + mountains, spring-decay screen shake, gravity particles.
- **Physics**: fixed-timestep update at 60 FPS; `GRAVITY = 1600 px/s²`, `FLAP_V = -520 px/s`, `MAX_FALL = 700 px/s`.
- **Coin pickup**: **localized** gold/white sparkle particles + "+1" / "+3" floating text. No full-screen flash.
- **Persistence**: high score saved to `skybit_save.json`, top-10 leaderboard to `skybit_scores.json`.
