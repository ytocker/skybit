"""full-bleed-disc — store_card_v4 concept, round 1 headless render.

The thumbnail IS the card: one oversized cabochon (R≈m(62)) domes corner-to-
corner, bleeding past the body edges and clipped by the card's rounded-rect
mask so the glass reads as the whole face. The item name rides a STRAIGHT
full-width frosted bar across the lower third; the price is bare numerals struck
into the short bottom chord of the disc, curve-masked to the circle so they
appear embedded in the glass. A faceted tier gem anchors the top-right corner.

Headless (SDL dummy) → a 3-up RARE / EPIC / LEGENDARY strip at SS (324×200 per
panel, no downscale) on a near-black ground with tier labels below. Not wired
into the live store; writes docs/store_card_v4/full-bleed-disc/round_1.png.
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
    plain_text, font, m, SS, soft_glow, coin_glyph,                    # noqa: F401
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
)

# LOCKED card shell constants (mirrors store_cards.render_card).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R_FULL = 62                    # disc radius — domes past the body, then clipped


def _name_autofit(surf, name, cx, cy, max_w):
    """Item name in cream with a tight dark keyline, shrunk to fit the bar."""
    sz = 13.0
    f = font(sz)
    while f.render(name, True, (255, 255, 255)).get_width() > max_w and sz > 8:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cx, cy), (250, 248, 240), shadow_a=150,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


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

    # ── full-bleed disc + labels on a body-clipped overlay ──
    # Everything that bleeds past the body (the oversized dome + the full-width
    # frosted bar) is composed on one overlay, then masked ONCE to the body's
    # rounded-rect so the glass is cropped by the card silhouette instead of the
    # raw surface edges.
    overlay = pygame.Surface(big.get_size(), pygame.SRCALPHA)

    soft_glow(overlay, cx, cy, m(R_FULL + 2), pal["glow"], 24, layers=8)
    cabochon(overlay, cx, cy, m(R_FULL), CABO_LO, CABO_HI, CARD_RING_BRIGHT, 200)
    blit_thumb(overlay, sid, cx, cy, int(m(R_FULL) * 1.4))
    cabochon_glass(overlay, cx, cy, m(R_FULL))

    # frosted name bar — STRAIGHT, full card width (bleeds ±m(6), clipped later).
    # Lifted off the bottom so a genuine disc chord survives beneath it to carry
    # the price, per the brief's "short bottom chord below the name bar".
    bar_h = m(20)
    chord_h = m(18)
    bar_y = rect.bottom - chord_h - bar_h
    bar_surf = vgrad_stops(rect.w + m(12), bar_h, m(4),
                           [(0.0, CABO_LO), (1.0, CABO_HI)], alpha=210)
    overlay.blit(bar_surf, (rect.x - m(6), bar_y))
    # a fine gold keyline on the bar's crown so the frost reads as a set panel.
    pygame.draw.line(overlay, (*CARD_RING_BRIGHT, 150),
                     (rect.x - m(6), bar_y), (rect.right + m(6), bar_y),
                     max(1, m(1)))
    _name_autofit(overlay, store_catalog.name(sid), cx, bar_y + bar_h // 2,
                  rect.w - m(12))

    # price — bare numerals struck into the bottom chord, curve-masked to the
    # disc circle so the digits read as embedded in the glass.
    price_layer = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    price_y = rect.bottom - m(9)
    pf = font(11.0)
    txt = "480"
    tw = pf.render(txt, True, (255, 255, 255)).get_width()
    coin_d = m(11)
    gap = m(4)
    total = coin_d + gap + tw
    coin_cx = cx - total // 2 + coin_d // 2
    coin_glyph(price_layer, coin_cx, price_y, coin_d // 2)
    plain_text(price_layer, txt, pf,
               (coin_cx + coin_d // 2 + gap + tw // 2, price_y),
               pal["gem"], shadow_a=0, weight=m(0.9), keyline=(6, 6, 16),
               kw=m(0.7))
    cmask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(cmask, (255, 255, 255, 255), (cx, cy), m(R_FULL))
    price_layer.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    overlay.blit(price_layer, (0, 0))

    # clip the whole overlay to the body rounded-rect, then drop it on the card.
    bmask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(bmask, (255, 255, 255, 255), rect, border_radius=rad)
    overlay.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(overlay, (0, 0))

    # ── final frame pass over the bled disc, then the corner tier gem ──
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])
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
htxt = hfont.render("store_card_v4  —  full-bleed-disc  —  round 1",
                    True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
for i, (sid, tier) in enumerate(PANELS):
    px = MARGIN + i * (PANEL_W + GAP)
    sheet.blit(render_card(sid), (px, panel_y))
    ltxt = lfont.render(tier, True, (214, 210, 196))
    sheet.blit(ltxt, (px + (PANEL_W - ltxt.get_width()) // 2,
                      panel_y + PANEL_H + (LABEL_H - ltxt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v4/full-bleed-disc/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
