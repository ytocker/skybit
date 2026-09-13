"""v5 card item — final locked design vs original production.

Left:  original card (all v4 defaults)
Right: v5 locked card (box=84, dome proportional, item +5 log px up, lozenge ribbon -4 log px)

Output: docs/store_card_v5_card_item/final_r1.png
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

SID    = "skin_mummy"
CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
SS = sc.SS
_INSET = 6
PANEL_W = CARD_W * SS
PANEL_H = CARD_H * SS


def _ribbon_original(surf, tier_word, cx, cy, max_w, pal):
    """Production notched-hex ribbon (v4 original)."""
    f = sc.font(8.5)
    tw = sc._glyph_base(tier_word, f, sc.m(1.4)).get_width()
    pad = sc.m(12)
    w = min(max_w, tw + pad * 2)
    h = sc.m(15)
    notch = sc.m(5)
    x0, y0 = cx - w // 2, cy - h // 2
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = sc.vgrad_stops(w, h, 0, [(0.0, top), (0.5, pal["glow"]), (1.0, bot)], 255, gamma=1.08)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2), (w - notch, h), (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), poly)
    surf.blit(sh, (x0, y0 + sc.m(2)))
    surf.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(surf, (4, 5, 16), abspoly, width=max(1, sc.m(1.4)))
    sc.plain_text(surf, tier_word, f, (cx, cy), (14, 12, 26), shadow_a=0,
                  tracking=sc.m(1.4), weight=sc.m(0.7))


def render_original():
    """v4-style card: original dome size, centred item, notched ribbon."""
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       PANEL_W - 2 * sc.m(_INSET), PANEL_H - 2 * sc.m(_INSET))
    pal = sc.RARITY[sc._rarity(SID)]
    rad = sc.m(sc.CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=sc.m(8), alpha=160, dy=sc.m(4))
    big.blit(sc.vgrad(rect.w, rect.h, rad, sc.CARD_T, sc.CARD_B, 252, gamma=1.15), rect.topleft)
    sc.top_sheen(big, rect, rad, sc.m(30), peak=62)
    sc.contact_shadow(big, rect, rad, sc.m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, sc.m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, sc.CARD_RING_DEEP, (*sc.CARD_RING_BRIGHT, 235), w=max(1, sc.m(2.0)))
    tray = rect.inflate(-sc.m(7), -sc.m(7))
    trad = rad - sc.m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(sc.m(2), sc.m(2)), width=max(1, sc.m(1)), border_radius=trad + sc.m(1))
    pygame.draw.rect(big, (*sc.CARD_RING_BRIGHT, 90), tray, width=max(1, sc.m(1)), border_radius=trad)
    cx, cy = rect.centerx, rect.y + sc.m(sc.CY_DISC)
    orig_r = sc.m(sc.R_DISC)
    sc.soft_glow(big, cx, cy, orig_r + sc.m(3), pal["glow"], 30, layers=8)
    sc.cabochon(big, cx, cy, orig_r, sc.CABO_LO, sc.CABO_HI, ring=pal["gem"], ring_a=50)
    sc.blit_thumb(big, SID, cx, cy, orig_r * 1.5)
    sc.cabochon_glass(big, cx, cy, orig_r, tint=pal["gem"])
    sc.facet_gem(big, rect.right - sc.m(19), rect.y + sc.m(19), sc.m(sc.GEM_R + 3), pal["gem"], pal["deep"], mystery=False)
    _ribbon_original(big, sc._rarity(SID).upper(), cx, rect.y + sc.m(55), rect.w - sc.m(34), pal)
    sc._name_on(big, sc._name(SID), cx, rect.y + sc.m(70), rect.w - sc.m(26))
    sc.state_chip(big, SID, cx, rect.y + sc.m(88), False, False, sc.m(20), variant=sc.PRICE_VARIANT)
    pygame.draw.rect(big, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)
    return big


def render_v5():
    """v5 locked card — uses the updated draw_card()."""
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       PANEL_W - 2 * sc.m(_INSET), PANEL_H - 2 * sc.m(_INSET))
    sc.draw_card(big, SID, rect, equipped=False, secret=False)
    pygame.draw.rect(big, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)
    return big


BG     = (8, 8, 20)
GAP    = 20
MARGIN = 30
HDR_H  = 44
LBL_H  = 26
FOOTER = LBL_H + 8

canvas_w = MARGIN * 2 + PANEL_W * 2 + GAP
canvas_h = MARGIN + HDR_H + PANEL_H + FOOTER + MARGIN
canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hf   = hud_font(18, True)
htxt = hf.render(f"v5 card  —  {SID}  —  original vs locked v5 design", True, (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2, MARGIN + (HDR_H - htxt.get_height()) // 2))

panel_y   = MARGIN + HDR_H
lbl_font  = hud_font(13, False)
lbl_font2 = hud_font(10, False)

PANELS = [
    (render_original(), "ORIGINAL", "box=60  dome r=40  centred"),
    (render_v5(),       "v5 LOCKED", "box=84  dome r=56  item +5 lx  lozenge"),
]
for col, (surf, title, subtitle) in enumerate(PANELS):
    x = MARGIN + col * (PANEL_W + GAP)
    canvas.blit(surf, (x, panel_y))
    col_colour = (160, 156, 180) if col == 0 else (255, 230, 120)
    t1 = lbl_font.render(title, True, col_colour)
    t2 = lbl_font2.render(subtitle, True, (130, 126, 150))
    lbl_y = panel_y + PANEL_H + 6
    canvas.blit(t1, (x + (PANEL_W - t1.get_width()) // 2, lbl_y))
    canvas.blit(t2, (x + (PANEL_W - t2.get_width()) // 2, lbl_y + t1.get_height() + 2))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_card_v5_card_item", "final_r1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}×{canvas_h})")
