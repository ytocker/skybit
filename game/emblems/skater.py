"""Bespoke engraved center glyphs for the eight SKATER achievements (gold tone).

Drop-in `_glyph_<id>` functions matching `game/achievement_icons.py`'s engrave
idiom: BOLD filled polygons / thick lines / discs authored in the passed `col`,
stamped twice by the builder (dark inset down-right + lit body) for struck-metal
relief. `_GLYPH_SH` is read straight from the module so wheel/contact recesses
stay dark like the production `_glyph_skate`. Nothing here is wired into the
game; a render harness updates `ai._GLYPHS` to preview these.

Four silhouette FAMILIES carry the read so the eight never blur together at the
~22px glyph size:

  * board-profile  — board_meeting / sponsored / going_pro  (a deck in profile)
  * rotation-loop  — trickster / trick_legend               (a spin ring)
  * rail-cart      — grinder / rail_baron                    (rail + rider)
  * four-dot-combo — full_combo                              (four dots + arc)

The three tier families each escalate ONE motif through a shared helper with a
`tier` arg — the silhouette is constant, only added metal/marks climb — so a
glance reads the rank-up (grounded->stickered->airborne, half-spin->full-ring,
board-on-rail->cart-on-rail) before it ever notices a pip or crownlet.
"""
from __future__ import annotations

import math

import pygame

import game.achievement_icons as ai

# Engraved recess tone (wheels, rail contact, deck cavities) — pulled live from
# the production module so these previews stay in lock-step with any retune.
_SH = ai._GLYPH_SH


# ── shared rank-dressing accents (faint cherry-on-top; never the read) ────────
#
# The spec demotes L-marks: count/material/container growth carries the tier,
# these only confirm it. Kept tiny and tucked so they never compete with the
# motif at 44px.

def _pips(surf, cx, cy, r, col, n):
    # 1–3 notch-dots tucked along the glyph's lower edge.
    pr = max(2, int(r * 0.07))
    span = r * 0.22 * (n - 1)
    for i in range(n):
        px = cx - span / 2 + span * (i / max(1, n - 1) if n > 1 else 0)
        pygame.draw.circle(surf, col, (int(px), int(cy + r * 0.86)), pr)


def _wreath(surf, cx, cy, r, col):
    # Two short laurel-echo ticks flanking the base.
    w = max(2, r // 12)
    for sgn in (-1, 1):
        bx = cx + sgn * r * 0.74
        pygame.draw.line(surf, col, (int(bx), int(cy + r * 0.66)),
                         (int(bx + sgn * r * 0.16), int(cy + r * 0.50)), w)
        pygame.draw.line(surf, col, (int(bx), int(cy + r * 0.66)),
                         (int(bx + sgn * r * 0.16), int(cy + r * 0.82)), w)


def _crownlet(surf, cx, cy, r, col):
    # A 3-point engraved crownlet seated above the motif — the apex rung marker.
    w = max(2, r // 10)
    base_y = cy - r * 0.92
    span = r * 0.34
    pts = [
        (cx - span, base_y + r * 0.10),
        (cx - span, base_y - r * 0.06),
        (cx - span * 0.5, base_y + r * 0.06),
        (cx, base_y - r * 0.16),
        (cx + span * 0.5, base_y + r * 0.06),
        (cx + span, base_y - r * 0.06),
        (cx + span, base_y + r * 0.10),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])
    pygame.draw.line(surf, col, (int(cx - span), int(base_y + r * 0.12)),
                     (int(cx + span), int(base_y + r * 0.12)), w)


# ── board-profile family : board_meeting -> sponsored -> going_pro ────────────
#
# One skateboard-in-profile silhouette (concave deck + two upturned kick-tails +
# two wheels slung under). tier escalates grounded -> stickered -> airborne:
#   tier 0  grounded board, a single "caught" spark above it
#   tier 1  the deck wears a sponsor STAR sticker on its belly + wreath ticks
#   tier 2  the board is tilted mid-OLLIE with two motion-arcs below + crownlet
# Wheels are dark recesses (like the production _glyph_skate) so the board reads
# as a board, not a bench, at row size.

def _board_catch(surf, cx, cy, r, col, tier):
    th = max(4, int(r * 0.17))
    airborne = tier >= 2
    tilt = -0.26 if airborne else 0.0     # radians; ollie nose-up
    yk = cy - int(r * 0.04) + (int(r * 0.10) if airborne else 0)

    ct, st = math.cos(tilt), math.sin(tilt)

    def _pt(dx, dy):
        # rotate a deck-local point about the deck centre for the ollie tilt
        return (cx + dx * ct - dy * st, yk + dx * st + dy * ct)

    # concave deck with raised kick-tails — two stacked edges as a closed poly.
    # The belly is kept FLAT and full-thickness across the middle (a gentle dip
    # only near the tails) so a sponsor sticker can sit ON the deck without
    # severing it, and the board stays one solid bar at row size.
    deck = [
        _pt(-r * 0.80, -r * 0.26), _pt(-r * 0.56, -r * 0.02),
        _pt(r * 0.56, -r * 0.02), _pt(r * 0.80, -r * 0.26),
        _pt(r * 0.80, -r * 0.26 + th), _pt(r * 0.56, th + r * 0.04),
        _pt(-r * 0.56, th + r * 0.04), _pt(-r * 0.80, -r * 0.26 + th),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in deck])

    # two fat wheels slung under the deck — dark discs that break the silhouette
    wr = max(4, int(r * 0.20))
    for dx in (-0.40, 0.40):
        wx, wy = _pt(dx * r, th + wr * 0.7)
        pygame.draw.circle(surf, _SH, (int(wx), int(wy)), wr)
        pygame.draw.circle(surf, col, (int(wx), int(wy)), max(1, wr // 3))

    if tier == 0:
        # "caught" spark above the deck — a small four-tick twinkle
        sx, sy = cx + int(r * 0.10), cy - int(r * 0.66)
        s = max(3, int(r * 0.20))
        pygame.draw.line(surf, col, (sx - s, sy), (sx + s, sy), max(2, r // 12))
        pygame.draw.line(surf, col, (sx, sy - s), (sx, sy + s), max(2, r // 12))

    if tier == 1:
        # BOLD deck-spanning sponsor star riding ON the deck so it breaks the
        # flat top silhouette — at 44px the rung 1->2 read IS the star, not a
        # sub-pixel sticker. Its lower points overlap the deck while the top
        # point rises clear above it, so board_meeting (bare deck) and sponsored
        # (deck wearing a big star) read apart even at row size.
        cxx, cyy = _pt(0, -r * 0.06)
        _star(surf, int(cxx), int(cyy), r * 0.56, _SH)
        _star(surf, int(cxx), int(cyy), r * 0.48, col)
        _wreath(surf, cx, cy, r, col)

    if airborne:
        # two motion-arcs sweeping under the lifted board — the ollie lift-off
        for i, rad in enumerate((r * 0.62, r * 0.86)):
            arc = pygame.Rect(int(cx - rad), int(cy + r * 0.30 - rad * 0.4),
                              int(rad * 2), int(rad * 0.8))
            pygame.draw.arc(surf, col, arc, math.radians(205), math.radians(335),
                            max(2, r // 13))
        _crownlet(surf, cx, cy, r, col)


def _star(surf, cx, cy, r, col):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _glyph_board_meeting(surf, cx, cy, r, col):
    _board_catch(surf, cx, cy, r, col, 0)


def _glyph_sponsored(surf, cx, cy, r, col):
    _board_catch(surf, cx, cy, r, col, 1)


def _glyph_going_pro(surf, cx, cy, r, col):
    _board_catch(surf, cx, cy, r, col, 2)


# ── rotation-loop family : trickster -> trick_legend ──────────────────────────
#
# A board caught inside a spin. The ROTATION RING is the silhouette — distinct
# from the grounded board-profile by being a loop, not a deck-and-wheels:
#   tier 0  a HALF rotation arc (a kickflip arrow ~210°) wrapping a tilted board,
#           one landing-spark
#   tier 1  the loop CLOSES into a full 360° ring with three motion-arcs +
#           crownlet — the spin completes as the count climbs
# The board inside is a short tilted deck (NO wheels) so it never collides with
# the board-catch family's grounded silhouette.

def _spin_board(surf, cx, cy, r, col, ang):
    # a short fat deck tilted at `ang`, no wheels — the thing being spun
    ca, sa = math.cos(ang), math.sin(ang)
    half, th = r * 0.40, r * 0.16
    pts = []
    for dx, dy in ((-half, -th), (half, -th), (half, th), (-half, th)):
        pts.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])
    # the two kick-tail nibs so a tiny board still reads as a board
    for sgn in (-1, 1):
        nx = cx + sgn * half * ca
        ny = cy + sgn * half * sa
        pygame.draw.circle(surf, col, (int(nx - sa * th * 1.4),
                                       int(ny + ca * th * 1.4)), max(2, int(r * 0.10)))


def _trick_rotation(surf, cx, cy, r, col, tier):
    full = tier >= 1
    ring_r = r * 0.82
    w = max(3, int(r * 0.15))
    rect = pygame.Rect(int(cx - ring_r), int(cy - ring_r),
                       int(ring_r * 2), int(ring_r * 2))
    if full:
        # closed 360 ring + an arrowhead riding the top so it reads as a spin,
        # not a plain coin ring
        pygame.draw.circle(surf, col, (cx, cy), int(ring_r), w)
        ax, ay = cx + int(ring_r * 0.30), int(cy - ring_r)
        ah = max(4, int(r * 0.22))
        pygame.draw.polygon(surf, col, [
            (ax - ah, ay - ah // 2), (ax + ah, ay - ah // 2), (ax, ay + ah)])
        # three short motion-arcs nested inside the ring
        for rad in (ring_r * 0.46, ring_r * 0.62, ring_r * 0.78):
            mr = pygame.Rect(int(cx - rad), int(cy - rad), int(rad * 2), int(rad * 2))
            pygame.draw.arc(surf, col, mr, math.radians(20), math.radians(110),
                            max(2, r // 14))
        _spin_board(surf, cx, cy, r * 0.82, col, math.radians(-38))
        _crownlet(surf, cx, cy, r, col)
    else:
        # HALF rotation: an OPEN ~210° kickflip arc with an arrowhead on its
        # leading end, wrapping a small tilted board. The arc stroke is thinned
        # ~20% (vs the full ring) and the board is shrunk + pushed to a clean 45°
        # chevron centred LOW, so board and arc separate at 44px and the open
        # arc stays distinct from trick_legend's closed ring.
        wt = max(2, int(w * 0.8))
        pygame.draw.arc(surf, col, rect, math.radians(20), math.radians(230), wt)
        # arrowhead at the arc's leading (upper-right) end
        a = math.radians(20)
        ex, ey = cx + math.cos(a) * ring_r, cy - math.sin(a) * ring_r
        ah = max(4, int(r * 0.22))
        pygame.draw.polygon(surf, col, [
            (int(ex - ah * 0.2), int(ey - ah)), (int(ex + ah), int(ey)),
            (int(ex - ah), int(ey + ah * 0.4))])
        # smaller board, dropped below the arc's centre so the loop reads as
        # negative space AROUND it rather than crossing it
        _spin_board(surf, cx, cy + int(r * 0.22), r * 0.66, col, math.radians(45))
        # landing-spark at lower-left
        sx, sy = cx - int(r * 0.48), cy + int(r * 0.60)
        s = max(2, int(r * 0.16))
        pygame.draw.line(surf, col, (sx - s, sy), (sx + s, sy), max(2, r // 13))
        pygame.draw.line(surf, col, (sx, sy - s), (sx, sy + s), max(2, r // 13))
        _pips(surf, cx, cy, r, col, 1)


def _glyph_trickster(surf, cx, cy, r, col):
    _trick_rotation(surf, cx, cy, r, col, 0)


def _glyph_trick_legend(surf, cx, cy, r, col):
    _trick_rotation(surf, cx, cy, r, col, 1)


# ── rail-cart family : grinder -> rail_baron ──────────────────────────────────
#
# An angled grind rail with a rider on it. tier upgrades the RIDER:
#   tier 0  a board mid-grind on the rail + two grind-sparks at the contact pt
#   tier 1  a whole MINE-CART rides the rail (box body + two cart-wheels) +
#           crownlet — baron of the rails, matching the in-game rail cart
# The rail runs lower-left -> upper-right with two support posts (shared
# silhouette with the production _glyph_rail).

def _rail_ride(surf, cx, cy, r, col, tier):
    cart = tier >= 1
    rw = max(3, int(r * 0.15))
    x0, y0 = cx - r * 0.80, cy + r * 0.50
    x1, y1 = cx + r * 0.80, cy - r * 0.26
    pygame.draw.line(surf, col, (int(x0), int(y0)), (int(x1), int(y1)), rw)
    # two support posts dropping from the rail
    for f in (0.26, 0.74):
        px = x0 + (x1 - x0) * f
        py = y0 + (y1 - y0) * f
        pygame.draw.line(surf, col, (int(px), int(py)),
                         (int(px), int(py + r * 0.32)), max(2, r // 12))

    dxn, dyn = (x1 - x0), (y1 - y0)
    blen = math.hypot(dxn, dyn)
    ux, uy = dxn / blen, dyn / blen          # along-rail unit
    nx, ny = -uy, ux                          # rail normal (up-ish)

    bf = 0.50
    bx = x0 + dxn * bf
    by = y0 + dyn * bf

    if cart:
        # a mine-cart riding the rail: an open trapezoid tub sitting above the
        # rail on two cart-wheels — the silhouette upgrades board -> cart
        lift = r * 0.30
        ccx = bx + nx * lift
        ccy = by + ny * lift
        half_top, half_bot = r * 0.50, r * 0.34
        h = r * 0.42
        tub = [
            (ccx - ux * half_top + nx * h * 0.5, ccy - uy * half_top + ny * h * 0.5),
            (ccx + ux * half_top + nx * h * 0.5, ccy + uy * half_top + ny * h * 0.5),
            (ccx + ux * half_bot - nx * h * 0.5, ccy + uy * half_bot - ny * h * 0.5),
            (ccx - ux * half_bot - nx * h * 0.5, ccy - uy * half_bot - ny * h * 0.5),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in tub])
        # hollow the tub so it reads as an open cart, not a solid block
        inset = 0.62
        inner = [
            (ccx - ux * half_top * inset + nx * h * 0.36,
             ccy - uy * half_top * inset + ny * h * 0.36),
            (ccx + ux * half_top * inset + nx * h * 0.36,
             ccy + uy * half_top * inset + ny * h * 0.36),
            (ccx + ux * half_bot * inset - nx * h * 0.18,
             ccy + uy * half_bot * inset - ny * h * 0.18),
            (ccx - ux * half_bot * inset - nx * h * 0.18,
             ccy - uy * half_bot * inset - ny * h * 0.18),
        ]
        pygame.draw.polygon(surf, _SH, [(int(x), int(y)) for x, y in inner])
        # two cart-wheels straddling the rail at the tub's foot
        wr = max(3, int(r * 0.15))
        for wf in (-0.34, 0.34):
            wx = bx + ux * (wf * r) + nx * r * 0.04
            wy = by + uy * (wf * r) + ny * r * 0.04
            pygame.draw.circle(surf, _SH, (int(wx), int(wy)), wr)
            pygame.draw.circle(surf, col, (int(wx), int(wy)), max(1, wr // 3))
        _crownlet(surf, cx, cy, r, col)
    else:
        # a board mid-grind, lifted CLEAR above the rail line (so board and rail
        # don't collapse into one diagonal bar) and tilted to the rail's slope
        lift = r * 0.34
        half = r * 0.42
        board = [
            (bx - ux * half + nx * lift, by - uy * half + ny * lift),
            (bx + ux * half + nx * lift, by + uy * half + ny * lift),
            (bx + ux * half + nx * (lift + r * 0.16),
             by + uy * half + ny * (lift + r * 0.16)),
            (bx - ux * half + nx * (lift + r * 0.16),
             by - uy * half + ny * (lift + r * 0.16)),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in board])
        # BOLD grind BURST at the board-rail junction — a fat star of rays
        # between the board's underside and the rail, the focal "grinding here"
        # read that separates this from rail_baron's rolling cart.
        jx = bx + nx * (lift * 0.4)
        jy = by + ny * (lift * 0.4)
        bw = max(2, int(r * 0.12))
        for ang in range(0, 360, 45):
            a = math.radians(ang)
            length = r * (0.30 if ang % 90 == 0 else 0.20)
            pygame.draw.line(surf, col, (int(jx), int(jy)),
                             (int(jx + math.cos(a) * length),
                              int(jy + math.sin(a) * length)), bw)
        pygame.draw.circle(surf, col, (int(jx), int(jy)), max(2, int(r * 0.10)))
        _pips(surf, cx, cy, r, col, 1)


def _glyph_grinder(surf, cx, cy, r, col):
    _rail_ride(surf, cx, cy, r, col, 0)


def _glyph_rail_baron(surf, cx, cy, r, col):
    _rail_ride(surf, cx, cy, r, col, 1)


# ── four-dot-combo : full_combo (v2 LOCKED) ───────────────────────────────────
#
# v2 LOCK: four DOTS in a chevron + ONE combo-arc — NOT four distinct
# trick-glyphs (those die at row size). The read is "four marks under one
# combo-sweep": a count silhouette, distinct from the board / loop / rail
# families above. The dots are fat and identical; the arc ties them into a combo.

def _glyph_full_combo(surf, cx, cy, r, col):
    dr = max(4, int(r * 0.18))
    # four dots stepping up in a chevron (V-formation rising left->right->up)
    dots = [
        (cx - r * 0.58, cy + r * 0.30),
        (cx - r * 0.20, cy + r * 0.02),
        (cx + r * 0.20, cy + r * 0.02),
        (cx + r * 0.58, cy + r * 0.30),
    ]
    # one combo-arc sweeping over the four — the "COMBO!" tie
    arc_r = r * 0.92
    rect = pygame.Rect(int(cx - arc_r), int(cy - arc_r * 0.70),
                       int(arc_r * 2), int(arc_r * 1.5))
    pygame.draw.arc(surf, col, rect, math.radians(28), math.radians(152),
                    max(3, int(r * 0.15)))
    # the four identical dots, drawn after the arc so they sit crisp on top
    for dx, dy in dots:
        pygame.draw.circle(surf, col, (int(dx), int(dy)), dr)
    # a small apex spark crowning the combo-arc's peak so it reads "combo", not
    # a bare bridge
    sx, sy = cx, int(cy - r * 0.64)
    s = max(2, int(r * 0.16))
    pygame.draw.line(surf, col, (sx - s, sy), (sx + s, sy), max(2, r // 13))
    pygame.draw.line(surf, col, (sx, sy - s), (sx, sy + s), max(2, r // 13))


GLYPHS = {
    "board_meeting": _glyph_board_meeting,
    "sponsored": _glyph_sponsored,
    "going_pro": _glyph_going_pro,
    "trickster": _glyph_trickster,
    "trick_legend": _glyph_trick_legend,
    "grinder": _glyph_grinder,
    "rail_baron": _glyph_rail_baron,
    "full_combo": _glyph_full_combo,
}
