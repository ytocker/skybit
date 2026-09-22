# Rebrand crew — situation brief + roster

Strategy round for the brand relaunch on `v5_rebranding`. This document is the
roster only: it names the crew and what each role owns. The matching
`.claude/agents/*.md` files are a follow-up round.

**Mandate this relaunch:** new **name**, **logotype**, **palette**, and the
**growth surfaces**.
**Deferred, deliberately:** retiring the KFC tie-in; repositioning Pip the macaw.

---

## The situation

### We have a finished game and no brand

The product is mature — biomes, weather, a gated power-up roster, achievements,
a leaderboard, telemetry. The brand is not. What exists today:

**The name is one constant and fourteen hard-coded strings.** `game/config.py:3`
holds `TITLE = "Skybit"`, but the menu logotype is literal text at
`game/hud.py:2318` (`"SKYBIT"`, 72pt) with the subtitle `"POCKET  SKY  FLYER"` at
`:2327`; the same treatment repeats in `game/about_screen.py:43`, `game/intro.py`,
`main.py:57` and three fields in `pyproject.toml`. A rename is cheap in code and
expensive in judgement.

**Fifteen identifiers are migration-sensitive.** `skybit_save.json`,
`skybit_scores.json`, `skybit_store.json` (`game/config.py:444-446`), the
localStorage keys `skybit_device_id` / `skybit_ach` / `skybit_settings`
(`inject_theme.py:692,1006,1019`), the DOM id `skybit-loading` the deploy asserts
on (`inject_theme.py:1779+`), and the JS globals `window.__sk`, `window.skyPlay`,
`skybitGameReady`. Rename any of these naively and every existing player loses
their saves, achievements and identity. They get **aliased, never renamed**.

**A palette already exists and is used with discipline.** `_GOLD_BRIGHT
(240,192,64)` over `_RED_OUTLINE (168,32,16)`, applied through `_outlined_text`
(`game/hud.py:35,37,334`) across HUD, store, leaderboard and achievements. That
consistency is an asset — the relaunch refines a real system rather than
inventing one. Typography is the weak half: the entire identity rides on stock
`LiberationSans-Bold.ttf`, re-served to the browser as CSS family `SkybitMenu`.

**The growth surfaces do not exist at all.** `inject_theme.py` ships pygbag's
default `<head>` untouched — no `<title>`, no description, no OG or Twitter card,
no favicon, no manifest, no share image, no landing page. Every link to
`https://ytocker.github.io/skybit/` currently unfurls as a naked URL. This is the
highest-leverage gap on the board and the cheapest to close.

**Backend naming is version-based, not brand-based** (`public.scores`,
`scores_v5`, `plays`) — effectively free to carry through a rename.

**Standing risk, tracked but deferred:** `game/assets/kfc_logo.jpg` is a real
third-party mark composited on screen (`game/hud.py:1691`) and woven through
roughly twenty modules, including a *named gameplay power-up*. Commercial use
weakens a parody defence, and a relaunch is precisely when a rights-holder
notices. Out of scope this round; on the register from day one.

### What virality actually demands in 2026

Creative is now the primary performance lever — targeting precision has narrowed,
so the asset itself does the work. Around 59% of Gen Z discovers games through
short-form video. Browser games spread specifically because they are instant-play
with nothing to download, which is our structural advantage. And what travels is
a **clip moment**: one fifteen-second failure, streak or absurdity worth filming.

We have the instant-play advantage. We have no clip moment, no share loop, and
nothing that unfurls when a link is pasted.

### What the existing crew already covers

`.claude/agents/` holds eight specialists in a maker/critic house style —
`graphics-designer`↔`art-director`, `data-analyst`↔`analytics-director`, plus
`sound-designer`, `novelty-designer`, `gaming-experience-tester`, `qa-tester`.
A search across `.claude/` for market, brand, naming, copy, positioning, viral or
social returns nothing.

Visual craft is covered well. Everything **verbal, positional and
distributional** is missing. The roster below hires into that gap and reuses the
visual pair rather than duplicating it.

---

## The crew

Seven new roles; five existing roles on extended briefs. Each new maker pairs to a
critic and writes rounds to `docs/rebrand/<workstream>/round_N.md`, following the
established loop convention — the critic's first line is
`VERDICT: SHIP-READY | ITERATE | RE-ROLL`, maker ≤4 turns, critic ≤3, ending on a
maker revision.

### New roles

**1. Brand Strategist** — *maker, opus*
Owns the thesis: who this game is for, what feeling it sells, and what it is
called. Generates and defends name candidates, the tagline, the positioning
statement and the one-line pitch. Runs first-pass name clearance — existing
titles, app stores, domain and handle availability, obvious mark collisions — and
maintains the risk register the KFC exposure sits on. Proposes a shortlist; does
not pick the name.

**2. Brand Director** — *critic, opus*
Veteran casual-games brand critic. The paired critic for the Strategist, the
Copywriter, and the Growth Engineer's brand fit. Culls near-duplicate name
directions, kills anything generic or unsayable out loud, and returns ranked,
specific iteration briefs. Never edits production files.

**3. Verbal Identity Lead (Copywriter)** — *maker, opus*
Owns every word a player reads: the logotype lockup and subtitle, button and
power-up strings, death-screen lines, achievement names, store copy, the page
`<title>` and meta description, the OG card text, and the share caption. Writes
the voice rules that hold those together. Critiqued by the Brand Director.

**4. Growth Surface Engineer** — *maker, sonnet*
Builds what isn't there: `<title>`, meta description, OG and Twitter card tags,
favicon, web manifest, and the first-paint/landing experience — inside
`inject_theme.py` and `.github/workflows/pages.yml`, honouring the 5 MB bundle
ceiling and the `skybit-loading` DOM contract. Also owns **storage-key aliasing**,
so no rename ever orphans a save. Critiqued by the Brand Director for fit and
`qa-tester` for code.

**5. Share-Loop Designer** — *maker, opus*
Owns the clip moment and everything after it: the end-of-run shareable score card
(drawn procedurally, per project rules), the share CTA and its copy hand-off,
deep links back into a run, and which in-game moments are worth filming.
Critiqued by the Brand Director and `gaming-experience-tester` — a share prompt
that interrupts the tap loop is a regression, not a feature.

**6. Motion & Capture Lead** — *maker, sonnet*
Turns the game into footage: headless capture of runs, filmstrips, loops and
trailer cuts rendered under `docs/`, plus the animated logotype sting. Feeds the
short-form pipeline. Shares visuals as git links only, never inline.

**7. Community & Social Lead** — *maker, opus*
Owns the launch beats and the distribution calendar: posting cadence, creator and
streamer outreach list, a community home, launch-day sequencing across itch,
Reddit and TikTok, and the reply voice. Critiqued by the Brand Director.

### Existing roles, extended briefs — no new files

**8. Graphics Designer ↔ Art Director.** Extend from in-game art to **brand
marks**: wordmark, logotype, icon mark, and the palette now anchored on
`_GOLD_BRIGHT` + `_RED_OUTLINE` — including how it survives the day/night biome
cycle. The `/design` and `distinct-design-variants` skills already enforce
genuinely distinct concepts; reuse them unchanged.

**9. Sound Designer.** One addition: the audio logo. A sub-second sting under the
logotype that also closes every trailer cut. Dual-backend rules unchanged.

**10. Novelty Designer.** Feeds the Share-Loop Designer — which absurd,
screenshot-worthy moments should exist so there is something to clip.

**11. Data Analyst ↔ Analytics Director.** Extend the dashboard from gameplay
telemetry to the **growth funnel**: referrer, share→play conversion, D1 return,
and per-name / per-card A/B readouts, so the relaunch is judged on numbers rather
than taste.

**12. QA Tester.** One new duty: the **brand continuity sweep**. After any
rename, verify no stale string survives across the display sites, both build
targets boot, and every legacy `skybit_*` key still resolves.

---

## Coverage check

| Mandate surface | Owner |
|---|---|
| Name, tagline, positioning | Brand Strategist → Brand Director |
| Logotype, wordmark, palette | Graphics Designer → Art Director |
| On-screen and page copy | Verbal Identity Lead → Brand Director |
| `<head>`, OG card, favicon, landing | Growth Surface Engineer |
| Share loop and score card | Share-Loop Designer |
| Trailer, clips, logo sting | Motion & Capture Lead + Sound Designer |
| Launch and distribution | Community & Social Lead |
| Funnel measurement | Data Analyst → Analytics Director |
| Save-safe migration, continuity | Growth Surface Engineer + QA Tester |

---

## Sources

- [Mobile Game Marketing Strategy in 2026 — Stepico](https://stepico.com/blog/mobile-game-marketing-strategy-in-2026/)
- [The 2026 Guide to Mobile Game Marketing Strategy — Gamelight](https://www.gamelight.io/post/the-2026-guide-to-mobile-game-marketing-strategy)
- [Most Viral Browser Games on TikTok (2026) — OtterGames](https://ottergames.org/blog/most-viral-browser-games-on-tiktok/)
- [Branding Agency Roles — DesignRush](https://www.designrush.com/agency/logo-branding/trends/branding-agency-roles)
- [A Practical Guide to Protecting Your Indie Game — Corsearch](https://corsearch.com/content-library/blog/a-practical-guide-to-protecting-your-indie-game/)
- [IP Issues for Game Developers, Part 1: Trademarks 101 — Snell & Wilmer](https://www.swlaw.com/publication/intellectual-property-issues-for-game-developers-and-operators-part-1-trademarks-101-names-logos-trade-dress-and-protecting-a-brand-before-launch/)
