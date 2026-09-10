"""Dome size fine-grain comparison: dome radius 62 through 68, step 1.

box_px scaled proportionally (dome * 1.5), inset and rim interpolated.
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

SID = "skin_mummy"
CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
PANEL_W, PANEL_H = CARD_W * sc.SS, CARD_H * sc.SS   # 324×200

# dome 62–68 with proportional box, interpolated inset + rim
STEPS = [
    # (dome_r, inset, rim_w_logical)
    (62, 5, 2.3),
    (63, 5, 2.4),
    (64, 4, 2.45),
    (65, 4, 2.5),
    (66, 4, 2.52),
    (67, 4, 2.55),
    (68, 4, 2.6),
]

_ORIG_INSET  = sc._INSET
_ORIG_DOME_R = sc._DOME_R
_ORIG_BOX_PX = sc._BOX_PX
_orig_bevel  = sc.bevel_rim


def make_card_bevel(rim_w_logical):
    def _bevel(surf, rect, radius, deep, bright, w):
        if rect.w > 200:
            w = max(1, sc.m(rim_w_logical))
        _orig_bevel(surf, rect, radius, deep, bright, w)
    return _bevel


def render_panel(dome_r, inset, rim_w):
    sc._INSET    = inset
    sc._DOME_R   = dome_r
    sc._BOX_PX   = round(dome_r * 1.5)
    sc.bevel_rim = make_card_bevel(rim_w)
    sc._card_cache.clear()

    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    ri = sc.m(inset)
    rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
    sc.draw_card(big, SID, rect, equipped=False, secret=False)

    sc._INSET    = _ORIG_INSET
    sc._DOME_R   = _ORIG_DOME_R
    sc._BOX_PX   = _ORIG_BOX_PX
    sc.bevel_rim = _orig_bevel
    sc._card_cache.clear()
    return big


panels = [(dr, render_panel(dr, ins, rw)) for dr, ins, rw in STEPS]

# ── layout ────────────────────────────────────────────────────────────────────
BG     = (8, 8, 20)
PAD    = 20
GAP    = 10
HDR_H  = 48
LBL_H  = 34
ROW_GAP = 20
DISP_W, DISP_H = CARD_W * 2, CARD_H * 2

N = len(panels)
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + ROW_GAP + LBL_H + DISP_H + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh = hud_font(17, True)
fl = hud_font(12, True)
fs = hud_font(10, False)

title = fh.render("dome radius 62 → 68  ·  skin_mummy  ·  same design", True, (240, 224, 180))
sheet.blit(title, ((sheet_w - title.get_width()) // 2, PAD + (HDR_H - title.get_height()) // 2))

y_ss = PAD + HDR_H + LBL_H
for i, (dome_r, surf) in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    lbl = fl.render(f"dome {dome_r}", True, (255, 226, 120))
    sheet.blit(lbl, (x + (PANEL_W - lbl.get_width()) // 2,
                     PAD + HDR_H + (LBL_H - lbl.get_height()) // 2))
    sheet.blit(surf, (x, y_ss))

y_1x_lbl = y_ss + PANEL_H + ROW_GAP
y_1x     = y_1x_lbl + LBL_H
sub = fs.render("1× final pixels at 2× display zoom — judge here", True, (160, 160, 190))
sheet.blit(sub, ((sheet_w - sub.get_width()) // 2,
                  y_1x_lbl + (LBL_H - sub.get_height()) // 2))

for i, (_, surf) in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    one_x = pygame.transform.smoothscale(surf, (CARD_W, CARD_H))
    disp  = pygame.transform.scale(one_x, (DISP_W, DISP_H))
    sheet.blit(disp, (x + (PANEL_W - DISP_W) // 2, y_1x))

out = "docs/store_card_size/dome_range_62_68.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}×{sheet_h} → {out}")
