#!/usr/bin/env python3
"""
gem-cut-panel confirm_purchase_v5 round 1 render.

Concept: a purchase popup whose four corners are cut at ~45deg into a shallow
gem-cut chamfer, giving an 8-sided faceted crystal silhouette. Each of the 8
edges (4 straight + 4 chamfer planes) carries a value-stepped bevel highlight
lit from the top-left, the same emboss logic as bevel_rim extended to the
angled corners. Fills stay SKY-BRIGHT (tier gem/glow) so the card reads as cut
GLASS, not a dark RPG gemstone.

Three tiers side by side: RARE (sky-blue), EPIC (purple), LEGENDARY (gold).
"""
import os, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, soft_glow, plain_text, price_chip, chip_body_stops, chip_body,
    _glyph_base, font, m, SS, cabochon, cabochon_glass, thumb, _rim_light,
    GOLD_A_STOPS, GOLD_A_RIM_DARK as GOLD_RIM_DK, GOLD_A_RIM_BRIGHT as GOLD_RIM_BR,
)
from game.hud import _font
from game.draw import lerp_color, WHITE, NEAR_BLACK

# Patch gloss_sweep so additive intensity lives in RGB magnitude, not alpha —
# on a bright glass body BLEND_ADD would otherwise blow the crown to white.
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

# ── tiers (brief palette; brighter glow than the store DNA on purpose) ──────────
TIERS = [
    ("RARE",      "skin_ninja",     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}),
    ("EPIC",      "skin_mummy",     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut", {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}),
]
PRICE = {"RARE": "1,500", "EPIC": "6,000", "LEGENDARY": "15,000"}

POP_W, POP_H = 208, 300
CX = POP_W // 2
CHAMFER = 21          # ~45deg corner cut, logical px
BEVEL_W = 7           # width of the faceted bevel frame band
R_DISC = 46
CY_DISC = 150

# top-left light unit vector, shared by every facet's value step
LX, LY = -0.7071, -0.7071


def octagon(x, y, w, h, c):
    """8 points clipping the four corners of a rect at ~45deg — the gem-cut
    silhouette. Clockwise from the top edge's left end."""
    return [
        (x + c, y), (x + w - c, y),           # top
        (x + w, y + c), (x + w, y + h - c),   # right
        (x + w - c, y + h), (x + c, y + h),   # bottom
        (x, y + h - c), (x, y + c),           # left
    ]


def facet_value(a, b, cx, cy, dk, mid, hi):
    """Value-step a bevel plane from ONE top-left light: the edge's outward
    normal dotted with the light gives dark(away)->lit(toward), crossfaded
    across three BRIGHT glass values so no facet ever reads as a deep jewel."""
    mx = (a[0] + b[0]) / 2 - cx
    my = (a[1] + b[1]) / 2 - cy
    ml = math.hypot(mx, my) or 1
    d = (mx / ml) * LX + (my / ml) * LY
    f = (d + 1) / 2
    return lerp_color(lerp_color(dk, mid, min(1.0, f * 2)),
                      hi, max(0.0, (f - 0.5) * 2))


def render_popup(tier_word, skin, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    x, y = m(9), m(9)
    w, h = POP_W * SS - m(18), POP_H * SS - m(18)
    c = m(CHAMFER)
    bw = m(BEVEL_W)
    cx, cy = x + w / 2, y + h / 2

    outer = octagon(x, y, w, h, c)
    inner = octagon(x + bw, y + bw, w - 2 * bw, h - 2 * bw, c)

    gem, glow, deep = pal["gem"], pal["glow"], pal["deep"]

    # ── body fill: a SKY-BRIGHT vertical glass gradient, masked to the octagon.
    # Pale lit crown -> saturated gem -> glow foot; never the deep jewel tone.
    body_stops = [
        (0.00, lerp_color(gem, WHITE, 0.52)),
        (0.42, lerp_color(gem, WHITE, 0.12)),
        (1.00, lerp_color(gem, glow, 0.55)),
    ]
    body = vgrad_stops(w, h, 0, body_stops, 255, gamma=1.05)
    omask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(omask, (255, 255, 255, 255),
                        [(px - x, py - y) for px, py in outer])
    body.blit(omask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # soft outer drop shadow, cast down-right from the top-left light
    sh = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    for i in range(m(6), 0, -1):
        a = int(150 * (i / m(6)) ** 1.7 / m(6) * 2.6)
        if a <= 0:
            continue
        off = octagon(x - i, y - i + m(3), w + 2 * i, h + 2 * i, c + i)
        pygame.draw.polygon(sh, (0, 0, 0, a), off)
    big.blit(sh, (0, 0))
    big.blit(body, (x, y))

    # ── faceted bevel frame: one quad per edge between outer + inner octagon,
    # each value-stepped by its own facing to the light -> a cut-crystal rim.
    dk = lerp_color(gem, glow, 0.72)          # shaded facet — still bright
    mid = lerp_color(gem, WHITE, 0.10)
    hi = lerp_color(gem, WHITE, 0.72)         # lit facet — bright glass
    for i in range(8):
        a, b = outer[i], outer[(i + 1) % 8]
        ib, ia = inner[(i + 1) % 8], inner[i]
        col = facet_value(a, b, cx, cy, dk, mid, hi)
        pygame.draw.polygon(big, col, [a, b, ib, ia])

    # crisp glass sheen over the crown, masked to the octagon
    sheen = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(int(h * 0.5)):
        av = int(70 * (1 - yy / (h * 0.5)) ** 1.5)
        pygame.draw.line(sheen, (255, 255, 255, av), (0, yy), (w, yy))
    sheen.blit(omask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(sheen, (x, y))

    # ── edge strokes: bright top-left bevel on lit edges, dim shadow on the
    # bottom-right, plus a dark outer keyline so the silhouette stays defined.
    lit = lerp_color(gem, WHITE, 0.85)
    shd = lerp_color(deep, NEAR_BLACK, 0.15)
    key = lerp_color(deep, NEAR_BLACK, 0.35)
    pygame.draw.polygon(big, key, outer, max(1, m(1.4)))
    # inner octagon glass rim for a double-cut read
    pygame.draw.polygon(big, (*lerp_color(gem, WHITE, 0.55), 150), inner, max(1, m(0.8)))
    for i in range(8):
        a, b = inner[i], inner[(i + 1) % 8]
        col = facet_value(a, b, cx, cy, (*shd, 200), (*gem, 60), (*lit, 235))
        pygame.draw.line(big, col, a, b, max(1, m(1.4)))

    # ── 1. TIER WORD — dominant top focal, tier gem fill + deep keyline so the
    # saturated word pops off the pale glass crown; generous tracking.
    sz = 30
    tf = font(sz)
    while _glyph_base(tier_word, tf, m(2.0)).get_width() > w - m(24) and sz > 10:
        sz -= 1
        tf = font(sz)
    plain_text(big, tier_word, tf, (int(cx), y + m(40)),
               lerp_color(gem, WHITE, 0.04), shadow_a=0,
               tracking=m(2.0), weight=m(1.4),
               keyline=lerp_color(deep, NEAR_BLACK, 0.1), kw=m(1.1))

    # ── 2. DISC — centred, two-part rim glow: additive glow bloom, then a crisp
    # gem ring. A cabochon dome holds the real item skin under glass.
    dcx, dcy = int(cx), y + m(CY_DISC - 9)
    soft_glow(big, dcx, dcy, m(R_DISC + 8), glow, 26, layers=9)
    cabochon(big, dcx, dcy, m(R_DISC))
    try:
        t = thumb(skin, int(m(R_DISC) * 1.5))
        rt = t.get_rect(center=(dcx, dcy))
        big.blit(_rim_light(t), rt.topleft, special_flags=pygame.BLEND_ADD)
        big.blit(t, rt)
    except Exception:
        pygame.draw.circle(big, gem, (dcx, dcy), int(m(R_DISC) * 0.6))
    cabochon_glass(big, dcx, dcy, m(R_DISC), tint=gem)
    # two-part rim: crisp bright gem ring seated over the glass bezel
    pygame.draw.circle(big, lerp_color(gem, WHITE, 0.3), (dcx, dcy),
                       m(R_DISC) + max(2, m(2.0)) // 2, max(2, m(2.4)))
    pygame.draw.circle(big, lerp_color(deep, NEAR_BLACK, 0.2), (dcx, dcy),
                       m(R_DISC) - m(2), max(1, m(1)))

    # ── 3. PRICE + CONFIRM — foot row.
    aff = tier_word != "LEGENDARY"   # show one locked state so both reads land
    price_chip(big, int(cx), y + h - m(52), PRICE[tier_word], m(22), affordable=aff)
    _confirm_chip(big, int(cx), y + h - m(22), m(24), aff)

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


def _confirm_chip(surf, cx, cy, h, affordable):
    text = "CONFIRM"
    f = font(h * 0.44 / SS)
    nw = _glyph_base(text, f, m(1.4)).get_width()
    pad = m(20)
    r = pygame.Rect(cx - (nw + pad * 2) // 2, cy - h // 2, nw + pad * 2, h)
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


# =============================================================================
# Compose the three-tier review canvas
# =============================================================================
GAP = 22
CANVAS_W = GAP + 3 * (POP_W + GAP)
CANVAS_H = POP_H + 78
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((10, 12, 24))

title = _font(19, True)
tt = title.render("confirm_purchase_v5  ·  gem-cut-panel  ·  round 1", True, (224, 228, 244))
canvas.blit(tt, tt.get_rect(midtop=(CANVAS_W // 2, 12)))

lab = _font(14, True)
for i, (word, skin, pal) in enumerate(TIERS):
    pop = render_popup(word, skin, pal)
    px = GAP + i * (POP_W + GAP)
    py = 50
    canvas.blit(pop, (px, py))
    t = lab.render(word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(t, t.get_rect(midtop=(px + POP_W // 2, py + POP_H + 6)))

out = "/home/user/skybit/docs/confirm_purchase_v5/gem-cut-panel/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())
