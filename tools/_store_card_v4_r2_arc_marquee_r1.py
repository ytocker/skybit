"""arc-marquee — store_card_v4_r2 concept, round 1 headless render.

Visual thesis: the name band and the hero's stage light are the SAME event.
The band is the elliptical footprint where the spotlight pool lands on the
card floor — so the card's one warm light source (the disc) and the marquee
name-plate are read as a single continuous stage lamp, not two unrelated
panels.

  * The proven portrait-vignette lighting stack is reused verbatim: a shallow,
    wide _spotlight_vignette veil (peak 96) tracking the disc centre, then a
    warm additive _warm_core so the indigo collar reads genuinely lit.
  * The name band is ARC-shaped, not a rectangle: a cream-glass strip clipped
    to a wide, shallow dome top edge (apex only ~4.5 logical px above the
    baseline) — the pooled ellipse of light on the stage floor. It spans the
    full width, flush at the card bottom, and sits in front of the disc's
    lower rim like a lit ledge.
  * The price floats in the RIGHT COLLAR at disc mid-height (above the band,
    below the gem crest) on the lit indigo, so the band carries only the name
    and keeps its cap-height. The coin glyph is the one gold accent; numerals
    share the name's cream.
  * A warm additive glow rides the arc's top lip (drawn before the disc's
    catch-light and capped below it) so the pool reads as lit from the hero,
    never out-shining the disc specular.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200 panels, no downscale). Not wired into the live store; writes
docs/store_card_v4_r2/arc-marquee/round_1.png.
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
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    cabochon, cabochon_glass, blit_thumb, facet_gem, plain_text, soft_glow,
    coin_glyph, _glyph_base, _rarity, font, m, SS,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_DEEP, CARD_RING_BRIGHT,
    GEM_R, RARITY, MYSTERY, NEAR_BLACK,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Hero disc: R=34 leaves top headroom for the aura and a lit collar below the
# rim wide enough for the price to float clear of both gem and band.
R = 34

# Cream shared by the name AND the price numerals — one type value so gold never
# carries legibility (only the coin glyph is gold).
CREAM_LABEL = (236, 230, 208)

# The pooled-light band: a warm cream glass, deepening toward its floor edge so
# the cream name reads via its dark keyline like type lit on a stage floor.
BAND_STOPS = [(0.0, (224, 208, 170)), (1.0, (180, 160, 122))]


def _spotlight_vignette(surf, rect, spot, peak=104, reach=None, falloff=1.1):
    """Lay a radial stage-lamp veil over the indigo body: a uniform NEAR_BLACK
    sheet with a SHALLOW, WIDE light disc subtracted at `spot`, so a lit indigo
    COLLAR survives out to ~R60 and only the far corners keep the full veil.

    The light mask is built with BLEND_RGBA_MAX rings so the removed-veil alpha
    at distance d is exactly peak*(1-d/reach)**falloff — a clean radial falloff
    with no additive double-counting, hence no banding. Clipped to the body."""
    w, h = rect.w, rect.h
    sx, sy = spot
    if reach is None:
        reach = int(math.hypot(w, h) * 0.66)
    vig = pygame.Surface((w, h), pygame.SRCALPHA)
    vig.fill((*NEAR_BLACK, peak))
    light = pygame.Surface((w, h), pygame.SRCALPHA)
    layers = 84
    for i in range(layers, 0, -1):
        r = int(reach * i / layers)
        if r <= 0:
            continue
        frac = i / layers
        a = int(round(peak * (1 - frac) ** falloff))
        if a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (255, 255, 255, a), (r + 1, r + 1), r)
        light.blit(g, (sx - r - 1, sy - r - 1),
                   special_flags=pygame.BLEND_RGBA_MAX)
    vig.blit(light, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=m(CARD_RAD))
    vig.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(vig, rect.topleft)


def _warm_core(surf, cx, cy, radius, color=(30, 20, 8), peak=38, layers=24,
               exp=1.3):
    """A soft warm ADDITIVE glow at the lamp centre — the light the spotlight
    ADDS. Reaches out over the collar so the indigo annulus round the disc reads
    as genuinely lit (not merely un-shadowed black)."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak * (1 - (i - 1) / layers) ** exp)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


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
    pr = max(1, int(r * 0.17))
    pip = pygame.Surface((pr * 2 + m(2), pr * 2 + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 235), (pr + m(1), pr + m(1)), pr)
    off = int(r * 0.66)
    surf.blit(pip, (cx - pr - off, cy - pr - off),
              special_flags=pygame.BLEND_ADD)


def _arc_band(big, rect, rad):
    """Build the pooled-light name band: a cream-glass strip clipped to a wide
    shallow-dome top edge (the ellipse of spotlight on the stage floor), flush
    at the card bottom. Returns the band's absolute geometry so the name places
    inside it and the warm lip glow rides its top edge.

    The dome is a wide-circle sagitta: apex ~4.5 logical px above the baseline,
    so the arc never steals cap-height from the name — it just curves the top
    lip enough to read as a pool rather than a rectangle."""
    inset = m(2)
    bw = rect.w - inset * 2
    apex_h = m(17)                                 # band height at the dome apex
    sag = m(4.5)                                   # dome rise at the centre
    half = bw / 2.0
    # circle radius whose top arc rises exactly `sag` across the half-chord
    rc = (half * half + sag * sag) / (2 * sag)

    band_bottom_local = rect.h - inset             # flush at the card floor
    band_top_local = band_bottom_local - apex_h

    cream = vgrad_stops(bw, apex_h, 0, BAND_STOPS, alpha=210)
    # clip the strip to the dome: fill everything BELOW the wide arc (a huge
    # circle whose crown touches the strip top at centre).
    arc_mask = pygame.Surface((bw, apex_h), pygame.SRCALPHA)
    pygame.draw.circle(arc_mask, (255, 255, 255, 255),
                       (int(half), int(rc)), int(rc))
    cream.blit(arc_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # composite into a body-sized layer so the card's rounded bottom corners
    # trim the band's square corners.
    layer = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    layer.blit(cream, (inset, band_top_local))
    body_mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(body_mask, (255, 255, 255, 255),
                     (0, 0, rect.w, rect.h), border_radius=rad)
    layer.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(layer, rect.topleft)

    band_cx = rect.x + inset + int(half)
    band_top_abs = rect.y + band_top_local
    return {
        "cx": band_cx,
        "left": rect.x + inset,
        "right": rect.right - inset,
        "top": band_top_abs,
        "bottom": rect.y + band_bottom_local,
        "half": half,
        "rc": rc,
        "sag": sag,
    }


def _arc_lip_glow(big, band):
    """A warm additive glow riding the arc's top lip so the pool reads as lit by
    the same hero lamp. Kept BELOW the disc specular brightness so nothing on
    the card out-shines the catch-light."""
    n = 40
    pts = []
    for i in range(n + 1):
        x = -band["half"] + band["half"] * 2 * i / n
        dy = band["rc"] - math.sqrt(max(0.0, band["rc"] ** 2 - x * x))
        pts.append((band["cx"] + x, band["top"] + dy))
    glow = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    # wide dim feather then a tight warm crest — additive, capped well under the
    # near-white disc specular.
    pygame.draw.lines(glow, (255, 224, 150, 42), False, pts, max(1, m(3)))
    pygame.draw.lines(glow, (255, 232, 176, 96), False, pts, max(1, m(1.4)))
    big.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)


def _name_in_band(surf, name, cx, cy, max_w):
    """Cream item name with a tight dark keyline, auto-shrunk from 9.5pt in 0.5
    steps until it fits `max_w` — the keyline carries the cream-on-cream read so
    the name sits on the lit pool like stamped type."""
    sz = 9.5
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 6.0:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cx, cy), CREAM_LABEL, shadow_a=150,
               weight=m(0.9), keyline=(10, 8, 6), kw=m(0.9))


def render_card(sid):
    """Draw ONE arc-marquee card onto a fresh SS panel (324x200) and return it
    (drawn directly at SS, no smoothscale)."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, rect.y + m(43)          # top headroom for the aura

    # ── SHELL (locked order) ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    _spotlight_vignette(big, rect, (cx - rect.x, cy - rect.y), peak=96)
    _warm_core(big, cx, cy, m(60))
    contact_shadow(big, rect, rad, m(7), alpha=70)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── HERO DISC (base — specular deferred so it stays the brightest thing) ──
    soft_glow(big, cx, cy, m(R + 3), pal["glow"], 34, layers=9)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=55)
    blit_thumb(big, sid, cx, cy, m(R) * 0.66)
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── ARC MARQUEE — the spotlight pool on the stage floor, in front of the
    #    disc's lower rim; its warm lip glow rides the top edge. ──
    band = _arc_band(big, rect, rad)
    _arc_lip_glow(big, band)

    # disc catch-light LAST so the lip glow (and everything) sits under it.
    _hero_specular(big, cx, cy, m(R))

    # ── PRICE — floated in the right collar at disc mid-height, clear of the
    #    gem (above) and the band (below). Coin is the one gold; numerals cream.
    price_str = "480"
    pf = font(8.5)
    num_w = _glyph_base(price_str, pf, 0).get_width()
    coin_r = m(4.5)
    gap = m(3)
    price_cy = rect.y + m(43)
    # anchor from the disc rim outward so the coin never kisses the bezel — the
    # narrow right collar at disc mid-height is tight, so the cluster grows into
    # the free indigo toward the card edge.
    coin_cx = cx + m(R) + m(4) + coin_r
    num_cx = coin_cx + coin_r + gap + num_w // 2
    coin_glyph(big, coin_cx, price_cy, coin_r)
    plain_text(big, price_str, pf, (num_cx, price_cy), CREAM_LABEL,
               shadow_a=150, weight=m(0.9), keyline=(6, 6, 16), kw=m(0.8))

    # ── NAME — cream, biased left inside the arc band. ──
    band_h = band["bottom"] - band["top"]
    name_cy = band["bottom"] - band_h // 2 + m(1)
    max_w = rect.w - m(96)                         # left-biased, price-free band
    name_cx = band["left"] + m(8) + max_w // 2
    _name_in_band(big, name.upper(), name_cx, name_cy, max_w)

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

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(22, True)
ffont = _font(18, True)
htxt = hfont.render("store_card_v4_r2 — arc-marquee — round 1", True,
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

out = "/home/user/skybit/docs/store_card_v4_r2/arc-marquee/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# ── L* probes (no image display) — confirm the disc catch-light and the price
#    cell read against their grounds without ever viewing the PNG. ──
if "--probe" in sys.argv or True:
    def _lstar(rgb):
        def lin(c):
            c /= 255.0
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = (lin(v) for v in rgb[:3])
        y = 0.2126 * r + 0.7152 * g + 0.0722 * b
        return 903.3 * y if y <= 0.008856 else 116 * y ** (1 / 3) - 16

    r = pygame.Rect(m(_INSET), m(_INSET),
                    CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    dcx, dcy = r.centerx, r.y + m(43)
    for tier, sid in VARIANTS:
        panel = render_card(sid)
        # brightest disc catch-light pixel on the upper-left rim band
        best = 0.0
        for ang in range(120, 205, 5):
            rr = m(R) - m(4)
            px = dcx + int(rr * math.cos(math.radians(ang)))
            py = dcy + int(rr * math.sin(math.radians(ang)))
            best = max(best, _lstar(panel.get_at((px, py))))
        disc_c = _lstar(panel.get_at((dcx, dcy)))
        # collar ground the price floats on (between disc rim and the coin), a
        # numeral stroke peak, and the cream band ground under the name.
        collar = _lstar(panel.get_at((r.x + m(112), r.y + m(43))))
        numeral = _lstar(panel.get_at((r.right - m(16), r.y + m(43))))
        band_bg = _lstar(panel.get_at((r.x + m(60), r.bottom - m(9))))
        print(f"  {tier:10s} disc_center L*={disc_c:5.1f}  "
              f"disc_specular_peak L*={best:5.1f}  price_collar L*={collar:5.1f}  "
              f"price_numeral L*={numeral:5.1f}  band_ground L*={band_bg:5.1f}")
