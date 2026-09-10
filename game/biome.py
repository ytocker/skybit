"""
Biome / time-of-day palettes.

A single `phase` float in [0, 1) cycles through day → golden hour → sunset →
dusk → night → predawn → sunrise → day. The phase is driven by **real elapsed
gameplay seconds** — one full cycle every CYCLE_SECONDS seconds — so the
visuals evolve with time, not with score. The player sees the full cycle in
a long run regardless of how fast they score.

Pillar palette keys describe the sandstone columns plus the foliage that
crowns them:
  stone_light / stone_mid / stone_dark   — body sandstone gradient
  stone_accent                           — warm highlight band on the sunlit side
  foliage_top / foliage_mid / foliage_dark — plants on the cap
  foliage_accent                         — flower / berry / bright leaf tip
"""
from __future__ import annotations
import math

from game.draw import lerp_color


# ── keyframes ────────────────────────────────────────────────────────────────
# phase -> palette dict. Phases MUST be sorted ascending (0..1).

_KEYFRAMES: list[tuple[float, dict]] = [
    (0.00000, dict(  # DAY — bright cyan sky, warm tan sandstone, lush green canopy
        sky_top=(40, 110, 200),
        sky_mid=(90, 170, 230),
        sky_bot=(170, 220, 245),
        horizon=(255, 240, 200),
        mtn_far=(80, 120, 170),
        mtn_near=(55, 95, 145),
        ground_top=(80, 200, 80),
        ground_mid=(40, 150, 40),
        stone_light=(225, 195, 155),
        stone_mid=(175, 140, 105),
        stone_dark=(95, 70, 55),
        stone_accent=(255, 220, 170),
        foliage_top=(140, 220, 110),
        foliage_mid=(70, 170, 75),
        foliage_dark=(30, 100, 50),
        foliage_accent=(255, 240, 120),
        star_alpha=0,
    )),
    (0.23125, dict(  # GOLDEN HOUR — amber warmth
        sky_top=(80, 120, 200),
        sky_mid=(220, 175, 140),
        sky_bot=(255, 210, 160),
        horizon=(255, 220, 140),
        mtn_far=(130, 110, 150),
        mtn_near=(85, 75, 115),
        ground_top=(120, 190, 80),
        ground_mid=(80, 135, 50),
        stone_light=(240, 200, 145),
        stone_mid=(200, 150, 90),
        stone_dark=(110, 70, 40),
        stone_accent=(255, 225, 155),
        foliage_top=(180, 210, 90),
        foliage_mid=(130, 170, 60),
        foliage_dark=(70, 100, 40),
        foliage_accent=(255, 200, 80),
        star_alpha=0,
    )),
    (0.36250, dict(  # SUNSET — rose stone, autumn canopy
        sky_top=(90, 50, 130),
        sky_mid=(230, 95, 120),
        sky_bot=(255, 160, 90),
        horizon=(255, 200, 120),
        mtn_far=(90, 60, 120),
        mtn_near=(55, 35, 85),
        ground_top=(150, 105, 110),
        ground_mid=(95, 60, 80),
        stone_light=(240, 170, 155),
        stone_mid=(190, 105, 110),
        stone_dark=(100, 45, 60),
        stone_accent=(255, 210, 170),
        foliage_top=(210, 150, 90),
        foliage_mid=(150, 95, 65),
        foliage_dark=(85, 45, 40),
        foliage_accent=(255, 160, 80),
        star_alpha=20,
    )),
    (0.51250, dict(  # DUSK — lavender stone, teal foliage
        sky_top=(25, 20, 70),
        sky_mid=(70, 45, 130),
        sky_bot=(170, 95, 140),
        horizon=(255, 150, 140),
        mtn_far=(45, 30, 85),
        mtn_near=(25, 15, 55),
        ground_top=(80, 70, 110),
        ground_mid=(45, 35, 75),
        stone_light=(180, 160, 200),
        stone_mid=(110, 95, 150),
        stone_dark=(55, 40, 80),
        stone_accent=(220, 200, 240),
        foliage_top=(120, 160, 150),
        foliage_mid=(60, 100, 110),
        foliage_dark=(25, 50, 70),
        foliage_accent=(180, 220, 200),
        star_alpha=130,
    )),
    (0.64375, dict(  # NIGHT — moonlit cool stone, dark teal canopy
        sky_top=(5, 8, 30),
        sky_mid=(15, 25, 70),
        sky_bot=(35, 55, 115),
        horizon=(170, 190, 255),
        mtn_far=(25, 35, 75),
        mtn_near=(15, 20, 50),
        ground_top=(35, 60, 75),
        ground_mid=(20, 40, 55),
        stone_light=(150, 170, 210),
        stone_mid=(80, 100, 150),
        stone_dark=(30, 45, 85),
        stone_accent=(200, 225, 255),
        foliage_top=(80, 130, 130),
        foliage_mid=(35, 80, 90),
        foliage_dark=(10, 35, 55),
        foliage_accent=(160, 220, 230),
        star_alpha=235,
    )),
    (0.79375, dict(  # PREDAWN — cool pink stone, muted canopy
        sky_top=(30, 30, 80),
        sky_mid=(70, 60, 140),
        sky_bot=(200, 130, 180),
        horizon=(255, 200, 210),
        mtn_far=(55, 50, 110),
        mtn_near=(30, 25, 70),
        ground_top=(80, 95, 130),
        ground_mid=(45, 60, 95),
        stone_light=(220, 175, 200),
        stone_mid=(155, 110, 150),
        stone_dark=(75, 50, 90),
        stone_accent=(255, 210, 225),
        foliage_top=(130, 155, 130),
        foliage_mid=(70, 105, 95),
        foliage_dark=(35, 60, 60),
        foliage_accent=(200, 220, 180),
        star_alpha=90,
    )),
    (0.90625, dict(  # SUNRISE — peach stone, fresh canopy
        sky_top=(50, 100, 180),
        sky_mid=(255, 150, 150),
        sky_bot=(255, 220, 170),
        horizon=(255, 235, 180),
        mtn_far=(135, 105, 150),
        mtn_near=(85, 70, 110),
        ground_top=(130, 190, 120),
        ground_mid=(85, 140, 75),
        stone_light=(255, 205, 175),
        stone_mid=(215, 150, 125),
        stone_dark=(130, 75, 70),
        stone_accent=(255, 230, 195),
        foliage_top=(170, 220, 130),
        foliage_mid=(95, 170, 90),
        foliage_dark=(45, 110, 60),
        foliage_accent=(255, 210, 130),
        star_alpha=0,
    )),
    (1.00000, dict(  # loop back to DAY
        sky_top=(40, 110, 200),
        sky_mid=(90, 170, 230),
        sky_bot=(170, 220, 245),
        horizon=(255, 240, 200),
        mtn_far=(80, 120, 170),
        mtn_near=(55, 95, 145),
        ground_top=(80, 200, 80),
        ground_mid=(40, 150, 40),
        stone_light=(225, 195, 155),
        stone_mid=(175, 140, 105),
        stone_dark=(95, 70, 55),
        stone_accent=(255, 220, 170),
        foliage_top=(140, 220, 110),
        foliage_mid=(70, 170, 75),
        foliage_dark=(30, 100, 50),
        foliage_accent=(255, 240, 120),
        star_alpha=0,
    )),
]


# One full day-cycle every CYCLE_SECONDS seconds of gameplay.
# The keyframe fractions above were authored against a 320s cycle (DAY spans
# 0.00 -> 0.23125 = 74s). The clown event inserts content into the day; that
# added run-time (config.DAY_EXTRA_SECONDS) is absorbed by the DAY phase so every
# later time-of-day keeps its original wall-clock duration but starts later. We
# grow the cycle by the same delta and remap each fraction:
#     new_phase = (old_phase * BASE + DAY_EXTRA) / (BASE + DAY_EXTRA)   (i >= 1)
# DAY stays at 0.0 and the wrap keyframe stays at 1.0.
# Names parallel to _KEYFRAMES (the last keyframe is the wrap back to DAY).
_KEYFRAME_NAMES = ["DAY", "GOLDEN HOUR", "SUNSET", "DUSK", "NIGHT",
                   "PREDAWN", "SUNRISE", "DAY"]

# Fraction of the (possibly extended) DAY span to hold at SOLID daytime before
# the golden-hour fade begins. Without this, a single DAY→GOLDEN smoothstep
# spans the whole — now much longer — day, so the sky drifts toward amber from
# the very start. We deliberately keep this hold SHORT so the fade is already
# reading on screen within the first ~25-30 pillars: most runs end early, and a
# 60% hold left the sky frozen on solid blue until ~pillar 42. Only applied when
# the day is extended. Pairs with NIGHT_BORROW_SECONDS below, which trims the
# same daytime length and hands it to the night.
DAY_HOLD_FRAC = 0.51

# Seconds trimmed off the GOLDEN..NIGHT keyframes and handed to the
# NIGHT→PREDAWN span: an EQUAL swap that pulls the whole evening earlier (so the
# sky starts changing sooner) and makes the night correspondingly longer,
# WITHOUT changing the total cycle. PREDAWN/SUNRISE stay put, so the predawn
# snow squall and the day-end finale keep their pillars. ~26s ≈ 15 early pillars.
# Only meaningful while the day is extended.
NIGHT_BORROW_SECONDS = 26.0

_BASE_CYCLE_SECONDS = 320.0
from game.config import DAY_EXTRA_SECONDS as _DAY_EXTRA
CYCLE_SECONDS = _BASE_CYCLE_SECONDS + _DAY_EXTRA

if _DAY_EXTRA:
    _last = len(_KEYFRAMES) - 1

    def _remap(i, frac):
        # DAY pinned to 0, wrap pinned to 1. The evening block (GOLDEN..NIGHT,
        # indices 1-4) is pulled earlier by the borrow; PREDAWN/SUNRISE keep the
        # full DAY_EXTRA shift, so the gap they leave behind lengthens the night.
        if i == 0:
            return 0.0
        if i == _last:
            return 1.0
        extra = _DAY_EXTRA - (NIGHT_BORROW_SECONDS if 1 <= i <= 4 else 0.0)
        return (frac * _BASE_CYCLE_SECONDS + extra) / CYCLE_SECONDS

    _KEYFRAMES[:] = [(_remap(i, frac), pal)
                     for i, (frac, pal) in enumerate(_KEYFRAMES)]
    # Hold solid DAY for DAY_HOLD_FRAC of the day span, then fade to golden over
    # the remainder — a DAY-coloured keyframe inserted just before golden hour.
    _golden_phase = _KEYFRAMES[1][0]
    _KEYFRAMES.insert(1, (_golden_phase * DAY_HOLD_FRAC, dict(_KEYFRAMES[0][1])))
    _KEYFRAME_NAMES.insert(1, "")   # the hold is not a named time-of-day

# Named phase boundaries (fraction, label) for any consumer that draws the
# day cycle — excludes the unnamed DAY-hold and the wrap. Reads the LIVE
# keyframes so it tracks the real (extended) day length.
PHASE_BOUNDARIES = [
    (frac, name) for (frac, _pal), name in zip(_KEYFRAMES, _KEYFRAME_NAMES)
    if name and frac < 1.0
]


def phase_for_time(elapsed_seconds: float) -> float:
    """Return a phase in [0,1). t=0 lands exactly on the DAY keyframe so
    the first 30+ seconds of a run sit in bright daylight before the
    transition toward golden hour starts to read on screen."""
    return (elapsed_seconds / CYCLE_SECONDS) % 1.0


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
            t = t * t * (3 - 2 * t)  # smoothstep
            return _blend(p0, p1, t)
    return dict(_KEYFRAMES[0][1])


def palette_for_time(elapsed_seconds: float) -> dict:
    return palette_for_phase(phase_for_time(elapsed_seconds))


# ── cached-palette bucket helpers ────────────────────────────────────────────

# The sky and every phase-tinted foreground strip (mountains, ground, pagoda
# ornaments) bake once per bucket and reuse, so the bucket count is the temporal
# resolution of the whole day cycle. At 32 the sunset — the fastest-changing arc
# — only got ~9 nodes, so the sky's piecewise-linear cross-fade faceted and the
# foreground tint snapped in visible ~10s steps. 120 makes each step ~2.7s with a
# ~4x smaller colour delta, below the perceptual threshold. The count is now
# decoupled from RAM: the accumulating per-bucket surface caches (sky_designs
# ._sky_cache, draw._sky_b_cache, pagoda_ornaments._CELL_CACHE) are LRU-bounded,
# since only the two adjacent buckets are ever needed per frame.
PHASE_BUCKETS = 120


def phase_bucket(phase: float) -> int:
    return int((phase % 1.0) * PHASE_BUCKETS) % PHASE_BUCKETS


def bucketed_phase(phase: float) -> float:
    return phase_bucket(phase) / PHASE_BUCKETS
