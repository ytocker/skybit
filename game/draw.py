"""
Low-level drawing utilities: gradients, glow, rounded rects, etc.
All surfaces are pre-computed once and cached.
"""
import math
import pygame

# ── colour constants ────────────────────────────────────────────────────────
SKY_TOP       = (12,  18,  55)
SKY_MID       = (25,  60, 130)
SKY_BOT       = (40, 140, 210)
HORIZON_GLOW  = (255, 200, 100)

MTN_FAR       = (35,  45, 100)
MTN_NEAR      = (22,  30,  72)

GROUND_TOP    = ( 60, 190,  60)
GROUND_MID    = ( 30, 140,  30)
GROUND_BOT    = ( 80,  50,  20)

PIPE_HILIGHT  = (110, 240, 110)
PIPE_MID      = ( 45, 185,  45)
PIPE_DARK     = ( 20, 100,  20)
PIPE_SHADOW   = ( 12,  60,  12)

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


def get_sky_surface_biome(w, h, ground_y, palette, phase_bucket):
    """Biome-aware sky: cached by quantized phase bucket."""
    key = ('sky_b', w, h, phase_bucket)
    cached = _bg_cache.get(key)
    if cached is not None:
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

    _bg_cache[key] = surf
    return surf


def get_pipe_body_gradient(w, h):
    key = ('pipebody', w, h)
    if key not in _bg_cache:
        stops = [
            (0.0,  PIPE_HILIGHT),
            (0.18, PIPE_MID),
            (0.55, PIPE_DARK),
            (0.82, PIPE_DARK),
            (1.0,  PIPE_SHADOW),
        ]
        _bg_cache[key] = make_gradient_surface(w, h, stops, horizontal=True)
    return _bg_cache[key]


def get_pipe_cap_gradient(w, h):
    key = ('pipecap', w, h)
    if key not in _bg_cache:
        stops = [
            (0.0,  PIPE_HILIGHT),
            (0.12, PIPE_MID),
            (0.50, PIPE_DARK),
            (0.88, PIPE_DARK),
            (1.0,  PIPE_SHADOW),
        ]
        _bg_cache[key] = make_gradient_surface(w, h, stops, horizontal=True)
    return _bg_cache[key]


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

def draw_mountains(surf, scroll, ground_y, w, far_color=None, near_color=None):
    far_color  = far_color  or MTN_FAR
    near_color = near_color or MTN_NEAR
    # Tint the back layer halfway between sky-bottom-ish and far colour so
    # it reads as genuinely further away without needing a new palette key.
    back_color = (
        max(0, min(255, (far_color[0] + 200) // 2)),
        max(0, min(255, (far_color[1] + 210) // 2)),
        max(0, min(255, (far_color[2] + 230) // 2)),
    )
    pts_back = [(0, ground_y)]
    pts_far  = [(0, ground_y)]
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
    pygame.draw.polygon(surf, far_color,  pts_far)
    pygame.draw.polygon(surf, near_color, pts_near)


# ── cloud drawing ────────────────────────────────────────────────────────────

# Five hand-tuned cloud puff layouts: (ox, oy, radius, alpha). Each column in
# the list is one variant, so scenes that draw multiple clouds can pick
# different variants via modulo.
_CLOUD_VARIANTS: list[list[tuple[float, float, float, int]]] = [
    # V0 — classic wide, 5-bump
    [(0, 0, 22, 230), (28, -6, 28, 235), (56, 0, 20, 225),
     (14, 10, 18, 220), (42, 10, 18, 220)],
    # V1 — narrow tall, 4-bump with a tall centre
    [(0, 2, 18, 220), (22, -8, 24, 235), (40, 0, 20, 225),
     (16, 12, 16, 215)],
    # V2 — long stretched wisp, 6-bump
    [(0, 4, 16, 205), (18, -2, 22, 230), (38, -6, 22, 235),
     (58, -2, 20, 225), (78, 4, 14, 205), (28, 12, 16, 215)],
    # V3 — compact puff, 3-bump almost round
    [(0, 2, 22, 230), (20, -8, 26, 235), (42, 4, 18, 220)],
    # V4 — asymmetric, heavy on the left
    [(0, -4, 26, 235), (26, 2, 22, 228), (48, -2, 18, 222),
     (12, 14, 18, 215), (36, 14, 14, 205)],
]


def draw_cloud(surf, x, y, scale=1.0, variant: int = 0):
    """Draw a stylised cloud. `variant` picks one of the hand-tuned shapes
    so scenes don't paint the same 5-circle blob repeatedly. Each puff is
    composited with its OWN alpha (from the variant tuple), giving the
    cloud soft edges where small puffs overlap larger ones."""
    puffs = _CLOUD_VARIANTS[variant % len(_CLOUD_VARIANTS)]
    for ox, oy, r, a in puffs:
        rr = max(2, int(r * scale))
        s = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, a), (rr + 1, rr + 1), rr)
        surf.blit(s, (int(x + ox * scale) - rr - 1,
                      int(y + oy * scale) - rr - 1))
    # No underside shadow band — that solid-fill rectangle read as a hard
    # blue bar pinned to the cloud's bottom rather than as soft shading.


# ── ground drawing ───────────────────────────────────────────────────────────

def draw_ground(surf, ground_y, w, h, scroll, top_color=None, mid_color=None, bot_color=None):
    top_color = top_color or GROUND_TOP
    mid_color = mid_color or GROUND_MID
    bot_color = bot_color or GROUND_BOT

    # Grass strip
    grass_h = 22
    for i in range(grass_h):
        t = i / (grass_h - 1)
        c = lerp_color(top_color, mid_color, t)
        pygame.draw.line(surf, c, (0, ground_y + i), (w - 1, ground_y + i))

    # Dirt below
    for i in range(h - ground_y - grass_h):
        t = i / max(1, h - ground_y - grass_h - 1)
        c = lerp_color(mid_color, bot_color, t)
        pygame.draw.line(surf, c, (0, ground_y + grass_h + i), (w - 1, ground_y + grass_h + i))

    # Grass blade highlights (brighter tint of top color)
    blade_col = (
        min(255, top_color[0] + 40),
        min(255, top_color[1] + 40),
        min(255, top_color[2] + 40),
    )
    edge_col = (
        min(255, top_color[0] + 60),
        min(255, top_color[1] + 60),
        min(255, top_color[2] + 60),
    )
    off = int(scroll * 0.7) % 30
    for gx in range(-off, w, 30):
        pygame.draw.line(surf, blade_col, (gx, ground_y), (gx - 4, ground_y - 8), 2)
        pygame.draw.line(surf, blade_col, (gx + 12, ground_y), (gx + 8, ground_y - 6), 2)
    pygame.draw.line(surf, edge_col, (0, ground_y), (w - 1, ground_y), 2)


# ── Stone pillar drawing ────────────────────────────────────────────────────

def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _make_stone_pillar_body(w, h, light, mid, dark, accent, body_seed=0):
    """Quartzite column: vertical striations + erosion fissures,
    warm sunlit side → cool shadow side, no mid-column banding. `body_seed`
    shifts the pseudo-random crack layout so adjacent pillars don't share
    horizontal seam heights (REVIEW.md finding)."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # Horizontal cylinder shading (sunlit left → shadow right).
    for x in range(w):
        t = x / max(1, w - 1)
        if t < 0.18:
            c = lerp_color(mid, light, (0.18 - t) / 0.18)
        elif t < 0.55:
            seg = (t - 0.18) / 0.37
            c = lerp_color(light, mid, seg * seg * (3 - 2 * seg))
        else:
            seg = (t - 0.55) / 0.45
            c = lerp_color(mid, dark, seg * seg * (3 - 2 * seg))
        pygame.draw.line(surf, c, (x, 0), (x, h - 1))

    # Warm accent highlight stripe along the sunlit side (subtle).
    accent_surf = pygame.Surface((3, h), pygame.SRCALPHA)
    accent_surf.fill((*accent, 90))
    surf.blit(accent_surf, (int(w * 0.14), 0))

    # Vertical erosion striations — long thin grooves.
    import random as _r
    rng = _r.Random(w * 7919 + h + body_seed * 6151)
    for _ in range(4):
        gx = rng.randint(3, w - 4)
        col = _shade(dark, -10)
        pygame.draw.line(surf, col, (gx, 0), (gx, h - 1), 1)
    # Occasional horizontal crack for erosion realism.
    crack_step = 80
    ystart = rng.randint(10, crack_step)
    for cy in range(ystart, h - 10, crack_step):
        jitter = rng.randint(-3, 3)
        col = _shade(dark, -20)
        pygame.draw.line(surf, col, (2, cy + jitter), (w - 3, cy + jitter + rng.randint(-1, 1)), 1)
        # Tiny bright pebble flecks just below the crack
        pygame.draw.line(surf, light, (rng.randint(4, w - 5), cy + jitter + 1),
                         (rng.randint(4, w - 5), cy + jitter + 2), 1)

    return surf


_pillar_body_cache: dict = {}


def get_stone_pillar_body(w, h, light, mid, dark, accent, body_seed=0):
    # Quantize very-tall heights so we don't re-cache tiny differences.
    # Bucket body_seed to 8 distinct layouts so the cache stays finite.
    qh = ((h + 7) // 8) * 8
    bucket = body_seed % 8
    key = (w, qh, light, mid, dark, accent, bucket)
    s = _pillar_body_cache.get(key)
    if s is None or s.get_height() < h:
        s = _make_stone_pillar_body(w, max(qh, h), light, mid, dark, accent, bucket)
        _pillar_body_cache[key] = s
    return s.subsurface((0, 0, w, h))


# ── Template A: Slender Spire silhouettes ──────────────────────────────────

def silhouette_bottom_spire(w, h):
    """Bottom-pillar silhouette polygon: tapers to a single asymmetric peak
    at the top (y=0). Width `w`, height `h`. Coords are local to the rect."""
    s = w / 90.0
    pkR = (w // 2 + max(2, int(s * 12)), 0)
    pkL = (w // 2 - max(2, int(s * 8)),  0)
    right_taper = [
        (w - max(1, int(s * 18)), int(s * 18)),
        (w - max(1, int(s * 6)),  int(s * 40)),
        (w - max(1, int(s * 4)),  int(s * 80)),
        (w,                       int(s * 130)),
    ]
    left_taper = [
        (0,                  int(s * 130)),
        (max(1, int(s * 8)), int(s * 80)),
        (max(1, int(s * 14)), int(s * 40)),
        (max(1, int(s * 24)), int(s * 18)),
    ]
    rs = [pt for pt in right_taper if pt[1] < h]
    ls = [pt for pt in left_taper  if pt[1] < h]
    return [pkR] + rs + [(w, h), (0, h)] + ls + [pkL]


def silhouette_top_spire(w, h):
    """Top-pillar silhouette polygon: hangs from the ceiling (y=0) and
    tapers to an asymmetric downward fang at y=h."""
    s = w / 90.0
    pkR = (w // 2 + max(2, int(s * 10)), h)
    pkL = (w // 2 - max(2, int(s * 6)),  h)
    right_taper = [
        (w,                        h - int(s * 50)),
        (w - max(1, int(s * 4)),   h - int(s * 22)),
        (w - max(1, int(s * 14)),  h - int(s * 8)),
    ]
    left_taper = [
        (max(1, int(s * 16)), h - int(s * 8)),
        (max(1, int(s * 4)),  h - int(s * 22)),
        (0,                   h - int(s * 50)),
    ]
    rs = [pt for pt in right_taper if pt[1] > 0]
    ls = [pt for pt in left_taper  if pt[1] > 0]
    return [(0, 0), (w, 0)] + rs + [pkR, pkL] + ls


def silhouette_blit(target, body, polygon, top_left, shadow_alpha=110):
    """Mask a stone-body surface to a silhouette polygon and blit to `target`
    at `top_left`. Includes a soft drop shadow and a dark outline."""
    w, h = body.get_size()
    if shadow_alpha > 0:
        sh_surf = pygame.Surface((w + 8, h + 6), pygame.SRCALPHA)
        pygame.draw.polygon(sh_surf, (0, 0, 0, shadow_alpha),
                            [(p[0] + 4, p[1] + 3) for p in polygon])
        target.blit(sh_surf, (top_left[0] - 2, top_left[1] + 1))
    masked = body.copy()
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), polygon)
    masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    target.blit(masked, top_left)
    pygame.draw.polygon(target, (40, 28, 22),
                        [(p[0] + top_left[0], p[1] + top_left[1]) for p in polygon], 1)


# ── Wuling pine + moss strand ────────────────────────────────────────────────

_TRUNK = (60, 42, 28)


def draw_wuling_pine(surf, root_x, root_y, height, palette,
                     lean=0, direction='up', layers=5):
    """Stylised Wuling pine — narrow trunk + horizontal peacock-tail canopy.
    Colors come from `palette['foliage_*']` so the tree retints with biome."""
    pine_dk  = palette['foliage_dark']
    pine_mid = palette['foliage_mid']
    pine_lt  = palette['foliage_top']
    sign = -1 if direction == 'up' else 1
    tip_x = root_x + lean
    tip_y = root_y + sign * height
    pygame.draw.line(surf, _TRUNK, (root_x, root_y), (tip_x, tip_y), 2)
    for i in range(layers):
        t = i / max(1, layers - 1)
        layer_w = max(3, int(height * (0.55 - t * 0.40)))
        pos_t = 0.30 + t * 0.70
        cx = int(root_x + (tip_x - root_x) * pos_t)
        cy = int(root_y + (tip_y - root_y) * pos_t)
        offset = int(height * 0.10 * (1 if i % 2 == 0 else -1))
        rect = pygame.Rect(cx - layer_w + offset, cy - 4, layer_w * 2, 8)
        pygame.draw.ellipse(surf, pine_dk,  rect.inflate(2, 2))
        pygame.draw.ellipse(surf, pine_mid, rect)
        pygame.draw.ellipse(surf, pine_lt,  rect.inflate(-6, -4))


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


def draw_side_shrub(surf, x, y, palette, scale=1.0):
    """A small dome of leaves clinging to the rock face."""
    dark = palette['foliage_dark']
    mid  = palette['foliage_mid']
    top  = palette['foliage_top']
    rw = max(6, int(10 * scale))
    rh = max(4, int(6 * scale))
    pygame.draw.ellipse(surf, dark, (x - rw, y - rh, rw * 2, rh * 2))
    pygame.draw.ellipse(surf, mid,  (x - rw + 2, y - rh + 1, rw * 2 - 4, rh * 2 - 2))
    pygame.draw.ellipse(surf, top,  (x - rw + 4, y - rh,     rw * 2 - 8, max(2, rh)))


def draw_pillar_mist(surf, cx, base_y, width, alpha=110):
    """Soft fog halo around the base of a pillar where it meets the ground."""
    layers = [(width * 4, 32, alpha // 3),
              (width * 3, 22, alpha // 2),
              (width * 2, 14, alpha)]
    for w, h, a in layers:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (255, 255, 255, a), s.get_rect())
        surf.blit(s, (cx - w // 2, base_y - h // 2 + 4))
