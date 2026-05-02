"""Render 5 light-blue `$` variants for the ghost+triple hat — preview only.

User locked in V5 (ghost + triple) but the current strong blue
(25, 60, 230) reads as too dark/saturated. They want light blue. This
script renders 5 candidate light-blue tones side-by-side in real
gameplay context so the user can pick one.

Output:
    docs/ghost_hat_blue_variants/v1..v5.png  full gameplay frames
    docs/ghost_hat_blue_variants/compare.png labelled 2× zoom strip

Run from the repo root:

    PYTHONPATH=. python tools/render_ghost_hat_blue_picker.py
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))

# Five distinct light-blue tones for the ghost-hat $.
# Each entry: (label, dollar, dollar_dk, dollar_hi)
BLUE_VARIANTS = [
    ("1 — ice blue",       (180, 220, 250), ( 90, 130, 180), (225, 240, 255)),
    ("2 — powder blue",    (155, 195, 235), ( 75, 115, 175), (210, 230, 250)),
    ("3 — sky blue",       (115, 175, 230), ( 50,  95, 165), (185, 215, 250)),
    ("4 — cornflower",     (130, 160, 230), ( 60,  90, 175), (190, 205, 245)),
    ("5 — light cobalt",   ( 90, 150, 220), ( 30,  70, 155), (170, 200, 245)),
]


def main():
    pygame.init()
    pygame.font.init()

    from game.config import W, H, KFC_DURATION, GHOST_DURATION, TRIPLE_DURATION
    screen = pygame.display.set_mode((W, H))

    from game.world import World
    from game.hud import HUD
    from game import parrot
    from game.dollar_parrot_ghost import build_spectral_frame
    from game.dollar_parrot_hat import (
        COMPOSITE_W, COMPOSITE_H, PARROT_DY, HAT_HX, HAT_HY,
    )
    # Reuse the themed-stovepipe + composite helpers from the main
    # stacked-combo preview tool (no game-code imports needed).
    from render_stacked_combos import (
        HAT_PALETTE_GHOST, _draw_stovepipe_themed, _hatted_composite,
        draw_bg, render_bird_at,
    )

    world = World()
    world.score = 12
    world.coin_count = 7
    world.world_idle_tick(0.016)
    world.kfc_timer = 0.0
    world.ghost_timer = GHOST_DURATION
    world.triple_timer = TRIPLE_DURATION
    world.bird.kfc_active = False
    world.bird.ghost_active = True
    world.bird.triple_active = True

    hud = HUD()
    hud.title_t = 0.8

    FRAME_IDX = 1
    angle = parrot._WING_ANGLES[FRAME_IDX]
    GHOST_ALPHA = 130

    bird_x, bird_y = W * 0.40, H * 0.42

    out_dir = os.path.join("docs", "ghost_hat_blue_variants")
    os.makedirs(out_dir, exist_ok=True)
    full_frames: "list[pygame.Surface]" = []

    for idx, (label, dollar, dollar_dk, dollar_hi) in enumerate(BLUE_VARIANTS, 1):
        # Build a per-variant ghost palette by overriding only the
        # dollar/dollar_dk/dollar_hi entries.
        pal = dict(HAT_PALETTE_GHOST)
        pal["dollar"] = dollar
        pal["dollar_dk"] = dollar_dk
        pal["dollar_hi"] = dollar_hi

        def _hat_fn(surf, hx, hy, P=pal):
            _draw_stovepipe_themed(surf, hx, hy, P)

        sprite = parrot._add_outline(_hatted_composite(
            build_spectral_frame(angle), _hat_fn,
            PARROT_DY, HAT_HX, HAT_HY, COMPOSITE_W, COMPOSITE_H,
        ))

        draw_bg(screen)
        for p in world.pipes:
            p.draw(screen, world.biome_palette)
        world.weather.draw(screen)
        for c in world.coins:
            c.draw(screen, kfc_active=False, triple_active=True)
        render_bird_at(screen, sprite, int(bird_x), int(bird_y),
                       tilt_deg=0.0, ghost_alpha=GHOST_ALPHA)
        hud.draw_play(screen, world, best=18)

        frame = screen.copy()
        full_frames.append(frame)
        out_path = os.path.join(out_dir, f"v{idx}.png")
        pygame.image.save(frame, out_path)
        print(f"saved {out_path}  ({label})")

    # Comparison strip — tight crop around bird, 2× zoom.
    crop_w = 130
    crop_h = 150
    crop_x = max(0, min(W - crop_w, int(bird_x - crop_w / 2)))
    crop_y = max(0, min(H - crop_h, int(bird_y - crop_h / 2 - 10)))
    SCALE = 2
    cell_w = crop_w * SCALE
    cell_h = crop_h * SCALE

    n = len(BLUE_VARIANTS)
    GAP = 22
    LABEL_H = 32
    PAD = 24
    canvas_w = cell_w * n + GAP * (n - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((230, 232, 235))
    font = pygame.font.SysFont(None, 22, bold=True)

    for i, (label, *_rest) in enumerate(BLUE_VARIANTS):
        x = PAD + i * (cell_w + GAP)
        y = PAD
        crop = full_frames[i].subsurface(
            pygame.Rect(crop_x, crop_y, crop_w, crop_h)
        ).copy()
        scaled = pygame.transform.scale(crop, (cell_w, cell_h))
        pygame.draw.rect(canvas, (60, 70, 100),
                         pygame.Rect(x - 1, y - 1, cell_w + 2, cell_h + 2),
                         width=1)
        canvas.blit(scaled, (x, y))
        lbl = font.render(label, True, (30, 35, 55))
        canvas.blit(lbl, (x + (cell_w - lbl.get_width()) // 2, y + cell_h + 8))

    compare_path = os.path.join(out_dir, "compare.png")
    pygame.image.save(canvas, compare_path)
    print(f"saved {compare_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    sys.exit(main() or 0)
