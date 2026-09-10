VERDICT: SHIP-READY

# Jiangshi — Round 3 critique (Art Director, confirming pass)

Round 3 lands the gate. The two prior rounds both failed the ONE read this
concept owns — R1 had a single arm, R2 had frontal foreshortened tubes with no
horizontal extent. R3 delivers the canonical jiangshi: both rust-plum sleeves
thrust straight OUT to a true wide horizontal span, each reaching clearly past
its torso edge, both at the same shoulder height, capped with a jade hand-block.
The arm-to-arm span is now the widest horizontal in the silhouette — wider than
the hat wings — exactly as the R2 brief demanded. This is ship-ready.

## Strongest / weakest

- **Strongest:** the arms-out T silhouette, finally landed. It survives the
  whole scale ladder: at 48px it's crisp, at 32px (gameplay) the T is the first
  thing the eye reads, and critically at the 24px gate the horizontal arms still
  dominate the torso block — the smoothscale no longer eats them. The jade
  hand-blocks at each tip give the span a hard terminus so it doesn't taper into
  ambiguity. This is now the most unmistakable silhouette in the skeleton
  section.
- **Weakest:** nothing that blocks ship. The only thing I'd even note is that
  the queue braid is now almost fully hidden behind the torso at 24px — but the
  brief always made the arms the tell, not the queue, so this is correct
  triage, not a fault. Leave it.

## KEEP (do not touch on integration)

- **Arm staging.** True horizontal T, equal shoulder height, jade hand-blocks,
  span wider than the hat wings. This is the locked read — preserve the span
  ratio exactly when porting to code; do not let the procedural pose narrow it.
- **Arm/torso separation.** The sleeve-shade `(96,40,56)` + 1px ink gap at each
  shoulder breaks the arms off the body block cleanly — the arms read as two
  distinct masses at 32px, not one merged rust-plum slab. This was FIX #2 and
  it's resolved.
- **Single horizontal sash band** replacing the crossed-X. The eye now reads
  ARMS-OUT first, rank-badge second — the competing diagonal is gone. FIX #3
  resolved.
- **Jade-corpse skin** `(120,158,118)` — locked since R1. Stays clearly lighter,
  yellower, lower-chroma than Cernun's pine `(54,92,68)`; no green-band
  collision. Confirmed across both day and night chips.
- **Pillar:** talisman-scroll shaft + red lantern gap-cap — clean symmetric
  on-axis mirror, repeatable banding rhythm, no top-heavy risk. Unchanged and
  correct.
- **Face + hat:** red eyes, brow talisman (cream + cinnabar strokes), stitched
  mouth, winged mandarin hat kept secondary/taller-vertical to the arms.
  Scary-cute, on-brief.
- **Night read:** rust-plum robe sits mid-value but the gold hem/trim + cinnabar
  badge stay lifted, keeping the warm focal anchored on dark-blue night. Holds.

## Distinctness — confirmed clean

- **No green-band conflict.** Jade-corpse vs Cernun pine vs Tlaloc grey-jade vs
  Kappa yellow-green — four distinct value/chroma/hue lanes, and Jiangshi also
  sits on a separate (skeleton) body type. Safe.
- **No sibling drift.** Rust-plum + cinnabar warm family is unique in the
  skeleton section (Catrina cool ash/teal, Mariachi warm bone/ochre, Necrarch
  violet, Draugr ice). Its own lane.
- The T-of-arms — the sole distinctness lever this concept owns — is now
  delivered. Concept ships.

## Integration note

When this moves from the candidate render into procedural code, the one risk is
the pose drifting: a parametric arm that rotates or foreshortens will quietly
reintroduce the R2 failure. Pin the arm span as a flat horizontal projection
(no depth foreshortening) and assert the arm-to-arm width stays wider than the
hat-wing width at the 24px draw. That single invariant protects the read.
