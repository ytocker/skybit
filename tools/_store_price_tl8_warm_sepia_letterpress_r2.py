"""Round-2 render for tl8 numeral concept: warm_sepia_letterpress.

Round 1's single (0, +1) shadow read as a DROP shadow (numeral floating above
paper). A letterpress deboss is a plate PRESSED INTO paper, so the depth cue is
flipped here: a dark stamp at (0, -2) is the shaded TOP wall of the groove and a
pale stamp at (0, +2) is the lit BOTTOM wall. Dark-top + lit-bottom is the
carved-in signature. Offsets are ±2 at SS=2 so each wall stays a solid 1px at
final 1x and doesn't dissolve into AA fringe. All three stamps share one mask
and weight; all fills are opaque BLEND_RGBA_MULT. Review sheet only — not wired
live.
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


def _price_glyph(text):
    for fs in (13, 12, 11, 10, 9, 8):
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
        if mask.get_width() <= 66:
            return mask
    return mask


def _deboss(face, mask, rect, ink, ink_sh, ink_hi):
    """Stamp one glyph as a pressed-in plate groove: dark top wall at (0, -2),
    lit bottom wall at (0, +2), then the ink face at rect. ±2 at SS=2 keeps each
    wall a solid 1px after the 2x->1x smoothscale; every fill is opaque so no
    partial alpha survives to soften the carve."""
    shadow = mask.copy()
    shadow.fill((*ink_sh, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(shadow, (rect.x, rect.y - 2))
    highlight = mask.copy()
    highlight.fill((*ink_hi, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(highlight, (rect.x, rect.y + 2))
    fill = mask.copy()
    fill.fill((*ink, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(fill, rect)


def _draw_price(face, text, center, affordable):
    """Letterpress deboss with a flipped depth cue: dark top wall + lit bottom
    wall around an opaque ink face, so the numeral reads as pressed INTO the
    paper rather than floating above it. Only value contrast and the ±2 walls
    survive the 2x->1x smoothscale — no gradients, halos, or 8-way rings."""
    cx = center[0]
    if affordable:
        ink = (58, 38, 22)
        ink_sh = (38, 24, 14)
        ink_hi = (210, 190, 150)
        rule_col = (160, 120, 40)
    else:
        ink = (70, 68, 80)
        ink_sh = (50, 48, 60)
        ink_hi = (160, 158, 170)
        rule_col = (96, 100, 116)

    # Coin token — small "G", pushed high but sitting under the grommet's clear
    # line. Same deboss recipe as the amount so both press into the same paper.
    cy_token = int(FACE_H * 0.40)
    coin_mask = sc._stamp_bold(sc._glyph_base("G", sc.font(8), 0), sc.m(1.0))
    coin_r = coin_mask.get_rect(center=(cx, cy_token))
    _deboss(face, coin_mask, coin_r, ink, ink_sh, ink_hi)

    # Amount line — the deboss face plus its dark-top / lit-bottom groove walls.
    amt_mask = _price_glyph(text)
    cy_amount = int(FACE_H * 0.62)
    amt_r = amt_mask.get_rect(center=(cx, cy_amount))
    _deboss(face, amt_mask, amt_r, ink, ink_sh, ink_hi)
    amt_h = amt_mask.get_height()

    # Ledger underline directly beneath the amount, sized to the amount block.
    rule_y = cy_amount + amt_h // 2 + sc.m(2)
    rule_w = min(amt_mask.get_width() + sc.m(4), FACE_W - sc.m(8))
    rule_h = max(1, sc.m(1))
    rule_x = FACE_W // 2 - rule_w // 2
    pygame.draw.rect(face, (*rule_col, 255), (rule_x, rule_y, rule_w, rule_h))


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
sheet.blit(fh.render("WARM-SEPIA-LETTERPRESS price tag — round 2", True, (240, 224, 180)),
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
out = "docs/store_price_tl8/warm_sepia_letterpress/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
