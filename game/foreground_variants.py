"""Data-driven variety for the sidewalk cast/props.

The promenade used one fixed template per object, so the street read as a loop of
clones. This module supplies the SELECTION half of the fix: a stable, per-world-
slot, weather- and day-arc-aware pick into a per-family pool of variant
descriptors. The drawers consume a descriptor (palette / pose flags / accessory
flags) so adding variety is appending DATA rows here, not new code branches.

Stability (no flicker) comes from two things, mirroring the rest of the
foreground: the pick is a PURE function of (seed, beat, weather-bucket) with the
seed fixed per world slot `k`, and callers resolve it ONCE inside their existing
`_slot_latch` decision (frozen for the slot's whole on-screen traversal). The
beat/weather inputs are coarsely quantised so a slot rarely straddles a boundary,
and even then only not-yet-entered slots see the new mix.

`select_variant` returns 0 (== each drawer's legacy look) whenever a family pool
is empty or short, so this can be wired through every call site before any art
exists — a non-breaking identity until the registry is filled.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from game.config import WEATHER_UMBRELLA_RAIN_AT

# Day-arc beats — the ordinal vocabulary the variant weights key off. Matches the
# phase windows of foreground_promenade._roster_for so a variant can be "common at
# the morning market, rare at the night festival" etc.
BEAT_MARKET = 0     # p < 0.14   — food-market rush
BEAT_MORNING = 1    # 0.14–0.25 and 0.85–1.0 — calm morning / sunrise vendors
BEAT_GOLDEN = 2     # 0.25–0.40  — afternoon stroll
BEAT_DUSK = 3       # 0.40–0.58  — lamps lighting
BEAT_FESTIVAL = 4   # 0.58–0.80  — night festival
BEAT_PREDAWN = 5    # 0.80–0.85  — teardown

# Weather buckets — kept in lockstep with the umbrella/coat gate so wet-weather
# variants appear exactly when brollies do.
WB_CLEAR = 0
WB_RAIN = 1
WB_SNOW = 2


def beat_for_phase(phase: float) -> int:
    p = phase % 1.0
    if p < 0.14:
        return BEAT_MARKET
    if p < 0.25:
        return BEAT_MORNING
    if p < 0.40:
        return BEAT_GOLDEN
    if p < 0.58:
        return BEAT_DUSK
    if p < 0.80:
        return BEAT_FESTIVAL
    if p < 0.85:
        return BEAT_PREDAWN
    return BEAT_MORNING            # sunrise vendors share the calm-morning cast


def weather_bucket(rain: float, snow: float) -> int:
    if snow >= 0.35:
        return WB_SNOW
    if rain >= WEATHER_UMBRELLA_RAIN_AT:
        return WB_RAIN
    return WB_CLEAR


def slot_seed(k: int, salt: int) -> int:
    """Stable per-instance seed from the world slot `k` (same hash family as
    foreground_promenade._slot_on so it composes cleanly)."""
    return ((k * 0x9E3779B1) ^ (salt * 0x85EBCA77)) & 0xFFFFFFFF


@dataclass(frozen=True)
class Variant:
    """One look in a family pool. `palette` maps named colour roles the drawer
    reads (e.g. {'coat': (...), 'coat_dk': (...), 'hair': (...)}); `pose` and
    `accessory` are flag sets the drawer toggles existing code paths on; `attrs`
    carries family-specific scalars/strings (e.g. archetype, height, stoop,
    build). Weights shift the mix by day-arc beat and weather bucket."""
    palette: dict = field(default_factory=dict)
    pose: frozenset = field(default_factory=frozenset)
    accessory: frozenset = field(default_factory=frozenset)
    base_weight: float = 1.0
    beat_weights: dict = field(default_factory=dict)       # beat -> multiplier
    weather_weights: dict = field(default_factory=dict)    # wbucket -> multiplier
    attrs: dict = field(default_factory=dict)              # family-specific params


# Per-family pools. Index 0 of every family MUST reproduce the drawer's legacy
# look (so `variant=0` is a no-op). Filled family-by-family by the design loop.
_VARIANT_REGISTRY: dict[str, list[Variant]] = {}


def register(family: str, variants: list[Variant]) -> None:
    _VARIANT_REGISTRY[family] = list(variants)


def pool(family: str) -> list[Variant]:
    return _VARIANT_REGISTRY.get(family, ())


def variant_count(family: str) -> int:
    return len(_VARIANT_REGISTRY.get(family, ()))


def get(family: str, index: int) -> "Variant | None":
    p = _VARIANT_REGISTRY.get(family)
    if not p:
        return None
    return p[index % len(p)]


def _weighted_pick(seed: int, weights: list) -> int:
    total = 0.0
    for w in weights:
        if w > 0:
            total += w
    if total <= 0.0:
        return 0
    # Deterministic uniform in [0,total) from the integer seed.
    h = ((seed ^ 0x27D4EB2F) * 0x165667B1) & 0xFFFFFFFF
    x = (h / 4294967296.0) * total
    acc = 0.0
    for i, w in enumerate(weights):
        if w > 0:
            acc += w
            if x < acc:
                return i
    return len(weights) - 1


def select_variant(family: str, seed: int, beat: int, wbucket: int) -> int:
    """Stable variant index for a family at (seed, beat, weather). Returns 0 (the
    legacy look) when the family pool is empty/singleton, so it's safe to call
    everywhere before the registry is populated."""
    p = _VARIANT_REGISTRY.get(family)
    if not p or len(p) == 1:
        return 0
    weights = [
        v.base_weight
        * v.beat_weights.get(beat, 1.0)
        * v.weather_weights.get(wbucket, 1.0)
        for v in p
    ]
    # Fold beat/weather into the seed so the same slot can show different (but
    # still stable-per-traversal) picks across beats without correlating families.
    return _weighted_pick(seed ^ (beat << 3) ^ (wbucket << 6), weights)
