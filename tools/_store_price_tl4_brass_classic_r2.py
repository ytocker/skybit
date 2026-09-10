"""Round-2 render for the `brass-classic` tl4 store-card price tag.

A refined cream-boutique swing tag: the flat punched hole of earlier tiers is
upgraded to a proper three-layer brass eyelet (metal ring + lit/shadowed rims +
bore + void), the price sits inside a ruled cartouche panel so it reads as an
engraved plate, and the string is a twisted two-tone boutique cord. Locked
cards restate the whole tag in cold pewter so the affordability read survives
without relying on the numeral colour alone.

Round 2 addresses the art-director notes: a larger, fully-concentric grommet
with a deeper bore void, a darker engraved cartouche with an inner keyline, a
higher-contrast barber-pole cord, and a bigger 4-direction-keyed numeral so the
counters of "5" and "0" stay open.
Review sheet only — nothing here is wired into the live store draw path.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import math as _math
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

FACE_W, FACE_H = 68, 82
TILT = -7


def _grommet(face, gx, gy, r_out, r_bore, r_void, col_metal, col_hi, col_shadow, col_bore):
    """A raised brass eyelet reads as jewellery, not a stamped hole. The upper-
    left wedge catches light and the lower-right wedge sinks into shadow so the
    ring gains volume from a single fixed key light before the tag is tilted."""
    pygame.draw.circle(face, col_metal, (gx, gy), r_out)
    pts_hi = [(gx, gy)]
    for a in range(120, 221, 6):
        pts_hi.append((int(gx + r_out * _math.cos(_math.radians(a))),
                       int(gy + r_out * _math.sin(_math.radians(a)))))
    if len(pts_hi) >= 3:
        pygame.draw.polygon(face, col_hi, pts_hi)
    pts_sh = [(gx, gy)]
    for a in range(300, 401, 6):
        pts_sh.append((int(gx + r_out * _math.cos(_math.radians(a % 360))),
                       int(gy + r_out * _math.sin(_math.radians(a % 360)))))
    if len(pts_sh) >= 3:
        pygame.draw.polygon(face, col_shadow, pts_sh)
    pygame.draw.circle(face, col_metal, (gx, gy), r_out, max(1, sc.m(1.5)))
    pygame.draw.circle(face, col_bore, (gx, gy), r_bore)
    pygame.draw.circle(face, (*col_hi[:3], 120), (gx, gy), r_bore, 1)
    # A concentric inner bore ring drawn explicitly closes the annulus on the
    # +x side, where the lit-wedge overlay previously left the ring asymmetric.
    pygame.draw.circle(face, col_bore, (gx, gy), r_bore - 1, 1)
    pygame.draw.circle(face, (0, 0, 0, 0), (gx, gy), r_void)


def _cord(surf, p0, p1, col_a, col_b, seg_dp, lw):
    """Alternating light/dark segments along the run fake the barber-pole twist
    of a real boutique cord without per-strand geometry."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = max(1, int(_math.hypot(dx, dy) / seg_dp))
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        x0, y0 = p0[0] + dx * t0, p0[1] + dy * t0
        x1, y1 = p0[0] + dx * t1, p0[1] + dy * t1
        pygame.draw.line(surf, col_a if i % 2 == 0 else col_b,
                         (int(x0), int(y0)), (int(x1), int(y1)), lw)


def _rot_point(px, py, fw, fh, center, angle_deg):
    """Where a face-local point lands on the card buffer after the tag is
    rotated about its centre and blitted, so the cord anchors exactly on the
    grommet instead of a hand-guessed offset (pygame angle is +CCW)."""
    th = _math.radians(angle_deg)
    dx, dy = px - fw / 2, py - fh / 2
    rx = dx * _math.cos(th) + dy * _math.sin(th)
    ry = -dx * _math.sin(th) + dy * _math.cos(th)
    return (center[0] + rx, center[1] + ry)


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


def _draw_price(face, text, center, col_key, col_fill_stops=None, col_fill_flat=None, fs=15):
    """Pour the price into a faux-bold glyph mask wrapped in a 4-direction
    keyline so the engraved numerals stay crisp against the cartouche without
    the diagonal offsets closing the counters of "5" and "0"."""
    mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
    r = mask.get_rect(center=center)
    key = mask.copy()
    key.fill((*col_key, 255), special_flags=pygame.BLEND_RGBA_MULT)
    p = sc.m(1)
    for ang in (0, 90, 180, 270):
        face.blit(key, (r.x + int(p * _math.cos(_math.radians(ang))),
                        r.y + int(p * _math.sin(_math.radians(ang)))))
    img = mask.copy()
    if col_fill_stops:
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0, col_fill_stops, 255, 1.0)
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img.fill((*col_fill_flat, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(img, r)


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Draw the brass-classic swing tag at a fixed anchor in the 2x card buffer.
    Affordability is read from the variant (the store passes "locked" for
    gated/too-expensive cards); the wallet-derived `affordable` kwarg is absorbed
    and ignored so the exploration sheet can force both states deterministically."""
    affordable = (variant != "locked")
    text = _abbr(text)

    grommet_local = (28, 12)
    tag_center = (44, 60)
    knot = (22, 13)

    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, FACE_W, FACE_H)

    if affordable:
        body = sc.vgrad_stops(FACE_W, FACE_H, sc.m(3),
                              [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                              255, 1.04)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, sc.m(3), (80, 52, 12, 200),
                     (255, 240, 190, 200), w=max(1, sc.m(1.2)))
        pygame.draw.rect(face, (196, 178, 148),
                         pygame.Rect(0, 0, FACE_W, FACE_H).inflate(-6, -6),
                         1, border_radius=max(1, sc.m(2)))
        pygame.draw.line(face, (120, 72, 16), (4, 38), (FACE_W - 4, 38), max(1, sc.m(1)))
        pygame.draw.rect(face, (200, 176, 132),
                         pygame.Rect(4, 40, FACE_W - 8, 38), border_radius=sc.m(2))
        pygame.draw.rect(face, (168, 142, 104),
                         pygame.Rect(4, 40, FACE_W - 8, 38), 1)
        _grommet(face, 28, 12, sc.m(6.5), sc.m(3), sc.m(2),
                 (186, 142, 48), (250, 224, 120), (72, 44, 8), (12, 6, 2))
        _draw_price(face, text, (FACE_W // 2, 58), (76, 44, 8),
                    col_fill_stops=[(0.0, (224, 176, 64)), (0.35, (190, 144, 40)),
                                    (0.7, (136, 84, 16)), (1.0, (76, 44, 8))], fs=15)
        cord_a, cord_b = (210, 178, 118), (150, 118, 70)
        knot_col, knot_spec = (210, 178, 118), (240, 220, 180)
    else:
        body = sc.vgrad_stops(FACE_W, FACE_H, sc.m(3),
                              [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))],
                              255, 1.02)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, sc.m(3), (54, 58, 74, 200),
                     (214, 218, 232, 200), w=max(1, sc.m(1.2)))
        pygame.draw.rect(face, (140, 144, 160),
                         pygame.Rect(0, 0, FACE_W, FACE_H).inflate(-6, -6),
                         1, border_radius=max(1, sc.m(2)))
        pygame.draw.line(face, (88, 92, 108), (4, 38), (FACE_W - 4, 38), max(1, sc.m(1)))
        pygame.draw.rect(face, (128, 132, 148),
                         pygame.Rect(4, 40, FACE_W - 8, 38), border_radius=sc.m(2))
        pygame.draw.rect(face, (168, 142, 104),
                         pygame.Rect(4, 40, FACE_W - 8, 38), 1)
        _grommet(face, 28, 12, sc.m(6.5), sc.m(3), sc.m(2),
                 (78, 82, 96), (120, 126, 144), (30, 32, 42), (20, 22, 32))
        _draw_price(face, text, (FACE_W // 2, 58), (48, 52, 66),
                    col_fill_flat=(200, 206, 220), fs=15)
        cord_a, cord_b = (152, 156, 170), (170, 174, 186)
        knot_col, knot_spec = (152, 156, 170), (200, 204, 216)

    rot = pygame.transform.rotate(face, TILT)

    # cord under the tag so it reads as diving into the grommet bore, anchored
    # on the grommet's post-rotation centre.
    gx, gy = _rot_point(28, 12, FACE_W, FACE_H, tag_center, TILT)
    _cord(surf, (gx, gy), knot, cord_a, cord_b, sc.m(3), sc.m(2))

    surf.blit(rot, rot.get_rect(center=tag_center))

    # knot nub last, capping the cord at the card corner.
    pygame.draw.circle(surf, knot_col, knot, max(1, sc.m(2)))
    pygame.draw.circle(surf, knot_spec, knot, max(1, sc.m(0.6)))


sc.price_chip = my_price_chip


def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


# ── numeral fit sanity (abbreviation + no clip) ───────────────────────────────
assert _abbr("250") == "250", "250 abbreviation regressed"
assert _abbr("1100") == "1.1k", "1100 abbreviation regressed"
for _t in ("250", "1.1k"):
    _mask = sc._stamp_bold(sc._glyph_base(_t, sc.font(15), 0), sc.m(1.0))
    _ink = _mask.get_bounding_rect().width
    assert _ink <= FACE_W - 4, f"{_t} clips the tag face ({_ink}px ink)"
print("numeral fit PASS")

# ── pixel verification (run BEFORE saving the sheet) ──────────────────────────
va = render_card_1x("skin_mummy", True)
vl = render_card_1x("skin_mummy", False)
bg = (8, 8, 20)
found = False
for x in range(10, 30):
    for y in range(4, 18):
        p = va.get_at((x, y))[:3]
        if any(abs(p[i] - bg[i]) > 30 for i in range(3)):
            found = True
            break
    if found:
        break
assert found, "grommet zone not detected"
assert va.get_at((18, 12))[:3] != vl.get_at((18, 12))[:3], "states identical"
print("verify PASS")

# ── render sheet ──────────────────────────────────────────────────────────────
PAD, GAP, HEADER_H, LABEL_H = 20, 12, 40, 20
BG = (8, 8, 20)
row1 = [("skin_mummy", True, "MUMMY aff"), ("skin_mummy", False, "MUMMY locked"),
        ("skin_kitsune", True, "KITSUNE aff"), ("skin_kitsune", False, "KITSUNE locked")]
cards1 = [(render_card_1x(sid, aff), lbl) for sid, aff, lbl in row1]

crop_w, crop_h, zoom = 80, 100, 2
crops = [(pygame.transform.scale(va.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x crop aff"),
         (pygame.transform.scale(vl.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x crop locked")]

row1_w = 4 * sc.CARD_W + 3 * GAP
row2_w = 2 * crop_w * zoom + GAP
sheet_w = PAD * 2 + max(row1_w, row2_w)
sheet_h = PAD + HEADER_H + sc.CARD_H + LABEL_H + GAP + crop_h * zoom + LABEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)
fh = hud_font(22)
fl = hud_font(13)
sheet.blit(fh.render("BRASS-CLASSIC — tl4 hang-tag round 2", True, (240, 224, 180)),
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

out = "docs/store_price_tl4/brass_classic/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
print(f"canvas {sheet_w}x{sheet_h}")
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")

import subprocess
result = subprocess.run(['python3', '-c', '''
from PIL import Image
img = Image.open("docs/store_price_tl4/brass_classic/round_2.png")
print("size:", img.size)
'''], capture_output=True, text=True, cwd='/home/user/skybit')
print(result.stdout)
