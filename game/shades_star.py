"""STAR SHADES — novelty festival party glasses with 5-point STAR lenses.

The star silhouette is the entire read, so the points are kept CHUNKY: the
inner radius is ~0.53 of the outer (not the ~0.38 of a "true" rendered star),
which makes the five points stubby and fat. A slender pointy star fills to a
near-circle and loses its points at the in-game size (eye_w=22); a fat stubby
one keeps a countable 5-point silhouette even when each point is only a few
pixels tall.

To survive 22px the lens carries a SOLID GOLD backing star drawn behind the
glass (an outset star, not a 1px stroke — a stroked star stipples and breaks
at tiny radii while a filled backing star is always solid metal). The gold
rim ties STAR into the set idiom (ROUND / MONOCLE / HEART all gold). The glass
is a deep electric-blue, chosen for real value-contrast against Pip's scarlet
head so the dark lens + bright gold points stay separable at tiny size.

Every dimension scales off `eye_w` so the same code is a glam product shot at
eye_w=96 and a legible overlay at eye_w=22. The bridge sits behind both lenses
so the lens polygons overlap it cleanly.
"""
import math
import pygame

_RIM    = (240, 198, 84)            # warm gold metal frame
_RIM_H  = (255, 244, 178)           # bright catch-light on the gold
_RIM_D  = (176, 124, 36)            # underside / shadow side of the gold
_TINT_T = (70, 150, 240)            # electric-blue top of the glass
_TINT_B = (16, 46, 120)             # deep navy floor (vertical fade)
_GLINT  = (255, 255, 255)


def _star_points(cx, cy, r_out, r_in, rot=-math.pi / 2):
    """10 vertices of a 5-point star centred at (cx,cy). `rot` puts a point
    straight up (-90deg) so the star reads upright in side profile."""
    pts = []
    for i in range(10):
        ang = rot + i * math.pi / 5
        rad = r_out if i % 2 == 0 else r_in
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    return pts


def _tinted_star(r_out, r_in, top, bot, alpha):
    """Star-clipped glass: a vertical top→bot gradient masked to the star
    polygon. The vertical fade fakes curved tinted glass on the flat lens."""
    size = r_out * 2 + 2
    g = pygame.Surface((size, size), pygame.SRCALPHA)
    span = max(1, size - 1)
    for yy in range(size):
        t = yy / span
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t), alpha)
        pygame.draw.line(g, c, (0, yy), (size, yy))
    clip = pygame.Surface((size, size), pygame.SRCALPHA)
    c2 = r_out + 1
    pygame.draw.polygon(clip, (255, 255, 255, 255),
                        _star_points(c2, c2, r_out, r_in))
    g.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return g, c2


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    # Shrunk from 0.32 so the two stars sit ON the eye area instead of sprawling
    # over the beak; still fat-pointed enough to read as a star at 22px.
    r_out = max(5, int(eye_w * 0.26))
    # Fat stubby points: inner radius ~0.53*outer keeps the 5 points countable
    # at 22px where a slender star would fill to a blob.
    r_in  = max(3, int(r_out * 0.53))
    sep   = max(6, int(eye_w * 0.44))
    # Frame thickness as an outset of the backing star; min 2px so the gold rim
    # never thins to nothing, scaling up to a chunky rim on the product shot.
    fw    = max(2, int(eye_w * 0.07))
    # Seat the pair on the eye but ride it slightly FORWARD so the near star laps
    # the beak base naturally; a modest lift keeps its lower point off the beak
    # tip rather than retreating the whole pair away from the beak.
    cy    = cy - max(1, int(eye_w * 0.07))
    near  = (cx + f * (sep // 2) + f * max(1, int(eye_w * 0.03)), cy)
    far   = (cx - f * (sep // 2), cy)

    # Bridge BEHIND the lenses so the lens stars overlap it; the lower pass is
    # the gold catch-light beneath the bridge wire.
    by  = cy - max(1, int(r_out * 0.08))
    bx0 = far[0] + f * int(r_in * 1.0)
    bx1 = near[0] - f * int(r_in * 1.0)
    pygame.draw.line(surf, _RIM_D, (bx0, by + 1), (bx1, by + 1), max(2, fw))
    pygame.draw.line(surf, _RIM, (bx0, by), (bx1, by), max(2, fw - 1))

    # Temple arm toward the ear (-facing): straight gold wire with a shadow
    # underline so it reads off the scarlet head.
    ex = far[0] - f * (r_out + max(2, int(eye_w * 0.30)))
    ey = cy - max(1, int(eye_w * 0.05))
    hook = (far[0] - f * int(r_out * 0.5), cy)
    pygame.draw.line(surf, _RIM_D, hook, (ex, ey + 1), max(2, fw))
    pygame.draw.line(surf, _RIM, hook, (ex, ey), max(2, fw - 1))

    for (lx, ly) in (far, near):
        # Solid gold frame = outset gold star, then the tinted glass star inset
        # by the frame width — always solid metal even at eye_w=22. The backing
        # star uses a proportionally-grown inner radius so the gold preserves
        # the fat-point silhouette out past the glass on every spoke.
        f_out = r_out + fw
        f_in  = r_in + fw
        pygame.draw.polygon(surf, _RIM_D,
                            _star_points(lx, ly + 1, f_out, f_in))
        pygame.draw.polygon(surf, _RIM,
                            _star_points(lx, ly, f_out, f_in))

        glass, c2 = _tinted_star(r_out, r_in, _TINT_T, _TINT_B, 225)
        surf.blit(glass, (lx - c2, ly - c2))

        # Gold catch-light along the two upper-left point edges so the metal
        # frame pops and the star silhouette stays crisp on a warm head.
        sp = _star_points(lx, ly, f_out, f_in)
        pygame.draw.lines(surf, _RIM_H, False, [sp[8], sp[9], sp[0]],
                          max(1, fw - 1))

    # Single bright glint inside the near lens body — sells the glossy glass.
    pygame.draw.circle(surf, _GLINT,
                       (near[0] - f * (r_in // 3), cy - r_in // 3),
                       max(1, int(eye_w * 0.05)))
