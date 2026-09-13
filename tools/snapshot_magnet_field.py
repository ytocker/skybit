"""Render the magnet power-up's force-field at native scale and save a PNG.

Mirrors the draw code in game/scenes.py::PlayScene._render so the
screenshot tracks whatever pulse / palette / radius is currently live
in the v4_skybit_powerups branch. Run from the repo root:

    python tools/snapshot_magnet_field.py
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import pygame
pygame.init()

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import W, H, GROUND_Y, BIRD_X, MAGNET_RADIUS
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.entities import Bird, Coin
from game.scenes import _magnet_hex_grid


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "screenshots", "powerups", "magnet",
)
os.makedirs(OUT_DIR, exist_ok=True)


def draw_bg(surf, scroll=0.0, phase=0.62):
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    b = (a + 1) % buckets
    t = bucket_f - int(bucket_f)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
    sky_a.set_alpha(None)
    surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255))
        surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)
    for i, (bx, by, sc, variant) in enumerate((
            (20,  90, 0.9, 0),
            (180, 140, 1.1, 2),
            (60,  220, 0.8, 3),
            (230, 60, 0.7, 1),
            (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2 + i) * 3, sc, variant=variant)
    draw_mountains(surf, scroll, GROUND_Y, W,
                   pal_a['mtn_far'], pal_a['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                pal_a['ground_top'], pal_a['ground_mid'], (60, 40, 25))


def draw_magnet_field(surf, bird_x, bird_y, cloud_phase):
    """Lifted verbatim from game/scenes.py::PlayScene._render so the
    on-disk PNG matches the live in-game render exactly. Keep this in
    sync if the in-game code changes."""
    t_pulse = cloud_phase * 5.5
    rad = MAGNET_RADIUS
    field = pygame.Surface((rad * 2 + 8, rad * 2 + 8), pygame.SRCALPHA)
    lcx, lcy = rad + 4, rad + 4

    BREATH = 0.30
    s_outer = math.sin(t_pulse + 0.0)
    u_outer = (s_outer + 1) / 2
    outer_factor = 1.0 - BREATH * (1.0 - u_outer)
    glow_rad = rad * outer_factor

    GLOW_COL = (245, 175, 40)
    for i in range(18, 0, -1):
        r = int(glow_rad * i / 18)
        inner_t = i / 18
        bell = math.exp(-((inner_t - 0.85) ** 2) / 0.15)
        a = int(72 * bell)
        if a > 0:
            pygame.draw.circle(field, (*GLOW_COL, a), (lcx, lcy), r)

    field.blit(_magnet_hex_grid(int(rad)), (0, 0))

    AA_COL = (255, 240, 180)
    for rfac, phase, alpha, width, breath_scale, ring_col in (
            (1.00, 0.0, 180, 3, 1.00, (255, 220, 100)),
            (0.78, 0.6, 140, 2, 0.85, (255, 195,  60)),
            (0.55, 1.2, 100, 2, 0.70, (235, 165,  35))):
        amp = BREATH * breath_scale
        s = math.sin(t_pulse + phase)
        u = (s + 1) / 2
        rr = int(rad * rfac * (1.0 - amp * (1.0 - u)))
        pygame.draw.circle(field, (*AA_COL, alpha // 3),
                           (lcx, lcy), rr + 1, width)
        pygame.draw.circle(field, (*AA_COL, alpha // 3),
                           (lcx, lcy), rr - 1, width)
        pygame.draw.circle(field, (*ring_col, alpha),
                           (lcx, lcy), rr, width)

    surf.blit(field, (int(bird_x) - lcx, int(bird_y) - lcy))


def main():
    screen = pygame.Surface((W, H))
    draw_bg(screen)

    bird = Bird()
    bird.x = BIRD_X + 20
    bird.y = 280

    # Spread a few coins inside MAGNET_RADIUS so the field visibly
    # surrounds something to pull — without coins the rings look
    # decorative, which understates what the power-up actually does.
    coin_positions = (
        (bird.x + 55, bird.y - 30),
        (bird.x + 70, bird.y + 25),
        (bird.x - 50, bird.y + 35),
        (bird.x - 30, bird.y - 55),
        (bird.x + 30, bird.y + 70),
    )
    coins = [Coin(cx, cy) for cx, cy in coin_positions]
    # Stagger the spin so coins don't all show the same edge.
    for i, c in enumerate(coins):
        c.spin = i * 0.5
    for c in coins:
        c.draw(screen)

    bird.draw(screen, 0, 0)

    # cloud_phase picked so the rings sit roughly mid-pulse — full
    # outer ring visible, mid ring slightly inside, inner ring tight.
    draw_magnet_field(screen, bird.x, bird.y, cloud_phase=0.18)

    out_path = os.path.join(OUT_DIR, "field_current.png")
    pygame.image.save(screen, out_path)
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
