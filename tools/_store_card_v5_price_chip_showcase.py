"""Showcase figure: BEFORE vs 5 price-chip concepts, round 2.

Crops the first affordable card (324×200) from each concept's round_2.png
and lays it alongside a fresh BEFORE render using the current draw_card().

Output: docs/store_card_v5_price_chip/showcase.png
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.hud import _font as hud_font

SID = "skin_mummy"

CARD_W = sc.CARD_W * sc.SS   # 324
CARD_H = sc.CARD_H * sc.SS   # 200
_INSET  = sc._INSET


# ── BEFORE panel: current draw_card() ─────────────────────────────────────────
def render_before():
    surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       CARD_W - 2 * sc.m(_INSET),
                       CARD_H - 2 * sc.m(_INSET))
    sc.draw_card(surf, SID, rect, equipped=False, secret=False,
                 variant=sc.PRICE_VARIANT)
    return surf


# ── concept panels: crop first affordable card from each round_2.png ──────────
# Crop coordinates verified by pixel-sampling each PNG.
CONCEPTS = [
    ("Obsidian\nCoin Slot",    "obsidian-coin-slot",    128, 64),
    ("Night Enamel\nTablet",   "night-enamel-tablet",    22, 44),
    ("Struck\nIntaglio Plate", "struck-intaglio-plate",  30, 64),
    ("Deep Space\nTag",        "deep-space-tag",         82, 86),
    ("Recessed\nCoin Well",    "recessed-coin-well",     44, 70),
]

docs_dir = os.path.join(os.path.dirname(__file__), "..",
                        "docs", "store_card_v5_price_chip")

def load_concept_panel(slug, cx, cy):
    path = os.path.join(docs_dir, slug, "round_2.png")
    img = pygame.image.load(path)
    crop = img.subsurface(pygame.Rect(cx, cy, CARD_W, CARD_H)).copy()
    return crop


# ── layout ────────────────────────────────────────────────────────────────────
BG       = (8, 8, 20)
MARGIN   = 24
GAP      = 10
HDR_H    = 44
LBL_H    = 40

n        = 1 + len(CONCEPTS)
canvas_w = MARGIN * 2 + CARD_W * n + GAP * (n - 1)
canvas_h = MARGIN + HDR_H + CARD_H + LBL_H + MARGIN

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

# header
hf   = hud_font(18, True)
htxt = hf.render(
    f"v5 price chip redesign  —  BEFORE vs 5 concepts  —  round 2  ({SID})",
    True, (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

lbl_font  = hud_font(12, True)
lbl_font2 = hud_font(10, False)
panel_y   = MARGIN + HDR_H

# BEFORE panel
before = render_before()
canvas.blit(before, (MARGIN, panel_y))
t = lbl_font.render("BEFORE", True, (255, 230, 120))
canvas.blit(t, (MARGIN + (CARD_W - t.get_width()) // 2,
                panel_y + CARD_H + 6))
t2 = lbl_font2.render("current gold pill", True, (130, 126, 150))
canvas.blit(t2, (MARGIN + (CARD_W - t2.get_width()) // 2,
                 panel_y + CARD_H + 6 + t.get_height() + 2))

# concept panels
for col, (label, slug, cx, cy) in enumerate(CONCEPTS, start=1):
    x = MARGIN + col * (CARD_W + GAP)
    panel = load_concept_panel(slug, cx, cy)
    canvas.blit(panel, (x, panel_y))

    lines = label.split("\n")
    t1 = lbl_font.render(lines[0], True, (178, 174, 198))
    canvas.blit(t1, (x + (CARD_W - t1.get_width()) // 2,
                     panel_y + CARD_H + 6))
    if len(lines) > 1:
        t2 = lbl_font2.render(lines[1], True, (130, 126, 150))
        canvas.blit(t2, (x + (CARD_W - t2.get_width()) // 2,
                         panel_y + CARD_H + 6 + t1.get_height() + 2))

out = os.path.join(docs_dir, "showcase.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}×{canvas_h})")
