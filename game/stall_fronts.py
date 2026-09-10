"""Chosen stall-front designs for the lagoon hub's open categories.

Each open stall keeps its own item presentation — PARROTS: the goods slung in
a lashed rope cradle over a knotted swag valance; PARCELS: a grounded paper
floor lantern the hero stands in front of; COSTUMES: a turned-timber pedestal
in a hard pool of light — but every stall shares one sign: a bulb-studded
stepped cartouche in the awning's own lacquer red, with cream piping tracing
its outline, so the sign reads as kin to the red/cream flags below it.

draw_hut() in store_hub calls draw_sign()/draw_item() for any group present
in ITEM; groups outside that set keep the stock cabochon + name-board front
untouched, so the four not-yet-open categories are unaffected when they ship.

DESIGNS holds every item presentation the design effort produced, including
two — `hook_rail` and `counter` — that no stall wears yet. They are kept whole
rather than deleted because the shuttered categories will need them, and
tests/test_stall_fronts.py renders all five so a reserve design cannot rot
unnoticed while store_hub evolves around it.
"""
import math

import pygame

from game.store_hub import (
    m, font, lerp_color, vgrad, gradient_text, capped_glow, _glyph_base,
    _group_thumb, _punch_contrast, _rim_light,
    GOLD, GOLD_PALE, GOLD_DEEP, GOLD_A_TOP, GOLD_A_BOT,
    WOOD_HI, WOOD_MID, WOOD_LO, WOOD_EDGE, STALL_DARK, LABEL_KEY,
    AWN_CREAM_D,
)

# Hemp lane, derived from the stall's own timber so the rigging never reads as
# a foreign material — cord is bleached wood, not rope-coloured plastic.
ROPE_HI = lerp_color(WOOD_HI, (244, 232, 206), 0.42)
ROPE_MID = lerp_color(WOOD_MID, AWN_CREAM_D, 0.30)
ROPE_LO = lerp_color(WOOD_LO, WOOD_EDGE, 0.35)
SWAG_TOP = (138, 96, 72)
SWAG_BOT = (96, 64, 48)

# Washi ladder for the lantern: the shell sits one value step below the sign
# so the hero — front-lit from the same low upper-left sun — stays the
# brightest thing in the stall.
LANT_HI = (186, 150, 100)
LANT_LO = (150, 116, 74)
LANT_CORD = (196, 168, 124)
FLANK_SHADE = lerp_color(WOOD_LO, STALL_DARK, 0.35)

# Sign: awning-matched lacquer red, cream piping, gold bulbs a notch under
# GOLD_PALE so the sign's peak can never climb above the hero's.
CARTOUCHE_TOP = (122, 26, 30)
CARTOUCHE_BOT = (74, 12, 18)
PIPING_COLOR = AWN_CREAM_D
BULB_SEAT = GOLD_DEEP
BULB_GLASS = lerp_color(GOLD_PALE, GOLD, 0.18)
POOL_CORE = lerp_color(WOOD_HI, GOLD_PALE, 0.35)
INK_PT = 11.5  # the largest size that still fits COSTUMES (widest label)
               # inside the cartouche


def _sv(v, scale):
    """Logical px -> device px at a stall's own scale factor."""
    return int(m(v) * scale)


def _px(v, scale, lo=1):
    return max(lo, int(m(v) * scale))


# =============================================================================
# Rigging primitives (PARROTS item) — one low golden-hour key from the upper
# left, so every cord carries its highlight up-left and its shade down-right.
# =============================================================================
def _rope_run(surf, pts, w, twist=True):
    """A twisted hemp run along a polyline: a shaded core plus alternating
    diagonal ticks so the cord reads as laid strands rather than a drawn line.
    Ticks are authored at SS and dissolve into fibre texture on the downscale."""
    w = max(2, int(w))
    lo = [(x + w * 0.30, y + w * 0.34) for x, y in pts]
    hi = [(x - w * 0.24, y - w * 0.28) for x, y in pts]
    pygame.draw.lines(surf, ROPE_LO, False, lo, w)
    pygame.draw.lines(surf, ROPE_MID, False, pts, w)
    if w >= 3:
        pygame.draw.lines(surf, ROPE_HI, False, hi, max(1, int(w * 0.42)))
    if not twist or w < 3:
        return
    step = max(m(2), int(w * 1.7))
    carry = 0.0
    tick = 0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg <= 0:
            continue
        ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
        px, py = -uy, ux
        d = carry
        while d < seg:
            cxp, cyp = x0 + ux * d, y0 + uy * d
            col = ROPE_LO if tick % 2 else ROPE_HI
            ax = cxp - ux * w * 0.34 - px * w * 0.44
            ay = cyp - uy * w * 0.34 - py * w * 0.44
            bx = cxp + ux * w * 0.34 + px * w * 0.44
            by = cyp + uy * w * 0.34 + py * w * 0.44
            pygame.draw.line(surf, col, (ax, ay), (bx, by), max(1, int(w * 0.34)))
            tick += 1
            d += step
        carry = d - seg


def _lashing(surf, cx, cy, half_w, half_h, wraps, w):
    """A whipped lashing: N tight wraps banded across a spar or post, each wrap
    lit on its upper-left shoulder — the joint that tells the eye this thing was
    TIED on, not printed on."""
    w = max(2, int(w))
    span = half_w * 2
    for i in range(wraps):
        t = (i + 0.5) / wraps
        x = cx - half_w + span * t
        lean = half_h * 0.34
        pygame.draw.line(surf, ROPE_LO, (x + w * 0.3, cy - half_h + w * 0.3),
                         (x - lean + w * 0.3, cy + half_h + w * 0.3), w)
        pygame.draw.line(surf, ROPE_MID, (x, cy - half_h),
                         (x - lean, cy + half_h), w)
        pygame.draw.line(surf, ROPE_HI, (x - w * 0.22, cy - half_h),
                         (x - lean - w * 0.22, cy + half_h),
                         max(1, int(w * 0.40)))


def _knot(surf, x, y, r):
    """A tied-off knot boss: two overlapping lobes, lit up-left."""
    r = max(2, int(r))
    pygame.draw.circle(surf, ROPE_LO, (int(x + r * 0.28), int(y + r * 0.32)), r)
    pygame.draw.circle(surf, ROPE_MID, (int(x), int(y)), r)
    pygame.draw.circle(surf, WOOD_HI, (int(x - r * 0.30), int(y - r * 0.34)),
                       max(1, int(r * 0.58)))


def _fill_poly_vgrad(surf, pts, top, bot):
    """Fill an arbitrary polygon with a vertical ramp — the gradient is built on
    the polygon's own bbox so the ramp always spans the shape, never the frame."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = int(min(xs)) - 1, int(min(ys)) - 1
    w = max(1, int(max(xs)) - x0 + 2)
    h = max(1, int(max(ys)) - y0 + 2)
    body = vgrad(w, h, 0, top, bot)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - x0, p[1] - y0) for p in pts])
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (x0, y0))


def _soft_fold(surf, x, y_top, y_bot, w, alpha=30):
    """A slack fold read as a soft vertical shade band, feathered to nothing at
    its edges so it never becomes a drawn stripe."""
    w = max(2, int(w))
    band = pygame.Surface((w * 2 + 1, max(1, int(y_bot - y_top))), pygame.SRCALPHA)
    for i in range(-w, w + 1):
        a = int(alpha * (1.0 - abs(i) / (w + 0.5)) ** 1.4)
        if a <= 0:
            continue
        pygame.draw.line(band, (0, 0, 0, a), (i + w, 0), (i + w, band.get_height()))
    surf.blit(band, (int(x - w), int(y_top)))


# =============================================================================
# PARROTS item — the goods slung in a lashed rope cradle over a knotted swag.
# =============================================================================
def _item_sling(surf, ctx):
    cx = ctx["cx"]
    deck_y = ctx["deck_y"]
    body_top = ctx["body_top"]
    half_w = ctx["half_w"]
    scale = ctx["scale"]
    group = ctx["group"]

    # The m(8) posts are hard walls, so the span stops a hair short of the inner
    # face and lets the line cap land flush instead of biting into the timber.
    post_in = half_w - m(8) - max(3, _sv(2.0, scale))
    rope_y = body_top + _sv(15, scale)
    rope_w = max(m(1.6), _sv(1.8, scale))

    # ---- swag valance: mid-tone by contract. It is the backdrop the goods are
    # read against, so it must sit BELOW the kraft parcel and below the awning
    # cream in value or it starts competing for the eye.
    swag_x = min(_sv(34, scale), post_in - _sv(8, scale))
    swag_top = body_top + _sv(16, scale)
    swag_dip = body_top + _sv(30, scale)
    y_out = swag_top + max(2, _sv(3, scale))
    y_mid = swag_top + max(3, int((swag_dip - swag_top) * 0.35))
    dip = max(2, swag_dip - y_mid)

    steps = 20
    for s in (-1, 1):
        pts_b = []
        for i in range(steps + 1):
            u = i / steps
            x = cx + s * swag_x * (1.0 - u)
            y = y_out + (y_mid - y_out) * u + dip * math.sin(math.pi * u)
            pts_b.append((x, y))
        top_line = [(cx + s * swag_x, swag_top), (cx, swag_top + max(1, m(1)))]
        _fill_poly_vgrad(surf, top_line + pts_b[::-1], SWAG_TOP, SWAG_BOT)

    for fx in (cx - swag_x * 0.55, cx, cx + swag_x * 0.55):
        u = 1.0 - abs(fx - cx) / max(1.0, float(swag_x))
        fy = y_out + (y_mid - y_out) * u + dip * math.sin(math.pi * u)
        _soft_fold(surf, fx, swag_top + max(1, m(1)), fy - m(1),
                   max(2, _sv(2.0, scale)), alpha=46)

    # Swag knots tie off to the posts, and the leftover cloth keeps running past
    # them as short tails — the flank is rigging, not empty frame.
    for s in (-1, 1):
        kx = cx + s * swag_x
        tw = max(3, _sv(5, scale))
        tl = _sv(13, scale)
        tail = [(kx, swag_top + m(1)),
                (kx + s * tw, swag_top + m(1)),
                (kx + s * (tw + _sv(2.5, scale)), swag_top + tl),
                (kx + s * max(1, int(tw * 0.35)), swag_top + int(tl * 0.86))]
        _fill_poly_vgrad(surf, tail, SWAG_TOP, SWAG_BOT)
        _rope_run(surf, [(kx, swag_top + max(1, _sv(1.5, scale))),
                         (cx + s * post_in, swag_top - max(1, _sv(1.0, scale)))],
                  max(2, _sv(1.2, scale)), twist=False)
        _knot(surf, kx, swag_top + max(2, _sv(2.0, scale)),
              max(2, _sv(2.2, scale)))

    # ---- the main span: one rope, post to post, whipped at both ends.
    _rope_run(surf, [(cx - post_in, rope_y), (cx + post_in, rope_y)], rope_w)
    for s in (-1, 1):
        _lashing(surf, cx + s * (post_in - _sv(3, scale)), rope_y,
                 max(2, _sv(2.4, scale)), rope_w * 1.7, 3,
                 max(2, _sv(1.4, scale)))

    # ---- the cradle: two risers into a five-strand net sling.
    sling_x = _sv(30, scale)
    env = _sv(45, scale)
    item_bot = deck_y - m(9)
    end_y = item_bot - _sv(10, scale)
    sag_base = _sv(12, scale)

    def cord(k, sag_f, skew):
        pts = []
        for i in range(15):
            u = i / 14.0
            x = cx - sling_x + 2 * sling_x * u
            y = (end_y + skew * (1 - 2 * u) + sag_base * sag_f
                 * math.sin(math.pi * u))
            pts.append((x, y))
        return pts

    strands = [(0.30, _sv(2.4, scale)), (0.55, -_sv(1.6, scale)),
               (1.00, 0.0), (0.78, _sv(1.6, scale)), (0.42, -_sv(2.4, scale))]
    cw = max(2, _sv(1.5, scale))

    for s in (-1, 1):
        _rope_run(surf, [(cx + s * sling_x, rope_y),
                         (cx + s * sling_x, end_y)], max(2, _sv(1.4, scale)))

    for k in (2, 3, 4):
        _rope_run(surf, cord(k, *strands[k]), cw)
    for s in (-1, 1):
        _knot(surf, cx + s * sling_x, end_y, max(2, _sv(1.7, scale)))

    # ---- the goods. No dome, no glass: the item IS the hero, so it gets the
    # full envelope the rig leaves and the only real glow on the stall.
    src, _lb = _group_thumb(group)
    w, h = src.get_size()
    # Contain to the box the RIG leaves — width to the envelope, height to the
    # clear air between the span rope and the item's hang line — and solve it on
    # the POST-tilt footprint, or a near-square item grows through the rope it is
    # supposed to be hanging from.
    # The risers are SHORT: a heavy load rides right up under its span, and the
    # extra device pixel of hang would cost the goods legibility at 1x.
    avail = max(m(8), item_bot - rope_y - 1)
    # Rotate the SOURCE first so the hero is resampled once — tilting after the
    # downscale costs a second resample and half the edge acuity at 1x. The rim
    # still bakes after the tilt, locked to the one up-left key.
    rot = pygame.transform.rotate(src, 3)
    rw, rh = rot.get_size()
    f = min(env / rw, avail / rh)
    img = pygame.transform.smoothscale(
        rot, (max(1, int(rw * f)), max(1, int(rh * f))))
    img = _punch_contrast(img)
    bb = img.get_bounding_rect()
    ix = int(cx - bb.centerx)
    iy = int(item_bot - bb.bottom)

    capped_glow(surf, cx, int(iy + bb.centery), int(env * 0.82), GOLD, 30,
                layers=9)

    sh_img = img.copy()
    sh_img.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for i, a in enumerate((44, 60, 74)):
        sh_img.set_alpha(a)
        d = _sv(3.0, scale) - i
        surf.blit(sh_img, (ix + d, iy + d + _sv(1.5, scale)))
    sill = pygame.Surface((bb.width + m(8), max(3, _sv(5, scale))),
                          pygame.SRCALPHA)
    pygame.draw.ellipse(sill, (12, 8, 6, 105), sill.get_rect())
    surf.blit(sill, (int(cx - sill.get_width() * 0.5 + _sv(2, scale)),
                     int(deck_y - m(8) - sill.get_height() * 0.55)))

    surf.blit(_rim_light(img), (ix, iy), special_flags=pygame.BLEND_ADD)
    surf.blit(img, (ix, iy))

    # Two strands cross IN FRONT of the load, so the sling reads as carrying the
    # item rather than sitting politely behind it.
    for k in (0, 1):
        _rope_run(surf, cord(k, *strands[k]), cw)

    # ---- flank capacity: a coiled spare hank left, a slack empty sling right.
    peg_y = swag_top + _sv(26, scale)
    for s in (-1, 1):
        px = cx + s * (post_in - max(2, _sv(2, scale)))
        pygame.draw.line(surf, WOOD_LO, (px, peg_y),
                         (px - s * _sv(5, scale), peg_y), max(2, _sv(2, scale)))
        pygame.draw.line(surf, WOOD_HI, (px, peg_y - max(1, _sv(0.8, scale))),
                         (px - s * _sv(5, scale), peg_y - max(1, _sv(0.8, scale))),
                         max(1, _sv(0.9, scale)))

    hx = cx - (post_in - _sv(7, scale))
    hr = max(3, _sv(5, scale))
    _rope_run(surf, [(cx - post_in + _sv(2, scale), peg_y),
                     (hx, peg_y + hr)], max(2, _sv(1.2, scale)), twist=False)
    for i in range(3):
        rr = hr - i * max(1, _sv(1.4, scale))
        if rr < 2:
            break
        pygame.draw.ellipse(surf, ROPE_LO,
                            (hx - rr + m(1), peg_y + hr - rr * 1.1 + m(1),
                             rr * 2, rr * 2.2), max(2, _sv(1.1, scale)))
        pygame.draw.ellipse(surf, ROPE_MID,
                            (hx - rr, peg_y + hr - rr * 1.1, rr * 2, rr * 2.2),
                            max(1, _sv(0.9, scale)))

    ex = cx + (post_in - _sv(3, scale))
    ei = cx + (post_in - _sv(15, scale))
    slack = []
    for i in range(13):
        u = i / 12.0
        slack.append((ei + (ex - ei) * u,
                      peg_y + _sv(13, scale) * math.sin(math.pi * u)))
    _rope_run(surf, slack, max(2, _sv(1.2, scale)))
    _knot(surf, ei, peg_y + max(1, _sv(1.0, scale)), max(2, _sv(1.6, scale)))


# =============================================================================
# PARCELS item — a grounded paper floor lantern (andon) the hero stands in.
# =============================================================================
def _lantern_geom(ctx):
    """Every lantern part hangs off ONE metric set so the shell, the shadow it
    receives and the hero that casts it can never drift apart."""
    cx, deck_y, scale = ctx["cx"], ctx["deck_y"], ctx["scale"]
    sill = deck_y - m(8)
    pw, ph = _px(58, scale), _px(33, scale)
    foot_h = _px(3, scale, 2)
    return dict(
        cx=cx, scale=scale, sill=sill, foot_h=foot_h,
        awn_b=ctx["body_top"] + int(m(15) * scale),
        panel=pygame.Rect(cx - pw // 2, sill - foot_h - ph, pw, ph),
        fw=_px(5, scale, 3), hair=max(1, m(0.8)),
        box=int(m(44) * scale), base=deck_y - m(10),
    )


def _top_round(w, h, rad, top, bot):
    """Vertical gradient panel with only its TOP corners rounded — a paper shell
    stretched over a frame reads as square where it meets the floor."""
    body = vgrad(w, h, 0, top, bot)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_top_left_radius=rad, border_top_right_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return body


def _lantern_front_light(img, warm=(255, 216, 162), peak=52, ambient=18):
    """The ONE key, applied to the hero as a DIRECTIONAL additive ramp that is
    hottest at the upper-left and falls to ambient at the lower-right.

    A flat _punch_contrast alone lifts the whole silhouette evenly, which reads
    as a washed sticker AND still loses to warm paper at the shadow side; a
    directional ramp buys the same average lift while keeping modelling, so the
    hero sits IN the lantern's light instead of being pasted over it.

    The ramp is a smooth field, so it is authored on a small proxy surface and
    scaled up rather than walked pixel by pixel: a per-pixel Python loop over
    the hero is the classic pygbag cliff, and this is the same picture for a
    fraction of the work. BLEND_RGB_ADD leaves alpha alone, so transparent
    pixels stay transparent without needing to be skipped one at a time."""
    w, h = img.get_size()
    pw, ph = max(2, min(w, 48)), max(2, min(h, 48))
    ramp = pygame.Surface((pw, ph))
    for py in range(ph):
        ty = py / max(1, ph - 1)
        for px in range(pw):
            t = max(0.0, 1.0 - (px / max(1, pw - 1) * 0.55 + ty * 0.45))
            k = (ambient + peak * t ** 1.15) / 255.0
            ramp.set_at((px, py), (min(255, int(warm[0] * k)),
                                   min(255, int(warm[1] * k)),
                                   min(255, int(warm[2] * k))))
    out = img.copy()
    out.blit(pygame.transform.smoothscale(ramp, (w, h)), (0, 0),
             special_flags=pygame.BLEND_RGB_ADD)
    return out


def _item_lantern(surf, ctx):
    cx, scale = ctx["cx"], ctx["scale"]
    g = _lantern_geom(ctx)
    sill, awn_b, panel = g["sill"], g["awn_b"], g["panel"]
    pw, ph = panel.w, panel.h
    fw, hair = g["fw"], g["hair"]

    # The ~22px of opening either side of the shell is answered with STRUCTURE:
    # two bamboo uprights the lantern paper is strung between. They are the dark
    # rests that let lit paper + hero read as one bright centre.
    ux = _px(38, scale)
    uw = _px(3.2, scale, 3)
    for sgn in (-1, 1):
        x0 = cx + sgn * ux - uw // 2
        col = pygame.Rect(x0, awn_b, uw, sill - awn_b)
        if sgn < 0:
            surf.blit(vgrad(uw, col.h, 0, WOOD_MID, WOOD_LO), col.topleft)
            pygame.draw.line(surf, WOOD_HI, (x0, col.top), (x0, col.bottom - 1), 1)
            # the one key grazes the near upright's upper third and dies out
            wedge = pygame.Surface((uw, col.h), pygame.SRCALPHA)
            for y in range(int(col.h * 0.55)):
                a = int(80 * (1 - y / (col.h * 0.55)) ** 1.5)
                pygame.draw.line(wedge, (255, 206, 150, a), (0, y), (uw, y))
            surf.blit(wedge, col.topleft)
        else:
            surf.blit(vgrad(uw, col.h, 0, lerp_color(WOOD_LO, STALL_DARK, 0.55),
                            STALL_DARK), col.topleft)
        pygame.draw.line(surf, WOOD_EDGE, (x0 + uw - 1, col.top),
                         (x0 + uw - 1, col.bottom - 1), 1)

    for f in (0.20, 0.50, 0.80):
        cy = int(panel.top + panel.h * f)
        for sgn in (-1, 1):
            x0 = cx + sgn * ux
            inner = x0 - sgn * uw // 2
            edge = cx + sgn * (pw // 2 + fw)
            pygame.draw.line(surf, (*LANT_CORD, 150), (inner, cy), (edge, cy), hair)
            for k in (-1, 1):
                pygame.draw.line(surf, (*LANT_CORD, 200),
                                 (x0 - uw // 2 - 1, cy + k * hair),
                                 (x0 + uw // 2 + 1, cy + k * hair), 1)

    # Warmth seat only — a capped bleed behind the shell so the lantern separates
    # from STALL_DARK. It sits BEHIND the paper, so it never lifts the hero, and
    # it is clipped to the opening so it cannot wash over the deck lip or the
    # side posts, which are hard walls of the stall architecture.
    in_half = ctx["half_w"] - m(8)
    old_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(cx - in_half, awn_b, in_half * 2, sill - awn_b))
    capped_glow(surf, cx, panel.centery, int(pw * 0.62), GOLD, 22, layers=8)
    surf.set_clip(old_clip)

    for sgn in (-1, 1):
        ex = cx + sgn * pw // 2
        lean = _px(1.5, scale, 1)
        pygame.draw.polygon(surf, FLANK_SHADE, [
            (ex, panel.top + _px(2, scale)),
            (ex + sgn * fw, panel.top + _px(2, scale) + lean),
            (ex + sgn * fw, panel.bottom + lean),
            (ex, panel.bottom)])
        pygame.draw.line(surf, lerp_color(FLANK_SHADE, WOOD_HI, 0.35 if sgn < 0 else 0.10),
                         (ex + sgn * fw, panel.top + _px(2, scale) + lean),
                         (ex + sgn * fw, panel.bottom + lean), 1)

    surf.blit(_top_round(pw, ph, _px(6, scale, 3), LANT_HI, LANT_LO), panel.topleft)
    for k in range(1, 5):
        ry = panel.top + int(panel.h * k / 5)
        rib = pygame.Surface((pw, hair), pygame.SRCALPHA)
        rib.fill((*lerp_color(LANT_LO, WOOD_EDGE, 0.45), 140))
        surf.blit(rib, (panel.left, ry))
    pygame.draw.line(surf, lerp_color(LANT_HI, WOOD_EDGE, 0.30),
                     (panel.right - 1, panel.top + _px(6, scale, 3)),
                     (panel.right - 1, panel.bottom - 1), hair)

    foot = pygame.Rect(panel.left - _px(2, scale), sill - g["foot_h"],
                       pw + _px(4, scale), g["foot_h"])
    surf.blit(vgrad(foot.w, foot.h, 0, WOOD_HI, WOOD_LO), foot.topleft)
    pygame.draw.line(surf, WOOD_EDGE, (foot.left, foot.bottom - 1),
                     (foot.right - 1, foot.bottom - 1), 1)
    for sgn in (-1, 1):
        rx = cx + sgn * (pw // 2 - _px(4, scale))
        pygame.draw.line(surf, lerp_color(WOOD_LO, WOOD_EDGE, 0.5),
                         (rx, foot.top), (rx, foot.bottom - 1), 1)

    # ---- the hero, standing in front of the lit shell.
    src, _lb = _group_thumb(ctx["group"])
    w, h = src.get_size()
    s = g["box"] / max(w, h)
    img = pygame.transform.smoothscale(src, (max(1, int(w * s)), max(1, int(h * s))))
    img = _punch_contrast(img, boost=40)
    img = _lantern_front_light(img)
    r = img.get_rect(midbottom=(g["cx"], g["base"]))

    # The hero stands IN FRONT of lit paper, so the key must throw its shadow
    # ONTO that paper — down-right, clipped to the shell. Without it the item
    # reads as a silhouette cut out of a lantern; with it the paper is a lit
    # ground the item is planted on. This is the whole concept's load-bearing
    # beat, so it is measured, not eyeballed.
    sil = img.copy()
    sil.fill((8, 5, 3, 255), special_flags=pygame.BLEND_RGBA_MULT)
    step = _px(1.1, scale, 1)
    old_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(panel.left, panel.top,
                              panel.w + g["fw"], panel.h + g["foot_h"]))
    for k, a in ((1, 76), (2, 58), (3, 42), (4, 26), (5, 14)):
        sil.set_alpha(a)
        surf.blit(sil, (r.x + k * step, r.y + k * step))
    surf.set_clip(old_clip)

    # Contact shadow: cast down-RIGHT across the lantern floor and onto the
    # sill, so the item is planted by the same sun that lights it.
    ao = pygame.Surface((int(r.width * 1.45), _px(7, scale, 4)), pygame.SRCALPHA)
    for i in range(4):
        a = int(120 * (1 - i / 4))
        pygame.draw.ellipse(ao, (12, 8, 4, a),
                            (i * 2, i, ao.get_width() - i * 4, ao.get_height() - i * 2))
    surf.blit(ao, (r.centerx - ao.get_width() // 2 + _px(3, scale),
                   r.bottom - ao.get_height() // 2))

    surf.blit(_rim_light(img), r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(img, r.topleft)


# =============================================================================
# SIGN — a bulb-studded stepped cartouche in the awning's own lacquer red,
# shared by every open stall.
# =============================================================================
def _cartouche_points(cx, bottom_y, half_c, half_1, half_2, t0, t1, t2):
    """Stepped marquee silhouette: one tall central block whose top steps DOWN
    and OUT twice per side onto a shared flat bottom edge."""
    return [
        (cx - half_2, bottom_y), (cx - half_2, t2), (cx - half_1, t2),
        (cx - half_1, t1), (cx - half_c, t1), (cx - half_c, t0),
        (cx + half_c, t0), (cx + half_c, t1), (cx + half_1, t1),
        (cx + half_1, t2), (cx + half_2, t2), (cx + half_2, bottom_y),
    ]


def draw_sign(surf, ctx):
    cx, scale, label = ctx["cx"], ctx["scale"], ctx["label"]
    body_top = ctx["body_top"]

    # the awning seam is a hard ceiling for the opening below, so the board is
    # seated a hair above it and never dips onto the stripes.
    bottom_y = body_top - int(m(3) * scale)
    h = int(m(17) * scale)
    step = int(m(4) * scale)
    half_c, half_1, half_2 = (int(m(38) * scale), int(m(41) * scale),
                              int(m(44) * scale))
    t0 = bottom_y - h
    t1, t2 = t0 + step, t0 + step * 2

    pts = _cartouche_points(cx, bottom_y, half_c, half_1, half_2, t0, t1, t2)
    off = max(1, int(m(1.5) * scale))

    # one light (low sun, upper-left) => the board's own shadow falls down-right
    # onto the thatch, which is what lifts it off the roof.
    shadow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 90),
                        [(x + off, y + off) for x, y in pts])
    surf.blit(shadow, (0, 0))

    x0, y0 = cx - half_2, t0
    bw, bh = half_2 * 2, bottom_y - t0
    body = vgrad(bw, bh, 0, CARTOUCHE_TOP, CARTOUCHE_BOT)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(x - x0, y - y0) for x, y in pts])
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (x0, y0))

    pygame.draw.polygon(surf, WOOD_EDGE, pts, max(1, int(m(1.2) * scale)))

    d = max(1, int(m(2) * scale))
    bead = _cartouche_points(cx, bottom_y - d, half_c - d, half_1 - d,
                             half_2 - d, t0 + d, t1 + d, t2 + d)
    pygame.draw.polygon(surf, PIPING_COLOR, bead, max(1, m(0.5)))

    f = font(INK_PT * scale)
    gradient_text(surf, label, f, (cx, t0 + int(h * 0.56)),
                  GOLD_A_TOP, GOLD_A_BOT, weight=m(1.0 * scale),
                  keyline=LABEL_KEY, kw=m(1.0), shadow=False, tracking=m(0.6))

    # exactly six bulbs, each a discrete disc on its own seat — a fairy-light
    # dusting of 1px points would only read as noise after the downscale.
    r = max(2, int(round(m(1.5) * scale)))
    seat = max(1, m(0.8))
    pad = m(8)
    glow = pygame.Surface((bw + pad * 2, bh + pad * 2), pygame.SRCALPHA)
    bulbs = []
    for k in (12, 28, 42):
        for sgn in (-1, 1):
            bx = cx + sgn * int(m(k) * scale)
            ax = abs(bx - cx)
            by = t0 if ax <= half_c else (t1 if ax <= half_1 else t2)
            bulbs.append((bx, by))
    for bx, by in bulbs:
        capped_glow(glow, bx - x0 + pad, by - y0 + pad, m(5), GOLD, 30)
    surf.blit(glow, (x0 - pad, y0 - pad))
    for bx, by in bulbs:
        pygame.draw.circle(surf, BULB_SEAT, (bx, by), r + seat)
        pygame.draw.circle(surf, BULB_GLASS, (bx, by), r)
        pygame.draw.circle(surf, lerp_color(BULB_GLASS, WOOD_EDGE, 0.35),
                           (bx, by), r, 1)


# =============================================================================
# COSTUMES item — a turned-timber pedestal in a hard pool of light.
# =============================================================================
def _light_pool(surf, cx, bottom_y, w, h):
    """The spotlight itself, read as a POOL on the floor: a warm elliptical
    ramp alpha-feathered to nothing at its rim. No cone, no beam.

    The ramp is authored on a small proxy and scaled up rather than walked
    pixel by pixel: the field is smooth, so the picture is the same, and a
    per-pixel Python loop is the kind of thing that costs little natively and
    a great deal in the browser."""
    pw, ph = max(2, min(w, 40)), max(2, min(h, 40))
    proxy = pygame.Surface((pw, ph), pygame.SRCALPHA)
    hw, hh = pw / 2.0, ph / 2.0
    for py in range(ph):
        dy = (py + 0.5 - hh) / hh
        for px in range(pw):
            dx = (px + 0.5 - hw) / hw
            rr = math.sqrt(dx * dx + dy * dy)
            if rr >= 1.0:
                continue
            k = 1.0 - rr
            col = lerp_color(WOOD_MID, POOL_CORE, min(1.0, k ** 0.75))
            proxy.set_at((px, py), (*col, int(255 * k ** 0.85)))
    surf.blit(pygame.transform.smoothscale(proxy, (w, h)),
              (cx - w // 2, bottom_y - h))


def _pedestal(surf, cx, base_y, scale):
    """A turned baluster cut to the three elements that survive the 1x
    downscale: foot disc, short tapered shaft carrying the single gold bead,
    top plate. Every upper-left curve takes WOOD_HI and every lower-right one
    WOOD_EDGE so the turning still reads."""
    total = int(m(4.7) * scale)
    ys = [base_y - int(round(total * f / 10.0))
          for f in (0.0, 2.5, 7.5, 10.0)]
    hi, lo = WOOD_HI, WOOD_EDGE

    def band(y_bot, y_top, w_bot, w_top, ellipse=False):
        y_top = min(y_top, y_bot - 1)
        rect = pygame.Rect(cx - max(w_bot, w_top) // 2, y_top,
                           max(2, max(w_bot, w_top)), y_bot - y_top)
        if ellipse:
            pygame.draw.ellipse(surf, WOOD_LO, rect)
            pygame.draw.arc(surf, hi, rect, math.radians(95), math.radians(185),
                            max(1, m(0.6)))
            pygame.draw.arc(surf, lo, rect, math.radians(275), math.radians(360),
                            max(1, m(0.6)))
        else:
            pts = [(cx - w_bot // 2, y_bot), (cx - w_top // 2, y_top),
                   (cx + w_top // 2, y_top), (cx + w_bot // 2, y_bot)]
            pygame.draw.polygon(surf, WOOD_LO, pts)
            pygame.draw.line(surf, hi, pts[0], pts[1], max(1, m(0.6)))
            pygame.draw.line(surf, lo, pts[2], pts[3], max(1, m(0.6)))
        return rect

    w = lambda v: max(2, int(m(v) * scale))
    band(ys[0], ys[1], w(18), w(18), ellipse=True)
    shaft = band(ys[1], ys[2], w(9), w(7))
    plate = band(ys[2], ys[3], w(20), w(20))
    pygame.draw.line(surf, hi, plate.topleft, (plate.right - 1, plate.top),
                     max(1, m(0.6)))
    pygame.draw.line(surf, lo, (plate.left, plate.bottom - 1),
                     (plate.right - 1, plate.bottom - 1), max(1, m(0.6)))
    bead = max(1, int(round(m(0.7) * scale)))
    bcx = cx - max(1, int(m(2) * scale))
    pygame.draw.circle(surf, GOLD_DEEP, (bcx, shaft.centery), bead + 1)
    pygame.draw.circle(surf, GOLD_PALE, (bcx, shaft.centery), bead)
    return ys[3]


def _item_pedestal(surf, ctx):
    cx, deck_y, scale, group = ctx["cx"], ctx["deck_y"], ctx["scale"], ctx["group"]
    body_top, half_w = ctx["body_top"], ctx["half_w"]

    sill_y = deck_y - m(8)                      # deck lip: hard floor
    hem_y = body_top + int(m(15) * scale)       # awning hem: hard ceiling
    open_l, open_r = cx - half_w + m(8), cx + half_w - m(8)
    prev_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(open_l, hem_y, open_r - open_l, sill_y - hem_y))

    # hard vignette: past the light pool the interior drops to STALL_DARK so
    # the eye is squeezed back onto the lit hero instead of wandering the sill.
    half_open = (open_r - open_l) // 2
    knee = int(m(39) * scale)
    vig = pygame.Surface((open_r - open_l, sill_y - hem_y), pygame.SRCALPHA)
    for px in range(vig.get_width()):
        t = (abs(open_l + px - cx) - knee) / max(1, half_open - knee)
        a = int(210 * max(0.0, min(1.0, t)) ** 1.1)
        if a > 0:
            pygame.draw.line(vig, (*STALL_DARK, a), (px, 0),
                             (px, vig.get_height()))
    surf.blit(vig, (open_l, hem_y))

    pool_w, pool_h = int(m(46) * scale), max(3, int(m(7) * scale))
    _light_pool(surf, cx, sill_y, pool_w, pool_h)
    capped_glow(surf, cx, sill_y - pool_h // 2, int(m(16) * scale), GOLD, 22)

    # the pedestal stands one pixel BEHIND the deck lip, which is what buys the
    # contact shadow room to read instead of being cut off by the sill.
    base_y = sill_y - max(1, m(1))
    sh_w, sh_h = int(m(18) * scale), max(2, int(m(3) * scale))
    csh = pygame.Surface((sh_w, sh_h), pygame.SRCALPHA)
    pygame.draw.ellipse(csh, (12, 8, 6, 120), csh.get_rect())
    surf.blit(csh, (cx - sh_w // 2 + m(1.5), base_y - sh_h + m(1)))

    plate_y = _pedestal(surf, cx, base_y, scale)

    src, _lb = _group_thumb(group)
    iw, ih = src.get_size()
    # contain to the envelope, then give height priority to the awning hem so a
    # tall skin loses a pixel rather than tucking under the stripes.
    box = int(m(40) * scale)
    s = box / max(iw, ih)
    head_room = plate_y - (hem_y + m(1))
    if ih * s > head_room:
        s = head_room / ih
    img = pygame.transform.smoothscale(
        src, (max(1, int(iw * s)), max(1, int(ih * s))))
    img = _punch_contrast(img)
    r = img.get_rect(midbottom=(cx, plate_y))
    surf.blit(_rim_light(img), r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(_rim_light(img, color=(255, 224, 150), alpha=165),
              r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(img, r.topleft)

    surf.set_clip(prev_clip)


# =============================================================================
# HOOK-RAIL item — goods hung in open air from a brass rail. Held in reserve
# for a category that opens later; nothing renders it today.
# =============================================================================
TILT_HOOK_ITEM = 6.0
BRASS_HI = (206, 162, 74)
BRASS_LO = (96, 66, 24)


def _twist_rope(surf, p0, p1, thick, ticks=True):
    """A twisted two-strand rope: a WOOD_MID core with the lay caught on its
    upper-left flank and shaded on its lower-right, plus alternating cross
    ticks so the twist survives the downscale as texture rather than noise."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    if nx > 0:
        nx, ny = -nx, -ny
    off = max(1.0, thick / 2.0 - 0.5)
    pygame.draw.line(surf, WOOD_MID, p0, p1, thick)
    pygame.draw.line(surf, WOOD_HI, (x0 + nx * off, y0 + ny * off),
                     (x1 + nx * off, y1 + ny * off), 1)
    pygame.draw.line(surf, WOOD_EDGE, (x0 - nx * off, y0 - ny * off),
                     (x1 - nx * off, y1 - ny * off), 1)
    if not ticks:
        return
    step = max(2.0, thick * 1.6)
    n = int(L / step)
    for i in range(n):
        t = (i + 0.5) * step
        bx, by = x0 + ux * t, y0 + uy * t
        col = WOOD_EDGE if i % 2 else lerp_color(WOOD_HI, WOOD_MID, 0.35)
        pygame.draw.line(surf, col,
                         (bx + nx * off - ux * 0.8, by + ny * off - uy * 0.8),
                         (bx - nx * off + ux * 0.8, by - ny * off + uy * 0.8), 1)


def _hook_back_wall(inner, w, h):
    """Stall interior as a lit box: warm timber gloom in the sun-side upper
    left falling to near-black in the shaded lower right."""
    inner.blit(vgrad(w, h, 0, lerp_color(WOOD_MID, STALL_DARK, 0.55),
                     STALL_DARK), (0, 0))
    ramp = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        a = int(150 * (x / max(1, w - 1)) ** 1.15)
        pygame.draw.line(ramp, (*STALL_DARK, a), (x, 0), (x, h))
    inner.blit(ramp, (0, 0))


def _hook_sun_shaft(inner, w, h, die_x):
    """A soft slab of low sun entering the top-left of the opening and dying
    out before it reaches the goods — the item stays the brightest thing."""
    shaft = pygame.Surface((w, h), pygame.SRCALPHA)
    pts = [(w * 0.00, 0), (w * 0.30, 0), (w * 0.56, h * 0.78), (w * 0.24, h * 0.78)]
    cxp = sum(p[0] for p in pts) / 4.0
    cyp = sum(p[1] for p in pts) / 4.0
    layers = 5
    for k in range(layers):
        s = 1.0 - k * 0.07
        poly = [(cxp + (px - cxp) * s, cyp + (py - cyp) * s) for px, py in pts]
        lay = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(lay, (*GOLD_PALE, 40 // layers + 1), poly)
        shaft.blit(lay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    fade = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        t = min(1.0, max(0.0, (x - die_x * 0.45) / max(1.0, die_x * 0.55)))
        pygame.draw.line(fade, (255, 255, 255, int(255 * (1.0 - t) ** 1.2)),
                         (x, 0), (x, h))
    vf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        a = int(255 * (1.0 - (y / max(1, h - 1)) ** 1.5))
        pygame.draw.line(vf, (255, 255, 255, a), (0, y), (w, y))
    fade.blit(vf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    shaft.blit(fade, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    inner.blit(shaft, (0, 0))


def _hook_sill(inner, w, h, scale):
    """The counter board at the foot of the opening. Without it the stall has
    no floor for the goods to hang OVER, and a contact shadow thrown onto
    STALL_DARK is a shadow nobody can see."""
    sh_h = max(4, int(m(5) * scale))
    top = h - sh_h
    inner.blit(vgrad(w, sh_h, 0, lerp_color(WOOD_MID, WOOD_LO, 0.45),
                     WOOD_EDGE), (0, top))
    lip = pygame.Surface((w, 1), pygame.SRCALPHA)
    for x in range(w):
        lip.set_at((x, 0), (*WOOD_HI, int(190 * (1.0 - x / max(1, w - 1)) ** 1.2)))
    inner.blit(lip, (0, top))
    # blitted, not drawn: pygame.draw would WRITE alpha 120 into the wall and
    # punch a translucent slot through the stall interior
    ao = pygame.Surface((w, 1), pygame.SRCALPHA)
    ao.fill((0, 0, 0, 120))
    inner.blit(ao, (0, top - 1))
    return top


def _j_hook(inner, x, y, r, col, lit):
    """A bare J-hook hanging off the rail — near-silhouette, but given the same
    upper-left catch as everything else so it reads as an object in the gloom
    rather than a smudge."""
    tk = max(2, r // 2)
    pygame.draw.line(inner, col, (x, y), (x, y + r), tk)
    pygame.draw.arc(inner, col, (x - r, y + r - r // 2, r * 2, r * 2),
                    math.radians(200), math.radians(350), tk)
    pygame.draw.line(inner, lit, (x - tk // 2 - 1, y), (x - tk // 2 - 1, y + r), 1)


def _item_hook_rail(surf, ctx):
    """Goods in open air: a brass hook-rail lashed post-to-post, the hero
    hanging from a rope loop and gilt ring on the centre hook, and working
    stock (a coiled hank, a spare ring, two bare hooks) filling the flanks."""
    cx, deck_y = ctx["cx"], ctx["deck_y"]
    scale, group = ctx["scale"], ctx["group"]
    half_w, body_top = ctx["half_w"], ctx["body_top"]

    ol = cx - (half_w - m(8))
    ot = body_top + int(m(15) * scale)
    w = 2 * (half_w - m(8))
    h = (deck_y - m(8)) - ot
    inner = pygame.Surface((w, h), pygame.SRCALPHA)

    # ---- goods first, as geometry only: the lighting behind them keys off
    # where the hero actually lands.
    src, _lb = _group_thumb(group)
    sw, shh = src.get_size()
    box = int(m(40) * scale)
    s = box / max(sw, shh)
    img = pygame.transform.smoothscale(
        src, (max(1, int(sw * s)), max(1, int(shh * s))))
    img = _punch_contrast(img)
    img = pygame.transform.rotate(img, TILT_HOOK_ITEM)
    irect = img.get_rect()
    irect.centerx = w // 2
    irect.bottom = (deck_y - m(11)) - ot

    _hook_back_wall(inner, w, h)
    _hook_sun_shaft(inner, w, h, max(4, irect.left))
    sill_top = _hook_sill(inner, w, h, scale)

    rail_y = (body_top + int(m(16) * scale)) - ot
    rt = max(m(1.6), int(m(1.8) * scale))
    shs = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.line(shs, (0, 0, 0, 90), (0, rail_y + rt + 1),
                     (w, rail_y + rt + 2), max(1, rt - 1))
    inner.blit(shs, (0, 0))
    rail = pygame.Rect(0, rail_y, w, rt)
    inner.blit(vgrad(w, rt, 0, BRASS_HI, BRASS_LO), rail.topleft)
    # one light means the rail cannot be a uniform bright bar across the whole
    # opening — it burns brass at the sun end and sinks to gloom at the other,
    # which also keeps it from out-shouting the goods in a squint
    fall = pygame.Surface((w, rt), pygame.SRCALPHA)
    for x in range(w):
        a = int(130 * (x / max(1, w - 1)) ** 0.9)
        pygame.draw.line(fall, (*STALL_DARK, a), (x, 0), (x, rt))
    inner.blit(fall, rail.topleft)
    cat = pygame.Surface((w, 1), pygame.SRCALPHA)
    for x in range(w):
        a = int(150 * (1.0 - x / max(1, w - 1)) ** 1.6)
        cat.set_at((x, 0), (*GOLD_PALE, a))
    inner.blit(cat, (0, rail_y))

    # cord lashings at the post inner faces — the rail has to be tied to
    # something or it reads as a floating line
    lash = max(1, int(m(1.3) * scale))
    for side in (0, 1):
        for k in range(3):
            lx = (k * lash * 2 + lash) if side == 0 else (w - 1 - k * lash * 2 - lash)
            pygame.draw.line(inner, lerp_color(WOOD_MID, WOOD_LO, 0.3),
                             (lx, rail_y - lash - 1), (lx + 1, rail_y + rt + lash + 1),
                             lash)
            pygame.draw.line(inner, WOOD_EDGE, (lx + lash // 2, rail_y - lash - 1),
                             (lx + 1 + lash // 2, rail_y + rt + lash + 1), 1)

    # ---- flank stock. The sun side is bright enough to silhouette against,
    # the shade side is not — so the left flank goes DARKER than its wall and
    # the right flank goes lighter. Same tone family either way, both still
    # well under the hero.
    lit = lerp_color(WOOD_HI, WOOD_MID, 0.4)
    left_c = lerp_color(WOOD_EDGE, STALL_DARK, 0.25)
    right_c = lerp_color(WOOD_LO, WOOD_MID, 0.45)
    hx = w // 2 - int(m(32) * scale)
    rr = max(3, int(m(4.5) * scale))
    ring_w = max(1, int(m(1.2) * scale))
    pygame.draw.circle(inner, left_c, (hx, rail_y + rr + 1), rr, ring_w)
    pygame.draw.arc(inner, lit,
                    (hx - rr, rail_y + 1, rr * 2, rr * 2),
                    math.radians(60), math.radians(170), 1)
    hank_y = rail_y + rr * 2 + 2
    hank_r = max(4, int(m(6) * scale))
    for k in range(3):
        band = (hx - hank_r, hank_y + k * max(2, hank_r // 3),
                hank_r * 2, max(3, hank_r))
        pygame.draw.ellipse(inner, left_c, band, max(1, int(m(1.0) * scale)))
        pygame.draw.arc(inner, lit, band, math.radians(60), math.radians(160), 1)
    for dxs in (int(m(26) * scale), int(m(36) * scale)):
        _j_hook(inner, w // 2 + dxs, rail_y + rt, max(3, int(m(3.5) * scale)),
                right_c, lerp_color(WOOD_LO, WOOD_MID, 0.5))

    # ---- hero: capped glow only, so the gold bloom can never white out
    capped_glow(inner, irect.centerx, irect.centery + int(m(2) * scale),
                int(m(21) * scale), GOLD, 30, layers=9)

    # contact shadow on the sill, thrown down-right, sold as floating stock
    sh_s = pygame.Surface((w, h), pygame.SRCALPHA)
    ex = irect.centerx + int(m(3) * scale)
    ey = max(irect.bottom + max(2, int(m(1.5) * scale)), sill_top + 2)
    # widest/faintest ring FIRST: pygame.draw writes alpha rather than
    # compositing it, so an inner-out loop would leave only the faint pass
    for k in range(3, -1, -1):
        a = int(100 * (1 - k / 4.0))
        rx = int(irect.w * 0.40) + k * 2
        ry = max(2, int(m(1.6) * scale)) + k
        pygame.draw.ellipse(sh_s, (0, 0, 0, a), (ex - rx, ey - ry, rx * 2, ry * 2))
    inner.blit(sh_s, (0, 0))

    inner.blit(_rim_light(img), irect.topleft, special_flags=pygame.BLEND_ADD)
    inner.blit(img, irect.topleft)

    # ---- hanging hardware last: a square opening this shallow lets a tall
    # item's shoulder reach the rail, and a ring swallowed by the goods stops
    # reading as a hang at all — so the ring clasps in FRONT, on the centre
    # hook just left of the item's balance point, and the cord only shows
    # where the goods actually leave room for it.
    ax = irect.centerx - int(irect.w * 0.10)
    ay = irect.bottom
    col = max(0, min(img.get_width() - 1, ax - irect.left))
    for yy in range(irect.h):
        if img.get_at((col, yy))[3] > 24:
            ay = irect.top + yy
            break
    ring_r = max(3, int(m(3.2) * scale))
    ring_c = (ax, rail_y + rt // 2)
    cord_top = ring_c[1] + ring_r - 1
    if ay - cord_top > max(2, int(m(1.5) * scale)):
        _twist_rope(inner, (ring_c[0], cord_top), (ax, ay + 2),
                    max(m(1.5), int(m(1.6) * scale)), ticks=False)
    pygame.draw.circle(inner, (12, 8, 4), ring_c, ring_r + 1,
                       max(1, int(m(1.6) * scale)))
    pygame.draw.circle(inner, GOLD_PALE, ring_c, ring_r,
                       max(1, int(m(1.3) * scale)))
    pygame.draw.arc(inner, GOLD_DEEP,
                    (ring_c[0] - ring_r, ring_c[1] - ring_r, ring_r * 2, ring_r * 2),
                    math.radians(200), math.radians(340),
                    max(1, int(m(1.0) * scale)))
    surf.blit(inner, (ol, ot))


# =============================================================================
# COUNTER item — goods standing on a dressed market counter. Also held in
# reserve for a later category.
# =============================================================================
COUNTER_KRAFT = (150, 118, 78)
COUNTER_CLOTH = (176, 76, 66)


def _counter_geom(ctx):
    """One metric set the counter's parts are all authored against (hard walls
    = the m(8) posts + the deck lip).

    The ceiling is the AWNING HEM. This design was first drawn under a propped
    hatch board whose front edge capped the opening; that board is gone — every
    stall now carries the marquee sign — so the shadow band and the hero's
    headroom hang off the hem, which is the real top of the opening."""
    s = ctx["scale"]
    cx, deck_y, body_top = ctx["cx"], ctx["deck_y"], ctx["body_top"]
    return dict(
        s=s, cx=cx, deck_y=deck_y, body_top=body_top,
        in_half=ctx["half_w"] - m(8),
        sill_top=deck_y - m(8),
        y_ceil=body_top + int(m(15) * s),
        span_half=int(m(96) * s) // 2,
        item_base=deck_y - m(7),
        box=int(m(38) * s),
        dress_dx=int(m(32) * s),
    )


def _counter_eave_shadow(surf, g):
    """The awning throws its shadow DOWN-RIGHT onto the back wall — the cue
    that seats the lit counter below inside a real box rather than on a flat
    painted panel."""
    h = int(m(7) * g["s"])
    off = int(m(3) * g["s"])
    x0 = max(g["cx"] - g["in_half"], g["cx"] - g["span_half"] + off)
    x1 = min(g["cx"] + g["in_half"], g["cx"] + g["span_half"] + off)
    band = pygame.Surface((max(1, x1 - x0), h), pygame.SRCALPHA)
    for y in range(h):
        a = int(96 * (1 - y / h) ** 1.5)
        pygame.draw.line(band, (0, 0, 0, a), (0, y), (band.get_width(), y))
    surf.blit(band, (x0, g["y_ceil"]))


def _counter_sill(surf, g):
    """A full-width market counter across the deck lip: the plane the goods
    stand ON, so the item has a floor instead of floating in the opening."""
    x0 = g["cx"] - g["in_half"]
    w = g["in_half"] * 2
    top = g["sill_top"]
    h = (g["deck_y"] + m(2)) - top
    x1 = x0 + w - 1
    surf.blit(vgrad(w, h, 0, WOOD_HI, WOOD_LO), (x0, top))
    for k in range(1, 4):
        sy = top + h * k // 4
        pygame.draw.line(surf, lerp_color(WOOD_LO, WOOD_EDGE, 0.35),
                         (x0, sy), (x1, sy), max(1, m(0.7)))
    pygame.draw.line(surf, WOOD_EDGE, (x0, top + h - m(1)),
                     (x1, top + h - m(1)), max(1, m(1.4)))
    pygame.draw.line(surf, lerp_color(WOOD_HI, GOLD_PALE, 0.35),
                     (x0, top), (x1, top), max(1, m(1)))


def _counter_dressing(surf, g):
    """Market slack-filler for the wide sill: folded goods left, a price
    pennant + crate lip right. Deliberately capped below the hero's shoulder and
    knocked ~28% down in value — these read as DEPTH, never as competition."""
    s, top = g["s"], g["sill_top"]
    pad = m(20)
    lay = pygame.Surface((g["in_half"] * 2 + pad * 2, m(40)), pygame.SRCALPHA)
    ox, oy = g["cx"] - g["in_half"] - pad, top - m(30)

    def L(x, y):
        return (x - ox, y - oy)

    lx = g["cx"] - g["dress_dx"]
    bw, bh = int(m(15) * s), int(m(4.5) * s)
    tw, th = int(m(12) * s), int(m(4) * s)
    # authored a lane ABOVE their final value, because the whole cluster then
    # takes a flat 28% knock-down — pitched any darker they silhouette into the
    # unlit back wall and stop reading as goods at all.
    fold_lo = lerp_color(COUNTER_KRAFT, WOOD_HI, 0.30)

    def block(r, base):
        """Lit top-left edge, dark bottom-right edge — the one sun, and cheaper
        in pixels than a full keyline on forms this small."""
        lay.blit(vgrad(r.w, r.h, 0, lerp_color(base, WOOD_HI, 0.30), base), r)
        k = max(1, m(0.6))
        pygame.draw.line(lay, lerp_color(base, WOOD_HI, 0.70),
                         (r.x, r.y), (r.right - 1, r.y), k)
        pygame.draw.line(lay, WOOD_EDGE, (r.x, r.bottom - 1),
                         (r.right - 1, r.bottom - 1), k)
        pygame.draw.line(lay, WOOD_EDGE, (r.right - 1, r.y),
                         (r.right - 1, r.bottom - 1), k)

    for rw, rh, ry, base in ((bw, bh, top - bh, fold_lo),
                             (tw, th, top - bh - th, COUNTER_KRAFT)):
        block(pygame.Rect(*L(lx - rw // 2, ry), rw, rh), base)

    rx = g["cx"] + g["dress_dx"]
    cw, chh = int(m(16) * s), int(m(6) * s)
    cr = pygame.Rect(*L(rx - cw // 2, top - chh), cw, chh)
    block(cr, lerp_color(WOOD_MID, WOOD_HI, 0.20))
    pygame.draw.line(lay, WOOD_LO, (cr.x + m(1), cr.bottom - m(2)),
                     (cr.right - m(2), cr.y + m(1)), max(1, m(0.6)))

    pole_h = int(m(10) * s)
    px = rx - cw // 2 + int(m(2) * s)
    pygame.draw.line(lay, WOOD_EDGE, L(px, top - chh),
                     L(px, top - chh - pole_h), max(1, m(1.2)))
    fw, fh = int(m(9) * s), int(m(5) * s)
    ftop = top - chh - pole_h + int(m(1) * s)
    pygame.draw.polygon(lay, COUNTER_CLOTH,
                        [L(px, ftop), L(px + fw, ftop + fh // 2),
                         L(px, ftop + fh)])
    pygame.draw.polygon(lay, lerp_color(COUNTER_CLOTH, WOOD_EDGE, 0.45),
                        [L(px, ftop), L(px + fw, ftop + fh // 2),
                         L(px, ftop + fh)], max(1, m(0.7)))

    lay.fill((183, 183, 183, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(lay, (ox, oy))


def _counter_sun_shaft(surf, g):
    """ONE shaft, matching the one light: it enters at the opening's upper left
    and lands on the sill between the folded goods and the hero, so the gap
    that separates the dressing from the item is a lit gap, not an empty one."""
    s = g["s"]
    y0, y1 = g["y_ceil"], g["sill_top"]
    if y1 - y0 < 4:
        return
    x0a = g["cx"] - g["span_half"]
    x0b = x0a + int(m(8) * s)
    x1a = g["cx"] - int(m(21) * s)
    x1b = g["cx"] - int(m(14) * s)
    fe = max(2, m(3))
    xmin = min(x0a, x1a) - fe
    xmax = max(x0b, x1b) + fe
    h = y1 - y0
    # Each row is a flat core with a feathered edge either side, so it is drawn
    # as a handful of nested lines instead of pixel by pixel — same profile,
    # without a Python loop over every pixel of the beam.
    beam = pygame.Surface((xmax - xmin + 1, h), pygame.SRCALPHA)
    steps = max(2, int(2 * fe))
    for iy in range(h):
        t = iy / max(1, h - 1)
        a0 = 34.0 * (1.0 - t)
        if a0 <= 0:
            continue
        xa = x0a + (x1a - x0a) * t - fe
        xb = x0b + (x1b - x0b) * t + fe
        for j in range(steps, 0, -1):
            k = j / steps
            a = int(a0 * k)
            if a <= 0:
                continue
            inset = (1.0 - k) * 2 * fe
            lx, rx = xa + inset, xb - inset
            if rx <= lx:
                continue
            pygame.draw.line(beam, (*GOLD_PALE, a),
                             (int(lx - xmin), iy), (int(rx - xmin), iy))
    surf.blit(beam, (xmin, y0))

    pool_rx, pool_ry = int(m(5.5) * s), int(m(2) * s)
    pc = ((x1a + x1b) // 2, y1 + m(1))
    pool = pygame.Surface((pool_rx * 2 + 2, pool_ry * 2 + 2), pygame.SRCALPHA)
    for i in range(6, 0, -1):
        a = int(44 * (1 - (i - 1) / 6) ** 1.6)
        pygame.draw.ellipse(pool, (*GOLD_PALE, a),
                            (pool_rx - pool_rx * i // 6,
                             pool_ry - pool_ry * i // 6,
                             2 * pool_rx * i // 6, 2 * pool_ry * i // 6))
    surf.blit(pool, (pc[0] - pool_rx, pc[1] - pool_ry))


def _counter_plinth(surf, g, iw):
    """A 3px riser so the hero stands PROUD of the counter clutter rather than
    sharing its baseline."""
    s = g["s"]
    ph = m(3)
    pw = iw + int(m(7) * s)
    r = pygame.Rect(g["cx"] - pw // 2, g["item_base"], pw, ph + m(1))
    surf.blit(vgrad(r.w, r.h, 0, lerp_color(WOOD_MID, WOOD_HI, 0.25), WOOD_LO),
              r.topleft)
    pygame.draw.rect(surf, WOOD_EDGE, r, width=max(1, m(0.8)))


def _item_counter(surf, ctx):
    g = _counter_geom(ctx)
    _counter_eave_shadow(surf, g)
    _counter_sill(surf, g)
    _counter_dressing(surf, g)
    _counter_sun_shaft(surf, g)

    src, _lb = _group_thumb(ctx["group"])
    w, h = src.get_size()
    sc = g["box"] / max(w, h)
    # the awning owns the top of the opening; the hero is contained into what
    # is LEFT, never pushed under it.
    room = (g["item_base"] - g["y_ceil"]) - m(2)
    if h * sc > room:
        sc = room / h
    img = pygame.transform.smoothscale(
        src, (max(1, int(w * sc)), max(1, int(h * sc))))
    img = _punch_contrast(img)
    r = img.get_rect(midbottom=(g["cx"], g["item_base"]))

    _counter_plinth(surf, g, r.w)
    capped_glow(surf, r.centerx, r.centery, int(m(24) * g["s"]), GOLD, 30,
                layers=9)
    sh_off = m(3)
    cast = img.copy()
    cast.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    cast.set_alpha(130)
    surf.blit(cast, (r.x + sh_off, r.y + sh_off))
    surf.blit(_rim_light(img), r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(img, r.topleft)


# =============================================================================
# Registry.
# =============================================================================
# Every item presentation the stall-front design effort produced. Only three
# are on screen today; `hook_rail` and `counter` are kept whole and covered by
# tests/test_stall_fronts.py so they are still buildable when the shuttered
# categories (ANIMALS / SHOES / HATS / SHADES) open.
DESIGNS = {
    "sling": _item_sling,
    "lantern": _item_lantern,
    "pedestal": _item_pedestal,
    "hook_rail": _item_hook_rail,
    "counter": _item_counter,
}

# Which design each open category wears. Opening a stall is one line here;
# any group left out keeps the stock cabochon + name-board front in store_hub.
ITEM = {
    "parrot": "sling",
    "parcels": "lantern",
    "costume": "pedestal",
}


def draw_item(surf, ctx):
    DESIGNS[ITEM[ctx["group"]]](surf, ctx)
