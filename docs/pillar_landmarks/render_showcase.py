"""Combined showcase of the three matured non-pagoda pillar concepts.

Renders each SHIP-READY landmark candidate the SAME way — a full upright hero
tower baked over a daytime sky+ground gradient, laid out in a labeled 3-cell
row — so the harbor-lighthouse, smock-windmill and moai-monolith can be judged
side by side at a fair, identical scale. House style follows
`tools/render_pagoda_comparison.py`: dark sheet, title band, per-cell sky/ground
gradient, a serial `#N` badge, slug + thesis caption and a SHIP-READY tag.

Each concept lives in its own sibling `render.py`; we import all three by file
path (their dirs are added to sys.path) so this stays standalone and does not
touch any `game/` module. Baked exactly like the pagoda comparison: MARGIN=64
gutters, CACHE_W=PIPE_W+128, a tall bottom section over GROUND_Y, PHASE=0.30
daytime palette from `biome.palette_for_phase`, cropped to the upright tower.

Run:  python docs/pillar_landmarks/render_showcase.py
Out:  docs/pillar_landmarks/showcase.png
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = pathlib.Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
sys.path.insert(0, str(_REPO))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import GROUND_Y, PIPE_W
from game import biome


def _load(slug: str):
    """Load a concept's sibling render.py under a unique module name so the three
    same-named files don't collide in sys.modules."""
    path = _HERE / slug / "render.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(f"landmark_{slug.replace('-', '_')}",
                                                  path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The three matured finals — (slug, candidate attr, thesis) in a fixed order.
CONCEPTS = [
    ("harbor-lighthouse", "candidate_harbor_lighthouse",
     "coastal lighthouse: curved bottle-taper shaft + glowing lantern head"),
    ("smock-windmill", "candidate_smock_windmill",
     "battered tar smock-mill throwing a 4-blade sail-X"),
    ("moai-monolith", "candidate_moai_monolith",
     "stacked ancestor idols with a red pukao crown"),
]

MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2     # full baked width (captures gutter overhang)
CACHE_H = GROUND_Y

PHASE = 0.30                      # daytime so every body reads clearly
SEED = 7                          # one deterministic seed for every cell

# Tall bottom tower so the full silhouette shows top-to-bottom, cropped upright.
GAP_Y, GAP_H = 130, 130
BOT_TOP = int(GAP_Y + GAP_H / 2)
TIP_Y = BOT_TOP - 10             # a little sky headroom above the tip
BASE_Y = GROUND_Y + 8            # a hair of ground below the plinth
TOWER_H = BASE_Y - TIP_Y


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def bake_tower(candidate, pal) -> pygame.Surface:
    """Bake one concept's bottom section (empty ceiling), crop the upright tower."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    bot_rect = pygame.Rect(MARGIN, BOT_TOP, PIPE_W, GROUND_Y - BOT_TOP)
    candidate(surf, top_rect, bot_rect, pal, SEED)
    tower = pygame.Surface((CACHE_W, TOWER_H), pygame.SRCALPHA)
    tower.blit(surf, (0, 0), pygame.Rect(0, TIP_Y, CACHE_W, TOWER_H))
    return tower


def cell_background(w: int, h: int, pal) -> pygame.Surface:
    """Daytime sky gradient with a thin ground band, matching the live look."""
    cell = pygame.Surface((w, h))
    ground_h = h - (TOWER_H - (BASE_Y - GROUND_Y))   # ground line at GROUND_Y
    sky_h = h - ground_h
    for y in range(sky_h):
        t = y / max(1, sky_h - 1)
        pygame.draw.line(cell, _lerp(pal["sky_top"], pal["horizon"], t), (0, y), (w, y))
    for y in range(sky_h, h):
        t = (y - sky_h) / max(1, h - sky_h)
        pygame.draw.line(cell, _lerp(pal["ground_top"], pal["ground_mid"], t),
                         (0, y), (w, y))
    return cell


def main() -> None:
    pal = biome.palette_for_phase(PHASE)
    mods = [(_load(slug), attr, thesis) for slug, attr, thesis in CONCEPTS]

    pad = 16
    cw, ch = CACHE_W, TOWER_H
    cap_h = 74                    # room for slug + thesis + ship-ready tag
    cell_h = ch + cap_h
    head_h = 60

    cols = len(CONCEPTS)
    sheet_w = pad + cols * (cw + pad)
    sheet_h = head_h + pad + cell_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    title = pygame.font.SysFont(None, 34)
    sub = pygame.font.SysFont(None, 19)
    slug_f = pygame.font.SysFont(None, 24, bold=True)
    thesis_f = pygame.font.SysFont(None, 18)
    serial_f = pygame.font.SysFont(None, 24, bold=True)
    tag_f = pygame.font.SysFont(None, 17, bold=True)

    sheet.blit(title.render("Skybit — new non-pagoda pillar concepts", True,
                            (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render("3 matured landmark towers  ·  identical bake  ·  "
                          "daytime palette (phase 0.30)  ·  all SHIP-READY", True,
                          (170, 172, 182)), (pad, 38))

    for i, ((mod, attr, thesis), (slug, _, _)) in enumerate(zip(mods, CONCEPTS)):
        candidate = getattr(mod, attr)
        x = pad + i * (cw + pad)
        y = head_h + pad

        cell = cell_background(cw, ch, pal)
        cell.blit(bake_tower(candidate, pal), (0, 0))
        sheet.blit(cell, (x, y))
        pygame.draw.rect(sheet, (60, 62, 72), pygame.Rect(x, y, cw, ch), 1)

        # Serial badge, top-left — a stable ID to talk about each design ("#2").
        num = serial_f.render(f"#{i + 1}", True, (24, 25, 30))
        bw, bh = num.get_width() + 12, num.get_height() + 6
        badge = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.rect(badge, (255, 224, 150), badge.get_rect(), border_radius=6)
        badge.blit(num, (6, 3))
        sheet.blit(badge, (x + 4, y + 4))

        # SHIP-READY tag, top-right — a green pill so status reads at a glance.
        tag = tag_f.render("SHIP-READY", True, (24, 25, 30))
        tw, th = tag.get_width() + 12, tag.get_height() + 6
        pill = pygame.Surface((tw, th), pygame.SRCALPHA)
        pygame.draw.rect(pill, (150, 214, 130), pill.get_rect(), border_radius=6)
        pill.blit(tag, (6, 3))
        sheet.blit(pill, (x + cw - tw - 4, y + 4))

        # Caption: slug, then wrapped thesis.
        cy = y + ch + 6
        sheet.blit(slug_f.render(f"{i + 1}. {slug}", True, (255, 224, 150)), (x + 4, cy))
        cy += 24
        line, lines = "", []
        for word in thesis.split():
            trial = (line + " " + word).strip()
            if thesis_f.size(trial)[0] > cw - 10:
                lines.append(line)
                line = word
            else:
                line = trial
        lines.append(line)
        for ln in lines[:2]:
            sheet.blit(thesis_f.render(ln, True, (200, 202, 212)), (x + 4, cy))
            cy += 16

    out = _HERE / "showcase.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
