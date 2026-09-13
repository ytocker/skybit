# TEMPLE-MILL family — Phase A brainstorm (GD, brainstorm mode)

Seed: `docs/pillar_landmarks/windmills/waterwheel-mill/render.py` — the battered
Song-brick river-shrine tower. We KEEP its temple bones and material family and
REMOVE the water-wheel entirely (no `_water_wheel`, `_launder_and_splash`,
`_pond_aqua`/`_ochre_wood`/`_cedar`). Each direction below reuses:
`_brick_cone` scan-line masonry, corbel string-courses (`_songyue_dwarf_eave`),
`_corbel_cap` + bronze finial at the gap rim, the `_matte_niche` shrine door, the
3-layer plinth + `_draw_plinth_mist` + `draw_grass_bed`/`draw_side_shrub`, and the
triad materials `_terracotta`/`_brick_mortar`/`_song_brick`/`_bronze`/
`_gold_bright`/`_plaster`/`_songyue_dwarf_eave`/`_tile_hatch`. The signature of
each is its NEW wind mechanism / crown — the wheel's replacement — and (user's
call) the body is re-shaped too, staying inside the brick-temple material family.

Proposing **7** genuinely distinct DIRECTIONS for the art-director to cull to 5.
No finished render here — theses + silhouette tells + rough ASCII only.

Palette contract shared by all: brick body = `stone_dark`/`stone_mid`
(`_terracotta`/`_song_brick`); metal crown/bells/vanes = `stone_accent`
(`_bronze`/`_gold_bright`); canvas/paper = `stone_light`; ribbons/streamers =
`horizon`/`_vermilion`. Every panel `_gradient_rect` + lit/shadow triad that
retints day→night; every silhouette edge `_aa_polyline`; the metal crown gets a
night halo gated on `_is_dark_sky` (day palettes never trigger it).

Geometry contract shared by all: MARGIN=70, PIPE_W=58, radial gutter clearance
~27px. The brick BODY fills the ~58px collision column top-to-bottom (no empty
band >12px, 70–355px); the mechanism is crown/gutter overhang; body + finial
carry the centreline to the gap rim. Ceiling twin = vertical flip of an upright
temp surface (flip preserves LEFT/RIGHT, inverts TOP/BOTTOM).

---

## 1. `sail-fan-mill` — KIND: cone + wide scalloped fan-sweep halo

**Thesis:** A grist-shrine that has spread a great oriental FAN of canvas
sail-leaves across its whole crown — one continuous 180° scalloped sweep, not a
handful of spokes.

**Silhouette-tell (blackout):** a fat brick pyramid whose top erupts into a wide
half-sunburst — a solid fan arc of ~11 overlapping leaf-blades spilling into both
gutters. Reads as "temple wearing a peacock fan." Nothing else in the set has a
filled arc crown.

**Body shape:** the seed's battered brick CONE, unchanged (the constant against
which the six re-shaped bodies are read).

**Mechanism + eye-catch:** a fan-hub just above `shoulder_y` on `cx` fans out a
tight overlapping row of tapered canvas leaves (each a `_gradient_rect` quad with
a bronze rib), lit rim to shaded rim across the sweep so the fan reads as a single
rotating vane-sheet catching a low sun. Eye-catch = the biggest, most saturated
silhouette footprint of the set; the scallop edge is unmistakable at 58px.

**Materials:** leaves = canvas `stone_light` (`_plaster`) over a shaded backing;
ribs + hub = `_bronze`/`_gold_bright` (`stone_accent`); a `_vermilion` (`horizon`)
tip-band ties the fan to the shrine. Night halo on the bronze hub + rib tips.

**Column-fill + mirror:** cone fills 58px as in the seed; fan is pure crown/gutter
overhang. The fan is bilaterally symmetric about `cx`, so the vertical flip leaves
it reading as a fan on the hung twin (leaves point up on the ceiling copy — still a
clear fan-sweep).

```
        _.-~|~-._            .-'''''-.
     .-~   /|\   ~-.        (  fan     )
   (  \  / | \  /  )   →   =============  crown
    \  \/  |  \/  /        /###########\  cone
     |  \  |  /  |        /#############\
     |__|__|__|__|       /###############\
```

---

## 2. `furin-ring-mill` — KIND: drum + hanging bell-carousel ring

**Thesis:** A round brick bell-drum ringed by a spinning carousel of bronze
wind-bells (fūrin) that swing and chime as the wind turns the ring.

**Silhouette-tell (blackout):** a stout CYLINDER whose crown wears a wide
horizontal ring from which a row of little teardrop bells DANGLE, evenly spaced,
into both gutters. Reads as "drum with a fringe of hanging droplets." The only
concept whose crown silhouette is a row of discrete pendant teardrops.

**Body shape:** a cylindrical brick DRUM — straight flanks (near-zero batter),
capped by a corbel ring instead of a taper, so its blackout differs hard from the
five tapering bodies.

**Mechanism + eye-catch:** a bronze carousel armature rings the crown at
`shoulder_y`; ~8 fūrin bells hang on short cords, each a bronze cup + a paper
tan-zaku slip (`stone_light`). Alternating cords are drawn at swing-left / swing-
right offsets to freeze mid-chime motion. Eye-catch = rhythmic sparkle ring of
warm metal that catches a night halo brilliantly.

**Materials:** drum courses = `_song_brick`/`_terracotta` (`stone_dark`/
`stone_mid`); bells + ring = `_bronze`/`_gold_bright` (`stone_accent`); paper
slips = `stone_light`; slip print tick = `_vermilion` (`horizon`). Night halo on
the bell ring.

**Column-fill + mirror:** the straight drum trivially fills 58px full-height; the
bell ring is crown/gutter overhang. Bells hang DOWN in the upright; under vertical
flip they'd point UP — so draw the carousel as bells radiating from the ring with
a symmetric up/down pair per station (a chime cluster), or accept that on the hung
twin the bells read as chimes rising toward the ring (still a bell-carousel).
Flagged as a real mirror choice.

```
   o o o o o o o          o = swinging bells on a ring
  =================   ←── carousel ring at the crown
  | ||||||||||||| |
  | ||  DRUM  ||| |       straight cylindrical brick drum
  | ||||||||||||| |
  |_|||||||||||||_|
```

---

## 3. `vane-star-mill` — KIND: stepped ziggurat + gilded pinwheel star

**Thesis:** A stepped altar-tower crowned by a flat gilded PINWHEEL — a radial
star of curved gilt vanes spinning face-on to the viewer like a sun-disc.

**Silhouette-tell (blackout):** a receding STAIR-STEP pyramid topped by a bold
pointed STAR rosette (curved swept points, full 360°). Reads as "ziggurat with a
spinning star." Distinct from #1's filled fan arc (this is a pointed radial star,
not a swept sheet) and from the retired sibling's open sail-X (this is a solid
gilt rosette, not four bare sails).

**Body shape:** a STEPPED brick ziggurat — 3–4 receding square courses, each a
`_gradient_rect` slab with a `_songyue_dwarf_eave` lip, instead of a smooth cone.

**Mechanism + eye-catch:** a face-on pinwheel on `cx` above the top step: ~10
curved gilt vanes swept from a bronze boss, each vane a lit→shadow gradient quad
so the whole star looks caught spinning; a `_vermilion` back-disc peeks between
vanes for pop. Eye-catch = a literal spinning gold star, the highest-value hit in
the set, screaming "power/reward."

**Materials:** steps = `_terracotta`/`_song_brick` (`stone_dark`/`stone_mid`);
vanes + boss = `_gold_bright`/`_bronze` (`stone_accent`); back-disc = `_vermilion`
(`horizon`). Night halo on the vane star.

**Column-fill + mirror:** stepped courses each span ≥PIPE_W/2 so the column stays
full (steps are wider than the collision band; the recess is above-column crown).
The pinwheel is a centred radial rosette → vertical flip is near-invariant; it
reads as the same star on the hung twin.

```
        \ | /
       -- * --          gilt pinwheel star (face-on)
        / | \
      __________
     |__STEP 3__|        receding stepped brick ziggurat
    |___STEP 2___|
   |____STEP 1____|
```

---

## 4. `streamer-whirl-mill` — KIND: mini-pavilion + whirling ribbon spray

**Thesis:** A little roofed brick shrine whose rooftop mast flings a WHIRL of long
prayer-streamer ribbons that flow and snap outward on the wind.

**Silhouette-tell (blackout):** a small pitched-roof PAVILION box atop the shaft,
sprouting a spray of long trailing tails that curl into both gutters. Reads as
"shrine with flowing streamers" — the only soft/linear crown in a set otherwise
made of rigid metal and canvas. Its blackout is airy tails, not a solid mass.

**Body shape:** a MINI-PAVILION — the brick shaft carries a small square shrine
room with its own `_songyue_dwarf_eave` pitched roof, then continues to the finial
above it (roofed-box interruption of the cone).

**Mechanism + eye-catch:** a slim bronze mast above the pavilion roof anchors ~7
long ribbons drawn as tapering `_aa_polyline` S-curves at staggered phase, some
snapping taut, some rippling — a frozen whirl. Eye-catch = motion and colour: the
only concept that reads as actively FLUTTERING, with the richest `_vermilion`/
`horizon` colour story.

**Materials:** pavilion + shaft = `_terracotta`/`_song_brick`; roof tiles =
`_songyue_dwarf_eave` + `_tile_hatch`; mast + finial = `_bronze`; ribbons =
`_vermilion` warm + `horizon` cool alternating (`horizon`), tipped `stone_light`.
Night halo only on the bronze mast tip (ribbons stay matte cloth).

**Column-fill + mirror:** shaft + pavilion box fill 58px; the roof pitch stays
≥PIPE_W/2 at its eave so no empty band opens under it; ribbons are gutter overhang.
Ribbons have a wind direction — draw them radiating in a balanced whirl about the
mast (not all one way) so the vertical flip still reads as a whirl (tails sweep
outward on both halves); flagged as a deliberate mirror-safe layout.

```
       \\\ | ///
        \\ | //           whirling prayer-streamer ribbons
      ___\_|_/___
     /  ^^^^^^^  \         mini-pavilion (pitched shrine roof)
     |  | shrine |  |
     |__|_______|__|
        | shaft |
```

---

## 5. `roof-turbine-mill` — KIND: faceted tower + stacked flared-eave turbine

**Thesis:** A polygonal Songyue-brick tower crowned by a STACK of spinning
pagoda-roof eaves — three or four flared tile-roofs nested into a vertical-axis
turbine that the wind spins as one hat.

**Silhouette-tell (blackout):** a faceted brick tower topped by a nested
Christmas-tree of FLARED concave-curve roofs, each smaller upward, each eave
kicking out past the last. Reads as "pagoda hat that turns." Distinct from #1's
convex fan-sweep and #3's pointed star — this crown is a stack of downward-swept
eave curves.

**Body shape:** a faceted/octagonal brick TOWER (the real Songyue idiom is a
12-sided brick pagoda) — vertical facet seams down a barely-battered shaft, unlike
the smooth cone or round drum.

**Mechanism + eye-catch:** 3–4 stacked flared eaves (`_songyue_dwarf_eave` scaled
up), each ringed with `_tile_hatch` tile-ends and a bronze drip-edge, mounted on a
central shaft so the whole stack reads as one turbine; corner bronze bell-nubs at
each eave tip catch light. Eye-catch = architectural grandeur — the tallest, most
"landmark" crown, a spinning pagoda in miniature.

**Materials:** tower + eaves = `_song_brick`/`_terracotta` with `_tile_hatch`
coursing; drip-edges + corner nubs = `_bronze`/`_gold_bright` (`stone_accent`);
under-eave shadow = `_shade`d `stone_dark`. Night halo on the bronze drip-edges +
corner nubs.

**Column-fill + mirror:** the tower shaft fills 58px; each eave's inner ring stays
≥PIPE_W/2 so no sky peeks between roofs (brick disc behind each). The eave stack is
a centred axial cone of rings → vertical flip inverts it to an upward-flaring
stack; note it reads as an inverted-pagoda finial on the hung twin (acceptable
temple motif) OR mirror the eave curl so both halves flare down — flagged.

```
        _===_              stacked flared pagoda-roof turbine
      _/=====\_
    _/=========\_
   |   ||||||   |
   |   FACET    |          faceted (octagonal) brick tower
   |   TOWER    |
   |__||||||||__|
```

---

## 6. `phoenix-vane-mill` — KIND: slender spire + great gilded weathervane bird

**Thesis:** A tall slim shrine-spire topped by a single COMMANDING gilded
weathervane — a spread-winged phoenix that swings to face the wind.

**Silhouette-tell (blackout):** a needle-thin brick spire under one large, clearly
FIGURAL bird — spread wings, arched neck, trailing tail plume. Reads as "temple
with a golden phoenix perched on its spike." The only concept whose crown is a
recognizable creature, not geometry.

**Body shape:** a slender TAPERED SPIRE — a taller, thinner battered cone than the
seed, so the eye is led up to the perched creature (needle body, big figure).

**Mechanism + eye-catch:** a bronze staff on `cx` above the finial carries a
spread-winged phoenix cast in gilt — wings as `_aa_polyline` feather fans, a
`_vermilion` crest and tail streamers that flutter. Eye-catch = a single hero
emblem, the most characterful/premium silhouette; a strong night halo makes the
gold bird glow like a shrine icon.

**Materials:** spire = `_terracotta`/`_song_brick`; bird body + wings =
`_gold_bright`/`_bronze` (`stone_accent`); crest + tail streamers = `_vermilion`
(`horizon`); eye glint = `stone_light`. Strong night halo on the gilt bird.

**Column-fill + mirror:** the slender spire must be batter-capped so even its thin
shoulder stays ≥PIPE_W/2 (the collision column is carried by masonry, not the
bird). MIRROR RISK — biggest of the set: a figural bird has clear up/down; a
vertical flip hangs it UPSIDE-DOWN. Resolution options to render: (a) make the
phoenix a spread-winged, near-vertically-symmetric medallion (wings up, tail down,
head centred) that survives the flip, or (b) embrace it — the hung twin reads as a
DIVING phoenix descending from the ceiling shrine (a deliberately different, still-
on-theme pose). Will be noted explicitly on the round sheet.

```
        <\_@_/>            spread-winged gilded phoenix vane
          |||
          /|\
         / | \             slender tapered brick spire
        /  |  \
       /___|___\
```

---

## 7. `parasol-crown-mill` — KIND: squat pedestal drum + domed parasol canopy

**Thesis:** A low shrine pedestal crowned by one huge rotating temple PARASOL — a
smooth ribbed dome with a scalloped hanging fringe that turns like a canopy in the
wind.

**Silhouette-tell (blackout):** a short brick pedestal under a single wide smooth
DOME with a scalloped skirt-fringe hanging around its rim into both gutters. Reads
as "temple under a giant umbrella." Distinct from #5's multi-tier zigzag eave-stack
(this is ONE smooth convex dome) and from #1's flat fan (this is a 3-D canopy with
a hanging fringe, not a flat spread).

**Body shape:** a SQUAT DRUM-and-necking PEDESTAL — a short, wide brick base with a
corbelled neck, deliberately low so the broad parasol dominates the silhouette
(inverse proportion to the tall spire of #6).

**Mechanism + eye-catch:** a domed parasol on `cx`: ~9 `_aa_polyline` rib arcs from
a bronze crown-knob down to a scalloped `_vermilion`/`stone_light` fringe, the dome
panels `_gradient_rect`-shaded lit→shadow so it reads round and turning. Eye-catch
= the boldest single convex shape in the set, a warm canopy that feels sheltering
and regal; night halo rings the crown-knob and rib tips.

**Materials:** pedestal = `_terracotta`/`_song_brick`; dome panels = canvas/paper
`stone_light` (`_plaster`) with bronze ribs (`stone_accent`); fringe scallops =
`_vermilion`/`horizon`; crown-knob = `_gold_bright`. Night halo on knob + rib tips.

**Column-fill + mirror:** the squat wide pedestal easily fills 58px (its risk is the
opposite — keep it from over-widening the plinth); the parasol is crown/gutter
overhang. The dome + fringe are bilaterally symmetric about `cx` → vertical flip
leaves a clean canopy (dome points up on the hung twin, fringe reads at the gap
rim — still an obvious parasol). Cleanest mirror in the set alongside #1/#3.

```
       ___-~~~-___         smooth ribbed parasol dome
     /~  |  |  |  ~\       with a scalloped hanging fringe
    v_v_v_v_v_v_v_v_v
        |     |            corbelled neck
      __|_____|__
     |__PEDESTAL_|         squat wide brick pedestal (drum)
```

---

## CROSS-SET PINS (distinctness policing across the 7)

**Blackout test — each crown is a different KIND of shape:**
| # | slug | crown silhouette KIND | body silhouette KIND |
|---|------|----------------------|----------------------|
| 1 | sail-fan | filled convex FAN ARC (180° sweep) | tapered cone |
| 2 | furin-ring | row of hanging PENDANT TEARDROPS on a ring | straight cylinder |
| 3 | vane-star | pointed RADIAL STAR rosette (360°) | stepped ziggurat |
| 4 | streamer-whirl | airy SPRAY of trailing TAILS | mini-pavilion box |
| 5 | roof-turbine | nested ZIGZAG of flared eaves | faceted tower |
| 6 | phoenix-vane | a FIGURAL CREATURE | slender needle spire |
| 7 | parasol-crown | ONE smooth convex DOME + fringe | squat wide pedestal |

No two crowns share a silhouette KIND; no two bodies share a silhouette KIND.

**Swap test (could crown A sit on body B and be the same concept?):** No — each
mechanism is welded to a body whose proportion sells it: the fan needs the tall
cone's shoulder to fan from; the bell-ring needs the drum's flat crown to ring; the
star needs the ziggurat's flat top step; the ribbons need the pavilion mast; the
eave-turbine needs the tower's height; the phoenix needs the spire's lead-the-eye
slimness; the parasol needs the squat pedestal's inverse proportion. Swapping any
crown onto another body breaks the read.

**Cover-the-label test:** name each by silhouette alone — "the fan," "the bell
fringe," "the gold star," "the streamers," "the pagoda hat," "the phoenix," "the
umbrella." All seven survive without their captions.

**One-sentence test:** each thesis is one plain sentence naming a different real
temple/wind object (fan, wind-bell, pinwheel, prayer streamer, pagoda roof,
phoenix vane, parasol) — no two describe the same object.

**Guard vs the retired sibling set (must NOT echo):**
- pavilion-mill's radial sail-X → #1 is a FILLED overlapping fan sweep, not 4–5
  bare open sails; #3 is a SOLID gilt rosette, not open canvas spokes.
- mani-drum's copper drum stack → #2/#7 use a single brick drum/pedestal, and #5's
  vertical stack is flared ROOF EAVES (concave curves), not stacked copper cylinders.
- shoji-rose's glowing paper disc → nothing here is a flat glowing disc; the closest
  (parasol dome) is a 3-D convex ribbed canopy with a hanging fringe, and glow is
  clamped to a gated night halo on METAL only, never an emissive paper face.
- junk-sail's bamboo cage → no open lattice/cage crown appears in the set.

**Mirror risk ranking (for the AD to weigh):** cleanest = #1, #3, #7 (bilateral
about `cx`, flip-invariant). Mid = #2, #4, #5 (directional elements to be laid out
balanced/radial for a mirror-safe read). Highest = #6 phoenix (a figural creature
flips upside-down — resolve by symmetric-medallion pose or embrace a diving-phoenix
hung twin; called out explicitly).
