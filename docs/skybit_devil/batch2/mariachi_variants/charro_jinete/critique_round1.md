VERDICT: ITERATE

# El Charro Jinete — round 1 critique (lead facet: BLEND)

The large-render concept is genuinely charming and the palette discipline is
real — but the design FAILS at the only size that matters. At 32px the two
bodies collapse into one ambiguous brown-grey blob; the rearing-horse + rider
read does not survive, which means the grand-boss KIND that justifies this
entry isn't landing yet. Strong foundation, wrong outcome at gameplay scale.

## Strongest aspects (KEEP)
- **Palette pin nailed.** Rust at `(176,70,56)` sits convincingly in the
  desaturated brick/leather lane — clearly browner/darker than B's orange-chile
  and E's pink-rose. The three-swatch split panel proves it. Hold this exactly.
- **House triad on the large render.** Dark-core → flat-fill → top-left
  rim-sheen is clean; the embroidered jacket botonadura dots, marigold browband,
  and turquoise zarape stripe all read as on-style decoration, not noise.
- **Scary-CUTE balance.** The big-skull mount + tiny rider is friendly, not
  grim. Good.
- **Prop → pillar mirror is correct.** The slim lance shaft + compact on-axis
  horse-skull finial stays single-mass and symmetric — no top-heavy double-mass.
  The two-body prop risk is resolved. Leave the pillar essentially as-is.

## Weakest aspect — the 32px multi-body read (CRITICAL, the whole ballgame)
- **Two bodies fuse into one mass.** At 32px the horse barrel, the rider, and
  the rearing forelegs merge into a single dark lump. The "rearing horse + rider"
  silhouette — the entire reason this is the grand-boss KIND — is illegible. The
  @4x crop confirms it: a viewer can't separate mount from rider, and the raised
  sombrero arm (the motion tell) disappears into the head cluster.
- **The silhouette 32px (the black-shape panel) is actually clearer than the
  full-color 32px** — which tells you the INTERNAL value structure is fighting
  you: too many same-value brown/bone fills adjacent with no separating dark gap.
- **No air between the masses.** The rider sits flush on the spine with no ink
  channel between rider-pelvis and horse-back, so they read as one vertical bone
  smear rather than "something riding something."
- **Too much incident detail at scale.** Ribcage banding on BOTH bodies, jacket
  buttons, zarape stripes, browband — all of it turns to dither mush at 32px and
  steals the contrast budget the two-body separation needs.

## Iteration directives (prioritized punch list)
1. **Buy separation with a dark channel.** Insert a 1–2px ink gap (at 32px)
   between rider-mass and horse-back so the stacked-body read is forced by
   negative space, not by color. This is the single most important fix — if only
   one thing changes, change this.
2. **Simplify the 32px target deliberately, don't just downscale the 160px.**
   The horse needs to read as: arched-neck + skull-muzzle pointing up-left,
   barrel, two planted hind legs, two pawing forelegs. Reduce to ~3 leg shapes
   that read, drop the ribcage banding entirely at 32px (let the barrel be one
   bone mass with a single dark-core trough).
3. **Push the rearing diagonal harder.** Right now the horse is too upright/
   compact, so it reads as a lumpy quadruped, not a REAR. Steepen the neck-to-
   foreleg diagonal (~30–40° lean) and lift the forelegs clearly off the
   baseline so the rear is unmistakable in the black silhouette.
4. **Make the raised-sombrero arm a hard silhouette spike.** The motion facet
   must survive at 32px — the rider's up-thrust hat should break the outline as a
   distinct lollipop (thin arm + disc), separated from the skull by sky, not
   buried beside the head. It currently vanishes.
5. **Cut the rider's internal detail at scale.** At 32px the rider is ~6–8px
   tall — it can only afford a skull dot, a torso block, and the raised-arm
   spike. Kill the jacket buttons and reins at 32px; keep them only on the 160px.
6. **Re-balance the barrel value.** The horse body currently sits mid-tan/bone
   and the rider also reads bone — give the horse barrel a slightly deeper
   tan-shade core so the lighter rider pops off it. Value contrast between the two
   bodies (~15–20%) is what sells "rider on mount."
7. **Verify against day AND night sky.** Only the ochre-day crop is shown. The
   brick-rust zarape on a night biome could go muddy — add a night-sky 32px crop
   next round and confirm the bone bodies still carry the read.

## Distinctness check (PASS, conditional on the 32px fix)
- Distinct from the four siblings on KIND: it is the only multi-body /
  rearing-horse silhouette — no overlap with B's pear, D's paper rectangle,
  E's swept skirt, or G's head-back laugh. Good.
- Distinct from shipped batch-1 reapers: warm Mariachi palette + charro
  decoration + horse KIND keep it well clear of the cool grim cranium reapers.
- BUT distinctness is only real if the two-body read survives at 32px. Right now
  the silhouette is unique on paper and mush in practice — fix #1–#4 are what
  actually earn the KIND.

Re-roll not warranted: the concept, palette, and prop are right. This is a
focused legibility pass on the 32px master, not a rethink.
