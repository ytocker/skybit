"""
Anonymous per-run telemetry bridge.

Native play:  silent no-op. We don't cache telemetry locally — desktop
              is dev-only and there's no value in writing rows we'd
              never ship anywhere.

Browser (emscripten): delegates to window.skyLogPlayStart fire-and-poll
              JS function injected by inject_theme.py, which adds the
              localStorage-persisted device UUID and POSTs to the
              public.plays Supabase table.

The hook is fire-and-forget: scenes._on_death wraps log_run() in
asyncio.create_task and never awaits it. Errors degrade silently into
the JS console — they MUST NOT throw into the game loop.
"""
import json
import sys

_IS_BROWSER = sys.platform == "emscripten"

_logPlay = None


def _resolve() -> None:
    global _logPlay
    if _logPlay is not None:
        return
    try:
        import platform as _pgb  # type: ignore
        if hasattr(_pgb, "window") and hasattr(_pgb.window, "skyLogPlayStart"):
            _logPlay = _pgb.window.skyLogPlayStart
            return
    except Exception:
        pass
    try:
        import js  # type: ignore
        if hasattr(js, "skyLogPlayStart"):
            _logPlay = js.skyLogPlayStart
    except Exception:
        pass


def _build_payload(world) -> str:
    """Pack the run summary the JS side will POST. Returns a JSON string
    so the Python→JS handoff doesn't depend on dict-to-object coercion."""
    payload = {
        "score":       int(world.score),
        "duration_s":  int(world.time_alive),
        "coins":       int(world.coin_count),
        "pillars":     int(world.pillars_passed),
        "near_misses": int(world.near_misses),
        "powerups":    {k: int(v) for k, v in world.powerups_picked.items()},
    }
    return json.dumps(payload, separators=(",", ":"))


async def log_run(world) -> bool:
    """Fire-and-forget: hand the run summary to JS, wait for the POST to
    complete, return True on 2xx. Native = silent no-op."""
    if not _IS_BROWSER:
        return False
    _resolve()
    if _logPlay is None:
        return False
    try:
        import asyncio
        import platform as _p  # type: ignore
        _p.window.skyLogPlayStart(_build_payload(world))
        while True:
            v = _p.window._skyLogPlayDone
            if v is not None:
                return bool(v)
            await asyncio.sleep(0.05)
    except Exception:
        return False
