"""Comparison sheet of the CURRENT in-game pagoda designs.

Renders every entry in pillar_pagodas.VARIANT_KEYS (the live roster picked by
`seed % VARIANT_COUNT` per pillar) as a full upright ground tower over a daytime
sky, laid out in a labeled grid — a single at-a-glance "here is the whole set as
it ships today" figure to anchor a redesign pass.

Baked exactly the way entities.Pipe does (per-pillar SRCALPHA at local rects,
MARGIN side gutters for eave/ornament overhang), daytime palette so bodies read.

Run:  python tools/render_pagoda_comparison.py
Out:  docs/pillar_redesign/pagoda_comparison.png
"""
from __future__ import annotations

import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import GROUND_Y, PIPE_W
from game import biome
import game.pillar_pagodas as pgv

MARGIN = 64                       # matches entities.Pipe._build_pagoda_cache
CACHE_W = PIPE_W + MARGIN * 2     # full baked width (captures eave overhang)
CACHE_H = GROUND_Y

PHASE = 0.30                      # daytime so every body reads clearly
SEED_BASE = 13                    # one deterministic seed per variant

# Tall bottom tower so the full multi-tier silhouette shows top-to-bottom.
GAP_Y, GAP_H = 130, 130
TOP_H = int(GAP_Y - GAP_H / 2)
BOT_TOP = int(GAP_Y + GAP_H / 2)
TIP_Y = BOT_TOP - 10             # a little sky headroom above the finial
BASE_Y = GROUND_Y + 8            # a hair of ground below the plinth
TOWER_H = BASE_Y - TIP_Y


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def bake_tower(key: str) -> pygame.Surface:
    """Bake one variant's full pillar pair, return the cropped upright tower."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    palette = biome.palette_for_phase(PHASE)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, TOP_H)
    bot_rect = pygame.Rect(MARGIN, BOT_TOP, PIPE_W, GROUND_Y - BOT_TOP)
    ci = pgv.VARIANT_KEYS.index(key)
    seed = SEED_BASE - (SEED_BASE % pgv.VARIANT_COUNT) + ci
    pgv.CANDIDATES[key](surf, top_rect, bot_rect, palette, seed)
    tower = pygame.Surface((CACHE_W, TOWER_H), pygame.SRCALPHA)
    tower.blit(surf, (0, 0), pygame.Rect(0, TIP_Y, CACHE_W, TOWER_H))
    return tower


def cell_background(w: int, h: int, pal) -> pygame.Surface:
    """Daytime sky gradient with a thin ground band, matching the live look."""
    cell = pygame.Surface((w, h))
    ground_h = h - (TOWER_H - (BASE_Y - GROUND_Y))   # ground line at GROUND_Y
    sky_h = h - 14
    for y in range(sky_h):
        t = y / max(1, sky_h - 1)
        col = _lerp(pal["sky_top"], pal["horizon"], t)
        pygame.draw.line(cell, col, (0, y), (w, y))
    for y in range(sky_h, h):
        t = (y - sky_h) / max(1, h - sky_h)
        col = _lerp(pal["ground_top"], pal["ground_mid"], t)
        pygame.draw.line(cell, col, (0, y), (w, y))
    return cell


def main() -> None:
    keys = pgv.VARIANT_KEYS
    pal = biome.palette_for_phase(PHASE)

    cols = 6
    rows = (len(keys) + cols - 1) // cols
    pad = 10
    label_h = 26
    cw, ch = CACHE_W, TOWER_H
    cell_h = ch + label_h

    head_h = 52
    sheet_w = pad + cols * (cw + pad)
    sheet_h = head_h + pad + rows * (cell_h + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    title = pygame.font.SysFont(None, 34)
    sub = pygame.font.SysFont(None, 19)
    label = pygame.font.SysFont(None, 22)
    serial = pygame.font.SysFont(None, 24, bold=True)

    sheet.blit(title.render("Skybit — current pagoda designs (live roster)",
                            True, (245, 240, 230)), (pad, 10))
    sheet.blit(sub.render(f"{len(keys)} variants in play  ·  seed % {pgv.VARIANT_COUNT}"
                          "  ·  daytime palette", True, (170, 172, 182)), (pad, 36))

    for i, key in enumerate(keys):
        r, c = divmod(i, cols)
        x = pad + c * (cw + pad)
        y = head_h + pad + r * (cell_h + pad)
        cell = cell_background(cw, ch, pal)
        cell.blit(bake_tower(key), (0, 0))
        sheet.blit(cell, (x, y))
        pygame.draw.rect(sheet, (60, 62, 72), pygame.Rect(x, y, cw, ch), 1)

        # Serial number badge, top-left of the cell — a stable ID to talk about
        # each design ("#3") independent of its (long) internal key name.
        sn = f"#{i + 1}"
        num = serial.render(sn, True, (24, 25, 30))
        bw, bh = num.get_width() + 12, num.get_height() + 6
        badge = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.rect(badge, (255, 224, 150), badge.get_rect(), border_radius=6)
        badge.blit(num, (6, 3))
        sheet.blit(badge, (x + 4, y + 4))

        lab = label.render(f"{i + 1}. {key}", True, (255, 224, 150))
        sheet.blit(lab, (x + (cw - lab.get_width()) // 2, y + ch + 4))

    out = _REPO / "docs" / "pillar_redesign" / "pagoda_comparison.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print("variants:", ", ".join(keys))


if __name__ == "__main__":
    main()
