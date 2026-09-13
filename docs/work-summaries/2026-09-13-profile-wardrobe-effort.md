# Skybit — Profile: Wardrobe + Achievements Effort

*Branch: `v5_profile_equip` (exploration + code) · shipped to `v5_profile_wardrobe` · state as of 2026-09-13*

## Overview

The previous menu effort closed with an explicit open item:

> **Profile opens achievements directly** — there is no dedicated Profile screen
> yet. A natural next build is a Profile scene that showcases Pip's look *and*
> nests an Awards section.
> — [`2026-07-05-menu-profile-settings-effort.md`](2026-07-05-menu-profile-settings-effort.md)

This effort builds exactly that. **PROFILE** is now a real screen with two tabs —
**WARDROBE** (the player's owned cosmetics, with working tap-to-equip) and
**ACHIEVEMENTS** (the existing Hall of Fame / Hall of Shame wall, intact). Tapping
the menu's framed Pip diorama opens it.

Getting there took **20 rounds of design exploration** (7 concept families, 102
rendered comparison figures) before a single line of production code was written.
That exploration lives on `v5_profile_equip` and was **deliberately kept out of the
integration branch** — only the 3 code commits were cherry-picked onto
`v5_profile_wardrobe`.

---

## What shipped

- **A real PROFILE screen.** Tapping the menu's Pip diorama opens `STATE_PROFILE`,
  landing on WARDROBE.
- **A shared, persistent chrome.** A "PROFILE" wordmark (0–40px) and a
  WARDROBE / ACHIEVEMENTS segmented pill (40–72px) sit above both tabs, with one
  shared MENU button in the footer.
- **A working wardrobe.** The foam field-case UI — Pip posed in a die-cut cutout,
  a category rail (COSTUME / PARROT / PARCELS), and a scrollable tray of item
  tiles. Owned items show lit, with a gold rim, corner latches and a checkmark
  chip; unowned ones are die-cut silhouettes marked `?`.
- **Tap-to-equip that actually works.** Tapping an owned tile equips it through
  the real save (`store_data.equip`), persists immediately, flashes
  "<NAME> EQUIPPED", and re-renders Pip in the cutout wearing it — the same look
  that shows up in gameplay.
- **Achievements kept whole.** The FAME / SHAME toggle survives the move, hosted
  one band lower (72–104px) so it never collides with the new view pill.
- **Two achievements fixes** that rode along: category names now mask to `???`
  until you earn a badge in them (they were telegraphing whole classes of goals),
  and the redundant global progress bar left the header.

---

## How it works

Three scenes, one owner:

```
STATE_PROFILE ──> ProfileScene              (game/profile_screen.py)
                    │  draws shared header + view pill + footer
                    │  owns self.tab ("wardrobe" | "achievements")
                    ├─ WardrobeScene        (game/wardrobe_screen.py)
                    └─ AchievementsScene    (game/achievements_screen.py)
                         rendered with embedded_top = 72
```

**`ProfileScene`** is a thin coordinator. It renders the active child first, then
paints its own chrome on top, so the top band always wins. `tap_or_close(pos)`
resolves a tap in priority order — view pill → the active tab's own controls →
the shared MENU button — and returns `"close"` for the caller to dismiss.

**`WardrobeScene`** is the design mockup ported to real data and real input:

- **Data.** `_owned_ids_for(group)` intersects `store_data.owned_ids()` with
  `store_catalog.ids_of_group(group)`; `_equipped_sid_for(group)` reads the live
  equip slot. `category_rows()` turns that into tile rows. Every mock constant
  from the exploration script (`HERO_OWNED`, `HERO_EQUIPPED`, `hero_groups()`)
  is gone.
- **Two-tier caching**, mirroring `AchievementsScene._ensure_content`:
  `_ensure_chrome()` bakes the static case (shell, lid, cutout, Pip, rail) keyed
  on `(sel_group, rail icons, equipped ids)`; `_ensure_tray()` builds the full
  unscrolled tray as one tall surface keyed on
  `(sel_group, owned signature, equipped id)`. Per frame it blits a scrolled
  slice — no re-render while scrolling, and an equip invalidates both keys
  naturally.
- **Hit-testing.** `_tile_layout` stores tile rects in *tray-content* space;
  `handle_tap` converts a screen position by subtracting the viewport origin and
  adding `scroll_offset`, so scrolled tiles hit correctly without rebuilding rects.

**`AchievementsScene.embedded_top`** is the mechanism that preserves FAME/SHAME.
When set, the scene skips its own title block and footer and draws its toggle at
that y instead of `_HEADER_H`. `_viewport()` follows automatically, so the list
starts at 104. `embedded_top = None` is byte-for-byte the old standalone path.

**`store_data.slot_of()`** was promoted from `store.py`'s private `_slot_of` so
the equip-slot rule lives in one place; `store.py` now delegates to it.

---

## Files touched

| File | Role |
|---|---|
| `game/wardrobe_screen.py` *(new, 835 ln)* | `WardrobeScene` — case art, category rail, item tray, tap-to-equip, scroll + caching |
| `game/profile_screen.py` *(new, 166 ln)* | `ProfileScene` — shared chrome, tab state, pointer/tap routing to the active child |
| `game/achievements_screen.py` | `embedded_top` mode; category-name masking; progress bar removed |
| `game/scenes.py` | `STATE_PROFILE`, `_open_profile`/`_close_profile`, `_handle_profile_event`, update/render dispatch; menu PROFILE tap re-pointed |
| `game/store_data.py` | new public `slot_of()` |
| `game/store.py` | `_slot_of` delegates to `store_data.slot_of` |
| `tests/test_wardrobe_screen.py` *(new)* | 12 tests |
| `docs/profile_equip/**` *(102 PNGs)* | Design exploration — **exploration only, not cherry-picked** |

---

## Key decisions

**Equip slots are per-*kind*, not per-category.** The single most consequential
discovery. `store_data` has one `equipped_skin` slot shared by *all* of
costume / parrot / animal / hats / shoes / shades, plus an independent
`equipped_parcel`. So the rail's three categories are **browsing tabs into two
real slots** — equipping a parrot skin silently un-equips a costume. The UI now
reflects this honestly (only the genuinely-worn item shows the chip) instead of
implying three independent slots. Found during exploration, before it became a bug.

**A third chrome band, only where it's needed.** Stacking the new view pill above
achievements' FAME/SHAME toggle risked "two toggle bars" clutter — and an early
mockup composite silently *dropped* FAME/SHAME by cropping it away. The fix:
WARDROBE content starts at 72 (it has no sub-control and pays nothing), while
ACHIEVEMENTS spends 32px on its own toggle at 72–104. Each tab pays only for the
controls it has.

**Locker Tabs won on repeat-visit cost.** Five navigation mechanisms were
brainstormed and critiqued: Locker Tabs (segmented pill), Pip's Turntable (mascot
fixed, backdrop swipes), Flip Case (case flips to a trophy case), Hub Shelf, and
Trophy Shade. Two were cut on real defects — Hub Shelf adds a tap on *every*
visit and duplicates the main menu's job; Trophy Shade's drag-down gesture
collides head-on with the achievements list's own scroll. Locker Tabs is tap-native,
instantly discoverable, and reuses an idiom the game already has.

**The material-polish round was never locked in.** Five finishes
(single-key-vitrine, clearcoat, machined-alloy, saddle-and-brass, spec-plate) were
built as genuine pygame rebuilds and compared, but no winner was chosen — so the
shipped screen deliberately uses the **baseline flat-gradient styling**. Picking a
finish is a separate, still-open decision.

**No numpy.** The exploration scripts leaned on numpy for per-pixel desaturation;
the shipped game imports it nowhere. `dim_thumb()` uses a pygame `BLEND_RGBA_MULT`
instead — slightly less true desaturation, zero new runtime dependency.

---

## Tests & verification

- **12 new tests** in `tests/test_wardrobe_screen.py`: `slot_of()` parity with the
  old private helper, category switching, tap-to-equip + persistence,
  already-equipped tap is a no-op, void-tile tap is a no-op, cross-group mutual
  exclusion on the shared skin slot, grand-total counting, and both
  `AchievementsScene` render modes (embedded vs standalone).
- **Full suite: 139 passed** (127 pre-existing + 12), on both `v5_profile_equip`
  and the cherry-picked `v5_profile_wardrobe`.
- **Live headless integration check** against `v5_integration`'s *redesigned*
  harbour-post menu — the main risk, since that branch rewrote `hud.py` (+525 ln).
  `menu_profile_rect` survives; PROFILE opens → wardrobe renders → tap-to-equip
  persists → ACHIEVEMENTS switches with FAME/SHAME intact → Hall of Shame
  switches → MENU returns.
- **Both build targets:** pure pygame, no platform-specific code, reusing
  `store_data`'s existing native-JSON / `window.__sk` bridge abstraction. No
  `pygame.mixer` on the web path. Every visual procedural.

---

## Follow-ups / open items

- **Pick a material finish.** The five polish concepts are built and comparable
  ([`polish_showcase_v2.png`](https://github.com/ytocker/skybit/blob/v5_profile_equip/docs/profile_equip/foamcase/polish_showcase_v2.png));
  none is wired in. The shipped screen is baseline styling.
- **No "new/unseen" badges.** `store_data` has no persisted `seen` flag, so the
  gold unseen-dot and "N NEW" category tag from the design are unbuilt. (This is
  the same missing field the previous effort flagged for the Profile card.)
- **No first-open coaching hint** — same reason, no persisted flag.
- **Unowned tiles are inert.** Per "Wardrobe is what is owned", tapping one does
  nothing; a deep-link into the coin store is the obvious next step.
- **No sticky category header** while scrolling (the achievements list doesn't do
  this either), **no equip-confirmation burst** animation, and **Pip renders on a
  static frame** — all present in the design, all deferred.
- **Only 3 of 7 categories are open** (costume / parrot / parcels), matching the
  store's own `OPEN_GROUPS`. The rail scales, but adding a 4th needs a look at
  the column height.
- **`STATE_ACHIEVEMENTS` is now orphaned** — `_open_achievements` is no longer
  called from the menu. Kept deliberately (the standalone render path is still
  tested), but it's dead entry-point code worth a decision.

---

## Commits

**77 commits** on `v5_profile_equip` — 74 are `docs/profile_equip/**` exploration
figures, 3 are code. Only the code shipped:

| SHA (`v5_profile_equip`) | Subject | On `v5_profile_wardrobe` |
|---|---|---|
| `6558acc0` | achievements: mask category names until the first badge in them is earned | `138cbc5c` |
| `db1f76ef` | Remove global progress bar from achievements screen header | `b1e090f7` |
| `2bcf010e` | Round 20: real PROFILE screen — Locker Tabs navigation + full equip | `f746fdd2` |

`v5_profile_wardrobe` was branched off latest `v5_integration` and carries those
three cherry-picks and nothing else — **7 files, +1352/−59, zero `docs/` entries.**
All three applied without conflict.

### Key exploration figures

| Figure | What it shows |
|---|---|
| [`showcase.png`](https://github.com/ytocker/skybit/blob/v5_profile_equip/docs/profile_equip/showcase.png) | The original 7 concept families (aviary, dressing-perch, foamcase, quilt, steamer-trunk, tuner, vitrine) |
| [`final_two_designs.png`](https://github.com/ytocker/skybit/blob/v5_profile_equip/docs/profile_equip/final_two_designs.png) | The cut to two finalists — foamcase and vitrine |
| [`band_options_grid.png`](https://github.com/ytocker/skybit/blob/v5_profile_equip/docs/profile_equip/band_options_grid.png) | 8 hero-band height/composition options |
| [`polish_showcase_v2.png`](https://github.com/ytocker/skybit/blob/v5_profile_equip/docs/profile_equip/foamcase/polish_showcase_v2.png) | The 5 material finishes (still unpicked) |
| [`holistic_chrome_round_17.png`](https://github.com/ytocker/skybit/blob/v5_profile_equip/docs/profile_equip/holistic_chrome_round_17.png) | Wardrobe + achievements as a matched pair |
| [`profile_nav_concepts_round19.png`](https://github.com/ytocker/skybit/blob/v5_profile_equip/docs/profile_equip/profile_nav_concepts_round19.png) | All 5 navigation mechanisms, each answering FAME/SHAME |
