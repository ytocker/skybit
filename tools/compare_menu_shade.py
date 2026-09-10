"""Before/after for the menu-button drop-shadow removal.

Renders the menu twice from one identical state — once with the cast shadow
forced back on (before), once as it ships now (after) — so the only pixel
difference is the pill shade. Saves a labelled side-by-side to
docs/ui_audit/. Run from repo root.
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
from game.scenes import App, STATE_MENU
from game.world import World
import game.hud as hud

OUT_DIR = os.path.join(_ROOT, "docs", "ui_audit")
os.makedirs(OUT_DIR, exist_ok=True)

T0 = 1.1  # fixed title pulse so both frames share identical animation phase

app = App()
app.world = World()
for _ in range(40):
    app.world.world_idle_tick(1 / 60)
app.session_best = 47
app.state = STATE_MENU


def render_menu():
    app.hud.title_t = T0
    app._render()
    return app.screen.copy()


after = render_menu()

# Force the shadow back on for the "before" frame. draw_menu calls the
# module-global _pill_btn by name, so wrapping it here intercepts the
# menu's explicit shadow=False.
_orig = hud._pill_btn
def _shadowed(*a, **k):
    k["shadow"] = True
    return _orig(*a, **k)
hud._pill_btn = _shadowed
before = render_menu()
hud._pill_btn = _orig

# ── Compose labelled side-by-side ────────────────────────────────────────────
MARGIN = 24
GAP = 28
HEADER = 56
cw = MARGIN * 2 + W * 2 + GAP
chh = HEADER + H + MARGIN
canvas = pygame.Surface((cw, chh))
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
header("BEFORE", "drop shadow under each pill", lx + W // 2)
header("AFTER", "flat — shadow removed", rx + W // 2)

out = os.path.join(OUT_DIR, "menu_shade_before_after.png")
pygame.image.save(canvas, out)
print("saved", out)
pygame.quit()
