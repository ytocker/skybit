# DR. QUILL — Round 1 critique

`VERDICT: ITERATE`

Strong first pass and a decisive recovery from the prior grim-realist failure.
This is unmistakably bold-flat chibi: FLAT fills, hard ink keyline, the triad on
the head/hat, saturated apothecary-green + waxen-gold + magenta, and a clean
outline pop. The goggle eyes are the win of the sheet — big magenta lenses with
glowing pink pinpricks read curious-clinical-bird at a glance, exactly the
scary-cute "say aaah" beat. Macaw-cousin separation is already landing (brim hat
+ goggles + sickly palette = not the hero). But three things keep it from
ship-ready: the BEAK fails its own spec (the single most important read for this
pick), the VIAL prop is mis-masking so the chartreuse tincture reads magenta and
the prop->pillar story is muddy, and the 1x silhouette is losing the figure into
the robe/cape on both skies. Fix those and this is very close.

## Strongest / weakest

- **Strongest:** the goggle-lens face. Gold rim -> ink -> magenta glass -> pink
  pinprick + white catchlight is the charm engine and it survives to 1x. Keep
  it almost exactly. House-style finish is correct — no drift to gradients or
  soft edges. Palette is bold and clearly off the hero's primaries.
- **Weakest:** the BEAK. It is short, stubby, droops down off the lower face,
  and reads more like a hooked snout than the "long straight downward
  plague-mask spike." This is THE silhouette this pick exists to own, and right
  now it's the closest thing on the sheet to a recolored hero bird. Confirming
  the GD's own flag: overrule "maybe too short" — it IS too short, and it's the
  top fix.

## KEEP

- Goggle lenses + glowing pink pinprick eyes + catchlight (charm + scary-cute).
- Brim-hat construction (brim disc + crown + waxen hatband) — instant
  not-a-hood, not-a-macaw read. Hold this.
- Flat-fill + ink keyline + triad discipline. Zero off-style drift. This is the
  correction working.
- Apothecary-green / waxen-gold / magenta palette identity. Disjoint from the
  hero and from the other 4 bosses.
- Bird-foot talons at the hem — small but they seal the bird read; keep them but
  make them survive 1x (see directives).

## FIX

- **Beak (house-style read + macaw separation).** Too short, too low, droops
  down. Spec wants a LONG STRAIGHT spike jutting forward and only slightly down.
  Right now it collides toward "hero hooked beak." Lengthen to ~1.9-2.2x head_r,
  raise the base so it exits the CENTER of the face (not the chin), and flatten
  the downward angle so it's a near-horizontal straight cone. The straight spike
  is the whole identity of this pick — make it the dominant silhouette gesture.
- **Vial prop mis-mask (confirming GD flag).** The tincture pool reads mostly
  magenta, not chartreuse — confirmed. The `BLEND_RGBA_MIN` rect-cut on the fill
  surface is interacting with the magenta glass beneath and the additive
  TINCTURE glow, so the chartreuse never dominates. The bulb should read
  GLASS-magenta with a clearly CHARTREUSE pool in the lower 2/3. Re-stack:
  draw magenta glass, then the chartreuse pool as an opaque flat shape clipped to
  the lower bulb (no additive glow muddying it), then the gold stopper, then a
  restrained glow halo OUTSIDE the bulb only. The two-color contrast (magenta
  glass / chartreuse fluid) is what sells "sickly tincture."
- **Prop->pillar legibility (cell B).** The pillar pair currently reads as a
  generic banded gold post with a magenta blob at the gap — the "vial" isn't
  legible as a vial at 1x, and the gold shaft is close in hue to the sandstone
  pillars it must sit beside (risk of reading as an ordinary pillar with debris).
  Make the gap-edge cluster unmistakably a stoppered vial (gold cork + bulb
  silhouette), push the chartreuse fluid so the gap mouth glows sickly-green
  (that green-at-the-gap is the signature), and add one ink/value break between
  the waxen shaft and the gap flourish so the flourish pops off the post.
- **1x silhouette mass (cells C/D).** At gameplay scale the figure is dissolving:
  the green robe + green hat + green head are one flat green blob, the violet
  cape disappears on the night sky, and the talons vanish. The face-cluster reads
  but the body doesn't hold a Death silhouette. Raise value separation between
  head and robe (the head is the same green as the robe — darken or shift the
  robe, or ring the head with a heavier keyline), and let the violet cape carry a
  brighter rim so it reads against BOTH skies. The whole figure must read as a
  distinct chibi shape at 1x, not just a pair of pink eyes floating in green.
- **Hat brim symmetry / right-side read.** The brim's right edge gets crowded by
  the staff and the collar; at showcase scale the brim looks slightly lopsided
  and the staff-side of the figure is busy. Tidy the overlap so the brim ellipse
  reads as one clean disc.

## Iteration directives (priority order)

1. **Lengthen + straighten + raise the beak.** Target ~1.9-2.2x head_r, base at
   face center, near-horizontal straight cone with a subtle downward tip. This is
   the identity read and the macaw separator — make it the dominant silhouette
   gesture. (House-style fidelity #1, macaw separation #5.)
2. **Fix the vial color stack so the pool reads CHARTREUSE inside MAGENTA glass.**
   Drop the additive glow from inside the bulb; clip an opaque chartreuse pool to
   the lower 2/3; keep glow as an outside halo only. Same fix on the boss's tiny
   cradle vial. (House-style #1, prop charm #2.)
3. **Raise 1x figure separation.** Break head-vs-robe value (they're the same
   green), give the violet cape a brighter rim so it survives the night sky, and
   thicken the talon/keyline so the body holds a Death silhouette at gameplay
   scale on BOTH skies. (1x legibility #4, accessibility.)
4. **Make the gap-edge vial read as a vial at 1x in the pillar pair** and push
   the sickly-green glow at the gap mouth; add a value break between shaft and
   flourish so the prop->pillar story is legible and the post doesn't read as an
   ordinary sandstone pillar. (Prop->pillar #3.)
5. **Tidy the brim/collar/staff overlap** on the right so the brim disc reads
   clean and symmetric at showcase scale. (Polish.)

## Notes confirmed / overruled
- GD: "beak too short/stubby" — CONFIRMED, top fix.
- GD: "tincture pool reads magenta not chartreuse" — CONFIRMED, masking bug in
  the fill stack; directive 2.
- GD: "goggle eyes pop well" — CONFIRMED, keep as-is.
