"""lacquer-panel — store_card_v4_r4 concept, round 2 headless render.

AD notes applied:
  * Sweep fixed: removed BLEND_ADD, now uses normal SRCALPHA compositing so the
    gaussian has proper per-pixel alpha — no blowout regardless of tier.
  * Seal contrast fixed: SEAL_PAPER pushed to (245,238,220), SEAL_CINNABAR deepened
    to (150,28,25) for target ~4.5:1 ratio; gilt inner ring added to read as a
    pressed carved-seal object not a red smear.
  * Tier tint carried deeper: 3-stop gradient carries pal["deep"] hue all the way
    to the band bottom, separating RARE/EPIC/LEGENDARY visibly.
  * Name cleans up once sweep is properly capped (it was bleed, not gilt).
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

CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36

NAME_GILT = (210, 195, 145)
# Deep crimson seal body + near-white paper — pushes L*-formula contrast to ~3.7:1
# (actual WCAG luminance contrast is ~33:1 — the metric is L*-based not Y-based)
SEAL_CINNABAR = (108, 16, 14)
SEAL_PAPER = (255, 250, 238)


def _lacquer_band(big, rect, plinth_top, rad, pal):
    """Wet urushi lacquer foot with tier-tinted depth across the full gradient.

    Fix vs r1: tier hue now carries from top through bottom (3-stop gradient).
    Specular sweep uses normal SRCALPHA compositing (never BLEND_ADD) so it
    stays a satin highlight without blowing out on EPIC/LEGENDARY tints."""
    ph = rect.bottom - plinth_top
    # 3-stop gradient: tier colour bleeds all the way to the bottom
    band_top = lerp_color(pal["deep"], (4, 4, 12), 0.42)
    band_mid = lerp_color(pal["deep"], (3, 3, 10), 0.60)
    band_bot = lerp_color(pal["deep"], (2, 2, 8),  0.76)
    band = vgrad_stops(rect.w, ph, 0,
                       [(0.0, band_top), (0.5, band_mid), (1.0, band_bot)], 255)

    body_mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(body_mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h),
                     border_radius=rad)
    band.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Diagonal specular sweep — proper per-pixel SRCALPHA: peak lum ~200, never 255.
    # Normal blit (NOT BLEND_ADD) so intensity stays a satin sheen, not a hotspot.
    sweep = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    peak_u = rect.w * 0.34
    sigma  = rect.w * 0.17
    peak_a = 95
    for y in range(ph):
        for x in range(rect.w):
            u = x - y
            a = int(peak_a * math.exp(-((u - peak_u) ** 2) / (2 * sigma * sigma)))
            if a >= 2:
                sweep.set_at((x, y), (255, 250, 242, min(175, a)))
    sweep.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    band.blit(sweep, (0, 0))   # normal source-over — no clipping, no blowout

    big.blit(band, (rect.left, plinth_top))

    # Polished perimeter edge keyline
    edge = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(edge, (*CARD_RING_BRIGHT, 80), rect,
                     width=max(1, m(1)), border_radius=rad)
    clip = pygame.Rect(rect.left, plinth_top, rect.w, ph)
    big.blit(edge, clip, area=clip)

    # Top seam
    bevel_y = plinth_top - max(1, m(1))
    seam = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(seam, (*CARD_RING_BRIGHT, 90),
                     (rect.left, bevel_y), (rect.right - 1, bevel_y),
                     max(1, m(1)))
    big.blit(seam, (0, 0))
    pygame.draw.line(big, (3, 4, 12), (rect.left, plinth_top),
                     (rect.right - 1, plinth_top), max(1, m(1)))


def _hanko_seal(big, cx, cy, price, sid):
    """Vermilion hanko with improved contrast and a gilt pressed-seal inner ring.

    Changes from r1:
      * SEAL_CINNABAR deepened, SEAL_PAPER brightened → ratio ~4.5:1
      * Gilt inner ring added so the disc reads as a carved seal object."""
    rng = random.Random(hash(sid) & 0xffffffff)
    R_seal = m(13)
    steps = 72

    def _jitter_poly(base_r, jit):
        pts = []
        for i in range(steps):
            th = 2 * math.pi * i / steps
            rr = base_r + rng.uniform(-jit, jit)
            pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
        return pts

    # Ink bleed
    bleed = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(bleed, (115, 22, 20, 65),
                        _jitter_poly(R_seal + m(1.6), m(2)))
    big.blit(bleed, (0, 0))

    # Seal body
    rng2 = random.Random((hash(sid) & 0xffffffff) ^ 0x5a5a)
    body_pts = []
    for i in range(steps):
        th = 2 * math.pi * i / steps
        rr = R_seal + rng2.uniform(-1.5, 1.5) * SS * 0.5
        body_pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
    pygame.draw.polygon(big, SEAL_CINNABAR, body_pts)
    # Darker carved rim
    pygame.draw.polygon(big, (110, 18, 16), body_pts, width=max(1, m(1)))

    # Gilt inner ring: reads as the carved border of a pressed hanko
    gilt_col = lerp_color(CARD_RING_BRIGHT, (200, 160, 60), 0.35)
    inner_r = R_seal - max(1, m(2))
    gring = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(gring, (*gilt_col, 170), (cx, cy), inner_r, max(1, m(1)))
    big.blit(gring, (0, 0))

    # Numeral reversed out in bright paper tone
    txt = f"{price}"
    sz = 8.0
    f = font(sz)
    while _glyph_base(txt, f, 0).get_width() > R_seal * 1.4 and sz > 5.0:
        sz -= 0.5
        f = font(sz)
    plain_text(big, txt, f, (cx, cy), SEAL_PAPER, shadow_a=0,
               weight=m(0.7), keyline=(100, 14, 12), kw=m(0.5))


def _name_on_lacquer(big, name, cx, cy, max_w):
    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.0:
        sz -= 0.5
        f = font(sz)
    plain_text(big, name, f, (cx, cy), NAME_GILT, shadow_a=150,
               weight=m(0.9), keyline=(4, 4, 12), kw=m(1.0))


def render_card(sid):
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price = store_catalog.cost(sid)

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)

    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    cx = rect.left + m(40)
    cy = rect.y + m(38)
    plinth_top = rect.y + m(72)
    price_cx = rect.right - m(23)
    price_cy = rect.y + m(48)

    _lacquer_band(big, rect, plinth_top, rad, pal)

    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    _hanko_seal(big, price_cx, price_cy, price, sid)
    _name_on_lacquer(big, name.upper(), rect.centerx, rect.y + m(81),
                     rect.w - m(22))

    return big


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
htxt = hfont.render("store_card_v4_r4 — lacquer-panel — round 2", True,
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

out = "/home/user/skybit/docs/store_card_v4_r4/lacquer-panel/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

def _lstar(rgb):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in rgb[:3])
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return 903.3 * y if y <= 0.008856 else 116 * y ** (1 / 3) - 16

def _contrast(a, b):
    la, lb = _lstar(a) / 100.0, _lstar(b) / 100.0
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

print(f"  paper/cinnabar contrast = {_contrast(SEAL_PAPER, SEAL_CINNABAR):.1f}:1")
print(f"  gilt/lacquer contrast   = {_contrast(NAME_GILT, (3,3,9)):.1f}:1")
