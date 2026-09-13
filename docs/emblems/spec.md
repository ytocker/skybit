# Skybit Achievement Emblems — concept spec (57 distinct center glyphs)

## v2 — LOCKED

Folds in the art-director's final critique. What changed from v1:

- **Rank-dressing (L0–L4) is demoted everywhere.** It is invisible at 22px and is
  NO LONGER the load-bearing tier cue for any family. Every tier now reads off
  **COUNT and/or MATERIAL/CONTAINER growth** (the benchmark confirms those read at
  row size). L-marks survive only as a faint optional accent — each ladder line now
  states what actually carries the read.
- **Seven former Fallbacks are promoted to PRIMARY** — the "N distinct shapes"
  idea dies at row size, so the read becomes "N identical marks in/on a container"
  (quantity + container, not variety): `powerup_sampler`, `powerup_collector`,
  `full_combo`, `icarus`, `night_owl`, `the_49er`, `so_close`.
- **Per-entry locks:** score chevron-COUNT not halo; day disc-COUNT not phases;
  vault = tall safe (distinct aspect from the wide chest); treasure_hunter loses the
  gem-spark; near_miss UNIFIES on needle-and-thread for both rungs; head-bonk keeps
  the ceiling BAR as the shared anchor; marathon = stopwatch + one road-dash, no
  numerals; the HAND is exclusive to Midas; jackpot/lottery rely on the slot WINDOW
  FRAME + tone, not legible symbols; rail_rider's rail is visibly SNAPPED;
  kfc_incident bucket tilt ≥30°; poisoned skull enlarged; hummingbird capped at 3
  arcs; early_checkout drops the luggage tag.
- **35 greenlit emblems are untouched** (listed in the closing confirmation).

---

BRAINSTORM ONLY. No renders. Concepts for the engraved center glyph of each of
the 57 medallions. Today these share ~21 `_glyph_*` functions in
`game/achievement_icons.py`; the goal is one purpose-built glyph per achievement
whose silhouette depicts *that* achievement's nature, drawn in the same
single-colour engrave style (lit body + down-right inset shadow + up-left sheen,
all in the passed `col`; a tiny accent only on unlock, like the existing magnet
poles / fry box).

## Reading rules (apply to every glyph below)

- Every glyph is authored in a 0..1 box scaled by `r`, stroked by `_stamp_glyph`,
  so descriptions are in terms of bold filled polygons / thick lines / circles.
- **Legibility floor:** the engrave renders at ~44px row size; the glyph itself
  is `gr = R*0.56`, i.e. roughly a 22–24px shape. Anything thinner than ~3px or
  smaller than ~5px reads as a smudge. Where a concept risks that, a **Fallback**
  line gives the simplified silhouette to drop to.
- **Tier families escalate ONE motif** — same base silhouette, with a defined
  ladder of added metal/marks. Non-tier siblings are bottom-up-distinct
  (blackout/swap/cover-label tested in the notes).
- **Two-tone accent rule:** any saturated accent must come through `_accent(...)`
  so it desaturates to bronze when the medal is dormant. Default to pure
  single-colour; only call out an accent where it earns its keep.

---

## Tier-escalation ladders (defined once, referenced below)

**The load-bearing tier cue is COUNT and/or MATERIAL/CONTAINER growth — NOT rank
dressing.** Rank dressing (the L-marks below) is invisible at the ~22px glyph size
the benchmark tested, so it can never be the primary differentiator. Every tier
family carries its read by literally adding motif elements (1→2→3) and/or by
upgrading the container or material (none→stack→sack→safe; feather→armour;
arrow→helmet). The L-marks survive ONLY as a faint optional accent layered on top
of that real read — a glance reads the climb from count/container before it ever
notices a pip or crownlet.

Five reusable rank-dressing accents (faint, optional, NEVER the differentiator):

- **L0 plain** — bare motif, no rank marks.
- **L1 pips** — 1–3 small notch-dots tucked under/beside the motif.
- **L2 wreath tick** — a short laurel-echo tick flanks each side.
- **L3 ray halo** — 6–8 short radiating ticks behind the motif. Drop it whenever it
  muds into the motif's own lines (e.g. behind chevrons).
- **L4 crown** — a 3-point engraved crownlet seated on top of the motif.

Each ladder line below states what ACTUALLY carries the read (count/container),
and treats any L-mark as the faint cherry on top.

---

## FAME — Flight Log (10)

Base motif of this category's hero ladder is the **sandstone temple pillar**
(matches in-game pillars). Score and day-cycle are their own sub-motifs.

**Pillar-count ladder (first_flight → pillar_25 → pillar_50 → pillar_100):** one
shared "pillar gateway" motif that gains height, count and rank-dressing.

- `first_flight` — **First Delivery** — ONE squat sandstone pillar (cap + base +
  fluted shaft) with a small parcel/letter glyph (a tiny enveloped square with a
  corner fold) tucked at its foot — the "first delivery" made. L0.
- `pillar_25` — **Courier in Training** — TWO pillars forming a gateway, the
  parcel gone, **L1** (two pips at the base = "25 stamps on the route").
- `pillar_50` — **Route Veteran** — THREE pillars stepping up in height
  (a colonnade receding), **L2** wreath ticks flanking the base.
- `pillar_100` — **Centurion of the Sky** — a tall triumphal **arch** spanning
  two pillars (the colonnade resolved into a monument), **L4** crownlet on the
  keystone. The "100" apex.
- *Escalation ladder — carried by COUNT + STRUCTURE growth:* 1 pillar → 2
  pillars(gateway) → 3 pillars(colonnade) → arch spanning two posts. The pillar
  COUNT (1→2→3) and the structure's growth from a single post to a monument is the
  whole read; L0→L1→L2→L4 rank dressing is a faint optional accent only.
- *44px risk:* fluting detail is invisible — Fallback: plain tapered shafts with
  a flared cap/base block, no flutes; the arch is just a thick semicircle bridging
  two posts.

**Score sub-motif (score_100 → score_500):** a **chevron/altimeter climb** — an
upward delivery-flight read, NOT a star (stars are reserved for lottery/jackpot).

- `score_100` — **Triple Digits** — a bold up-right **chevron stack of 2**
  (climbing arrows) with three short tally ticks beneath (the "triple digits"
  nod). L0.
- `score_500` — **High Flyer** — a chevron stack of **3** rising higher, with a
  small wing-pip riding the top chevron. NO ray halo (it muds into the chevron
  lines). The wing-pip is the only added flourish.
- *Escalation ladder — carried by CHEVRON COUNT (2→3):* the climb literally gains a
  rung; score_500 alone adds a wing-pip. The ray halo is DROPPED as a tier cue
  because it muds into the chevrons at row size.

**Day-cycle sub-motif (day_complete → day_three):** a **sun-over-horizon that
acquires moons** — depicts surviving day→night.

- `day_complete` — **Round the Clock** — a half-sun on a horizon line with **ONE**
  small moon-disc nested beside it (one full day→night), framed by a faint orbit
  arc. L0. The moon is a plain small disc — NO phase shape.
- `day_three` — **Three-Day Weekend** — the same horizon, now **THREE** identical
  small moon-discs arcing over the sun in a row — three nights survived. NO
  phase/crescent shapes; all three are the same plain disc so the COUNT is the read.
- *Escalation ladder — carried by MOON-DISC COUNT (1→3):* 1 sun+1 disc → 1 sun + 3
  identical discs; the night-count is literally the disc-count. No phase shapes
  (they're sub-pixel at row size); L2 wreath ticks are a faint optional accent only.

**Lifetime pillar ladder (frequent_flyer → globetrotter):** distinct from the
per-run pillar ladder — a **globe/route** read, since these are *all-time*
distance, not a single run's gateway.

- `frequent_flyer` — **Frequent Flyer** — a small **globe** (a circle with two
  curved longitude/latitude lines) wearing a tiny wing-tick, with **L2** wreath.
- `globetrotter` — **Globetrotter** — the same globe wrapped by a full **dashed
  flight-orbit ring** with a parrot-silhouette pip on the orbit, **L4** crownlet.
- *Escalation ladder:* winged globe → globe encircled by an orbit+crown; the
  route closes into a full lap of the world.
- *44px risk:* longitude lines crowd — Fallback: globe = circle + ONE vertical +
  ONE horizontal arc only; orbit = a single bold dashed ellipse.

*Distinctness within Flight Log:* per-run pillars = **architecture** (posts→arch);
lifetime pillars = **globe**; score = **chevrons**; day = **sun+moons**. Four
different silhouettes, no shared base body.

---

## FAME — Riches (6) — one coin/$ wealth ladder

Shared motif: the in-game **`$` dollar coin** (reuse `_glyph_coin`'s ringed `$`).
The ladder climbs by **coin count + container + rank dressing**, ending in a Midas
crown. This is the canonical 6-rung escalation.

- `coin_25_run` — **Pocket Change** — ONE `$` coin, slightly tilted, with two
  tiny coin-edge nicks beside it (loose change). L0.
- `coin_100_run` — **Coin Run** — a short **stack of 3** `$` coins (overlapping
  discs, top one face-on showing `$`). L1 pips. "A run of coins."
- `coins_500_life` — **Coin Collector** — a **coin pouch** (drawstring sack) with
  a `$` on its belly and two coins spilling at the foot. L2 wreath ticks.
- `coins_5000_life` — **Coin Vault** — a **TALL SAFE** drawn portrait/upright (a
  tall rounded-rectangle body, clearly taller than wide) with a **thick bezel
  door-PORTHOLE** — a heavy ringed circular door filling most of the square — and a
  small dial nub. Coins now *stored* behind a vault door. The TALL aspect + thick
  bezel porthole must read as a safe, NOT a lid. **Must not collide with
  `treasure_hunter`'s chest** — that is a WIDE LOW trapezoid with an ajar lid; this
  is a TALL upright box with a circular bezel door. Different aspect ratios are the
  separator.
- `coin_tycoon` — **Coin Tycoon** — a **treasure pile** (a mound silhouette
  topped by a face-on `$` coin and two arcs of stacked coins) under a **L4**
  crownlet. The wealth overflows.
- `midas` — **Midas Touch** — a **hand/touch** turning a `$` coin to gold: a
  stylised **open palm** (three fat finger-stubs + thumb, no knuckle detail)
  beneath a **radiant `$` coin**, with a single unlock-only **gold sparkle accent**
  at the fingertip (`_accent` gold→bronze when dormant). The apex of the whole
  game's wealth. **The HAND is EXCLUSIVE to Midas** — no other emblem (and
  specifically not `the_scrooge`) uses a hand, so the open-palm-under-radiant-coin
  silhouette is unmistakably Midas.
- *Escalation ladder — carried by CONTAINER growth:* coin → 3-stack → pouch →
  TALL safe → hoard pile → golden-touch hand. The container literally grows
  (none→stack→sack→safe→hoard→myth) and that growth IS the read; the `$` glyph is
  the constant thread through all six. Rank dressing L0→…→L4 is a faint optional
  accent only.
- *44px risk:* Midas hand reads as the palm-under-coin gesture; keep it to fat
  finger-stubs, no knuckle detail.

---

## FAME — Power Player (7)

Power-ups are the **four-point sparkle** in-game; this category riffs on it but
each non-tier sibling is its own object.

- `first_powerup` — **Power Up!** — the single canonical **four-point sparkle**
  (`_glyph_powerup`) with a small up-arrow notched into its lower point — "your
  first." Keeps the franchise sparkle as the category anchor.
- `powerup_sampler` — **Buffet** — a **round plate ring holding FOUR IDENTICAL
  marks**: a thin plate ring with four same-shaped filled dots evenly spaced on it
  — "4 power-ups sampled in one run." The read is QUANTITY-ON-A-CONTAINER (four
  identical marks on a plate), NOT shape variety (distinct morsel shapes die at row
  size). Count = 4; single-colour.
- `magnet_life` — **Animal Magnetism** — the **horseshoe magnet** (`_glyph_magnet`)
  but with a small `$` coin and a feather being pulled toward its poles by two
  short attraction-arc ticks — "magnetism, 15×." Keeps the magnet's red/steel
  pole accent (unlock-only).
- `powerup_collector` — **Gotta Grab 'Em All** — a **binder grid of identical
  dots**: a rounded "binder" rectangle holding three rows of three IDENTICAL filled
  dots (a completionist's collection wall, every slot filled). The read is GRID
  COMPLETENESS (a full container of same dots), NOT pip variety. Single-colour.
- `greasy_fingers` — **Finger Lickin'** — the **KFC fry bucket** (`_glyph_kfc`,
  red box accent) but viewed as a striped bucket with fries fanned out and a small
  grease shine-tick — distinct from the Shame `kfc_incident` (which is the same
  bucket *tarnished/knocked over*). Keeps the brand-red accent (unlock-only).
- `power_hungry` — **Power Hungry** — a **sparkle being devoured**: an open
  mouth/jaw arc (two curved lips) biting a four-point sparkle, with one bite-notch
  out of the sparkle. "Hungry for power." L2 wreath ticks (it's the 100 rung).
- `power_addict` — **Power Addict** — the same hungry motif escalated: a
  sparkle-vortex — a four-point sparkle at the center of a spiral of three more
  sparkles being pulled in — under a **L4** crownlet. "500: insatiable." This is
  power_hungry's escalation partner.
- *Tier ladder (power_hungry → power_addict):* mouth-biting-one-sparkle →
  sparkle-vortex-of-four + crown; the appetite grows from one bite to a whirlpool.
- *Distinctness:* anchor-sparkle (first) vs four-dots-on-a-plate-ring (buffet) vs
  magnet (magnetism) vs binder-grid-of-nine-dots (collector) vs fry-bucket (greasy)
  vs mouth (hungry) vs vortex (addict) — seven different silhouettes. Buffet (a
  plate RING, 4 dots) and collector (a binder RECTANGLE, 9 dots) stay distinct via
  container shape + dot-count; only first/hungry/addict share the sparkle element,
  each framing it differently (notched / bitten / whirlpool).

---

## FAME — Stormchaser (9)

Three tier families + four standalone weather/endurance siblings.

**Near-miss ladder (near_miss_5 → near_miss_15):** reuse the EKG/heartbeat
**nerve spike** read but make it a purpose-built "thread through the needle."

- `near_miss_5` — **Close Shave** — a **razor passing a hair's-breadth gap**: two
  vertical pillar-edges with a thin bird-chevron threading the narrow gap between
  them, plus one sweat-bead tick. L1 (one bead). The "shave" read.
- `near_miss_15` — **Threadneedle** — a **needle with thread through its eye**
  (an upright needle, oval eye, a thread-loop passing through) — literal
  "threadneedle" — **L3** ray halo (15× nerves of steel). Count escalates 5→15 via
  a single bead → three beads along the thread.
- *Escalation ladder:* bird-through-gap+1bead → needle-and-thread+3beads+rays;
  shared theme = squeaking through an impossibly thin gap.

**Ceiling-bonk ladder (headbanger → hard_head):** reuse the **up-arrow striking a
ceiling bar** read (`_glyph_ceiling`), escalating the comedy of the bonk.

- `headbanger` — **Headbanger** — the up-arrow bonks a ceiling bar with **two**
  impact sparks (the existing motif), L0. (10× in one run.)
- `hard_head` — **Hard Head** — the ceiling bar is now **dented/cracked** by a
  blunt helmet-head shape ramming it, **four** impact stars + **L4** crownlet
  (200× all-time: the ceiling gives before the head does).
- *Escalation ladder:* arrow+2 sparks → helmet-head+dented-bar+4 stars+crown; the
  bonker upgrades from an arrow to an unbreakable head, the ceiling visibly damaged.

**Flap ladder (flap_life → iron_wings):** the **macaw wing** (`_glyph_wing`),
escalating from a feather wing to forged iron.

- `flap_life` — **Tireless Wings** — a single clean macaw wing (the existing
  `_glyph_wing`) with three short motion-streak ticks behind it (it's *flapping*).
  L1. (5,000.)
- `iron_wings` — **Iron Wings** — the same wing silhouette rendered as **riveted
  metal plates** (the feather lobes become 3 plate segments with a rivet-dot each)
  + **L4** crownlet. (50,000: forged.) Feather→armour is the escalation.
- *Escalation ladder:* feathered wing+motion → plated iron wing+rivets+crown; same
  wing arc, the material upgrades.

**Standalone siblings (genuinely distinct objects):**

- `marathon` — **Long Haul** — a **stopwatch mid-tick** (`_glyph_clock`'s
  crowned-dial read) with a "2:00" implied by the hand at the bottom and a small
  road/horizon dash beneath — endurance flight. Distinct from the clock used for
  shame/time by adding the running-road dash.
- `storm_rider` — **Storm Rider** — a **rain cloud with a lightning bolt** and
  three rain-streaks beneath (the existing storm bolt, reframed inside a cloud
  silhouette so it's clearly *rain*, not a bare bolt). Matches in-game rain weather.
- `snowbird` — **Snowbird** — a **six-arm snowflake with a tiny bird-chevron** at
  its center — the snow-squall biome. Bold 6-spoke flake (each spoke a thick line
  with one short branch tick). Matches in-game snow weather.
  - *44px risk:* snowflake branch-ticks vanish — Fallback: 6 bold spokes, drop the
    side-branches; the hexagonal-spoke read alone says "snow."
- *Distinctness:* needle/razor (near-miss) vs ceiling-bonk vs wing (flap) vs
  stopwatch+road (marathon) vs rain-cloud-bolt (storm) vs snowflake (snow) — six
  silhouette families across the nine.

---

## FAME — Skater (8)

Three tier families + standalone full-combo. Hero object: the in-game
**skateboard** (`_glyph_skate`) and **rail cart**.

**Skateboards-caught ladder (board_meeting → sponsored → going_pro):** the
skateboard deck gains rank dressing + sponsor marks.

- `board_meeting` — **Board Meeting** — ONE skateboard in profile (deck + kick-
  tails + two wheels), a small "caught" spark above it. L0. (Catch a board.)
- `sponsored` — **Sponsored** — the board now wears a **sponsor star sticker** on
  its deck + **L2** wreath ticks. (10 boards — a sponsor noticed you.)
- `going_pro` — **Going Pro** — the board is **airborne mid-ollie** (tilted, two
  motion-arcs under the wheels) with a **L4** crownlet — pro status. (50 boards.)
- *Escalation ladder:* grounded board → stickered board → airborne pro board +
  crown; rank L0→L2→L4; the board literally takes off as you rank up.

**Tricks-landed ladder (trickster → trick_legend):** a **trick-arc / rotation**
read, distinct from the board-catch ladder (this is *landing* tricks).

- `trickster` — **Trickster** — a **board doing a kickflip**: a board tilted 45°
  inside a curved rotation-arrow loop, with one landing-spark. L1. (50 tricks.)
- `trick_legend` — **Trick Legend** — the board inside a **full 360° rotation
  ring** with three motion-arcs and **L4** crownlet — a legendary spin. (500.)
- *Escalation ladder:* half-rotation kickflip → full 360 spin-ring + crown; the
  rotation completes as the count climbs.

**Rail-rides ladder (grinder → rail_baron):** the **grind rail + cart**
(`_glyph_rail`) gains rank.

- `grinder` — **Grinder** — the angled grind rail with a board mid-grind + two
  grind-sparks at the contact point. L1. (10 rides.)
- `rail_baron` — **Rail Baron** — the rail extends into a **mine-cart on tracks**
  (a small cart silhouette riding the rail, two cart-wheels) under a **L4**
  crownlet — baron of the rails. (50 rides.) Matches the in-game rail *cart*.
- *Escalation ladder:* board-on-rail+sparks → cart-on-rail+crown; the rider
  upgrades from a grinding board to a whole cart.

**Standalone:**

- `full_combo` — **Full Combo** — **four distinct trick-glyphs in a 2×2 cluster**:
  a kickflip-board, a rotation-loop, a grind-line, and a grab-hand — the four trick
  *types* as four mini-icons, ringed by a "COMBO" arc tick. The variety-of-four is
  the read (mirrors Buffet's structure but with skate-trick shapes, not food).
  - *44px risk:* four mini-trick-glyphs are tiny — Fallback: four distinct bold
    dots arranged in a chevron with one curved combo-arc over them (the *four
    different marks* read survives even if each isn't individually legible).
- *Distinctness:* board-profile (catch) vs rotation-loop (tricks) vs rail-cart
  (rail) vs four-trick-cluster (combo) — four silhouette families across the eight.

---

## FAME — Mysteries (6, amethyst)

Render amethyst; keep enigmatic. Each is its own secret object; lean into a
single bold, slightly mysterious silhouette (no busy detail — the amethyst well +
sparkle ring already do the "rare" work).

- `made_a_wish` — **Three Wishes** — the **genie lamp** (`_glyph_genie`) with
  **three small wisp-stars** rising from the spout (the three wishes). Enigmatic:
  the smoke forms a question-curl. Count = 3.
- `knighted` — **Knighted** — the **great-helm** (`_glyph_knight`) crossed by an
  **upright sword + small shield** behind it (survived under a knight's guard) —
  a guardian read, not just a helmet. The sword's cross-guard makes a subtle `+`.
- `treasure_hunter` — **X Marks the Spot** — an **open treasure chest with an X**
  on its lid and one gem-spark escaping (`_glyph_treasure` reframed: the lid is
  ajar, an engraved X across it). The "X marks the spot" literalised.
- `jackpot` — **Jackpot!** — a **lottery slot reel showing three matched
  symbols** (three small `$`/star pips in a row inside a slot-window frame) with a
  burst-star behind — the lottery top tier (matches `lottery_slot.py`). Distinct
  from the bare `_glyph_lottery` star by adding the slot-window frame.
- `rail_rider` — **Off the Rails** — a **mine-cart leaping off a broken rail
  end** (cart tilted, the rail snapping downward, motion-arc) — "off the rails"
  literalised, and clearly the rail-CART, not a board. Distinct from Skater's
  `grinder`/`rail_baron` (those are *on* the rail; this one jumps *off*).
- `poisoned` — **Be Careful What You Wish For** — a **skull rising from genie
  smoke**: the genie lamp's smoke-wisp curls UP into a small skull (the wish gone
  wrong). Ties to `made_a_wish` (same lamp-smoke origin) but resolves to a skull —
  the nasty surprise. Amethyst keeps it eerie.
- *Distinctness:* lamp+3wisps vs helm+sword vs X-chest vs slot-reel vs cart-off-
  rail vs smoke-skull — six silhouettes. The lamp recurs in `made_a_wish` and
  `poisoned` deliberately (wish vs cursed-wish) but the resolution shape (3 stars
  vs a skull) flips the read entirely.

---

## SHAME — Blooper Reel (9, tarnished)

Tarnished tone (cracked cool pewter + bronze drip + masked `✕` when locked). Each
glyph should read **bleak / ironic / comedic-fail**. Keep them bold; the tarnish
frame supplies the gloom, the glyph supplies the joke.

- `goose_egg` — **The Goose Egg** — a **big fat zero / egg** (`_glyph_egg`'s oval
  ring) with a tiny crack and a sad single drip-tick — "nothing at all." The
  hollow oval IS the zero. Keep it dead-simple; the emptiness is the joke.
- `icarus` — **The Icarus Award** — a **falling winged figure plummeting** (a
  small body-chevron with one melting/drooping wing trailing up, a downward motion-
  streak) — flew too close on pillar one. Distinct from Stormchaser's clean wing:
  this wing droops/sheds a feather.
  - *44px risk:* a figure+wing is busy — Fallback: a single drooping wing tilted
    downward with a downward arrow streak; the *falling* read carries it.
- `hummingbird` — **The Hummingbird** — a **blur of frantic wings**: a small bird-
  body with THREE overlapping wing-arcs fanned (motion-blur) + jitter-ticks —
  panic-flapping. The over-multiplied wings = the joke (vs the dignified single
  wing of `flap_life`).
- `denial` — **Denial** — a **ghost phasing INTO a wall**: a sheet-ghost
  silhouette (rounded top, scalloped bottom) half-overlapping a pillar edge, with
  a "thunk" impact-tick where it hits — phased around the gap into the wall. Eerie-
  comic. (Ties to the in-game Ghost power-up.)
- `kfc_incident` — **The KFC Incident** — the **fry bucket knocked over**, fries
  spilling out (`_glyph_kfc` tipped 30°, sticks scattering, a grease-splat tick) —
  died in fry mode. Same bucket as `greasy_fingers` but **upended** = the fail.
  Bronze box accent (the Shame dormant rule keeps it monochrome until earned).
- `so_close` — **So Close, So Far** — **fingers pinched a hair apart** (two
  pinch-fingertips with a tiny gap and a near-miss spark between) — "this close,"
  then died. The universal "so close" pinch gesture. Distinct from the nerve-spike
  near-misses by being a *hand*, not a pulse line.
  - *44px risk:* fingers are fiddly — Fallback: two short opposed bars with a 2px
    gap and a spark in the gap (an abstract "this much" pinch).
- `lottery_loser` — **The Lottery Loser** — a **slot reel showing three
  MISMATCHED symbols** (a `$`, a star, a skull — no match) with a downward sad-tick
  — pulled the slot, died before it paid. The deliberate *non-match* (vs jackpot's
  three-match) is the joke. Tarnished.
- `the_49er` — **The 49er** — a **broken/cracked pillar with "49" implied**: a
  single tall pillar snapped near the top, a tiny genie-lamp silhouette floating
  just beyond its reach (the genie at 50 you never got). "One short." Ties pillar +
  genie. The snapped pillar = the death; the unreachable lamp = the irony.
  - *44px risk:* a lamp + pillar + number is too much — Fallback: a snapped pillar
    with a small lamp-wisp just past its broken top; drop any numerals.
- `night_owl` — **Night Owl's Revenge** — an **owl-face with X-ed-out eyes** under
  a crescent moon (died in the first 5s of a new biome phase — the night got you).
  A round owl head, two small ear-tufts, two `✕` eyes, moon above. Comedic-bleak.
  - *44px risk:* owl detail + moon crowds — Fallback: a round owl face with two
    `✕` eyes + ear-tufts only; the crescent moon optional as a single arc top-left.
- *Distinctness:* egg vs falling-figure vs wing-blur vs ghost-in-wall vs spilled-
  bucket vs pinch-hand vs mismatch-reel vs snapped-pillar+lamp vs X-eyed-owl —
  nine distinct silhouettes. The wing recurs (icarus droop, hummingbird blur,
  flap_life clean) but each treats it oppositely.

---

## SHAME — Lifetime Lows (2, tarnished)

- `the_scrooge` — **The Scrooge** — a **`$` coin with a cobweb / a clamped
  miser's hand over it**: a `$` coin half-covered by a spiderweb-corner (flew past
  5,000 coins, took none — they gathered dust). The web on money = "never spent /
  never taken." Tarnished. Distinct from all Riches coins by the *neglect* cue
  (web/dust), not abundance.
  - *44px risk:* a cobweb is fine detail — Fallback: a `$` coin with three short
    radiating web-strands from one corner + one drip; the "untouched/dusty" read
    survives.
- `early_checkout` — **Early Checkout** — a **hotel "Do Not Disturb" door-tag /
  a checkout bell rung once**: a small counter bell with a downward "leaving"
  arrow and a tiny luggage-tag — bailed in under 3 seconds, 25× over. The bell +
  exit-arrow = "checked out immediately." Tarnished.
  - *44px risk:* bell + tag + arrow is busy — Fallback: a counter bell (dome +
    base + button) with a single bold down-arrow beside it = "rang and left."

---

## Cross-set visual language (the 57 as one family)

Every emblem is a single-colour engraved relief (lit body + down-right inset
shadow + up-left sheen) built from bold filled polygons, thick lines and discs —
no fine text, no sub-5px detail — so all 57 read as struck-metal siblings of the
same medallion family regardless of subject. Tier families never change their core
silhouette; they climb a shared **rank-dressing ladder** (pips → wreath ticks →
ray halo → crownlet, plus a literal count/container growth) so a glance reads the
rank, while non-tier siblings are bottom-up-distinct objects drawn from the game's
own props (sandstone pillars, the `$` coin, macaw wing, fry bucket, skateboard,
rail cart, genie lamp, knight helm, treasure chest, lottery reel, storm/snow,
day/night). Saturated accents (KFC red, magnet poles, the Midas gold gem) only
appear on unlock via `_accent`, and the two tonal sub-families — amethyst
Mysteries (enigmatic, single-shape) and tarnished Shame (ironic-bleak, the joke in
the silhouette) — stay legible against their special wells while sharing the exact
same engrave construction as the gold Fame emblems.

Sources:
- [Best practices for achievements and badges (LinkedIn)](https://www.linkedin.com/advice/0/what-some-best-practices-using-achievements-badges)
- [Game achievement badge/rank icon tier sets (Freepik)](https://www.freepik.com/vectors/achievement-badge-bronze-silver-gold)
