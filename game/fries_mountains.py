"""KFC powerup fries-mountains: 3 variants randomly picked per activation.

When the KFC powerup is active, the background mountain silhouettes
get swapped for piles of French fries. The variant pool below holds
the 3 picked designs - one is chosen at random per `_activate_kfc`
call (see World.kfc_mountain_variant) and used for the duration of
that powerup window.

Variants:
    0  Classic Spilled Fries  dense scatter of golden fry sticks at
                              varied tilts filling the silhouette
    1  Fries Box Skyline      red+white striped fries cartons with
                              fries poking out the top, varied heights
    2  Curly Fry Spirals      dense scatter of spring-shaped curls
                              filling the silhouette

All variants keep the existing 3-layer parallax shape + scroll
multipliers (back x0.06 / far x0.15 / near x0.28) from
game.draw.draw_mountains so the depth feel is preserved - only the
silhouette content changes. Each layer is rendered to its own
Surface so PlayScene can blit them with independent parallax offsets,
matching the depth feel of the normal mountains.
"""
import math
import random

import pygame

from game.pillar_kfc import (
    OUTLINE, KFC_RED, KFC_RED_D, KFC_WHITE,
)


# Parallax multipliers - must match game.draw.draw_mountains so the
# fries pile drifts at the same depth-cued speed as normal mountains.
PARALLAX_SPEEDS = (0.06, 0.15, 0.28)

# How much extra width each cached layer carries beyond the screen so
# parallax scroll never runs past the rendered content during a single
# KFC buff window. SCROLL_BASE (~160 px/s) x KFC_DURATION (8s) x max
# parallax (0.28) = 358 px, rounded up with headroom.
CACHE_PAD = 420


# --- Palette extensions for fries -----------------------------------------

FRY_LIGHT = (252, 220, 130)
FRY_GOLD  = (244, 192,  82)
FRY_DEEP  = (200, 140,  40)
SALT      = (252, 248, 240)


def _layer_shade(color, layer):
    """Tint a colour for the 3 parallax layers.
    layer=0 (back): heavily faded toward sky
    layer=1 (far):  lightly faded
    layer=2 (near): unchanged
    """
    if layer == 0:
        mix = (180, 160, 200)
        return tuple(int((color[i] + mix[i]) / 2) for i in range(3))
    if layer == 1:
        mix = (210, 180, 200)
        return tuple(int(color[i] * 0.72 + mix[i] * 0.28) for i in range(3))
    return color


def _outline_for_layer(layer):
    if layer == 0:
        return (90, 70, 90)
    if layer == 1:
        return (60, 36, 18)
    return OUTLINE


# --- Horizon shape (mirrors draw_mountains) -------------------------------

def horizon_y(x, ground_y, layer):
    """y-coordinate of the silhouette top at world-x for the given layer.
    Matches the sine stack used by game.draw.draw_mountains - scroll is
    handled at blit time by parallax-shifting the cached Surface, so
    each cache is rendered at scroll=0."""
    if layer == 0:
        h = 105 + math.sin(x * 0.008) * 32 + math.sin(x * 0.023 + 2.1) * 14
    elif layer == 1:
        h = 80 + math.sin(x * 0.012) * 42 + math.sin(x * 0.031) * 22
    else:
        h = 55 + math.sin(x * 0.019 + 1.4) * 34 + math.sin(x * 0.047 + 0.7) * 16
    return int(ground_y - h)


# --- Single-fry sprite ----------------------------------------------------

def _make_fry_sprite(length, fw, light, gold, deep, outline, salt_dots, seed):
    """Build one fry sprite (axis-aligned) at native size."""
    pad = 2
    s = pygame.Surface((length + pad * 2, fw + pad * 2), pygame.SRCALPHA)
    rect = pygame.Rect(pad, pad, length, fw)
    radius = max(2, fw // 2)
    pygame.draw.rect(s, outline, rect.inflate(2, 2), border_radius=radius)
    pygame.draw.rect(s, deep, rect.inflate(0, 0), border_radius=radius)
    pygame.draw.rect(s, gold, rect.inflate(-1, -1), border_radius=radius)
    hl = pygame.Rect(rect.x + 2, rect.y + 1,
                     max(2, rect.width - 4), max(1, fw // 3))
    pygame.draw.rect(s, light, hl, border_radius=max(1, fw // 4))
    if salt_dots:
        rng = random.Random(seed)
        for _ in range(salt_dots):
            sx = rng.randint(rect.left + 2, rect.right - 2)
            sy = rng.randint(rect.top + 1, rect.bottom - 1)
            s.set_at((sx, sy), SALT)
    return s


def draw_fry(surf, cx, cy, length, *, tilt_deg=0,
              light=FRY_LIGHT, gold=FRY_GOLD, deep=FRY_DEEP,
              outline=OUTLINE, salt_dots=0, seed=0):
    """A golden fry stick at native render resolution. Rounded ends +
    optional rotation. No supersampling - we trade a touch of pixel
    grain for a ~10x faster cache build."""
    fw = max(3, length // 6)
    sprite = _make_fry_sprite(length, fw, light, gold, deep, outline,
                               salt_dots, seed)
    if tilt_deg:
        sprite = pygame.transform.rotate(sprite, tilt_deg)
    rect = sprite.get_rect(center=(cx, cy))
    surf.blit(sprite, rect.topleft)


# --- Curly fry sprite -----------------------------------------------------

def draw_curly_fry(surf, cx, cy, *, radius=14, turns=2.2, color=FRY_GOLD,
                    deep=FRY_DEEP, outline=OUTLINE, light=FRY_LIGHT,
                    tilt_deg=0):
    """Spring-shaped fry curl drawn as a polyline along a spiral."""
    size = radius * 2 + 12
    layer = pygame.Surface((size, size), pygame.SRCALPHA)
    cx_l, cy_l = size // 2, size // 2
    n = max(24, int(turns * 18))
    pts = []
    for i in range(n):
        u = i / max(1, n - 1)
        a = u * turns * 2 * math.pi
        r = radius * (0.45 + 0.55 * u)
        x = cx_l + math.cos(a) * r
        y = cy_l + math.sin(a) * r * 0.55
        pts.append((x, y))
    if len(pts) >= 2:
        pygame.draw.lines(layer, outline, False, pts, 7)
        pygame.draw.lines(layer, deep, False, pts, 5)
        pygame.draw.lines(layer, color, False, pts, 4)
        hi_pts = [(p[0], p[1] - 1) for p in pts]
        pygame.draw.lines(layer, light, False, hi_pts, 1)
    if tilt_deg:
        layer = pygame.transform.rotate(layer, tilt_deg)
    rect = layer.get_rect(center=(cx, cy))
    surf.blit(layer, rect.topleft)


# --- Fries carton (McD-style) ---------------------------------------------

def draw_fry_carton(surf, base_x, base_y, w_top, h, *,
                     stripe_color=KFC_RED, stripe_count=5,
                     outline=OUTLINE, layer_idx=2):
    """Trapezoid fries carton with red+white stripes. base_x/base_y is
    the BOTTOM-CENTRE; returns rim_y so the caller can stack fries
    on top."""
    bot_w = max(int(w_top * 0.75), 16)
    rim_y = base_y - h
    tl = (base_x - w_top // 2, rim_y)
    tr = (base_x + w_top // 2, rim_y)
    br = (base_x + bot_w // 2, base_y)
    bl = (base_x - bot_w // 2, base_y)
    poly = [tl, tr, br, bl]
    pygame.draw.polygon(surf, outline,
                        [(p[0], p[1] + 1) for p in poly])
    white = _layer_shade(KFC_WHITE, layer_idx)
    pygame.draw.polygon(surf, white, poly)
    red = _layer_shade(stripe_color, layer_idx)
    for i in range(stripe_count):
        u0 = (i + 0.10) / stripe_count
        u1 = (i + 0.58) / stripe_count
        sx0_top = tl[0] + (tr[0] - tl[0]) * u0
        sx1_top = tl[0] + (tr[0] - tl[0]) * u1
        sx0_bot = bl[0] + (br[0] - bl[0]) * u0
        sx1_bot = bl[0] + (br[0] - bl[0]) * u1
        pygame.draw.polygon(
            surf, red,
            [(sx0_top, tl[1]), (sx1_top, tl[1]),
             (sx1_bot, br[1]), (sx0_bot, br[1])])
    pygame.draw.polygon(surf, outline, poly, 2)
    rim_band = pygame.Rect(tl[0] - 2, rim_y - 4, w_top + 4, 7)
    pygame.draw.rect(surf, outline, rim_band.inflate(2, 2), border_radius=3)
    pygame.draw.rect(surf, _layer_shade(KFC_RED_D, layer_idx),
                      rim_band, border_radius=3)
    pygame.draw.rect(surf, red, rim_band.inflate(-4, -3), border_radius=2)
    return rim_y


# ============================================================================
# Variant 0: Classic Spilled Fries
# ============================================================================

def _classic_layer(surf, ground_y, w, layer):
    fry_light = _layer_shade(FRY_LIGHT, layer)
    fry_gold = _layer_shade(FRY_GOLD, layer)
    fry_deep = _layer_shade(FRY_DEEP, layer)
    outline = _outline_for_layer(layer)
    rng = random.Random(layer * 1337 + 7)
    n_fries = (150, 230, 360)[layer]
    length_range = ((8, 14), (12, 22), (16, 30))[layer]
    salt_dots = (0, 1, 2)[layer]
    fries = []
    for _ in range(n_fries):
        x = rng.randint(-12, w + 12)
        hy = horizon_y(x, ground_y, layer)
        if hy >= ground_y:
            continue
        y = rng.randint(hy, ground_y - 1)
        tilt = rng.uniform(-85, 85)
        L = rng.randint(*length_range)
        fries.append((y, x, L, tilt))
    fries.sort(key=lambda f: -f[0])
    for (y, x, L, tilt) in fries:
        draw_fry(surf, x, y, L, tilt_deg=tilt,
                  light=fry_light, gold=fry_gold, deep=fry_deep,
                  outline=outline, salt_dots=salt_dots,
                  seed=x * 7 + y * 11 + layer)


# ============================================================================
# Variant 1: Fries Box Skyline
# ============================================================================

def _boxes_layer(surf, ground_y, w, layer):
    spacing = (60, 50, 44)[layer]
    carton_w_range = ((34, 50), (38, 56), (42, 64))[layer]
    fry_count_range = ((4, 6), (5, 8), (6, 10))[layer]
    rng = random.Random(layer * 99 + 7)
    outline = _outline_for_layer(layer)
    fry_light = _layer_shade(FRY_LIGHT, layer)
    fry_gold = _layer_shade(FRY_GOLD, layer)
    fry_deep = _layer_shade(FRY_DEEP, layer)
    x = -spacing // 2
    while x < w + spacing // 2:
        hy = horizon_y(x, ground_y, layer)
        carton_h = ground_y - hy + rng.randint(-6, 6)
        carton_h = max(40, carton_h)
        c_w = rng.randint(*carton_w_range)
        rim_y = draw_fry_carton(surf, x, ground_y, c_w, carton_h,
                                  layer_idx=layer)
        n_fries = rng.randint(*fry_count_range)
        fry_max_len = (16, 22, 30)[layer]
        for _ in range(n_fries):
            off = rng.uniform(-c_w / 2 + 4, c_w / 2 - 4)
            tilt = rng.uniform(-30, 30)
            L = rng.randint(fry_max_len - 6, fry_max_len)
            draw_fry(surf, int(x + off), rim_y - L // 2 + 2, L,
                      tilt_deg=tilt + 90,
                      light=fry_light, gold=fry_gold, deep=fry_deep,
                      outline=outline, salt_dots=0)
        x += spacing + rng.randint(-8, 8)


# ============================================================================
# Variant 2: Curly Fry Spirals
# ============================================================================

def _curly_layer(surf, ground_y, w, layer):
    light = _layer_shade(FRY_LIGHT, layer)
    gold = _layer_shade(FRY_GOLD, layer)
    deep = _layer_shade(FRY_DEEP, layer)
    outline = _outline_for_layer(layer)
    rng = random.Random(layer * 311 + 11)
    n_curls = (90, 140, 220)[layer]
    radius_range = ((4, 8), (6, 11), (9, 14))[layer]
    curls = []
    for _ in range(n_curls):
        x = rng.randint(-12, w + 12)
        hy = horizon_y(x, ground_y, layer)
        if hy >= ground_y:
            continue
        y = rng.randint(hy, ground_y - 1)
        r = rng.randint(*radius_range)
        tilt = rng.uniform(-45, 45)
        turns = rng.uniform(1.6, 2.6)
        curls.append((y, x, r, tilt, turns))
    curls.sort(key=lambda c: -c[0])
    for (y, x, r, tilt, turns) in curls:
        draw_curly_fry(surf, x, y, radius=r, turns=turns,
                        color=gold, deep=deep, outline=outline,
                        light=light, tilt_deg=tilt)


# ============================================================================
# Dispatcher + cache build/blit
# ============================================================================

LAYER_DRAWERS = (
    _classic_layer,
    _boxes_layer,
    _curly_layer,
)

# Public count - World picks an index into this range.
KFC_MOUNTAIN_DRAWERS = LAYER_DRAWERS  # back-compat alias


def make_fries_mountain_cache(variant_idx, ground_y, w):
    """Pre-render one fries-mountain variant to three per-layer Surfaces
    so PlayScene can blit them each frame at the same parallax depths
    as the normal mountains. Returns a tuple of 3 Surfaces (back,
    far, near) each (w + CACHE_PAD) wide so the layer can scroll for
    the full KFC buff window without exposing un-rendered edge.

    Heavy — 7-37 ms per variant. Use ``get_cached_mountain`` for the
    per-pickup hot path so the actual build runs at most once per
    variant for the whole session.
    """
    layer_fn = LAYER_DRAWERS[variant_idx % len(LAYER_DRAWERS)]
    cache_w = w + CACHE_PAD
    layers = []
    for layer_idx in (0, 1, 2):
        s = pygame.Surface((cache_w, ground_y + 8), pygame.SRCALPHA)
        layer_fn(s, ground_y, cache_w, layer_idx)
        layers.append(s)
    return layers


# Per-variant memo of built layers. Each entry is a list of 3 Surfaces
# (back/far/near) or ``None`` if that variant has never been built yet.
# Keyed by (variant_idx, ground_y, w) so the cache stays valid even if
# screen geometry changes between sessions (it doesn't today, but the
# explicit key makes the invariant obvious).
_VARIANT_CACHE: dict = {}


def get_cached_mountain(variant_idx, ground_y, w):
    """Return the per-layer Surfaces for ``variant_idx``, building on
    first request and reusing thereafter. Called from
    ``World._activate_kfc`` so KFC pickup is O(1) (cache hit) instead
    of triggering a 7-37 ms build mid-game."""
    key = (variant_idx % len(LAYER_DRAWERS), ground_y, w)
    cached = _VARIANT_CACHE.get(key)
    if cached is None:
        cached = make_fries_mountain_cache(variant_idx, ground_y, w)
        _VARIANT_CACHE[key] = cached
    return cached


def prewarm_all(ground_y, w):
    """Build every variant's per-layer cache. Call once during app
    startup (under the HTML splash) so the first KFC pickup in-game
    has zero build cost."""
    for v in range(len(LAYER_DRAWERS)):
        get_cached_mountain(v, ground_y, w)


def blit_fries_mountains(surf, caches, scroll_offset):
    """Blit the per-layer fries caches parallax-shifted by
    `scroll_offset` (the bg_scroll delta since the buff activated).
    Each layer shifts at its own parallax speed so the depth feel
    matches the normal mountains. Layers are blitted back-to-front
    so the near pile reads in front of the far/back ones."""
    for layer_idx, cache in enumerate(caches):
        ox = -int(scroll_offset * PARALLAX_SPEEDS[layer_idx])
        surf.blit(cache, (ox, 0))
