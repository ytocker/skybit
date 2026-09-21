"""Chapter filmstrips for the weekend sidewalk build.

Dev-only — renders one real game frame per chapter checkpoint of the weekend
day (sky, mountains, floor, ground weather, promenade, pillars, near lane +
living crowd), so the day's story can be reviewed as stills.

    SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/weekend_filmstrips.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y, PIPE_W              # noqa: E402
from game import biome as _biome                            # noqa: E402
from game import foreground                                 # noqa: E402
from game import foreground_promenade as pr                 # noqa: E402
from game.sidewalk_crowd import SidewalkCrowd               # noqa: E402
from tools._family_showcase import (_build_background, _draw_pillars,  # noqa: E402
                                    _gold_coin, _font)

CYCLE = 393.5
_PILLAR_SPACING = 341        # measured steady-state pillar pitch

# (t, chapter label, extra signal overrides)
CHECKPOINTS = [
    (10.0,  "CH1  shutters up (calm opening)", {}),
    (35.0,  "CH2  morning market peak", {}),
    (110.0, "CH3  the long middle (authored floor)", {}),
    (156.0, "CH4  golden refill — the median frame", {}),
    (178.0, "CH5  lamps & market setup (carts)", {}),
    (205.0, "CH6  first umbrellas (drizzle)", {}),
    (247.0, "CH7  storm peak — tarps + suoyi", {}),
    (282.0, "CH8a NIGHT MARKET — first crest", {}),
    (296.0, "CH8b Monkey King troupe (second crest)", {}),
    (303.0, "CH8c THE LION — self-contained troupe", {}),
    (316.0, "CH8d THE DRAGON — parade, first flakes", {}),
    (342.0, "CH9  small hours — winter dress, snow", {}),
    (372.0, "CH10 first light — tea + the sweeper", {}),
]


def _wetness(t):
    if 197.0 <= t <= 273.3:
        return min(1.0, (t - 197.0) / 18.0)
    if t > 273.3:
        return max(0.0, 1.0 - (t - 273.3) * 0.18)
    return 0.0


def _snow_cover(t):
    if t < 320.0:
        return 0.0
    cover = min(1.0, (t - 320.0) / 23.0)
    if t > 358.5:
        cover = max(0.0, cover - (t - 358.5) * 0.08)
    return cover


def _frame(t, extra):
    phase = (t / CYCLE) % 1.0
    scroll = t * 160.0
    foreground.reset_street()
    crowd = SidewalkCrowd()
    foreground.set_crowd(crowd)
    # The prayer-flag row hangs between gameplay pillars, which this harness
    # does not simulate — without anchors the sheet would show a bare sky and
    # misrepresent the build. Synthesise a steady-state pillar row (the measured
    # 341px spacing) so the daytime frames show the bunting as it really ships.
    first = int((scroll - 400) // _PILLAR_SPACING)
    anchors = tuple((k * _PILLAR_SPACING,
                     int(k * _PILLAR_SPACING - scroll) + PIPE_W // 2)
                    for k in range(first, first + int((W + 800) / _PILLAR_SPACING) + 2))
    sig = dict(clown_active=False, newbie_calm=t < 19.0, score=int(t),
               near_misses=0, finale_active=False, pillar_anchors=anchors,
               wetness=_wetness(t), snow_cover=_snow_cover(t))
    sig.update(extra)
    foreground.set_world_signals(**sig)
    # settle the living crowd + behaviors into this moment
    sc = scroll - 25.0 * 160.0
    for i in range(25 * 30):
        sc += 160.0 / 30.0
        crowd.update(sc, 160.0, 1.0 / 30.0, phase, t - 25.0 + i / 30.0)
    surf = pygame.Surface((W, H))
    # Warm-up renders: the first pass fills the light-spot collector for the
    # ground-weather mirror AND primes the slot latches — a cold latch state
    # shifts ~1-2% of cast pixels vs what actually ships, so the sheet must
    # show the steady state, not the first frame. Two discarded full passes
    # settle both lanes.
    pal = _biome.palette_for_phase(phase)
    for _ in range(2):
        foreground.draw_promenade(surf, scroll, pal, phase, t)
        foreground.draw_near_lane(surf, scroll, pal, phase, t)
    surf.fill((0, 0, 0))
    # the real frame, in the play scene's order
    _build_background_pre(surf, scroll, phase, t, sig)
    _draw_pillars(surf, pal, phase, [(236, 300, 168)])
    _gold_coin(surf, 168, 300)
    foreground.draw_near_lane(surf, scroll, pal, phase, t)
    return surf


def _build_background_pre(surf, scroll, phase, t, sig):
    """The showcase background, with the ground-weather pass inserted between
    the floor and the promenade exactly as scenes.PlayScene draws it."""
    pal = _biome.palette_for_phase(phase)
    # sky + clouds + mountains + floor come from the showcase helper — but it
    # also draws the promenade, so replicate its order with weather in between.
    import tools._family_showcase as fs
    from game.draw import get_sky_surface_biome, draw_cloud, draw_mountains
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    b = (a + 1) % buckets
    tt = bucket_f - int(bucket_f)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, _biome.palette_for_phase(a / buckets), a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, _biome.palette_for_phase(b / buckets), b)
    sky_a.set_alpha(None)
    surf.blit(sky_a, (0, 0))
    if tt > 0:
        sky_b.set_alpha(int(tt * 255))
        surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)
    for i, (bx, by, sc_) in enumerate(fs._CLOUD_SLOTS):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(0.3 * i) * 3, sc_, variant=0, palette=pal)
    draw_mountains(surf, scroll, GROUND_Y, W, phase=phase)
    foreground.draw_foreground_floor(surf, scroll, pal, phase)
    foreground.draw_ground_weather(surf, scroll, pal, sig["wetness"], sig["snow_cover"])
    foreground.draw_promenade(surf, scroll, pal, phase, t)


def main():
    scale = 0.8
    fw, fh = int(W * scale), int(H * scale)
    cols, rows = 3, 5
    gap, head, foot = 8, 46, 26
    sheet = pygame.Surface((cols * fw + (cols + 1) * gap,
                            head + rows * (fh + foot + gap) + gap))
    sheet.fill((8, 8, 20))
    f = _font(15, bold=True)
    sheet.blit(f.render("THE TOWN IS HAVING A WEEKEND — chapter filmstrips (live build)",
                        True, (228, 224, 214)), (gap + 4, 14))
    lf = _font(11)
    for i, (t, label, extra) in enumerate(CHECKPOINTS):
        frame = pygame.transform.smoothscale(_frame(t, extra), (fw, fh))
        cx = gap + (i % cols) * (fw + gap)
        cy = head + (i // cols) * (fh + foot + gap)
        sheet.blit(frame, (cx, cy))
        pygame.draw.rect(sheet, (70, 70, 90), (cx, cy, fw, fh), 1)
        sheet.blit(lf.render(f"t={t:.0f}s  ·  {label}", True, (196, 200, 210)),
                   (cx + 2, cy + fh + 5))
        print(f"rendered t={t:.0f}s {label}")
    out = "docs/sidewalk_overhaul/filmstrips/weekend_chapters.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
