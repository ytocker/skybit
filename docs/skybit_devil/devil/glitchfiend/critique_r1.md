# GLITCHFIEND (B6) — round 1 critique

VERDICT: ITERATE

A genuinely promising silhouette and a strong head — this is recognizably
the neon synthwave devil, sharp and distinct from the other nine, with no
ram-horn or warm-flame collision. But it fails its own headline guardrail in
two of the four diagnostic cells you wisely put on the sheet: (1) the DAY 1x
read collapses into a pink blob, and (2) the grayscale-with-glow-stripped read
is a flat mid-value mess, not a hard near-black silhouette. The whole pitch of
this concept is "glow is an ACCENT over a void body that carries the read on
its own." Right now glow IS the construction. That is the thing to fix before
anything else. The good news: the geometry is right; this is a value/contrast
and glow-restraint problem, not a redesign.

## Strongest aspect
The HEAD at showcase scale. The hexagonal faceted plate, the swept laser-blade
horns, the cyan brow-cross grid, and the laser-yellow narrowed eyes read
instantly as a cocky tech devil. Distinct, on-brief, charming. The angular
shape language is correct and nothing here reads as any of the other devils.

## Weakest aspect
VALUE STRUCTURE. The "near-black void body" promise is not kept where it
matters. On the bright day sky the body reads as solid hot-pink/magenta with
no dark anchor, and in grayscale the body is a uniform mid-gray crossed by
near-white gridlines — there is no dominant dark mass, so the silhouette does
not survive glow-strip. This is the single guardrail this concept exists to
prove, and round 1 does not pass it.

## KEEP
- The head construction (hex plate + swept laser horns + brow grid + yellow
  eyes). It is the concept's anchor — do not touch the geometry.
- The chevron-fin collar crest and the chevron torso silhouette — sharp,
  tech, distinct mass-language.
- The forked-lightning-bolt tail — reads as a glitch spade, clever and clean.
- The light-trident PROP at showcase scale — the three tines + caught orb read
  well and the up/down mirror geometry is correct.
- Palette discipline: electric magenta/cyan only, no warm gold, no green. The
  laser-yellow eyes are the right single warm note. No collision with Baalgoat
  or Pyrecrown. Hold this exactly.

## FIX (ranked, specific)

1. **DAY-SKY READ FAILS — the body washes to a pink blob.** At 1x on the
   light-blue day sky the magenta facet fills + bloomed cyan gridlines fuse
   into one bright pink mass; the angular silhouette is lost. Root cause: the
   magenta fill covers ~70% of the visible body and the void is almost never
   seen. Push the VOID to be the dominant value — let near-black `(18,14,30)`
   read as the body and confine `MAGENTA` to ~30-40% accent planes on the
   LIT side only. The right side should stay genuinely dark. Target: on the
   day sky the figure should read as a dark angular devil with neon piping,
   the same way it reads on night.

2. **GRAYSCALE READ FAILS — no dark anchor, flat mid-values.** With glow
   stripped the body is uniform mid-gray + near-white lines. There is no value
   hierarchy. Re-cast the triad so there are three CLEAR grayscale steps:
   void (near-black, dominant), magenta fill (mid), neon edge (bright, thin).
   The grayscale panel should look like a near-black devil-shape with a few
   bright filaments — if you squint and it's still a clear devil silhouette,
   you've passed. Right now it isn't.

3. **GRID BANDS HAVE BLOOMED INTO A WASH.** The cyan brow/torso scan-bands and
   especially the rod bands are blooming and multiplying at 1x — exactly the
   "soft blurry cloud" the spec forbids. Cut the glow radius and steepen the
   falloff further, and REDUCE the number of gridlines (the torso has too many
   horizontal bands stacking into noise at 1x). Fewer, bolder, crisper bands
   that survive smoothscale as discrete lines, not a haze.

4. **THE PILLAR ROD READS AS A WHITE STICK, NOT A NEON CONDUIT.** At true
   obstacle width the rod is a pale near-white post with faint thin bands — it
   reads like a thermometer, and its value is identical to the boss's bright
   highlights so there's no figure/pillar distinction. Make the rod a clearly
   DARK post (void-dominant) with magenta rail-tubes and 3-4 BOLD cyan bands
   that pulse. It must read as a dark glowing conduit, not white plastic. Same
   void-first fix as the body.

5. **THE PRONGS ARE SPIDERY AT 1X.** The three energy tines at obstacle scale
   are thin pale legs with little glow; they don't read as a trident cap. Make
   the tines thicker / shorter, push the caught orb brighter and larger as the
   focal point, and let the prongs splay with more conviction so the cap silhouette
   is unmistakable as a fork against the gap.

6. **THE GLITCH-DOUBLED HORN DOESN'T REGISTER.** The signature scary-cute beat
   (buggy hologram) is invisible at showcase and 1x. Either commit to it
   harder — a clear, readable cyan ghost-offset of the whole horn (not just a
   faint edge) — or move the glitch to a more readable spot (e.g. a doubled
   eye or a sliced scan-offset across the head). It needs to read as
   intentional glitch, not a rendering smudge.

7. **THE GRIN IS WEAK.** The zig-zag smirk gets lost between the chin facet and
   the under-jaw. Raise its contrast and simplify to a bolder, fewer-segment
   neon zig with one clearly cocked-up corner so the "cocky arcade" attitude
   lands at 1x. Right now the eyes carry all the personality.

## Distinctness / identity — PASS
Sharp laser horns (no ram), electric palette (no warm torch, no green
soul-fire), angular geometric body — clearly the only neon/tech devil and
clearly separable from B1's iron pitchfork (this is glow geometry). No roster
collision. Keep all of this; the fixes above are about legibility, not
identity.

## Top 3 directives (do these first)
1. Flip the value hierarchy: VOID near-black becomes the dominant body value;
   magenta drops to a ~30-40% lit-side accent — so the silhouette survives on
   the DAY sky and in grayscale.
2. Tame the glow: smaller radius, steeper falloff, FEWER gridlines — crisp
   discrete neon filaments, not a bloomed pink/cyan wash.
3. Rebuild the pillar rod as a DARK void post with bold magenta rails + 3-4
   bold cyan bands (not a pale white stick), and beef up the prong cap so the
   trident reads at 82px.
