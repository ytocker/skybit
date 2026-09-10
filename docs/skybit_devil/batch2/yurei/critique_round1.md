VERDICT: ITERATE

# Yurei — round 1 critique (AD)

A genuinely promising, atmospheric first pass. The blue-cyan hitodama lands,
the kimono/hair value structure is strong, and the pillar mirror is clean. But
the single thing that justifies this concept's existence over batch-1 Hollow —
a **visible mournful FACE** — does not survive to 32px, and that is the gate.
ITERATE, focused almost entirely on the face read.

## Verdict drivers (ranked)

1. **FACE fails the 32px brief-gate (most important).** The brief's whole
   distinction from Hollow is "a visible mournful FACE under hair, NOT a
   faceless hood." At 3x and especially at true 32px the face is a pale,
   near-featureless oval wedged between two black hair-curtains — the eyes are
   dim grey smudges that read as shadow, not features. At gameplay scale this
   is indistinguishable from a faceless pale void framed by black, i.e. it
   drifts straight toward Hollow. This must be fixed or the concept doesn't
   earn its slot.

2. **Hitodama color: PASS, but they out-shout the face.** The cyan reads
   correctly blue (verified distinct from Kitsune's teal-mint foxfire — good
   separation, no trade). However three loose teardrops float around her body
   like equal-weight confetti; at 32px the brightest cyan dot competes with /
   beats the face for the eye's first landing. The face must win the focal
   contest; the hitodama is the second read.

3. **Limp dangling hands vanish at 32px.** Present and nicely palms-down in the
   large render, but at small scale they melt into the kimono silhouette. The
   "wrist-limp dangling hands" are a named silhouette beat — they need to break
   the body outline as distinct dark notches.

4. **Wisp tail reads as torn cloth, not a fade.** The legless taper is jagged
   and hard-edged like a ragged hem rather than a ghost dissolving into
   nothing. It currently looks shredded, which leans grim/creepy over the
   brief's "wistful, scary-CUTE."

## KEEP (working — do not lose these)

- Blue-cyan hitodama hue `(120,206,232)` — correct, distinct from Kitsune. Lock it.
- Hair-curtain framing: strong dark verticals giving the pale face a clean
  value pop in the large render. The triad-lit black panels are good.
- Pillar/mirror: slim banded pole + framed-hitodama gap cap is clean,
  symmetric, on-axis, repeatable. No top-heavy risk. Ship-quality as-is.
- Overall cool day/night palette — pale-white + ink-black + cyan will sit
  cleanly against both biomes; no green/violet sibling collision.

## FIX — prioritized punch list for round 2

1. **Build a face that survives 32px.** Give the droop-eyes real positive
   shape: two larger, darker, downturned oval eyes with a 1px lighter sheen
   lower-lid so they read as EYES, not socket shadow, at 1x. Add the faintest
   suggestion of a small downturned mouth or under-shadow so the oval reads
   "sad face," not "blank disc." Pull the hair-curtains ~10-15% wider apart at
   the face so more pale face shows between them — right now the black almost
   pinches the face shut. Test: at true 32px a stranger should say "a sad
   ghost face," never "an empty hood."

2. **Demote the hitodama to second read.** Drop from three floating flames to
   ONE clear hitodama hovering at hand height (or shoulder), slightly smaller,
   so the cyan supports rather than competes. The face is the focal; the soul-
   flame is the accent + the obvious prop→pillar tie.

3. **Make the dangling hands break the silhouette.** Render the two limp
   palms-down hands as small dark notches that protrude past the kimono outline
   at the cuffs, so at 32px the silhouette reads arms-limp-dangling, not a
   smooth bell. This is a key separator from any hooded shape.

4. **Soften the wisp into a fade, not a shred.** Replace the jagged torn-hem
   bottom with 2-3 smooth tapering lobes losing opacity toward the tip (hard
   triad fills, stepped alpha — still procedural, no soft gradient needed), so
   it reads "drifting into nothing," wistful not gory.

5. **Optional cute-menace lift:** a tiny lavender rim `(184,182,212)` catch on
   the hair-curtain edge (top-left, per the triad) would lift her off a dark
   night sky and reinforce the spectral, gentle-eerie tone over grim.

## Sibling / drift check

- vs **Hollow** (batch 1, faceless hood): currently TOO CLOSE at 32px because
  the face doesn't read — fix #1 is the entire mitigation.
- vs **Necrarch** robe-wisp: clear separation — Necrarch is tall/narrow,
  bronze-crowned, violet-orb-cradling; Yurei is hair-curtained and faceful.
  No drift concern once the face lands.
- vs **Kitsune** cool glow: PASS — blue-cyan vs teal-mint hold apart.

Re-render round 2 with the face fix as the headline; everything else is minor.
