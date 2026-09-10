"""Fuller wind-burst geyser: same curved wobbling wind-lines as
``sketch_geyser_windlines`` but with many more lines, tighter spacing and
optional depth layers so the burst reads FULL instead of sparse. Renders as
looping GIFs (+ posters + comparison) under
``docs/screenshots/geyser_windfull/``:

    python tools/sketch_geyser_windfull.py

Throwaway design sketch. Reuses the ``_wind_line`` primitive (curved crescent
+ curl + wobble, near-white for contrast). Variants step up density and add
flavors (leaves, heavier ribbons). Contrast guard prints wind-vs-sky luminance
so it can't go dark.
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
from tools.sketch_geyser_windlines import (
    _wind_line, _life, _vent, _luma, WIND, WINDW, STREAMS)
from tools.sketch_geyser_gust import _leaf
from tools.sketch_geyser_wind import _stamp


def _full(scene, streams, t, *, n, cw, length=124, amp=15, hook=11,
          maxw_lo=2.4, maxw_hi=5.5, alpha=170, layers=1):
    """A full fan of evenly-spaced wobbling wind-lines (the wave technique)."""
    for (x, by, h, inten) in streams:
        for layer in range(layers):
            back = layer > 0
            for i in range(n):
                frac = (i - (n - 1) / 2) / max(1, (n - 1) / 2)   # -1..1
                x0 = x + frac * cw * 0.5 + layer * 4
                phase = ((i / n) + layer * 0.5 / n) % 1.0
                gust = (i % 3 == 0)
                mw = maxw_hi if gust else maxw_lo
                amp_i = amp * (0.8 + 0.45 * ((i * 37) % 5) / 4.0)
                a = alpha * (0.6 if back else 1.0) * inten
                _wind_line(scene, x0, by, h, t, phase=phase, length=length,
                           amp=amp_i, hook=hook, lean=1.0, maxw=mw,
                           color=WINDW if gust else WIND, alpha=a,
                           blur=3 if back else 2)


# ── WF1: fuller ──────────────────────────────────────────────────────────────
def render_wf1(scene, streams, t):
    _full(scene, streams, t, n=8, cw=42, alpha=175)


# ── WF2: full ─────────────────────────────────────────────────────────────────
def render_wf2(scene, streams, t):
    _full(scene, streams, t, n=11, cw=50, alpha=165)


# ── WF3: very full (with a faint back layer for body) ────────────────────────
def render_wf3(scene, streams, t):
    _full(scene, streams, t, n=13, cw=56, alpha=150, layers=2)


# ── WF4: full + carried leaves ───────────────────────────────────────────────
def render_wf4(scene, streams, t):
    _full(scene, streams, t, n=9, cw=46, alpha=168)
    for (x, by, h, inten) in streams:
        for li in range(4):
            p = ((t / PERIOD) * 0.95 + li / 4.0) % 1.0
            yy = by - (0.05 + 0.6 * p) * h
            xx = x + 12 + math.sin(p * 3 + li) * (8 + 16 * p)
            for s in range(3):
                _stamp(scene, xx - 4 * s, yy + 2 * s, 1.6, WIND,
                       90 * _life(p) * inten * (1 - s / 3))
            _leaf(scene, xx, yy, p * 8 + li, 1.05 - 0.4 * p,
                  225 * _life(p) * inten)


# ── WF5: full heavy ribbons ──────────────────────────────────────────────────
def render_wf5(scene, streams, t):
    _full(scene, streams, t, n=8, cw=48, length=140, amp=18, hook=15,
          maxw_lo=3.6, maxw_hi=7.5, alpha=160)


VARIANTS = [
    ("wf1_fuller", "WF1 - Fuller", render_wf1),
    ("wf2_full", "WF2 - Full", render_wf2),
    ("wf3_veryfull", "WF3 - Very full", render_wf3),
    ("wf4_leaves", "WF4 - Full + leaves", render_wf4),
    ("wf5_ribbons", "WF5 - Full ribbons", render_wf5),
]

OUT_DIR = os.path.join(ROOT, "docs", "screenshots", "geyser_windfull")


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
        a = pygame.surfarray.array3d(mid_scene).astype(float)
        d = np.abs(a - base_arr).sum(2)
        mask = d > 24
        delta = (_luma(a)[mask] - _luma(base_arr)[mask]).mean() if mask.any() else 0
        print("%-20s luma_delta=%+6.1f  coverage=%4.1f%%  %s"
              % (label, delta, mask.mean() * 100,
                 "OK" if delta > 0 else "** TOO DARK **"))
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
