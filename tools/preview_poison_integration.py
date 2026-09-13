"""Sanity render of the integrated poison vial sprite + Pip mid-poison
cross-fade frames. Committed as a verification artifact so the
integration can be eyeballed without spinning the game."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.entities import PowerUp, Bird
from game import poison_vial, parrot

OUT_VIAL = pathlib.Path(__file__).parent.parent / "docs" / "poison_pickup" / "integrated_vial_preview.png"
OUT_BIRD = pathlib.Path(__file__).parent.parent / "docs" / "poison_pickup" / "integrated_pip_crossfade.png"

OUT_VIAL.parent.mkdir(parents=True, exist_ok=True)

# Vial sprite at 1x, 2x, 4x on a charcoal card
vial = poison_vial.get_vial_sprite()
W = 60 + 96 + 200 + 60 + 40 + 40
H = 240
surf = pygame.Surface((W, H), pygame.SRCALPHA)
surf.fill((26, 30, 38))
font = pygame.font.SysFont("DejaVu Sans", 13, bold=True)
surf.blit(font.render("Poison vial — 1x  /  2x  /  4x  (with breathing halo)", True, (220, 230, 200)), (20, 8))
import math
pulse = math.pi / 2
x = 20
for scale in (1, 2, 4):
    sz = 48 * scale
    sub = pygame.Surface((sz + 40, sz + 40), pygame.SRCALPHA)
    poison_vial.draw(sub, sub.get_width() // 2, sub.get_height() // 2, pulse)
    if scale != 1:
        sub = pygame.transform.scale(sub, (sub.get_width() * scale, sub.get_height() * scale))
    surf.blit(sub, (x, 32))
    x += sub.get_width() + 16
pygame.image.save(surf, str(OUT_VIAL))
print(f"wrote {OUT_VIAL}  {surf.get_size()}")

# Pip cross-fade strip: poison_t = 0.0, 0.25, 0.5, 0.75, 1.0
bird = Bird()
SCALE = 4
labels = ["t=0.0 (healthy)", "t=0.25", "t=0.5", "t=0.75", "t=1.0 (dead)"]
ts = [0.0, 0.25, 0.5, 0.75, 1.0]
frame_size = 68 * SCALE
W2 = 20 + (frame_size + 20) * len(ts)
H2 = 40 + frame_size + 30
surf2 = pygame.Surface((W2, H2), pygame.SRCALPHA)
surf2.fill((26, 30, 38))
surf2.blit(font.render("Integrated Pip — poison cross-fade at 4x", True, (220, 230, 200)), (20, 8))
small = pygame.font.SysFont("DejaVu Sans", 12)
for i, t in enumerate(ts):
    sub = pygame.Surface((68, 64), pygame.SRCALPHA)
    bird.poison_active = True
    bird.poison_t = t
    bird.y = 32
    bird.x = 34
    bird.draw(sub)
    scaled = pygame.transform.scale(sub, (frame_size, frame_size * 64 // 68))
    x = 20 + i * (frame_size + 20)
    surf2.blit(scaled, (x, 32))
    label = small.render(labels[i], True, (200, 210, 180))
    surf2.blit(label, (x + (frame_size - label.get_width()) // 2, 32 + scaled.get_height() + 6))
pygame.image.save(surf2, str(OUT_BIRD))
print(f"wrote {OUT_BIRD}  {surf2.get_size()}")
