"""Exploration harness for the Stage-B PLANT FAMILY UPGRADE.

Five DISTINCT procedural greenery families for the Chinese market promenade,
each rendered as a full SET (potted bamboo, bonsai/tiered pine, flowering
shrub, cascading vine) at DAY and at NIGHT side by side on a neutral deck
strip for scale. Pure-Pygame, headless (SDL dummy), saved to the round sheet.

Nothing here is written into game/ — this is a review-sheet generator. The
night retint follows the live convention: foliage is mixed toward a cool
night blue by a `night` factor derived from the biome's day/night keyframes,
so plants DARKEN and never out-glow the gameplay actors.
"""
from __future__ import annotations

import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

# ── biome keyframes lifted from game/biome.py (DAY = keyframe 0, NIGHT) ────────
PAL_DAY = dict(
    stone_mid=(175, 140, 105), stone_dark=(95, 70, 55),
    foliage_top=(140, 220, 110), foliage_mid=(70, 170, 75),
    foliage_dark=(30, 100, 50), sky_top=(40, 110, 200),
)
PAL_NIGHT = dict(
    stone_mid=(80, 100, 150), stone_dark=(30, 45, 85),
    foliage_top=(80, 130, 130), foliage_mid=(35, 80, 90),
    foliage_dark=(10, 35, 55), sky_top=(5, 8, 30),
)


def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _nightf(pal):
    r, g, b = pal.get('sky_top', (60, 120, 200))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return max(0.0, min(1.0, (95.0 - lum) / 75.0))


# Cool night target for foliage — the same blue the live foreground mixes to.
_NIGHT_BLUE = (40, 56, 86)


def _fol(pal):
    """Foliage sub-palette cooled toward night so plants match the deck."""
    n = _nightf(pal)
    return {
        'dark': _mix(pal['foliage_dark'], _NIGHT_BLUE, 0.30 * n),
        'mid':  _mix(pal['foliage_mid'], (46, 64, 94), 0.30 * n),
        'top':  _mix(pal['foliage_top'], (60, 80, 110), 0.30 * n),
    }


# A bloom colour at night is DARKENED + desaturated so a flower never spikes
# brighter than the coin. Day blooms keep their saturated pop.
def _bloom(color, pal, *, cap=150):
    n = _nightf(pal)
    if n <= 0.02:
        return color
    c = _mix(color, _shade(color, -70), 0.55 * n)
    c = _mix(c, (70, 70, 96), 0.30 * n)
    lum = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    if lum > cap and lum > 0:
        f = cap / lum
        c = (int(c[0] * f), int(c[1] * f), int(c[2] * f))
    return c


# ══════════════════════════════════════════════════════════════════════════
# Shared POT primitives — glazed ceramic vessels replacing the flat boxes.
# ══════════════════════════════════════════════════════════════════════════

def _pot_glaze(surf, sx, by, w, h, base, *, rim=True, motif=None, night=0.0):
    """A glazed ceramic pot: tapered body, a lit rim lip, a soft vertical
    sheen, and an optional motif band. `base` is the day glaze colour; it is
    cooled by `night`. Feet rest at `by`."""
    base = _mix(base, (62, 70, 100), 0.34 * night)
    top_w = w
    bot_w = max(6, int(w * 0.72))
    x0t, x1t = sx - top_w // 2, sx + top_w // 2
    x0b, x1b = sx - bot_w // 2, sx + bot_w // 2
    body = [(x0t, by - h), (x1t, by - h), (x1b, by), (x0b, by)]
    pygame.draw.polygon(surf, _shade(base, -26), body)
    inner = [(x0t + 1, by - h + 1), (x1t - 1, by - h + 1),
             (x1b, by - 1), (x0b, by - 1)]
    pygame.draw.polygon(surf, base, inner)
    # A soft vertical sheen on the left third — the wet-glaze highlight.
    sheen = _mix(base, (255, 255, 255), 0.22 * (1.0 - 0.5 * night))
    pygame.draw.line(surf, sheen, (x0t + 2, by - h + 2), (x0b + 2, by - 2), 2)
    # Shaded right edge for roundness.
    pygame.draw.line(surf, _shade(base, -34), (x1t - 1, by - h + 1),
                     (x1b - 1, by - 1), 1)
    # Rim lip — a flared collar with a lit top edge.
    if rim:
        rim_c = _mix(base, (255, 255, 255), 0.30 * (1.0 - 0.55 * night))
        pygame.draw.rect(surf, _shade(base, -22),
                         (x0t - 1, by - h - 2, top_w + 2, 3))
        pygame.draw.line(surf, rim_c, (x0t, by - h - 2), (x1t, by - h - 2), 1)
    # Motif band — a thin painted ring a third up the body.
    if motif is not None:
        my = by - int(h * 0.55)
        mw = int(top_w * 0.86)
        mc = _mix(motif, (40, 50, 80), 0.4 * night)
        for i in range(-mw // 2, mw // 2, 4):
            pygame.draw.line(surf, mc, (sx + i, my),
                             (sx + i + 2, my), 1)


def _terracotta(night):
    return _mix((176, 96, 58), (62, 70, 100), 0.34 * night)


def _blue_white(night):
    return _mix((228, 232, 240), (62, 70, 100), 0.30 * night)


def _celadon(night):
    return _mix((150, 186, 158), (62, 70, 100), 0.32 * night)


# ══════════════════════════════════════════════════════════════════════════
# PLANT BUILDING BLOCKS — each family overrides these with its own idiom.
# ══════════════════════════════════════════════════════════════════════════

def _leaf_spray(surf, ox, oy, ang, length, col, *, n=4, spread=0.5, lw=1):
    """A fan of thin leaves from a stem joint — the bamboo / fern idiom."""
    for i in range(n):
        a = ang + (i - (n - 1) / 2) * spread / max(1, n - 1)
        ex = ox + int(math.cos(a) * length)
        ey = oy - int(math.sin(a) * length)
        mx = ox + int(math.cos(a) * length * 0.5)
        my = oy - int(math.sin(a) * length * 0.5) - 1
        pygame.draw.lines(surf, col, False, [(ox, oy), (mx, my), (ex, ey)], lw)


# ── Family A: SCHOLAR'S COURTYARD — refined, painterly, blue-and-white pots ───

def fam_scholar_bamboo(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 18, 12, _blue_white(n), motif=(70, 110, 180), night=n)
    cane = _mix((150, 180, 110), (60, 74, 100), 0.34 * n)
    cane_dk = _shade(cane, -34)
    top = by - 12
    for i, (dx, htop, lean) in enumerate(((-4, 30, -2), (0, 36, 0), (5, 27, 3))):
        cx = sx + dx
        ct = top - htop
        # Segmented cane: short verticals with a darker node band between.
        segs = 5
        for s in range(segs):
            y0 = top - htop * s // segs
            y1 = top - htop * (s + 1) // segs
            nx = cx + int(lean * (s / segs))
            pygame.draw.line(surf, cane, (nx, y0), (nx + lean // segs, y1), 2)
            pygame.draw.line(surf, cane_dk, (nx - 1, y1 + 1),
                             (nx + 2, y1 + 1), 2)
        # Thin leaf sprays at the upper joints.
        for s in range(2, segs):
            jy = top - htop * s // segs
            jx = cx + int(lean * (s / segs))
            _leaf_spray(surf, jx, jy, 1.1 + 0.4 * (i - 1), 8,
                        f['mid'], n=3, spread=0.7)
            _leaf_spray(surf, jx, jy, 2.1, 7, f['dark'], n=2, spread=0.5)
        pygame.draw.line(surf, _shade(cane, 24), (cx, ct), (cx, ct + 6), 1)


def fam_scholar_bonsai(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 22, 9, _blue_white(n), motif=(70, 110, 180), night=n)
    trunk = _mix((96, 70, 46), (58, 62, 92), 0.32 * n)
    top = by - 9
    # A gnarled S-trunk: short kinked segments leaning right.
    pts = [(sx - 2, top), (sx, top - 8), (sx + 4, top - 14),
           (sx + 2, top - 22), (sx + 6, top - 28)]
    pygame.draw.lines(surf, _shade(trunk, -26), False, pts, 4)
    pygame.draw.lines(surf, trunk, False, pts, 2)
    # Distinct horizontal foliage tiers (clouds), darkest at the bottom.
    tiers = (((sx - 8, top - 16), 11, 4), ((sx + 9, top - 22), 9, 3),
             ((sx + 4, top - 30), 8, 3), ((sx - 4, top - 27), 7, 3))
    for (cx, cy), tw, th in tiers:
        pygame.draw.ellipse(surf, f['dark'], (cx - tw, cy - th, tw * 2, th * 2))
        pygame.draw.ellipse(surf, f['mid'],
                            (cx - tw + 1, cy - th, tw * 2 - 3, th * 2 - 1))
        pygame.draw.ellipse(surf, f['top'],
                            (cx - tw + 3, cy - th, tw - 2, max(2, th)))


def fam_scholar_flower(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 20, 11, _blue_white(n), motif=(70, 110, 180), night=n)
    top = by - 11
    # A rounded dark-green mound.
    pygame.draw.ellipse(surf, f['dark'], (sx - 13, top - 18, 26, 22))
    pygame.draw.ellipse(surf, f['mid'], (sx - 11, top - 17, 22, 19))
    pygame.draw.ellipse(surf, f['top'], (sx - 9, top - 17, 14, 8))
    # Peony blooms — clustered 3-petal dabs studding the mound.
    rng = random.Random(11)
    cols = ((236, 120, 170), (244, 180, 200), (220, 70, 90))
    for _ in range(9):
        a = rng.uniform(0, math.tau)
        rr = rng.uniform(2, 11)
        bx = sx + int(math.cos(a) * rr)
        byp = top - 9 + int(math.sin(a) * rr * 0.7)
        c = _bloom(rng.choice(cols), pal)
        pygame.draw.circle(surf, _shade(c, -40), (bx, byp), 2)
        pygame.draw.circle(surf, c, (bx, byp), 1)
        pygame.draw.circle(surf, _bloom((255, 230, 150), pal), (bx, byp), 0)


def fam_scholar_vine(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 16, 12, _blue_white(n), motif=(70, 110, 180), night=n)
    top = by - 12
    # A vine spilling over the LEFT lip — a curving stem with paired leaves.
    stem = [(sx - 7, top - 1)]
    for i in range(1, 13):
        t = i / 12
        px = sx - 7 - int(math.sin(t * 2.2) * 4) - int(t * 3)
        py = top - 1 + int(t * 22)
        stem.append((px, py))
    pygame.draw.lines(surf, f['dark'], False, stem, 2)
    for i, (px, py) in enumerate(stem):
        if i % 2 == 0 and i > 0:
            side = 1 if i % 4 == 0 else -1
            # Heart/teardrop leaf as a small filled triangle pair.
            lx = px + side * 3
            pygame.draw.polygon(surf, f['mid'],
                                [(px, py), (lx, py - 2), (lx + side, py + 2)])
            pygame.draw.polygon(surf, f['top'],
                                [(px, py), (lx, py - 1), (lx, py + 1)])
    # The odd small flower along the trail.
    for (px, py) in (stem[4], stem[9]):
        c = _bloom((240, 200, 120), pal)
        pygame.draw.circle(surf, c, (px - 2, py), 1)


# ── Family B: TEMPLE MARKET — bold, festive, terracotta + red glaze ───────────

def fam_market_bamboo(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 19, 13, _terracotta(n), night=n)
    cane = _mix((120, 165, 80), (60, 74, 100), 0.34 * n)
    cane_dk = _shade(cane, -38)
    top = by - 13
    for i, (dx, htop) in enumerate(((-5, 27), (-1, 34), (4, 30), (8, 23))):
        cx = sx + dx
        segs = 4
        for s in range(segs):
            y0 = top - htop * s // segs
            y1 = top - htop * (s + 1) // segs
            pygame.draw.line(surf, cane, (cx, y0), (cx, y1), 2)
            pygame.draw.line(surf, cane_dk, (cx - 1, y1), (cx + 1, y1), 2)
        for s in range(1, segs):
            jy = top - htop * s // segs
            _leaf_spray(surf, cx, jy, 0.9, 9, f['mid'], n=4, spread=1.0)
            _leaf_spray(surf, cx, jy, 2.2, 8, f['dark'], n=3, spread=0.8)


def fam_market_bonsai(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 23, 10, _terracotta(n), night=n)
    trunk = _mix((110, 76, 48), (58, 62, 92), 0.30 * n)
    top = by - 10
    pts = [(sx, top), (sx - 3, top - 9), (sx + 2, top - 18), (sx - 1, top - 27)]
    pygame.draw.lines(surf, _shade(trunk, -28), False, pts, 5)
    pygame.draw.lines(surf, trunk, False, pts, 3)
    # Bold layered pine tiers — wider, flatter discs.
    for (cx, cy), tw in (((sx - 9, top - 14), 12), ((sx + 9, top - 19), 10),
                         ((sx - 6, top - 24), 9), ((sx + 2, top - 30), 8)):
        pygame.draw.ellipse(surf, f['dark'], (cx - tw, cy - 4, tw * 2, 8))
        pygame.draw.ellipse(surf, f['mid'], (cx - tw + 2, cy - 3, tw * 2 - 4, 6))
        pygame.draw.ellipse(surf, f['top'], (cx - tw + 4, cy - 3, tw - 2, 3))


def fam_market_flower(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 21, 12, _terracotta(n), night=n)
    top = by - 12
    pygame.draw.ellipse(surf, f['dark'], (sx - 14, top - 16, 28, 20))
    pygame.draw.ellipse(surf, f['mid'], (sx - 12, top - 15, 24, 17))
    pygame.draw.ellipse(surf, f['top'], (sx - 10, top - 15, 15, 7))
    # Azalea — denser, brighter red/white clusters at the crown.
    rng = random.Random(23)
    cols = ((232, 60, 70), (250, 90, 110), (245, 220, 225))
    for _ in range(12):
        a = rng.uniform(-0.2, math.pi + 0.2)
        rr = rng.uniform(3, 12)
        bx = sx + int(math.cos(a) * rr)
        byp = top - 8 - int(math.sin(a) * rr * 0.6)
        c = _bloom(rng.choice(cols), pal)
        pygame.draw.circle(surf, _shade(c, -45), (bx, byp), 2)
        pygame.draw.circle(surf, c, (bx, byp), 1)


def fam_market_vine(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 17, 13, _terracotta(n), night=n)
    top = by - 13
    # A fuller, spilling vine over the right lip with leaf fans + flowers.
    stem = [(sx + 7, top - 1)]
    for i in range(1, 14):
        t = i / 13
        px = sx + 7 + int(math.sin(t * 2.6) * 4) + int(t * 3)
        py = top - 1 + int(t * 24)
        stem.append((px, py))
    pygame.draw.lines(surf, f['dark'], False, stem, 2)
    for i, (px, py) in enumerate(stem):
        if i % 2 == 1:
            for side in (-1, 1):
                pygame.draw.polygon(surf, f['mid'],
                                    [(px, py), (px + side * 4, py - 2),
                                     (px + side * 3, py + 2)])
                pygame.draw.line(surf, f['top'], (px, py),
                                 (px + side * 3, py), 1)
    for (px, py) in (stem[5], stem[10], stem[13]):
        c = _bloom((250, 140, 170), pal)
        pygame.draw.circle(surf, _shade(c, -40), (px, py), 2)
        pygame.draw.circle(surf, c, (px, py), 1)


# ── Family C: CELADON SERENE — soft, naturalistic, celadon-green glaze ────────

def fam_serene_bamboo(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 18, 12, _celadon(n), night=n)
    cane = _mix((140, 175, 105), (60, 74, 100), 0.34 * n)
    top = by - 12
    # Sparse, elegant — three tall slim canes with airy sprays.
    for dx, htop, lean in ((-3, 32, -1), (1, 38, 1), (5, 29, 2)):
        cx = sx + dx
        ct = top - htop
        pygame.draw.line(surf, cane, (cx, top), (cx + lean, ct), 2)
        for s in (1, 2, 3):
            jy = top - htop * s // 4
            jx = cx + int(lean * (s / 4))
            pygame.draw.line(surf, _shade(cane, -36), (jx - 1, jy),
                             (jx + 1, jy), 2)
            _leaf_spray(surf, jx, jy, 1.4, 9, f['mid'], n=2, spread=0.6)
            _leaf_spray(surf, jx, jy, 1.9, 8, f['top'], n=1)


def fam_serene_bonsai(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 24, 8, _celadon(n), night=n)
    trunk = _mix((104, 78, 54), (58, 62, 92), 0.32 * n)
    top = by - 8
    # A windswept literati trunk — long lean, foliage only at the tip + one pad.
    pts = [(sx - 1, top), (sx + 4, top - 12), (sx + 9, top - 20),
           (sx + 7, top - 30)]
    pygame.draw.lines(surf, _shade(trunk, -26), False, pts, 4)
    pygame.draw.lines(surf, trunk, False, pts, 2)
    for (cx, cy), tw, th in (((sx + 8, top - 31), 9, 4), ((sx + 14, top - 24), 7, 3),
                             ((sx - 2, top - 17), 6, 3)):
        pygame.draw.ellipse(surf, f['dark'], (cx - tw, cy - th, tw * 2, th * 2))
        pygame.draw.ellipse(surf, f['mid'],
                            (cx - tw + 1, cy - th + 1, tw * 2 - 3, th * 2 - 2))
        pygame.draw.ellipse(surf, f['top'], (cx - tw + 2, cy - th, tw - 1, th))


def fam_serene_flower(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 20, 10, _celadon(n), night=n)
    top = by - 10
    # A looser, lobed mound (two overlapping domes) rather than one ellipse.
    for cx, cy, rw, rh in ((sx - 5, top - 11, 9, 8), (sx + 5, top - 13, 9, 8),
                           (sx, top - 16, 8, 7)):
        pygame.draw.ellipse(surf, f['dark'], (cx - rw, cy - rh, rw * 2, rh * 2))
        pygame.draw.ellipse(surf, f['mid'],
                            (cx - rw + 1, cy - rh + 1, rw * 2 - 3, rh * 2 - 2))
    # Soft pastel blooms scattered naturally.
    rng = random.Random(31)
    cols = ((244, 190, 205), (250, 220, 225), (236, 150, 175))
    for _ in range(8):
        a = rng.uniform(0, math.tau)
        rr = rng.uniform(2, 10)
        bx = sx + int(math.cos(a) * rr)
        byp = top - 13 + int(math.sin(a) * rr * 0.7)
        c = _bloom(rng.choice(cols), pal)
        pygame.draw.circle(surf, c, (bx, byp), 1)


def fam_serene_vine(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 16, 11, _celadon(n), night=n)
    top = by - 11
    # A fern/palm fan tuft + a short trailing tendril.
    base_x, base_y = sx, top - 1
    for k in range(7):
        a = math.radians(20 + k * 23)
        length = 13 - abs(k - 3) * 2
        ex = base_x + int(math.cos(a) * length)
        ey = base_y - int(math.sin(a) * length)
        col = f['mid'] if k % 2 else f['dark']
        pygame.draw.line(surf, col, (base_x, base_y), (ex, ey), 2)
        # Pinnae along the frond.
        for t in (0.45, 0.7):
            mx = base_x + int(math.cos(a) * length * t)
            my = base_y - int(math.sin(a) * length * t)
            pygame.draw.line(surf, f['top'], (mx, my),
                             (mx + 2, my - 2), 1)
    # A short trailing tendril over the lip.
    pygame.draw.lines(surf, f['dark'], False,
                      [(sx - 6, top - 1), (sx - 8, top + 5), (sx - 6, top + 11)], 2)


# ── Family D: GLAZED PARADE — every pot a different glaze, leafy + lush ────────

def fam_parade_bamboo(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 20, 13, _mix((60, 130, 150), (62, 70, 100), 0.34 * n),
               rim=True, night=n)
    cane = _mix((130, 175, 90), (60, 74, 100), 0.34 * n)
    cane_dk = _shade(cane, -40)
    top = by - 13
    # Dense clump — five canes, lush leaf mass at top.
    for dx, htop in ((-6, 26), (-2, 33), (2, 36), (6, 30), (9, 22)):
        cx = sx + dx
        segs = 4
        for s in range(segs):
            y0 = top - htop * s // segs
            y1 = top - htop * (s + 1) // segs
            pygame.draw.line(surf, cane, (cx, y0), (cx, y1), 2)
            pygame.draw.line(surf, cane_dk, (cx - 1, y1), (cx + 1, y1), 1)
    # A leafy canopy mass over the cane tops.
    for cx, cy, rw in ((sx - 3, top - 32, 10), (sx + 5, top - 30, 9),
                       (sx, top - 26, 8)):
        pygame.draw.ellipse(surf, f['dark'], (cx - rw, cy - 5, rw * 2, 10))
        pygame.draw.ellipse(surf, f['mid'], (cx - rw + 2, cy - 4, rw * 2 - 4, 7))
    for cx in range(sx - 8, sx + 9, 3):
        _leaf_spray(surf, cx, top - 28, 1.5, 6, f['top'], n=2, spread=0.8)


def fam_parade_bonsai(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 24, 9, _mix((150, 70, 60), (62, 70, 100), 0.34 * n),
               night=n)
    trunk = _mix((100, 72, 46), (58, 62, 92), 0.30 * n)
    top = by - 9
    # A twin-trunk bonsai (mother-and-son style).
    for base_dx, lean, h in ((-2, -4, 26), (3, 5, 20)):
        pts = [(sx + base_dx, top), (sx + base_dx + lean // 2, top - h // 2),
               (sx + base_dx + lean, top - h)]
        pygame.draw.lines(surf, _shade(trunk, -26), False, pts, 4)
        pygame.draw.lines(surf, trunk, False, pts, 2)
    for (cx, cy), tw in (((sx - 8, top - 22), 11), ((sx + 9, top - 17), 9),
                         ((sx + 1, top - 28), 9), ((sx - 3, top - 26), 7)):
        pygame.draw.ellipse(surf, f['dark'], (cx - tw, cy - 4, tw * 2, 9))
        pygame.draw.ellipse(surf, f['mid'], (cx - tw + 2, cy - 3, tw * 2 - 4, 6))
        pygame.draw.ellipse(surf, f['top'], (cx - tw + 4, cy - 3, tw - 2, 3))


def fam_parade_flower(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 22, 11, _mix((200, 170, 70), (62, 70, 100), 0.34 * n),
               night=n)
    top = by - 11
    # A full, rounded peony bush — generous bloom load, three colours.
    pygame.draw.ellipse(surf, f['dark'], (sx - 15, top - 19, 30, 23))
    pygame.draw.ellipse(surf, f['mid'], (sx - 13, top - 18, 26, 20))
    rng = random.Random(43)
    cols = ((236, 110, 160), (250, 80, 100), (250, 240, 245), (240, 170, 90))
    for _ in range(16):
        a = rng.uniform(-0.3, math.pi + 0.3)
        rr = rng.uniform(2, 13)
        bx = sx + int(math.cos(a) * rr)
        byp = top - 9 - int(math.sin(a) * rr * 0.65)
        c = _bloom(rng.choice(cols), pal)
        pygame.draw.circle(surf, _shade(c, -45), (bx, byp), 2)
        pygame.draw.circle(surf, c, (bx, byp), 1)
        if rng.random() < 0.4:
            pygame.draw.circle(surf, _bloom((255, 235, 160), pal), (bx, byp), 0)


def fam_parade_vine(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 18, 12, _mix((120, 90, 160), (62, 70, 100), 0.34 * n),
               night=n)
    top = by - 12
    # Two cascading strands from both lips — the lushest vine.
    for side, x0 in ((-1, sx - 7), (1, sx + 7)):
        stem = [(x0, top - 1)]
        for i in range(1, 13):
            t = i / 12
            px = x0 + side * (int(math.sin(t * 2.4) * 3) + int(t * 4))
            py = top - 1 + int(t * 23)
            stem.append((px, py))
        pygame.draw.lines(surf, f['dark'], False, stem, 2)
        for i, (px, py) in enumerate(stem):
            if i % 2 == 0 and i:
                pygame.draw.polygon(surf, f['mid'],
                                    [(px, py), (px + side * 4, py - 2),
                                     (px + side * 3, py + 2)])
                pygame.draw.line(surf, f['top'], (px, py), (px + side * 3, py), 1)
        for idx in (4, 9):
            px, py = stem[idx]
            c = _bloom((250, 150, 180), pal)
            pygame.draw.circle(surf, c, (px, py), 1)


# ── Family E: INK-WASH MINIMAL — restrained, dark silhouettes, one accent ─────

def fam_ink_bamboo(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 17, 11, _mix((90, 96, 104), (62, 70, 100), 0.30 * n),
               motif=(40, 44, 52), night=n)
    cane = _mix((90, 120, 70), (52, 66, 92), 0.36 * n)
    top = by - 11
    # Calligraphic — few strokes, strong negative space.
    for dx, htop, lean in ((-2, 34, -2), (3, 40, 2)):
        cx = sx + dx
        ct = top - htop
        pygame.draw.line(surf, _shade(cane, -30), (cx, top), (cx + lean, ct), 3)
        pygame.draw.line(surf, cane, (cx, top), (cx + lean, ct), 1)
        for s in (1, 2, 3):
            jy = top - htop * s // 4
            jx = cx + int(lean * (s / 4))
            _leaf_spray(surf, jx, jy, 1.6, 11, f['dark'], n=2, spread=0.4)
            _leaf_spray(surf, jx, jy, 1.4, 9, f['mid'], n=1)


def fam_ink_bonsai(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 22, 7, _mix((86, 92, 100), (62, 70, 100), 0.30 * n),
               motif=(40, 44, 52), night=n)
    trunk = _mix((80, 60, 42), (54, 58, 86), 0.34 * n)
    top = by - 7
    # A stark gnarled trunk with two cloud pads — ink-painting pine.
    pts = [(sx, top), (sx - 4, top - 10), (sx + 3, top - 17),
           (sx - 2, top - 26), (sx + 3, top - 31)]
    pygame.draw.lines(surf, _shade(trunk, -28), False, pts, 4)
    pygame.draw.lines(surf, trunk, False, pts, 2)
    for (cx, cy), tw, th in (((sx - 9, top - 19), 10, 3), ((sx + 8, top - 28), 9, 3)):
        pygame.draw.ellipse(surf, f['dark'], (cx - tw, cy - th, tw * 2, th * 2))
        pygame.draw.ellipse(surf, f['mid'],
                            (cx - tw + 2, cy - th + 1, tw * 2 - 4, th * 2 - 2))
    # A single bright accent — one red seed cone.
    pygame.draw.circle(surf, _bloom((220, 70, 60), pal), (sx + 8, top - 28), 1)


def fam_ink_flower(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 19, 10, _mix((92, 98, 106), (62, 70, 100), 0.30 * n),
               motif=(40, 44, 52), night=n)
    top = by - 10
    # A tight dark mound — restrained, with just a few white plum blossoms.
    pygame.draw.ellipse(surf, f['dark'], (sx - 11, top - 15, 22, 18))
    pygame.draw.ellipse(surf, f['mid'], (sx - 9, top - 14, 18, 15))
    pygame.draw.ellipse(surf, f['top'], (sx - 7, top - 14, 11, 6))
    # Sparse white/pink plum blossoms on bare twig tips above the mound.
    rng = random.Random(53)
    for tx, ty in ((sx - 6, top - 18), (sx + 4, top - 20), (sx, top - 22),
                   (sx + 8, top - 16)):
        pygame.draw.line(surf, f['dark'], (tx, top - 12), (tx, ty), 1)
        c = _bloom((250, 230, 235), pal)
        pygame.draw.circle(surf, c, (tx, ty), 1)
        pygame.draw.circle(surf, _bloom((230, 120, 140), pal), (tx + 1, ty), 0)


def fam_ink_vine(surf, sx, by, pal):
    f = _fol(pal)
    n = _nightf(pal)
    _pot_glaze(surf, sx, by, 15, 11, _mix((88, 94, 102), (62, 70, 100), 0.30 * n),
               motif=(40, 44, 52), night=n)
    top = by - 11
    # A single elegant trailing stroke with sparse leaves — wabi minimal.
    stem = [(sx + 6, top - 1)]
    for i in range(1, 14):
        t = i / 13
        px = sx + 6 + int(math.sin(t * 1.8) * 5) + int(t * 2)
        py = top - 1 + int(t * 26)
        stem.append((px, py))
    pygame.draw.lines(surf, _shade(f['dark'], -10), False, stem, 2)
    for i in (3, 6, 9, 12):
        px, py = stem[i]
        side = 1 if i % 6 else -1
        pygame.draw.polygon(surf, f['mid'],
                            [(px, py), (px + side * 4, py - 1),
                             (px + side * 2, py + 3)])
    px, py = stem[7]
    pygame.draw.circle(surf, _bloom((240, 210, 140), pal), (px, py), 1)


# ══════════════════════════════════════════════════════════════════════════
# Sheet layout
# ══════════════════════════════════════════════════════════════════════════

FAMILIES = [
    ("Scholar's Courtyard  (blue-and-white porcelain, refined cloud-tiers)",
     (fam_scholar_bamboo, fam_scholar_bonsai, fam_scholar_flower, fam_scholar_vine)),
    ("Temple Market  (terracotta + festive azalea, bold market read)",
     (fam_market_bamboo, fam_market_bonsai, fam_market_flower, fam_market_vine)),
    ("Celadon Serene  (soft celadon glaze, naturalistic, literati)",
     (fam_serene_bamboo, fam_serene_bonsai, fam_serene_flower, fam_serene_vine)),
    ("Glazed Parade  (mixed glazes, lush full planting)",
     (fam_parade_bamboo, fam_parade_bonsai, fam_parade_flower, fam_parade_vine)),
    ("Ink-Wash Minimal  (calligraphic silhouettes, single accent)",
     (fam_ink_bamboo, fam_ink_bonsai, fam_ink_flower, fam_ink_vine)),
]


def _deck_strip(surf, x, y, w, h, pal):
    """A neutral sidewalk deck strip the plants sit on, tinted per phase."""
    night = _nightf(pal)
    base = _mix((182, 168, 146), (66, 74, 104), 0.42 * night)
    pygame.draw.rect(surf, base, (x, y, w, h))
    pygame.draw.rect(surf, _shade(base, 14), (x, y, w, 2))
    pygame.draw.rect(surf, _shade(base, -22), (x, y + h - 3, w, 3))
    # Faint paving joints.
    for jx in range(x + 24, x + w, 48):
        pygame.draw.line(surf, _shade(base, -16), (jx, y + 2), (jx, y + h - 2), 1)


def _bg(pal):
    return _mix(pal['sky_top'], (255, 255, 255), 0.15)


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 13, bold=True)
    small = pygame.font.SysFont("dejavusans", 10)

    cell_w = 320          # per phase (day | night) within a family row
    cell_h = 132
    plant_slots = 4
    slot_w = cell_w // plant_slots
    deck_h = 16
    label_h = 22
    gap = 8
    margin = 14

    rows = len(FAMILIES)
    body_w = margin * 2 + cell_w * 2 + gap
    sheet_w = max(body_w, 720)   # headroom so the title isn't clipped
    sheet_h = margin * 2 + label_h + rows * (cell_h + label_h + gap) + 30

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((28, 28, 34))

    title = font.render(
        "PLANT FAMILY UPGRADE — Chinese-garden / temple-market planting   "
        "(DAY | NIGHT)   round 1", True, (236, 236, 240))
    sheet.blit(title, (margin, 10))

    y = margin + label_h + 8
    for name, fns in FAMILIES:
        lbl = font.render(name, True, (226, 222, 210))
        sheet.blit(lbl, (margin, y - 18))
        for ci, pal in enumerate((PAL_DAY, PAL_NIGHT)):
            cx = margin + ci * (cell_w + gap)
            cell = pygame.Surface((cell_w, cell_h))
            cell.fill(_bg(pal))
            deck_y = cell_h - deck_h
            _deck_strip(cell, 0, deck_y, cell_w, deck_h, pal)
            by = deck_y + 2
            names = ("bamboo", "bonsai", "flower", "vine")
            for si, fn in enumerate(fns):
                sx = si * slot_w + slot_w // 2
                fn(cell, sx, by, pal)
                tag = small.render(names[si], True,
                                   (40, 40, 46) if ci == 0 else (170, 175, 195))
                cell.blit(tag, (sx - tag.get_width() // 2, cell_h - 11))
            pygame.draw.rect(cell, (70, 70, 80), cell.get_rect(), 1)
            sheet.blit(cell, (cx, y))
            phase = small.render("DAY" if ci == 0 else "NIGHT", True,
                                 (200, 200, 205))
            sheet.blit(phase, (cx + 4, y + 2))
        y += cell_h + label_h + gap

    foot = small.render(
        "Each cell shows one family's full SET (pot+bamboo / bonsai-pine / "
        "flowering shrub / cascading-vine) at ~10-38px deck scale.",
        True, (150, 150, 158))
    sheet.blit(foot, (margin, sheet_h - 22))

    out = "/home/user/skybit/docs/foreground_redesign/plants/round_1.png"
    pygame.image.save(sheet, out)
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
