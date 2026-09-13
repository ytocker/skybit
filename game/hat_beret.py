import pygame


# Wool palette: deep red felt with a darker rim where the band cinches the head.
# Layered tones (not a gradient) keep the read crisp at head_w~18 where blends muddy.
_FELT_HI = (196, 44, 52)
_FELT = (164, 30, 40)
_FELT_LO = (118, 20, 30)
_BAND = (96, 16, 26)
_BAND_LO = (74, 12, 20)
_STALK = (132, 24, 34)


def _lerp(a, b, t):
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile BERET sized for a head of width head_w, centered at cx, band line at base_y."""
    # All geometry scales off head_w so the silhouette survives big and small.
    r = head_w * 0.5
    f = 1 if facing >= 0 else -1

    # The disc overhangs the head and droops to the trailing side; the slouch is
    # the read, so its centre is pushed off-axis and the radius beats the head.
    disc_rx = r * 1.34
    disc_ry = r * 0.60
    disc_cx = cx + f * r * 0.32
    disc_cy = base_y - r * 0.16

    # Band hugs the head just under the disc — a shallow cinched arc, not a brim.
    band_h = max(2, int(r * 0.30))
    band_cy = base_y + r * 0.06

    pts = max(20, int(head_w * 0.9))

    import math

    def full_ellipse(ecx, ecy, erx, ery, squash_lo=1.0):
        # squash_lo flattens the lower half so the disc underside curves to seat
        # snugly on the round head rather than ballooning below the band.
        out = []
        n = pts * 2
        for i in range(n + 1):
            a = math.tau * (i / n)
            y = math.sin(a)
            yy = y * (squash_lo if y > 0 else 1.0)
            out.append((ecx + erx * math.cos(a), ecy + ery * yy))
        return out

    # --- Band: a soft cinched ring sitting on the crown line. ---
    band_rx = r * 0.96
    band_top = full_ellipse(cx, band_cy, band_rx, band_h * 0.9, squash_lo=1.15)
    pygame.draw.polygon(surf, _BAND, band_top)
    # Lower lip of the band, a touch darker, for fabric depth.
    lip = full_ellipse(cx, band_cy + band_h * 0.35, band_rx * 0.98, band_h * 0.7,
                       squash_lo=1.1)
    pygame.draw.polygon(surf, _BAND_LO, lip)

    # --- Disc body: the overhanging slouchy crown. ---
    disc = full_ellipse(disc_cx, disc_cy, disc_rx, disc_ry, squash_lo=1.25)
    pygame.draw.polygon(surf, _FELT, disc)

    # Trailing droop: a second smaller blob dragging down toward the facing side
    # so the brim reads as soft cloth slumping, not a rigid plate.
    droop_cx = disc_cx + f * disc_rx * 0.55
    droop_cy = disc_cy + disc_ry * 0.55
    droop = full_ellipse(droop_cx, droop_cy, disc_rx * 0.42, disc_ry * 0.78,
                        squash_lo=1.2)
    pygame.draw.polygon(surf, _FELT, droop)

    # --- Soft top-lit shading: a highlight cap and a shadowed underside. ---
    hi = full_ellipse(disc_cx - f * disc_rx * 0.22, disc_cy - disc_ry * 0.34,
                     disc_rx * 0.62, disc_ry * 0.5, squash_lo=0.7)
    pygame.draw.polygon(surf, _FELT_HI, hi)

    # A darker underside crescent reads as the shadowed lower lip of the felt.
    under = []
    n = pts * 2
    for i in range(n + 1):
        a = math.pi * (i / n)  # lower half only
        under.append((disc_cx + disc_rx * 0.95 * math.cos(a),
                     disc_cy + disc_ry * 0.9 * math.sin(a)))
    pygame.draw.polygon(surf, _FELT_LO, under)

    # Re-assert the highlight so the underside crescent can't bleed over it.
    pygame.draw.polygon(surf, _FELT_HI, hi)

    # --- Stalk / nub on the very top centre — the signature beret cue. ---
    nub_r = max(2, int(r * 0.13))
    nub_cx = disc_cx - f * disc_rx * 0.05
    nub_cy = disc_cy - disc_ry * 0.92
    pygame.draw.circle(surf, _STALK, (int(nub_cx), int(nub_cy)), nub_r)
    pygame.draw.circle(surf, _FELT_HI, (int(nub_cx - nub_r * 0.3),
                                       int(nub_cy - nub_r * 0.3)),
                      max(1, int(nub_r * 0.45)))

    # 1px soft edge along the disc top arc (no full outline — caller owns that).
    top_arc = []
    for i in range(pts + 1):
        a = math.pi + math.pi * (i / pts)  # upper half
        top_arc.append((disc_cx + disc_rx * math.cos(a),
                       disc_cy + disc_ry * math.sin(a)))
    if len(top_arc) > 1:
        pygame.draw.lines(surf, _lerp(_FELT_HI, (255, 255, 255), 0.25),
                         False, top_arc, 1)
