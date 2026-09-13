"""Round-1 mountain redesign — 5 distinct, palette-driven mountain ranges.

Each renderer keeps the live ``draw_mountains`` contract so it drops straight
into the review harness::

    def variant(surf, scroll, ground_y, w, far_color, near_color)

All colour is derived from the two biome mountain colours (plus a synthesised
``mtn_back``) so every concept re-themes correctly across the day cycle —
warm at golden/sunset, deep blue at night — instead of hard-coding a look.
We keep the three-layer parallax (back 0.06 / far 0.15 / near 0.28) so the
depth read matches the rest of the world, and lean on translucent haze bands
between layers for atmospheric perspective rather than flat silhouettes.
"""
from __future__ import annotations

import math
import random

import pygame


# ── shared colour + geometry helpers ─────────────────────────────────────────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    """Linear blend a→b. t is clamped so callers can pass eased values freely."""
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _luma(c) -> float:
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255.0


def _back_color(far):
    """Synthesise the most-distant ridge tint — the live draw does the same,
    pushing the far colour toward a pale sky-ish value so it recedes."""
    return (_clamp((far[0] + 200) // 2),
            _clamp((far[1] + 210) // 2),
            _clamp((far[2] + 230) // 2))


def _haze(far, near):
    """Atmospheric veil colour — a lightened, desaturated far tone. Used as a
    translucent band so each receding layer sits in a little more 'air'."""
    base = _mix(far, (235, 238, 248), 0.55)
    return base


def _ridge(w, ground_y, scroll, speed, base_h, terms, step=2):
    """Sampled ridgeline. ``terms`` is a list of (freq, amp, phase) sines that
    sum into the height profile, letting each concept tune its own silhouette
    character (smooth dunes vs. jagged peaks) from one helper."""
    pts = [(0, ground_y)]
    heights: list[tuple[int, int]] = []
    for x in range(0, w + 1, step):
        sx = x + scroll * speed
        h = base_h
        for freq, amp, ph in terms:
            h += math.sin(sx * freq + ph) * amp
        y = ground_y - int(h)
        pts.append((x, y))
        heights.append((x, y))
    pts.append((w, ground_y))
    return pts, heights


def _haze_band(surf, heights, ground_y, color, top_alpha, depth):
    """Soft gradient veil hugging the top of a ridge, fading downward — sells
    distance without flattening the silhouette. Drawn as horizontal slabs so
    it stays cheap on both native and WASM."""
    if not heights:
        return
    top = min(y for _, y in heights)
    band = pygame.Surface((surf.get_width(), depth), pygame.SRCALPHA)
    for i in range(depth):
        a = int(top_alpha * (1.0 - i / depth))
        if a <= 0:
            continue
        pygame.draw.line(band, (color[0], color[1], color[2], a),
                         (0, i), (surf.get_width(), i))
    surf.blit(band, (0, max(0, top - depth // 3)))


# ══════════════════════════════════════════════════════════════════════════
# V1 — Danxia Rainbow Strata
# Diagonal mineral bands (hematite red → ochre → cream → violet) banded across
# each ridge, with sharp boundaries. Band hues are biome-tinted so they warm at
# golden hour and cool at night while keeping the rainbow read.
# ══════════════════════════════════════════════════════════════════════════

def _danxia_palette(near):
    """Six mineral bands keyed off the near-mountain tone so the rainbow
    inherits the time-of-day mood instead of fighting it."""
    warm = _luma(near)
    # Canonical Danxia minerals, then pull each toward the biome tone so the
    # set desaturates and darkens together at dusk/night.
    raw = [
        (170, 60, 55),    # hematite red
        (205, 120, 60),   # iron orange
        (225, 185, 110),  # goethite ochre
        (235, 225, 200),  # cream marl
        (150, 130, 165),  # magnetite violet-grey
        (120, 95, 120),   # shadowed band
    ]
    # Keep the rainbow vivid by day; only pull hard toward the biome tone once
    # the scene goes dark so night reads as moonlit strata, not a daytime
    # rainbow pasted on a dark sky.
    pull = 0.25 + (1.0 - warm) * 0.45
    return [_mix(c, near, pull) for c in raw]


def _danxia_layer(surf, heights, ground_y, bands, slant, seed):
    """Fill under a ridge with bold diagonal mineral strata. Each column gets
    a stack of evenly spaced bands; a per-column slant offset shears the whole
    stack so the boundaries run diagonally — the wind-folded Danxia look — and
    bands stay parallel and crisp rather than noisy. Bands follow the contour
    and never spill above the silhouette because they start at the ridge y."""
    n = len(bands)
    band_h = 9  # thick, readable mineral stripe at 360px wide
    for x, y in heights:
        depth = ground_y - y
        if depth <= 0:
            continue
        # Diagonal shear: deeper slant pushes the colour index along with x so
        # a single mineral band rises across the face from right to left.
        shear = int(x * slant + math.sin(x * 0.018 + seed) * 3)
        ny = y
        while ny < ground_y:
            ci = ((ny - y + shear) // band_h) % n
            seg = min(band_h, ground_y - ny)
            pygame.draw.line(surf, bands[ci], (x, ny), (x, ny + seg))
            ny += band_h


def draw_mountains_v1(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far = far_color or (90, 70, 120)
    near = near_color or (60, 45, 95)
    back = _back_color(far)
    haze = _haze(far, near)

    # BACK — smooth distant ridge, lightly banded so it reads as the same
    # geology without competing for attention.
    pts, hb = _ridge(w, ground_y, scroll, 0.06, 100,
                     [(0.010, 24, 0.8), (0.026, 11, 2.1)])
    bands_back = _danxia_palette(_mix(near, back, 0.6))
    pygame.draw.polygon(surf, bands_back[3], pts)
    _danxia_layer(surf, hb, ground_y, bands_back, slant=0.18, seed=11)
    _haze_band(surf, hb, ground_y, haze, 150, 26)

    # FAR — full rainbow strata.
    pts, hf = _ridge(w, ground_y, scroll, 0.15, 76,
                     [(0.013, 30, 1.4), (0.033, 14, 0.3)])
    bands_far = _danxia_palette(_mix(near, far, 0.4))
    pygame.draw.polygon(surf, bands_far[2], pts)
    _danxia_layer(surf, hf, ground_y, bands_far, slant=0.26, seed=29)
    _haze_band(surf, hf, ground_y, haze, 90, 18)

    # NEAR — strongest saturation + crisp ridge rimlight.
    pts, hn = _ridge(w, ground_y, scroll, 0.28, 52,
                     [(0.018, 22, 0.5), (0.045, 10, 1.9)])
    bands_near = _danxia_palette(near)
    pygame.draw.polygon(surf, bands_near[1], pts)
    _danxia_layer(surf, hn, ground_y, bands_near, slant=0.34, seed=53)
    # Sunlit ridge rim picks up the brightest mineral band.
    rim = _shade(bands_near[3], 25)
    pygame.draw.lines(surf, rim, False, hn, 1)


# ══════════════════════════════════════════════════════════════════════════
# V2 — Wind-Sculpted Dunes
# Smooth flowing sand ridges, each split into a lit windward face and a
# shadowed slip face along the crest, with a warm sand gradient per layer.
# ══════════════════════════════════════════════════════════════════════════

def _sand_tones(base):
    lit = _mix(base, (255, 240, 200), 0.45)
    shadow = _shade(base, -38)
    return lit, base, shadow


def _dune_layer(surf, heights, ground_y, lit, mid, shadow, crest_bias):
    """Render a dune band: vertical gradient mid→shadow downward, then a bright
    crest highlight on the windward (left) side of each local peak. crest_bias
    shifts where the lit/shadow split lands so layers don't look identical."""
    w = surf.get_width()
    # Body gradient — light near crest, deeper toward the base.
    top = min(y for _, y in heights)
    depth = ground_y - top
    body = pygame.Surface((w, ground_y - top), pygame.SRCALPHA)
    for i in range(ground_y - top):
        t = i / max(1, depth)
        col = _mix(mid, shadow, t * 0.9)
        pygame.draw.line(body, col, (0, i), (w, i))
    # Clip the gradient to under the ridge by overpainting the sky region.
    poly = [(x, y - top) for x, y in heights]
    poly = [(0, ground_y - top)] + poly + [(w, ground_y - top)]
    mask = pygame.Surface((w, ground_y - top), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (0, top))

    # Crest highlight: follow the ridge and brighten the windward slope where
    # the line descends to the left (sun from upper-left).
    for i in range(1, len(heights)):
        x0, y0 = heights[i - 1]
        x1, y1 = heights[i]
        slope = y1 - y0
        if slope > crest_bias:  # descending toward the right → lit windward
            pygame.draw.line(surf, lit, (x0, y0), (x1, y1), 2)
        else:
            pygame.draw.line(surf, _shade(mid, -10), (x0, y0), (x1, y1), 1)
    # Fine wind-ripple striations parallel to the crest.
    rng = random.Random(int(min(y for _, y in heights)))
    for _ in range(int(w / 22)):
        idx = rng.randrange(0, len(heights) - 1)
        x, y = heights[idx]
        ry = y + rng.randint(6, max(7, depth - 6))
        if ry < ground_y - 2:
            pygame.draw.line(surf, _mix(mid, lit, 0.3),
                             (x - rng.randint(3, 9), ry), (x, ry), 1)


def draw_mountains_v2(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far = far_color or (120, 100, 130)
    near = near_color or (90, 70, 95)
    back = _back_color(far)
    haze = _haze(far, near)

    lit, mid, sh = _sand_tones(_mix(back, far, 0.5))
    pts, hb = _ridge(w, ground_y, scroll, 0.06, 92,
                     [(0.009, 20, 0.3), (0.021, 9, 1.7)])
    pygame.draw.polygon(surf, mid, pts)
    _dune_layer(surf, hb, ground_y, lit, mid, sh, crest_bias=1)
    _haze_band(surf, hb, ground_y, haze, 150, 26)

    lit, mid, sh = _sand_tones(far)
    pts, hf = _ridge(w, ground_y, scroll, 0.15, 66,
                     [(0.012, 26, 1.0), (0.027, 11, 0.4)])
    pygame.draw.polygon(surf, mid, pts)
    _dune_layer(surf, hf, ground_y, lit, mid, sh, crest_bias=0)
    _haze_band(surf, hf, ground_y, haze, 80, 16)

    lit, mid, sh = _sand_tones(near)
    pts, hn = _ridge(w, ground_y, scroll, 0.28, 46,
                     [(0.016, 20, 0.5), (0.034, 8, 2.2)])
    pygame.draw.polygon(surf, mid, pts)
    _dune_layer(surf, hn, ground_y, lit, mid, sh, crest_bias=-1)


# ══════════════════════════════════════════════════════════════════════════
# V3 — Alpine Snow Peaks
# Sharp jagged granite ridges with snow caps that pool in the high crevices,
# a darker rock body, blue-shadowed valleys and haze pooling between ranges.
# ══════════════════════════════════════════════════════════════════════════

def _snow_color(near):
    """Snow takes the scene's highlight: bright + cool by day, moonlit blue at
    night, peach at sunrise — biased toward the near tone's hue."""
    base = (245, 248, 255)
    return _mix(base, _shade(near, 90), 0.35)


def _alpine_layer(surf, heights, ground_y, rock_lo, rock_hi, snow, snow_line):
    """Rock body with a vertical gradient, plus snow filling everything above a
    per-column snow line so caps cling to the peaks and melt into the valleys."""
    w = surf.get_width()
    top = min(y for _, y in heights)
    depth = ground_y - top
    poly = [(0, ground_y - top)] + [(x, y - top) for x, y in heights] + [(w, ground_y - top)]
    body = pygame.Surface((w, depth), pygame.SRCALPHA)
    for i in range(depth):
        t = i / max(1, depth)
        pygame.draw.line(body, _mix(rock_hi, rock_lo, t), (0, i), (w, i))
    mask = pygame.Surface((w, depth), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (0, top))

    # Snow: for each column, the peaks (lowest y) hold the most snow. Snow
    # reaches down to snow_line below the local crest, jittered for crevices.
    for i in range(1, len(heights)):
        x0, y0 = heights[i - 1]
        x1, y1 = heights[i]
        # Local relief — only well-above-average crests keep deep snow.
        cap = int(snow_line * (0.4 + 0.6 * max(0, (ground_y - 30 - y1)) / max(1, depth)))
        # Sunlit (left) faces get a touch more snow than shaded faces.
        pygame.draw.polygon(
            surf, snow,
            [(x0, y0), (x1, y1), (x1, y1 + cap), (x0, y0 + cap)])
    # Crisp white ridge highlight.
    pygame.draw.lines(surf, _shade(snow, 8), False, heights, 1)


def draw_mountains_v3(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far = far_color or (70, 95, 150)
    near = near_color or (45, 65, 120)
    back = _back_color(far)
    haze = _haze(far, near)
    snow = _snow_color(near)

    pts, hb = _ridge(w, ground_y, scroll, 0.06, 112,
                     [(0.011, 30, 0.8), (0.029, 16, 2.1), (0.071, 7, 0.4)])
    _alpine_layer(surf, hb, ground_y, _mix(back, far, 0.5),
                  _mix(back, (255, 255, 255), 0.3),
                  _mix(snow, back, 0.45), snow_line=14)
    _haze_band(surf, hb, ground_y, haze, 160, 30)

    pts, hf = _ridge(w, ground_y, scroll, 0.15, 84,
                     [(0.014, 34, 1.4), (0.037, 18, 0.3), (0.083, 8, 1.1)])
    _alpine_layer(surf, hf, ground_y, _shade(far, -25), far,
                  _mix(snow, far, 0.2), snow_line=18)
    _haze_band(surf, hf, ground_y, haze, 95, 20)

    pts, hn = _ridge(w, ground_y, scroll, 0.28, 56,
                     [(0.019, 26, 0.5), (0.047, 13, 1.9), (0.099, 6, 0.8)])
    _alpine_layer(surf, hn, ground_y, _shade(near, -22), near,
                  snow, snow_line=22)


# ══════════════════════════════════════════════════════════════════════════
# V4 — Shan-Shui Ink Ridges
# Soft layered ridgelines, each a flat wash that fades from saturated at the
# crest to near-transparent at the base, separated by thick fog bands —
# atmospheric perspective straight out of ink-wash landscape painting.
# ══════════════════════════════════════════════════════════════════════════

def _ink_layer(surf, heights, ground_y, ink, alpha_top, fade):
    """A translucent wash that's densest at the ridge crest and dissolves
    downward, mimicking ink bleeding into wet paper."""
    w = surf.get_width()
    top = min(y for _, y in heights)
    depth = ground_y - top
    wash = pygame.Surface((w, depth), pygame.SRCALPHA)
    for i in range(depth):
        t = i / max(1, depth)
        a = int(alpha_top * (1.0 - t) ** fade)
        if a > 0:
            pygame.draw.line(wash, (ink[0], ink[1], ink[2], a), (0, i), (w, i))
    poly = [(0, depth)] + [(x, y - top) for x, y in heights] + [(w, depth)]
    mask = pygame.Surface((w, depth), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    wash.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(wash, (0, top))
    # Darker brushed crest line — the calligraphic ridge stroke.
    pygame.draw.lines(surf, _shade(ink, -30), False, heights, 1)


def draw_mountains_v4(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far = far_color or (95, 105, 135)
    near = near_color or (55, 60, 90)
    haze = _haze(far, near)

    # Many thin ridges, far→near, each darker, with a fog veil between them so
    # depth reads as receding washes rather than stacked solids.
    ridge_specs = [
        (0.05, 104, 130, _mix(near, haze, 0.72)),
        (0.08, 92, 150, _mix(near, haze, 0.58)),
        (0.13, 80, 175, _mix(near, far, 0.7)),
        (0.20, 66, 200, _mix(near, far, 0.4)),
        (0.28, 50, 225, near),
    ]
    for k, (speed, base_h, atop, ink) in enumerate(ridge_specs):
        pts, h = _ridge(w, ground_y, scroll, speed, base_h,
                        [(0.011 + k * 0.002, 22 - k * 2, 0.6 + k),
                         (0.030 + k * 0.004, 10, 1.5 - k * 0.3)])
        _ink_layer(surf, h, ground_y, ink, atop, fade=1.6)
        if k < len(ridge_specs) - 1:
            _haze_band(surf, h, ground_y, haze, 70, 22)


# ══════════════════════════════════════════════════════════════════════════
# V5 — Mesa Buttes
# Flat-topped desert plateaus and buttes with stratified terrace bands, a
# warm sunlit rim on the left face and a cool shadowed right face.
# ══════════════════════════════════════════════════════════════════════════

def _mesa_profile(w, ground_y, scroll, speed, base_h, seed, step_w, jitter):
    """Stepped, flat-topped silhouette: a chain of plateaus at quantised
    heights with vertical cliff drops between them — the mesa skyline. Heights
    snap to a terrace grid so the buttes read as the same sedimentary layers
    stacked to different counts (the Monument-Valley signature)."""
    phase = scroll * speed
    pts = [(0, ground_y)]
    heights: list[tuple[int, int]] = []
    x = 0
    cur_h = base_h
    while x <= w:
        k = int((x + phase) // step_w)
        r = random.Random((k * 2654435761 ^ seed) & 0xFFFFFFFF)
        # Snap to terrace multiples so plateaus line up across the range.
        levels = r.choice([0, 1, 1, 2, 2, 3])
        cur_h = base_h + levels * jitter
        seg = step_w + r.randint(-step_w // 5, step_w // 5)
        y = ground_y - int(cur_h)
        # Vertical cliff up to the new plateau, then a flat top.
        if heights:
            pts.append((x, heights[-1][1]))
        pts.append((x, y))
        heights.append((x, y))
        for xx in range(x, min(w, x + seg), 3):
            pts.append((xx, y))
            heights.append((xx, y))
        x += seg
    pts.append((w, ground_y - int(cur_h)))
    pts.append((w, ground_y))
    return pts, heights


def _mesa_terraces(surf, heights, ground_y, rock_lo, rock_hi, rim, bands=4):
    w = surf.get_width()
    top = min(y for _, y in heights)
    depth = ground_y - top
    body = pygame.Surface((w, depth), pygame.SRCALPHA)
    for i in range(depth):
        t = i / max(1, depth)
        # Quantise into hard terrace bands for the sedimentary stratum look,
        # and darken the very top of each band so each terrace casts a thin
        # ledge shadow — the cue that sells stacked rock layers.
        step = t * bands
        bt = math.floor(step) / bands
        col = _mix(rock_hi, rock_lo, bt)
        if step - math.floor(step) < 0.16:
            col = _shade(col, -22)
        pygame.draw.line(body, col, (0, i), (w, i))
    poly = [(0, depth)] + [(x, y - top) for x, y in heights] + [(w, depth)]
    mask = pygame.Surface((w, depth), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (0, top))
    # Bright sunlit rim on every plateau top + cliff edge.
    pygame.draw.lines(surf, rim, False, heights, 2)


def draw_mountains_v5(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far = far_color or (130, 90, 90)
    near = near_color or (95, 60, 65)
    back = _back_color(far)
    haze = _haze(far, near)
    rim = _mix(near, (255, 225, 180), 0.5)

    pts, hb = _mesa_profile(w, ground_y, scroll, 0.06, 70, 7, 64, 20)
    _mesa_terraces(surf, hb, ground_y, _mix(back, far, 0.5),
                   _mix(back, (255, 240, 215), 0.35),
                   _shade(rim, -10), bands=3)
    _haze_band(surf, hb, ground_y, haze, 150, 26)

    pts, hf = _mesa_profile(w, ground_y, scroll, 0.15, 52, 23, 52, 22)
    _mesa_terraces(surf, hf, ground_y, _shade(far, -28), far, rim, bands=4)
    _haze_band(surf, hf, ground_y, haze, 80, 16)

    pts, hn = _mesa_profile(w, ground_y, scroll, 0.28, 34, 41, 46, 24)
    _mesa_terraces(surf, hn, ground_y, _shade(near, -30),
                   _mix(near, (255, 200, 160), 0.25), rim, bands=5)


# ── baseline (current live design) for side-by-side comparison ───────────────

def draw_mountains_baseline(surf, scroll, ground_y, w, far_color=None, near_color=None):
    """Verbatim reproduction of game.draw.draw_mountains so the contact sheet
    can show the existing look in the same scene. Kept self-contained here so
    the live module is never imported/altered by the exploration."""
    far_color = far_color or (35, 45, 100)
    near_color = near_color or (22, 30, 72)
    back_color = (_clamp((far_color[0] + 200) // 2),
                  _clamp((far_color[1] + 210) // 2),
                  _clamp((far_color[2] + 230) // 2))
    pts_back = [(0, ground_y)]
    pts_far = [(0, ground_y)]
    pts_near = [(0, ground_y)]
    for x in range(0, w + 1, 2):
        bx = x + scroll * 0.06
        hb = int(105 + math.sin(bx * 0.008) * 32 + math.sin(bx * 0.023 + 2.1) * 14)
        pts_back.append((x, ground_y - hb))
        fx = x + scroll * 0.15
        hf = int(80 + math.sin(fx * 0.012) * 42 + math.sin(fx * 0.031) * 22)
        pts_far.append((x, ground_y - hf))
        nx = x + scroll * 0.28
        hn = int(55 + math.sin(nx * 0.019 + 1.4) * 34 + math.sin(nx * 0.047 + 0.7) * 16)
        pts_near.append((x, ground_y - hn))
    for pts in (pts_back, pts_far, pts_near):
        pts.append((w, ground_y))
    pygame.draw.polygon(surf, back_color, pts_back)
    pygame.draw.polygon(surf, far_color, pts_far)
    pygame.draw.polygon(surf, near_color, pts_near)


# ── dispatcher ───────────────────────────────────────────────────────────────

VARIANTS = {
    0: draw_mountains_baseline,
    1: draw_mountains_v1,
    2: draw_mountains_v2,
    3: draw_mountains_v3,
    4: draw_mountains_v4,
    5: draw_mountains_v5,
}

VARIANT_NAMES = {
    0: "Baseline (current)",
    1: "Danxia Rainbow Strata",
    2: "Wind-Sculpted Dunes",
    3: "Alpine Snow Peaks",
    4: "Shan-Shui Ink Ridges",
    5: "Mesa Buttes",
}
