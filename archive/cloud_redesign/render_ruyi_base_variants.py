"""Render docs/cloud_redesign/ruyi_base_faithful_round_N.png.

6 rows × 5 phases. Row 0 = byte-identical round-23 baseline
(`cloud_variants.draw_cloud_ruyi`); rows 1–5 = the 5 new base-
faithful variants from `ruyi_base_variants`. Sky + V14 backdrop +
ground per cell via the shared `_scene_backdrop` from
`render_cloud_variants`. INT-hashed seed pattern (no tuples)."""

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

from game.config import W, H, GROUND_Y
from game import biome as _biome
from render_cloud_variants import (
    _scene_backdrop, ROW_SCROLL, PHASES, CLOUD_SLOTS_XY,
)
import cloud_variants as cv
import ruyi_base_variants as rbv

OUT = _REPO / "docs" / "cloud_redesign"
OUT.mkdir(parents=True, exist_ok=True)


def render_cell(row_idx: int, phase: float, col_idx: int) -> pygame.Surface:
    surf = _scene_backdrop(phase, ROW_SCROLL)
    palette = _biome.palette_for_phase(phase)
    if row_idx == 0:
        draw_fn = cv.draw_cloud_ruyi
    else:
        draw_fn = rbv.VARIANTS[row_idx]
    for i, (cx, cy) in enumerate(CLOUD_SLOTS_XY):
        rng = random.Random(row_idx * 10007 + col_idx * 131 + i)
        sc = 0.7 + rng.random() * 0.6
        bob = math.sin(i * 0.9) * 2
        cy_eff = cy + bob if i != 0 else 340 + rng.randint(-20, 40)
        draw_fn(surf, cx, cy_eff, palette, scale=sc)
    return surf


def make_sheet() -> pygame.Surface:
    n_rows = 6  # baseline + 5 variants
    tw, th = W, H
    label_h = 32
    row_label_w = 240
    pad = 10
    sheet_w = row_label_w + pad + len(PHASES) * (tw + pad)
    sheet_h = label_h + pad + n_rows * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 22))

    font_small = pygame.font.SysFont(None, 18)
    font_mid = pygame.font.SysFont(None, 22)
    font_head = pygame.font.SysFont(None, 28)

    title = font_head.render(
        "RUYI BASE-FAITHFUL — ROUND 3 · 5 surgical variations + baseline",
        True, (240, 240, 240))
    sheet.blit(title, (row_label_w + pad, 6))

    for c, (plabel, _p) in enumerate(PHASES):
        x = row_label_w + pad + c * (tw + pad)
        lbl = font_mid.render(plabel, True, (250, 230, 180))
        sheet.blit(lbl, (x + 8, label_h - 22))

    for r in range(n_rows):
        y = label_h + pad + r * (th + pad)
        if r == 0:
            name = "BASE — Ruyi Auspicious Scroll (round-23 baseline)"
            src = "cloud_variants.draw_cloud_ruyi"
            idx_label = "BASE"
            idx_color = (140, 200, 255)
        else:
            name = rbv.VARIANT_NAMES[r]
            src = rbv.VARIANT_SOURCES[r]
            idx_label = f"#{r}"
            idx_color = (255, 220, 130)

        sheet.blit(font_head.render(idx_label, True, idx_color), (8, y + 6))
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

        for c, (plabel, phase) in enumerate(PHASES):
            x = row_label_w + pad + c * (tw + pad)
            tile = render_cell(r, phase, c)
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
    out = OUT / "ruyi_base_faithful_round_3.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
