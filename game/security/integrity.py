"""Run integrity: HMAC-chained event log + trajectory stats + signed envelope.

Anti-cheat goals
----------------
The user's #1 concern: a hacker who patches out collision and flies the
parrot in a straight line forever, racking up max score. This module
makes that flavour of attack visible:

* RunRecorder ingests every score-relevant event (pillar, coin, powerup)
  AND samples the bird's y-position several times per second. Each entry
  is HMAC'd with the previous link → tampering with any entry breaks
  every later signature.
* On `seal()` (called from World._die), we compute trajectory statistics
  — y-stddev, y-range, count — that distinguish real flapping (high
  variance) from straight-line cheats (~zero variance). The Supabase
  `submit_score` RPC rejects runs whose variance is implausibly low.
* The chain MUST end with a 'death' event sealed during _die(). A run
  that didn't terminate via the engine has no death link → server rejects.

This file also signs/verifies the local native scoreboard
(skybit_scores.json) so casual edits get wiped on next load.
"""
from __future__ import annotations

import json
import math
import os
import time
from typing import NamedTuple

from . import crypto

_CHAIN_LABEL = "run-chain-v1"
_LOCAL_SCORES_LABEL = "local-scores-v1"

# Sampling cadence for bird-y. World.update is called at FPS — we sample
# every ~6 frames (~10 Hz at 60 FPS) which is enough to compute std-dev
# and not so much that the chain blows up over a 30-min run.
_Y_SAMPLE_INTERVAL_S = 0.10


class SignedRun(NamedTuple):
    run_sig: str          # final HMAC link (envelope-level)
    chain_root: str       # first link, useful as a run identifier
    chain_last: str       # name of the last event ('death' on legit runs)
    chain_count: int
    y_stddev_centi: int   # std-dev of bird-y samples × 100
    y_range_centi: int    # (max y − min y) × 100
    pillars: int
    duration_s: int
    score: int


class RunRecorder:
    """Records score-relevant events + bird-y samples, HMAC-chained."""

    def __init__(self, seed: bytes | None = None):
        self._seed = seed if seed is not None else os.urandom(16)
        self._key = crypto.derive_key(self._seed, _CHAIN_LABEL)
        self._prev = crypto.sign(self._seed, self._key)
        self._root = self._prev
        self._count = 0
        self._last_kind = "init"
        self._sealed = False

        self._y_samples: list[float] = []
        self._last_y_sample_t = -1.0

    # ── chain helpers ───────────────────────────────────────────────────────

    def _append(self, kind: str, t: float, **detail) -> None:
        if self._sealed:
            return
        # Canonical encoding: previous-hash + kind + sorted detail JSON.
        body = json.dumps(
            {"k": kind, "t": round(float(t), 3), "d": detail, "p": self._prev},
            separators=(",", ":"), sort_keys=True,
        ).encode("utf-8")
        self._prev = crypto.sign(body, self._key)
        self._count += 1
        self._last_kind = kind

    # ── public event hooks (called from World) ──────────────────────────────

    def record_pillar(self, t: float, x: float, gap_y: float) -> None:
        self._append("pillar", t, x=round(float(x), 1), gy=round(float(gap_y), 1))

    def record_coin(self, t: float, x: float, y: float, value: int) -> None:
        self._append("coin", t, x=round(float(x), 1), y=round(float(y), 1), v=int(value))

    def record_powerup(self, t: float, kind: str) -> None:
        self._append("powerup", t, kind=str(kind))

    def sample_bird_y(self, t: float, y: float) -> None:
        """Throttled y-sample. Call every World.update(); we'll downsample."""
        if self._sealed:
            return
        if t - self._last_y_sample_t < _Y_SAMPLE_INTERVAL_S:
            return
        self._last_y_sample_t = float(t)
        yf = float(y)
        self._y_samples.append(yf)
        # Keep the chain coupled to the trajectory by mixing samples in too,
        # otherwise an attacker could omit them. Cheap; fires ~10 Hz.
        self._append("y", t, y=round(yf, 1))

    # ── seal ────────────────────────────────────────────────────────────────

    def _y_stats(self) -> tuple[int, int]:
        if not self._y_samples:
            return 0, 0
        n = len(self._y_samples)
        mean = sum(self._y_samples) / n
        var = sum((y - mean) ** 2 for y in self._y_samples) / n
        stddev = math.sqrt(var)
        return int(round(stddev * 100)), int(round((max(self._y_samples) - min(self._y_samples)) * 100))

    def seal(self, world) -> SignedRun:
        """Append a 'death' link and return the SignedRun envelope."""
        if self._sealed:
            return self._cached  # type: ignore[has-type]
        self._append(
            "death",
            float(getattr(world, "time_alive", 0.0)),
            score=int(getattr(world, "score", 0)),
            pillars=int(getattr(world, "pillars_passed", 0)),
        )
        self._sealed = True
        y_std, y_range = self._y_stats()
        envelope = {
            "v": 1,
            "score": int(getattr(world, "score", 0)),
            "pillars": int(getattr(world, "pillars_passed", 0)),
            "duration_s": int(getattr(world, "time_alive", 0.0)),
            "chain_root": self._root,
            "chain_last": self._last_kind,
            "chain_count": self._count,
            "y_stddev_centi": y_std,
            "y_range_centi": y_range,
            "ts": int(time.time()),
        }
        body = json.dumps(envelope, separators=(",", ":"), sort_keys=True).encode("utf-8")
        run_sig = crypto.sign(body)
        out = SignedRun(
            run_sig=run_sig,
            chain_root=self._root,
            chain_last=self._last_kind,
            chain_count=self._count,
            y_stddev_centi=y_std,
            y_range_centi=y_range,
            pillars=int(getattr(world, "pillars_passed", 0)),
            duration_s=int(getattr(world, "time_alive", 0.0)),
            score=int(getattr(world, "score", 0)),
        )
        self._cached = out
        return out


# ── Local-scores tamper protection (native only) ─────────────────────────────


def sign_local_scores(scores: list) -> dict:
    """Wrap a scores list in a tamper-evident envelope."""
    body = json.dumps(scores, separators=(",", ":"), sort_keys=True).encode("utf-8")
    key = crypto.derive_key(b"local-scores", _LOCAL_SCORES_LABEL)
    return {"v": 1, "scores": scores, "sig": crypto.sign(body, key)}


def load_local_scores_verified(path: str) -> list:
    """Load and verify; on tamper or read failure, return [] silently.

    Callers can react to a tamper by emitting a security event — see
    leaderboard.py.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except Exception:
        return []
    # Back-compat: legacy plain list (pre-security). Treat as untrusted but
    # accept once, then re-sign on next save.
    if isinstance(doc, list):
        return [{"name": str(e.get("name", "")), "score": int(e.get("score", 0))}
                for e in doc if isinstance(e, dict)]
    if not isinstance(doc, dict) or doc.get("v") != 1:
        return []
    scores = doc.get("scores")
    sig = doc.get("sig")
    if not isinstance(scores, list) or not isinstance(sig, str):
        return []
    body = json.dumps(scores, separators=(",", ":"), sort_keys=True).encode("utf-8")
    key = crypto.derive_key(b"local-scores", _LOCAL_SCORES_LABEL)
    if not crypto.verify(body, sig, key):
        # Tamper detected — wipe and start fresh.
        try:
            os.remove(path)
        except Exception:
            pass
        return []
    return [{"name": str(e.get("name", "")), "score": int(e.get("score", 0))}
            for e in scores if isinstance(e, dict)]
