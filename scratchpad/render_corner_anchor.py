"""Round 1 render for the corner-anchor store card concept (3-panel strip)."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem, vgrad, vgrad_stops,
    drop_shadow, bevel_rim, top_sheen, contact_shadow, plain_text, font, m, SS,
    soft_glow, coin_glyph, CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _glyph_base, _rarity, _cost,
    CARD_RAD,
)
from game.draw import lerp_color
from game import store_catalog


def _fit_name(surf, name, cx, cy, max_w):
    """Auto-fit the item name in the trapezoid field, 9.5 -> 7.5."""
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

    # ── diagonal shadow crease (bronze/indigo — splits disc from text) ─────
    # Drawn on its own alpha surface so the overlapping band lines blend
    # against the card body instead of overwriting it.
    crease_color = lerp_color(CARD_B, (60, 44, 20), 0.35)
    crease = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    for offset, alpha in [(-2, 30), (-1, 60), (0, 90), (1, 60), (2, 30)]:
        p0 = (rect.left + m(8) + offset, rect.y + m(32))
        p1 = (rect.right - m(8) + offset, rect.bottom - m(8))
        pygame.draw.line(crease, (*crease_color, alpha), p0, p1, max(1, m(1)))
    big.blit(crease, (0, 0))

    # ── disc anchored bottom-left ──────────────────────────────────────────
    cx = rect.left + m(30)
    cy = rect.bottom - m(24)
    # tier aura behind the disc (before the cabochon)
    soft_glow(big, cx, cy, m(52), pal["glow"], 70)
    soft_glow(big, cx, cy, m(50), pal["glow"], 90)
    cabochon(big, cx, cy, m(38), CABO_LO, CABO_HI, CARD_RING_BRIGHT, 200)
    blit_thumb(big, sid, cx, cy, int(m(38) * 1.5))
    cabochon_glass(big, cx, cy, m(38))

    # ── gem badge top-right corner ─────────────────────────────────────────
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── trapezoid text field (upper-right, above the crease) ───────────────
    _fit_name(big, store_catalog.name(sid), rect.right - m(40),
              rect.y + m(32), m(70))
    coin_cx = rect.right - m(55)
    coin_cy = rect.y + m(55)
    coin_glyph(big, coin_cx, coin_cy, m(5))
    price = f"{_cost(sid):,}"
    pf = font(8.5)
    nw = _glyph_base(price, pf, 0).get_width()
    tx = coin_cx + m(5) + m(4) + nw // 2
    plain_text(big, price, pf, (tx, coin_cy), pal["gem"], shadow_a=140,
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

out = "/home/user/skybit/docs/store_card_v4/corner-anchor/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(strip, out)
print("saved", out, strip.get_size())
