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

MUSH_CAP      = (220,  30,  30)
MUSH_CAP2     = (255,  70,  50)
MUSH_SPOT     = (255, 255, 255)
MUSH_STEM     = (245, 225, 195)

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

    # Sprinkle stars on dark skies. Deterministic via phase bucket.
    sa = int(palette.get('star_alpha', 0))
    if sa > 0:
        import random as _r
        rng = _r.Random(phase_bucket * 7919 + w)
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
    pts_far  = [(0, ground_y)]
    pts_near = [(0, ground_y)]
    for x in range(0, w + 1, 2):
        fx = x + scroll * 0.15
        hf = int(80 + math.sin(fx * 0.012) * 42 + math.sin(fx * 0.031) * 22)
        pts_far.append((x, ground_y - hf))
        nx = x + scroll * 0.28
        hn = int(55 + math.sin(nx * 0.019 + 1.4) * 34 + math.sin(nx * 0.047 + 0.7) * 16)
        pts_near.append((x, ground_y - hn))
    pts_far.append((w, ground_y))
    pts_near.append((w, ground_y))
    pygame.draw.polygon(surf, far_color,  pts_far)
    pygame.draw.polygon(surf, near_color, pts_near)


# ── cloud drawing ────────────────────────────────────────────────────────────

def draw_cloud(surf, x, y, scale=1.0):
    def _circ(ox, oy, r, a=220):
        s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255,255,255,a), (r+1,r+1), r)
        surf.blit(s, (int(x+ox*scale)-r-1, int(y+oy*scale)-r-1))
    ri = int
    _circ(0,     0,  ri(22*scale), 230)
    _circ(28*scale,  -6*scale, ri(28*scale), 235)
    _circ(56*scale,   0,       ri(20*scale), 225)
    _circ(14*scale,  10*scale, ri(18*scale), 220)
    _circ(42*scale,  10*scale, ri(18*scale), 220)
    # Soft shadow underside
    shadow = pygame.Surface((int(80*scale), int(14*scale)), pygame.SRCALPHA)
    shadow.fill((130, 170, 220, 60))
    surf.blit(shadow, (int(x), int(y + 14*scale)))


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


# ── Zhangjiajie-style stone pillar drawing ──────────────────────────────────

def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _make_stone_pillar_body(w, h, light, mid, dark, accent):
    """Zhangjiajie quartzite column: vertical striations + erosion fissures,
    warm sunlit side → cool shadow side, no mid-column banding. The surface
    tapers slightly at the top but we leave that to the caller's rect."""
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
    rng = _r.Random(w * 7919 + h)
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


def get_stone_pillar_body(w, h, light, mid, dark, accent):
    # Quantize very-tall heights so we don't re-cache tiny differences.
    qh = ((h + 7) // 8) * 8
    key = (w, qh, light, mid, dark, accent)
    s = _pillar_body_cache.get(key)
    if s is None or s.get_height() < h:
        s = _make_stone_pillar_body(w, max(qh, h), light, mid, dark, accent)
        _pillar_body_cache[key] = s
    return s.subsurface((0, 0, w, h))


def _draw_tree_silhouette(surf, cx, base_y, palette, size, direction='up'):
    """A stylised tree / shrub silhouette. direction='up' grows upward from
    base_y; 'down' grows downward (used on the hanging top pillar)."""
    top = palette['foliage_top']
    mid = palette['foliage_mid']
    dark = palette['foliage_dark']
    accent = palette['foliage_accent']

    sign = -1 if direction == 'up' else 1

    # Trunk
    trunk_h = int(size * 0.45)
    trunk = pygame.Rect(int(cx - 1), int(base_y if sign < 0 else base_y),
                        3, trunk_h)
    if sign < 0:
        trunk = pygame.Rect(int(cx - 1), int(base_y - trunk_h), 3, trunk_h)
    pygame.draw.rect(surf, (70, 50, 35), trunk)

    # Foliage cluster: three overlapping ellipses
    cluster_y = base_y - int(size * 0.55) * (1 if sign < 0 else 0)
    if sign > 0:
        cluster_y = base_y + int(size * 0.3)
    ellipses = [
        (cx - int(size * 0.35), cluster_y - int(size * 0.10), int(size * 0.55), int(size * 0.45)),
        (cx + int(size * 0.20), cluster_y - int(size * 0.25), int(size * 0.50), int(size * 0.40)),
        (cx + int(size * 0.05), cluster_y + int(size * 0.05), int(size * 0.60), int(size * 0.45)),
    ]
    # Dark base layer
    for ex, ey, rw, rh in ellipses:
        pygame.draw.ellipse(surf, dark, (ex - rw // 2, ey - rh // 2, rw, rh))
    # Mid layer (slightly inset)
    for ex, ey, rw, rh in ellipses:
        pygame.draw.ellipse(surf, mid, (ex - rw // 2 + 2, ey - rh // 2 + 1, rw - 4, rh - 2))
    # Bright top layer (sunlit)
    for ex, ey, rw, rh in ellipses:
        pygame.draw.ellipse(surf, top, (ex - rw // 2 + 4, ey - rh // 2 - 2, rw - 10, max(3, rh - 8)))
    # Accent specks (flowers / berries)
    for ex, ey, rw, rh in ellipses:
        pygame.draw.circle(surf, accent, (ex + rw // 4, ey - rh // 3), 2)


def draw_foliage_crown(surf, cx, cy, width, palette, direction='up'):
    """Lush vegetation crown on the gap-facing end of a stone pillar.
    direction='up' → foliage grows upward (bottom pillar's top).
    direction='down' → foliage hangs down (top pillar's bottom)."""

    # Rocky summit strip just before the foliage
    plate_col = palette['stone_light']
    plate = pygame.Rect(int(cx - width // 2 - 4), int(cy - 4 if direction == 'up' else cy),
                        width + 8, 6)
    pygame.draw.rect(surf, plate_col, plate, border_radius=3)
    pygame.draw.line(surf, palette['stone_dark'],
                     (plate.x, plate.y + plate.height - 1),
                     (plate.right, plate.y + plate.height - 1), 1)

    if direction == 'up':
        # Three trees / shrubs of varying size, rooted on the plate
        base_y = plate.y
        _draw_tree_silhouette(surf, cx - width // 3, base_y, palette, size=36, direction='up')
        _draw_tree_silhouette(surf, cx + width // 4, base_y, palette, size=30, direction='up')
        _draw_tree_silhouette(surf, cx,              base_y, palette, size=42, direction='up')
        # Low shrubs along the plate edge
        for dx in (-width // 2 + 6, width // 2 - 6):
            pygame.draw.ellipse(surf, palette['foliage_dark'],
                                (cx + dx - 8, base_y - 6, 16, 10))
            pygame.draw.ellipse(surf, palette['foliage_mid'],
                                (cx + dx - 6, base_y - 7, 12, 8))
    else:
        # Hanging vines / moss clumps from the bottom end
        base_y = plate.y + plate.height
        # Three cascading moss clumps with vines underneath
        clumps = [
            (cx - width // 3, 28, 14),
            (cx + width // 4, 34, 16),
            (cx,              40, 18),
            (cx - width // 6, 22, 12),
            (cx + width // 6 + 4, 26, 12),
        ]
        for mx, mh, mw in clumps:
            # Vine strand
            for i in range(mh):
                yy = base_y + i
                jitter = int(math.sin(i * 0.4 + mx * 0.1) * 1.5)
                col = lerp_color(palette['foliage_dark'], palette['foliage_mid'], i / max(1, mh))
                pygame.draw.line(surf, col, (mx + jitter, yy), (mx + jitter, yy + 1), 1)
            # Bulb at the tip
            tip_y = base_y + mh
            pygame.draw.ellipse(surf, palette['foliage_dark'],
                                (mx - mw // 2, tip_y - mw // 2, mw, mw))
            pygame.draw.ellipse(surf, palette['foliage_mid'],
                                (mx - mw // 2 + 2, tip_y - mw // 2, mw - 4, mw - 2))
            pygame.draw.ellipse(surf, palette['foliage_top'],
                                (mx - mw // 2 + 3, tip_y - mw // 2, mw - 7, max(2, mw - 8)))
            # Accent flower/berry
            pygame.draw.circle(surf, palette['foliage_accent'],
                               (mx + 2, tip_y - mw // 3), 2)
