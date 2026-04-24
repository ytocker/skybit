# Pillar Variants — 5 Options (Original Design + Rich Decoration Packs)

## Intent

Keep the **current Zhangjiajie-quartzite silhouette** (same stone body, same
pine / moss / shrub helpers) and layer **dense, lively decoration** on top so
each pillar feels inhabited and story-rich, not "baked":

1. **Stone palette** — a strong, clearly distinct tint per variant
2. **Vegetation** — multiple pines, shrubs, vines, moss, grass, berries, mushrooms
3. **Ornaments + wildlife** — flags, lanterns, bells, plaques, cairns, birds,
   butterflies, fireflies, a crane, a rabbit — anything that tells a little story

No new silhouettes, no new primitives. Every element slots into the existing
pillar pipeline.

---

## The 5 options

### 1. Pilgrim's Peak — Tibetan shrine route

A **warm honey-gold** sandstone (pushed warmer than default: light ≈ 235/200/150,
accent ≈ 255/225/170). The pillar reads as a high-altitude pilgrimage stop.

**Vegetation**
- 2 Wuling pines staggered on the peak (tall central + shorter lean-right)
- 1 side shrub on the upper ledge, 1 on the lower ledge
- Climbing shrub creeping up the north face of the bottom pillar
- Small moss patch under the top pillar's fang
- Grass tufts in two mid-face crevices

**Ornaments + wildlife**
- **Prayer-flag string** (blue / white / red / green / yellow × 7) strung
  diagonally from the top pillar's shoulder down to a pine bough
- Tiny **brass bells** hung on every third flag, glinting
- **White Tibetan stupa** shrine nestled on a low ledge at the base, with a
  thin **incense smoke wisp** curling upward
- 2 **bird silhouettes** (V-shapes) crossing the distant sky behind the column

---

### 2. Ribbon Pine — wish-tree offering

A **cool silver-grey sand** palette (light ≈ 205/200/180, dark ≈ 75/70/60) —
noticeably colder than default, almost bluish in shadow.

**Vegetation**
- 2 pines on the peak: one tall central (6 canopy layers), one small companion
- **5+ moss strands** cascading from the top pillar's underside
- **Flowering vine** creeping along the stone face (tiny pink + violet dots)
- **Berry cluster** tucked inside the main pine canopy (deep red specks)
- 2 small **mushrooms** (red caps, white stems) at the base
- 1 low side shrub

**Ornaments + wildlife**
- **Red silk ribbon** knotted low on the main pine trunk with two fluttering tails
- **3 additional smaller ribbons** tied to outer branches of both pines
- **Wooden wish plaque** (calligraphy marks) hanging from a low bough by a cord
- **Small brass bell** with a yellow tassel swinging from a higher branch

---

### 3. Lantern Ledge — festival lights at dusk

A **pale bone-ivory** sandstone (light ≈ 245/225/195) — sun-bleached, highest
contrast against the sky.

**Vegetation**
- 1 small pine with an airy crown
- 2 flower-blooming shrubs at different ledge heights (dots of yellow + white)
- Hanging vine with small **pom-pom leaf balls** draped from an upper ledge
- Grass tufts growing in 3 stone crevices

**Ornaments + wildlife**
- **Main red paper lantern** hanging from the top pillar's underside
  (cord + wooden caps + ribs + amber flame glow + yellow tassel)
- **2 smaller paper lanterns** strung along the underside on the same cord
- **Ledge lantern** on a short post, sitting on a mid-face ledge
- **3–4 fireflies** (soft yellow glow dots) floating in the gap
- 1 small **moth** circling the main lantern

---

### 4. Crane's Rest — wildlife stopover

An **olive-green-tinted sandstone** (light ≈ 215/200/160, accent ≈ 240/230/170) —
the stone subtly reads as moss-shaded, unique among the five.

**Vegetation**
- 1 main pine with slightly mossier cap + 1 companion shrub-pine on a lower ledge
- **Wildflower patches** on 2 separate ledges (yellow + white dots)
- **Berry bush** on the upper ledge (orange berries)
- **Mushroom cluster** (3 caps) at the base
- 2 hanging vines of different lengths from the top pillar

**Ornaments + wildlife**
- **White-and-red-crowned crane** perched on the peak ledge beside the pine
- **Second crane silhouette** in flight in the distant sky
- **2–3 butterflies** (one orange, two blue) hovering near the wildflower ledge
- **Small rabbit silhouette** curled on a low ledge at the base
- Tiny **bird's nest** (twig ring) tucked in the main pine canopy

---

### 5. Cairn Marker — hiker's summit route

A **rich terracotta red** sandstone (light ≈ 235/175/130, mid ≈ 185/115/80,
dark ≈ 105/55/40) — the warmest, rustiest of the set, clearly iron-oxide tinted.

**Vegetation**
- 1 pine off to one side of the peak
- 1 moss strand from the top pillar
- 1 larger side shrub on the lower ledge
- Small tuft of dried grass beside the cairn

**Ornaments + wildlife**
- **Main 4-stone cairn** on the peak ledge with a thin pole + **red triangular pennant**
- **Secondary smaller 3-stone cairn** on a lower ledge
- **Multi-coloured pennant string** (red / orange / yellow triangles) strung
  from the main pole down the pine
- **Wooden signpost with two carved-arrow boards** at the base
- **Walking stick** leaning against the stone face
- **Small campfire** (crossed-log shape + orange ember glow + thin smoke wisp)
  at the base
- **Wooden wish plaque** nailed to the pine trunk
- **Raven silhouette** perched on the topmost cairn stone

---

## Summary

| # | Name | Stone tint | Vegetation | Signature ornaments |
|---|------|------------|------------|----------------------|
| 1 | Pilgrim's Peak   | warm honey-gold       | 2 pines, climbing shrub, moss, grass      | prayer flags + bells, stupa, incense, birds |
| 2 | Ribbon Pine      | cool silver-grey      | 2 pines, 5 moss, vine, berries, mushrooms | 4 ribbons, wish plaque, bell + tassel |
| 3 | Lantern Ledge    | pale bone-ivory       | small pine, flower shrubs, pom-pom vine   | 3 hanging lanterns + ledge lantern, fireflies, moth |
| 4 | Crane's Rest     | olive-green tinted    | pine, wildflowers, berries, mushrooms     | perched + flying crane, butterflies, rabbit, nest |
| 5 | Cairn Marker     | rich terracotta red   | pine, moss, shrub, dried grass            | 2 cairns, pennant string, signpost, stick, campfire, raven |

---

## Next step

Reply with your picks (e.g. `"1, 3, 5"` or `"all"`) and those variants will be
folded into `game/entities.py` as random-per-spawn decorations, seeded by the
world RNG so each run is deterministic. If you want to tweak a palette, add or
drop decorations on any variant, just say the word.
