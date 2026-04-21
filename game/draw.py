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

def draw_mountains(surf, scroll, ground_y, w):
    # Far range
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
    pygame.draw.polygon(surf, MTN_FAR,  pts_far)
    pygame.draw.polygon(surf, MTN_NEAR, pts_near)


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

def draw_ground(surf, ground_y, w, h, scroll):
    # Grass strip
    grass_h = 22
    for i in range(grass_h):
        t = i / (grass_h - 1)
        c = lerp_color(GROUND_TOP, GROUND_MID, t)
        pygame.draw.line(surf, c, (0, ground_y + i), (w - 1, ground_y + i))

    # Dirt below
    for i in range(h - ground_y - grass_h):
        t = i / max(1, h - ground_y - grass_h - 1)
        c = lerp_color(GROUND_MID, GROUND_BOT, t)
        pygame.draw.line(surf, c, (0, ground_y + grass_h + i), (w - 1, ground_y + grass_h + i))

    # Grass blade highlights
    off = int(scroll * 0.7) % 30
    for gx in range(-off, w, 30):
        pygame.draw.line(surf, (100, 240, 100), (gx, ground_y), (gx - 4, ground_y - 8), 2)
        pygame.draw.line(surf, (100, 240, 100), (gx+12, ground_y), (gx+8, ground_y - 6), 2)
    # Ground edge highlight
    pygame.draw.line(surf, (140, 255, 140), (0, ground_y), (w-1, ground_y), 2)
