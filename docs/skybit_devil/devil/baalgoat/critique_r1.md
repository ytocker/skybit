# BAALGOAT (B2) — round 1 critique

VERDICT: ITERATE

A legible, on-palette chibi devil with a strong Baphomet skeleton (back-swept
amber horns + pentagram + bat-wing width + indigo) — but the two load-bearing
guardrails for THIS pick are not landing yet: the face does not read GOAT-MUZZLE
(it reads robot-visor / coin-slot), and the prop->pillar is broken (no banded
torch-pole body renders — the obstacle is just a floating cap). Both are
fixable without a rebuild. Iterate, don't re-roll.

## Ranking of issues (worst first)
1. **PILLAR is non-functional** — the headline mandate failure.
2. **Muzzle does not read as a goat** — the pick's whole reason to exist.
3. **Crown-torch loses to the cranium dome** — flame reads as a bald gold cap.
4. **Body/muzzle value-merge at 1x** — silhouette softens to a blob.
5. Eyes/horns/wings/palette — mostly KEEP.

## KEEP (working — protect these next round)
- **Back-swept amber ridged horns.** Exactly the owned curved-horn pair; ridge
  nicks survive, sweep reads, distinct from every other horn primitive. Don't
  touch the horn primitive.
- **Indigo + torch-gold + blood-red palette.** Bold, saturated, triad-flat, no
  realistic drift. Reads clean on day AND night; clearly NOT Glitchfiend neon /
  Pyrecrown green. Grayscale holds value separation. House-style fidelity: pass.
- **Bat wings as the width anchor + the pentagram medallion.** Wings give the
  1x silhouette its breadth; the gold-rimmed blood-red pentagram is an instant
  Baphomet tell. Keep both.
- **Scary-cute eyes.** Big sulphur lozenge eyes with slot pupils + derp tilt are
  charming and solemn-not-grim. Good.

## FIX (specific)
- **PILLAR (lens 3, the mandate).** At true obstacle heights the 96px `cap_band`
  eats the entire post, so `_torch_pole_body` never draws: there is NO indigo
  shaft, NO gold cuff bands, NO tileable repeat — just the brazier blob + a brown
  ember circle that reads as a chess pawn. This fails "torch-pole mirrors into a
  clean tileable pillar pair." The body must dominate; the cap must be a small
  detachable gap-edge flourish. Right now it's inverted.
- **MUZZLE (lens 2 + 5, the firewall).** The flat-bottom cream box with two
  vertical black nostril slots reads as a knight visor / vending-machine coin
  slot, not a goat snout. It is also the brightest, highest-value shape on the
  figure, so the eye lands there and the goat read is the thing that fails. A
  goat muzzle is a long tapering snout with the nostrils at the FRONT TIP and a
  visible mouth-line/lip — not a square plate with two punched holes.
- **CROWN-TORCH (lens 1 + guardrail).** Between the horns the flame sits so low
  and wide on the cranium that it reads as a shiny bald-gold skullcap, not a
  flame rising BETWEEN the horns. At 1x it fuses with the horn bases into one
  gold mass. It needs a clear dark gap of indigo cranium beneath it and a taller,
  narrower teardrop so "torch between horns" is unmistakable.
- **1x VALUE-MERGE (lens 4/7).** Head, body and wings are all the same FUR indigo
  with only a 1px keyline between them; at 1x the figure reads as one lump. The
  internal head/body break and the wing/body break need either a darker FUR_DK
  separation seam or a slight value step so the chibi proportions survive small.
- **MEDALLION SIZE.** At showcase the pentagram disc is large enough to read as
  the "face/belly," competing with the head. Trim it ~20% so it's an emblem, not
  a second focal point.

## Iteration directives (prioritized punch list)
1. **Rebuild the pillar so the POLE is the body.** Drop `cap_band` to ~28-34px;
   make the brazier bowl small and the flame a compact gap-edge cap. Ensure
   `_torch_pole_body` draws across the full remaining height with the indigo
   shaft + gold cuff bands visible and TILING at the 46px pitch even on a short
   bottom post. Prove the top/bottom mirror as one continuous banded pole with a
   flame at each gap-edge — that mirror is the whole point of this prop.
2. **Re-sculpt the muzzle into a real goat snout.** Taper it forward to a rounded
   tip, move the two nostrils to the front of the tip (not vertical face-plate
   slots), add a clear down-curved mouth/lip line, and DROP the muzzle value ~15%
   (less pure-white MUZZLE_SH) so it stops out-shouting the eyes/horns. Goal:
   reads "goat" in the grayscale cell without the horns helping.
3. **Lift the crown-torch off the skull.** Raise the flame stub, narrow the flame
   to a taller gold teardrop, and leave a visible band of dark indigo cranium
   below it between the horn bases so it reads as a flame BETWEEN horns, not a
   gold cap. Keep it warm-gold and small (guardrail: no neon, no green).
4. **Add a 1x separation seam** between head/body and wing/body (one FUR_DK step)
   so the chibi silhouette doesn't collapse into a single indigo blob at gameplay
   scale.
5. **Shrink the pentagram medallion ~20%** so it's an accent, not a second face.

## References
- Lévi's Baphomet — note the long forward goat snout + flame rising clear ABOVE
  the brow between the horns (the two reads this round misses):
  en.wikipedia.org/wiki/Baphomet
- For the pillar body/cap ratio, study how Big Reapy's bone-bident keeps a long
  repeatable shaft and a SMALL detachable cap — mirror that proportion here.
