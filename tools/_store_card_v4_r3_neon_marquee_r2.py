"""neon-marquee — store_card_v4_r3 concept, round 2 headless render.

Visual thesis unchanged from round 1: a single thin neon tube runs along the
plinth top and dips into a bottom-only U cradle under the hero disc, so the
disc reads as resting in a lit socket at the card floor.

Round 2 implements all art-director notes from round 1 critique:
  * Cradle deepened to rc = m(R+5) — U-dip is now ~7 display px (was ~3.5),
    so the disc base visibly nests rather than skimming an almost-flat arc.
  * Contact bloom added at the cradle's lowest point — a tight additive soft_glow
    dab (rarity glow color, peak alpha 60, radius m(10)) that reads as the glow
    of a lit socket under the disc without overpowering the tube restraint.
  * Price numerals drop the thousands comma — 520 / 1400 / 3500 read cleanly
    at 162px width and gain a glyph-width of breathing room.
  * Tube core now tapers on the flat horizontal runs: full brightness (alpha 236)
    only in the cradle arc; flat runs use a reduced baseline (170) with the
    outer 15% of each side fading to 60 at the card edge — wire vs. source.
  * Plinth top seam firmed: a 1px lit micro-bevel (CARD_RING_BRIGHT, alpha 180)
    sits directly above the dark keyline so the foot reads as a discrete plate.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200 panels, no downscale). Not wired into the live store; writes
docs/store_card_v4_r3/neon-marquee/round_2.png.
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

# Cream shared by the name AND escutcheon numerals.
CREAM = (246, 244, 232)


def _neon_path(rect, cx, cy_abs, rc, plinth_top):
    """Build the neon tube centreline: flat along the plinth top, dipping into
    a concentric-arc cradle under the disc bottom.  The arc is clamped to the
    plinth-top height at its ends so it flows seamlessly into the flat runs —
    a bottom-only U that never rises past the disc's equator."""
    s = max(-1.0, min(1.0, (plinth_top - cy_abs) / rc))
    a = math.asin(s)
    th_r = a
    th_l = math.pi - a
    pts = [(rect.left, plinth_top)]
    steps = 30
    for i in range(steps + 1):
        th = th_l + (th_r - th_l) * i / steps
        pts.append((cx + rc * math.cos(th), cy_abs + rc * math.sin(th)))
    pts.append((rect.right, plinth_top))
    return pts


def _neon_tube(big, pts, glow_col, core_col):
    """Draw the neon tube.

    Glow layers are applied across the full path at restrained additive alphas
    so the tube reads as jewel-grade accent, not a neon sign.  The 1px core is
    split into three zones: the cradle arc receives full brightness (alpha 236);
    flat runs use a dimmer baseline (170) so they read as wire rather than
    source; the outer 15% of each flat run tapers further to 60 at the card
    edge, reinforcing that the cradle is where light emanates.
    """
    # Glow: three tight layers over the full path.
    glow = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    for w, a in ((m(5.0), 24), (m(3.2), 46), (m(2.0), 78)):
        pygame.draw.lines(glow, (*glow_col, a), False, pts, max(1, int(w)))
    big.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # Core alpha zones.
    MAX_A  = 236   # cradle arc — light source
    FLAT_A = 170   # flat run baseline — wire, reduced brightness
    EDGE_A =  60   # outermost edge after taper
    TAPER  = 0.15  # fraction of each flat run that tapers
    cw = max(1, m(1))

    def _fseg(surf, col, p0, p1, a0, a1, w):
        """Sub-segment line with per-step alpha interpolation from a0 to a1."""
        L = math.dist(p0, p1)
        if L < 1:
            return
        N = max(2, int(L / 1.5))
        for i in range(N):
            t0, t1 = i / N, (i + 1) / N
            a = max(0, min(255, int(a0 + (a1 - a0) * (t0 + t1) * 0.5)))
            sx0 = int(p0[0] + (p1[0] - p0[0]) * t0)
            sy0 = int(p0[1] + (p1[1] - p0[1]) * t0)
            sx1 = int(p0[0] + (p1[0] - p0[0]) * t1)
            sy1 = int(p0[1] + (p1[1] - p0[1]) * t1)
            pygame.draw.line(surf, (*col, a), (sx0, sy0), (sx1, sy1), w)

    core = pygame.Surface(big.get_size(), pygame.SRCALPHA)

    # Left flat run: pts[0] (card edge) → pts[1] (arc start).
    p0, p1 = pts[0], pts[1]
    if math.dist(p0, p1) >= 1:
        split = (p0[0] + (p1[0] - p0[0]) * TAPER,
                 p0[1] + (p1[1] - p0[1]) * TAPER)
        _fseg(core, core_col, p0, split, EDGE_A, FLAT_A, cw)   # taper zone
        _fseg(core, core_col, split, p1,   FLAT_A, FLAT_A, cw)  # wire zone

    # Cradle arc: pts[1:-1] — full source brightness.
    arc = pts[1:-1]
    if len(arc) >= 2:
        pygame.draw.lines(core, (*core_col, MAX_A), False, arc, cw)

    # Right flat run: pts[-2] (arc end) → pts[-1] (card edge).
    p0, p1 = pts[-2], pts[-1]
    if math.dist(p0, p1) >= 1:
        split = (p0[0] + (p1[0] - p0[0]) * (1.0 - TAPER),
                 p0[1] + (p1[1] - p0[1]) * (1.0 - TAPER))
        _fseg(core, core_col, p0,    split, FLAT_A, FLAT_A, cw)  # wire zone
        _fseg(core, core_col, split, p1,    FLAT_A, EDGE_A, cw)  # taper zone

    big.blit(core, (0, 0), special_flags=pygame.BLEND_ADD)


def _escutcheon(big, cx, cy, price, pal):
    """A small beveled tier-metal shield plate: deep->gem gradient, bevel_rim
    edge, coin glyph + cream numerals.  Price is rendered without a thousands
    comma to keep the numeral block compact at display size."""
    f = font(7.5)
    txt = f"{price}"                                 # no comma — cleaner at 162px
    nw = _glyph_base(txt, f, 0).get_width()
    coin_d = m(9)
    gap = m(3)
    padx = m(6)
    w = coin_d + gap + nw + padx * 2
    h = m(30)
    shoulder = int(h * 0.60)
    poly = [(0, 0), (w, 0), (w, shoulder), (w // 2, h - 1), (0, shoulder)]
    x0, y0 = cx - w // 2, cy - h // 2

    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 150), poly)
    big.blit(sh, (x0, y0 + m(2)))

    fill = vgrad_stops(w, h, 0, [(0.0, pal["deep"]), (1.0, pal["gem"])], 255,
                       gamma=1.06)
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    fill.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(fill, (x0, y0))

    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    dark = lerp_color(pal["deep"], NEAR_BLACK, 0.45)
    bright = lerp_color(pal["gem"], WHITE, 0.62)
    pygame.draw.polygon(big, dark, abspoly, width=max(1, m(1.6)))
    lit = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    inner = m(1.4)
    pygame.draw.line(lit, (*bright, 230), (x0 + inner, y0 + inner),
                     (x0 + w - inner, y0 + inner), max(1, m(1)))
    pygame.draw.line(lit, (*bright, 210), (x0 + inner, y0 + inner),
                     (x0 + inner, y0 + shoulder - m(1)), max(1, m(1)))
    big.blit(lit, (0, 0), special_flags=pygame.BLEND_ADD)

    row_cy = y0 + int(shoulder * 0.48)
    cxx = x0 + padx
    coin_glyph(big, cxx + coin_d // 2, row_cy, coin_d // 2)
    cxx += coin_d + gap
    plain_text(big, txt, f, (cxx + nw // 2, row_cy), CREAM, shadow_a=0,
               weight=m(0.8), keyline=(10, 8, 20), kw=m(0.8))


def _name_on_plinth(big, name, cx, cy, max_w):
    """Gilt/lit cream name centred on the plinth, auto-shrunk to fit."""
    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.0:
        sz -= 0.5
        f = font(sz)
    plain_text(big, name, f, (cx, cy), (250, 246, 226), shadow_a=150,
               weight=m(0.95), keyline=(4, 5, 14), kw=m(1.0))


def render_card(sid):
    """Draw ONE neon-marquee card onto a fresh SS panel (324x200) and return it."""
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

    # ── PLINTH — full-width near-black foot, clipped to the card's rounded
    #    bottom corners so it seats flush into the shell. ──
    cx = rect.left + m(40)
    cy = rect.y + m(38)
    plinth_top = rect.y + m(72)
    ph = rect.bottom - plinth_top
    plinth = vgrad_stops(rect.w, ph, 0,
                         [(0.0, (11, 12, 30)), (1.0, (5, 6, 18))], 255)
    body_mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(body_mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h),
                     border_radius=rad)
    plinth.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(plinth, (rect.left, plinth_top))

    # ── PLINTH TOP SEAM — a 1px lit micro-bevel immediately above the dark
    #    keyline makes the plinth read as a discrete raised plate rather than
    #    a gradient fade into the card body. ──
    bevel_y = plinth_top - max(1, m(1))
    bevel_surf = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(bevel_surf, (*CARD_RING_BRIGHT, 180),
                     (rect.left, bevel_y), (rect.right - 1, bevel_y),
                     max(1, m(1)))
    big.blit(bevel_surf, (0, 0))
    pygame.draw.line(big, (3, 4, 12), (rect.left, plinth_top),
                     (rect.right - 1, plinth_top), max(1, m(1)))

    # ── HERO DISC (R=36, left-leaning; base seats into the plinth cradle) ──
    # rc is deepened to m(R+5) so the U-dip is ~7 display px — the disc base
    # visibly nests in the cradle rather than skimming a near-flat arc.
    rc = m(R + 5)
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── NEON TUBE — flat along the plinth top, cradling the disc base in a
    #    bottom-only U.  Core brightness is highest in the cradle and tapers
    #    toward the card edges on the flat runs. ──
    pts = _neon_path(rect, cx, cy, rc, plinth_top)
    _neon_tube(big, pts, pal["glow"], lerp_color(pal["gem"], WHITE, 0.6))

    # ── CONTACT BLOOM — a tight additive glow dab at the cradle's lowest
    #    point (directly below the disc) simulates a pool of light in the
    #    socket where the disc base rests on the tube. ──
    bloom_cx = int(cx)
    bloom_cy = int(cy + rc)
    soft_glow(big, bloom_cx, bloom_cy, m(10), pal["glow"], 60, layers=4)

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── PRICE ESCUTCHEON — small tier-metal shield upper-right, clear of the
    #    disc and gem crest. ──
    _escutcheon(big, rect.right - m(23), rect.y + m(48), price, pal)

    # ── NAME — gilt cream, centred across the plinth below the tube. ──
    _name_on_plinth(big, name.upper(), rect.centerx, rect.y + m(81),
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
htxt = hfont.render("store_card_v4_r3 — neon-marquee — round 2", True,
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

out = "/home/user/skybit/docs/store_card_v4_r3/neon-marquee/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# ── L* probes — verify legibility unchanged after all round-2 edits ──
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
    plinth_bg = panel.get_at((r2.right - m(30), r2.y + m(81)))
    name_stroke = (250, 246, 226)
    print(f"  {tier:10s} plinth_bg L*={_lstar(plinth_bg):5.1f}  "
          f"name/plinth contrast={_contrast(name_stroke, plinth_bg):4.1f}:1")
