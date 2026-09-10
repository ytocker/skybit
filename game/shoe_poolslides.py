import pygame


# Pool-slide palette. The band is a saturated slate-blue rubber so the three
# stripes can be bright white and survive the read all the way down to ~15px.
# The footbed is a clearly lighter sandy EVA grey so it never merges with the
# band into one dark mass; a thin groove line separates the two on the side.
_BAND = (44, 70, 120)            # saturated rubber strap
_BAND_HI = (78, 110, 168)        # rounded sheen on the strap crown
_BAND_DK = (28, 46, 84)          # strap underside / arch shadow
_STRIPE = (242, 246, 252)        # bright stripes across the band
_FOOTBED = (176, 172, 162)       # sandy/EVA grey slab (much lighter than band)
_FOOTBED_HI = (206, 202, 192)    # top-surface highlight skim
_SOLE = (132, 128, 118)          # darker sole underbody beneath the footbed
_GROOVE = (108, 104, 96)         # 1px groove between band and footbed


def _mirror_pts(pts, cx):
    return [(2 * cx - px, py) for (px, py) in pts]


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile POOL SLIDE sandal into box (x,y,w,h)."""
    cx = x + w * 0.5

    def px(fx, fy):
        # Proportional point, mirrored about the box centre when facing left so
        # the open toe always points the requested way.
        nx = fx if facing >= 0 else (1.0 - fx)
        return (x + nx * w, y + fy * h)

    ground = y + h

    # ---- FOOTBED: a low flat slab sitting on the shared baseline. ----
    # Kept thin and ground-hugging (like the flip-flop sole) so at 16px the
    # silhouette is a flat sole with one arched bump on top — never a sneaker.
    # Toe and heel are squared-but-open; the slab does NOT wrap upward into an
    # upper, leaving the band to float over clear daylight.
    bed_top = 0.78          # top surface of the footbed
    bed_bot = 0.95          # footbed / sole-edge boundary
    heel_x = 0.07
    toe_x = 0.93

    footbed = [
        (px(heel_x, bed_top + 0.03)),    # heel: slight curl up, open scoop
        (px(0.22, bed_top - 0.01)),
        (px(0.50, bed_top + 0.01)),      # gentle arch dip under the strap
        (px(0.78, bed_top - 0.01)),
        (px(toe_x, bed_top + 0.03)),     # toe: slight curl up, open scoop
        (px(toe_x, bed_bot)),
        (px(heel_x, bed_bot)),
    ]
    pygame.draw.polygon(surf, _FOOTBED, footbed)

    # Darker sole edge band hugging the ground beneath the footbed slab.
    sole_edge = [
        (px(heel_x, bed_bot)),
        (px(toe_x, bed_bot)),
        (px(toe_x - 0.01, 1.0)),
        (px(heel_x + 0.01, 1.0)),
    ]
    pygame.draw.polygon(surf, _SOLE, sole_edge)

    # Thin highlight skim along the footbed top to sell the molded EVA surface.
    pygame.draw.line(surf, _FOOTBED_HI, px(heel_x, bed_top + 0.02),
                     px(toe_x, bed_top + 0.02), max(1, int(h * 0.035)))

    # ---- BAND: a single thick arched strap floating over open space. ----
    # The band spans only the midfoot and its underside arches WELL above the
    # footbed, cutting a clear empty wedge of negative space (open toe in front,
    # open heel behind, daylight gap below the crown). This is the open-slide
    # read — strap over a gap, not a covered upper.
    b_back = 0.33           # narrow footprint: band lands only mid-span so the
    b_front = 0.67          # toe in front and heel behind stay clearly open
    band_under = 0.70       # where the band legs meet the footbed (top of gap)
    arch_inner = 0.34       # underside crown — pulled high to open a big gap
    band_peak = 0.09        # outer crown of the arched band
    leg = 0.04              # how far the band legs splay at their feet

    band = [
        (px(b_back - leg, band_under)),          # back foot of the strap
        (px(b_back - leg - 0.02, band_under - 0.12)),
        (px(0.39, band_peak + 0.04)),
        (px(0.50, band_peak)),                   # outer crown
        (px(0.61, band_peak + 0.04)),
        (px(b_front + leg + 0.02, band_under - 0.12)),
        (px(b_front + leg, band_under)),         # front foot of the strap
        # inner underside — arches steeply up to leave a tall clear gap so the
        # daylight wedge under the crown is unmistakable (foot slides in here)
        (px(b_front - 0.01, band_under - 0.05)),
        (px(0.58, arch_inner + 0.05)),
        (px(0.50, arch_inner)),                  # underside crown of the arch
        (px(0.42, arch_inner + 0.05)),
        (px(b_back + 0.01, band_under - 0.05)),
    ]
    pygame.draw.polygon(surf, _BAND, band)

    # Soft top highlight on the band crown for rounded-rubber sheen.
    pygame.draw.lines(surf, _BAND_HI, False,
                      [px(0.41, band_peak + 0.05), px(0.50, band_peak + 0.015),
                       px(0.59, band_peak + 0.05)], max(1, int(h * 0.045)))

    # Darker underside line along the inner arch to deepen the open gap.
    pygame.draw.lines(surf, _BAND_DK, False,
                      [px(b_back + 0.02, band_under - 0.06),
                       px(0.50, arch_inner + 0.02),
                       px(b_front - 0.02, band_under - 0.06)],
                      max(1, int(h * 0.035)))

    # ---- HERO CUE: three thick bright stripes running ACROSS the band. ----
    # Each stripe is a band of constant proportional width laid across the arch,
    # evenly spaced and contrasting the slate band so the trio survives to 48px.
    # They follow the slant from the strap's front foot up toward its back, so
    # the rhythm stays legible at every size.
    sw = max(1.0, w * 0.04)         # stripe half-width, scales with box
    span = 0.22                     # total horizontal spread of the three centers
    base = 0.50 - span * 0.5        # first center, trio centred on the crown
    step = span * 0.5               # gap between stripe centers
    for i in range(3):
        c = base + i * step
        low = px(c + 0.04, arch_inner + 0.04)     # lower end on the band underside
        high = px(c - 0.04, band_peak + 0.08)     # upper end near the crown
        quad = [
            (low[0] - sw, low[1]),
            (low[0] + sw, low[1]),
            (high[0] + sw, high[1]),
            (high[0] - sw, high[1]),
        ]
        pygame.draw.polygon(surf, _STRIPE, quad)

    # ---- 1px groove between band feet and footbed for side-profile depth. ----
    pygame.draw.line(surf, _GROOVE, px(b_back - leg, band_under),
                     px(b_front + leg, band_under), 1)
