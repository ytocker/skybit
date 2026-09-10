"""forge-plate — store_card_v4_r4 concept, round 1 headless render.

Visual thesis: the card's bottom band is a hammered forged-iron plate, and the
price is a heat-glow deboss struck straight into that plate.  The numeral is the
single brightest ember value on the whole card — a near-white-hot core grading
to tier colour at its edges — ringed by a dark scorch halo so it reads as hot
iron pressed into cold metal, not a neon tube laid on top.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200 panels, no downscale).  Not wired into the live store; writes
docs/store_card_v4_r4/forge-plate/round_1.png.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import math
import random
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
    plain_text, font, m, SS, soft_glow, coin_glyph, _glyph_base,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36

# Warm off-white for the engraved name — reads as pale cast iron, not gilt.
NAME_COL = (210, 205, 195)


def _dark_scorch(surf, cx, cy, radius, color, peak_alpha, layers=8):
    """soft_glow's feathered falloff, but composited NORMAL (not additive) so a
    near-black colour actually darkens the iron beneath it.  This is what makes
    the scorch ring read as burned/scored metal rather than a lit halo."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.8)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1))


def _forge_band(big, rect, plinth_top, pal, seed):
    """Hammered forged-iron plate filling plinth_top -> card bottom.

    A near-black->graphite vertical iron gradient, clipped to the card's rounded
    bottom corners.  Sparse ember specks — deterministically seeded, concentrated
    in the plate's lower half — read as metal that was recently worked and hasn't
    fully cooled.  A 1px lit top bevel + 1px dark bottom shadow seat the plate as
    a discrete raised slab.
    """
    ph = rect.bottom - plinth_top
    rad = m(CARD_RAD)
    band = vgrad_stops(rect.w, ph, 0,
                       [(0.0, (18, 17, 20)), (1.0, (10, 9, 11))], 255)
    body_mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(body_mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h),
                     border_radius=rad)
    band.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (rect.left, plinth_top))

    # Ember specks — seeded so the plate is identical every render.  Weighted
    # toward the lower half (rnd()**0.6 biases y downward) where cooling iron
    # would still be glowing.
    rnd = random.Random(seed)
    n = rnd.randint(8, 12)
    inset = m(6)
    for _ in range(n):
        ex = rect.left + inset + rnd.random() * (rect.w - 2 * inset)
        ey = plinth_top + (0.5 + 0.5 * rnd.random() ** 0.6) * ph
        er = m(rnd.choice((1, 1, 2)))
        soft_glow(big, int(ex), int(ey), er, pal["glow"],
                  rnd.randint(20, 35), layers=4)

    # Top lit bevel + bottom dark shadow seat the plate.
    seam = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(seam, (150, 146, 150, 150),
                     (rect.left + m(2), plinth_top),
                     (rect.right - m(2), plinth_top), max(1, m(1)))
    pygame.draw.line(seam, (0, 0, 0, 170),
                     (rect.left + m(2), rect.bottom - m(1)),
                     (rect.right - m(2), rect.bottom - m(1)), max(1, m(1)))
    big.blit(seam, (0, 0))


def _forge_price(big, txt, center, pal):
    """Heat-glow deboss: the brightest ember value on the card.

    Layered floor-to-ceiling:
      1. Dark scorch halo — normal-composite near-black dabs strung along the
         numeral, so the surrounding iron reads as burned/scored.
      2. Additive glyph-shaped bloom in tier glow colour — fattens the numeral
         edges so they grade toward tier hue.
      3. A tight additive soft_glow core stack (radius m(5), peak 180) under
         each digit-cluster — the white-hot heart of the strike.
      4. The glyph itself stroked in lerp(glow, WHITE, 0.7) on top, crisp.
    """
    sz = 13.0
    f = font(sz)
    max_w = m(52)                                    # clear of disc + card edge
    while _glyph_base(txt, f, 0).get_width() > max_w and sz > 8.0:
        sz -= 0.5
        f = font(sz)
    base = _glyph_base(txt, f, 0)
    r = base.get_rect(center=center)

    n = 5
    xs = [int(r.left + r.width * k / (n - 1)) for k in range(n)]

    # 1) scorch halo pressed into the iron (normal composite, dark).
    for sx in xs:
        _dark_scorch(big, sx, center[1], m(8), (7, 6, 8), 140)

    # 2) additive glyph-shaped ember bloom (tier hue at the edges).
    glow = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    tint = base.copy()
    tint.fill((*pal["glow"], 255), special_flags=pygame.BLEND_RGBA_MULT)
    for off, a in ((m(2.2), 55), (m(1.4), 90), (m(0.7), 140)):
        for ang in range(0, 360, 45):
            dx = int(round(off * math.cos(math.radians(ang))))
            dy = int(round(off * math.sin(math.radians(ang))))
            t = tint.copy()
            t.set_alpha(a)
            glow.blit(t, (r.x + dx, r.y + dy))
    big.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # 3) white-hot core stack — tight additive dabs under the numeral.  Kept to
    #    radius m(5) so it reads as hot iron, not a neon bar; the crisp glyph on
    #    top preserves legibility over the bloom.
    hot_core = lerp_color(pal["glow"], WHITE, 0.55)
    for sx in xs:
        soft_glow(big, sx, center[1], m(5), hot_core, 180, layers=6)

    # 4) glyph — near-white-hot fill on top; a hair of dark keyline seats the
    #    digits against their own bloom without reading as an outline.
    plain_text(big, txt, f, center, lerp_color(pal["glow"], WHITE, 0.7),
               shadow_a=0, weight=m(0.95), keyline=(10, 7, 6), kw=m(0.5))

    # Mint symbol — a thin low-alpha ember ring struck to the left of the value.
    ring_r = int(f.get_height() * 0.30)
    rx = r.left - m(6) - ring_r
    ry = center[1]
    mint = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(mint, (*lerp_color(pal["glow"], WHITE, 0.4), 90),
                       (rx, ry), ring_r, max(1, m(1)))
    big.blit(mint, (0, 0))


def _forge_name(big, name, cx, cy, max_w):
    """Name engraved into the plate — warm off-white with a 1px dark inset
    shadow so it reads as debossed cast iron.  No glow: only the price is hot."""
    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.0:
        sz -= 0.5
        f = font(sz)
    plain_text(big, name, f, (cx, cy), NAME_COL, shadow_a=0,
               weight=m(0.9), keyline=(4, 5, 10), kw=m(0.8))


def render_card(sid):
    """Draw ONE forge-plate card onto a fresh SS panel (324x200) and return it."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price = store_catalog.cost(sid)

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)

    # ── SHELL (locked order) ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── LOCKED skeleton ──
    cx = rect.left + m(40)
    cy = rect.y + m(38)
    plinth_top = rect.y + m(72)
    name_cx = rect.centerx
    name_cy = rect.y + m(81)
    price_cx = rect.right - m(23)
    price_cy = rect.y + m(48)

    # ── FORGED-IRON BAND ──
    _forge_band(big, rect, plinth_top, pal, seed=hash(sid) & 0xFFFF)

    # ── HERO DISC (R=36, left-leaning; seats into the band top) ──
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── PRICE — heat-glow deboss struck into the upper-right of the plate. ──
    _forge_price(big, f"{price}", (price_cx, price_cy), pal)

    # ── NAME — engraved warm off-white across the plate. ──
    _forge_name(big, name.upper(), name_cx, name_cy, rect.w - m(22))

    return big


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_tophat"),
    ("EPIC",      "skin_prism"),
    ("LEGENDARY", "skin_kitsune"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN = 10
GUTTER = 8
HEADER_H = 26
FOOTER_H = 22

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(20, True)
ffont = _font(18, True)
htxt = hfont.render("store_card_v4_r4 — forge-plate — round 1", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel = render_card(sid)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v4_r4/forge-plate/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
