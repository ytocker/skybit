"""Column-density sweep for the chosen M4 steam look (opacity locked at 1.4x).
Renders 5 versions from the original column count up to much denser, as a
single-row STATIC poster and one looping GIF for easy comparison:

    python tools/sketch_geyser_columns.py

Outputs under docs/screenshots/geyser_windmotion/:
    columns_compare.png   columns_compare.gif

Throwaway design sketch. Left = original 6 columns, right = densest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from PIL import Image

from game.config import W, H
from tools.sketch_geyser_windmotion import (
    _backdrop, _vent, STREAMS, FPS, N_FRAMES, render_steam,
)

OUT = os.path.join(ROOT, "docs", "screenshots", "geyser_windmotion",
                   "columns_compare.png")
GIF = os.path.join(ROOT, "docs", "screenshots", "geyser_windmotion",
                   "columns_compare.gif")

NCOLS = (6, 9, 13, 18, 24)                     # original → densest


def _panel(base, font, ncols, t):
    scene = base.copy()
    for (x, by, h, inten) in STREAMS:
        _vent(scene, x)
    render_steam(scene, STREAMS, t, 1.0, ncols)
    label = "M4 1.4x  %d cols" % ncols
    sh = font.render(label, True, (0, 0, 0)); scene.blit(sh, (9, 9))
    tx = font.render(label, True, (255, 255, 255)); scene.blit(tx, (8, 8))
    return Image.frombytes("RGB", (W, H), pygame.image.tostring(scene, "RGB"))


def _sheet(base, font, t):
    gap = 8
    img = Image.new("RGB", (W * len(NCOLS) + gap * (len(NCOLS) - 1), H),
                    (18, 18, 24))
    for c, ncols in enumerate(NCOLS):
        img.paste(_panel(base, font, ncols, t), (c * (W + gap), 0))
    return img


def main():
    pygame.init()
    pygame.display.set_mode((W, H))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    base = _backdrop()
    font = pygame.font.Font(None, 24)
    _sheet(base, font, (N_FRAMES // 2) / FPS).save(OUT)
    print("wrote", OUT)
    frames = []
    for i in range(N_FRAMES):
        s = _sheet(base, font, i / FPS)
        frames.append(s.resize((s.width // 2, s.height // 2)))
        print("frame %d/%d" % (i + 1, N_FRAMES))
    frames[0].save(GIF, save_all=True, append_images=frames[1:],
                   duration=int(1000 / FPS), loop=0, optimize=True)
    print("wrote", GIF)


if __name__ == "__main__":
    main()
