"""Per-device client-side rate limiting + telemetry dedup.

This is the client mirror of the Supabase RPC's 30-second cooldown. The
goal is fast UX feedback ("you just submitted, wait a bit") and to avoid
spamming the server even when the user mashes the submit button. The
authoritative limit lives in supabase/schema.sql.

Native: persists the last-submit timestamp under SCORES_FILE's sibling
~/.skybit_rl.json. Browser: localStorage key `skybit_ratelimit`.
"""
from __future__ import annotations

import json
import os
import sys
import time

from game.config import SCORES_FILE

_IS_BROWSER = sys.platform == "emscripten"

_SUBMIT_COOLDOWN_S = 30.0
_LB_REFRESH_COOLDOWN_S = 5.0

_RL_FILE = os.path.join(os.path.dirname(os.path.abspath(SCORES_FILE)),
                        "skybit_ratelimit.json")
_LS_KEY = "skybit_ratelimit"


def _load_state() -> dict:
    if _IS_BROWSER:
        try:
            import platform as _p  # type: ignore
            raw = _p.window.localStorage.getItem(_LS_KEY)
            if raw:
                return json.loads(str(raw))
        except Exception:
            return {}
        return {}
    try:
        with open(_RL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(state: dict) -> None:
    blob = json.dumps(state, separators=(",", ":"))
    if _IS_BROWSER:
        try:
            import platform as _p  # type: ignore
            _p.window.localStorage.setItem(_LS_KEY, blob)
        except Exception:
            pass
        return
    try:
        with open(_RL_FILE, "w", encoding="utf-8") as f:
            f.write(blob)
    except Exception:
        pass


def can_submit_score(now: float | None = None) -> bool:
    now = time.time() if now is None else now
    last = float(_load_state().get("last_submit_ts", 0.0))
    return now - last >= _SUBMIT_COOLDOWN_S


def record_submission(now: float | None = None) -> None:
    now = time.time() if now is None else now
    state = _load_state()
    state["last_submit_ts"] = now
    _save_state(state)


def can_refresh_leaderboard(now: float | None = None) -> bool:
    now = time.time() if now is None else now
    last = float(_load_state().get("last_lb_refresh_ts", 0.0))
    if now - last < _LB_REFRESH_COOLDOWN_S:
        return False
    state = _load_state()
    state["last_lb_refresh_ts"] = now
    _save_state(state)
    return True


def telemetry_dedup_key(world) -> str:
    """Stable, run-identifying key. We dedup against the previous one to
    suppress double-fires (e.g., scenes._on_death racing with retry button).
    """
    return f"{int(getattr(world, 'time_alive', 0) * 1000)}:{getattr(world, 'score', 0)}:{getattr(world, 'pillars_passed', 0)}"


def remember_telemetry_key(key: str) -> bool:
    """Record `key` and return True if it differs from the last one
    (i.e., this telemetry hasn't been sent yet)."""
    state = _load_state()
    if state.get("last_telemetry_key") == key:
        return False
    state["last_telemetry_key"] = key
    _save_state(state)
    return True
