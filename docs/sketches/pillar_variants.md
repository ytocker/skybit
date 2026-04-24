# Pillar Variants — 20 Dense Options (uniform stone, varied tops)

![Preview of the 20 pillar variants](pillar_variants.png)

*Rendered by `tools/pillar_variants.py`. 5×4 grid, 300×820 per cell, 1500×3280 total.*

## Design axes

All 20 share the **same warm-honey Zhangjiajie sandstone palette** — the
variety comes from three other axes:

1. **Top-pillar silhouette** — 7 shapes (rounded spire, spike, flat cap, twin
   fork, notched, bell-cap, stepped terrace)
2. **Vegetation density** — 2–3 pines per peak, many moss strands, side shrubs
   on multiple ledges, grass tufts, wildflowers, berries, mushrooms, vines
3. **Ornament + wildlife packs** — prayer flags, ribbons, wish plaques, bells,
   paper lanterns in 6 colours, lantern strings, ledge lanterns, cairns,
   pennant strings, banners, wind chimes, stupas, incense smoke, signposts,
   campfires, walking sticks, cranes, ravens, rabbits, butterflies, fireflies,
   moths, bird silhouettes, bird nests

## The 20

| # | Name | Top silhouette | Signature pack |
|---|------|----------------|----------------|
| 01 | Pilgrim's Peak    | spire    | 3 pines · prayer flags + bells · 2 stupas · incense · 5 birds |
| 02 | Ribbon Pine       | spike    | 3 pines · 7 moss · 5 red ribbons · 2 plaques · 2 bells · berries · mushrooms · pink vine |
| 03 | Lantern Ledge     | spire    | hero + gold lantern · string · 4 small coloured lanterns · 2 ledge lanterns · 4 flower shrubs · 6 fireflies · 2 moths |
| 04 | Crane's Rest      | flat     | 3 pines · 2 cranes · 4 butterflies · rabbit · 4 birds · 4 wildflower patches · berries · nest · mushrooms |
| 05 | Cairn Marker      | spike    | 2 pines · 3 cairns · 2 pennant strings · signpost · walking stick · campfire · 2 ravens · 2 plaques |
| 06 | Bell Tower        | bell     | 6 bells · 2 wind chimes · 2 lanterns · stupa · pennants · moss · shrubs |
| 07 | Twin Fangs        | twin     | 3 pines · 5 moss · 2 pom-pom vines · 4 flower shrubs · 2 berry clusters · 2 ravens |
| 08 | Fortress Notch    | notched  | 3 pines · 4 coloured banners · cairn · pennants · signpost · walking stick · campfire |
| 09 | Stepped Shrine    | stepped  | 4 coloured lanterns · prayer flags · 4 flower shrubs · 5 moss · stupa + incense · plaque · bell |
| 10 | Night Market      | flat     | 6 coloured lanterns at top · 2 lantern strings · 4 small lanterns · 2 ledge lanterns · fireflies |
| 11 | Mushroom Grotto   | bell     | 2 pines · 5 moss · 4 mushroom patches · 5 flower shrubs · 2 pom-pom vines · rabbit · fireflies |
| 12 | Moss Cascade      | spire    | 3 pines · **17 moss strands** · 5 shrubs · 2 berry clusters · mushrooms · grass |
| 13 | Butterfly Garden  | flat     | 2 pines · 5 flower shrubs · 5 wildflower patches · **8 butterflies** · nest · berries · 2 birds |
| 14 | Banner Keep       | notched  | 2 pines · 5 banners (red/blue/gold/green/purple) · 2 pennant strings · plaque · bell · signpost |
| 15 | Raven Cliff       | twin     | 2 pines · 4 moss · **7 ravens** · 2 cairns · 4 birds · walking stick · campfire |
| 16 | Firefly Hollow    | spike    | 2 pines · 4 flower shrubs · 2 pom-pom vines · **14 fireflies** · 2 moths · rabbit · mushrooms |
| 17 | Forest Summit     | stepped  | **5 pines** · 5 moss · 4 shrubs · 2 berries · nest · 2 mushroom clusters · 3 birds |
| 18 | Chime Pagoda      | bell     | 2 pines · **5 wind chimes** · 4 bells · pennants · stupa · incense · plaque |
| 19 | Festival Arch     | flat     | 2 pines · 6 coloured lanterns · lantern string · prayer flags · pennants · **5 banners** |
| 20 | Wildflower Crest  | spire    | 3 pines · 5 flower shrubs · 7 wildflower patches · 4 butterflies · berries · vine |

## How to pick

Reply with the numbers you like (e.g. `"1, 6, 13, 18"` or ranges `"1-5, 11-13"`
or `"all"`). Chosen variants will be folded into `game/entities.py` as a
random-per-spawn decoration pool seeded by the world RNG.
