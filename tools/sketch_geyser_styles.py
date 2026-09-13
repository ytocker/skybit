"""Render 5 distinctive 'hot-air stream rising from the ground' geyser styles
as looping animated GIFs (+ poster PNGs) under
``docs/screenshots/geyser_styles/``. Run from the repo root:

    python tools/sketch_geyser_styles.py

This is a throwaway design-exploration sketch — none of it ships in the game.
Once a style is chosen, that one gets ported into ``Geyser.draw`` in
``game/entities.py`` and this file/the other styles are dropped.

Each style draws two streams (a tall one + a shorter one) over a real
golden-hour backdrop composed with the same draw helpers the game uses, so
the look is judged in context. Motion is the point, hence GIFs.
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

OUT_DIR = os.path.join(ROOT, "docs", "screenshots", "geyser_styles")
PHASE = 0.25                       # golden-hour-ish, matches the ~80s peak
PERIOD = 1.6                       # loop length (s)
FPS = 25
N_FRAMES = int(PERIOD * FPS)

# Warm hot-air palette shared by the styles.
HOT = (255, 150, 45)
MID = (255, 190, 95)
PALE = (255, 226, 170)


def _lerp_c(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _glow(surf, x, y, r, color, a):
    r = int(r)
    a = int(max(0, min(255, a)))
    if r < 1 or a <= 0:
        return
    s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(s, (color[0], color[1], color[2], a), (r + 1, r + 1), r)
    surf.blit(s, (int(x - r - 1), int(y - r - 1)), special_flags=pygame.BLEND_ADD)


def _vent(surf, x, base_y):
    vw = 34
    v = pygame.Surface((vw + 4, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(v, (92, 72, 60, 200), (2, 3, vw, 8))
    pygame.draw.ellipse(v, (58, 44, 36, 230), (2, 5, vw, 5))
    surf.blit(v, (int(x) - vw // 2 - 2, base_y - 6))


# ── Style 1: heat-haze refraction ────────────────────────────────────────────
def style_haze(surf, x, base_y, hcol, t, intensity):
    _vent(surf, x, base_y)
    w = 54
    x0 = max(0, int(x - w // 2))
    x1 = min(W, x0 + w)
    y_top = int(base_y - hcol)
    arr = pygame.surfarray.pixels3d(surf)        # (W, H, 3), indexed [x][y]
    region = arr[x0:x1, y_top:base_y].copy()
    rows = region.shape[1]
    phase = 2 * math.pi * t / PERIOD
    for j in range(rows):
        yy = y_top + j
        up = j / max(1, rows)                    # 0 top → 1 base
        env = math.sin(math.pi * up) ** 0.6      # fade at both ends
        amp = (2.0 + 5.0 * up) * env * intensity
        off = int(round(amp * math.sin(0.17 * yy * 2.0 - phase * 2.2)))
        if off:
            arr[x0:x1, yy] = np.roll(region[:, j], off, axis=0)
    del arr                                       # unlock before blitting
    # Faint warm haze over the warp — normal alpha (not additive) so it stays
    # a soft warm breath instead of saturating to white. The shimmer itself
    # is the background warp above; this just warms the air.
    hc = int(hcol)
    tint = pygame.Surface((w, hc), pygame.SRCALPHA)
    for j in range(hc):
        up = j / hc                               # 0 top → 1 base
        a = int(40 * (up ** 1.3) * intensity)
        sway = math.sin(0.10 * (hc - j) - phase * 2.0) * 2.0
        pygame.draw.line(tint, (255, 168, 82, a),
                         (sway, j), (w + sway, j))
    surf.blit(tint, (int(x - w / 2), int(base_y - hc)))


# ── Style 2: wavy rising ribbons ─────────────────────────────────────────────
def style_ribbons(surf, x, base_y, hcol, t, intensity):
    _vent(surf, x, base_y)
    phase = 2 * math.pi * t / PERIOD
    for k in range(3):
        kp = phase + k * 2.1
        amp = 9 + 4 * k
        for j in range(0, int(hcol), 3):
            up = j / max(1, hcol)                 # 0 base → 1 top
            env = math.sin(math.pi * min(1.0, up * 1.05)) ** 0.7
            xx = x + math.sin(3.4 * up + kp - phase * 1.6) * amp * (0.3 + up)
            yy = base_y - j
            col = _lerp_c(HOT, PALE, up)
            r = (4.0 - 2.0 * up) * (0.6 + 0.4 * env)
            _glow(surf, xx, yy, r, col, 150 * env * intensity)


# ── Style 3: ember / particle plume ──────────────────────────────────────────
def style_embers(surf, x, base_y, hcol, t, intensity):
    _vent(surf, x, base_y)
    rng = np.random.RandomState(int(x) * 7 + 13)
    n = 46
    for e in range(n):
        off = rng.rand()
        sway_f = 2.0 + rng.rand() * 3.0
        sway_a = 6 + rng.rand() * 12
        ph = rng.rand() * math.tau
        size = 1.5 + rng.rand() * 2.5
        p = ((t / PERIOD) + off) % 1.0            # 0 just spawned → 1 faded
        yy = base_y - p * hcol
        xx = x + math.sin(p * sway_f * math.pi + ph) * sway_a * p
        flick = 0.6 + 0.4 * math.sin(t * 18 + ph)
        a = 210 * (1.0 - p) * flick * intensity
        col = _lerp_c(HOT, PALE, p)
        _glow(surf, xx, yy, size * (1.2 - 0.7 * p), col, a)
    # Hot base glow where embers are densest.
    _glow(surf, x, base_y - 6, 22, HOT, 120 * intensity)


# ── Style 4: volumetric updraft cone ─────────────────────────────────────────
def style_cone(surf, x, base_y, hcol, t, intensity):
    _vent(surf, x, base_y)
    phase = 2 * math.pi * t / PERIOD
    base_w = 30
    col = pygame.Surface((W, int(hcol)), pygame.SRCALPHA)
    for j in range(int(hcol)):
        up = j / max(1, hcol)                     # 0 base → 1 top
        half = base_w * (1.0 - 0.45 * up)         # taper upward
        vbright = (1.0 - up) ** 1.3
        stri = 0.18 * math.sin(0.10 * j - phase * 2.4)   # rising striations
        yy = int(hcol) - 1 - j
        for side in range(int(half)):
            hb = math.cos((side / max(1, half)) * (math.pi / 2)) ** 1.4
            m = max(0.0, min(1.0, (vbright + stri) * hb)) * intensity
            if m <= 0.02:
                continue
            c = _lerp_c(HOT, PALE, up)
            cc = (min(255, int(c[0] * m)), min(255, int(c[1] * m)),
                  min(255, int(c[2] * m)))
            col.set_at((int(x) + side, yy), (*cc, 255))
            col.set_at((int(x) - side, yy), (*cc, 255))
    surf.blit(col, (0, int(base_y - hcol)), special_flags=pygame.BLEND_ADD)
    # bright rising core spark
    cp = (t / PERIOD) % 1.0
    _glow(surf, x, base_y - cp * hcol, 5, PALE, 180 * intensity)


# ── Style 5: cartoon gust curls ──────────────────────────────────────────────
def _curl(surf, cx, cy, scale, col, outline, a):
    """A bold comma/curl glyph drawn as a thick arc with an outline."""
    rect = pygame.Rect(0, 0, int(22 * scale), int(26 * scale))
    rect.center = (int(cx), int(cy))
    s = pygame.Surface((rect.w + 12, rect.h + 12), pygame.SRCALPHA)
    r2 = pygame.Rect(6, 6, rect.w, rect.h)
    pygame.draw.arc(s, (*outline, a), r2, math.radians(40), math.radians(330),
                    max(6, int(7 * scale)))
    pygame.draw.arc(s, (*col, a), r2, math.radians(45), math.radians(325),
                    max(3, int(4 * scale)))
    surf.blit(s, (rect.x - 6, rect.y - 6))


def style_cartoon(surf, x, base_y, hcol, t, intensity):
    _vent(surf, x, base_y)
    cp = (t / PERIOD)
    n = 4
    for i in range(n):
        p = ((cp + i / n) % 1.0)                  # 0 base → 1 top
        yy = base_y - 10 - p * (hcol - 10)
        xx = x + math.sin(p * 3.0 + i) * 12
        scale = (1.15 - 0.6 * p) * (0.6 + 0.5 * intensity)
        a = int(235 * (1.0 - p) * intensity)
        col = _lerp_c(MID, PALE, p)
        _curl(surf, xx, yy, scale, col, (210, 120, 40), a)


STYLES = [
    ("v1_heat_haze", "1 - Heat-haze refraction", style_haze),
    ("v2_ribbons", "2 - Wavy rising ribbons", style_ribbons),
    ("v3_embers", "3 - Ember / particle plume", style_embers),
    ("v4_cone", "4 - Volumetric updraft cone", style_cone),
    ("v5_cartoon", "5 - Cartoon gust curls", style_cartoon),
]


def _backdrop():
    pal = biome.palette_for_phase(PHASE)
    bucket = int(PHASE * biome.PHASE_BUCKETS)
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal, bucket)
    base = pygame.Surface((W, H)).convert()
    base.blit(sky, (0, 0))
    draw_mountains(base, 600, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    draw_ground(base, GROUND_Y, W, H, 600,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    return base


def main():
    pygame.init()
    pygame.display.set_mode((W, H))
    os.makedirs(OUT_DIR, exist_ok=True)
    base = _backdrop()
    font = pygame.font.Font(None, 26)

    for slug, label, fn in STYLES:
        frames = []
        for i in range(N_FRAMES):
            t = i / FPS
            surf = base.copy()
            fn(surf, 120, GROUND_Y, 212, t, 1.0)      # tall stream
            fn(surf, 252, GROUND_Y, 150, t + 0.5, 0.8)  # shorter, desynced
            cap = font.render(label, True, (255, 255, 255))
            surf.blit(cap, (10, 10))
            data = pygame.image.tostring(surf, "RGB")
            frames.append(Image.frombytes("RGB", (W, H), data))
        gif = os.path.join(OUT_DIR, slug + ".gif")
        frames[0].save(gif, save_all=True, append_images=frames[1:],
                       duration=int(1000 / FPS), loop=0, optimize=True)
        frames[len(frames) // 2].save(os.path.join(OUT_DIR, slug + ".png"))
        print("wrote", gif)


if __name__ == "__main__":
    main()
