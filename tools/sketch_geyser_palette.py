"""Colour-coordination study for the chosen sinter-cone vent + scattered
rocks. Five palettes where the cone and the rocks share a tone:

    V1  rocks recoloured to match the cone (pale sinter)
    V2  cone recoloured to match the rocks (dark stone)
    V3  rust / iron-oxide
    V4  slate basalt (cool blue-grey)
    V5  ochre / sulfur

Renders one animated comparison GIF (+ static poster) under
docs/screenshots/geyser_vent/:

    python tools/sketch_geyser_palette.py

Throwaway design sketch — game code untouched.
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

from game.config import W, H, GROUND_Y
from tools.sketch_geyser_cone import _backdrop, _lerp_c, _sc, FPS, N_FRAMES
from tools.sketch_geyser_wind import _stamp
from tools.sketch_geyser_windmotion import render_steam
from tools.sketch_geyser_vent import _ell
from tools.sketch_geyser_scene import ROCKS, CX

OUT = os.path.join(ROOT, "docs", "screenshots", "geyser_vent")


def _cone(scene, x, base_y, t, pal):
    LO, HI = pal["cone_lo"], pal["cone_hi"]
    coneH = 15
    for k in range(coneH + 1):
        u = k / coneH
        _ell(scene, x, base_y - k, 40 - 9 * u, 12 - 4 * u, _lerp_c(LO, HI, u * 0.8))
    top = base_y - coneH
    _ell(scene, x, top, 31, 8, HI)
    th = pal["throat"]
    _ell(scene, x, top + 1, 25, 6, th)
    _ell(scene, x, top + 1, 19, 4, _sc(th, 0.6))
    _stamp(scene, x - 15, top + 3, 16, (255, 250, 240), 70)      # lit left
    _stamp(scene, x + 17, base_y - 3, 15, _sc(LO, 0.4), 60)      # shadow right
    for dxs in (-16, -6, 6, 16):
        pygame.draw.line(scene, pal["crack"], (int(x + dxs), top + 6),
                         (int(x + dxs * 1.08), base_y - 3), 1)
    return top + 1


def _rock(scene, bx, by, rw, rh, pal):
    _ell(scene, bx + 1, by + rh * 0.7, rw * 1.05, max(2, rh * 0.5),
         (34, 48, 22), alpha=85)                                 # grass shadow
    _ell(scene, bx, by, rw, rh, pal["rock_body"])
    _ell(scene, bx - rw * 0.18, by - rh * 0.22, rw * 0.6, rh * 0.6,
         pal["rock_facet"])
    _stamp(scene, bx - 1, by - rh * 0.3, 2, pal["rock_speck"], 120)


PALETTES = [
    ("v1_rocks_to_sinter", "V1 - Rocks match cone (sinter)", dict(
        cone_lo=(168, 156, 136), cone_hi=(236, 230, 214), throat=(60, 50, 44),
        crack=(126, 114, 96), rock_body=(150, 140, 122),
        rock_facet=(214, 206, 188), rock_speck=(92, 82, 68))),
    ("v2_cone_to_dark", "V2 - Cone matches rocks (dark)", dict(
        cone_lo=(58, 52, 48), cone_hi=(112, 104, 96), throat=(24, 20, 18),
        crack=(40, 34, 30), rock_body=(58, 52, 48),
        rock_facet=(98, 90, 82), rock_speck=(152, 144, 132))),
    ("v3_rust", "V3 - Rust / iron-oxide", dict(
        cone_lo=(150, 92, 66), cone_hi=(216, 152, 114), throat=(58, 28, 20),
        crack=(110, 64, 44), rock_body=(96, 52, 38),
        rock_facet=(154, 96, 68), rock_speck=(206, 154, 112))),
    ("v4_basalt", "V4 - Slate basalt", dict(
        cone_lo=(96, 108, 124), cone_hi=(172, 184, 200), throat=(28, 36, 48),
        crack=(64, 74, 90), rock_body=(54, 64, 78),
        rock_facet=(106, 118, 136), rock_speck=(162, 174, 192))),
    ("v5_ochre", "V5 - Ochre / sulfur", dict(
        cone_lo=(170, 150, 70), cone_hi=(230, 216, 122), throat=(70, 58, 24),
        crack=(120, 104, 50), rock_body=(110, 96, 40),
        rock_facet=(178, 162, 82), rock_speck=(222, 208, 132))),
]


def _full(base, font, pal, label, t):
    scene = base.copy()
    for bx, by, rw, rh in ROCKS:
        _rock(scene, bx, by, rw, rh, pal)
    mouth_y = _cone(scene, CX, GROUND_Y, t, pal)
    render_steam(scene, [(CX, mouth_y, 236, 1.0)], t)
    sh = font.render(label, True, (0, 0, 0)); scene.blit(sh, (9, 9))
    tx = font.render(label, True, (255, 255, 255)); scene.blit(tx, (8, 8))
    return Image.frombytes("RGB", (W, H), pygame.image.tostring(scene, "RGB"))


def main():
    pygame.init()
    pygame.display.set_mode((W, H))
    os.makedirs(OUT, exist_ok=True)
    base = _backdrop()
    font = pygame.font.Font(None, 24)
    gap = 8
    n = len(PALETTES)

    def sheet(t):
        img = Image.new("RGB", (W * n + gap * (n - 1), H), (18, 18, 24))
        for c, (_, lbl, pal) in enumerate(PALETTES):
            img.paste(_full(base, font, pal, lbl, t), (c * (W + gap), 0))
        return img

    sheet((N_FRAMES // 2) / FPS).save(os.path.join(OUT, "palette_compare.png"))
    print("wrote palette_compare.png")
    frames = []
    for i in range(N_FRAMES):
        s = sheet(i / FPS)
        frames.append(s.resize((s.width // 2, s.height // 2)))
        print("frame %d/%d" % (i + 1, N_FRAMES))
    frames[0].save(os.path.join(OUT, "palette_compare.gif"), save_all=True,
                   append_images=frames[1:], duration=int(1000 / FPS),
                   loop=0, optimize=True)
    print("wrote palette_compare.gif")


if __name__ == "__main__":
    main()
