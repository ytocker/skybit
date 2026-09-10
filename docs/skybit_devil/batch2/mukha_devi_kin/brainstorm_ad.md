# Mukha-Devi KIN — AD brainstorm cull (7 → 5)

VERDICT: ITERATE → locks to the 5 below. The 7-set is strong and coherent; the cull spends its
distinctness budget making the FIVE survivors maximally separable AT 32px, cuts the one direction that
re-fights a settled parent ruling, and tightens the two highest-risk corners.

## The SET read
A genuinely good sister-brood: all 7 keep the three pinned DNA elements — six-arm radial fan, rose/gold/teal
+ ink palette, chibi skull-face with the rose third-eye as brightest pixel. None drifts to a new silhouette
KIND, none invents a clashing hue, none goes realistic. Distinctness correctly lives in two levers (arm-end
ornament SET + skull treatment), with a real spread on both axes.
- **Weakness 1 — "ring of six small gold things" collision.** Ghanta bells / Astra chakra / Mala ring-clasps
  / Padma bloom-relics / Kapala cup-rims all resolve at 32px to "six gold-rimmed circles with a rose dot."
  Distinct at hero size; converge at gameplay scale. The cull must maximize 32px separability, not paper
  distinctness.
- **Weakness 2 — Astra re-litigates a settled ruling.** The shipped `relic()` docstring (render_mukha_devi.py
  lines 116–124): six distinct weapons were tried and REJECTED — "at 32px six fussy silhouettes blur to mush
  and pull weight to the rim, starving the face — the AD ruling." Astra is that exact idea. Cannot ship.

## The 5 to PURSUE (ranked)
1. **KAPALA-DEVI — six skull-cup wrath (TIGHT · skull-motif).** Strongest single direction; most economical
   (swap cap type only) and the cleanest read: six skulls ringing the rim like Mukha's six glow-caps.
2. **MAHA-KAPALI — great skull-crowned dread (LOOSE · skull-motif).** The brood's "final boss" + mandatory
   loose+skull-motif corner; only sister stacking skulls on BOTH crown and arms. Highest 32px risk → tightest spec.
3. **NRITYA-DEVI — dancing wrath (LOOSE · prominent).** The only POSE-mover; irreplaceable for loose+prominent.
   Dance-attribute arm-ends (scarves/bells/drum) are a unique ornament family, no collision.
4. **MALA-MATA — skull-garland mother (MID · skull-motif).** Irreplaceable for its CONNECTED rim — a
   continuous skull-garland swagged hand-to-hand vs everyone else's discrete caps. Different rim logic.
5. **PADMA-MATA — bloom-and-relic mother (TIGHT · prominent).** The non-wrathful tonal counterweight + accent
   showcase; "a flower with a tiny skull hidden inside" is the most scary-CUTE (most Skybit) hook on the page.

## The 2 to CUT
- **CUT ASTRA-DEVI.** Verbatim re-roll of the parent's rejected six-weapons idea (docstring lines 116–124);
  six fussy weapon silhouettes mush at 32px and starve the face. Also a big contributor to the gold-ring
  collision. Could only return as TWO alternating weapon types (= a recolor of Mukha, not a real sister).
- **CUT GHANTA-MATA.** The GD's own "control sister" — the deliberately-minimal entry; too precious a slot to
  spend on the least-changed idea. Its six gold dome-bells are the worst offender in the gold-ring collision
  (≈ Kapala cup-rims ≈ Mala clasps at 32px). Kapala owns the tight skull-motif corner more strikingly; Padma
  owns tight+prominent with more charm. Squeezed from both sides.
(Two cuts, not three — the remaining 5 cover both spreads with margin while staying maximally separable.)

## Per-survivor LOCK notes
- **KAPALA-DEVI:** six upturned `tiara_skull` craniums as bowls, rim-up, `GOLD` rim-band + pooled
  `ROSE`→`ROSE_BR` offering-glow inside; keep A-B-A-B by glow size (A fat bright pool / B small deep-`ROSE_D`
  ember); teal a hairline on upper-pair rims only. Six arm skull-cups + kept LOW 3-skull tiara = halo of 9.
  No crown/pose change. 32px: STRONGEST (skull cranium is the most-legible bone shape; `tiara_skull` proven).
  Watch: cap each rose pool BELOW `THIRD_BR` so the brow third-eye stays the single brightest pixel.
- **MAHA-KAPALI:** six skull-trophy strands — short `GOLD`-capped rod, TWO stacked `tiara_skull` trophies +
  a `ROSE` tassel-dot. Tall fanned mega-crown, centre skull lit `ROSE_BR`. LOOSE: taller upper mass, strands
  hang lower than Mukha's caps. 32px RISK (≈19 skulls = the "mush" failure mode): LOCK crown to 5 skulls
  (odd reads cleaner), arm trophies to 2 max (drop to 1 + tassel if the chip mushes); the GD MUST show a
  32px chip proving crown skulls don't merge into the topmost arm strands. Target read = "tall skull-crown +
  skulls dripping off the arms" value-clump, NOT 19 countable skulls.
- **NRITYA-DEVI:** asymmetric dance ornaments — 2 hands trail thin `ROSE` scarf-ribbons (flicked gap-ward),
  2 shake `GOLD` ankle-bell clusters, 1 spins a `TEAL`-headed `GOLD` damaru (rose cord), 1 holds a single
  `tiara_skull` rattle. Taller fanned ~4–5-skull crest. LOOSE: asymmetric arm angles + slight tribhanga tilt.
  32px: fatten scarves to short ink-keylined 2-segment ribbons (thin flicks vanish on busy sky); keep the
  tilt subtle (dance, not breakage). Hold crest ≤5 so it stays prominent, not Maha's mega-crown.
- **MALA-MATA:** six small `GOLD` ring-clasps each hanging a `tiara_skull`, joined hand-to-hand by a sagging
  `ROSE`-cord garland with gold spacer-dots; the three upper swags dip into the sky beside the crown, framing
  the face. 6 garland skulls + 3 tiara ≈ 9. MID. 32px: cord = 2px ink-keylined rose line; let the SKULL BEADS
  carry the read (a sag of skull-dots under the arms); protect the negative-space wedge above the crown.
- **PADMA-MATA:** six bloom-clusters — short `BONE`/`GOLD` petal-blobs around a central relic (A = `ROSE` disc
  in petals; B = `GOLD` seed-pod with `TEAL` dewdrop); TWO of six (mid arms) tuck a tiny `tiara_skull` bud in
  the petals. 3 tiara + 2 hidden buds = 5, soft → prominent not motif. No crown/pose change; faint coral-warm
  rose in bloom hearts (within family, clear of owned warm/red). 32px: LOW petal count (4–5 fat petals) so each
  reads as a chunky flower-mass; size the skull-buds ≥ tiara-skull footprint so "is that a skull?" survives.

## Push-apart fixes (police every round)
1. **KAPALA vs MALA (skull-motif pair):** separate by RIM LOGIC — Kapala skulls sit UP as cups WITH internal
   rose glow, evenly spaced; Mala skulls hang DOWN as inert beads on a visible cord, no internal glow. Show
   both 32px chips side by side to prove it.
2. **NRITYA crest vs MAHA-KAPALI mega-crown (tall-crown pair):** separate by COUNT + ROLE — Nritya ≤5 airy
   fanned crest, body/face lead (prominent); Maha 5 dense stack + lit centre + arm-trophies (motif). If both
   land at 5, push Nritya's fan wider/lighter and Maha's tighter/taller so silhouette mass differs.

## Spread-coverage audit
| Survivor | Tight ↔ Loose | Prominent ↔ Skull-motif | Corner |
|---|---|---|---|
| Kapala-Devi | TIGHT | skull-motif | tight + skull-motif |
| Padma-Mata | TIGHT | prominent | tight + prominent |
| Mala-Mata | MID | skull-motif | (mid bridge) |
| Nritya-Devi | LOOSE | prominent | loose + prominent |
| Maha-Kapali | LOOSE | skull-motif | loose + skull-motif |
All four corners filled; Mala bridges the middle. Both spreads covered with margin.
