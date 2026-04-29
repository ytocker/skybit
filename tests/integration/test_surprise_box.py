"""SURPRISE box pickup resolves to one of the 6 real kinds, weighted
roughly uniformly. Both the ``surprise`` and the resolved kind's pick
counters increment."""
import random

import pytest

from game.entities import PowerUp


REAL_KINDS = ("triple", "magnet", "slowmo", "kfc", "ghost", "grow")


def _pickup_one_surprise(world):
    pu = PowerUp(world.bird.x, world.bird.y, kind="surprise")
    pu.collected = False
    world._on_powerup(pu)


def test_surprise_increments_surprise_counter(world):
    _pickup_one_surprise(world)
    assert world.powerups_picked["surprise"] == 1


def test_surprise_also_increments_resolved_kind(world):
    """After a surprise pickup, exactly one of the 6 real-kind counters
    should also be at 1."""
    _pickup_one_surprise(world)
    real_total = sum(world.powerups_picked[k] for k in REAL_KINDS)
    assert real_total == 1


def test_surprise_activates_some_real_powerup(world):
    _pickup_one_surprise(world)
    # Exactly one of the 6 real timers should be positive
    timers = {
        "triple":  world.triple_timer,
        "magnet":  world.magnet_timer,
        "slowmo":  world.slowmo_timer,
        "kfc":     world.kfc_timer,
        "ghost":   world.ghost_timer,
        "grow":    world.grow_timer,
    }
    active = [k for k, v in timers.items() if v > 0]
    assert len(active) == 1


def test_surprise_distribution_roughly_uniform(world):
    """600 surprise pickups: each real kind should be hit at least 60
    times (10% of 600 — generous lower bound for a uniform 1/6 draw)."""
    random.seed(123)   # override the autouse seed for this distribution test
    counts = {k: 0 for k in REAL_KINDS}
    for _ in range(600):
        # Reset world state so timers don't shadow new picks
        for k in REAL_KINDS:
            setattr(world, f"{k}_timer", 0.0)
        before = {k: world.powerups_picked[k] for k in REAL_KINDS}
        _pickup_one_surprise(world)
        for k in REAL_KINDS:
            if world.powerups_picked[k] > before[k]:
                counts[k] += 1
                break
    total = sum(counts.values())
    assert total == 600
    for k, n in counts.items():
        assert n >= 60, f"{k} hit only {n}/600 — distribution looks broken"


def test_surprise_reveal_particles_spawn(world):
    p_before = len(world.particles)
    _pickup_one_surprise(world)
    # Reveal spawns 18 particles + the resolved activator's burst (≥ 28
    # for kfc/ghost/grow, 30 for default). Either way, well over 18.
    assert len(world.particles) - p_before >= 18
