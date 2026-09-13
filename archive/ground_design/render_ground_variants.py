"""Render preview screenshots of the 5 ground variants for design review.

For each variant V1..V5 and each phase (day, sunset, night) renders a full
W×H game-style composite (sky + clouds + mountains + ground + pillars).
Output goes to ``screenshots/ground_variants/``. A contact sheet
``_contact_sheet.png`` (5 rows × 3 cols) is also written for quick
side-by-side comparison.

Run from anywhere:
    python archive/ground_design/render_ground_variants.py
"""
import os, sys, pathlib, math, random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE.parent.parent))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y, PIPE_W
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_cloud, draw_mountains,
)
from game.ground_variants import VARIANTS, VARIANT_NAMES
from game.pillar_variants import draw_pillar_pair


PHASES = [
    ("day",    0.05),
    ("sunset", 0.32),
    ("night",  0.62),
]

OUT = _HERE / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)


def render_scene(variant_id: int, phase: float,
                 scroll: float = 80.0) -> pygame.Surface:
    palette = _biome.palette_for_phase(phase)

    surf = pygame.Surface((W, H))

    # Sky
    bucket = int(phase * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
    sky.set_alpha(None)
    surf.blit(sky, (0, 0))

    # Clouds for context
    cloud_phase = 1.5
    for i, (bx, by, sc, variant) in enumerate((
            (40, 95, 0.9, 0), (200, 150, 1.0, 2),
            (90, 230, 0.8, 3), (270, 70, 0.7, 1))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(cloud_phase * 0.3 + i) * 3,
                   sc, variant=variant)

    # Mountains
    draw_mountains(surf, scroll, GROUND_Y, W,
                   palette['mtn_far'], palette['mtn_near'])

    # The variant's ground
    VARIANTS[variant_id](surf, GROUND_Y, W, H, scroll,
                         palette['ground_top'], palette['ground_mid'],
                         (60, 40, 25))

    # Two pillar pairs near the right for scale reference
    gap_y = 280
    gap_h = 150
    for px, seed in ((W - 90, 7), (W - 220, 13)):
        top = pygame.Rect(px, 0, PIPE_W, gap_y - gap_h // 2)
        bot = pygame.Rect(px, gap_y + gap_h // 2, PIPE_W,
                          GROUND_Y - (gap_y + gap_h // 2))
        draw_pillar_pair(surf, top, bot, palette, seed)

    return surf


def make_contact_sheet(images: dict) -> pygame.Surface:
    cols = len(PHASES)
    rows = 5
    thumb_w, thumb_h = W // 2, H // 2
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
    from game import ground_variants as _gv

    for old in OUT.glob("*.png"):
        old.unlink()

    images: dict = {}
    for vid in (1, 2, 3, 4, 5):
        for pname, pval in PHASES:
            # Different run seed per cell so the preview also exercises
            # the per-run variability code path.
            _gv.set_run_seed(vid * 7919 + int(pval * 10007))
            surf = render_scene(vid, pval)
            images[(vid, pname)] = surf
            out_path = OUT / f"v{vid}_{pname}.png"
            pygame.image.save(surf, out_path)
            print(f"wrote {out_path}")

    # Per-run variation: V3-day rendered 4 times with different RUN_SEEDs
    # to prove no two plays look identical even on the same theme.
    cell_w, cell_h = W // 2, H // 2
    pad = 8
    label_h = 22
    font = pygame.font.SysFont(None, 16)

    def _showcase(path, title, frames):
        """frames is a list of (label, render_fn -> Surface)."""
        sheet = pygame.Surface(
            (pad + len(frames) * (cell_w + pad), pad + cell_h + label_h + pad))
        sheet.fill((24, 24, 28))
        for i, (lbl, fn) in enumerate(frames):
            surf = fn()
            thumb = pygame.transform.smoothscale(surf, (cell_w, cell_h))
            x = pad + i * (cell_w + pad)
            y = pad
            sheet.blit(thumb, (x, y))
            sheet.blit(font.render(lbl, True, (220, 220, 220)),
                       (x + 4, y + cell_h + 4))
        pygame.image.save(sheet, path)
        print(f"wrote {path}")

    # Per-run (between plays) — different RUN_SEEDs reshuffle theme + sparsity
    def _per_run_frame(i):
        def _fn():
            _gv.set_run_seed(91200 + i * 31337)
            return render_scene(3, 0.05)
        return _fn
    _showcase(OUT / "_v3_per_run_variation.png",
              "V3 across runs (different RUN_SEEDs)",
              [(f"run #{i + 1}", _per_run_frame(i)) for i in range(4)])

    # Sparsity per run — pin RUN_DENSITY_BASE so the difference is obvious
    def _sparsity_frame(label, base):
        def _fn():
            _gv.set_run_seed(42)            # fix seed so positions are stable
            _gv.RUN_DENSITY_BASE = base     # override the derived base
            return render_scene(3, 0.05)
        return _fn
    _showcase(OUT / "_v3_sparsity_variation.png",
              "V3 sparsity per run (RUN_DENSITY_BASE)",
              [("very sparse (0.35)", _sparsity_frame("vs", 0.35)),
               ("sparse (0.55)",      _sparsity_frame("s",  0.55)),
               ("lush (0.80)",        _sparsity_frame("l",  0.80)),
               ("jungle (1.00)",      _sparsity_frame("j",  1.00))])

    # Within-run (during a single play): same RUN_SEED, scrolling forward
    def _within_run_frame(scroll_val):
        def _fn():
            _gv.set_run_seed(42)
            return render_scene(3, 0.05, scroll=scroll_val)
        return _fn
    _showcase(OUT / "_v3_within_run_variation.png",
              "V3 within one run (scrolling forward)",
              [(f"scroll {sv}", _within_run_frame(sv))
               for sv in (80, 1200, 2400, 3600)])

    sheet = make_contact_sheet(images)
    sheet_path = OUT / "_contact_sheet.png"
    pygame.image.save(sheet, sheet_path)
    print(f"wrote {sheet_path}")


if __name__ == "__main__":
    main()
