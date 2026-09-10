"""Round-2 render for the `rubber-stamp` tl6 numeral treatment.

Hand-stamped boutique label. All the distress that reads as a rubber stamp —
edge void nicks and the bleed halo — is now authored at 1x AFTER smoothscale,
because pixel-level work baked into the 2x supersample buffer was averaged away
by the downscale and left a plain bold numeral. The 2x pass keeps the ink flat
and crisp so there is a clean base to punch and bleed onto. The numeral itself
is canted relative to the tag frame so the stamp looks hand-applied.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import math
import random
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

FACE_W, FACE_H = 68, 82
TILT = -7

# Numeral zone on the 1x card (top-left hang tag). Distress is confined here.
_ZONE = (14, 36, 26, 44)  # x0, x1, y0, y1


def _abbr(text):
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _rot_point(px, py, center, angle_deg=TILT):
    th = math.radians(angle_deg)
    dx, dy = px - FACE_W / 2, py - FACE_H / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _draw_price(face, text, center, affordable):
    # Locked ink darkened for legible contrast against the grey tag body.
    ink = (38, 30, 24) if affordable else (52, 56, 72)
    for fs in (13, 12, 11, 10):
        mask = sc._glyph_base(text, sc.font(fs), 0)
        if mask.get_width() <= 58:
            break
    mw, mh = mask.get_size()
    pad = sc.m(4)
    pw, ph = mw + 2 * pad, mh + 2 * pad
    price_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
    mx, my = pad, pad

    # Flat, opaque ink — no halo/void here; the distress is applied post-scale.
    body = mask.copy()
    body.fill((*ink, 255), special_flags=pygame.BLEND_RGBA_MULT)
    price_surf.blit(body, (mx, my))

    # Cant the numeral clearly against the tag frame so it reads hand-stamped.
    price_rot = pygame.transform.rotate(price_surf, 6.0)
    face.blit(price_rot, price_rot.get_rect(center=center))


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
    pygame.draw.circle(surf, (min(cord[0]+30,255), min(cord[1]+30,255),
                              min(cord[2]+30,255)), knot, max(1, sc.m(0.6)))


sc.price_chip = my_price_chip


def _apply_stamp_distress(card1x, sid, affordable):
    """Post-smoothscale distress: 1px bleed halo + a few edge void nicks.

    Baked-in-at-2x distress is averaged out by the downscale, so it has to land
    on the final 1x pixels to survive and actually read.
    """
    ink = (38, 30, 24) if affordable else (52, 56, 72)
    x0, x1, y0, y1 = _ZONE
    x1 = min(x1, card1x.get_width() - 1)
    y1 = min(y1, card1x.get_height() - 1)
    rng = random.Random(hash(sid + str(affordable)) & 0xFFFFFFFF)

    def dark(x, y):
        c = card1x.get_at((x, y))
        return c[3] > 40 and (c[0] + c[1] + c[2]) < 350

    core = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if dark(x, y)]

    # Bleed halo — tint the light neighbours of the ink so the stamp looks wet.
    ha = 35 / 255.0
    touched = set()
    for (x, y) in core:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (nx, ny) in touched or (dx == 0 and dy == 0):
                    continue
                if not (x0 - 1 <= nx <= x1 and y0 - 1 <= ny <= y1):
                    continue
                c = card1x.get_at((nx, ny))
                if (c[0] + c[1] + c[2]) < 350:  # already ink — skip
                    continue
                nr = int(c[0] * (1 - ha) + ink[0] * ha)
                ng = int(c[1] * (1 - ha) + ink[1] * ha)
                nb = int(c[2] * (1 - ha) + ink[2] * ha)
                card1x.set_at((nx, ny), (nr, ng, nb, c[3]))
                touched.add((nx, ny))

    # Void nicks — only where the stroke meets lighter pixels (its edge), so the
    # punches read as broken ink rather than salt-and-pepper noise.
    def edge(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                c = card1x.get_at((x + dx, y + dy))
                if (c[0] + c[1] + c[2]) >= 350:
                    return True
        return False

    edges = [(x, y) for (x, y) in core
             if x0 < x < x1 - 1 and y0 < y < y1 - 1 and edge(x, y)]
    rng.shuffle(edges)
    for (x, y) in edges[:rng.randint(3, 4)]:
        card1x.set_at((x, y), (0, 0, 0, 0))


def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    card1x = pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))
    _apply_stamp_distress(card1x, sid, affordable)
    return card1x


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
sheet.blit(fh.render("RUBBER-STAMP price tag — round 2", True, (240, 224, 180)),
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
out = "docs/store_price_tl6/rubber_stamp/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
