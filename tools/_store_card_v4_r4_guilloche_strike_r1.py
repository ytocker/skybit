"""guilloche-strike — store_card_v4_r4 concept, round 1 headless render.

Visual thesis: the plinth band is an engine-turned guilloche field — the fine
concentric shimmering curves of a watch dial or banknote — struck into warm
gunmetal.  The price is a numeral MINTED directly into that plate: a struck
maker's mark with a beveled bright edge and a turned rim, no chip, no leader
line, no bubble.  The name is engraved into the same turning.

Construction:
  * Band base is a warm gunmetal vgrad (never cold blue) filling plinth_top ->
    rect.bottom, clipped to the card's rounded bottom corners.
  * Guilloche field: overlapping 1px sinusoids swept across the band, each row's
    wave phase-shifted by its own y so successive curves interfere into the
    rose-engine shimmer instead of flat stripes.  Tier hue is whispered in but
    kept warm so no tier reads cyan.
  * Band top + bottom are bound by a hairline bright rim (CARD_RING_BRIGHT).
  * Price is a struck numeral: bright bevel highlight up-left, dark inner shadow
    down-right, ringed by a short bright turned-rim arc — reads as physically
    minted into the plate.
  * Name is engraved into the turning with the same deboss bevel logic.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200 panels, no downscale).  Not wired into the live store; writes
docs/store_card_v4_r4/guilloche-strike/round_1.png.
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

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Hero disc: R=36, left-leaning.
R = 36


def _guilloche_band(big, rect, plinth_top, pal):
    """The engine-turned plinth.

    A warm gunmetal base (deliberately not cold blue) is overlaid with a field
    of overlapping 1px sinusoids.  Each row is swept horizontally as a wavy
    polyline whose vertical wobble is a sine of x PLUS a per-row phase term
    (y / period_y).  Because that phase drifts row to row, the curves slip past
    one another and interfere into the concentric shimmer of rose-engine
    turning rather than stacking into flat stripes.  Everything is clipped to
    the card's rounded bottom corners so it seats flush into the shell."""
    ph = rect.bottom - plinth_top
    band = vgrad_stops(rect.w, ph, 0,
                       [(0.0, (32, 28, 38)), (1.0, (18, 16, 22))], 255)

    # Tier hue is whispered into a warm metal so no tier turns cyan; the field
    # stays a gunmetal shimmer that merely leans toward the card's colour.
    warm = (150, 132, 110)
    line_col = lerp_color(warm, pal["gem"], 0.20)

    field = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    period_x = m(26.0)      # curve wavelength across the plate
    period_y = m(9.0)       # row-to-row phase drift — the moire engine
    amp = m(2.6)            # shallow wobble so curves shimmer, not zig-zag
    xstep = m(2)
    for row in range(0, ph + m(3), m(3)):
        # Two interleaved wave families (opposed phase drift) cross-hatch into
        # the characteristic lens/rosette weave of a turned dial.
        for sign in (1.0, -1.0):
            phase = sign * row / period_y
            pts = []
            x = 0
            while x <= rect.w:
                yy = row + math.sin(x / period_x + phase) * amp
                pts.append((x, yy))
                x += xstep
            if len(pts) >= 2:
                a = 52 if sign > 0 else 46
                pygame.draw.aalines(field, (*line_col, a), False, pts)
    band.blit(field, (0, 0))

    # Clip the whole band to the card's rounded bottom corners.
    mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h),
                     border_radius=m(CARD_RAD))
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (rect.left, plinth_top))

    # Hairline bright rims bind the field top and bottom so the turning reads as
    # a discrete inlaid plate.
    rim = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(rim, (*CARD_RING_BRIGHT, 120),
                     (rect.left, plinth_top), (rect.right - 1, plinth_top),
                     max(1, m(1)))
    pygame.draw.line(rim, (*CARD_RING_BRIGHT, 120),
                     (rect.left + m(2), rect.bottom - max(1, m(1))),
                     (rect.right - 1 - m(2), rect.bottom - max(1, m(1))),
                     max(1, m(1)))
    big.blit(rim, (0, 0))
    # A dark keyline directly under the top rim firms the seam.
    pygame.draw.line(big, (6, 5, 9),
                     (rect.left, plinth_top - max(1, m(1))),
                     (rect.right - 1, plinth_top - max(1, m(1))), max(1, m(1)))


def _struck_numeral(big, cx, cy, price, pal):
    """The price minted into the plate as a struck maker's mark.

    No enclosing chip or bubble: the numeral itself is the mark.  A dark inner
    shadow offset down-right sinks the strokes into the metal; a bright bevel
    highlight offset up-left catches the top-left light on the raised stroke
    edge; a short bright arc rings the mark to read as the turned rim of the
    die that struck it."""
    f = font(9.0)
    txt = f"{price}"                                 # no comma — cleaner at 162px
    nw = _glyph_base(txt, f, 0).get_width()

    # Turned-rim arc: a bright quarter sweep hugging the mark's top-left, the
    # lit edge of the struck die.
    ar = nw // 2 + m(6)
    rimbox = pygame.Rect(cx - ar, cy - ar, ar * 2, ar * 2)
    arc = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(arc, (*CARD_RING_BRIGHT, 160), rimbox,
                    math.radians(70), math.radians(200), max(1, m(1)))
    # A faint deep counter-arc on the lower-right seats the mark into shadow.
    pygame.draw.arc(arc, (*lerp_color(pal["deep"], NEAR_BLACK, 0.4), 120),
                    rimbox, math.radians(250), math.radians(20), max(1, m(1)))
    big.blit(arc, (0, 0))

    dark = lerp_color(pal["deep"], NEAR_BLACK, 0.45)
    bright = lerp_color(pal["gem"], WHITE, 0.55)
    mid = lerp_color(pal["gem"], WHITE, 0.20)
    o = max(1, m(1))
    # Sink shadow (down-right), bevel highlight (up-left), then the struck face.
    plain_text(big, txt, f, (cx + o, cy + o), dark, shadow_a=0, weight=m(0.9))
    plain_text(big, txt, f, (cx - o, cy - o), bright, shadow_a=0, weight=m(0.8))
    plain_text(big, txt, f, (cx, cy), mid, shadow_a=0, weight=m(0.9))


def _engrave_name(big, name, cx, cy, max_w):
    """Warm-silver name engraved into the turning, auto-shrunk to fit.  Same
    deboss bevel as the struck numeral: bright top-left edge, dark down-right
    sink, so the letters read as cut into the guilloche rather than printed on
    top of it."""
    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.0:
        sz -= 0.5
        f = font(sz)
    o = max(1, m(1))
    dark = (10, 9, 14)
    bright = (236, 232, 240)
    silver = (200, 195, 210)
    plain_text(big, name, f, (cx + o, cy + o), dark, shadow_a=0, weight=m(0.9))
    plain_text(big, name, f, (cx - o, cy - o), bright, shadow_a=0, weight=m(0.8))
    plain_text(big, name, f, (cx, cy), silver, shadow_a=0, weight=m(0.95))


def render_card(sid):
    """Draw ONE guilloche-strike card onto a fresh SS panel (324x200)."""
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

    # ── GUILLOCHE PLINTH BAND ──
    _guilloche_band(big, rect, plinth_top, pal)

    # ── HERO DISC (R=36, left-leaning) ──
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── PRICE — struck maker's mark minted into the plate. ──
    _struck_numeral(big, rect.right - m(23), rect.y + m(48), price, pal)

    # ── NAME — engraved across the guilloche band. ──
    _engrave_name(big, name.upper(), rect.centerx, rect.y + m(81),
                  rect.w - m(22))

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
htxt = hfont.render("store_card_v4_r4 — guilloche-strike — round 1", True,
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

out = "/home/user/skybit/docs/store_card_v4_r4/guilloche-strike/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# ── L* probes — verify the engraved name/struck numeral stay legible on the
#    warm guilloche ground. ──
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


r2 = pygame.Rect(m(_INSET), m(_INSET),
                 CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
for tier, sid in VARIANTS:
    panel = render_card(sid)
    band_bg = panel.get_at((r2.right - m(30), r2.y + m(81)))
    name_stroke = (200, 195, 210)
    print(f"  {tier:10s} band_bg L*={_lstar(band_bg):5.1f}  "
          f"name/band contrast={_contrast(name_stroke, band_bg):4.1f}:1")
