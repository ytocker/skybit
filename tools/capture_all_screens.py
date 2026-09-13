"""Seeded headless capture of every non-gameplay screen, for before/after
review. Drives the real App._render per scene state. Two modes:

  capture <outdir>                 render all screens to outdir
  compose <beforedir> <afterdir> <outdir>   per-screen before/after sheets

RNG is reseeded per screen so the gameplay frame behind pause/stats is
identical across two runs of different code — before/after then differs only
by the UI code.
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


def _sim_play(seconds=2.6, dt=1 / 60):
    from game.config import H
    from game.world import World
    w = World()
    w.ready_t = 0.0
    w.flap()
    for _ in range(int(seconds / dt)):
        if w.bird.y > H * 0.42:
            w.flap()
        w.update(dt)
        if w.game_over:
            break
    return w


def capture(outdir):
    os.makedirs(outdir, exist_ok=True)
    from game.config import W, H
    from game.scenes import (App, STATE_MENU, STATE_PAUSE, STATE_STATS,
                             STATE_NAMEENTRY, STATE_LEADERBOARD, STATE_POWERUPS)
    from game.world import World
    from game.powerup_help import PowerUpHelpScene

    def save(app, name):
        pygame.image.save(app.screen, os.path.join(outdir, name + ".png"))
        print("  saved", name)

    app = App()
    app._cooldown_t = 0.0
    app._fetch_pending = False

    # Menu
    random.seed(100)
    app.world = World()
    for _ in range(40):
        app.world.world_idle_tick(1 / 60)
    app.hud.title_t = 1.1
    app.session_best = 47
    app.state = STATE_MENU
    app._render()
    save(app, "menu")

    # Power-ups explainer
    random.seed(101)
    app.powerup_help = PowerUpHelpScene()
    for _ in range(30):
        app.powerup_help.update(1 / 60)
    app.state = STATE_POWERUPS
    app._render()
    save(app, "powerups")

    # Pause (live pillars behind)
    random.seed(42)
    app.world = _sim_play()
    app.world.score = 8
    app.hud.title_t = 0.9
    app.state = STATE_PAUSE
    app._render()
    save(app, "pause")

    # Run summary / stats (NEW BEST)
    random.seed(42)
    w = _sim_play()
    w.score = 47
    w.pillars_passed = 47
    w.coin_count = 31
    w.coins = []
    w.coins_spawned = 38
    w.time_alive = 132.0
    w.flap_count = 198
    w.powerups_picked = {"triple": 2, "magnet": 1, "slowmo": 1, "ghost": 1}
    app.world = w
    app.session_best = 47
    app._new_best = True
    app.hud.title_t = 1.4
    app._stats_t = 1.5
    app.state = STATE_STATS
    app._render()
    save(app, "stats")

    # Name entry (native)
    app._name_input_buf = "PIP"
    app.hud.title_t = 0.9
    app.state = STATE_NAMEENTRY
    app._render()
    save(app, "name_entry")

    # Leaderboard
    app._lb_scores = [
        {"name": "Hawkins", "score": 148}, {"name": "Garrick", "score": 132},
        {"name": "Atticus", "score": 117}, {"name": "Pip", "score": 104},
        {"name": "Mira", "score": 96}, {"name": "Bo", "score": 83},
        {"name": "Quill", "score": 61}, {"name": "Wren", "score": 38},
        {"name": "Stilt", "score": 29}, {"name": "Cinder", "score": 18},
    ]
    app._lb_player_rank = 4
    app._lb_fetch_error = ""
    app._cooldown_t = 0.0
    app.hud.title_t = 1.4
    app.state = STATE_LEADERBOARD
    app._render()
    save(app, "leaderboard")


SCREENS = [
    ("menu", "MAIN MENU"),
    ("powerups", "POWER-UPS"),
    ("pause", "PAUSE"),
    ("stats", "RUN SUMMARY"),
    ("name_entry", "NAME ENTRY"),
    ("leaderboard", "LEADERBOARD"),
]


def compose(beforedir, afterdir, outdir):
    os.makedirs(outdir, exist_ok=True)
    from game.config import W, H
    title_f = pygame.font.Font(None, 34)
    sub_f = pygame.font.Font(None, 26)
    big_f = pygame.font.Font(None, 30)
    MARGIN, GAP, HEADER = 22, 26, 70

    def load(d, key):
        p = os.path.join(d, key + ".png")
        return pygame.image.load(p) if os.path.exists(p) else None

    def placeholder(text):
        s = pygame.Surface((W, H))
        s.fill((24, 18, 34))
        msg = big_f.render(text, True, (200, 120, 120))
        s.blit(msg, msg.get_rect(center=(W // 2, H // 2)))
        return s

    for key, label in SCREENS:
        before = load(beforedir, key)
        after = load(afterdir, key)
        if before is None and after is None:
            continue
        if before is None:
            before = placeholder("(did not exist)")
        if after is None:
            after = placeholder("REMOVED")
        canvas = pygame.Surface((MARGIN * 2 + W * 2 + GAP, HEADER + H + MARGIN))
        canvas.fill((18, 16, 30))
        t = title_f.render(label, True, (250, 224, 140))
        canvas.blit(t, t.get_rect(center=(canvas.get_width() // 2, 22)))
        lx, rx = MARGIN, MARGIN + W + GAP
        canvas.blit(before, (lx, HEADER))
        canvas.blit(after, (rx, HEADER))
        pygame.draw.rect(canvas, (90, 80, 110), (lx, HEADER, W, H), 1)
        pygame.draw.rect(canvas, (90, 80, 110), (rx, HEADER, W, H), 1)
        for lbl, cx in (("BEFORE", lx + W // 2), ("AFTER", rx + W // 2)):
            s = sub_f.render(lbl, True, (180, 172, 195))
            canvas.blit(s, s.get_rect(center=(cx, 50)))
        out = os.path.join(outdir, f"{key}_before_after.png")
        pygame.image.save(canvas, out)
        print("  composed", out)


if __name__ == "__main__":
    if sys.argv[1] == "capture":
        capture(sys.argv[2])
    elif sys.argv[1] == "compose":
        compose(sys.argv[2], sys.argv[3], sys.argv[4])
