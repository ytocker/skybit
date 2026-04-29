"""Integrity / anti-cheat / local-scores-tamper tests."""
import json
import math
import os
import tempfile

import pytest

from game.security.integrity import (
    RunRecorder,
    sign_local_scores,
    load_local_scores_verified,
)


class FakeWorld:
    def __init__(self, score=0, time_alive=0.0, pillars_passed=0):
        self.score = score
        self.time_alive = time_alive
        self.pillars_passed = pillars_passed


def _drive_realistic_run(rec: RunRecorder, *, duration=10.0, pillars=6, fps=60):
    """Simulate a flapping bird: y oscillates between ~150 and ~450."""
    t = 0.0
    dt = 1.0 / fps
    pillar_interval = duration / max(pillars, 1)
    next_pillar = pillar_interval
    p_idx = 0
    while t < duration:
        # 1 Hz sine, amplitude 150 → ~106 px std-dev across the run.
        y = 300.0 + math.sin(t * 2 * math.pi) * 150.0
        rec.sample_bird_y(t, y)
        if t >= next_pillar and p_idx < pillars:
            rec.record_pillar(t, x=300, gap_y=300)
            next_pillar += pillar_interval
            p_idx += 1
        t += dt
    return p_idx


def test_seal_of_realistic_run_passes_thresholds():
    rec = RunRecorder()
    pillars = _drive_realistic_run(rec, duration=10.0, pillars=6)
    world = FakeWorld(score=pillars, time_alive=10.0, pillars_passed=pillars)
    sr = rec.seal(world)
    assert sr.chain_last == "death"
    assert sr.chain_count >= pillars + 1  # pillars + death (+ y-samples)
    assert sr.duration_s == 10
    # Realistic flapping: std-dev should easily clear the 8-pixel
    # (centi: 800) anti-straight-run threshold.
    assert sr.y_stddev_centi > 800
    assert sr.y_range_centi > 4000


def test_seal_of_straight_run_fails_thresholds():
    """The classic 'fly straight, max score' attack: no y variance at all."""
    rec = RunRecorder()
    t = 0.0
    while t < 10.0:
        rec.sample_bird_y(t, 300.0)  # constant y
        t += 1.0 / 60.0
    rec.record_pillar(1.0, 300, 300)
    rec.record_pillar(3.0, 300, 300)
    world = FakeWorld(score=10000, time_alive=10.0, pillars_passed=2)
    sr = rec.seal(world)
    # Straight run → near-zero std-dev — server must reject.
    assert sr.y_stddev_centi < 800
    assert sr.y_range_centi < 4000


def test_run_must_terminate_via_death():
    """Without seal()/death event, chain_last is not 'death'."""
    rec = RunRecorder()
    rec.record_pillar(1.0, 300, 300)
    # Don't call seal — RunRecorder still has _last_kind == 'pillar'.
    assert rec._last_kind == "pillar"


def test_local_scores_tamper_wipe():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "scores.json")
        data = [{"name": "alice", "score": 50}, {"name": "bob", "score": 30}]
        signed = sign_local_scores(data)
        with open(path, "w") as f:
            json.dump(signed, f)
        # Round-trip OK.
        loaded = load_local_scores_verified(path)
        assert {(e["name"], e["score"]) for e in loaded} == {("alice", 50), ("bob", 30)}

        # Tamper: bump alice's score.
        signed["scores"][0]["score"] = 99999
        with open(path, "w") as f:
            json.dump(signed, f)
        # Verification must fail → returns [], file is wiped.
        assert load_local_scores_verified(path) == []
        assert not os.path.exists(path)


def test_legacy_plain_list_accepted_once():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "scores.json")
        with open(path, "w") as f:
            json.dump([{"name": "old", "score": 7}], f)
        # Pre-security format: accepted as untrusted, but accepted.
        assert load_local_scores_verified(path) == [{"name": "old", "score": 7}]
