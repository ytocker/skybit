"""Final — the chosen Profile entry: Card C (JEWEL EDGE + BEVELED NAMEPLATE),
with the top-right records badge removed per the owner's call.

Reuses round_2.py's exact menu mock + Card C construction, minus the
records_badge() cue. Renders the full 360x640 menu over the DUSK biome sky
(2x for clarity) plus a paired TRUE 1x proof crop over DUSK and the brightest
MIDDAY sky, so the clean jewel-edge card reads at native scale on both.
"""
import os
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

pygame.init()
pygame.display.set_mode((8, 8))

from game.config import W, H
from game.hud import _font  # noqa: F401  (module import warms caches)

# Reuse every helper + the biome skies from the round-2 sheet, unchanged.
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "_r2", os.path.join(os.path.dirname(__file__), "render.py"))
_r2 = importlib.util.module_from_spec(_spec)
# Guard render.py's main() from firing on import.
_r2.__name__ = "_r2"
_spec.loader.exec_module(_r2)


def card_plate_clean(surf):
    """Card C exactly as shipped, but WITHOUT the records_badge() call."""
    fr = _r2.dio_region(pad=12)
    fr.height += 20
    _r2.tap_glow(surf, fr, radius=15, strength=0.9)

    pygame.draw.rect(surf, _r2._GOLD_MID, fr, width=1, border_radius=14)
    pygame.draw.rect(surf, _r2._GOLD_BRIGHT, fr.inflate(-12, -12), width=1,
                     border_radius=9)
    pygame.draw.line(surf, (*_r2._GOLD_PALE, 200), (fr.left + 16, fr.top + 2),
                     (fr.right - 16, fr.top + 2), 1)

    plate = pygame.Rect(fr.centerx - 60, fr.bottom - 24, 120, 22)
    sh = pygame.Surface((plate.w + 6, plate.h + 6), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 140), sh.get_rect(), border_radius=8)
    surf.blit(sh, (plate.x - 3, plate.y + 2))
    pygame.draw.rect(surf, _r2._GOLD_DEEP, plate, border_radius=7)
    pygame.draw.rect(surf, _r2._GOLD_MID, plate.inflate(-3, -3), border_radius=6)
    pygame.draw.line(surf, _r2._GOLD_PALE, (plate.left + 8, plate.top + 3),
                     (plate.right - 8, plate.top + 3), 1)
    pygame.draw.line(surf, (60, 40, 6), (plate.left + 8, plate.bottom - 3),
                     (plate.right - 8, plate.bottom - 3), 1)
    inset = plate.inflate(-8, -8)
    pygame.draw.rect(surf, (30, 18, 8), inset, border_radius=4)
    _r2.profile_label(surf, inset, dark_engrave=True, size=13)


def build(sky):
    surf = _r2.menu_base(sky)
    card_plate_clean(surf)
    _r2.bottom_chips(surf)
    return surf


def main():
    dusk = build(_r2.DUSK_SKY)
    midday = build(_r2.DAY_SKY)

    hero = pygame.transform.smoothscale(dusk, (W * 2, H * 2))

    pad = 24
    proof = _r2.PROOF
    proof_lab = 26
    sheet_w = pad * 3 + W * 2 + proof.width
    sheet_h = pad * 2 + H * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 18, 34))

    tf = _font(24, True)
    sheet.blit(tf.render("SKYBIT · Profile entry — FINAL · Card C (jewel edge + "
                         "nameplate), records badge removed",
                         True, (240, 224, 180)), (pad, 6))

    hx, hy = pad, pad + 8
    pygame.draw.rect(sheet, (8, 5, 20), (hx - 3, hy - 3, W * 2 + 6, H * 2 + 6))
    sheet.blit(hero, (hx, hy))

    # True-1x proofs stacked on the right: dusk over midday.
    px = hx + W * 2 + pad
    lab_f = _font(13, True)
    py = hy + 6
    for panel, tag in ((dusk, "DUSK"), (midday, "MIDDAY")):
        crop = panel.subsurface(proof).copy()
        pl = lab_f.render("TRUE 1× · " + tag, True, (232, 214, 168))
        sheet.blit(pl, (px, py))
        py += proof_lab
        pygame.draw.rect(sheet, (40, 30, 58),
                         (px - 2, py - 2, proof.width + 4, proof.height + 4))
        sheet.blit(crop, (px, py))
        py += proof.height + 34

    out = os.path.join(os.path.dirname(__file__), "final.png")
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
