"""Alive-world expansions of the four keeper backgrounds (V4 / V12 / V13 / V14).

Brief from the user: the four keepers all read well visually, but each variant
produces near-identical output every frame — the world doesn't feel like it's
changing or alive as the player scrolls. Solution: keep the keeper DNA intact,
then layer a rich, per-variant element library on top, scattered at varied
sizes with irregular spacing so each "scene" of the world looks distinct.

Element libraries per variant:

  V4  Shan-Shui Ink Ridges
        – pagodas (2/3/5 tier, small + medium)
        – lone bent pines clinging to ledges
        – sailing-junk silhouettes in misty valleys
        – calligraphic V-bird scribbles in flight
        – brushy waterfall strokes off the highest crags

  V12 Cloud Sea Peaks
        – varied peak silhouettes (lone, twin, triple)
        – tiny pavilion / temple cluster on a peak crown
        – V-flocks of cranes between peaks
        – ribbon waterfalls vanishing into cloud

  V13 Sumi-e Bold Crags + Lone Pines
        – three pine shapes (bonsai stubby / twisted medium / fan-canopy tall)
        – scholar-rock outcrops
        – hidden mini-pagoda silhouettes on low crags
        – calligraphic bird-scribble flights

  V14 Pagoda-Crowned Ridges (user explicitly named this one)
        – pagodas at 3 / 5 / 7 tiers, scale 0.7×..1.6×
        – twisted pines and bamboo clumps on the ridges
        – weeping willows on lower shoulders
        – stone lanterns flanking pagodas
        – occasional hanging banners

Variation mechanics: every element-placement call seeds a ``random.Random`` off
``int(scroll) ^ layer_const ^ section_index``, so the same scroll position
always paints the same scene (no flicker per frame) while moving 200 px down
the world swaps the entire element layout out for a new one. Sections are
variable-width on each layer so element clusters are uneven — believable.

Drop-in: same ``def variant(surf, scroll, ground_y, w, far_color, near_color)``
signature as the original keepers; all colours derive from the biome palette.
"""
from __future__ import annotations

import math
import random

import pygame

from game import biome as _biome

# Re-use the underlying primitives from the keeper module so the silhouettes,
# washes, and crest strokes match what the user already approved.
from mountain_variants_r2 import (
    _clamp, _mix, _shade, _sat, _haze, _back_color, _ridge, _aa_crest,
    _haze_band, _gradient_fill, _ink_wash_strong, _dry_brush_crest,
    _crag_ridge, _peak_silhouette, _cloud_sea_band, set_phase,
)
import mountain_variants_r2 as _keepers


# ── element library ──────────────────────────────────────────────────────────

def _pagoda(surf, x, base_y, tiers, base_w, color, accent, scale=1.0):
    """Multi-tier pagoda. Tiers narrow upward, each capped by an upturned eave
    and finishing in a finial spire. Reads as architectural silhouette at any
    scale; tier count and base width drive the read so a 3-tier 8 px-wide
    "village" pagoda sits naturally beside a 7-tier 18 px-wide "temple" one."""
    tier_h = max(4, int(7 * scale))
    eave_lip = max(1, int(3 * scale))
    bw = base_w
    cy = base_y
    for t in range(tiers):
        tw = max(5, bw - t * 2)
        body = pygame.Rect(x - tw // 2, cy - tier_h, tw, tier_h)
        pygame.draw.rect(surf, color, body)
        eave_w = tw + max(6, int(8 * scale))
        roof_top = cy - tier_h - max(2, int(3 * scale))
        roof_pts = [
            (x - eave_w // 2, cy - tier_h),
            (x - eave_w // 2 + 2, roof_top),
            (x + eave_w // 2 - 2, roof_top),
            (x + eave_w // 2, cy - tier_h),
        ]
        pygame.draw.polygon(surf, color, roof_pts)
        pygame.draw.line(surf, color,
                         (x - eave_w // 2 - 1, cy - tier_h - 1),
                         (x - eave_w // 2 + 1, cy - tier_h - max(3, int(4 * scale))), 1)
        pygame.draw.line(surf, color,
                         (x + eave_w // 2, cy - tier_h - 1),
                         (x + eave_w // 2 - 2, cy - tier_h - max(3, int(4 * scale))), 1)
        pygame.draw.aaline(surf, accent,
                           (x - eave_w // 2 + 1, roof_top + 1),
                           (x + eave_w // 2 - 1, roof_top + 1))
        cy -= tier_h + eave_lip
    spire_h = max(4, int(6 * scale))
    pygame.draw.polygon(surf, color,
                        [(x - 1, cy), (x + 1, cy), (x, cy - spire_h)])
    surf.set_at((x, cy - spire_h - 1), accent)


def _bent_pine(surf, x, y_base, h, ink, accent, lean=1):
    """Huangshan-style twisted pine: bent trunk + two flat canopy puffs.
    Compact, silhouette-only, reads as iconic East-Asian punctuation."""
    if y_base <= h + 4:
        return
    seg = max(3, h // 3)
    p0 = (x, y_base)
    p1 = (x + lean * 2, y_base - seg)
    p2 = (x + lean * 4, y_base - seg * 2)
    p3 = (x + lean * 2, y_base - h)
    pygame.draw.lines(surf, ink, False, [p0, p1, p2, p3], 2)
    cw1 = max(7, int(h * 0.75))
    ch1 = max(3, h // 6)
    cw2 = max(5, int(h * 0.5))
    ch2 = max(2, h // 8)
    pygame.draw.ellipse(surf, ink,
                        pygame.Rect(p3[0] - cw1 // 2, p3[1] - ch1 - 1, cw1, ch1 * 2))
    pygame.draw.ellipse(surf, ink,
                        pygame.Rect(p3[0] - cw2 // 2, p3[1] - ch2 - h // 4, cw2, ch2 * 2))
    surf.set_at((p3[0], p3[1] - ch1 - 2), accent)


def _bonsai_pine(surf, x, y_base, h, ink, accent):
    """Squat bonsai-style pine: stout trunk + one wide flat canopy. Sells the
    "small wind-stunted tree" read against a low scholar rock."""
    if y_base <= h + 4:
        return
    p0 = (x, y_base)
    p1 = (x + 2, y_base - h // 2)
    p2 = (x - 1, y_base - h)
    pygame.draw.lines(surf, ink, False, [p0, p1, p2], 2)
    cw = max(9, int(h * 1.1))
    ch = max(2, h // 5)
    pygame.draw.ellipse(surf, ink,
                        pygame.Rect(p2[0] - cw // 2, p2[1] - ch, cw, ch * 2))
    surf.set_at((p2[0], p2[1] - ch - 1), accent)


def _fan_pine(surf, x, y_base, h, ink, accent):
    """Tall fan-canopy pine: straight slim trunk + 3 stacked horizontal layers
    fanning outward. Reads as the dominant pine on a high ridge."""
    if y_base <= h + 4:
        return
    pygame.draw.line(surf, ink, (x, y_base), (x, y_base - h), 2)
    top_y = y_base - h
    layers = 3
    for i in range(layers):
        ly = top_y + i * max(3, h // 6)
        lw = max(8, int(h * (0.55 + i * 0.15)))
        lh = max(2, h // 9)
        pygame.draw.ellipse(surf, ink,
                            pygame.Rect(x - lw // 2, ly - lh, lw, lh * 2))
    surf.set_at((x, top_y - 1), accent)


def _scholar_rock(surf, x, y_base, w_, h, color, rim):
    """Squat irregular outcrop with one or two flaring tops — a 'scholar rock'
    silhouette to break up empty mid-ridge stretches."""
    pts = [
        (x - w_ // 2, y_base),
        (x - w_ // 2 + 1, y_base - h // 2),
        (x - 2, y_base - h),
        (x + 2, y_base - int(h * 0.85)),
        (x + w_ // 2 - 1, y_base - h // 2),
        (x + w_ // 2, y_base),
    ]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.aalines(surf, rim, False, pts)


def _willow(surf, x, y_base, h, ink):
    """Weeping willow whisk: a tiny trunk topped by a few drooping fronds.
    The fronds are short downward strokes fanning from a centre point — reads
    as a delicate near-ground tree silhouette."""
    if y_base <= h + 4:
        return
    pygame.draw.line(surf, ink, (x, y_base), (x, y_base - h), 1)
    top_y = y_base - h
    for i in range(7):
        ang = -math.pi / 2 + (i - 3) * 0.32
        fx = x + math.cos(ang) * (h // 2 + 1)
        fy = top_y + 1
        pygame.draw.aaline(surf, ink, (x, top_y), (fx, fy + h // 2 - 1))


def _bamboo(surf, x, y_base, h, ink, accent):
    """Bamboo clump: 3 thin vertical stalks of varied heights with small
    paired leaves at the top. Slim, distinct from pines."""
    for k in range(3):
        sx = x + (k - 1) * 3
        sh = int(h * (0.7 + 0.3 * (k % 2 == 1)))
        pygame.draw.line(surf, ink, (sx, y_base), (sx, y_base - sh), 1)
        # Two paired leaves near the top — short diagonal flicks.
        ty = y_base - sh
        pygame.draw.aaline(surf, ink, (sx, ty + 2), (sx - 3, ty - 1))
        pygame.draw.aaline(surf, ink, (sx, ty + 2), (sx + 3, ty - 1))
    surf.set_at((x, y_base - h - 1), accent)


def _stone_lantern(surf, x, y_base, ink, accent):
    """Tiny ishi-doro stone lantern: square base + pillar + lit head with a
    pointed cap. Three pixels tall for body, the lit window is the accent."""
    pygame.draw.rect(surf, ink, pygame.Rect(x - 2, y_base - 2, 5, 2))
    pygame.draw.rect(surf, ink, pygame.Rect(x - 1, y_base - 6, 3, 4))
    pygame.draw.rect(surf, ink, pygame.Rect(x - 2, y_base - 9, 5, 3))
    surf.set_at((x, y_base - 8), accent)
    pygame.draw.polygon(surf, ink, [(x - 3, y_base - 9),
                                    (x + 3, y_base - 9),
                                    (x, y_base - 12)])


def _calligraphic_bird(surf, x, y, scale, ink):
    """A V-shaped bird scribble — two short brush ticks. The most economical
    way to read 'distant flying bird' in shan-shui shorthand."""
    s = max(2, int(scale))
    pygame.draw.aaline(surf, ink, (x - s, y + s // 2), (x, y))
    pygame.draw.aaline(surf, ink, (x, y), (x + s, y + s // 2))


def _bird_flight(surf, cx, cy, count, ink, rng):
    """A loose flock — birds scattered around (cx, cy) with random scale and
    slight vertical staggering so the flight reads as moving forward."""
    for _ in range(count):
        dx = rng.randint(-22, 22)
        dy = rng.randint(-8, 8)
        s = rng.randint(2, 4)
        _calligraphic_bird(surf, cx + dx, cy + dy, s, ink)


def _waterfall(surf, x, top_y, fall_h, ink, accent):
    """Brushy waterfall stroke: a tapered narrow vertical band of slightly
    desaturated bright ink dropping from a crest, ending in a small splash
    accent. Stays a silhouette — no per-droplet detail."""
    if fall_h < 8:
        return
    for i in range(fall_h):
        t = i / fall_h
        width = max(1, int(3 - t * 2))
        a = int(220 * (1.0 - t * 0.4))
        col = (accent[0], accent[1], accent[2], a)
        for dx in range(-width, width + 1):
            yy = top_y + i
            xx = x + dx + int(math.sin(i * 0.4) * 0.6)
            if 0 <= xx < surf.get_width() and 0 <= yy < surf.get_height():
                # Soft additive accumulation so it reads as luminous water.
                prev = surf.get_at((xx, yy))
                surf.set_at((xx, yy), (
                    _clamp(prev[0] + col[0] * a // 1024),
                    _clamp(prev[1] + col[1] * a // 1024),
                    _clamp(prev[2] + col[2] * a // 1024)))
    # Splash basin: a small bright ellipse at the foot.
    splash_y = top_y + fall_h
    pygame.draw.ellipse(surf, accent,
                        pygame.Rect(x - 3, splash_y - 1, 7, 3))


def _junk_boat(surf, x, y, scale, ink, accent):
    """A tiny Chinese sailing junk: shallow curved hull + slanted sail. Sits
    in a misty valley to ground the scale of the mountains around it."""
    hw = max(5, int(7 * scale))
    hh = max(2, int(2 * scale))
    hull = [
        (x - hw, y), (x - hw + 1, y + hh),
        (x + hw - 1, y + hh), (x + hw, y),
    ]
    pygame.draw.polygon(surf, ink, hull)
    mast_h = max(7, int(10 * scale))
    pygame.draw.line(surf, ink, (x, y), (x, y - mast_h), 1)
    # Slanted batten sail.
    sail = [
        (x, y - mast_h),
        (x + max(4, int(6 * scale)), y - mast_h + 2),
        (x + max(3, int(5 * scale)), y - 1),
        (x, y - 2),
    ]
    pygame.draw.polygon(surf, ink, sail)
    surf.set_at((x, y - mast_h - 1), accent)


def _pavilion(surf, x, y_base, color, accent, scale=1.0):
    """A small one-tier pavilion / temple: wider eave than a pagoda, no spire.
    Sits on a hilltop or high ridge as architectural punctuation distinct
    from a tall pagoda."""
    bw = max(7, int(9 * scale))
    bh = max(3, int(4 * scale))
    pygame.draw.rect(surf, color,
                     pygame.Rect(x - bw // 2, y_base - bh, bw, bh))
    eave_w = bw + max(6, int(8 * scale))
    eave_y = y_base - bh
    roof_top = eave_y - max(3, int(5 * scale))
    pygame.draw.polygon(surf, color, [
        (x - eave_w // 2, eave_y),
        (x - eave_w // 2 + 2, roof_top),
        (x + eave_w // 2 - 2, roof_top),
        (x + eave_w // 2, eave_y),
    ])
    pygame.draw.line(surf, color, (x - eave_w // 2 - 1, eave_y - 1),
                     (x - eave_w // 2 + 1, eave_y - max(3, int(4 * scale))), 1)
    pygame.draw.line(surf, color, (x + eave_w // 2, eave_y - 1),
                     (x + eave_w // 2 - 2, eave_y - max(3, int(4 * scale))), 1)
    pygame.draw.aaline(surf, accent,
                       (x - eave_w // 2 + 1, roof_top + 1),
                       (x + eave_w // 2 - 1, roof_top + 1))


def _stone_arch(surf, x, y_base, span, ink, accent):
    """A small humpback stone bridge: arc + two end blocks. Spans a low
    saddle between two crags — adds the human-touch motif of shan-shui."""
    rise = max(4, span // 3)
    rect = pygame.Rect(x - span // 2, y_base - rise, span, rise * 2)
    pygame.draw.arc(surf, ink, rect, 0, math.pi, 2)
    # End piers.
    pygame.draw.rect(surf, ink, pygame.Rect(x - span // 2 - 1, y_base - 2, 3, 3))
    pygame.draw.rect(surf, ink, pygame.Rect(x + span // 2 - 1, y_base - 2, 3, 3))
    surf.set_at((x, y_base - rise - 1), accent)


def _hanging_banner(surf, x, top_y, length, color):
    """A vertical hanging cloth banner — a tall thin coloured rectangle with
    a tassel at the bottom. Marks villages/shrines on a ridge crown."""
    rect = pygame.Rect(x - 1, top_y, 3, length)
    pygame.draw.rect(surf, color, rect)
    # Tassel — a single pixel tail.
    surf.set_at((x, top_y + length), color)
    surf.set_at((x, top_y + length + 1), color)


# ── placement helpers ────────────────────────────────────────────────────────

def _local_peaks(heights, look=14):
    """Return indices of local maxima (highest crest points) so element
    placement lands on visible summits, not random pixels."""
    out = []
    for i in range(look, len(heights) - look):
        x, y = heights[i]
        if all(y <= heights[i + d][1] for d in range(-look, look + 1)):
            out.append(i)
    return out


def _local_valleys(heights, look=14):
    """Inverse of _local_peaks — for placing boats, willows in low spots."""
    out = []
    for i in range(look, len(heights) - look):
        x, y = heights[i]
        if all(y >= heights[i + d][1] for d in range(-look, look + 1)):
            out.append(i)
    return out


def _ledges(heights, look=8):
    """Find ledge points: spots where the slope flattens briefly. Used to
    park pines and lanterns mid-face instead of always on the very crest."""
    out = []
    for i in range(look, len(heights) - look):
        a = heights[i - look][1]
        c = heights[i + look][1]
        b = heights[i][1]
        if abs(a - c) < 3 and b <= a + 1 and b <= c + 1:
            # Reject the global crest — only flat shoulders count.
            out.append(i)
    return out


def _seed_for(scroll, layer_const):
    """Deterministic per-scroll-bucket seed. Bucket size 1px so the variation
    re-rolls smoothly as the world moves; layer_const keeps each band's RNG
    independent so the three layers aren't lockstep."""
    return (int(scroll) ^ layer_const) & 0xFFFFFFFF


# ══════════════════════════════════════════════════════════════════════════
# V4 — Shan-Shui Ink Ridges (ALIVE)
# Inherits the 5-layer ink-wash silhouette stack from the keeper module,
# then scatters pagodas, lone pines, sailing junks, calligraphic birds, and
# the occasional waterfall stroke. Variation is keyed off scroll so the same
# section always paints the same scene; clusters/gaps are uneven by design.
# ══════════════════════════════════════════════════════════════════════════

def draw_mountains_v4(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_keepers._PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    haze = _mix(_haze(far, near), horizon, 0.35)
    night = min(1.0, pal['star_alpha'] / 235.0)
    # Element ink tones: leaning darker for silhouette weight against the wash.
    ink_far = _shade(_sat(_mix(far, near, 0.5), 1.1), -38)
    ink_mid = _shade(_sat(near, 1.15), -42)
    ink_near = _shade(_sat(near, 1.25), -54)
    accent = _mix(horizon, (255, 230, 180), 0.55)
    # Waterfall reads as bright mist regardless of phase — pulled toward pale
    # cool tone so the brush stroke shines off the dark ridge.
    fall_col = _mix((240, 248, 255), horizon, 0.25)

    far_tint = _mix(far, horizon, 0.45)
    specs = [
        (0.05, 104, 120, _mix(far_tint, (235, 238, 248), 0.30), far_tint),
        (0.08, 92, 145, _mix(far_tint, far, 0.6), _mix(far_tint, haze, 0.5)),
        (0.13, 80, 170, _sat(far, 1.15), _mix(far, haze, 0.45)),
        (0.20, 66, 200, _sat(_mix(near, far, 0.4), 1.2), _mix(near, far, 0.5)),
        (0.28, 50, 230, _sat(near, 1.25), _mix(near, far, 0.3)),
    ]
    crest_heights = []
    for k, (speed, base_h, atop, itop, ibot) in enumerate(specs):
        pts, h = _ridge(w, ground_y, scroll, speed, base_h,
                        [(0.011 + k * 0.002, 22 - k * 2, 0.6 + k),
                         (0.030 + k * 0.004, 10, 1.5 - k * 0.3)])
        _ink_wash_strong(surf, h, ground_y, itop, ibot, atop, fade=1.6,
                         rim_col=_shade(_sat(itop, 1.2), -28))
        crest_heights.append(h)

    # ── element scatter, mid-front layers only so distant rows stay quiet ──
    # Per-layer section-based scatter: split the row into 3–5 sections of
    # uneven width, drop 0–2 elements per section with random size + offset.
    def scatter(layer_idx, ink, count_range, types, layer_seed):
        h = crest_heights[layer_idx]
        rng = random.Random(_seed_for(scroll, layer_seed))
        # Section boundaries: uneven so cluster/gap rhythm doesn't repeat.
        n_sections = rng.randint(3, 5)
        cuts = sorted(rng.sample(range(40, w - 40), n_sections - 1))
        bounds = [0] + cuts + [w]
        peaks = _local_peaks(h, look=12)
        valleys = _local_valleys(h, look=10)
        ledges = _ledges(h, look=8)
        peak_xy = {h[i][0]: i for i in peaks}
        valley_xy = {h[i][0]: i for i in valleys}
        ledge_xy = {h[i][0]: i for i in ledges}
        for s in range(n_sections):
            lo, hi = bounds[s], bounds[s + 1]
            n = rng.randint(*count_range)
            for _ in range(n):
                t = rng.choice(types)
                # Pick anchor according to element type.
                if t in ('pagoda', 'pine_bent', 'pine_fan', 'birds'):
                    candidates = [i for x, i in peak_xy.items() if lo <= x <= hi]
                    if not candidates and ledge_xy:
                        candidates = [i for x, i in ledge_xy.items() if lo <= x <= hi]
                elif t in ('junk', 'willow'):
                    candidates = [i for x, i in valley_xy.items() if lo <= x <= hi]
                else:
                    candidates = [i for x, i in ledge_xy.items() if lo <= x <= hi]
                if not candidates:
                    # Fallback: any crest column in the section.
                    candidates = [i for i, (x, _) in enumerate(h)
                                  if lo <= x <= hi]
                if not candidates:
                    continue
                idx = rng.choice(candidates)
                cx, cy = h[idx]
                if t == 'pagoda':
                    tiers = rng.choice((2, 3, 3, 5))
                    bw = rng.randint(7, 13)
                    sc = rng.uniform(0.7, 1.15)
                    _pagoda(surf, cx, cy - 1, tiers, bw, ink, accent, sc)
                elif t == 'pine_bent':
                    ph = rng.randint(14, 28)
                    _bent_pine(surf, cx, cy - 1, ph, ink, accent,
                               lean=rng.choice((-1, 1)))
                elif t == 'pine_fan':
                    ph = rng.randint(22, 36)
                    _fan_pine(surf, cx, cy - 1, ph, ink, accent)
                elif t == 'birds':
                    by = cy - rng.randint(18, 60)
                    n_b = rng.randint(2, 5)
                    _bird_flight(surf, cx, by, n_b, ink, rng)
                elif t == 'junk':
                    # Boat sits in the valley at the local ridge low.
                    _junk_boat(surf, cx, cy + rng.randint(0, 6),
                               rng.uniform(0.8, 1.3), ink, accent)
                elif t == 'willow':
                    _willow(surf, cx, cy, rng.randint(8, 14), ink)
                elif t == 'waterfall':
                    # Drop from this crest to the next ridge below if it exists.
                    nxt = crest_heights[min(layer_idx + 1, len(crest_heights) - 1)]
                    if nxt is h:
                        continue
                    foot = nxt[min(cx, len(nxt) - 1)][1]
                    fall_h = max(8, foot - cy - 2)
                    _waterfall(surf, cx, cy + 1, fall_h, ink, fall_col)

    # Far band — sparse pagodas + occasional bird flock + sail in the misty valley.
    scatter(2, ink_far, (1, 2),
            ['pagoda', 'pagoda', 'birds', 'junk', 'pine_bent'], 0xA11CE)
    # Mid band — more variety, includes waterfall + willow.
    scatter(3, ink_mid, (1, 3),
            ['pagoda', 'pine_bent', 'pine_fan', 'birds', 'willow',
             'waterfall', 'junk'], 0xC0FFEE)
    # Near band — biggest silhouettes, more pines than architecture.
    scatter(4, ink_near, (2, 3),
            ['pine_bent', 'pine_bent', 'pine_fan', 'pagoda',
             'pagoda', 'waterfall'], 0xBEEF1E)


# ══════════════════════════════════════════════════════════════════════════
# V12 — Cloud Sea Peaks (ALIVE)
# Same Huangshan peak-island silhouette stack from the keeper, but each
# section now picks a peak archetype (lone / twin / triple) plus scatters
# crane V-flocks between peaks, hilltop pavilions, and one or two ribbon
# waterfalls vanishing into the cloud sea.
# ══════════════════════════════════════════════════════════════════════════

def _peak_silhouette_alive(w, ground_y, scroll, speed, peak_y, peak_spacing,
                           peak_h_min, peak_h_max, base_anchor, jag, seed,
                           layout_seed):
    """Variant of the keeper's peak silhouette that picks 'lone / twin / triple'
    archetypes per section so the peak chain itself reads with different
    silhouettes from scene to scene."""
    phase = scroll * speed
    heights = []
    k0 = int(phase // peak_spacing) - 2
    peaks = []
    rng_layout = random.Random(layout_seed)
    for k in range(k0, k0 + int(w / peak_spacing) + 4):
        rng = random.Random((k * 2654435761 ^ seed ^ layout_seed) & 0xFFFFFFFF)
        cx = int(k * peak_spacing - phase) + rng.randint(-12, 12)
        archetype = rng.choice(('lone', 'lone', 'twin', 'triple', 'broad'))
        if archetype == 'lone':
            ph = rng.randint(peak_h_min, peak_h_max)
            half = int(peak_spacing * rng.uniform(0.50, 0.70))
            skew = rng.uniform(-0.18, 0.18)
            peaks.append((cx, ph, half, skew, rng))
        elif archetype == 'twin':
            for off in (-peak_spacing // 4, peak_spacing // 4):
                ph = rng.randint(peak_h_min - 30, peak_h_max - 20)
                half = int(peak_spacing * rng.uniform(0.30, 0.42))
                peaks.append((cx + off, ph, half, rng.uniform(-0.18, 0.18), rng))
        elif archetype == 'triple':
            for off, sc in ((-peak_spacing // 3, 0.8),
                            (0, 1.0), (peak_spacing // 3, 0.7)):
                ph = int(rng.randint(peak_h_min - 20, peak_h_max) * sc)
                half = int(peak_spacing * rng.uniform(0.26, 0.36))
                peaks.append((cx + off, ph, half, rng.uniform(-0.18, 0.18), rng))
        else:  # 'broad' — single broad-shouldered peak
            ph = rng.randint(peak_h_min, peak_h_max)
            half = int(peak_spacing * rng.uniform(0.80, 1.05))
            peaks.append((cx, ph, half, rng.uniform(-0.10, 0.10), rng))
    for x in range(w + 1):
        best_y = base_anchor
        for cx, ph, half, skew, rng in peaks:
            if cx - half <= x <= cx + half:
                d = (x - cx) / max(1, half)
                if d < 0:
                    f = 1.0 - abs(d) ** (1.1 + skew)
                else:
                    f = 1.0 - abs(d) ** (1.1 - skew)
                f += math.sin(x * 0.45 + cx) * jag / max(1, ph)
                yy = peak_y - int(ph * max(0.0, f))
                if yy < best_y:
                    best_y = yy
        heights.append((x, best_y))
    return heights


def draw_mountains_v12(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_keepers._PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    night = min(1.0, pal['star_alpha'] / 235.0)
    haze = _mix(_haze(far, near), horizon, 0.35)
    cloud_hi = _shade(_mix((255, 250, 235), horizon, 0.45), int(-60 * night))
    cloud_base = _shade(_mix((220, 224, 235), haze, 0.55), int(-65 * night))
    accent = _mix(horizon, (255, 230, 180), 0.55)
    fall_col = _mix((240, 248, 255), horizon, 0.20)

    far_tint = _mix(far, horizon, 0.40)
    base_b = ground_y - 80
    peak_y_b = ground_y - 90
    hb = _peak_silhouette_alive(w, ground_y, scroll, 0.07,
                                peak_y=peak_y_b, peak_spacing=86,
                                peak_h_min=44, peak_h_max=86,
                                base_anchor=base_b, jag=1.5,
                                seed=11, layout_seed=_seed_for(scroll, 0xB1))
    _ink_wash_strong(surf, hb, base_b, _sat(far_tint, 1.0),
                     _mix(far_tint, haze, 0.6), alpha_top=190, fade=1.4,
                     rim_col=_mix(far_tint, horizon, 0.55))
    _cloud_sea_band(surf, w, ground_y - 132, 56, cloud_base, cloud_hi,
                    density=170, seed=17)

    mid_tint = _mix(near, far, 0.35)
    base_m = ground_y - 30
    peak_y_m = ground_y - 40
    hm = _peak_silhouette_alive(w, ground_y, scroll, 0.16,
                                peak_y=peak_y_m, peak_spacing=108,
                                peak_h_min=150, peak_h_max=220,
                                base_anchor=base_m, jag=3.2,
                                seed=29, layout_seed=_seed_for(scroll, 0xB2))
    _ink_wash_strong(surf, hm, base_m, _sat(mid_tint, 1.20),
                     _mix(mid_tint, haze, 0.30), alpha_top=234, fade=1.55,
                     rim_col=_shade(_sat(mid_tint, 1.35), -32))
    _dry_brush_crest(surf, hm, _shade(_sat(mid_tint, 1.4), -48),
                     density=0.36, max_drip=4, seed=29)

    # Crane V-flocks + small pavilions on mid-band peaks before the front
    # cloud band swallows the lower silhouette.
    ink_mid_elem = _shade(_sat(mid_tint, 1.4), -52)
    rng = random.Random(_seed_for(scroll, 0xC4A4E))
    peaks_mid = _local_peaks(hm, look=18)
    for i in peaks_mid:
        if rng.random() < 0.4:
            # Pavilion on this peak.
            cx, cy = hm[i]
            _pavilion(surf, cx, cy - 1, ink_mid_elem, accent,
                      scale=rng.uniform(0.85, 1.15))
    # Crane flocks scatter between peaks at high altitude — 1 to 3 flocks.
    for _ in range(rng.randint(1, 3)):
        fx = rng.randint(30, w - 30)
        fy = ground_y - rng.randint(140, 220)
        _bird_flight(surf, fx, fy, rng.randint(3, 6), ink_mid_elem, rng)

    _cloud_sea_band(surf, w, ground_y - 76, 50, cloud_base, cloud_hi,
                    density=210, seed=41)

    near_ink = _sat(near, 1.25)
    base_n = ground_y + 6
    peak_y_n = ground_y
    hn = _peak_silhouette_alive(w, ground_y, scroll, 0.30,
                                peak_y=peak_y_n, peak_spacing=148,
                                peak_h_min=240, peak_h_max=320,
                                base_anchor=base_n, jag=3.8,
                                seed=53, layout_seed=_seed_for(scroll, 0xB3))
    _ink_wash_strong(surf, hn, base_n, near_ink,
                     _mix(near_ink, far, 0.40), alpha_top=252, fade=1.55,
                     rim_col=_shade(_sat(near_ink, 1.35), -40))
    _dry_brush_crest(surf, hn, _shade(_sat(near_ink, 1.4), -56),
                     density=0.48, max_drip=6, seed=53)

    # Front-band: occasional waterfall ribbon vanishing into the front cloud
    # sea. Drawn before the cloud band so the cloud covers the splash foot.
    ink_near_elem = _shade(_sat(near_ink, 1.45), -62)
    rng2 = random.Random(_seed_for(scroll, 0xFA11))
    peaks_n = _local_peaks(hn, look=22)
    for i in peaks_n:
        if rng2.random() < 0.35:
            cx, cy = hn[i]
            # Pagoda on tallest near-peak.
            tiers = rng2.choice((3, 5))
            _pagoda(surf, cx, cy - 1, tiers, rng2.randint(11, 14),
                    ink_near_elem, accent, scale=rng2.uniform(0.9, 1.2))
    for i in peaks_n[:rng2.randint(1, 2)]:
        cx, cy = hn[i]
        fall_h = (ground_y - 28) - cy
        if fall_h > 12:
            _waterfall(surf, cx + rng2.randint(-4, 4), cy + 2,
                       fall_h, ink_near_elem, fall_col)

    _cloud_sea_band(surf, w, ground_y - 34, 36, cloud_base, cloud_hi,
                    density=220, seed=73)


# ══════════════════════════════════════════════════════════════════════════
# V13 — Sumi-e Bold Crags + Lone Pines (ALIVE)
# Same heavy ink crag silhouettes from the keeper, now with a three-shape
# pine vocabulary (bonsai / twisted / fan), scholar-rock outcrops between
# peaks, hidden mini-pagodas on low crags, and calligraphic bird scribbles.
# ══════════════════════════════════════════════════════════════════════════

def draw_mountains_v13(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_keepers._PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    night = min(1.0, pal['star_alpha'] / 235.0)
    haze = _mix(_haze(far, near), horizon, 0.30)
    ink_far = _shade(_mix(far, (25, 28, 42), 0.55), -10)
    ink_mid = _shade(_mix(near, (18, 20, 30), 0.55), -10)
    ink_near = _shade(_mix(near, (10, 12, 22), 0.65), -10)
    pine_accent = _mix(horizon, (255, 230, 200), 0.6)

    hb = _crag_ridge(w, ground_y, scroll, 0.07, 90,
                     jag_amp=6, jag_freq=0.5, seed=11)
    _ink_wash_strong(surf, hb, ground_y, ink_far,
                     _mix(ink_far, haze, 0.4),
                     alpha_top=200, fade=1.3,
                     rim_col=_mix(ink_far, horizon, 0.55))

    hm = _crag_ridge(w, ground_y, scroll, 0.16, 130,
                     jag_amp=22, jag_freq=0.7, seed=29)
    _ink_wash_strong(surf, hm, ground_y, ink_mid,
                     _mix(ink_mid, far, 0.25),
                     alpha_top=232, fade=1.4,
                     rim_col=_shade(ink_mid, -22))
    _dry_brush_crest(surf, hm, _shade(ink_mid, -28),
                     density=0.45, max_drip=4, seed=29)

    def scatter_crag(heights, layer_idx, ink, layer_seed, accent_col=pine_accent,
                     pine_h_range=(18, 32), allow_pagoda=False,
                     bird_count_range=(1, 3), rock_chance=0.4):
        rng = random.Random(_seed_for(scroll, layer_seed))
        n_sections = rng.randint(4, 6)
        cuts = sorted(rng.sample(range(30, w - 30), n_sections - 1))
        bounds = [0] + cuts + [w]
        peaks = _local_peaks(heights, look=14)
        peak_by_x = sorted([(heights[i][0], i) for i in peaks])
        for s in range(n_sections):
            lo, hi = bounds[s], bounds[s + 1]
            section_peaks = [i for x, i in peak_by_x if lo <= x <= hi]
            if not section_peaks:
                continue
            # 0-2 pines per section (clusters/gaps), random shape.
            n_pines = rng.randint(0, 2)
            for _ in range(n_pines):
                idx = rng.choice(section_peaks)
                cx, cy = heights[idx]
                shape = rng.choice(('bent', 'bent', 'fan', 'bonsai'))
                ph = rng.randint(*pine_h_range)
                if shape == 'bent':
                    _bent_pine(surf, cx, cy - 1, ph, ink, accent_col,
                               lean=rng.choice((-1, 1)))
                elif shape == 'fan':
                    _fan_pine(surf, cx, cy - 1, int(ph * 1.25),
                              ink, accent_col)
                else:
                    _bonsai_pine(surf, cx, cy - 1, max(8, ph - 8),
                                 ink, accent_col)
            # Maybe a scholar rock on a non-peak crest column.
            if rng.random() < rock_chance and hi - lo > 24:
                rx = rng.randint(lo + 8, hi - 8)
                ry = heights[min(rx, len(heights) - 1)][1]
                rw = rng.randint(8, 14)
                rh = rng.randint(8, 14)
                _scholar_rock(surf, rx, ry + 2, rw, rh,
                              _shade(ink, -8), _shade(ink, -18))
            # Maybe a hidden mini-pagoda silhouette on a low crest.
            if allow_pagoda and rng.random() < 0.3 and section_peaks:
                idx = rng.choice(section_peaks)
                cx, cy = heights[idx]
                _pagoda(surf, cx, cy - 1,
                        rng.choice((2, 3)), rng.randint(6, 9),
                        ink, accent_col, scale=rng.uniform(0.65, 0.9))
            # Tiny bird scribble overhead.
            if rng.random() < 0.5 and hi - lo > 28:
                bx = rng.randint(lo + 10, hi - 10)
                by = ground_y - rng.randint(120, 220)
                _bird_flight(surf, bx, by, rng.randint(*bird_count_range),
                             _shade(ink, -10), rng)

    # Element ink leans slightly lighter than the crag wash so the silhouettes
    # read off the heavy dark mid-band; pine accent stays warm so the brush-tap
    # finishing dot remains visible at any phase.
    elem_ink_mid = _mix(_shade(ink_mid, -20), (40, 45, 60), 0.0)
    elem_ink_mid = _shade(elem_ink_mid, 16)
    scatter_crag(hm, layer_idx=1,
                 ink=elem_ink_mid, layer_seed=0xD13A,
                 pine_h_range=(16, 28), allow_pagoda=True,
                 bird_count_range=(2, 4), rock_chance=0.4)

    hn = _crag_ridge(w, ground_y, scroll, 0.30, 180,
                     jag_amp=34, jag_freq=0.9, seed=53)
    _ink_wash_strong(surf, hn, ground_y, ink_near,
                     _mix(ink_near, far, 0.25),
                     alpha_top=250, fade=1.5,
                     rim_col=_shade(ink_near, -22))
    _dry_brush_crest(surf, hn, _shade(ink_near, -32),
                     density=0.55, max_drip=6, seed=53)
    # Near-band elements: a touch lighter than the heaviest ink so pines and
    # rock outcrops still read as separate shapes off the silhouette.
    elem_ink_near = _shade(ink_near, 10)
    scatter_crag(hn, layer_idx=2,
                 ink=elem_ink_near, layer_seed=0xD13B,
                 pine_h_range=(22, 38), allow_pagoda=True,
                 bird_count_range=(2, 5), rock_chance=0.5)

    # Occasional stone arch bridging two near-band crags.
    rng = random.Random(_seed_for(scroll, 0xB12D6E))
    if rng.random() < 0.5:
        valleys = _local_valleys(hn, look=20)
        if valleys:
            idx = rng.choice(valleys)
            vx, vy = hn[idx]
            _stone_arch(surf, vx, vy - 4, rng.randint(14, 22),
                        _shade(ink_near, -16), pine_accent)


# ══════════════════════════════════════════════════════════════════════════
# V14 — Pagoda-Crowned Ridges (ALIVE)
# User explicitly asked for varied pagoda tiers/sizes + trees and other
# elements. Full element vocabulary: pagodas (3/5/7 tier, 0.7×..1.6×),
# twisted pines, bamboo clumps, weeping willows, stone lanterns flanking
# pagodas, occasional smaller pavilions, and hanging banners between trees.
# ══════════════════════════════════════════════════════════════════════════

# Region-style table keeps every spawn within the shan-shui family while
# letting the look drift as the player scrolls right. Bucket is keyed off
# the element's WORLD-X (not the camera scroll) so an element retains its
# style for as long as it lives in the viewport; only new spawns picked up
# further along the world pick from later regions.
_V14_REGION_WIDTH = 600

_V14_REGION_STYLES = (
    # 0: slim Tang-tower silhouettes + bamboo + willow groves.
    dict(tier_choices=(5, 7, 7), pag_scale_mul=1.00,
         tree_weights=(('bamboo', 0.45), ('willow', 0.35),
                       ('pine_bent', 0.10), ('pine_fan', 0.10)),
         flavour_weights=(('pagoda', 0.40), ('grove', 0.30),
                          ('shrine', 0.15), ('mixed', 0.15))),
    # 1: squat 3-tier hilltop + fan-pine grove.
    dict(tier_choices=(3, 3, 5), pag_scale_mul=0.88,
         tree_weights=(('pine_fan', 0.55), ('pine_bent', 0.30),
                       ('bamboo', 0.10), ('willow', 0.05)),
         flavour_weights=(('pagoda', 0.30), ('grove', 0.40),
                          ('shrine', 0.15), ('mixed', 0.15))),
    # 2: mid-tier pair + weeping-willow river bank.
    dict(tier_choices=(5, 7), pag_scale_mul=1.05,
         tree_weights=(('willow', 0.55), ('bamboo', 0.20),
                       ('pine_bent', 0.15), ('pine_fan', 0.10)),
         flavour_weights=(('pagoda', 0.45), ('grove', 0.30),
                          ('shrine', 0.10), ('mixed', 0.15))),
    # 3: shrine-heavy + stone lantern paths + bent pine.
    dict(tier_choices=(3, 5), pag_scale_mul=0.92,
         tree_weights=(('pine_bent', 0.50), ('pine_fan', 0.25),
                       ('bamboo', 0.15), ('willow', 0.10)),
         flavour_weights=(('pagoda', 0.20), ('grove', 0.15),
                          ('shrine', 0.50), ('mixed', 0.15))),
    # 4: tallest 7-tier marker + dense bamboo summit.
    dict(tier_choices=(5, 7, 7), pag_scale_mul=1.18,
         tree_weights=(('bamboo', 0.55), ('pine_fan', 0.20),
                       ('willow', 0.15), ('pine_bent', 0.10)),
         flavour_weights=(('pagoda', 0.45), ('grove', 0.35),
                          ('shrine', 0.10), ('mixed', 0.10))),
)


def _v14_region(world_x):
    bucket = int(max(0, world_x) // _V14_REGION_WIDTH)
    return _V14_REGION_STYLES[bucket % len(_V14_REGION_STYLES)]


def _v14_weighted(rng, weights):
    total = sum(w for _, w in weights)
    r = rng.random() * total
    acc = 0.0
    for k, w in weights:
        acc += w
        if r <= acc:
            return k
    return weights[-1][0]


def draw_mountains_v14(surf, scroll, ground_y, w, far_color=None, near_color=None):
    pal = _biome.palette_for_phase(_keepers._PHASE)
    far = far_color or pal['mtn_far']
    near = near_color or pal['mtn_near']
    horizon = pal['horizon']
    night = min(1.0, pal['star_alpha'] / 235.0)
    haze = _mix(_haze(far, near), horizon, 0.32)

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
        crest_heights.append(h)

    pag_far = _shade(_sat(_mix(far, near, 0.7), 1.15), -42)
    pag_mid = _shade(_sat(near, 1.20), -46)
    pag_near = _shade(_sat(near, 1.30), -58)
    accent = _mix(horizon, (255, 230, 180), 0.55)
    # Banners pull a warm cinnabar by day, dim toward night.
    banner_col = _shade(_mix(_sat(horizon, 1.3), (190, 70, 60), 0.5),
                        int(-70 * night))

    def scatter_pagoda(heights, layer_idx, base_color, layer_seed,
                       pag_scale_range, tier_choices, tree_scale=1.0,
                       allow_banner=True):
        rng = random.Random(_seed_for(scroll, layer_seed))
        # Far band runs sparser than mid/near so the horizon stays calm.
        if layer_idx == 2:
            n_sections = 1
        else:
            n_sections = 2
        cuts = sorted(rng.sample(range(40, w - 40), n_sections - 1))
        bounds = [0] + cuts + [w]
        peaks = _local_peaks(heights, look=18)
        peaks_by_x = sorted([(heights[i][0], i) for i in peaks])

        def _draw_tree(kind, tx, ty):
            # Region-style picks the kind; this routes to the right helper
            # at a kind-appropriate height (scaled by depth band).
            if kind == 'pine_bent':
                _bent_pine(surf, tx, ty - 1,
                           int(rng.randint(14, 26) * tree_scale),
                           base_color, accent, lean=rng.choice((-1, 1)))
            elif kind == 'pine_fan':
                _fan_pine(surf, tx, ty - 1,
                          int(rng.randint(20, 32) * tree_scale),
                          base_color, accent)
            elif kind == 'bamboo':
                _bamboo(surf, tx, ty - 1,
                        int(rng.randint(10, 18) * tree_scale),
                        base_color, accent)
            else:
                _willow(surf, tx, ty,
                        int(rng.randint(9, 14) * tree_scale), base_color)

        for s in range(n_sections):
            lo, hi = bounds[s], bounds[s + 1]
            section_peaks = [i for x, i in peaks_by_x if lo <= x <= hi]
            # Section flavour follows the REGION at the section's world-x —
            # so consecutive regions feel like different villages on the
            # same shan-shui ridgeline.
            sec_wx = scroll + (lo + hi) * 0.5
            sec_region = _v14_region(sec_wx)
            flavour = _v14_weighted(rng, sec_region['flavour_weights'])

            if flavour == 'pagoda' and section_peaks:
                idx = rng.choice(section_peaks)
                cx, cy = heights[idx]
                elem_region = _v14_region(scroll + cx)
                tiers = rng.choice(elem_region['tier_choices'])
                bw = rng.randint(10, 16)
                lo_s, hi_s = pag_scale_range
                sc = rng.uniform(lo_s, hi_s) * elem_region['pag_scale_mul']
                _pagoda(surf, cx, cy - 1, tiers, bw, base_color, accent, sc)
                if rng.random() < 0.25:
                    _stone_lantern(surf, cx - 10, cy - 1, base_color, accent)
                    _stone_lantern(surf, cx + 10, cy - 1, base_color, accent)
            elif flavour == 'grove' and section_peaks:
                idx = rng.choice(section_peaks)
                cx, cy = heights[idx]
                count = rng.randint(1, 2)
                for _ in range(count):
                    tx = cx + rng.randint(-22, 22)
                    if not (lo <= tx <= hi):
                        continue
                    ty = heights[min(tx, len(heights) - 1)][1]
                    elem_region = _v14_region(scroll + tx)
                    kind = _v14_weighted(rng, elem_region['tree_weights'])
                    _draw_tree(kind, tx, ty)
                if allow_banner and rng.random() < 0.30:
                    bx = cx + rng.randint(-18, 18)
                    by = heights[min(bx, len(heights) - 1)][1]
                    _hanging_banner(surf, bx, by - 18,
                                    rng.randint(10, 16), banner_col)
            elif flavour == 'shrine' and section_peaks:
                idx = rng.choice(section_peaks)
                cx, cy = heights[idx]
                elem_region = _v14_region(scroll + cx)
                pscale = rng.uniform(0.85, 1.15) * elem_region['pag_scale_mul']
                _pavilion(surf, cx, cy - 1, base_color, accent, scale=pscale)
                _stone_lantern(surf, cx + rng.choice((-12, 12)), cy - 1,
                               base_color, accent)
                if rng.random() < 0.50:
                    tx = cx + rng.randint(-26, 26)
                    if lo <= tx <= hi:
                        ty = heights[min(tx, len(heights) - 1)][1]
                        kind = _v14_weighted(rng,
                                             elem_region['tree_weights'])
                        _draw_tree(kind, tx, ty)
            else:  # 'mixed' — one pagoda + at most one accent tree
                if section_peaks:
                    idx = rng.choice(section_peaks)
                    cx, cy = heights[idx]
                    elem_region = _v14_region(scroll + cx)
                    tiers = rng.choice(elem_region['tier_choices'])
                    lo_s, hi_s = pag_scale_range
                    sc = rng.uniform(lo_s, hi_s) * elem_region['pag_scale_mul']
                    _pagoda(surf, cx, cy - 1, tiers, rng.randint(9, 13),
                            base_color, accent, scale=sc)
                if rng.random() < 0.50 and hi - lo >= 20:
                    tx = rng.randint(lo + 6, hi - 6)
                    ty = heights[min(tx, len(heights) - 1)][1]
                    elem_region = _v14_region(scroll + tx)
                    kind = _v14_weighted(rng, elem_region['tree_weights'])
                    _draw_tree(kind, tx, ty)

    # Far band — small pagodas, no trees.
    scatter_pagoda(crest_heights[2], layer_idx=2,
                   base_color=pag_far, layer_seed=0xE14A,
                   pag_scale_range=(0.7, 0.95),
                   tier_choices=(3, 5), tree_scale=0.7,
                   allow_banner=False)
    # Mid band — full vocabulary.
    scatter_pagoda(crest_heights[3], layer_idx=3,
                   base_color=pag_mid, layer_seed=0xE14B,
                   pag_scale_range=(0.95, 1.25),
                   tier_choices=(3, 5, 5, 7), tree_scale=1.0)
    # Near band — biggest pagodas + trees.
    scatter_pagoda(crest_heights[4], layer_idx=4,
                   base_color=pag_near, layer_seed=0xE14C,
                   pag_scale_range=(1.15, 1.55),
                   tier_choices=(5, 7, 7), tree_scale=1.3)


# ── dispatcher ───────────────────────────────────────────────────────────────

VARIANTS = {
    4: draw_mountains_v4,
    12: draw_mountains_v12,
    13: draw_mountains_v13,
    14: draw_mountains_v14,
}

VARIANT_NAMES = {
    4: "Shan-Shui Ink Ridges (alive)",
    12: "Cloud Sea Peaks (alive)",
    13: "Sumi-e Crags + Pines (alive)",
    14: "Pagoda-Crowned Ridges (alive)",
}
