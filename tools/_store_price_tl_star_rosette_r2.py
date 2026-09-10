"""Round-2 render sheet for the `star-rosette` store-card price badge.

An 8-point heraldic rosette / sunburst seal struck into the card's TOP-LEFT
corner. Eight crisp wedge points (outer r=22, inner notch r=13 — ratio 0.60,
sharp non-cog wedges) around a broad central disc that carries the price
numerals with no coin glyph. Affordable reads as a warm burnished-bronze struck
medallion that lifts clear of the dark card interior; locked reads as a cool
faded-grey stamp — same silhouette, only the metal + hue carry the state.

Implemented as a monkey-patch of store_cards.price_chip: state_chip still feeds
it the price + affordability, but the badge ignores the handed chip anchor and
strikes itself at the fixed top-left corner of the 2x author buffer, so the
default bottom price chip is replaced by the corner seal.

Review-only tooling — never imported by the game.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game import store_data
from game.draw import lerp_color, WHITE, NEAR_BLACK
from game.hud import _font as hud_font

store_data.load()


# ── seal palette (device px in the 2x author buffer) ─────────────────────────
# Affordable = burnished bronze (target lum ~70, a clear +30 above the card
# interior) so the medallion reads as warm struck metal, not a dark smudge.
# Locked = cool faded grey — differs from bronze by HUE and VALUE, so the two
# states stay separable in colourblind viewing. The STAR silhouette is
# byte-identical between states; only the enamel + metal finish switches.
AFFORD = {
    "body":   [(0.0, (90, 70, 38)), (1.0, (64, 48, 22))],
    "rim_dk": (58, 40, 14, 230),
    "rim_hi": (240, 210, 140, 210),
    "disc":   (110, 84, 46),         # brightest field => raised struck boss
    "accent": (210, 170, 80, 150),
    "gloss":  (36, 30, 16),          # warm additive top-left sheen
    "num":    None,                  # None => sovereign coin-metal gradient
}
LOCKED = {
    "body":   [(0.0, (44, 44, 54)), (1.0, (30, 30, 40))],
    "rim_dk": (18, 18, 26, 200),
    "rim_hi": (96, 98, 112, 170),
    "disc":   (40, 40, 50),          # recessed dark centre => faded/inactive
    "accent": (90, 92, 108, 120),
    "gloss":  (12, 12, 16),
    "num":    (120, 122, 138),
}


def _star_pts(cx, cy, ro, ri, n=8, rot=-math.pi / 2):
    """16 vertices alternating outer ro / inner ri, so 8 crisp wedge points sit
    at ro and 8 notches at ri — the sharp medallion silhouette."""
    pts = []
    for i in range(2 * n):
        ang = rot + i * (math.pi / n)
        r = ro if i % 2 == 0 else ri
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    return pts


def _fit_numerals(text, f, field):
    """The disc field is small, so hard-scale the mask down if the abbreviated
    numeral still overshoots — the seal must never spill past the disc."""
    mask = sc._glyph_base(text, f, 0)
    if mask.get_width() > field:
        s = field / mask.get_width()
        mask = pygame.transform.smoothscale(
            mask, (max(1, int(mask.get_width() * s)),
                   max(1, int(mask.get_height() * s))))
    return mask


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    # Abbreviate first — a broad-but-still-small disc reads cleanest with a
    # compact numeral ("1.2k") instead of a five-glyph price crushed to fit.
    def _abbr(text):
        digits = ''.join(c for c in text if c.isdigit())
        if not digits:
            return text
        v = int(digits)
        if v >= 1000:
            frac = (v % 1000) // 100
            return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
        return str(v)
    text = _abbr(text)

    affordable = kw.get("affordable", True)
    pal = AFFORD if affordable else LOCKED

    badge_cx = sc.m(25)              # = 50 in the 2x buffer
    badge_cy = sc.m(25)              # = 50
    ro = sc.m(11)                    # outer point radius = 22
    ri = sc.m(6.5)                   # inner notch radius  = 13 (ratio 0.60)

    abs_pts = _star_pts(badge_cx, badge_cy, ro, ri)
    bbox = pygame.Rect(badge_cx - ro, badge_cy - ro, 2 * ro, 2 * ro)
    loc_pts = [(x - bbox.x, y - bbox.y) for x, y in abs_pts]

    # star silhouette mask reused to clip every fill to the wedge outline.
    mask = pygame.Surface(bbox.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), loc_pts)

    # soft cast shadow so the seal reads struck ONTO the card, not printed flat.
    sh = pygame.Surface(bbox.size, pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120),
                        [(x, y + sc.m(1.4)) for x, y in loc_pts])
    surf.blit(sh, bbox.topleft)

    # enamel body: one vertical ramp poured into the star via BLEND_RGBA_MIN.
    grad = sc.vgrad_stops(bbox.w, bbox.h, 0, pal["body"], 255, gamma=1.05)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, bbox.topleft)

    # top-left gloss ellipse, clipped to the star, added for a faint crown lift.
    gl = pygame.Surface(bbox.size, pygame.SRCALPHA)
    er = pygame.Rect(0, 0, int(bbox.w * 0.72), int(bbox.h * 0.72))
    er.center = (int(bbox.w * 0.36), int(bbox.h * 0.34))
    pygame.draw.ellipse(gl, pal["gloss"], er)
    gl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(gl, bbox.topleft, special_flags=pygame.BLEND_ADD)

    # rim on a scratch SRCALPHA layer so the keyline + bevel alpha-blend cleanly:
    # a bright bevel nudged up-left UNDER a dark keyline = a struck emboss edge.
    # 2px wide — the outer star perimeter is the badge's main shape-carrier at 1x.
    off = max(1, sc.m(0.5))
    rim = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(rim, pal["rim_hi"],
                        [(x - off, y - off) for x, y in abs_pts], 2)
    pygame.draw.polygon(rim, pal["rim_dk"], abs_pts, 2)
    surf.blit(rim, (0, 0))

    # central disc: broad enough to dominate the composition and carry the
    # price; a slightly brighter bronze field so it reads as the raised boss.
    disc_r = sc.m(6.5)
    pygame.draw.circle(surf, pal["disc"], (badge_cx, badge_cy), disc_r)
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(ring, pal["accent"], (badge_cx, badge_cy),
                       sc.m(7), max(1, sc.m(0.7)))
    surf.blit(ring, (0, 0))

    # numerals — sovereign coin-metal (affordable) or dim tarnish (locked).
    # font(7): the enlarged disc lets a smaller glyph fill 80% of the disc.
    # No coin glyph: the seal IS the denomination.
    f = sc.font(7)
    field = int(disc_r * 2 * 0.80)
    nmask = _fit_numerals(text, f, field)
    img = nmask.copy()
    if pal["num"] is None:
        gnum = sc.vgrad_stops(nmask.get_width(), nmask.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img.blit(gnum, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img.fill((*pal["num"], 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(img, img.get_rect(center=(badge_cx, badge_cy)))
    return bbox


sc.price_chip = my_price_chip            # patch BEFORE any draw_card call


# ── render helpers ────────────────────────────────────────────────────────────
def render_card_1x(sid, affordable=True):
    """Full v5 card at native 162x100 — 2x author render then one smoothscale.
    Wallet stubbed so state_chip resolves the affordability state we want."""
    store_data.balance = (lambda: 10 ** 9) if affordable else (lambda: 0)
    variant = sc.PRICE_VARIANT
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def _lum(px):
    return 0.299 * px[0] + 0.587 * px[1] + 0.114 * px[2]


def main():
    out_dir = "/home/user/skybit/docs/store_price_tl_badges/star-rosette"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_2.png")

    pad, gap = 20, 12
    header_h, label_h = 40, 20

    specs = [
        ("skin_mummy",   True,  "MUMMY - EPIC - affordable"),
        ("skin_mummy",   False, "MUMMY - EPIC - locked"),
        ("skin_kitsune", True,  "KITSUNE - LEG - affordable"),
        ("skin_kitsune", False, "KITSUNE - LEG - locked"),
    ]
    cards = [(render_card_1x(sid, aff), lbl) for sid, aff, lbl in specs]
    cw, ch = cards[0][0].get_size()

    # 4x zoom of the top-left seal corner (0..64 in 1x) -> 256x256.
    crop = pygame.Rect(0, 0, 64, 64)
    zdim = (256, 256)
    zoom_a = pygame.transform.scale(
        render_card_1x("skin_mummy", True).subsurface(crop).copy(), zdim)
    zoom_l = pygame.transform.scale(
        render_card_1x("skin_mummy", False).subsurface(crop).copy(), zdim)

    row1_w = cw * 4 + gap * 3
    zw, zh = zoom_a.get_size()
    row2_w = zw + gap + zw
    canvas_w = pad * 2 + max(row1_w, row2_w)
    row1_y = header_h
    row2_y = row1_y + ch + label_h + gap
    canvas_h = row2_y + zh + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))
    hf = hud_font(26, True)
    lf = hud_font(15)
    canvas.blit(hf.render("STAR-ROSETTE / PRICE SEAL  -  top-left price badge r2",
                          True, (236, 232, 250)), (pad, 8))

    x = pad
    for card, lbl in cards:
        canvas.blit(card, (x, row1_y))
        canvas.blit(lf.render(lbl, True, (206, 202, 224)),
                    (x, row1_y + ch + 3))
        x += cw + gap

    x = pad
    canvas.blit(zoom_a, (x, row2_y))
    canvas.blit(lf.render("4x zoom - mummy affordable", True, (206, 202, 224)),
                (x, row2_y + zh + 3))
    x += zw + gap
    canvas.blit(zoom_l, (x, row2_y))
    canvas.blit(lf.render("4x zoom - mummy locked", True, (206, 202, 224)),
                (x, row2_y + zh + 3))

    pygame.image.save(canvas, out)

    # ── pixel verification ───────────────────────────────────────────────────
    aff = render_card_1x("skin_mummy", True)
    lok = render_card_1x("skin_mummy", False)
    pa = aff.get_at((25, 25))
    pl = lok.get_at((25, 25))
    la, ll = _lum(pa), _lum(pl)
    assert pa[0] > 70, f"affordable seal not bronze (R={pa[0]} <= 70)"
    assert abs(la - ll) > 30, f"states too close in lum ({la:.0f} vs {ll:.0f})"
    print("verify affordable (25,25):", tuple(pa), f"lum={la:.0f}")
    print("verify locked     (25,25):", tuple(pl), f"lum={ll:.0f}")

    print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")


if __name__ == "__main__":
    main()
