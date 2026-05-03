"""Render in-gameplay screenshots of the GROW-mode parrot, one per
hi-res variant. Mirrors the prior `render_grow_gameplay.py` workflow.

For each variant:
  - Build the 4 hi-res wing frames at the variant's resolution.
  - Monkey-patch `parrot.FRAMES` to those hi-res frames.
  - Set `game.config.GROW_SCALE = 1.0` so `Bird.draw` does NOT
    smoothscale-up (the frames are already at grow size).
  - Clear `parrot._rot_cache` so cached rotations get rebuilt against
    the new frames.
  - Render the scene with `bird.grow_active = True`.

v0 uses the original blurry path (no patching) for direct comparison.

Output:
  docs/grow_parrot_variants/v0..v5.png    full 360 × 640 frames
  docs/grow_parrot_variants/compare.png   labelled 2× zoom strip

Run from the repo root:

    PYTHONPATH=. python tools/render_grow_parrot_gameplay.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))
from render_grow_parrot_variants import BUILDERS, build_frames  # noqa: E402


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

    from game.config import W, H
    screen = pygame.display.set_mode((W, H))

    import game.config as _cfg
    from game import parrot
    from game.world import World
    from game.hud import HUD

    original_FRAMES     = parrot.FRAMES
    original_GROW_SCALE = _cfg.GROW_SCALE

    world = World()
    world.score = 12
    world.coin_count = 7
    world.world_idle_tick(0.016)

    # Activate grow buff so the bird draws at grow size AND the HUD shows
    # the active-buff bar with the velvet mushroom emblem (verifies the
    # round-19 ship in passing).
    world.bird.grow_active = True
    world.grow_timer = 6.0

    hud = HUD()
    hud.title_t = 0.8

    out_dir = os.path.join("docs", "grow_parrot_variants")
    os.makedirs(out_dir, exist_ok=True)

    full_frames: "list[pygame.Surface]" = []

    for idx, (label, builder) in BUILDERS.items():
        if idx == 0:
            # Reference: keep the live FRAMES + GROW_SCALE so we capture the
            # exact current blurry path.
            parrot.FRAMES = original_FRAMES
            _cfg.GROW_SCALE = original_GROW_SCALE
        else:
            parrot.FRAMES = build_frames(builder)
            # Frames are already at the grow display size — disable the
            # in-method upscale so Bird.draw blits at 1×.
            _cfg.GROW_SCALE = 1.0

        # Cached rotations were built against the OLD frames; flush so the
        # next get_parrot() rebuilds against the patched FRAMES.
        parrot._rot_cache.clear()

        draw_bg(screen)
        for p in world.pipes:
            p.draw(screen, world.biome_palette)
        world.weather.draw(screen)
        for c in world.coins:
            c.draw(screen, kfc_active=False, triple_active=False)
        for m in world.powerups:
            m.draw(screen)
        world.bird.draw(screen, 0, 0)
        hud.draw_play(screen, world, best=18)

        frame = screen.copy()
        full_frames.append(frame)

        out_path = os.path.join(out_dir, f"v{idx}.png")
        pygame.image.save(frame, out_path)
        print(f"saved {out_path}  ({label})")

    # Restore so any subsequent code in this process sees the live state.
    parrot.FRAMES = original_FRAMES
    _cfg.GROW_SCALE = original_GROW_SCALE
    parrot._rot_cache.clear()

    # Comparison strip — tight crop around the bird, 2× zoom so sharpness
    # differences read clearly.
    bird_cx = int(world.bird.x)
    bird_cy = int(world.bird.y)
    crop_w = 140
    crop_h = 130
    crop_x = max(0, min(W - crop_w, bird_cx - crop_w // 2))
    crop_y = max(0, min(H - crop_h, bird_cy - crop_h // 2))
    SCALE = 2
    cell_w = crop_w * SCALE
    cell_h = crop_h * SCALE

    items = list(BUILDERS.items())
    n = len(items)
    GAP = 24
    LABEL_H = 30
    PAD = 24
    canvas_w = cell_w * n + GAP * (n - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((230, 232, 235))
    font = pygame.font.SysFont(None, 24, bold=True)

    for i, (idx, (label, _b)) in enumerate(items):
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
