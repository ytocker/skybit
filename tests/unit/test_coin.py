"""Coin spin/float updates, collected flag, public attrs."""
import math

import pytest

from game.entities import Coin


def test_initial_state():
    c = Coin(100, 200)
    assert c.x == 100
    assert c.y == 200
    assert c.collected is False
    assert 0 <= c.spin < math.tau
    assert isinstance(c.float_t, float)


def test_spin_advances():
    c = Coin(100, 200)
    s0 = c.spin
    c.update(0.1)
    # Spin advanced by SPIN_RATE * dt, modulo tau
    expected = (s0 + Coin.SPIN_RATE * 0.1) % math.tau
    assert c.spin == pytest.approx(expected)


def test_float_t_advances():
    c = Coin(100, 200)
    t0 = c.float_t
    c.update(0.1)
    assert c.float_t == pytest.approx(t0 + 0.1)


def test_spin_wraps_at_tau():
    c = Coin(100, 200)
    c.spin = math.tau - 0.01
    c.update(0.1)
    # Should have wrapped — spin now small positive
    assert c.spin < math.pi


def test_position_does_not_drift_on_update():
    """update() should not move x/y — those are managed by the world's
    scroll loop."""
    c = Coin(100, 200)
    for _ in range(10):
        c.update(0.1)
    assert c.x == 100
    assert c.y == 200
