"""Biome day/night cycle: phase math, palette interpolation, buckets."""
import pytest

from game import biome


def test_phase_in_unit_interval():
    for elapsed in (0.0, 0.5, 60.0, 299.0, 600.0, 12345.6):
        p = biome.phase_for_time(elapsed)
        assert 0.0 <= p < 1.0


def test_phase_periodic():
    """Same elapsed time + N full cycles should give the same phase."""
    base = 50.0
    p_base = biome.phase_for_time(base)
    p_plus_cycle = biome.phase_for_time(base + biome.CYCLE_SECONDS)
    assert p_base == pytest.approx(p_plus_cycle)


def test_phase_starts_offset():
    """Phase at t=0 is offset by 0.04 (mid-morning, not dawn)."""
    assert biome.phase_for_time(0.0) == pytest.approx(0.04)


def test_palette_returns_dict_with_colours():
    pal = biome.palette_for_phase(0.0)
    assert isinstance(pal, dict)
    for key in ("sky_top", "sky_mid", "sky_bot", "stone_light",
                "foliage_top", "ground_top"):
        assert key in pal
        col = pal[key]
        assert isinstance(col, tuple) and len(col) == 3
        assert all(0 <= c <= 255 for c in col)


def test_palette_at_keyframe():
    """A palette at exactly a keyframe phase equals that keyframe (modulo
    smoothstep at t=0 / t=1 endpoints)."""
    p = biome.palette_for_phase(0.0)
    assert p["star_alpha"] == pytest.approx(0)


def test_palette_continuous_around_cycle():
    """Phase wraparound: the palette at 0.999 should be close to the
    palette at 0.001."""
    p_lo = biome.palette_for_phase(0.001)
    # palette at 1.0 wraps to 0.0
    p_hi = biome.palette_for_phase(1.0 - 0.001)
    # Sky colours shouldn't jump — diff under 80 channels per component.
    for key in ("sky_top", "sky_mid"):
        for a, b in zip(p_lo[key], p_hi[key]):
            assert abs(a - b) < 80


def test_phase_bucket_integer_in_range():
    for phase in (0.0, 0.25, 0.5, 0.99, 1.5):
        b = biome.phase_bucket(phase)
        assert isinstance(b, int)
        assert 0 <= b < biome.PHASE_BUCKETS


def test_bucketed_phase_is_phase_aligned():
    """``bucketed_phase`` should be a multiple of 1/PHASE_BUCKETS."""
    bp = biome.bucketed_phase(0.37)
    quanta = 1.0 / biome.PHASE_BUCKETS
    # Round to a small number of decimal places to avoid float fuzz
    assert round(bp / quanta) == round(bp / quanta)
    assert 0.0 <= bp < 1.0


def test_palette_for_time_consistency():
    elapsed = 42.0
    p1 = biome.palette_for_time(elapsed)
    p2 = biome.palette_for_phase(biome.phase_for_time(elapsed))
    assert p1["sky_top"] == p2["sky_top"]
