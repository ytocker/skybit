"""Round-2 render for tl7 numeral concept: engraved-tablet.

Recessed rounded plaque in the tag face; numeral pressed INTO it via true
intaglio lighting — near wall (up-left) in shadow, far wall (down-right)
catching light, dark recessed floor fill. Round-2 tightens the read:
much darker figure fill, flipped (intaglio) emboss polarity, a doubled
bevel offset that survives the downscale, and plaque padding so the
numeral has margins. Review sheet only — not wired into live draw path.
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


def _price_glyph(text, max_w):
    # Fit the figure inside the padded plaque interior, not the full face.
    for fs in (13, 12, 11, 10, 9, 8):
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
        if mask.get_width() <= max_w:
            return mask
    return mask


def _draw_price(face, text, center, affordable):
    """Inner plaque + three-pass intaglio numeral (near-wall shadow, far-wall
    highlight, dark recessed floor fill)."""
    # Plaque geometry
    pr = pygame.Rect(sc.m(6), sc.m(22), FACE_W - sc.m(12), FACE_H - sc.m(34))
    pr_rad = sc.m(2)

    # Padded interior — gives the numeral room to breathe against the rim.
    inner = pr.inflate(-sc.m(4), -sc.m(4))

    # Plaque fill — one step darker than body to read as recessed.
    # State differs only by plaque hue + figure value/lightness, never by
    # emboss polarity (unified intaglio for both).
    if affordable:
        plaque_stops = [(0.0, (214, 198, 158)), (1.0, (198, 178, 138))]
        shadow_col = (60, 38, 12)        # dark charcoal-brown near wall
        highlight_col = (236, 224, 194)  # bright near-cream far wall
        mid_col = (88, 56, 14)           # deep warm brown recessed floor
        rim_deep = (120, 88, 32, 200)
        rim_bright = (255, 242, 200, 150)
    else:
        plaque_stops = [(0.0, (120, 124, 142)), (1.0, (96, 100, 118))]
        shadow_col = (34, 38, 52)        # dark cool near wall
        highlight_col = (224, 230, 242)  # bright cool far wall
        mid_col = (64, 70, 88)           # deep cool grey-blue floor
        rim_deep = (54, 58, 74, 200)
        rim_bright = (200, 204, 218, 150)

    plaque_surf = sc.vgrad_stops(pr.width, pr.height, pr_rad, plaque_stops, 255)
    face.blit(plaque_surf, pr.topleft)

    # Inner AO on the plaque (reads as "sunken")
    sc.contact_shadow(face, pr, pr_rad, depth=sc.m(2), alpha=100)

    # Plaque rim — dark-dominant bevel (sunken look: dark wins, bright is subtle)
    sc.bevel_rim(face, pr, pr_rad, rim_deep, rim_bright, w=max(1, sc.m(1)))

    # Numeral: three-pass intaglio emboss, centered in the padded interior
    mask = _price_glyph(text, inner.width)
    r = mask.get_rect(center=inner.center)
    # Doubled offset (4px in this 2x face -> 2px at 1x) so both bevel walls
    # stay distinct through the smoothscale downsample.
    o = max(2, sc.m(2))

    # Pass 1: near-wall shadow shifted UP-LEFT (pressed-in look)
    sh = mask.copy()
    sh.fill((*shadow_col, 160), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(sh, (r.x - o, r.y - o))

    # Pass 2: far-wall highlight shifted DOWN-RIGHT (lit far side of the groove)
    hi = mask.copy()
    hi.fill((*highlight_col, 160), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(hi, (r.x + o, r.y + o))

    # Pass 3: dark recessed floor fill at center
    fill = mask.copy()
    fill.fill((*mid_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(fill, r)


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

    # Pass center param but _draw_price ignores it (uses plaque center)
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
sheet.blit(fh.render("ENGRAVED-TABLET price tag — round 2", True, (240, 224, 180)),
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
out = "docs/store_price_tl7/engraved_tablet/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
