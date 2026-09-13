# AD CRITIQUE — Quinkan-Imjim (knob-lollipop ambush-imp) — ROUND 1

VERDICT: ITERATE

A genuinely strong first round. The flat-graphic fidelity is clean, the lollipop
silhouette is unmistakable at hero scale, and the cross-set palette pin holds.
But it does NOT yet clear the bar at TRUE 32px, where the whole character collapses
into a single bullseye-ring that reads as a TARGET/dartboard, not a creature — and
that, plus the flagged hero foot, is what keeps this from SHIP-READY.

---

## RANKING OF ISSUES (most important first)

### 1. [BLOCKER — 32px] The knob is a bullseye, not a FACE. Lost identity at gameplay scale.
At hero scale (panel a) the knob reads as a charming chibi face: two big eyes, a
fanged grin, a yellow-ochre rim. Good. But on the TRUE 32px chips (panel c, day/
night and especially the 1x no-blow-up row), the eyes+mouth dissolve and what
survives is purely the CONCENTRIC PIPECLAY KNOB-BANDS — i.e. a red/white/charcoal
**bullseye**. That is the brief's hue-blind tell doing its job, BUT it has eaten the
character: at 1x this reads as a dartboard/target on a stick, not an ambush-imp.
The grayscale-tell swatch confirms it — pure rings, zero face.
- The fix is NOT to kill the bands (they're the tell and they're correct). It's to
  make the FACE survive alongside them. At 32px the eyes need to punch through the
  innermost band as 2 hard charcoal dots with a pipeclay catch-light, and the mouth
  as one decisive charcoal bar/fang-notch — sized so they read at native res, not
  just at SS=6. Right now the face features are sub-pixel at 1x and vanish.
- Compare to the source Mokoi (round_2): at 32px Mokoi keeps a clear two-eye + bar-
  mouth face on its plank. Quinkan currently loses its face faster than its parent.
  That's the regression to close.

### 2. [CONFIRMED — clean the foot] The club-body base reads as a tripod/flared stand.
You flagged it and you're right — RULE: CLEAN THE FOOT. On the hero (panel a) the
bottom band is a smoothscale-softened flared trapezoid that reads as a tripod base
/ lamp foot / rocket fin. It introduces a SECOND silhouette idea (a standing object
with a base) that fights the pure FAT-knob / THIN-neck / dot-club lollipop read the
brief pins. It also imports faint 3D-stand thinking into a flat-graphic piece.
- Replace the flared base with a flat, hard-edged terminal that stays on the club
  KIND: either (a) the club shaft simply ends in one more red-ochre handprint-stamp
  + a hard 1px ink cap, or (b) a single fat charcoal knob-foot echoing the head
  (a smaller bookend bulb) — NOT a widening tripod skirt. Keep it on-axis and no
  wider than the shaft so the mirror stays clean. Kill the smoothscale fuzz on that
  bottom edge specifically; it's the only place the keyline goes soft.

### 3. [PILLAR] Repeat is sound, but verify it doesn't also read as stacked targets at 1x.
The pillar construction (panel b) is correct to brief: dot-column + handprint-stamp
per repeat, knob-head finial at the cap (~+30%), ember CONFINED to the cap. Mirror
is bottom-rooted and on-axis — good. BUT the cap knob inherits issue #1: the gap-
edge finial at 32px is another bullseye. In a scrolling column of pillars, a stack
of identical red/white concentric rings risks reading as a row of targets rather
than lurking imp-heads.
- Once the cap knob gets its face-punch (issue #1), confirm the finial still reads
  as a tiny head at 1x. If the face truly can't survive at cap scale, lean the cap
  finial slightly more OVAL (head-shaped) than perfect-circle so silhouette alone
  signals "head," not "ring."

### 4. [FLAT FIDELITY] Mostly excellent — one watch item.
KEEP: saturated flat fills, hard ink keyline + 1px outline, detail entirely via
pattern density (concentric knob-bands + dot-column + handprint). No 3D triad
creeping in. Charcoal-dominant with the red-ochre lean is exactly the pin; thin
yellow-ochre rim is restrained; ember stays cap-confined. This is on-style and
sits naturally beside the source Mokoi.
- WATCH: the handprint stamps on the hero club are lovely at SS=6 but already
  mushing toward red blobs on the 3x/64px audit. At true 32px they'll be a texture,
  not a readable handprint — which is FINE (they're secondary density), but don't
  spend pixels trying to keep the fingers legible at 1x. Let the dot-column carry
  the body rhythm and let the handprint be a hero-scale reward only.

### 5. [DISTINCTNESS] Clear of source + roster. Hold the line.
KEEP: distinct from source Mokoi (plank-mask, not lollipop), no Tlaloc stone-goggle
mask, no Karakasa object-cyclops. The knob-lollipop KIND is unmistakable in its lane.
- The ONE drift risk is issue #1 turning it generic: a "ringed disc on a stick" is
  close to a number of casual power-up/target motifs. The face is what makes it a
  CHARACTER and keeps it off-the-shelf. Solving #1 also solves this.

---

## ITERATION DIRECTIVES (next-round punch list)

1. **Make the FACE survive at TRUE 32px.** Re-author the knob so at native res the
   two charcoal eye-dots (with a pipeclay catch-light) and a single hard mouth-bar/
   fang-notch punch through the innermost band. Test by reading the 1x no-blow-up
   chips ONLY — if it's a bullseye there, it's not done. The bands stay; the face
   must coexist with them.
2. **Clean the hero foot (CONFIRMED).** Remove the flared tripod base. End the club
   on-axis with either a hard-capped stamp or a small charcoal bookend-knob, no
   wider than the shaft. Kill the smoothscale softness on that bottom edge.
3. **Re-verify the cap finial at 1x** after #1 — make sure the gap-edge knob reads as
   a tiny HEAD, not a target. Nudge the finial slightly oval if a circle still rings.
4. **Confirm a scrolling column of pillars** doesn't read as stacked dartboards —
   shoot a quick 1x strip of 3-4 repeating pillars day+night to check.
5. **Leave the handprint as hero-scale-only reward.** Don't fight to keep fingers
   legible at 32px; let the dot-column carry body rhythm.
6. **Hold everything else** — palette pin, charcoal-dominant red-lean, thin yellow
   rim, cap-confined ember, flat fidelity, on-axis bottom-rooted mirror. All correct.

---

## REFERENCES
- Source parent for the face-at-32px bar: docs/skybit_devil/batch2/leyak_epic/mokoi/round_2.png
  (keeps a legible 2-eye + bar-mouth face on its 1x chip — match that read).
- Brief pin: brainstorm_locked5.md concept #3 — "Keep neck THIN + knob FAT; body
  detail must not compete with the knob." Currently the BANDS compete with the FACE;
  rebalance so the face wins the focal at 1x while bands carry the hue-blind tell.
