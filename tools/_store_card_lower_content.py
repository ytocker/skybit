"""Lower content position comparison — dome=66 locked, 5 vertical shift options.

Shifts dome center, rarity ribbon, and name label down together by a uniform
delta (SS px), keeping the price chip fixed at the card bottom.

Locked: _INSET=4, _DOME_R=66, _BOX_PX=99, rim w=m(2.52).
Shifts (in SS px → logical px): 0, 6, 10, 14, 18.
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
PANEL_W, PANEL_H = CARD_W * sc.SS, CARD_H * sc.SS

# ── locked size values ────────────────────────────────────────────────────────
LOCKED_INSET  = 4
LOCKED_DOME_R = 64
LOCKED_BOX_PX = 96   # round(64 * 1.5)
LOCKED_RIM_W  = 2.45

# ── shift steps (SS pixels, all even so m() is exact) ────────────────────────
STEPS = [
    ("BASELINE\nno shift",  0),
    ("LOWER +1\n+3 lx",     6),
    ("LOWER +2\n+5 lx",    10),
    ("LOWER +3\n+7 lx",    14),
    ("LOWER +4\n+9 lx",    18),
]

# ── originals ─────────────────────────────────────────────────────────────────
_ORIG_INSET   = sc._INSET
_ORIG_DOME_R  = sc._DOME_R
_ORIG_BOX_PX  = sc._BOX_PX
_ORIG_CY_DISC = sc.CY_DISC
_orig_bevel   = sc.bevel_rim
_orig_ribbon  = sc._ribbon_lozenge
_orig_name    = sc._name_on


def make_card_bevel(rim_w_logical):
    def _bevel(surf, rect, radius, deep, bright, w):
        if rect.w > 200:
            w = max(1, sc.m(rim_w_logical))
        _orig_bevel(surf, rect, radius, deep, bright, w)
    return _bevel


def render_panel(delta_ss):
    # apply locked size
    sc._INSET   = LOCKED_INSET
    sc._DOME_R  = LOCKED_DOME_R
    sc._BOX_PX  = LOCKED_BOX_PX
    sc.bevel_rim = make_card_bevel(LOCKED_RIM_W)

    # shift dome: CY_DISC is in logical px; delta_ss/2 = logical shift
    sc.CY_DISC = _ORIG_CY_DISC + delta_ss // 2

    # shift ribbon and name label by delta_ss in the draw call
    def shifted_ribbon(surf, tier_word, cx, cy, max_w, pal):
        _orig_ribbon(surf, tier_word, cx, cy + delta_ss, max_w, pal)

    def shifted_name(surf, name, cx, cy, max_w):
        _orig_name(surf, name, cx, cy + delta_ss, max_w)

    sc._ribbon_lozenge = shifted_ribbon
    sc._name_on        = shifted_name

    sc._card_cache.clear()
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    ri = sc.m(LOCKED_INSET)
    rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
    sc.draw_card(big, SID, rect, equipped=False, secret=False)

    # restore
    sc._INSET          = _ORIG_INSET
    sc._DOME_R         = _ORIG_DOME_R
    sc._BOX_PX         = _ORIG_BOX_PX
    sc.CY_DISC         = _ORIG_CY_DISC
    sc.bevel_rim       = _orig_bevel
    sc._ribbon_lozenge = _orig_ribbon
    sc._name_on        = _orig_name
    sc._card_cache.clear()
    return big


panels = [(lbl, render_panel(d)) for lbl, d in STEPS]

# ── layout ────────────────────────────────────────────────────────────────────
BG      = (8, 8, 20)
PAD     = 20
GAP     = 10
HDR_H   = 48
LBL_H   = 36
ROW_GAP = 18
DISP_W, DISP_H = CARD_W * 2, CARD_H * 2

N = len(panels)
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + ROW_GAP + LBL_H + DISP_H + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh = hud_font(17, True)
fl = hud_font(12, True)
fs = hud_font(10, False)

title = fh.render(
    "content position — dome 64 locked · item + banner shifted lower",
    True, (240, 224, 180))
sheet.blit(title, ((sheet_w - title.get_width()) // 2, PAD + (HDR_H - title.get_height()) // 2))

y_ss = PAD + HDR_H + LBL_H
for i, (lbl, surf) in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    col = (170, 166, 190) if i == 0 else (255, 226, 120)
    lines = lbl.split("\n")
    lh = fl.get_height()
    for li, line in enumerate(lines):
        t = fl.render(line, True, col)
        ly = PAD + HDR_H + (LBL_H - lh * len(lines)) // 2 + li * lh
        sheet.blit(t, (x + (PANEL_W - t.get_width()) // 2, ly))
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

out = "docs/store_card_size/lower_content.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}×{sheet_h} → {out}")
