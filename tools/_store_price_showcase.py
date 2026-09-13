"""Showcase comparison for store price redesign — 6 panels (BEFORE + 5 concepts).

Renders the original price_chip plus crops skin_mummy EPIC affordable from each
round_2 render sheet, arranges them in a 3×2 grid, and saves the showcase.

Review-only tooling — never imported by the game.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

# ── render the BEFORE card (original unpatched price_chip) ───────────────────
def render_before():
    sd.wallet = 999_999          # ensure affordable
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset,
                       sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, "skin_mummy", rect, equipped=False, secret=False,
                 variant=sc.PRICE_VARIANT)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


# ── crop regions for each r2 PNG (skin_mummy EPIC affordable at 1×) ──────────
# Each tuple: (label, png_path, crop_rect)
CONCEPTS = [
    ("spine-foot",
     "docs/store_price_redesign/spine-foot/round_2.png",
     pygame.Rect(28, 70, 162, 100)),
    ("dog-ear",
     "docs/store_price_redesign/dog-ear/round_2.png",
     pygame.Rect(20, 40, 162, 100)),
    ("stacked-header",
     "docs/store_price_redesign/header-rail/round_2.png",
     pygame.Rect(20, 60, 162, 100)),
    ("museum-label",
     "docs/store_price_redesign/museum-label/round_2.png",
     pygame.Rect(20, 60, 162, 100)),
    ("denomination-badge",
     "docs/store_price_redesign/denomination-badge/round_2.png",
     pygame.Rect(20, 64, 162, 108)),   # badge overflows card bottom by 8px
]

# ── collect panels ────────────────────────────────────────────────────────────
panels = [("BEFORE\n(original)", render_before(), (162, 100))]

for slug, path, crop in CONCEPTS:
    img = pygame.image.load(path)
    sub = img.subsurface(crop).copy()
    panels.append((slug, sub, (crop.w, crop.h)))

# ── layout constants ──────────────────────────────────────────────────────────
NCOLS    = 3
PAD      = 20
GAP      = 10
HEADER_H = 44
LABEL_H  = 22
PANEL_W  = 240
PANEL_H  = 158   # enough room for tallest crop (108px) at ~1.46× zoom

BG      = (8, 8, 20)
BORDER  = (46, 44, 68)
GOLD    = (255, 220, 80)
PALE    = (206, 202, 224)

NROWS   = (len(panels) + NCOLS - 1) // NCOLS
canvas_w = PAD * 2 + NCOLS * PANEL_W + (NCOLS - 1) * GAP
canvas_h = HEADER_H + NROWS * (PANEL_H + LABEL_H) + (NROWS - 1) * GAP + PAD

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

# header
hf = hud_font(11, True)
ht = hf.render("store price redesign — round 2 concepts", True, GOLD)
canvas.blit(ht, (canvas_w // 2 - ht.get_width() // 2,
                 (HEADER_H - ht.get_height()) // 2))

lf = hud_font(8, True)

for i, (label, surf, (src_w, src_h)) in enumerate(panels):
    col = i % NCOLS
    row = i // NCOLS
    px = PAD + col * (PANEL_W + GAP)
    py = HEADER_H + row * (PANEL_H + LABEL_H + GAP)

    # scale proportionally to fit within PANEL_W × PANEL_H, center
    scale = min(PANEL_W / src_w, PANEL_H / src_h)
    dw, dh = int(src_w * scale), int(src_h * scale)
    scaled = pygame.transform.smoothscale(surf, (dw, dh))

    ox = px + (PANEL_W - dw) // 2
    oy = py + (PANEL_H - dh) // 2
    pygame.draw.rect(canvas, BORDER, (px, py, PANEL_W, PANEL_H))
    canvas.fill(BG, (px + 1, py + 1, PANEL_W - 2, PANEL_H - 2))
    canvas.blit(scaled, (ox, oy))
    pygame.draw.rect(canvas, BORDER, (px, py, PANEL_W, PANEL_H), 1)

    # label (may contain \n)
    top_lbl = label.split("\n")[0]
    lt = lf.render(top_lbl, True, GOLD if i == 0 else PALE)
    canvas.blit(lt, (px + (PANEL_W - lt.get_width()) // 2, py + PANEL_H + 4))
    if "\n" in label:
        sub_lbl = label.split("\n")[1]
        ls = lf.render(sub_lbl, True, (160, 156, 180))
        canvas.blit(ls, (px + (PANEL_W - ls.get_width()) // 2, py + PANEL_H + 4 + lt.get_height()))

out = "docs/store_price_redesign/showcase.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
