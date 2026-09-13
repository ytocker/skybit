"""Price digit + rule size comparison — 5 options.

Tag face stays at _TAG_W=76, _TAG_H=88. Each option raises the max glyph
width (making digits larger) and scales the wedge rule beneath them.

Skin: skin_mummy (price 2800 — 4 digits, stress-tests the width cap).
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

# ── steps: (label, max_glyph_w, rule_peak_h, rule_min_h) ────────────────────
STEPS = [
    ("CURRENT",     66, 6, 2),
    ("DIGIT +1",    70, 7, 2),
    ("DIGIT +2",    74, 8, 3),
    ("DIGIT +3",    78, 9, 3),
    ("DIGIT +4",    82, 10, 4),
]

_orig_glyph      = sc._tag_price_glyph
_orig_draw_price = sc._tag_draw_price


def make_glyph(max_w):
    def _fn(text):
        for fs in (15, 14, 13, 12, 11, 10, 9, 8):
            raw = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
            crushed = pygame.transform.smoothscale(
                raw, (max(1, int(raw.get_width() * 0.86)), raw.get_height()))
            if crushed.get_width() <= max_w:
                return crushed
        return crushed
    return _fn


def make_draw_price(peak_h, min_h):
    def _fn(face, text, affordable):
        cx  = sc._TAG_W // 2
        ink           = (40, 30, 26) if affordable else (40, 40, 52)
        rule_col      = (56, 42, 30) if affordable else (40, 40, 52)
        amt_mask = sc._tag_price_glyph(text)
        cy_amount = int(sc._TAG_H * 0.52)
        amt_r = amt_mask.get_rect(center=(cx, cy_amount))
        amt_fill = amt_mask.copy()
        amt_fill.fill((*ink, 255), special_flags=pygame.BLEND_RGBA_MULT)
        face.blit(amt_fill, amt_r)
        amt_h = amt_mask.get_height()
        rule_y = cy_amount + amt_h // 2 + sc.m(2)
        rule_w = min(amt_mask.get_width() + sc.m(4), sc._TAG_W - sc.m(8))
        rule_x = sc._TAG_W // 2 - rule_w // 2
        pts = [
            (rule_x,          rule_y),
            (rule_x + rule_w, rule_y + (peak_h - min_h) // 2),
            (rule_x + rule_w, rule_y + (peak_h + min_h) // 2),
            (rule_x,          rule_y + peak_h),
        ]
        pygame.draw.polygon(face, rule_col, pts)
    return _fn


def render_panel(max_w, peak_h, min_h):
    sc._tag_price_glyph = make_glyph(max_w)
    sc._tag_draw_price  = make_draw_price(peak_h, min_h)
    sc._card_cache.clear()
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    ri = sc.m(sc._INSET)
    rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
    sc.draw_card(big, SID, rect, equipped=False, secret=False)
    sc._tag_price_glyph = _orig_glyph
    sc._tag_draw_price  = _orig_draw_price
    sc._card_cache.clear()
    return big


panels = [(lbl, render_panel(mw, ph, mnh)) for lbl, mw, ph, mnh in STEPS]

# ── layout ────────────────────────────────────────────────────────────────────
BG     = (8, 8, 20)
PAD    = 20
GAP    = 10
HDR_H  = 48
LBL_H  = 34
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
    "price digit + rule size — tag 76×88 fixed · skin_mummy",
    True, (240, 224, 180))
sheet.blit(title, ((sheet_w - title.get_width()) // 2,
                   PAD + (HDR_H - title.get_height()) // 2))

y_ss = PAD + HDR_H + LBL_H
for i, (lbl, surf) in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    col = (170, 166, 190) if i == 0 else (255, 226, 120)
    t = fl.render(lbl, True, col)
    sheet.blit(t, (x + (PANEL_W - t.get_width()) // 2,
                   PAD + HDR_H + (LBL_H - t.get_height()) // 2))
    sheet.blit(surf, (x, y_ss))

y_1x_lbl = y_ss + PANEL_H + ROW_GAP
y_1x = y_1x_lbl + LBL_H
sub = fs.render("1× final pixels at 2× display zoom — judge here", True, (160, 160, 190))
sheet.blit(sub, ((sheet_w - sub.get_width()) // 2,
                  y_1x_lbl + (LBL_H - sub.get_height()) // 2))

for i, (_, surf) in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    one_x = pygame.transform.smoothscale(surf, (CARD_W, CARD_H))
    disp  = pygame.transform.scale(one_x, (DISP_W, DISP_H))
    sheet.blit(disp, (x + (PANEL_W - DISP_W) // 2, y_1x))

out = "docs/store_card_size/price_digit_size.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}×{sheet_h} → {out}")
