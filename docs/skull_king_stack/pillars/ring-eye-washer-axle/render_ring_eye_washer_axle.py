import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

TITLE = "P8 ring-eye-washer-axle"

# THE AXLE: an unbroken rod threading a flat necklace ring-eye washer through every
# seam, where the round void-eyed skulls RHYME the rings. Each tier carries exactly
# one round void so the silhouette reads as a regular voids-and-rings cadence at 58px,
# and the skull family (round dome / single socket / punched eye) reinforces the same
# read the ring-washer skewer makes — one mechanism, one shape language. The cycle is
# a clean A-B-C-A-B so the rhythm is regular, not a random pile: cyclops (one big
# socket) -> keyhole (one punched void) -> calvaria (round dome) -> repeat. Focal is
# cyclops-brow at the gap so the lit element is the boldest single round void, set
# directly above the first ring washer. COLLAR is off because the ring washers ARE the
# seam joinery — adding bead collars would muddy the one-shape read with a second tell.
RECIPE = [
    "new:cyclops-brow",   # focal at gap — one big round socket, auto-lit
    "new:keyhole-relic",  # one punched void echoes the socket + the ring below it
    "classic:calvaria",   # round dome closes the triad, a void-less round to vary value
    "new:cyclops-brow",   # cycle repeats so the voids-and-rings cadence stays regular
    "new:keyhole-relic",  # far end keeps the round-void rhythm to the pillar top
]

WITH_SKEWER = True
SKEWER_STYLE = "ring-washer"
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
