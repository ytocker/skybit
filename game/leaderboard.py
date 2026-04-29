"""
Global leaderboard bridge.

Native play:  reads/writes a local JSON file (SCORES_FILE from config).
              No network required — scores persist across sessions on-device.

Browser (emscripten): delegates to window.lbSubmitStart / window.lbFetchStart
              fire-and-poll JS functions injected by inject_theme.py which
              talk to Supabase.
"""
import os
import sys
import json

from game.config import SCORES_FILE

_IS_BROWSER = sys.platform == "emscripten"

# ── Browser-side JS handle (resolved lazily) ─────────────────────────────────

_lbSubmit = None
_lbFetch = None
_openNameEntry = None


def _resolve() -> None:
    global _lbSubmit, _lbFetch, _openNameEntry
    if _lbSubmit is not None:
        return
    try:
        import js  # type: ignore
        if hasattr(js, "openNameEntry"):
            _openNameEntry = js.openNameEntry
            _lbSubmit = True
            _lbFetch = True
            return
    except Exception:
        pass
    try:
        import platform as _pgb  # type: ignore
        if hasattr(_pgb, "window") and hasattr(_pgb.window, "openNameEntry"):
            _openNameEntry = _pgb.window.openNameEntry
            _lbSubmit = True
            _lbFetch = True
    except Exception:
        pass


# ── Native local-JSON helpers ─────────────────────────────────────────────────

def _load_local() -> list:
    """Read local scores file; return list of {name, score}, sorted desc."""
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return sorted(
            [{"name": str(e["name"]), "score": int(e["score"])} for e in data],
            key=lambda e: e["score"], reverse=True
        )
    except Exception:
        return []


def _save_local(scores: list) -> None:
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f)
    except Exception:
        pass


def _native_submit(name: str, score: int) -> bool:
    scores = _load_local()
    scores.append({"name": name, "score": score})
    scores.sort(key=lambda e: e["score"], reverse=True)
    scores = scores[:10]
    _save_local(scores)
    return True


def _native_fetch() -> list:
    return _load_local()[:10]


# ── Public API ────────────────────────────────────────────────────────────────

async def open_name_entry() -> "str | None":
    """Show browser name-entry overlay; returns submitted name or None if skipped."""
    if not _IS_BROWSER:
        return None
    _resolve()
    if _openNameEntry is None:
        return None
    try:
        import asyncio
        import platform as _p  # type: ignore
        _openNameEntry()
        while True:
            try:
                v = str(_p.window._pendingName)
            except Exception:
                v = "__pending__"
            if v != "__pending__":
                break
            await asyncio.sleep(0.05)
        v = str(_p.window._pendingName)
        return None if v in ("__skip__", "null", "None", "undefined") else v
    except Exception:
        return None


async def submit(name: str, score: int) -> bool:
    """Save score. Browser: POST to Supabase via JS bridge. Native: local JSON."""
    if _IS_BROWSER:
        _resolve()
        if _lbSubmit is None:
            return False
        try:
            import asyncio
            import platform as _p  # type: ignore
            _p.window.lbSubmitStart(name, score)
            while True:
                v = _p.window._lbSubmitDone
                if v is not None:
                    return bool(v)
                await asyncio.sleep(0.05)
        except Exception:
            return False
    else:
        return _native_submit(name, score)


async def fetch_top10() -> list:
    """GET top-10 scores. Browser: Supabase via JS bridge. Native: local JSON."""
    if _IS_BROWSER:
        _resolve()
        if _lbFetch is None:
            return []
        try:
            import asyncio, json as _json
            import js as _js  # type: ignore
            import platform as _p  # type: ignore
            _p.window.lbFetchStart()
            while True:
                v = _p.window._lbFetchResult
                if v is not None:
                    data = _json.loads(_js.JSON.stringify(v))
                    return [{"name": str(e["name"]), "score": int(e["score"])} for e in data]
                await asyncio.sleep(0.05)
        except Exception:
            return []
    else:
        return _native_fetch()
