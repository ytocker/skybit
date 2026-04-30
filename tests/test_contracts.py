"""Cross-module contracts.

These don't test gameplay — they test that one module hasn't silently
violated the interface another module depends on. A merge that renames
``World.score`` to ``World.points`` would pass every gameplay test
(scenes still tick, World still updates) yet crash on death because
``play_log._build_payload`` reads ``world.score``.

Contracts catch that class of bug.
"""
import inspect

import pytest


# ── World <-> play_log telemetry payload ───────────────────────────────────

def test_play_log_payload_attributes_exist_on_world(world):
    """``play_log._build_payload`` reads several attributes off the
    world. If any get renamed, every browser run silently drops
    telemetry. Fail fast at the contract level."""
    from game import play_log
    src = inspect.getsource(play_log._build_payload)
    # Pull every "world.<name>" reference out of the source.
    import re
    referenced = set(re.findall(r"world\.([a-zA-Z_]\w*)", src))
    missing = [name for name in referenced if not hasattr(world, name)]
    assert not missing, (
        "play_log reads attributes that World no longer exposes: "
        f"{missing}"
    )


# ── World <-> audio play_X interface ───────────────────────────────────────

def test_world_only_calls_audio_functions_that_exist():
    """Find every ``audio.play_X(...)`` in world.py and confirm each
    function still exists in game.audio. Catches a sound rename that
    leaves an orphan call site."""
    import re
    import pathlib
    from game import audio
    world_src = (pathlib.Path(__file__).resolve().parents[1]
                 / "game" / "world.py").read_text()
    called = set(re.findall(r"audio\.(play_\w+)\(", world_src))
    missing = [name for name in called if not hasattr(audio, name)]
    assert not missing, (
        "world.py calls audio functions that no longer exist: "
        f"{missing}"
    )


# ── PowerUp kinds known to World vs. POWERUP_WEIGHTS ───────────────────────

def test_powerup_weight_kinds_match_world_activations():
    """Every kind in POWERUP_WEIGHTS must either route to an _activate_X
    method or be the special 'surprise' wildcard."""
    import re
    import pathlib
    from game.config import POWERUP_WEIGHTS

    weight_kinds = {k for k, _ in POWERUP_WEIGHTS}
    world_src = (pathlib.Path(__file__).resolve().parents[1]
                 / "game" / "world.py").read_text()

    # The dispatcher block in _on_powerup looks like:
    #   if kind == "triple": self._activate_triple(...)
    handled_kinds = set(re.findall(r'kind == "(\w+)"', world_src))
    handled_kinds.add("surprise")     # surprise resolves *to* the others

    missing_handler = weight_kinds - handled_kinds
    orphan_handler = handled_kinds - weight_kinds - {"surprise"}

    assert not missing_handler, (
        f"POWERUP_WEIGHTS includes kinds with no activation handler: "
        f"{missing_handler}"
    )
    assert not orphan_handler, (
        f"world.py handles kinds that aren't in POWERUP_WEIGHTS: "
        f"{orphan_handler}"
    )


def test_each_real_kind_is_drawable():
    """Every kind in POWERUP_WEIGHTS can be constructed and drawn —
    catches a kind that's been added to the registry without a draw
    branch in PowerUp.draw."""
    import pygame
    pygame.display.init()
    pygame.font.init()
    from game.config import POWERUP_WEIGHTS
    from game.entities import PowerUp
    surf = pygame.Surface((360, 640), pygame.SRCALPHA)
    for kind, _ in POWERUP_WEIGHTS:
        p = PowerUp(180, 320, kind=kind)
        p.update(0.1)
        p.draw(surf)


# ── Scene state constants are stable ──────────────────────────────────────

def test_scene_state_constants_exist():
    """Other modules import these by name. If one is removed, every
    branch that compares ``app.state == STATE_X`` either errors or
    silently mismatches."""
    from game import scenes
    for name in ("STATE_MENU", "STATE_PLAY", "STATE_PAUSE",
                 "STATE_STATS", "STATE_NAMEENTRY",
                 "STATE_LEADERBOARD", "STATE_GAMEOVER"):
        assert hasattr(scenes, name), f"scenes.{name} is missing"


# ── Leaderboard JSON schema ───────────────────────────────────────────────

def test_leaderboard_persists_recognised_schema(monkeypatch, tmp_path):
    """A submission persists to disk in a shape the loader will
    re-accept. If we ever silently change the schema (e.g. drop
    'name'), every existing user's saved scores would be wiped on next
    launch. Lock the schema in."""
    import json
    from game import leaderboard
    p = tmp_path / "scores.json"
    monkeypatch.setattr(leaderboard, "SCORES_FILE", str(p))

    leaderboard._native_submit("hello", 7)
    raw = json.loads(p.read_text())
    assert isinstance(raw, list)
    assert len(raw) == 1
    entry = raw[0]
    assert set(entry.keys()) >= {"name", "score"}
    assert isinstance(entry["name"], str)
    assert isinstance(entry["score"], int)


# ── Config constants used cross-module ────────────────────────────────────

def test_config_has_every_constant_world_imports():
    """``world.py`` does a big multi-line ``from game.config import ...``.
    If any of those constants vanish, world.py won't even import, which
    test_boot covers — but having an explicit assertion here means a
    contributor sees "you removed PIPE_SPACING; world.py needs it"
    instead of a generic ImportError stack."""
    from game import config
    expected = [
        "W", "H", "GROUND_Y", "PIPE_W", "PIPE_SPACING",
        "GAP_START", "GAP_MIN", "SCROLL_BASE", "SCROLL_MAX",
        "BIRD_X", "BIRD_R", "COIN_R", "POWERUP_R",
        "POWERUP_CHANCE", "POWERUP_COOLDOWN",
        "TRIPLE_DURATION", "MAGNET_DURATION", "MAGNET_RADIUS",
        "SLOWMO_DURATION", "SLOWMO_SCALE",
        "KFC_DURATION", "GHOST_DURATION",
        "GROW_DURATION", "GROW_SCALE",
        "POWERUP_WEIGHTS",
        "COIN_RUSH_INTERVAL", "COIN_RUSH_GAP_BOOST", "COIN_RUSH_COINS",
        "SAVE_FILE", "SCORES_FILE",
    ]
    missing = [name for name in expected if not hasattr(config, name)]
    assert not missing, f"config.py missing constants: {missing}"
