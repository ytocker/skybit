"""
NY CAP — navy 6-panel baseball cap with a white interlocking serif "NY"
monogram (a generic homage, not a traced mark). Procedural pygame draw
calls only; sized purely from head_w so it reads BIG (product shot) and
small (on Pip's head). The monogram is gated off below ~22px so the tiny
silhouette stays a clean navy cap + bill.
"""
import math
import pygame

# Crown is a mid royal/steel navy rather than midnight navy: on a dark-navy
# store card (18,14,40) a true navy crown has near-zero value separation and
# the silhouette dissolves, so the body is lifted ~25-30% in value and a
# bright RIM colour rakes the top-left edge to pop the shape off the card.
# The palette stays narrow — one royal navy, a darker seam navy, white, and a
# grey-green underbill that mimics the real cap's lining.
NAVY        = (48, 62, 116)   # mid royal/steel navy crown body
NAVY_D      = (30, 40, 82)    # seam / shadow navy
NAVY_HI     = (78, 96, 158)   # front-top catch-light
NAVY_RIM    = (120, 142, 206) # bright rim-light on the top-left silhouette edge
WHITE       = (244, 246, 252)
WHITE_D     = (200, 206, 222)
BILL_NAVY   = (38, 50, 96)
UNDERBILL   = (96, 110, 96)   # classic grey-green underbill
UNDERBILL_D = (74, 86, 74)
BUTTON      = (96, 116, 176)


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


def _poly(surf, color, pts):
    pygame.draw.polygon(surf, color, [(int(round(x)), int(round(y))) for x, y in pts])


def _arc_pts(cx, cy, rx, ry, a0, a1, n):
    """Sampled ellipse-arc points (angles in radians, screen y-down)."""
    out = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        out.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return out


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile NY CAP sized for a head of width head_w,
    centered at cx, base/brim line at base_y."""
    f = facing
    r = head_w * 0.5

    # --- Crown dome ----------------------------------------------------
    # The dome is a squashed half-ellipse seated over the round head's top.
    # Front (bill side, +x*f) is a touch higher and fuller than the back so
    # it reads as a forward-tilted baseball crown rather than a beanie.
    dome_h   = head_w * 0.62
    crown_cy = base_y - dome_h * 0.30
    rx_back  = r * 1.02
    rx_front = r * 1.08
    top_y    = base_y - dome_h

    # Underside curves slightly downward at the band so the cap looks
    # wrapped onto a round head instead of cut flat. A deeper dip pulls the
    # band down over the head's curve so there's no floating gap.
    band_dip = head_w * 0.16

    dome = []
    # back side up and over to front, sampled as two ellipse quadrants
    dome += _arc_pts(cx, crown_cy, rx_back * f, dome_h, math.pi, math.pi * 1.5, 10)
    dome += _arc_pts(cx, crown_cy, rx_front * f, dome_h, math.pi * 1.5, math.pi * 2.0, 10)
    # front band corner, dipping down onto the head, then back along the band
    dome.append((cx + rx_front * f, base_y))
    dome.append((cx + r * 0.55 * f, base_y + band_dip))
    dome.append((cx - r * 0.55 * f, base_y + band_dip))
    dome.append((cx - rx_back * f, base_y))
    _poly(surf, NAVY, dome)

    # Rim-light: a thin lighter line raked along the crown's top-left edge so
    # the silhouette separates from a dark navy backdrop instead of dissolving
    # into it. Traced over the back-and-top arc only (the lit side away from
    # the bill), and kept >=1px so it survives at the smallest size.
    rim_w = max(1, int(round(head_w * 0.045)))
    rim = _arc_pts(cx, crown_cy, rx_back * f, dome_h, math.pi, math.pi * 1.62, 14)
    rim_pts = [(int(round(px)), int(round(py))) for px, py in rim]
    if len(rim_pts) >= 2:
        pygame.draw.lines(surf, NAVY_RIM, False, rim_pts, rim_w)

    # Soft top highlight (front-top catches light) — a smaller inset dome.
    hi = []
    hi += _arc_pts(cx + r * 0.10 * f, crown_cy - dome_h * 0.04,
                   rx_front * 0.62 * f, dome_h * 0.66,
                   math.pi * 1.15, math.pi * 1.92, 14)
    hi.append((cx + r * 0.55 * f, crown_cy))
    _poly(surf, NAVY_HI, hi)

    # Lower-back shading for roundness.
    sh = [
        (cx - rx_back * f, base_y),
        (cx - rx_back * 0.94 * f, crown_cy),
        (cx - r * 0.30 * f, base_y),
        (cx - r * 0.55 * f, base_y + band_dip),
    ]
    _poly(surf, NAVY_D, sh)

    # --- Bill (curved, points right) -----------------------------------
    # A flat-ish stiff bill that droops slightly at the tip; built as a
    # closed shape from a top curve and a bottom curve.
    bill_len  = head_w * 0.74
    bill_y    = base_y + head_w * 0.06
    tip_x     = cx + (r * 0.80 + bill_len) * f
    tip_y     = bill_y + head_w * 0.12         # tip droops down
    root_x    = cx + r * 0.55 * f
    seam = max(1, int(round(head_w * 0.045)))

    top_curve = [
        (root_x, base_y + band_dip * 0.4),
        (cx + (r * 0.55 + bill_len * 0.5) * f, bill_y - head_w * 0.03),
        (cx + (r * 0.55 + bill_len * 0.85) * f, tip_y - head_w * 0.01),
        (tip_x, tip_y + head_w * 0.03),
    ]
    bot_curve = [
        (tip_x, tip_y + head_w * 0.11),
        (cx + (r * 0.55 + bill_len * 0.55) * f, bill_y + head_w * 0.20),
        (cx + r * 0.40 * f, base_y + band_dip),
    ]
    bill = top_curve + bot_curve
    _poly(surf, UNDERBILL, bill)

    # Top face of the bill (navy) sits above the grey-green underbill edge.
    bill_top = top_curve + [
        (tip_x - head_w * 0.05 * f, tip_y + head_w * 0.045),
        (cx + (r * 0.55 + bill_len * 0.45) * f, bill_y + head_w * 0.10),
        (root_x, base_y + band_dip * 0.4),
    ]
    _poly(surf, BILL_NAVY, bill_top)
    # Underbill dark edge for thickness.
    _poly(surf, UNDERBILL_D, [
        (tip_x, tip_y + head_w * 0.085),
        (tip_x - head_w * 0.05 * f, tip_y + head_w * 0.045),
        (cx + (r * 0.55 + bill_len * 0.45) * f, bill_y + head_w * 0.17),
    ])
    # Bill top sheen.
    pygame.draw.line(
        surf, NAVY_HI,
        (int(root_x + r * 0.10 * f), int(base_y + band_dip * 0.2)),
        (int(cx + (r * 0.55 + bill_len * 0.6) * f), int(bill_y - head_w * 0.01)),
        max(1, int(round(head_w * 0.03))),
    )

    # --- Front band -----------------------------------------------------
    band_h = head_w * 0.14
    band = [
        (cx - rx_back * 0.96 * f, base_y - band_h * 0.2),
        (cx + rx_front * 0.98 * f, base_y - band_h * 0.2),
        (cx + rx_front * 0.92 * f, base_y + band_dip),
        (cx - rx_back * 0.92 * f, base_y + band_dip),
    ]
    _poly(surf, NAVY_D, band)

    # --- Seams + button (skip when too small to resolve) ---------------
    if head_w >= 16:
        # Panel seams radiating from the crown button down the dome.
        for frac in (0.30, 0.70):
            sx = cx + (rx_front * (frac - 0.5) * 2.0) * 0.55 * f
            pygame.draw.line(
                surf, NAVY_D,
                (int(cx + r * 0.05 * f), int(top_y + dome_h * 0.10)),
                (int(sx), int(base_y - band_h * 0.1)),
                seam,
            )
        # Top button.
        br = max(1, int(round(head_w * 0.05)))
        pygame.draw.circle(surf, BUTTON, (int(cx + r * 0.04 * f), int(top_y + dome_h * 0.07)), br + 1)
        pygame.draw.circle(surf, NAVY_HI, (int(cx + r * 0.04 * f), int(top_y + dome_h * 0.07)), br)

    # --- Interlocking "NY" monogram (hero cue) -------------------------
    # Gated off below ~22px so the tiny on-bird silhouette stays clean.
    if head_w >= 22:
        _draw_ny(surf, cx, base_y, head_w, crown_cy, dome_h, f)


def _draw_ny(surf, cx, base_y, head_w, crown_cy, dome_h, f):
    """White interlocking serif N + Y on the front panel — a generic
    homage. The N is set back (toward the crown) and the Y overlaps in
    front, both tilted to follow the forward-angled front panel so the
    pair reads in profile."""
    # Monogram cell, slightly forward of crown center and tilted with panel.
    mx   = cx + head_w * 0.20 * f
    my   = base_y - dome_h * 0.42
    s    = head_w * 0.30                 # glyph height scale
    sw   = max(1, int(round(head_w * 0.052)))   # stroke width
    skew = 0.16 * f                      # panel-follow lean

    def P(ux, uy):
        # unit glyph space -> screen, with a slight forward lean (skew)
        x = mx + (ux * s) * f + (uy * s) * skew
        y = my + uy * s
        return (x, y)

    def stroke(p0, p1, w, color):
        pygame.draw.line(surf, color, (int(p0[0]), int(p0[1])),
                         (int(p1[0]), int(p1[1])), w)

    # Subtle navy drop so the white pops off the navy crown.
    dsh = (12, 16, 40)
    off = (head_w * 0.018 * f, head_w * 0.022)

    def stroke_d(p0, p1, w):
        stroke((p0[0] + off[0], p0[1] + off[1]),
               (p1[0] + off[0], p1[1] + off[1]), w, dsh)

    # --- N : two verticals + a diagonal. Sits toward the back. ---------
    n_l_t, n_l_b = P(-0.62, -0.55), P(-0.62, 0.55)
    n_r_t, n_r_b = P(-0.06, -0.55), P(-0.06, 0.55)
    # --- Y : a V from two arms meeting at center, plus a stem down. ----
    y_la_t = P(0.04, -0.55)
    y_ra_t = P(0.70, -0.55)
    y_mid  = P(0.37, 0.02)
    y_stem = P(0.37, 0.55)

    # Shadow pass (drawn first, slightly offset).
    stroke_d(n_l_t, n_l_b, sw)
    stroke_d(n_r_t, n_r_b, sw)
    stroke_d(n_l_t, n_r_b, sw)
    stroke_d(y_la_t, y_mid, sw)
    stroke_d(y_ra_t, y_mid, sw)
    stroke_d(y_mid, y_stem, sw)

    # White glyph pass.
    stroke(n_l_t, n_l_b, sw, WHITE)
    stroke(n_r_t, n_r_b, sw, WHITE)
    stroke(n_l_t, n_r_b, sw, WHITE)   # N diagonal
    stroke(y_la_t, y_mid, sw, WHITE)  # Y left arm
    stroke(y_ra_t, y_mid, sw, WHITE)  # Y right arm
    stroke(y_mid, y_stem, sw, WHITE)  # Y stem

    # Serif caps — short cross-bars at stroke ends sell the classic serif.
    serif = max(1, int(round(head_w * 0.05)))
    sh = head_w * 0.018
    for (px, py) in (n_l_t, n_r_t, y_la_t, y_ra_t):
        pygame.draw.line(surf, WHITE, (int(px - serif), int(py)), (int(px + serif), int(py)), sw)
    for (px, py) in (n_l_b, n_r_b, y_stem):
        pygame.draw.line(surf, WHITE, (int(px - serif), int(py)), (int(px + serif), int(py)), sw)

    # The Y overlaps in FRONT of the N where its left arm crosses — redraw
    # that arm's top segment so it reads as interlocking, not just adjacent.
    stroke(y_la_t, y_mid, sw, WHITE)
    pygame.draw.line(surf, WHITE,
                     (int(y_la_t[0] - serif), int(y_la_t[1])),
                     (int(y_la_t[0] + serif), int(y_la_t[1])), sw)
