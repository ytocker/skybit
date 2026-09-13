"""Threshold-height sweep of the LIVE Coral Ember sky (`alpine_haze`).

Five variants of the live design that differ ONLY in how far the sunset "warm
threshold" sits down the screen — the horizontal line where the cool upper dome
gives way to the warm gold/red/plum band during golden hour → sunset → night.

That line is the vertical placement of the `sky_mid` colour stop, set by
`SkyParams.positions` (consumed by `game/biome_sky.py:_sky_stops`). The Coral
Ember keyframe COLOURS (`_ALPINE_HAZE_KF`) are shared verbatim across every row,
so the only thing that changes is where the warm onset sits: pushing `sky_mid`
(and its neighbours) toward 1.0 slides the threshold lower, letting the cool
night-blue extend further down before the warm band begins.

Live `sky_mid` is at 0.58 (≈ y371 on the 640-tall tile, just below mid-screen);
the sweep walks it down toward ≈0.80 (≈ y512, hugging the mountain line).

Preview-only data; the game never imports this and `ACTIVE_SKY_DESIGN` is
untouched.
"""
from __future__ import annotations

from game.biome_sky import BiomeSpec, SkyParams
from game.biome_sky_keyframes import ALPINE_HAZE, _ALPINE_HAZE_KF

# Kept from the live spec for every row so ONLY the stop placement varies.
_DITHER = 1.8
_ZENITH = 0.14

# (label, positions) — `sky_mid` (index 2) is the threshold; index 1/3 follow it
# down so the gradient stays smooth + monotonic. Original first, then an even
# descent of the warm onset.
_SWEEP = [
    ("V1 slight  (mid 0.63 ~y403)", (0.0, 0.34, 0.63, 0.85, 1.0)),
    ("V2         (mid 0.68 ~y435)", (0.0, 0.38, 0.68, 0.88, 1.0)),
    ("V3 medium  (mid 0.72 ~y461)", (0.0, 0.42, 0.72, 0.90, 1.0)),
    ("V4         (mid 0.76 ~y486)", (0.0, 0.46, 0.76, 0.92, 1.0)),
    ("V5 max     (mid 0.80 ~y512)", (0.0, 0.50, 0.80, 0.94, 1.0)),
]


def _variant(label, positions):
    return BiomeSpec(
        name=label,
        note=f"Coral Ember colours, sunset threshold lowered — positions={positions}.",
        keyframes=_ALPINE_HAZE_KF,
        sky=SkyParams(positions=positions, dither_amp=_DITHER, zenith_dark=_ZENITH),
    )


# Row 0 is the verbatim live spec; rows 1-5 are the lowered-threshold variants.
VARIANTS = [("Original (live)  (mid 0.58 ~y371)", ALPINE_HAZE)] + [
    (label, _variant(label, pos)) for label, pos in _SWEEP
]
