"""Render 5 separate review images, one per surprise-box gift-wrap variant.

Each file shows a single wrapped present on a navy backdrop at 6× scale
so the detail is legible. Writes docs/surprise_box_<slug>.png.

Run:
    python tools/surprise_box_preview.py
"""
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.surprise_box_variants import VARIANTS
from game.draw import UI_GOLD, NEAR_BLACK, lerp_color

OUT_DIR = pathlib.Path(__file__).parent.parent / "docs"
SCALE   = 5
NATIVE  = 64
PAD     = 28


def _font(size):
    asset_dir = pathlib.Path(__file__).parent.parent / "game" / "assets"
    return pygame.font.Font(str(asset_dir / "LiberationSans-Bold.ttf"), size)


def _draw_centered(surf, text, center, size, color):
    f   = _font(size)
    img = f.render(text, True, color)
    sh  = f.render(text, True, NEAR_BLACK)
    r   = img.get_rect(center=center)
    surf.blit(sh,  (r.x + 2, r.y + 2))
    surf.blit(img, r.topleft)


def render_variant(name: str, draw_fn) -> pygame.Surface:
    native = pygame.Surface((NATIVE, NATIVE), pygame.SRCALPHA)
    draw_fn(native, NATIVE // 2, NATIVE // 2)
    big    = pygame.transform.scale(native, (NATIVE * SCALE, NATIVE * SCALE))
    bw, bh = big.get_size()

    out_w = max(bw + PAD * 2, 320)
    out_h = bh + PAD * 2 + 50

    surf = pygame.Surface((out_w, out_h))
    for y in range(out_h):
        t = y / max(1, out_h - 1)
        c = lerp_color((18, 28, 64), (8, 14, 36), t)
        pygame.draw.line(surf, c, (0, y), (out_w - 1, y))

    surf.blit(big, ((out_w - bw) // 2, PAD))
    _draw_centered(surf, f"Skybit — gift box — {name}",
                   (out_w // 2, out_h - 24), 20, UI_GOLD)
    return surf


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, fn in VARIANTS:
        surf = render_variant(name, fn)
        slug = name.lower()
        out  = OUT_DIR / f"surprise_box_{slug}.png"
        pygame.image.save(surf, out)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
