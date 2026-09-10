# Mukha-Devi — six-armed wrathful bone-mother — Critique ROUND 1

VERDICT: ITERATE

A strong, genuinely distinct first pass. The radial-fan KIND is unmistakable and owns its slot in the roster, the warm dusty rose-bone is on-pin (clearly NOT Leyak ash-white), and the magenta-rose glow is its own focal — clearly distinct from source cinnabar+ember. The blocker is the FACE-UNDER-STARBURST read at 32px, which currently fails: the six arms swallow the head into an undifferentiated blob and the third-eye/tiara do not survive. That is the hard rule in the brief, so it gates SHIP. Two secondary fixes (relic-type simplification + tiara count legibility) come along for the ride.

---

## Strongest / weakest

- **Strongest:** KIND distinctiveness + palette. Six even arms fanning around a central skull is the only radial silhouette in the brood and it reads INSTANTLY as "many-armed death-goddess showing off." Rose-bone is warm-dusty and on-pin; magenta third-eye + relic glow is a clean, owned focal. House-style triad (dark-core → fill → top-left sheen), hard ink keyline, 1px outline all present and consistent with Citipati.
- **Weakest:** the FACE loses the fight with the arm-starburst at 32px. The brief's hard rule — "the radial fan must FRAME the face, not swallow it" — is not yet met. At true gameplay scale the head is just the bright center of a spiky blob; the three-eye tell and the 3-skull tiara are gone.

---

## Per-aspect KEEP / FIX

### 1. FACE under the starburst (HARD RULE — most important)
- **FIX.** At 32px day AND night the skull-face is a featureless pale lump at the hub of the fan. The two eye-sockets, the magenta third-eye, and the jaw all vanish. Right now the arms read but the CHARACTER (a face) does not — it looks like a hand/firework, not a goddess.
  - Make the head **bigger relative to the arms** — push chibi proportion harder. Target head ≈ 38–42% of the creature's bounding height; currently it's closer to ~28% and the arms out-mass it.
  - **Open the radial gap around the face.** The two inner arm-pairs originate too high and too close to the skull crown, crowding the head from above. Drop the arm origin points to shoulder/temple line and splay the upper arms wider so there's clean negative space ABOVE the tiara. The fan should bracket the face like a peacock tail behind it, not close over the top of it.
  - **Hold the third-eye as the brightest pixel on the whole sprite.** At 32px it must survive as the single magenta dot that says "this thing is looking at you." Bump its value/size ~1px-equivalent and keep the two socket-eyes a notch dimmer so the THREE-eye triangle reads as a triangle, not a smear. The eye triangle is the entire scary-CUTE charm here — protect it.

### 2. Relic-TYPE blur at 32px (you flagged this — RULING)
- **RULING: simplify. Six even blobs framing the face IS the radial read, and that read is GOOD — keep six.** But the per-weapon TYPE differentiation is not worth fighting for at 32px and is actively costing you: chasing chakra-vs-bell-vs-cup detail is what's pulling visual weight out to the rim and starving the face. Do NOT try to make six distinct relic silhouettes legible at gameplay scale — that's a hero-zoom-only flourish.
  - Collapse to **2 relic types max, alternating** (e.g. a round disc-relic and a gold triangle/flame-relic, A-B-A-B-A-B around the fan). Alternation gives rhythm and "six holy weapons" energy without six fussy shapes that all blur to dots anyway.
  - Keep the per-relic GLOW dots (magenta/gold) — those are what survive and read as "holy relics." The TYPE can live in the hero art; the 32px just needs six glowing caps in a ring.
  - Current outliers: the teal-trimmed "cup/box" relic at far right and the gold trapezoid at top read as a different visual family (squarer, flatter) than the round caps — at 32px the right side looks unbalanced/heavier. Even them up.

### 3. LOW 3-skull tiara (re-spec check)
- **KEEP:** count is correct — three skulls, demonstrably lower/shorter arc than Citipati's 5-skull crown. Good separation from the source.
- **FIX:** at 32px the tiara is invisible — it merges into the arm-bases and the skull crown. Two of the three skulls sit BEHIND/between the inner arms and get eaten. Once you open the negative space above the head (fix #1), seat the 3-skull tiara in that gap so it reads as a low crown ON the head, against sky, not buried in the arm cluster. It doesn't need to read as "skulls" at 32px, but it must read as a small dark-toothed band that lowers the crown's apparent count vs Citipati.

### 4. Pillar
- **KEEP:** banded bone shaft + ring-pendant relics is a clean, bottom-rooted, symmetric mirror. Gap-cap with the radiating hand-fan/bell is on-brief. The pendant rhythm tiles well.
- **FIX (minor):** the relic-pendants on the shaft inherit the same type-blur — same ruling, alternate 2 types. Make sure the gap-cap's little hand-fan doesn't read as a SECOND face; right now the bell-relic glow at the cap is good, keep that as the gap focal.

### 5. Body / proportion
- **FIX (minor):** the torso/base is a touch tall and columnar, which adds to "totem/hand" rather than "goddess." Shortening the torso and widening the base block slightly (more chibi weight-shift) will read more as a pint-sized deity and less as a candelabra. The magenta belly-gem is a nice secondary focal — keep it but make sure it doesn't compete with the third-eye for "brightest pixel."

---

## Cross-set pins (police)
- **Rose-bone warm-dusty, NOT white:** PASS. Clearly warm, clearly anti-Leyak.
- **Magenta-rose glow distinct from source cinnabar+ember:** PASS. Cleanly its own hue; reads on day and night.
- **Distinct KIND vs roster:** PASS. The only radial/many-armed silhouette; no upright skull-man read; clearly not Citipati's dancing-flamenco pose.
- **Tiara lower than Citipati's 5-skull crown:** PASS on count, FAIL on 32px legibility (fix #3).

---

## Prioritized punch list (do in order)
1. **Win the face fight.** Enlarge head to ~38–42% of body height; drop arm origins to shoulder/temple line; open clean negative space ABOVE the head so the fan FRAMES rather than caps the skull.
2. **Lock the third-eye as the single brightest pixel** and keep socket-eyes a notch dimmer so the 3-eye triangle survives at 32px. Verify on both day and night chips.
3. **Collapse relics to 2 alternating types (A-B-A-B-A-B), six glow-caps retained.** Stop chasing per-weapon type legibility at 32px. Balance the heavier right-side relics against the left.
4. **Re-seat the 3-skull tiara** in the new negative space so it reads as a low dark band on the head at 32px.
5. **Shorten torso / widen base block** for more chibi weight-shift; keep belly-gem secondary to the third-eye.
6. Re-render and re-judge specifically on the true-32px day AND night chips — the hero zoom already passes; the chips are the bar.

## References
- Your own source `citipati/round_2.png`: note how the 5-skull crown sits in open space ABOVE the face and the third-eye stays the brightest hub even at 32px — that's the face-framing relationship Mukha-Devi needs, just radial instead of crown-arc.
