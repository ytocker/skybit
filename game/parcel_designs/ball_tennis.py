"""TENNIS BALL — neon yellow-green sphere with the white curved seam.

The identity is the neon tennis colour plus the single signature white SEAM that
wavers down the ball like a stretched S. The colour alone reads "tennis", and the
white curve confirms it; both survive grayscale because the white seam is the
brightest mark on a mid-value body.

Read tradeoffs (WHY): the seam is built as a wavy vertical polyline (a sine down
the ball) rather than fussy facet curves, so one bold committed S-curve carries
the read. A 1px darker green shadow rides under the white so the seam reads
recessed. Volume is baked like the other balls (outline, light->shade body,
upper-left highlight, lower-right shade). A cool keyline rim is the NIGHT lifeline.
"""
import math
import pygame

YEL = (206, 226, 70)           # neon tennis yellow-green — the body
YEL_HI = (230, 244, 120)       # lit upper-left
YEL_SH = (158, 184, 50)        # lower-right shade
YEL_SH2 = (120, 144, 36)       # deep rim shade
SEAM = (244, 247, 232)         # white seam — the signature curve
SEAM_SH = (120, 144, 36)       # darker green shadow under the seam
OUTLINE = (58, 68, 20)         # dark olive, drawn first + inflated: day read
KEYLINE = (210, 236, 150)      # cool rim — the NIGHT lifeline


# 6x supersample: all geometry below stays in the original 44px design space and
# is scaled UP to a 264px work surface, then smoothscaled DOWN to OUT. This is a
# pure resolution/AA bump over the old 44px(2x)->22px path — the sphere edge and
# especially the wavy sine SEAM resolve as a smooth curve instead of a stairstep.
# Output is bumped to 26px (a touch over PARCEL_SIZE, matching the coin / mini-pip
# convention) so the added crispness survives on-screen without growing footprint.
DES = 44                          # original design coordinate space (unchanged)
OUT = 26
SS  = 6
S   = DES * SS                    # 264px work surface


def _s(v):  return v * SS
def _p(pt): return (pt[0] * SS, pt[1] * SS)
def _w(v):  return max(1, int(round(v * SS)))


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    # All geometry below is authored in the original 44px space; _s/_p scale to SS.
    cx = cy = DES / 2
    R = 16

    pygame.draw.circle(surf, OUTLINE, _p((cx, cy)), _s(R + 2))
    pygame.draw.circle(surf, YEL_SH2, _p((cx, cy)), _s(R))
    pygame.draw.circle(surf, YEL_SH, _p((cx - 1, cy - 1)), _s(R - 1))
    pygame.draw.circle(surf, YEL, _p((cx - 3, cy - 3)), _s(R - 3))

    # White seam: a wavy vertical line (sine down the ball), masked to the sphere.
    # Sampled densely at high res so the S-curve is a smooth arc, not facets.
    seams = pygame.Surface((S, S), pygame.SRCALPHA)
    amp = R * 0.62
    pts = []
    N = 240
    for i in range(0, N + 1):
        t = i / float(N)                  # 0..1 top->bottom
        y = cy - R + t * 2 * R
        x = cx + amp * math.sin(t * math.pi * 2 - math.pi / 2)
        pts.append((x, y))
    pygame.draw.lines(seams, SEAM_SH, False,
                      [_p((p[0] + 1, p[1] + 1)) for p in pts], _w(3))
    pygame.draw.lines(seams, SEAM, False, [_p(p) for p in pts], _w(3))
    smask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), _p((cx, cy)), _s(R - 2))
    seams.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(seams, (0, 0))

    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shade, (40, 50, 12, 70), _p((cx + 5, cy + 6)), _s(R))
    shmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shmask, (255, 255, 255, 255), _p((cx, cy)), _s(R - 1))
    shade.blit(shmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))

    hi = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hi, (240, 250, 180, 150), _p((cx - 5, cy - 6)), _s(4))
    pygame.draw.circle(hi, YEL_HI, _p((cx - 6, cy - 7)), _s(2))
    hmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hmask, (255, 255, 255, 255), _p((cx, cy)), _s(R - 2))
    hi.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hi, (0, 0))

    pygame.draw.circle(surf, KEYLINE, _p((cx, cy)), _s(R), _w(1))
    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (OUT, OUT))
