"""Round-1 exploration render for the `hang-tag` store-card price tag.

A classic apparel swing tag dangling from the card's top-left on a short
twisted string: cream/manila face when affordable, cool pewter when locked,
with a flat coin silhouette above-left of large horizontal price numerals.
Review sheet only — nothing here is wired into the live store draw path.
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
    """Prices climb into the thousands; a swing-tag face is narrow, so collapse
    long numbers to a compact `1.2k` style that still stays readable at 1x."""
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _price_glyph(text):
    """Faux-bold numeral master that auto-shrinks until it fits the tag face."""
    for fs in (12, 11, 10, 9, 8, 7):
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(0.8))
        if mask.get_width() <= 44:
            return mask
    return mask


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Draw the hang-tag at a fixed anchor in the 2x card buffer. Affordability
    is read from the variant (the store passes "locked" for gated/too-expensive
    cards); the wallet-derived `affordable` kwarg is absorbed and ignored so the
    exploration sheet can force both states deterministically."""
    affordable = (variant != "locked")
    text = _abbr(text)

    face_w, face_h = 56, 82
    rad = sc.m(3)
    face = pygame.Surface((face_w, face_h), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, face_w, face_h)

    if affordable:
        body = sc.vgrad_stops(face_w, face_h, rad,
                              [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                              255, gamma=1.04)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, rad, (80, 52, 12, 200),
                     (255, 240, 190, 200), w=max(1, sc.m(1.2)))
        coin_col = (160, 100, 20)
        ring_col = (110, 80, 30)
    else:
        body = sc.vgrad_stops(face_w, face_h, rad,
                              [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))],
                              255, gamma=1.02)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, rad, (54, 58, 74, 200),
                     (214, 218, 232, 200), w=max(1, sc.m(1.2)))
        coin_col = (100, 104, 122)
        ring_col = (60, 64, 80)

    # flat coin silhouette, above-left of the numerals
    pygame.draw.circle(face, coin_col, (22, 44), sc.m(6))

    # price numerals below the coin
    mask = _price_glyph(text)
    img = mask.copy()
    if affordable:
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        fill = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
        fill.fill((178, 184, 206, 255))
        img.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(img, img.get_rect(center=(30, 58)))

    # punch the hanging hole through the face, then rim it so it reads as a
    # grommet; over the card the hole shows the card body through it.
    pygame.draw.circle(face, (0, 0, 0, 0), (28, 10), sc.m(5))
    pygame.draw.circle(face, ring_col, (28, 10), sc.m(5) + 1,
                       width=max(1, sc.m(1)))

    rot = pygame.transform.rotate(face, -7)

    if affordable:
        cord = (140, 120, 80)
    else:
        cord = (110, 114, 130)

    # twisted string: two thin parallel strands from the grommet up to a knot
    # nub pinned at the card's top-left corner.
    lw = max(1, sc.m(0.8))
    pygame.draw.line(surf, cord, (36, 20), (20, 14), lw)
    pygame.draw.line(surf, cord, (34, 22), (18, 16), lw)

    # tag on top of the strands, its visual center hung just below the anchor
    surf.blit(rot, rot.get_rect(center=(44, 60)))

    # knot nub last so it caps the strands cleanly at the corner
    pygame.draw.circle(surf, cord, (20, 14), 2)


sc.price_chip = my_price_chip


def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


# ── pixel verification (run BEFORE saving the sheet) ──────────────────────────
_va = render_card_1x("skin_mummy", True)
_vl = render_card_1x("skin_mummy", False)
bg = (8, 8, 20)
for px, py in [(20, 35), (22, 50), (20, 60)]:
    pa, pl = _va.get_at((px, py))[:3], _vl.get_at((px, py))[:3]
    if any(abs(pa[i] - bg[i]) > 30 for i in range(3)):
        break
else:
    raise AssertionError("hang-tag face not detected in probed pixels")
assert pa != pl, f"affordable/locked identical at ({px},{py}): {pa}"
print(f"verify aff:{pa} lock:{pl} PASS")

# ── render sheet ──────────────────────────────────────────────────────────────
PAD, GAP, HEADER_H, LABEL_H = 20, 12, 40, 20
BG = (8, 8, 20)
row1 = [("skin_mummy", True, "MUMMY aff"), ("skin_mummy", False, "MUMMY locked"),
        ("skin_kitsune", True, "KITSUNE aff"), ("skin_kitsune", False, "KITSUNE locked")]
cards1 = [(render_card_1x(sid, aff), lbl) for sid, aff, lbl in row1]
crop_w, crop_h, zoom = 80, 100, 2
crops = [(pygame.transform.scale(_va.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x left aff"),
         (pygame.transform.scale(_vl.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x left locked")]
row1_w = 4 * sc.CARD_W + 3 * GAP
row2_w = 2 * crop_w * zoom + GAP
sheet_w = PAD * 2 + max(row1_w, row2_w)
sheet_h = PAD + HEADER_H + sc.CARD_H + LABEL_H + GAP + crop_h * zoom + LABEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)
fh = hud_font(22)
fl = hud_font(13)
sheet.blit(fh.render("HANG-TAG price tag — round 1", True, (240, 224, 180)),
           (PAD, PAD // 2))


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
out = "docs/store_price_tl2/hang-tag/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
