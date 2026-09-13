"""
Low-level drawing utilities: gradients, glow, rounded rects, etc.
All surfaces are pre-computed once and cached.
"""
import math
from collections import OrderedDict

import pygame

# ── colour constants ────────────────────────────────────────────────────────
SKY_TOP       = (12,  18,  55)
SKY_MID       = (25,  60, 130)
SKY_BOT       = (40, 140, 210)
HORIZON_GLOW  = (255, 200, 100)

GROUND_TOP    = ( 60, 190,  60)
GROUND_MID    = ( 30, 140,  30)
GROUND_BOT    = ( 80,  50,  20)

COIN_GOLD     = (255, 210,  20)
COIN_LIGHT    = (255, 245, 120)
COIN_DARK     = (200, 140,   0)

MUSH_CAP      = (125,  30,  45)   # velvet wine cone body
MUSH_CAP2     = (180,  60,  75)   # velvet highlight stripe
MUSH_SPOT     = (255, 235, 175)   # cream-butter ornament
MUSH_STEM     = (245, 230, 200)   # ivory stem

BIRD_RED      = (240,  55,  55)
BIRD_RED_D    = (170,  25,  25)
BIRD_WING     = ( 40, 100, 255)
BIRD_WING_D   = ( 20,  55, 180)
BIRD_TIP      = ( 50, 220, 100)
BIRD_BELLY    = (255, 170,  50)
BIRD_BEAK     = (255, 185,   0)
BIRD_BEAK_D   = (200, 130,   0)
WHITE         = (255, 255, 255)
BLACK         = (  0,   0,   0)
NEAR_BLACK    = ( 15,  15,  30)

UI_SCORE      = (255, 255, 255)
UI_GOLD       = (255, 215,   0)
UI_ORANGE     = (255, 155,  30)
UI_SHADOW     = (  0,   0,   0)
UI_CREAM      = (245, 230, 200)
UI_RED        = (230,  40,  40)

PARTICLE_GOLD = (255, 215,   0)
PARTICLE_ORNG = (255, 140,   0)
PARTICLE_WHT  = (255, 255, 220)
PARTICLE_CRIM = (220,  30,  30)


# ── gradient helpers ────────────────────────────────────────────────────────

def lerp_color(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


def lerp_color_multi(stops, t):
    """stops = [(t0,col0),(t1,col1),...] sorted ascending"""
    t = max(0.0, min(1.0, t))
    for i in range(len(stops)-1):
        t0, c0 = stops[i]
        t1, c1 = stops[i+1]
        if t <= t1:
            seg = (t - t0) / (t1 - t0) if t1 > t0 else 0
            return lerp_color(c0, c1, seg)
    return stops[-1][1]


def make_gradient_surface(w, h, stops, horizontal=False):
    surf = pygame.Surface((w, h))
    span = w if horizontal else h
    for i in range(span):
        c = lerp_color_multi(stops, i / max(1, span-1))
        if horizontal:
            pygame.draw.line(surf, c, (i, 0), (i, h-1))
        else:
            pygame.draw.line(surf, c, (0, i), (w-1, i))
    return surf


# ── glow helper ─────────────────────────────────────────────────────────────

def make_glow_surface(radius, color, alpha_center=180, falloff=1.8):
    """Pre-rendered radial glow. Blit with BLEND_ADD or BLEND_ALPHA_SDL2."""
    size = radius * 2 + 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = radius + 1
    for r in range(radius, 0, -1):
        t   = (r / radius) ** falloff
        a   = int(alpha_center * (1 - t))
        c   = (*color, max(0, min(255, a)))
        pygame.draw.circle(surf, c, (cx, cy), r)
    return surf


# ── rounded-rect helper ──────────────────────────────────────────────────────

def rounded_rect(surf, rect, radius, color, alpha=255):
    x, y, w, h = rect
    r = min(radius, w//2, h//2)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (0, 0, w, h), border_radius=r)
    surf.blit(s, (x, y))


def rounded_rect_grad(surf, rect, radius, top_color, bot_color):
    x, y, w, h = rect
    r = min(radius, w//2, h//2)
    for i in range(h):
        c = lerp_color(top_color, bot_color, i/max(1, h-1))
        pygame.draw.line(surf, c, (x, y+i), (x+w-1, y+i))
    # clip corners with a mask
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    pygame.draw.rect(mask, (255,255,255,255), (0,0,w,h), border_radius=r)
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    tmp.blit(surf.subsurface((x,y,w,h)), (0,0))
    tmp.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tmp, (x, y))


# ── background cache ─────────────────────────────────────────────────────────

_bg_cache: dict = {}


def get_sky_surface(w, h, ground_y):
    key = ('sky', w, h)
    if key not in _bg_cache:
        stops = [
            (0.0,  SKY_TOP),
            (0.35, SKY_MID),
            (0.75, SKY_BOT),
            (1.0,  (120, 195, 235)),
        ]
        _bg_cache[key] = make_gradient_surface(w, ground_y, stops)
    return _bg_cache[key]


# Bounded LRU for the biome sky surfaces, kept separate from `_bg_cache` so the
# count-based eviction can't drop the legacy static-sky entry. Only the two
# adjacent phase buckets are touched per frame, so a small cap holds RAM flat
# regardless of PHASE_BUCKETS. (This path is the dormant fallback — the live sky
# goes through sky_designs.render_active — but it stays bounded for safety.)
_SKY_B_CACHE_MAX = 6
_sky_b_cache: OrderedDict = OrderedDict()


def get_sky_surface_biome(w, h, ground_y, palette, phase_bucket):
    """Biome-aware sky: cached by quantized phase bucket."""
    key = ('sky_b', w, h, phase_bucket)
    cached = _sky_b_cache.get(key)
    if cached is not None:
        _sky_b_cache.move_to_end(key)
        return cached
    stops = [
        (0.0,  palette['sky_top']),
        (0.45, palette['sky_mid']),
        (0.85, palette['sky_bot']),
        (1.0,  palette['horizon']),
    ]
    surf = make_gradient_surface(w, ground_y, stops)

    # Sprinkle stars on dark skies. Positions are seeded by `w` only (not
    # `phase_bucket`) so all buckets share the same star layout — that lets
    # the scene fade between adjacent buckets without stars visibly jumping.
    sa = int(palette.get('star_alpha', 0))
    if sa > 0:
        import random as _r
        rng = _r.Random(w * 7919)
        star_band = int(ground_y * 0.72)
        n = 60 if sa > 180 else 30
        for _ in range(n):
            sx = rng.randint(0, w - 1)
            sy = rng.randint(0, star_band)
            sz = rng.choice((1, 1, 1, 2))
            col = (255, 255, 255, sa)
            pygame.draw.circle(surf, col, (sx, sy), sz)
        # Add a handful of warm-tinted brighter stars
        for _ in range(6):
            sx = rng.randint(0, w - 1)
            sy = rng.randint(0, star_band)
            col = (255, 240, 200, min(255, sa + 20))
            pygame.draw.circle(surf, col, (sx, sy), 2)

    _sky_b_cache[key] = surf
    if len(_sky_b_cache) > _SKY_B_CACHE_MAX:
        _sky_b_cache.popitem(last=False)
    return surf


# ── glow cache ───────────────────────────────────────────────────────────────

_glow_cache: dict = {}


def get_glow(radius, color, alpha=160):
    key = (radius, color, alpha)
    if key not in _glow_cache:
        _glow_cache[key] = make_glow_surface(radius, color, alpha)
    return _glow_cache[key]


def blit_glow(surf, cx, cy, radius, color, alpha=160):
    g = get_glow(radius, color, alpha)
    surf.blit(g, (cx - radius - 1, cy - radius - 1),
              special_flags=pygame.BLEND_ADD)


# ── mountain drawing ─────────────────────────────────────────────────────────

from game import mountains_v14


def draw_mountains(surf, scroll, ground_y, w, phase=0.02):
    """Live mountains = the V14 'Pagoda-Crowned Ridges' design (body lives in
    game/mountains_v14). Thin shim preserving the historical import surface so
    every existing `draw_mountains(...)` call site keeps working; `phase` drives
    the biome day/night retint."""
    mountains_v14.draw_mountains_v14(surf, scroll, ground_y, w, phase=phase)


# ── cloud drawing ────────────────────────────────────────────────────────────

from game import cloud_variants


def draw_cloud(surf, x, y, scale=1.0, variant: int = 0, palette=None):
    """Dispatch to one of the palette-aware shan-shui cloud variants (slots
    0..VARIANT_COUNT-1 in `cloud_variants._VARIANTS`). `palette` lets each cloud retint with
    the biome cycle; callers with no palette in scope (offline tools) fall back
    to the day palette so they keep rendering."""
    if palette is None:
        from game import biome  # lazy: biome imports draw.lerp_color (cycle)
        palette = biome.palette_for_phase(0.0)
    cloud_variants._VARIANTS[variant % cloud_variants.VARIANT_COUNT](
        surf, x, y, palette, scale)


# ── ground drawing ───────────────────────────────────────────────────────────

def draw_ground(surf, ground_y, w, h, scroll, top_color=None, mid_color=None, bot_color=None):
    # Dispatch to the run's chosen meadow variant. ``RUN_VARIANT_ID`` is
    # picked once per play in ``World.__init__`` via
    # ``ground_variants.set_run_seed(None)``.
    from game.ground_variants import draw_run_ground
    draw_run_ground(surf, ground_y, w, h, scroll,
                    top_color or GROUND_TOP,
                    mid_color or GROUND_MID,
                    bot_color or GROUND_BOT)


# ── Plant-family helpers (celadon foliage discipline + ink-wash trunk) ────────
#
# The plant primitives below draw ONLY the greenery; the pot/box is the caller's
# responsibility. They receive an ALREADY night-cooled `palette['foliage_*']`
# (callers retint via _fol), so their job is to stay in the foliage value band
# and keep every accent (blossom, stamen) below the foliage's own brightness so
# nothing can out-glow the coin once the foliage itself is capped at night.

_TRUNK = (60, 42, 28)
# Ink-wash trunk base hue — warm bark for the gnarled S-trunk, cooled toward the
# foliage at night so the trunk sits in the same value band as its canopy.
_TRUNK_INK = (92, 66, 44)


def _fol_lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _fol_night(palette):
    """Recover a 0..1 night-ness from the foliage the caller already cooled, so
    the primitives can darken hardcoded trunk/accent tones in lockstep without a
    separate `night` arg. Day foliage is bright + green; night foliage is dim +
    blue, so its top luma collapses — that drop IS the night signal."""
    top = palette.get('foliage_top', (140, 220, 110))
    return max(0.0, min(1.0, (175.0 - _fol_lum(top)) / 120.0))


def _trunk_tone(palette):
    """Ink-wash trunk, cooled + dimmed toward the foliage's night so it never
    stands brighter than the canopy it carries."""
    n = _fol_night(palette)
    return _mix_c(_TRUNK_INK, (56, 60, 90), 0.34 * n)


def _mix_c(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _shade_c(c, d):
    return (max(0, min(255, int(c[0] + d))),
            max(0, min(255, int(c[1] + d))),
            max(0, min(255, int(c[2] + d))))


def _accent_under_foliage(color, palette):
    """Cap an accent colour (blossom, stamen, vine bloom) below the foliage's
    OWN luminance ceiling and desaturate+darken it toward night, so a saturated
    red never rivals the coin once the foliage has already dropped under the cap.
    Day keeps the saturated pop; night collapses it ~35%."""
    n = _fol_night(palette)
    c = color
    if n > 0.02:
        c = _mix_c(c, _shade_c(c, -78), 0.42 * n)             # darken
        g = (int(_fol_lum(c)),) * 3
        c = _mix_c(c, g, 0.36 * n)                             # desaturate
        c = _mix_c(c, (62, 70, 96), 0.22 * n)                 # cool
    # Never let an accent out-read the brightest foliage pixel — AND hold it
    # under a hard day ceiling at ~0.9× the coin gold so even a fully saturated
    # day blossom keeps a clear margin below the coin (note 5: nothing out-glows
    # the coin, including against the brighter DAY gold).
    fol_ceil = _fol_lum(palette.get('foliage_top', (140, 220, 110))) + 12
    day_ceil = _fol_lum(COIN_GOLD) * 0.9
    ceil = min(fol_ceil, day_ceil)
    lum = _fol_lum(c)
    if lum > ceil and lum > 0:
        f = ceil / lum
        c = (int(c[0] * f), int(c[1] * f), int(c[2] * f))
    return c


def _bonsai_pads(surf, pads, dark, mid, top):
    """Cloud-pads each ringed with a 1px DARKER valley so neighbours don't merge
    into a blob at 1x. The keyline is the lighter foliage-dark valley (one line
    language shared with the flowering shrub)."""
    valley = _shade_c(dark, -22)
    for (cx, cy), tw, th in pads:
        pygame.draw.ellipse(surf, valley,
                            (cx - tw - 1, cy - th - 1, tw * 2 + 2, th * 2 + 2))
        pygame.draw.ellipse(surf, dark, (cx - tw, cy - th, tw * 2, th * 2))
        pygame.draw.ellipse(surf, mid,
                            (cx - tw + 1, cy - th + 1, tw * 2 - 3, th * 2 - 2))
        pygame.draw.ellipse(surf, top,
                            (cx - tw + 2, cy - th, max(2, tw - 2), max(2, th)))


def draw_wuling_pine(surf, root_x, root_y, height, palette,
                     lean=0, direction='up', layers=5):
    """Tiered ink-wash literati BONSAI-pine: a gnarled zig-zag S-trunk that kinks
    left/right/left as it climbs, crowned with 3 separated cloud-pads. Colours
    come from `palette['foliage_*']` so it retints with biome. The signature is
    unchanged; `height`/`lean`/`layers` still scale + tilt the silhouette so the
    pillar bases and the near-lane scale-up both read."""
    dark = palette['foliage_dark']
    mid  = palette['foliage_mid']
    top  = palette['foliage_top']
    trunk = _trunk_tone(palette)
    sign = -1 if direction == 'up' else 1
    h = max(14, height)
    s = h / 30.0                          # pad/kink scale relative to the base 30px
    base_y = root_y
    # A transitional mid-brown nub where the ink trunk meets the soil so it
    # plants into the pot instead of dissolving behind the rim.
    join = _shade_c(trunk, 16)
    pygame.draw.line(surf, join, (root_x - 1, base_y), (root_x + 1, base_y), 3)
    # Gnarled S-trunk: kink amplitude scales with lean so a leaning pillar pine
    # still reads as the same calligraphic gesture.
    kx = 1 + abs(lean) * 0.3
    pts = [
        (root_x + 1, base_y),
        (root_x - int(5 * kx) + lean // 3, base_y + sign * int(8 * s)),
        (root_x + int(4 * kx) + lean,      base_y + sign * int(15 * s)),
        (root_x - int(3 * kx) + lean,      base_y + sign * int(22 * s)),
        (root_x + int(5 * kx) + lean,      base_y + sign * int(29 * s)),
    ]
    pygame.draw.lines(surf, _shade_c(trunk, -28), False, pts, max(3, int(4 * s)))
    pygame.draw.lines(surf, trunk, False, pts, max(1, int(2 * s)))
    # A bare jutting deadwood twig — the literati signature.
    pygame.draw.line(surf, _shade_c(trunk, -12),
                     pts[1], (pts[1][0] - int(4 * s), pts[1][1] - int(3 * s)), 1)
    ty = base_y + sign * int(29 * s)
    th3 = max(2, int(3 * s))
    # Place 3 separated pads clustered around the canopy crown (pads climb in the
    # trunk's growth direction via `sign`). The topmost pad's day highlight is
    # held one value down (via the shaded _bonsai_pads top tone) so all tiers
    # share a single highlight ceiling and don't pull focus from the flower-shrub
    # red accent.
    pad_set = (
        ((root_x + lean - int(8 * s), ty - sign * int(2 * s)),
         max(4, int(9 * s)), th3),
        ((root_x + lean + int(8 * s), ty + sign * int(4 * s)),
         max(3, int(8 * s)), th3),
        ((root_x + lean + int(4 * s), ty + sign * int(9 * s)),
         max(3, int(6 * s)), th3),
    )
    _bonsai_pads(surf, pad_set, dark, mid, _shade_c(top, -10))


def draw_moss_strand(surf, x, y, length, palette, jitter_seed=0):
    """Short cascading moss vine hanging from a crack."""
    dark = palette['foliage_dark']
    mid  = palette['foliage_mid']
    top  = palette['foliage_top']
    accent = palette['foliage_accent']
    for i in range(length):
        yy = y + i
        jitter = int(math.sin((i + jitter_seed) * 0.45) * 1.2)
        col = lerp_color(dark, mid, i / max(1, length))
        pygame.draw.line(surf, col, (x + jitter, yy), (x + jitter, yy + 1), 1)
    tip_y = y + length
    bulb = max(5, length // 3)
    pygame.draw.ellipse(surf, dark, (x - bulb // 2, tip_y - bulb // 2, bulb, bulb))
    pygame.draw.ellipse(surf, mid,  (x - bulb // 2 + 1, tip_y - bulb // 2, bulb - 2, bulb - 1))
    pygame.draw.ellipse(surf, top,  (x - bulb // 2 + 2, tip_y - bulb // 2, max(2, bulb - 5), max(2, bulb - 5)))
    pygame.draw.circle(surf, accent, (x + 2, tip_y - bulb // 3), 2)


_BLOSSOM_TINTS = ((228, 96, 132), (236, 120, 158), (222, 78, 104),
                  (240, 150, 178))


def draw_side_shrub(surf, x, y, palette, scale=1.0):
    """A two-value FLOWERING SHRUB: a lobed dark-green base mass, then 3-5
    DISTINCT lighter blossom clusters (tight rosettes, not scattered confetti).
    `y` is the base; the dome grows upward. Day keeps a saturated red pop; night
    desaturates+darkens the blooms so they never rival the coin (every accent is
    routed through _accent_under_foliage). Signature unchanged so the pillar-base
    and near-lane callers keep working at 0.9× up to ~1.9×."""
    dark = palette['foliage_dark']
    mid  = palette['foliage_mid']
    s = scale
    top_y = y - 1
    # Lobed dark base mass — overlapping domes for a natural shrub read. Outline
    # is the lighter foliage-dark keyline (shared line language with the bonsai).
    domes = ((-int(5 * s), -int(12 * s), int(9 * s), int(8 * s)),
             (int(5 * s),  -int(14 * s), int(9 * s), int(8 * s)),
             (0,           -int(17 * s), int(8 * s), int(7 * s)))
    for dx, dy, rw, rh in domes:
        cx, cy = x + dx, top_y + dy
        pygame.draw.ellipse(surf, dark, (cx - rw, cy - rh, rw * 2, rh * 2))
        pygame.draw.ellipse(surf, mid,
                            (cx - rw + 1, cy - rh + 1, rw * 2 - 3, rh * 2 - 2))
    # 3-5 discrete blossom clusters — each a 5-petal rosette (dark ring + lit
    # cap + a tiny golden stamen). Counts scale a touch with size.
    spots = ((-int(6 * s), -int(15 * s)), (int(6 * s), -int(17 * s)),
             (0, -int(21 * s)), (int(2 * s), -int(12 * s)))
    n_blooms = 3 if s < 0.85 else 4
    for i in range(n_blooms):
        bx, byp = x + spots[i][0], top_y + spots[i][1]
        base = _BLOSSOM_TINTS[i % len(_BLOSSOM_TINTS)]
        core = _accent_under_foliage(base, palette)
        cap = _accent_under_foliage(_shade_c(base, 34), palette)
        rr = max(1, int(2 * s))
        for k in range(5):
            a = k * (math.tau / 5) - 0.3
            px = bx + int(math.cos(a) * rr)
            py = byp + int(math.sin(a) * rr * 0.8)
            pygame.draw.circle(surf, _shade_c(core, -34), (px, py), 1)
        pygame.draw.circle(surf, core, (bx, byp), max(1, rr - 1))
        pygame.draw.circle(surf, cap, (bx, byp), 0)
        pygame.draw.circle(surf, _accent_under_foliage((255, 226, 150), palette),
                           (bx, byp), 0)


def draw_pillar_mist(surf, cx, base_y, width, alpha=110):
    """Soft fog halo around the base of a pillar where it meets the ground."""
    layers = [(width * 4, 32, alpha // 3),
              (width * 3, 22, alpha // 2),
              (width * 2, 14, alpha)]
    for w, h, a in layers:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (255, 255, 255, a), s.get_rect())
        surf.blit(s, (cx - w // 2, base_y - h // 2 + 4))
