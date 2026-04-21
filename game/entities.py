"""
Game entities: Bird, Pipe, Coin, Mushroom, Particle, FloatText.
All drawing is smooth (gradients, alpha, glows) — no pixel art.
"""
import math
import random
import pygame

from game.config import (
    W, H, GRAVITY, FLAP_V, MAX_FALL,
    BIRD_X, BIRD_R, PIPE_W, COIN_R, MUSHROOM_R, GROUND_Y,
)
from game.draw import (
    blit_glow, get_pipe_body_gradient, get_pipe_cap_gradient,
    rounded_rect, lerp_color,
    COIN_GOLD, COIN_LIGHT, COIN_DARK,
    MUSH_CAP, MUSH_CAP2, MUSH_SPOT, MUSH_STEM,
    PIPE_HILIGHT, PIPE_MID, PIPE_DARK, PIPE_SHADOW,
    PARTICLE_GOLD, PARTICLE_ORNG, PARTICLE_WHT, PARTICLE_CRIM,
    WHITE, NEAR_BLACK,
)
from game import parrot


# ── Bird ─────────────────────────────────────────────────────────────────────

class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = H * 0.42
        self.vy = 0.0
        self.alive = True
        self.frame_t = 0.0       # animation timer
        self.flap_boost = 0.0    # temp speed-up of wing flap on input
        self.trail: list[tuple[float, float]] = []

    @property
    def tilt_deg(self):
        # Up when rising, down when falling (negative deg = nose-up in pygame coords)
        t = max(-0.5, min(1.1, self.vy / 500.0))
        # Rotate: nose-up (-) when t<0, nose-down (+) when t>0
        return -t * 55.0

    def flap(self):
        if self.alive:
            self.vy = FLAP_V
            self.flap_boost = 0.45

    def update(self, dt):
        self.vy = min(self.vy + GRAVITY * dt, MAX_FALL)
        self.y += self.vy * dt
        # trail sample
        if len(self.trail) == 0 or (self.x - self.trail[-1][0]) ** 2 + (self.y - self.trail[-1][1]) ** 2 > 16:
            self.trail.append((self.x, self.y))
            if len(self.trail) > 8:
                self.trail.pop(0)

        # flap animation speed: faster just after flap / when rising
        base_hz = 9.0 + self.flap_boost * 20.0
        if self.vy < -100:
            base_hz += 3.0
        elif self.vy > 200:
            base_hz = max(3.0, base_hz - 4.0)
        self.frame_t = (self.frame_t + dt * base_hz)
        self.flap_boost = max(0.0, self.flap_boost - dt * 1.8)

    def draw(self, surf, shake_x=0, shake_y=0):
        # trail echoes
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


# ── Pipe ─────────────────────────────────────────────────────────────────────

class Pipe:
    CAP_H = 24

    def __init__(self, x: float, gap_y: float, gap_h: float):
        self.x = x
        self.gap_y = gap_y      # center of the gap
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

    def _draw_segment(self, surf, rect: pygame.Rect):
        if rect.height <= 0:
            return
        # Soft drop shadow
        shadow = pygame.Surface((rect.width + 10, rect.height + 6), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 0))
        pygame.draw.rect(shadow, (0, 0, 0, 70), (5, 3, rect.width, rect.height), border_radius=6)
        surf.blit(shadow, (rect.x - 2, rect.y + 2))

        # Body with horizontal gradient
        body = get_pipe_body_gradient(rect.width, max(1, rect.height))
        surf.blit(body, rect.topleft)

        # Rivet highlight lines
        pygame.draw.line(surf, PIPE_HILIGHT, (rect.x + 6, rect.y), (rect.x + 6, rect.y + rect.height), 2)
        pygame.draw.line(surf, PIPE_SHADOW, (rect.x + rect.width - 4, rect.y),
                         (rect.x + rect.width - 4, rect.y + rect.height), 2)

    def _draw_cap(self, surf, cx, cy_top):
        cap_w = PIPE_W + 12
        cap_x = int(self.x - 6)
        cap_rect = pygame.Rect(cap_x, int(cy_top), cap_w, self.CAP_H)

        # Shadow
        shadow = pygame.Surface((cap_rect.width + 10, cap_rect.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 80), (5, 3, cap_rect.width, cap_rect.height), border_radius=6)
        surf.blit(shadow, (cap_rect.x - 2, cap_rect.y + 2))

        cap = get_pipe_cap_gradient(cap_rect.width, cap_rect.height).copy()
        mask = pygame.Surface(cap.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=6)
        cap.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(cap, cap_rect.topleft)

        # top highlight strip
        hi = pygame.Surface((cap_rect.width - 6, 4), pygame.SRCALPHA)
        hi.fill((*PIPE_HILIGHT, 180))
        surf.blit(hi, (cap_rect.x + 3, cap_rect.y + 3))

    def draw(self, surf):
        tr = self.top_rect
        br = self.bot_rect
        self._draw_segment(surf, tr)
        self._draw_segment(surf, br)
        # caps
        self._draw_cap(surf, self.x + PIPE_W / 2, tr.bottom - self.CAP_H)
        self._draw_cap(surf, self.x + PIPE_W / 2, br.top)


# ── Coin ─────────────────────────────────────────────────────────────────────

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
        # Glow
        blit_glow(surf, cx, cy, COIN_R + 8, COIN_GOLD, 130)
        rx = max(2, int(abs(math.cos(self.spin)) * COIN_R))
        ry = COIN_R
        # Disc body
        pygame.draw.ellipse(surf, COIN_DARK, (cx - rx - 1, cy - ry - 1, (rx + 1) * 2, (ry + 1) * 2))
        pygame.draw.ellipse(surf, COIN_GOLD, (cx - rx, cy - ry, rx * 2, ry * 2))
        # Highlight
        pygame.draw.ellipse(surf, COIN_LIGHT, (cx - rx + 1, cy - ry + 2, max(2, rx), max(2, ry - 3)))
        # Star stamp when face-on
        if rx > COIN_R * 0.7:
            pygame.draw.line(surf, COIN_DARK, (cx - rx + 3, cy), (cx + rx - 3, cy), 1)


# ── Mushroom ─────────────────────────────────────────────────────────────────

class Mushroom:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.pulse = 0.0

    def update(self, dt):
        self.pulse += dt * 3.0

    def draw(self, surf):
        cx = int(self.x)
        cy = int(self.y)
        halo_r = MUSHROOM_R + 8 + int(math.sin(self.pulse) * 3)
        blit_glow(surf, cx, cy - 4, halo_r, (255, 240, 200), 150)

        # Stem
        stem = pygame.Rect(cx - 6, cy, 12, 12)
        rounded_rect(surf, stem, 4, MUSH_STEM, 255)
        pygame.draw.line(surf, (220, 200, 165), (cx - 4, cy + 2), (cx - 4, cy + 10), 2)

        # Cap (half-ellipse)
        cap_rect = pygame.Rect(cx - MUSHROOM_R, cy - MUSHROOM_R + 2, MUSHROOM_R * 2, MUSHROOM_R + 4)
        # shadow under cap
        sh = pygame.Surface((cap_rect.width + 6, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 100), sh.get_rect())
        surf.blit(sh, (cap_rect.x - 3, cy - 2))

        pygame.draw.ellipse(surf, MUSH_CAP, cap_rect)
        # upper highlight
        hi = pygame.Rect(cap_rect.x + 3, cap_rect.y + 2, cap_rect.width - 6, 6)
        pygame.draw.ellipse(surf, MUSH_CAP2, hi)
        # spots
        pygame.draw.circle(surf, MUSH_SPOT, (cx - 6, cy - 4), 3)
        pygame.draw.circle(surf, MUSH_SPOT, (cx + 5, cy - 6), 4)
        pygame.draw.circle(surf, MUSH_SPOT, (cx + 2, cy + 1), 3)


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
