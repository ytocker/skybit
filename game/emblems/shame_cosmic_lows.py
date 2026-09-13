"""Bespoke engraved center glyphs for the SHAME — Cosmic Jokes + Lifetime Lows
(Hall of SHAME) medallions, rendered TARNISHED (cracked-pewter anti-trophy).

Seven anti-trophy glyphs in the single-colour engrave idiom of
``game.achievement_icons``: each ``_glyph_<id>(surf, cx, cy, r, col)`` lays BOLD
filled shapes in the passed ``col`` only — the builder strokes a down-right inset
shadow + up-left sheen for the struck-relief look, so a glyph hard-codes no fills
of its own. Recessed sockets/eyes use the engraved-shadow tone ``_SH``; the lone
two-tone prop (the magnet pole-tips) routes through ``ai._accent`` so it stays
bronze until the medal is earned. Authored to the ~44px legibility floor:
nothing thinner than ~2px, and each id resolves to ONE decisive silhouette that
puts the JOKE in the shape.

The tricky trio is drawn apart on purpose: ``groundhog_day`` wraps the repeat
loop around a rectangular PILLAR, ``same_time_tomorrow`` wraps it around a round
CLOCK, and ``three_am`` is a clock with a MOON and NO loop — three unmistakable
silhouettes. ``lightning_magnet`` shows a magnet catching MANY bolts (poles UP),
the mirror of the coin-pulling ``magnet_life`` (poles down).

WRITE-ONLY module: imports ``game`` read-only and never mutates it; the render
harness merges ``GLYPHS`` into a private copy of the badge glyph table.
"""
from __future__ import annotations

import math

import pygame

import game.achievement_icons as ai

# Reuse the live module's engraved-shadow tone so the dark sockets/recesses in
# these glyphs match the cast-shadow pass the builder stamps around them.
_SH = ai._GLYPH_SH


def _loop_arrow(surf, cx, cy, rad, col, w):
    # A single circular repeat/recycle arrow leaving a gap at the lower-right and
    # chasing its own tail — the shared "stuck in a loop" cue. Wrapped around a
    # pillar (groundhog) or a clock (same_time), the enclosed object is what tells
    # the two apart; the loop itself is deliberately identical.
    rect = pygame.Rect(cx - rad, cy - rad, rad * 2, rad * 2)
    a_start = math.radians(-32)
    a_stop = math.radians(250)
    pygame.draw.arc(surf, col, rect, a_start, a_stop, w)
    # Arrowhead at the visual stop end. pygame arcs run CCW in math angles while
    # the surface y is flipped, so place points with y negated and aim the head
    # along the direction of travel (toward a slightly larger angle).
    ex = cx + rad * math.cos(a_stop)
    ey = cy - rad * math.sin(a_stop)
    a_prev = a_stop - math.radians(20)
    px = cx + rad * math.cos(a_prev)
    py = cy - rad * math.sin(a_prev)
    dx, dy = ex - px, ey - py
    dl = math.hypot(dx, dy) or 1.0
    dx, dy = dx / dl, dy / dl
    # Fat barbs — the arrowhead is the ONLY "repeat" cue, so it must survive 44px.
    hl = rad * 0.72
    bw = w + max(1, w // 2)
    for sgn in (-1, 1):
        bx = ex - dx * hl + sgn * (-dy) * hl * 0.72
        by = ey - dy * hl + sgn * dx * hl * 0.72
        pygame.draw.line(surf, col, (int(ex), int(ey)), (int(bx), int(by)), bw)


def _pillar(surf, cx, cy, r, col, scale=1.0):
    # A single sandstone pillar — a CHUNKY rectilinear block (fat shaft + bold
    # flared capital + base slabs). Kept as square-cornered and rectangular as
    # possible so it can never read as the round clock inside same_time's loop —
    # pillar-vs-clock is the only thing separating those two glyphs.
    shaft_w = max(6, int(r * 0.42 * scale))
    cap_w = int(shaft_w * 1.7)
    h = int(r * 1.10 * scale)
    top = cy - h // 2
    cap_h = max(4, int(r * 0.20 * scale))
    pygame.draw.rect(surf, col, (cx - shaft_w // 2, top + cap_h,
                                 shaft_w, h - cap_h * 2))
    for yy in (top, cy + h // 2 - cap_h):            # capital + base slabs
        pygame.draw.rect(surf, col, (cx - cap_w // 2, yy, cap_w, cap_h))


def _clock_face(surf, cx, cy, rr, col, w):
    # Bare clock dial: a bold ring, four cardinal ticks, and a hub. Hands are the
    # caller's job so three_am / same_time can pose them differently.
    pygame.draw.circle(surf, col, (cx, cy), rr, w)
    for i in range(4):
        a = i * math.pi / 2
        x1 = cx + int(math.cos(a) * rr * 0.74)
        y1 = cy + int(math.sin(a) * rr * 0.74)
        x2 = cx + int(math.cos(a) * rr * 0.94)
        y2 = cy + int(math.sin(a) * rr * 0.94)
        pygame.draw.line(surf, col, (x1, y1), (x2, y2), max(2, w - 1))
    pygame.draw.circle(surf, col, (cx, cy), max(3, int(rr * 0.14)))


def _glyph_ninety_nine(surf, cx, cy, r, col):
    # A circular fill-gauge nearly complete, with one ~50° CHUNK missing at the
    # upper-right (1–2 o'clock) and a compact down-chevron tucked in that gap at
    # the rim — "almost full, one chunk left, and dropping." The wedge sits off
    # the vertical axis and nothing pierces the hub, so it cannot read as a
    # power-button. No numerals; the missing chunk IS the 99.
    rad = int(r * 0.66)
    w = max(5, int(r * 0.28))
    rect = pygame.Rect(cx - rad, cy - rad, rad * 2, rad * 2)
    # Fill arc sweeping from just past the gap (math ~35°) CCW nearly all the way
    # round to just before it (math ~85°), leaving a wide ~50° wedge open at the
    # 1–2 o'clock rim.
    pygame.draw.arc(surf, col, rect, math.radians(35), math.radians(85 + 360), w)
    # Compact down-chevron seated INSIDE the gap on the rim — the notch that fell
    # short. Centred on the gap's bearing (~60° up-right); it never crosses the
    # vertical axis or reaches the hub, so no power-button read.
    ga = math.radians(60)
    gx = cx + int(math.cos(ga) * rad)
    gy = cy - int(math.sin(ga) * rad)
    cw = max(4, int(r * 0.16))
    ch = int(r * 0.24)
    pygame.draw.lines(surf, col, False, [
        (gx - ch, gy - int(ch * 0.45)),
        (gx, gy + int(ch * 0.75)),
        (gx + ch, gy - int(ch * 0.45)),
    ], cw)


def _glyph_groundhog_day(surf, cx, cy, r, col):
    # A repeat/loop arrow wound around a single sandstone PILLAR — stuck reliving
    # the same pillar. The enclosed rectangular pillar is what sets this apart
    # from same_time_tomorrow (whose loop rings a round clock).
    _pillar(surf, cx, cy, r, col, scale=0.94)
    _loop_arrow(surf, cx, cy, int(r * 0.80), col, max(4, int(r * 0.16)))


def _glyph_stat_impossible(surf, cx, cy, r, col):
    # A SYMMETRIC bell curve sitting on a bold baseline, with a lone outlier spike
    # stranded off to the right — clearly TALLER than the hump peak and detached,
    # capped by a bold dot ("off the chart"). The one-in-a-million all-prime run;
    # the isolated over-tall spike is the whole read.
    base_y = cy + int(r * 0.66)
    peak = cx - int(r * 0.24)                 # bell centred left-of-middle
    half = int(r * 0.60)                      # symmetric half-width
    left = peak - half
    right = peak + half
    # baseline axis, run out under the outlier so the spike reads as "on the chart"
    pygame.draw.line(surf, col, (left - int(r * 0.06), base_y),
                     (cx + int(r * 0.98), base_y), max(3, int(r * 0.12)))
    # Gaussian hump as a filled polygon, symmetric about `peak`.
    hump_h = r * 0.78
    pts = [(left, base_y)]
    span = right - left
    for i in range(1, 21):
        t = i / 21
        x = left + int(t * span)
        u = (x - peak) / (r * 0.34)
        y = base_y - int(math.exp(-u * u) * hump_h)
        pts.append((x, y))
    pts.append((right, base_y))
    pygame.draw.polygon(surf, col, pts)
    # Lone outlier: a spike far to the right, taller than the hump and clearly
    # detached, capped with a bold dot — the improbable event off the chart.
    ox = cx + int(r * 0.74)
    spike_top = base_y - int(hump_h + r * 0.36)
    pygame.draw.line(surf, col, (ox, base_y), (ox, spike_top), max(4, int(r * 0.13)))
    pygame.draw.circle(surf, col, (ox, spike_top - int(r * 0.06)), max(5, int(r * 0.17)))


def _glyph_three_am(surf, cx, cy, r, col):
    # A clock reading 3 o'clock with a crescent moon tucked at its shoulder and NO
    # loop — the "it is 3 a.m., go to bed" gag. Short hour hand out to 3, long
    # minute hand up to 12; the moon is what separates it from same_time_tomorrow.
    ccx = cx - int(r * 0.14)
    ccy = cy + int(r * 0.10)
    rr = int(r * 0.60)
    w = max(3, int(r * 0.11))
    _clock_face(surf, ccx, ccy, rr, col, w)
    hw = max(3, int(r * 0.10))
    # hour hand -> 3 o'clock (right), short
    pygame.draw.line(surf, col, (ccx, ccy),
                     (ccx + int(rr * 0.62), ccy), hw)
    # minute hand -> 12 (up), long
    pygame.draw.line(surf, col, (ccx, ccy),
                     (ccx, ccy - int(rr * 0.88)), hw)
    # Crescent moon at the upper-right shoulder: a disc with a bite carved out by
    # a second disc in the shadow tone — a clean waning crescent.
    mx = cx + int(r * 0.62)
    my = cy - int(r * 0.56)
    mr = int(r * 0.34)
    pygame.draw.circle(surf, col, (mx, my), mr)
    pygame.draw.circle(surf, _SH, (mx + int(mr * 0.55), my - int(mr * 0.30)),
                       int(mr * 0.92))


def _glyph_same_time_tomorrow(surf, cx, cy, r, col):
    # A repeat/loop arrow wound around a round CLOCK — déjà-vu of the exact same
    # clock-minute on two days. Same loop as groundhog, but here it rings a clock
    # dial (not a pillar), and there is no moon (unlike three_am).
    # Shrunk dial pushed well inside a wide-radius loop so the two rings never
    # fuse into a double-ring blob (the biggest confusion risk vs groundhog).
    rr = int(r * 0.36)
    w = max(3, int(r * 0.10))
    _clock_face(surf, cx, cy, rr, col, w)
    hw = max(3, int(r * 0.10))
    # generic pose (~10:10) so the hands don't mimic three_am's 3 o'clock.
    pygame.draw.line(surf, col, (cx, cy),
                     (cx - int(rr * 0.56), cy - int(rr * 0.44)), hw)
    pygame.draw.line(surf, col, (cx, cy),
                     (cx + int(rr * 0.30), cy - int(rr * 0.68)), hw)
    _loop_arrow(surf, cx, cy, int(r * 0.90), col, max(4, int(r * 0.15)))


def _glyph_snake_bit(surf, cx, cy, r, col):
    # A reared COBRA about to strike: a chunky coil mass at the bottom, a short
    # thick S-neck rising out of it, and a clearly enlarged triangular WEDGE head
    # at the top with a forked V-flick tongue. The reared, wedge-headed silhouette
    # reads unmistakably as a snake (never a squiggle, bottle or skull).
    # Chunky coil at the base — a fat body ring the snake is coiled into.
    coil_cx = cx + int(r * 0.06)
    coil_cy = cy + int(r * 0.50)
    coil_r = int(r * 0.40)
    pygame.draw.circle(surf, col, (coil_cx, coil_cy), coil_r, max(6, int(r * 0.22)))
    # Short S-neck (~1.25 waves) rising from the coil to the head, kept thick so
    # it reads reared-to-strike rather than a thin thread.
    n = 16
    start = (coil_cx + int(r * 0.02), coil_cy - coil_r)
    head_base = (cx - int(r * 0.06), cy - int(r * 0.44))
    path = []
    for i in range(n + 1):
        t = i / n
        x = int(start[0] + t * (head_base[0] - start[0])
                + math.sin(t * math.pi * 1.25) * r * 0.26)
        y = int(start[1] + t * (head_base[1] - start[1]))
        path.append((x, y))
    for i, (x, y) in enumerate(path):
        rad = int(r * (0.17 - 0.03 * (i / n)))       # taper thick -> head base
        pygame.draw.circle(surf, col, (x, y), max(4, rad))
    # Enlarged triangular wedge head at the top, tipped up-left (the strike line).
    hx, hy = head_base
    tip = (hx - int(r * 0.30), hy - int(r * 0.24))    # snout apex, up-left
    pygame.draw.polygon(surf, col, [
        tip,
        (hx + int(r * 0.20), hy - int(r * 0.20)),     # crown, back-right
        (hx + int(r * 0.14), hy + int(r * 0.16)),     # jaw, joins the neck
    ])
    # Recessed eye so the wedge reads as a head, not a plain arrow.
    pygame.draw.circle(surf, _SH, (hx + int(r * 0.02), hy - int(r * 0.06)),
                       max(2, int(r * 0.07)))
    # Forked V-flick tongue darting from the snout apex — the bite.
    tw = max(2, int(r * 0.06))
    mid = (tip[0] - int(r * 0.16), tip[1] - int(r * 0.10))
    pygame.draw.line(surf, col, tip, mid, tw)
    for dx, dy in ((-0.12, -0.02), (-0.06, -0.14)):
        pygame.draw.line(surf, col, mid,
                         (mid[0] + int(r * dx), mid[1] + int(r * dy)), tw)


def _glyph_lightning_magnet(surf, cx, cy, r, col):
    # A poles-UP horseshoe magnet with TWO fat jagged bolts stabbing straight down
    # into its pole mouths — "you attract the strikes." No cloud (it fused the
    # poles into a cup blob); the bold U + two thick zig-zags carry the joke alone.
    # This is the mirror of magnet_life (poles down pulling one coin).
    mcx = cx
    mcy = cy + int(r * 0.42)
    rr = int(r * 0.50)
    leg_w = max(8, int(r * 0.32))
    bar = max(8, int(r * 0.34))
    # Curved yoke at the BOTTOM (opening upward): lower semicircle arc.
    arc_rect = pygame.Rect(mcx - rr, mcy - rr, rr * 2, rr * 2)
    pygame.draw.arc(surf, col, arc_rect, math.radians(184), math.radians(356), bar)
    # Two legs rising to the square pole mouths.
    leg_h = int(r * 0.58)
    leg_top = mcy - leg_h
    for sgn in (-1, 1):
        lx = mcx + sgn * rr - leg_w // 2
        pygame.draw.rect(surf, col, (lx, leg_top, leg_w, leg_h))
    # Pole-tip bands (accent on unlock) capping the mouths that face the bolts.
    tip_h = max(5, int(r * 0.20))
    for sgn, tip in ((-1, ai._accent((212, 64, 56))), (1, ai._accent((224, 228, 240)))):
        lx = mcx + sgn * rr - leg_w // 2
        pygame.draw.rect(surf, tip, (lx, leg_top - tip_h, leg_w, tip_h))
    # TWO fat jagged bolts, one plunging into each pole mouth — thick, few, and
    # clearly zig-zagged so they never wash out at 44px.
    def bolt(bx, top_y, h, w):
        seg = h / 3.0
        pts = [
            (bx - w * 0.4, top_y),
            (bx + w * 0.9, top_y + seg),
            (bx + w * 0.2, top_y + seg),
            (bx + w * 1.4, top_y + seg * 2),
            (bx + w * 0.5, top_y + seg * 2),
            (bx + w * 1.3, top_y + h),        # sharp strike tip
            (bx - w * 0.2, top_y + seg * 1.7),
            (bx + w * 0.5, top_y + seg * 1.7),
            (bx - w * 0.6, top_y + seg * 0.8),
            (bx + w * 0.1, top_y + seg * 0.8),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])

    bolt_top = cy - int(r * 0.74)
    bolt_h = int(r * 0.64)
    bw = int(r * 0.18)
    bolt(mcx - rr, bolt_top, bolt_h, bw)
    bolt(mcx + rr - int(bw * 0.6), bolt_top, bolt_h, bw)


GLYPHS = {
    "ninety_nine": _glyph_ninety_nine,
    "groundhog_day": _glyph_groundhog_day,
    "stat_impossible": _glyph_stat_impossible,
    "three_am": _glyph_three_am,
    "same_time_tomorrow": _glyph_same_time_tomorrow,
    "snake_bit": _glyph_snake_bit,
    "lightning_magnet": _glyph_lightning_magnet,
}
