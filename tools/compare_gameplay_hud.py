"""Before/after of the gameplay HUD over ONE shared, identical gameplay frame.

Before = the current live HUD (real HUD.draw_play). After = the corrected
candidate C (reused from tools/gen_gameplay_hud_round4.cand_plaques). The world
is built once (same deterministic seed-selection as the round-4 generator) so
the only difference between the two panels is the HUD itself.
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
import random
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import pygame
pygame.init()

from game.config import W, H
from game.scenes import App, STATE_PLAY
from game.world import World
import gen_gameplay_hud_round4 as r4


def build_world():
    """Same deterministic survive-the-pillars selection the round-4 backdrop
    uses, but return the live (app, world) so we can render either HUD on it."""
    best = None
    for seed in range(60):
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
        for _ in range(int(7.0 / dt)):
            target = H * 0.45
            ahead = [p for p in w.pipes if p.x > w.bird.x - 18]
            if ahead:
                target = min(ahead, key=lambda p: p.x).gap_y - 12
            if w.bird.y > target:
                w.flap()
            w.update(dt)
            if w.game_over:
                break
        on_screen = any(0 < c.x < W for c in w.coins)
        if (not w.game_over and w.score >= 3 and on_screen
                and 140 < w.bird.y < 470):
            return app, w
        if best is None and not w.game_over and w.score >= 2:
            best = (app, w)
    return best


app, w = build_world()

# Match the candidate's representative values (score 12, coins x7) so both
# panels show the same numbers and only the HUD design differs.
w.score = 12
w.coin_count = 7

# BEFORE — real current HUD over the frame.
app._render()
before = app.screen.copy()

# Shared backdrop — same frame with the HUD suppressed.
app.hud.draw_play = lambda *a, **k: None
app._render()
backdrop = app.screen.copy()

# AFTER — corrected candidate C HUD over the same backdrop.
after = backdrop.copy()
r4.cand_plaques(after)

# Compose.
MARGIN, GAP, HEADER = 24, 28, 56
canvas = pygame.Surface((MARGIN * 2 + W * 2 + GAP, HEADER + H + MARGIN))
canvas.fill((18, 16, 30))
title_f = pygame.font.Font(None, 38)
sub_f = pygame.font.Font(None, 24)


def header(label, sublabel, cx):
    t = title_f.render(label, True, (245, 235, 210))
    canvas.blit(t, t.get_rect(center=(cx, 22)))
    s = sub_f.render(sublabel, True, (170, 160, 185))
    canvas.blit(s, s.get_rect(center=(cx, 44)))


lx, rx = MARGIN, MARGIN + W + GAP
canvas.blit(before, (lx, HEADER))
canvas.blit(after, (rx, HEADER))
pygame.draw.rect(canvas, (90, 80, 110), (lx, HEADER, W, H), 1)
pygame.draw.rect(canvas, (90, 80, 110), (rx, HEADER, W, H), 1)
header("BEFORE", "current HUD", lx + W // 2)
header("AFTER", "Adventure Plaques HUD", rx + W // 2)

OUT = os.path.join(_ROOT, "docs", "gameplay_hud", "gameplay_hud_before_after.png")
pygame.image.save(canvas, OUT)
print("saved", OUT)
