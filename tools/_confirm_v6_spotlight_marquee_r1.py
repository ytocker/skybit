#!/usr/bin/env python3
"""
spotlight-marquee confirm_purchase_v6 round 1 render.

Concept: a theatre-marquee confirm popup.
  - A HERO cabochon disc crowns the card, overhanging the top edge by ~40% so
    its tier-coloured soft_glow aura escapes upward unclipped — the tier reads
    before a word is parsed.
  - A dominant horizontal MARQUEE BANNER (the notched-hex `_ribbon` construction
    scaled to ~2.6x store-card height) crosses the upper third, carrying the tier
    word.
  - A translucent BLEND_ADD SPOTLIGHT CONE in the tier glow originates at the
    disc and fans down. Its edges are the rays from the disc centre through the
    two banner-underside corners, so the cone's width AT the banner exactly
    matches the banner's width — the marquee reads as lit from below. The cone
    feathers (in RGB magnitude, since BLEND_ADD ignores alpha) to nothing at the
    card's lower edge.
  - Below: item name in cream, gold price chip.

Sheet shows the three tiers side by side (RARE / EPIC / LEGENDARY). Only the
tier tint (disc aura + gem ring, banner gradient, cone hue) changes per tier.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import math

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, drop_shadow, bevel_rim, top_sheen,
    plain_text, price_chip,
    cabochon, cabochon_glass, blit_thumb, _glyph_base, font, m, SS,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_DEEP, CARD_RING_BRIGHT,
)
from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK, WHITE


# BLEND_ADD ignores source alpha, so an alpha-driven sweep silently blows the
# gold chips to white. Keeping the sweep value in RGB MAGNITUDE keeps it tame.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0:
            continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)
sc.gloss_sweep = _gloss_sweep_fixed


# ── brief palette (per-tier gem / glow / deep) ────────────────────────────────
TIERS = [
    ("RARE",      "skin_lorikeet",  600,
     {"gem": (108, 188, 252), "glow": (74, 158, 248), "deep": (18, 44, 90)}),
    ("EPIC",      "skin_prism",    1400,
     {"gem": (194, 122, 248), "glow": (172, 94, 244), "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_kitsune",  3500,
     {"gem": (255, 202, 104), "glow": (255, 168, 58), "deep": (90, 50, 0)}),
]


# ── popup metrics (logical px; flow through m()) ──────────────────────────────
POP_W, POP_H = 292, 300
CX = POP_W // 2                     # 146

CARD_X, CARD_TOP = 8, 74
CARD_W, CARD_H = POP_W - CARD_X * 2, POP_H - CARD_TOP - 8   # 276 x 228
CARD_BOT = CARD_TOP + CARD_H        # 292
CARD_RAD = 18

# Hero disc: overhangs the top edge by ~40% => 0.4 of the diameter sits ABOVE
# the card top, so the centre is 0.2*R below it.
R_HERO = 40
DISC_CY = CARD_TOP + int(round(0.2 * R_HERO))   # 72

# Marquee banner: ~2.6x store-card height wide, spanning the upper third.
BANNER_W, BANNER_H = int(round(2.6 * sc.CARD_H)), 48   # 260 x 48
HALF_BW = BANNER_W // 2                                # 130
BANNER_UNDER = 162                  # underside y (bottom of the upper third band)
BANNER_CY = BANNER_UNDER - BANNER_H // 2              # 138

# Cone: apex at the disc centre; its edges are the rays through the two
# banner-underside corners (cx +/- HALF_BW, BANNER_UNDER). This makes the cone's
# width AT the banner equal the banner width by construction.
CONE_SLOPE = HALF_BW / (BANNER_UNDER - DISC_CY)       # dx per dy
CONE_RGB_SCALE = 0.30               # keep additive magnitude low => tinted, not white

Y_NAME = 198
Y_CHIP = 236


def _alpha_aura(surf, cx, cy, radius, color, peak=27, layers=15):
    """A feathered tier-colour halo drawn with NORMAL (alpha-carrying) blits so
    it survives compositing where it escapes above the card top into transparent
    headroom — soft_glow's BLEND_ADD would leave that region alpha-0 (invisible)."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        if r <= 0:
            continue
        a = int(peak * (1 - (i - 1) / layers) ** 1.6)
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1))


def _spotlight_cone(big, pal):
    """The translucent downward cone. Built on its own surface with the feather
    baked into RGB MAGNITUDE (BLEND_ADD discards alpha), masked to the card's
    rounded-rect so the bottom corners clip, then added onto the body. The top
    scanline sits at the banner underside so the cone appears to spill out from
    beneath the marquee; it fades to nothing at the card's lower edge."""
    cone = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    apex_y = m(DISC_CY)
    y0, y1 = m(BANNER_UNDER), m(CARD_BOT)
    cx = m(CX)
    base = pal["glow"]
    span = max(1, y1 - y0)
    for y in range(y0, y1):
        v = (1 - (y - y0) / span) ** 1.5           # 1 at the banner, 0 at foot
        half = int((y - apex_y) * CONE_SLOPE)
        if half <= 0:
            continue
        col = (int(base[0] * CONE_RGB_SCALE * v),
               int(base[1] * CONE_RGB_SCALE * v),
               int(base[2] * CONE_RGB_SCALE * v))
        pygame.draw.line(cone, (*col, 255), (cx - half, y), (cx + half, y))
    # clip to the card body so the widening wedge doesn't spill past the rounded
    # corners / edges.
    mask = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H)),
                     border_radius=m(CARD_RAD))
    cone.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(cone, (0, 0), special_flags=pygame.BLEND_ADD)

    # footlight kiss: a soft additive bloom hugging the banner underside so the
    # marquee reads as genuinely lit from below.
    kiss = pygame.Surface((BANNER_W * SS, m(20)), pygame.SRCALPHA)
    kw, kh = kiss.get_size()
    for yy in range(kh):
        a = int(70 * (1 - yy / kh) ** 1.4)
        c = (int(base[0] * 0.5), int(base[1] * 0.5), int(base[2] * 0.5))
        pygame.draw.line(kiss, (*c, a), (0, yy), (kw, yy))
    big.blit(kiss, (cx - kw // 2, y0), special_flags=pygame.BLEND_ADD)


def _marquee(big, tier_word, pal):
    """The dominant marquee banner: the notched-hex `_ribbon` construction (tier
    gradient body, notched ends, dark defined edge, dropped shadow) scaled up to
    the hero span, ringed by a row of warm marquee bulbs top and bottom, with the
    tier word embossed large across it."""
    w, h = m(BANNER_W), m(BANNER_H)
    cx, cy = m(CX), m(BANNER_CY)
    x0, y0 = cx - w // 2, cy - h // 2
    notch = int(h * 0.34)

    top = lerp_color(pal["gem"], WHITE, 0.10)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = vgrad_stops(w, h, 0, [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                       255, gamma=1.08)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2), (w - notch, h),
            (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # a glossy top sheen inside the notched silhouette
    sheen = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h // 2):
        a = int(70 * (1 - yy / (h / 2)) ** 1.4)
        pygame.draw.line(sheen, (255, 255, 255, a), (0, yy), (w, yy))
    sheen.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    body.blit(sheen, (0, 0))

    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 130), poly)
    big.blit(sh, (x0, y0 + m(3)))
    big.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    # dark defined outer edge + a fine warm inner keyline (marquee framing).
    pygame.draw.polygon(big, (4, 5, 16), abspoly, width=max(1, m(2)))
    innerpoly = [(x0 + px, y0 + py + (m(3) if py < h // 2 else -m(3)))
                 for px, py in [(notch + m(3), m(3)), (w - notch - m(3), m(3)),
                                (w - m(3), h // 2), (w - notch - m(3), h - m(3)),
                                (notch + m(3), h - m(3)), (m(3), h // 2)]]
    pygame.draw.polygon(big, (*lerp_color(pal["gem"], WHITE, 0.4), 130), innerpoly,
                        width=max(1, m(1)))

    # marquee bulbs: a warm dotted lamp row hugging the top + bottom edges.
    n = 11
    bulb_r = max(2, m(1.7))
    for row_y, inset in ((y0 + m(6), 0), (y0 + h - m(6), 0)):
        for k in range(n):
            bx = x0 + notch + int((w - 2 * notch) * (k / (n - 1)))
            _alpha_aura(big, bx, row_y, m(4), (255, 232, 170), peak=22, layers=5)
            pygame.draw.circle(big, (255, 244, 210), (bx, row_y), bulb_r)
            pygame.draw.circle(big, (255, 210, 120), (bx, row_y), bulb_r, max(1, m(0.5)))

    # tier word — embossed dark ink with a crisp top cream lip, auto-fit to span.
    sz = 27
    tf = font(sz)
    avail = w - 2 * notch - m(20)
    while _glyph_base(tier_word, tf, m(2.0)).get_width() > avail and sz > 12:
        sz -= 1
        tf = font(sz)
    ink = lerp_color(pal["deep"], NEAR_BLACK, 0.5)
    plain_text(big, tier_word, tf, (cx, cy + m(1)),
               lerp_color(pal["gem"], WHITE, 0.62), shadow_a=0,
               tracking=m(2.0), weight=m(1.3), keyline=ink, kw=m(1.2))


def _hero_aura(big, cx, cy, r, glow):
    """A strong tier halo around the medallion: a broad soft bloom plus a tight
    rim halo brightest at the disc edge, all drawn with NORMAL alpha-carrying
    blits so the portion escaping above the card survives compositing over the
    transparent headroom."""
    _alpha_aura(big, cx, cy, r + m(40), glow, peak=36, layers=16)
    lite = lerp_color(glow, WHITE, 0.14)
    extra, layers = m(26), 16
    for i in range(layers, 0, -1):
        rr = r + int(extra * i / layers)
        a = int(155 * (1 - (i - 1) / layers) ** 1.5)
        g = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*lite, a), (rr + 1, rr + 1), rr)
        big.blit(g, (cx - rr - 1, cy - rr - 1))


def _hero_disc(big, sid, pal):
    """The overhanging cabochon medallion + its escaping tier aura. Drawn last so
    it crowns the banner; the aura reaches up into the transparent headroom above
    the card, unclipped."""
    cx, cy, r = m(CX), m(DISC_CY), m(R_HERO)
    _hero_aura(big, cx, cy, r, pal["glow"])
    cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(r * 1.5))
    cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    # crisp tier gem ring so the tint is unmistakable on the medallion rim.
    ring_w = max(3, m(3.0))
    pygame.draw.circle(big, pal["gem"], (cx, cy), r + ring_w // 2 + m(1), ring_w)
    pygame.draw.circle(big, lerp_color(pal["deep"], NEAR_BLACK, 0.35), (cx, cy),
                       r - m(1), max(1, m(1)))


def _card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad, [(0.0, CARD_T), (1.0, CARD_B)],
                         255, gamma=1.15), rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
              w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 55), tray, width=max(1, m(1)),
                     border_radius=rad - m(3))


def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    _card_body(big)
    _spotlight_cone(big, pal)
    _marquee(big, tier_word, pal)
    name = sc._name(sid)
    plain_text(big, name, font(15), (m(CX), m(Y_NAME)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    price_chip(big, m(CX), m(Y_CHIP), f"{price:,}", m(24), affordable=True)
    _hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# =============================================================================
# Review sheet — three tiers side by side over a modal-style scrim
# =============================================================================
GUT = 26
MARGIN = 26
HEAD = 62
CANVAS_W = MARGIN * 2 + POP_W * 3 + GUT * 2
CANVAS_H = HEAD + POP_H + 34

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
for y in range(CANVAS_H):
    pygame.draw.line(canvas, lerp_color((10, 11, 26), (5, 5, 14), y / CANVAS_H),
                     (0, y), (CANVAS_W, y))

title = _font(19, True).render(
    "confirm_purchase_v6 — spotlight-marquee  (round 1)", True, (232, 226, 208))
canvas.blit(title, (MARGIN, 16))
sub = _font(11, True).render(
    "overhanging hero disc + upper-third marquee banner lit from below by a "
    "tier spotlight cone", True, (150, 156, 178))
canvas.blit(sub, (MARGIN, 38))

lab = _font(13, True)
for i, (tier_word, sid, price, pal) in enumerate(TIERS):
    pop = render_popup(tier_word, sid, price, pal)
    px = MARGIN + i * (POP_W + GUT)
    py = HEAD
    canvas.blit(pop, (px, py))
    t = lab.render(tier_word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(t, t.get_rect(center=(px + POP_W // 2, py - 8)))

out = "/home/user/skybit/docs/confirm_purchase_v6/spotlight-marquee/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())
