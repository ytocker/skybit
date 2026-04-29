"""``world._lerp(a, b, t)`` clamps ``t`` to [0, 1]."""
import pytest

from game.world import _lerp


def test_lerp_at_zero():
    assert _lerp(10.0, 20.0, 0.0) == 10.0


def test_lerp_at_one():
    assert _lerp(10.0, 20.0, 1.0) == 20.0


def test_lerp_midpoint():
    assert _lerp(10.0, 20.0, 0.5) == 15.0


@pytest.mark.parametrize("t", [-1.0, -0.5, 1.5, 2.0, 1e9])
def test_lerp_clamps_out_of_range(t):
    """Out-of-range ``t`` must NOT extrapolate — saturate at the endpoints."""
    out = _lerp(10.0, 20.0, t)
    assert 10.0 <= out <= 20.0


def test_lerp_clamps_negative_to_a():
    assert _lerp(10.0, 20.0, -100.0) == 10.0


def test_lerp_clamps_positive_to_b():
    assert _lerp(10.0, 20.0, 100.0) == 20.0


def test_lerp_descending_range():
    """``a > b`` is fine — direction-agnostic."""
    assert _lerp(20.0, 10.0, 0.5) == 15.0
