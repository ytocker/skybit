import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

# WHY this pillar still reads as a WARBAND TOTEM: the antler-stag racks throw bone
# OUTWARD and UP off the column, so the silhouette stays ragged and irregular. The
# plain simple-skulls between the racks are calm breaks that let each antler spread
# read on its own (tall spurs, then a clean skull, repeat) instead of a solid horn
# mass. The gold bead sits as a single HORIZONTAL SPACER TIER (one bead element
# between two skulls), a clean breath in the rack — never a vertical centre line.
TITLE = "P2 horned-warband"
RECIPE = [
    "new:antler-stag",   # focal at the gap — tall branched rack announces the warband
    "new:simple-skull",  # a calm plain skull between the racks
    "orn:bead_gold",     # lone horizontal spacer pip — a breath between the racks
    "new:antler-stag",   # rack again, far tine spread re-broadens the top
    "new:simple-skull",  # plain skull caps the totem under the top rack
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
