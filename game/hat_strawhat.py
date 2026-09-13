"""Procedural side-profile STRAW HAT for Skybit's coin Store.

One public entry: `draw_hat(surf, cx, base_y, head_w, facing=1)`.

The straw hat reads through a modest farmer/beach silhouette — a LOW
rounded crown and a MEDIUM flat brim with a gently wavy edge — plus two
hero cues: woven warm-wheat straw with horizontal weave lines, and a
simple cloth band wrapping the crown base. Deliberately NOT a sombrero:
the crown is short and dome-soft, the brim is flat-ish and only medium
width, so it never reads as the tall wide-brim Mexican hat.

All geometry derives from (cx, base_y, head_w) so the same code scales
from a hero head (head_w~80) down to a tiny product pip (head_w~18).
Below ~22px the woven-weave micro-texture is gated off so the small icon
keeps a clean low-crown + brim silhouette instead of muddy noise.

No image files, no real brand marks — natural straw tones + a cloth band.
"""
import math
import pygame

# ── straw palette (warm wheat / tan) ─────────────────────────────────────────
# Straw is a warm matte fibre, so the spread is gentle: a bright top catch
# on the crown dome, a mid body, a tan shoulder, and a darker brim
# underside that sits in shadow. The weave lines use the two mid tones so
# they read as woven ridges, not hard ink. The cloth band is a faded red
# that contrasts cleanly against the wheat without going pure saturated.
STRAW_HI   = (244, 220, 150)   # sunlit crown top / brim-edge catch
STRAW      = (228, 196, 116)   # main woven body
STRAW_MID  = (206, 170,  92)   # tan shoulder / weave shadow line
STRAW_DK   = (176, 138,  70)   # crown-base shade under the band
UNDER      = (150, 112,  56)   # brim underside — darkest, in shadow
UNDER_DK   = (128,  94,  46)
BAND       = (176,  72,  62)   # faded red cloth band
BAND_HI    = (208, 104,  92)
BAND_DK    = (138,  52,  46)


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile straw hat sized for a round head of diameter head_w.

    cx        head centre x.
    base_y    brim line — the hat seats on a head whose crown-top is here.
    head_w    head diameter; all proportions derive from it.
    facing    +1 = looking right; -1 mirrors the whole hat. The straw hat
              is near-symmetric, so facing only nudges the weave/shading.
    """
    f = 1 if facing >= 0 else -1
    hw = head_w / 2.0

    # Medium brim — reaches modestly past the head on both sides. Kept well
    # short of sombrero width so it stays a farmer/beach sun hat.
    brim_w   = hw * 1.42
    # LOW crown: a soft dome only ~half the head tall. This short height is
    # the main thing separating it from the tall sombrero cone.
    crown_hw = hw * 0.86
    crown_h  = head_w * 0.40

    detailed = head_w >= 22

    seat_y = base_y + head_w * 0.02      # where the brim meets the crown base
    front_x = cx + f * brim_w
    back_x  = cx - f * brim_w

    # ── BRIM ─────────────────────────────────────────────────────────────────
    # A flat-ish sheet seen edge-on: a long shallow curve that droops only a
    # little at each tip (medium, not sombrero-floppy) with a gently WAVY
    # edge. Thickness tapers toward the tips so the straw reads as a sheet.
    # The top edge dips a touch at the very ends and the underside is drawn
    # first (in shadow) so the rim catches light along the top.
    droop  = head_w * 0.10               # gentle tip droop (modest)
    thick  = max(2.0, head_w * 0.085)    # brim thickness through the middle
    wave   = head_w * 0.035 if detailed else 0.0   # edge wobble amplitude

    # Build top and bottom edge point chains from back tip to front tip.
    # A handful of samples gives the gentle wave without per-pixel noise.
    samples = [-1.0, -0.66, -0.33, 0.0, 0.33, 0.66, 1.0]
    top_pts = []
    bot_pts = []
    for s in samples:
        x = cx + f * brim_w * s
        # Brim rides at base_y in the middle and droops toward the tips.
        edge = abs(s)
        y = base_y + droop * (edge * edge)
        # Gentle wave: a low-frequency ripple along the rim, fading to nil
        # at the centre so only the outer brim looks hand-woven.
        y += math.sin(s * math.pi * 1.5) * wave * edge
        # Thickness shrinks to a near point at the tips.
        t_here = thick * (0.45 + 0.55 * (1.0 - edge))
        top_pts.append((x, y))
        bot_pts.append((x, y + t_here))

    # Underside (shadow) — full slab.
    pygame.draw.polygon(surf, UNDER, top_pts + list(reversed(bot_pts)))
    # Top straw surface — the upper ~60% of the slab catches light.
    top_face = []
    for (tx, ty), (bx, by) in zip(top_pts, bot_pts):
        top_face.append((tx, ty))
    for (tx, ty), (bx, by) in zip(reversed(top_pts), reversed(bot_pts)):
        top_face.append((tx, ty + (by - ty) * 0.58))
    pygame.draw.polygon(surf, STRAW, top_face)

    if detailed:
        # A brighter catch right along the front-of-brim top edge.
        pygame.draw.lines(surf, STRAW_HI, False, top_pts,
                          max(1, round(head_w * 0.03)))
        # Concentric weave: two shallow arcs following the brim sweep so the
        # flat sheet reads as woven rings, not a plain disc.
        for frac in (0.34, 0.66):
            ring = []
            for (tx, ty), (bx, by) in zip(top_pts, bot_pts):
                ring.append((tx, ty + (by - ty) * frac))
            pygame.draw.lines(surf, STRAW_MID, False, ring,
                              max(1, round(head_w * 0.018)))
        # A sliver of darker underside peeking at the front tip sells the
        # brim as a thin curved sheet rather than a flat decal.
        pygame.draw.line(surf, UNDER_DK,
                         bot_pts[-1],
                         (bot_pts[-1][0] - f * head_w * 0.10,
                          bot_pts[-1][1] - head_w * 0.01),
                         max(1, round(head_w * 0.03)))

    # ── CROWN ────────────────────────────────────────────────────────────────
    # A LOW rounded dome — short and soft, the defining straw-hat shape. The
    # underside is curved so it seats on a round head. Sampled as a smooth
    # half-dome arc from back base to front base.
    crown_front = cx + f * crown_hw
    crown_back  = cx - f * crown_hw
    top_y = base_y - crown_h

    dome = []
    steps = 9
    for i in range(steps + 1):
        # Parametrise across the dome; cosine gives a flat-topped low arch
        # rather than a pointy cone (anti-sombrero).
        u = i / steps                      # 0 back -> 1 front
        x = crown_back + (crown_front - crown_back) * u
        # Height profile: rounded shoulders, gently flat top.
        h = math.sin(u * math.pi)
        h = h ** 0.7                       # broaden the top, lower the peak
        y = base_y - crown_h * h
        dome.append((x, y))
    crown_pts = dome + [(crown_front, seat_y), (crown_back, seat_y)]
    pygame.draw.polygon(surf, STRAW, crown_pts)

    if detailed:
        # Sunlit cap across the top of the dome (light from upper-front).
        hi_cap = []
        for (x, y) in dome:
            hi_cap.append((x, y))
        for (x, y) in reversed(dome):
            hi_cap.append((x, y + crown_h * 0.34))
        # Clip the highlight to roughly the upper dome by only filling the
        # front/top half toward the light.
        pygame.draw.polygon(surf, STRAW_HI, [
            (crown_back + (crown_front - crown_back) * 0.18,
             base_y - crown_h * 0.46),
            dome[2], dome[3], dome[4], dome[5], dome[6],
            (crown_back + (crown_front - crown_back) * 0.62,
             base_y - crown_h * 0.40),
        ])
        # Horizontal weave lines wrapping the dome — the woven-straw cue.
        for frac in (0.30, 0.55, 0.78):
            wy = base_y - crown_h * (1.0 - frac) * 0.9
            lx = crown_back + crown_hw * 0.18 * (1.0 - frac)
            rx = crown_front - f * crown_hw * 0.18 * (1.0 - frac)
            pygame.draw.line(surf, STRAW_MID, (lx, wy), (rx, wy),
                             max(1, round(head_w * 0.018)))
        # Soft shade where the dome meets the band so the crown sits proud.
        pygame.draw.line(surf, STRAW_DK,
                         (crown_back + crown_hw * 0.14, seat_y - head_w * 0.04),
                         (crown_front - crown_hw * 0.14, seat_y - head_w * 0.04),
                         max(1, round(head_w * 0.03)))
    else:
        # Tiny: a single soft top highlight keeps the dome reading round.
        pygame.draw.line(surf, STRAW_HI,
                         (cx - crown_hw * 0.4, base_y - crown_h * 0.78),
                         (cx + crown_hw * 0.4, base_y - crown_h * 0.78),
                         max(1, round(head_w * 0.09)))

    # ── CLOTH BAND ───────────────────────────────────────────────────────────
    # A simple ribbon wrapping the crown base, just above the brim seat. Drawn
    # as a filled band following the crown width with a highlight on top and a
    # shadow beneath so it reads as folded cloth, not a painted stripe.
    band_h   = max(2.0, head_w * 0.11)
    band_top = seat_y - head_w * 0.03 - band_h
    bl = crown_back + crown_hw * 0.06
    br = crown_front - f * crown_hw * 0.0
    pygame.draw.polygon(surf, BAND, [
        (bl, band_top + head_w * 0.012),
        (br, band_top),
        (br, band_top + band_h),
        (bl, band_top + band_h + head_w * 0.006),
    ])
    if detailed:
        pygame.draw.line(surf, BAND_HI,
                         (bl, band_top + head_w * 0.012),
                         (br, band_top),
                         max(1, round(head_w * 0.022)))
        pygame.draw.line(surf, BAND_DK,
                         (bl, band_top + band_h + head_w * 0.006),
                         (br, band_top + band_h),
                         max(1, round(head_w * 0.02)))
        # A small flat knot toward the back so the band reads as cloth tied
        # round the crown rather than a paint ring.
        knot_x = cx - f * crown_hw * 0.52
        knot_y = band_top + band_h * 0.5
        kw = head_w * 0.06
        kh = band_h * 0.92
        pygame.draw.polygon(surf, BAND_DK, [
            (knot_x - kw, knot_y - kh * 0.55),
            (knot_x + kw, knot_y - kh * 0.45),
            (knot_x + kw, knot_y + kh * 0.45),
            (knot_x - kw, knot_y + kh * 0.55),
        ])
        pygame.draw.line(surf, BAND_HI,
                         (knot_x - kw, knot_y - kh * 0.55),
                         (knot_x + kw, knot_y - kh * 0.45),
                         max(1, round(head_w * 0.018)))
