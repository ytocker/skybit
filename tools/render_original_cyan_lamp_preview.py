"""Preview render of the ORIGINAL pale-cyan Faceted Crystal lamp with the
handle gem + inner-disc both retoned to the cyan family. Imports the
existing draw function from render_a1_lamp_variants so any palette
change there propagates automatically.

Layout: hero render top, in-game-scale strip (3x) bottom, single
charcoal card. Output:
    docs/screenshots/genie_designs/original_cyan_handlefix.png
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.dirname(THIS_DIR))

pygame.init()
pygame.display.set_mode((1, 1))

from tools.render_a1_lamp_variants import (
    draw_lamp_4_faceted, render_one,
    DISPLAY_BIG, DISPLAY_SMALL, W, H,
)


OUT_DIR = os.path.join(os.path.dirname(THIS_DIR),
                       "docs", "screenshots", "genie_designs")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, "original_cyan_handlefix.png")


CARD_BG = (22, 24, 32)
CARD_TINT = (30, 32, 42)
LABEL_FG = (220, 225, 235)
SUB_FG = (170, 178, 195)


def main():
    big = render_one(draw_lamp_4_faceted, DISPLAY_BIG)
    small = render_one(draw_lamp_4_faceted, DISPLAY_SMALL)

    bw, bh = big.get_size()
    sw, sh = small.get_size()

    margin = 28
    label_h = 30
    sub_h = 22
    gap = 18
    small_gap = 16
    strip_h = sh + 8

    sheet_w = max(bw, sw * 3 + small_gap * 2) + margin * 2
    sheet_h = (margin + label_h + bh + gap + sub_h + strip_h + margin)

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    font_big = pygame.font.SysFont("Arial", 22, bold=True)
    font_sub = pygame.font.SysFont("Arial", 13)

    title = font_big.render(
        "Original cyan Faceted Crystal  -  handle gem + inner disc retoned",
        True, LABEL_FG,
    )
    sheet.blit(title, ((sheet_w - title.get_width()) // 2, margin // 2 + 4))

    bx = (sheet_w - bw) // 2
    by = margin + label_h
    pygame.draw.rect(sheet, CARD_TINT,
                     (bx - 6, by - 6, bw + 12, bh + 12))
    sheet.blit(big, (bx, by))

    sub = font_sub.render(
        "in-game scale (3x at native pickup footprint)", True, SUB_FG,
    )
    sub_y = by + bh + gap
    sheet.blit(sub, ((sheet_w - sub.get_width()) // 2, sub_y))

    strip_y = sub_y + sub_h
    strip_w = sw * 3 + small_gap * 2
    sx0 = (sheet_w - strip_w) // 2
    for i in range(3):
        sx = sx0 + i * (sw + small_gap)
        pygame.draw.rect(sheet, CARD_TINT, (sx - 3, strip_y - 3, sw + 6, sh + 6))
        sheet.blit(small, (sx, strip_y))

    pygame.image.save(sheet, OUT_PATH)
    print(f"saved {OUT_PATH}  ({sheet_w}x{sheet_h})")

    # Pixel sample at hero handle-centre to confirm cyan family
    # (not the prior sapphire ~(70,100,220)).
    # The lamp is centered, so the handle ring sits left of the body
    # center. Sample a few px to find the gem core. The hero scale is
    # DISPLAY_BIG=4, lamp drawn at W*SS then smoothscaled to W*DISPLAY_BIG.
    # Handle anchor (h_cx) lives inside paint_torus_handle - sample a
    # range and report the most-saturated pixel.
    samples = []
    # Hero render only - cover roughly the left third where the handle sits.
    for px in range(bw // 8, bw // 3):
        for py in range(bh // 3, 2 * bh // 3):
            c = big.get_at((px, py))[:3]
            samples.append(c)
    # Find the pixel most blue-saturated (max B - max(R,G))
    blue_dominant = max(samples, key=lambda c: c[2] - max(c[0], c[1]))
    print(f"  most-blue pixel in handle region: {blue_dominant}")
    if blue_dominant[2] > 200 and blue_dominant[0] < 90:
        print("  WARNING: looks like residual sapphire (B>200 with low R)")
    else:
        print("  OK: no sapphire-tier blue in handle region")


if __name__ == "__main__":
    main()
