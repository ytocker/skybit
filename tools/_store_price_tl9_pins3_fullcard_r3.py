"""Full-card comparison: 5 pins3 r3 final concepts at 2×"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
from game.hud import _font as hud_font

SLUGS = ["staple", "toothpick", "straight_pin", "bobby_pin", "push_pin"]
LABELS = [
    "1 · staple",
    "2 · toothpick",
    "3 · straight pin",
    "4 · bobby pin",
    "5 · push pin (thumbtack)",
]

ZOOM   = 2
CW, CH = 162 * ZOOM, 100 * ZOOM   # 324 × 200
LABEL_W = 220
PAD, GAP, HEADER_H = 20, 10, 40

N = len(SLUGS)
sheet_w = PAD + LABEL_W + GAP + CW + PAD
sheet_h = PAD + HEADER_H + N * (CH + GAP) - GAP + PAD
BG = (8, 8, 20)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh = hud_font(18)
fl = hud_font(14)

title = fh.render("tl9 pins3 — round 3 final (affordable, mummy, 2×)", True, (240, 224, 180))
sheet.blit(title, (PAD, PAD // 2))

img_x = PAD + LABEL_W + GAP
y = PAD + HEADER_H

for i, slug in enumerate(SLUGS):
    r3_path = f"docs/store_price_tl9_pins3/{slug}/round_3.png"
    r3_sheet = pygame.image.load(r3_path).convert_alpha()
    # mummy-aff card at (PAD=20, PAD+HEADER_H=60) in sheet, size 162×100
    crop = r3_sheet.subsurface(pygame.Rect(20, 60, 162, 100))
    panel = pygame.transform.smoothscale(crop, (CW, CH))

    lbl = fl.render(LABELS[i], True, (200, 210, 228))
    sheet.blit(lbl, (PAD, y + CH // 2 - lbl.get_height() // 2))
    sheet.blit(panel, (img_x, y))
    y += CH + GAP

out = "docs/store_price_tl9_pins3/full_card_comparison_r3.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
