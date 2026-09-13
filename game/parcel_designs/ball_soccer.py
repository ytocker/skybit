"""SOCCER BALL — the universal football parcel cosmetic.

A white sphere wearing the classic black PENTAGON patches: one panel facing
square-on near the centre and a ring of partial pentagons biting in from the
sphere's edge. That black-on-white pentagon pattern IS the identity — no other
parcel is a white sphere blocked out in hard black panels — so the read lands
before colour even matters, which is what keeps it alive under grayscale.

22px read tradeoffs (WHY): a true geodesic 32-panel grid aliases to grey mud at
this size, so the ball commits to a FEW bold pentagons instead — one centred
hero panel plus four partial ones poked in from the rim. Each panel is a flat
filled polygon (no seam strokes, which vanish), and the partials are clipped to
the sphere so they read as patches curving away rather than floating shapes. The
sphere's volume is sold the same way the coconut is: a baked dark outline first
for the DAY read, a light->shade body so it never flattens to a disc, a soft
upper-left highlight, and a lower-right shade crescent. White vs panel-black is
the widest value step available, so the pattern survives the rotozoom and the
grayscale swatch. A cool keyline rim inside the outline is the NIGHT lifeline,
and the whole ball is held off the surface edges so panels never clip under bank.
"""
import math
import pygame

# Tight football palette. IDENTITY RIDES ON VALUE: the white shell is the
# brightest mass and the panels are near-black, so the pattern is a max value
# step that desaturates cleanly. The shade tone is a cool grey (not a tint of
# the panels) so the sphere reads round without muddying toward the black.
WHITE = (244, 245, 247)       # shell white — the bright body mass
WHITE_HI = (255, 255, 255)    # upper-left specular highlight (brightest pixel)
SHADE = (200, 205, 214)       # cool lower-right shade crescent — gives volume
SHADE2 = (170, 176, 188)      # deeper rim shade so the sphere turns at the edge
PANEL = (34, 36, 42)          # panel-black — the signature patches
PANEL_HI = (58, 61, 70)       # a hair-lighter panel top so panels look domed too
OUTLINE = (26, 28, 34)        # dark, drawn first + inflated: reads on day sky
KEYLINE = (150, 196, 232)     # cool rim — the NIGHT lifeline on dark sky


# 6x supersample: all geometry below stays in the original 44px design space and
# is scaled UP to a 264px work surface, then smoothscaled DOWN to OUT. This is a
# pure resolution/AA bump over the old 44px(2x)->22px path — the seams, sphere
# edge and pentagon corners resolve cleanly instead of crawling. Output is bumped
# to 26px (a touch over PARCEL_SIZE, matching the coin / mini-pip convention) so
# the added crispness actually survives on-screen without growing the footprint.
DES = 44                          # original design coordinate space (unchanged)
OUT = 26
SS  = 6
S   = DES * SS                    # 264px work surface


def _s(v):  return v * SS
def _p(pt): return (pt[0] * SS, pt[1] * SS)
def _w(v):  return max(1, int(round(v * SS)))


def _pentagon(cx, cy, r, rot):
    # A regular pentagon as a point list; rot in radians orients the flat/point.
    return [(cx + r * math.cos(rot + i * 2 * math.pi / 5),
             cy + r * math.sin(rot + i * 2 * math.pi / 5)) for i in range(5)]


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    # Mode-agnostic: one static football sprite for every Pip skin.
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    # All geometry below is authored in the original 44px space; _s/_p scale to SS.
    cx = cy = DES / 2
    R = 16                        # ball radius — bold, held off the edges

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    pygame.draw.circle(surf, OUTLINE, _p((cx, cy)), _s(R + 2))

    # --- White shell with baked volume: flat white, a deep rim shade ring, then
    # a tighter lit core so the sphere turns from a near-white top-left into a
    # cooler grey lower-right instead of reading as a flat paper disc.
    pygame.draw.circle(surf, SHADE2, _p((cx, cy)), _s(R))
    pygame.draw.circle(surf, SHADE, _p((cx - 1, cy - 1)), _s(R - 1))
    pygame.draw.circle(surf, WHITE, _p((cx - 3, cy - 3)), _s(R - 3))

    # Panels are drawn on a separate layer and MIN-masked to the sphere so the
    # partial rim pentagons clip to the ball's curve (they read as patches
    # wrapping away, not shards floating off the edge).
    panels = pygame.Surface((S, S), pygame.SRCALPHA)

    # Centred hero pentagon — flat edge up so it reads as a square-on panel; this
    # single bold black shape is what names the object at true size.
    hero = _pentagon(cx, cy - 1, 7.0, -math.pi / 2)
    pygame.draw.polygon(panels, PANEL, [_p(pt) for pt in hero])
    # A faint lighter cap on the hero panel's upper edge so even the black mass
    # picks up the light and the ball doesn't look like a hole.
    pygame.draw.polygon(panels, PANEL_HI, [
        _p(hero[0]), _p(hero[1]), _p((cx, cy - 1))])

    # Ring of PARTIAL pentagons poked in from the rim, one per hero edge so the
    # spacing echoes a real ball. Pushed out past R so only a wedge bites the
    # shell; the MIN-mask trims the rest. Kept to four — five would crowd to mud.
    for k in range(4):
        ang = -math.pi / 2 + (k + 0.5) * 2 * math.pi / 5 * 1.25
        # Bias the ring toward the lit upper area and the right so the pattern
        # isn't symmetric (a real ball never shows a tidy halo of panels). The
        # partials are pulled in a hair and grown so they bite a committed wedge
        # of black off the rim instead of a thin sliver that reads as noise.
        pcx = cx + R * math.cos(ang)
        pcy = cy + R * math.sin(ang) - 1
        pygame.draw.polygon(panels, PANEL,
                            [_p(pt) for pt in _pentagon(pcx, pcy, 6.6, ang + math.pi)])

    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), _p((cx, cy)), _s(R - 1))
    panels.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(panels, (0, 0))

    # --- Lower-right shade crescent over BOTH shell and panels so the whole
    # sphere darkens into the same lit/shade gradient (drawn semi-transparent so
    # it tints the panels without erasing them).
    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shade, (40, 46, 58, 70), _p((cx + 5, cy + 6)), _s(R))
    smask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), _p((cx, cy)), _s(R - 1))
    shade.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))

    # --- Upper-left specular highlight: a small soft white bloom that sits on
    # the shell (and reads as the glossy top of the sphere). The brightest pixel.
    hi = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hi, (255, 255, 255, 150), _p((cx - 5, cy - 6)), _s(4))
    pygame.draw.circle(hi, WHITE_HI, _p((cx - 6, cy - 7)), _s(2))
    hmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(hmask, (255, 255, 255, 255), _p((cx, cy)), _s(R - 2))
    hi.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hi, (0, 0))

    # --- Cool keyline rim INSIDE the outline — the NIGHT lifeline that glows on
    # dark sky while staying subtle on day. Traces the sphere.
    pygame.draw.circle(surf, KEYLINE, _p((cx, cy)), _s(R), _w(1))

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (OUT, OUT))
