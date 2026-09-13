"""Stitch docs/store_card_v4/showcase.png from original + 5 concept r2 renders.

Each source is a 3-panel (RARE/EPIC/LEGENDARY) strip at SS=2. We crop the
EPIC panel (middle, x=342, y=10, 324x200) from each and arrange 6 panels with
labels into a single comparison figure.
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from game.store_cards import font

BASE = os.path.join(os.path.dirname(__file__), "..", "docs", "store_card_v4")

PANELS = [
    ("CURRENT",          os.path.join(BASE, "original.png")),
    ("portrait-vignette",os.path.join(BASE, "portrait-vignette", "round_2.png")),
    ("landscape-hero",   os.path.join(BASE, "landscape-hero",    "round_2.png")),
    ("full-bleed-disc",  os.path.join(BASE, "full-bleed-disc",   "round_2.png")),
    ("intaglio-seal",    os.path.join(BASE, "intaglio-seal",     "round_2.png")),
    ("corner-anchor",    os.path.join(BASE, "corner-anchor",     "round_2.png")),
]

# EPIC panel coordinates inside each strip (SS=2 geometry, MARGIN=10, GAP=8, BIG_W=324)
EPIC_X = 10 + (324 + 8)  # = 342
EPIC_Y = 10
PANEL_W = 324
PANEL_H = 200

BG       = (8,  8,  20)
GAP      = 8
MARGIN   = 20
HEADER_H = 40
FOOTER_H = 32

n = len(PANELS)
canvas_w = MARGIN * 2 + PANEL_W * n + GAP * (n - 1)
canvas_h = HEADER_H + PANEL_H + FOOTER_H + MARGIN

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

# Header
hdr_font = font(10)
hdr = hdr_font.render("Store Card v4 — Concept Exploration", True, (200, 200, 220))
canvas.blit(hdr, ((canvas_w - hdr.get_width()) // 2, (HEADER_H - hdr.get_height()) // 2))

lbl_font  = font(7)
tiny_font = font(5.5)

for i, (label, path) in enumerate(PANELS):
    x = MARGIN + i * (PANEL_W + GAP)
    y = HEADER_H

    src = pygame.image.load(path)
    crop = pygame.Rect(EPIC_X, EPIC_Y, PANEL_W, PANEL_H)
    panel = src.subsurface(crop).copy()
    canvas.blit(panel, (x, y))

    # Footer label
    lbl_surf = lbl_font.render(label, True, (180, 180, 200))
    if lbl_surf.get_width() > PANEL_W:
        lbl_surf = tiny_font.render(label, True, (180, 180, 200))
    canvas.blit(lbl_surf, (x + (PANEL_W - lbl_surf.get_width()) // 2,
                            y + PANEL_H + (FOOTER_H - lbl_surf.get_height()) // 2))

out_path = os.path.join(BASE, "showcase.png")
pygame.image.save(canvas, out_path)
print(f"Saved: {out_path}  ({canvas_w}x{canvas_h})")
