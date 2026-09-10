# Skull-King — 8 new skulls · BRAINSTORM (directions only, no full render)

Eight new ~24px procedural skulls for `docs/skull_king_stack/skulls_individual.png`,
same Asthi-Dakini house grammar (flat saturated fills, hard INK keyline, dark-core →
fill → top-left sheen triad, 1px grown outline, chibi scary-cute) and the same value
ladder (cyan focal brightest → mid bone → CROWN_BONE tier dimmest).

## What I must NOT duplicate (the existing 14)

Every one of the shipped 14 skulls — 6 CROWN, 6 PALM, 2 round-9 — is the **same base
build**: one rounded dome cranium + a trapezoid jaw + **two round eye sockets** + a
horizontal tooth bar, varied ONLY by dome width/height/lean, suture style (dots/zig/
line), brow on/off, jaw set/agape/cracked, tooth count/chip, and at most one cyan pip.
So "another dome with a different suture" is a DUPLICATE by the doctrine. My 8 break
that build at the **anatomy/silhouette** level — different cranium topology, different
socket count/shape, added structural appendages, or a different read of "what a skull
is." Distinctness lives in the **blackout outline first**, ornament second.

## The MIX (4 WILD · 4 CROWN-RELIC)

| # | slug | flavor | one-word silhouette hook |
|---|------|--------|--------------------------|
| 1 | horned-ram-reliquary   | WILD        | two spiral horns sweeping wide |
| 2 | antler-crown-stag      | WILD        | branched antler rack on top |
| 3 | sabertooth-fanged-maw  | WILD        | two long down-fangs below jaw |
| 4 | third-socket-cyclops   | WILD        | tall single-socket teardrop dome |
| 5 | longjaw-relic          | CROWN-RELIC | deep elongated mandible (horse-skull read) |
| 6 | cracked-half-relic     | CROWN-RELIC | asymmetric vertical break, one side sheared |
| 7 | flat-brow-slab-relic   | CROWN-RELIC | low boxy flat-topped cranium |
| 8 | conical-peak-relic     | CROWN-RELIC | tall pointed dome, narrow temples |

---

## WILD HALF (4) — bold crania, rich ornament, full palette

### 1 · `horned-ram-reliquary`  (WILD)
- **Thesis:** A ram-skull reliquary — the skull's identity IS the pair of thick spiral
  horns curling out from the temples, the cranium almost incidental beneath them.
- **Silhouette:** Reads as a wide **"omega" / curled-bracket** shape — two fat spirals
  bulging out past the cranium on both sides, far wider than tall. Nothing else in the
  set is horizontally horn-dominant; blackout is unmistakable (two curl-lobes flanking
  a small central lump).
- **Construction/anatomy:** Small low cranium; the build budget goes into two **spiral
  horn ribbons** (a thickening polyline coiling ~1.25 turns out from each temple).
  Short muzzle, narrow set jaw — deliberately under-built so the horns own the shape.
- **Ornament + primitives:** Horn ridges carved with `bead_strand` (pale bone beads as
  the horn's growth-rings) + `GOLD`/`GOLD_D` spacer-pips at the curl tips; a single
  `cyan_gem(focal=False)` cabochon set in the brow boss between the horns; `triad_blob`
  spiral ribbons with `BONE_DD` socket pits. Full bone tier (mid value).

```
   ((@))   <- spirals dominate, small skull between
  ( o o )
   \___/
```

### 2 · `antler-crown-stag`  (WILD)
- **Thesis:** A stag-king skull whose crown is a branched **antler rack** — the skull
  wears bone like a tree, not like a tiara.
- **Silhouette:** A spiky **upward-branching candelabra** above a normal-ish skull —
  4–6 tine forks reaching up and out. Distinct from #1 (horns go UP and branch, not
  sideways-spiral) and from everything else (only design with a tall jagged crown of
  separate spikes). Blackout reads as antler tines, not a dome.
- **Construction/anatomy:** Standard chibi cranium as the BASE, but topped with a
  symmetric **antler armature** — two main beams off the crown, each splitting into 2–3
  tines of decreasing length. The vertical spread roughly doubles the bounding box
  height; that tall spiky top is the identity.
- **Ornament + primitives:** Antler beams as tapering `triad_blob` ribbons; tine TIPS
  capped with tiny `GOLD` `triad_circle` ferrules + an occasional `bead_arc` swag
  strung between two tines (trophy-string). Brow carries a dim cyan socket-glint.
  Full bone + gold. Mid tier; the gold tine-caps are a warm hue accent (never out-
  glowing cyan).

```
  \|/ \|/   <- branched tines reaching up
   \._./
   (o o)
    \_/
```

### 3 · `sabertooth-fanged-maw`  (WILD)
- **Thesis:** A predator reliquary defined by two long down-curving **sabre fangs** —
  the menace lives below the jawline, opposite to where every existing skull's interest
  sits (the dome).
- **Silhouette:** A **downward dagger / inverted-tongs** shape — compact cranium up top,
  then two long fang spikes plunging well below the jaw, wider apart at the root and
  hooking inward at the tips. Bottom-heavy, fang-forward — no existing skull has mass
  hanging below the jaw, so blackout is unique.
- **Construction/anatomy:** Mid cranium, **agape down-dropped jaw**, and the structural
  star: two oversized recurved canines extending ~1× cranium-height past the jaw. Upper
  tooth row reduced to a few small slits so the two sabres dominate.
- **Ornament + primitives:** Fangs as ink-keyed `triad_blob` tapers with a `BONE_SH`
  edge-sheen down the front; a `GOLD` band ferrule wrapping each fang root (mounted-
  trophy read); `cyan_gem(focal=False)` in ONE socket as the hot-ish predator eye.
  Full bone tier; the lit socket is the brightest of THIS skull but capped under focal.

```
   (o o)
   /vvv\    <- small upper teeth
   V   V    <- two long sabre fangs hanging below
```

### 4 · `third-socket-cyclops`  (WILD)
- **Thesis:** A monk-relic with a single great central socket — a one-eyed skull whose
  whole face geometry is reorganized around one vertical eye instead of a symmetric pair.
- **Silhouette:** A **tall narrowing teardrop / flame** — a high pointed-ish cranium
  tapering to a small chin, no temple-bulges (because there are no paired sockets pushing
  the cheeks wide). The only single-axis, vertically-symmetric-about-a-centerline skull;
  blackout is a clean teardrop, unlike every twin-socket dome.
- **Construction/anatomy:** Elongated cranium, **one large central almond socket** where
  the brow/nasal would meet, a small nasal slit below it, and a narrow chin with a tight
  tooth cluster. The face is built around the vertical midline, not the left-right pair.
- **Ornament + primitives:** The central socket holds a **`ring_eye`** (the concentric
  cyan-gold-cyan disc) as a contained third-eye — its own focal device, reused not
  reinvented; a `bead_arc` halo crowning the dome (a saint-relic ring); carved `GOLD_D`
  suture down the midline. Full bone + the ring_eye cyan; this is the most "lit" of the
  wild four but its cyan still caps a value step under the king's hero gem.

```
    /^\
   / O \   <- one big central ring-eye socket
   \ v /
    \_/
```

---

## CROWN-RELIC HALF (4) — restrained, cooler CROWN_BONE tier, geometry-only

These stay in the dim CROWN_BONE / CROWN_BONE_D / CROWN_SH palette, no cyan gems (at
most a single dim `CYAN_D` socket tint on none-to-one of them), no gold beadwork — they
earn distinctness purely from **cranial + mandible geometry**, each a different
blackout, and each different from the 6 existing crown skulls (which only varied dome
width/height/lean + suture). My four change the SKULL TOPOLOGY, not just its dome dial.

### 5 · `longjaw-relic`  (CROWN-RELIC)
- **Thesis:** An equine-style relic — a long projecting muzzle/mandible so the skull
  reads front-heavy and snouted, not round-faced.
- **Silhouette:** An **elongated keystone / boot** — modest cranium up top, then a
  long deep jaw projecting DOWN-and-slightly-forward, roughly 1.4× the cranium height.
  No existing crown skull has an elongated muzzle; blackout reads as a long-faced wedge.
- **Construction/anatomy:** Compact dome, sockets set HIGH and close, then a markedly
  **lengthened mandible block** with a long tooth row (8 fine slits) running its length.
  Identity is the vertical face elongation, not the dome.
- **Ornament + primitives:** Pure `triad_blob` in CROWN_BONE; `CROWN_BONE_D` median
  suture (line style) + a faint `CROWN_SH` muzzle-ridge sheen; INK sockets/teeth. No
  gems, no gold. Dimmest tier.

### 6 · `cracked-half-relic`  (CROWN-RELIC)
- **Thesis:** A battle-worn relic split by a vertical fracture — one half of the cranium
  sheared lower than the other, an asymmetric BROKEN skull.
- **Silhouette:** An **asymmetric stepped dome** — left half full-height, a jagged
  vertical crack line, right half sheared down ~25% with a chipped temple. The existing
  "lopsided" crowns only LEAN a whole intact dome; this one is genuinely BROKEN, with a
  notch removed from the silhouette edge. Blackout reads as a half-collapsed shape.
- **Construction/anatomy:** Two cranium halves at different heights joined by a ragged
  `BONE_DD` fracture seam; the sheared side loses its temple corner (a bite out of the
  outline) and its socket sits lower than the intact side. Jaw plain but tilted to match.
- **Ornament + primitives:** `triad_blob` halves; ragged crack drawn as a jagged
  `CROWN_BONE_D` polyline; one socket INK, one with a faint hairline `CROWN_SH` rim. No
  gold/cyan. Dimmest tier — the silhouette break is the whole story.

### 7 · `flat-brow-slab-relic`  (CROWN-RELIC)
- **Thesis:** A blunt, architectural relic — a low FLAT-TOPPED slab cranium with a heavy
  squared brow, reading like carved masonry rather than an organic dome.
- **Silhouette:** A **wide boxy plateau** — flat horizontal crown, near-vertical temple
  walls, a heavy straight brow-shelf, then a short jaw. The only non-domed, hard-edged
  rectangular skull in the whole set; blackout reads as a box, instantly separable from
  every rounded dome.
- **Construction/anatomy:** Trapezoidal/box cranium (flat top, slightly battered
  corners), a pronounced straight `CROWN_BONE_D` **brow shelf** casting a shade band
  over deep-set rectangular sockets, short squared jaw. Angular throughout.
- **Ornament + primitives:** `triad_blob` box with hard corners; brow shelf as a thick
  `CROWN_BONE_D` bar with a `CROWN_SH` top-lip sheen; rectangular INK sockets (not
  circles — reinforces the architectural read). No gems/gold. Dimmest tier.

### 8 · `conical-peak-relic`  (CROWN-RELIC)
- **Thesis:** An ascetic relic — a tall, narrow CONICAL cranium rising to a soft peak,
  elongated skyward like a deformed/bound skull, narrow at the temples.
- **Silhouette:** A **tall teardrop/spire** — narrow rounded peak at top widening only
  slightly to tight temples, then a small jaw. Distinct from the existing "tall-narrow"
  crown (which is still a normal egg-dome) because this one PEAKS to a near-point and the
  temples pinch IN; and distinct from #4 cyclops because it keeps the normal twin
  sockets. Blackout reads as a spire, not an egg.
- **Construction/anatomy:** Cranium height ~1.5× width, crown converging toward a single
  rounded apex, temples narrowed so the face is a tall slim oval; standard paired sockets
  kept small and high, tiny tucked jaw. Vertical, ascetic, pinched.
- **Ornament + primitives:** `triad_blob` spire with a long vertical `CROWN_BONE_D`
  median suture climbing to the apex; a `CROWN_SH` highlight ribbon down the lit (left)
  face to sell the curvature; small INK sockets. No gems/gold. Dimmest tier.

---

## Distinctness self-audit (the SET, before AD critique)

- **Blackout test:** ram-spirals (wide curls) · antler-rack (tall branched spikes) ·
  sabre-fangs (mass below jaw) · cyclops-teardrop (single-axis taper) · longjaw
  (elongated muzzle wedge) · cracked-half (stepped/notched dome) · flat-slab (box) ·
  conical-spire (pinched peak). Eight different black shapes — no two collapse together.
- **Construction test:** four break the base build with appendages or socket-count
  (horns / antlers / fangs / one-socket); four keep a single bony mass but each a
  different cranium-or-mandible topology (long muzzle / fracture / flat box / cone) —
  none is just the shipped dome with a new suture.
- **Shape-language test:** spiral-curl, branching-tine, recurved-dagger, vertical-flame
  (wild) vs elongated-wedge, broken-asymmetry, hard-rectangle, ascending-spire (relic).
- **Cover-the-label test:** each has a one-word read (horned / antlered / fanged /
  one-eyed / long-faced / broken / boxy / spired) that no sibling shares.
- **Mix:** 4 WILD use full bone + gold + a cyan focal device; 4 CROWN-RELIC stay in the
  cool dim CROWN_BONE tier, geometry-only — clearly the two requested flavors.

NEXT: hand this SET to art-director (brainstorm-critique) to cull/sharpen; then mature
each surviving direction in its own per-concept loop under
`docs/skull_king_stack/new8/<slug>/round_N.png`.
