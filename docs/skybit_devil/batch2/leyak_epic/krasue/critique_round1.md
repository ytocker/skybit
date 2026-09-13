VERDICT: ITERATE

# Krasue — Round 1 critique (Leyak-epic concept #1)

Strong bones: the cool dusk-mauve body vs warm-gold-confined-to-orbs lane is
correctly built, the pillar is genuinely grounded in the creature's own forms
(orb-string shaft + cracked end-orb cap), and the triad/keyline/outline house
grammar is intact. But it does NOT yet clear the bar on the two things that
matter most for a boss: the **32px read fails** (sleepy face collapses to a
generic two-gold-eye skull; orb-string nearly disappears) and it does **not yet
feel EPIC** (it reads as a mid-tier coin/skull pickup, not a boss). One more
round fixes both.

---

## Ranking of the design's aspects

1. **STRONGEST — palette lane / color discipline.** Body stays cool mauve, gold
   is strictly inside the orbs, never on flesh. Clean separation from Ifra
   (coral body) and from shipped Leyak (ash-white + hot-pink). This is locked;
   protect it.
2. **STRONG — pillar groundedness + mirror.** Orb-string shaft and cracked
   lantern-orb cap are the creature's own forms, on-axis, no top-heavy cap. The
   cap is correctly modest. Good.
3. **WEAK — 32px legibility of the face.** At the true chips the half-lid sleepy
   read is gone; the two gold eye-glows merge into "skull with two gold dots."
   It loses its own identity and drifts toward a generic skull/Necrarch read.
4. **WEAKEST — EPIC scale + orb-string survival at size.** The orb-string is the
   silhouette signature and it is the FIRST thing to die at 32px (collapses to
   2-3 faint pale dots). And nothing about the hero panel says "boss" — the head
   is small in its own frame and the glow is timid.

---

## KEEP

- Cool dusk-mauve face/skull `(150,128,150)` base with the lilac top-left
  rim-sheen — reads cleanly cool on day, night AND dusk chips. Hold it.
- Gold `(255,224,128)` confined to orb interiors only. Zero gold bleed onto
  flesh. This is the whole concept; do not let it leak.
- Cracked bottom lantern-orb as the gap-cap, on-axis, modest size. Mirror is
  clean. Keep the crack as the cap's distinguishing tell.
- 1-2px ink keyline + 1px grown outline — silhouette pops on all three
  backgrounds. Correct.
- Grayscale chip: body-vs-orb VALUE separation survives (orbs read lighter than
  skull). Accessibility tell is hue-independent — good, keep it.

## FIX

- **Face dies at 32px (priority 1).** On the true chips the sleepy half-lids
  vanish and you get two equal gold blobs = generic skull. The eyes are doing
  two jobs (glow + expression) and winning at neither. The sleepy-CUTE charm is
  the hook and it's invisible at size.
- **Orb-string evaporates at 32px (priority 2).** The signature "head on a
  beaded gut-string" is the silhouette KIND. At the chip it's 2-3 washed-out
  dots that don't read as a string and barely separate from the sky. The boss's
  one-of-a-kind read is the part that disappears first.
- **Not EPIC.** Hero head occupies maybe half its panel and the glow is gentle.
  Next to a boss expectation this currently reads as a coin/skull power-up, not
  a screen-filling threat. Per brief: push render scale, more geometry, richer
  triad, stronger `make_glow_surface`.
- **Orb glow lobe is flat/centered.** Each orb's gold is a soft centered fill;
  it lacks the inner glow-LOBE the brief calls for and the top-left rim-sheen,
  so the orbs read as flat gold discs, not luminous gut-lanterns.
- **Eye-socket vs eye-glow conflation.** Because both eyes glow gold equally and
  the mouth is a small ink grille, the face has no clear focal hierarchy — at
  size it's symmetric-blobby. The mouth/teeth row also nearly disappears.
- **Sinew is invisible at 1x.** The "thin sinew" threading the orbs doesn't
  carry; at the chip the string has no connective tissue, so the orbs look like
  detached coins rather than a strung gut-line.

---

## Iteration directives (prioritized, concrete)

1. **Make the sleepy half-lids read at 32px.** Don't rely on the gold glow to
   carry expression. Add a hard ink `(28,22,30)` upper-lid bar across the top
   ~45% of each socket so the half-closed shape survives downscale; let only a
   thin gold crescent of glow show beneath it. The lid is a SHAPE tell, not a
   value tell — it must be ink, not a darker mauve.
2. **Fatten + separate the orb-string so it survives the chip.** At true scale
   the string must read as >=3 clearly distinct beads. Drop to a clean cadence of
   larger orbs (5 in the shaft is fine for the hero, but size them so each is
   >=3px and clearly gapped at 32px). Push orb value/saturation up ~15-20% and
   give each a 1px ink keyline so they don't smear into one blob or wash into the
   night sky.
3. **Render the sinew as a visible 1-2px ink thread** running through the orb
   centers, with a hint of mauve shade on its underside. It must connect the
   beads into one string at 1x, not just at the hero scale.
4. **Add the inner glow-lobe + rim-sheen to every orb.** Three-zone each orb:
   warm-gold core glow lobe (offset slightly down-right, like a lantern flame),
   mid gold fill, and a small lilac-cool top-left rim-sheen pip. That converts
   flat discs into luminous gut-lanterns and reinforces the warm-in-orb /
   cool-body story.
5. **Push EPIC.** Scale the head up to ~60-65% of the hero frame; add a soft
   cool-mauve outer aura around the whole head (low-alpha `make_glow_surface`,
   restrained — NOT a gradient wash) and a stronger warm bloom localized inside
   the orbs only. Add membrane veining on the skull dome (thin lilac-sheen hatch
   lines) for the "more geometry" elevated read — keep it crisp, it must not turn
   to noise at 1x (test it on the chip before committing).
6. **Give the face a focal hierarchy.** Make the cracked brow / a single tell or
   the mouth-grille the secondary read so the head isn't bilaterally
   symmetric-blobby. Strengthen the tooth grille to a bolder ink shape so the
   "lantern-skull" (jack-o tell) survives at size — right now it's the cleanest
   cue to NOT being Necrarch/Yurei and it's too faint.
7. **Cap polish.** The cracked end-orb cap is good; add the same inner glow-lobe
   so it clearly LIGHTS the gap (the brief's "lanterns the gap"), and make the
   crack a 1px ink line with a thin lilac-sheen lip so it reads as cracked
   ceramic, not a smudge.
8. **Re-verify on chips before next commit.** The pass/fail test for round 2 is
   the 32px DAY and NIGHT chips, not the hero panel: the sleepy half-lid, the
   3+-bead string, and the lantern-skull grille must all be legible at 1x.

---

## Cross-set distinctness check (holds, with one watch)

- vs **Ifra** (shipped): clean — Ifra coral body + saffron flame; Krasue cool
  mauve body + gold-in-orbs. No conflict.
- vs **shipped Leyak**: clean — Leyak ash-white + hot-pink trailing viscera;
  Krasue mauve skull + gold orb-string. Different hue + different trail KIND.
- vs **Yurei / Necrarch / Karakasa / The Hollow**: **WATCH.** At 32px the current
  collapsed "round skull + two gold eye-glows" drifts toward a generic
  lich/skull read and could blur against Necrarch (also a glowing-socket skull).
  Directives 1, 2 and 6 (ink half-lids, surviving orb-string, bold grille) are
  exactly what re-opens the distinct lane — the sleepy-cute lantern-skull on a
  bead-string is the separator, and right now it isn't surviving the downscale.

## References

- Big Reapy bone-bident mirror (in-roster) as the cap-mass benchmark: cap should
  feel like a finial that drops mass toward the gap line — Krasue's already does;
  match its glow-restraint.
- Plants vs. Zombies / Angry Birds boss reads: expression carried by hard
  ink-shape lids + a single dominant focal, never by glow alone — that is the fix
  for directive 1.
