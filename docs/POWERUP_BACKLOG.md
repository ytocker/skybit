# Skybit Powerup Backlog — Unimplemented Ideas

Powerup concepts brainstormed during v5_powerups planning but never built.
Each entry has a score (0-10) and a brief why-it's-rated-that-way.

## Scoring rubric

Every idea is judged against Skybit's identity:

- **One-button casual.** Tap = flap. No second input allowed.
- **Procedural art only.** No new PNG assets — sketchable with pygame
  primitives + existing palettes.
- **60 FPS native + pygbag WASM.** Anything with numpy on the hot path
  or first-frame stalls is disqualified (this is what killed NIGHTGLOW).
- **Skill ceiling preserved.** No "free pillar hit" gimmes (this is what
  killed SHIELD; same reason CLAUDE.md hard-rules REVERSE off).
- **8 s effect window.** Buffs should feel like a rush, not a long mode
  change.
- **Reads in 2 frames mid-flap.** A player has to recognise the buff
  instantly.
- **Skybit-native preferred.** Leans into the parcel, the parrot, the
  sandstone-with-vegetation pillars, the biome cycle, the dollar-coin
  economy — not generic Sonic / Jetpack Joyride / Temple Run copies.

---

## Top tier (score 8+ — ready to prototype)

### AIR POCKET — 9
Translucent columns of rising air appear in alternating pipe gaps for
the buff window. Flying into a column auto-boosts Pip upward (free flap,
particle shimmer). The ONLY unselected idea that introduces a NEW
SPATIAL VERB (positional use of the gap) without violating one-button,
removing agency, or creating powercreep. Procedural art is trivial
(alpha-blit a shimmer mask in the gap column). Strongest unshipped
concept in the entire backlog.

### PARCEL HATCH — 8
Pip's parcel cracks open; a baby Pip pops out and flies ~30 px ahead of
Pip as a "coin scout" — any coin the chick touches teleports to Pip.
10 s. Activates the most-underused asset in the game (the parcel has its
own hitbox but no gameplay). The chick reaches coins Pip can't physically
collect (above pillars, deep in the gap). Auto-grab keeps it
set-and-forget, so the second moving entity doesn't add cognitive load.

### PILLAR SHAVE — 8
A magical wind shaves the green vegetation tops off the next 5 pillars;
pillars become ~40 px shorter; gap moves upward. Leans into Skybit's
specific art (the sandstone pillars with vegetation tops are unique to
this game). Cumulative shift across 5 pillars is substantial; falling-
vegetation particles sell the effect.

### COMPOUND INTEREST — 8
Each coin collected during the buff multiplies cumulatively:
×1.1 → ×1.21 → ×1.33 → ×1.46 → ... A coin streak gets exponentially
valuable. Cap at ×3.0 prevents runaway. Quantitatively distinct from
TRIPLE (which is a flat ×3) — this rewards uninterrupted skill streaks.

---

## Solid candidates (score 6-7 — worth prototyping if cheap)

### MOONSHINE — 7
Sky instantly transitions to night for 15 s; every coin pulses with
moonlight and is worth 3×. Atmospheric AND scoreful. Leans on Skybit's
existing biome system. Risk: could create "wait for moonshine to spend
other buffs" meta, but 15 s is too short to game.

### AFTERIMAGE / ECHO — 7
A faint Pip-shadow trails 0.5 s behind. Any coin the shadow grazes is
collected at full value. Adds a spatial-prediction layer ("if I dive now
my shadow catches the coin I'm about to overshoot") without a second
input. Shadow collects coins ONLY, not pillars — kill-box stays on Pip
so hitbox confusion is bounded.

### COCONUT BOMB — 7
A coconut tumbles from the sky and bonks the next upper pillar, breaking
off its bottom ~40 px. Gap grows downward for that one pillar. One-shot
dramatic relief moment that fits the comic vocabulary. Auto-targeted, so
no aim mechanic needed — "relief moment" buffs work fine (same model as
TREASURE BOX).

### GRAVITY WELL — 6
Pip becomes a tiny "planet" for 8 s; coins orbit him at increasing
speed; on timer end all orbiting coins are collected at 2× value.
Visually unique, very Skybit. Risk: orbit math at 60 FPS on WASM is the
exact perf-tier of trouble that killed NIGHTGLOW. The "cash-in at ×2"
also has MEGA-MAGNET-style powercreep flavour.

### FORKLIFT PARCEL — 6
Parcel becomes a forklift fork. Sliding under the next lower pillar
lifts it up 40 px as Pip passes — the gap moves down for that one
pillar. One-pillar effect. Parcel-as-X is a strong Skybit-native vein.
Risk: "lift the pillar" physics isn't realistic but is legible.

### SPRING PAD — 8†
*(†rated in the synthesized round, not in the user's original
brainstorm — included for completeness.)* Pillar tops temporarily get
bounce-pad sprites; landing on a top flings Pip back up instead of
killing him. Adds a NEW VERB (bounce) and turns lethal pillar-tops into
playful targets. Fits the skateboard energy. Tuning risk: bounce
velocity has to feel intentional, not chaotic.

---

## Mid tier (score 4-5 — keep on shelf)

### SQUAWK ECHO — 5
Pip lets out a visible 3-burst squawk; each wave hits an upcoming
pillar and makes it lean away ~20 px. Original (bird literally talks
the pillars out of his way), but "leaning pillar" reads as a bug to a
first-time viewer.

### PARCEL DROP — 5
Pip releases the parcel; it falls and knocks the next pillar over
sideways (gap doubles for one pillar). Novel verb. Drawing a tilted /
toppled pillar breaks visual coherence with the rest of the game.

### DRAGON BREATH — 5
Tiny dragon hat on Pip; each flap shoots a small flame forward, burning
off ~30 px of vegetation per upcoming pillar tops. Cool, but
functionally PILLAR SHAVE with extra particles — redundant if PILLAR
SHAVE ships.

### NIGHTGLOW — 5
Biome-gated glow-in-the-dark visual effect. Killed for WASM perf last
time (numpy on activate). Even without numpy, pure-visual buffs feel
weightless next to mechanical ones.

### DOUBLE FLAP — 5
A second mid-air flap window. Mechanically rich. But typical gap
requires ~1 well-timed flap; with double flap, no gap fails — it's
SHIELD-by-stealth, same reason SHIELD itself was killed.

### CHAIN LIGHTNING — 7†
*(†synthesized round.)* Each collected coin auto-zaps every coin within
~30 px to Pip. Turns a 14-coin rush into "tap one, get the cluster".
Proximity propagation is genuinely new mechanically and thematically
ties to the existing thunder weather.

### BLUEPRINT VISION — 7†
*(†previously approved by user but never built.)* Next 2-3 pillars
render as faint blue wireframe outlines on the right horizon. Adds
tactical depth without a second input. Risk: players may not read the
ghost lines as "future pillars".

---

## Hard cuts (do NOT entertain)

These were considered and rejected for clear cause. Don't re-litigate
without explicit user direction.

- **TIME REWIND** — fatally overlaps PHOENIX, which already shipped.
- **STORK COURIER** — autopilots Pip past 4 pillars. Removes player
  agency, the cardinal sin in a one-button game. Same reason RAIL was
  cut.
- **BUTTERFLY GUIDE** — draws a glowing ribbon along the optimal path.
  "Follow the line" deletes the planning skill that IS the game.
- **PROPELLER HAT** — each flap delivers 1.5× thrust. Changes flap
  physics tuning; players will mash flap and pop off the top of the
  screen.
- **VINE BRIDGE** — horizontal vines between pillar tops at gap-height.
  Mid-air horizontal hitboxes are bad design (collide with what?).
- **STATIC CLING** — magnet++ that pulls unspawned powerups too. Pure
  powercreep on MAGNET.
- **FLOCK CALL** — V-formation of 4 ghost parrots widens pickup zone.
  Also pure powercreep on MAGNET.
- **SHIELD (full)** — one free pillar hit. Compresses the entire skill
  ceiling.
- **REVERSE / GRAVITY FLIP** — implementation intact in `game/world.py`
  but CLAUDE.md hard-rules it off ("the climbing pitch is uncomfortable
  and the inversion disorients players").
- **VACUUM (5× MAGNET)** — strictly dominated by MEGA MAGNET, which
  itself ranked dead last.
- **MIRROR PILLARS** — vertical flip of pillar geometry. Visual chaos
  without a mechanical hook.
- **All Round-1 "copies"** — BUBBLE / FIRE / LIGHTNING SHIELD, JETPACK,
  ROCKET DASH, TIME STOP, HOVERBOARD, JACKPOT 5×, COIN RAIN, WINGMAN,
  ECLIPSE, GOLDEN HOUR, DISCO, RAINSTORM, SNOWSTORM, AURORA, 8-BIT,
  CHERRY BLOSSOM, ZERO-G, MIRROR MODE, TINY PILLARS, GIANT GAPS, UFO
  ABDUCTION, SHOCKWAVE, WORMHOLE, SYMPHONY, PIRATE TREASURE / HAT,
  CROWN, CRACKERS, FEATHER STORM, CHICKEN BUCKET BOMB. User rejected
  these as derivative of other games (Sonic, Subway Surfers, Jetpack
  Joyride) in the original brainstorm — that decision stands.

---

## Categories at a glance

A meta-observation from the rating: the strongest unimplemented ideas
cluster into a few recognisable families.

### Parcel-as-X (under-leveraged)
Pip carries a parcel permanently; it has its own hitbox. Transforming
it is a Skybit-native idea space.
- PARCEL HATCH (8) — chick coin-scout
- FORKLIFT PARCEL (6) — lifts next pillar up 40 px
- PARCEL DROP (5) — knocks next pillar sideways
- PARCEL ROCKET — 2× speed dash through 2-3 pillars (not separately
  scored, but solid concept)
- PARCEL PARACHUTE — slow-descent glider
- GENIE LAMP — parcel becomes a lamp, genie grants 1 random buff
- BEAK RUDDER — parcel as auto-steer fin
- YO-YO PARCEL — parcel launches forward to break pillar tops

### Pillar manipulation
- PILLAR SHAVE (8) — vegetation off, gap up
- COCONUT BOMB (7) — bonks upper pillar, gap down
- DRAGON BREATH (5) — flame burns pillar tops
- CRUMBLING WALLS — next 3 pillars disintegrate over 2 s
- HONEY DRIZZLE — pillar tops become slick (mini-skateboard effect)
- BANANA PEEL — drop slides next pillar backwards 80 px

### Spatial / level interaction
- AIR POCKET (9) — updraft columns
- SPRING PAD (8†) — bounce-pad pillar tops
- AFTERIMAGE / ECHO (7) — shadow collects coins
- BLUEPRINT VISION (7†) — pillar preview on right horizon

### Coin economy
- COMPOUND INTEREST (8) — streak multiplier
- MOONSHINE (7) — night + 3× coin value
- CHAIN LIGHTNING (7†) — proximity propagation
- GRAVITY WELL (6) — orbit-then-cash-in

### Atmosphere
- MOONSHINE (7) — forced night
- BIOME WARP — jump biome phase ahead
- NIGHTGLOW (5) — glow-in-dark
- AURORA / RAINSTORM / SNOWSTORM — cosmetic weather (all cut as
  too-generic)

### Wearables (skateboard cousins)
- PROPELLER HAT (5) — 1.5× flap
- LEAF GLIDER — halves gravity
- BEAK RUDDER — auto-steer
- HARD HAT — folded into SKATEBOARD's helmet at design time

### Vision / foresight
- BLUEPRINT VISION (7†)
- BUTTERFLY GUIDE — hard-cut (deletes planning skill)

### Pip mechanics (parrot identity)
- SQUAWK ECHO (5) — squawk-wave pillar nudge
- MOLT — sheds feathers, gravity drops to 0.3×
- FLOCK CALL — hard-cut (powercreep)

### Narrative moments
- COCONUT BOMB (7) — one-shot relief
- STORK COURIER — hard-cut (removes agency)
- SHOOTING STAR — catch for 3 random buffs
- FORTUNE COOKIE — random buff reveal
- GIFT CHAIN — 5 wrapped presents, risk-reward chain

---

## Recommendation

If a slot opens up in the powerup pool (e.g., a future cut creates
room), the natural prototyping sequence is:

1. **AIR POCKET** — highest novelty + lowest risk to identity
2. **PARCEL HATCH** — unlocks the parcel as a feature class
3. **PILLAR SHAVE** — leans on the unique pillar art uniquely
4. **COMPOUND INTEREST** — score-rush flavour distinct from TRIPLE

All four are score 8+ and pass every rubric criterion. Anything below
score 7 should stay on the shelf unless game-design intent shifts.

---

# Expansion concepts (orthogonal to current backlog)

The catalogue above covers obvious categories: parcel-as-X, pillar
manipulation, spatial verbs, coin economy, atmosphere, wearables,
vision, narrative. This section adds a different axis — **currencies
and hooks the game already has but never reads**, paired with
**design-space holes nothing in the catalogue addresses**.

## Missing categories

What no existing or backlogged powerup does:

1. **Near-miss as a resource.** `world.near_misses` is incremented on
   every close-call but only displayed in post-run stats. The game
   has a hidden "bravery" stat the player can't see or spend.
2. **Weather as a gameplay input.** Rain, lightning, fog, wind all
   render in `game/weather.py` but never affect physics or scoring.
   Weather is decoration, not a partner.
3. **Sacrifice / chosen trade.** Every existing powerup is pure
   positive. LOTTERY has downside but that's passive RNG; the player
   never makes an *active* in-the-moment trade.
4. **Restraint-rewarding.** Every powerup rewards taps (HEIST, TRIPLE,
   SKATEBOARD tricks) or fires regardless of input. Nothing rewards
   NOT flapping.
5. **Conditional / context-aware.** No powerup reads the world state
   at pickup. The biome cycle is a 5-minute clock that no powerup
   ever consults.
6. **Streak / momentum meta.** No persistent meter survives between
   pickups. Pillars-passed is counted but not "perfect streak".

## Unpolished gems (under-leveraged code already in the repo)

| Asset | File | What it does today | What it could feed |
|---|---|---|---|
| `world.near_misses` | `world.py` | Written, never read live | A "bravery" currency |
| Weather phase | `weather.py` | Renders rain / lightning / wind / fog with zero gameplay effect | Conditional powerup behaviour |
| Biome phase | `biome.py` | Drives only sky palette | Time-of-day-conditional buffs |
| `Pipe.seed` | `entities.py` | Deterministic decoration only | Per-pillar danger / loot tags |
| `Bird.grind_type` | `entities.py` | Tilts Pip ±18°, never scores | Grind-chain combos |
| `world.flap_count` | `world.py` | Stat-only post-run display | Restraint-reward systems |
| `coins_spawned vs grabbed` | `world.py` | Stat-only; never read live | Dynamic spawn modulation |
| 18 ambient events | `ambient.py` | Single 240 s cooldown for all | Per-event time-of-day loot tables |

## Six original concepts (each ties to one gem + one missing category)

### 1. BRAVADO — score 9

**Hook:** for 8 s, every near-miss bumps a visible multiplier
(1× → 2× → 3× → cap 5×). Coins collected pay out at the live
multiplier. Pillar hit (death) drops back to 1×. Pip visibly shivers
a feather on each near-miss so the bank is *felt*.

*Uses: `world.near_misses` (live consumer for the first time). Fills:
near-miss-as-currency, streak rewards. Rationale: first powerup that
actively wants the boldest play, not the safest.*

### 2. STORM RIDER — score 8

**Hook:** pickup does nothing visible. For 8 s, the effect depends on
current weather:

- **Clear** → magnet
- **Rain** → coins slide an extra 30 px toward Pip (slippery)
- **Fog** → screen dims but every coin is worth ×3
- **Lightning** → every flash auto-collects all on-screen coins

HUD shows a tiny weather icon next to the timer so the rule is
learnable.

*Uses: `weather.py` phase (live consumer). Fills: conditional powerup,
weather as partner. Rationale: same pickup, four expressions — the
world becomes a strategy axis.*

### 3. TRADE WIND — score 8

**Hook:** on pickup, a 1 s ring closes around Pip. Tap during the
ring = surrender half your current score, gain a 10 s ×3 coin storm.
Don't tap = the powerup does nothing. The decision is the gameplay;
the existing tap input becomes a yes/no choice.

*Uses: `world.score` as currency to spend. Fills: sacrifice mechanic,
active in-buff choice. Rationale: first powerup where the player
decides something meaningful IN the buff, not just by picking it up.
No new input — tap is the canonical verb.*

### 4. MIGRATION — score 8

**Hook:** same icon, different effect by biome phase at pickup:

- **Day** → standard magnet
- **Golden hour / dusk** → ghost-through-next-3-pillars
- **Night** → all coins on screen become $5 (instead of $1) for 8 s
- **Dawn** → refresh every other active powerup timer to full

The pickup's in-world icon morphs to show the current variant before
collection, so the player can read the world clock.

*Uses: `biome.py` phase (live consumer for the first time). Fills:
conditional / context-aware. Rationale: makes the 5-minute biome cycle
a strategy variable for free — players save the pickup for night to
bank the high-value variant.*

### 5. THERMAL — score 8

**Hook:** for 8 s, every second Pip goes WITHOUT flapping awards +1
coin with a small particle puff so the bank is felt. Gravity is
unchanged — if you wait too long, you hit the ground.

*Uses: `world.flap_count` (read live for the first time). Fills:
restraint reward, no-input-as-input. Rationale: every other powerup
rewards taps; this is the first that rewards stillness. Parrots glide
on thermals — most thematically on-brand idea in the entire backlog.*

### 6. WINDFALL — score 7

**Hook:** on pickup, the next 5 pillars' gaps shrink by 30 % (harder),
but every coin in those 5 pillars is worth ×5. Hard-edged, advertised
cost. No RNG.

*Uses: per-pillar tagging infrastructure (mirrors `Pipe.is_kfc` sticky
flag). Fills: sacrifice via difficulty, not score. Rationale: pure
expression of "voluntary constraint = multiplier"; players grab this
only when they feel sharp.*

## Recommendation (expansion set)

| If you want… | Pick |
|---|---|
| Cleanest activation of a dormant system | **BRAVADO** (near-miss counter) |
| Most Skybit-thematic | **THERMAL** (parrots glide on a thermal) |
| Deepest mechanical ceiling | **MIGRATION** (turns the biome system into strategy) |
| First true sacrifice mechanic | **TRADE WIND** (flexible) or **WINDFALL** (dramatic) |
| Weather as a real partner | **STORM RIDER** |

Together with the catalogue above, Skybit gets ~10 distinct mechanical
hooks to draw from. None of these copy any specific game — each is
grounded in a Skybit-only asset (the parcel, biome cycle, weather,
near-miss counter, flap economy) and addresses a design hole nothing
else fills.
