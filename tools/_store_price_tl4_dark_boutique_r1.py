"""dark-boutique tl4 hang-tag concept — round 1 render (Midnight Velvet Luxury Tag).

Standalone review harness: monkey-patches store_cards.price_chip with the
dark-boutique swing tag — a deep midnight-blue body with a gold grommet, gold
satin ribbon, and a champagne price sat over a gold underrule — then renders
mummy/kitsune cards in affordable + locked states and tiles them into
docs/store_price_tl4/dark_boutique/round_1.png. Exploration only; nothing here
is wired into the live store draw path.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import math as _math
import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()


def _abbr(text):
    """Prices climb into the thousands but a swing-tag face is narrow, so collapse
    long numbers to a compact `1.2k` style that stays legible after the 1x scale."""
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _rot_point(px, py, fw, fh, center, angle_deg):
    """Map a face-local point to world space after the tag is rotated about its
    own centre — lets the ribbon meet the grommet exactly where it emerges."""
    th = _math.radians(angle_deg)
    dx, dy = px - fw / 2, py - fh / 2
    rx = dx * _math.cos(th) + dy * _math.sin(th)
    ry = -dx * _math.sin(th) + dy * _math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _grommet(face, gx, gy, r_out, r_bore, r_void, col_metal, col_hi, col_shadow, col_bore):
    """Struck metal eyelet: a lit upper-left arc and a shaded lower-right arc give
    the ring dimension, then the bore is punched clear so the card body shows
    through the hanging hole the way a real grommet reads."""
    pygame.draw.circle(face, col_metal, (gx, gy), r_out)
    pts_hi = [(gx, gy)]
    for a in range(120, 221, 6):
        pts_hi.append((int(gx + r_out * _math.cos(_math.radians(a))),
                       int(gy + r_out * _math.sin(_math.radians(a)))))
    if len(pts_hi) >= 3:
        pygame.draw.polygon(face, col_hi, pts_hi)
    pts_sh = [(gx, gy)]
    for a in range(300, 401, 6):
        pts_sh.append((int(gx + r_out * _math.cos(_math.radians(a % 360))),
                       int(gy + r_out * _math.sin(_math.radians(a % 360)))))
    if len(pts_sh) >= 3:
        pygame.draw.polygon(face, col_shadow, pts_sh)
    pygame.draw.circle(face, col_metal, (gx, gy), r_out, max(1, sc.m(1.5)))
    pygame.draw.circle(face, col_bore, (gx, gy), r_bore)
    pygame.draw.circle(face, (*col_hi[:3], 120), (gx, gy), r_bore, 1)
    pygame.draw.circle(face, (0, 0, 0, 0), (gx, gy), r_void)


def _draw_price(face, text, center, col_key, col_fill_stops=None, col_fill_flat=None, fs=13):
    """Pour a flat or gradient fill into the numeral mask over an 8-point keyline
    halo so the champagne price stays readable against the dark velvet body."""
    mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
    r = mask.get_rect(center=center)
    key = mask.copy()
    key.fill((*col_key, 255), special_flags=pygame.BLEND_RGBA_MULT)
    p = sc.m(1)
    for ang in range(0, 360, 45):
        face.blit(key, (r.x + int(p * _math.cos(_math.radians(ang))),
                        r.y + int(p * _math.sin(_math.radians(ang)))))
    img = mask.copy()
    if col_fill_stops:
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0, col_fill_stops, 255, 1.0)
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img.fill((*col_fill_flat, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(img, r)
    return mask.get_rect(center=center)


FACE_W, FACE_H, TILT = 68, 82, -7


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Draw the dark-boutique swing tag at a fixed anchor in the 2x card buffer.
    Affordability is read from the variant (the store passes "locked" for
    gated/too-expensive cards); the wallet-derived `affordable` kwarg is absorbed
    and ignored so the exploration sheet can force both states deterministically."""
    affordable = (variant != "locked")
    text = _abbr(text)

    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, FACE_W, FACE_H)

    if affordable:
        body = sc.vgrad_stops(FACE_W, FACE_H, sc.m(3),
                              [(0.0, (14, 16, 42)), (1.0, (22, 26, 60))], 255, 1.04)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, sc.m(3), (34, 32, 60, 200), (60, 64, 110, 180),
                     w=max(1, sc.m(1.2)))
        pygame.draw.rect(face, (44, 48, 82), brect.inflate(-8, -8), 1, border_radius=sc.m(2))
        # gold coin-ring brand mark
        pygame.draw.circle(face, (188, 148, 48), (FACE_W // 2, 28), sc.m(4))
        pygame.draw.circle(face, (14, 16, 42), (FACE_W // 2, 28), sc.m(2.5))
        pygame.draw.circle(face, (188, 148, 48), (FACE_W // 2, 28), sc.m(4), 1)
        pygame.draw.line(face, (156, 122, 44), (4, 40), (FACE_W - 4, 40), max(1, sc.m(1)))
        _grommet(face, 28, 12, sc.m(5), sc.m(3), sc.m(2),
                 (196, 154, 50), (244, 216, 96), (62, 40, 8), (20, 14, 4))
        pygame.draw.circle(face, (255, 248, 200), (28 - sc.m(3), 12 - sc.m(3)), max(1, sc.m(1)))
        num_key, num_fill = (80, 64, 16), (242, 224, 176)
        underrule_col = (172, 136, 46)
        ribbon_col, ribbon_hi = (196, 154, 50), (240, 208, 90)
        knot_col, knot_hi = (196, 154, 50), (240, 208, 90)
    else:
        body = sc.vgrad_stops(FACE_W, FACE_H, sc.m(3),
                              [(0.0, (22, 24, 50)), (1.0, (16, 18, 38))], 255, 1.04)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, sc.m(3), (24, 22, 48, 200), (44, 48, 78, 160),
                     w=max(1, sc.m(1.2)))
        pygame.draw.rect(face, (36, 40, 70), brect.inflate(-8, -8), 1, border_radius=sc.m(2))
        pygame.draw.circle(face, (72, 76, 92), (FACE_W // 2, 28), sc.m(4))
        pygame.draw.circle(face, (22, 24, 50), (FACE_W // 2, 28), sc.m(2.5))
        pygame.draw.circle(face, (72, 76, 92), (FACE_W // 2, 28), sc.m(4), 1)
        pygame.draw.line(face, (80, 84, 100), (4, 40), (FACE_W - 4, 40), max(1, sc.m(1)))
        _grommet(face, 28, 12, sc.m(5), sc.m(3), sc.m(2),
                 (68, 72, 88), (110, 116, 134), (28, 30, 44), (18, 18, 28))
        pygame.draw.circle(face, (180, 184, 200), (28 - sc.m(3), 12 - sc.m(3)), max(1, sc.m(1)))
        num_key, num_fill = (48, 52, 74), (178, 182, 198)
        underrule_col = (80, 84, 100)
        ribbon_col, ribbon_hi = (152, 156, 168), (180, 184, 200)
        knot_col, knot_hi = (152, 156, 168), (180, 184, 200)

    # price numeral + gold underrule; measure the mask rect first so the rule
    # brackets the numerals rather than a fixed span.
    mask = sc._stamp_bold(sc._glyph_base(text, sc.font(13), 0), sc.m(1.0))
    nr = mask.get_rect(center=(FACE_W // 2, 56))
    _draw_price(face, text, (FACE_W // 2, 56), num_key, col_fill_flat=num_fill, fs=13)
    ul_y = nr.bottom + max(1, sc.m(2))
    ul_x0 = nr.left - max(1, sc.m(4))
    ul_x1 = nr.right + max(1, sc.m(4))
    pygame.draw.line(face, underrule_col, (ul_x0, ul_y), (ul_x1, ul_y), max(1, sc.m(1)))

    rot = pygame.transform.rotate(face, TILT)

    # satin ribbon runs from the grommet's world position up to the knot; drawn
    # under the tag so only the exposed length between hole and knot shows.
    gx, gy = _rot_point(28, 12, FACE_W, FACE_H, (44, 60), TILT)
    pygame.draw.line(surf, ribbon_col, (int(gx), int(gy)), (22, 13), max(2, sc.m(2)))
    pygame.draw.line(surf, ribbon_hi, (int(gx), int(gy)), (22, 13), max(1, sc.m(1)))

    surf.blit(rot, rot.get_rect(center=(44, 60)))

    pygame.draw.circle(surf, knot_col, (22, 13), max(1, sc.m(1.5)))
    pygame.draw.circle(surf, knot_hi, (22, 13), max(1, sc.m(0.8)))


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
va = render_card_1x("skin_mummy", True)
vl = render_card_1x("skin_mummy", False)
bg = (8, 8, 20)
found = any(any(abs(va.get_at((x, y))[i] - bg[i]) > 30 for i in range(3))
            for x in range(10, 30) for y in range(4, 18))
assert found, "grommet zone not detected"
assert va.get_at((18, 12))[:3] != vl.get_at((18, 12))[:3], "states identical"
print("verify PASS")

# ── render sheet ──────────────────────────────────────────────────────────────
PAD, GAP, HEADER_H, LABEL_H = 20, 12, 40, 20
BG = (8, 8, 20)
row1 = [("skin_mummy", True, "MUMMY aff"), ("skin_mummy", False, "MUMMY locked"),
        ("skin_kitsune", True, "KITSUNE aff"), ("skin_kitsune", False, "KITSUNE locked")]
cards1 = [(render_card_1x(sid, aff), lbl) for sid, aff, lbl in row1]

crop_w, crop_h, zoom = 80, 100, 2
crops = [(pygame.transform.scale(va.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x left aff"),
         (pygame.transform.scale(vl.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x left locked")]

row1_w = 4 * sc.CARD_W + 3 * GAP
row2_w = 2 * crop_w * zoom + GAP
sheet_w = PAD * 2 + max(row1_w, row2_w)
sheet_h = PAD + HEADER_H + sc.CARD_H + LABEL_H + GAP + crop_h * zoom + LABEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh = hud_font(22)
fl = hud_font(13)
sheet.blit(fh.render("DARK-BOUTIQUE — tl4 hang-tag round 1", True, (240, 224, 180)),
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

out = "docs/store_price_tl4/dark_boutique/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
