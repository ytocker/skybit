"""Assembly-only showcase: the endgame clown lined up beside the five matured
EPIC event-boss concepts, all on ONE shared ground line at a MATCHED figure
scale so the lineup honestly shows the bosses out-scaling the chibi clown.

This composites the already-built per-figure renderers — it designs nothing.
Each boss keeps its own locked palette; we import each renderer's FIGURE draw
function directly (never its full review-sheet entry point) and call it onto a
shared neutral studio strip.

    SDL_VIDEODRIVER=dummy python tools/render_epic_showcase.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from game.pillar_staff import draw_chosen_hero
from tools.render_jester_variants import build_jester, JESTERS
from tools.render_epic_sovereign import build_sovereign
from tools.render_epic_lich import draw_lich
from tools.render_epic_wyrm import draw_wyrm
from tools.render_epic_leviathan import draw_leviathan
from tools.render_epic_reaper import draw_reaper


# Per-figure scale factors chosen so painted heights land near a common target
# (~400px) while the clown stays shortest — the honest relative-scale read the
# lineup exists to prove. Measured from each builder's own bounding box.
CELL_W = 320
CELL_H = 560
GROUND_FRAC = 0.90                 # the single shared ground line across all six
SS = 2                             # supersample each cell for crisp curves


def _studio_bg(surf, rect):
    """A single flat dark studio gradient behind the whole lineup so all six
    locked palettes read against neutral value — this is a lineup card, not a
    biome scene."""
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        c = (int(30 + (16 - 30) * t),
             int(32 + (18 - 32) * t),
             int(40 + (26 - 40) * t))
        pygame.draw.line(surf, c, (x, y + i), (x + w, y + i))


def _ground_shadow(surf, cx, gy, w):
    """A soft contact ellipse so each figure sits ON the shared ground line
    rather than floating."""
    sh = pygame.Surface((w, max(8, w // 6)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 110), sh.get_rect())
    surf.blit(sh, (cx - w // 2, gy - sh.get_height() // 3))


# Each entry: (caption, thesis, painter(figure_surface, cx, ground_y)).
# `painter` draws ONE figure at the matched lineup scale, feet/base on ground_y.

def _paint_clown(fig, cx, gy):
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    draw_chosen_hero(fig, cx, gy, build_jester=build_jester, spec=spec)


def _paint_sovereign(fig, cx, gy):
    # build_sovereign's line widths assume an INTEGER scale, so render it at a
    # clean integer K onto its own scratch, then smoothscale to the matched
    # lineup height before blitting (target ~400px figure at SS-space).
    K = 3
    src = pygame.Surface((280 * K, 360 * K), pygame.SRCALPHA)
    build_sovereign(src, 140 * K, 348 * K, K)
    bb = src.get_bounding_rect()
    crop = src.subsurface(bb).copy()
    target_h = int(400 * SS)                       # matched figure height in SS-space
    sc = target_h / bb.height
    out = pygame.transform.smoothscale(
        crop, (max(1, int(bb.width * sc)), target_h))
    fig.blit(out, (cx - out.get_width() // 2, gy - out.get_height()))


def _paint_lich(fig, cx, gy):
    draw_lich(fig, cx, gy, scale=1.02 * SS)


def _paint_wyrm(fig, cx, gy):
    # The horizontal serpent framed to fill the cell: tail low-left, the heavy
    # hard-browed skull reared toward the upper-right so it reads prominently.
    # It is epic by LENGTH, so it spans the cell width while its lowest coil
    # rests on the shared ground line. Scale is held so the full sprawl fits the
    # cell with the skull big enough to read its hard brow.
    w = CELL_W * SS
    draw_wyrm(fig, x0=int(w * 0.08), x1=int(w * 0.82),
              ymid=gy - int(130 * SS), scale=1.18 * SS)


def _paint_leviathan(fig, cx, gy):
    # The whale-god is a WIDE bulbous mass — the shortest boss, epic by bulk not
    # height. Held a touch smaller (and nudged right, since its jaw juts left of
    # the draw centre) so its full sprawl stays inside the cell while still
    # towering over the chibi clown.
    draw_leviathan(fig, cx + int(18 * SS), gy, scale=1.12 * SS, t=0.7)


def _paint_reaper(fig, cx, gy):
    draw_reaper(fig, cx, gy, scale=0.86 * SS, ss=1)


CELLS = [
    ("Endgame Clown",  "the live boss (scale ref)",      _paint_clown,     False),
    ("horned-sovereign", "infernal monarch + trident",   _paint_sovereign, True),
    ("frost-lich",     "obelisk sorcerer + soul-standard", _paint_lich,    True),
    ("storm-wyrm",     "sky-serpent dragon, epic by length", _paint_wyrm,  True),
    ("deep-leviathan", "abyssal whale-god + esca-lure",  _paint_leviathan, True),
    ("reaper-shade",   "faceless specter + great-scythe", _paint_reaper,   True),
]


def main():
    pygame.init()
    title_f = pygame.font.SysFont("dejavusans", 30, bold=True)
    cap_f = pygame.font.SysFont("dejavusans", 18, bold=True)
    th_f = pygame.font.SysFont("dejavusans", 14)

    n = len(CELLS)
    head_h = 64
    cap_h = 50
    W = CELL_W * n
    H = head_h + CELL_H + cap_h

    sheet = pygame.Surface((W, H))
    _studio_bg(sheet, (0, head_h, W, CELL_H))
    sheet.fill((14, 15, 22), (0, 0, W, head_h))
    sheet.fill((14, 15, 22), (0, head_h + CELL_H, W, cap_h))

    gy_local = int(CELL_H * GROUND_FRAC)             # shared ground line (cell-local)
    ground_y_sheet = head_h + gy_local

    for i, (name, thesis, painter, is_boss) in enumerate(CELLS):
        x0 = i * CELL_W
        # Supersampled figure scratch (transparent) so AA is clean on downscale.
        fig = pygame.Surface((CELL_W * SS, CELL_H * SS), pygame.SRCALPHA)
        cx = (CELL_W // 2) * SS
        gy = gy_local * SS
        painter(fig, cx, gy)
        small = pygame.transform.smoothscale(fig, (CELL_W, CELL_H))
        # Contact shadow on the studio strip, then the figure.
        _ground_shadow(sheet, x0 + CELL_W // 2, ground_y_sheet, int(CELL_W * 0.6))
        sheet.blit(small, (x0, head_h))
        # Cell divider + caption band.
        pygame.draw.line(sheet, (54, 58, 70), (x0, head_h), (x0, head_h + CELL_H), 1)
        cap = cap_f.render(name, True, (236, 238, 244) if is_boss else (255, 224, 120))
        sheet.blit(cap, (x0 + (CELL_W - cap.get_width()) // 2, head_h + CELL_H + 6))
        th = th_f.render(thesis, True, (170, 176, 190))
        sheet.blit(th, (x0 + (CELL_W - th.get_width()) // 2, head_h + CELL_H + 28))

    # The shared ground line drawn across the whole strip so the matched scale
    # (clown shortest) reads at a glance.
    pygame.draw.line(sheet, (96, 102, 116), (0, ground_y_sheet), (W, ground_y_sheet), 2)

    sheet.blit(title_f.render("EPIC EVENT-BOSS — candidate lineup", True,
                              (240, 242, 248)), (20, 16))
    sub = th_f.render("matched scale on one ground line — the clown is the size "
                      "reference; each boss keeps its own locked palette",
                      True, (160, 166, 182))
    sheet.blit(sub, (20, 46))

    out = "/home/user/skybit/docs/epic_boss/showcase.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
