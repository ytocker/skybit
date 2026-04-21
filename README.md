# Skybit — A Retro Pixel Flyer

A Flappy-Bird-style casual arcade game with coin collection and a rare **mushroom power-up** that grants **3× coin value** for 8 seconds. Handmade pixel art, dithered sunset skies, parallax mountains, scanline CRT vibe, synthesized chiptune SFX — no external assets, no build step, no dependencies.

<p align="center">
  <img src="docs/screenshots/gameplay.png" alt="Skybit gameplay" width="360">
</p>

---

## Features

- **Classic one-tap flying**: tap, click, or press Space / ↑ / W to flap.
- **Coin collection** with arc, line, and cluster patterns spawned between pipes.
- **Power mushroom** (rare, every few gaps) → **3× coin value** for 8 seconds, with a visible timer bar, glowing aura, brief time-slow on pickup, and a 20-particle radial burst.
- **Combo counter** for consecutive coins inside a short time window.
- **Juicy game feel**: screen shake, screen flashes, bird tilt, motion trail, floating `+1` / `+3` pickup text.
- **Lush retro backdrop**: dithered 4-band sky, parallax mountains (2 layers), drifting clouds, animated sun, scrolling ground with grass tufts and dirt specks.
- **Scanlines + vignette** CRT post-FX (toggle with `C`).
- **Pure procedural pixel art**: every sprite (bird, coin, pipe, mushroom, cloud, HUD font) is built in code — no image files.
- **Synthesized SFX**: flap, coin, combo, mushroom, hit — all generated with the Web Audio API at runtime.
- **Mobile-friendly**: full-screen canvas, safe-area insets, `touch-action: none`, integer scaling, pause button hit rect.
- **Local high score** persisted via `localStorage`.
- **Scaling difficulty**: pipe gaps tighten and scroll speed ramps up as your score climbs.

---

## How to Run

### Option 0 — No server needed: `play.html`

A single-file bundle is included at the repo root. Just open `play.html` in any modern browser (double-click it, or drag it onto a browser window). Everything — JS, CSS, sprites, SFX — is inlined. Works from `file://`.

Rebuild it after editing source with:

```bash
node tools/bundle.mjs
```

### Other options (run the modular version)

The modular source in `src/*.js` uses native **ES modules**, so it needs a tiny static http server.

### Option 1 — Python (installed almost everywhere)

```bash
cd Claude_test
python3 -m http.server 8000
```

Open <http://localhost:8000> in any modern browser.

### Option 2 — Node

```bash
cd Claude_test
npx --yes serve -l 8000 .
```

### Option 3 — Play on your phone

Run either server above on your laptop, find your machine's LAN IP (`ipconfig` / `ifconfig`), then visit `http://<your-ip>:8000` on your phone on the same Wi-Fi.

### Option 4 — GitHub Pages

Push this branch and enable GitHub Pages for it — `index.html` is at the root and will work out of the box.

> No `npm install`. No build step. No bundler. Just open the page.

---

## How to Play

Get the bird as far as possible without hitting the pipes or the ground, collecting as many coins as you can along the way.

### Controls

| Action                | Desktop                          | Mobile        |
|-----------------------|----------------------------------|---------------|
| Flap                  | Tap / Click, `Space`, `↑`, `W`   | Tap the screen |
| Pause / Resume        | `P` or `Esc`, or tap the ⏸ button | Tap the ⏸ button |
| Toggle CRT scanlines  | `C`                              | —             |
| Toggle sound          | `M`                              | —             |

### Scoring

- **+1** for each pipe you pass.
- **+1** for each coin collected (**+3** while the mushroom buff is active).
- Chain coins quickly to build a **combo multiplier** badge — `x2`, `x3`, … — with escalating pickup sound.

### The Mushroom

Rarely — roughly one in every several pipe gaps — a red-spotted mushroom spawns in the middle of the gap. Grab it to activate **3× POWER** for 8 seconds:

- A timer bar appears under the score.
- Your bird gains a glowing orange halo.
- Time briefly slows on pickup so you can line up your first buffed coin.
- Every coin you touch during the buff is worth **+3** instead of +1.

### Tips

- Early pipes are wide and slow — use them to warm up your rhythm.
- Gaps tighten and the world scrolls faster after score **~20** and again after **~40**.
- Stay in the middle of the screen to keep options open.
- The mushroom is worth chasing into tight spots — 8 seconds of 3× adds up fast.

---

## Screenshots

<table>
<tr>
  <td align="center">
    <img src="docs/screenshots/title.png" alt="Title screen" width="260"><br>
    <sub><b>Title screen</b> — dithered sunset sky, parallax hills, tap to flap</sub>
  </td>
  <td align="center">
    <img src="docs/screenshots/gameplay.png" alt="Gameplay" width="260"><br>
    <sub><b>Gameplay</b> — arc coin pattern between pipes, x3 combo, motion trail</sub>
  </td>
</tr>
<tr>
  <td align="center">
    <img src="docs/screenshots/mushroom.png" alt="3X Power mushroom active" width="260"><br>
    <sub><b>3× POWER!</b> — mushroom collected, aura glowing, timer bar counting down</sub>
  </td>
  <td align="center">
    <img src="docs/screenshots/gameover.png" alt="Game over" width="260"><br>
    <sub><b>Game over</b> — new-best announcement, tap to retry</sub>
  </td>
</tr>
</table>

> The screenshots above are generated by `tools/snapshot.mjs`, which reuses the exact same sprite/palette/rendering code as the live game. If you modify sprites, run `node tools/snapshot.mjs` to refresh them.

---

## Project Structure

```
index.html             Canvas host + module entry point
style.css              Full-screen, pixel-perfect, safe-area-aware styling
src/
├── main.js            Bootstrap, rAF fixed-timestep loop, input wiring
├── config.js          All gameplay constants (physics, spawn rates, timings)
├── palette.js         16-color retro palette, 32-bit ABGR encoded
├── gfx.js             Offscreen pixel buffer: rects, sprites, dither, scanlines, vignette
├── sprites.js         Procedural bird / coin / mushroom / pipe / cloud sprites + 3x5 bitmap font
├── input.js           Unified pointer / touch / keyboard input
├── audio.js           Web Audio SFX synth (flap, coin, combo, mushroom, hit, score)
├── storage.js         localStorage wrapper for high score + settings
├── fx.js              Screen shake, screen flash, time-slow effects
├── entities.js        Bird, Pipe, Coin, Mushroom, Particle, FloatText
├── world.js           World simulation: scrolling, spawning, collisions, difficulty ramp
├── hud.js             Score, high score, coin count, combo badge, mushroom timer, pause button
└── scenes.js          Menu / Play / GameOver state machine + render composition
tools/
└── snapshot.mjs       Headless PNG renderer for README screenshots (zero deps)
docs/screenshots/      Generated game screenshots
```

Total ≈1200 lines of hand-written, dependency-free JavaScript.

---

## Tech Notes

- **Internal resolution**: 180×320 virtual pixels, integer-scaled to fit the viewport. `image-rendering: pixelated` keeps every pixel crisp at any size.
- **Rendering**: a single `ImageData` buffer is filled as a `Uint32Array` (fast palette writes), then blitted once per frame with `putImageData`.
- **Fixed timestep**: 60 Hz update (`DT = 1/60`) with an accumulator and a 5-step cap, so gameplay stays stable even when the tab lags.
- **Palette**: a tuned variant of Adigun Polack's **AAP-16** — a beautiful 16-color pixel-art palette in the public domain.
- **No assets**: sprites live as short ASCII grids in `src/sprites.js`. Readable, diff-friendly, and tiny.
- **No audio files**: every sound effect is generated on the fly from oscillators + a short burst of noise.

---

## Credits

- Game design, code, pixel art, and SFX synthesis: handmade for this repo.
- Palette inspired by Adigun Polack's AAP-16 (public domain).

Enjoy, and good luck chasing that high score.
