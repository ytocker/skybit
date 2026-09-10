VERDICT: ITERATE

# Xinniang — Round 1 critique (Jiangshi-epic set, concept #3)

Strong, confident first pass. The thesis lands: this is unmistakably the one
saturated-vermilion mass in the set, the square-veil-under-gold-crown tell is
present and legible, and the pillar mirrors cleanly from the dowry-pole's own
forms. It does NOT collapse into Catrina (no wide plumed brim, no visible face)
or Yurei (no hair-curtain, no legless wisp — this is a rooted bell). It clears
the house-style bar on flat triad + ink keyline + procedural. It is NOT yet
ship-ready: the dead-eyes are too cute/owlish (GD's own flag — confirmed), the
crown-arc footprint is wide enough to flirt with top-heavy, and a couple of
details fuzz at true 32px. One more round gets this there.

## Strongest aspect
The COLOR + silhouette identity. At every scale the vermilion bell + gold
crown-arc + gold hem read as "red bride in a wedding crown" and nothing else in
the roster. The concave bell flare reads as silk, not a cone, even at 32px —
exactly the brief's hardest ask. Value contrast of gold-on-red is doing real
work. Keep all of it.

## Weakest aspect
The dead-eye treatment. At hero scale the two glowing dots sit far apart, are
large, round, and near-equal in size to the crown jewel — the read is "cute
owl/surprised face," not "two cold pinpricks of the dead glimpsed through a
veil." This is the single thing pulling the piece toward TOO cute and away from
the scary-CUTE dread the brief wants. RULING BELOW.

## RULING on the dead-eyes (GD flagged: too large/owlish)
The GD is right — shrink and tighten them. Specifics:
- Drop the eye-glow disc `int(6*s)` radius and the `EYE_GLOW int(3.4*s)` /
  `EYE_CORE int(2.0*s)` dots by ~30-35%. Two SMALL hot pinpricks read as dread;
  two big soft discs read as a face.
- Bring them CLOSER together: `sgn * int(9*s)` → roughly `sgn * int(6.5*s)`.
  Wide-set = owl/baby; close-set + small = uncanny corpse-stare. This is the
  highest-leverage change in the round.
- Keep them slightly NARROWED, not perfectly round — a faint downward squash
  (taller-than-wide is wrong; very-slightly wider-than-tall, or a flat-bottomed
  dot) sells "eyes" over "buttons" and kills the owl read. Procedural-cheap.
- Keep the warm veil-glow halo behind them but lower its peak a touch so the
  eyes don't bloom into one fuzzy mass at 32px — at small scale two close hot
  dots must stay TWO dots, not merge.

## KEEP (do not regress)
- The concave bell flare and floor-shadow root — reads as hanging silk, never a
  cone. The whole point of the concept.
- Gold hem band at the floor: it anchors the bell at 32px and gives the warm
  mass its value-contrast. Working.
- Gold-on-red value hierarchy generally; the night-lift `GOLD_BR` choice keeps
  the crown popping on the dark-blue night chip.
- Jade hairpin is correctly a literal sliver — lineage tell present without
  becoming a second hue mass. Good restraint.
- Pillar mirror: round wedding-lantern cap + silk-band/medallion shaft is
  grounded in the creature's own forms and is genuinely NOT top-heavy. The
  lantern reads at the 32px cap chip. Clean.
- No bone shown anywhere — cross-set rule respected.

## FIX (prioritized punch list)
1. **Dead-eyes** — apply the full ruling above (shrink ~30%, pull closer to
   ~`6.5*s` spacing, slight flatten, lower glow peak). #1 priority; it's the
   cute-vs-dread dial for the whole piece.
2. **Crown-arc footprint vs top-heavy** — the fengguan at `int(58*s)` wide with
   temple-dangle strings reaching down to `base_y + 26*s` is the widest mass on
   the figure and the dangles add visual weight at the temples. At 32px it's on
   the edge of crowning a top-heavy read. Either narrow the arc ~8-10% OR pull
   the phoenix-drop strings tighter to the temple axis so the head silhouette
   stays a clean dome, not a widening fan. The brief's "no top-heavy cap" is
   about the pillar (which is fine) — but keep the HERO head from going
   pagoda-wide too.
3. **Veil weave + beaded gold fringe at 32px** — the vertical thread lines
   (`VEIL_D` 1px) and the row of `int(1.8*s)` gold fringe beads turn to noise /
   a muddy band at true 32px. At hero scale they're lovely; at gameplay scale
   they dirty the clean veil panel and compete with the eye-dots. Suppress or
   coarsen the weave below a scale threshold (fewer, fatter threads) and reduce
   the fringe to 3-4 beads max so it stays a crisp gold lower-edge, not a
   stipple.
4. **Veil vs robe value separation** — `VEIL (182,26,34)` over `ROBE
   (206,34,40)` is a subtle deepening; good for not splitting the red mass, but
   at 32px the square veil can lose its edge against the shoulders. Add a 1px
   ink keyline along the veil's BOTTOM edge (you have the gold fringe there, but
   confirm an ink seam under it) so the square stays a crisp square — the
   square-under-crown tell depends on that hard bottom edge reading.
5. **Bound silk hands** — at hero scale they read; at 32px the cream block + 3
   gold cord lines risks reading as a second bright spot competing with the
   hem. Fine to keep, but slightly reduce the cream value or shrink the clasp so
   the eye still goes crown → eyes → hem first. Verify on the 32px chip after
   the eye fix.
6. **Pillar medallion glyph density** — the 囍 glyph (two uprights + two
   crossbars + center red) is busy inside an `int(11*s)` medallion; at the 32px
   pillar cap it muddies. Simplify the shaft medallions to a bolder, lower-detail
   gold disc + a single bold cross-stroke at small scale; reserve the full glyph
   for the lantern cap only where there's room. Keeps the shaft a clean tileable
   band.

## Cross-set check (PASS, hold the line)
- Warmest mass in the set: YES, owned. Do not let the veil/robe deepening creep
  cooler — stay vermilion-warm.
- Gold value-contrast carrying the read: YES. Keep `GOLD_BR` for night-lift.
- No bone, jade a sliver: PASS.
- Distinct from Catrina (couture wide-brim, visible face) and Yurei (hair
  curtains, legless wisp): PASS — rooted hidden-face bell is its own silhouette.

## Accessibility
Read does not rely on hue alone: the SQUARE veil shape + gold crown-arc + gold
hem carry it for colorblind players, and gold-on-red is a strong value contrast.
After the eye-shrink, double-check the two dots still read as two (not merged)
at 32px in a colorblind sim — that's the one element that's hue+glow dependent.

## Next-round target
Land the eye ruling, rein the crown width / dangles, and clean the veil-weave +
medallion noise at 32px. Hit those and this is ship-ready.
