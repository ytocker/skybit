"""Palette-aware shan-shui cloud variants for the live game.

Six procedural cloud silhouettes that re-tint across the biome day/night cycle
via the imported palette (no hard-coded white). Consolidated single module so the
live game has one import surface; `draw.py:draw_cloud` dispatches into `_VARIANTS`.

Source of truth for the original explorations + the user-picked winners lives in
`archive/cloud_redesign/` and `docs/cloud_redesign/winners_sheet.png`.
"""
from __future__ import annotations

import math
import pygame


# ── palette helpers ──────────────────────────────────────────────────────────

def _cloud_body_color(palette: dict) -> tuple[int, int, int]:
    horizon = palette['horizon']
    sky_bot = palette['sky_bot']
    sky_top = palette['sky_top']
    # A warm horizon-led mix (0.70 horizon / 0.30 sky_bot) by day ties clouds to
    # the dawn/dusk rim light; a cooler sky_top-led mix (0.50 / 0.50) after dark
    # keeps night cumulus pale-COOL instead of warm. Crossfade the two by sky_top
    # luminance with a smoothstep over a band around lum 90, so the body fades
    # between recipes across the cycle instead of SNAPPING at one phase.
    top_lum = (sky_top[0] * 299 + sky_top[1] * 587 + sky_top[2] * 114) / 1000
    f = (105.0 - top_lum) / 30.0          # 0 = bright day, 1 = dark night
    f = 0.0 if f < 0.0 else (1.0 if f > 1.0 else f)
    f = f * f * (3.0 - 2.0 * f)           # smoothstep
    out = []
    for hc, bc, tc in zip(horizon, sky_bot, sky_top):
        warm = hc * 0.70 + bc * 0.30
        cool = hc * 0.50 + tc * 0.50
        out.append(min(255, int(warm + (cool - warm) * f) + 25))
    return tuple(out)

def _ink_shadow_color(palette: dict) -> tuple[int, int, int]:
    # The "wet ink" edge of a calligraphic wash — pulled from the sky (deep
    # sky_top toward sky_mid) so it tracks the active sky design rather than the
    # separately-themed mountains, and stays valid on a sky-only palette.
    top = palette['sky_top']
    mid = palette.get('sky_mid', top)
    return (
        max(0, int(top[0] * 0.55 + mid[0] * 0.45) - 10),
        max(0, int(top[1] * 0.55 + mid[1] * 0.45) - 10),
        max(0, int(top[2] * 0.55 + mid[2] * 0.45) - 10),
    )

def _lit_edge_color(palette: dict) -> tuple[int, int, int]:
    # The single bright sliver on the cloud's sunlit side — picked from
    # horizon and pushed brighter so it pops even in dusk/night phases.
    h = palette['horizon']
    return (
        min(255, h[0] + 30),
        min(255, h[1] + 30),
        min(255, h[2] + 30),
    )

def _lerp(a, b, t):
    return a + (b - a) * t

def _lerp_color(a, b, t):
    return (
        int(_lerp(a[0], b[0], t)),
        int(_lerp(a[1], b[1], t)),
        int(_lerp(a[2], b[2], t)),
    )

def _alpha_surf(w, h) -> pygame.Surface:
    return pygame.Surface((max(2, int(w)), max(2, int(h))), pygame.SRCALPHA)

# ── ruyi-lobe / ink helpers ──────────────────────────────────────────────────

def _cozy_lobe_sway(x: float, idx: int, amp: float) -> int:
    # Gentle continuous lobe drift keyed to the cloud's scroll position rather
    # than a per-frame hash of it: the silhouette breathes smoothly instead of
    # flickering. Long spatial period + small amplitude keep it cozy at every
    # parallax depth. (A hashed jitter re-rolled every frame as x/y changed,
    # which read as an unpleasant flicker.)
    return int(math.sin(x * 0.06 + idx * 2.1) * amp)

def _is_night(palette: dict) -> bool:
    # Single luminance test used to gate night-only branches like the
    # ghost-white halos on the Sovereign and Sumi-e variants. Threshold
    # matches `_cloud_body_color`'s 90 split point so the cloud cools
    # in sync with its night-branch body.
    top = palette['sky_top']
    return (top[0] * 299 + top[1] * 587 + top[2] * 114) / 1000 < 90

def _ruyi_lobe(s: pygame.Surface, cx: int, cy: int, r: int,
               body, edge, lit,
               body_a: int = 245, key_a: int = 160,
               lit_arc: bool = False) -> None:
    # One canonical ruyi lobe: filled circle + lower-left calligraphic
    # arc keyline (200°–340°) + inner-curl arc (20°–200°). Pulled out
    # of the round-23 inline code so all 8 variants paint the same lobe
    # vocabulary, only varying count / spacing / palette.
    pygame.draw.circle(s, (*body, body_a), (cx, cy), r)
    pygame.draw.arc(
        s, (*edge, key_a),
        pygame.Rect(cx - r, cy - r, r * 2, r * 2),
        math.radians(200), math.radians(340), 2)
    inner = max(3, r - 5)
    pygame.draw.arc(
        s, (*edge, min(255, key_a + 20)),
        pygame.Rect(cx - inner, cy - inner, inner * 2, inner * 2),
        math.radians(20), math.radians(200), 2)
    if lit_arc and r >= 6:
        pygame.draw.arc(
            s, (*lit, 200),
            pygame.Rect(cx - r + 2, cy - r + 2,
                        max(2, r * 2 - 4), max(2, r * 2 - 4)),
            math.radians(110), math.radians(220), 2)

def _ruyi_heart(s: pygame.Surface, cx: int, cy: int, r: int,
                body, edge, lit,
                body_a: int = 245, key_a: int = 170,
                lit_arc: bool = False) -> None:
    # Two mirrored half-lobes joined at the base — this is the silhouette
    # signature that says "Ruyi" rather than "circle". Cluster of: left
    # lobe + right lobe centred horizontally on cx, vertically tucked so
    # their bottoms meet just under cy, with a downward V-notch between
    # them. The notch is what reads as a heart, not a peanut, at thumb-
    # nail. Used wherever the AD called for "double-lobed heart DNA".
    off = max(2, int(r * 0.55))
    lr = max(3, int(r * 0.78))
    lcx_l = cx - off
    lcx_r = cx + off
    lcy = cy - max(1, int(r * 0.10))
    # Drop-shadow first (under both halves) so it doesn't double-bake
    # in the join seam.
    pygame.draw.circle(s, (*edge, 30), (cx + 1, cy + 3), r)
    # Twin half-lobes — drawn as full discs then welded by a small
    # bridging ellipse at the base so the silhouette reads as one
    # continuous heart rather than two stamped balls.
    pygame.draw.circle(s, (*body, body_a), (lcx_l, lcy), lr)
    pygame.draw.circle(s, (*body, body_a), (lcx_r, lcy), lr)
    bridge_w = off * 2 + 2
    bridge_h = max(3, int(r * 0.55))
    pygame.draw.ellipse(
        s, (*body, body_a),
        pygame.Rect(cx - bridge_w // 2, lcy, bridge_w, bridge_h))
    # V-notch on top centre — small triangle in transparent so the heart
    # cleavage is visible. Achieved by repainting the body's interior
    # gap with the surface's clear-pixel through BLEND_RGBA_MULT mask
    # would be heavier; here a single 1-px tip indent is enough at the
    # scales we render.
    notch_top = (cx, lcy - lr + 2)
    notch_l = (cx - max(1, lr // 4), lcy - lr // 2)
    notch_r = (cx + max(1, lr // 4), lcy - lr // 2)
    pygame.draw.polygon(s, (0, 0, 0, 0), [notch_top, notch_l, notch_r])
    # Calligraphic keyline arcs hugging each half-lobe's outer flank —
    # mirrored so the heart has two flanking curls, the classic Ruyi
    # double-spiral signature.
    pygame.draw.arc(
        s, (*edge, key_a),
        pygame.Rect(lcx_l - lr, lcy - lr, lr * 2, lr * 2),
        math.radians(200), math.radians(350), 2)
    pygame.draw.arc(
        s, (*edge, key_a),
        pygame.Rect(lcx_r - lr, lcy - lr, lr * 2, lr * 2),
        math.radians(190), math.radians(340), 2)
    inner = max(2, lr - 4)
    pygame.draw.arc(
        s, (*edge, min(255, key_a + 20)),
        pygame.Rect(lcx_l - inner, lcy - inner, inner * 2, inner * 2),
        math.radians(40), math.radians(200), 2)
    pygame.draw.arc(
        s, (*edge, min(255, key_a + 20)),
        pygame.Rect(lcx_r - inner, lcy - inner, inner * 2, inner * 2),
        math.radians(340), math.radians(140), 2)
    if lit_arc and lr >= 5:
        pygame.draw.arc(
            s, (*lit, 200),
            pygame.Rect(lcx_l - lr + 2, lcy - lr + 2,
                        max(2, lr * 2 - 4), max(2, lr * 2 - 4)),
            math.radians(120), math.radians(220), 2)
        pygame.draw.arc(
            s, (*lit, 200),
            pygame.Rect(lcx_r - lr + 2, lcy - lr + 2,
                        max(2, lr * 2 - 4), max(2, lr * 2 - 4)),
            math.radians(110), math.radians(210), 2)

def _mix(a, b, t: float):
    # Local palette blend used by the celadon + eclipse variants below
    # so their colour-mix expressions match the AD's verbatim spec.
    return (
        int(a[0] * (1 - t) + b[0] * t),
        int(a[1] * (1 - t) + b[1] * t),
        int(a[2] * (1 - t) + b[2] * t),
    )

# ── softened-linework ink recipes (cinnabar base) ────────────────────────────

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
            cy + int(h * yo) + _cozy_lobe_sway(x, i, h * 0.035),
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

# ── the six winners (slots 0..5) ─────────────────────────────────────────────

def draw_cloud_ruyi(surf, x, y, palette, scale=1.0):
    """Tang/Ming auspicious-cloud scroll — 3 lobes + inner-arc swoops."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    # Dropped from 96 px / 4 lobes to 72 px / 3 lobes: the prior fan of
    # 4 lobes on a strict diagonal read as a vector decal / heraldic
    # crest, which competed with the KFC pillar logo. 3-lobe Tang
    # arrangement with broken alignment lands as a sky motif.
    w = int(72 * scale)
    h = int(46 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # 3-lobe layout — the base y offsets already break the strict diagonal
    # (dominant lobe on the leading right side). The small per-lobe vertical
    # variation uses the smooth scroll-keyed sway (_cozy_lobe_sway), NOT a hash
    # of the live x: the old hash re-rolled every frame as the cloud drifted, so
    # the lobes jumped and the silhouette flickered. The sway breathes gently
    # with a long spatial period — almost no motion, and no flicker.
    base_lobes = (
        (int(w * 0.25), cy - int(h * 0.05), int(h * 0.36)),
        (int(w * 0.55), cy - int(h * 0.18), int(h * 0.42)),
        (int(w * 0.82), cy - int(h * 0.08), int(h * 0.38)),
    )
    lobes = tuple(
        (lx, ly + _cozy_lobe_sway(x, i, h * 0.045), lr)
        for i, (lx, ly, lr) in enumerate(base_lobes)
    )

    # 1. Soft ink-shadow halo offset down-right. Alpha pulled 70 → 45
    # and offset +2,+3 → +1,+2 so the halo reads as drop-shadow whisper
    # instead of bordering the lobes like a stencil.
    for (lx, ly, lr) in lobes:
        pygame.draw.circle(
            s, (*edge, 45), (lx + pad + 1, ly + 2), lr + 1)
    # Base ribbon — halved vertical extent (was h*0.28, now ~h*0.18) so
    # the ribbon supports the lobes rather than overwhelming them.
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

    # 2. Lobe fills.
    for (lx, ly, lr) in lobes:
        pygame.draw.circle(s, (*body, 245), (lx + pad, ly), lr)

    # 3. Arc-segment keylines instead of full circumference rings — the
    # full ring read as a logo/badge; a 200°–340° arc on the lower-left
    # quadrant only reads as a calligraphic ruyi curl on each lobe.
    for (lx, ly, lr) in lobes:
        cx_l = lx + pad
        pygame.draw.arc(
            s, (*edge, 160),
            pygame.Rect(cx_l - lr, ly - lr, lr * 2, lr * 2),
            math.radians(200), math.radians(340), 2)
        # Inner swoop — the actual ruyi flourish. No centre pinpoint:
        # at 1× the dot read as a pixel defect.
        inner = max(3, lr - 5)
        rect = pygame.Rect(cx_l - inner, ly - inner, inner * 2, inner * 2)
        pygame.draw.arc(s, (*edge, 180), rect,
                        math.radians(20), math.radians(200), 2)

    # 4. Base-ribbon keyline.
    pygame.draw.lines(s, (*edge, 170), False, base_pts[:5], 2)
    pygame.draw.lines(s, (*edge, 130), False, base_pts[4:], 1)

    # 5. Sunlit crescent — restricted to the dominant (middle) lobe only.
    # Three crescents lit the silhouette like a vector decal; one
    # crescent on the apex lobe reads as a single directional sun-kiss.
    lx, ly, lr = lobes[1]
    cx_l = lx + pad
    pygame.draw.arc(s, (*lit, 200),
                    pygame.Rect(cx_l - lr + 2, ly - lr + 2,
                                lr * 2 - 4, lr * 2 - 4),
                    math.radians(110), math.radians(220), 2)

    surf.blit(s, (int(x - cx), int(y - cy)))

def draw_ruyi_dragon(surf, x, y, palette, scale=1.0):
    """Long horizontal Ruyi-spine dragon-cloud — 120 × 18 px aspect."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    # Body length trimmed 120 → 102 (-15%) per AD round-3: at 1× the
    # 120 px form ate more sky than the spacing budget allows for a
    # 3-cloud parallax band. Head 0.95×h and tail 0.35×h ratios held
    # constant, sine period stays at π * 1.4 — only the horizontal
    # footprint shrinks.
    length = int(102 * scale)
    h = int(20 * scale)
    pad = 8
    s = _alpha_surf(length + pad * 2, h * 3 + pad * 2)
    cx = pad + length // 2
    cy = s.get_height() // 2

    # Sine period dropped 2.2π → 1.4π per AD round-2 — round-1 zig-zag
    # read as a pufferfish at NIGHT. Undulation now reads as a single
    # gentle dragon coil rather than two compressed peaks.
    sine_period = math.pi * 1.4

    # Spine — soft horizontal body painted as stacked low-alpha
    # ellipses with a gentle sinusoidal undulation, mimicking a dragon's
    # coil from imperial robe motifs. The spine is what carries the
    # "elongated Ruyi" read; the lobes punctuate.
    spine_n = 14
    for i in range(spine_n):
        t = i / (spine_n - 1)
        sx = pad + int(t * length)
        sy = cy + int(math.sin(t * sine_period) * h * 0.45)
        sw = max(4, int(h * 1.4 * (1 - abs(t - 0.5))))
        sh = max(2, h - 2)
        a = int(_lerp(160, 220, 1 - abs(t - 0.5) * 2))
        pygame.draw.ellipse(
            s, (*body, a),
            pygame.Rect(sx - sw // 2, sy - sh // 2, sw, sh))

    # Three Ruyi-lobe punctuation points along the spine: tail (left),
    # mid-coil, head (right). Head pushed to 0.95× h, tail dropped to
    # 0.35× h per AD round-2 — round-1 lobes were too uniform and the
    # dragon had no head/tail directionality. The eye now reads the
    # body as flowing left-to-right with the head at the right edge.
    spine_pts = (
        (pad + int(length * 0.10), cy + int(math.sin(0.10 * sine_period) * h * 0.45), int(h * 0.35)),
        (pad + int(length * 0.50), cy + int(math.sin(0.50 * sine_period) * h * 0.45), int(h * 0.55)),
        (pad + int(length * 0.88), cy + int(math.sin(0.88 * sine_period) * h * 0.45), int(h * 0.95)),
    )
    for i, (lx, ly, lr) in enumerate(spine_pts):
        _ruyi_lobe(s, lx, ly, lr, body, edge, lit,
                   body_a=240, key_a=150, lit_arc=(i == 2))

    # Curling tail-tip Ruyi inner-curl on the rightmost (head) lobe —
    # small spiral arc tracing 180°→20° outside the head lobe so the
    # dragon's flick reads as "tail of breath" coming off the leading
    # edge. AD round-2: directional cue at distance.
    hx, hy, hr = spine_pts[2]
    curl_r = max(3, int(hr * 0.55))
    curl_cx = hx + hr - 1
    curl_cy = hy - int(hr * 0.20)
    pygame.draw.arc(
        s, (*edge, 200),
        pygame.Rect(curl_cx - curl_r, curl_cy - curl_r,
                    curl_r * 2, curl_r * 2),
        math.radians(40), math.radians(280), 1)

    # Ink-shadow undertow — single very thin long ellipse beneath the
    # spine. Gated at night per cross-cutting A: deep-blue night sky
    # turns the dark undertow into a smudge halo. Day/golden keep the
    # shadow for body-depth read.
    if not night:
        pygame.draw.ellipse(
            s, (*edge, 50),
            pygame.Rect(pad + 4, cy + h // 2, length - 8, max(2, h // 3)))

    surf.blit(s, (int(x - cx), int(y - cy)))

def draw_ruyi_mandala(surf, x, y, palette, scale=1.0):
    """Radial 6-lobe Tang caisson cloud — the denser contrast direction."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    w = int(78 * scale)
    h = int(56 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # Inner tier — 1 large central lobe.
    centre_r = int(h * 0.22)
    pygame.draw.circle(s, (*edge, 50), (cx + 1, cy + 2), centre_r + 1)

    # Outer tier — 6 satellite lobes in a hexagonal mandala arrangement.
    # The radial layout is what gives the variant its Tang caisson read;
    # exactly six lobes matches the most common Mogao panel.
    outer_r = int(h * 0.16)
    ring_radius = int(h * 0.36)
    for k in range(6):
        ang = (k / 6) * math.tau - math.pi / 2
        ox = cx + int(math.cos(ang) * ring_radius)
        oy = cy + int(math.sin(ang) * ring_radius * 0.78)
        pygame.draw.circle(s, (*edge, 38), (ox + 1, oy + 2), outer_r + 1)
        _ruyi_lobe(s, ox, oy, outer_r, body, edge, lit,
                   body_a=235, key_a=145, lit_arc=False)

    # Centre lobe drawn LAST so it sits on top of the satellite-lobe
    # arc keylines that would otherwise overlap into the middle.
    _ruyi_lobe(s, cx, cy, centre_r, body, edge, lit,
               body_a=250, key_a=180, lit_arc=True)

    surf.blit(s, (int(x - cx), int(y - cy)))

def draw_ruyi_deco(surf, x, y, palette, scale=1.0):
    """Ruyi Eclipse — heart silhouette with hard half-light / half-shadow split."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    stone_dark = palette.get('stone_dark', edge)
    horizon = palette['horizon']
    sky_top = palette['sky_top']

    # Two-tone body palette per AD spec.
    body_lit = _cloud_body_color(palette)
    # Cool shadow — pulled toward stone_dark + horizon so the dark half
    # reads as a single graphic shadow, not a generic grey.
    body_shadow = _mix(stone_dark, horizon, 0.55)
    # Single hard 3 px outline keyline — heavy chevron-rim per AD spec.
    keyline = _mix(stone_dark, sky_top, 0.4)

    head_r = int(15 * scale)
    pad = int(head_r * 2) + 8
    s = _alpha_surf(pad * 2 + head_r * 3, pad * 2 + head_r * 3)
    cx = s.get_width() // 2
    cy = s.get_height() // 2

    # Drop-shadow gated at night per cross-cutting A.
    if not night:
        pygame.draw.circle(s, (*edge, 40), (cx + 2, cy + 3), head_r + 2)

    # Eclipse split — upper/left half of the heart is lit, lower/right
    # half is shadow. Implemented by drawing the heart fully in the lit
    # tone, then over-painting a half-disc shadow on the same heart's
    # twin-lobe layout. The split is the design's geometric clarity.
    _ruyi_heart(s, cx, cy, head_r, body_lit, keyline, lit,
                body_a=240, key_a=210, lit_arc=False)

    # Shadow overlay — paint the shadow tone onto the heart's right /
    # lower flank. Done by drawing two filled half-circles (right halves
    # of each twin lobe) at alpha 200, so the rest of the body shows
    # through as the lit half. This is the "eclipse" hard divide.
    off = max(2, int(head_r * 0.55))
    lr = max(3, int(head_r * 0.78))
    lcy = cy - max(1, int(head_r * 0.10))
    for half_cx, ang_a, ang_b in (
        (cx - off, math.radians(340), math.radians(160)),
        (cx + off, math.radians(340), math.radians(160)),
    ):
        # Filled right-half arc emulated by stacking thin pie-slice
        # lines from centre. Cheap and silhouette-clipped because the
        # heart body already exists under it.
        for k in range(lr):
            t = (k + 1) / (lr + 1)
            seg_r = int(lr * t)
            pygame.draw.arc(
                s, (*body_shadow, 200),
                pygame.Rect(half_cx - seg_r, lcy - seg_r,
                            seg_r * 2, seg_r * 2),
                ang_a, ang_b, 2)

    # Heavy 3 px outline keyline running the entire heart silhouette —
    # survives at all scales (AD spec). Two arcs flanking the twin
    # lobes so the keyline traces the canonical Ruyi double-curl
    # rather than a flat circle outline.
    pygame.draw.arc(
        s, (*keyline, 240),
        pygame.Rect(cx - off - lr, lcy - lr, lr * 2, lr * 2),
        math.radians(180), math.radians(360), 3)
    pygame.draw.arc(
        s, (*keyline, 240),
        pygame.Rect(cx + off - lr, lcy - lr, lr * 2, lr * 2),
        math.radians(180), math.radians(360), 3)
    # Bottom V-curve of the heart — single arc joining the two lobes'
    # base curves so the silhouette reads as one continuous chevron.
    pygame.draw.arc(
        s, (*keyline, 240),
        pygame.Rect(cx - off - lr // 2, lcy - 2,
                    (off + lr // 2) * 2, lr + 4),
        math.radians(20), math.radians(160), 3)

    # Single warm rim accent along the lit half so the eclipse split
    # doesn't go flat-graphic. Directional cue per cross-cutting D —
    # the lit side of the eclipse always sits on the upper-left flank.
    pygame.draw.arc(
        s, (*lit, 200),
        pygame.Rect(cx - off - lr + 1, lcy - lr + 1,
                    lr * 2 - 2, lr * 2 - 2),
        math.radians(180), math.radians(280), 2)

    surf.blit(s, (int(x - cx), int(y - cy)))

def draw_cloud_origami(surf, x, y, palette, scale=1.0):
    """Faceted paper-fold cloud — pillow silhouette with lit/shadow split."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(74 * scale)
    h = int(46 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)

    cx = pad + w // 2
    cy = pad + h // 2

    # Two faceted plane tones — lit (upper-left) and shadow (lower-
    # right) — so the polygon reads as a folded sheet catching light.
    face_lit = _lerp_color(body, lit, 0.40)
    face_shadow = _lerp_color(body, edge, 0.30)
    # Crease keyline brightens against deep-blue night so the fold
    # geometry doesn't dissolve into the shadow plane; day keeps the
    # original body-toward-edge crease so the keyline still reads as
    # one confident ink line against the lit facet.
    if night:
        crease = _lerp_color(edge, lit, 0.45)
    else:
        crease = _lerp_color(edge, body, 0.35)

    # Five-vertex pillow profile: the silhouette family says "cloud"
    # before the faceted shading announces "paper" as the second beat.
    # Apex sits left-of-centre so the crease angle isn't symmetric and
    # the fold reads as a deliberate paper crease rather than a tent.
    body_poly = [
        (pad + int(w * 0.06), pad + int(h * 0.62)),  # left wing
        (pad + int(w * 0.40), pad + int(h * 0.08)),  # apex / lit peak
        (pad + int(w * 0.78), pad + int(h * 0.24)),  # right shoulder
        (pad + int(w * 0.96), pad + int(h * 0.58)),  # right wing
        (pad + int(w * 0.50), pad + int(h * 0.92)),  # belly low
    ]
    pygame.draw.polygon(s, (*face_shadow, 240), body_poly)

    # Lit plane — upper-left half cut along the crease running from
    # left wing through the apex out to the right shoulder. The brighter
    # triangle sits where a top-left light source would actually catch
    # the folded paper.
    lit_poly = [
        (pad + int(w * 0.06), pad + int(h * 0.62)),
        (pad + int(w * 0.40), pad + int(h * 0.08)),
        (pad + int(w * 0.78), pad + int(h * 0.24)),
        (pad + int(w * 0.50), pad + int(h * 0.55)),
    ]
    pygame.draw.polygon(s, (*face_lit, 235), lit_poly)

    # Crease keyline — single ridge running from the belly up through
    # the apex out to the right shoulder. One clean fold is the signal
    # that the shape is paper, not a vapour blob.
    crease_pts = [
        (pad + int(w * 0.50), pad + int(h * 0.92)),
        (pad + int(w * 0.40), pad + int(h * 0.08)),
        (pad + int(w * 0.78), pad + int(h * 0.24)),
    ]
    pygame.draw.lines(s, (*crease, 220), False, crease_pts,
                      max(1, int(scale * 1.4)))

    # Full silhouette outline — 1-px keyline so the paper edge stays
    # crisp against busy backdrops. Night drops alpha so the line
    # doesn't read as overbright against deep blue.
    outline_a = 220 if not night else 170
    pygame.draw.lines(s, (*edge, outline_a), True, body_poly,
                      max(1, int(scale * 1.2)))

    # One sharp lit highlight at the apex — paper catches a sun specular
    # at fold vertices. Drawn as a tiny lit triangle so the highlight
    # has angular character matching the faceted geometry.
    apex = (pad + int(w * 0.40), pad + int(h * 0.08))
    hi_pts = [
        apex,
        (apex[0] - max(2, int(scale * 3)), apex[1] + max(3, int(scale * 4))),
        (apex[0] + max(2, int(scale * 3)), apex[1] + max(3, int(scale * 4))),
    ]
    pygame.draw.polygon(s, (*lit, 230), hi_pts)

    surf.blit(s, (int(x - cx), int(y - cy)))

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

# Active rotation. Each run picks one variant at random (scenes/intro use
# random.randrange(VARIANT_COUNT)); nothing persists a variant id, so retiring one
# and letting the rest renumber is safe. All designs are kept defined above for
# easy re-activation — add them back to the tuple to restore them.
# Currently pinned to the mandala design (user request).
_VARIANTS = (draw_ruyi_mandala,)
VARIANT_COUNT = len(_VARIANTS)
