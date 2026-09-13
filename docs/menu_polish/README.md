# Skybit v4 — Menu Redesign (Pip Scarlet)

The selected and final 7-screen UI set. Every non-gameplay screen uses
the same primitives — polished v3 night-sky backdrop, gold-on-red
SKYBIT-style title, scarlet pills with gold trim, dark-navy
gold-trimmed cards, hero circular score medallion. Rendered at
**720 × 1280** (2× the game canvas) so every detail is crisp on web
and on modern mobile. The how-to-play screen is not mocked — it
remains the existing animated intro clip.

Generator: [`tools/gen_scarlet_set.py`](../../tools/gen_scarlet_set.py)
Earlier exploration rounds (5 polish directions, 5 safe pill colours,
5 aggressive on-theme variants, the rejected ROYAL set, etc.) live
in [`archive/`](archive/) for reference.

| # | Screen | File |
|---|---|---|
| 1 | **Main menu** — SKYBIT title, 3 scarlet pills, BEST + TOP 10 panels | [v3_scarlet_main.png](v3_scarlet_main.png) |
| 2 | **Pause overlay** — score medallion + PAUSED + RESUME / RESTART / MAIN MENU | [v3_scarlet_pause.png](v3_scarlet_pause.png) |
| 3 | **Run summary** — big score medallion w/ scarlet ribbon + 5-row stat card + TAP TO CONTINUE | [v3_scarlet_stats.png](v3_scarlet_stats.png) |
| 4 | **Game over (NEW BEST)** — gold NEW BEST ribbon + score medallion inside gold sparkle burst + TAP TO RETRY / MAIN MENU | [v3_scarlet_gameover.png](v3_scarlet_gameover.png) |
| 5 | **Name entry** — trophy + NEW HIGH SCORE! + engraved nameplate + on-screen QWERTY keyboard + SUBMIT / SKIP | [v3_scarlet_name_entry.png](v3_scarlet_name_entry.png) |
| 6 | **Leaderboard** — TOP 10 between twin trophies + 10 ranked cards w/ gold/silver/bronze medals (top 3) + player row highlighted | [v3_scarlet_leaderboard.png](v3_scarlet_leaderboard.png) |
| 7 | **Power-ups help** — 2×3 card grid w/ the EXACT in-game power-up sprites + Surprise card + EFFECTS LAST 8 SECONDS ribbon | [v3_scarlet_powerups.png](v3_scarlet_powerups.png) |

## Brand bar

* **Palette** — gold `#F0C040`, scarlet `#F03737 → #941414`, deep
  purple `#0C0826`, night-deep `#060115`, red outline `#A82010`,
  cream text `#FAEED2`.
* **Font** — bundled Liberation Sans (Bold + Regular) from
  `game/assets/`.
* **Primary action** — always a scarlet pill with a soft gold glow
  halo so the player instantly knows what to tap.
* **Hero score readout** — circular gold medallion with a slim
  scarlet accent ring inside, radial laurel ticks, dark-navy
  interior, label-at-top + big gold value, optional scarlet ribbon
  tail for celebratory moments.
