"""NERD SPECS — chunky BLACK horn-rim prescription glasses with TINTED-CLEAR
lenses (geek-chic). The read is two rounded-SQUARE black rims joined by a short
bridge, a temple arm to the ear, and a faintly cool glass that lets the eye show
through WITHOUT looking like an empty hole. A tiny tape-on-bridge nod sits on top
of the bridge.

Identity vs. the even BLACK wayfarer in the store grid: NERD is BROW-FORWARD —
the upper rim is drawn noticeably thicker than the sides/bottom, so the
silhouette is top-heavy and unmistakably "nerd," not the wayfarer's even frame.

The rim is a FILLED rounded-rect with the lens INSET by the rim width, never a
stroked outline — a 1px stroke stipples and breaks at tiny radii, but a filled
frame with an inset glass panel keeps the thick black brow solid even at
eye_w=22 in-game. The glass tint is opaque enough to read as glass over the
scarlet head, so the rim is NOT the only thing visible at tiny size. Everything
is proportional to `eye_w` so the same code blooms into a clean product shot
(eye_w~96) and stays legible over Pip's eye.
"""
import pygame

_RIM    = (24, 24, 28)              # near-black horn-rim plastic
_RIM_HI = (92, 92, 104)            # top-bevel sheen so black plastic reads round
_RIM_LO = (8, 8, 12)               # underside shadow of the chunky rim
# Cool glass wash, strong enough to read as glass (not a hole) over scarlet at
# 22px, yet still translucent so Pip's eye shows through.
_GLASS  = (196, 220, 240, 132)
_SHEEN  = (255, 255, 255)
_TAPE   = (236, 232, 214)          # off-white bandage tape on the bridge
_TAPE_E = (198, 192, 168)          # tape edge/shadow


def _rrect(surf, color, rect, radius):
    """Filled rounded-rect that never errors when radius exceeds the half-span
    (tiny lenses) — pygame clamps internally, but we guard the degenerate case."""
    r = max(0, min(radius, rect.w // 2, rect.h // 2))
    pygame.draw.rect(surf, color, rect, border_radius=r)


def _clear_lens(surf, rect, radius):
    """Paint a faint clear lens into `rect` with a diagonal glossy streak, so the
    eye reads THROUGH the glass — the rim stays the dominant black feature."""
    w, h = rect.w, rect.h
    if w < 2 or h < 2:
        return
    glass = pygame.Surface((w, h), pygame.SRCALPHA)
    _rrect(glass, _GLASS, pygame.Rect(0, 0, w, h), radius)
    # Diagonal sheen wedge across the upper portion, clipped to the lens shape
    # so the gloss never spills past the rim.
    band = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(band, (*_SHEEN, 110),
                        [(0, h * 0.18), (w * 0.46, 0), (w * 0.68, 0),
                         (0, h * 0.66)])
    clip = pygame.Surface((w, h), pygame.SRCALPHA)
    _rrect(clip, (255, 255, 255, 255), pygame.Rect(0, 0, w, h), radius)
    band.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    glass.blit(band, (0, 0))
    surf.blit(glass, rect.topleft)


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    hw   = max(2, int(eye_w * 0.26))           # lens half-width
    sep  = max(4, int(eye_w * 0.46))           # centre-to-centre lens spacing
    rim  = max(2, int(eye_w * 0.085))          # CHUNKY horn-rim thickness (sides)
    # Brow-forward identity: the upper rim is the heaviest stroke on the frame,
    # at least ~1px chunkier than the sides so NERD never collides with the even
    # BLACK wayfarer at thumbnail size.
    brow = rim + max(1, int(eye_w * 0.035))
    hh   = int(hw * 1.05)                       # lens half-height (square-ish)
    rad  = max(2, int(hw * 0.42))               # softly rounded corners
    # Seat the frame on the eye but riding slightly FORWARD so the near lens
    # grazes the beak base the way real specs sit on a face — a modest lift keeps
    # the lens mass off the beak TIP while the front rim laps the beak naturally.
    lift = max(1, int(eye_w * 0.10))
    cy   = cy - lift
    near = (cx + f * (sep // 2) + f * max(1, int(eye_w * 0.03)), cy)
    far  = (cx - f * (sep // 2), cy)            # back lens (toward ear)

    def lens_rect(c):
        return pygame.Rect(c[0] - hw, c[1] - hh, hw * 2, hh * 2)

    # Temple arm to the ear (-facing): a thick black bar so it reads as the same
    # heavy plastic as the rims even at tiny size. Drawn first, behind the rim.
    tlen = max(3, int(eye_w * 0.30))
    ty   = cy - max(1, int(hh * 0.45))
    far_edge = far[0] - f * hw
    pygame.draw.line(surf, _RIM_LO, (far_edge, ty + 1),
                     (far_edge - f * tlen, ty - max(1, int(eye_w * 0.05)) + 1),
                     rim)
    pygame.draw.line(surf, _RIM, (far_edge, ty),
                     (far_edge - f * tlen, ty - max(1, int(eye_w * 0.05))), rim)

    # Bridge BEHIND the rims (the rim frames overlap it), kept high & short like
    # real horn-rims and tucked up under the heavy brow; the lower pass is its
    # drop shadow.
    by   = cy - int(hh * 0.46)
    bx0  = far[0] + f * hw
    bx1  = near[0] - f * hw
    bh   = max(2, brow)
    pygame.draw.line(surf, _RIM_LO, (bx0, by + 1), (bx1, by + 1), bh)
    pygame.draw.line(surf, _RIM, (bx0, by), (bx1, by), bh)

    for c in (far, near):
        r = lens_rect(c)
        # Drop shadow so the chunky frame lifts off the scarlet head.
        _rrect(surf, _RIM_LO, r.move(0, max(1, rim // 2)), rad)
        # Solid black frame, then the glass inset — MORE from the top than the
        # sides/bottom, so the upper rim reads as a heavy brow and the
        # silhouette is top-heavy (the NERD tell).
        _rrect(surf, _RIM, r, rad)
        inner = pygame.Rect(r.left + rim, r.top + brow,
                            r.w - rim * 2, r.h - brow - rim)
        irad = max(1, rad - rim)
        # Lay the tinted glass into the eye-hole; the tint keeps it reading as
        # glass over the scarlet head rather than as a punched-through hole.
        _clear_lens(surf, inner, irad)
        # Top-bevel sheen line on the brow so the heavy black plastic reads as a
        # rounded ridge, not a flat slab.
        pygame.draw.line(surf, _RIM_HI,
                         (r.left + rad, r.top + max(1, brow // 3)),
                         (r.right - rad, r.top + max(1, brow // 3)),
                         max(1, brow // 3))

    # Optional taped-bridge nod: a small off-white bandage wrap over the bridge
    # centre, the unmistakable broke-the-glasses geek detail. Only at sizes that
    # can carry it, so it never muddies the tiny in-game read.
    if eye_w >= 30:
        tw = max(2, int(eye_w * 0.075))
        th = int(hh * 0.85)
        tape = pygame.Rect(0, 0, tw, th)
        tape.center = (cx, by + 1)
        _rrect(surf, _TAPE_E, tape.move(0, 1), max(1, tw // 3))
        _rrect(surf, _TAPE, tape, max(1, tw // 3))
        # Two faint cross-lines so it reads as wrapped tape, not a plain block.
        pygame.draw.line(surf, _TAPE_E,
                         (tape.left, tape.centery - th // 6),
                         (tape.right, tape.centery - th // 6), 1)
        pygame.draw.line(surf, _TAPE_E,
                         (tape.left, tape.centery + th // 6),
                         (tape.right, tape.centery + th // 6), 1)

    # One pinprick glint on the near lens — sells the glossy clear glass.
    pygame.draw.circle(surf, _SHEEN,
                       (near[0] - f * (hw // 2), cy - hh // 2),
                       max(1, int(eye_w * 0.045)))
