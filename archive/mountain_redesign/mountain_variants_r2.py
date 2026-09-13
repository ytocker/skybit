"""Round-2 background exploration — refined V2/V4 plus five "go wild" concepts.

Round 1 stayed strictly on the mountain theme; the brief for round 2 is "a
really cool background that fits the game atmosphere — go wild". So beyond the
two refined dune/ink ranges, the new concepts are free-form mid-background
forms (floating islands, crystal spires, glowing canyons, aurora ridges, a
distant skyline) — but each keeps the live ``draw_mountains`` contract so the
winner drops straight into the world::

    def variant(surf, scroll, ground_y, w, far_color, near_color)

Every colour is still derived from the biome palette (the two passed mountain
tones, plus a few extra keys pulled from ``game.biome`` for richer mid-tones)
so the whole set re-themes across the day cycle instead of hard-coding a look.
We keep the three-layer parallax read (≈0.06 / 0.15 / 0.28) wherever the form
allows, and lean on translucent haze for atmospheric depth.

Fidelity bump over round 1: ridge sampling steps 1px (was 2), gradients are
built per-band, and crest strokes are drawn so they stay crisp at full size —
the round-1 sheet read low-res because it down-sampled to half tiles.
"""
from __future__ import annotations

import math
import random

import pygame

from game import biome as _biome


# ── shared colour + geometry helpers ─────────────────────────────────────────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _luma(c) -> float:
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255.0


def _sat(c, f):
    """Scale saturation around the colour's own luma — f>1 vivid, f<1 muted."""
    g = _luma(c) * 255.0
    return (_clamp(g + (c[0] - g) * f),
            _clamp(g + (c[1] - g) * f),
            _clamp(g + (c[2] - g) * f))


def _back_color(far):
    return (_clamp((far[0] + 200) // 2),
            _clamp((far[1] + 210) // 2),
            _clamp((far[2] + 230) // 2))


def _haze(far, near):
    return _mix(far, (235, 238, 248), 0.55)


def _ridge(w, ground_y, scroll, speed, base_h, terms, step=1):
    """Sampled ridgeline summed from sine terms. step=1 keeps crests smooth at
    full 360px width (round 1 used step=2 and read jaggy when scaled)."""
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


def _aa_crest(surf, heights, color, width=1):
    """Anti-aliased ridge stroke where it's cheap (native+WASM both support
    aaline). Falls back gracefully if the segment list is short."""
    if len(heights) < 2:
        return
    pygame.draw.aalines(surf, color, False, heights)
    if width > 1:
        pygame.draw.lines(surf, color, False, heights, width)


def _gradient_fill(surf, heights, ground_y, top_col, bot_col, ease=1.0):
    """Vertical gradient clipped under a ridge silhouette. One reusable body
    builder so every concept gets a real per-band gradient, not a flat fill."""
    w = surf.get_width()
    top = min(y for _, y in heights)
    depth = ground_y - top
    if depth <= 0:
        return top, depth
    body = pygame.Surface((w, depth), pygame.SRCALPHA)
    for i in range(depth):
        t = (i / max(1, depth)) ** ease
        pygame.draw.line(body, _mix(top_col, bot_col, t), (0, i), (w, i))
    poly = [(0, depth)] + [(x, y - top) for x, y in heights] + [(w, depth)]
    mask = pygame.Surface((w, depth), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (0, top))
    return top, depth


# ══════════════════════════════════════════════════════════════════════════
# V1 — Danxia Rainbow Strata (REFINED, round-1 returning favourite)
# Diagonal mineral strata — hematite red → iron orange → goethite ochre →
# cream marl → magnetite violet — sheared across each ridge face. Round 1 drew
# flat per-column line stacks; this rebuild samples a sheared band coordinate
# per pixel through a smooth multi-stop mineral ramp, so every band carries its
# own crest→base gradient, boundaries are AA-feathered rather than hard-stepped,
# and a horizon-keyed sunlit rim catches the upper edge. Mineral hues are pulled
# toward the biome near/horizon tones and darkened by ``star_alpha`` so the
# rainbow stays vivid by day and reads as moonlit strata at night.
# ══════════════════════════════════════════════════════════════════════════

def _danxia_ramp(near, horizon, night):
    """Smooth mineral ramp as ordered (stop, colour). ``stop`` is the fraction
    along the sheared band axis where each mineral peaks; interpolating between
    them gives soft band-to-band transitions instead of flat slabs. Every hue is
    pulled toward the biome ``near`` tone, lifted slightly toward ``horizon`` on
    the warm minerals, and darkened by ``night`` (0..1) so the set desaturates
    and dims into dusk rather than sitting as a daytime rainbow on a dark sky."""
    raw = [
        (0.00, (188, 64, 58)),    # hematite red — top crest band
        (0.20, (214, 116, 62)),   # iron orange
        (0.40, (232, 178, 104)),  # goethite ochre
        (0.58, (240, 224, 192)),  # cream marl — the bright relief band
        (0.76, (176, 120, 150)),  # magnetite violet
        (1.00, (120, 84, 116)),   # shadowed basal band
    ]
    pull = 0.22 + night * 0.42
    out = []
    for k, (stop, c) in enumerate(raw):
        col = _mix(c, near, pull)
        if stop < 0.55:  # warm minerals catch a little horizon glow
            col = _mix(col, horizon, 0.12 * (1.0 - night * 0.5))
        col = _shade(col, int(-46 * night))
        out.append((stop, col))
    return out


def _ramp_at(ramp, t):
    """Sample the ordered mineral ramp at axis position ``t`` (0..1)."""
    t = max(0.0, min(1.0, t))
    for i in range(1, len(ramp)):
        s0, c0 = ramp[i - 1]
        s1, c1 = ramp[i]
        if t <= s1:
            f = (t - s0) / max(1e-5, s1 - s0)
            return _mix(c0, c1, f)
    return ramp[-1][1]


def _danxia_layer(surf, heights, ground_y, ramp, slant, band_scale, seed,
                  rim_col):
    """Fill under a ridge with sheared mineral strata. For each pixel the band
    axis is ``(y - x*slant)`` so equal-value contours run as parallel diagonals
    — the wind-folded Danxia signature. The axis is wrapped through the ramp,
    and a thin darkened seam at each band boundary plus an AA crest sell crisp,
    high-relief stratification rather than a smooth wash."""
    w = surf.get_width()
    top = min(y for _, y in heights)
    depth = ground_y - top
    if depth <= 0:
        return
    xy = {x: y for x, y in heights}
    body = pygame.Surface((w, depth), pygame.SRCALPHA)
    period = band_scale  # px between repeats of the full mineral sequence
    wobble = band_scale * 0.16
    for x in range(w):
        ry = xy.get(x)
        if ry is None:  # step>1 ridges: nearest sampled column
            ry = xy.get(min(xy, key=lambda k: abs(k - x)))
        # Per-column phase wobble bends the strata so seams aren't ruler-straight.
        ph = math.sin(x * 0.02 + seed) * wobble
        for y in range(ry, ground_y):
            axis = ((y - x * slant + ph) % period) / period
            col = _ramp_at(ramp, axis)
            # Thin dark seam at the wrap boundary reads as a bedding plane.
            edge = min(axis, 1.0 - axis)
            if edge < 0.04:
                col = _shade(col, -22)
            # Gentle vertical relief: lift the band a touch near the crest so the
            # face catches light, deepen toward the base.
            vt = (y - top) / depth
            col = _shade(col, int(10 - 26 * vt))
            body.set_at((x, y - top), col)
    poly = [(0, depth)] + [(x, y - top) for x, y in heights] + [(w, depth)]
    mask = pygame.Surface((w, depth), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (0, top))
    # Sunlit ridge rim — horizon-keyed, AA'd, sits exactly on the silhouette.
    _aa_crest(surf, heights, rim_col)


def draw_mountains_v1(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    night = min(1.0, pal['star_alpha'] / 235.0)
    back = _back_color(far)
    haze = _haze(far, near)

    # BACK — distant, hazier strata; tighter bands so it reads as the same
    # geology receding, and a softer rim so it doesn't compete with the front.
    pts, hb = _ridge(w, ground_y, scroll, 0.06, 100,
                     [(0.010, 24, 0.8), (0.026, 11, 2.1)])
    ramp_b = _danxia_ramp(_mix(near, back, 0.55), horizon, min(1.0, night + 0.1))
    rim_b = _mix(far, horizon, 0.5)
    _danxia_layer(surf, hb, ground_y, ramp_b, slant=0.22, band_scale=46,
                  seed=11, rim_col=rim_b)
    _haze_band(surf, hb, ground_y, _mix(haze, horizon, 0.2), 150, 26)

    # FAR — full rainbow, mid band scale.
    pts, hf = _ridge(w, ground_y, scroll, 0.15, 76,
                     [(0.013, 30, 1.4), (0.033, 14, 0.3)])
    ramp_f = _danxia_ramp(_mix(near, far, 0.4), horizon, night)
    rim_f = _mix(near, horizon, 0.55)
    _danxia_layer(surf, hf, ground_y, ramp_f, slant=0.30, band_scale=56,
                  seed=29, rim_col=rim_f)
    _haze_band(surf, hf, ground_y, _mix(haze, horizon, 0.12), 90, 18)

    # NEAR — strongest saturation + brightest sunlit rim; widest bands so the
    # closest strata read large and bold.
    pts, hn = _ridge(w, ground_y, scroll, 0.28, 52,
                     [(0.018, 22, 0.5), (0.045, 10, 1.9)])
    ramp_n = _danxia_ramp(_sat(near, 1.05), horizon, night)
    rim_n = _mix(_mix(near, horizon, 0.6), (255, 245, 220), 0.4 * (1.0 - night))
    _danxia_layer(surf, hn, ground_y, ramp_n, slant=0.38, band_scale=66,
                  seed=53, rim_col=rim_n)


# ══════════════════════════════════════════════════════════════════════════
# V2 — Wind-Sculpted Dunes (REFINED)
# Richer multi-tone sand: each dune face runs a crest→trough gradient through
# rose / gold / amber / mauve stops keyed off the biome tone, with a smooth
# lit-windward / shadowed-slip-face split and finer wind-ripple striations.
# ══════════════════════════════════════════════════════════════════════════

def _sand_ramp(base):
    """Five-stop sand ramp from a single biome tone. Highlights push toward
    warm gold, mids hold the biome hue, shadows fall into a cool mauve so the
    dunes read as lit sand rather than one muddy brown — the colour the user
    asked for. Each stop stays tinted by ``base`` so it re-themes at night."""
    crest = _mix(base, (255, 236, 188), 0.62)        # sun-struck crest, gold
    upper = _mix(base, (244, 196, 150), 0.40)         # warm amber upper face
    mid = _mix(base, (215, 150, 130), 0.18)           # rose body
    lower = _shade(_mix(base, (120, 95, 130), 0.30), -10)  # mauve trough
    shadow = _shade(_mix(base, (70, 55, 95), 0.35), -22)   # cool slip-face shade
    return crest, upper, mid, lower, shadow


def _dune_layer(surf, heights, ground_y, ramp, crest_bias, ripple_density):
    crest, upper, mid, lower, shadow = ramp
    w = surf.get_width()
    top = min(y for _, y in heights)
    depth = ground_y - top
    if depth <= 0:
        return
    # Multi-stop vertical gradient: crest→upper→mid→lower→shadow. A small set
    # of stops interpolated by depth gives the rose/gold/amber/mauve banding.
    stops = [crest, upper, mid, lower, shadow]
    body = pygame.Surface((w, depth), pygame.SRCALPHA)
    for i in range(depth):
        t = i / max(1, depth)
        seg = t * (len(stops) - 1)
        k = min(len(stops) - 2, int(seg))
        col = _mix(stops[k], stops[k + 1], seg - k)
        pygame.draw.line(body, col, (0, i), (w, i))
    poly = [(0, depth)] + [(x, y - top) for x, y in heights] + [(w, depth)]
    mask = pygame.Surface((w, depth), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (0, top))

    # Smooth lit/shadow split along the crest: descending-right slopes catch
    # the sun (bright crest line), ascending slopes fall into slip-face shade.
    for i in range(1, len(heights)):
        x0, y0 = heights[i - 1]
        x1, y1 = heights[i]
        if (y1 - y0) > crest_bias:
            pygame.draw.aaline(surf, crest, (x0, y0), (x1, y1))
        else:
            pygame.draw.aaline(surf, _mix(mid, shadow, 0.45), (x0, y0), (x1, y1))

    # Fine wind-ripple striations — short, near-horizontal strokes hugging the
    # contour. Denser + finer than round 1 for a sculpted-sand read.
    rng = random.Random(top * 131 + depth)
    for _ in range(int(w * ripple_density)):
        idx = rng.randrange(0, len(heights) - 1)
        x, y = heights[idx]
        ry = y + rng.randint(4, max(5, depth - 4))
        if ry < ground_y - 2:
            length = rng.randint(4, 11)
            tone = _mix(mid, upper, rng.uniform(0.2, 0.6))
            pygame.draw.aaline(surf, tone, (x - length, ry + 1), (x, ry))


def draw_mountains_v2(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far = far_color or (120, 100, 130)
    near = near_color or (90, 70, 95)
    back = _back_color(far)
    haze = _haze(far, near)

    pts, hb = _ridge(w, ground_y, scroll, 0.06, 92,
                     [(0.009, 20, 0.3), (0.021, 9, 1.7), (0.05, 3, 0.9)])
    _dune_layer(surf, hb, ground_y, _sand_ramp(_mix(back, far, 0.5)),
                crest_bias=1, ripple_density=0.05)
    _haze_band(surf, hb, ground_y, haze, 150, 26)

    pts, hf = _ridge(w, ground_y, scroll, 0.15, 66,
                     [(0.012, 26, 1.0), (0.027, 11, 0.4), (0.06, 4, 2.1)])
    _dune_layer(surf, hf, ground_y, _sand_ramp(far),
                crest_bias=0, ripple_density=0.07)
    _haze_band(surf, hf, ground_y, haze, 80, 16)

    pts, hn = _ridge(w, ground_y, scroll, 0.28, 46,
                     [(0.016, 20, 0.5), (0.034, 8, 2.2), (0.07, 4, 1.3)])
    _dune_layer(surf, hn, ground_y, _sand_ramp(near),
                crest_bias=-1, ripple_density=0.09)


# ══════════════════════════════════════════════════════════════════════════
# V4 — Shan-Shui Ink Ridges (REFINED)
# Layered washes, but each ridge layer now carries a distinct theme-matched
# colour wash (cool/violet far → warm/saturated near) instead of near-mono
# grey, with crisper, brighter fog veils opening the gaps between layers.
# ══════════════════════════════════════════════════════════════════════════

def _ink_wash(surf, heights, ground_y, ink_top, ink_bot, alpha_top, fade):
    """Translucent wash, densest + most saturated at the crest, dissolving and
    cooling toward the base. Two-colour so each layer reads as tinted ink."""
    w = surf.get_width()
    top = min(y for _, y in heights)
    depth = ground_y - top
    if depth <= 0:
        return
    wash = pygame.Surface((w, depth), pygame.SRCALPHA)
    for i in range(depth):
        t = i / max(1, depth)
        a = int(alpha_top * (1.0 - t) ** fade)
        if a <= 0:
            continue
        col = _mix(ink_top, ink_bot, t)
        pygame.draw.line(wash, (col[0], col[1], col[2], a), (0, i), (w, i))
    poly = [(0, depth)] + [(x, y - top) for x, y in heights] + [(w, depth)]
    mask = pygame.Surface((w, depth), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    wash.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(wash, (0, top))
    # Calligraphic crest stroke — a darker, saturated brush edge, AA'd.
    _aa_crest(surf, heights, _shade(_sat(ink_top, 1.2), -28))


def draw_mountains_v4(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    haze = _mix(_haze(far, near), horizon, 0.35)

    # Far layers lean cool/atmospheric toward the horizon tint; near layers get
    # the saturated biome ink. Each (speed, base_h, alpha, top_ink, bot_ink).
    far_tint = _mix(far, horizon, 0.45)
    specs = [
        (0.05, 104, 120, _mix(far_tint, (235, 238, 248), 0.30), far_tint),
        (0.08, 92, 145, _mix(far_tint, far, 0.6), _mix(far_tint, haze, 0.5)),
        (0.13, 80, 170, _sat(far, 1.15), _mix(far, haze, 0.45)),
        (0.20, 66, 200, _sat(_mix(near, far, 0.4), 1.2), _mix(near, far, 0.5)),
        (0.28, 50, 230, _sat(near, 1.25), _mix(near, far, 0.3)),
    ]
    for k, (speed, base_h, atop, itop, ibot) in enumerate(specs):
        pts, h = _ridge(w, ground_y, scroll, speed, base_h,
                        [(0.011 + k * 0.002, 22 - k * 2, 0.6 + k),
                         (0.030 + k * 0.004, 10, 1.5 - k * 0.3)])
        # Fog veils between bands removed — they read as coloured horizontal
        # stripes across the frame. Each wash layer's own ramped alpha already
        # carries the soft atmospheric transition.
        _ink_wash(surf, h, ground_y, itop, ibot, atop, fade=1.6)


# ══════════════════════════════════════════════════════════════════════════
# NEW 1 — Floating Sky Islands
# Drifting chunks of land at three parallax depths, each with a grass-lit cap,
# a rocky underbelly tapering to a point, and a few hanging roots/vines. Caps
# borrow the biome foliage tones; rock borrows the mountain tones.
# ══════════════════════════════════════════════════════════════════════════

def _island(surf, cx, cy, scale, rock_hi, rock_lo, grass_hi, grass_lo, rim, rng):
    """One floating island: elliptical grassy top + downward rocky spike."""
    rw = int(34 * scale)
    grass_h = int(11 * scale)
    spike_h = int(40 * scale)
    # Rocky underbelly — irregular downward wedge, faceted.
    base_y = cy + grass_h // 2
    left = (cx - rw, base_y)
    right = (cx + rw, base_y)
    tip = (cx + rng.randint(-6, 6), base_y + spike_h)
    mid_l = (cx - rw // 2, base_y + spike_h // 2 + rng.randint(-4, 4))
    mid_r = (cx + rw // 2, base_y + spike_h // 2 + rng.randint(-4, 4))
    rock = [left, mid_l, tip, mid_r, right]
    pygame.draw.polygon(surf, rock_lo, rock)
    # Lit left facet of the rock.
    pygame.draw.polygon(surf, rock_hi, [left, mid_l, tip])
    pygame.draw.aalines(surf, _shade(rock_lo, -18), False, rock)
    # Grassy cap — flattened ellipse sitting on the rock shoulders.
    cap = pygame.Rect(cx - rw, cy - grass_h, rw * 2, grass_h * 2)
    pygame.draw.ellipse(surf, grass_lo, cap)
    pygame.draw.ellipse(surf, grass_hi,
                        pygame.Rect(cx - rw, cy - grass_h, rw * 2, grass_h + 2))
    pygame.draw.arc(surf, rim, cap, math.pi, math.tau, 2)
    # Hanging roots/vines from the underbelly.
    for _ in range(int(2 + scale * 2)):
        vx = cx + rng.randint(-rw + 4, rw - 4)
        vy = base_y + rng.randint(2, 6)
        pygame.draw.line(surf, _mix(rock_lo, grass_lo, 0.4),
                         (vx, vy), (vx + rng.randint(-2, 2),
                                    vy + int(rng.randint(8, 18) * scale)), 1)


def _island_band(surf, w, ground_y, scroll, speed, y_base, scale, spacing,
                 rock_hi, rock_lo, grass_hi, grass_lo, rim, seed):
    phase = scroll * speed
    k0 = int(phase // spacing) - 1
    for k in range(k0, k0 + int(w / spacing) + 3):
        rng = random.Random((k * 374761393 ^ seed) & 0xFFFFFFFF)
        x = int(k * spacing - phase) + rng.randint(-12, 12)
        if -60 < x < w + 60:
            y = y_base + rng.randint(-18, 18)
            s = scale * rng.uniform(0.78, 1.18)
            _island(surf, x, y, s, rock_hi, rock_lo, grass_hi, grass_lo, rim, rng)


def draw_mountains_islands(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    g_top = pal['foliage_top']
    g_mid = pal['foliage_mid']
    haze = _haze(far, near)

    # BACK band — small, hazy, high.
    _island_band(surf, w, ground_y, scroll, 0.06, ground_y - 150, 0.7, 150,
                 _mix(far, (255, 240, 210), 0.25), _mix(far, near, 0.4),
                 _mix(g_top, far, 0.45), _mix(g_mid, far, 0.5),
                 _mix(g_top, (255, 255, 255), 0.3), 17)
    # FAR band.
    _island_band(surf, w, ground_y, scroll, 0.15, ground_y - 95, 0.95, 132,
                 _mix(far, (255, 235, 200), 0.3), far,
                 _mix(g_top, far, 0.2), g_mid,
                 _mix(g_top, (255, 255, 255), 0.4), 41)
    # NEAR band — largest, most saturated, lowest.
    _island_band(surf, w, ground_y, scroll, 0.28, ground_y - 40, 1.25, 150,
                 _mix(near, (255, 225, 180), 0.35), near,
                 _mix(g_top, pal['foliage_accent'], 0.2), g_mid,
                 _shade(g_top, 30), 73)


# ══════════════════════════════════════════════════════════════════════════
# NEW 2 — Crystal / Geode Spires
# Clusters of tall faceted crystal shards rising from the horizon, each shard a
# two-tone facet split with an emissive inner glow and a bright rim. Glow hue
# borrows the biome accent so it blooms warm by day and electric at night.
# ══════════════════════════════════════════════════════════════════════════

def _crystal_cluster(surf, cx, base_y, h, lit, dark, glow, rim, rng):
    """A fan of 3–5 shards sharing a base, tallest in the middle."""
    n = rng.randint(3, 5)
    for i in range(n):
        off = (i - (n - 1) / 2.0)
        sh = int(h * (1.0 - abs(off) * rng.uniform(0.16, 0.26)))
        bx = cx + int(off * h * 0.16)
        top = (bx + rng.randint(-3, 3), base_y - sh)
        half = max(3, int(sh * rng.uniform(0.12, 0.18)))
        bl = (bx - half, base_y)
        br = (bx + half, base_y)
        # Split facet: left lit, right shadow, meeting at a centre ridge.
        ridge_b = (bx, base_y)
        pygame.draw.polygon(surf, lit, [top, bl, ridge_b])
        pygame.draw.polygon(surf, dark, [top, br, ridge_b])
        # Emissive core: a thin bright sliver up the centre ridge.
        pygame.draw.aaline(surf, glow, (bx, base_y), top)
        pygame.draw.aaline(surf, rim, top, bl)
        # Soft glow halo at the tip.
        halo = pygame.Surface((half * 4, half * 4), pygame.SRCALPHA)
        for r in range(half * 2, 0, -2):
            a = int(70 * (1 - r / (half * 2)))
            pygame.draw.circle(halo, (glow[0], glow[1], glow[2], a),
                               (half * 2, half * 2), r)
        surf.blit(halo, (top[0] - half * 2, top[1] - half * 2),
                  special_flags=pygame.BLEND_RGBA_ADD)


def _crystal_band(surf, w, ground_y, scroll, speed, y_base, h, spacing,
                  lit, dark, glow, rim, seed):
    phase = scroll * speed
    k0 = int(phase // spacing) - 1
    for k in range(k0, k0 + int(w / spacing) + 3):
        rng = random.Random((k * 2246822519 ^ seed) & 0xFFFFFFFF)
        x = int(k * spacing - phase) + rng.randint(-18, 18)
        if -50 < x < w + 50:
            ch = int(h * rng.uniform(0.7, 1.15))
            _crystal_cluster(surf, x, y_base + rng.randint(-6, 6), ch,
                             lit, dark, glow, rim, rng)


def draw_mountains_crystal(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    accent = pal['stone_accent']
    haze = _haze(far, near)
    # Emissive glow hue: blend the warm accent toward an electric cyan/magenta
    # so it pops at night; biome accent keeps it warm by day.
    glow = _mix(accent, (140, 230, 255), 0.45)
    glow = _sat(glow, 1.3)

    # A dark, hazy ridge base so the crystals have something to grow out of.
    pts, hb = _ridge(w, ground_y, scroll, 0.06, 60, [(0.01, 14, 0.5)])
    _gradient_fill(surf, hb, ground_y, _mix(far, haze, 0.5), far, ease=1.2)
    _haze_band(surf, hb, ground_y, haze, 130, 22)

    _crystal_band(surf, w, ground_y, scroll, 0.06, ground_y - 60, 70, 150,
                  _mix(far, glow, 0.3), _mix(far, near, 0.55),
                  _mix(glow, (255, 255, 255), 0.2), _mix(glow, (255, 255, 255), 0.5), 17)
    _haze_band(surf, hb, ground_y, haze, 70, 16)
    _crystal_band(surf, w, ground_y, scroll, 0.15, ground_y - 30, 95, 124,
                  _mix(far, glow, 0.35), _shade(_mix(far, near, 0.4), -10),
                  glow, _mix(glow, (255, 255, 255), 0.55), 41)
    _crystal_band(surf, w, ground_y, scroll, 0.28, ground_y - 4, 125, 138,
                  _mix(near, glow, 0.4), _shade(near, -18),
                  _sat(glow, 1.4), _mix(glow, (255, 255, 255), 0.6), 73)


# ══════════════════════════════════════════════════════════════════════════
# NEW 3 — Bioluminescent Canyon
# Dark layered canyon mesas in silhouette, each veined with rivers of glowing
# spores/lichen that pool brightest near the rims and trickle down the faces.
# The glow is additive so it reads emissive against the night sky and warm by
# day. Inspired by deep-cave bioluminescence palettes (cyan/teal/magenta).
# ══════════════════════════════════════════════════════════════════════════

def _biolum_layer(surf, heights, ground_y, body_top, body_bot, glow, density, seed):
    top, depth = _gradient_fill(surf, heights, ground_y, body_top, body_bot, ease=1.3)
    if depth <= 0:
        return
    w = surf.get_width()
    # Glowing rim hugging the crest — additive so it blooms into the sky a bit.
    rim = pygame.Surface((w, 8), pygame.SRCALPHA)
    crest_top = min(y for _, y in heights)
    for i, (x, y) in enumerate(heights):
        for dy in range(-3, 4):
            a = int(120 * (1 - abs(dy) / 4))
            yy = y + dy - crest_top + 3
            if 0 <= yy < 8 and a > 0:
                rim.set_at((x, yy), (glow[0], glow[1], glow[2], a))
    surf.blit(rim, (0, crest_top - 3), special_flags=pygame.BLEND_RGBA_ADD)
    # Trickling veins down the faces + glowing pools.
    rng = random.Random(seed ^ (crest_top * 911))
    for _ in range(int(w * density)):
        idx = rng.randrange(len(heights))
        x, y = heights[idx]
        vx = x
        vy = y
        steps = rng.randint(6, 16)
        pts = [(vx, vy)]
        for _s in range(steps):
            vx += rng.randint(-2, 2)
            vy += rng.randint(2, 5)
            if vy >= ground_y:
                break
            pts.append((vx, vy))
        if len(pts) > 1:
            pygame.draw.aalines(surf, glow, False, pts)
            # A brighter glowing pool/node at the end.
            pool = pygame.Surface((10, 10), pygame.SRCALPHA)
            for r in range(5, 0, -1):
                a = int(110 * (1 - r / 5))
                pygame.draw.circle(pool, (glow[0], glow[1], glow[2], a), (5, 5), r)
            surf.blit(pool, (pts[-1][0] - 5, pts[-1][1] - 5),
                      special_flags=pygame.BLEND_RGBA_ADD)


def draw_mountains_biolum(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    accent = pal['foliage_accent']
    haze = _haze(far, near)
    # Spore glow: teal-cyan by default, pulled toward the biome foliage accent
    # so it warms at golden hour and stays vivid mint at night.
    glow_far = _sat(_mix(accent, (90, 230, 210), 0.55), 1.25)
    glow_near = _sat(_mix(accent, (120, 255, 235), 0.6), 1.35)

    pts, hb = _ridge(w, ground_y, scroll, 0.06, 100,
                     [(0.01, 24, 0.6), (0.027, 11, 1.8)])
    _biolum_layer(surf, hb, ground_y, _shade(_mix(far, near, 0.5), -10),
                  _shade(near, -25), glow_far, 0.05, 17)
    _haze_band(surf, hb, ground_y, _mix(haze, glow_far, 0.2), 80, 20)

    pts, hf = _ridge(w, ground_y, scroll, 0.15, 76,
                     [(0.013, 30, 1.4), (0.033, 14, 0.3)])
    _biolum_layer(surf, hf, ground_y, _shade(near, -20), _shade(near, -45),
                  _mix(glow_far, glow_near, 0.5), 0.07, 41)
    _haze_band(surf, hf, ground_y, _mix(haze, glow_near, 0.15), 60, 16)

    pts, hn = _ridge(w, ground_y, scroll, 0.28, 52,
                     [(0.018, 22, 0.5), (0.045, 10, 1.9)])
    _biolum_layer(surf, hn, ground_y, _shade(near, -40), _shade(near, -65),
                  glow_near, 0.10, 73)


# ══════════════════════════════════════════════════════════════════════════
# NEW 4 — Aurora Ridgelines
# Low, soft rolling ridges in dark silhouette, fronted by a tall vertical
# aurora curtain rising from behind the far ridge — ribboned bands of light
# that sway with parallax. Curtain hues borrow the sky/horizon palette so the
# aurora always harmonises with the sky behind it.
# ══════════════════════════════════════════════════════════════════════════

def _aurora_curtain(surf, w, ground_y, scroll, top_y, hues, strength, seed):
    """Discrete vertical light streamers. Each ribbon owns its hue and only
    paints where its own gaussian band is the clear local winner above a
    threshold, so dark sky shows between streamers instead of merging into a
    solid slab. ``strength`` (0..1) scales the whole curtain by how dark the
    sky is — auroras read against night, wash out by day, like the real thing.
    Additive but alpha-capped so the sky still shows through."""
    if strength <= 0.02:
        return
    h = ground_y - top_y
    curtain = pygame.Surface((w, h), pygame.SRCALPHA)
    rng = random.Random(seed)
    # Each ribbon snakes: its centre x is a function of y, so the streamer
    # curves like a real auroral curtain instead of standing as a stiff bar.
    ribbons = []
    for r in range(5):
        ribbons.append(dict(
            base=rng.uniform(0.08, 0.92),       # rough screen fraction
            drift=rng.uniform(0.004, 0.007),    # horizontal scroll drift
            phase=rng.uniform(0, math.tau),
            sway_amp=rng.uniform(18, 40),       # how far it snakes with y
            sway_freq=rng.uniform(0.006, 0.013),
            sigma=rng.uniform(11, 20),          # soft width
            top=rng.randint(0, 40),             # ragged top start
            hue=hues[r % len(hues)],
        ))
    peak = 70 * strength
    drift = scroll * 0.04
    for r in ribbons:
        cx0 = r['base'] * w - (math.sin(drift * r['drift'] + r['phase']) * 0)
        for yy in range(r['top'], h):
            ty = (yy - r['top']) / max(1, h - r['top'])
            # Curtain centre snakes with height; whole ribbon drifts with scroll.
            centre = (cx0
                      + math.sin(yy * r['sway_freq'] + r['phase']) * r['sway_amp']
                      + math.sin(drift * r['drift'] + r['phase']) * 24)
            vfade = (1.0 - ty) ** 1.25 * (0.4 + 0.6 * math.sin(ty * math.pi) ** 0.4)
            half = r['sigma']
            lo = int(centre - half * 2.5)
            hi = int(centre + half * 2.5)
            for x in range(max(0, lo), min(w, hi)):
                band = math.exp(-((x - centre) ** 2) / (2 * half * half))
                a = int(peak * band * vfade)
                if a <= 2:
                    continue
                prev = curtain.get_at((x, yy))
                # Additive accumulation in the buffer, capped, so crossing
                # ribbons brighten without blowing straight to white.
                na = min(150, prev[3] + a)
                curtain.set_at((x, yy), (r['hue'][0], r['hue'][1], r['hue'][2], na))
    surf.blit(curtain, (0, top_y), special_flags=pygame.BLEND_RGBA_ADD)


def draw_mountains_aurora(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    haze = _haze(far, near)
    # Aurora ribbon hues from the palette — foliage greens, sky/horizon tints,
    # plus a magenta lift so it reads as classic aurora regardless of time.
    hues = [
        _sat(_mix(pal['foliage_mid'], (120, 255, 180), 0.6), 1.4),
        _sat(_mix(pal['horizon'], (150, 220, 255), 0.4), 1.3),
        _sat(_mix(pal['sky_mid'], (200, 120, 255), 0.5), 1.3),
        _sat(_mix(pal['foliage_accent'], (160, 255, 220), 0.5), 1.35),
    ]

    # Aurora rises from behind the far ridge. Strength tracks how dark the sky
    # is (star_alpha climbs toward night) so it glows after dusk and all but
    # vanishes in daylight — but keep a faint floor so the row never reads
    # empty in the day/sunrise review cells.
    strength = 0.06 + 0.94 * min(1.0, pal['star_alpha'] / 235.0)
    _aurora_curtain(surf, w, ground_y, scroll, ground_y - 235, hues, strength, 17)

    # Three dark rolling ridges in front, so the curtain reads as "behind".
    pts, hb = _ridge(w, ground_y, scroll, 0.06, 86,
                     [(0.008, 22, 0.4), (0.02, 9, 1.6)])
    _gradient_fill(surf, hb, ground_y, _shade(_mix(far, near, 0.5), -25),
                   _shade(near, -40), ease=1.1)
    _aa_crest(surf, hb, _mix(far, hues[1], 0.3))
    _haze_band(surf, hb, ground_y, _mix(haze, hues[1], 0.2), 70, 18)

    pts, hf = _ridge(w, ground_y, scroll, 0.15, 60,
                     [(0.012, 26, 1.0), (0.03, 11, 0.4)])
    _gradient_fill(surf, hf, ground_y, _shade(near, -30), _shade(near, -55), ease=1.1)
    _aa_crest(surf, hf, _mix(near, hues[0], 0.3))

    pts, hn = _ridge(w, ground_y, scroll, 0.28, 38,
                     [(0.017, 20, 0.5), (0.04, 8, 2.2)])
    _gradient_fill(surf, hn, ground_y, _shade(near, -45), _shade(near, -70), ease=1.1)
    _aa_crest(surf, hn, _mix(near, hues[3], 0.3))


# ══════════════════════════════════════════════════════════════════════════
# NEW 5 — Distant Fantasy Skyline
# A receding city of spires, domes, towers and arches on the horizon. Far rows
# are flat hazy silhouettes; the near row gains lit windows and rim light. A
# storybook skyline that re-themes from sunny pastel to glowing night city.
# ══════════════════════════════════════════════════════════════════════════

def _spire(surf, x, base_y, w_, h, color, rng, roof):
    """A single tower: rectangular body + a roof (dome / cone / flat / arch)."""
    body = pygame.Rect(x - w_ // 2, base_y - h, w_, h)
    pygame.draw.rect(surf, color, body)
    cap_h = max(4, w_)
    if roof == 'dome':
        pygame.draw.ellipse(surf, color,
                            pygame.Rect(x - w_ // 2, base_y - h - cap_h, w_, cap_h * 2))
        pygame.draw.rect(surf, color, pygame.Rect(x - w_ // 2, base_y - h, w_, 4))
    elif roof == 'cone':
        pygame.draw.polygon(surf, color, [(x - w_ // 2, base_y - h),
                                          (x + w_ // 2, base_y - h),
                                          (x, base_y - h - cap_h - 4)])
    elif roof == 'arch':
        pygame.draw.ellipse(surf, color,
                            pygame.Rect(x - w_ // 2, base_y - h - w_, w_, w_ * 2))
    # flat → nothing extra
    return body


def _skyline_row(surf, w, ground_y, scroll, speed, y_base, hmin, hmax, spacing,
                 color, seed, lit_windows=False, window_glow=None, rim=None):
    phase = scroll * speed
    k0 = int(phase // spacing) - 1
    roofs = ['dome', 'cone', 'flat', 'arch', 'cone', 'dome']
    for k in range(k0, k0 + int(w / spacing) + 3):
        rng = random.Random((k * 40503 ^ seed) & 0xFFFFFFFF)
        x = int(k * spacing - phase) + rng.randint(-6, 6)
        if not (-40 < x < w + 40):
            continue
        tw = rng.randint(10, 20)
        th = rng.randint(hmin, hmax)
        roof = roofs[rng.randrange(len(roofs))]
        body = _spire(surf, x, y_base, tw, th, color, rng, roof)
        if rim:
            pygame.draw.line(surf, rim, body.topleft, body.bottomleft, 1)
            pygame.draw.line(surf, rim, body.topleft, body.topright, 1)
        if lit_windows and window_glow:
            cols = max(1, tw // 6)
            rows = max(1, th // 12)
            for cxi in range(cols):
                for ryi in range(rows):
                    if rng.random() < 0.55:
                        wx = body.left + 3 + cxi * 6
                        wy = body.top + 6 + ryi * 12
                        if wy < y_base - 3 and wx < body.right - 2:
                            surf.fill(window_glow, pygame.Rect(wx, wy, 2, 3))


def draw_mountains_skyline(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    haze = _haze(far, near)
    # Window glow: warm lamplight, leaning brighter at night via the horizon
    # tone (which goes pale-bright after dark in this palette).
    window_glow = _sat(_mix(pal['stone_accent'], (255, 220, 130), 0.5), 1.2)

    # BACK row — palest, hazy, tallest-but-thin spires far off.
    _skyline_row(surf, w, ground_y, scroll, 0.06, ground_y - 8, 70, 120, 70,
                 _mix(far, horizon, 0.5), 17)
    _haze_band(surf, [(0, ground_y - 120), (w, ground_y - 120)], ground_y,
               _mix(haze, horizon, 0.4), 110, 26)

    # FAR row.
    _skyline_row(surf, w, ground_y, scroll, 0.15, ground_y - 4, 55, 100, 58,
                 _mix(far, near, 0.5), 41)
    _haze_band(surf, [(0, ground_y - 100), (w, ground_y - 100)], ground_y,
               _mix(haze, horizon, 0.25), 70, 18)

    # NEAR row — darkest silhouette, rim-lit, with lit windows.
    rim = _mix(near, horizon, 0.5)
    _skyline_row(surf, w, ground_y, scroll, 0.28, ground_y, 40, 80, 48,
                 _shade(near, -18), 73, lit_windows=True,
                 window_glow=window_glow, rim=rim)


# ══════════════════════════════════════════════════════════════════════════
# ROUND-3 SHAN-SHUI EXPANSIONS — five derivatives of V4 pushed for PRESENCE
# Brief: V4 was the user's pick from round 2 but read soft and recessive.
# Round-3 set keeps the ink-wash DNA (layered tinted washes, atmospheric
# perspective, calligraphic crest strokes, fog veils between bands) but
# pushes for visible weight: larger silhouettes, stronger per-layer colour
# saturation, dynamic brushwork, and iconic East-Asian punctuation
# (karst spires, cloud sea, twisted pines, pagodas, glowing neon ink).
# Each variant must read as clearly distinct from V4 AND from the others.
# ══════════════════════════════════════════════════════════════════════════

def _ink_wash_strong(surf, heights, ground_y, ink_top, ink_bot, alpha_top,
                     fade=1.4, rim_col=None, rim_w=1):
    """Bolder cousin of ``_ink_wash``: opaque-feeling base alpha plus a
    distinct rim colour argument so the silhouette reads with weight while
    crest brushwork stays calligraphic. Used by every R3 shan-shui variant."""
    w = surf.get_width()
    top = min(y for _, y in heights)
    depth = ground_y - top
    if depth <= 0:
        return
    wash = pygame.Surface((w, depth), pygame.SRCALPHA)
    for i in range(depth):
        t = i / max(1, depth)
        a = int(alpha_top * (1.0 - t) ** fade)
        if a <= 0:
            continue
        col = _mix(ink_top, ink_bot, t)
        pygame.draw.line(wash, (col[0], col[1], col[2], a), (0, i), (w, i))
    poly = [(0, depth)] + [(x, y - top) for x, y in heights] + [(w, depth)]
    mask = pygame.Surface((w, depth), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    wash.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(wash, (0, top))
    if rim_col is not None:
        _aa_crest(surf, heights, rim_col, width=rim_w)


def _dry_brush_crest(surf, heights, color, density=0.55, max_drip=4, seed=0):
    """Sumi-e "flying-white" feel: scatter short vertical drip-strokes off
    the crest so the edge reads as a loaded brush instead of a smooth line.
    Cheap — only paints a few px per sampled column, both targets OK."""
    rng = random.Random(seed ^ (len(heights) * 91))
    for x, y in heights:
        if rng.random() > density:
            continue
        h = rng.randint(1, max_drip)
        for dy in range(h):
            a = max(0, 255 - int(64 * dy))
            surf.set_at((x, y + dy), (color[0], color[1], color[2]))


# ══════════════════════════════════════════════════════════════════════════
# V11 — Karst Pinnacles (Guilin / Halong)
# Vertical limestone spires emerging from a low mist band. Tall thin
# silhouettes (h ≫ w), three parallax depths. Near band hits ~55% of the
# screen height so the front reads as monumental; sumi-e calligraphic
# crest line with dry-brush flying-white at the tips, soft mist veils
# pooling between every band to sell ocean-of-mist atmosphere.
# Presence vs V4: replaces rolling washes with hard vertical spires that
# pierce upward, so the background reads with strong silhouette weight.
# ══════════════════════════════════════════════════════════════════════════

def _karst_silhouette(w, ground_y, scroll, speed, base_y, spacing, h_min, h_max,
                      width_min, width_max, seed):
    """Vertical-spire silhouette: build a saw-tooth-ish ridge where each
    "tooth" is a karst pinnacle with a slim convex top. ``heights`` returned
    has one entry per pixel column so the existing wash / crest helpers
    work without modification — every pinnacle becomes a continuous polygon
    with mist-line gaps between them."""
    phase = scroll * speed
    heights = []
    k0 = int(phase // spacing) - 2
    # Pre-compute the spire layout so each column samples it deterministically.
    spires = []
    for k in range(k0, k0 + int(w / spacing) + 4):
        rng = random.Random((k * 1664525 ^ seed) & 0xFFFFFFFF)
        cx = int(k * spacing - phase) + rng.randint(-spacing // 4, spacing // 4)
        sh = rng.randint(h_min, h_max)
        sw = rng.randint(width_min, width_max)
        # Pinnacles bow inward — wider at base, narrowing to a rounded crown.
        # Curve exponent biases the bulge: >1 sharper crown, <1 wider mid.
        bulge = rng.uniform(1.35, 2.1)
        tip_off = rng.randint(-2, 2)  # small crown wobble for organic feel
        spires.append((cx, sh, sw, bulge, tip_off))
    for x in range(w + 1):
        # The pinnacle this column belongs to is the nearest centre within
        # half-width; otherwise this column is mist (ground_y).
        best_y = base_y
        for cx, sh, sw, bulge, tip_off in spires:
            half = sw // 2
            if cx - half - 1 <= x <= cx + half + 1:
                # Normalised distance from centre, 0=middle, 1=edge.
                d = abs(x - cx) / max(1, half)
                if d > 1.0:
                    continue
                # Crown profile: 1 - d^bulge gives a sharp narrow crest.
                col_h = sh * (1.0 - d ** bulge)
                yy = base_y - int(col_h) + tip_off
                if yy < best_y:
                    best_y = yy
        heights.append((x, best_y))
    return heights


def draw_mountains_karst(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    night = min(1.0, pal['star_alpha'] / 235.0)
    haze = _mix(_haze(far, near), horizon, 0.30)

    # BACK band — small distant spires near the horizon, very hazy.
    far_tint = _mix(far, horizon, 0.40)
    base_b = ground_y - 12
    hb = _karst_silhouette(w, ground_y, scroll, 0.07, base_b,
                           spacing=46, h_min=70, h_max=120,
                           width_min=18, width_max=30, seed=11)
    _ink_wash_strong(surf, hb, ground_y, _mix(far_tint, (240, 244, 252), 0.18),
                     _mix(far_tint, haze, 0.5), alpha_top=170, fade=1.5,
                     rim_col=_mix(far, horizon, 0.45))
    # Horizontal mist veil — heavy at the base so the spires look like they
    # rise from a sea of cloud, classic shan-shui yúnhǎi look.
    _haze_band(surf, hb, ground_y,
               _mix(haze, (255, 255, 255), 0.25 * (1.0 - night)), 130, 28)

    # MID band — taller, denser, mid contrast.
    mid_tint = _mix(near, far, 0.4)
    base_m = ground_y + 8
    hm = _karst_silhouette(w, ground_y, scroll, 0.15, base_m,
                           spacing=58, h_min=150, h_max=240,
                           width_min=24, width_max=44, seed=29)
    _ink_wash_strong(surf, hm, ground_y,
                     _sat(_mix(mid_tint, far, 0.3), 1.1),
                     _mix(mid_tint, haze, 0.35), alpha_top=210, fade=1.6,
                     rim_col=_shade(_sat(mid_tint, 1.25), -20), rim_w=1)
    _dry_brush_crest(surf, hm,
                     _shade(_sat(mid_tint, 1.3), -36), density=0.32,
                     max_drip=3, seed=29)
    _haze_band(surf, hm, ground_y,
               _mix(haze, (255, 255, 255), 0.18 * (1.0 - night)), 105, 22)

    # NEAR band — monumental front-spires, near-opaque, brightest crest rim.
    near_ink = _sat(near, 1.20)
    base_n = ground_y + 16
    hn = _karst_silhouette(w, ground_y, scroll, 0.28, base_n,
                           spacing=72, h_min=240, h_max=330,
                           width_min=30, width_max=58, seed=53)
    _ink_wash_strong(surf, hn, ground_y, near_ink,
                     _mix(near_ink, far, 0.4), alpha_top=242, fade=1.5,
                     rim_col=_shade(_sat(near_ink, 1.3), -32), rim_w=1)
    _dry_brush_crest(surf, hn, _shade(_sat(near_ink, 1.35), -48),
                     density=0.40, max_drip=5, seed=53)


# ══════════════════════════════════════════════════════════════════════════
# V12 — Cloud Sea / Yúnhǎi Peaks
# Peak islands poking through a rolling cloud sea. Classic Huangshan motif:
# triangular mountain crowns float above thick horizontal cloud rolls so the
# bottom of each peak dissolves into bright mist. Multiple cloud bands stack
# with the peaks, and lit cloud edges catch the horizon glow.
# Presence vs V4: replaces uniform layered wash with a strong figure-ground
# contrast — bright cloud sea against dark peak crowns reads loud and far.
# ══════════════════════════════════════════════════════════════════════════

def _peak_silhouette(w, ground_y, scroll, speed, peak_y, peak_spacing,
                     peak_h_min, peak_h_max, base_anchor, jag, seed):
    """Mountain crown silhouette: triangular peaks with slightly jagged sides,
    each pulled up from ``base_anchor`` so the band reads as a chain of free-
    standing crowns rather than a single rolling ridge."""
    phase = scroll * speed
    heights = []
    k0 = int(phase // peak_spacing) - 2
    peaks = []
    for k in range(k0, k0 + int(w / peak_spacing) + 4):
        rng = random.Random((k * 2654435761 ^ seed) & 0xFFFFFFFF)
        cx = int(k * peak_spacing - phase) + rng.randint(-12, 12)
        ph = rng.randint(peak_h_min, peak_h_max)
        half = int(peak_spacing * rng.uniform(0.55, 0.78))
        # Slight asymmetry — Chinese ink peaks rarely sit symmetric.
        skew = rng.uniform(-0.18, 0.18)
        peaks.append((cx, ph, half, skew, rng))
    for x in range(w + 1):
        # Highest contributor wins (largest closest peak draws the column).
        best_y = base_anchor
        for cx, ph, half, skew, rng in peaks:
            if cx - half <= x <= cx + half:
                d = (x - cx) / max(1, half)  # -1..+1
                # Triangle profile with skew (one side steeper, like sumi-e).
                if d < 0:
                    f = 1.0 - abs(d) ** (1.1 + skew)
                else:
                    f = 1.0 - abs(d) ** (1.1 - skew)
                # Jagged jitter on the slope sells brushy ink edges.
                f += math.sin(x * 0.45 + cx) * jag / max(1, ph)
                yy = peak_y - int(ph * max(0.0, f))
                if yy < best_y:
                    best_y = yy
        heights.append((x, best_y))
    return heights


def _cloud_sea_band(surf, w, top_y, depth, base_col, hi_col, density, seed):
    """Horizontal rolling cloud sea: stacked horizontal bands of varying
    alpha and lit edges so it reads as billowing rolls, not a flat fill.
    The brightest highlight sits at the wave crest of each roll — that's
    where the sun catches the cloud sea in real Huangshan photos. Thickness
    and density both run high so the cloud sea reads bright and present
    rather than as a thin smear (previous tuning was too subtle)."""
    band = pygame.Surface((w, depth), pygame.SRCALPHA)
    rng = random.Random(seed)
    # Solid bright "floor" wash removed — its full-width horizontal lines read
    # as coloured stripes across the screen. The rolling cloud waves below
    # carry the cloud-sea body on their own; their per-wave gaussian falloff
    # plus the 5-7 stacked rolls fill the band volumetrically without forming
    # a continuous horizontal seam.
    # 5-7 rolling cloud "waves" stacked vertically with bright lit upper rims.
    n_rolls = rng.randint(5, 7)
    for r in range(n_rolls):
        roll_y = int((r + 0.5) / n_rolls * depth) + rng.randint(-3, 3)
        amp = rng.uniform(3.0, 6.0)
        freq = rng.uniform(0.015, 0.030)
        phase = rng.uniform(0, math.tau)
        thickness = rng.randint(8, 14)
        for x in range(w):
            cy = roll_y + math.sin(x * freq + phase) * amp
            for dy in range(-thickness, thickness + 1):
                yy = int(cy + dy)
                if 0 <= yy < depth:
                    a = int(density * math.exp(-(dy * dy) / (thickness * 0.55)))
                    if a <= 1:
                        continue
                    if dy < -thickness * 0.4:
                        col = hi_col
                    else:
                        col = base_col
                    prev = band.get_at((x, yy))
                    na = min(245, prev[3] + a)
                    band.set_at((x, yy), (col[0], col[1], col[2], na))
    surf.blit(band, (0, top_y))


def draw_mountains_cloudsea(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    night = min(1.0, pal['star_alpha'] / 235.0)
    haze = _mix(_haze(far, near), horizon, 0.35)
    # Cloud sea colour: bright on the lit edge keyed by horizon glow,
    # base tone slightly cooler so the rim "pops". At night the sea reads
    # as cold moonlit fog.
    cloud_hi = _mix((255, 250, 235), horizon, 0.45)
    cloud_hi = _shade(cloud_hi, int(-60 * night))
    cloud_base = _mix((220, 224, 235), haze, 0.55)
    cloud_base = _shade(cloud_base, int(-65 * night))

    # BACK peaks — small distant island crowns peeking just above the highest
    # cloud band so the eye reads "endless layers".
    far_tint = _mix(far, horizon, 0.40)
    base_b = ground_y - 80
    peak_y_b = ground_y - 90
    hb = _peak_silhouette(w, ground_y, scroll, 0.07,
                          peak_y=peak_y_b, peak_spacing=86,
                          peak_h_min=44, peak_h_max=86,
                          base_anchor=base_b, jag=1.5, seed=11)
    _ink_wash_strong(surf, hb, base_b,
                     _sat(far_tint, 1.0),
                     _mix(far_tint, haze, 0.6),
                     alpha_top=190, fade=1.4,
                     rim_col=_mix(far_tint, horizon, 0.55))
    _cloud_sea_band(surf, w, ground_y - 132, 56, cloud_base, cloud_hi,
                    density=170, seed=17)

    # MID peaks — main island chain, the focal hero band. Sharper, taller
    # crowns + tighter spacing so the silhouette holds presence.
    mid_tint = _mix(near, far, 0.35)
    base_m = ground_y - 30
    peak_y_m = ground_y - 40
    hm = _peak_silhouette(w, ground_y, scroll, 0.16,
                          peak_y=peak_y_m, peak_spacing=108,
                          peak_h_min=150, peak_h_max=220,
                          base_anchor=base_m, jag=3.2, seed=29)
    _ink_wash_strong(surf, hm, base_m,
                     _sat(mid_tint, 1.20),
                     _mix(mid_tint, haze, 0.30),
                     alpha_top=234, fade=1.55,
                     rim_col=_shade(_sat(mid_tint, 1.35), -32))
    _dry_brush_crest(surf, hm, _shade(_sat(mid_tint, 1.4), -48),
                     density=0.36, max_drip=4, seed=29)
    _cloud_sea_band(surf, w, ground_y - 76, 50, cloud_base, cloud_hi,
                    density=210, seed=41)

    # NEAR peaks — biggest crowns, rising tall through the lowest cloud roll
    # so they read up close, with the front cloud sea covering their feet.
    near_ink = _sat(near, 1.25)
    base_n = ground_y + 6
    peak_y_n = ground_y
    hn = _peak_silhouette(w, ground_y, scroll, 0.30,
                          peak_y=peak_y_n, peak_spacing=148,
                          peak_h_min=240, peak_h_max=320,
                          base_anchor=base_n, jag=3.8, seed=53)
    _ink_wash_strong(surf, hn, base_n,
                     near_ink,
                     _mix(near_ink, far, 0.40),
                     alpha_top=252, fade=1.55,
                     rim_col=_shade(_sat(near_ink, 1.35), -40))
    _dry_brush_crest(surf, hn, _shade(_sat(near_ink, 1.4), -56),
                     density=0.48, max_drip=6, seed=53)
    # Front cloud sea sits on the ground line, swallowing the spire feet.
    # Extra thickness here so the cloud rolls clearly cap the near peaks.
    _cloud_sea_band(surf, w, ground_y - 34, 36, cloud_base, cloud_hi,
                    density=220, seed=73)


# ══════════════════════════════════════════════════════════════════════════
# V13 — Sumi-e Bold Crags + Lone Pines
# Heavy near-black Huangshan-style jagged ridges with twisted lone pines
# clinging to crests. The whole set leans dark: high contrast against sky,
# rough sawtooth silhouettes, dry-brush "flying-white" edges, and one or
# two iconic gnarled pines per band as cultural punctuation.
# Presence vs V4: nearly opaque black ink instead of soft tinted wash;
# silhouettes are angular and aggressive instead of soft rollers.
# ══════════════════════════════════════════════════════════════════════════

def _crag_ridge(w, ground_y, scroll, speed, base_h, jag_amp, jag_freq, seed):
    """Sawtooth-flavoured ridge with sharp upward stabs at irregular spacing.
    Built on top of a low rolling base so the line still reads as a mountain
    range, just with hard angular sumi-e crags poking up."""
    rng = random.Random(seed)
    # Pre-roll the spike positions: a sparse list of "stab" centres with
    # random heights, summed onto the smooth base in pixel pass below.
    spikes = []
    for k in range(int(w / 30) + 6):
        spikes.append((rng.uniform(-1, w + 1) + (k - 2) * 30,
                       rng.uniform(jag_amp * 0.4, jag_amp * 1.6),
                       rng.uniform(8, 18)))  # spike half-width
    heights = []
    phase = scroll * speed
    for x in range(w + 1):
        sx = x + phase
        h = base_h + math.sin(sx * 0.012 + 0.3) * 18 + math.sin(sx * 0.027 + 1.4) * 9
        # Triangular stabs from the spike list.
        for cx, amp, half in spikes:
            sxs = (x + phase * 0.15) - cx
            if abs(sxs) < half:
                h += amp * (1.0 - abs(sxs) / half) ** 1.2
        # High-frequency tiny jag on top of everything for brushy roughness.
        h += math.sin(sx * jag_freq) * 2.0
        heights.append((x, ground_y - int(h)))
    return heights


def _lone_pine(surf, x, y_base, h, ink, accent, rng):
    """Twisted Huangshan-style pine in silhouette: short bent trunk with two
    flat horizontal canopy puffs, sumi-e simplification (no detail needles).
    Reads as iconic East-Asian punctuation at this scale."""
    if y_base <= h + 4:
        return
    # Bent trunk: 3 segments, each leaning slightly opposite for character.
    lean = rng.choice((-1, 1))
    seg = h // 3
    p0 = (x, y_base)
    p1 = (x + lean * 2, y_base - seg)
    p2 = (x + lean * 4, y_base - seg * 2)
    p3 = (x + lean * 2, y_base - h)
    pygame.draw.lines(surf, ink, False, [p0, p1, p2, p3], 2)
    # Two horizontal canopy puffs, the upper smaller. Flat ellipses for the
    # sumi-e "umbrella pine" silhouette.
    cw1 = int(h * 0.7)
    ch1 = max(3, h // 6)
    cw2 = int(h * 0.45)
    ch2 = max(2, h // 8)
    pygame.draw.ellipse(surf, ink,
                        pygame.Rect(p3[0] - cw1 // 2, p3[1] - ch1 - 1, cw1, ch1 * 2))
    pygame.draw.ellipse(surf, ink,
                        pygame.Rect(p3[0] - cw2 // 2, p3[1] - ch2 - h // 4, cw2, ch2 * 2))
    # Tiny accent dot at the highest point — the brush "tap" finishing stroke.
    surf.set_at((p3[0], p3[1] - ch1 - 2), accent)


def _crag_pines(surf, heights, ground_y, count, ink, accent, h_min, h_max, seed):
    """Pick the locally-tallest crest points and plant pines on them so the
    iconic punctuation lands on visible summits, not random columns."""
    rng = random.Random(seed)
    # Sample local maxima.
    candidates = []
    look = 14
    for i in range(look, len(heights) - look):
        x, y = heights[i]
        if all(y <= heights[i + d][1] for d in range(-look, look + 1)):
            candidates.append(i)
    if not candidates:
        return
    rng.shuffle(candidates)
    for i in candidates[:count]:
        x, y = heights[i]
        ph = rng.randint(h_min, h_max)
        _lone_pine(surf, x, y, ph, ink, accent, rng)


def draw_mountains_sumie_crags(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    night = min(1.0, pal['star_alpha'] / 235.0)
    haze = _mix(_haze(far, near), horizon, 0.30)
    # Dark ink tones: pulled toward near-black, but always tinted by the
    # biome near tone so each phase still tints the ink (warm sunset ink,
    # cool dusk ink, etc.). Daylight ink reads as deep slate, dusk goes
    # near-black.
    ink_far = _shade(_mix(far, (25, 28, 42), 0.55), -10)
    ink_mid = _shade(_mix(near, (18, 20, 30), 0.55), -10)
    ink_near = _shade(_mix(near, (10, 12, 22), 0.65), -10)
    # Accent for the brush tap on pines — leans warm so it's always visible.
    pine_accent = _mix(horizon, (255, 230, 200), 0.6)

    # BACK — gentle ink wash for a hint of distant range. Horizontal haze
    # veils removed: they showed up as coloured bright stripes behind the
    # crag silhouettes. The wash's own alpha ramp keeps the soft fade.
    hb = _crag_ridge(w, ground_y, scroll, 0.07, 90, jag_amp=6, jag_freq=0.5, seed=11)
    _ink_wash_strong(surf, hb, ground_y, ink_far,
                     _mix(ink_far, haze, 0.4),
                     alpha_top=200, fade=1.3,
                     rim_col=_mix(ink_far, horizon, 0.55))

    # MID — angular crags, the hero ink band.
    hm = _crag_ridge(w, ground_y, scroll, 0.16, 130, jag_amp=22, jag_freq=0.7, seed=29)
    _ink_wash_strong(surf, hm, ground_y, ink_mid,
                     _mix(ink_mid, far, 0.25),
                     alpha_top=232, fade=1.4,
                     rim_col=_shade(ink_mid, -22))
    _dry_brush_crest(surf, hm, _shade(ink_mid, -28),
                     density=0.45, max_drip=4, seed=29)
    # Mid pines on the high points.
    _crag_pines(surf, hm, ground_y, count=2,
                ink=_shade(ink_mid, -20), accent=pine_accent,
                h_min=18, h_max=28, seed=29)

    # NEAR — heaviest black silhouette with the most aggressive sawtooth.
    hn = _crag_ridge(w, ground_y, scroll, 0.30, 180, jag_amp=34, jag_freq=0.9, seed=53)
    _ink_wash_strong(surf, hn, ground_y, ink_near,
                     _mix(ink_near, far, 0.25),
                     alpha_top=250, fade=1.5,
                     rim_col=_shade(ink_near, -22))
    _dry_brush_crest(surf, hn, _shade(ink_near, -32),
                     density=0.55, max_drip=6, seed=53)
    # Front pines — bigger, more visible.
    _crag_pines(surf, hn, ground_y, count=3,
                ink=_shade(ink_near, -10), accent=pine_accent,
                h_min=26, h_max=42, seed=53)


# ══════════════════════════════════════════════════════════════════════════
# V14 — Pagoda-Crowned Ridges
# Layered shan-shui washes (true to V4 DNA) crowned with silhouetted
# multi-tiered pagodas planted on the highest summits of the front bands.
# Pagodas are tiny but instantly readable: storybook Chinese scroll feel.
# Presence vs V4: the iconic architectural punctuation gives the eye a
# clear focal anchor on every band; pagoda silhouettes read with weight
# even from the back row, plus all ridge bands run +20% taller / more
# saturated for a bolder overall read.
# ══════════════════════════════════════════════════════════════════════════

def _pagoda(surf, x, base_y, tiers, base_w, color, accent, scale=1.0):
    """A multi-tier pagoda silhouette. Each tier is a rectangular body with
    upturned eave overhangs, narrowing slightly toward the top, capped by a
    spire finial. Scaled up vs first pass so pagodas read as architectural
    weight, not specks; the rim accent runs along the eaves of every tier
    so the iconic upturned silhouette catches the eye at any phase."""
    tier_h = max(5, int(7 * scale))
    eave_lip = max(1, int(3 * scale))
    bw = base_w
    cy = base_y
    # Stone platform removed — a hard horizontal rectangle under each pagoda
    # read as a tiny coloured stripe planted on the ridge. The bottom tier
    # already sits flush on the crest, so the silhouette stays grounded.
    for t in range(tiers):
        tw = max(6, bw - t * 2)
        body = pygame.Rect(x - tw // 2, cy - tier_h, tw, tier_h)
        pygame.draw.rect(surf, color, body)
        # Eave roof: a flatter wedge wider than the body with upturned corners.
        eave_w = tw + max(7, int(9 * scale))
        roof_top = cy - tier_h - max(2, int(3 * scale))
        roof_pts = [
            (x - eave_w // 2, cy - tier_h),
            (x - eave_w // 2 + 3, roof_top),
            (x + eave_w // 2 - 3, roof_top),
            (x + eave_w // 2, cy - tier_h),
        ]
        pygame.draw.polygon(surf, color, roof_pts)
        # Upturned eave corners — the single most recognisable cue. Drawn as
        # short hooks above the eave line so they read against any sky.
        pygame.draw.line(surf, color,
                         (x - eave_w // 2 - 1, cy - tier_h - 1),
                         (x - eave_w // 2 + 1, cy - tier_h - max(3, int(4 * scale))), 1)
        pygame.draw.line(surf, color,
                         (x + eave_w // 2, cy - tier_h - 1),
                         (x + eave_w // 2 - 2, cy - tier_h - max(3, int(4 * scale))), 1)
        # Accent rim along the eave so the architectural silhouette holds
        # against the wash even in distant rows.
        pygame.draw.aaline(surf, accent,
                           (x - eave_w // 2 + 1, roof_top + 1),
                           (x + eave_w // 2 - 1, roof_top + 1))
        cy -= tier_h + eave_lip
    # Tapered finial spire on top, taller than before.
    spire_h = max(5, int(7 * scale))
    pygame.draw.polygon(surf, color, [
        (x - 1, cy), (x + 1, cy), (x, cy - spire_h)])
    # A small accent dot at the spire tip — the calligrapher's punctuation.
    surf.set_at((x, cy - spire_h - 1), accent)


def _summit_pagodas(surf, heights, count, tiers_choices, base_w_choices,
                    color, accent, seed, scale=1.0):
    """Plant pagodas on the locally-tallest crest points."""
    rng = random.Random(seed)
    look = 18
    candidates = []
    for i in range(look, len(heights) - look):
        x, y = heights[i]
        if all(y <= heights[i + d][1] for d in range(-look, look + 1)):
            candidates.append(i)
    if not candidates:
        return
    rng.shuffle(candidates)
    for i in candidates[:count]:
        x, y = heights[i]
        tiers = rng.choice(tiers_choices)
        bw = rng.choice(base_w_choices)
        _pagoda(surf, x, y - 1, tiers, bw, color, accent, scale=scale)


def draw_mountains_pagoda(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    night = min(1.0, pal['star_alpha'] / 235.0)
    haze = _mix(_haze(far, near), horizon, 0.32)

    # V4 lineage: 5-layer wash, but every base_h is taller and every alpha
    # bumped so the ridges hold more visual weight in the frame.
    far_tint = _mix(far, horizon, 0.42)
    specs = [
        (0.05, 124, 140, _mix(far_tint, (235, 238, 248), 0.28), far_tint),
        (0.08, 108, 165, _mix(far_tint, far, 0.62), _mix(far_tint, haze, 0.5)),
        (0.13, 96, 190, _sat(far, 1.20), _mix(far, haze, 0.4)),
        (0.20, 80, 218, _sat(_mix(near, far, 0.4), 1.25), _mix(near, far, 0.5)),
        (0.28, 64, 244, _sat(near, 1.30), _mix(near, far, 0.28)),
    ]
    crest_heights = []
    for k, (speed, base_h, atop, itop, ibot) in enumerate(specs):
        pts, h = _ridge(w, ground_y, scroll, speed, base_h,
                        [(0.011 + k * 0.002, 24 - k * 2, 0.6 + k),
                         (0.030 + k * 0.004, 12, 1.5 - k * 0.3)])
        _ink_wash_strong(surf, h, ground_y, itop, ibot, atop, fade=1.6,
                         rim_col=_shade(_sat(itop, 1.2), -28))
        # Inter-band fog veils removed — they read as coloured horizontal
        # stripes between layers. Each wash's alpha falloff carries the
        # atmospheric depth on its own.
        crest_heights.append(h)

    # Pagodas on the three FRONT bands so they read clearly. Distant pagodas
    # are small silhouettes; near ones are big multi-tier with a rim-light
    # accent so they punch hard off the front wash. Pagoda colour leans
    # near-black so it always reads as architectural shape regardless of
    # the wash tone behind it.
    pag_far = _shade(_sat(_mix(far, near, 0.7), 1.15), -42)
    pag_mid = _shade(_sat(near, 1.20), -46)
    pag_near = _shade(_sat(near, 1.30), -58)
    accent = _mix(horizon, (255, 230, 180), 0.55)
    _summit_pagodas(surf, crest_heights[2], count=2,
                    tiers_choices=(2, 3), base_w_choices=(9, 10, 11),
                    color=pag_far, accent=accent, seed=29, scale=0.85)
    _summit_pagodas(surf, crest_heights[3], count=2,
                    tiers_choices=(3, 4), base_w_choices=(12, 13, 14),
                    color=pag_mid, accent=accent, seed=53, scale=1.05)
    _summit_pagodas(surf, crest_heights[4], count=2,
                    tiers_choices=(4, 5), base_w_choices=(14, 15, 17),
                    color=pag_near, accent=accent, seed=83, scale=1.35)


# ══════════════════════════════════════════════════════════════════════════
# V15 — Neon-Ink Shan-Shui
# Modern reinterpretation: dark ink ridges with electric glow piped along
# every crest. Additive bloom on the ridge edge, hot accent-coloured mist
# veils between bands. By day the glow pulls toward the warm horizon hue
# so it reads as sun-struck rim light; at night it pops as neon cyberpunk
# shan-shui. Direct response to "more presence" — silhouettes go heavy
# and dark, edges go luminous.
# ══════════════════════════════════════════════════════════════════════════

def _neon_crest(surf, heights, ground_y, glow, core, halo_h=10, intensity=1.0):
    """Bloomed neon edge: a soft additive halo above the crest, a hot core
    line right on it. Halo width tapers with distance from the line. Both
    additive so the colour stacks over whatever sky sits behind. ``intensity``
    scales the halo alpha — front bands push past 1 to overdrive the glow so
    the eye reads them as "closest light"."""
    if not heights:
        return
    w = surf.get_width()
    top = min(y for _, y in heights)
    band_top = max(0, top - halo_h)
    band_h = ground_y - band_top
    if band_h <= 0:
        return
    band = pygame.Surface((w, band_h), pygame.SRCALPHA)
    xy = {x: y for x, y in heights}
    peak_alpha = int(220 * intensity)
    for x in range(w):
        ry = xy.get(x)
        if ry is None:
            continue
        local_y = ry - band_top
        for dy in range(-halo_h, 1):
            yy = local_y + dy
            if 0 <= yy < band_h:
                d = abs(dy) / halo_h
                a = int(peak_alpha * (1.0 - d) ** 1.5)
                if a <= 1:
                    continue
                prev = band.get_at((x, yy))
                na = min(240, prev[3] + a)
                band.set_at((x, yy), (glow[0], glow[1], glow[2], na))
    surf.blit(band, (0, band_top), special_flags=pygame.BLEND_RGBA_ADD)
    # Hot core line — exact ridge silhouette in a brighter tone, drawn twice
    # for visible weight on the WASM target (where AA can be subtle).
    pygame.draw.aalines(surf, core, False, heights)
    pygame.draw.lines(surf, core, False, heights, 1)


def _neon_mist(surf, heights, ground_y, color, top_alpha, depth):
    """Coloured fog veil keyed to the neon accent — sits in the gap above
    each ridge so the spaces between bands also carry the accent hue."""
    if not heights:
        return
    top = min(y for _, y in heights)
    band = pygame.Surface((surf.get_width(), depth), pygame.SRCALPHA)
    for i in range(depth):
        a = int(top_alpha * (1.0 - i / depth) ** 1.3)
        if a <= 0:
            continue
        pygame.draw.line(band, (color[0], color[1], color[2], a),
                         (0, i), (surf.get_width(), i))
    surf.blit(band, (0, max(0, top - depth // 2)),
              special_flags=pygame.BLEND_RGBA_ADD)


def draw_mountains_neonink(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    accent = pal['stone_accent']
    foliage_accent = pal['foliage_accent']
    night = min(1.0, pal['star_alpha'] / 235.0)
    # Dark ink body — push hard toward near-black with only a sliver of the
    # biome tone left in, so silhouettes read with weight at every phase
    # (previous tuning let day silhouettes wash into the haze).
    ink_far = _shade(_mix(far, (12, 14, 28), 0.75), -16)
    ink_mid = _shade(_mix(near, (6, 8, 18), 0.78), -18)
    ink_near = _shade(_mix(near, (2, 3, 12), 0.85), -22)
    # Neon glow hues: electric magenta + cyan. Day tint pulls just enough
    # toward horizon warm to read as sun-struck rim; night pushes hard into
    # neon. Saturation cranked so the edge always pops against a dark wash.
    magenta = (255, 90, 200)
    cyan = (80, 230, 255)
    neon = _sat(_mix(_mix(accent, horizon, 0.4), magenta, 0.45 + 0.45 * night), 1.7)
    neon_alt = _sat(_mix(foliage_accent, cyan, 0.45 + 0.45 * night), 1.7)
    core = _mix(neon, (255, 255, 255), 0.6)

    # BACK — distant neon mist plus a soft ridge silhouette. Heavier wash
    # so the band reads as solid dark, not a low-contrast tint.
    hb = _ridge(w, ground_y, scroll, 0.07, 106,
                [(0.011, 24, 0.5), (0.028, 11, 1.8)])[1]
    _ink_wash_strong(surf, hb, ground_y, ink_far,
                     _mix(ink_far, ink_mid, 0.4), alpha_top=232, fade=1.4)
    _neon_crest(surf, hb, ground_y, neon, core, halo_h=10, intensity=0.7)
    _neon_mist(surf, hb, ground_y, neon, 60, 28)

    # MID — heavier ridge, brighter glow with the secondary neon hue.
    hm = _ridge(w, ground_y, scroll, 0.16, 90,
                [(0.014, 30, 1.3), (0.032, 14, 0.4)])[1]
    _ink_wash_strong(surf, hm, ground_y, ink_mid,
                     _mix(ink_mid, ink_near, 0.4), alpha_top=246, fade=1.5)
    _neon_crest(surf, hm, ground_y, neon_alt,
                _mix(neon_alt, (255, 255, 255), 0.55),
                halo_h=14, intensity=0.95)
    _neon_mist(surf, hm, ground_y, neon_alt, 70, 24)

    # NEAR — heaviest dark silhouette, hottest neon edge — the band that
    # truly sells the "modern shan-shui" pitch. Overdrive intensity past 1
    # so the front edge reads as the brightest light source in the frame.
    hn = _ridge(w, ground_y, scroll, 0.30, 70,
                [(0.019, 26, 0.4), (0.045, 12, 1.9)])[1]
    _ink_wash_strong(surf, hn, ground_y, ink_near,
                     _shade(ink_near, -10), alpha_top=255, fade=1.6)
    _neon_crest(surf, hn, ground_y, neon,
                _mix(neon, (255, 255, 255), 0.65),
                halo_h=18, intensity=1.25)


# ── phase plumbing ────────────────────────────────────────────────────────
# Several concepts need palette keys beyond mtn_far/mtn_near (foliage, horizon,
# accents). The drop-in signature can't carry the phase, so the harness sets
# this module-level phase right before each call. In the live game the same
# extra keys would be read from the already-known palette dict.

_PHASE = 0.02


def set_phase(p: float) -> None:
    global _PHASE
    _PHASE = p % 1.0


# ── dispatcher ───────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_mountains_v1,
    2: draw_mountains_v2,
    4: draw_mountains_v4,
    6: draw_mountains_islands,
    7: draw_mountains_crystal,
    8: draw_mountains_biolum,
    9: draw_mountains_aurora,
    10: draw_mountains_skyline,
    11: draw_mountains_karst,
    12: draw_mountains_cloudsea,
    13: draw_mountains_sumie_crags,
    14: draw_mountains_pagoda,
    15: draw_mountains_neonink,
}

VARIANT_NAMES = {
    1: "Danxia Rainbow Strata (refined)",
    2: "Wind-Sculpted Dunes (refined)",
    4: "Shan-Shui Ink Ridges (refined) — R2 favourite",
    6: "Floating Sky Islands",
    7: "Crystal Geode Spires",
    8: "Bioluminescent Canyon",
    9: "Aurora Ridgelines",
    10: "Distant Fantasy Skyline",
    11: "Karst Pinnacles (Guilin)",
    12: "Cloud Sea Peaks (Yúnhǎi)",
    13: "Sumi-e Bold Crags + Lone Pines",
    14: "Pagoda-Crowned Ridges",
    15: "Neon-Ink Shan-Shui",
}

# V1 leads as the returning round-1 favourite, brought up to round-2 fidelity.
ROW_ORDER = [1, 2, 4, 6, 7, 8, 9, 10]

# Round-3 sheet — V4 reference on top + 5 new shan-shui derivatives.
ROW_ORDER_SHANSHUI = [4, 11, 12, 13, 14, 15]
