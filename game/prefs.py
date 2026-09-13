"""Device-local settings (mute, …).

Kept deliberately SEPARATE from the achievements save blob's cloud-merge path:
these are per-device preferences — a mute set on one device must not sync to
another — so they never touch ``profile_push``/``profile_pull``.

* Native: nested under the ``"settings"`` key of ``skybit_save.json`` (a sibling
  of ``"achievements"``), read-modify-written so the other keys survive.
* Browser: ``localStorage["skybit_settings"]`` via the ``window.__sk`` dispatcher
  (``settings_load`` / ``settings_save`` actions defined in ``inject_theme.py``).

Every read/write is wrapped so a corrupt/missing store degrades to defaults
rather than crashing.
"""
import sys
import json

from game.config import SAVE_FILE

_IS_BROWSER = sys.platform == "emscripten"
_KEY = "settings"          # native skybit_save.json sub-key

_DEFAULTS = {"muted": False}

_cache: "dict | None" = None


def _blank() -> dict:
    return dict(_DEFAULTS)


def _coerce(d) -> dict:
    """Normalise a loaded blob to the known schema (additive-safe)."""
    out = dict(_DEFAULTS)
    if isinstance(d, dict):
        out["muted"] = bool(d.get("muted", False))
    return out


# ── Native local-JSON (mirrors achievements._load_native / _save_native) ──────

def _load_native() -> dict:
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            doc = json.load(f)
        return _coerce(doc.get(_KEY))
    except Exception:
        return _blank()


def _save_native(store: dict) -> None:
    try:
        doc = {}
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                doc = json.load(f) or {}
        except Exception:
            doc = {}
        if not isinstance(doc, dict):
            doc = {}
        doc[_KEY] = store
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(doc, f)
    except Exception:
        pass


# ── Browser localStorage via window.__sk (probed like achievements) ──────────

def _dispatcher():
    try:
        import platform as _p  # pygbag platform module  # type: ignore
        win = getattr(_p, "window", None)
        return getattr(win, "__sk", None) if win is not None else None
    except Exception:
        return None


def _load_web() -> dict:
    try:
        sk = _dispatcher()
        if sk is None:
            return _blank()
        raw = sk("settings_load", "")
        if not raw:
            return _blank()
        return _coerce(json.loads(str(raw)))
    except Exception:
        return _blank()


def _save_web(store: dict) -> None:
    try:
        sk = _dispatcher()
        if sk is None:
            return
        sk("settings_save", json.dumps(store, separators=(",", ":")))
    except Exception:
        pass


# ── Public API ────────────────────────────────────────────────────────────────

def load() -> dict:
    """Return the (cached) settings blob, loading once from disk/localStorage."""
    global _cache
    if _cache is None:
        _cache = _load_web() if _IS_BROWSER else _load_native()
    return _cache


def save() -> None:
    if _cache is None:
        return
    if _IS_BROWSER:
        _save_web(_cache)
    else:
        _save_native(_cache)


def get_muted() -> bool:
    return bool(load().get("muted", False))


def set_muted(m: bool) -> None:
    store = load()
    store["muted"] = bool(m)
    save()


def reset_cache() -> None:
    """Drop the in-memory copy (tests / forced reload)."""
    global _cache
    _cache = None
