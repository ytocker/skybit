"""Compile 5 tab-strip concept round_2 renders into a showcase PNG.
Includes a BEFORE panel (unpatched current _draw_tabs) + 5 concept panels.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((360, 640), pygame.NOFRAME)

import sys
sys.path.insert(0, "/home/user/skybit")

from game.config import W, H
import game.store_data as sd
import game.store as st
from game.hud import _font

sd.load()
sd._STATE["wallet"] = 12340

# Render BEFORE (unpatched)
before_surf = pygame.Surface((W, H))
scene = st.StoreScene()
scene.view = "category"
scene.tab = 0
scene.page = 0
scene.render(before_surf)

SLUGS = [
    "pill-capsule",
    "segmented-bar",
    "ribbon-fold",
    "underline-indicator",
    "backlight-glow",
]
LABELS = [
    "PILL-CAPSULE",
    "SEGMENTED-BAR",
    "RIBBON-FOLD",
    "UNDERLINE",
    "BACKLIGHT-GLOW",
]

# Layout constants
PANEL_W = 200
PANEL_H = 355   # ~360×640 scaled 0.556×
MARGIN = 20
GAP = 8
HDR_H = 40
FTR_H = 32
N_PANELS = 6  # BEFORE + 5 concepts

canvas_w = MARGIN * 2 + PANEL_W * N_PANELS + GAP * (N_PANELS - 1)
canvas_h = MARGIN + HDR_H + PANEL_H + FTR_H + MARGIN
canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill((8, 8, 20))

hf = _font(13, True)
sf = _font(11, False)

base_dir = "/home/user/skybit/docs/store_tab_strip_redesign"

def draw_panel(panel_surf, x, label, footer):
    """Blit a scaled panel + label + footer onto canvas."""
    thumb = pygame.transform.smoothscale(panel_surf, (PANEL_W, PANEL_H))
    y_panel = MARGIN + HDR_H
    # Panel border
    pygame.draw.rect(canvas, (60, 50, 30), (x - 1, y_panel - 1, PANEL_W + 2, PANEL_H + 2), 1)
    canvas.blit(thumb, (x, y_panel))
    # Footer label
    lt = sf.render(label, True, (255, 220, 80))
    canvas.blit(lt, (x + (PANEL_W - lt.get_width()) // 2, y_panel + PANEL_H + 6))
    # Footer verdict
    fv = sf.render(footer, True, (180, 200, 180))
    canvas.blit(fv, (x + (PANEL_W - fv.get_width()) // 2, y_panel + PANEL_H + 20))

# Header
hdr = hf.render("STORE TAB STRIP — REDESIGN CANDIDATES", True, (255, 240, 160))
canvas.blit(hdr, ((canvas_w - hdr.get_width()) // 2, MARGIN + (HDR_H - hdr.get_height()) // 2))

# BEFORE panel
x0 = MARGIN
draw_panel(before_surf, x0, "BEFORE", "(current)")

# 5 concept panels
for i, (slug, label) in enumerate(zip(SLUGS, LABELS)):
    path = os.path.join(base_dir, slug, "round_2.png")
    img = pygame.image.load(path)
    # round_2 is 360×799: crop to first 640 rows (the full store screen)
    screen_part = img.subsurface(pygame.Rect(0, 0, W, H))
    x = MARGIN + (i + 1) * (PANEL_W + GAP)
    draw_panel(screen_part, x, label, "FINAL")

out = os.path.join(base_dir, "showcase.png")
pygame.image.save(canvas, out)
print(f"saved {canvas_w}×{canvas_h} → {out}")
