"""v5 chipup r1 — price chip nudged upward, everything else fixed.

Panels:
  #0  CURRENT    chip at m(88)   (baseline)
  #1  +1 lx      chip 1 logical px higher
  #2  +2 lx      chip 2 logical px higher
  #3  +3 lx      chip 3 logical px higher
  #4  +4 lx      chip 4 logical px higher
  #5  +5 lx      chip 5 logical px higher

Output: docs/store_card_v5_card_item/chipup_r1.png
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

CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
SS = sc.SS
_INSET = 6
PANEL_W = CARD_W * SS
PANEL_H = CARD_H * SS


def draw_card_chipup(surf, sid, rect, chip_up_dev):
    """draw_card() with price chip raised chip_up_dev device px."""
    pal = sc.RARITY[sc._rarity(sid)]
    rad = sc.m(sc.CARD_RAD)
    sc.drop_shadow(surf, rect, rad, blur=sc.m(8), alpha=160, dy=sc.m(4))
    surf.blit(sc.vgrad(rect.w, rect.h, rad, sc.CARD_T, sc.CARD_B, 252, gamma=1.15),
              rect.topleft)
    sc.top_sheen(surf, rect, rad, sc.m(30), peak=62)
    sc.contact_shadow(surf, rect, rad, sc.m(9), alpha=120)
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, sc.m(2)), border_radius=rad)
    sc.bevel_rim(surf, rect, rad, sc.CARD_RING_DEEP, (*sc.CARD_RING_BRIGHT, 235),
                 w=max(1, sc.m(2.0)))
    tray = rect.inflate(-sc.m(7), -sc.m(7))
    trad = rad - sc.m(4)
    pygame.draw.rect(surf, (10, 10, 24, 200), tray.inflate(sc.m(2), sc.m(2)),
                     width=max(1, sc.m(1)), border_radius=trad + sc.m(1))
    pygame.draw.rect(surf, (*sc.CARD_RING_BRIGHT, 90), tray,
                     width=max(1, sc.m(1)), border_radius=trad)

    cx, cy = rect.centerx, rect.y + sc.m(sc.CY_DISC) + sc._DOME_DY
    sc.soft_glow(surf, cx, cy, sc._DOME_R + sc.m(3), pal["glow"], 30, layers=8)
    sc.cabochon(surf, cx, cy, sc._DOME_R, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    name = sc._name(sid)
    sc.cabochon_glass(surf, cx, cy, sc._DOME_R, tint=pal["gem"])
    sc.blit_thumb(surf, sid, cx, cy - sc._ITEM_DY, sc._BOX_PX)

    sc.facet_gem(surf, rect.right - sc.m(19), rect.y + sc.m(19),
                 sc.m(sc.GEM_R + 3), pal["gem"], pal["deep"], mystery=False)
    tier_word = sc._rarity(sid).upper()
    sc._ribbon_lozenge(surf, tier_word, cx, rect.y + sc.m(55) - sc._RIBN_DY,
                       rect.w - sc.m(34), pal)
    sc._name_on(surf, name, cx, rect.y + sc.m(70), rect.w - sc.m(26))
    sc.state_chip(surf, sid, cx, rect.y + sc.m(88) - chip_up_dev,
                  False, False, sc.m(20), variant=sc.PRICE_VARIANT)


def render_panel(chip_up_dev):
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       PANEL_W - 2 * sc.m(_INSET),
                       PANEL_H - 2 * sc.m(_INSET))
    draw_card_chipup(big, SID, rect, chip_up_dev)
    pygame.draw.rect(big, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)
    return big


# ── panels ────────────────────────────────────────────────────────────────────
PANELS = [
    (0,  "CURRENT",  "chip at m(88)"),
    (2,  "+1 lx",    "1 logical px up"),
    (4,  "+2 lx",    "2 logical px up"),
    (6,  "+3 lx",    "3 logical px up"),
    (8,  "+4 lx",    "4 logical px up"),
    (10, "+5 lx",    "5 logical px up"),
]

BG       = (8, 8, 20)
GAP      = 10
MARGIN   = 20
HDR_H    = 44
LBL_H    = 36
FOOTER_H = LBL_H + 8

n        = len(PANELS)
canvas_w = MARGIN * 2 + PANEL_W * n + GAP * (n - 1)
canvas_h = MARGIN + HDR_H + PANEL_H + FOOTER_H + MARGIN

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hf   = hud_font(18, True)
htxt = hf.render(
    f"v5 chipup r1  —  {SID}  —  price chip raised (dome + ribbon fixed)",
    True, (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

lbl_font  = hud_font(12, False)
lbl_font2 = hud_font(10, False)
panel_y   = MARGIN + HDR_H

for col, (chip_up_dev, title, subtitle) in enumerate(PANELS):
    x = MARGIN + col * (PANEL_W + GAP)
    canvas.blit(render_panel(chip_up_dev), (x, panel_y))

    col_colour = (255, 230, 120) if col == 0 else (178, 174, 198)
    t1 = lbl_font.render(title, True, col_colour)
    t2 = lbl_font2.render(subtitle, True, (130, 126, 150))
    lbl_y = panel_y + PANEL_H + 6
    canvas.blit(t1, (x + (PANEL_W - t1.get_width()) // 2, lbl_y))
    canvas.blit(t2, (x + (PANEL_W - t2.get_width()) // 2, lbl_y + t1.get_height() + 2))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_card_v5_card_item", "chipup_r1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}×{canvas_h})")
