import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

TITLE = "P1 relic-reliquary-totem"
# The dignified baseline: pure crown+palm royal reliquary, focal crown at the gap.
# Tier silhouettes alternate crown<->palm and step wide->narrow->wide so the column
# breathes evenly; a single gold bead seated once mid-stack is the only added
# ornament, so the skulls stay calm and regular rather than busy.
RECIPE = ["crown:2", "palm:1", "crown:0", "orn:bead_gold", "palm:4", "crown:5"]
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
