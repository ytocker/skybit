"""
Sky-only painter for the dormant biome sky-design registry.

Extracted from the biome exploration's `scene_engine.py`, keeping ONLY the sky
color-field path — the per-phase palette model plus `paint_sky`. Every ridge,
structure, ground, foliage and atmosphere drawer from the full scene engine is
intentionally absent: these designs contribute a sky gradient and a night-star
sprinkle, nothing else.

A biome is a `BiomeSpec` — its own day-cycle keyframes (sky stops + star alpha)
and a `SkyParams` describing how those stops are placed/eased into the OKLab
bake. The 10-stage day→night arc falls out of interpolating each biome's
keyframes against `phase` (0..1).

NOTE: this module is preview-only. Nothing on the live render path imports it;
it is reached solely through `game/sky_designs.py`, which stays dormant until
`ACTIVE_SKY_DESIGN` is deliberately set. All draw code is pure-Pygame /
pygbag-safe (the OKLab engine bakes on the cache-miss path only — no
surfarray/gfxdraw/numpy).
"""
from __future__ import annotations

from dataclasses import dataclass

import pygame

from game import biome_sky_field as sf
from game.draw import lerp_color


# ── palette authoring (mirrors game/biome.py's smoothstep interpolation) ──────

def _blend(a: dict, b: dict, t: float) -> dict:
    """Lerp two palette dicts: color tuples via lerp_color, scalars linearly.
    Keys present in only one side pass through unchanged so a biome can omit
    keys it doesn't use."""
    out = {}
    for k in a:
        va = a[k]
        vb = b.get(k, va)
        if isinstance(va, tuple) and isinstance(vb, tuple):
            out[k] = lerp_color(va, vb, t)
        elif isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            out[k] = va + (vb - va) * t
        else:
            out[k] = va
    for k in b:
        out.setdefault(k, b[k])
    return out


def make_palette(keyframes):
    """Return a `palette_for_phase(phase)` closure for a biome's own keyframes
    = sorted list of (phase, dict). Identical model to game/biome.py: smoothstep
    eased blend between the two surrounding anchors, wrapping at 1.0."""
    kf = sorted(keyframes, key=lambda p: p[0])
    # Ensure the cycle closes: if no anchor at >=1.0, append a wrap of the first.
    if kf[-1][0] < 1.0:
        kf = kf + [(1.0, kf[0][1])]

    def palette_for_phase(phase: float) -> dict:
        phase = phase % 1.0
        for i in range(len(kf) - 1):
            t0, p0 = kf[i]
            t1, p1 = kf[i + 1]
            if t0 <= phase <= t1:
                span = t1 - t0
                t = (phase - t0) / span if span > 0 else 0.0
                t = t * t * (3 - 2 * t)  # smoothstep
                return _blend(p0, p1, t)
        return dict(kf[0][1])

    return palette_for_phase


# ── parameter schema ──────────────────────────────────────────────────────────

@dataclass
class SkyParams:
    """Eased stop positions + dither for the sky_field bake. Stops read the
    palette's sky_top/mid/bot/horizon; positions let a biome compress the grade
    toward the horizon. zenith_dark deepens the very top a touch."""
    positions: tuple = (0.0, 0.30, 0.62, 0.85, 1.0)
    dither_amp: float = 2.0
    zenith_dark: float = 0.06
    # Time-of-day descent of the warm band: a real sunset's cool->warm line sinks
    # toward the horizon as the sun drops. `descent_drop` is the max downward
    # translation of the interior stops, eased in across the evening and back out
    # at dawn (0 = the classic static placement, every other biome). The anchors
    # are the (golden, deep-night, dawn-start, dawn-end) phases shaping the ease.
    descent_drop: float = 0.0
    descent_anchors: tuple = (0.235, 0.56, 0.82, 0.97)


@dataclass
class BiomeSpec:
    """Sky-only biome spec: a day-cycle palette (keyframes) + its sky bake
    params. Structural fields from the full exploration engine (ridges,
    signature, foliage, ground, atmosphere) are intentionally dropped."""
    name: str
    note: str
    keyframes: list                    # [(phase, palette_dict), ...]
    sky: SkyParams

    def __post_init__(self):
        self._pal = make_palette(self.keyframes)

    def palette_for_phase(self, phase):
        return self._pal(phase)


# ── the sky painter ───────────────────────────────────────────────────────────

def _smoothstep(t):
    t = 0.0 if t < 0.0 else 1.0 if t > 1.0 else t
    return t * t * (3 - 2 * t)


def _evening_progress(phase, anchors):
    """0 in daylight, rising LINEARLY across the evening from golden hour, held
    through the dark night, falling linearly back across dawn. A steady, gradual
    descent that begins right at golden hour (a constant rate, not eased-in late)
    so the warm band visibly starts sinking the moment golden hour arrives."""
    golden, night, dawn0, dawn1 = anchors
    p = phase % 1.0
    if p <= golden or p >= dawn1:
        return 0.0
    if p < night:
        return (p - golden) / (night - golden)
    if p <= dawn0:
        return 1.0
    return 1.0 - (p - dawn0) / (dawn1 - dawn0)


def _sky_stops(spec, pal, phase=None):
    """The 5 positional OKLab stops for a biome's sky at one stage — a deepened
    zenith over the palette's sky_top/mid/bot/horizon. When the biome sets
    `descent_drop` and a `phase` is supplied, the interior stops translate down
    with the evening so the warm sunset band sinks toward the horizon over time."""
    sky_top = pal.get('sky_top', (40, 110, 200))
    cols = [
        sf.with_value(sky_top, -spec.sky.zenith_dark),
        pal.get('sky_top', sky_top),
        pal.get('sky_mid', (120, 170, 220)),
        pal.get('sky_bot', (200, 220, 240)),
        pal.get('horizon', (245, 235, 215)),
    ]
    positions = spec.sky.positions
    if phase is not None and spec.sky.descent_drop:
        delta = _evening_progress(phase, spec.sky.descent_anchors) * spec.sky.descent_drop
        z, top, mid, bot, hz = positions
        positions = (z, top + delta, mid + delta, min(bot + delta, 0.985), hz)
    return list(zip(positions, cols))


def paint_sky(surf, spec, w, h, phase, stars=False, ground_y=None):
    """Bake ONLY the biome's sky color field, filling the full tile — no ridges,
    structures, ground, foliage or atmosphere. With `stars=True`, restores the
    night sprinkle in the SAME band/positions as the full-scene sheets (pass
    `ground_y` so the upper-band layout matches), gated on the stage's
    `star_alpha`."""
    pal = spec.palette_for_phase(phase)
    stops = _sky_stops(spec, pal, phase)
    surf.blit(sf.make_sky_field(w, h, stops, dither_amp=spec.sky.dither_amp), (0, 0))
    if stars:
        sa = int(pal.get('star_alpha', 0))
        if sa > 0:
            _scatter_stars(surf, w, ground_y or h, sa)


def _scatter_stars(surf, w, ground_y, sa):
    """Width-seeded star sprinkle (shared layout across stages so stars don't
    jump between adjacent columns)."""
    import random as _r
    rng = _r.Random(w * 7919)
    band = int(ground_y * 0.62)
    n = 50 if sa > 150 else 26
    for _ in range(n):
        sx = rng.randint(0, w - 1)
        sy = rng.randint(0, band)
        r = rng.choice((1, 1, 1, 2))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, sa), (r + 1, r + 1), r)
        surf.blit(s, (sx, sy))
