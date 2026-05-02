"""
Global leaderboard bridge.

Native play:  reads/writes a local JSON file (SCORES_FILE from config).
              No network required — scores persist across sessions on-device.

Browser (emscripten): delegates to the closure-private ``window.__sk``
              dispatcher injected by inject_theme.py. The submit path
              ships a tamper-evident proof bundle (events + chain hash
              + run UUID) and runs a deterministic plausibility check
              before the network call.
"""
import os
import sys
import json

from game.config import SCORES_FILE
from game import _plausibility

_IS_BROWSER = sys.platform == "emscripten"

# ── Browser-side bridge ──────────────────────────────────────────────────────
#
# We resolve a single handle: ``js.window.openNameEntry`` (kept on window
# because the name-entry overlay is not security-sensitive). Once we see
# it, we know the JS bridge has booted and ``window.__sk`` is wired up.

_dispatcherReady = False
_openNameEntry = None

# Set by fetch_top10() after each browser-side fetch. Empty string means
# the fetch was successful (whether or not it returned rows). Non-empty
# means a specific failure mode the leaderboard scene can render to the
# canvas so the user sees something other than a silent empty list. See
# inject_theme.py's doFetch() for the values produced ("config missing",
# "http NNN", "rls or empty", "network").
_last_fetch_error: str = ""


def last_fetch_error() -> str:
    """Read-only accessor for the last browser fetch's error code."""
    return _last_fetch_error


def _resolve() -> None:
    global _dispatcherReady, _openNameEntry
    if _dispatcherReady:
        return
    try:
        import js  # type: ignore
        if hasattr(js, "openNameEntry"):
            _openNameEntry = js.openNameEntry
            _dispatcherReady = True
            return
    except Exception:
        pass
    try:
        import platform as _pgb  # type: ignore
        if hasattr(_pgb, "window") and hasattr(_pgb.window, "openNameEntry"):
            _openNameEntry = _pgb.window.openNameEntry
            _dispatcherReady = True
    except Exception:
        pass


def _to_json(payload: dict) -> str:
    """Pre-serialise to a JSON string. Matches the proven handoff
    pattern in the legacy bridge — Pyodide-to-JS dict conversion
    behaves differently across pygbag versions, but a string is just
    a string."""
    out = dict(payload)
    if "events" in out:
        out["events"] = [list(e) for e in out["events"]]
    return json.dumps(out, separators=(",", ":"))


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


def _build_submit_payload(name: str, world) -> "dict | None":
    """Assemble the submission bundle from the world's ProofState. Returns
    ``None`` if the local plausibility check rejects the run — the bridge
    is never called in that case, so the network sees no submission for
    a tampered score."""
    proof = getattr(world, "_proof", None)
    if proof is None:
        return None
    score = proof.score()
    events = proof.events_tuple()
    try:
        _plausibility.check(
            score=int(score),
            pillars_passed=int(world.pillars_passed),
            coin_count=int(world.coin_count),
            time_alive=float(world.time_alive),
            events=events,
            chain_hex=proof.chain_hex(),
        )
    except _plausibility.PlausibilityError:
        return None
    return {
        "name": str(name)[:10],
        "score": int(score),
        "run_id": proof.run_id(),
        "chain_hex": proof.chain_hex(),
        "events": list(events),
    }


async def submit(name: str, world) -> bool:
    """Save score for the run captured in ``world``. Browser: assembles a
    proof bundle, runs the plausibility check, ships through ``__sk``.
    Native: writes the visible ``world.score`` to the local JSON.

    Note: signature changed from ``submit(name, score)`` — the proof
    state lives on ``world``, so passing the int alone would lose it."""
    if _IS_BROWSER:
        _resolve()
        if not _dispatcherReady:
            return False
        payload = _build_submit_payload(name, world)
        if payload is None:
            return False
        try:
            import asyncio
            import platform as _p  # type: ignore
            _p.window.__sk("submit", _to_json(payload))
            while True:
                v = _p.window.__sk("submit_done")
                if v is not None:
                    return bool(v)
                await asyncio.sleep(0.05)
        except Exception:
            return False
    else:
        # Native: dev-only path, unsigned. The on-disk JSON is a debug
        # convenience, not a competitive surface.
        return _native_submit(name, int(getattr(world, "score", 0)))


async def fetch_top10() -> list:
    """GET top-10 scores. Browser: ``__sk('fetch')`` → Supabase fetch +
    client-side plausibility filter. Native: local JSON.

    On the browser path, also captures any fetch error code into the
    module-level ``_last_fetch_error`` so the leaderboard scene can
    render a "Top-10 unavailable" line instead of a silent empty list
    when the network/auth/RLS path fails."""
    global _last_fetch_error
    _last_fetch_error = ""
    if _IS_BROWSER:
        _resolve()
        if not _dispatcherReady:
            _last_fetch_error = "bridge"
            return []
        try:
            import asyncio, json as _json
            import js as _js  # type: ignore
            import platform as _p  # type: ignore
            _p.window.__sk("fetch")
            while True:
                v = _p.window.__sk("fetch_done")
                if v is not None:
                    data = _json.loads(_js.JSON.stringify(v))
                    try:
                        err = _p.window.__sk("fetch_error")
                        _last_fetch_error = str(err) if err else ""
                    except Exception:
                        _last_fetch_error = ""
                    return [{"name": str(e["name"]), "score": int(e["score"])} for e in data]
                await asyncio.sleep(0.05)
        except Exception:
            _last_fetch_error = "exception"
            return []
    else:
        return _native_fetch()
