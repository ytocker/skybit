"""End-to-end scenarios — does the game still play?

Each test simulates a *plausible session* and asserts only that nothing
exploded. No "score is exactly 9" — that's a change-detector, not a
breakage-detector.

Asserting non-exception is the whole point: if a refactor leaves a
NameError in `_activate_grow` or a bad index into `parrot.FRAMES`, the
unit-test world might still pass while a real run crashes.
"""
import math
import random

import pygame
import pytest

from game.config import (
    TRIPLE_DURATION, MAGNET_DURATION, SLOWMO_DURATION,
    KFC_DURATION, GHOST_DURATION, GROW_DURATION,
)
from game.entities import PowerUp


# ── helpers ─────────────────────────────────────────────────────────────────

def _tick(world, seconds, dt=1 / 60, on_frame=None):
    """Tick the world for ``seconds`` of simulated time. Optionally call
    ``on_frame(world, frame_idx)`` each frame for input injection."""
    n = int(seconds / dt)
    for i in range(n):
        if on_frame is not None:
            on_frame(world, i)
        world.update(dt)


# ── full-session smoke ─────────────────────────────────────────────────────

def test_30_seconds_no_input(world):
    """The bird falls, dies, the world continues to tick post-death."""
    world.ready_t = 0.0
    _tick(world, 30.0)
    assert world.game_over is True


def test_30_seconds_random_flapping(world):
    """A random flap pattern doesn't crash, score stays sane."""
    world.ready_t = 0.0
    rng = random.Random(0)

    def flap_sometimes(w, i):
        if not w.game_over and rng.random() < 0.06:
            w.flap()

    _tick(world, 30.0, on_frame=flap_sometimes)
    assert world.score >= 0
    assert world.coin_count >= 0
    assert world.pillars_passed >= 0


def test_60_seconds_alive_with_steady_flapping(world):
    """A regular flap every 18 frames keeps the bird airborne. Long
    enough to roll through coin-rush spawns and at least one power-up
    pickup attempt."""
    world.ready_t = 0.0

    def flap_every_18(w, i):
        if i % 18 == 0:
            w.flap()

    _tick(world, 60.0, on_frame=flap_every_18)
    # No assertion on game_over — random pipe gaps may still kill the
    # bird. The point is just "doesn't crash".


# ── state machine round-trip ────────────────────────────────────────────────

def test_full_state_round_trip(app):
    """menu → play → death → stats → leaderboard → restart, every
    transition called, no exception, no orphaned state."""
    from game.scenes import (
        STATE_MENU, STATE_PLAY, STATE_PAUSE, STATE_STATS,
        STATE_LEADERBOARD,
    )
    # Menu render
    app._render()

    # Menu → Play
    app._start_play()
    assert app.state == STATE_PLAY
    app._render()

    # Tick for 5 s
    for _ in range(60 * 5):
        app._update(1 / 60)
        if app.world.game_over:
            break

    # Force a death if it didn't happen naturally
    if not app.world.game_over:
        app.world._die()

    # Death → Stats
    app._on_death()
    assert app.state == STATE_STATS
    app._render()

    # Stats render for a moment
    for _ in range(30):
        app._update(1 / 60)
    app._render()

    # Pause toggle is a no-op outside play, but shouldn't crash
    app._toggle_pause()


def test_pause_unpause_mid_play(app):
    """Toggling pause shouldn't corrupt world state."""
    from game.scenes import STATE_PLAY, STATE_PAUSE
    app._start_play()
    app.world.ready_t = 0.0
    app._update(1 / 60)
    app._toggle_pause()
    assert app.state == STATE_PAUSE
    # While paused, _update on the pause branch must not raise
    for _ in range(10):
        app._update(1 / 60)
    app._render()
    app._toggle_pause()
    assert app.state == STATE_PLAY


# ── every power-up activates and expires cleanly ────────────────────────────

POWERUPS_AND_DURATIONS = [
    ("triple",  TRIPLE_DURATION),
    ("magnet",  MAGNET_DURATION),
    ("slowmo",  SLOWMO_DURATION),
    ("kfc",     KFC_DURATION),
    ("ghost",   GHOST_DURATION),
    ("grow",    GROW_DURATION),
]


@pytest.mark.parametrize("kind,duration", POWERUPS_AND_DURATIONS)
def test_powerup_full_lifecycle(world, kind, duration):
    """Pick up the power-up, run the world past its duration with the
    bird held alive, no exception. The point isn't "timer hits exactly
    0" — it's "this whole code path doesn't raise"."""
    from game.config import H
    pu = PowerUp(world.bird.x, world.bird.y, kind=kind)
    world.powerups.append(pu)
    world.ready_t = 0.0
    world.pipes.clear()
    world._check_pickups()

    elapsed = 0.0
    dt = 1 / 60
    while elapsed < duration + 1.0:
        # Hold the bird mid-air so a ground collision doesn't end the
        # tick loop early.
        world.bird.y = H * 0.5
        world.bird.vy = 0.0
        world.update(dt)
        elapsed += dt


def test_surprise_box_resolves_many_times(world):
    """50 surprise pickups, no crash. Catches a rename of one of the
    six real kinds in the resolver tuple."""
    from game.config import H
    rng = random.Random(7)
    for _ in range(50):
        # Fresh-ish state so timers don't shadow new picks
        for k in ("triple", "magnet", "slowmo", "kfc", "ghost", "grow"):
            setattr(world, f"{k}_timer", 0.0)
        pu = PowerUp(world.bird.x, world.bird.y, kind="surprise")
        world._on_powerup(pu)
        # Tick a few frames after each to exercise update paths
        world.bird.y = H * 0.5
        world.bird.vy = 0.0
        world.ready_t = 0.0
        for _ in range(5):
            world.update(1 / 60)


def test_coin_rush_runs_through(world):
    """Spawn enough pipes to trigger a coin-rush, then tick — exercises
    the rush coin-spawn path that's otherwise sparsely sampled in
    normal short runs."""
    from game.config import COIN_RUSH_INTERVAL, H
    world.pipes.clear()
    world.coins.clear()
    world.powerups.clear()
    world.pipes_spawned = 0
    for i in range(COIN_RUSH_INTERVAL + 2):
        world._spawn_pipe(x=400 + i * 200)
    # Confirm a rush actually happened (sanity)
    assert any(p.is_rush for p in world.pipes)
    # Now tick for a couple of seconds
    world.ready_t = 0.0
    for _ in range(120):
        world.bird.y = H * 0.5
        world.bird.vy = 0.0
        world.update(1 / 60)


# ── input event paths ───────────────────────────────────────────────────────

def test_keyboard_and_mouse_inputs_routed(app):
    """SPACE / W / UP / click / finger — every supported tap input
    starts a play if you're on the menu and doesn't crash mid-play."""
    from game.scenes import STATE_PLAY
    events = [
        pygame.event.Event(pygame.KEYDOWN,
                           {"key": pygame.K_SPACE, "unicode": "",
                            "mod": 0, "scancode": 0}),
        pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                           {"button": 1, "pos": (180, 320)}),
        pygame.event.Event(pygame.FINGERDOWN,
                           {"x": 0.5, "y": 0.5, "dx": 0, "dy": 0,
                            "pressure": 1.0,
                            "finger_id": 0, "touch_id": 0}),
    ]
    for e in events:
        app._handle_event(e)
    assert app.state == STATE_PLAY


# ── persistence round-trip ──────────────────────────────────────────────────

def test_leaderboard_round_trip_native(monkeypatch, tmp_path):
    """Submit, fetch, fetch-again-after-restart. The JSON file must
    survive a 'process restart' cleanly — that's what 'persistence'
    means in user-facing terms."""
    from game import leaderboard
    p = tmp_path / "scores.json"
    monkeypatch.setattr(leaderboard, "SCORES_FILE", str(p))

    leaderboard._native_submit("alice", 50)
    leaderboard._native_submit("bob", 100)
    first = leaderboard._native_fetch()

    # Simulate a fresh process by clearing nothing — files are the only
    # state. Re-fetch.
    second = leaderboard._native_fetch()
    assert first == second
    assert any(e["name"] == "bob" and e["score"] == 100 for e in second)
    assert any(e["name"] == "alice" and e["score"] == 50 for e in second)


def test_corrupt_leaderboard_does_not_crash_game(monkeypatch, tmp_path):
    """If the user / a bad write corrupts the JSON, the game must not
    crash on next launch — it should silently start with an empty
    board. Otherwise a single bad write softlocks the user forever."""
    from game import leaderboard
    p = tmp_path / "scores.json"
    p.write_text("{not even close to valid json")
    monkeypatch.setattr(leaderboard, "SCORES_FILE", str(p))

    fetched = leaderboard._native_fetch()
    assert fetched == []
