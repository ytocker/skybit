# Tatsu-no-Takemura — AD critique round 2

VERDICT: ITERATE (final GD round 3 — tight punch list, the coil is good enough that a corrected head +
coarser collars ships)

Real structural progress on the body, but both hard gates are still open and the head regressed.

- **GATE 1 (bamboo-as-scales): PARTIAL — pass at hero, FAIL at 32px.** Collar rings now tile the whole
  spine incl. bends at hero (good), but at 32px they dissolve into a smooth tube → reads as a green
  caterpillar/inchworm. Pitched too fine + too low-contrast to survive downscale.
- **GATE 2 (head-maw wins at 32px): FAIL (regressed).** The reared head is now a concentric oval-on-oval
  cream DISC → reads as a closed eye / fried-egg / Kappa saucer (the round-1 failure mode minus the
  pupil), not an open diagonal cut. At 32px it's a round pale BALL ("head with a face"), not a sliced
  culm. Credit: the foot no longer out-brights the head. But the pillar gap-cap abandons the maw and uses
  the plum cluster — the signature cut is absent where the brief names it.

KEEP: the 2.5-loop vertical S coil + framing (blackout reads clean); foot value brought down; collars
tiling the bends at hero; overlap cut-nubs; thread-thin teal dorsal + whiskers; base-weighted foot.

## Round-3 punch list (final — land 1+2+3 to clear both gates)
1. **Rebuild the head as an unmistakable OPEN SOGI-CUT, not a disc (GATE):** kill the concentric
   oval-on-oval; cut the culm-end on a STEEP diagonal so the silhouette is an ELLIPSE-ON-A-SLANT (not a
   frontal ball). Inside: a wide `CUT_HI` sheen ring-wall around a clearly lightened open `CAVITY` slot
   (a parted gullet), warm lip on the near edge only. The slant asymmetry = "sliced open" not "a face."
   Clone the parent `diagonal_cut()` slant + value spread.
2. **Make the maw survive 32px as the single brightest CUT, not a ball (GATE):** push cavity→sheen
   contrast so it collapses to a bright cream wedge/chevron, never a uniform pale circle. Slightly narrow
   the head caliber so it doesn't bobble-head the neck.
3. **Coarsen the belly-collar rhythm (GATE):** fewer, FATTER segments — pitch collars ~one-diameter
   spacing (not half), widen + raise the dark-groove contrast so each ring reads as a distinct belly-band
   at 32px (~6-8 clearly stepped segments per visible coil run).
4. **Put the maw on the gap-cap:** cap the pillar with the bright cut-maw disc (plum/straw → lower mirror
   only) so the cut-mouth signature is present at gameplay scale.
5. Tidy the upper-bend teal tangle where the dorsal filament meets the whiskers (keep filament-only).
