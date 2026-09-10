# Skybit — Living-World Event Ideas — Master List & Top 5

A brainstorm of new events/mechanics to make Skybit feel alive and memorable —
genuinely new gameplay, not reskins of the existing force-based events (geyser
updraft, rain dampen, snow tailwind, fog). 36 ideas across three "axes of
novelty," then a final Top 5.

---

## Wave A — new gameplay VERBS
*(reinvent the control mapping, fail-state, resource, or add a second body)*

| # | Name | Core novelty |
|---|------|--------------|
| 1 | Blood-Moon Inversion | Gravity/input flips — tap pushes DOWN. |
| 2 | Twister Climb | Scroll rotates to vertical; climb a chimney. |
| 3 | Hawk on Your Tail | A predator chases from behind; a pace floor. |
| 4 | The Fork in the Clouds | Corridor splits into risk/reward lanes (choice). |
| 5 | Fledgling (Escort) | Protect a tag-along chick (second-entity goal). |
| 6 | Whale Tow (Tether) | A towed mass swings like a pendulum (coupled body). |
| 7 | Living Gates | Gaps rhythmically open/close (aiming → timing). |
| 8 | The Maelstrom | A whirlpool exerts an orbital pull (rotational force). |
| 9 | Lights-Out Echo | Near-black; each flap sonar-reveals the pillars. |
| 10 | Lodestone Storm | Magnetic pillars; tap toggles attract/repel. |
| 11 | Festival Drums | On-beat taps are stronger (rhythm scoring). |
| 12 | Magpie Toll | Pay coins to pass (score becomes spendable). |
| 13 | The Gale (Pushback) | Headwind shoves you BACKWARD into passed pillars. |
| 14 | Mirror Mirage | An inverted anti-self you must dodge. |
| 15 | Chrono Squall | Drifting local fast/slow time rifts. |

## Wave B — STRUCTURAL
*(the obstacle field stops being a row of gates and becomes a continuous,
shaped, sometimes-living interior space — seeded by the Pagoda Warren)*

| # | Name | Core novelty |
|---|------|--------------|
| 16 | **Pagoda Warren** *(user's idea)* | Pagodas touch; gaps link into one winding corridor. |
| 17 | Switchback Slalom | A connected corridor that zig-zags steeply. |
| 18 | Crumbling Collapse | Passages seal in real time as the structure falls. |
| 19 | Keyhole Apertures | Thread a single irregular SHAPED opening. |
| 20 | Rising Tide | A flood rises; the playable space shrinks. |
| 21 | Ziggurat Descent | Drop floor-to-floor through offset holes. |
| 22 | Strand Weave | Thread a dense soft mesh of hanging strands. |
| 23 | Blind Bends | Tunnel bends hide what's ahead; read telegraphs. |
| 24 | Honeycomb Lattice | A hex maze with multiple routes and dead ends. |
| 25 | Iris Throat | A continuous tube that pulses and snakes. |
| 26 | Cog Maze | Rotating gear teeth form moving gaps. |

## Wave C — OUT-OF-BOX, NON-STRUCTURAL
*(reinvent the avatar, the meaning of the tap, what you trust on screen, or
what persists across runs)*

| # | Name | Core novelty |
|---|------|--------------|
| 27 | Split Soul | Two birds, two layouts, one tap flaps both. |
| 28 | Slipstream Trail | Your lingering contrail becomes a usable/avoidable object. |
| 29 | The Hush | Tapping makes noise that wakes danger — tap as little as you dare. |
| 30 | Metamorphosis | The bird becomes fish/glider/hummingbird — each a new control model. |
| 31 | Symbiote Passenger | A rider grants a perk AND a paired drawback. |
| 32 | Possession (Reins) | Bird auto-flies; your tap controls the WORLD instead. |
| 33 | Call & Bloom | Your tap is a call the ecosystem responds to. |
| 34 | Mirage Truth | The visuals lie; navigate by the bird's true shadow. |
| 35 | The Egg (Steady Hands) | Keep flight smooth or the balanced egg falls off. |
| 36 | The World Remembers | Past runs reshape the world (ghost line, landmarks, chants). |

---

## TOP 5

Chosen for novelty × feasibility × "they really invested thought," and
deliberately spanning five DIFFERENT axes so the set isn't one trick repeated.

### 1. Pagoda Warren (#16, user's idea) — *Geometry axis*
Best novelty-per-effort on the board. Reinvents the core obstacle from discrete
gates into a continuous corridor, reuses the existing pillar art + gap pipeline
(cheap and on-brand), and is a *platform*: Blind Bends, Strand Weave, Iris Throat
and narrowing throats all live inside it. One build, many flavours.

### 2. Split Soul (#27) — *Control axis*
The purest "a flappy game can do THAT?" moment: solve two flight problems with one
tap. Zero new buttons, sky-high skill ceiling, unforgettable on first encounter.
The strongest pure-wow idea here.

### 3. The Hush (#29) — *Verb axis*
Inverts the one compulsion the genre is built on — "tap to survive" becomes "tap
as little as you dare." Deeply original yet trivial to build (a noise meter that
fills on flap, drains on glide), and it makes a familiar level feel alien.

### 4. Metamorphosis (#30) — *Avatar axis*
Transforming the bird into different creatures with different control models gives
several "re-learn the controls" beats in one event, with big procedural-art
payoff. Keeps the world familiar while the *feel* keeps changing — high variety,
high charm.

### 5. The World Remembers (#36) — *Meta axis*
The biggest "they really invested thought" payoff, and partly feasible today
because Skybit already has the leaderboard/Supabase backbone. Ghost lines and
landmarks grown from your own history turn isolated runs into a saga — the deepest
expression of the "this world is alive, this is an adventure" goal.

**Honorable mentions:** Crumbling Collapse (#18) for memorability, Mirage Truth
(#34) for the perception twist, Symbiote Passenger (#31) for decision-rich
trade-offs.

---

## DIRECTION TAKEN — the Warren route + two dice-gated character events

### Why Pagoda Warren won in practice
Pagoda Warren (#16) had the best novelty-per-effort on the board: it reuses the
existing pillar + gap pipeline (cheap, on-brand) and is a *platform* rather than a
one-off — Blind Bends, Strand Weave, narrowing throats and future set-pieces can all
live inside it. So it became the spine of the work, maturing from "gaps link into one
corridor" into a full scripted **route**.

### The route + two dice-gated character events
A route isn't entered cold: it's framed by a **boss character who strolls on
trailing a floating die**. The player grabs the die, the die rolls, and the roll
**sizes/grades the route** that then scrolls in. That gives every event the same
living-world shape — a telegraphed character beat → a player grab → a bespoke route →
a payoff — which breaks the flat gate-after-gate loop. Two events are realized:

| Event | Character | Die roll | Route | Twist |
|---|---|---|---|---|
| **Clown / Dice** | fairground jester (Carousel-Barker scepter) | N = 10–25 pillars | fused-pagoda warren, one of 5 easy (d1–5) archetypes — Long Plunge, The Ascent, Rolling Hills, The Valley, The Crest | **GHOST** outcome — 10 pillars but Pip phases through them; prize-wheel celebration |
| **King-Skull** | Asthi-Dakini, six-armed bone deity | difficulty 6–10 | 22-pillar hard-band route of stacked-skull totem pillars (20 column recipes) | the totem units are the chosen king-skull design's *own* small skulls (crown + palm), reused directly |

### Status + where the detail lives
Branch-only R&D prototype on `v5_skybit_enrich` — no spawn trigger, no score
gating, no DB write yet; it runs only when the demo harness launches it
(native, this branch). The connective detail lives in:

- Event mechanics / route demo — [`game/warren_demo.py`](../game/warren_demo.py)
- Warren route catalog — [`docs/pagoda_warren/ROUTES.md`](./pagoda_warren/ROUTES.md)
- King-Skull character art lineage — [`docs/skybit_devil/batch2/DESIGN_JOURNEY.md`](./skybit_devil/batch2/DESIGN_JOURNEY.md) (chosen design: Asthi-Dakini **`SWITCHED + BIG`**)
- Skull totem pillars — [`docs/skull_king_stack/README.md`](./skull_king_stack/README.md)
- Clown columns — [`docs/clown_bone_columns/`](./clown_bone_columns/)
