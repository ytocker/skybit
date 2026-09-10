"""Round-2 render for tl6 numeral concept: didone-contrast.

Simulates Didone thick/thin stroke modulation on the ships-only Bold sans:
vertical stems are fattened by compositing horizontal offsets of the glyph
mask, then a vertical erosion pass thins the horizontal cross-strokes so the
thick/thin contrast survives the 2x->1x downscale and actually reads. A darker
hairline keyline rings the numerals to reinforce the letterpress "plate".
Flat charcoal ink; no gradient, no shadow. Review sheet only — nothing here is
wired into the live store draw path.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import math
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

FACE_W, FACE_H = 68, 82
TILT = -7

# Horizontal fatten offset. At SS=2 this is +-4px in the buffer -> +-2px at 1x,
# which is the minimum that survives smoothscale as a readable Didone stem.
_OX = sc.m(2)


def _abbr(text):
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _thin_horizontals(fat):
    """Vertical erosion: short vertical runs are the horizontal cross-strokes,
    so drop their alpha. Combined with the horizontally-fattened stems this is
    what actually produces the Didone thick/thin split on a sans master."""
    w, h = fat.get_size()
    thin = sc.m(2.5)          # runs no taller than this read as a horizontal
    fat.lock()
    for x in range(w):
        col = [fat.get_at((x, y)) for y in range(h)]
        y = 0
        while y < h:
            if col[y].a > 40:
                y0 = y
                while y < h and col[y].a > 40:
                    y += 1
                if y - y0 <= thin:
                    for yy in range(y0, y):
                        c = col[yy]
                        fat.set_at((x, yy), (c.r, c.g, c.b, (c.a * 60) // 100))
            else:
                y += 1
    fat.unlock()


def _draw_price(face, text, center, affordable):
    """Fatten vertical stems (horizontal offset composite), then thin the
    horizontal cross-strokes so the thick/thin modulation is unmistakable at
    1x. Darker keyline rings the glyphs. Flat charcoal ink; no gradient."""
    ink = (52, 38, 30) if affordable else (58, 62, 74)
    key_ink = (30, 20, 14) if affordable else (36, 40, 50)

    # Pick the largest size whose FAT composite still clears the face: the
    # composite grows the glyph by 2*_OX, so leave ~sc.m(3) of side margin.
    limit = FACE_W - sc.m(3) - 2 * _OX
    for fs in (13, 12, 11, 10):
        base_mask = sc._glyph_base(text, sc.font(fs), 0)
        if base_mask.get_width() <= limit:
            break
    w, h = base_mask.get_size()

    fw = w + 2 * _OX
    fat = pygame.Surface((fw, h), pygame.SRCALPHA)
    for ox in (0, _OX, 2 * _OX):
        fat.blit(base_mask, (ox, 0))

    _thin_horizontals(fat)

    r = fat.get_rect(center=center)

    # Hairline keyline: the fat mask in a darker ink, offset one device px on
    # eight compass points, laid down first so the numerals read pressed-in.
    key = fat.copy()
    key.fill((*key_ink, 255), special_flags=pygame.BLEND_RGBA_MULT)
    kp = sc.m(1)
    for ang in range(0, 360, 45):
        dx = int(round(kp * math.cos(math.radians(ang))))
        dy = int(round(kp * math.sin(math.radians(ang))))
        face.blit(key, (r.x + dx, r.y + dy))

    fill = fat.copy()
    fill.fill((*ink, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(fill, r)


def _rot_point(px, py, center, angle_deg=TILT):
    th = math.radians(angle_deg)
    dx, dy = px - FACE_W / 2, py - FACE_H / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    return (center[0] + rx, center[1] + ry)


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _abbr(text)

    rad = sc.m(3)
    grommet = (28, 12)
    tag_center = (44, 60)

    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, FACE_W, FACE_H)

    if affordable:
        body = sc.vgrad_stops(FACE_W, FACE_H, rad,
                              [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                              255, gamma=1.04)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, rad, (80, 52, 12, 200),
                     (255, 240, 190, 200), max(2, sc.m(1)))
        ring_col = (110, 80, 30)
    else:
        body = sc.vgrad_stops(FACE_W, FACE_H, rad,
                              [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))],
                              255, gamma=1.02)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, rad, (54, 58, 74, 200),
                     (214, 218, 232, 200), max(2, sc.m(1)))
        ring_col = (60, 64, 80)

    _draw_price(face, text, (FACE_W // 2, int(FACE_H * 0.55)), affordable)

    pygame.draw.circle(face, (0, 0, 0, 0), grommet, sc.m(5))
    pygame.draw.circle(face, ring_col, grommet, sc.m(5) + 1,
                       width=max(1, sc.m(1)))

    rot = pygame.transform.rotate(face, TILT)

    cord = (190, 165, 115) if affordable else (155, 160, 175)

    gx, gy = _rot_point(*grommet, tag_center)
    knot = (22, 13)
    lw = sc.m(1.5)
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] - 1, knot[1] - 1), lw)
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] + 2, knot[1] + 2), lw)

    surf.blit(rot, rot.get_rect(center=tag_center))

    pygame.draw.circle(surf, cord, knot, sc.m(1.5))
    pygame.draw.circle(surf, (min(cord[0] + 30, 255), min(cord[1] + 30, 255),
                              min(cord[2] + 30, 255)), knot, max(1, sc.m(0.6)))


sc.price_chip = my_price_chip


def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


_va = render_card_1x("skin_mummy", True)
_vl = render_card_1x("skin_mummy", False)
bg = (8, 8, 20)

dark_hit = None
for px in range(14, 42, 2):
    for py in range(22, 44, 2):
        col = _va.get_at((px, py))[:3]
        if sum(col) < 350 and any(abs(col[i] - bg[i]) > 20 for i in range(3)):
            dark_hit = ((px, py), col)
            break
    if dark_hit:
        break
assert dark_hit, "no dark numeral pixel found on affordable face"
print(f"dark numeral at {dark_hit[0]}: {dark_hit[1]}")

pa, pl = _va.get_at((20, 35))[:3], _vl.get_at((20, 35))[:3]
assert pa != pl, f"states identical: {pa}"
print(f"aff:{pa} lock:{pl} PASS")

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
sheet.blit(fh.render("DIDONE-CONTRAST price tag — round 2", True, (240, 224, 180)),
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
out = "docs/store_price_tl6/didone_contrast/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
