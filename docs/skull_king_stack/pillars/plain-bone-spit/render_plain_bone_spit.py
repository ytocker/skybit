import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

TITLE = "P6 plain-bone-spit"

# The crude anchor of the skewered family: simple CLASSIC skulls run through on a
# plain dark bone spit (white beads at seams, blunt knob tip, NO gold core, NO barb).
# Rhythm is an A-B-A-C-A butcher's cadence — round-cap (A) recurs as the dumb
# repeating motif so the column reads as a primitive spit rather than a curated
# ornate stack; square-jaw (B) and broad-zygo (C) vary the silhouette without adding
# decoration. Focal = a round classic skull at the gap, auto-lit. COLLAR=False so the
# rod + its white beads are the only joinery, keeping the pillar deliberately bare.
RECIPE = [
    "classic:round-cap",
    "classic:square-jaw",
    "classic:round-cap",
    "classic:broad-zygo",
    "classic:round-cap",
]
WITH_SKEWER = True
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
