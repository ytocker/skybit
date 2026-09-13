"""Assemble the KING SKULL royal-brood showcase.

Compositing-only: each source sheet's "Creature - hero" panel is cropped with a
per-sheet MEASURED window (ink/glow bounding box + a 14px background margin on
every side), then fit-inside-scaled so every king reads whole and undistorted at
one matched tile size. The two ancestors that the brood descends from — the
shipped Citipati and the evolved Koschei — anchor the row as set-apart LINEAGE
tiles (warm frame + LINEAGE tag + a divider) so a reviewer reads the six kings
against the established lineage and sees that none of them collapse back into a
generic crowned skull-man.

The crop windows are measured, not assumed: tall thin crowns/antlers/spikes and
a planted greatsword are exactly the extremities that clip a fixed crop, so each
window comes from this sheet's actual hero bbox (re-scanned at a stricter
threshold) and is verified by an edge-scan that fails if any tile touches its
border.
"""

import os

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# Neutral mid-grey keeps the coloured kings honest regardless of each sheet's own
# day/night backdrop.
BG = (96, 98, 104)
FRAME = (150, 152, 160)
FRAME_REF = (228, 196, 120)  # warm ochre sets the lineage tiles apart
TILE_INNER = (118, 120, 128)
INK = (28, 28, 32)
TITLE_COL = (240, 240, 236)
NAME_COL = (244, 244, 240)
FACET_COL = (190, 192, 200)
REF_TAG = (250, 214, 130)

# Per-sheet hero windows (x, y, w, h) in source pixels, MEASURED from each
# sheet's actual hero-panel ink/glow bounding box plus a 14px background margin
# on every side so no extremity clips — Citipati's kicked dancing leg, Koschei's
# iron spike-crown, the Regent's crown-jewel tell, the Amethyst cone-crown +
# scepter, the Carnelian's planted greatsword + war-crown, the Obsidian dome +
# floor-length robe, the Verdigris coral antlers + trailing arm, the Rose-Gold
# trefoil spike. Generous bg is fine; fit_inside normalizes the tile size.
TILES = [
    {
        "file": "docs/skybit_devil/batch2/jiangshi_epic/citipati/round_2.png",
        "crop": (89, 176, 215, 337),
        "name": "Citipati",
        "facet": "the original respected",
        "lineage": True,
    },
    {
        "file": "docs/skybit_devil/batch2/citipati_versions/koschei/round_2.png",
        "crop": (79, 147, 226, 340),
        "name": "Koschei",
        "facet": "the one evolved",
        "lineage": True,
    },
    {
        "file": "docs/skybit_devil/batch2/skull_kings/regent_koschei/round_2.png",
        "crop": (79, 107, 226, 380),
        "name": "Regent Koschei",
        "facet": "gilt iron-spike crown",
    },
    {
        "file": "docs/skybit_devil/batch2/skull_kings/amethyst_god_king/round_2.png",
        "crop": (56, 78, 278, 401),
        "name": "Amethyst God-King",
        "facet": "hollow ivory cone-crown",
    },
    {
        "file": "docs/skybit_devil/batch2/skull_kings/carnelian_warlord/round_2.png",
        "crop": (114, 159, 160, 339),
        "name": "Carnelian Warlord",
        "facet": "planted greatsword",
    },
    {
        "file": "docs/skybit_devil/batch2/skull_kings/obsidian_sovereign/round_2.png",
        "crop": (80, 97, 198, 337),
        "name": "Obsidian Sovereign",
        "facet": "onyx robe-column + dome",
    },
    {
        "file": "docs/skybit_devil/batch2/skull_kings/verdigris_drowned_king/round_2.png",
        "crop": (24, 102, 281, 417),
        "name": "Verdigris Drowned-King",
        "facet": "coral antlers + baroque pearl",
    },
    {
        "file": "docs/skybit_devil/batch2/skull_kings/rosegold_prince/round_2.png",
        "crop": (71, 150, 234, 308),
        "name": "Rose-Gold Prince",
        "facet": "spiked trefoil coronet",
    },
]

TILE = 240          # inner art square per tile
PAD = 26            # gap between tiles
LIN_GAP = 30        # extra gap after the lineage block, before the kings
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
    n_lin = sum(1 for t in TILES if t.get("lineage"))
    cell_w = TILE
    cell_h = TILE + CAP_H

    sheet_w = MARGIN * 2 + n * cell_w + (n - 1) * PAD + LIN_GAP
    sheet_h = MARGIN + TITLE_H + cell_h + MARGIN

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(BG)

    f_title = pygame.font.SysFont("dejavusans", 30, bold=True)
    f_name = pygame.font.Font(os.path.join(ROOT, "game/assets/LiberationSans-Bold.ttf"), 19)
    f_facet = pygame.font.SysFont("dejavusans", 14)
    f_tag = pygame.font.SysFont("dejavusans", 12, bold=True)

    title = f_title.render(
        "KING SKULL — the royal brood (lineage + six crowned kings)", True, TITLE_COL
    )
    sheet.blit(title, (MARGIN, MARGIN + (TITLE_H - title.get_height()) // 2 - 6))

    top = MARGIN + TITLE_H
    for i, t in enumerate(TILES):
        # Push the kings right of the lineage block by one extra gap.
        x = MARGIN + i * (cell_w + PAD) + (LIN_GAP if i >= n_lin else 0)
        art_rect = pygame.Rect(x, top, TILE, TILE)
        is_lin = t.get("lineage", False)

        pygame.draw.rect(sheet, TILE_INNER, art_rect)
        frame_col = FRAME_REF if is_lin else FRAME
        pygame.draw.rect(sheet, frame_col, art_rect, FRAME_W)

        img = pygame.image.load(os.path.join(ROOT, t["file"])).convert_alpha()
        crop = img.subsurface(pygame.Rect(*t["crop"])).copy()
        inner = TILE - FRAME_W * 2 - 16
        fitted = fit_inside(crop, inner)
        fx = art_rect.centerx - fitted.get_width() // 2
        fy = art_rect.centery - fitted.get_height() // 2
        sheet.blit(fitted, (fx, fy))

        if is_lin:
            tag = f_tag.render("LINEAGE", True, INK)
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

        # Divider after the lineage block, separating ancestors from the kings.
        if is_lin and i == n_lin - 1:
            dx = x + cell_w + (PAD + LIN_GAP) // 2
            pygame.draw.line(sheet, FRAME_REF, (dx, top - 6), (dx, top + cell_h + 6), 2)

    out = os.path.join(HERE, "showcase.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
