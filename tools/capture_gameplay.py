"""Headless capture of a live gameplay frame (STATE_PLAY) so the in-game UI
(score pill, coins counter, pause button, pillars, coins, bird) can be
reviewed. Runs a short seeded sim that flaps to stay alive, then renders the
real App._render. Run from repo root: python tools/capture_gameplay.py
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

from game.config import W, H
from game.scenes import App, STATE_PLAY
from game.world import World

OUT = os.path.join(_ROOT, "docs", "ui_audit", "gameplay.png")


def _run(seed, seconds):
    random.seed(seed)
    app = App()
    if hasattr(app, "_splash_covering"):
        app._splash_covering = False
    w = World()
    w.ready_t = 0.0
    w.flap()
    app.world = w
    app.state = STATE_PLAY
    dt = 1 / 60
    for _ in range(int(seconds / dt)):
        # Flap toward the nearest upcoming gap centre (a touch above it, since
        # Pip falls) so the run threads pillars and survives long enough to
        # show a real score + coins on screen.
        target = H * 0.45
        ahead = [p for p in w.pipes if p.x > w.bird.x - 18]
        if ahead:
            target = min(ahead, key=lambda p: p.x).gap_y - 12
        if w.bird.y > target:
            w.flap()
        w.update(dt)
        if w.game_over:
            break
    return app, w


def capture(seconds=7.0):
    # Pick the first seed that survives with a believable score and at least
    # one coin on screen, so the captured frame shows the live HUD in action.
    best = None
    for seed in range(40):
        app, w = _run(seed, seconds)
        on_screen_coin = any(0 < c.x < W for c in w.coins)
        if not w.game_over and w.score >= 3 and on_screen_coin:
            best = (app, w)
            break
        if best is None and not w.game_over and w.score >= 2:
            best = (app, w)  # fallback: alive with some score
    if best is None:
        best = (app, w)
    app, w = best
    app._render()
    pygame.image.save(app.screen, OUT)
    print(f"saved {OUT}  score={w.score} coins={w.coin_count} "
          f"on_screen_coins={sum(1 for c in w.coins if 0 < c.x < W)} "
          f"game_over={w.game_over}")


if __name__ == "__main__":
    capture()
