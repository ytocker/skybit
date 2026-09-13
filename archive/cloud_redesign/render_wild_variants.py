"""Render docs/cloud_redesign/wild_round_N.png — 8 wild-divergence variants.

8 rows × 5 phases, no baseline reference row (the prior shipped Ruyi
disc is one git checkout away). Scene composition mirrors the round-25
harness so direct comparisons hold: sky + V14 backdrop + ground per
cell, 6 cloud instances scattered at seeded x/y/scale.

Slot-0 ridge anchor + per-variant placement overrides keep the wild
shapes legible: vertical pillars (#2, #6) are anchored at the lower
sky band so the column reads as rising rather than floating; the
horizontal cirrus streak (#3) is pushed to the upper third where
real cirrus actually sits."""

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
import cloud_wild_variants as wv

OUT = _REPO / "docs" / "cloud_redesign"
OUT.mkdir(parents=True, exist_ok=True)


# Variants whose silhouette is vertical or fall-streak heavy need
# placement overrides so the form has space to register. Mapping is
# variant_id → callable(row, col, idx, default_x, default_y, rng) →
# (x, y). None means use the default scatter pattern.
def _place(variant_id, i, default_x, default_y, rng):
    # Vertical Sumeru pillar: anchor near the lower-mid sky so the
    # 80-px column can rise without clipping into the V14 ridges or
    # the top edge of the canvas.
    if variant_id == 2 and i in (1, 3):
        return default_x, int(H * 0.42) + rng.randint(-8, 8)
    # Cirrus mare's-tail: cirrus belongs at altitude — push slot 2/4
    # to upper third.
    if variant_id == 3 and i in (2, 4):
        return default_x, int(H * 0.18) + rng.randint(-8, 8)
    # Incense smoke volute: rising column wants a lower anchor so the
    # dispersion bloom has room to reach toward the upper sky.
    if variant_id == 6 and i in (1, 3, 5):
        return default_x, int(H * 0.50) + rng.randint(-6, 6)
    return default_x, default_y


def render_cell(variant_id: int, phase: float, col_idx: int) -> pygame.Surface:
    surf = _scene_backdrop(phase, ROW_SCROLL)
    palette = _biome.palette_for_phase(phase)
    draw_fn = wv.VARIANTS[variant_id]
    for i, (cx, cy) in enumerate(CLOUD_SLOTS_XY):
        rng = random.Random(variant_id * 10007 + col_idx * 131 + i)
        # Scale variance per-slot so the row isn't a uniform-scale grid;
        # tightened to 0.8-1.25 because the wild shapes need to read at
        # their intended aspect ratio rather than blob into thumbnails.
        sc = 0.8 + rng.random() * 0.45
        bob = math.sin(i * 0.9) * 2
        if i == 0:
            cy_eff = 340 + rng.randint(-20, 40)
        else:
            cy_eff = cy + bob
        cx_eff, cy_eff = _place(variant_id, i, cx, cy_eff, rng)
        draw_fn(surf, cx_eff, cy_eff, palette, scale=sc)
    return surf


def make_sheet() -> pygame.Surface:
    n_rows = len(wv.VARIANTS)
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
        "WILD CLOUDS — ROUND 3 · 8 divergent variants × 5 phases",
        True, (240, 240, 240))
    sheet.blit(title, (row_label_w + pad, 6))

    for c, (plabel, _p) in enumerate(PHASES):
        x = row_label_w + pad + c * (tw + pad)
        lbl = font_mid.render(plabel, True, (250, 230, 180))
        sheet.blit(lbl, (x + 8, label_h - 22))

    variant_ids = sorted(wv.VARIANTS.keys())
    for r, vid in enumerate(variant_ids):
        y = label_h + pad + r * (th + pad)
        name = wv.VARIANT_NAMES[vid]
        src = wv.VARIANT_SOURCES[vid]

        idx_lbl = font_head.render(f"#{vid}", True, (255, 220, 130))
        sheet.blit(idx_lbl, (8, y + 6))

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
            tile = render_cell(vid, phase, c)
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
    out = OUT / "wild_round_3.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
