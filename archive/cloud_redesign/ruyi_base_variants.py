"""5 surgical variations on the round-23 baseline Ruyi cloud.

Each variant paints the round-23 silhouette (3 lobes + base ribbon +
drop-shadow halo + arc keylines + dominant-lobe lit crescent) via a
shared internal _baseline_skeleton() helper, then applies ONE
surgical edit on top. Same family as the baseline by construction,
in contrast to ruyi_variants.py which deliberately diverged."""

from __future__ import annotations

import math
import random

import pygame

from cloud_variants import (
    _cloud_body_color, _ink_shadow_color, _lit_edge_color,
)
from ruyi_variants import (
    _ruyi_lobe, _ruyi_heart, _is_night, _lerp, _lerp_color,
    _seeded_jit, _alpha_surf,
)


# ── Local helpers ──────────────────────────────────────────────────────

def _pearl_dot(surf, cx, cy, r, color, edge_col, alpha):
    """Porcelain pearl bead: outer glow ring + 1-px edge contour + lit fill.
    The contour is what keeps the bead readable when it sits on top of the
    already-white lit crescent of a sunlit lobe in the DAY phase tile."""
    pad = int(r * 2.5)
    glow = _alpha_surf(pad * 2, pad * 2)
    pygame.draw.circle(glow, (*color, alpha // 3), (pad, pad), int(r * 2.0))
    pygame.draw.circle(glow, (*edge_col, min(255, alpha)), (pad, pad), r + 1, 1)
    pygame.draw.circle(glow, (*color, alpha), (pad, pad), r)
    surf.blit(glow, (cx - pad, cy - pad))


def _tassel_fringe(surf, x_top, y_top, length, body_col, accent_col, alpha):
    """Hanging silk tassel: 3-px knot + 3 fanned strands + cinnabar tip.
    Fan widens at the bottom so the tassel reads as ceremonial silk rather
    than three parallel sticks at the small scales of mid-screen tiles."""
    pygame.draw.circle(surf, (*body_col, alpha), (x_top, y_top), 3)
    top_xs = (-3, 0, 3)
    bot_xs = (-4, 0, 4)
    for tx, bx in zip(top_xs, bot_xs):
        pygame.draw.line(surf, (*body_col, max(80, alpha - 50)),
                         (x_top + tx, y_top + 3),
                         (x_top + bx, y_top + length), 2)
    pygame.draw.line(surf, (*accent_col, alpha),
                     (x_top, y_top + length),
                     (x_top, y_top + length + 3), 2)


def _ribbon_stem(surf, x, y_top, y_bot, color, alpha):
    """2-px vertical stem connecting a floating lobe to the ribbon below.
    2 px (vs the prior 1 px) survives down-rez to DAY column scale without
    dropping pixels into the ribbon's own keyline."""
    pygame.draw.line(surf, (*color, alpha), (x, y_top), (x, y_bot), 2)


def _baseline_skeleton(surf, x, y, palette, scale,
                       lobe_xs=(0.30, 0.50, 0.70),
                       lobe_lift=0,
                       lift_stems=False,
                       lobe_bottom_alpha_mul=1.0,
                       mid_lobe_scale=1.1,
                       w=72, h=58):
    """Paints the round-23 baseline silhouette and returns lobe coords so
    decorating variants can place pearls / tassels / inner echoes on
    consistent anchor points. Halo padding scales with frame so it never
    detaches into a separate ring when w shrinks; halo also stays gated
    at night so it doesn't muddy the lit lobes against a dark sky."""
    w = int(w * scale)
    h = int(h * scale)
    night = _is_night(palette)
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    cx_left = x - w // 2
    cy_top = y - h // 2

    if not night:
        hp_x = max(6, int(w * 0.18))
        hp_y = max(4, int(h * 0.20))
        halo = _alpha_surf(w + hp_x * 2, h + hp_y * 2)
        pygame.draw.ellipse(halo, (*edge, 38),
                            pygame.Rect(0, hp_y // 2,
                                        w + hp_x * 2 - 2,
                                        h + hp_y))
        surf.blit(halo, (cx_left - hp_x, cy_top - hp_y))

    ribbon_h = max(4, int(h * 0.18))
    ribbon_y = cy_top + h - ribbon_h
    pygame.draw.ellipse(surf, (*body, 230),
                        pygame.Rect(cx_left + 4, ribbon_y, w - 8, ribbon_h))
    pygame.draw.arc(surf, edge,
                    pygame.Rect(cx_left + 4, ribbon_y, w - 8, ribbon_h),
                    math.radians(200), math.radians(340), 1)

    lobe_centers = []
    lobe_r = max(8, int(min(w, h) * 0.32))
    for i, xfrac in enumerate(lobe_xs):
        lcx = cx_left + int(w * xfrac)
        lcy = ribbon_y - lobe_lift - lobe_r // 2
        r = int(lobe_r * (mid_lobe_scale if i == 1 else 1.0))
        # Soften the lower-rim alpha on lifted lobes so the lobe shadow
        # that now sits on sky (not on the ribbon) doesn't look pasted.
        key_a = int(180 * lobe_bottom_alpha_mul) if lobe_lift > 0 else 180
        _ruyi_lobe(surf, lcx, lcy, r, body, edge, lit,
                   body_a=248, key_a=key_a, lit_arc=(i == 1))
        if lift_stems and lobe_lift > 0:
            _ribbon_stem(surf, lcx, lcy + r // 2 + 1,
                         ribbon_y - 1, edge, 160)
        lobe_centers.append((lcx, lcy, r))
    return lobe_centers, (body, edge, lit, night)


# ══════════════════════════════════════════════════════════════════════
# 5 base-faithful variants — one surgical edit each
# ══════════════════════════════════════════════════════════════════════

# https://en.wikipedia.org/wiki/Ruyi_(scepter)
def draw_ruyi_compressed(surf, x, y, palette, scale=1.0):
    """Compressed Triplet: same DNA at lower aspect ratio — lobes pulled
    toward centre, mid lobe brought closer to the helpers in radius so the
    cluster reads as three nested pearls of cloud rather than a big lobe
    with two satellites."""
    _baseline_skeleton(surf, x, y, palette, scale,
                       lobe_xs=(0.38, 0.50, 0.62),
                       mid_lobe_scale=1.05,
                       w=54, h=48)


# https://www.metmuseum.org/art/collection/search/61945
def draw_ruyi_pearled(surf, x, y, palette, scale=1.0):
    """Pearled Crown: baseline + 5 porcelain pearl beads along the top
    edges of the 3 lobes (Tang/Ming pearl-rim motif). Beads carry a 1-px
    edge contour so they stay visible when they land on a lit crescent,
    which would otherwise wash them out at small (DAY-column) tiles."""
    centers, (body, edge, lit, night) = _baseline_skeleton(
        surf, x, y, palette, scale)
    pearl_r = max(2, int(round(3 * scale)))
    pearl_col = lit if not night else _lerp_color(lit, body, 0.4)
    pearl_a = 220 if not night else 180
    pattern = ((2, -0.6), (1, -0.9), (2, -0.6))
    for (lcx, lcy, r), (n, yoff) in zip(centers, pattern):
        py = lcy + int(r * yoff)
        if n == 1:
            _pearl_dot(surf, lcx, py, pearl_r, pearl_col, edge, pearl_a)
        else:
            spread = max(int(r * 0.75), pearl_r * 4)
            for k in range(n):
                px = lcx - spread // 2 + k * spread
                _pearl_dot(surf, px, py, pearl_r, pearl_col, edge, pearl_a)


# https://en.wikipedia.org/wiki/Chinese_paper_cutting
def draw_ruyi_lifted(surf, x, y, palette, scale=1.0):
    """Lifted Petals: 3 lobes float ~6 px above the ribbon, joined by
    2-px vertical stems. Stems stay on so the petal-on-stem-frame
    silhouette is unmistakable — without them the variant would collapse
    back into the baseline at thumbnail scale."""
    base_lift = int(round(6 * scale))
    lift = max(4, base_lift) if scale < 0.6 else base_lift
    _baseline_skeleton(surf, x, y, palette, scale,
                       lobe_lift=lift, lift_stems=True,
                       lobe_bottom_alpha_mul=0.7)


# https://www.dunhuang.ds.lib.uw.edu/mogao-cave-321-early-tang-dynasty/
def draw_ruyi_double_arc(surf, x, y, palette, scale=1.0):
    """Double-Arc Keyline: baseline + a second concentric arc keyline on
    the dominant middle lobe, sitting 3–4 px inside the primary one. Same
    Tang Buddhist caisson / Mogao concentric-ring inspiration as the
    prior Inner Echo, but rendered as a deliberate second highlight
    contour that still reads at 1× DAY-column scale."""
    centers, (body, edge, lit, night) = _baseline_skeleton(
        surf, x, y, palette, scale)
    mlcx, mlcy, mr = centers[1]
    inset = max(2, int(round(4 * scale)))
    inner_r = max(3, mr - inset)
    contour = _lerp_color(lit, body, 0.3)
    rect = pygame.Rect(mlcx - inner_r, mlcy - inner_r,
                       inner_r * 2, inner_r * 2)
    # Mirror the baseline's (200°, 340°) lower-left calligraphic keyline
    # so the doubled arc reads as a deliberate echo of the primary one,
    # not a foreign curve.
    pygame.draw.arc(surf, (*contour, 210), rect,
                    math.radians(200), math.radians(340), 2)


# https://en.wikipedia.org/wiki/Dancheong
def draw_ruyi_tassel(surf, x, y, palette, scale=1.0):
    """Tassel Court Banner: baseline + 2 cinnabar silk tassels anchored
    under the outer lobe centres. Forced cinnabar accent keeps the silk
    unmistakably red even at SUNSET (where horizon itself is cinnabar and
    a raw horizon-tinted accent would otherwise dissolve into the sky)."""
    centers, (body, edge, lit, night) = _baseline_skeleton(
        surf, x, y, palette, scale)
    lcx0 = centers[0][0]
    lcx2 = centers[2][0]
    ribbon_y = centers[1][1] + centers[1][2] // 2 + 1
    tassel_len = max(7, int(round(11 * scale)))
    # Bias hard toward cinnabar so the tassel survives every phase; the
    # horizon channel only seeds enough hue to keep the strand sitting in
    # the same warm family as the surrounding biome.
    accent = _lerp_color(palette['horizon'], (200, 60, 40), 0.6)
    tassel_body = _lerp_color(accent, _ink_shadow_color(palette), 0.4)
    alpha = 200 if not night else 150
    for tx in (lcx0, lcx2):
        _tassel_fringe(surf, tx, ribbon_y, tassel_len,
                       tassel_body, accent, alpha)


# ── Registry ──────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_ruyi_compressed,
    2: draw_ruyi_pearled,
    3: draw_ruyi_lifted,
    4: draw_ruyi_double_arc,
    5: draw_ruyi_tassel,
}

VARIANT_NAMES = {
    1: "Compressed Triplet",
    2: "Pearled Crown",
    3: "Lifted Petals",
    4: "Double-Arc Keyline",
    5: "Tassel Court Banner",
}

VARIANT_SOURCES = {
    1: "https://en.wikipedia.org/wiki/Ruyi_(scepter)",
    2: "https://www.metmuseum.org/art/collection/search/61945",
    3: "https://en.wikipedia.org/wiki/Chinese_paper_cutting",
    4: "https://www.dunhuang.ds.lib.uw.edu/mogao-cave-321-early-tang-dynasty/",
    5: "https://en.wikipedia.org/wiki/Dancheong",
}
