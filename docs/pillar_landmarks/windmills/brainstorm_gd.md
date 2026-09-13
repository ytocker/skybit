# Windmill Family — Brainstorm (graphics-designer, Phase A)

Seven genuinely distinct **wind-mill / wind-tower** directions, every one
**re-themed into Skybit's Asian / temple world** so the family reads as a peer to
the 11 shipped pagodas — NOT a European outlier. Same ROLE as every pillar (top
section hung mirrored from the ceiling, bottom rising from the ground, gap
between; the two halves are the SAME builder flipped) and the same grandeur. The
signature of each concept is its **mechanism** (radial sail-cross vs side
water-wheel vs stacked prayer-drums vs paper rosette vs vertical junk-sail comb
vs flag-line vs static wind-scoop crown) but the **temple-material BODY carries
the ~58 px collision column** top-to-bottom; the mechanism is gutter overhang.

This deliberately does NOT re-propose the shipped `smock-windmill` (a tarred grey
European drainage mill, flat single-colour sails) — that was the low-fidelity
outlier this family exists to replace. Every direction below is built to the
**pagoda fidelity bar** by reusing the ACTUAL `pillar_pagodas.py` helpers:

- **Materials — never raw RGB on a body.** `_mix(palette[family_key], anchor,
  t≈0.55–0.86)` + a lit/shadow triad, so day→dusk→night retints sweep through.
  Temple timber → `stone_dark` (`_cedar`, `_ochre_wood`+`_lit`/`_shadow`,
  `_vermilion`, `_toji_cypress`); stone/plaster body → `stone_light`/`stone_mid`
  (`_plaster`, `_white_plaster_warm`, `_stupa_white`, `_terracotta`,
  `_brick_mortar`); glazed roof tile → `_vn_tile_red`/`_bluetile`+`_tile_gloss`;
  metal cap/hub/vane → `stone_accent` (`_bronze`, `_gold_deep`, `_gold_laos`);
  paper sails → `stone_light` (`_plaster`); flags/water → `horizon`
  (`_pond_aqua` + horizon-tinted lungta colours).
- **Finish.** `_gradient_rect` on every panel; sails/wheels get a real
  lit/shadow SPLIT + `_tile_hatch` ribs/battens + `_aa_polyline` edges (never a
  flat fill); tiled caps via `_glazed_tile_checker`; `_dougong_cluster` under
  eaves; `_bronze` finial with a `_draw_sorin_flame_halo` night glow; niche/vent
  glow via `_lit_niche`; base = 3-layer plinth + `_draw_plinth_mist` +
  `draw_grass_bed`/`draw_side_shrub`.
- **Fill.** Body fills the full column at heights 70–355 px (no empty band
  >12 px) via `_fit_floors`/`_tier_bounds`/`_mirror_fill_tower`; each note states
  short-height degradation.

## Blackout strip (solid-black shapes — no two share a pole)

```
 1 PAVILION-MILL  2 WATERWHEEL   3 MANI-DRUM    4 SHOJI-ROSE   5 JUNK-SAIL   6 PRAYER-FLAG  7 WINDCATCHER
    /^\               ___            .vane.        __            \|/|/          ^              |^|^|^|
   /^^^\   \ /       /   \  ___     (=====)       /  \          |cage|         /|\    ~._     | | | |
  __|_|__   X       | brick|(( ))   (=====)      ( ((O)) )       |||||        /_|_\  ~. `-.   |=====|
 |  |  |  / \       | cone |(( ))   (=====)      |paper |        |||||       /white\    `-.~. |     |
 |  |  |           |battered|((_))   |post|      | slab |       /|||||\     /batter \  flags  |     |
 |__|__|           |________|        |___|       |______|      /_bamboo_\  /________\  line   |_____|
 tiered pavilion   brick cone +      fat drum     plaster slab  open cage +  steep white  tall square +
 + open sail-X     side WHEEL disc   stack + vane  + paper DISC  upright comb trapezoid+   scoop-crown
                                                                             flag catenary  (no sail)
```

Shape-language poles: **tiered-pavilion + open radial X** (1),
**battered brick cone + one big side disc** (2), **fat stacked-drum cylinder**
(3), **plaster slab + centred filled glowing disc** (4), **open lattice cage +
upright vertical comb** (5), **steep white trapezoid + soft drooping catenary**
(6), **tall straight square + slotted hooded crown, zero moving parts** (7).

---

## 1. `pavilion-mill`
**KIND tag:** tiered-pagoda-pavilion-body-with-open-radial-canvas-sail-X
**Thesis:** A wedding-cake pavilion tower whose tiled eaves shelter a milling
floor, throwing four open matting sails in a giant X across the gap.

- **Silhouette-tell:** The ONLY concept that pairs a **stepped multi-eave pagoda
  pavilion** (2–4 flared tiled roofs, widest at the base) with a **thin OPEN
  four-arm sail cross** — an X of narrow lattice arms with clear air between them,
  radiating past the body into both gutters. Blackout reads as a little pagoda
  wearing a saltire. Nothing else has radiating open diagonal limbs.
- **Construction:** Body = `_tier_bounds` storey stack of `_ochre_wood` posts
  framing `_white_plaster_warm` panels, each storey crowned by a flared glazed
  eave (`_eave_tang_curl`) with a `_dougong_cluster` bracket row underneath;
  glazed tile via `_glazed_tile_checker` on `_vn_tile_red`. A `_bronze` **hub
  boss** at the top-storey face carries four **sail arms** — each a stock
  centre-line with laddered whisker battens + a triangular `_plaster` canvas leaf
  along one edge (a jib-sail, not a solid paddle).
- **Shape-language:** Stepped, roofed, horizontal-eave rhythm crossed by hard
  diagonal limbs — the "temple that spins" pole.
- **Materials:** body timber `_ochre_wood` / `_ochre_wood_lit` /
  `_ochre_wood_shadow` (**stone_dark**); panels `_white_plaster_warm`
  (**stone_light**); glazed eaves `_vn_tile_red` + `_tile_gloss`
  (**stone_dark/light**); sail canvas `_plaster` (**stone_light**); hub + finial
  `_bronze` (**stone_accent**).
- **Sail/mechanism shading:** each arm gets a `_gradient_rect` lit/shadow SPLIT
  down the canvas leaf, `_tile_hatch` lattice ribs across the frame, and an
  `_aa_polyline` outer edge; the sunward two arms read a half-stop brighter than
  the shaded pair so the X has depth, not four identical sticks.
- **Column-fill + mirror:** the pavilion stack fills the full column at every
  height via `_mirror_fill_tower` (storey COUNT adapts; short 70 px → a single
  eaved cabin + hub). Sails are pure gutter overhang. The hub is CENTRED, so the
  flipped ceiling half keeps a legible X; arms are drawn per-section at a seeded
  angle so the top X isn't a pixel-identical mirror.

## 2. `waterwheel-mill`
**KIND tag:** battered-song-brick-temple-cone-with-side-mounted-vertical-wheel
**Thesis:** A river-shrine grist tower — a battered Song-brick cone with a big
spoked water-wheel turning on one flank, half-sunk into the gutter.

- **Silhouette-tell:** The ONLY concept with a **single large solid CIRCLE
  bolted asymmetrically to one side** of a **steeply battered brick cone** — a
  spoked/paddled wheel whose rim overhangs one gutter while the other stays
  clean. Blackout is a fat pyramid-cone with one round bulge stuck on its cheek.
  No radial X, no centred disc — the off-axis wheel is the tell.
- **Construction:** Body = `_terracotta`/`_brick_mortar` battered trapezoid with
  `_songyue_brick_band` string-courses and stacked `_songyue_dwarf_eave` corbel
  bands, a `_lit_niche` shrine door low on the shaft. On one flank a `_cedar`
  timber head-race launder feeds a **vertical wheel**: `_aa_polyline` twin rims,
  `_cedar` spokes, `_plaster` paddle-boards between them, `_bronze` axle boss.
  `_pond_aqua` splash + froth ticks where the wheel meets the plinth pool.
- **Shape-language:** Heavy, ground-rooted, conical masonry with one bold
  off-centre wheel — the industrial-shrine pole.
- **Materials:** brick body `_terracotta` + `_brick_mortar` (**stone_dark /
  stone_mid**); corbel/string bands via `_songyue_brick_band`; wheel frame
  `_cedar` (**stone_dark**); paddles `_plaster` (**stone_light**); axle `_bronze`
  (**stone_accent**); water `_pond_aqua` (**horizon**).
- **Sail/mechanism shading:** each paddle-board is an individual `_gradient_rect`
  lit/shadow cell so the wheel reads as a ring of dished buckets; twin `_aa_polyline`
  rims + radial spokes; the lower paddles darken toward `_brick_mortar` where they
  dip into the shaded pool, giving the wheel real rotation-depth.
- **Column-fill + mirror:** the brick cone fills the whole column (batter capped
  so the top shoulder ≥0.72 w); wheel is gutter overhang only. Short-height →
  cone stub + shrine niche + a smaller wheel. The wheel is CENTRED vertically on
  the flank, so a vertical flip keeps it a wheel on the ceiling half; the launder
  spout is drawn per-section so water always reads as falling toward the gap.

## 3. `mani-drum-tower`
**KIND tag:** stacked-rotating-prayer-drum-cylinder (the body IS the mechanism)
**Thesis:** A Tibetan mani-wheel tower — the "mill" is a fat stack of embossed
copper prayer-drums that spin on the wind, no sail at all bar a tiny top vane.

- **Silhouette-tell:** The ONLY **fat, near-cylindrical drum STACK** — a column
  of bulging horizontal-banded barrels (each drum wider in the middle) with a
  single small **cross-vane** on top. Blackout is a stubby ribbed cylinder, no
  radiating arms, no side disc, no filled sail-disc — the drum bulge rhythm is
  the tell. The anti-sail concept.
- **Construction:** `_fit_floors` count of **mani-drum units**, each an
  `_gradient_rect` copper cylinder with a `_lacquer_red` cap-and-base band, a
  `_saffron` pull-rope tick, and embossed mantra bands via `_tile_hatch`; the
  drums thread on a `_cedar` centre-post frame with corner uprights. Crown = a
  small `_bronze` **fantail cross-vane** + `_gold_deep` finial with a
  `_draw_sorin_flame_halo` night glow.
- **Shape-language:** Fat, ribbed, vertical-cylinder stack — the rounded,
  bulging, mechanism-as-body pole.
- **Materials:** drums `_bronze` / `_gold_deep` (**stone_accent**); band trim
  `_lacquer_red` (**stone_dark**); rope/accent `_saffron` (**stone_accent**);
  post frame `_cedar` (**stone_dark**); finial `_bronze` (**stone_accent**).
- **Sail/mechanism shading:** each drum is a horizontal 3-stop `_gradient_rect`
  (lit crown → mid belly → shadow foot) so the barrel reads cylindrical; the
  mantra `_tile_hatch` bands wrap with a 1-px `_gold_bright` specular on the
  sunward third; the tiny top vane gets its own lit/shadow split.
- **Column-fill + mirror:** drum COUNT adapts to height (min 1) so the barrel
  stack fills the full column solid at any section; short-height → one big drum +
  vane. The vane is CENTRED and the drums are horizontal bands, so a vertical
  flip is clean (mirrors as a hanging drum stack, vane pointing into the gap).

## 4. `shoji-rose-mill`
**KIND tag:** plaster-timber-lattice-slab-with-centred-glowing-paper-rosette
**Thesis:** A lantern-mill — a plastered temple slab whose sail is a full CIRCLE
of translucent shoji panels, a paper rose that glows amber at dusk.

- **Silhouette-tell:** The ONLY concept with a **large CENTRED filled disc** — a
  solid many-panelled paper rosette (an umbrella/fan wheel) hubbed on the tower
  axis, no open gutter air inside its rim. Distinct from #1's thin open X and
  from #2's off-axis wooden wheel: this is a symmetric filled paper disc, and it
  is the only mechanism that **emits light**. Blackout is a slab tower with a big
  solid coin at the gap.
- **Construction:** Body = `_plaster`/`_white_plaster_warm` slab framed by
  `_cedar` timber lattice posts + a low `_bluetile` glazed hip-cap
  (`_glazed_tile_checker`). The **rosette** = a radial fan of ~12 `_plaster`
  shoji leaves between `_cedar` mullion ribs, centred on a `_bronze` hub; a
  `draw_paper_lantern`-style cached radial glow blit behind it at dusk/night.
- **Shape-language:** Flat plaster slab crossed by a single bold luminous
  circle — the "paper-and-light" pole.
- **Materials:** slab `_plaster` / `_white_plaster_warm` (**stone_light**);
  frame `_cedar` (**stone_dark**); hip-cap `_bluetile` + `_tile_gloss`
  (**stone_dark/light**); paper leaves `_plaster` (**stone_light**); hub
  `_bronze` (**stone_accent**).
- **Sail/mechanism shading:** each paper leaf is a `_gradient_rect` lit/shadow
  wedge with `_cedar` `_aa_polyline` mullion ribs; the sunward semicircle is a
  half-stop brighter; at dark skies an additive amber halo (the `_lit_niche`
  glow technique) seeps through the whole disc so it reads as a back-lit lantern,
  not a flat pale coin.
- **Column-fill + mirror:** the slab fills the full column; the rosette is a
  centred overhang. Short-height → slab stub + a smaller rosette. Hub is CENTRED,
  so a vertical flip keeps a symmetric disc; leaf rotation is seeded per-section.

## 5. `junk-sail-mill`
**KIND tag:** open-bamboo-lattice-cage-with-vertical-axis-battened-junk-sail-comb
**Thesis:** A South-China vertical-axis mill — an open lashed-bamboo cage tower
ringed by a crown of upright battened junk sails standing like a fluttering comb.

- **Silhouette-tell:** The ONLY concept whose body is an **open, see-through
  bamboo LATTICE cage** (diagonal-lashed frame, not a solid wall) and whose
  mechanism is a ring of **UPRIGHT vertical sails** — a fluttering vertical comb
  around the crown, NOT a radial X, NOT a disc, NOT a side wheel. Blackout reads
  as an X-braced open trellis under a picket-fence of tall slatted flags.
- **Construction:** Body = `_ochre_wood`/`_toji_cypress` bamboo culms in an
  X-braced cage (posts + diagonal `_aa_polyline` lashings, node ticks), a solid
  `_plaster` milling-floor band low down so the collision core is never
  see-through. Crown = 6–8 **battened junk sails** stood vertical around a
  `_cedar` vertical shaft — each a `_vermilion` matting panel ribbed by
  horizontal `_aa_polyline` battens; `_bronze` cap ring.
- **Shape-language:** Airy, angular open trellis under an upright slatted fringe
  — the light, lattice pole.
- **Materials:** bamboo `_ochre_wood` / `_toji_cypress` (**stone_dark**); floor
  band + sail highlights `_plaster` (**stone_light**); junk sails `_vermilion` /
  `_vermilion_shadow` (**stone_dark**); shaft `_cedar` (**stone_dark**); cap
  ring `_bronze` (**stone_accent**).
- **Sail/mechanism shading:** each vertical junk sail is a `_gradient_rect`
  lit/shadow panel with horizontal `_aa_polyline` batten ribs (the junk-sail
  signature); the near sails overlap the far ones a half-stop brighter so the
  ring reads as a rotating cylinder of sails, not a flat fence.
- **Column-fill + mirror:** the cage looks open but a solid `_plaster` floor band
  + `_gradient_rect` core posts keep the collision column full (no gutter-visible
  band >12 px); short-height → one floor band + a short sail crown. The shaft is
  CENTRED and battens are horizontal, so a vertical flip is clean.

## 6. `prayer-flag-tower`
**KIND tag:** steep-battered-white-tibetan-trapezoid-with-flag-line-catenary
**Thesis:** A Himalayan wind-tower — a steeply battered whitewashed slab with a
crimson kham-beng frieze, its "sails" five-colour prayer flags swagging into the
gutters.

- **Silhouette-tell:** The ONLY concept with a **steep inward-battered white
  trapezoid** (a truncated pyramid slab, dead-straight sloping sides) whose
  mechanism is **soft drooping catenary flag-lines** — bunting that SAGS in a
  curve, not a rigid diagonal. Blackout reads as a fat wedge with thin swooping
  garland arcs to each side. Straight-batter body + soft-sag line is the tell.
- **Construction:** Body = `_stupa_white`/`_white_plaster_warm` battered
  trapezoid with a `_lacquer_red` kham-beng frieze band near the crown, a
  `_gold_laos` trim line, and `_lit_niche` trapezoidal windows. From the crown, 2
  flag-lines run out and down into each gutter as `_aa_polyline` catenaries hung
  with small square lungta flags.
- **Shape-language:** Massive straight-sloped white wedge crossed by soft textile
  arcs — the austere-mountain pole.
- **Materials:** body `_stupa_white` / `_white_plaster_warm` (**stone_light**);
  frieze `_lacquer_red` (**stone_dark**); trim `_gold_laos` (**stone_accent**);
  flags horizon-tinted lungta set — `_saffron`, `_lacquer_red`, `_gold_laos`,
  `_lapis`, `_plaster` each pulled toward **horizon** so they retint day→night;
  finial `_bronze` (**stone_accent**) with `_draw_sorin_flame_halo`.
- **Sail/mechanism shading:** each flag is a tiny `_gradient_rect` with a 1-px
  fold shadow and a printed-glyph `_tile_hatch` tick; the string is an
  `_aa_polyline` catenary that darkens at the sag; near-string flags overlap far
  ones for depth.
- **Column-fill + mirror:** the battered slab fills the full column (batter capped
  ≥0.7 w at the crown); flags are gutter overhang. Short-height → wedge stub +
  one short flag swag. **Mirror note:** flags are drawn PER-SECTION, not by raw
  flip, so the catenary always sags toward the gap on both halves (a naive
  vertical flip would make the ceiling swags arc upward and look wrong).

## 7. `windcatcher-tower`
**KIND tag:** tall-straight-square-badgir-with-static-hooded-scoop-crown
**Thesis:** A wind-catcher shrine tower — a tall straight square temple slab
crowned by a comb of hooded vertical wind-scoops; the wind is the mechanism, no
moving part at all.

- **Silhouette-tell:** The ONLY concept with **perfectly straight square vertical
  sides** (no taper, no batter) topped by a **slotted crown of tall hooded
  vertical scoops** — a comb of organ-pipe flues each with a tiled hood. Blackout
  reads as a domino stamped with a row of tall fin-slots at the top. No rotating
  disc, no sail, no wheel — the static scoop-crown is the tell, and it's the only
  concept that never moves.
- **Construction:** Body = `_white_plaster_warm` slab with `_cedar` corner posts,
  a mid string course, and `_lit_niche` shrine windows. Crown = 3–5 tall
  **wind-scoop flues** (`_gradient_rect` `_cedar` louvered hoods) each with a
  small `_vn_tile_red` glazed hood-cap and a **dark recessed vent mouth** that
  `_lit_niche` lights amber at night; `_bronze` ridge finials between flues.
- **Shape-language:** Tall, crisp, rectilinear straight shaft under a slotted
  vented crown — the vertical-flue pole.
- **Materials:** body `_white_plaster_warm` (**stone_light**); posts + hoods
  `_cedar` / `_ochre_wood` (**stone_dark**); hood-caps `_vn_tile_red` +
  `_tile_gloss` (**stone_dark/light**); vent glow via `_lit_niche` amber
  (**stone_accent**); ridge finials `_bronze` (**stone_accent**).
- **Sail/mechanism shading:** each scoop flue is a `_gradient_rect` lit/shadow
  hood with an `_aa_polyline` louver lip and a recessed dark mouth; the mouths
  read as quiet shadow by day and warm point-sources at night via `_lit_niche`'s
  three-stop halo ramp — the crown "breathes light" instead of spinning.
- **Column-fill + mirror:** the square slab fills the whole column (straight
  sides, full width); the scoop crown is only the top ~14 % and its base spans
  the full slab, so the gap end stays fully filled. Short-height → slab stub + a
  2-flue crown. Vent scoops are near-symmetric and CENTRED across the top, so a
  vertical flip mirrors cleanly (a down-hooded windcatcher into the gap).

---

## CROSS-SET PINS (distinctness policing)

- **Radial open X is #1 ONLY.** `pavilion-mill` is the sole concept with four
  thin open diagonal sail-arms (air between them). If a later render fills the X
  into a solid disc it has collided with #4; if it drops to a single side-arm it
  has collided with #2. Keep it an open saltire on a tiered pavilion.
- **The mechanism is a DIFFERENT object in every concept (Swap test):** open
  sail-X (1) / one off-axis wooden water-wheel (2) / stacked rotating copper
  drums, body-as-mechanism (3) / one centred glowing paper rosette disc (4) /
  ring of upright battened junk sails (5) / soft flag-line catenary (6) / static
  hooded wind-scoop crown (7). No two may borrow another's mechanism.
- **#2 side wheel vs #4 centred disc:** #2's circle is a WOODEN spoked/paddled
  wheel bolted OFF-AXIS to one flank (asymmetric bulge, half in one gutter, never
  glows); #4's circle is a PAPER rosette hubbed ON the tower axis (symmetric,
  centred, glows amber at night). Off-axis-wood vs centred-paper-glow is the pin.
- **#4 disc vs #1 X:** filled luminous paper coin vs thin open canvas saltire —
  a solid disc must never read as four sticks, and the X must never fill in.
- **#5 vertical comb vs #1/#4:** #5's sails stand UPRIGHT in a ring (a fluttering
  vertical fence around a vertical axis), not radiating (1) nor a flat disc (4);
  and #5 is the ONLY open see-through bamboo-cage body.
- **Body silhouettes are all different KINDS (Blackout):** tiered pavilion (1) /
  battered brick cone (2) / fat drum cylinder (3) / flat plaster slab (4) / open
  bamboo cage (5) / steep white battered trapezoid (6) / tall straight square
  slab (7). No two share a body pole. In particular #2 (battered brick cone) and
  #6 (battered white trapezoid) split on curve-vs-straight taper AND on
  colour/material (warm brick vs whitewash) AND on mechanism (side wheel vs flag
  line) — they can't collapse together.
- **#7 vs everything (Cover-the-label):** the windcatcher is the ONLY concept
  with NO moving part — remove every label and it's still identifiable by its
  slotted hooded-scoop crown on a ruler-straight square shaft. If a render bolts
  a sail or wheel onto it, it has failed its thesis.
- **Terminations spread:** open sail-hub (1), off-axis wheel + brick cone shoulder
  (2), fantail cross-vane + sorin finial (3), luminous paper rosette (4), upright
  junk-sail crown (5), flag-line + sorin finial (6), hooded scoop crown (7) —
  seven readable gap-end tips, none repeated.
- **None duplicates a shipped pagoda or the old `smock-windmill`:** every body is
  a temple material carried on the real `pillar_pagodas.py` helpers, and none is a
  grey tarred European cone with flat sails.
```
