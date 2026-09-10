# A7 TWINFACE — round 1 critique (art-director)

VERDICT: ITERATE

The concept is alive and the half/half split DOES land at showcase scale — but
round 1 fails the two tests that matter most for this pick: (1) the split does
not survive 1x (the whole reason TWINFACE was locked was its clean asymmetric
read), and (2) several elements are rendering WRONG, not just weak — the devil
eye, the horn, and the pole finials are reading as the opposite of what the spec
intends. This is a fixable round, not a re-roll: the bones are good, the
execution is muddy.

## Ranking of this design's aspects (strongest -> weakest)

1. **The bone/skull half (showcase)** — STRONGEST. Clean hollow socket, bright
   teeth row, calm read. This half is doing its job.
2. **The split-robe body + gold throat clasp** — solid, echoes the divide,
   silhouette is clean.
3. **The pillar shaft / gold barber-banding** — reads as a tileable column at
   both scales; the mirror logic is sound.
4. **The gold seam** — present and the right idea, but under-powered (too thin,
   and the devil-side pink sheen fights it).
5. **The devil/red half** — MUDDY. The eye is rendering as a loud flat yellow
   disc (not the intended sly wink), the brow/mouth/fang collapse into the red,
   and the pink rim-sheen blob reads as a wound, not form.
6. **The single horn** — WEAKEST as identity. It sweeps back nearly horizontal,
   pale and thin, reading as a swoosh/banana behind the head rather than a horn.
   At 1x it vanishes — and the lopsided horn IS the silhouette gag.
7. **The pole finials** — WEAKEST as craft. Both the skull-knob and the
   fork/spade end are tiny ambiguous blobs; the skull finial reads as a little
   snowman/face, the fork barely reads at all.

## KEEP

- The vertical hard split as the core construction. It works at showcase — do
  not abandon it.
- The bone half almost entirely: socket + sulphur spark + three-tooth jaw row.
- The gold throat clasp and the split robe trapezoid.
- The banded bone+gold pillar shaft. The repeatable-mid read is genuinely clean.
- Vermilion + bone + gold triad. Palette family is correct and on-brief.

## FIX

- **The devil eye is wrong.** In the render it is a large flat yellow disc that
  out-shouts everything, including the bone socket. The spec calls for the devil
  side to WINK (sly closed arc) against the calm hollow skull socket. Either the
  wink arc is being drawn under a stray filled ellipse, or the glow+slit path is
  firing — the result is a solid yellow eye that reads angry/bug-eyed, not sly.
  This single element is breaking the "two halves disagree" gag.
- **Value structure on the red half is too low-contrast.** The DEVIL_SH
  dark-core, DEVIL fill, and DEVIL_HI pink sheen are all close in value, so the
  brow, smirk, fang, and goatee all sink into the red. The red half currently
  reads as a smooth red mass with one loud eye — i.e. exactly the "lumpy red
  skull" the guardrail warned against. The pink rim blob in particular reads as
  a soft wound, not as form-defining sheen.
- **The horn does not read as a horn.** It is pale (HORN_BONE on the warm-red
  half = low contrast), thin, and swept almost horizontally off the back, so it
  reads as a decorative swoosh. It must read as a HORN in the silhouette — the
  lopsided one-horn head is the locked distinctness hook. It also clips the panel
  edge.
- **The gold seam is too thin to be "the gag."** At showcase it is a narrow
  line; the devil-side pink highlight sits right beside it and muddies the
  divide. The seam should be the second-loudest thing after the eyes — a bold,
  high-contrast ridge that visually CUTS the head in two.
- **1x legibility fails.** In both day and night insets the head reads as an
  undifferentiated cream-and-red lump; the seam, horn, and devil features are all
  gone. On night the red half nearly merges into the dark sky on its shaded edge.
  The split must survive at gameplay scale or the concept hasn't earned its slot.
- **Pole finials are noise.** The skull-knob reads as a snowman/face and competes
  with the boss head; the fork/spade end is illegible. At 1x both finials are
  blobs. They need bolder, simpler, more distinct silhouettes (a clear crescent
  blade vs a clear two-prong fork), and the skull-knob should NOT mimic a second
  face.
- **Mouth/expression on the devil half is grim, not cute.** The smirk curve is
  drawn in DEVIL_SH on DEVIL — barely visible — and what reads is a downturned
  dark line. Combined with the bug-eye it tips grim. Push it sly/cheeky.

## ITERATION DIRECTIVES (prioritized punch list)

1. **Fix the devil eye to actually be the sly wink.** Make it a bold INK closed
   arc (lash-up curl) so it clearly contrasts the calm hollow bone socket. Kill
   the solid yellow disc. If you keep an open devil eye instead, make it a clear
   vertical slit on a lit lid — NOT a full yellow circle. The two eyes must read
   as two different moods at a glance.
2. **Raise the red half's internal value contrast ~30%.** Darken DEVIL_SH and/or
   ink the brow, smirk, and goatee in INK (not DEVIL_SH) so the devil features
   read as crisp dark marks on the red. Shrink the pink DEVIL_HI to a small
   top-left sheen tick instead of a large soft blob.
3. **Rebuild the horn so it reads as a HORN in silhouette.** Make it thicker at
   the base, sweep it UP-and-back at a steeper angle (more vertical), darken it
   against the red half (use HORN_SH as the body, HORN_BONE only as the lit
   edge), add 2 bold keratin nicks, and keep it inside frame. It should be the
   clearest single "devil" signpost in the blackout silhouette.
4. **Make the gold seam bold and dominant.** Widen it ~2x, give it a dark valley
   on the red side and a bright gold ridge, and pull the devil-side sheen away
   from it so nothing competes. Goal: at 1x the head still reads as two halves
   divided by a gold line.
5. **Redesign the two pole finials for clarity.** Skull end = a clean reaper
   crescent + a small bone knob that does NOT read as a face (drop the twin
   sockets or make them a single dark slot). Fork end = a bold, obvious two-prong
   spade. Test both at 1x — each finial must read as its own shape, not a blob,
   and neither should rival the boss head.
6. **Re-shoot the 1x insets and judge there first.** The split, seam, and horn
   must all survive at the inset size on BOTH day and night. On night, add a
   touch more contrast to the red half's shaded edge so it doesn't sink into the
   sky. If the split doesn't read at 1x after the above, simplify further (fewer
   devil-side marks, bigger seam) until it does.
7. **Confirm distinctness holds after the horn rework** — keep it ONE horn only
   (no second curved pair), and ensure the bolder horn doesn't drift toward A1's
   ram-spiral or B-group horn primitives. Single, asymmetric, profile horn.

## References / benchmarks

- Two-face / split-character casual reads stay legible by keeping the DIVIDE the
  loudest mid-frequency element and each half's features bold + few (cf. mobile
  two-face villain icons; the split line carries the read, not the detail).
- Hold the bone half as your value anchor; the red half currently has nowhere
  near the bone half's internal contrast — match it.
