"""Headless visual audit of every non-gameplay screen.

Drives the real ``App._render`` per scene state (the same code path the game
runs) so each capture is pixel-faithful — including the menu's house+Pip
opener and the gameplay frame that shows through the pause overlay. Output
lands in ``docs/ui_audit/`` (excluded from the pygbag bundle). Run from repo
root: ``python tools/capture_menu_screens.py``.
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()

from game.config import W, H
from game.scenes import (
    App, STATE_MENU, STATE_PAUSE, STATE_STATS, STATE_NAMEENTRY,
    STATE_LEADERBOARD, STATE_INTRO, STATE_POWERUPS,
)
from game.world import World
from game.powerup_help import PowerUpHelpScene

OUT_DIR = os.path.join(_ROOT, "docs", "ui_audit")
os.makedirs(OUT_DIR, exist_ok=True)


def save(app, name):
    pygame.image.save(app.screen, os.path.join(OUT_DIR, name + ".png"))
    print(f"  saved {name}.png")


def sim_play(seconds=2.6, dt=1 / 60):
    """Run a short, gentle real game so pillars/coins populate the world —
    used as the live frame behind the pause overlay and the death screens.
    Flaps whenever Pip dips past mid-screen so the run stays alive."""
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


app = App()
app._cooldown_t = 0.0          # set by input handlers in-game; needed by _render
app._fetch_pending = False

# ── 1. Intro cinematic — representative frame per beat ───────────────────────
# Beat windows (game/intro.py): dawn 0-1, handoff 1-4, tutorial 4-12
# (jump/pillars/coins/powerups, 2 s each), arrival 12-15.
app.state = STATE_INTRO
for name, t in (
    ("01_intro_a_dawn",              0.7),
    ("01_intro_b_handoff",           2.6),
    ("01_intro_c_tutorial_jump",     5.0),
    ("01_intro_d_tutorial_pillars",  7.0),
    ("01_intro_e_tutorial_coins",    9.0),
    ("01_intro_f_tutorial_powerups", 11.0),
    ("01_intro_g_arrival",           13.8),
):
    app.intro.t = t
    app.intro._title_t = t
    app._render()
    save(app, name)

# ── 2. Main menu / title (gameplay opener as a static frame) ─────────────────
app.world = World()
for _ in range(40):
    app.world.world_idle_tick(1 / 60)
app.hud.title_t = 1.1
app.state = STATE_MENU
app.session_best = 47
app._render()
save(app, "02_menu")

# ── 3. Power-ups explainer ───────────────────────────────────────────────────
app.powerup_help = PowerUpHelpScene()
for _ in range(30):
    app.powerup_help.update(1 / 60)
app.state = STATE_POWERUPS
app._render()
save(app, "03_powerups_help")

# ── 4. Pause overlay (live pillars showing through) ──────────────────────────
app.world = sim_play()
app.world.score = 8
app.hud.title_t = 0.9
app.state = STATE_PAUSE
app._render()
save(app, "04_pause")

# ── 5. Run summary / stats (realistic finished run, NEW BEST) ────────────────
w = sim_play()
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
app._stats_t = 1.5            # past the 0.6 s reveal gate → buttons visible
app.state = STATE_STATS
app._render()
save(app, "05_stats")

# ── 6. High-score name entry (native screen; mid-typing) ─────────────────────
app._name_input_buf = "PIP"
app.hud.title_t = 0.9
app.state = STATE_NAMEENTRY
app._render()
save(app, "06_name_entry")

# ── 7. Top-10 leaderboard (sample scores, player highlighted) ────────────────
app._lb_scores = [
    {"name": "Hawkins", "score": 148},
    {"name": "Garrick", "score": 132},
    {"name": "Atticus", "score": 117},
    {"name": "Pip",     "score": 104},
    {"name": "Mira",    "score":  96},
    {"name": "Bo",      "score":  83},
    {"name": "Quill",   "score":  61},
    {"name": "Wren",    "score":  38},
    {"name": "Stilt",   "score":  29},
    {"name": "Cinder",  "score":  18},
]
app._lb_player_rank = 4
app._lb_fetch_error = ""
app._cooldown_t = 0.0
app.hud.title_t = 1.4
app.state = STATE_LEADERBOARD
app._render()
save(app, "07_leaderboard")

pygame.quit()
print("Done —", OUT_DIR)
