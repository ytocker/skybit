"""Render docs/cloud_redesign/winners_sheet.png.

6 user-picked cloud winners across the 5 day-night phases. Imports the
live registries from each round's module so each winner is byte-identical
to what shipped in its source sheet."""

from __future__ import annotations

import math
import os
import pathlib
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = pathlib.Path(__file__).parent
_REPO = _HERE.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "archive" / "mountain_redesign"))
sys.path.insert(0, str(_HERE))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from game import biome as _biome
from render_cloud_variants import (
    _scene_backdrop, ROW_SCROLL, PHASES, CLOUD_SLOTS_XY,
)
import cloud_variants as cv
import ruyi_variants as rv
import cloud_wild_variants as cwv
import ruyi_soft_variants as rsv

OUT = _REPO / "docs" / "cloud_redesign"
OUT.mkdir(parents=True, exist_ok=True)


# (round_label, draw_fn, variant_name, source_url)
WINNERS = [
    ("R23 #2", cv.draw_cloud_ruyi,
     "Ruyi Auspicious Scroll",
     "en.wikipedia.org/wiki/Xiangyun_(Auspicious_clouds)"),
    ("R24 #6", rv.draw_ruyi_dragon,
     "Dragon-Coil Long-Form",
     rv.VARIANT_SOURCES[6]),
    ("R24 #7", rv.draw_ruyi_mandala,
     "Tang Mandala Crest",
     rv.VARIANT_SOURCES[7]),
    ("R24 #8", rv.draw_ruyi_deco,
     "Ruyi Eclipse",
     rv.VARIANT_SOURCES[8]),
    ("R26 #5", cwv.draw_cloud_origami,
     "Origami Folded Pillow",
     cwv.VARIANT_SOURCES[5]),
    ("R27 #2", rsv.draw_cloud_cinnabar,
     "Cinnabar-Tipped Tan",
     rsv.VARIANT_SOURCES[2]),
]


def render_cell(draw_fn, row_seed: int, phase: float, col_idx: int) -> pygame.Surface:
    surf = _scene_backdrop(phase, ROW_SCROLL)
    palette = _biome.palette_for_phase(phase)
    for i, (cx, cy) in enumerate(CLOUD_SLOTS_XY):
        rng = random.Random(row_seed * 10007 + col_idx * 131 + i)
        sc = 0.7 + rng.random() * 0.6
        bob = math.sin(i * 0.9) * 2
        cy_eff = cy + bob if i != 0 else 340 + rng.randint(-20, 40)
        draw_fn(surf, cx, cy_eff, palette, scale=sc)
    return surf


def make_sheet() -> pygame.Surface:
    n_rows = len(WINNERS)
    tw, th = W, H
    label_h = 32
    row_label_w = 280
    pad = 10
    sheet_w = row_label_w + pad + len(PHASES) * (tw + pad)
    sheet_h = label_h + pad + n_rows * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 22))

    font_small = pygame.font.SysFont(None, 18)
    font_mid = pygame.font.SysFont(None, 22)
    font_head = pygame.font.SysFont(None, 28)

    title = font_head.render(
        "CLOUD DESIGN WINNERS — 6 picks across rounds 23 · 24 · 26 · 27",
        True, (240, 240, 240))
    sheet.blit(title, (row_label_w + pad, 6))

    for c, (plabel, _p) in enumerate(PHASES):
        x = row_label_w + pad + c * (tw + pad)
        lbl = font_mid.render(plabel, True, (250, 230, 180))
        sheet.blit(lbl, (x + 8, label_h - 22))

    for r, (idx_label, draw_fn, name, src) in enumerate(WINNERS):
        y = label_h + pad + r * (th + pad)

        sheet.blit(font_head.render(idx_label, True, (255, 220, 130)),
                   (8, y + 6))
        words = name.split()
        line, ly = "", y + 40
        for word in words:
            test = (line + " " + word).strip()
            if font_mid.size(test)[0] > row_label_w - 16 and line:
                sheet.blit(font_mid.render(line, True, (235, 235, 235)),
                           (8, ly))
                ly += 20
                line = word
            else:
                line = test
        if line:
            sheet.blit(font_mid.render(line, True, (235, 235, 235)), (8, ly))
            ly += 24
        url_line = ""
        for word in src.split():
            test = (url_line + " " + word).strip()
            if font_small.size(test)[0] > row_label_w - 16 and url_line:
                sheet.blit(font_small.render(url_line, True, (170, 180, 200)),
                           (8, ly))
                ly += 16
                url_line = word
            else:
                url_line = test
        if url_line:
            sheet.blit(font_small.render(url_line, True, (170, 180, 200)),
                       (8, ly))

        row_seed = (r + 1) * 31337
        for c, (plabel, phase) in enumerate(PHASES):
            x = row_label_w + pad + c * (tw + pad)
            tile = render_cell(draw_fn, row_seed, phase, c)
            sheet.blit(tile, (x, y))
            tagtxt = font_small.render(
                f"{plabel} · phase {phase:.2f}", True, (250, 250, 250))
            bg = pygame.Surface(
                (tagtxt.get_width() + 8, tagtxt.get_height() + 4),
                pygame.SRCALPHA)
            bg.fill((0, 0, 0, 150))
            sheet.blit(bg, (x + 4, y + 4))
            sheet.blit(tagtxt, (x + 8, y + 6))

    return sheet


def main() -> None:
    sheet = make_sheet()
    out = OUT / "winners_sheet.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
