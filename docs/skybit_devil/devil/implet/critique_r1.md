# IMPLET (B8 "pocket gremlin imp") — Round 1 critique

VERDICT: ITERATE

A strong, charming first pass. The showcase imp is genuinely delightful — the
huge orange eyes, snaggle-fang grin, cream belly and acid-green body land the
"scary-cute gremlin glee" beat instantly, and the distinctness firewall against
Grim Sprout is fully clear (no hood, no skull, pear body, devil bat-wings,
fire-trident, acid-green vs reaper violet). The blocking problem is that almost
NONE of that survives to 1x. At gameplay scale the wings, the imp, and the spear
collapse into an ambiguous dark wedge with a green dot — the figure loses its
read exactly where it has to keep it. That, plus a comedy-of-scale gag that
isn't yet firing and a couple of construction noise issues, is the iterate list.

## Strongest / weakest

- **Strongest:** the showcase face + palette. Acid-green body, orange eyes, cream
  belly, the tongue-tip and snaggle fang — pure gremlin charm, on-thesis, and
  100% distinct from every other pick and from the shipped reaper. House triad
  (dark-core / fill / sheen) is honored cleanly on the body and belly.
- **Weakest:** 1x legibility. At in-game scale the bat-wings read as a flat black
  mass that swallows the body, the imp shrinks to an unreadable lump, and the
  whole assembly (imp + wings + towering spear) becomes a tall vertical smudge
  rather than a winged figure. Look at the (c) DAY/NIGHT/B-W insets: the wings
  have no internal structure at 1x, the curl tail vanishes, and the silhouette
  anchor the renderer's own comments promise (`the 1x silhouette ANCHOR`) is not
  delivering.

## Per-lens KEEP / FIX

### 1. Readability & silhouette
- KEEP the bold orange-on-green eyes — they are the one feature that survives the
  shrink, and they carry the read. Good instinct making them the cute lever.
- FIX: the wings are the headline failure at 1x. In the showcase they're lovely
  (finger ribs, plum top-light, claw hooks), but every bit of that internal
  structure is sub-pixel at gameplay scale, so they read as one black blob with a
  green head stuck on it. The brainstorm guardrail said "give the wings a bold
  enough spread to anchor the read" — right intent, wrong execution: a finely
  detailed wing reads as NOISE-then-mush, not as an anchor. The anchor has to be
  the SHAPE of the wing pair (two bold scalloped membrane lobes with clear sky
  cutting between them and the body), not the rib detail. Open the negative space
  between wing and body so the green torso doesn't get eaten.
- FIX: the wings are too dark and too LARGE relative to the imp. Right now the
  black membrane out-masses the green body roughly 2:1 at 1x, so the silhouette
  reads "dark winged thing," not "tiny green imp WITH wings." Pull the wing reach
  in ~15-20% and lift the body's footprint so green is the dominant 1x value.

### 2. Appeal & charm
- KEEP the face entirely. The asymmetric eyes + fang + tongue are exactly right.
- FIX: the comedy-of-scale gag (the thesis: "can barely lift its own spear") is
  not reading. In the showcase the imp stands upright and relaxed with one arm
  casually raised — it looks like it's holding the spear comfortably, even
  pointing with it, not straining. Sell the gag: tip the imp's body/lean, bend
  both arms up overhead in a two-handed strain, maybe buckle one knee, and let
  the spear tilt so its weight visibly drags the wee body. Right now the joke is
  in the caption, not the picture.

### 3. Color
- KEEP the acid-green + orange-eye + cream-belly triad. Harmonious, high-chroma,
  on-brief, and distinct from Pyrecrown (this is a green BODY, not green flame —
  good).
- FIX: the wings' near-black `(32,26,34)` with plum accents reads as a value
  hole, not a hue. On the NIGHT panel the wing merges into the dark sky and the
  bottom of the figure dissolves. Either warm/lighten the wing membrane a notch
  (a desaturated plum-grey rather than near-black) OR lean harder on the grown
  outline to keep the wing edge crisp against night. The body green is fine on
  both skies; it's the wing that fails night.

### 4. Identity & consistency
- KEEP the construction approach — `_triad_circle`, grown outline, supersample.
  It sits in-style beside Grim Sprout and the parrot.
- No real fix here; this is house-faithful.

### 5. Distinctiveness (CRITICAL — PASS)
- Verified directly against shipped Grim Sprout R3: that is a violet HOODED blob
  with a curved SCYTHE; this is an acid-green PEAR with spread BAT-WINGS and a
  warm fire-TRIDENT. No collision — pear body, no hood, no skull, devil wings,
  fire-spear, acid-green. Single pointy horn-nub, no ram pair. Warm orange flame,
  not Pyrecrown's green soul-fire and not Glitchfiend's neon. All guardrails met.
- One watch-item, not a fail: the fire-fork tip is a THREE-prong trident shape.
  That's in-spec (the brainstorm calls it a "flame-fork" / "fire-spear"), but
  keep the prong read clearly FLAME (teardrop, licking, warm gradient of prongs)
  so it never converges with B1's iron 3-tine pitchfork or A3's bone fork at 1x.
  Right now the cap flame in the (b) pillar is good and flame-like; the small
  showcase tip is borderline reading as solid orange spikes — push the inner
  core/taper so it stays fire.

### 6. Feasibility (PASS)
- Fully procedural, imports real game helpers, no sprite-sheet thinking. Good.

### 7. Accessibility
- KEEP orange-on-green eyes — that contrast pairing is colorblind-safe and is the
  load-bearing feature.
- FIX: the figure currently relies on the black wing mass for its silhouette,
  which (per the B-W inset) collapses to a low-contrast grey lump on a mid-grey
  field — the face barely registers. Once the wing shape is bolder and the green
  body is the dominant value, re-check the B-W: the imp should read as imp on
  luminance alone.

### 8. Polish
- KEEP the iron banding collars on the shaft (good pillar-banding cue) and the
  clean flame core layering on the (b) cap.
- FIX: the curl tail with bead segments is a 1x noise risk — at gameplay scale
  it's a row of green dots that disappears or fuzzes. Simplify to a single bold
  S-curve stroke + the spade tip; the spade is the devil tell, the beads are not
  earning their pixels.
- FIX (pillar): the (b) pillar pair is clean and tiles well, BUT the flame-fork
  cap is quite large and a bit static. Verify the gap-edge flame doesn't crowd
  the playable gap at the real PIPE_W — and give the cap flame the same teardrop
  licking shape you'll use on the prop so the two stay one language.

## Prioritized iteration directives (next-round brief)

1. **Fix the 1x silhouette — the #1 blocker.** Make the wing PAIR read as a bold
   two-lobe shape with clear sky negative-space between wing and body; pull wing
   reach in ~15-20% and ensure the acid-green body is the DOMINANT value at 1x
   (not the black wing). The figure must read "tiny green winged imp" at the (c)
   insets, not "dark wedge with a green dot." Re-check on the B-W panel.
2. **Sell the comedy-of-scale gag.** Pose the imp visibly STRAINING under the
   too-big spear: both stubby arms up overhead, a body lean/knee-buckle, the
   spear tilted so its weight drags. The thesis is "can barely lift it" — put
   that in the picture, not the caption.
3. **De-noise the small details + lift the wing value for night.** Reduce the
   curl tail to one bold S-stroke + spade tip (drop the bead chain), and warm/
   lighten the wing membrane (or strengthen the outline) so the lower figure
   doesn't dissolve into the night sky. Keep the flame-fork reading as FLAME
   (teardrop taper) at both showcase and cap so it never collapses toward an
   iron/bone fork.

## References
- Compare to your own shipped Grim Sprout R3 (`docs/skybit_reaper/grim_sprout/round_3.png`)
  for how a tiny-imp-with-oversized-prop reads at 1x — note how its compact body
  keeps a clear colored mass even as the blade dwarfs it; Implet currently loses
  that because the wings out-value the body.
