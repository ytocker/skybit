"""Side-by-side comparison: BEFORE (brushwork) vs axis_crush, coin token removed.

Both tags re-centered so the price numeral sits in the middle of the face
without the 'G' token above it.
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


def _rot_point(px, py, center, angle_deg=TILT):
    th = math.radians(angle_deg)
    dx, dy = px - FACE_W / 2, py - FACE_H / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _tag_body(face, affordable):
    rad = sc.m(3)
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
    return ring_col


def _tag_finish(surf, face, affordable, ring_col, tag_center=(44, 60)):
    grommet = (28, 12)
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


def _wedge_rule(face, cx, rule_y, rule_w, affordable):
    rule_col = (56, 42, 30) if affordable else (40, 40, 52)
    rw = min(rule_w, FACE_W - sc.m(8))
    rx = cx - rw // 2
    ph = max(3, sc.m(3))
    mh = max(1, sc.m(1))
    pts = [
        (rx,      rule_y),
        (rx + rw, rule_y + (ph - mh) // 2),
        (rx + rw, rule_y + (ph + mh) // 2),
        (rx,      rule_y + ph),
    ]
    pygame.draw.polygon(face, rule_col, pts)


# ── BEFORE: brushwork (comma, bold stamp) — no coin ──────────────────────────

def _full_brushwork(text):
    digits = ''.join(c for c in text if c.isdigit())
    return f"{int(digits):,}" if digits else text


def _glyph_brushwork(text):
    for fs in (13, 12, 11, 10, 9, 8):
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.8))
        if mask.get_width() <= 66:
            return mask
    return mask


def price_chip_brushwork_nocoin(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _full_brushwork(text)
    ink = (40, 30, 26) if affordable else (40, 40, 52)

    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    ring_col = _tag_body(face, affordable)

    amt_mask = _glyph_brushwork(text)
    cy_amount = int(FACE_H * 0.52)   # centered without coin above
    amt_r = amt_mask.get_rect(center=(FACE_W // 2, cy_amount))
    amt_fill = amt_mask.copy()
    amt_fill.fill((*ink, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(amt_fill, amt_r)

    rule_y = cy_amount + amt_mask.get_height() // 2 + sc.m(2)
    _wedge_rule(face, FACE_W // 2, rule_y, amt_mask.get_width() + sc.m(4), affordable)

    _tag_finish(surf, face, affordable, ring_col)


# ── AXIS_CRUSH: no comma, 0.86 crush — no coin ───────────────────────────────

def _full_axis(text):
    digits = ''.join(c for c in text if c.isdigit())
    return str(int(digits)) if digits else text


def _glyph_axis(text):
    for fs in (15, 14, 13, 12, 11, 10, 9, 8):
        raw = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
        crushed = pygame.transform.smoothscale(
            raw, (max(1, int(raw.get_width() * 0.86)), raw.get_height()))
        if crushed.get_width() <= 66:
            return crushed
    return crushed


def price_chip_axis_nocoin(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _full_axis(text)
    ink = (40, 30, 26) if affordable else (40, 40, 52)

    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    ring_col = _tag_body(face, affordable)

    amt_mask = _glyph_axis(text)
    cy_amount = int(FACE_H * 0.52)   # centered without coin above
    amt_r = amt_mask.get_rect(center=(FACE_W // 2, cy_amount))
    amt_fill = amt_mask.copy()
    amt_fill.fill((*ink, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(amt_fill, amt_r)

    rule_y = cy_amount + amt_mask.get_height() // 2 + sc.m(2)
    _wedge_rule(face, FACE_W // 2, rule_y, amt_mask.get_width() + sc.m(4), affordable)

    _tag_finish(surf, face, affordable, ring_col)


# ── render helper ─────────────────────────────────────────────────────────────

def render_1x(chip_fn, sid, affordable=True):
    sc.price_chip = chip_fn
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


# ── layout ────────────────────────────────────────────────────────────────────

VARIANTS = [
    ("BEFORE\n(brushwork)", price_chip_brushwork_nocoin),
    ("axis_crush\n(no comma)", price_chip_axis_nocoin),
]

ZOOM = 3
CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
CW, CH = CARD_W * ZOOM, CARD_H * ZOOM

BG = (8, 8, 20)
PAD = 20
GAP = 16
HEADER_H = 40
LABEL_H = 24

sheet_w = PAD + len(VARIANTS) * CW + (len(VARIANTS) - 1) * GAP + PAD
sheet_h = PAD + HEADER_H + CH + LABEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh = hud_font(20)
fl = hud_font(14)
title = fh.render("no-coin comparison — tl9 (affordable, mummy, 3×)", True, (240, 224, 180))
sheet.blit(title, (PAD, PAD // 2))

x = PAD
for (label, chip_fn) in VARIANTS:
    card = render_1x(chip_fn, "skin_mummy", True)
    zoomed = pygame.transform.smoothscale(card, (CW, CH))
    sheet.blit(zoomed, (x, PAD + HEADER_H))

    # two-line label
    lines = label.split("\n")
    ly = PAD + HEADER_H + CH + 4
    for line in lines:
        img = fl.render(line, True, (190, 196, 210))
        sheet.blit(img, (x + (CW - img.get_width()) // 2, ly))
        ly += img.get_height() + 1

    x += CW + GAP

out = "docs/store_price_tl9/nocoin_compare.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
