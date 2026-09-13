"""CORNER-SASH store-card price tag — round 2 exploration render.

Round-1 read: a corner ribbon pinned into the top-left corner — a diagonal fold
triangle opening into a HORIZONTAL end-tab whose price reads in upright numerals.
Round 2 lifts the price off the gold: numerals are stamped DARK so they carry the
contrast instead of relying on a gold-on-gold sheen. The coin disc is dropped —
even at the smallest legible size "3.5k" needs the whole 68px tab, so the numeral
owns the full width. The fold now draws OVER the tab so the squared left edge
tucks under it as one continuous ribbon, with a thickened, shadowed crease.
"""
import math
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


def _price_glyph(text, num_col):
    """Upright abbreviated numerals stamped in a DARK ink so they carry the
    contrast against the light tab. font(10) fills the 30px tab height crisply;
    a step down guards the widest abbreviation if a longer price ever appears.
    Returns (dark glyph, white top-lit copy) for the pressed-stamp keyline."""
    mask = sc._stamp_bold(sc._glyph_base(text, sc.font(10), 0), sc.m(0.8))
    if mask.get_width() > 52:
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(8), 0), sc.m(0.8))
    img = mask.copy()
    img.fill((*num_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    hi = mask.copy()
    hi.fill((255, 255, 255, 140), special_flags=pygame.BLEND_RGBA_MULT)
    return img, hi


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _abbr(text)

    if affordable:
        fold = (150, 96, 20)
        tab_stops = [(0.0, (252, 220, 120)), (1.0, (224, 176, 60))]
        tab_gamma = 1.04
        bevel_top, bevel_bot = (255, 240, 190), (80, 52, 12)
        crease_dark = (80, 52, 12)
        crease_hi = (255, 240, 200, 180)
        num_col = (60, 38, 10)           # dark espresso: ~5:1 on gold
    else:
        fold = (60, 64, 82)
        tab_stops = [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))]
        tab_gamma = 1.02
        bevel_top, bevel_bot = (214, 218, 232), (54, 58, 74)
        crease_dark = (38, 42, 58)
        crease_hi = (200, 210, 228, 160)
        num_col = (38, 42, 58)           # dark slate on pewter

    # 1. Horizontal end-tab drawn FIRST so the fold can lie over its squared
    #    left edge — the tab visibly slides under the corner fold. Pushed 3px
    #    left (x=23) so that overlap reads as a single continuous ribbon.
    surf.blit(_tab_body(tab_stops, tab_gamma), (23, 28))

    # 2. Tab bevel — bright top edge, dark bottom edge, lit right corner.
    pygame.draw.line(surf, bevel_top, (23, 28), (90, 28), 1)
    pygame.draw.line(surf, bevel_bot, (23, 58), (90, 58), 1)
    pygame.draw.arc(surf, bevel_top, pygame.Rect(91 - 2 * sc.m(4), 28,
                    2 * sc.m(4), 2 * sc.m(4)), 0.0, 1.571, 1)

    # 3. Upright dark price numerals, centred on the tab's clear right span
    #    (coin dropped — the widest abbreviation needs the full width to stay
    #    legible). A 1px white top-lit copy behind gives a pressed-stamp lip.
    glyph, glyph_hi = _price_glyph(text, num_col)
    r = glyph.get_rect(center=(54, 43))
    surf.blit(glyph_hi, (r.x, r.y - 1))
    surf.blit(glyph, r)

    # 4. Corner fold triangle ON TOP — the ribbon's darker underside pinning the
    #    top-left, gripping the tab's tucked edge.
    pygame.draw.polygon(surf, fold, [(12, 12), (42, 12), (12, 42)])

    # 5. Crease where the fold lies over the tab: a 2px dark seam (survives the
    #    2x->1x downscale) with a soft shadow spilling onto the tab and a bright
    #    catch-light lip. Alpha edges blit through a temp so they blend onto the
    #    opaque tab rather than punching translucent holes in it.
    p1, p2 = (26, 28), (12, 42)
    edge = pygame.Surface((100, 72), pygame.SRCALPHA)
    # soft shadow cast by the fold, offset into the tab (down-right of the seam)
    pygame.draw.line(edge, (0, 0, 0, 60), (p1[0] + 3, p1[1] + 3),
                     (p2[0] + 3, p2[1] + 3), 3)
    # bright lip riding the fold edge, one step inside the seam
    pygame.draw.line(edge, crease_hi, (p1[0] + 2, p1[1] + 2),
                     (p2[0] + 2, p2[1] + 2), 1)
    surf.blit(edge, (0, 0))
    pygame.draw.line(surf, crease_dark, p1, p2, 2)

    return pygame.Rect(23, 28, 68, 30)


sc.price_chip = my_price_chip


def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


# ── numeral-fit check (in the 2x author buffer) ─────────────────────────────────
for _t in ["1.1k", "3.5k", "2.5k", "10k", "500"]:
    _g, _ = _price_glyph(_t, (60, 38, 10))
    _rr = _g.get_rect(center=(54, 43))
    _corner_start = 91 - sc.m(4)          # where the right rounded corner begins
    _margin = _corner_start - _rr.right
    assert _margin >= 3, f"{_t}: only {_margin}px before corner (need >=3)"
print("numeral fit OK: all abbreviations clear the corner by >=3px")

# ── pixel verification ─────────────────────────────────────────────────────────
_va = render_card_1x("skin_mummy", True)
_vl = render_card_1x("skin_mummy", False)
bg = (8, 8, 20)
px, py = 30, 21
pa, pl = _va.get_at((px, py))[:3], _vl.get_at((px, py))[:3]
assert any(abs(pa[i] - bg[i]) > 40 for i in range(3)), f"no sash at ({px},{py}) aff: {pa}"
assert any(abs(pl[i] - bg[i]) > 40 for i in range(3)), f"no sash at ({px},{py}) locked: {pl}"
assert pa != pl, f"states identical at ({px},{py})"
_dark = None
for px2 in range(15, 45, 2):
    for py2 in range(15, 28, 2):
        col = _va.get_at((px2, py2))[:3]
        if col[0] < 130 and col[1] < 90 and col[2] < 40:
            _dark = (px2, py2, col)
            break
    if _dark:
        break
assert _dark, "no dark numeral pixel found in affordable state"
print(f"dark numeral at {_dark[:2]}: {_dark[2]}")
print(f"verify aff:{pa} lock:{pl} PASS")

# ── render sheet ────────────────────────────────────────────────────────────────
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
sheet.blit(fh.render("CORNER-SASH price tag — round 2", True, (240, 224, 180)), (PAD, PAD // 2))


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

out = "docs/store_price_tl2/corner-sash/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
