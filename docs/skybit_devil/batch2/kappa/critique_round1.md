VERDICT: ITERATE

# KAPPA — Round 1 critique (art-director)

Solid bones: the bottom-heavy squat is right, the head-dish reads beautifully,
and the bamboo pillar mirror is the cleanest part of the sheet. But two of the
three pillars of this concept's 32px read — the **bright yellow-green body** and
the **turtle-shell hump** — are not landing, and the **beak** has gone missing.
This is an ITERATE, not a re-roll: the construction is sound, the fixes are
surgical, and the silhouette is one good shell-and-beak pass from shippable.

## Strongest → weakest (this concept)

- STRONGEST: head-dish. The turquoise bowl-with-ripple on the crown is crisp,
  reads at 32px and survives to 24px. Don't touch it.
- STRONG: bottom-heavy squat proportion + the bamboo node-banded shaft. Good
  chibi weight; clean repeatable pillar body.
- WEAK: body hue — drifting to a generic mid-leaf-green, NOT the pinned bright
  yellow-green. (see FIX 1 — this is the gate)
- WEAKEST: the turtle-shell. It's a brown hex PATCH on the side, not a domed
  hump on the silhouette; it vanishes by 32px. The signature "shell-hump" read
  is gone. Tied for weakest: the beak, which currently reads as a chest-bib.

## KEEP

- The head-dish: turquoise `(120,206,200)` bowl, single ripple, crown placement.
- The squat bottom-heavy mass and the big round friendly eyes (scary-CUTE is on).
- The bamboo pillar shaft: node banding + symmetric on-axis is exactly the
  Big-Reapy mirror grammar. House triad + ink keylines are present.

## FIX (prioritized punch list)

1. **BODY HUE — the gate. Push it to the pinned bright YELLOW-GREEN
   `(120,194,72)`.** Right now it reads as a medium leaf-green that is LESS
   yellow and LESS saturated than batch-1 Implet's acid-green — the exact drift
   the green-band pin exists to prevent. It must be the yellowest, lightest,
   WARMEST of the three greens: clearly lighter+warmer than Cernun's pine
   `(54,92,68)` and yellower than Tlaloc's grey-jade `(86,134,128)`. Verify by
   dropping all three creatures on ONE green day-sky card at 32px — Kappa should
   visibly jump warm/yellow off the other two. (It currently does NOT clear
   Implet; it must.)

2. **TURTLE-SHELL must become a domed HUMP on the SILHOUETTE, not a side
   patch.** This is half the concept's read and it's absent at scale. Move the
   shell to a domed hump rising off the BACK/top so the outline itself bulges —
   the alpha mask should show "froggy body + shell bump," readable at 24px.
   Render it as 2–3 big hard hexagon plates in turtle-bronze `(150,108,52)` with
   the dark-core/fill/top-left-sheen triad; do NOT scatter many small hexes
   (noise at 1x). Aim for the shell to be ~25–30% of the silhouette mass.

3. **Restore the BEAK as a face feature.** The current gold downturned triangle
   sits low and reads as a bib/chest-piece, not a beak. Put a small beak-gold
   `(228,188,72)` beak on the FACE between the eyes, breaking the head outline so
   it's a silhouette tell. The "head-dish + beak" combo is the signature — the
   beak can't be buried on the torso.

4. **Bamboo gap-edge CAP is under-rendered.** The brief's cap is a tipping bamboo
   dipper (shishi-odoshi) pouring a turquoise water-RIBBON into the gap. Right now
   the cap is just a flat bamboo stub. Build the tipping-dipper + spilling
   water-ribbon so the cap is a distinct, legible gap-edge event (mirror the
   head-dish water hue for cohesion), keeping mass on-axis.

5. **Add the cucumber.** The brief calls for the kappa clutching a cucumber — a
   cheap, high-charm read and a green-on-green value study. Keep it a hard flat
   triad shape, small, held low so it doesn't fight the shell hump.

6. **Belly/plastron.** Give the front a pale plastron oval so the bronze shell on
   the back has a value partner and the body isn't a single flat green mass — this
   also helps the yellow-green body read against green skies via internal contrast.

## Distinctness / sibling check (PASS-conditional)

Against Cernun (deep pine) and Tlaloc (grey-jade+coral) the SILHOUETTE KINDs are
clearly distinct — no shape collision. The risk is purely HUE: once FIX 1 lands,
the three-green band separates cleanly. Until then the body hue is the single
failing item that blocks ship.

## References

- Batch-1 Implet (acid-green imp) — the saturation/yellow FLOOR Kappa must
  exceed, not match: docs/skybit_devil/devil/implet/round_2.png
- Sibling greens for the on-one-card comparison: cernun/round_1.png (pine),
  tlaloc_tiki/round_1.png (grey-jade).
