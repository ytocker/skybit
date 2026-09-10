"""In-engine verification filmstrip for the integrated plant-family upgrade.

Unlike the round-2 review harness, this renders through the LIVE foreground draw
path (game.foreground.draw_foreground_floor / draw_promenade / draw_near_lane)
at DAY and NIGHT, with a real gameplay coin composited into frame, so we can
confirm the shipped art (not the harness copy) reads right and that no plant
pixel out-glows the coin — including against the brighter DAY coin gold.
"""
from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

from game.config import W, H, GROUND_Y  # noqa: E402
from game import foreground  # noqa: E402
from game import biome  # noqa: E402
from game.draw import COIN_GOLD, COIN_LIGHT, COIN_DARK  # noqa: E402

# DAY = phase 0.0; NIGHT = the NIGHT keyframe phase from biome.py.
PHASES = (("DAY", 0.0), ("NIGHT", 0.64375))


def _draw_coin(surf, cx, cy):
    """The real gameplay coin tones — the brightness yardstick. The DAY coin is
    the brightest gold; nothing on the deck may out-read it."""
    pygame.draw.circle(surf, COIN_DARK, (cx, cy), 8)
    pygame.draw.circle(surf, COIN_GOLD, (cx, cy), 7)
    pygame.draw.circle(surf, COIN_LIGHT, (cx - 2, cy - 2), 3)
    halo = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(halo, (255, 220, 80, 60), (15, 15), 14)
    surf.blit(halo, (cx - 15, cy - 15))


def _lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _render(phase, scroll, t):
    pal = biome.palette_for_phase(phase)
    surf = pygame.Surface((W, H))
    # Sky fill so the foreground band composites against a representative bg.
    surf.fill(pal.get('sky_bot', (170, 220, 245)))
    # The play floor + the deck band the plants sit on.
    foreground.draw_foreground_floor(surf, scroll, pal)
    foreground.draw_promenade(surf, scroll, pal, phase, t)
    foreground.draw_near_lane(surf, scroll, pal, phase, t)
    return surf, pal


# The plant primitives the upgrade owns — temporarily no-op'd to render a
# plant-FREE baseline so the probe can isolate the pixels the plants paint and
# measure ONLY those against the coin (other bright props are not our contract).
import game.draw as _gdraw           # noqa: E402
import game.pillar_variants as _gpv  # noqa: E402
import game.foreground_props as _gsp  # noqa: E402
import game.foreground_near_lane as _gnl  # noqa: E402

# Every module-level binding of a plant primitive across the live draw path. The
# near-lane re-imports them by name, so patching only game.draw would leave the
# scaled-up near plants in the baseline — we patch every binding.
_PLANT_BINDINGS = (
    (_gdraw, 'draw_side_shrub'), (_gdraw, 'draw_wuling_pine'),
    (_gpv, 'draw_cascading_vine'),
    (_gsp, 'draw_side_shrub'), (_gsp, 'draw_wuling_pine'),
    (_gsp, 'draw_cascading_vine'), (_gsp, '_draw_bamboo_canes'),
    (_gnl, 'draw_side_shrub'), (_gnl, 'draw_wuling_pine'),
    (_gnl, 'draw_cascading_vine'),
)


def _render_plantfree(phase, scroll, t):
    saved = [(m, n, getattr(m, n)) for m, n in _PLANT_BINDINGS]
    noop = lambda *a, **k: None
    for m, n in _PLANT_BINDINGS:
        setattr(m, n, noop)
    try:
        surf, _ = _render(phase, scroll, t)
    finally:
        for m, n, fn in saved:
            setattr(m, n, fn)
    return surf


def _max_plant_lum(surf, base, coin_rect):
    """Brightest PLANT pixel: only pixels that differ from the plant-free
    baseline (i.e. painted by a plant primitive) count, so unrelated props/sky
    don't pollute the coin comparison."""
    peak = 0.0
    for y in range(GROUND_Y - 70, H):
        for x in range(0, W):
            if coin_rect.collidepoint(x, y):
                continue
            c = surf.get_at((x, y))[:3]
            if c != base.get_at((x, y))[:3]:
                peak = max(peak, _lum(c))
    return peak


def main():
    margin = 12
    gap = 10
    label_h = 26
    # Two scroll offsets per phase so the bamboo/bonsai/flower/vine rotation all
    # land in frame across the strip.
    scrolls = (0, 180, 360, 540)
    cell_w = W
    cell_h = H
    cols = len(scrolls)
    rows = len(PHASES)

    sheet_w = margin * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = margin * 2 + label_h + rows * (cell_h + label_h + gap) + 30
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 26, 32))

    font = pygame.font.SysFont("dejavusans", 14, bold=True)
    small = pygame.font.SysFont("dejavusans", 11)

    sheet.blit(font.render(
        "INTEGRATED PLANT FAMILY (candidate E) — LIVE foreground.draw_* path   "
        "DAY + NIGHT, coin = glow yardstick", True, (236, 236, 240)),
        (margin, 8))

    y = margin + label_h
    coin_peaks = []
    for label, phase in PHASES:
        sheet.blit(font.render(label, True, (224, 220, 208)), (margin, y - 2))
        x = margin
        for scroll in scrolls:
            surf, pal = _render(phase, scroll, 10.0)
            base = _render_plantfree(phase, scroll, 10.0)
            coin_cx, coin_cy = 196, GROUND_Y - 30
            coin_lum = _lum(COIN_GOLD)
            coin_rect = pygame.Rect(coin_cx - 16, coin_cy - 16, 32, 32)
            plant_peak = _max_plant_lum(surf, base, coin_rect)
            # Drop a coin onto the deck in frame as the brightness reference.
            _draw_coin(surf, coin_cx, coin_cy)
            coin_peaks.append((label, scroll, coin_lum, plant_peak))
            sheet.blit(surf, (x, y + label_h))
            pygame.draw.rect(sheet, (70, 70, 80),
                             (x, y + label_h, cell_w, cell_h), 1)
            sheet.blit(small.render(f"scroll {scroll}", True, (200, 200, 210)),
                       (x + 4, y + 2))
            sheet.blit(small.render(
                f"coin~{coin_lum:.0f}  maxplant~{plant_peak:.0f}", True,
                (170, 230, 170) if plant_peak <= coin_lum else (255, 150, 150)),
                (x + 4, y + label_h + 2))
            x += cell_w + gap
        y += cell_h + label_h + gap

    worst = max(coin_peaks, key=lambda r: r[3])
    ok = all(p <= c for _, _, c, p in coin_peaks)
    sheet.blit(small.render(
        f"NOTE 5 CHECK: max plant luma {worst[3]:.0f} vs coin {worst[2]:.0f} "
        f"({worst[0]} scroll {worst[1]}) -> "
        f"{'PASS — nothing out-glows the coin' if ok else 'FAIL'}",
        True, (170, 230, 170) if ok else (255, 150, 150)),
        (margin, sheet_h - 22))

    out = "/home/user/skybit/docs/foreground_redesign/plants/integrated.png"
    pygame.image.save(sheet, out)
    print("WROTE", out, sheet.get_size())
    for lbl, sc, c, p in coin_peaks:
        print(f"  {lbl:5s} scroll {sc:4d}: coin {c:.0f}  max-plant {p:.0f}  "
              f"{'ok' if p <= c else 'OVER'}")


if __name__ == "__main__":
    main()
