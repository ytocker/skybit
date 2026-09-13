"""POISON VIAL — final pick: variant A (CLASSIC) with halo recoloured
from red → vapor yellow-green per user direction.

Renders a single hi-res preview sheet so the user can sign off before the
sprite is wired into the game. Reuses the Round-5 flask + label draws and
overrides only the warning-halo color via _warning_glow_blit.
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

# Import the variant draw machinery from round 5
from render_death_trap_round_5_vial import (
    DAWN_TEAL, SS, VAPOR_HI,
    _ss_canvas, _resolve, _draw_flask_body, _label_classic,
    _warning_glow_blit,
)


INK      = (235, 240, 250)
DIM      = (150, 158, 178)
HOT      = (160, 230, 110)
PANEL_BG = (24, 28, 42)
GRID     = (54, 62, 86)


def draw_variant_A(out_size: int, pulse: float) -> pygame.Surface:
    """Variant A with the warning halo recoloured to vapor yellow-green."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 4, pulse,
                       color=VAPOR_HI,
                       core_alpha=190, core_r=14, halo_r=19,
                       outer_alpha=95)
    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 4 * SS
    _draw_flask_body(big, cx, cy, pulse, _label_classic)
    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


SIZES_ZOOM = [(48, 1, "in-world (48 px)"),
              (192, 4, "4× zoom"),
              (384, 8, "8× zoom")]

GUTTER  = 18
SWATCH_PAD = 24


def _swatch_circle(d: int) -> pygame.Surface:
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(s, DAWN_TEAL, (d // 2, d // 2), d // 2)
    pygame.draw.circle(s, (28, 32, 50), (d // 2, d // 2), d // 2, 2)
    return s


def build_sheet() -> pygame.Surface:
    swatch_widths = [(s + SWATCH_PAD * 2 + 16) for s, _, _ in SIZES_ZOOM]
    sheet_w = sum(swatch_widths) + GUTTER * (len(SIZES_ZOOM) + 1)
    sheet_h = 110 + max(swatch_widths) + 60

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(DAWN_TEAL)

    font_title = pygame.font.SysFont("dejavusansmono", 26, bold=True)
    font_sub   = pygame.font.SysFont("dejavusans", 14)
    font_size  = pygame.font.SysFont("dejavusans", 13, bold=True)
    font_xs    = pygame.font.SysFont("dejavusans", 11)

    sheet.blit(font_title.render(
        "POISON VIAL  —  variant A FINAL  (halo: vapor yellow-green)",
        True, INK), (GUTTER, 14))
    sheet.blit(font_sub.render(
        "Skull-and-crossbones inside the flask outline (Round-5). "
        "Warning halo recoloured from red → matching the toxic vapor "
        "puffs above the cork.",
        True, DIM), (GUTTER, 46))
    sheet.blit(font_sub.render(
        f"halo color = VAPOR_HI ({VAPOR_HI[0]}, {VAPOR_HI[1]}, {VAPOR_HI[2]})",
        True, HOT), (GUTTER, 70))

    pulse = 0.5
    x = GUTTER
    base_icon = draw_variant_A(48, pulse)
    for display_size, zoom, lbl in SIZES_ZOOM:
        if zoom == 1:
            icon = base_icon
        else:
            icon = pygame.transform.scale(
                base_icon, (48 * zoom, 48 * zoom))
        d = display_size + SWATCH_PAD * 2
        swatch = _swatch_circle(d)
        sy = 110
        sheet.blit(swatch, (x, sy))
        bob = int(math.sin(pulse * 1.0) * 2 * zoom)
        ix = x + (d - icon.get_width()) // 2
        iy = sy + (d - icon.get_height()) // 2 + bob
        sheet.blit(icon, (ix, iy))
        lbl_surf = font_size.render(lbl, True, INK)
        sheet.blit(lbl_surf,
                   (x + (d - lbl_surf.get_width()) // 2, sy + d + 8))
        x += d + 16 + GUTTER

    sheet.blit(font_xs.render(
        "ready to wire into the game — kind='poison', anti-powerup that "
        "kills Pip on pickup",
        True, DIM), (GUTTER, sheet_h - 20))
    return sheet


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR), "docs", "death_pickup")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_7_A_final_greenhalo.png")
    sheet = build_sheet()
    pygame.image.save(sheet, out)
    print(f"saved {out}  size={sheet.get_size()}")


if __name__ == "__main__":
    main()
