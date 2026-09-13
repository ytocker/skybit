"""Render the store lagoon-hub landing screen headlessly to a PNG.

Usage: python _hub_landing_shot.py <out.png>

Uses the REAL game code path (StoreScene view="hub" -> LagoonHub.render) with
no patching, so the shot is exactly what the game draws. Run in a fresh
process per shot — the lagoon base is module-cached.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUT = sys.argv[1]

import pygame
pygame.init()
pygame.display.set_mode((8, 8))

import game.store_data as store_data
store_data.balance = lambda: 1250

from game.store import StoreScene
from game.config import W, H

scene = StoreScene()
scene.view = "hub"
surf = pygame.Surface((W, H))
scene.render(surf)
pygame.image.save(surf, OUT)
print(f"saved {OUT} ({W}x{H})")
