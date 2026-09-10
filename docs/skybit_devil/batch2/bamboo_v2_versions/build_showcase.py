"""Assemble the REALISTIC bamboo-boss (bamboo v2) showcase.

Compositing-only: each source sheet's hero-creature region is cropped with a
per-sheet measured window (the "Creature - hero" left panel), then
fit-inside-scaled so every creature reads whole and undistorted at the same
tile size. Bamboo v2 is a fresh elevated-realism pass with NO shipped
reference, so all five are NEW versions — there is no REFERENCE anchor tile.
They are deliberately five DISTINCT silhouette KINDs (armored sprout / wide-low
snow drift-mound / winged crow-tengu / tall three-culm gate-stack / squat
culm-legged spider); the matched tile size proves none of them collapse back
into one generic bamboo stalk.

All five earned a ship sign-off, so every tile carries a green SHIP-READY chip.
"""

import os

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# Neutral mid-grey keeps the straw/sage/lacquer-black/pine/grove palettes
# honest regardless of each source sheet's own panel backdrop.
BG = (96, 98, 104)
FRAME = (150, 152, 160)
TILE_INNER = (118, 120, 128)
INK = (28, 28, 32)
TITLE_COL = (240, 240, 236)
NAME_COL = (244, 244, 240)
FACET_COL = (190, 192, 200)
CHIP_SHIP = (96, 196, 110)   # green: passed art-director sign-off

# Per-sheet hero windows (x, y, w, h) in source pixels, measured from each
# sheet's actual left-panel hero ink bounding box plus a ~12-13px background
# margin on every side so no extremity clips — the sprout's full armored cap,
# the snow drift-mound's widest lance-clumps, the tengu's full wingspan + beak,
# the gate-god's tallest culm + base, the spider's outermost culm-legs.
# Generous bg is fine; fit_inside normalizes to the matched tile.
TILES = [
    {
        "file": "docs/skybit_devil/batch2/bamboo_v2_versions/takenoko_warashi/round_2.png",
        "crop": (1, 137, 385, 336),
        "name": "Takenoko-Warashi",
        "facet": "armored bamboo-shoot sprout",
        "ship": True,
    },
    {
        "file": "docs/skybit_devil/batch2/bamboo_v2_versions/sasa_yuki_onna/round_2.png",
        "crop": (0, 145, 424, 233),
        "name": "Sasa-Yuki-Onna",
        "facet": "snow-grass drift-spirit",
        "ship": True,
    },
    {
        "file": "docs/skybit_devil/batch2/bamboo_v2_versions/kurochiku_garasu_tengu/round_3.png",
        "crop": (39, 142, 316, 329),
        "name": "Kurochiku-Garasu-Tengu",
        "facet": "black-bamboo crow-tengu",
        "ship": True,
    },
    {
        "file": "docs/skybit_devil/batch2/bamboo_v2_versions/kadomatsu_shin/round_2.png",
        "crop": (97, 114, 226, 351),
        "name": "Kadomatsu-Shin",
        "facet": "New-Year three-culm gate-god",
        "ship": True,
    },
    {
        "file": "docs/skybit_devil/batch2/bamboo_v2_versions/take_tsuchigumo/round_2.png",
        "crop": (86, 240, 194, 193),
        "name": "Take-Tsuchigumo",
        "facet": "culm-legged grove spider",
        "ship": True,
    },
]

TILE = 240          # inner art square per tile
PAD = 26            # gap between tiles
MARGIN = 34         # outer margin
CAP_H = 76          # caption band: name + thesis + status tag
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

    f_title = pygame.font.SysFont("dejavusans", 28, bold=True)
    f_name = pygame.font.Font("game/assets/LiberationSans-Bold.ttf", 18)
    f_facet = pygame.font.SysFont("dejavusans", 13)
    f_tag = pygame.font.SysFont("dejavusans", 12, bold=True)
    f_status = pygame.font.SysFont("dejavusans", 12, bold=True)

    title = f_title.render(
        "Bamboo v2 — realistic bamboo bosses (5 distinct silhouette KINDs)",
        True, TITLE_COL,
    )
    sheet.blit(title, (MARGIN, MARGIN + (TITLE_H - title.get_height()) // 2 - 6))

    top = MARGIN + TITLE_H
    for i, t in enumerate(TILES):
        x = MARGIN + i * (cell_w + PAD)
        art_rect = pygame.Rect(x, top, TILE, TILE)

        pygame.draw.rect(sheet, TILE_INNER, art_rect)
        pygame.draw.rect(sheet, FRAME, art_rect, FRAME_W)

        img = pygame.image.load(os.path.join(ROOT, t["file"])).convert_alpha()
        crop = img.subsurface(pygame.Rect(*t["crop"])).copy()
        inner = TILE - FRAME_W * 2 - 16
        fitted = fit_inside(crop, inner)
        fx = art_rect.centerx - fitted.get_width() // 2
        fy = art_rect.centery - fitted.get_height() // 2
        sheet.blit(fitted, (fx, fy))

        # Top-left chip: all five shipped, so every tile is green SHIP-READY.
        chip_text = "SHIP-READY"
        chip_col = CHIP_SHIP
        tag = f_tag.render(chip_text, True, INK)
        tag_pad = 6
        tag_bg = pygame.Rect(
            art_rect.x + FRAME_W + 4,
            art_rect.y + FRAME_W + 4,
            tag.get_width() + tag_pad * 2,
            tag.get_height() + 4,
        )
        pygame.draw.rect(sheet, chip_col, tag_bg, border_radius=3)
        sheet.blit(tag, (tag_bg.x + tag_pad, tag_bg.y + 2))

        # Caption band: name + thesis + status line.
        cap_y = top + TILE + 8
        name = f_name.render(t["name"], True, NAME_COL)
        sheet.blit(name, (art_rect.centerx - name.get_width() // 2, cap_y))
        facet = f_facet.render(t["facet"], True, FACET_COL)
        sheet.blit(facet, (art_rect.centerx - facet.get_width() // 2, cap_y + 23))
        status = f_status.render("SHIP-READY", True, CHIP_SHIP)
        sheet.blit(status, (art_rect.centerx - status.get_width() // 2, cap_y + 44))

    out = os.path.join(HERE, "showcase.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
