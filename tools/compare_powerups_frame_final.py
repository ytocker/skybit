"""Before/after for the final 'raised metal' power-up card frame.

Before = the naked rim-only frame (previous ship). After = the integrated
raised-metal V5 frame (two-tone rim + inner bevel + faint lit body). Saves
a labelled full-screen side-by-side + a 3x zoom crop. Run from repo root.
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
import game.powerup_help as ph
from game.powerup_help import PowerUpHelpScene
from game.hud import _GOLD_BRIGHT, _PANEL_DARK


def _naked_panel(surf, rect, radius, alpha):
    """Verbatim previous frame — flat navy body + single 2px gold rim."""
    os_ = ph._PANEL_OS
    ow, oh = rect.width * os_, rect.height * os_
    orad = radius * os_
    pnl = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*_PANEL_DARK, alpha), (0, 0, ow, oh), border_radius=orad)
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 130), (0, 0, ow, oh),
                     width=2 * os_, border_radius=orad)
    surf.blit(pygame.transform.smoothscale(pnl, rect.size), rect.topleft)


def render_screen():
    scene = PowerUpHelpScene()
    scene.update(0.5)
    s = pygame.Surface((W, H))
    scene.render(s)
    return s


after = render_screen()
ph._dark_panel = _naked_panel
before = render_screen()

OUT_DIR = os.path.join(_ROOT, "docs", "ui_audit")
MARGIN, GAP, HEADER = 24, 28, 56
title_f = pygame.font.Font(None, 38)
sub_f = pygame.font.Font(None, 24)

canvas = pygame.Surface((MARGIN * 2 + W * 2 + GAP, HEADER + H + MARGIN))
canvas.fill((18, 16, 30))
def header(label, sublabel, cx):
    t = title_f.render(label, True, (245, 235, 210))
    canvas.blit(t, t.get_rect(center=(cx, 22)))
    s = sub_f.render(sublabel, True, (170, 160, 185))
    canvas.blit(s, s.get_rect(center=(cx, 44)))
lx, rx = MARGIN, MARGIN + W + GAP
canvas.blit(before, (lx, HEADER))
canvas.blit(after, (rx, HEADER))
header("BEFORE", "naked rim only", lx + W // 2)
header("AFTER", "raised metal — rim + bevel + lit body", rx + W // 2)
out = os.path.join(OUT_DIR, "powerups_frame_final_before_after.png")
pygame.image.save(canvas, out)
print("saved", out)

base_x = (W - (162 * 2 + 8)) // 2
crop = pygame.Rect(base_x - 4, 110 - 4, 162 + 8, 124 + 8)
ZOOM = 3
zc = pygame.Surface((MARGIN * 2 + crop.w * ZOOM * 2 + GAP,
                     HEADER + crop.h * ZOOM + MARGIN))
zc.fill((18, 16, 30))
b_crop = pygame.transform.scale(before.subsurface(crop), (crop.w * ZOOM, crop.h * ZOOM))
a_crop = pygame.transform.scale(after.subsurface(crop), (crop.w * ZOOM, crop.h * ZOOM))
zc.blit(b_crop, (MARGIN, HEADER))
zc.blit(a_crop, (MARGIN + crop.w * ZOOM + GAP, HEADER))
def zh(label, cx):
    t = title_f.render(label, True, (245, 235, 210))
    zc.blit(t, t.get_rect(center=(cx, 28)))
zh("BEFORE  (3x)", MARGIN + crop.w * ZOOM // 2)
zh("AFTER  (3x)", MARGIN + crop.w * ZOOM + GAP + crop.w * ZOOM // 2)
out2 = os.path.join(OUT_DIR, "powerups_frame_final_zoom.png")
pygame.image.save(zc, out2)
print("saved", out2)
pygame.quit()
