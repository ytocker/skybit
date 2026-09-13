"""Air-flow geyser, take 2: long continuous wobbling streamlines (not tapered
swooshes — those read as flak/shell trails). Renders 5 variants as looping
GIFs (+ posters + comparison) under ``docs/screenshots/geyser_flow/``:

    python tools/sketch_geyser_flow.py

Throwaway design sketch. Each stream is a set of near-vertical, constant-thin
streamlines that rise from the vent and wobble side-to-side via travelling
sine(s); a faint brightness pulse travels *up* each line to cue flow
direction. Translucent cool/white, subtle. Minimal fan so it reads as rising
air, not an aerial burst.
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
from tools.sketch_geyser_wind import _stamp

OUT_DIR = os.path.join(ROOT, "docs", "screenshots", "geyser_flow")

AIR = (228, 240, 250)
AIRW = (255, 250, 240)
MOTE = (246, 240, 228)


def _fade(up):
    # fade in over the first 6%, hold, fade out over the top 28%
    return max(0.0, min(1.0, min(up / 0.06, (1.0 - up) / 0.28)))


def _streamline(scene, x0, base_y, hcol, t, *, harms, r, alpha, color,
                drift=0.0, pulse_speed=2.0, lane_phase=0.0):
    """One thin wobbling line. ``harms`` = list of (amp, freq, speed, phase)."""
    ph = 2 * math.pi * t / PERIOD
    step = 3
    for j in range(0, int(hcol), step):
        up = j / hcol
        wob = 0.0
        for (amp, freq, speed, phse) in harms:
            wob += amp * math.sin(freq * j - speed * ph + phse + lane_phase)
        x = x0 + drift + wob * (0.5 + 0.7 * up)        # wobble grows a little upward
        y = base_y - j
        pulse = 0.6 + 0.4 * math.sin(0.05 * j - ph * pulse_speed + lane_phase)
        a = alpha * _fade(up) * pulse
        _stamp(scene, x, y, r, color, a)


def _lanes(x, n, cw):
    if n == 1:
        return [x]
    return [x + (i - (n - 1) / 2.0) * (cw / (n - 1)) for i in range(n)]


def _field(scene, streams, t, *, n=8, cw=54, r=1.8, alpha=72, harms_fn=None,
           drift_amp=0.0, pulse_speed=2.0, warm_every=4):
    for (x, by, h, inten) in streams:
        for li, x0 in enumerate(_lanes(x, n, cw)):
            harms = harms_fn(li)
            drift = (drift_amp * math.sin(2 * math.pi * t / PERIOD)) if drift_amp else 0.0
            col = AIRW if li % warm_every == 0 else AIR
            _streamline(scene, x0, by, h, t, harms=harms, r=r,
                        alpha=alpha * inten, color=col, drift=drift,
                        pulse_speed=pulse_speed, lane_phase=li * 0.7)


# ── F1: gentle single-wobble lines ───────────────────────────────────────────
def render_f1(scene, streams, t):
    _field(scene, streams, t, n=8, r=1.9, alpha=74,
           harms_fn=lambda li: [(7.0, 0.022, 1.6, 0.0)])


# ── F2: double-harmonic organic wobble ───────────────────────────────────────
def render_f2(scene, streams, t):
    _field(scene, streams, t, n=8, r=1.8, alpha=70,
           harms_fn=lambda li: [(6.0, 0.018, 1.5, 0.0),
                                (3.0, 0.052, 2.6, 1.1)])


# ── F3: group drift (whole column sways like a breeze) + wobble ──────────────
def render_f3(scene, streams, t):
    _field(scene, streams, t, n=9, r=1.8, alpha=70, drift_amp=10.0,
           harms_fn=lambda li: [(5.0, 0.020, 1.4, 0.0),
                                (2.4, 0.048, 2.3, 0.6)])


# ── F4: dense wispy (many very thin, very subtle) ────────────────────────────
def render_f4(scene, streams, t):
    _field(scene, streams, t, n=14, cw=60, r=1.4, alpha=46,
           harms_fn=lambda li: [(6.0, 0.020, 1.5, li * 0.4),
                                (2.6, 0.050, 2.4, li)])


# ── F5: wobbling lines + drifting motes riding the flow ──────────────────────
def render_f5(scene, streams, t):
    _field(scene, streams, t, n=8, r=1.7, alpha=58,
           harms_fn=lambda li: [(6.0, 0.020, 1.5, 0.0),
                                (2.6, 0.050, 2.4, 0.8)])
    ph = 2 * math.pi * t / PERIOD
    for (x, by, h, inten) in streams:
        rng = np.random.RandomState(int(x) * 7 + 9)
        for d in range(16):
            off = rng.rand()
            lane = (rng.rand() - 0.5) * 50
            p = ((t / PERIOD) + off) % 1.0
            y = by - p * h
            xx = x + lane + math.sin(0.05 * (h * p) - ph * 1.6 + d) * 8
            a = 140 * _fade(p) * inten
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*MOTE, int(a)), (2, 2), 1 + (p < 0.5))
            scene.blit(s, (int(xx - 2), int(y - 2)))


VARIANTS = [
    ("f1_wobble", "F1 - Gentle wobble", render_f1),
    ("f2_organic", "F2 - Organic wobble", render_f2),
    ("f3_drift", "F3 - Breeze drift", render_f3),
    ("f4_wispy", "F4 - Dense wispy", render_f4),
    ("f5_motes", "F5 - Wobble + motes", render_f5),
]

STREAMS = [(120, GROUND_Y, 236, 1.0), (252, GROUND_Y, 172, 0.85)]


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
