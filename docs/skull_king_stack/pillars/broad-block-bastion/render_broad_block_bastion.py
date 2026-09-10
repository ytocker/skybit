import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

# WHY a bulging fortress wall: broad-zygo wide-cheek skulls stacked nearly edge-to-edge
# so the blackout is the WIDEST, most barrel-sided column of the pool — a solid bastion
# that bows outward at the cheeks, the girth answer to the slim tapers elsewhere in the
# set. All-classic bone, COLLAR off so the wall stays unbroken, with a lone third-eye
# gem as the single keystone glint set into the masonry.
TITLE = "P16 broad-block-bastion"
RECIPE = [
    "classic:broad-zygo",       # focal: widest cheek block anchors the barrel base
    "classic:flat-brow-robust",  # heavy flat course keeps the wall solid
    "orn:gem_thirdeye",          # lone keystone gem set into the bastion
    "classic:broad-zygo",        # the wide cheek block recurs — defines the girth
    "classic:square-jaw",        # squared cap closes the fortress wall
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
