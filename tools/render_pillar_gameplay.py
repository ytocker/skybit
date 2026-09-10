"""Render gameplay screenshots of the 5-tier pillar upgrade picker.

For each tier (0..5):
  - `install_tier(n)` monkey-patches the live pillar draw path.
  - `set_render_state(t, sun_phase)` seeds V2 rim-light and V3+ animations.
  - The same scene is rendered (3 pillars spanning the most
    decoration-rich variants: lungta / lantern / menhir).

Output:
  docs/pillar_variants/v0..v5.png    full 360 × 640 frames
  docs/pillar_variants/compare.png   labelled vertical strip across all tiers

Run from the repo root:

    PYTHONPATH=. python tools/render_pillar_gameplay.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))
from render_pillar_variants import install_tier, set_render_state, TIERS  # noqa: E402


def draw_bg(surf, scroll=0.0, phase=0.62):
    """Cluttered cloud + sky backdrop matching the live game look so the
    V4 readability bloom visibly helps the gap silhouette stand out."""
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

    from game.config import W, H, GAP_START
    from game.entities import Pipe
    from game import biome as _biome

    screen = pygame.display.set_mode((W, H))

    # 3 pillars chosen to span the most decoration-rich variants so each
    # tier's distinguishing features have somewhere to land:
    #   variant 1 (lungta)  — prayer flags + cairn + climbing vines
    #   variant 5 (lantern) — paper lanterns + bougainvillea + incense
    #   variant 7 (menhir)  — spiral-glow carvings + ribbons + raven
    # Pipe.seed % 8 picks the variant; gap_y differs per pillar so the
    # compare strip shows different silhouettes too.
    pillars = []
    for x, gap_y, seed in [
        ( 35, 300,  9),   # 9  % 8 == 1 → lungta
        (150, 360, 13),   # 13 % 8 == 5 → lantern
        (265, 290, 15),   # 15 % 8 == 7 → menhir
    ]:
        p = Pipe(float(x), float(gap_y), float(GAP_START))
        p.seed = seed
        pillars.append(p)

    # Dusk-ish phase: sun lights the lit side of each pillar from the
    # right (V2 rim-light visible) and decorations read in warm tones.
    phase = 0.62
    palette = _biome.palette_for_phase(phase)
    sun_phase = phase

    # Mid-sway animation time so V3+ shows lanterns tilted, mist breathed
    # in, vines off-axis. Frozen `t` means deterministic output.
    render_t = 4.20

    out_dir = os.path.join("docs", "pillar_variants")
    os.makedirs(out_dir, exist_ok=True)

    full_frames: "list[pygame.Surface]" = []

    for tier_idx, label in TIERS.items():
        with install_tier(tier_idx):
            set_render_state(t=render_t, sun_phase=sun_phase)
            draw_bg(screen, phase=phase)
            for p in pillars:
                p.draw(screen, palette)

            full_frames.append(screen.copy())
            out_path = os.path.join(out_dir, f"v{tier_idx}.png")
            pygame.image.save(screen, out_path)
            print(f"saved {out_path}  ({label})")

    # Comparison strip — zoomed crop centred on the LANTERN pillar (mid)
    # so the user can inspect rim-light, lantern sway, sparkles, and
    # foliage layering side-by-side.
    crop_x, crop_y, crop_w, crop_h = 95,  50, 220, 500
    SCALE = 1
    cell_w = crop_w * SCALE
    cell_h = crop_h * SCALE

    items = list(TIERS.items())
    n = len(items)
    GAP = 14
    LABEL_H = 30
    PAD = 18
    canvas_w = cell_w * n + GAP * (n - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((230, 232, 235))
    font = pygame.font.SysFont(None, 22, bold=True)

    for i, (idx, label) in enumerate(items):
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
