"""denom-stamp — store_card_v4_r4_price concept, round 2.

All five art-director notes from the r1 critique addressed:

1. Hierarchy inverted: coin shrunk to m(8) logical diameter (from m(14)); numeral
   sized to fill the available width first, reaching ~9 logical font height for
   "1,400" — the number is now the loudest element in the stamp.

2. Tracking added: _glyph_base is called with tracking=1 device per inter-glyph
   gap so each digit resolves cleanly at these small dimensions, and the sizing
   loop accounts for that extra width so nothing overflows.

3. Disc gap opened: stamp cx moved from m(90) to m(93), placing the stamp left
   edge at m(80.5) from rect.left vs the disc hard right edge at m(76) — 4.5
   logical clearance at the coin's widest latitude.

4. Bright hairline removed: the full-width bright rule is gone. The natural gap
   between the coin icon and the numeral (≈ m(4)–m(5) of breathing room) already
   reads as two distinct registers without any line.

5. Kept unchanged: m(25) body width, dark-indigo body fill, value-contrast cream
   numeral, rarity carried via soft_glow peak escalation and rim warmth toward
   pal["gem"].
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

# Rarity read lives ONLY in glow intensity + rim warmth; indigo body is constant
# so the stamp is a stable mint-token across the grid — escalation is felt as heat.
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
    """Vertical denomination stamp: coin icon over a price numeral inside a
    rounded indigo tablet. The numeral is the primary read; the coin is a small
    denomination icon that supports it, not competes with it."""
    numeral = f"{price:,}"
    h = m(28)
    rad = m(3)
    # Tight side padding so the numeral can grow as large as the locked m(25)
    # width allows before the sizing loop ever has to shrink the font.
    side_pad = m(1.5)
    # Coin is the small supporting icon — shrunk to ~m(8) diameter so the
    # numeral below it reads as the dominant element in the stamp.
    coin_d = m(8)

    # Width locked at m(25). Numeral is sized down from 9.5 only if it can't
    # fit with 1-device-per-gap tracking included in the width estimate.
    w = m(25)
    sz = 9.5
    f = font(sz)
    # Include tracking=1 in the width estimate so the loop lands at the exact
    # size that fits rendered glyphs, not a theoretical unspaced width.
    nw = _glyph_base(numeral, f, 1).get_width()
    while nw + 2 * side_pad > w and sz > 7.0:
        sz -= 0.5
        f = font(sz)
        nw = _glyph_base(numeral, f, 1).get_width()

    stamp = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    # Rarity halo beneath; peak escalates so epic/legendary feel hotter.
    soft_glow(big, cx, cy, m(18), pal["glow"], _TIER_PEAK.get(tier, 30), layers=8)

    # Grounding drop shadow so the token reads as a proud, slightly lifted mint.
    drop_shadow(big, stamp, rad, blur=m(5), alpha=150, dy=m(2))

    # Constant dark-indigo body — the stable mint-metal of the denomination token.
    body = vgrad_stops(w, h, rad, [(0.0, (34, 36, 78)), (1.0, (14, 15, 40))],
                       255, gamma=1.12)
    big.blit(body, stamp.topleft)

    # Warm rim biased toward the tier hue so rarity escalates in the edge too.
    rim_bright = lerp_color(CARD_RING_BRIGHT, pal["gem"], _TIER_WARM.get(tier, 0.3))
    pygame.draw.rect(big, (4, 5, 16), stamp, width=max(1, m(1.2)), border_radius=rad)
    bevel_rim(big, stamp, rad, CARD_RING_DEEP, (*rim_bright, 232), w=max(1, m(1.4)))

    # No divider line: the natural breathing room between the small coin above
    # and the large numeral below already reads as two distinct registers.

    # Coin in upper register — small denomination icon, symmetric in the top half.
    coin_glyph(big, cx, cy - m(7), coin_d // 2)

    # Numeral in lower register — hero element. 1-device-per-gap tracking keeps
    # each glyph individually legible at this small stamp scale.
    plain_text(big, numeral, f, (cx, cy + m(7)), (240, 240, 230), shadow_a=0,
               tracking=1, weight=m(0.9), keyline=(8, 8, 20), kw=m(0.5))


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

    # Stamp cx at m(93): stamp left edge = m(93) - m(12.5) = m(80.5), disc hard
    # right edge = m(40)+m(36) = m(76) → 4.5 logical clearance at coin latitude.
    _denom_stamp_price(big, rect.left + m(93), rect.y + m(50), price, tier, pal)

    _name_filament_core(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26))
    return big


out = "/home/user/skybit/docs/store_card_v4_r4_price/denom-stamp/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
card = render_card("skin_prism")   # EPIC tier — 1,400 coins
pygame.image.save(card, out)
print("saved", out, card.get_size())
