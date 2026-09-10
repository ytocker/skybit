"""Assemble the Mukha-Devi many-armed bone-goddess versions showcase.

Compositing-only: each source sheet's hero-creature region is cropped with a
per-sheet measured window (the "creature - hero" panel only — not the pillar,
32px chips, blackout proof, or palette strip), then fit-inside-scaled so every
goddess reads whole and undistorted at the same tile size. The shipped
Mukha-Devi anchors the row as a set-apart REFERENCE so a reviewer can read each
spin-off against the established six-armed bone-mother — and because the row is
ordered chibi -> monumental left-to-right, the matched tile size makes the
proportion story (tiny-idol saint up to temple-pylon colossus) legible at a
glance.
"""

import os

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# Neutral mid-grey keeps coloured bone-goddesses honest regardless of their own
# day/night backdrop in the source sheet.
BG = (96, 98, 104)
FRAME = (150, 152, 160)
FRAME_REF = (228, 196, 120)  # warm ochre sets the reference tile apart
TILE_INNER = (118, 120, 128)
INK = (28, 28, 32)
TITLE_COL = (240, 240, 236)
NAME_COL = (244, 244, 240)
FACET_COL = (190, 192, 200)
REF_TAG = (250, 214, 130)

# Per-sheet hero windows (x, y, w, h) in source pixels, measured from each
# sheet's actual hero-panel ink/glow bounding box plus a 14px background margin
# on every side so no extremity clips — the reference fan's full arm-spread +
# plinth, the saint's pointed-almond mandorla tips, the naga hood-ring lobes,
# the crescent horn cusps + low cupping arms, the coral canopy spread, the
# pylon's cornice lips + rooted plinth. Generous bg is fine; fit_inside
# normalizes. Each window was edge-scan verified to leave a clean border
# after fit_inside (zero non-background pixels touch the tile edge).
TILES = [
    {
        "file": "docs/skybit_devil/batch2/citipati_versions/mukha_devi/round_2.png",
        "crop": (31, 203, 314, 219),
        "name": "Mukha-Devi",
        "facet": "six-armed bone-mother (the Original)",
        "reference": True,
    },
    {
        "file": "docs/skybit_devil/batch2/mukha_devi_versions/asha_mukti/round_3.png",
        "crop": (115, 163, 157, 307),
        "name": "Asha-Mukti",
        "facet": "lotus bloom-mandorla saint",
    },
    {
        "file": "docs/skybit_devil/batch2/mukha_devi_versions/nagini_devi/round_2.png",
        "crop": (85, 225, 213, 185),
        "name": "Nagini-Devi",
        "facet": "serpent hood-ring naga-queen",
    },
    {
        "file": "docs/skybit_devil/batch2/mukha_devi_versions/chandra_mata/round_3.png",
        "crop": (40, 163, 278, 235),
        "name": "Chandra-Mata",
        "facet": "lunar crescent-arc mother",
    },
    {
        "file": "docs/skybit_devil/batch2/mukha_devi_versions/rakta_ambu/round_3.png",
        "crop": (68, 182, 274, 230),
        "name": "Rakta-Ambu",
        "facet": "coral-tree bone-canopy",
    },
    {
        "file": "docs/skybit_devil/batch2/mukha_devi_versions/asthi_samrat/round_3.png",
        "crop": (107, 190, 175, 348),
        "name": "Asthi-Samrat",
        "facet": "temple-pylon colossus",
    },
]

TILE = 240          # inner art square per tile
PAD = 26            # gap between tiles
MARGIN = 34         # outer margin
CAP_H = 56          # caption band under each tile art
TITLE_H = 70
FRAME_W = 4


def fit_inside(surf, box):
    """Scale a surface to sit whole inside a box, preserving aspect."""
    sw, sh = surf.get_size()
    s = min(box / sw, box / sh)
    return pygame.transform.smoothscale(surf, (max(1, int(sw * s)), max(1, int(sh * s))))


def main():
    pygame.init()
    pygame.font.init()
    # A display mode is required before convert_alpha() even under the dummy
    # video driver used for headless rendering.
    pygame.display.set_mode((1, 1))

    n = len(TILES)
    tile_outer = TILE
    cell_w = tile_outer
    cell_h = tile_outer + CAP_H

    sheet_w = MARGIN * 2 + n * cell_w + (n - 1) * PAD
    sheet_h = MARGIN + TITLE_H + cell_h + MARGIN

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(BG)

    f_title = pygame.font.SysFont("dejavusans", 30, bold=True)
    f_name = pygame.font.Font("game/assets/LiberationSans-Bold.ttf", 19)
    f_facet = pygame.font.SysFont("dejavusans", 14)
    f_tag = pygame.font.SysFont("dejavusans", 12, bold=True)

    title = f_title.render(
        "Mukha-Devi versions — many-armed bone-goddess bosses", True, TITLE_COL
    )
    sheet.blit(title, (MARGIN, MARGIN + (TITLE_H - title.get_height()) // 2 - 6))

    top = MARGIN + TITLE_H
    for i, t in enumerate(TILES):
        x = MARGIN + i * (cell_w + PAD)
        art_rect = pygame.Rect(x, top, tile_outer, tile_outer)
        is_ref = t.get("reference", False)

        # Set the reference apart: warm frame, a vertical divider after it.
        pygame.draw.rect(sheet, TILE_INNER, art_rect)
        frame_col = FRAME_REF if is_ref else FRAME
        pygame.draw.rect(sheet, frame_col, art_rect, FRAME_W)

        img = pygame.image.load(os.path.join(ROOT, t["file"])).convert_alpha()
        crop = img.subsurface(pygame.Rect(*t["crop"])).copy()
        inner = TILE - FRAME_W * 2 - 16
        fitted = fit_inside(crop, inner)
        fx = art_rect.centerx - fitted.get_width() // 2
        fy = art_rect.centery - fitted.get_height() // 2
        sheet.blit(fitted, (fx, fy))

        if is_ref:
            tag = f_tag.render("REFERENCE", True, INK)
            tag_pad = 6
            tag_bg = pygame.Rect(
                art_rect.x + FRAME_W + 4,
                art_rect.y + FRAME_W + 4,
                tag.get_width() + tag_pad * 2,
                tag.get_height() + 4,
            )
            pygame.draw.rect(sheet, REF_TAG, tag_bg, border_radius=3)
            sheet.blit(tag, (tag_bg.x + tag_pad, tag_bg.y + 2))

        # Caption band: name + lead facet.
        cap_y = top + tile_outer + 8
        name = f_name.render(t["name"], True, NAME_COL)
        sheet.blit(name, (art_rect.centerx - name.get_width() // 2, cap_y))
        facet = f_facet.render(t["facet"], True, FACET_COL)
        sheet.blit(facet, (art_rect.centerx - facet.get_width() // 2, cap_y + 24))

        # Divider between the reference and the five new versions.
        if is_ref:
            dx = x + cell_w + PAD // 2
            pygame.draw.line(sheet, FRAME_REF, (dx, top - 6), (dx, top + cell_h + 6), 2)

    out = os.path.join(HERE, "showcase.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
