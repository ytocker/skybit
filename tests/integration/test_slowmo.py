"""Slowmo: world scales by SLOWMO_SCALE; bird physics stay at 1.0."""
import pytest

from game.config import SLOWMO_SCALE


def test_pipes_scroll_slower_under_slowmo(world):
    world.ready_t = 0.0
    pipe_x_start = world.pipes[0].x
    # Burn ~1s of normal updates
    for _ in range(60):
        world.update(1 / 60)
        if world.game_over:
            break
    drift_normal = pipe_x_start - world.pipes[0].x

    # Reset and run again under slowmo
    from game.world import World
    world2 = World()
    world2.ready_t = 0.0
    world2.slowmo_timer = 999.0
    pipe_x_start_2 = world2.pipes[0].x
    for _ in range(60):
        world2.update(1 / 60)
        if world2.game_over:
            break
    drift_slow = pipe_x_start_2 - world2.pipes[0].x

    # Allow up to 5% slack for off-screen culling timing
    assert drift_slow < drift_normal
    # The ratio should be close to SLOWMO_SCALE (within ±15% slack)
    if drift_normal > 0:
        ratio = drift_slow / drift_normal
        assert ratio == pytest.approx(SLOWMO_SCALE, abs=0.15)


def test_bird_physics_not_scaled_by_slowmo(world):
    """The bird's y-velocity advances under real dt regardless of slowmo —
    flapping must feel responsive even when the world crawls."""
    world.ready_t = 0.0
    world.slowmo_timer = 999.0
    vy0 = world.bird.vy
    world.update(0.5)
    # Gravity is applied at full real dt, so vy should grow by ~GRAVITY*0.5
    from game.config import GRAVITY
    expected = vy0 + GRAVITY * 0.5
    # Allow some slack for clamping etc.
    assert world.bird.vy >= min(expected, 700.0) * 0.95


def test_slowmo_timer_decays_in_real_time(world):
    """The buff itself should NOT self-extend under slowmo — its timer
    decays at real dt, not scaled dt."""
    world.ready_t = 0.0
    world.slowmo_timer = 1.0
    world.update(0.5)
    # Slowmo should have lost 0.5 s of real time (not 0.5 * 0.7).
    assert world.slowmo_timer == pytest.approx(0.5, abs=0.05)
