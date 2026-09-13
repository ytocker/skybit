"""full-bleed-disc — store_card_v4 concept, round 2 headless render.

The thumbnail IS the card: one oversized cabochon (R≈m(62)) domes corner-to-
corner, bleeding past the body edges and clipped by the card's rounded-rect mask
so the glass reads as the whole face. Round 2 kills the lifted-bar + curve-masked
price chord: a SINGLE dark-glass bar now seats flush at the body bottom (name
left, price right, one row), the disc domes uninterrupted above it, and the disc
is deliberately set in a bezel — a tier-colour aura halo plus a bright gold inner
keyline ring frame the ~side gutters so the glass no longer dissolves into the
indigo body. Price is one warm gold across all tiers (rarity reads only through
gem + aura). A dark backing bead protects the corner tier gem from the busy glass.

Headless (SDL dummy) → a 3-up RARE / EPIC / LEGENDARY strip at SS (324×200 per
panel, no downscale) on a near-black ground with tier labels below. Not wired
into the live store; writes docs/store_card_v4/full-bleed-disc/round_2.png.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color                                       # noqa: F401
from game.hud import _font
from game import store_catalog
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, coin_glyph, _glyph_base, _cost,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
)

# LOCKED card shell constants (mirrors store_cards.render_card).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R_FULL = 62                    # disc radius — domes past the body, then clipped

# One warm gold for the price across ALL tiers so it never collides with the
# per-tier gem/aura hue; rarity reads only through the gem + the disc aura.
PRICE_GOLD = CARD_RING_BRIGHT
# Dark-glass bar: a deep indigo panel that owns being a scrim, crowned by a gold
# keyline so it reads as a mounted plate, not a muddy smear.
BAR_TOP = (20, 22, 46)
BAR_BOT = (7, 8, 22)


def _name_left(surf, name, left_x, cy, max_w):
    """Item name in cream, LEFT-anchored on the bar, auto-shrunk to fit."""
    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.5:
        sz -= 0.5
        f = font(sz)
    w = _glyph_base(name, f, 0).get_width()
    plain_text(surf, name, f, (left_x + w // 2, cy), (246, 240, 220),
               shadow_a=140, weight=m(0.9), keyline=(6, 6, 16), kw=m(0.9))


def _price_right(surf, sid, right_x, cy):
    """coin_glyph + warm-gold numerals, RIGHT-anchored on the bar. Returns the
    left edge of the price group so the name lane can size against it."""
    txt = f"{_cost(sid):,}"
    pf = font(11.0)
    tw = _glyph_base(txt, pf, 0).get_width()
    coin_d = m(12)
    gap = m(4)
    num_cx = right_x - tw // 2
    coin_cx = right_x - tw - gap - coin_d // 2
    coin_glyph(surf, coin_cx, cy, coin_d // 2)
    plain_text(surf, txt, pf, (num_cx, cy), PRICE_GOLD, shadow_a=0,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(0.8))
    return coin_cx - coin_d // 2


def render_card(sid):
    """Draw ONE full-bleed-disc card onto a fresh SS panel (324×200) and return
    it (authored directly at SS, no smoothscale)."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)

    # ── card shell (locked order) ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    cx, cy = rect.centerx, rect.centery
    R = m(R_FULL)

    # Tier aura FIRST, on the opaque body so BLEND_ADD registers (on the
    # transparent overlay it left alpha=0 and dissolved). A boosted peak floods
    # the side gutters with tier colour so the dome edge visibly halos.
    soft_glow(big, cx, cy, R + m(13), pal["glow"], 72, layers=9)

    # ── full-bleed disc + bar on a body-clipped overlay ──
    # Everything that bleeds past the body (the oversized dome + the flush bar)
    # is composed on one overlay, then masked ONCE to the body rounded-rect so
    # the glass is cropped by the card silhouette, not the raw surface edges.
    overlay = pygame.Surface(big.get_size(), pygame.SRCALPHA)

    cabochon(overlay, cx, cy, R, CABO_LO, CABO_HI, CARD_RING_BRIGHT, 200)
    blit_thumb(overlay, sid, cx, cy, int(R * 1.4))
    cabochon_glass(overlay, cx, cy, R)
    # a bright gold inner keyline just OUTSIDE the disc so the dome reads as a
    # dome deliberately set into a bezel frame, not one dissolving into indigo.
    pygame.draw.circle(overlay, (*CARD_RING_BRIGHT, 225), (cx, cy), R + m(2),
                       max(1, m(1)))

    # ── one dark-glass bar, flush to the body bottom, full width ──
    bar_h = m(20)
    bar_y = rect.bottom - bar_h
    bar = vgrad_stops(rect.w + m(12), bar_h, 0,
                      [(0.0, BAR_TOP), (1.0, BAR_BOT)], alpha=226)
    overlay.blit(bar, (rect.x - m(6), bar_y))
    # gold crown keyline along the bar's top edge — mounted plate, not a smear.
    pygame.draw.line(overlay, (*CARD_RING_BRIGHT, 220),
                     (rect.x - m(6), bar_y), (rect.right + m(6), bar_y),
                     max(1, m(1.6)))

    cy_bar = bar_y + bar_h // 2
    price_left = _price_right(overlay, sid, rect.right - m(10), cy_bar)
    name_left_x = rect.x + m(10)
    _name_left(overlay, store_catalog.name(sid), name_left_x, cy_bar,
               price_left - name_left_x - m(8))

    # clip the whole overlay to the body rounded-rect, then drop it on the card.
    bmask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(bmask, (255, 255, 255, 255), rect, border_radius=rad)
    overlay.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(overlay, (0, 0))

    # ── final frame pass over the bled disc, then the corner tier gem ──
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    # a solid near-black backing bead so the gem separates from the busy glass.
    gx, gy = rect.right - m(19), rect.y + m(19)
    pygame.draw.circle(big, (8, 8, 20), (gx, gy), m(GEM_R + 5))
    facet_gem(big, gx, gy, m(GEM_R + 3), pal["gem"], pal["deep"])
    return big


# ── review strip ───────────────────────────────────────────────────────────────
PANELS = [
    ("skin_tophat", "RARE"),
    ("skin_prism", "EPIC"),
    ("skin_kitsune", "LEGENDARY"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS       # 324 × 200
MARGIN = 10
GAP = 8
HEADER_H = 26
LABEL_H = 22

sheet_w = MARGIN * 2 + PANEL_W * 3 + GAP * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + LABEL_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(20, True)
lfont = _font(18, True)
htxt = hfont.render("store_card_v4  —  full-bleed-disc  —  round 2",
                    True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
for i, (sid, tier) in enumerate(PANELS):
    px = MARGIN + i * (PANEL_W + GAP)
    sheet.blit(render_card(sid), (px, panel_y))
    ltxt = lfont.render(tier, True, (214, 210, 196))
    sheet.blit(ltxt, (px + (PANEL_W - ltxt.get_width()) // 2,
                      panel_y + PANEL_H + (LABEL_H - ltxt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v4/full-bleed-disc/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
