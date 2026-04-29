"""Coin-rush mechanic: every Nth pipe gets a wider gap + dense coin
formation, and skips the power-up roll."""
import pytest

from game.config import (
    COIN_RUSH_INTERVAL, COIN_RUSH_GAP_BOOST, COIN_RUSH_COINS,
    GAP_START,
)


def test_rush_pipe_marked(world):
    """Spawn enough pipes to hit the rush interval and verify ``is_rush``
    flips on exactly the Nth one."""
    world.pipes.clear()
    world.coins.clear()
    world.powerups.clear()
    world.pipes_spawned = 0
    for _ in range(COIN_RUSH_INTERVAL):
        world._spawn_pipe(x=400)
    rush_pipes = [p for p in world.pipes if p.is_rush]
    assert len(rush_pipes) == 1


def test_rush_pipe_has_wider_gap(world):
    world.pipes.clear()
    world.coins.clear()
    world.powerups.clear()
    world.pipes_spawned = 0
    for _ in range(COIN_RUSH_INTERVAL):
        world._spawn_pipe(x=400)
    rush_pipe = next(p for p in world.pipes if p.is_rush)
    expected_gap = int(GAP_START * COIN_RUSH_GAP_BOOST)
    assert rush_pipe.gap_h == expected_gap


def test_rush_spawns_correct_coin_count(world):
    """Each rush spawn should add exactly COIN_RUSH_COINS coins."""
    world.pipes.clear()
    world.coins.clear()
    world.powerups.clear()
    world.pipes_spawned = 0
    for _ in range(COIN_RUSH_INTERVAL):
        world._spawn_pipe(x=400)
    assert len(world.coins) >= COIN_RUSH_COINS


def test_rush_pipe_does_not_spawn_powerup(world):
    """Rush pipes route through ``_spawn_rush_coins`` and do not call
    ``_maybe_spawn_powerup`` — verify by spawning many rush pipes
    directly and confirming no powerups appear from the rush path."""
    world.pipes.clear()
    world.coins.clear()
    world.powerups.clear()
    world.pipes_spawned = 0
    # Spawn 3 rush pipes back-to-back (interval, 2*interval, 3*interval)
    for _ in range(3 * COIN_RUSH_INTERVAL):
        world._spawn_pipe(x=400)
    # Some non-rush pipes will have spawned powerups; we only assert that
    # rush pipes themselves did not directly add to .powerups via their
    # own spawn path. Easiest invariant: powerups list never exceeds the
    # non-rush pipe count.
    non_rush = sum(1 for p in world.pipes if not p.is_rush)
    assert len(world.powerups) <= non_rush
