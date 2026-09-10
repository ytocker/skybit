"""Poison vial — aura SIZE fine-tune at D2 palette.

User picked D2 colours + wants 5 aura sizes scaling between A3 (18/25)
and A4 (22/32). This sheet sweeps that interval inclusive so they can
pick the exact halo size at the locked D2 hue.

Output: docs/screenshots/icon_sizes/poison_aura_finetune.png
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


# D2 palette (the picked colour ramp cell).
D2_GLASS   = (130, 195, 110)
D2_LIQUID  = (160, 215, 125)
D2_TOX     = (185, 225, 140)
D2_OUTLINE = ( 28,  42,  30)
D2_VAPOR   = (210, 240, 155)


# Each entry: label, core_r, halo_r — A3=18/25 → A4=22/32.
AURA_SIZES = (
    ("B1 = A3",       18, 25),
    ("B2",            19, 27),
    ("B3",            20, 28),
    ("B4",            21, 30),
    ("B5 = A4",       22, 32),
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

    pv.GREEN_GLASS = D2_GLASS
    pv.GREEN_LO    = D2_LIQUID
    pv.GREEN_TOX   = D2_TOX
    pv.BLACK_DOME  = D2_OUTLINE
    pv.VAPOR_HI    = D2_VAPOR
    pv._VIAL_CACHE = None

    def patched_glow(s, gcx, gcy, pulse_phase,
                     color=D2_VAPOR,
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
    out_path = os.path.join(out_dir, "poison_aura_finetune.png")

    n = len(AURA_SIZES)
    sheet_w = PAD * 2 + n * (CELL_W + PAD) - PAD
    sheet_h = HEADER_H + CELL_H + LEGEND_H + 14
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(20, bold=True).render(
        "POISON vial — aura size fine-tune (A3 → A4 at D2 palette)",
        True, LABEL)
    sheet.blit(title, (PAD, 14))
    sub = _font(13).render(
        "D2 colours locked. Five aura sizes evenly sweeping from "
        "A3 (18/25) to A4 (22/32). Pick a B cell.",
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
