"""Headless capture of the achievements-related screens, for view-only review.

Drives the real game render paths against an offscreen surface and writes PNGs
under docs/achievements/screenshots/. No production code is touched; the unlock
state is supplied as a plain store dict so the on-disk save is never read or
written.

    python tools/capture_achievement_shots.py
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
import random
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()

OUTDIR = os.path.join(_ROOT, "docs", "achievements", "screenshots")


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    from game.scenes import App, STATE_MENU, STATE_STATS
    from game.achievements_screen import AchievementsScene
    from game.world import World
    from game import achievements as ach

    def save(app, name):
        pygame.image.save(app.screen, os.path.join(OUTDIR, name + ".png"))
        print("  saved", name)

    app = App()
    app._cooldown_t = 0.0
    app._fetch_pending = False

    # The two achievements demoed across the unlock-toast and unlocked-list
    # shots: the first two of the first category, so they sit at the top of the
    # list (visible without scrolling) and read as the same pair throughout.
    id_a, id_b = (a.id for a in ach.BY_CAT[ach.CATEGORY_ORDER[0]][:2])
    title_a = ach.BY_ID[id_a].title
    title_b = ach.BY_ID[id_b].title

    # ── 1. Main menu ──────────────────────────────────────────────────────
    random.seed(100)
    app.world = World()
    for _ in range(40):
        app.world.world_idle_tick(1 / 60)
    app.hud.title_t = 1.1
    app.session_best = 47          # App.best is a read-only view of this
    app.state = STATE_MENU
    app._render()
    save(app, "menu")

    # ── 2. Achievements screen — fresh profile (nothing unlocked) ─────────
    app.achievements = AchievementsScene()
    blank = ach._blank()
    app.achievements.render(app.screen, 1 / 60, blank)
    save(app, "achievements_initial")

    # A run worth summarising — realistic stats behind the unlock toasts.
    def fresh_run():
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

    # ── 3 & 4. Run summary with each unlock toast visible ─────────────────
    # Only one toast shows at a time, so the two-in-a-run case is two frames.
    app.world = fresh_run()
    app.session_best = 47
    app._new_best = False
    app.hud.title_t = 1.4
    app._stats_t = 1.5
    app._achv_toast_t = 1.4          # mid-window → full opacity
    app.state = STATE_STATS

    app._achv_toast_queue = [id_a, id_b]
    app._render()
    save(app, "run_summary_unlock_1")

    app._achv_toast_queue = [id_b]
    app._render()
    save(app, "run_summary_unlock_2")

    # ── 5. Achievements screen — after the two are earned ─────────────────
    store = ach._blank()
    store["unlocked"][id_a] = 1
    store["unlocked"][id_b] = 1
    app.achievements = AchievementsScene()
    app.achievements.render(app.screen, 1 / 60, store)
    save(app, "achievements_unlocked")

    print(f"Done. Demoed pair: {title_a!r}, {title_b!r}")


if __name__ == "__main__":
    main()
