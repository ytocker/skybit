"""
Bespoke engraved center glyphs for BATCH 3 of the Hall-of-Fame emblems
(GOLD tone) — nine calendar / milestone / "you never gave up" achievements.

Authored in the single-colour engrave idiom of ``game.achievement_icons``: each
``_glyph_<id>(surf, cx, cy, r, col)`` lays BOLD filled polygons / thick lines /
discs in the passed ``col`` only, so the builder's dark inset pass (down-right) +
up-left sheen give every glyph the same struck-metal relief. Recessed detail
(eye pupils, gear hubs, calendar field) is cut in ``_GLYPH_SH`` so it reads as an
engraved indent, and the three "fire" motifs (candle flame, firework sparks,
phoenix embers) route a warm accent through ``_accent`` so the heat reads on an
earned medal yet desaturates to bronze while the badge is dormant.

Every shape is sized for the ~20px glyph well inside the wreath: nothing thinner
than ~3px, no numerals — the SILHOUETTE carries each read (owl+moon, sun+bird,
leaping frog, firework, trophy, cake, calendar, meshing gears, phoenix).

WRITE-ONLY exploration module under ``tools/`` — it imports ``game`` read-only;
the sibling render harness merges ``GLYPHS`` into a private copy of the badge
glyph table so nothing in the live game is touched.
"""
from __future__ import annotations

import math
import pygame

from game.achievement_icons import _GLYPH_SH, _accent

# Warm ember accent — essentially gold, so it never out-saturates the family's
# "gold = earned" rule, but gives the three fire motifs a live glow.
_EMBER = (255, 196, 92)


# ── shared primitives ────────────────────────────────────────────────────────

def _star(surf, cx, cy, r, col, points=4, inner=0.42):
    # A pointed star burst (default 4-point twinkle); ``points`` bumps it to a
    # 5-point award star for the trophy.
    pts = []
    n = points * 2
    for i in range(n):
        ang = -math.pi / 2 + i * math.pi / points
        rad = r if i % 2 == 0 else r * inner
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _flame(surf, cx, base_y, w, h, col):
    # A teardrop flame lick: a pointed top over a rounded belly, drawn as a
    # polygon so it stays crisp when embossed.
    pts = [
        (cx, base_y - h),                    # tip
        (cx + w * 0.62, base_y - h * 0.42),
        (cx + w, base_y - h * 0.02),
        (cx + w * 0.5, base_y + h * 0.10),
        (cx - w * 0.5, base_y + h * 0.10),
        (cx - w, base_y - h * 0.02),
        (cx - w * 0.62, base_y - h * 0.42),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _gear(surf, gcx, gcy, r_out, teeth, col):
    # A cog: a body disc ringed by trapezoidal teeth, with a bored hub. The hub
    # is cut in the inset tone so the wheel reads as a machined gear, not a sun.
    rb = r_out * 0.74
    half = math.pi / teeth * 0.52          # angular half-width of a tooth
    for i in range(teeth):
        a = i * math.tau / teeth
        pts = []
        for da, rad in ((-half, rb), (-half * 0.62, r_out),
                        (half * 0.62, r_out), (half, rb)):
            pts.append((gcx + math.cos(a + da) * rad, gcy + math.sin(a + da) * rad))
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])
    pygame.draw.circle(surf, col, (int(gcx), int(gcy)), int(rb))
    # bored hub — a dark ring + open core so the cog reads at chip size
    pygame.draw.circle(surf, _GLYPH_SH, (int(gcx), int(gcy)), int(r_out * 0.34))
    pygame.draw.circle(surf, col, (int(gcx), int(gcy)), int(r_out * 0.34),
                       max(2, int(r_out * 0.12)))


# ═══════════════════════════════════════════════════════════════════════════
# 1. after_hours — Night Owl: a serene perched owl beneath a crescent moon + a
#    star. Two calm round eyes (bright iris + dark pupil) are the read — the
#    heroic counterpart to the shame reel's X-eyed owl.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_after_hours(surf, cx, cy, r, col):
    # Crescent moon, upper-right: a lit disc bitten by an offset inset disc so a
    # true crescent opens down toward the owl. Kept bold so it survives at 44px.
    mx, my = cx + int(r * 0.50), cy - int(r * 0.56)
    rm = int(r * 0.36)
    pygame.draw.circle(surf, col, (mx, my), rm)
    pygame.draw.circle(surf, _GLYPH_SH, (mx + int(rm * 0.60), my - int(rm * 0.28)),
                       int(rm * 1.02))
    # a small four-point star, upper-left
    _star(surf, cx - int(r * 0.54), cy - int(r * 0.50), int(r * 0.22), col)

    # Owl body — a rounded pear filling the lower well.
    ocy = cy + int(r * 0.30)
    bw, bh = int(r * 1.16), int(r * 1.46)
    pygame.draw.ellipse(surf, col, (cx - bw // 2, ocy - bh // 2, bw, bh))
    top = ocy - bh // 2
    # two ear tufts poking off the crown
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.40)
        pygame.draw.polygon(surf, col, [
            (ex - int(r * 0.06), top + int(r * 0.18)),
            (ex + sgn * int(r * 0.20), top - int(r * 0.20)),
            (ex + int(r * 0.14), top + int(r * 0.18)),
        ])
    # two big calm eyes: dark socket, bright iris disc, dark pupil
    for sgn in (-1, 1):
        exc = cx + sgn * int(r * 0.30)
        eyc = cy - int(r * 0.02)
        pygame.draw.circle(surf, _GLYPH_SH, (exc, eyc), int(r * 0.27))
        pygame.draw.circle(surf, col, (exc, eyc), int(r * 0.18))
        pygame.draw.circle(surf, _GLYPH_SH, (exc, eyc), int(r * 0.075))
    # small beak between/under the eyes
    pygame.draw.polygon(surf, _GLYPH_SH, [
        (cx - int(r * 0.09), cy + int(r * 0.12)),
        (cx + int(r * 0.09), cy + int(r * 0.12)),
        (cx, cy + int(r * 0.32)),
    ])
    # folded-wing fold lines curving down the flanks
    for sgn in (-1, 1):
        pts = [(cx + sgn * int(r * 0.40), cy + int(r * 0.18)),
               (cx + sgn * int(r * 0.46), cy + int(r * 0.52)),
               (cx + sgn * int(r * 0.30), cy + int(r * 0.86))]
        pygame.draw.lines(surf, _GLYPH_SH, False, pts, max(2, r // 12))
    # two little feet gripping a short perch branch
    perch_y = ocy + bh // 2 - int(r * 0.02)
    for sgn in (-1, 1):
        fx = cx + sgn * int(r * 0.16)
        pygame.draw.line(surf, col, (fx, perch_y - int(r * 0.02)),
                         (fx, perch_y + int(r * 0.16)), max(3, r // 11))
    pygame.draw.line(surf, col, (cx - int(r * 0.42), perch_y + int(r * 0.16)),
                     (cx + int(r * 0.42), perch_y + int(r * 0.16)), max(3, r // 11))


# ═══════════════════════════════════════════════════════════════════════════
# 2. early_bird — a small bird in flight over a rising half-sun on the horizon,
#    dawn rays fanning up. The bird is what parts it from the day-cycle family.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_early_bird(surf, cx, cy, r, col):
    # A BOLD perched songbird is the focal point, sitting on a twig in front of a
    # rising-sun DISC (a full circle, not a dome, so it never reads as a hill).
    # The bird is what makes the badge say "early BIRD", not "sunny landscape".
    horizon_y = cy + int(r * 0.70)
    sun_cx, sun_cy = cx + int(r * 0.04), cy - int(r * 0.06)
    sun_r = int(r * 0.42)
    pygame.draw.circle(surf, col, (sun_cx, sun_cy), sun_r)
    # thin radial dawn rays — kept slim + clearly separated so they read as light,
    # never as mountain peaks
    for k in range(10):
        a = k * math.tau / 10 - math.radians(90)
        x1 = sun_cx + math.cos(a) * sun_r * 1.24
        y1 = sun_cy + math.sin(a) * sun_r * 1.24
        x2 = sun_cx + math.cos(a) * sun_r * 1.60
        y2 = sun_cy + math.sin(a) * sun_r * 1.60
        pygame.draw.line(surf, col, (int(x1), int(y1)), (int(x2), int(y2)),
                         max(2, int(r * 0.08)))
    # horizon / perch twig
    pygame.draw.line(surf, col, (cx - int(r * 0.86), horizon_y),
                     (cx + int(r * 0.86), horizon_y), max(3, int(r * 0.11)))

    # The bird: a plump robin perched facing right, big enough to own the well.
    # Every part is drawn first in the inset tone at a slight outset (a dark
    # halo) so the gold bird separates cleanly from the gold sun behind it.
    bcx, bcy = cx - int(r * 0.06), cy + int(r * 0.20)
    hx, hy = bcx + int(r * 0.40), bcy - int(r * 0.36)
    body = pygame.Rect(int(bcx - r * 0.46), int(bcy - r * 0.40),
                       int(r * 0.92), int(r * 0.80))
    tail = [(bcx - int(r * 0.30), bcy - int(r * 0.06)),
            (bcx - int(r * 0.86), bcy - int(r * 0.46)),
            (bcx - int(r * 0.70), bcy - int(r * 0.02)),
            (bcx - int(r * 0.34), bcy + int(r * 0.22))]
    beak = [(hx + int(r * 0.16), hy - int(r * 0.06)),
            (hx + int(r * 0.52), hy + int(r * 0.02)),
            (hx + int(r * 0.16), hy + int(r * 0.12))]

    def _bird(fill, grow):
        pygame.draw.ellipse(surf, fill, body.inflate(grow, grow))
        pygame.draw.circle(surf, fill, (hx, hy), int(r * 0.28) + grow // 2)
        pygame.draw.polygon(surf, fill, [(int(x), int(y)) for x, y in tail])
        pygame.draw.polygon(surf, fill, [(int(x), int(y)) for x, y in beak])

    _bird(_GLYPH_SH, int(r * 0.14))     # separating halo against the sun disc
    _bird(col, 0)
    # eye + a folded-wing groove so the perched bird reads at chip size
    pygame.draw.circle(surf, _GLYPH_SH, (hx + int(r * 0.06), hy - int(r * 0.04)),
                       max(2, int(r * 0.06)))
    pygame.draw.lines(surf, _GLYPH_SH, False, [
        (bcx + int(r * 0.02), bcy - int(r * 0.18)),
        (bcx - int(r * 0.10), bcy + int(r * 0.04)),
        (bcx + int(r * 0.14), bcy + int(r * 0.10)),
    ], max(2, int(r * 0.08)))
    # two legs down to the perch
    for sgn in (-1, 1):
        lx = bcx + sgn * int(r * 0.12)
        pygame.draw.line(surf, col, (lx, bcy + int(r * 0.36)), (lx, horizon_y),
                         max(2, int(r * 0.07)))


# ═══════════════════════════════════════════════════════════════════════════
# 3. leap_of_faith — a frog coiled to launch, viewed head-on on a baseline:
#    eyes up, two big bent haunches symmetric about the body, feet planted. The
#    coiled-spring crouch is the read that holds at chip size (the leap-year pun).
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_leap_of_faith(surf, cx, cy, r, col):
    base_y = cy + int(r * 0.74)
    # the ground the frog pushes off — anchors the pose so no leg floats free
    pygame.draw.line(surf, col, (cx - int(r * 0.80), base_y),
                     (cx + int(r * 0.80), base_y), max(3, int(r * 0.10)))

    bcx, bcy = cx, cy + int(r * 0.16)
    # TWO bent hind legs, symmetric — raised knees flared out to each side, shins
    # driving down to planted feet on the baseline. The M of the coiled haunches
    # is drawn before the body so the body caps the hips cleanly.
    lw_leg = max(5, int(r * 0.20))
    for sgn in (-1, 1):
        hip = (bcx + sgn * int(r * 0.26), bcy + int(r * 0.02))
        knee = (bcx + sgn * int(r * 0.66), bcy - int(r * 0.30))   # raised knee
        foot = (bcx + sgn * int(r * 0.52), base_y)
        pygame.draw.lines(surf, col, False, [hip, knee, foot], lw_leg)
        # webbed foot fan planted on the baseline
        for da in (-0.45, 0.0, 0.45):
            tx = foot[0] + int(math.sin(da) * r * 0.20) + sgn * int(r * 0.06)
            pygame.draw.line(surf, col, foot, (tx, base_y - int(r * 0.16)),
                             max(2, int(r * 0.08)))

    # body — a broad rounded crouch
    body = pygame.Rect(int(bcx - r * 0.46), int(bcy - r * 0.34),
                       int(r * 0.92), int(r * 0.66))
    pygame.draw.ellipse(surf, col, body)
    # two front feet planted under the chin
    for sgn in (-1, 1):
        fx = bcx + sgn * int(r * 0.14)
        pygame.draw.line(surf, col, (fx, bcy + int(r * 0.26)), (fx, base_y),
                         max(3, int(r * 0.09)))

    # two big bulging eyes riding the top of the head — the unmistakable frog cue
    for sgn in (-1, 1):
        ex, ey = bcx + sgn * int(r * 0.24), bcy - int(r * 0.40)
        pygame.draw.circle(surf, col, (ex, ey), int(r * 0.20))
        pygame.draw.circle(surf, _GLYPH_SH, (ex, ey), int(r * 0.09))
    # wide smile line so the crouch reads as a face-on frog
    pygame.draw.arc(surf, _GLYPH_SH,
                    (int(bcx - r * 0.34), int(bcy - r * 0.18),
                     int(r * 0.68), int(r * 0.44)),
                    math.radians(200), math.radians(340), max(2, int(r * 0.08)))
    # a pair of upward push-off ticks — the launch impulse
    for sgn in (-1, 1):
        ax = bcx + sgn * int(r * 0.60)
        pygame.draw.line(surf, col, (ax, bcy - int(r * 0.52)),
                         (ax, bcy - int(r * 0.74)), max(2, int(r * 0.08)))


# ═══════════════════════════════════════════════════════════════════════════
# 4. auld_lang_syne — New Year's Day: a firework burst mid-bloom with spark-tip
#    rays + a launch trail rising from below and a small second burst. Warm
#    ember accents on the spark tips.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_auld_lang_syne(surf, cx, cy, r, col):
    ember = _accent(_EMBER)

    def burst(bcx, bcy, rad, n, rot):
        for i in range(n):
            a = rot + i * math.tau / n
            x1 = bcx + math.cos(a) * rad * 0.30
            y1 = bcy + math.sin(a) * rad * 0.30
            x2 = bcx + math.cos(a) * rad
            y2 = bcy + math.sin(a) * rad
            pygame.draw.line(surf, col, (int(x1), int(y1)), (int(x2), int(y2)),
                             max(2, int(r * 0.08)))
            pygame.draw.circle(surf, ember, (int(x2), int(y2)),
                               max(2, int(rad * 0.16)))
        pygame.draw.circle(surf, col, (int(bcx), int(bcy)), max(2, int(rad * 0.14)))

    # launch trail curving up to the main burst, with two rising spark dots
    trail = [
        (cx - int(r * 0.22), cy + int(r * 0.92)),
        (cx - int(r * 0.02), cy + int(r * 0.42)),
        (cx + int(r * 0.08), cy - int(r * 0.06)),
    ]
    pygame.draw.lines(surf, col, False, trail, max(2, int(r * 0.07)))
    for tx, ty in ((cx - int(r * 0.12), cy + int(r * 0.66)),
                   (cx + int(r * 0.02), cy + int(r * 0.24))):
        pygame.draw.circle(surf, ember, (tx, ty), max(2, int(r * 0.06)))

    # main burst, upper-centre + a smaller companion lower-left
    burst(cx + int(r * 0.10), cy - int(r * 0.30), r * 0.62, 10, math.radians(0))
    burst(cx - int(r * 0.52), cy + int(r * 0.18), r * 0.30, 8, math.radians(22))


# ═══════════════════════════════════════════════════════════════════════════
# 5. the_completionist — the capstone: a grand two-handled trophy cup crowned by
#    an award star, engraved with a second star on its bowl.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_the_completionist(surf, cx, cy, r, col):
    rim_y = cy - int(r * 0.34)
    bowl_bot = cy + int(r * 0.18)
    # handles — two open C-loops springing off the bowl shoulders
    for sgn in (-1, 1):
        hrect = pygame.Rect(int(cx + sgn * r * 0.46 - r * 0.24),
                            int(rim_y - r * 0.02), int(r * 0.48), int(r * 0.52))
        if sgn < 0:
            pygame.draw.arc(surf, col, hrect, math.radians(40), math.radians(320),
                            max(3, int(r * 0.13)))
        else:
            pygame.draw.arc(surf, col, hrect, math.radians(-140), math.radians(140),
                            max(3, int(r * 0.13)))
    # bowl — a rounded cup narrowing to the stem
    bowl = [
        (cx - int(r * 0.52), rim_y),
        (cx + int(r * 0.52), rim_y),
        (cx + int(r * 0.30), bowl_bot),
        (cx - int(r * 0.30), bowl_bot),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in bowl])
    # rim cap ellipse so the cup reads open at the top
    pygame.draw.ellipse(surf, col, (cx - int(r * 0.56), rim_y - int(r * 0.11),
                                    int(r * 1.12), int(r * 0.22)))
    pygame.draw.ellipse(surf, _GLYPH_SH, (cx - int(r * 0.44), rim_y - int(r * 0.07),
                                          int(r * 0.88), int(r * 0.14)))
    # stem + tiered base
    pygame.draw.rect(surf, col, (cx - int(r * 0.09), bowl_bot,
                                 int(r * 0.18), int(r * 0.22)))
    pygame.draw.rect(surf, col, (cx - int(r * 0.24), cy + int(r * 0.36),
                                 int(r * 0.48), int(r * 0.09)),
                     border_radius=max(1, r // 20))
    pygame.draw.rect(surf, col, (cx - int(r * 0.38), cy + int(r * 0.45),
                                 int(r * 0.76), int(r * 0.13)),
                     border_radius=max(1, r // 16))
    # engraved award star on the bowl face
    _star(surf, cx, cy - int(r * 0.06), int(r * 0.20), _GLYPH_SH, points=5, inner=0.45)
    # a small crowning star riding above the rim — the "every badge" capstone
    _star(surf, cx, rim_y - int(r * 0.34), int(r * 0.17), col, points=5, inner=0.45)


# ═══════════════════════════════════════════════════════════════════════════
# 6. many_happy_returns — a birthday cake with a single lit candle on a plate;
#    the anniversary of the first flight. Warm ember flame.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_many_happy_returns(surf, cx, cy, r, col):
    top_y = cy + int(r * 0.06)
    bot_y = cy + int(r * 0.66)
    # cake body
    pygame.draw.rect(surf, col, (cx - int(r * 0.56), top_y,
                                 int(r * 1.12), bot_y - top_y),
                     border_radius=max(2, int(r * 0.10)))
    # icing scallops along the top edge
    scn = 4
    sw = int(r * 1.02) // scn
    for i in range(scn):
        sxc = cx - int(r * 0.51) + sw // 2 + i * sw
        pygame.draw.circle(surf, col, (sxc, top_y), sw // 2 + 1)
    # engraved icing drips under the scallops
    for i in range(scn):
        sxc = cx - int(r * 0.51) + sw + i * sw
        pygame.draw.circle(surf, _GLYPH_SH, (sxc, top_y + int(r * 0.06)),
                           max(2, sw // 4))
    # plate the cake rests on
    pygame.draw.ellipse(surf, col, (cx - int(r * 0.78), bot_y - int(r * 0.02),
                                    int(r * 1.56), int(r * 0.22)))
    # candle rising from the centre
    pygame.draw.rect(surf, col, (cx - int(r * 0.06), cy - int(r * 0.34),
                                 int(r * 0.12), int(r * 0.44)))
    # engraved wick band so the candle reads as wax
    pygame.draw.line(surf, _GLYPH_SH, (cx - int(r * 0.06), cy - int(r * 0.16)),
                     (cx + int(r * 0.06), cy - int(r * 0.16)), max(2, r // 14))
    # ember flame
    _flame(surf, cx, cy - int(r * 0.34), int(r * 0.14), int(r * 0.34),
           _accent(_EMBER))


# ═══════════════════════════════════════════════════════════════════════════
# 7. creature_of_habit — a wall calendar checked off for a full week: two
#    binding rings, a header band, a bold tick stamped across the field, and a
#    row of seven day-pips. Played on seven different days.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_creature_of_habit(surf, cx, cy, r, col):
    px0, py0 = cx - int(r * 0.64), cy - int(r * 0.52)
    pw, ph = int(r * 1.28), int(r * 1.18)
    # binding rings poking above the page
    for sgn in (-1, 1):
        rx = cx + sgn * int(r * 0.30)
        pygame.draw.rect(surf, col, (rx - max(2, r // 16), py0 - int(r * 0.16),
                                     max(4, r // 8), int(r * 0.22)),
                         border_radius=max(1, r // 20))
    # page frame
    pygame.draw.rect(surf, col, (px0, py0, pw, ph),
                     border_radius=max(2, int(r * 0.10)))
    # header band (col) above the dark paper field
    hdr_h = int(r * 0.26)
    field_top = py0 + hdr_h
    pygame.draw.rect(surf, _GLYPH_SH, (px0 + int(r * 0.08), field_top,
                                       pw - int(r * 0.16),
                                       ph - hdr_h - int(r * 0.10)),
                     border_radius=max(1, int(r * 0.05)))
    # bold check stamped across the field — the "done / kept the habit" read
    pygame.draw.lines(surf, col, False, [
        (cx - int(r * 0.34), cy + int(r * 0.14)),
        (cx - int(r * 0.08), cy + int(r * 0.36)),
        (cx + int(r * 0.38), cy - int(r * 0.14)),
    ], max(4, int(r * 0.17)))
    # a row of seven day-pips along the foot — the week
    for i in range(7):
        dx = px0 + int(r * 0.16) + i * (pw - int(r * 0.32)) // 6
        pygame.draw.circle(surf, col, (dx, cy + int(r * 0.46)),
                           max(2, int(r * 0.055)))


# ═══════════════════════════════════════════════════════════════════════════
# 8. the_grind — two meshing gears: the daily grind of 100 runs.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_the_grind(surf, cx, cy, r, col):
    _gear(surf, cx - int(r * 0.28), cy + int(r * 0.18), int(r * 0.64), 9, col)
    _gear(surf, cx + int(r * 0.42), cy - int(r * 0.36), int(r * 0.42), 7, col)


# ═══════════════════════════════════════════════════════════════════════════
# 9. never_say_die — a phoenix rising from the embers: symmetric spread wings,
#    a fanned tail, and ember licks at the base. 1,000 crashes and still flying.
# ═══════════════════════════════════════════════════════════════════════════

def _glyph_never_say_die(surf, cx, cy, r, col):
    # body — an upright teardrop
    pygame.draw.ellipse(surf, col, (cx - int(r * 0.17), cy - int(r * 0.20),
                                    int(r * 0.34), int(r * 0.66)))
    # head + beak lifted heroically
    pygame.draw.circle(surf, col, (cx, cy - int(r * 0.32)), int(r * 0.15))
    pygame.draw.polygon(surf, col, [
        (cx + int(r * 0.10), cy - int(r * 0.40)),
        (cx + int(r * 0.30), cy - int(r * 0.50)),
        (cx + int(r * 0.10), cy - int(r * 0.28)),
    ])
    pygame.draw.circle(surf, _GLYPH_SH, (cx + int(r * 0.04), cy - int(r * 0.34)),
                       max(2, r // 16))
    # two symmetric raised wings with a feathered trailing edge
    for sgn in (-1, 1):
        def X(f):
            return cx + sgn * int(r * f)
        wing = [
            (X(0.10), cy - int(r * 0.06)),   # shoulder
            (X(0.42), cy - int(r * 0.42)),   # leading edge climbing
            (X(0.70), cy - int(r * 0.60)),
            (X(0.96), cy - int(r * 0.60)),   # tip
            (X(0.78), cy - int(r * 0.34)),   # trailing feather lobe
            (X(0.82), cy - int(r * 0.18)),
            (X(0.54), cy - int(r * 0.08)),
            (X(0.58), cy + int(r * 0.08)),
            (X(0.30), cy + int(r * 0.14)),
            (X(0.14), cy + int(r * 0.08)),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in wing])
    # fanned tail dropping from the body
    for f in (-0.20, 0.0, 0.20):
        pygame.draw.line(surf, col, (cx, cy + int(r * 0.42)),
                         (cx + int(r * f), cy + int(r * 0.82)),
                         max(3, int(r * 0.13)))
    # ember licks at the base — the ashes it rises from
    ember = _accent(_EMBER)
    for fx, sc in ((-0.34, 0.72), (0.0, 1.0), (0.34, 0.72)):
        _flame(surf, cx + int(r * fx), cy + int(r * 0.98),
               int(r * 0.13 * sc), int(r * 0.34 * sc), ember)


GLYPHS = {
    "after_hours": _glyph_after_hours,
    "early_bird": _glyph_early_bird,
    "leap_of_faith": _glyph_leap_of_faith,
    "auld_lang_syne": _glyph_auld_lang_syne,
    "the_completionist": _glyph_the_completionist,
    "many_happy_returns": _glyph_many_happy_returns,
    "creature_of_habit": _glyph_creature_of_habit,
    "the_grind": _glyph_the_grind,
    "never_say_die": _glyph_never_say_die,
}
