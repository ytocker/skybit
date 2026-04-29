"""Player-facing privacy controls: telemetry opt-out, device-ID rotation,
GDPR notice, "clear all local data".

Storage layout
--------------
Browser: localStorage.
  skybit_device_id        — anonymous run UUID
  skybit_telemetry        — "on"|"off" (default on)
  skybit_gdpr_seen        — "1" once notice acknowledged
  skybit_ratelimit        — last submission/refresh ts (ratelimit.py)

Native: ~/.skybit_privacy.json sidecar next to skybit_scores.json.
"""
from __future__ import annotations

import json
import os
import sys
import uuid

from game.config import SCORES_FILE

_IS_BROWSER = sys.platform == "emscripten"

_PRIV_FILE = os.path.join(os.path.dirname(os.path.abspath(SCORES_FILE)),
                          "skybit_privacy.json")


def _ls_get(key: str) -> str | None:
    try:
        import platform as _p  # type: ignore
        v = _p.window.localStorage.getItem(key)
        return None if v is None else str(v)
    except Exception:
        return None


def _ls_set(key: str, value: str) -> None:
    try:
        import platform as _p  # type: ignore
        _p.window.localStorage.setItem(key, value)
    except Exception:
        pass


def _ls_remove(key: str) -> None:
    try:
        import platform as _p  # type: ignore
        _p.window.localStorage.removeItem(key)
    except Exception:
        pass


def _native_load() -> dict:
    try:
        with open(_PRIV_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _native_save(state: dict) -> None:
    try:
        with open(_PRIV_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        pass


# ── Telemetry opt-out ────────────────────────────────────────────────────────


def telemetry_enabled() -> bool:
    if _IS_BROWSER:
        v = _ls_get("skybit_telemetry")
        return v != "off"
    return _native_load().get("telemetry", "on") != "off"


def set_telemetry(enabled: bool) -> None:
    val = "on" if enabled else "off"
    if _IS_BROWSER:
        _ls_set("skybit_telemetry", val)
    else:
        s = _native_load()
        s["telemetry"] = val
        _native_save(s)


# ── Device-ID rotation ───────────────────────────────────────────────────────


def rotate_device_id() -> str:
    """Generate a fresh anonymous device ID. Returns the new UUID."""
    new_id = str(uuid.uuid4())
    if _IS_BROWSER:
        _ls_set("skybit_device_id", new_id)
    else:
        s = _native_load()
        s["device_id"] = new_id
        _native_save(s)
    return new_id


# ── GDPR/privacy notice ──────────────────────────────────────────────────────


def gdpr_notice_shown() -> bool:
    if _IS_BROWSER:
        return _ls_get("skybit_gdpr_seen") == "1"
    return bool(_native_load().get("gdpr_seen"))


def mark_gdpr_notice_shown() -> None:
    if _IS_BROWSER:
        _ls_set("skybit_gdpr_seen", "1")
    else:
        s = _native_load()
        s["gdpr_seen"] = True
        _native_save(s)


# ── Clear-all-data (right to erasure) ────────────────────────────────────────


def clear_all_local_data() -> None:
    """Wipe every Skybit-owned client-side artefact."""
    if _IS_BROWSER:
        for k in ("skybit_device_id", "skybit_telemetry", "skybit_gdpr_seen",
                  "skybit_ratelimit", "skybit_security_events"):
            _ls_remove(k)
        return
    for path in (SCORES_FILE, _PRIV_FILE):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
    rl = os.path.join(os.path.dirname(os.path.abspath(SCORES_FILE)),
                      "skybit_ratelimit.json")
    try:
        if os.path.exists(rl):
            os.remove(rl)
    except Exception:
        pass
