"""Refine the 'volumetric updraft cone' geyser into 5 top-notch variants and
render each as a looping GIF (+ poster PNG) under
``docs/screenshots/geyser_cone_v2/``. Run from the repo root:

    python tools/sketch_geyser_cone.py

Throwaway design-exploration sketch — none of it ships. After a variant is
chosen it gets ported into ``Geyser.draw`` (``game/entities.py``).

Pro recipe shared by every variant: layered additive glow built from
Gaussian-soft *disc stacks* (smoothscale blur → no banding), a height color
ramp (hot amber → gold → transparent), a thin white-hot core, a bloom pass
(blurred copy added back), a warm ground glow pool + lit vent, gentle
turbulence, and a few fine hero sparks (never one floating dot).
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
from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground

OUT_DIR = os.path.join(ROOT, "docs", "screenshots", "geyser_cone_v2")
PHASE = 0.25
PERIOD = 1.6
FPS = 25
N_FRAMES = int(PERIOD * FPS)

AMBER = (255, 120, 28)
GOLD = (255, 198, 96)
WHITE_HOT = (255, 246, 224)
CORAL = (255, 146, 104)
POOL = (255, 138, 52)
ADD = pygame.BLEND_ADD


def _lerp_c(a, b, t):
    t = max(0.0, min(1.0, t))
    return (a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


def _sc(c, m):
    m = max(0.0, min(1.0, m))
    return (int(max(0, min(255, c[0] * m))),
            int(max(0, min(255, c[1] * m))),
            int(max(0, min(255, c[2] * m))))


def _q(c):
    return (int(c[0]) // 8 * 8, int(c[1]) // 8 * 8, int(c[2]) // 8 * 8)


def _blur(s, downs):
    w, h = s.get_size()
    if w < downs * 2 or h < downs * 2:
        return s
    sm = pygame.transform.smoothscale(s, (w // downs, h // downs))
    return pygame.transform.smoothscale(sm, (w, h))


_disc_cache: dict = {}


def _disc(rad, color):
    rad = max(1, int(rad))
    key = (rad, color)
    s = _disc_cache.get(key)
    if s is None:
        d = rad * 2
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, 255), (rad, rad), max(1, int(rad * 0.55)))
        s = _blur(s, 3 if rad >= 7 else 2)
        _disc_cache[key] = s
    return s


def _blit_disc(layer, x, y, rad, color, flags=ADD):
    rad = max(1, int(rad))
    layer.blit(_disc(rad, color), (int(x - rad), int(y - rad)),
               special_flags=flags)


def _vent(scene, x, base_y):
    vw = 34
    v = pygame.Surface((vw + 8, 16), pygame.SRCALPHA)
    pygame.draw.ellipse(v, (58, 44, 36, 235), (4, 4, vw, 9))
    pygame.draw.ellipse(v, (28, 20, 16, 255), (4, 6, vw, 6))
    scene.blit(v, (int(x) - vw // 2 - 4, base_y - 8))


def _base_pool(scene, x, base_y, inten):
    # warm light cast on the terrain at the vent
    _blit_disc(scene, x, base_y - 2, 30, _q(_sc(POOL, 0.55 * inten)))
    _blit_disc(scene, x, base_y - 2, 16, _q(_sc(GOLD, 0.5 * inten)))


def _sparks(scene, x, base_y, hcol, inten, t, seed):
    rng = np.random.RandomState(seed)
    for e in range(7):
        off = rng.rand()
        ph = rng.rand() * math.tau
        sway = 7 + rng.rand() * 11
        p = ((t / PERIOD) + off) % 1.0
        y = base_y - p * hcol
        xx = x + math.sin(p * 3.0 + ph) * sway * p
        a = (1.0 - p) * inten * (0.7 + 0.3 * math.sin(t * 17 + ph))
        _blit_disc(scene, xx, y, 2 + 2.2 * (1 - p), _q(_sc(WHITE_HOT, a)))


def _column(layer, x, base_y, hcol, inten, t, body=(AMBER, GOLD),
            base_half=26, taper=0.5, alpha=0.9, turb=0.0, flick=0.0, core=True):
    step = 5
    ph = 2 * math.pi * t / PERIOD
    for j in range(0, int(hcol), step):
        up = j / hcol
        ox, wob = (0.0, 1.0)
        if turb:
            ox = math.sin(up * 4.0 - ph * 2.0 + x) * turb * (0.3 + up * 1.2)
            wob = 1.0 + 0.18 * math.sin(up * 6.0 - ph * 3.0 + x * 0.5)
        rad = base_half * (1.0 - taper * up) * wob
        bright = (1.0 - up) ** 1.4 * inten * alpha
        if flick:
            bright *= 0.85 + 0.15 * math.sin(t * 20 - j * 0.4 + x)
        _blit_disc(layer, x + ox, base_y - j, rad,
                   _q(_sc(_lerp_c(body[0], body[1], up), bright)))
    if core:
        for j in range(0, int(hcol), step):
            up = j / hcol
            ox = (math.sin(up * 4.0 - ph * 2.0 + x) * turb * (0.3 + up * 1.2)
                  if turb else 0.0)
            rad = max(1.0, base_half * 0.30 * (1.0 - 0.65 * up))
            bright = (1.0 - up) ** 1.8 * inten
            _blit_disc(layer, x + ox, base_y - j, rad,
                       _q(_sc(WHITE_HOT, bright)))


def _compose(scene, streams, t, halo_downs=4, **col_kw):
    """Standard layered build: vents + pool under, glow + bloom, sparks over."""
    for (x, by, h, inten) in streams:
        _vent(scene, x, by)
        _base_pool(scene, x, by, inten)
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for (x, by, h, inten) in streams:
        _column(layer, x, by, h, inten, t, **col_kw)
    scene.blit(_blur(layer, halo_downs), (0, 0), special_flags=ADD)  # bloom halo
    scene.blit(layer, (0, 0), special_flags=ADD)                     # crisp body
    for (x, by, h, inten) in streams:
        _sparks(scene, x, by, h, inten, t, int(x) * 13 + 7)


# ── C1: layered bloom column ─────────────────────────────────────────────────
def render_c1(scene, streams, t):
    _compose(scene, streams, t, body=(AMBER, GOLD), turb=0.0, flick=0.0)


# ── C2: turbulent heat plume (undulating + wispy top) ────────────────────────
def render_c2(scene, streams, t):
    for (x, by, h, inten) in streams:
        _vent(scene, x, by)
        _base_pool(scene, x, by, inten)
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    ph = 2 * math.pi * t / PERIOD
    for (x, by, h, inten) in streams:
        _column(layer, x, by, h, inten, t, body=(AMBER, GOLD),
                turb=10.0, flick=0.5)
        # top dissipation into 2 curling wisps
        for k in (-1, 1):
            for j in range(int(h * 0.62), int(h * 1.05), 5):
                up = j / h
                tt = (up - 0.62) / 0.43
                ox = math.sin(up * 5.0 - ph * 2.5 + x) * 14 * (0.4 + up)
                ox += k * tt * 18
                rad = 9 * (1.0 - tt)
                a = (1.0 - tt) ** 1.5 * inten * 0.6
                if rad > 1 and a > 0:
                    _blit_disc(layer, x + ox, by - j, rad,
                               _q(_sc(_lerp_c(GOLD, WHITE_HOT, up), a)))
    scene.blit(_blur(layer, 4), (0, 0), special_flags=ADD)
    scene.blit(layer, (0, 0), special_flags=ADD)
    for (x, by, h, inten) in streams:
        _sparks(scene, x, by, h, inten, t, int(x) * 13 + 31)


# ── C3: refractive heat column (glow + background warp) ──────────────────────
def _warp(scene, x, base_y, hcol, t, amp=4.5):
    w = 76
    x0 = max(0, int(x - w // 2))
    x1 = min(W, x0 + w)
    y0 = max(0, int(base_y - hcol))
    arr = pygame.surfarray.pixels3d(scene)
    region = arr[x0:x1, y0:base_y].copy()
    rows = region.shape[1]
    ph = 2 * math.pi * t / PERIOD
    for j in range(rows):
        frac = j / max(1, rows)
        env = math.sin(math.pi * frac) ** 0.6
        off = int(round(amp * env * math.sin(0.12 * (y0 + j) * 2.0 - ph * 2.2)))
        if off:
            arr[x0:x1, y0 + j] = np.roll(region[:, j], off, axis=0)
    del arr


def render_c3(scene, streams, t):
    for (x, by, h, inten) in streams:
        _warp(scene, x, by, h, t)
        _vent(scene, x, by)
        _base_pool(scene, x, by, inten * 0.8)
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for (x, by, h, inten) in streams:
        _column(layer, x, by, h, inten * 0.7, t, body=(AMBER, GOLD),
                alpha=0.7, turb=4.0)
    scene.blit(_blur(layer, 4), (0, 0), special_flags=ADD)
    scene.blit(layer, (0, 0), special_flags=ADD)
    for (x, by, h, inten) in streams:
        _sparks(scene, x, by, h, inten, t, int(x) * 13 + 5)


# ── C4: god-ray light shaft ──────────────────────────────────────────────────
def render_c4(scene, streams, t):
    for (x, by, h, inten) in streams:
        _vent(scene, x, by)
        _blit_disc(scene, x, by - 2, 42, _q(_sc(POOL, 0.6 * inten)))  # base bloom
        _blit_disc(scene, x, by - 2, 22, _q(_sc(GOLD, 0.55 * inten)))
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    ph = 2 * math.pi * t / PERIOD
    rays = (-0.16, -0.105, -0.055, 0.0, 0.055, 0.105, 0.16)
    for (x, by, h, inten) in streams:
        for r, ang in enumerate(rays):
            mid = (r == 3)
            sweep = ang + 0.012 * math.sin(ph * 1.5 + r)
            reach = int(h * (1.0 if mid else 0.85))
            for j in range(0, reach, 3):              # denser → continuous shafts
                up = j / h
                xx = x + sweep * j
                rad = (5.0 - 3.2 * up) * (1.0 if mid else 0.55)
                bright = (1.0 - up) ** 1.5 * inten * (0.95 if mid else 0.40)
                _blit_disc(layer, xx, by - j, rad,
                           _q(_sc(WHITE_HOT if mid else GOLD, bright)))
        # sparse dust motes drifting in the beam
        rng = np.random.RandomState(int(x) * 9 + 3)
        for d in range(8):
            off = rng.rand()
            mx = x + (rng.rand() - 0.5) * 50
            p = ((t / PERIOD) * 0.5 + off) % 1.0
            my = by - p * h
            a = (1.0 - p) * inten * 0.4 * (0.5 + 0.5 * math.sin(t * 6 + d))
            _blit_disc(layer, mx, my, 1.6, _q(_sc(WHITE_HOT, a)))
    scene.blit(_blur(layer, 4), (0, 0), special_flags=ADD)
    scene.blit(layer, (0, 0), special_flags=ADD)


# ── C5: stylized gradient plume (art-directed, crisper) ──────────────────────
def render_c5(scene, streams, t):
    pulse = 0.92 + 0.08 * math.sin(2 * math.pi * t / PERIOD)
    for (x, by, h, inten) in streams:
        _vent(scene, x, by)
        _base_pool(scene, x, by, inten)
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for (x, by, h, inten) in streams:
        _column(layer, x, by, h, inten * pulse, t, body=(GOLD, CORAL),
                base_half=24, taper=0.42, alpha=1.0, turb=3.0)
    scene.blit(_blur(layer, 2), (0, 0), special_flags=ADD)   # crisper halo
    scene.blit(layer, (0, 0), special_flags=ADD)
    for (x, by, h, inten) in streams:
        _sparks(scene, x, by, h, inten, t, int(x) * 13 + 19)


VARIANTS = [
    ("c1_bloom", "C1 - Layered bloom", render_c1),
    ("c2_turbulent", "C2 - Turbulent plume", render_c2),
    ("c3_refractive", "C3 - Refractive heat", render_c3),
    ("c4_godray", "C4 - God-ray shaft", render_c4),
    ("c5_stylized", "C5 - Stylized plume", render_c5),
]


def _backdrop():
    pal = biome.palette_for_phase(PHASE)
    bucket = int(PHASE * biome.PHASE_BUCKETS)
    base = pygame.Surface((W, H)).convert()
    base.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, bucket), (0, 0))
    draw_mountains(base, 600, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    draw_ground(base, GROUND_Y, W, H, 600,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    return base


STREAMS = [(120, GROUND_Y, 212, 1.0), (252, GROUND_Y, 150, 0.82)]


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
