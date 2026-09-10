"""Live mountain backdrop — V14 "Pagoda-Crowned Ridges (alive)".

Five parallax ridge bands washed with ink-gradient depth, then scattered with
pagodas, pavilions, pines, bamboo, willows, stone lanterns and banners whose mix
follows a per-world-x region archetype — so each stretch of the ridgeline reads
as a different village. Everything re-tints across the biome day/night cycle via
the imported palette. Ornaments are anchored to fixed WORLD cells (RNG seeded off
the cell's world index, not the camera), so a given village keeps its identity and
scrolls smoothly with the ridge — a few alive at once, new ones entering at the
right edge — instead of re-rolling every frame.

Consolidated single module for the live game (one import surface). Source of
truth for the design exploration + the user-picked winner lives in
`archive/mountain_redesign/` and `docs/mountain_redesign/_comparison_alive_dayNight.png`.
"""
from __future__ import annotations

import math
import random

import pygame


# ── colour math + ridge/ink primitives ───────────────────────────────────────

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

def _aa_crest(surf, heights, color, width=1):
    """Anti-aliased ridge stroke where it's cheap (native+WASM both support
    aaline). Falls back gracefully if the segment list is short."""
    if len(heights) < 2:
        return
    pygame.draw.aalines(surf, color, False, heights)
    if width > 1:
        pygame.draw.lines(surf, color, False, heights, width)

# ── ornament drawers ─────────────────────────────────────────────────────────

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

def _hanging_banner(surf, x, top_y, length, color):
    """A vertical hanging cloth banner — a tall thin coloured rectangle with
    a tassel at the bottom. Marks villages/shrines on a ridge crown."""
    rect = pygame.Rect(x - 1, top_y, 3, length)
    pygame.draw.rect(surf, color, rect)
    # Tassel — a single pixel tail.
    surf.set_at((x, top_y + length), color)
    surf.set_at((x, top_y + length + 1), color)

# ── ridge analysis ───────────────────────────────────────────────────────────

def _layer_terms(k):
    """Sine terms for ridge band k — shared by the silhouette (`_ridge`) and the
    ornament projection (`_ridge_h`) so both read the same crest line."""
    return [(0.011 + k * 0.002, 24 - k * 2, 0.6 + k),
            (0.030 + k * 0.004, 12, 1.5 - k * 0.3)]

def _ridge_h(wx, base_h, terms):
    """Scalar ridge height at WORLD-x `wx` — the same per-point sum `_ridge`
    evaluates, so an ornament placed here sits on the drawn silhouette pixel."""
    h = base_h
    for freq, amp, ph in terms:
        h += math.sin(wx * freq + ph) * amp
    return h

def _summit_near(wx, base_h, terms, span=16):
    """Nudge a world-x to the nearest crest within ±span so ornaments crown
    summits rather than slopes. World-space stand-in for the old screen-index
    peak scan — stable as the world scrolls because it's a function of `wx`."""
    best_x, best_h = wx, _ridge_h(wx, base_h, terms)
    for d in range(-span, span + 1):
        ch = _ridge_h(wx + d, base_h, terms)
        if ch > best_h:
            best_h, best_x = ch, wx + d
    return best_x

# ── region archetype system ──────────────────────────────────────────────────

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

# ── baked-strip cache ─────────────────────────────────────────────────────────
#
# draw_mountains_v14 is a pure function of (scroll, phase): every ridge sample is
# a function of camera-x (cam = scroll*speed) and every ornament is world-cell
# seeded. Recomputing it per frame cost ~5.8 ms (per-pixel ridge scans + a
# Surface+mask per layer in _ink_wash_strong + per-cell ornament draws). So bake
# each render unit into a wide strip ONCE per (phase bucket, camera window) and
# blit it at the parallax offset — mirroring foreground._bake_floor_strip
# (game/foreground.py:37-67). A unit re-bakes only when its bucket changes or its
# scroll offset leaves the window. Colours snap per phase bucket exactly like the
# baked floor strip; the cross-blend the sky uses can't apply here because these
# strips carry per-pixel alpha (set_alpha is ignored on SRCALPHA surfaces).
#
# Render units are kept in BLIT ORDER — all 5 ink-wash layers (far->near) then the
# 3 ornament bands (far->near) — so a far village still paints over a nearer ridge
# exactly as the original single-pass draw did (washes first, scatter last).

_MTN_MARGIN = 96            # camera-space slack each side; > widest ornament half-w
_MTN_BAND_H = 340           # tallest crest (124) + sine swing + tallest ornament
_SPECS_SPEED = (0.05, 0.08, 0.13, 0.20, 0.28)
_UNITS = (('wash', 0), ('wash', 1), ('wash', 2), ('wash', 3), ('wash', 4),
          ('deco', 2), ('deco', 3), ('deco', 4))
_NUM_UNITS = len(_UNITS)
# Per-band ornament config (mirrors the old scatter_pagoda call sites). `base` =
# index into the (pag_far, pag_mid, pag_near) colour triple.
_SCATTER = {
    2: dict(base=0, layer_seed=0xE14A, pag_scale_range=(0.7, 0.95), cell=230,
            tree_scale=0.7, allow_banner=False),
    3: dict(base=1, layer_seed=0xE14B, pag_scale_range=(0.95, 1.25), cell=190,
            tree_scale=1.0, allow_banner=True),
    4: dict(base=2, layer_seed=0xE14C, pag_scale_range=(1.15, 1.55), cell=165,
            tree_scale=1.3, allow_banner=True),
}

_u_surf:   list = [None] * _NUM_UNITS   # baked pygame.Surface per unit (cropped)
_u_anchor: list = [0] * _NUM_UNITS      # integer camera-x mapped to strip local x=0
_u_bucket: list = [-1] * _NUM_UNITS     # biome.phase_bucket the strip was baked for
_u_top:    list = [0] * _NUM_UNITS      # screen-y the cropped strip blits at
_u_left:   list = [0] * _NUM_UNITS      # crop x-offset (local x=0 -> anchor + left)
_u_dims = None                          # (w, ground_y) the cache was built for
_EMPTY_STRIP = None                     # shared 1x1 placeholder for empty units

# At most this many COLOUR-only re-bakes per frame: a phase-bucket change dirties
# all 8 units at once and re-baking them in one frame is a ~14 ms hitch, so spread
# them over a few frames (each unit keeps blitting its prior-bucket strip until its
# turn — a few frames of slightly-stale tint, invisible). Geometry (window-exit)
# re-bakes are NOT budgeted — they must happen the frame they're needed.
_MTN_REBAKE_BUDGET = 2


def _ensure_dims(w, ground_y):
    global _u_dims, _EMPTY_STRIP
    if _EMPTY_STRIP is None:
        _EMPTY_STRIP = pygame.Surface((1, 1), pygame.SRCALPHA)
    if _u_dims != (w, ground_y):
        _u_dims = (w, ground_y)
        for i in range(_NUM_UNITS):
            _u_surf[i] = None


def _resolve_specs(phase):
    """Palette-derived layer specs + ornament colours at `phase` (the BUCKET edge
    phase, so baked colours match the sky's per-bucket palette). Verbatim of the
    old draw_mountains_v14 colour block."""
    from game import biome as _biome
    pal = _biome.palette_for_phase(phase)
    far = pal['mtn_far']
    near = pal['mtn_near']
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
    pag_far = _shade(_sat(_mix(far, near, 0.7), 1.15), -42)
    pag_mid = _shade(_sat(near, 1.20), -46)
    pag_near = _shade(_sat(near, 1.30), -58)
    accent = _mix(horizon, (255, 230, 180), 0.55)
    banner_col = _shade(_mix(_sat(horizon, 1.3), (190, 70, 60), 0.5),
                        int(-70 * night))
    return specs, (pag_far, pag_mid, pag_near, accent, banner_col)


def _scatter_pagoda_strip(surf, strip_w, gy_local, cam, base_h, terms,
                          base_color, layer_seed, pag_scale_range, cell,
                          accent, banner_col, tree_scale=1.0, allow_banner=True):
    """Module-level form of the old `scatter_pagoda` closure, drawing into a baked
    strip whose local x=0 maps to camera-x `cam`. Placement/seeding is identical to
    the live path (cell RNG by index, summit by world-x), so baked villages match."""
    margin = 60
    c0 = int(math.floor((cam - margin) / cell))
    c1 = int(math.floor((cam + strip_w + margin) / cell))

    def _project(wx):
        return (int(round(wx - cam)),
                gy_local - int(round(_ridge_h(wx, base_h, terms))))

    def _draw_tree(rng, kind, tx, ty):
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

    for c in range(c0, c1 + 1):
        rng = random.Random((c * 0x9E3779B1) ^ layer_seed)
        anchor = _summit_near(c * cell + rng.uniform(12, cell - 12),
                              base_h, terms)
        region = _v14_region(anchor)
        flavour = _v14_weighted(rng, region['flavour_weights'])
        cx, cy = _project(anchor)

        if flavour == 'pagoda':
            tiers = rng.choice(region['tier_choices'])
            bw = rng.randint(10, 16)
            lo_s, hi_s = pag_scale_range
            sc = rng.uniform(lo_s, hi_s) * region['pag_scale_mul']
            _pagoda(surf, cx, cy - 1, tiers, bw, base_color, accent, sc)
            if rng.random() < 0.25:
                _stone_lantern(surf, cx - 10, cy - 1, base_color, accent)
                _stone_lantern(surf, cx + 10, cy - 1, base_color, accent)
        elif flavour == 'grove':
            for _ in range(rng.randint(1, 2)):
                twx = anchor + rng.randint(-22, 22)
                tx, ty = _project(twx)
                kind = _v14_weighted(rng, _v14_region(twx)['tree_weights'])
                _draw_tree(rng, kind, tx, ty)
            if allow_banner and rng.random() < 0.30:
                bx, by = _project(anchor + rng.randint(-18, 18))
                _hanging_banner(surf, bx, by - 18,
                                rng.randint(10, 16), banner_col)
        elif flavour == 'shrine':
            pscale = rng.uniform(0.85, 1.15) * region['pag_scale_mul']
            _pavilion(surf, cx, cy - 1, base_color, accent, scale=pscale)
            lx, ly = _project(anchor + rng.choice((-12, 12)))
            _stone_lantern(surf, lx, ly - 1, base_color, accent)
            if rng.random() < 0.50:
                twx = anchor + rng.randint(-26, 26)
                tx, ty = _project(twx)
                kind = _v14_weighted(rng, _v14_region(twx)['tree_weights'])
                _draw_tree(rng, kind, tx, ty)
        else:  # 'mixed' — one pagoda + at most one accent tree
            tiers = rng.choice(region['tier_choices'])
            lo_s, hi_s = pag_scale_range
            sc = rng.uniform(lo_s, hi_s) * region['pag_scale_mul']
            _pagoda(surf, cx, cy - 1, tiers, rng.randint(9, 13),
                    base_color, accent, scale=sc)
            if rng.random() < 0.50:
                twx = anchor + rng.randint(-14, 14)
                tx, ty = _project(twx)
                kind = _v14_weighted(rng, _v14_region(twx)['tree_weights'])
                _draw_tree(rng, kind, tx, ty)


def _bake_unit(ui, w, ground_y, anchor, bucket):
    """Bake one render unit's strip (ink-wash layer OR ornament band) at camera
    anchor `anchor` for phase `bucket`. Returns (surface, screen_top)."""
    from game import biome as _biome
    kind, layer = _UNITS[ui]
    bphase = bucket / _biome.PHASE_BUCKETS
    specs, deco = _resolve_specs(bphase)
    speed, base_h, atop, itop, ibot = specs[layer]
    terms = _layer_terms(layer)
    strip_w = w + 2 * _MTN_MARGIN
    band_top = max(0, ground_y - _MTN_BAND_H)
    gy_local = ground_y - band_top
    strip = pygame.Surface((strip_w, gy_local), pygame.SRCALPHA)
    if kind == 'wash':
        # speed=1.0, scroll=anchor -> per-pixel sample sx = x + anchor = camera-x.
        _, heights = _ridge(strip_w, gy_local, anchor, 1.0, base_h, terms)
        _ink_wash_strong(strip, heights, gy_local, itop, ibot, atop, fade=1.6,
                         rim_col=_shade(_sat(itop, 1.2), -28))
    else:
        cfg = _SCATTER[layer]
        _scatter_pagoda_strip(strip, strip_w, gy_local, anchor, base_h, terms,
                              deco[cfg['base']], cfg['layer_seed'],
                              cfg['pag_scale_range'], cfg['cell'],
                              deco[3], deco[4], tree_scale=cfg['tree_scale'],
                              allow_banner=cfg['allow_banner'])
    # Crop to the drawn content so the per-frame blit only touches live pixels —
    # the washes are mostly transparent sky above the crest and the ornament
    # strips are nearly empty. Store the crop's (left, top) so the blit re-adds it.
    bbox = strip.get_bounding_rect()
    if bbox.width == 0 or bbox.height == 0:
        return _EMPTY_STRIP, band_top, 0
    return strip.subsurface(bbox).copy(), band_top + bbox.y, bbox.x


def prewarm(w, ground_y, phase=0.02):
    """Bake every unit for the current bucket at scroll=0 so the first gameplay
    frame is a cache hit (mirrors geyser_fx.prewarm)."""
    from game import biome as _biome
    _ensure_dims(w, ground_y)
    bucket = _biome.phase_bucket(phase)
    for ui in range(_NUM_UNITS):
        anchor = -_MTN_MARGIN
        (_u_surf[ui], _u_top[ui],
         _u_left[ui]) = _bake_unit(ui, w, ground_y, anchor, bucket)
        _u_anchor[ui] = anchor
        _u_bucket[ui] = bucket



# ── entry point ──────────────────────────────────────────────────────────────

def draw_mountains_v14(surf, scroll, ground_y, w, *, phase=0.02):
    """Blit the baked ridge/ornament strips at their per-layer parallax offsets,
    re-baking a unit only when its phase bucket changes or its scroll offset
    leaves the baked window — the mountains' equivalent of the cached floor strip.
    Pure blits on the steady-state frame; the heavy procedural draw happens at most
    once per bucket/window change per unit."""
    from game import biome as _biome
    _ensure_dims(w, ground_y)
    bucket = _biome.phase_bucket(phase)
    win = 2 * _MTN_MARGIN
    budget = _MTN_REBAKE_BUDGET
    for ui in range(_NUM_UNITS):
        cam = scroll * _SPECS_SPEED[_UNITS[ui][1]]
        off = cam - _u_anchor[ui]
        need_geom = _u_surf[ui] is None or off < 0 or off > win
        need_color = bucket != _u_bucket[ui]
        if need_geom or (need_color and budget > 0):
            anchor = int(round(cam)) - _MTN_MARGIN
            (_u_surf[ui], _u_top[ui],
             _u_left[ui]) = _bake_unit(ui, w, ground_y, anchor, bucket)
            _u_anchor[ui] = anchor
            _u_bucket[ui] = bucket
            off = cam - anchor
            if need_color and not need_geom:
                budget -= 1
        surf.blit(_u_surf[ui], (round(-off) + _u_left[ui], _u_top[ui]))
