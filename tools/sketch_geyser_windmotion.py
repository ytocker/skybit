"""Motion-first WIND geyser sketches. Previous attempts failed because drawn
lines wobble *in place* and read as marks, not moving air. Wind reads through
MOTION, so every variant here banks on fast travel across the loop (judge the
GIFs, not the posters). Four directions the user asked to see side by side:

    M1  streaming debris   - fine specks + tumbling leaves streaking fast,
                             each with a motion-blur trail (the moving stuff
                             is the wind tell)
    M2  fast flow-streaks  - anime speed-lines that zip UP the screen and
                             fade, instead of sitting still
    M3  bend the world     - windswept reeds/grass bending in a travelling
                             gust + torn leaves carried off (wind by effect)
    M4  steam column       - soft billowing vapor rising, widening, drifting
                             and dissipating (geyser-steam look)

Run:  python tools/sketch_geyser_windmotion.py
Outputs GIFs + posters + comparison under docs/screenshots/geyser_windmotion/.
Throwaway design sketch. Contrast guard measures only the AIRBORNE region so
bright wisps stay lighter than sky (ground foliage in M3 is exempt).
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
from tools.sketch_geyser_windlines import WIND, WINDW, _luma

OUT_DIR = os.path.join(ROOT, "docs", "screenshots", "geyser_windmotion")
STREAMS = [(120, GROUND_Y, 236, 1.0), (252, GROUND_Y, 172, 0.85)]
LEAFC = (206, 150, 66)
GRASS = (118, 142, 74)
GRASS_T = (150, 176, 96)


def _life(p):
    return math.sin(math.pi * p) ** 0.7


def _vent(scene, x):
    vw = 28
    v = pygame.Surface((vw + 6, 13), pygame.SRCALPHA)
    pygame.draw.ellipse(v, (74, 60, 50, 190), (3, 3, vw, 7))
    pygame.draw.ellipse(v, (44, 33, 26, 220), (3, 5, vw, 4))
    scene.blit(v, (int(x) - vw // 2 - 3, GROUND_Y - 6))


# ── M1: streaming debris (motion-blur particles + leaves) ────────────────────
def _flow(x, by, h, p, seed, bias):
    """Parametric flow path: rises fast, pushed coherently leeward, sways."""
    y = by - (0.02 + 0.98 * p) * h
    sway = math.sin(p * 5.0 + seed) * (4 + 9 * p)
    lead = bias * (6 + 48 * p)            # coherent push (wind direction)
    return x + lead + sway, y


def render_debris(scene, streams, t):
    n = 42
    for (x, by, h, inten) in streams:
        for i in range(n):
            seed = i * 1.937
            bias = 0.7 + 0.3 * ((i % 4) / 3.0)
            spd = 1.0 + (i % 3) * 0.13
            p = ((t / PERIOD) * spd + i / n + (i * 0.137) % 1.0) % 1.0
            xh, yh = _flow(x, by, h, p, seed, bias)
            for s in range(8):                       # motion-blur trail
                pp = p - s * 0.018
                if pp <= 0:
                    break
                xs, ys = _flow(x, by, h, pp, seed, bias)
                _stamp(scene, xs, ys, max(0.8, 2.3 - s * 0.2), WINDW,
                       205 * _life(p) * inten * (1 - s / 8.0))
            if i % 11 == 4:                           # a few torn leaves
                _leaf(scene, xh, yh, p * 9 + i, 1.05 - 0.4 * p,
                      225 * _life(p) * inten)


# ── M2: fast flow-streaks (anime speed-lines zipping up) ─────────────────────
def render_streaks(scene, streams, t, scale=1.0):
    ph = 2 * math.pi * t / PERIOD
    n = 44
    for (x, by, h, inten) in streams:
        rise = by - 28                               # travel vent → near top
        for i in range(n):
            p = ((t / PERIOD) * 1.2 + (i * 0.6180339) % 1.0) % 1.0
            yh = by - (0.03 + 0.96 * p) * rise        # head zips full height
            length = 34 + 24 * math.sin(math.pi * p)  # stretch mid-flight
            x0 = x + (i % 9 - 4) * 7
            segs = 12
            pts, ws = [], []
            for k in range(segs + 1):
                u = k / segs
                yy = yh + u * length                 # tail trails below head
                curl = math.sin(u * 3.0 - ph * 1.6 + i) * (3 + 4 * u)
                lead = (8 + 26 * p)                  # coherent lean
                pts.append((x0 + lead + curl, yy))
                ws.append(math.sin(math.pi * u) ** 0.7)
            _swoosh(scene, pts, ws, 2.0, WINDW if i % 2 else WIND,
                    38 * _life(p) * inten * scale, blur=2)


# ── M3: bend the world (windswept foliage + carried leaves) ──────────────────
def _blade(scene, root_x, hb, lean, color, t, seed, quiver):
    segs = 10
    pts, ws = [], []
    for k in range(segs + 1):
        u = k / segs                                  # 0 root → 1 tip
        yy = GROUND_Y - u * hb
        bend = lean * (u * u) * hb                    # curve sharpens toward tip
        q = math.sin(t * 7 + seed + u * 3) * quiver * u
        pts.append((root_x + bend + q, yy))
        ws.append(1.0 - 0.85 * u)                     # taper to a point
    _swoosh(scene, pts, ws, 2.6, color, 235, blur=1)


def render_bend(scene, streams, t):
    # travelling gust: lean strength pulses across the loop
    gust = 0.34 + 0.30 * math.sin(2 * math.pi * t / PERIOD)
    for (x, by, h, inten) in streams:
        blades = [(-34, 26, 0), (-22, 40, 1), (-11, 31, 2), (0, 46, 3),
                  (11, 36, 4), (23, 28, 5), (34, 38, 6), (44, 22, 7)]
        for dx, hb, sd in blades:
            tall = hb > 36
            _blade(scene, x + dx, hb, gust * (1.1 if tall else 0.9),
                   GRASS_T if tall else GRASS, t, sd * 1.7,
                   quiver=3.5 if tall else 2.0)
        # a couple of leaves torn off the tips and carried leeward
        for li in range(3):
            p = ((t / PERIOD) * 1.05 + li / 3.0) % 1.0
            yy = GROUND_Y - 34 - (0.3 + 0.7 * p) * (h * 0.55)
            xx = x + 18 + (20 + 40 * p) * gust + math.sin(p * 5 + li) * 9
            _leaf(scene, xx, yy, p * 10 + li, 1.0 - 0.35 * p,
                  220 * _life(p) * inten)
        # faint speed hint in the air above
        for i in range(4):
            p = ((t / PERIOD) * 1.3 + i / 4.0) % 1.0
            yh = by - (0.2 + 0.7 * p) * h
            _stamp(scene, x + 16 + (14 + 40 * p) * gust, yh, 1.4, WINDW,
                   70 * _life(p) * inten)


# ── M4: steam column (rising flowing vapor, not glued discs) ─────────────────
def _flow_ribbon(scene, x, by, h, t, phase, *, amp, length_f, maxw, alpha,
                 fan, blur, spd):
    """One soft translucent filament of vapour: rises, wavers turbulently,
    widens and spreads as it climbs. Many overlapping → flowing column."""
    p = ((t / PERIOD) * spd + phase) % 1.0
    y_bot = by - (0.02 + 0.22 * p) * h         # base stays near the vent
    length = h * length_f
    ph = 2 * math.pi * t / PERIOD
    segs = 22
    pts, ws = [], []
    for k in range(segs + 1):
        u = k / segs                           # 0 bottom → 1 top
        yy = y_bot - u * length
        wav = math.sin(u * 3.4 - ph * 1.5 + phase * 6.0) * amp * (0.25 + u)
        taper = 1.0 - max(0.0, (u - 0.85) / 0.15) ** 2   # soften the crest
        pts.append((x + wav + fan * u, yy))
        ws.append((0.3 + 0.85 * u) * taper)    # narrow at vent → broad aloft
    _swoosh(scene, pts, ws, maxw, WINDW, alpha * _life(p), blur=blur)


STEAM_LOW_BOOST = 2.4          # alpha multiplier at ground level
STEAM_NORM_FRAC = 0.30         # height (frac of rise) where it eases to normal


def _boost_low(layer, ground_y, norm_y, boost):
    """Scale alpha up near the ground, ramping back to 1.0 by norm_y so the
    column reads solid through the mountains and stays faint higher up."""
    a = pygame.surfarray.pixels_alpha(layer)
    ys = np.arange(layer.get_height(), dtype=float)
    f = np.ones_like(ys)
    reg = ys >= norm_y
    f[reg] = 1.0 + (boost - 1.0) * np.clip(
        (ys[reg] - norm_y) / (ground_y - norm_y), 0.0, 1.0)
    a[:, :] = np.clip(a.astype(float) * f[None, :], 0, 255).astype(np.uint8)
    del a


def render_steam(scene, streams, t, scale=1.0, ncols=9):
    span = 28.0                                # column spread half-width
    if ncols <= 1:
        offs = [0.0]
    else:
        offs = [-span + 2 * span * j / (ncols - 1) for j in range(ncols)]
    layer = pygame.Surface(scene.get_size(), pygame.SRCALPHA)
    for (x, by, h, inten) in streams:
        rise = by - 28                         # span vent → near the top
        for c, dx in enumerate(offs):
            for i in range(3):                 # a few filaments per column
                idx = c * 3 + i
                _flow_ribbon(layer, x + dx, by, rise, t,
                             phase=(idx * 0.6180339) % 1.0,
                             amp=6 + (idx % 3) * 5,
                             length_f=0.9 + 0.06 * (idx % 2),
                             maxw=3.4 + 1.2 * (idx % 2), alpha=21 * inten * scale,
                             fan=(i - 1) * 4, blur=3,
                             spd=0.9 + 0.05 * (idx % 3))
    gy = max(by for _, by, _, _ in streams)
    _boost_low(layer, gy, gy - STEAM_NORM_FRAC * (gy - 28), STEAM_LOW_BOOST)
    scene.blit(layer, (0, 0))


VARIANTS = [
    ("m1_debris", "M1 - Streaming debris", render_debris),
    ("m2_streaks", "M2 - Fast flow-streaks", render_streaks),
    ("m3_bend", "M3 - Bend the world", render_bend),
    ("m4_steam", "M4 - Steam column", render_steam),
]


def main():
    pygame.init()
    pygame.display.set_mode((W, H))
    os.makedirs(OUT_DIR, exist_ok=True)
    base = _backdrop()
    base_arr = pygame.surfarray.array3d(base).astype(float)
    yc = GROUND_Y - 16                                # airborne region only
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
        a = pygame.surfarray.array3d(mid_scene).astype(float)[:, :yc]
        b = base_arr[:, :yc]
        d = np.abs(a - b).sum(2)
        mask = d > 20
        delta = (_luma(a)[mask] - _luma(b)[mask]).mean() if mask.any() else 0.0
        print("%-22s air_luma_delta=%+6.1f  air_cover=%4.1f%%  %s"
              % (label, delta, mask.mean() * 100,
                 "OK" if delta > 0 else "** dark **"))
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
