# AD critique — Haedung (fire-eating guardian-lion totem-post) — ROUND 3 (final budgeted)

**VERDICT: ITERATE**

This is the final budgeted designer round, so it ships as-is WITH A FLAG. Most
of the design is locked and excellent — but the single round-2 ship-gate did NOT
land. The ember maw INTERIOR is still blown out to a near-white high-key yellow
(sampled L≈239–244, brighter than the eye-rings at L≈188) and it fuses with the
lit lower-face zone into one continuous bright mass. The focal read order is
inverted at hero scale: the lower face out-pulls the eyes, and the flame-curl's
cream tip is swimming in that bright field instead of popping. The 32px chips
still pass; this is a hero-scale value-control miss on the one note that gated
ship. One more pass on maw-interior value would clear it.

---

## Round-2 fix verification

- **Fix #1 — drop the maw INTERIOR a value notch toward spec ember mid `(238,128,64)`
  ≈ L152: NOT LANDED (ship-gate miss).** Sampled maw interior is `(252,252,~150)`,
  L≈239–244 — i.e. pushed UP toward near-white, the opposite of the directive. It
  is now the single brightest mass in the whole piece, out-valuing the cream
  eye-rings (L≈188) and matching the flame tip. The maw "blows out," it does not
  "glow." This is the exact failure round 2 named.
- **Fix #2 — dark chin/jaw separation band between maw and bell: PARTIAL / WEAK.**
  A vertical scan down the lower-face centre shows the bright maw zone (L≈230–244)
  running into the lit bell zone with only a thin, broken dark interruption rather
  than a clean continuous dark chin band. The maw and the upper bell still read as
  one connected light source; the warm focal still smears downward off the face.
- **Fix #3 — knock the bell's lit-area value down the last 10–15%: PARTIAL.** The
  bell plate itself reads gold-hardware (L≈154) which is fine, but its upper lit
  lip is caught in the same near-white spill as the maw, so the de-coupling reads
  as incomplete. Hue is correct; the lit-area value at the maw/bell seam is the
  problem.
- **Fix #4 — read order EYES > flame+maw > rest: NOT MET at hero.** Because the
  maw interior is the brightest mass, the read order at hero scale is currently
  LOWER FACE > eyes > flame, i.e. inverted.

## What HELD from earlier rounds (do NOT touch — all good)

- **Flame-curl — HELD and reads as a genuine flame.** Distinct ink-gapped comma-
  lobe with a hooked cream tip biting above the mouth corner, breaking the mouth's
  top silhouette. The fire-EATER soul is intact at hero AND at true 32px (day +
  night both legible). The ONLY thing hurting it now is the over-bright maw behind
  it stealing its value contrast — fix the maw and the flame pops on its own.
- **Eyes — HELD.** Simple round bug-eyes, single carved ring, warm-cream
  catchlight, thick ink keyline. Anti-Tlaloc compliant (no concentric goggles).
- **Brow-horn — HELD.** ONE stubby centered carved nub with triad dimension and a
  taper. Correct.
- **Mane — HELD.** Sparse ring of ~6 bold, spaced curl-lobes, each its own
  silhouette bump. Not a noise ring.
- **Jade — HELD (cross-set pin compliant).** Stays a blue-leaning SCALE-BAND
  course + mane-tip flecks — a placed accent, NOT a body fill or second mass. Eye
  glow stays warm-only. Clean separation from Muljang's prow-foam band and
  Hyeoljang's paua eye-ring.
- **Matte wood — HELD.** Honey-cedar tone, flat triad + ink keyline + 1px outline,
  no glaze/crackle/kiln sheen. Anti-Zhenmushou.
- **Pillar / weight — HELD.** Clean bottom-rooted mirror, visibly tall scaled cedar
  column, mask not top-heavy; fish-scale courses survive downscale as repeat
  texture.

---

## The remaining gap (state plainly — it ships with this flag)

At HERO scale the ember maw interior is rendered near-white (L≈240) rather than at
the spec ember mid (L≈152), so (a) the lower face out-values the eyes and the read
order inverts, and (b) the maw fuses with the lit bell lip into one bright mass
with no clean dark chin gap. The flame-curl, eyes, brow-horn, mane, jade, matte
wood, and pillar are all locked and shippable; this is purely an unaddressed
hero-scale value-control note on the maw interior. The 32px gameplay chips are
unaffected and pass, so in actual gameplay the miss is mild — but at hero/marketing
scale the focal hierarchy is wrong.

## Iteration directives (if a corrective pass is granted)

1. Pull the maw INTERIOR fill DOWN from `(252,252,~150)` / L≈240 to the spec ember
   `(238,128,64)` / L≈152 mid. Reserve the top cream value ONLY for the flame-curl
   tip and a single thin maw rim-lick — the maw glows, never blows out.
2. Re-establish a continuous dark chin/jaw band (`(28,22,30)` ink keyline + cedar
   shade) across the full width between the lit maw and the bell so they are two
   shapes, not one light source. The bell sits a clear value below the maw.
3. Kill the near-white spill on the bell's upper lip so its lit area never matches
   maw key.
4. Re-shoot the hero render and confirm read order EYES > flame-curl + maw ember >
   everything else, with a visible dark gap under the chin.
5. Do NOT touch the 32px chips, flame-curl shape, eyes, brow-horn, mane, jade,
   matte wood, or mirror — all HOLD.
