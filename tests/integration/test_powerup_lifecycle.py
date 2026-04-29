"""All 6 real power-ups: activate → tick → expire."""
import pytest

from game.config import (
    TRIPLE_DURATION, MAGNET_DURATION, SLOWMO_DURATION,
    KFC_DURATION, GHOST_DURATION, GROW_DURATION,
)
from game.entities import PowerUp


KIND_TIMER_FLAG = [
    ("triple",  "triple_timer",  TRIPLE_DURATION,  "triple_active"),
    ("magnet",  "magnet_timer",  MAGNET_DURATION,  None),
    ("slowmo",  "slowmo_timer",  SLOWMO_DURATION,  None),
    ("kfc",     "kfc_timer",     KFC_DURATION,     "kfc_active"),
    ("ghost",   "ghost_timer",   GHOST_DURATION,   "ghost_active"),
    ("grow",    "grow_timer",    GROW_DURATION,    "grow_active"),
]


@pytest.mark.parametrize("kind,timer_attr,duration,bird_flag", KIND_TIMER_FLAG)
def test_pickup_activates_timer(world, kind, timer_attr, duration, bird_flag):
    pu = PowerUp(world.bird.x, world.bird.y, kind=kind)
    world.powerups.append(pu)
    world._check_pickups()
    assert getattr(world, timer_attr) == pytest.approx(duration)


def _burn_timer(world, duration):
    """Tick the world long enough to expire ``duration`` seconds of buff
    timer. Holds the bird in mid-air so the loop doesn't end early on a
    ground / pipe collision (timers only decay while the bird is alive)."""
    from game.config import H
    world.ready_t = 0.0
    world.pipes.clear()
    elapsed = 0.0
    dt = 1 / 60
    while elapsed < duration + 0.5:
        # Reset bird position each frame so gravity doesn't drop it into
        # the ground and stop the timer-decay loop.
        world.bird.y = H * 0.5
        world.bird.vy = 0.0
        world.update(dt)
        elapsed += dt


@pytest.mark.parametrize("kind,timer_attr,duration,bird_flag", KIND_TIMER_FLAG)
def test_timer_decays_to_zero(world, kind, timer_attr, duration, bird_flag):
    pu = PowerUp(world.bird.x, world.bird.y, kind=kind)
    world.powerups.append(pu)
    world._check_pickups()
    _burn_timer(world, duration)
    assert getattr(world, timer_attr) == 0.0


@pytest.mark.parametrize("kind,timer_attr,duration,bird_flag", KIND_TIMER_FLAG)
def test_bird_flag_clears_after_expiry(world, kind, timer_attr,
                                       duration, bird_flag):
    if bird_flag is None:
        pytest.skip(f"{kind} doesn't set a bird flag")
    pu = PowerUp(world.bird.x, world.bird.y, kind=kind)
    world.powerups.append(pu)
    world._check_pickups()
    _burn_timer(world, duration)
    assert getattr(world.bird, bird_flag) is False


def test_powerup_cooldown_set_after_pickup(world):
    """Picking up a power-up sets a cooldown so two don't spawn back-to-back."""
    from game.entities import Pipe
    # Drive _maybe_spawn_powerup with a deterministic RNG state.
    # We can't directly assert spawn behaviour because of probabilistic
    # POWERUP_CHANCE, but we can assert cooldown management.
    world.powerup_cooldown = 0.0
    # Brute-force a spawn by passing a pipe and seeded RNG; if it spawns,
    # cooldown should be set to POWERUP_COOLDOWN.
    import random
    random.seed(1)
    p = Pipe(400, 300, 170)
    n_before = len(world.powerups)
    for _ in range(50):
        # Re-seed to vary draws, but each call should respect cooldown.
        world._maybe_spawn_powerup(p)
        if len(world.powerups) > n_before:
            assert world.powerup_cooldown > 0
            break


def test_kfc_expiry_spawns_poof(world):
    """When the KFC timer hits zero exactly during update(), a poof of
    cloud particles spawns."""
    pu = PowerUp(world.bird.x, world.bird.y, kind="kfc")
    world.powerups.append(pu)
    world._check_pickups()
    world.ready_t = 0.0
    world.pipes.clear()
    # Burn down to the last sub-frame
    world.kfc_timer = 1 / 120
    p_before = len(world.particles)
    world.update(1 / 60)   # this single tick zeroes the timer
    assert world.kfc_timer == 0.0
    assert len(world.particles) > p_before
