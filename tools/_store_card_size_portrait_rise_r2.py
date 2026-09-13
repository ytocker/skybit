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

CARD_W_SS, CARD_H_SS = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS  # 324, 200
inset = sc.m(sc._INSET)
rect_ss = pygame.Rect(inset, inset, CARD_W_SS - 2*inset, CARD_H_SS - 2*inset)

def render_card(sid='skin_mummy', equipped=False):
    sc._card_cache.clear()
    surf = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    sc.draw_card(surf, sid, rect_ss, equipped=equipped, secret=False)
    return surf

# Baseline
baseline_ss = render_card()

# Patch for portrait-rise (r2: nudge dome down + shrink to rebalance margins)
orig_cy = sc.CY_DISC
orig_dr = sc._DOME_R
orig_bp = sc._BOX_PX
sc.CY_DISC = 28
sc._DOME_R = 62
sc._BOX_PX = 100
concept_ss = render_card()
# Restore
sc.CY_DISC = orig_cy
sc._DOME_R = orig_dr
sc._BOX_PX = orig_bp
sc._card_cache.clear()

# Comparison sheet
GAP, PAD, LABEL_H, HEADER_H = 8, 16, 28, 40
NCOLS = 2
sheet_w = PAD*2 + NCOLS*CARD_W_SS + (NCOLS-1)*GAP
sheet_h = PAD*2 + HEADER_H + 2*(LABEL_H + CARD_H_SS + GAP) + LABEL_H + sc.CARD_H*2 + GAP
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

fl = hud_font(14)
fh = hud_font(17)

title = fh.render("portrait-rise r2  ·  baseline vs concept  (skin_mummy)", True, (240,224,180))
sheet.blit(title, (sheet_w//2 - title.get_width()//2, (HEADER_H - title.get_height())//2))

panels_ss = [("BASELINE (2×)", baseline_ss), ("PORTRAIT-RISE r2 (2×)", concept_ss)]
y_ss = PAD + HEADER_H
for i, (label, surf) in enumerate(panels_ss):
    x = PAD + i*(CARD_W_SS + GAP)
    lbl = fl.render(label, True, (200,210,228))
    sheet.blit(lbl, (x + CARD_W_SS//2 - lbl.get_width()//2, y_ss))
    sheet.blit(surf, (x, y_ss + LABEL_H))

y_1x = y_ss + LABEL_H + CARD_H_SS + GAP + LABEL_H
row_label = fl.render("at 1x  (162x100 final size)", True, (180, 180, 200))
sheet.blit(row_label, (PAD, y_1x - LABEL_H))
for i, (label, surf) in enumerate(panels_ss):
    x = PAD + i*(CARD_W_SS + GAP)
    small = pygame.transform.smoothscale(surf, (sc.CARD_W, sc.CARD_H))
    sheet.blit(small, (x, y_1x))

import os as _os
out = "docs/store_card_size/portrait_rise/round_2.png"
_os.makedirs(_os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
