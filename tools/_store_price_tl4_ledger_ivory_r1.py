"""Round-1 render for the `ledger-ivory` store-card price tag (tier-line 4).

A heritage two-zone ledger swing-tag. The face is a symmetric ivory card stock
with a NEAR-FLAT gradient, hung from a single brass grommet punched at the
top-CENTRE (this is a balanced ledger card, not a corner-hung label). An
embossed double-rule pressed across the card splits it into an upper price zone
carrying the largest numeral of the whole tl4 line, and a lower ruled sub-band
that reads as the ledger's ruled foot. The identity is that pressed-ridge rule:
a dark line with a bright highlight row just under it so the card stock looks
physically debossed rather than printed.

Locked cards cool the whole stock to grey and desaturate the brass to pewter so
the tag reads as the same pressed object, just spent of colour.

Review sheet only — nothing here is wired into the live store draw path.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import math
import math as _math
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

# The tag face is authored directly in the 2x card buffer's device px, so
# FACE_W/FACE_H and every sc.m() feature share one scale.
FACE_W = 68
FACE_H = 82
TILT = -7                                # pygame +CCW; the tag leans -7deg


def _abbr(text):
    """Prices climb into the thousands; a ledger face is narrow, so collapse
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
    """Where a face-local point lands in world space after the face is rotated
    about `center` — used so the cord dives into the grommet's true position."""
    th = _math.radians(angle_deg)
    dx, dy = px - fw / 2, py - fh / 2
    rx = dx * _math.cos(th) + dy * _math.sin(th)
    ry = -dx * _math.sin(th) + dy * _math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _cord_double(surf, p0, p1, col_a, col_b, lw):
    """Two parallel cotton strands offset either side of the centre line, so the
    drape reads as twisted twine rather than a single drawn stroke."""
    import math as _m
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = _m.hypot(dx, dy)
    if length < 1:
        return
    nx, ny = -dy / length, dx / length
    off = max(1, sc.m(1))
    pygame.draw.line(surf, col_a,
                     (int(p0[0] + nx * off), int(p0[1] + ny * off)),
                     (int(p1[0] + nx * off), int(p1[1] + ny * off)), lw)
    pygame.draw.line(surf, col_b,
                     (int(p0[0] - nx * off), int(p0[1] - ny * off)),
                     (int(p1[0] - nx * off), int(p1[1] - ny * off)), lw)


def _draw_price(face, text, center, col_key, col_fill_flat, fs=14):
    """Solid numerals poured into the bold glyph mask, ringed by a 1px keyline so
    the price lifts off the ivory stock in either state."""
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


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Draw the ledger-ivory tag at a fixed anchor in the 2x card buffer.
    Affordability is read from the variant ("locked" for gated/too-expensive
    cards); any wallet-derived kwarg is absorbed so the sheet can force states."""
    affordable = (variant != "locked")
    text = _abbr(text)

    tag_center = (44, 60)
    knot = (22, 13)
    GX, GY = FACE_W // 2, 14              # grommet punched top-CENTRE

    if affordable:
        body_stops = [(0.0, (240, 232, 212)),
                      (0.5, (236, 228, 208)),
                      (1.0, (228, 218, 198))]
        rim_deep, rim_bright = (64, 32, 8, 200), (255, 244, 210, 180)
        patch_col = (210, 192, 160)
        grommet_main = (184, 140, 46)
        grommet_ul = (238, 208, 88)
        grommet_lr = (68, 42, 8)
        grommet_bore = (32, 18, 4)
        grommet_inner_rim = (238, 208, 88, 120)
        price_key, price_fill = (44, 24, 8), (44, 24, 8)
        rule_main, rule_hi = (108, 60, 16), (228, 214, 186)
        coins_col = (108, 60, 16)
        cord_a, cord_b = (198, 178, 144), (160, 138, 104)
        knot_col = (180, 160, 128)
    else:
        body_stops = [(0.0, (210, 206, 198)),
                      (0.5, (206, 202, 194)),
                      (1.0, (200, 196, 188))]
        rim_deep, rim_bright = (80, 76, 68, 200), (230, 226, 218, 160)
        patch_col = (178, 174, 164)
        grommet_main = (70, 74, 88)
        grommet_ul = (110, 116, 132)
        grommet_lr = (28, 30, 44)
        grommet_bore = (24, 24, 32)
        grommet_inner_rim = (110, 116, 132, 100)
        price_key, price_fill = (50, 50, 64), (88, 88, 102)
        rule_main, rule_hi = (120, 120, 130), (220, 220, 228)
        coins_col = (140, 142, 155)
        cord_a, cord_b = (140, 136, 130), (112, 108, 104)
        knot_col = (126, 122, 116)

    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)

    # near-flat ivory body
    body = sc.vgrad_stops(FACE_W, FACE_H, sc.m(3), body_stops, 255, 1.0)
    face.blit(body, (0, 0))

    sc.bevel_rim(face, pygame.Rect(0, 0, FACE_W, FACE_H), sc.m(3),
                 rim_deep, rim_bright, w=max(1, sc.m(1.5)))

    # reinforcement washer pressed under the grommet before the eyelet lands
    pygame.draw.circle(face, patch_col, (FACE_W // 2, 14), sc.m(8))

    # brass grommet: solid disc, an upper-left lit wedge + lower-right shaded
    # wedge for the bevel, a ring, a dark bore, an inner sheen, a punched void.
    gx, gy = GX, GY
    r_out = sc.m(5)
    pygame.draw.circle(face, grommet_main, (gx, gy), r_out)
    pts_hi = [(gx, gy)]
    for a in range(120, 221, 6):
        pts_hi.append((int(gx + r_out * _math.cos(_math.radians(a))),
                       int(gy + r_out * _math.sin(_math.radians(a)))))
    if len(pts_hi) >= 3:
        pygame.draw.polygon(face, grommet_ul, pts_hi)
    pts_sh = [(gx, gy)]
    for a in range(300, 401, 6):
        pts_sh.append((int(gx + r_out * _math.cos(_math.radians(a % 360))),
                       int(gy + r_out * _math.sin(_math.radians(a % 360)))))
    if len(pts_sh) >= 3:
        pygame.draw.polygon(face, grommet_lr, pts_sh)
    pygame.draw.circle(face, grommet_main, (gx, gy), r_out, max(1, sc.m(1.5)))
    pygame.draw.circle(face, grommet_bore, (gx, gy), sc.m(3))
    pygame.draw.circle(face, grommet_inner_rim, (gx, gy), sc.m(3), 1)
    pygame.draw.circle(face, (0, 0, 0, 0), (gx, gy), sc.m(2))

    # UPPER ZONE price — largest numeral of the tl4 line; fall to fs=13 if the
    # tall glyph would clip up into the reinforcement patch.
    price_fs = 14
    trial = sc._stamp_bold(sc._glyph_base(text, sc.font(price_fs), 0), sc.m(1.0))
    if trial.get_height() > sc.m(30):    # ~top of glyph would reach the patch
        price_fs = 13
    _draw_price(face, text, (FACE_W // 2, 32), price_key, price_fill, fs=price_fs)

    # embossed double-rule at the zone boundary: dark rule, a bright highlight
    # row just under it (the pressed ridge), then a second dark rule.
    lw = max(1, sc.m(1))
    pygame.draw.line(face, rule_main, (4, 52), (FACE_W - 4, 52), lw)
    pygame.draw.line(face, rule_hi, (4, 53), (FACE_W - 4, 53), lw)
    pygame.draw.line(face, rule_main, (4, 55), (FACE_W - 4, 55), lw)

    # lower ruled sub-band label
    f_sub = sc.font(4)
    coins_surf = f_sub.render("COINS", True, coins_col)
    if coins_surf.get_height() >= 4:
        face.blit(coins_surf, coins_surf.get_rect(center=(FACE_W // 2, 68)))

    rot = pygame.transform.rotate(face, TILT)

    # cord dives into the grommet's true (rotated) world position, then up to
    # the knot; drawn before the face blit so it tucks under the eyelet.
    gx2, gy2 = _rot_point(FACE_W // 2, 14, FACE_W, FACE_H, tag_center, TILT)
    _cord_double(surf, (gx2, gy2), knot, cord_a, cord_b, max(1, sc.m(1.5)))

    surf.blit(rot, rot.get_rect(center=tag_center))

    pygame.draw.circle(surf, knot_col, knot, max(1, sc.m(1.5)))


sc.price_chip = my_price_chip


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


# ── pixel verification (run BEFORE saving the sheet) ──────────────────────────
va = render_card_1x("skin_mummy", True)
vl = render_card_1x("skin_mummy", False)
bg = (8, 8, 20)
# grommet is top-center for the ledger — check around x=15..34, y=4..18
found = any(any(abs(va.get_at((x, y))[i] - bg[i]) > 30 for i in range(3))
            for x in range(15, 35) for y in range(4, 18))
assert found, "grommet zone not detected"
assert va.get_at((20, 12))[:3] != vl.get_at((20, 12))[:3], "states identical"
print("verify PASS")

# ── render sheet ──────────────────────────────────────────────────────────────
BG = (8, 8, 20)
PAD = 20
GAP = 12
HEADER_H = 40
LABEL_H = 20
CW, CH = sc.CARD_W, sc.CARD_H

cards = {
    "mummy_aff":   render_card_1x("skin_mummy",   True),
    "mummy_lck":   render_card_1x("skin_mummy",   False),
    "kitsune_aff": render_card_1x("skin_kitsune", True),
    "kitsune_lck": render_card_1x("skin_kitsune", False),
}

row1_h = CH
row2_h = 200
total_w = PAD + 4 * CW + 3 * GAP + PAD
total_h = HEADER_H + LABEL_H + row1_h + GAP + row2_h + PAD
canvas = pygame.Surface((total_w, total_h))
canvas.fill(BG)

hf = hud_font(9, True)
ht = hf.render("LEDGER-IVORY — tl4 hang-tag round 1", True, (255, 220, 80))
canvas.blit(ht, (total_w // 2 - ht.get_width() // 2,
                 (HEADER_H - ht.get_height()) // 2))

lf = hud_font(7)
card_list = [cards["mummy_aff"], cards["mummy_lck"],
             cards["kitsune_aff"], cards["kitsune_lck"]]
labels = ["mummy aff", "mummy lck", "kitsune aff", "kitsune lck"]
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

out = "docs/store_price_tl4/ledger_ivory/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
