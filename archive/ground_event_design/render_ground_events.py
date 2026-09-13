"""Render preview screenshots of the 9 ground ambient events.

For each event, render a full W×H scene composite (sky + clouds +
mountains + ground + the event force-spawned at screen-center) at the
event's preferred biome phase. Output goes to ``./screenshots/`` plus a
contact sheet.

Run from anywhere:
    python archive/ground_event_design/render_ground_events.py
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
    get_sky_surface_biome, draw_cloud, draw_mountains, draw_ground,
)
from game import ambient as _amb
from game import ground_variants as _gv


# (slug, label, class, preview phase, animation t to use)
EVENTS = [
    ("g01_sheep",      "G1 Sheep pack",         _amb._SheepPack,     0.05, 0.4),
    ("g02_rabbits",    "G2 Rabbit hop trio",    _amb._RabbitHop,     0.90, 0.18),
    ("g03_fox",        "G3 Sleeping fox",       _amb._SleepingFox,   0.35, 1.1),
    ("g05_well",       "G5 Wishing well",       _amb._WishingWell,   0.05, 0.6),
    ("g06_scarecrow",  "G6 Scarecrow",          _amb._Scarecrow,     0.18, 1.7),
    ("g08_mushring",   "G8 Fairy mushroom ring", _amb._MushroomRing, 0.82, 0.7),
    ("g11_bench",      "G11 Bench (2 people)",  _amb._Bench,         0.05, 1.0),
    ("g12_napper",     "G12 Napping person",    _amb._Napper,        0.05, 1.3),
    ("g13_dog",        "G13 Running dog",       _amb._RunningDog,    0.05, 0.06),
]

OUT = _HERE / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)


def render_event_scene(event_cls, phase, anim_t, ground_variant=1) -> pygame.Surface:
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

    # Ground (V1 meadow) — keeps grass + flowers under the event for context
    _gv.set_run_seed(7)
    _gv.VARIANTS[ground_variant](surf, GROUND_Y, W, H, scroll,
                                 palette['ground_top'], palette['ground_mid'],
                                 (60, 40, 25))

    # The event itself, force-spawned at screen-centre
    rng = random.Random(0xCAFE)
    event = event_cls(palette, rng)
    event.x = float(W // 2)
    event.t = anim_t
    event.draw(surf)

    return surf


def make_contact_sheet(images: dict) -> pygame.Surface:
    cols = 3
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
