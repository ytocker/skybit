# Stupika — round 1 critique (art-director)

VERDICT: ITERATE

A strong, characterful first pass. The base-tier face is genuinely scary-CUTE,
the mass sits at the base (NOT top-heavy — the re-spec landed), tiers are within
the 3–4 cap, and gilt/vermilion are correctly disciplined to cornice bands +
spire and a thin linear swag. The mirror is the cleanest in the brood as
promised. It does NOT yet clear the bar on the one thing the brief flags hardest:
the CREATURE-vs-masonry read at true 32px. The flagged merge is real and is the
top fix. One round should land it.

## Ranking of strengths / weaknesses

STRONGEST
1. Hero-scale charm + silhouette. The lowest-tier face — twin lamp-eyes, the
   little teeth band, the vermilion swag like a grin/brow — is exactly the
   "holy bone-skyscraper that grew a face on its ground floor" hook. Endearing,
   sacred, stompy. The stubby splayed feet sell "toddled off."
2. Mass distribution. Bottom-rooted, widening toward the base, spire light and
   thin. Not top-heavy. Re-spec satisfied.
3. Accent discipline. Gilt is strictly cornice bands + spire finial; vermilion
   is strictly a thin linear cord. Neither has grown into a second mass. This is
   the anti-source-gold/cinnabar pin, held.
4. Pillar mirror. Skull-tier modules tile cleanly; kapala-dome + spire cap each
   gap edge, on-axis, bottom-rooted. Cleanest mirror in the set — delivered.

WEAKEST
1. The 32px creature read (see fix #1) — at gameplay scale the face softens
   toward "ornamented tower," which is the one thing the brief says it must NOT do.
2. Two faces competing. There is a SECOND set of eyes on the tier ABOVE the live
   face (the round grey sockets + small swag). The brief says the ONE live face
   is the LOWEST tier. The upper sockets dilute "one face" and at 32px add noise
   right where we need a clean single read.

## Per-aspect KEEP / FIX

### 1. Readability & silhouette  — the gate, and where it falls short
KEEP: The overall stepped-cone silhouette is instantly a stupa/pagoda. Good.
FIX (HIGHEST PRIORITY): The GD's flag is confirmed at 32px. On both day and
night chips the two lamp-eyes and the vermilion swag crossing just above them
collapse into one horizontal gold-and-red band that reads as a decorated cornice
course, not a face. The eyes are too close to the swag line and there is no dark
socket gap isolating them. Prescribed fix:
   - Move the vermilion swag OFF the eye band entirely — drop it to the cornice
     seam BELOW the eyes (or raise it to the tier division above the eyes), so
     no red line crosses or kisses the eye row. The swag must read as masonry
     trim, the eyes as the creature; they cannot share a horizontal line.
   - Give each lamp-eye a clear DARK socket gap: a 1–2px ink ring / recessed
     dark surround so the warm lamp-core sits in a hole, not flush on the bone
     face. At 32px that dark gap is what flips "two gold dots on a band" into
     "two glowing eyes."
   - Widen the dark gap BETWEEN the two eyes a touch and keep the teeth band
     directly under them — eyes-over-teeth is the whole face read; protect it.

### 2. "One live face" — second-face conflict
FIX (HIGH): Kill or fully demote the upper-tier eye sockets. Right now the tier
above the live face has its own round eyes + mini-swag, so at a glance there are
TWO faces stacked. Make the upper tier unambiguously ARCHITECTURE: replace those
round sockets with blind niche-shapes / lattice / a different geometry that does
not read as eyes (no round + no warm core). Reserve roundness + lamp-glow for the
ONE base face. This also cleans the 32px read directly.

### 3. Color / value
KEEP: Triad (dark-core → flat-fill → top-left sheen) is reading; gilt is focal
against the chalk bone; night chip holds — gilt + lamp-core carry it on dark
blue. Good day AND night legibility on the body.
FIX (MED): Verify chalk-grey against the CROSS-SET PIN — it should be a hair
DARKER/warmer-neutral than Nagaraja's cool-pearl so gilt stays focal and the
brood separates by bone-cast. The current chalk looks correct-to-slightly-light;
confirm the pinned `(206,202,196)` / shade `(146,144,142)` and that it does not
drift toward Nagaraja's lighter cool-pearl. The lamp-eye core and the gilt are
close in hue — the dark socket gap (fix #1) also buys the value separation that
keeps them from blending into the gold cornices.

### 4. Identity & consistency
KEEP: Sits naturally beside source Citipati — same chibi + flat-triad + hard ink
keyline language, distinct KIND (stacked-tower vs Citipati's dancing skeleton).
No upright skull-man. On-brood.

### 5. Distinctiveness
KEEP: Unmistakable as the stacked-tower of the five. No conflict with the serpent
-coil / radial-fan / spread-wing / seated-throne siblings at silhouette level.

### 6. Feasibility
KEEP: Entirely procedural — stacked polygons, gradient bands, glow-cache lamp
cores, linear cord. No sprite-sheet thinking. Good.

### 7. Accessibility
FIX (MED): Right now the face read leans on the warm lamp-core hue + the red
swag. For colorblind safety the SHAPE must carry it: the dark socket rings +
eyes-over-teeth geometry (fixes #1, #2) give a hue-independent face read. After
those land, the creature reads even if you desaturate it. Confirm the vermilion
cord is not the ONLY thing distinguishing face-tier from the tiers above — let
the geometry do it.

### 8. Polish
KEEP: Edge quality and 1px outline are clean; glow is restrained.
FIX (LOW): The stubby feet read slightly as loose debris at 32px on the day chip
(faint detached flecks). Anchor them to the base block silhouette so they don't
shimmer as noise. Spire finial is good — keep it thin.

## Prioritized punch list (act in order)
1. Separate the vermilion swag from the eye band — move the cord to a cornice
   seam clear of the eyes; no red line crosses or touches the eye row.
2. Add a clear DARK ink socket gap around each lamp-eye so eyes sit in holes;
   widen the inter-eye dark gap. This is what makes the face survive at 32px.
3. Demote the upper-tier eyes to blind architecture (no round + no warm core) so
   there is exactly ONE live face — the lowest tier.
4. Confirm chalk-grey to the pinned `(206,202,196)` / `(146,144,142)` — a hair
   darker/warmer-neutral than Nagaraja cool-pearl; keep gilt focal.
5. Anchor the feet to the base silhouette so they don't read as detached flecks
   at 1×.
6. Re-render the 32px day + night chips and confirm: eyes-over-teeth reads as a
   FACE, not a cornice course, on the first glance.

## Reference
Casual-arcade "face on a building" reads (e.g. animated-tower/totem mobile
bosses) consistently isolate eyes in dark recesses and keep ornamental trim
OFF the eye line — the recess is doing the legibility work, not the color.
