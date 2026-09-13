"""SKI GOGGLES — one wide single-lens snow goggle in side profile.

A single big rounded-rectangular lens spans both eyes (NOT two discs), with a
mirrored icy-blue→violet gradient tint and a hard diagonal sheen streak (the
goggle "flash"). A clean white-plastic frame rings the lens, and one solid warm
strap wraps from the far (-facing) edge back toward the ear.

SET cohesion: every frame in the eyewear set standardizes on neutral plastic so
the LENS colour carries the personality — here the icy-blue→violet mirror. The
frame is plain white plastic; the strap is one flat warm band.

Everything scales off `eye_w` so the chunky lens + frame + strap all still read
in-game (eye_w=22) yet bloom into a clean product shot (eye_w=96). The lens is
a FILLED inset rounded-rect (frame rect, then the tinted glass inset by the
frame width) rather than a stroked outline — a 1px stroke stipples at tiny
sizes, but an inset fill is always solid frame + glass. At 22px the simplified
strap (one band, no stripe) and the inset highlight stop the goggle from
reading as random specks bleeding past Pip's scarlet head edge.
"""
import pygame

_PLAS    = (248, 249, 252)          # white-plastic frame top edge
_PLAS_D  = (196, 202, 214)          # plastic shadow side (lower rim)
_FRAME   = (44, 52, 74)             # dark moulded line between plastic and lens
_LENS_T  = (150, 214, 248)          # icy blue — top of the mirrored tint
_LENS_M  = (108, 150, 234)          # cobalt mid
_LENS_B  = (150, 96, 214)           # violet floor of the tint
_SHEEN   = (236, 248, 255)          # diagonal flash streak
_STRAP   = (236, 84, 110)           # one solid warm strap band
_GLINT   = (255, 255, 255)


def _lens(w, h, rad, facing):
    """Mirrored goggle glass: a w*h surface with a vertical icy-blue→violet
    tint, a bright diagonal sheen streak, masked to a rounded-rect so the lens
    reads as one curved snow-goggle window. `facing` slants the sheen."""
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    span = max(1, h - 1)
    for yy in range(h):
        t = yy / span
        # Two-stop fade (icy → cobalt → violet) gives the mirror more depth
        # than a flat blend would.
        if t < 0.5:
            u = t / 0.5
            a, b = _LENS_T, _LENS_M
        else:
            u = (t - 0.5) / 0.5
            a, b = _LENS_M, _LENS_B
        c = (int(a[0] + (b[0] - a[0]) * u),
             int(a[1] + (b[1] - a[1]) * u),
             int(a[2] + (b[2] - a[2]) * u), 255)
        pygame.draw.line(g, c, (0, yy), (w, yy))

    # Diagonal flash streak — a fat bright parallelogram swept across the glass,
    # leaning with `facing` so it tracks the head direction.
    streak = pygame.Surface((w, h), pygame.SRCALPHA)
    sw = max(2, int(w * 0.12))
    sx = int(w * (0.62 if facing >= 0 else 0.38))
    lean = int(h * 0.55) * (1 if facing >= 0 else -1)
    pts = [(sx, 0), (sx + sw, 0),
           (sx + sw - lean, h), (sx - lean, h)]
    pygame.draw.polygon(streak, (*_SHEEN, 150), pts)
    # A thinner, brighter inner streak alongside reads as a second highlight.
    sx2 = sx - int(sw * 1.6) * (1 if facing >= 0 else -1)
    sw2 = max(1, sw // 2)
    pts2 = [(sx2, 0), (sx2 + sw2, 0),
            (sx2 + sw2 - lean, h), (sx2 - lean, h)]
    pygame.draw.polygon(streak, (*_SHEEN, 90), pts2)
    g.blit(streak, (0, 0))

    # Mask everything to a rounded-rect so the glass is one clean lens.
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=rad)
    g.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return g


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    # Narrowed from 0.96: the full-face goggle swallowed the beak. A tighter span
    # still reads as one wide single-lens snow goggle but stays off the beak.
    lw   = max(8, int(eye_w * 0.70))           # one wide lens across both eyes
    lh   = max(5, int(eye_w * 0.46))
    plas = max(1, int(eye_w * 0.08))           # white-plastic frame ring
    rad  = max(2, int(lh * 0.42))              # rounded goggle corners
    # Seat the goggle on the eye but ride it slightly FORWARD so its leading edge
    # laps the beak base naturally; only a small lift and a small forward shift so
    # it covers the eye like a worn goggle rather than retreating toward the ear.
    cy   = cy - max(1, int(eye_w * 0.07))
    cx   = cx + f * max(1, int(eye_w * 0.03))
    x0   = cx - lw // 2
    y0   = cy - lh // 2

    # One solid warm strap FIRST so the frame overlaps it cleanly. A single flat
    # band (no centre stripe) so it never reads as a stray streak at 22px. It
    # wraps off the far (-facing) edge toward the ear, dipping slightly like
    # webbing pulled around the head.
    strap_h = max(3, int(eye_w * 0.30))
    sx_in   = cx - f * (lw // 2 - plas)        # tuck under the lens edge
    sx_out  = cx - f * int(lw * 0.92)
    sy      = cy - max(1, int(eye_w * 0.02))
    dip     = max(1, int(eye_w * 0.10))        # sag toward the ear
    band = [(sx_in, sy - strap_h // 2), (sx_out, sy - strap_h // 2 + dip),
            (sx_out, sy + strap_h // 2 + dip), (sx_in, sy + strap_h // 2)]
    pygame.draw.polygon(surf, _STRAP, band)

    # White-plastic frame = bright rounded-rect; the lens glass is inset by
    # `plas`. Shadow-side plastic first (offset down) so the lower rim reads as
    # a moulded plastic edge.
    fr = (x0 - plas, y0 - plas, lw + plas * 2, lh + plas * 2)
    pygame.draw.rect(surf, _PLAS_D,
                     (fr[0], fr[1] + max(1, plas // 2), fr[2], fr[3]),
                     border_radius=rad + plas)
    pygame.draw.rect(surf, _PLAS, fr, border_radius=rad + plas)
    # Thin dark frame line between plastic and glass sells the moulded rim.
    pygame.draw.rect(surf, _FRAME, (x0, y0, lw, lh),
                     border_radius=rad, width=max(1, plas // 2))

    # The mirrored glass lens, inset inside the dark frame.
    inset = max(1, plas // 2)
    gw, gh = lw - inset * 2, lh - inset * 2
    if gw > 2 and gh > 2:
        glass = _lens(gw, gh, max(1, rad - inset), f)
        surf.blit(glass, (x0 + inset, y0 + inset))

    # White highlight pulled INWARD onto the glass (not the outer rim) so the
    # gloss pop never bleeds past Pip's head edge at 22px. It rides the upper
    # leading corner of the lens itself.
    gx = cx + f * (lw // 2 - plas - max(2, int(eye_w * 0.16)))
    gy = y0 + inset + max(1, int(eye_w * 0.07))
    pygame.draw.circle(surf, _GLINT, (gx, gy), max(1, int(eye_w * 0.05)))
