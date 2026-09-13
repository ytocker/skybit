# Art-Director critique — Hyeoljang (tongue-out warrior guardian post) — ROUND 1

VERDICT: ITERATE

Strong, genuinely funny-fierce first pull. The hero reads as a memorable EPIC
character at a glance, the comedy-IS-the-menace thesis lands, and at 32px the
tongue + goggle-eyes carry exactly as the GD predicted. Two fixes stand between
this and ship; one of them is the paua ruling the brief asked me to make.

## Ranking of aspects (strongest → weakest)
1. **Tongue + goggle-eye lower-face read (STRONGEST).** The big floppy pink
   tongue is the dominant lower-face mass and the warm focal gag; crossed
   goggle-eyes + bulb-nose + top-knot give a big-and-few read that survives 32px
   day AND night. This is the soul of the piece — keep it untouched.
2. **House-style fidelity.** Chibi, scary-CUTE, flat triad, hard ink keyline +
   1px outline, ruddy red-totara body — all present and elevated, not grim.
3. **Color / value.** Warm red-totara is correctly the warmest, most saturated
   wood of the brood; tongue-pink focal sits cleanly on it; warm-cream eye glow
   is the single warm focal. Holds day and night.
4. **Pillar mirror.** Clean, bottom-rooted, on-axis; cap is a smaller mirrored
   tongue-out face. Reads as the shaft body, no top-heavy risk.
5. **Distinctness vs source + roster.** Clearly its own creature vs the slate
   Jangseung source and the rest of the brood.
6. **Paua eye-ring tell (WEAKEST — the ruling).** See FIX 1.

## RULING on the paua eye-ring (the question put to me)
**The teal rim needs a touch more contrast/thickness — but NOT a recolor of the
spec.** At true 32px (verified on both day and night chips) the teal rim is
effectively gone: the eye reads as cream-glow eyeball inside a bright cream
goggle ring, and the violet inner is correctly sub-pixel-invisible. The brief
deliberately specced paua as the SMALLEST accent and said tongue+goggle-eyes
carry the read — and they DO. So the character does not fail without it.

BUT the cross-set pin requires paua to survive as the *tell* that separates
Hyeoljang from the brood's other two teals (Haedung jade scale-band, Muljang
prow-foam band). Right now there is no teal visible at 32px at all — the tell is
absent, not merely small. That's a pin failure, not a legibility failure.

Resolution: the paua does NOT need to grow into a glow or a mass (anti-Yurei /
anti-Kitsune holds). It needs to stop fighting the cream goggle ring next to it.
The reason it dies is a VALUE collision: a thin mid-value teal is sandwiched
between bright cream goggle binding and the dark ink keyline, so at 32px it gets
averaged into the cream. The fix is contrast + placement, not thickness alone:

- Make the paua rim 1px thicker on the OUTER edge of the eye only (the side
  facing the cheek, away from the cream goggle band), so it sits against the
  ruddy wood — wood-vs-teal is a real value/hue jump that survives downscale,
  whereas teal-vs-cream does not.
- Push the rim teal a hair DEEPER and cooler (toward `(48,132,134)`) so it reads
  as the deepest, coolest, SMALLEST of the three brood teals — exactly the
  cross-set role. Keep the hard flat paint edge; no glow.
- Keep the violet inner as a sub-pixel sliver. Correct as-is.

This keeps paua the smallest accent of the set while making the tell actually
present at gameplay scale.

## Iteration directives (prioritized)
1. **Rescue the paua tell at 32px (pin).** Thicken the teal rim 1px on the
   outer/cheek-facing edge only so it borders wood not cream; deepen to
   ~`(48,132,134)`. Hard flat edge, no glow, no growth into a mass. Re-render
   the 32px day+night chips and confirm a teal pixel survives on both.
2. **Crossed goggle-eyes are reading parallel, not crossed.** At hero scale the
   pupils sit near-centered; the "crossed" warrior gag — the funniest-fierce
   beat — is underselling. Pull both warm eyeballs/pupils inward toward the
   nose-bridge so they visibly cross. This is free comedy and strengthens the
   whole thesis; do it before any polish pass.
3. **Top-knot is reading slightly soft/ambiguous at 32px.** It's there but the
   pink binding-wrap blurs into the wood crown. Give the knot one hard ink
   keyline notch where it meets the head so the silhouette tells "top-knot" and
   not "lump" at thumbnail.
4. **Tooth row is fine at hero scale but turns to a grey smear at 32px.** Drop
   to 3–4 bigger tooth-bone blocks with a clear gap between each so the grimace
   stays a grimace, not a noise band, when small.
5. **Spiral grooves — confirm SPARSE.** The cheek/body grooves read sparse and
   correct at hero scale; just verify they don't tile into busy repetition down
   the shaft on the pillar mirror. Keep ~1 groove per face/band, no more.

## Notes that are already RIGHT — do not touch
- Tongue mass, shape, and pink focal value.
- Bottom-rooted on-axis mirror and the smaller lit cap-face.
- Red-totara warmth vs the rest of the brood.
- Violet inner staying sub-pixel (anti-Necrarch) — correct.
