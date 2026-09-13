"""Compare the clown-event "staff" gauntlet across horizontal spacings.

Renders ONE fixed (seeded) warren route at several centre-to-centre tower
spacings so the only variable between panels is the horizontal gap, then
stacks them into a single labelled figure for picking a value. Static figure
only — it places the staff Pipes directly and does NOT go through the live
passability gate (which is irrelevant to a still image).
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import random

import pygame

from game.config import W, H, GROUND_Y, PIPE_W, BIRD_X
from game.draw import get_sky_surface_biome, draw_mountains
from game import foreground
from game import biome as _biome
from game.entities import Pipe
from game.clown_routes import build_clown_route

# Original (72) + the just-picked value (58) + five more, ascending.
SPACINGS = [40, 48, 54, 58, 64, 72, 84]
NOTES = {58: "JUST PICKED", 72: "ORIGINAL / CURRENT"}

PANEL_W = 800          # wide enough to show the whole cluster at 84 px
N_TOWERS = 9           # towers per panel (held constant across spacings)
X0 = 48                # first tower centre
PHASE = 0.12           # daytime — the clown event plays during the day block
ROUTE_SEED = 7         # fixed so every panel shows the SAME route shape
SCALE = 0.75           # downscale each panel so the stacked figure stays sane
GAP = 8                # px between stacked panels


def _palette_and_bucket(phase):
    buckets = _biome.PHASE_BUCKETS
    bucket = int(phase * buckets) % buckets
    return _biome.palette_for_phase(bucket / buckets), bucket


def _render_panel(route, spacing, pal, bucket, font):
    panel = pygame.Surface((PANEL_W, H))
    sky = get_sky_surface_biome(PANEL_W, H, GROUND_Y, pal, bucket)
    sky.set_alpha(None)
    panel.blit(sky, (0, 0))
    draw_mountains(panel, 0, GROUND_Y, PANEL_W, phase=PHASE)
    foreground.draw_foreground_floor(panel, 0, pal, PHASE)

    # Place the staff towers left→right at the test spacing. Deterministic
    # per-tower seed so the towers are byte-identical between panels and only
    # their x positions differ.
    for i in range(N_TOWERS):
        cy, gap_h = route[i]
        x = X0 + i * spacing
        p = Pipe(float(x), float(cy), int(gap_h))
        p.is_staff = True
        p.seed = 1000 + i
        p.draw(panel, palette=pal, phase=PHASE)

    panel = pygame.transform.smoothscale(
        panel, (int(PANEL_W * SCALE), int(H * SCALE)))

    # Label bar.
    edge = spacing - PIPE_W
    rel = f"overlap {-edge}" if edge < 0 else (f"gap {edge}" if edge > 0
                                               else "touching")
    text = f"{spacing} px  ({rel})"
    if spacing in NOTES:
        text += f"  —  {NOTES[spacing]}"
    bar = pygame.Surface((panel.get_width(), 30), pygame.SRCALPHA)
    bar.fill((12, 12, 18, 200))
    panel.blit(bar, (0, 0))
    panel.blit(font.render(text, True, (255, 235, 140)), (10, 5))
    return panel


def main():
    pygame.init()
    pygame.display.set_mode((PANEL_W, H))
    font = pygame.font.Font(None, 28)

    route = build_clown_route(N_TOWERS, random.Random(ROUTE_SEED))
    pal, bucket = _palette_and_bucket(PHASE)

    panels = [_render_panel(route, sp, pal, bucket, font) for sp in SPACINGS]

    pw = panels[0].get_width()
    ph = panels[0].get_height()
    fig = pygame.Surface((pw, len(panels) * ph + (len(panels) - 1) * GAP))
    fig.fill((20, 20, 26))
    for i, panel in enumerate(panels):
        fig.blit(panel, (0, i * (ph + GAP)))

    out_dir = os.path.join("docs", "clown_gap_sweep")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "sweep.png")
    pygame.image.save(fig, out)
    print(f"wrote {out}  size={fig.get_size()}  route={route}")


if __name__ == "__main__":
    main()
