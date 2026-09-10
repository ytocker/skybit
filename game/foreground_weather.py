"""Weather ON the sidewalk — the ground-state overlay that makes the paving react.

Drawn in the foreground stack BETWEEN the cached floor strip and the living
promenade, so a wet glaze or a snow frosting sits on the paving UNDER the crowd's
feet (the falling rain + the splashes it kicks up are a separate, in-front layer
in `weather.Weather.draw`).

Two ground states, both driven by the persistent weather accumulators so they lag
the raw envelope (soak/dry, settle/melt) rather than strobe with it:

  * wetness    (weather.Weather.wetness, 0..1) — a cool sheen darkening the band
    plus world-anchored puddles with a faint specular rim and a rain-fed ripple.
  * snow_cover (weather.Weather.snow_cover, 0..1) — a white rim along the top lip
    plus a settling scatter of frost, the same source-of-truth that buries Pip.

Everything is world-anchored to `scroll` so puddles + frost ride the ground, and
everything composites through ONE band-sized SRCALPHA overlay so the whole
reactive layer costs a single blit. Pure-Pygame / pygbag-safe (fill, blit,
draw.* into an SRCALPHA surface only).
"""
from __future__ import annotations

import pygame

from game.config import W, H, GROUND_Y
from game.foreground_props import _world_xs, GROUND_MULT

# The reactive layer paints into this band-local overlay (y=0 maps to GROUND_Y),
# then blits once. Reused every frame so no per-frame allocation.
_BAND_H = H - GROUND_Y
_OVERLAY = pygame.Surface((W, _BAND_H), pygame.SRCALPHA)


def _wet_sheen(ov, wetness):
    """A cool, semi-transparent darkening of the whole band — the soaked-paving
    read. Alpha tracks wetness; capped well under opaque so the running-bond
    texture still shows through the glaze."""
    a = int(72 * wetness)
    if a <= 0:
        return
    # A deep slate-blue wash; darker + bluer than the buff stone so it reads wet,
    # not merely shadowed.
    ov.fill((34, 46, 66, a))


def _puddles(ov, scroll, wetness):
    """World-anchored puddles that pool in the downpour and fade as it dries. Each
    is a dark reflective ellipse with a faint specular rim; the bigger ones catch
    a slow rain-fed ripple. Held back until the rain is genuinely heavy so a light
    shower only damps the stone."""
    # Puddles only read once the ground is properly soaked; ramp their presence
    # across the upper half of the wetness range so they pool in, not pop in.
    pud = max(0.0, (wetness - 0.45) / 0.55)
    if pud <= 0.01:
        return
    ticks = pygame.time.get_ticks() / 1000.0
    for sx, k in _world_xs(scroll, W, 132, x0=28, mult=GROUND_MULT, margin=60):
        h = (k * 0x9E3779B1) & 0xFFFFFFFF
        # Skip ~a third of slots so puddles read scattered, not a regular row.
        if (h & 7) < 3:
            continue
        pw = 26 + (h >> 3 & 31)                 # 26..57 px wide
        ph = 5 + (h >> 8 & 3)                   # 5..8 px tall (flattened by perspective)
        # Lower in the band (nearer the camera), jittered per slot.
        cy = 18 + (h >> 11 & 15)                # band-local centre y
        a = int(150 * pud)
        rect = (int(sx - pw / 2), int(cy - ph / 2), pw, ph)
        pygame.draw.ellipse(ov, (22, 30, 44, a), rect)
        # Specular rim — a brighter top arc where the sky reflects off the water.
        pygame.draw.ellipse(ov, (120, 140, 172, int(a * 0.6)), rect, 1)
        # A slow expanding ripple ring on the wider puddles — rain landing in it.
        if pw >= 40:
            rt = (ticks * 0.8 + (h >> 4 & 7) * 0.4) % 1.0
            rr = 2 + rt * (pw * 0.32)
            ra = int(90 * pud * (1.0 - rt))
            if ra > 0:
                pygame.draw.ellipse(
                    ov, (140, 158, 188, ra),
                    (int(sx - rr), int(cy - rr * ph / pw),
                     int(rr * 2), max(1, int(rr * 2 * ph / pw))), 1)


def _snow_dusting(ov, scroll, snow_cover):
    """A white frosting that settles on the paving during the squall and melts
    after. A bright rim along the top lip (where snow piles against the kerb)
    plus a world-anchored scatter of settled frost; alpha + density ramp with
    snow_cover but stay a frosting, never a whiteout that hides the stone."""
    a_rim = int(180 * snow_cover)
    if a_rim > 0:
        # Frost banked along the sidewalk's top edge — brightest, where it gathers.
        pygame.draw.rect(ov, (236, 242, 250, a_rim), (0, 0, W, 2))
        pygame.draw.rect(ov, (220, 230, 244, int(a_rim * 0.6)), (0, 2, W, 2))
    # Settled frost patches across the band — more of them as cover builds.
    a_patch = int(150 * snow_cover)
    if a_patch <= 0:
        return
    for sx, k in _world_xs(scroll, W, 26, x0=10, mult=GROUND_MULT, margin=40):
        h = (k * 0x85EBCA77) & 0xFFFFFFFF
        # Gate patches in by cover so the band frosts up gradually, slot by slot.
        if (h & 0xFF) / 255.0 > snow_cover:
            continue
        pw = 4 + (h >> 8 & 7)                   # 4..11 px
        cy = 3 + (h >> 12 & 31) % _BAND_H       # band-local y
        pygame.draw.ellipse(ov, (240, 246, 252, a_patch),
                            (int(sx - pw / 2), int(cy), pw, 2 + (h >> 5 & 1)))


def draw_ground_weather(surf, scroll, pal, wetness, snow_cover):
    """Paint the reactive ground state (wet sheen + puddles, snow dusting) into the
    sidewalk band, world-anchored to `scroll`. A no-op in clear weather."""
    if wetness <= 0.01 and snow_cover <= 0.01:
        return
    _OVERLAY.fill((0, 0, 0, 0))
    if wetness > 0.01:
        _wet_sheen(_OVERLAY, wetness)
        _puddles(_OVERLAY, scroll, wetness)
    if snow_cover > 0.01:
        _snow_dusting(_OVERLAY, scroll, snow_cover)
    surf.blit(_OVERLAY, (0, GROUND_Y))
