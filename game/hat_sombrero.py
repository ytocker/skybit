"""Procedural side-profile SOMBRERO for Skybit's coin Store.

One public entry: `draw_hat(surf, cx, base_y, head_w, facing=1)`.

The sombrero reads almost entirely through its silhouette: a VERY WIDE
brim (~2x head_w total) that sweeps down past the head and curls UP at
both outer edges, topped by a tall conical crown. Two hero cues sit on
that shape — a colourful embroidered zigzag BAND wrapping the cone base
and a little pom/tassel dangling from the upturned brim edge. Warm woven
straw tones with faint radial texture lines fan across the brim. All
geometry derives from (cx, base_y, head_w) so the same code scales from a
hero head (head_w~80) to a tiny product pip (head_w~18). Below ~22px the
band, tassel and straw texture are gated off so the icon keeps only the
clean wide-brim + cone read.

No image files, no real brand marks — generic festival straw + embroidery.
"""
import pygame

# ── straw palette (warm woven tan) ───────────────────────────────────────────
# Straw catches light brightly along ridges and goes warm-amber in the
# weave shadow. The crown is the same fibre but reads a touch deeper
# because it curves away from the light.
STRAW_HI  = (236, 202, 132)
STRAW     = (212, 170,  96)
STRAW_MID = (190, 146,  76)
STRAW_DK  = (150, 110,  54)
UNDER     = (118,  84,  44)   # brim underside — in shadow

# Embroidered band: a bright fiesta zigzag. Kept to two saturated hats of
# colour over a darker ribbon so it reads as stitching, not a paint stripe.
BAND_BG   = ( 96,  40,  58)
BAND_RED  = (212,  62,  66)
BAND_GRN  = ( 64, 168,  96)
BAND_GOLD = (240, 206, 110)
POM       = (224,  86,  92)


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile sombrero sized for a round head of diameter head_w.

    cx        head centre x.
    base_y    brim line — the hat seats on a head whose crown-top is here.
    head_w    head diameter; all proportions derive from it.
    facing    +1 = looking right; -1 mirrors the whole hat. (The sombrero is
              near-symmetric, so facing mostly nudges the tassel side.)
    """
    f = 1 if facing >= 0 else -1
    hw = head_w / 2.0

    detailed = head_w >= 22

    # The brim is the dominant read: it reaches roughly a full head-width
    # past the head on each side, so total span ~2x head_w.
    brim_out = hw * 2.05           # outer edge x-offset from cx
    # Crown narrower than the head so the brim collar tucks under it.
    crown_hw = hw * 0.62
    crown_h  = head_w * 0.92       # tall cone above base_y

    # The brim dips below base_y as it leaves the crown, then curls back UP
    # at the tips — the signature upturned sombrero edge.
    dip      = head_w * 0.30       # how far the mid-brim droops below base_y
    curl     = head_w * 0.34       # how high the outer tips rise back up
    thick    = max(2.0, head_w * 0.13)

    seat_y = base_y - head_w * 0.02   # where cone base meets the brim collar

    left_x  = cx - brim_out
    right_x = cx + brim_out
    curl_in = head_w * 0.16           # tip width before it curls up

    # ── BRIM ─────────────────────────────────────────────────────────────────
    # Side profile of a wide upturned disc: from each upturned tip the edge
    # sweeps down to a low belly under the crown, then back up symmetrically.
    # Drawn as a closed band (top sheet over a shadowed underside).
    def brim_top():
        return [
            (left_x,  base_y - curl),                       # left tip (raised)
            (left_x + curl_in,        base_y - curl * 0.30),
            (cx - crown_hw * 1.15,    base_y + dip),        # left belly
            (cx,                      base_y + dip * 1.06),  # lowest centre
            (cx + crown_hw * 1.15,    base_y + dip),        # right belly
            (right_x - curl_in,       base_y - curl * 0.30),
            (right_x, base_y - curl),                       # right tip (raised)
        ]

    top = brim_top()
    # Underside echoes the top, offset down by the brim thickness, tips pinched.
    bot = [
        (left_x  + head_w * 0.02, top[0][1] + thick * 0.5),
        (top[1][0],               top[1][1] + thick * 0.85),
        (top[2][0],               top[2][1] + thick),
        (top[3][0],               top[3][1] + thick),
        (top[4][0],               top[4][1] + thick),
        (top[5][0],               top[5][1] + thick * 0.85),
        (right_x - head_w * 0.02, top[6][1] + thick * 0.5),
    ]

    pygame.draw.polygon(surf, UNDER, top + list(reversed(bot)))
    pygame.draw.polygon(surf, STRAW_MID, top)

    if detailed:
        # Radial straw texture: faint fibres fanning from the crown out to the
        # brim edge, the hand-woven palm look.
        for k in range(-3, 4):
            t = k / 3.0
            ex = cx + t * brim_out
            ey = (base_y - curl) if abs(t) > 0.82 else (base_y + dip * (1 - abs(t) * 0.5))
            sx = cx + t * crown_hw * 1.05
            sy = seat_y + head_w * 0.04
            pygame.draw.line(surf, STRAW_DK, (sx, sy), (ex, ey),
                             max(1, round(head_w * 0.012)))
        # Bright catch along the top of each upturned tip.
        pygame.draw.line(surf, STRAW_HI, top[0],
                         (top[1][0], top[1][1]), max(1, round(head_w * 0.03)))
        pygame.draw.line(surf, STRAW_HI, top[6],
                         (top[5][0], top[5][1]), max(1, round(head_w * 0.03)))

    # Crisp upper rim line so the woven edge reads as a sheet, not a slab.
    pygame.draw.lines(surf, STRAW, False, top, max(1, round(head_w * 0.022)))

    # ── CROWN (tall cone) ──────────────────────────────────────────────────────
    # A rounded-tip cone rising from the brim collar. Light from upper-left,
    # so the facing-back side carries the highlight and the front falls into
    # shade.
    tip_y   = base_y - crown_h
    tip_x   = cx - f * head_w * 0.03      # apex leans very slightly off-centre
    base_l  = cx - crown_hw
    base_r  = cx + crown_hw

    cone = [
        (base_l,  seat_y),
        (base_l + crown_hw * 0.10, base_y - crown_h * 0.50),
        (tip_x - head_w * 0.06,    tip_y + head_w * 0.07),
        (tip_x,                    tip_y),                  # rounded apex
        (tip_x + head_w * 0.06,    tip_y + head_w * 0.07),
        (base_r - crown_hw * 0.10, base_y - crown_h * 0.50),
        (base_r,  seat_y),
    ]
    pygame.draw.polygon(surf, STRAW, cone)

    if detailed:
        # Lit (back/left) flank of the cone.
        pygame.draw.polygon(surf, STRAW_HI, [
            (base_l, seat_y),
            (base_l + crown_hw * 0.10, base_y - crown_h * 0.50),
            (tip_x - head_w * 0.05, tip_y + head_w * 0.08),
            (tip_x, tip_y),
            (tip_x, seat_y),
        ] if f >= 0 else [
            (base_r, seat_y),
            (base_r - crown_hw * 0.10, base_y - crown_h * 0.50),
            (tip_x + head_w * 0.05, tip_y + head_w * 0.08),
            (tip_x, tip_y),
            (tip_x, seat_y),
        ])
        # Shaded (front) flank.
        pygame.draw.polygon(surf, STRAW_MID, [
            (base_r, seat_y),
            (base_r - crown_hw * 0.10, base_y - crown_h * 0.50),
            (tip_x + head_w * 0.05, tip_y + head_w * 0.08),
            (tip_x, tip_y),
            (tip_x, seat_y),
        ] if f >= 0 else [
            (base_l, seat_y),
            (base_l + crown_hw * 0.10, base_y - crown_h * 0.50),
            (tip_x - head_w * 0.05, tip_y + head_w * 0.08),
            (tip_x, tip_y),
            (tip_x, seat_y),
        ])

    # ── EMBROIDERED BAND (zigzag) ──────────────────────────────────────────────
    # Wraps the cone just above the collar. A dark ribbon carrying a fiesta
    # red/green zigzag with gold dots — the second hero cue.
    band_h = max(3.0, head_w * 0.16)
    band_top = seat_y - head_w * 0.05 - band_h
    bl, br = base_l + head_w * 0.02, base_r - head_w * 0.02

    pygame.draw.polygon(surf, BAND_BG, [
        (bl, band_top), (br, band_top),
        (br, band_top + band_h), (bl, band_top + band_h),
    ])

    if detailed:
        # Zigzag built from alternating up/down triangles across the ribbon.
        span = br - bl
        n = max(4, round(span / max(3.0, head_w * 0.14)))
        step = span / n
        mid = band_top + band_h * 0.5
        amp = band_h * 0.34
        for i in range(n):
            x0 = bl + i * step
            x1 = x0 + step
            up = (i % 2 == 0)
            col = BAND_RED if up else BAND_GRN
            apex = mid - amp if up else mid + amp
            pygame.draw.polygon(surf, col, [
                (x0, mid + (amp if up else -amp) * 0.4),
                ((x0 + x1) * 0.5, apex),
                (x1, mid + (amp if up else -amp) * 0.4),
            ])
        # Gold accent line top and bottom edges of the ribbon.
        gw = max(1, round(head_w * 0.018))
        pygame.draw.line(surf, BAND_GOLD, (bl, band_top + gw),
                         (br, band_top + gw), gw)
        pygame.draw.line(surf, BAND_GOLD, (bl, band_top + band_h - gw),
                         (br, band_top + band_h - gw), gw)

    # ── POM / TASSEL on the upturned brim edge ─────────────────────────────────
    # A little dangling ball-trim off the front-facing tip — the festival
    # finishing touch. Gated with the rest of the detail.
    if detailed:
        tip = top[6] if f >= 0 else top[0]
        px = tip[0] - f * head_w * 0.02
        py = tip[1] + head_w * 0.04
        # short cord
        pygame.draw.line(surf, BAND_GOLD, (px, py),
                         (px, py + head_w * 0.10), max(1, round(head_w * 0.02)))
        r = max(2, round(head_w * 0.07))
        pygame.draw.circle(surf, POM, (round(px), round(py + head_w * 0.13 + r)), r)
        pygame.draw.circle(surf, BAND_GOLD,
                           (round(px - r * 0.3), round(py + head_w * 0.13 + r * 0.7)),
                           max(1, round(r * 0.35)))
