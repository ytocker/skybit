"""Top-level ``scenes.App`` state machine: menu → play → death → stats →
leaderboard transitions and pause toggles."""
import pytest

from game.scenes import (
    STATE_MENU, STATE_PLAY, STATE_PAUSE,
    STATE_STATS, STATE_NAMEENTRY, STATE_LEADERBOARD,
    STATE_GAMEOVER,
)


def test_initial_state_is_menu(app):
    assert app.state == STATE_MENU


def test_flap_input_in_menu_starts_play(app):
    app._flap_input()
    assert app.state == STATE_PLAY


def test_pause_toggle(app):
    app.state = STATE_PLAY
    app._toggle_pause()
    assert app.state == STATE_PAUSE
    app._toggle_pause()
    assert app.state == STATE_PLAY


def test_pause_toggle_only_active_in_play_or_pause(app):
    """Pause toggle does nothing when on the menu / stats / leaderboard."""
    app.state = STATE_MENU
    app._toggle_pause()
    assert app.state == STATE_MENU


def test_death_routes_to_stats(app):
    app.state = STATE_PLAY
    # Force a death: mark world.game_over and call _on_death directly
    app.world.game_over = True
    app._on_death()
    assert app.state == STATE_STATS


def test_qualify_check_for_empty_leaderboard():
    """Any positive score qualifies when the board has < 10 entries."""
    from game.scenes import App
    assert App._qualifies_for_top10([], 1) is True
    assert App._qualifies_for_top10([], 0) is False  # zero never qualifies


def test_qualify_check_for_full_leaderboard():
    full = [{"name": str(i), "score": (10 - i) * 100} for i in range(10)]
    # Bottom score is 100 (i=9). 99 doesn't qualify; 101 does.
    assert App_qualifies(full, 99) is False
    assert App_qualifies(full, 101) is True
    # Tying the bottom score does not qualify (strictly greater).
    assert App_qualifies(full, 100) is False


def App_qualifies(scores, score):
    from game.scenes import App
    return App._qualifies_for_top10(scores, score)


def test_advance_past_stats_native_path_to_leaderboard(app, monkeypatch,
                                                       tmp_scores):
    """Native (non-emscripten) path: short-circuit to leaderboard if score
    doesn't qualify."""
    import sys
    monkeypatch.setattr(sys, "platform", "linux")
    app.state = STATE_STATS
    app._stats_t = 1.0
    app.world.score = 0  # cannot qualify
    app._advance_past_stats()
    assert app.state == STATE_LEADERBOARD


def test_advance_past_stats_native_qualifies_to_nameentry(app, monkeypatch,
                                                          tmp_scores):
    import sys
    monkeypatch.setattr(sys, "platform", "linux")
    app.state = STATE_STATS
    app._stats_t = 1.0
    app.world.score = 9999
    app._advance_past_stats()
    assert app.state == STATE_NAMEENTRY


def test_session_best_tracks_max(app):
    """``session_best`` is updated on death only when score exceeds it."""
    assert app.session_best == 0
    app.state = STATE_PLAY
    app.world.score = 50
    app.world.game_over = True
    app._on_death()
    assert app.session_best == 50

    # New run: lower score should NOT lower session_best
    app.state = STATE_PLAY
    app.world.score = 10
    app.world.game_over = True
    app._on_death()
    assert app.session_best == 50


def test_restart_creates_fresh_world(app):
    app.state = STATE_PLAY
    app.world.score = 999
    app._restart()
    assert app.world.score == 0
    assert app.state == STATE_PLAY


def test_start_play_resets_world(app):
    app.world.score = 999
    app._start_play()
    assert app.world.score == 0
    assert app.state == STATE_PLAY
