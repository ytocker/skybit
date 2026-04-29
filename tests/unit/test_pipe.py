"""Pipe geometry, collision, off-screen detection."""
import pygame
import pytest

from game.config import PIPE_W, GROUND_Y
from game.entities import Pipe


def test_init_attributes():
    p = Pipe(x=200, gap_y=300, gap_h=170)
    assert p.x == 200
    assert p.gap_y == 300
    assert p.gap_h == 170
    assert p.scored is False
    assert p.is_rush is False
    assert isinstance(p.seed, int)


def test_top_rect_above_gap():
    p = Pipe(x=200, gap_y=300, gap_h=170)
    top = p.top_rect
    assert top.x == 200
    assert top.y == 0
    assert top.width == PIPE_W
    assert top.bottom == int(300 - 170 / 2)


def test_bot_rect_below_gap():
    p = Pipe(x=200, gap_y=300, gap_h=170)
    bot = p.bot_rect
    assert bot.x == 200
    assert bot.y == int(300 + 170 / 2)
    assert bot.bottom == GROUND_Y
    assert bot.width == PIPE_W


def test_off_screen_when_far_left():
    p = Pipe(x=-100, gap_y=300, gap_h=170)
    assert p.off_screen() is True


def test_not_off_screen_when_visible():
    p = Pipe(x=100, gap_y=300, gap_h=170)
    assert p.off_screen() is False


def test_collides_circle_in_top_pillar():
    p = Pipe(x=200, gap_y=300, gap_h=170)
    # Circle squarely inside the top pillar
    assert p.collides_circle(200 + PIPE_W // 2, 50, 14) is True


def test_collides_circle_in_bot_pillar():
    p = Pipe(x=200, gap_y=300, gap_h=170)
    # Circle squarely inside the bottom pillar
    assert p.collides_circle(200 + PIPE_W // 2, GROUND_Y - 20, 14) is True


def test_no_collision_in_gap_centre():
    p = Pipe(x=200, gap_y=300, gap_h=170)
    # Right inside the gap, dead-centre
    assert p.collides_circle(200 + PIPE_W // 2, 300, 10) is False


def test_no_collision_far_to_the_left():
    p = Pipe(x=200, gap_y=300, gap_h=170)
    assert p.collides_circle(50, 300, 10) is False


def test_no_collision_far_to_the_right():
    p = Pipe(x=200, gap_y=300, gap_h=170)
    assert p.collides_circle(500, 300, 10) is False


def test_collision_uses_bounding_box_of_circle():
    """The collision is rect-vs-rect (circle bounding box). A radius=20
    circle at the gap edge that just clips into the pillar should collide."""
    p = Pipe(x=200, gap_y=300, gap_h=170)
    edge_y = int(300 - 170 / 2)  # bottom of top pillar
    # Centre 5 px below the edge with radius 20 → bbox extends 15 px
    # above the edge → into the pillar.
    assert p.collides_circle(200 + PIPE_W // 2, edge_y + 5, 20) is True


def test_seed_stable_per_instance():
    p = Pipe(x=200, gap_y=300, gap_h=170)
    s1 = p.seed
    s2 = p.seed
    assert s1 == s2
