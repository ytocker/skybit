"""Poison vial — aura SIZE variants at the W1 palette.

Five cells, all using W1 colours (the lightest end of the colour ramp),
but with progressively larger warning aura behind the bottle so the
user can pick the size separately from the colour. All cells use the
strengthened alphas (core 230 / outer 140) so the size differences are
the only thing changing.

Output: docs/screenshots/icon_sizes/poison_aura_size_variants.png
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

from game import poison_vial as pv, parrot


# W1 palette (the lightest end of the D1..D5 ramp).
W1_GLASS   = (145, 210, 125)
W1_LIQUID  = (175, 230, 140)
W1_TOX     = (200, 240, 155)
W1_OUTLINE = ( 32,  48,  34)
W1_VAPOR   = (225, 250, 170)


# Each entry: label, core_r, halo_r
AURA_SIZES = (
    ("A1 — small",      10, 14),
    ("A2 — default",    14, 19),
    ("A3 — medium",     18, 25),
    ("A4 — large",      22, 32),
    ("A5 — huge",       28, 40),
)

STRONG_CORE_ALPHA  = 230
STRONG_OUTER_ALPHA = 140

CARD_BG = (24, 26, 34)
LABEL   = (235, 235, 240)
SUB     = (165, 173, 185)

CELL_W = 220
CELL_H = 180
PAD    = 14
HEADER_H = 80
LEGEND_H = 44


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _render_vial_with_aura(surf, cx, cy, core_r, halo_r):
    saved = {
        "GREEN_GLASS": pv.GREEN_GLASS,
        "GREEN_LO":    pv.GREEN_LO,
        "GREEN_TOX":   pv.GREEN_TOX,
        "BLACK_DOME":  pv.BLACK_DOME,
        "VAPOR_HI":    pv.VAPOR_HI,
    }
    prev_cache = getattr(pv, "_VIAL_CACHE", None)
    prev_warning = pv._warning_glow_blit

    pv.GREEN_GLASS = W1_GLASS
    pv.GREEN_LO    = W1_LIQUID
    pv.GREEN_TOX   = W1_TOX
    pv.BLACK_DOME  = W1_OUTLINE
    pv.VAPOR_HI    = W1_VAPOR
    pv._VIAL_CACHE = None

    def patched_glow(s, gcx, gcy, pulse_phase,
                     color=W1_VAPOR,
                     core_alpha=STRONG_CORE_ALPHA,
                     core_r=core_r, halo_r=halo_r,
                     outer_alpha=STRONG_OUTER_ALPHA):
        return prev_warning(s, gcx, gcy, pulse_phase,
                            color=color, core_alpha=core_alpha,
                            core_r=core_r, halo_r=halo_r,
                            outer_alpha=outer_alpha)
    pv._warning_glow_blit = patched_glow

    pv.draw(surf, int(cx), int(cy), 0.0)

    for k, v in saved.items():
        setattr(pv, k, v)
    pv._warning_glow_blit = prev_warning
    pv._VIAL_CACHE = prev_cache


def _build_cell(core_r, halo_r):
    cell = pygame.Surface((CELL_W, CELL_H))
    cell.fill((32, 34, 42))
    pip = parrot.get_parrot(0, 0.0)
    cell.blit(pip, pip.get_rect(center=(50, CELL_H // 2)))
    _render_vial_with_aura(cell, CELL_W - 60, CELL_H // 2,
                            core_r, halo_r)
    pygame.draw.rect(cell, (45, 50, 62), cell.get_rect(), 1)
    return cell


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "poison_aura_size_variants.png")

    n = len(AURA_SIZES)
    sheet_w = PAD * 2 + n * (CELL_W + PAD) - PAD
    sheet_h = HEADER_H + CELL_H + LEGEND_H + 14
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(20, bold=True).render(
        "POISON vial — aura SIZE variants (W1 palette, strengthened alphas)",
        True, LABEL)
    sheet.blit(title, (PAD, 14))
    sub = _font(13).render(
        "Pick a core_r / halo_r pair separately from the colour. All "
        "cells use the W1 palette + bumped alphas (core 230 / outer 140).",
        True, SUB)
    sheet.blit(sub, (PAD, 38))

    for i, (code, core_r, halo_r) in enumerate(AURA_SIZES):
        x = PAD + i * (CELL_W + PAD)
        y = HEADER_H
        sheet.blit(_build_cell(core_r, halo_r), (x, y))
        cap = _font(13, bold=True).render(code, True, LABEL)
        sheet.blit(cap, (x + (CELL_W - cap.get_width()) // 2,
                         y + CELL_H + 6))
        leg = _font(11).render(
            f"core_r={core_r}   halo_r={halo_r}", True, SUB)
        sheet.blit(leg, (x + (CELL_W - leg.get_width()) // 2,
                         y + CELL_H + 24))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
