"""
Headless screenshot generator. Uses SDL_VIDEODRIVER=dummy so it runs
without a real display. Produces 4 PNGs into docs/screenshots/.

Usage:  python tools/snapshot.py
"""
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# Make repo root importable when run from anywhere
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))  # init video subsystem for SRCALPHA

from game.config import W, H  # noqa: E402
from game.scenes import App, STATE_MENU, STATE_PLAY, STATE_GAMEOVER  # noqa: E402


OUT_DIR = os.path.join(ROOT, "docs", "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)


def _render_to_png(app, name):
    app._render()
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(app.screen, path)
    print("wrote", path)


def _tick_world(app, n, flap_every=18):
    for i in range(n):
        if flap_every and i % flap_every == 0:
            app.world.flap()
        app._update(1 / 60)


def snap_title():
    random.seed(42)
    app = App()
    app.state = STATE_MENU
    for _ in range(80):
        app._update(1 / 60)
    _render_to_png(app, "title.png")


def snap_gameplay():
    random.seed(7)
    app = App()
    app.state = STATE_PLAY
    # Compose a hand-placed frame: keep a pipe onscreen with a visible coin arc
    from game.entities import Pipe, Coin
    from game.config import PIPE_W, GROUND_Y
    app.world.pipes.clear()
    app.world.coins.clear()
    p1 = Pipe(220, 330, 170)
    p2 = Pipe(220 + 280, 240, 170)
    app.world.pipes.extend((p1, p2))
    # an arc of coins just in front of p1
    import math
    for i, t in enumerate((0.0, 0.25, 0.5, 0.75, 1.0)):
        ang = -math.pi * 0.35 + math.pi * 0.7 * t
        cx = 170 + math.sin(ang) * 36
        cy = 320 + math.cos(ang) * 42 - 10
        app.world.coins.append(Coin(cx, cy))
    app.world.bird.y = 300
    app.world.bird.vy = -80
    # drive a few frames so particles/trail exist
    for _ in range(8):
        app.world.flap()
        app._update(1 / 60)
    app.world.coin_count = 7
    app.world.score = 12
    app.world.combo = 4
    app.world.combo_timer = 1.2
    _render_to_png(app, "gameplay.png")


def snap_mushroom():
    random.seed(21)
    app = App()
    app.state = STATE_PLAY
    from game.entities import Pipe, Coin, Mushroom, Particle
    import math
    app.world.pipes.clear()
    app.world.coins.clear()
    app.world.mushrooms.clear()
    app.world.pipes.append(Pipe(230, 300, 170))
    for i in range(5):
        ang = -math.pi * 0.4 + math.pi * 0.8 * (i / 4)
        app.world.coins.append(Coin(150 + math.sin(ang) * 40, 300 + math.cos(ang) * 42 - 10))
    app.world.bird.y = 280
    app.world.bird.vy = -60
    for _ in range(6):
        app._update(1 / 60)
    # Radial particle burst around bird position for mushroom-pickup feel
    for _ in range(18):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(80, 220)
        app.world.particles.append(Particle(
            app.world.bird.x, app.world.bird.y,
            math.cos(ang) * spd, math.sin(ang) * spd,
            random.uniform(0.4, 0.9), random.randint(3, 5),
            random.choice(((255, 215, 0), (255, 155, 30), (255, 245, 120))),
            gravity=120,
        ))
    app.world.triple_timer = 6.4
    app.world.score = 18
    app.world.coin_count = 11
    _render_to_png(app, "mushroom.png")


def snap_gameover():
    random.seed(99)
    app = App()
    app.state = STATE_PLAY
    for i in range(120):
        if i % 15 == 0:
            app.world.flap()
        app._update(1 / 60)
    # force game over
    app.world.score = 27
    app.best = 42
    app.prev_best_at_death = 42
    app.world._die()
    app.state = STATE_GAMEOVER
    app._cooldown_t = 0.5
    for _ in range(40):
        app._update(1 / 60)
    _render_to_png(app, "gameover.png")


if __name__ == "__main__":
    snap_title()
    snap_gameplay()
    snap_mushroom()
    snap_gameover()
    print("done")
