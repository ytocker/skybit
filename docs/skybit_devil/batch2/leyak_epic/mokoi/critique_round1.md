VERDICT: ITERATE

# MOKOI — leyak-epic flat-graphic plank-mask — ROUND 1 critique (AD)

Strong, confident first round. The flat-graphic dialect is genuinely realized
(no smuggled bevels or gradients), the charcoal-dominant mass is right, and the
pipeclay dot tell survives the grayscale check — which is the whole game for
this concept. It is NOT ship-ready yet: the true-32px chip loses the mask read
to the strip, the ochre is sitting dangerously close to Mariachi/Karakasa, and
the cap+ember has a top-heavy/over-glow tendency at night. All fixable in one
round.

## Strongest / weakest
- **Strongest:** grayscale tell. The dotted two-eye + grin-bar mask reads as a
  *built, keylined* object in pure luminance — it is not a foreign flat cutout,
  and it is not a striped rope. That is the hardest bar this concept had to clear
  and it clears it. Hero panel (a) is legitimately epic and on-style.
- **Weakest:** the TRUE-32px-at-1x chips (panel c, "day/night/neutral" row). At
  true 1x the mask collapses toward the strip — the head does NOT dominate the
  budget the way `compact` intends, so the read is "speckled vertical bar with a
  blob on top," not "dotted plank-mask." This is the panel the orchestrator
  judges feasibility on, and right now it is the failure point.

## KEEP
- Flat fills + 1–2px ink keyline + 1px grown outline: house-built, not cutout. KEEP.
- Charcoal dominant, ochre minor, ember cap-only: palette discipline is correct. KEEP.
- Concentric ring-eye target motif + dot brow/cheek/chin rows: the signature reads
  and is distinct from every other roster face. KEEP.
- Pillar body construction (1 dot-band + 1 hatch-band per repeat, twin ochre rails,
  ink long-edges) mirrors cleanly with no top-heavy SHAFT. KEEP the body.

## FIX (ranked, actionable — this is the round-2 brief)

1. **HEAD MUST WIN THE 32px BUDGET (top priority).** On the true-32 compact chip
   the mask is not dominating. Push `compact` harder: grow the mask to ~70–75%
   of the icon's vertical budget and cut the strip to a single SHORT repeat
   (current `strip_mult=0.55` is still too long at true scale). Target read at
   1x: "a dotted mask with a stub of strip," head unmistakably the hero. Re-audit
   on the day/night/neutral 1x chips, not just the 3x blow-up.

2. **OCHRE COLLISION — shift it away from Mariachi/Karakasa.** Mokoi's
   `(206,150,72)/(170,108,52)` sits right on top of Mariachi sombrero-ochre
   `(214,168,84)` and Karakasa ochre-bamboo `(204,168,96)`. At 32px on a day sky
   these will read as the same warm. Push Mokoi's ochre REDDER/earthier (toward a
   burnt sienna, e.g. ~`(192,118,56)` bright / `(150,86,40)` deep) so it lands as
   a distinct red-ochre, not the yellow-ochre those two own. Keep both ochres a
   true MINOR mass — charcoal+pipeclay still carry the read.

3. **NIGHT EMBER IS OVER-GLOWING / CAP READS TOP-HEAVY.** In panel (b) the night
   cap glow (`gr ×1.7`, `alpha_center=210`) blooms wide enough that the ember
   stops being "confined to the cap" and washes into the gap and shaft — it
   reads as the brightest mass and pulls the eye off the charcoal silhouette.
   Pull night alpha down (~150–170) and the radius multiplier toward ~1.35 so the
   glow stays a contained cap halo. Also the plaque at `plaque_hw ×1.30` + the dot
   ring + ring-eye reads slightly heavier than the shaft at the gap line — trim
   the plaque to ~+20% and/or drop the outer dot-ring count so the cap doesn't
   crown-heavy the mirror.

4. **DOT CADENCE DRIFTS TO NOISE AT SCALE in the strip.** On the 1x-native pillar
   (panel b) the two tight dot rows per repeat start to merge into a texture
   rather than reading as discrete pipeclay dots — the protected tell weakens
   exactly where the pillar is seen most. Drop to ONE cleaner dot row per repeat
   with larger, better-spaced dots, OR widen the row spacing, so the dot stays a
   countable motif at true obstacle scale. Verify on the 1x native, not the 2x zoom.

5. **EYE INTERIOR MUDDLES AT SMALL SCALE.** The 6-band concentric ring-eye
   (charcoal/pipeclay/ochre/pipeclay/ochre/ink) is gorgeous at hero scale but the
   inner ochre-on-ochre bands (frac 0.66 OCHRE_D, 0.34 OCHRE_L) lose separation
   and turn to mud below ~64px. For the eye, alternate strictly pipeclay↔ink in
   the inner bands (reserve ochre for the OUTER ring only) so the target stays
   crisp value-contrast all the way down.

6. **SHEET COMPOSITION — title overflow (GD-flagged).** The round-1 title runs to
   the right edge. Next round, either shorten the header or widen the canvas; keep
   the three panels but give panel (c) a touch more breathing room so the 1x chips
   aren't crowded against the 3x/grayscale audits.

## Distinctness check (vs the locked set) — PASS with the ochre fix
- Charcoal-dominant mass: unique in the leyak-epic five (krasue mauve, tzitzimitl
  indigo, umibozu teal-black, nukekubi lacquer-black+gold). Holds.
- Pipeclay dot-pattern tell: unique, survives grayscale. Holds.
- Ochre: the ONE risk — see FIX 2. Once shifted red-ochre, clean vs Mariachi/Karakasa.
- Flat-graphic-via-pattern-density vs the triad-sculpted siblings: clearly the flat
  one, as briefed. Holds.

## References
- Benchmark the 32px head-dominance against how Vampire Survivors / Archero icon
  bosses keep the FACE the hero at tiny scale and let the "body" become a stub.
- Aboriginal X-ray/dot-painting cadence: countable dots beat dense fields at scale —
  fewer, larger dots read as "painted dots," dense rows read as grain.
