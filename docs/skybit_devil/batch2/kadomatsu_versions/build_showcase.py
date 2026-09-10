"""Assemble the Kadomatsu brood showcase — 5 epic bamboo-plant bosses.

Compositing-only: each source sheet's hero-creature region is cropped with a
per-sheet measured window (the "Body-is-bamboo - hero" panel), then
fit-inside-scaled so every plant-boss reads whole and undistorted at one tile
size. The shipped Kadomatsu-Shin anchors the row as a set-apart REFERENCE so a
reviewer reads each new version against the established three-culm silhouette —
and because these five are deliberately five DISTINCT KINDs (open gate-frame /
offering-mound pyre / coiling serpent / single fat monolith / squat guardian),
the matched tile size proves none of them collapse back into the parent trio.

Shishi-Kadomatsu carries an honest AMBER "SHIP w/ note" chip rather than the
green SHIP-READY — its R5 crown-notch fix is a single flagged caveat, not a
clean pass, and the chip colour says so at a glance.
"""

import os

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# Neutral mid-grey keeps the green/cream culms honest regardless of each
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
SHIP_TAG = (118, 196, 120)    # green — clean SHIP-READY
NOTE_TAG = (236, 176, 72)     # amber — flags "SHIP w/ note" honestly

# Per-sheet hero windows (x, y, w, h) in source pixels, measured from each
# sheet's "Body-is-bamboo - hero" panel ink/glow bounding box plus a generous
# ~12-14px background margin on every side so no extremity (top cut-disc, foot
# plums, straw bind, serpent whisker, guardian crown) clips. fit_inside then
# normalizes — generous background is fine and keeps every creature WHOLE.
TILES = [
    {
        "file": "docs/skybit_devil/batch2/bamboo_v2_versions/kadomatsu_shin/round_2.png",
        "crop": (114, 116, 200, 348),
        "name": "Kadomatsu-Shin",
        "facet": "New-Year three-culm gate-god (parent)",
        "reference": True,
    },
    {
        "file": "docs/skybit_devil/batch2/kadomatsu_versions/kadomatsu_torii/round_3.png",
        "crop": (12, 166, 360, 332),
        "name": "Kadomatsu-Torii",
        "facet": "colossal shrine-gate of cut culms",
        "ship": True,
    },
    {
        "file": "docs/skybit_devil/batch2/kadomatsu_versions/kazari_no_yama/round_2.png",
        "crop": (52, 88, 320, 392),
        "name": "Kazari-no-Yama",
        "facet": "bristling offering-mound pyre",
        "ship": True,
    },
    {
        "file": "docs/skybit_devil/batch2/kadomatsu_versions/tatsu_no_takemura/round_4.png",
        "crop": (86, 120, 220, 356),
        "name": "Tatsu-no-Takemura",
        "facet": "coiling grove-serpent",
        "ship": True,
    },
    {
        "file": "docs/skybit_devil/batch2/kadomatsu_versions/moso_no_taisho/round_3.png",
        "crop": (98, 88, 192, 352),
        "name": "Moso-no-Taisho",
        "facet": "great single-culm monolith",
        "ship": True,
    },
    {
        "file": "docs/skybit_devil/batch2/kadomatsu_versions/shishi_kadomatsu/round_5.png",
        "crop": (74, 272, 246, 190),
        "name": "Shishi-Kadomatsu",
        "facet": "komainu guardian, bound-culm",
        "note": True,  # SHIP w/ note — amber chip, not clean green
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


def chip(sheet, art_rect, text, bg_col, f_tag):
    """Draw a status/reference chip pinned to the tile's top-left corner."""
    tag = f_tag.render(text, True, INK)
    tag_pad = 6
    tag_bg = pygame.Rect(
        art_rect.x + FRAME_W + 4,
        art_rect.y + FRAME_W + 4,
        tag.get_width() + tag_pad * 2,
        tag.get_height() + 4,
    )
    pygame.draw.rect(sheet, bg_col, tag_bg, border_radius=3)
    sheet.blit(tag, (tag_bg.x + tag_pad, tag_bg.y + 2))


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

    f_title = pygame.font.SysFont("dejavusans", 28, bold=True)
    f_name = pygame.font.Font("game/assets/LiberationSans-Bold.ttf", 18)
    f_facet = pygame.font.SysFont("dejavusans", 13)
    f_tag = pygame.font.SysFont("dejavusans", 12, bold=True)

    title = f_title.render(
        "Kadomatsu brood — 5 epic bamboo-plant bosses (inspired by Kadomatsu-Shin)",
        True,
        TITLE_COL,
    )
    sheet.blit(title, (MARGIN, MARGIN + (TITLE_H - title.get_height()) // 2 - 6))

    top = MARGIN + TITLE_H
    for i, t in enumerate(TILES):
        x = MARGIN + i * (cell_w + PAD)
        art_rect = pygame.Rect(x, top, TILE, TILE)
        is_ref = t.get("reference", False)

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
            chip(sheet, art_rect, "ORIGINAL", REF_TAG, f_tag)
        elif t.get("note"):
            chip(sheet, art_rect, "SHIP w/ note", NOTE_TAG, f_tag)
        elif t.get("ship"):
            chip(sheet, art_rect, "SHIP-READY", SHIP_TAG, f_tag)

        # Caption band: name + lead facet.
        cap_y = top + TILE + 8
        name = f_name.render(t["name"], True, NAME_COL)
        sheet.blit(name, (art_rect.centerx - name.get_width() // 2, cap_y))
        facet = f_facet.render(t["facet"], True, FACET_COL)
        sheet.blit(facet, (art_rect.centerx - facet.get_width() // 2, cap_y + 24))

        # Divider sets the reference apart from the five new versions.
        if is_ref:
            dx = x + cell_w + PAD // 2
            pygame.draw.line(sheet, FRAME_REF, (dx, top - 6), (dx, top + cell_h + 6), 2)

    out = os.path.join(HERE, "showcase.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
