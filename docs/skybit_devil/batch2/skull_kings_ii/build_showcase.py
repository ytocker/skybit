"""Assemble the KING SKULL II second-court showcase.

Compositing-only: each king's review sheet carries its hero in a left-hand
"Creature - hero" column alongside a pillar strip + a right-side proof panel.
This MEASURES that hero's bounding box by scanning only the hero column (so the
pillar strip and proof panel never leak in), crops it with a margin, and
fit-inside-scales every figure to one matched tile so the whole brood reads at a
single size with nothing clipped.

The split that defines this court — five MANDATORY-CRADLE kings (a skull cupped
in arms/structure) versus five DISCRETION kings (no cradle) — is made visible by
grouping them into two labeled rows of five, each tile carrying a [CRADLE] /
[no cradle] tag. The two ancestors the brood descends from (shipped Citipati,
evolved Koschei) sit apart in a warm-framed LINEAGE band above the court so a
reviewer reads the ten kings against the established lineage.

Crop windows are measured, never assumed: tall plumes, gear-spires, antler
crowns and floor-length robes are exactly the extremities a fixed crop clips, so
each window comes from this sheet's actual hero bbox and is verified by an
edge-scan that fails if any figure touches its tile border.
"""

import os

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# Neutral mid-grey keeps the coloured kings honest regardless of each sheet's own
# day/night backdrop. It also matches the sheets' own flat canvas grey, which is
# what the hero-bbox scan keys off of.
BG = (96, 98, 104)
FRAME = (150, 152, 160)
FRAME_CRADLE = (210, 180, 120)   # warm tag for the mandatory-cradle row
FRAME_REF = (228, 196, 120)      # warm ochre sets the lineage tiles apart
TILE_INNER = (118, 120, 128)
INK = (28, 28, 32)
TITLE_COL = (240, 240, 236)
SUB_COL = (206, 208, 214)
NAME_COL = (244, 244, 240)
TAG_CRADLE_BG = (236, 198, 120)
TAG_PLAIN_BG = (150, 152, 160)
TAG_REF_BG = (250, 214, 130)
ROWLBL_COL = (224, 224, 220)

# The sheets share a flat-grey canvas. The hero lives in a left column; to its
# right are a centered pillar strip and a proof panel that must be excluded from
# the bbox scan. These bounds carve out just the hero column (below the title
# band, above the caption text).
HERO_COL_RIGHT = 360    # hero column ends well left of the pillar strip (~475)
HERO_TOP = 80           # below the title band
HERO_BOTTOM = 540       # above the "Creature - hero" caption text

LINEAGE = [
    {
        "file": "docs/skybit_devil/batch2/jiangshi_epic/citipati/round_2.png",
        "name": "Citipati",
        "tag": "the original respected",
    },
    {
        "file": "docs/skybit_devil/batch2/citipati_versions/koschei/round_2.png",
        "name": "Koschei",
        "tag": "the one evolved",
    },
]

CRADLE = [
    {"file": "jade_empress_dowager/round_4.png",      "name": "Jade Empress Dowager"},
    {"file": "sunfire_solar_khan/round_5.png",        "name": "Sunfire Solar-Khan"},
    {"file": "starlit_night_shepherd/round_3.png",    "name": "Starlit Night-Shepherd"},
    {"file": "opal_pearl_diver_queen/round_6.png",    "name": "Opal Pearl-Diver Queen"},
    {"file": "lapis_navigator_king/round_2.png",      "name": "Lapis Navigator-King"},
]

DISCRETION = [
    {"file": "garnet_cardinal_inquisitor/round_4.png", "name": "Garnet Cardinal-Inquisitor"},
    {"file": "ember_ash_walker/round_5.png",           "name": "Ember Ash-Walker"},
    {"file": "malachite_magistrate/round_4.png",       "name": "Malachite Magistrate"},
    {"file": "oxblood_automaton_king/round_6.png",      "name": "Oxblood Automaton-King"},
    {"file": "bismuth_prism_architect/round_3.png",     "name": "Bismuth Prism-Architect"},
]

TILE = 232          # inner art square per tile
PAD = 22            # gap between tiles
MARGIN = 36         # outer margin
CAP_H = 50          # caption band under each tile art
TITLE_H = 84
ROWLBL_H = 30
BAND_GAP = 30       # gap between the lineage band and the court
FRAME_W = 4
BG_MARGIN = 16      # background margin added around each measured hero bbox


def hero_crop(img):
    """Measure the hero figure's bbox inside the left hero column and return a
    cropped surface with a uniform background margin so nothing clips."""
    w, h = img.get_size()
    right = min(HERO_COL_RIGHT, w)
    bottom = min(HERO_BOTTOM, h)
    minx, miny, maxx, maxy = right, bottom, 0, 0
    found = False
    # Coarse step keeps the per-sheet scan cheap; the BG_MARGIN absorbs the step.
    step = 2
    for y in range(HERO_TOP, bottom, step):
        for x in range(0, right, step):
            r, g, b, a = img.get_at((x, y))
            if a == 0:
                continue
            # Anything that departs from the flat canvas grey is figure ink/glow.
            if abs(r - BG[0]) + abs(g - BG[1]) + abs(b - BG[2]) > 24:
                found = True
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x
                if y < miny:
                    miny = y
                if y > maxy:
                    maxy = y
    if not found:
        raise RuntimeError("no hero pixels found in column")
    minx = max(0, minx - BG_MARGIN)
    miny = max(0, miny - BG_MARGIN)
    maxx = min(w, maxx + BG_MARGIN)
    maxy = min(h, maxy + BG_MARGIN)
    return img.subsurface(pygame.Rect(minx, miny, maxx - minx, maxy - miny)).copy()


def fit_inside(surf, box):
    """Scale a surface to sit whole inside a box, preserving aspect."""
    sw, sh = surf.get_size()
    s = min(box / sw, box / sh)
    return pygame.transform.smoothscale(surf, (max(1, int(sw * s)), max(1, int(sh * s))))


def crop_clip_violation(crop):
    """True if figure ink touches the measured crop's own border — i.e. the crop
    window cut the figure off before its BG_MARGIN. Scanned on the crop itself
    (pre-scale), since fit_inside legitimately lets one axis reach the tile box.
    A figure pixel is anything departing from the flat canvas grey."""
    w, h = crop.get_size()

    def figure(x, y):
        r, g, b, a = crop.get_at((x, y))
        if a == 0:
            return False
        return abs(r - BG[0]) + abs(g - BG[1]) + abs(b - BG[2]) > 24

    for x in range(w):
        if figure(x, 0) or figure(x, h - 1):
            return True
    for y in range(h):
        if figure(0, y) or figure(w - 1, y):
            return True
    return False


def main():
    pygame.init()
    pygame.font.init()
    # A display mode is required before convert_alpha() even under the dummy
    # video driver used for headless rendering.
    pygame.display.set_mode((1, 1))

    cell_w = TILE
    cell_h = TILE + CAP_H
    inner = TILE - FRAME_W * 2 - 16

    # Layout: a 2-tile lineage band, then two rows of five. Row width is driven
    # by the wider court rows.
    court_cols = 5
    court_row_w = court_cols * cell_w + (court_cols - 1) * PAD

    sheet_w = MARGIN * 2 + court_row_w
    sheet_h = (
        MARGIN + TITLE_H
        + ROWLBL_H + cell_h            # lineage band
        + BAND_GAP
        + ROWLBL_H + cell_h            # cradle row
        + PAD + ROWLBL_H + cell_h      # discretion row
        + MARGIN
    )

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(BG)

    f_title = pygame.font.SysFont("dejavusans", 32, bold=True)
    f_sub = pygame.font.SysFont("dejavusans", 16)
    f_name = pygame.font.Font(os.path.join(ROOT, "game/assets/LiberationSans-Bold.ttf"), 17)
    f_rowlbl = pygame.font.SysFont("dejavusans", 17, bold=True)
    f_tag = pygame.font.SysFont("dejavusans", 11, bold=True)

    title = f_title.render(
        "KING SKULL II — a second royal court of ten skeleton-kings", True, TITLE_COL
    )
    sheet.blit(title, (MARGIN, MARGIN))
    sub = f_sub.render(
        "five MANDATORY-CRADLE kings + five DISCRETION kings · lineage set apart above",
        True, SUB_COL,
    )
    sheet.blit(sub, (MARGIN, MARGIN + 44))

    violations = []

    def draw_tile(x, top, t, kind):
        """kind in {'lineage','cradle','plain'} picks frame + tag styling."""
        art_rect = pygame.Rect(x, top, TILE, TILE)
        pygame.draw.rect(sheet, TILE_INNER, art_rect)
        if kind == "lineage":
            frame_col = FRAME_REF
        elif kind == "cradle":
            frame_col = FRAME_CRADLE
        else:
            frame_col = FRAME
        pygame.draw.rect(sheet, frame_col, art_rect, FRAME_W)

        path = t["file"]
        if not os.path.isabs(path) and path.startswith("docs/"):
            full = os.path.join(ROOT, path)
        else:
            full = os.path.join(HERE, path)
        img = pygame.image.load(full).convert_alpha()
        crop = hero_crop(img)
        if crop_clip_violation(crop):
            violations.append(t["name"])
        fitted = fit_inside(crop, inner)

        fx = art_rect.centerx - fitted.get_width() // 2
        fy = art_rect.centery - fitted.get_height() // 2
        sheet.blit(fitted, (fx, fy))

        # Corner tag.
        if kind == "lineage":
            tag_txt, tag_bg, tag_fg = "LINEAGE", TAG_REF_BG, INK
        elif kind == "cradle":
            tag_txt, tag_bg, tag_fg = "CRADLE", TAG_CRADLE_BG, INK
        else:
            tag_txt, tag_bg, tag_fg = "no cradle", TAG_PLAIN_BG, INK
        tag = f_tag.render(tag_txt, True, tag_fg)
        tp = 5
        tag_box = pygame.Rect(
            art_rect.x + FRAME_W + 4, art_rect.y + FRAME_W + 4,
            tag.get_width() + tp * 2, tag.get_height() + 4,
        )
        pygame.draw.rect(sheet, tag_bg, tag_box, border_radius=3)
        sheet.blit(tag, (tag_box.x + tp, tag_box.y + 2))

        # Name caption.
        cap_y = top + TILE + 8
        name = t["name"]
        nsurf = f_name.render(name, True, NAME_COL)
        if nsurf.get_width() > TILE - 6:
            nsurf = pygame.transform.smoothscale(
                nsurf,
                (TILE - 6, int(nsurf.get_height() * (TILE - 6) / nsurf.get_width())),
            )
        sheet.blit(nsurf, (art_rect.centerx - nsurf.get_width() // 2, cap_y))

    def row_label(text, x, y, col):
        lbl = f_rowlbl.render(text, True, col)
        sheet.blit(lbl, (x, y + (ROWLBL_H - lbl.get_height()) // 2))

    y = MARGIN + TITLE_H

    # Lineage band (2 tiles, centered under the title block, warm framed).
    row_label("LINEAGE — the brood's ancestors", MARGIN, y, FRAME_REF)
    band_top = y + ROWLBL_H
    lin_w = len(LINEAGE) * cell_w + (len(LINEAGE) - 1) * PAD
    lin_x0 = MARGIN + (court_row_w - lin_w) // 2
    for i, t in enumerate(LINEAGE):
        draw_tile(lin_x0 + i * (cell_w + PAD), band_top, t, "lineage")
    # Divider line under the lineage band.
    div_y = band_top + cell_h + BAND_GAP // 2
    pygame.draw.line(sheet, FRAME_REF, (MARGIN, div_y), (sheet_w - MARGIN, div_y), 2)

    y = band_top + cell_h + BAND_GAP

    # Cradle row (5 tiles).
    row_label("MANDATORY-CRADLE — a skull cupped in arms / structure", MARGIN, y, FRAME_CRADLE)
    crad_top = y + ROWLBL_H
    for i, t in enumerate(CRADLE):
        draw_tile(MARGIN + i * (cell_w + PAD), crad_top, t, "cradle")

    y = crad_top + cell_h + PAD

    # Discretion row (5 tiles).
    row_label("DISCRETION — no cradle", MARGIN, y, FRAME)
    disc_top = y + ROWLBL_H
    for i, t in enumerate(DISCRETION):
        draw_tile(MARGIN + i * (cell_w + PAD), disc_top, t, "plain")

    out = os.path.join(HERE, "showcase.png")
    pygame.image.save(sheet, out)
    size = os.path.getsize(out)
    print("wrote", out, sheet.get_size(), f"{size} bytes")
    print("edge-clip violations:", len(violations), violations)


if __name__ == "__main__":
    main()
