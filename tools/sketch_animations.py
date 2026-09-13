"""Render short MP4 animations of each ambient event for visual review.

Each event runs in isolation against the real game backdrop at its
appropriate biome phase. Output saved to docs/scene_sketches/animations/.

Run:
    python tools/sketch_animations.py
"""
import os, sys, pathlib, math, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import imageio.v2 as imageio
import numpy as np

from game.config import W, H, GROUND_Y, SCROLL_BASE
from game.world import World
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game import ambient as A


CYCLE = _biome.CYCLE_SECONDS
OUT_DIR = pathlib.Path(__file__).parent.parent / "docs" / "scene_sketches" / "animations"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _phase_to_time(phase: float) -> float:
    return ((phase - 0.04) % 1.0) * CYCLE


def _draw_backdrop(surf: pygame.Surface, world: World) -> None:
    palette = world.biome_palette
    buckets = _biome.PHASE_BUCKETS
    bf = (world.biome_phase % 1.0) * buckets
    a = int(bf) % buckets
    b = (a + 1) % buckets
    t = bf - int(bf)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y,
                                  _biome.palette_for_phase(a / buckets), a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y,
                                  _biome.palette_for_phase(b / buckets), b)
    sky_a.set_alpha(None)
    surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255))
        surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)
    scroll = world.bg_scroll
    for i, (bx, by, sc, variant) in enumerate((
            (20, 90, 0.9, 0), (180, 140, 1.1, 2),
            (60, 220, 0.8, 3), (230, 60, 0.7, 1),
            (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.5 * 0.3 + i) * 3, sc, variant=variant)
    draw_mountains(surf, scroll, GROUND_Y, W,
                   palette['mtn_far'], palette['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))


def _surf_to_array(surf: pygame.Surface):
    """pygame.Surface (RGB) → (H, W, 3) uint8 numpy array for imageio."""
    arr = pygame.surfarray.array3d(surf)
    # pygame stores (W, H, 3); imageio wants (H, W, 3)
    return np.transpose(arr, (1, 0, 2))


def _make_world(phase: float) -> World:
    world = World()
    world.biome_time = _phase_to_time(phase)
    world.ready_t = 0.0
    for _ in range(60):
        world.update(1 / 60)
    world.biome_time = _phase_to_time(phase)
    return world


def render_event_clip(slug: str, phase: float, duration_s: float,
                      setup_fn, fps: int = 30) -> None:
    """Render a single ambient event in isolation at the given phase.
    setup_fn(world) is called once after the world is built; it should
    spawn the desired event and clear the others."""
    world = _make_world(phase)
    # Replace the ambient controller with a fresh one so only the
    # requested event runs.
    world.ambient = A.AmbientScenes()
    setup_fn(world)

    n_frames = int(duration_s * fps)
    dt = 1 / fps
    out = OUT_DIR / f"{slug}.mp4"
    writer = imageio.get_writer(out, fps=fps, codec="libx264",
                                quality=8, pixelformat="yuv420p",
                                macro_block_size=1)
    try:
        for _ in range(n_frames):
            world.biome_time = _phase_to_time(phase)  # pin the sky
            # Advance bg_scroll like the running game does so foreground
            # parallax layers (and the world-anchored campfire) actually
            # scroll across the screen.
            world.bg_scroll += SCROLL_BASE * dt
            world.ambient.update(dt, world.biome_phase, world.biome_palette,
                                 world.bg_scroll)

            surf = pygame.Surface((W, H))
            _draw_backdrop(surf, world)
            world.ambient.draw(surf)
            writer.append_data(_surf_to_array(surf))
    finally:
        writer.close()
    print(f"wrote {out}  ({n_frames} frames @ {fps}fps)")


def setup_flock(world: World) -> None:
    world.ambient.flock = A._VFlock(world.biome_palette, H * 0.28)


def setup_fireworks(world: World) -> None:
    world.ambient.fireworks = A._Fireworks(rng=random.Random(1))


def setup_balloon(world: World) -> None:
    rng = random.Random(7)
    balloon = A._PaneledBalloon(rng)
    # Move the balloon so it starts visible at the right edge, not
    # off-screen — otherwise a short clip catches only the slow entry
    # and the balloon appears stationary.
    balloon.x = float(W * 0.90)
    world.ambient.balloon = balloon


def setup_parrots(world: World) -> None:
    world.ambient.parrots = A._ParrotFamily(random.Random(3))


def setup_blossoms(world: World) -> None:
    # Blossoms is continuous; just need to be in window. Pre-spawn a few
    # so the clip starts mid-stream rather than empty.
    for _ in range(60):
        world.ambient.blossoms.update(1 / 30, 0.90)


def setup_campfire(world: World) -> None:
    fire = A._Campfire(random.Random(11))
    # Start the campfire just inside the right edge so it's visible from
    # frame 1 and scrolls leftward across the screen.
    fire.x = float(W * 0.95)
    world.ambient.campfire = fire
    # Pre-tick sparks so the clip opens with sparks already rising.
    for _ in range(40):
        fire.update(1 / 30, world.bg_scroll)


CLIPS = [
    # slug,                phase, duration, setup
    ("anim_flock",         0.16,  5.0, setup_flock),
    ("anim_fireworks",     0.62,  6.0, setup_fireworks),
    ("anim_balloon",       0.16, 12.0, setup_balloon),
    ("anim_parrots",       0.05,  4.5, setup_parrots),
    ("anim_blossoms",      0.90,  4.0, setup_blossoms),
    ("anim_campfire",      0.62, 10.0, setup_campfire),
]


def main() -> None:
    for slug, phase, dur, setup in CLIPS:
        render_event_clip(slug, phase, dur, setup)


if __name__ == "__main__":
    main()
