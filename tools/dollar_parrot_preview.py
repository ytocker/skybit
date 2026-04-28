"""Render a one-off review image of 5 dollar-glasses parrot variants.

Each cell shows the parrot at level-wing pose (clearest view of the glasses)
scaled 2× from the native 64×60 sprite. Writes docs/dollar_parrot_variants.png.
Review-only; not a game asset.

Run:
    python tools/dollar_parrot_preview.py
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

from game.dollar_parrot_glasses import VARIANTS, build_dollar_frames
from game.draw import UI_GOLD, UI_CREAM, NEAR_BLACK, lerp_color

OUT = pathlib.Path(__file__).parent.parent / "docs" / "dollar_parrot_variants.png"

CELL_W   = 190
CELL_H   = 220
SCALE    = 2
LABEL_Y  = 200
# Wing frame index 2 = level wing (-10°) — best view of the glasses
WING_IDX = 2


def _font(size, bold=True):
    asset_dir = pathlib.Path(__file__).parent.parent / "game" / "assets"
    path = str(asset_dir / ("LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"))
    return pygame.font.Font(path, size)


def _draw_centered(surf, text, center, size, color, bold=True):
    f = _font(size, bold)
    img = f.render(text, True, color)
    sh  = f.render(text, True, NEAR_BLACK)
    r   = img.get_rect(center=center)
    surf.blit(sh,  (r.x + 2, r.y + 2))
    surf.blit(img,  r.topleft)


def render_cell(name, glasses_fn, index):
    cell = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)

    # Plate backdrop
    plate_rect = pygame.Rect(8, 12, CELL_W - 16, CELL_H - 40)
    plate = pygame.Surface(plate_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(plate, (15, 25, 60, 220), plate.get_rect(), border_radius=14)
    pygame.draw.rect(plate, (60, 90, 160, 255), plate.get_rect(), 1, border_radius=14)
    cell.blit(plate, plate_rect.topleft)

    # Build and scale the parrot frame
    frames = build_dollar_frames(glasses_fn)
    native = frames[WING_IDX]
    nw, nh = native.get_size()
    big = pygame.transform.smoothscale(native, (nw * SCALE, nh * SCALE))
    cell.blit(big, big.get_rect(center=(CELL_W // 2, CELL_H // 2 - 14)).topleft)

    # Numeric tag
    _draw_centered(cell, f"{index + 1}", (24, 28), 18, UI_GOLD)
    # Label
    _draw_centered(cell, name, (CELL_W // 2, LABEL_Y), 15, UI_CREAM)
    return cell


def main():
    cols  = len(VARIANTS)
    out_w = CELL_W * cols
    out_h = CELL_H + 44

    surf = pygame.Surface((out_w, out_h))
    for y in range(out_h):
        t = y / max(1, out_h - 1)
        c = lerp_color((18, 28, 64), (8, 14, 36), t)
        pygame.draw.line(surf, c, (0, y), (out_w - 1, y))

    _draw_centered(surf, "Skybit — triple parrot dollar-glasses variants",
                   (out_w // 2, 22), 17, UI_GOLD)

    for i, (name, fn) in enumerate(VARIANTS):
        cell = render_cell(name, fn, i)
        surf.blit(cell, (i * CELL_W, 36))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, OUT)
    print(f"wrote {OUT}  ({out_w}x{out_h}, {cols} variants)")


if __name__ == "__main__":
    main()
