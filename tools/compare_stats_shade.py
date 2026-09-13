"""Before/after for the run-summary shadow removal.

Renders the stats screen twice from one identical state — once with the
card / plaque / button shadows forced back on (before), once as it ships
now (after) — so the only pixel difference is the removed shades. Saves a
labelled side-by-side to docs/ui_audit/. Run from repo root.
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import random
random.seed(0)

import pygame
pygame.init()

from game.config import W, H
from game.scenes import App, STATE_STATS
from game.world import World
import game.hud as hud

OUT_DIR = os.path.join(_ROOT, "docs", "ui_audit")
os.makedirs(OUT_DIR, exist_ok=True)

T0 = 1.4  # fixed title pulse so both frames share the same animation phase

# Realistic finished run with a NEW BEST so every element is populated.
w = World()
w.score = 47
w.pillars_passed = 47
w.coin_count = 31
w.coins = []
w.coins_spawned = 38
w.time_alive = 132.0
w.flap_count = 198
w.powerups_picked = {"triple": 2, "magnet": 1, "slowmo": 1, "ghost": 1}

app = App()
app.world = w
app.session_best = 47
app._new_best = True
app._stats_t = 1.5      # past the 0.6 s reveal gate → buttons visible
app.state = STATE_STATS


def render_stats():
    app.hud.title_t = T0
    app._render()
    return app.screen.copy()


after = render_stats()

# Force every removed shade back on for the "before" frame: the pill
# button (PLAY AGAIN) shadow plus the stat-tile and score-plaque cast
# shadows. draw_stats calls these by their module-global names, so
# wrapping them here reinstates the old look.
_orig_pill = hud._pill_btn
def _shadowed_pill(*a, **k):
    k["shadow"] = True
    return _orig_pill(*a, **k)

_orig_tile = hud._stat_tile_chunky
def _shadowed_tile(surf, rect, *a, **k):
    sh = pygame.Surface((rect.w + 4, rect.h + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120),
                     (0, 0, rect.w + 4, rect.h + 4), border_radius=10)
    surf.blit(sh, (rect.x - 2, rect.y + 4))
    return _orig_tile(surf, rect, *a, **k)

_orig_plaque = hud._score_plaque
def _shadowed_plaque(surf, rect, *a, **k):
    sh = pygame.Surface((rect.w + 8, rect.h + 10), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 130),
                     (0, 0, rect.w + 8, rect.h + 10), border_radius=20)
    surf.blit(sh, (rect.x - 4, rect.y + 6))
    return _orig_plaque(surf, rect, *a, **k)

hud._pill_btn = _shadowed_pill
hud._stat_tile_chunky = _shadowed_tile
hud._score_plaque = _shadowed_plaque
before = render_stats()
hud._pill_btn = _orig_pill
hud._stat_tile_chunky = _orig_tile
hud._score_plaque = _orig_plaque

# ── Compose labelled side-by-side ────────────────────────────────────────────
MARGIN = 24
GAP = 28
HEADER = 56
canvas = pygame.Surface((MARGIN * 2 + W * 2 + GAP, HEADER + H + MARGIN))
canvas.fill((18, 16, 30))

title_f = pygame.font.Font(None, 38)
sub_f = pygame.font.Font(None, 24)

def header(label, sublabel, cx):
    t = title_f.render(label, True, (245, 235, 210))
    canvas.blit(t, t.get_rect(center=(cx, 22)))
    s = sub_f.render(sublabel, True, (170, 160, 185))
    canvas.blit(s, s.get_rect(center=(cx, 44)))

lx = MARGIN
rx = MARGIN + W + GAP
canvas.blit(before, (lx, HEADER))
canvas.blit(after, (rx, HEADER))
pygame.draw.rect(canvas, (90, 80, 110), (lx, HEADER, W, H), 1)
pygame.draw.rect(canvas, (90, 80, 110), (rx, HEADER, W, H), 1)
header("BEFORE", "shadows on cards + plaque + button", lx + W // 2)
header("AFTER", "flat — shadows removed", rx + W // 2)

out = os.path.join(OUT_DIR, "stats_shade_before_after.png")
pygame.image.save(canvas, out)
print("saved", out)
pygame.quit()
