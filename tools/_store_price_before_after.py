"""Before/after comparison: Gold-Sovereign chip (before) vs brushwork hang-tag (after).

Four skins (mummy aff, mummy locked, kitsune aff, kitsune locked) rendered
side by side at 2× zoom so the price treatment reads clearly at review size.
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


def render_card(sid, affordable):
    """Render a 1× card using whatever sc.price_chip is currently wired."""
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset,
                       sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    card = pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))
    # Override affordability: the live chip reads balance; force the right state
    # by monkey-patching price_chip to use variant, then restore.
    return card


def render_card_forced(sid, affordable, chip_fn):
    """Render with a specific chip_fn that accepts affordable kwarg directly."""
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset,
                       sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    # Temporarily set price_chip to a wrapper that forces affordability
    def _forced(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
        return chip_fn(surf, cx, cy, text, h, variant=variant, affordable=affordable)
    old = sc.price_chip
    sc.price_chip = _forced
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=sc.PRICE_VARIANT)
    sc.price_chip = old
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def old_price_chip(surf, cx, cy, text, h, variant=1, affordable=True):
    """Gold-Sovereign price chip — the design replaced by the brushwork tag."""
    coin_d = int(h * 0.66)
    pad    = sc.m(13)
    gapc   = sc.m(8)
    f      = sc.font(h * 0.60 / sc.SS)
    nw     = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w      = pad + coin_d + gapc + nw + pad
    r      = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    rad    = h // 2
    if affordable:
        sc._dark_chip_body(surf, r, rad,
                           [(0.0, (26, 20, 32)), (1.0, (18, 14, 24))],
                           (10, 11, 22), (56, 52, 76), gloss=14, gamma=1.04)
        sc.bevel_rim(surf, r, rad, (120, 88, 28, 235), (230, 200, 130, 220), w=2)
        coin_rim = (180, 150, 60)
        tint_col = (200, 160, 40, 40)
    else:
        sc._dark_chip_body(surf, r, rad,
                           [(0.0, (14, 15, 28)), (1.0, (10, 11, 22))],
                           (10, 11, 22), (40, 38, 56), gloss=14, gamma=1.04)
        sc.bevel_rim(surf, r, rad, (80, 60, 18, 200), (170, 150, 100, 180), w=2)
        coin_rim = (120, 108, 78)
        tint_col = (70, 74, 84, 180)
    ccx = r.x + pad + coin_d // 2
    cr  = coin_d // 2
    sc.coin_glyph(surf, ccx, cy, cr, rim=coin_rim)
    tint = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
    pygame.draw.circle(tint, tint_col, (cr, cr), cr)
    surf.blit(tint, (ccx - cr, cy - cr))
    nx = r.x + pad + coin_d + gapc + nw // 2
    if affordable:
        mask = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(1.0))
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img = mask.copy()
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(img, img.get_rect(center=(nx, cy)))
    else:
        sc.plain_text(surf, text, f, (nx, cy), color=(150, 132, 92),
                      shadow_a=0, weight=sc.m(1.0))
    return r


new_price_chip = sc.price_chip

SKINS = [
    ("skin_mummy",   True,  "MUMMY aff"),
    ("skin_mummy",   False, "MUMMY locked"),
    ("skin_kitsune", True,  "KITSUNE aff"),
    ("skin_kitsune", False, "KITSUNE locked"),
]

before_cards = [(render_card_forced(sid, aff, old_price_chip), lbl)
                for sid, aff, lbl in SKINS]
after_cards  = [(render_card_forced(sid, aff, new_price_chip), lbl)
                for sid, aff, lbl in SKINS]

ZOOM = 2
CW = sc.CARD_W * ZOOM
CH = sc.CARD_H * ZOOM

BG       = (8, 8, 20)
PAD      = 20
GAP      = 12
COL_GAP  = 32
HEADER_H = 44
LABEL_H  = 22

col_w   = 4 * CW + 3 * GAP
sheet_w = PAD + col_w + COL_GAP + col_w + PAD
sheet_h = PAD + HEADER_H + CH + LABEL_H + PAD
sheet   = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh = hud_font(20)
fl = hud_font(13)

# Column headers
before_lbl = fh.render("BEFORE  —  Gold-Sovereign chip", True, (240, 200, 120))
after_lbl  = fh.render("AFTER  —  Brushwork hang-tag",   True, (190, 230, 170))
sheet.blit(before_lbl, (PAD, PAD // 2))
sheet.blit(after_lbl,  (PAD + col_w + COL_GAP, PAD // 2))

y0 = PAD + HEADER_H

def draw_row(cards, x0):
    x = x0
    for card, lbl in cards:
        zoomed = pygame.transform.smoothscale(card, (CW, CH))
        sheet.blit(zoomed, (x, y0))
        img = fl.render(lbl, True, (190, 196, 210))
        sheet.blit(img, (x + (CW - img.get_width()) // 2, y0 + CH + 4))
        x += CW + GAP

draw_row(before_cards, PAD)
draw_row(after_cards,  PAD + col_w + COL_GAP)

# Vertical divider
mid_x = PAD + col_w + COL_GAP // 2
pygame.draw.line(sheet, (40, 44, 64),
                 (mid_x, PAD), (mid_x, sheet_h - PAD), 1)

out = "docs/store_price_before_after.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
