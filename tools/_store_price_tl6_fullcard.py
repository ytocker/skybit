"""Fullcard comparison: BEFORE (tl2 r2) vs 5 tl6 numeral concept round-2 renders.

Crops the affordable mummy card from each existing round_2.png sheet (no
re-exec of concept scripts) and arranges them in a single numbered column
at 2× zoom so the hang-tag numeral treatment reads clearly at review size.
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

# Each round_2 sheet uses PAD=20, HEADER_H=40 → mummy-aff card starts at (20,60).
PAD_SHEET = 20
HEADER_SHEET = 40
CROP_X0, CROP_Y0 = PAD_SHEET, PAD_SHEET + HEADER_SHEET   # 20, 60
CROP_X1, CROP_Y1 = CROP_X0 + sc.CARD_W, CROP_Y0 + sc.CARD_H  # 182, 160

ZOOM = 2
CW = sc.CARD_W * ZOOM   # 324
CH = sc.CARD_H * ZOOM   # 200

CONCEPTS = [
    ("BEFORE",             "docs/store_price_tl2/hang-tag/round_2.png"),
    ("1  kiss-impression", "docs/store_price_tl6/kiss_impression/round_2.png"),
    ("2  rubber-stamp",    "docs/store_price_tl6/rubber_stamp/round_2.png"),
    ("3  spot-accent",     "docs/store_price_tl6/spot_accent/round_2.png"),
    ("4  didone-contrast", "docs/store_price_tl6/didone_contrast/round_2.png"),
    ("5  tinted-deboss",   "docs/store_price_tl6/tinted_deboss/round_2.png"),
]

BG = (8, 8, 20)
PAD = 20
GAP = 10
HEADER_H = 40
LABEL_W = 170

sheet_w = PAD + LABEL_W + GAP + CW + PAD
row_h = CH + GAP
sheet_h = PAD + HEADER_H + len(CONCEPTS) * row_h - GAP + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh = hud_font(20)
fl = hud_font(13)
title = fh.render("tl6 numeral — round 2 comparison (affordable, mummy)", True, (240, 224, 180))
sheet.blit(title, (PAD, PAD // 2))

y = PAD + HEADER_H
for label, src_path in CONCEPTS:
    src = pygame.image.load(src_path).convert()
    card = src.subsurface(pygame.Rect(CROP_X0, CROP_Y0, sc.CARD_W, sc.CARD_H))
    zoomed = pygame.transform.smoothscale(card, (CW, CH))
    sheet.blit(zoomed, (PAD + LABEL_W + GAP, y))

    col = (240, 220, 160) if label == "BEFORE" else (190, 196, 210)
    lbl = fl.render(label, True, col)
    sheet.blit(lbl, (PAD, y + CH // 2 - lbl.get_height() // 2))

    # separator between rows (skip after last)
    if label != CONCEPTS[-1][0]:
        sep_y = y + CH + GAP // 2
        pygame.draw.line(sheet, (30, 32, 48), (PAD, sep_y), (sheet_w - PAD, sep_y))

    y += row_h

out = "docs/store_price_tl6/full_card_comparison.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
