"""Render 8 consecutive pipes as they'd scroll across a real gameplay session."""
import os, sys, pathlib, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y, PIPE_W, PIPE_SPACING
from game.entities import Pipe, _DEFAULT_PILLAR

random.seed(7)
pipes = []
x = 60
for _ in range(8):
    gap_h = random.randint(140, 200)
    margin = 70
    gy = random.randint(margin + gap_h // 2, GROUND_Y - margin - gap_h // 2)
    p = Pipe(x=x, gap_y=gy, gap_h=gap_h)
    pipes.append(p)
    x += PIPE_SPACING

canvas_w = x
surf = pygame.Surface((canvas_w, H))
for y in range(H):
    t = y / (H - 1)
    c = (min(255, int(40 + 130 * t)), min(255, int(110 + 110 * t)), min(255, int(200 + 45 * t)))
    pygame.draw.line(surf, c, (0, y), (canvas_w - 1, y))
pygame.draw.rect(surf, (60, 120, 60), (0, GROUND_Y, canvas_w, H - GROUND_Y))

for p in pipes:
    p.draw(surf, palette=_DEFAULT_PILLAR)

font = pygame.font.SysFont("arial", 14, bold=True)
for p in pipes:
    v = p.seed % 8
    t = font.render(f"v{v}", True, (18, 18, 26))
    bg = pygame.Surface((t.get_width() + 6, t.get_height() + 2), pygame.SRCALPHA)
    bg.fill((255, 255, 255, 220))
    surf.blit(bg, (p.x + PIPE_W // 2 - t.get_width() // 2 - 3, 4))
    surf.blit(t, (p.x + PIPE_W // 2 - t.get_width() // 2, 5))

print("variants:", [p.seed % 8 for p in pipes])
out = "/home/user/Claude_test/docs/gameplay_panorama.png"
pygame.image.save(surf, out)
print("wrote", out)
