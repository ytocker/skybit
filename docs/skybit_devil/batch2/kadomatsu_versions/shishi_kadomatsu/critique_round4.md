# Shishi-Kadomatsu — AD critique round 4

VERDICT: ITERATE (scoped pass held everything but missed its one gate — notches hit the wrong edge)

Everything from r3 held, no regressions: FOUR evenly-spaced black leg-posts (3 clean sky-slots split the
skirt), no bright center face-window, ship-quality 32px day+night creature read (bound-culm quadruped +
cream cut-disc crown as brightest cluster). But the ONE scoped gate — scalloped/toothed crown TOP contour
in pure black — did NOT land: the `crown_notch()` slots were driven through the crown's LIP/underside
(rows 45-53, the already-toothed area) instead of the TOP arc (rows 28-37), which is still a smooth
gap-free dome cap. Carving the underside is invisible because the dome sits above it.

## Round-5 (final, last attempt) — single isolated fix
- **Re-target `crown_notch()` to pierce the TOPMOST contour rows of the crown** (~rows 28-37): cut 2-3px
  SKY notches DOWN into the top arc between the upper outer cut-discs so the BLACK silhouette's top edge
  itself goes bumpy — a visible ring of cut-tips against sky (the same negative-space trick that won the
  legs). At least 3 notches breaking the top arc; they must pierce the actual top contour, not interior fill.
- Watch: don't shave the leftmost/rightmost cut-tips so thin the crown loses its wider-than-tall komainu read.

NOTE: in-game the boss renders in COLOR, where day+night reads are already ship-quality; this gate is the
pure-black silhouette QA proof only. If r5 still domes, SHIP AS-IS and flag this nuance to the user.
