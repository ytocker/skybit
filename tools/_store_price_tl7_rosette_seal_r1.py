"""Round-1 render for tl7 numeral concept: rosette-seal.

Guilloché radial disc behind the price: 40 spokes every 9°, 3 concentric
hairline rings, near-white numeral reversed out over the gold centre — like
a notarial seal or security-print watermark embossed on the tag face.
Four-point sparkle glints sit at the cardinal rim positions.
Review sheet only — nothing here is wired into the live store draw path.
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

FACE_W, FACE_H = 76, 88
TILT = -7


def _full(text):
    digits = ''.join(c for c in text if c.isdigit())
    return f"{int(digits):,}" if digits else text


def _rot_point(px, py, center, angle_deg=TILT):
    th = math.radians(angle_deg)
    dx, dy = px - FACE_W / 2, py - FACE_H / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _draw_price(face, text, center, affordable):
    """Guilloché rosette seal: solid disc base + 40 spokes every 9° +
    3 concentric hairline rings + reversed near-white numeral with dark
    keyline + four-point sparkle glints at the cardinal rim positions."""
    R = sc.m(16)
    cx, cy = center

    if affordable:
        disc_base   = (206, 158, 52)
        spoke_col   = (150, 104, 26)
        ring_col    = (90,  60, 14)
        num_col     = (250, 244, 220)
        key_col     = (56,  36,  8)
        glint_col   = (255, 248, 214)
    else:
        disc_base   = (132, 138, 158)
        spoke_col   = (90,  96, 116)
        ring_col    = (58,  62,  80)
        num_col     = (232, 236, 246)
        key_col     = (36,  40,  54)
        glint_col   = (220, 224, 238)

    # Solid disc base
    pygame.draw.circle(face, disc_base, (cx, cy), R)

    # 40 spokes (every 9°), slightly darker than base
    for a in range(0, 360, 9):
        th = math.radians(a)
        ex = cx + int(R * math.cos(th))
        ey = cy + int(R * math.sin(th))
        pygame.draw.line(face, spoke_col, (cx, cy), (ex, ey), max(1, sc.m(1)))

    # 3 concentric rings
    for frac in (1.0, 0.66, 0.34):
        r = max(2, int(R * frac))
        pygame.draw.circle(face, ring_col, (cx, cy), r, width=max(1, sc.m(1)))

    # Anchor dot at centre
    pygame.draw.circle(face, ring_col, (cx, cy), max(2, sc.m(2)))

    # Numeral — dark keyline first (8-compass), then near-white fill
    for fs in (13, 12, 11, 10, 9, 8):
        mask = sc._glyph_base(text, sc.font(fs), 0)
        if mask.get_width() <= 66:
            break
    r_mask = mask.get_rect(center=(cx, cy))
    key_layer = mask.copy()
    key_layer.fill((*key_col, 220), special_flags=pygame.BLEND_RGBA_MULT)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            face.blit(key_layer, (r_mask.x + dx, r_mask.y + dy))
    fill = mask.copy()
    fill.fill((*num_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(fill, r_mask)

    # Four-point sparkle glints at the cardinal outer-ring positions
    arm = max(3, sc.m(2))
    for gox, goy in ((R, 0), (-R, 0), (0, R), (0, -R)):
        gx, gy = cx + int(gox), cy + int(goy)
        pygame.draw.line(face, glint_col, (gx - arm, gy), (gx + arm, gy), 1)
        pygame.draw.line(face, glint_col, (gx, gy - arm), (gx, gy + arm), 1)


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _full(text)
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
                     (255, 240, 190, 200), w=max(1, sc.m(1.2)))
        ring_col = (110, 80, 30)
    else:
        body = sc.vgrad_stops(FACE_W, FACE_H, rad,
                              [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))],
                              255, gamma=1.02)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, rad, (54, 58, 74, 200),
                     (214, 218, 232, 200), w=max(1, sc.m(1.2)))
        ring_col = (60, 64, 80)
    _draw_price(face, text, (FACE_W // 2, int(FACE_H * 0.62)), affordable)
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
for _px in range(14, 42, 2):
    for _py in range(22, 44, 2):
        col = _va.get_at((_px, _py))[:3]
        if sum(col) < 350 and any(abs(col[i] - bg[i]) > 20 for i in range(3)):
            dark_hit = ((_px, _py), col)
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
sheet.blit(fh.render("ROSETTE-SEAL price tag — round 1", True, (240, 224, 180)),
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
out = "docs/store_price_tl7/rosette_seal/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
