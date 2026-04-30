"""Shared fixtures.

Minimal — the merge-safety suite mostly uses `pytest`'s built-in
`tmp_path`/`monkeypatch` plus a couple of helpers for headless game
construction.
"""
import os
import pathlib
import sys

# Force headless before any pygame import.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest


@pytest.fixture
def app(monkeypatch):
    """Return a fresh ``scenes.App`` with telemetry disabled.

    ``play_log.log_run`` is replaced with a no-op coroutine so
    ``_on_death`` doesn't raise ``RuntimeError`` when there's no
    asyncio loop running.
    """
    from game import play_log

    async def _noop_log(*a, **k):
        return False

    monkeypatch.setattr(play_log, "log_run", _noop_log)

    from game.scenes import App
    return App()


@pytest.fixture
def world():
    """A fresh ``World`` instance. Audio gracefully no-ops under
    SDL_AUDIODRIVER=dummy, so no extra mocking is needed."""
    from game.world import World
    return World()
