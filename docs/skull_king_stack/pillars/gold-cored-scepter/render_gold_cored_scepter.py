"""P7 gold-cored-scepter — the KING'S STAFF of the skewer family.

Why this recipe: the regal pole among the five skewer styles. The gem-tip skewer
draws a gold-MARROW rod (RK._rod_seg, not the dark crude spit) capped by a clean
faceted cyan gem point lancing into the gap — no barbs (those own the harpoon
pillar). To earn "richest, most regal" it stacks ONLY palm reliquary skulls — the
ornamented, gold-suture, cabochon-bearing family — so the whole column reads as a
jewelled relic-staff rather than a war-spit. The cyan jewels cluster toward the gap
(focal forehead cabochon directly under the lancing gem point = jewel-on-jewel
crown), then thin to plain weathered relics at the far end so the regal end is
unmistakable. Rhythm closed/agape/cracked avoids a uniform palm run and out-varies
the all-classic plain-bone-spit (P6) and the alternating totem (P1).
"""
import os, sys
sys.path.insert(0, "/home/user/skybit/docs/skull_king_stack/pillars")
import pygame
import pillar_engine as PE

TITLE = "P7 gold-cored-scepter"
# gap-edge -> far. palm:4 focal = closed jaw + gold-pip suture + forehead third-eye
# cabochon, meeting the lancing gem point. palm:0/palm:2 keep the cyan jewels dense
# near the gap (forehead then eye-socket = same jewel, different seat, so it reads
# varied not repeated). palm:1 (broad, gem-free) and palm:5 (chipped relic) give a
# heavier, un-jewelled base that lets the crown jewels pop.
RECIPE = [
    "palm:4",
    "palm:0",
    "palm:2",
    "palm:1",
    "palm:5",
]
WITH_SKEWER = True
SKEWER_STYLE = "gem-tip"
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
