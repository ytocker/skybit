"""Composition test: the chosen V1 sinter-cone vent PLUS scattered individual
rocks (lifted from the V5 fissure) strewn across the grass to add ground
atmosphere. Renders a static poster + a looping GIF (steam animating) under
docs/screenshots/geyser_vent/:

    python tools/sketch_geyser_scene.py

Throwaway design sketch — game code untouched.
"""
from __future__ import annotations

import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from PIL import Image

from game.config import W, H, GROUND_Y
from tools.sketch_geyser_cone import _backdrop, FPS, N_FRAMES
from tools.sketch_geyser_wind import _stamp
from tools.sketch_geyser_windmotion import render_steam
from tools.sketch_geyser_vent import vent_cone, _ell

OUT = os.path.join(ROOT, "docs", "screenshots", "geyser_vent")
CX = W // 2


def _rock(scene, bx, by, rw, rh):
    _ell(scene, bx + 1, by + rh * 0.7, rw * 1.05, max(2, rh * 0.5),
         (34, 48, 22), alpha=85)                          # contact shadow
    _ell(scene, bx, by, rw, rh, (58, 52, 48))
    _ell(scene, bx - rw * 0.18, by - rh * 0.22, rw * 0.6, rh * 0.6,
         (98, 90, 82))                                    # lit top-left facet
    _stamp(scene, bx - 1, by - rh * 0.3, 2, (152, 144, 132), 120)  # crust speck


def _scatter():
    """Deterministic rocks across the grass, clear of the vent + steam base."""
    rng = random.Random(7)
    rocks = []
    while len(rocks) < 13:
        x = rng.uniform(12, W - 12)
        if abs(x - CX) < 46:                              # keep the vent clear
            continue
        by = GROUND_Y + rng.uniform(0, 7)
        rw = rng.uniform(3.0, 8.5)
        rocks.append((x, by, rw, rw * rng.uniform(0.7, 0.85)))
        if rng.random() < 0.45:                           # occasional pebble pal
            rocks.append((x + rng.uniform(-12, 12), by + rng.uniform(-2, 3),
                          rw * 0.5, rw * 0.42))
    return sorted(rocks, key=lambda r: r[1])              # back → front


ROCKS = _scatter()


def _frame(base, t):
    scene = base.copy()
    for bx, by, rw, rh in ROCKS:
        _rock(scene, bx, by, rw, rh)
    mouth_y = vent_cone(scene, CX, GROUND_Y, t)
    render_steam(scene, [(CX, mouth_y, 236, 1.0)], t)
    return Image.frombytes("RGB", (W, H), pygame.image.tostring(scene, "RGB"))


def main():
    pygame.init()
    pygame.display.set_mode((W, H))
    os.makedirs(OUT, exist_ok=True)
    base = _backdrop()
    _frame(base, (N_FRAMES // 2) / FPS).save(os.path.join(OUT, "cone_rocks.png"))
    print("wrote cone_rocks.png")
    frames = [_frame(base, i / FPS) for i in range(N_FRAMES)]
    frames[0].save(os.path.join(OUT, "cone_rocks.gif"), save_all=True,
                   append_images=frames[1:], duration=int(1000 / FPS),
                   loop=0, optimize=True)
    print("wrote cone_rocks.gif")


if __name__ == "__main__":
    main()
