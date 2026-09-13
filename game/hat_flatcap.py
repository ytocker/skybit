"""
FLAT CAP (newsboy) — a low, single-piece tweed panel that slumps forward
over the brow and overhangs a SHORT stiff front brim, the classic
triangular flat-cap profile. Procedural pygame draw calls only; sized
purely from head_w so it reads BIG (product shot) and small (on Pip's
head). Earthy heathered colorway with a subtle 2-tone fleck/dither that
suggests tweed. The tweed weave is a large-size read-luxury only: it is
gated off entirely below ~40px so the small on-bird silhouette stays a
clean forward-flopped panel + short brim with no speckle mud.
"""
import math
import pygame


# A flat cap lives or dies on its earthy heathered tweed read, so the
# palette is a tight family: a mid heather brown panel, a lighter top
# catch-light, a darker brow shade where the panel slumps, plus two fleck
# tones (warm + cool) that dither into a tweed weave. The brim is a touch
# desaturated/darker so the stiff front piece separates from the soft panel.
TWEED      = (122, 104, 80)    # mid heathered brown panel
TWEED_HI   = (150, 132, 104)   # sunlit panel top
TWEED_SH   = (92, 76, 58)      # brow / underside shade
FLECK_WARM = (160, 140, 104)   # light tan slub
FLECK_COOL = (84, 84, 92)      # cool grey fleck (the "grey" in the heather)
BRIM       = (78, 64, 48)      # stiff front brim top
BRIM_SH    = (54, 43, 32)      # brim underside / edge
SEAM       = (96, 80, 60)      # faint panel seam


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
    """Draw a side-profile FLAT CAP (newsboy) sized for a head of width
    head_w, centered at cx, base line at base_y."""
    f = facing
    r = head_w * 0.5

    # --- Short stiff front brim (points right) -------------------------
    # Drawn first so the soft panel can overhang and overlap its root.
    # A flat cap brim is small and stiff: a thin, near-flat tab that the
    # panel front flops over. It sits just below the brow line.
    brim_len = head_w * 0.40
    brim_y   = base_y + head_w * 0.04
    root_x   = cx + r * 0.46 * f
    tip_x    = cx + (r * 0.62 + brim_len) * f
    tip_y    = brim_y + head_w * 0.045          # slight downward stiffness

    brim_top = [
        (root_x, brim_y - head_w * 0.02),
        (cx + (r * 0.62 + brim_len * 0.5) * f, brim_y - head_w * 0.005),
        (tip_x, tip_y),
    ]
    brim_bot = [
        (tip_x, tip_y + head_w * 0.075),
        (cx + (r * 0.62 + brim_len * 0.5) * f, brim_y + head_w * 0.115),
        (root_x, brim_y + head_w * 0.10),
    ]
    _poly(surf, BRIM_SH, brim_top + brim_bot)          # underside / thickness
    _poly(surf, BRIM, brim_top + [                     # top face above it
        (tip_x - head_w * 0.04 * f, tip_y + head_w * 0.035),
        (cx + (r * 0.62 + brim_len * 0.5) * f, brim_y + head_w * 0.05),
        (root_x, brim_y + head_w * 0.045),
    ])

    # --- Low panel / crown ---------------------------------------------
    # The whole flat-cap read: a LOW rounded dome (much flatter than a
    # baseball crown) whose front bulges FORWARD and DOWN past the brim
    # root, overhanging the brim. Back of the panel is fuller and droops
    # a touch behind the head for the soft slumped look.
    dome_h   = head_w * 0.34                     # low: that's a flat cap
    crown_cy = base_y - dome_h * 0.22
    rx_back  = r * 1.04
    rx_front = r * 1.00
    top_y    = base_y - dome_h

    # The forward flop: the panel front comes down BELOW base_y and out
    # over the brim root, the signature overhang.
    flop_x = cx + (r * 0.88) * f
    flop_y = base_y + head_w * 0.10

    panel = []
    # back: up and over from low-back to crown top
    panel += _arc_pts(cx, crown_cy, rx_back * f, dome_h, math.pi, math.pi * 1.5, 12)
    # front-top quadrant, then push out/down into the forward flop
    panel += _arc_pts(cx, crown_cy, rx_front * f, dome_h, math.pi * 1.5, math.pi * 1.86, 8)
    panel.append((flop_x, flop_y))                       # overhang lip
    panel.append((cx + r * 0.42 * f, base_y + head_w * 0.07))  # tuck onto brim
    # underside curve back onto the round head
    panel.append((cx - r * 0.10 * f, base_y + head_w * 0.075))
    panel.append((cx - r * 0.62 * f, base_y + head_w * 0.045))
    panel.append((cx - rx_back * f, base_y))
    _poly(surf, TWEED, panel)

    # Sunlit top: an inset cap over the front-top of the panel.
    hi = []
    hi += _arc_pts(cx + r * 0.06 * f, crown_cy - dome_h * 0.05,
                   rx_front * 0.70 * f, dome_h * 0.66,
                   math.pi * 1.12, math.pi * 1.80, 12)
    hi.append((cx + r * 0.50 * f, crown_cy + dome_h * 0.10))
    hi.append((cx - r * 0.30 * f, crown_cy + dome_h * 0.10))
    _poly(surf, TWEED_HI, hi)

    # Brow shade: the underside of the forward flop where it overhangs the
    # brim falls into shadow — this is what sells the "slumps over the
    # brow" depth.
    brow = [
        (cx + r * 0.42 * f, base_y + head_w * 0.005),
        (flop_x, flop_y - head_w * 0.01),
        (cx + r * 0.78 * f, base_y + head_w * 0.10),
        (cx + r * 0.40 * f, base_y + head_w * 0.075),
        (cx - r * 0.06 * f, base_y + head_w * 0.075),
    ]
    _poly(surf, TWEED_SH, brow)

    # Lower-back shade for roundness on the head.
    _poly(surf, TWEED_SH, [
        (cx - rx_back * f, base_y),
        (cx - rx_back * 0.92 * f, crown_cy + dome_h * 0.2),
        (cx - r * 0.32 * f, base_y + head_w * 0.04),
        (cx - r * 0.62 * f, base_y + head_w * 0.045),
    ])

    # --- Faint panel seam (cue) ----------------------------------------
    # A single soft seam arcing from the crown down toward the brow sells
    # the single-piece flat-cap construction without newsboy panel-clutter.
    if head_w >= 14:
        sw = max(1, int(round(head_w * 0.035)))
        seam_pts = _arc_pts(cx + r * 0.10 * f, crown_cy + dome_h * 0.05,
                            rx_front * 0.78 * f, dome_h * 0.92,
                            math.pi * 1.32, math.pi * 1.80, 8)
        pygame.draw.lines(surf, SEAM, False,
                          [(int(x), int(y)) for x, y in seam_pts], sw)

    # --- Tweed fleck/dither (large-size luxury only) -------------------
    # The weave only reads as tweed at product-shot scale; below ~40px the
    # flecks collapse into noise/dirt and muddy the silhouette, so the
    # texture fades out entirely and we keep a clean flat-fabric panel.
    if head_w >= 40:
        _fleck_tweed(surf, cx, base_y, head_w, crown_cy, dome_h, top_y,
                     rx_back, rx_front, f)


def _fleck_tweed(surf, cx, base_y, head_w, crown_cy, dome_h, top_y,
                 rx_back, rx_front, f):
    """Scatter a deterministic 2-tone fleck across the panel to read as a
    heathered tweed weave. Pseudo-random but seeded from grid coords so it
    is stable frame-to-frame and identical across desktop/web."""
    r = head_w * 0.5
    # Fleck dot size scales with the hat; a touch under 1px would vanish.
    d = max(1, int(round(head_w * 0.028)))
    # Grid step in panel space — wider step thins the weave. Kept airy on
    # purpose: a sparse fleck reads as tweed without crowding into grit.
    step = max(2, int(round(head_w * 0.120)))

    x0 = int(cx - r * 1.0)
    x1 = int(cx + r * 1.05)
    y0 = int(top_y + dome_h * 0.08)
    y1 = int(base_y + head_w * 0.06)

    # Approximate the panel as an ellipse for an in-bounds membership test
    # so flecks never spill past the silhouette onto the navy background.
    ex = r * 1.04
    ey = dome_h * 1.18
    ecy = crown_cy + dome_h * 0.30

    for gy in range(y0, y1, step):
        for gx in range(x0, x1, step):
            # Cheap deterministic hash -> jitter + tone selection.
            h = (gx * 73856093) ^ (gy * 19349663)
            jx = ((h >> 3) & 3) - 1
            jy = ((h >> 7) & 3) - 1
            px = gx + jx
            py = gy + jy
            # Inside the panel ellipse?
            nx = (px - cx) / ex
            ny = (py - ecy) / ey
            if nx * nx + ny * ny > 1.0:
                continue
            # Skip the forward-flop / brow band so the shaded overhang stays
            # readable rather than speckled flat.
            if (px - cx) * f > r * 0.42 and py > base_y - head_w * 0.02:
                continue
            tone = FLECK_WARM if (h & 8) else FLECK_COOL
            # Cool flecks are sparser — heather is mostly warm with grey grit.
            if tone is FLECK_COOL and (h & 0x30):
                continue
            pygame.draw.rect(surf, tone, (px, py, d, d))
