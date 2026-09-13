"""Research-grounded WIND geyser: a few bold curved wind-lines (crescents with
curled tips) rising, expanding, evenly spaced, looping — the classic art
language for wind. Renders 5 variants as looping GIFs (+ posters +
comparison) under ``docs/screenshots/geyser_windlines/``:

    python tools/sketch_geyser_windlines.py

Throwaway design sketch. Principles applied: curved flow lines of varied
weight; the "wave" build (lines rise at a constant rate and recycle → seamless
loop); a curl/hook near the crest; generous negative space (few lines); and —
critically — NEAR-WHITE high-contrast wisps that are *lighter than the sky*
(a numeric contrast guard prints the luminance delta so the old "too dark"
failure can't recur).
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
from tools.sketch_geyser_cone import _backdrop, PERIOD, FPS, N_FRAMES
from tools.sketch_geyser_gust import _swoosh, _leaf
from tools.sketch_geyser_wind import _stamp

OUT_DIR = os.path.join(ROOT, "docs", "screenshots", "geyser_windlines")

WIND = (250, 253, 255)     # near-white — must read lighter than the sky
WINDW = (255, 252, 244)    # faintly warm white
MOTE = (255, 252, 244)


def _life(p):
    return math.sin(math.pi * p) ** 0.6


def _wind_line(scene, x0, base_y, hcol, t, *, phase, length, amp, hook,
               lean, maxw, color, alpha, blur=2, waver=2.0):
    """One rising curved wind-line (crescent + curl), advancing up + looping."""
    p = ((t / PERIOD) + phase) % 1.0
    y_bot = base_y - (0.04 + 0.55 * p) * hcol
    ph = 2 * math.pi * t / PERIOD
    segs = 18
    pts, ws = [], []
    for k in range(segs + 1):
        u = k / segs                                  # 0 tail(bottom) → 1 head(top)
        yy = y_bot - u * length
        bow = math.sin(u * math.pi) * amp             # crescent: out then back
        hk = max(0.0, (u - 0.72) / 0.28)
        hk = hk * hk * (3 - 2 * hk) * hook            # smooth curl near the crest
        wv = math.sin(u * 4.0 - ph * 1.4 + phase * 6) * waver
        pts.append((x0 + lean * (bow + hk) + wv, yy))
        ws.append(0.35 + 0.65 * math.sin(math.pi * u) ** 0.7)  # lens, min width
    _swoosh(scene, pts, ws, maxw, color, alpha * _life(p), blur=blur)


# ── V1: classic wind crescents (few, bold, curled, lots of negative space) ───
def render_v1(scene, streams, t):
    for (x, by, h, inten) in streams:
        specs = [(0.00, 6.0, 18, 12), (0.34, 3.2, 14, 9),
                 (0.62, 5.0, 20, 13), (0.84, 2.6, 12, 8)]
        for i, (phase, mw, amp, hook) in enumerate(specs):
            _wind_line(scene, x + (i - 1.5) * 8, by, h, t, phase=phase,
                       length=120, amp=amp, hook=hook, lean=1.0, maxw=mw,
                       color=WINDW if i == 0 else WIND, alpha=185 * inten)


# ── V2: stacked wave-lines (even, thinner, strong loop) ──────────────────────
def render_v2(scene, streams, t):
    for (x, by, h, inten) in streams:
        n = 6
        for i in range(n):
            _wind_line(scene, x + (i - (n - 1) / 2) * 7, by, h, t,
                       phase=i / n, length=104, amp=13, hook=8, lean=1.0,
                       maxw=3.0, color=WIND, alpha=150 * inten, waver=1.5)


# ── V3: curled ribbons (longer, heavier, big crest curl) ─────────────────────
def render_v3(scene, streams, t):
    for (x, by, h, inten) in streams:
        specs = [(0.0, 7.0, 18, 18), (0.4, 5.5, 22, 16), (0.72, 4.0, 14, 14)]
        for i, (phase, mw, amp, hook) in enumerate(specs):
            _wind_line(scene, x + (i - 1) * 10, by, h, t, phase=phase,
                       length=150, amp=amp, hook=hook, lean=1.0, maxw=mw,
                       color=WINDW if i == 1 else WIND, alpha=170 * inten,
                       blur=2)


# ── V4: wind + carried leaves ────────────────────────────────────────────────
def render_v4(scene, streams, t):
    for (x, by, h, inten) in streams:
        for i, (phase, mw, amp, hook) in enumerate(
                [(0.0, 5.5, 18, 12), (0.4, 3.0, 14, 9), (0.72, 4.5, 20, 12)]):
            _wind_line(scene, x + (i - 1) * 9, by, h, t, phase=phase,
                       length=124, amp=amp, hook=hook, lean=1.0, maxw=mw,
                       color=WIND, alpha=175 * inten)
        ph = 2 * math.pi * t / PERIOD
        for li in range(3):
            p = ((t / PERIOD) * 0.95 + li / 3.0) % 1.0
            yy = by - (0.05 + 0.6 * p) * h
            xx = x + 14 + math.sin(p * 3 + li) * (8 + 14 * p)
            # short motion streak behind the leaf
            for s in range(3):
                _stamp(scene, xx - 4 * s, yy + 2 * s, 1.6, WIND,
                       90 * _life(p) * inten * (1 - s / 3))
            _leaf(scene, xx, yy, p * 8 + li, 1.05 - 0.4 * p,
                  225 * _life(p) * inten)


# ── V5: soft breeze (minimal / maximal negative space) ───────────────────────
def render_v5(scene, streams, t):
    for (x, by, h, inten) in streams:
        for i, phase in enumerate((0.0, 0.4, 0.74)):
            _wind_line(scene, x + (i - 1) * 12, by, h, t, phase=phase,
                       length=132, amp=15, hook=10, lean=1.0,
                       maxw=2.6, color=WIND, alpha=135 * inten, waver=1.5)


VARIANTS = [
    ("v1_crescents", "V1 - Wind crescents", render_v1),
    ("v2_wavelines", "V2 - Stacked wave-lines", render_v2),
    ("v3_ribbons", "V3 - Curled ribbons", render_v3),
    ("v4_leaves", "V4 - Wind + leaves", render_v4),
    ("v5_breeze", "V5 - Soft breeze", render_v5),
]

STREAMS = [(120, GROUND_Y, 236, 1.0), (252, GROUND_Y, 172, 0.85)]


def _vent(scene, x):
    vw = 28
    v = pygame.Surface((vw + 6, 13), pygame.SRCALPHA)
    pygame.draw.ellipse(v, (74, 60, 50, 190), (3, 3, vw, 7))
    pygame.draw.ellipse(v, (44, 33, 26, 220), (3, 5, vw, 4))
    scene.blit(v, (int(x) - vw // 2 - 3, GROUND_Y - 6))


def _luma(rgb):
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def main():
    pygame.init()
    pygame.display.set_mode((W, H))
    os.makedirs(OUT_DIR, exist_ok=True)
    base = _backdrop()
    base_arr = pygame.surfarray.array3d(base).astype(float)
    font = pygame.font.Font(None, 26)
    panels = []
    for slug, label, fn in VARIANTS:
        frames = []
        mid_scene = None
        for i in range(N_FRAMES):
            t = i / FPS
            scene = base.copy()
            for (x, by, h, inten) in STREAMS:
                _vent(scene, x)
            fn(scene, STREAMS, t)
            if i == N_FRAMES // 2:
                mid_scene = scene.copy()
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
        # contrast guard: wind pixels must be brighter than the sky behind them
        a = pygame.surfarray.array3d(mid_scene).astype(float)
        d = np.abs(a - base_arr).sum(2)
        mask = d > 24
        if mask.any():
            delta = (_luma(a)[mask] - _luma(base_arr)[mask]).mean()
            flag = "OK" if delta > 0 else "** TOO DARK **"
            print("%-22s luma_delta=%+6.1f  coverage=%4.1f%%  %s"
                  % (label, delta, mask.mean() * 100, flag))
        else:
            print("%-22s no wind pixels?!" % label)
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
