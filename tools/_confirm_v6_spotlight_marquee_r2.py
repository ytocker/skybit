#!/usr/bin/env python3
"""
spotlight-marquee confirm_purchase_v6 round 2.

Addresses all art-director notes from r1:
  1. Real tier-hued bloom — two concentric _alpha_aura passes (raw glow colour,
     peak=95 / peak=70) anchored on the disc centre; extends 40–60px above
     card top into transparent headroom, no gap, no near-white smear.
  2. Near-white top smear removed — the r1 inner-ring loop that lerped glow
     toward WHITE at a=155 is gone; only tier-coloured passes remain.
  3. Banner leads the eye — BANNER_H raised to 50px; gradient top=gem_light,
     mid=glow (pure tier), bottom=deep; marquee bulbs tinted to tier gem, not
     always warm gold.
  4. Visible spotlight cone — BANNER_UNDER moved from 162→185 giving a 13px
     clear gap between disc bottom (y=122) and banner top (y=135); cone is
     drawn through that gap, plus a lit-arc BLEND_ADD strip on the banner's
     upper edge makes the "disc illuminates the banner" read survive inside
     the banner body.
  5. Consistent vertical layout — DISC_CY, BANNER_CY, BANNER_UNDER, Y_NAME,
     Y_CHIP are all constants; no per-tier offsets.
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


# BLEND_ADD alpha rule: keep the sweep in RGB magnitude so the additive path
# never blows price-chip gold to white (BLEND_ADD ignores source alpha).
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


# ── brief palette (r2 spec) ───────────────────────────────────────────────────
TIERS = [
    ("RARE",      "skin_lorikeet",  600,
     {"gem": (108, 188, 252), "glow": (60, 140, 230),  "deep": (18, 44, 90)}),
    ("EPIC",      "skin_prism",    1400,
     {"gem": (194, 122, 248), "glow": (150, 60, 220),  "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_kitsune",  3500,
     {"gem": (255, 202, 104), "glow": (220, 160, 40),  "deep": (90, 50, 0)}),
]


# ── popup metrics — every constant shared by all three tiers ──────────────────
POP_W, POP_H = 292, 300
CX = POP_W // 2                              # 146

CARD_X, CARD_TOP = 8, 74
CARD_W  = POP_W - CARD_X * 2               # 276
CARD_H  = POP_H - CARD_TOP - 8             # 218
CARD_BOT = CARD_TOP + CARD_H               # 292
CARD_RAD = 18

# Hero disc: 40% of diameter (= R_HERO) overhangs above card top,
# so centre sits 0.20×R below the card edge.
R_HERO   = 40
DISC_CY  = CARD_TOP + int(round(0.2 * R_HERO))  # 82
DISC_BOT = DISC_CY + R_HERO                      # 122

# Marquee banner: taller + pushed down to open a clear gap above its top edge.
# Gap: BANNER_TOP(135) − DISC_BOT(122) = 13 px — the cone is visible there.
BANNER_H    = 50                                  # was 48
HALF_BW     = int(round(2.6 * sc.CARD_H)) // 2  # 130
BANNER_W    = HALF_BW * 2                         # 260
BANNER_UNDER = 185                               # banner underside y  (was 162)
BANNER_CY   = BANNER_UNDER - BANNER_H // 2      # 160
BANNER_TOP  = BANNER_UNDER - BANNER_H            # 135

# Cone apex at disc centre; edge slope so cone width at banner underside = banner width.
CONE_SLOPE   = HALF_BW / max(1, BANNER_UNDER - DISC_CY)  # ≈1.26 dx/dy
CONE_RGB     = 0.28      # additive RGB scale: tinted not blown out

Y_NAME = 207
Y_CHIP = 250


# ── helpers ───────────────────────────────────────────────────────────────────

def _alpha_aura(surf, cx, cy, radius, color, peak=27, layers=15):
    """Feathered halo via normal alpha-carry blits — survives compositing in
    transparent headroom above the card top where BLEND_ADD would leave alpha=0."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        if r <= 0:
            continue
        a = int(peak * (1 - (i - 1) / layers) ** 1.6)
        if a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1))


def _hero_aura(big, cx, cy, r, glow):
    """Pure tier-hued radial bloom — two concentric passes, no white lerp.
    The broad outer pass (r+55) reaches 40–60 px above the card top; the
    tighter inner ring (r+20) concentrates the hue at the disc edge. Both use
    raw glow colour so sky-blue/vivid-purple/warm-gold reads unmistakably."""
    _alpha_aura(big, cx, cy, r + m(55), glow, peak=95, layers=24)
    _alpha_aura(big, cx, cy, r + m(20), glow, peak=70, layers=12)


def _spotlight_cone(big, pal):
    """Tier-hued widening cone from disc-bottom down to banner underside.
    The 13 px gap between disc bottom and banner top is where the cone reads
    as 'beam in air'. Inside the banner body the cone is painted over by the
    banner fill; a lit-arc on the banner's upper edge preserves the 'disc
    illuminates the banner' read after the banner paints over the cone pixels.

    Built on an SRCALPHA scratch surface; RGB magnitudes are kept small
    (CONE_RGB=0.28) so the additive composite doesn't blow out the hue."""
    cone = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    apex_y = m(DISC_CY)
    y0 = m(DISC_BOT)
    y1 = m(BANNER_UNDER)
    cx = m(CX)
    base = pal["glow"]
    span = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        # fade from 1 (at disc bottom) toward 0 (at banner underside)
        v = (1 - (y - y0) / span) ** 1.1
        half = int((y - apex_y) * CONE_SLOPE)
        if half <= 0:
            continue
        col = (int(base[0] * CONE_RGB * v),
               int(base[1] * CONE_RGB * v),
               int(base[2] * CONE_RGB * v))
        pygame.draw.line(cone, (*col, 255), (cx - half, y), (cx + half, y))
    # clip to card body rounded-rect so the cone never bleeds outside the card
    mask = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H)),
                     border_radius=m(CARD_RAD))
    cone.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(cone, (0, 0), special_flags=pygame.BLEND_ADD)


def _lit_arc(big, pal, x0, y0, w, arc_h):
    """Horizontal BLEND_ADD brightening strip along the banner's top edge.
    Drawn AFTER the banner body so the lit-glint sits on the gradient fill,
    making the top of the banner read as struck by the spotlight from above.
    RGB magnitudes stay modest to tint rather than bleach."""
    glow = pal["glow"]
    lit = pygame.Surface((w, arc_h), pygame.SRCALPHA)
    for y in range(arc_h):
        v = (1 - y / max(1, arc_h)) ** 1.3
        col = (int(glow[0] * 0.40 * v),
               int(glow[1] * 0.40 * v),
               int(glow[2] * 0.40 * v))
        pygame.draw.line(lit, (*col, 255), (0, y), (w - 1, y))
    big.blit(lit, (x0, y0), special_flags=pygame.BLEND_ADD)


def _marquee(big, tier_word, pal):
    """Dominant marquee banner: notched-hex silhouette, tier-hued gradient face
    (gem-bright top → pure glow mid → deep shadow bottom so each tier's banner
    immediately declares its rarity), 11 tier-gem bulbs top + bottom, tier word
    embossed across the centre, lit-arc on the top edge."""
    w, h = m(BANNER_W), m(BANNER_H)
    cx, cy = m(CX), m(BANNER_CY)
    x0, y0 = cx - w // 2, cy - h // 2
    notch = int(h * 0.34)

    # Tier-hued face: the gradient top/mid/bottom are all derived from the tier
    # palette — no blended-to-gold fallback that could make tiers look similar.
    top = lerp_color(pal["gem"], WHITE, 0.22)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.18)
    body = vgrad_stops(w, h, 0,
                       [(0.0, top), (0.38, pal["glow"]), (1.0, bot)],
                       255, gamma=1.05)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2), (w - notch, h),
            (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # banner drop shadow
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 140), poly)
    big.blit(sh, (x0, y0 + m(3)))
    big.blit(body, (x0, y0))

    # dark defined outer edge + fine tier-tinted inner keyline
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(big, (4, 5, 16), abspoly, width=max(1, m(2)))
    innerpoly = [
        (x0 + px, y0 + py + (m(3) if py < h // 2 else -m(3)))
        for px, py in [(notch + m(3), m(3)), (w - notch - m(3), m(3)),
                       (w - m(3), h // 2), (w - notch - m(3), h - m(3)),
                       (notch + m(3), h - m(3)), (m(3), h // 2)]
    ]
    pygame.draw.polygon(big, (*lerp_color(pal["gem"], WHITE, 0.42), 145), innerpoly,
                        width=max(1, m(1)))

    # Lit-arc on banner top — placed right after the banner body so the glow
    # sits on top of the gradient, reading as the spotlight striking the face.
    _lit_arc(big, pal, x0, y0, w, max(m(7), h // 6))

    # Marquee bulbs: tier-gem tinted, not always warm gold.
    n = 11
    bulb_r = max(2, m(1.7))
    bulb_fill = lerp_color(pal["gem"], (255, 252, 244), 0.38)
    bulb_rim  = lerp_color(pal["glow"], (240, 210, 110), 0.28)
    for row_y in (y0 + m(7), y0 + h - m(7)):
        for k in range(n):
            bx = x0 + notch + int((w - 2 * notch) * (k / (n - 1)))
            _alpha_aura(big, bx, row_y, m(4), pal["gem"], peak=22, layers=5)
            pygame.draw.circle(big, bulb_fill, (bx, row_y), bulb_r)
            pygame.draw.circle(big, bulb_rim,  (bx, row_y), bulb_r, max(1, m(0.5)))

    # Tier word — embossed, cream-tinted gem colour, auto-fit to span.
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


def _hero_disc(big, sid, pal):
    """Overhanging cabochon medallion drawn last so it crowns the banner.
    Tier aura reaches into transparent headroom above the card, unclipped."""
    cx, cy, r = m(CX), m(DISC_CY), m(R_HERO)
    _hero_aura(big, cx, cy, r, pal["glow"])
    cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(r * 1.5))
    cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    # crisp tier gem ring — the tier hue is unmistakable on the medallion rim
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
GUT    = 26
MARGIN = 26
HEAD   = 62
CANVAS_W = MARGIN * 2 + POP_W * 3 + GUT * 2
CANVAS_H = HEAD + POP_H + 34

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
for y in range(CANVAS_H):
    pygame.draw.line(canvas, lerp_color((10, 11, 26), (5, 5, 14), y / CANVAS_H),
                     (0, y), (CANVAS_W, y))

title = _font(19, True).render(
    "confirm_purchase_v6 — spotlight-marquee  (round 2)", True, (232, 226, 208))
canvas.blit(title, (MARGIN, 16))
sub = _font(11, True).render(
    "tier bloom anchored on disc · near-white smear gone · taller tier-hued banner "
    "· cone visible in disc–banner gap · consistent layout all three tiers",
    True, (150, 156, 178))
canvas.blit(sub, (MARGIN, 38))

lab = _font(13, True)
for i, (tier_word, sid, price, pal) in enumerate(TIERS):
    pop = render_popup(tier_word, sid, price, pal)
    px = MARGIN + i * (POP_W + GUT)
    py = HEAD
    canvas.blit(pop, (px, py))
    t = lab.render(tier_word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(t, t.get_rect(center=(px + POP_W // 2, py - 8)))

out = "/home/user/skybit/docs/confirm_purchase_v6/spotlight-marquee/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())
