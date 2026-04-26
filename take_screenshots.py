"""
Render each HUD screen to a PNG file using an offscreen pygame display.
Run from the repo root: python3 take_screenshots.py
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()

import math, sys
sys.path.insert(0, os.path.dirname(__file__))

from game.config import W, H, GROUND_Y
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.world import World
from game.hud import HUD

OUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

screen = pygame.Surface((W, H))

def draw_bg(surf, scroll=0, phase=0.62):
    """Render the night-sky biome background (phase 0.62 ≈ deep-night palette)."""
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
    for i, (bx, by, sc, variant) in enumerate(
            ((20,90,0.9,0),(180,140,1.1,2),(60,220,0.8,3),(230,60,0.7,1),(320,180,0.9,4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2 + i) * 3, sc, variant=variant)
    palette = pal_a
    draw_mountains(surf, scroll, GROUND_Y, W, palette['mtn_far'], palette['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))

def save(name):
    pygame.image.save(screen, os.path.join(OUT_DIR, name))
    print(f"  saved {name}")

hud = HUD()
# Advance title_t so animations are mid-cycle (looks better in a still)
hud.title_t = 1.1

world = World()
world.world_idle_tick(0.016)

# ── 1. Menu ──────────────────────────────────────────────────────────────────
draw_bg(screen)
for p in world.pipes: p.draw(screen, world.biome_palette)
world.weather.draw(screen)
world.bird.draw(screen, 0, 0)
hud.title_t = 1.1
hud.draw_menu(screen, 0, 5)
save("01_menu.png")

# ── 2. Play HUD ───────────────────────────────────────────────────────────────
hud2 = HUD(); hud2.title_t = 0.8
draw_bg(screen)
w2 = World(); w2.world_idle_tick(0.016)
# Give it a plausible in-play state
w2.score = 12
w2.coin_count = 7
for p in w2.pipes: p.draw(screen, w2.biome_palette)
w2.weather.draw(screen)
w2.bird.draw(screen, 0, 0)
hud2.draw_play(screen, w2, 18)
save("02_play_hud.png")

# ── 3. Pause ─────────────────────────────────────────────────────────────────
hud3 = HUD(); hud3.title_t = 0.9
draw_bg(screen)
w3 = World(); w3.score = 12
for p in w3.pipes: p.draw(screen, w3.biome_palette)
w3.bird.draw(screen, 0, 0)
hud3.draw_play(screen, w3, 18, paused=True)
hud3.draw_pause_overlay(screen)
save("03_pause.png")

# ── 4. Stats / Run Summary ────────────────────────────────────────────────────
hud4 = HUD(); hud4.title_t = 1.4
draw_bg(screen)
w4 = World()
w4.score = 23; w4.coin_count = 11; w4.max_combo = 4
w4.pillars_passed = 23; w4.near_misses = 3
w4.time_alive = 87.0
w4.powerups_picked = {"triple": 2, "magnet": 1}
w4.bird.draw(screen, 0, 0)
hud4.draw_stats(screen, w4, 0, 1.8)
save("04_stats.png")

# ── 5. Game Over (with score) ─────────────────────────────────────────────────
hud5 = HUD(); hud5.title_t = 1.2
draw_bg(screen)
w5 = World(); w5.score = 23
w5.bird.draw(screen, 0, 0)
hud5.draw_gameover(screen, 0, 23, new_best=True)
save("05_gameover_best.png")

# ── 6. Game Over (zero score / try again) ────────────────────────────────────
hud6 = HUD(); hud6.title_t = 0.7
draw_bg(screen)
w6 = World(); w6.score = 0
w6.bird.draw(screen, 0, 0)
hud6.draw_gameover(screen, 0, 0, new_best=False)
save("06_gameover_tryagain.png")

pygame.quit()
print("Done — screenshots in", OUT_DIR)
