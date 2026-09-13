"""Render the current live store card as docs/store_card_v4/original.png.

Shows 3 tiers side-by-side: RARE (skin_tophat), EPIC (skin_prism), LEGENDARY (skin_kitsune).
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from game.store_cards import draw_card, SS, m, font, plain_text, CARD_T, CARD_B
from game.config import W, H

SKINS = [
    ("skin_tophat", "RARE"),
    ("skin_prism",  "EPIC"),
    ("skin_kitsune","LEGENDARY"),
]

CARD_W, CARD_H = 162, 100
BIG_W, BIG_H = CARD_W * SS, CARD_H * SS
GAP = 8
MARGIN = 10
LABEL_H = 24
BG = (8, 8, 20)

n = len(SKINS)
canvas_w = MARGIN * 2 + BIG_W * n + GAP * (n - 1)
canvas_h = MARGIN + BIG_H + LABEL_H + MARGIN

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

for i, (sid, tier_label) in enumerate(SKINS):
    x = MARGIN + i * (BIG_W + GAP)
    y = MARGIN

    big = pygame.Surface((BIG_W, BIG_H), pygame.SRCALPHA)
    rect = pygame.Rect(m(6), m(6), BIG_W - m(12), BIG_H - m(12))
    draw_card(big, sid, rect, equipped=False, secret=False, variant=1)
    canvas.blit(big, (x, y))

    lbl_font = font(7.5)
    lbl = lbl_font.render(tier_label, True, (180, 180, 200))
    canvas.blit(lbl, (x + (BIG_W - lbl.get_width()) // 2, y + BIG_H + 4))

out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "store_card_v4")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "original.png")
pygame.image.save(canvas, out_path)
print(f"Saved: {out_path}  ({canvas_w}x{canvas_h})")
