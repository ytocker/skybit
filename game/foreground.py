"""Live play-scene foreground facade — the buff sandstone sidewalk that replaces
the grass meadow ground.

Stage 1 ships the floor + embedded surface detail. Later stages add the
promenade props/characters and the near/front activity lane through this same
facade. All procedural; safe on native + web.
"""
from __future__ import annotations

import pygame

from game.config import W, H, GROUND_Y
from game import biome
from game import foreground_floor as _floor
from game import foreground_detail as _detail
from game import foreground_promenade as _promenade
from game import foreground_near_lane as _near
from game import foreground_weather as _gweather
from game import foreground_zbuffer as _zbuf


# The floor + embedded detail are STATIC: a pure function of world-x (scroll) and
# the biome palette. Recomputing the ~250 draws + ~100k per-cell RNG seeds every
# frame was the single biggest per-frame cost. Instead we bake a wide strip once
# per (palette bucket, world window) and just blit it at the scroll offset — the
# same per-bucket palette quantisation the pillars already use (they bake their
# palette once at spawn and never re-tint). A generous side margin lets the strip
# scroll a few hundred px before it must be re-baked.
_FLOOR_MARGIN = 256
_FLOOR_STRIP_W = W + 2 * _FLOOR_MARGIN
# Small headroom above GROUND_Y so the contact lip/shadow is captured too.
_FLOOR_BAND_TOP = GROUND_Y - 4

_floor_strip = None        # cached pygame.Surface (None until first bake)
_floor_anchor = 0.0        # world-x mapped to local x=0 of the strip
_floor_bucket = -1         # biome.phase_bucket the strip was baked for

# The stateful near-lane crowd (game.sidewalk_crowd.SidewalkCrowd), registered by
# World.__init__. Held here so draw_near_lane can hand it to the lane module
# without threading it through every scenes.py call site. Re-registered whenever a
# new World is built (each run), so it always points at the live sim.
_crowd = None


def set_crowd(crowd):
    global _crowd
    _crowd = crowd


def _bake_floor_strip(scroll, pal, bucket):
    global _floor_strip, _floor_anchor, _floor_bucket
    # Anchor on an integer world-x so an integer scroll reproduces the live
    # render bit-for-bit (the floor ints every position via `int(wx - scroll)`);
    # a fractional scroll then drifts at most 1px, imperceptibly.
    anchor = int(round(scroll)) - _FLOOR_MARGIN
    band_h = H - _FLOOR_BAND_TOP
    gy_local = GROUND_Y - _FLOOR_BAND_TOP   # where the play-floor band starts
    strip = pygame.Surface((_FLOOR_STRIP_W, band_h), pygame.SRCALPHA)
    _floor.fg_swatch_buff_running_bond(strip, _FLOOR_STRIP_W, gy_local, band_h,
                                       anchor, pal)
    _detail.add_embedded_detail("buff", strip, _FLOOR_STRIP_W, gy_local, band_h,
                                anchor, pal)
    _floor_strip = strip
    _floor_anchor = anchor
    _floor_bucket = bucket


def draw_foreground_floor(surf, scroll, pal, phase):
    """Paint the buff running-bond sidewalk + its embedded surface detail into
    the ~45px play-floor band (y=GROUND_Y..H), world-anchored to `scroll`.

    Served from a cached strip; re-baked only when the palette bucket changes or
    the scroll leaves the baked window, so the per-frame cost is a single blit."""
    bucket = biome.phase_bucket(phase)
    off = scroll - _floor_anchor
    if (_floor_strip is None or bucket != _floor_bucket
            or off < 0 or off + W > _FLOOR_STRIP_W):
        _bake_floor_strip(scroll, pal, bucket)
        off = scroll - _floor_anchor
    surf.blit(_floor_strip, (round(-off), _FLOOR_BAND_TOP))


def draw_ground_weather(surf, scroll, pal, wetness, snow_cover):
    """Paint the weather's reactive ground state (wet sheen + puddles, snow
    dusting) onto the sidewalk band — drawn after the floor, before the crowd, so
    it glazes/frosts the paving UNDER the cast's feet."""
    _gweather.draw_ground_weather(surf, scroll, pal, wetness, snow_cover)


def draw_promenade(surf, scroll, pal, phase, t):
    """Draw the FAR promenade props + living cast on the sidewalk, depth-sorted by
    feet-Y. Flushed here (in _draw_background, before the gameplay pillars) so the
    far lane sits BEHIND the pillars, as it always has."""
    _zbuf.reset()
    _promenade.draw_promenade(surf, scroll, pal, phase, t)   # enqueue only
    _zbuf.flush(surf)


def draw_near_lane(surf, scroll, pal, phase, t):
    """Draw the NEAR/front activity lane, depth-sorted by feet-Y. Flushed here —
    relocated in scenes._render to run AFTER the gameplay pillars — so near-lane
    plants/people (feet lower on screen) occlude the pillar bases."""
    _near.draw_near_lane(surf, scroll, pal, phase, t, crowd=_crowd)  # enqueue only
    _zbuf.flush(surf)
