import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

# WHY a cold bone rosary: classic domed skulls threaded on dark-blue beads — every
# seam carries a bead_darkblue so the column reads as a deep-indigo prayer strand of
# bare bone domes, the cool midnight counterpart to a warm multi-colour strand, but
# PLAIN (no skewer underneath). It leads with classic domes (egg-dome, round-cap,
# calvaria) rather than royal crowns so it stays distinct from the garlanded-warlord's
# crown family. Heaviest bead_darkblue use in the pool; an unlit r9 crown caps the far
# end as the one relic terminal. COLLAR is OFF — the blue pips ARE the seam rhythm, and
# a gold collar would fight their cold count.
TITLE = "P15 darkblue-bone-rosary"
RECIPE = [
    "classic:egg-dome",     # focal: smooth domed bone head opens the strand at the gap
    "orn:bead_darkblue",     # cold pip — first bead of the rosary
    "classic:round-cap",     # rounded dome bead-split from the focal
    "orn:bead_darkblue",     # second blue pip keeps the count
    "classic:calvaria",      # high braincase dome continues the bare-bone rhythm
    "orn:bead_darkblue",     # third pip — heaviest dark-blue use anchors the strand
    "r9:0",                  # far terminal: an unlit crown closes the cold rosary
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
