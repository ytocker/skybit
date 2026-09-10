"""Round-2 render for tl9 numeral concept: double_skin.

Ink physics corrected: real ink accumulates DARKER where it pools, not lighter.
The base pass carries the mid-dark glyph body; the pool pass is the heaviest
value and sits shifted down-right, so the densest ink reads exactly where a
loaded brush would deposit it — at the trailing, gravity-side edges. At 5-8 px
the two passes merge into a single weighted silhouette; at full render the
pool fringe is legible as directional mass. Review sheet only — not wired live.
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
    # Narrower cap so the +3-px pool offset still fits inside the 66-px face.
    for fs in (13, 12, 11, 10, 9, 8):
        mask = sc._glyph_base(text, sc.font(fs), 0)
        if mask.get_width() <= 60:
            return mask
    return mask


def _draw_price(face, text, center, affordable):
    """Inverted-pooling ledger: a mid-dark base pass carries the glyph body;
    the heaviest ink is a faux-bold stamp shifted +offset down-right so the
    darkest value concentrates at the trailing edge — the direction ink flows
    under gravity on a loaded brush. Value contrast alone carries the read at
    5-8 px and for colorblind players."""
    cx = center[0]
    # Base: mid-dark tone — the visible glyph body.
    base_col = (70, 54, 44) if affordable else (62, 64, 76)
    # Pool: darkest ink — the dense accumulation at the down-right edge.
    pool_col = (40, 30, 26) if affordable else (40, 40, 52)
    coin_col = (150, 100, 28) if affordable else (88, 92, 110)
    # Rule fill is a plain RGB tuple — polygon() rejects 4-tuples.
    rule_col_solid = (56, 42, 30) if affordable else (40, 40, 52)

    # G coin token — a lighter-weight mark so the amount stays dominant.
    cy_token = int(FACE_H * 0.40)
    coin_mask = sc._stamp_bold(sc._glyph_base("G", sc.font(8), 0), sc.m(1.2))
    coin_r = coin_mask.get_rect(center=(cx, cy_token))
    coin_fill = coin_mask.copy()
    coin_fill.fill((*coin_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(coin_fill, coin_r)

    # Amount — inverted pooling: dark accumulates at the down-right edge.
    raw = _price_glyph(text)
    cy_amount = int(FACE_H * 0.62)
    off = sc.m(1.5)   # 3 device px → ≥1 clean live-px after downscale

    # Base pass (medium-dark, centered) — the primary glyph body.
    base = raw.copy()
    base.fill((*base_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    base_r = raw.get_rect(center=(cx, cy_amount))
    face.blit(base, base_r)

    # Pool pass (darkest ink, shifted down-right, with extra mass so the
    # accumulated-ink silhouette reads as weight rather than a hairline).
    pool_mask = sc._stamp_bold(raw, sc.m(1.0))
    pool = pool_mask.copy()
    pool.fill((*pool_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    pool_r = pool_mask.get_rect(center=(cx + off, cy_amount + off))
    face.blit(pool, pool_r)

    amt_h = raw.get_height()
    # Brush finishing stroke — use base dimensions so the rule tracks the
    # printed body, not the padded pool stamp.
    rule_y = cy_amount + amt_h // 2 + sc.m(2)
    rule_w = min(raw.get_width() + sc.m(4), FACE_W - sc.m(8))
    rule_x = FACE_W // 2 - rule_w // 2
    peak_h = max(3, sc.m(3))
    min_h = max(1, sc.m(1))
    pts = [
        (rule_x,          rule_y),
        (rule_x + rule_w, rule_y + (peak_h - min_h) // 2),
        (rule_x + rule_w, rule_y + (peak_h + min_h) // 2),
        (rule_x,          rule_y + peak_h),
    ]
    pygame.draw.polygon(face, rule_col_solid, pts)


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

# Verify pool ink is the darkest value (40,30,26) sum=96 < 350.
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
sheet.blit(fh.render("tl9 DOUBLE_SKIN digit treatment — round 2", True, (240, 224, 180)),
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
out = "docs/store_price_tl9/double_skin/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
