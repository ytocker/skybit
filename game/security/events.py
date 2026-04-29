"""In-memory security-event ring buffer + optional remote flush.

Anything suspicious — HMAC mismatch, ratelimit hit, local-scores tamper,
sanitize rejection, plausibility-fail from server — gets emitted here.
The ring is bounded so a noisy attacker can't OOM us, and a debug-menu
hook (scenes.py) can render the most recent entries.

Optional remote flush POSTs to public.security_events via the JS bridge
so the Supabase dashboard surfaces real-world abuse patterns.
"""
from __future__ import annotations

import time
from collections import deque
from typing import NamedTuple

_RING_CAP = 64


class SecurityEvent(NamedTuple):
    name: str
    detail: dict
    ts: float


_ring: "deque[SecurityEvent]" = deque(maxlen=_RING_CAP)


def emit(name: str, **detail) -> None:
    """Record a security event. Never raises."""
    try:
        _ring.append(SecurityEvent(name=str(name), detail=dict(detail), ts=time.time()))
    except Exception:
        pass


def recent(n: int = 20) -> list[SecurityEvent]:
    return list(_ring)[-max(0, int(n)):]


def clear() -> None:
    _ring.clear()


async def flush_remote() -> None:
    """Best-effort POST of the ring to public.security_events via JS bridge.

    Native: no-op (no network). Browser: delegates to window.skySecEventStart
    which inject_theme.py installs alongside the lb / play bridges.
    """
    try:
        import sys
        if sys.platform != "emscripten":
            return
        if not _ring:
            return
        import json as _json
        import platform as _p  # type: ignore
        if not hasattr(_p.window, "skySecEventStart"):
            return
        payload = _json.dumps(
            [{"name": e.name, "detail": e.detail, "ts": e.ts} for e in list(_ring)],
            separators=(",", ":"),
        )
        _p.window.skySecEventStart(payload)
    except Exception:
        pass
