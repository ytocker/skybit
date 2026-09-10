import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

# WHY a garlanded war-totem: bare royal crowns swagged by TWO necklace-ring garlands
# draped between courses, crowned at the far end by a single antler-stag head — so the
# column reads as relic domes hung with looped chains under one wild beast trophy. It
# mixes a single appendage (the antlers) into an otherwise royal body and carries the
# heaviest ornament_necklace use in the pool. COLLAR is OFF — the two big ring-garlands
# ARE the ornament, and bead seams would clutter the drape. A slight positive lean lets
# the hung loops sway off-axis like real swag.
TITLE = "P19 necklace-draped-warlord"
RECIPE = [
    "crown:0",              # focal: a bare royal crown relic opens the war-totem
    "orn:ornament_necklace", # first draped ring-garland swagged above the crown
    "crown:3",               # second royal dome continues the relic body
    "orn:ornament_necklace", # second garland — the defining double drape
    "new:antler-stag",       # far cap: a wild beast head crowns the trophy
]
WITH_SKEWER = False
SKEWER_STYLE = "plain"
COLLAR = False
LEAN = 0.12


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
