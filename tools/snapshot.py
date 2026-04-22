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
    app.world.coin_count = 2
    app.world.score = 0          # day biome for the primary shot
    app.world.combo = 4
    app.world.combo_timer = 1.2
    _render_to_png(app, "gameplay.png")


def _biome_scene(app, target_score, y_bird=300):
    """Populate a stable gameplay frame at a given score (drives biome phase)."""
    from game.entities import Pipe, Coin
    from game.config import PIPE_W
    import math
    app.state = STATE_PLAY
    app.world.pipes.clear()
    app.world.coins.clear()
    app.world.mushrooms.clear()
    app.world.pipes.extend((
        Pipe(220, 320, 165),
        Pipe(220 + 280, 240, 160),
    ))
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        ang = -math.pi * 0.35 + math.pi * 0.7 * t
        app.world.coins.append(Coin(170 + math.sin(ang) * 36, 315 + math.cos(ang) * 42 - 10))
    app.world.score = target_score
    app.world.coin_count = target_score // 2
    app.world.bird.y = y_bird
    app.world.bird.vy = -50
    for _ in range(6):
        app.world.flap()
        app._update(1 / 60)


def snap_sunset():
    random.seed(11)
    from game.biome import CYCLE_SECONDS
    app = App()
    _biome_scene(app, target_score=0)
    app.world.biome_time = CYCLE_SECONDS * 0.28   # → phase ≈ 0.32 sunset
    _render_to_png(app, "sunset.png")


def snap_night():
    random.seed(17)
    from game.biome import CYCLE_SECONDS
    app = App()
    _biome_scene(app, target_score=0)
    app.world.biome_time = CYCLE_SECONDS * 0.58   # → phase ≈ 0.62 night
    _render_to_png(app, "night.png")


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
    # use a disposable scores file so the seeded leaderboard is deterministic
    import game.config as cfg
    cfg.SCORES_FILE = "/tmp/snapshot_scores.json"
    try:
        os.remove(cfg.SCORES_FILE)
    except FileNotFoundError:
        pass

    app = App()
    # seed a plausible leaderboard
    from game.storage import insert_score
    seed = [("ACE", 84), ("DAN", 71), ("KIM", 65), ("SAM", 54), ("TIA", 47),
            ("JON", 39), ("RAE", 32), ("LEO", 28), ("AMY", 21), ("IAN", 18)]
    for name, sc in seed:
        app.scores, _ = insert_score(app.scores, name, sc)
    app.state = STATE_PLAY
    for i in range(60):
        if i % 15 == 0:
            app.world.flap()
        app._update(1 / 60)
    # Force a score that lands at rank 3
    app.world.score = 57
    app.prev_best_at_death = 84
    app.world._die()
    app._on_death()  # may go to nameentry
    if app.state == 2:  # STATE_NAMEENTRY
        for ch in "YAN":
            app.name_entry.press_char(ch)
        app.name_entry.submit()
        app._update(1 / 60)
    app._cooldown_t = 0.3
    for _ in range(30):
        app._update(1 / 60)
    _render_to_png(app, "gameover.png")


def snap_nameentry():
    random.seed(13)
    import game.config as cfg
    cfg.SCORES_FILE = "/tmp/snapshot_scores2.json"
    try:
        os.remove(cfg.SCORES_FILE)
    except FileNotFoundError:
        pass
    app = App()
    from game.storage import insert_score
    seed = [("ACE", 84), ("DAN", 71), ("KIM", 65), ("SAM", 54), ("TIA", 47),
            ("JON", 39), ("RAE", 32), ("LEO", 28), ("AMY", 21), ("IAN", 18)]
    for name, sc in seed:
        app.scores, _ = insert_score(app.scores, name, sc)
    app.state = STATE_PLAY
    for i in range(60):
        if i % 15 == 0:
            app.world.flap()
        app._update(1 / 60)
    app.world.score = 128
    app.world._die()
    app._on_death()
    # press Y and A
    app.name_entry.press_char("Y")
    app.name_entry.press_char("A")
    app._update(1 / 60)
    _render_to_png(app, "nameentry.png")


if __name__ == "__main__":
    snap_title()
    snap_gameplay()
    snap_sunset()
    snap_night()
    snap_mushroom()
    snap_nameentry()
    snap_gameover()
    print("done")
