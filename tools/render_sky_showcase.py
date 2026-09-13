"""Assemble sky-transition showcase: ORIGINAL + 5 concept round_2 rows.

Output: docs/sky_transition/showcase.png

Each row is a full 9-panel golden-hour→night strip (1532×540).
ORIGINAL is rendered live from ALPINE_HAZE; concepts loaded from round_2.png.

    python tools/render_sky_showcase.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game.biome_sky_keyframes import ALPINE_HAZE  # noqa: E402
from game.biome_sky import paint_sky               # noqa: E402
from game.config import W, H, GROUND_Y            # noqa: E402


SAMPLES = [
    (0.235, "Golden Hour\n(start)"),
    (0.27,  "Golden Hour"),
    (0.31,  "Golden Hour\n(late)"),
    (0.37,  "Sunset"),
    (0.42,  "Sunset\n(deep)"),
    (0.47,  "Dusk"),
    (0.52,  "Dusk (late)"),
    (0.56,  "Twilight"),
    (0.62,  "Night"),
]

PANEL_W = 160
PANEL_H = 440
GAP = 8
MARGIN = 14
HEADER = 44
FOOTER = 56
ROW_H = HEADER + PANEL_H + FOOTER     # 540
N = len(SAMPLES)
ROW_W = MARGIN * 2 + N * PANEL_W + (N - 1) * GAP   # 1532

BG       = (8, 8, 20)
BG_LABEL = (14, 14, 32)
TEXT_HI  = (245, 246, 250)
TEXT_LO  = (170, 175, 190)
ACCENT   = (70, 80, 110)
GROUND_L = (60, 65, 80)

LABEL_W     = 90
INTER_GAP   = 8
MAIN_TITLE_H = 52

CONCEPTS = [
    ("ORIGINAL",             None),
    ("A2  Smoky Haze",       "a2_smoky_haze/round_2.png"),
    ("B   Ozone Bloom",      "b_ozone_bloom/round_2.png"),
    ("C   Ember Core",       "c_ember_core/round_2.png"),
    ("D2  Amber Afterglow",  "d2_amber_afterglow/round_2.png"),
    ("E   Velvet Deep",      "e_velvet_deep/round_2.png"),
]


def _wrap(text):
    return text.split("\n")


def _render_original(f_title, f_label, f_phase):
    surf = pygame.Surface((ROW_W, ROW_H))
    surf.fill(BG)

    t = f_title.render("ORIGINAL — Alpine Haze  (live deployed sky)", True, TEXT_HI)
    surf.blit(t, (ROW_W // 2 - t.get_width() // 2, 12))

    ground_frac = GROUND_Y / H

    for i, (phase, label) in enumerate(SAMPLES):
        x = MARGIN + i * (PANEL_W + GAP)
        y = HEADER

        tile = pygame.Surface((W, H))
        paint_sky(tile, ALPINE_HAZE, W, H, phase, stars=True, ground_y=GROUND_Y)
        panel = pygame.transform.smoothscale(tile, (PANEL_W, PANEL_H))
        surf.blit(panel, (x, y))

        gy = y + int(ground_frac * PANEL_H)
        for dx in range(0, PANEL_W, 8):
            pygame.draw.line(surf, GROUND_L,
                             (x + dx, gy), (x + min(dx + 4, PANEL_W - 1), gy), 1)

        fy = y + PANEL_H + 6
        for j, line in enumerate(_wrap(label)):
            lbl = f_label.render(line, True, TEXT_HI)
            surf.blit(lbl, (x + PANEL_W // 2 - lbl.get_width() // 2, fy + j * 16))

        ph = f_phase.render(f"phase {phase}", True, TEXT_LO)
        surf.blit(ph, (x + PANEL_W // 2 - ph.get_width() // 2, fy + 36))

    return surf


def main():
    canvas_w = LABEL_W + ROW_W
    canvas_h = MAIN_TITLE_H + len(CONCEPTS) * ROW_H + (len(CONCEPTS) - 1) * INTER_GAP
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill(BG)

    f_main  = pygame.font.SysFont("dejavusans", 18, bold=True)
    f_title = pygame.font.SysFont("dejavusans", 14, bold=True)
    f_label = pygame.font.SysFont("dejavusans", 12, bold=True)
    f_phase = pygame.font.SysFont("dejavusans", 10)
    f_id    = pygame.font.SysFont("dejavusans", 13, bold=True)

    # Main title
    mt = f_main.render(
        "Alpine Haze — Sky Palette Alternatives  (Golden Hour → Night)", True, TEXT_HI)
    canvas.blit(mt, (canvas_w // 2 - mt.get_width() // 2,
                     MAIN_TITLE_H // 2 - mt.get_height() // 2))

    base_dir = os.path.join(_ROOT, "docs", "sky_transition")

    for i, (name, rel_path) in enumerate(CONCEPTS):
        y = MAIN_TITLE_H + i * (ROW_H + INTER_GAP)

        # Left label strip
        label_surf = pygame.Surface((LABEL_W, ROW_H))
        label_surf.fill(BG_LABEL)
        # Right edge accent line
        pygame.draw.rect(label_surf, ACCENT, (LABEL_W - 2, 0, 2, ROW_H))

        id_text = f_id.render(name, True, TEXT_HI)
        id_rot  = pygame.transform.rotate(id_text, 90)
        label_surf.blit(id_rot, (LABEL_W // 2 - id_rot.get_width() // 2,
                                  ROW_H // 2 - id_rot.get_height() // 2))
        canvas.blit(label_surf, (0, y))

        # Row content
        if rel_path is None:
            row = _render_original(f_title, f_label, f_phase)
            canvas.blit(row, (LABEL_W, y))
        else:
            row = pygame.image.load(os.path.join(base_dir, rel_path))
            canvas.blit(row, (LABEL_W, y))

        # Separator between rows
        if i < len(CONCEPTS) - 1:
            sep_y = y + ROW_H + INTER_GAP // 2
            pygame.draw.line(canvas, ACCENT, (0, sep_y), (canvas_w, sep_y), 1)

    out = os.path.join(_ROOT, "docs", "sky_transition", "showcase.png")
    pygame.image.save(canvas, out)

    # Verify without displaying
    from PIL import Image
    img = Image.open(out)
    print(f"wrote {out}  ({img.width}×{img.height})")

    # Sample a few pixels per row to confirm variety
    for i, (name, _) in enumerate(CONCEPTS):
        row_y = MAIN_TITLE_H + i * (ROW_H + INTER_GAP) + HEADER + PANEL_H // 2
        mid_x = LABEL_W + MARGIN + 4 * (PANEL_W + GAP) + PANEL_W // 2  # panel 4 (0.42)
        px = img.getpixel((mid_x, row_y))
        print(f"  {name:24s} panel4 mid: {px}")


if __name__ == "__main__":
    main()
