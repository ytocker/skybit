"""End-to-end collision: ground / ceiling / pipe / ghost-immunity / grow."""
import pytest

from game.config import BIRD_R, GROUND_Y, GROW_SCALE


def test_ground_collision_kills_bird(world):
    world.ready_t = 0.0
    world.bird.y = GROUND_Y + 1
    world.update(1 / 60)
    assert world.game_over is True
    assert world.bird.alive is False


def test_ceiling_collision_kills_bird(world):
    world.ready_t = 0.0
    world.bird.y = -1   # already past the top
    world.update(1 / 60)
    assert world.game_over is True


def test_no_collision_in_safe_air(world):
    world.ready_t = 0.0
    world.bird.y = GROUND_Y / 2
    # Move pipes well off-screen left to avoid coincidental collisions
    for p in world.pipes:
        p.x = -500
    # Re-fill the pipe list since update() culls off-screen pipes
    world.update(1 / 60)
    # Bird may still be alive (no pipes left to hit; ground/ceiling clear)
    assert world.bird.alive is True


def test_pipe_collision_kills_bird(world):
    world.ready_t = 0.0
    # Place a pipe right under the bird's centre with a tiny gap
    from game.entities import Pipe
    world.pipes = [Pipe(world.bird.x, world.bird.y + 200, 10)]
    world.update(1 / 60)
    assert world.game_over is True


def test_ghost_phases_through_pipes(world):
    world.ready_t = 0.0
    world.ghost_timer = 5.0
    from game.entities import Pipe
    # Pipe with a tiny gap squarely on the bird
    world.pipes = [Pipe(world.bird.x, world.bird.y + 200, 10)]
    world.update(1 / 60)
    assert world.bird.alive is True
    assert world.game_over is False


def test_ghost_does_not_phase_through_ground(world):
    world.ready_t = 0.0
    world.ghost_timer = 5.0
    world.bird.y = GROUND_Y + 10
    world.update(1 / 60)
    assert world.game_over is True


def test_grow_uses_larger_radius(world):
    world.grow_timer = 5.0
    assert world.bird_radius() == pytest.approx(BIRD_R * GROW_SCALE)


def test_grow_collision_triggers_earlier(world):
    """A pipe whose gap edge sits right at BIRD_R + 1 px above the bird
    should be safe at normal size but kill the bird while grown."""
    from game.entities import Pipe
    world.ready_t = 0.0
    by = world.bird.y
    bx = world.bird.x
    # Pipe whose top-pillar bottom is BIRD_R + 1 px above the bird
    gap_top = by - BIRD_R - 1
    gap_bot = by + 200
    gap_y = (gap_top + gap_bot) / 2
    gap_h = gap_bot - gap_top

    # Snapshot: the bird should NOT collide at normal size
    world.pipes = [Pipe(bx - 5, gap_y, gap_h)]
    safe_radius = BIRD_R - 2     # what _check_collisions actually uses
    assert not world.pipes[0].collides_circle(bx, by, safe_radius)

    # Now grow the bird and re-check
    world.grow_timer = 5.0
    grown_radius = world.bird_radius() - 2
    assert world.pipes[0].collides_circle(bx, by, grown_radius)


def test_die_only_fires_once(world):
    """``_die`` should be idempotent — call it twice, only one round of
    death particles spawns."""
    world._die()
    n1 = len(world.particles)
    world._die()
    n2 = len(world.particles)
    assert n2 == n1


def test_death_particles_spawn(world):
    n_before = len(world.particles)
    world._die()
    assert len(world.particles) > n_before
    assert world.bird.alive is False
    assert world.shake_t > 0
