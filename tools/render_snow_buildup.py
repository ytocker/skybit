"""Render the snow-on-Pip's-back accumulation across the squall:
the drift settles partway into the build, keeps growing a little
PAST the storm peak, then melts off as the storm passes. Simulates
the real integrator (storm_intensity + the world's accum/melt
model) so the captured loads are exactly what plays in-game.

Each panel = the full snowy scene at one moment, with a zoomed
inset of Pip's back so the drift detail is clear. Labels show
play-time / storm intensity / snow load.

Output: docs/screenshots/wind_themes/snow_back/buildup_sheet.png

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
      python -m tools.render_snow_buildup
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import (
    W, H, GROUND_Y, BIRD_X,
    WEATHER_SNOW_ACCUM_RATE as ACCUM,
    WEATHER_SNOW_MELT_BASE as MELT_BASE,
    WEATHER_SNOW_MELT_FADE as MELT_FADE,
)
from game.entities import Bird
from game.weather import Weather, storm_intensity
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground

pygame.init()
pygame.display.set_mode((W, H))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "wind_themes", "snow_back")
os.makedirs(OUT_DIR, exist_ok=True)

DT = 1 / 60.0
CY = _biome.CYCLE_SECONDS
START_PHASE = 0.73
BIRD_Y = H * 0.42

# Play-times (s, from phase 0.73) telling the accumulation story.
CAPTURES = [
    (28, "t=28s  settling"),
    (37, "t=37s  storm peak"),
    (44, "t=44s  MAX"),
    (54, "t=54s  fading starts"),
    (60, "t=60s  melting off"),
    (66, "t=66s  nearly gone"),
]


def render_scene(phase, load, weather):
    surf = pygame.Surface((W, H))
    pal = _biome.palette_for_phase(phase)
    bucket = int((phase % 1.0) * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    surf.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, bucket), (0, 0))
    draw_mountains(surf, 0, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    draw_ground(surf, GROUND_Y, W, H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    # In-game order: weather (cold wash + snow) draws first, then
    # the bird on top.
    weather.draw(surf)
    b = Bird()
    b.x = BIRD_X
    b.y = BIRD_Y
    b.snow_load = load
    b.draw(surf)
    return surf


def main():
    weather = Weather()
    load = 0.0
    want = {t: lbl for t, lbl in CAPTURES}
    shots = {}
    total_t = max(want) + 1.0
    t = 0.0
    k = 0
    while t <= total_t:
        phase = ((START_PHASE * CY + t) / CY) % 1.0
        weather.update(DT, phase)
        st = storm_intensity(phase)
        melt = MELT_BASE + MELT_FADE * (1.0 - st)
        load = max(0.0, min(1.0, load + (ACCUM * st - melt) * DT))
        sec = round(t)
        if sec in want and sec not in shots:
            scene = render_scene(phase, load, weather)
            shots[sec] = (scene, want[sec], st, load)
        t += DT
        k += 1

    # Compose a 3x2 contact sheet; each panel carries a zoomed
    # inset of Pip's back in the top-left corner.
    cols, rows = 3, 2
    margin = 12
    label_h = 26
    sheet_w = W * cols + margin * (cols + 1)
    sheet_h = (H + label_h) * rows + margin * (rows + 1)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 22, 30))
    font = pygame.font.SysFont("Arial", 13, bold=True)

    # Zoom region around Pip
    zw, zh, zf = 78, 70, 2.4
    for i, (t_lbl, _) in enumerate(CAPTURES):
        scene, lbl, st, load = shots[t_lbl]
        c = i % cols
        r = i // cols
        x = margin + c * (W + margin)
        y = margin + r * (H + label_h + margin)
        pygame.draw.rect(sheet, (60, 70, 95), (x - 2, y - 2, W + 4, H + 4), 2)
        sheet.blit(scene, (x, y))
        # zoomed inset of Pip
        crop = pygame.Surface((zw, zh))
        crop.blit(scene, (0, 0),
                  (int(BIRD_X - zw / 2), int(BIRD_Y - zh / 2), zw, zh))
        inset = pygame.transform.scale(crop, (int(zw * zf), int(zh * zf)))
        ix, iy = x + 6, y + 6
        pygame.draw.rect(sheet, (230, 240, 255),
                         (ix - 2, iy - 2, inset.get_width() + 4,
                          inset.get_height() + 4), 2)
        sheet.blit(inset, (ix, iy))
        full = font.render(f"{lbl}  storm={st:.2f} load={load:.2f}",
                           True, (235, 242, 250))
        sheet.blit(full, (x + (W - full.get_width()) // 2, y + H + 5))

    out = os.path.join(OUT_DIR, "buildup_sheet.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
