"""BASKETBALL — orange sphere with the black seam pattern parcel cosmetic.

The identity is basketball-orange crossed by the black SEAMS: a vertical
meridian, a horizontal equator, and the two bowed side seams (an 8-panel read).
Orange + the seam cross is unmistakable and survives grayscale because the seams
are near-black against a mid-value orange.

Read tradeoffs (WHY): the full curved-panel seam set aliases to mud, so the
seams commit to a vertical line + a horizontal line + ONE tall-narrow ellipse
whose left/right arcs read as the two bowed side seams — masked to the sphere so
they curve away at the rim. Volume is baked like the other balls: dark outline
first, a light->shade orange body, an upper-left highlight, a lower-right shade
crescent. A warm keyline rim is the NIGHT lifeline.
"""
import pygame

ORANGE = (224, 122, 34)        # basketball orange — the mid-value body
ORANGE_HI = (242, 162, 78)     # lit upper-left
ORANGE_SH = (168, 85, 26)      # lower-right shade
ORANGE_SH2 = (134, 64, 18)     # deep rim shade so the sphere turns
SEAM = (32, 26, 20)            # near-black seams — the signature
OUTLINE = (22, 18, 12)         # dark, drawn first + inflated: reads on day sky
KEYLINE = (250, 196, 120)      # warm rim — the NIGHT lifeline


# 6x supersample: all geometry below stays in the original 44px design space and
# is scaled UP to a 264px work surface, then smoothscaled DOWN to OUT. This is a
# pure resolution/AA bump over the old 44px(2x)->22px path — the seam cross, side
# arcs and sphere edge resolve cleanly instead of crawling. Output is bumped to
# 26px (a touch over PARCEL_SIZE, matching the coin / mini-pip convention) so the
# added crispness survives on-screen without growing the footprint.
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
    # Orange shell with baked volume.
    pygame.draw.circle(surf, ORANGE_SH2, _p((cx, cy)), _s(R))
    pygame.draw.circle(surf, ORANGE_SH, _p((cx - 1, cy - 1)), _s(R - 1))
    pygame.draw.circle(surf, ORANGE, _p((cx - 3, cy - 3)), _s(R - 3))

    # Seams on their own layer, MIN-masked to the sphere so the side arcs curve
    # away at the rim instead of running straight off the edge.
    seams = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.line(seams, SEAM, _p((cx - R, cy)), _p((cx + R, cy)), _w(2))   # equator
    pygame.draw.line(seams, SEAM, _p((cx, cy - R)), _p((cx, cy + R)), _w(2))   # meridian
    ew = R * 0.78
    pygame.draw.ellipse(seams, SEAM,                                            # side seams
                        pygame.Rect(_p((cx - ew, cy - R)),
                                    (_s(2 * ew), _s(2 * R))), _w(2))
    smask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), _p((cx, cy)), _s(R - 1))
    seams.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(seams, (0, 0))

    # Lower-right shade crescent over shell + seams for a unified sphere gradient.
    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shade, (60, 30, 8, 70), _p((cx + 5, cy + 6)), _s(R))
    shmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shmask, (255, 255, 255, 255), _p((cx, cy)), _s(R - 1))
    shade.blit(shmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))

    # Upper-left specular highlight.
    hi = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hi, (255, 232, 190, 150), _p((cx - 5, cy - 6)), _s(4))
    pygame.draw.circle(hi, ORANGE_HI, _p((cx - 6, cy - 7)), _s(2))
    hmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hmask, (255, 255, 255, 255), _p((cx, cy)), _s(R - 2))
    hi.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hi, (0, 0))

    pygame.draw.circle(surf, KEYLINE, _p((cx, cy)), _s(R), _w(1))
    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (OUT, OUT))
