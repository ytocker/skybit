"""Headless per-frame cost profiler for the foreground day-arc.

Dev-only — NOT imported by the game and NOT bundled by pygbag (lives outside
game/). Renders the full foreground stack (floor + promenade + near lane) many
times at representative phases and reports ms/frame, so we can confirm the calm
baseline is cheap and the two peak events stay under the 16.6 ms budget.

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYTHONPATH=. python tools/profile_foreground.py
"""
import os
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from game import biome
import game.foreground as fg

# (label, phase, biome_time): biome_time large enough to be past the 7 s opening
# so the density curve is fully expressed.
_CASES = [
    ("calm late-morning", 0.30, 60.0),
    ("calm golden lull", 0.34, 60.0),
    ("FOOD-MARKET peak", 0.06, 60.0),
    ("NIGHT FESTIVAL peak", 0.66, 60.0),
    ("pre-dawn (near-empty)", 0.86, 60.0),
]

_FRAMES = 120
_BUDGET = 16.6


def _profile(phase, t0):
    pal = biome.palette_for_phase(phase)
    surf = pygame.Surface((W, H))
    # warm caches first (palette strips, scaled-cast bake) so we time steady state
    for i in range(8):
        sc = 1000 + i * 7
        fg.draw_foreground_floor(surf, sc, pal)
        fg.draw_promenade(surf, sc, pal, phase, t0 + i * 0.05)
        fg.draw_near_lane(surf, sc, pal, phase, t0 + i * 0.05)
    start = time.perf_counter()
    for i in range(_FRAMES):
        sc = 2000 + i * 7
        t = t0 + i * 0.05
        fg.draw_foreground_floor(surf, sc, pal)
        fg.draw_promenade(surf, sc, pal, phase, t)
        fg.draw_near_lane(surf, sc, pal, phase, t)
    return (time.perf_counter() - start) / _FRAMES * 1000.0


def main():
    print(f"foreground stack ms/frame  (budget {_BUDGET} ms, {_FRAMES} frames each)\n")
    worst = 0.0
    for label, phase, t0 in _CASES:
        ms = _profile(phase, t0)
        worst = max(worst, ms)
        flag = "  <-- OVER BUDGET" if ms > _BUDGET else ""
        print(f"  {label:<24} phase {phase:.2f}  {ms:6.2f} ms{flag}")
    print(f"\nworst case: {worst:.2f} ms  ({'PASS' if worst <= _BUDGET else 'FAIL'})")
    return 0 if worst <= _BUDGET else 1


if __name__ == "__main__":
    raise SystemExit(main())
