"""Render what the actual game shows: random-seeded Pipes side by side."""
import os, sys, pathlib, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import pygame

from game.config import W, H, GROUND_Y, PIPE_W
from game.entities import Pipe, _DEFAULT_PILLAR


def main():
    pygame.init()
    random.seed(1234)  # deterministic for review
    n = 10
    cell_w = 130
    canvas_w = cell_w * n
    canvas_h = GROUND_Y + 10
    surf = pygame.Surface((canvas_w, canvas_h))
    for y in range(canvas_h):
        t = y / (canvas_h - 1)
        c = (min(255, int(40 + 130 * t)), min(255, int(110 + 110 * t)), min(255, int(200 + 45 * t)))
        pygame.draw.line(surf, c, (0, y), (canvas_w - 1, y))
    pygame.draw.rect(surf, (60, 120, 60), (0, GROUND_Y, canvas_w, canvas_h - GROUND_Y))

    variants_seen = []
    for i in range(n):
        x = i * cell_w + (cell_w - PIPE_W) // 2
        p = Pipe(x=x, gap_y=H / 2, gap_h=170)
        variants_seen.append(p.seed % 8)
        p.draw(surf, palette=_DEFAULT_PILLAR)

    font = pygame.font.SysFont("arial", 13, bold=True)
    for i, v in enumerate(variants_seen):
        t = font.render(f"v{v}", True, (18, 18, 26))
        bg = pygame.Surface((t.get_width() + 6, t.get_height() + 2), pygame.SRCALPHA)
        bg.fill((255, 255, 255, 220))
        x = i * cell_w + (cell_w - t.get_width() - 6) // 2
        surf.blit(bg, (x, 4))
        surf.blit(t, (x + 3, 5))

    print("variants seen:", variants_seen)
    out = "/home/user/Claude_test/docs/pillar_variants_random.png"
    pygame.image.save(surf, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
