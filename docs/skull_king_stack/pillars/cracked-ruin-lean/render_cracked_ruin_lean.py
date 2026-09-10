import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

# WHY a collapsing ruin pile leaning the OTHER way: cracked-half and keyhole voids
# stacked at a gentle POSITIVE lean so the broken faces all slump toward the gap, like
# a wall mid-collapse. It stays distinct from the harder-leaning broken-bone pile by a
# different break-family mix (keyhole voids, not antler debris), a gentler lean, and a
# cold dark-blue bead marking the fracture line instead of a warm necklace. COLLAR is
# OFF — a ruin shouldn't look tidily strapped.
TITLE = "P17 cracked-ruin-lean"
RECIPE = [
    "new:cracked-half",     # focal: a split, broken face slumps at the gap
    "new:keyhole-relic",     # hollow keyhole void — the ruin's pierced course
    "orn:bead_darkblue",     # cold pip marks the fracture line
    "new:cracked-half",      # the broken half recurs — the collapse repeats
    "classic:gaunt-hollow",  # far tail: a gaunt hollow tops the slumping pile
]
WITH_SKEWER = False
SKEWER_STYLE = "plain"
COLLAR = False
LEAN = 0.22


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
