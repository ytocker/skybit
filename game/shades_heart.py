"""HEART SHADES (festival / Lolita) — playful heart-shaped lenses.

The heart silhouette IS the read, and it has to survive at eye_w=22 sitting on
a scarlet (240,55,55) head — where a pink-on-red lens is a near-zero value gap.
So the lens is built as a FILLED GOLD heart (ties to ROUND/MONOCLE's gold) and
the pink glass is inset by a BOLD gold rim band — never a stroke, which thins
out and drops the point at tiny radii. The rim is a fat fraction of the lens so
the lobed/pointed gold silhouette holds against the head, and the glass is a
COOLED, DARKENED rose→plum (not bright candy pink) so it reads as a separate
shape rather than smearing into the scarlet. Everything scales off `eye_w` so
the same code is a clean product shot at eye_w=96 and a legible heart at 22.
"""
import math

import pygame

_RIM    = (240, 200, 90)            # warm gold metal (matches ROUND/MONOCLE)
_RIM_H  = (255, 244, 184)           # bright top-lobe highlight
_RIM_D  = (176, 130, 44)            # underside / shadow side of the wire
# Cooled + darkened glass: a rose top sinking to plum, both well below the
# scarlet head in value and pushed toward blue so the lens separates from red.
_PINK_T = (236, 120, 168)           # cool rose top of the glass
_PINK_B = (150,  48, 118)           # deep plum floor (vertical fade)
_GLINT  = (255, 255, 255)


def _heart_points(cx, cy, r):
    """Polygon outline of a heart whose bounding span is ~2r wide, centred so
    (cx,cy) sits at the lens centre. Two lobe arcs sampled as points plus the
    bottom point — a polygon fills solidly at any size, where a curve stroke
    would thin out and drop pixels at the tip."""
    lobe_r = r * 0.50
    lobe_y = cy - r * 0.28
    lx = cx - r * 0.46
    rx = cx + r * 0.46
    tip = (cx, cy + r * 0.94)

    pts = []
    # Left lobe: sweep over the top-left arc from the valley up and around.
    for deg in range(210, 410, 12):
        a = math.radians(deg)
        pts.append((lx + lobe_r * math.cos(a), lobe_y + lobe_r * math.sin(a)))
    # Down the right shoulder of the right lobe into the tip.
    for deg in range(130, 330, 12):
        a = math.radians(deg)
        pts.append((rx + lobe_r * math.cos(a), lobe_y + lobe_r * math.sin(a)))
    pts.append(tip)
    return pts


def _tinted_heart(r, top, bot, alpha, rim):
    """Glass heart inset by `rim`, with a vertical top→bot fade so the flat
    fill reads as curved glass. The inset is uniform so the surrounding gold
    band is the same thickness all the way round, including at the point."""
    size = int(r * 2.4)
    g = pygame.Surface((size, size), pygame.SRCALPHA)
    grad = pygame.Surface((size, size), pygame.SRCALPHA)
    span = max(1, size - 1)
    for yy in range(size):
        t = yy / span
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t), alpha)
        pygame.draw.line(grad, c, (0, yy), (size, yy))
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    inner = max(2, r - rim)
    # The tip reaches further from centre than the lobes, so a uniform inset on
    # a centroid-aligned heart leaves a fat gold band only at the point. Drop
    # the glass centre slightly so the gold rim is even all the way around.
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        _heart_points(size / 2, size / 2 + rim * 0.55, inner))
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    g.blit(grad, (0, 0))
    return g, size


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    r    = max(4, int(eye_w * 0.27))
    sep  = max(4, int(eye_w * 0.46))
    # Wire thickness for the bridge/temple — thin metal, kept readable at 22px.
    wire = max(1, int(eye_w * 0.06))
    # Rim is a FAT band, not a stroke: a big fraction of the lens with a hard
    # floor so the gold heart silhouette survives downscaling to ~22px on red.
    rim  = max(2, int(r * 0.42))
    # The heart hangs its point below centre, so keep enough lift that the tip
    # stops short of the beak TIP — but ride the pair slightly FORWARD so the
    # near heart laps the beak base, the natural forward seat of glasses on a
    # face (don't retreat it off the beak entirely).
    cy   = cy - max(2, int(r * 0.48))
    near = (cx + f * (sep // 2) + f * max(1, int(eye_w * 0.03)), cy)
    far  = (cx - f * (sep // 2), cy)

    # Bridge BEHIND the lenses so the heart lobes overlap it cleanly; the
    # lower pass is the gold catch-light underside.
    bx0 = far[0] + f * int(r * 0.30)
    bx1 = near[0] - f * int(r * 0.30)
    by = cy - max(1, int(r * 0.30))
    pygame.draw.line(surf, _RIM_D, (bx0, by + 1), (bx1, by + 1), wire)
    pygame.draw.line(surf, _RIM, (bx0, by), (bx1, by), wire)

    # Temple wire toward the ear (-facing).
    ex = far[0] - f * (r + max(2, int(eye_w * 0.30)))
    ey = cy - max(1, int(eye_w * 0.10))
    pygame.draw.line(surf, _RIM_D, (far[0] - f * int(r * 0.6), cy), (ex, ey), wire)
    pygame.draw.line(surf, _RIM, (far[0] - f * int(r * 0.6), cy), (ex, ey),
                     max(1, wire - 1))

    for (lx, ly) in (far, near):
        # Solid gold heart = filled gold polygon (with a 1px-down shadow copy
        # for the wire underside), then the cooled glass heart inset so a bold
        # gold rim frames the lens on every side.
        pygame.draw.polygon(surf, _RIM_D, _heart_points(lx, ly + 1, r))
        pygame.draw.polygon(surf, _RIM, _heart_points(lx, ly, r))
        glass, gs = _tinted_heart(r, _PINK_T, _PINK_B, 226, rim)
        surf.blit(glass, (lx - gs // 2, ly - gs // 2))
        # Bright crescent over the two top lobes so the gold pops off the head.
        hi = max(1, int(rim * 0.45))
        pygame.draw.arc(surf, _RIM_H,
                        (lx - r * 0.96, ly - r * 0.78, r * 0.92, r * 0.92),
                        0.3, 2.9, hi)
        pygame.draw.arc(surf, _RIM_H,
                        (lx + r * 0.04, ly - r * 0.78, r * 0.92, r * 0.92),
                        0.3, 2.9, hi)

    # One pinprick glint on the near lens's left lobe — sells glossy glass.
    pygame.draw.circle(surf, _GLINT,
                       (int(near[0] - r * 0.30), int(cy - r * 0.26)),
                       max(1, int(eye_w * 0.05)))
