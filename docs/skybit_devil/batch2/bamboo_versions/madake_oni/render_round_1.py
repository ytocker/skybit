"""
Round-1 concept renderer for MADAKE-ONI — the dry-timber bamboo ogre hauling a
giant knotted culm kanabo (bamboo-versions set, concept #2). Headless Pygame;
ELEVATED pipeline (supersample SS=6 -> smoothscale) so the studded-club geometry
and node-ring banding stay crisp at downscale. Keeps the shipped house grammar:
flat fills, hard 1-2px ink keyline, dark-core -> flat-fill -> top-left rim-sheen
triad, 1px alpha-grown outline, chibi proportions, scary-CUTE pushed EPIC;
procedural-only (no gradients/PNGs/soft halos).

WHY this is the OGRE-WITH-CLUB of the bamboo brood: the other four are a
serpent-coil, a slim noble stack, a bowed snow-stalk, and a split light-stalk.
Madake-Oni is the ONLY squat brute and the ONLY warm-STRAW body. The 32px read
is bottom-heavy: a broad low ogre mass (knot-brow, jutting under-fangs, two short
bamboo-node stub horns) hoisting a thick studded culm KANABO taller than itself.

WHY the palette is held warm-DESATURATED straw, NOT bronze: the AD pin is that
Madake must never drift into Kappa's turtle-bronze. So the timber-straw and
burnt-amber shade carry only a small chroma; the ONLY saturated accent is a TINY
ember-red eye. The sparkle lane is gold-leaf split-cracks rendered as HARD
METALLIC stepped facets (sharp little gold lozenges with a white catch-pip), NOT
a soft glow -- the deliberate foil to Kaguya's soft stepped moon-halo so the two
gold accents never collide.

WHY the kanabo IS the pillar: a fat knotted culm shaft with raised node-rings
ringed by stud-knobs = the tileable repeat band; the gnarled root-ball head =
the creature-derived gap-edge cap. Heavy mass low and on-axis -> clean
bottom-rooted top<->bottom mirror.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* -- only colour math + the triad/outline
helpers cloned from the lineage template.
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
GOLD      = (238, 206, 120)   # gold-leaf split accent (HARD metallic facets)
GOLD_HI   = (252, 238, 176)   # hot gold-leaf catch-pip (the metallic glint)
CREAM     = (236, 222, 178)   # husk-cream (fang/horn highlight, inner culm)
SHEEN     = (244, 222, 160)   # hottest straw sheen (top-left rim)
EMBER     = (206,  72,  52)   # ember-red eye -- the ONLY saturated accent, TINY
EMBER_HOT = (244, 150, 110)   # tiny hot pip inside the ember eye
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
    """A gold-leaf split-crack rendered as a SHARP STEPPED metallic facet -- a
    thin gold lozenge along the grain with a single white catch-pip, NOT a soft
    glow. WHY hard-metallic: the AD pin splits Madake's gold (hard stepped) from
    Kaguya's soft stepped moon-halo so the two gold accents never collide. Each
    crack is its own little angular sliver of struck gold leaf catching the
    light along a grain split."""
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca
    hw = max(1.0, length * 0.10)
    tip = (x + ca * length, y + sa * length)
    # thin gold lozenge with one offset belly -> a struck, faceted sliver
    belly = (x + ca * length * 0.42, y + sa * length * 0.42)
    leaf = [
        (x, y),
        (belly[0] + px * hw * flip, belly[1] + py * hw * flip),
        (tip[0], tip[1]),
        (belly[0] - px * hw * 0.5 * flip, belly[1] - py * hw * 0.5 * flip),
    ]
    pygame.draw.polygon(surf, STRAW_DD, leaf)            # the dark split it sits in
    inset = [(int(x + (qx - x) * 0.82), int(y + (qy - y) * 0.82)) for qx, qy in leaf]
    pygame.draw.polygon(surf, GOLD, inset)               # the gold leaf
    # one HARD white catch-pip up the leading facet -> the metallic glint
    pip = (int(x + ca * length * 0.30 + px * hw * 0.4 * flip),
           int(y + sa * length * 0.30 + py * hw * 0.4 * flip))
    pygame.draw.circle(surf, GOLD_HI, pip, max(1, int(hw * 0.7)))


def node_band(surf, cx, y, half_w, s, studs=True):
    """One culm NODE-RING: the twin raised rings of a real madake node (lower
    sheath-scar + upper nodal ridge) drawn as a banded swell, ringed with stud
    knobs when `studs` (the kanabo stud band = the repeat tell). WHY twin
    grooves: it's the unmistakable bamboo read AND the stud-band repeat at once."""
    # the swollen node collar (slightly fatter than the shaft)
    nb = int(half_w * 1.18)
    coll = [(cx - nb, y + int(6 * s)),
            (cx - int(nb * 0.9), y - int(7 * s)),
            (cx + int(nb * 0.9), y - int(7 * s)),
            (cx + nb, y + int(6 * s)),
            (cx + int(nb * 0.9), y + int(13 * s)),
            (cx - int(nb * 0.9), y + int(13 * s))]
    triad_blob(surf, STRAW, coll,
               core_pts=[(cx, y + int(2 * s)), (cx + nb, y + int(6 * s)),
                         (cx + int(nb * 0.9), y + int(13 * s)), (cx, y + int(11 * s))],
               sheen_pts=[(cx - nb, y + int(6 * s)),
                          (cx - int(nb * 0.5), y - int(6 * s)),
                          (cx - int(nb * 0.2), y - int(4 * s)),
                          (cx - int(nb * 0.7), y + int(5 * s))],
               ow=max(1, int(1.4 * s)))
    # twin transverse node grooves (sheath scar + nodal ridge) -- the bamboo tell
    pygame.draw.line(surf, STRAW_DD, (cx - int(nb * 0.82), y - int(2 * s)),
                     (cx + int(nb * 0.82), y - int(2 * s)), max(1, int(1.8 * s)))
    pygame.draw.line(surf, STRAW_DD, (cx - int(nb * 0.82), y + int(8 * s)),
                     (cx + int(nb * 0.82), y + int(8 * s)), max(1, int(1.8 * s)))
    if studs:
        # stud knobs around the ring -> the kanabo studded band (the repeat tell)
        for k in (-1.0, -0.55, 0.0, 0.55, 1.0):
            sxk = cx + int(k * nb * 0.92)
            syk = y + int(2 * s) + int(abs(k) * 3 * s)
            triad_circle(surf, STRAW, (sxk, syk), max(2, int(3.4 * s)),
                         ow=max(1, int(1.0 * s)), sheen=True, core=False)


# -- the gnarled ROOT-BALL head (kanabo butt -> reused for hero club + cap) ----
def root_ball(surf, cx, cy, r, s):
    """The gnarled root-ball head that crowns the kanabo: a lumpy bulbous
    culm-root mass (the heavy striking knob) drawn as an irregular triad-lit
    polygon so it reads ROOT, not a smooth ball. Gold-leaf cracks split across
    it. WHY: this is the creature-derived gap-edge cap -- the heavy business
    end of the club -- so it must read as a knotted root, never a head."""
    knob = [(cx - int(r * 0.96), cy),
            (cx - int(r * 0.70), cy - int(r * 0.78)),
            (cx - int(r * 0.18), cy - int(r * 1.02)),
            (cx + int(r * 0.46), cy - int(r * 0.86)),
            (cx + int(r * 0.94), cy - int(r * 0.34)),
            (cx + int(r * 1.00), cy + int(r * 0.34)),
            (cx + int(r * 0.62), cy + int(r * 0.84)),
            (cx - int(r * 0.06), cy + int(r * 1.00)),
            (cx - int(r * 0.66), cy + int(r * 0.78)),
            (cx - int(r * 0.98), cy + int(r * 0.30))]
    triad_blob(surf, STRAW, knob,
               core_pts=[(cx + int(r * 0.10), cy + int(r * 0.10)),
                         (cx + int(r * 0.92), cy + int(r * 0.10)),
                         (cx + int(r * 0.58), cy + int(r * 0.78)),
                         (cx - int(r * 0.04), cy + int(r * 0.86)),
                         (cx + int(r * 0.20), cy + int(r * 0.30))],
               sheen_pts=[(cx - int(r * 0.86), cy - int(r * 0.04)),
                          (cx - int(r * 0.56), cy - int(r * 0.66)),
                          (cx - int(r * 0.18), cy - int(r * 0.50)),
                          (cx - int(r * 0.46), cy + int(r * 0.10))],
               ow=max(1, int(1.8 * s)))
    # gnarled root knots -- a few dark gouges so the lump reads knotted root
    for dx_f, dy_f, rr in ((-0.34, -0.30, 0.20), (0.30, 0.06, 0.24), (-0.06, 0.42, 0.18)):
        pygame.draw.circle(surf, STRAW_DD,
                           (cx + int(r * dx_f), cy + int(r * dy_f)), max(1, int(r * rr)))
        pygame.draw.circle(surf, STRAW,
                           (cx + int(r * dx_f) - max(1, int(r * 0.05)),
                            cy + int(r * dy_f) - max(1, int(r * 0.05))),
                           max(1, int(r * rr * 0.5)))
    # HARD gold-leaf split-cracks across the root-ball (the sparkle, metallic)
    gold_crack(surf, cx - int(r * 0.5), cy - int(r * 0.2), r * 0.9, math.radians(28), s, 1)
    gold_crack(surf, cx + int(r * 0.1), cy + int(r * 0.1), r * 0.7, math.radians(-52), s, -1)


# -- the studded culm KANABO (the club -- reused for hero + pillar shaft) ------
def kanabo_shaft(surf, cx, y0, y1, half_w, s, n_nodes=4, butt="bottom"):
    """A fat knotted culm shaft segmented by raised stud-ringed node bands. WHY
    this IS the pillar repeat: each node-segment (flat straw fill, dark-core
    groove, top-left sheen, gold-leaf cracks down the grain) tiles cleanly, and
    the stud-ringed node band is the kanabo tell repeated down the shaft."""
    # the long culm body
    body = [(cx - half_w, y0), (cx + half_w, y0),
            (cx + half_w, y1), (cx - half_w, y1)]
    triad_blob(surf, STRAW, body,
               core_pts=[(cx + int(half_w * 0.1), y0), (cx + half_w, y0),
                         (cx + half_w, y1), (cx + int(half_w * 0.1), y1)],
               sheen_pts=[(cx - half_w, y0),
                          (cx - int(half_w * 0.55), y0),
                          (cx - int(half_w * 0.55), y1),
                          (cx - half_w, y1)],
               ow=max(1, int(1.6 * s)))
    # gold-leaf split-cracks running the grain (hard metallic glints, sparse)
    span = y1 - y0
    for fy, fx, fl, fa, fp in ((0.16, -0.32, 0.14, 96, 1), (0.40, 0.30, 0.12, 84, -1),
                               (0.66, -0.22, 0.13, 100, 1), (0.86, 0.28, 0.11, 80, -1)):
        gold_crack(surf, cx + int(half_w * fx), y0 + int(span * fy),
                   span * fl, math.radians(fa), s, fp)
    # raised stud-ringed node bands spaced down the shaft = the repeat band
    for i in range(n_nodes):
        ny = y0 + int(span * (i + 0.5) / n_nodes)
        node_band(surf, cx, ny, half_w, s, studs=True)


# -- the ogre FACE (knot-brow, fangs, stub horns, the single ember eye-pair) ---
def oni_face(surf, cx, cy, r, s):
    """The squat ogre head: a broad knot-browed straw skull, two short
    bamboo-node STUB horns, jutting under-fangs, and the ONLY saturated accent
    -- a TINY ember-red eye-pair pinned under a heavy knot brow. WHY tiny ember:
    the AD pin keeps the single saturated accent small so the body stays warm
    desaturated straw and never bronzes."""
    # broad chibi cranium (wider than tall -> brutish ogre mass)
    head = [(cx - int(r * 1.06), cy - int(r * 0.30)),
            (cx - int(r * 0.74), cy - int(r * 0.92)),
            (cx, cy - int(r * 1.04)),
            (cx + int(r * 0.74), cy - int(r * 0.92)),
            (cx + int(r * 1.06), cy - int(r * 0.30)),
            (cx + int(r * 0.92), cy + int(r * 0.60)),
            (cx + int(r * 0.40), cy + int(r * 1.00)),
            (cx - int(r * 0.40), cy + int(r * 1.00)),
            (cx - int(r * 0.92), cy + int(r * 0.60))]
    triad_blob(surf, STRAW, head,
               core_pts=[(cx + int(r * 0.10), cy - int(r * 0.10)),
                         (cx + int(r * 1.0), cy - int(r * 0.20)),
                         (cx + int(r * 0.84), cy + int(r * 0.58)),
                         (cx + int(r * 0.10), cy + int(r * 0.90))],
               sheen_pts=[(cx - int(r * 0.96), cy - int(r * 0.24)),
                          (cx - int(r * 0.62), cy - int(r * 0.78)),
                          (cx - int(r * 0.30), cy - int(r * 0.58)),
                          (cx - int(r * 0.56), cy + int(r * 0.20))],
               ow=max(1, int(1.8 * s)))

    # two short bamboo-NODE stub horns (twin-grooved, the bamboo tell on horns)
    for sgn in (-1, 1):
        hx = cx + sgn * int(r * 0.62)
        hy = cy - int(r * 0.94)
        horn = [(hx - sgn * int(r * 0.20), hy + int(r * 0.10)),
                (hx - sgn * int(r * 0.14), hy - int(r * 0.42)),
                (hx + sgn * int(r * 0.10), hy - int(r * 0.50)),
                (hx + sgn * int(r * 0.22), hy + int(r * 0.06))]
        triad_blob(surf, CREAM, horn,
                   core_pts=[(hx + sgn * int(r * 0.02), hy - int(r * 0.10)),
                             (hx + sgn * int(r * 0.10), hy - int(r * 0.46)),
                             (hx + sgn * int(r * 0.20), hy + int(r * 0.04))],
                   ow=max(1, int(1.2 * s)))
        # node groove across the stub horn (it's a bamboo-node nub)
        pygame.draw.line(surf, STRAW_DD,
                         (hx - sgn * int(r * 0.16), hy - int(r * 0.18)),
                         (hx + sgn * int(r * 0.14), hy - int(r * 0.22)),
                         max(1, int(1.4 * s)))

    # heavy KNOT BROW -- a thick straw ridge with a centre dip (the oni scowl),
    # overhanging the eyes so the ember reads recessed under bone
    brow = [(cx - int(r * 0.86), cy - int(r * 0.30)),
            (cx - int(r * 0.30), cy - int(r * 0.46)),
            (cx, cy - int(r * 0.24)),                  # centre dip (the frown)
            (cx + int(r * 0.30), cy - int(r * 0.46)),
            (cx + int(r * 0.86), cy - int(r * 0.30)),
            (cx + int(r * 0.70), cy - int(r * 0.06)),
            (cx, cy - int(r * 0.04)),
            (cx - int(r * 0.70), cy - int(r * 0.06))]
    triad_blob(surf, STRAW_D, brow,
               sheen_pts=[(cx - int(r * 0.80), cy - int(r * 0.28)),
                          (cx - int(r * 0.36), cy - int(r * 0.40)),
                          (cx - int(r * 0.30), cy - int(r * 0.16)),
                          (cx - int(r * 0.66), cy - int(r * 0.12))],
               ow=max(1, int(1.2 * s)))
    # a knot-gouge on the brow centre -> the burl knot of cured timber
    pygame.draw.circle(surf, STRAW_DD, (cx, cy - int(r * 0.22)), max(1, int(r * 0.10)))

    # the TINY ember-red eye-pair -- the ONLY saturated accent, deep under brow
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.44)
        ey = cy + int(r * 0.04)
        # a small angular eye pit bored in the straw, glowing ember (kept TINY)
        pit = [(ex - sgn * int(r * 0.14), ey - int(r * 0.12)),
               (ex + sgn * int(r * 0.20), ey - int(r * 0.08)),
               (ex + sgn * int(r * 0.10), ey + int(r * 0.14))]
        pygame.draw.polygon(surf, INK, pit)
        pygame.draw.polygon(surf, STRAW_DD, pit)
        pygame.draw.circle(surf, EMBER, (ex, ey), max(1, int(r * 0.10)))
        pygame.draw.circle(surf, EMBER_HOT, (ex - sgn * max(1, int(r * 0.03)),
                                             ey - max(1, int(r * 0.03))),
                           max(1, int(r * 0.04)))

    # broad flat nose-knot + the jutting UNDER-FANGS (chibi-scary tusk grin)
    pygame.draw.circle(surf, STRAW_DD, (cx, cy + int(r * 0.40)), max(1, int(r * 0.12)))
    # wide grim mouth line
    pygame.draw.line(surf, INK, (cx - int(r * 0.46), cy + int(r * 0.66)),
                     (cx + int(r * 0.46), cy + int(r * 0.66)), max(2, int(2.4 * s)))
    for sgn in (-1, 1):
        fx = cx + sgn * int(r * 0.30)
        fang = [(fx - int(r * 0.12), cy + int(r * 0.62)),
                (fx + int(r * 0.12), cy + int(r * 0.62)),
                (fx, cy + int(r * 0.98))]   # tusk juts UP from the lower jaw
        triad_blob(surf, CREAM, fang,
                   sheen_pts=[(fx - int(r * 0.08), cy + int(r * 0.64)),
                              (fx, cy + int(r * 0.64)),
                              (fx - int(r * 0.02), cy + int(r * 0.82))],
                   ow=max(1, int(1.0 * s)))


# -- the ogre-with-club hero ---------------------------------------------------
def draw_madake_oni(surf, cx, cy, s):
    """Squat straw-tan oni hoisting a studded culm kanabo taller than its body.
    `s` = unit scale around a ~150-unit figure. Drawn back-to-front: the raised
    club behind one shoulder -> the broad low body -> arms gripping the haft ->
    head last. Heavy mass sits LOW (bottom-heavy ogre read)."""

    # === the KANABO raised over the shoulder (taller than the ogre) ==========
    # WHY drawn first/behind: the brute grips it across the body; the club's
    # heavy root-ball butt rides high while the haft drops into both fists.
    club_cx = cx + int(36 * s)
    haft_top = cy - int(96 * s)
    haft_bot = cy + int(8 * s)
    cw = int(13 * s)
    kanabo_shaft(surf, club_cx, haft_top + int(20 * s), haft_bot, cw, s, n_nodes=3)
    # the gnarled root-ball striking head crowns the club
    root_ball(surf, club_cx, haft_top + int(2 * s), int(22 * s), s)

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
    # a couple of hard gold-leaf grain cracks on the chest (the sparkle)
    gold_crack(surf, cx - int(18 * s), cy - int(20 * s), 22 * s, math.radians(96), s, 1)
    gold_crack(surf, cx + int(14 * s), cy + int(28 * s), 18 * s, math.radians(86), s, -1)

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
        # broad three-toed ogre foot
        foot = [(lx - int(16 * s), cy + int(76 * s)),
                (lx + int(18 * s), cy + int(76 * s)),
                (lx + int(16 * s), cy + int(86 * s)),
                (lx - int(14 * s), cy + int(86 * s))]
        triad_blob(surf, STRAW_D, foot, ow=max(1, int(1.4 * s)))
        for k in (-0.5, 0.1, 0.7):
            tx = lx + int(k * 20 * s)
            pygame.draw.line(surf, STRAW_DD, (tx, cy + int(80 * s)),
                             (tx, cy + int(86 * s)), max(1, int(1.6 * s)))

    # === ARMS -- two stout straw arms gripping the haft ======================
    # near arm reaches across to grip the club low; far arm grips it high
    for sgn, gy in ((-1, cy + int(2 * s)), (1, cy - int(20 * s))):
        sx = cx + sgn * int(30 * s)
        sy = cy - int(20 * s)
        gx = club_cx - int(6 * s)
        arm = [(sx - int(10 * s), sy - int(8 * s)),
               (sx + int(10 * s), sy - int(2 * s)),
               (gx + int(8 * s), gy + int(8 * s)),
               (gx - int(6 * s), gy + int(12 * s)),
               (sx - int(12 * s), sy + int(12 * s))]
        triad_blob(surf, STRAW, arm,
                   core_pts=[(sx, sy + int(2 * s)), (gx + int(6 * s), gy + int(6 * s)),
                             (gx - int(4 * s), gy + int(10 * s)), (sx - int(4 * s), sy + int(8 * s))],
                   ow=max(1, int(1.6 * s)))
        # a fat fist knot at the grip
        triad_circle(surf, STRAW, (gx, gy + int(4 * s)), max(3, int(8 * s)),
                     ow=max(1, int(1.4 * s)), sheen=True, core=False)

    # === HEAD last -- big chibi ogre head owns the top of the body ===========
    head_c = (cx - int(2 * s), cy - int(48 * s))
    # short thick neck knot
    pygame.draw.rect(surf, INK, (head_c[0] - int(11 * s), head_c[1] + int(14 * s),
                                 int(22 * s), int(16 * s)))
    pygame.draw.rect(surf, STRAW, (head_c[0] - int(9 * s), head_c[1] + int(14 * s),
                                   int(18 * s), int(16 * s)))
    oni_face(surf, head_c[0], head_c[1], int(26 * s), s)


# -- the kanabo-totem -> pillar mirror -----------------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The kanabo IS the pillar: a fat knotted culm shaft with stud-ringed node
    bands = the tileable shaft; the gnarled root-ball striking head = the
    creature-derived gap-edge cap. Heavy mass low, on-axis, symmetric -> a clean
    bottom-rooted top<->bottom mirror.

    `cap` names the END that faces the GAP."""
    half_w = int(15 * s)
    cap_room = int(46 * s)
    if cap == "bottom":
        s0, s1 = top + int(4 * s), bot - cap_room
        cap_y = bot - int(28 * s)
    else:
        s0, s1 = top + cap_room, bot - int(4 * s)
        cap_y = top + int(28 * s)

    # repeating stud-ringed node-segment shaft (the tileable band)
    span = s1 - s0
    n = max(2, int(span / (44 * s)))
    kanabo_shaft(surf, cx, s0, s1, half_w, s, n_nodes=n)

    # gap-edge cap = the gnarled root-ball striking head, mass toward the gap
    if cap == "bottom":
        root_ball(surf, cx, cap_y, int(20 * s), s)
    else:
        # mirror vertically so the root-ball faces UP toward the gap -> proves
        # the clean top<->bottom mirror of a bottom-rooted club
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        root_ball(tmp, cx, surf.get_height() - cap_y, int(20 * s), s)
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
        "dry-timber bamboo ogre + culm KANABO  ·  OGRE-WITH-CLUB · warm-straw body · tiny ember eye · hard gold-leaf cracks · round 1",
        True, LABEL_DIM), (270, 26))

    # === (a) BIG HERO ========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_madake_oni(big, 172 * SS, 250 * SS, 1.72 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature -- hero", True, LABEL), (104, 566))
    sheet.blit(font_sm.render("Squat straw OGRE (knot-brow, jutting under-fangs, bamboo-node stub horns)", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("hoisting a studded culm KANABO taller than its body; heavy mass sits LOW.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("ONLY accent = TINY ember eye. Sparkle = HARD gold-leaf split-cracks (metallic).", True, LABEL_DIM), (14, 622))

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
    sheet.blit(font_sm.render("knotted culm + stud-ringed node bands =", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("repeat shaft; gnarled root-ball striking", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("head caps each gap edge -- mirror visible", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky =====================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_madake_oni(big, 48 * SS, 52 * SS, (32 / 168.0) * SS)
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

    # blacked-out 32px silhouette -- the OGRE-WITH-CLUB read TEST: a broad low
    # brute mass beside a tall studded shaft, never an ambiguous blob
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_madake_oni(big, 48 * SS, 52 * SS, (32 / 168.0) * SS)
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
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette --", True, LABEL), (sx + 104, sil_y + 30))
    sheet.blit(font_sm.render("must read OGRE-WITH-CLUB, mass LOW", True, LABEL_DIM), (sx + 104, sil_y + 48))

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
        (EMBER, "ember eye (TINY)"), (CREAM, "husk-cream"),
        (STRAW_DD, "deep amber hollow"), (INK, "ink keyline"),
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
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (34,24,18) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-CUTE · procedural-only · warm-DESAT straw, NO bronze.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
