# Mimi — thin crosshatch stick-spirit — ROUND 1 critique (art-director)

VERDICT: ITERATE

A genuinely charming, on-brief flat-graphic read — the dot-head + sprawled
mid-stride pose is instantly likable and the yellow-DOMINANT/LIGHT value pin is
nailed. But it does NOT yet clear the true-32 bar: the GD's flag is half-right.
The limbs survive (they don't fully dissolve), but the JOINT-DOTS — the
brief-pinned hue-blind tell — are effectively gone at 32px, and the thin ochre
limbs sit too close in value to the body to hold against a busy day sky. One
articulation/contrast pass and this ships.

## Ranking of issues (most important first)

1. **Joint-dots vanish at true-32 — the protected hue-blind tell is lost.**
   At 64px the pipeclay dot-joints read beautifully; at true-32 (and in the
   day/night sky chips) they collapse into the ochre limb and you cannot count
   them. The brief PINS the pipeclay dot-joints as the protected tell. Right now
   the tell is HEAD-ONLY at gameplay scale, which is acceptable as the anchor but
   NOT as the sole carrier — a stick-figure with no visible articulation reads as
   "scribble," which is exactly the failure mode the GD called. FIX: make the
   joint-dots fewer, FATTER and HIGHER-CONTRAST — drop to the 4 load-bearing
   joints only (two shoulders/elbows fused into one dot per arm, two hips/knees
   into one per leg) and render each as a 2px pipeclay square with a 1px ink ring
   so it survives smoothscale. Better four dots that read than eight that mush.

2. **Limb value too close to body — limbs go soft on the day sky.**
   The hatch-banded ochre limbs `(204,158,86)` are mid-light against the bright
   blue day chip and lose their edge; in motion they'll smear. The GD's "thin
   hatch nearly dissolves" is really a CONTRAST problem, not only a width problem.
   FIX (do this before fattening): push the limb KEYLINE darker/heavier — the
   charcoal hatch-keyline `(42,38,44)` should wrap the full limb at 1px minimum so
   the ochre always sits inside an ink edge at 32px. Then, only if still weak,
   bump limb width from ~2px to ~3px at the 1x native target. Keep the head
   oversized so it stays the anchor; do not let fatter limbs steal the head's
   dominance.

3. **Head interior reads muddy at small scale.**
   At 32px the two dark eye-marks blur into a single grey smudge inside the
   pipeclay disk, costing the face its scary-CUTE charm. FIX: simplify to two
   small high-contrast ink dot-eyes with clear pipeclay between them; ensure the
   ink keyline fully rings the head disk so it pops off both day and night skies.

4. **Spear/woomera pillar cap leans graphically thin and slightly Mokoi-ish.**
   The barbed spear-tip plaque is clean and bottom-rooted and the ember is
   correctly cap-confined — good. But the diamond-tip silhouette at the cap is
   close enough to a generic barb that it doesn't yet shout "thrown spear +
   woomera." FIX: add the woomera notch read — a small asymmetric hook/lug at the
   tip base — so the cap is unmistakably a spear-thrower, distinct from source
   Mokoi's totem-plaque and from the roster's other staff/pole caps. Keep
   shaft+~30%, on-axis mirror as drawn.

## KEEP (working — do not lose these)
- Oversized pipeclay dot-HEAD as the silhouette anchor — exactly the brief PIN;
  it carries the read at 32px and is the right call.
- Frantic mid-stride sprawl pose — genuine "doodle come alive" charm and energy;
  distinct silhouette from every sibling KIND.
- Yellow-DOMINANT, overall-LIGHT value structure — clean and correct.
- Ember strictly cap-confined; shaft hatch-banding + dot-knot-per-repeat tiles
  cleanly; on-axis mirror is honest.
- Flat fills, hard ink keyline, pattern-density detail — full flat-graphic
  fidelity, zero 3D triad creep. On-medium.

## CROSS-SET PIN ruling — Mimi vs Baiame
PASS, with a forward note. Mimi reads correctly as a LIGHT, yellow-DOMINANT body;
the grayscale-tell chip confirms a high-key value mass. Baiame is the deliberate
OPPOSITE (charcoal-DOMINANT block, yellow as accent) and is not yet rendered, so
there is no live collision to judge here — but the two KINDs are also
silhouette-distinct (sprawled thin stick-figure vs wide-arc authority block), so
even at 32px the value AND shape separation hold. No action needed on Mimi for
this pin; flag stays on Baiame's loop to keep its body charcoal-dark.

## Iteration directives (next-round punch list)
1. Re-render joint-dots: 4 load-bearing joints only, each a 2px pipeclay square
   with a 1px ink ring; confirm they're countable on the true-32 day chip.
2. Wrap every limb in a full 1px (min) charcoal keyline so ochre always sits
   inside ink at 32px; verify against the bright-blue day sky specifically.
3. Only if limbs still read weak after (2), widen limb stroke ~2px → ~3px at 1x
   native — keep the head visibly dominant.
4. Simplify the face to two clean ink dot-eyes with a fully-ringed head disk.
5. Add a woomera notch/lug to the spear-tip cap so it reads as spear-thrower, not
   a generic barb; hold shaft+30%, on-axis, ember cap-confined.
6. Re-post the SAME true-32 day/night/neutral row + 64px audit + grayscale tell so
   the dot-count and limb contrast can be re-judged at gameplay scale.
