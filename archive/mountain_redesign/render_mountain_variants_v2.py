"""Render the round-1 mountain redesign contact sheet.

Rows = baseline (current draw_mountains) + 5 redesign variants.
Cols = 5 times of day (day / sunrise / sunset / dusk / night).
Each cell is a full game-style composite: biome sky + clouds + mountains +
ground + two pillar pairs for scale. Output: docs/mountain_redesign/.

Run from anywhere:
    python archive/mountain_redesign/render_mountain_variants_v2.py
"""
import os, sys, pathlib, math, random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE.parent.parent))  # repo root → game/ package
sys.path.insert(0, str(_HERE))                 # this dir → variants module

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y, PIPE_W
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_cloud, draw_ground
from game.pillar_variants import draw_pillar_pair
from mountain_variants_v2 import VARIANTS, VARIANT_NAMES


# Five representative keyframes across the cycle.
PHASES = [
    ("day", 0.02),
    ("sunrise", 0.906),
    ("sunset", 0.363),
    ("dusk", 0.513),
    ("night", 0.644),
]

OUT = _HERE.parent.parent / "docs" / "mountain_redesign"
OUT.mkdir(parents=True, exist_ok=True)


def render_scene(variant_id: int, phase: float) -> pygame.Surface:
    palette = _biome.palette_for_phase(phase)
    surf = pygame.Surface((W, H))

    bucket = int(phase * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
    sky.set_alpha(None)
    surf.blit(sky, (0, 0))

    scroll = 120.0
    for i, (bx, by, sc, variant) in enumerate((
            (40, 95, 0.9, 0), (200, 150, 1.0, 2),
            (90, 230, 0.8, 3), (270, 70, 0.7, 1))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(0.45 + i) * 3, sc, variant=variant)

    VARIANTS[variant_id](surf, scroll, GROUND_Y, W,
                         palette['mtn_far'], palette['mtn_near'])

    draw_ground(surf, GROUND_Y, W, H, scroll,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))

    gap_y, gap_h = 285, 150
    for px, seed in ((W - 78, 7), (W - 210, 13)):
        top = pygame.Rect(px, 0, PIPE_W, gap_y - gap_h // 2)
        bot = pygame.Rect(px, gap_y + gap_h // 2, PIPE_W,
                          GROUND_Y - (gap_y + gap_h // 2))
        draw_pillar_pair(surf, top, bot, palette, seed)

    return surf


def make_contact_sheet(images: dict) -> pygame.Surface:
    rows = [0, 1, 2, 3, 4, 5]
    cols = PHASES
    thumb_w, thumb_h = W // 2, H // 2     # 180 × 320
    label_h = 20
    row_label_w = 132
    pad = 8
    sheet_w = row_label_w + pad + len(cols) * (thumb_w + pad)
    sheet_h = label_h + pad + len(rows) * (thumb_h + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 22, 26))

    font = pygame.font.SysFont(None, 17)
    head = pygame.font.SysFont(None, 19)

    for c, (pname, _) in enumerate(cols):
        x = row_label_w + pad + c * (thumb_w + pad)
        lbl = head.render(pname.upper(), True, (235, 235, 235))
        sheet.blit(lbl, (x + thumb_w // 2 - lbl.get_width() // 2, 3))

    for r, vid in enumerate(rows):
        y = label_h + pad + r * (thumb_h + pad)
        name = VARIANT_NAMES[vid]
        tag = head.render(f"V{vid}" if vid else "BASE", True, (255, 220, 130))
        sheet.blit(tag, (6, y + 6))
        # Wrap the variant name onto a couple of lines in the row gutter.
        words = name.split()
        line, ly = "", y + 28
        for word in words:
            test = (line + " " + word).strip()
            if font.size(test)[0] > row_label_w - 10 and line:
                sheet.blit(font.render(line, True, (210, 210, 210)), (6, ly))
                ly += 16
                line = word
            else:
                line = test
        if line:
            sheet.blit(font.render(line, True, (210, 210, 210)), (6, ly))

        for c, (pname, _) in enumerate(cols):
            full = images[(vid, pname)]
            thumb = pygame.transform.smoothscale(full, (thumb_w, thumb_h))
            x = row_label_w + pad + c * (thumb_w + pad)
            sheet.blit(thumb, (x, y))

    return sheet


def main() -> None:
    for old in OUT.glob("*.png"):
        old.unlink()

    images: dict = {}
    for vid in (0, 1, 2, 3, 4, 5):
        for pname, pval in PHASES:
            random.seed(vid * 100 + int(pval * 1000))
            images[(vid, pname)] = render_scene(vid, pval)

    sheet = make_contact_sheet(images)
    sheet_path = OUT / "_comparison.png"
    pygame.image.save(sheet, sheet_path)
    print(f"wrote {sheet_path}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
