"""COURT GREEN — clean minimalist white-leather tennis low-top homage.

Drawn entirely from pygame primitives so it survives the full size range:
the SAME function is the ~104×62 product shot AND a ~15×10 sprite on the
bird's feet. Geometry is expressed as fractions of the (x, y, w, h) box so it
scales cleanly; stroke widths clamp to >=1px so detail never vanishes tiny.

It is a HOMAGE in the spirit of the game's KFC parody theme — a silhouette +
colorway with two stylized cues (green heel tab, perforation-dot column where
a side stripe would be), never an exact trademarked mark. No text, no logo.
"""
import pygame


# Crisp all-white leather + understated green accent. Edges are 1px darker
# tints of the base, not black, so the shoe stays premium and clean.
_LEATHER   = (246, 246, 242)
_LEATHER_S = (220, 220, 214)   # leather shadow / soft seam
_SOLE      = (250, 250, 248)   # slim flat white sole face
_SOLE_UND  = (198, 198, 190)   # warmer mid-grey sole underside (anti-float)
_SOLE_EDGE = (182, 182, 174)   # darker sole tread / edge line
_GREEN      = (28, 158, 88)    # heel-tab green — the one accent that reads at 16px
_GREEN_D    = (20, 104, 58)    # heel-tab shadow
_GREEN_SOLE = (24, 138, 80)    # outsole/heel green stripe — strong value so a
                               # green accent survives even when the tab does not
_PERF       = (212, 212, 206)  # midfoot perforation dots
_PERF_S     = (198, 198, 192)  # per-dot soft shadow, one value-step darker
_LACE       = (236, 236, 230)
_GROUND     = (12, 9, 28)      # thin grounded contact shadow under the sole


def _u(u, v, x, y, w, h, facing):
    """Map unit-box (u, v) in [0..1] to device pixels, mirroring about u=0.5
    when facing left so one core serves both feet / both store orientations."""
    if facing < 0:
        u = 1.0 - u
    return (int(round(x + u * w)), int(round(y + v * h)))


def _poly(surf, color, pts, x, y, w, h, facing):
    pygame.draw.polygon(surf, color, [_u(u, v, x, y, w, h, facing)
                                      for u, v in pts])


def _line(surf, color, a, b, x, y, w, h, facing, width):
    pygame.draw.line(surf, color, _u(*a, x, y, w, h, facing),
                     _u(*b, x, y, w, h, facing), max(1, int(round(width))))


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile COURT GREEN sneaker into box (x, y, w, h).

    Toe points RIGHT when facing=1 (mirrored for -1). Slim low-profile tennis
    shoe: outsole/midsole is the bottom ~18% of h, upper top near y. No outer
    outline — the caller adds the house outline.
    """
    # ── grounded contact shadow ───────────────────────────────────────────
    # A thin dark sliver beneath the sole so the white shoe doesn't float on
    # the dark Store card. Drawn first, just under the tread line.
    _poly(surf, _GROUND, [(0.05, 0.985), (0.95, 0.985), (0.92, 1.0),
                          (0.08, 1.0)], x, y, w, h, facing)

    # ── slim flat sole (bottom ~18%) ──────────────────────────────────────
    # A low cupsole grounded on the box floor, matching AIR FLYER / CANVAS
    # HIGH's sole thickness + ground line. Warmer-grey underside first, the
    # white sidewall on top, so the shoe reads as a solid mass, not a sliver.
    sole_und = [(0.03, 0.86), (0.10, 0.83), (0.92, 0.84), (0.99, 0.88),
                (0.96, 0.98), (0.05, 0.98), (0.01, 0.92)]
    _poly(surf, _SOLE_EDGE, sole_und, x, y, w, h, facing)
    sole_bot = [(0.04, 0.92), (0.96, 0.93), (0.94, 0.975), (0.06, 0.975)]
    _poly(surf, _SOLE_UND, sole_bot, x, y, w, h, facing)
    sole_face = [(0.05, 0.855), (0.92, 0.855), (0.95, 0.915), (0.07, 0.925)]
    _poly(surf, _SOLE, sole_face, x, y, w, h, facing)
    # Foxing seam where leather meets sole.
    _line(surf, _SOLE_EDGE, (0.06, 0.85), (0.93, 0.855), x, y, w, h, facing,
          max(1, h * 0.025))

    # ── CUE · green outsole stripe ────────────────────────────────────────
    # The heel tab alone vanishes at 16px, so a strong-value green band rides
    # the heel half of the sidewall right above the tread. As a solid mass on
    # the largest single element, it is the accent that still reads when tiny.
    _poly(surf, _GREEN_SOLE, [(0.04, 0.875), (0.55, 0.875), (0.55, 0.925),
                              (0.06, 0.925)], x, y, w, h, facing)

    # ── white leather upper — low-top, clean swept silhouette ─────────────
    upper = [(0.06, 0.85), (0.06, 0.46), (0.14, 0.34), (0.30, 0.30),
             (0.46, 0.30), (0.66, 0.34), (0.86, 0.46), (0.95, 0.62),
             (0.96, 0.85)]
    _poly(surf, _LEATHER_S, upper, x, y, w, h, facing)
    upper_face = [(0.08, 0.84), (0.08, 0.47), (0.16, 0.36), (0.30, 0.32),
                  (0.46, 0.32), (0.65, 0.36), (0.84, 0.47), (0.93, 0.62),
                  (0.94, 0.84)]
    _poly(surf, _LEATHER, upper_face, x, y, w, h, facing)

    # ── CUE · toe-cap stitched seam ───────────────────────────────────────
    # The standard tennis-shoe cue: one faint curved stitch line arcing across
    # the toe to split the toe cap from the vamp, so the toe box isn't dead.
    seam = [(0.66, 0.40), (0.74, 0.43), (0.82, 0.50), (0.88, 0.60)]
    pygame.draw.lines(surf, _LEATHER_S, False,
                      [_u(u, v, x, y, w, h, facing) for u, v in seam],
                      max(1, int(round(w * 0.016))))

    # ── collar notch + tongue (clean, tonal) ──────────────────────────────
    _poly(surf, _LEATHER_S, [(0.14, 0.44), (0.30, 0.32), (0.36, 0.40),
                             (0.20, 0.52)], x, y, w, h, facing)
    _poly(surf, _LEATHER, [(0.16, 0.45), (0.30, 0.35), (0.34, 0.41),
                           (0.20, 0.51)], x, y, w, h, facing)
    # Lace bars across the throat.
    for lv in (0.44, 0.52, 0.60):
        _line(surf, _LACE, (0.34, lv), (0.50, lv - 0.04), x, y, w, h, facing,
              max(1, h * 0.045))

    # ── CUE · perforation-dot column on the midfoot ───────────────────────
    # Where rivals run a side stripe, this model has only quiet perforations.
    # A deliberate evenly-spaced vertical arc of round holes, each with a soft
    # one-step-darker shadow under it so the column survives at 48px and never
    # reads as diagonal scratches.
    rad = max(1, int(round(w * 0.016)))
    dots = ((0.50, 0.46), (0.51, 0.54), (0.53, 0.62),
            (0.56, 0.70), (0.60, 0.77))
    for du, dv in dots:
        sx, sy = _u(du, dv + 0.012, x, y, w, h, facing)
        pygame.draw.circle(surf, _PERF_S, (sx, sy), rad)
        cx, cy = _u(du, dv, x, y, w, h, facing)
        pygame.draw.circle(surf, _PERF, (cx, cy), rad)

    # ── CUE · green heel tab ──────────────────────────────────────────────
    # The signature: a small coloured tab at the back collar. Shadow block
    # first, brighter green on top for a touch of dimension. The one colour
    # that has to survive at 16px, so it sits a notch more saturated.
    _poly(surf, _GREEN_D, [(0.055, 0.38), (0.125, 0.335), (0.150, 0.47),
                           (0.085, 0.555)], x, y, w, h, facing)
    _poly(surf, _GREEN, [(0.065, 0.39), (0.125, 0.355), (0.138, 0.46),
                         (0.085, 0.53)], x, y, w, h, facing)
