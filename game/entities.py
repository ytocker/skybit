"""
Game entities: Bird, Pipe, Coin, Mushroom, Particle, FloatText.
All drawing is smooth (gradients, alpha, glows) — no pixel art.

Pipes are nature-pillar style and re-tint with the active biome palette.
Coins have a bold embossed star for clarity. The mushroom uses a pulsing
magenta halo and a much higher-contrast cap.
"""
import math
import random
import pygame

from game.config import (
    W, H, GRAVITY, FLAP_V, MAX_FALL,
    BIRD_X, BIRD_R, PIPE_W, COIN_R, MUSHROOM_R, GROUND_Y,
)
from game.draw import (
    blit_glow, get_pillar_body, draw_pillar_bands, draw_pillar_leaves,
    rounded_rect, lerp_color,
    COIN_GOLD, COIN_LIGHT, COIN_DARK,
    MUSH_CAP, MUSH_CAP2, MUSH_SPOT, MUSH_STEM,
    PIPE_HILIGHT, PIPE_MID, PIPE_DARK, PIPE_SHADOW,
    PARTICLE_GOLD, PARTICLE_ORNG, PARTICLE_WHT, PARTICLE_CRIM,
    WHITE, NEAR_BLACK,
)
from game import parrot


# Default pillar palette (fallback when no biome provided)
_DEFAULT_PILLAR = {
    'pillar_light': PIPE_HILIGHT,
    'pillar_mid':   PIPE_MID,
    'pillar_dark':  PIPE_DARK,
    'pillar_band':  (255, 240, 160),
    'pillar_leaf':  (90, 200, 100),
}


# ── Bird ─────────────────────────────────────────────────────────────────────

class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = H * 0.42
        self.vy = 0.0
        self.alive = True
        self.frame_t = 0.0
        self.flap_boost = 0.0
        self.trail: list[tuple[float, float]] = []

    @property
    def tilt_deg(self):
        t = max(-0.5, min(1.1, self.vy / 500.0))
        return -t * 55.0

    def flap(self):
        if self.alive:
            self.vy = FLAP_V
            self.flap_boost = 0.45

    def update(self, dt):
        self.vy = min(self.vy + GRAVITY * dt, MAX_FALL)
        self.y += self.vy * dt
        if len(self.trail) == 0 or (self.x - self.trail[-1][0]) ** 2 + (self.y - self.trail[-1][1]) ** 2 > 16:
            self.trail.append((self.x, self.y))
            if len(self.trail) > 8:
                self.trail.pop(0)

        base_hz = 9.0 + self.flap_boost * 20.0
        if self.vy < -100:
            base_hz += 3.0
        elif self.vy > 200:
            base_hz = max(3.0, base_hz - 4.0)
        self.frame_t = (self.frame_t + dt * base_hz)
        self.flap_boost = max(0.0, self.flap_boost - dt * 1.8)

    def draw(self, surf, shake_x=0, shake_y=0):
        for i, (tx, ty) in enumerate(self.trail[:-1]):
            a = int(40 * (i + 1) / len(self.trail))
            if a <= 0:
                continue
            s = pygame.Surface((26, 26), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 90, 90, a), (13, 13), 11)
            surf.blit(s, (tx - 13 + shake_x, ty - 13 + shake_y), special_flags=pygame.BLEND_ADD)

        frame_idx = int(self.frame_t) % len(parrot.FRAMES)
        img = parrot.get_parrot(frame_idx, self.tilt_deg)
        r = img.get_rect(center=(self.x + shake_x, self.y + shake_y))
        surf.blit(img, r.topleft)


# ── Pipe (nature pillar) ─────────────────────────────────────────────────────

class Pipe:
    CAP_H = 22

    def __init__(self, x: float, gap_y: float, gap_h: float):
        self.x = x
        self.gap_y = gap_y
        self.gap_h = gap_h
        self.scored = False

    @property
    def top_rect(self):
        return pygame.Rect(int(self.x), 0, PIPE_W, int(self.gap_y - self.gap_h / 2))

    @property
    def bot_rect(self):
        top = int(self.gap_y + self.gap_h / 2)
        return pygame.Rect(int(self.x), top, PIPE_W, GROUND_Y - top)

    def off_screen(self):
        return self.x + PIPE_W + 8 < 0

    def collides_circle(self, cx, cy, r):
        return self.top_rect.colliderect(pygame.Rect(cx - r, cy - r, r * 2, r * 2)) or \
               self.bot_rect.colliderect(pygame.Rect(cx - r, cy - r, r * 2, r * 2))

    def _draw_segment(self, surf, rect: pygame.Rect, palette):
        if rect.height <= 0:
            return
        light = palette['pillar_light']
        mid   = palette['pillar_mid']
        dark  = palette['pillar_dark']
        band  = palette['pillar_band']

        # Soft drop shadow
        shadow = pygame.Surface((rect.width + 12, rect.height + 8), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 90), (6, 4, rect.width, rect.height), border_radius=5)
        surf.blit(shadow, (rect.x - 3, rect.y + 2))

        # Pillar body (cylinder shading, cached)
        body = get_pillar_body(rect.width, max(1, rect.height), light, mid, dark)
        surf.blit(body, rect.topleft)

        # Glowing horizontal bands with central gem
        draw_pillar_bands(surf, rect, band, light, spacing=44)

        # Bright left edge and dark right edge for sculpted feel
        pygame.draw.line(surf, light, (rect.x + 1, rect.y), (rect.x + 1, rect.y + rect.height), 1)
        pygame.draw.line(surf, dark,  (rect.x + rect.width - 2, rect.y),
                         (rect.x + rect.width - 2, rect.y + rect.height), 1)

    def _draw_cap(self, surf, cy_top, palette, direction='down'):
        """Draw the ornate crown cap. direction='down' → cap on a top pillar
        (leaves droop downward into the gap). 'up' → cap on bottom pillar."""
        light = palette['pillar_light']
        mid   = palette['pillar_mid']
        dark  = palette['pillar_dark']
        band  = palette['pillar_band']
        leaf  = palette['pillar_leaf']

        cap_w = PIPE_W + 14
        cap_x = int(self.x - 7)
        cap_rect = pygame.Rect(cap_x, int(cy_top), cap_w, self.CAP_H)

        # Shadow
        shadow = pygame.Surface((cap_rect.width + 12, cap_rect.height + 8), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 100), (6, 4, cap_rect.width, cap_rect.height), border_radius=7)
        surf.blit(shadow, (cap_rect.x - 3, cap_rect.y + 2))

        # Body
        cap = get_pillar_body(cap_rect.width, cap_rect.height, light, mid, dark).copy()
        mask = pygame.Surface(cap.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=7)
        cap.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(cap, cap_rect.topleft)

        # Bright top highlight strip
        hi = pygame.Surface((cap_rect.width - 8, 3), pygame.SRCALPHA)
        hi.fill((*light, 220))
        surf.blit(hi, (cap_rect.x + 4, cap_rect.y + 3))

        # Central gem stamp on the cap
        cx = cap_rect.x + cap_rect.width // 2
        cy = cap_rect.y + cap_rect.height // 2
        pygame.draw.circle(surf, dark, (cx, cy), 4)
        pygame.draw.circle(surf, band, (cx, cy), 3)
        blit_glow(surf, cx, cy, 10, band, 180)

        # Leaves / fern tufts along the edge facing the gap
        leaf_y = cap_rect.y + cap_rect.height if direction == 'down' else cap_rect.y
        draw_pillar_leaves(surf, cx, leaf_y, leaf, cap_rect.width, direction=direction)

    def draw(self, surf, palette=None):
        palette = palette or _DEFAULT_PILLAR
        tr = self.top_rect
        br = self.bot_rect
        self._draw_segment(surf, tr, palette)
        self._draw_segment(surf, br, palette)
        self._draw_cap(surf, tr.bottom - self.CAP_H, palette, direction='down')
        self._draw_cap(surf, br.top,                 palette, direction='up')


# ── Coin ─────────────────────────────────────────────────────────────────────

def _build_star(r, color):
    """Pre-render a 5-pointed star into an SRCALPHA surface."""
    size = r * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = r + 1
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        radius = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(ang) * radius, cy + math.sin(ang) * radius))
    pygame.draw.polygon(s, color, pts)
    return s


_STAR_CACHE: dict = {}


def _get_star(r, color):
    key = (r, color)
    s = _STAR_CACHE.get(key)
    if s is None:
        s = _build_star(r, color)
        _STAR_CACHE[key] = s
    return s


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spin = random.uniform(0, math.tau)
        self.collected = False
        self.float_t = random.uniform(0, math.tau)

    def update(self, dt):
        self.spin = (self.spin + dt * 4.0) % math.tau
        self.float_t += dt

    def draw(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.float_t * 2.2) * 2)
        # Outer glow
        blit_glow(surf, cx, cy, COIN_R + 12, COIN_GOLD, 170)
        blit_glow(surf, cx, cy, COIN_R + 6,  COIN_LIGHT, 130)

        rx = max(2, int(abs(math.cos(self.spin)) * COIN_R))
        ry = COIN_R

        # Outline ring (dark, high contrast)
        pygame.draw.ellipse(surf, NEAR_BLACK, (cx - rx - 2, cy - ry - 2, (rx + 2) * 2, (ry + 2) * 2))
        # Dark edge
        pygame.draw.ellipse(surf, COIN_DARK, (cx - rx - 1, cy - ry - 1, (rx + 1) * 2, (ry + 1) * 2))
        # Gold face
        pygame.draw.ellipse(surf, COIN_GOLD, (cx - rx, cy - ry, rx * 2, ry * 2))
        # Bright upper-left arc highlight
        pygame.draw.ellipse(surf, COIN_LIGHT, (cx - rx + 1, cy - ry + 2, max(2, rx - 1), max(2, ry - 4)))

        # Embossed star when mostly face-on; side view shows a dark band
        if rx > COIN_R * 0.55:
            star_r = max(3, int(rx * 0.55))
            # shadow
            sh = _get_star(star_r, (*COIN_DARK, 255))
            surf.blit(sh, (cx - star_r, cy - star_r + 1))
            # bright face
            fg = _get_star(star_r - 1, (*COIN_LIGHT, 255))
            surf.blit(fg, (cx - (star_r - 1), cy - (star_r - 1)))
        else:
            # Side-on: single dark stripe
            pygame.draw.line(surf, COIN_DARK, (cx - rx + 1, cy), (cx + rx - 1, cy), 2)

        # Pinprick white glint
        pygame.draw.circle(surf, WHITE, (cx - max(1, rx - 3), cy - ry + 3), 1)


# ── Mushroom ─────────────────────────────────────────────────────────────────

class Mushroom:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.pulse = 0.0

    def update(self, dt):
        self.pulse += dt * 3.5

    def draw(self, surf):
        cx = int(self.x)
        cy = int(self.y)
        # Double halo: warm outer + magenta inner
        outer_r = MUSHROOM_R + 14 + int(math.sin(self.pulse) * 4)
        inner_r = MUSHROOM_R + 6  + int(math.sin(self.pulse * 1.4) * 2)
        blit_glow(surf, cx, cy - 4, outer_r, (255, 230, 160), 160)
        blit_glow(surf, cx, cy - 4, inner_r, (255,  90, 180), 170)

        # Stem with vivid highlight
        stem = pygame.Rect(cx - 7, cy, 14, 13)
        rounded_rect(surf, stem, 5, MUSH_STEM, 255)
        pygame.draw.line(surf, (255, 255, 230), (cx - 4, cy + 2), (cx - 4, cy + 11), 2)
        pygame.draw.line(surf, (200, 180, 145), (cx + 3, cy + 2), (cx + 3, cy + 11), 1)
        # Stem base shadow
        sh = pygame.Surface((16, 4), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 120), sh.get_rect())
        surf.blit(sh, (cx - 8, cy + 11))

        # Cap shadow (under)
        cap_rect = pygame.Rect(cx - MUSHROOM_R - 1, cy - MUSHROOM_R + 2, (MUSHROOM_R + 1) * 2, MUSHROOM_R + 5)
        sh = pygame.Surface((cap_rect.width + 8, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 130), sh.get_rect())
        surf.blit(sh, (cap_rect.x - 4, cy - 2))

        # Cap base (deep crimson outline) then vivid red
        pygame.draw.ellipse(surf, (130, 10, 20), cap_rect.inflate(2, 2))
        pygame.draw.ellipse(surf, MUSH_CAP,     cap_rect)
        # Upper highlight arc (hot pink / orange)
        hi = pygame.Rect(cap_rect.x + 3, cap_rect.y + 2, cap_rect.width - 6, 7)
        pygame.draw.ellipse(surf, MUSH_CAP2, hi)
        # Specular sheen
        sh2 = pygame.Surface((cap_rect.width - 14, 3), pygame.SRCALPHA)
        pygame.draw.ellipse(sh2, (255, 230, 220, 200), sh2.get_rect())
        surf.blit(sh2, (cap_rect.x + 7, cap_rect.y + 3))

        # Spots with a soft ring so they read clearly
        for sx, sy, sr in ((cx - 7, cy - 5, 3),
                           (cx + 6, cy - 7, 4),
                           (cx + 2, cy + 1, 3),
                           (cx - 3, cy + 2, 2)):
            pygame.draw.circle(surf, (220, 190, 200), (sx, sy), sr + 1)
            pygame.draw.circle(surf, MUSH_SPOT,       (sx, sy), sr)


# ── Particle ─────────────────────────────────────────────────────────────────

class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "life_max", "r", "color", "gravity")

    def __init__(self, x, y, vx, vy, life, r, color, gravity=900.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.life_max = life
        self.r = r
        self.color = color
        self.gravity = gravity

    def update(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, self.life / self.life_max)
        a = int(255 * t)
        rr = max(1, int(self.r * (0.4 + 0.6 * t)))
        s = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, a), (rr + 1, rr + 1), rr)
        surf.blit(s, (int(self.x - rr - 1), int(self.y - rr - 1)), special_flags=pygame.BLEND_ADD)


# ── FloatText ────────────────────────────────────────────────────────────────

_float_font_cache: dict = {}


def _get_float_font(size, bold=True):
    key = (size, bold)
    f = _float_font_cache.get(key)
    if f is None:
        f = pygame.font.SysFont("arial", size, bold=bold)
        _float_font_cache[key] = f
    return f


class FloatText:
    __slots__ = ("text", "x", "y", "vy", "life", "life_max", "color", "size")

    def __init__(self, text, x, y, color, size=22, life=1.0, vy=-60):
        self.text = text
        self.x = x
        self.y = y
        self.vy = vy
        self.life = life
        self.life_max = life
        self.color = color
        self.size = size

    def update(self, dt):
        self.y += self.vy * dt
        self.vy += 40.0 * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, self.life / self.life_max)
        a = int(255 * min(1.0, t * 2))
        font = _get_float_font(self.size)
        shadow = font.render(self.text, True, NEAR_BLACK)
        text = font.render(self.text, True, self.color)
        shadow.set_alpha(a)
        text.set_alpha(a)
        r = text.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(shadow, (r.x + 2, r.y + 2))
        surf.blit(text, r.topleft)
