VERDICT: SHIP-READY

# Pillar Landmarks — Brainstorm Critique (art-director, Phase A)

The set is strong: six genuinely-conceived KINDS, each with a real
silhouette-tell and a credible column-fill story. It does NOT yield six
distinct-enough towers — three of them cluster on the "straight-sided vertical
that ends in a point or a hard crown," which is also the pole the 11 shipped
pagodas already own. But it cleanly yields **3 maximally-distinct, high-juice,
feasible towers**, so the brainstorm locks. Proceed to mature the trio below.

The winning move is to pick the three concepts that are LEAST like the shipped
pagodas and MOST unlike each other — and to deliberately drop the entire
rectilinear/point-terminated cluster, because that cluster is where every
internal collision lives AND where the roster is already crowded. Adding
another tall straight tower would be the weakest possible portfolio choice
even if each one is individually fine.

---

## Ranking (all 6)

1. **`smock-windmill`** — Uncontested pole. The only radiating-diagonal
   silhouette and the only steeply-battered squat cone; collides with nothing
   internal or shipped. Highest structural originality in the set. **PURSUE.**
2. **`moai-monolith`** — Uncontested pole. The only organic bulbous stacked-
   ovoid body; the brow/nose bumps break the outline in a way no shipped shape
   does (cairn = smooth pebbles, `stone_face` = one tiny dressing face). High
   charm, silhouette-carried read. **PURSUE.**
3. **`harbor-lighthouse`** — The only smooth curved-side taper anywhere in the
   roster (pagodas, bones, menhir are all angular/lumpy), and the only concept
   with a glowing focal (the lantern room) — genuine day/night juice. Best
   column-fill story in the set (head-at-gap = most-filled exactly where it
   matters). **PURSUE.**
4. **`battlement-keep`** — Strong, characterful fortress pole, and the cleanest
   of the three geometric towers to keep (a flat toothed crown is the most
   un-pagoda-like of the geometric tops). But its jagged crown soft-collides
   with moai's lumpy top-edge at 58px, and it's the third straight block.
   **CULL — first alternate.**
5. **`civic-clocktower`** — Individually the most "finished" idea, but it is the
   double-collision hub: it shares point-termination with the obelisk AND
   straight-block-body with the keep, and its signature (clock disc, arched
   louvers) is exactly the detail that dies at 58px. Closest of all six to the
   shipped pagoda idiom. **CULL.**
6. **`sunspire-obelisk`** — Lowest juice: an austere featureless wedge. Collides
   with the lighthouse (taper) and the clocktower (point), and sits nearest the
   shipped menhir. A near-triangle is the least memorable thing you can add.
   **CULL.**

---

## The 3 to pursue — silhouette poles

| Slug | Pole | Blackout shape | Tip at the gap |
|---|---|---|---|
| `harbor-lighthouse` | soft / smooth-curved-taper | bottle: narrow head over swelling round shaft | round dome |
| `smock-windmill` | hard / radial-diagonal battered cone | squat cone throwing an X | sail-hub cap |
| `moai-monolith` | organic / bulbous stacked ovoids | knobbly stack of heads | lumpy pukao cylinder |

**Why the trio is maximally distinct — four tests:**
- **Blackout:** bottle-with-head vs battered-cone-with-X vs lumpy-egg-stack —
  three unmistakable solid-black shapes, no shared mass. PASS.
- **Swap:** you cannot reskin one into another — horizontal candy bands, a
  single battered trapezoid + lattice arms, and a flush stack of carved ovoids
  are three different constructions/anatomies. PASS.
- **Cover-the-label (tips):** round dome / radial sail-hub / lumpy pukao — three
  different terminations, all readable at the gap. PASS.
- **One-sentence:** "a coastal light" / "a windmill" / "an ancestor stack" —
  three sentences with no shared noun. PASS.

Bonus: their gap-ends read oppositely — the lighthouse is WIDE at the gap
(head), the windmill is NARROW at the gap (hub), the moai is a capped bump.
That variety at the collision edge is exactly what keeps a scrolling field of
these from feeling samey.

---

## Per-concept KEEP + FIX (into round 1)

### `harbor-lighthouse`
- **KEEP:** the head-on-a-taper bottle silhouette; the lantern-room glow (route
  it through a cached radial like `draw_paper_lantern`, not per-pixel); candy
  bands driven by `stone_light`↔`stone_dark` VALUE (colorblind-safe, holds at
  night); head-at-gap fill logic.
- **FIX:**
  1. Guard the flared head/gallery against the ±64px gutter — the shoulder may
     spill into gutters as ornament but the collision column stays 58px; confirm
     the widest ring never implies a wider hitbox.
  2. Bands must alternate on VALUE, not hue — verify the light/dark delta
     survives the night palette (target ~25%+ value separation at 1x).
  3. Astragal bars in the lantern room will turn to noise at 58px — cap to 3–4
     bold verticals max, or let the glow carry it and drop the bars.
  4. Keep the taper a true smooth CURVE (per your own pin) — the moment the
     sides go dead-straight it becomes the obelisk you're culling.

### `smock-windmill`
- **KEEP:** the battered squat trapezoid (ground-heavy, unique); the 4-blade
  sail X as the identity; sails-as-gutter-ornament-over-a-solid-core fill logic.
- **FIX:**
  1. **Gap clutter is the real risk.** Mirrored, both sections point their hub
     at the gap — angle the sail arms so the X fans OUTWARD/sideways into the
     gutters and leaves the gap visually clean; the sails must never read as
     bridging or obstructing the flyable gap.
  2. Sails at 58px: a fine lattice ladder will vanish/alias. Make each arm a
     bold solid-ish stroke with only 2–3 rung ticks — the X must read as four
     confident bars, not filigree.
  3. Weatherboard seams: keep them sparse (a few string-courses), or they
     stipple into noise on a dark matte body against a busy sky.

### `moai-monolith`
- **KEEP:** the height-adaptive head-count (1 big head at 70px, a stack tall);
  brow/nose breaking the outline as the silhouette-carried tell (does not rely
  on interior detail surviving 58px); red pukao accent as the focal; full-width
  flush stacking for zero killzone.
- **FIX:**
  1. **Resolve the mirror now.** An inverted stack of upside-down faces can read
     creepy rather than charming. Decide: either hang the top section as heads
     that still face "up" (rooted at the ceiling) or lean fully into a symmetric
     totem — pick the friendlier read and pin it, don't discover it in render.
  2. Interior face relief (eye sockets, chin) will mush at gameplay size — make
     sure the read survives on the OUTLINE alone; treat face carving as
     close-up reward, not the small-size identity.
  3. Distinctness pin vs the shipped `stone_face` dressing (a single tiny face
     on a stone) as well as the cairn — your tell is the STACK of outline-
     breaking heads; keep at least the brow+nose proud enough to separate it
     from a smooth cairn in blackout.

---

## The 3 culled + gap coverage

- **`civic-clocktower`** — double internal collision (point w/ obelisk, block
  w/ keep) and its signature detail dies small; nearest to shipped pagodas.
- **`sunspire-obelisk`** — lowest charm, collides on taper + point, nearest the
  shipped menhir; a featureless wedge is the least memorable add.
- **`battlement-keep`** — best of the three, but the third straight block and
  its toothed crown soft-collides with moai's lumpy top-edge.

**Gap left:** the crisp hard-rectilinear / geometric pole is unrepresented in
the trio. This is intentional and correct — the 11 pagodas already own tall-
vertical-architectural, so a fourth straight tower is the lowest-value add, and
all three culls live in that crowded zone. **If** the user later wants a hard-
geometric landmark, promote `battlement-keep` (NOT the clocktower/obelisk —
their points echo pagoda finials; the keep's flat toothed crown is the most
distinct geometric top), with a FIX to make its teeth crisp/regular/square
(machine-cut) so they can't be confused with moai's organic lumps.

---

## References
- Silhouette-first read at small size: same discipline your Songyue eave-count
  and chorten stepped-base already follow — key every repeated element off a
  natural step so it adapts in COUNT, never squashes.
- Value-not-hue banding for colorblind safety and night survival: benchmark the
  lighthouse stripes the way the coin rim-light and HUD hold value across biomes.
