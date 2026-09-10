"""BASEBALL — white sphere with the two red curved stitch seams.

The identity is white + the red STITCHING: two facing curved seams with little
red stitch ticks. It stays distinct from the soccer ball (which is white with
BLACK panels) because here the marks are thin RED curves, not black blocks.

Read tradeoffs (WHY): the two seams are parametric curves bowing apart down the
ball ("( )"), drawn as a red line with short perpendicular stitch ticks — a fussy
stitch count vanishes, so a few bold ticks per seam carry the "stitched" read.
Volume is baked like the other balls (outline, light->shade body, upper-left
highlight, lower-right shade). A cool keyline rim is the NIGHT lifeline.
"""
import math
import pygame

WHITE = (244, 242, 236)        # shell white — the bright body
WHITE_HI = (255, 255, 255)     # upper-left specular
SHADE = (206, 202, 192)        # lower-right shade
SHADE2 = (176, 172, 162)       # deep rim shade
STITCH = (210, 58, 48)         # red stitching — the signature
STITCH_D = (162, 38, 32)       # darker red for the seam line under the ticks
OUTLINE = (42, 38, 32)         # dark, drawn first + inflated: day read
KEYLINE = (150, 196, 232)      # cool rim — the NIGHT lifeline


# 6x supersample: all geometry below stays in the original 44px design space and
# is scaled UP to a 264px work surface, then smoothscaled DOWN to OUT. This is a
# pure resolution/AA bump over the old 44px(2x)->22px path — the two red seams,
# their stitch ticks and the sphere edge resolve cleanly instead of crawling.
# Output is bumped to 26px (a touch over PARCEL_SIZE, matching the coin / mini-pip
# convention) so the added crispness actually survives on-screen.
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
    pygame.draw.circle(surf, SHADE2, _p((cx, cy)), _s(R))
    pygame.draw.circle(surf, SHADE, _p((cx - 1, cy - 1)), _s(R - 1))
    pygame.draw.circle(surf, WHITE, _p((cx - 3, cy - 3)), _s(R - 3))

    seams = pygame.Surface((S, S), pygame.SRCALPHA)

    def _seam(side):
        # A vertical curve bowing toward `side` (-1 left, +1 right). Returns the
        # point list in DESIGN space; ticks read off the local tangent normal.
        off = side * R * 0.16
        bow = side * R * 0.62
        pts = []
        for i in range(0, 25):
            t = i / 24.0
            y = cy - (R - 2) + t * 2 * (R - 2)
            x = cx + off + bow * math.sin(t * math.pi)
            pts.append((x, y))
        return pts

    for side in (-1, 1):
        pts = _seam(side)
        pygame.draw.lines(seams, STITCH_D, False, [_p(pt) for pt in pts], _w(2))
        # Stitch ticks: short perpendicular dashes along the seam, alternating.
        for j in range(2, len(pts) - 2, 3):
            x, y = pts[j]
            px, py = pts[j - 1]
            dx, dy = x - px, y - py
            n = math.hypot(dx, dy) or 1
            nx, ny = -dy / n, dx / n           # normal
            k = 2.2 * (1 if (j // 3) % 2 == 0 else -1)
            pygame.draw.line(seams, STITCH,
                             _p((x - nx * k, y - ny * k)),
                             _p((x + nx * k * 0.3, y + ny * k * 0.3)), _w(1))

    smask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), _p((cx, cy)), _s(R - 2))
    seams.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(seams, (0, 0))

    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shade, (60, 56, 48, 70), _p((cx + 5, cy + 6)), _s(R))
    shmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shmask, (255, 255, 255, 255), _p((cx, cy)), _s(R - 1))
    shade.blit(shmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))

    hi = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hi, (255, 255, 255, 150), _p((cx - 5, cy - 6)), _s(4))
    pygame.draw.circle(hi, WHITE_HI, _p((cx - 6, cy - 7)), _s(2))
    hmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hmask, (255, 255, 255, 255), _p((cx, cy)), _s(R - 2))
    hi.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hi, (0, 0))

    pygame.draw.circle(surf, KEYLINE, _p((cx, cy)), _s(R), _w(1))
    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (OUT, OUT))
