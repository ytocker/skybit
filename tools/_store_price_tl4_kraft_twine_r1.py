"""Round-1 render for the `kraft-twine` store-card price tag (tier-line 4).

An artisan kraft-paper swing-tag: a warm brown portrait face with horizontal
grain banding so it reads as pressed paper stock rather than flat plastic, a
matte bronze eyelet (a soft luma lift, deliberately no bright UL arc — bronze
is diffuse, not chrome) seated in a reinforcement washer, threaded on hemp
twine, and a rubber-stamped espresso price pressed into the face. The kraft
palette and grain sell it as a physical hang-tag off the card's top-left.

Locked cards drain the stock to a cool grey-brown and cool the metal and ink to
match, so the tag still reads as the same object, just spent of colour.

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

# The tag face is authored directly in the 2x card buffer's device px (like the
# tl2/tl3 swing-tags), so FACE_W/FACE_H and every sc.m() feature share one scale.
FACE_W = 68
FACE_H = 82
TILT = -7                            # pygame +CCW => a small clockwise lean


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


def _rot_point(px, py, fw, fh, center, angle_deg):
    """Map a face-local point to sheet space after the tag is rotated about its
    center, so the twine can anchor to the grommet's true post-rotation spot."""
    th = _math.radians(angle_deg)
    dx, dy = px - fw / 2, py - fh / 2
    rx = dx * _math.cos(th) + dy * _math.sin(th)
    ry = -dx * _math.sin(th) + dy * _math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _cord(surf, p0, p1, col_a, col_b, seg_dp, lw):
    """Two-tone dashed segments read as a twisted hemp strand rather than a flat
    line — alternating shade fakes the twist without per-fibre drawing."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = max(1, int(_math.hypot(dx, dy) / seg_dp))
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        x0, y0 = p0[0] + dx * t0, p0[1] + dy * t0
        x1, y1 = p0[0] + dx * t1, p0[1] + dy * t1
        pygame.draw.line(surf, col_a if i % 2 == 0 else col_b,
                         (int(x0), int(y0)), (int(x1), int(y1)), lw)


def _draw_price(face, text, center, col_key, col_fill_flat, fs=13):
    """Solid-fill numeral with a thick keyline for a rubber-stamp feel — the ink
    reads as pressed into the paper, not printed flat, thanks to the heavy
    outline halo struck around a flat espresso core."""
    mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
    r = mask.get_rect(center=center)
    key = mask.copy()
    key.fill((*col_key, 255), special_flags=pygame.BLEND_RGBA_MULT)
    p = max(1, sc.m(1.5))            # THICK keyline for rubber-stamp look
    for ang in range(0, 360, 45):
        face.blit(key, (r.x + int(p * _math.cos(_math.radians(ang))),
                        r.y + int(p * _math.sin(_math.radians(ang)))))
    img = mask.copy()
    img.fill((*col_fill_flat, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(img, r)


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Draw the kraft hang-tag at a fixed anchor in the 2x card buffer.
    Affordability is read from the variant (the store passes "locked" for
    gated/too-expensive cards); the wallet `affordable` kwarg is absorbed so the
    exploration sheet can force both states deterministically."""
    affordable = (variant != "locked")
    text = _abbr(text)

    rad = sc.m(3)
    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)

    if affordable:
        # Kraft paper: warm brown vertical falloff with a 2-row banding so it
        # reads as pressed paper grain even after smoothscale to 1x.
        for y in range(FACE_H):
            t = y / max(1, FACE_H - 1)
            base_r = int(204 - t * 36)          # 204 -> 168
            base_g = int(168 - t * 36)          # 168 -> 132
            base_b = int(112 - t * 28)          # 112 -> 84
            band = 8 if (y // 2) % 2 == 0 else -4
            r = max(0, min(255, base_r + band))
            g = max(0, min(255, base_g + band))
            b = max(0, min(255, base_b + band))
            pygame.draw.line(face, (r, g, b), (0, y), (FACE_W - 1, y))
    else:
        # Spent stock: flat cool grey-brown, no grain, still card-shaped.
        for y in range(FACE_H):
            pygame.draw.line(face, (152, 138, 118), (0, y), (FACE_W - 1, y))

    # Rounded-rect clip so the paper stock keeps the tag silhouette.
    mask_surf = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.rect(mask_surf, (255, 255, 255, 255),
                     (0, 0, FACE_W, FACE_H), border_radius=rad)
    face.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    if affordable:
        bevel_deep, bevel_bright = (80, 46, 14, 200), (230, 190, 130, 160)
        patch_col = (194, 164, 116)
        g_base, g_soft = (152, 96, 36), (184, 128, 68, 80)
        g_shadow, g_ring = (78, 44, 10), (152, 96, 36)
        g_bore, g_bore_rim = (40, 20, 6), (100, 64, 30, 100)
        rule_col = (60, 28, 8)
        price_key, price_fill = (16, 8, 2), (44, 22, 8)
        cord_a, cord_b = (176, 146, 96), (138, 106, 56)
        knot_col = (156, 124, 74)
    else:
        bevel_deep, bevel_bright = (80, 74, 64, 200), (190, 182, 168, 160)
        patch_col = (168, 164, 156)
        g_base, g_soft = (100, 106, 112), (130, 136, 144, 60)
        g_shadow, g_ring = (60, 64, 72), (100, 106, 112)
        g_bore, g_bore_rim = (40, 42, 50), (72, 76, 84, 100)
        rule_col = (100, 96, 90)
        price_key, price_fill = (56, 50, 44), (102, 92, 82)
        cord_a, cord_b = (140, 136, 128), (110, 108, 104)
        knot_col = (120, 118, 114)

    sc.bevel_rim(face, pygame.Rect(0, 0, FACE_W, FACE_H), sc.m(3),
                 bevel_deep, bevel_bright, w=max(1, sc.m(1)))

    # Reinforcement washer under the eyelet, drawn before the metal.
    pygame.draw.circle(face, patch_col, (28, 12), sc.m(7))

    # Matte bronze grommet: a diffuse metal, so a soft UL luma lift stands in
    # for a highlight rather than a bright chrome arc.
    gx, gy = 28, 12
    r_out = sc.m(5)
    pygame.draw.circle(face, g_base, (gx, gy), r_out)
    soft_surf = pygame.Surface((r_out * 2 + 2, r_out * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(soft_surf, g_soft,
                       (r_out + 1 - sc.m(2), r_out + 1 - sc.m(2)), sc.m(3))
    face.blit(soft_surf, (gx - r_out - 1, gy - r_out - 1))
    pts_sh = [(gx, gy)]
    for a in range(300, 401, 6):
        pts_sh.append((int(gx + r_out * _math.cos(_math.radians(a % 360))),
                       int(gy + r_out * _math.sin(_math.radians(a % 360)))))
    if len(pts_sh) >= 3:
        pygame.draw.polygon(face, g_shadow, pts_sh)
    pygame.draw.circle(face, g_ring, (gx, gy), r_out, max(1, sc.m(1.5)))
    pygame.draw.circle(face, g_bore, (gx, gy), sc.m(3))
    pygame.draw.circle(face, g_bore_rim, (gx, gy), sc.m(3), 1)
    pygame.draw.circle(face, (0, 0, 0, 0), (gx, gy), sc.m(2))

    # Double ruling lines separate the header field from the price panel.
    pygame.draw.line(face, rule_col, (4, 32), (FACE_W - 4, 32), 1)
    pygame.draw.line(face, rule_col, (4, 34), (FACE_W - 4, 34), 1)

    _draw_price(face, text, (FACE_W // 2, 56), price_key, price_fill, fs=13)

    rot = pygame.transform.rotate(face, TILT)

    # Twine from the rotated grommet up to the knot nub, under the tag.
    gx2, gy2 = _rot_point(gx, gy, FACE_W, FACE_H, (44, 60), TILT)
    _cord(surf, (gx2, gy2), (22, 13), cord_a, cord_b, sc.m(3), sc.m(1.5))

    surf.blit(rot, rot.get_rect(center=(44, 60)))

    # Knot nub last so it caps the twine cleanly.
    pygame.draw.circle(surf, knot_col, (22, 13), max(1, sc.m(1.5)))


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
va = render_card_1x("skin_mummy", True)
vl = render_card_1x("skin_mummy", False)
bg = (8, 8, 20)
found = any(any(abs(va.get_at((x, y))[i] - bg[i]) > 30 for i in range(3))
            for x in range(10, 30) for y in range(4, 18))
assert found, "grommet zone not detected"
assert va.get_at((15, 30))[:3] != vl.get_at((15, 30))[:3], "states identical"
print("verify PASS")

# ── render sheet ──────────────────────────────────────────────────────────────
PAD, GAP, HEADER_H, LABEL_H = 20, 12, 40, 20
BG = (8, 8, 20)
row1 = [("skin_mummy", True, "MUMMY aff"), ("skin_mummy", False, "MUMMY locked"),
        ("skin_kitsune", True, "KITSUNE aff"),
        ("skin_kitsune", False, "KITSUNE locked")]
cards1 = [(render_card_1x(sid, aff), lbl) for sid, aff, lbl in row1]
crop_w, crop_h, zoom = 80, 100, 2
crops = [(pygame.transform.scale(va.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x left aff"),
         (pygame.transform.scale(vl.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x left locked")]
row1_w = 4 * sc.CARD_W + 3 * GAP
row2_w = 2 * crop_w * zoom + GAP
sheet_w = PAD * 2 + max(row1_w, row2_w)
sheet_h = PAD + HEADER_H + sc.CARD_H + LABEL_H + GAP + crop_h * zoom + LABEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)
fh = hud_font(22)
fl = hud_font(13)
sheet.blit(fh.render("KRAFT-TWINE — tl4 hang-tag round 1", True, (232, 204, 150)),
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
out = "docs/store_price_tl4/kraft_twine/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
