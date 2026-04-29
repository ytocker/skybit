"""Per-run scoring stats: pillars_passed, near_misses, time_alive."""
import pytest

from game.config import BIRD_R, PIPE_W


def test_pillar_pass_increments_score_and_pillars(world):
    """Move a pipe past the bird; world.update should bump both."""
    world.ready_t = 0.0
    world.pipes.clear()
    from game.entities import Pipe
    p = Pipe(world.bird.x - 100, world.bird.y, 200)  # already past
    p.scored = False
    world.pipes.append(p)
    world.update(1 / 60)
    assert world.pillars_passed == 1
    assert world.score == 1
    assert p.scored is True


def test_pillar_only_scored_once(world):
    """Multiple updates over the same passed pipe should not re-score."""
    world.ready_t = 0.0
    world.pipes.clear()
    from game.entities import Pipe
    p = Pipe(world.bird.x - 100, world.bird.y, 200)
    p.scored = False
    world.pipes.append(p)
    for _ in range(5):
        world.update(1 / 60)
    assert world.pillars_passed == 1


def test_near_miss_detection(world):
    """A bird flying just inside the gap edge should register a near miss
    when the pipe overlaps the bird's x-range."""
    world.ready_t = 0.0
    world.pipes.clear()
    from game.entities import Pipe
    bx, by = world.bird.x, world.bird.y
    # Need 0 < d_top < 10, where d_top = by - gap_top, gap_top = gap_y - gap_h/2.
    # Pick gap_h=100, gap_top = by - 5 → gap_y = by - 5 + 50 = by + 45.
    gap_h = 100
    gap_y = by + 45
    p = Pipe(bx - 5, gap_y, gap_h)
    world.pipes.append(p)
    world.update(1 / 60)
    assert world.near_misses == 1


def test_near_miss_counted_once_per_pipe(world):
    world.ready_t = 0.0
    world.pipes.clear()
    from game.entities import Pipe
    bx, by = world.bird.x, world.bird.y
    p = Pipe(bx - 5, by + 45, 100)
    world.pipes.append(p)
    for _ in range(5):
        # Hold bird still so geometry doesn't drift across frames.
        world.bird.y = by
        world.bird.vy = 0
        world.update(1 / 60)
        if world.game_over:
            break
    assert world.near_misses <= 1


def test_far_from_edge_no_near_miss(world):
    """Bird centred dead in a wide gap — no near miss expected."""
    world.ready_t = 0.0
    world.pipes.clear()
    from game.entities import Pipe
    p = Pipe(world.bird.x - 5, world.bird.y, 300)
    world.pipes.append(p)
    world.update(1 / 60)
    assert world.near_misses == 0


def test_time_alive_monotonic(world):
    world.ready_t = 0.0
    samples = []
    for _ in range(30):
        world.update(1 / 60)
        samples.append(world.time_alive)
        if world.game_over:
            break
    for a, b in zip(samples, samples[1:]):
        assert b >= a


def test_score_never_negative(world):
    """score can only go up."""
    world.ready_t = 0.0
    for _ in range(100):
        world.update(1 / 60)
        assert world.score >= 0
        if world.game_over:
            break
