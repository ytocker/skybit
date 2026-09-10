VERDICT: ITERATE

# Mariachi — round 2 critique (AD, final critique)

Big jump. The round-1 punch list landed almost entirely: the guitarron is now
off-axis and survives as a held-instrument bump, the kick leg splays into the
outline as a real zapateado diagonal, and the crown is flattened to a low peak
so the flat-disc read stays clearly Mariachi (not Catrina). This is genuinely
close to ship. It does NOT quite clear the bar at TRUE 32px for one reason —
the GD's own flag is correct — so this is a tight ITERATE into the final
round-3 pass, not a re-roll. The fixes below are surgical; the design is right.

## Strongest / weakest
- **Strongest:** the silhouette now reads "hatted musician kicking" in pure
  black — disc brim, the planted+splayed leg pair, and a clear round bump
  breaking the lower-right body edge. That is the brief's win condition for the
  outline, and it is met. Palette weighting and the turquoise rosette spark are
  still dead-on; warm-festive lane is unmistakable vs Catrina.
- **Weakest:** at TRUE 32px (the small sample, not the @4x blow-up) the
  guitarron body and the ribcage merge into one dark warm mass. The rosette
  turquoise pixel survives as a spark, but the disc EDGE between instrument and
  torso does not — so the "held round instrument" cue degrades toward a single
  rounded body blob. The @4x view reads great; the 1x does not yet. That gap is
  the whole remaining job.

## KEEP (do not touch)
- Off-axis guitarron tilt and the lower-right edge-break. The construction
  decision is right — only its 1x value separation needs work, not its position.
- The splayed kick leg + red boot toe as the lowest/outermost silhouette point.
  This is the accessibility shape-tell working exactly as briefed. Hold it.
- Flattened sombrero crown. The flat-disc read is now clean and stays apart from
  Catrina's couture brim and Jiangshi's mandarin hat. No plume crept in — good.
- Palette and rosette spark. Locked. Do not re-weight any hue.
- Pillar: cap is now ~shaft +35% and mirrors on-axis with the rosette as the gap
  focal. Resolved — leave it.

## FIX (prioritized — the round-3 brief)
1. **Separate the guitarron from the ribcage at TRUE 32px (only blocker).** At
   1x the instrument and torso are the same warm dark value and fuse. Force the
   disc edge to survive the alpha-outline: (a) drop a 1px INK gap between the
   guitarron rim and the jacket/ribcage where they overlap, and (b) push the
   guitarron body one value-step DARKER (deeper rust) than the warm-bone ribcage
   AND keep a 1px top-left sheen on the rim so the disc curve still catches light.
   The test is the small sample, not the @4x: at 32px I must see two distinct
   rounded masses — body + held disc — not one lump. This is the round-1 fix #1
   carried the last 20%.
2. **Lift the rosette focal contrast a touch.** The turquoise spark is the one
   thing telling "instrument, not shield" at 1x once the edge is fixed. Make it
   1px larger / one step brighter so it reads as a deliberate sound-hole point,
   not stray noise. It is your cheapest musician cue at scale — bank it.
3. **Verify the brim-underside shadow on a warm/ochre day sky.** Round-1 fix #5:
   confirm the thin ink band under the brim keeps the face disc-edge legible on
   desert/ochre biomes, not just the dark mat shown here. Render one frame on a
   light warm sky before locking.

That's it. Land fix #1 and this ships. If the next small-sample shows two clean
rounded masses + the turquoise spark, treat it as SHIP-READY without waiting on
another AD pass — this is my final critique and the design is otherwise locked.

## Sibling-drift check
- vs Catrina: resolved — flat crown + warm palette keep them apart.
- vs Tlaloc/Draugr round-mass: resolved by the off-axis tilt; once fix #1 lands
  the held instrument will never read as a body-centered shield/idol.
