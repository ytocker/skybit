"""Round 5 — historical king crowns with bolder rendering.

Rounds 2, 3, 4 all rejected ("amateur" / "didn't like" / "horrible").
Hypothesis: the 3× smoothscale + thin DARK_GOLD borders at 36-46 px
targets washes out every edge — silhouettes blur into the gold row
no matter what shape they take. Real classical king crowns rely on a
bold black outline + iconic 3-5 element silhouette + one dominant
gem. This round changes the *rendering*, not just the designs.

Five crowns modelled on famous historical kings' crowns:

  crown_k1.png — St Edward's Crown      (UK coronation, 1661)
  crown_k2.png — Tudor Imperial Crown   (Henry VIII era)
  crown_k3.png — Iron Crown of Lombardy (heavy plated band, no top)
  crown_k4.png — Crown of Charlemagne   (Holy Roman, octagonal plates)
  crown_k5.png — Crown of St Wenceslaus (Bohemian, deep dome)

Pipeline changes:
  - 2× oversampling (down from 3×) — less smoothscale washout
  - Target sizes 56-64 px wide (up from 36-46)
  - Every gold shape gets a NEAR_BLACK outline pass
  - High-contrast 2-stop gold gradient (GOLD_HI → GOLD_LO)
  - Single dominant central gem per crown (radius ~3 * s)

Run from repo root:
  python3 tools/preview_crown_kings.py
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
from tools.preview_crown_grandiose import (
    GOLD_HI, GOLD, GOLD_LO, GOLD_DEEP,
    VELVET, VELVET_DK,
    PEARL, PEARL_SH,
    RUBY, RUBY_HI,
    SAPPHIRE, SAPPHIRE_HI,
    EMERALD, EMERALD_HI,
    DARK_GOLD, WHITE_HI,
    _with_shadow, _quad_bezier,
)

# ── Round-5 local palette / rendering primitives ────────────────────────────

NEAR_BLACK = (28, 18, 4)

OS = 2  # oversampling factor


def _oversampled2(draw_fn, w, h):
    """2× oversample + smoothscale — less washout than the 3× helpers
    used by rounds 2-4. The draw function must consume the actual
    surface size via big.get_width() / get_height()."""
    big = pygame.Surface((w * OS, h * OS), pygame.SRCALPHA)
    draw_fn(big, OS)
    return pygame.transform.smoothscale(big, (w, h))


def _gold_grad_rect2(surf, rect):
    """Two-stop GOLD_HI → GOLD_LO gradient. Less subtle than the
    three-stop version in preview_crown_grandiose — more punch at
    icon scale where mid-tones get lost."""
    x, y, w, h = rect
    for yy in range(h):
        u = yy / max(1, h - 1)
        col = tuple(int(GOLD_HI[i] * (1 - u) + GOLD_LO[i] * u)
                    for i in range(3))
        pygame.draw.line(surf, col + (255,),
                         (x, y + yy), (x + w - 1, y + yy))


def _band_outlined(big, s, band_l, band_top, band_r, band_bot,
                   outline_w=None):
    """Gold-gradient band with a NEAR_BLACK perimeter outline.
    `outline_w` defaults to 2 * s (≈ 1 final pixel after smoothscale)."""
    if outline_w is None:
        outline_w = 2 * s
    # Drop shadow
    pygame.draw.rect(big, NEAR_BLACK,
                     (band_l - 1, band_top + s,
                      band_r - band_l + 2, band_bot - band_top),
                     border_radius=s)
    # Gradient fill
    _gold_grad_rect2(big,
                     (band_l, band_top,
                      band_r - band_l, band_bot - band_top))
    # Dark perimeter outline (stronger than the prior thin DARK_GOLD)
    pygame.draw.rect(big, NEAR_BLACK,
                     (band_l, band_top,
                      band_r - band_l, band_bot - band_top),
                     border_radius=s, width=outline_w)


def _outlined_polygon(surf, pts, fill, hi=None):
    """Draw a filled polygon with a NEAR_BLACK outline. Outline drawn
    first (wider), then fill on top — leaves the outer 1-2 px of
    outline showing."""
    pygame.draw.polygon(surf, NEAR_BLACK, pts, max(2, OS * 2))
    pygame.draw.polygon(surf, fill, pts)
    if hi is not None and len(pts) >= 3:
        # Highlight on the upper-left half of the polygon
        # Use first vertex (assumed tip) + first edge midpoint
        mid = ((pts[0][0] + pts[1][0]) / 2,
               (pts[0][1] + pts[1][1]) / 2)
        pygame.draw.polygon(surf, hi, [pts[0], pts[1], mid])


def _outlined_gem(surf, cx, cy, r, col, hi):
    """Round cabochon gem with a NEAR_BLACK outline."""
    pygame.draw.circle(surf, NEAR_BLACK, (cx, cy + 1), r + 1)
    pygame.draw.circle(surf, col, (cx, cy), r)
    pygame.draw.circle(surf, hi,
                       (cx - max(1, r // 3), cy - max(1, r // 3)),
                       max(1, r // 2))
    # Dark perimeter — ensures gem reads against gold band
    pygame.draw.circle(surf, NEAR_BLACK, (cx, cy), r,
                       max(1, OS // 2))


def _outlined_velvet_dome(big, dome_rect):
    """Deep red velvet ellipse with darker right shading + dark outline."""
    pygame.draw.ellipse(big, NEAR_BLACK,
                        (dome_rect.x - 1, dome_rect.y - 1,
                         dome_rect.w + 2, dome_rect.h + 2))
    pygame.draw.ellipse(big, VELVET, dome_rect)
    pygame.draw.ellipse(big, VELVET_DK,
                        (dome_rect.x + dome_rect.w * 3 // 5,
                         dome_rect.y + dome_rect.h // 8,
                         dome_rect.w * 2 // 5,
                         dome_rect.h * 6 // 8))


def _outlined_arches(big, s, anchor_l, anchor_r, apex, ctrl_dy=None):
    """Two bezier arches from anchor_l + anchor_r converging to apex.
    NEAR_BLACK outline (thick) underneath, GOLD body, GOLD_HI inner
    highlight. ctrl_dy is the y-offset for the bezier control point."""
    if ctrl_dy is None:
        ctrl_dy = (anchor_l[1] - apex[1]) * 2 // 3
    ctrl_l_x = anchor_l[0] + s
    ctrl_r_x = anchor_r[0] - s
    arches = [
        _quad_bezier(anchor_l,
                     (ctrl_l_x, apex[1] + ctrl_dy), apex),
        _quad_bezier(anchor_r,
                     (ctrl_r_x, apex[1] + ctrl_dy), apex),
    ]
    arch_thick = max(2, OS)
    for arch in arches:
        pygame.draw.lines(big, NEAR_BLACK, False, arch,
                          arch_thick + 2 * s)
        pygame.draw.lines(big, GOLD_LO, False, arch, arch_thick + s)
        pygame.draw.lines(big, GOLD, False, arch, arch_thick)
    # Inner highlight on left arch
    pygame.draw.lines(big, GOLD_HI, False,
                      [(x, y - 1) for x, y in
                       arches[0][: len(arches[0]) // 2 + 1]],
                      max(1, s // 2))


def _outlined_fleur(big, s, cx, base_y, w, h):
    """Outlined fleur-de-lis: tall central petal, 2 side petals,
    horizontal binding bar. Every petal gets a NEAR_BLACK outline."""
    half = w // 2
    body_w = max(2, w // 5)

    # Centre petal
    c_tip = (cx, base_y - h)
    c_l   = (cx - body_w, base_y)
    c_r   = (cx + body_w, base_y)
    _outlined_polygon(big, [c_tip, c_l, c_r], GOLD, GOLD_HI)

    # Left side petal
    l_tip   = (cx - half, base_y - h * 2 // 3)
    l_inner = (cx - body_w, base_y - h // 3)
    l_base  = (cx - body_w, base_y)
    _outlined_polygon(big, [l_tip, l_inner, l_base], GOLD_LO)

    # Right side petal (mirror)
    r_tip   = (cx + half, base_y - h * 2 // 3)
    r_inner = (cx + body_w, base_y - h // 3)
    r_base  = (cx + body_w, base_y)
    _outlined_polygon(big, [r_tip, r_inner, r_base], GOLD_LO)

    # Horizontal binding bar
    bar_y = base_y - h * 2 // 5
    bar_h = max(2, h // 7)
    pygame.draw.rect(big, NEAR_BLACK,
                     (cx - half - 1, bar_y - 1, w + 2, bar_h + 2),
                     border_radius=bar_h // 2)
    pygame.draw.rect(big, GOLD,
                     (cx - half, bar_y, w, bar_h),
                     border_radius=bar_h // 2)


def _outlined_cross_pattee(big, s, cx, base_y, size):
    """Cross with flared arms, NEAR_BLACK outlined. `size` = total height."""
    h = size
    arm_thick = max(2, s + 1)
    flare = arm_thick + max(1, s)
    bar_y = base_y - h * 5 // 8

    # Vertical bar — outline + fill
    v_rect = (cx - arm_thick // 2, base_y - h, arm_thick, h)
    pygame.draw.rect(big, NEAR_BLACK,
                     (v_rect[0] - 1, v_rect[1] - 1,
                      v_rect[2] + 2, v_rect[3] + 2))
    pygame.draw.rect(big, GOLD, v_rect)

    # Horizontal bar
    h_rect = (cx - h // 2, bar_y, h, arm_thick)
    pygame.draw.rect(big, NEAR_BLACK,
                     (h_rect[0] - 1, h_rect[1] - 1,
                      h_rect[2] + 2, h_rect[3] + 2))
    pygame.draw.rect(big, GOLD, h_rect)

    # Flared tips (no outlines, would crowd the shape at icon scale)
    pygame.draw.rect(big, GOLD,
                     (cx - flare // 2, base_y - h,
                      flare, max(1, arm_thick // 2)))
    pygame.draw.rect(big, GOLD,
                     (cx - flare // 2, base_y - max(1, arm_thick // 2),
                      flare, max(1, arm_thick // 2)))


def _outlined_maltese(big, s, cx, top_y, h):
    """Maltese cross with flared arms on all four ends, NEAR_BLACK outlined."""
    arm_thick = max(2, s + 1)
    flare = arm_thick + max(2, s)
    h_y = top_y + h // 3

    # Vertical bar
    v_rect = (cx - arm_thick // 2, top_y, arm_thick, h)
    pygame.draw.rect(big, NEAR_BLACK,
                     (v_rect[0] - 1, v_rect[1] - 1,
                      v_rect[2] + 2, v_rect[3] + 2))
    pygame.draw.rect(big, GOLD, v_rect)

    # Horizontal bar
    h_rect = (cx - h // 3, h_y, h * 2 // 3, arm_thick)
    pygame.draw.rect(big, NEAR_BLACK,
                     (h_rect[0] - 1, h_rect[1] - 1,
                      h_rect[2] + 2, h_rect[3] + 2))
    pygame.draw.rect(big, GOLD, h_rect)

    # Flared tips (top + bottom + sides)
    flare_h = max(1, arm_thick // 2)
    pygame.draw.rect(big, GOLD,
                     (cx - flare // 2, top_y, flare, flare_h))
    pygame.draw.rect(big, GOLD,
                     (cx - flare // 2, top_y + h - flare_h, flare, flare_h))
    pygame.draw.rect(big, GOLD,
                     (cx - h // 3, h_y + arm_thick // 2 - flare // 2,
                      flare_h, flare))
    pygame.draw.rect(big, GOLD,
                     (cx + h // 3 - flare_h,
                      h_y + arm_thick // 2 - flare // 2,
                      flare_h, flare))


# ── K1: St Edward's Crown ───────────────────────────────────────────────────

def _draw_k1(big, s):
    """Heavy jeweled band, 5 alternating fleur/cross ornaments on the
    rim, 2 arches converging to a monde + cross apex, velvet dome
    behind. 60 × 56 px (target)."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    # Band
    band_top = 40 * s
    band_bot = 48 * s
    band_l = 4 * s
    band_r = bw - 4 * s
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)
    # Single dominant central sapphire
    band_cy = (band_top + band_bot) // 2
    _outlined_gem(big, cx, band_cy, 3 * s, SAPPHIRE, SAPPHIRE_HI)
    # Two small flanking rubies
    _outlined_gem(big, band_l + 6 * s, band_cy, s, RUBY, RUBY_HI)
    _outlined_gem(big, band_r - 6 * s, band_cy, s, RUBY, RUBY_HI)

    # Velvet dome (behind arches)
    dome_rect = pygame.Rect(cx - 15 * s, 14 * s, 30 * s, 27 * s)
    _outlined_velvet_dome(big, dome_rect)

    # 5 ornaments along the band top, alternating fleur + cross
    ornament_xs = [band_l + 4 * s, band_l + 12 * s, cx,
                   band_r - 12 * s, band_r - 4 * s]
    for i, ox in enumerate(ornament_xs):
        if i % 2 == 0:
            _outlined_fleur(big, s, ox, band_top, 6 * s, 7 * s)
        else:
            _outlined_cross_pattee(big, s, ox, band_top, 6 * s)

    # 2 arches converging at apex
    apex = (cx, 8 * s)
    _outlined_arches(big, s,
                     anchor_l=(band_l + 4 * s, band_top),
                     anchor_r=(band_r - 4 * s, band_top),
                     apex=apex)

    # Apex monde + Maltese cross
    _outlined_gem(big, apex[0], apex[1], 2 * s, GOLD, GOLD_HI)
    _outlined_maltese(big, s, apex[0],
                      top_y=apex[1] - 6 * s, h=5 * s)


def draw_crown_k1(surf, cx, cy):
    bw, bh = 60, 56
    img = _with_shadow(_oversampled2(_draw_k1, bw, bh))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── K2: Tudor Imperial Crown ────────────────────────────────────────────────

def _draw_k2(big, s):
    """Heavy band with 3 large gems, 5 alternating ornaments along the
    rim, tall pair of arches forming a deep dome, big apex cross.
    62 × 60 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    # Heavier band
    band_top = 42 * s
    band_bot = 52 * s
    band_l = 3 * s
    band_r = bw - 3 * s
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)
    band_cy = (band_top + band_bot) // 2
    # Three large gems on the band: ruby — large sapphire — ruby
    _outlined_gem(big, band_l + 8 * s, band_cy, int(2 * s), RUBY, RUBY_HI)
    _outlined_gem(big, cx,              band_cy, int(3 * s), SAPPHIRE, SAPPHIRE_HI)
    _outlined_gem(big, band_r - 8 * s,  band_cy, int(2 * s), RUBY, RUBY_HI)

    # Deep velvet dome
    dome_rect = pygame.Rect(cx - 16 * s, 12 * s, 32 * s, 31 * s)
    _outlined_velvet_dome(big, dome_rect)

    # 5 ornaments: cross — fleur — cross — fleur — cross
    ornament_xs = [band_l + 3 * s, band_l + 13 * s, cx,
                   band_r - 13 * s, band_r - 3 * s]
    for i, ox in enumerate(ornament_xs):
        if i % 2 == 0:
            _outlined_cross_pattee(big, s, ox, band_top, 7 * s)
        else:
            _outlined_fleur(big, s, ox, band_top, 6 * s, 8 * s)

    # Two tall arches converging at apex
    apex = (cx, 8 * s)
    _outlined_arches(big, s,
                     anchor_l=(band_l + 3 * s, band_top),
                     anchor_r=(band_r - 3 * s, band_top),
                     apex=apex)

    # Apex orb + Maltese cross
    _outlined_gem(big, apex[0], apex[1], int(2 * s), GOLD, GOLD_HI)
    _outlined_maltese(big, s, apex[0],
                      top_y=apex[1] - 6 * s, h=5 * s)


def draw_crown_k2(surf, cx, cy):
    bw, bh = 62, 60
    img = _with_shadow(_oversampled2(_draw_k2, bw, bh))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── K3: Iron Crown of Lombardy ──────────────────────────────────────────────

def _draw_k3(big, s):
    """Wide low gold ring. Six rectangular gem-plate cells across the
    band. No arches, no peaks — pure heavy ornate band. 60 × 30 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    band_top = 4 * s
    band_bot = 26 * s
    band_l = 2 * s
    band_r = bw - 2 * s
    _band_outlined(big, s, band_l, band_top, band_r, band_bot,
                   outline_w=2 * s)

    # 6 rectangular gem-plate cells across the band
    inner_l = band_l + 2 * s
    inner_r = band_r - 2 * s
    cell_w  = (inner_r - inner_l) // 6
    cell_top = band_top + 3 * s
    cell_bot = band_bot - 3 * s
    cell_gems = [(RUBY, RUBY_HI), (EMERALD, EMERALD_HI),
                 (SAPPHIRE, SAPPHIRE_HI), (RUBY, RUBY_HI),
                 (EMERALD, EMERALD_HI), (SAPPHIRE, SAPPHIRE_HI)]
    for i, (gc, gh) in enumerate(cell_gems):
        cell_l = inner_l + i * cell_w + s
        cell_r = inner_l + (i + 1) * cell_w - s
        # Recessed dark cell pocket
        pygame.draw.rect(big, NEAR_BLACK,
                         (cell_l - 1, cell_top - 1,
                          cell_r - cell_l + 2, cell_bot - cell_top + 2))
        pygame.draw.rect(big, GOLD_LO,
                         (cell_l, cell_top,
                          cell_r - cell_l, cell_bot - cell_top))
        # Gem inside the cell
        gem_cx = (cell_l + cell_r) // 2
        gem_cy = (cell_top + cell_bot) // 2
        gem_r = min(cell_r - cell_l, cell_bot - cell_top) // 2 - 1
        _outlined_gem(big, gem_cx, gem_cy, gem_r, gc, gh)

    # Hairline gold dividers between cells
    for i in range(1, 6):
        x = inner_l + i * cell_w
        pygame.draw.line(big, GOLD_HI,
                         (x, band_top + 2 * s),
                         (x, band_bot - 2 * s), max(1, s // 2))


def draw_crown_k3(surf, cx, cy):
    bw, bh = 60, 30
    img = _with_shadow(_oversampled2(_draw_k3, bw, bh))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── K4: Crown of Charlemagne ────────────────────────────────────────────────

def _draw_k4(big, s):
    """Octagonal-plated band: 4 visible plates alternating tall + short.
    Tall plates carry gems, short ones carry crosses pattée. Single
    arch crossing diagonally over the top, large Maltese cross at the
    apex. 58 × 52 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    # 4 octagonal plates spanning the bottom area
    band_bot = 44 * s
    short_top = 28 * s   # shorter plates
    tall_top  = 22 * s   # taller plates

    plate_w = (bw - 4 * s) // 4
    plate_xs = [2 * s + i * plate_w for i in range(5)]  # 5 boundaries → 4 plates

    plate_types = [True, False, True, False]  # tall, short, tall, short
    plate_gems  = [(RUBY, RUBY_HI), None, (EMERALD, EMERALD_HI), None]

    for i, (tall, gem_data) in enumerate(zip(plate_types, plate_gems)):
        l = plate_xs[i] + s
        r = plate_xs[i + 1] - s
        top = tall_top if tall else short_top
        # Outer outline
        pygame.draw.rect(big, NEAR_BLACK,
                         (l - 1, top - 1,
                          r - l + 2, band_bot - top + 2),
                         border_radius=s)
        # Fill
        _gold_grad_rect2(big, (l, top, r - l, band_bot - top))
        # Outline stroke
        pygame.draw.rect(big, NEAR_BLACK,
                         (l, top, r - l, band_bot - top),
                         border_radius=s, width=2 * s)
        # Decoration inside
        plate_cx = (l + r) // 2
        plate_cy = (top + band_bot) // 2
        if gem_data is not None:
            gc, gh = gem_data
            _outlined_gem(big, plate_cx, plate_cy + s,
                          int(2.5 * s), gc, gh)
        else:
            _outlined_cross_pattee(big, s, plate_cx, band_bot - s, 8 * s)

    # Single diagonal arch — bezier from one outer corner over the top
    # to the other. Less steep than the K1/K2 pair.
    arch_l = (plate_xs[0] + 2 * s, tall_top)
    arch_r = (plate_xs[4] - 2 * s, tall_top)
    apex   = (cx, 6 * s)
    arch_pts = _quad_bezier(arch_l, (cx, apex[1]), arch_r, n=24)
    pygame.draw.lines(big, NEAR_BLACK, False, arch_pts,
                      4 * s)
    pygame.draw.lines(big, GOLD_LO, False, arch_pts, 3 * s)
    pygame.draw.lines(big, GOLD, False, arch_pts, 2 * s)
    pygame.draw.lines(big, GOLD_HI, False,
                      [(x, y - 1) for x, y in arch_pts[:len(arch_pts) // 2 + 1]],
                      max(1, s // 2))

    # Large Maltese cross at the apex
    _outlined_gem(big, apex[0], apex[1], 2 * s, GOLD, GOLD_HI)
    _outlined_maltese(big, s, apex[0],
                      top_y=apex[1] - 6 * s, h=5 * s)


def draw_crown_k4(surf, cx, cy):
    bw, bh = 58, 52
    img = _with_shadow(_oversampled2(_draw_k4, bw, bh))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── K5: Crown of Saint Wenceslaus ───────────────────────────────────────────

def _draw_k5(big, s):
    """Bohemian crown: jeweled band, 4 large fleurs-de-lis along the
    rim (no crosses pattée), 2 arches forming a deep dome, large
    central ruby. 60 × 58 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    band_top = 42 * s
    band_bot = 50 * s
    band_l = 4 * s
    band_r = bw - 4 * s
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)
    band_cy = (band_top + band_bot) // 2
    # Dominant central ruby
    _outlined_gem(big, cx, band_cy, 3 * s, RUBY, RUBY_HI)
    # Two flanking emeralds
    _outlined_gem(big, band_l + 7 * s, band_cy, s, EMERALD, EMERALD_HI)
    _outlined_gem(big, band_r - 7 * s, band_cy, s, EMERALD, EMERALD_HI)

    # Deep velvet dome
    dome_rect = pygame.Rect(cx - 16 * s, 12 * s, 32 * s, 31 * s)
    _outlined_velvet_dome(big, dome_rect)

    # 4 large fleurs-de-lis along the band top
    fleur_xs = [cx - 21 * s, cx - 7 * s, cx + 7 * s, cx + 21 * s]
    for fx in fleur_xs:
        _outlined_fleur(big, s, fx, band_top, 7 * s, 9 * s)

    # 2 arches converging at apex (deep dome — apex higher)
    apex = (cx, 7 * s)
    _outlined_arches(big, s,
                     anchor_l=(band_l + 4 * s, band_top),
                     anchor_r=(band_r - 4 * s, band_top),
                     apex=apex)

    # Apex orb + small cross
    _outlined_gem(big, apex[0], apex[1], 2 * s, GOLD, GOLD_HI)
    _outlined_maltese(big, s, apex[0],
                      top_y=apex[1] - 5 * s, h=4 * s)


def draw_crown_k5(surf, cx, cy):
    bw, bh = 60, 58
    img = _with_shadow(_oversampled2(_draw_k5, bw, bh))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── Render ──────────────────────────────────────────────────────────────────

OUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

CROWNS = [
    ("crown_k1.png", draw_crown_k1, "St Edward's Crown"),
    ("crown_k2.png", draw_crown_k2, "Tudor Imperial Crown"),
    ("crown_k3.png", draw_crown_k3, "Iron Crown of Lombardy"),
    ("crown_k4.png", draw_crown_k4, "Crown of Charlemagne"),
    ("crown_k5.png", draw_crown_k5, "Crown of St Wenceslaus"),
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
