# Skybit — Retro Pixel Flyer

A Flappy-Bird-style casual arcade game written in **Python** with [Pyxel](https://github.com/kitao/pyxel). Navigate a vivid scarlet parrot through pipes, collect glowing coins, and grab the rare mushroom for a **3× coin multiplier** for 8 seconds. Pure procedural pixel art, synthesized chiptune SFX, no external assets.

<p align="center">
  <img src="docs/screenshots/gameplay.png" width="340" alt="Gameplay">
  <img src="docs/screenshots/mushroom.png"  width="340" alt="3X Power">
</p>

---

## Play instantly — no install

Open **`play.html`** in any modern browser. It loads Pyxel's WebAssembly runtime from a CDN (~5 MB one-time download) and runs the full Python game in your browser. Works on desktop and mobile.

```
git clone https://github.com/ytocker/Claude_test.git
cd Claude_test
git checkout claude/retro-pixel-game-gPPYY
open play.html          # macOS — or double-click the file
```

An active internet connection is required for the first load (the Pyxel WASM runtime). After that the browser caches it.

---

## Run natively (Python)

```bash
pip install pyxel
python main.py
```

Requires Python 3.9+ and Pyxel 2.x.

---

## How to Play

Tap, click, or press **Space / Up / W** to flap. Survive as long as possible, score points by passing pipes and collecting coins.

| Action       | Desktop                        | Mobile       |
|--------------|--------------------------------|--------------|
| Flap         | Tap / Click · Space · Up · W   | Tap screen   |
| Pause        | P · Esc · ⏸ button             | Tap ⏸ button |

### Scoring

| Event                              | Points |
|------------------------------------|--------|
| Pass a pipe                        | +1     |
| Collect a coin                     | +1     |
| Collect a coin while 3× is active  | +3     |

Chain coins quickly to build a **combo multiplier** — the badge reads `X4 COMBO!` and so on, with escalating SFX.

### The Mushroom Power-Up

A red-spotted mushroom occasionally spawns in the gap between pipes (roughly 1-in-10 chance). Grab it to:

- Activate **3× POWER** for 8 seconds — coins worth +3 each
- Trigger a radial sparkle burst and brief time-slow
- See an orange/gold aura glow around the parrot for the duration
- Watch a timer bar under the score drain in real time

### Difficulty

The game gets harder as your score climbs:

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
    <sub>Gameplay — arc coin pattern, X4 combo</sub>
  </td>
</tr>
<tr>
  <td align="center">
    <img src="docs/screenshots/mushroom.png" width="280"><br>
    <sub>3X POWER active — aura + sparkle burst</sub>
  </td>
  <td align="center">
    <img src="docs/screenshots/gameover.png" width="280"><br>
    <sub>Game Over — new best score</sub>
  </td>
</tr>
</table>

---

## Project Structure

```
main.py                   Entry point — starts the Pyxel app
play.html                 Browser-playable build (Pyxel WASM + embedded game)
skybit/
├── app.py                Pyxel App class: init, run, scene management
├── config.py             All gameplay constants (physics, spawn rates, timings)
├── palette.py            Custom 16-colour palette (0xRRGGBB values + aliases)
├── sprites.py            Procedural drawing: parrot (4-frame flap), pipes,
│                         coins, mushroom, clouds, parallax bg, bitmap font
├── entities.py           Bird, Pipe, Coin, Mushroom, Particle, FloatText
├── world.py              World simulation: scrolling, spawning, collision,
│                         difficulty ramp, particle FX, screen shake/flash
├── hud.py                Score, hi-score, coin count, mushroom timer bar,
│                         combo badge, floating pickup text, pause button
└── storage.py            High score + settings persistence (JSON file)
tools/
└── snapshot.py           Headless screenshot generator (Pillow-backed pyxel shim)
docs/screenshots/         PNG screenshots (regenerate with: python tools/snapshot.py)
```

---

## Technical Notes

- **Screen**: 160 × 240 virtual pixels, displayed at 3× scale (480 × 720) — crisp on any monitor or phone
- **Language**: Python 3, [Pyxel 2.x](https://github.com/kitao/pyxel) game engine
- **Palette**: custom 16-colour set tuned for the scarlet-macaw parrot and lush sky tones
- **Sprites**: every sprite (parrot, pipe, coin, mushroom, clouds, font glyphs) is drawn procedurally via `pyxel.rect/circ/pset` — no image files
- **SFX**: Pyxel's built-in chiptune synth — flap, coin, combo, mushroom, hit
- **Physics**: fixed-timestep update at 60 FPS, `GRAVITY = 900 px/s²`, `FLAP_V = −255 px/s`
- **Persistence**: high score saved to `~/.skybit_save.json`
- **Web export**: `pyxel package . main.py && pyxel app2html *.pyxapp` → `play.html`

Rebuild `play.html` after editing source:
```bash
pip install pyxel
pyxel package . main.py
pyxel app2html *.pyxapp
mv Claude_test.html play.html
rm *.pyxapp
```
