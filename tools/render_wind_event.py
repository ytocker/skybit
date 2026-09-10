"""Render a 6-panel contact sheet of the predawn headwind event:
phases 0.72 (pre-event calm), 0.78 (building), 0.83 (climax),
0.85 (peak), 0.90 (fading), 0.95 (event ends). Saved to
docs/screenshots/wind_event_sequence.png.

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_wind_event
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import random
import pygame
pygame.init()
pygame.display.set_mode((360, 640))

random.seed(7)

from game.config import W, H, GROUND_Y, SCROLL_BASE
from game.world import World
from game.weather import wind_intensity as _wind_intensity
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground


OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)


def render(w, target):
    pal = _biome.palette_for_phase(w.biome_phase)
    buckets = _biome.PHASE_BUCKETS
    a = int((w.biome_phase % 1.0) * buckets) % buckets
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal, a)
    target.blit(sky, (0, 0))
    draw_mountains(target, 0, GROUND_Y, W,
                   pal["mtn_far"], pal["mtn_near"])
    draw_ground(target, GROUND_Y, W, H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    w.bird.draw(target, flipped=False)
    w.weather.draw(target)


def setup_world(phase):
    """World pre-warmed to the given biome phase with a fresh
    Pip pinned at his hover height + the weather pre-populated."""
    w = World()
    w.ready_t = 0
    w.biome_time = _biome.CYCLE_SECONDS * phase
    w.weather.phase = w.biome_phase
    # Bird at the canonical hover position
    w.bird.y = H * 0.42
    w.bird.vy = 0
    # Warm the weather particle pools so streaks/leaves are
    # already in motion at the captured moment
    for _ in range(120):
        w.weather.update(1 / 60.0, w.biome_phase)
    # Apply the wind effect (sets bird.wind_lean)
    w._apply_weather_effects(1 / 60.0)
    return w


def main():
    panels = []
    labels = []
    phases = (
        (0.72, "0.72  pre-event calm"),
        (0.78, "0.78  building (~22%)"),
        (0.83, "0.83  near peak (~85%)"),
        (0.85, "0.85  PEAK TAILWIND"),
        (0.90, "0.90  fading (~50%)"),
        (0.95, "0.95  event ends"),
    )
    for phase, label in phases:
        w = setup_world(phase)
        wi = _wind_intensity(w.biome_phase)
        scroll = w._current_scroll() / SCROLL_BASE
        # Pin the bird back in case _apply_weather_effects nudged
        # anything (it's visual-only so this is paranoia).
        surf = pygame.Surface((W, H))
        render(w, surf)
        panels.append(surf)
        labels.append(
            f"{label}  |  wind={wi:.2f}  scroll={scroll:.2f}×  "
            f"lean={w.bird.wind_lean:+.1f}px"
        )

    # 3 cols x 2 rows
    cols, rows = 3, 2
    margin = 12
    label_h = 30
    sheet_w = W * cols + margin * (cols + 1)
    sheet_h = (H + label_h) * rows + margin * (rows + 1) + label_h
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 24, 32))
    font = pygame.font.SysFont("Arial", 13, bold=True)
    for i, (panel, lab) in enumerate(zip(panels, labels)):
        col = i % cols
        row = i // cols
        x = margin + col * (W + margin)
        y = margin + row * (H + label_h + margin)
        pygame.draw.rect(sheet, (60, 65, 80),
                         (x - 2, y - 2, W + 4, H + 4), 2)
        sheet.blit(panel, (x, y))
        text = font.render(lab, True, (240, 240, 245))
        sheet.blit(text, (x + (W - text.get_width()) // 2,
                          y + H + 4))
    out = os.path.join(OUT_DIR, "wind_event_sequence.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
