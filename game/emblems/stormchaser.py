"""
Bespoke engraved center glyphs for the STORMCHASER achievement family (gold).

These are author-time overrides for ``game.achievement_icons._GLYPHS`` — drawn
in the exact same single-colour engrave idiom (bold filled polygons / thick
lines / discs in the passed ``col``, embossed by the builder's inset-shadow +
sheen passes). Each glyph lives in a 0..1 box scaled by ``r`` (~22px), no
sub-5px detail, no numerals.

Three tier pairs each share ONE silhouette via a helper with a ``tier`` arg so a
glance reads the climb off COUNT / MATERIAL, never rank dressing:
  * near_miss_5/15  — needle-and-thread; bead COUNT 1 → 3.
  * headbanger/hard_head — ceiling BAR is the constant anchor; the bonker swaps
    arrow → helmet-head, and the bar goes from clean to dented.
  * flap_life/iron_wings — macaw wing; feathered → riveted iron plates.

Four standalones are bottom-up-distinct silhouettes: stopwatch+road-dash,
rain-cloud-bolt, six-arm snowflake, (the pairs cover the rest).
"""
from __future__ import annotations

import math
import pygame

import game.achievement_icons as ai

# Pull the family's engraved-shadow tone + accent resolver so these glyphs use
# the exact same recessed-detail treatment as the shipped ones.
_GLYPH_SH = ai._GLYPH_SH
_accent = ai._accent


# ── shared tier helper: needle-and-thread (near_miss_5 → near_miss_15) ────────
#
# ONE motif for both rungs (v2 lock: NO razor-gap scene). An upright sewing
# needle, an oval eye near the top, and a thread looping through the eye. The
# tier climbs purely by BEAD COUNT strung on the thread: 1 bead at L0, 3 beads
# at the high rung — "threading an impossibly fine gap, again and again."

def _needle_thread(surf, cx, cy, r, col, tier):
    lw = max(3, int(r * 0.16))
    # The needle runs lower-right to upper-left so the eye sits up top with room
    # for the thread loop to swing off it.
    tip = (cx + r * 0.46, cy + r * 0.78)        # sharp point, lower-right
    eye_c = (cx - r * 0.30, cy - r * 0.52)      # eye, upper-left
    butt = (cx - r * 0.46, cy - r * 0.78)       # blunt end past the eye
    pygame.draw.line(surf, col, (int(tip[0]), int(tip[1])),
                     (int(eye_c[0]), int(eye_c[1])), lw)
    pygame.draw.line(surf, col, (int(eye_c[0]), int(eye_c[1])),
                     (int(butt[0]), int(butt[1])), lw)
    # The oval eye — a ring straddling the shaft near the blunt end.
    ew, eh = int(r * 0.30), int(r * 0.44)
    eye_rect = pygame.Rect(int(eye_c[0] - ew / 2), int(eye_c[1] - eh / 2), ew, eh)
    pygame.draw.ellipse(surf, col, eye_rect, max(2, int(r * 0.10)))
    # Thread loop swinging off the eye (up top), then a STRAIGHT lower segment
    # running down-right that the beads are strung on — a clean baseline so the
    # bead COUNT reads cleanly instead of smearing into the loop.
    loop = pygame.Rect(int(cx - r * 0.16), int(cy - r * 0.74),
                       int(r * 0.58), int(r * 0.50))
    pygame.draw.arc(surf, col, loop, math.radians(-30), math.radians(210),
                    max(2, int(r * 0.11)))
    # Straightened thread run holding the beads, well clear of the loop.
    str_a = (cx + r * 0.04, cy + r * 0.06)
    str_b = (cx + r * 0.74, cy + r * 0.80)
    pygame.draw.line(surf, col, (int(str_a[0]), int(str_a[1])),
                     (int(str_b[0]), int(str_b[1])), max(2, int(r * 0.09)))
    # Beads on that straight run — fat discs so the 1 vs 3 COUNT is unmistakable
    # at chip size. Each beads' centre is evenly spaced along the segment.
    n = 1 if tier == 0 else 3
    bead_r = max(4, int(r * 0.15))
    if n == 1:
        fracs = [0.55]
    else:
        fracs = [0.30, 0.55, 0.80]
    for f in fracs:
        bx = str_a[0] + (str_b[0] - str_a[0]) * f
        by = str_a[1] + (str_b[1] - str_a[1]) * f
        pygame.draw.circle(surf, col, (int(bx), int(by)), bead_r)
        # tiny dark bead-hole so each reads as a strung bead, not a dot
        pygame.draw.circle(surf, _GLYPH_SH, (int(bx), int(by)), max(1, bead_r // 3))


def _glyph_near_miss_5(surf, cx, cy, r, col):
    _needle_thread(surf, cx, cy, r, col, tier=0)


def _glyph_near_miss_15(surf, cx, cy, r, col):
    _needle_thread(surf, cx, cy, r, col, tier=1)


# ── shared tier helper: ceiling bonk (headbanger → hard_head) ─────────────────
#
# The ceiling BAR across the top is the CONSTANT shared anchor. Tier swaps the
# bonker (up-arrow → blunt helmet-head) and the bar's state (clean → dented),
# and the impact spark COUNT grows 2 → 4.

def _ceiling_bonk(surf, cx, cy, r, col, tier):
    w = max(3, int(r * 0.15))
    # Bar geometry is IDENTICAL across both tiers — the shared anchor. hard_head
    # only carves damage INTO this same bar (same width / position / thickness).
    bar_y = cy - int(r * 0.56)
    bar_h = max(4, int(r * 0.24))
    bar_l, bar_w = cx - int(r * 0.84), int(r * 1.68)
    top = bar_y - bar_h // 2
    bot = bar_y + bar_h // 2
    if tier == 0:
        # Clean ceiling bar.
        pygame.draw.rect(surf, col, (bar_l, top, bar_w, bar_h),
                         border_radius=max(1, int(r * 0.08)))
    else:
        # Same bar, now visibly damaged: a deep V-notch bitten UP into the
        # underside where the head rams it. The notch eats most of the bar's
        # thickness so the dent is unmistakable beside headbanger's clean bar.
        d = int(bar_h * 0.92)                 # dent nearly through the bar
        nw = int(r * 0.30)                    # notch mouth half-width
        pts = [
            (bar_l, top), (bar_l + bar_w, top),
            (bar_l + bar_w, bot),
            (cx + nw, bot),
            (cx, bot - d),                    # the dent apex driven up
            (cx - nw, bot),
            (bar_l, bot),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])
        # crack-ticks lancing up out of the dent apex into the bar body, in the
        # engraved-shadow tone so they read as fractures struck into the metal.
        for ddx in (-int(r * 0.12), int(r * 0.13)):
            pygame.draw.line(surf, _GLYPH_SH, (cx, bot - d),
                             (cx + ddx, top + max(1, int(r * 0.03))),
                             max(2, int(r * 0.08)))

    contact_y = bar_y + bar_h // 2 + int(r * 0.04)
    if tier == 0:
        # Up-arrow striking the bar from below.
        tip = (cx, contact_y + int(r * 0.06))
        pygame.draw.lines(surf, col, False, [
            (cx - int(r * 0.40), cy + int(r * 0.30)), tip,
            (cx + int(r * 0.40), cy + int(r * 0.30)),
        ], w)
        pygame.draw.line(surf, col, (cx, cy + int(r * 0.86)), tip, w)
    else:
        # Blunt helmet-head ramming the bar: a domed crown (the helmet) on a
        # short neck — an unbreakable noggin, not an arrow.
        head_r = int(r * 0.40)
        head_c = (cx, contact_y + head_r)
        pygame.draw.circle(surf, col, head_c, head_r)
        # helmet brim line so the dome reads as a helmet, not a ball
        pygame.draw.line(surf, _GLYPH_SH,
                         (cx - head_r, head_c[1] + int(r * 0.08)),
                         (cx + head_r, head_c[1] + int(r * 0.08)),
                         max(2, int(r * 0.09)))
        # stubby neck
        pygame.draw.rect(surf, col,
                         (cx - int(r * 0.14), head_c[1] + head_r - int(r * 0.04),
                          int(r * 0.28), int(r * 0.30)))

    # Impact sparks at the contact point — COUNT carries the tier: a clear pair
    # (headbanger) vs a busy four (hard_head). Tier 0's two are drawn longer +
    # bolder so the count reads as exactly 2.
    if tier == 0:
        spark_xs, slen, sw = [-0.44, 0.44], 0.28, 0.11
    else:
        spark_xs, slen, sw = [-0.64, -0.34, 0.34, 0.64], 0.20, 0.08
    for fx in spark_xs:
        sgn = 1 if fx > 0 else -1
        sx = cx + int(fx * r)
        sy = bar_y + int(r * 0.20)
        pygame.draw.line(surf, col, (sx, sy),
                         (sx + sgn * int(r * slen), sy + int(r * (slen * 0.72))),
                         max(2, int(r * sw)))


def _glyph_headbanger(surf, cx, cy, r, col):
    _ceiling_bonk(surf, cx, cy, r, col, tier=0)


def _glyph_hard_head(surf, cx, cy, r, col):
    _ceiling_bonk(surf, cx, cy, r, col, tier=1)


# ── shared tier helper: macaw wing (flap_life → iron_wings) ───────────────────
#
# Same wing arc as the in-game wing. Tier 0 = a feathered wing with motion
# streaks behind it (it's flapping). Tier 1 = the SAME silhouette rendered as
# riveted iron: three plate segments split by groove lines, a rivet-dot on each
# — feather → forged metal is the whole escalation.

def _wing_shape(cx, cy, r):
    sx, sy = cx - r * 0.70, cy + r * 0.44          # shoulder
    tx, ty = cx + r * 0.74, cy - r * 0.58          # wing tip
    lebx, leby = cx - r * 0.50, cy - r * 0.68      # camber control point
    leading = []
    for i in range(9):
        t = i / 8
        mt = 1 - t
        bx = mt * mt * sx + 2 * mt * t * lebx + t * t * tx
        by = mt * mt * sy + 2 * mt * t * leby + t * t * ty
        leading.append((bx, by))
    lobes = [
        (cx + r * 0.46, cy + r * 0.06),
        (cx + r * 0.04, cy + r * 0.22),
        (cx - r * 0.34, cy + r * 0.52),
    ]
    return leading + lobes


def _macaw_wing(surf, cx, cy, r, col, tier):
    pts = _wing_shape(cx, cy, r)
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])
    if tier == 0:
        # Feather wing flapping: three parallel motion-streak ticks set in CLEAR
        # space behind (left of) the shoulder, not touching the wing, so they
        # read as speed-lines rather than damage to the feather.
        for dy in (-0.40, -0.06, 0.28):
            x1 = cx - r * 1.04                 # outer end, well off the wing
            x0 = cx - r * 0.78                 # inner end, clear of the shoulder
            y = cy + r * dy
            pygame.draw.line(surf, col, (int(x1), int(y)),
                             (int(x0), int(y)), max(3, int(r * 0.11)))
    else:
        # Riveted iron: split the wing into just THREE bold plate segments with
        # WIDE seam grooves between them, and ONE clear rivet-dot per plate — so
        # "plated metal" survives the chip instead of dissolving into noise.
        seams = [
            ((cx + r * 0.28, cy - r * 0.42), (cx + r * 0.22, cy + r * 0.12)),
            ((cx - r * 0.14, cy - r * 0.24), (cx - r * 0.18, cy + r * 0.34)),
        ]
        for a, b in seams:
            pygame.draw.line(surf, _GLYPH_SH, (int(a[0]), int(a[1])),
                             (int(b[0]), int(b[1])), max(3, int(r * 0.13)))
        # One rivet centred in each of the three plates.
        rivets = [
            (cx + r * 0.46, cy - r * 0.28),
            (cx + r * 0.06, cy - r * 0.04),
            (cx - r * 0.34, cy + r * 0.22),
        ]
        rr = max(3, int(r * 0.11))
        for rx, ry in rivets:
            pygame.draw.circle(surf, _GLYPH_SH, (int(rx), int(ry)), rr)
            pygame.draw.circle(surf, col, (int(rx), int(ry)), max(1, rr - max(2, int(r * 0.05))))


def _glyph_flap_life(surf, cx, cy, r, col):
    _macaw_wing(surf, cx, cy, r, col, tier=0)


def _glyph_iron_wings(surf, cx, cy, r, col):
    _macaw_wing(surf, cx, cy, r, col, tier=1)


# ── standalone: marathon — stopwatch + one road-dash ──────────────────────────

def _glyph_marathon(surf, cx, cy, r, col):
    # A stopwatch mid-tick lifted clear of centre, with ONE road/horizon dash
    # beneath it (no numerals) — the running-road cue separates it from a plain
    # clock.
    cyd = cy - int(r * 0.16)                    # dial nudged up to make room
    rr = int(r * 0.56)
    pygame.draw.circle(surf, col, (cx, cyd), rr, max(3, int(r * 0.13)))
    # crown nub + side button so it reads as a stopwatch
    pygame.draw.rect(surf, col, (cx - max(2, r // 10), cyd - rr - int(r * 0.20),
                                 max(4, r // 5), max(3, int(r * 0.18))),
                     border_radius=max(1, r // 14))
    pygame.draw.rect(surf, col,
                     (cx + int(rr * 0.62), cyd - rr - int(r * 0.04),
                      max(3, int(r * 0.14)), max(3, int(r * 0.14))))
    # hands: one bottom-pointing (the implied 2:00 sweep) + one short
    pygame.draw.line(surf, col, (cx, cyd), (cx, cyd + int(rr * 0.64)),
                     max(2, int(r * 0.11)))
    pygame.draw.line(surf, col, (cx, cyd),
                     (cx + int(rr * 0.50), cyd - int(rr * 0.14)),
                     max(2, int(r * 0.10)))
    # the road — a bold SEGMENTED lane marking clearly below the dial: three
    # fat dashes so the running-road cue (what separates this from any clock)
    # survives at chip size.
    dash_y = cy + int(r * 0.78)
    dash_w = max(4, int(r * 0.18))
    seg = r * 0.26
    for fx in (-0.46, 0.0, 0.46):
        x0 = cx + fx * r - seg / 2
        pygame.draw.line(surf, col, (int(x0), dash_y),
                         (int(x0 + seg), dash_y), dash_w)


# ── standalone: storm_rider — rain cloud + lightning bolt + streaks ───────────

def _glyph_storm_rider(surf, cx, cy, r, col):
    # A puffy rain cloud silhouette so the bolt reads as RAIN, not a bare bolt.
    cloud_y = cy - int(r * 0.32)
    lobes = [
        (cx - r * 0.46, cloud_y, r * 0.34),
        (cx - r * 0.06, cloud_y - r * 0.16, r * 0.42),
        (cx + r * 0.40, cloud_y, r * 0.36),
    ]
    for lx, ly, lr in lobes:
        pygame.draw.circle(surf, col, (int(lx), int(ly)), int(lr))
    # flat cloud base bar so the lobes fuse into one cloud
    pygame.draw.rect(surf, col,
                     (int(cx - r * 0.56), int(cloud_y - r * 0.02),
                      int(r * 1.06), int(r * 0.30)),
                     border_radius=max(2, int(r * 0.10)))
    # lightning bolt dropping out of the cloud's belly (accent yellow on unlock)
    by = cloud_y + int(r * 0.28)
    bolt = [
        (cx + r * 0.04, by),
        (cx - r * 0.18, by + r * 0.40),
        (cx + r * 0.00, by + r * 0.40),
        (cx - r * 0.10, by + r * 0.86),
        (cx + r * 0.26, by + r * 0.24),
        (cx + r * 0.06, by + r * 0.24),
    ]
    pygame.draw.polygon(surf, _accent((255, 214, 84)),
                        [(int(x), int(y)) for x, y in bolt])
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in bolt],
                        max(1, int(r * 0.05)))
    # rain streaks flanking the bolt
    for fx in (-0.40, 0.42):
        rx = cx + int(fx * r)
        ry = by + int(r * 0.12)
        pygame.draw.line(surf, col, (rx, ry),
                         (rx - int(r * 0.10), ry + int(r * 0.42)),
                         max(2, int(r * 0.09)))


# ── standalone: snowbird — six-arm snowflake + tiny bird-chevron centre ───────

def _glyph_snowbird(surf, cx, cy, r, col):
    # Six bold spokes with one short branch tick each (drop to bare spokes if the
    # branch ever muds), and a tiny bird-chevron nested at the hub — the
    # snow-squall biome.
    arm = r * 0.86
    sw = max(3, int(r * 0.13))
    for i in range(6):
        a = i * math.pi / 3 - math.pi / 2
        ex = cx + math.cos(a) * arm
        ey = cy + math.sin(a) * arm
        pygame.draw.line(surf, col, (cx, cy), (int(ex), int(ey)), sw)
        # one branch tick part-way out, on each side
        bf = 0.62
        bx = cx + math.cos(a) * arm * bf
        by = cy + math.sin(a) * arm * bf
        blen = r * 0.24
        for da in (math.radians(38), -math.radians(38)):
            tx = bx + math.cos(a + da) * blen
            ty = by + math.sin(a + da) * blen
            pygame.draw.line(surf, col, (int(bx), int(by)),
                             (int(tx), int(ty)), max(2, int(r * 0.09)))
    # tiny bird-chevron at the hub — a small filled "M" of two wings
    chv = r * 0.30
    pts = [
        (cx - chv, cy + chv * 0.30),
        (cx - chv * 0.30, cy - chv * 0.30),
        (cx, cy + chv * 0.10),
        (cx + chv * 0.30, cy - chv * 0.30),
        (cx + chv, cy + chv * 0.30),
        (cx, cy + chv * 0.46),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


GLYPHS = {
    "near_miss_5": _glyph_near_miss_5,
    "near_miss_15": _glyph_near_miss_15,
    "marathon": _glyph_marathon,
    "storm_rider": _glyph_storm_rider,
    "snowbird": _glyph_snowbird,
    "flap_life": _glyph_flap_life,
    "headbanger": _glyph_headbanger,
    "hard_head": _glyph_hard_head,
    "iron_wings": _glyph_iron_wings,
}
