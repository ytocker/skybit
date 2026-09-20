"""BEFORE panel: today's prayer-flag bunting, whose spans end in empty sky.

Dev-only, scratch — renders the live build unmodified so the showcase has a
truthful reference panel to compare the anchor-post concepts against.

Scrolls the street for a while before capturing: the span latches decide at
slot ENTRY, so a cold single frame under-reports the row (a first attempt
caught one span mostly off-screen left and read as "no bunting at all").
The capture frame is then chosen as the one whose span endpoints sit
furthest inside the viewport, so the figure shows the rope ENDS — which is
the whole point of the comparison.

    SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/_pagoda_before.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y                       # noqa: E402
from game import biome as _biome                             # noqa: E402
from game import foreground                                  # noqa: E402
from game import foreground_promenade as pr                  # noqa: E402
from game import foreground_props as fp                      # noqa: E402
from game.draw import get_sky_surface_biome                  # noqa: E402
from tools._family_showcase import _font                     # noqa: E402

CYCLE = 393.5
ROPE_Y = GROUND_Y - 118

_spans = []
_real_flags = pr.draw_prayer_flags


def _spy(surf, x1, y1, x2, y2, n=7, **kw):
    _spans.append((x1, x2))
    return _real_flags(surf, x1, y1, x2, y2, n)


pr.draw_prayer_flags = _spy


def _paint(phase, scroll, t):
    surf = pygame.Surface((W, H))
    pal = _biome.palette_for_phase(phase)
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal,
                                int(phase * _biome.PHASE_BUCKETS))
    sky.set_alpha(None)
    surf.blit(sky, (0, 0))
    foreground.draw_foreground_floor(surf, scroll, pal, phase)
    foreground.draw_promenade(surf, scroll, pal, phase, t)
    return surf


def _best_frame(p0):
    """Scroll ~9 s and keep the frame whose bunting endpoints are most inside
    the viewport, so the panel actually shows a rope END and not a span that
    happens to run off both edges."""
    fp._LATCH.clear()
    fp._LATCH_SEEN.clear()
    foreground.reset_street()
    best = (-1e9, None, None)
    for i in range(90):
        phase = (p0 + i * 0.0004) % 1.0
        t = phase * CYCLE
        scroll = t * 160.0
        foreground.set_world_signals(clown_active=False, newbie_calm=False,
                                     score=int(t), near_misses=0,
                                     finale_active=False, wetness=0.0,
                                     snow_cover=0.0)
        _spans.clear()
        surf = _paint(phase, scroll, t)
        if not _spans:
            continue
        # score = how far the nearest endpoint sits from either screen edge
        score = max(min(x, W - x) for sp in _spans for x in sp)
        if score > best[0]:
            best = (score, surf, phase)
    return best[1], best[2]


def main():
    panels = [(0.10, "early morning — no lamp posts installed yet"),
              (0.30, "mid-morning — lamps up, still 26px below the rope")]
    pw, ph = W, 205
    crop_top = ROPE_Y - 46
    sheet = pygame.Surface((pw * 2 + 24, ph + 82))
    sheet.fill((8, 8, 20))
    sheet.blit(_font(14, bold=True).render(
        "BEFORE — the rope hangs at y477 with nothing at either end",
        True, (232, 226, 214)), (8, 8))
    lf = _font(11)
    for i, (p0, label) in enumerate(panels):
        fr, phase = _best_frame(p0)
        if fr is None:
            raise RuntimeError(f"no bunting span found near phase {p0}")
        crop = fr.subsurface(pygame.Rect(0, crop_top, W, ph))
        x = 8 + i * (pw + 8)
        sheet.blit(crop, (x, 34))
        pygame.draw.rect(sheet, (70, 70, 90), (x, 34, pw, ph), 1)
        ry = 34 + (ROPE_Y - crop_top)
        pygame.draw.line(sheet, (220, 90, 90), (x, ry), (x + pw, ry), 1)
        sheet.blit(lf.render("y477 rope line", True, (232, 120, 120)),
                   (x + 4, ry - 13))
        sheet.blit(lf.render(f"{label}  (phase {phase:.3f})", True,
                             (198, 202, 212)), (x + 2, 34 + ph + 6))
    out = "docs/pagoda_anchors/original.png"
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
