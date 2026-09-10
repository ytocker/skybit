"""Render the live main menu by calling ``HUD.draw_menu`` directly.
Proves the V1 emboss treatment is wired into ``game/hud.py`` end-to-end.

Output:
  docs/screenshots/menu_variants/wired_live.png   1080 × 1920

Run from the repo root:

    PYTHONPATH=. python tools/render_menu_live.py
"""
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))
from render_hud_variants import draw_bg  # noqa: E402


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    from game.config import W, H
    from game.hud import HUD
    pygame.display.set_mode((W, H))

    surf = pygame.Surface((W, H))
    draw_bg(surf, scroll=120.0, phase=0.62)

    hud = HUD()
    hud.title_t = 0.0
    hud.draw_menu(surf, dt=0.0, best=842)

    out_dir = os.path.join("docs", "screenshots", "menu_variants")
    os.makedirs(out_dir, exist_ok=True)
    big = pygame.transform.smoothscale(surf, (W * 3, H * 3))
    out_path = os.path.join(out_dir, "wired_live.png")
    pygame.image.save(big, out_path)
    print(f"saved {out_path}  ({W * 3}x{H * 3})")


if __name__ == "__main__":
    sys.exit(main() or 0)
