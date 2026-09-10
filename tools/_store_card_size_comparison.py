"""Store card size comparison — same design, 5 size steps.

Baseline vs progressively larger character + golden rim, keeping the
visual language identical. Six panels in a row:

  baseline  |  S+1  |  S+2  |  S+3  |  S+4  |  S+5

Size knobs per step:
  _INSET   : 6 → 5 → 4 → 3 → 2 → 1   (shrinks card body margin)
  _DOME_R  : 56 → 62 → 68 → 74 → 80 → 86  (bigger dome)
  _BOX_PX  : 84 → 93 → 102 → 111 → 120 → 129  (bigger hero)
  rim w    : m(2.0) → m(2.3) → m(2.6) → m(3.0) → m(3.3) → m(3.6)
             (thicker gold perimeter rim on the card body — chip rects untouched)
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
SS = sc.SS
CARD_W, CARD_H = sc.CARD_W, sc.CARD_H    # 162, 100
PANEL_W = CARD_W * SS                     # 324
PANEL_H = CARD_H * SS                     # 200

# ── size steps ────────────────────────────────────────────────────────────────
STEPS = [
    # (label,   inset, dome_r, box_px, rim_w_logical)
    ("BASELINE\ninset 6 · dome 56", 6, 56,  84, 2.0),
    ("SIZE +1\ninset 5 · dome 62",  5, 62,  93, 2.3),
    ("SIZE +2\ninset 4 · dome 68",  4, 68, 102, 2.6),
    ("SIZE +3\ninset 3 · dome 74",  3, 74, 111, 3.0),
    ("SIZE +4\ninset 2 · dome 80",  2, 80, 120, 3.3),
    ("SIZE +5\ninset 1 · dome 86",  1, 86, 129, 3.6),
]

_ORIG_INSET   = sc._INSET
_ORIG_DOME_R  = sc._DOME_R
_ORIG_BOX_PX  = sc._BOX_PX
_orig_bevel   = sc.bevel_rim


def make_card_bevel(rim_w_logical):
    """Wrap bevel_rim to use a larger w for the card body rect (w > 200 SS),
    leaving chip and badge calls (smaller rects) at their original width."""
    def _bevel(surf, rect, radius, deep, bright, w):
        if rect.w > 200:
            w = max(1, sc.m(rim_w_logical))
        _orig_bevel(surf, rect, radius, deep, bright, w)
    return _bevel


def render_panel(inset, dome_r, box_px, rim_w_logical):
    sc._INSET   = inset
    sc._DOME_R  = dome_r
    sc._BOX_PX  = box_px
    sc.bevel_rim = make_card_bevel(rim_w_logical)
    sc._card_cache.clear()

    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    r_inset = sc.m(inset)
    rect = pygame.Rect(r_inset, r_inset, PANEL_W - 2 * r_inset, PANEL_H - 2 * r_inset)
    sc.draw_card(big, SID, rect, equipped=False, secret=False)

    # restore immediately
    sc._INSET    = _ORIG_INSET
    sc._DOME_R   = _ORIG_DOME_R
    sc._BOX_PX   = _ORIG_BOX_PX
    sc.bevel_rim = _orig_bevel
    sc._card_cache.clear()
    return big


panels = [(lbl, render_panel(ins, dr, bp, rw))
          for lbl, ins, dr, bp, rw in STEPS]

# ── layout ────────────────────────────────────────────────────────────────────
BG      = (8, 8, 20)
PAD     = 20
GAP     = 10
HDR_H   = 52
LBL_H   = 38       # two-line label area above cards
ROW_GAP = 20
FOOTER  = 20

N = len(panels)
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD

# Row 1: 2× (PANEL_W×PANEL_H), Row 2: 1× (CARD_W×CARD_H) displayed at 2× zoom
DISP_W, DISP_H = CARD_W * 2, CARD_H * 2

sheet_h = (PAD + HDR_H
           + LBL_H + PANEL_H         # row 1: SS panels
           + ROW_GAP
           + LBL_H + DISP_H          # row 2: 1× final pixels at 2× display zoom
           + FOOTER)

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh   = hud_font(18, True)
fl   = hud_font(12, True)
fs   = hud_font(10, False)

title = fh.render("store card · same design · 6 size options  ·  skin_mummy", True, (240, 224, 180))
sheet.blit(title, ((sheet_w - title.get_width()) // 2, PAD + (HDR_H - title.get_height()) // 2))

# ── row 1: full SS panels ─────────────────────────────────────────────────────
y_ss = PAD + HDR_H + LBL_H

for i, (lbl, surf) in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    col = (170, 166, 190) if i == 0 else (255, 226, 120)

    # two-line label centered above panel
    lines = lbl.split("\n")
    line_h = fl.get_height()
    total_lbl_h = line_h * len(lines)
    for li, line in enumerate(lines):
        t = fl.render(line, True, col)
        ly = PAD + HDR_H + (LBL_H - total_lbl_h) // 2 + li * line_h
        sheet.blit(t, (x + (PANEL_W - t.get_width()) // 2, ly))

    sheet.blit(surf, (x, y_ss))

# ── row 2: 1× pixels shown at 2× display zoom ─────────────────────────────────
y_row2_lbl = y_ss + PANEL_H + ROW_GAP
y_row2     = y_row2_lbl + LBL_H

sub_lbl = fs.render("1× final size (162×100), displayed at 2× — judge pixel quality here",
                    True, (160, 160, 190))
sheet.blit(sub_lbl, ((sheet_w - sub_lbl.get_width()) // 2,
                      y_row2_lbl + (LBL_H - sub_lbl.get_height()) // 2))

for i, (_, surf) in enumerate(panels):
    one_x = pygame.transform.smoothscale(surf, (CARD_W, CARD_H))
    disp  = pygame.transform.scale(one_x, (DISP_W, DISP_H))
    x = PAD + i * (PANEL_W + GAP)
    ox = (PANEL_W - DISP_W) // 2
    sheet.blit(disp, (x + ox, y_row2))

# ── save ─────────────────────────────────────────────────────────────────────
out = "docs/store_card_size/size_comparison.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}×{sheet_h} → {out}")
