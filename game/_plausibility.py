"""
Deterministic plausibility check for a run-proof bundle.

Pure functions, no Pygame imports — runs in the browser, runs in tests,
runs in any future audit script. All thresholds derive from constants in
``game.config`` so the model never drifts from the gameplay rules.

A run that fails any rule below is rejected by ``leaderboard.submit``
before the network call. A run that passes is *not* guaranteed honest
— a self-consistent forgery (events that line up, chain hash that
matches, plausibility envelope respected) is indistinguishable from a
real run on the client. That gap can only close with server-side
validation, which is out of scope for this build.
"""
import hashlib
import struct

from game.config import (
    PIPE_SPACING, SCROLL_MAX, COIN_RUSH_INTERVAL, COIN_RUSH_COINS,
)


# Floor for the per-pipe travel time at top scroll speed. Used both as a
# minimum gap between consecutive pipe-pass events and as a lower bound
# on total run duration. The 0.05 s slack absorbs frame-time jitter.
_MIN_PIPE_INTERVAL_S = (PIPE_SPACING / SCROLL_MAX) - 0.05

# Hard score ceiling used by the leaderboard read filter. A real run at
# top scroll passes ~62 pipes/min and a coin rush adds ~14 coins every
# 15 pipes, so an hour of perfect play tops out near 4500. 10_000 leaves
# generous headroom while still rejecting a curl-injected 999_999.
MAX_PLAUSIBLE_SCORE = 10_000


class PlausibilityError(ValueError):
    """Raised when a proof bundle violates a rule. The message names the
    rule so a future audit log can group failures by cause."""


def _recompute_chain(events: tuple) -> bytes:
    """Mirror of ``ProofState`` chain computation — kept here as a pure
    function so the validator never imports the writer."""
    chain = b"\x00" * 32
    for (t_alive, dscore, kind) in events:
        t_ms = int(round(float(t_alive) * 1000))
        kind_b = kind.encode("ascii")[:8]
        kind_b = kind_b + b"\x00" * (8 - len(kind_b))
        packed = struct.pack(">qIB", t_ms, int(dscore), len(kind)) + kind_b
        chain = hashlib.sha256(chain + packed).digest()
    return chain


def check(
    *,
    score: int,
    pillars_passed: int,
    coin_count: int,
    time_alive: float,
    events: tuple,
    chain_hex: str,
) -> None:
    """Raise ``PlausibilityError`` on any failure; return ``None`` on pass.

    Each rule is named in the error message so debugging a rejection
    later doesn't require diffing the source against a stack trace."""

    # ── score sanity ────────────────────────────────────────────────────
    if not isinstance(score, int) or score < 0:
        raise PlausibilityError("score: must be a non-negative integer")
    if score > MAX_PLAUSIBLE_SCORE:
        raise PlausibilityError(f"score: exceeds MAX_PLAUSIBLE_SCORE ({MAX_PLAUSIBLE_SCORE})")

    # ── ledger integrity ────────────────────────────────────────────────
    actual_chain = _recompute_chain(events).hex()
    if actual_chain != chain_hex:
        raise PlausibilityError("chain: SHA-256 of events does not match the submitted chain hash")

    ledger_score = sum(int(e[1]) for e in events)
    if ledger_score != score:
        raise PlausibilityError(
            f"score: submitted ({score}) != sum of event dscores ({ledger_score})"
        )

    # ── per-event bounds ────────────────────────────────────────────────
    pipe_events = [e for e in events if e[2] == "pipe"]
    coin_events = [e for e in events if e[2] == "coin"]

    if any(int(e[1]) != 1 for e in pipe_events):
        raise PlausibilityError("events: pipe-pass dscore must be exactly 1")
    if any(int(e[1]) not in (1, 3) for e in coin_events):
        raise PlausibilityError("events: coin dscore must be 1 or 3")

    if len(pipe_events) != int(pillars_passed):
        raise PlausibilityError(
            f"events: ledger has {len(pipe_events)} pipe events but pillars_passed={pillars_passed}"
        )
    if len(coin_events) != int(coin_count):
        raise PlausibilityError(
            f"events: ledger has {len(coin_events)} coin events but coin_count={coin_count}"
        )

    # ── timing bounds ───────────────────────────────────────────────────
    last_t = -1.0
    for (t, _ds, _kind) in events:
        if float(t) < last_t:
            raise PlausibilityError("events: t_alive must be non-decreasing")
        last_t = float(t)

    last_pipe_t = -1e9
    for (t, _ds, _kind) in pipe_events:
        if float(t) - last_pipe_t < _MIN_PIPE_INTERVAL_S:
            raise PlausibilityError(
                "timing: pipe-pass events spaced closer than top-scroll allows"
            )
        last_pipe_t = float(t)

    if float(time_alive) < pillars_passed * (PIPE_SPACING / SCROLL_MAX) - 0.5:
        raise PlausibilityError(
            "timing: time_alive too short for the number of pillars passed"
        )

    # ── coin volume bound ──────────────────────────────────────────────
    rushes = pillars_passed // COIN_RUSH_INTERVAL + 1  # +1 for partial
    coin_ceiling = rushes * COIN_RUSH_COINS + max(pillars_passed, 0) * 5
    if coin_count > coin_ceiling:
        raise PlausibilityError(
            f"coins: collected {coin_count} but ceiling for {pillars_passed} pillars is {coin_ceiling}"
        )

    # ── pillars bound (max scroll speed) ────────────────────────────────
    pillars_ceiling = int(time_alive * SCROLL_MAX / PIPE_SPACING) + 2
    if pillars_passed > pillars_ceiling:
        raise PlausibilityError(
            f"pillars: passed {pillars_passed} in {time_alive:.2f}s but ceiling is {pillars_ceiling}"
        )


def is_displayable(score) -> bool:
    """Lightweight filter for the leaderboard read path. Drops rows that
    obviously can't be from a real run (negative, wrong type, or above
    the deterministic ceiling). A curl-injected ``score: 999999`` is
    invisible after this; a curl-injected ``score: 200`` is not — that
    requires server-side validation we don't have."""
    try:
        n = int(score)
    except (TypeError, ValueError):
        return False
    return 0 <= n <= MAX_PLAUSIBLE_SCORE
