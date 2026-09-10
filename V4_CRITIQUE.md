# Skybit v4 — Outside Critique

> A senior casual-gaming veteran's honest read of the v4 build, focused
> on user experience and viral potential, grounded in 2026 mobile market
> reality. Methodology: full code walk of `game/`, `inject_theme.py`,
> `supabase/schema.sql`, and the CI pipeline; cross-reference with the
> maintainer's own `REVIEW.md`, `UPGRADE_BRIEF.md`, and
> `docs/POWERUP_BACKLOG.md`; web research on 2026 hyper-casual /
> hybrid-casual benchmarks and viral mechanics.

---

## 1. Executive Summary

**Headline:** Skybit is the most *taste*ful Flappy-clone I have played
in years. The procedural art, the difficulty ramp, and the first-30-
seconds onboarding are all *senior-grade* work. But the game ships
**zero viral surface area** and a **bare-bones retention loop**, so
its current ceiling is "respected portfolio piece," not "hit." Two
small interventions — a shareable run card and a daily seed — would
disproportionately move the needle.

| Category                  | Score | Why                                                   |
|---------------------------|------:|-------------------------------------------------------|
| Core mechanic / game feel | 9 / 10 | Tight physics, fair hitbox, no late cliff             |
| First 30 seconds (UX)     | 9 / 10 | Intro → menu → play in three taps, no friction         |
| Art / procedural identity | 9 / 10 | 8 pillar themes × 7 biome phases; cohesive            |
| Audio                     | 6 / 10 | Curated SFX, **no music layer**                       |
| Mid-run pacing            | 8 / 10 | Coin Rush every 15 pillars is a designer-grade beat   |
| End-of-run flow           | 7 / 10 | Clean, but **no share, no replay-card**               |
| Retention loop            | 4 / 10 | All-time leaderboard, no daily/weekly, no meta        |
| Virality                  | 2 / 10 | Nothing leaves the page. No screenshot, no deep link  |
| Accessibility             | 5 / 10 | No reduced-motion, no colorblind, no landscape         |
| Anti-cheat (declared)     | 7 / 10 | Honest "soft leaderboard" caveat; ledger + chain hash  |

**Ship call:** Hold the launch. You are *one weekend* away from a
materially better product. Land share-card + daily seed + one music
loop, and the next 30 days of organic reach are 3–5× what they would
be today.

---

## 2. The Game in 30 Seconds

You open `ytocker.github.io/skybit/`. A ~12-second cinematic plays:
dawn, a parrot named Pip picks up a parcel, flies through the day/
night cycle, delivers it home. Tap to skip if you want. Menu shows
one START pill. Tap. Pip flaps. You thread sandstone pillars, grab
golden `$` coins, collect 8-second power-ups (Magnet, Triple,
Slow-Mo, KFC, Ghost, Grow, Surprise). Every 15th pillar opens wide
and rains 14 coins in a wave/S/chevron/oval/double-arc. You die. You
see your stats. If you're top-10 you enter a name. You see the
leaderboard. You tap. You play again.

That loop is *very* well-built. The problem is it ends with the tap.

---

## 3. 2026 Market Context

A few things matter for where Skybit sits today:

- **Hyper-casual is no longer where the money lives.** Industry D7
  retention for pure hyper-casual sits around **8%**, D30 around
  **2–4%**. The category has consolidated around *hybrid-casual* —
  hyper-casual core loops *plus* layered progression — which is
  hitting **~16% D7** and is where the IAP/ad-blend revenue growth is
  happening.
- **Virality is the actual user-acquisition channel.** TikTok and
  Reddit screenshot/clip culture moves more installs than paid UA for
  most indie casual hits. Games that don't ship a shareable artifact
  (post-run card, replay clip, score badge) effectively opt out of
  organic acquisition.
- **D1 ≥ 30% is now the bar for "good"** for casual; top performers
  on iOS sit at **35–40%**. Industry median is ~26%. First-30-second
  UX is where you win or lose that number.
- **Web-first casual on a free GitHub Pages link** is a perfectly
  legitimate distribution path *if* the share loop pulls people back
  in. Without one, every visitor is a dead end.

Skybit is sitting on the right side of the D1 line and the wrong
side of every other one.

---

## 4. Strengths — Where Skybit Is Best

### 4.1 First 30 seconds — A grade

`STATE_INTRO → STATE_MENU → STATE_PLAY` is a three-tap path with
zero modal friction (see `game/scenes.py:299` onwards). The intro
(`game/intro.py`) is 12–15s, **plays once per launch**, and is
skippable from frame one. The menu is *one button* — `START` — at
a comfortable thumb-target size. The first tap on START doubles as
Pip's first flap, so the player launches into motion with no dead
moment. That's a deliberate design choice and a senior one.

This matches the 2026 onboarding best practice: teach by playing,
not by telling. There is *no* tutorial wall, but there is an
auto-launched `PowerUpHelpScene` after the intro that the player can
tap through in <5s if they want to.

### 4.2 Difficulty curve — designer-grade

Read `game/config.py:137–148` and `game/world.py` (`_lerp`,
`_ramp_t`). The first 5 pillars are a flat "plateau" at
`GAP_NEWBIE_START = 225 px`, `SCROLL_NEWBIE_BASE = 125 px/s`,
`PIPE_SPACING_NEWBIE = 370 px`. Then over the next 20 pillars an
ease-out curve `1 − (1 − x)²` tightens to the regular tuning
(`GAP_START = 170`, `SCROLL_BASE = 160`, `PIPE_SPACING = 280`). And
then — and this is the crucial part — *it stops*. The unused
`GAP_MIN = 115` and `SCROLL_MAX = 290` slots in `config.py:13,18`
sit there as a deliberate non-choice. There is **no late-game
cliff**. The game does not punish skill with arbitrary tightening.

Forgiveness gestures back this up: the ceiling clamps Pip instead
of killing him (only the ground kills, `world.py`); the pipe hitbox
is `BIRD_R − PIPE_HITBOX_SHRINK = 14 − 4 = 10 px` while the visible
bird is 14 px, so brushes don't count (`config.py:129`). Dying
mostly feels like "I *almost* made it," which is the right death
vibe for retention.

### 4.3 Art identity — cohesive and elevated

This is not a Flappy clone visually. It's something more like a
casual Monument-Valley-adjacent thing in 1-bit ambition:

- **8 pillar silhouette pairs** and **8 decoration themes**
  (prayer flags, banner poles, monasteries, hanging lanterns,
  strangler figs, masonry, menhirs, cascading vines), each with
  density that scales to the gap height so cramped gaps don't
  clutter (see `game/pillar_variants.py` + the theme functions in
  `game/draw.py`).
- **7-keyframe biome cycle** over 320 seconds — day → golden hour
  → sunset → dusk → starry night → predawn → sunrise → loop —
  with smooth-step interpolation and 32 cache buckets so sky
  re-renders are cheap (`game/biome.py`). Stars fade in (~130 alpha
  at dusk, ~235 at deep night). Mountains parallax in three depth
  layers.
- **Pip variants** (`game/parrot.py`): 4-frame wing animation, plus
  KFC, Ghost, Top-Hat (Triple) and combination skins. The 1-pixel
  outline added at boot is a deliberate fix for tracking the bird
  on warm sunset stone — a fix `REVIEW.md` already documents
  honestly.
- **Procedural coin glyphs** (`game/dollar_coin_glyphs.py`),
  procedural surprise-box ribbons (`game/surprise_box_variants.py`),
  procedural KFC fries (`game/kfc_fries.py`) — the procedural-art
  hard-rule from `CLAUDE.md` is enforced and pays off.

This is the kind of art language that *screenshots well*. The
problem is that screenshots aren't actually offered to the player.

### 4.4 Coin Rush — pacing intelligence

Every 15th pillar (`COIN_RUSH_INTERVAL`, `config.py:32`) widens the
gap 30% (`COIN_RUSH_GAP_BOOST = 1.30`) and packs 14 coins in one of
five formations — wave, S-curve, chevron, oval, double-arc, picked
fresh per rush. Power-ups don't spawn during a rush. This is a
*breather* + *reward* + *photo moment* all at once. With Magnet
active it vacuums; without, it's a pure skill flex. That cadence —
~62s between rushes at base scroll — gives every minute of play a
predictable peak, which is exactly the rhythm you want for clip-
worthy moments.

### 4.5 Honesty as a feature

The anti-cheat (`game/_proof.py`'s append-only event ledger + rolling
SHA-256 chain hash; `game/_plausibility.py`'s 10,000-score ceiling
applied both on submit *and* on read) is good. More importantly, the
README and `REVIEW.md` *tell you* it's a soft leaderboard — that a
motivated attacker can `curl` the Supabase table. That kind of
disclosure builds maintainer credibility in a way mobile-casual
rarely sees. Keep it.

---

## 5. Weaknesses — Where Skybit Needs Work

### 5.1 Virality — F grade

I grepped the entire repo for `share`, `screenshot`, `twitter`,
`tiktok`, `whatsapp`, `invite`, `deep[-_.]link`. **Zero hits in
runtime code.** Every match was a code comment about "shared
helpers." This is the single biggest gap.

The end-of-run flow (`game/scenes.py:710–773`, `game/hud.py`'s
stats and leaderboard screens) is information-dense and clean, but
it terminates at "tap to play again." There is no:

- Share-as-image button on the stats card
- "Copy link" with embedded score / run UUID
- Auto-snapshot of the death frame
- Tweet / Reddit / TikTok intent URL
- QR / friend-invite link

A `tools/gen_run_summary_redesigns.py` design exploration in `docs/`
mocks a "Bottom CTA — primary pill + share button," but no share
button code ships. The intent is there. The execution isn't.

A player who hits a 500-pillar run in 2026 expects to be one tap
away from posting it. Skybit makes them screenshot the screen, crop
it, find the URL to paste underneath, and hope their friend bothers
to click. That friction is fatal for organic spread.

### 5.2 No music — Sound 6/10

`game/audio.py` ships 13 curated CC0 OGG SFX (flap, coin,
coin_triple, magnet, slowmo, thunder, death, gameover, poof, ghost,
grow — plus wrappers reusing the same files for shrink/rail/lottery).
Voice limiter caps high-frequency events at 2 concurrent channels so
14-coin rushes don't muddy. That's all good.

What's missing: a music layer. Long runs (~3 minutes) play against
silence + ambient weather. `REVIEW.md` already flags this as the
single biggest "feels like a prototype" signal. Four short looping
pads — one per biome quadrant (day / sunset / night / sunrise),
crossfading on `biome.py`'s `phase` — would lift the perceived
production value of the entire game by a full point.

### 5.3 Retention loop — 4/10

Skybit's retention loop today is:

> Play → die → see score → optional leaderboard → tap → play again.

That's it. The leaderboard is **all-time global, anonymous-or-named,
top-10** (`supabase/schema.sql`'s `public.scores` with permissive
RLS). There is no daily reset, no weekly bracket, no friend filter,
no streak counter shown to the player, no unlockable cosmetic, no
achievement vocabulary, no quest, no rotating modifier. `near_misses`
is tracked per-run in `world.py`'s stats and shown in the post-run
summary, but never used as a currency or progression signal.
`POWERUP_BACKLOG.md`'s "Bravado" concept (score 9/10) sits ready in
the design doc but unbuilt.

The current loop is fine for a single sitting. It gives a returning
player no reason to come back tomorrow. In hyper-casual terms,
Skybit is optimised for the install, not the resurrection.

### 5.4 Accessibility — 5/10

`REVIEW.md` already lists these. The headline gaps:

- **No reduced-motion toggle.** Lightning flashes (`weather.py`),
  screen shake (death = 8 px / 0.45 s; magnet = 2.5 px / 0.25 s),
  and the 14-coin particle bursts can trigger photosensitive
  players.
- **No colorblind mode.** Red Pip on green-vine pillars at dusk is
  borderline failure-of-readability for ~5% of male players.
- **No text scaling.** HUD is fixed pixel sizes.
- **No landscape.** The game is portrait-only (`W=360, H=640`).
  Tablet players, accessibility-tool users, and laptop browser
  visitors all get a tall thin column with whitespace gutters.

### 5.5 Mobile sprite readability at thumb scale

This is subtle but real. Several procedural sprites are tuned for
the 64-px sprite canvas and compress poorly when downscaled to a 6"
phone's effective gameplay viewport:

- The **KFC bird's** 12–15 crackle spots blur into a tan blob.
- The **Surprise Box's** five ribbon layouts collapse to "red
  square" at the in-game 28 px power-up footprint.
- The **dollar coin glyph** loses its embossed depth at small
  sizes.

None of this is broken — Pip stays distinguishable in motion — but
all of this matters when a viewer is watching a 5-second clip on a
phone screen at 1/3 size.

### 5.6 Power-up HUD: implicit, not explicit

When Triple is active, the player has no on-screen badge saying
"TRIPLE — 6s." Active power-ups are signalled by world-tinting
(Slow-Mo desaturates, Ghost cools, KFC repaints), but a brand-new
player won't connect "I see a tint" with "my next coin is worth
+3." A small icon strip in the HUD corner with a countdown ring per
active buff would be a 1-day win.

### 5.7 38-px pause button is borderline

`PauseButton` in `game/hud.py:965` sits in the top-right at ~38 px
diameter. On a 6" phone that's about 10% of screen width, comfortably
*above* the 44-px Apple HIG recommendation only if you're including a
generous touch margin. For thick thumbs, it's a near-miss target.
This is a one-line fix.

### 5.8 No app-store reach

Web link is fine, but it's the *only* path. No itch.io publish, no
TWA wrapper, no Capacitor build for the App Store / Play Store. The
maintainer might intentionally not want that, but if "viral" is the
goal, the install-on-home-screen ladder matters.

### 5.9 No monetization scaffolding (intentional)

Zero ads, zero IAP, zero cosmetic shop. Not a flaw if the goal is
portfolio/hobby. Worth naming so any future "should we monetize"
conversation starts from facts. The natural path if you ever wanted
to is cosmetics — Pip skins unlocked by play-count, with a single
optional skip-grind tier — which the game's existing parrot-variant
infrastructure (`game/parrot.py`'s combinator scheme) would support
cleanly.

---

## 6. UX Deep Dive

### 6.1 First 30 seconds — annotated

- **t=0–3s:** Tab loads. Splash overlay (`inject_theme.py`)
  while WASM warms. Web-Audio is gated to a user gesture.
- **t=3–4s:** Intro cinematic starts. Dawn → parcel handoff → flight
  → arrival → "TAP TO FLY" logo. Skip on any tap.
- **t=4–6s:** Menu state. Single START pill, sized ~220 × 66 px —
  comfortable thumb target.
- **t=6s:** First tap = START + first flap. Pip launches.
- **t=6–25s:** Plateau zone. Five pillars at 225 px gaps, 125 px/s
  scroll. The game is teaching you flap rhythm with a wide margin.
- **t=25–60s:** Ramp zone. Gap and speed ease toward regular tuning.
  This is where most first-runs end.

Verdict: this is the right shape. I would only add **a single
animated arrow on the first menu visit** pointing at the START pill
the moment it appears, decaying after 2 seconds. New players on
mobile sometimes need the affordance.

### 6.2 Mid-run friction

None worth fixing. Coin Rush works. Power-up stacking works (each
buff has its own timer, no mutual exclusion except the deliberate
Magnet→Megamagnet swap at score 250 in `config.py:122`). Slow-Mo
scales world tick but not bird input, which is the correct call.

One small win: when **Surprise Box** resolves to one of the six base
power-ups at pickup time (`world.py`'s `_on_powerup`), the player
gets a float-text reveal but no extra "*rolled*" beat. A 200 ms
shimmer-then-resolve animation would make the gambling moment feel
*much* better. The `lottery_slot.py` already in the repo proves the
maintainer knows how to do this.

### 6.3 End-of-run friction

The flow `Death → Stats → optional Name Entry → Leaderboard →
Restart` is clean, but it does the **wrong thing emotionally** at
the moment of peak emotion. The player just died with a memorable
near-miss. The game responds by showing a database table. What it
*should* show is a single hero card with the player's run summary
designed for screenshot — score, pillars, coins, biome reached,
near-misses, longest power-up chain — and a SHARE button. The
leaderboard can be one tap behind that.

This is the highest-leverage change in the whole game.

### 6.4 Portrait-only

Decision is defensible — phones are portrait, taps are vertical —
but it does limit tablets and the (large) population of desktop
browser visitors who'd rather not maximize a 360×640 column. A
"fit-to-window with letterboxing" toggle would cost nothing and
double the surface area on big screens.

---

## 7. Audience Fit

**Today's audience.** Flappy Bird nostalgic players, indie-game
curious folks who appreciate craft, fellow developers, and people
who clicked a link on a portfolio. Average session: 5–15 runs over
one sitting. Returning rate: probably <10% beyond week one based on
the absence of any return-day signal.

**Adjacent audience you could win with small changes.** Commute
casual — the "I have 90 seconds at a stoplight" crowd that drives
the actual casual mobile market. They want: instant load, instant
restart, a daily reason to come back, and something to share. Skybit
has the first two. It needs the second two.

**Audience you will never serve.** Console / Steam / landscape
tablet players. Gamepad users. Controller-first audiences. That's
fine. Don't try.

---

## 8. Virality Diagnosis

The maintainer asked specifically about virality. Here's the
diagnosis in one paragraph:

> Skybit doesn't go viral because every viral artifact ends at the
> tab close. The game generates beautiful, screenshot-worthy moments
> (a starry-night Coin Rush with Ghost active, Pip silhouetted
> against a sunset pillar, a near-miss frame with the bird 2 pixels
> from a pillar edge) and *throws them all away* the moment the
> player dies. There is no share card, no replay clip, no permanent
> URL for a specific run, no friend-callout, no daily seed, no
> brag-able streak. A player has no surface on which to brag and a
> friend has no surface on which to be summoned. That's the whole
> problem.

Concrete interventions, in rough order of impact:

1. **Post-run share card** — a single procedurally-composed PNG
   blob: Pip's death frame, score, pillars, biome, top power-up.
   Web build calls `canvas.toBlob()` via the existing `__sk`
   dispatcher and offers Web Share API where available, falls back
   to copy-link + download. Native build writes to clipboard.
2. **Daily seed** — same RNG seed for everyone every day, displayed
   under the score (`DAY 7 · #42`). One leaderboard per day. Top-10
   per day. Resets at UTC midnight. Anyone clicking a daily-seed
   link enters that day's run.
3. **Deep-link run URL** — every submitted score gets a
   `?run=<uuid>` URL that opens a leaderboard scrolled to that row,
   with the player's name highlighted. Use the run UUID that's
   already in `game/_proof.py`'s ledger.
4. **Ghost-of-best-friend ribbon** — if the URL had a `?ghost=`
   param, render a translucent silhouette of that player's death
   position at every pillar. Doesn't replay them, just shows where
   they died. Asynchronous competition in 50 lines of code.
5. **Streak counter on the menu** — "Day 4 of 7." Two days in a
   row plays = badge. A week = different badge. Local-only is fine
   for v1.
6. **Music** — see §5.2. Improves clip-shareability of every
   recorded moment.

If you ship #1 and #2 in a weekend, the next 30 days of organic
reach are 3–5× what they would be today, assuming any baseline
traffic at all. If the game has no baseline traffic, it doesn't
matter what you ship.

---

## 9. Top 10 Prioritized Recommendations

| # | Recommendation                          | Impact | Effort  | Where                                                    |
|--:|-----------------------------------------|:------:|--------:|----------------------------------------------------------|
| 1 | Post-run share card + Web Share API     | **H** | 2 days  | `game/hud.py` end-of-run, `inject_theme.py` JS bridge     |
| 2 | Daily seed + daily leaderboard          | **H** | 2 days  | `game/world.py` RNG, `supabase/schema.sql` day-partition  |
| 3 | One music loop per biome quadrant       | **H** | 1 day   | `game/audio.py`, OGG assets in `game/assets/sounds/`      |
| 4 | Active-power-up HUD strip (icon + ring) | **M** | 1 day   | `game/hud.py` `draw_play`                                 |
| 5 | Bigger pause button (48–56 px)          | **L** | 10 min  | `game/hud.py` `PauseButton`                               |
| 6 | Reduced-motion + colorblind toggles     | **M** | 1 day   | new options scene, gates in `weather.py` and palettes     |
| 7 | Deep-link run URLs (`?run=<uuid>`)      | **M** | 1 day   | `game/leaderboard.py`, `inject_theme.py`                  |
| 8 | Surprise Box reveal-shimmer animation   | **L** | 0.5 day | reuse `game/lottery_slot.py`                              |
| 9 | Streak counter on menu                  | **M** | 1 day   | `game/scenes.py` menu, persisted via `SAVE_FILE`          |
| 10 | Cosmetic Pip skins unlocked by playcount | **M** | 3 days  | `game/parrot.py` combinator already supports it           |

(Effort estimates assume someone fluent in this codebase. Real
elapsed time depends on review cadence.)

---

## 10. Verdict & Ship Call

Skybit at v4 is a **8.0 / 10** game in mechanic, art, and
onboarding craft, and a **3.0 / 10** game in 2026-market viability.
The gap is almost entirely about surfaces *outside* the core loop.

If the goal is *portfolio piece*: ship it as-is. Add music. Done.

If the goal is *viral hit*: do not ship until #1 (share card) and
#2 (daily seed) are in. Without them, every visitor is a dead end,
and you cannot recover from that with paid UA on a hobby budget.

If the goal is *commercial release*: rebuild the retention loop
first (meta-progression, daily quests, cosmetics), wrap in a TWA for
Play Store, and accept that you have entered a different game.

The good news: Skybit is *not* one of those games where the bones
are wrong. The bones are excellent. It needs a face the world can
see.

---

*— Outside review, May 2026.*
