"""store_card_v4_r3 — concept BOOK-SPINE, round 1 review render.

Floating-medallion take: the glass disc sits as a cover medallion in the
upper-left, clear of a leather book-spine strip at the card's foot. The name is
gold-foil letterpressed into the spine; the price hangs from a brass eyelet as a
small leather hang-tag in the upper-right margin. Headless-only exploration —
writes a labelled 3-tier strip under docs/, never wired into the live store.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")

import math
import random

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, coin_glyph, _glyph_base, _name, _cost,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
)

CARD_W, CARD_H = 162, 100
CARD_RAD = 17
R = 34                       # cover-medallion disc radius (logical)

GOLD_FOIL = (240, 208, 122)  # warm letterpress gold for the spine name
TAG_CREAM = (248, 244, 230)


def _leather_base(pal):
    """Cool indigo leather tone with a restrained tier hint. The strong blue
    anchor + a blue floor guarantee the spine stays cool even for the warm-deep
    legendary tier — never brown/tan."""
    base = lerp_color((22, 22, 58), pal["deep"], 0.30)
    base = lerp_color(base, (16, 16, 46), 0.30)
    # blue floor: never let the blue channel fall below red, so it can't warm up.
    r, g, b = base
    return (r, g, max(b, r + 8))


def _soft_shadow_circle(surf, cx, cy, r, alpha=120, layers=7):
    """Feathered round shadow blitted (not drawn) so it blends onto the opaque
    card body instead of punching its per-pixel alpha."""
    pad = m(4)
    s = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    for i in range(layers, 0, -1):
        rr = int(r * i / layers)
        a = int(alpha * (1 - (i - 1) / layers) ** 1.7)
        if rr <= 0 or a <= 0:
            continue
        pygame.draw.circle(s, (0, 0, 0, a), (c, c), rr)
    surf.blit(s, (cx - c, cy - c))


def _leather_band(surf, sid, rect, rad, pal):
    """The book-spine strip at the card foot: a cool indigo leather grain framed
    by a gilt double-rule, carrying the gold-foil letterpressed item name."""
    # Cool indigo base with only a hint of the tier's deep — a strong blue anchor
    # keeps even warm-deep tiers (legendary) reading as cool leather, never
    # brown/tan.
    base = _leather_base(pal)
    b_top = lerp_color(base, WHITE, 0.07)
    b_bot = lerp_color(base, NEAR_BLACK, 0.5)

    inset = max(1, m(2))
    band_h = m(15)
    band = pygame.Rect(rect.left + inset, rect.bottom - band_h - inset,
                       rect.w - 2 * inset, band_h)
    brad = max(1, rad - inset)

    body = vgrad_stops(band.w, band.h, 0, [(0.0, b_top), (1.0, b_bot)], 255,
                       gamma=1.12)

    # Leather grain: thin, low-opacity, slightly-diagonal streaks on an overlay so
    # the alpha blends instead of overwriting the band's opaque fill.
    grain = pygame.Surface((band.w, band.h), pygame.SRCALPHA)
    rng = random.Random(abs(hash(sid)) & 0xFFFF)
    n = 15
    for i in range(n):
        y = int((i + 0.5) / n * band.h + rng.uniform(-1.4, 1.4))
        a = rng.randint(12, 32)
        lit = rng.random() < 0.5
        col = (lerp_color(base, WHITE, 0.5) if lit
               else lerp_color(base, NEAR_BLACK, 0.6))
        slope = rng.uniform(-0.05, 0.05)
        pygame.draw.line(grain, (*col, a), (0, y),
                         (band.w, int(y + slope * band.w)), max(1, m(0.6)))
    body.blit(grain, (0, 0))

    # Gilt double-rule: a bright gold rule paired with a finer dimmer one, top and
    # bottom, so the spine reads as a tooled leather panel.
    g = max(1, m(0.9))
    thin = max(1, m(0.6))
    dim = lerp_color(CARD_RING_BRIGHT, NEAR_BLACK, 0.45)
    for yy, order in ((m(2), 1), (band.h - m(2), -1)):
        pygame.draw.line(body, CARD_RING_BRIGHT, (0, yy), (band.w, yy), g)
        y2 = yy + order * (g + max(1, m(1.4)))
        pygame.draw.line(body, dim, (0, y2), (band.w, y2), thin)

    # Round only the bottom corners to sit inside the card's gold bevel frame.
    mask = pygame.Surface((band.w, band.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, band.w, band.h),
                     border_bottom_left_radius=brad,
                     border_bottom_right_radius=brad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, band.topleft)

    # Gold-foil letterpress name: warm gold fill + a tight dark keyline pressed
    # into the leather. Auto-shrink to fit the spine width.
    name = _name(sid)
    max_w = band.w - m(10)
    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.5:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (band.centerx, band.centery - m(0.5)), GOLD_FOIL,
               shadow_a=0, weight=m(0.8), keyline=(18, 12, 4), kw=m(0.9))
    return band


def _eyelet(surf, cx, cy, r):
    """A brass eyelet: a dark seat, concentric gold rings on the CARD_RING ramp,
    and a dark bore at the centre for the hang string to thread."""
    pad = m(3)
    seat = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    pygame.draw.circle(seat, (0, 0, 0, 150), (c, c), r + m(1))
    surf.blit(seat, (cx - c, cy - c))
    pygame.draw.circle(surf, CARD_RING_DEEP, (cx, cy), r, max(1, m(1.3)))
    pygame.draw.circle(surf, CARD_RING_BRIGHT, (cx, cy), r - m(1.2), max(1, m(1.1)))
    pygame.draw.circle(surf, (250, 226, 150), (cx, cy), r - m(2.4), max(1, m(0.7)))
    pygame.draw.circle(surf, (10, 10, 22), (cx, cy), max(1, r - m(3.4)))


def _hang_tag(surf, cx, top, price, pal):
    """A small leather hang-tag: a pointed pentagon in the spine's leather tone
    with a gilt keyline, carrying the coin glyph + price numerals in cream."""
    base = _leather_base(pal)
    t_top = lerp_color(base, WHITE, 0.09)
    t_bot = lerp_color(base, NEAR_BLACK, 0.45)

    text = f"{price:,}"
    f = font(7.5)
    nw = _glyph_base(text, f, 0).get_width()
    coin_d = m(9)
    padx = m(4)
    gap = m(3)
    tw = padx + coin_d + gap + nw + padx
    th = m(21)
    peak = m(5)                                # pointed top where the string ties

    surf_tag = vgrad_stops(tw, th, 0, [(0.0, t_top), (1.0, t_bot)], 255, gamma=1.1)
    poly = [(tw / 2, 0), (tw, peak), (tw, th), (0, th), (0, peak)]
    pmask = pygame.Surface((tw, th), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    surf_tag.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    x0 = int(cx - tw / 2)
    # Drop a soft shadow so the tag reads as dangling, not glued.
    sh = pygame.Surface((tw, th), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 90),
                        [(px, py + m(1.5)) for px, py in poly])
    surf.blit(sh, (x0, top))
    surf.blit(surf_tag, (x0, top))
    abspoly = [(x0 + px, top + py) for px, py in poly]
    pygame.draw.polygon(surf, (6, 6, 16), abspoly, width=max(1, m(1.2)))
    pygame.draw.polygon(surf, (*CARD_RING_BRIGHT, 180), abspoly, width=max(1, m(0.7)))
    # eyelet hole punched through the tag's point
    pygame.draw.circle(surf, (8, 8, 18), (int(cx), top + int(peak * 0.7)),
                       max(1, m(1.6)))
    pygame.draw.circle(surf, (*CARD_RING_BRIGHT, 200), (int(cx), top + int(peak * 0.7)),
                       max(1, m(1.6)), max(1, m(0.5)))

    cy = top + peak + (th - peak) // 2 + m(1)
    x = x0 + padx
    coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
    x += coin_d + gap
    plain_text(surf, text, f, (x + nw // 2, cy), TAG_CREAM, shadow_a=0,
               weight=m(0.8), keyline=(14, 10, 4), kw=m(0.6))
    return x0, top, tw, th


def draw_card(big, sid, rect):
    pal = RARITY[_rarity(sid)]
    rad = m(CARD_RAD)

    # ── locked shell ──────────────────────────────────────────────────────────
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── leather spine strip (drawn first so the medallion floats over it) ──────
    _leather_band(big, sid, rect, rad, pal)

    # ── cover medallion: floating disc, upper-left, clear of the band ─────────
    cx = rect.left + m(38)
    cy = rect.top + m(36)
    _soft_shadow_circle(big, cx, cy + m(3), m(R), alpha=120)
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── tier gem badge, top-right corner ──────────────────────────────────────
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── brass eyelet + hang-tag, upper-right margin (left of + below the gem) ──
    ex = rect.right - m(30)
    ey = rect.top + m(38)
    tag_x0, tag_top, tw, th = _hang_tag(big, ex, ey + m(9), _cost(sid), pal)
    # short arc "string" from the eyelet down to the tag's point
    tie_y = tag_top + int(m(5) * 0.7)
    arc_r = pygame.Rect(ex - m(4), ey, m(8), (tie_y - ey) * 2)
    pygame.draw.arc(big, (206, 172, 96), arc_r, math.radians(200),
                    math.radians(340), max(1, m(1.2)))
    _eyelet(big, ex, ey, m(6))


def render_card(sid):
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    inset = m(6)
    rect = pygame.Rect(inset, inset, CARD_W * SS - 2 * inset,
                       CARD_H * SS - 2 * inset)
    draw_card(big, sid, rect)
    return pygame.transform.smoothscale(big, (CARD_W, CARD_H))


def main():
    tiers = [("skin_tophat", "RARE"), ("skin_prism", "EPIC"),
             ("skin_kitsune", "LEGENDARY")]
    margin, gap, header, footer = 10, 8, 26, 22
    W = margin * 2 + 3 * CARD_W + 2 * gap
    Hh = margin + header + CARD_H + footer + margin
    strip = pygame.Surface((W, Hh))
    strip.fill((8, 8, 20))

    hfont = _font(17, True)
    lab = hfont.render("store_card_v4_r3  —  book-spine  —  round 1", True,
                       (232, 224, 244))
    strip.blit(lab, (margin, (header - lab.get_height()) // 2 + margin // 2))

    tfont = _font(13, True)
    for i, (sid, word) in enumerate(tiers):
        x = margin + i * (CARD_W + gap)
        y = margin + header
        strip.blit(render_card(sid), (x, y))
        t = tfont.render(word, True, (206, 198, 222))
        strip.blit(t, (x + (CARD_W - t.get_width()) // 2, y + CARD_H + 5))

    out = "/home/user/skybit/docs/store_card_v4_r3/book-spine/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(strip, out)
    print("saved", out, strip.get_size())


if __name__ == "__main__":
    main()
