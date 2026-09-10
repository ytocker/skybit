"""Wildflower meadow — 5 flower-style variants.

The meadow base scene (grass band, tall hero blades, half-buried rocks,
small accent creatures) is identical across all 5 variants; only the
flower-drawing function changes. Each variant adds one signature accent
(butterflies / ladybugs / bees / etc.) tied to its flower style.

Each ``draw_ground_vN`` is a drop-in replacement for
``game.draw.draw_ground``.
"""
from __future__ import annotations

import math
import random

import pygame


# ── shared palette ─────────────────────────────────────────────────────────

_GRASS_TOP = (90, 200, 80)
_GRASS_MID = (45, 145, 50)
_GRASS_DK = (25, 90, 35)
_DIRT_TOP = (95, 70, 45)
_DIRT_DEEP = (55, 38, 25)
_ROCK = (140, 130, 115)
_YELLOW_CENTER = (255, 220, 90)
_BLACK = (25, 15, 15)


# ── helpers ────────────────────────────────────────────────────────────────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, delta):
    return (_clamp(c[0] + delta), _clamp(c[1] + delta), _clamp(c[2] + delta))


def _lerp_color(a, b, t):
    return _mix(a, b, t)


def _brightness(c) -> float:
    return min(1.0, (c[0] + c[1] + c[2]) / 510.0)


def _warmth(c) -> float:
    return (c[0] - c[2]) / 255.0


def _vertical_gradient(surf, x0, y0, x1, y1, top, bot):
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / max(1, h - 1)
        c = _lerp_color(top, bot, t)
        pygame.draw.line(surf, c, (x0, y0 + i), (x1 - 1, y0 + i))


def _ambient_ground_overlay(surf, ground_y, w, h, mid_color):
    b = _brightness(mid_color)
    band = pygame.Surface((w, h - ground_y), pygame.SRCALPHA)
    if b < 0.6:
        alpha = int(160 * (0.6 - b))
        band.fill((mid_color[0] // 3, mid_color[1] // 3,
                   mid_color[2] // 3, alpha))
    w_amt = _warmth(mid_color)
    if w_amt > 0.05:
        alpha = int(min(85, w_amt * 220))
        warm = pygame.Surface((w, h - ground_y), pygame.SRCALPHA)
        warm.fill((255, 150, 90, alpha))
        band.blit(warm, (0, 0))
    surf.blit(band, (0, ground_y))


# Per-run seed mixed into every decoration position so two plays of the same
# theme never look identical. Re-randomise via ``set_run_seed()`` on each
# new game so the meadow reshuffles.
RUN_SEED: int = 0
# Per-run overall lushness in [0.35, 1.0]. Combined with the density wave
# so each play has its own "personality" (sparse meadow ↔ jungle-thick)
# in addition to the within-run patchiness.
RUN_DENSITY_BASE: float = 0.7
# Which of the 5 themes this run uses — also derived from RUN_SEED so it
# reshuffles every play. The live game's ``draw_ground`` reads this.
RUN_VARIANT_ID: int = 1


def set_run_seed(seed: int | None = None) -> None:
    """Set the run seed. Pass ``None`` to draw a fresh random one — call this
    once when starting a new game/play. Derives a density baseline AND
    picks which of the 5 themes this play uses, from the same seed, so
    everything reshuffles together."""
    global RUN_SEED, RUN_DENSITY_BASE, RUN_VARIANT_ID
    RUN_SEED = seed if seed is not None else random.randint(0, 0x7FFFFFFF)
    rng = random.Random(RUN_SEED ^ 0xCAFEBABE)
    RUN_DENSITY_BASE = rng.uniform(0.35, 1.0)
    RUN_VARIANT_ID = rng.choice((1, 2, 3, 4, 5))


def draw_run_ground(surf, ground_y, w, h, scroll,
                    top_color=None, mid_color=None, bot_color=None):
    """Drop-in replacement for ``game.draw.draw_ground`` that dispatches
    to whichever variant ``RUN_VARIANT_ID`` currently names."""
    VARIANTS[RUN_VARIANT_ID](surf, ground_y, w, h, scroll,
                             top_color, mid_color, bot_color)


set_run_seed()  # initialise on import


def _density_at(world_x: float) -> float:
    """Density factor 0..RUN_DENSITY_BASE driven by three phase-shifted sine
    waves over world-x:

    * a SLOW regional wave (wavelength ~4200 px) — the bird flies through
      long stretches that feel sparse, then long stretches that feel
      lush, all within one play;
    * two FAST patch waves (~570 / ~900 px) — local clusters and gaps
      inside each region;
    * all three are phase-shifted by ``RUN_SEED`` so the regional pattern
      also reshuffles every new play;
    * the whole thing is then scaled by ``RUN_DENSITY_BASE`` so a play's
      overall lushness also varies between runs.
    """
    slow = math.sin(world_x * 0.0015 + RUN_SEED * 7.3e-4) * 0.5 + 0.5
    fast_a = math.sin(world_x * 0.011 + RUN_SEED * 1.4e-3) * 0.5 + 0.5
    fast_b = math.sin(world_x * 0.005 + RUN_SEED * 3.1e-3 + 1.7) * 0.5 + 0.5
    fast = fast_a * 0.6 + fast_b * 0.4
    combined = slow * 0.6 + fast * 0.4  # slow dominates, fast adds patches
    return combined * RUN_DENSITY_BASE


def _scatter(scroll, w, speed, step, seed_off):
    phase = scroll * speed
    first = int(phase // step) - 1
    last = int((phase + w) // step) + 2
    for k in range(first, last + 1):
        rng = random.Random(
            (k * 2654435761 ^ seed_off ^ RUN_SEED) & 0xFFFFFFFF)
        wx = k * step + rng.uniform(-step * 0.25, step * 0.25)
        sx = int(wx - phase)
        if -20 < sx < w + 20:
            yield sx, k, rng


# ── accent creatures (small) ───────────────────────────────────────────────

def _butterfly(surf, x, y, color):
    pygame.draw.circle(surf, color, (x - 1, y), 2)
    pygame.draw.circle(surf, color, (x + 2, y), 2)
    pygame.draw.line(surf, _BLACK, (x, y - 1), (x, y + 1), 1)


def _ladybug(surf, x, y):
    pygame.draw.ellipse(surf, (200, 30, 30), (x - 2, y - 1, 4, 3))
    pygame.draw.circle(surf, _BLACK, (x - 2, y), 1)
    pygame.draw.line(surf, _BLACK, (x, y - 1), (x, y + 1), 1)
    pygame.draw.circle(surf, _BLACK, (x - 1, y), 1)
    pygame.draw.circle(surf, _BLACK, (x + 1, y), 1)


def _bee(surf, x, y):
    pygame.draw.ellipse(surf, (245, 210, 70), (x - 2, y - 1, 4, 3))
    pygame.draw.line(surf, _BLACK, (x - 1, y - 1), (x - 1, y + 1), 1)
    pygame.draw.line(surf, _BLACK, (x + 1, y - 1), (x + 1, y + 1), 1)
    pygame.draw.line(surf, (235, 240, 255), (x - 1, y - 2), (x + 1, y - 2), 1)


# ── flower style helpers (one per variant) ─────────────────────────────────

_V1_PALETTE = [(235, 80, 80), (255, 220, 90), (250, 248, 240),
               (250, 170, 210), (190, 130, 230)]


def _flower_mixed(surf, x, ground_y, rng):
    """V1 — 4-petal flower in a random mixed colour."""
    col = rng.choice(_V1_PALETTE)
    fy = ground_y + rng.randint(-2, 6)
    pygame.draw.line(surf, _GRASS_DK, (x, fy + 3), (x, fy), 1)
    pygame.draw.circle(surf, col, (x - 1, fy), 1)
    pygame.draw.circle(surf, col, (x + 1, fy), 1)
    pygame.draw.circle(surf, col, (x, fy - 1), 1)
    pygame.draw.circle(surf, col, (x, fy + 1), 1)
    pygame.draw.circle(surf, _YELLOW_CENTER, (x, fy), 1)


def _flower_daisy(surf, x, ground_y, rng):
    """V2 — white 5-petal daisy with yellow centre."""
    fy = ground_y + rng.randint(-2, 5)
    pygame.draw.line(surf, _GRASS_DK, (x, fy + 3), (x, fy), 1)
    white = (252, 250, 240)
    # 4 cardinal petals
    pygame.draw.circle(surf, white, (x - 1, fy), 1)
    pygame.draw.circle(surf, white, (x + 1, fy), 1)
    pygame.draw.circle(surf, white, (x, fy - 1), 1)
    pygame.draw.circle(surf, white, (x, fy + 1), 1)
    # Diagonal 5th petal so silhouette doesn't read identical to V1
    pygame.draw.circle(surf, white, (x - 1, fy - 1), 1)
    pygame.draw.circle(surf, _YELLOW_CENTER, (x, fy), 1)


_V3_TULIP_COLORS = [(225, 65, 70), (240, 200, 70), (250, 130, 180),
                    (180, 100, 220), (245, 130, 60)]


def _flower_tulip(surf, x, ground_y, rng):
    """V3 — closed tulip bud on a tall stem with one leaf."""
    col = rng.choice(_V3_TULIP_COLORS)
    base_y = ground_y + rng.randint(0, 4)
    bud_y = base_y - rng.randint(8, 12)
    # Stem
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, bud_y + 1), 1)
    pygame.draw.line(surf, _GRASS_TOP, (x + 1, base_y), (x + 1, bud_y + 2), 1)
    # Leaf (curving)
    pygame.draw.line(surf, _GRASS_DK,
                     (x, base_y - 3), (x + 3, base_y - 6), 1)
    pygame.draw.line(surf, _GRASS_TOP,
                     (x, base_y - 4), (x + 3, base_y - 7), 1)
    # Bud — 3 vertical strokes for a closed-tulip silhouette
    pygame.draw.line(surf, _shade(col, -40),
                     (x - 1, bud_y - 1), (x - 1, bud_y + 2), 1)
    pygame.draw.line(surf, col, (x, bud_y - 2), (x, bud_y + 2), 1)
    pygame.draw.line(surf, _shade(col, -40),
                     (x + 1, bud_y - 1), (x + 1, bud_y + 2), 1)
    pygame.draw.line(surf, _mix(col, (255, 255, 255), 0.6),
                     (x, bud_y - 1), (x, bud_y), 1)


def _flower_poppy(surf, x, ground_y, rng):
    """V4 — round red poppy with black centre."""
    base_y = ground_y + rng.randint(0, 4)
    fy = base_y - rng.randint(2, 5)
    # Thin stem
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, fy + 1), 1)
    # Bloom — overlapping filled circles in two reds for a chunky look
    pygame.draw.circle(surf, (155, 30, 35), (x - 1, fy), 2)
    pygame.draw.circle(surf, (215, 50, 45), (x + 1, fy), 2)
    pygame.draw.circle(surf, (230, 70, 55), (x, fy - 1), 1)
    # Black centre
    pygame.draw.circle(surf, _BLACK, (x, fy), 1)


def _flower_lavender(surf, x, ground_y, rng):
    """V5 — tall vertical lavender spike."""
    base_y = ground_y + rng.randint(0, 4)
    height = rng.randint(9, 14)
    top_y = base_y - height
    # Stem
    pygame.draw.line(surf, (95, 135, 80), (x, base_y), (x, top_y), 1)
    # Spike: dotted purple cluster along the upper third
    spike_start = top_y
    spike_end = top_y + height // 2
    for sy in range(spike_start, spike_end + 1):
        # Center dot
        col = (180, 130, 220) if (sy - spike_start) % 2 == 0 else (155, 105, 200)
        pygame.draw.circle(surf, col, (x, sy), 1)
        # Side dots
        if rng.random() < 0.6:
            pygame.draw.circle(surf, _shade(col, -20), (x - 1, sy), 1)
        if rng.random() < 0.6:
            pygame.draw.circle(surf, _shade(col, -20), (x + 1, sy), 1)
    # Bright tip
    pygame.draw.circle(surf, (215, 175, 245), (x, spike_start - 1), 1)


# ── shared meadow scene ────────────────────────────────────────────────────

def _meadow_scene(surf, ground_y, w, h, scroll, mid_color, flower_fn,
                  accent_kind):
    """Render grass + blades + flowers (via ``flower_fn``) + rocks +
    creatures. ``accent_kind`` is one of: butterfly / ladybug / bee /
    bumblebee / mixed_bee."""
    grass_h = 22
    _vertical_gradient(surf, 0, ground_y, w, ground_y + grass_h,
                       _GRASS_TOP, _GRASS_MID)
    _vertical_gradient(surf, 0, ground_y + grass_h, w, h,
                       _DIRT_TOP, _DIRT_DEEP)

    # Sparse darker grass tufts
    for sx, k, rng in _scatter(scroll, w, 0.7, 5, 11):
        if 0 <= sx < w:
            tuft_h = rng.randint(3, 9)
            lean = rng.randint(-2, 2)
            base_y = ground_y + rng.randint(0, 4)
            pygame.draw.line(surf, _GRASS_DK,
                             (sx, base_y), (sx + lean, base_y - tuft_h), 1)
            pygame.draw.line(surf, _GRASS_TOP,
                             (sx, base_y), (sx + lean, base_y - tuft_h + 1), 1)

    # Tall hero blades
    for sx, k, rng in _scatter(scroll, w, 0.7, 11, 23):
        if 0 <= sx < w:
            tuft_h = rng.randint(7, 12)
            base_y = ground_y + rng.randint(0, 2)
            lean = rng.randint(-2, 2)
            pygame.draw.line(surf, _GRASS_DK,
                             (sx, base_y), (sx + lean, base_y - tuft_h), 1)
            pygame.draw.line(surf, _GRASS_TOP,
                             (sx + 1, base_y), (sx + 1 + lean, base_y - tuft_h + 1), 1)

    # Flowers — variant-specific. Tighter step (denser candidate positions),
    # skip probability driven by a per-world-x density wave so the bird
    # flies through lush patches and sparse stretches as it scrolls.
    # The wave phase is mixed with RUN_SEED so the pattern of lush vs
    # sparse also reshuffles every new play.
    flower_step = 14
    for sx, k, rng in _scatter(scroll, w, 0.7, flower_step, 37):
        if 0 <= sx < w:
            world_x = k * flower_step
            if rng.random() < _density_at(world_x):
                flower_fn(surf, sx, ground_y, rng)

    # Dandelion puffballs (kept across variants — universal meadow accent)
    for sx, k, rng in _scatter(scroll, w, 0.7, 55, 53):
        if 0 <= sx < w and rng.random() < 0.55:
            fy = ground_y + rng.randint(-3, 4)
            pygame.draw.line(surf, _GRASS_DK,
                             (sx, fy + 4), (sx, fy), 1)
            pygame.draw.circle(surf, (255, 245, 200), (sx, fy), 2)
            pygame.draw.circle(surf, (255, 255, 255), (sx, fy), 1)

    # Half-buried rocks
    for sx, k, rng in _scatter(scroll, w, 0.7, 70, 67):
        if 0 <= sx < w and rng.random() < 0.55:
            ry = ground_y + 10 + rng.randint(0, 8)
            rw = rng.randint(4, 7)
            pygame.draw.ellipse(surf, _ROCK,
                                (sx - rw // 2, ry, rw, 3))
            pygame.draw.line(surf, _shade(_ROCK, 30),
                             (sx - rw // 2 + 1, ry),
                             (sx + rw // 2 - 2, ry), 1)

    # Accent creatures — variant-specific
    if accent_kind == "butterfly":
        for sx, k, rng in _scatter(scroll, w, 0.7, 130, 91):
            if 0 <= sx < w and rng.random() < 0.5:
                by = ground_y - rng.randint(8, 22)
                col = rng.choice([(255, 220, 90), (250, 170, 210),
                                  (190, 130, 230)])
                _butterfly(surf, sx, by, col)
    elif accent_kind == "ladybug":
        for sx, k, rng in _scatter(scroll, w, 0.7, 65, 113):
            if 0 <= sx < w and rng.random() < 0.55:
                ly = ground_y + rng.randint(2, 28)
                _ladybug(surf, sx, ly)
    elif accent_kind == "bee":
        for sx, k, rng in _scatter(scroll, w, 0.7, 60, 131):
            if 0 <= sx < w and rng.random() < 0.55:
                by = ground_y - rng.randint(2, 18)
                _bee(surf, sx, by)
    elif accent_kind == "bumblebee":
        # Sparser — a few bees + a few butterflies for a calmer mood
        for sx, k, rng in _scatter(scroll, w, 0.7, 110, 137):
            if 0 <= sx < w and rng.random() < 0.5:
                by = ground_y - rng.randint(6, 18)
                _bee(surf, sx, by)
        for sx, k, rng in _scatter(scroll, w, 0.7, 160, 149):
            if 0 <= sx < w and rng.random() < 0.4:
                by = ground_y - rng.randint(10, 24)
                _butterfly(surf, sx, by, (255, 220, 90))

    # Edge highlight
    pygame.draw.line(surf, _shade(_GRASS_TOP, 60),
                     (0, ground_y), (w - 1, ground_y), 1)

    _ambient_ground_overlay(surf, ground_y, w, h, mid_color)


# ── public variant entry points ────────────────────────────────────────────

def draw_ground_v1(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    """V1 — Mixed Wildflowers (original)."""
    _meadow_scene(surf, ground_y, w, h, scroll,
                  mid_color or _GRASS_MID,
                  _flower_mixed, "butterfly")


def draw_ground_v2(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    """V2 — Daisy Lawn."""
    _meadow_scene(surf, ground_y, w, h, scroll,
                  mid_color or _GRASS_MID,
                  _flower_daisy, "bumblebee")


def draw_ground_v3(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    """V3 — Tulip Garden."""
    _meadow_scene(surf, ground_y, w, h, scroll,
                  mid_color or _GRASS_MID,
                  _flower_tulip, "butterfly")


def draw_ground_v4(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    """V4 — Poppy Field."""
    _meadow_scene(surf, ground_y, w, h, scroll,
                  mid_color or _GRASS_MID,
                  _flower_poppy, "ladybug")


def draw_ground_v5(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    """V5 — Lavender Spikes."""
    _meadow_scene(surf, ground_y, w, h, scroll,
                  mid_color or _GRASS_MID,
                  _flower_lavender, "bee")


# ── dispatcher ─────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_ground_v1,
    2: draw_ground_v2,
    3: draw_ground_v3,
    4: draw_ground_v4,
    5: draw_ground_v5,
}

VARIANT_NAMES = {
    1: "Mixed Wildflowers (original)",
    2: "Daisy Lawn",
    3: "Tulip Garden",
    4: "Poppy Field",
    5: "Lavender Spikes",
}
