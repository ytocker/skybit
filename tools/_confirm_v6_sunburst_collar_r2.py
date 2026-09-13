#!/usr/bin/env python3
"""
sunburst-collar  ·  confirm_purchase_v6  ·  round 2

Disc sits 100 logical px below the card top so 80–100 px of card body lies
above it — the tier-coloured sunburst fans freely upward into that space.
Upward rays fire at full brightness, downward rays throttled to 30% of that
peak. Ribbon threads through the disc lower-third via explicit z-order (lower
half drawn first → ribbon → upper half + glass redrawn on top). Disc glass
lifted to a brighter dome so the disc face and rarity word are the eye's first
landing. Rarity word anchored with a dark shadow pass + inner keyline stroke
so it reads on LEGENDARY gold where value contrast is weakest.
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
    vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, price_chip,
    cabochon, cabochon_glass, blit_thumb, _glyph_base, font, m, SS,
    CARD_T, CARD_B, CARD_RING_DEEP, CARD_RING_BRIGHT,
)
from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK, WHITE


# gloss_sweep patch — BLEND_ADD reads RGB magnitude only; alpha-driven sweep
# would silently blow gold chips to white, so sheen lives in RGB magnitude.
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


# ── tier palette (brief-exact) ────────────────────────────────────────────────
TIERS = [
    ("RARE",      "skin_wizard",    "720",
     {"gem": (108, 188, 252), "glow": (60, 140, 230),  "deep": (18, 44, 90)}),
    ("EPIC",      "skin_prism",     "1,400",
     {"gem": (194, 122, 248), "glow": (150, 60, 220),  "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut", "2,600",
     {"gem": (255, 202, 104), "glow": (220, 160, 40),  "deep": (90, 50, 0)}),
]

_NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}

# ── popup metrics (logical px — all flow through m()) ─────────────────────────
POP_W, POP_H = 278, 368
CX = POP_W // 2          # 139

CARD_X   = 12
CARD_TOP = 16
CARD_W   = POP_W - CARD_X * 2    # 254
CARD_H   = POP_H - CARD_TOP - 14  # 338
CARD_RAD = 17

R_DISC = 48
# Disc centre 100 px into card body → 84 px of card above it for bloom headroom
DISC_CY = CARD_TOP + 100          # 116  (popup-origin logical coords)

# Ribbon crosses the disc lower-third: centre at disc_cy + 0.40*R
RIBBON_CY = DISC_CY + int(R_DISC * 0.40)   # 135

Y_NAME = DISC_CY + R_DISC + 56   # 220
Y_CHIP = Y_NAME + 48              # 268

# Brighter dome glass so the disc face pops (lifted from the near-black defaults)
_DISC_LO = (54, 64, 118)
_DISC_HI = (22, 28, 76)


# =============================================================================
# Directional brightness — 100 % upward, 30 % downward, cosine blend
# =============================================================================
def _uf(angle_deg):
    """Up-factor for this screen angle. Pygame y↓ → screen angle 270° = up.
    Returns 1.0 straight up, 0.30 straight down, smooth cosine in between."""
    # -sin maps 270° → +1 (up), 90° → -1 (down)
    up_dot = -math.sin(math.radians(angle_deg))
    lo = 0.30
    return lo + (1.0 - lo) * ((up_dot + 1.0) * 0.5)


# =============================================================================
# Sunburst bloom — opaque dark buffer + BLEND_ADD keeps tier hue pure
# =============================================================================
def draw_sunburst(surf, cx, cy, pal, n_rays=48):
    """Tier-coloured sunburst radiating from the disc centre.

    Each ray is a trapezoid (narrow at disc rim, wider at tip), brightness
    and length scaled by _uf so the upper fan dominates. Built on an opaque
    black buffer and composited with BLEND_ADD — dark areas add 0 so the card
    body shows through; bright rays add their tier hue without white blowout
    (per-channel cap at 205 keeps saturation ceiling well clear of white)."""
    W, H = surf.get_size()
    buf = pygame.Surface((W, H))
    buf.fill((0, 0, 0))

    glow = pal["glow"]
    gem  = pal["gem"]
    # Tip colour: warm blend between glow and gem for sparkle
    tip = lerp_color(glow, gem, 0.32)

    r_inner    = m(R_DISC + 5)         # rays start just outside the disc rim
    r_outer_up = m(R_DISC + 86)        # max reach at full-brightness (up)

    for i in range(n_rays):
        angle = 360.0 * i / n_rays
        rad   = math.radians(angle)
        uf    = _uf(angle)

        # Keep magnitude low — hue survives, no channel clips to white
        cap = 205
        r_v = int(tip[0] * uf * cap / 255)
        g_v = int(tip[1] * uf * cap / 255)
        b_v = int(tip[2] * uf * cap / 255)
        if r_v + g_v + b_v == 0:
            continue

        r_outer = int(r_inner + (r_outer_up - r_inner) * uf)

        perp  = rad + math.pi * 0.5
        w_in  = m(2.0)
        w_out = m(3.8) + int(m(6.0) * uf)   # tips broaden with brightness

        pts = [
            (cx + r_inner * math.cos(rad) + w_in  * math.cos(perp),
             cy + r_inner * math.sin(rad) + w_in  * math.sin(perp)),
            (cx + r_inner * math.cos(rad) - w_in  * math.cos(perp),
             cy + r_inner * math.sin(rad) - w_in  * math.sin(perp)),
            (cx + r_outer * math.cos(rad) - w_out * math.cos(perp),
             cy + r_outer * math.sin(rad) - w_out * math.sin(perp)),
            (cx + r_outer * math.cos(rad) + w_out * math.cos(perp),
             cy + r_outer * math.sin(rad) + w_out * math.sin(perp)),
        ]
        pygame.draw.polygon(buf, (r_v, g_v, b_v),
                            [(int(x), int(y)) for x, y in pts])

    # Soft halo fills gaps between rays. Per-scanline brightness modulation
    # with the same directional rule — top rows bright, bottom rows dim.
    halo_r      = m(R_DISC + 62)
    halo_layers = 14
    for li in range(halo_layers, 0, -1):
        ri = int(halo_r * li / halo_layers)
        if ri <= 0:
            continue
        base_mag = int(68 * (1 - (li - 1) / halo_layers) ** 1.7)
        for dy in range(-ri, ri + 1):
            gy = cy + dy
            if gy < 0 or gy >= H:
                continue
            # frac: -1 = topmost row in circle, +1 = bottommost
            frac     = dy / ri
            row_uf   = 0.30 + 0.70 * max(0.0, (1.0 - frac) * 0.5)
            mag      = int(base_mag * row_uf * 0.46)
            if mag <= 0:
                continue
            r_v = int(glow[0] * mag / 255)
            g_v = int(glow[1] * mag / 255)
            b_v = int(glow[2] * mag / 255)
            dx  = int(math.sqrt(max(0, ri * ri - dy * dy)))
            x0  = max(0, cx - dx)
            x1  = min(W - 1, cx + dx)
            if x1 > x0:
                pygame.draw.line(buf, (r_v, g_v, b_v), (x0, gy), (x1, gy))

    surf.blit(buf, (0, 0), special_flags=pygame.BLEND_ADD)


# =============================================================================
# Disc helpers — explicit upper / lower split for ribbon threading
# =============================================================================
def _disc_lower(surf, sid, cx, cy, r, pal):
    """Cabochon + thumb, writing only to y ≥ disc centre (lower half).
    No glass here — glass is added with the upper half after the ribbon."""
    clip = pygame.Rect(cx - r - m(8), cy,
                       (r + m(8)) * 2, r + m(10))
    surf.set_clip(clip)
    cabochon(surf, cx, cy, r, _DISC_LO, _DISC_HI, ring=pal["gem"], ring_a=70)
    blit_thumb(surf, sid, cx, cy, int(r * 1.52))
    surf.set_clip(None)


def _disc_upper(surf, sid, cx, cy, r, pal):
    """Re-draw dome + thumb + glass clipped to y ≤ disc centre (upper half).
    Sits on top of the ribbon so the disc unmistakably wins its upper half.
    Rim ring drawn un-clipped so it straddles the split cleanly."""
    clip = pygame.Rect(cx - r - m(8), cy - r - m(10),
                       (r + m(8)) * 2, r + m(10))
    surf.set_clip(clip)
    cabochon(surf, cx, cy, r, _DISC_LO, _DISC_HI, ring=pal["gem"], ring_a=70)
    blit_thumb(surf, sid, cx, cy, int(r * 1.52))
    cabochon_glass(surf, cx, cy, r, tint=pal["gem"])
    surf.set_clip(None)

    # Tier-coloured rim ring drawn unclipped — straddles the midline naturally
    ring_w = max(3, m(2.6))
    pygame.draw.circle(surf, pal["gem"], (cx, cy),
                       r + ring_w // 2 + m(1), ring_w)
    pygame.draw.circle(surf, lerp_color(pal["deep"], NEAR_BLACK, 0.4),
                       (cx, cy), r - m(1), max(1, m(1)))


# =============================================================================
# Ribbon — wider than disc so tips flare past edges, rarity word protected
# =============================================================================
def draw_ribbon(surf, tier_word, cx, cy, pal):
    """Notched-hex ribbon wider than the disc diameter so chevron tips flare
    past the disc edges. Rarity word protected with a dark shadow pass + inner
    keyline stroke — legible on LEGENDARY gold where contrast is weakest."""
    # Tips flare R_DISC + 14 px past each disc edge
    w     = m(R_DISC * 2 + 28)
    h     = m(20)
    notch = m(7)
    x0, y0 = cx - w // 2, cy - h // 2

    top  = lerp_color(pal["gem"], WHITE, 0.12)
    bot  = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = vgrad_stops(w, h, 0,
                       [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                       255, gamma=1.08)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2),
            (w - notch, h), (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Drop shadow so ribbon sits proud
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 130), poly)
    surf.blit(sh, (x0, y0 + m(2)))
    surf.blit(body, (x0, y0))

    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(surf, (4, 5, 16), abspoly, width=max(1, m(1.6)))
    # Fine warm inner bevel on the top edge for definition
    edge_br = lerp_color(pal["gem"], WHITE, 0.44)
    inner_poly = [
        (x0 + px + (m(2) if px < w // 2 else -m(2)),
         y0 + py + (m(1.5) if py < h // 2 else -m(1.5)))
        for px, py in poly
    ]
    pygame.draw.polygon(surf, (*edge_br, 105), inner_poly, width=max(1, m(1)))

    # Rarity word — shadow pass first for legibility, then bright foreground
    f   = font(9.5)
    trk = m(1.8)
    shd = lerp_color(pal["deep"], NEAR_BLACK, 0.55)
    plain_text(surf, tier_word, f, (cx + m(1), cy + m(1.5)), shd,
               shadow_a=0, tracking=trk, weight=m(0.5))
    txt_col = lerp_color(pal["gem"], WHITE, 0.82)
    plain_text(surf, tier_word, f, (cx, cy), txt_col, shadow_a=0,
               tracking=trk, weight=m(0.62),
               keyline=lerp_color(pal["deep"], NEAR_BLACK, 0.45), kw=m(0.8))


# =============================================================================
# Full popup render
# =============================================================================
def render_popup(tier_word, sid, price, pal):
    big  = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    cx   = m(CX)
    cy   = m(DISC_CY)
    r    = m(R_DISC)
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad  = m(CARD_RAD)

    # ── 1. Card body ──────────────────────────────────────────────────────────
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(
        vgrad_stops(rect.w, rect.h, rad,
                    [(0.0, CARD_T), (1.0, CARD_B)], 252, gamma=1.15),
        rect.topleft,
    )
    top_sheen(big, rect, rad, m(28), peak=56)
    contact_shadow(big, rect, rad, m(9), alpha=115)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
              w=max(1, m(2.0)))

    # ── 2. Sunburst bloom (additive onto opaque card body — hue stays pure) ──
    draw_sunburst(big, cx, cy, pal)

    # ── 3. Disc lower half (behind ribbon) ───────────────────────────────────
    _disc_lower(big, sid, cx, cy, r, pal)

    # ── 4. Ribbon threaded through disc lower-third ───────────────────────────
    draw_ribbon(big, tier_word, cx, m(RIBBON_CY), pal)

    # ── 5. Disc upper half + glass redrawn over the ribbon ───────────────────
    _disc_upper(big, sid, cx, cy, r, pal)

    # ── 6. Item name + price chip ─────────────────────────────────────────────
    nf = font(13)
    plain_text(big, _NAMES[tier_word], nf, (m(CX), m(Y_NAME)),
               (250, 248, 240), shadow_a=150, weight=m(0.9),
               keyline=(6, 6, 16), kw=m(1.0))
    price_chip(big, m(CX), m(Y_CHIP), price, m(22), affordable=True)

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# =============================================================================
# Three-tier review sheet
# =============================================================================
GAP      = 22
MARGIN   = 24
HEAD     = 64
CANVAS_W = MARGIN * 2 + POP_W * 3 + GAP * 2
CANVAS_H = HEAD + POP_H + 44

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
for y in range(CANVAS_H):
    pygame.draw.line(
        canvas,
        lerp_color((11, 12, 27), (5, 5, 14), y / CANVAS_H),
        (0, y), (CANVAS_W, y),
    )

_hf = _font(19, True)
canvas.blit(
    _hf.render("confirm_purchase_v6  ·  sunburst-collar  ·  round 2",
               True, (232, 226, 208)),
    (MARGIN, 16),
)
canvas.blit(
    _font(11, True).render(
        "up-dominant bloom · disc 100 px into card · ribbon threaded · "
        "bright disc face · word protected",
        True, (150, 156, 178)),
    (MARGIN, 40),
)

lab = _font(13, True)
for i, (word, sid, price, pal) in enumerate(TIERS):
    pop = render_popup(word, sid, price, pal)
    px  = MARGIN + i * (POP_W + GAP)
    py  = HEAD
    canvas.blit(pop, (px, py))
    t = lab.render(word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(t, t.get_rect(midtop=(px + POP_W // 2, py + POP_H + 8)))

OUT = "/home/user/skybit/docs/confirm_purchase_v6/sunburst-collar/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
print("saved", OUT, canvas.get_size())
