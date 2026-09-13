"""5 base-faithful Ruyi cloud variants with softened interior linework.

Each variant inherits the round-23 V2 silhouette DNA — 3 asymmetric
lobes on a leading-side ribbon, drop-shadow halo, sunlit crescent on
the dominant middle lobe — but tames the inner ink strokes (the
lobe-divider arcs, inner-swoop curls, and ribbon keyline lines) that
prior critique flagged as too aggressive against a daylight sky.

The OUTER silhouette and main outline arc on each lobe stay at full
weight; only the INNER detail softens, so the family read at thumbnail
is preserved.

Drop-in contract identical to `cloud_variants.draw_cloud_*`:
    `draw_cloud_<name>(surf, x, y, palette, scale=1.0)`
"""
from __future__ import annotations

import math

import pygame

from cloud_variants import (
    _cloud_body_color,
    _ink_shadow_color,
    _lit_edge_color,
)
from ruyi_variants import (
    _alpha_surf,
    _is_night,
    _lerp,
    _lerp_color,
    _seeded_jit,
)


# ── Inner-line softening recipes ─────────────────────────────────────────────
#
# The base Ruyi's interior-line layer is what the user called "too
# aggressive": three calligraphic strokes per lobe (outer arc + inner
# swoop + ribbon keyline). Each soft-variant picks ONE recipe from this
# row to thin / fade / dash / decimate / tint-shift that interior ink
# while leaving the outer silhouette discs and ribbon body untouched.

_INK_SOFT_THIN = "thin"        # full alpha, stroke width 2 → 1 px
_INK_SOFT_FADE = "fade"        # width 2, alpha 160 → 70
_INK_SOFT_DASH = "dash"        # break long arcs into short dry-brush dabs
_INK_SOFT_SKIP = "skip"        # drop the inner-swoop curl entirely
_INK_SOFT_TINT = "tint"        # pull ink colour 50% toward body fill


def _ink_color(edge, body, recipe: str):
    # Tint recipe pulls the ink shadow deep toward the body fill so the
    # inner detail bleeds into the cloud mass like wet ink on damp paper
    # rather than slicing across it. Other recipes preserve canonical
    # shadow hue.
    if recipe == _INK_SOFT_TINT:
        return _lerp_color(edge, body, 0.65)
    return edge


def _ink_width(recipe: str) -> int:
    return 1 if recipe == _INK_SOFT_THIN else 2


def _ink_alpha(base_alpha: int, recipe: str) -> int:
    if recipe == _INK_SOFT_FADE:
        return max(40, int(base_alpha * 0.45))
    if recipe == _INK_SOFT_DASH:
        return max(80, int(base_alpha * 0.7))
    return base_alpha


def _dashed_arc(surf, color_rgba, rect, ang_a, ang_b, n_dash=5):
    # Replace one continuous arc with short dry-brush segments along the
    # same sweep. Even segments are painted, odd ones skipped, so the
    # eye still reads the curve without the ruler-edge of a solid stroke.
    span = ang_b - ang_a
    seg = span / (n_dash * 2 - 1)
    for k in range(n_dash):
        a0 = ang_a + (k * 2) * seg
        a1 = a0 + seg
        pygame.draw.arc(surf, color_rgba, rect, a0, a1, 2)


# ── Shared base painter ─────────────────────────────────────────────────────
#
# Faithful reproduction of `cloud_variants.draw_cloud_ruyi` structure so
# every soft variant starts from the same DNA: 3-lobe asymmetric layout
# at 0.25 / 0.55 / 0.82, ribbon polygon, drop-shadow halo, sunlit
# crescent on the dominant middle lobe. The variant-specific hooks
# control aspect (w_base / h_base), the lobe x-fractions, lobe radius
# scaling, body/edge palette overrides, inner-line recipe, ribbon
# variation, and any per-lobe ornamentation.


def _draw_base_ruyi(
    surf, x, y, palette, scale,
    *,
    w_base=72, h_base=46,
    lobe_xs=(0.25, 0.55, 0.82),
    lobe_y_offsets=(-0.05, -0.18, -0.08),
    lobe_r_fracs=(0.36, 0.42, 0.38),
    body_override=None,
    edge_override=None,
    lit_override=None,
    ink_recipe=_INK_SOFT_FADE,
    skip_inner_swoop=False,
    ribbon_style="oval",
    on_lobe=None,
):
    """Paint a softened Ruyi using the round-23 base structure.

    body/edge/lit overrides let palette-branch variants substitute their
    own colour recipes without re-implementing the silhouette. on_lobe
    is invoked after each lobe is drawn so ornamentation variants can
    drop heart sub-lobes, dot tips, etc. without owning the loop.
    """
    body = body_override if body_override is not None else _cloud_body_color(palette)
    edge = edge_override if edge_override is not None else _ink_shadow_color(palette)
    lit = lit_override if lit_override is not None else _lit_edge_color(palette)

    w = int(w_base * scale)
    h = int(h_base * scale)
    pad = 8
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    base_lobes = tuple(
        (
            int(w * xf),
            cy + int(h * yo) + _seeded_jit(x, y, i, max(2, int(h * 0.06))),
            int(h * rf),
        )
        for i, (xf, yo, rf) in enumerate(zip(lobe_xs, lobe_y_offsets, lobe_r_fracs))
    )

    # Drop-shadow halo under the lobes — kept at the base alpha (45) so
    # the outer silhouette presence matches the round-23 reference.
    for (lx, ly, lr) in base_lobes:
        pygame.draw.circle(s, (*edge, 45), (lx + pad + 1, ly + 2), lr + 1)

    # Ribbon — outer silhouette stays solid. Variant control here is in
    # the SHAPE family (oval vs scalloped wave), not in linework alpha.
    if ribbon_style == "wave":
        # Multi-scalloped cresting ribbon — four peaks along the top
        # edge, deeper than the flat oval. The wave form IS the variant's
        # distinctness, so peak amplitude must survive the smallest
        # render scale: floor each crest's vertical offset to at least
        # 3 px from centerline so the 4-peak count remains readable at
        # 0.7× rather than degenerating into a wobbly oval.
        base_pts = []
        peak_xs = (0.18, 0.42, 0.68, 0.86)
        peak_up = -max(3, int(h * 0.10))
        peak_dn = max(2, int(h * 0.04))
        for k, pf in enumerate(peak_xs):
            base_pts.append((pad + int(w * pf),
                             cy + (peak_dn if k % 2 == 0 else peak_up)))
        # Wider trailing trough below — floored so the body keeps depth
        # under the crests even at small scale.
        trough_lo = max(4, int(h * 0.14))
        trough_mid = max(6, int(h * 0.20))
        trough_lo2 = max(5, int(h * 0.19))
        trough_hi = max(4, int(h * 0.13))
        base_pts.extend([
            (pad + int(w * 0.78), cy + trough_lo),
            (pad + int(w * 0.55), cy + trough_mid),
            (pad + int(w * 0.30), cy + trough_lo2),
            (pad + int(w * 0.12), cy + trough_hi),
        ])
        pygame.draw.polygon(s, (*edge, 60),
                            [(px + 2, py + 3) for px, py in base_pts])
        pygame.draw.polygon(s, (*body, 240), base_pts)
        # Softened ribbon keyline — dashed dry-brush instead of solid.
        ink_col = _ink_color(edge, body, ink_recipe)
        ink_a = _ink_alpha(140, ink_recipe)
        # Trace the top scallop edge with short segments (every other
        # line drawn) so the curl reads as hand-painted, not ruled.
        for k in range(0, len(peak_xs) - 1, 2):
            pygame.draw.line(s, (*ink_col, ink_a),
                             base_pts[k], base_pts[k + 1],
                             _ink_width(ink_recipe))
    else:
        base_pts = [
            (pad + int(w * 0.10), cy + int(h * 0.05)),
            (pad + int(w * 0.30), cy + int(h * 0.12)),
            (pad + int(w * 0.55), cy + int(h * 0.13)),
            (pad + int(w * 0.78), cy + int(h * 0.09)),
            (pad + int(w * 0.90), cy + int(h * 0.04)),
            (pad + int(w * 0.78), cy + int(h * 0.14)),
            (pad + int(w * 0.55), cy + int(h * 0.18)),
            (pad + int(w * 0.30), cy + int(h * 0.17)),
            (pad + int(w * 0.12), cy + int(h * 0.12)),
        ]
        pygame.draw.polygon(s, (*edge, 60),
                            [(px + 2, py + 3) for px, py in base_pts])
        pygame.draw.polygon(s, (*body, 240), base_pts)
        # Softened ribbon keyline — same poly path the base draws but
        # at the variant's chosen recipe.
        ink_col = _ink_color(edge, body, ink_recipe)
        ribbon_a_top = _ink_alpha(170, ink_recipe)
        ribbon_a_bot = _ink_alpha(130, ink_recipe)
        if ink_recipe == _INK_SOFT_DASH:
            # Skip every other segment for the dashed read.
            for k in range(0, 4, 2):
                pygame.draw.line(s, (*ink_col, ribbon_a_top),
                                 base_pts[k], base_pts[k + 1],
                                 _ink_width(ink_recipe))
        else:
            pygame.draw.lines(s, (*ink_col, ribbon_a_top), False,
                              base_pts[:5], _ink_width(ink_recipe))
            pygame.draw.lines(s, (*ink_col, ribbon_a_bot), False,
                              base_pts[4:], _ink_width(ink_recipe))

    # Lobe body fills — outer silhouette, full alpha.
    for (lx, ly, lr) in base_lobes:
        pygame.draw.circle(s, (*body, 245), (lx + pad, ly), lr)

    # Interior lobe linework — the surgical softening layer. Each lobe
    # gets the outer arc keyline (still present so the family reads),
    # plus the inner swoop unless the variant skipped it; both rendered
    # via the recipe so width/alpha/colour pull together.
    ink_col = _ink_color(edge, body, ink_recipe)
    # Per-recipe interior alpha tuning: TINT pulls deeper toward body
    # AND drops arc opacity so the wet-ink bloom reads as bleed rather
    # than as a slightly tinted hard line. THIN drops the 1 px outer
    # alpha so "thin" actually reads "soft" at thumbnail rather than
    # just "narrow but still shouting."
    if ink_recipe == _INK_SOFT_TINT:
        outer_a = 120
        inner_a = 140
    elif ink_recipe == _INK_SOFT_THIN:
        outer_a = 110
        inner_a = 180
    else:
        outer_a = _ink_alpha(160, ink_recipe)
        inner_a = _ink_alpha(180, ink_recipe)
    ink_w = _ink_width(ink_recipe)
    for (lx, ly, lr) in base_lobes:
        cx_l = lx + pad
        outer_rect = pygame.Rect(cx_l - lr, ly - lr, lr * 2, lr * 2)
        if ink_recipe == _INK_SOFT_DASH:
            _dashed_arc(s, (*ink_col, outer_a), outer_rect,
                        math.radians(200), math.radians(340), n_dash=3)
        else:
            pygame.draw.arc(s, (*ink_col, outer_a), outer_rect,
                            math.radians(200), math.radians(340), ink_w)
        if not skip_inner_swoop:
            inner = max(3, lr - 5)
            inner_rect = pygame.Rect(cx_l - inner, ly - inner,
                                     inner * 2, inner * 2)
            if ink_recipe == _INK_SOFT_DASH:
                _dashed_arc(s, (*ink_col, inner_a), inner_rect,
                            math.radians(20), math.radians(200), n_dash=3)
            else:
                pygame.draw.arc(s, (*ink_col, inner_a), inner_rect,
                                math.radians(20), math.radians(200), ink_w)

    # Sunlit crescent on the dominant middle lobe — outer rim accent,
    # never softened so the directional sun-kiss survives.
    lx, ly, lr = base_lobes[1]
    cx_l = lx + pad
    pygame.draw.arc(s, (*lit, 200),
                    pygame.Rect(cx_l - lr + 2, ly - lr + 2,
                                lr * 2 - 4, lr * 2 - 4),
                    math.radians(110), math.radians(220), 2)

    if on_lobe is not None:
        for i, (lx, ly, lr) in enumerate(base_lobes):
            on_lobe(s, i, lx + pad, ly, lr, body, ink_col, lit)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ═════════════════════════════════════════════════════════════════════════════
# Variant 1 — Wet-Ink Bloom Wash
# Research:
#   https://en.wikipedia.org/wiki/Ink_wash_painting
#   https://www.asianbrushpainter.com/blogs/kb/brush-techniques-2
#
# Interior arcs pulled 50% toward body fill (the TINT recipe) so the
# ink reads as wet paint sinking INTO the cloud rather than ruled atop
# it. Aspect held to baseline; ribbon untouched. The softening is the
# whole variant — purest "less aggressive linework" answer.
# ═════════════════════════════════════════════════════════════════════════════

def draw_cloud_bloom(surf, x, y, palette, scale=1.0):
    """Ruyi with wet-on-wet bleed — inner ink mixed half toward body."""
    _draw_base_ruyi(surf, x, y, palette, scale,
                    ink_recipe=_INK_SOFT_TINT)


# ═════════════════════════════════════════════════════════════════════════════
# Variant 2 — Cinnabar-Tipped Tan
# Research:
#   https://oricultural.com/blogs/blogs/the-color-palette-of-chinese-dynasties-a-historical-journey-through-imperial-hues
#   https://www.pagodared.com/blog/2024/10/11/as-you-wish-the-ruyi-symbol-in-chinese-japanse-decorative-arts/
#
# Palette-branch variant: body warmed toward Tang court tan/buff, the
# inner-line ink shifted to cinnabar so the softened curls read as
# painted vermilion on porcelain instead of a darker shadow. The
# alpha-fade recipe is what tones the cinnabar down to a whisper.
# ═════════════════════════════════════════════════════════════════════════════

def draw_cloud_cinnabar(surf, x, y, palette, scale=1.0):
    """Tang court porcelain palette — buff body, faded cinnabar curls."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)
    horizon = palette['horizon']

    # Buff body — pull the standard cloud body toward warm tan so the
    # Tang sancai porcelain mood lands without abandoning palette-driven
    # sky coupling. Night gates the buff way down: a warm-tan body
    # against deep cool-blue night sky reads as a colour clash, so under
    # night the body stays mostly cool with only a whisper of warmth to
    # keep family identity.
    tan_warm = (230, 200, 150)
    buff_amt = 0.15 if night else 0.30
    body_buff = _lerp_color(body, tan_warm, buff_amt)

    # Cinnabar ink — vermilion sliding to red oxide, only painted at
    # day/golden where vermilion belongs to the warm light. At night
    # the cinnabar would shout against deep blue, so the cinnabar lerps
    # toward the standard edge tone to keep palette honesty.
    cinnabar = (190, 70, 50)
    if night:
        ink_warm = _lerp_color(edge, cinnabar, 0.25)
    else:
        ink_warm = _lerp_color(edge, cinnabar, 0.60)
    # Compose with horizon so sunset's cinnabar sky doesn't double-cook
    # the inner-line tint into pure red.
    ink_warm = _lerp_color(ink_warm, horizon, 0.15)

    _draw_base_ruyi(surf, x, y, palette, scale,
                    body_override=body_buff,
                    edge_override=ink_warm,
                    lit_override=lit,
                    ink_recipe=_INK_SOFT_FADE)


# ═════════════════════════════════════════════════════════════════════════════
# Variant 3 — Wide-Spread Coronet
# Research:
#   https://en.wikipedia.org/wiki/Yunjian
#   https://en.wikipedia.org/wiki/Xiangyun_(Auspicious_clouds)
#
# Silhouette-proportion variant: pull the lobes apart along an 88 × 38
# coronet aspect (wider, shallower than the 72 × 46 base) and skip the
# inner-swoop curl on every lobe — so each lobe carries one calligraphic
# arc instead of two. Reads as a low yunjian collar in cloud form
# rather than a tight stacked stamp.
# ═════════════════════════════════════════════════════════════════════════════

def draw_cloud_coronet(surf, x, y, palette, scale=1.0):
    """Wide-spread yunjian coronet — lobes apart, one arc per lobe."""
    _draw_base_ruyi(surf, x, y, palette, scale,
                    w_base=88, h_base=38,
                    lobe_xs=(0.18, 0.50, 0.82),
                    lobe_y_offsets=(-0.04, -0.20, -0.06),
                    lobe_r_fracs=(0.40, 0.46, 0.42),
                    ink_recipe=_INK_SOFT_THIN,
                    skip_inner_swoop=True)


# ═════════════════════════════════════════════════════════════════════════════
# Variant 4 — Cresting Wave-Ribbon
# Research:
#   https://www.suembroidery.com/chinese-silk-embroidery-blog/chinese-silk-embroidery-patterns-and-symbolisms
#   https://en.wikipedia.org/wiki/Xiangyun_(Auspicious_clouds)
#
# Ribbon-form variant: replace the flat-oval base ribbon with a
# multi-peaked cresting silhouette (lishui wave-stripe lineage from
# Ming/Qing imperial robes), and break the ribbon's keyline + lobe arcs
# into dry-brush dashes so the wave reads as painted silk rather than
# stamped foil.
# ═════════════════════════════════════════════════════════════════════════════

def draw_cloud_cresting(surf, x, y, palette, scale=1.0):
    """Multi-peaked lishui-wave ribbon — interior dashed dry-brush."""
    _draw_base_ruyi(surf, x, y, palette, scale,
                    w_base=76, h_base=50,
                    lobe_xs=(0.22, 0.52, 0.80),
                    lobe_y_offsets=(-0.10, -0.22, -0.12),
                    lobe_r_fracs=(0.34, 0.40, 0.36),
                    ink_recipe=_INK_SOFT_DASH,
                    ribbon_style="wave")


# ═════════════════════════════════════════════════════════════════════════════
# Variant 5 — Lingzhi Twin-Tip Crown
# Research:
#   https://en.wikipedia.org/wiki/Ruyi_(scepter)
#   https://www.pagodared.com/blog/2024/10/11/as-you-wish-the-ruyi-symbol-in-chinese-japanse-decorative-arts/
#
# Lobe-ornamentation variant: each lobe acquires a small twin-tip
# notch on its upper rim — the lingzhi mushroom's bilobed cap that the
# Ruyi sceptre's head historically references. The notches are body-
# coloured outer silhouette so they read on the cloud's edge; interior
# arcs are dropped to half-alpha so the new top detail leads the eye
# instead of competing.
# ═════════════════════════════════════════════════════════════════════════════

def _lingzhi_tips(s, idx, lcx, lcy, lr, body, ink_col, lit):
    # Twin small body-coloured discs straddling the top of each lobe —
    # silhouette-positive notches that read as the lingzhi mushroom's
    # bilobed cap carved INTO the lobe rim, not as separate bumps stuck
    # on top. Pulled inward and sunk ~50% into the lobe so the gap
    # between them reads as a notch rather than a pair of warts.
    tip_r = max(2, int(lr * 0.32))
    sep = max(2, int(lr * 0.25))
    top_y = lcy - lr + tip_r
    for dx in (-sep, sep):
        pygame.draw.circle(s, (*body, 245), (lcx + dx, top_y), tip_r)
        # One thin keyline arc along the tip's outer flank so the bump
        # reads as part of the lobe rather than a stuck-on bead.
        pygame.draw.arc(
            s, (*ink_col, 110),
            pygame.Rect(lcx + dx - tip_r, top_y - tip_r,
                        tip_r * 2, tip_r * 2),
            math.radians(180 if dx < 0 else 0),
            math.radians(360 if dx < 0 else 180),
            1,
        )


def draw_cloud_lingzhi(surf, x, y, palette, scale=1.0):
    """Lingzhi-tipped Ruyi — twin notches on each lobe's upper rim."""
    _draw_base_ruyi(surf, x, y, palette, scale,
                    ink_recipe=_INK_SOFT_FADE,
                    on_lobe=_lingzhi_tips)


# ── Registries ──────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_cloud_bloom,
    2: draw_cloud_cinnabar,
    3: draw_cloud_coronet,
    4: draw_cloud_cresting,
    5: draw_cloud_lingzhi,
}

VARIANT_NAMES = {
    1: "Wet-Ink Bloom Wash",
    2: "Cinnabar-Tipped Tan",
    3: "Wide-Spread Coronet",
    4: "Cresting Wave-Ribbon",
    5: "Lingzhi Twin-Tip Crown",
}

VARIANT_SOURCES = {
    1: "https://en.wikipedia.org/wiki/Ink_wash_painting",
    2: "https://oricultural.com/blogs/blogs/the-color-palette-of-chinese-dynasties-a-historical-journey-through-imperial-hues",
    3: "https://en.wikipedia.org/wiki/Yunjian",
    4: "https://www.suembroidery.com/chinese-silk-embroidery-blog/chinese-silk-embroidery-patterns-and-symbolisms",
    5: "https://www.pagodared.com/blog/2024/10/11/as-you-wish-the-ruyi-symbol-in-chinese-japanse-decorative-arts/",
}
