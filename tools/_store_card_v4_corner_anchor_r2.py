"""Round 2 (final) render for the corner-anchor store card concept.

Addresses the art-director ITERATE notes: the disc + its tier aura are painted
onto a scratch surface and hard-masked to the card's rounded-rect body (nothing
bleeds into the grid gutter); name + price drop clear of the corner gem into the
upper-right field; the diagonal crease becomes a readable VALUE EDGE via a
dark shadow band on the disc side plus a bright light-catch keyline on the text
side; the aura shrinks to just beyond the disc rim.
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem, vgrad,
    drop_shadow, bevel_rim, top_sheen, contact_shadow, plain_text, font, m, SS,
    coin_glyph, CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _glyph_base, _rarity, _cost,
    CARD_RAD,
)
from game import store_catalog


def _ring_glow(surf, cx, cy, radius, color, peak, layers=10):
    """A feathered radial halo drawn with NORMAL alpha-carry blits (not
    BLEND_ADD) so it survives the rounded-rect mask below — BLEND_ADD would add
    RGB but leave alpha=0 on the transparent scratch, erasing the aura when it's
    clipped. Linear falloff keeps real alpha out at the rim so the thin ring
    beyond the opaque disc still reads as a tier halo."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak * (1 - (i - 1) / layers))
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1))


def _fit_name(surf, name, cx, cy, max_w):
    """Auto-fit the item name in the upper-right field, 9.5 -> 7.5."""
    sz = 9.5
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.5:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cx, cy), (250, 248, 240), shadow_a=150,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(0.9))


def draw_corner_anchor(big, sid, rect):
    pal = RARITY.get(_rarity(sid), MYSTERY)
    rad = m(CARD_RAD)

    # ── card shell (locked order) ──────────────────────────────────────────
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── diagonal crease as a VALUE EDGE ────────────────────────────────────
    # A dark shadow band offset toward the disc + a thin bright light-catch
    # keyline offset toward the text: the darker->lighter differential across
    # the ~4px band reads as a genuine fold, where a single flat line did not.
    p0 = (rect.left + m(8), rect.y + m(32))
    p1 = (rect.right - m(8), rect.bottom - m(8))
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dy) or 1.0
    ux_disc, uy_disc = -dy / ln, dx / ln            # perpendicular toward disc
    ux_text, uy_text = dy / ln, -dx / ln            # perpendicular toward text
    crease = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    od = SS * 2                                       # 2px toward the disc
    pygame.draw.line(crease, (4, 4, 12, 100),
                     (p0[0] + ux_disc * od, p0[1] + uy_disc * od),
                     (p1[0] + ux_disc * od, p1[1] + uy_disc * od), SS * 3)
    ot = SS * 1                                       # 1px toward the text
    pygame.draw.line(crease, (*CARD_RING_BRIGHT, 90),
                     (p0[0] + ux_text * ot, p0[1] + uy_text * ot),
                     (p1[0] + ux_text * ot, p1[1] + uy_text * ot), max(1, SS))
    big.blit(crease, (0, 0))

    # ── disc + aura, hard-masked to the body ───────────────────────────────
    # The disc anchors bottom-left and deliberately overflows the body rect;
    # painting it (and its shrunk tier aura) onto a scratch and MIN-masking to
    # the rounded body keeps every pixel inside the card — no bleed into the
    # transparent tile / grid gutter.
    cx = rect.left + m(30)
    cy = rect.bottom - m(24)
    scratch = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    _ring_glow(scratch, cx, cy, m(46), pal["glow"], 160)
    cabochon(scratch, cx, cy, m(38), CABO_LO, CABO_HI, CARD_RING_BRIGHT, 200)
    blit_thumb(scratch, sid, cx, cy, int(m(38) * 1.5))
    cabochon_glass(scratch, cx, cy, m(38))
    mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=m(17))
    scratch.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(scratch, (0, 0))

    # ── gem badge top-right corner ─────────────────────────────────────────
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── name + price grouped in the upper-right, clear of the gem floor ────
    cy_name = rect.y + m(52)
    cy_price = rect.y + m(72)
    name_cx = rect.right - m(42)
    _fit_name(big, store_catalog.name(sid), name_cx, cy_name, m(58))

    price = f"{_cost(sid):,}"
    pf = font(8.5)
    nw = _glyph_base(price, pf, 0).get_width()
    coin_d = m(10)
    gap = m(4)
    total = coin_d + gap + nw
    x0 = name_cx - total // 2
    coin_glyph(big, x0 + coin_d // 2, cy_price, m(5))
    tx = x0 + coin_d + gap + nw // 2
    plain_text(big, price, pf, (tx, cy_price), (250, 248, 240), shadow_a=140,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(0.8))


PANELS = [("skin_tophat", "RARE"), ("skin_prism", "EPIC"),
          ("skin_kitsune", "LEGENDARY")]

CW, CH = 324, 200
GAP = 8
MARGIN = 10
LABEL_H = 22
BG = (8, 8, 20)

strip_w = MARGIN * 2 + CW * 3 + GAP * 2
strip_h = MARGIN * 2 + CH + LABEL_H
strip = pygame.Surface((strip_w, strip_h))
strip.fill(BG)

lf = font(9)
for i, (sid, tier) in enumerate(PANELS):
    big = pygame.Surface((CW, CH), pygame.SRCALPHA)
    rect = pygame.Rect(12, 12, 300, 176)
    draw_corner_anchor(big, sid, rect)
    x = MARGIN + i * (CW + GAP)
    strip.blit(big, (x, MARGIN))
    lbl = lf.render(tier, True, (232, 226, 240))
    strip.blit(lbl, lbl.get_rect(center=(x + CW // 2, MARGIN + CH + LABEL_H // 2)))

out = "/home/user/skybit/docs/store_card_v4/corner-anchor/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(strip, out)
print("saved", out, strip.get_size())
