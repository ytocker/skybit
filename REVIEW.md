# Skybit — Project Review

> A comprehensive end-of-project review of **Skybit: Pocket Sky Flyer** — a
> Pygame casual flyer built with procedural art, procedural difficulty, and
> a tamper-evident leaderboard. Scoring uses a 1–10 scale, with anchor
> definitions adapted from GamesRadar+, The Indie Game Report (TIGR), and
> the rubric work surveyed in the "References" section.

| Field           | Value                                       |
|-----------------|---------------------------------------------|
| **Title**       | Skybit — Pocket Sky Flyer                   |
| **Genre**       | Casual arcade / Flappy-style sky flyer      |
| **Platform**    | Web (pygbag/WASM) + native Python desktop   |
| **Engine**      | Python 3.11 + Pygame 2.x                    |
| **Codebase**    | ~13,000 LOC Python, 7 unit tests (all green) |
| **Status**      | Late-stage, near release                    |
| **Review date** | 2026-05-11                                  |

---

## 1. Scoring framework

The review evaluates 12 categories, each scored 1–10. Industry rubrics
(GamesRadar+, Game Informer, IndieGameReport "Fairway") generally agree
on a common set of axes — **gameplay**, **controls**, **visuals**,
**audio**, **content/replayability**, **performance**, **accessibility**,
and **originality** — with weighting that depends on the game's design
focus. Because Skybit is a one-button casual flyer, gameplay feel,
controls, and replayability are weighted highest in the final summary;
narrative is omitted (not applicable). A "software craftsmanship" axis
is added because the codebase is part of the deliverable.

**Score anchors (1–10):**

| Score | Meaning                                                                  |
|------:|--------------------------------------------------------------------------|
| 10    | Exceptional, defines the bar for the genre                               |
| 9     | Excellent, near-best-in-class with one or two small gaps                 |
| 8     | Great, clearly above-average, would recommend                            |
| 7     | Good, solid execution with notable but bounded weaknesses                |
| 6     | Above-average, enjoyable but with clear rough edges                      |
| 5     | Average, functional but unremarkable                                     |
| 4     | Below average, frustrating or generic                                    |
| 1–3   | Broken, unenjoyable, or fundamentally flawed                             |

---

## 2. Category scores

### 2.1 Gameplay & Core Loop — **8.5 / 10**

Skybit nails the "one more round" Flappy loop. The 1-second `TAP TO FLY`
freeze at run start is a small but disciplined choice — it gives the
player free trial taps before pillars enter the danger zone, which is
exactly the on-ramp Dong Nguyen famously baked into the original Flappy
Bird. The procedural opener (pickup-cottage drifting off-screen left
over the first ~2.5 s) is a charming touch that integrates the cinematic
intro with gameplay rather than cutting hard.

The seven power-ups (six active + a re-rolling Surprise Box) add a
meaningful second-tier decision layer the original Flappy Bird never
had: **do I dive into that gap to grab the Magnet, or stay safe?**
That's a genuinely new tension on top of the tap-rhythm core. The
**Coin Rush** every 15th pillar is a great "treat" beat — the gap is
widened 30% so it's actually catchable, and the 14-coin formation
varies between sine / S-curve / chevron / oval / double-arc so it
doesn't get stale.

What keeps this from a 9: the difficulty doesn't ramp (gap and scroll
speed are constants — `GAP_START = 170`, `SCROLL_BASE = 160`). Variety
comes from pillar silhouettes and coin rushes, but a long run can feel
flat once you've internalized the rhythm. A subtle speed-up curve, or
unlock-gated harder gaps, would lift this to "excellent".

### 2.2 Controls & Feel — **9 / 10**

The control surface is *correct*: **Space / Up / W / click / tap** all
flap. Inputs are deduplicated through `scenes.py`'s cooldown gate, so
the menu-tap → first-flap cascade doesn't fire two flaps on one finger
press (commits `36c9e87`, `7b...` show this was actively debugged into
shape). Physics are constants in `config.py`: `GRAVITY = 1600 px/s²`,
`FLAP_V = -520 px/s`, `MAX_FALL = 700 px/s`. **Fixed timestep at 60 FPS**
makes the tap feel identical on web and desktop, which is the single
biggest control-feel deliverable in this genre.

Two specific polish details that earn the high score:

1. **Downward tilt capped ≈ 41°** so fast falls don't visually
   pre-announce a crash the player hasn't actually committed.
2. **Slow-Mo scales the world but not Pip's input physics** — taps stay
   crisp while the obstacles crawl. That's a non-obvious gameplay
   decision that respects player agency.

Half-point off: there's no rebindable input layer and no controller
support (Switch/Steam Deck would love this game).

### 2.3 Visuals & Art Direction — **9 / 10**

This is the project's strongest axis. Everything is **drawn procedurally
in Python** — no sprite sheets, no PNG assets — using SRCALPHA surfaces,
BLEND_ADD glows, smoothscale super-sampling, and pre-computed
gradient/glow caches. Highlights:

- **Pip the macaw** is a 4-frame procedural sprite, with full variant
  re-skins for KFC mode (fried-chicken parrot), Ghost mode (holographic
  foil), Grow mode (1.5× cached parrot), and Triple mode (top-hat).
- **Eight sandstone pillar variants** with distinct silhouettes —
  prayer flags, banner poles, terraces with cascading vines,
  monasteries, hero lanterns, jungle-ruin masonry, menhirs. Picked per
  spawn from a seed.
- **Continuous day → golden hour → sunset → dusk → starry night →
  pre-dawn → sunrise → day** biome cycle over 5 minutes of gameplay,
  with the pillars and clouds re-tinted per phase. This single feature
  carries enormous mileage — a 90-second run actually looks visually
  different from minute 1 to minute 2.
- **Power-up float text** uses unified gradient-fill + auto-derived
  outline + 8 deterministic sparkle dots so the six different labels
  feel like a family.
- **Anti-aliasing via perimeter-stroke on 8–16× supersampled canvases**
  is a level of attention you don't see in 99% of game-jam casual
  flyers.

Minor docks: a few of the pillar variants (e.g. the green-vines pillar
in `01_start_between_pillars.png`) read busier than the cleaner
sandstone ones, and the menu logo's outlined-block font, while
on-brand, can feel a touch heavy against the soft-glow background.

### 2.4 Sound Design — **7.5 / 10**

The audio pipeline is more impressive than the audio itself. Two
backends:

- **Native:** `pygame.mixer.Sound` plays curated CC0 OGG samples, with
  a per-event voice limiter (e.g. `coin` capped at 2 concurrent
  channels) so a 14-coin Coin Rush doesn't mud.
- **Browser:** Every `play_X` call routes through `window.skyPlay`
  (Web Audio), because pygame's mixer isn't available under emscripten.

Both paths **fall back silently** when the audio device can't open
(headless snapshots, missing JS bridge) — a small but professional
detail.

On the actual sound: cues are distinct (flap whoosh, coin pickup,
mushroom fanfare, magnet shimmer, slow-mo descending tone, ghost pad,
grow chime, KFC poof, thunder, death sting), and the pitch-climbing on
3× chains was removed when it became uncomfortable — a tasteful choice
that not every dev would make.

Why not higher: there's no music layer, only SFX, so a long run plays
out against ambient silence + weather. A subtle looping ambient pad
that crossfades with biome phases would lift this category to a 9.

### 2.5 Replayability & Hook — **8 / 10**

The Flappy genre is inherently replayable — runs end fast, the failure
state is unambiguous, and "one more try" is the default reaction. Skybit
amplifies that with:

- **Global top-10 leaderboard** (Supabase) on the web build, with
  per-run leaderboard highlight when you place.
- **Run summary screen** (time alive, coins, pillars cleared, max
  combo, near misses, power-ups picked) gives the player a richer
  vocabulary of self-improvement than just "score".
- **Coin Rush every 15th pipe** is a long-run reward — players who
  reach 30, 45, 60 pillars get a visible payoff.
- **Power-up variety** changes what each run *feels* like, even when
  the underlying pillar pattern hasn't changed.

What's missing for a 9: there's no meta-progression (no unlockable Pip
skins, no daily challenge, no achievements). Casual flyers like Alto's
Adventure use unlockable characters to extend retention past the first
hundred runs.

### 2.6 Originality — **8 / 10**

The premise is unapologetically Flappy — that's the genre, not a flaw.
Where Skybit earns originality points:

- **Scarlet macaw with aviator sunglasses carrying a parcel** is an
  unmistakable identity. Pip is not a generic bird.
- **Six themed power-ups** (Triple, Magnet, Slow-Mo, KFC, Ghost, Grow)
  on top of a Flappy core is uncommon — most clones add coins and stop.
  The **KFC bucket pillar variants** are a genuinely funny detail.
- **Procedural-only art pipeline** (no PNG sheets, no audio asset
  files originally — the README still mentions the procedural-wave
  history) is itself a creative constraint that paid off visually.
- **Tamper-evident proof-of-play ledger** with SHA-256 chain hashing
  is overengineering for a casual flyer, in the best way. Almost no
  Flappy clone has even tried.

### 2.7 UI / UX & Onboarding — **8.5 / 10**

The state machine is well-thought-out: **Intro → Menu → Play → Pause /
Stats → Name Entry → Leaderboard → Game Over**. The intro is **once-
per-launch** (not per-run, which would be punishing) and skippable on
any tap. The menu is three stacked pills (`TAP TO START` / `HOW TO
PLAY` / `POWER-UPS`) so a first-time player can read about the game
without committing to a death.

UI details that show care:

- The HUD `BEST` and `coin` pills **fade out when Pip enters the
  upper 60 px** so the sprite isn't occluded by chrome.
- The score sits on a soft dark-gradient ellipse so digits stay
  legible across any biome.
- Active power-up timer rows stack at the top with **low-time pulse
  rings** on high-priority bars — readable at a glance.

Half-point dock: the `TAP TO FLY` prompt overlaps with `PAUSED` text in
the pause screenshot (`03_pause.png`), and the name-entry 3-letter
keyboard, while charmingly arcade-styled, is slow on mobile compared
to a system text-field.

### 2.8 Accessibility — **6.5 / 10**

The bar in 2026 has been raised by GAconf and Microsoft's gaming
accessibility guidelines. Skybit gets the basics right:

- **Single-button input** is one of the most accessible control
  schemes possible.
- Multiple equivalent keys (Space / Up / W / click / tap) cover most
  input devices.
- High-contrast UI gradients on dark-ellipse backings.

What's missing:

- No colour-blind mode (the red Pip + green vines pillar can blur for
  deuteranopia).
- No reduced-motion option (the screen shake on death, sparkle
  bursts, and biome glow could be a problem for photosensitive
  players).
- No text size scaling.
- No subtitle / sound-cue redundancy (the thunder cue has no visual
  counterpart for deaf players).

### 2.9 Performance & Technical Execution — **9 / 10**

The performance story is genuinely impressive:

- **Procedural-art caching:** Sprites with non-trivial draws (ghost
  body, magnet U-shape, coin face, KFC logo, surprise box) are built
  once at first use and cached at module level. Per-frame cost is one
  blit. The README calls this out explicitly.
- **Fixed-timestep 60 FPS** with a clean integration step.
- **Dual-target build:** native Python + pygbag WASM browser. The
  audio path branches via `sys.platform == "emscripten"` cleanly, and
  the leaderboard does an explicit startup probe so a Python↔JS
  bridge regression surfaces in the browser console on page load
  rather than at first death.
- **Graceful degradation:** the audio module is a silent no-op when no
  device is available; the error path in `main.py` *paints the
  traceback onto the canvas* so pygbag isn't a silent gray rectangle.

The only reason this isn't a 10: I can't independently benchmark FPS
on a low-end Android device in this review environment. The
`COEP/COOP` headers in `netlify.toml` show the team has already wrestled
with iOS Safari freezes and switched away from SharedArrayBuffer, so
mobile is clearly a tested target — but I'd want a frame-time chart on
a 2020-era Pixel before declaring this perfect.

### 2.10 Software Craftsmanship — **8.5 / 10**

Reviewing the codebase itself (not just the game it produces):

**Strengths:**
- **~13,000 LOC, modular layout.** `game/config.py` holds every tuning
  constant. `game/world.py` is the sim, `game/draw.py` is the low-level
  graphics, `game/hud.py` is the UI, etc. Names are honest.
- **7 unit tests** (`tests/test_plausibility.py`) covering the anti-
  cheat plausibility model — happy path, score inflation, impossible
  pacing, chain hash mismatch, score-above-ceiling, invalid coin
  dscore, and a pinned negative case for self-consistent forgeries.
  All pass on `python -m unittest` cleanly.
- **Comments explain WHY, not WHAT.** Every non-obvious decision has a
  short doc paragraph explaining the rationale (e.g. why the pitch-
  climbing was removed, why COEP was dropped, why a separate ledger
  exists). Future-Claude (or a human maintainer) inheriting this
  codebase will be unblocked fast.
- **Anti-cheat layer is honest.** `_proof.py` and `_plausibility.py`
  explicitly document what they *don't* protect against (a determined
  reverse engineer with Pyodide DevTools), and the README spells out
  the "soft leaderboard" caveat. This is the right level of paranoia
  for a casual game.
- **Tools directory** has 24 utility scripts (preview renderers,
  diagnostic snippets, sound-candidate generation) — the asset
  pipeline is reproducible.

**Weaknesses:**
- **Several files are very large.** `entities.py` is 1,664 LOC,
  `intro.py` is 1,404, `hud.py` is 1,071, `world.py` is 823. These
  could be split (e.g. each power-up sprite into its own module).
- **Test coverage is narrow.** Only the plausibility model is tested.
  The physics integrator, the world spawner, and the HUD state
  machine have no unit tests. A regression in `World._step` would
  ship.
- **Some module-level mutable caches** (`_grow_parrot`,
  `_surprise_sprite`) are global state. Fine for a single-window
  game; would break if the engine were ever embedded twice.

### 2.11 Anti-cheat & Online Hygiene — **8 / 10**

This is a casual leaderboard, but the team built it like a security
project, and it shows.

- **Closure-private dispatcher** (`window.__sk`) — no
  `lbSubmitStart` / `lbFetchStart` globals exposed to the console.
- **Tamper-evident proof bundle** with per-run UUID, append-only
  event ledger, rolling SHA-256 chain hash. The JS bridge recomputes
  the chain before submission and refuses mismatches.
- **Submitted score is the ledger sum**, not `world.score`. Patching
  `world.score = 99999` in DevTools has no effect.
- **Plausibility check** runs on both submit and read paths — rows
  above `MAX_PLAUSIBLE_SCORE = 10_000` are filtered from the displayed
  top-10.
- **Replay protection:** consumed run UUIDs are tracked in a
  closure-private set, so a captured legitimate submission can't be
  replayed.

The README is admirably honest about what this does *not* defeat: a
determined attacker who reads the JS bundle can post forged rows via
`curl`. Without a server to validate, that's unavoidable. Two more
honest points to make would push this to a 9: **rate-limiting** at the
Supabase RPC layer (Postgres function with a per-IP throttle) and a
**reproducible run replay** on the server side. Both are out of scope
for the current build.

### 2.12 Documentation & Project Hygiene — **9 / 10**

The `README.md` is **381 lines of solid documentation**: project
intro, run instructions, scoring table, per-power-up descriptions with
sprite previews, coin rush rules, sound list, biome / scenery
explanation, leaderboard architecture, anti-cheat caveat, game-state
diagram, technical notes, file-by-file directory listing. The
`docs/screenshots/` tree preserves the exploration sets for ghost /
magnet / reverse variants as a visual changelog.

The commit history (last 30 visible) tells a coherent story —
iterative menu redesigns, the intro rework, the KFC bucket
investigation. Each commit message says *what* and often *why*. No
"wip" / "fix stuff" noise.

Half-point dock: no `CONTRIBUTING.md`, no architecture diagram (the
state-machine description in the README is text-only), and the
`supabase/schema.sql` notes it's a "reference doc — not run
automatically by any build step", which is fine but means a fresh
deployer has to do that step by hand without a checklist.

---

## 3. Aggregate score

Unweighted mean across 12 categories:

```
(8.5 + 9 + 9 + 7.5 + 8 + 8 + 8.5 + 6.5 + 9 + 8.5 + 8 + 9) / 12 = 8.29
```

**Final: 8.3 / 10** — Great. A clearly above-average casual flyer with
some best-in-class craftsmanship beats (procedural art pipeline,
anti-cheat layer, dual-target build) held back from "excellent" by
missing meta-progression, no music, and a thin accessibility layer.

A weighted score that emphasizes gameplay / controls / replayability
(the genre's load-bearing axes) lands at **8.4** — essentially the
same. The headline figure should be **8.3 / 10**.

---

## 4. Strengths to keep

1. **Procedural-art pipeline as constraint.** No sprite sheets forced
   strong design decisions and produces a unique visual identity.
2. **Biome cycle as variety driver** is doing more work than any other
   single feature — keep this front and centre on the marketing page.
3. **Honest anti-cheat layer.** Most casual games either skip it or
   pretend the leaderboard is "secure". Skybit ships the right
   compromise and tells the user about it.
4. **Dual-target build (native + WASM)** with one codebase. Get this
   on itch.io and Steam (via Pygbag-as-Tauri) at the same time.
5. **Documented commits.** This codebase is genuinely maintainable.

---

## 5. Recommendations for shipping

In priority order:

1. **Add a difficulty curve.** Even a gentle one — `SCROLL_BASE`
   ramping from 160 to 220 over 5 minutes, or the `GAP` tightening
   from 170 → 145 — would lift the long-run gameplay score from 8.5
   to 9.0. The current flat curve is the single biggest "feels off"
   item.
2. **Music.** One looping ambient pad per biome phase
   (day / sunset / night / sunrise) crossfading on the biome `phase`
   variable would lift the sound score from 7.5 to 9.
3. **Accessibility pass.** Reduced-motion toggle in the pause menu
   that disables screen shake + biome glow pulse. A visual flash on
   thunder cue. A high-contrast / colour-blind palette swap.
4. **Meta-progression.** Three unlockable Pip palettes at 50 / 200 /
   500 lifetime pillars. No purchase tier, no FOMO — just a "look,
   you made it this far" reward.
5. **Server-side leaderboard validation.** Move the plausibility
   check into a Supabase Edge Function and pin the anon key to read-
   only. The current client-only model is honest but trivially
   bypassed by a curl-armed attacker.
6. **Split the giant files.** `entities.py` and `intro.py` are each
   over 1,000 lines. Splitting them per-entity / per-beat would help
   future maintenance.
7. **Broaden test coverage.** Unit tests for `World._step` (one
   physics step with a known seed should produce a known scoreline),
   for the spawn-cooldown logic, and for the biome interpolation.

---

## 6. Recommendations for future game development with Claude Code

Patterns that worked well on Skybit and should be reused on the next
project:

1. **Lock the tuning constants in one file early.** `game/config.py`
   is 71 lines and every gameplay knob lives there. When Claude
   iterates on difficulty or power-up balance, it edits one file and
   the diff is obvious in code review. *Never* spread magic numbers
   across game logic — that's the single biggest cause of slow Claude
   iteration on game projects.

2. **Make Claude render preview images, not just code.** The
   `tools/render_*.py` scripts let Claude propose, e.g., "five
   variants of the grow icon" and immediately produce a PNG grid.
   That tight loop (Claude proposes → Claude renders → human picks)
   beats Claude-proposes → human-runs-game by a wide margin. Bake
   this into the project skeleton from day one.

3. **Procedural assets > shipped assets.** If the game's aesthetic
   allows it, procedural sprites mean Claude can re-design any asset
   in a single edit. Compared to "open Photoshop, edit PNG, save,
   reload" the velocity difference is huge.

4. **Comment the WHY, never the WHAT.** Skybit's comments explaining
   *why* the pitch-climbing was removed, *why* COEP was dropped, *why*
   the proof ledger exists are exactly the rationale Claude needs on
   the next iteration. Code that documents its own intent stays
   maintainable across long Claude sessions.

5. **Write small, focused unit tests for the load-bearing invariants.**
   Skybit's `test_plausibility.py` is only 144 lines and only covers
   one module, but those tests are exactly the ones that protect the
   leaderboard from a stray refactor. Pick the 1–3 most important
   invariants in your game (physics determinism, scoring rules,
   anti-cheat) and test them. Don't try to unit-test the rendering.

6. **Use the screenshot folder as a visual changelog.** Skybit's
   `docs/screenshots/powerups/*/variants/` directories preserve five-
   option exploration sets even after a winner was picked. When you
   come back in a month and ask "why didn't we pick the metallic
   ghost?", the answer is one folder away. Claude is great at
   producing those grids — don't throw them away.

7. **Build the WASM target from week one.** Pygbag-on-Netlify lets you
   share a playable URL with playtesters from day one. Don't wait
   until "it's ready" — the cross-platform debugging surfaces
   (audio backends, COEP headers, asset paths) are easier to fix
   incrementally than in one big "now port to web" sprint.

8. **Let Claude write the README as the game evolves, not at the end.**
   Skybit's README is detailed because it grew with the project, not
   because someone sat down at the end to write it. Treat the README
   as the spec — if a power-up doesn't have a one-paragraph entry in
   the README, it doesn't exist yet.

9. **Use `/ultrareview` (or equivalent) before declaring done.** A
   late-stage multi-agent review (like the one that produced this
   document) catches systemic issues — accessibility gaps, missing
   meta-progression, untested invariants — that small per-commit
   reviews miss. Schedule one before each release milestone.

10. **Capture the failure mode visibly.** Skybit's `main.py` paints
    the Python traceback onto the canvas when the game crashes at
    startup. That is the single most useful three-line addition you
    can make to a Pygame/pygbag project; it has probably saved a
    deploy multiple times. Steal this pattern.

---

## 7. Verdict

**Skybit ships ready.** It's a polished, charming, mechanically sound
casual flyer with a remarkable procedural-art pipeline, dual-target
build, and a leaderboard-with-conscience that most of its competitors
don't bother with. The headline weaknesses (no difficulty curve, no
music, thin accessibility) are all addressable in low single-digit
days of work. The codebase is in better shape than 90% of solo /
two-person game projects at the same stage.

**Final: 8.3 / 10 — Great. Ship it, then polish.**

---

## 8. References

Frameworks and rubrics consulted while writing this review:

- [GamesRadar+ — Our approach to reviewing and scoring](https://www.gamesradar.com/review-guidelines-how-we-score/)
- [Game Informer — Review System](https://gameinformer.com/scoring)
- [The Indie Game Report — Fairway's Review Rubric](https://www.theindiegamereport.com/about-us/fairways-review-rubric/)
- [A Comprehensive Rubric for Rating Video Games — Commissioner of Video Games (Medium)](https://medium.com/@fpires1/a-comprehensive-rubric-for-rating-video-games-6c1efa0ae89d)
- [Particlebit — Review Scoring System](https://particlebit.wordpress.com/review-scoring-system/)
- [Critical-Gaming Network — How To Write A Critical Video Game Review](https://critical-gaming.squarespace.com/blog/2008/7/7/how-to-write-a-critical-video-game-review.html)
- [Inven Global — How to Write a Video Game Review](https://www.invenglobal.com/articles/13634/how-to-write-a-video-game-review)
- [Updated Video Game Review Criteria — Doomfan1, 30 April 2026](https://doomfan1.wordpress.com/2026/04/30/updated-video-game-review-criteria-april-30th-2026-or-30-04-2026/)
- [Scientific American — Be one with Flappy Bird: The science of "flow" in game design](https://www.scientificamerican.com/article/be-one-with-flappy-bird-the-science-of-flow-in-game-design/)
- [Thomas Palef — Game Design Analysis of Flappy Bird and Swing Copters](https://medium.com/@thomaspalef/game-design-analysis-of-flappy-bird-and-swing-copters-5c6df9fc10f0)
- [GameAnalytics — How To Perfect Your Game's Core Loop](https://www.gameanalytics.com/blog/how-to-perfect-your-games-core-loop)
- [RealPython — Pygame: A Primer on Game Programming in Python](https://realpython.com/pygame-a-primer/)
- [MarsDevs — Python in Game Development: When It Works (and When It Doesn't)](https://www.marsdevs.com/blog/python-in-game-development)
