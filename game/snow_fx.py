"""Windblown snow that accumulates on Pip during the predawn snow squall.

Chosen design: **W2 "sculpted blanket"** from the tools/sketch_snow_accum.py
exploration. The squall is a tailwind (blows left->right), so snow builds on
Pip's rear/left-facing surfaces first and spreads forward + inward as the storm
grows. Real-snow cues: rear end tapers to a point (no hard wall), a gentle
inward pile (not just an outline rim), a bright crest highlight, and a cool-blue
shadowed underside. As the storm reaches its PEAK (load -> 1.0) the blanket
grows to bury the entire parrot — every silhouette column filled top-to-bottom,
the face cap lifted — so Pip ends up fully covered in snow at the climax.

Overlays are baked per (frame, load-bucket) onto the native parrot frame using
its own alpha silhouette, then cached — so per-frame cost in Bird.draw is just
a rotozoom + blit (pure pygame, no numpy; WASM-safe). Bird.draw applies the
SAME rotozoom(tilt) the sprite gets, so the snow stays glued to Pip.
"""
from __future__ import annotations

import math

import pygame

from game import parrot

# Snow depth + palette (sprite px; W2 tuning from the sketch).
MAXD = 21.0
CORNICE = 1.6
WHITE = (255, 255, 255)
OFF = (236, 244, 252)
BLUE = (188, 206, 230)           # cool shadowed underside
SHADOW = (150, 168, 198)
_BUCKET = 0.06                    # load quantisation for the cache
_REF_FRAME = 2                    # level-wing frame: a stable resting silhouette
                                  # used for ALL frames so a wing flap can't pop
                                  # the head snow (the wing-up frame raises the
                                  # head topline ~6px → per-frame jitter otherwise)

_topline_cache: dict = {}
_overlay_cache: dict = {}


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _cov(xf, load):
    """Rear-first coverage: rear (left) columns snow at low load, the front
    only as the storm builds. The 0.42 spread (was 0.55) lets the blanket
    reach across more of the body sooner, so the first flakes read promptly
    instead of leaving Pip looking bare through the early load range."""
    thr = 0.42 * xf
    return 0.0 if load <= thr else min(1.0, (load - thr) / (1.0 - thr))


def _topline(frame_idx):
    """First AND last opaque row per column of the native frame (the top + bottom
    silhouette edges), plus the leftmost occupied column. The bottom edge lets
    the peak-storm overlay fill a whole column so Pip is fully buried. Cached per
    frame; no numpy."""
    cached = _topline_cache.get(frame_idx)
    if cached is not None:
        return cached
    frame = parrot._get_frames()[frame_idx]
    w, h = frame.get_size()
    mask = pygame.mask.from_surface(frame, 50)
    top = [-1] * w
    bot = [-1] * w
    x_min = -1
    for x in range(w):
        col_top = -1
        col_bot = -1
        for y in range(h):
            if mask.get_at((x, y)):
                if col_top < 0:
                    col_top = y
                col_bot = y
        top[x] = col_top
        bot[x] = col_bot
        if col_top >= 0 and x_min < 0:
            x_min = x
    _topline_cache[frame_idx] = (top, bot, x_min, w, h)
    return _topline_cache[frame_idx]


def get_snow_overlay(load, frame_idx=None):
    """Cached W2 snow overlay (native frame size) for this load. Below the
    full-cover band it's baked from a single resting frame (frame-independent)
    so a wing flap never jitters the head snow; at FULL cover (load≈1.0) it's
    baked from the CURRENT frame so the actual silhouette — raised wing and all
    — is buried."""
    if load <= 0.04:
        return None
    b = round(load / _BUCKET) * _BUCKET
    # Bake from the CURRENT frame so the snow matches the drawn wing pose at every
    # load. Only the full wing-up frame differs (head topline ~5px higher); using
    # _REF_FRAME for it left a visible gap above the snow during flaps. _REF_FRAME
    # is only the fallback when no frame is supplied.
    use_frame = frame_idx if frame_idx is not None else _REF_FRAME
    key = (b, use_frame)
    cached = _overlay_cache.get(key)
    if cached is not None:
        return cached

    top, bot, x_min, w, h = _topline(use_frame)
    if x_min < 0:
        _overlay_cache[key] = None
        return None
    # Resting-frame topline: at partial load the snow top is capped to this so a
    # raised wing (frame 0 lifts the silhouette ~5–8px over the head/back) does
    # NOT grow an isolated snow blob that pops above the eye between flap frames.
    # At full cover (fc→1) we ease back to the live frame so the wing still buries.
    ref_top = _topline(_REF_FRAME)[0]
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    taper_w = 13.0
    # Perceptual load: snow_load rises LINEARLY in time, but a linear load left
    # Pip looking bare through the first chunk of the storm (the rear sliver is
    # too thin to read) and then snapped to fully-buried near the peak. Ease the
    # load IN (gamma < 1) so the visible accumulation is front-loaded — the first
    # flakes show promptly and the curve climbs evenly instead of dead-then-rush.
    bv = b ** 0.72
    # Full-cover ramp: from 0.62 up to peak (load 1.0) the snow grows to bury the
    # ENTIRE parrot — every column filled top->bottom of its silhouette, face cap
    # lifted — so at the storm peak Pip is completely covered. Driven by the eased
    # load over a wide range (was a narrow 0.78->1.0 snap), so the final
    # "blanket -> fully buried" change is gradual, not a sudden snap near the peak.
    fc = _smooth((bv - 0.62) / (1.0 - 0.62))
    drew = False
    for x in range(w):
        yt = top[x]
        yb = bot[x]
        if yt < 0:
            continue
        # Cap the snow top to the resting silhouette at partial load (no snow on a
        # lifted wing tip), easing to the live topline as full cover takes over.
        rt = ref_top[x]
        if rt >= 0:
            yt = yt + max(0.0, rt - yt) * (1.0 - fc)
        xf = x / w
        # Coverage: rear-first blanket, but forced to full on every column as the
        # full-cover ramp engages so the front/head get buried too.
        cov = max(_cov(xf, bv), fc)
        if cov <= 0.0:
            continue
        rear = 1.0 - xf
        bulge = math.exp(-((xf - 0.40) / 0.26) ** 2)        # inward hump
        d_bl = MAXD * cov * (0.50 + 0.45 * rear + 0.45 * bulge)
        if xf > 0.60:
            # Head: a thin crown cap at low load, but as the storm peaks
            # (load 0.68->1.0) snow creeps onto the face — more on the LEFT
            # (back) of the head, tapering so the front/beak stays readable.
            hi = max(0.0, (bv - 0.55) / 0.45)
            headfrac = (xf - 0.60) / 0.40                   # 0 back-of-head .. 1 beak
            d_bl = min(d_bl, 7.0 + hi * 11.0 * (1.0 - headfrac))
        taper = _smooth((x - x_min) / taper_w)              # rear-end slope
        d_bl *= taper
        # Blend the blanket depth toward the full silhouette column at peak.
        d_full = max(0.0, yb - yt)
        d = d_bl * (1.0 - fc) + max(d_bl, d_full) * fc
        if d < 0.6:
            continue
        # Rear-edge cornice eases out as full cover takes over (the whole top is
        # snow by then, so a per-column lip would just look ragged).
        over = CORNICE * (rear * taper * (1.0 - fc) + fc)
        nb = (math.sin(x * 1.26) + math.sin(x * 0.34)) * 0.25 + 0.5
        y0 = yt - over
        y1 = yt + d + (nb - 0.5) * 2.4 * (1.0 - fc)         # quiet the noise at full cover
        span = max(1.0, y1 - y0)
        # W2 sculpted blanket: clean fill + bright crest + cool under-edge.
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + max(2.0, span * 0.18))), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - max(2.0, span * 0.26))), (x, int(y1)), 1)
        drew = True
    if not drew:
        _overlay_cache[key] = None
        return None
    _overlay_cache[key] = ov
    return ov


# ── snow on the parcel (snow settles on objects too, only at high load) ──────
PARCEL_MAXD = 7.0
PARCEL_ONSET = 0.68               # parcel only gets capped once Pip is well-covered

_parcel_top_cache: dict = {}
_parcel_ov_cache: dict = {}


def _parcel_topline(mode):
    cached = _parcel_top_cache.get(mode)
    if cached is not None:
        return cached
    p = parrot.get_parcel(mode)
    w, h = p.get_size()
    mask = pygame.mask.from_surface(p, 50)
    top = [-1] * w
    bot = [-1] * w
    x_min = -1
    for x in range(w):
        col_top = -1
        col_bot = -1
        for y in range(h):
            if mask.get_at((x, y)):
                if col_top < 0:
                    col_top = y
                col_bot = y
        top[x] = col_top
        bot[x] = col_bot
        if col_top >= 0 and x_min < 0:
            x_min = x
    _parcel_top_cache[mode] = (top, bot, x_min, w, h)
    return _parcel_top_cache[mode]


def get_parcel_snow(mode, load):
    """Small W2 snow cap on the parcel's top, fading in over PARCEL_ONSET→1.0
    (snow lands on objects, not under them). Cached per (mode, ramp-bucket)."""
    if load < PARCEL_ONSET:
        return None
    ll = min(1.0, (load - PARCEL_ONSET) / (1.0 - PARCEL_ONSET))
    b = round(ll / 0.1) * 0.1
    key = (mode, b)
    cached = _parcel_ov_cache.get(key)
    if cached is not None:
        return cached
    top, bot, x_min, w, h = _parcel_topline(mode)
    if x_min < 0:
        _parcel_ov_cache[key] = None
        return None
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    taper_w = 4.0
    # Full-cover ramp: a small lid early, but as the snow peaks the cap grows to
    # bury the WHOLE parcel (every column filled top->bottom) so it whites out
    # with Pip rather than keeping a bare underside.
    fc = _smooth((ll - 0.45) / 0.55)
    drew = False
    for x in range(w):
        yt = top[x]
        yb = bot[x]
        if yt < 0:
            continue
        rear = 1.0 - x / w
        te = _smooth((x - x_min) / taper_w)
        d_cap = PARCEL_MAXD * ll * (0.65 + 0.5 * rear) * te
        d_full = max(0.0, yb - yt)
        d = d_cap * (1.0 - fc) + max(d_cap, d_full) * fc
        if d < 0.6:
            continue
        nb = math.sin(x * 1.7) * 0.25 + 0.5
        y0 = yt - 0.6 * te * (1.0 - fc)
        y1 = yt + d + (nb - 0.5) * 1.4 * (1.0 - fc)
        span = max(1.0, y1 - y0)
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + max(1.5, span * 0.22))), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - max(1.5, span * 0.3))), (x, int(y1)), 1)
        drew = True
    if not drew:
        _parcel_ov_cache[key] = None
        return None
    _parcel_ov_cache[key] = ov
    return ov
