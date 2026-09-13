"""Poison vial — colour ramp from W1 (lightest) toward darker.

Five cells, each progressively darker than W1. Every cell shifts the
full palette together (glass + liquid + meniscus + outline) AND binds
the vapor puffs + warning aura to a per-variant vapor colour so all
three layers stay in the same hue family. Aura alphas are bumped
(core 190 -> 230, outer 95 -> 140) so the glow reads as a stronger
warning behind the bottle.

Output: docs/screenshots/icon_sizes/poison_palette_variants.png
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


# Each entry: label, glass, liquid, tox, outline, vapor
VARIANTS = (
    ("D1 (=W1)",
        (145, 210, 125), (175, 230, 140), (200, 240, 155),
        ( 32,  48,  34), (225, 250, 170)),
    ("D2",
        (130, 195, 110), (160, 215, 125), (185, 225, 140),
        ( 28,  42,  30), (210, 240, 155)),
    ("D3",
        (115, 180,  95), (145, 200, 110), (170, 210, 125),
        ( 24,  36,  26), (195, 230, 140)),
    ("D4",
        (100, 165,  80), (130, 185,  95), (155, 195, 110),
        ( 20,  30,  22), (180, 220, 125)),
    ("D5",
        ( 85, 150,  65), (115, 170,  80), (140, 180,  95),
        ( 16,  24,  18), (165, 210, 110)),
)

# Aura defaults stronger than today's (190 / 95) so the halo carries
# the "avoid me" cue at any colour. Geometry unchanged (core_r=14,
# halo_r=19).
STRONG_CORE_ALPHA  = 230
STRONG_OUTER_ALPHA = 140

CARD_BG = (24, 26, 34)
LABEL   = (235, 235, 240)
SUB     = (165, 173, 185)

CELL_W = 200
CELL_H = 160
PAD    = 14
HEADER_H = 80
LEGEND_H = 96


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _render_vial_with_palette(surf, cx, cy,
                              glass, liquid, tox, outline, vapor):
    """Swap all five palette slots + override _warning_glow_blit
    defaults so the aura reads stronger. Restore afterwards."""
    saved = {
        "GREEN_GLASS": pv.GREEN_GLASS,
        "GREEN_LO":    pv.GREEN_LO,
        "GREEN_TOX":   pv.GREEN_TOX,
        "BLACK_DOME":  pv.BLACK_DOME,
        "VAPOR_HI":    pv.VAPOR_HI,
    }
    prev_cache = getattr(pv, "_VIAL_CACHE", None)
    prev_warning = pv._warning_glow_blit

    pv.GREEN_GLASS = glass
    pv.GREEN_LO    = liquid
    pv.GREEN_TOX   = tox
    pv.BLACK_DOME  = outline
    pv.VAPOR_HI    = vapor
    pv._VIAL_CACHE = None

    def patched_glow(s, gcx, gcy, pulse_phase,
                     color=vapor,
                     core_alpha=STRONG_CORE_ALPHA, core_r=14,
                     halo_r=19, outer_alpha=STRONG_OUTER_ALPHA):
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


def _build_cell(glass, liquid, tox, outline, vapor):
    cell = pygame.Surface((CELL_W, CELL_H))
    cell.fill((32, 34, 42))
    pip = parrot.get_parrot(0, 0.0)
    cell.blit(pip, pip.get_rect(center=(46, CELL_H // 2)))
    _render_vial_with_palette(cell, CELL_W - 50, CELL_H // 2,
                              glass, liquid, tox, outline, vapor)
    pygame.draw.rect(cell, (45, 50, 62), cell.get_rect(), 1)
    return cell


def _fmt(rgb):
    return f"({rgb[0]:>3}, {rgb[1]:>3}, {rgb[2]:>3})"


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "poison_palette_variants.png")

    n = len(VARIANTS)
    sheet_w = PAD * 2 + n * (CELL_W + PAD) - PAD
    sheet_h = HEADER_H + CELL_H + LEGEND_H + 14
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(20, bold=True).render(
        "POISON vial — colour ramp from W1 (D1) toward darker (D5)",
        True, LABEL)
    sheet.blit(title, (PAD, 14))
    sub = _font(13).render(
        "Bubbles + aura now use a per-variant vapor colour. Aura "
        "alphas bumped 190 -> 230 / 95 -> 140 (stronger halo).",
        True, SUB)
    sheet.blit(sub, (PAD, 38))

    for i, (code, glass, lo, tox, outline, vapor) in enumerate(VARIANTS):
        x = PAD + i * (CELL_W + PAD)
        y = HEADER_H
        sheet.blit(_build_cell(glass, lo, tox, outline, vapor), (x, y))
        cap = _font(13, bold=True).render(code, True, LABEL)
        sheet.blit(cap, (x + (CELL_W - cap.get_width()) // 2,
                         y + CELL_H + 6))
        legend = (
            ("glass",   glass),
            ("liquid",  lo),
            ("tox",     tox),
            ("outline", outline),
            ("vapor",   vapor),
        )
        for ln, (lbl, val) in enumerate(legend):
            s = _font(11).render(f"{lbl}  {_fmt(val)}", True, SUB)
            sheet.blit(s, (x + (CELL_W - s.get_width()) // 2,
                           y + CELL_H + 24 + ln * 14))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
