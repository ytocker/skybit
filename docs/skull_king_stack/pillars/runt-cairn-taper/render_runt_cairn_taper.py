import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

# WHY an inverted nursery: a fat broad-cheeked base shrinks course by course up to a
# tiny child-skull crown, so the blackout reads as a bottom-heavy ziggurat that
# pinches to a nub — the deliberate opposite of a gaunt spire's top-heavy taper. The
# child-skull is exiled to the far nub (a vulnerable tip, not a focal subject), and a
# single cold dark-blue pip is the only metal so the masonry stays austere bone.
TITLE = "P11 runt-cairn-taper"
RECIPE = [
    "classic:broad-zygo",   # focal: widest cheek base anchors the bottom-heavy read
    "classic:square-jaw",    # narrows a step — first course of the pinch
    "classic:round-cap",     # narrower still as the taper climbs
    "orn:bead_darkblue",     # lone cold pip — the only ornament, marking the choke
    "classic:child-skull",   # far nub: the tiny crown the ziggurat pinches to
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
