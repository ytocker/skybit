"""v5_card_item_size r2 — item thumbnail + dome size ladder on the CONSTELLATION card.

Dome radius scales with item: dome_r = int(box_px / 1.5), preserving the
original ratio (dome_r=40 when box_px=60). The dome center shifts down when
the dome would bleed above the card top.

Panels (all use skin_mummy — EPIC):
  #0  60 px  baseline  (current production)
  #1  72 px  +20 %
  #2  84 px  +40 %
  #3  96 px  +60 %
  #4 108 px  +80 %
  #5 120 px  +100 %

Output: docs/store_card_v5_card_item/size_r2.png
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
PANEL_W = CARD_W * SS   # 324
PANEL_H = CARD_H * SS   # 200

SIZES = [
    ("baseline  60 px", 60),
    ("+20 %   72 px",  72),
    ("+40 %   84 px",  84),
    ("+60 %   96 px",  96),
    ("+80 %  108 px", 108),
    ("+100 % 120 px", 120),
]


def draw_sized_card(surf, sid, rect, box_px):
    """CONSTELLATION card body with dome and item both scaled to box_px.
    Everything else (body, tray, gem badge, ribbon, name, chip) is identical
    to the production draw_card()."""
    pal = sc.RARITY[sc._rarity(sid)]
    rad = sc.m(sc.CARD_RAD)

    sc.drop_shadow(surf, rect, rad, blur=sc.m(8), alpha=160, dy=sc.m(4))
    surf.blit(sc.vgrad(rect.w, rect.h, rad, sc.CARD_T, sc.CARD_B, 252, gamma=1.15),
              rect.topleft)
    sc.top_sheen(surf, rect, rad, sc.m(30), peak=62)
    sc.contact_shadow(surf, rect, rad, sc.m(9), alpha=120)
    pygame.draw.rect(surf, (4, 5, 16), rect,
                     width=max(1, sc.m(2)), border_radius=rad)
    sc.bevel_rim(surf, rect, rad, sc.CARD_RING_DEEP, (*sc.CARD_RING_BRIGHT, 235),
                 w=max(1, sc.m(2.0)))

    tray = rect.inflate(-sc.m(7), -sc.m(7))
    trad = rad - sc.m(4)
    pygame.draw.rect(surf, (10, 10, 24, 200), tray.inflate(sc.m(2), sc.m(2)),
                     width=max(1, sc.m(1)), border_radius=trad + sc.m(1))
    pygame.draw.rect(surf, (*sc.CARD_RING_BRIGHT, 90), tray,
                     width=max(1, sc.m(1)), border_radius=trad)

    # Dome + item, both scaled proportionally to box_px
    dome_r = int(box_px / 1.5)   # original ratio: dome_r=40 when box_px=60
    cx = rect.centerx
    # Prevent dome from bleeding above the card; never move lower than original cy
    cy = max(rect.y + dome_r + sc.m(2), rect.y + sc.m(sc.CY_DISC))

    sc.soft_glow(surf, cx, cy, dome_r + sc.m(3), pal["glow"], 30, layers=8)
    sc.cabochon(surf, cx, cy, dome_r, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    sc.blit_thumb(surf, sid, cx, cy, box_px)
    sc.cabochon_glass(surf, cx, cy, dome_r, tint=pal["gem"])

    sc.facet_gem(surf, rect.right - sc.m(19), rect.y + sc.m(19),
                 sc.m(sc.GEM_R + 3), pal["gem"], pal["deep"], mystery=False)

    name = sc._name(sid)
    tier_word = sc._rarity(sid).upper()
    sc._ribbon(surf, tier_word, cx, rect.y + sc.m(55), rect.w - sc.m(34), pal)
    sc._name_on(surf, name, cx, rect.y + sc.m(70), rect.w - sc.m(26))
    sc.state_chip(surf, sid, cx, rect.y + sc.m(88), False, False, sc.m(20),
                  variant=sc.PRICE_VARIANT)


def render_panel(box_px):
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       PANEL_W - 2 * sc.m(_INSET),
                       PANEL_H - 2 * sc.m(_INSET))
    draw_sized_card(big, SID, rect, box_px)
    pygame.draw.rect(big, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)
    return big


# ── canvas ────────────────────────────────────────────────────────────────────
BG       = (8, 8, 20)
GAP      = 10
MARGIN   = 20
HDR_H    = 44
LBL_H    = 26
FOOTER_H = LBL_H + 8

n         = len(SIZES)
canvas_w  = MARGIN * 2 + PANEL_W * n + GAP * (n - 1)
canvas_h  = MARGIN + HDR_H + PANEL_H + FOOTER_H + MARGIN

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hf   = hud_font(18, True)
htxt = hf.render(
    f"v5 card item size r2  —  {SID}  (EPIC)  — item + dome scale together",
    True, (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

lbl_font = hud_font(12, False)
panel_y  = MARGIN + HDR_H

for col, (label, box_px) in enumerate(SIZES):
    x = MARGIN + col * (PANEL_W + GAP)
    panel = render_panel(box_px)
    canvas.blit(panel, (x, panel_y))

    lbl = f"{'BASELINE' if col == 0 else f'#{col}'}  {label}"
    col_colour = (255, 230, 120) if col == 0 else (178, 174, 198)
    lbl_surf = lbl_font.render(lbl, True, col_colour)
    if lbl_surf.get_width() > PANEL_W - 4:
        lbl_surf = hud_font(10, False).render(lbl, True, col_colour)
    canvas.blit(lbl_surf,
                (x + (PANEL_W - lbl_surf.get_width()) // 2,
                 panel_y + PANEL_H + 6))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_card_v5_card_item", "size_r2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}×{canvas_h})")
