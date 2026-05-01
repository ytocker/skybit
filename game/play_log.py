"""
Anonymous per-run telemetry bridge.

Native play:  silent no-op. We don't cache telemetry locally — desktop
              is dev-only and there's no value in writing rows we'd
              never ship anywhere.

Browser (emscripten): delegates to the closure-private ``window.__sk``
              dispatcher injected by inject_theme.py, which adds the
              localStorage-persisted device UUID and POSTs to the
              public.plays Supabase table.

The hook is fire-and-forget: scenes._on_death wraps log_run() in
asyncio.create_task and never awaits it. Errors degrade silently —
they MUST NOT throw into the game loop.
"""
import json
import sys

_IS_BROWSER = sys.platform == "emscripten"

_dispatcherReady = False


def _resolve() -> None:
    global _dispatcherReady
    if _dispatcherReady:
        return
    try:
        import platform as _pgb  # type: ignore
        if hasattr(_pgb, "window") and hasattr(_pgb.window, "openNameEntry"):
            _dispatcherReady = True
            return
    except Exception:
        pass
    try:
        import js  # type: ignore
        if hasattr(js, "openNameEntry"):
            _dispatcherReady = True
    except Exception:
        pass


def _build_payload(world) -> str:
    """Pack the run summary the JS side will POST as a JSON string. The
    dispatcher adds ``device_id`` itself so the value never round-trips
    through Python. JSON-string handoff (matching the legacy bridge)
    avoids Pyodide-version-specific dict→JS object conversion quirks."""
    return json.dumps({
        "score":       int(world.score),
        "duration_s":  int(world.time_alive),
        "coins":       int(world.coin_count),
        "pillars":     int(world.pillars_passed),
        "near_misses": int(world.near_misses),
        "powerups":    {k: int(v) for k, v in world.powerups_picked.items()},
    }, separators=(",", ":"))


async def log_run(world) -> bool:
    """Fire-and-forget: hand the run summary to JS, wait for the POST to
    complete, return True on 2xx. Native = silent no-op."""
    if not _IS_BROWSER:
        return False
    _resolve()
    if not _dispatcherReady:
        return False
    try:
        import asyncio
        import platform as _p  # type: ignore
        _p.window.__sk("log", _build_payload(world))
        while True:
            v = _p.window.__sk("log_done")
            if v is not None:
                return bool(v)
            await asyncio.sleep(0.05)
    except Exception:
        return False
