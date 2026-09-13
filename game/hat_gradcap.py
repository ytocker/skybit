"""Procedural side-profile GRAD CAP (mortarboard) for Skybit's coin Store.

One public entry: `draw_hat(surf, cx, base_y, head_w, facing=1)`.

The cap reads as three stacked cues so it never collapses into a bare plank:
a rounded black SKULL-CAP dome that visibly seats on the head, a square flat
BOARD resting on that dome — drawn as a tilted plate whose lit TOP face reads
distinctly from its shadowed UNDER edge so it looks like a 3D square plane, a
BUTTON pinned at the board's centre, and a gold TASSEL draped over the front
edge into a fringed bob. All geometry derives from (cx, base_y, head_w) so the
same code scales from a hero head (head_w~80) to a tiny product pip (head_w~18).
Below ~22px the button + tassel-fringe micro detail is gated off, leaving the
dome + board (top/under contrast) + a single tassel line.

No image files, no real brand marks — classic black board + bright tassel only.
"""
import pygame

# ── palette ──────────────────────────────────────────────────────────────────
# The board's TOP face is clearly lighter than its UNDER edge so the slab reads
# as a tilted plate catching light, not a flat hole. The skull-cap dome is a
# warmer near-black with its own catch-light so it separates from the board and
# reads as a rounded base. The tassel is bright gold so the academic cue locks
# the eye even at icon size.
BOARD_TOP = ( 60,  58,  82)   # lit top face of the slab (square plane)
BOARD     = ( 30,  28,  44)   # board body / front fascia
BOARD_DK  = ( 12,  10,  20)   # under edge in shadow
CAP       = ( 26,  24,  40)   # skull-cap dome fabric
CAP_DK    = ( 14,  12,  24)   # cap underside / shadow
CAP_HI    = ( 60,  58,  82)   # cap top catch-light
TASSEL    = (255, 196,  44)   # gold cord + fringe
TASSEL_HI = (255, 226, 120)   # cord highlight
TASSEL_DK = (206, 150,  20)   # fringe shadow
BUTTON    = (255, 210,  70)   # gold centre button


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile grad cap sized for a round head of diameter head_w.

    cx        head centre x.
    base_y    cap line — the dome seats on a head whose crown-top is here.
    head_w    head diameter; all proportions derive from it.
    facing    +1 = looking right, tassel drapes to the right/front;
              -1 mirrors the whole hat.
    """
    f = 1 if facing >= 0 else -1
    hw = head_w / 2.0
    detailed = head_w >= 22

    # ── SKULL-CAP DOME ───────────────────────────────────────────────────────
    # A rounded black dome that hugs the crown and rises a real, visible amount
    # above base_y, so the board has something domed to rest on instead of
    # floating as a slab. Drawn as a filled half-ellipse (a stack of horizontal
    # spans) so the silhouette is a clean curved cap, not a brick.
    dome_hw  = hw * 0.94                 # half-width of the dome (hugs the head)
    dome_h   = head_w * 0.42             # how tall the dome stands above base_y
    dome_cy  = base_y                    # ellipse centre row = the cap line
    rows = max(4, round(dome_h))
    for i in range(rows + 1):
        t = i / rows
        y = base_y - dome_h * t          # walk up from the cap line to the crown
        # Ellipse half-width at this height: full at the base, tapering to 0.
        span = dome_hw * (1.0 - t * t) ** 0.5
        if span < 0.5:
            continue
        # Shade the dome: lighter near the (lit) top-back, darker toward the base.
        col = _lerp(CAP, CAP_HI, max(0.0, (t - 0.45) * 1.8)) if t > 0.45 \
            else _lerp(CAP_DK, CAP, t / 0.45)
        pygame.draw.line(surf, col, (cx - span, y), (cx + span, y),
                         max(1, round(head_w * 0.045)))
    # Shadow wedge on the front of the dome under the board's overhang.
    pygame.draw.polygon(surf, CAP_DK, [
        (cx, base_y - dome_h * 0.45),
        (cx + f * dome_hw, base_y - dome_h * 0.05),
        (cx + f * dome_hw, base_y + head_w * 0.02),
        (cx, base_y + head_w * 0.02),
    ])
    if detailed:
        # Crown catch-light arc so the dome reads as a rounded surface.
        pygame.draw.arc(surf, CAP_HI,
                        pygame.Rect(round(cx - dome_hw * 0.7),
                                    round(base_y - dome_h),
                                    round(dome_hw * 1.4), round(dome_h * 1.2)),
                        0.5, 2.4, max(1, round(head_w * 0.03)))

    # ── BOARD (mortarboard slab) ─────────────────────────────────────────────
    # The square board seen side-on: a long slab tilted so its FRONT corner dips
    # below the back. It overhangs the dome on both sides and sits ON TOP of the
    # dome's crown. Thickened ~30% over the old slab for a readable edge, and
    # split into a LIT top face above a DARK under edge so it reads as a tilted
    # square plane rather than a featureless plank.
    over   = hw * 1.34                 # half-span of the slab (overhang)
    tilt   = head_w * 0.085            # gentle vertical drop of the front corner
    thick  = max(3.0, head_w * 0.135)  # slab thickness (readable edge)
    cy     = base_y - dome_h * 0.96    # board sits just below the dome crown

    back_x  = cx - f * over
    front_x = cx + f * over
    # Top-face corners: back rides higher, front dips with the tilt; centre is
    # lifted a hair so the square plane shows a soft crease toward the viewer.
    tb = (back_x,  cy - tilt * 0.5)    # top-back corner
    tf = (front_x, cy + tilt * 0.5)    # top-front corner (dips, nearest viewer)
    tm = (cx,      cy - head_w * 0.02) # top-centre crease

    # Under-edge corners (top face + thickness, following the same tilt).
    bb = (tb[0], tb[1] + thick)
    bf = (tf[0], tf[1] + thick)
    bm = (tm[0], tm[1] + thick)

    # 1) The shadowed UNDER edge / fascia first.
    pygame.draw.polygon(surf, BOARD_DK, [tb, tm, tf, bf, bm, bb])
    # 2) The board body (front fascia) over the lower part, a mid value.
    pygame.draw.polygon(surf, BOARD, [
        (tb[0], tb[1] + thick * 0.40),
        (tm[0], tm[1] + thick * 0.40),
        (tf[0], tf[1] + thick * 0.40),
        bf, bm, bb,
    ])
    # 3) The LIT top face on top — the tilted square plane the eye should catch.
    #    Kept as the dominant band so the slab reads as a flat square, lit.
    pygame.draw.polygon(surf, BOARD_TOP, [tb, tm, tf,
                                          (tf[0], tf[1] + thick * 0.48),
                                          (tm[0], tm[1] + thick * 0.48),
                                          (tb[0], tb[1] + thick * 0.48)])
    # Crisp ridge line along the top so the square corner survives small sizes.
    pygame.draw.line(surf, CAP_HI, tb, tf, max(1, round(head_w * 0.022)))

    # ── BUTTON ───────────────────────────────────────────────────────────────
    # Gold disc pinned at the board's centre-top, where the tassel cord anchors.
    btn_x = cx + f * head_w * 0.02
    btn_y = tm[1] - head_w * 0.01
    if detailed:
        br = max(2, round(head_w * 0.05))
        pygame.draw.circle(surf, BUTTON, (round(btn_x), round(btn_y)), br)
        pygame.draw.circle(surf, TASSEL_HI, (round(btn_x - f), round(btn_y - 1)),
                           max(1, br - 2))
    else:
        # Tiny: a single bright pixel so the centre still glints.
        pygame.draw.circle(surf, BUTTON, (round(btn_x), round(btn_y)),
                           max(1, round(head_w * 0.07)))

    # ── TASSEL ───────────────────────────────────────────────────────────────
    # A cord runs from the button toward the front corner, then drops over the
    # front edge into a fringed bob. The cord sags slightly for cloth feel.
    edge_x = tf[0] - f * head_w * 0.10            # where the cord crosses the rim
    edge_y = tf[1] + head_w * 0.02
    drop   = head_w * (0.34 if detailed else 0.30)
    bob_x  = edge_x + f * head_w * 0.02
    bob_y  = edge_y + drop
    cord_w = max(1, round(head_w * 0.035))

    # Cord: button -> sag point -> over the edge.
    sag = (cx + f * over * 0.55, tm[1] + head_w * 0.04)
    pygame.draw.lines(surf, TASSEL, False,
                      [(btn_x, btn_y), sag, (edge_x, edge_y)], cord_w)
    # Hanging cord down to the bob.
    pygame.draw.line(surf, TASSEL, (edge_x, edge_y), (bob_x, bob_y - drop * 0.32),
                     cord_w)
    if detailed:
        pygame.draw.line(surf, TASSEL_HI, (btn_x, btn_y), sag,
                         max(1, cord_w - 1))

    # Fringed bob at the end.
    fr_w = head_w * 0.10
    fr_top = bob_y - drop * 0.32
    if detailed:
        # A small cap knot then several fringe strands fanning down.
        pygame.draw.circle(surf, TASSEL, (round(bob_x), round(fr_top)),
                           max(1, round(head_w * 0.03)))
        n = 4
        for i in range(n):
            t = i / (n - 1)
            sx = bob_x - fr_w * 0.5 + fr_w * t
            ex = sx + f * head_w * 0.01
            ey = bob_y + (drop * 0.10 if i in (0, n - 1) else drop * 0.18)
            col = TASSEL if i % 2 == 0 else TASSEL_DK
            pygame.draw.line(surf, col, (sx, fr_top), (ex, ey),
                             max(1, round(head_w * 0.02)))
    else:
        # Tiny: a single short fringe bob so the tassel still terminates.
        pygame.draw.line(surf, TASSEL, (bob_x, fr_top),
                         (bob_x, bob_y), max(1, round(head_w * 0.06)))
