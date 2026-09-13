"""Stitch docs/store_card_v4_r3/showcase.png — 7-panel comparison figure.

Panel layout (left→right):
  #1 ORIGINAL       docs/store_card_v4/original.png
  #2 BASIS          docs/store_card_v4/landscape-hero/round_2.png
  #3 tidal-shelf    docs/store_card_v4_r3/tidal-shelf/round_2.png
  #4 neon-marquee   docs/store_card_v4_r3/neon-marquee/round_2.png
  #5 astral-lattice docs/store_card_v4_r3/astral-lattice/round_2.png
  #6 book-spine     docs/store_card_v4_r3/book-spine/round_2.png
  #7 dock-notch     docs/store_card_v4_r3/dock-notch/round_2.png

Source crop — EPIC panel (middle of each 3-panel strip):
  SS=2 strips (1008×268): EPIC_X=342, EPIC_Y=36, W=324, H=200
  original (1008×244):    EPIC_X=342, EPIC_Y=10, W=324, H=200  (no header)
  book-spine (522×168):   EPIC_X=180, EPIC_Y=36, W=162, H=100  → smoothscale→(324,200)
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

PANELS = [
    ("#1", "ORIGINAL",       "docs/store_card_v4/original.png",                  342, 10,  324, 200, False),
    ("#2", "BASIS",          "docs/store_card_v4/landscape-hero/round_2.png",     342, 36,  324, 200, False),
    ("#3", "tidal-shelf",    "docs/store_card_v4_r3/tidal-shelf/round_2.png",     342, 36,  324, 200, False),
    ("#4", "neon-marquee",   "docs/store_card_v4_r3/neon-marquee/round_2.png",    342, 36,  324, 200, False),
    ("#5", "astral-lattice", "docs/store_card_v4_r3/astral-lattice/round_2.png",  342, 36,  324, 200, False),
    ("#6", "book-spine",     "docs/store_card_v4_r3/book-spine/round_2.png",      180, 36,  162, 100, True),
    ("#7", "dock-notch",     "docs/store_card_v4_r3/dock-notch/round_2.png",      342, 36,  324, 200, False),
]

PANEL_W  = 324
PANEL_H  = 200
BG       = (8, 8, 20)
GAP      = 8
MARGIN   = 20
HEADER_H = 40
ID_H     = 26   # line 1: big numeric ID
LBL_H    = 20   # line 2: concept slug
FOOTER_H = ID_H + LBL_H + 4   # total footer strip height

n        = len(PANELS)
canvas_w = MARGIN * 2 + PANEL_W * n + GAP * (n - 1)
canvas_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

# Header
hdr_f   = hud_font(18, True)
hdr_txt = hdr_f.render("Store Card v4  —  Landscape Evolution  (r3 concepts)", True,
                        (210, 206, 224))
canvas.blit(hdr_txt, ((canvas_w - hdr_txt.get_width()) // 2,
                       MARGIN + (HEADER_H - hdr_txt.get_height()) // 2))

# Fonts for footer
id_font  = hud_font(17, True)    # big #N
lbl_font = hud_font(13, False)   # slug name

panel_y = MARGIN + HEADER_H

for num, label, rel_path, crop_x, crop_y, crop_w, crop_h, scale_up in PANELS:
    col = PANELS.index((num, label, rel_path, crop_x, crop_y, crop_w, crop_h, scale_up))
    x   = MARGIN + col * (PANEL_W + GAP)

    # Load and crop the EPIC panel from the source strip
    src   = pygame.image.load(os.path.join(BASE, rel_path))
    crop  = pygame.Rect(crop_x, crop_y, crop_w, crop_h)
    panel = src.subsurface(crop).copy()
    if scale_up:
        panel = pygame.transform.smoothscale(panel, (PANEL_W, PANEL_H))

    # Thin separator border on all panels for legibility at narrow gaps
    pygame.draw.rect(panel, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)

    canvas.blit(panel, (x, panel_y))

    # Footer: line 1 — numeric ID, prominent
    id_surf = id_font.render(num, True, (255, 230, 120))   # gold-ish
    id_x    = x + (PANEL_W - id_surf.get_width()) // 2
    id_y    = panel_y + PANEL_H + 4
    canvas.blit(id_surf, (id_x, id_y))

    # Footer: line 2 — slug/label
    lbl_surf = lbl_font.render(label, True, (178, 174, 198))
    if lbl_surf.get_width() > PANEL_W - 4:
        tiny = hud_font(11, False)
        lbl_surf = tiny.render(label, True, (178, 174, 198))
    lbl_x = x + (PANEL_W - lbl_surf.get_width()) // 2
    lbl_y = id_y + ID_H + 2
    canvas.blit(lbl_surf, (lbl_x, lbl_y))

out_path = os.path.join(BASE, "docs", "store_card_v4_r3", "showcase.png")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
pygame.image.save(canvas, out_path)
print(f"Saved: {out_path}  ({canvas_w}×{canvas_h})")
