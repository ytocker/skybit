"""DESIGN PICK: 5 distinctive snow-BUILDUP orders. The flake SET
(and the max-weather frame) is unchanged — only the ORDER flakes
activate as the storm builds differs, so the snow coats the
perimeter first and then piles up / wraps inward, instead of
popping in mid-body.

Each option just RE-SORTS game.entities._build_snow_pool() by a
different fill-rank, sets _SNOW_POOL, and renders Pip via Bird.draw
at several loads — the exact shipped activation (first-K by load +
load-scaled flake size). Renders a 5-row (options) x 4-col (loads)
key-frame grid.

Output: docs/screenshots/wind_themes/snow_back/buildup_order_sheet.png

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
      python -m tools.render_buildup_order
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import game.entities as E
from game.entities import Bird

pygame.init()
pygame.display.set_mode((360, 640))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "wind_themes", "snow_back")
os.makedirs(OUT_DIR, exist_ok=True)

LOADS = [0.18, 0.40, 0.65, 1.00]


def fill_ranks(pool):
    """Return {label: keyfn}. dy = signed distance below the snow
    line: ~0 perimeter edge, <0 piled height, >0 into the body.
    All key primarily on |dy| so each STARTS as a thin perimeter
    coat; they differ in how they then expand. Lower = earlier."""
    xs = [p[0] for p in pool]
    xmin, xmax = min(xs), max(xs)
    xr = (xmax - xmin) or 1.0

    def edge_out(p):
        x, y, dy, w = p
        return abs(dy)

    def pile_up(p):                       # height before depth
        x, y, dy, w = p
        return abs(dy) * 0.7 if dy < 0 else dy * 2.0

    def sink_in(p):                       # into the body before height
        x, y, dy, w = p
        return dy * 0.7 if dy > 0 else abs(dy) * 2.0

    def windward(p):                      # perimeter rear -> front
        x, y, dy, w = p
        return abs(dy) + ((x - xmin) / xr) * 4.0

    def patchy(p):                        # windward high-spots seed first
        x, y, dy, w = p
        return abs(dy) * 1.3 - w * 3.0

    return [
        ("1  EDGE-OUT (even)", edge_out),
        ("2  PILE-UP (height first)", pile_up),
        ("3  SINK-IN (depth first)", sink_in),
        ("4  WINDWARD sweep", windward),
        ("5  PATCHY (organic)", patchy),
    ]


def render_pip(pool, load, zoom):
    E._SNOW_POOL = pool
    b = Bird()
    b.x = 34
    b.y = 32
    b.vy = 0
    b.snow_load = load
    cell = pygame.Surface((68, 64), pygame.SRCALPHA)
    b.draw(cell, 0, 0)
    return pygame.transform.scale(cell, (68 * zoom, 64 * zoom))


def main():
    base = E._build_snow_pool()
    options = fill_ranks(base)

    Z = 4
    pw, ph = 68 * Z, 64 * Z
    left = 150
    top = 30
    cell_pad = 6
    sheet_w = left + len(LOADS) * (pw + cell_pad) + cell_pad
    sheet_h = top + len(options) * (ph + cell_pad) + cell_pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 40, 56))
    font = pygame.font.SysFont("Arial", 14, bold=True)
    small = pygame.font.SysFont("Arial", 13, bold=True)

    # column headers (loads)
    for c, ld in enumerate(LOADS):
        x = left + c * (pw + cell_pad) + cell_pad
        sheet.blit(small.render(f"load {ld:.2f}", True, (210, 225, 245)),
                   (x + 4, 8))

    for r, (label, keyfn) in enumerate(options):
        sorted_pool = sorted(base, key=keyfn)
        y = top + r * (ph + cell_pad) + cell_pad
        # row label (wrapped)
        for li, line in enumerate(label.split("  ", 1)):
            sheet.blit(font.render(line, True, (240, 246, 255)),
                       (8, y + 6 + li * 18))
        for c, ld in enumerate(LOADS):
            x = left + c * (pw + cell_pad) + cell_pad
            panel = render_pip(sorted_pool, ld, Z)
            sheet.blit(panel, (x, y))
            pygame.draw.rect(sheet, (70, 90, 120), (x - 1, y - 1, pw + 2, ph + 2), 1)

    out = os.path.join(OUT_DIR, "buildup_order_sheet.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
