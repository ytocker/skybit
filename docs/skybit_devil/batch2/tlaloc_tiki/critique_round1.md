VERDICT: ITERATE

# Tlaloc-Tiki — round 1 critique (per-concept, AD)

Strong construction and a genuinely charming chibi idol. The silhouette tell,
seam grammar, and mirror are basically there. But the round FAILS its single
CRITICAL pin: the coral mouth is NOT the brightest focal — the gold goggle
eye-rings are. Until that focal hierarchy flips, this melts toward "gold-eyed
green thing" and loses the one cue the brief built the concept around. Iterate.

## Strongest / weakest

- Strongest: the goggle eye-ring + carved-seam silhouette tell is unmistakable
  at 32px and survives to 28px — accessibility shape read is locked. The stepped
  totem mirror is clean, symmetric, and repeatable; the stone base color is
  correctly pushed grey/neutral.
- Weakest: focal hierarchy is inverted. The two huge concentric GOLD rings are
  the brightest, highest-contrast, highest-area warm masses on the head — the eye
  lands on them first and the coral mouth reads second. That is the exact opposite
  of the brief's hero-color pin, and it's the thing that will make Tlaloc read
  generically against Cernun/Kappa rather than as "the coral-mouthed idol."

## Measured (sampled from the committed PNG)

- Stone body (92,124,121) — relative luminance ~0.18, sat ~0.26. GOOD: near-neutral
  grey slate-jade, on-pin, correctly desaturated and recessive. No green-band drift.
- Coral mouth (219,86,71) — luminance ~0.22, sat ~0.67. On-hue, but only ~0.04
  brighter than the stone body.
- Gold goggle-ring (221,181,77) — luminance ~0.49, sat ~0.65. More than 2x the
  coral's luminance. Two of these, large-area, framing the face = the de facto
  focal. This is the fail.
- Turquoise inlay is present but reading as scattered teal flecks (117,205,192)
  inside the rings — it competes with, rather than supports, the eye read.

So: stone passes, hue of coral passes, but VALUE hierarchy fails. Coral must
out-pop gold, not sit below it.

## KEEP

- Grey-neutral stone base and the deep slate-jade shade — do not touch the body hue;
  it is exactly the "neutral backdrop" the green-band separation needs.
- Goggle eye-ring + downturned-fang mouth silhouette; the carved-seam triad grooves;
  the stepped-pyramid body and stubby blocky limbs. Scary-cute menace is landing.
- The totem pillar: stacked mini-mask bands as repeatable shaft + feathered-serpent
  finial cap. Symmetric, on-axis, no top-heavy risk. Ship-quality mirror.

## FIX (prioritized punch list for round 2)

1. FLIP THE FOCAL — highest priority. The coral mouth must be the brightest,
   warmest, eye-first mass; the gold rings must drop below it. Concretely:
   a) Brighten/enlarge the coral: raise the mouth's top-left sheen and push the fill
      to the pinned (224,90,74) with a hotter coral rim-light so its peak luminance
      clears the gold ring's (~0.49). Give it more area — widen the mouth and/or
      fatten the two curled fangs so the warm mass is the largest non-stone shape on
      the face. b) DEMOTE the gold: drop the goggle-ring gold to a darker,
      lower-luminance bronze-gold (target luminance ~0.32–0.36, well under the
      mouth) OR thin the rings so they read as a keyline ACCENT, not a filled disc.
      Right now they are filled coins; make them rings.
2. Stop the turquoise from fighting the eyes. The turquoise inlay should be a small
   support accent (brow/cheek inlay or a thin ring-inner), not bright flecks inside
   the pupils. Pull turquoise out of the eye interior so the eye reads as ring + dark
   pupil, and the mouth wins the warm-focal contest uncontested.
3. Pupil contrast. Give each eye a clean dark (22,32,30) pupil with a single tiny
   sheen dot — currently the eye centers are muddy (gold/teal mix) and lose the crisp
   "goggle" read at 28px. A dark pupil also visually lowers the gold's pull.
4. Coral mouth at 32px. In the 32px inset the mouth is a small dark-red smear while
   the gold eyes dominate. After fix 1, re-render the inset and confirm the eye
   genuinely lands on the mouth FIRST at 32px and 28px — that is the pass test.
5. Minor — fang clarity. The two curling serpent-tusks are reading as small white
   teeth rather than the signature out-curled Tlaloc fangs. Push them outboard and
   give them the curl so the "rain-fang" identity reads in silhouette.
6. Minor — gold belt. The horizontal gold belt-band on the body is a third gold mass
   competing for warm attention. After demoting the ring gold, keep the belt
   subordinate (thin, lower-lum) so the only bright-warm focal is the mouth.

## Cross-check (siblings / batch-1 drift)

- Green-band: stone is correctly the neutral/grey lane vs Cernun's pine and Kappa's
  yellow-green — no conflict there. The risk is NOT the green; it is that the
  gold-eye dominance erases the coral cue that is supposed to be Tlaloc's separator.
  Fix the focal and the band separation is fully satisfied.
- Gold collisions: big bright-gold discs also edge toward Pazul/Kappa/Mariachi
  gold-accent territory. Demoting the rings to bronze keeps Tlaloc's warm signature
  uniquely CORAL, as pinned.
- House style (chibi, flat fills, ink keyline, triad lighting, alpha-grown outline)
  is on-grammar and consistent with batch-1.

## Pass test for round 2

At 32px, squint: the first thing you see must be the CORAL MOUTH, then the goggle
RINGS as shape, then the grey body. If gold still wins, iterate again.
