"""store_card_v3 showcase stitch.

Extracts the EPIC-tier panel (2× SS, 324×200) from each concept's round_2.png
review sheet, plus the pre-rendered original, and stitches them into a 6-panel
showcase. A real-scale 1× strip (162×100) is appended below each panel.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.hud import _font

# ── layout constants (must match every r2 script) ────────────────────────────
MARGIN   = 20
HEADER_H = 30
GUTTER   = 16
PANEL_W  = 324   # CARD_W * SS
PANEL_H  = 200   # CARD_H * SS
CARD_W   = 162
CARD_H   = 100

# EPIC is the second column (index 1) in every 3-up review sheet.
EPIC_X = MARGIN + 1 * (PANEL_W + GUTTER)   # 360
EPIC_Y = MARGIN + HEADER_H                  # 50
EPIC_CROP = (EPIC_X, EPIC_Y, EPIC_X + PANEL_W, EPIC_Y + PANEL_H)

CONCEPTS = [
    ("CURRENT",          "docs/store_card_v3/original.png",              None),
    ("arc-veil-pill",    "docs/store_card_v3/arc-veil-pill/round_2.png",    EPIC_CROP),
    ("product-line-bar", "docs/store_card_v3/product-line-bar/round_2.png", EPIC_CROP),
    ("struck-denom.",    "docs/store_card_v3/struck-denomination/round_2.png", EPIC_CROP),
    ("sidebar-spine",    "docs/store_card_v3/sidebar-spine/round_2.png",   EPIC_CROP),
    ("bridge-nameplate", "docs/store_card_v3/bridge-nameplate/round_2.png", EPIC_CROP),
]

N = len(CONCEPTS)

SHOWCASE_HEADER_H = 40
FOOTER_H          = 28
STRIP_LABEL_H     = 18
STRIP_H           = CARD_H   # 1× real scale

sheet_w = MARGIN * 2 + PANEL_W * N + GUTTER * (N - 1)
sheet_h = (MARGIN + SHOWCASE_HEADER_H + PANEL_H + FOOTER_H
           + STRIP_LABEL_H + STRIP_H + MARGIN)

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont  = _font(24, True)
ffont  = _font(18, True)
sfont  = _font(14, True)

htxt = hfont.render("store_card_v3 — showcase (EPIC tier)", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (SHOWCASE_HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + SHOWCASE_HEADER_H
panels  = []

for i, (label, path, crop) in enumerate(CONCEPTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    src = pygame.image.load(path)
    if crop is not None:
        panel = src.subsurface(pygame.Rect(
            crop[0], crop[1], crop[2] - crop[0], crop[3] - crop[1]
        ))
    else:
        # original.png is already a single 324×200 surface.
        panel = src

    # Blit SS panel.
    sheet.blit(panel, (px, panel_y))
    panels.append(panel)

    # Footer label.
    ftxt = ffont.render(label, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# Real-scale 1× strip.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1×):", True, (190, 194, 210))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))

strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (px + (PANEL_W - CARD_W) // 2, strip_y))

out = "docs/store_card_v3/showcase.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
