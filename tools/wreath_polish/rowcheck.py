"""Zoomed clip-check: tile all 5 variations' Fame+Shame 44px row badges at 6x
on a single sheet, each in its red 44px square, so any leaf clipping the badge
edge is obvious. Run headless."""
from __future__ import annotations
import os
import pygame
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame.init(); pygame.font.init()

from tools.wreath_polish.concepts import VARIATIONS, compose  # noqa: E402

_BADGE = 44
Z = 6
ICONS = {"fame": "pillar_100", "shame": "goose_egg"}


def main():
    cell = _BADGE * Z + 40
    cols = 2
    rows = len(VARIATIONS)
    sheet = pygame.Surface((cell * cols + 120, cell * rows + 60), pygame.SRCALPHA)
    sheet.fill((10, 6, 24))
    f = pygame.font.SysFont(None, 22, bold=True)
    for ri, (name, fn) in enumerate(VARIATIONS):
        lab = f.render(name, True, (255, 226, 150))
        sheet.blit(lab, (10, 30 + ri * cell + cell // 2))
        for ci, shame in enumerate((False, True)):
            badge = compose(_BADGE, fn, shame, ICONS["shame" if shame else "fame"])
            big = pygame.transform.scale(badge, (_BADGE * Z, _BADGE * Z))
            ox = 120 + ci * cell + 20
            oy = 30 + ri * cell + 20
            sheet.blit(big, (ox, oy))
            pygame.draw.rect(sheet, (255, 60, 60), (ox, oy, _BADGE * Z, _BADGE * Z), 2)
    for ci, t in enumerate(("FAME 44px", "SHAME 44px")):
        sheet.blit(f.render(t, True, (200, 200, 220)), (120 + ci * cell + 20, 4))
    out = "/home/user/skybit/docs/wreath_polish/rowcheck_44px.png"
    pygame.image.save(sheet, out)
    print(out)


if __name__ == "__main__":
    main()
