"""enamel-pin — store_card_v4_r2 concept, round 1 headless render.

A soft-enamel PIN BADGE read of the disc-led card. The lower name plate is
recast as a polished metal strip: a gold bevel frame enclosing a FLAT, matte
tier-tinted enamel channel, with the item name set in RAISED metal caps so the
letters look proud of the enamel. The price abandons its pill entirely — bare
coin + numerals are STAMPED naked into the lit right collar over a soft glow
pad, the boldest/most minimal denomination treatment in the v4 set.

The register is deliberately flat: enamel is a single matte value (no glassy
noise, no gradient banding) so the strip reads clean at 1x. Everything else
holds the locked v4 shell + hero-disc + gem-crest stack.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200 panels, no downscale) plus a real-scale 1x strip for the at-scale
legibility read. Not wired into the live store; writes
docs/store_card_v4_r2/enamel-pin/round_1.png.
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
from game.draw import lerp_color
from game.store_cards import (
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    cabochon, cabochon_glass, blit_thumb, facet_gem, plain_text, soft_glow,
    coin_glyph, _glyph_base, _rarity, font, m, SS,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_DEEP, CARD_RING_BRIGHT,
    GEM_R, RARITY, MYSTERY,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Logical hero-disc radius — the near-full-width v4 disc.
R = 34

# Cream shared by the price numerals (copied verbatim from portrait_vignette_r2)
# so the naked denomination never has to carry legibility on gold.
CREAM_LABEL = (236, 230, 208)

# A lighter METAL cream for the raised name caps — brighter than CREAM_LABEL so
# the letters read as polished metal proud of the matte enamel channel.
CREAM_METAL = (250, 245, 220)


def _hero_specular(surf, cx, cy, r):
    """A guaranteed high-value glass specular on the upper-left rim, drawn OVER
    the cabochon glass so EVERY skin keeps a lit crescent — dark heroes (e.g.
    skin_tophat) no longer read as a flat low-value blob under the dome."""
    ec = r + m(3)
    edge = pygame.Surface((ec * 2 + m(2), ec * 2 + m(2)), pygame.SRCALPHA)
    steps = max(2, m(4))
    for k in range(steps):
        a = int(210 * (1 - k / steps))
        rk = r - m(1) - k
        if rk <= 0:
            break
        pygame.draw.arc(edge, (255, 250, 234, a),
                        (ec - rk, ec - rk, rk * 2, rk * 2),
                        math.radians(110), math.radians(198), max(1, m(1)))
    surf.blit(edge, (cx - ec, cy - ec), special_flags=pygame.BLEND_ADD)
    # a single hot pip upper-left so there is always a crisp catch-light.
    pr = max(1, int(r * 0.17))
    pip = pygame.Surface((pr * 2 + m(2), pr * 2 + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 235), (pr + m(1), pr + m(1)), pr)
    off = int(r * 0.66)
    surf.blit(pip, (cx - pr - off, cy - pr - off),
              special_flags=pygame.BLEND_ADD)


def _raised_caps(surf, txt, f, center, max_w):
    """The item name in RAISED metal caps: auto-shrunk to `max_w`, then stamped
    thrice — a dark drop offset down-right, a bright bevel offset up-left, and
    the metal-cream face on top — so each glyph reads as a polished cap standing
    proud of the flat enamel (a one-px directional bevel, not a flat outline)."""
    sz = 9.5
    while _glyph_base(txt, f, 0).get_width() > max_w and sz > 6.0:
        sz -= 0.5
        f = font(sz)
    off = max(1, m(0.9))
    cx, cy = center
    # dark drop (down-right) seats the cap in the enamel; bright bevel (up-left)
    # is the lit metal edge; metal-cream face rides on top.
    plain_text(surf, txt, f, (cx + off, cy + off), (28, 20, 10),
               shadow_a=0, weight=m(0.9))
    plain_text(surf, txt, f, (cx - off, cy - off), (255, 250, 232),
               shadow_a=0, weight=m(0.9))
    plain_text(surf, txt, f, (cx, cy), CREAM_METAL, shadow_a=0, weight=m(0.9))


def _enamel_channel_color(pal):
    """A single FLAT matte enamel value on the tier deep->gem ramp — pulled to
    mid so the channel reads as coloured enamel, not glass, and stays uniform
    (no gradient banding) at 1x."""
    return lerp_color(pal["deep"], pal["gem"], 0.42)


def render_card(sid):
    """Draw ONE enamel-pin card onto a fresh SS panel (324x200) and return it
    (drawn directly at SS, no smoothscale)."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price_str = f"{store_catalog.cost(sid):,}"

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, rect.y + m(37)          # top headroom; lower rim tucks

    # ── SHELL (locked order) ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── HERO DISC ──
    soft_glow(big, cx, cy, m(R + 3), pal["glow"], 34, layers=9)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=55)
    blit_thumb(big, sid, cx, cy, m(R) * 0.66)
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])
    _hero_specular(big, cx, cy, m(R))              # luminance-independent catch-light

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── PRICE — bare coin + numerals STAMPED into the right collar, no pill.
    #    A tiny warm glow pad is laid FIRST so the naked digits stay legible
    #    against the lit collar; placed mid-collar, clear of gem + band. ──
    collar_cx = (cx + m(R) + rect.right - m(6)) // 2
    price_cy = rect.y + m(45)
    collar_w = rect.right - m(6) - (cx + m(R))
    soft_glow(big, collar_cx, price_cy, m(15), (255, 236, 196), 30, layers=8)
    coin_r = m(4.5)
    coin_cy = price_cy - m(8)
    coin_glyph(big, collar_cx, coin_cy, coin_r)
    pf = font(9.0)
    dcy = price_cy + m(6)
    while _glyph_base(price_str, pf, 0).get_width() > collar_w * 0.92 and \
            pf.get_height() > m(11):
        pf = font(pf.get_height() / SS - 0.5)
    plain_text(big, price_str, pf, (collar_cx, dcy), CREAM_LABEL,
               shadow_a=0, weight=m(1.0), keyline=(8, 8, 18), kw=m(0.7))

    # ── NAME BAND — enamel PIN STRIP flush at the bottom: a polished gold metal
    #    frame enclosing a FLAT matte tier-enamel channel, name in raised caps. ──
    bar_h = m(17)
    bar = pygame.Rect(rect.x + m(3), rect.bottom - m(3) - bar_h,
                      rect.w - m(6), bar_h)
    brad = m(5)
    # polished metal strip (the pin body): a compact gold ramp so it reads as a
    # struck metal edge round the enamel.
    big.blit(vgrad_stops(bar.w, bar.h, brad,
                         [(0.0, (248, 216, 142)), (0.5, (212, 166, 86)),
                          (1.0, (118, 80, 28))], 255, gamma=1.05),
             bar.topleft)
    # FLAT matte enamel channel, inset so the gold metal border frames it.
    ch = bar.inflate(-m(7), -m(7))
    crad = max(1, brad - m(3))
    pygame.draw.rect(big, _enamel_channel_color(pal), ch, border_radius=crad)
    # a thin dark keyline seats the enamel below the metal lip (reads recessed).
    pygame.draw.rect(big, lerp_color(pal["deep"], (0, 0, 0), 0.45), ch,
                     width=max(1, m(0.8)), border_radius=crad)
    # the strip's own bevel: dark outer contact keyline UNDER a bright top-left
    # gold bevel so the metal frame reads polished + raised off the card.
    bevel_rim(big, bar, brad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(1.5)))

    _raised_caps(big, name.upper(), font(9.5), ch.center, ch.w - m(6))

    return big


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_tophat"),
    ("EPIC",      "skin_prism"),
    ("LEGENDARY", "skin_kitsune"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS   # 324 x 200 (SS panels, no downscale)
MARGIN = 10
GUTTER = 8
HEADER_H = 30
FOOTER_H = 22
STRIP_LABEL_H = 20
STRIP_H = CARD_H

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = (MARGIN + HEADER_H + PANEL_H + FOOTER_H + STRIP_LABEL_H + STRIP_H
           + MARGIN)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(22, True)
ffont = _font(18, True)
sfont = _font(15, True)
htxt = hfont.render("store_card_v4_r2 — enamel-pin — round 1", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel = render_card(sid)
    panels.append(panel)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# 1x real-scale strip so the enamel + raised caps + naked price are judged at
# the live card size (the flat-at-1x legibility read this concept is about).
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1x, 162x100)", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    left = px + (PANEL_W - CARD_W) // 2
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (left, strip_y))

out = "/home/user/skybit/docs/store_card_v4_r2/enamel-pin/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
