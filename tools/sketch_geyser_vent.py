"""Redesign the geyser VENT (the hole the hot air rises from) into something
that actually reads as a geyser. Renders 5 grounded variants — each shown
with the locked steam rising AND as a magnified bare crop — into one
comparison poster + a looping GIF under docs/screenshots/geyser_vent/:

    python tools/sketch_geyser_vent.py

Throwaway design sketch (game code untouched until a pick). Variants span
neutral↔colorful and flat↔raised:
    V1 sinter cone        - pale geyserite mini-volcano, wet throat, cracks
    V2 terraced sinter    - stepped mineral tiers (Mammoth-style), pink tint
    V3 blue thermal pool  - steep blue→turquoise pool, wet lip, ripple
    V4 bacterial-mat spring- concentric orange→amber→green thermophile rings
    V5 cracked rocky fissure- rugged dark boulder rim around a glowing throat

Real-geyser references: sinter cones/terraces/eggs (pale silica, pink iron
oxide, grey pyrite), near-boiling blue pools, thermophile mat colours.
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

import pygame
from PIL import Image

from game.config import W, H, GROUND_Y
from tools.sketch_geyser_cone import _backdrop, _blur, _lerp_c, _sc, FPS, N_FRAMES, PERIOD
from tools.sketch_geyser_wind import _stamp
from tools.sketch_geyser_windmotion import render_steam

OUT = os.path.join(ROOT, "docs", "screenshots", "geyser_vent")


def _ell(scene, cx, cy, rx, ry, color, alpha=255, blur=0):
    rx, ry = max(1, int(rx)), max(1, int(ry))
    s = pygame.Surface((rx * 2 + 4, ry * 2 + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (int(color[0]), int(color[1]), int(color[2]),
                            int(alpha)), (2, 2, rx * 2, ry * 2))
    if blur:
        s = _blur(s, blur)
    scene.blit(s, (int(cx - rx - 2), int(cy - ry - 2)))


# ── V1: sinter cone (raised, neutral) ────────────────────────────────────────
def vent_cone(scene, x, base_y, t):
    LO, HI = (168, 156, 136), (236, 230, 214)
    coneH = 15
    for k in range(coneH + 1):
        u = k / coneH
        _ell(scene, x, base_y - k, 40 - 9 * u, 12 - 4 * u,
             _lerp_c(LO, HI, u * 0.8))
    top = base_y - coneH
    _ell(scene, x, top, 31, 8, HI)
    _ell(scene, x, top + 1, 25, 6, (60, 50, 44))          # wet throat
    _ell(scene, x, top + 1, 19, 4, (34, 27, 23))
    _stamp(scene, x - 15, top + 3, 16, (255, 250, 240), 70)   # warm-lit left
    _stamp(scene, x + 17, base_y - 3, 15, (54, 38, 30), 60)   # shadow right
    for dxs in (-16, -6, 6, 16):                          # drip cracks
        pygame.draw.line(scene, (126, 114, 96),
                         (int(x + dxs), top + 6),
                         (int(x + dxs * 1.08), base_y - 3), 1)
    return top + 1


# ── V2: terraced sinter (raised, neutral-pink) ───────────────────────────────
def vent_terraced(scene, x, base_y, t):
    LO, HI = (184, 162, 158), (238, 226, 216)
    specs = [(42, 12, 0), (34, 10, 4), (26, 8, 8), (19, 6, 11)]
    n = len(specs)
    for i, (rx, ry, dy) in enumerate(specs):
        u = i / (n - 1)
        col = _lerp_c(LO, HI, u)
        yy = base_y - dy
        _ell(scene, x, yy, rx, ry, col)
        _ell(scene, x, yy - 1, rx - 2, max(1, ry - 3),
             _lerp_c(col, (255, 250, 244), 0.5), alpha=170)   # wet ledge
    _ell(scene, x, base_y - 12, 15, 4, (72, 54, 54))
    _ell(scene, x, base_y - 12, 11, 3, (40, 28, 30))
    _stamp(scene, x - 16, base_y - 6, 14, (255, 248, 240), 60)
    _stamp(scene, x + 18, base_y - 2, 14, (70, 48, 48), 55)
    return base_y - 12


# ── V3: blue thermal pool (flat, colorful) ───────────────────────────────────
def vent_pool(scene, x, base_y, t):
    _ell(scene, x, base_y, 42, 13, (54, 48, 46))          # wet stone rim
    _ell(scene, x, base_y - 1, 40, 12, (74, 66, 60))      # lit lip
    for rx, ry, col in [(36, 10, (118, 202, 196)), (30, 8, (40, 140, 150)),
                        (22, 6, (26, 96, 120)), (14, 4, (16, 60, 86))]:
        _ell(scene, x, base_y - 1, rx, ry, col, blur=1)
    ph = 2 * math.pi * t / PERIOD
    _stamp(scene, x - 6 + 5 * math.sin(ph), base_y - 3,
           5, (200, 245, 240), 120)                       # moving ripple
    _stamp(scene, x - 16, base_y - 4, 10, (220, 250, 248), 95)  # gloss
    return base_y - 2


# ── V4: bacterial-mat spring (flat, very colorful) ───────────────────────────
def vent_mats(scene, x, base_y, t):
    for rx, ry, col in [(44, 13, (110, 150, 78)), (37, 11, (152, 172, 80)),
                        (31, 9, (228, 182, 82)), (24, 7, (214, 120, 50)),
                        (17, 5, (150, 70, 40))]:
        _ell(scene, x, base_y - 1, rx, ry, col, blur=1)
    _ell(scene, x, base_y - 1, 11, 3, (40, 30, 28))       # throat
    _stamp(scene, x - 14, base_y - 4, 10, (255, 250, 235), 85)   # gloss
    return base_y - 2


# ── V5: cracked rocky fissure (raised, rugged) ───────────────────────────────
def vent_fissure(scene, x, base_y, t):
    glow = 100 + 35 * math.sin(2 * math.pi * t / PERIOD)
    _ell(scene, x, base_y - 3, 27, 8, (28, 20, 18))          # dark throat
    _stamp(scene, x, base_y - 5, 18, (255, 150, 70), glow)   # hot glow on top
    _stamp(scene, x, base_y - 6, 10, (255, 210, 140), glow)
    n = 9
    rocks = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rocks.append((x + math.cos(a) * 39, base_y - 3 + math.sin(a) * 10,
                      8 + (i % 3) * 2, 7 + (i % 2) * 2))
    for bx, by, rw, rh in sorted(rocks, key=lambda r: r[1]):   # back→front
        _ell(scene, bx, by, rw, rh, (58, 52, 48))
        _ell(scene, bx - 2, by - 2, rw * 0.6, rh * 0.6, (98, 90, 82))
        _stamp(scene, bx - 1, by - 2, 2, (152, 144, 132), 120)
    return base_y - 4


VARIANTS = [
    ("v1_cone", "V1 - Sinter cone", vent_cone),
    ("v2_terraced", "V2 - Terraced sinter", vent_terraced),
    ("v3_pool", "V3 - Blue thermal pool", vent_pool),
    ("v4_mats", "V4 - Bacterial mats", vent_mats),
    ("v5_fissure", "V5 - Cracked fissure", vent_fissure),
]

CX = W // 2
CROP = (CX - 60, GROUND_Y - 44, 120, 56)       # magnified bare-vent crop
CROP_SCALE = 3


def _full(base, font, fn, label, t):
    scene = base.copy()
    mouth_y = fn(scene, CX, GROUND_Y, t)
    render_steam(scene, [(CX, mouth_y, 236, 1.0)], t)
    sh = font.render(label, True, (0, 0, 0)); scene.blit(sh, (9, 9))
    tx = font.render(label, True, (255, 255, 255)); scene.blit(tx, (8, 8))
    return Image.frombytes("RGB", (W, H), pygame.image.tostring(scene, "RGB"))


def _crop(base, fn):
    scene = base.copy()
    fn(scene, CX, GROUND_Y, (N_FRAMES // 2) / FPS)
    img = Image.frombytes("RGB", (W, H), pygame.image.tostring(scene, "RGB"))
    cx, cy, cw, ch = CROP
    return img.crop((cx, cy, cx + cw, cy + ch)).resize(
        (cw * CROP_SCALE, ch * CROP_SCALE), Image.NEAREST)


def main():
    pygame.init()
    pygame.display.set_mode((W, H))
    os.makedirs(OUT, exist_ok=True)
    base = _backdrop()
    font = pygame.font.Font(None, 24)
    gap = 8
    cw = CROP[2] * CROP_SCALE
    top = [_full(base, font, fn, lbl, (N_FRAMES // 2) / FPS)
           for _, lbl, fn in VARIANTS]
    bot = [_crop(base, fn) for _, _, fn in VARIANTS]
    cols = len(VARIANTS)
    sheet_w = max(W, cw) * cols + gap * (cols - 1)
    bh = bot[0].height
    sheet = Image.new("RGB", (sheet_w, H + gap + bh), (18, 18, 24))
    step = max(W, cw) + gap
    for c in range(cols):
        sheet.paste(top[c], (c * step + (max(W, cw) - W) // 2, 0))
        sheet.paste(bot[c], (c * step + (max(W, cw) - cw) // 2, H + gap))
    sheet.save(os.path.join(OUT, "vent_compare.png"))
    print("wrote vent_compare.png")
    # animated top row
    frames = []
    for i in range(N_FRAMES):
        t = i / FPS
        row = Image.new("RGB", (W * cols + gap * (cols - 1), H), (18, 18, 24))
        for c, (_, lbl, fn) in enumerate(VARIANTS):
            row.paste(_full(base, font, fn, lbl, t), (c * (W + gap), 0))
        frames.append(row.resize((row.width // 2, row.height // 2)))
        print("frame %d/%d" % (i + 1, N_FRAMES))
    frames[0].save(os.path.join(OUT, "vent_compare.gif"), save_all=True,
                   append_images=frames[1:], duration=int(1000 / FPS),
                   loop=0, optimize=True)
    print("wrote vent_compare.gif")


if __name__ == "__main__":
    main()
