# CLASSIC-8 skull-king reference set — brainstorm (round 1, BRAINSTORM MODE)

The previous `new8` batch (horned-ram, antler-stag, sabertooth-maw, cyclops-brow,
longjaw-relic, cracked-half, flat-slab, keyhole-relic) was rejected as **"too
futuristic / exotic"** — horns, antlers, sabre fangs, a single cyclops eye,
broken/architectural crania, plus cyan gems and gold beadwork. This batch pulls
the OPPOSITE way: eight takes on the **timeless, universal "simple skull"** —
rounded vault, two big round/oval sockets, a triangular nose hole, a plain tooth
row. No fantasy, no sci-fi, no jewels, no beads.

---

## Research note — "what makes a shape read instantly as a CLASSIC skull"

**From real anatomy** (the landmarks that, in their normal proportions, the eye
locks onto as "skull"):

- **The vertical stack.** Front-on, a skull is an ovoid read top-to-bottom as
  four bands: **cranial vault (frontal bone)** at top → **orbits (eye sockets)**
  at the middle → **nasal aperture** just below and between them → **maxilla +
  mandible (tooth row + jaw)** at the bottom. That stack, in that order, IS the
  skull. Get the stack right and almost any cranium outline still reads as skull.
- **Proportion that reads as "human, classic":** the **vault is the biggest
  mass** — roughly the top ~⅔ of the height is brain-case, the face is the
  bottom ~⅓. Casual/cartoon skulls exaggerate this (big round dome, small low
  face) because the oversized cranium is the most "skull" signal.
- **Orbits** are large, rounded, and sit wide — set noticeably **below the
  vault's midline**, leaving a tall smooth **forehead** above them. Too-high or
  too-small sockets stop reading as a skull. The **glabella** (smooth pad between
  the brows) and a soft **browridge** sit just above them.
- **Nasal aperture** is the **inverted heart / spade / triangle** hole, narrow
  at top (between the orbits) flaring down — the single most "skull-not-anything-
  else" feature after the sockets.
- **Zygomatic arches (cheekbones)** flare out at orbit-level then the face
  **tapers inward** toward the chin — that hourglass cheek-to-jaw taper is what
  separates a skull from a plain circle.
- **Tooth row** is a gentle arch of small even blocks across the maxilla; the
  **mandible** hangs below as a U with a squared or rounded **chin**.

**From flat-icon / emoji / casual-game skulls** (how that anatomy is SIMPLIFIED
into a few bold shapes that survive a 24px chip):

- **Cranium = one circle/oval.** Jaw = one boxy shape under it. That's the whole
  silhouette. Everything else is a hole punched into it.
- **Sockets = two big dark ovals**, oversized and friendly; the bigger and
  rounder, the more "cute skull / icon," the smaller and squarer, the more
  "real bone."
- **Nose = one small inverted heart / upside-down triangle** (a spade) — almost
  never realistically rendered, just a dark notch.
- **Teeth = a row of short vertical slits** in a pale bar, or a few "fence-post"
  blocks. Number and evenness set the mood (even = clean, gapped = old/grin).
- **Depth = a couple of grey shapes**: a top-left sheen on the dome, dark cores
  in the sockets. That's exactly our BONE-tier triad. Nothing more is needed.

**The lesson for this set:** keep all 8 inside that stack and those few bold
shapes. Make them DISTINCT by changing the **proportions of the masses**
(vault height vs. width, face length, jaw mass, cheek flare) and the **condition
of the bone** (child / aged / gaunt / robust / jawless) — never by adding an
accessory or a single weird feature. If a shape needs a label to read as a
skull, it has failed the brief.

---

## House grammar baked into every direction (hard constraints)

- Procedural pygame only; final module exposes `draw(surf, cx, cy, r, s, lit=False)`,
  `import render_switchbig as sk`, supersample → `sk.grow_outline`, `s = r/12`
  line-weight, must survive a ~24px chip with the `_panel()` harness from
  `new8/horned-ram/render_horned_ram.py`.
- **Plain BONE tier ONLY:** `sk.triad_blob` flat fill + INK keyline + a single
  top-left `BONE_SH` sheen wedge on the dome; sockets/nose are `INK` / `BONE_DD`
  dark holes with a `triad_circle`-style dark core. Teeth = INK slits in a pale
  `BONE`/`BONE_SH` bar. **NO cyan gems, NO gold beads, NO sutures-as-jewelry.**
- `lit` is a **no-op or at most a faint BONE_SH socket-rim glow** — never a color
  accent.
- Every cranium is an **ink-keyed polygon** (like horned-ram's `dome` loop), so
  the distinct proportions live in the SILHOUETTE, not only in interior lines —
  this is what carries the blackout test.

---

## The 8 directions

Each is a different **idea of what the skull IS** — built bottom-up from its own
mass proportions, not one base re-dressed. The axis each one owns is named.

### 1. `round-cap` — the plain icon skull (the platonic default)
**Thesis:** the skull everyone draws first — a near-perfect round dome, two big
friendly round sockets, an inverted-heart nose, a clean even tooth row. The
neutral anchor the other seven deviate from.
**Construction:** cranium = a wide circle (cw≈ch≈1.0) sitting on a short boxy
upper-face; **no separate hanging jaw** — teeth bite straight off the lower edge
(calvaria-feel but full-faced). Sockets are the LARGEST and ROUNDEST of the set
(`r*0.34`), set wide and a touch low. Nose = symmetric inverted heart. Teeth =
6 even slits in a gently arched bar. Tall smooth forehead, single soft sheen
wedge top-left. Shape language: **all circles** — maximum friendliness, the
flat-icon read. Owns the axis: *broad round low-brow, the baseline.*

### 2. `egg-dome` — the tall domed cranium
**Thesis:** a skull that is markedly TALLER than wide — a high egg/lightbulb
vault rising well above the sockets, giving a long noble forehead. Same parts as
#1 but the vault proportion is inverted (ch≈1.25, cw≈0.88).
**Construction:** cranium = a vertical ovoid, narrowest across the temples,
crown lifted high. Sockets pushed LOW on the long face to leave that tall brow.
Face below is narrow; jaw is a small tucked U. Sheen wedge runs the full height
of the tall dome. Shape language: **vertical egg** — elegant, slightly solemn.
Owns the axis: *tall domed cranium (vs. #1's round, #3's broad-low).*

### 3. `broad-zygo` — the wide-cheeked robust skull
**Thesis:** a low, WIDE skull whose identity is big flaring cheekbones — the
zygomatic arches bulge out hard at socket level, then the face sweeps in to the
jaw, a strong hourglass. Reads "broad heavy-boned man."
**Construction:** cranium = low and wide (cw≈1.18, ch≈0.9); the **outline kinks
OUT at the cheek corners** (two bumped vertices beside the sockets) before
tapering to a square jaw. Sockets mid-size, set under a flat low brow. The
silhouette's defining trait is the cheek flare — visible in blackout. Shape
language: **hexagonal/diamond face** from the cheek kinks. Owns the axis:
*full broad zygomatic flare (vs. #6's sunken hollow cheeks).*

### 4. `square-jaw` — the heavy full mandible
**Thesis:** the only skull with a big, separately-hanging SQUARE lower jaw — a
broad blocky mandible with a flat wide chin slung under the cranium, a clear
gap-shadow above it. The "full-jaw, strong-chinned" skull.
**Construction:** standard round-ish vault, but below the maxilla a **distinct
mandible polygon** drops as a wide squared U (almost as wide as the cranium) with
a flat chin. A thin INK shadow band separates upper teeth from the lower jaw so
the mandible reads as its own bone. Lower teeth hinted on the mandible's top
edge. Shape language: **circle-over-box**, jaw-forward. Owns the axis:
*heavy square full mandible (vs. #2 / #7's narrow tucked jaw, vs. #5 jawless).*

### 5. `calvaria` — the jawless cranium (skull-and-crossbones)
**Thesis:** the flag/poison skull: **cranium + upper teeth only, NO lower jaw.**
The bottom of the face ends in a clean arc of upper teeth — the instantly-
recognizable "skull-and-crossbones" truncation.
**Construction:** a strong round-to-slightly-egg vault; the face stops at the
maxilla, finishing in a shallow rounded **upper dental arch** (a half-ring of
6–7 teeth) with nothing hanging below — open background where a jaw would be.
Sockets large and dark, nose a bold inverted triangle. The MISSING jaw is the
whole identity and is obvious in blackout (the silhouette is a rounded blob that
just stops). Shape language: **dome capped by a tooth-arch, flat bottom.** Owns
the axis: *jawless calvaria (vs. every full-face sibling).*

### 6. `gaunt-hollow` — the sunken gaunt skull
**Thesis:** a long, lean, weathered skull with HOLLOW temples and sunken cheeks —
the face pinches inward between the cheekbone and the jaw, deep shadow pockets,
a tired aged read. The "memento-mori, starved" skull.
**Construction:** narrowish tall-ish vault; the face outline **dents INWARD**
below the cheekbones (concave temple hollows on each side) instead of flaring.
Larger BONE_DD shade pockets in the temple/cheek hollows (drawn as dark polygon
patches, NOT jewels). Sockets set deep with a heavier dark core; nose a longer
narrow slot. Thin narrow jaw. Shape language: **pinched-waist face, concave
sides.** Owns the axis: *sunken gaunt hollow (the negative of #3's flare).*

### 7. `child-skull` — the infant/juvenile proportions
**Thesis:** the unmistakable child skull: a HUGE round bulging cranium (big
forehead, big braincase) over a TINY low face — sockets sit very low, face is
small and short, jaw delicate. Cute and a little eerie from proportion alone.
**Construction:** cranium = oversized near-circle bulging at the forehead
(cw≈1.1, ch≈1.05) taking the top ~70% of the height; face crammed into a small
low zone — sockets large-but-low, a small nose, a short tooth row of tiny even
teeth, a tiny soft-cornered jaw. The drama is purely the **vault-to-face ratio.**
Shape language: **giant balloon dome, mini face.** Owns the axis:
*juvenile big-cranium-small-face proportion (vs. the adult balance of #1).*

### 8. `gap-grin` — the aged gap-tooth skull
**Thesis:** an OLD skull defined by its mouth: a wide weathered tooth row with
several teeth MISSING — irregular gaps in the grin, a couple of longer
surviving teeth — plus a generally worn, slightly asymmetric face. The
"grinning old memento-mori" read.
**Construction:** a normal broad adult vault (close to #1 so the contrast is the
mouth, not the dome), but the tooth row is the focal: a wide bar with **uneven
gaps** (2–3 slits dropped, the survivors varying in length), faintly receding
into a darker gum-line band. Slight asymmetry in the jaw and a hair-thin worn
crack hint on the temple (a single shade line, NOT a broken-off chunk — we
deliberately avoid `cracked-half`'s architectural break). Shape language:
**round skull, ragged grin.** Owns the axis: *gap-tooth aged grin (vs. #1's
clean even set).*

---

## Distinctness self-audit (the four tests, applied to the SET)

**Blackout test** (silhouette alone, label hidden):
- `round-cap` = round blob, flat-ish bottom · `egg-dome` = tall vertical egg ·
  `broad-zygo` = wide hexagon with cheek bumps · `square-jaw` = circle with a
  big box hanging under it · `calvaria` = rounded blob that stops at a tooth-arch
  (no jaw) · `gaunt-hollow` = pinched-waist concave-sided face · `child-skull` =
  giant dome + tiny face nub · `gap-grin` = round blob like #1 but its outline
  is the only twin of #1.
  → 7 of 8 silhouettes are mutually unmistakable. **One flagged overlap:**
  `round-cap` vs. `gap-grin` share the round outline. Mitigation: gap-grin's
  identity is an INTERIOR feature (the ragged mouth), so it fails pure blackout
  against #1 — I'll push its jaw a touch more asymmetric/receding so the
  silhouette diverges, OR accept that its distinctness is "condition" (aged
  grin) which is a legitimate archetypal axis the brief explicitly lists. Worth
  the art-director's call on whether to keep both or swap #8 for another
  silhouette-distinct idea.

**Swap test** (could two be the same base re-dressed?): No accessories exist to
swap — every difference is mass proportion or bone condition. `square-jaw` ↔
`calvaria` are opposite jaw decisions (max jaw vs. no jaw); `broad-zygo` ↔
`gaunt-hollow` are opposite cheek decisions (flare vs. sink); `egg-dome` ↔
`child-skull` differ in WHERE the big vault sits relative to the face. No pair is
a re-dress. Pass.

**Cover-the-label test:** each one-sentence thesis names a different *kind* of
skull (default / tall / wide-cheeked / strong-jawed / jawless / gaunt / child /
aged-gap), not a different decoration. Pass.

**One-sentence test:** every direction is describable as "the [proportion/
condition] skull" without referencing another. Pass — with the noted caveat that
`gap-grin` leans on condition rather than silhouette.

**Net:** strong, mutually-distinct set spread across the brief's archetypal axes
(round vs. tall vault; broad vs. gaunt cheeks; full vs. square vs. jawless jaw;
child vs. adult vs. aged). The single soft spot is the `round-cap`/`gap-grin`
silhouette twinning — surfaced for the director to either accept (condition axis)
or have me re-roll #8 into a more silhouette-divergent idea (e.g. a
**`bullet-narrow`** tall-narrow gracile cranium, or a **`flat-brow-robust`**
heavy archaic browridge skull) before the per-concept loops begin.
