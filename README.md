# Skybit — Pocket Sky Flyer

A colorful Flappy-style casual arcade game. Fly a **vivid scarlet-macaw parrot** through pipes, collect glowing coins, and grab the rare mushroom for a **3× coin multiplier** that lasts 8 seconds. Built in **Python** with Pygame — procedural graphics, smooth gradients, soft glows, no pixel art.

<p align="center">
  <img src="docs/screenshots/gameplay.png" width="340" alt="Gameplay">
  <img src="docs/screenshots/mushroom.png"  width="340" alt="3X Power">
</p>

---

## Play online — share the link

Two zero-install URLs. Send either to anyone — phone, tablet, desktop. Nothing to install, no account, it just loads and plays.

### 1. GitHub Pages (canonical, auto-updating)

**<https://ytocker.github.io/Claude_test/>**

Served by the workflow at `.github/workflows/pages.yml`, which rebuilds the WebAssembly bundle on every push to `claude/retro-pixel-game-gPPYY` (and `main`) and auto-enables Pages on the first run (`configure-pages` is set with `enablement: true`). First deploy takes ~1–2 minutes after the push; subsequent pushes redeploy in ~30 seconds.

If Pages hasn't kicked in yet, watch the run at **Actions → Deploy Skybit to GitHub Pages**.

### 2. raw.githack.com (instant, zero-setup fallback)

**<https://raw.githack.com/ytocker/Claude_test/claude/retro-pixel-game-gPPYY/play.html>**

This works the moment the branch is pushed — no Pages, no Actions, no config. raw.githack.com proxies any public GitHub file with correct MIME types and CORS headers, so `play.html` and its sibling `skybit.apk` load directly from the repo. Ideal for sharing a WIP build before a Pages deploy finishes.

> **Other free options** that also work with the `play.html` + `skybit.apk` pair if you ever need them: **Netlify Drop** (drag-and-drop the repo folder), **Cloudflare Pages**, **Vercel static**, **itch.io** (HTML5 game upload), or any S3/nginx that serves static files. GitHub Pages is free for public repos; private repos need GitHub Pro / Team.

### Run locally in a browser

```
git clone https://github.com/ytocker/Claude_test.git
cd Claude_test
git checkout claude/retro-pixel-game-gPPYY
python3 -m http.server 8000
# open http://localhost:8000/play.html
```

The first load pulls a one-time CPython WebAssembly runtime (~10 MB) from the Pygame-web CDN. Subsequent loads are cached.

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

### Leaderboard

Cracking the **top 10** pops up an arcade-style name-entry screen after Game Over. Tap the on-screen keyboard (or type on a keyboard — A–Z, Backspace, Enter) to pick three initials. Your entry is sorted into the list and persisted to `skybit_scores.json` next to the game.

> When playing in a browser, scores are saved to pygbag's in-browser virtual filesystem (IndexedDB) — they survive refreshes on the same device and domain, but aren't shared across players or devices. For a shared leaderboard, deploy with a backend of your choice.

<p align="center">
  <img src="docs/screenshots/nameentry.png" width="280" alt="Name entry">
  <img src="docs/screenshots/gameover.png"  width="280" alt="Leaderboard on Game Over">
</p>

### Difficulty

- **Score 0–20**: wide gaps, relaxed scroll speed
- **Score 20–35**: gaps tighten, speed ramps up
- **Score 35+**: near-minimum gap, maximum scroll speed

### Evolving scenery

The sky and the nature pillars follow a continuous **day → golden hour → sunset → dusk → starry night → predawn → sunrise → day** cycle. One full cycle every ~30 points, interpolated smoothly — every run looks different depending on how far you get.

| Phase       | Sky tone                | Pillar tint          |
|-------------|-------------------------|----------------------|
| Day         | Bright cyan             | Lush green with gold bands |
| Sunset      | Pink-orange horizon     | Warm coral pillars, cream bands |
| Night       | Navy + scattered stars  | Cool cyan-silver with glowing gems |
| Sunrise     | Peach + pink bloom      | Blush-pink with amber leaves |

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
    <sub>Sunset biome (~score 10)</sub>
  </td>
  <td align="center">
    <img src="docs/screenshots/night.png" width="280"><br>
    <sub>Starry night biome (~score 18)</sub>
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
main.py                    Entry point — asyncio loop so pygbag can export to WASM
play.html                  Browser-playable build (Pygame on WebAssembly)
game/
├── config.py              Gameplay constants (physics, spawn rates, timings)
├── biome.py               Day/night palette keyframes + phase interpolation
├── draw.py                Low-level drawing: gradient surfaces, glow caches,
│                          mountains, clouds, ground, nature-pillar bodies
├── parrot.py              4-frame scarlet-macaw w/ aviator sunglasses (procedural)
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
