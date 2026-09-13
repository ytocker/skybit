"""Render 5 separate review images, one per ghost-parrot variant.

Each file shows the parrot at level-wing pose with the ghost
transformation applied. Writes docs/dollar_parrot_ghost_<slug>.png at
5x scale on a navy backdrop.

Run:
    python tools/dollar_parrot_ghost_preview.py
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

from game.dollar_parrot_ghost import VARIANTS, build_ghost_variant_frames
from game.draw import UI_GOLD, NEAR_BLACK, lerp_color

OUT_DIR  = pathlib.Path(__file__).parent.parent / "docs"
SCALE    = 5
WING_IDX = 2          # level wing — clearest, calmest pose for review
PAD      = 24


def _font(size, bold=True):
    asset_dir = pathlib.Path(__file__).parent.parent / "game" / "assets"
    name = "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"
    return pygame.font.Font(str(asset_dir / name), size)


def _draw_centered(surf, text, center, size, color):
    f   = _font(size, True)
    img = f.render(text, True, color)
    sh  = f.render(text, True, NEAR_BLACK)
    r   = img.get_rect(center=center)
    surf.blit(sh,  (r.x + 2, r.y + 2))
    surf.blit(img, r.topleft)


def render_variant(name: str, build_fn) -> pygame.Surface:
    frames = build_ghost_variant_frames(build_fn)
    native = frames[WING_IDX]
    nw, nh = native.get_size()
    big    = pygame.transform.scale(native, (nw * SCALE, nh * SCALE))
    bw, bh = big.get_size()

    out_w = bw + PAD * 2
    out_h = bh + PAD * 2 + 50

    surf = pygame.Surface((out_w, out_h))
    for y in range(out_h):
        t = y / max(1, out_h - 1)
        c = lerp_color((18, 28, 64), (8, 14, 36), t)
        pygame.draw.line(surf, c, (0, y), (out_w - 1, y))

    surf.blit(big, ((out_w - bw) // 2, PAD))
    _draw_centered(surf, f"Skybit — ghost parrot — {name}",
                   (out_w // 2, out_h - 24), 22, UI_GOLD)
    return surf


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, fn in VARIANTS:
        surf = render_variant(name, fn)
        slug = name.lower()
        out  = OUT_DIR / f"dollar_parrot_ghost_{slug}.png"
        pygame.image.save(surf, out)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
