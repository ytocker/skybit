"""Round-2 render for tl7 numeral concept: rosette-seal.

Guilloché is now confined to an OUTER ANNULUS so the numeral reads on a
clean flat inner medallion — a notarial-seal disc rather than a texture
that swallows the digits. 24 low-contrast spokes whisper the radial print;
a positive dark numeral sits directly on the flat gold/grey centre for
maximum legibility; four sparkle glints mark the cardinal ring positions.
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
    """Guilloché rosette seal, annulus-confined: solid outer disc + 24
    low-contrast spokes and two rings in the OUTER ANNULUS only + a flat
    inner medallion carrying a positive dark numeral + four cardinal
    sparkle glints on the outer ring."""
    R_outer = sc.m(14)              # 28px — outer disc radius
    R_inner = int(R_outer * 0.52)   # ~15px — clean inner medallion radius
    cx, cy = center

    if affordable:
        disc_base      = (206, 158, 52)
        inner_disc_col = (186, 140, 44)
        spoke_col      = (188, 142, 42)   # within ~8% of disc_base — a whisper
        ring_col       = (90,  60, 14)
        num_col        = (62,  38,  8)    # dark charcoal-brown on gold (~5:1)
        glint_col      = (255, 248, 214)
    else:
        disc_base      = (132, 138, 158)
        inner_disc_col = (112, 118, 138)
        spoke_col      = (118, 124, 144)
        ring_col       = (58,  62,  80)
        num_col        = (38,  42,  56)   # dark blue-grey on grey (~4.5:1)
        glint_col      = (218, 222, 234)

    # Solid outer disc — fills everything inside R_outer
    pygame.draw.circle(face, disc_base, (cx, cy), R_outer)

    # 24 spokes (every 15°) in the annulus only, R_inner -> R_outer
    for a in range(0, 360, 15):
        th = math.radians(a)
        sx = cx + int(R_inner * math.cos(th))
        sy = cy + int(R_inner * math.sin(th))
        ex = cx + int(R_outer * math.cos(th))
        ey = cy + int(R_outer * math.sin(th))
        pygame.draw.line(face, spoke_col, (sx, sy), (ex, ey), max(1, sc.m(1)))

    # Two rings framing the annulus
    pygame.draw.circle(face, ring_col, (cx, cy), R_outer, width=max(1, sc.m(1)))
    pygame.draw.circle(face, ring_col, (cx, cy), int(R_outer * 0.72),
                       width=max(1, sc.m(1)))

    # Flat inner medallion — clean field for the numeral, thin framing ring
    pygame.draw.circle(face, inner_disc_col, (cx, cy), R_inner)
    pygame.draw.circle(face, ring_col, (cx, cy), R_inner, width=max(1, sc.m(1)))

    # Positive dark numeral, flat-filled to fit inside the inner medallion
    for fs in (13, 12, 11, 10, 9, 8):
        mask = sc._glyph_base(text, sc.font(fs), 0)
        if mask.get_width() <= R_inner * 2 - sc.m(4):
            break
    r_mask = mask.get_rect(center=(cx, cy))
    fill = mask.copy()
    fill.fill((*num_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(fill, r_mask)

    # Four-point sparkle glints at the cardinal outer-ring positions
    arm = max(3, sc.m(3))
    for gox, goy in ((R_outer, 0), (-R_outer, 0), (0, R_outer), (0, -R_outer)):
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
    _draw_price(face, text, (FACE_W // 2, int(FACE_H * 0.58)), affordable)
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
sheet.blit(fh.render("ROSETTE-SEAL price tag — round 2", True, (240, 224, 180)),
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
out = "docs/store_price_tl7/rosette_seal/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
