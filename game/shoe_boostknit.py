import pygame

# Side-profile BOOST KNIT runner. Every coordinate is derived from the box
# (x,y,w,h) so the same code reads as a 104x62 product shot AND as a 15x10
# bird-foot sprite — no fixed-pixel detail that survives only at one scale.

# Sand/tan knit upper, creamy speckled boost midsole.
_UPPER       = (208, 184, 148)
_UPPER_DK    = (176, 152, 118)   # subtle 1px seam/shadow on the knit
_UPPER_HI    = (226, 206, 174)   # collar lip / front highlight
_COLLAR_DK   = (150, 124, 90)    # carved opening behind the crown
_SEAM        = (132, 108, 78)    # solid upper/sole divider band
_SOLE        = (244, 240, 230)   # creamy boost foam
_SOLE_DK     = (212, 206, 192)   # speckle ticks + bottom shadow
_OUTSOLE     = (190, 182, 168)   # rubber rim under the foam
_LOOP        = (150, 120, 86)    # heel pull-tab


def _fx(x, w, fx, facing):
    """Flip a 0..1 horizontal fraction when the shoe faces left."""
    return x + (fx if facing == 1 else 1.0 - fx) * w


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile BOOST KNIT sneaker into box (x,y,w,h)."""
    gx = y + h  # ground line
    # Below this size the wedge silhouette + heel bump must carry the read
    # alone; knit rows and foam speckle collapse into mud, so we drop them.
    detailed = w >= 22

    # Chunky ribbed boost midsole — trimmed to ~24.5% of the box height so its
    # sole proportion sits in the AIR FLYER / SHELL TOE family instead of
    # towering over the set. Ground line (gx) is unchanged, so it re-seats on
    # the shared baseline; the upper anchors off sole_top and follows down.
    sole_top = y + h * 0.755
    # Foam slab: thick at the heel, sweeping out long and low under the toe.
    foam = [
        (_fx(x, w, 0.04, facing), sole_top),
        (_fx(x, w, 0.04, facing), gx - h * 0.07),
        (_fx(x, w, 0.10, facing), gx),
        (_fx(x, w, 0.92, facing), gx),
        (_fx(x, w, 0.98, facing), gx - h * 0.10),
        (_fx(x, w, 0.95, facing), sole_top + h * 0.02),
        (_fx(x, w, 0.55, facing), sole_top - h * 0.02),
        (_fx(x, w, 0.28, facing), sole_top),
    ]
    pygame.draw.polygon(surf, _SOLE, foam)

    # Thin rubber outsole rim grounding the foam.
    pygame.draw.polygon(surf, _OUTSOLE, [
        (_fx(x, w, 0.10, facing), gx),
        (_fx(x, w, 0.92, facing), gx),
        (_fx(x, w, 0.98, facing), gx - h * 0.10),
        (_fx(x, w, 0.94, facing), gx - h * 0.04),
        (_fx(x, w, 0.10, facing), gx - h * 0.05),
        (_fx(x, w, 0.07, facing), gx - h * 0.02),
    ])

    if detailed:
        # Speckled-foam cue: close vertical ticks across the midsole only.
        n = max(3, int(w / 7))
        for i in range(n):
            f = 0.12 + (0.76 * i / (n - 1))
            tx = _fx(x, w, f, facing)
            ty0 = sole_top + h * 0.04
            ty1 = gx - h * 0.05
            pygame.draw.line(surf, _SOLE_DK, (tx, ty0), (tx, ty1), 1)

    # Knit upper as a runner WEDGE: tall heel, crown pushed back over the
    # instep (~x0.37), then a long low taper down to a defined toe tip.
    upper = [
        (_fx(x, w, 0.07, facing), sole_top - h * 0.02),       # heel base
        (_fx(x, w, 0.10, facing), y + h * 0.30),              # tall heel top
        (_fx(x, w, 0.18, facing), y + h * 0.22),              # collar back wall
        (_fx(x, w, 0.24, facing), y + h * 0.30),              # collar floor dip
        (_fx(x, w, 0.30, facing), y + h * 0.18),              # front collar lip
        (_fx(x, w, 0.37, facing), y + h * 0.09),              # instep crown
        (_fx(x, w, 0.55, facing), y + h * 0.20),
        (_fx(x, w, 0.72, facing), y + h * 0.36),              # long toe taper
        (_fx(x, w, 0.82, facing), y + h * 0.50),
        (_fx(x, w, 0.89, facing), y + h * 0.62),              # low toe tip
        (_fx(x, w, 0.86, facing), sole_top - h * 0.01),
        (_fx(x, w, 0.28, facing), sole_top),
    ]
    pygame.draw.polygon(surf, _UPPER, upper)

    # Carve the collar OPENING: a darker concave notch behind the crown reads
    # "foot goes in here," with a lighter front lip catching the light.
    pygame.draw.polygon(surf, _COLLAR_DK, [
        (_fx(x, w, 0.18, facing), y + h * 0.23),
        (_fx(x, w, 0.24, facing), y + h * 0.31),
        (_fx(x, w, 0.30, facing), y + h * 0.20),
        (_fx(x, w, 0.27, facing), y + h * 0.17),
    ])
    pygame.draw.line(surf, _UPPER_HI,
                     (_fx(x, w, 0.30, facing), y + h * 0.18),
                     (_fx(x, w, 0.37, facing), y + h * 0.10), 1)

    if detailed:
        # Horizontal knit lines confined to the upper's top half — woven
        # Primeknit texture that never bleeds into the clean toe box / sole.
        rows = max(2, int(h / 11))
        for i in range(rows):
            ry = y + h * (0.20 + 0.22 * i / max(1, rows - 1))
            x0 = _fx(x, w, 0.20, facing)
            x1 = _fx(x, w, 0.66 - 0.05 * i, facing)
            pygame.draw.line(surf, _UPPER_DK, (x0, ry), (x1, ry), 1)

    # Heel pull-tab — a real silhouette nub poking up+back past the collar.
    nub_w = max(2, int(w / 32))
    nx = _fx(x, w, 0.07, facing)
    pygame.draw.polygon(surf, _LOOP, [
        (_fx(x, w, 0.05, facing), y + h * 0.22),
        (_fx(x, w, 0.05, facing), y + h * 0.12),
        (_fx(x, w, 0.09, facing), y + h * 0.13),
        (_fx(x, w, 0.10, facing), y + h * 0.24),
    ])

    # Solid 1-2px dark band where the upper meets the foam — the seam that
    # keeps upper and sole reading as two distinct materials at a glance.
    band = max(1, int(h / 30))
    pygame.draw.line(surf, _SEAM,
                     (_fx(x, w, 0.10, facing), sole_top - h * 0.01),
                     (_fx(x, w, 0.86, facing), sole_top - h * 0.01), band + 1)
    # Bottom shadow seating the outsole on the ground.
    pygame.draw.line(surf, _SOLE_DK,
                     (_fx(x, w, 0.10, facing), gx - 1),
                     (_fx(x, w, 0.92, facing), gx - 1), 1)
