VERDICT: ITERATE

# Nukekubi (Leyak-epic #5) — Round 1 critique

A strong, confident first pass that nails the hardest pin in the brief: the black/gold/coral
stack genuinely carries the silhouette, and at true 32px this reads as an ornate crowned head
with a warm collar below — NOT as the porcelain-face source Leyak. The distinctness gate is
PASSED. It iterates, rather than re-rolls, because three concrete things keep it off ship-ready:
the gold-pin halo dissolves to noise at 32px, the pillar shaft tiles muddy, and the face/collar
junction has a value collision. All fixable in one round.

## Strongest aspect
The face-mitigation pin is the win. Lacquer-black top-knot is clearly the dominant mass, gold
pins are the second read, coral collar is the warm focal — face is well under 25% and sits as a
small powder lozenge. Demure half-lid eyes + bow-mouth land scary-CUTE with zero Leyak grin and
zero ash tone. On both day and night chips the creature stays legibly the SAME creature — the
collar's coral pops on the blue day sky and the gold pins pop on night. That cross-biome
robustness is exactly what the brief asked for.

## Weakest aspect
The gold kanzashi-pin halo. At hero scale it's gorgeous (8 fanned pins, clean radial), but at
true 32px (see the DAY/NIGHT chips) the individual pins collapse into a dotty gold fringe that
reads as visual fizz / dirt around the head rather than a crown of pins. It's the one element
doing the most work in the brief and the one degrading worst at scale.

## KEEP
- Black/gold/coral stack and its 32px hierarchy (Distinctness, Color) — locked, don't touch the
  intent.
- Top-knot lacquer sheen lobe — clean single hard rim-sheen, correct triad, not a gradient
  (House-style, Polish).
- Lobed coral flame-collar shape language — the petal lobes read as flame, not gore, and give a
  warm focal that survives downscale (Appeal, Readability).
- Bow-mouth + half-lid eyes — demure, cute, on-brief (Identity).
- o-fuda glyph charm shape on the shaft — the kanji-stroke marks are legible and on-theme.

## FIX (prioritized)
1. **Pins fizz at 32px (Readability — top priority).** The 8-pin fan is too fine to survive
   downscale. Drop to **5 pins max**, thicken each pin-stem to read at 1x, and FUSE the pin-heads
   visually into the top-knot's outline rather than floating them on thin gold wires — the
   crown should read as a single ornate jagged silhouette, not as a halo of separate dots. Test
   the chip BEFORE the hero render this round.
2. **Shaft tiles muddy (Pillar — high).** In the 1x native column the o-fuda + bead-knot repeat
   reads as an indistinct cream-and-gold stack; the bead-knot and the o-fuda are too close in
   value/size and the repeat boundary is lost. Raise the **value contrast between o-fuda (light
   cream) and bead-knot (dark lacquer or coral)** so each repeat has a clear LIGHT-then-DARK
   rhythm, and add a touch more vertical gap so the tile seam is unmistakable. The shaft should
   read as obvious beads-on-a-cord at gameplay scale.
3. **Face/collar value collision (Polish — high).** The warm powder face and the top coral
   collar-lobes sit at nearly the same value where they meet, so the chin/jaw edge mushes into
   the collar at 32px (the night chip shows the face dissolving downward). Add a **1px ink keyline
   or a darker neck-shadow notch** between face-base and collar-top to hold the chin edge — keep
   the face a crisp lozenge sitting ON the collar, not melting into it.
4. **Cap is slightly under-grounded (Pillar — medium).** The tassel + warding-bell cap radiates
   into the gap correctly (good, no top-heavy cap), but the bell currently reads as a generic
   gold blob — give it ONE clear bell silhouette beat (a flared lip + a clapper dot or a vertical
   seam) so it reads as a bell, not a coin, and so it visually rhymes with the bead-knots above.
5. **Coral collar on day sky (Color — medium).** On the DAY chip the coral collar against the
   warm-blue sky is fine, but verify it doesn't drift toward the shipped Ifra coral body — the
   brief deepened it off Ifra. Confirm the deepened coral `(232,108,64)` holds and isn't reading
   as Ifra's `(238,108,72)` at 32px; nudge slightly cooler/deeper if they collide.
6. **Minor — pin gold vs o-fuda gold-trim (Color — low).** The pin-gold and the shaft o-fuda
   gold-trim are the same hue; that's fine for cohesion, but make sure the pins read brighter
   (higher value) than the shaft trim so the head wins the focal hierarchy top-to-bottom.

## Accessibility
Passes hue-independence: the crown-jag SHAPE + the collar-lobe SHAPE + the strong dark-knot /
light-face / warm-collar VALUE ladder carry the read without relying on the gold or coral hue.
Keep that ladder intact through fix #3 — the face must stay the lightest value, knot the darkest.

## Bottom line
The identity is right and the distinctness pin is solidly cleared. This is a polish-and-legibility
round, not a rethink: simplify the pins so they survive 32px, give the shaft a clear light/dark
tile rhythm, and lock the chin edge. Re-shoot the 32px chip first and let it gate the hero render.
