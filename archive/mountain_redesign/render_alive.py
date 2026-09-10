"""Render two contact sheets for the alive-world keeper expansions.

Sheet A — ``_comparison_alive.png``
    4 rows (V4, V12, V13, V14) × 5 columns = 5 different procedural SEEDS,
    all at the same SUNSET phase. Each row shows five different "scenes"
    of the same variant — that's how the user judges whether the world
    feels like it's changing as the player scrolls.

Sheet B — ``_comparison_alive_dayNight.png``
    4 rows × 5 columns = 5 PHASES (day / sunrise / sunset / dusk / night),
    each row pinned to a SINGLE shared scroll value so the column reads as
    one consistent world walking through the day cycle. Confirms element
    variation holds across the palette interpolation.

Run from anywhere::

    python archive/mountain_redesign/render_alive.py
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
import mountain_variants_alive as mv


PHASES = [
    ("day", 0.02),
    ("sunrise", 0.906),
    ("sunset", 0.363),
    ("dusk", 0.513),
    ("night", 0.644),
]

# Five distinct scroll values for the seed sheet — chosen to be far apart so
# each cell gets a completely different procedural scatter.
SEED_SCROLLS = [120.0, 540.0, 1080.0, 1820.0, 2730.0]

VARIANTS = [4, 12, 13, 14]

OUT = _HERE.parent.parent / "docs" / "mountain_redesign"
OUT.mkdir(parents=True, exist_ok=True)


def render_scene(variant_id: int, phase: float, scroll: float) -> pygame.Surface:
    """One full 360x640 tile: sky + clouds + the alive mountain variant +
    ground + a pair of pillars, in the same composite shape as the keeper
    sheet, so the new sheets read like real in-game frames."""
    palette = _biome.palette_for_phase(phase)
    surf = pygame.Surface((W, H))

    bucket = int(phase * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
    sky.set_alpha(None)
    surf.blit(sky, (0, 0))

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


def make_sheet(images: dict, col_labels, row_label_extra: str) -> pygame.Surface:
    tw, th = W, H
    label_h = 30
    row_label_w = 200
    pad = 10
    sheet_w = row_label_w + pad + len(col_labels) * (tw + pad)
    sheet_h = label_h + pad + len(VARIANTS) * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    font = pygame.font.SysFont(None, 22)
    head = pygame.font.SysFont(None, 28)
    cell_lbl = pygame.font.SysFont(None, 22)

    for c, label in enumerate(col_labels):
        x = row_label_w + pad + c * (tw + pad)
        lbl = head.render(label.upper(), True, (240, 240, 240))
        sheet.blit(lbl, (x + tw // 2 - lbl.get_width() // 2, 4))

    for r, vid in enumerate(VARIANTS):
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
        if row_label_extra:
            extra = font.render(row_label_extra, True, (160, 200, 255))
            sheet.blit(extra, (8, ly + 24))

        for c, label in enumerate(col_labels):
            full = images[(vid, label)]
            x = row_label_w + pad + c * (tw + pad)
            sheet.blit(full, (x, y))
            cap = cell_lbl.render(f"V{vid} · {label}", True, (250, 250, 250))
            bg = pygame.Surface((cap.get_width() + 8, cap.get_height() + 4),
                                pygame.SRCALPHA)
            bg.fill((0, 0, 0, 120))
            sheet.blit(bg, (x + 4, y + 4))
            sheet.blit(cap, (x + 8, y + 6))

    return sheet


def main() -> None:
    # ── Sheet A: same phase (sunset), 5 different scroll seeds per row.
    sunset_phase = 0.363
    images_a: dict = {}
    col_labels_a = [f"seed {i + 1}" for i in range(len(SEED_SCROLLS))]
    for vid in VARIANTS:
        for label, scroll in zip(col_labels_a, SEED_SCROLLS):
            random.seed(vid * 100 + int(scroll))
            images_a[(vid, label)] = render_scene(vid, sunset_phase, scroll)
    sheet_a = make_sheet(images_a, col_labels_a,
                         row_label_extra="5 different seeds @ sunset")
    a_path = OUT / "_comparison_alive.png"
    pygame.image.save(sheet_a, a_path)
    print(f"wrote {a_path}  ({sheet_a.get_width()}x{sheet_a.get_height()})")

    # ── Sheet B: 5 phases (day cycle), single shared scroll per row to show
    # the same world holds shape across the palette.
    images_b: dict = {}
    col_labels_b = [name for name, _ in PHASES]
    for vid in VARIANTS:
        # Shared scroll per row keeps element layout fixed across phases.
        scroll = 1080.0
        for name, val in PHASES:
            random.seed(vid * 100 + int(val * 1000))
            images_b[(vid, name)] = render_scene(vid, val, scroll)
    sheet_b = make_sheet(images_b, col_labels_b,
                         row_label_extra="shared seed across day cycle")
    b_path = OUT / "_comparison_alive_dayNight.png"
    pygame.image.save(sheet_b, b_path)
    print(f"wrote {b_path}  ({sheet_b.get_width()}x{sheet_b.get_height()})")


if __name__ == "__main__":
    main()
