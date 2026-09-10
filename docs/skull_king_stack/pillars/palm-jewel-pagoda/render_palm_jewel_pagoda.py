import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

# WHY a jewel-box pagoda: the ornamented cradled palm skulls ONLY, with COLLAR on for a
# warm gold-pip metronome at every seam — the richest PLAIN (un-skewered) reliquary in
# the pool. Where the scepter column put its gold into a central rod, here the gold
# lives entirely in the collar beads and the palm gems, so the whole tower glows warm
# without a shaft. It leads with the forehead-gem palm as the lit focal so the jewel
# read starts at the gap.
TITLE = "P18 palm-jewel-pagoda"
RECIPE = [
    "palm:4",   # focal: forehead-gem palm relic opens the jewel-box at the gap
    "palm:3",    # mid-stack cradled palm continues the all-palm family
    "palm:5",    # another ornamented palm — the pagoda's even tiers
    "palm:0",    # plainer palm varies the gem placement without breaking family
    "palm:2",    # far cap palm closes the pagoda
]
WITH_SKEWER = False
SKEWER_STYLE = "plain"
COLLAR = True
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
