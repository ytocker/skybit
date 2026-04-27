"""Render each HUD screen + entity close-ups to PNG. Run from repo root."""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()

import math, sys
sys.path.insert(0, os.path.dirname(__file__))

from game.config import W, H, GROUND_Y, COIN_R, MUSHROOM_R
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground
from game.world import World
from game.hud import HUD
from game.entities import Coin, PowerUp

OUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

screen = pygame.Surface((W, H))

def draw_bg(surf, scroll=0, phase=0.62):
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
            ((20,90,0.9,0),(180,140,1.1,2),(60,220,0.8,3),(230,60,0.7,1),(320,180,0.9,4))):
        ox = ((bx - scroll * (0.04 + 0.02*i)) % (W+160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2+i)*3, sc, variant=variant)
    pal = pal_a
    draw_mountains(surf, scroll, GROUND_Y, W, pal['mtn_far'], pal['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll, pal['ground_top'], pal['ground_mid'], (60,40,25))

def save(name):
    pygame.image.save(screen, os.path.join(OUT_DIR, name))
    print(f"  saved {name}")

# ── UI screens ───────────────────────────────────────────────────────────────
hud = HUD(); hud.title_t = 1.1
world = World(); world.world_idle_tick(0.016)

draw_bg(screen); world.bird.draw(screen,0,0)
hud.draw_menu(screen, 0, 5);        save("01_menu.png")

hud2 = HUD(); hud2.title_t = 0.8
w2 = World(); w2.score = 12; w2.coin_count = 7
draw_bg(screen)
for p in w2.pipes: p.draw(screen, w2.biome_palette)
w2.bird.draw(screen,0,0); hud2.draw_play(screen, w2, 18)
save("02_play_hud.png")

hud3 = HUD(); hud3.title_t = 0.9
draw_bg(screen); w2.bird.draw(screen,0,0)
hud3.draw_play(screen, w2, 18, paused=True)
hud3.draw_pause_overlay(screen);    save("03_pause.png")

hud4 = HUD(); hud4.title_t = 1.4
w4 = World()
w4.score=23; w4.coin_count=11; w4.max_combo=4
w4.pillars_passed=23; w4.near_misses=3; w4.time_alive=87.0
w4.powerups_picked={"triple":2,"magnet":1}
draw_bg(screen); w4.bird.draw(screen,0,0)
hud4.draw_stats(screen, w4, 0, 1.8);  save("04_stats.png")

hud5 = HUD(); hud5.title_t = 1.2
draw_bg(screen); w4.bird.draw(screen,0,0)
hud5.draw_gameover(screen, 0, 23, new_best=True); save("05_gameover_best.png")

hud6 = HUD(); hud6.title_t = 0.7
draw_bg(screen); w4.bird.draw(screen,0,0)
hud6.draw_gameover(screen, 0, 0, new_best=False); save("06_gameover_tryagain.png")

# ── Entity close-ups (zoomed panel) ─────────────────────────────────────────
def entity_panel(entities_data, filename):
    """Render entities on a dark panel for a clear close-up."""
    panel = pygame.Surface((W, 220))
    panel.fill((12, 8, 38))
    # Subtle grid dots
    for gy in range(20, 220, 30):
        for gx in range(30, W, 30):
            pygame.draw.circle(panel, (25, 18, 55), (gx, gy), 1)

    for obj, cx, cy, pulses in entities_data:
        for p in range(pulses):
            obj.pulse = p * (math.tau / pulses)
            obj.float_t = p * (math.tau / pulses)
            obj.x = cx
            obj.y = cy
            if hasattr(obj, 'spin'):
                obj.spin = p * (math.tau / pulses)
            obj.draw(panel)

    pygame.image.save(panel, os.path.join(OUT_DIR, filename))
    print(f"  saved {filename}")

# Coins at different spin angles
coins = []
for i in range(5):
    c = Coin(60 + i * 58, 110)
    c.spin = i * (math.tau / 5)
    c.float_t = i * 0.8
    coins.append(c)

coin_panel = pygame.Surface((W, 220))
coin_panel.fill((12, 8, 38))
for gy in range(20, 220, 30):
    for gx in range(30, W, 30):
        pygame.draw.circle(coin_panel, (25, 18, 55), (gx, gy), 1)
# Labels
import pygame.font
lf = pygame.font.Font(None, 20)
lbl = lf.render("COINS  —  5 rotation angles", True, (180, 160, 110))
coin_panel.blit(lbl, (W//2 - lbl.get_width()//2, 8))
for c in coins:
    c.draw(coin_panel)
pygame.image.save(coin_panel, os.path.join(OUT_DIR, "07_coins.png"))
print("  saved 07_coins.png")

# Powerups
pu_panel = pygame.Surface((W, 220))
pu_panel.fill((12, 8, 38))
for gy in range(20, 220, 30):
    for gx in range(30, W, 30):
        pygame.draw.circle(pu_panel, (25, 18, 55), (gx, gy), 1)
lbl2 = lf.render("POWERUPS  —  mushroom · magnet · slowmo · kfc", True, (180, 160, 110))
pu_panel.blit(lbl2, (W//2 - lbl2.get_width()//2, 8))

for kind, cx in (("triple", 55), ("magnet", 145), ("slowmo", 235), ("kfc", 325)):
    pu = PowerUp(cx, 120, kind)
    pu.pulse = 1.5  # mid-animation
    pu.draw(pu_panel)
    kf = pygame.font.Font(None, 18)
    kl = kf.render(kind.upper(), True, (200, 180, 120))
    pu_panel.blit(kl, (cx - kl.get_width()//2, 170))

pygame.image.save(pu_panel, os.path.join(OUT_DIR, "08_powerups.png"))
print("  saved 08_powerups.png")

# ── KFC fried-chicken parrot in flight ───────────────────────────────────────
from game import parrot as _parrot
from game.entities import Bird

kfc_panel = pygame.Surface((W, H))
draw_bg(kfc_panel, phase=0.72)

bird = Bird()
bird.x, bird.y = W * 0.38, H * 0.44
bird.kfc_active = True
bird.frame_t = 0.0

lf3 = pygame.font.Font(None, 22)
kfc_lbl = lf3.render("KFC MODE — fried chicken parrot", True, (200, 180, 120))
kfc_panel.blit(kfc_lbl, (W//2 - kfc_lbl.get_width()//2, 12))

# Draw all 4 wing frames across the screen
for fi in range(4):
    bx = int(W * 0.15 + fi * W * 0.22)
    by = int(H * 0.48)
    frame = _parrot.KFC_FRAMES[fi]
    kfc_panel.blit(frame, (bx - frame.get_width()//2, by - frame.get_height()//2))

pygame.image.save(kfc_panel, os.path.join(OUT_DIR, "09_kfc_chicken.png"))
print("  saved 09_kfc_chicken.png")

pygame.quit()
print("Done —", OUT_DIR)
