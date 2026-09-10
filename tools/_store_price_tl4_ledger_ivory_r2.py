"""Round-2 render for the `ledger-ivory` store-card price tag (tier-line 4).

A heritage two-zone ledger swing-tag hung from a single brass grommet punched at
the top-CENTRE (this is the balanced ledger card of the tl4 line, not a
corner-hung label). Round 2 resolves the round-1 grommet/brand collision by
demoting "SKYBIT" to a micro-text band that tucks below the eyelet, hands the
whole upper face to the dominant fs=14 numeral, and re-presses the embossed
double-rule with a genuine dark/bright ridge. The cord now re-anchors to the
top-centre grommet as two clearly parallel warm cotton strands.

Locked cards drop BOTH value and hue — greyed stock plus a gunmetal eyelet — so
a spent card reads as disabled at a glance rather than merely dimmed.

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


def _cord_strands(surf, p0, p1, off, col_a, col_b, lw):
    """Two explicit parallel lines (not one offset path) so the twin-strand gap
    survives at every scale — a lone drawn stroke reads as a single wire."""
    pygame.draw.line(surf, col_a,
                     (int(p0[0] - off), int(p0[1])),
                     (int(p1[0] - off), int(p1[1])), lw)
    pygame.draw.line(surf, col_b,
                     (int(p0[0] + off), int(p0[1])),
                     (int(p1[0] + off), int(p1[1])), lw)


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
    knot = (22, 8)                       # cord terminates up-left at the knot
    GX, GY = FACE_W // 2, 14              # grommet punched top-CENTRE

    if affordable:
        # Flatter, brighter ramp: the whole face should read as one even sheet
        # of ivory stock rather than darkening toward the ruled foot.
        body_stops = [(0.0, (242, 234, 214)),
                      (0.5, (240, 232, 212)),
                      (1.0, (236, 228, 210))]
        rim_deep, rim_bright = (64, 32, 8, 200), (255, 244, 210, 180)
        patch_col = (210, 192, 160)
        grommet_main = (184, 140, 46)
        grommet_ul = (238, 208, 88)
        grommet_lr = (68, 42, 8)
        grommet_bore = (32, 18, 4)
        grommet_inner_rim = (238, 208, 88, 120)
        price_key, price_fill = (44, 24, 8), (44, 24, 8)
        brand_col = (110, 68, 26)
        coins_col = (108, 60, 16)
        cord_a, cord_b = (205, 185, 140), (165, 148, 110)
        knot_col = (180, 160, 128)
    else:
        # Locked drops value AND hue: greyed stock + gunmetal eyelet so the card
        # reads as disabled, not just a warmer copy dimmed a notch.
        body_stops = [(0.0, (204, 200, 196)),
                      (1.0, (188, 184, 180))]
        rim_deep, rim_bright = (80, 76, 68, 200), (230, 226, 218, 160)
        patch_col = (164, 160, 154)
        grommet_main = (104, 108, 120)
        grommet_ul = (160, 164, 178)
        grommet_lr = (40, 42, 52)
        grommet_bore = (18, 18, 24)
        grommet_inner_rim = (160, 164, 178, 100)
        price_key, price_fill = (50, 50, 64), (88, 88, 102)
        brand_col = (150, 148, 154)
        coins_col = (140, 142, 155)
        cord_a, cord_b = (150, 146, 138), (118, 114, 108)
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

    # ZONE A — "SKYBIT" micro-brand, dropped to face y~22..30 and rendered tiny
    # so it breathes below the grommet instead of colliding with the patch.
    f_brand = sc.font(3)
    brand_surf = f_brand.render("SKYBIT", True, brand_col)
    if brand_surf.get_height() >= 3:
        face.blit(brand_surf, brand_surf.get_rect(center=(FACE_W // 2, 24)))

    # ZONE B — dominant price numeral; the concept's win, held at fs=14 and
    # centred between the brand band and the ruled foot.
    _draw_price(face, text, (FACE_W // 2, 43), price_key, price_fill, fs=14)

    # embossed double-rule: each dark rule gets a bright highlight row pressed
    # directly under it so the stock reads physically debossed, not printed.
    rule_y = sc.m(28)
    pygame.draw.line(face, (90, 48, 12), (sc.m(3), rule_y),
                     (FACE_W - sc.m(3), rule_y), max(1, sc.m(1)))
    pygame.draw.line(face, (248, 232, 200), (sc.m(3), rule_y + max(1, sc.m(1))),
                     (FACE_W - sc.m(3), rule_y + max(1, sc.m(1))), max(1, sc.m(1)))
    rule_y2 = rule_y + max(2, sc.m(2)) + max(1, sc.m(1))
    pygame.draw.line(face, (90, 48, 12), (sc.m(3), rule_y2),
                     (FACE_W - sc.m(3), rule_y2), max(1, sc.m(1)))
    pygame.draw.line(face, (248, 232, 200), (sc.m(3), rule_y2 + max(1, sc.m(1))),
                     (FACE_W - sc.m(3), rule_y2 + max(1, sc.m(1))), max(1, sc.m(1)))

    # ZONE C — ruled sub-band label
    f_sub = sc.font(4)
    coins_surf = f_sub.render("COINS", True, coins_col)
    if coins_surf.get_height() >= 4:
        face.blit(coins_surf, coins_surf.get_rect(center=(FACE_W // 2, 70)))

    rot = pygame.transform.rotate(face, TILT)

    # Cord re-anchors to the grommet's true (rotated) top-CENTRE world position,
    # drawn before the face blit so both strands tuck under the eyelet. The
    # strand offset is widened past sc.m(1) because at that spacing the two
    # sc.m(1.5)-wide lines collapse into one — sc.m(1.5) keeps a visible gap.
    gx2, gy2 = _rot_point(FACE_W // 2, 14, FACE_W, FACE_H, tag_center, TILT)
    _cord_strands(surf, (gx2, gy2), knot, sc.m(1.5),
                  cord_a, cord_b, max(1, sc.m(1.5)))

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
ht = hf.render("LEDGER-IVORY — tl4 hang-tag round 2", True, (255, 220, 80))
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

print(f"canvas {canvas.get_width()}x{canvas.get_height()}")

out = "docs/store_price_tl4/ledger_ivory/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
