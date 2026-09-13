"""CORNER-SASH store-card price tag — round 1 exploration render.

A corner ribbon pinned into the card's top-left corner: a small diagonal fold
triangle anchors the ribbon "behind" the card, opening into a HORIZONTAL end-tab
whose price reads in fully upright numerals (never rotated). Drawn at fixed 2x
buffer coordinates in the top-left corner, so it ignores the bottom-centre chip
slot the stock price_chip is handed.
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


def _abbr(text):
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _tab_body(stops, gamma):
    """Warm/pewter gradient tab with ONLY the right corners rounded — the left
    edge is squared so it reads as tucking under the corner fold."""
    w, h, rad = 68, 30, sc.m(4)
    body = sc.vgrad_stops(w, h, 0, stops, 255, gamma).copy()
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_top_right_radius=rad, border_bottom_right_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return body


def _price_glyph(text, affordable):
    """Upright abbreviated numerals; poured gold gradient (affordable) or a flat
    readable pewter (locked). Shrinks a size step if the tab would overflow."""
    mask = sc._stamp_bold(sc._glyph_base(text, sc.font(11), 0), sc.m(0.8))
    if mask.get_width() > 46:
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(9), 0), sc.m(0.8))
    img = mask.copy()
    if affordable:
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img.fill((178, 184, 206, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return img


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _abbr(text)

    if affordable:
        fold = (150, 96, 20)
        tab_stops = [(0.0, (252, 220, 120)), (1.0, (224, 176, 60))]
        tab_gamma = 1.04
        bevel_top, bevel_bot = (255, 240, 190), (80, 52, 12)
        coin_col = (160, 100, 20)
    else:
        fold = (60, 64, 82)
        tab_stops = [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))]
        tab_gamma = 1.02
        bevel_top, bevel_bot = (214, 218, 232), (54, 58, 74)
        coin_col = (100, 104, 122)

    # 1. Corner fold triangle — the darker ribbon "back" pinning the top-left.
    pygame.draw.polygon(surf, fold, [(12, 12), (42, 12), (12, 42)])

    # 2. Horizontal end-tab — the readable price face.
    surf.blit(_tab_body(tab_stops, tab_gamma), (26, 28))

    # 3. Crease where the fold meets the tab: a 1px dark keyline with a 1px
    #    bright highlight one value-step inside it (not a gradient).
    pygame.draw.line(surf, bevel_bot, (26, 28), (42, 42), 1)
    pygame.draw.line(surf, bevel_top, (27, 28), (43, 42), 1)

    # 4a. Tab bevel — bright top edge, dark bottom edge, lit right corner.
    pygame.draw.line(surf, bevel_top, (26, 28), (93, 28), 1)
    pygame.draw.line(surf, bevel_bot, (26, 58), (93, 58), 1)
    pygame.draw.arc(surf, bevel_top, pygame.Rect(93 - 2 * sc.m(4), 28,
                    2 * sc.m(4), 2 * sc.m(4)), 0.0, 1.571, 1)

    # 4b. Flat coin disc left of the numerals.
    pygame.draw.circle(surf, coin_col, (34, 43), sc.m(4))

    # 4c. Upright price numerals, centred on the tab.
    glyph = _price_glyph(text, affordable)
    surf.blit(glyph, glyph.get_rect(center=(60, 43)))
    return pygame.Rect(26, 28, 68, 30)


sc.price_chip = my_price_chip


def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


# ── pixel verification ────────────────────────────────────────────────────────
_va = render_card_1x("skin_mummy", True)
_vl = render_card_1x("skin_mummy", False)
bg = (8, 8, 20)
px, py = 30, 21
pa, pl = _va.get_at((px, py))[:3], _vl.get_at((px, py))[:3]
assert any(abs(pa[i] - bg[i]) > 40 for i in range(3)), f"no sash at ({px},{py}) aff: {pa}"
assert any(abs(pl[i] - bg[i]) > 40 for i in range(3)), f"no sash at ({px},{py}) locked: {pl}"
assert pa != pl, f"states identical at ({px},{py})"
print(f"verify aff:{pa} lock:{pl} PASS")

# ── render sheet ──────────────────────────────────────────────────────────────
PAD, GAP, HEADER_H, LABEL_H = 20, 12, 40, 20
BG = (8, 8, 20)
row1 = [("skin_mummy", True, "MUMMY aff"), ("skin_mummy", False, "MUMMY locked"),
        ("skin_kitsune", True, "KITSUNE aff"), ("skin_kitsune", False, "KITSUNE locked")]
cards1 = [(render_card_1x(sid, aff), lbl) for sid, aff, lbl in row1]
crop_w, crop_h, zoom = 80, 100, 2
crops = [(pygame.transform.scale(_va.subsurface((0, 0, crop_w, crop_h)), (crop_w * zoom, crop_h * zoom)), "2x left aff"),
         (pygame.transform.scale(_vl.subsurface((0, 0, crop_w, crop_h)), (crop_w * zoom, crop_h * zoom)), "2x left locked")]
row1_w = 4 * sc.CARD_W + 3 * GAP
row2_w = 2 * crop_w * zoom + GAP
sheet_w = PAD * 2 + max(row1_w, row2_w)
sheet_h = PAD + HEADER_H + sc.CARD_H + LABEL_H + GAP + crop_h * zoom + LABEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)
fh = hud_font(22)
fl = hud_font(13)
sheet.blit(fh.render("CORNER-SASH price tag — round 1", True, (240, 224, 180)), (PAD, PAD // 2))


def _lbl(t, x, y, w):
    img = fl.render(t, True, (190, 196, 210))
    sheet.blit(img, (x + (w - img.get_width()) // 2, y))


y0 = PAD + HEADER_H
x = PAD
for card, lbl in cards1:
    sheet.blit(card, (x, y0))
    _lbl(lbl, x, y0 + sc.CARD_H + 3, sc.CARD_W)
    x += sc.CARD_W + GAP
y1 = y0 + sc.CARD_H + LABEL_H + GAP
x = PAD
for crop, lbl in crops:
    sheet.blit(crop, (x, y1))
    _lbl(lbl, x, y1 + crop_h * zoom + 3, crop_w * zoom)
    x += crop_w * zoom + GAP

out = "docs/store_price_tl2/corner-sash/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
