import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

# WHY an all-seeing watchtower: three faceted third-eye gems are seated as their own
# keystone tiers between single-socket cyclops skulls, so the silhouette becomes a
# vertical ladder of glinting lenses — skull-eye, gem, skull-eye, gem — that reads as
# a row of lit eyes rather than a row of skulls. COLLAR stays OFF so nothing competes
# with the gems for the glint; the gems alone carry the metal.
TITLE = "P12 thirdeye-watchtower"
RECIPE = [
    "new:cyclops-brow",     # focal: single deep socket sets the one-eye motif at the gap
    "orn:gem_thirdeye",      # keystone gem — the first lens in the ladder
    "classic:calvaria",      # smooth domed course between the eyes
    "orn:gem_thirdeye",      # second lens, mid-stack
    "new:cyclops-brow",      # the rhyming eye-socket recurs
    "orn:gem_thirdeye",      # third lens caps the tower — heaviest gem use in the pool
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
