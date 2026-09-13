"""5×5 grid: item name label size (columns) × y-offset (rows). skin_mummy at 2×.

Current baseline: size=13.5, offset=70. Grid steps size up and offset down.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

SIZES   = [13.5, 14.5, 15.5, 16.5, 17.5]
OFFSETS = [70, 72, 74, 76, 78]

# Use the SS canvas directly → 2× display size (324×200)
CARD_W = sc.CARD_W * sc.SS   # 324
CARD_H = sc.CARD_H * sc.SS   # 200

COL_LABEL_W = 52
ROW_LABEL_H = 30
GAP     = 6
PAD     = 16
HEADER_H = 40

NCOLS, NROWS = len(SIZES), len(OFFSETS)
sheet_w = PAD + COL_LABEL_W + NCOLS * (CARD_W + GAP) - GAP + PAD
sheet_h = PAD + HEADER_H + ROW_LABEL_H + NROWS * (CARD_H + GAP) - GAP + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

fh = hud_font(17)
fl = hud_font(13)
ft = hud_font(11)

title = fh.render(
    "name label · columns = font size · rows = y-offset · skin_mummy 2×",
    True, (240, 224, 180))
sheet.blit(title, (sheet_w // 2 - title.get_width() // 2,
                   (HEADER_H - title.get_height()) // 2))

# Column headers
for ci, sz in enumerate(SIZES):
    lbl = fl.render(f"sz {sz}" + ("  ←cur" if ci == 0 else ""), True, (200, 210, 228))
    x = PAD + COL_LABEL_W + ci * (CARD_W + GAP) + CARD_W // 2
    sheet.blit(lbl, (x - lbl.get_width() // 2,
                     PAD + HEADER_H + (ROW_LABEL_H - lbl.get_height()) // 2))

# Row headers
for ri, off in enumerate(OFFSETS):
    tag = "  ←cur" if ri == 0 else ""
    lbl = ft.render(f"+{off - 70} ({off}){tag}", True, (200, 210, 228))
    y = PAD + HEADER_H + ROW_LABEL_H + ri * (CARD_H + GAP) + CARD_H // 2
    sheet.blit(lbl, (PAD, y - lbl.get_height() // 2))

# ── patch _name_on and render each cell ──────────────────────────────────────

orig_name_on = sc._name_on


def make_name_on(sz_fixed, dy_delta):
    def _fn(surf, name, cx, cy, max_w):
        f = sc.font(sz_fixed)
        sc.plain_text(surf, name, f, (cx, cy + dy_delta),
                      (250, 248, 240), shadow_a=160,
                      weight=sc.m(0.9), keyline=(6, 6, 16), kw=sc.m(1.0))
    return _fn


inset = sc.m(sc._INSET)
rect  = pygame.Rect(inset, inset,
                    sc.CARD_W * sc.SS - 2 * inset,
                    sc.CARD_H * sc.SS - 2 * inset)

for ri, off in enumerate(OFFSETS):
    dy_delta = sc.m(off - 70)   # SS-space pixels lower than baseline
    for ci, sz in enumerate(SIZES):
        sc._name_on = make_name_on(sz, dy_delta)
        big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
        sc.draw_card(big, 'skin_mummy', rect, equipped=False, secret=False)
        sc._name_on = orig_name_on

        cx = PAD + COL_LABEL_W + ci * (CARD_W + GAP)
        cy = PAD + HEADER_H + ROW_LABEL_H + ri * (CARD_H + GAP)
        sheet.blit(big, (cx, cy))

        # Gold border marks current baseline
        if ri == 0 and ci == 0:
            pygame.draw.rect(sheet, (180, 148, 60),
                             (cx - 2, cy - 2, CARD_W + 4, CARD_H + 4), 2)

sc._name_on = orig_name_on

out = "docs/store_price_tl9/name_label_grid.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
