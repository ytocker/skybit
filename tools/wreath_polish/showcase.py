"""Combined showcase — all 5 wreath variations, Fame + Shame heroes in one
labeled grid. Run headless."""
from __future__ import annotations
import os
import pygame
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame.init(); pygame.font.init()

from tools.wreath_polish.concepts import VARIATIONS, compose  # noqa: E402

HERO = 132
ICONS = {"fame": "pillar_100", "shame": "goose_egg"}


def main():
    f = pygame.font.SysFont(None, 24, bold=True)
    fbig = pygame.font.SysFont(None, 30, bold=True)
    pad = 18
    col_w = HERO + 30
    cols = len(VARIATIONS)
    sheet_w = pad * 2 + col_w * cols
    sheet_h = 70 + (HERO + 26) * 2 + 30
    sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    sheet.fill((10, 6, 24))
    sheet.blit(fbig.render("WREATH POLISH — 5 laurel variations (Fame / Shame)",
                           True, (255, 226, 150)), (pad, 14))
    for ci, (name, fn) in enumerate(VARIATIONS):
        ox = pad + ci * col_w
        lab = f.render(name.replace("_", " "), True, (220, 222, 240))
        sheet.blit(lab, (ox, 48))
        for ri, shame in enumerate((False, True)):
            hero = compose(HERO, fn, shame, ICONS["shame" if shame else "fame"])
            oy = 72 + ri * (HERO + 26)
            sheet.blit(hero, (ox, oy))
            tag = f.render("SHAME" if shame else "FAME", True,
                           (228, 182, 130) if shame else (255, 226, 150))
            sheet.blit(tag, (ox, oy + HERO + 2))
    out = "/home/user/skybit/docs/wreath_polish/showcase.png"
    pygame.image.save(sheet, out)
    print(out)


if __name__ == "__main__":
    main()
