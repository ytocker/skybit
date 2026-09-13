"""Round-2 render for the `ornament-rule` tl5 store-card price tag.

Iterates r1 on art-director notes: the bronze diamond ornament is enlarged so
it survives the SS downscale (m(4) + mahogany keyline), the invisible cool
overlay is dropped, the price sits on a recessed champagne well for its own
ground, the specular pip is bumped to a readable size, and the hemp cord uses
tighter segments so the two-tone twist reads over the short run.
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
    pygame.draw.circle(face, col_bore, (gx, gy), r_bore - 1, 1)


def _cord(surf, p0, p1, col_a, col_b, seg_dp, lw):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = max(1, int(_math.hypot(dx, dy) / seg_dp))
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        x0, y0 = p0[0] + dx * t0, p0[1] + dy * t0
        x1, y1 = p0[0] + dx * t1, p0[1] + dy * t1
        pygame.draw.line(surf, col_a if i % 2 == 0 else col_b,
                         (int(x0), int(y0)), (int(x1), int(y1)), lw)


def _rot_point(px, py, fw, fh, center, angle_deg):
    th = _math.radians(angle_deg)
    dx, dy = px - fw / 2, py - fh / 2
    rx = dx * _math.cos(th) + dy * _math.sin(th)
    ry = -dx * _math.sin(th) + dy * _math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _abbr(text):
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _draw_price(face, text, center, col_key, col_fill_stops=None, col_fill_flat=None, fs=14):
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


def _ornament_divider(face, y, col):
    """Enlarged bronze diamond flanked by hairlines — sized to survive the downscale.

    The r1 m(2) diamond blurred to noise; m(4) plus a darker mahogany keyline
    reads as a crisp ~8px lozenge after smoothscale.
    """
    diamond_r = sc.m(4)
    cx = FACE_W // 2
    line_w = max(2, sc.m(1))
    line_col = (120, 72, 16)  # mahogany hairline framing the ornament
    pygame.draw.line(face, col, (6, y), (cx - diamond_r - 2, y), line_w)
    pygame.draw.line(face, col, (cx + diamond_r + 2, y), (FACE_W - 6, y), line_w)
    key_pts = [(cx, y - diamond_r - 1), (cx + diamond_r + 1, y),
               (cx, y + diamond_r + 1), (cx - diamond_r - 1, y)]
    pygame.draw.polygon(face, line_col, key_pts)
    pts = [(cx, y - diamond_r), (cx + diamond_r, y), (cx, y + diamond_r), (cx - diamond_r, y)]
    pygame.draw.polygon(face, col, pts)


def _price_well(face, plate_col, shadow_col):
    """Recessed champagne plate so the numeral has its own ground vs the cream body."""
    plate_rect = pygame.Rect(8, 46, FACE_W - 16, 24)
    plate = pygame.Surface((plate_rect.w, plate_rect.h), pygame.SRCALPHA)
    plate.fill(plate_col)
    face.blit(plate, plate_rect)
    pygame.draw.line(face, shadow_col, (plate_rect.x, plate_rect.y),
                     (plate_rect.right, plate_rect.y), 1)


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _abbr(text)

    gx_local, gy_local = 28, 12
    tag_center = (44, 60)
    knot = (22, 13)

    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, FACE_W, FACE_H)

    if affordable:
        body = sc.vgrad_stops(FACE_W, FACE_H, sc.m(3),
                              [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))], 255, 1.04)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, sc.m(3), (80, 52, 12, 200), (255, 240, 190, 200),
                     max(1, sc.m(1.2)))
        pygame.draw.rect(face, (196, 178, 148),
                         pygame.Rect(0, 0, FACE_W, FACE_H).inflate(-6, -6),
                         1, border_radius=max(1, sc.m(2)))

        # enlarged bronze ornament divider replacing the ruling line
        _ornament_divider(face, 38, (186, 142, 48))

        # recessed amber well grounds the numeral against the cream body
        _price_well(face, (210, 190, 150, 80), (160, 132, 80))

        # grommet + specular pip (pip bumped to a readable size)
        _grommet(face, gx_local, gy_local, sc.m(6.5), sc.m(3), sc.m(2),
                 (194, 152, 48), (244, 212, 88), (60, 38, 8), (20, 14, 4))
        pygame.draw.circle(face, (255, 248, 200),
                           (gx_local - sc.m(2), gy_local - sc.m(3)),
                           max(1, sc.m(1.1)))

        # price: darkened champagne so it reads over the well, keyline mahogany
        _draw_price(face, text, (FACE_W // 2, 58), (80, 48, 12),
                    col_fill_flat=(220, 200, 148), fs=14)

        cord_a, cord_b = (198, 176, 128), (150, 128, 88)
        knot_col, knot_spec = (198, 176, 128), (230, 214, 178)

    else:
        body = sc.vgrad_stops(FACE_W, FACE_H, sc.m(3),
                              [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))], 255, 1.02)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, sc.m(3), (54, 58, 74, 200), (214, 218, 232, 200),
                     max(1, sc.m(1.2)))
        pygame.draw.rect(face, (140, 144, 160),
                         pygame.Rect(0, 0, FACE_W, FACE_H).inflate(-6, -6),
                         1, border_radius=max(1, sc.m(2)))
        _ornament_divider(face, 38, (100, 106, 126))

        _price_well(face, (96, 100, 120, 90), (60, 64, 80))

        _grommet(face, gx_local, gy_local, sc.m(6.5), sc.m(3), sc.m(2),
                 (78, 82, 96), (120, 126, 144), (30, 32, 42), (20, 22, 32))
        pygame.draw.circle(face, (180, 184, 200),
                           (gx_local - sc.m(2), gy_local - sc.m(3)),
                           max(1, sc.m(1.1)))

        _draw_price(face, text, (FACE_W // 2, 58), (48, 52, 66),
                    col_fill_flat=(188, 196, 214), fs=14)

        cord_a, cord_b = (140, 144, 160), (108, 112, 128)
        knot_col, knot_spec = (140, 144, 160), (190, 194, 208)

    rot = pygame.transform.rotate(face, TILT)
    gx, gy = _rot_point(gx_local, gy_local, FACE_W, FACE_H, tag_center, TILT)
    _cord(surf, (gx, gy), knot, cord_a, cord_b, sc.m(2), sc.m(1.5))
    surf.blit(rot, rot.get_rect(center=tag_center))
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


# ── numeral fit sanity ─────────────────────────────────────────────────────────
assert _abbr("250") == "250"
assert _abbr("1100") == "1.1k"
for _t in ("250", "1.1k"):
    _mask = sc._stamp_bold(sc._glyph_base(_t, sc.font(14), 0), sc.m(1.0))
    _ink = _mask.get_bounding_rect().width
    assert _ink <= FACE_W - 4, f"{_t} clips ({_ink}px)"
print("numeral fit PASS")

# ── pixel verification ─────────────────────────────────────────────────────────
va = render_card_1x("skin_mummy", True)
vl = render_card_1x("skin_mummy", False)
bg = (8, 8, 20)
found = False
for x in range(8, 36):
    for y in range(4, 24):
        p = va.get_at((x, y))[:3]
        if any(abs(p[i] - bg[i]) > 30 for i in range(3)):
            found = True
            break
    if found:
        break
assert found, "grommet zone not detected"
assert va.get_at((18, 12))[:3] != vl.get_at((18, 12))[:3], "states identical"
print("verify PASS")

# ── ornament visibility: the enlarged diamond must land at y≈36-42 as non-cream ──
cream = (248, 238, 210)
orn_hits = 0
for y in range(34, 44):
    for x in range(28, 40):
        p = va.get_at((x, y))[:3]
        if any(abs(p[i] - cream[i]) > 40 for i in range(3)):
            orn_hits += 1
assert orn_hits >= 6, f"ornament too faint ({orn_hits} non-cream px)"
print(f"ornament PASS ({orn_hits} non-cream px at y36-42)")

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
sheet.blit(fh.render("ORNAMENT-RULE — tl5 hang-tag round 2", True, (240, 224, 180)),
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

out = "docs/store_price_tl5/ornament_rule/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")

import subprocess
result = subprocess.run(['python3', '-c', f'''
from PIL import Image
img = Image.open("{out}")
print("PIL size:", img.size)
'''], capture_output=True, text=True, cwd='/home/user/skybit')
print(result.stdout)
