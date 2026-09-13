"""Refine the 'gust ribbon' geyser direction into clean cartoon wind swooshes.
Renders a few takes as looping GIFs (+ posters) under
``docs/screenshots/geyser_gust/``:

    python tools/sketch_geyser_gust.py

Throwaway design sketch. W4's ribbons looked odd because they were built from
overlapping soft blobs (lumpy). These use proper tapered calligraphic
strokes: a curved centreline with a thin→thick→thin width profile, drawn as a
filled polygon and lightly blurred for clean soft edges — translucent,
cool/white, fanning and curling as they rise. Wind, not blobs.
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

import pygame
from PIL import Image

from game.config import W, H, GROUND_Y
from tools.sketch_geyser_cone import _backdrop, _blur, PERIOD, FPS, N_FRAMES

OUT_DIR = os.path.join(ROOT, "docs", "screenshots", "geyser_gust")

AIR = (228, 240, 250)
AIRW = (255, 250, 240)
LEAF = (206, 150, 66)


def _ph(t):
    return 2 * math.pi * t / PERIOD


def _stroke_pts(x, base_y, hcol, p, i, n, ph, length_f=0.36, fan=9.0):
    """Curved centreline + half-width profile for one rising swoosh."""
    yc = base_y - (0.12 + 0.76 * p) * hcol
    length = hcol * length_f
    side = (i - (n - 1) / 2.0)
    segs = 14
    pts, ws = [], []
    for k in range(segs + 1):
        u = k / segs                         # 0 tail (low) → 1 head (high)
        yy = yc + (0.5 - u) * length
        g = max(0.0, (base_y - yy) / hcol)   # global height 0..1
        curl = math.sin(g * 3.2 - ph * 1.6 + i * 1.7) * (7 + 12 * g)
        outw = side * fan * (0.5 + g)        # fan outward as it rises
        pts.append((x + outw + curl, yy))
        ws.append(math.sin(math.pi * u) ** 0.85)  # 0→1→0 lens taper
    return pts, ws


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
    pygame.draw.polygon(s, (*color, int(alpha)),
                        [(px - minx, py - miny) for px, py in poly])
    if blur:
        s = _blur(s, blur)
    scene.blit(s, (minx, miny))


def _leaf(scene, x, y, ang, scale, alpha):
    w, h = int(11 * scale), int(7 * scale)
    if w < 2 or h < 2:
        return
    s = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (*LEAF, int(alpha)), (1, 1, w, h))
    s = pygame.transform.rotate(s, math.degrees(ang))
    scene.blit(s, (int(x - s.get_width() / 2), int(y - s.get_height() / 2)))


def _life(p):
    return math.sin(math.pi * p) ** 0.7


# ── G1: elegant thin swooshes ────────────────────────────────────────────────
def render_g1(scene, streams, t):
    ph = _ph(t)
    for (x, by, h, inten) in streams:
        n = 3
        for i in range(n):
            p = ((t / PERIOD) + i / n) % 1.0
            pts, ws = _stroke_pts(x, by, h, p, i, n, ph)
            _swoosh(scene, pts, ws, 5.0, AIR if i % 2 else AIRW,
                    105 * _life(p) * inten, blur=2)


# ── G2: layered translucent sheets ───────────────────────────────────────────
def render_g2(scene, streams, t):
    ph = _ph(t)
    for (x, by, h, inten) in streams:
        # faint wide background sheets
        for i in range(2):
            p = ((t / PERIOD) + i / 2 + 0.15) % 1.0
            pts, ws = _stroke_pts(x, by, h, p, i, 2, ph, length_f=0.5, fan=13)
            _swoosh(scene, pts, ws, 13.0, AIR, 45 * _life(p) * inten, blur=3)
        # crisper foreground swooshes
        n = 3
        for i in range(n):
            p = ((t / PERIOD) + i / n) % 1.0
            pts, ws = _stroke_pts(x, by, h, p, i, n, ph, fan=10)
            _swoosh(scene, pts, ws, 7.0, AIRW if i == 1 else AIR,
                    90 * _life(p) * inten, blur=2)


# ── G3: swooshes carrying leaves ─────────────────────────────────────────────
def render_g3(scene, streams, t):
    ph = _ph(t)
    for (x, by, h, inten) in streams:
        n = 3
        for i in range(n):
            p = ((t / PERIOD) + i / n) % 1.0
            pts, ws = _stroke_pts(x, by, h, p, i, n, ph)
            _swoosh(scene, pts, ws, 4.5, AIR, 90 * _life(p) * inten, blur=2)
        for li in range(3):
            p = ((t / PERIOD) * 0.95 + li / 3.0) % 1.0
            yy = by - (0.1 + 0.82 * p) * h
            xx = x + math.sin(p * 4 + li * 2) * (10 + 22 * p)
            _leaf(scene, xx, yy, p * 8 + li, 1.1 - 0.4 * p,
                  225 * _life(p) * inten)


# ── G4: brisk multi-swoosh (more, thinner, faster) ───────────────────────────
def render_g4(scene, streams, t):
    ph = _ph(t)
    for (x, by, h, inten) in streams:
        n = 5
        for i in range(n):
            p = ((t / PERIOD) * 1.25 + i / n) % 1.0
            pts, ws = _stroke_pts(x, by, h, p, i, n, ph, length_f=0.30, fan=11)
            _swoosh(scene, pts, ws, 3.6, AIR if i % 2 else AIRW,
                    95 * _life(p) * inten, blur=1)


VARIANTS = [
    ("g1_elegant", "G1 - Elegant swooshes", render_g1),
    ("g2_sheets", "G2 - Layered sheets", render_g2),
    ("g3_leaves", "G3 - Swooshes + leaves", render_g3),
    ("g4_brisk", "G4 - Brisk multi-swoosh", render_g4),
]

STREAMS = [(120, GROUND_Y, 232, 1.0), (252, GROUND_Y, 168, 0.85)]


def _vent(scene, x):
    vw = 30
    v = pygame.Surface((vw + 6, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(v, (70, 56, 46, 200), (3, 3, vw, 8))
    pygame.draw.ellipse(v, (40, 30, 24, 230), (3, 5, vw, 5))
    scene.blit(v, (int(x) - vw // 2 - 3, GROUND_Y - 7))


def main():
    pygame.init()
    pygame.display.set_mode((W, H))
    os.makedirs(OUT_DIR, exist_ok=True)
    base = _backdrop()
    font = pygame.font.Font(None, 26)
    panels = []
    for slug, label, fn in VARIANTS:
        frames = []
        for i in range(N_FRAMES):
            t = i / FPS
            scene = base.copy()
            for (x, by, h, inten) in STREAMS:
                _vent(scene, x)
            fn(scene, STREAMS, t)
            sh = font.render(label, True, (0, 0, 0)); scene.blit(sh, (11, 11))
            tx = font.render(label, True, (255, 255, 255)); scene.blit(tx, (10, 10))
            frames.append(Image.frombytes(
                "RGB", (W, H), pygame.image.tostring(scene, "RGB")))
        frames[0].save(os.path.join(OUT_DIR, slug + ".gif"), save_all=True,
                       append_images=frames[1:], duration=int(1000 / FPS),
                       loop=0, optimize=True)
        mid = frames[len(frames) // 2]
        mid.save(os.path.join(OUT_DIR, slug + ".png"))
        panels.append(mid)
        print("wrote", slug)
    gap = 8
    sheet = Image.new("RGB", (W * len(panels) + gap * (len(panels) - 1), H),
                      (18, 18, 24))
    xo = 0
    for p in panels:
        sheet.paste(p, (xo, 0)); xo += W + gap
    sheet.save(os.path.join(OUT_DIR, "comparison.png"))
    print("wrote comparison")


if __name__ == "__main__":
    main()
