# Skybit — Pocket Sky Flyer

A colorful Flappy-style casual arcade game. Fly a **vivid scarlet-macaw parrot** through pipes, collect glowing coins, and grab the rare mushroom for a **3× coin multiplier** that lasts 8 seconds. Built in **Python** with Pygame — procedural graphics, smooth gradients, soft glows, no pixel art.

<p align="center">
  <img src="docs/screenshots/gameplay.png" width="340" alt="Gameplay">
  <img src="docs/screenshots/mushroom.png"  width="340" alt="3X Power">
</p>

---

## Play instantly — no install

Open **`play.html`** in any modern browser. It loads the Pygame runtime on top of WebAssembly (via [pygbag](https://pygame-web.github.io/)) and runs the full Python game in your browser. Works on desktop and mobile.

```
git clone https://github.com/ytocker/Claude_test.git
cd Claude_test
git checkout claude/retro-pixel-game-gPPYY
# open play.html through a local web server:
python3 -m http.server 8000
# then open http://localhost:8000/play.html
```

The first load pulls a one-time CPython WebAssembly runtime (~10 MB). Subsequent loads are cached.

---

## Run natively (Python)

```bash
pip install pygame
python main.py
```

Requires Python 3.9+ and Pygame 2.x.

---

## How to Play

Tap, click, or press **Space / Up / W** to flap. Survive as long as possible, rack up points by passing pipes and collecting coins.

| Action       | Desktop                        | Mobile       |
|--------------|--------------------------------|--------------|
| Flap         | Tap / Click · Space · Up · W   | Tap screen   |
| Quit         | Esc                            | —            |

### Scoring

| Event                              | Points |
|------------------------------------|--------|
| Pass a pipe                        | +1     |
| Collect a coin                     | +1     |
| Collect a coin while 3× is active  | +3     |

Chain coins quickly to build a **combo multiplier** — a bouncing `X4 COMBO!` badge appears near the bottom of the screen.

### The Mushroom Power-Up

A red-capped mushroom occasionally spawns in the gap between pipes (roughly 1-in-9 chance, with a cooldown). Grab it to:

- Activate **3× POWER** for 8 seconds — coins worth +3 each
- Trigger a radial sparkle burst and a brief time-slow
- See an orange/gold aura glow around the parrot for the duration
- Watch a timer bar below the score drain in real time

### Difficulty

- **Score 0–20**: wide gaps, relaxed scroll speed
- **Score 20–35**: gaps tighten, speed ramps up
- **Score 35+**: near-minimum gap, maximum scroll speed

---

## Screenshots

<table>
<tr>
  <td align="center">
    <img src="docs/screenshots/title.png" width="280"><br>
    <sub>Title screen</sub>
  </td>
  <td align="center">
    <img src="docs/screenshots/gameplay.png" width="280"><br>
    <sub>Gameplay — coin arc, X4 combo</sub>
  </td>
</tr>
<tr>
  <td align="center">
    <img src="docs/screenshots/mushroom.png" width="280"><br>
    <sub>3X POWER active — timer bar + sparkle</sub>
  </td>
  <td align="center">
    <img src="docs/screenshots/gameover.png" width="280"><br>
    <sub>Game Over</sub>
  </td>
</tr>
</table>

---

## Project Structure

```
main.py                    Entry point — asyncio loop so pygbag can export to WASM
play.html                  Browser-playable build (Pygame on WebAssembly)
game/
├── config.py              Gameplay constants (physics, spawn rates, timings)
├── draw.py                Low-level drawing: gradient surfaces, glow caches,
│                          mountains, clouds, ground, rounded rects
├── parrot.py              4-frame animated scarlet-macaw sprite (procedural)
├── entities.py            Bird, Pipe, Coin, Mushroom, Particle, FloatText
├── world.py               Simulation: scroll, spawn, collision, pickups,
│                          difficulty ramp, shake, pickup FX
├── hud.py                 Score, best, coin count, 3X timer, combo badge,
│                          pause button, menu/game-over overlays
├── scenes.py              Scene state machine (Menu / Play / GameOver) + App
└── storage.py             High-score persistence (JSON file)
tools/
└── snapshot.py            Headless screenshot generator
docs/screenshots/          PNG screenshots (regenerate with: python tools/snapshot.py)
```

---

## Technical Notes

- **Screen**: 360 × 640 virtual pixels (mobile portrait). Smooth graphics, no integer upscaling.
- **Language**: Python 3, [Pygame 2.x](https://www.pygame.org/). Rendered with `SRCALPHA` surfaces, `BLEND_ADD` glows, pre-computed gradient/glow caches for performance.
- **Sprites**: everything — parrot, pipes, coins, mushroom, clouds, mountains, UI — is drawn procedurally (no image files).
- **Graphics polish**: radial glows around coins, soft drop shadows on pipes, antialiased parrot silhouette with 4 wing-cycle frames, parallax clouds + mountains, spring-decay screen shake, gravity particles.
- **Physics**: fixed-timestep update at 60 FPS; `GRAVITY = 1600 px/s²`, `FLAP_V = -520 px/s`, `MAX_FALL = 700 px/s`.
- **Coin pickup**: **localized** gold/white sparkle particles + "+1" / "+3" floating text. No full-screen flash.
- **Persistence**: high score saved to `skybit_save.json`.
- **Web export**: `python -m pygbag --build main.py` produces `build/web/index.html`. Copy it to `play.html` in the repo root.

Rebuild `play.html` after editing source:
```bash
pip install pygbag
python -m pygbag --build main.py
cp build/web/index.html play.html
```
