"""Render the wired-in gameplay HUD by calling the real
``HUD.draw_play()`` method against a minimal mock world. Proves that
the changes to ``game/hud.py`` produce the chosen design end-to-end
(not just match the mockup).

Output:
  docs/screenshots/hud_variants/wired_live.png   1080 × 1920

Run from the repo root:

    PYTHONPATH=. python tools/render_hud_live.py
"""
import os
import random
import sys
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))
from render_hud_variants import draw_bg, draw_pillar_context  # noqa: E402


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    from game.config import W, H
    from game.hud import HUD
    pygame.display.set_mode((W, H))

    # Backdrop at native res, then upscale 3× for the saved screenshot.
    surf = pygame.Surface((W, H))
    palette = draw_bg(surf, scroll=120.0, phase=0.62)
    draw_pillar_context(surf, palette)

    # Mock world — only the attributes ``draw_play`` reads.
    bird  = SimpleNamespace(y=200.0)
    world = SimpleNamespace(
        score=127,
        coin_count=23,
        bird=bird,
        ready_t=0.0,
        triple_timer=0.0, magnet_timer=0.0, slowmo_timer=0.0,
        kfc_timer=0.0,    ghost_timer=0.0,  grow_timer=0.0,
        reverse_timer=0.0,
        float_texts=[],
    )

    hud = HUD()
    hud.draw_play(surf, world, best=842, paused=False)

    out_dir = os.path.join("docs", "screenshots", "hud_variants")
    os.makedirs(out_dir, exist_ok=True)
    big = pygame.transform.smoothscale(surf, (W * 3, H * 3))
    out_path = os.path.join(out_dir, "wired_live.png")
    pygame.image.save(big, out_path)
    print(f"saved {out_path}  ({W * 3}x{H * 3})")


if __name__ == "__main__":
    sys.exit(main() or 0)
