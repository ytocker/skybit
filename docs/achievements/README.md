# Skybit — Achievements

A main-menu **Achievements** section: a scrollable, discovery-driven list of
**46 unlockables** across six categories, earned by playing. Progress persists
locally on both build targets (native desktop + the pygbag/WASM browser build),
unlocks fire a toast on the run-summary screen, and every badge is drawn
procedurally (no PNGs) in the "Courier's Commendation" struck-metal style.

This document covers **what the player sees** and **how it's built**.

---

## 1. Player experience

- **Menu entry.** A fourth pill — `ACHIEVEMENTS` — sits in the main-menu button
  stack (below `START` / `HOW TO PLAY` / `POWER-UPS`).
- **The screen.** A full-screen scrollable list:
  - **Scroll** with the mouse wheel or by **dragging** (touch + mouse); a thin
    gold scrollbar tracks position. A near-stationary tap dismisses back to the
    menu.
  - **Category sections** (Flight Log, Riches, Power Player, Stormchaser, Skater,
    Mysteries) each with a `unlocked / total` count.
  - A fixed gilded **"ACHIEVEMENTS"** header with a global `N / 46` counter and a
    thin gold **overall progress bar**; a pulsing "TAP TO RETURN · DRAG TO SCROLL"
    footer.
- **Discovery mode.** Every **locked** achievement is a mystery: the row shows
  `???` + a generic hint ("Hidden — discover it in play."), the badge is a masked
  `?` medallion, and **no progress or requirement is revealed**. You learn what an
  achievement was only when you earn it. The rarer **Mystery** tier shows an
  amethyst `?` (vs the normal pewter `?`) so it reads as special-locked.
- **Unlock toast.** Achievements are evaluated once at the **end of a run**; any
  newly-earned ones slide in one at a time on the run-summary screen as an
  "ACHIEVEMENT UNLOCKED — {title}" badge toast with a short chime.

---

## 2. The full roster (46)

**(L)** = lifetime / cumulative across all runs; everything else is within a
single run. The six **Mysteries** are the hidden rare tier.

### 🪶 Flight Log (10) — pillars, score, day-cycles
| Title | Unlock |
|---|---|
| First Delivery | Clear your very first pillar |
| Courier in Training | Pass 25 pillars in one run |
| Route Veteran | Pass 50 pillars in one run |
| Centurion of the Sky | Pass 100 pillars in one run |
| Triple Digits | Reach a score of 100 |
| High Flyer | Reach a score of 500 |
| Round the Clock | Survive a full day-into-night cycle |
| Three-Day Weekend | Survive three full day cycles in one run |
| Frequent Flyer | Pass 1,000 pillars **(L)** |
| Globetrotter | Pass 10,000 pillars **(L)** |

### 💰 Riches (6) — coins
| Title | Unlock |
|---|---|
| Pocket Change | Collect 25 coins in one run |
| Coin Run | Collect 100 coins in one run |
| Coin Collector | Collect 500 coins **(L)** |
| Coin Vault | Collect 5,000 coins **(L)** |
| Coin Tycoon | Collect 25,000 coins **(L)** |
| Midas Touch | Collect 100,000 coins **(L)** |

### ⚡ Power Player (7) — power-ups
| Title | Unlock |
|---|---|
| Power Up! | Grab your first power-up |
| Buffet | Use 4 different power-ups in a single run |
| Animal Magnetism | Trigger the magnet 15 times **(L)** |
| Gotta Grab 'Em All | Discover 10 different power-ups **(L)** |
| Finger Lickin' | Go into KFC mode |
| Power Hungry | Collect 100 power-ups **(L)** |
| Power Addict | Collect 500 power-ups **(L)** |

### 🌩️ Stormchaser (9) — nerve, endurance, ceiling, weather
| Title | Unlock |
|---|---|
| Close Shave | Squeak past 5 pillars in one run |
| Threadneedle | Squeak past 15 pillars in one run |
| Long Haul | Stay airborne for two minutes straight |
| Storm Rider | Fly into the rain (reach pillar 70) |
| Snowbird | Reach the snow squall (reach pillar 139) |
| Tireless Wings | Flap 5,000 times **(L)** |
| Headbanger | Bonk the ceiling 10 times in one run |
| Hard Head | Bonk the ceiling 200 times **(L)** |
| Iron Wings | Flap 50,000 times **(L)** |

### 🛹 Skater (8) — skateboards, tricks, rails
| Title | Unlock |
|---|---|
| Board Meeting | Catch a skateboard |
| Sponsored | Catch 10 skateboards **(L)** |
| Going Pro | Catch 50 skateboards **(L)** |
| Full Combo | Land all four trick types in one run |
| Trickster | Land 50 skateboard tricks **(L)** |
| Trick Legend | Land 500 skateboard tricks **(L)** |
| Grinder | Ride the rail cart 10 times **(L)** |
| Rail Baron | Ride the rail cart 50 times **(L)** |

### 🔮 Mysteries (6) — hidden / rare tier
| Title | Unlock |
|---|---|
| Three Wishes | Summon the genie and make a wish |
| Knighted | Survive a fatal hit under a knight's guard |
| X Marks the Spot | Crack open a cycle-finale treasure chest |
| Jackpot! | Hit the lottery's top tier |
| Off the Rails | Ride the rail cart |
| Be Careful What You Wish For | Discover the genie's nastier surprise (poison) |

**Totals:** Flight Log 10 · Riches 6 · Power Player 7 · Stormchaser 9 ·
Skater 8 · Mysteries 6 = **46**.

---

## 3. How it works (architecture)

Three new modules, plus small hooks into the existing game.

| File | Role |
|---|---|
| `game/achievements.py` | Data model, registry, end-of-run engine, persistence |
| `game/achievement_icons.py` | Procedural medallion badges + per-key glyphs |
| `game/achievements_screen.py` | `AchievementsScene` — the scrollable screen |

**Integration points (existing files):**

| File | Change |
|---|---|
| `game/scenes.py` | `STATE_ACHIEVEMENTS`; menu-button + input routing; `_on_death` runs `evaluate_run` (demo-gated); unlock-toast queue + render on `STATE_STATS` |
| `game/hud.py` | The `ACHIEVEMENTS` menu pill + its hit-rect |
| `game/audio.py` | `play_achievement()` (reuses existing OGGs; safe on both backends) |
| `game/world.py` | `ceiling_hits` (edge-detected ceiling bonk) and `tricks_landed` / `tricks_landed_types` counters |
| `inject_theme.py` | `ach_load` / `ach_save` actions on the `window.__sk` dispatcher (browser localStorage) |

### Data model
Each achievement is a frozen dataclass in the `ACHIEVEMENTS` registry:

```python
Achievement(id, title, desc, category, icon_key, stat, target=1,
            scope="run"|"life", hidden=False)
```

- `id` is **permanent** — never rename or reuse one (it would orphan a player's
  saved unlock). Adding new rows is additive and needs no migration.
- `hidden=True` marks the **Mystery** rarity tier (amethyst badge). Note: in the
  current "discovery mode" UI **all** locked rows are masked, so `hidden` only
  controls the rarity look, not whether the text is hidden.
- Derived lookups `BY_ID`, `BY_CAT`, and `CATEGORY_ORDER` are built once.

### Unlock engine — evaluated once at end-of-run
`evaluate_run(world, store) -> list[str]` (called from `scenes._on_death`, skipped
for the scripted demo):
1. `_accumulate(store, world)` folds the finished run into lifetime counters.
2. For each still-locked achievement, compute its current value (run-scope from
   the `World`, life-scope from the save) and compare to `target`.
3. Mark newly-unlocked ids, persist once, return the new ids (for the toast).

Zero per-frame cost — all stats are final at death.

---

## 4. Data & persistence

One JSON blob, abstracted behind `load()` / `save()` so a future account-scoped
cloud sync is an additive change that never touches the engine or UI:

```json
{
  "v": 1,
  "unlocked": { "first_flight": 1718800000, "headbanger": 1718800500 },
  "life": {
    "total_runs": 0, "total_coins": 0, "total_pillars": 0,
    "total_flaps": 0, "total_time": 0, "best_cycles": 0,
    "total_tricks": 0, "total_ceiling": 0,
    "powerups_seen": { "magnet": 0, "skateboard": 0, "rail": 0, "...": 0 }
  }
}
```

- **Native** — read-modify-written under the `"achievements"` key of
  `skybit_save.json` (sibling keys preserved).
- **Browser (URL build)** — a single string in `localStorage["skybit_ach"]` via
  the `ach_load` / `ach_save` actions on the closure-private `window.__sk`
  dispatcher (synchronous; localStorage persists per browser, like the device
  UUID).
- Every read/write is wrapped so a corrupt save degrades to "nothing unlocked"
  rather than crashing. `_migrate()` back-fills any missing lifetime keys on load.

> **Why local-first?** There's no account/login yet, so a cloud row couldn't truly
> follow a player across devices anyway (its key would itself live in
> localStorage). Local persistence works on the live URL build today and the
> `load()`/`save()` seam keeps a cloud mirror a drop-in later.

---

## 5. Stat vocabulary

What each achievement's `stat` reads (resolved in `_run_value` / `_life_value`):

| Scope | Stat | Source |
|---|---|---|
| run | `pillars_passed`, `score`, `coin_count`, `cycles_completed`, `near_misses`, `time_alive`, `ceiling_hits` | plain `World` attributes |
| run | `pu:<kind>` | `World.powerups_picked[kind]` (e.g. `pu:kfc`, `pu:skateboard`) |
| run | `distinct_powerups` | count of distinct power-up kinds picked this run |
| run | `trick_types` | count of distinct skate trick types landed this run (target 4 = "Full Combo") |
| run | `lottery_jackpot` | scans the proof event ledger for a top-tier lottery hit |
| life | `total_coins`, `total_pillars`, `total_flaps`, `total_tricks`, `total_ceiling` | accumulated in `_accumulate` |
| life | `puseen:<kind>` | lifetime pickup count of a kind (e.g. `puseen:skateboard`, `puseen:rail`) |
| life | `distinct_powerups` | distinct power-up kinds seen all-time |
| life | `total_powerups` | sum of all lifetime power-up pickups |
| life | `magnet_life` | lifetime `magnet` + `megamagnet` pickups |

The two new `World` counters added for this feature:
- **`ceiling_hits`** — incremented once per ceiling **bonk** (the top edge clamps
  Pip rather than killing him), edge-detected via `_was_ceiling_clamped` so a held
  bonk counts once.
- **`tricks_landed`** / **`tricks_landed_types`** — bumped in the four skate-trick
  triggers (`backflip` / `kickflip` / `heelflip` / `popshuvit`).

Lifetime rail rides and skateboards needed **no** new instrumentation — they read
the existing `powerups_seen` dict via `puseen:rail` / `puseen:skateboard`.

---

## 6. Adding or tuning an achievement

1. Append an `Achievement(...)` to the `ACHIEVEMENTS` tuple in
   `game/achievements.py`. Pick a **new, permanent** `id`.
2. Choose a `stat` from the vocabulary above (or add a new one):
   - A new **lifetime** counter needs one line in `_accumulate()` and, if it's
     derived, a branch in `_run_value` / `_life_value`.
3. Set `category`, `target`, `scope`, and `hidden` (only for a rare Mystery).
4. Reuse an existing `icon_key`, or add a new glyph: write a `_glyph_<name>` in
   `game/achievement_icons.py` and register it in the `_GLYPHS` dict.
5. Tuning a threshold is just changing the `target` — no migration needed.

Adding achievements is always additive: an id absent from a player's `unlocked`
map simply reads as locked.

---

## 7. Badge art & design history

Badges are the **"Courier's Commendation"** family: a struck-metal gold medallion
lit from a single upper-left source (specular rim hot-spot, recessed enamel well,
beveled step, twin-laurel sprig) stamped with an engraved per-key glyph. States:

- **Unlocked (normal)** — gold rim + navy enamel + glyph.
- **Unlocked (Mystery)** — gold rim + desaturated **amethyst** enamel + sparkle
  ring (gold stays the only fully-saturated accent).
- **Locked (normal)** — a warm-pewter **`?`** disc (masked).
- **Locked (Mystery)** — an amethyst **`?`** disc + sparkle ring (rarer-looking).

The family was produced via the project's orchestrator design-loop
(graphics-designer ↔ art-director). Artifacts:

- [`round_1.png`](round_1.png) — initial concept
- [`round_2.png`](round_2.png) — amethyst Mystery tier + struck-metal relief
  (SHIP-READY)
- [`round_3.png`](round_3.png) — closing polish (skate/wing/dormant fixes)
- [`round_4_discovery.png`](round_4_discovery.png) — all-locked discovery masking
- [`round_5_grind.png`](round_5_grind.png) — grind achievements + the new
  `ceiling` glyph

---

## 8. Testing & build notes

- **Unit tests:** `tests/test_achievements.py` (35 tests) cover threshold unlocks,
  lifetime accumulation, derived stats (distinct power-ups, lottery jackpot, trick
  types, total power-ups), the Headbanger/Full-Combo paths, and no-rerun-duplicate
  behavior. Run with `python -m pytest tests/`.
- **Both build targets stay green.** The only target-divergent code is
  `load`/`save` (branches on `sys.platform == "emscripten"`) and the `__sk`
  localStorage actions; the toast sound is safe on web because `game/audio.py`
  routes through `window.skyPlay` and never touches `pygame.mixer`.
- **No new runtime assets** — all art is procedural and the toast reuses existing
  OGGs, so the player-facing bundle size is unaffected.
- Achievement evaluation is skipped for the scripted demo run.

---

## 9. Menu entry — placement exploration

The section is reached today from a **"HALL OF FAME" pill** in the main-menu
four-pill stack (`START · HOW TO PLAY · POWER-UPS · HALL OF FAME`), with a
separate **BEST** panel and **TOP 10** leaderboard panel along the bottom
([main-menu capture](screenshots/main_menu.png)). As the feature grew (99 badges
across two halls), we explored better ways to surface it.

**Advice gathered (read-only agents):**
- *Gaming-experience tester:* keep a **labeled** entry (icon-only nav hurts
  discoverability), don't add a 5th pill (menu real-estate is tight) or a separate
  two-level hub state, grow the destination screen via its existing tab system,
  and add a cheap **"new unlocks" indicator** (the one real discoverability gap
  today).
- *Novelty designer:* make the door *diegetic/characterful* (tap Pip, who wears
  his rank; the post-house door; a courier ID card) and lead a profile with a
  **Fame↔Shame "personality readout"** so it reads as identity, not a stats page.

**Profile-tile concept sheet** (5 options, mockups only — not production):
[`menu_profile_concepts/options.png`](../menu_profile_concepts/options.png).
Each drops the 4th pill and folds the achievements entry + best + leaderboard into
one bottom **Profile** tile:

| # | Concept | Thesis |
|---|---|---|
| 1 | Full-width Profile bar | one wide identity pill: crest + rank + best + trophy `N/99` |
| 2 | Courier ID card | lanyard ID badge: Pip mugshot, member-since, medal strip, count |
| 3 | Heraldic crest + chips | laurel category-quadrant crest on a ranked ribbon, flanked by BEST + count chips |
| 4 | Trophy shelf | a row of your top earned badges on a gold shelf + `N/99` tally |
| 5 | Two compact tiles | conservative split: a PROFILE tile beside the kept slim BEST tile |

**Chosen direction (simpler):** rather than a full profile hub, repurpose the
bottom-left **BEST** tile into a compact **icon entry** that opens the
achievements section (leaderboard stays on the right). Icon concepts are being
explored separately; this profile-hub sheet is kept as a record for when a store /
cosmetics feature later warrants a full Profile surface.
