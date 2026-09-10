"""Render the live TOP 10 leaderboard via the real game's
``HUD.draw_leaderboard`` so the screenshot reflects exactly what the
game shows on screen. Pass an HD-sized surface (W*3, H*3) so the
method skips its downsample-for-display step and writes the HD
intermediate directly into the surface.

Output:
  docs/screenshots/menu_variants/leaderboard_live.png   1080 × 1920

Run from the repo root:

    PYTHONPATH=. python tools/render_leaderboard_live.py
"""
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))
from render_hud_variants import draw_bg  # noqa: E402


SAMPLE_SCORES = [
    {"name": "Ace",      "score": 1284},
    {"name": "Pipsqueak","score": 1052},
    {"name": "Raven",    "score":  912},
    {"name": "Zephyr",   "score":  742},
    {"name": "Whiskey",  "score":  617},
    {"name": "Maverick", "score":  588},
    {"name": "Echo",     "score":  475},
    {"name": "Gunner",   "score":  402},
    {"name": "Piper",    "score":  351},
    {"name": "Tango",    "score":  287},
]
PLAYER_RANK = 4
S = 3   # game's internal supersample factor — must match HUD.draw_leaderboard


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    from game.config import W, H
    from game.hud import HUD
    pygame.display.set_mode((W, H))

    # Backdrop at native, smoothscaled up. The dim overlay on top is
    # near-opaque so the backdrop barely matters, but render it anyway
    # so the screenshot matches the in-game scene's bottom layer.
    bg_native = pygame.Surface((W, H))
    draw_bg(bg_native, scroll=120.0, phase=0.62)
    canvas = pygame.transform.smoothscale(bg_native, (W * S, H * S))

    hud = HUD()
    # title_t past the slide-in so the rows are settled in place
    hud.title_t = 1.0
    # The HD-sized canvas tells draw_leaderboard to skip its internal
    # downsample step and write the supersampled intermediate directly.
    hud.draw_leaderboard(canvas, dt=0.0, scores=SAMPLE_SCORES,
                          player_rank=PLAYER_RANK, cooldown=0.0)

    out_dir = os.path.join("docs", "screenshots", "menu_variants")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "leaderboard_live.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({W * S}x{H * S})")


if __name__ == "__main__":
    sys.exit(main() or 0)
