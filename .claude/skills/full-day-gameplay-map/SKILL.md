---
name: full-day-gameplay-map
description: >-
  Regenerate and surface the canonical "full-day gameplay map" — Skybit's run-
  content figure showing how a whole day advances by pillars: the sky/biome strip
  on top and every gameplay event (morning thermal geysers, rain/thunderstorm,
  snow squall, lightning strike zone, genie lamp + umbrella anchors, clown
  gauntlet, newbie ramp, end-of-day treasure box) plotted against pagodas passed.
  Use whenever the user asks for the "full day gameplay map/figure", "the figure
  that shows the whole game / biome / events by pillars", "the run content map",
  "the pagoda map", or any rephrasing of that one canonical chart. This is the
  LIVE base map only — no design-proposal overlays (e.g. candidate power-up
  positions); those are separate one-off figures.
---

# Full-day gameplay map

The one canonical figure for reasoning about *where in a run* things happen:
the day's sky/biome progression plus every gameplay event, on a
**pagodas-passed (pillars scored)** axis.

## What it is — the fixed identity
- **Generator:** `tools/plot_event_pagoda_map.py` (factored helpers
  `compute_axis` / `draw_map` / `phase_labels_for`; reads everything LIVE from
  `game/` — `weather`, `biome`, `config` — so the chart always tracks the real
  game).
- **Output (stable path — never rename):**
  `docs/screenshots/event_pagoda_map_clown_v6.png`.
- **Contents:** sky-colour banner sampled per pillar; the three weather curves
  (thermal geysers / rain / snow), the lightning + storm-jolt zones, the genie
  lamp + umbrella power-up anchors, the clown gauntlet band with its clear-sky
  relief notches, the newbie plateau/ramp, and the end-of-day treasure-box
  finale — all on the live `weather._phase_for_pillar` axis.

## How to produce it (every time the user asks)
1. Regenerate headless from the repo root:
   ```
   SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python tools/plot_event_pagoda_map.py
   ```
   (`tight_layout` UserWarning is harmless.) `print_summary` echoes the live
   landmark pillars — glance at it to confirm nothing looks off.
2. **Validate without viewing.** Confirm the PNG is non-blank with PIL only —
   print `size`, distinct-colour count, and byte size. NEVER view or `Read` the
   image (project hard rule: rendered visuals are shared as git links only).
3. Commit `docs/screenshots/event_pagoda_map_clown_v6.png` (plus the generator
   if it changed) to the active working branch and push
   (`git push -u origin <branch>`, retry with backoff on network errors).
4. Surface the figure as a **GitHub blob URL on the working branch** — e.g.
   `https://github.com/ytocker/skybit/blob/<branch>/docs/screenshots/event_pagoda_map_clown_v6.png`
   — plus a one-line note of any landmark that moved. Never embed/attach the
   image in chat.

## Boundaries
- This skill renders the **live** map only. If the user wants candidate /
  proposal markers overlaid (e.g. "show the 3 genie placements on it"), that is a
  SEPARATE one-off tool that *imports* `draw_map` and writes a DIFFERENT PNG
  (pattern: `tools/plot_genie_placement_candidates.py` →
  `docs/screenshots/genie_placement_candidates.png`). Do not add proposal markers
  to the canonical artifact.
- If a real game constant changed (a new event, moved anchor, new biome phase),
  the generator already reads it live — just regenerate. Only edit
  `plot_event_pagoda_map.py` when a genuinely new live element needs drawing.
