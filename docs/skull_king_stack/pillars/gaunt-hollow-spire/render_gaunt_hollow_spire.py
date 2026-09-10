import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

TITLE = "P4 gaunt-hollow-spire"
# The ascetic: the thinnest column in the set. Only the narrowest-silhouette skulls
# (egg-dome / gaunt-hollow / calvaria) so the stack tapers tall and slender rather
# than bulking out. A single cyan bead tier sits mid-stack as ONE cold joint between
# two gaunt skulls — a discontinuous accent, never a continuous centre rod/spine.
# Identity is carried by the narrow skull family + the lone cyan seam, not by colour.
RECIPE = ["classic:egg-dome", "classic:gaunt-hollow", "orn:bead_cyan",
          "classic:calvaria", "classic:gaunt-hollow"]
WITH_SKEWER = False
SKEWER_STYLE = "plain"
COLLAR = True
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
