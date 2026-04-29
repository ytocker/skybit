"""Scene-level fixtures: stub out ``play_log.log_run`` so tests don't try
to spin up an asyncio task in environments without a running loop."""
import pytest


@pytest.fixture
def app(mute_audio, monkeypatch):
    """A fresh ``scenes.App`` instance, headless-friendly."""
    from game import play_log
    # Make the telemetry helper a no-op coroutine
    async def _noop_log(*a, **k):
        return False
    monkeypatch.setattr(play_log, "log_run", _noop_log)

    from game.scenes import App
    return App()


@pytest.fixture
def qualifying_score():
    """Score that should always qualify for the top-10 (when populated)."""
    return 99999
