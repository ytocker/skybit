"""Air-flow geyser: dense fields of fine, subtle swoosh streamlines (built on
the G4 'brisk multi-swoosh' direction). Renders 5 variants as looping GIFs
(+ posters + comparison) under ``docs/screenshots/geyser_airflow/``:

    python tools/sketch_geyser_airflow.py

Throwaway design sketch. Each stream is many thin tapered swooshes whose
horizontal displacement comes from a *shared* flow function of (x, height,
time), so neighbouring strokes bend together and read as coherent flowing
air rather than scattered marks. Translucent cool/white, kept subtle.
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
from tools.sketch_geyser_gust import _swoosh

OUT_DIR = os.path.join(ROOT, "docs", "screenshots", "geyser_airflow")

AIR = (228, 240, 250)
AIRW = (255, 250, 240)
MOTE = (246, 240, 228)


def _life(p):
    return math.sin(math.pi * p) ** 0.7


def _fan_out(g):
    return 0.6 + 0.5 * g          # gently widen with height


def _fan_conv(g):
    return 1.0 - 0.82 * g         # converge toward the top (plume)


def _flow_stroke(xc, base_y, hcol, lane, p, t, *, length_f, amp, curl_k,
                 swirl, cw, fan):
    ph = 2 * math.pi * t / PERIOD
    yc = base_y - (0.07 + 0.85 * p) * hcol
    length = hcol * length_f
    segs = 16
    pts, ws = [], []
    for k in range(segs + 1):
        u = k / segs
        yy = yc + (0.5 - u) * length
        g = max(0.0, (base_y - yy) / hcol)
        lane_off = lane * cw * 0.5 * fan(g)
        # shared flow displacement: phase tied to absolute x → neighbours align
        disp = amp * math.sin(g * curl_k - ph * 1.6 + (xc + lane_off) * 0.05
                              + lane * 0.6)
        sw = swirl * 4.0 * math.sin(g * 7.0 - ph * 3.0 + lane * 4.0) if swirl else 0.0
        pts.append((xc + lane_off + disp + sw, yy))
        ws.append(math.sin(math.pi * u) ** 0.85)
    return pts, ws


def _field(scene, streams, t, *, lanes=9, per=3, amp=6.0, curl_k=2.6,
           swirl=0.0, cw=64, fan=_fan_out, length_f=0.34, maxw=2.6,
           alpha=56, blur=1, warm_every=4):
    for (x, by, h, inten) in streams:
        for li in range(lanes):
            lane = (li - (lanes - 1) / 2.0) / max(1.0, (lanes - 1) / 2.0)
            for m in range(per):
                p = ((t / PERIOD) + li * 0.11 + m / per) % 1.0
                pts, ws = _flow_stroke(x, by, h, lane, p, t, length_f=length_f,
                                       amp=amp, curl_k=curl_k, swirl=swirl,
                                       cw=cw, fan=fan)
                col = AIRW if (li + m) % warm_every == 0 else AIR
                _swoosh(scene, pts, ws, maxw, col,
                        alpha * _life(p) * inten, blur=blur)


def _motes(scene, streams, t, seed, n=18, cw=60):
    for (x, by, h, inten) in streams:
        rng = np.random.RandomState(int(x) * 7 + seed)
        for d in range(n):
            off = rng.rand()
            lane = (rng.rand() - 0.5) * 2
            p = ((t / PERIOD) + off) % 1.0
            yy = by - (0.07 + 0.85 * p) * h
            g = (by - yy) / h
            xx = x + lane * cw * 0.5 * (0.6 + 0.5 * g) + \
                math.sin(g * 5 - 2 * math.pi * t / PERIOD + d) * (4 + 8 * g)
            a = 130 * _life(p) * inten
            r = 1.3 + 0.8 * (1 - p)
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*MOTE, int(a)), (2, 2), max(1, int(r)))
            scene.blit(s, (int(xx - 2), int(yy - 2)))


# ── A1: laminar flow (clean, near-parallel rising streamlines) ───────────────
def render_a1(scene, streams, t):
    _field(scene, streams, t, lanes=9, per=3, amp=5.0, curl_k=2.3, swirl=0.0,
           maxw=2.6, alpha=54, blur=1)


# ── A2: turbulent eddies (wavier, small vortical wiggle) ─────────────────────
def render_a2(scene, streams, t):
    _field(scene, streams, t, lanes=9, per=3, amp=9.0, curl_k=3.6, swirl=1.0,
           maxw=2.4, alpha=54, blur=1)


# ── A3: converging plume (many fine lines pinching upward) ───────────────────
def render_a3(scene, streams, t):
    _field(scene, streams, t, lanes=11, per=3, amp=5.0, curl_k=2.6, swirl=0.0,
           cw=78, fan=_fan_conv, length_f=0.40, maxw=2.2, alpha=52, blur=1)


# ── A4: layered depth (faint wide back layer + crisp fine front) ─────────────
def render_a4(scene, streams, t):
    _field(scene, streams, t, lanes=5, per=2, amp=7.0, curl_k=2.0, swirl=0.0,
           cw=78, maxw=5.0, alpha=26, blur=3, length_f=0.5)     # background
    _field(scene, streams, t, lanes=10, per=3, amp=5.0, curl_k=2.8, swirl=0.3,
           cw=58, maxw=2.3, alpha=62, blur=1)                   # foreground


# ── A5: wispy streamlines + drifting motes ───────────────────────────────────
def render_a5(scene, streams, t):
    _field(scene, streams, t, lanes=9, per=3, amp=6.0, curl_k=2.6, swirl=0.4,
           maxw=2.2, alpha=48, blur=1)
    _motes(scene, streams, t, seed=3)


VARIANTS = [
    ("a1_laminar", "A1 - Laminar flow", render_a1),
    ("a2_turbulent", "A2 - Turbulent eddies", render_a2),
    ("a3_plume", "A3 - Converging plume", render_a3),
    ("a4_layered", "A4 - Layered depth", render_a4),
    ("a5_motes", "A5 - Wisps + motes", render_a5),
]

STREAMS = [(120, GROUND_Y, 234, 1.0), (252, GROUND_Y, 170, 0.85)]


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
