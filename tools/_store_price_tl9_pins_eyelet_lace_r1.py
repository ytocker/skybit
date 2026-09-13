"""Round-1 render for tl9 pin concept: eyelet_lace.

A heavy brass annulus replaces the thin grommet — a wide ring reads as a
punched eyelet even at 1x. Two lace lines cross through the ring in a V and
converge on a dark iron tack below, so the tag reads as pinned to the card
rather than tied by a floppy cord. The amount is an axis_crush numeral: one
heavy pass horizontally crushed so the digits stay dense and legible at 5-8px
with no coin token and no comma. Review sheet only — not wired live.
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
    return str(int(digits)) if digits else text


def _price_glyph(text):
    for fs in (15, 14, 13, 12, 11, 10, 9, 8):
        raw = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
        crushed = pygame.transform.smoothscale(
            raw, (max(1, int(raw.get_width() * 0.86)), raw.get_height()))
        if crushed.get_width() <= 66:
            return crushed
    return crushed


def _draw_price(face, text, center, affordable):
    cx = center[0]
    ink = (40, 30, 26) if affordable else (40, 40, 52)
    rule_col = (56, 42, 30) if affordable else (40, 40, 52)

    amt_mask = _price_glyph(text)
    cy_amount = int(FACE_H * 0.52)
    amt_r = amt_mask.get_rect(center=(cx, cy_amount))
    amt_fill = amt_mask.copy()
    amt_fill.fill((*ink, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(amt_fill, amt_r)

    rule_y = cy_amount + amt_mask.get_height() // 2 + sc.m(2)
    rule_w = min(amt_mask.get_width() + sc.m(4), FACE_W - sc.m(8))
    rule_x = FACE_W // 2 - rule_w // 2
    peak_h = max(3, sc.m(3))
    min_h = max(1, sc.m(1))
    pygame.draw.polygon(face, rule_col, [
        (rule_x,          rule_y),
        (rule_x + rule_w, rule_y + (peak_h - min_h) // 2),
        (rule_x + rule_w, rule_y + (peak_h + min_h) // 2),
        (rule_x,          rule_y + peak_h),
    ])


def _rot_point(px, py, center, angle_deg=TILT):
    th = math.radians(angle_deg)
    dx, dy = px - FACE_W / 2, py - FACE_H / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _eyelet_lace(surf, tag_center, affordable):
    # Eyelet center = where grommet was, rotated into card canvas coords.
    ex, ey = _rot_point(28, 12, tag_center)
    ex, ey = int(ex), int(ey)

    outer_col = (160, 120, 40) if affordable else (110, 115, 128)
    # Inner punch approximates the tag body colour showing through the hole so
    # the annulus reads as a real punched eyelet rather than a painted disc.
    hole_col = (200, 195, 180) if affordable else (140, 145, 160)

    outer_r = sc.m(7)   # 14 device px
    inner_r = sc.m(5)   # 10 device px — band = 4 device px (meets sc.m(2) minimum)

    pygame.draw.circle(surf, outer_col, (ex, ey), outer_r)
    pygame.draw.circle(surf, hole_col, (ex, ey), inner_r)

    # Silver/brass highlight arc on the upper-left rim gives the ring volume.
    highlight = (220, 210, 165) if affordable else (180, 185, 200)
    hi_pts = [
        (ex + int(outer_r * math.cos(math.radians(225))),
         ey + int(outer_r * math.sin(math.radians(225)))),
        (ex + int((outer_r - 2) * math.cos(math.radians(225))),
         ey + int((outer_r - 2) * math.sin(math.radians(225)))),
        (ex + int((outer_r - 2) * math.cos(math.radians(200))),
         ey + int((outer_r - 2) * math.sin(math.radians(200)))),
        (ex + int(outer_r * math.cos(math.radians(200))),
         ey + int(outer_r * math.sin(math.radians(200)))),
    ]
    pygame.draw.polygon(surf, highlight, hi_pts)

    # Lace: a V that crosses through the eyelet and converges on the tack.
    tack_pos = (ex + sc.m(2), ey + sc.m(8))
    cord_col = (58, 48, 42) if affordable else (80, 84, 100)
    lw = sc.m(1)
    pygame.draw.line(surf, cord_col,
                     (ex - sc.m(3), ey - sc.m(3)),
                     tack_pos, lw)
    pygame.draw.line(surf, cord_col,
                     (ex + sc.m(3), ey - sc.m(3)),
                     tack_pos, lw)

    # Tack/nail: a small iron head over a short stem pins the lace to the card.
    iron = (80, 82, 90)
    pygame.draw.circle(surf, iron, tack_pos, sc.m(1.5))
    pygame.draw.line(surf, iron, tack_pos,
                     (tack_pos[0], tack_pos[1] + sc.m(3)), sc.m(1))


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _full(text)

    rad = sc.m(3)
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
    else:
        body = sc.vgrad_stops(FACE_W, FACE_H, rad,
                              [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))],
                              255, gamma=1.02)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, rad, (54, 58, 74, 200),
                     (214, 218, 232, 200), w=max(1, sc.m(1.2)))

    _draw_price(face, text, (FACE_W // 2, int(FACE_H * 0.58)), affordable)

    rot = pygame.transform.rotate(face, TILT)
    surf.blit(rot, rot.get_rect(center=tag_center))

    # Eyelet and lace drawn AFTER tag blit so the ring sits over the card edge.
    _eyelet_lace(surf, tag_center, affordable)


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
sheet.blit(fh.render("tl9 pins: eyelet_lace — round 1", True, (240, 224, 180)),
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
out = "docs/store_price_tl9_pins/eyelet_lace/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
