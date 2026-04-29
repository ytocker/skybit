"""Render the chosen V5a GROW icon — tall green up-arrow BEHIND the
real in-game parrot sprite. Transparent background.

Run from repo root:  python tools/render_grow_final.py
Outputs:             screenshots/grow_final.png  (256×256, transparent)
"""
import os
import sys

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import parrot

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)


GREEN_HI  = ( 50, 220, 100)
GREEN_MID = ( 38, 190,  85)
GREEN_OUT = ( 28, 160,  70)


def draw_block_arrow(surf, cx, cy, head_w, shaft_w, total_h, fill, outline,
                     hi_band=None):
    """Vertical block-arrow centered at (cx, cy). Arrow head at TOP."""
    head_h = int(total_h * 0.42)
    top_y    = cy - total_h // 2
    head_bot = top_y + head_h
    bot_y    = cy + total_h // 2
    pts_out = [
        (cx,                  top_y),
        (cx + head_w // 2,    head_bot),
        (cx + shaft_w // 2,   head_bot),
        (cx + shaft_w // 2,   bot_y),
        (cx - shaft_w // 2,   bot_y),
        (cx - shaft_w // 2,   head_bot),
        (cx - head_w // 2,    head_bot),
    ]
    pygame.draw.polygon(surf, outline, pts_out)
    pts_in = [
        (cx,                      top_y + 2),
        (cx + head_w // 2 - 2,    head_bot - 1),
        (cx + shaft_w // 2 - 1,   head_bot - 1),
        (cx + shaft_w // 2 - 1,   bot_y - 1),
        (cx - shaft_w // 2 + 1,   bot_y - 1),
        (cx - shaft_w // 2 + 1,   head_bot - 1),
        (cx - head_w // 2 + 2,    head_bot - 1),
    ]
    pygame.draw.polygon(surf, fill, pts_in)
    if hi_band:
        pygame.draw.line(surf, hi_band,
                         (cx - shaft_w // 2 + 2, head_bot + 1),
                         (cx - shaft_w // 2 + 2, bot_y - 2), 2)
        pygame.draw.line(surf, hi_band,
                         (cx - 2, top_y + 4),
                         (cx - head_w // 4, head_bot - 2), 2)


# Source canvas — sized so the in-game parrot fits comfortably.
SIZE = 128
canvas = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
cx = cy = SIZE // 2

# Tall block-arrow as the backdrop. Tuned so the head clears the parrot's
# head and the shaft extends below the parrot's body.
draw_block_arrow(
    canvas, cx, cy,
    head_w=int(SIZE * 0.62),
    shaft_w=int(SIZE * 0.26),
    total_h=int(SIZE * 0.92),
    fill=GREEN_HI, outline=GREEN_OUT, hi_band=GREEN_MID,
)

# Real in-game parrot (mid-flap pose for liveliness). Scale to ~62% of canvas.
bird_src = parrot.FRAMES[1]
target_w = int(SIZE * 0.62)
ratio = target_w / bird_src.get_width()
target_h = int(bird_src.get_height() * ratio)
bird = pygame.transform.smoothscale(bird_src, (target_w, target_h))
canvas.blit(bird, (cx - bird.get_width() // 2, cy - bird.get_height() // 2))

# Upscale to 256 with nearest-neighbor for the close-up review.
final = pygame.transform.scale(canvas, (256, 256))
out = os.path.join(OUT_DIR, "grow_final.png")
pygame.image.save(final, out)
print("  saved", os.path.basename(out))
