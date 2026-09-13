# Skybit — Menu, Profile, Settings & About UI Effort

*Branch: `v5_achievements` · state as of 2026-07-05*

## Overview

This session reshaped the **main menu and the screens that hang off it**. The
menu went from a stack of pills to a single scarlet **START** hero flanked by a
framed **Profile** card (the live Pip diorama, made tappable) and a bottom trio
of icon chips. Two brand-new screens landed — a real **Settings** screen and an
**About** screen — plus the game's first **device-local preference** (an SFX
mute) that never touches the cloud leaderboard. It also closed out the
**Hall of Shame** achievements expansion (the achievements system itself is
documented in depth in
[`2026-07-03-achievements-effort.md`](2026-07-03-achievements-effort.md); this
doc is the menu/UI-side companion).

Everything below is **live in-game on `v5_achievements`** unless explicitly
marked as a design exploration. All 56 unit tests pass; both build targets
(native desktop + pygbag/WASM) stay green; every visual is procedural.

---

## The menu, as a player sees it now

```
                 SKYBIT
             Pocket Sky Flyer
        ┌───────────────────────┐
        │   [ live Pip + house ]│   ← framed PROFILE card (tap → your records)
        │        PROFILE ▸      │
        └───────────────────────┘
              (  START  )            ← single scarlet hero
        [ STORE ] [ TOP 10 ] [ SETTINGS ]   ← icon chips
```

**Removed from the old menu:** the `HOW TO PLAY` and `POWER-UPS` pills (moved
into Settings), and the standalone `AWARDS` tile (folded into the Profile card).

---

## What shipped (live in-game)

### 1. Menu redesign
- **START** recentered and enlarged to own the middle band; drawn in the quieter
  bordeaux ("dim") variant so it sits in the night palette.
- **Bottom trio of icon chips** — `STORE · TOP 10 · SETTINGS`. Each is an
  icon-forward `_volume_panel` chip with a tracked caption; hit-rects are
  published each frame and routed in `scenes.py` `STATE_MENU`.
- Tap routing (`game/scenes.py`): Profile card → achievements, STORE →
  coming-soon toast (stub), TOP 10 → leaderboard, SETTINGS → Settings screen.

### 2. Profile card entry (`game/hud.py` `_draw_profile_card`)
- The Pip-at-the-house diorama the menu already draws is now **framed as a
  tappable character card** — a thin double-rule gold "jewel edge" + a beveled
  brass **PROFILE** nameplate + a gold tap-glow halo that rides the same
  `sin(t·3.6)` pulse as START, so it reads as interactive rather than scenery.
- Tapping it **opens the achievements screen** — the player's *records* fold
  into Profile. (The card itself already showcases Pip's current *look*, which
  sets up the future loop: see your Pip → tap → re-skin in the Store → new look
  shows on the menu.)

### 3. Settings screen (`game/settings_screen.py`, new)
- A full-screen list in the night-sky family (gilded header + grounded MENU
  pill), grouped into sections:
  - **HELP** — *How to Play* and *Power-Ups* (working launchers; they return to
    Settings, not the menu).
  - **GENERAL** — *Sound Effects* (mute toggle) and *About* (nav).
- Each row is a `_volume_panel` body with a gold icon disc; `nav` rows carry a
  chevron, the toggle row a track-and-knob switch. Row hit-rects + the MENU pill
  are published for the `STATE_SETTINGS` tap router.

### 4. SFX mute — first device-local preference (`game/prefs.py`, new)
- A tiny settings store `{"muted": bool}` that is **device-local and never
  cloud-merged**: native writes a `"settings"` key inside the save JSON; web uses
  `localStorage["skybit_settings"]` via new `settings_load` / `settings_save`
  `__sk` actions in `inject_theme.py`.
- `game/audio.py` gained `set_muted()` / `is_muted()`; both `_play` backends
  early-return when muted. On web, muting also sets `window.__skMuted`, and
  `window.skyPlay` guards on it — so **one flag silences game SFX *and* the UI
  button clicks** on both targets. Applied at launch from the saved pref.

### 5. About screen (`game/about_screen.py`, new)
- Reached from Settings → About (renamed from the original "Credits"). Shows
  `SKYBIT / Pocket Sky Flyer / Version 1.1.0 / The game was built using code`,
  centered in the same night-sky family, with a MENU pill back to Settings.
- `VERSION = "1.1.0"` added to `game/config.py` (kept in sync with `pyproject`).

### 6. Achievements — Hall of Shame expansion (closed out)
- The 15 new anti-achievements and their bespoke tarnished emblems were finished
  and wired. **Roster now: 99 badges — 73 Fame / 8 categories + 26 Shame / 4
  categories**, each with a procedural center emblem ringed by an olive-laurel
  wreath that wilts for Shame. Full detail:
  [`2026-07-03-achievements-effort.md`](2026-07-03-achievements-effort.md).

---

## Design explorations (the picks — and what didn't ship)

Every visual above went through the orchestrated design loop (graphics-designer →
art-director critique → revision). The matured figures, with the choice made:

| Exploration | Figure (blob link) | Chosen |
|---|---|---|
| Achievements menu entry | [`menu_profile_concepts`](https://github.com/ytocker/skybit/tree/v5_achievements/docs/menu_profile_concepts) | Struck-bevel **star → AWARDS tile** (later folded into Profile) |
| Settings *entry* + menu layout | [`menu_settings_concepts`](https://github.com/ytocker/skybit/tree/v5_achievements/docs/menu_settings_concepts) | **Concept 3** bottom trio, narrow "icon chip" width |
| Settings *screen* | [`settings_concepts/round_2.png`](https://github.com/ytocker/skybit/blob/v5_achievements/docs/settings_concepts/round_2.png) | **#1 row list** |
| Profile + Store menu entries | [`menu_profile_store_concepts/round_2.png`](https://github.com/ytocker/skybit/blob/v5_achievements/docs/menu_profile_store_concepts/round_2.png) | superseded by the Profile-panel direction below |
| Profile as a bust panel | [`menu_profile_panel_concepts/round_2.png`](https://github.com/ytocker/skybit/blob/v5_achievements/docs/menu_profile_panel_concepts/round_2.png) | *not chosen* — a separate cropped bust competed with the live Pip |
| Profile reusing the standing Pip | [`menu_profile_uses_pip_concepts/round_2.png`](https://github.com/ytocker/skybit/blob/v5_achievements/docs/menu_profile_uses_pip_concepts/round_2.png) | **Framed-in-place** (frame the existing Pip) |
| Frame refine (thinner + bigger label) | [`menu_profile_frame_refine_concepts/final.png`](https://github.com/ytocker/skybit/blob/v5_achievements/docs/menu_profile_frame_refine_concepts/final.png) | **Card C** — jewel edge + brass nameplate, records badge & full-width band removed → **this is what shipped** |

*Not built:* the bust-portrait / avatar-medallion Profile treatments, the
pedestal/spotlight/tap-bubble Pip treatments, and the corner-bracket / heavy-bezel
frames were all culled along the way. The Store was designed into the menu but
is a **stub** on this branch (see follow-ups).

---

## Files touched

**New**
- `game/prefs.py` — device-local settings store (SFX mute).
- `game/settings_screen.py` — the Settings scene.
- `game/about_screen.py` — the About scene.

**Changed**
- `game/hud.py` — `_draw_profile_card` + STORE/TOP 10/SETTINGS chip trio + a
  transient STORE "coming soon" toast in `draw_menu`.
- `game/scenes.py` — `STATE_SETTINGS` (11) + `STATE_ABOUT` (12), open/close
  handlers, `STATE_MENU` tap routing for the Profile card + STORE chip, and the
  mute pref applied at launch.
- `game/audio.py` — `set_muted` / `is_muted`; both backends gate on it.
- `inject_theme.py` — `window.skyPlay` mute guard + `settings_load/save` actions.
- `game/config.py` — `VERSION = "1.1.0"`.

---

## Verification

- **Tests:** `python -m pytest tests/` → **56 passed** throughout.
- **In-game render:** the real `STATE_MENU` frame was rendered headless — the
  Profile frame + all four menu rects publish correctly, and the STORE tap fires
  the coming-soon toast.
- **Both targets:** the mute is a pure flag plus one `window.skyPlay` guard; the
  `settings_*` JS mirrors the proven `ach_*` localStorage pattern; every new
  screen is pure procedural render — **no `pygame.mixer` on the web path**.

---

## Open follow-ups

- **Profile opens achievements directly** — there is no dedicated Profile screen
  yet. A natural next build is a Profile scene that showcases Pip's look *and*
  nests an Awards section, rather than jumping straight to the achievements wall.
- **STORE is a stub** (coming-soon toast). The real shop lives on another branch;
  wiring it here will replace the toast.
- **Coin balance needs a menu home** once the Store ships.
- **No "unseen unlock" state** is persisted, so the Profile card can't yet show a
  "new record" pip — the records badge was intentionally dropped from the final
  card. Adding a live "NEW" dot would need a small new persisted field.
- `docs/achievements/README.md` still describes the pre-expansion roster; the two
  work-summaries are the current-state source of truth.
