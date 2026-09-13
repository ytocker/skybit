"""Assemble the Mokoi-versions flat-graphic painted-spirit showcase.

Compositing-only: each source sheet's hero-creature panel (a) is cropped with a
per-sheet measured window (the bounding box of the whole creature, clear of the
caption text and the pillar / 32px gameplay panels), then fit-inside-scaled so
every spirit reads whole and undistorted at the same tile size. The shipped
Mokoi anchors the row as a set-apart REFERENCE so a reviewer can read each new
spin-off against the established source mask.

This lineage is intentionally FLAT-GRAPHIC (saturated flat fills + ink keyline
+ pattern detail), not 3D-shaded -- that is the look, not a defect.
"""

import os

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# Neutral mid-grey keeps the saturated flat fills honest regardless of each
# source sheet's own day/night backdrop.
BG = (96, 98, 104)
FRAME = (150, 152, 160)
FRAME_REF = (228, 196, 120)  # warm ochre sets the reference tile apart
TILE_INNER = (118, 120, 128)
INK = (28, 28, 32)
TITLE_COL = (240, 240, 236)
NAME_COL = (244, 244, 240)
FACET_COL = (190, 192, 200)
REF_TAG = (250, 214, 130)

# Per-sheet hero windows (x, y, w, h) in source pixels, measured against each
# sheet's panel-(a) inner fill so only the creature carries in -- no caption
# text, no pillar / 32px chip panels.
TILES = [
    {
        "file": "docs/skybit_devil/batch2/leyak_epic/mokoi/round_2.png",
        "crop": (85, 101, 185, 512),
        "name": "Mokoi",
        "facet": "the source mask (shipped)",
        "reference": True,
    },
    {
        "file": "docs/skybit_devil/batch2/mokoi_versions/wandjina/round_2.png",
        "crop": (60, 101, 288, 387),
        "name": "Wandjina",
        "facet": "white-clay rain-ancestor",
    },
    {
        "file": "docs/skybit_devil/batch2/mokoi_versions/mimi/round_2.png",
        "crop": (82, 252, 173, 215),
        "name": "Mimi",
        "facet": "crosshatch stick-spirit",
    },
    {
        "file": "docs/skybit_devil/batch2/mokoi_versions/quinkan_imjim/round_2.png",
        "crop": (75, 101, 205, 456),
        "name": "Quinkan-Imjim",
        "facet": "knob-headed ambush-imp",
    },
    {
        "file": "docs/skybit_devil/batch2/mokoi_versions/barramundi/round_2.png",
        "crop": (60, 274, 264, 194),
        "name": "Barramundi",
        "facet": "x-ray fish-beast",
    },
    {
        "file": "docs/skybit_devil/batch2/mokoi_versions/baiame/round_2.png",
        "crop": (66, 101, 283, 241),
        "name": "Baiame",
        "facet": "horned sky all-father",
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
    cell_w = TILE
    cell_h = TILE + CAP_H

    sheet_w = MARGIN * 2 + n * cell_w + (n - 1) * PAD
    sheet_h = MARGIN + TITLE_H + cell_h + MARGIN

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(BG)

    f_title = pygame.font.SysFont("dejavusans", 30, bold=True)
    f_name = pygame.font.Font(os.path.join(ROOT, "game/assets/LiberationSans-Bold.ttf"), 19)
    f_facet = pygame.font.SysFont("dejavusans", 14)
    f_tag = pygame.font.SysFont("dejavusans", 12, bold=True)

    title = f_title.render(
        "Mokoi versions — flat-graphic painted-spirit bosses", True, TITLE_COL
    )
    sheet.blit(title, (MARGIN, MARGIN + (TITLE_H - title.get_height()) // 2 - 6))

    top = MARGIN + TITLE_H
    for i, t in enumerate(TILES):
        x = MARGIN + i * (cell_w + PAD)
        art_rect = pygame.Rect(x, top, TILE, TILE)
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
        cap_y = top + TILE + 8
        name = f_name.render(t["name"], True, NAME_COL)
        sheet.blit(name, (art_rect.centerx - name.get_width() // 2, cap_y))
        facet = f_facet.render(t["facet"], True, FACET_COL)
        sheet.blit(facet, (art_rect.centerx - facet.get_width() // 2, cap_y + 24))

        # Divider between the reference and the five new spin-offs.
        if is_ref:
            dx = x + cell_w + PAD // 2
            pygame.draw.line(sheet, FRAME_REF, (dx, top - 6), (dx, top + cell_h + 6), 2)

    out = os.path.join(HERE, "showcase.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
