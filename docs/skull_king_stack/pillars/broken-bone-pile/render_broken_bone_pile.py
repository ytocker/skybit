import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

# A teetering BROKEN cairn: cracked/asymmetric skulls stacked off-axis with an
# exaggerated alternating lean, garlanded by the ring-eye necklace so the zig-zag
# reads as decorative decay rather than a render fault. The only off-axis pillar
# in the set, so the asymmetric column itself is the identity at 58px.
TITLE = "P5 broken-bone-pile"
RECIPE = [
    "new:cracked-half",        # focal at the gap — the freshest crack, auto-lit
    "new:keyhole-relic",       # hollow eye-socket relic, leans the other way
    "orn:ornament_necklace",   # ring-eye garland: the "decorative decay" tell
    "new:cracked-half",        # second cracked skull keeps the family rhythm
    "new:flat-slab",           # crude flat capstone teetering at the far end
]
WITH_SKEWER = False
SKEWER_STYLE = "plain"
COLLAR = True
# Pushed near the engine's ceiling so the off-axis break is unmistakably INTENT.
LEAN = 0.42


def _render():
    day = PE.render_pair(RECIPE, with_skewer=WITH_SKEWER, skewer_style=SKEWER_STYLE, collar=COLLAR, lean=LEAN, night=False)
    night = PE.render_pair(RECIPE, with_skewer=WITH_SKEWER, skewer_style=SKEWER_STYLE, collar=COLLAR, lean=LEAN, night=True)
    pad = 22
    W = day.get_width() + night.get_width() + pad * 3
    H = day.get_height() + 52
    sheet = pygame.Surface((W, H))
    sheet.fill((26, 24, 30))
    sheet.blit(PE.sk.font(20).render(TITLE, True, PE.sk.LABEL), (pad, 12))
    sheet.blit(day, (pad, 44))
    sheet.blit(night, (pad * 2 + day.get_width(), 44))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("WROTE", out)


if __name__ == "__main__":
    _render()
