"""Procedural side-profile FEDORA for Skybit's coin Store.

One public entry: `draw_hat(surf, cx, base_y, head_w, facing=1)`.

The fedora reads through its silhouette (snap brim that dips at the front
and lifts at the back) plus two hero cues: a pinched/creased teardrop
crown and a contrasting grosgrain band with a small flat side-bow. All
geometry is derived from (cx, base_y, head_w) so the same code scales from
a hero head (head_w~80) down to a tiny product pip (head_w~18). Below
~22px the crease/band micro-detail is gated off so the small icon keeps a
clean brim+crown silhouette instead of muddy noise.

No image files, no real brand marks — felt tones + grosgrain band only.
"""
import pygame

# ── felt palette (warm brown) ────────────────────────────────────────────────
# Felt is matte, so the tonal spread is gentle — a bright top-left catch,
# a mid body, and a darker right/under face. The band is a near-black
# grosgrain that contrasts cleanly against the brown without going pure
# black (reads as ribbon, not a hole).
FELT_HI   = (158, 110,  62)
FELT      = (124,  80,  44)
FELT_MID  = (102,  64,  34)
FELT_DK   = ( 74,  44,  22)
BAND      = ( 46,  30,  20)
BAND_HI   = ( 78,  54,  36)
UNDER     = ( 52,  30,  16)   # brim underside — darkest, in shadow


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile fedora sized for a round head of diameter head_w.

    cx        head centre x.
    base_y    brim line — the hat seats on a head whose crown-top is here.
    head_w    head diameter; all proportions derive from it.
    facing    +1 = looking right (brim dips lower at the right/front);
              -1 mirrors the whole hat.
    """
    f = 1 if facing >= 0 else -1
    hw = head_w / 2.0

    # Brim reaches past the head on both sides; the front (facing) side
    # extends further and snaps down for the classic shading-the-eyes look.
    brim_back  = hw * 1.30        # rear overhang
    brim_front = hw * 1.50        # front overhang (longer snap)
    # Crown narrower than the head so the brim band tucks in below it.
    crown_hw   = hw * 0.80
    crown_h    = head_w * 0.66    # crown height above base_y

    detailed = head_w >= 22

    # X helpers in screen space (f flips front/back).
    front_x = cx + f * brim_front
    back_x  = cx - f * brim_back
    crown_front = cx + f * crown_hw
    crown_back  = cx - f * crown_hw

    seat_y = base_y + head_w * 0.04     # where brim meets crown base

    # ── BRIM ─────────────────────────────────────────────────────────────────
    # A snap brim seen from the side is a long shallow curve: it lifts above
    # base_y at the BACK, sweeps down through the head, and droops well below
    # base_y at the FRONT tip. Thickness tapers to a point at each tip so the
    # felt edge reads as a sheet, not a slab.
    front_dip = head_w * 0.18
    back_lift = head_w * 0.08
    thick     = max(2.0, head_w * 0.10)   # brim thickness through the middle

    # Top edge, back -> front (screen-space x already carries facing).
    top_back  = (back_x,                       base_y - back_lift)
    top_q1    = (cx - f * hw * 0.55,           base_y - head_w * 0.02)
    top_mid   = (cx,                           seat_y + head_w * 0.02)
    top_q3    = (cx + f * hw * 0.70,           base_y + head_w * 0.07)
    top_front = (front_x,                      base_y + front_dip)

    # Bottom edge mirrors the top with a thickness offset, tips pinched in.
    bot_front = (front_x - f * head_w * 0.05,  top_front[1] + thick * 0.55)
    bot_q3    = (top_q3[0] - f * head_w * 0.02, top_q3[1] + thick)
    bot_mid   = (cx,                           top_mid[1] + thick)
    bot_q1    = (top_q1[0] + f * head_w * 0.02, top_q1[1] + thick)
    bot_back  = (back_x + f * head_w * 0.04,   top_back[1] + thick * 0.55)

    # Underside (shadowed) drawn first; top felt surface overlaps it.
    pygame.draw.polygon(surf, UNDER, [
        top_back, top_q1, top_mid, top_q3, top_front,
        bot_front, bot_q3, bot_mid, bot_q1, bot_back,
    ])
    pygame.draw.polygon(surf, FELT_MID, [
        top_back, top_q1, top_mid, top_q3, top_front,
        (top_front[0] - f * head_w * 0.04, top_front[1] + thick * 0.45),
        (top_q3[0], top_q3[1] + thick * 0.5),
        (cx, top_mid[1] + thick * 0.45),
        (top_q1[0], top_q1[1] + thick * 0.45),
        (top_back[0] + f * head_w * 0.03, top_back[1] + thick * 0.45),
    ])
    # Highlight along the top edge of the upturned BACK half (back-lit felt).
    if detailed:
        pygame.draw.line(surf, FELT, top_back, top_mid,
                         max(1, round(head_w * 0.035)))

    # ── CROWN ────────────────────────────────────────────────────────────────
    # Teardrop side profile: one continuous felt dome with rounded shoulders.
    # The rear shoulder is the tallest point; the dome slopes gently down
    # toward the front. The lengthwise crease is a single centre dip in the
    # otherwise smooth top — NOT two separate humps — so it reads as a felt
    # hat that's been pinched, not a pair of bumps.
    top_y    = base_y - crown_h           # back shoulder peak height
    front_pk = top_y + head_w * 0.14      # front of the dome rides lower
    dent_y   = top_y + head_w * 0.13      # centre crease dip
    dent_x   = cx + f * crown_hw * 0.06   # crease sits just behind centre

    crown_pts = [
        (crown_front, seat_y),                                    # front base
        (crown_front + f * head_w * 0.01, base_y - crown_h * 0.42),
        (cx + f * crown_hw * 0.62, front_pk + head_w * 0.05),     # front shoulder
        (cx + f * crown_hw * 0.30, front_pk),                     # front peak
        (dent_x, dent_y),                                         # crease dent
        (cx - f * crown_hw * 0.34, top_y),                        # back peak
        (cx - f * crown_hw * 0.70, top_y + head_w * 0.04),        # back shoulder
        (crown_back - f * head_w * 0.01, base_y - crown_h * 0.38),
        (crown_back, seat_y),                                     # back base
    ]
    pygame.draw.polygon(surf, FELT, crown_pts)

    if detailed:
        # Front face in shadow (light from back-upper-left of the profile).
        pygame.draw.polygon(surf, FELT_MID, [
            (crown_front, seat_y),
            (crown_front + f * head_w * 0.01, base_y - crown_h * 0.42),
            (cx + f * crown_hw * 0.62, front_pk + head_w * 0.05),
            (cx + f * crown_hw * 0.30, front_pk),
            (dent_x, dent_y + head_w * 0.05),
            (cx + f * crown_hw * 0.20, seat_y),
        ])
        # Back shoulder highlight ridge.
        pygame.draw.polygon(surf, FELT_HI, [
            (cx - f * crown_hw * 0.34, top_y),
            (cx - f * crown_hw * 0.70, top_y + head_w * 0.04),
            (crown_back - f * head_w * 0.01, base_y - crown_h * 0.55),
            (cx - f * crown_hw * 0.30, base_y - crown_h * 0.62),
        ])
        # The crease itself: a dark valley line from the dent down the dome,
        # the fedora's signature lengthwise pinch.
        pygame.draw.line(surf, FELT_DK,
                         (cx + f * crown_hw * 0.30, front_pk + head_w * 0.01),
                         (dent_x, dent_y),
                         max(1, round(head_w * 0.04)))
        pygame.draw.line(surf, FELT_DK,
                         (dent_x, dent_y),
                         (cx - f * crown_hw * 0.34, top_y + head_w * 0.015),
                         max(1, round(head_w * 0.04)))
        # Side pinch near the front shoulder — the other half of the cue.
        pygame.draw.line(surf, FELT_MID,
                         (cx + f * crown_hw * 0.46, front_pk + head_w * 0.04),
                         (cx + f * crown_hw * 0.40, front_pk + head_w * 0.22),
                         max(1, round(head_w * 0.03)))
    else:
        # Tiny: a soft highlight up the back shoulder so the dome reads round.
        pygame.draw.line(surf, FELT_HI,
                         (cx - f * crown_hw * 0.40, top_y + head_w * 0.06),
                         (cx - f * crown_hw * 0.10, base_y - crown_h * 0.30),
                         max(1, round(head_w * 0.07)))

    # ── GROSGRAIN BAND ───────────────────────────────────────────────────────
    # Wraps the base of the crown just above the brim seat. Drawn as a filled
    # quad that follows the crown base width, with a thin highlight along its
    # top edge to suggest the ribbed ribbon catching light.
    band_h = max(2.0, head_w * 0.12)
    band_top = seat_y - head_w * 0.06 - band_h
    band_l = crown_back
    band_r = crown_front
    pygame.draw.polygon(surf, BAND, [
        (band_l, band_top + head_w * 0.02),
        (band_r, band_top),
        (band_r, band_top + band_h),
        (band_l, band_top + band_h + head_w * 0.01),
    ])
    if detailed:
        pygame.draw.line(surf, BAND_HI,
                         (band_l, band_top + head_w * 0.02),
                         (band_r, band_top),
                         max(1, round(head_w * 0.02)))

        # Small flat bow on the side, set toward the back so the front stays
        # clean (classic placement). Two trapezoid loops + a centre knot.
        bow_cx = cx - f * crown_hw * 0.46
        bow_cy = band_top + band_h * 0.5
        wing   = head_w * 0.10
        bh     = band_h * 0.78
        # back loop
        pygame.draw.polygon(surf, BAND_HI, [
            (bow_cx - f * head_w * 0.015, bow_cy - bh * 0.5),
            (bow_cx - f * (head_w * 0.015 + wing), bow_cy - bh * 0.7),
            (bow_cx - f * (head_w * 0.015 + wing), bow_cy + bh * 0.7),
            (bow_cx - f * head_w * 0.015, bow_cy + bh * 0.5),
        ])
        # front loop
        pygame.draw.polygon(surf, BAND_HI, [
            (bow_cx + f * head_w * 0.015, bow_cy - bh * 0.5),
            (bow_cx + f * (head_w * 0.015 + wing), bow_cy - bh * 0.7),
            (bow_cx + f * (head_w * 0.015 + wing), bow_cy + bh * 0.7),
            (bow_cx + f * head_w * 0.015, bow_cy + bh * 0.5),
        ])
        # knot
        pygame.draw.rect(surf, BAND, (
            bow_cx - max(1, head_w * 0.018),
            bow_cy - bh * 0.5,
            max(2, head_w * 0.036),
            bh,
        ))
