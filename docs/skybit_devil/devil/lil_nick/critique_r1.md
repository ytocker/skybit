# LIL NICK (take B1) — round 1 critique

VERDICT: ITERATE

A strong, confident first round. The figure reads unmistakably as THE storybook
red devil at showcase scale, the firewall is honored (zero skull, short upturned
horns, not a ram pair), and it owns the pure-cherry-red lane cleanly. The prop
-> pillar mirror is the real success here. But three things keep it off
ship-ready: the horns lean too far OUTWARD (reading bull/longhorn, not the
short upturned candle-flame the spec calls for), the face loses its key beats at
1x, and the showcase pose has a stiff/over-reachy right arm. All fixable; no
re-roll.

---

## Strongest / weakest

- **Strongest:** the PROP -> PILLAR. The banded wrought-iron haft + gold ferrule
  rhythm + 3-short-tine cap is genuinely tileable, the top/bottom mirror reads as
  one clean post biting the gap, and the banding survives the 82px native
  downscale in cell (b) instead of washing to a grey bar. This is the hardest
  part of the brief and it is basically there. Iron + 3-short-tine is also
  clearly material-distinct from the A3 bone / B8 fire / B6 neon forks.
- **Weakest:** the HORNS. At every scale they sweep outward and slightly back into
  a wide V that reads as bull/longhorn or ram-adjacent — the exact silhouette the
  guardrail exists to avoid. They are the figure's top-of-silhouette signature and
  right now they fight the "short UPTURNED candle-flame" thesis.

---

## Per-aspect KEEP / FIX

### 1. House-style fidelity — PASS
- KEEP: FLAT fills + hard ink keyline + dark-core/fill/top-left-sheen triad are
  all honored; no gradient/soft/bevel drift. The alpha-mask outline pops the
  silhouette correctly on both skies.
- KEEP: the spade tail's S-flick and the ace-of-spades tip are excellent — bold,
  iconic, and the SPADE_HI facet keeps the near-black from going dead.
- FIX (minor): the belly has THREE concentric value rings (RED triad + BELLY_DK
  seat + BELLY patch) stacking in a small area — at 1x it reads slightly busy /
  target-like. Simplify to a single clean rose belly oval inside the body.

### 2. Reads as the classic DEVIL, scary-cute — PARTIAL
- KEEP: pot-bellied smug stance, gold belt cinch, cloven hooves, goatee, snaggle-
  fang — all the canonical cues are present and the intent is gleeful, not grim.
- FIX: the horns (see below) currently muddy the instant devil read by tipping
  toward bull. Tighten them and the at-a-glance read locks.
- FIX: the right "brace" arm reaches up the fork haft at a stiff diagonal and the
  hand-ball floats off the haft — it reads awkward/disconnected, not a confident
  twirl. Either plant the hand ON the haft (clear grip) or drop it to a hip/akimbo
  pose and let the fork stand on its own. Right now it's the least charming line in
  the figure.

### 3. Color — PASS
- KEEP: cherry-red dominant, crimson shade, rose belly, cream horns, gold trim —
  harmonious, bold, unmistakably the red anchor. Holds focal hierarchy well.
- FIX (night): on the night inset the body is fine, but confirm the RED_DK ears +
  brows don't merge into the head mass at 1x — consider nudging the ear-inner
  BELLY pink slightly brighter so the pointed elf-ears stay legible against the
  body on the dark sky.

### 4. Identity & consistency — PASS
- KEEP: sits naturally beside the existing roster's chibi grammar; the triad +
  outline recipe matches parrot/Big-Reapy. Gold trim ties to the coin/HUD family.

### 5. Distinctness — PASS (with the horn caveat)
- KEEP: pure-red lane owned; no skull; iron 3-tine fork distinct from the other
  fork-family props. Spade tail + goatee + belt all unique to this pick.
- FIX: the horn shape is the ONE distinctness risk — outward-swept horns drift
  toward the ram/bull primitive the set-wide guardrail forbids. Pull them
  upright-and-upturned so they can never be confused with A-side ram horns.

### 6. Feasibility — PASS
- Fully procedural, deterministic, imports only the game kit. No sprite thinking.

### 7. Accessibility — PASS
- KEEP: the grayscale cell proves the devil reads on value alone (horns + spade +
  fork silhouette carry it) — not hue-dependent. Good.
- FIX: in the grayscale strip the body-vs-belly value separation is weak (belly
  nearly matches body luminance) — the single-oval belly simplification above also
  helps the colorblind/value read.

### 8. Polish — PARTIAL (the 1x gate)
- The showcase figure is clean. The 1x insets are where it slips:
  - The FACE collapses at 1x. The wink-arc, button nose, smug-asymmetric mouth and
    snaggle-fang all blur into a dark smudge in the day/night insets — you read
    "round red head with two eyes" but lose the cheeky personality that IS the
    concept. The open eye is doing all the work; the wink + fang need to be bolder
    or simpler to survive.
  - The brow wedges are heavy at 1x and tend to merge with the eye, darkening the
    whole upper face into a band.

---

## Iteration directives (prioritized)

1. **Re-shape the horns to short + UPRIGHT + upturned.** Reduce the outward sweep
   (`out`/`length*0.32` term) by ~40% and increase the upturn flick so each horn
   rises mostly vertically then hooks to a sharp inward-leaning point — a little
   candle-flame, NOT a wide bull/ram V. This is the headline fix: it locks both the
   instant-devil read and the anti-ram guardrail. Keep them short (current length
   is fine once the sweep tightens).

2. **Make the face survive 1x.** Drop the snaggle-fang and wink to BOLDER, simpler
   shapes: thicken the wink arc, enlarge the fang triangle ~30% and keep its ink
   outline crisp, and thin/soften the brow wedges so they don't merge with the eye.
   Goal: at the day/night inset scale you should still read wink + grin + fang, not
   a dark smudge. Test by eye at the (c) inset size, not the showcase.

3. **Fix the right arm + simplify the belly.** Either plant the right hand clearly
   gripping the fork haft (contact reads as a confident twirl) or drop it to akimbo
   and free the fork; remove the floating hand-ball gap. Separately, collapse the
   three-ring belly into ONE clean rose oval so it reads bellied, not target-like,
   and improves the grayscale value separation.

Minor (if budget allows): brighten the ear-inner pink a touch for night
legibility; nudge the smug mouth asymmetry up slightly so it reads at 1x.

---

## References
- Classic cartoon red-devil mascot conventions (horns, spade tail, goatee,
  pitchfork) — the short upturned/candle-flame horn is the storybook read; the
  outward bull/ram sweep belongs to a different archetype:
  https://www.dreamstime.com/illustration/red-devil-mascot.html ,
  https://www.istockphoto.com/illustrations/devil-pitchfork-cartoon
