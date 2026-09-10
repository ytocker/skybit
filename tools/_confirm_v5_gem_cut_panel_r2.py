#!/usr/bin/env python3
"""
gem-cut-panel confirm_purchase_v5 round 2 — revised.

All five art-director mandatories addressed:

1. Disc rebuilt as bright tier-coloured gem well.  CABO_LO (centre, drawn
   last and topmost) and CABO_HI (rim) are both well above lum 100.
2. Additive bloom radiates OUTWARD with no dark seam:  BLEND_ADD ignores
   source alpha and adds raw RGB.  Every layer scales its circle RGB by
   ai/255 so the actual per-pixel addition is ai*ng_c/255 as intended — no
   accidental full-magnitude blowout.
3. Disc core stays tier-saturated to the centre.  Skin thumbnail removed so
   nothing buries the bright base; a thin specular crescent adds glass feel.
4. Tier word raised to 35 px cap-height starting point (auto-shrinks to
   floor 26 px for long words), reduced tracking, heavier stamp weight.
5. Glow colour normalised to perceptual lum ≈ 100 so the same bloom
   procedure yields matched brightness with a colour-swap only.
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, plain_text, price_chip, chip_body_stops, chip_body,
    _glyph_base, font, m, SS, GOLD_A_STOPS,
    GOLD_A_RIM_DARK  as GOLD_RIM_DK,
    GOLD_A_RIM_BRIGHT as GOLD_RIM_BR,
)
from game.hud import _font
from game.draw import lerp_color, WHITE, NEAR_BLACK


# ── mandatory gloss_sweep patch ───────────────────────────────────────────────
# BLEND_ADD uses RGB magnitude directly (source alpha is ignored), so the
# sheen must live in the RGB channels, not in alpha.
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


# ── tier palette ──────────────────────────────────────────────────────────────
TIERS = [
    ("RARE",      "skin_ninja",
     {"gem": (108, 188, 252), "glow": (60, 140, 230),  "deep": (18, 44, 90)}),
    ("EPIC",      "skin_mummy",
     {"gem": (194, 122, 248), "glow": (150, 60, 220),  "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut",
     {"gem": (255, 202, 104), "glow": (220, 160, 40),  "deep": (90, 50, 0)}),
]
PRICE = {"RARE": "1,500", "EPIC": "6,000", "LEGENDARY": "15,000"}

POP_W, POP_H = 208, 300
CHAMFER = 21
BEVEL_W = 7
R_DISC   = 46        # logical px
CY_DISC  = 152       # disc centre y from popup-body top, logical px

LX, LY = -0.7071, -0.7071


# ── geometry ──────────────────────────────────────────────────────────────────
def octagon(x, y, w, h, c):
    return [
        (x + c, y), (x + w - c, y),
        (x + w, y + c), (x + w, y + h - c),
        (x + w - c, y + h), (x + c, y + h),
        (x, y + h - c), (x, y + c),
    ]


def facet_value(a, b, cx, cy, dk, mid, hi):
    mx, my = (a[0] + b[0]) / 2 - cx, (a[1] + b[1]) / 2 - cy
    ml = math.hypot(mx, my) or 1
    d = (mx / ml) * LX + (my / ml) * LY
    f = (d + 1) / 2
    return lerp_color(lerp_color(dk, mid, min(1.0, f * 2)),
                      hi, max(0.0, (f - 0.5) * 2))


# ── glow normalisation ────────────────────────────────────────────────────────
def _lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _norm_glow(color, target=100.0):
    """Scale glow colour's perceptual luminance to `target` so the bloom
    yields equal visual brightness across all tiers (colour-swap only).
    Target=100 avoids channel clamping for all three tiers."""
    lum = _lum(color)
    if lum < 1:
        return color
    s = min(3.0, target / lum)
    return (min(255, int(color[0] * s)),
            min(255, int(color[1] * s)),
            min(255, int(color[2] * s)))


# ── disc primitives ───────────────────────────────────────────────────────────
def _bloom_outward(surf, cx, cy, r, glow, peak=55, layers=14):
    """BLEND_ADD rings that extend ~1.65× disc radius into card fill.

    BLEND_ADD ignores source alpha — raw RGB is added directly.  Each
    circle's colour is pre-scaled by ai/255 so the actual per-pixel
    contribution equals ai*ng_c/255, preventing blowout on the bright
    sky-fill card body."""
    ng = _norm_glow(glow)
    bloom_r = int(r * 2.65)
    for i in range(layers, 0, -1):
        ri  = int(bloom_r * i / layers)
        ai  = int(peak * (1 - (i - 1) / layers) ** 1.8)
        if ai <= 0 or ri <= 0:
            continue
        # Pre-scale RGB so BLEND_ADD adds ai*ng_c/255 per channel.
        rc  = max(0, ng[0] * ai // 255)
        gc  = max(0, ng[1] * ai // 255)
        bc  = max(0, ng[2] * ai // 255)
        if rc == 0 and gc == 0 and bc == 0:
            continue
        g   = pygame.Surface((ri * 2 + 2, ri * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (rc, gc, bc, 255), (ri + 1, ri + 1), ri)
        surf.blit(g, (cx - ri - 1, cy - ri - 1), special_flags=pygame.BLEND_ADD)


def _bright_gem_disc(surf, cx, cy, r, gem, glow, deep):
    """Bright tier-coloured gem disc — the second-brightest zone on the card.

    Stack (bottom to top):
      bloom outward → bright radial body → inner specular → gem ring.

    No skin thumbnail: the disc is a pure gem / crystal focal element.
    Both CABO equivalents (centro-lo and rim-hi) are well above lum 100
    for all three tiers, so the disc is never a dark hole."""

    # 1. Wide bloom first — glow field already present in card fill before
    #    disc body lands, ensuring no dark seam at disc–card boundary.
    _bloom_outward(surf, cx, cy, r, glow)

    # 2. Bright radial disc body.
    #    centro (drawn last / topmost): gem lerped strongly toward white
    #    rim (drawn first / outermost): gem-adjacent, still deeply saturated
    cabo_lo = lerp_color(gem, (255, 255, 255), 0.48)   # centre lum ≈ 200–230
    cabo_hi = lerp_color(gem, glow, 0.22)              # rim    lum ≈ 133–196

    pad  = m(4)
    dsz  = r * 2 + pad * 2
    disc = pygame.Surface((dsz, dsz), pygame.SRCALPHA)
    cc   = r + pad
    for i in range(r, 0, -1):
        col = lerp_color(cabo_lo, cabo_hi, (i / r) ** 1.28)
        pygame.draw.circle(disc, (*col, 255), (cc, cc), i)
    surf.blit(disc, (cx - cc, cy - cc))

    # 3. Top-left crescent specular — dome highlight for the glass surface.
    #    A bright circle offset up-left, with the overlapping inner-disc cut
    #    away, leaves a slim arc hugging the upper-left rim (the lit face).
    #    Peak=22 keeps BLEND_ADD additive contribution tight (raw RGB only).
    spec  = pygame.Surface((dsz, dsz), pygame.SRCALPHA)
    peak_sv = 22
    pygame.draw.circle(spec, (peak_sv, peak_sv, peak_sv, 255),
                       (cc - int(r * 0.25), cc - int(r * 0.25)), int(r * 0.72))
    # subtract interior offset-disc to carve the crescent shape
    cut = pygame.Surface((dsz, dsz), pygame.SRCALPHA)
    cut.fill((255, 255, 255, 255))
    pygame.draw.circle(cut, (0, 0, 0, 0),
                       (cc + int(r * 0.10), cc + int(r * 0.10)), int(r * 0.80))
    spec.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # mask to disc circle
    cm = pygame.Surface((dsz, dsz), pygame.SRCALPHA)
    pygame.draw.circle(cm, (255, 255, 255, 255), (cc, cc), r - m(2))
    spec.blit(cm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(spec, (cx - cc, cy - cc), special_flags=pygame.BLEND_ADD)

    # 4. Crisp bright gem ring — well-lit edge, not a dark trench.
    ring_col = lerp_color(gem, (255, 255, 255), 0.52)
    pygame.draw.circle(surf, ring_col, (cx, cy), r, max(2, m(2.5)))
    # Thin accent line inset from the ring for layered edge depth.
    pygame.draw.circle(surf, lerp_color(deep, (0, 0, 0), 0.12),
                       (cx, cy), r - m(2), max(1, m(0.8)))


# ── popup card ────────────────────────────────────────────────────────────────
def render_popup(tier_word, skin, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    x  = m(9)
    y  = m(9)
    w  = POP_W * SS - m(18)
    h  = POP_H * SS - m(18)
    c  = m(CHAMFER)
    bw = m(BEVEL_W)
    cx = x + w / 2
    cy = y + h / 2

    outer = octagon(x, y, w, h, c)
    inner = octagon(x + bw, y + bw, w - 2 * bw, h - 2 * bw, c)

    gem, glow, deep = pal["gem"], pal["glow"], pal["deep"]

    # ── card body: sky-bright octagon-masked gradient ─────────────────────────
    body_stops = [
        (0.00, lerp_color(gem, WHITE, 0.52)),
        (0.42, lerp_color(gem, WHITE, 0.12)),
        (1.00, lerp_color(gem, glow,  0.55)),
    ]
    body  = vgrad_stops(w, h, 0, body_stops, 255, gamma=1.05)
    omask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(omask, (255, 255, 255, 255),
                        [(px - x, py - y) for px, py in outer])
    body.blit(omask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # octagon drop shadow
    sh = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    for i in range(m(6), 0, -1):
        a = int(150 * (i / m(6)) ** 1.7 / m(6) * 2.6)
        if a <= 0:
            continue
        off_oct = octagon(x - i, y - i + m(3), w + 2 * i, h + 2 * i, c + i)
        pygame.draw.polygon(sh, (0, 0, 0, a), off_oct)
    big.blit(sh, (0, 0))
    big.blit(body, (x, y))

    # ── faceted bevel frame ───────────────────────────────────────────────────
    dk  = lerp_color(gem, glow, 0.72)
    mid = lerp_color(gem, WHITE, 0.10)
    hi  = lerp_color(gem, WHITE, 0.72)
    for i in range(8):
        a, b   = outer[i], outer[(i + 1) % 8]
        ib, ia = inner[(i + 1) % 8], inner[i]
        col    = facet_value(a, b, cx, cy, dk, mid, hi)
        pygame.draw.polygon(big, col, [a, b, ib, ia])

    # glass crown sheen (top half of octagon body)
    sheen = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(int(h * 0.5)):
        av = int(70 * (1 - yy / (h * 0.5)) ** 1.5)
        pygame.draw.line(sheen, (255, 255, 255, av), (0, yy), (w, yy))
    sheen.blit(omask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(sheen, (x, y))

    # edge strokes: outer keyline + value-stepped inner rim
    lit = lerp_color(gem, WHITE, 0.85)
    shd = lerp_color(deep, NEAR_BLACK, 0.15)
    key = lerp_color(deep, NEAR_BLACK, 0.35)
    pygame.draw.polygon(big, key, outer, max(1, m(1.4)))
    pygame.draw.polygon(big, (*lerp_color(gem, WHITE, 0.55), 150), inner, max(1, m(0.8)))
    for i in range(8):
        a, b = inner[i], inner[(i + 1) % 8]
        col  = facet_value(a, b, cx, cy, (*shd, 200), (*gem, 60), (*lit, 235))
        pygame.draw.line(big, col, a, b, max(1, m(1.4)))

    # ── 1. TIER WORD — top-third dominant focal ───────────────────────────────
    # Starts at 35 px cap-height; auto-shrinks to floor 26 px.  Reduced
    # tracking from R1 keeps LEGENDARY at ~29 px vs ~20 px previously.
    icx     = int(cx)
    tw_y    = y + m(40)
    sz      = 35
    tf      = font(sz)
    trk     = m(1.2)
    inner_w = w - 2 * bw - m(8)   # slightly wider budget → LEGENDARY stays ≥28px
    while _glyph_base(tier_word, tf, trk).get_width() > inner_w and sz > 26:
        sz -= 1
        tf  = font(sz)

    word_col = lerp_color(gem, WHITE, 0.06)
    word_kl  = lerp_color(deep, NEAR_BLACK, 0.08)
    plain_text(big, tier_word, tf, (icx, tw_y), word_col, shadow_a=0,
               tracking=trk, weight=m(1.5),
               keyline=word_kl, kw=m(1.2))

    # ── 2. DISC — bright gem well; second-brightest zone ──────────────────────
    dcx = icx
    dcy = y + m(CY_DISC)
    _bright_gem_disc(big, dcx, dcy, m(R_DISC), gem, glow, deep)

    # ── 3. PRICE + CONFIRM — foot row ─────────────────────────────────────────
    aff = (tier_word != "LEGENDARY")
    price_chip(big, icx, y + h - m(52), PRICE[tier_word], m(22), affordable=aff)
    _confirm_chip(big, icx, y + h - m(22), m(24), aff)

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


def _confirm_chip(surf, cx, cy, h, affordable):
    text = "CONFIRM"
    f    = font(h * 0.44 / SS)
    nw   = _glyph_base(text, f, m(1.4)).get_width()
    pad  = m(20)
    r    = pygame.Rect(cx - (nw + pad * 2) // 2, cy - h // 2, nw + pad * 2, h)
    if affordable:
        chip_body_stops(surf, r, h // 2, GOLD_A_STOPS, GOLD_RIM_DK, GOLD_RIM_BR,
                        gloss=64, gamma=1.04)
        col, kl = (54, 30, 4), None
    else:
        chip_body(surf, r, h // 2, (92, 98, 122), (50, 54, 76),
                  (14, 16, 28), (162, 170, 196), gloss=44)
        col, kl = (196, 202, 224), (20, 24, 40)
    plain_text(surf, text, f, r.center, col, shadow_a=0,
               tracking=m(1.4), weight=m(1.0), keyline=kl, kw=m(0.7))
    return r


# ── compose three-tier review canvas ─────────────────────────────────────────
GAP      = 22
CANVAS_W = GAP + 3 * (POP_W + GAP)
CANVAS_H = POP_H + 78
canvas   = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((10, 12, 24))

title_f = _font(19, True)
tt = title_f.render(
    "confirm_purchase_v5  ·  gem-cut-panel  ·  round 2", True, (224, 228, 244))
canvas.blit(tt, tt.get_rect(midtop=(CANVAS_W // 2, 12)))

lab_f = _font(14, True)
for i, (word, skin, pal) in enumerate(TIERS):
    pop = render_popup(word, skin, pal)
    px  = GAP + i * (POP_W + GAP)
    py  = 50
    canvas.blit(pop, (px, py))
    lt = lab_f.render(word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(lt, lt.get_rect(midtop=(px + POP_W // 2, py + POP_H + 6)))

OUT = "/home/user/skybit/docs/confirm_purchase_v5/gem-cut-panel/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
print("saved", OUT, canvas.get_size())
