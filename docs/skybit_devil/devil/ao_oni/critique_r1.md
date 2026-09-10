# AO-ONI — round 1 critique (art-director)

VERDICT: ITERATE

A strong, honest first slab. The mass-language is right — this reads as a heavy,
broad, low-CoG strongman the instant you see it, and that owns a lane nothing
else in the set touches. House grammar (flat fills, ink keyline, triad) is
respected, the up-tusks + sulky pout land the scary-cute brief, and the blue is
genuinely the blue lane. It does NOT yet ship, for two reasons that both live in
the prop->pillar half of the spec: the kanabo shaft is too THIN to read as a
Skybit obstacle pillar, and the rivet banding is too fine/cool to survive 1x.
Plus three figure-level fixes. None are re-roll material — the concept is sound,
the execution needs a heavier, bolder pass.

## Strongest / weakest
- STRONGEST: silhouette mass + the up-tusk/pout face. The slab is the heaviest,
  most distinct body in the ten; the grayscale panel proves the read survives
  with no colour. This is the concept's whole reason to exist and it works.
- WEAKEST: the PROP->PILLAR. At true obstacle scale (cell b) the studded shaft
  is a thin grey pole stranded in a wide column of empty sky — it neither fills
  the pillar footprint nor reads "heavy iron kanabo." The pillar is the half of
  the brief that has to mirror cleanly and tile, and right now it underdelivers.

## KEEP
- The broad square-shoulder slab with tiny legs (cell a) — max mass-contrast, on-brief.
- UP-tusks: bold, ivory, unmistakably oni; survive grayscale and 1x. Hold these.
- Tiger-gold loincloth as the single warm accent popping the cobalt — good value/hue break.
- Cobalt + deep-indigo dark-core holds the day read against a bright sky (cell c, day).
- Sulky lower-lip pout = the scary-cute beat. Reads grumpy-sumo, not grim.

## FIX (ranked, tied to the lens)
1. PILLAR WIDTH / FEASIBILITY — the shaft must FILL the obstacle footprint. Right
   now `khw=10*ss` gives a post far narrower than `PIPE_W+2*OVERHANG`, so the
   pillar is mostly sky. A Skybit pillar IS the full-width obstacle. Widen the
   shaft to fill ~80-90% of `pw`, and make the rivet studs scale with it. This is
   the single biggest blocker.
2. RIVET BANDING LEGIBILITY (1x) — at native scale the rivet rows wash toward a
   blank grey bar (the exact failure the spec's guardrail warns against). Fewer,
   BIGGER, higher-contrast studs (push `RIVET` brighter and `RIVET_DK` darker,
   fewer rows), and make the inter-row dark groove a full-width band so the
   banding reads as rhythm at 1x. The studs are the pillar's identity — they must
   survive smoothscale.
3. NIGHT IDENTITY — the night glow halo washes the head to a pale cyan and you
   LOSE the cobalt (cell c, night). Drop or greatly soften the additive glow;
   instead lift night legibility with a cooler rim-sheen tick on the slab edge,
   keeping the body unmistakably cobalt. Identity must hold across both biomes.
4. OX HORN READ — the single stub-horn (head top-left) currently reads as a hair
   tuft, not a horn; it vanishes in grayscale. Make it bigger, blunter, amber,
   and clearly SEPARATE from the topknot silhouette so the "one short ox horn,
   no ram pair" guardrail actually reads. Or commit harder to making it a
   confident blunt nub the eye catches at a glance.
5. HEAD CLUTTER vs POLISH — topknot + side tufts + brows + horn crowd the small
   head at 1x and the topknot reads as a generic dark ball. Simplify the hair to
   one bolder topknot shape with 2-3 decisive spikes; let the brows go thicker
   and darker so the scowl is the face's loudest cue. Proportion the head a touch
   larger relative to the kanabo head, which currently competes with it.

## Top 3 directives (next-round brief)
1. WIDEN the kanabo shaft to fill ~80-90% of the pillar footprint and scale the
   studs up with it — the pillar must read as a full, heavy iron obstacle, not a
   thin pole in empty sky.
2. BOLDER rivets + full-width inter-row groove bands; fewer, brighter, higher-
   contrast studs so the banding survives the 1x downscale.
3. KILL the night glow wash — keep the head cobalt on the dark sky via a crisp
   cool rim-sheen, not an additive halo; and fix the ox horn so it reads as a
   blunt amber horn (not a hair tuft) in colour AND grayscale.
