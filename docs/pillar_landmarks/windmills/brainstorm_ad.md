VERDICT: SHIP-READY

# Windmill Family — Brainstorm Critique (art-director, Phase A)

Five locked, two culled. This is a strong, genuinely spread brainstorm — the
material discipline (real `pillar_pagodas.py` helpers, `_mix` retints, no raw
RGB) already puts the whole family at the pagoda fidelity bar, and the Blackout
strip proves six of seven bodies are distinct KINDS. The cull is not about weak
craft; it is about the ONE gate the brief makes non-negotiable: **"windmill" must
read at a glance at ~58px.** Two directions fail that gate and nothing else in
the set does, so they go, and the surviving quintet needs no replacement — it
already covers the interesting space with maximum mechanism + silhouette spread.

## Ranking (all 7, best → worst as a DIRECTION)

1. **`pavilion-mill`** — the single clearest "this spins in the wind" read in the
   set; a tiered pagoda wearing a saltire is instantly a temple AND instantly a
   mill. Anchor of the family. PURSUE.
2. **`shoji-rose-mill`** — the only light-emitter; a centred glowing paper coin
   at the gap is a night-biome showpiece and a totally different sensation from
   the others. PURSUE.
3. **`junk-sail-mill`** — the boldest, most original silhouette (only open-lattice
   body, only upright-comb mechanism); highest ceiling, with one real fill risk
   to police. PURSUE.
4. **`waterwheel-mill`** — an unambiguous mill mechanism on a heavy conical
   masonry body; the off-axis wheel is a distinctness asset, not a liability.
   PURSUE.
5. **`mani-drum-tower`** — the only rounded, bulging body-as-mechanism pole;
   moderate mill-tell, saved by the top vane. Weakest survivor but earns its slot
   on silhouette uniqueness. PURSUE.
6. **`prayer-flag-tower`** — beautiful austere body, but the catenary is the
   weakest mechanism-tell in the set: soft sagging bunting reads as *festival
   decoration / wires*, not a mill, and thin catenary arcs are the first thing to
   vanish at 58px. Mirror-fragile too (per-section redraw needed just to keep the
   sag pointing right). CULL.
7. **`windcatcher-tower`** — self-defeating for this brief: it has NO moving part,
   so it cannot say "mill," and a ruler-straight square slab + slotted crown is
   the silhouette CLOSEST to a plain shipped pagoda/tower. Cover the label and it
   reads "temple," not "windmill." CULL.

## The 5 to pursue — one distinct pole each

The quintet is maximally distinct because every one differs SIMULTANEOUSLY on
concept, blackout silhouette, construction, and shape language — and, critically,
**every survivor carries an obvious moving mechanism**, so all five clear the
glance-read gate that 6 and 7 fail:

| # | Slug | BODY pole (blackout) | MECHANISM pole | Shape language |
|---|------|----------------------|----------------|----------------|
| 1 | `pavilion-mill` | stepped tiered pavilion | thin OPEN radial sail-X (air between arms) | stepped-roofed rhythm crossed by hard diagonals |
| 2 | `waterwheel-mill` | battered BRICK CONE | ONE off-axis solid WOODEN wheel on a flank | heavy conical masonry + one asymmetric bulge |
| 3 | `mani-drum-tower` | fat ROUNDED drum cylinder | stacked rotating drums (body IS the mechanism) + top vane | rounded, ribbed, bulging |
| 4 | `shoji-rose-mill` | flat plaster SLAB | ONE centred FILLED GLOWING paper disc | flat slab crossed by a single luminous circle |
| 5 | `junk-sail-mill` | open bamboo LATTICE CAGE | ring of UPRIGHT battened junk sails (vertical comb) | airy, angular, open trellis under a slatted fringe |

Swap test passes: no mechanism is transplantable between two of them. Blackout
passes: pavilion / cone / cylinder / slab / cage are five different solid shapes.
Cover-the-label passes: each is nameable from its gap-end termination alone.

### Set-level FIX — the ONE thing to police in round 1
**Three of five mechanisms are circular/radial (X, wheel, disc).** This is the
tightest cluster in the set and the only place the quintet can collapse. It is
acceptable BECAUSE #3 (vertical drum stack) and #5 (vertical comb) break the
circle, and because the three circles are pinned on three independent axes — but
every round-1 render must protect those pins:
- **#1 X = OPEN + THIN** (radiating diagonal limbs with visible air). If it fills, it becomes #4. If it drops an arm, it becomes #2.
- **#2 wheel = OFF-AXIS + WOODEN + SPOKED + NEVER glows** (asymmetric, half in one gutter).
- **#4 disc = CENTRED + FILLED + GLOWING** (symmetric on-axis; the amber emission is its unique tell — lean into it hard so it never reads as a pale coin or as #1's open X).

## KEEP + FIX per survivor (fold into round 1)

**1. `pavilion-mill` — KEEP:** the strongest family anchor; stepped eaves +
diagonal limbs is unmistakably "temple that spins." **FIX:** at 58px four thin
lattice arms risk turning to noise — render the X as 4 clean arms max, each a
single readable canvas leaf + stock (not a busy ladder of whiskers); let the
sunward pair sit a half-stop brighter so the cross has depth, not four identical
sticks. Confirm the hub is dead-centred so the mirrored ceiling half keeps a
legible X.

**2. `waterwheel-mill` — KEEP:** unambiguous mill mechanism; off-axis wheel is
the distinctness win, and vertical flip preserves its left/right placement so the
mirror is clean. **FIX:** (a) guard against the wheel reading as a ship's-wheel /
gear at scale — keep clear paddle-BOARDS between twin rims (a paddled water-wheel
silhouette), not bare spokes; (b) cap the batter so the cone shoulder stays ≥0.72w
and the body still fills the ~58px column where the wheel overhangs the gutter;
(c) draw the launder/splash per-section so water always falls toward the gap on
both halves.

**3. `mani-drum-tower` — KEEP:** the only rounded body pole; the anti-sail idea
is a genuine concept, not a recolor. **FIX:** this is the weakest mill-tell of the
survivors — drums can read as a stack of pots/lanterns. Make the **top fantail
cross-vane larger and unmistakable** as the wind-catching cue, and give the drums
a clear rotation tell (banded specular sweep / slight motion hint) so the stack
reads as *turning*, not static barrels. Keep the vane centred for a clean flip.

**4. `shoji-rose-mill` — KEEP:** the night showpiece and the only emitter — a huge
identity asset. **FIX:** push the amber back-glow so the disc is a distinct
sensation from #1/#2 in ALL biomes, and verify it reads by DAY too (when the glow
is subtle) via strong mullion-rib structure and a value contrast against a bright
day sky — don't let it flatten into a pale coin. Keep the disc filled and on-axis
(never let the panels open into an X).

**5. `junk-sail-mill` — KEEP:** the most original, boldest silhouette; worth the
risk. **FIX (highest feasibility risk in the set):** an open lattice body must NOT
leave a gutter-visible empty band >12px in the ~58px collision column. Prove the
solid `_plaster` milling-floor band + `_gradient_rect` core posts keep the column
visually filled top-to-bottom at short heights AND that the cage still reads as
open/airy against busy skies (the lattice must not disappear into a day sky nor
turn to noise). Keep the shaft centred + battens horizontal for a clean flip.

## The 2 culls — why, and whether a gap opens

- **CULL `prayer-flag-tower` (#6):** weakest mechanism-tell (catenary reads as
  decoration, not a mill), first to vanish at 58px, mirror-fragile. Its body pole
  (steep white battered trapezoid) is the only thing lost — and it is covered:
  #2's brick cone holds the "heavy battered/tapered masonry" reading, and #4's
  plaster slab holds the "pale/white plaster body" reading. **No gap; no
  replacement needed.**
- **CULL `windcatcher-tower` (#7):** no moving part = fails the glance-read gate
  outright, and its straight square slab is the silhouette nearest a plain shipped
  pagoda — least differentiated from what already ships. Its body pole (tall
  straight square) is the least valuable to lose precisely because it reads as
  "tower," not "mill." **No gap; no replacement needed.**

I am deliberately NOT back-filling to seven. Five clean, obviously-a-mill,
maximally-spread directions beat seven where two whisper. If the user later wants
a sixth non-radial mechanism to further break the three-circle cluster, the best
*future* candidate would be a **horizontal bank of tilting louver-shutter vanes**
(a persiana/shutter-mill on a slab) — a new mechanism pole, not a rescue of #6/#7
— but it is not needed to lock this set.

---

Set locked: proceed to per-concept maturation loops.
