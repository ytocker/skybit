"""Render the 4-row "keepers" contact sheet (V4 / V12 / V13 / V14).

Survivor set after user feedback "Keep versions 4, 12, 13, 14. Now in most of
them there are some horizontal lines clearly seen with a colour. No need for
the lines." This sheet exists to verify the offending stripes are gone while
each variant still holds its presence.

Rows = V4, V12, V13, V14 (in that order). Cols = 5 times of day. Each tile
is a FULL-SIZE 360x640 game-style composite. Output:
docs/mountain_redesign/_comparison_keepers.png

Run from anywhere:
    python archive/mountain_redesign/render_keepers.py
"""
import os, sys, pathlib, math, random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE.parent.parent))
sys.path.insert(0, str(_HERE))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y, PIPE_W
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_cloud, draw_ground
from game.pillar_variants import draw_pillar_pair
import mountain_variants_r2 as mv


PHASES = [
    ("day", 0.02),
    ("sunrise", 0.906),
    ("sunset", 0.363),
    ("dusk", 0.513),
    ("night", 0.644),
]

# Only the four survivor variants — same identities as in the previous
# shan-shui sheet, just narrowed to the keep-list.
KEEPERS = [4, 12, 13, 14]

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

    mv.set_phase(phase)
    mv.VARIANTS[variant_id](surf, scroll, GROUND_Y, W,
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
    rows = KEEPERS
    cols = PHASES
    tw, th = W, H
    label_h = 26
    row_label_w = 178
    pad = 10
    sheet_w = row_label_w + pad + len(cols) * (tw + pad)
    sheet_h = label_h + pad + len(rows) * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    font = pygame.font.SysFont(None, 22)
    head = pygame.font.SysFont(None, 28)
    cell_lbl = pygame.font.SysFont(None, 22)

    for c, (pname, _) in enumerate(cols):
        x = row_label_w + pad + c * (tw + pad)
        lbl = head.render(pname.upper(), True, (240, 240, 240))
        sheet.blit(lbl, (x + tw // 2 - lbl.get_width() // 2, 4))

    for r, vid in enumerate(rows):
        y = label_h + pad + r * (th + pad)
        name = mv.VARIANT_NAMES[vid]
        tag = head.render(f"V{vid}", True, (255, 220, 130))
        sheet.blit(tag, (8, y + 8))
        words = name.split()
        line, ly = "", y + 38
        for word in words:
            test = (line + " " + word).strip()
            if font.size(test)[0] > row_label_w - 12 and line:
                sheet.blit(font.render(line, True, (215, 215, 215)), (8, ly))
                ly += 20
                line = word
            else:
                line = test
        if line:
            sheet.blit(font.render(line, True, (215, 215, 215)), (8, ly))

        for c, (pname, _) in enumerate(cols):
            full = images[(vid, pname)]
            x = row_label_w + pad + c * (tw + pad)
            sheet.blit(full, (x, y))
            cap = cell_lbl.render(f"V{vid} · {pname}", True, (250, 250, 250))
            bg = pygame.Surface((cap.get_width() + 8, cap.get_height() + 4),
                                pygame.SRCALPHA)
            bg.fill((0, 0, 0, 120))
            sheet.blit(bg, (x + 4, y + 4))
            sheet.blit(cap, (x + 8, y + 6))

    return sheet


def main() -> None:
    images: dict = {}
    for vid in KEEPERS:
        for pname, pval in PHASES:
            random.seed(vid * 100 + int(pval * 1000))
            images[(vid, pname)] = render_scene(vid, pval)

    sheet = make_contact_sheet(images)
    sheet_path = OUT / "_comparison_keepers.png"
    pygame.image.save(sheet, sheet_path)
    print(f"wrote {sheet_path}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
