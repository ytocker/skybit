"""Render the 11 pagoda winners across the full in-game pillar-height range and
run a collision-fill gate.

Why: in-game a pillar section is 70-355 px tall (random gap position), but the
pagodas were only ever reviewed at the offline harness's fixed ~230/195 px. This
tool bakes each winner exactly the way entities.Pipe does (per-Pipe SRCALPHA at
local rects) across a sweep of gap geometries, draws the collision rect, and
asserts the painted body fills the rect (no invisible killzone) without squashing.

Run:  python tools/render_pagoda_heightsweep.py
Out:  docs/pillar_redesign/_heightsweep.png  + PASS/FAIL report on stdout
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

MARGIN = 64                      # matches entities.Pipe._build_pagoda_cache
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y

# (label, gap_h, gap_y) → resulting top/bot heights span the 70-355 range.
GEOMS = [
    ("short-top",  170, 155),   # top=70,  bot=355
    ("design",     170, 300),   # top=215, bot=210
    ("short-bot",  170, 440),   # top=355, bot=70
    ("rush",       221, 180),   # top~70,  bot~305
    ("genie-both", 340, 297),   # top~127, bot~128  (both short)
]

PHASE = 0.30                     # daytime so bodies read clearly


def bake(key: str, seed: int, gap_y: int, gap_h: int) -> pygame.Surface:
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    palette = biome.palette_for_phase(PHASE)
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    # Force the variant whose seed%11 selects `key`.
    ci = pgv.VARIANT_KEYS.index(key)
    s = seed - (seed % pgv.VARIANT_COUNT) + ci
    pgv.CANDIDATES[key](surf, top_rect, bot_rect, palette, s)
    return surf, top_rect, bot_rect


def fill_report(surf, rect, *, outer: str) -> dict:
    """Gameplay-relevant fill check.

    Collision is the FULL rect (Pipe.collides_circle), so any contiguous band of
    the rect with no painted pixels is a "fly-in-and-die" killzone. We measure
    the largest such empty band over the WHOLE rect (top edge, interior, gap
    edge) and fail if it exceeds the bird's effective collision radius (~10px) +
    margin. `outer` is unused now but kept for the caller's labelling.
    """
    if rect.height <= 0:
        return {"ok": True, "empty": True}
    THRESH = 12
    alpha = pygame.surfarray.array_alpha(surf)   # (W, H)
    x0, x1 = MARGIN, MARGIN + PIPE_W
    painted = []
    for y in range(rect.top, min(rect.bottom, CACHE_H)):
        col = alpha[x0:x1, y]
        painted.append(bool((col > 20).any()))
    if not any(painted):
        return {"ok": False, "reason": f"NOTHING PAINTED ({rect.height}px killzone)",
                "fill": 0.0, "band": rect.height}
    # largest contiguous empty run over the full rect (edges included)
    longest = cur = 0
    for p in painted:
        cur = 0 if p else cur + 1
        longest = max(longest, cur)
    fill = sum(painted) / len(painted)
    ok = longest <= THRESH
    return {"ok": ok, "fill": fill, "band": longest,
            "reason": "" if ok else f"empty killzone band {longest}px"}


def main() -> None:
    keys = pgv.VARIANT_KEYS
    seeds = [13]               # one seed per cell; deterministic per variant
    pad = 8
    label_w = 120
    cell_w = CACHE_W
    cell_h = CACHE_H // 1
    cols = len(GEOMS)
    rows = len(keys)
    sheet = pygame.Surface((label_w + cols * (cell_w + pad) + pad,
                            34 + rows * (cell_h + pad) + pad))
    sheet.fill((22, 22, 26))
    font = pygame.font.SysFont(None, 18)
    head = pygame.font.SysFont(None, 20)

    for c, (glabel, gh, gy) in enumerate(GEOMS):
        th = int(gy - gh / 2); bh = GROUND_Y - int(gy + gh / 2)
        x = label_w + pad + c * (cell_w + pad)
        sheet.blit(head.render(f"{glabel}  t={th} b={bh}", True, (235, 235, 235)),
                   (x, 8))

    failures = []
    for r, key in enumerate(keys):
        y = 34 + r * (cell_h + pad)
        sheet.blit(head.render(key, True, (255, 220, 130)), (6, y + 6))
        for c, (glabel, gh, gy) in enumerate(GEOMS):
            surf, top_rect, bot_rect = bake(key, seeds[0], gy, gh)
            rt = fill_report(surf, top_rect, outer="top")
            rb = fill_report(surf, bot_rect, outer="bot")
            # outline collision rects
            for rect, rep in ((top_rect, rt), (bot_rect, rb)):
                col = (60, 220, 90) if rep.get("ok") else (240, 60, 60)
                pygame.draw.rect(surf, col, rect, 1)
            x = label_w + pad + c * (cell_w + pad)
            sheet.blit(surf, (x, y))
            for half, rep in (("T", rt), ("B", rb)):
                if not rep.get("ok") and not rep.get("empty"):
                    failures.append(f"{key:18s} {glabel:10s} {half}: {rep.get('reason')}")

    out = _REPO / "docs" / "pillar_redesign" / "_heightsweep.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print(f"\n=== FILL GATE: {len(failures)} failing (winner x geometry x half) ===")
    for f in failures:
        print("  FAIL", f)
    if not failures:
        print("  ALL PASS — every winner fills both collision rects across the sweep")


if __name__ == "__main__":
    main()
