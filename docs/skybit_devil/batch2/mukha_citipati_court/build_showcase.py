"""Assemble the Mukha-Citipati COURT brood showcase.

Compositing-only: the two source bone-deities (Mukha-Devi + Citipati) lead the
sheet set apart as smaller, ochre-framed REFERENCES, then the five matured
"sister" deities run in a matched-scale row. Each sister borrows ONE of the two
references' body bases (Citipati: dancing/standing skeleton-lord; Mukha: low-origin
six-arm fan), so every tile is captioned with its body base to keep the relaxed-
distinctness brood honest against its two parents.

Every figure is measured-cropped by an edge scan so the row sits on a common
baseline at one tile size — no per-sheet hand-tuned window. The scan handles two
backdrop kinds the source files actually use:
  * transparent heroes (alpha == 0 is background) — vajra_rakta, naga_kapali, ratna_padmini
  * opaque-gradient heroes (per-row background sampled from the edge columns, so the
    smooth day/night gradient never counts as ink) — asthi_dakini, mundamala_mata
A `skip_top` band excludes a hero sheet's printed title text from the figure bbox
(mundamala_mata carries a name strip). The two references are full multi-panel
sheets, so their scan is confined to the hero-panel region (left of the GAP/pillar
columns, below the title band) against that panel's flat (96,92,100) fill.

A measured margin pads each bbox; after fit-inside scaling, a post-check re-runs the
content test on the placed tile's inner box and reports clip violations (target 0).
"""

import os

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# Neutral mid-grey keeps the rose/ivory/cinnabar court honest regardless of each
# source's own day/night backdrop.
BG = (96, 98, 104)
FRAME = (150, 152, 160)
FRAME_REF = (228, 196, 120)  # warm ochre sets the references apart
TILE_INNER = (118, 120, 128)
INK = (28, 28, 32)
TITLE_COL = (240, 240, 236)
NAME_COL = (244, 244, 240)
FACET_COL = (190, 192, 200)
BASE_COL = (236, 206, 132)   # body-base tag echoes the reference frame
REF_TAG = (250, 214, 130)

# Reference hero panels live inside a full sheet; scan only the left hero region
# (clear of the title band, the centre GAP/pillar strip, and the caption text).
# bg is that panel's flat fill; opaque gradient sisters are scanned via edge-sampling.
REF_PANEL_BG = (96, 92, 100)

TILES = [
    {
        "file": "docs/skybit_devil/batch2/citipati_versions/mukha_devi/round_2.png",
        "name": "Mukha-Devi",
        "facet": "source bone-mother (shipped)",
        "base": "MUKHA base",
        "reference": True,
        "mode": "panel",
        "scan": (20, 400, 150, 470),  # x0,x1,y0,y1 hero-panel window
    },
    {
        "file": "docs/skybit_devil/batch2/jiangshi_epic/citipati/round_2.png",
        "name": "Citipati",
        "facet": "source skeleton-lord (shipped)",
        "base": "CITIPATI base",
        "reference": True,
        "mode": "panel",
        "scan": (20, 400, 150, 520),
    },
    {
        "file": "docs/skybit_devil/batch2/mukha_citipati_court/asthi_dakini/round_3_hero.png",
        "name": "Asthi-Dakini",
        "facet": "halo-eye bead-string dancer",
        "base": "CITIPATI base",
        "mode": "gradient",
    },
    {
        "file": "docs/skybit_devil/batch2/mukha_citipati_court/vajra_rakta/round_2_hero.png",
        "name": "Vajra-Rakta",
        "facet": "cinnabar-skirt thunder mother",
        "base": "CITIPATI base",
        "mode": "alpha",
    },
    {
        "file": "docs/skybit_devil/batch2/mukha_citipati_court/naga_kapali/round_3_hero.png",
        "name": "Naga-Kapali",
        "facet": "jade-serpent sash striding lord",
        "base": "CITIPATI base",
        "mode": "alpha",
    },
    {
        "file": "docs/skybit_devil/batch2/mukha_citipati_court/mundamala_mata/round_3_hero.png",
        "name": "Mundamala-Mata",
        "facet": "severed-head garland mother",
        "base": "MUKHA base",
        "mode": "gradient",
        "skip_top": 120,  # excludes the printed name strip from the figure bbox
    },
    {
        "file": "docs/skybit_devil/batch2/mukha_citipati_court/ratna_padmini/round_2_hero.png",
        "name": "Ratna-Padmini",
        "facet": "radiant sun-spoke jewel throne",
        "base": "MUKHA base",
        "mode": "alpha",
    },
]

TILE = 248          # inner art square per tile
PAD = 26            # gap between tiles
REF_DIV = 30        # extra gap separating the references from the sisters
MARGIN = 36         # outer margin
CAP_H = 70          # caption band under each tile art
TITLE_H = 72
FRAME_W = 4
MARGIN_PX = 16      # background margin baked around each measured bbox

# References sit smaller than the matured sisters so they read as set-apart sources.
REF_SCALE = 0.82


def _content_mask(img, t):
    """Return (xa, xb, ya, yb) scan window and a predicate(x, y) -> bool is-ink.

    Background varies by source: transparent alpha, an opaque vertical gradient
    (sampled per row from the edge columns), or a reference panel's flat fill.
    """
    w, h = img.get_size()
    mode = t["mode"]

    if mode == "alpha":
        xa, xb, ya, yb = 0, w, 0, h

        def is_ink(x, y):
            return img.get_at((x, y))[3] > 24

        return xa, xb, ya, yb, is_ink

    if mode == "panel":
        xa, xb, ya, yb = t["scan"]
        bg = REF_PANEL_BG

        def is_ink(x, y):
            c = img.get_at((x, y))[:3]
            return abs(c[0] - bg[0]) + abs(c[1] - bg[1]) + abs(c[2] - bg[2]) >= 24

        return xa, xb, ya, yb, is_ink

    # gradient: per-row background = mean of the two edge columns; ink deviates from it.
    skip = t.get("skip_top", 0)
    xa, xb, ya, yb = 0, w, skip, h
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

    return xa, xb, ya, yb, is_ink


def measure_bbox(img, t):
    """Edge-scan the figure's ink bbox; return a Rect padded by MARGIN_PX (clamped)."""
    w, h = img.get_size()
    xa, xb, ya, yb, is_ink = _content_mask(img, t)
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

    n = len(TILES)
    n_ref = sum(1 for t in TILES if t.get("reference"))
    cell_w = TILE
    cell_h = TILE + CAP_H

    # References get an extra divider gap before the first sister.
    sheet_w = MARGIN * 2 + n * cell_w + (n - 1) * PAD + REF_DIV
    sheet_h = MARGIN + TITLE_H + cell_h + MARGIN

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(BG)

    f_title = pygame.font.SysFont("dejavusans", 30, bold=True)
    f_name = pygame.font.Font(
        os.path.join(ROOT, "game/assets/LiberationSans-Bold.ttf"), 19
    )
    f_facet = pygame.font.SysFont("dejavusans", 14)
    f_base = pygame.font.SysFont("dejavusans", 13, bold=True)
    f_tag = pygame.font.SysFont("dejavusans", 12, bold=True)

    title = f_title.render(
        "Mukha-Citipati COURT — two sources + five sister bone-deities",
        True,
        TITLE_COL,
    )
    sheet.blit(title, (MARGIN, MARGIN + (TITLE_H - title.get_height()) // 2 - 6))

    top = MARGIN + TITLE_H
    clip_violations = 0

    x = MARGIN
    for i, t in enumerate(TILES):
        is_ref = t.get("reference", False)
        # Open the divider gap once, right after the last reference.
        if not is_ref and i == n_ref:
            x += REF_DIV

        art_rect = pygame.Rect(x, top, cell_w, TILE)

        pygame.draw.rect(sheet, TILE_INNER, art_rect)
        frame_col = FRAME_REF if is_ref else FRAME
        pygame.draw.rect(sheet, frame_col, art_rect, FRAME_W)

        img = pygame.image.load(os.path.join(ROOT, t["file"])).convert_alpha()
        bbox = measure_bbox(img, t)
        crop = img.subsurface(bbox).copy()

        # References sit slightly smaller so they read as set-apart sources.
        inner = TILE - FRAME_W * 2 - 18
        if is_ref:
            inner = int(inner * REF_SCALE)
        fitted = fit_inside(crop, inner)
        fx = art_rect.centerx - fitted.get_width() // 2
        fy = art_rect.centery - fitted.get_height() // 2
        sheet.blit(fitted, (fx, fy))

        # Post-check: the placed figure must sit inside the framed inner box with a
        # small safety inset. Count any fitted figure that would touch the frame.
        inset = FRAME_W + 4
        if (
            fx < art_rect.x + inset
            or fy < art_rect.y + inset
            or fx + fitted.get_width() > art_rect.right - inset
            or fy + fitted.get_height() > art_rect.bottom - inset
        ):
            clip_violations += 1
            print("CLIP:", t["name"], fitted.get_size(), "in", art_rect)

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

        # Caption band: name, body base, lead facet.
        cap_y = top + TILE + 8
        name = f_name.render(t["name"], True, NAME_COL)
        sheet.blit(name, (art_rect.centerx - name.get_width() // 2, cap_y))
        base = f_base.render(t["base"], True, BASE_COL)
        sheet.blit(base, (art_rect.centerx - base.get_width() // 2, cap_y + 24))
        facet = f_facet.render(t["facet"], True, FACET_COL)
        sheet.blit(facet, (art_rect.centerx - facet.get_width() // 2, cap_y + 44))

        # Divider line after the last reference.
        if is_ref and i == n_ref - 1:
            dx = x + cell_w + (PAD + REF_DIV) // 2
            pygame.draw.line(
                sheet, FRAME_REF, (dx, top - 6), (dx, top + cell_h + 6), 2
            )

        x += cell_w + PAD

    out = os.path.join(HERE, "showcase.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())
    print("clip_violations:", clip_violations)


if __name__ == "__main__":
    main()
