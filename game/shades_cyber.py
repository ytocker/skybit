"""CYBER VISOR — single dark wraparound visor with a cyan edge-light.

ONE continuous band across both eyes (Kamina / Cyclops / Geordi idiom),
NOT two lenses. The read at 22px is a VALUE SANDWICH: a dark near-black
wedge mass with real vertical height, capped by a bright cyan edge-light
along the BOTTOM. The dark mass is what survives the downscale and reads
as eyewear against a scarlet head; the neon is the personality accent
riding its lower lip, not the whole shape.

Earlier single-bar pass collapsed to a thin cyan line and read as a
scratch on scarlet. The fix here is mass first: the body is a FILLED
wedge kept >=0.34*eye_w tall (>=~4px at eye_w=22) so the dark form holds,
then the cyan is layered as a hard bottom edge so dark-over-bright gives
contrast in BOTH directions. One off-center glint sells the gloss. A
short temple bar trails toward the ear (-facing) to anchor it on the
head. Everything scales off `eye_w` so the same code is a crisp 22px
overlay and a glossy 96px product shot.
"""
import pygame

_BODY_T = (38, 44, 60)              # cool top of the dark visor body
_BODY_B = (8, 10, 18)               # near-black underside — the mass
_FRAME  = (74, 84, 108)             # brushed-metal rim catching sky light
_FRAME_D = (20, 24, 36)             # rim shadow underside
_NEON   = (44, 230, 250)            # cyan edge-light (the signature)
_NEON_H = (208, 255, 255)           # hot core of the edge-light
_TOPTICK = (34, 120, 140)           # dim cyan tick on the top rim
_GLINT  = (236, 252, 255)


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    # Narrowed from 0.50 and the whole band shifted BACK toward the ear: the wide
    # raked visor reached its leading edge well past the beak. A tighter span +
    # smaller rake keeps the wraparound read while the lead edge clears the beak.
    half_w = max(4, int(eye_w * 0.40))      # ~0.8*eye_w total span
    half_h = max(3, int(eye_w * 0.19))      # ~0.38*eye_w tall -> >=5px @22
    rake = max(1, int(eye_w * 0.09))        # forward lean of the near edge
    rim = max(1, int(eye_w * 0.045))
    # Seat on the eye but ride slightly FORWARD so the leading edge laps the beak
    # base naturally; a small lift and small forward shift keep the visor over the
    # eye like a worn wraparound rather than retreating toward the ear.
    cy = cy - max(1, int(eye_w * 0.06))
    cx = cx + f * max(1, int(eye_w * 0.03))

    # Edge-light thickness must not eat the dark mass at tiny sizes: keep
    # the body clearly taller than the cyan lip so the sandwich survives.
    neon_t = max(2, int(eye_w * 0.075))

    near_x = cx + f * half_w
    far_x = cx - f * half_w
    top = cy - half_h
    bot = cy + half_h

    # Raked wraparound wedge: the near (+facing) edge slants forward at top
    # and pulls back at bottom so the bar reads as a curved visor, and it
    # tapers slightly toward the ear so the leading lens reads as the hero.
    quad = [
        (far_x,             top + max(1, half_h // 3)),   # rear top, dropped
        (near_x + f * rake, top),                          # lead top, raised
        (near_x,            bot),                          # lead bottom
        (far_x - f * (rake // 2), bot - max(1, half_h // 4)),  # rear bottom
    ]

    # Short temple bar trailing toward the ear so it anchors on the head.
    tx = far_x - f * max(2, int(eye_w * 0.22))
    ty = cy - max(1, int(eye_w * 0.03))
    pygame.draw.line(surf, _FRAME_D, (far_x, cy + 1), (tx, ty + 1),
                     max(2, rim + 1))
    pygame.draw.line(surf, _FRAME, (far_x, cy), (tx, ty), max(1, rim))

    # Metal rim = a slightly larger wedge drawn under the body so a thin
    # bright frame peeks around the dark mass and separates it from scarlet.
    rim_quad = [(x - f * (rim if i in (0, 3) else -rim),
                 y - rim if i < 2 else y + rim) for i, (x, y) in enumerate(quad)]
    pygame.draw.polygon(surf, _FRAME_D, [(x, y + 1) for x, y in rim_quad])
    pygame.draw.polygon(surf, _FRAME, rim_quad)

    # BODY: the dark wedge mass with a vertical top->bottom tint. Built on
    # its own surface and clipped to the raked quad so the gloss axis stays
    # vertical (cool top, near-black bottom) regardless of the rake.
    bx0 = min(p[0] for p in quad)
    bx1 = max(p[0] for p in quad)
    bw = max(2, bx1 - bx0)
    bh = max(2, bot - top)
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)
    span = max(1, bh - 1)
    for yy in range(bh):
        t = yy / span
        c = (int(_BODY_T[0] + (_BODY_B[0] - _BODY_T[0]) * t),
             int(_BODY_T[1] + (_BODY_B[1] - _BODY_T[1]) * t),
             int(_BODY_T[2] + (_BODY_B[2] - _BODY_T[2]) * t), 255)
        pygame.draw.line(body, c, (0, yy), (bw, yy))
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(x - bx0, y - top) for x, y in quad])
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (bx0, top))

    # SIGNATURE: bright cyan edge-light riding the BOTTOM lip of the wedge.
    # Drawn as a filled quad (a thin band, not a stroke) so it keeps real
    # thickness when downscaled, with a hot core line on top for the glow.
    le_top = bot - neon_t
    lead_b = (near_x, bot)
    rear_b = (far_x - f * (rake // 2), bot - max(1, half_h // 4))
    lead_t = (near_x, le_top)
    rear_t = (rear_b[0], rear_b[1] - neon_t)
    pygame.draw.polygon(surf, _NEON, [rear_t, lead_t, lead_b, rear_b])
    # Hot 1-2px core just above the lip keeps a crisp bright line at 22px
    # where the band alone would muddy.
    pygame.draw.line(surf, _NEON_H,
                     (rear_t[0], rear_t[1]), (lead_t[0], lead_t[1]),
                     max(1, neon_t // 2))

    # Dim cyan tick on the top rim ties the wrap together without competing
    # with the bottom hero edge-light.
    pygame.draw.line(surf, _TOPTICK,
                     (far_x, top + max(1, half_h // 3) + 1),
                     (near_x + f * rake, top + 1),
                     max(1, rim - 1) or 1)

    # Single off-center pinprick glint on the leading edge — sells gloss.
    pygame.draw.circle(surf, _GLINT,
                       (near_x - f * max(2, int(eye_w * 0.13)),
                        cy - max(1, int(eye_w * 0.07))),
                       max(1, int(eye_w * 0.04)))
