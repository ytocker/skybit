"""Web-safe warren-route generation for the clown event.

The clown gauntlet is a tight "warren" of fused staff-pillars whose gap centres
trace a deliberate flight figure (plunge / climb / sine / valley / crest). The
look-dev versions of this live under tools/ (render_warren_routes,
render_warren_mockup) which are NOT bundled into the pygbag/web build, so the
inline gameplay event can't import them. This module re-homes just the route
GEOMETRY + the physics passability budget into game/ so the event builds the
same provably-flyable routes on both targets.

A route is a list of ``(gap_cy, gap_h)`` per pillar; the world places them at
``CLOWN_WARREN_SPACING`` apart. Every primitive keeps the per-pillar drift inside
the one-flap climb budget, and ``assert_passable`` is the final gate (a failure
falls back to a flat tube so a bad roll never breaks a run).
"""
from __future__ import annotations

import math

from game.config import (
    FLAP_V, GRAVITY, SCROLL_BASE, BIRD_R, PIPE_HITBOX_SHRINK, GROUND_Y,
    CLOWN_WARREN_SPACING as SP, CLOWN_WARREN_GAP as ROUTE_GAP,
)

# ── physics-derived passability budget (mirrors the look-dev tool) ────────────
# One flap buys FLAP_V**2 / (2*GRAVITY) px of altitude before gravity wins — the
# hard ceiling on climb per tap, anchoring every "is this slope flyable" check.
FLAP_RISE = (FLAP_V * FLAP_V) / (2.0 * GRAVITY)          # ~84 px
EFFECTIVE_R = BIRD_R - PIPE_HITBOX_SHRINK                # forgiven hitbox = 10 px
PARROT_H = 2 * BIRD_R

GAP_H_MIN, GAP_H_MAX = 150, 185        # per-pillar gap-height window
DRIFT_MAX = 56                         # per-pillar gap-centre vertical step
SPACING_MIN, SPACING_MAX = 62, 84      # fused-warren spacing window
CHANNEL_MIN = int(2.5 * PARROT_H)      # ~70 px clear threadable width
CEIL_PAD = 72
FLOOR_PAD = 72
GAP_CY_MIN = CEIL_PAD + GAP_H_MAX // 2
GAP_CY_MAX = GROUND_Y - FLOOR_PAD - GAP_H_MAX // 2


def assert_passable(name, pagodas):
    """Reject any corridor the real bird physics couldn't fly. Mirrors the
    look-dev budget exactly so an inline route is as fair as a vetted one."""
    prev = None
    for i, (x, cy, gap_h, _seed) in enumerate(pagodas):
        assert GAP_H_MIN <= gap_h <= GAP_H_MAX, \
            f"{name}: gap_h {gap_h} outside [{GAP_H_MIN},{GAP_H_MAX}]"
        assert GAP_CY_MIN <= cy <= GAP_CY_MAX, \
            f"{name}: gap centre {cy} too close to ceiling/ground"
        if prev is not None:
            px, pcy, pgap_h, _ = prev
            spacing = x - px
            assert SPACING_MIN <= spacing <= SPACING_MAX, \
                f"{name}: spacing {spacing} outside fused-warren window"
            drift = abs(cy - pcy)
            assert drift <= DRIFT_MAX, f"{name}: drift {drift} > {DRIFT_MAX}"
            top = max(cy - gap_h / 2, pcy - pgap_h / 2)
            bot = min(cy + gap_h / 2, pcy + pgap_h / 2)
            overlap = bot - top
            assert overlap >= CHANNEL_MIN + 2 * EFFECTIVE_R, \
                f"{name}: channel pinch {overlap:.0f}px between gaps {i-1}->{i}"
            travel_s = spacing / SCROLL_BASE
            taps = max(1, math.floor(travel_s / 0.34))   # ~0.34 s per useful tap
            climb_budget = FLAP_RISE * taps
            rise = max(0.0, pcy - cy)
            assert rise <= climb_budget, \
                f"{name}: needs {rise:.0f}px climb, budget {climb_budget:.0f}px"
        prev = (x, cy, gap_h, _seed)
    return True


class _Route:
    """Builds a route as a list of (x, gap_cy, gap_h, seed). Only the primitives
    the clown archetypes use are kept (hold / ramp / sine)."""

    def __init__(self, name):
        self.name = name
        self.pagodas = []
        self.cy = None

    def _push(self, cy, gap):
        cy = max(GAP_CY_MIN, min(GAP_CY_MAX, cy))
        x = len(self.pagodas) * SP
        self.pagodas.append((x, int(round(cy)), int(gap), 0))
        self.cy = cy

    def hold(self, n, cy, gap):
        for _ in range(n):
            self._push(cy, gap)
        return self

    def ramp(self, target, n, gap):
        start = self.cy if self.cy is not None else target
        for i in range(n):
            self._push(start + (target - start) * (i + 1) / n, gap)
        return self

    def sine(self, amp, wl, n, gap, base=None):
        b = base if base is not None else (self.cy if self.cy is not None else 300)
        for i in range(n):
            self._push(b + math.sin((i / wl) * 2 * math.pi) * amp, gap)
        return self


def _pads(n):
    pad = 2 if n >= 8 else 1
    return pad, pad


def _r_plunge(n):               # the long gentle dip
    r = _Route("Long Plunge")
    h, t = _pads(n); m = n - h - t
    r.hold(h, 210, ROUTE_GAP).ramp(410, m, ROUTE_GAP).hold(t, r.cy, ROUTE_GAP)
    return r


def _r_ascent(n):               # steady climb
    r = _Route("The Ascent")
    h, t = _pads(n); m = n - h - t
    r.hold(h, 410, ROUTE_GAP).ramp(210, m, ROUTE_GAP).hold(t, r.cy, ROUTE_GAP)
    return r


def _r_rolling(n):              # smooth sine
    r = _Route("Rolling Hills")
    h, t = _pads(n); m = n - h - t
    r.hold(h, 300, ROUTE_GAP).sine(62, 10, m, ROUTE_GAP, base=300) \
        .hold(t, r.cy, ROUTE_GAP)
    return r


def _r_valley(n):               # fall then climb (V)
    r = _Route("The Valley")
    h, t = _pads(n); m = n - h - t
    m1 = m // 2; m2 = m - m1
    r.hold(h, 255, ROUTE_GAP).ramp(405, m1, ROUTE_GAP) \
        .ramp(255, m2, ROUTE_GAP).hold(t, r.cy, ROUTE_GAP)
    return r


def _r_crest(n):                # climb then fall (hill)
    r = _Route("The Crest")
    h, t = _pads(n); m = n - h - t
    m1 = m // 2; m2 = m - m1
    r.hold(h, 405, ROUTE_GAP).ramp(255, m1, ROUTE_GAP) \
        .ramp(405, m2, ROUTE_GAP).hold(t, r.cy, ROUTE_GAP)
    return r


_ARCHETYPES = (_r_plunge, _r_ascent, _r_rolling, _r_valley, _r_crest)


def build_clown_route(n, rng):
    """Return a passable warren route of EXACTLY n pillars as a list of
    ``(gap_cy, gap_h)``. Picks a random archetype; on any passability failure
    falls back to a flat tube so a bad roll never breaks a run."""
    archetype = rng.choice(_ARCHETYPES)
    try:
        route = archetype(n)
        assert_passable(route.name, route.pagodas)
    except Exception:
        route = _Route("Flat Tube").hold(n, 300, ROUTE_GAP)
    return [(cy, gap_h) for (_x, cy, gap_h, _seed) in route.pagodas]
