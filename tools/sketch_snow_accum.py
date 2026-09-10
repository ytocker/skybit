"""Snow-accumulation design exploration for Pip during the snow squall.

The predawn squall is a TAILWIND (blows left->right), so snow plasters Pip's
rear / left-facing upper surfaces first (tail, back, nape, crown) and spreads
forward + down as it builds, eventually nearly covering him (face stays
readable). Renders 5 distinct snow styles across phases
(original -> light -> mid -> near-full) into one comparison grid:

    python tools/sketch_snow_accum.py  -> docs/screenshots/snow_accum/comparison.png

Throwaway design sketch — no game code is touched. Real-snow principles baked
in: snow only on up-facing/windward surfaces; bright white tops with cool
blue/purple shadowed undersides; bulkier silhouette + a slight windward
cornice; deterministic (never shimmers).
"""
from __future__ import annotations

import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import numpy as np
import pygame
from PIL import Image

from game import parrot, biome
from game.draw import make_gradient_surface

OUT = os.path.join(ROOT, "docs", "screenshots", "snow_accum")
SCALE = 6
MAXD = 15.0                       # max snow depth in sprite px (rear, full load)
PHASES = [("original", 0.0), ("light", 0.30), ("mid", 0.60), ("near-full", 0.92)]

WHITE = (255, 255, 255)
OFF = (236, 244, 252)
BLUE = (188, 206, 230)           # cool shadowed underside
SHADOW = (150, 168, 198)         # deep crevice blue/purple


def _sprite():
    return parrot._get_frames()[2]     # level-wing frame, outlined


def _topline(big):
    """First opaque row per column (the top silhouette) at big scale."""
    a = pygame.surfarray.array_alpha(big)        # (W, H)
    mask = a > 50
    has = mask.any(axis=1)
    top = np.where(has, mask.argmax(axis=1), -1)
    return top, has


def _cov(x_frac, load):
    """Per-column coverage 0..1 — REAR-FIRST: each column has a load threshold
    that's ~0 at the rear (left) and high at the front, so snow starts on the
    tail/back and only creeps onto the head/front as the storm builds."""
    thr = 0.55 * x_frac
    return 0.0 if load <= thr else min(1.0, (load - thr) / (1.0 - thr))


def _shade(t):
    """Colour from snow-surface (t=0, bright) to underside (t=1, cool blue)."""
    if t < 0.16:
        return WHITE
    if t < 0.45:
        return OFF
    if t < 0.78:
        return BLUE
    return SHADOW


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ── shared column scaffold: gives each style the per-column snow band ────────
def _columns(big, load, cornice=0.0, lump=0.0):
    """Yield (x, y_top, y_bot, depth) snow bands per column.

    Round-2 scaffold: (a) the rear/left end TAPERS to a point over a slope zone
    (no sharp vertical wall at the tail); (b) snow piles INWARD via a smooth
    depth bulge over the mid-body, not just a thin outline rim. cornice lifts
    the windward top edge; lump adds a bumpy crest."""
    top, has = _topline(big)
    W = big.get_width()
    xs = np.nonzero(has)[0]
    if len(xs) == 0:
        return []
    x_min = int(xs[0])                                      # tail tip (rear end)
    taper_w = 13.0 * SCALE                                  # rear slope length
    out = []
    for x in range(W):
        if not has[x]:
            continue
        xf = x / W
        cov = _cov(xf, load)
        if cov <= 0.0:
            continue
        rear = 1.0 - xf
        bulge = math.exp(-((xf - 0.40) / 0.26) ** 2)        # inward hump over the back
        d = MAXD * SCALE * cov * (0.50 + 0.45 * rear + 0.45 * bulge)
        if xf > 0.60:                                       # crown: thin cap so
            d = min(d, 7.0 * SCALE)                         # eyes/glasses stay clear
        te = _smooth((x - x_min) / taper_w)                 # rear-end slope 0→1
        d *= te
        if d < 1.0:
            continue
        yt = top[x]
        over = cornice * rear * SCALE * te                  # taper the overhang too
        if lump:
            over += lump * SCALE * (0.5 + 0.5 * math.sin(x * 0.10)) * (0.4 + rear) * te
        nb = (math.sin(x * 0.21) + math.sin(x * 0.057)) * 0.25 + 0.5
        y1 = yt + d + (nb - 0.5) * 2.4 * SCALE              # irregular settled edge
        out.append((x, yt - over, y1, y1 - (yt - over)))
    return out


def _stamp_soft(layer, x, y, r, color, alpha):
    d = max(2, int(r * 2))
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color, alpha), (d // 2, d // 2), max(1, d // 2 - 1))
    layer.blit(s, (int(x - d / 2), int(y - d / 2)))


def blur(s, downs):
    w, h = s.get_size()
    if w < downs * 2 or h < downs * 2:
        return s
    sm = pygame.transform.smoothscale(s, (w // downs, h // downs))
    return pygame.transform.smoothscale(sm, (w, h))


def _crest(layer, x, y0, d):
    """Thin bright highlight along the very top of the snow — catches light,
    gives the pile volume."""
    pygame.draw.line(layer, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.18)), 1)


# ── W1: soft inward drift (overlapping soft discs, deep inward fill) ──────────
def snow_w1(layer, big, load):
    for x, y0, y1, d in _columns(big, load, cornice=1.2):
        n = max(1, int(d / (2.0 * SCALE) * 3) + 1)
        for i in range(n + 1):
            t = i / max(1, n)
            _stamp_soft(layer, x, y0 + (y1 - y0) * t, 2.1 * SCALE, _shade(t), 215)
    return blur(layer, 2)


# ── W2: sculpted blanket (smooth centre-heavy fill, bright crest, blue under) ─
def snow_w2(layer, big, load):
    for x, y0, y1, d in _columns(big, load, cornice=1.6):
        pygame.draw.line(layer, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        _crest(layer, x, y0, d)
        pygame.draw.line(layer, (*BLUE, 255), (x, int(y1 - d * 0.26)), (x, int(y1)), 1)
    return blur(layer, 1)


# ── W3: windswept cornice + taper (overhang on the back, streaks, sloped tail)
def snow_w3(layer, big, load):
    for x, y0, y1, d in _columns(big, load, cornice=3.0):
        pygame.draw.line(layer, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        _crest(layer, x, y0, d)
        pygame.draw.line(layer, (*SHADOW, 255), (x, int(y1 - d * 0.2)), (x, int(y1)), 1)
        if (x % (3 * SCALE)) < SCALE and d > 3 * SCALE:    # faint wind streak
            yy = int(y0 + d * 0.5)
            pygame.draw.line(layer, (*WHITE, 110), (x, yy), (x + 2 * SCALE, yy - SCALE), 1)
    return blur(layer, 1)


# ── W4: frosted granular + sparkle (granular inward fill + glints) ────────────
def snow_w4(layer, big, load):
    for x, y0, y1, d in _columns(big, load, cornice=1.0):
        pygame.draw.line(layer, (*OFF, 245), (x, int(y0)), (x, int(y1)), 1)
        _crest(layer, x, y0, d)
        pygame.draw.line(layer, (*BLUE, 255), (x, int(y1 - d * 0.28)), (x, int(y1)), 1)
        h = (math.sin(x * 91.7) * 4373.1) % 1.0
        if h > 0.74 and d > 1.5 * SCALE:                    # granular speck
            _stamp_soft(layer, x, int(y0 + d * h), 1.4 * SCALE, WHITE, 255)
        g = (math.sin(x * 12.99) * 4375.5) % 1.0
        if g > 0.93:                                        # sparkle glint
            sx, sy = x, int(y0 + d * 0.18)
            for dx, dy in ((-SCALE, 0), (SCALE, 0), (0, -SCALE), (0, SCALE)):
                pygame.draw.line(layer, (*WHITE, 230), (sx, sy), (sx + dx, sy + dy), 1)
    return layer


# ── W5: heavy caked inward (bulky clumps toward centre, deep occlusion) ───────
def snow_w5(layer, big, load):
    for x, y0, y1, d in _columns(big, load, cornice=2.2, lump=2.8):
        pygame.draw.line(layer, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        _crest(layer, x, y0, d)
        pygame.draw.line(layer, (*SHADOW, 255), (x, int(y1 - d * 0.32)), (x, int(y1)), 1)
    return blur(layer, 2)


VARIANTS = [
    ("W1 soft inward drift", snow_w1),
    ("W2 sculpted blanket", snow_w2),
    ("W3 windswept cornice", snow_w3),
    ("W4 frosted + sparkle", snow_w4),
    ("W5 caked inward", snow_w5),
]


def _backdrop(w, h):
    pal = biome.palette_for_phase(0.85)            # predawn squall
    return make_gradient_surface(w, h, [(0.0, pal["sky_top"]), (1.0, pal["sky_bot"])])


def main():
    pygame.init(); pygame.display.set_mode((64, 64))
    os.makedirs(OUT, exist_ok=True)
    spr = _sprite()
    W, H = spr.get_size()
    bw, bh = W * SCALE, H * SCALE
    big = pygame.transform.scale(spr, (bw, bh))
    pad, gap = 12, 8
    cellw, cellh = bw + pad * 2, bh + pad * 2 + 22
    font = pygame.font.Font(None, 24); small = pygame.font.Font(None, 22)
    cols, rows = len(PHASES), len(VARIANTS)
    sheet = pygame.Surface((cellw * cols + gap * (cols - 1) + 150,
                            cellh * rows + gap * (rows - 1) + 30))
    sheet.fill((16, 18, 26))
    # column headers
    for c, (plabel, _) in enumerate(PHASES):
        t = small.render(plabel, True, (235, 235, 245))
        sheet.blit(t, (150 + c * (cellw + gap) + pad, 6))
    for r, (vname, fn) in enumerate(VARIANTS):
        ry = 30 + r * (cellh + gap)
        lbl = small.render(vname, True, (235, 235, 245))
        sheet.blit(lbl, (6, ry + cellh // 2 - 8))
        for c, (_, load) in enumerate(PHASES):
            cx = 150 + c * (cellw + gap)
            cell = pygame.Surface((cellw, cellh))
            cell.blit(_backdrop(cellw, cellh), (0, 0))
            cell.blit(big, (pad, pad + 22))
            if load > 0.0:
                layer = pygame.Surface((bw, bh), pygame.SRCALPHA)
                drawn = fn(layer, big, load)
                cell.blit(drawn, (pad, pad + 22))
            sheet.blit(cell, (cx, ry))
    path = os.path.join(OUT, "comparison_round2.png")
    pygame.image.save(sheet, path)
    print("wrote", path, sheet.get_size())


if __name__ == "__main__":
    main()
