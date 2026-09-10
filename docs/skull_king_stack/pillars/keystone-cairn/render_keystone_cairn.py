import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

# WHY masonry: square/flat-topped skulls butted with COLLAR=False read as stone
# courses; the faceted third-eye gem is seated mid-stack as the structural
# keystone (the jewel set into the wall), an ornament role rather than decoration.
TITLE = "P3 keystone-cairn"
RECIPE = [
    "classic:square-jaw",       # focal: hard square skull at the gap
    "new:flat-slab",            # flat course above
    "orn:gem_thirdeye",         # keystone tier — jewel set in the wall
    "classic:flat-brow-robust", # robust flat-browed course
    "classic:square-jaw",       # squared cap closes the column
]
WITH_SKEWER = False
SKEWER_STYLE = "plain"
COLLAR = False
LEAN = 0.0


def _render():
    day = PE.render_pair(RECIPE, with_skewer=WITH_SKEWER, skewer_style=SKEWER_STYLE, collar=COLLAR, lean=LEAN, night=False)
    night = PE.render_pair(RECIPE, with_skewer=WITH_SKEWER, skewer_style=SKEWER_STYLE, collar=COLLAR, lean=LEAN, night=True)
    pad = 22
    W = day.get_width() + night.get_width() + pad*3; H = day.get_height() + 52
    sheet = pygame.Surface((W, H)); sheet.fill((26,24,30))
    sheet.blit(PE.sk.font(20).render(TITLE, True, PE.sk.LABEL), (pad, 12))
    sheet.blit(day, (pad, 44)); sheet.blit(night, (pad*2+day.get_width(), 44))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out); print("WROTE", out)


if __name__ == "__main__":
    _render()
