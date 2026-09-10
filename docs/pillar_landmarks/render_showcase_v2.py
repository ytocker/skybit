"""Combined showcase of all 10 matured non-pagoda pillar concepts (round_2).

One at-a-glance figure: two labeled rows (TOTEMS, WINDMILLS), five cells each,
every cell baked IDENTICALLY (same MARGIN gutters, same tall daytime gap, same
crop) so the finals compare fairly as upright hero towers over a daytime sky.

Each concept lives in its own standalone render.py with a `candidate_*` fn of
the shipped `(surf, top_rect, bot_rect, palette, seed)` shape. The windmill slug
dirs use hyphens, so every module is loaded by FILE PATH via importlib and only
its own candidate fn is reused — nothing is re-implemented here.

Run:  python docs/pillar_landmarks/render_showcase_v2.py
Out:  docs/pillar_landmarks/showcase_v2.png
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = pathlib.Path(__file__).resolve().parent
_REPO = _HERE.parent.parent
sys.path.insert(0, str(_REPO))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import GROUND_Y, PIPE_W
from game import biome

# ── identical bake geometry for every cell (mirrors render_pagoda_comparison) ──
MARGIN = 64                        # eave/ornament gutter, matches entities.Pipe
CACHE_W = PIPE_W + MARGIN * 2      # 186 px — captures sideways overhang
CACHE_H = GROUND_Y
PHASE = 0.30                       # daytime so every body reads clearly

# Tall gap so the full upright tower shows top finial → plinth in one crop.
GAP_Y, GAP_H = 130, 130
BOT_TOP = int(GAP_Y + GAP_H / 2)
TIP_Y = BOT_TOP - 10               # a little sky headroom above the finial
BASE_Y = GROUND_Y + 8              # a hair of ground below the plinth
TOWER_H = BASE_Y - TIP_Y

# (slug dir, render.py subpath, candidate fn name, one-line thesis)
TOTEMS = [
    ("totem_formline", "totems/totem_formline/render.py", "candidate_totem_formline",
     "painted Pacific-NW cedar pole, formline crest faces"),
    ("moai_ancestor", "totems/moai_ancestor/render.py", "candidate_moai_ancestor",
     "gaunt dark-basalt ancestor heads + red scoria pukao"),
    ("jade_serpent", "totems/jade_serpent/render.py", "candidate_jade_serpent",
     "angular stepped jade guardian, gold fanged maw"),
    ("kota_reliquary", "totems/kota_reliquary/render.py", "candidate_kota_reliquary",
     "hammered brass repousse guardian on open lozenge frame"),
    ("tiwanaku_stele", "totems/tiwanaku_stele/render.py", "candidate_tiwanaku_stele",
     "flat incised andesite stele, staff-god face + ray halo"),
]
WINDMILLS = [
    ("pavilion-mill", "windmills/pavilion-mill/render.py", "candidate_pavilion_mill",
     "tiered pagoda-pavilion body + open canvas sail-X"),
    ("waterwheel-mill", "windmills/waterwheel-mill/render.py", "candidate_waterwheel_mill",
     "brick temple cone + off-axis wooden water-wheel"),
    ("mani-drum-tower", "windmills/mani-drum-tower/render.py", "candidate_mani_drum_tower",
     "stacked copper prayer-drum body + wind cross-vane"),
    ("shoji-rose-mill", "windmills/shoji-rose-mill/render.py", "candidate_shoji_rose_mill",
     "plaster slab + glowing swept paper rosette"),
    ("junk-sail-mill", "windmills/junk-sail-mill/render.py", "candidate_junk_sail_mill",
     "open bamboo cage + upright battened junk-sail comb"),
]


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _load_candidate(subpath: str, fn_name: str, slug: str):
    """Load one concept's render.py by FILE PATH (slugs contain hyphens, so a
    package import won't do) and return only its own candidate fn."""
    path = _HERE / subpath
    mod_name = "concept_" + slug.replace("-", "_")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def bake_tower(fn, seed: int) -> pygame.Surface:
    """Bake one concept's full pillar pair, crop the upright ground tower.

    Identical geometry for every concept so the finals compare fairly."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    palette = biome.palette_for_phase(PHASE)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, int(GAP_Y - GAP_H / 2))
    bot_rect = pygame.Rect(MARGIN, BOT_TOP, PIPE_W, GROUND_Y - BOT_TOP)
    fn(surf, top_rect, bot_rect, palette, seed)
    tower = pygame.Surface((CACHE_W, TOWER_H), pygame.SRCALPHA)
    tower.blit(surf, (0, 0), pygame.Rect(0, TIP_Y, CACHE_W, TOWER_H))
    return tower


def cell_background(w: int, h: int, pal) -> pygame.Surface:
    """Daytime sky gradient with a thin ground band at the tower's base."""
    cell = pygame.Surface((w, h))
    sky_h = h - 14
    for y in range(sky_h):
        t = y / max(1, sky_h - 1)
        pygame.draw.line(cell, _lerp(pal["sky_top"], pal["horizon"], t), (0, y), (w, y))
    for y in range(sky_h, h):
        t = (y - sky_h) / max(1, h - sky_h)
        pygame.draw.line(cell, _lerp(pal["ground_top"], pal["ground_mid"], t),
                         (0, y), (w, y))
    return cell


def _wrap(font, text, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if font.size(trial)[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _painted_pixels(tower: pygame.Surface) -> int:
    """Count non-transparent pixels — proves a tower actually painted in a cell."""
    n = 0
    w, h = tower.get_width(), tower.get_height()
    for x in range(w):
        for y in range(h):
            if tower.get_at((x, y))[3] > 0:
                n += 1
    return n


def main() -> None:
    pal = biome.palette_for_phase(PHASE)

    cw, ch = CACHE_W, TOWER_H
    cols = 5
    pad = 12
    thesis_font = pygame.font.SysFont(None, 16)
    slug_font = pygame.font.SysFont(None, 20)
    thesis_lines_max = 2
    thesis_line_h = thesis_font.get_height()
    caption_h = 22 + thesis_lines_max * thesis_line_h  # slug + up to 2 thesis lines

    head_h = 56
    row_header_h = 30
    cell_block_h = ch + caption_h
    sheet_w = pad + cols * (cw + pad)
    sheet_h = (head_h + pad
               + (row_header_h + cell_block_h + pad) * 2)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    title = pygame.font.SysFont(None, 32)
    sub = pygame.font.SysFont(None, 19)
    row_font = pygame.font.SysFont(None, 26, bold=True)
    serial = pygame.font.SysFont(None, 24, bold=True)

    sheet.blit(title.render(
        "Skybit — non-pagoda pillar concepts (high-fidelity round 2)",
        True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render(
        "10 matured finals  ·  identical daytime bake (phase 0.30)  ·  upright hero towers",
        True, (170, 172, 182)), (pad, 38))

    rows = [("TOTEMS", TOTEMS), ("WINDMILLS", WINDMILLS)]
    counts = {}
    y_row = head_h + pad
    for row_label, concepts in rows:
        sheet.blit(row_font.render(row_label, True, (255, 224, 150)), (pad, y_row + 4))
        y_cells = y_row + row_header_h
        for c, (slug, subpath, fn_name, thesis) in enumerate(concepts):
            idx = len(counts) + 1
            fn = _load_candidate(subpath, fn_name, slug)
            tower = bake_tower(fn, seed=13 + idx)
            counts[slug] = _painted_pixels(tower)

            x = pad + c * (cw + pad)
            cell = cell_background(cw, ch, pal)
            cell.blit(tower, (0, 0))
            sheet.blit(cell, (x, y_cells))
            pygame.draw.rect(sheet, (60, 62, 72), (x, y_cells, cw, ch), 1)

            # Gold #N badge, top-left of the cell.
            num = serial.render(f"#{idx}", True, (24, 25, 30))
            bw, bh = num.get_width() + 12, num.get_height() + 6
            badge = pygame.Surface((bw, bh), pygame.SRCALPHA)
            pygame.draw.rect(badge, (255, 224, 150), badge.get_rect(), border_radius=6)
            badge.blit(num, (6, 3))
            sheet.blit(badge, (x + 4, y_cells + 4))

            # Caption: slug then wrapped thesis, below the tower.
            cy = y_cells + ch + 3
            sheet.blit(slug_font.render(slug, True, (255, 224, 150)), (x + 2, cy))
            ty = cy + 20
            for line in _wrap(thesis_font, thesis, cw - 4)[:thesis_lines_max]:
                sheet.blit(thesis_font.render(line, True, (196, 198, 208)), (x + 2, ty))
                ty += thesis_line_h
        y_row = y_cells + cell_block_h + pad

    out = _HERE / "showcase_v2.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print("per-cell painted-pixel counts:")
    for i, (slug, n) in enumerate(counts.items(), 1):
        print(f"  #{i:2d} {slug:18s} {n:6d} px  [{'OK' if n > 500 else 'EMPTY'}]")


if __name__ == "__main__":
    main()
