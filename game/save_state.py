"""Tiny key/value save used by the intro's first-launch flag.

A single JSON dict is read on App init and written when the intro is
marked seen. Schema is intentionally minimal — currently just
``intro_seen: bool`` — so this file stays additive and won't conflict with
the leaderboard's own local-scores JSON in `leaderboard.py`.
"""
import json
from game import config as _cfg


_SAVE_FILE = getattr(_cfg, "SAVE_FILE", "skybit_save.json")


def load_save() -> dict:
    try:
        with open(_SAVE_FILE, "r") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def save_save(d: dict) -> None:
    try:
        with open(_SAVE_FILE, "w") as f:
            json.dump(d, f)
    except Exception:
        pass
