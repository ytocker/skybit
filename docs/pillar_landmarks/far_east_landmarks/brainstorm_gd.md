# FAR-EAST-LANDMARKS — Phase A brainstorm (8 distinct pillar directions)

Brainstorm mode: concept directions only, NO finished render. Each direction is a
REAL, recognizable Far-East landmark, chosen so its blackout silhouette is
unmistakable and no two collapse. Span is **4 modern + 1 statue + 3 historic**,
**East + Southeast Asia**. The art-director culls these 8 down to 6.

Shared contract every concept will honour when rendered (same bar as the pagoda
set in `game/pillar_pagodas.py`):
- Every material is `_mix(palette[key], anchor, t)` with a lit / mid / shadow
  triad so the biome's day→night retint sweeps through — no raw RGB in the body.
- `_gradient_rect` on every panel; `_aa_polyline` for silhouette edges/lattice;
  `night halo` on beacons/spires/finials; statue faces via `_buddha_eye`.
- Body fills the ~58px collision column across 70–355px with no empty band >12px;
  mirror = vertical flip of a solid centred core.

Nothing here reuses a taken pagoda/stupa, Taipei 101, or an anime building.

---

## 1. `oriental_pearl` — Oriental Pearl Tower, Shanghai, CHINA (modern)
- **KIND silhouette tag:** spheres-threaded-on-a-tripod-spire
- **Thesis:** a rocket-string of glass pearls skewered on a three-legged mast — the
  most sci-fi silhouette in the row, all circles-on-a-line.
- **Silhouette-tell:** two big stacked spheres (a fat lower one, a mid one) + a
  tiny space-capsule bead, threaded on a thin central mast that splays into three
  slanting tripod legs at the base and tapers to an antenna needle up top. Circles
  on a stick — reads instantly, matches no other pillar.
- **Construction:** solid central mast as the spine; lower entertainment sphere
  (largest, wide) anchors the mid-column, upper sphere above it, capsule bead near
  the crown, needle finial. Tripod legs are drawn as thick relief struts fanning
  off the mast onto the base, backed by a dim recessed core so the leg triangle is
  never a hole.
- **Materials:** steel mast/legs → `_mix(palette['stone_light'], (198,206,218), .6)`
  cool-steel with a hard white specular streak; spheres a signature rose-glass
  `_mix(palette['stone_accent'], (216,98,120), .58)` lit/mid/shadow via a radial
  `_gradient_rect`, white hot-spot top-left; capsule bead carries a night halo.
- **Column-fill + mirror:** the two large spheres + the solid mast keep every band
  filled; the tripod fills the base. Mirror flips to a spire pointing down with
  spheres hanging into the gap — centred mast survives clean.
- **Cite:** https://en.wikipedia.org/wiki/Oriental_Pearl_Tower
```
   |          . needle
  (o)         . capsule bead
   |
  ( O )       . upper sphere
   |
 (  O  )      . lower sphere (fat)
  /|\         . tripod legs
```

## 2. `canton_twist` — Canton Tower, Guangzhou, CHINA (modern)
- **KIND silhouette tag:** twisting-hyperboloid-lattice-WAIST (hourglass)
- **Thesis:** a woven steel corset that pinches to a slim waist then flares — the
  only see-through, twisting-mesh silhouette in the set.
- **Silhouette-tell:** wide oval bottom, a narrow cinched waist two-thirds up, a
  flared upper oval, and a thin off-set antenna mast. The diagonal lattice spirals
  ~45° so the edges read as a twisted hourglass, not a straight tube.
- **Construction:** 24 `_aa_polyline` diagonals crossing over a dim inner-tube
  shade (so the transparent mesh still fills the column and the waist never opens a
  hole); horizontal ring hoops mark each floor; the mesh envelope IS the silhouette.
- **Materials:** steel lattice → `_bronze(palette)` / `_mix(palette['stone_accent'],
  (176,150,96), .55)` with a strong specular on the sun-side diagonals; inner tube a
  shadow triad step darker; at night the lattice takes a soft magenta→cyan beacon
  tint + halo on the mast (the real tower's colour-lit skin).
- **Column-fill + mirror:** waist is the risk — pinned to stay ≥ the collision
  width by treating the mesh+inner-tube as one solid envelope. Near-symmetric
  hourglass mirrors clean; the antenna is the only asymmetry, flipped with it.
- **Cite:** https://en.wikipedia.org/wiki/Canton_Tower
```
  \_/    flared top + mast
   X
  ) (    <- pinched waist
   X
  / \    wide base
```

## 3. `petronas_twins` — Petronas Twin Towers, Kuala Lumpur, MALAYSIA (modern)
- **KIND silhouette tag:** twin-tapered-shafts-joined-by-a-skybridge
- **Thesis:** two identical stepped steel minarets holding hands across a mid-air
  bridge — the only doubled, mirror-symmetric silhouette in the row.
- **Silhouette-tell:** two parallel ringed shafts that step-taper up to spike
  pinnacles, linked by a two-storey skybridge at mid-height; the negative gap
  between them is a tall thin slot, and the crown is a pair of needles, not one.
- **Construction:** eight-lobed ringed shafts (horizontal setback rings as
  `_gradient_rect` bands catching specular); skybridge as two angled struts + deck;
  a solid recessed podium base + a dim curtain-wall backing fills BEHIND the two
  towers so the slot between them reads as a shadowed recess, never a killzone hole.
- **Materials:** stainless steel + glass → `_mix(palette['stone_light'], (204,210,220),
  .58)` with a bright horizontal specular on each setback ring; glass spandrels a
  cooler shadow step; pinnacle needles carry night beacons + halo.
- **Column-fill + mirror:** twin shafts sit close to the column centre; backing +
  podium hold the column solid across the slot. Vertical flip mirrors the tapers
  downward and the bridge with them — symmetric pair survives.
- **Cite:** https://en.wikipedia.org/wiki/Petronas_Towers
```
  |^|   |^|   twin needle pinnacles
  |=|   |=|
  |=|===|=|   <- skybridge link
  |=|   |=|
  |###|###|   solid recessed podium
```

## 4. `marina_bay_boat` — Marina Bay Sands, Singapore, SINGAPORE (modern)
- **KIND silhouette tag:** boat-deck-balanced-on-three-splayed-legs
- **Thesis:** a ship stranded on top of three leaning pillars — a table-shaped,
  top-heavy silhouette that reads as nothing else here.
- **Silhouette-tell:** three curved towers that lean apart at the base and gather
  at the top, capped by ONE long horizontal boat-shaped SkyPark that cantilevers
  past the end tower — a wide flat "ship" crown on three splayed legs.
- **Construction:** the middle leg is the solid centred core; outer two legs read
  as relief grooves against a dim recessed atrium backing (so the two inter-leg
  gaps aren't holes). The boat deck is a wide overhanging crown (gutter overhang)
  on the centred core, with an infinity-pool lip line + palm nubs on top.
- **Materials:** pale concrete/glass legs → `_mix(palette['stone_light'], (208,212,214),
  .6)` with a soft vertical specular; the boat deck a darker banded `stone_mid`
  shadow triad so it reads as a heavy cap; deck-edge lights carry a faint night halo.
- **Column-fill + mirror:** middle leg + backing keep the column solid; the boat is
  the wide crown. Vertical flip drops the boat to the bottom and splays legs up —
  centred middle leg survives; crown overhang is gutter-only.
- **Cite:** https://en.wikipedia.org/wiki/Marina_Bay_Sands
```
 [====ship====]   long boat SkyPark (overhang)
   \   |   /       three splayed legs
    \  |  /
   [ recessed podium ]
```

## 5. `himeji_heron` — Himeji Castle, Hyōgo, JAPAN (historic)
- **KIND silhouette tag:** stepped-white-castle-keep with fanned gables
- **Thesis:** the "White Heron" — a tapering white plaster keep of stacked
  curved-and-triangular gables that read as a bird about to take flight.
- **Silhouette-tell:** a wide stone base, then five receding white tiers, each edged
  by dark tiled eaves that flare up at the corners; triangular chidori gables and
  curved kara gables fan across the face; gold shachihoko fish-finials crown the top
  ridge. A soft, many-gabled pyramid — no straight tower, no boat, no lattice.
- **Construction:** solid tapering keep block; each tier a `_gradient_rect` white
  panel between dark `_aa_polyline` eave curves; layered gable triangles as the
  face texture; base is battered stone masonry.
- **Materials:** white plaster → `_plaster(palette)` / `_mix(palette['stone_light'],
  (244,238,222), .58)` lit/mid/shadow; roof tiles a cool blue-grey
  `_mix(palette['stone_dark'], (86,96,116), .5)`; shachihoko finials `_gold_bright`
  with a small night glint; stone base `stone_mid`.
- **Column-fill + mirror:** solid wide-based keep fills the whole column, tiers step
  inward. Vertical flip = inverted keep pointing down, gables fanning into the gap —
  centred core survives.
- **Cite:** https://en.wikipedia.org/wiki/Himeji_Castle
```
    ^^      gold finials
   /##\
  /####\    stacked white gabled tiers
 /######\
[==base==]
```

## 6. `potala_fortress` — Potala Palace, Lhasa, TIBET / CHINA (historic)
- **KIND silhouette tag:** stepped-red-and-white batter-walled fortress mass
- **Thesis:** a solid mountain-palace — inward-sloping white flanks hugging a crimson
  central block, crowned by golden roofs; a fortress trapezoid, not a tower.
- **Silhouette-tell:** a broad trapezoid whose walls lean inward as they rise, rows
  of small dark tapering windows marching up the flat faces, a deep-red central
  palace set into white wings, and a cluster of flat golden pavilion roofs on top.
  Reads as a heavy stepped massif — the widest, most solid silhouette in the set.
- **Construction:** solid battered trapezoid; white wings and central red block as
  `_gradient_rect` faces; window rows as small `_iron_brown` trapezoids in a grid;
  gold flat-roof pavilions perched on the crown with a night glint.
- **Materials:** white walls → `_stupa_white(palette)` / `_mix(palette['stone_light'],
  (246,240,226), .6)`; central red palace `_vermilion` / `_mix(palette['stone_dark'],
  (150,44,40), .68)` lacquer-crimson triad; windows `_iron_brown`
  `_mix(palette['stone_dark'], (60,44,34), .7)`; roofs `_gold_bright`.
- **Column-fill + mirror:** the massive trapezoid fills the entire column trivially.
  Vertical flip inverts the trapezoid; centred red core + gold roofs survive.
- **Cite:** https://en.wikipedia.org/wiki/Potala_Palace
```
  [==gold roofs==]
  |white|RED|white|
  | . . |...| . . |   window rows
  |  batter walls  |   (widening to base)
```

## 7. `angkor_lotus` — Angkor Wat central tower, Siem Reap, CAMBODIA (historic)
- **KIND silhouette tag:** redented lotus-bud sanctuary tower (ogival prasat)
- **Thesis:** a single sandstone lotus bud — a fluted, redented conical spire rising
  from a stepped temple base; a bullet-beehive profile no other pillar shares.
- **Silhouette-tell:** an ogival (pointed-dome) tower with vertical redented ribs so
  the outline is a scalloped, tiered cone tapering to a lotus finial, sitting on a
  broad stepped-pyramid base with a steep central stair. Curvy-cone, not a straight
  taper, not a stack of eaves.
- **Construction:** solid centred spire built as receding redented tiers
  (`_aa_polyline` scalloped ribs), stepped square base widening to fill the bottom,
  steep stair line down the face, lotus-bud finial.
- **Materials:** weathered sandstone → `_mix(palette['stone_mid'], (154,142,112), .6)`
  grey-gold lit/mid/shadow, with `foliage_dark/mid` moss stain in the recesses;
  deep ribs `_iron_brown`; a warm gold dawn tint + faint halo on the finial.
- **Column-fill + mirror:** spire is a solid centred core; base tiers fill the base;
  ribs keep the taper from opening bands. Symmetric bud mirrors clean top↔bottom.
- **Cite:** https://en.wikipedia.org/wiki/Angkor_Wat
```
    (^)     lotus finial
   /|||\    redented ribbed cone
  /|||||\
 [==tiers==] stepped base + stair
```

## 8. `merlion` — Merlion, Marina Bay, SINGAPORE (statue / monument)
- **KIND silhouette tag:** lion-head-fish-body creature statue with a water spout
- **Thesis:** the wild-card outlier — an organic, asymmetric maned lion head over a
  coiled scaly fish tail, spouting a bright arc of water; nothing architectural
  about it, so it can never collapse into the towers.
- **Silhouette-tell:** a round maned lion head (open mouth, teeth, big eyes) up top,
  a thick scaled body curving down into a fluked fish tail that coils onto a rocky
  plinth, plus a translucent water-arc jetting from the mouth into the gutter.
- **Construction:** a solid centred figure core (head→body→tail) stacked to fill the
  column height; mane as radial `_aa_polyline` tufts; scales as `_gradient_rect`
  scallop rows; eyes via `_buddha_eye`; rock plinth at the base; water spout a pale
  cyan translucent overhanging arc that catches a night halo (the only glow).
- **Materials:** white cast-stone → `_stupa_white(palette)` / `_mix(palette['stone_light'],
  (240,236,226), .6)` with a firm lit/mid/shadow so the volume reads sculptural;
  scale rows a step-darker shadow triad; plinth `_iron_brown`; spout a cool
  `_mix(palette['stone_light'], (150,210,224), .5)` translucent + halo.
- **Column-fill + mirror:** the statue is deliberately stacked vertically (head, body,
  coiled tail, plinth) so it fills the tall column — NOT a squat statue; the water
  arc is gutter overhang only, on a solid centred body core. Vertical flip mirrors
  the creature head-down (reads as a playful hanging gargoyle); the coiled body core
  stays centred, plinth flips to the top.
- **Cite:** https://en.wikipedia.org/wiki/Merlion
```
  (lion head)~~~   water spout arc ->
   \body/
    )tail(         coiled scaly body
  [~plinth~]
```

---

## CROSS-SET PINS — distinctness policing (distinct-design-variants)

**Blackout (fill each solid black — must stay mutually unmistakable):**
- `oriental_pearl` = circles-on-a-stick (unique: only concept with discrete beads).
- `canton_twist` = pinched hourglass mesh (unique: only WAIST/negative-curve edge).
- `petronas_twins` = TWO shafts + a bridge (unique: only doubled silhouette).
- `marina_bay_boat` = wide horizontal cap on splayed legs (unique: only top-heavy
  table/ship profile).
- `himeji_heron` = fanned many-gabled white pyramid (soft stacked triangles).
- `potala_fortress` = broad inward-battered solid trapezoid (widest, flat-topped mass).
- `angkor_lotus` = scalloped ribbed cone / lotus bud (curvy pointed spire).
- `merlion` = organic asymmetric creature + spout (only non-architectural blob).

**Nearest-neighbour separations (the pairs a critic would suspect):**
- himeji vs potala vs angkor (the three historic): himeji TAPERS via stacked
  triangular gables (jagged pyramid); potala is a FLAT-topped inward-battered
  rectangle-trapezoid (no gables, no cone); angkor is a single CURVED redented cone.
  Base-to-top edge shape differs in kind — jagged / straight-slanted / scalloped-curve.
- oriental_pearl vs canton_twist (the two China tower-spikes): pearl = discrete
  beads on a thin straight mast; canton = continuous twisting mesh that necks at a
  waist. Bead-string vs corset — no overlap.
- petronas_twins vs marina_bay_boat (the two multi-leg SE-Asia moderns): petronas is
  a symmetric VERTICAL pair with a mid bridge (tall slot between); marina is a
  top-heavy HORIZONTAL boat cap over three splayed legs. Vertical-twins vs
  horizontal-crown — the mass sits at opposite ends.
- merlion vs himeji (both white, `stone_light`-based): SWAP test — recolour merlion
  in Himeji's blue-grey roof + gold finials and it still reads as a lion-fish, not a
  castle; construction (organic figure vs stacked gables) carries the ID, not palette.

**Swap test (palette can't be traded without breaking the read):** every concept's ID
lives in construction/silhouette, not colour — e.g. paint `potala_fortress` steel-grey
and it's still a battered trapezoid fortress, not Petronas; paint `angkor_lotus` white
and it's still a redented cone, not Himeji.

**Cover-the-label:** each thesis names a shape a player can call out cold — "the
pearl-tower," "the twisty one," "the twin towers," "the boat one," "the white castle,"
"the red palace," "the lotus temple," "the lion-fish." No two share a nickname.

**One-sentence:** each direction is stated above as a single silhouette sentence; none
is a re-dress of another — they differ in concept, blackout silhouette, construction,
and shape language, and span modern↔historic and East↔Southeast Asia.
