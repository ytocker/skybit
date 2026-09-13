"""Procedural side-profile BUCKET HAT for Skybit's coin Store.

Hero cue: the classic round brim that dips DOWN to BOTH sides, under a
soft flat-ish topstitched crown. Friendly khaki/tan cotton colourway
with a slightly darker brim underside, parallel topstitching rows and a
small side eyelet vent. All proportional to head_w so it reads at
head_w=80 (hero) down to head_w=18 (tiny product chip); stitching detail
is gated off below ~22px so the round-brim silhouette survives small.
"""
import pygame

# ── khaki / tan cotton colourway ────────────────────────────────────────────
# A friendly warm tan body, a darker brim underside for visible thickness,
# and a soft highlight band so the cotton reads as fabric, not plastic.
TAN_HI    = (214, 192, 148)   # sun-lit crown sheen
TAN       = (192, 168, 120)   # main cotton body
TAN_MID   = (170, 145,  98)   # brim top / lower crown
TAN_DK    = (138, 114,  74)   # brim underside (darker, shaded)
TAN_DK2   = (112,  90,  56)   # deepest underside edge / eyelet ring
STITCH    = (228, 214, 180)   # topstitching thread (lighter than body)
EYELET_HOLE = (96, 78, 52)    # vent hole interior


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile BUCKET HAT sized for a head of width head_w,
    centered at cx, brim line at base_y."""
    f = 1 if facing >= 0 else -1

    # Proportions derived only from head_w so big/small stay identical in feel.
    half      = head_w * 0.5
    # Brim spans clearly wider than the head on both sides.
    brim_half = half * 1.42
    brim_dip  = max(2.0, head_w * 0.20)   # how far the brim tips dip below base_y
    brim_th   = max(2.0, head_w * 0.13)   # brim slab thickness
    # Soft, low, flat-ish crown — short so it reads bucket hat, not beanie.
    crown_h   = head_w * 0.40
    crown_half = half * 0.96
    detail    = head_w >= 22              # gate fine stitching/eyelet for tiny

    crown_top = base_y - crown_h

    # ── soft flat-ish crown ──────────────────────────────────────────────────
    # A wide rounded-rect dome: tall enough to sit above base_y, but with a
    # broad flat top and gently rounded shoulders — the bucket silhouette.
    # The bottom extends below base_y and is later capped by the brim so the
    # underside reads as curving onto a round head (head itself not drawn).
    cw = crown_half * 2
    crown_rect = pygame.Rect(int(cx - crown_half), int(crown_top), int(cw),
                             int(crown_h + brim_th))
    rad = max(2, int(head_w * 0.18))
    pygame.draw.rect(surf, TAN_MID, crown_rect, border_radius=rad)
    # Main lit body inset a hair so the mid-tone shows as a thin shaded edge.
    body = crown_rect.inflate(-max(2, head_w * 0.06), 0)
    body.height = int(crown_h * 0.95)
    body.top = int(crown_top)
    pygame.draw.rect(surf, TAN, body, border_radius=rad)
    # Sun-lit sheen across the broad flat top, biased to the facing side.
    top_hi = pygame.Rect(0, 0, int(cw * 0.62), int(crown_h * 0.5))
    top_hi.center = (int(cx + f * crown_half * 0.18), int(crown_top + crown_h * 0.32))
    pygame.draw.ellipse(surf, TAN_HI, top_hi)

    # ── round brim: a solid slab that dips DOWN to both sides ────────────────
    # Two stacked droop-curves (top edge + lower edge) define a slab with real
    # thickness. The tips sit BELOW base_y; the centre tucks up under the
    # crown — the signature bucket droop, symmetric on both sides.
    lx = cx - brim_half
    rx = cx + brim_half
    tip_y   = base_y + brim_dip               # outer tips, lowest point
    inner_y = base_y - brim_th * 0.45         # where brim meets crown, highest
    # Underside slab (darker) — full body of the brim.
    under = [
        (lx, tip_y),
        (cx - crown_half * 0.5, inner_y + brim_th),
        (cx + crown_half * 0.5, inner_y + brim_th),
        (rx, tip_y),
        (rx, tip_y + brim_th),
        (cx, base_y + brim_th * 0.7),
        (lx, tip_y + brim_th),
    ]
    pygame.draw.polygon(surf, TAN_DK2, under)
    # Brim top surface (the lit curve a viewer sees from the front).
    top = [
        (lx, tip_y),
        (cx - crown_half * 0.5, inner_y),
        (cx + crown_half * 0.5, inner_y),
        (rx, tip_y),
        (rx, tip_y + brim_th * 0.55),
        (cx, base_y + brim_th * 0.25),
        (lx, tip_y + brim_th * 0.55),
    ]
    pygame.draw.polygon(surf, TAN_DK, top)          # mid layer = slab body
    # Lit upper face of the brim, inset so the TAN_DK rim shows below it.
    top_face = [
        (lx + brim_half * 0.04, tip_y),
        (cx - crown_half * 0.5, inner_y),
        (cx + crown_half * 0.5, inner_y),
        (rx - brim_half * 0.04, tip_y),
        (cx, base_y - brim_th * 0.05),
    ]
    pygame.draw.polygon(surf, TAN_MID, top_face)
    # A brighter sweep along the very top of the brim sells the cotton sheen.
    pygame.draw.lines(
        surf, TAN, False,
        [(lx + brim_half * 0.14, tip_y - brim_th * 0.05),
         (cx, inner_y + brim_th * 0.25),
         (rx - brim_half * 0.14, tip_y - brim_th * 0.05)],
        max(1, int(head_w * 0.03)),
    )

    if detail:
        # ── topstitching: rows parallel to the brim edge ─────────────────────
        sw = max(1, int(head_w * 0.026))
        # Two stitch rows following the brim's droop, inset from the edge so
        # they run parallel to the slab's top curve.
        for k in (0.32, 0.62):
            iy = inner_y + brim_th * k
            ty = tip_y + brim_th * (0.45 + k * 0.4)
            pygame.draw.lines(
                surf, STITCH, False,
                [(lx + brim_half * 0.16, ty),
                 (cx, iy),
                 (rx - brim_half * 0.16, ty)],
                sw,
            )
        # One stitch row hugging the crown base (where crown meets brim).
        cs_y = base_y - crown_h * 0.30
        pygame.draw.lines(
            surf, STITCH, False,
            [(cx - crown_half * 0.78, cs_y + crown_h * 0.10),
             (cx, cs_y),
             (cx + crown_half * 0.78, cs_y + crown_h * 0.10)],
            sw,
        )

        # ── side eyelet vent on the crown (toward the facing side) ───────────
        ev_x = cx + f * crown_half * 0.44
        ev_y = base_y - crown_h * 0.50
        er = max(1.5, head_w * 0.05)
        pygame.draw.circle(surf, TAN_DK, (int(ev_x), int(ev_y)), int(er))
        pygame.draw.circle(surf, EYELET_HOLE, (int(ev_x), int(ev_y)),
                           max(1, int(er * 0.5)))
