# Muljang — prow-rider ship-figurehead spirit · ROUND 1 critique

VERDICT: ITERATE

A genuinely strong first pass. The motion read lands — the ~15° lean + swept blade-lock
fan gives Muljang a silhouette none of its four siblings will have, and the heavy stacked
scroll base keeps the gap-cap from going top-heavy. It is recognizably the same elevated
chibi/scary-cute house style as the Jangseung source, not a clone of it. One real,
already-flagged problem keeps it from ship-ready: the lit cap/face value drifts ~60 L
points lighter than the teak body, breaking the "creature IS the pillar" wood read. That
plus a couple of legibility tightenings at 32px are this round's brief.

## Ranking — strongest to weakest aspect
1. **Motion silhouette (hook).** Excellent. The lean + blade-lock hair fan is the set's
   only motion read and it's unmistakable even in the day-sky thumbnail. Keep it.
2. **Base weighting / mirror.** The stacked foam-curl scroll mass reads heavy and
   bottom-rooted; the gap-cap mirror is clearly not top-heavy. On-axis spine holds. Keep.
3. **Cross-set pin discipline.** Sea-teal is held to the foam scroll-eye band + eye-paint
   (not a body fill), coral is a single small lip/medallion focal, eye glow is warm. Clean.
4. **Cap-to-hero value match (THE FIX).** The lit face plate is far too pale — see ruling.
5. **32px feature legibility.** The two big eyes survive; the blade-lock fan and coral
   focal start to mush at true 32px night. Tightenable, see punch list.

## RULING — tighten the cap-to-hero value match (the GD's flag is correct)
I sampled the committed PNG. The lit salt-bleach face plate reads **L≈204,
RGB≈(232,207,161)** — essentially a cream value. The teak body fill reads **L≈141–146,
RGB≈(201,155,96)** (correctly on the locked `(204,158,98)` teak). That is a ~60-point
luminance gap. At gameplay scale the cap/face stops reading as the same carved teak as the
body and starts reading as a separate pale-stone mask sitting on top of a wood post — which
fights both "creature IS the pillar" and the teak-dominant spec.

**Rule: tighten it. Teak body value stays dominant; restrain the salt-bleach on the lit
face.** Concretely:
- Cap the salt-bleach sheen on the face plate at roughly **L≈170–180** (a warm light-teak,
  not cream). Target the lit face within ~25 L of the body fill, never more than ~35.
- Keep salt-bleach as an EDGE treatment (wind-facing rim of cheek/brow/scroll), not a
  full-face fill. Right now it's flooding the whole cheek mass; pull it back to a
  top-left rim-sheen sliver so the cheek core stays teak.
- The eye/lip glow can stay bright — they're meant to be the warm focal — but they
  should sit ON teak, not on a bleached plate. Let the warm eye glow do the "lifts the
  cap so it reads at night" job that the over-bleach is currently doing wrongly.
- Net: the white eye-rings remain the brightest thing; teak is the dominant value; the
  salt-bleach is the third-tier accent it's specced to be.

## KEEP
- The lean angle (~15°) and blade-lock fan — exactly the motion hook the brief wanted.
- Heavy scroll base; bottom-weighted, non-top-heavy mirror.
- Teak body hue/value (on-spec, and reads a hair cooler/greyer than Haedung's honey-cedar
  will — good separation on the closest wood pair).
- Sea-teal confined to the foam/eye band; coral as a single small focal; warm eye glow.

## FIX
- **Cap/face over-bleach** (above) — top priority.
- **Blade-lock count + read.** Count the fan — brief is ~5 hard blade-locks max. The hero
  currently fans more than that and at 32px night they collapse into a single dark fringe
  with no internal read. Drop to 5 chunky hard-edged locks with visible teak gaps between,
  so the fan still reads as swept HAIR (motion) and not noise.
- **Coral focal at scale.** The coral lip/medallion is the only warm-saturated focal but
  it nearly vanishes at true 32px (the medallion dot does most of the work; the lip line
  is sub-pixel). Slightly enlarge the medallion and thicken the lip so the coral survives
  downscale as a deliberate dot, not stray noise.
- **Mid-body teal eye-scroll.** The teal commas on the scroll mass are reading as a second
  teal cluster competing with the eye-paint. Confirm they stay the deeper/cooler PROW-FOAM
  value (deeper than Haedung jade) and keep them clustered/few so they don't grow into a
  band that rivals the body mass.

## Iteration directives (prioritized)
1. Restrain salt-bleach on the LIT face: bring the face-plate fill from ~L204 down to
   ~L170–180, within ~25 L of the teak body; convert the bleach from full-cheek fill to a
   top-left rim-sheen sliver. Keep teak the dominant value on cap AND hero.
2. Let the WARM eye/lip glow (not the bleach) carry the cap's night lift; verify the cap
   still pops on the night-sky chip after the bleach is pulled back.
3. Reduce the hair to exactly ~5 hard blade-locks with teak gaps; verify the fan reads as
   distinct swept locks (not a solid fringe) on the 32px night chip.
4. Enlarge the coral medallion + thicken the coral lip ~1px so the single coral focal
   survives true-32px downscale.
5. Confirm the mid-body teal commas are the deeper prow-foam value and stay a small
   clustered accent, not a second teal mass.
6. Re-pull both 32px day + night chips after the above and confirm: teak-dominant value,
   one clean two-eye face read, swept-hair motion legible, coral dot present.

## References
- Source lineage for house style + mirror discipline:
  docs/skybit_devil/batch2/jiangshi_epic/jangseung/round_2.png
- Locked brief (concept #3 muljang + cross-set pin):
  docs/skybit_devil/batch2/jangseung_versions/brainstorm_locked5.md
