"""Coin pickup → score+coin_count, power-up pickup → activation."""
import pytest


from game.entities import Coin, PowerUp


def _place_at_bird(world, ent):
    """Position an entity right on top of the bird so the next pickup
    pass collects it."""
    ent.x = world.bird.x
    ent.y = world.bird.y


def test_coin_collected_increments_score(world):
    coin = Coin(world.bird.x, world.bird.y)
    world.coins.append(coin)
    s0 = world.score
    cc0 = world.coin_count
    world._check_pickups()
    assert coin.collected is True
    assert world.score == s0 + 1
    assert world.coin_count == cc0 + 1


def test_coin_far_from_bird_not_collected(world):
    coin = Coin(world.bird.x + 500, world.bird.y)
    world.coins.append(coin)
    world._check_pickups()
    assert coin.collected is False
    assert world.score == 0


def test_coin_with_triple_active_scores_three(world):
    world.triple_timer = 5.0
    coin = Coin(world.bird.x, world.bird.y)
    world.coins.append(coin)
    world._check_pickups()
    assert world.score == 3
    assert world.coin_count == 1


def test_powerup_pickup_activates(world):
    pu = PowerUp(world.bird.x, world.bird.y, kind="triple")
    world.powerups.append(pu)
    world._check_pickups()
    assert pu.collected is True
    assert world.triple_timer > 0


def test_powerup_pickup_increments_picked_counter(world):
    pu = PowerUp(world.bird.x, world.bird.y, kind="magnet")
    world.powerups.append(pu)
    world._check_pickups()
    assert world.powerups_picked["magnet"] == 1


def test_already_collected_coin_not_double_counted(world):
    coin = Coin(world.bird.x, world.bird.y)
    coin.collected = True   # pre-flagged
    world.coins.append(coin)
    world._check_pickups()
    assert world.score == 0


def test_already_collected_powerup_not_double_activated(world):
    pu = PowerUp(world.bird.x, world.bird.y, kind="magnet")
    pu.collected = True
    world.powerups.append(pu)
    world._check_pickups()
    assert world.magnet_timer == 0


def test_coin_pickup_emits_particles(world):
    coin = Coin(world.bird.x, world.bird.y)
    world.coins.append(coin)
    p0 = len(world.particles)
    world._check_pickups()
    assert len(world.particles) > p0


def test_coin_pickup_emits_float_text(world):
    coin = Coin(world.bird.x, world.bird.y)
    world.coins.append(coin)
    f0 = len(world.float_texts)
    world._check_pickups()
    assert len(world.float_texts) == f0 + 1
