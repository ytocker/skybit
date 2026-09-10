import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

# WHY a snarling jaw-stack tilted hard left: sabertooth maws and longjaw relics whose
# fangs all hang the same way down a strong NEGATIVE lean, so the column looks like
# it's lunging and sliding off its own base. This is the set's only negative-lean
# column and the only fang-heavy PLAIN totem (the harpoon column's fangs were
# skewered). COLLAR is ON so warm gold seam beads cinch the off-axis tiers together
# like a strap holding a slumping load — the only thing keeping the snarl from
# tipping over. The tail gaunt-hollow drains to a hollow socket, deflating the lunge.
TITLE = "P13 lopsided-fang-lean"
RECIPE = [
    "new:sabertooth-maw",   # focal: sabre fangs plunge into the gap, set the snarl
    "new:longjaw-relic",     # long muzzle wedge rhymes the downward thrust
    "new:sabertooth-maw",    # the plunging maw recurs — the fang motif repeats
    "new:longjaw-relic",     # second muzzle wedge keeps the cascade pointing one way
    "classic:gaunt-hollow",  # far tail: a hollow socket deflates the lunge to bone
]
WITH_SKEWER = False
SKEWER_STYLE = "plain"
COLLAR = True
LEAN = -0.34
# the focal sabertooth-maw drops long fangs toward the gap, so seat the stack
# further off the edge — clears clean room so the fangs don't tangle with the gap rim.
MARGIN_R = 2.4


def _render():
    day = PE.render_pair(RECIPE, with_skewer=WITH_SKEWER, skewer_style=SKEWER_STYLE, collar=COLLAR, lean=LEAN, margin_r=MARGIN_R, night=False)
    night = PE.render_pair(RECIPE, with_skewer=WITH_SKEWER, skewer_style=SKEWER_STYLE, collar=COLLAR, lean=LEAN, margin_r=MARGIN_R, night=True)
    pad = 22
    W = day.get_width() + night.get_width() + pad*3; H = day.get_height() + 52
    sheet = pygame.Surface((W, H)); sheet.fill((26,24,30))
    sheet.blit(PE.sk.font(20).render(TITLE, True, PE.sk.LABEL), (pad, 12))
    sheet.blit(day, (pad, 44)); sheet.blit(night, (pad*2+day.get_width(), 44))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out); print("WROTE", out)


if __name__ == "__main__":
    _render()
