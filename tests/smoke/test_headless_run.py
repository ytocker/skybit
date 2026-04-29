"""End-to-end headless smoke test: run a few simulated seconds of
gameplay without a display and verify nothing throws."""
import pytest


def test_world_runs_for_5_seconds_without_exception(world):
    """Tick the world at 60 fps for 5 simulated seconds. No flap input,
    so the bird falls and dies somewhere along the way — the run must
    finish without raising."""
    world.ready_t = 0.0
    elapsed = 0.0
    dt = 1 / 60
    n_ticks = 0
    while elapsed < 5.0:
        world.update(dt)
        elapsed += dt
        n_ticks += 1
    assert n_ticks > 0
    # By 5 s of free-fall the bird must have died. (Not guaranteed if the
    # ground is unreachable from start — but with default H/GROUND_Y it is.)
    assert world.game_over is True


def test_world_idle_tick(world):
    """``world_idle_tick`` is the menu-screen heartbeat. Must not raise."""
    for _ in range(60):
        world.world_idle_tick(1 / 60)


def test_world_runs_with_flaps(world):
    """Inject a flap every ~1 s so the bird stays alive longer. We don't
    require it to survive 10 s — just that flapping doesn't crash."""
    world.ready_t = 0.0
    dt = 1 / 60
    for tick in range(600):
        if tick % 60 == 0 and not world.game_over:
            world.flap()
        world.update(dt)


def test_full_app_one_frame(mute_audio, monkeypatch):
    """``App.async_run`` is async; just exercise ``_update`` + ``_render``
    for one frame to confirm the full pipeline survives a tick."""
    from game import play_log
    async def _noop(*a, **k): return False
    monkeypatch.setattr(play_log, "log_run", _noop)

    from game.scenes import App, STATE_PLAY
    app = App()
    app.state = STATE_PLAY
    app._cooldown_t = 0.0
    app._update(1 / 60)
    app._render()
    # Drawing went to the dummy display — no exception is the assertion.


def test_score_after_long_run(world):
    """Run idle ticks for a while; score may stay 0 (no flaps) but must
    never go negative."""
    world.ready_t = 0.0
    for _ in range(300):
        world.update(1 / 60)
        assert world.score >= 0
        assert world.coin_count >= 0
        assert world.pillars_passed >= 0
        if world.game_over:
            break
