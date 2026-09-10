import pygame


# RETRO 1 — high-top basketball sneaker. The read is the colour-blocked AJ1
# silhouette in THREE clean alternating vertical blocks so it survives shrink:
# red toe box | black midfoot/lace panel | red heel counter, on a chunky white
# midsole, with a tall padded ankle collar (open at the top) that is the hero
# cue. All geometry is proportional so the same call works at product-shot size
# and at bird-foot size. The collar deliberately rises ABOVE the box top
# (t < 0), so callers/previews must leave vertical headroom.

_RED     = (206,  34,  40)
_RED_D   = (150,  20,  26)
_BLACK   = ( 28,  26,  32)
_BLACK_D = ( 12,  11,  16)
_WHITE   = (240, 238, 232)
_WHITE_D = (188, 184, 178)


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile RETRO 1 sneaker into box (x,y,w,h)."""
    # Work in facing=1 (toe right) space, then mirror coordinates if needed so
    # one body of geometry serves both directions.
    def px(t):
        return x + (t * w if facing == 1 else (1.0 - t) * w)

    def py(t):
        return y + t * h

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [(px(a), py(b)) for a, b in pts])

    def line(color, a, b, width):
        pygame.draw.line(surf, color, (px(a[0]), py(a[1])),
                         (px(b[0]), py(b[1])), max(1, int(round(width))))

    # Sole band lives in the bottom ~22% of the box; collar rises above the top.
    sole_top = 0.80

    # ── outsole (dark tread) + white midsole stack ─────────────────────────────
    poly(_BLACK_D, [
        (0.03, 1.00), (0.95, 1.00), (0.98, 0.92),
        (0.91, 0.89), (0.06, 0.89), (0.03, 0.94),
    ])
    # Chunky white midsole — thickened to match the set and ground the colour
    # block. Top edge is the shared baseline the rest of the set sits on.
    poly(_WHITE, [
        (0.04, 0.93), (0.07, sole_top), (0.91, sole_top),
        (0.96, 0.88), (0.96, 0.945), (0.92, 0.965),
        (0.07, 0.965),
    ])
    poly(_WHITE_D, [
        (0.04, 0.93), (0.07, 0.96), (0.07, sole_top), (0.055, sole_top),
    ])

    # ── BLOCK 2 (base) · black midfoot / lace panel ────────────────────────────
    # The dark central mass. Drawn first as the base; the two red blocks overlay
    # its front and rear so three alternating colours read at 48px.
    poly(_BLACK, [
        (0.20, sole_top), (0.20, 0.36), (0.34, 0.30),
        (0.58, 0.32), (0.66, 0.42), (0.66, sole_top),
    ])

    # ── BLOCK 1 (front) · red toe box ──────────────────────────────────────────
    # A distinct red wedge at the toe, cleanly separated from the heel red by the
    # black panel between them.
    poly(_RED, [
        (0.66, 0.42), (0.74, 0.42), (0.86, 0.50),
        (0.93, 0.64), (0.93, sole_top), (0.66, sole_top),
    ])
    poly(_RED_D, [
        (0.89, 0.66), (0.93, 0.64), (0.93, sole_top), (0.89, sole_top),
    ])
    # Toe-box / panel seam keeps the two front blocks crisp when shrunk.
    line(_BLACK_D, (0.66, 0.43), (0.66, sole_top), max(1, w * 0.012))

    # ── BLOCK 3 (rear) · red heel counter ──────────────────────────────────────
    # The heel red. Together with the collar above it, the rear reads taller-
    # than-long — that vertical heel mass IS the high-top signal at 16px.
    poly(_RED, [
        (0.07, sole_top), (0.07, 0.34), (0.16, 0.28),
        (0.24, 0.32), (0.20, sole_top),
    ])
    poly(_RED_D, [
        (0.07, sole_top), (0.07, 0.34), (0.105, 0.345), (0.105, sole_top),
    ])
    # Heel / panel seam.
    line(_BLACK_D, (0.205, 0.40), (0.205, sole_top), max(1, w * 0.012))

    # ── HERO · tall padded ankle collar with an open top ───────────────────────
    # A rounded, padded black collar rising well above the laces (t < 0), with a
    # red leather band wrapping its base. A dark ankle-hole notch sits at the top
    # so it reads as an OPENING you step into — not a flat tongue/slab.
    # Red collar band wrapping the base of the cuff over the heel.
    poly(_RED, [
        (0.14, 0.40), (0.16, 0.10), (0.34, 0.08),
        (0.40, 0.30), (0.30, 0.36), (0.20, 0.34),
    ])
    poly(_RED_D, [
        (0.30, 0.36), (0.40, 0.30), (0.40, 0.34), (0.30, 0.40),
    ])
    # Padded black collar pad — taller than it is long, rounded shoulders.
    collar = [
        (0.16, 0.22), (0.155, -0.04), (0.20, -0.18),
        (0.30, -0.22), (0.40, -0.16), (0.43, 0.02),
        (0.40, 0.20), (0.30, 0.26), (0.22, 0.24),
    ]
    poly(_BLACK, collar)
    # Padded-cuff highlight along the outer shoulder so the collar reads round.
    poly(_BLACK_D, [
        (0.155, -0.04), (0.20, -0.18), (0.30, -0.22),
        (0.27, -0.16), (0.20, -0.13), (0.175, -0.02),
    ])
    # Open ankle hole — a dark notch/ellipse sunk into the top of the collar so
    # the eye reads an opening rising clearly above the laces.
    # Keep the notch small enough that the padded ring still rings it when tiny.
    hole_c = (px(0.295), py(-0.05))
    rx = max(1, int(round(w * 0.060)))
    ry = max(1, int(round(h * 0.095)))
    pygame.draw.ellipse(surf, _BLACK_D,
                        (hole_c[0] - rx, hole_c[1] - ry, rx * 2, ry * 2))

    # ── lace panel · clean horizontal lace strokes on the black panel ──────────
    # Two-to-three bright laces spanning the throat; thick lines clamp to >=1px
    # so the "laced" cue survives the foot-sprite. No speckle/noise.
    lace_w = max(1, h * 0.045)
    for ty in (0.40, 0.52, 0.64):
        line(_WHITE, (0.32, ty - 0.02), (0.60, ty), lace_w)
        line(_WHITE_D, (0.32, ty - 0.005), (0.60, ty + 0.015),
             max(1, lace_w * 0.45))
