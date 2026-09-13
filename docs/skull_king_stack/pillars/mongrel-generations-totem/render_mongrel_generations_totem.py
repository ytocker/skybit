import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

# WHY a museum of skull lineages: one skull from every FAMILY in a single column
# (new / r9 / palm / classic), so the blackout is a deliberately mismatched mongrel
# stack — each tier a different shape-language, no two seams alike. It leads with the
# long longjaw-relic muzzle as the lit focal and climbs a loose size-ladder spine, with
# the unlit r9 crown demoted to a mid-body course (its profile pressed into the lineup,
# not a focal). The terminal swaps to a cracked-half so that broken-half motif recurs
# across two columns. Mixed beads + a third-eye gem give each seam its own ornament, so
# COLLAR stays OFF — a uniform collar would erase the point. A slight negative lean lets
# the heterogeneous stack slouch casually left.
TITLE = "P20 mongrel-generations-totem"
RECIPE = [
    "new:longjaw-relic",    # focal: the long muzzle wedge anchors the lineup at the gap
    "orn:bead_darkblue",     # cold pip — one distinct seam ornament
    "palm:3",                # ornamented cradled palm — the palm family's entry
    "orn:gem_thirdeye",      # a faceted gem seam, different from the bead below
    "r9:0",                  # unlit crown demoted to a mid-body course (the r9 family)
    "new:cracked-half",      # far terminal: a broken half caps the mongrel stack
]
WITH_SKEWER = False
SKEWER_STYLE = "plain"
COLLAR = False
LEAN = -0.16


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
