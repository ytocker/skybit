# Pillar Landmarks — Brainstorm (graphics-designer, Phase A)

Six genuinely distinct **landmark-tower** directions to sit as peers to the 11
pagodas — same ROLE (top section hung from the ceiling + bottom section rising
from the ground, gap between; the two are the SAME builder mirrored) and same
grandeur, but each a clearly different architectural KIND. None are tiered-roof
pagodas; none overlap the shipped pagodas, the clown bone-columns, or the
existing `pillar_variants.py` dressings.

Idiom I'm designing to (from `pillar_pagodas.py` + the comparison renderer):
each concept is one `candidate_*(surf, top_rect, bot_rect, palette, seed)` with
a `draw_one(cx, base_y, top_y, ...)` helper called for both rects. Height is
**budgeted as proportions of the section**, and any repeated element is
**height-adaptive in COUNT** (the way Songyue keys eave count off a natural step
and the chorten keys its stepped base) so the body FILLS `[top_y, base_y]` with
zero killzone across the full 70–355 px range. Volume comes from `_shade`/`_mix`
edge shading + 3-stop gradient rects, not flat fills. Palette is pulled entirely
from the biome `stone_light/mid/dark/accent` (+ `foliage_*`, `horizon`) roles so
every tower retints day→night.

The distinctness spread, at a glance (Blackout test — solid-black shapes):

```
  1 LIGHTHOUSE   2 WINDMILL     3 CLOCKTOWER   4 OBELISK    5 KEEP        6 MOAI
     .-.            \ | /          /^\            /\          |_|_|         (o o)
    ( O )            \|/          | : |          /  \         |   |         |   |
    |===|          .-###-.        |[o]|         |    |        |===|  <corbel (@ @)
    |   |         /  ###  \       |   |         |    |        |   |         |   |
    | | |        /   ###   \      |   |         |    |        |   |         (^ ^)
    |   |       /  batter   \     |   |         | || |        |   |         |   |
   /     \     /____________ \   /_____\       /______\      /_____\       /_____\
  round        squat cone      straight sq.   gaunt wedge   toothed block  stacked
  taper+head   + radiating X   + spike + disc  to a point   + corbel flare  bulbous
```

Shape-language poles covered: **round-smooth-tapered** (1), **squat-conical +
radiating diagonal lattice** (2), **rectilinear straight-sided + spike** (3),
**gaunt sharp wedge-to-point** (4), **blocky + jagged toothed crown** (5),
**organic bulbous stacked ovoids** (6). No two share a silhouette pole.

---

## 1. `harbor-lighthouse`
**KIND tag:** round-tapered-cylinder-with-lantern-head
**Thesis:** A candy-banded coastal light — a smooth round column that swells
into a glass lantern room and a domed cap right at the gap.

- **Silhouette-tell:** The only smoothly **curved-sided taper** in the set,
  crowned by a distinct **wider "head"** — the gallery ring flares out, then the
  bulbous lantern room, then a low dome finial. Blackout reads as a bottle:
  narrow-shouldered head over a gently swelling round shaft. Nothing else here
  has that head-on-a-taper profile.
- **Construction:** Stacked full-width horizontal **bands** (rects that narrow
  slightly toward the tip) painted in **alternating light/dark candy stripes**;
  a corbelled **gallery ring** (thin wide rect + tiny baluster ticks) as a
  shoulder; the **lantern room** as a short polygon with vertical astragal bars
  and a warm glow blit (cached radial, like `draw_paper_lantern`'s glow); a
  **half-ellipse/arc dome** cap + ball finial. Barnacle/moss stipple at the
  waterline base.
- **Shape-language:** Round, smooth, monotone taper — the soft pole of the set.
- **Palette:** `stone_light`↔`stone_dark` drive the two candy-stripe tones;
  `stone_mid` for the gallery corbel; `stone_accent` for the warm lantern glass
  + glow; `foliage_dark` for waterline barnacle-moss.
- **Column-fill:** Bands span full width for the whole shaft; taper capped so the
  topmost band ≥ ~0.7 w. The gallery + lantern **head is wider than the shaft**
  and sits at the gap tip, so the gap end is the *most* filled part — no thin
  spire. Budget: base plinth / striped shaft (elastic bulk) / gallery / lantern /
  dome. Mirrors cleanly (a hung lighthouse; dome points into the gap).

## 2. `smock-windmill`
**KIND tag:** battered-conical-mill-with-radiating-sail-cross
**Thesis:** A weatherboarded drainage mill — a fat, steeply battered cone whose
four latticed sails throw a giant X across the gap.

- **Silhouette-tell:** A **squat, strongly tapering (battered) trunk** — widest
  at the ground, visibly pinching inward — topped by the unmistakable **4-blade
  sail CROSS**, an X of thin lattice arms radiating past the body into the side
  gutters. No other concept has radiating diagonal limbs; the X alone identifies
  it in blackout.
- **Construction:** Body is a single **battered trapezoid polygon** with vertical
  weatherboard seam lines + a couple of hooped string-courses; a rotatable
  **cap** as a small ogee polygon at the tip; the **sail cross** built from four
  lattice arms (a stock line + laddered whisker ticks, like a sparse `draw_ladder`)
  fanned at 45° from a hub; a tiny **fantail** paddle spur off the cap. Grass
  apron at the base.
- **Shape-language:** Squat, conical, ground-heavy, with hard diagonal lattice —
  the only radial/diagonal silhouette.
- **Palette:** `stone_mid`/`stone_dark` for the tarred weatherboard body (dark,
  matte); `stone_light` for the sail lattice "canvas" arms; `stone_accent` on the
  cap ogee + fantail; `foliage_top/mid` grass apron.
- **Column-fill:** The battered trapezoid fills the full width along its whole
  height (base = full w, cap shoulder still ~0.75 w) — the sails are **ornament
  spilling into the ±64 px gutters** over the solid core, never a substitute for
  body. Budget: plinth / battered body (elastic bulk) / cap + sail hub at tip.
  Mirrors as an X either way up.

## 3. `civic-clocktower`
**KIND tag:** straight-square-shaft-with-belfry-clock-and-spire
**Thesis:** A town campanile — a ruler-straight square ashlar shaft that steps
out into a louvred belfry with a clock face, capped by a sharp pyramidal spire.

- **Silhouette-tell:** **Perfectly straight vertical sides** (no taper at all —
  the anti-lighthouse/anti-obelisk), then a **belfry that steps OUTWARD** (a
  wider overhanging box) before a **narrow pyramidal spike**. Blackout reads as a
  domino topped by a notch-out box and a triangle. The step-out shoulder + spike
  combo is unique here.
- **Construction:** Body is **stacked ashlar rects** (`_gradient_rect` vertical
  for volume) with quoined corner blocks + a mid **string course**; the belfry a
  wider rect with **tall round-arched louver** voids drawn as recessed dark
  niches (arc + rect, blind — never see-through); a **clock disc** (filled
  circle + rim + 12 tick marks + two hand lines) inset in the shaft face; a
  **pyramidal roof** polygon + orb-and-cross finial. Ivy trails on one corner.
- **Shape-language:** Rectilinear, straight, tall, terminating in a spike — the
  crisp-geometry pole.
- **Palette:** `stone_light` ashlar face, `stone_mid` body core, `stone_dark`
  louver recesses + roof shadow side; `stone_accent` for the gilt clock face,
  hands + finial; `foliage_mid/dark` corner ivy.
- **Column-fill:** Straight shaft is full-width for the entire bulk. The belfry
  overhangs (shoulder into gutters); the **pyramidal roof is only the top ~12 %**
  and its base spans the full belfry width, so the point sits at the gap with
  only a few px of side air (same as a pagoda finial). Budget: plinth / shaft
  (elastic bulk) / clock band / belfry / roof. Mirrors as a stalactite tower.

## 4. `sunspire-obelisk`
**KIND tag:** monolithic-tapered-needle-with-pyramidion
**Thesis:** A single incised monolith — one clean stone wedge tapering to a
gilded pyramidion, the leanest, sharpest tower in the roster.

- **Silhouette-tell:** A **single unbroken mass** with **dead-straight sloping
  sides** narrowing to a **sharp pyramidal point** — no eaves, no overhang, no
  shoulder, no disc. Blackout is a near-triangle needle: the minimalist,
  featureless wedge. Distinct from the *irregular lumpy* menhir (which is a rough
  blob) — this is ruler-precise and geometric.
- **Construction:** The whole shaft is **one tapering quadrilateral polygon**,
  volume from a lit-face / shadow-face split down the centerline (two-tone fill,
  `_shade`); a **pyramidion triangle** cap; incised detail = faint **vertical
  groove lines** + a sparse column of **glyph nicks** (tiny rects/dots) down the
  sunlit face; a subtle chisel bevel at the base. Almost no vegetation — a lone
  moss smear at the plinth.
- **Shape-language:** Gaunt, sharp, single-mass wedge — the austere pole.
- **Palette:** `stone_mid` body, `stone_light` sunlit face, `stone_dark` shadow
  face + glyph incisions; `stone_accent` gilds the pyramidion cap so the tip
  catches light; a whisper of `foliage_dark` at the base only.
- **Column-fill:** Taper is **capped** so the pyramidion base ≥ ~0.72 w — the
  wedge stays a fat solid column, never a filament; the pyramidion is only the
  top ~10–12 %. All detail is interior to the mass. Budget: plinth / tapered
  shaft (elastic bulk) / pyramidion. Mirrors as a plumb-bob point into the gap.

## 5. `battlement-keep`
**KIND tag:** blocky-crenellated-tower-with-machicolation-corbel
**Thesis:** A defensive corner keep — a broad rough-masonry block that flares on
corbels into a machicolated parapet with a jagged crenellated crown.

- **Silhouette-tell:** A **flat-topped block** whose top edge is a **row of
  square merlon TEETH** (crenellations), sitting on a **corbelled shoulder that
  flares OUTWARD** just below the crown (the machicolation). Blackout reads as a
  broad column with a comb of square teeth over a slight overhang — the only
  toothed/jagged top-edge in the set, and the anti-spike to the clocktower.
- **Construction:** Broad body of **rough irregular masonry** (staggered
  `draw_masonry_blocks`-style courses); a **machicolation corbel row** (line of
  small stacked brackets, like `_dougong_cluster` re-tuned) that steps the
  parapet proud of the wall; the **crenellations** as a height-adaptive loop of
  alternating merlon rects + crenel gaps along the top edge; **arrow-slit**
  crosses + a corner **clasping buttress** rect running the full height. Moss in
  the machicolation shadows, a small banner spur.
- **Shape-language:** Blocky, squat-to-medium, jagged crown — the heavy fortress
  pole.
- **Palette:** `stone_mid`/`stone_dark` rough wall, `stone_light` on the merlon
  tops + buttress edge; `stone_accent` for a banner/torch flame; `foliage_dark`
  moss packed in the corbel undershadow.
- **Column-fill:** Body is full-width solid the whole height (buttress reinforces
  one edge); the **crenel gaps are shallow notches in the top ~6–8 px edge
  only** — collision-solid below. The corbel flares into the gutters. Merlon
  COUNT scales with width so teeth never squash. Budget: battered plinth / wall
  (elastic bulk) / machicolation corbel / crenellated crown. Mirrors as a
  down-toothed keep.

## 6. `moai-monolith`
**KIND tag:** stacked-carved-face-monolith-with-pukao
**Thesis:** An ancestor stack — carved tuff heads piled into a knobbly column of
heavy-browed faces, crowned by a red scoria topknot.

- **Silhouette-tell:** A **column of stacked bulbous ovoids** with jutting
  **brow ledges and long straight noses** breaking the outline — an organic,
  lumpy, face-bearing stack. Blackout reads as knobbly stacked eggs with a
  cylindrical cap, unlike the smooth cairn pebbles (rounded, featureless) or any
  geometric tower. The brow/nose bumps in profile are the tell.
- **Construction:** A **height-adaptive stack of head units** (count keyed off a
  natural head height, like Songyue's eave rhythm); each head = an **ovoid
  polygon/ellipse** with a heavy **brow arc**, a **long nose wedge**, deep
  **eye-socket** recesses, a jutting chin lip, carved via `_shade` relief; heads
  flush-stacked so shoulders overlap; a **pukao** topknot cylinder caps the top
  head. Grass tufts sprout between the stacked shoulders.
- **Shape-language:** Organic, bulbous, stacked, irregular — the only living/
  carved-figure pole.
- **Palette:** `stone_dark` volcanic tuff body, `stone_mid` face planes,
  `stone_light` lit brow + nose ridge; `stone_accent` for the red pukao + coral
  eye inlays; `foliage_top/mid` grass tufts in the seams.
- **Column-fill:** Each head unit **spans the full column width** and stacks
  flush, so the body is solid top-to-bottom at any height; head COUNT (min 1)
  adapts to the section height so short sections show one big head and tall ones
  a taller stack. Pukao caps the tip at the gap. Budget: base plinth / N stacked
  heads (elastic) / pukao. Mirrors as an inverted ancestor stack (odd but valid
  — the roster's chorten mirrors the same way).

---

## CROSS-SET PINS (distinctness policing)

- **Round-taper is #1 ONLY.** Lighthouse is the sole smooth curved-side taper.
  #4 obelisk tapers with **dead-straight sides to a sharp point** (a wedge, not a
  curve) and has **no head, gallery, band, or dome** — so it can't collapse into
  the lighthouse. If a later render softens the obelisk's sides, it's failed.
- **#2 vs everything:** the windmill is the ONLY concept with **radiating
  diagonal limbs (the sail X)** and the ONLY steeply **battered squat cone**. No
  other concept may add sails or a strong ground-heavy batter.
- **#3 vs #5 (both angular/straight-sided):** clocktower **ends in a SPIKE**
  (pyramidal roof) and has a clock disc + arched louvers; keep **ends FLAT with
  square TEETH** (crenellations) and has arrow slits + a corbel flare. Spike-top
  vs toothed-flat-top must stay the divider — neither may borrow the other's
  crown.
- **#3 vs #4 (both terminate in a point):** clocktower's point is a **separate
  roof on a step-out belfry over a straight shaft**; obelisk is **one continuous
  tapering monolith** with no belfry/overhang/disc. The presence/absence of the
  belfry step-out is the pin.
- **#4 vs menhir (existing):** obelisk is **ruler-straight and geometric** with a
  crisp pyramidion + incised glyph grid; the shipped menhir is a **rough,
  irregular, lumpy** standing stone. Precise-wedge vs lumpy-blob.
- **#6 vs cairn (existing):** moai heads carry **brows, noses, eye sockets** that
  break the outline; the shipped cairn is **smooth stacked pebbles** with no
  facial relief. Face-bearing stack vs blank pebble stack.
- **#5 vs monastery (existing dressing):** keep is a **tall full-height crenellated
  tower body**; the monastery dressing is a **small squat cap building** — keep
  is not a whitewashed hut with a red gable.
- **Terminations spread (Cover-the-label):** dome (1), sail-hub cap (2),
  pyramidal spire (3), pyramidion (4), crenellated flat crown (5), pukao cylinder
  (6) — six different tips, all readable at the gap.
