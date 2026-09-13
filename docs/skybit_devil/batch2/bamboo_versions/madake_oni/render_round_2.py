"""
Round-2 concept renderer for MADAKE-ONI -- the dry-timber bamboo ogre hauling a
giant knotted culm kanabo (bamboo-versions set, concept #2). Headless Pygame;
ELEVATED pipeline (supersample SS=6 -> smoothscale) so the studded-club geometry
and node-ring banding stay crisp at downscale. Keeps the shipped house grammar:
flat fills, hard 1-2px ink keyline, dark-core -> flat-fill -> top-left rim-sheen
triad, 1px alpha-grown outline, chibi proportions, scary-CUTE pushed EPIC;
procedural-only (no gradients/PNGs/soft halos).

WHY this is the OGRE-WITH-CLUB of the bamboo brood: the other four are a
serpent-coil, a slim noble stack, a bowed snow-stalk, and a split light-stalk.
Madake-Oni is the ONLY squat brute and the ONLY warm-STRAW body.

=== ROUND-2 REVISIONS (AD verdict ITERATE) ============================
The hero portrait was good; the failures were all gameplay-scale reads + binding
pins. Fixes, in the AD's priority order:

1. CLUB BREAKS THE SILHOUETTE (the gate fix). Round 1 shouldered the kanabo
   vertically behind/beside the body so the crossed arms hid it and the boss
   read as a straw lump. Now the club is SHOULDERED ON A STEEP DIAGONAL across
   the back: the root-ball head juts clearly ABOVE the horns and the studded
   shaft crosses out past the body's right edge, so it survives the blackout
   test as a distinct upper lobe + diagonal bar. Brief: "taller than its body."
2. ROOT-BALL != OGRE HEAD. The root-ball is now a SPHERICAL gnarled knob with a
   stud-ring collar banding up to it, distinctly rounder and a different value
   from the SQUARE brow-barred horned ogre head. They can never read as twins.
3. EMBER SURVIVES 32px. Switched to a SINGLE dominant cyclopean ember seated in
   a dark bored socket, brightened one value (EMBER_HOT core), so the lone
   saturated accent stays visible as red on the night chip.
4. HARD-METALLIC GOLD-LEAF SPLIT-CRACKS. Now 3-5 sharp angular STEPPED facets
   (bright gold core + ink-side step edge) on chest, club shaft, and a horn --
   they snap as struck metal, the deliberate foil to Kaguya's soft moon-halo.
5. PILLAR TILE + GAP-CAP. Enlarged + gnarled the root-ball cap so the gap edge
   reads as a deliberate terminal; ONE locked node-band height + stud-ring style
   repeated exactly for a seamless tile; cap mirrors cleanly top<->bottom.
6. WARM HORN TIPS. Horn tips recolored from cool-white to husk-cream/bone so
   nothing on the boss reads cold (kept clear of Yukitake's snow palette).
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# -- PINNED PALETTE (locked brief) --------------------------------------------
# Warm DRY-STRAW madake -- basically NOT green. Held genuinely warm but
# DESATURATED so it never tips into Kappa's turtle-bronze. The ember-red eye is
# the SOLE saturated accent and stays TINY; the sparkle is hard-metallic
# gold-leaf split-cracks, never a glow.
STRAW     = (212, 176, 104)   # timber-straw base (the dominant warm fill)
STRAW_D   = (158, 116,  56)   # burnt-amber shade / dark-core groove
STRAW_DD  = (112,  80,  40)   # deepest amber hollow (node grooves, eye pits)
CLUB      = (190, 150,  82)   # club body -- a notch DARKER than the ogre body so
CLUB_D    = (138, 100,  48)   # the club mass reads apart from the brute at 32px
GOLD      = (238, 206, 120)   # gold-leaf split accent (HARD metallic facets)
GOLD_HI   = (252, 238, 176)   # hot gold-leaf catch-pip (the metallic glint)
CREAM     = (236, 222, 178)   # husk-cream (fang/horn highlight, inner culm)
BONE      = (224, 204, 150)   # warm bone -- horn tips (NOT cool-white, anti-snow)
SHEEN     = (244, 222, 160)   # hottest straw sheen (top-left rim)
EMBER     = (216,  68,  46)   # ember-red eye -- the ONLY saturated accent, TINY
EMBER_HOT = (252, 158, 104)   # hot pip inside the ember eye (brightened 1 value)
EMBER_DK  = ( 78,  20,  16)   # dark socket the ember is seated in (read at 32px)
INK       = ( 34,  24,  18)   # hard ink keyline (warm-dark)

BG        = ( 96,  84,  62)   # neutral warm-tan review backdrop
PANEL     = ( 74,  64,  46)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (244, 238, 224)
LABEL_DIM = (210, 198, 172)


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
        pygame.draw.polygon(surf, lerp(color, SHEEN, 0.6), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    """Round equivalent of triad_blob -- dark core bottom-right, sheen top-left."""
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, lerp(color, SHEEN, 0.65),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


# -- a HARD-METALLIC gold-leaf split-crack glint (the sparkle lane) -----------
def gold_crack(surf, x, y, length, ang, s, flip=1):
    """A gold-leaf split-crack rendered as a SHARP 2-TONE STEPPED metallic facet.
    WHY hard-metallic: the AD pin splits Madake's gold (hard stepped) from
    Kaguya's soft stepped moon-halo so the two gold accents never collide. The
    crack is a thin angular sliver with a BRIGHT gold-leaf core and a hard
    INK-SIDE step edge so it snaps as struck metal along a grain split, never a
    soft glow. A single white catch-pip is the metallic glint."""
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca
    hw = max(1.5, length * 0.13)
    tip = (x + ca * length, y + sa * length)
    belly = (x + ca * length * 0.42, y + sa * length * 0.42)
    # the angular sliver (asymmetric facet -> reads chipped, not lens-shaped)
    leaf = [
        (x, y),
        (belly[0] + px * hw * flip, belly[1] + py * hw * flip),
        (tip[0], tip[1]),
        (belly[0] - px * hw * 0.55 * flip, belly[1] - py * hw * 0.55 * flip),
    ]
    # 1) the dark split it sits in (so the gold has an ink edge to snap against)
    pygame.draw.polygon(surf, EMBER_DK if False else INK, leaf)
    # 2) the ink-side STEP: shift the sliver toward the shadow side and fill dark
    step = [(int(qx - px * hw * 0.5 * flip), int(qy - py * hw * 0.5 * flip))
            for qx, qy in leaf]
    pygame.draw.polygon(surf, STRAW_DD, step)
    # 3) the BRIGHT gold-leaf core, inset toward the light side -> the 2nd tone
    core = [(int(x + (qx - x) * 0.84 + px * hw * 0.22 * flip),
             int(y + (qy - y) * 0.84 + py * hw * 0.22 * flip)) for qx, qy in leaf]
    pygame.draw.polygon(surf, GOLD, core)
    # 4) one HARD white catch-pip up the leading facet -> the metallic glint
    pip = (int(x + ca * length * 0.32 + px * hw * 0.45 * flip),
           int(y + sa * length * 0.32 + py * hw * 0.45 * flip))
    pygame.draw.circle(surf, GOLD_HI, pip, max(1, int(hw * 0.55)))


# -- ONE locked node-band: same height + same stud-ring style everywhere ------
# WHY a single locked geometry: the AD pin requires ONE consistent node-segment
# band height + stud-ring style repeated EXACTLY for a seamless tile. These
# module constants pin the band so the hero club, pillar shaft, and gap-cap
# collar all draw the identical ring.
NODE_H_U   = 18.0   # node-band vertical footprint in figure-units (locked)
STUD_KS    = (-1.0, -0.5, 0.0, 0.5, 1.0)   # locked stud angular positions


def node_band(surf, cx, y, half_w, s, color=CLUB, shade=CLUB_D, studs=True):
    """One culm NODE-RING drawn from the LOCKED geometry: twin raised grooves
    (sheath-scar + nodal ridge) on a swollen collar, ringed with evenly-spaced
    stud knobs. WHY locked: identical band height + identical stud cadence is
    what lets the pillar shaft tile seamlessly top<->bottom."""
    h = NODE_H_U
    nb = int(half_w * 1.20)
    coll = [(cx - nb,            y + int(h * 0.34 * s)),
            (cx - int(nb * 0.9), y - int(h * 0.39 * s)),
            (cx + int(nb * 0.9), y - int(h * 0.39 * s)),
            (cx + nb,            y + int(h * 0.34 * s)),
            (cx + int(nb * 0.9), y + int(h * 0.72 * s)),
            (cx - int(nb * 0.9), y + int(h * 0.72 * s))]
    triad_blob(surf, color, coll,
               core_pts=[(cx, y + int(h * 0.11 * s)), (cx + nb, y + int(h * 0.34 * s)),
                         (cx + int(nb * 0.9), y + int(h * 0.72 * s)), (cx, y + int(h * 0.61 * s))],
               sheen_pts=[(cx - nb, y + int(h * 0.34 * s)),
                          (cx - int(nb * 0.5), y - int(h * 0.33 * s)),
                          (cx - int(nb * 0.2), y - int(h * 0.22 * s)),
                          (cx - int(nb * 0.7), y + int(h * 0.28 * s))],
               ow=max(1, int(1.4 * s)))
    # twin transverse node grooves (sheath scar + nodal ridge) -- the bamboo tell
    pygame.draw.line(surf, shade, (cx - int(nb * 0.82), y - int(h * 0.11 * s)),
                     (cx + int(nb * 0.82), y - int(h * 0.11 * s)), max(1, int(1.8 * s)))
    pygame.draw.line(surf, shade, (cx - int(nb * 0.82), y + int(h * 0.44 * s)),
                     (cx + int(nb * 0.82), y + int(h * 0.44 * s)), max(1, int(1.8 * s)))
    if studs:
        for k in STUD_KS:
            sxk = cx + int(k * nb * 0.92)
            syk = y + int(h * 0.11 * s) + int(abs(k) * h * 0.17 * s)
            triad_circle(surf, color, (sxk, syk), max(2, int(3.4 * s)),
                         ow=max(1, int(1.0 * s)), sheen=True, core=False)


# -- the gnarled ROOT-BALL head (kanabo butt -> reused for hero club + cap) ----
def root_ball(surf, cx, cy, r, s, collar=True):
    """The gnarled root-ball striking head: a near-SPHERICAL lumpy culm-root knob
    with a stud-ring COLLAR banding up to it. WHY spherical + collar: the AD pin
    requires this to read distinctly from the SQUARE brow-barred ogre head -- so
    it's round, knotted, a darker club-value, and ringed by a node collar, never
    an octagonal twin of the face."""
    # the stud-ring collar where the shaft swells into the root-ball
    if collar:
        node_band(surf, cx, cy + int(r * 0.92), int(r * 0.62), s, studs=True)
    # a rounder, lumpier knob than r1 -- more circle vertices, gentler dents, so
    # it reads SPHERICAL (a struck root knob), not a faceted head
    knob = []
    bumps = (1.00, 0.93, 1.02, 0.90, 1.00, 0.95, 1.03, 0.92,
             0.99, 0.94, 1.01, 0.91)
    n = len(bumps)
    for i, bm in enumerate(bumps):
        a = math.pi * 2 * i / n - math.pi / 2
        knob.append((cx + int(math.cos(a) * r * bm),
                     cy + int(math.sin(a) * r * bm)))
    triad_blob(surf, CLUB, knob,
               core_pts=[(cx + int(r * 0.10), cy + int(r * 0.06)),
                         (cx + int(r * 0.86), cy + int(r * 0.04)),
                         (cx + int(r * 0.54), cy + int(r * 0.78)),
                         (cx - int(r * 0.04), cy + int(r * 0.88)),
                         (cx + int(r * 0.18), cy + int(r * 0.26))],
               sheen_pts=[(cx - int(r * 0.84), cy - int(r * 0.06)),
                          (cx - int(r * 0.52), cy - int(r * 0.64)),
                          (cx - int(r * 0.16), cy - int(r * 0.48)),
                          (cx - int(r * 0.44), cy + int(r * 0.10))],
               ow=max(1, int(1.9 * s)))
    # gnarled root knots -- a few dark gouges so the lump reads knotted root
    for dx_f, dy_f, rr in ((-0.34, -0.28, 0.18), (0.32, 0.04, 0.22),
                           (-0.04, 0.40, 0.16), (0.18, -0.40, 0.13)):
        pygame.draw.circle(surf, CLUB_D,
                           (cx + int(r * dx_f), cy + int(r * dy_f)), max(1, int(r * rr)))
        pygame.draw.circle(surf, CLUB,
                           (cx + int(r * dx_f) - max(1, int(r * 0.05)),
                            cy + int(r * dy_f) - max(1, int(r * 0.05))),
                           max(1, int(r * rr * 0.5)))
    # HARD gold-leaf split-cracks across the root-ball (the sparkle, metallic)
    gold_crack(surf, cx - int(r * 0.5), cy - int(r * 0.18), r * 0.92, math.radians(30), s, 1)
    gold_crack(surf, cx + int(r * 0.08), cy + int(r * 0.12), r * 0.74, math.radians(-54), s, -1)


# -- the studded culm KANABO (the club -- reused for hero + pillar shaft) ------
def kanabo_shaft(surf, cx, y0, y1, half_w, s, n_nodes=4):
    """A fat knotted culm shaft segmented by raised stud-ringed node bands using
    the LOCKED node geometry. WHY this IS the pillar repeat: each node-segment
    tiles cleanly because every band is the same height + same stud cadence."""
    body = [(cx - half_w, y0), (cx + half_w, y0),
            (cx + half_w, y1), (cx - half_w, y1)]
    triad_blob(surf, CLUB, body,
               core_pts=[(cx + int(half_w * 0.1), y0), (cx + half_w, y0),
                         (cx + half_w, y1), (cx + int(half_w * 0.1), y1)],
               sheen_pts=[(cx - half_w, y0),
                          (cx - int(half_w * 0.55), y0),
                          (cx - int(half_w * 0.55), y1),
                          (cx - half_w, y1)],
               ow=max(1, int(1.6 * s)))
    # gold-leaf split-cracks running the grain (hard metallic glints, sparse)
    span = y1 - y0
    for fy, fx, fl, fa, fp in ((0.20, -0.32, 0.14, 96, 1), (0.52, 0.30, 0.12, 84, -1),
                               (0.82, -0.24, 0.13, 100, 1)):
        gold_crack(surf, cx + int(half_w * fx), y0 + int(span * fy),
                   span * fl, math.radians(fa), s, fp)
    # raised stud-ringed node bands spaced evenly down the shaft = repeat band
    for i in range(n_nodes):
        ny = y0 + int(span * (i + 0.5) / n_nodes)
        node_band(surf, cx, ny, half_w, s, studs=True)


# -- the ogre FACE (knot-brow, fangs, stub horns, the SINGLE ember eye) --------
def oni_face(surf, cx, cy, r, s):
    """The squat ogre head -- deliberately SQUARER than the round root-ball: a
    broad knot-browed straw skull with a heavy horizontal BROW-BAR, two short
    bamboo-node STUB horns with warm BONE tips, jutting under-fangs, and the ONLY
    saturated accent -- a SINGLE dominant cyclopean ember eye seated in a dark
    bored socket. WHY one dominant ember: at 32px two specks both vanished, so
    the lone saturated accent is consolidated + brightened to survive the chip."""
    # broad chibi cranium -- squarer / flatter top than the round root-ball
    head = [(cx - int(r * 1.08), cy - int(r * 0.42)),
            (cx - int(r * 0.86), cy - int(r * 0.96)),
            (cx - int(r * 0.30), cy - int(r * 1.06)),
            (cx + int(r * 0.30), cy - int(r * 1.06)),
            (cx + int(r * 0.86), cy - int(r * 0.96)),
            (cx + int(r * 1.08), cy - int(r * 0.42)),
            (cx + int(r * 0.94), cy + int(r * 0.58)),
            (cx + int(r * 0.42), cy + int(r * 1.02)),
            (cx - int(r * 0.42), cy + int(r * 1.02)),
            (cx - int(r * 0.94), cy + int(r * 0.58))]
    triad_blob(surf, STRAW, head,
               core_pts=[(cx + int(r * 0.10), cy - int(r * 0.10)),
                         (cx + int(r * 1.0), cy - int(r * 0.30)),
                         (cx + int(r * 0.86), cy + int(r * 0.56)),
                         (cx + int(r * 0.10), cy + int(r * 0.92))],
               sheen_pts=[(cx - int(r * 0.98), cy - int(r * 0.34)),
                          (cx - int(r * 0.70), cy - int(r * 0.84)),
                          (cx - int(r * 0.30), cy - int(r * 0.62)),
                          (cx - int(r * 0.56), cy + int(r * 0.16))],
               ow=max(1, int(1.8 * s)))

    # two short bamboo-NODE stub horns with WARM BONE tips (anti-snow)
    for sgn in (-1, 1):
        hx = cx + sgn * int(r * 0.66)
        hy = cy - int(r * 0.98)
        horn = [(hx - sgn * int(r * 0.20), hy + int(r * 0.12)),
                (hx - sgn * int(r * 0.14), hy - int(r * 0.42)),
                (hx + sgn * int(r * 0.10), hy - int(r * 0.50)),
                (hx + sgn * int(r * 0.22), hy + int(r * 0.08))]
        triad_blob(surf, BONE, horn,
                   core_pts=[(hx + sgn * int(r * 0.02), hy - int(r * 0.10)),
                             (hx + sgn * int(r * 0.10), hy - int(r * 0.46)),
                             (hx + sgn * int(r * 0.20), hy + int(r * 0.06))],
                   ow=max(1, int(1.2 * s)))
        # node groove across the stub horn (it's a bamboo-node nub)
        pygame.draw.line(surf, STRAW_DD,
                         (hx - sgn * int(r * 0.16), hy - int(r * 0.18)),
                         (hx + sgn * int(r * 0.14), hy - int(r * 0.22)),
                         max(1, int(1.4 * s)))
    # a hard gold-leaf crack splitting up the LEFT horn (sparkle pin on a horn)
    gold_crack(surf, cx - int(r * 0.70), cy - int(r * 0.70), r * 0.5,
               math.radians(-104), s, 1)

    # heavy horizontal BROW-BAR -- a thick straw ridge with a centre dip, the
    # SQUARE oni scowl that distinguishes the head from the round root-ball
    brow = [(cx - int(r * 0.90), cy - int(r * 0.34)),
            (cx - int(r * 0.32), cy - int(r * 0.48)),
            (cx, cy - int(r * 0.26)),                  # centre dip (the frown)
            (cx + int(r * 0.32), cy - int(r * 0.48)),
            (cx + int(r * 0.90), cy - int(r * 0.34)),
            (cx + int(r * 0.74), cy - int(r * 0.06)),
            (cx, cy - int(r * 0.02)),
            (cx - int(r * 0.74), cy - int(r * 0.06))]
    triad_blob(surf, STRAW_D, brow,
               sheen_pts=[(cx - int(r * 0.84), cy - int(r * 0.30)),
                          (cx - int(r * 0.38), cy - int(r * 0.42)),
                          (cx - int(r * 0.30), cy - int(r * 0.18)),
                          (cx - int(r * 0.68), cy - int(r * 0.12))],
               ow=max(1, int(1.2 * s)))
    # a knot-gouge on the brow centre -> the burl knot of cured timber
    pygame.draw.circle(surf, STRAW_DD, (cx, cy - int(r * 0.24)), max(1, int(r * 0.10)))

    # the SINGLE dominant cyclopean EMBER eye -- the ONLY saturated accent,
    # seated in a dark bored socket so the red survives 32px. Sits centred just
    # under the brow dip; brightened one value vs r1.
    ey = cy + int(r * 0.10)
    # dark bored socket (a wide angular pit cut into the straw under the brow)
    sock = [(cx - int(r * 0.40), ey - int(r * 0.20)),
            (cx + int(r * 0.40), ey - int(r * 0.20)),
            (cx + int(r * 0.30), ey + int(r * 0.30)),
            (cx - int(r * 0.30), ey + int(r * 0.30))]
    pygame.draw.polygon(surf, INK, sock)
    pygame.draw.polygon(surf, EMBER_DK, sock)
    # the ember disc -- big enough to read at 32px (the whole eye is the accent)
    pygame.draw.circle(surf, EMBER, (cx, ey), max(2, int(r * 0.26)))
    pygame.draw.circle(surf, EMBER_HOT, (cx - max(1, int(r * 0.05)), ey - max(1, int(r * 0.05))),
                       max(1, int(r * 0.12)))
    # a slit pupil keeps it scary-CUTE, not a plain dot
    pygame.draw.line(surf, EMBER_DK, (cx, ey - int(r * 0.16)), (cx, ey + int(r * 0.16)),
                     max(1, int(1.6 * s)))

    # broad flat nose-knot + the jutting UNDER-FANGS (chibi-scary tusk grin)
    pygame.draw.circle(surf, STRAW_DD, (cx, cy + int(r * 0.46)), max(1, int(r * 0.11)))
    pygame.draw.line(surf, INK, (cx - int(r * 0.46), cy + int(r * 0.70)),
                     (cx + int(r * 0.46), cy + int(r * 0.70)), max(2, int(2.4 * s)))
    for sgn in (-1, 1):
        fx = cx + sgn * int(r * 0.30)
        fang = [(fx - int(r * 0.12), cy + int(r * 0.66)),
                (fx + int(r * 0.12), cy + int(r * 0.66)),
                (fx, cy + int(r * 1.00))]   # tusk juts UP from the lower jaw
        triad_blob(surf, CREAM, fang,
                   sheen_pts=[(fx - int(r * 0.08), cy + int(r * 0.68)),
                              (fx, cy + int(r * 0.68)),
                              (fx - int(r * 0.02), cy + int(r * 0.86))],
                   ow=max(1, int(1.0 * s)))


# -- the ogre-with-club hero ---------------------------------------------------
def draw_madake_oni(surf, cx, cy, s):
    """Squat straw-tan oni SHOULDERING a studded culm kanabo taller than its body
    on a steep diagonal across the back. `s` = unit scale around a ~150-unit
    figure. Drawn back-to-front: the diagonal club (root-ball jutting above the
    horns, shaft crossing out past the body) -> broad low body -> arms gripping
    the haft -> head last. Heavy mass sits LOW; the club breaks the silhouette."""

    # === the KANABO shouldered on a STEEP DIAGONAL across the back ===========
    # WHY a diagonal: round 1 hid the vertical club behind the body so the boss
    # read as a lump. Shouldered diagonally, the root-ball head juts clearly
    # ABOVE the horns (upper-right lobe) and the studded shaft crosses down past
    # the body's right edge into the low fists -> the club survives the blackout
    # test as its own upper lobe + diagonal bar. The club is drawn vertically on
    # a temp surface (so node rings tile level), rotated, then pinned by its GRIP
    # point so the heavy root-ball end rides high and right above the head.
    haft_len = int(154 * s)
    cw = int(11 * s)
    pad = int(46 * s)
    csurf = pygame.Surface((cw * 2 + pad * 2, haft_len + pad * 2), pygame.SRCALPHA)
    ccx = cw + pad
    rb_y = pad + int(24 * s)          # root-ball sits at the TOP of the temp strip
    grip_local = (ccx, pad + haft_len - int(12 * s))   # fists clamp near the bottom
    kanabo_shaft(csurf, ccx, pad + int(40 * s), pad + haft_len, cw, s, n_nodes=3)
    root_ball(csurf, ccx, rb_y, int(20 * s), s, collar=True)

    ang_deg = 38.0                    # rotate so root-ball end swings up-and-right
    ang = math.radians(ang_deg)
    rot = pygame.transform.rotate(csurf, -ang_deg)
    rw, rh = rot.get_size()
    ow, oh = csurf.get_size()
    # where the grip point lands after a rotate about the surface centre
    gx0, gy0 = grip_local[0] - ow / 2, grip_local[1] - oh / 2
    ca, sa = math.cos(ang), math.sin(ang)
    grip_rot = (gx0 * ca - gy0 * sa, gx0 * sa + gy0 * ca)
    # target grip at the low fists, club passing diagonally up over the shoulder
    grip_x = cx + int(6 * s)
    grip_y = cy + int(22 * s)
    surf.blit(rot, (int(grip_x - rw / 2 - grip_rot[0]),
                    int(grip_y - rh / 2 - grip_rot[1])))

    # === BODY -- a broad squat barrel, mass sitting LOW ======================
    body = [(cx - int(34 * s), cy - int(30 * s)),
            (cx + int(34 * s), cy - int(30 * s)),
            (cx + int(40 * s), cy + int(20 * s)),
            (cx + int(30 * s), cy + int(54 * s)),
            (cx - int(30 * s), cy + int(54 * s)),
            (cx - int(40 * s), cy + int(20 * s))]
    triad_blob(surf, STRAW, body,
               core_pts=[(cx + int(4 * s), cy - int(28 * s)),
                         (cx + int(38 * s), cy + int(18 * s)),
                         (cx + int(28 * s), cy + int(52 * s)),
                         (cx + int(2 * s), cy + int(52 * s))],
               sheen_pts=[(cx - int(32 * s), cy - int(28 * s)),
                          (cx - int(10 * s), cy - int(28 * s)),
                          (cx - int(16 * s), cy + int(20 * s)),
                          (cx - int(36 * s), cy + int(18 * s))],
               ow=max(1, int(1.9 * s)))
    # belly node-grooves -> the body is itself cured culm (twin-grooved bands)
    for i in range(2):
        gy = cy - int(6 * s) + i * int(22 * s)
        pygame.draw.line(surf, STRAW_DD, (cx - int(30 * s), gy),
                         (cx + int(32 * s), gy), max(1, int(2 * s)))
        pygame.draw.line(surf, STRAW_DD, (cx - int(28 * s), gy + int(5 * s)),
                         (cx + int(30 * s), gy + int(5 * s)), max(1, int(1.6 * s)))
    # HARD gold-leaf grain cracks on the chest (the sparkle, 2-tone stepped)
    gold_crack(surf, cx - int(20 * s), cy - int(22 * s), 26 * s, math.radians(100), s, 1)
    gold_crack(surf, cx + int(8 * s), cy + int(4 * s), 22 * s, math.radians(78), s, -1)
    gold_crack(surf, cx - int(6 * s), cy + int(30 * s), 18 * s, math.radians(92), s, 1)

    # === short stout LEGS planted wide (bottom-heavy stance) =================
    for sgn in (-1, 1):
        lx = cx + sgn * int(18 * s)
        leg = [(lx - int(12 * s), cy + int(48 * s)),
               (lx + int(12 * s), cy + int(48 * s)),
               (lx + int(14 * s), cy + int(78 * s)),
               (lx - int(14 * s), cy + int(78 * s))]
        triad_blob(surf, STRAW, leg,
                   core_pts=[(lx + int(2 * s), cy + int(48 * s)),
                             (lx + int(14 * s), cy + int(78 * s)),
                             (lx + int(2 * s), cy + int(78 * s))],
                   sheen_pts=[(lx - int(12 * s), cy + int(48 * s)),
                              (lx - int(4 * s), cy + int(48 * s)),
                              (lx - int(6 * s), cy + int(78 * s)),
                              (lx - int(14 * s), cy + int(78 * s))],
                   ow=max(1, int(1.6 * s)))
        foot = [(lx - int(16 * s), cy + int(76 * s)),
                (lx + int(18 * s), cy + int(76 * s)),
                (lx + int(16 * s), cy + int(86 * s)),
                (lx - int(14 * s), cy + int(86 * s))]
        triad_blob(surf, STRAW_D, foot, ow=max(1, int(1.4 * s)))
        for k in (-0.5, 0.1, 0.7):
            tx = lx + int(k * 20 * s)
            pygame.draw.line(surf, STRAW_DD, (tx, cy + int(80 * s)),
                             (tx, cy + int(86 * s)), max(1, int(1.6 * s)))

    # === ARMS -- both stout straw arms reach up-right to grip the diagonal ====
    # haft low at the body; the brute hauls the club over its shoulder. Both
    # fists clamp the haft near the grip point so the diagonal club reads held.
    for sgn, dy in ((-1, int(6 * s)), (1, -int(12 * s))):
        sx = cx + sgn * int(28 * s)
        sy = cy - int(16 * s)
        gx = grip_x + int(2 * s)
        gy = grip_y + dy
        arm = [(sx - int(10 * s), sy - int(8 * s)),
               (sx + int(10 * s), sy - int(2 * s)),
               (gx + int(10 * s), gy + int(6 * s)),
               (gx - int(4 * s), gy + int(12 * s)),
               (sx - int(12 * s), sy + int(12 * s))]
        triad_blob(surf, STRAW, arm,
                   core_pts=[(sx, sy + int(2 * s)), (gx + int(8 * s), gy + int(4 * s)),
                             (gx - int(2 * s), gy + int(10 * s)), (sx - int(4 * s), sy + int(8 * s))],
                   ow=max(1, int(1.6 * s)))
        triad_circle(surf, STRAW, (gx, gy + int(4 * s)), max(3, int(8 * s)),
                     ow=max(1, int(1.4 * s)), sheen=True, core=False)

    # === HEAD last -- big chibi ogre head owns the top of the body ===========
    head_c = (cx - int(4 * s), cy - int(48 * s))
    pygame.draw.rect(surf, INK, (head_c[0] - int(11 * s), head_c[1] + int(14 * s),
                                 int(22 * s), int(16 * s)))
    pygame.draw.rect(surf, STRAW, (head_c[0] - int(9 * s), head_c[1] + int(14 * s),
                                   int(18 * s), int(16 * s)))
    oni_face(surf, head_c[0], head_c[1], int(26 * s), s)


# -- the kanabo-totem -> pillar mirror -----------------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The kanabo IS the pillar: a fat knotted culm shaft of LOCKED stud-ringed
    node bands = the tileable shaft; the ENLARGED gnarled root-ball + collar =
    the deliberate gap-edge terminal cap. Heavy mass low, on-axis, symmetric ->
    a clean bottom-rooted top<->bottom mirror. `cap` names the END facing the GAP.

    WHY the enlarged cap: round 1's cap was small/undersold so the gap edge
    didn't read as a deliberate terminal. The cap root-ball is now bigger than a
    shaft node and sits on its collar, pointing INTO the gap on both pillars."""
    half_w = int(15 * s)
    cap_r = int(26 * s)               # ENLARGED root-ball cap (bigger than nodes)
    cap_room = int(64 * s)
    if cap == "bottom":
        s0, s1 = top + int(4 * s), bot - cap_room
        cap_y = bot - int(34 * s)
    else:
        s0, s1 = top + cap_room, bot - int(4 * s)
        cap_y = top + int(34 * s)

    # repeating LOCKED node-segment shaft (band height + stud cadence fixed)
    span = s1 - s0
    n = max(2, int(round(span / (NODE_H_U * 2.4 * s))))
    kanabo_shaft(surf, cx, s0, s1, half_w, s, n_nodes=n)

    # gap-edge cap = the ENLARGED gnarled root-ball, mass + collar toward the gap
    if cap == "bottom":
        root_ball(surf, cx, cap_y, cap_r, s, collar=True)
    else:
        # mirror vertically so the root-ball faces UP into the gap -> proves the
        # clean top<->bottom mirror of a bottom-rooted club
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        root_ball(tmp, cx, surf.get_height() - cap_y, cap_r, s, collar=True)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, 0))


# -- compose the review sheet --------------------------------------------------
SS = 6


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def main():
    W, H = 1010, 900
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("MADAKE-ONI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "dry-timber ogre + diagonal culm KANABO  ·  club BREAKS silhouette · single ember · hard gold-leaf cracks · ROUND 2",
        True, LABEL_DIM), (270, 26))

    # === (a) BIG HERO ========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_madake_oni(big, 168 * SS, 256 * SS, 1.72 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature -- hero", True, LABEL), (104, 566))
    sheet.blit(font_sm.render("Squat straw OGRE (square brow-bar, under-fangs, warm-bone stub horns)", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("SHOULDERS a studded culm KANABO on a diagonal -- root-ball juts ABOVE the horns.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("SINGLE dominant ember eye. Sparkle = HARD 2-tone gold-leaf split-cracks (metallic).", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled -- mirrored, clean tileable shaft ==============
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (58, 52, 40), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar -- the kanabo", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("LOCKED node band + stud cadence =", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("seamless shaft; ENLARGED root-ball cap", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("points into the gap, mirrored top<->bottom", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky =====================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_madake_oni(big, 46 * SS, 54 * SS, (32 / 168.0) * SS)
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
    sheet.blit(font_sm.render("32px on night sky -- RED visible", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blacked-out 32px silhouette -- the OGRE-WITH-CLUB read TEST: a broad low
    # brute mass with a DIAGONAL club lobe breaking out of the top, never a blob
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_madake_oni(big, 46 * SS, 54 * SS, (32 / 168.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
        return sil

    sil_y = night_y + 188
    sx = panel_x + 20
    pygame.draw.rect(sheet, (214, 206, 186), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKOUT -- club lobe", True, LABEL), (sx + 104, sil_y + 30))
    sheet.blit(font_sm.render("breaks the brute silhouette", True, LABEL_DIM), (sx + 104, sil_y + 48))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 192
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 636))
    swatches = [
        (STRAW, "timber-straw"), (STRAW_D, "burnt-amber sh"),
        (GOLD, "gold-leaf split"), (GOLD_HI, "gold glint pip"),
        (EMBER, "ember eye (TINY)"), (BONE, "warm-bone horn"),
        (CLUB, "club body (darker)"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 664
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 850, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  R2 fixes: diagonal club breaks silhouette · round darker root-ball != square head · "
        "single bright ember in dark socket · 2-tone gold-leaf cracks · locked node tile + enlarged cap · warm-bone horns.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
