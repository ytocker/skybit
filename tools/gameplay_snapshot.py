"""Simulate a few seconds of gameplay and render the actual screen —
this catches anything the static pipe preview wouldn't."""
import os, sys, pathlib, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import pygame
pygame.init()
pygame.display.set_mode((1, 1))  # so fonts and image.save work

from game.config import W, H
from game.world import World

random.seed(42)
world = World()
# step the world forward so several pipes are in flight
dt = 1 / 60
for _ in range(240):  # 4 seconds
    world.update(dt)

screen = pygame.Surface((W, H))
# quick sky + ground
for y in range(H):
    t = y / (H - 1)
    c = (min(255, int(40 + 130 * t)), min(255, int(110 + 110 * t)), min(255, int(200 + 45 * t)))
    pygame.draw.line(screen, c, (0, y), (W - 1, y))
pygame.draw.rect(screen, (60, 120, 60), (0, 580, W, H - 580))

# draw pipes with the world's biome palette
palette = world.biome_palette
print("pipe count:", len(world.pipes))
print("variants on-screen:", [p.seed % 8 for p in world.pipes])
for p in world.pipes:
    p.draw(screen, palette)

out = "/home/user/Claude_test/docs/gameplay_snapshot.png"
pygame.image.save(screen, out)
print("wrote", out)
