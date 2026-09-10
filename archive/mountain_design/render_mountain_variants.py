"""Render preview screenshots of the 5 mountain variants for design review.

For each variant V1..V5 and each phase (day, sunset, night) renders a full
W×H game-style composite (sky + clouds + mountains + ground + a couple of
pillars). Output goes to ``./screenshots/``. A contact sheet
``_contact_sheet.png`` (5 rows × 3 cols) is also written for quick
side-by-side comparison.

Run from anywhere:
    python archive/mountain_design/render_mountain_variants.py
"""
import os, sys, pathlib, math, random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE.parent.parent))  # repo root → game/ package
sys.path.insert(0, str(_HERE))                # this dir → mountain_variants

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y, PIPE_W
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_cloud, draw_ground,
)
from mountain_variants import VARIANTS, VARIANT_NAMES
from game.pillar_variants import draw_pillar_pair


PHASES = [
    ("day",    0.05),
    ("sunset", 0.32),
    ("night",  0.62),
]

OUT = _HERE / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)


def render_scene(variant_id: int, phase: float) -> pygame.Surface:
    palette = _biome.palette_for_phase(phase)

    surf = pygame.Surface((W, H))

    # Sky (single bucket — no fade in the still frame).
    bucket = int(phase * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
    sky.set_alpha(None)
    surf.blit(sky, (0, 0))

    # A few clouds for context.
    scroll = 80.0
    cloud_phase = 1.5
    for i, (bx, by, sc, variant) in enumerate((
            (40, 95, 0.9, 0), (200, 150, 1.0, 2),
            (90, 230, 0.8, 3), (270, 70, 0.7, 1))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(cloud_phase * 0.3 + i) * 3,
                   sc, variant=variant)

    # The variant's mountains.
    VARIANTS[variant_id](surf, scroll, GROUND_Y, W,
                         palette['mtn_far'], palette['mtn_near'])

    # Ground.
    draw_ground(surf, GROUND_Y, W, H, scroll,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))

    # Two pillar pairs near the right for scale reference.
    gap_y = 280
    gap_h = 150
    for px, seed in ((W - 90, 7), (W - 220, 13)):
        top = pygame.Rect(px, 0, PIPE_W, gap_y - gap_h // 2)
        bot = pygame.Rect(px, gap_y + gap_h // 2, PIPE_W,
                          GROUND_Y - (gap_y + gap_h // 2))
        draw_pillar_pair(surf, top, bot, palette, seed)

    return surf


def make_contact_sheet(images: dict) -> pygame.Surface:
    """5 rows × 3 cols thumbnail grid with labels."""
    cols = len(PHASES)
    rows = 5
    thumb_w, thumb_h = W // 2, H // 2  # 180 × 320
    label_h = 22
    pad = 8
    sheet_w = pad + cols * (thumb_w + pad)
    sheet_h = pad + rows * (thumb_h + label_h + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 24, 28))

    font = pygame.font.SysFont(None, 16)

    for r, vid in enumerate((1, 2, 3, 4, 5)):
        for c, (pname, _) in enumerate(PHASES):
            full = images[(vid, pname)]
            thumb = pygame.transform.smoothscale(full, (thumb_w, thumb_h))
            x = pad + c * (thumb_w + pad)
            y = pad + r * (thumb_h + label_h + pad)
            sheet.blit(thumb, (x, y))
            txt = f"V{vid} {VARIANT_NAMES[vid]} — {pname}"
            label = font.render(txt, True, (220, 220, 220))
            sheet.blit(label, (x + 4, y + thumb_h + 4))

    return sheet


def main() -> None:
    # Wipe old previews so renames don't leave stale files.
    for old in OUT.glob("*.png"):
        old.unlink()

    images: dict = {}
    for vid in (1, 2, 3, 4, 5):
        for pname, pval in PHASES:
            random.seed(vid * 100 + int(pval * 1000))
            surf = render_scene(vid, pval)
            images[(vid, pname)] = surf
            out_path = OUT / f"v{vid}_{pname}.png"
            pygame.image.save(surf, out_path)
            print(f"wrote {out_path}")

    sheet = make_contact_sheet(images)
    sheet_path = OUT / "_contact_sheet.png"
    pygame.image.save(sheet, sheet_path)
    print(f"wrote {sheet_path}")


if __name__ == "__main__":
    main()
