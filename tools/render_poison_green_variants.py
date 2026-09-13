"""Poison vial — brighter green variants (W1..W5).

Builds on the user's V4/V5 picks from the prior round but goes lighter
across the WHOLE bottle — glass body, liquid, meniscus AND the
silhouette outline (BLACK_DOME) so the vial doesn't carry a heavy
near-black border that pulls the whole pickup back to "dark green".

Output: docs/screenshots/icon_sizes/poison_green_variants.png
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

pygame.init()
pygame.display.set_mode((1, 1))

from game import poison_vial, parrot


# Each entry: label, GREEN_GLASS (above-liquid body), GREEN_LO (the
# liquid itself — what shows behind/below the skull), GREEN_TOX
# (meniscus line), DARK (bottle silhouette outline, currently
# BLACK_DOME = (10,10,18)).  W1 ≈ prior V4/V5 brightness + lighter
# outline; W5 is the brightest pass — closer to lime than to forest.
VARIANTS = (
    ("CURRENT",
        ( 35,  90,  50), ( 40, 100,  50), (120, 200,  90),
        ( 10,  10,  18)),
    ("W1",
        (145, 210, 125), (175, 230, 140), (200, 240, 155),
        ( 32,  48,  34)),
    ("W2",
        (160, 220, 135), (190, 235, 150), (215, 245, 170),
        ( 42,  62,  44)),
    ("W3",
        (175, 230, 145), (205, 240, 160), (225, 250, 180),
        ( 55,  80,  56)),
    ("W4",
        (195, 240, 160), (220, 245, 175), (235, 252, 195),
        ( 70, 100,  72)),
    ("W5",
        (215, 250, 180), (235, 252, 195), (245, 255, 210),
        ( 90, 125,  92)),
)


CARD_BG = (24, 26, 34)
LABEL   = (235, 235, 240)
SUB     = (165, 173, 185)

CELL_W = 200
CELL_H = 160
PAD    = 14
HEADER_H = 80


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _draw_vial(surf, cx, cy, glass_rgb, liquid_rgb, tox_rgb, dark_rgb):
    """Render the vial with FOUR palette slots swapped for this
    render only. Restores the originals + cache after."""
    prev = {
        "GREEN_GLASS": poison_vial.GREEN_GLASS,
        "GREEN_LO":    poison_vial.GREEN_LO,
        "GREEN_TOX":   poison_vial.GREEN_TOX,
        "BLACK_DOME":  poison_vial.BLACK_DOME,
    }
    prev_cache = getattr(poison_vial, "_VIAL_CACHE", None)
    poison_vial.GREEN_GLASS = glass_rgb
    poison_vial.GREEN_LO    = liquid_rgb
    poison_vial.GREEN_TOX   = tox_rgb
    poison_vial.BLACK_DOME  = dark_rgb
    poison_vial._VIAL_CACHE = None
    poison_vial.draw(surf, int(cx), int(cy), 0.0)
    for k, v in prev.items():
        setattr(poison_vial, k, v)
    poison_vial._VIAL_CACHE = prev_cache


def _build_cell(glass_rgb, liquid_rgb, tox_rgb, dark_rgb):
    cell = pygame.Surface((CELL_W, CELL_H))
    cell.fill((32, 34, 42))
    pip = parrot.get_parrot(0, 0.0)
    cell.blit(pip, pip.get_rect(center=(46, CELL_H // 2)))
    _draw_vial(cell, CELL_W - 50, CELL_H // 2,
               glass_rgb, liquid_rgb, tox_rgb, dark_rgb)
    pygame.draw.rect(cell, (45, 50, 62), cell.get_rect(), 1)
    return cell


def _fmt(rgb):
    return f"({rgb[0]:>3}, {rgb[1]:>3}, {rgb[2]:>3})"


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "poison_green_variants.png")

    n = len(VARIANTS)
    sheet_w = PAD * 2 + n * (CELL_W + PAD) - PAD
    sheet_h = HEADER_H + CELL_H + 108
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(20, bold=True).render(
        "POISON vial — brighter palette (W1..W5)",
        True, LABEL)
    sheet.blit(title, (PAD, 14))
    sub = _font(13).render(
        "Left = current; W1..W5 lift glass + liquid + meniscus AND "
        "lighten the dark silhouette outline so the whole bottle reads "
        "brighter.",
        True, SUB)
    sheet.blit(sub, (PAD, 38))

    for i, (code, glass, lo, tox, dark) in enumerate(VARIANTS):
        x = PAD + i * (CELL_W + PAD)
        y = HEADER_H
        sheet.blit(_build_cell(glass, lo, tox, dark), (x, y))
        cap_font = _font(13, bold=True)
        sub_font = _font(11)
        cap = cap_font.render(code, True, LABEL)
        sheet.blit(cap, (x + (CELL_W - cap.get_width()) // 2,
                         y + CELL_H + 6))
        for ln, (lbl, val) in enumerate((
                ("glass",   glass),
                ("liquid",  lo),
                ("tox",     tox),
                ("outline", dark))):
            text = f"{lbl}  {_fmt(val)}"
            s = sub_font.render(text, True, SUB)
            sheet.blit(s, (x + (CELL_W - s.get_width()) // 2,
                           y + CELL_H + 24 + ln * 14))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
