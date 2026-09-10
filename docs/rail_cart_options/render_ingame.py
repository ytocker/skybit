import os, math, sys
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
sys.path.insert(0, "/home/user/skybit")

from game.config import W, H, GROUND_Y, PIPE_W
from game import biome as _biome, audio, scenes
from game.draw import get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground
from game.world import World

audio.play_rail = lambda *a, **k: None  # avoid mixer on the headless native path

screen = pygame.Surface((W, H))


def draw_bg(surf, scroll=0, phase=0.30):
    buckets = _biome.PHASE_BUCKETS
    bf = (phase % 1.0) * buckets
    a = int(bf) % buckets
    pal = _biome.palette_for_phase(a / buckets)
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal, a)
    sky.set_alpha(None); surf.blit(sky, (0, 0))
    for i, (bx, by, sc, variant) in enumerate(
            ((20, 90, 0.9, 0), (180, 140, 1.1, 2), (60, 220, 0.8, 3),
             (230, 60, 0.7, 1), (320, 180, 0.9, 4))):
        ox = ((bx - scroll) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2 + i) * 3, sc, variant=variant)
    draw_mountains(surf, scroll, GROUND_Y, W, pal['mtn_far'], pal['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll, pal['ground_top'],
                pal['ground_mid'], (60, 40, 25))
    return pal


world = World()
world.world_idle_tick(0.016)

# Activate the rail buff, then lock Pip onto the cart pillar mid-ride.
class _M:  # minimal pickup stand-in
    pass
m = _M(); m.x = world.bird.x + 100; m.y = world.bird.y
world._activate_rail(m)
world.float_texts.clear()           # drop the "RAILS UP!" label for a clean shot
world.particles.clear()
cart_pipe = world.rail_cart_pipe
# Slide the tagged pillars so the cart pillar sits under Pip's fixed x.
shift = (world.bird.x) - (cart_pipe.x + PIPE_W // 2)
for p in world.pipes:
    p.x += shift
world.rail_pipes = [p for p in world.pipes if getattr(p, "rail_active", False)]
world.rail_cart_pipe = sorted(world.rail_pipes, key=lambda p: p.x)[0]
world.bird.cart_locked = True
world._snap_cart_to_rail(world.bird.x)

pal = draw_bg(screen)
for p in world.pipes:
    p.draw(screen, world.biome_palette)

# Mimic App._render's rail block: rails -> wheels -> Pip -> bucket body.
scenes._draw_rails(screen, world.rail_pipes)
scenes._draw_cart_on_bird(screen, world, 0, 0, layer="wheels")
world.bird.draw(screen, 0, 0)
scenes._draw_cart_on_bird(screen, world, 0, 0, layer="body")

big = pygame.transform.scale(screen, (W * 2, H * 2))
pygame.image.save(big, "/tmp/rail_ingame.png")
print("saved /tmp/rail_ingame.png", big.get_size())
