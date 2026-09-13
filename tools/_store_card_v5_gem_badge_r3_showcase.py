"""Phase-5 showcase for the gem-badge iteration 3 /design run.

Six panels (BEFORE + 5 concepts), single row:
  BEFORE           — original facet_gem unchanged (skin_mummy EPIC)
  improved-octagon — r2 crop
  princess-cut     — r2 crop
  oval-cut         — r2 crop
  radiant-cut      — r2 crop
  kite-cut         — r2 crop
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
from game.hud import _font as hud_font

# ── layout constants ────────────────────────────────────────────────────────
BG         = (8, 8, 20)
MARGIN     = 20
GAP        = 8
PANEL_W    = sc.CARD_W * sc.SS          # 324
PANEL_H    = sc.CARD_H * sc.SS + 16     # 216
HDR_H      = 40
FTR_H      = 32
_INSET     = sc._INSET

# r3 canvas constants: header_h=40, pad=28, row1_y=68
# All r3 round_2 scripts use canvas_w=1792 with row1_y=header_h+pad=68
R3_HDR_H   = 40
R3_PAD     = 28
R3_GAP     = 24
R3_CARD_Y  = R3_HDR_H + R3_PAD         # 68
R3_ROW1_W  = PANEL_W * 2 + R3_GAP      # 672

SLUGS = [
    "improved-octagon",
    "princess-cut",
    "oval-cut",
    "radiant-cut",
    "kite-cut",
]


def _render_before():
    """Render the card with the original (unpatched) facet_gem."""
    ch = sc.CARD_H * sc.SS
    surf = pygame.Surface((PANEL_W, ch + 16), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       PANEL_W - 2 * sc.m(_INSET),
                       ch - 2 * sc.m(_INSET))
    sc.draw_card(surf, "skin_mummy", rect,
                 equipped=False, secret=False, variant=sc.PRICE_VARIANT)
    return surf


def _crop_mummy(slug):
    """Load round_2.png for a concept and crop the skin_mummy EPIC card."""
    path = f"/home/user/skybit/docs/store_card_v5_gem_badge_r3/{slug}/round_2.png"
    img = pygame.image.load(path).convert_alpha()
    canvas_w = img.get_width()
    x0 = (canvas_w - R3_ROW1_W) // 2
    y0 = R3_CARD_Y
    return img.subsurface((x0, y0, PANEL_W, PANEL_H)).copy()


def main():
    panels = [("BEFORE\noriginal", _render_before())]
    for slug in SLUGS:
        panels.append((slug + "\nFINAL", _crop_mummy(slug)))

    n = len(panels)   # 6
    canvas_w = MARGIN * 2 + PANEL_W * n + GAP * (n - 1)
    canvas_h = MARGIN + HDR_H + GAP + PANEL_H + GAP + FTR_H + MARGIN

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill(BG)

    hdr_f = hud_font(28, True)
    lbl_f = hud_font(16, True)

    hdr = hdr_f.render("gem badge redesign — iteration 3 showcase", True, (232, 228, 246))
    y = MARGIN + (HDR_H - hdr.get_height()) // 2
    canvas.blit(hdr, ((canvas_w - hdr.get_width()) // 2, y))

    y = MARGIN + HDR_H + GAP
    x = MARGIN
    for label, panel in panels:
        canvas.blit(panel, (x, y))
        lines = label.split("\n")
        ly = y + PANEL_H + GAP
        for line in lines:
            lbl = lbl_f.render(line, True, (200, 196, 220))
            canvas.blit(lbl, (x + (PANEL_W - lbl.get_width()) // 2, ly))
            ly += lbl.get_height() + 2
        x += PANEL_W + GAP

    out = "/home/user/skybit/docs/store_card_v5_gem_badge_r3/showcase.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
