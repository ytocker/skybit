"""Baked visual assets for the morning-thermal geysers.

Everything expensive (the sinter-cone vent, the flowing steam column, and the
scattered sinter rocks) is rendered ONCE into cached surfaces here, so the
per-frame cost in ``Geyser.draw`` / ``Rock.draw`` is blit-only — important for
the pygbag/WASM target. Mirrors the long-standing ``_get_geyser_column`` bake
pattern. Pure pygame (no numpy), procedural art only.

Designs were chosen in the throwaway ``tools/sketch_geyser_*`` explorations:
V1 sinter cone, V1 sinter rocks ("rocks match cone"), and the M4 steam column
(9 sub-columns, 1.4x opacity, with a base-weighted opacity boost easing to the
faint baseline higher up).
"""
from __future__ import annotations

import math

import pygame

from game.config import GEYSER_W, GEYSER_H
from game import biome

PERIOD = 1.6                      # steam loop length (s) — matches the sketch
WINDW = (255, 252, 244)          # near-white vapour

# The vent cone + scattered rocks are sandstone like the pillars, so they take
# their colours from the biome STONE palette — the same keys the pillars use —
# to read as one theme. Geysers only appear in the golden-hour→sunset band, so
# baking at a representative phase in that band matches the pillars on screen.
_TINT_PHASE = 0.25


def _stone():
    return biome.palette_for_phase(_TINT_PHASE)

# ── tiny local draw helpers (used only during the one-time bake) ─────────────


def _lerp_c(a, b, t):
    t = max(0.0, min(1.0, t))
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


def _sc(c, m):
    m = max(0.0, min(1.0, m))
    return (int(c[0] * m), int(c[1] * m), int(c[2] * m))


def _blur(s, downs):
    w, h = s.get_size()
    if w < downs * 2 or h < downs * 2:
        return s
    sm = pygame.transform.smoothscale(s, (w // downs, h // downs))
    return pygame.transform.smoothscale(sm, (w, h))


def _ell(surf, cx, cy, rx, ry, color, alpha=255, blur=0):
    rx, ry = max(1, int(rx)), max(1, int(ry))
    s = pygame.Surface((rx * 2 + 4, ry * 2 + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (int(color[0]), int(color[1]), int(color[2]),
                            int(alpha)), (2, 2, rx * 2, ry * 2))
    if blur:
        s = _blur(s, blur)
    surf.blit(s, (int(cx - rx - 2), int(cy - ry - 2)))


_soft_cache: dict = {}


def _soft(rad, color, alpha):
    rad = max(1, int(rad))
    key = (rad, color, int(alpha) // 8 * 8)
    s = _soft_cache.get(key)
    if s is None:
        d = rad * 2 + 2
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, 255), (d // 2, d // 2),
                           max(1, int(rad * 0.62)))
        s = _blur(s, 3 if rad >= 6 else 2)
        s.fill((*color, int(alpha)), special_flags=pygame.BLEND_RGBA_MULT)
        _soft_cache[key] = s
    return s


def _stamp(surf, x, y, rad, color, alpha):
    b = _soft(rad, color, alpha)
    surf.blit(b, (int(x - b.get_width() / 2), int(y - b.get_height() / 2)))


# ── V1 sinter-cone vent (baked once) ─────────────────────────────────────────

CONE_W, CONE_H = 96, 42
CONE_BASE_ROW = 28               # surface row that maps to GROUND_Y
_MOUTH_ROW = 14                  # surface row where the throat opens (steam base)
MOUTH_DY = CONE_BASE_ROW - _MOUTH_ROW   # steam base sits this far above GROUND_Y

_vent_cone_cache: "pygame.Surface | None" = None


def get_vent_cone() -> "pygame.Surface":
    global _vent_cone_cache
    if _vent_cone_cache is None:
        s = pygame.Surface((CONE_W, CONE_H), pygame.SRCALPHA)
        x, base_y = CONE_W // 2, CONE_BASE_ROW
        pal = _stone()
        hi, lo, dk = pal["stone_light"], pal["stone_mid"], pal["stone_dark"]
        cone_h = 15
        for k in range(cone_h + 1):
            u = k / cone_h
            _ell(s, x, base_y - k, 40 - 9 * u, 12 - 4 * u, _lerp_c(lo, hi, u * 0.8))
        top = base_y - cone_h
        _ell(s, x, top, 31, 8, hi)
        _ell(s, x, top + 1, 25, 6, _sc(dk, 0.8))           # wet throat
        _ell(s, x, top + 1, 19, 4, _sc(dk, 0.45))
        _stamp(s, x - 15, top + 3, 16, (255, 250, 240), 70)    # warm-lit left
        _stamp(s, x + 17, base_y - 3, 15, _sc(lo, 0.4), 60)    # shadow right
        for dxs in (-16, -6, 6, 16):                       # drip cracks
            pygame.draw.line(s, _sc(lo, 0.7), (int(x + dxs), top + 6),
                             (int(x + dxs * 1.08), base_y - 3), 1)
        _vent_cone_cache = s
    return _vent_cone_cache


# ── steam column (baked once into a looping frame set) ───────────────────────

STEAM_W, STEAM_H = 128, int(GEYSER_H)
STEAM_FPS = 20                    # frames are full screen-height now → fewer, lighter
STEAM_N = int(PERIOD * STEAM_FPS)
_STEAM_BASE_ALPHA = 21.0          # the faint baseline (the locked 1.4x level)
_STEAM_BOOST = 2.4               # base-region opacity multiplier
_STEAM_NORM_FRAC = 0.30          # eases back to baseline by this frac of height

_steam_frames: "list[pygame.Surface] | None" = None
_boost_mask_cache: "pygame.Surface | None" = None


def _life(p):
    return math.sin(math.pi * p) ** 0.7


def _swoosh(scene, pts, ws, maxw, color, alpha, blur=2):
    n = len(pts)
    left, right = [], []
    for i in range(n):
        x, y = pts[i]
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        hw = ws[i] * maxw
        left.append((x + nx * hw, y + ny * hw))
        right.append((x - nx * hw, y - ny * hw))
    poly = left + right[::-1]
    xs = [q[0] for q in poly]
    ys = [q[1] for q in poly]
    minx, miny = int(min(xs)) - 3, int(min(ys)) - 3
    w = int(max(xs)) - minx + 3
    h = int(max(ys)) - miny + 3
    if w < 3 or h < 3:
        return
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(s, (*color, int(max(0, min(255, alpha)))),
                        [(px - minx, py - miny) for px, py in poly])
    if blur:
        s = _blur(s, blur)
    scene.blit(s, (minx, miny))


def _flow_ribbon(scene, x, by, h, t, phase, *, amp, length_f, maxw, alpha,
                 fan, blur, spd):
    p = ((t / PERIOD) * spd + phase) % 1.0
    y_bot = by - (0.02 + 0.22 * p) * h
    length = h * length_f
    ph = 2 * math.pi * t / PERIOD
    segs = 22
    pts, ws = [], []
    for k in range(segs + 1):
        u = k / segs
        yy = y_bot - u * length
        wav = math.sin(u * 3.4 - ph * 1.5 + phase * 6.0) * amp * (0.25 + u)
        taper = 1.0 - max(0.0, (u - 0.85) / 0.15) ** 2
        pts.append((x + wav + fan * u, yy))
        ws.append((0.3 + 0.85 * u) * taper)
    _swoosh(scene, pts, ws, maxw, WINDW, alpha * _life(p), blur=blur)


def _boost_mask() -> "pygame.Surface":
    """Vertical alpha-multiply gradient: 1.0 at the base, 1/BOOST at the top.
    Ribbons are baked at BASE*BOOST, so multiplying by this leaves the base
    boosted and the upper column back at the faint baseline."""
    global _boost_mask_cache
    if _boost_mask_cache is None:
        col = pygame.Surface((1, STEAM_H), pygame.SRCALPHA)
        ground = STEAM_H - 1
        norm = ground - _STEAM_NORM_FRAC * ground
        for y in range(STEAM_H):
            if y >= norm:
                frac = (y - norm) / max(1.0, ground - norm)
                factor = 1.0 + (_STEAM_BOOST - 1.0) * frac
            else:
                factor = 1.0
            a = int(255 * factor / _STEAM_BOOST)
            col.set_at((0, y), (255, 255, 255, max(0, min(255, a))))
        _boost_mask_cache = pygame.transform.scale(col, (STEAM_W, STEAM_H))
    return _boost_mask_cache


def get_steam_frames() -> "list[pygame.Surface]":
    global _steam_frames
    if _steam_frames is None:
        span, ncols = 28.0, 9
        offs = [-span + 2 * span * j / (ncols - 1) for j in range(ncols)]
        cx, by, rise = STEAM_W / 2, STEAM_H, STEAM_H - 4
        mask = _boost_mask()
        frames = []
        for fi in range(STEAM_N):
            t = fi / STEAM_FPS
            s = pygame.Surface((STEAM_W, STEAM_H), pygame.SRCALPHA)
            for c, dx in enumerate(offs):
                for i in range(3):
                    idx = c * 3 + i
                    _flow_ribbon(s, cx + dx, by, rise, t,
                                 (idx * 0.6180339) % 1.0,
                                 amp=6 + (idx % 3) * 5,
                                 length_f=0.9 + 0.06 * (idx % 2),
                                 maxw=3.4 + 1.2 * (idx % 2),
                                 alpha=_STEAM_BASE_ALPHA * _STEAM_BOOST,
                                 fan=(i - 1) * 4, blur=3,
                                 spd=0.9 + 0.05 * (idx % 3))
            s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            frames.append(s)
        _steam_frames = frames
    return _steam_frames


# ── V1 sinter rocks (baked once into a handful of size variants) ─────────────

_ROCK_SHADOW = (34, 48, 22)       # soft green contact shadow on the grass
_ROCK_SIZES = (3.5, 4.5, 5.5, 6.5, 7.5, 8.5)
ROCK_N = len(_ROCK_SIZES)
ROCK_MAX_W = int(_ROCK_SIZES[-1] * 1.05 * 2) + 6

_rock_variants: "list[tuple] | None" = None


def get_rock_variants() -> "list[tuple]":
    """List of (surface, ox, oy): blit at (rock.x - ox, rock.y - oy) to place
    the rock's centre at (rock.x, rock.y)."""
    global _rock_variants
    if _rock_variants is None:
        pal = _stone()
        body, facet, speck = pal["stone_mid"], pal["stone_light"], pal["stone_accent"]
        out = []
        for rw in _ROCK_SIZES:
            rh = rw * 0.8
            cw = int(rw * 1.05 * 2) + 6
            ch = int(2.2 * rh) + 6
            ox, oy = cw / 2.0, rh + 3.0
            s = pygame.Surface((cw, ch), pygame.SRCALPHA)
            _ell(s, ox + 1, oy + rh * 0.7, rw * 1.05, max(2, rh * 0.5),
                 _ROCK_SHADOW, alpha=85)
            _ell(s, ox, oy, rw, rh, body)
            _ell(s, ox - rw * 0.18, oy - rh * 0.22, rw * 0.6, rh * 0.6, facet)
            _stamp(s, ox - 1, oy - rh * 0.3, 2, speck, 120)
            out.append((s, ox, oy))
        _rock_variants = out
    return _rock_variants


def prewarm() -> None:
    """Bake every cache up front (cone, steam frame loop, rock variants) so the
    first geyser eruption mid-run never stutters. Called once from World."""
    get_vent_cone()
    get_steam_frames()
    get_rock_variants()
