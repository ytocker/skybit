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


def _pylog(*args) -> None:
    """Log to the browser console from Python so the deployed-page
    diagnostic (and any user with DevTools open) can see what the
    leaderboard module is doing. Native runs silently no-op."""
    if not _IS_BROWSER:
        return
    try:
        import js as _js  # type: ignore
        _js.console.log("[skybit/py/lb]", *args)
    except Exception:
        pass


def _resolve() -> None:
    """Detect the JS bridge's readiness.

    Earlier versions used ``hasattr(js, "openNameEntry")`` which was
    unreliable in pygbag 0.9.x (CPython's `js` proxy doesn't always
    return False from hasattr the way Pyodide does). Browser-side
    diagnostic confirmed the bridge IS wired up but ``_dispatcherReady``
    stayed False, so ``fetch_top10`` returned ``[]`` without ever
    invoking ``__sk('fetch')``.

    New strategy: pull `platform.window.__sk` via ``getattr`` (no
    hasattr-style detection) and probe by calling it with an unknown
    action — the dispatcher returns ``null`` for any action it doesn't
    know, so a successful return proves the bridge is callable."""
    global _dispatcherReady, _openNameEntry
    if _dispatcherReady:
        return
    try:
        import platform as _pgb  # type: ignore
        win = getattr(_pgb, "window", None)
        if win is None:
            _pylog("_resolve: platform.window is None")
            return
        sk = getattr(win, "__sk", None)
        if sk is None:
            _pylog("_resolve: window.__sk not found")
            return
        # Probe: dispatch returns null for any unknown action. Reaching
        # the next line proves __sk is callable from Python.
        sk("__probe__")
        _openNameEntry = getattr(win, "openNameEntry", None)
        _dispatcherReady = True
        _pylog("_resolve: bridge ready (openNameEntry=" +
               ("yes" if _openNameEntry is not None else "no") + ")")
    except Exception as e:
        _pylog("_resolve: exception: " + type(e).__name__ + ": " + str(e)[:120])


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
            _pylog("fetch_top10: bridge not ready, returning []")
            return []
        try:
            import asyncio
            import platform as _p  # type: ignore
            _pylog("fetch_top10: calling __sk('fetch')")
            _p.window.__sk("fetch")
            tries = 0
            while tries < 200:  # 200 * 0.05s = 10s timeout
                v = _p.window.__sk("fetch_done")
                if v is not None:
                    # v is a JS array proxy. Earlier code went through
                    # `_js.JSON.stringify(v)` then json.loads, but
                    # pygbag's CPython 3.12 exposes `js` as a module
                    # named `__EMSCRIPTEN__` that lacks JSON. Iterate
                    # the proxy directly via its length property and
                    # bracket-index access (the same pattern used by
                    # the dispatcher itself).
                    rows: list = []
                    try:
                        length = int(getattr(v, "length", 0) or 0)
                    except Exception:
                        length = 0
                    for i in range(length):
                        try:
                            entry = v[i]
                            rows.append({
                                "name": str(entry["name"])[:10],
                                "score": int(entry["score"]),
                            })
                        except Exception as row_err:
                            _pylog("fetch_top10: row " + str(i) + " skipped: " +
                                   type(row_err).__name__)
                            continue
                    try:
                        err = _p.window.__sk("fetch_error")
                        _last_fetch_error = str(err) if err else ""
                    except Exception:
                        _last_fetch_error = ""
                    _pylog("fetch_top10: got " + str(len(rows)) + " rows from JS bridge")
                    return rows
                tries += 1
                await asyncio.sleep(0.05)
            _pylog("fetch_top10: timeout waiting for fetch_done after 10s")
            _last_fetch_error = "timeout"
            return []
        except Exception as e:
            _pylog("fetch_top10: exception: " + type(e).__name__ + ": " + str(e)[:120])
            _last_fetch_error = "exception:" + type(e).__name__
            return []
    else:
        return _native_fetch()
