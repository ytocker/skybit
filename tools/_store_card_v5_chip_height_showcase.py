"""Chip-height options: BEFORE vs 4 shorter variants.

The chip height h is passed as a single argument to price_chip_split_cream;
everything inside (coin diameter, font size, pill radius, bounding rect) scales
from it automatically. Options trim equally from top and bottom by reducing h.

Output: docs/store_card_v5_chip_height/showcase.png
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

SID    = "skin_mummy"
CARD_W = sc.CARD_W * sc.SS   # 324
_INSET = sc._INSET

docs_dir = os.path.join(os.path.dirname(__file__), "..",
                        "docs", "store_card_v5_chip_height")


# ── split-cream chip (verbatim from _store_card_v5_price_chip_r3_split_cream_r2) ──

def _gloss_corrected(surf, rect, radius, peak):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        a = int(peak * (1 - y / h) ** 2.4)
        pygame.draw.line(sweep, (a, a, a, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)


def dark_chip_body(surf, r, radius, stops, rim_dark, rim_bright_3tup, gloss=12, gamma=1.04):
    sc.drop_shadow(surf, r, radius, blur=sc.m(4), alpha=110, dy=sc.m(2))
    surf.blit(sc.vgrad_stops(r.w, r.h, radius, stops, 255, gamma=gamma), r.topleft)
    _gloss_corrected(surf, r, radius, peak=gloss)
    sc.contact_shadow(surf, r, radius, sc.m(3), alpha=80)
    pygame.draw.rect(surf, rim_dark, r, width=max(1, sc.m(1.6)), border_radius=radius)
    sc.bevel_rim(surf, r, radius, rim_dark, (*rim_bright_3tup, 235), w=max(1, sc.m(1.5)))


def price_chip_split_cream(surf, cx, cy, text, h, affordable=True):
    coin_d = int(h * 0.66)
    pad    = sc.m(13)
    gapc   = sc.m(8)
    f      = sc.font(h * 0.62 / sc.SS)
    nw     = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w      = pad + coin_d + gapc + nw + pad
    rad    = h // 2
    r      = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    if affordable:
        dark_chip_body(surf, r, rad, [(0.0, (12, 13, 22)), (1.0, (34, 37, 56))],
                       (8, 10, 20), (60, 65, 100), gloss=12, gamma=1.04)
        coin_rim  = (180, 150, 60)
        cool_coin = None
        rim_a     = 150
    else:
        dark_chip_body(surf, r, rad, [(0.0, (10, 11, 20)), (1.0, (26, 28, 44))],
                       (8, 10, 20), (60, 65, 100), gloss=12, gamma=1.04)
        coin_rim  = (120, 110, 80)
        cool_coin = (70, 74, 84, 180)
        rim_a     = 80
    rim_surf = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
    pygame.draw.rect(rim_surf, (220, 170, 60, rim_a), rim_surf.get_rect(),
                     width=max(1, sc.m(1)), border_radius=rad)
    surf.blit(rim_surf, r.topleft)
    x   = r.x + pad
    ccx = x + coin_d // 2
    sc.coin_glyph(surf, ccx, cy, coin_d // 2, rim=coin_rim)
    if cool_coin is not None:
        cr   = coin_d // 2
        tint = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(tint, cool_coin, (cr, cr), cr)
        surf.blit(tint, (ccx - cr, cy - cr))
    x  += coin_d + gapc
    nx  = x + nw // 2
    if affordable:
        mask = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(1.0))
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              [(0.0, (255, 244, 196)), (0.48, (250, 228, 148)),
                               (0.52, (224, 164, 62)), (1.0, (210, 150, 60))],
                              255, 1.0)
        img = mask.copy()
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(img, img.get_rect(center=(nx, cy)))
    else:
        sc.plain_text(surf, text, f, (nx, cy), color=(150, 140, 110),
                      shadow_a=0, weight=sc.m(1.0))
    return r


def draw_card_split_cream(surf, sid, rect, affordable=True, chip_h=None):
    if chip_h is None:
        chip_h = sc.m(20)
    m   = sc.m
    pal = sc.RARITY[sc._rarity(sid)]
    rad = m(sc.CARD_RAD)
    sc.drop_shadow(surf, rect, rad, blur=m(8), alpha=160, dy=m(4))
    surf.blit(sc.vgrad(rect.w, rect.h, rad, sc.CARD_T, sc.CARD_B, 252, gamma=1.15),
              rect.topleft)
    sc.top_sheen(surf, rect, rad, m(30), peak=62)
    sc.contact_shadow(surf, rect, rad, m(9), alpha=120)
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(surf, rect, rad, sc.CARD_RING_DEEP, (*sc.CARD_RING_BRIGHT, 235),
                 w=max(1, m(2.0)))
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(surf, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(surf, (*sc.CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)
    cx, cy = rect.centerx, rect.y + m(sc.CY_DISC) + sc._DOME_DY
    sc.soft_glow(surf, cx, cy, sc._DOME_R + m(3), pal["glow"], 30, layers=8)
    sc.cabochon(surf, cx, cy, sc._DOME_R, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    name = sc._name(sid)
    sc.cabochon_glass(surf, cx, cy, sc._DOME_R, tint=pal["gem"])
    sc.blit_thumb(surf, sid, cx, cy - sc._ITEM_DY, sc._BOX_PX)
    sc.facet_gem(surf, rect.right - m(19), rect.y + m(19), m(sc.GEM_R + 3),
                 pal["gem"], pal["deep"], mystery=False)
    tier_word = sc._rarity(sid).upper()
    sc._ribbon_lozenge(surf, tier_word, cx, rect.y + m(55) - sc._RIBN_DY,
                       rect.w - m(34), pal)
    sc._name_on(surf, name, cx, rect.y + m(70), rect.w - m(26))
    price = f"{sc._cost(sid):,}"
    price_chip_split_cream(surf, cx, rect.y + m(88) - sc._CHIP_DY, price,
                           chip_h, affordable=affordable)


def render_card(chip_h_device):
    ch   = sc.CARD_H * sc.SS                          # 200, original card height for rect
    surf = pygame.Surface((CARD_W, ch + 16), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       CARD_W - 2 * sc.m(_INSET),
                       ch - 2 * sc.m(_INSET))         # rect.h=184, matches split-cream r2
    draw_card_split_cream(surf, SID, rect, affordable=True, chip_h=chip_h_device)
    return surf


# ── options ───────────────────────────────────────────────────────────────────
# (panel-id, sublabel, chip height in device px)
OPTIONS = [
    ("BEFORE", f"h={sc.m(20)}px (current)", sc.m(20)),
    ("A",      f"h={sc.m(19)}px (−1 each side)", sc.m(19)),
    ("B",      f"h={sc.m(18)}px (−2 each side)", sc.m(18)),
    ("C",      f"h={sc.m(17)}px (−3 each side)", sc.m(17)),
    ("D",      f"h={sc.m(16)}px (−4 each side)", sc.m(16)),
]

# ── layout ────────────────────────────────────────────────────────────────────
BG      = (8, 8, 20)
MARGIN  = 24
GAP     = 10
HDR_H   = 44
LBL_H   = 44
ch      = sc.CARD_H * sc.SS
PANEL_H = ch + 16  # 216

n        = len(OPTIONS)
canvas_w = MARGIN * 2 + CARD_W * n + GAP * (n - 1)
canvas_h = MARGIN + HDR_H + PANEL_H + LBL_H + MARGIN

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hf   = hud_font(18, True)
htxt = hf.render(
    f"v5 store card — chip height options ({SID})",
    True, (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

lbl_id  = hud_font(16, True)
lbl_sm  = hud_font(10, False)
panel_y = MARGIN + HDR_H

for col, (oid, sublabel, chip_h) in enumerate(OPTIONS):
    x    = MARGIN + col * (CARD_W + GAP)
    card = render_card(chip_h)
    canvas.blit(card, (x, panel_y))

    ly  = panel_y + PANEL_H + 4
    tid = lbl_id.render(oid, True, (255, 230, 120))
    canvas.blit(tid, (x + (CARD_W - tid.get_width()) // 2, ly))
    ly += tid.get_height() + 1

    t = lbl_sm.render(sublabel, True, (130, 126, 150))
    canvas.blit(t, (x + (CARD_W - t.get_width()) // 2, ly))

out = os.path.join(docs_dir, "showcase.png")
os.makedirs(docs_dir, exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}×{canvas_h})")
