# Sidewalk Overhaul — Living Promenade

The foreground sidewalk is no longer a loop of interchangeable props. It is a
**single Chinese-market street told as one continuous day's arc** — a
*day-arc director* (`game/foreground_promenade.py → draw_promenade`) that reads
the biome clock and stages the right cast, fixtures, crowd density and lighting
for that moment of the cycle.

Two signals drive everything:

| Signal | Source | Role |
| --- | --- | --- |
| `phase` | biome day-cycle position `0.0 → 1.0` | selects the cast + fixture vocabulary, the crowd-density curve, and the lighting |
| `t` (`biome_time`) | seconds since run-start | ramps the street **in from empty** as a run opens — the market "opening" (`_run_fill`, over the first **7 s**) |

One full day-cycle = **`CYCLE_SECONDS = 320 s`** of gameplay (`game/biome.py`).

All art is **procedural** (drawn from code — no sprite sheets) and **pygbag-safe**
(only `fill` / `blit` / `draw.*` / `SRCALPHA` / `BLEND_RGB_ADD`).

---

## 1. The element catalogue (new designs)

Each "family" is a pool of hand-drawn variants with a no-repeat placement rule,
so the on-screen street never reads as a short loop. Counts and drawers:

| Family | Designs | Drawer | Catalogue sheet | In-scene sheet |
| --- | --- | --- | --- | --- |
| **Pedestrians** | 50 adult walkers | `ped_cast._draw_one` | [pedestrians_designs](./showcase/pedestrians_designs.png) | [gameplay](./showcase/pedestrians_gameplay.png) |
| **Day-cast** | 19 — kids ×6, temple elders ×6, market vendors ×7 | `day_cast.draw_kid/draw_elder/draw_vendor` | [day_cast_designs](./showcase/day_cast_designs.png) | [gameplay](./showcase/day_cast_gameplay.png) |
| **Food stalls** | 5 — steamer / cauldron / grill / wok / tea | `food_stalls.STALLS` | [food_stalls_designs](./showcase/food_stalls_designs.png) | [gameplay](./showcase/food_stalls_gameplay.png) |
| **Animals** | 9 — 5 dog breeds + 4 street critters | `animals_cast.draw_dog/draw_critter` | [animals_designs](./showcase/animals_designs.png) | [gameplay](./showcase/animals_gameplay.png) |
| **Greenery** | 30 potted-plant designs | `greenery_cast.draw_greenery` | [greenery_designs](./showcase/greenery_designs.png) | [gameplay](./showcase/greenery_gameplay.png) |
| **Props / fixtures** | 15 across 5 pools — lamp / banner / fire / bench / dress | `props_cast.*` | [props_designs](./showcase/props_designs.png) | [gameplay](./showcase/props_gameplay.png) |
| **Performers** | 8 busker acts | `performers_cast.draw_act` | [performers_designs](./showcase/performers_designs.png) | [gameplay](./showcase/performers_gameplay.png) |
| **Festival specials** | 5 — lion dance, red dragon, jade dragon, banner pole, brazier | `foreground_promenade._near_*` / `perf_lion_dance` / `perf_dragon_dance` | [festival_designs](./showcase/festival_designs.png) | [gameplay](./showcase/festival_gameplay.png) |

> Greenery was expanded from 10 → **30** designs this round; the festival
> specials and the showcase gallery were added alongside. The 30-design pool is
> now planted as small **static cluster beds** standing directly on the sidewalk
> (a tall centre + short flanker, ±a low filler) rather than scattered lone pots —
> placed by `_ground_furniture` via `_draw_greenery_cluster`. Unlike the rest of
> the cast, the plants **hold their daytime colour the whole day-night cycle**
> (cluster passes `night=0`): `greenery_cast`'s night retint cooled the foliage
> to a muddy blue-green after dusk, which read worse than the clean day colour.

**Street fixtures (the "dressing")** are a separate layer from the cast: prayer-flag
bunting, the **lantern garland**, **fairy-light strings**, two rows of **lamp posts**,
planters/cairns and the kiosk. These are placed by `_dressing` / `_ground_furniture`.

---

## 2. Time-of-day strategy — the day arc

The director walks the street through six beats per cycle. `phase` is taken
`mod 1.0`; the windows below are the `_roster_for` / `_dressing` gates.

| Phase window | Beat | Cast roster | Crowd | Fixtures up | Lighting |
| --- | --- | --- | --- | --- | --- |
| `0.00 – 0.14` | **DAY — food-market rush** (the run opener) | grill, soup, market, steamer, tea, dawn-setup, vendor | **peak ≈ 0.85** | bunting, garland, fairy | unlit shells (day floor on strings) |
| `0.14 – 0.25` | **Calm late morning** | pastoral, vendor, quiet, stroll | ~0.26 | bunting (to 0.28), garland, fairy | unlit |
| `0.25 – 0.40` | **GOLDEN — afternoon stroll** | stroll, pastoral, quiet, bench | ~0.24 lull | lamp posts up (from 0.20), garland, fairy | strings lit a touch; lamps still dark |
| `0.40 – 0.58` | **DUSK — lamps lighting** | **lamplighter**, stroll, bench, rest | 0.30 → ramp | lamps, garland, fairy | lamps *just kindling* (`_lit_intensity ≈ 0.40`) |
| `0.58 – 0.80` | **NIGHT — festival PEAK** | campfire, grill, soup, stroll, bench (+ festival specials) | **1.00 peak ≈ 0.66** | lamps, garland, fairy, braziers | full glow, capped under the coin |
| `0.80 – 0.85` | **PRE-DAWN teardown** | quiet, rest | **≈ 0.06** near-empty | lamps (to 0.93), garland, fairy | fading out |
| `0.85 – 1.00` | **SUNRISE — first vendors return** | pastoral, vendor, quiet, stroll | 0.22 → 0.58 | bunting returns (≥0.85) | back to day |

**Crowd-density curve** (`_POP_KEYS`) is the heartbeat of the arc — busy at the
morning market, a golden-hour lull, the night-festival spike, then a near-empty
pre-dawn:

```
0.00 .58 │ run-start, market already opening
0.06 .85 │ ███████  FOOD-MARKET peak
0.14 .50 │ winding down
0.20 .26 │ calm late morning
0.34 .24 │ golden lull — just strolling
0.50 .30 │ dusk, lamps starting to light
0.58 .55 │ festival ramp
0.66 1.0 │ ██████████  NIGHT FESTIVAL peak
0.74 .94 │ █████████
0.80 .22 │ teardown
0.86 .06 │ pre-dawn — near-empty
0.93 .22 │ sunrise — first vendors return
1.00 .58 │ wrap back to the opener
```

Fixture density (`_furn_density`) follows the same curve but is **phase-only**
(not multiplied by `_run_fill`), so static deck dressing is present from `t = 0`
and never flickers — just sparser off-peak, fuller at the peak.

---

## 3. String lights — always strung, always lit

The hung **lantern garland** and **fairy lights** stay **strung and lit across the
whole cycle** (`lantern_win = True`, `fairy_win = True` in `_dressing`). Earlier
they were night-only and read as dead beads by day. They now carry a daytime floor:

```python
_STRING_DAY_FLOOR = 0.40
def _string_intensity(pal):
    return max(_STRING_DAY_FLOOR, _lit_intensity(pal))
```

So the strings glow *a little* even in full daylight and ramp to full at night,
while the **lamp posts** stay phase-gated (`0.20 ≤ p < 0.93`) and only kindle at
dusk. The day/golden showcase gameplay shots were regenerated to reflect this.

---

## 4. Event strategy — the night festival

The festival is not a separate mode; it is the **peak of the night window**
(`phase 0.58 – 0.80`, crest at `0.66`). It layers special objects on top of the
normal cast — drawn in the **near lane** at the night palette:

- **Lion dance** and **dragon dance** (red + jade skins) — `perf_lion_dance` /
  `perf_dragon_dance`.
- **Banner poles** and glowing **braziers** — `_near_banner` / `_near_brazier`.
- A busier kiosk, a **campfire** scenario, and the fullest crowd of the cycle.

These specials are **gated to night only** — they read by lantern/brazier light and
would look wrong in daylight, so they never appear in the day rosters.

---

## 5. Weather + run-fill coupling

Two more signals reshape the street on top of the day arc:

- **Run-fill** (`_run_fill`, `_FILL_SECONDS = 7.0`): the cast ramps in from empty
  over the first ~7 s of every run — the market "opening" — via a smoothstep, so a
  fresh run never starts on a crowded street.
- **Weather** (`_weather_crowd_factor`): in rain/snow the crowd thins. Because the
  factor only lowers each slot's *stable* inclusion gate, figures walk off **once**
  as the storm builds (no flicker); survivors raise **umbrellas**
  (`_wants_umbrella`), and a few **shelter figures** tuck under kiosk awnings and
  lamp posts so the worst of a storm still feels inhabited.

---

## 6. The glow contract (why nothing out-shines the coin)

The gold coin must always be the brightest object on screen. Every promenade light
obeys this:

- **`NIGHT_GLOW_CAP = 150`** — each lit RGB channel is clamped before any additive
  halo, so no lantern, bulb or brazier can rival the coin (measured ~206 isolated).
- **`_lit_intensity`** — `0` by day, `≈ 0.40` at dusk (lamps *just* beginning), `1.0`
  at full night; **gated to a dark sky** so day/golden stay unlit shells.
- A gentle **dusk → night fade-in** so dusk reads "lamps just lighting" rather than
  dead-then-on.

---

## Gallery

Per-family **catalogue grids** (every variant) and **in-scene gameplay frames**
(each family staged at its most flattering time of day) live in
[`./showcase/`](./showcase/). Iteration history per family — `round_N.png` +
`integrated.png` — lives in the per-family folders alongside this file.
