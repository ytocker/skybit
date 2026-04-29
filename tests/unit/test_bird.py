"""Bird physics: flap, gravity integration, frame animation, alive flag."""
import pytest

from game.config import (
    BIRD_X, FLAP_V, GRAVITY, MAX_FALL, H,
)
from game.entities import Bird


def test_initial_state():
    b = Bird()
    assert b.x == BIRD_X
    assert b.y == pytest.approx(H * 0.42)
    assert b.vy == 0.0
    assert b.alive is True
    assert b.flap_boost == 0.0
    assert b.kfc_active is False
    assert b.ghost_active is False
    assert b.grow_active is False
    assert b.triple_active is False


def test_flap_sets_velocity_and_boost():
    b = Bird()
    b.flap()
    assert b.vy == FLAP_V
    assert b.flap_boost == 0.45


def test_flap_noop_when_dead():
    b = Bird()
    b.alive = False
    b.flap()
    assert b.vy == 0.0
    assert b.flap_boost == 0.0


def test_gravity_increases_vy():
    b = Bird()
    before = b.vy
    b.update(0.1)
    assert b.vy > before
    assert b.vy == pytest.approx(GRAVITY * 0.1)


def test_position_changes_with_velocity():
    b = Bird()
    b.vy = 100.0
    y0 = b.y
    b.update(0.1)
    assert b.y > y0


def test_vy_clamped_to_max_fall():
    b = Bird()
    b.vy = 99999.0
    b.update(0.1)
    assert b.vy == MAX_FALL


def test_flap_boost_decays():
    b = Bird()
    b.flap()
    boost0 = b.flap_boost
    b.update(0.1)
    assert b.flap_boost < boost0
    assert b.flap_boost >= 0.0


def test_flap_boost_does_not_go_negative():
    b = Bird()
    b.flap_boost = 0.0
    for _ in range(10):
        b.update(0.1)
    assert b.flap_boost == 0.0


def test_frame_t_advances():
    b = Bird()
    b.update(0.1)
    assert b.frame_t > 0.0


def test_tilt_clamped():
    """Tilt is reported in degrees; the bird should not flip through itself
    even at ridiculous velocities."""
    b = Bird()
    b.vy = 9999.0
    assert -55.0 <= b.tilt_deg <= 55.0
    b.vy = -9999.0
    assert -55.0 <= b.tilt_deg <= 55.0


def test_ghost_pulse_only_advances_when_active():
    b = Bird()
    p0 = b.ghost_pulse
    b.update(0.1)
    assert b.ghost_pulse == p0
    b.ghost_active = True
    b.update(0.1)
    assert b.ghost_pulse > p0
