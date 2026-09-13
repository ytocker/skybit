"""
Bespoke engraved center glyphs for the FAME — Flight Log achievement family
(GOLD tone). Procedural art only; these drop into
``game.achievement_icons._GLYPHS`` via the sibling render harness and are stamped
by the same engrave pipeline (dark inset pass down-right + lit body + up-left
sheen), so each glyph is authored with the single passed ``col`` and only routes
a saturated accent through ``_accent`` (none are needed here — Flight Log is pure
single-colour gold).

Four silhouette families keep the category readable at the ~22px glyph floor:

  * per-run pillars  — ARCHITECTURE that grows by count + structure
                       (1 post → 2-post gate → 3-post colonnade → triumphal arch).
  * score            — a CHEVRON climb whose rung-COUNT is the read (2 → 3).
  * day-cycle        — sun-on-horizon that gains identical MOON DISCS (1 → 3);
                       count is the read, no phase/crescent shapes.
  * lifetime pillars — a GLOBE that closes into a full flight-ORBIT.

Tier escalation for every family lives in ONE shared helper taking a ``tier``
arg, so the count/material climb is defined once and a glance reads the rank off
real motif growth rather than sub-pixel rank-pips.
"""
from __future__ import annotations

import math
import pygame

from game.achievement_icons import _GLYPH_SH, _accent


# ── shared rank-dressing accents (faint cherry-on-top, never the read) ────────
#
# The spec demotes L-marks to optional accents. They are drawn in the engraved
# inset-shadow tone so they sit UNDER the lit motif and never compete with the
# count/structure read that actually carries each tier.

def _rank_pips(surf, cx, baseline_y, r, col, n):
    # L1 — up to three small notch-dots tucked under the motif's foot.
    pr = max(2, int(r * 0.07))
    span = r * 0.30
    x0 = cx - span * (n - 1) / 2
    for i in range(n):
        pygame.draw.circle(surf, col, (int(x0 + span * i), int(baseline_y)), pr)


def _rank_wreath(surf, cx, baseline_y, r, col):
    # L2 — a short laurel-echo tick flanking each side of the foot.
    for sgn in (-1, 1):
        bx = cx + sgn * r * 0.66
        pygame.draw.line(surf, col, (int(bx), int(baseline_y)),
                         (int(bx + sgn * r * 0.18), int(baseline_y - r * 0.18)),
                         max(2, int(r * 0.07)))
        pygame.draw.line(surf, col, (int(bx), int(baseline_y)),
                         (int(bx + sgn * r * 0.20), int(baseline_y + r * 0.02)),
                         max(2, int(r * 0.07)))


def _rank_crownlet(surf, cx, top_y, r, col):
    # L4 — a 3-point engraved crownlet seated on top of the motif's apex.
    w = r * 0.50
    h = r * 0.26
    base_y = top_y
    pts = [
        (cx - w, base_y),
        (cx - w, base_y - h * 0.5),
        (cx - w * 0.5, base_y - h * 0.1),
        (cx, base_y - h),
        (cx + w * 0.5, base_y - h * 0.1),
        (cx + w, base_y - h * 0.5),
        (cx + w, base_y),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


# ═══════════════════════════════════════════════════════════════════════════
# Family 1 — per-run pillars: architecture grows by COUNT + STRUCTURE.
#   tier 0 first_flight  : ONE squat pillar + a parcel at its foot.       L0
#   tier 1 pillar_25     : TWO pillars (a gateway), parcel gone.          L1 pips
#   tier 2 pillar_50     : THREE pillars stepping up (a colonnade).       L2 wreath
#   tier 3 pillar_100    : a triumphal ARCH spanning two posts.           L4 crown
# ═══════════════════════════════════════════════════════════════════════════

def _draw_one_pillar(surf, cx, top, h, shaft_w, cap_w, cap_h, col):
    # A single sandstone post: flared capital + base block + plain tapered shaft
    # (flutes are sub-pixel at row size, so the shaft is left clean per the spec
    # Fallback).
    pygame.draw.rect(surf, col, (int(cx - shaft_w / 2), int(top + cap_h),
                                 int(shaft_w), int(h - cap_h * 2)))
    for yy in (top, top + h - cap_h):
        pygame.draw.rect(surf, col, (int(cx - cap_w / 2), int(yy),
                                     int(cap_w), int(cap_h)),
                         border_radius=max(1, int(cap_h * 0.35)))


def _glyph_pillar_tier(surf, cx, cy, r, col, tier):
    # Shared "pillar gateway" motif. The number of posts and the resolution into
    # a monument IS the escalation; rank marks ride underneath only.
    base_y = cy + r * 0.92          # common foot line for all tiers

    if tier == 0:
        # First Delivery — one squat post with a little parcel at its foot.
        h = r * 1.20
        top = base_y - h
        sw = max(3, int(r * 0.34))
        cw = int(sw * 1.7)
        ch = max(2, int(r * 0.16))
        _draw_one_pillar(surf, cx - r * 0.30, top, h, sw, cw, ch, col)
        # parcel/letter: a small enveloped square with a corner-fold, at the foot.
        bx, by = cx + r * 0.46, base_y - r * 0.30
        bs = r * 0.42
        pygame.draw.rect(surf, col, (int(bx - bs / 2), int(by - bs / 2),
                                     int(bs), int(bs)),
                         border_radius=max(1, int(bs * 0.12)))
        # the corner fold (cross-tie of the parcel) in the inset tone so it reads
        # as an indent on the parcel face.
        pygame.draw.line(surf, _GLYPH_SH, (int(bx - bs / 2), int(by - bs * 0.1)),
                         (int(bx + bs / 2), int(by - bs * 0.1)), max(2, int(r * 0.07)))
        pygame.draw.line(surf, _GLYPH_SH, (int(bx), int(by - bs / 2)),
                         (int(bx), int(by + bs / 2)), max(2, int(r * 0.07)))
        return

    if tier == 1:
        # Courier in Training — two equal posts framing a gateway.
        h = r * 1.34
        top = base_y - h
        sw = max(3, int(r * 0.30))
        cw = int(sw * 1.7)
        ch = max(2, int(r * 0.15))
        for sgn in (-1, 1):
            _draw_one_pillar(surf, cx + sgn * r * 0.50, top, h, sw, cw, ch, col)
        # a lintel bridging the two caps so the pair reads as a GATE, not a tally.
        pygame.draw.rect(surf, col, (int(cx - r * 0.74), int(top - r * 0.04),
                                     int(r * 1.48), max(2, int(r * 0.16))),
                         border_radius=max(1, int(r * 0.05)))
        _rank_pips(surf, cx, base_y + r * 0.14, r, _GLYPH_SH, 2)
        return

    if tier == 2:
        # Route Veteran — three posts stepping up in height (a colonnade
        # receding to the right reads as DEPTH). Bold flared capitals PLUS a
        # shared stepped entablature lintel riding all three caps, so the trio
        # reads as a portico of PILLARS, never a flat-topped equalizer bar-chart.
        sw = max(3, int(r * 0.26))
        cw = int(sw * 2.0)
        ch = max(3, int(r * 0.18))
        cols = (-0.62, 0.0, 0.62)
        heights = (1.02, 1.28, 1.54)
        tops = []
        for fx, fh in zip(cols, heights):
            h = r * fh
            top = base_y - h
            tops.append((cx + fx * r, top))
            _draw_one_pillar(surf, cx + fx * r, top, h, sw, cw, ch, col)
        # entablature: a sloped lintel band bridging the shortest cap (left) up
        # to the tallest (right), tying the three into one colonnade roof.
        (rx, ry) = tops[0]          # shortest (left)
        (lx, ly) = tops[-1]         # tallest (right)
        lh = max(2, int(r * 0.12))
        lintel = [
            (int(rx - cw * 0.55), int(ry - ch * 0.10)),
            (int(lx + cw * 0.55), int(ly - ch * 0.10)),
            (int(lx + cw * 0.55), int(ly - ch * 0.10 - lh)),
            (int(rx - cw * 0.55), int(ry - ch * 0.10 - lh)),
        ]
        pygame.draw.polygon(surf, col, lintel)
        _rank_wreath(surf, cx, base_y + r * 0.14, r, _GLYPH_SH)
        return

    # tier 3 — Centurion: a triumphal MONUMENT that out-masses the gateway. Two
    # heavy piers carry a thick arch, capped by a bold stepped keystone block —
    # the colonnade resolved into a single mass (NOT a thin horseshoe).
    sw = max(5, int(r * 0.36))      # heavier piers than the gateway's posts
    span = r * 0.52                 # half-distance between the two pier centres
    leg_top = cy - r * 0.06
    leg_h = base_y - leg_top
    for sgn in (-1, 1):
        px = cx + sgn * span
        pygame.draw.rect(surf, col, (int(px - sw / 2), int(leg_top),
                                     int(sw), int(leg_h)))
        # impost block where the arch springs, + a base block — solid masonry.
        pygame.draw.rect(surf, col, (int(px - sw * 0.78), int(leg_top - r * 0.04),
                                     int(sw * 1.56), max(2, int(r * 0.13))),
                         border_radius=max(1, int(r * 0.04)))
        pygame.draw.rect(surf, col, (int(px - sw * 0.85), int(base_y - r * 0.16),
                                     int(sw * 1.7), max(2, int(r * 0.16))),
                         border_radius=max(1, int(r * 0.05)))
    # the arch: a fat semicircular band springing from the two pier tops.
    arc_r = span + sw / 2
    rect = pygame.Rect(int(cx - arc_r), int(leg_top - arc_r),
                       int(arc_r * 2), int(arc_r * 2))
    pygame.draw.arc(surf, col, rect, math.radians(0), math.radians(180),
                    max(5, int(sw * 1.05)))
    # Bold STEPPED triumphal keystone crowning the arch: a wide lower plinth, a
    # taller narrower attic block on top — the monument's apex mass, replacing
    # the sub-pixel crownlet so the "100" rung reads as a built memorial.
    apex_y = leg_top - arc_r
    plinth_w, plinth_h = r * 0.62, r * 0.20
    attic_w, attic_h = r * 0.40, r * 0.30
    pygame.draw.rect(surf, col, (int(cx - plinth_w / 2), int(apex_y - plinth_h),
                                 int(plinth_w), int(plinth_h)),
                     border_radius=max(1, int(r * 0.04)))
    pygame.draw.rect(surf, col, (int(cx - attic_w / 2), int(apex_y - plinth_h - attic_h),
                                 int(attic_w), int(attic_h)),
                     border_radius=max(1, int(r * 0.04)))
    # a small crownlet seated on the attic — the L4 cherry-on-top.
    _rank_crownlet(surf, cx, apex_y - plinth_h - attic_h, r, col)


def _glyph_first_flight(surf, cx, cy, r, col):
    _glyph_pillar_tier(surf, cx, cy, r, col, 0)


def _glyph_pillar_25(surf, cx, cy, r, col):
    _glyph_pillar_tier(surf, cx, cy, r, col, 1)


def _glyph_pillar_50(surf, cx, cy, r, col):
    _glyph_pillar_tier(surf, cx, cy, r, col, 2)


def _glyph_pillar_100(surf, cx, cy, r, col):
    _glyph_pillar_tier(surf, cx, cy, r, col, 3)


# ═══════════════════════════════════════════════════════════════════════════
# Family 2 — score: a chevron climb. The rung-COUNT carries the tier (2 → 3);
# score_500 alone adds a wing-pip. NO ray-halo (it muds into the chevrons).
#   tier 0 score_100 : 2 chevrons + three tally ticks beneath.
#   tier 1 score_500 : 3 chevrons rising higher + a wing-pip on the top one.
# ═══════════════════════════════════════════════════════════════════════════

def _draw_chevron(surf, cx, apex_y, half_w, thick, col):
    # An up-pointing chevron (a thick fat-bottomed ">" rotated to point up).
    drop = half_w * 0.62
    outer = [
        (cx - half_w, apex_y + drop),
        (cx, apex_y),
        (cx + half_w, apex_y + drop),
        (cx + half_w - thick * 0.5, apex_y + drop + thick * 0.7),
        (cx, apex_y + thick),
        (cx - half_w + thick * 0.5, apex_y + drop + thick * 0.7),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in outer])


def _glyph_score_tier(surf, cx, cy, r, col, tier):
    n = 2 if tier == 0 else 3
    half_w = r * 0.66
    thick = max(3, int(r * 0.22))
    step = r * 0.46                 # vertical spacing between stacked chevrons
    # Stack rises up-right: each higher chevron is nudged right so the climb
    # reads as a delivery-flight ascent, not a static stack.
    # score_500 nudges the whole stack down so its added wing flag has clear air
    # above the apex.
    top_apex = cy - (n - 1) * step / 2 - r * 0.18 + (r * 0.14 if tier else 0)
    for i in range(n):
        ax = cx + (i - (n - 1) / 2) * r * 0.16
        ay = top_apex + (n - 1 - i) * step
        _draw_chevron(surf, ax, ay, half_w, thick, col)

    if tier == 0:
        # three short tally ticks beneath — the "triple digits" nod.
        ty = cy + r * 0.82
        for dx in (-0.26, 0.0, 0.26):
            x = cx + dx * r
            pygame.draw.line(surf, col, (int(x), int(ty)),
                             (int(x), int(ty + r * 0.22)), max(2, int(r * 0.10)))
    else:
        # a bold 2-lobe WING FLAG riding the apex above the top chevron — the
        # only added flourish (NO ray halo, which muds into the chevrons). Drawn
        # big with a clear convex leading edge and a 2-lobe trailing scallop so
        # it never reads as a stray spur / fourth chevron at 44px.
        wcx = cx
        wy = top_apex - r * 0.40
        wing = [
            (wcx - r * 0.52, wy + r * 0.20),    # shoulder
            (wcx - r * 0.18, wy - r * 0.18),    # leading-edge camber
            (wcx + r * 0.30, wy - r * 0.40),    # leading edge to tip
            (wcx + r * 0.58, wy - r * 0.42),    # tip
            (wcx + r * 0.28, wy - r * 0.10),    # trailing lobe 1
            (wcx + r * 0.06, wy + r * 0.06),    # trailing lobe 2
            (wcx - r * 0.22, wy + r * 0.18),    # inner trailing
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in wing])


def _glyph_score_100(surf, cx, cy, r, col):
    _glyph_score_tier(surf, cx, cy, r, col, 0)


def _glyph_score_500(surf, cx, cy, r, col):
    _glyph_score_tier(surf, cx, cy, r, col, 1)


# ═══════════════════════════════════════════════════════════════════════════
# Family 3 — day-cycle: a half-sun over a horizon that acquires identical moon
# discs. The disc-COUNT is the night-count and the read (1 → 3); no phase
# shapes (sub-pixel at row size).
#   tier 0 day_complete : half-sun + 1 moon-disc, faint orbit arc.     L0
#   tier 1 day_three    : half-sun + 3 identical moon-discs in a row.  L2 wreath
# ═══════════════════════════════════════════════════════════════════════════

def _draw_half_sun(surf, sun_cx, horizon_y, sun_r, r, col):
    # A clean half-disc sitting ON the horizon (drawn as a filled polygon fan of
    # the upper semicircle so it's a solid dome with a flat base), ringed by a
    # gap then distinct radiating rays so it reads as a SUN, not a hill.
    fan = [(sun_cx + sun_r, horizon_y)]
    for k in range(13):
        a = math.pi * k / 12          # 0..pi sweeping the upper half
        fan.append((sun_cx + math.cos(a) * sun_r, horizon_y - math.sin(a) * sun_r))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in fan])
    for k in range(5):
        a = math.pi * (k + 0.5) / 5    # five rays fanning over the upper half
        x1 = sun_cx + math.cos(a) * sun_r * 1.28
        y1 = horizon_y - math.sin(a) * sun_r * 1.28
        x2 = sun_cx + math.cos(a) * sun_r * 1.66
        y2 = horizon_y - math.sin(a) * sun_r * 1.66
        pygame.draw.line(surf, col, (int(x1), int(y1)), (int(x2), int(y2)),
                         max(2, int(r * 0.09)))


def _glyph_day_tier(surf, cx, cy, r, col, tier):
    horizon_y = cy + r * 0.52
    sun_r = r * 0.42
    sun_cx = cx - r * 0.30
    _draw_half_sun(surf, sun_cx, horizon_y, sun_r, r, col)
    # horizon line.
    pygame.draw.line(surf, col, (int(cx - r * 0.94), int(horizon_y)),
                     (int(cx + r * 0.94), int(horizon_y)), max(2, int(r * 0.11)))

    moon_r = r * 0.22
    if tier == 0:
        # one plain moon-disc up-right of the sun, framed by a faint orbit arc
        # (one day → night). The moon carries an inset bite of shadow on its
        # lower-right so it reads as a celestial disc, not just a dot.
        mx, my = cx + r * 0.52, cy - r * 0.42
        pygame.draw.circle(surf, col, (int(mx), int(my)), int(moon_r))
        pygame.draw.circle(surf, _GLYPH_SH,
                           (int(mx + moon_r * 0.42), int(my + moon_r * 0.30)),
                           int(moon_r * 0.62))
        orb = pygame.Rect(int(mx - r * 0.82), int(my - r * 0.82),
                          int(r * 1.64), int(r * 1.64))
        pygame.draw.arc(surf, col, orb, math.radians(-20), math.radians(150),
                        max(2, int(r * 0.07)))
    else:
        # three identical moon-discs on an EVEN rising-then-setting arc over the
        # sun — the deliberate COUNT-of-3 is the read. The arc is drawn first as
        # a faint orbit, then the discs sit at symmetric, well-separated angles
        # on it (left-low, centre-high, right-low) so it never reads as scatter.
        m3 = r * 0.20
        arc_cx, arc_cy = cx, cy + r * 0.46
        arc_r = r * 0.92
        orb = pygame.Rect(int(arc_cx - arc_r), int(arc_cy - arc_r),
                          int(arc_r * 2), int(arc_r * 2))
        pygame.draw.arc(surf, col, orb, math.radians(34), math.radians(146),
                        max(2, int(r * 0.07)))
        for ang in (140, 90, 40):       # symmetric about the apex, evenly spaced
            a = math.radians(ang)
            mx = arc_cx + math.cos(a) * arc_r
            my = arc_cy - math.sin(a) * arc_r
            pygame.draw.circle(surf, col, (int(mx), int(my)), int(m3))
        _rank_wreath(surf, cx, horizon_y + r * 0.34, r, _GLYPH_SH)


def _glyph_day_complete(surf, cx, cy, r, col):
    _glyph_day_tier(surf, cx, cy, r, col, 0)


def _glyph_day_three(surf, cx, cy, r, col):
    _glyph_day_tier(surf, cx, cy, r, col, 1)


# ═══════════════════════════════════════════════════════════════════════════
# Family 4 — lifetime pillars: a globe that closes into a full flight-orbit.
# Distinct from the per-run architecture: this is all-time DISTANCE.
#   tier 0 frequent_flyer : winged globe (circle + 1 lat + 1 long arc).  L2 wreath
#   tier 1 globetrotter   : globe wrapped by a full dashed orbit ring +
#                           a parrot-pip on the orbit.                    L4 crown
# ═══════════════════════════════════════════════════════════════════════════

def _draw_globe(surf, cx, cy, gr, col):
    # Circle + ONE vertical meridian + ONE horizontal equator arc (the spec
    # Fallback — extra longitude lines crowd at row size).
    lw = max(2, int(gr * 0.12))
    pygame.draw.circle(surf, col, (int(cx), int(cy)), int(gr), lw)
    # equator: a shallow horizontal ellipse arc across the middle.
    eq = pygame.Rect(int(cx - gr), int(cy - gr * 0.34),
                     int(gr * 2), int(gr * 0.68))
    pygame.draw.ellipse(surf, col, eq, lw)
    # meridian: a tall narrow ellipse for the front-facing longitude.
    mer = pygame.Rect(int(cx - gr * 0.40), int(cy - gr),
                      int(gr * 0.80), int(gr * 2))
    pygame.draw.ellipse(surf, col, mer, lw)


def _glyph_lifetime_tier(surf, cx, cy, r, col, tier):
    gr = r * 0.52
    gcx, gcy = cx, cy + (0 if tier else -r * 0.04)

    if tier == 0:
        _draw_globe(surf, gcx, gcy, gr, col)
        # a tiny wing-tick riding the globe's upper-right shoulder — "flyer".
        wx, wy = gcx + gr * 0.78, gcy - gr * 0.72
        wing = [
            (wx - r * 0.06, wy + r * 0.16),
            (wx + r * 0.40, wy - r * 0.16),
            (wx + r * 0.16, wy + r * 0.04),
            (wx + r * 0.34, wy + r * 0.10),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in wing])
        _rank_wreath(surf, cx, cy + r * 0.96, r, _GLYPH_SH)
        return

    # tier 1 — the route closes into a full lap: ONE bold dashed flight-orbit
    # ellipse clearly OUTSIDE the globe, crowned. No parrot pip (it mushed into
    # the orbit at row size); the closed dashed ring alone says "a full lap of
    # the world", and the crown is the tier topper.
    gr2 = r * 0.46                  # globe shrunk so the orbit clears it cleanly
    _draw_globe(surf, gcx, gcy, gr2, col)
    orb_rx, orb_ry = r * 0.94, r * 0.52
    tilt = math.radians(-20)
    n = 16
    dash_w = max(3, int(r * 0.12))
    for i in range(n):
        if i % 2:                    # every other segment skipped → dashed look
            continue
        a0 = i / n * math.tau
        a1 = (i + 1) / n * math.tau
        seg = []
        for a in (a0, a1):
            ex = math.cos(a) * orb_rx
            ey = math.sin(a) * orb_ry
            rx = ex * math.cos(tilt) - ey * math.sin(tilt)
            ry = ex * math.sin(tilt) + ey * math.cos(tilt)
            seg.append((int(gcx + rx), int(gcy + ry)))
        # the front (lower) arc lit, the rear (upper) arc in the inset tone, so
        # the dashed ring reads as wrapping AROUND the globe.
        a_mid = (a0 + a1) / 2
        front = math.sin(a_mid) > 0
        pygame.draw.line(surf, col if front else _GLYPH_SH, seg[0], seg[1], dash_w)
    _rank_crownlet(surf, cx, gcy - gr2 - r * 0.30, r, col)


def _glyph_frequent_flyer(surf, cx, cy, r, col):
    _glyph_lifetime_tier(surf, cx, cy, r, col, 0)


def _glyph_globetrotter(surf, cx, cy, r, col):
    _glyph_lifetime_tier(surf, cx, cy, r, col, 1)


GLYPHS = {
    "first_flight": _glyph_first_flight,
    "pillar_25": _glyph_pillar_25,
    "pillar_50": _glyph_pillar_50,
    "pillar_100": _glyph_pillar_100,
    "score_100": _glyph_score_100,
    "score_500": _glyph_score_500,
    "day_complete": _glyph_day_complete,
    "day_three": _glyph_day_three,
    "frequent_flyer": _glyph_frequent_flyer,
    "globetrotter": _glyph_globetrotter,
}
