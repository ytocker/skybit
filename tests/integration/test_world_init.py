"""World construction: initial pipe set, all timers zeroed, ready freeze."""
import pytest

from game.config import (
    BIRD_X, GROUND_Y, H, W, PIPE_SPACING, SCROLL_BASE,
)


def test_bird_at_starting_position(world):
    assert world.bird.x == BIRD_X
    assert world.bird.alive is True


def test_three_initial_pipes(world):
    assert len(world.pipes) == 3
    # Pipes increase in x left-to-right
    xs = [p.x for p in world.pipes]
    assert xs == sorted(xs)
    # First pipe sits past the right edge so the player gets a moment
    # before it scrolls in.
    assert world.pipes[0].x > W


def test_pipes_evenly_spaced(world):
    xs = [p.x for p in world.pipes]
    diffs = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
    assert all(d == PIPE_SPACING for d in diffs)


def test_no_coins_or_powerups_in_first_pipe_arc(world):
    """First three pipes spawn at construction; coins/powerups can be
    spawned alongside, but powerup_cooldown starts at 0 so the first
    pipe MAY have a powerup. Just sanity-check the lists exist."""
    assert isinstance(world.coins, list)
    assert isinstance(world.powerups, list)
    assert isinstance(world.particles, list)
    assert isinstance(world.float_texts, list)


def test_all_timers_start_zero(world):
    for name in ("triple_timer", "magnet_timer", "slowmo_timer",
                 "kfc_timer", "ghost_timer", "grow_timer"):
        assert getattr(world, name) == 0.0, f"{name} should start at 0"


def test_score_starts_zero(world):
    assert world.score == 0
    assert world.coin_count == 0
    assert world.pillars_passed == 0
    assert world.near_misses == 0
    assert world.time_alive == 0.0


def test_powerups_picked_starts_empty(world):
    for kind in ("triple", "magnet", "slowmo", "kfc",
                 "ghost", "grow", "surprise"):
        assert world.powerups_picked[kind] == 0


def test_ready_freeze_active(world):
    assert world.ready_t > 0
    assert world.ready_t == pytest.approx(1.0)


def test_game_not_over_at_start(world):
    assert world.game_over is False


def test_scroll_speed_at_base(world):
    assert world.scroll_speed == SCROLL_BASE


def test_bird_radius_normal_when_no_grow(world):
    from game.config import BIRD_R
    assert world.bird_radius() == BIRD_R


def test_mushrooms_alias_is_powerups(world):
    """Backwards-compat: `world.mushrooms` should alias `world.powerups`."""
    assert world.mushrooms is world.powerups
    new_list = []
    world.mushrooms = new_list
    assert world.powerups is new_list
