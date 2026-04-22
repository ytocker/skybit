"""
Deterministic gameplay-moment screenshot generator for a review pass.

Writes 20 screenshots into docs/review/ covering scene states, core gameplay
moments, tension/edge cases, difficulty variation, and biome variety. Each
function scripts a specific scene (no AI — direct state manipulation), so
the captures are repeatable frame-for-frame.
"""
import os
import random
import sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from game import config as cfg
cfg.SCORES_FILE = "/tmp/playtest_shots_scores.json"
try:
    os.remove(cfg.SCORES_FILE)
except OSError:
    pass

from game.scenes import App, STATE_MENU, STATE_PLAY, STATE_NAMEENTRY, STATE_GAMEOVER
from game.config import W, H, GAP_MIN, GAP_START, PIPE_SPACING, PIPE_W, TRIPLE_DURATION, COMBO_WINDOW
from game.entities import Bird, Pipe, Coin, Mushroom, Particle, FloatText
from game.nameentry import NameEntry
from game.storage import save_scores
from game.biome import CYCLE_SECONDS
from game.draw import (
    COIN_GOLD, COIN_LIGHT, UI_GOLD, UI_ORANGE, UI_CREAM, PARTICLE_GOLD,
    PARTICLE_WHT, PARTICLE_ORNG, PARTICLE_CRIM, BIRD_RED,
)
import math

OUT = os.path.join(ROOT, "docs", "review")
os.makedirs(OUT, exist_ok=True)


def _save(app, name):
    pygame.image.save(app.screen, os.path.join(OUT, name))
    print("wrote", name)


def _advance(app, frames, dt=1 / 60.0):
    for _ in range(frames):
        app._update(dt)


def _setup_world(app, *, score=0, coins=0, biome_t=12.0, seed=1):
    random.seed(seed)
    app._start_play()
    w = app.world
    w.score = score
    w.coin_count = coins
    w.biome_time = biome_t
    return w


def _clear_and_spawn(w, pipe_xs, gap_y_list, gap_h=None, coin_patterns=None):
    """Replace world pipes with a specific deterministic set."""
    from game.config import GAP_START
    if gap_h is None:
        gap_h = GAP_START
    w.pipes.clear()
    w.coins.clear()
    w.mushrooms.clear()
    for i, (x, gy) in enumerate(zip(pipe_xs, gap_y_list)):
        p = Pipe(x, gy, gap_h)
        w.pipes.append(p)
        pattern = coin_patterns[i] if coin_patterns and i < len(coin_patterns) else "arc"
        cx = x + PIPE_W + PIPE_SPACING * 0.5
        if pattern == "arc":
            for k in range(5):
                t = k / 4
                ang = -math.pi * 0.35 + math.pi * 0.7 * t
                w.coins.append(Coin(cx + math.sin(ang) * 50,
                                    gy + math.cos(ang) * 34 - 8))
        elif pattern == "line":
            for k in range(4):
                w.coins.append(Coin(cx - 40 + k * 22, gy))
        elif pattern == "none":
            pass


# ──────────────────────────────────────────────────────────────────────────────
# A. Scene-flow states
# ──────────────────────────────────────────────────────────────────────────────

def shot_menu():
    app = App()
    app._cooldown_t = 0.0
    app.state = STATE_MENU
    app.world.biome_time = 15.0
    _advance(app, 30)
    app._render()
    _save(app, "01_menu.png")


def shot_gameover_tryagain():
    app = App()
    app._cooldown_t = 0.0
    _setup_world(app, biome_t=15.0)
    app.world._die()
    app._advance = None
    app._cooldown_t = 0.35
    app.state = STATE_GAMEOVER
    app.prev_best_at_death = 0
    app._render()
    _save(app, "02_gameover_tryagain.png")


def shot_gameover_leaderboard():
    # Pre-seed a full top-10 with one highlighted row
    save_scores([
        {"name": "ACE", "score": 87},
        {"name": "MAX", "score": 72},
        {"name": "ZOE", "score": 60},
        {"name": "KAI", "score": 51},
        {"name": "IRA", "score": 42},
        {"name": "BEN", "score": 28},
        {"name": "EVA", "score": 16},
        {"name": "SAM", "score": 14},
        {"name": "LEO", "score": 9},
        {"name": "MEI", "score": 5},
    ])
    app = App()
    app._cooldown_t = 0.25
    _setup_world(app, biome_t=15.0)
    app.world.score = 42  # matches IRA (rank 4)
    app.world._die()
    app.state = STATE_GAMEOVER
    app.highlight_rank = 4
    app.prev_best_at_death = 87
    app._render()
    _save(app, "03_gameover_leaderboard.png")


def shot_gameover_new_best():
    save_scores([
        {"name": "KAT", "score": 22},
        {"name": "RIO", "score": 14},
        {"name": "SAM", "score": 8},
    ])
    app = App()
    _setup_world(app, biome_t=60.0)
    app.world.score = 31
    app.world._die()
    app.state = STATE_GAMEOVER
    app._cooldown_t = 0.2
    app.highlight_rank = 0
    app.prev_best_at_death = 22
    _advance(app, 4)
    app._render()
    _save(app, "04_gameover_new_best.png")


def shot_nameentry():
    save_scores([])
    app = App()
    _setup_world(app, biome_t=50.0)
    app.world.score = 27
    app.name_entry = NameEntry(27, 1)
    app.name_entry.press_char("Y")
    app.name_entry.press_char("A")
    app.state = STATE_NAMEENTRY
    _advance(app, 10)
    app._render()
    _save(app, "05_nameentry.png")


# ──────────────────────────────────────────────────────────────────────────────
# B. Core gameplay moments
# ──────────────────────────────────────────────────────────────────────────────

def shot_gap_traversal():
    app = App()
    w = _setup_world(app, score=3, biome_t=20.0, seed=7)
    _clear_and_spawn(w,
                     pipe_xs=[180, 180 + PIPE_SPACING, 180 + 2 * PIPE_SPACING],
                     gap_y_list=[310, 250, 370])
    w.bird.x = 90 + 15
    w.bird.y = 295
    w.bird.vy = 40
    w.bird.frame_t = 1.8
    _advance(app, 2)
    app._render()
    _save(app, "06_gap_traversal.png")


def shot_coin_grab():
    app = App()
    w = _setup_world(app, score=4, coins=3, biome_t=20.0, seed=9)
    _clear_and_spawn(w,
                     pipe_xs=[220, 220 + PIPE_SPACING],
                     gap_y_list=[300, 260])
    # Place coin right at the bird's position + spawn pickup particles
    cx, cy = w.bird.x + 4, w.bird.y + 2
    w.coins.append(Coin(cx, cy))
    w.coins[-1].collected = True
    # Reproduce _on_coin's particle burst
    for _ in range(10):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(80, 220)
        col = random.choice((PARTICLE_GOLD, COIN_LIGHT, PARTICLE_WHT))
        w.particles.append(Particle(cx, cy,
                                    math.cos(ang) * spd, math.sin(ang) * spd,
                                    0.6, 3, col, gravity=300))
    w.float_texts.append(FloatText("+1", cx, cy - 8, UI_GOLD, size=22, life=0.9))
    _advance(app, 5)
    app._render()
    _save(app, "07_coin_grab.png")


def shot_combo_x5():
    app = App()
    w = _setup_world(app, score=11, coins=8, biome_t=30.0, seed=11)
    _clear_and_spawn(w,
                     pipe_xs=[260, 260 + PIPE_SPACING],
                     gap_y_list=[290, 320])
    w.combo = 5
    w.combo_timer = COMBO_WINDOW * 0.85
    w.bird.y = 285
    w.bird.vy = -200
    w.bird.frame_t = 0.5
    _advance(app, 2)
    app._render()
    _save(app, "08_combo_x5.png")


def shot_mushroom_in_gap():
    app = App()
    w = _setup_world(app, score=6, coins=5, biome_t=40.0, seed=13)
    _clear_and_spawn(w,
                     pipe_xs=[200, 200 + PIPE_SPACING],
                     gap_y_list=[320, 280])
    # Mushroom pre-pickup, floating in front of the bird
    w.mushrooms.append(Mushroom(w.bird.x + 110, 315))
    w.bird.y = 300; w.bird.vy = 40
    _advance(app, 4)
    app._render()
    _save(app, "09_mushroom_in_gap.png")


def shot_mushroom_pickup():
    app = App()
    w = _setup_world(app, score=6, coins=6, biome_t=40.0, seed=15)
    _clear_and_spawn(w,
                     pipe_xs=[260, 260 + PIPE_SPACING],
                     gap_y_list=[310, 280])
    # Trigger the pickup + time-slow + sparkle burst
    m = Mushroom(w.bird.x + 6, w.bird.y + 2)
    w.mushrooms.append(m)
    m.collected = True
    w.triple_timer = TRIPLE_DURATION
    w.shake_mag = 3.0; w.shake_t = 0.25
    w.time_scale = 0.35; w.time_scale_t = 0.2
    for _ in range(30):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(100, 320)
        col = random.choice((UI_ORANGE, UI_GOLD, BIRD_RED, UI_CREAM))
        w.particles.append(Particle(m.x, m.y,
                                    math.cos(ang) * spd, math.sin(ang) * spd,
                                    0.9, 5, col, gravity=150))
    w.float_texts.append(FloatText("3X POWER!", m.x, m.y - 22,
                                   UI_ORANGE, size=26, life=1.4, vy=-30))
    _advance(app, 2)
    app._render()
    _save(app, "10_mushroom_pickup.png")


def shot_triple_active_plus3():
    app = App()
    w = _setup_world(app, score=14, coins=9, biome_t=45.0, seed=17)
    _clear_and_spawn(w,
                     pipe_xs=[240, 240 + PIPE_SPACING],
                     gap_y_list=[300, 260])
    w.triple_timer = TRIPLE_DURATION * 0.65
    # Immediately-collected coin during the buff
    cx, cy = w.bird.x + 2, w.bird.y
    w.coins.append(Coin(cx, cy)); w.coins[-1].collected = True
    for _ in range(12):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(80, 220)
        col = random.choice((PARTICLE_GOLD, COIN_LIGHT, PARTICLE_WHT))
        w.particles.append(Particle(cx, cy,
                                    math.cos(ang) * spd, math.sin(ang) * spd,
                                    0.6, 3, col, gravity=300))
    w.float_texts.append(FloatText("+3", cx, cy - 8,
                                   UI_ORANGE, size=24, life=0.9))
    _advance(app, 4)
    app._render()
    _save(app, "11_triple_active_+3.png")


# ──────────────────────────────────────────────────────────────────────────────
# C. Tension / edge moments
# ──────────────────────────────────────────────────────────────────────────────

def shot_ceiling_close():
    app = App()
    w = _setup_world(app, score=9, biome_t=25.0, seed=21)
    _clear_and_spawn(w,
                     pipe_xs=[220, 220 + PIPE_SPACING],
                     gap_y_list=[260, 300])
    w.bird.y = 26; w.bird.vy = -140
    w.bird.frame_t = 0.3
    _advance(app, 1)
    app._render()
    _save(app, "12_ceiling_close.png")


def shot_floor_mist():
    app = App()
    w = _setup_world(app, score=12, biome_t=90.0, seed=23)
    _clear_and_spawn(w,
                     pipe_xs=[220, 220 + PIPE_SPACING],
                     gap_y_list=[400, 420])
    w.bird.y = 540; w.bird.vy = 240
    w.bird.frame_t = 2.5
    _advance(app, 1)
    app._render()
    _save(app, "13_floor_mist.png")


def shot_death_hitflash():
    app = App()
    w = _setup_world(app, score=8, biome_t=30.0, seed=25)
    _clear_and_spawn(w,
                     pipe_xs=[110, 110 + PIPE_SPACING],
                     gap_y_list=[230, 320])
    w.bird.y = 160; w.bird.vy = 300
    w._die()
    w.hit_flash = 0.30
    w.shake_t = 0.35; w.shake_mag = 8
    _advance(app, 2)
    app._render()
    _save(app, "14_death_hitflash.png")


def shot_death_particles():
    app = App()
    w = _setup_world(app, score=22, biome_t=40.0, seed=27)
    _clear_and_spawn(w,
                     pipe_xs=[120, 120 + PIPE_SPACING],
                     gap_y_list=[330, 250])
    w.bird.y = 400; w.bird.vy = 100
    w._die()
    _advance(app, 16)
    app._render()
    _save(app, "15_death_particles.png")


# ──────────────────────────────────────────────────────────────────────────────
# D. Difficulty variation
# ──────────────────────────────────────────────────────────────────────────────

def shot_max_difficulty():
    app = App()
    w = _setup_world(app, score=42, biome_t=60.0, seed=31)
    _clear_and_spawn(w,
                     pipe_xs=[150, 150 + PIPE_SPACING, 150 + 2 * PIPE_SPACING],
                     gap_y_list=[280, 330, 260],
                     gap_h=GAP_MIN)
    w.bird.y = 275; w.bird.vy = -80; w.bird.frame_t = 0.8
    _advance(app, 2)
    app._render()
    _save(app, "16_max_difficulty.png")


def shot_low_difficulty():
    app = App()
    w = _setup_world(app, score=2, biome_t=20.0, seed=33)
    _clear_and_spawn(w,
                     pipe_xs=[200, 200 + PIPE_SPACING, 200 + 2 * PIPE_SPACING],
                     gap_y_list=[320, 260, 350],
                     gap_h=GAP_START)
    w.bird.y = 300; w.bird.vy = 50; w.bird.frame_t = 1.2
    _advance(app, 2)
    app._render()
    _save(app, "17_low_difficulty.png")


# ──────────────────────────────────────────────────────────────────────────────
# E. Biome variety
# ──────────────────────────────────────────────────────────────────────────────

def _biome_shot(name, phase):
    t = CYCLE_SECONDS * phase
    app = App()
    w = _setup_world(app, score=9, biome_t=t, seed=41 + int(phase * 100))
    _clear_and_spawn(w,
                     pipe_xs=[200, 200 + PIPE_SPACING],
                     gap_y_list=[300, 350])
    w.bird.y = 280; w.bird.vy = -60; w.bird.frame_t = 1.0
    _advance(app, 2)
    app._render()
    _save(app, name)


def shot_biome_golden():   _biome_shot("18_biome_golden_hour.png", 0.14)
def shot_biome_dusk():     _biome_shot("19_biome_dusk.png",         0.44)
def shot_biome_predawn():  _biome_shot("20_biome_predawn.png",      0.74)


# ──────────────────────────────────────────────────────────────────────────────
# Driver
# ──────────────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    pygame.display.set_mode((W, H))
    # A
    shot_menu()
    shot_gameover_tryagain()
    shot_gameover_leaderboard()
    shot_gameover_new_best()
    shot_nameentry()
    # B
    shot_gap_traversal()
    shot_coin_grab()
    shot_combo_x5()
    shot_mushroom_in_gap()
    shot_mushroom_pickup()
    shot_triple_active_plus3()
    # C
    shot_ceiling_close()
    shot_floor_mist()
    shot_death_hitflash()
    shot_death_particles()
    # D
    shot_max_difficulty()
    shot_low_difficulty()
    # E
    shot_biome_golden()
    shot_biome_dusk()
    shot_biome_predawn()
    print("done — 20 shots in docs/review/")


if __name__ == "__main__":
    main()
