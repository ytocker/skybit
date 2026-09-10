# TOTEM / ancestral-idol pillar family — Phase A brainstorm (GD, brainstorm mode)

Seven genuinely distinct stacked-idol tower DIRECTIONS for Skybit, peers to the
shipped pagoda pillars. Each is a grand procedural pillar: the top section hangs
mirror-flipped from the ceiling (via the `_mirror_fill_tower` pattern already in
`pillar_pagodas.py`), the bottom rises from a 3-layer plinth on the ground, with
a flappable gap between. No finished render here — theses + build recipes only.
The art-director will cull these 7 to the best 5.

**How every concept hits the pagoda fidelity bar (shared spine).** Nothing paints
raw RGB on a body: every surface is `_mix(palette[family_key], anchor_rgb, t≈0.55–0.86)`
with a lit/shadow triad so it retints across the 5-min day→night biome cycle,
exactly like `_cedar`/`_basalt`/`_bronze`. Every panel gets a `_gradient_rect` so a
stacked head reads as a 3-D volume not a flat cutout; every silhouette edge gets an
`_aa_polyline` keyline with a 1-px drop-shadow. Faces derive from the `_buddha_eye`
model (white eye-pad → filled-polygon brow → colored iris → dark keyline) retinted
to each culture's paints, with recessed sockets/mouths via `_lit_niche` (which
already gives us the free night-lantern glow), PLUS a 2-dot thumbnail fallback so
the face still reads at the 58-px collision column. Each tower ends in a finial/crown
carrying a night halo, and each sits on the 3-layer plinth + `_draw_plinth_mist` +
ground foliage the pagodas use. Reused named materials: `_cedar`, `_vermilion`,
`_lacquer_red`, `_basalt(+_lit/_shadow/_accent)`, `_bronze`, `_gold_bright`. New
per-concept materials are named below, each anchored to a `stone_*`/`horizon` family
key so the biome retint sweeps through.

**Section contract every builder honors.** Body fills the ~58-px collision column
top-to-bottom with no empty band > 12 px, at any section height 70–355 px. The
stacked idol CORE is always the full-column load-bearing element; wings/beaks/hands
are gutter overhang only (they may exceed 58 px sideways, they never substitute for
column fill). Degrade-short rule is stated per concept (how many stacked units drop
out at 70 px and what single hero unit survives).

---

## 1 — `totem_formline`  ·  KIND-tag: WINGED PAINTED CREST POLE

**Thesis.** The bright one: a Pacific-NW cedar pole of stacked, boldly *painted*
crest beings — thunderbird crowning, then bear, raven, orca — in classic formline
red + black + teal, wings and beaks flaring into the gutters.

**Silhouette-tell (blackout).** The only WINGED pole in the set: a wide thunderbird
wing-span crown and out-thrust raven/eagle beaks break the vertical into a stepped
zig-zag of horizontal paddles. As a solid black shape it reads as a totem
*with arms out*, unmistakable against every other concept's near-straight column.

```
   /=====\        wing-span crown (thunderbird)
  ( (o)(o) )      formline ovoid eyes
   \__>__ /       out-thrust beak (gutter overhang)
  |[ bear  ]|
  |( (o)(o))|
  |__________|
  |[ raven ]==>   beak overhang
  |[ orca  ]|
 [===plinth===]
```

**Construction.** Own builder `_draw_totem_formline`. A repeatable *crest-being unit*
= a rounded-rectangle cedar block (`_gradient_rect`) + a big formline ovoid eye-pair
+ an appendage layer (wings / beak / fin) painted on top. The unit stacks bottom-up
to fill the section; the topmost unit swaps in the winged thunderbird. Formline is
its own primitive: `_ovoid()` (the fat-top/thin-bottom Northwest-coast egg drawn as a
filled polygon + inner ovoid) and `_u_form()` (the crescent/U split-shapes for
feathers and joints), both `_aa_polyline`-edged.

**Shape-language.** Rounded-BOLD + winged. Thick soft-cornered forms, everything
built from the ovoid; the anti-thesis of the moai's gaunt planes and the stele's
straight edges.

**Materials (named, palette-keyed).** `_cedar` (stone_dark) body already exists;
new `_formline_red` = `_mix(palette['stone_dark'], (176,44,38), 0.74)` — the primary
formline black-red on stone_dark so night stays warm; `_formline_black` =
`_mix(palette['stone_dark'], (26,24,26), 0.86)`; `_formline_teal` =
`_mix(palette['stone_light'], (60,150,150), 0.60)` (secondary blue-green); wing-tip
gilt reuses `_gold_bright` (stone_accent). Sky-reactive: the teal borrows a touch of
`horizon` so dawn/dusk warm it.

**Face-carving.** Straight `_buddha_eye` re-paint: white eye-pad → black formline
brow polygon → teal iris → red keyline, wrapped inside a painted ovoid socket rather
than a stone niche. Mouth = a `_u_form` lip in `_formline_red`. Thumbnail fallback:
the two ovoids collapse to a 2-dot teal-on-black eye-pair that still reads at 58 px.

**Column-fill.** Cedar block core is full-width (58 px); wings/beaks overhang the
gutters and never carry the column. Short (70 px): drop to a single thunderbird
hero unit — winged crown + one face — filling the whole stub.

---

## 2 — `moai_ancestor`  ·  KIND-tag: GAUNT SMOOTH BASALT MONOLITH

**Thesis.** The Easter Island direction, rebuilt ground-up at pagoda fidelity: a
stack of 3–4 smooth dark-basalt ancestor heads — heavy shelf brow, long straight
nose, thin pouting lip, jutting jaw — crowned with a red-scoria *pukao* topknot.

**Silhouette-tell (blackout).** The GAUNT column: a smooth, near-featureless
vertical with the signature moai profile notches — the long straight nose-ridge and
the under-cut chin/jaw shelf — and a single fat red drum (pukao) offset on top.
No wings, no beaks, no fret; the cleanest, most monolithic edge in the set.

```
   (####)      red scoria pukao (offset drum)
  |======|
  | .  . |     deep-shadow brow socket eyes
  |  ||  |     long nose ridge
  |  <>  |     thin pout lip
  |______|     jutting jaw shelf (undercut)
  | .  . |
  |  ||  |
 [==plinth==]
```

**Construction.** Own builder `_draw_moai_ancestor`. Repeatable *head unit* = a
trapezoidal basalt mass (`_gradient_rect`, wider jaw than crown) with relief carved
by LIGHT/SHADOW planes, not paint: a `_aa_polyline` nose-ridge catching a lit edge,
a `_lit_niche`-driven deep socket under the shelf brow, an under-chin shadow band.
Heads stack with a thin neck seam. Top head wears the pukao = a red-scoria cylinder
(own primitive `_pukao()` with a pitted top).

**Shape-language.** Gaunt + smooth + planar. Chisel-flat facets, zero ornament, all
form read through raking light — deliberately the austere opposite of #1 and #4.

**Materials.** `_basalt`/`_basalt_lit`/`_basalt_shadow`/`_basalt_accent` reused
straight (stone_mid/light/dark). New `_scoria_red` = `_mix(palette['stone_dark'],
(150,58,40), 0.72)` for the pukao (stone_dark so the red drum still reads warm at
night). Monochrome by design; the pukao is the only hue.

**Face-carving.** NOT `_buddha_eye` (moai eyes are hollow shadow, not painted) — the
eye is a `_lit_niche` socket under a filled-polygon brow shelf, giving the free
night-glow as ancestral "living eye". Nose + lip are lit/shadow polygon relief.
Thumbnail fallback: brow-shadow + two socket dots read the ancestor face at 58 px.

**Column-fill.** Trapezoid heads butt edge-to-edge = solid column by construction, no
overhang at all (safest fill in the set). Short (70 px): one oversized hero head +
pukao fills the stub.

---

## 3 — `sepik_spirit`  ·  KIND-tag: SPIKY HOOK-NOSE SPIRIT POLE

**Thesis.** A Papuan Sepik-River ancestor spirit-pole: gaunt long-faced spirits
whose enormous curving hook-noses sweep down to touch the lips below, ringed with
cowrie-shell eyes and a fibre/feather fringe — a bristling, organic, asymmetric idol.

**Silhouette-tell (blackout).** The HOOKED profile: each face's giant scroll-nose
curls outward and down like a bird-beak-crossed-with-a-scroll, and a tufted
feather/cassowary crown spikes off the top. Reads as a column *dripping with hooks
and quills* — spiky and irregular where the moai is smooth and the stele is straight.

```
  \|/|/\|/      cassowary quill crown (spikes)
  |( o o )|     cowrie-ring eyes
  |  (    |     huge hook-nose scrolling down...
  |   \_  |
  |_____v_|     ...to touch the mouth below
  |( o o )|
  ~fibre~~      fibre fringe (gutter overhang)
 [==plinth==]
```

**Construction.** Own builder `_draw_sepik_spirit`. Repeatable *spirit-mask unit* =
narrow ochre-wood plank (`_gradient_rect`) + a `_hook_nose()` primitive (a tapering
`_aa_polyline` scroll filled as a polygon, the concept's signature) + concentric
cowrie-ring eyes + a lime-white incised border. Between units, a `_fibre_fringe()`
primitive = short vertical hatch tufts (reuses the `_tile_hatch` hatch idea) hanging
into the gutter. Crown = a `_quill_crown()` fan of thin spikes with a night halo.

**Shape-language.** Spiky + gaunt + organic-asymmetric. Curved scroll-hooks and
irregular quills; nothing rectilinear, nothing bulbous — its own lane.

**Materials.** New `_sago_wood` = `_mix(palette['stone_dark'], (120,72,40), 0.76)`
(darker, redder than `_cedar` so it doesn't twin #1); `_ochre` =
`_mix(palette['stone_mid'], (188,120,52), 0.62)`; `_lime_white` =
`_mix(palette['stone_light'], (240,236,222), 0.60)` for incised lines + cowrie;
`_cowrie_cream` = `_mix(palette['stone_light'], (236,224,196), 0.58)` eyes. Accent:
`_bronze` (stone_accent) on the quill tips.

**Face-carving.** `_buddha_eye` retinted to cowrie: cream eye-pad → ochre brow →
dark iris → lime keyline, encircled by the concentric cowrie ring. Mouth is a
`_lit_niche` under the hook-nose tip. Thumbnail fallback: the two cowrie rings become
2 cream dots + one bold down-hook stroke — the hook alone identifies the concept at
58 px.

**Column-fill.** Plank core is full-width; hook-noses and fibre fringe are gutter
overhang. Short (70 px): one hero spirit-mask, hook-nose + quill crown, fills the stub.

---

## 4 — `jade_serpent`  ·  KIND-tag: ANGULAR STEPPED FANGED GUARDIAN

**Thesis.** A Mesoamerican feathered-serpent temple-guardian column: stacked
fanged serpent-jaw masks (Kukulkán) framed by stepped stone frets, carved in
glossy jade-green with gold and obsidian inlay — the polished, geometric idol.

**Silhouette-tell (blackout).** The STEPPED-ANGULAR one: hard right-angle Puuc
fret notches step the edges in and out like a ziggurat profile, and each mask's
upper serpent-jaw juts forward with a fanged snout. Reads as a rectilinear
notched column with beak-like jaws — all straight lines and 90° steps, the geometric
foil to #1's curves and #3's scrolls.

```
 [_|‾|_|‾|_]    stepped fret crown
 |[]==[]==[]|   fret-band
 | (O)  (O) |   ring eyes
 |  VvVvV   |   fanged serpent jaw (juts fwd)
 |[]==[]==[]|
 | (O)  (O) |
 |  VvVvV   |
[=== plinth ==]
```

**Construction.** Own builder `_draw_jade_serpent`. Repeatable *serpent-mask unit* =
jade block (`_gradient_rect`) + a `_fret_band()` primitive (the stepped Greek-key/
Puuc meander drawn as filled rects, its own signature) top and bottom + a
`_serpent_jaw()` primitive (a fanged trapezoid with `_aa_polyline` fang teeth
overhanging the gutter). Ring eyes = concentric circles. Gold inlay dots along the
fret; obsidian keylines.

**Shape-language.** Angular + stepped + glossy. Orthogonal frets, hard steps, high
specular — reads "cut stone / lapidary", distinct from every carved-wood concept.

**Materials.** New `_jade` = `_mix(palette['stone_light'], (72,150,120), 0.58)` +
`_jade_shadow` = `_mix(palette['stone_dark'], (28,74,60), 0.80)` + `_jade_lit` =
`_mix(palette['stone_light'], (150,210,180), 0.55)` (the specular gloss);
`_obsidian` = `_mix(palette['stone_dark'], (22,20,26), 0.86)` keylines; gold inlay
reuses `_gold_bright` (stone_accent).

**Face-carving.** `_buddha_eye` retinted jade→gold: jade eye-pad → obsidian brow →
gold ring iris → obsidian keyline. The "mouth" is the fanged `_serpent_jaw` with a
`_lit_niche` throat behind the fangs (night-glow = the serpent's lit maw). Thumbnail
fallback: 2 gold ring-dots over one fanged bar reads the guardian at 58 px.

**Column-fill.** Jade block + fret-bands are full-width, edge-to-edge; only the fang
snout overhangs. Short (70 px): one hero serpent-mask between two fret-bands.

---

## 5 — `tiwanaku_stele`  ·  KIND-tag: FLAT RECTILINEAR SLAB STELE

**Thesis.** An Andean carved-monolith stele (Tiwanaku Gateway/Ponce lineage): a
single broad flat SLAB incised with rows of low-relief square-eyed staff-god faces
haloed by radiating ray-appendages — grey andesite with faint cinnabar traces.

**Silhouette-tell (blackout).** The SLAB: not a round pole but a wide, flat,
straight-sided plank — the broadest, most rectangular block in the set — its only
edge-breaks the little rayed spokes fanning off each haloed face. Reads as a
standing tablet, instantly separable from every rounded/pole concept.

```
 [============]   flat broad slab (no taper)
 | *\ |[]| /* |   rayed halo spokes (small overhang)
 |   [#][#]   |   square-eyed staff-god face
 | *\ |[]| /* |
 |   [#][#]   |   incised low-relief rows
 |============|
[==== plinth ====]
```

**Construction.** Own builder `_draw_tiwanaku_stele`. NOT a stack of volumes but a
single slab (`_gradient_rect`, faint vertical taper) carrying a GRID of low-relief
faces incised by `_lit_niche` shadow-lines + `_aa_polyline` bright edges (relief is
1–2 px deep, all read through light). `_ray_halo()` primitive = short spokes (some
puma/condor-headed) radiating from each face into the gutter. Deliberately the only
non-stacked, monolithic-slab concept — its distinctness is the format itself.

**Shape-language.** Flat + rectilinear + low-relief. Everything incised and square;
no protruding volumes, minimal overhang — a carved tablet, the planar extreme.

**Materials.** New `_andesite` = `_mix(palette['stone_mid'], (128,124,116), 0.60)` +
`_andesite_lit`/`_andesite_shadow` from stone_light/dark; `_cinnabar` =
`_mix(palette['stone_dark'], (168,66,44), 0.66)` for faded pigment traces in the
recesses; `_bronze` (stone_accent) glints on the staff-god's staffs. Reads bare
grey stone with red ghosts of old paint.

**Face-carving.** Square-eyed staff-god variant of `_buddha_eye`: square andesite
eye-pad → incised brow → cinnabar square pupil → shadow keyline (rectilinear where
every other face is almond/round). Mouth = a bar-shaped `_lit_niche`. Thumbnail
fallback: 2 square shadow-pits + a rayed halo silhouette read the stele at 58 px.

**Column-fill.** The slab IS the column — full-width solid by definition, the most
robust fill of all; rays are the only gutter overhang. Short (70 px): one large
staff-god face + halo fills the slab stub.

---

## 6 — `kota_reliquary`  ·  KIND-tag: METALLIC OVAL-AND-CRESCENT GUARDIAN

**Thesis.** The metal one: a Kota (Bakota) reliquary guardian — a big concave OVAL
face sheathed in hammered brass and copper strips, crowned by a wide half-moon
crescent with side cheek-panels, over an open-lozenge body; ancestral idols stacked
as gleaming metal masks.

**Silhouette-tell (blackout).** The OVAL-AND-CRESCENT: a wide half-moon lunette over
a dished oval face flanked by curved cheek-wings, sitting on an open diamond
(lozenge) frame — a rounded T/anchor shape found nowhere else in the set. Reads
"mask on a diamond", the only concept whose body is an open frame not a solid pole.

```
   (  ‾‾‾  )     half-moon crescent crown
  \_( o o )_/    dished oval face + cheek-wings
     | ^ |       ridge nose
    /     \
   /  < >  \     open lozenge body (diamond frame)
   \  > <  /
    \     /
  [=== plinth ==]
```

**Construction.** Own builder `_draw_kota_reliquary`. Repeatable *reliquary unit* =
`_crescent()` primitive (filled half-moon, `_aa_polyline`-edged) + a dished oval face
(`_gradient_rect` with an inward concave shadow gradient — the signature "face
projects out of a hollow") + curved cheek panels + a `_lozenge_frame()` primitive
(open diamond of brass strips) linking to the unit below. Hammered texture = a fine
`_tile_hatch` stipple of brass rivets catching specular.

**Shape-language.** Metallic + rounded-geometric + open-frame. Sheet-metal sheen and
concave dishing; the only non-earthen (metal, not wood/stone/ceramic) finish — its
distinctness is material as much as shape.

**Materials.** `_brass_sheet` = `_mix(palette['stone_accent'], (198,164,86), 0.70)`
+ `_brass_lit` = `_gold_bright` reuse; `_copper_strip` =
`_mix(palette['stone_accent'], (176,104,66), 0.66)` for the alternating vertical
strips; `_bronze` (stone_accent) shadow; face-wood peeking = `_cedar` (stone_dark).
All-accent palette = it glows as the metal landmark at night without a niche.

**Face-carving.** `_buddha_eye` in metal: brass eye-pad → copper brow → dark iris →
bronze keyline, set in the concave dish so raking light rims one side. Mouth = a small
`_lit_niche` (the free glow = ancestor's breath). Thumbnail fallback: crescent
silhouette + 2 bright rivet-dots read the guardian at 58 px.

**Column-fill.** Face + cheek-wings fill full-width; the open lozenge body is the
tricky part — its diamond void would leave a hole, so the builder fills the lozenge
interior with a dark recessed `_gradient_rect` "shadow-box" (reads as depth, keeps
the column solid, no > 12 px gap). Short (70 px): crescent + oval face only, lozenge
dropped.

---

## 7 — `olmec_colossal`  ·  KIND-tag: BULBOUS BOULDER-HELMET HEAD STACK

**Thesis.** An Olmec colossal-head stack: massive rounded ancestor heads in
close-fitting ball-court helmets, with broad flat noses, thick everted lips and
almond eyes — carved in warm greenish basalt; boulders piled into a tower.

**Silhouette-tell (blackout).** The BULBOUS one: a stack of near-circular boulders,
each capped by a smooth rounded helmet dome with ear-flaps — a bumpy string of
spheres, the roundest, heaviest edge in the set. Where the moai is a gaunt vertical
and the stele is a flat slab, this is a fat beaded column of balls.

```
  (  ___  )      rounded helmet dome + ear-flaps
 ( ( o o ) )     almond eyes, broad flat nose
  ( \___/ )      thick everted lips
   (=====)       heavy jaw boulder
  (  ___  )
 ( ( o o ) )
  ( \___/ )
 [=== plinth ==]
```

**Construction.** Own builder `_draw_olmec_colossal`. Repeatable *colossal-head
unit* = a near-circular basalt boulder (`_gradient_rect` masked to an ellipse, big
soft form-shadow) + a `_helmet_dome()` primitive (rounded cap with a low-relief
ball-game band and two ear-flap lobes overhanging the gutters) + heavy-lidded almond
eyes + a broad flat-nose polygon + everted-lip relief. Boulders overlap slightly at
the seam so the stack reads as piled stone.

**Shape-language.** Bulbous + rounded + heavy-massive. All circles and soft lobes,
maximal visual weight — the bulbous extreme opposite the flat stele (#5) and the
angular jade (#4).

**Materials.** New `_olmec_basalt` = `_mix(palette['stone_mid'], (96,104,92), 0.64)`
— deliberately GREENER + warmer than `_basalt` so #7 and #2 never twin; plus
`_olmec_lit` = `_mix(palette['stone_light'], (150,156,140), 0.55)` and
`_olmec_shadow` = `_mix(palette['stone_dark'], (54,60,50), 0.80)`. Faint moss accent
`_mix(palette['stone_mid'], (110,140,86), 0.40)` in the helmet-band recess.
Monochrome-green, no paint.

**Face-carving.** `_buddha_eye` for the almond eye (basalt pad → heavy-lid brow →
dark iris → shadow keyline) but wide + heavy-lidded, not tall like Boudhanath. Nose
+ lips are big soft-shadow polygon relief; helmet band is a `_lit_niche` row.
Thumbnail fallback: rounded dome silhouette + 2 heavy-lid eye-dots read the colossal
head at 58 px.

**Column-fill.** Overlapping boulders butt seam-to-seam = solid full-width column;
only the ear-flaps overhang. Short (70 px): one giant colossal head + helmet fills
the stub (its roundness fills the column corners better than the gaunt moai — note:
tune the ellipse mask so basalt reaches the 58-px edges, no > 12 px corner gaps).

---

## CROSS-SET PINS — distinctness policing (7-way)

**Blackout test (solid-black silhouette must be unique):**
1 `totem_formline` = **winged** zig-zag (wings + beaks out). 2 `moai_ancestor` =
**gaunt smooth** vertical (nose-ridge + jaw notch, offset drum). 3 `sepik_spirit` =
**spiky/hooked** (down-curling scroll-noses + quills). 4 `jade_serpent` =
**stepped-angular** (90° fret notches + fang snout). 5 `tiwanaku_stele` = **flat
broad slab** (rectangular tablet + tiny ray spokes). 6 `kota_reliquary` =
**oval-and-crescent on a diamond** (open-frame body). 7 `olmec_colossal` = **bulbous
bead-string of balls**. Seven readable-apart silhouettes, no two share a profile.

**Shape-language spread (no two in the same lane):** winged-bold (1) · gaunt-smooth-
planar (2) · spiky-organic-scroll (3) · angular-stepped-glossy (4) · flat-rectilinear-
incised (5) · rounded-metallic-open-frame (6) · bulbous-heavy-massive (7).

**Swap test (parts are not interchangeable):** each concept has its OWN signature
primitive that would look wrong on any other body — `_ovoid`/`_u_form` (1),
plane-relief + `_pukao` (2), `_hook_nose`/`_quill_crown` (3), `_fret_band`/
`_serpent_jaw` (4), `_ray_halo` on a slab (5), `_crescent`/`_lozenge_frame` (6),
`_helmet_dome` boulder ellipse (7). Swapping a fret-band onto the moai or a hook-nose
onto the stele instantly breaks the read.

**Cover-the-label test (material/finish, not just label):** painted red/black/teal
on cedar (1) · cool grey basalt monochrome + one red drum (2) · red-ochre sago wood
+ lime + cowrie cream (3) · glossy jade-green + gold + obsidian (4) · bare grey
andesite + faded cinnabar (5) · hammered brass + copper (metal) (6) · warm GREEN
basalt (7). Finishes span painted-wood / raw-stone / ochre-wood / lapidary-gloss /
incised-stone / sheet-metal / mossy-stone.

**Watch-item flagged for the AD cull:** #2 `moai` and #7 `olmec` are both basalt
heads — the two closest cousins. They are pinned apart on THREE axes (silhouette:
gaunt-vertical vs bulbous-boulder; tone: cool-grey `_basalt` vs warm-green
`_olmec_basalt`; face: hollow-shadow socket vs painted almond `_buddha_eye`), so they
pass the blackout + cover-the-label tests independently. If the AD wants to trim to 5
and finds them too close in KIND, this is the pair to cut from first; otherwise the
set already spans 7 lanes.

**One-sentence test:** 1 "totem pole with its wings out" · 2 "smooth stone ancestor
faces with a red topknot" · 3 "spirit pole dripping with hook-noses and quills" ·
4 "green fanged serpent-god behind stone frets" · 5 "a carved standing stone tablet" ·
6 "a shining brass mask on a diamond" · 7 "a tower of round helmeted stone heads."
Each sentence fits exactly one concept.
