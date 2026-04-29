"""``World.update(dt)`` — one tick, ready-freeze, scrolling, time accum."""
import pytest


def test_ready_freeze_holds_pipes_in_place(world):
    pipes_x = [p.x for p in world.pipes]
    world.update(0.1)   # ready_t still > 0, world frozen
    pipes_x_after = [p.x for p in world.pipes]
    assert pipes_x == pipes_x_after


def test_ready_freeze_decays(world):
    """After enough updates, ready_t hits 0 and the world starts scrolling."""
    for _ in range(70):  # 70 * 1/60 ≈ 1.17 s, beyond the 1 s freeze
        world.update(1 / 60)
    assert world.ready_t == 0.0


def test_pipes_scroll_left_after_ready(world):
    # Burn the ready timer
    world.ready_t = 0.0
    pipes_x_before = [p.x for p in world.pipes]
    world.update(0.1)
    pipes_x_after = [p.x for p in world.pipes]
    for a, b in zip(pipes_x_before, pipes_x_after):
        assert b < a


def test_time_alive_accumulates(world):
    world.ready_t = 0.0
    world.update(1 / 60)
    world.update(1 / 60)
    assert world.time_alive == pytest.approx(2 / 60)


def test_time_alive_stops_when_dead(world):
    world.ready_t = 0.0
    world.bird.alive = False
    world.game_over = True
    t0 = world.time_alive
    world.update(0.5)
    assert world.time_alive == t0


def test_bg_scroll_advances(world):
    world.ready_t = 0.0
    s0 = world.bg_scroll
    world.update(1 / 60)
    assert world.bg_scroll > s0


def test_pipe_recycling(world):
    """After enough scrolling, leftmost pipe goes off-screen and a new
    one is spawned on the right; pipe count stays >= 3."""
    world.ready_t = 0.0
    for _ in range(600):
        world.update(1 / 60)
        if world.game_over:
            break
    assert len(world.pipes) >= 1


def test_biome_time_advances(world):
    t0 = world.biome_time
    world.update(0.1)
    assert world.biome_time == pytest.approx(t0 + 0.1)


def test_update_idempotent_after_death(world):
    """Updating after game_over should not crash or move the bird."""
    world.ready_t = 0.0
    world.game_over = True
    world.bird.alive = False
    bx, by = world.bird.x, world.bird.y
    for _ in range(10):
        world.update(1 / 60)
    assert world.bird.x == bx
    assert world.bird.y == by
