"""Render a smoke-test grid of 8 Pipe variants using the actual in-game code."""
import os, sys, pathlib
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import pygame

from game.config import W, H, GROUND_Y, PIPE_W
from game.entities import Pipe, _DEFAULT_PILLAR
from game import pillar_variants as pv


def main():
    pygame.init()
    # one canvas wide enough to show 8 pipe pairs side-by-side
    cell_w = 140
    cell_h = GROUND_Y + 10
    canvas_w = cell_w * pv.VARIANT_COUNT
    canvas_h = cell_h
    surf = pygame.Surface((canvas_w, canvas_h))
    # Simple gradient sky + green ground
    for y in range(canvas_h):
        t = y / (canvas_h - 1)
        c = (min(255, int(40 + 130 * t)), min(255, int(110 + 110 * t)), min(255, int(200 + 45 * t)))
        pygame.draw.line(surf, c, (0, y), (canvas_w - 1, y))
    pygame.draw.rect(surf, (60, 120, 60), (0, GROUND_Y, canvas_w, canvas_h - GROUND_Y))

    # Make one Pipe per variant by using seed = variant_id (since draw_pillar_pair
    # picks variant_id = seed % VARIANT_COUNT)
    for i in range(pv.VARIANT_COUNT):
        p = Pipe(x=i * cell_w + (cell_w - PIPE_W) // 2, gap_y=H / 2, gap_h=170)
        p.seed = i
        p.draw(surf, palette=_DEFAULT_PILLAR)

    font = pygame.font.SysFont("arial", 14, bold=True)
    names = ["0 original", "1 Lung-ta", "2 Darchog", "3 Babylon",
             "4 Monastery", "5 Lantern", "6 Overgrown", "7 Menhir"]
    for i, name in enumerate(names):
        t = font.render(name, True, (18, 18, 26))
        bg = pygame.Surface((t.get_width() + 8, t.get_height() + 4), pygame.SRCALPHA)
        bg.fill((255, 255, 255, 220))
        x = i * cell_w + (cell_w - t.get_width() - 8) // 2
        surf.blit(bg, (x, 4))
        surf.blit(t, (x + 4, 6))

    out = "/home/user/Claude_test/docs/pillar_variants_ingame.png"
    pygame.image.save(surf, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
