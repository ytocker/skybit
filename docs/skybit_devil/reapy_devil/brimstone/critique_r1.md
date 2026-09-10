# BRIMSTONE (A2) — round 1 critique

VERDICT: ITERATE

The bones are right and the concept is alive — but the magma glow has eaten the
design. Right now this reads as a flaming OWL / jack-o-lantern, not a faceted
hellfire-STONE skull, because the additive bloom has drowned the charcoal-basalt
value anchor the whole concept depends on. The grayscale panel proves the
construction is sound (sockets + grin + crags carry a skull with zero magma); the
fix is almost entirely about restoring the COOL ROCK as the dominant value and
demoting the magma to disciplined accents. This is very recoverable in one round.

## Strongest / weakest

- **Strongest:** the grayscale read. Faceted crags, hex sockets and the square-
  tooth grin genuinely say "skull" with the color stripped — the silhouette and
  bone-logic are doing their job. The basalt COLUMN prop is also the clear win:
  it reads as a literal column with a fire cap and the top<->bottom mirror is
  honest. This is the most "literally a pillar" prop in the set, as promised.
- **Weakest:** value structure / glow restraint. The seam bloom is so wide it
  turns the entire figure orange — the "charcoal-basalt DOMINANT cool anchor"
  from the renderer's own palette note is gone. At showcase scale the rock only
  survives in scraps; at 1x day the figure is a warm blob with two glowing eyes.

## KEEP

- Faceted low-poly cranium + jagged crag outline — it reads stony and is NOT Big
  Reapy's smooth dome. Hold this.
- Hex ink sockets + chunky square teeth + one chipped tooth — the skull cues that
  survive grayscale. Keep them.
- The basalt column shaft, segment banding and brazier cap. Mirror works.
- The soot puff is a nice quiet beat (barely visible at 1x, fine — it's garnish).

## FIX (ranked, tied to the lens)

1. **GLOW IS OVERBLOWN — this is the headline fix (Color / Polish / Identity).**
   The seam `make_glow_surface` bloom (radius `width*2.2`, alpha 150, stamped per
   polyline point AND per circle) compounds into a solid orange wash over the
   whole skull and body. Cut it hard: roughly HALVE the glow radius, drop
   alpha_center to ~70-90, and stamp the bloom ONCE along the seam, not per-vertex
   AND per-node. The magma should look like light leaking from a CRACK in cool
   rock, not like the rock is on fire all over. After the cut, the charcoal must
   visually dominate (~65-70% of the figure's value mass) on the DAY sky.

2. **THE FACE READS OWL/JACK-O-LANTERN, NOT SKULL (Readability / Identity).**
   Two things cause it: (a) the sockets are big round full-disc orange "irises"
   with a white catchlight — that's an EYE, not an empty molten socket; and (b)
   the big yellow cheek-chevron under the sockets reads as an owl facial disc /
   pumpkin nose. Fix: make the socket a DARK angular cavity that is mostly INK,
   with only a small molten POOL low in the cavity (not a centered glowing iris),
   so it reads "empty eye socket with embers at the bottom." Kill or drastically
   shrink the yellow cheek-chevron — let the cheekbone be basalt, not magma. Right
   now magma is doing the face-drawing that bone should do.

3. **RESTORE COOL-BASALT AS THE PALETTE ANCHOR + PROTECT THE SOULFORGE FIREWALL
   (Color / Distinctness).** The brief requires Brimstone's all-over-lava palette
   to NOT collide with Soulforge's contained forge-orange — the intended
   separator is that Brimstone is STONE-dominant with seams, Soulforge is
   soot-dominant with sparks. As rendered, Brimstone is orange-dominant, which
   pushes it TOWARD the warm-skull cluster (A3/A8) the brainstorm flagged. Once
   the glow is cut (fix 1) this largely self-corrects, but verify on the final:
   the dominant impression at 1x must be "dark volcanic rock that's cracked,"
   not "orange creature."

4. **SEAM COUNT / WIDTH AT 1x (Readability).** On the body and column the seams
   are thin wiggly snakes that at 1x native turn to noise/squiggle. Per the
   guardrail, go BOLDER and FEWER: keep ~3 bold cranial seams, 1-2 on the body,
   1 down the column — each a confident zigzag with real width, not a sine wobble.
   A few decisive molten lines read; many thin ones shimmer.

5. **BROWS + EXPRESSION (Appeal).** The angular basalt brows currently sit as
   sharp up-swept wedges that, combined with the glaring round eyes, tip toward
   ANGRY/aggressive rather than scary-CUTE. Once the sockets become empty-with-
   embers (fix 2), soften/round the brow outer corner so the read is eager/curious,
   not a menace glare. The thesis is "magma grin blushes" — lead with the friendly
   grin, not the eyes.

6. **POLISH — column seam vs banding (Feasibility/Polish).** The column reads
   well but the magma seam sine-wraps over the segment joints awkwardly. Let the
   seam well BRIGHTER at the joints (as the docstring intends) and run straighter
   between them so the Giant's-Causeway banding stays the dominant column read and
   the seam is a secondary crack, not a competing element.

## Distinctness check (vs the set + roster)

- Still the set's ONLY angular/faceted skull — construction is genuinely distinct
  from every other pick. PASS on shape language.
- Palette collision risk with Soulforge is REAL right now (both reading
  orange-dominant). Fix 1 + 3 are what keep the firewall. Re-verify next round.
- The owl/jack-o-lantern read (fix 2) is also a soft collision with Big Reapy's
  jack-o-skull warmth — another reason to de-emphasize the glowing-face look and
  lean on cold stone + a small grin glow.

## References

- Look at how cooled-lava / "obsidian with magma veins" is handled in casual VFX:
  the rock stays near-black and the glow is a TIGHT rim on the crack edge only —
  e.g. Brawl Stars / Clash Royale lava-themed assets keep the dark value dominant
  and use thin hot cracks. That contained-crack discipline is exactly what fix 1
  is asking for.
