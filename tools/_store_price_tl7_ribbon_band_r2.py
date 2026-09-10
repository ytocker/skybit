"""Round-2 render for tl7 numeral concept: ribbon-band.

Full-face-width mahogany sash with cream numeral reversed out. The
swallowtail is a genuine CUT — transparent V-notches in the band surface
reveal the cream tag body behind it, rather than a dark triangle painted
on top (which read as a fold/shadow in r1). Deep red-brown mahogany lifts
the cream numeral contrast to ~5.5:1. One locked font size keeps the band
proportion identical across every price. Review sheet only.
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

# Notch depth is shared by the band cut AND the numeral's x-clamp, so the
# glyph can never spill into the swallowtail bite.
NOTCH_D = sc.m(5)

# The band proportion must stay constant across cards, so the font size is
# resolved ONCE against the widest realistic price and reused everywhere,
# rather than auto-fitting per price.
_LOCKED_FS = None


def _full(text):
    digits = ''.join(c for c in text if c.isdigit())
    return f"{int(digits):,}" if digits else text


def _max_glyph_w():
    return FACE_W - 2 * NOTCH_D - sc.m(4)


def _locked_fs():
    global _LOCKED_FS
    if _LOCKED_FS is not None:
        return _LOCKED_FS
    limit = _max_glyph_w()
    _LOCKED_FS = 9
    for fs in (10, 9):
        mask = sc._stamp_bold(sc._glyph_base("12,000", sc.font(fs), 0), sc.m(1.0))
        if mask.get_width() <= limit:
            _LOCKED_FS = fs
            break
    return _LOCKED_FS


def _price_glyph(text):
    return sc._stamp_bold(sc._glyph_base(text, sc.font(_locked_fs()), 0), sc.m(1.0))


def _draw_price(face, text, center, affordable):
    """Mahogany band bisecting the tag; cream numeral reversed out of it.

    The swallowtail is cut as transparent holes in a standalone band
    surface so the cream body shows through — that is what makes it read
    as a notched ribbon rather than a painted-on triangle.
    """
    cx, cy = center
    band_h = sc.m(12)
    band_y0 = cy - band_h // 2

    if affordable:
        band_stops = [(0.0, (114, 54, 40)), (1.0, (76, 32, 24))]
        sheen_col = (196, 118, 92, 80)
        num_col = (250, 244, 220)
        key_col = (52, 22, 16)
    else:
        band_stops = [(0.0, (90, 94, 110)), (1.0, (58, 62, 78))]
        sheen_col = (198, 202, 216, 64)
        num_col = (232, 236, 248)
        key_col = (34, 38, 52)

    # Band lives on its own SRCALPHA layer so the notches can be punched
    # out as fully transparent pixels (draw ops overwrite alpha, no blend).
    band_surf = pygame.Surface((FACE_W, band_h), pygame.SRCALPHA)
    band_surf.blit(sc.vgrad_stops(FACE_W, band_h, 0, band_stops, 255), (0, 0))

    # Soft top sheen for the satin-ribbon read, cut by the notches below.
    pygame.draw.line(band_surf, sheen_col, (NOTCH_D, sc.m(1)),
                     (FACE_W - NOTCH_D, sc.m(1)), max(1, sc.m(1)))

    band_cy = band_h // 2
    left_notch = [(0, 0), (NOTCH_D, band_cy), (0, band_h)]
    pygame.draw.polygon(band_surf, (0, 0, 0, 0), left_notch)
    right_notch = [(FACE_W, 0), (FACE_W - NOTCH_D, band_cy), (FACE_W, band_h)]
    pygame.draw.polygon(band_surf, (0, 0, 0, 0), right_notch)

    face.blit(band_surf, (0, band_y0))

    # Numeral: locked font, then clamped to the notch-free width and to
    # ~70% of the band height so it always sits contained inside the sash.
    mask = _price_glyph(text)
    mw, mh = mask.get_size()
    max_w = _max_glyph_w()
    target_h = int(band_h * 0.70)
    scale = min(max_w / mw, target_h / mh)
    mask = pygame.transform.smoothscale(mask, (max(1, int(mw * scale)),
                                               max(1, int(mh * scale))))
    r = mask.get_rect(center=(cx, band_y0 + band_h // 2))

    # Single bottom-right key for edge separation — 8-way keyline clogged
    # the narrow strokes once the card downscaled to 1x.
    kl = mask.copy()
    kl.fill((*key_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(kl, (r.x + 1, r.y + 1))

    img = mask.copy()
    img.fill((*num_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(img, r)


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
print(f"dark band pixel at {dark_hit[0]}: {dark_hit[1]}")

pa, pl = _va.get_at((20, 35))[:3], _vl.get_at((20, 35))[:3]
assert pa != pl, f"states identical: {pa}"
print(f"aff:{pa} lock:{pl} PASS (locked_fs={_locked_fs()})")

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
sheet.blit(fh.render("RIBBON-BAND price tag — round 2", True, (240, 224, 180)),
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
out = "docs/store_price_tl7/ribbon_band/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
