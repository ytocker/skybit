"""Shared pytest fixtures.

Forces SDL into dummy-display / dummy-audio mode before any pygame import,
seeds the RNG to 42 for every test (autouse), and provides a fresh
``World`` with audio fully muted plus a ``tmp_scores`` fixture that
re-routes the leaderboard JSON to a tmpdir.
"""
import os
import pathlib
import random
import sys

# Force headless BEFORE pygame is imported anywhere downstream.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest


# ── deterministic randomness ────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _seed_rng():
    """Reset the RNG before every test so spawn order, coin patterns,
    and surprise-box rolls are reproducible."""
    random.seed(42)
    yield


# ── audio mute ─────────────────────────────────────────────────────────────

_AUDIO_PLAY_FNS = (
    "play_flap", "play_coin", "play_coin_triple", "play_triple_coin",
    "play_magnet", "play_slowmo", "play_thunder", "play_death",
    "play_gameover", "play_poof", "play_ghost", "play_grow",
)


@pytest.fixture
def mute_audio(monkeypatch):
    """Replace every ``audio.play_*`` with a no-op so tests don't depend
    on the mixer (already silent under SDL_AUDIODRIVER=dummy, but explicit
    is safer and lets tests count call invocations via mock objects)."""
    from game import audio
    for name in _AUDIO_PLAY_FNS:
        monkeypatch.setattr(audio, name, lambda *a, **k: None, raising=False)
    yield


# ── World factory ──────────────────────────────────────────────────────────

@pytest.fixture
def world(mute_audio):
    """A fresh, audio-muted World. The autouse RNG seed makes its initial
    pipe layout deterministic across tests."""
    from game.world import World
    return World()


# ── Persistence sandbox ────────────────────────────────────────────────────

@pytest.fixture
def tmp_scores(monkeypatch, tmp_path):
    """Re-route the leaderboard JSON to a tmpdir so tests don't pollute
    the repo. Both ``game.config`` and ``game.leaderboard`` cache the
    constant, so we patch both."""
    from game import config, leaderboard
    target = str(tmp_path / "scores.json")
    monkeypatch.setattr(config, "SCORES_FILE", target, raising=False)
    monkeypatch.setattr(leaderboard, "SCORES_FILE", target, raising=False)
    return tmp_path
