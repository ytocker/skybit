"""Triple: coin pickup pays out 3 instead of 1 while active."""
import pytest

from game.entities import Coin


def test_coin_value_three_when_triple_active(world):
    world.triple_timer = 5.0
    coin = Coin(world.bird.x, world.bird.y)
    world.coins.append(coin)
    world._check_pickups()
    assert world.score == 3
    assert world.coin_count == 1   # coin COUNT is unchanged; only score *3


def test_coin_value_one_when_triple_inactive(world):
    coin = Coin(world.bird.x, world.bird.y)
    world.coins.append(coin)
    world._check_pickups()
    assert world.score == 1


def test_three_coins_under_triple_score_nine(world):
    """Clear the world's pre-spawned coins first — World()'s constructor
    seeds 3 pipes + their coin patterns, which would otherwise be picked
    up by the same _check_pickups call."""
    world.coins.clear()
    world.triple_timer = 5.0
    for _ in range(3):
        world.coins.append(Coin(world.bird.x, world.bird.y))
    world._check_pickups()
    assert world.score == 9
    assert world.coin_count == 3


def test_triple_expires_then_normal_score(world):
    """Pick a coin under triple, then pick another after triple expires."""
    world.triple_timer = 0.001
    coin1 = Coin(world.bird.x, world.bird.y)
    world.coins.append(coin1)
    world._check_pickups()    # +3
    assert world.score == 3
    world.ready_t = 0.0
    world.pipes.clear()
    world.update(1 / 60)
    assert world.triple_timer == 0.0
    coin2 = Coin(world.bird.x, world.bird.y)
    world.coins.append(coin2)
    world._check_pickups()    # +1
    assert world.score == 4
