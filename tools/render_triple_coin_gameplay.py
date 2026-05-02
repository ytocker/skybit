"""Render in-gameplay screenshots of 3X-mode coins, one per `$` variant.

Same harness pattern as the previous picker rounds. World + HUD built
directly; world.coins is replaced with a hand-positioned cluster so
multiple coins are visible at once. For each variant we monkey-patch
`entities._COIN_FACE_CACHE` with the variant's face surface so every
coin in the frame uses the new design. Output:

    docs/triple_coin_variants/v0.png … v5.png  full 360×640 frames
    docs/triple_coin_variants/compare.png      labelled 2× zoom strip

Run from the repo root:

    PYTHONPATH=. python tools/render_triple_coin_gameplay.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))
from render_triple_coin_variants import VARIANTS  # noqa: E402


def draw_bg(surf, scroll=0.0, phase=0.62):
    from game.config import W, H, GROUND_Y
    from game import biome as _biome
    from game.draw import (
        get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
    )
    buckets = _biome.PHASE_BUCKETS
    bf = (phase % 1.0) * buckets
    a = int(bf) % buckets
    b = (a + 1) % buckets
    t = bf - int(bf)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
    sky_a.set_alpha(None); surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255)); surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)
    for i, (bx, by, sc, var) in enumerate(
            ((20, 90, 0.9, 0), (180, 140, 1.1, 2), (60, 220, 0.8, 3),
             (230, 60, 0.7, 1), (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2 + i) * 3, sc, variant=var)
    pal = pal_a
    draw_mountains(surf, scroll, GROUND_Y, W, pal['mtn_far'], pal['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                pal['ground_top'], pal['ground_mid'], (60, 40, 25))


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    from game.config import W, H, COIN_R, TRIPLE_DURATION
    screen = pygame.display.set_mode((W, H))

    from game.world import World
    from game.hud import HUD
    from game.entities import Coin
    from game import entities

    world = World()
    world.score = 12
    world.coin_count = 7
    world.triple_timer = TRIPLE_DURATION   # so the HUD shows the active 3X bar
    world.bird.triple_active = True         # bird wears the hat parrot
    world.world_idle_tick(0.016)

    # Hand-place 3 coins at staggered spin phases so the user sees the
    # `$` in face-on, ~45°, and edge-leaning positions in the same frame.
    coin_positions = [
        (W * 0.55, H * 0.30),
        (W * 0.70, H * 0.45),
        (W * 0.45, H * 0.55),
    ]
    coins = []
    for i, (cx, cy) in enumerate(coin_positions):
        c = Coin(cx, cy)
        c.spin = i * (math.pi / 6)        # 0°, 30°, 60°
        c.float_t = i * 0.5
        coins.append(c)
    world.coins = coins
    world.powerups = []                    # remove pickups so the focus is coins

    hud = HUD()
    hud.title_t = 0.8

    cells: "list[tuple[str, callable | None]]" = [
        ("0 — current (parrot)", None),
    ]
    cells += [VARIANTS[i] for i in (1, 2, 3, 4, 5)]

    out_dir = os.path.join("docs", "triple_coin_variants")
    os.makedirs(out_dir, exist_ok=True)

    full_frames: "list[pygame.Surface]" = []

    for idx, (label, builder) in enumerate(cells):
        if builder is None:
            entities._COIN_FACE_CACHE = None  # rebuild on demand → original
        else:
            entities._COIN_FACE_CACHE = builder(COIN_R)

        draw_bg(screen)
        for p in world.pipes:
            p.draw(screen, world.biome_palette)
        world.weather.draw(screen)
        for c in world.coins:
            c.draw(screen, kfc_active=False)
        for m in world.powerups:
            m.draw(screen)
        world.bird.draw(screen, 0, 0)
        hud.draw_play(screen, world, best=18)

        frame = screen.copy()
        full_frames.append(frame)

        out_path = os.path.join(out_dir, f"v{idx}.png")
        pygame.image.save(frame, out_path)
        print(f"saved {out_path}  ({label})")

    # Restore so any later code in this process sees the original.
    entities._COIN_FACE_CACHE = None

    # Comparison strip — tight crop around the centre coin, 2× zoom.
    crop_w = 140
    crop_h = 120
    crop_x = max(0, min(W - crop_w, int(coin_positions[1][0] - crop_w / 2)))
    crop_y = max(0, min(H - crop_h, int(coin_positions[1][1] - crop_h / 2)))
    SCALE = 2
    cell_w = crop_w * SCALE
    cell_h = crop_h * SCALE

    n = len(cells)
    GAP = 24
    LABEL_H = 30
    PAD = 24
    canvas_w = cell_w * n + GAP * (n - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((230, 232, 235))
    font = pygame.font.SysFont(None, 22, bold=True)

    for i, (label, _b) in enumerate(cells):
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
