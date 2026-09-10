"""Full-card comparison: BEFORE (axis_crush) + 10 pins2 r2 concepts, vertical strip at 2×"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
from game.hud import _font as hud_font

SLUGS = [
    "paper_clip",
    "binder_clip",
    "fish_hook",
    "chain",
    "toggle_clasp",
    "brass_brad",
    "zip_tie",
    "treasury_tag",
    "carabiner",
    "split_ring",
]
LABELS = [
    "BEFORE (axis_crush)",
    "1 · paper clip",
    "2 · binder clip",
    "3 · fish hook",
    "4 · chain",
    "5 · toggle clasp",
    "6 · brass brad",
    "7 · zip tie",
    "8 · treasury tag",
    "9 · carabiner",
    "10 · split ring",
]

ZOOM   = 2
CW, CH = 162 * ZOOM, 100 * ZOOM   # 324 × 200
LABEL_W = 220
PAD, GAP, HEADER_H = 20, 10, 40

N = 11  # BEFORE + 10 concepts
sheet_w = PAD + LABEL_W + GAP + CW + PAD
sheet_h = PAD + HEADER_H + N * (CH + GAP) - GAP + PAD
BG = (8, 8, 20)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh = hud_font(18)
fl = hud_font(14)
fs = hud_font(12)

title = fh.render("tl9 pins2 — round 2 comparison (affordable, mummy, 2×)", True, (240, 224, 180))
sheet.blit(title, (PAD, PAD // 2))

img_x = PAD + LABEL_W + GAP

# --- BEFORE: crop axis_crush mummy-aff panel from nocoin_compare at (522, 60, 486, 300) ---
before_src = pygame.image.load("docs/store_price_tl9/nocoin_compare.png").convert_alpha()
before_crop = before_src.subsurface(pygame.Rect(522, 60, 486, 300))
before_panel = pygame.transform.smoothscale(before_crop, (CW, CH))

y = PAD + HEADER_H
lbl = fl.render(LABELS[0], True, (240, 224, 180))
sheet.blit(lbl, (PAD, y + CH // 2 - lbl.get_height() // 2))
sheet.blit(before_panel, (img_x, y))
y += CH + GAP

# --- 10 r2 concept panels ---
for i, slug in enumerate(SLUGS):
    r2_path = f"docs/store_price_tl9_pins2/{slug}/round_2.png"
    r2_sheet = pygame.image.load(r2_path).convert_alpha()
    # mummy-aff card starts at (PAD=20, PAD+HEADER_H=60) in the sheet, size 162×100
    crop = r2_sheet.subsurface(pygame.Rect(20, 60, 162, 100))
    panel = pygame.transform.smoothscale(crop, (CW, CH))

    lbl = fl.render(LABELS[i + 1], True, (200, 210, 228))
    sheet.blit(lbl, (PAD, y + CH // 2 - lbl.get_height() // 2))
    sheet.blit(panel, (img_x, y))
    y += CH + GAP

out = "docs/store_price_tl9_pins2/full_card_comparison.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
