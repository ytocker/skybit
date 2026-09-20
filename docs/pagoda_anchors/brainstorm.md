# Pagoda anchor post for the prayer-flag bunting — brainstorm (phase 1)

## The problem (measured)

`game/foreground_promenade.py` `_dressing()` (~2062) strings prayer-flag
bunting at y477 (`GROUND_Y-118`). Nothing in the scene reaches that height:

| element | top y | gap below the rope |
|---|---|---|
| prayer-flag rope | **477** | — |
| lantern garland | 498 | 21px |
| tallest street lamp | 503 | 26px |
| kiosk pagoda roof | 549 | 72px |

So every span terminates in empty sky. Measured row density across the
daytime window (`p >= 0.924 or p < 0.416`), continuous scroll with the span
latches settled: **~1.5-2.0 spans on screen**, with real gaps at phases
0.25 / 0.40 / 0.96 where `_overhead_busy` suppresses quiet blocks.

## User-locked constraint

The rope height is CORRECT and must not change. The pagoda rises to meet it.

## Shared integration problems (apply to every concept)

1. **Lattice lock.** Posts must be emitted on exactly `period=149, x0=20`
   (`sp._garland_spans`), at `mult=PROP_MULT == GROUND_MULT == 1.0`, or the
   posts and the rope ends will never coincide.
2. **Lamp collision — confirmed independently.** Lamps run two rows at
   `period=251`, `x0=18` and `x0=143`. Over the 37399px lattice repeat,
   **83/252 post slots (32.9%) land within 20px of a lamp, and the minimum
   separation is 0px** (slot k=80, world x=11940). Without a suppression or
   nudge rule a pagoda will grow out of a lamp post.
3. **The 2px hook mismatch.** Each post is the right end of one span (y479)
   and the left end of the next (y477), so the hook detail must be >=4px
   tall or there will be a visible kink.
4. **Bare is the majority state.** Bunting is suppressed at night and on
   `_wk._LOW` blocks, so posts stand flagless most of the time. "Looks
   intentional bare" is a requirement, not a nice-to-have.

## The five directions

### 1. `sutra-stele` — inscribed dharani pillar  ★
Octagonal stone shaft 595->490, three 3px canopy discs interrupting it at
555/522/495 so the pagoda cue repeats vertically, 2-tier `_pagoda_roof`
crown at 486, bronze collar-ring hook at y477, lotus-bud spire.
**Widest 20px (plinth); shaft 9px** — slimmest of the five.
Static, bakeable, one blit/frame. Zero corridor and zero luma risk.

### 2. `mini-to` — five-storey miniature pagoda  ★
Five telescoping storeys 595->500, `_eave_tang_curl` half_w 13/12/10/9/7 at
constant 7px overhang, `sorin` disc mast piercing to the y477 hook ring.
**Widest 28px** (lowest eave); under 20px above y540.
Hero silhouette, ties the street to the pagoda pillars the player dodges.
Most expensive (~60-80 calls, must bake). **Highest corridor mass.**

### 3. `paifang-gate` — one-bay roofed archway  ★
Two 4px legs at cx±12, a 34x4px lintel crossing at **y477-481** with the
rope tied at its mid-span, low 2-tier `_pagoda_roof` above, tie-beam and
plaque at y520.
**Widest 34px but ~80% open sky; solid occlusion only 8px.**
The only concept where the rope visibly terminates on a beam — the literal
answer to the complaint — and it absorbs the 2px hook mismatch for free.
The bird flies through a temple gate.

### 4. `huabiao-crossarm` — cloud-board yoke column
8px drum-banded column to ~500 with a 2-tier roof at 496 (pagoda cue kept
BELOW the play band), 4px neck up to a 30x5px carved cloud board at
y475-481 with curled scroll tips.
**Widest 30px but only 4px of solid silhouette above y500** — lowest
corridor mass of any concept that reaches the rope. Cheapest (~18 calls).
Risks: roof at y500 is only 3px above the tallest lamp, so it may read as
"a pole with a hat"; tying at the board tips would shorten the span.

### 5. `toro-beacon` — stretched stone lantern
Canonical four-part toro: kiso plinth, 7px fluted sao shaft, chudai
platform, lit hibukuro fire box at 510-490, 2-tier `_pagoda_roof` kasa,
hoju finial, iron eye-bracket hook at y477.
**Widest 22px; shaft 7px.** Best night payoff — the street lights a row of
these as the flags come down, so the bunting's absence gets a reason.
**Only concept with real night-luma risk**, and a genuine identity risk:
`_props.draw_lamp` already ships a stone-shrine lamp variant, so this may
read as "the street lamp, but taller" — the complaint in reverse.

## Designer's picks
`sutra-stele` (slimmest, safest), `paifang-gate` (strongest narrative fix),
`mini-to` (hero shot, highest risk).
