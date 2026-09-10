"""Faintness sweep for the two finalist wind-geyser looks (M2 flow-streaks,
M4 steam column). Renders 5 opacity levels of each as STATIC posters and
tiles them into one comparison figure for easy side-by-side picking:

    python tools/sketch_geyser_faintness.py

Output: docs/screenshots/geyser_windmotion/faintness_compare.png
Throwaway design sketch. Top row = M2 streaks, bottom row = M4 steam,
faint → bold left → right. The number is the alpha-scale vs the current
build (1.0x = what's on the branch now).
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
    _backdrop, _vent, STREAMS, FPS, N_FRAMES,
    render_streaks, render_steam,
)

OUT = os.path.join(ROOT, "docs", "screenshots", "geyser_windmotion",
                   "faintness_compare.png")
GIF = os.path.join(ROOT, "docs", "screenshots", "geyser_windmotion",
                   "faintness_compare.gif")

ROWS = [
    ("M2 streaks", render_streaks, (1.0, 1.175, 1.35, 1.525, 1.7)),
    ("M4 steam", render_steam, (1.0, 1.3, 1.6, 1.9, 2.2)),
]


def _panel(base, font, fn, scale, label, t):
    scene = base.copy()
    for (x, by, h, inten) in STREAMS:
        _vent(scene, x)
    fn(scene, STREAMS, t, scale)
    sh = font.render(label, True, (0, 0, 0)); scene.blit(sh, (9, 9))
    tx = font.render(label, True, (255, 255, 255)); scene.blit(tx, (8, 8))
    return Image.frombytes("RGB", (W, H), pygame.image.tostring(scene, "RGB"))


def _sheet(base, font, t):
    gap = 8
    cols = max(len(s) for _, _, s in ROWS)
    img = Image.new("RGB", (W * cols + gap * (cols - 1),
                            H * len(ROWS) + gap * (len(ROWS) - 1)),
                    (18, 18, 24))
    for r, (name, fn, scales) in enumerate(ROWS):
        for c, scale in enumerate(scales):
            panel = _panel(base, font, fn, scale, "%s  %.3gx" % (name, scale), t)
            img.paste(panel, (c * (W + gap), r * (H + gap)))
    return img


def main():
    pygame.init()
    pygame.display.set_mode((W, H))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    base = _backdrop()
    font = pygame.font.Font(None, 24)
    # static poster (mid-frame)
    _sheet(base, font, (N_FRAMES // 2) / FPS).save(OUT)
    print("wrote", OUT)
    # animated version: same grid, every cell looping
    frames = []
    for i in range(N_FRAMES):
        s = _sheet(base, font, i / FPS)
        s = s.resize((s.width // 2, s.height // 2))   # halve for a sane GIF size
        frames.append(s)
        print("frame %d/%d" % (i + 1, N_FRAMES))
    frames[0].save(GIF, save_all=True, append_images=frames[1:],
                   duration=int(1000 / FPS), loop=0, optimize=True)
    print("wrote", GIF)


if __name__ == "__main__":
    main()
