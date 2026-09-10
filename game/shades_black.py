"""BLACK SHADES (Wayfarer) — bold trapezoidal acetate frames, near-black lenses.

The read is the canonical Ray-Ban Wayfarer: two trapezoidal lenses (wider at
the top, tucked in at the bottom) in thick BLACK plastic, joined by a short
chunky bridge, with a prominent angular "shark-fin" temple toward the ear and
very dark lenses carrying only a faint cool blue-grey sheen. Cool and iconic.

Like the round-shades reference, every frame element is a FILLED shape rather
than a stroked outline — a thick black trapezoid drawn solid, then the tinted
glass inset inside it. A 1px stroked rim stipples and breaks at eye_w=22, but a
filled black polygon with a smaller glass polygon on top is always solid at any
size. Everything scales off `eye_w` so the same code is a clean product shot at
eye_w=96 and a legible in-game overlay at eye_w=22.
"""
import pygame

_FRAME   = (24, 24, 28)             # bold near-black acetate
_FRAME_H = (78, 82, 96)             # cool top-browline highlight (the sheen)
_FRAME_D = (8, 8, 10)               # deepest shadow edge under the frame
_LENS_T  = (40, 44, 58)             # faint blue-grey top of the dark glass
_LENS_B  = (12, 13, 18)             # near-black floor (vertical fade = curve)
_GLINT   = (208, 218, 236)          # cool white catch-light


def _tinted_disc(w, h, top, bot, alpha):
    """Rectangular dark-glass panel with a vertical top→bot tint at `alpha`.
    The vertical fade reads as curved glass; callers clip it to a lens polygon
    via BLEND_RGBA_MIN against a white mask so the tint takes the lens shape."""
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    span = max(1, h - 1)
    for yy in range(h):
        t = yy / span
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t), alpha)
        pygame.draw.line(g, c, (0, yy), (w, yy))
    return g


def _lens_poly(cx, cy, r, f):
    """Trapezoidal wayfarer lens outline centred on (cx,cy): wider across the
    top browline, narrower and tucked along the bottom, with the outer (ear-
    side) top corner lifted into the signature flared brow."""
    top = int(r * 0.92)             # half-width across the brow
    bot = int(r * 0.74)             # narrower base
    up  = int(r * 0.80)             # rise above the eye
    dn  = int(r * 0.92)             # drop below the eye
    brow = int(r * 0.16)            # extra lift on the outer top corner
    outer = -f                      # ear side is -facing
    return [
        (cx + f * top, cy - up),                 # inner-top
        (cx + outer * top, cy - up - brow),      # outer-top (flared brow)
        (cx + outer * bot, cy + dn),             # outer-bottom
        (cx + f * bot, cy + dn),                 # inner-bottom
    ]


def _inset_poly(pts, cx, cy, k):
    """Shrink a polygon toward its lens centre by factor k (0..1) — gives the
    inner glass opening the same trapezoid shape as the outer black frame."""
    return [(int(cx + (x - cx) * k), int(cy + (y - cy) * k)) for (x, y) in pts]


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    r    = max(3, int(eye_w * 0.26))
    sep  = max(4, int(eye_w * 0.46))
    rim  = max(2, int(eye_w * 0.085))   # chunky acetate is thicker than wire
    # Wayfarer lens drops below centre; keep enough lift that the lower-inner
    # corner clears the beak tip, but ride the pair slightly FORWARD so the near
    # lens laps the beak base — the natural seat of sunglasses on a face.
    cy   = cy - max(1, int(eye_w * 0.08))
    near = (cx + f * (sep // 2) + f * max(1, int(eye_w * 0.03)), cy)
    far  = (cx - f * (sep // 2), cy)

    # Chunky bridge BEHIND the lenses so the frame trapezoids overlap it clean;
    # sits high like a real wayfarer brow-bar. Drawn as a filled bar (+ shadow)
    # so it stays solid at tiny sizes.
    bx0 = far[0] + f * int(r * 0.55)
    bx1 = near[0] - f * int(r * 0.55)
    by  = cy - int(r * 0.46)
    bh  = max(2, rim)
    blo, bhi = (min(bx0, bx1), max(bx0, bx1))
    pygame.draw.rect(surf, _FRAME_D, (blo, by + 1, bhi - blo, bh))
    pygame.draw.rect(surf, _FRAME,   (blo, by, bhi - blo, bh))
    pygame.draw.rect(surf, _FRAME_H, (blo, by, bhi - blo, max(1, bh // 3)))

    # Angular shark-fin temple toward the ear (-facing): a tapered black wedge
    # hinged at the outer-top of the far lens, the way thick acetate arms read
    # in side profile. Filled triangle stays solid where a wire would stipple.
    hinge_x = far[0] - f * int(r * 0.92)
    hinge_y = cy - int(r * 0.70)
    arm_len = max(3, int(eye_w * 0.34))
    tip_x   = hinge_x - f * arm_len
    fin = [
        (hinge_x, hinge_y - max(1, rim)),
        (tip_x,   hinge_y - int(r * 0.10)),
        (tip_x,   hinge_y + int(r * 0.34)),
        (hinge_x, hinge_y + max(2, rim)),
    ]
    pygame.draw.polygon(surf, _FRAME_D, [(x, y + 1) for (x, y) in fin])
    pygame.draw.polygon(surf, _FRAME, fin)

    for (lx, ly) in (far, near):
        outer = _lens_poly(lx, ly, r, f)
        # Solid black trapezoid = the bold acetate rim (shadow pass, then face).
        pygame.draw.polygon(surf, _FRAME_D, [(x, y + 1) for (x, y) in outer])
        pygame.draw.polygon(surf, _FRAME, outer)

        # Inner glass opening: same trapezoid inset by the rim thickness, then
        # the vertical-tint panel clipped to that opening so the dark lens takes
        # the lens shape and shows its faint blue-grey-to-black sheen.
        k = max(0.40, 1.0 - rim / max(2, r))
        inner = _inset_poly(outer, lx, ly, k)
        xs = [x for x, _ in inner]; ys = [y for _, y in inner]
        gx0, gy0 = min(xs), min(ys)
        gw, gh = max(1, max(xs) - gx0), max(1, max(ys) - gy0)
        glass = _tinted_disc(gw, gh, _LENS_T, _LENS_B, 255)
        mask = pygame.Surface((gw, gh), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255),
                            [(x - gx0, y - gy0) for (x, y) in inner])
        glass.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(glass, (gx0, gy0))

        # Cool browline highlight along the top edge so the black frame pops off
        # the scarlet head — the sheen that says "glossy plastic", not flat.
        pygame.draw.line(surf, _FRAME_H, outer[0], outer[1], max(1, rim // 2))

    # Single diagonal glint streak across the near lens sells the dark glossy
    # glass — a hard cool slash, the classic wayfarer reflection.
    gx = near[0]
    pygame.draw.line(surf, _GLINT,
                     (gx + f * int(r * 0.10), cy - int(r * 0.45)),
                     (gx - f * int(r * 0.35), cy + int(r * 0.30)),
                     max(1, int(eye_w * 0.045)))
