"""
Global leaderboard bridge.

Native play:  reads/writes a local JSON file (SCORES_FILE from config).
              Tamper-protected with an HMAC envelope (game.security.integrity).

Browser (emscripten): delegates to window.lbSubmitSignedStart / window.lbFetchStart
              fire-and-poll JS functions injected by inject_theme.py which
              talk to Supabase via the validated submit_score RPC.
"""
import json
import sys

from game.config import SCORES_FILE
from game.security import (
    sanitize_name,
    can_submit_score,
    record_submission,
    can_refresh_leaderboard,
)
from game.security import events as _sec_events
from game.security.integrity import (
    sign_local_scores,
    load_local_scores_verified,
)

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


# ── Native local-JSON helpers (HMAC-protected) ───────────────────────────────

def _load_local() -> list:
    """Read local scores file; return list of {name, score}, sorted desc.
    On tamper or read failure returns []."""
    raw = load_local_scores_verified(SCORES_FILE)
    return sorted(
        [{"name": str(e["name"]), "score": int(e["score"])} for e in raw],
        key=lambda e: e["score"], reverse=True,
    )


def _save_local(scores: list) -> None:
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(sign_local_scores(scores), f)
    except Exception:
        pass


def _native_submit(name: str, score: int) -> bool:
    safe = sanitize_name(name)
    if safe is None:
        _sec_events.emit("name_rejected", reason="sanitize_native")
        return False
    scores = _load_local()
    scores.append({"name": safe, "score": int(score)})
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
        if v in ("__skip__", "null", "None", "undefined"):
            return None
        # Defense in depth: sanitize even though the JS overlay also clamps.
        return sanitize_name(v)
    except Exception:
        return None


async def submit(name: str, score: int, world=None) -> bool:
    """Save score. Browser: signed-RPC submit via JS bridge. Native: local JSON.

    `world` (optional) supplies the SignedRun envelope so the server can run
    its anti-cheat checks. If omitted (legacy path), only basic plausibility
    is enforced server-side.
    """
    safe = sanitize_name(name)
    if safe is None:
        _sec_events.emit("name_rejected", reason="sanitize_pre_submit")
        return False
    if not can_submit_score():
        _sec_events.emit("ratelimit_hit", scope="submit_score")
        return False
    record_submission()

    if _IS_BROWSER:
        _resolve()
        if _lbSubmit is None:
            return False
        try:
            import asyncio
            import platform as _p  # type: ignore
            envelope = _build_envelope(safe, int(score), world)
            _p.window.lbSubmitSignedStart(envelope)
            while True:
                v = _p.window._lbSubmitDone
                if v is not None:
                    if not bool(v):
                        _sec_events.emit("submit_failed")
                    return bool(v)
                await asyncio.sleep(0.05)
        except Exception:
            return False
    else:
        return _native_submit(safe, int(score))


def _build_envelope(name: str, score: int, world) -> str:
    """Build the JSON envelope passed to window.lbSubmitSignedStart."""
    sr = getattr(world, "signed_run", None) if world is not None else None
    payload: dict = {
        "name": name,
        "score": score,
        "duration": int(getattr(world, "time_alive", 0)) if world is not None else 0,
        "pillars": int(getattr(world, "pillars_passed", 0)) if world is not None else 0,
    }
    if sr is not None:
        payload.update({
            "run_sig":        sr.run_sig,
            "chain_last":     sr.chain_last,
            "chain_count":    sr.chain_count,
            "y_stddev_centi": sr.y_stddev_centi,
            "y_range_centi":  sr.y_range_centi,
        })
    else:
        payload.update({
            "run_sig":        "",
            "chain_last":     "",
            "chain_count":    0,
            "y_stddev_centi": 0,
            "y_range_centi":  0,
        })
    return json.dumps(payload, separators=(",", ":"))


async def fetch_top10() -> list:
    """GET top-10 scores. Browser: Supabase via JS bridge. Native: local JSON."""
    if not can_refresh_leaderboard():
        # Soft cooldown — return whatever's cached (None == skip refresh).
        # The HUD reuses its previous list rather than blanking out.
        return []
    if _IS_BROWSER:
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
                    out = []
                    for e in data:
                        safe = sanitize_name(str(e.get("name", "")))
                        out.append({"name": safe or "?", "score": int(e.get("score", 0))})
                    return out
                await asyncio.sleep(0.05)
        except Exception:
            return []
    else:
        return _native_fetch()
