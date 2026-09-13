"""ROUND SHADES (Lennon) — chosen round-1 design (variant A).

Small, PERFECTLY-CIRCULAR thin gold wire rims with rose-quartz tinted glass —
the canonical 1960s/70s rockstar Lennon look. The two distinct gold circles,
the delicate dipped bridge, and the rose tint are the read; everything scales
off `eye_w` so a 1px rim still draws as solid metal in-game (eye_w=22) while
the same code blooms into a clean product shot at eye_w=96.

The rim is a FILLED ring (gold disc, then the tinted glass inset by the rim
width) rather than a stroked circle — a 1px stroked outline stipples and
breaks at tiny radii, but an inset disc is always solid metal.
"""
import pygame

_RIM    = (236, 196, 96)            # warm gold metal
_RIM_H  = (255, 242, 188)           # bright top-rim crescent
_RIM_D  = (176, 132, 52)            # underside / shadow side of the wire
_ROSE_T = (236, 180, 196)           # bright rose top of the glass
_ROSE_B = (170, 96, 124)            # deeper rose floor (vertical fade)
_GLINT  = (255, 255, 255)


def _tinted_disc(r, top, bot, alpha):
    """Round glass disc of radius r with a vertical top→bot tint at `alpha`.
    The vertical fade gives the flat disc a sense of curved glass."""
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    span = max(1, r * 2 - 1)
    for yy in range(r * 2):
        t = yy / span
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t), alpha)
        pygame.draw.line(g, c, (0, yy), (r * 2, yy))
    clip = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(clip, (255, 255, 255, 255), (r, r), r)
    g.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return g


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    r    = max(3, int(eye_w * 0.26))
    sep  = max(4, int(eye_w * 0.46))
    rim  = max(1, int(eye_w * 0.065))
    # Seat the rose discs on the eye but ride them slightly FORWARD so the near
    # ring laps the beak base naturally (sunglasses sit in front of the bridge);
    # a small lift keeps the discs off the beak tip.
    cy   = cy - max(1, int(eye_w * 0.06))
    near = (cx + f * (sep // 2) + f * max(1, int(eye_w * 0.04)), cy)
    far  = (cx - f * (sep // 2), cy)

    # Delicate dipped bridge BEHIND the rims so the rim discs overlap it
    # cleanly; the lower second pass is the gold catch-light.
    bx0 = far[0] + f * (r - rim)
    bx1 = near[0] - f * (r - rim)
    by = cy - max(1, int(r * 0.42))
    pygame.draw.line(surf, _RIM_D, (bx0, by + 1), (bx1, by + 1), max(1, rim))
    pygame.draw.line(surf, _RIM, (bx0, by), (bx1, by), max(1, rim))

    # Cable temple toward the ear (-facing), thin gold wire.
    ex = far[0] - f * (r + max(2, int(eye_w * 0.30)))
    ey = cy - max(1, int(eye_w * 0.06))
    pygame.draw.line(surf, _RIM_D, (far[0] - f * (r - 1), cy - 1), (ex, ey),
                     max(1, rim))
    pygame.draw.line(surf, _RIM, (far[0] - f * (r - 1), cy - 1), (ex, ey),
                     max(1, rim - 1) or 1)

    for (lx, ly) in (far, near):
        # Solid gold ring = gold disc, then the tinted glass disc inset by rim.
        pygame.draw.circle(surf, _RIM_D, (lx, ly + 1), r)      # underside wire
        pygame.draw.circle(surf, _RIM, (lx, ly), r)
        gr = max(2, r - rim)
        glass = _tinted_disc(gr, _ROSE_T, _ROSE_B, 205)
        surf.blit(glass, (lx - gr, ly - gr))
        # Bright top crescent so the round metal pops off the scarlet head.
        pygame.draw.arc(surf, _RIM_H, (lx - r, ly - r, r * 2, r * 2),
                        0.5, 2.5, max(1, rim))

    # One pinprick glint on the near lens — sells the glossy round glass.
    pygame.draw.circle(surf, _GLINT, (near[0] - f * (r // 2), cy - r // 2),
                       max(1, int(eye_w * 0.05)))
