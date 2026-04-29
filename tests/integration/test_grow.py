"""Grow: bird_radius() flips, bigger collision footprint."""
import pytest

from game.config import BIRD_R, GROW_SCALE, GROW_DURATION


def test_bird_radius_changes_with_grow_timer(world):
    assert world.bird_radius() == BIRD_R
    world.grow_timer = 1.0
    assert world.bird_radius() == pytest.approx(BIRD_R * GROW_SCALE)


def test_grow_activation_sets_duration(world):
    from game.entities import PowerUp
    pu = PowerUp(world.bird.x, world.bird.y, kind="grow")
    world._activate_grow(pu)
    assert world.grow_timer == pytest.approx(GROW_DURATION)
    assert world.bird.grow_active is True


def test_grow_active_flag_clears_after_expiry(world):
    world.grow_timer = 1 / 120  # one sub-frame remaining
    world.bird.grow_active = True
    world.ready_t = 0.0
    world.pipes.clear()
    world.update(1 / 60)
    assert world.grow_timer == 0.0
    assert world.bird.grow_active is False


def test_radius_returns_to_normal_after_expiry(world):
    world.grow_timer = 0.001
    world.ready_t = 0.0
    world.pipes.clear()
    world.update(1 / 60)
    assert world.bird_radius() == BIRD_R
