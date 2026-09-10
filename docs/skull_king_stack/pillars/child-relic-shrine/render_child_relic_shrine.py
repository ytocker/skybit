import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

# WHY a small reliquary shrine: a child-skull is cradled and venerated at the gap as
# the FOCAL subject (distinct from the runt-cairn, where the child-skull is an exiled
# far nub), with larger guardians standing above it — a forehead-gem palm relic and an
# unlit r9 crown keeping vigil. A single dark-blue votive bead marks the shrine subject
# (the draped halo garland is left to the warlord, which owns that ornament) and COLLAR
# is ON so warm gold seam beads frame the devotional read: tiny focal, larger
# protectors. The unlit crown reads as a relic in repose, not a reigning king.
TITLE = "P14 child-relic-shrine"
RECIPE = [
    "classic:child-skull",   # focal: the small venerated subject cradled at the gap
    "orn:bead_darkblue",     # a dark-blue votive bead set just above the shrine subject
    "palm:4",                # forehead-gem palm relic — the first guardian
    "r9:0",                  # unlit crown standing in vigil (no lit reign)
    "palm:3",                # far guardian closes the shrine
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
