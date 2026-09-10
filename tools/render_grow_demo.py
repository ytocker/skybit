"""Render demo screenshots for the GROW power-up.

Produces two PNGs in screenshots/:
  grow_icon.png       — close-up of the world pickup icon (bird + green up-arrows)
  grow_big_bird.png   — sample game frame with the bird at 2x scale (GROW active)

Run from repo root:  python tools/render_grow_demo.py
"""
import os
import sys
import math

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import W, H, GROUND_Y
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground
from game.entities import Bird, Pipe, PowerUp
from game.world import World
from game.hud import HUD


OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)


def draw_bg(surf, scroll=0, phase=0.55):
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
        sky_b.set_alpha(int(t * 255)); surf.blit(sky_b, (0, 0)); sky_b.set_alpha(None)
    for i, (bx, by, sc, variant) in enumerate(
            ((20, 90, 0.9, 0), (180, 140, 1.1, 2), (60, 220, 0.8, 3),
             (230, 60, 0.7, 1), (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2 + i) * 3, sc, variant=variant)
    pal = pal_a
    draw_mountains(surf, scroll, GROUND_Y, W, pal['mtn_far'], pal['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll, pal['ground_top'], pal['ground_mid'], (60, 40, 25))
    return pal


# ── 1. Icon close-up ─────────────────────────────────────────────────────────
ICON_W = 256
icon = pygame.Surface((ICON_W, ICON_W), pygame.SRCALPHA)
# Subtle dark vignette so green arrows pop on the README/PR view
pygame.draw.rect(icon, (12, 8, 38, 235), icon.get_rect(), border_radius=24)
# Render the icon onto a small surface, then upscale 4x with no smoothing
# so the procedural pixel-shapes stay crisp.
inner = pygame.Surface((ICON_W // 4, ICON_W // 4), pygame.SRCALPHA)
pu = PowerUp(inner.get_width() // 2, inner.get_height() // 2, "grow")
pu.pulse = 1.0
pu.draw(inner)
icon.blit(pygame.transform.scale(inner, (ICON_W, ICON_W)), (0, 0))
pygame.image.save(icon, os.path.join(OUT_DIR, "grow_icon.png"))
print("  saved grow_icon.png")


# ── 2. Big-bird scene ────────────────────────────────────────────────────────
scene = pygame.Surface((W, H))
pal = draw_bg(scene, phase=0.55)

# Two pillars framing the gap so the size contrast is obvious.
p1 = Pipe(60,  H * 0.42, 220)
p2 = Pipe(240, H * 0.50, 200)
p1.draw(scene, pal)
p2.draw(scene, pal)

# Bird at 2x scale, mid-flap, slight downward tilt.
bird = Bird()
bird.x = W * 0.42
bird.y = H * 0.46
bird.vy = 80.0
bird.frame_t = 1.7      # mid-flap pose
bird.grow_active = True
bird.draw(scene, 0, 0)

# Overlay an active GROW HUD badge so the icon design is also visible in this frame.
world = World()
world.bird = bird
world.grow_timer = 3.1   # mid-buff for the timer bar
world.ready_t   = 0      # suppress the "TAP TO FLY" prompt
world.score     = 7
hud = HUD()
hud.draw_play(scene, world, 12)

pygame.image.save(scene, os.path.join(OUT_DIR, "grow_big_bird.png"))
print("  saved grow_big_bird.png")
