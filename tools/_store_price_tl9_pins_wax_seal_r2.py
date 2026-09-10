"""Round-2 render for tl9 attachment concept: wax_seal.

Axis_crush numeral (no coin token, no thousands comma) fills the tag face at
uniform bold weight, horizontally compressed so tall four-figure amounts still
land at 5-8px. The grommet + cord + knot attachment is replaced with a pressed
wax seal at the tag's top-left corner. Round 2 answers the director: the blob is
sized to the full ~18px spec, built from 5 bold vertices with large asymmetric
jitter plus a hanging drip lobe so the irregular silhouette survives smoothscale
and never reads as the round eyelet disc. Embossing now reads via a light catch
(a lit highlight dot) rather than a deeper-dark star, and the inner depression is
shifted down-right so a thin lit lip appears at the top-left. A short cord stub
under the blob says the seal is holding the tag on. Review sheet only.
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
    """Axis_crush ledger: one heavy ink pass, horizontally compressed so the
    numeral keeps its height while narrowing enough for four figures to fit.
    No coin token — the amount alone owns the tag — with a wedge underline that
    tapers to a point so it reads as a finishing stroke, not a flat rule."""
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


def _wax_seal(surf, tag_center, affordable):
    """Pressed wax blob at the tag's top-left corner. Full-spec ~18px diameter
    from 5 bold vertices with large asymmetric jitter plus a hanging drip lobe,
    so the irregular silhouette survives smoothscale and never reads as the
    round eyelet disc. Embossing reads via a lit light-catch highlight, not a
    deeper-dark mark, and the inner depression is offset down-right so a thin
    lit lip appears at the top-left."""
    sx = tag_center[0] - 16
    sy = tag_center[1] - 22

    if affordable:
        outer_col = (126, 52, 82)
        inner_col = (88, 34, 58)
        lit_col   = (160, 90, 120)
        cord_col  = (58, 48, 42)
    else:
        outer_col = (96, 86, 132)
        inner_col = (66, 58, 96)
        lit_col   = (130, 118, 168)
        cord_col  = (80, 84, 100)

    # Cord stub — drawn first, under the seal, so only the nub past the blob
    # shows and reads as the tie holding the tag on.
    cord_end = (tag_center[0] - 24, tag_center[1] - 30)
    pygame.draw.line(surf, cord_col, (sx, sy), cord_end, sc.m(1))

    # Outer blob: 5 bold vertices + big asymmetric jitter so the irregular
    # silhouette survives the 2x down-scale instead of washing to a circle.
    nominal_r = sc.m(9)  # 18 device px -> ~9px final radius
    angles = [0, 72, 144, 216, 288]
    jitters = [6, -8, 5, -6, 7]  # device px
    outer_pts = []
    for i, ang in enumerate(angles):
        th = math.radians(ang - 20)  # slight rotation off cardinal
        r = nominal_r + jitters[i]
        outer_pts.append((int(sx + r * math.cos(th)),
                          int(sy + r * math.sin(th))))
    # Drip lobe pulled down-right — the key move that keeps the blob clearly
    # non-circular versus the eyelet disc.
    drip_th = math.radians(50)
    drip_r = nominal_r + sc.m(5)
    drip_pt = (int(sx + drip_r * math.cos(drip_th)),
               int(sy + drip_r * math.sin(drip_th)))
    outer_pts.insert(1, drip_pt)
    pygame.draw.polygon(surf, outer_col, outer_pts)

    # Inner depression — shifted down-right 2 device px so a thin lit lip of the
    # outer wax survives at the top-left, selling the pressed emboss.
    inner_r = sc.m(5)  # 10 device px
    inner_jitter = [3, -4, 3, -5, 4]
    inner_pts = []
    ox, oy = sx + 2, sy + 2
    for i, ang in enumerate(angles):
        th = math.radians(ang + 15)
        r = inner_r + inner_jitter[i]
        inner_pts.append((int(ox + r * math.cos(th)),
                          int(oy + r * math.sin(th))))
    pygame.draw.polygon(surf, inner_col, inner_pts)

    # Light catch at the top-left raised edge — real embossing reads via a lit
    # highlight, not a deeper-dark center mark (invisible at this final size).
    hi_pos = (int(sx - sc.m(2)), int(sy - sc.m(2)))
    pygame.draw.circle(surf, lit_col, hi_pos, sc.m(1.5))


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

    # Wax seal drawn AFTER tag blit
    _wax_seal(surf, tag_center, affordable)


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
sheet.blit(fh.render("tl9 pins: wax_seal — round 2", True, (240, 224, 180)),
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
out = "docs/store_price_tl9_pins/wax_seal/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
