"""WHITE RETRO SHADES — chunky 80s white-plastic frames, smoke-tinted glass.

The read is the THICK glossy WHITE rim popping hard off Pip's scarlet head:
bold Miami/retro plastic, not delicate wire. Two slightly-squarish rounded
lenses joined by a fat white bridge, with a chunky white temple arm to the
ear. The lens glass is a vertical amber→rose smoke fade so the flat inset
still reads as curved glass.

Every dimension scales off `eye_w` so the white frame stays solid and bright
at eye_w=22 (in-game overlay over the eye) and blooms into a clean product
shot at eye_w=96. The rim is a FILLED rounded-rect frame (white plate, then
the tinted glass inset by the rim width) rather than a stroked outline — a
thin stroke stipples and breaks at tiny sizes, but an inset plate is always
solid plastic. A bright top band on the white sells the plastic gloss.
"""
import pygame

_WHITE   = (244, 246, 248)          # body of the white plastic frame
_WHITE_H = (255, 255, 255)          # top gloss band on the plastic
_WHITE_D = (196, 202, 212)          # underside / shadow edge of the plastic
_SMOKE_T = (250, 196, 150)          # warm amber top of the smoke glass
_SMOKE_B = (196, 92, 132)           # rose floor (vertical fade)
_GLINT   = (255, 255, 255)


def _rrect(surf, color, rect, radius):
    """Filled rounded rect that stays solid even when radius collapses at
    tiny sizes — pygame clamps radius, so guard the degenerate case."""
    r = max(0, min(radius, rect.w // 2, rect.h // 2))
    pygame.draw.rect(surf, color, rect, border_radius=r)


def _tinted_glass(w, h, radius, top, bot, alpha):
    """Rounded glass plate w×h with a vertical top→bot tint at `alpha`.
    The vertical fade fakes the curve of real lens glass on a flat inset."""
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    span = max(1, h - 1)
    for yy in range(h):
        t = yy / span
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t), alpha)
        pygame.draw.line(g, c, (0, yy), (w, yy))
    clip = pygame.Surface((w, h), pygame.SRCALPHA)
    _rrect(clip, (255, 255, 255, 255), pygame.Rect(0, 0, w, h), radius)
    g.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return g


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    hw   = max(3, int(eye_w * 0.27))          # lens half-width
    hh   = max(3, int(eye_w * 0.30))          # lens half-height (slightly tall)
    sep  = max(6, int(eye_w * 0.46))          # centre-to-centre lens spacing
    rim  = max(2, int(eye_w * 0.09))          # chunky white rim
    rad  = max(2, int(eye_w * 0.12))          # squarish-rounded 80s corner
    # Tall chunky lens drapes below the eye; keep enough lift that the bottom-
    # front rim clears the beak tip, but ride the pair slightly FORWARD so the
    # near lens laps the beak base — the natural seat of glasses on a face.
    cy   = cy - max(1, int(eye_w * 0.10))
    near = (cx + f * (sep // 2) + f * max(1, int(eye_w * 0.03)), cy)
    far  = (cx - f * (sep // 2), cy)

    def frame_rect(c):
        return pygame.Rect(c[0] - hw, c[1] - hh, hw * 2, hh * 2)

    # Fat white bridge BEHIND the lenses so the rim plates overlap it cleanly;
    # the lower pass is the plastic underside shadow.
    bx0 = far[0] + f * (hw - rim)
    bx1 = near[0] - f * (hw - rim)
    bw  = max(2, rim + 1)
    by  = cy - max(1, int(hh * 0.30))
    pygame.draw.line(surf, _WHITE_D, (bx0, by + 1), (bx1, by + 1), bw)
    pygame.draw.line(surf, _WHITE, (bx0, by), (bx1, by), bw)

    # Chunky white temple arm toward the ear (-facing), angled slightly down.
    ex = far[0] - f * (hw + max(3, int(eye_w * 0.34)))
    ey = cy - max(1, int(eye_w * 0.04))
    tw = max(2, rim)
    pygame.draw.line(surf, _WHITE_D, (far[0] - f * (hw - 1), cy + 1), (ex, ey + 1), tw)
    pygame.draw.line(surf, _WHITE, (far[0] - f * (hw - 1), cy), (ex, ey), tw)

    for (lx, ly) in (far, near):
        fr = frame_rect((lx, ly))
        # Underside shadow plate offset down 1px gives the plastic thickness.
        _rrect(surf, _WHITE_D, fr.move(0, 1), rad)
        _rrect(surf, _WHITE, fr, rad)
        # Tinted glass inset by the rim width.
        gw = max(2, fr.w - rim * 2)
        gh = max(2, fr.h - rim * 2)
        grad = max(1, rad - rim)
        glass = _tinted_glass(gw, gh, grad, _SMOKE_T, _SMOKE_B, 210)
        surf.blit(glass, (fr.x + rim, fr.y + rim))
        # Bright gloss band across the top of the white plastic so it pops off
        # the scarlet head and reads as glossy, not matte.
        hb = max(1, rim // 2)
        pygame.draw.line(surf, _WHITE_H,
                         (fr.x + rad, fr.y + max(1, rim // 3)),
                         (fr.right - rad, fr.y + max(1, rim // 3)), hb)

    # Diagonal glass glint on the near lens sells the glossy smoke surface.
    fr = frame_rect(near)
    gx0 = fr.x + rim + max(1, int(hw * 0.30))
    gy0 = fr.y + rim + max(1, int(hh * 0.30))
    pygame.draw.line(surf, _GLINT, (gx0, gy0),
                     (gx0 + max(2, int(hw * 0.5)), gy0 + max(2, int(hh * 0.5))),
                     max(1, int(eye_w * 0.035)))
    pygame.draw.circle(surf, _GLINT, (gx0, gy0), max(1, int(eye_w * 0.045)))
