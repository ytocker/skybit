"""v5_card_item_ribbon r2 — lozenge ribbon, Y-offset ladder.

Design #2 locked: box_px=84. Ribbon B (lozenge) locked.
Shows original position + 5 progressively higher placements.

Panels:
  #0  ORIGINAL   ribbon at m(55)          — no shift
  #1  -4 dev     m(55) - 4  (2 log px up)
  #2  -8 dev     m(55) - 8  (4 log px up)
  #3  -12 dev    m(55) - 12 (6 log px up)
  #4  -16 dev    m(55) - 16 (8 log px up)
  #5  -20 dev    m(55) - 20 (10 log px up)

Output: docs/store_card_v5_card_item/ribbon_r2.png
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.draw import lerp_color, WHITE, NEAR_BLACK
from game.hud import _font as hud_font

BOX_PX = 84
SID    = "skin_mummy"

CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
SS = sc.SS
_INSET = 6
PANEL_W = CARD_W * SS   # 324
PANEL_H = CARD_H * SS   # 200


def _ribbon_lozenge(surf, tier_word, cx, cy, max_w, pal):
    """Lozenge — outward pointed ends (ribbon B)."""
    f = sc.font(8.5)
    tw = sc._glyph_base(tier_word, f, sc.m(1.4)).get_width()
    pad = sc.m(14)
    w = min(max_w, tw + pad * 2)
    h = sc.m(10)
    pt = h // 2
    x0, y0 = cx - w // 2, cy - h // 2
    poly = [(0, h // 2), (pt, 0), (w - pt, 0),
            (w, h // 2), (w - pt, h), (pt, h)]
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = sc.vgrad_stops(w, h, 0,
                          [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                          255, gamma=1.08)
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), poly)
    surf.blit(sh, (x0, y0 + sc.m(2)))
    surf.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(surf, (4, 5, 16), abspoly, width=max(1, sc.m(1.4)))
    sc.plain_text(surf, tier_word, f, (cx, cy), (14, 12, 26),
                  shadow_a=0, tracking=sc.m(1.4), weight=sc.m(0.7))


def draw_card_with_ribbon(surf, sid, rect, box_px, ribbon_y_offset_dev):
    """Full CONSTELLATION card with lozenge ribbon shifted up by ribbon_y_offset_dev device px."""
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

    dome_r = int(box_px / 1.5)
    cx = rect.centerx
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
    ribbon_cy = rect.y + sc.m(55) - ribbon_y_offset_dev
    _ribbon_lozenge(surf, tier_word, cx, ribbon_cy, rect.w - sc.m(34), pal)
    sc._name_on(surf, name, cx, rect.y + sc.m(70), rect.w - sc.m(26))
    sc.state_chip(surf, sid, cx, rect.y + sc.m(88), False, False, sc.m(20),
                  variant=sc.PRICE_VARIANT)


def render_panel(offset_dev):
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       PANEL_W - 2 * sc.m(_INSET),
                       PANEL_H - 2 * sc.m(_INSET))
    draw_card_with_ribbon(big, SID, rect, BOX_PX, offset_dev)
    pygame.draw.rect(big, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)
    return big


# ── panels: (offset_dev, label_line1, label_line2) ────────────────────────────
PANELS = [
    (0,  "ORIGINAL",  "no shift"),
    (4,  "#1  -4 dev", "2 log px up"),
    (8,  "#2  -8 dev", "4 log px up"),
    (12, "#3  -12 dev","6 log px up"),
    (16, "#4  -16 dev","8 log px up"),
    (20, "#5  -20 dev","10 log px up"),
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
    f"v5 card ribbon r2  —  {SID}  (EPIC)  —  lozenge ribbon Y-offset ladder",
    True, (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

lbl_font  = hud_font(12, False)
lbl_font2 = hud_font(10, False)
panel_y   = MARGIN + HDR_H

for col, (offset_dev, title, subtitle) in enumerate(PANELS):
    x = MARGIN + col * (PANEL_W + GAP)
    panel = render_panel(offset_dev)
    canvas.blit(panel, (x, panel_y))

    col_colour = (255, 230, 120) if col == 0 else (178, 174, 198)
    t1 = lbl_font.render(title, True, col_colour)
    t2 = lbl_font2.render(subtitle, True, (130, 126, 150))
    lbl_y = panel_y + PANEL_H + 6
    canvas.blit(t1, (x + (PANEL_W - t1.get_width()) // 2, lbl_y))
    canvas.blit(t2, (x + (PANEL_W - t2.get_width()) // 2, lbl_y + t1.get_height() + 2))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_card_v5_card_item", "ribbon_r2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}×{canvas_h})")
