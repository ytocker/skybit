"""Geyser as a WINDY rising-air stream (not fire). Renders 5 variants as
looping GIFs (+ poster PNGs) under ``docs/screenshots/geyser_wind/``:

    python tools/sketch_geyser_wind.py

Throwaway design sketch. The previous cone variants read as fire because of
the warm additive glow + white-hot core. Wind is the opposite: **translucent,
cool/white, motion-driven** — flowing streak lines, swirling eddies, and bits
of debris lifted upward. Everything here uses NORMAL alpha blending (airy
see-through strokes), never additive glow.
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

from game.config import W, H, GROUND_Y
from tools.sketch_geyser_cone import _backdrop, _blur, PERIOD, FPS, N_FRAMES

OUT_DIR = os.path.join(ROOT, "docs", "screenshots", "geyser_wind")

AIR = (230, 241, 250)     # cool airy white — the wind itself
AIRW = (255, 250, 240)    # faint warm-white accent (it is *warm* air)
LEAF = (206, 150, 66)     # lifted autumn leaf
DUST = (245, 238, 222)

_brush_cache: dict = {}


def _brush(rad, color, alpha):
    rad = max(1, int(rad))
    alpha = int(max(0, min(255, alpha)))
    if alpha <= 3:
        return None
    color = (int(color[0]) // 16 * 16, int(color[1]) // 16 * 16,
             int(color[2]) // 16 * 16)
    aq = max(12, alpha // 12 * 12)
    key = (rad, color, aq)
    b = _brush_cache.get(key)
    if b is None:
        d = rad * 2 + 2
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, 255), (d // 2, d // 2),
                           max(1, int(rad * 0.62)))
        s = _blur(s, 3 if rad >= 6 else 2)
        s.fill((*color, aq), special_flags=pygame.BLEND_RGBA_MULT)
        _brush_cache[key] = s
        b = s
    return b


def _stamp(scene, x, y, rad, color, alpha):
    b = _brush(rad, color, alpha)
    if b is None:
        return
    scene.blit(b, (int(x - b.get_width() / 2), int(y - b.get_height() / 2)))


def _ph(t):
    return 2 * math.pi * t / PERIOD


# ── W1: flowing wind streaks (speed lines of rising air) ─────────────────────
def render_w1(scene, streams, t):
    ph = _ph(t)
    for (x, by, h, inten) in streams:
        for k in range(6):
            spread = (k - 2.5) * 7
            for j in range(0, int(h), 4):
                up = j / h
                flow = math.sin(up * 3.0 - ph * 1.8 + k) * (6 + 12 * up)
                xx = x + spread * (0.5 + up) + flow
                dash = 0.5 + 0.5 * math.sin(up * 24 - ph * 6 + k * 2.0)
                a = 120 * (1.0 - up) ** 0.8 * dash * inten
                col = AIRW if k % 3 == 0 else AIR
                _stamp(scene, xx, by - j, 2.4 * (1.0 - 0.4 * up), col, a)


# ── W2: swirling eddies (rising curls of air) ────────────────────────────────
def _curl(scene, cx, cy, scale, color, alpha, spin):
    pts = 16
    for i in range(pts):
        u = i / (pts - 1)
        ang = spin + u * math.pi * 1.7
        r = scale * (3 + 10 * u)
        x = cx + math.cos(ang) * r
        y = cy + math.sin(ang) * r * 0.85
        _stamp(scene, x, y, 2.3 * (0.6 + u), color, alpha * (0.25 + 0.75 * u))


def render_w2(scene, streams, t):
    ph = _ph(t)
    for (x, by, h, inten) in streams:
        n = 4
        for i in range(n):
            p = ((t / PERIOD) + i / n) % 1.0
            y = by - 12 - p * (h - 12)
            cx = x + math.sin(p * 3.0 + i) * 16
            scale = (1.1 - 0.5 * p)
            a = 150 * (1.0 - p) * inten
            _curl(scene, cx, y, scale, AIR if i % 2 else AIRW, a,
                  spin=ph * 1.5 + i * 1.3)
        # a few faint connecting streaks for cohesion
        for j in range(0, int(h), 6):
            up = j / h
            xx = x + math.sin(up * 3.4 - ph * 1.5) * (6 + 10 * up)
            _stamp(scene, xx, by - j, 1.8, AIR, 50 * (1 - up) * inten)


# ── W3: wind made visible by lifted debris (leaves + dust) ───────────────────
def _leaf(scene, x, y, ang, scale, alpha):
    w, h = int(11 * scale), int(7 * scale)
    if w < 2 or h < 2:
        return
    s = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (*LEAF, int(alpha)), (1, 1, w, h))
    pygame.draw.line(s, (120, 80, 30, int(alpha)), (1, h // 2 + 1),
                     (w, h // 2 + 1), 1)
    s = pygame.transform.rotate(s, math.degrees(ang))
    scene.blit(s, (int(x - s.get_width() / 2), int(y - s.get_height() / 2)))


def render_w3(scene, streams, t):
    ph = _ph(t)
    for (x, by, h, inten) in streams:
        # faint air streaks
        for k in range(3):
            for j in range(0, int(h), 7):
                up = j / h
                xx = x + math.sin(up * 3.0 - ph * 1.6 + k * 2) * (8 + 10 * up)
                _stamp(scene, xx, by - j, 1.8, AIR, 45 * (1 - up) * inten)
        # dust specks
        rng = np.random.RandomState(int(x) * 5 + 1)
        for d in range(16):
            off = rng.rand()
            p = ((t / PERIOD) + off) % 1.0
            y = by - p * h
            xx = x + math.sin(p * 6 + d) * (10 + 22 * p)
            _stamp(scene, xx, y, 1.5, DUST, 150 * (1 - p) * inten)
        # a couple of fluttering leaves spiralling up
        for li in range(3):
            off = (li / 3.0)
            p = ((t / PERIOD) * 0.9 + off) % 1.0
            y = by - p * h
            xx = x + math.sin(p * 5 + li * 2) * (12 + 26 * p)
            _leaf(scene, xx, y, p * 9 + li, 1.1 - 0.4 * p,
                  220 * (1 - p * 0.7) * inten)


# ── W4: broad gust ribbons (sheets of moving air) ────────────────────────────
def render_w4(scene, streams, t):
    ph = _ph(t)
    for (x, by, h, inten) in streams:
        for rb in range(2):
            off = rb * math.pi
            for j in range(0, int(h), 4):
                up = j / h
                sway = math.sin(up * 2.6 - ph * 1.6 + off) * (10 + 16 * up)
                xx = x + sway + (rb - 0.5) * 10
                width = (16 - 8 * up)
                a = 70 * (1.0 - up) ** 0.9 * inten
                _stamp(scene, xx, by - j, width, AIR, a)
                # brighter leading edge
                _stamp(scene, xx + width * 0.7, by - j, 3.5,
                       AIRW, a * 1.6)


# ── W5: heat-shimmer warp + faint wind streaks ───────────────────────────────
def _warp(scene, x, base_y, hcol, t, amp=4.0):
    w = 80
    x0 = max(0, int(x - w // 2))
    x1 = min(W, x0 + w)
    y0 = max(0, int(base_y - hcol))
    arr = pygame.surfarray.pixels3d(scene)
    region = arr[x0:x1, y0:base_y].copy()
    rows = region.shape[1]
    ph = _ph(t)
    for j in range(rows):
        frac = j / max(1, rows)
        env = math.sin(math.pi * frac) ** 0.6
        off = int(round(amp * env * math.sin(0.12 * (y0 + j) * 2.0 - ph * 2.2)))
        if off:
            arr[x0:x1, y0 + j] = np.roll(region[:, j], off, axis=0)
    del arr


def render_w5(scene, streams, t):
    ph = _ph(t)
    for (x, by, h, inten) in streams:
        _warp(scene, x, by, h, t, amp=5.0)
    for (x, by, h, inten) in streams:
        for k in range(4):
            for j in range(0, int(h), 6):
                up = j / h
                xx = x + (k - 1.5) * 8 + math.sin(up * 3.0 - ph * 1.8 + k) * (6 + 10 * up)
                dash = 0.5 + 0.5 * math.sin(up * 20 - ph * 5 + k * 2)
                _stamp(scene, xx, by - j, 1.9 * (1 - 0.3 * up), AIR,
                       70 * (1 - up) * dash * inten)


VARIANTS = [
    ("w1_streaks", "W1 - Flow streaks", render_w1),
    ("w2_swirls", "W2 - Swirling eddies", render_w2),
    ("w3_debris", "W3 - Lifted debris", render_w3),
    ("w4_ribbons", "W4 - Gust ribbons", render_w4),
    ("w5_shimmer", "W5 - Shimmer + streaks", render_w5),
]

STREAMS = [(120, GROUND_Y, 230, 1.0), (252, GROUND_Y, 165, 0.85)]


def _vent(scene, x):
    vw = 32
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
        frames[len(frames) // 2].save(os.path.join(OUT_DIR, slug + ".png"))
        print("wrote", slug)


if __name__ == "__main__":
    main()
