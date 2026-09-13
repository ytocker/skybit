"""Round-2 render for the `kraft-twine` store-card price tag (tier-line 4).

An artisan kraft-paper swing-tag: a warm brown portrait face with per-row grain
banding so it reads as pressed paper stock rather than flat plastic, a matte
bronze eyelet (a diffuse metal — a soft warm glint stands in for a highlight,
never a chrome arc) seated in a reinforcement washer that reads as its own disc
ring, threaded on hemp twine, and an espresso rubber-stamp price pressed DIRECTLY
into the kraft face (no chip behind it). The kraft palette and grain sell it as a
physical hang-tag off the card's top-left.

Round-1 rendered the eyelet centre as a punched transparent hole, so the dark
bluish card body bled through and read as violet. Round 2 fills the bore solid
and keeps every metal/cord tone strictly warm; the grommet is rebuilt as matte
bronze, the washer as a distinct ring, the ruling as two crisp hairlines.

Locked cards drain the stock to a true mid-slate grey (lifted well clear of the
night sky) and cool the metal and ink to match, so the tag still reads as the
same object, just spent of colour.

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


def _grommet(face, gx, gy, col_metal, glint, bore, kraft_body):
    """Matte bronze eyelet: a diffuse metal, so a soft warm glint at the UL stands
    in for a highlight (no chrome arc). A distinct washer ring seats it, and the
    bore is a SOLID dark disc — never a punched transparent hole, which is what
    let the dark card body bleed through as false violet in round 1."""
    # Reinforcement washer as its own disc: a darker ring punched by the kraft
    # body colour, so it reads as a separate washer before the metal covers it.
    pygame.draw.circle(face, tuple(max(0, c - 16) for c in kraft_body[:3]),
                       (gx, gy), sc.m(7))
    pygame.draw.circle(face, kraft_body, (gx, gy), sc.m(5.5))

    r_out = sc.m(5)
    pygame.draw.circle(face, col_metal, (gx, gy), r_out)
    # Soft matte glint biased up-left, then the metal ring is redrawn over it so
    # the glint is contained inside the rim and the eyelet edge stays crisp.
    pygame.draw.circle(face, glint, (gx - sc.m(2), gy - sc.m(2)), sc.m(2.5))
    pygame.draw.circle(face, col_metal, (gx, gy), r_out, max(1, sc.m(1.5)))
    # Solid dark bore + a faint lifted rim for depth (never transparent).
    pygame.draw.circle(face, bore, (gx, gy), sc.m(3))
    pygame.draw.circle(face, tuple(min(255, c + 26) for c in bore),
                       (gx, gy), sc.m(3), 1)


def _draw_price(face, text, center, col_key, col_fill_flat, fs=13):
    """Espresso rubber-stamp numeral pressed DIRECTLY into the kraft face — a flat
    dark-ink core struck with a thick near-black keyline halo so it reads as
    pressed into the paper, not printed on a chip."""
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
        # Kraft paper: warm brown vertical falloff with a per-row +/-20 luma swing
        # so it reads as pressed paper grain even after smoothscale to 1x.
        for y in range(FACE_H):
            t = y / max(1, FACE_H - 1)
            base_r = int(204 - t * 36)          # 204 -> 168
            base_g = int(168 - t * 36)          # 168 -> 132
            base_b = int(112 - t * 28)          # 112 -> 84
            band = 20 if (y % 2 == 0) else -20
            r = max(0, min(255, base_r + band))
            g = max(0, min(255, base_g + band))
            b = max(0, min(255, base_b + band))
            pygame.draw.line(face, (r, g, b), (0, y), (FACE_W - 1, y))
    else:
        # Spent stock: true mid-slate grey (lifted ~3x off the night sky), still
        # card-shaped, still grained so it reads as the same paper object.
        for y in range(FACE_H):
            t = y / max(1, FACE_H - 1)
            base_r = int(74 - t * 18)           # 74 -> 56
            base_g = int(80 - t * 18)           # 80 -> 62
            base_b = int(96 - t * 20)           # 96 -> 76
            band = 12 if (y % 2 == 0) else -12
            r = max(0, min(255, base_r + band))
            g = max(0, min(255, base_g + band))
            b = max(0, min(255, base_b + band))
            pygame.draw.line(face, (r, g, b), (0, y), (FACE_W - 1, y))

    # Rounded-rect clip so the paper stock keeps the tag silhouette.
    mask_surf = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.rect(mask_surf, (255, 255, 255, 255),
                     (0, 0, FACE_W, FACE_H), border_radius=rad)
    face.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    if affordable:
        bevel_deep, bevel_bright = (80, 46, 14, 200), (230, 190, 130, 160)
        # Strictly warm metal — matte bronze, never any high-blue tint.
        g_metal, g_glint, g_bore = (170, 120, 64), (205, 165, 110), (40, 20, 6)
        kraft_body = (204, 168, 112)
        rule_col = (60, 28, 8)
        price_key, price_fill = (16, 8, 2), (44, 22, 8)
        cord_a, cord_b = (198, 176, 128), (150, 128, 88)
        knot_col = (190, 168, 120)
    else:
        bevel_deep, bevel_bright = (38, 42, 52, 200), (150, 160, 178, 160)
        g_metal, g_glint, g_bore = (96, 104, 112), (150, 160, 175), (34, 38, 46)
        kraft_body = (74, 80, 96)
        rule_col = (44, 50, 62)
        price_key, price_fill = (20, 24, 32), (52, 58, 70)
        cord_a, cord_b = (150, 156, 168), (120, 126, 138)
        knot_col = (135, 142, 154)

    sc.bevel_rim(face, pygame.Rect(0, 0, FACE_W, FACE_H), sc.m(3),
                 bevel_deep, bevel_bright, w=max(1, sc.m(1)))

    gx, gy = 28, 12
    _grommet(face, gx, gy, g_metal, g_glint, g_bore, kraft_body)

    # Double ruling: two hairlines with a 2dp gap, dividing the header field from
    # the price field. Each is authored 2 device-px tall so the 2:1 downscale
    # resolves it as one crisp 1px hairline instead of averaging it away.
    pygame.draw.rect(face, rule_col, (4, sc.m(16), FACE_W - 8, 2))
    pygame.draw.rect(face, rule_col, (4, sc.m(18), FACE_W - 8, 2))

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


def _no_violet(card, x0, x1, y0, y1):
    """A pixel is 'violet' when blue clearly dominates a warm tan/bronze zone.
    The tag must never do this again — the round-1 bore bled the blue card body."""
    for x in range(x0, x1):
        for y in range(y0, y1):
            r, g, b = card.get_at((x, y))[:3]
            if b > r + 25 and b > g + 25 and b > 70:
                return False, (x, y, (r, g, b))
    return True, None


# The tag renders top-left about device (44,60) -> 1x card centre ~ (22,30). The
# grommet+cord live in x 8..25, y 4..20; the price stamp in x 8..30, y 30..44.
ok_cord, bad_cord = _no_violet(va, 8, 25, 4, 20)
ok_price, bad_price = _no_violet(va, 8, 30, 30, 45)
assert ok_cord, f"cord/grommet zone went violet: {bad_cord}"
assert ok_price, f"price zone went violet: {bad_price}"

# Price must be DARK espresso ink pressed on kraft, not a light chip.
price_dark = any(sum(va.get_at((x, y))[:3]) < 180
                 for x in range(14, 26) for y in range(33, 43))
assert price_dark, "price stamp is not dark espresso ink"
print("verify PASS")

# ── render sheet ──────────────────────────────────────────────────────────────
PAD, GAP, HEADER_H, LABEL_H = 20, 12, 40, 20
BG = (8, 8, 20)
row1 = [("skin_mummy", True, "MUMMY EPIC aff"),
        ("skin_mummy", False, "MUMMY EPIC locked"),
        ("skin_kitsune", True, "KITSUNE LEG aff"),
        ("skin_kitsune", False, "KITSUNE LEG locked")]
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
sheet.blit(fh.render("KRAFT-TWINE — tl4 hang-tag round 2", True, (232, 204, 150)),
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

print(f"verify PASS — canvas {sheet_w}x{sheet_h}")
out = "docs/store_price_tl4/kraft_twine/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")

# ── post-save probe: confirm the cord/grommet is warm, not violet ─────────────
from PIL import Image
img = Image.open(out).convert("RGB")
ox, oy = PAD, PAD + HEADER_H          # card-1 origin on the sheet
print("Checking cord is not violet...")
warm_hits = viol_hits = 0
for yy in range(4, 20):
    for xx in range(8, 25):
        r, g, b = img.getpixel((ox + xx, oy + yy))
        if r > 120 and r >= g >= b:
            warm_hits += 1
        if b > r + 25 and b > g + 25 and b > 70:
            viol_hits += 1
print(f"cord/grommet zone: warm_hits={warm_hits} violet_hits={viol_hits}")
assert viol_hits == 0, "cord/grommet still rendering violet!"
print("cord + grommet confirmed warm tan/bronze — no violet.")
