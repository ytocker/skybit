"""Round 3 crown previews — five grandiose redesigns.

Iteration on round 2 (preview_crown_redesigns.py), which the user
called "still amateur" + flagged a 3-4 px leftward centering bias.
This round goes wild: papal tiara stacks, imperial state arched
dome, sun-ray spike crown, byzantine laurel arch with pendants,
and an everything-included maximalist hybrid.

Each `_draw_g*(big, s)` reads its surface size via `big.get_width()`
and symmetrises around `cx = bw // 2`, so the art always lands on
the badge centre regardless of the wrapper's chosen target size.

Renders:
  crown_g1.png — Papal Tiara
  crown_g2.png — Imperial State
  crown_g3.png — Sun Crown
  crown_g4.png — Byzantine Laurel
  crown_g5.png — Maximalist Hybrid

Run from repo root:
  python3 tools/preview_crown_grandiose.py
"""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import sys
import pygame

pygame.init()
pygame.font.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import W, H
from tools.preview_crown_variants import (
    draw_leaderboard_variant, draw_bg, SCORES,
)


# ── Palette ─────────────────────────────────────────────────────────────────

GOLD_HI    = (255, 232, 132)
GOLD       = (240, 192,  64)
GOLD_LO    = (188, 138,  28)
GOLD_DEEP  = (110,  72,   8)
VELVET     = (140,  18,  22)
VELVET_DK  = ( 80,   8,  10)
PEARL      = (252, 248, 232)
PEARL_SH   = (200, 195, 175)
RUBY       = (220,  40,  50)
RUBY_HI    = (255, 180, 190)
SAPPHIRE   = ( 64, 102, 220)
SAPPHIRE_HI= (172, 200, 255)
EMERALD    = ( 64, 200, 100)
EMERALD_HI = (172, 240, 192)
FUR        = (245, 240, 230)
FUR_SH     = (170, 160, 145)
ERMINE     = ( 40,  30,  25)
DARK_GOLD  = (115,  85,  20)
WHITE_HI   = (255, 255, 255)


# ── Shared rendering helpers ────────────────────────────────────────────────

def _oversampled(draw_fn, w, h, s=3):
    """Render draw_fn onto an s×-oversampled surface, then smoothscale
    down to (w, h) for anti-aliased edges. The draw function must
    consume the actual surface size via big.get_width()/get_height()
    so it stays centred regardless of the wrapper's target dimensions."""
    big = pygame.Surface((w * s, h * s), pygame.SRCALPHA)
    draw_fn(big, s)
    return pygame.transform.smoothscale(big, (w, h))


def _with_shadow(img, offset=(2, 2), alpha=110):
    """Composite drop shadow under the crown so its silhouette pops
    against the gold #1 row instead of fading into the gradient."""
    shadow = img.copy()
    shadow.fill((0, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
    shadow.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    composite = pygame.Surface(
        (img.get_width() + offset[0], img.get_height() + offset[1]),
        pygame.SRCALPHA)
    composite.blit(shadow, offset)
    composite.blit(img, (0, 0))
    return composite


def _gold_grad_rect(surf, rect):
    """Vertical 3-stop gold gradient fill within `rect`."""
    x, y, w, h = rect
    for yy in range(h):
        u = yy / max(1, h - 1)
        if u < 0.4:
            t = u / 0.4
            col = tuple(int(GOLD_HI[i] * (1 - t) + GOLD[i] * t) for i in range(3))
        else:
            t = (u - 0.4) / 0.6
            col = tuple(int(GOLD[i] * (1 - t) + GOLD_LO[i] * t) for i in range(3))
        pygame.draw.line(surf, col + (255,),
                         (x, y + yy), (x + w - 1, y + yy))


def _quad_bezier(p0, p1, p2, n=18):
    """Quadratic-bezier polyline."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


def _gem(surf, cx, cy, r, col, hi, shadow_dy=1):
    """Round cabochon: dark drop-shadow ring + body fill + bright highlight."""
    pygame.draw.circle(surf, GOLD_DEEP, (cx, cy + shadow_dy), r + 1)
    pygame.draw.circle(surf, col, (cx, cy), r)
    pygame.draw.circle(surf, hi, (cx - max(1, r // 3), cy - max(1, r // 3)),
                       max(1, r // 2))


def _maltese_cross(surf, cx, top_y, h, thick, col, shadow=GOLD_DEEP):
    """Maltese-style cross: vertical + horizontal arms with flared tips.
    `top_y` is the top of the vertical arm, `h` is total height."""
    arm_thick = max(thick, 2)
    flare = arm_thick + max(1, thick // 2)
    v_top = top_y
    v_bot = top_y + h
    h_y = top_y + h // 3
    h_l = cx - h // 3
    h_r = cx + h // 3
    # Shadow
    pygame.draw.rect(surf, shadow,
                     (cx - arm_thick // 2 + 1, v_top + 1, arm_thick, h))
    pygame.draw.rect(surf, shadow,
                     (h_l + 1, h_y + 1, h_r - h_l, arm_thick))
    # Body — vertical
    pygame.draw.rect(surf, col,
                     (cx - arm_thick // 2, v_top, arm_thick, h))
    # Body — horizontal
    pygame.draw.rect(surf, col,
                     (h_l, h_y, h_r - h_l, arm_thick))
    # Flared tips (4 — top, bottom, left, right of cross)
    flare_h = max(1, arm_thick // 2)
    pygame.draw.rect(surf, col,
                     (cx - flare // 2, v_top, flare, flare_h))
    pygame.draw.rect(surf, col,
                     (cx - flare // 2, v_bot - flare_h, flare, flare_h))
    pygame.draw.rect(surf, col,
                     (h_l, h_y + arm_thick // 2 - flare // 2, flare_h, flare))
    pygame.draw.rect(surf, col,
                     (h_r - flare_h, h_y + arm_thick // 2 - flare // 2, flare_h, flare))


def _pendant_strand(surf, x_top, y_top, x_bot, y_bot, n_pearls):
    """Hanging pearl strand from (x_top, y_top) to (x_bot, y_bot) with
    n_pearls evenly spaced + thin gold chain between them."""
    for i in range(1, n_pearls + 1):
        t = i / (n_pearls + 0.5)
        px = int(x_top + (x_bot - x_top) * t)
        py = int(y_top + (y_bot - y_top) * t)
        # Chain segment from previous anchor to here
        prev_t = (i - 1) / (n_pearls + 0.5)
        ppx = int(x_top + (x_bot - x_top) * prev_t)
        ppy = int(y_top + (y_bot - y_top) * prev_t)
        pygame.draw.line(surf, DARK_GOLD, (ppx, ppy), (px, py), 1)
        # Pearl
        pygame.draw.circle(surf, PEARL_SH, (px, py + 1), 2)
        pygame.draw.circle(surf, PEARL, (px, py), 2)
        pygame.draw.circle(surf, WHITE_HI, (px - 1, py - 1), 1)


def _aura(surf, cx, cy, radii, alphas):
    """Soft concentric golden halo behind the crown."""
    for r, a in zip(radii, alphas):
        glow = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (GOLD[0], GOLD[1], GOLD[2], a),
                            (0, 0, r * 2, r * 2))
        surf.blit(glow, (cx - r, cy - r))


# ── G1: Papal Tiara ─────────────────────────────────────────────────────────

def _draw_g1(big, s):
    """Three stacked gold bands (shrinking upward) topped by a Maltese
    cross. Velvet between tiers, gem row on each band. Tall narrow
    silhouette ≈ 36 × 38 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    # Tier 1 (bottom, widest)
    t1_l = 3 * s
    t1_r = bw - 3 * s
    t1_top, t1_bot = 28 * s, 34 * s
    # Velvet behind tier 1 (just narrow strip between tiers)
    pygame.draw.rect(big, VELVET,
                     (t1_l + s, 24 * s, t1_r - t1_l - 2 * s, t1_top - 24 * s))
    _gold_grad_rect(big, (t1_l, t1_top, t1_r - t1_l, t1_bot - t1_top))
    pygame.draw.rect(big, DARK_GOLD,
                     (t1_l, t1_top, t1_r - t1_l, t1_bot - t1_top),
                     border_radius=s, width=max(1, s // 2))
    # Tier 1 gems (5 across: ruby-sapphire-ruby-sapphire-ruby)
    t1_cy = (t1_top + t1_bot) // 2
    gem_cols = [(RUBY, RUBY_HI), (SAPPHIRE, SAPPHIRE_HI),
                (RUBY, RUBY_HI), (SAPPHIRE, SAPPHIRE_HI),
                (RUBY, RUBY_HI)]
    for i, (gc, gh) in enumerate(gem_cols):
        gx = t1_l + (i + 1) * (t1_r - t1_l) // 6
        _gem(big, gx, t1_cy, int(1.3 * s), gc, gh)

    # Tier 2 (middle)
    t2_l = 5 * s
    t2_r = bw - 5 * s
    t2_top, t2_bot = 21 * s, 26 * s
    pygame.draw.rect(big, VELVET,
                     (t2_l + s, 19 * s, t2_r - t2_l - 2 * s, t2_top - 19 * s))
    _gold_grad_rect(big, (t2_l, t2_top, t2_r - t2_l, t2_bot - t2_top))
    pygame.draw.rect(big, DARK_GOLD,
                     (t2_l, t2_top, t2_r - t2_l, t2_bot - t2_top),
                     border_radius=s, width=max(1, s // 2))
    t2_cy = (t2_top + t2_bot) // 2
    for i, (gc, gh) in enumerate(
            [(EMERALD, EMERALD_HI), (RUBY, RUBY_HI), (EMERALD, EMERALD_HI)]):
        gx = t2_l + (i + 1) * (t2_r - t2_l) // 4
        _gem(big, gx, t2_cy, int(1.2 * s), gc, gh)

    # Tier 3 (top, narrowest)
    t3_l = 8 * s
    t3_r = bw - 8 * s
    t3_top, t3_bot = 14 * s, 19 * s
    _gold_grad_rect(big, (t3_l, t3_top, t3_r - t3_l, t3_bot - t3_top))
    pygame.draw.rect(big, DARK_GOLD,
                     (t3_l, t3_top, t3_r - t3_l, t3_bot - t3_top),
                     border_radius=s, width=max(1, s // 2))
    t3_cy = (t3_top + t3_bot) // 2
    _gem(big, cx, t3_cy, int(1.6 * s), SAPPHIRE, SAPPHIRE_HI)

    # Small gold orb between tier 3 and the cross
    orb_cy = 11 * s
    _gem(big, cx, orb_cy, int(1.6 * s), GOLD, GOLD_HI, shadow_dy=1)

    # Maltese cross at apex
    _maltese_cross(big, cx, top_y=2 * s, h=7 * s, thick=s, col=GOLD)


def draw_crown_g1(surf, cx, cy):
    bw, bh = 36, 38
    img = _with_shadow(_oversampled(_draw_g1, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── G2: Imperial State ──────────────────────────────────────────────────────

def _draw_g2(big, s):
    """Heavy jeweled band, four arches converging to apex with cross
    orb, velvet dome inside, pendant pearls. ≈ 44 × 40 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    # Band
    band_top, band_bot = 26 * s, 33 * s
    band_l = 3 * s
    band_r = bw - 3 * s
    pygame.draw.rect(big, GOLD_DEEP,
                     (band_l - 1, band_top + s,
                      band_r - band_l + 2, band_bot - band_top),
                     border_radius=s)
    _gold_grad_rect(big,
                    (band_l, band_top, band_r - band_l, band_bot - band_top))
    pygame.draw.rect(big, DARK_GOLD,
                     (band_l, band_top, band_r - band_l, band_bot - band_top),
                     border_radius=s, width=max(1, s // 2))
    # 5 gems on band (sapphire-ruby-large emerald-ruby-sapphire)
    band_cy = (band_top + band_bot) // 2
    gem_positions = [
        (band_l + 4 * s, SAPPHIRE, SAPPHIRE_HI, int(1.4 * s)),
        (cx - 8 * s,     RUBY,     RUBY_HI,     int(1.5 * s)),
        (cx,             EMERALD,  EMERALD_HI,  int(2.0 * s)),
        (cx + 8 * s,     RUBY,     RUBY_HI,     int(1.5 * s)),
        (band_r - 4 * s, SAPPHIRE, SAPPHIRE_HI, int(1.4 * s)),
    ]
    for gx, gc, gh, gr in gem_positions:
        _gem(big, gx, band_cy, gr, gc, gh)

    # Velvet dome behind arches
    dome_rect = pygame.Rect(cx - 14 * s, 8 * s, 28 * s, 20 * s)
    pygame.draw.ellipse(big, VELVET, dome_rect)
    pygame.draw.ellipse(big, VELVET_DK,
                        (dome_rect.x + dome_rect.w * 3 // 5,
                         dome_rect.y + 2 * s,
                         dome_rect.w * 2 // 5,
                         dome_rect.h - 4 * s))

    # Four arches converging at apex
    apex = (cx, 8 * s)
    arch_thick = max(s, 2)
    arches = [
        # Outer arches start at band corners
        _quad_bezier((band_l + 2 * s, band_top),
                     (band_l + 3 * s, 9 * s), apex),
        _quad_bezier((band_r - 2 * s, band_top),
                     (band_r - 3 * s, 9 * s), apex),
        # Inner arches start nearer to centre
        _quad_bezier((cx - 7 * s, band_top),
                     (cx - 6 * s, 10 * s), apex),
        _quad_bezier((cx + 7 * s, band_top),
                     (cx + 6 * s, 10 * s), apex),
    ]
    for arch in arches:
        pygame.draw.lines(big, GOLD_DEEP, False,
                          [(x, y + s) for x, y in arch], arch_thick + s)
        pygame.draw.lines(big, GOLD_LO, False, arch, arch_thick + 1)
        pygame.draw.lines(big, GOLD, False, arch, arch_thick)
    # Highlight along the outer-left arch
    pygame.draw.lines(big, GOLD_HI, False,
                      [(x, y - 1) for x, y in arches[0][: len(arches[0]) // 2 + 1]],
                      max(1, s // 2))

    # Apex orb + Maltese cross
    _gem(big, apex[0], apex[1], 2 * s, GOLD, GOLD_HI, shadow_dy=1)
    _maltese_cross(big, apex[0], top_y=apex[1] - 8 * s, h=6 * s,
                   thick=s, col=GOLD)

    # Pendant pearls hanging from band sides (3 per side)
    _pendant_strand(big, band_l + 2 * s, band_bot,
                    band_l + 2 * s, band_bot + 7 * s, 3)
    _pendant_strand(big, band_r - 2 * s, band_bot,
                    band_r - 2 * s, band_bot + 7 * s, 3)


def draw_crown_g2(surf, cx, cy):
    bw, bh = 44, 40
    img = _with_shadow(_oversampled(_draw_g2, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── G3: Sun Crown ───────────────────────────────────────────────────────────

def _draw_g3(big, s):
    """Radial 9-spike crown with halo aura behind. Central sun-disc gem
    with gold ring. ≈ 44 × 36 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    # Aura behind everything
    _aura(big, cx, 29 * s,
          radii=[20 * s, 16 * s, 12 * s],
          alphas=[60, 100, 160])

    # Band first so spikes anchor onto it
    band_top, band_bot = 26 * s, 33 * s
    band_l = 5 * s
    band_r = bw - 5 * s
    pygame.draw.rect(big, GOLD_DEEP,
                     (band_l - 1, band_top + s,
                      band_r - band_l + 2, band_bot - band_top),
                     border_radius=s)
    _gold_grad_rect(big,
                    (band_l, band_top, band_r - band_l, band_bot - band_top))
    pygame.draw.rect(big, DARK_GOLD,
                     (band_l, band_top, band_r - band_l, band_bot - band_top),
                     border_radius=s, width=max(1, s // 2))

    # Nine radial spikes anchored on the band top
    angle_lengths = [
        (0,    22 * s),
        (-20,  18 * s), (20,  18 * s),
        (-35,  15 * s), (35,  15 * s),
        (-50,  12 * s), (50,  12 * s),
        (-65,  8 * s),  (65,  8 * s),
    ]
    anchor_y = band_top + 1
    for angle_deg, length in angle_lengths:
        a = math.radians(angle_deg)
        tip = (cx + math.sin(a) * length,
               anchor_y - math.cos(a) * length)
        # Base width tapers from ~1.5*s at the bottom
        bw_half = max(1, int(1.5 * s))
        # Construct triangle base perpendicular to the spike direction
        perp_a = a + math.pi / 2
        base_l = (cx + math.sin(a) * 0 + math.cos(perp_a) * bw_half,
                  anchor_y - math.cos(a) * 0 + math.sin(perp_a) * bw_half)
        base_r = (cx + math.sin(a) * 0 - math.cos(perp_a) * bw_half,
                  anchor_y - math.cos(a) * 0 - math.sin(perp_a) * bw_half)
        pygame.draw.polygon(big, GOLD_DEEP,
                            [(tip[0], tip[1] + 1),
                             (base_l[0] - 1, base_l[1] + 1),
                             (base_r[0] + 1, base_r[1] + 1)])
        pygame.draw.polygon(big, GOLD_LO, [tip, base_l, base_r])
        # Inner-facet highlight (only on the side facing centre)
        if angle_deg <= 0:
            pygame.draw.polygon(big, GOLD,
                                [tip, base_r,
                                 ((tip[0] + base_r[0]) / 2,
                                  (tip[1] + base_r[1]) / 2)])
        else:
            pygame.draw.polygon(big, GOLD,
                                [tip, base_l,
                                 ((tip[0] + base_l[0]) / 2,
                                  (tip[1] + base_l[1]) / 2)])
        pygame.draw.line(big, GOLD_HI,
                         (tip[0], tip[1]), base_l, max(1, s // 2))

    # Central sun-disc on the band
    sun_cy = (band_top + band_bot) // 2
    pygame.draw.circle(big, GOLD_DEEP, (cx, sun_cy + 1), 4 * s + 1)
    pygame.draw.circle(big, GOLD, (cx, sun_cy), 4 * s)
    pygame.draw.circle(big, GOLD_HI, (cx - s, sun_cy - s), 2 * s)
    _gem(big, cx, sun_cy, 2 * s, RUBY, RUBY_HI, shadow_dy=1)
    # White six-ray glint inside the ruby
    for k in range(6):
        ang = k * math.pi / 3
        ex = cx + math.cos(ang) * (1.5 * s)
        ey = sun_cy + math.sin(ang) * (1.5 * s)
        pygame.draw.line(big, WHITE_HI, (cx, sun_cy), (ex, ey), 1)


def draw_crown_g3(surf, cx, cy):
    bw, bh = 44, 36
    img = _with_shadow(_oversampled(_draw_g3, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── G4: Byzantine Laurel ────────────────────────────────────────────────────

def _draw_g4(big, s):
    """Arched gold band with laurel leaves, central frontispiece
    plaque with ruby + cross, pendant strands. ≈ 44 × 30 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    # Arched band: build a closed polygon = top bezier + bottom flat
    arch_l = (2 * s, 24 * s)
    arch_apex = (cx, 12 * s)
    arch_r = (bw - 2 * s, 24 * s)
    top_pts = _quad_bezier(arch_l, arch_apex, arch_r, n=30)
    bot_pts = [(arch_r[0], arch_r[1] + 4 * s),
               (arch_l[0], arch_l[1] + 4 * s)]
    band_polygon = top_pts + bot_pts
    # Shadow
    pygame.draw.polygon(big, GOLD_DEEP,
                        [(x, y + 1) for x, y in band_polygon])
    pygame.draw.polygon(big, GOLD_LO, band_polygon)
    # Highlight stripe along the top edge
    pygame.draw.lines(big, GOLD_HI, False,
                      [(x, y + 1) for x, y in top_pts],
                      max(1, s // 2))
    # Dark inner edge along the bottom
    pygame.draw.line(big, DARK_GOLD,
                     bot_pts[1], bot_pts[0], max(1, s // 2))

    # Laurel-leaf decoration along the top edge
    for i, (px, py) in enumerate(top_pts):
        if i % 3 == 0 and 2 < i < len(top_pts) - 3:
            tilt = (top_pts[i + 1][0] - top_pts[i - 1][0],
                    top_pts[i + 1][1] - top_pts[i - 1][1])
            ang = math.atan2(tilt[1], tilt[0]) + math.pi / 2
            lw, lh = int(1.4 * s), int(2.6 * s)
            # Build a small rotated ellipse via points
            leaf_color = EMERALD if (i // 3) % 2 == 0 else GOLD_HI
            pts = []
            for k in range(12):
                a = k * math.pi * 2 / 12
                ex = math.cos(a) * lw
                ey = math.sin(a) * lh
                rx = ex * math.cos(ang) - ey * math.sin(ang)
                ry = ex * math.sin(ang) + ey * math.cos(ang)
                pts.append((px + rx, py + ry - 2 * s))
            pygame.draw.polygon(big, GOLD_DEEP,
                                [(x, y + 1) for x, y in pts])
            pygame.draw.polygon(big, leaf_color, pts)
            pygame.draw.line(big, DARK_GOLD,
                             (px, py - 2 * s - lh + 1),
                             (px, py - 2 * s + lh - 1), 1)

    # Central frontispiece plaque
    plaque = pygame.Rect(cx - 3 * s, 13 * s, 6 * s, 11 * s)
    pygame.draw.rect(big, GOLD_DEEP,
                     (plaque.x + 1, plaque.y + 1, plaque.w, plaque.h),
                     border_radius=s)
    _gold_grad_rect(big, plaque)
    pygame.draw.rect(big, DARK_GOLD, plaque,
                     border_radius=s, width=max(1, s // 2))
    # Ruby orb on plaque
    _gem(big, cx, 19 * s, int(2.0 * s), RUBY, RUBY_HI)
    # Small gold cross above the plaque
    _maltese_cross(big, cx, top_y=5 * s, h=7 * s, thick=s, col=GOLD)

    # Side pendant strands
    _pendant_strand(big, arch_l[0] + 2 * s, arch_l[1] + 4 * s,
                    arch_l[0] + 2 * s, arch_l[1] + 4 * s + 6 * s, 3)
    _pendant_strand(big, arch_r[0] - 2 * s, arch_r[1] + 4 * s,
                    arch_r[0] - 2 * s, arch_r[1] + 4 * s + 6 * s, 3)


def draw_crown_g4(surf, cx, cy):
    bw, bh = 44, 30
    img = _with_shadow(_oversampled(_draw_g4, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── G5: Maximalist Hybrid ───────────────────────────────────────────────────

def _draw_g5(big, s):
    """Everything: ermine trim, two-tier band, velvet dome, arches,
    apex cross, pendants, gem cluster, aura. ≈ 46 × 42 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    # Aura behind everything
    _aura(big, cx, 24 * s,
          radii=[18 * s, 14 * s, 10 * s],
          alphas=[50, 90, 130])

    # Ermine fur strip at the bottom
    fur_top, fur_bot = 33 * s, 39 * s
    fur_l = 3 * s
    fur_r = bw - 3 * s
    pygame.draw.rect(big, FUR_SH,
                     (fur_l - 1, fur_top + 1,
                      fur_r - fur_l + 2, fur_bot - fur_top),
                     border_radius=s)
    pygame.draw.rect(big, FUR,
                     (fur_l, fur_top, fur_r - fur_l, fur_bot - fur_top),
                     border_radius=s)
    for sx in (fur_l + 4 * s, fur_l + 12 * s, fur_r - 4 * s):
        pygame.draw.circle(big, ERMINE, (sx, fur_top + 3 * s), max(1, s))

    # Tier 1: lower gold band
    t1_l, t1_r = 4 * s, bw - 4 * s
    t1_top, t1_bot = 24 * s, 32 * s
    pygame.draw.rect(big, GOLD_DEEP,
                     (t1_l - 1, t1_top + s,
                      t1_r - t1_l + 2, t1_bot - t1_top),
                     border_radius=s)
    _gold_grad_rect(big, (t1_l, t1_top, t1_r - t1_l, t1_bot - t1_top))
    pygame.draw.rect(big, DARK_GOLD,
                     (t1_l, t1_top, t1_r - t1_l, t1_bot - t1_top),
                     border_radius=s, width=max(1, s // 2))
    # Rose-cut gem cluster on tier 1
    cluster_cy = (t1_top + t1_bot) // 2
    _gem(big, cx, cluster_cy, 3 * s, RUBY, RUBY_HI)
    for k in range(6):
        ang = k * math.pi / 3 + math.pi / 6
        ox = cx + int(math.cos(ang) * 4.5 * s)
        oy = cluster_cy + int(math.sin(ang) * 4.5 * s)
        if 0 <= ox < bw and t1_top <= oy <= t1_bot:
            c, h = (SAPPHIRE, SAPPHIRE_HI) if k % 2 == 0 \
                else (EMERALD, EMERALD_HI)
            _gem(big, ox, oy, max(1, int(1.2 * s)), c, h)

    # Tier 2: upper narrow gold band
    t2_l, t2_r = 7 * s, bw - 7 * s
    t2_top, t2_bot = 19 * s, 23 * s
    pygame.draw.rect(big, VELVET,
                     (t2_l + s, t1_top - 2 * s,
                      t2_r - t2_l - 2 * s, t1_top - t2_bot))
    _gold_grad_rect(big, (t2_l, t2_top, t2_r - t2_l, t2_bot - t2_top))
    pygame.draw.rect(big, DARK_GOLD,
                     (t2_l, t2_top, t2_r - t2_l, t2_bot - t2_top),
                     border_radius=s, width=max(1, s // 2))
    t2_cy = (t2_top + t2_bot) // 2
    for i, (gc, gh) in enumerate(
            [(SAPPHIRE, SAPPHIRE_HI), (RUBY, RUBY_HI), (SAPPHIRE, SAPPHIRE_HI)]):
        gx = t2_l + (i + 1) * (t2_r - t2_l) // 4
        _gem(big, gx, t2_cy, int(1.1 * s), gc, gh)

    # Velvet dome above tier 2
    dome = pygame.Rect(cx - 11 * s, 7 * s, 22 * s, 16 * s)
    pygame.draw.ellipse(big, VELVET, dome)
    pygame.draw.ellipse(big, VELVET_DK,
                        (dome.x + dome.w * 3 // 5, dome.y + s,
                         dome.w * 2 // 5, dome.h - 2 * s))

    # Two arches converging at apex
    apex = (cx, 6 * s)
    arch_thick = max(s, 2)
    arches = [
        _quad_bezier((t2_l + 1 * s, t2_top),
                     (t2_l + 2 * s, 8 * s), apex),
        _quad_bezier((t2_r - 1 * s, t2_top),
                     (t2_r - 2 * s, 8 * s), apex),
    ]
    for arch in arches:
        pygame.draw.lines(big, GOLD_DEEP, False,
                          [(x, y + s) for x, y in arch], arch_thick + s)
        pygame.draw.lines(big, GOLD_LO, False, arch, arch_thick + 1)
        pygame.draw.lines(big, GOLD, False, arch, arch_thick)
    pygame.draw.lines(big, GOLD_HI, False,
                      [(x, y - 1) for x, y in arches[0][: len(arches[0]) // 2 + 1]],
                      max(1, s // 2))

    # Apex orb + Maltese cross
    _gem(big, apex[0], apex[1], 2 * s, GOLD, GOLD_HI, shadow_dy=1)
    _maltese_cross(big, apex[0], top_y=apex[1] - 7 * s, h=5 * s,
                   thick=s, col=GOLD)

    # Side pendant strands hanging from tier 1 corners
    _pendant_strand(big, t1_l + 1 * s, t1_bot,
                    t1_l + 1 * s, t1_bot + 6 * s, 3)
    _pendant_strand(big, t1_r - 1 * s, t1_bot,
                    t1_r - 1 * s, t1_bot + 6 * s, 3)


def draw_crown_g5(surf, cx, cy):
    bw, bh = 46, 42
    img = _with_shadow(_oversampled(_draw_g5, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── Render ──────────────────────────────────────────────────────────────────

OUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

CROWNS = [
    ("crown_g1.png", draw_crown_g1, "Papal Tiara"),
    ("crown_g2.png", draw_crown_g2, "Imperial State"),
    ("crown_g3.png", draw_crown_g3, "Sun Crown"),
    ("crown_g4.png", draw_crown_g4, "Byzantine Laurel"),
    ("crown_g5.png", draw_crown_g5, "Maximalist Hybrid"),
]


def main():
    screen = pygame.Surface((W, H))
    for fname, drawer, label in CROWNS:
        draw_bg(screen)
        draw_leaderboard_variant(
            screen, title_t=1.4, scores=SCORES,
            player_rank=6, variant=6, crown_drawer=drawer)
        out = os.path.join(OUT_DIR, fname)
        pygame.image.save(screen, out)
        print(f"saved {out}  ({label})")


if __name__ == "__main__":
    main()
