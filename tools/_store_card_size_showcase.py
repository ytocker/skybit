"""Phase 5 showcase — store-card-size exploration.

Baseline (current live card) + 5 concepts, all at 2× SS (324×200),
with a second row at 1× (162×100) for final-size legibility.

Concept panel crop offsets (gathered from r2 script layouts):
  portrait_rise:  x=348, y=84,  324×200
  tight_inset:    x=362, y=68,  324×200
  dome_swell:     x=348, y=84,  324×200
  full_bleed:     x=368, y=74,  324×200
  arched_niche:   x=348, y=84,  324×200
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from PIL import Image as PILImage
import numpy as np

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

SID = "skin_mummy"
SS = sc.SS
CARD_W, CARD_H = sc.CARD_W, sc.CARD_H    # 162, 100
PANEL_W = CARD_W * SS                     # 324
PANEL_H = CARD_H * SS                     # 200


# ── helpers ──────────────────────────────────────────────────────────────────

def pil_crop_to_pygame(path, x, y, w, h):
    """Load a PNG with PIL, crop to (x, y, w, h), return a pygame Surface."""
    img = PILImage.open(path).convert("RGBA")
    region = img.crop((x, y, x + w, y + h))
    arr = np.array(region, dtype=np.uint8)
    # pygame expects (w, h, 4) with RGBA byte order
    surf = pygame.image.fromstring(arr.tobytes(), (w, h), "RGBA")
    return surf


def render_baseline():
    """Fresh baseline card at SS=2."""
    sc._card_cache.clear()
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, PANEL_W - 2 * inset, PANEL_H - 2 * inset)
    sc.draw_card(big, SID, rect, equipped=False, secret=False)
    sc._card_cache.clear()
    return big


BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "store_card_size")

CONCEPTS = [
    # (slug, display label, png path, crop_x, crop_y)
    ("portrait_rise",  "A · portrait-rise",  "portrait_rise/round_2.png",  348, 84),
    ("tight_inset",    "B · tight-inset",     "tight_inset/round_2.png",    362, 68),
    ("dome_swell",     "C · dome-swell",      "dome_swell/round_2.png",     348, 84),
    ("full_bleed",     "D · full-bleed",      "full_bleed/round_2.png",     368, 74),
    ("arched_niche",   "E · arched-niche",    "arched_niche/round_2.png",   348, 84),
]

# ── load all panels ──────────────────────────────────────────────────────────

baseline_surf = render_baseline()

concept_surfs = []
for slug, lbl, rel_path, cx, cy in CONCEPTS:
    full_path = os.path.join(BASE_DIR, rel_path)
    surf = pil_crop_to_pygame(full_path, cx, cy, PANEL_W, PANEL_H)
    concept_surfs.append((lbl, surf))

all_panels = [("BASELINE\n(current)", baseline_surf)] + concept_surfs

N = len(all_panels)   # 6

# ── layout constants ─────────────────────────────────────────────────────────
BG      = (8, 8, 20)
PAD     = 20
GAP     = 10
HDR_H   = 52
LBL_H   = 32       # label row above each card row
ROW_GAP = 22       # vertical gap between 2× and 1× rows
FOOTER  = 20

sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = (PAD + HDR_H
           + LBL_H + PANEL_H          # row 1: 2× panels
           + ROW_GAP
           + LBL_H + CARD_H           # row 2: 1× panels
           + FOOTER)

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

# ── fonts ─────────────────────────────────────────────────────────────────────
fh = hud_font(18, True)
fl = hud_font(13, True)
fs = hud_font(11, False)

# header
title = fh.render("store card size — 5 concepts vs baseline  ·  skin_mummy", True, (240, 224, 180))
sheet.blit(title, ((sheet_w - title.get_width()) // 2, PAD + (HDR_H - title.get_height()) // 2))

# ── row 1: 2× panels ─────────────────────────────────────────────────────────
y2 = PAD + HDR_H + LBL_H
for i, (lbl, surf) in enumerate(all_panels):
    x = PAD + i * (PANEL_W + GAP)

    # label (may contain \n)
    lines = lbl.split("\n")
    col = (170, 166, 190) if i == 0 else (255, 226, 120)
    for li, line in enumerate(lines):
        t = fl.render(line, True, col)
        ly = PAD + HDR_H + (LBL_H - fl.get_height() * len(lines)) // 2 + li * fl.get_height()
        sheet.blit(t, (x + (PANEL_W - t.get_width()) // 2, ly))

    sheet.blit(surf, (x, y2))

# ── row 2: 1× panels ─────────────────────────────────────────────────────────
y1 = y2 + PANEL_H + ROW_GAP + LBL_H
sub_row_lbl = fs.render("1× final size (162×100 shipped pixels)", True, (160, 160, 190))
sheet.blit(sub_row_lbl, ((sheet_w - sub_row_lbl.get_width()) // 2,
                          y2 + PANEL_H + ROW_GAP + (LBL_H - sub_row_lbl.get_height()) // 2))

for i, (lbl, surf) in enumerate(all_panels):
    x = PAD + i * (PANEL_W + GAP)
    small = pygame.transform.smoothscale(surf, (CARD_W, CARD_H))
    # centre the small card under its 2× counterpart
    ox = (PANEL_W - CARD_W) // 2
    sheet.blit(small, (x + ox, y1))

# ── save ─────────────────────────────────────────────────────────────────────
out = os.path.join(BASE_DIR, "showcase.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}×{sheet_h} → {out}")

# ── pixel sanity (no image open — use PIL on saved file) ─────────────────────
check = PILImage.open(out).convert("RGB")
w_check, h_check = check.size
assert w_check == sheet_w and h_check == sheet_h, f"size mismatch {w_check}×{h_check}"
# Background corner should be dark navy
bg_px = check.getpixel((2, 2))
assert bg_px[0] < 30 and bg_px[2] < 40, f"BG pixel unexpected: {bg_px}"
print(f"pixel sanity OK — {w_check}×{h_check}, corner={bg_px}")
