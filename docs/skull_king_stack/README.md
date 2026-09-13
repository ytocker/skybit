# Skull-King stacked-skull pillar — design only

Two pillar concepts built by **stacking the various small skulls from the chosen
king-skull design** (Asthi-Dakini **`SWITCHED + BIG`**, see
[`../skybit_devil/batch2/asthi_ringeye/CHOSEN.md`](../skybit_devil/batch2/asthi_ringeye/CHOSEN.md))
one on top of another, pagoda-style.

The stacked units are that design's own distinct small skulls, reused directly
from its render script
([`render_switchbig.py`](../skybit_devil/batch2/asthi_ringeye/render_switchbig.py)):

- the **6 crown skulls** (`crown_skull`, idx 0–5) — the bare relic skulls above her head, and
- the **6 palm skulls** (`palm_skull`, idx 0–5) — the ornamented reliquary skulls
  from her palms, several carrying the cyan gem. Stacked **bare** (the open-palm
  cup / finger-ticks are removed — only the skull is kept).

They are interleaved up the column so each pillar shows the bare relic skulls
*and* the jewelled cradled ones. The gap-edge skull is the lit focal (cyan eyes),
facing Pip's lane.

## Variants

- **`stack.png`** — the plain pagoda stack (skull-on-skull, thin gold bead collars).
- **`skewer.png`** — the same stack with a central gold-cored bone **skewer**
  threaded down through every skull, ending in a barbed point that juts into the gap.
- **`showcase.png`** — both, side by side.

Each sheet shows the top+bottom pillar pair framing a gap on **day** and **night**
sky, plus a true **58px** in-game crop.

## Status

**Design exploration only — not wired into the game.** Renderer:
[`../../tools/render_skull_king_stack.py`](../../tools/render_skull_king_stack.py)
(procedural; reuses the chosen design's skull functions + palette).
