"""Before/after for the power-up card frame quality.

Renders the power-ups explainer twice: once with the old native-resolution
card frame (before — pixel-stepped corners + rim) and once with the new
supersampled frame (after). Saves a labelled side-by-side plus a 3x zoom
crop of one card so the corner/rim difference is unmistakable. Run from
repo root.
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

OUT_DIR = os.path.join(_ROOT, "docs", "ui_audit")
os.makedirs(OUT_DIR, exist_ok=True)


def _old_dark_panel(surf, rect, radius, alpha):
    """Verbatim pre-change frame — native-resolution rounded rect + 1 px rim."""
    sh = pygame.Surface((rect.width + 4, rect.height + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90),
                     (0, 0, rect.width + 4, rect.height + 4),
                     border_radius=radius)
    surf.blit(sh, (rect.x - 2, rect.y + 4))
    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*_PANEL_DARK, alpha),
                     (0, 0, rect.width, rect.height), border_radius=radius)
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 130),
                     (0, 0, rect.width, rect.height), width=1, border_radius=radius)
    inset = max(radius - 2, 6)
    rail_w = max(rect.width - inset * 2, 0)
    if rail_w > 0:
        accent = pygame.Surface((rail_w, 2), pygame.SRCALPHA)
        accent.fill((*_GOLD_BRIGHT, 110))
        pnl.blit(accent, (inset, 4))
        pygame.draw.line(pnl, (255, 220, 140, 90),
                         (inset, 2), (rect.width - inset, 2), 1)
    surf.blit(pnl, rect.topleft)


def render_screen():
    scene = PowerUpHelpScene()
    scene.update(0.5)            # fixed star phase, identical for both frames
    s = pygame.Surface((W, H))
    scene.render(s)
    return s


after = render_screen()
ph._dark_panel = _old_dark_panel
before = render_screen()

# ── full side-by-side ────────────────────────────────────────────────────────
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
header("BEFORE", "native frame — stepped corners", lx + W // 2)
header("AFTER", "supersampled frame — crisp", rx + W // 2)
out = os.path.join(OUT_DIR, "powerups_frame_before_after.png")
pygame.image.save(canvas, out)
print("saved", out)

# ── zoom crop of the top-left card so the rim/corner is obvious ──────────────
# Top-left grid card: base_x..; grid_top=110, card 162x124.
base_x = (W - (162 * 2 + 8)) // 2
crop = pygame.Rect(base_x - 4, 110 - 4, 162 + 8, 124 + 8)
ZOOM = 3
zc_w = MARGIN * 2 + crop.w * ZOOM * 2 + GAP
zc = pygame.Surface((zc_w, HEADER + crop.h * ZOOM + MARGIN))
zc.fill((18, 16, 30))
def zheader(label, cx):
    t = title_f.render(label, True, (245, 235, 210))
    zc.blit(t, t.get_rect(center=(cx, 28)))
b_crop = pygame.transform.scale(before.subsurface(crop), (crop.w * ZOOM, crop.h * ZOOM))
a_crop = pygame.transform.scale(after.subsurface(crop), (crop.w * ZOOM, crop.h * ZOOM))
zc.blit(b_crop, (MARGIN, HEADER))
zc.blit(a_crop, (MARGIN + crop.w * ZOOM + GAP, HEADER))
zheader("BEFORE  (3x)", MARGIN + crop.w * ZOOM // 2)
zheader("AFTER  (3x)", MARGIN + crop.w * ZOOM + GAP + crop.w * ZOOM // 2)
out2 = os.path.join(OUT_DIR, "powerups_frame_zoom.png")
pygame.image.save(zc, out2)
print("saved", out2)
pygame.quit()
