"""Sanity checks on tunable constants — catches accidental zeros or
sign-flips that would break gameplay."""
import pytest

from game import config


def test_screen_dimensions_positive():
    assert config.W > 0 and config.H > 0
    assert config.GROUND_Y > 0
    assert config.GROUND_Y < config.H


def test_physics_constants_signs():
    assert config.GRAVITY > 0
    assert config.FLAP_V < 0          # flap goes UP (negative y in pygame)
    assert config.MAX_FALL > 0
    assert config.SCROLL_BASE > 0
    assert config.SCROLL_MAX >= config.SCROLL_BASE


def test_pipe_geometry_sane():
    assert config.PIPE_W > 0
    assert config.PIPE_SPACING > config.PIPE_W
    assert config.GAP_START > config.GAP_MIN > 0


def test_bird_geometry_sane():
    assert 0 < config.BIRD_X < config.W
    assert config.BIRD_R > 0
    assert config.COIN_R > 0
    assert config.POWERUP_R > 0


def test_powerup_durations_positive():
    for name in ("TRIPLE_DURATION", "MAGNET_DURATION", "SLOWMO_DURATION",
                 "KFC_DURATION", "GHOST_DURATION", "GROW_DURATION"):
        assert getattr(config, name) > 0, f"{name} must be > 0"


def test_powerup_chance_in_range():
    assert 0.0 < config.POWERUP_CHANCE <= 1.0
    assert config.POWERUP_COOLDOWN >= 0


def test_slowmo_scale_lt_one():
    """Slow-mo must actually slow the world down."""
    assert 0.0 < config.SLOWMO_SCALE < 1.0


def test_grow_scale_gt_one():
    """Grow must actually scale the bird UP."""
    assert config.GROW_SCALE > 1.0


def test_magnet_radius_positive():
    assert config.MAGNET_RADIUS > config.BIRD_R


def test_coin_rush_constants():
    assert config.COIN_RUSH_INTERVAL >= 1
    assert config.COIN_RUSH_GAP_BOOST > 1.0
    assert config.COIN_RUSH_COINS > 0


def test_powerup_weights_shape():
    assert isinstance(config.POWERUP_WEIGHTS, tuple)
    assert len(config.POWERUP_WEIGHTS) >= 1
    expected_kinds = {"triple", "magnet", "slowmo", "kfc",
                      "ghost", "grow", "surprise"}
    seen = {kind for kind, _ in config.POWERUP_WEIGHTS}
    assert seen.issubset(expected_kinds)
    for kind, weight in config.POWERUP_WEIGHTS:
        assert isinstance(kind, str)
        assert isinstance(weight, (int, float))
        assert weight > 0


def test_save_files_strings():
    assert isinstance(config.SAVE_FILE, str)
    assert isinstance(config.SCORES_FILE, str)
    assert config.SAVE_FILE.endswith(".json")
    assert config.SCORES_FILE.endswith(".json")
