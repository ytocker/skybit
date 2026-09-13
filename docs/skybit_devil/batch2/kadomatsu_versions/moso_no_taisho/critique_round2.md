# Moso-no-Taisho — AD critique round 2

VERDICT: ITERATE (final GD round 3 — a focused two-fix pass, not a rebuild)

Bamboo-plant gate still solidly held (one fat node-collared culm at hero + 32px day/night/blackout). The
round-2 must-fix — ONE solid cream coin, no second cream focal — did NOT clear, and the foot fix
overcorrected into a louder new focal failure.

## Single-bright-coin gate: NOT cleared
1. **Top disc is STILL a doughnut, not a coin.** At 32px a distinct dark olive pupil sits in the cream
   ring → reads as a washer with a hole. CUT_HI flooded the ring-wall but the cavity is still too dark
   relative to contrast, so the eye locks the dark center.
2. **The foot is now a WORSE second focal.** The matte blessing-face was replaced by a pure-white,
   hard-edged, diagonally-striped glowing BALL — now the single brightest, highest-chroma object in the
   piece; on the 32px day chip the eye goes to the FOOT first. Reads as a golf ball/pearl/lottery orb —
   breaks bamboo identity. The wrong cream focal wins.

KEEP (landed): flared crown_collar (dumbbell/keyhole neck gone — disc sits like a crown); 5-6 big node
collars read + survive 32px; gold veins hairline (not boiling); foot L/R balance fixed (symmetric straw
+ mirrored pine + twin plums → stable standing-stone blackout); night rim holds.

## Round-3 punch list (final — items 1+2 are the gate)
1. **KILL the dark pupil → SOLID coin:** remove the cavity at render scale, OR raise `CAVITY` to within
   ~one value-band of `CUT_CREAM` so at 32px there's no dark center. Test: squint at the day chip — if
   you see a hole, it failed. (The parent `diagonal_cut()` already solved this collapse — re-check its
   CAVITY→CUT_CREAM value delta; this cavity is too dark relative to it.) Top disc = single brightest,
   near-uniform cream mass.
2. **DELETE the white foot ball (or crush it):** first choice REMOVE it (straw cinch + plum + pine give
   enough base life). If kept: not white (matte `GLOW (244,224,150)` at most), clearly smaller + lower
   value than the top disc, and NO high-contrast diagonal stripes (they sparkle + grab the eye). The top
   coin must win the value fight unambiguously at 32px.
3. Re-shoot the 32px day chip as the acceptance test: ONE solid cream coin crowning a fat green column,
   eye going to the TOP first, nothing competing at the foot.
4. Minor: tidy the hero disc's doubled upper-left ink rim to one clean keyline.
