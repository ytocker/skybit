"""One-off sanity render of the integrated B · CHARTREUSE KO dead-Pip
sprite (post-integration into game/dollar_parrot_dead.py). 4 wing-angle
frames at 4x scale on a charcoal card, no panel chrome — just confirms
the production builder produces the B-OFF look from round 10."""
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.dollar_parrot_dead import build_dead_variant_frames

OUT = pathlib.Path(__file__).parent.parent / "docs" / "dead_pip_v3" / "integrated_b_preview.png"

SCALE = 4
frames = build_dead_variant_frames("B", aura_scale=1.0)
fw, fh = frames[0].get_size()
gap = 16
pad = 20
W = pad * 2 + len(frames) * fw * SCALE + (len(frames) - 1) * gap
H = pad * 2 + fh * SCALE + 32

surf = pygame.Surface((W, H), pygame.SRCALPHA)
surf.fill((26, 30, 38))

font = pygame.font.SysFont("DejaVu Sans", 14, bold=True)
label = font.render("Integrated B · CHARTREUSE KO — 4 frames @ 4x", True, (220, 230, 200))
surf.blit(label, (pad, 6))

x = pad
y = pad + 20
for f in frames:
    scaled = pygame.transform.scale(f, (fw * SCALE, fh * SCALE))
    surf.blit(scaled, (x, y))
    x += fw * SCALE + gap

OUT.parent.mkdir(parents=True, exist_ok=True)
pygame.image.save(surf, str(OUT))
print(f"wrote {OUT}  {surf.get_size()}")
