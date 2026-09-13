"""AMERICAN FOOTBALL — brown prolate ball with white laces parcel cosmetic.

The only non-round ball, so it wins on SILHOUETTE: a pointed brown oval. The
identity is that oval + the white LACES across the centre and the white end
STRIPES near each tip. Brown + the lace marks reads "gridiron" at a glance and
the oval keeps it distinct from every round ball at true size.

22px read tradeoffs (WHY): the ball is a horizontal ellipse (pointed ends), with
volume baked the same way as the spheres (dark outline, light->shade body,
upper-left highlight). The laces are a short white bar with a few cross-ticks —
fussy stitching vanishes, so a few bold ticks carry it — flanked by two short
white end stripes. A warm keyline rim is the NIGHT lifeline.
"""
import pygame

BROWN = (138, 84, 42)          # pigskin brown — the body
BROWN_HI = (176, 116, 64)      # lit upper-left
BROWN_SH = (96, 54, 24)        # lower-right shade
BROWN_SH2 = (74, 40, 16)       # deep rim shade
LACE = (242, 238, 226)         # white laces + end stripes — the signature
LACE_SH = (190, 184, 168)      # lace shadow
OUTLINE = (40, 22, 10)         # dark, drawn first + inflated: day read
KEYLINE = (236, 196, 140)      # warm rim — the NIGHT lifeline


# 6x supersample: all geometry below stays in the original 44px design space and
# is scaled UP to a 264px work surface, then smoothscaled DOWN to OUT. This is a
# pure resolution/AA bump over the old 44px(2x)->22px path — the pointed-oval
# edge, the white laces and end stripes resolve crisply instead of crawling.
# Output is bumped to 26px (a touch over PARCEL_SIZE, matching the coin /
# mini-pip convention) so the added crispness survives on-screen without growing
# the footprint.
DES = 44                          # original design coordinate space (unchanged)
OUT = 26
SS  = 6
S   = DES * SS                    # 264px work surface


def _s(v):  return v * SS
def _p(pt): return (pt[0] * SS, pt[1] * SS)
def _w(v):  return max(1, int(round(v * SS)))


def _ell(surf, color, cx, cy, rx, ry, width=0):
    # Geometry authored in 44px space; scale the bounding box to the SS surface.
    rect = pygame.Rect(_s(cx - rx), _s(cy - ry), _s(rx * 2), _s(ry * 2))
    if width:
        pygame.draw.ellipse(surf, color, rect, _w(width))
    else:
        pygame.draw.ellipse(surf, color, rect)


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    # All geometry below is authored in the original 44px space; _s/_p scale to SS.
    cx = cy = DES / 2
    RX, RY = 17, 11               # prolate: wider than tall, held off the edges

    # Outline (inflated ellipse) for the DAY silhouette read.
    _ell(surf, OUTLINE, cx, cy, RX + 2, RY + 2)
    # Brown body with baked volume (concentric offset ellipses lit up-left).
    _ell(surf, BROWN_SH2, cx, cy, RX, RY)
    _ell(surf, BROWN_SH, cx - 1, cy - 1, RX - 1, RY - 1)
    _ell(surf, BROWN, cx - 2, cy - 2, RX - 3, RY - 3)

    marks = pygame.Surface((S, S), pygame.SRCALPHA)
    # Two short white END STRIPES near each pointed tip.
    pygame.draw.line(marks, LACE, _p((cx - RX + 4, cy - 4)), _p((cx - RX + 4, cy + 4)), _w(2))
    pygame.draw.line(marks, LACE, _p((cx + RX - 4, cy - 4)), _p((cx + RX - 4, cy + 4)), _w(2))
    # Central LACES: a short horizontal white bar + cross-ticks.
    pygame.draw.line(marks, LACE_SH, _p((cx - 6, cy + 1)), _p((cx + 6, cy + 1)), _w(3))
    pygame.draw.line(marks, LACE, _p((cx - 6, cy)), _p((cx + 6, cy)), _w(2))
    for lx in range(-5, 7, 3):
        pygame.draw.line(marks, LACE, _p((cx + lx, cy - 2)), _p((cx + lx, cy + 2)), _w(1))
    mmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.ellipse(mmask, (255, 255, 255, 255),
                        pygame.Rect(_s(cx - RX + 1), _s(cy - RY + 1),
                                    _s((RX - 1) * 2), _s((RY - 1) * 2)))
    marks.blit(mmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(marks, (0, 0))

    # Lower-right shade for a unified gradient.
    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    _ell(shade, (50, 26, 8, 70), cx + 4, cy + 4, RX, RY)
    shmask = pygame.Surface((S, S), pygame.SRCALPHA)
    _ell(shmask, (255, 255, 255, 255), cx, cy, RX - 1, RY - 1)
    shade.blit(shmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))

    # Upper-left highlight.
    hi = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hi, (200, 150, 100, 140), _p((cx - 6, cy - 5)), _s(4))
    pygame.draw.circle(hi, BROWN_HI, _p((cx - 7, cy - 5)), _s(2))
    hmask = pygame.Surface((S, S), pygame.SRCALPHA)
    _ell(hmask, (255, 255, 255, 255), cx, cy, RX - 2, RY - 2)
    hi.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hi, (0, 0))

    _ell(surf, KEYLINE, cx, cy, RX, RY, width=1)
    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (OUT, OUT))
