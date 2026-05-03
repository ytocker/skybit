"""Pillar graphics upgrade picker — 5-tier cumulative ladder.

V0 — Current (reference)
V1 — Hi-res stone (3× supersample → smoothscale-down)
V2 — V1 + sun-aware rim-light + warm-top/cool-bottom grad + crack lip
V3 — V2 + animated vegetation + breathing mist
V4 — V3 + sparkles on spiral glows / lanterns + gap-edge readability bloom
V5 — V4 + cinematic layered foliage + falling leaf particles

Each `install_tier(n)` returns a context manager that monkey-patches
the live draw path. On exit, originals are restored. Picker only —
does NOT modify any `game/` file.
"""
import contextlib
import math
import random

import pygame

from game import draw as gdraw
from game import pillar_variants as gpv


# ── Module-level state set by the harness per render ──────────────────
_CURRENT_T: float = 0.0          # game time → V3+ animations
_CURRENT_SUN_PHASE: float = 0.5  # biome phase 0..1 → V2 rim-light direction


def set_render_state(t: float, sun_phase: float):
    """Harness calls this before each tier's render."""
    global _CURRENT_T, _CURRENT_SUN_PHASE
    _CURRENT_T = float(t)
    _CURRENT_SUN_PHASE = float(sun_phase)


# ──────────────────────────────────────────────────────────────────────
# V1 — hi-res stone body
# ──────────────────────────────────────────────────────────────────────
SS = 3   # supersample factor


def _make_body_scaled(w, h, light, mid, dark, accent, body_seed=0):
    """Scale-aware port of `gdraw._make_stone_pillar_body`. Builds at
    `SS × native`, smoothscales DOWN to (w, h)."""
    bw, bh = w * SS, h * SS
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)

    # Cylinder shading: per source-x column at hi-res
    for x in range(bw):
        u = x / max(1, bw - 1)
        if u < 0.18:
            c = gdraw.lerp_color(mid, light, (0.18 - u) / 0.18)
        elif u < 0.55:
            seg = (u - 0.18) / 0.37
            c = gdraw.lerp_color(light, mid, seg * seg * (3 - 2 * seg))
        else:
            seg = (u - 0.55) / 0.45
            c = gdraw.lerp_color(mid, dark, seg * seg * (3 - 2 * seg))
        pygame.draw.line(surf, c, (x, 0), (x, bh - 1))

    # Accent stripe
    accent_w = max(1, 3 * SS)
    accent_surf = pygame.Surface((accent_w, bh), pygame.SRCALPHA)
    accent_surf.fill((*accent, 90))
    surf.blit(accent_surf, (int(bw * 0.14), 0))

    # Erosion striations + horizontal cracks (rng keyed off NATIVE w,h
    # so layout matches the original at this body_seed bucket)
    rng = random.Random(w * 7919 + h + body_seed * 6151)
    stripe_w = max(1, SS // 2 + 1)
    striation_xs = [rng.randint(3, w - 4) for _ in range(4)]
    for gx in striation_xs:
        pygame.draw.line(surf, gdraw._shade(dark, -10),
                         (gx * SS, 0), (gx * SS, bh - 1), stripe_w)

    crack_step = 80
    ystart = rng.randint(10, crack_step)
    for cy in range(ystart, h - 10, crack_step):
        jitter = rng.randint(-3, 3)
        cy_a = (cy + jitter) * SS
        cy_b = (cy + jitter + rng.randint(-1, 1)) * SS
        pygame.draw.line(surf, gdraw._shade(dark, -20),
                         (2 * SS, cy_a), ((w - 3) * SS, cy_b), stripe_w)
        # Tiny pebble flecks
        px1 = rng.randint(4, w - 5) * SS
        px2 = rng.randint(4, w - 5) * SS
        pygame.draw.line(surf, light,
                         (px1, (cy + jitter + 1) * SS),
                         (px2, (cy + jitter + 2) * SS), stripe_w)

    return pygame.transform.smoothscale(surf, (w, h))


# ──────────────────────────────────────────────────────────────────────
# V2 — stone richness (rim-light + vertical grad + deeper crack lip)
# ──────────────────────────────────────────────────────────────────────
def _make_body_v2(w, h, light, mid, dark, accent, body_seed=0):
    """V1 + sun-aware rim-light + warm-top/cool-bottom grad + crack lip."""
    base = _make_body_scaled(w, h, light, mid, dark, accent, body_seed)

    # Vertical gradient overlay: warm boost in top 30%, cool tint in bottom 40%
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    warm = (255, 220, 170)
    cool = (90, 110, 150)
    for y in range(h):
        t = y / max(1, h - 1)
        if t < 0.30:
            mix = (0.30 - t) / 0.30
            grad.fill((*warm, int(34 * mix)), pygame.Rect(0, y, w, 1))
        elif t > 0.60:
            mix = (t - 0.60) / 0.40
            grad.fill((*cool, int(22 * mix)), pygame.Rect(0, y, w, 1))
    base.blit(grad, (0, 0))

    # Sun-aware rim-light bright stripe
    sp = _CURRENT_SUN_PHASE
    sun_brightness = 0.5 + 0.5 * math.cos((sp - 0.25) * 2 * math.pi)
    if sun_brightness > 0.15:
        sun_x_norm = math.sin(sp * 2 * math.pi)         # -1..+1
        rim_pos = int(w * (0.5 + sun_x_norm * 0.42))
        rim_w = max(2, w // 14)
        rim_alpha = int(140 * sun_brightness)
        rim = pygame.Surface((rim_w, h), pygame.SRCALPHA)
        rim.fill((255, 240, 200, rim_alpha))
        base.blit(rim, (max(0, rim_pos - rim_w // 2), 0),
                  special_flags=pygame.BLEND_RGBA_ADD)

    # Deeper crack lip — derive same crack ys from the same RNG sequence
    rng = random.Random(w * 7919 + h + body_seed * 6151)
    for _ in range(4):
        rng.randint(3, w - 4)
    crack_step = 80
    ystart = rng.randint(10, crack_step)
    for cy in range(ystart, h - 10, crack_step):
        jitter = rng.randint(-3, 3)
        cy_p = cy + jitter
        if 1 <= cy_p < h - 1:
            highlight = pygame.Surface((w - 6, 1), pygame.SRCALPHA)
            highlight.fill((*light, 170))
            base.blit(highlight, (3, cy_p - 1))
            shadow = pygame.Surface((w - 6, 1), pygame.SRCALPHA)
            shadow.fill((10, 8, 6, 200))
            base.blit(shadow, (3, cy_p + 1))
        rng.randint(-1, 1)
        rng.randint(4, w - 5)
        rng.randint(4, w - 5)

    return base


# ──────────────────────────────────────────────────────────────────────
# V3 — animated vegetation (monkey-patched at install)
# Each helper mirrors the original signature and reads `_CURRENT_T`.
# ──────────────────────────────────────────────────────────────────────
def _v3_prayer_flags(surf, x1, y1, x2, y2, n=7):
    """Bezier flag chain with breathing sag + per-flag flutter."""
    t = _CURRENT_T
    sag = math.sin(t * 0.9) * 4 + 14
    mx, my = (x1 + x2) // 2, max(y1, y2) + sag
    steps = 30
    pts = []
    for i in range(steps + 1):
        u = i / steps
        bx = (1 - u) ** 2 * x1 + 2 * (1 - u) * u * mx + u * u * x2
        by = (1 - u) ** 2 * y1 + 2 * (1 - u) * u * my + u * u * y2
        pts.append((int(bx), int(by)))
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, (90, 70, 55), pts[i], pts[i + 1], 1)
    for i in range(n):
        px, py = pts[int((i + 0.5) / n * steps)]
        flap = int(math.sin(t * 4.0 + i * 0.7) * 1.5)
        rect = pygame.Rect(px - 3, py + flap, 6, 8)
        pygame.draw.rect(surf, gpv._FLAG_COLORS[i % 5], rect)
        pygame.draw.rect(surf, (40, 30, 20), rect, 1)


def _v3_paper_lantern(surf, x, y, strand=14, scale=1.0, color='red'):
    """Pendulum sway: lantern offset by sin(t·1.4 + per-pillar phase)."""
    t = _CURRENT_T
    sway = int(math.sin(t * 1.4 + x * 0.05) * 2)
    gpv._ORIG_paper_lantern(surf, x + sway, y, strand=strand,
                             scale=scale, color=color)


def _v3_pillar_mist(surf, cx, base_y, width, alpha=110):
    """Mist alpha breathes on slow sine."""
    t = _CURRENT_T
    breath = 0.85 + 0.15 * math.sin(t * 0.7 + cx * 0.04)
    gdraw._ORIG_pillar_mist(surf, cx, base_y, width,
                             alpha=int(alpha * breath))


def _v3_cascading_vine(surf, x, y, length, palette):
    """Vine tip sways; root anchored. Sway amplitude grows along length."""
    t = _CURRENT_T
    seed_phase = x * 0.07 + y * 0.03
    dark, mid, top = (palette['foliage_dark'], palette['foliage_mid'],
                      palette['foliage_top'])
    for i in range(length):
        u = i / max(1, length - 1)
        off = int(math.sin(u * 4 + t * 1.3 + seed_phase) * 2 * (0.4 + u))
        pygame.draw.line(surf, dark, (x + off, y + i),
                         (x + off, y + i + 1), 2)
    for frac, r in ((0.25, 3), (0.55, 4), (0.85, 4)):
        py = y + int(frac * length)
        sway = math.sin(frac * 4 + t * 1.3 + seed_phase) * 2 * (0.4 + frac)
        px = x + int(sway)
        pygame.draw.circle(surf, dark, (px, py), r + 1)
        pygame.draw.circle(surf, mid, (px, py), r)
        pygame.draw.circle(surf, top, (px - 1, py - 1), max(1, r - 2))
        pygame.draw.circle(surf, (255, 180, 120), (px + 1, py + 1), 1)


def _v3_moss_strand(surf, x, y, length, palette, jitter_seed=0):
    """Moss tip sways; bulb at the end follows."""
    t = _CURRENT_T
    dark = palette['foliage_dark']
    mid  = palette['foliage_mid']
    top  = palette['foliage_top']
    accent = palette['foliage_accent']
    for i in range(length):
        yy = y + i
        u = i / max(1, length)
        sway = math.sin(t * 1.0 + (i + jitter_seed) * 0.45) * 1.5 * u
        jitter = int(math.sin((i + jitter_seed) * 0.45) * 1.2 + sway)
        col = gdraw.lerp_color(dark, mid, u)
        pygame.draw.line(surf, col, (x + jitter, yy),
                         (x + jitter, yy + 1), 1)
    tip_sway = int(math.sin(t * 1.0 + jitter_seed * 0.45) * 1.5)
    tip_y = y + length
    bulb = max(5, length // 3)
    bx = x + tip_sway
    pygame.draw.ellipse(surf, dark,
                        (bx - bulb // 2, tip_y - bulb // 2, bulb, bulb))
    pygame.draw.ellipse(surf, mid,
                        (bx - bulb // 2 + 1, tip_y - bulb // 2,
                         bulb - 2, bulb - 1))
    pygame.draw.ellipse(surf, top,
                        (bx - bulb // 2 + 2, tip_y - bulb // 2,
                         max(2, bulb - 5), max(2, bulb - 5)))
    pygame.draw.circle(surf, accent, (bx + 2, tip_y - bulb // 3), 2)


# ──────────────────────────────────────────────────────────────────────
# V4 — sparkles + readability bloom
# ──────────────────────────────────────────────────────────────────────
def _v4_spiral_glow(surf, cx, cy, radius=10):
    """Original spiral + 3 bounded sparkles orbiting the rim."""
    gpv._ORIG_spiral_glow(surf, cx, cy, radius=radius)
    t = _CURRENT_T
    seed_phase = cx * 0.13 + cy * 0.07
    for k in range(3):
        a = t * 1.6 + seed_phase + k * (2 * math.pi / 3)
        r = radius + 2 + math.sin(t * 2.0 + k) * 1.5
        sx = cx + int(math.cos(a) * r)
        sy = cy + int(math.sin(a) * r)
        pygame.draw.circle(surf, (255, 240, 200), (sx, sy), 1)
        pygame.draw.circle(surf, (255, 220, 140), (sx, sy), 2, 1)


def _v4_paper_lantern(surf, x, y, strand=14, scale=1.0, color='red'):
    """V3 sway + 2 fireflies floating up from the lantern body."""
    _v3_paper_lantern(surf, x, y, strand=strand, scale=scale, color=color)
    t = _CURRENT_T
    seed_phase = x * 0.11 + y * 0.05
    for k in range(2):
        u = (t * 0.4 + seed_phase + k * 0.5) % 1.0
        sx = x + int(math.sin(u * 4 + seed_phase) * 6)
        sy = y + strand // 2 - int(u * 28)
        pygame.draw.circle(surf, (255, 235, 170), (sx, sy), 1)


def _v4_paint_stone(surf, rect, polygon_fn, palette, body_seed):
    """Live `_paint_stone` + soft ellipse halo straddling the gap-facing
    edge so the gap silhouette reads against busy backdrops. The halo
    is an ellipse (not a rectangle) and uses additive blending with
    moderate alpha so it reads as a glow, not a paint stripe."""
    gpv._ORIG_paint_stone(surf, rect, polygon_fn, palette, body_seed)
    if rect.height <= 6 or rect.width <= 4:
        return
    name = polygon_fn.__name__
    is_top = name.startswith('silhouette_top') or name.startswith('sil_top')
    # Confine the halo to the pillar polygon shape so it lights the
    # GAP-FACING RIM of the stone without staining the sky. We build a
    # local pillar-only surface, draw the halo into it, mask to the
    # silhouette polygon, and blit back.
    poly = polygon_fn(rect.width, rect.height)
    halo_layer = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    halo_col = gdraw.lerp_color(palette['stone_light'], (255, 230, 170), 0.65)
    bloom_h = max(6, min(14, rect.height // 6))
    if is_top:
        # Halo at bottom of polygon (gap-facing edge of top pillar)
        for i in range(bloom_h):
            u = i / max(1, bloom_h - 1)            # 0 at top of band, 1 at bottom
            a = int(95 * u)                         # peaks at the gap edge
            halo_layer.fill((*halo_col, a),
                            pygame.Rect(0, rect.height - bloom_h + i,
                                        rect.width, 1))
    else:
        # Halo at top of polygon (gap-facing edge of bottom pillar)
        for i in range(bloom_h):
            u = i / max(1, bloom_h - 1)
            a = int(95 * (1 - u))                   # peaks at the gap edge
            halo_layer.fill((*halo_col, a),
                            pygame.Rect(0, i, rect.width, 1))
    # Mask halo to the polygon silhouette (so it doesn't bleed past the
    # silhouette's tapers / ledges).
    mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    halo_layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(halo_layer, rect.topleft)


# ──────────────────────────────────────────────────────────────────────
# V5 — layered cinematic foliage + leaf particles
# ──────────────────────────────────────────────────────────────────────
def _v5_wuling_pine(surf, root_x, root_y, height, palette,
                     lean=0, direction='up', layers=5):
    """Layered pine: back-shadow + original + front-rimlight passes.
    Rim-light side derived from current sun phase."""
    pine_dk  = palette['foliage_dark']
    pine_mid = palette['foliage_mid']
    pine_lt  = palette['foliage_top']
    sp = _CURRENT_SUN_PHASE
    rim_dx = -1 if math.sin(sp * 2 * math.pi) < 0 else +1
    sign = -1 if direction == 'up' else 1
    tip_x = root_x + lean
    tip_y = root_y + sign * height
    # Back-shadow trunk (down-right offset, darker)
    pygame.draw.line(surf, (35, 24, 16),
                     (root_x + 1, root_y + 1), (tip_x + 1, tip_y + 1), 2)
    pygame.draw.line(surf, (60, 42, 28), (root_x, root_y), (tip_x, tip_y), 2)
    for i in range(layers):
        u = i / max(1, layers - 1)
        layer_w = max(3, int(height * (0.55 - u * 0.40)))
        pos_t = 0.30 + u * 0.70
        cx = int(root_x + (tip_x - root_x) * pos_t)
        cy = int(root_y + (tip_y - root_y) * pos_t)
        offset = int(height * 0.10 * (1 if i % 2 == 0 else -1))
        rect = pygame.Rect(cx - layer_w + offset, cy - 4, layer_w * 2, 8)
        # Back shadow (down-right, dark)
        pygame.draw.ellipse(surf, (15, 25, 12),
                            rect.move(1, 1).inflate(2, 2))
        # Original mid layer
        pygame.draw.ellipse(surf, pine_dk,  rect.inflate(2, 2))
        pygame.draw.ellipse(surf, pine_mid, rect)
        pygame.draw.ellipse(surf, pine_lt,  rect.inflate(-6, -4))
        # Front rim-light
        rim_rect = rect.move(rim_dx, -1).inflate(-8, -6)
        if rim_rect.width > 2 and rim_rect.height > 2:
            pygame.draw.ellipse(surf, (240, 255, 200), rim_rect)


def _emit_leaf(surf, anchor_x, anchor_y, palette, seed):
    """Single deterministic-phase falling leaf per pillar."""
    t = _CURRENT_T
    phase = (t * 0.18 + seed * 0.013) % 1.0
    fall_y = int(phase * 70)
    sway_x = int(math.sin(phase * 6 + seed * 0.1) * 12)
    lx = anchor_x + sway_x
    ly = anchor_y + fall_y
    if phase < 0.10:
        a = int(255 * phase / 0.10)
    elif phase > 0.85:
        a = int(255 * (1 - phase) / 0.15)
    else:
        a = 220
    color = (*palette['foliage_top'], a)
    leaf = pygame.Surface((6, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(leaf, color, leaf.get_rect())
    rot = math.degrees(phase * 6.28 + seed * 0.5)
    leaf_r = pygame.transform.rotate(leaf, rot)
    surf.blit(leaf_r, leaf_r.get_rect(center=(lx, ly)).topleft)


def _wrap_decorate_with_leaves(orig_dec, idx):
    def wrapper(surf, top_rect, bot_rect, palette, seed, *args, **kw):
        orig_dec(surf, top_rect, bot_rect, palette, seed, *args, **kw)
        anchor_x = bot_rect.x + bot_rect.width // 2
        anchor_y = bot_rect.y + 6
        _emit_leaf(surf, anchor_x, anchor_y, palette, seed + idx * 31)
    return wrapper


# ──────────────────────────────────────────────────────────────────────
# install_tier — context manager for all monkey-patches
# ──────────────────────────────────────────────────────────────────────
@contextlib.contextmanager
def install_tier(n: int):
    """Apply tier V1..Vn cumulative monkey-patches; restore on exit."""
    saved = []

    def _patch(module, attr, replacement):
        orig = getattr(module, attr)
        saved.append((module, attr, orig))
        setattr(module, attr, replacement)

    if n >= 1:
        _patch(gdraw, '_make_stone_pillar_body', _make_body_scaled)
        gdraw._pillar_body_cache.clear()
    if n >= 2:
        _patch(gdraw, '_make_stone_pillar_body', _make_body_v2)
    if n >= 3:
        # Capture originals these patches will call
        gdraw._ORIG_pillar_mist = gdraw.draw_pillar_mist
        gpv._ORIG_paper_lantern = gpv.draw_paper_lantern
        _patch(gpv, 'draw_prayer_flags', _v3_prayer_flags)
        _patch(gpv, 'draw_paper_lantern', _v3_paper_lantern)
        _patch(gdraw, 'draw_pillar_mist', _v3_pillar_mist)
        _patch(gpv, 'draw_cascading_vine', _v3_cascading_vine)
        # draw_moss_strand is exported from draw and re-imported by name
        # into pillar_variants — patch BOTH so all call sites pick up the
        # animated version.
        _patch(gdraw, 'draw_moss_strand', _v3_moss_strand)
        _patch(gpv, 'draw_moss_strand', _v3_moss_strand)
    if n >= 4:
        gpv._ORIG_spiral_glow = gpv.draw_spiral_glow
        gpv._ORIG_paint_stone = gpv._paint_stone
        _patch(gpv, 'draw_spiral_glow', _v4_spiral_glow)
        _patch(gpv, 'draw_paper_lantern', _v4_paper_lantern)
        _patch(gpv, '_paint_stone', _v4_paint_stone)
    if n >= 5:
        _patch(gdraw, 'draw_wuling_pine', _v5_wuling_pine)
        _patch(gpv, 'draw_wuling_pine', _v5_wuling_pine)
        # Wrap each variant's decorate fn to emit a falling leaf.
        new_variants = tuple(
            (top_sil, bot_sil, _wrap_decorate_with_leaves(dec, i))
            for i, (top_sil, bot_sil, dec) in enumerate(gpv._VARIANTS)
        )
        _patch(gpv, '_VARIANTS', new_variants)

    try:
        yield
    finally:
        for module, attr, orig in reversed(saved):
            setattr(module, attr, orig)
        gdraw._pillar_body_cache.clear()


# ──────────────────────────────────────────────────────────────────────
# Tier registry — used by the harness
# ──────────────────────────────────────────────────────────────────────
TIERS = {
    0: "0 — current",
    1: "1 — hi-res stone",
    2: "2 — + rim & grad",
    3: "3 — + animated",
    4: "4 — + sparkles",
    5: "5 — + cinematic",
}
