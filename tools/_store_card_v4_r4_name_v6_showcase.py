"""Stitch docs/store_card_v4_r4_name_v6/showcase.png — 7-panel comparison figure.

Panel layout (left→right):
  #1 ORIGINAL            docs/store_card_v4/original.png
  #2 BASIS (v4 best)     docs/store_card_v4_r4_name_v4/filament-core/round_2.png
  #3 corona-bloom        docs/store_card_v4_r4_name_v6/corona-bloom/round_2.png
  #4 temper-gradient     docs/store_card_v4_r4_name_v6/temper-gradient/round_2.png
  #5 rim-forge           docs/store_card_v4_r4_name_v6/rim-forge/round_2.png
  #6 niche-void          docs/store_card_v4_r4_name_v6/niche-void/round_2.png
  #7 filament-spark      docs/store_card_v4_r4_name_v6/filament-spark/round_2.png

Source crop — EPIC panel (middle of each 3-panel strip):
  SS=2 strips (1008x268): EPIC_X=342, EPIC_Y=36, W=324, H=200
  original (1008x244):    EPIC_X=342, EPIC_Y=10, W=324, H=200
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from game.hud import _font as hud_font

BASE = os.path.join(os.path.dirname(__file__), "..")

# (id, label, rel_path, crop_x, crop_y, crop_w, crop_h, scale_up)
PANELS = [
    ("#1", "ORIGINAL",           "docs/store_card_v4/original.png",                                      342, 10,  324, 200, False),
    ("#2", "BASIS (v4 best)",    "docs/store_card_v4_r4_name_v4/filament-core/round_2.png",              342, 36,  324, 200, False),
    ("#3", "corona-bloom",       "docs/store_card_v4_r4_name_v6/corona-bloom/round_2.png",               342, 36,  324, 200, False),
    ("#4", "temper-gradient",    "docs/store_card_v4_r4_name_v6/temper-gradient/round_2.png",            342, 36,  324, 200, False),
    ("#5", "rim-forge",          "docs/store_card_v4_r4_name_v6/rim-forge/round_2.png",                  342, 36,  324, 200, False),
    ("#6", "niche-void",         "docs/store_card_v4_r4_name_v6/niche-void/round_2.png",                 342, 36,  324, 200, False),
    ("#7", "filament-spark",     "docs/store_card_v4_r4_name_v6/filament-spark/round_2.png",             342, 36,  324, 200, False),
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
hdr_txt = hdr_f.render("Store Card v4  —  Name Treatment v6  (filament-core evolved)", True,
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
        lbl_surf = hud_font(11, False).render(label, True, (178, 174, 198))
    lbl_x = x + (PANEL_W - lbl_surf.get_width()) // 2
    lbl_y = id_y + ID_H + 2
    canvas.blit(lbl_surf, (lbl_x, lbl_y))

out_path = os.path.join(BASE, "docs", "store_card_v4_r4_name_v6", "showcase.png")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
pygame.image.save(canvas, out_path)
print(f"Saved: {out_path}  ({canvas_w}x{canvas_h})")
