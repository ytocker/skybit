import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

TITLE = "P10 bead-threaded-strand-spindle"
# The rosary/spindle: the rod is buried under one continuous chunky bead cord that
# runs the whole column (the "strand" skewer), so the relic skulls read as the big
# centerpiece BEADS threaded on a string rather than masonry stacked on a spit.
# COLLAR is off on purpose — the strand IS the connective tissue; a seam-collar
# would compete with it. Identity must survive at 58px on SEAM-THICKNESS RHYTHM,
# not bead colour, so the recipe swings the skull cranium WIDTH wide->pinch->wide
# down the cord: the strand visibly bulges at a broad relic and necks down at a
# narrow one, giving the knobbly threaded-seam beat. Three relic families are
# mixed for the sacred-rosary read (crown + palm + r9), not for hue.
#   crown:2 -> focal centerpiece at the gap (cw 1.10 broad heart-dome, auto-lit)
#   palm:0  -> narrow cradled-core node; the cord necks down here
#   r9:1    -> dim cool round-9 dome; a darker bead between two pale ones (VALUE beat)
#   crown:5 -> cw 1.08 broad zig crown; the cord swells wide again
#   palm:2  -> palm node closing the strand before the bead-nub tip in the gap
RECIPE = ["crown:2", "palm:0", "r9:1", "crown:5", "palm:2"]
WITH_SKEWER = True
SKEWER_STYLE = "strand"
COLLAR = False
LEAN = 0.0

def _render():
    day = PE.render_pair(RECIPE, with_skewer=WITH_SKEWER, skewer_style=SKEWER_STYLE, collar=COLLAR, lean=LEAN, night=False)
    night = PE.render_pair(RECIPE, with_skewer=WITH_SKEWER, skewer_style=SKEWER_STYLE, collar=COLLAR, lean=LEAN, night=True)
    pad = 22
    W = day.get_width() + night.get_width() + pad*3
    H = day.get_height() + 52
    sheet = pygame.Surface((W, H)); sheet.fill((26,24,30))
    sheet.blit(PE.sk.font(20).render(TITLE, True, PE.sk.LABEL), (pad, 12))
    sheet.blit(day, (pad, 44)); sheet.blit(night, (pad*2+day.get_width(), 44))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out); print("WROTE", out)

if __name__ == "__main__":
    _render()
