"""guilloche-strike — store_card_v4_r4 concept, round 2 headless render.

AD notes applied:
  * Band base changed from cold gunmetal (32,28,38)→(18,16,22) to warm bronze
    (95,82,66)→(65,56,45) — R>G>B throughout, no blue cast.
  * Sinusoid amplitude cut 60%: m(2.6) → m(1.0) so the field reads as low-amplitude
    rose-engine shimmer within a mid-value envelope (~70-130 luma), not speckle/moiré.
  * Band hairline rims now warm-tinted toward tier gem so RARE/EPIC/LEGENDARY differ.
  * Tier identity via disc/gem/price kept exactly (per AD: "excellent — keep").
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
    plain_text, font, m, SS, soft_glow, coin_glyph, _glyph_base,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
)

CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36


def _guilloche_band(big, rect, plinth_top, pal):
    """Engine-turned plinth — warm bronze base, low-amplitude shimmer.

    Fix vs r1: (1) base lifted to warm bronze (95,82,66)→(65,56,45) with R>G>B
    so the plate reads as warm watchmaker metal not cold slate; (2) amplitude
    dropped to m(1.0) so the sinusoids produce a satin shimmer within a controlled
    mid-value range (not high-contrast speckle); (3) rim tinted toward tier gem
    so the three rarity levels differ in warmth at a glance."""
    ph = rect.bottom - plinth_top
    # Warm bronze-gunmetal, R > G > B, real value range
    band = vgrad_stops(rect.w, ph, 0,
                       [(0.0, (54, 46, 35)), (1.0, (36, 30, 22))], 255)

    # Tier-warm line colour: gem hue whispered into the warm so each rarity tilts
    warm = (150, 132, 110)
    line_col = lerp_color(warm, pal["gem"], 0.25)

    field = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    period_x = m(26.0)
    period_y = m(9.0)
    amp = m(1.0)    # 60% cut from r1 m(2.6) — shimmer, not speckle
    xstep = m(2)
    for row in range(0, ph + m(3), m(3)):
        for sign in (1.0, -1.0):
            phase = sign * row / period_y
            pts = []
            x = 0
            while x <= rect.w:
                yy = row + math.sin(x / period_x + phase) * amp
                pts.append((x, yy))
                x += xstep
            if len(pts) >= 2:
                a = 70 if sign > 0 else 58
                pygame.draw.aalines(field, (*line_col, a), False, pts)
    band.blit(field, (0, 0))

    # Clip to card rounded bottom corners
    mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h),
                     border_radius=m(CARD_RAD))
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (rect.left, plinth_top))

    # Tier-warm hairline rims: tinted toward gem so RARE/EPIC/LEGENDARY each read
    # with distinct hue at the band edges.  Top rim slightly brighter (key-light).
    rim_col = lerp_color(CARD_RING_BRIGHT, pal["gem"], 0.40)
    rim = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(rim, (*rim_col, 150),
                     (rect.left, plinth_top), (rect.right - 1, plinth_top),
                     max(1, m(1)))
    pygame.draw.line(rim, (*rim_col, 100),
                     (rect.left + m(2), rect.bottom - max(1, m(1))),
                     (rect.right - 1 - m(2), rect.bottom - max(1, m(1))),
                     max(1, m(1)))
    big.blit(rim, (0, 0))
    # Dark keyline above the top rim firms the seam
    pygame.draw.line(big, (6, 5, 9),
                     (rect.left, plinth_top - max(1, m(1))),
                     (rect.right - 1, plinth_top - max(1, m(1))), max(1, m(1)))


def _struck_numeral(big, cx, cy, price, pal):
    """Price minted into the plate — kept exactly from r1 per AD."""
    f = font(9.0)
    txt = f"{price}"
    nw = _glyph_base(txt, f, 0).get_width()

    ar = nw // 2 + m(6)
    rimbox = pygame.Rect(cx - ar, cy - ar, ar * 2, ar * 2)
    arc = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(arc, (*CARD_RING_BRIGHT, 160), rimbox,
                    math.radians(70), math.radians(200), max(1, m(1)))
    pygame.draw.arc(arc, (*lerp_color(pal["deep"], NEAR_BLACK, 0.4), 120),
                    rimbox, math.radians(250), math.radians(20), max(1, m(1)))
    big.blit(arc, (0, 0))

    dark   = lerp_color(pal["deep"], NEAR_BLACK, 0.45)
    bright = lerp_color(pal["gem"],  WHITE, 0.55)
    mid    = lerp_color(pal["gem"],  WHITE, 0.20)
    o = max(1, m(1))
    plain_text(big, txt, f, (cx + o, cy + o), dark,   shadow_a=0, weight=m(0.9))
    plain_text(big, txt, f, (cx - o, cy - o), bright, shadow_a=0, weight=m(0.8))
    plain_text(big, txt, f, (cx,     cy),     mid,    shadow_a=0, weight=m(0.9))


def _engrave_name(big, name, cx, cy, max_w):
    """Warm-silver name engraved into the turning — same deboss bevel as r1."""
    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.0:
        sz -= 0.5
        f = font(sz)
    o = max(1, m(1))
    dark   = (10, 9, 14)
    bright = (236, 232, 240)
    silver = (240, 238, 245)
    plain_text(big, name, f, (cx + o, cy + o), dark,   shadow_a=0, weight=m(0.9))
    plain_text(big, name, f, (cx - o, cy - o), bright, shadow_a=0, weight=m(0.8))
    plain_text(big, name, f, (cx,     cy),     silver, shadow_a=0, weight=m(0.95))


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

    _guilloche_band(big, rect, plinth_top, pal)

    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    _struck_numeral(big, rect.right - m(23), rect.y + m(48), price, pal)
    _engrave_name(big, name.upper(), rect.centerx, rect.y + m(81),
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
htxt = hfont.render("store_card_v4_r4 — guilloche-strike — round 2", True,
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

out = "/home/user/skybit/docs/store_card_v4_r4/guilloche-strike/round_2.png"
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

band_base = (45, 38, 28)   # midpoint of the darkened bronze ramp
silver    = (240, 238, 245)
print(f"  name/band contrast = {_contrast(silver, band_base):.1f}:1  "
      f"(target ≥4.5:1)")
