"""Render one full gameplay frame per biome keyframe and save under
`docs/screenshots/biome_<name>.png`. Mirrors what scenes.App._render()
draws so the screenshots match what the player actually sees.

Run:
    python tools/biome_snapshots.py
"""
import os, sys, pathlib, math, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))   # needed for fonts / image.save

from game.config import W, H, GROUND_Y
from game.world import World
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)

CYCLE = _biome.CYCLE_SECONDS

# (slug, label, target biome phase) — one screenshot per keyframe in biome.py.
SCENES = [
    ("day",         "Day",         0.00),
    ("golden_hour", "Golden hour", 0.18),
    ("sunset",      "Sunset",      0.32),
    ("dusk",        "Dusk",        0.48),
    ("night",       "Night",       0.62),
    ("predawn",     "Pre-dawn",    0.78),
    ("sunrise",     "Sunrise",     0.90),
]

OUT_DIR = pathlib.Path(__file__).parent.parent / "docs" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def render_scene(phase: float) -> pygame.Surface:
    # Deterministic pipe variety across all 7 screenshots
    random.seed(int(phase * 1000) + 17)

    world = World()
    # Drive biome_phase to the keyframe by setting biome_time directly
    # (phase_for_time adds a 0.04 morning offset).
    world.biome_time = ((phase - 0.04) % 1.0) * CYCLE

    # Step the world forward so multiple pipes are on-screen.
    dt = 1 / 60
    for _ in range(180):  # 3 seconds
        world.update(dt)

    # Reset biome_time after the simulation so the rendered palette is the
    # phase we asked for, not the slightly-advanced phase after 180 ticks.
    world.biome_time = ((phase - 0.04) % 1.0) * CYCLE
    palette = world.biome_palette

    surf = pygame.Surface((W, H))

    # ── Sky (matches scenes._draw_background) ──────────────────────────────
    buckets = _biome.PHASE_BUCKETS
    bf = (world.biome_phase % 1.0) * buckets
    a = int(bf) % buckets
    b = (a + 1) % buckets
    t = bf - int(bf)
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

    # ── Clouds, mountains, ground ──
    scroll = world.bg_scroll
    cloud_phase = 1.5
    for i, (bx, by, sc, variant) in enumerate((
            (20, 90, 0.9, 0), (180, 140, 1.1, 2),
            (60, 220, 0.8, 3), (230, 60, 0.7, 1),
            (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(cloud_phase * 0.3 + i) * 3,
                   sc, variant=variant)
    draw_mountains(surf, scroll, GROUND_Y, W, palette['mtn_far'], palette['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))

    # ── Pipes (the variant pillars), coins, power-ups, bird ──
    for p in world.pipes:
        p.draw(surf, palette)
    world.weather.draw(surf)
    for c in world.coins:
        c.draw(surf)
    for m in world.powerups:
        m.draw(surf)
    world.bird.draw(surf, 0, 0)
    return surf


def main() -> None:
    for slug, label, phase in SCENES:
        surf = render_scene(phase)
        out = OUT_DIR / f"biome_{slug}.png"
        pygame.image.save(surf, out)
        print(f"wrote {out}  (biome={label}, phase={phase:.2f})")


if __name__ == "__main__":
    main()
