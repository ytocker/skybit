import math

import pygame


# WING BOOTS — legendary Hermes greave boot. The whole point is that the
# silhouette BREAKS the unit box outward: feathered ankle wings flare up
# (t < 0) and back past the heel (t < 0 in x after the facing flip), so even
# at 40px the outline reads "winged relic" and not "sneaker". The gold shell
# is a metal greave (light/dark pair gives the curved sheen), wrapped by a
# laurel band with a gemmed clasp. Wings are drawn as a few BOLD feather
# wedges (not fine barbs) so the shape holds when the foot shrinks; sparkle
# motes are kept tiny so they never compete with the wing read.

_GOLD    = (240, 200,  96)   # body gold
_GOLD_L  = (255, 246, 205)   # lit gold (sheen band)
_GOLD_D  = (158, 110,  34)   # deep warm gold (shadow / forged metal break)
_WHITE   = (255, 255, 255)   # feather white
_WHITE_D = (214, 222, 236)   # cool feather shadow
_LAUREL  = ( 92, 150,  78)   # olive laurel
_LAUREL_D= ( 58, 104,  52)
_GEM     = (111, 227, 255)   # cyan clasp gem / sparkle
_GEM_D   = ( 36, 138, 176)


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a side-profile WING BOOTS greave into box (x,y,w,h).

    Wings deliberately exceed the box (t<0 above, t<0 behind the heel) so the
    winged silhouette is unmistakable — callers must leave head/side room.
    """
    def px(t):
        return x + (t * w if facing == 1 else (1.0 - t) * w)

    def py(t):
        return y + t * h

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [(px(a), py(b)) for a, b in pts])

    def line(color, a, b, width):
        pygame.draw.line(surf, color, (px(a[0]), py(a[1])),
                         (px(b[0]), py(b[1])), max(1, int(round(width))))

    def dot(color, t, s):
        pygame.draw.circle(surf, color, (int(px(t[0])), int(py(t[1]))),
                           max(1, int(round(s))))

    sole_top = 0.86

    # ── ANKLE WINGS (drawn FIRST so the gold shell overlaps their roots) ───────
    # Two BOLD layered plumes, not straight darts. Each feather is built as a
    # broad wedge: a near-straight LEADING SPAR springs from the cuff up-and-out,
    # then the TRAILING EDGE arcs back in a convex fan of stepped barb-tips. The
    # convex sampling (a quarter-circle-ish sweep of points) is what makes the
    # outline read "plumage" rather than "paper airplane". The top plume genuinely
    # clears the cuff (tip near t -0.34) and the fan is wider+taller than the
    # gold shell, so the wing mass — not the boot — owns the silhouette and still
    # breaks outward as solid shapes at 40px.
    def feather(spar_root, spar_tip, fan_depth, color, edge, serrate=True):
        """A curved, BROAD wing feather. spar_root→spar_tip is the near-straight
        leading edge; the trailing edge sweeps back to the root as a convex arc
        (a solid bowed belly), with a few stepped barb-tips near the tip so the
        plume reads as feathers. `fan_depth` is how far the belly bulges
        heel-ward+down — that bulge is the wing's area, what keeps it solid and
        visible when the foot shrinks to 40px."""
        rx, ry = spar_root
        tx, ty = spar_tip
        # Perp-ish direction the belly bows toward: back (heel) and down.
        bow_dx, bow_dy = -0.62, 0.78
        pts = [spar_root, spar_tip]
        # Dense smooth arc => a filled convex fan, not a thin zigzag.
        n = 9
        for i in range(1, n + 1):
            u = i / (n + 1)                # tip(0) → root(1)
            bx = tx + (rx - tx) * u
            by = ty + (ry - ty) * u
            bow = math.sin(u * math.pi) * fan_depth
            # subtle outer serration only on the tip third — plume barbs
            if serrate and u < 0.45:
                bow *= 1.0 if (i % 2) else 0.86
            pts.append((bx + bow_dx * bow, by + bow_dy * bow))
        poly(color, pts)
        # hard leading-spar highlight so the white edge survives on dark night bg
        line(edge, spar_root, spar_tip, max(1, w * 0.026))

    # TOP plume — springs highest, clears the cuff (tip above the box, t<0).
    feather((0.16, 0.20), (-0.22, -0.36), 0.34, _WHITE_D, _WHITE)
    feather((0.17, 0.21), (-0.17, -0.32), 0.27, _WHITE, _WHITE)
    # LOWER plume — broader + sweeps further BACK past the heel, splayed down-out.
    feather((0.15, 0.30), (-0.44, 0.02), 0.36, _WHITE_D, _WHITE)
    feather((0.16, 0.31), (-0.37, 0.05), 0.28, _WHITE, _WHITE)
    # Gold forged root where both plumes spring from the cuff — ties wing to metal.
    poly(_GOLD_D, [
        (0.10, 0.34), (0.14, 0.16), (0.24, 0.20), (0.22, 0.34),
    ])
    line(_GOLD_L, (0.14, 0.17), (0.12, 0.33), max(1, w * 0.018))

    # ── GREAVE OUTSOLE (winged sandal sole, dark-gold tread) ───────────────────
    poly(_GOLD_D, [
        (0.06, 1.00), (0.94, 1.00), (0.98, 0.93),
        (0.90, 0.90), (0.10, 0.90), (0.06, 0.94),
    ])
    poly(_GOLD, [
        (0.08, 0.92), (0.10, sole_top), (0.90, sole_top),
        (0.95, 0.91), (0.95, 0.94), (0.10, 0.945),
    ])
    poly(_GOLD_L, [
        (0.10, sole_top), (0.90, sole_top), (0.88, 0.895), (0.12, 0.895),
    ])

    # ── GREAVE BOOT SHELL (curved gold metal, rises into a cuff) ───────────────
    # Toe-to-cuff metal body. The light/dark split runs vertically so the shell
    # reads as a rounded forged plate catching light along its front ridge.
    shell = [
        (0.10, sole_top), (0.12, 0.40), (0.22, 0.28),
        (0.40, 0.24), (0.62, 0.30), (0.84, 0.46),
        (0.93, 0.66), (0.93, sole_top),
    ]
    poly(_GOLD, shell)
    # WIDE lit sheen band running vertically down the front ridge — a true
    # specular stripe so the shell reads as curved polished metal, not putty.
    poly(_GOLD_L, [
        (0.58, 0.30), (0.78, 0.40), (0.90, 0.60), (0.90, sole_top),
        (0.74, sole_top), (0.72, 0.56), (0.56, 0.42),
    ])
    # Deep warm shadow wrapping the heel half — the dark side of the round plate.
    poly(_GOLD_D, [
        (0.10, sole_top), (0.12, 0.40), (0.22, 0.28), (0.30, 0.36),
        (0.24, 0.50), (0.23, sole_top),
    ])
    # Vertical greave seam (forged plate split) — survives shrink as one stroke.
    line(_GOLD_D, (0.50, 0.30), (0.50, sole_top), max(1, w * 0.018))

    # ── ANKLE CUFF + GEMMED CLASP ──────────────────────────────────────────────
    # The cuff rounds the top of the boot where the wings spring from.
    poly(_GOLD, [
        (0.14, 0.36), (0.20, 0.24), (0.40, 0.21),
        (0.52, 0.26), (0.50, 0.36), (0.30, 0.40),
    ])
    # Hard bright highlight riding the cuff curve so it reads as a forged
    # greave plate catching the light, not flat tan.
    poly(_GOLD_L, [
        (0.20, 0.24), (0.40, 0.21), (0.50, 0.25), (0.48, 0.28),
        (0.40, 0.25), (0.22, 0.28),
    ])
    # Gemmed clasp at the cuff front — the one cool accent on all that gold.
    clasp = (0.45, 0.31)
    dot(_GOLD_D, clasp, w * 0.055)
    dot(_GEM_D, clasp, w * 0.040)
    dot(_GEM, (clasp[0] - 0.010, clasp[1] - 0.010), w * 0.022)

    # ── LAUREL ANKLE WRAP (olive band over the cuff base) ──────────────────────
    # A short laurel sprig wraps the ankle — the mythic tell. Kept as a couple
    # of bold leaf wedges so it survives downscale rather than dissolving.
    poly(_LAUREL_D, [
        (0.18, 0.44), (0.30, 0.40), (0.50, 0.42), (0.50, 0.50),
        (0.30, 0.49), (0.18, 0.52),
    ])
    poly(_LAUREL, [
        (0.18, 0.44), (0.30, 0.40), (0.50, 0.42), (0.48, 0.46), (0.30, 0.45),
        (0.20, 0.48),
    ])
    for lt in (0.24, 0.34, 0.44):
        poly(_LAUREL, [
            (lt, 0.40), (lt + 0.04, 0.34), (lt + 0.07, 0.40),
        ])
        poly(_LAUREL_D, [
            (lt + 0.07, 0.40), (lt + 0.04, 0.34), (lt + 0.045, 0.40),
        ])

    # ── SPARKLE MOTES (tight — frame the wing fan, don't scatter) ──────────────
    # Clustered just off the plume tips so they read as motion-glint trailing the
    # wings, while the cyan clasp stays the single focal accent on the boot.
    for mt, ms in (((-0.24, -0.30), w * 0.022),
                   ((-0.30, 0.04), w * 0.018),
                   ((-0.06, -0.20), w * 0.014)):
        dot(_GEM, mt, ms)
        dot(_WHITE, (mt[0], mt[1]), max(1, ms * 0.45))
