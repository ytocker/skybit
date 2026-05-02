"""Render real-gameplay screenshots of the 3× powerup, one per variant.

Same pattern as the previous round's ghost-variant harness. Builds World
+ HUD directly, uses the local draw_bg() helper (copied from
tools/take_screenshots.py), spawns a single triple powerup at a known
visible spot, then re-renders the same deterministic frame 6 times —
once per icon variant — by monkey-patching `entities._draw_dollar_coin`
with each variant's draw function. Output:

    docs/triple_variants/v0.png … v5.png  — full 360×640 frames
    docs/triple_variants/compare.png      — labelled 2× zoom strip
                                            tightly cropped to the icon

Run from the repo root:

    PYTHONPATH=. python tools/render_triple_gameplay.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))
from render_triple_variants import VARIANTS  # noqa: E402


def draw_bg(surf, scroll=0.0, phase=0.62):
    # Same helper as tools/take_screenshots.py so the gameplay scene
    # matches the rest of the repo's screenshots.
    from game.config import W, H, GROUND_Y
    from game import biome as _biome
    from game.draw import (
        get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
    )
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    b = (a + 1) % buckets
    t = bucket_f - int(bucket_f)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
    sky_a.set_alpha(None); surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255)); surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)
    for i, (bx, by, sc, variant) in enumerate(
            ((20, 90, 0.9, 0), (180, 140, 1.1, 2), (60, 220, 0.8, 3),
             (230, 60, 0.7, 1), (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2 + i) * 3, sc, variant=variant)
    pal = pal_a
    draw_mountains(surf, scroll, GROUND_Y, W, pal['mtn_far'], pal['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                pal['ground_top'], pal['ground_mid'], (60, 40, 25))


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    from game.config import W, H
    screen = pygame.display.set_mode((W, H))

    from game.world import World
    from game.hud import HUD
    from game.entities import PowerUp
    from game import entities

    # Snapshot the original triple draw function so we can restore it
    # for the "0 — current" reference frame.
    original_triple_draw = entities._draw_dollar_coin

    world = World()
    world.score = 12
    world.coin_count = 7
    world.world_idle_tick(0.016)

    triple_x, triple_y = W * 0.62, H * 0.42
    world.powerups = [PowerUp(triple_x, triple_y, "triple")]
    # Lock pulse to a stable mid-animation phase so each variant renders
    # at the same animation moment.
    world.powerups[0].pulse = 1.2

    hud = HUD()
    hud.title_t = 0.8

    cells: "list[tuple[str, object]]" = [("0 — current", None)]
    cells += [VARIANTS[i] for i in (1, 2, 3, 4, 5)]

    out_dir = os.path.join("docs", "triple_variants")
    os.makedirs(out_dir, exist_ok=True)
    full_frames: "list[pygame.Surface]" = []

    for idx, (label, fn) in enumerate(cells):
        # Monkey-patch the alias used by entities.PowerUp._draw_triple.
        if fn is None:
            entities._draw_dollar_coin = original_triple_draw
        else:
            entities._draw_dollar_coin = fn

        # Render the gameplay frame using the same layer order as
        # scenes.App._render's STATE_PLAY branch.
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
    entities._draw_dollar_coin = original_triple_draw

    # Comparison strip — tight crop, 2× scale, labelled.
    crop_w = 88
    crop_h = 104
    crop_x = max(0, min(W - crop_w, int(triple_x - crop_w / 2)))
    crop_y = max(0, min(H - crop_h, int(triple_y - crop_h / 2)))
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
    font = pygame.font.SysFont(None, 24, bold=True)

    for i, (label, _fn) in enumerate(cells):
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
