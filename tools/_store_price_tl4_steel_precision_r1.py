"""tl4 price concept: STEEL-PRECISION — round 1.

An industrial brushed-steel hang-tag price fob. The body is a warm brushed
steel with a 3-row micro-banding that reads as a machined finish, an
extra-large chrome grommet punched through the top, and a distinct darker
nameplate panel that seats the bright white price so the numeral holds even on
a busy card. The tag hangs at a slight -5deg tilt off a woven cord + knot so it
reads as a physical price fob, not an upright system chip. LOCKED swaps the
whole fob to a colder blue-steel (bluer body, greyer numeral) so "can't afford"
reads at a glance without a separate badge.

The concept is delivered by monkey-patching sc.price_chip so the real
sc.draw_card composites the fob in the state-chip lane; everything below the
`sc.price_chip = my_price_chip` line is the review sheet.

Output: docs/store_price_tl4/steel_precision/round_1.png
"""
import os
import sys
import math as _math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font
sd.load()


def _abbr(text):
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _rot_point(px, py, fw, fh, center, angle_deg):
    # Map a face-local point through the same rotate-about-centre transform the
    # tag surface undergoes, so the cord anchors to the grommet after tilt.
    th = _math.radians(angle_deg)
    dx, dy = px - fw / 2, py - fh / 2
    rx = dx * _math.cos(th) + dy * _math.sin(th)
    ry = -dx * _math.sin(th) + dy * _math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _cord(surf, p0, p1, col_a, col_b, seg_dp, lw):
    # Alternating two-tone segments fake a woven/twisted cord without per-strand
    # geometry.
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = max(1, int(_math.hypot(dx, dy) / seg_dp))
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        x0, y0 = p0[0] + dx * t0, p0[1] + dy * t0
        x1, y1 = p0[0] + dx * t1, p0[1] + dy * t1
        pygame.draw.line(surf, col_a if i % 2 == 0 else col_b,
                         (int(x0), int(y0)), (int(x1), int(y1)), lw)


def _draw_price(face, text, center, col_key, col_fill_flat, fs=13):
    # 8-way keyline halo behind a flat fill keeps the numeral crisp against the
    # brushed-steel nameplate at 1x.
    mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
    r = mask.get_rect(center=center)
    key = mask.copy()
    key.fill((*col_key, 255), special_flags=pygame.BLEND_RGBA_MULT)
    p = sc.m(1)
    for ang in range(0, 360, 45):
        face.blit(key, (r.x + int(p * _math.cos(_math.radians(ang))),
                        r.y + int(p * _math.sin(_math.radians(ang)))))
    img = mask.copy()
    img.fill((*col_fill_flat, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(img, r)


FACE_W, FACE_H = 68, 82
TILT = -5


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT,
                  affordable=True, **kw):
    # The "locked" variant string forces the cool fob regardless of wallet so
    # the review sheet can render both states side by side.
    affordable = (variant != "locked")
    text = _abbr(text)

    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    rad = sc.m(3)
    for y in range(FACE_H):
        t = y / max(1, FACE_H - 1)
        if affordable:
            # warm steel top->bottom
            base_r = int(148 - t * 44)
            base_g = int(152 - t * 46)
            base_b = int(162 - t * 52)
        else:
            # cooler, bluer steel that reads as "unavailable"
            base_r = int(108 - t * 44)
            base_g = int(114 - t * 46)
            base_b = int(128 - t * 52)
        # 3-row banding: groups of 3 rows, two lighter then one darker, for a
        # machined brushed-finish read.
        band = 6 if (y % 3) < 2 else -8
        r = max(0, min(255, base_r + band))
        g = max(0, min(255, base_g + band))
        b = max(0, min(255, base_b + band))
        pygame.draw.line(face, (r, g, b), (0, y), (FACE_W - 1, y))
    # rounded-rect clip
    msk = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.rect(msk, (255, 255, 255, 255), (0, 0, FACE_W, FACE_H),
                     border_radius=rad)
    face.blit(msk, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    if affordable:
        bevel_deep, bevel_bright = (56, 60, 72, 200), (200, 208, 218, 200)
        inner_border = (180, 186, 200)
        g_main, g_hi, g_lo = (158, 164, 176), (218, 224, 236), (56, 60, 72)
        g_bore = (18, 18, 22)
        g_rim = (200, 208, 220, 120)
        plate = (106, 110, 122)
        price_key, price_fill = (28, 28, 34), (252, 252, 255)
        cord_a, cord_b = (44, 40, 38), (72, 68, 66)
        knot_col = (56, 52, 50)
    else:
        bevel_deep, bevel_bright = (44, 48, 60, 200), (180, 186, 200, 180)
        inner_border = (148, 152, 168)
        g_main, g_hi, g_lo = (130, 136, 148), (188, 194, 208), (40, 44, 56)
        g_bore = (12, 12, 18)
        g_rim = (170, 176, 192, 100)
        plate = (82, 86, 98)
        price_key, price_fill = (16, 16, 20), (186, 190, 208)
        cord_a, cord_b = (100, 96, 94), (72, 70, 68)
        knot_col = (72, 70, 68)

    # bevel emboss + a crisp inner border for the machined-plate edge.
    sc.bevel_rim(face, pygame.Rect(0, 0, FACE_W, FACE_H), sc.m(3),
                 bevel_deep, bevel_bright, w=max(1, sc.m(1.5)))
    pygame.draw.rect(face, inner_border,
                     pygame.Rect(0, 0, FACE_W, FACE_H).inflate(-6, -6), 1,
                     border_radius=sc.m(2))

    # extra-large chrome grommet punched through the top
    gx, gy = 28, 12
    r_out = sc.m(6)
    pygame.draw.circle(face, g_main, (gx, gy), r_out)
    # upper-left lit sector
    pts_hi = [(gx, gy)]
    for a in range(120, 221, 6):
        pts_hi.append((int(gx + r_out * _math.cos(_math.radians(a))),
                       int(gy + r_out * _math.sin(_math.radians(a)))))
    if len(pts_hi) >= 3:
        pygame.draw.polygon(face, g_hi, pts_hi)
    # lower-right shadow sector
    pts_sh = [(gx, gy)]
    for a in range(300, 401, 6):
        pts_sh.append((int(gx + r_out * _math.cos(_math.radians(a % 360))),
                       int(gy + r_out * _math.sin(_math.radians(a % 360)))))
    if len(pts_sh) >= 3:
        pygame.draw.polygon(face, g_lo, pts_sh)
    pygame.draw.circle(face, g_main, (gx, gy), r_out, max(1, sc.m(2)))
    pygame.draw.circle(face, g_bore, (gx, gy), sc.m(4))
    pygame.draw.circle(face, g_rim, (gx, gy), sc.m(4), 1)
    # punch a real transparent hole so the fob reads as physically pierced.
    pygame.draw.circle(face, (0, 0, 0, 0), (gx, gy), sc.m(2.5))

    # darker nameplate panel seats the numeral
    pygame.draw.rect(face, plate, pygame.Rect(4, 36, FACE_W - 8, 42),
                     border_radius=sc.m(2))
    _draw_price(face, text, (FACE_W // 2, 56), price_key, price_fill, fs=13)

    # tilt the whole fob, anchor the cord to the rotated grommet, seat it.
    rot = pygame.transform.rotate(face, TILT)
    gx2, gy2 = _rot_point(28, 12, FACE_W, FACE_H, (44, 60), TILT)
    _cord(surf, (gx2, gy2), (22, 13), cord_a, cord_b, sc.m(2), sc.m(1))
    surf.blit(rot, rot.get_rect(center=(44, 60)))
    pygame.draw.circle(surf, knot_col, (22, 13), max(1, sc.m(1.5)))
    return pygame.Rect(cx, cy, 0, 0)


sc.price_chip = my_price_chip


# ── render sheet ────────────────────────────────────────────────────────────
def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset,
                       sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def zoom_left(card_1x):
    crop = card_1x.subsurface((0, 0, 80, 100))
    return pygame.transform.scale(crop, (160, 200))


BG = (8, 8, 20)
PAD = 20
GAP = 12
HEADER_H = 40
LABEL_H = 20

CW, CH = sc.CARD_W, sc.CARD_H

cards = {
    "mummy_aff": render_card_1x("skin_mummy", True),
    "mummy_lck": render_card_1x("skin_mummy", False),
    "kitsune_aff": render_card_1x("skin_kitsune", True),
    "kitsune_lck": render_card_1x("skin_kitsune", False),
}

row1_h = CH
row2_h = 200
total_h = HEADER_H + LABEL_H + row1_h + GAP + row2_h + PAD
total_w = PAD + 4 * CW + 3 * GAP + PAD
canvas = pygame.Surface((total_w, total_h))
canvas.fill(BG)

hf = hud_font(9, True)
ht = hf.render("STEEL-PRECISION — tl4 hang-tag round 1", True, (255, 220, 80))
canvas.blit(ht, (total_w // 2 - ht.get_width() // 2,
                 (HEADER_H - ht.get_height()) // 2))

lf = hud_font(7)
labels = ["mummy aff", "mummy lck", "kitsune aff", "kitsune lck"]
card_list = [cards["mummy_aff"], cards["mummy_lck"],
             cards["kitsune_aff"], cards["kitsune_lck"]]

y1 = HEADER_H + LABEL_H
for i, (card, label) in enumerate(zip(card_list, labels)):
    x = PAD + i * (CW + GAP)
    lbl = lf.render(label, True, (160, 156, 180))
    canvas.blit(lbl, (x, HEADER_H + (LABEL_H - lbl.get_height()) // 2))
    canvas.blit(card, (x, y1))

y2 = y1 + row1_h + GAP
for i, (key, label) in enumerate([("mummy_aff", "mummy aff (2×crop)"),
                                  ("mummy_lck", "mummy lck (2×crop)")]):
    x = PAD + i * (160 + GAP)
    lbl = lf.render(label, True, (140, 136, 160))
    canvas.blit(lbl, (x, y2 - lf.get_height() - 2))
    canvas.blit(zoom_left(cards[key]), (x, y2))

out = "docs/store_price_tl4/steel_precision/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")


# ── pixel verification ───────────────────────────────────────────────────────
va = render_card_1x("skin_mummy", True)
vl = render_card_1x("skin_mummy", False)
bg = (8, 8, 20)
found = any(any(abs(va.get_at((x, y))[i] - bg[i]) > 30 for i in range(3))
            for x in range(10, 30) for y in range(4, 18))
assert found, "grommet zone not detected"
assert va.get_at((22, 30))[:3] != vl.get_at((22, 30))[:3], "states not distinct"
print("verify PASS")
