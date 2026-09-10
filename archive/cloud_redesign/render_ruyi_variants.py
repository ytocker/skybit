"""Render `docs/cloud_redesign/ruyi_variations_round_3.png`.

Row 1 is the round-23 baseline (`cloud_variants.draw_cloud_ruyi`) so the
critique can compare every new candidate against the byte-identical
reference. Rows 2-9 are the 8 new Ruyi-direction explorations registered
in `ruyi_variants.VARIANTS`.

5 columns: DAY 0.02 / GOLDEN 0.23 / SUNSET 0.36 / DUSK 0.51 / NIGHT 0.64.
Each tile reuses the V14 backdrop pattern from the round-23 harness so
the AD judges each variant in situ against the live shan-shui ridges,
not on a bare swatch.

Run from anywhere:
    python archive/cloud_redesign/render_ruyi_variants.py
"""
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

# Reuse the round-23 backdrop pattern verbatim so the baseline-row tile
# matches the round-23 reference pixel-perfectly. The original harness
# already imports + initializes the V14 mountain pack; pulling
# `_scene_backdrop` keeps the V14 keeper + ground rendering identical.
from render_cloud_variants import _scene_backdrop, ROW_SCROLL

import cloud_variants as cv
import ruyi_variants as rv


# Phases — locked to the round brief.
PHASES = [
    ("DAY",     0.02),
    ("GOLDEN",  0.23),
    ("SUNSET",  0.36),
    ("DUSK",    0.51),
    ("NIGHT",   0.64),
]

# Cloud placement scattered across the canvas — same slot pattern as
# round 23 so the AD's eye lands on the same anchor points across
# rounds. Slot 0 is the ridge-anchored slot (y replaced at runtime).
RIDGE_SLOT = (140, 340)
CLOUD_SLOTS_XY = (
    RIDGE_SLOT,
    (60,  90),
    (220, 130),
    (290, 250),
    (40,  290),
    (200, 340),
)

OUT = _REPO / "docs" / "cloud_redesign"
OUT.mkdir(parents=True, exist_ok=True)


# Row 0 (baseline) calls `cv.draw_cloud_ruyi` directly. Rows 1-8 call
# the matching `rv.VARIANTS[key]` candidate. Centralizing the resolver
# keeps the cell render loop simple and ensures the baseline path
# never accidentally diverges from the round-23 contract.
def _draw_for_row(row_idx: int):
    if row_idx == 0:
        return cv.draw_cloud_ruyi
    return rv.VARIANTS[row_idx]


def _row_label(row_idx: int) -> tuple[str, str]:
    if row_idx == 0:
        return ("Original Ruyi V2 (round-23 ref)",
                "cloud_variants.draw_cloud_ruyi")
    return (rv.VARIANT_NAMES[row_idx], rv.VARIANT_SOURCES[row_idx])


def render_cell(row_idx: int, phase: float, col_idx: int) -> pygame.Surface:
    surf = _scene_backdrop(phase, ROW_SCROLL)
    palette = _biome.palette_for_phase(phase)
    draw_fn = _draw_for_row(row_idx)
    for i, (cx, cy) in enumerate(CLOUD_SLOTS_XY):
        # Per-instance seed: (row, col, idx) as INT — round-23 brief
        # explicitly forbids tuple seeds. Same hashing weights as
        # round-23 so seed shuffling is consistent across rounds.
        rng = random.Random(row_idx * 10007 + col_idx * 131 + i)
        sc = 0.7 + rng.random() * 0.6
        bob = math.sin(i * 0.9) * 2
        # Slot 0 force-anchored to the V14 ridgeline — same as round 23.
        if i == 0:
            cy_eff = 340 + rng.randint(-20, 40)
        else:
            cy_eff = cy + bob
        # Variant 6 (Dragon long-form) is 120 px wide — clamp x so the
        # silhouette doesn't get cut off at the right edge of the tile.
        cx_eff = cx
        if row_idx == 6 and cx > W - 80:
            cx_eff = W - 80
        draw_fn(surf, cx_eff, cy_eff, palette, scale=sc)
    return surf


def make_sheet() -> pygame.Surface:
    tw, th = W, H
    label_h = 36
    row_label_w = 240
    pad = 10
    n_rows = 1 + len(rv.VARIANTS)  # baseline row + 8 candidates
    sheet_w = row_label_w + pad + len(PHASES) * (tw + pad)
    sheet_h = label_h + pad + n_rows * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 22))

    font_small = pygame.font.SysFont(None, 18)
    font_mid = pygame.font.SysFont(None, 22)
    font_head = pygame.font.SysFont(None, 28)

    title = font_head.render(
        "RUYI VARIATIONS — ROUND 3 · final surgical fixes (Sovereign + Dragon)",
        True, (240, 240, 240))
    sheet.blit(title, (row_label_w + pad, 6))

    # Phase column headers.
    for c, (plabel, _p) in enumerate(PHASES):
        x = row_label_w + pad + c * (tw + pad)
        lbl = font_mid.render(plabel, True, (250, 230, 180))
        sheet.blit(lbl, (x + 8, label_h - 22))

    for row_idx in range(n_rows):
        y = label_h + pad + row_idx * (th + pad)
        name, src = _row_label(row_idx)

        # Row index — "BASE" for the round-23 reference, then #1..#8.
        if row_idx == 0:
            idx_text = "BASE"
            idx_col = (180, 220, 255)
        else:
            idx_text = f"#{row_idx}"
            idx_col = (255, 220, 130)
        idx_lbl = font_head.render(idx_text, True, idx_col)
        sheet.blit(idx_lbl, (8, y + 6))

        # Wrap variant name into row-label column.
        words = name.split()
        line, ly = "", y + 42
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
            sheet.blit(font_mid.render(line, True, (235, 235, 235)),
                       (8, ly))
            ly += 24

        # Research URL — smaller, wrapped, dim.
        url_line = ""
        for word in src.split():
            test = (url_line + " " + word).strip()
            if font_small.size(test)[0] > row_label_w - 16 and url_line:
                sheet.blit(
                    font_small.render(url_line, True, (170, 180, 200)),
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
            tile = render_cell(row_idx, phase, c)
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
    out = OUT / "ruyi_variations_round_3.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
