"""Assemble the Jangseung carved-wood guardian-boss variant showcase.

Compositing-only: each source sheet's hero-creature region (panel (a)) is
cropped with a per-sheet measured window, then fit-inside-scaled so every
guardian reads whole and undistorted at the same tile size. The shipped
Jangseung anchors the row as a set-apart REFERENCE so a reviewer can read each
new spin-off against the established carved-post silhouette.
"""

import os

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# Neutral mid-grey keeps the warm carved-wood tones honest regardless of each
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

# Per-sheet hero windows (x, y, w, h) in source pixels. Each window was
# re-measured from the actual painted creature bounds (an automated non-
# background bounding-box scan of the hero panel) and padded with a clear
# margin on every side, so no carved post, mane-ring, hat, lean, hair fan,
# bird bill, scroll/pole base or keyline touches a crop edge. Generous extra
# background is fine — fit_inside() normalizes every tile to the same size —
# but clipping the creature is not. Windows stay left of the (b) gap-pillar /
# (c) chip columns and above each sheet's "(a) Hero ..." caption so only the
# hero carries in. Muljang is the tight case: its forward lean reaches within
# 10px of the panel's left edge and its base plate ends only ~9px above its own
# caption, so those two margins are the most the source affords without clipping
# the figure or pulling caption text in.
TILES = [
    {
        "file": "docs/skybit_devil/batch2/jiangshi_epic/jangseung/round_2.png",
        "crop": (80, 56, 159, 462),
        "name": "Jangseung",
        "facet": "the source post",
        "reference": True,
    },
    {
        "file": "docs/skybit_devil/batch2/jangseung_versions/haedung/round_4.png",
        "crop": (40, 56, 238, 475),
        "name": "Haedung",
        "facet": "fire-eating guardian-lion",
    },
    {
        "file": "docs/skybit_devil/batch2/jangseung_versions/harubang/round_2.png",
        "crop": (64, 99, 190, 438),
        "name": "Harubang",
        "facet": "bellied grandfather post",
    },
    {
        "file": "docs/skybit_devil/batch2/jangseung_versions/muljang/round_2.png",
        "crop": (0, 139, 325, 411),
        "name": "Muljang",
        "facet": "prow-rider figurehead",
    },
    {
        "file": "docs/skybit_devil/batch2/jangseung_versions/hyeoljang/round_2.png",
        "crop": (72, 56, 174, 457),
        "name": "Hyeoljang",
        "facet": "tongue-out warrior",
    },
    {
        "file": "docs/skybit_devil/batch2/jangseung_versions/sotjang/round_2.png",
        "crop": (71, 65, 164, 480),
        "name": "Sotjang",
        "facet": "sky-bird sentinel pole",
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

    title = f_title.render("Jangseung versions — carved-wood guardian bosses", True, TITLE_COL)
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

        # Divider between the reference and the five new variants.
        if is_ref:
            dx = x + cell_w + PAD // 2
            pygame.draw.line(sheet, FRAME_REF, (dx, top - 6), (dx, top + cell_h + 6), 2)

    out = os.path.join(HERE, "showcase.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
