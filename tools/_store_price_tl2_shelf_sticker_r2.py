"""Round-2 refinement render for the SHELF-STICKER store-card price tag.

An adhesive shelf label stuck onto the top-left of the card. Round 2 makes the
peel unmistakable (a big lifted corner + a full drop shadow so the label reads as
sitting ON the card), gives the sticker a slight hand-applied tilt, and pushes
the locked-state numeral/kicker contrast. Authored on its own SRCALPHA
sub-surface (local coords) then rotated + blitted onto the 2x author buffer.
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
    digits = "".join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _solid_label(txt, font_obj, color, tracking=0):
    """Bold glyph mask flooded with one flat colour (kicker / grey numerals)."""
    base = sc._stamp_bold(sc._glyph_base(txt, font_obj, tracking), sc.m(0.8))
    img = base.copy()
    img.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    return img


def _gold_numerals(base):
    """Pour the coin-metal sovereign ramp into a white glyph mask (keeps alpha)."""
    img = base.copy()
    w, h = img.get_size()
    grad = sc.vgrad_stops(w, h, 0, sc._SOVEREIGN_NUM_STOPS, 255)
    img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return img


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    # Affordability is driven by the render variant (state_chip's wallet-based
    # `affordable` kwarg is swallowed by **kw) so both states are forced on-sheet.
    affordable = (variant != "locked")
    text = _abbr(text)

    # Sticker body is 80x46 authored at local (0,0). The sub-surface is padded so
    # the full drop shadow + peel can bleed past the body without clipping.
    sticker = pygame.Surface((88, 54), pygame.SRCALPHA)
    body = pygame.Rect(0, 0, 80, 46)
    rad = sc.m(4)

    if affordable:
        fill = sc.vgrad_stops(80, 46, rad,
                              [(0.0, (252, 244, 220)), (1.0, (228, 206, 158))],
                              255, gamma=1.04)
        rule_col = (160, 120, 50)
        kicker_col = (150, 96, 20, 255)
        under_col = (255, 240, 200)
        edge_hi = (255, 252, 236)
    else:
        fill = sc.vgrad_stops(80, 46, rad,
                              [(0.0, (120, 124, 142)), (1.0, (68, 72, 90))],
                              255, gamma=1.02)
        rule_col = (100, 106, 128)
        kicker_col = (140, 146, 168, 255)
        under_col = (206, 212, 228)
        edge_hi = (232, 236, 246)

    # Full-body drop shadow so the label reads as stuck ON the card, not printed
    # into it (offset down-right, ~35% black under the entire footprint).
    shadow = pygame.Surface((88, 54), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 90), pygame.Rect(3, 4, 80, 46),
                     border_radius=rad)
    sticker.blit(shadow, (0, 0))

    sticker.blit(fill, body.topleft)
    if affordable:
        sc.bevel_rim(sticker, body, rad, (80, 52, 12, 180), (255, 240, 190, 180),
                     w=max(1, sc.m(1)))
    else:
        sc.bevel_rim(sticker, body, rad, (54, 58, 74, 180), (214, 218, 232, 180),
                     w=max(1, sc.m(1)))

    # PRICE kicker (top) + a decisive 2px printed rule + big numerals. The kicker
    # carries tracking so it resolves as text (not a blob) once shrunk to 1x.
    kick = _solid_label("PRICE", sc.font(7), kicker_col, tracking=sc.m(1))
    sticker.blit(kick, (8, 6))
    pygame.draw.line(sticker, rule_col, (6, 19), (74, 19), max(2, sc.m(1)))

    # Numerals sit lower-left, clear of the peel corner; auto-shrink to stay in.
    for fs in (13, 11, 9):
        base = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(0.8))
        if base.get_width() <= 50:
            break
    numerals = _gold_numerals(base) if affordable else \
        _solid_label(text, sc.font(fs), (178, 184, 206, 255))
    nr = numerals.get_rect(center=(32, 33))
    sticker.blit(numerals, nr.topleft)

    # PEEL-CURL at the top-right corner, deliberately large (~24x24) so it can't
    # be missed: a shadow cast on the card, the lifted underside catching light,
    # and a bright highlight along the free fold edge.
    curl = [(56, 34), (80, 34), (80, 10)]
    curl_shadow = pygame.Surface((88, 54), pygame.SRCALPHA)
    pygame.draw.polygon(curl_shadow, (0, 0, 0, 80), [(x + 3, y + 3) for x, y in curl])
    sticker.blit(curl_shadow, (0, 0))
    pygame.draw.polygon(sticker, under_col, curl)
    pygame.draw.line(sticker, edge_hi, (56, 34), (80, 10), max(1, sc.m(1)))

    # A slight hand-applied tilt: rotate the whole sticker before placing it, and
    # re-centre so the expanded rotated surface stays where the body was authored.
    rotated = pygame.transform.rotate(sticker, -3)
    origin = (12, 12)  # where the un-rotated sub-surface top-left would land
    center = (origin[0] + sticker.get_width() // 2,
              origin[1] + sticker.get_height() // 2)
    surf.blit(rotated, rotated.get_rect(center=center).topleft)


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
px, py = 20, 16
pa, pl = _va.get_at((px, py))[:3], _vl.get_at((px, py))[:3]
assert any(abs(pa[i] - bg[i]) > 40 for i in range(3)), f"no sticker aff at ({px},{py}): {pa}"
assert any(abs(pl[i] - bg[i]) > 40 for i in range(3)), f"no sticker locked at ({px},{py}): {pl}"
assert pa != pl, f"states identical at ({px},{py})"
print(f"verify aff:{pa} lock:{pl} PASS")

# ── render sheet ──────────────────────────────────────────────────────────────
PAD, GAP, HEADER_H, LABEL_H = 20, 12, 40, 20
BG = (8, 8, 20)
row1 = [("skin_mummy", True, "MUMMY aff"), ("skin_mummy", False, "MUMMY locked"),
        ("skin_kitsune", True, "KITSUNE aff"), ("skin_kitsune", False, "KITSUNE locked")]
cards1 = [(render_card_1x(sid, aff), lbl) for sid, aff, lbl in row1]
crop_w, crop_h, zoom = 80, 100, 2
_va2 = render_card_1x("skin_mummy", True)
_vl2 = render_card_1x("skin_mummy", False)
crops = [(pygame.transform.scale(_va2.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x left aff"),
         (pygame.transform.scale(_vl2.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x left locked")]
row1_w = 4 * sc.CARD_W + 3 * GAP
row2_w = 2 * crop_w * zoom + GAP
sheet_w = PAD * 2 + max(row1_w, row2_w)
sheet_h = PAD + HEADER_H + sc.CARD_H + LABEL_H + GAP + crop_h * zoom + LABEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)
fh = hud_font(22)
fl = hud_font(13)
sheet.blit(fh.render("SHELF-STICKER price tag — round 2", True, (240, 224, 180)), (PAD, PAD // 2))


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

out = "docs/store_price_tl2/shelf-sticker/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
