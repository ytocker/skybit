"""Stitch docs/store_card_v4_r4_price/showcase.png — 7-panel price-tag comparison.

Panel layout (left→right):
  #1 ORIGINAL       docs/store_card_v4/original.png
  #2 BASIS          docs/store_card_v4_r4_name_v4/filament-core/round_2.png
  #3 coin-pill      docs/store_card_v4_r4_price/coin-pill/round_2.png
  #4 scroll-ribbon  docs/store_card_v4_r4_price/scroll-ribbon/round_2.png
  #5 denom-stamp    docs/store_card_v4_r4_price/denom-stamp/round_2.png
  #6 gem-bubble     docs/store_card_v4_r4_price/gem-bubble/round_2.png
  #7 bare-numeral   docs/store_card_v4_r4_price/bare-numeral/round_2.png

Source crops — EPIC panel only:
  original (1008×244):    crop_x=342 crop_y=10  W=324 H=200  (no header in source)
  filament-core (1008×268): crop_x=342 crop_y=36  W=324 H=200
  coin-pill / denom-stamp / gem-bubble / bare-numeral (324×200): full card, crop (0,0)
  scroll-ribbon (636×338): full-res card at (16,46), crop W=324 H=200
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from game.store_cards import font as sc_font
from game.hud import _font as hud_font

BASE = os.path.join(os.path.dirname(__file__), "..")

# (id, label, rel_path, crop_x, crop_y, crop_w, crop_h, scale_up)
PANELS = [
    ("#1", "ORIGINAL",       "docs/store_card_v4/original.png",                          342,  10, 324, 200, False),
    ("#2", "BASIS",          "docs/store_card_v4_r4_name_v4/filament-core/round_2.png",  342,  36, 324, 200, False),
    ("#3", "coin-pill",      "docs/store_card_v4_r4_price/coin-pill/round_2.png",          0,   0, 324, 200, False),
    ("#4", "scroll-ribbon",  "docs/store_card_v4_r4_price/scroll-ribbon/round_2.png",     16,  46, 324, 200, False),
    ("#5", "denom-stamp",    "docs/store_card_v4_r4_price/denom-stamp/round_2.png",        0,   0, 324, 200, False),
    ("#6", "gem-bubble",     "docs/store_card_v4_r4_price/gem-bubble/round_2.png",         0,   0, 324, 200, False),
    ("#7", "bare-numeral",   "docs/store_card_v4_r4_price/bare-numeral/round_2.png",       0,   0, 324, 200, False),
]

PANEL_W  = 324
PANEL_H  = 200
BG       = (8, 8, 20)
GAP      = 8
MARGIN   = 20
HEADER_H = 40
ID_H     = 26
LBL_H    = 20
FOOTER_H = ID_H + LBL_H + 4

n        = len(PANELS)
canvas_w = MARGIN * 2 + PANEL_W * n + GAP * (n - 1)
canvas_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hdr_f   = hud_font(18, True)
hdr_txt = hdr_f.render("Store Card v4  —  Price Tag Concepts  (r4 price)", True,
                        (210, 206, 224))
canvas.blit(hdr_txt, ((canvas_w - hdr_txt.get_width()) // 2,
                       MARGIN + (HEADER_H - hdr_txt.get_height()) // 2))

id_font  = hud_font(17, True)
lbl_font = hud_font(13, False)

panel_y = MARGIN + HEADER_H

for col, (num, label, rel_path, crop_x, crop_y, crop_w, crop_h, scale_up) in enumerate(PANELS):
    x = MARGIN + col * (PANEL_W + GAP)

    src   = pygame.image.load(os.path.join(BASE, rel_path))
    crop  = pygame.Rect(crop_x, crop_y, crop_w, crop_h)
    panel = src.subsurface(crop).copy()
    if scale_up:
        panel = pygame.transform.smoothscale(panel, (PANEL_W, PANEL_H))

    pygame.draw.rect(panel, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)
    canvas.blit(panel, (x, panel_y))

    id_surf = id_font.render(num, True, (255, 230, 120))
    id_x    = x + (PANEL_W - id_surf.get_width()) // 2
    id_y    = panel_y + PANEL_H + 4
    canvas.blit(id_surf, (id_x, id_y))

    lbl_surf = lbl_font.render(label, True, (178, 174, 198))
    if lbl_surf.get_width() > PANEL_W - 4:
        tiny = hud_font(11, False)
        lbl_surf = tiny.render(label, True, (178, 174, 198))
    lbl_x = x + (PANEL_W - lbl_surf.get_width()) // 2
    lbl_y = id_y + ID_H + 2
    canvas.blit(lbl_surf, (lbl_x, lbl_y))

out_path = os.path.join(BASE, "docs", "store_card_v4_r4_price", "showcase.png")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
pygame.image.save(canvas, out_path)
print(f"Saved: {out_path}  ({canvas_w}x{canvas_h})")
