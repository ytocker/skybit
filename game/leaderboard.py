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
    # Try standard Pyodide js module first, then pygbag's platform.window
    try:
        import js  # type: ignore
        if hasattr(js, "lbSubmit"):
            _lbSubmit = js.lbSubmit
            _lbFetch = js.lbFetch
            _openNameEntry = js.openNameEntry
            return
    except Exception:
        pass
    try:
        import platform as _pgb  # type: ignore
        if hasattr(_pgb, "window") and hasattr(_pgb.window, "lbSubmit"):
            _lbSubmit = _pgb.window.lbSubmit
            _lbFetch = _pgb.window.lbFetch
            _openNameEntry = _pgb.window.openNameEntry
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
    """POST score to Supabase. Returns True on success."""
    if not _IS_BROWSER:
        return False
    _resolve()
    if _lbSubmit is None:
        return False
    try:
        result = await _lbSubmit(name, score)
        return bool(result)
    except Exception:
        return False


async def fetch_top10() -> list:
    """GET top-10 scores. Returns list of {'name': str, 'score': int}."""
    if not _IS_BROWSER:
        return []
    _resolve()
    if _lbFetch is None:
        return []
    try:
        import js as _js  # type: ignore
        import json as _json
        raw = await _lbFetch()
        data = _json.loads(_js.JSON.stringify(raw))
        return [{"name": str(e["name"]), "score": int(e["score"])} for e in data]
    except Exception:
        return []
