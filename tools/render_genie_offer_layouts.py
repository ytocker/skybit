"""Genie offer-positioning comparison — all six candidate layouts.

Each layout (A..F) is shown as a WIDE world-view schematic: a sky
strip wide enough to include the off-screen spawn positions, Pip at
his live BIRD_X, the 3 offers (KNIGHT / POISON / SKATEBOARD) drawn at
their true world x/y, and a marker for the visible screen-right edge
(x=360) past which offers scroll in. Offers to the RIGHT of that line
are off-screen at spawn and slide left toward Pip.

Output: docs/screenshots/icon_sizes/genie_offer_layouts.png
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

from game.config import W, H
from game import parrot, biome
from game.entities import PowerUp


BX, BY = 90, 300            # Pip's fixed x, a representative mid-screen y
WORLD_W = 780               # wide enough to hold x+640 + margin
WORLD_H = 300
SCREEN_EDGE = W             # x=360: right edge of the live play screen


def _layout(opt, bx, by):
    if opt == "A":
        xs = (bx + 220, bx + 320, bx + 420); ys = (by - 15, by, by + 15)
    elif opt == "B":
        xs = (bx + 250, bx + 250, bx + 250); ys = (by - 60, by, by + 60)
    elif opt == "C":
        xs = (bx + 240, bx + 440, bx + 640); ys = (by - 15, by, by + 15)
    elif opt == "D":
        xs = (bx + 500, bx + 500, bx + 500); ys = (by - 80, by, by + 80)
    elif opt == "E":
        xs = (bx + 360, bx + 480, bx + 600); ys = (by + 60, by, by - 60)
    elif opt == "F":
        xs = (bx + 600, bx + 600, bx + 600); ys = (by - 30, by, by + 30)
    kinds = ("knight", "poison", "skateboard")
    return list(zip(kinds, xs, ys))


DESCRIPTIONS = {
    "A": "Wide row, CLOSE  (x+220/320/420 @ Pip Y)",
    "B": "Tight column, CLOSE  (x+250, Y +/-60)",
    "C": "Wide row, FAR  (x+240/440/640 @ Pip Y)",
    "D": "Far column  (x+500, Y +/-80)   <- AI pick",
    "E": "Far diagonal fan  (x+360..600)",
    "F": "Screen-right row  (x+600, Y +/-30)",
}
OPTIONS = ("A", "B", "C", "D", "E", "F")

CARD_BG = (24, 26, 34)
LABEL   = (235, 235, 240)
SUB     = (165, 173, 185)
PICK    = (140, 230, 150)
KIND_COL = {
    "knight":     (120, 200, 255),
    "poison":     (180, 230, 130),
    "skateboard": (255, 170, 120),
}

PAD     = 16
HEADER  = 60
CAP_H   = 40
ROW_GAP = 18


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _sky(w, h):
    pal = biome.palette_for_phase(0.46)
    top = pal.get("sky_top", (110, 165, 220))
    bot = pal.get("sky_bot", (220, 200, 200))
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        s.fill((int(top[0] + (bot[0] - top[0]) * t),
                int(top[1] + (bot[1] - top[1]) * t),
                int(top[2] + (bot[2] - top[2]) * t)),
               (0, y, w, 1))
    return s


def _world_view(opt):
    surf = _sky(WORLD_W, WORLD_H)
    # Shade the off-screen region (x > SCREEN_EDGE) so the player can
    # see which offers spawn outside the visible play area.
    shade = pygame.Surface((WORLD_W - SCREEN_EDGE, WORLD_H),
                           pygame.SRCALPHA)
    shade.fill((0, 0, 0, 70))
    surf.blit(shade, (SCREEN_EDGE, 0))
    pygame.draw.line(surf, (255, 255, 255), (SCREEN_EDGE, 0),
                     (SCREEN_EDGE, WORLD_H), 2)
    edge_lbl = _font(11, bold=True).render("screen edge", True,
                                           (255, 255, 255))
    surf.blit(edge_lbl, (SCREEN_EDGE + 4, 4))

    # Pip
    pip = parrot.get_parrot(0, 0.0)
    surf.blit(pip, pip.get_rect(center=(BX, BY - 90)))  # shift up into view

    # Offers — draw at world x, y shifted by the same -90 as Pip.
    for kind, x, y in _layout(opt, BX, BY):
        p = PowerUp(x, y - 90, kind=kind)
        p.pulse = 0.0
        p.draw(surf)
        dot = KIND_COL[kind]
        tag = _font(10, bold=True).render(kind.upper(), True, dot)
        surf.blit(tag, (x - tag.get_width() // 2, y - 90 + 40))
    return surf


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "genie_offer_layouts.png")

    cell_w = WORLD_W
    cell_h = WORLD_H
    cols = 2
    rows = 3

    sheet_w = PAD * 2 + cols * (cell_w + PAD) - PAD
    sheet_h = HEADER + rows * (cell_h + CAP_H + ROW_GAP) - ROW_GAP + PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(22, bold=True).render(
        "GENIE offer layouts — where the 3 wishes spawn relative to Pip",
        True, LABEL)
    sheet.blit(title, (PAD, 12))
    sub = _font(13).render(
        "Shaded region = off-screen at spawn (offers scroll left into "
        "view). KNIGHT=blue  POISON=green  SKATEBOARD=orange.  D = AI pick.",
        True, SUB)
    sheet.blit(sub, (PAD, 36))

    for i, opt in enumerate(OPTIONS):
        col = i % cols
        row = i // cols
        x = PAD + col * (cell_w + PAD)
        y = HEADER + row * (cell_h + CAP_H + ROW_GAP)
        print(f"  rendering layout {opt} ...")
        view = _world_view(opt)
        sheet.blit(view, (x, y))
        is_pick = (opt == "D")
        pygame.draw.rect(sheet, PICK if is_pick else (60, 66, 80),
                         (x, y, cell_w, cell_h), 3 if is_pick else 1)
        cap = _font(15, bold=True).render(
            f"{opt}", True, PICK if is_pick else LABEL)
        sheet.blit(cap, (x, y + cell_h + 4))
        desc = _font(12).render(DESCRIPTIONS[opt], True, SUB)
        sheet.blit(desc, (x + 22, y + cell_h + 6))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
