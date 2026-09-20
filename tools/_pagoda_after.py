"""AFTER panel: prayer-flag bunting strung pagoda to pagoda.

Dev-only, scratch. Companion to `_pagoda_before.py`, which captured the same
two daytime phases from the pre-change build (bunting on its own 149px
lattice, both ends in open sky). This renders the same crop with the row
anchored to gameplay pillars so the two can be compared side by side.

The promenade never reads gameplay objects, so pillars reach it as the
`pillar_anchors` signal that scenes pushes. This harness does not run a
World, so it synthesises a steady-state pillar row at the measured 341px
pitch and draws real pillars at those same anchors, proving the rope ends
land on pagoda bodies rather than on nothing.

    SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/_pagoda_after.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y, PIPE_W                # noqa: E402
from game import biome as _biome                              # noqa: E402
from game import foreground                                   # noqa: E402
from game import foreground_promenade as pr                   # noqa: E402
from game import foreground_props as fp                       # noqa: E402
from game.draw import get_sky_surface_biome                   # noqa: E402
from game.entities import Pipe                                # noqa: E402
from tools._family_showcase import _font                      # noqa: E402

CYCLE = 393.5
ROPE_Y = GROUND_Y - 118
SPACING = 341            # measured steady-state pillar pitch


def _anchors(scroll):
    first = int((scroll - 400) // SPACING)
    return tuple((k * SPACING, int(k * SPACING - scroll) + PIPE_W // 2)
                 for k in range(first, first + int((W + 800) / SPACING) + 2))


def _paint(phase, scroll, t, pipes):
    surf = pygame.Surface((W, H))
    pal = _biome.palette_for_phase(phase)
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal,
                                int(phase * _biome.PHASE_BUCKETS))
    sky.set_alpha(None)
    surf.blit(sky, (0, 0))
    foreground.draw_foreground_floor(surf, scroll, pal, phase)
    foreground.set_world_signals(clown_active=False, newbie_calm=False,
                                 score=int(t), near_misses=0,
                                 finale_active=False, wetness=0.0,
                                 snow_cover=0.0,
                                 pillar_anchors=_anchors(scroll))
    foreground.draw_promenade(surf, scroll, pal, phase, t)
    # Pillars paint after the promenade in the real scene, so the rope ends
    # tuck behind the pagoda bodies exactly as they do in play.
    for p in pipes:
        p.draw(surf, pal, phase)
    return surf


def _frame(p0):
    fp._LATCH.clear()
    fp._LATCH_SEEN.clear()
    foreground.reset_street()
    phase = p0
    t = phase * CYCLE
    scroll = t * 160.0
    pipes = []
    for wx, sx in _anchors(scroll):
        p = Pipe(sx - PIPE_W // 2, 300.0, 170)
        pipes.append(p)
    # settle the span latches the way a scrolled-in row would
    for _ in range(3):
        _paint(phase, scroll, t, [])
    return _paint(phase, scroll, t, pipes), phase


def main():
    panels = [(0.10, "early morning"), (0.30, "mid-morning")]
    pw, ph = W, 205
    crop_top = ROPE_Y - 46
    sheet = pygame.Surface((pw * 2 + 24, ph + 82))
    sheet.fill((8, 8, 20))
    sheet.blit(_font(14, bold=True).render(
        "AFTER — each strand runs pagoda to pagoda",
        True, (232, 226, 214)), (8, 8))
    lf = _font(11)
    for i, (p0, label) in enumerate(panels):
        fr, phase = _frame(p0)
        crop = fr.subsurface(pygame.Rect(0, crop_top, W, ph))
        x = 8 + i * (pw + 8)
        sheet.blit(crop, (x, 34))
        pygame.draw.rect(sheet, (70, 70, 90), (x, 34, pw, ph), 1)
        ry = 34 + (ROPE_Y - crop_top)
        pygame.draw.line(sheet, (220, 90, 90), (x, ry), (x + pw, ry), 1)
        sheet.blit(lf.render("y477 rope line (unchanged)", True, (232, 120, 120)),
                   (x + 4, ry - 13))
        sheet.blit(lf.render(f"{label}  (phase {phase:.3f})", True,
                             (198, 202, 212)), (x + 2, 34 + ph + 6))
    out = "docs/pagoda_anchors/after.png"
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
