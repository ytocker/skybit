"""Native local-JSON leaderboard — save / load / sort / cap at 10."""
import json
import pathlib

import pytest

from game import leaderboard


def test_load_returns_empty_when_file_missing(tmp_scores):
    assert leaderboard._load_local() == []


def test_save_and_load_roundtrip(tmp_scores):
    leaderboard._save_local([{"name": "Alice", "score": 100}])
    loaded = leaderboard._load_local()
    assert loaded == [{"name": "Alice", "score": 100}]


def test_load_returns_sorted_descending(tmp_scores):
    leaderboard._save_local([
        {"name": "A", "score": 50},
        {"name": "B", "score": 200},
        {"name": "C", "score": 100},
    ])
    loaded = leaderboard._load_local()
    scores = [e["score"] for e in loaded]
    assert scores == [200, 100, 50]


def test_submit_adds_new_score(tmp_scores):
    leaderboard._native_submit("Bob", 300)
    loaded = leaderboard._load_local()
    assert {"name": "Bob", "score": 300} in loaded


def test_submit_caps_at_top_ten(tmp_scores):
    """Submit 12 entries; only the top 10 should persist after each call."""
    for i in range(12):
        leaderboard._native_submit(f"P{i}", i * 10)   # 0, 10, 20 .. 110
    loaded = leaderboard._load_local()
    assert len(loaded) == 10
    # The top 10 are the highest 10 (20..110)
    scores = sorted([e["score"] for e in loaded], reverse=True)
    assert scores == list(range(110, 10, -10))


def test_fetch_returns_only_first_ten(tmp_scores):
    for i in range(15):
        leaderboard._save_local(
            leaderboard._load_local() + [{"name": f"P{i}", "score": i}]
        )
    fetched = leaderboard._native_fetch()
    assert len(fetched) == 10


def test_corrupt_file_returns_empty(tmp_scores):
    """A malformed JSON file should not raise — returns empty list."""
    p = pathlib.Path(leaderboard.SCORES_FILE)
    p.write_text("{not valid json")
    assert leaderboard._load_local() == []


def test_save_silently_swallows_errors(tmp_scores, monkeypatch):
    """Even if writing fails, no exception bubbles up."""
    monkeypatch.setattr(leaderboard, "SCORES_FILE", "/nonexistent/dir/file.json")
    # Should not raise
    leaderboard._save_local([{"name": "X", "score": 1}])


def test_submit_returns_true(tmp_scores):
    assert leaderboard._native_submit("Z", 9) is True
