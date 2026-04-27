"""
Global leaderboard bridge — Supabase REST API via the JS layer.

In-browser (emscripten): delegates to window.lbSubmit / window.lbFetch /
window.openNameEntry injected by inject_theme.py.
Native / headless: all calls are silent no-ops that return immediately.
"""
import sys

_IS_BROWSER = sys.platform == "emscripten"

_lbSubmit = None
_lbFetch = None
_openNameEntry = None


def _resolve() -> None:
    global _lbSubmit, _lbFetch, _openNameEntry
    if _lbSubmit is not None:
        return
    # Only openNameEntry needs a cached reference; submit/fetch use polling globals directly.
    try:
        import js  # type: ignore
        if hasattr(js, "openNameEntry"):
            _openNameEntry = js.openNameEntry
            _lbSubmit = True   # sentinel: resolved
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
        # Poll until JS sets _pendingName to something other than the sentinel
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
    """POST score to Supabase. Returns True on success.

    Uses fire-and-poll: calls window.lbSubmitStart() synchronously (it kicks
    off a JS async IIFE internally), then polls window._lbSubmitDone each tick.
    This avoids awaiting a JS Promise directly, which freezes Python's asyncio.
    """
    if not _IS_BROWSER:
        return False
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


async def fetch_top10() -> list:
    """GET top-10 scores. Returns list of {'name': str, 'score': int}.

    Same fire-and-poll pattern: calls window.lbFetchStart() synchronously
    then polls window._lbFetchResult.
    """
    if not _IS_BROWSER:
        return []
    _resolve()
    if _lbFetch is None:
        return []
    try:
        import asyncio
        import json as _json
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
