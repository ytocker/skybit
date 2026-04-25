"""Render the 4 staged README screenshots.

Each scene picks a biome, sets up the world, then forces the bird into a
specific in-game moment (between pillars / approaching coins / near a
power-up / gliding) so the screenshots read as real gameplay rather than
empty test fixtures.

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

from game.config import W, H, GROUND_Y, PIPE_W, COIN_R
from game.world import World
from game.entities import Coin, PowerUp
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)

CYCLE = _biome.CYCLE_SECONDS

# 4 staged scenes for the README, in display order.
SCENES = [
    dict(slug="01_start_between_pillars", phase=0.00, kind="between_pillars",
         seed=11, sim_ticks=60),
    dict(slug="02_coins_run",             phase=0.18, kind="coins",
         seed=29, sim_ticks=120),
    dict(slug="03_night_powerup",         phase=0.62, kind="powerup",
         seed=53, sim_ticks=150),
    dict(slug="04_glide_sunrise",         phase=0.90, kind="glide",
         seed=7,  sim_ticks=210),
]

OUT_DIR = pathlib.Path(__file__).parent.parent / "docs" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _phase_to_time(phase: float) -> float:
    # phase_for_time adds a 0.04 morning offset; invert it.
    return ((phase - 0.04) % 1.0) * CYCLE


def _stage_bird(world: World, kind: str) -> None:
    """Snap the bird into a believable mid-flight pose for this scene."""
    bird = world.bird
    bird.alive = True
    # Find the nearest visible pipe to anchor the bird inside its gap.
    visible = [p for p in world.pipes if -PIPE_W < p.x < W]
    if visible:
        nearest = min(visible, key=lambda p: abs(p.x - bird.x))
        bird.y = nearest.gap_y
    if kind == "glide":
        # Slight downward velocity → tilt-down "gliding" pose
        bird.vy = 220
    else:
        # Slight upward velocity → tilt-up "just-flapped" pose
        bird.vy = -120


def _stage_coins(world: World) -> None:
    """Drop a small horizontal arc of coins right in front of the bird so the
    'about to grab coins' framing reads even on a still frame."""
    bx = world.bird.x
    by = world.bird.y
    for i, dx in enumerate((28, 50, 72, 94)):
        # Subtle vertical arc so it reads as a pickup trail, not a row.
        dy = int(math.sin(i * 0.6) * 10)
        world.coins.append(Coin(bx + dx, by + dy))


def _stage_powerup(world: World, kind: str = "triple") -> None:
    """Spawn a power-up just to the right of the bird so it's clearly the
    next thing the player would pick up."""
    bx = world.bird.x
    by = world.bird.y
    # Clear any auto-spawned ones so the staged one is unambiguous.
    world.powerups.clear()
    world.powerups.append(PowerUp(bx + 60, by - 6, kind=kind))


def render_scene(scene: dict) -> pygame.Surface:
    random.seed(scene["seed"])
    world = World()
    world.biome_time = _phase_to_time(scene["phase"])
    # Skip the 1-second "TAP TO FLY" hold so pipes scroll from frame 1.
    world.ready_t = 0.0

    # Step the world forward (with periodic flaps) so multiple pipes are
    # on-screen and the bird hasn't fallen.
    dt = 1 / 60
    for tick in range(scene["sim_ticks"]):
        if tick % 24 == 0:
            world.bird.flap()
        world.update(dt)

    # Restore biome_time so the rendered palette matches the keyframe.
    world.biome_time = _phase_to_time(scene["phase"])

    _stage_bird(world, scene["kind"])
    if scene["kind"] == "coins":
        _stage_coins(world)
    elif scene["kind"] == "powerup":
        _stage_powerup(world)

    palette = world.biome_palette

    surf = pygame.Surface((W, H))

    # ── Sky (matches scenes._draw_background) ──
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

    # ── Pipes, weather, coins, power-ups, bird ──
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
    # Wipe any old biome_*.png from previous runs.
    for old in OUT_DIR.glob("biome_*.png"):
        old.unlink()
    for scene in SCENES:
        surf = render_scene(scene)
        out = OUT_DIR / f"{scene['slug']}.png"
        pygame.image.save(surf, out)
        print(f"wrote {out}  (kind={scene['kind']}, phase={scene['phase']:.2f})")


if __name__ == "__main__":
    main()
