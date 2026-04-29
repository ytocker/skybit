"""PowerUp entity construction & update."""
import pytest

from game.entities import PowerUp


KINDS = ["triple", "magnet", "slowmo", "kfc", "ghost", "grow", "surprise"]


@pytest.mark.parametrize("kind", KINDS)
def test_construct_each_kind(kind):
    p = PowerUp(50, 60, kind=kind)
    assert p.x == 50
    assert p.y == 60
    assert p.kind == kind
    assert p.collected is False
    assert p.pulse == 0.0


def test_default_kind_is_triple():
    p = PowerUp(0, 0)
    assert p.kind == "triple"


def test_update_advances_pulse():
    p = PowerUp(0, 0, kind="triple")
    pulse0 = p.pulse
    p.update(0.1)
    assert p.pulse > pulse0


def test_update_does_not_move():
    p = PowerUp(50, 60, kind="magnet")
    for _ in range(10):
        p.update(0.1)
    assert p.x == 50
    assert p.y == 60


def test_collected_starts_false():
    p = PowerUp(0, 0)
    assert p.collected is False
