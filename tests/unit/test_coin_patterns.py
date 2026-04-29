"""Coin-pattern geometry: ``arc/line/cluster`` for normal pipes,
``wave/s_curve/chevron/oval/double_arc`` for coin-rush pipes."""
import pytest

from game.config import COIN_RUSH_COINS
from game.entities import Pipe


def _spawn_normal(world, pattern, pipe_x=400, gap_y=300, gap_h=170):
    """Force ``random.choice`` to return ``pattern`` and spawn coins."""
    import random
    real_choice = random.choice

    def fake_choice(seq):
        # Only intercept the pattern selection (3-tuple); pass everything
        # else through.
        if seq == ("arc", "line", "cluster"):
            return pattern
        return real_choice(seq)

    random.choice = fake_choice
    try:
        world.coins.clear()
        p = Pipe(pipe_x, gap_y, gap_h)
        world._spawn_coins_in_gap(p)
    finally:
        random.choice = real_choice
    return list(world.coins)


def _spawn_rush(world, variant, pipe_x=400, gap_y=300, gap_h=200):
    """Force the rush variant and spawn 14 coins."""
    import random
    real_choice = random.choice
    rush_kinds = ("wave", "s_curve", "chevron", "oval", "double_arc")

    def fake_choice(seq):
        if tuple(seq) == rush_kinds:
            return variant
        return real_choice(seq)

    random.choice = fake_choice
    try:
        world.coins.clear()
        p = Pipe(pipe_x, gap_y, gap_h)
        world._spawn_rush_coins(p)
    finally:
        random.choice = real_choice
    return list(world.coins)


def test_arc_pattern_spawns_5_coins(world):
    coins = _spawn_normal(world, "arc")
    assert len(coins) == 5


def test_line_pattern_spawns_4_coins(world):
    coins = _spawn_normal(world, "line")
    assert len(coins) == 4


def test_cluster_pattern_spawns_5_coins(world):
    coins = _spawn_normal(world, "cluster")
    assert len(coins) == 5


@pytest.mark.parametrize("variant",
                         ["wave", "s_curve", "chevron", "oval", "double_arc"])
def test_rush_variants_all_produce_correct_count(world, variant):
    coins = _spawn_rush(world, variant)
    assert len(coins) == COIN_RUSH_COINS


def test_line_pattern_y_constant(world):
    """In ``line`` mode, every coin sits at gap_y."""
    coins = _spawn_normal(world, "line", gap_y=300)
    ys = {c.y for c in coins}
    assert ys == {300}


def test_cluster_centred_at_gap(world):
    """Cluster is symmetric around (cx, gap_y) — sums of relative offsets
    should be near zero."""
    gap_y = 300
    coins = _spawn_normal(world, "cluster", gap_y=gap_y)
    cy = sum(c.y for c in coins) / len(coins)
    assert cy == pytest.approx(gap_y, abs=1.0)


def test_rush_oval_closes_loop(world):
    """``oval`` is parametric; first and last sample should be near each
    other (within ~half a coin span)."""
    coins = _spawn_rush(world, "oval")
    first, last = coins[0], coins[-1]
    # Distance between consecutive samples on a 14-step ellipse
    import math
    dx = first.x - last.x
    dy = first.y - last.y
    d = math.hypot(dx, dy)
    # The pitch between samples on a closed loop is < the loop's
    # bounding-box diameter; 80px is a generous upper bound.
    assert d < 80
