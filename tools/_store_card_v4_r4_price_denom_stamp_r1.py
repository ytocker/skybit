"""denom-stamp — store_card_v4_r4_price concept, round 1 headless render.

The only price direction with a PORTRAIT coin-over-numeral stack: a compact
vertical denomination stamp hugging the disc/right-column seam. Its upright
silhouette is a deliberate counter to every horizontal price pill/plate/deboss
concept, so the price reads as a minted token rather than a label.

Base card is the locked name_v4 filament-core card, replicated verbatim; only
the price element is swapped for the stamp.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import math
import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import store_catalog
from game.hud import _font
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, coin_glyph, _glyph_base, _stamp_bold,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
)

CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36

# The rarity read lives ONLY in the glow beneath + the rim warmth; the indigo
# body is constant so the stamp stays a stable "mint" object across the grid and
# tier escalation is felt as heat, not a body recolour.
_TIER_PEAK = {"common": 16, "rare": 26, "epic": 36, "legendary": 48}
_TIER_WARM = {"common": 0.16, "rare": 0.26, "epic": 0.36, "legendary": 0.52}


# ── locked name element (filament-core r2) ────────────────────────────────────
_FILAMENT_RINGS = ((3, 90, (255, 236, 190)),
                   (2, 160, (255, 236, 190)),
                   (1, 210, (255, 255, 252)))


def _name_filament_core(big, name, cx, cy, max_w):
    sz = 13.5
    f = font(sz)
    while sum(f.size(c)[0] for c in name) > max_w and sz > 9.0:
        sz -= 0.5
        f = font(sz)

    advances = [f.size(c)[0] for c in name]
    total_w = sum(advances)
    x = cx - total_w // 2
    for char, adv in zip(name, advances):
        glyph_cx = x + adv // 2
        tile = _stamp_bold(_glyph_base(char, f, 0), m(0.8))
        tw, th = tile.get_size()
        bx, by = glyph_cx - tw // 2, cy - th // 2
        for rad, alpha, col in _FILAMENT_RINGS:
            tinted = tile.copy()
            tinted.fill((*col, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            steps = max(8, rad * 10)
            for s in range(steps):
                ang = 2 * math.pi * s / steps
                dx = int(round(rad * math.cos(ang)))
                dy = int(round(rad * math.sin(ang)))
                big.blit(tinted, (bx + dx, by + dy))
        x += adv

    plain_text(big, name, f, (cx, cy), (250, 244, 225), shadow_a=0,
               weight=m(0.8), keyline=(8, 8, 20), kw=m(0.5))


def _neutral_band(big, rect, plinth_top, rad):
    ph = rect.bottom - plinth_top
    band = vgrad_stops(rect.w, ph, 0, [(0.0, (28, 24, 44)), (1.0, (14, 12, 26))], 255)
    mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h), border_radius=rad)
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (rect.left, plinth_top))
    seam = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(seam, (*CARD_RING_BRIGHT, 80),
                     (rect.left, plinth_top - max(1, m(1))),
                     (rect.right - 1, plinth_top - max(1, m(1))), max(1, m(1)))
    big.blit(seam, (0, 0))
    pygame.draw.line(big, (6, 5, 12), (rect.left, plinth_top),
                     (rect.right - 1, plinth_top), max(1, m(1)))


# ── denom-stamp price element ─────────────────────────────────────────────────
def _denom_stamp_price(big, cx, cy, price, tier, pal):
    """A vertical denomination stamp: coin stacked over the numeral inside a
    rounded indigo tablet with a warm beveled rim. The upright token shape is the
    hero, so the numeral is allowed to be small — but legibility is the key risk,
    so the tablet WIDENS (within the locked bounds) to seat the price at a
    readable hero size before the font is ever shrunk."""
    numeral = f"{price:,}"
    h = m(28)
    rad = m(3)
    side_pad = m(3.5)
    coin_d = m(14)

    # Width flexes to seat the numeral at a hero-readable size: start at the
    # locked m(22), grow toward the m(26) ceiling to fit, only then drop the font.
    sz = 7.0
    f = font(sz)
    nw = _glyph_base(numeral, f, 0).get_width()
    w = min(m(26), max(m(22), nw + 2 * side_pad))
    while nw + 2 * side_pad > w and sz > 5.0:
        sz -= 0.5
        f = font(sz)
        nw = _glyph_base(numeral, f, 0).get_width()

    stamp = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    # Rarity halo beneath (peak escalates by tier); body stays constant indigo.
    soft_glow(big, cx, cy, m(18), pal["glow"], _TIER_PEAK.get(tier, 30), layers=8)

    # Grounding drop shadow so the token sits proud of the card face.
    drop_shadow(big, stamp, rad, blur=m(5), alpha=150, dy=m(2))

    # Constant dark-indigo body — the stable "mint metal" of the token.
    body = vgrad_stops(w, h, rad, [(0.0, (34, 36, 78)), (1.0, (14, 15, 40))],
                       255, gamma=1.12)
    big.blit(body, stamp.topleft)

    # Warm rim biased toward the tier hue so the rarity carries in the edge too.
    rim_bright = lerp_color(CARD_RING_BRIGHT, pal["gem"], _TIER_WARM.get(tier, 0.3))
    pygame.draw.rect(big, (4, 5, 16), stamp, width=max(1, m(1.2)), border_radius=rad)
    bevel_rim(big, stamp, rad, CARD_RING_DEEP, (*rim_bright, 232), w=max(1, m(1.4)))

    # A hairline divider between the coin cell and the numeral cell so the stack
    # reads as two stamped registers, not a coin floating over text.
    divy = cy + m(1)
    div = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(div, (*rim_bright, 70),
                     (stamp.left + side_pad, divy),
                     (stamp.right - side_pad, divy), max(1, m(0.6)))
    big.blit(div, (0, 0))

    # Coin stacked in the upper register.
    coin_glyph(big, cx, cy - m(7), coin_d // 2)

    # Numeral seated in the lower register, near-white so it pops off the indigo.
    plain_text(big, numeral, f, (cx, cy + m(9)), (240, 240, 230), shadow_a=0,
               weight=m(0.9), keyline=(8, 8, 20), kw=m(0.5))


def render_card(sid):
    pal = RARITY.get(_rarity(sid), MYSTERY)
    tier = _rarity(sid)
    name = store_catalog.name(sid)
    price = store_catalog.cost(sid)

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)

    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15), rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235), w=max(1, m(2.0)))

    cx = rect.left + m(40)
    cy = rect.y + m(38)
    plinth_top = rect.y + m(72)
    _neutral_band(big, rect, plinth_top, rad)

    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3), pal["gem"], pal["deep"])

    # Stamp hugs the disc/right-column seam; cx nudged to m(90) so its left edge
    # clears the disc's hard right edge (~x=164 device) with a few px of air.
    _denom_stamp_price(big, rect.left + m(90), rect.y + m(50), price, tier, pal)

    _name_filament_core(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26))
    return big


out = "/home/user/skybit/docs/store_card_v4_r4_price/denom-stamp/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
card = render_card("skin_prism")   # EPIC tier
pygame.image.save(card, out)
print("saved", out, card.get_size())
