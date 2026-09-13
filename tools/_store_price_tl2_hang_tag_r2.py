"""Round-2 refinement render for the `hang-tag` store-card price tag.

A classic apparel swing tag dangling from the card's top-left on a short
twisted string. Round 2 answers the art-director notes: the coin blob is
gone so the price owns the face; affordable numerals are poured with a deep
sovereign-bronze ramp + dark keyline so they read strong on cream (no more
gold-on-cream wash-out); the face is widened for numeral room; and the string
now anchors on the grommet centre with fatter, lighter strands.
Review sheet only — nothing here is wired into the live store draw path.
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

# Deep sovereign-bronze numeral ramp (top->bottom). Bottom stops sit far below
# the cream body luminance so the numerals clear the >=2.5:1 contrast target
# that plain coin-gold missed.
NUM_STOPS_AFF = [
    (0.00, (230, 185, 80)),
    (0.33, (200, 155, 50)),
    (0.66, (140,  90, 20)),
    (1.00, (80,   48,  8)),
]
NUM_KEY_AFF = (80, 52, 12)
NUM_LOCK_FILL = (206, 212, 228)
NUM_KEY_LOCK = (48, 52, 66)

FACE_W, FACE_H = 68, 82          # widened from 56 into the unused top-left zone
TILT = -7                        # swing-tag lean; grommet math below tracks it


def _abbr(text):
    """Prices climb into the thousands; a swing-tag face is narrow, so collapse
    long numbers to a compact `1.2k` style that still stays readable at 1x."""
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _price_glyph(text):
    """Faux-bold numeral master at the largest size that still fits the widened
    face; the price is the focal element so it starts big and only shrinks when
    a wide value forces it."""
    for fs in (13, 12, 11, 10):
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
        if mask.get_width() <= 58:
            return mask
    return mask


def _draw_price(face, text, center, affordable):
    """Pour the price into the glyph mask, wrapped in a 1px keyline so the
    numerals stay crisp against the tag body in either state."""
    mask = _price_glyph(text)
    r = mask.get_rect(center=center)

    # keyline first: the bold mask stamped in the dark key colour around the
    # 8 compass points so the fill lands inside a clean dark contour.
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


def _rot_point(px, py, center, angle_deg=TILT):
    """Where a face-local point lands on the card buffer after the tag is
    rotated about its centre and blitted. Lets the string anchor exactly on the
    grommet instead of a hand-guessed offset (pygame angle is +CCW)."""
    th = math.radians(angle_deg)
    dx, dy = px - FACE_W / 2, py - FACE_H / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    return (center[0] + rx, center[1] + ry)


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Draw the hang-tag at a fixed anchor in the 2x card buffer. Affordability
    is read from the variant (the store passes "locked" for gated/too-expensive
    cards); the wallet-derived `affordable` kwarg is absorbed and ignored so the
    exploration sheet can force both states deterministically."""
    affordable = (variant != "locked")
    text = _abbr(text)

    rad = sc.m(3)
    grommet = (28, 12)                  # hole near the top, offset to the cord side
    tag_center = (44, 60)               # face visual centre on the card buffer

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

    # price owns the face: centred on the vertical mid, no coin, no dead band.
    _draw_price(face, text, (FACE_W // 2, int(FACE_H * 0.55)), affordable)

    # punch the hanging hole, then rim it so it reads as a grommet; over the
    # card the hole shows the card body — and the string — through it.
    pygame.draw.circle(face, (0, 0, 0, 0), grommet, sc.m(5))
    pygame.draw.circle(face, ring_col, grommet, sc.m(5) + 1,
                       width=max(1, sc.m(1)))

    rot = pygame.transform.rotate(face, TILT)

    cord = (190, 165, 115) if affordable else (155, 160, 175)

    # twisted string: two lighter, thicker strands whose bottoms land exactly on
    # the grommet centre and run up to a knot pinned near the card corner.
    gx, gy = _rot_point(*grommet, tag_center)
    knot = (22, 13)
    lw = sc.m(1.5)
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] - 1, knot[1] - 1), lw)
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] + 2, knot[1] + 2), lw)

    # tag over the strands so the cord reads as diving into the grommet hole.
    surf.blit(rot, rot.get_rect(center=tag_center))

    # knot nub last, capping the strands at the corner.
    pygame.draw.circle(surf, cord, knot, sc.m(1.5))
    pygame.draw.circle(surf, (min(cord[0] + 30, 255), min(cord[1] + 30, 255),
                              min(cord[2] + 30, 255)), knot, max(1, sc.m(0.6)))


sc.price_chip = my_price_chip


def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


# ── pixel verification (run BEFORE saving the sheet) ──────────────────────────
_va = render_card_1x("skin_mummy", True)
_vl = render_card_1x("skin_mummy", False)
bg = (8, 8, 20)

dark_hit = None
for px in range(14, 42, 2):
    for py in range(22, 44, 2):
        col = _va.get_at((px, py))[:3]
        if sum(col) < 350 and any(abs(col[i] - bg[i]) > 20 for i in range(3)):
            dark_hit = ((px, py), col)
            break
    if dark_hit:
        break
assert dark_hit, "no dark sovereign numeral pixel found on affordable face"
print(f"dark numeral at {dark_hit[0]}: {dark_hit[1]}")

pa, pl = _va.get_at((20, 35))[:3], _vl.get_at((20, 35))[:3]
assert pa != pl, f"states identical: {pa}"
print(f"aff:{pa} lock:{pl} PASS")

# ── render sheet ──────────────────────────────────────────────────────────────
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
sheet.blit(fh.render("HANG-TAG price tag — round 2", True, (240, 224, 180)),
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
out = "docs/store_price_tl2/hang-tag/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
