"""Render a one-off review image of 5 `$` glyph treatments on the gold coin.

Same layout as tools/dollar_icon_preview.py — five cells in one row at 3×
in-game scale with labels and a numeric tag. Writes
docs/dollar_coin_variants.png. Review-only; not a game asset.

Run:
    python tools/dollar_coin_preview.py
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

from game.config import MUSHROOM_R
from game.dollar_coin_glyphs import VARIANTS
from game.draw import UI_GOLD, UI_CREAM, NEAR_BLACK, lerp_color

OUT = pathlib.Path(__file__).parent.parent / "docs" / "dollar_coin_variants.png"

CELL_W = 144
CELL_H = 200
SCALE = 3
ROW_PAD_TOP = 56
LABEL_Y = 168


def _font(size, bold=True):
    asset_dir = pathlib.Path(__file__).parent.parent / "game" / "assets"
    path = str(asset_dir / ("LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"))
    return pygame.font.Font(path, size)


def _draw_centered(surf, text, center, size, color, bold=True):
    f = _font(size, bold)
    img = f.render(text, True, color)
    sh = f.render(text, True, NEAR_BLACK)
    r = img.get_rect(center=center)
    surf.blit(sh, (r.x + 2, r.y + 2))
    surf.blit(img, r.topleft)


def render_cell(name, draw_fn, index):
    cell = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
    plate_rect = pygame.Rect(8, 12, CELL_W - 16, 132)
    plate = pygame.Surface(plate_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(plate, (15, 25, 60, 220), plate.get_rect(), border_radius=14)
    pygame.draw.rect(plate, (60, 90, 160, 255), plate.get_rect(), 1, border_radius=14)
    cell.blit(plate, plate_rect.topleft)

    native_size = MUSHROOM_R * 4
    icon = pygame.Surface((native_size, native_size), pygame.SRCALPHA)
    draw_fn(icon, native_size // 2, native_size // 2, pulse=0.8)
    big = pygame.transform.smoothscale(icon, (native_size * SCALE // 2,
                                              native_size * SCALE // 2))
    cell.blit(big, big.get_rect(center=(CELL_W // 2, ROW_PAD_TOP + 38)).topleft)

    _draw_centered(cell, f"{index + 1}", (24, 28), 18, UI_GOLD)
    _draw_centered(cell, name, (CELL_W // 2, LABEL_Y), 16, UI_CREAM)
    return cell


def main():
    cols = len(VARIANTS)
    out_w = CELL_W * cols
    out_h = CELL_H + 40

    surf = pygame.Surface((out_w, out_h))
    for y in range(out_h):
        t = y / max(1, out_h - 1)
        c = lerp_color((18, 28, 64), (8, 14, 36), t)
        pygame.draw.line(surf, c, (0, y), (out_w - 1, y))

    _draw_centered(surf, "Skybit — coin $-glyph treatments",
                   (out_w // 2, 22), 18, UI_GOLD)

    for i, (name, fn) in enumerate(VARIANTS):
        cell = render_cell(name, fn, i)
        surf.blit(cell, (i * CELL_W, 36))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, OUT)
    print(f"wrote {OUT}  ({out_w}x{out_h}, {cols} variants)")


if __name__ == "__main__":
    main()
