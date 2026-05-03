# Skybit web — TypeScript + HTML5 Canvas2D

The deployed Skybit build. Replaces the previous pygbag/Pyodide pipeline:
cold-start critical-path went from ~4–6 MB gzipped (CPython + pygame
WASM + APK) to ~21 KB gzipped (HTML + JS).

## Run locally

```bash
cd web
npm ci
npm run dev          # Vite dev server at http://localhost:5173
```

Or open `dist/index.html` directly in any browser after `npm run build` —
the production build is fully self-contained (assets streamed lazily).

## Build for deploy

```bash
npm run build
```

Outputs to `web/dist/`. Netlify is wired to run this from the repo root
via `netlify.toml`.

## Layout

```
src/
  main.ts            entry; mounts the canvas, wires the loading overlay
  config.ts          gameplay constants (W/H/FPS, physics, durations)
  biome.ts           day-night palette interpolation
  draw.ts            Canvas2D primitive layer + caches (sky/pillar/glow)
  parrot.ts          procedural macaw + KFC variant + parcel + recolour stubs
  pillar-variants.ts pillar pair drawing (silhouette + foliage cap)
  entities.ts        Bird, Pipe, Coin, PowerUp, Particle, CloudPuff, FloatText
  world.ts           physics, spawner, collision, power-up timers
  weather.ts         rain particles
  hud.ts             score, timer bars, menu/pause/stats/leaderboard overlays
  scenes.ts          state machine + RAF loop + main App class
  audio.ts           Web Audio sample playback (lazy-load on first play)
  leaderboard.ts     Supabase REST + localStorage fallback + name-entry overlay
public/
  fonts/             vendored LiberationSans (Bold + Regular)
  sounds/            12 OGG samples (CC0)
  kfc_logo.png       KFC power-up sprite
index.html           markup + loading splash + name-entry overlay
```

## Pygame → Canvas2D mapping

| pygame                           | Canvas2D equivalent                        |
| -------------------------------- | ------------------------------------------ |
| `Surface((w,h), SRCALPHA)`       | `document.createElement("canvas")`         |
| `draw.{circle,rect,line,...}`    | `ctx.{arc,fillRect,moveTo+lineTo,...}`     |
| `BLEND_ADD`                      | `ctx.globalCompositeOperation = 'lighter'` |
| `BLEND_RGBA_MIN` (alpha cutout)  | `ctx.globalCompositeOperation = 'destination-in'` |
| `BLEND_RGBA_MULT`                | `'multiply'`                               |
| `transform.smoothscale`          | `ctx.drawImage(s, 0, 0, w, h)`             |
| `transform.rotate / rotozoom`    | `ctx.translate + rotate + drawImage` (cached) |
| `mask.from_surface()` (outline)  | `globalCompositeOperation = 'source-in'` + 8-neighbour blits |
| `font.Font(path, size)`          | `@font-face` + `ctx.font = '<size>px LiberationSans'` |

## What's deferred

Tracked for follow-up commits — gameplay is complete without these:

- 12-second intro cinematic (`game/intro.py`, 1106 LOC). Menu → Play
  flow works the same; players who load the page just see the menu.
- Full hand-drawn ghost / hat / grow parrot variants (currently
  recolour fallbacks of the base sprite).
- Eight-variant pillar styles (currently a single tuned variant).
- Lightning thunderclaps in `weather.ts`.

## Leaderboard config

Set Netlify env vars `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`
to enable the global leaderboard. Without them the build falls back to
a per-browser localStorage top-10.
