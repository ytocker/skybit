"""Round-1 render sheet for the `star-rosette` store-card price badge.

An 8-point heraldic rosette / sunburst seal struck into the card's TOP-LEFT
corner. Eight crisp wedge points (outer r=22, inner notch r=11 — ratio 0.50,
sharp non-cog wedges) in a dark enamel body from the corner-shield family; a
central disc carries the price numerals with no coin glyph. Affordable reads as
a luxury certification seal — warm gold points, bright sovereign numerals;
locked reads as a faded official stamp — nearly-black body, dull rim, dim
numerals — so the silhouette is identical and only the finish carries the state.

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
# Warm-gold certification seal vs. faded official stamp; the STAR silhouette is
# byte-identical between states — only the enamel + metal finish switches.
AFFORD = {
    "body":   [(0.0, (26, 20, 32)), (1.0, (18, 14, 24))],
    "rim_dk": (60, 44, 18, 220),
    "rim_hi": (230, 200, 130, 200),
    "disc":   (38, 30, 48),
    "accent": (180, 140, 60, 120),
    "gloss":  (22, 19, 12),          # warm additive top-left sheen (~alpha 18)
    "num":    None,                  # None => sovereign coin-metal gradient
}
LOCKED = {
    "body":   [(0.0, (18, 14, 22)), (1.0, (12, 10, 16))],
    "rim_dk": (80, 60, 18, 160),
    "rim_hi": (110, 90, 50, 140),
    "disc":   (24, 20, 32),
    "accent": (110, 90, 50, 90),
    "gloss":  (10, 9, 6),
    "num":    (130, 110, 80),
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
    """Widest catalog prices are 4-5 glyphs; the inner notch field is tiny, so
    drop the comma before tracking, then hard-scale the mask to seal the fit."""
    mask = sc._glyph_base(text, f, 0)
    if mask.get_width() > field:
        mask = sc._glyph_base(text.replace(",", ""), f, 0)
    if mask.get_width() > field:
        s = field / mask.get_width()
        mask = pygame.transform.smoothscale(
            mask, (max(1, int(mask.get_width() * s)),
                   max(1, int(mask.get_height() * s))))
    return mask


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = kw.get("affordable", True)
    pal = AFFORD if affordable else LOCKED

    badge_cx = sc.m(25)              # = 50 in the 2x buffer
    badge_cy = sc.m(25)              # = 50
    ro = sc.m(11)                    # outer point radius = 22
    ri = sc.m(5.5)                   # inner notch radius  = 11

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
    off = max(1, sc.m(0.5))
    rim = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(rim, pal["rim_hi"],
                        [(x - off, y - off) for x, y in abs_pts], 1)
    pygame.draw.polygon(rim, pal["rim_dk"], abs_pts, 1)
    surf.blit(rim, (0, 0))

    # central disc: a slightly lighter enamel field so the numerals separate,
    # ringed by a thin gold accent.
    pygame.draw.circle(surf, pal["disc"], (badge_cx, badge_cy), sc.m(5))
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(ring, pal["accent"], (badge_cx, badge_cy),
                       sc.m(5.5), max(1, sc.m(0.6)))
    surf.blit(ring, (0, 0))

    # numerals — sovereign coin-metal (affordable) or dim tarnish (locked),
    # fitted into the notch field. No coin glyph: the seal IS the denomination.
    f = sc.font(8)
    field = int(ri * 1.9)
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


def main():
    out_dir = "/home/user/skybit/docs/store_price_tl_badges/star-rosette"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")

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
    canvas.blit(hf.render("store price top-left badge - star-rosette r1", True,
                          (236, 232, 250)), (pad, 8))

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
    bg = (8, 8, 20)
    aff = render_card_1x("skin_mummy", True)
    lok = render_card_1x("skin_mummy", False)
    pa = aff.get_at((25, 25))
    pl = lok.get_at((25, 25))
    assert (pa[0], pa[1], pa[2]) != bg, "seal absent on affordable card"
    assert sum(pl[:3]) < sum(pa[:3]), "locked seal not darker than affordable"
    print("verify affordable (25,25):", tuple(pa))
    print("verify locked     (25,25):", tuple(pl))

    print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")


if __name__ == "__main__":
    main()
