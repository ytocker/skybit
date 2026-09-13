"""POISON VIAL — Round 6 high-resolution A vs B comparison.

Uses the Round-5 variant draw functions (A=CLASSIC, B=CARTOON), but
renders them at much larger native sizes (96 px and 192 px) so the
user can see the skull detail clearly when choosing between A and B.
"""
from __future__ import annotations

import os
import sys
import math
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

pygame.init()
pygame.display.set_mode((1, 1))

from render_death_trap_round_5_vial import VARIANTS, DAWN_TEAL


INK       = (235, 240, 250)
DIM       = (150, 158, 178)
HOT       = (255, 120, 130)
PANEL_BG  = (24, 28, 42)
GRID      = (54, 62, 86)

# Native render is 48; bigger views are nearest-neighbor upscales so each
# pixel stays crisp at any size (true pixel-art comparison)
SIZES = [48, 192, 384]
ZOOM  = [1, 4, 8]
SIZE_LABELS = ["in-world (48 px)", "4× zoom", "8× zoom"]

GUTTER  = 18
SWATCH_PAD = 24
TITLE_H = 90

# A and B only
DUO = [v for v in VARIANTS if v[0] in ("A", "B")]


def _swatch_for(size_native: int) -> int:
    """Background swatch diameter for a given native render size."""
    return size_native + SWATCH_PAD * 2


COL_WIDTHS = [_swatch_for(s) + 16 for s in SIZES]
ROW_HEIGHT = max(COL_WIDTHS) + 60  # one variant per row, room for labels

LABEL_COL_W = 220
SHEET_W = LABEL_COL_W + sum(COL_WIDTHS) + GUTTER * (len(SIZES) + 2)
SHEET_H = TITLE_H + ROW_HEIGHT * len(DUO) + GUTTER * (len(DUO) + 1)


def _panel_bg(surf, rect):
    pygame.draw.rect(surf, PANEL_BG, rect, border_radius=12)
    pygame.draw.rect(surf, GRID, rect, width=1, border_radius=12)


def _swatch_circle(d: int) -> pygame.Surface:
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(s, DAWN_TEAL, (d // 2, d // 2), d // 2)
    pygame.draw.circle(s, (28, 32, 50), (d // 2, d // 2), d // 2, 2)
    return s


def build_sheet() -> pygame.Surface:
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill(DAWN_TEAL)

    font_title = pygame.font.SysFont("dejavusansmono", 26, bold=True)
    font_sub   = pygame.font.SysFont("dejavusans", 14)
    font_var   = pygame.font.SysFont("dejavusans", 22, bold=True)
    font_blurb = pygame.font.SysFont("dejavusans", 13)
    font_size  = pygame.font.SysFont("dejavusans", 12, bold=True)
    font_xs    = pygame.font.SysFont("dejavusans", 10)

    sheet.blit(font_title.render(
        "POISON VIAL  —  A vs B head-to-head (high-res)",
        True, INK), (GUTTER, 16))
    sheet.blit(font_sub.render(
        "Same Round-5 contained-glyph treatment. Same pulse. "
        "Three render scales so the skull detail is unambiguous.",
        True, DIM), (GUTTER, 50))

    base_pulse = {"A": 0.5, "B": 1.1}

    for ri, (tag, name, blurb, fn) in enumerate(DUO):
        row_top = TITLE_H + ri * (ROW_HEIGHT + GUTTER)
        row_rect = pygame.Rect(GUTTER, row_top,
                               SHEET_W - GUTTER * 2, ROW_HEIGHT)
        _panel_bg(sheet, row_rect)

        # left text column
        tag_color = HOT if tag in ("A", "B") else INK
        sheet.blit(font_var.render(f"{tag}.  {name}", True, tag_color),
                   (row_rect.left + 18, row_rect.top + 18))
        sheet.blit(font_blurb.render(blurb, True, DIM),
                   (row_rect.left + 18, row_rect.top + 48))

        # short why-pick notes
        if tag == "A":
            notes = [
                "Universal poison pictogram",
                "Square jaw + no nose = stark",
                "Cleanest read at any scale",
            ]
        else:
            notes = [
                "Rounder, friendlier silhouette",
                "Dot-nose + bigger sockets",
                "Skybit-leaning charm",
            ]
        for ni, line in enumerate(notes):
            sheet.blit(font_blurb.render(f"• {line}", True, INK),
                       (row_rect.left + 22, row_rect.top + 84 + ni * 18))

        # render columns
        col_x = row_rect.left + LABEL_COL_W + GUTTER
        base_icon = fn(48, base_pulse[tag])
        for ci, (display_size, zoom, lbl) in enumerate(
                zip(SIZES, ZOOM, SIZE_LABELS)):
            if zoom == 1:
                icon = base_icon
            else:
                icon = pygame.transform.scale(
                    base_icon, (48 * zoom, 48 * zoom))
            bob = int(math.sin(base_pulse[tag] * 1.0) * 2 * zoom)
            d = _swatch_for(display_size)
            swatch = _swatch_circle(d)
            sx = col_x + (COL_WIDTHS[ci] - d) // 2
            sy = row_rect.top + 28
            sheet.blit(swatch, (sx, sy))
            ix = sx + (d - icon.get_width()) // 2
            iy = sy + (d - icon.get_height()) // 2 + bob
            sheet.blit(icon, (ix, iy))

            # size label under swatch
            lbl_surf = font_size.render(lbl, True, INK)
            sheet.blit(lbl_surf,
                       (sx + (d - lbl_surf.get_width()) // 2,
                        sy + d + 8))

            col_x += COL_WIDTHS[ci] + GUTTER

    sheet.blit(font_xs.render(
        "Round-6 hi-res comparison  |  variants drawn by render_death_trap_round_5_vial.py  "
        "|  same supersample pipeline at every scale",
        True, DIM), (GUTTER, SHEET_H - 18))

    return sheet


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR), "docs", "death_pickup")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_6_AvB_hires.png")
    sheet = build_sheet()
    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  size={sheet.get_size()}")


if __name__ == "__main__":
    main()
