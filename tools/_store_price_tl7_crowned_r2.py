"""Round-2 render for tl7 numeral concept: crowned.

Unified three-peak polygon coronet above the price, darker bronze foil, and
open headroom between crown and numeral. Full comma-grouped digits.
Review sheet only — not wired into live draw path.
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

# Darker warm-bronze foil — pale tops washed out on the cream body, so the top
# stop now clears ~4.5:1 on (248,238,210) while keeping the top-to-dark sheen.
NUM_STOPS_AFF = [
    (0.00, (140,  98, 26)),
    (0.45, (124,  82, 20)),
    (1.00, (98,   62, 12)),
]
NUM_KEY_AFF = (80, 52, 12)
NUM_LOCK_FILL = (206, 212, 228)
NUM_KEY_LOCK = (48, 52, 66)


def _full(text):
    digits = ''.join(c for c in text if c.isdigit())
    return f"{int(digits):,}" if digits else text


def _price_glyph(text):
    for fs in (13, 12, 11, 10, 9, 8):
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
        if mask.get_width() <= 66:
            return mask
    return mask


def _pour_numeral(face, mask, r, affordable):
    """Keyline ring + gradient/flat fill on a glyph mask."""
    kcol = NUM_KEY_AFF if affordable else NUM_KEY_LOCK
    kl = mask.copy()
    kl.fill((*kcol, 255), special_flags=pygame.BLEND_RGBA_MULT)
    p = sc.m(1)
    for ang in range(0, 360, 45):
        dx = int(round(p * math.cos(math.radians(ang))))
        dy = int(round(p * math.sin(math.radians(ang))))
        face.blit(kl, (r.x + dx, r.y + dy))
    img = mask.copy()
    if affordable:
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              NUM_STOPS_AFF, 255, 1.0)
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        fill = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
        fill.fill((*NUM_LOCK_FILL, 255))
        img.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(img, r)


def _draw_price(face, text, center, affordable):
    """Crowned numeral: bronze/grey glyph beneath one fused 3-peak coronet."""
    cx = center[0]
    # Numeral sits lower so the crown gets clear headroom above it
    cy = int(FACE_H * 0.70)
    mask = _price_glyph(text)
    r = mask.get_rect(center=(cx, cy))
    _pour_numeral(face, mask, r, affordable)

    # Open a clean gap between crown base and the numeral's top edge
    numeral_top_y = r.top
    peak_base_y = numeral_top_y - sc.m(4) - sc.m(2)

    # One connected silhouette antialiases cleanly at 1x final size — single
    # fill + single 1px perimeter, no per-peak strokes to alias against.
    if affordable:
        crown_col = (214, 168, 64)
        outline_col = (110, 72, 14)
    else:
        # Grey-on-grey needs real contrast or the crown reads as a plain bar
        crown_col = (96, 104, 128)
        outline_col = (50, 54, 70)

    bar_h = max(2, sc.m(1.5))
    base_bottom = peak_base_y
    base_top = peak_base_y - bar_h

    center_peak_h = sc.m(10)
    flank_peak_h = int(center_peak_h * 0.6)

    l_peak = (cx - sc.m(7), base_top - flank_peak_h)
    c_peak = (cx,           base_top - center_peak_h)
    r_peak = (cx + sc.m(7), base_top - flank_peak_h)

    pts = [
        (cx - sc.m(11), base_bottom),
        (cx - sc.m(11), base_top),
        l_peak,
        (cx - sc.m(4),  base_top),
        c_peak,
        (cx + sc.m(4),  base_top),
        r_peak,
        (cx + sc.m(11), base_top),
        (cx + sc.m(11), base_bottom),
    ]
    pygame.draw.polygon(face, (*crown_col, 255), pts)
    pygame.draw.polygon(face, (*outline_col, 255), pts, 1)

    # Rounded finials cap the pointed tips; fill-matched, no extra stroke weight
    finial_r = max(2, sc.m(1.5))
    for tip in (l_peak, c_peak, r_peak):
        pygame.draw.circle(face, (*crown_col, 255), tip, finial_r)


def _rot_point(px, py, center, angle_deg=TILT):
    th = math.radians(angle_deg)
    dx, dy = px - FACE_W / 2, py - FACE_H / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    return (center[0] + rx, center[1] + ry)


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
    pygame.draw.circle(surf, (min(cord[0]+30,255), min(cord[1]+30,255),
                              min(cord[2]+30,255)), knot, max(1, sc.m(0.6)))


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
assert dark_hit, "no dark pixel found in tag zone"
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
sheet.blit(fh.render("CROWNED price tag — round 2", True, (240, 224, 180)),
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
out = "docs/store_price_tl7/crowned/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
