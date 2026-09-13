"""Round-2 render for tl9 numeral concept: stroke_rects.

Same seven-segment topology as r1 but with structural fixes that address
every art-director note:

• Cells sized so "1,100" = 52 device-px — no pre-scale composite needed.
  The only downscale is the card's own 2×→1×, preserving all segment detail.
• WV=4 px, WH=2 px → 2:1 thick:thin at 2× scale; ~2 px / ~1 px at live size.
• Each segment extends 1 px into joints so corners close cleanly.
• Comma replaced with a solid 3×4 px block — visible mass at tag scale.
• '1' gets a humanist serif treatment (top crossbar + bottom foot) so it reads
  as a numeral, not a lone vertical bar.
• '2', '5', '6', '9' get a tiny diagonal-foot polygon so strokes lift like a
  flat brush instead of cutting off cleanly like an LCD segment.
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


# --- Stroke rect digit blueprints ---
# Cell: 10×16 device-px at 2× card scale. After the card's 2×→1× downscale
# each stem is ~2 px and each bar ~1 px, giving the 2:1 calligraphic ratio
# with no intermediate smoothscale blurring the segments.
_CELL_W, _CELL_H = 10, 16
_WV, _WH = 4, 2   # vertical stem width, horizontal bar height


def _seg_rects(cell_w=_CELL_W, cell_h=_CELL_H, wv=_WV, wh=_WH):
    mid = cell_h // 2
    # Each segment extends 1 px beyond its nominal boundary so corners close
    # fully — the notched gaps r1 had at T/TL, M/BL etc. are eliminated.
    return {
        'T':  (wv,        0,           cell_w - 2*wv, wh + 1),
        'TL': (0,         wh,          wv,            mid - wh + 1),
        'TR': (cell_w-wv, wh,          wv,            mid - wh + 1),
        'M':  (wv,        mid - 1,     cell_w - 2*wv, wh + 2),
        'BL': (0,         mid+wh-1,    wv,            cell_h - mid - 2*wh + 2),
        'BR': (cell_w-wv, mid+wh-1,    wv,            cell_h - mid - 2*wh + 2),
        'B':  (wv,        cell_h-wh-1, cell_w - 2*wv, wh + 1),
    }


_DIGIT_SEGS = {
    '0': ['T','TL','TR','BL','BR','B'],
    '1': [],        # handled in _draw_digit — serif treatment replaces bare stem
    '2': ['T','TR','M','BL','B'],
    '3': ['T','TR','M','BR','B'],
    '4': ['TL','TR','M','BR'],
    '5': ['T','TL','M','BR','B'],
    '6': ['T','TL','M','BL','BR','B'],
    '7': ['T','TR','BR'],
    '8': ['T','TL','TR','M','BL','BR','B'],
    '9': ['T','TL','TR','M','BR','B'],
}


def _diag_foot(surf, px, py, ink):
    """2×3 parallelogram at stroke-end — mimics a flat-brush 45° lift."""
    # Slants rightward-downward: left edge drops one row relative to right edge.
    pygame.draw.polygon(surf, ink, [
        (px,   py+1),
        (px+2, py),
        (px+3, py+2),
        (px+1, py+2),
    ])


def _draw_digit(surf, x, y, ch, ink):
    """Draw one character at (x, y) with humanist proportions.

    '1' uses explicit serif rects rather than the shared segment table — a
    lone right stem without top/bottom accents reads as 'l' at small sizes.
    Digits '2', '5', '6', '9' get a diagonal polygon at the stroke-end so the
    mark lifts rather than terminating with a clean rectangular cut.
    """
    segs = _seg_rects()

    if ch == '1':
        # Right stem: TR + BR
        for seg in ('TR', 'BR'):
            rx, ry, rw, rh = segs[seg]
            pygame.draw.rect(surf, ink, (x+rx, y+ry, rw, rh))
        # Top serif — 3 px left overhang identifies the numeral at tag scale
        pygame.draw.rect(surf, ink,
                         (x + _CELL_W - _WV - 3, y, _WV + 3, _WH))
        # Bottom foot — same width, flush with cell bottom
        pygame.draw.rect(surf, ink,
                         (x + _CELL_W - _WV - 3, y + _CELL_H - _WH, _WV + 3, _WH))

    elif ch == ',':
        # Solid 3×4 block below baseline — gives the comma visual mass at
        # live scale instead of the invisible 2 px tick that r1 produced.
        pygame.draw.rect(surf, ink, (x + 1, y + _CELL_H - 4, 3, 4))

    elif ch == '.':
        pygame.draw.rect(surf, ink, (x + 1, y + _CELL_H - 3, 2, 2))

    elif ch in _DIGIT_SEGS:
        for seg in _DIGIT_SEGS[ch]:
            rx, ry, rw, rh = segs[seg]
            if rw > 0 and rh > 0:
                pygame.draw.rect(surf, ink, (x+rx, y+ry, rw, rh))

        # Diagonal foot — converts the hard LCD termination into a calligraphic
        # brush-lift. Position varies per glyph to match where the stroke ends.
        if ch in ('2', '5'):
            # Right end of the bottom bar — where the descending stroke exits
            bx = x + _WV + (_CELL_W - 2*_WV)   # right edge of B segment
            by = y + _CELL_H - _WH - 1
            _diag_foot(surf, bx, by, ink)

        elif ch == '6':
            # Top-right opening — '6' has no TR, so the right end of T is open;
            # a foot here suggests the stroke's calligraphic entry from above.
            tx = x + _WV + (_CELL_W - 2*_WV)
            ty = y
            _diag_foot(surf, tx, ty, ink)

        elif ch == '9':
            # Bottom-right below BR — the descender tail of a handwritten '9'.
            bx = x + _CELL_W - _WV
            by = y + _CELL_H - _WH
            _diag_foot(surf, bx, by, ink)


def _price_rects(text, ink):
    """Render price text using procedural rect digits. Returns Surface.

    Cells are pre-sized so common prices fit under the 66 device-px cap with
    no intermediate smoothscale — the card's own 2×→1× is the only downscale,
    so every segment survives intact to the final pixel.
    """
    COMMA_W, GAP = 4, 2
    total_w = 0
    widths = []
    for ch in text:
        w = COMMA_W if ch in ',./' else _CELL_W
        widths.append(w)
        total_w += w
    total_w += GAP * (len(text) - 1)

    surf = pygame.Surface((total_w, _CELL_H), pygame.SRCALPHA)
    x = 0
    for ch, w in zip(text, widths):
        _draw_digit(surf, x, 0, ch, (*ink, 255))
        x += w + GAP

    # Only scale if an unusually long number genuinely overflows — nearest-
    # neighbour scale avoids the blurring that smoothscale caused at this size.
    if surf.get_width() > 66:
        scale = 66 / surf.get_width()
        surf = pygame.transform.scale(
            surf,
            (max(1, int(surf.get_width() * scale)), surf.get_height()))
    return surf


def _draw_price(face, text, center, affordable):
    """Stroke-rect ledger: the amount is built from filled rectangles on a
    seven-segment topology instead of a font mask — thick stems and thin bars
    give a flat-brush numeral. A burnt-copper 'G' token sits above it at
    lighter weight, and the underline is a brush finishing stroke: a filled
    polygon that tapers in height and flicks to a point at the right."""
    cx = center[0]
    ink = (40, 30, 26) if affordable else (40, 40, 52)
    # Burnt-copper token when affordable; a cool grey when locked keeps the two
    # states unmistakable on a glance.
    coin_col = (150, 100, 28) if affordable else (88, 92, 110)
    # Rule fill is a plain RGB tuple — polygon() rejects 4-tuples.
    rule_col_solid = (56, 42, 30) if affordable else (40, 40, 52)

    # Coin token — a 'G' stamp at lighter weight than the amount so the numeral
    # stays the dominant mark on the tag.
    cy_token = int(FACE_H * 0.40)
    coin_mask = sc._stamp_bold(sc._glyph_base("G", sc.font(8), 0), sc.m(1.2))
    coin_r = coin_mask.get_rect(center=(cx, cy_token))
    coin_fill = coin_mask.copy()
    coin_fill.fill((*coin_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(coin_fill, coin_r)

    # Amount — procedural rect digits, no font mask involved.
    amt_surf = _price_rects(text, ink)
    cy_amount = int(FACE_H * 0.62)
    amt_r = amt_surf.get_rect(center=(cx, cy_amount))
    face.blit(amt_surf, amt_r)
    amt_h = amt_surf.get_height()

    # Brush finishing stroke: a wedge that is tall at the left and tapers to a
    # near-point at the right, so the mark reads as the brush lifting and
    # flicking off the page rather than a flat rule.
    rule_y = cy_amount + amt_h // 2 + sc.m(2)
    rule_w = min(amt_surf.get_width() + sc.m(4), FACE_W - sc.m(8))
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
sheet.blit(fh.render("tl9 STROKE_RECTS digit treatment — round 2", True, (240, 224, 180)),
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
out = "docs/store_price_tl9/stroke_rects/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
