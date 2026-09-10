"""
BATCH 1 — nine bespoke engraved centre glyphs for the new Hall-of-Fame
achievements, authored in the struck-metal engrave idiom shared with
``game/achievement_icons.py`` and the ``game/emblems/*`` modules.

Each ``_glyph_<id>(surf, cx, cy, r, col)`` draws BOLD filled polygons / thick
lines / discs in the single passed ``col`` (the host stamps a dark inset pass
down-right + lit body + up-left sheen for the engraved relief), reaching for the
inset-shadow tone ``ai._GLYPH_SH`` only where a shape must read as a recessed
cutout, and routing any saturated accent through ``ai._accent`` so a dormant
medal stays bronze-monochrome. Every feature is kept above the ~5px floor so the
read survives the 44px row size inside the gold laurel wreath.

These are the LADDER APEXES — each one is deliberately drawn to out-mass the
existing rung it climbs past (pillar_100 -> a crowned obelisk, score_500's three
chevrons -> four + a burst, day_three's three moons -> a seven-moon night arc,
midas -> the million-coin bag, the sparkle -> overcharged / cradled / plumbed).
"""
from __future__ import annotations

import math

import pygame

import game.achievement_icons as ai


# ── shared primitives ────────────────────────────────────────────────────────

def _sparkle_pts(cx, cy, r, waist=0.28, reach=0.86):
    # The franchise four-point sparkle body, reused so every power-up emblem in
    # this batch shares one star silhouette.
    return [
        (cx, cy - r * reach), (cx + r * waist, cy - r * waist),
        (cx + r * reach, cy), (cx + r * waist, cy + r * waist),
        (cx, cy + r * reach), (cx - r * waist, cy + r * waist),
        (cx - r * reach, cy), (cx - r * waist, cy - r * waist),
    ]


def _sparkle(surf, cx, cy, r, col, waist=0.28, reach=0.86):
    pygame.draw.polygon(surf, col,
                        [(int(x), int(y)) for x, y in
                         _sparkle_pts(cx, cy, r, waist, reach)])


def _star(surf, cx, cy, r_out, col, r_in_f=0.42):
    # A five-point victory star (the pillar-ladder apex topper).
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rad = r_out if i % 2 == 0 else r_out * r_in_f
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _crownlet(surf, cx, base_y, r, col):
    # The shared L4 three-point coronet seated on a motif's apex.
    w = r * 0.52
    h = r * 0.28
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


def _dollar(surf, cx, cy, px, col):
    f = ai._glyph_font(int(px))
    g = f.render("$", True, col)
    surf.blit(g, g.get_rect(center=(int(cx), int(cy))))


# ═══════════════════════════════════════════════════════════════════════════
# 1 — sky_legend — Pass 250 pillars in one run.
#     Beyond pillar_100's triumphal arch: a crowned OBELISK monument rising from
#     a stepped plinth between two short flanking posts, a victory STAR blazing
#     at its apex — the pillar ladder's summit.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_sky_legend(surf, cx, cy, r, col):
    base_y = cy + r * 0.90

    # Two short flanking posts frame the monument (the colonnade left behind).
    post_w = max(4, int(r * 0.22))
    post_h = r * 0.74
    cap_w = int(post_w * 1.7)
    cap_h = max(3, int(r * 0.13))
    for sgn in (-1, 1):
        px = cx + sgn * r * 0.74
        top = base_y - post_h
        pygame.draw.rect(surf, col, (int(px - post_w / 2), int(top + cap_h),
                                     post_w, int(post_h - cap_h * 2)))
        for yy in (top, base_y - cap_h):
            pygame.draw.rect(surf, col, (int(px - cap_w / 2), int(yy),
                                         cap_w, cap_h),
                             border_radius=max(1, int(r * 0.04)))

    # Stepped plinth — two stacked blocks so the obelisk stands on real masonry.
    for w_f, h_f, y_off in ((0.98, 0.16, 0.0), (0.70, 0.15, 0.15)):
        bw = r * w_f
        bh = r * h_f
        pygame.draw.rect(surf, col,
                         (int(cx - bw / 2), int(base_y - (y_off + h_f) * r),
                          int(bw), int(bh)),
                         border_radius=max(1, int(r * 0.03)))

    # The tapering obelisk shaft — clearly the tallest, heaviest mass.
    shaft_top = cy - r * 0.62
    bw_bot, bw_top = r * 0.40, r * 0.22
    plinth_top = base_y - r * 0.31
    shaft = [
        (cx - bw_bot / 2, plinth_top),
        (cx - bw_top / 2, shaft_top),
        (cx + bw_top / 2, shaft_top),
        (cx + bw_bot / 2, plinth_top),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in shaft])
    # Pyramidion cap.
    pygame.draw.polygon(surf, col, [
        (int(cx - bw_top / 2), int(shaft_top)),
        (int(cx), int(shaft_top - r * 0.22)),
        (int(cx + bw_top / 2), int(shaft_top))])

    # The victory star crowning the apex, lifted clear on a short neck.
    sy = shaft_top - r * 0.58
    _star(surf, cx, sy, r * 0.40, col)


# ═══════════════════════════════════════════════════════════════════════════
# 2 — quad_digits — Reach a score of 1,000.
#     Beyond score_500's three chevrons: FOUR chevrons climbing up-right, capped
#     by a small burst — "quadruple digits".
# ═══════════════════════════════════════════════════════════════════════════

def _draw_chevron(surf, cx, apex_y, half_w, thick, col):
    drop = half_w * 0.60
    outer = [
        (cx - half_w, apex_y + drop),
        (cx, apex_y),
        (cx + half_w, apex_y + drop),
        (cx + half_w - thick * 0.5, apex_y + drop + thick * 0.72),
        (cx, apex_y + thick),
        (cx - half_w + thick * 0.5, apex_y + drop + thick * 0.72),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in outer])


def _glyph_quad_digits(surf, cx, cy, r, col):
    n = 4
    half_w = r * 0.56
    thick = max(2, int(r * 0.13))     # ~30% slimmer so it reads as an ascent,
    step = r * 0.36                   # not a stack of chunky sergeant stripes
    top_apex = cy - (n - 1) * step / 2 - r * 0.02
    top_ax = None
    for i in range(n):
        ax = cx + (i - (n - 1) / 2) * r * 0.12
        ay = top_apex + (n - 1 - i) * step
        _draw_chevron(surf, ax, ay, half_w, thick, col)
        if i == n - 1:
            top_ax = ax
    # A BIG score-explosion burst blazing off the top chevron — enlarged so the
    # motif reads as a number blowing past a milestone, not rank insignia. Long
    # rays + a fat core, kept clear above the top chevron.
    bx, by = top_ax, top_apex - r * 0.60
    for i in range(8):
        a = i * math.pi / 4
        long_ray = i % 2 == 0
        r_in = r * 0.14
        r_out = r * (0.62 if long_ray else 0.42)
        x1 = bx + math.cos(a) * r_in
        y1 = by + math.sin(a) * r_in
        x2 = bx + math.cos(a) * r_out
        y2 = by + math.sin(a) * r_out
        pygame.draw.line(surf, col, (int(x1), int(y1)), (int(x2), int(y2)),
                         max(2, int(r * 0.10)))
    pygame.draw.circle(surf, col, (int(bx), int(by)), max(4, int(r * 0.19)))


# ═══════════════════════════════════════════════════════════════════════════
# 3 — weeklong_bender — Survive seven full day cycles in one run.
#     Beyond day_three's three moons: a half-sun on the horizon crowned by an ARC
#     of SEVEN identical moon discs — a whole week of nights.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_weeklong_bender(surf, cx, cy, r, col):
    horizon_y = cy + r * 0.66
    sun_r = r * 0.34
    sun_cx = cx
    # Half-sun dome on the horizon.
    fan = [(sun_cx + sun_r, horizon_y)]
    for k in range(13):
        a = math.pi * k / 12
        fan.append((sun_cx + math.cos(a) * sun_r,
                    horizon_y - math.sin(a) * sun_r))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in fan])
    for k in range(5):
        a = math.pi * (k + 0.5) / 5
        x1 = sun_cx + math.cos(a) * sun_r * 1.30
        y1 = horizon_y - math.sin(a) * sun_r * 1.30
        x2 = sun_cx + math.cos(a) * sun_r * 1.62
        y2 = horizon_y - math.sin(a) * sun_r * 1.62
        pygame.draw.line(surf, col, (int(x1), int(y1)), (int(x2), int(y2)),
                         max(2, int(r * 0.08)))
    # Horizon line.
    pygame.draw.line(surf, col, (int(cx - r * 1.0), int(horizon_y)),
                     (int(cx + r * 1.0), int(horizon_y)), max(2, int(r * 0.10)))

    # FOUR big, unmistakable crescent moons arcing over the sun — a small count
    # of LARGE phases survives the 44px shrink where seven tiny discs smeared into
    # a dotted blur. Each is a fat disc carved to a clean crescent by an offset
    # inset bite; the arc of nights is the "seven day-cycles" read.
    arc_cx, arc_cy = cx, cy + r * 0.66
    arc_r = r * 1.10
    moon_r = r * 0.24
    for i in range(4):
        ang = math.radians(150 - i * (120 / 3))     # 150° .. 30°, evenly spaced
        mx = arc_cx + math.cos(ang) * arc_r
        my = arc_cy - math.sin(ang) * arc_r
        pygame.draw.circle(surf, col, (int(mx), int(my)), int(moon_r))
        # a big offset inset bite carves each fat disc into a clear crescent.
        pygame.draw.circle(surf, ai._GLYPH_SH,
                           (int(mx + moon_r * 0.44), int(my - moon_r * 0.20)),
                           int(moon_r * 0.80))


# ═══════════════════════════════════════════════════════════════════════════
# 4 — purist — Reach 100 pillars without touching a power-up.
#     A serene HALO ringing an untouched four-point sparkle, with one gentle
#     prohibition slash — restraint / purity: the power-up left alone.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_purist(surf, cx, cy, r, col):
    # The untouched power-up: a four-point sparkle, drawn hollow (an outline)
    # rather than solid — it was never taken.
    star = _sparkle_pts(cx, cy, r * 0.62, waist=0.30, reach=0.94)
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in star],
                        max(3, int(r * 0.13)))
    # A serene halo ring floating around it — the purity crown.
    halo_r = int(r * 0.92)
    pygame.draw.circle(surf, col, (cx, cy), halo_r, max(3, int(r * 0.11)))
    # One gentle diagonal restraint slash across the ring — "not touched".
    d = halo_r * 0.90
    a = math.radians(-38)
    dx, dy = math.cos(a) * d, math.sin(a) * d
    pygame.draw.line(surf, col, (int(cx - dx), int(cy - dy)),
                     (int(cx + dx), int(cy + dy)), max(3, int(r * 0.12)))


# ═══════════════════════════════════════════════════════════════════════════
# 5 — millionaire — Collect 1,000,000 coins all-time.
#     Beyond Midas: the fat round MONEY BAG stamped with a bold $, crowned as the
#     wealth apex, radiant, with loose coins spilling at its foot.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_millionaire(surf, cx, cy, r, col):
    by = cy + r * 0.18                      # belly centre
    bw = r * 0.94                           # bag half-width
    bh = r * 0.86                           # bag half-height
    # The fat round sack body — a wide-bottomed bag narrowing to a tied neck.
    body = [
        (cx - bw * 0.40, by - bh * 0.44),   # neck left
        (cx - bw, by + bh * 0.18),          # bulge left
        (cx - bw * 0.66, by + bh),          # base left
        (cx + bw * 0.66, by + bh),          # base right
        (cx + bw, by + bh * 0.18),          # bulge right
        (cx + bw * 0.40, by - bh * 0.44),   # neck right
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in body])
    # Cinched neck band + flared drawstring ears.
    neck = pygame.Rect(int(cx - bw * 0.46), int(by - bh * 0.66),
                       int(bw * 0.92), max(4, int(bh * 0.26)))
    pygame.draw.rect(surf, col, neck, border_radius=max(2, int(r * 0.10)))
    # Short drawstring ears tucked close to the neck so they don't compete with
    # the crown that sits above.
    for sgn in (-1, 1):
        pygame.draw.line(surf, col,
                         (int(cx + sgn * bw * 0.22), int(by - bh * 0.58)),
                         (int(cx + sgn * bw * 0.40), int(by - bh * 0.80)),
                         max(3, int(r * 0.10)))
    # The bold $ stamped into the bag's belly (inset so it reads struck-in).
    _dollar(surf, cx, by + bh * 0.30, r * 0.94, ai._GLYPH_SH)
    # A small engraved CROWN centered ATOP the bag — the wealth-apex marker that
    # sets Millionaire apart from the Midas/coin family. A solid base band + three
    # ball-tipped points, lifted clear above the neck with a gap so it reads as a
    # distinct crown, not lost in the drawstring.
    cw = r * 0.46                       # crown half-width
    cby = by - bh * 1.02                # crown base line, clear above the bag
    ch = r * 0.30
    crown = [
        (cx - cw, cby),
        (cx - cw, cby - ch * 0.40),
        (cx - cw * 0.5, cby - ch * 0.05),
        (cx, cby - ch),
        (cx + cw * 0.5, cby - ch * 0.05),
        (cx + cw, cby - ch * 0.40),
        (cx + cw, cby),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in crown])
    pygame.draw.rect(surf, col, (int(cx - cw), int(cby - ch * 0.02),
                                 int(cw * 2), max(3, int(r * 0.12))),
                     border_radius=max(1, int(r * 0.04)))
    for px, ptip in ((-cw, ch * 0.40), (0.0, ch), (cw, ch * 0.40)):
        pygame.draw.circle(surf, col, (int(cx + px), int(cby - ptip)),
                           max(2, int(r * 0.07)))
    # Loose coins spilling at the foot, lower-right (the overflow of a million).
    for dx, dy, sc in ((0.70, 1.02, 0.24), (0.98, 0.84, 0.18)):
        nx, ny = cx + int(r * dx), cy + int(r * dy)
        nr = max(4, int(r * sc))
        pygame.draw.circle(surf, ai._GLYPH_SH, (nx + 1, ny + 1), nr)
        pygame.draw.circle(surf, col, (nx, ny), nr)
        pygame.draw.circle(surf, ai._GLYPH_SH, (nx, ny), nr, max(1, nr // 3))


# ═══════════════════════════════════════════════════════════════════════════
# 6 — power_overwhelming — Collect 2,500 power-ups all-time.
#     A dominant four-point sparkle OVERCHARGED with four radiating lightning
#     bolts — raw power spilling out of the star.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_power_overwhelming(surf, cx, cy, r, col):
    # THREE thick, radially-symmetric zig-zag bolts fired out at 120° (points up,
    # lower-left, lower-right) so the silhouette stays a clean three-pronged power
    # star instead of collapsing into diagonal noise. Drawn FIRST so the central
    # sparkle overlaps their roots (power radiates FROM the star).
    for k in range(3):
        a = math.radians(-90 + k * 120)
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux                    # across-bolt normal for the zig-zag
        r0, r1, r2 = r * 0.40, r * 0.76, r * 1.12
        bolt = [
            (cx + ux * r0 + px * r * 0.16, cy + uy * r0 + py * r * 0.16),
            (cx + ux * r1 + px * r * 0.28, cy + uy * r1 + py * r * 0.28),
            (cx + ux * r1 - px * r * 0.02, cy + uy * r1 - py * r * 0.02),
            (cx + ux * r2, cy + uy * r2),
            (cx + ux * r1 - px * r * 0.30, cy + uy * r1 - py * r * 0.30),
            (cx + ux * r1 + px * r * 0.02, cy + uy * r1 + py * r * 0.02),
            (cx + ux * r0 - px * r * 0.16, cy + uy * r0 - py * r * 0.16),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in bolt])
    # The dominant overcharged sparkle at the core.
    _sparkle(surf, cx, cy, r * 0.72, col, waist=0.32, reach=0.90)
    # A LARGER saturated gold overcharge core (unlock-only) so the centre anchors
    # the star and the whole reads as one overcharged emblem.
    core = ai._accent((255, 214, 92))
    pygame.draw.circle(surf, core, (cx, cy), max(4, int(r * 0.24)))


# ═══════════════════════════════════════════════════════════════════════════
# 7 — overachiever — Collect 20 power-ups in one run.
#     An ARMFUL: two forearms cradling a heaped, overflowing pile of sparkles —
#     more than you can hold.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_overachiever(surf, cx, cy, r, col):
    # The cradle — a thick bowl arc across the bottom, with two short forearm
    # stubs angling up off its ends so it reads as a held armful, not a cup.
    bowl_cy = cy + r * 0.46
    bowl_r = r * 0.86
    rect = pygame.Rect(int(cx - bowl_r), int(bowl_cy - bowl_r),
                       int(bowl_r * 2), int(bowl_r * 2))
    pygame.draw.arc(surf, col, rect, math.radians(200), math.radians(340),
                    max(5, int(r * 0.20)))
    for sgn in (-1, 1):
        ex = cx + sgn * bowl_r * 0.94
        ey = bowl_cy - bowl_r * 0.34
        pygame.draw.line(surf, col, (int(ex), int(ey)),
                         (int(ex + sgn * r * 0.30), int(ey - r * 0.34)),
                         max(5, int(r * 0.19)))

    # A heaped pile of sparkles overflowing the cradle — one big in the middle,
    # smaller ones packed around and spilling above the rim.
    heap = [
        (cx, cy - r * 0.02, 0.52),          # dominant centre
        (cx - r * 0.52, cy + r * 0.10, 0.34),
        (cx + r * 0.52, cy + r * 0.10, 0.34),
        (cx - r * 0.24, cy - r * 0.52, 0.30),
        (cx + r * 0.28, cy - r * 0.50, 0.30),
        (cx, cy - r * 0.86, 0.26),          # one tumbling off the top
    ]
    for sx, sy, sc in heap:
        # a dark gap-halo behind each so the pile never fuses into one blob
        pygame.draw.circle(surf, ai._GLYPH_SH, (int(sx), int(sy)),
                           max(3, int(r * sc * 0.92)))
        _sparkle(surf, sx, sy, r * sc, col)


# ═══════════════════════════════════════════════════════════════════════════
# 8 — kitchen_sink — Use all six power-ups in one run.
#     The pun made literal: a gooseneck FAUCET pouring over a BASIN, with six
#     little power-up pips collected in the bowl — everything but the kitchen
#     sink, in the sink.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_kitchen_sink(surf, cx, cy, r, col):
    rim_y = cy + r * 0.12
    # Basin: a flat rim slab over a tapered bowl.
    rim = pygame.Rect(int(cx - r * 0.92), int(rim_y - r * 0.12),
                      int(r * 1.84), max(4, int(r * 0.20)))
    pygame.draw.rect(surf, col, rim, border_radius=max(2, int(r * 0.06)))
    bowl = [
        (cx - r * 0.80, rim_y + r * 0.08),
        (cx + r * 0.80, rim_y + r * 0.08),
        (cx + r * 0.52, rim_y + r * 0.86),
        (cx - r * 0.52, rim_y + r * 0.86),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in bowl])
    # Hollow out the bowl interior (inset tone) so the pips sit INSIDE it.
    inner = [
        (cx - r * 0.66, rim_y + r * 0.16),
        (cx + r * 0.66, rim_y + r * 0.16),
        (cx + r * 0.44, rim_y + r * 0.74),
        (cx - r * 0.44, rim_y + r * 0.74),
    ]
    pygame.draw.polygon(surf, ai._GLYPH_SH, [(int(x), int(y)) for x, y in inner])

    # Gooseneck faucet rising from the right, arcing over the basin's centre.
    pipe_w = max(4, int(r * 0.15))
    stem_x = cx + r * 0.66
    pygame.draw.line(surf, col, (int(stem_x), int(rim_y - r * 0.04)),
                     (int(stem_x), int(cy - r * 0.62)), pipe_w)
    neck = pygame.Rect(int(cx - r * 0.10), int(cy - r * 0.92),
                       int((stem_x - (cx - r * 0.10)) * 2), int(r * 0.60))
    pygame.draw.arc(surf, col, neck, math.radians(30), math.radians(178),
                    pipe_w)
    # spout dropping at the arc's left end
    spout_x = cx - r * 0.10
    pygame.draw.line(surf, col, (int(spout_x), int(cy - r * 0.62)),
                     (int(spout_x), int(cy - r * 0.40)), pipe_w)
    # a handle nub on the stem
    pygame.draw.line(surf, col, (int(stem_x), int(cy - r * 0.30)),
                     (int(stem_x + r * 0.26), int(cy - r * 0.30)),
                     max(3, int(r * 0.11)))

    # Six little power-up pips collected in the bowl (all six used), plus one
    # sparkle droplet mid-fall from the spout so the faucet reads as pouring
    # power-ups in.
    _sparkle(surf, spout_x, cy - r * 0.20, r * 0.20, col)
    pip_r = max(3, int(r * 0.115))
    pip_row = [(-0.40, 0.42), (0.0, 0.36), (0.40, 0.42),
               (-0.22, 0.66), (0.22, 0.66), (0.0, 0.60)]
    for fx, fy in pip_row:
        _sparkle(surf, cx + fx * r, rim_y + fy * r, pip_r * 1.0, col)


# ═══════════════════════════════════════════════════════════════════════════
# 9 — endless — Stay airborne for ten minutes straight.
#     An INFINITY loop threaded with a macaw WING — endless flight.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_endless(surf, cx, cy, r, col):
    # The lemniscate: two thick tangent rings crossing at centre = ∞.
    loop_cy = cy + r * 0.14
    ring_r = int(r * 0.44)
    ring_w = max(4, int(r * 0.20))
    off = int(r * 0.44)
    for sgn in (-1, 1):
        pygame.draw.circle(surf, col, (cx + sgn * off, loop_cy), ring_r, ring_w)
    # A small crossover diamond where the loops meet, so the centre reads as a
    # true infinity knot rather than two touching O's.
    kx, ky = cx, loop_cy
    ks = r * 0.20
    pygame.draw.polygon(surf, col, [
        (int(kx), int(ky - ks)), (int(kx + ks), int(ky)),
        (int(kx), int(ky + ks)), (int(kx - ks), int(ky))])

    # A bold macaw wing swept up off the upper-right loop — the flight that never
    # lands. Bigger, with a strong convex leading edge and a three-lobe trailing
    # scallop so it reads clearly as a WING against the ∞, not a stray tail.
    sx, sy = cx + off * 0.55, loop_cy - ring_r * 0.78     # shoulder on the loop
    tx, ty = cx + r * 1.06, cy - r * 0.98                 # wing tip
    lebx, leby = cx + r * 0.52, cy - r * 1.12             # camber control point
    leading = []
    for i in range(9):
        t = i / 8
        mt = 1 - t
        bx = mt * mt * sx + 2 * mt * t * lebx + t * t * tx
        byy = mt * mt * sy + 2 * mt * t * leby + t * t * ty
        leading.append((bx, byy))
    lobes = [
        (cx + r * 0.82, cy - r * 0.40),
        (cx + r * 0.54, cy - r * 0.30),
        (cx + r * 0.30, cy - r * 0.26),
        (sx, sy + ring_r * 0.30),
    ]
    pygame.draw.polygon(surf, col,
                        [(int(x), int(y)) for x, y in leading + lobes])


GLYPHS = {
    "sky_legend": _glyph_sky_legend,
    "quad_digits": _glyph_quad_digits,
    "weeklong_bender": _glyph_weeklong_bender,
    "purist": _glyph_purist,
    "millionaire": _glyph_millionaire,
    "power_overwhelming": _glyph_power_overwhelming,
    "overachiever": _glyph_overachiever,
    "kitchen_sink": _glyph_kitchen_sink,
    "endless": _glyph_endless,
}
