"""
Round-1 concept renderer for KOSCHEI — the deathless bone-sorcerer enthroned on
a marrow-throne (Citipati-versions set, concept #5). Headless Pygame; ELEVATED
pipeline (supersample SS=6 -> smoothscale) so the extra geometry stays crisp at
downscale. Keeps the shipped house grammar: flat saturated fills, hard 1-2px ink
keyline, dark-core -> flat-fill -> top-left rim-sheen triad, 1px alpha-grown
outline, chibi proportions, scary-CUTE; procedural-only (no gradients/PNGs).

WHY this concept is the anti-dancer: the source Citipati is the ONLY motion
silhouette (cocked-hip flamenco). Koschei is the ONLY ENTHRONED/SEATED mass —
a wide-base block: a skinny sulking skeleton king sunk back into a throne, knees
together, hunched over the one thing he cares about. That low-slung pyramid of
mass reads instantly OFF every upright skull-man and off the dancer.

WHY the bone stays COOL and the egg carries the heat: the body is corpse-tallow
grey-green (cooler/greener than warm parchment, so it can never be mistaken for
Necrarch parchment or the Mariachi warm-bone). With the body desaturated and
receding, the SINGLE warm focal — the poison-chartreuse soul-egg cupped in his
lap — owns all the warmth and the eye. The eye-sockets glow deep INDIGO (not
Draugr/Yurei cyan), a second cool pin that survives day AND night.

WHY the crown is IRON SPIKES, never skulls (the HARD tell): Citipati wears a
5-skull crown and Mukha-Devi a 3-skull tiara. Koschei's tall tomb-crown is
blackened-iron THIN BENT SPIKES — a dark, jagged comb, the opposite read from a
ring of bone domes — so he can never be confused for either at 32px.

WHY the femur-throne-column IS the pillar: stacked PAIRED femurs lashed into a
column (joint banding) tile as the repeatable shaft; the gap-edge cap is a
rib-spire throne-back FAN cradling the soul-egg orb at the gap, glowing —
symmetric, bottom-rooted, never top-heavy.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# -- PINNED PALETTE (locked re-spec brief) -------------------------------------
# Corpse-tallow grey-green bone is the dominant MASS and is deliberately
# DESATURATED + cool so it recedes; the one warm focal is the egg.
BONE      = (190, 192, 158)   # corpse-tallow grey-green bone (dominant fill)
BONE_D    = (146, 130,  92)   # olive-bone shade / dark-core
BONE_DD   = (104,  94,  66)   # deepest bone hollow (rib gaps, joint sockets)
BONE_SH   = (238, 232, 206)   # bone top-left rim-sheen
# the SINGLE warm focal — the cupped soul-egg (poison-chartreuse glow).
# WHY pushed saturation/brightness vs round 1: at 32px the egg was outgunned by
# the indigo eyes and bled into the tallow lap; it must be the brightest, most-
# saturated thing in the figure so the cool body recedes as briefed.
EGG       = (196, 232,  72)   # poison-chartreuse soul-egg body (more saturated)
EGG_BR    = (228, 250, 132)   # hot egg inner glow
EGG_HOT   = (248, 255, 206)   # hottest egg core (lightest)
EGG_D     = (132, 166,  48)   # egg shade
EGG_RIM   = (108, 138,  36)   # egg dark rim (its own crisp keyline, warmer than ink)
# blackened-iron crown + throne frame (the dark structural accent)
IRON      = ( 58,  54,  60)
IRON_BR   = ( 96,  92, 100)   # iron top-left sheen
IRON_D    = ( 34,  32,  38)   # iron dark-core
# deep INDIGO socket pin-glow (a second cool pin, NOT cyan)
INDIGO    = (110, 118, 212)
INDIGO_BR = (176, 182, 244)   # hot indigo pin core
INDIGO_D  = ( 60,  66, 150)
INK       = ( 26,  26,  24)   # hard ink keyline

BG        = ( 96, 100, 108)   # neutral grey review backdrop
PANEL     = ( 74,  78,  88)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (188, 196, 208)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# -- outline grown from the alpha mask (the house keyline) --------------------
def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    pts = mask.outline()
    if len(pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(base, (0, 0))
    return ring


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.4), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    """Round equivalent of triad_blob — dark core bottom-right, sheen top-left."""
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.45),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


def bone_limb(surf, p0, p1, p2, thick, s, joint=True):
    """Two-segment bone limb with ink keyline + bulbous joint (shared helper)."""
    for (a, b) in ((p0, p1), (p1, p2)):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * thick / 2, dx / L * thick / 2
        quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
        triad_blob(surf, BONE, quad,
                   sheen_pts=[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                              (b[0] + nx * 0.3, b[1] + ny * 0.3),
                              (a[0] + nx * 0.3, a[1] + ny * 0.3)],
                   ow=max(1, int(thick * 0.18)))
    if joint:
        triad_circle(surf, BONE, p1, int(thick * 0.62), ow=max(1, int(1.2 * s)),
                     core=False)


# -- the cupped soul-egg (the SINGLE warm focal, reused in figure + pillar cap)-
def egg_socket(surf, cx, cy, r, s):
    """A dark blackened-iron RECESS the egg is set into. WHY drawn first, behind
    the egg: at 32px the chartreuse alone won't separate from the tallow lap —
    the AD ruling is that a hard dark frame on every side is what makes 'held
    object' read at 1×. A full dark cup (taller-than-wide, matching the ovoid)
    gives the egg a high-contrast socket gap on all sides; the cupping thumbs
    then close it from below."""
    sr = int(r * 1.30)
    socket = []
    for k in range(24):
        a = math.radians(k * 15)
        socket.append((cx + math.cos(a) * sr,
                       cy + math.sin(a) * sr * 1.18))
    pygame.draw.polygon(surf, INK, socket)
    pygame.draw.polygon(surf, IRON_D,
                        [(p[0], p[1]) for p in socket])
    # inner deepest shadow so the rim of the socket itself reads as a lip
    inner = [(cx + math.cos(math.radians(k * 15)) * sr * 0.82,
              cy + math.sin(math.radians(k * 15)) * sr * 0.98)
             for k in range(24)]
    pygame.draw.polygon(surf, INK, inner)


def soul_egg(surf, cx, cy, r, s):
    """A clean hard-rim poison-chartreuse OVOID with a hot top-left core. WHY a
    single crisp vertical ovoid (taller than wide) with its own dark rim instead
    of the round-1 lumpy contour: at 32px it must read as an EGG shape, not a
    round blob, and the warm rim keeps it separated from the dark socket behind.
    The egg is the one warm light source so a faint aura bleeds onto the cool
    bone, popping the focal on both day and night."""
    # emitted aura — concentric translucent rings (the only soft element)
    for (rr, a) in ((r * 1.85, 30), (r * 1.45, 54), (r * 1.15, 90)):
        halo = pygame.Surface((int(rr * 2) + 4, int(rr * 2) + 4), pygame.SRCALPHA)
        pygame.draw.circle(halo, EGG_BR + (a,), (int(rr) + 2, int(rr) + 2), int(rr))
        surf.blit(halo, (cx - int(rr) - 2, cy - int(rr) - 2))
    # the egg ovoid — a clean vertical ellipse, taller than wide, narrower top
    egg_pts = []
    for k in range(28):
        a = math.radians(k * (360 / 28))
        wx = 0.74 if math.sin(a) < 0 else 0.80   # taper the top a hair
        egg_pts.append((cx + math.cos(a) * r * wx,
                        cy + math.sin(a) * r * 1.22))
    # crisp dark rim keyline (warmer than ink so the egg still glows, not muddy)
    pygame.draw.polygon(surf, EGG_RIM, egg_pts)
    inner = [(cx + (p[0] - cx) * 0.86, cy + (p[1] - cy) * 0.88) for p in egg_pts]
    pygame.draw.polygon(surf, EGG, inner)
    # hot inner glow stacked top-left (the glow heart), kept tight + bright
    pygame.draw.ellipse(surf, EGG_BR,
                        (cx - int(r * 0.52), cy - int(r * 0.62),
                         int(r * 0.84), int(r * 1.02)))
    pygame.draw.circle(surf, EGG_HOT, (cx - int(r * 0.18), cy - int(r * 0.26)),
                       max(1, int(r * 0.30)))
    # a thin meridian crack — hints the death-needle sealed inside
    pygame.draw.line(surf, EGG_D, (cx + int(r * 0.26), cy - int(r * 0.92)),
                     (cx - int(r * 0.08), cy + int(r * 1.04)), max(1, int(1.4 * s)))


# -- the blackened-iron tomb-crown of thin bent SPIKES (the HARD tell) ---------
def iron_crown(surf, cx, cy, r, s, n=7):
    """A tall dark comb of thin bent iron spikes — NEVER skulls. WHY bent + tall
    + thin: a jagged dark crown is the polar opposite read from a ring of bone
    domes, so at 32px the head silhouette can't be mistaken for Citipati's
    5-skull crown or Mukha-Devi's tiara. The spikes lean slightly outward from
    centre (a splayed tomb-fence) and the centre spike is tallest."""
    base_y = cy
    # a thin iron browband the spikes rise from (keeps them rooted, not floating)
    band = [(cx - int(r * 1.02), base_y - int(2 * s)),
            (cx + int(r * 1.02), base_y - int(2 * s)),
            (cx + int(r * 0.96), base_y + int(5 * s)),
            (cx - int(r * 0.96), base_y + int(5 * s))]
    triad_blob(surf, IRON, band,
               sheen_pts=[(cx - int(r * 1.0), base_y - int(2 * s)),
                          (cx + int(r * 0.2), base_y - int(2 * s)),
                          (cx + int(r * 0.2), base_y + int(1 * s)),
                          (cx - int(r * 1.0), base_y + int(1 * s))],
               ow=max(1, int(1.4 * s)))
    half = (n - 1) / 2.0
    # uneven per-spike jitter for charm (a ragged tomb-fence, not a tidy comb)
    jitter = (0.0, 0.12, -0.08, 0.0, -0.08, 0.12, 0.0)
    for i in range(n):
        f = (i - half) / max(1.0, half)          # -1 .. +1 across the comb
        bx = cx + f * r * 0.92
        # centre tallest, flanks shorter -> a tomb-crown arc, jittered for charm
        h = r * (1.58 - 0.62 * abs(f) + (jitter[i] if i < len(jitter) else 0))
        lean = f * r * 0.42                       # outward bend at the tip
        tipx = bx + lean
        tipy = base_y - h
        # a thin tapering spike with one kink so it reads "bent iron", not a horn
        kinkx = bx + lean * 0.42 + (r * 0.05 if f >= 0 else -r * 0.05)
        kinky = base_y - h * 0.55
        wbot = r * 0.13
        spike = [(bx - wbot, base_y + int(2 * s)),
                 (bx + wbot, base_y + int(2 * s)),
                 (kinkx + wbot * 0.5, kinky),
                 (tipx, tipy),
                 (kinkx - wbot * 0.5, kinky)]
        triad_blob(surf, IRON, spike,
                   core_pts=[(bx, base_y), (bx + wbot, base_y + int(1 * s)),
                             (kinkx + wbot * 0.4, kinky), (tipx, tipy)],
                   sheen_pts=[(bx - wbot, base_y), (bx - wbot * 0.4, base_y),
                              (kinkx - wbot * 0.4, kinky), (tipx, tipy)],
                   ow=max(1, int(1.1 * s)))
        # cool indigo rim-light up the gap-side edge so each spike survives
        # the night sky (ink-on-indigo-dark otherwise erases the crown)
        pygame.draw.line(surf, lerp(IRON, INDIGO, 0.5),
                         (bx - wbot * 0.6, base_y),
                         (tipx - wbot * 0.4, tipy + int(1 * s)),
                         max(1, int(1.0 * s)))


# -- a single rib-spine throne-back blade (reused for the cap fan) -------------
def rib_blade(surf, x0, y0, x1, y1, w, s, curve=0.0):
    """A slim curved rib bone — a hard spline blade (the throne-back fan unit)."""
    mx = (x0 + x1) / 2 + curve
    my = (y0 + y1) / 2
    left = [(x0 - w * 0.5, y0), (mx - w * 0.5, my), (x1, y1),
            (mx + w * 0.5, my), (x0 + w * 0.5, y0)]
    triad_blob(surf, BONE, left,
               sheen_pts=[(x0 - w * 0.5, y0), (mx - w * 0.5, my),
                          (mx - w * 0.2, my), (x0 - w * 0.1, y0)],
               ow=max(1, int(1.1 * s)))


# -- the enthroned bone-sorcerer ----------------------------------------------
def draw_koschei(surf, cx, cy, s):
    """A skinny, sulking skeleton king SEATED on a marrow-throne: low wide base
    (the throne block + splayed seated legs), knees drawn together, torso hunched
    forward, both bony hands cupping the soul-egg in his lap. Tall blackened-iron
    spike crown + a rib-spire throne-back fan rising behind the shoulders.
    `s` = unit scale around a ~130-unit figure."""

    head_c = (cx, cy - int(38 * s))
    hr = int(22 * s)
    seat_y = cy + int(40 * s)        # top of the throne seat
    base_w = int(54 * s)             # the wide seated base

    # === THRONE BACK + SEAT (drawn first -> behind the king) =================
    # WHY a dark iron frame around pale rib-spires: the throne reads as a heavy
    # seated block (the KIND tell) and the iron stiles echo the crown so the
    # whole silhouette is "pale king in a dark cage."
    # iron throne seat / dais — the wide flat base the mass sits on
    dais = [(cx - base_w, seat_y + int(20 * s)),
            (cx + base_w, seat_y + int(20 * s)),
            (cx + base_w - int(6 * s), seat_y + int(40 * s)),
            (cx - base_w + int(6 * s), seat_y + int(40 * s))]
    triad_blob(surf, IRON, dais,
               core_pts=[(cx - int(4 * s), seat_y + int(22 * s)),
                         (cx + base_w - int(6 * s), seat_y + int(21 * s)),
                         (cx + base_w - int(10 * s), seat_y + int(39 * s)),
                         (cx - int(4 * s), seat_y + int(39 * s))],
               ow=max(1, int(1.6 * s)))
    # two iron stiles = throne ARMS rising behind the shoulders.
    # WHY brought inboard + tied to the dais with a visible armrest cross-bar:
    # round 1's posts floated free and read as external pillars. Each stile now
    # springs off the dais and is joined to the seat mass by a horizontal arm-
    # rest bar at lap height, so the throne reads as ONE caged mass, not
    # skeleton + 2 sticks. A 1px cool rim-light on the gap-side edge keeps the
    # iron silhouette alive on the night sky (ink-on-indigo otherwise vanishes).
    for sgn in (-1, 1):
        sx0 = cx + sgn * int(30 * s)
        sx1 = cx + sgn * int(36 * s)
        stile = [(sx0 - int(5 * s), seat_y + int(22 * s)),
                 (sx0 + int(5 * s), seat_y + int(22 * s)),
                 (sx1 + int(5 * s), cy - int(24 * s)),
                 (sx1 - int(5 * s), cy - int(24 * s))]
        triad_blob(surf, IRON, stile, ow=max(1, int(1.4 * s)))
        # armrest cross-bar tying the stile inboard to the seated mass (lap-high)
        armrest = [(cx + sgn * int(10 * s), seat_y - int(6 * s)),
                   (sx0 + sgn * int(5 * s), seat_y - int(2 * s)),
                   (sx0 + sgn * int(5 * s), seat_y + int(7 * s)),
                   (cx + sgn * int(10 * s), seat_y + int(3 * s))]
        triad_blob(surf, IRON, armrest, ow=max(1, int(1.3 * s)))
        # cool rim-light on the outer edge so the iron survives night 32px
        pygame.draw.line(surf, lerp(IRON, INDIGO, 0.45),
                         (sx0 + sgn * int(5 * s), seat_y + int(20 * s)),
                         (sx1 + sgn * int(5 * s), cy - int(23 * s)),
                         max(1, int(1.4 * s)))
        # a small iron finial knob atop each stile (the throne arm-cap)
        triad_circle(surf, IRON, (sx1, cy - int(26 * s)), int(6 * s),
                     ow=max(1, int(1.2 * s)), core=False)

    # rib-spire throne-back fan between the stiles (pale bone splines)
    for i in range(-2, 3):
        f = i / 2.0
        bx = cx + f * int(26 * s)
        h = int((54 - 14 * abs(f)) * s)
        rib_blade(surf, bx, seat_y + int(16 * s), bx + f * int(8 * s),
                  seat_y + int(16 * s) - h, int(7 * s), s, curve=f * int(5 * s))

    # === SEATED LEGS — splayed femurs + shins forming the wide base ==========
    # WHY splayed-then-tucked: a seated figure's thighs go OUT to the knees then
    # the shins drop straight down, making a stable trapezoid base (the throne
    # KIND). Knees ride near the seat front, feet planted on the dais.
    leg_th = int(13 * s)
    for sgn in (-1, 1):
        hip = (cx + sgn * int(12 * s), seat_y + int(4 * s))
        knee = (cx + sgn * int(34 * s), seat_y + int(10 * s))
        foot = (cx + sgn * int(34 * s), seat_y + int(34 * s))
        bone_limb(surf, hip, knee, foot, leg_th, s)
        # bony foot block on the dais
        fb = [(foot[0] - sgn * int(2 * s), foot[1] - int(3 * s)),
              (foot[0] + sgn * int(16 * s), foot[1] - int(1 * s)),
              (foot[0] + sgn * int(15 * s), foot[1] + int(8 * s)),
              (foot[0] - sgn * int(3 * s), foot[1] + int(7 * s))]
        triad_blob(surf, BONE, fb, ow=max(1, int(1.2 * s)))

    # === PELVIS + SPINE + HUNCHED RIBCAGE ====================================
    pelvis = [(cx - int(18 * s), seat_y - int(4 * s)),
              (cx + int(18 * s), seat_y - int(4 * s)),
              (cx + int(14 * s), seat_y + int(10 * s)),
              (cx, seat_y + int(13 * s)),
              (cx - int(14 * s), seat_y + int(10 * s))]
    triad_blob(surf, BONE, pelvis,
               core_pts=[(cx - int(6 * s), seat_y + int(2 * s)),
                         (cx + int(14 * s), seat_y - int(2 * s)),
                         (cx + int(13 * s), seat_y + int(9 * s)),
                         (cx, seat_y + int(12 * s))],
               ow=max(1, int(1.6 * s)))
    pygame.draw.circle(surf, BONE_DD, (cx, seat_y + int(2 * s)), int(4 * s))

    # spine — hunched FORWARD (the sulking stoop), curving toward the lap egg
    spine = [(cx, seat_y - int(2 * s)),
             (cx - int(4 * s), cy + int(6 * s)),
             (cx - int(2 * s), cy - int(14 * s))]
    pygame.draw.lines(surf, INK, False, spine, int(8 * s))
    pygame.draw.lines(surf, BONE, False, spine, int(5 * s))

    # ribcage — a narrow hunched barrel (skinny king), tilted forward
    rc_cx, rc_cy = cx - int(2 * s), cy - int(4 * s)
    rc_w, rc_h = int(30 * s), int(36 * s)
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.42), rc_cy + rc_h // 2)]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(6 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(4 * s))],
               ow=max(1, int(1.8 * s)))
    # hard rib bands (curved dark grooves) — the motif the femur pillar echoes
    for i in range(4):
        ry = rc_cy - rc_h // 2 + int(8 * s) + i * int(7 * s)
        bw = int(rc_w * (0.44 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(7 * s), bw * 2, int(15 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.2 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(5 * s)), max(1, int(2 * s)))

    # === SOUL-EGG cupped in the lap (socket behind -> egg -> two thumbs) ======
    # WHY +size + a dark socket frame: round 1's egg bled into the lap at 32px
    # and lost to the eyes. It is bigger now (the single focal) and set into a
    # hard dark recess so its rim has a high-contrast frame on every side.
    egg_c = (cx + int(1 * s), cy + int(21 * s))
    egg_r = int(16 * s)
    egg_socket(surf, egg_c[0], egg_c[1], egg_r, s)
    soul_egg(surf, egg_c[0], egg_c[1], egg_r, s)

    # === ARMS — both reaching DOWN-IN to cradle the egg from below ============
    # WHY two fat thumbs meeting UNDER the egg instead of finger-arc filigree:
    # at 32px the thin arcs read as dirt; two simple thumb shapes forming a
    # cupped bracket below the egg read cleanly as "hands holding."
    arm_th = int(7 * s)
    for sgn in (-1, 1):
        shoulder = (rc_cx + sgn * int(15 * s), rc_cy - rc_h // 2 + int(7 * s))
        elbow = (cx + sgn * int(25 * s), cy + int(8 * s))
        hand = (egg_c[0] + sgn * int(12 * s), egg_c[1] + int(12 * s))
        bone_limb(surf, shoulder, elbow, hand, arm_th, s)
    # two fat thumbs sweeping UNDER the egg into a cupped bracket
    for sgn in (-1, 1):
        bx = egg_c[0] + sgn * int(13 * s)
        by = egg_c[1] + int(13 * s)
        tip = (egg_c[0] + sgn * int(4 * s), egg_c[1] + int(int(egg_r) * 1.18))
        mid = (egg_c[0] + sgn * int(11 * s), egg_c[1] + int(int(egg_r) * 1.30))
        thumb = [(bx - sgn * int(3 * s), by - int(3 * s)),
                 (bx + sgn * int(4 * s), by - int(1 * s)),
                 (mid[0], mid[1]),
                 (tip[0], tip[1]),
                 (tip[0] - sgn * int(2 * s), tip[1] - int(4 * s))]
        triad_blob(surf, BONE, thumb,
                   sheen_pts=[(bx - sgn * int(3 * s), by - int(3 * s)),
                              (bx + sgn * int(1 * s), by - int(2 * s)),
                              (mid[0] - sgn * int(2 * s), mid[1] - int(1 * s)),
                              (tip[0], tip[1] - int(2 * s))],
                   ow=max(1, int(1.3 * s)))

    # === SKULL HEAD — chibi, sulking, scary-cute, indigo socket glow =========
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    # gaunt cheek hollows (skin-clings-to-bone gaunt read)
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.30)),
                           int(hr * 0.28))
    # big round INDIGO sockets — the second cool pin (down-cast = sulking)
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.06)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.36))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INDIGO_D, (ex, ey), int(hr * 0.22))
        pygame.draw.circle(surf, INDIGO, (ex + sgn * int(1 * s), ey + int(2 * s)),
                           int(hr * 0.15))
        pygame.draw.circle(surf, INDIGO_BR, (ex, ey + int(1 * s)),
                           max(1, int(hr * 0.07)))
    # the SULK CUE: a heavy indigo brow shadow angled DOWN-toward-centre over
    # the sockets — one unmistakable "grumpy immortal" tell that reads at 32px
    # (a neutral skull has no brow; the down-cant + indigo tint sells the scowl)
    for sgn in (-1, 1):
        brow = [(head_c[0] + sgn * int(hr * 0.74), head_c[1] - int(hr * 0.34)),
                (head_c[0] + sgn * int(hr * 0.10), head_c[1] - int(hr * 0.08)),
                (head_c[0] + sgn * int(hr * 0.12), head_c[1] + int(hr * 0.02)),
                (head_c[0] + sgn * int(hr * 0.78), head_c[1] - int(hr * 0.22))]
        pygame.draw.polygon(surf, lerp(BONE_DD, INDIGO_D, 0.45), brow)
        pygame.draw.aalines(surf, INK, False, brow[:2])
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.13), head_c[1] + int(hr * 0.32)),
                         (head_c[0] + int(hr * 0.13), head_c[1] + int(hr * 0.32)),
                         (head_c[0], head_c[1] + int(hr * 0.58))])
    # a small smug down-turned grin (dangerously smug, not a wide grin)
    my = head_c[1] + int(hr * 0.74)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.42), my - int(hr * 0.02)),
                     (head_c[0] + int(hr * 0.42), my + int(hr * 0.06)),
                     max(1, int(2 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, INK,
                         (head_c[0] + int(k * hr * 0.18), my - int(hr * 0.06)),
                         (head_c[0] + int(k * hr * 0.18), my + int(hr * 0.10)),
                         max(1, int(1 * s)))

    # === TOMB-CROWN of blackened-iron spikes (the HARD tell) =================
    iron_crown(surf, head_c[0], head_c[1] - int(hr * 0.86), int(hr * 0.96), s, n=7)


# -- the femur-throne-column -> pillar mirror ---------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The femur-throne-column IS the pillar: stacked PAIRED femurs lashed into a
    column (joint banding) = the tileable shaft; a rib-spire throne-back FAN
    cradling the glowing soul-egg orb at the gap = the creature-derived gap-edge
    cap. On-axis, symmetric, bottom-rooted, never top-heavy.

    `cap` names the END that faces the GAP."""
    shaft_w = int(16 * s)
    # central ink rod the femur pairs lash onto
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    # === stacked PAIRED FEMURS — the repeatable shaft unit ===================
    pitch = int(26 * s)
    cap_room = int(40 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    while y <= b1:
        # a pair of femurs side by side, each a shaft with two knobby ends
        for sgn in (-1, 1):
            fx = cx + sgn * int(7 * s)
            top_y = y - int(8 * s)
            bot_y = y + int(8 * s)
            # femur shaft (slightly waisted bar)
            shaft = [(fx - int(4 * s), top_y), (fx + int(4 * s), top_y),
                     (fx + int(3 * s), y), (fx + int(4 * s), bot_y),
                     (fx - int(4 * s), bot_y), (fx - int(3 * s), y)]
            triad_blob(surf, BONE, shaft,
                       sheen_pts=[(fx - int(4 * s), top_y), (fx - int(1 * s), top_y),
                                  (fx - int(1 * s), bot_y), (fx - int(4 * s), bot_y)],
                       ow=max(1, int(1.2 * s)))
            # knobby condyle ends (top + bottom)
            for ky in (top_y, bot_y):
                triad_circle(surf, BONE, (fx - int(3 * s), ky), int(3 * s),
                             ow=max(1, int(1.0 * s)), core=False)
                triad_circle(surf, BONE, (fx + int(3 * s), ky), int(3 * s),
                             ow=max(1, int(1.0 * s)), core=False)
        # iron lashing band cinching the pair (joint banding)
        band = [(cx - shaft_w * 0.66, y - int(4 * s)),
                (cx + shaft_w * 0.66, y - int(4 * s)),
                (cx + shaft_w * 0.66, y + int(4 * s)),
                (cx - shaft_w * 0.66, y + int(4 * s))]
        triad_blob(surf, IRON, band,
                   sheen_pts=[(cx - shaft_w * 0.66, y - int(4 * s)),
                              (cx, y - int(4 * s)), (cx, y - int(1 * s)),
                              (cx - shaft_w * 0.66, y - int(1 * s))],
                   ow=max(1, int(1.0 * s)))
        y += pitch

    # === gap-edge cap: rib-spire throne-back fan cradling the soul-egg =======
    cap_y = (bot - int(26 * s)) if cap == "bottom" else (top + int(26 * s))
    fan_dir = -1 if cap == "bottom" else 1   # fan spreads AWAY from the gap
    # iron seat lip the fan + egg sit on
    lip = [(cx - int(18 * s), cap_y - fan_dir * int(2 * s)),
           (cx + int(18 * s), cap_y - fan_dir * int(2 * s)),
           (cx + int(14 * s), cap_y - fan_dir * int(11 * s)),
           (cx - int(14 * s), cap_y - fan_dir * int(11 * s))]
    triad_blob(surf, IRON, lip, ow=max(1, int(1.2 * s)))
    # rib-spire fan rising away from the gap — thinned by one spline so the dark
    # socket (not a busy splay) does the framing where the fan meets the egg
    for i in (-2, -1, 1, 2):
        f = i / 2.0
        bx = cx + f * int(18 * s)
        h = int((30 - 8 * abs(f)) * s)
        rib_blade(surf, bx, cap_y - fan_dir * int(8 * s),
                  bx + f * int(6 * s), cap_y - fan_dir * int(8 * s) - fan_dir * h,
                  int(6 * s), s, curve=f * int(4 * s))
    # the glowing soul-egg cradled at the gap edge (the single warm focal):
    # same socket + clean-ovoid fix as the lap egg so the cap reads at 32px
    egg_y = cap_y + fan_dir * int(11 * s)
    egg_pr = int(13 * s)
    egg_socket(surf, cx, egg_y, egg_pr, s)
    soul_egg(surf, cx, egg_y, egg_pr, s)


# -- compose the review sheet -------------------------------------------------
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_koschei(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def main():
    W, H = 1010, 820
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("KOSCHEI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "deathless bone-sorcerer on a marrow-throne  ·  SEATED wide-base · iron-SPIKE crown · socketed cupped soul-egg focal · round 2",
        True, LABEL_DIM), (220, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 232, 1.80)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("SEATED king: wide throne base, splayed legs, hunched stoop — the only", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("enthroned mass. Tall BLACKENED-IRON spike crown (never skulls) = the tell.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Socketed chartreuse soul-egg (dark recess + two thumbs) = single warm focal.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, clean tileable shaft ================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — femur-throne", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("paired-femur column (iron lashings) = shaft;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("rib-spire fan + cupped soul-egg caps the gap", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, bottom-rooted)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_koschei(big, 48 * SS, 52 * SS, (32 / 132.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, night_y + 27))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 192
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (BONE, "corpse-tallow bone"), (BONE_D, "olive-bone shade"),
        (EGG, "chartreuse soul-egg"), (EGG_HOT, "egg hot core"),
        (IRON, "blackened iron"), (INDIGO, "indigo socket"),
        (INDIGO_BR, "indigo pin"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (26,26,24) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
