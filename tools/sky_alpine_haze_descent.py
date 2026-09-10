"""Time-varying sunset threshold for the live Coral Ember sky (`alpine_haze`).

Where `tools/sky_alpine_haze_threshold.py` lowered the warm threshold to a FIXED
height for the whole cycle, this models the real thing: as the sun drops, the
cool->warm line **descends over time**. The warm-onset `sky_mid` stop starts at
its original height at golden hour and translates DOWN as the scene advances
through sunset -> night, then rises back at dawn. Five versions differ in the
RATE of descent (gentle -> steep).

The Coral Ember keyframe COLOURS (`_ALPINE_HAZE_KF`) are shared verbatim; only
`SkyParams.positions` moves, and now it moves with phase. The descent envelope
follows the live keyframe anchors: the warm band only exists over the evening
(~0.235 golden -> 0.52 twilight) and dawn (~0.86 -> 0.97); deep night
(0.56 -> 0.82) is cool, so the band is gone by colour there regardless.

Preview-only; the game never imports this. NB the live render path uses a STATIC
positions tuple — shipping a descent would need a small engine addition.
"""
from __future__ import annotations

from game.biome_sky import BiomeSpec, SkyParams
from game.biome_sky_keyframes import ALPINE_HAZE, _ALPINE_HAZE_KF

_DITHER = 1.8
_ZENITH = 0.14
_BASE = (0.30, 0.58, 0.82)            # live interior stops (top, mid, bot)

# Descent-envelope phase anchors (from _ALPINE_HAZE_KF).
_GOLDEN = 0.235                       # warm appears here -> start at original
_NIGHT = 0.56                         # fully descended by deep night
_DAWN0 = 0.82                         # night hold ends
_DAWN1 = 0.97                         # band risen back to original by sunrise


def _smoothstep(t):
    t = 0.0 if t < 0.0 else 1.0 if t > 1.0 else t
    return t * t * (3 - 2 * t)


def evening_progress(phase):
    """0 in daylight, eased up to 1 across the evening descent, held through the
    dark night, eased back to 0 across dawn — so the threshold starts at its
    original height, sinks as the scene advances, and rises again at sunrise."""
    p = phase % 1.0
    if p <= _GOLDEN or p >= _DAWN1:
        return 0.0
    if p < _NIGHT:
        return _smoothstep((p - _GOLDEN) / (_NIGHT - _GOLDEN))
    if p <= _DAWN0:
        return 1.0
    return _smoothstep(1.0 - (p - _DAWN0) / (_DAWN1 - _DAWN0))


def positions_for(phase, drop):
    """Live positions with the interior stops translated down by the current
    evening progress times this version's max `drop`."""
    delta = evening_progress(phase) * drop
    top, mid, bot = (s + delta for s in _BASE)
    return (0.0, top, mid, min(bot, 0.985), 1.0)


def spec_for(phase, drop):
    """A BiomeSpec carrying Coral Ember's colours with the descended positions
    for this phase — baked per time-of-day column by the preview tools."""
    return BiomeSpec(
        name=f"descent drop={drop}",
        note=f"Coral Ember colours, threshold descending (drop={drop}).",
        keyframes=_ALPINE_HAZE_KF,
        sky=SkyParams(positions=positions_for(phase, drop),
                      dither_amp=_DITHER, zenith_dark=_ZENITH),
    )


# (label, drop) — drop is the max downward translation reached at deep night.
RATES = [
    ("Rate 1 gentle (drop 0.08)", 0.08),
    ("Rate 2        (drop 0.14)", 0.14),
    ("Rate 3 medium (drop 0.20)", 0.20),
    ("Rate 4        (drop 0.28)", 0.28),
    ("Rate 5 steep  (drop 0.36)", 0.36),
]

# Row 0 is the verbatim live (static) spec; rows 1-5 carry a `drop` (the preview
# tools build a per-column spec from it via `spec_for`).
VARIANTS = [("Original (live, static)", None)] + RATES
