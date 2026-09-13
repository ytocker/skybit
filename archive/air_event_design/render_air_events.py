"""Render preview screenshots of the 8 air ambient events.

For each event, render a full W×H scene composite (sky + clouds +
mountains + ground + the event advanced to a representative animation
moment) at the event's preferred biome phase. Output goes to
``./screenshots/`` plus a 4×2 contact sheet.

Run from anywhere:
    python archive/air_event_design/render_air_events.py
"""
import os, sys, pathlib, math, random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE.parent.parent))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_cloud, draw_mountains,
)
from game import ambient as _amb
from game import ground_variants as _gv


# (slug, label, class, preview phase, animation t to use)
EVENTS = [
    ("a1_banner_plane",  "A1 Banner plane",         _amb._BannerPlane,       0.05, 5.5),
    ("a2_zeppelin",      "A2 Zeppelin",             _amb._Zeppelin,          0.35, 18.0),
    ("a3_eagle",         "A3 Gliding eagle",        _amb._GlidingEagle,      0.05, 5.5),
    ("a4_bats",          "A4 Bat swarm",            _amb._BatSwarm,          0.62, 4.0),
    ("a5_shooting_star", "A5 Shooting star",        _amb._ShootingStar,      0.62, 0.55),
    ("a6_rainbow",       "A6 Rainbow arc",          _amb._RainbowArc,        0.90, 4.5),
    ("a7_lanterns",      "A7 Lantern festival",     _amb._LanternFestival,   0.55, 7.0),
    ("a8_balloons",      "A8 Balloon cluster",      _amb._BalloonCluster,    0.10, 5.0),
]

OUT = _HERE / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)


def render_event_scene(event_cls, phase, anim_t) -> pygame.Surface:
    palette = _biome.palette_for_phase(phase)
    surf = pygame.Surface((W, H))

    # Sky
    bucket = int(phase * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
    sky.set_alpha(None)
    surf.blit(sky, (0, 0))

    # Clouds
    scroll = 80.0
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

    # Ground (a meadow variant for context)
    _gv.set_run_seed(7)
    _gv.VARIANTS[1](surf, GROUND_Y, W, H, scroll,
                    palette['ground_top'], palette['ground_mid'],
                    (60, 40, 25))

    # The event — let its constructor pick its own position, then advance
    # to anim_t by stepping its update loop at a fixed dt.
    rng = random.Random(0xCAFE)
    event = event_cls(palette, rng)
    dt = 1 / 60
    steps = max(1, int(anim_t / dt))
    for _ in range(steps):
        event.update(dt)
    event.draw(surf)

    return surf


def make_contact_sheet(images: dict) -> pygame.Surface:
    cols = 2
    rows = (len(EVENTS) + cols - 1) // cols
    thumb_w, thumb_h = W // 2, H // 2
    label_h = 22
    pad = 8
    sheet_w = pad + cols * (thumb_w + pad)
    sheet_h = pad + rows * (thumb_h + label_h + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 24, 28))

    font = pygame.font.SysFont(None, 16)
    for i, (slug, label, *_rest) in enumerate(EVENTS):
        r = i // cols
        c = i % cols
        full = images[slug]
        thumb = pygame.transform.smoothscale(full, (thumb_w, thumb_h))
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + label_h + pad)
        sheet.blit(thumb, (x, y))
        sheet.blit(font.render(label, True, (220, 220, 220)),
                   (x + 4, y + thumb_h + 4))
    return sheet


def main() -> None:
    for old in OUT.glob("*.png"):
        old.unlink()

    images: dict = {}
    for slug, label, cls, phase, anim_t in EVENTS:
        surf = render_event_scene(cls, phase, anim_t)
        images[slug] = surf
        out_path = OUT / f"{slug}.png"
        pygame.image.save(surf, out_path)
        print(f"wrote {out_path}")

    sheet = make_contact_sheet(images)
    sheet_path = OUT / "_contact_sheet.png"
    pygame.image.save(sheet, sheet_path)
    print(f"wrote {sheet_path}")


if __name__ == "__main__":
    main()
