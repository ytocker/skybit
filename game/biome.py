"""
Biome / time-of-day palettes.

A single `phase` float in [0, 1) cycles through day → golden hour → sunset →
dusk → night → predawn → sunrise → day. The phase is driven by the score
(every ~30 points = one full cycle) so the visuals evolve as the player
progresses without ever fully stopping the cycle.

Everything biome-colored (sky, mountains, horizon glow, pillars, ground tint,
stars) interpolates between the keyframes below. Each keyframe is a dict
declaring all the fields a frame needs; missing fields fall back to the
previous keyframe via the interpolator.
"""
from __future__ import annotations
import math

from game.draw import lerp_color


# ── keyframes ────────────────────────────────────────────────────────────────
# phase -> palette dict. Phases MUST be sorted ascending (0..1).

_KEYFRAMES: list[tuple[float, dict]] = [
    (0.00, dict(  # DAY — bright cyan sky, lush green pillars
        sky_top=(40, 110, 200),
        sky_mid=(90, 170, 230),
        sky_bot=(170, 220, 245),
        horizon=(255, 240, 200),
        mtn_far=(80, 120, 170),
        mtn_near=(55, 95, 145),
        ground_top=(80, 200, 80),
        ground_mid=(40, 150, 40),
        pillar_light=(120, 235, 130),
        pillar_mid=(55, 180, 70),
        pillar_dark=(25, 110, 45),
        pillar_band=(255, 235, 140),
        pillar_leaf=(80, 210, 100),
        star_alpha=0,
    )),
    (0.18, dict(  # GOLDEN HOUR — amber warmth
        sky_top=(80, 120, 200),
        sky_mid=(220, 175, 140),
        sky_bot=(255, 210, 160),
        horizon=(255, 220, 140),
        mtn_far=(130, 110, 150),
        mtn_near=(85, 75, 115),
        ground_top=(120, 190, 80),
        ground_mid=(80, 135, 50),
        pillar_light=(240, 220, 120),
        pillar_mid=(200, 150, 55),
        pillar_dark=(110, 75, 30),
        pillar_band=(255, 240, 180),
        pillar_leaf=(220, 200, 90),
        star_alpha=0,
    )),
    (0.32, dict(  # SUNSET — orange / pink / violet
        sky_top=(90, 50, 130),
        sky_mid=(230, 95, 120),
        sky_bot=(255, 160, 90),
        horizon=(255, 200, 120),
        mtn_far=(90, 60, 120),
        mtn_near=(55, 35, 85),
        ground_top=(150, 105, 110),
        ground_mid=(95, 60, 80),
        pillar_light=(255, 170, 140),
        pillar_mid=(210, 90, 100),
        pillar_dark=(110, 35, 65),
        pillar_band=(255, 220, 160),
        pillar_leaf=(230, 130, 110),
        star_alpha=20,
    )),
    (0.48, dict(  # DUSK — deep purple
        sky_top=(25, 20, 70),
        sky_mid=(70, 45, 130),
        sky_bot=(170, 95, 140),
        horizon=(255, 150, 140),
        mtn_far=(45, 30, 85),
        mtn_near=(25, 15, 55),
        ground_top=(80, 70, 110),
        ground_mid=(45, 35, 75),
        pillar_light=(180, 140, 230),
        pillar_mid=(115, 75, 175),
        pillar_dark=(55, 30, 95),
        pillar_band=(230, 170, 255),
        pillar_leaf=(150, 110, 200),
        star_alpha=130,
    )),
    (0.62, dict(  # NIGHT — dark navy, starry
        sky_top=(5, 8, 30),
        sky_mid=(15, 25, 70),
        sky_bot=(35, 55, 115),
        horizon=(170, 190, 255),
        mtn_far=(25, 35, 75),
        mtn_near=(15, 20, 50),
        ground_top=(35, 60, 75),
        ground_mid=(20, 40, 55),
        pillar_light=(140, 200, 255),
        pillar_mid=(55, 110, 185),
        pillar_dark=(20, 40, 90),
        pillar_band=(210, 240, 255),
        pillar_leaf=(90, 160, 220),
        star_alpha=235,
    )),
    (0.78, dict(  # PREDAWN — cool indigo fading
        sky_top=(30, 30, 80),
        sky_mid=(70, 60, 140),
        sky_bot=(200, 130, 180),
        horizon=(255, 200, 210),
        mtn_far=(55, 50, 110),
        mtn_near=(30, 25, 70),
        ground_top=(80, 95, 130),
        ground_mid=(45, 60, 95),
        pillar_light=(200, 170, 240),
        pillar_mid=(130, 95, 190),
        pillar_dark=(55, 40, 105),
        pillar_band=(255, 200, 230),
        pillar_leaf=(165, 130, 220),
        star_alpha=90,
    )),
    (0.90, dict(  # SUNRISE — pink / yellow bloom
        sky_top=(50, 100, 180),
        sky_mid=(255, 150, 150),
        sky_bot=(255, 220, 170),
        horizon=(255, 235, 180),
        mtn_far=(135, 105, 150),
        mtn_near=(85, 70, 110),
        ground_top=(130, 190, 120),
        ground_mid=(85, 140, 75),
        pillar_light=(255, 200, 200),
        pillar_mid=(230, 130, 130),
        pillar_dark=(140, 60, 80),
        pillar_band=(255, 240, 200),
        pillar_leaf=(240, 170, 140),
        star_alpha=0,
    )),
    (1.00, dict(  # loop back to DAY (same as 0.00)
        sky_top=(40, 110, 200),
        sky_mid=(90, 170, 230),
        sky_bot=(170, 220, 245),
        horizon=(255, 240, 200),
        mtn_far=(80, 120, 170),
        mtn_near=(55, 95, 145),
        ground_top=(80, 200, 80),
        ground_mid=(40, 150, 40),
        pillar_light=(120, 235, 130),
        pillar_mid=(55, 180, 70),
        pillar_dark=(25, 110, 45),
        pillar_band=(255, 235, 140),
        pillar_leaf=(80, 210, 100),
        star_alpha=0,
    )),
]


# One full day-cycle every CYCLE_SCORE points.
CYCLE_SCORE = 30.0


def phase_for_score(score: int) -> float:
    """Return a phase in [0,1). Uses a fractional offset so phase 0 is a
    bright mid-morning rather than cold dawn — matches the menu screen mood."""
    return ((score / CYCLE_SCORE) + 0.04) % 1.0


def _blend(a: dict, b: dict, t: float) -> dict:
    out = {}
    for k in a:
        va, vb = a[k], b[k]
        if isinstance(va, tuple):
            out[k] = lerp_color(va, vb, t)
        else:
            out[k] = va + (vb - va) * t
    return out


def palette_for_phase(phase: float) -> dict:
    """Interpolate the biome palette for a phase in [0,1)."""
    phase = phase % 1.0
    for i in range(len(_KEYFRAMES) - 1):
        t0, p0 = _KEYFRAMES[i]
        t1, p1 = _KEYFRAMES[i + 1]
        if t0 <= phase <= t1:
            span = t1 - t0
            t = (phase - t0) / span if span > 0 else 0.0
            # smoothstep for gentler transitions
            t = t * t * (3 - 2 * t)
            return _blend(p0, p1, t)
    return dict(_KEYFRAMES[0][1])


def palette_for_score(score: int) -> dict:
    return palette_for_phase(phase_for_score(score))


# ── cached-palette bucket helpers ────────────────────────────────────────────

# Quantize the phase to keep the surface cache small (32 buckets → ~smooth).
PHASE_BUCKETS = 32


def phase_bucket(phase: float) -> int:
    return int((phase % 1.0) * PHASE_BUCKETS) % PHASE_BUCKETS


def bucketed_phase(phase: float) -> float:
    return phase_bucket(phase) / PHASE_BUCKETS
