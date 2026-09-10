"""Before/after pillar comparison: archived sandstone vs live pagoda.

Renders the same set of seeds through both draw_pillar_pair implementations
so the silhouette change (and the tall pagoda finials/sorin "antennas") is
directly visible. Output: docs/pillar_redesign/_sandstone_vs_pagoda.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from game.config import PIPE_W, GROUND_Y
from game.biome import palette_for_phase
import archive.sandstone_pillars as sandstone
import game.pillar_pagodas as pagoda

pygame.init()

# Daytime biome palette — full key set both renderers expect (sky_*, stone_*,
# foliage_*, and the pagoda-specific material keys).
PALETTE = palette_for_phase(0.0)

SEEDS = [0, 1, 2, 3, 4, 5]
MARGIN = 64                      # matches entities._build_pagoda_cache overhang
CELL_W = PIPE_W + MARGIN * 2     # full column incl. eave/finial overhang
CELL_H = GROUND_Y
GAP_H = 175
GAP_Y = int(GROUND_Y * 0.46)    # mid-ish gap so both bodies have real height

SKY = (150, 205, 235)
PAD = 14
LABEL_H = 34
TITLE_H = 44


def render_cell(draw_fn, seed, is_pagoda):
    surf = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
    surf.fill(SKY)
    top = pygame.Rect(MARGIN, 0, PIPE_W, int(GAP_Y - GAP_H / 2))
    bot_top = int(GAP_Y + GAP_H / 2)
    bot = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    if is_pagoda:
        draw_fn(surf, top, bot, PALETTE, seed,
                phase=0.0, is_rush=False, pillar_index=seed + 1)
    else:
        draw_fn(surf, top, bot, PALETTE, seed)
    return surf


def main():
    cols = len(SEEDS)
    grid_w = PAD + cols * (CELL_W + PAD)
    grid_h = TITLE_H + 2 * (LABEL_H + CELL_H + PAD) + PAD
    out = pygame.Surface((grid_w, grid_h))
    out.fill((28, 30, 36))

    fbig = pygame.font.SysFont("dejavusans", 24, bold=True)
    frow = pygame.font.SysFont("dejavusans", 19, bold=True)
    fsmall = pygame.font.SysFont("dejavusans", 14)

    t = fbig.render("Pillars: sandstone (before)  vs  pagoda (after)", True, (240, 240, 240))
    out.blit(t, ((grid_w - t.get_width()) // 2, 10))

    rows = [
        ("BEFORE — sandstone variants (seed % 8)", sandstone.draw_pillar_pair, False, (255, 214, 150)),
        ("AFTER — pagoda variants (seed % 11)", pagoda.draw_pillar_pair, True, (150, 220, 255)),
    ]

    y = TITLE_H
    for label, fn, is_pagoda, col in rows:
        lab = frow.render(label, True, col)
        out.blit(lab, (PAD, y + 6))
        y += LABEL_H
        x = PAD
        for seed in SEEDS:
            cell = render_cell(fn, seed, is_pagoda)
            out.blit(cell, (x, y))
            s = fsmall.render(f"seed {seed}", True, (200, 200, 200))
            out.blit(s, (x + (CELL_W - s.get_width()) // 2, y + CELL_H - 18))
            x += CELL_W + PAD
        y += CELL_H + PAD

    os.makedirs("docs/pillar_redesign", exist_ok=True)
    path = "docs/pillar_redesign/_sandstone_vs_pagoda.png"
    pygame.image.save(out, path)
    print("wrote", path, out.get_size())


if __name__ == "__main__":
    main()
