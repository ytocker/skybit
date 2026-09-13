"""landscape-hero — store_card_v4 concept, round 2 headless render.

An oversized cabochon disc (R=38) domes off the LEFT edge, its rim pushing
through the card frame so the hero reads as "too big to contain"; the item
name rides above a coin-price line in a left-aligned text column to the right,
with a faceted tier gem anchoring the top-right corner.

Round 2 folds in the art-director notes on r1:
  1. Price legibility — Option A: a frosted dark-glass mini-chip (CABO_LO->HI,
     alpha~185) with a 1px gold keyline behind the coin + CREAM numerals, so
     the digits clear ≥7:1 on the body instead of the failed rarity-tinted
     numerals.
  2. The imperceptible indigo-on-indigo vertical divider is gone; the disc's
     right edge already parts the two zones.
  3. Left bleed is SOLD — after the frame is closed, a sliver of the disc's
     glow + gold rim is repainted ON TOP of the left bevel so the dome appears
     to punch through the frame rather than be masked by it.
  4. The text column is widened (x_gut at m(78)); short names (≤8 chars) are
     allowed a larger size instead of shrinking everything to the longest
     name's floor.

Headless (SDL dummy) -> a 3-up RARE / EPIC / LEGENDARY strip at SS (324×200 per
panel, no downscale) on a near-black ground with tier labels below. Not wired
into the live store; writes docs/store_card_v4/landscape-hero/round_2.png.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.hud import _font
from game import store_catalog
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, coin_glyph, _alpha_aura, _glyph_base,
    _cost,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity, NAME_COL,
)

# LOCKED card shell constants (mirrors store_cards.render_card).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R_DISC = 38                    # oversized hero disc — domes off the left edge

CREAM_NUM = (236, 230, 208)    # price numerals: same cream family as the name


def _name_left(surf, name, x_left, cy, max_w):
    """Item name in cream, LEFT-aligned at x_left, with a tight dark keyline.
    Short names sit at a larger size; only long names shrink toward the floor
    so a 5-letter word isn't punished by the longest name in the set."""
    sz = 15.0 if len(name) <= 8 else 14.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 9:
        sz -= 0.5
        f = font(sz)
    nw = _glyph_base(name, f, 0).get_width()
    plain_text(surf, name, f, (x_left + nw // 2, cy), NAME_COL, shadow_a=160,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


def _price_chip_frost(surf, x_left, cy, text, tier_rim):
    """Frosted dark-glass price chip: a CABO_LO->HI rounded pill at alpha~185
    with a 1px gold keyline (the card system's 'dark glass + gold rim'), a coin
    carrying the gold tone, then CREAM numerals so the digits read ≥7:1 on the
    body. LEFT-aligned so it stacks under the name in one column."""
    h = m(19)
    f = font(11.0)
    coin_d = int(h * 0.64)
    padx = m(7)
    gap = m(5)
    nw = _glyph_base(text, f, 0).get_width() + m(2)          # allow faux-bold
    w = padx + coin_d + gap + nw + padx
    r = pygame.Rect(x_left, cy - h // 2, w, h)
    # frosted glass body — translucent so the indigo body still reads behind it
    surf.blit(vgrad_stops(w, h, h // 2, [(0.0, CABO_LO), (1.0, CABO_HI)],
                          alpha=185), r.topleft)
    # a faint top sheen sells the glass, then the fine gold keyline rim
    top_sheen(surf, r, h // 2, m(6), peak=40)
    pygame.draw.rect(surf, (0, 0, 0, 170), r, width=max(1, m(1.2)),
                     border_radius=h // 2)
    pygame.draw.rect(surf, (*CARD_RING_BRIGHT, 205), r.inflate(-m(1), -m(1)),
                     width=max(1, m(1)), border_radius=h // 2 - m(0.5))
    coin_glyph(surf, r.x + padx + coin_d // 2, cy, coin_d // 2)
    tx = r.x + padx + coin_d + gap
    plain_text(surf, text, f, (tx + nw // 2, cy), CREAM_NUM, shadow_a=0,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(0.7))
    return r


def render_card(sid):
    """Draw ONE landscape-hero card onto a fresh SS panel (324×200) and return
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

    # ── oversized hero disc, domed off the LEFT edge ──
    cx = rect.left + m(40)
    cy = rect.centery
    soft_glow(big, cx, cy, m(R_DISC + 2), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R_DISC), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R_DISC) * 1.5))
    cabochon_glass(big, cx, cy, m(R_DISC), tint=pal["gem"])

    # ── text column (right of the disc's right edge) ──
    x_gut = rect.left + m(78)
    max_w = rect.right - x_gut - m(8)
    _name_left(big, store_catalog.name(sid), x_gut, rect.centery + m(1), max_w)
    _price_chip_frost(big, x_gut, rect.centery + m(26),
                      f"{_cost(sid):,}", pal["gem"])

    # ── corner tier gem ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── SELL THE LEFT BLEED (drawn LAST, over the closed frame) ──
    # A sliver of the disc's aura + gold bezel is repainted on top of the left
    # bevel so the dome punches THROUGH the frame instead of being masked flush
    # by it. Composed on an alpha-carrying overlay (BLEND_ADD dies in the
    # transparent headroom), then hard-masked to the leftmost strip so only the
    # disc's leading rim overlaps the bevel — the rest of the card is untouched.
    bleed = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    _alpha_aura(bleed, cx, cy, m(R_DISC + 6), pal["glow"], peak=46, layers=14)
    pygame.draw.circle(bleed, (0, 0, 0, 190), (cx, cy), m(R_DISC), max(1, m(1.4)))
    pygame.draw.circle(bleed, (*CARD_RING_BRIGHT, 235), (cx, cy),
                       m(R_DISC) - m(0.9), max(1, m(1.2)))
    pygame.draw.circle(bleed, (246, 220, 140, 160), (cx, cy),
                       m(R_DISC) - m(1.8), max(1, m(0.7)))
    strip = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(strip, (255, 255, 255, 255),
                     (0, 0, rect.left + m(17), big.get_height()))
    bleed.blit(strip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(bleed, (0, 0))
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
htxt = hfont.render("store_card_v4  —  landscape-hero  —  round 2",
                    True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
for i, (sid, tier) in enumerate(PANELS):
    px = MARGIN + i * (PANEL_W + GAP)
    sheet.blit(render_card(sid), (px, panel_y))
    ltxt = lfont.render(tier, True, (214, 210, 196))
    sheet.blit(ltxt, (px + (PANEL_W - ltxt.get_width()) // 2,
                      panel_y + PANEL_H + (LABEL_H - ltxt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v4/landscape-hero/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
