"""Shared scaffolding for the run-summary unlock-notice concept mockups.

Each concept script imports `render_backdrop()` to get an identical, freshly
rendered RUN SUMMARY surface (the real `HUD.draw_stats` output, WITHOUT the
current top toast) and `demo_titles()` for the achievements the mock run
unlocked. This keeps every concept's comparison honest — same backdrop, same
unlocked pair — so the showcase compares notice treatments, not backdrops.

Scratch tooling only; nothing here is imported by the game. `game/` is untouched.

    from tools.unlock_notice_common import render_backdrop, demo_titles
"""
import os
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame
if not pygame.get_init():
    pygame.init()


def _fresh_run():
    """A realistic, roomy-layout run (two power-up rows) to summarise."""
    from game.world import World
    w = World()
    w.score = 36
    w.pillars_passed = 36
    w.coin_count = 24
    w.coins = []
    w.coins_spawned = 31
    w.time_alive = 98.0
    w.flap_count = 154
    w.powerups_picked = {"triple": 2, "magnet": 1, "slowmo": 1}
    return w


def demo_ids(n: int = 2):
    """The first `n` achievements of the first category — same pair the
    ADDENDUM 7 screenshots demoed, so the story stays continuous."""
    from game import achievements as ach
    cat = ach.BY_CAT[ach.CATEGORY_ORDER[0]]
    return [a.id for a in cat[:n]]


def demo_titles(n: int = 2):
    from game import achievements as ach
    return [ach.BY_ID[i].title for i in demo_ids(n)]


def demo_varied_ids(n: int = 3):
    """The first achievement of each of the first `n` categories — distinct
    icon glyphs (pillar / coin / power-up / nerve …) and short titles, so a
    LIST of unlocked achievements reads as visually varied rows rather than a
    column of identical badges."""
    from game import achievements as ach
    return [ach.BY_CAT[cat][0].id for cat in ach.CATEGORY_ORDER[:n]]


def render_backdrop():
    """Return a fresh 360x640 Surface holding the real RUN SUMMARY screen with
    NO unlock notice drawn — the clean canvas each concept composites onto."""
    from game.scenes import App, STATE_STATS
    app = App()
    app._cooldown_t = 0.0
    app._fetch_pending = False
    app.world = _fresh_run()
    app.session_best = 47
    app._new_best = False
    app.hud.title_t = 1.4
    app._stats_t = 1.5
    app.state = STATE_STATS
    # draw_stats only — deliberately NOT _render(), which would add the toast.
    app.hud.draw_stats(app.screen, app.world, 1 / 60, app._stats_t,
                       best=app.best, new_best=app._new_best, show_prompt=False)
    return app.screen.copy()
