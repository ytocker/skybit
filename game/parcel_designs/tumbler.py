"""TUMBLER — insulated reusable hydro-flask parcel cosmetic.

A trendy reusable bottle carried upright below Pip. The IDENTITY is the OPAQUE
chunky read: a wide, straight-walled MATTE pastel-teal body (no see-through
water at all), a fat BLACK flip-straw LID capping it, and a small carry LOOP
arching off the top. Those three masses — opaque body / black lid / loop — carry
the read; the body is solid colour, so the contrast is silhouette + the black
cap, not a meniscus.

22px read tradeoffs (WHY): the body is wide and squat so the chunky insulated
mass reads even before colour, and the body fill is FLAT matte (one soft
vertical shade, no glint streak, no water line) because any internal detail
would just re-read as a see-through water cue, which an opaque tumbler must
avoid. The lid is exaggeratedly tall and BLACK — the grayscale-safe anchor —
sitting as a clearly separate dark cap so body and lid never fuse at the
downscale; a 2px lighter spout NUB at one corner breaks the lid silhouette so
it reads as a flip-straw cap, not a void, and the asymmetry helps track the
bank. The carry loop is a thin TEAL handle (a colored bump over the black lid:
teal-on-black survives the downscale far better than grey-on-dark) lifted on
2px posts so a clear hole of BACKGROUND shows under the arc — a real handle, not
a frame. A double-wall SEAM band across the lower third is the insulated cue;
it sits low and is teal-shade (never a bright meniscus) so it never re-reads as
a water line. Drawn on a 44px work surface then smoothscaled to 22 so the loop
arc and lid edges antialias cleanly. A baked dark outline (inflated, drawn
first) carries the shape on bright DAY sky; a cool keyline rim inside — tracing
the TOP edge of the lid so the cap stays a distinct mass — is the NIGHT
lifeline; the whole tumbler is held off the surface edges so the gameplay
rotozoom never clips the loop or base.
"""
import math

import pygame

# Tight palette: opaque pastel-teal body with a darker shade for the rounded
# base, a near-black lid (the grayscale-safe anchor + the strongest identity
# cue), and the day/night line colours. The carry loop is the body teal so it
# reads as a coloured handle bump over the black cap.
TEAL = ( 92, 201, 192)        # matte pastel-teal body (flat, opaque)
TEAL_SHADE = ( 46, 154, 146)  # darker teal — base + lower-body shading + seam
TEAL_HI = (188, 240, 234)     # bright upper highlight (survives the downscale)
LID = ( 42,  46,  54)         # black flip-straw lid — the eye-magnet / GS anchor
LID_HI = (140, 148, 160)      # spout nub + lid top edge so the cap reads raised
LOOP = ( 92, 201, 192)        # carry loop — body teal (teal-on-black handle bump)
OUTLINE = ( 21,  48,  46)     # dark, high-value: reads on bright day sky
KEYLINE = (190, 232, 226)     # cool rim — the NIGHT lifeline


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    # Mode-agnostic: one static tumbler sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Tumbler geometry. WIDE straight side walls + squat proportions so the
    # chunky insulated mass reads before colour even resolves. Held off the
    # surface edges so the gameplay rotozoom never clips loop/base.
    BW = 22                       # body width (chunky, squat insulated mass)
    body_top = 15                 # top of the body wall (just under the lid)
    body_bot = 39                 # rounded base
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 5                  # base corners round; top stays square under the lid

    # Lid: a fat black flip-straw cap, slightly NARROWER than the body so a
    # shoulder step reads. Tall so it stays a clear separate mass when banked.
    LW, LH = 16, 10
    lid_rect = pygame.Rect(cx - LW // 2, body_top - LH + 1, LW, LH)

    # Carry loop: a thin teal handle arching off the lid top, biased LEFT so it
    # clears the right-corner spout. Lifted on short posts so a hole of
    # BACKGROUND shows under the arc — a real grab handle, not a square frame.
    loop_cx = cx - 3              # biased left so the arc clears the spout nub
    loop_r = 5                    # outer radius of the loop arc
    loop_cy = lid_rect.y - 4      # arc centre above the lid (opens a real gap)
    post_top = loop_cy + 1        # where the posts meet the arc ends
    post_bot = lid_rect.y + 1     # posts land on the lid top (~3px tall)

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    # Loop arc outline (a fat dark arc); the daylight gap to the lid stays open.
    pygame.draw.arc(surf, OUTLINE,
                    pygame.Rect(loop_cx - loop_r - 2, loop_cy - loop_r - 2,
                                (loop_r + 2) * 2, (loop_r + 2) * 2),
                    math.radians(0), math.radians(180), 5)
    # Outline backing for the two short posts so the teal reads on bright day sky.
    pygame.draw.line(surf, OUTLINE, (loop_cx - loop_r, post_top),
                     (loop_cx - loop_r, post_bot), 3)
    pygame.draw.line(surf, OUTLINE, (loop_cx + loop_r, post_top),
                     (loop_cx + loop_r, post_bot), 3)
    pygame.draw.rect(surf, OUTLINE, lid_rect.inflate(4, 4), border_radius=3)
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4),
                     border_radius=body_rad + 2,
                     border_top_left_radius=2, border_top_right_radius=2)

    # --- LID: fat black cap drawn BEFORE the loop so the teal handle sits on top
    # of it. A 2px lighter spout NUB at one corner breaks the silhouette (the
    # flip-straw tell + bank-tracking asymmetry); a top edge keeps it raised.
    spout_w, spout_h = 5, 3
    spout = pygame.Rect(lid_rect.right - spout_w - 1, lid_rect.y - spout_h + 1,
                        spout_w, spout_h + 2)
    pygame.draw.rect(surf, OUTLINE, spout.inflate(2, 2), border_radius=2)
    pygame.draw.rect(surf, LID, lid_rect, border_radius=3)
    pygame.draw.rect(surf, LID, spout, border_top_left_radius=2,
                     border_top_right_radius=2)
    # Spout nub highlight — the lighter cue that makes it read as a straw/spout.
    pygame.draw.line(surf, LID_HI, (spout.x + 1, spout.y + 1),
                     (spout.right - 1, spout.y + 1), 2)
    # Lid top edge so the broad cap reads raised, not a flat dark hole.
    pygame.draw.line(surf, LID_HI,
                     (lid_rect.x + 2, lid_rect.y + 1),
                     (lid_rect.right - spout_w - 2, lid_rect.y + 1), 1)
    # Thick lid/body groove so the lid clearly seats onto the body (2px on NIGHT).
    pygame.draw.line(surf, OUTLINE,
                     (lid_rect.x, lid_rect.bottom),
                     (lid_rect.right - 1, lid_rect.bottom), 2)

    # --- Carry LOOP: thin TEAL handle arc over the black lid, lifted on 2px
    # posts so a hole of background shows under it. Teal-on-black reads as a
    # coloured grab handle at 22px where grey-on-dark just muddied into the cap.
    pygame.draw.arc(surf, LOOP,
                    pygame.Rect(loop_cx - loop_r, loop_cy - loop_r,
                                loop_r * 2, loop_r * 2),
                    math.radians(2), math.radians(178), 3)
    pygame.draw.line(surf, LOOP, (loop_cx - loop_r, post_top),
                     (loop_cx - loop_r, post_bot), 2)
    pygame.draw.line(surf, LOOP, (loop_cx + loop_r, post_top),
                     (loop_cx + loop_r, post_bot), 2)

    # --- BODY: opaque matte teal on its own alpha surface so the straight-walled
    # base-rounded shape composites cleanly, then blitted in one piece. A gentle
    # top->bottom shade gives volume WITHOUT any water-line / glint that would
    # re-read as a see-through bottle.
    body = pygame.Surface((body_rect.w, body_rect.h), pygame.SRCALPHA)
    for y in range(body_rect.h):
        t = y / max(1, body_rect.h - 1)
        # Highlight near the top, settling into the base shade at the bottom.
        if t < 0.5:
            tt = t / 0.5
            c = (
                int(TEAL_HI[0] + (TEAL[0] - TEAL_HI[0]) * tt),
                int(TEAL_HI[1] + (TEAL[1] - TEAL_HI[1]) * tt),
                int(TEAL_HI[2] + (TEAL[2] - TEAL_HI[2]) * tt),
            )
        else:
            tt = (t - 0.5) / 0.5
            c = (
                int(TEAL[0] + (TEAL_SHADE[0] - TEAL[0]) * tt),
                int(TEAL[1] + (TEAL_SHADE[1] - TEAL[1]) * tt),
                int(TEAL[2] + (TEAL_SHADE[2] - TEAL[2]) * tt),
            )
        body.fill(c + (255,), pygame.Rect(0, y, body_rect.w, 1))
    # Mask to a chunky shape: base corners round, top stays square (lid sits on it).
    mask = pygame.Surface((body_rect.w, body_rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=body_rad, border_top_left_radius=1,
                     border_top_right_radius=1)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- A soft vertical edge-shade down the right side (~3px) so the cylinder
    # reads as round, not a flat tile (kept dark/teal, never a bright glint).
    pygame.draw.line(surf, TEAL_SHADE,
                     (body_rect.right - 3, body_rect.y + 3),
                     (body_rect.right - 3, body_rect.bottom - 4), 3)

    # --- Double-wall SEAM band across the lower third: the insulated-tumbler cue.
    # Teal-shade (never bright) and placed LOW so it never reads as a water line.
    seam_y = body_rect.y + int(body_rect.h * 0.66)
    pygame.draw.line(surf, TEAL_SHADE,
                     (body_rect.x + 2, seam_y),
                     (body_rect.right - 3, seam_y), 2)

    # --- Cool keyline rim INSIDE the outline — the NIGHT lifeline that glows on
    # dark sky while staying subtle on day. Traces the body wall, and the TOP
    # edge of the lid so the cap stays a distinct mass against the dark sky.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad,
                     border_top_left_radius=1, border_top_right_radius=1)
    pygame.draw.line(surf, KEYLINE, (lid_rect.x + 1, lid_rect.y + 1),
                     (lid_rect.right - 2, lid_rect.y + 1), 1)
    pygame.draw.line(surf, KEYLINE, (lid_rect.x, lid_rect.y + 1),
                     (lid_rect.x, lid_rect.bottom - 1), 1)
    pygame.draw.line(surf, KEYLINE, (lid_rect.right - 1, lid_rect.y + 1),
                     (lid_rect.right - 1, lid_rect.bottom - 1), 1)

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (22, 22))
