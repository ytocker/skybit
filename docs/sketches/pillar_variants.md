# Pillar Variants — 5 Options (Original Design + Lively Touches)

![Preview of the 5 pillar variants](pillar_variants.png)

*Rendered by `tools/pillar_variants_preview.py`, using the game's actual pillar
helpers (`get_stone_pillar_body`, `silhouette_top_spire`, `silhouette_bottom_spire`,
`draw_wuling_pine`, `draw_moss_strand`, `draw_side_shrub`, `draw_pillar_mist`).*

## Intent

Keep the **current Zhangjiajie-quartzite look** and add variability across three
small axes per variant:

1. **Stone palette** — a slight tint shift (cooler, paler, rustier, …)
2. **Vegetation mix** — pine / moss / shrub proportions
3. **One lively ornament** — the signature "lived-in" detail

No new silhouettes, no new primitives, no reskin. Each variant drops straight
into the existing pillar pipeline.

---

## The 5 options

### 1. Pilgrim's Peak — prayer-flag string

A warm honey-sandstone pillar (≈ current default) with a single dominant Wuling
pine on the peak and a string of small **Tibetan-style prayer flags** (blue /
white / red / green / yellow) strung diagonally across the gap from the top
pillar's shoulder down to a pine bough.

- **Stone**: default DAY palette
- **Flora**: 1 pine + 1 side shrub + 1 moss strand on the top pillar
- **Ornament**: 7 small rectangular flags on a sagging cord

---

### 2. Ribbon Pine — red silk ribbon on the trunk

A slightly **cooler grey-sand** palette with a heavier **moss cascade** (3
strands) dripping from the top pillar's fang. The signature pine has a bright
**red silk ribbon** knotted low on the bare trunk, two tails fluttering
sideways — a classic "wish tree" offering.

- **Stone**: +5 blue, −5 red on light/mid/dark (cool shift)
- **Flora**: 1 tall pine (+1 layer) + 3 moss strands + 1 low shrub
- **Ornament**: red silk ribbon + two fluttering tails at the base of the trunk

---

### 3. Lantern Ledge — hanging paper lantern

A **paler ivory** sandstone body (more sun-bleached) with a smaller pine and
two shrubs at different heights. A **red paper lantern** hangs on a short cord
from the underside of the top pillar, complete with wooden caps, ribs, a
glowing amber flame and a small yellow tassel.

- **Stone**: +15 on all light/mid (bleached, more reflective)
- **Flora**: 1 small pine + 2 side shrubs
- **Ornament**: paper lantern with flame-glow and tassel

---

### 4. Crane's Rest — perched crane + wildflowers

The default warm palette with a slightly mossier cap. A tiny **white-and-red
crowned crane** perches on the bottom pillar's peak ledge beside the pine, and
a **small cluster of yellow-and-white wildflowers** dots a lower ledge — the
pillar feels inhabited, a stopover for wildlife.

- **Stone**: default DAY palette
- **Flora**: 1 pine + 1 side shrub + wildflower dots
- **Ornament**: crane silhouette perched by the peak

---

### 5. Cairn Marker — stacked cairn + red pennant

An **iron-rust-accented** sandstone (warmer, more orange) with one pine off to
the side and a moss strand on the top pillar. A **four-stone cairn** (decreasing
pebble sizes) is stacked on the peak ledge, topped with a thin pole and a
small **red triangular pennant** — a hiker's marker, a summit reached.

- **Stone**: +rust accent in light/mid, deeper red in shadows
- **Flora**: 1 pine + 1 moss strand + 1 larger side shrub
- **Ornament**: stacked cairn + red pennant on a pole

---

## Summary

| # | Name | Stone tweak | Flora | Ornament |
|---|------|-------------|-------|----------|
| 1 | Pilgrim's Peak   | default warm      | pine + shrub + moss   | prayer flags across the gap |
| 2 | Ribbon Pine      | cool grey-sand    | big pine + 3 moss     | red silk ribbon on trunk |
| 3 | Lantern Ledge    | pale ivory        | small pine + 2 shrubs | hanging paper lantern |
| 4 | Crane's Rest     | default warm      | pine + wildflowers    | perched crane |
| 5 | Cairn Marker     | iron-rust warm    | pine + moss + shrub   | stacked cairn + pennant |

## Next step

Reply with your picks (e.g. "1, 3, 5" or "all") and those variants will be
folded into `game/entities.py` as random-per-spawn decorations, seeded by the
world RNG so each run is deterministic. If you want to tweak a palette or an
ornament first, say the word and the renderer will re-run.
