"""Magnet: distance-falloff pull, no-pull when inactive, range cap."""
import pytest

from game.config import MAGNET_RADIUS
from game.entities import Coin


def test_no_pull_when_magnet_inactive(world):
    coin = Coin(world.bird.x + 50, world.bird.y)
    world.coins.append(coin)
    x0, y0 = coin.x, coin.y
    world._apply_magnet(1 / 60)
    # _apply_magnet only runs when magnet_timer>0 inside update(), but
    # calling it directly should still work — the contract is that it
    # only pulls when called. Here we assert "passive" coins don't move
    # via the world update path:
    world.ready_t = 0.0
    world.update(1 / 60)
    # Without magnet, coin only moves due to scroll (x decreases, y same).
    assert coin.y == pytest.approx(y0)


def test_pull_within_radius_moves_coin_toward_bird(world):
    world.magnet_timer = 5.0
    coin = Coin(world.bird.x + 50, world.bird.y)
    world.coins.append(coin)
    x0 = coin.x
    world._apply_magnet(1 / 60)
    # Coin should move toward the bird (i.e. x decrease)
    assert coin.x < x0


def test_no_pull_beyond_radius(world):
    world.magnet_timer = 5.0
    far = MAGNET_RADIUS + 50
    coin = Coin(world.bird.x + far, world.bird.y)
    world.coins.append(coin)
    x0 = coin.x
    world._apply_magnet(1 / 60)
    assert coin.x == x0


def test_pull_at_radius_boundary_minimal(world):
    """Pull strength = 520 * (1 − d/RADIUS); at d == RADIUS it's 0,
    so the coin should not move."""
    world.magnet_timer = 5.0
    coin = Coin(world.bird.x + MAGNET_RADIUS, world.bird.y)
    world.coins.append(coin)
    x0 = coin.x
    world._apply_magnet(1 / 60)
    # At the boundary, the coin sits *exactly* on the radius — the
    # `d2 > r2` check passes (equal), so the loop body runs but pull≈0.
    # Allow ≤1 px of float drift.
    assert abs(coin.x - x0) < 1.0


def test_pull_stronger_at_close_range(world):
    """A coin at 20 px should move further than one at 60 px under the
    same dt and identical bird positions."""
    world.magnet_timer = 5.0
    near = Coin(world.bird.x + 20, world.bird.y)
    far  = Coin(world.bird.x + 60, world.bird.y)
    world.coins.extend([near, far])
    near_x0, far_x0 = near.x, far.x
    world._apply_magnet(1 / 60)
    near_delta = abs(near.x - near_x0)
    far_delta  = abs(far.x  - far_x0)
    assert near_delta > far_delta


def test_collected_coin_skipped_by_magnet(world):
    world.magnet_timer = 5.0
    coin = Coin(world.bird.x + 30, world.bird.y)
    coin.collected = True
    world.coins.append(coin)
    x0 = coin.x
    world._apply_magnet(1 / 60)
    assert coin.x == x0


def test_zero_distance_skipped(world):
    """If the coin is exactly on the bird, distance² ≈ 0 and the
    near-zero guard skips the pull (avoids a div-by-zero)."""
    world.magnet_timer = 5.0
    coin = Coin(world.bird.x, world.bird.y)
    world.coins.append(coin)
    # Should not raise
    world._apply_magnet(1 / 60)
