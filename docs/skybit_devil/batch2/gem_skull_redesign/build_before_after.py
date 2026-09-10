"""Assemble the five-sister gem/skull/hand BEFORE/AFTER aggregate.

Compositing-only: no new design here. Each of the five sisters gets one row —
the pre-redesign hero on the left BEFORE column, the matured hero on the right
AFTER column — so the redesign reads as a side-by-side per sister. Every figure
is measured-cropped by an edge scan so all ten tiles sit on a common baseline at
one matched tile scale; no hand-tuned per-sheet window.

The scan handles the two backdrop kinds these source heroes actually use (matching
the COURT showcase's edge-scan approach):
  * transparent heroes (alpha == 0 is background) — vajra_rakta, ratna_padmini
  * opaque-gradient heroes (per-row background sampled from the edge columns, so the
    smooth day/night gradient never counts as ink) — asthi_dakini, bhasma_yogini,
    jvala_nirmala
A `skip_top` band excludes a hero sheet's printed name strip from the figure bbox
(bhasma_yogini + jvala_nirmala carry a title strip above a clear gap before the
figure). A measured margin pads each bbox; after fit-inside scaling, a post-check
re-runs the content test on the placed tile's inner box and reports clip
violations (target 0).
"""

import os

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
# docs/skybit_devil/batch2/gem_skull_redesign/ -> four hops to the repo root,
# where game/assets/ lives.
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# Neutral mid-grey keeps every sister's own day/night backdrop from skewing the
# matched-scale read.
BG = (96, 98, 104)
FRAME = (150, 152, 160)
FRAME_AFTER = (228, 196, 120)  # warm ochre marks the matured AFTER column
TILE_INNER = (118, 120, 128)
INK = (28, 28, 32)
TITLE_COL = (240, 240, 236)
COL_COL = (244, 244, 240)
NAME_COL = (244, 244, 240)
CAP_COL = (208, 210, 218)

# Per sister: the BEFORE/AFTER hero files plus each hero's scan mode. Both heroes
# in a row share the row's backdrop kind, but the mode is declared per file so a
# future swap stays honest.
ROWS = [
    {
        "name": "#1 Asthi-Dakini",
        "before": {
            "file": "docs/skybit_devil/batch2/mukha_citipati_court/asthi_dakini/round_1_hero.png",
            "mode": "gradient",
        },
        "after": {
            "file": "docs/skybit_devil/batch2/mukha_citipati_court/asthi_dakini/round_10_hero.png",
            "mode": "gradient",
        },
    },
    {
        "name": "#2 Vajra-Rakta",
        "before": {
            "file": "docs/skybit_devil/batch2/mukha_citipati_court/vajra_rakta/round_2_hero.png",
            "mode": "alpha",
        },
        "after": {
            "file": "docs/skybit_devil/batch2/mukha_citipati_court/vajra_rakta/round_7_hero.png",
            "mode": "alpha",
        },
    },
    {
        "name": "#3 Ratna-Padmini",
        "before": {
            "file": "docs/skybit_devil/batch2/mukha_citipati_court/ratna_padmini/round_2_hero.png",
            "mode": "alpha",
        },
        "after": {
            "file": "docs/skybit_devil/batch2/mukha_citipati_court/ratna_padmini/round_7_hero.png",
            "mode": "alpha",
        },
    },
    {
        "name": "#4 Bhasma-Yogini",
        "before": {
            "file": "docs/skybit_devil/batch2/mukha_citipati_court_ii/bhasma_yogini/round_2_hero.png",
            "mode": "gradient",
            "skip_top": 120,  # excludes the printed name strip above the figure
        },
        "after": {
            "file": "docs/skybit_devil/batch2/mukha_citipati_court_ii/bhasma_yogini/round_7_hero.png",
            "mode": "gradient",
            "skip_top": 120,
        },
    },
    {
        "name": "#5 Jvala-Nirmala",
        "before": {
            "file": "docs/skybit_devil/batch2/mukha_citipati_court_ii/jvala_nirmala/round_2_hero.png",
            "mode": "gradient",
            "skip_top": 120,
        },
        "after": {
            "file": "docs/skybit_devil/batch2/mukha_citipati_court_ii/jvala_nirmala/round_8_hero.png",
            "mode": "gradient",
            "skip_top": 120,
        },
    },
]

TILE = 300          # inner art square per tile
PAD = 26            # gap between the two columns
ROW_GAP = 22        # gap between sister rows
MARGIN = 40         # outer margin
LABEL_W = 196      # left gutter carrying each sister's #N + name
COLHEAD_H = 52      # BEFORE/AFTER column header band
TITLE_H = 74
CAP_H = 62          # bottom caption strip
FRAME_W = 4
MARGIN_PX = 16      # background margin baked around each measured bbox


def _content_mask(img, spec):
    """Return (xa, xb, ya, yb) scan window and a predicate(x, y) -> bool is-ink.

    Background varies by source: transparent alpha or an opaque vertical gradient
    (sampled per row from the edge columns so the smooth backdrop never reads as ink).
    """
    w, h = img.get_size()
    mode = spec["mode"]

    if mode == "alpha":
        def is_ink(x, y):
            return img.get_at((x, y))[3] > 24

        return 0, w, 0, h, is_ink

    # gradient: per-row background = mean of the two edge columns; ink deviates from it.
    skip = spec.get("skip_top", 0)
    left = [img.get_at((1, y))[:3] for y in range(h)]
    right = [img.get_at((w - 2, y))[:3] for y in range(h)]
    rowbg = [
        ((left[y][0] + right[y][0]) // 2,
         (left[y][1] + right[y][1]) // 2,
         (left[y][2] + right[y][2]) // 2)
        for y in range(h)
    ]

    def is_ink(x, y):
        c = img.get_at((x, y))[:3]
        b = rowbg[y]
        return abs(c[0] - b[0]) + abs(c[1] - b[1]) + abs(c[2] - b[2]) >= 30

    return 0, w, skip, h, is_ink


def measure_bbox(img, spec):
    """Edge-scan the figure's ink bbox; return a Rect padded by MARGIN_PX (clamped)."""
    w, h = img.get_size()
    xa, xb, ya, yb, is_ink = _content_mask(img, spec)
    minx = miny = 10 ** 9
    maxx = maxy = -1
    # Step 2px on the coarse pass for speed; figures are large so 2px never skips a limb.
    for y in range(ya, yb, 2):
        for x in range(xa, xb, 2):
            if is_ink(x, y):
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x
                if y < miny:
                    miny = y
                if y > maxy:
                    maxy = y
    if maxx < 0:
        return pygame.Rect(0, 0, w, h)
    minx = max(0, minx - MARGIN_PX)
    miny = max(0, miny - MARGIN_PX)
    maxx = min(w - 1, maxx + MARGIN_PX)
    maxy = min(h - 1, maxy + MARGIN_PX)
    return pygame.Rect(minx, miny, maxx - minx + 1, maxy - miny + 1)


def fit_inside(surf, box):
    """Scale a surface to sit whole inside a box, preserving aspect."""
    sw, sh = surf.get_size()
    s = min(box / sw, box / sh)
    return pygame.transform.smoothscale(
        surf, (max(1, int(sw * s)), max(1, int(sh * s)))
    )


def main():
    pygame.init()
    pygame.font.init()
    # A display mode is required before convert_alpha() even under the dummy
    # video driver used for headless rendering.
    pygame.display.set_mode((1, 1))

    n = len(ROWS)
    cell_w = TILE
    cell_h = TILE

    sheet_w = MARGIN + LABEL_W + cell_w + PAD + cell_w + MARGIN
    sheet_h = (
        MARGIN + TITLE_H + COLHEAD_H
        + n * cell_h + (n - 1) * ROW_GAP
        + CAP_H + MARGIN
    )

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(BG)

    f_title = pygame.font.SysFont("dejavusans", 30, bold=True)
    f_col = pygame.font.SysFont("dejavusans", 26, bold=True)
    f_name = pygame.font.Font(
        os.path.join(ROOT, "game/assets/LiberationSans-Bold.ttf"), 22
    )
    f_cap = pygame.font.SysFont("dejavusans", 15)

    title = f_title.render(
        "Five sisters — original BEFORE vs themed-skull final AFTER",
        True,
        TITLE_COL,
    )
    sheet.blit(title, (MARGIN, MARGIN + (TITLE_H - title.get_height()) // 2 - 6))

    # Column anchors.
    before_x = MARGIN + LABEL_W
    after_x = before_x + cell_w + PAD
    head_top = MARGIN + TITLE_H

    # Column headers.
    bh = f_col.render("BEFORE", True, COL_COL)
    ah = f_col.render("AFTER", True, FRAME_AFTER)
    sheet.blit(bh, (before_x + (cell_w - bh.get_width()) // 2,
                    head_top + (COLHEAD_H - bh.get_height()) // 2))
    sheet.blit(ah, (after_x + (cell_w - ah.get_width()) // 2,
                    head_top + (COLHEAD_H - ah.get_height()) // 2))

    grid_top = head_top + COLHEAD_H
    clip_violations = 0

    for ri, row in enumerate(ROWS):
        top = grid_top + ri * (cell_h + ROW_GAP)

        # Sister name in the left gutter, vertically centred on the row.
        name = f_name.render(row["name"], True, NAME_COL)
        sheet.blit(
            name,
            (MARGIN + (LABEL_W - 12 - name.get_width()) // 2,
             top + (cell_h - name.get_height()) // 2),
        )

        for col, (spec, cx, is_after) in enumerate((
            (row["before"], before_x, False),
            (row["after"], after_x, True),
        )):
            art_rect = pygame.Rect(cx, top, cell_w, cell_h)

            pygame.draw.rect(sheet, TILE_INNER, art_rect)
            frame_col = FRAME_AFTER if is_after else FRAME
            pygame.draw.rect(sheet, frame_col, art_rect, FRAME_W)

            img = pygame.image.load(
                os.path.join(ROOT, spec["file"])
            ).convert_alpha()
            bbox = measure_bbox(img, spec)
            crop = img.subsurface(bbox).copy()

            inner = TILE - FRAME_W * 2 - 18
            fitted = fit_inside(crop, inner)
            fx = art_rect.centerx - fitted.get_width() // 2
            fy = art_rect.centery - fitted.get_height() // 2
            sheet.blit(fitted, (fx, fy))

            # Post-check: the placed figure must sit inside the framed inner box
            # with a small safety inset. Count any fitted figure that touches the
            # frame.
            inset = FRAME_W + 4
            if (
                fx < art_rect.x + inset
                or fy < art_rect.y + inset
                or fx + fitted.get_width() > art_rect.right - inset
                or fy + fitted.get_height() > art_rect.bottom - inset
            ):
                clip_violations += 1
                print(
                    "CLIP:",
                    row["name"],
                    "AFTER" if is_after else "BEFORE",
                    fitted.get_size(),
                    "in",
                    art_rect,
                )

    # Bottom caption strip.
    cap = f_cap.render(
        "final: per-character themed skulls (palm + crown), 6 distinct each, gem-hue accents; "
        "#1 bone-jewel #2 war-marked #3 gilded #4 ascetic #5 frost-cracked.",
        True,
        CAP_COL,
    )
    sheet.blit(
        cap,
        (sheet_w // 2 - cap.get_width() // 2,
         sheet_h - MARGIN - CAP_H + (CAP_H - cap.get_height()) // 2),
    )

    out = os.path.join(HERE, "before_after.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())
    print("clip_violations:", clip_violations)


if __name__ == "__main__":
    main()
