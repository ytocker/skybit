import pygame


# Beachy thong sandal: cream foam sole, white midsole edge, bright teal strap.
# Kept deliberately flat + minimal so the silhouette reads as a flip-flop (not a
# sneaker) even at bird-foot size; the hero cue is a WIDE, LOW Y-thong lying on
# the footbed — never a tall vertical strap (that reads as a sign/easel).
_SOLE_TOP = (224, 200, 156)      # warm cream/tan footbed
_SOLE_TOP_DK = (196, 170, 124)   # subtle 1px lip under the footbed
_SOLE_EDGE = (244, 240, 232)     # white midsole stripe
_SOLE_EDGE_DK = (210, 204, 192)  # shadow line at the very bottom
_STRAP = (38, 196, 190)          # bright teal thong
_STRAP_DK = (24, 150, 146)       # strap shading / underside / anchor


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile FLIP-FLOP sandal into box (x,y,w,h)."""

    def px(fx, fy):
        # Proportional point; mirror horizontally about the box centre when
        # facing left so the toe always points the requested way.
        nx = fx if facing >= 0 else (1.0 - fx)
        return (x + nx * w, y + fy * h)

    # Slim two-layer sole filling the full footprint WIDTH (matches its
    # row-mates) and seated on the same ground line. Kept thin so it stays a
    # flat slab and never out-masses the Y-thong hero cue. Slight curl at the
    # toe + heel so it isn't a plain block.
    foot_top = 0.74          # top of the cream footbed (slim slab, bottom band)
    foot_bot = 0.90          # footbed / white-edge boundary
    edge_bot = 1.0           # ground
    heel_x = 0.04
    toe_x = 0.97

    footbed = [
        px(heel_x, foot_top + 0.03),   # heel: tiny curl up
        px(0.22, foot_top - 0.03),
        px(0.74, foot_top - 0.03),
        px(toe_x, foot_top + 0.04),    # toe: tiny curl up
        px(toe_x, foot_bot),
        px(heel_x, foot_bot),
    ]
    pygame.draw.polygon(surf, _SOLE_TOP, footbed)
    # 1px darker lip along the footbed/edge seam for separation.
    pygame.draw.line(surf, _SOLE_TOP_DK, px(heel_x, foot_bot), px(toe_x, foot_bot),
                     max(1, int(h * 0.03)))

    white_edge = [
        px(heel_x, foot_bot),
        px(toe_x, foot_bot),
        px(toe_x - 0.01, edge_bot),
        px(heel_x + 0.01, edge_bot),
    ]
    pygame.draw.polygon(surf, _SOLE_EDGE, white_edge)
    pygame.draw.line(surf, _SOLE_EDGE_DK, px(heel_x + 0.01, edge_bot - 0.005),
                     px(toe_x - 0.01, edge_bot - 0.005), max(1, int(h * 0.03)))

    # Y-THONG STRAP — the signature cue, laid DOWN on the footbed as a wide, low
    # Y. The toe-post sits near the front of the sole; the two side straps fan
    # out SHALLOWLY to the left and right edges of the footbed, peaking only a
    # little above the surface so it hugs the bed instead of standing up.
    sw = max(1, int(h * 0.07))     # strap thickness scales with size

    bed_y = foot_top - 0.02        # the strap rides just above the footbed top
    apex = px(0.78, foot_top - 0.22)   # low apex: ~22% above the sole, near toe
    front_root = px(0.93, bed_y)       # anchored at the front/toe edge
    back_root = px(0.16, bed_y)        # anchored back toward the heel edge

    # Wide fanning V (the arms of the Y) reaching the sole's outer edges.
    pygame.draw.line(surf, _STRAP, apex, front_root, sw)
    pygame.draw.line(surf, _STRAP, apex, back_root, sw)

    # Thong line carried back ALONG the footbed top — a faint strap that hugs
    # the bed from the toe-post toward the arch. This low cue survives at 16px
    # even when the raised V blurs into the sole.
    toe_post = px(0.80, bed_y)
    pygame.draw.line(surf, _STRAP_DK, toe_post, px(0.42, bed_y), max(1, sw - 1))

    # Rounded caps so thin straps don't fray at any scale, plus the apex knob.
    for pt in (front_root, back_root, apex):
        pygame.draw.circle(surf, _STRAP, (int(pt[0]), int(pt[1])), max(1, sw // 2 + 1))
    pygame.draw.circle(surf, _STRAP_DK, (int(apex[0]), int(apex[1])),
                       max(1, sw // 2))

    # TOE-THONG ANCHOR: a clear dot/post where the thong plugs into the sole
    # between the toes. Sits low on the footbed and is the most durable cue at
    # tiny sizes, so it gets its own bold dot.
    ax, ay = int(toe_post[0]), int(toe_post[1])
    pygame.draw.circle(surf, _STRAP_DK, (ax, ay), max(2, sw // 2 + 1))
    pygame.draw.circle(surf, _STRAP, (ax, ay), max(1, sw // 2))
