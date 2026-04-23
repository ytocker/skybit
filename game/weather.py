"""
Biome-driven weather: rain streaks, lightning flashes, fog, wind-blown leaves.

Weather is keyed to `biome_phase` rather than `biome_time` so it follows the
sky. Everything is procedural — particle-style rain streaks, a cached fog
gradient, and a brief full-surface alpha pulse for lightning.
"""
from __future__ import annotations

import math
import random

import pygame

from game.config import W, H, GROUND_Y
from game import audio


# ── phase → intensity curves ────────────────────────────────────────────────

def _bump(phase: float, center: float, width: float) -> float:
    """Smooth bump peaking at `center` and fading over ±width. Returns 0..1."""
    d = abs(((phase - center + 0.5) % 1.0) - 0.5)
    if d >= width:
        return 0.0
    t = 1.0 - d / width
    return t * t * (3 - 2 * t)  # smoothstep


def rain_intensity(phase: float) -> float:
    """Rain: amber-warm at sunset (0.32), cool-blue at dusk (0.48),
    sparse at night (0.62)."""
    a = _bump(phase, 0.35, 0.12) * 0.55   # sunset drizzle
    b = _bump(phase, 0.50, 0.10) * 1.00   # dusk storm
    c = _bump(phase, 0.62, 0.10) * 0.45   # night residual
    return max(0.0, min(1.0, a + b + c))


def rain_color(phase: float):
    """Blend between warm amber (sunset) and cool slate (dusk/night)."""
    warm = (255, 200, 140)
    cool = (140, 170, 220)
    # Closer to 0.35 → warmer; closer to 0.50+ → cooler
    t_cool = min(1.0, max(0.0, (phase - 0.35) / 0.2))
    return (
        int(warm[0] + (cool[0] - warm[0]) * t_cool),
        int(warm[1] + (cool[1] - warm[1]) * t_cool),
        int(warm[2] + (cool[2] - warm[2]) * t_cool),
    )


def lightning_active(phase: float) -> bool:
    """Lightning only during the night window."""
    return 0.55 <= phase <= 0.72


def fog_intensity(phase: float) -> float:
    """Patchy fog peaks in predawn (0.78), fades by sunrise (0.90)."""
    return _bump(phase, 0.80, 0.10) * 0.9


def wind_intensity(phase: float) -> float:
    """Golden-hour wind (0.18) — drifting leaves."""
    return _bump(phase, 0.18, 0.10) * 1.0


# ── particle: a single rain streak ──────────────────────────────────────────

class _Streak:
    __slots__ = ("x", "y", "vx", "vy", "len", "color")

    def __init__(self, x, y, vx, vy, length, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.len = length
        self.color = color

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def off_screen(self):
        return self.y > GROUND_Y or self.x < -8 or self.x > W + 8

    def draw(self, surf):
        dx = self.vx / max(1.0, abs(self.vy)) * self.len
        dy = self.len
        pygame.draw.line(surf, self.color,
                         (int(self.x), int(self.y)),
                         (int(self.x - dx), int(self.y - dy)), 1)


class _Leaf:
    __slots__ = ("x", "y", "vx", "vy", "spin", "phase", "color")

    def __init__(self, x, y, vx, vy, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.spin = random.uniform(0, math.tau)
        self.phase = random.uniform(0, math.tau)
        self.color = color

    def update(self, dt):
        self.phase += dt * 3.0
        self.spin += dt * 2.0
        # Lateral flutter
        self.x += (self.vx + math.sin(self.phase) * 20) * dt
        self.y += self.vy * dt

    def off_screen(self):
        return self.x < -20 or self.x > W + 20 or self.y > GROUND_Y

    def draw(self, surf):
        r = 3
        sx = math.cos(self.spin)
        rx = max(1, int(abs(sx) * r))
        pygame.draw.ellipse(surf, self.color,
                            (int(self.x) - rx, int(self.y) - r, rx * 2, r * 2))


# ── fog overlay ─────────────────────────────────────────────────────────────

_fog_cache: dict = {}


def _get_fog_band(alpha_scale: float) -> pygame.Surface:
    key = int(alpha_scale * 100)
    cached = _fog_cache.get(key)
    if cached is not None:
        return cached
    band_h = 200
    surf = pygame.Surface((W, band_h), pygame.SRCALPHA)
    for i in range(band_h):
        # Fade in from the top, peak near the ground, fade out the last 20 px
        t = i / (band_h - 1)
        if t < 0.2:
            a = t / 0.2 * 0.6
        elif t > 0.85:
            a = (1.0 - (t - 0.85) / 0.15) * 0.9
        else:
            a = 0.9
        alpha = int(180 * a * alpha_scale)
        pygame.draw.line(surf, (220, 225, 240, alpha),
                         (0, i), (W - 1, i))
    _fog_cache[key] = surf
    return surf


# ── main Weather controller ────────────────────────────────────────────────

class Weather:
    def __init__(self):
        self.streaks: list[_Streak] = []
        self.leaves: list[_Leaf] = []
        self.phase: float = 0.0

        # Lightning state: countdown to next strike, and flash envelope 0..1.
        self.flash_remaining: float = 0.0
        self.next_strike: float = random.uniform(4.0, 9.0)

    def update(self, dt, phase):
        self.phase = phase

        # Rain
        intensity = rain_intensity(phase)
        if intensity > 0:
            color = rain_color(phase)
            target = int(50 + intensity * 90)
            # Top up the pool — streaks spawn above the screen and fall.
            while len(self.streaks) < target:
                self._spawn_streak(intensity, color)
            for s in self.streaks:
                s.update(dt)
            self.streaks = [s for s in self.streaks if not s.off_screen()]
        else:
            # Fade out lingering rain
            self.streaks = [s for s in self.streaks if not s.off_screen()][:max(0, len(self.streaks) - 2)]
            for s in self.streaks:
                s.update(dt)

        # Wind leaves
        wind = wind_intensity(phase)
        if wind > 0:
            target = int(wind * 10)
            while len(self.leaves) < target:
                self._spawn_leaf(wind)
            for lf in self.leaves:
                lf.update(dt)
            self.leaves = [lf for lf in self.leaves if not lf.off_screen()]
        else:
            self.leaves = []

        # Lightning (only in night window)
        if lightning_active(phase):
            self.next_strike -= dt
            if self.next_strike <= 0 and self.flash_remaining <= 0:
                self.flash_remaining = 0.18
                self.next_strike = random.uniform(6.0, 12.0)
                audio.play_thunder()
        else:
            self.next_strike = max(self.next_strike, random.uniform(4.0, 9.0))
        if self.flash_remaining > 0:
            self.flash_remaining = max(0.0, self.flash_remaining - dt)

    def _spawn_streak(self, intensity, color):
        x = random.uniform(-20, W + 20)
        y = random.uniform(-80, -4)
        vx = -60 - intensity * 60
        vy = 420 + intensity * 220
        length = 10 + int(intensity * 14)
        self.streaks.append(_Streak(x, y, vx, vy, length, color))

    def _spawn_leaf(self, wind):
        x = -10
        y = random.uniform(60, GROUND_Y - 60)
        vx = 80 + wind * 40 + random.uniform(-15, 30)
        vy = random.uniform(-15, 40)
        hue = random.choice((
            (255, 210, 100),
            (245, 180, 80),
            (220, 140, 60),
            (230, 200, 120),
        ))
        self.leaves.append(_Leaf(x, y, vx, vy, hue))

    def draw(self, surf):
        # Rain
        for s in self.streaks:
            s.draw(surf)
        # Leaves
        for lf in self.leaves:
            lf.draw(surf)
        # Fog near the ground
        fog = fog_intensity(self.phase)
        if fog > 0:
            band = _get_fog_band(fog)
            surf.blit(band, (0, GROUND_Y - 160))
        # Lightning flash — additive white-blue pulse
        if self.flash_remaining > 0:
            t = self.flash_remaining / 0.18
            alpha = int(180 * t)
            flash = pygame.Surface((W, H), pygame.SRCALPHA)
            flash.fill((210, 220, 255, alpha))
            surf.blit(flash, (0, 0))
