"""Round-1 render sheet for the `price-scroll` store-card price badge.

A tiny parchment scroll seated in the card's TOP-LEFT corner — the only
warm-light body in the price-badge set, a deliberate fantasy-RPG-shop tonal
outlier to the dark-enamel siblings. The scroll is a STACKED build (panel +
two turned rolls + a wax seal), not a single silhouette polygon: a warm vellum
panel carries the price, capsule rolls cap it top and bottom with a cast
roll-shadow onto the vellum (so the rolls read as turned edges, not hairlines),
and an oxblood wax seal is the accent in place of a coin glyph.

Locked state stays legible WITHOUT flipping the body: the vellum desaturates to
parchment-grey, the rolls and wax darken, and the numerals dim — the scroll is
plainly "sealed/inert" while its shape and dimensions are unchanged.

Implemented as a monkey-patch of store_cards.price_chip. price_chip is called by
state_chip only for the non-equipped states, and it normally strikes the price
chip at the card's bottom centre; this patch ignores that anchor and instead
draws the scroll at the fixed top-left badge zone (cx=cy=m(25)=50 in the 2x
author buffer). Affordability is driven deterministically off the variant the
harness threads through draw_card ("locked" => sealed), not the live wallet, so
both states appear on one sheet.

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
import game.store_data as sd
from game.draw import lerp_color, WHITE, NEAR_BLACK
from game.hud import _font as hud_font

sd.load()


# ── vellum / scroll palette (device-px RGB) ───────────────────────────────────
# Warm parchment body when affordable; a cool parchment-grey when sealed so the
# locked scroll reads inert WITHOUT any body-shape change.
VELLUM_TOP,  VELLUM_BOT  = (232, 214, 176), (210, 188, 146)
VELLUM_GREY_TOP, VELLUM_GREY_BOT = (206, 198, 182), (184, 176, 158)
ROLL_TOP,    ROLL_BOT    = (196, 172, 130), (168, 142, 98)
ROLL_LOCK_TOP, ROLL_LOCK_BOT = (162, 152, 134), (150, 140, 122)
WAX_TOP,     WAX_BOT     = (150, 42, 40),  (104, 24, 26)
WAX_LOCK_TOP, WAX_LOCK_BOT = (96, 58, 52), (64, 34, 32)
NUM_LOCK = (110, 92, 70)
ROLL_SHADOW = (68, 48, 26)               # warm dark cast onto the vellum


def _disc_gradient(d, top, bot):
    """A circular disc filled by a vertical two-stop ramp (wax seal body)."""
    surf = pygame.Surface((d, d), pygame.SRCALPHA)
    for y in range(d):
        c = lerp_color(top, bot, y / max(1, d - 1))
        pygame.draw.line(surf, (*c, 255), (0, y), (d - 1, y))
    mask = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (d // 2, d // 2), d // 2)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return surf


def _roll_shadow_band(w, h):
    """A short vertical fade (alpha 80 -> 0) used as the shadow the turned roll
    casts onto the vellum. Cast, not a curl hairline — this is what sells the
    roll as a rounded edge lifting off the panel."""
    band = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        a = int(80 * (1 - y / max(1, h)))
        pygame.draw.line(band, (*ROLL_SHADOW, a), (0, y), (w - 1, y))
    return band


def _roll_highlight_arc(rw, rh):
    """A 1px white specular arc on the top-left of a roll, blitted at alpha 60 so
    the turned edge catches the card's top-left key light."""
    arc = pygame.Surface((rw, rh), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(1), sc.m(1), rw - sc.m(2), rh - sc.m(2))
    pygame.draw.arc(arc, WHITE, rect, math.radians(95), math.radians(178),
                    max(1, sc.m(1)))
    arc.set_alpha(60)
    return arc


# Vellum panel inner width the price must clear (40px panel less a margin each
# side). font(8.5) overflows a 5-digit price, so the size auto-shrinks to fit —
# a tiny scroll can't carry big numerals.
_NUM_MAX_W = sc.m(17)


def _fit_price_mask(text):
    """The glyph mask, auto-shrunk from font(8.5) until a 5-digit price clears the
    vellum panel. Returns (mask, size)."""
    sz = 8.5
    while sz > 5.0:
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(sz), 0), sc.m(0.8))
        if mask.get_width() <= _NUM_MAX_W:
            return mask
        sz -= 0.5
    return sc._stamp_bold(sc._glyph_base(text, sc.font(sz), 0), sc.m(0.8))


def _numerals_affordable(surf, text, cx, cy):
    """Sovereign coin-metal fill poured into the glyph mask via BLEND_RGBA_MULT,
    with a m(0.5) dark stamp offset behind it: gold-on-cream is low contrast, so
    the dark under-stamp gives the numerals a struck edge that seats them on the
    vellum. The gold face stays on top, so the numeral reads warm and light."""
    mask = _fit_price_mask(text)
    grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                          sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
    img = mask.copy()
    img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    r = img.get_rect(center=(cx, cy))

    stamp = mask.copy()
    stamp.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
    stamp.set_alpha(140)
    surf.blit(stamp, (r.x + sc.m(0.5), r.y + sc.m(0.5)))
    surf.blit(img, r)


def _numerals_locked(surf, text, cx, cy):
    """Dim ink on the desaturated vellum — legible, plainly inert."""
    mask = _fit_price_mask(text)
    img = mask.copy()
    img.fill((*NUM_LOCK, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(img, img.get_rect(center=(cx, cy)))


def _draw_scroll(surf, bx, by, text, affordable):
    """The whole stacked scroll, authored around the badge centre (bx, by) in the
    2x buffer. Panel + top roll + bottom roll (each with a cast shadow onto the
    vellum + a top-left highlight arc) + wax seal + numerals."""
    v_top, v_bot = (VELLUM_TOP, VELLUM_BOT) if affordable else (VELLUM_GREY_TOP,
                                                                VELLUM_GREY_BOT)
    r_top, r_bot = (ROLL_TOP, ROLL_BOT) if affordable else (ROLL_LOCK_TOP,
                                                            ROLL_LOCK_BOT)

    # geometry (device px; brief coords are centred on 50,50 => offsets from bx,by)
    pan = pygame.Rect(bx - 20, by - 14, 40, 28)          # x30..70  y36..64
    top_roll = pygame.Rect(bx - 21, by - 19, 42, 9)      # x29..71  y31..40
    bot_roll = pygame.Rect(bx - 21, by + 10, 42, 9)      # x29..71  y60..69

    # soft seating shadow so the parchment sits on the card rather than floating
    seat = pygame.Surface((pan.w + sc.m(8), pan.h + sc.m(16)), pygame.SRCALPHA)
    pygame.draw.ellipse(seat, (0, 0, 0, 60), seat.get_rect())
    surf.blit(seat, (pan.x - sc.m(4), pan.y - sc.m(4)))

    # 1) vellum panel
    surf.blit(sc.vgrad_stops(pan.w, pan.h, sc.m(1.5),
                             [(0.0, v_top), (1.0, v_bot)], 255), pan.topleft)

    # 2/3) rolls (deeper ramp = turned edge) + cast shadow onto the panel + arc
    for roll, cast_y, arc_flip in ((top_roll, top_roll.bottom, False),
                                   (bot_roll, bot_roll.top - sc.m(3), True)):
        rad = roll.h // 2
        surf.blit(sc.vgrad_stops(roll.w, roll.h, rad,
                                 [(0.0, r_top), (1.0, r_bot)], 255), roll.topleft)
        band = _roll_shadow_band(pan.w, sc.m(3))
        if arc_flip:
            band = pygame.transform.flip(band, False, True)
        surf.blit(band, (pan.x, cast_y))
        surf.blit(_roll_highlight_arc(roll.w, roll.h), roll.topleft)

    # 4) numerals — nudged UP so the wax seal clears below
    if affordable:
        _numerals_affordable(surf, text, bx, by - 3)
    else:
        _numerals_locked(surf, text, bx, by - 3)

    # 5) wax seal (oxblood) — the accent, in place of a coin glyph
    d = sc.m(8)
    wax_top, wax_bot = (WAX_TOP, WAX_BOT) if affordable else (WAX_LOCK_TOP,
                                                              WAX_LOCK_BOT)
    disc = _disc_gradient(d, wax_top, wax_bot)
    # seated 2px below the brief's nominal so the disc's top edge clears the panel
    # centre — the numeral/vellum reads there, the wax is the lower accent.
    wcx, wcy = bx, by + 10
    # tiny bright top-left pip so the wax reads glossy/domed
    pip_a = 150 if affordable else 90
    pygame.draw.circle(disc, (255, 210, 200, pip_a),
                       (int(d * 0.34), int(d * 0.32)), max(1, sc.m(1.1)))
    # dark keyline so the disc seats on the vellum
    pygame.draw.circle(disc, (40, 12, 14, 200), (d // 2, d // 2), d // 2,
                       max(1, sc.m(0.8)))
    surf.blit(disc, (wcx - d // 2, wcy - d // 2))


# ── monkey-patch: price_chip becomes the top-left scroll ──────────────────────
def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    badge_cx = sc.m(25)                 # = 50 in the 2x author buffer
    badge_cy = sc.m(25)                 # = 50
    affordable = (variant != "locked")  # harness threads state via the variant
    _draw_scroll(surf, badge_cx, badge_cy, text, affordable)
    return pygame.Rect(badge_cx - sc.m(21), badge_cy - sc.m(19),
                       sc.m(42), sc.m(38))


sc.price_chip = my_price_chip           # patch BEFORE any draw_card call


# =============================================================================
# Render
# =============================================================================
def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def zoom_badge(card_1x, scale=4):
    """4x nearest-neighbour crop of the top-left badge (x0..64, y0..64 in 1x)."""
    src = pygame.Rect(0, 0, 64, 64)
    crop = card_1x.subsurface(src.clip(card_1x.get_rect())).copy()
    return pygame.transform.scale(crop, (64 * scale, 64 * scale))


def verify():
    aff = render_card_1x("skin_mummy", True)
    lock = render_card_1x("skin_mummy", False)
    pa = aff.get_at((25, 25))
    pl = lock.get_at((25, 25))
    sa = pa[0] + pa[1] + pa[2]
    sl = pl[0] + pl[1] + pl[2]
    print("affordable (25,25):", tuple(pa), "sum", sa)
    print("locked     (25,25):", tuple(pl), "sum", sl)
    assert sa > 200, f"affordable badge not warm/light at (25,25): {tuple(pa)}"
    assert sl < sa, f"locked badge should be dimmer than affordable: {sl} vs {sa}"
    print("VERIFICATION PASSED")


def main():
    verify()

    out_dir = "/home/user/skybit/docs/store_price_tl_badges/price-scroll"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")

    specs = [
        ("skin_mummy",   True,  "MUMMY · EPIC · affordable"),
        ("skin_mummy",   False, "MUMMY · EPIC · locked"),
        ("skin_kitsune", True,  "KITSUNE · LEGENDARY · affordable"),
        ("skin_kitsune", False, "KITSUNE · LEGENDARY · locked"),
    ]
    cards = [(render_card_1x(sid, aff), lbl) for sid, aff, lbl in specs]

    zooms = [
        (zoom_badge(cards[0][0]), "badge 4x · MUMMY affordable"),
        (zoom_badge(cards[1][0]), "badge 4x · MUMMY locked"),
    ]

    pad, gap, header_h, label_h = 20, 12, 40, 20
    cw, ch = 162, 100
    zsz = 256

    row1_w = cw * 4 + gap * 3
    row1_y = header_h + pad
    row2_y = row1_y + ch + label_h + gap * 2
    row2_w = zsz * 2 + gap
    content_w = max(row1_w, row2_w)
    canvas_w = pad * 2 + content_w
    canvas_h = row2_y + zsz + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(26, True)
    lf = hud_font(13)
    canvas.blit(hf.render("store price — top-left badge · price-scroll · round 1",
                          True, (236, 232, 250)), (pad, pad // 2 + 2))

    def put_label(text, cx, y):
        img = lf.render(text, True, (208, 204, 226))
        canvas.blit(img, (cx - img.get_width() // 2, y))

    x = pad + (content_w - row1_w) // 2
    for card, lbl in cards:
        canvas.blit(card, (x, row1_y))
        put_label(lbl, x + cw // 2, row1_y + ch + 3)
        x += cw + gap

    x = pad + (content_w - row2_w) // 2
    for z, lbl in zooms:
        canvas.blit(z, (x, row2_y))
        put_label(lbl, x + zsz // 2, row2_y + zsz + 3)
        x += zsz + gap

    pygame.image.save(canvas, out)
    print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")


if __name__ == "__main__":
    main()
