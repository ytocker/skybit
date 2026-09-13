"""Fullcard comparison: BEFORE (axis_crush no-coin) vs 5 tl9 pin attachment r2 renders.

Crops the affordable mummy card from each round_2.png sheet and arranges them
in a single numbered column at 3× zoom so the pin treatment reads clearly at
review size.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.hud import _font as hud_font

# nocoin_compare layout: ZOOM=3, PAD=20, HEADER_H=40, CW=CARD_W*3=486, GAP=16.
# axis_crush panel (second) starts at x=20+486+16=522, y=60, w=486, h=300.
NOCOIN_AX_RECT = (522, 60, 486, 300)

PAD_SHEET = 20
HEADER_SHEET = 40
CROP_X0, CROP_Y0 = PAD_SHEET, PAD_SHEET + HEADER_SHEET
CROP_W, CROP_H = sc.CARD_W, sc.CARD_H

ZOOM = 3
CW = CROP_W * ZOOM
CH = CROP_H * ZOOM

CONCEPTS = [
    ("BEFORE",           "docs/store_price_tl9/nocoin_compare.png",                  True),
    ("1  safety_pin",    "docs/store_price_tl9_pins/safety_pin/round_2.png",         False),
    ("2  ribbon_bow",    "docs/store_price_tl9_pins/ribbon_bow/round_2.png",         False),
    ("3  eyelet_lace",   "docs/store_price_tl9_pins/eyelet_lace/round_2.png",        False),
    ("4  clothespin_peg","docs/store_price_tl9_pins/clothespin_peg/round_2.png",     False),
    ("5  wax_seal",      "docs/store_price_tl9_pins/wax_seal/round_2.png",           False),
]

BG = (8, 8, 20)
PAD = 20
GAP = 10
HEADER_H = 40
LABEL_W = 220

sheet_w = PAD + LABEL_W + GAP + CW + PAD
row_h = CH + GAP
sheet_h = PAD + HEADER_H + len(CONCEPTS) * row_h - GAP + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh = hud_font(20)
fl = hud_font(13)
title = fh.render("tl9 pins — round 2 comparison (affordable, mummy, 3×)", True, (240, 224, 180))
sheet.blit(title, (PAD, PAD // 2))

y = PAD + HEADER_H
for i, (label, src_path, is_before) in enumerate(CONCEPTS):
    src = pygame.image.load(src_path).convert()
    if is_before:
        card = src.subsurface(pygame.Rect(*NOCOIN_AX_RECT))
    else:
        raw = src.subsurface(pygame.Rect(CROP_X0, CROP_Y0, CROP_W, CROP_H))
        card = pygame.transform.smoothscale(raw, (CW, CH))
    sheet.blit(card, (PAD + LABEL_W + GAP, y))

    col = (240, 220, 160) if is_before else (190, 196, 210)
    lbl = fl.render(label, True, col)
    sheet.blit(lbl, (PAD, y + CH // 2 - lbl.get_height() // 2))

    if i < len(CONCEPTS) - 1:
        sep_y = y + CH + GAP // 2
        pygame.draw.line(sheet, (30, 32, 48), (PAD, sep_y), (sheet_w - PAD, sep_y))

    y += row_h

out = "docs/store_price_tl9_pins/full_card_comparison.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
