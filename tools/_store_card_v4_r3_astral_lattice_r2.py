"""astral-lattice — store_card_v4_r3 concept, round 2.

Art-director revision applied in priority order:
  1. Band pushed to near-true-black (BAND_BOT ~5,5,13) with internal top→bot
     value drop; gold horizon kiss strengthened to alpha 140.
  2. Lattice lines now read as warm gold — two-pass strokes (dark under-stroke
     for separation, bright CARD_RING_BRIGHT core at alpha 150, width m(1.0)),
     with a third hot pass on the landing wire only for the "glint where wire
     meets bezel" moment.
  3. Bezel-landing node is the hero: drawn last (on top of all hairlines and
     other nodes), largest pip (rp m(3.0)), hottest glow (peak 55), gold
     ambient halo, and a 4-point twinkle.
  4. Constellation vocabulary: 2 large stars (bez + p_low, both with 4-point
     twinkles) + 3 small pips; 4 ultra-faint single-pixel star-speckle dots
     in the band void for deep-space depth.
  5. Right-field declutter: node chain hugs the band→bezel arc, topmost node
     at only band.top - m(5), well clear of the price (band.top - m(20)).
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

from game.draw import lerp_color, WHITE
from game.hud import _font
from game import store_catalog
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, _glyph_base, _rarity,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, NEAR_BLACK,
)

CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36                          # hero disc radius (logical), left-leaning

# Pushed well past CARD_B=(12,13,38) toward true black: at this value the gold
# hairlines read "light on void" rather than "light on indigo". TOP stays a touch
# lighter so the strip has an internal top→bot value drop that sells it as a lit
# horizon band, not a flat rectangle.
BAND_TOP = (10, 10, 24)
BAND_BOT = (5, 5, 13)
GILT = (238, 206, 132)          # warm gilt for the name


def _draw_4pt_twinkle(surf, cx, cy, spike, color, alpha):
    """4-point axis-aligned cross-hair for large constellation nodes.
    The classic pointed-star vocabulary that distinguishes star-chart
    nodes from circuit-board dots. Tiny and short so the glow pip
    dominates; the spike is supporting punctuation, not the statement."""
    ext = spike + 4
    lyr = pygame.Surface((ext * 2, ext * 2), pygame.SRCALPHA)
    c = ext
    for dx, dy in [(spike, 0), (-spike, 0), (0, spike), (0, -spike)]:
        pygame.draw.line(lyr, (*color, alpha),
                         (c, c), (c + dx, c + dy), max(1, m(0.7)))
    surf.blit(lyr, (cx - c, cy - c))


def _draw_lattice(surf, rect, band, cx, cy, rd, pal):
    """Diagonal gold star-chart lines + tiered constellation nodes.

    Line approach: two-pass per segment — a dark NEAR_BLACK under-stroke
    (for separation against the deep band) then a warm CARD_RING_BRIGHT
    gold core at alpha 150, so the hue survives compositing.  The bezel
    landing wire gets a third ultra-bright pass so the eye reads a "glint
    where wire meets bezel."

    Node layout: 5 total, chained to hug the band→bezel arc. Topmost
    anchor sits at band.top - m(5) — well below the price (band.top - m(20))
    and the gem crest — so the lattice and price read as separate objects."""

    # Bezel-landing node: ~22° below disc horizontal so it sits just above
    # band.top, giving a clean horizon-crossing entry.
    ba = math.radians(22)
    bez = (cx + rd * math.cos(ba), cy + rd * math.sin(ba))

    # Chain designed to arc right-and-slightly-up from the band, never
    # drifting into the upper-right corner.
    p_low    = (rect.x + m(86),  band.top + m(8))   # secondary large star — in band
    p_mid    = (rect.x + m(102), band.top + m(3))   # small pip — upper band edge
    p_branch = (rect.x + m(118), band.top - m(2))   # small pip — just above band
    p_corner = (rect.x + m(132), band.top - m(5))   # small pip — right anchor

    # All links are diagonal (both x and y change) — never Manhattan / grid.
    links = [
        (p_low, bez),           # landing wire: band → bezel
        (p_low, p_mid),         # rightward band chain
        (p_mid, p_branch),      # rising right
        (p_branch, p_corner),   # far-right hop
        (p_low, p_branch),      # closure diagonal — triangulates into star-chart
    ]

    layer = pygame.Surface(rect.size, pygame.SRCALPHA)
    ox, oy = rect.topleft

    def lxy(pt):
        return (int(pt[0] - ox), int(pt[1] - oy))

    # Pass 1: all links — dark under + warm gold core
    for a, b in links:
        al, bl = lxy(a), lxy(b)
        pygame.draw.line(layer, (*NEAR_BLACK, 110), al, bl, max(2, m(1.6)))
        pygame.draw.line(layer, (*CARD_RING_BRIGHT, 150), al, bl, max(1, m(1.0)))

    # Pass 2: extra-bright redraw on the landing wire — the "glint where wire
    # meets bezel" that makes the disc look wired-up rather than merely adjacent.
    pygame.draw.line(layer, (*NEAR_BLACK, 70),
                     lxy(p_low), lxy(bez), max(2, m(2.0)))
    pygame.draw.line(layer, (*CARD_RING_BRIGHT, 215),
                     lxy(p_low), lxy(bez), max(1, m(1.2)))

    surf.blit(layer, rect.topleft)

    # Sparse star-field inside the band void — 4 ultra-faint single-pixel dots.
    # Background depth that reads "deep space" without competing with the hairlines.
    dr = int(cx + rd)
    for dx, dy in [(m(8), m(11)), (m(30), m(5)), (m(52), m(13)), (m(60), m(4))]:
        sx, sy = dr + dx, int(band.top + dy)
        if band.left < sx < band.right and band.top < sy < band.bottom:
            g = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(g, (*pal["glow"], 48), (2, 2), 1)
            surf.blit(g, (sx - 2, sy - 2))

    # --- Nodes drawn small→large so the hero bez ends up on top of everything --
    rp_sm = max(1, m(1.4))
    rp_lg = max(2, m(2.1))
    rp_hz = max(2, m(3.0))

    # Small pips (p_mid, p_branch, p_corner)
    for nx, ny in [(int(p_mid[0]),    int(p_mid[1])),
                   (int(p_branch[0]), int(p_branch[1])),
                   (int(p_corner[0]), int(p_corner[1]))]:
        soft_glow(surf, nx, ny, m(3.5), pal["glow"], 26, layers=5)
        pip = pygame.Surface((rp_sm * 2 + 4, rp_sm * 2 + 4), pygame.SRCALPHA)
        c = rp_sm + 2
        pygame.draw.circle(pip, (*pal["gem"], 255), (c, c), rp_sm)
        pygame.draw.circle(pip, (*lerp_color(pal["gem"], WHITE, 0.85), 255),
                           (c, c), max(1, int(rp_sm * 0.45)))
        surf.blit(pip, (nx - c, ny - c))

    # Secondary large star (p_low) — 4-point twinkle at m(5) spike length
    nx, ny = int(p_low[0]), int(p_low[1])
    soft_glow(surf, nx, ny, m(5.5), pal["glow"], 40, layers=7)
    _draw_4pt_twinkle(surf, nx, ny, m(5), CARD_RING_BRIGHT, 118)
    pip = pygame.Surface((rp_lg * 2 + 4, rp_lg * 2 + 4), pygame.SRCALPHA)
    c = rp_lg + 2
    pygame.draw.circle(pip, (*pal["gem"], 255), (c, c), rp_lg)
    pygame.draw.circle(pip, (*lerp_color(pal["gem"], WHITE, 0.9), 255),
                       (c, c), max(1, int(rp_lg * 0.45)))
    surf.blit(pip, (nx - c, ny - c))

    # HERO: bez node — drawn last so it sits above all hairlines and nodes.
    # Largest glow, hottest pip (near-white core), gold ambient halo, biggest
    # twinkle. This is the money moment — disc looks plugged into the star lattice.
    nx, ny = int(bez[0]), int(bez[1])
    soft_glow(surf, nx, ny, m(7.5), pal["glow"], 55, layers=8)
    soft_glow(surf, nx, ny, m(4.0), CARD_RING_BRIGHT, 28, layers=6)
    _draw_4pt_twinkle(surf, nx, ny, m(6), CARD_RING_BRIGHT, 168)
    pip = pygame.Surface((rp_hz * 2 + 4, rp_hz * 2 + 4), pygame.SRCALPHA)
    c = rp_hz + 2
    pygame.draw.circle(pip, (*CARD_RING_BRIGHT, 255), (c, c), rp_hz)
    pygame.draw.circle(pip, (*WHITE, 255), (c, c), max(1, int(rp_hz * 0.55)))
    surf.blit(pip, (nx - c, ny - c))


def _name_gilt(surf, name, band, disc_right):
    """Warm gilt name across the band's clear right zone, over a subtle darkening
    vgrad so the hairlines never fight the glyphs. Unchanged from r1 — legibility
    and placement were both correct."""
    zone_l = int(disc_right + m(4))
    zone_r = band.right - m(8)
    cxn = (zone_l + zone_r) // 2
    max_w = zone_r - zone_l
    pad_h = m(19)
    pad = vgrad_stops(max_w + m(12), pad_h, m(6),
                      [(0.0, (*NEAR_BLACK, 0)), (0.5, (*NEAR_BLACK, 150)),
                       (1.0, (*NEAR_BLACK, 0))], alpha=255)
    surf.blit(pad, (cxn - (max_w + m(12)) // 2, band.centery - pad_h // 2))

    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.0:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cxn, band.centery), GILT, shadow_a=0,
               weight=m(0.9), keyline=(4, 4, 12), kw=m(0.9))


def _price_phosphor(surf, text, cx, cy, pal):
    """Digit-only phosphor stencil — unchanged from r1: rarity-tint glowing
    numerals with a hairline bare coin token. No chip body."""
    f = font(11.5)
    nw = _glyph_base(text, f, 0).get_width()
    coin_r = m(5)
    gap = m(6)
    total = coin_r * 2 + gap + nw
    x0 = cx - total // 2
    coin_cx = x0 + coin_r
    num_cx = x0 + coin_r * 2 + gap + nw // 2

    soft_glow(surf, num_cx, cy, m(15), pal["glow"], 30, layers=8)
    pygame.draw.circle(surf, (*CARD_RING_BRIGHT, 200), (coin_cx, cy), coin_r,
                       max(1, m(0.8)))
    pygame.draw.circle(surf, (*CARD_RING_BRIGHT, 90), (coin_cx, cy),
                       coin_r - m(1.4), max(1, m(0.7)))
    phosphor = lerp_color(pal["glow"], WHITE, 0.30)
    plain_text(surf, text, f, (num_cx, cy), phosphor, shadow_a=0,
               weight=m(1.0), keyline=(*lerp_color(pal["deep"], NEAR_BLACK, 0.4),),
               kw=m(0.7))


def render_card(sid):
    """Draw ONE astral-lattice card onto a fresh SS panel and return it."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid).upper()
    price = f"{store_catalog.cost(sid):,}"

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

    # ── CELESTIAL BAND — near-true-black strip at the foot ──
    band = pygame.Rect(rect.x + m(9), rect.bottom - m(28),
                       rect.w - m(18), m(20))
    band_body = vgrad_stops(band.w, band.h, m(6),
                            [(0.0, BAND_TOP), (1.0, BAND_BOT)], alpha=236)
    big.blit(band_body, band.topleft)
    pygame.draw.rect(big, (2, 3, 10), band, width=max(1, m(1)),
                     border_radius=m(6))
    # Gold horizon kiss at alpha 140: a clean luminous top-edge horizon line
    pygame.draw.line(big, (*CARD_RING_BRIGHT, 140),
                     (band.x + m(8), band.top), (band.right - m(8), band.top),
                     max(1, m(0.8)))

    # ── HERO DISC (left-leaning) ──
    cx = rect.left + m(40)
    cy = rect.centery
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── LATTICE — after cabochon_glass so the bez hero node sits ON the glass ──
    _draw_lattice(big, rect, band, cx, cy, m(R), pal)

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── PRICE — phosphor stencil digits, right-biased above the band ──
    _price_phosphor(big, price, rect.right - m(52), band.top - m(20), pal)

    # ── NAME — warm gilt across the band's clear right zone ──
    _name_gilt(big, name, band, cx + m(R))

    return big


# ── review strip ───────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_tophat"),
    ("EPIC",      "skin_prism"),
    ("LEGENDARY", "skin_kitsune"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN = 10
GAP = 8
HEADER_H = 26
FOOTER_H = 22

sheet_w = MARGIN * 2 + PANEL_W * 3 + GAP * 2
sheet_h = MARGIN * 2 + HEADER_H + PANEL_H + FOOTER_H
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(20, True)
ffont = _font(17, True)
htxt = hfont.render("store_card_v4_r3 — astral-lattice — round 2", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GAP)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v4_r3/astral-lattice/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
