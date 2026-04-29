"""Rate-limit + telemetry-dedup tests."""
import os
import tempfile

import pytest

from game.security import ratelimit


@pytest.fixture(autouse=True)
def _isolate_state(monkeypatch, tmp_path):
    """Redirect the native state file into a temp dir so tests are hermetic."""
    monkeypatch.setattr(ratelimit, "_RL_FILE", str(tmp_path / "rl.json"))


def test_first_submit_allowed():
    assert ratelimit.can_submit_score(now=1000.0)


def test_second_submit_within_window_blocked():
    ratelimit.record_submission(now=1000.0)
    assert not ratelimit.can_submit_score(now=1010.0)


def test_submit_after_cooldown_allowed():
    ratelimit.record_submission(now=1000.0)
    assert ratelimit.can_submit_score(now=1000.0 + 31.0)


def test_lb_refresh_debounce():
    assert ratelimit.can_refresh_leaderboard(now=2000.0)
    # Immediate re-check inside the window: blocked.
    assert not ratelimit.can_refresh_leaderboard(now=2001.0)
    assert ratelimit.can_refresh_leaderboard(now=2010.0)


class _W:
    def __init__(self, t, s, p):
        self.time_alive, self.score, self.pillars_passed = t, s, p


def test_telemetry_dedup_same_run():
    w = _W(12.5, 33, 7)
    k1 = ratelimit.telemetry_dedup_key(w)
    assert ratelimit.remember_telemetry_key(k1)
    # Identical run summary → already remembered, refuse second send.
    assert not ratelimit.remember_telemetry_key(k1)


def test_telemetry_dedup_different_run():
    a = ratelimit.telemetry_dedup_key(_W(10.0, 20, 5))
    b = ratelimit.telemetry_dedup_key(_W(11.0, 20, 5))
    assert ratelimit.remember_telemetry_key(a)
    assert ratelimit.remember_telemetry_key(b)
