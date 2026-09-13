"""Render the 11 winners × 5 seeds at sunset with the ornament layer on
top.

The structural pillar drawers in `pillar_pagoda_variants.py` and
`pillar_pagoda_variants_r4.py` are unchanged — `apply_ornaments()` paints
the ornament cells on top of the drawn pair. Each tile lists the active
ornament names so the AD can verify the picker's choices at a glance.

Output:
  docs/pillar_redesign/_alive_variants.png

Run from anywhere:
    python archive/pillar_redesign/render_alive_variants.py
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

from game.config import W, H, GROUND_Y, PIPE_W
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome,
    draw_cloud,
    draw_ground,
)
import mountain_variants_alive as mv
from game import pillar_pagodas as pgv          # promoted from this dir
from game import pagoda_ornaments as orn        # promoted from this dir

# stupa_canopy was merged into pillar_pagodas at promotion time.
pgv_r4 = pgv


# AD asked for sunset (~0.36) so the warm light makes the ornament glyphs
# read but the night-only items are still gated off (sunset is < 0.58).
PHASE = 0.363

# 5 different seeds per pagoda so each row shows ornament variation, not
# the same draw 5 times. Pillar indices stride through 0/1/2/3 so the
# first-pillar suppression rule is exercised in at least one cell per row.
# Per-column scroll lands each cell in a distinct V14 region bucket
# (REGION_WIDTH = 600 in mountain_variants_alive) so the backdrop visibly
# EVOLVES left-to-right — early-game silhouettes on the left, mid-game in
# the middle, late-game on the right — while each cell still demos its
# own ornament roll.
SEEDS = [
    ("s1 · early",  13,  0,  200.0),
    ("s2 · early-mid", 47,  1,  900.0),
    ("s3 · mid",    92,  2, 1500.0),
    ("s4 · mid-late", 131, 3, 2100.0),
    ("s5 · late",  199, 4, 2700.0),
]

WINNERS = [
    ("Stupa + Prayer-Flag Canopy",
     pgv_r4, "candidate_stupa_canopy",     "stupa_canopy"),
    ("Wat Arun (Thai Khmer prang)",
     pgv,    "candidate_wat_arun",         "wat_arun"),
    ("Songyue Sandstone",
     pgv,    "candidate_songyue_sandstone","songyue_sandstone"),
    ("Hōryū-ji (Japanese 5-storey)",
     pgv,    "candidate_horyuji",          "horyuji"),
    ("Fogong / Yingxian (Liao wooden)",
     pgv,    "candidate_fogong",           "fogong"),
    ("Tō-ji (dark cypress)",
     pgv,    "candidate_toji",             "toji"),
    ("Daigo-ji (vermillion + gold)",
     pgv,    "candidate_daigoji",          "daigoji"),
    ("Yakushi-ji (mokoshi + bronze suien)",
     pgv,    "candidate_yakushiji",        "yakushiji"),
    ("Bao'en Porcelain Tower",
     pgv,    "candidate_baoen",            "baoen"),
    ("Murō-ji (thatched cypress-bark)",
     pgv,    "candidate_muroji",           "muroji"),
    ("Palsangjeon / Beopjusa",
     pgv,    "candidate_palsangjeon",      "palsangjeon"),
]

ROW_GROUND_ACCENT = {
    "daigoji":      (148, 80, 50),
    "wat_arun":     (180, 120, 140),
    "songyue_sandstone": (192, 148, 110),
    "toji":         (96, 76, 60),
    "yakushiji":    (140, 116, 78),
    "baoen":        (208, 196, 178),
    "muroji":       (52, 78, 50),
    "palsangjeon":  (118, 130, 138),
    "stupa_canopy": (172, 152, 124),
}

KEEPER_V14 = 14

OUT = _REPO / "docs" / "pillar_redesign"
OUT.mkdir(parents=True, exist_ok=True)


def _apply_ground_accent(surf, row_key):
    accent = ROW_GROUND_ACCENT.get(row_key)
    if accent is None:
        return
    overlay = pygame.Surface((W, 7), pygame.SRCALPHA)
    overlay.fill((*accent, 110))
    surf.blit(overlay, (0, GROUND_Y))
    for x in range(0, W, 9):
        r = (x * 7 + row_key.__hash__() & 0xFF) % 5
        col = (max(0, accent[0] - 30), max(0, accent[1] - 30),
               max(0, accent[2] - 30))
        surf.set_at((x + r, GROUND_Y + 2), col)
        surf.set_at((x + r + 4, GROUND_Y + 5), col)


def _scene_backdrop(phase: float, scroll: float) -> pygame.Surface:
    palette = _biome.palette_for_phase(phase)
    surf = pygame.Surface((W, H))
    bucket = _biome.phase_bucket(phase)
    sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
    sky.set_alpha(None)
    surf.blit(sky, (0, 0))
    for i, (bx, by, _sc, variant) in enumerate((
            (40, 95, 0.9, 0), (200, 150, 1.0, 2),
            (90, 230, 0.8, 3), (270, 70, 0.7, 1))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(0.45 + i) * 3, _sc, variant=variant)
    mv.set_phase(phase)
    mv.VARIANTS[KEEPER_V14](surf, scroll, GROUND_Y, W,
                            palette['mtn_far'], palette['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    return surf


def render_tile(source_module, candidate_name: str, candidate_key: str,
                seed: int, pillar_index: int,
                scroll: float) -> tuple[pygame.Surface, tuple[str, ...]]:
    surf = _scene_backdrop(PHASE, scroll)
    palette = _biome.palette_for_phase(PHASE)

    _apply_ground_accent(surf, candidate_key)

    # One foreground pillar pair in the canonical right-hand position so
    # the ornament layer has a single, predictable subject per tile.
    gap_y = 280
    gap_h = 170
    px = W - 90
    top_rect = pygame.Rect(px, 0, PIPE_W, gap_y - gap_h // 2)
    bot_rect = pygame.Rect(px, gap_y + gap_h // 2, PIPE_W,
                           GROUND_Y - (gap_y + gap_h // 2))

    fn = getattr(source_module, candidate_name)
    fn(surf, top_rect, bot_rect, palette, seed)

    applied = orn.apply_ornaments(
        surf, top_rect, bot_rect,
        candidate_key, palette, seed, PHASE,
        pillar_index=pillar_index, is_rush=False,
    )
    return surf, applied


def make_sheet() -> pygame.Surface:
    tw, th = W, H
    label_h = 30
    row_label_w = 260
    pad = 10
    sheet_w = row_label_w + pad + len(SEEDS) * (tw + pad)
    sheet_h = label_h + pad + len(WINNERS) * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    font_small = pygame.font.SysFont(None, 20)
    font_head = pygame.font.SysFont(None, 26)

    title = font_head.render(
        "PAGODA ORNAMENT LAYER — 11 winners × 5 seeds @ sunset",
        True, (240, 240, 240))
    sheet.blit(title, (row_label_w + pad, 6))

    for c, (slabel, seed, pi, scroll) in enumerate(SEEDS):
        x = row_label_w + pad + c * (tw + pad)
        lbl = font_head.render(
            f"{slabel} · seed {seed} · pi={pi} · scroll={int(scroll)}",
            True, (240, 240, 240))
        sheet.blit(lbl, (x + 6, label_h - 22))

    for r, (label, module, fn_name, key) in enumerate(WINNERS):
        y = label_h + pad + r * (th + pad)
        idx_lbl = font_head.render(f"#{r + 1}", True, (255, 220, 130))
        sheet.blit(idx_lbl, (8, y + 6))

        words = label.split()
        line, ly = "", y + 36
        for word in words:
            test = (line + " " + word).strip()
            if font_small.size(test)[0] > row_label_w - 16 and line:
                sheet.blit(font_small.render(line, True, (215, 215, 215)),
                           (8, ly))
                ly += 18
                line = word
            else:
                line = test
        if line:
            sheet.blit(font_small.render(line, True, (215, 215, 215)),
                       (8, ly))
        sheet.blit(font_small.render(f"key: {key}", True, (170, 180, 200)),
                   (8, ly + 22))

        for c, (slabel, seed, pi, scroll) in enumerate(SEEDS):
            # Clear pillar cache so each seed actually re-draws the
            # structural pair (the cache key is per-seed already, but
            # the keeper modules share the dict).
            if hasattr(pgv, "_PILLAR_CACHE"):
                pgv._PILLAR_CACHE.clear()
            if hasattr(pgv_r4, "_PILLAR_CACHE"):
                pgv_r4._PILLAR_CACHE.clear()
            tile, applied = render_tile(module, fn_name, key, seed, pi,
                                        scroll)
            x = row_label_w + pad + c * (tw + pad)
            sheet.blit(tile, (x, y))
            # Active-ornament label per cell.
            if applied:
                ornaments_txt = "ornaments: " + " + ".join(applied)
            else:
                ornaments_txt = "ornaments: (none)"
            tagtxt = font_small.render(ornaments_txt, True, (250, 250, 250))
            bg = pygame.Surface(
                (tagtxt.get_width() + 8, tagtxt.get_height() + 4),
                pygame.SRCALPHA)
            bg.fill((0, 0, 0, 150))
            sheet.blit(bg, (x + 4, y + 4))
            sheet.blit(tagtxt, (x + 8, y + 6))

    return sheet


def main() -> None:
    sheet = make_sheet()
    out = OUT / "_alive_variants.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
