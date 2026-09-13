VERDICT: ITERATE

# Pazul — round 1 critique (boss sprite sheet)

Reviewed: `docs/skybit_devil/batch2/pazul/round_1.png` against the locked
Pazul brief in `docs/skybit_devil/batch2/brainstorm_locked15.md`
(turquoise-wings-PROMINENT pin; double-deck wings + over-the-head scorpion
sting silhouette; desert-ochre/turquoise palette; scary-CUTE; sting-spear
mirror).

This is a strong, on-grammar first pass — the head, snarl, ochre triad, and
the sting-spear pillar all land. But it MISSES the single hardest pin on the
whole brief, so it cannot ship as-is.

## Strongest / weakest
- **Strongest:** the head. Square canine-lion muzzle, hard square snarl with
  tiny up-fangs, amber slit-eyes, the flat ochre triad (dark-core → fill →
  top-left sheen) is textbook house style and reads scary-CUTE at every scale.
  The sting-spear pillar panel (b) is clean, slim, symmetric, with the
  venom-bulb cap + lime drip — mirror discipline is correct, no top-heavy risk.
- **Weakest:** the turquoise WINGS. They are the headline pin of this concept
  and they currently fail it — they read as ragged, low-mass slivers tucked
  BEHIND the torso, not as the two largest non-body masses. This is the
  make-or-break fix.

## CRITICAL — the turquoise-wing pin is not met (palette + silhouette + 32px)
The brief pins turquoise `(64,176,168)` as "the two LARGEST non-body masses …
must NOT shrink to a sliver." In the render the ochre body is ~60-70% of the
visual mass; the wings are thin, torn-edged fins poking out sideways from
behind the torso. At 32px (panel c) and grayscale (the value tell) the wings
nearly vanish into a frayed dark fringe — the cool counterweight is GONE and
the creature reads as a solid ochre block. Fixes, in order:

1. **Bring wings FORWARD and enlarge them.** Move both wing pairs in front of
   the shoulder line (front-facing membranes per the brief), and grow each
   membrane so the four panels together rival the torso in area. Target: at
   32px the turquoise should be the first cool note your eye catches, framing
   the body left and right — not hiding behind it.
2. **Solidify the membrane shape.** Right now the wing edges are noisy/torn and
   the internal struts chop the turquoise into thin shards (it turns to noise at
   1×). Make each membrane ONE bold faceted flat shape with a single clean
   keyline, 2-3 internal vane struts MAX, triad-lit (dark turquoise core →
   `(64,176,168)` fill → cool sheen). Hard faceted panels, not feathered fringe.
3. **Double-deck must read as TWO pairs.** Currently the stacking is muddy — it
   looks like one tattered pair. Stagger an upper (larger) and lower (smaller)
   pair with a clear value/overlap step between decks so the "double-deck" read
   — the one thing no sibling has — survives at 32px.

## House-style / palette
- KEEP the ink keyline weight, the flat saturated ochre fills, and the
  dark-core/fill/sheen triad on the body — all correct.
- The ochre `(206,158,84)` body looks on-pin. **Sibling-drift watch:** this
  broad ochre must stay clearly distinct from Cernun's torc-gold (which is a
  THIN throat-ring accent only). Pazul owns ochre as a BODY fill; that's fine —
  just keep the value a touch warmer/darker than any gold accent so they don't
  converge. No action needed this round beyond not lightening the hide.
- Lime sting-glow `(176,224,72)` is present on the spear cap but barely on the
  creature's own tail tip. Push a small venom-lime glow node onto the
  over-the-head bulb-sting so the warm-ochre/cool-turquoise/acid-lime triangle
  reads on the hero too, not just the pillar.

## Silhouette / 32px read
- The over-the-head scorpion sting is the other signature blob and it is too
  TIMID. In panel (a) the tail bulb sits low and to the side, half-lost among
  the shoulder lumps; the grayscale read does not show a clear sting arcing UP
  over the head. Raise the tail so the bulb-sting clears the skull crown and
  hooks forward — the "stinger over the head" should be unmistakable in
  silhouette alone.
- The shoulder area is cluttered (multiple round lumps + the sting bulb compete
  near the head). Simplify: let the sting bulb be the ONE dominant round mass up
  top; reduce the secondary shoulder spheres so they don't read as extra heads.

## Scary-CUTE / appeal
- Menace and charm are well balanced — the snarl + slit-eyes are mean, the
  chibi proportions keep it likable. No notes; preserve this.

## Accessibility
- Once the wings are enlarged + solidified, the warm-body / cool-wing VALUE
  split will also carry the read for colorblind players. Right now the
  grayscale shows almost no value separation between wing and dark background —
  fixing the mass (above) fixes this too. Aim for the wings to sit a clear value
  step apart from both the ochre body and the sky.

## Prioritized punch list for round 2
1. Enlarge turquoise wings to rival the body mass and bring them FORWARD of the
   torso — they must be the two largest non-body masses (HARD PIN).
2. Re-shape each membrane as one bold faceted flat panel, clean keyline, ≤3
   struts — kill the torn/feathered fringe that turns to noise at 1×.
3. Make the double-deck read explicit: staggered upper/lower pairs with a clear
   overlap step.
4. Raise the scorpion sting so the bulb clearly arcs UP over the head in
   silhouette; declutter the shoulder lumps so the sting bulb is the lone top
   mass.
5. Add a small venom-lime glow on the creature's own sting tip (echo the pillar
   cap).
6. Hold the body ochre value where it is — do not let it drift toward
   Cernun's torc-gold.

When the wings carry their pinned mass and the sting clears the head, this is
ship-track. The foundation (head, triad, pillar) is already right.
