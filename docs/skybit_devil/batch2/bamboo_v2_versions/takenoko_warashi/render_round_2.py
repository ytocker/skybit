"""
Round-2 concept renderer for TAKENOKO-WARASHI — the armored sprout-child that
erupts from the earth (bamboo v2 set, concept #1). Headless Pygame; ELEVATED
pipeline (supersample SS=6 -> smoothscale) so the layered husk-plate facets stay
crisp at downscale.

This set is a DELIBERATE DEPARTURE from the chibi/flat first bamboo set: it must
read REALISTIC and botanically accurate. Technique is REALISTIC proportions (no
chibi big-head), PROCEDURAL only (no PNGs), the house triad pushed to 4-6 HARD
STEPPED value bands per form — NEVER smooth gradients (smooth ramps boil to mud
at true 32px). Radial glow accents only. Hard ink keyline + 1px alpha outline.

WHY this is the SHEATH-SCALE CONE-WARRIOR of the set: it is the ONLY upward-
tapering CONE of overlapping pointed husk-plates — a fat, bottom-WIDE, apex-
narrow rocket of MATTE takenoko sheath-armor, a fierce little face peeking from
the apex notch, two stubby arms. Bottom-weighted (the torn soil-root ball hugs
the ground); never top-heavy.

WHY the palette is takenoko sprout-tan/cream, warm-earth, MATTE: it holds clear
of Madake's gold-leaf straw by being cooler/earthier and MATTE (no metallic
glint) — the cream reads PAPERY, not lacquered. A SINGLE fresh-shoot lime apex
node-ring is the ONLY green in the whole form so the eye locks there.

ROUND-2 changes vs round-1 (AD verdict ITERATE; realism + KIND kept):
  1. SPECKLE DEMOTED (the GATE): ~40% fewer dots, smaller + lower-contrast, mixed
     to sit INSIDE the husk-tan fill band — never a darker value LAYER. At 32px
     it vanishes into flat tan and the PLATE EDGES carry the read.
  2. LIGULE survives 32px: every plate-top gets a true 1px pale-cream band STEP
     (drawn as a discrete band, sized to hold at downscale), plus 2-3 BOLD curling
     fringe hairs — the day chip reads fringed-husk, not smooth-scale.
  3. 3 plate ROWS only, BIGGER + HARDER-STEPPED: a 4-band facet (highlight / base
     / mid / shade) per plate so STEPPED VALUE carries the volume, not the speckle.
  4. Day-32px chip widened ~10% at the base + brighter ligule edges (anti-pinecone
     insurance on the weakest deliverable).
  5. Arms resolved: a clear stubby-arm silhouette break (bigger, lower, angled).
  6. MATTE throughout — no metallic glint anywhere.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the triad/outline
/glow helpers cloned from the lineage templates.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief, takenoko sprout-tan/cream, warm-earth MATTE) ─
# 4 hard stepped bands per plate are mixed FROM these anchors so the whole form
# reads as one warm-earth family. No metallic glint anywhere (the Madake gap).
HUSK_HI   = (224, 200, 148)   # NEW band-0 highlight (lit crown of each facet)
HUSK      = (198, 168, 112)   # husk-tan base fill (the dominant mass)
HUSK_MID  = (170, 134,  82)   # derived mid step between base + shade
HUSK_SH   = (140, 104,  58)   # umber shade (the deep facet step)
# WHY a dedicated speckle tone close to HUSK: the GATE ruling — the speckle must
# read as fine texture INSIDE the tan band, never as a darker VALUE layer. This
# sits only ~one notch off HUSK so at 32px it dissolves into flat tan.
SPECK     = (180, 150,  98)   # low-contrast in-band speckle (near HUSK, not umber)
LIGULE    = (236, 222, 176)   # cream ligule-edge / scale-top line (pale band)
LIGULE_HI = (248, 238, 202)   # brightest ligule (the 32px anti-pinecone edge)
ROOT      = ( 96,  70,  44)   # deep soil-umber root (the torn base + soil crumbs)
ROOT_DK   = ( 64,  46,  28)   # deepest soil hollow
LIME      = (150, 196,  96)   # fresh-shoot lime apex node-ring — the ONLY green
LIME_HI   = (190, 222, 140)   # lime sheen (still inside the single green accent)
LIME_DK   = (104, 150,  64)   # lime shade
SKIN      = (210, 176, 120)   # the sprout-child's small face (warm husk-kin tan)
SKIN_SH   = (150, 112,  66)
INK       = ( 28,  22,  30)   # hard ink keyline (pinned)

# review-sheet chrome (kept off-palette so it never reads as the creature)
BG        = ( 78,  72,  62)   # warm-neutral earth backdrop
PANEL     = ( 58,  54,  46)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 234, 220)
LABEL_DIM = (198, 188, 168)

SS = 6


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def grow_outline(surf, color, px):
    """1px (post-downscale) ink keyline grown from the alpha mask — the house
    silhouette POP."""
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


def radial_glow(radius, color, alpha_center=200, falloff=2.0):
    """Soft radial accent (apex lime node-glow only). Cloned from necrarch."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


def _centroid(poly):
    gx = sum(p[0] for p in poly) / len(poly)
    gy = sum(p[1] for p in poly) / len(poly)
    return gx, gy


def inset(poly, t):
    gx, gy = _centroid(poly)
    return [(int(gx + (px - gx) * t), int(gy + (py - gy) * t))
            for (px, py) in poly]


def speckle(surf, poly, color, n, s, rng_seed):
    """DEMOTED in-band speckle (the GATE): a low-contrast tone close to HUSK,
    stippled sparsely INSIDE the fill band so it reads as fine paper texture, not
    a darker value LAYER. ~40% fewer dots than round-1 and smaller, so at true
    32px it vanishes into flat tan and the PLATE EDGES carry the read. Seeded so
    the texture is stable; clipped to the polygon so dots never leak past edges."""
    import random
    rng = random.Random(rng_seed)
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)

    def inside(px, py):
        c = False
        j = len(poly) - 1
        for i in range(len(poly)):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if ((yi > py) != (yj > py)) and \
               (px < (xj - xi) * (py - yi) / ((yj - yi) or 1e-9) + xi):
                c = not c
            j = i
        return c

    placed = 0
    tries = 0
    # smaller dots than round-1 (0.7x radius) so they stay sub-pixel at 32px
    rad = max(1, int(0.7 * s))
    while placed < n and tries < n * 8:
        tries += 1
        px = rng.uniform(x0, x1)
        py = rng.uniform(y0, y1)
        if inside(px, py):
            pygame.draw.circle(surf, color, (int(px), int(py)), rad)
            placed += 1


# ── ONE husk sheath-plate — the core repeated form (a discrete stepped facet) ─
def husk_plate(surf, cx, base_y, half_w, height, s, lit_left=True,
               speckle_seed=0, fringe=True):
    """A broad triangular overlapping sheath-scale: wide rounded base, tapering
    to a blunt point, lit as 4 HARD STEPPED value bands (highlight / base / mid /
    shade — NO gradient) so STEPPED VALUE carries the facet volume. A true 1px
    pale-CREAM LIGULE band STEPS across the scale-top and a BOLD curling HAIR-
    FRINGE sprouts from the tip. Low-contrast in-band speckle textures the body
    only. These two botanical tells (ligule band + bold fringe) on EVERY plate
    are what keep the form from drifting to a pinecone at 32px."""
    apex = (cx, base_y - height)
    side = -1 if lit_left else 1
    # the plate outline: a broad shield, wider at the base, blunt-pointed top
    plate = [
        (cx - half_w, base_y),
        (cx - half_w * 0.92, base_y - height * 0.42),
        (cx - half_w * 0.34, base_y - height * 0.88),
        apex,
        (cx + half_w * 0.34, base_y - height * 0.88),
        (cx + half_w * 0.92, base_y - height * 0.42),
        (cx + half_w, base_y),
    ]
    pygame.draw.polygon(surf, INK, plate)
    # BAND 3 (darkest SHADE) — the whole plate floored in umber (the deep step)
    pygame.draw.polygon(surf, HUSK_SH, plate)
    # BAND 2 (MID) — a side-weighted facet covering most of the plate, the
    # shaded flank stepping toward the lit side
    mid = [
        (cx - half_w * 0.86, base_y - height * 0.02),
        (cx - half_w * 0.80, base_y - height * 0.44),
        (cx - half_w * 0.26, base_y - height * 0.86),
        apex,
        (cx + half_w * 0.10, base_y - height * 0.84),
        (cx + half_w * 0.40, base_y - height * 0.40),
        (cx + half_w * 0.46, base_y - height * 0.02),
    ]
    if not lit_left:
        mid = [(2 * cx - mx, my) for (mx, my) in mid]
    pygame.draw.polygon(surf, HUSK_MID, mid)
    # BAND 1 (BASE fill) — the broad body, the dominant tan
    body = [
        (cx - half_w * 0.74, base_y - height * 0.04),
        (cx - half_w * 0.66, base_y - height * 0.46),
        (cx - half_w * 0.20, base_y - height * 0.82),
        (cx, base_y - height * 0.90),
        (cx + half_w * 0.04, base_y - height * 0.78),
        (cx + half_w * 0.22, base_y - height * 0.40),
        (cx + half_w * 0.20, base_y - height * 0.04),
    ]
    if not lit_left:
        body = [(2 * cx - bx, by) for (bx, by) in body]
    pygame.draw.polygon(surf, HUSK, body)
    # BAND 0 (HIGHLIGHT) — a hard lit crown-sliver on the lit flank, the brightest
    # step; this is what gives a sculpted faceted read so the speckle never has to
    hi = [
        (cx + side * half_w * 0.02, base_y - height * 0.10),
        (cx + side * half_w * 0.10, base_y - height * 0.52),
        (cx + side * half_w * 0.18, base_y - height * 0.78),
        (cx, base_y - height * 0.86),
        (cx + side * half_w * 0.40, base_y - height * 0.34),
        (cx + side * half_w * 0.36, base_y - height * 0.08),
    ]
    pygame.draw.polygon(surf, HUSK_HI, hi)
    # DEMOTED speckle INSIDE the body band only (low-contrast, sparse) — texture,
    # NEVER a value step. ~40% fewer dots than round-1.
    speckle(surf, body, SPECK, max(3, int(half_w * 0.09)), s, speckle_seed)
    # a true 1px pale-CREAM LIGULE band STEPPING across the scale-top — drawn as a
    # discrete band (not speckle), sized to hold at 32px (the anti-pinecone edge)
    lig = [
        (cx - half_w * 0.42, base_y - height * 0.82),
        (cx, base_y - height * 0.965),
        (cx + half_w * 0.42, base_y - height * 0.82),
        (cx + half_w * 0.26, base_y - height * 0.74),
        (cx, base_y - height * 0.84),
        (cx - half_w * 0.26, base_y - height * 0.74),
    ]
    pygame.draw.polygon(surf, LIGULE, lig)
    # a brighter inner ligule sliver so the cream edge survives the downscale
    lig_hi = [
        (cx - half_w * 0.26, base_y - height * 0.86),
        (cx, base_y - height * 0.95),
        (cx + half_w * 0.26, base_y - height * 0.86),
        (cx, base_y - height * 0.89),
    ]
    pygame.draw.polygon(surf, LIGULE_HI, lig_hi)
    # BOLD curling HAIR-FRINGE sprouting from the plate tip — fewer, THICKER,
    # higher-arcing hooked bristles than round-1 so the fringed edge still reads
    # as a notch/fringe at 32px (the anti-pinecone tell on every plate)
    if fringe:
        n = 3
        for i in range(n):
            t = (i - (n - 1) / 2.0) / max(1, (n - 1) / 2.0)
            root = (cx + t * half_w * 0.26, base_y - height * 0.92)
            ln = height * (0.30 + 0.07 * (1 - abs(t)))
            # a curling hook: two segments, the second kinked sideways (the curl)
            mid_pt = (root[0] + t * half_w * 0.14, root[1] - ln * 0.62)
            tip = (mid_pt[0] + (0.55 + 0.25 * t) * half_w * 0.40,
                   mid_pt[1] - ln * 0.30)
            pygame.draw.line(surf, INK, root, mid_pt, max(3, int(2.6 * s)))
            pygame.draw.line(surf, INK, mid_pt, tip, max(2, int(2.2 * s)))
            pygame.draw.line(surf, HUSK_SH, root, mid_pt, max(2, int(1.4 * s)))
            pygame.draw.line(surf, LIGULE, mid_pt, tip, max(1, int(1.1 * s)))


# ── the fierce sprout-child face peeking from the apex notch ──────────────────
def sprout_face(surf, cx, cy, r, s):
    """A small FIERCE young earth-spirit face peeking from the apex notch —
    realistic-proportioned (small head relative to the armored cone, NOT chibi),
    angry knit brow, two hard slit eyes, a snarling set mouth. Warm husk-kin
    skin tone, stepped (not gradient)."""
    head = [
        (cx - r, cy - r * 0.2),
        (cx - r * 0.7, cy - r),
        (cx + r * 0.7, cy - r),
        (cx + r, cy - r * 0.2),
        (cx + r * 0.6, cy + r),
        (cx - r * 0.6, cy + r),
    ]
    pygame.draw.polygon(surf, INK, head)
    pygame.draw.polygon(surf, SKIN_SH, head)        # band 1 shade
    pygame.draw.polygon(surf, SKIN, inset(head, 0.82))  # band 2 lit fill
    # angry knit brow — a hard chevron of shade above the eyes
    brow = [
        (cx - r * 0.7, cy - r * 0.18),
        (cx, cy - r * 0.02),
        (cx + r * 0.7, cy - r * 0.18),
        (cx + r * 0.5, cy - r * 0.36),
        (cx, cy - r * 0.22),
        (cx - r * 0.5, cy - r * 0.36),
    ]
    pygame.draw.polygon(surf, SKIN_SH, brow)
    # two hard slit eyes (down-angled, fierce)
    for sgn in (-1, 1):
        ex = cx + sgn * r * 0.42
        ey = cy + r * 0.06
        eye = [
            (ex - sgn * r * 0.30, ey - r * 0.04),
            (ex + sgn * r * 0.06, ey + r * 0.16),
            (ex - sgn * r * 0.04, ey + r * 0.22),
            (ex - sgn * r * 0.30, ey + r * 0.10),
        ]
        pygame.draw.polygon(surf, INK, eye)
    # snarling set mouth — a short hard down-bar
    pygame.draw.line(surf, INK,
                     (cx - r * 0.34, cy + r * 0.56),
                     (cx + r * 0.34, cy + r * 0.50), max(2, int(1.8 * s)))


# ── one stubby fierce arm (a small fist of bound husk) ────────────────────────
def stub_arm(surf, sx, sy, sign, s):
    """A short stubby arm thrust out and DOWN from the lower cone — a fist of
    bound husk, stepped, with a small ligule cuff. ROUND-2: bigger + angled
    downward + a hard fist knob so it reads as a CLEAR stubby-arm silhouette
    BREAK off the cone edge (no more half-read nub). Stubby + low so the figure
    never reads top-heavy."""
    # angle the arm down-and-out so the silhouette breaks the smooth cone line
    ex = sx + sign * 24 * s
    ey = sy + 20 * s
    arm = [
        (sx, sy - 9 * s),
        (ex, ey - 11 * s),
        (ex + sign * 12 * s, ey - 1 * s),
        (ex + sign * 8 * s, ey + 12 * s),
        (sx, sy + 11 * s),
    ]
    pygame.draw.polygon(surf, INK, arm)
    pygame.draw.polygon(surf, HUSK_SH, arm)
    pygame.draw.polygon(surf, HUSK, inset(arm, 0.74))
    # a hard fist knob at the end — a clear rounded silhouette stop (stepped, matte)
    fist = (int(ex + sign * 9 * s), int(ey + 4 * s))
    pygame.draw.circle(surf, INK, fist, int(11 * s))
    pygame.draw.circle(surf, HUSK_SH, fist, int(9 * s))
    pygame.draw.circle(surf, HUSK, (fist[0] - sign * int(2 * s),
                                    fist[1] - int(2 * s)), int(6 * s))
    pygame.draw.circle(surf, HUSK_HI, (fist[0] - sign * int(3 * s),
                                       fist[1] - int(3 * s)), int(3 * s))
    # ligule cuff line at the shoulder
    pygame.draw.line(surf, LIGULE, (sx, sy - 8 * s), (sx, sy + 10 * s),
                     max(2, int(1.8 * s)))


# ── the fresh-green apex node-ring — the SOLE green eye-lock ──────────────────
def lime_apex(surf, cx, cy, r, s):
    """The single fresh-shoot LIME apex node — the ONLY green in the whole form,
    tiny, at the crown, with a soft radial glow so the eye locks there. A short
    emerging shoot-tip with one or two node-rings. MATTE elsewhere; this is the
    sole place a soft glow lives."""
    # soft lime glow halo (the only radial accent on the figure)
    g = radial_glow(int(r * 2.0), LIME, alpha_center=120, falloff=2.4)
    surf.blit(g, (cx - g.get_width() // 2, cy - g.get_height() // 2),
              special_flags=pygame.BLEND_ADD)
    # a small upward shoot-tip cone
    tip = [
        (cx - r * 0.8, cy + r * 0.9),
        (cx, cy - r * 1.6),
        (cx + r * 0.8, cy + r * 0.9),
    ]
    pygame.draw.polygon(surf, INK, tip)
    pygame.draw.polygon(surf, LIME_DK, tip)
    pygame.draw.polygon(surf, LIME, inset(tip, 0.74))
    # one bright node-ring band across the shoot (the fresh node)
    pygame.draw.line(surf, LIME_DK, (cx - r * 0.6, cy + r * 0.1),
                     (cx + r * 0.6, cy + r * 0.1), max(2, int(2.2 * s)))
    pygame.draw.line(surf, LIME_HI, (cx - r * 0.5, cy - r * 0.4),
                     (cx + r * 0.5, cy - r * 0.4), max(1, int(1.6 * s)))


# ── the torn soil-root ball (bottom mass + soil crumbs) ───────────────────────
def root_ball(surf, cx, cy, half_w, s):
    """The torn soil-root ball clinging at the base — deep soil-umber, ragged,
    with loose soil crumbs scattered below. Anchors the mass LOW (bottom-rooted,
    never top-heavy)."""
    ball = [
        (cx - half_w, cy - 8 * s),
        (cx - half_w * 0.6, cy - 14 * s),
        (cx - half_w * 0.2, cy - 9 * s),
        (cx + half_w * 0.3, cy - 13 * s),
        (cx + half_w * 0.7, cy - 7 * s),
        (cx + half_w, cy - 11 * s),
        (cx + half_w * 0.8, cy + 8 * s),
        (cx + half_w * 0.3, cy + 14 * s),
        (cx - half_w * 0.3, cy + 12 * s),
        (cx - half_w * 0.7, cy + 16 * s),
        (cx - half_w * 0.9, cy + 6 * s),
    ]
    pygame.draw.polygon(surf, INK, ball)
    pygame.draw.polygon(surf, ROOT_DK, ball)      # band 1 deep
    pygame.draw.polygon(surf, ROOT, inset(ball, 0.82))  # band 2 fill
    # a few hairy torn roots dangling
    for i in range(5):
        t = (i - 2) / 2.0
        rx = cx + t * half_w * 0.7
        ry = cy + 10 * s
        tip = (rx + t * 6 * s, ry + (16 + 6 * abs(t)) * s)
        pygame.draw.line(surf, INK, (rx, ry), tip, max(2, int(1.8 * s)))
        pygame.draw.line(surf, ROOT, (rx, ry), tip, max(1, int(1.0 * s)))
    # loose soil crumbs scattered below
    import random
    rng = random.Random(99)
    for _ in range(max(6, int(half_w * 0.5))):
        cxp = cx + rng.uniform(-half_w, half_w)
        cyp = cy + rng.uniform(6 * s, 24 * s)
        pygame.draw.circle(surf, ROOT_DK, (int(cxp), int(cyp)),
                           max(1, int(rng.uniform(1, 2.4) * s)))


# ── the cone-warrior hero ─────────────────────────────────────────────────────
def draw_takenoko(surf, cx, base_y, s):
    """The armored sprout-child as a fat upward-tapering CONE of overlapping
    pointed husk-plates: bottom-WIDE, apex-narrow. Built back-to-front and
    bottom-to-top so each higher plate-ring overlaps the one below (real shoot
    sheath layering). Root ball anchors the base; the small fierce face peeks
    from the apex notch under the lime node-tip; two stubby arms low on the cone.
    `s` = unit scale around a ~150-unit-tall figure.

    ROUND-2: cut to 3 plate ROWS, BIGGER + harder-stepped, so the 4-band facet
    value carries the volume and the stacked PLATE EDGES dominate the read."""
    # geometry of the cone: 3 BIG overlapping rings of plates, bottom-wide->narrow
    # (centre y above base, ring half-width, plate height, plate count)
    rings = [
        (16 * s,  50 * s, 46 * s, 4),   # widest base ring (bottom-WIDE, ~10% wider)
        (52 * s,  38 * s, 44 * s, 3),   # mid ring
        (88 * s,  24 * s, 40 * s, 3),   # narrow apex ring (face sits just above)
    ]

    # root ball FIRST (behind the lowest plate ring)
    root_ball(surf, cx, base_y - 2 * s, 44 * s, s)

    # plate rings bottom-to-top; within a ring lay plates left-to-right with
    # slight overlap so the whole ring reads as one banded sheath layer
    seed = 1
    for ri, (yc, hw, ph, count) in enumerate(rings):
        by = base_y - yc
        for i in range(count):
            t = (i - (count - 1) / 2.0) / max(1, (count - 1) / 2.0)
            px = cx + t * hw * 0.86
            # plate width scales so plates overlap into one continuous banded ring
            pw = hw * (0.74 if count > 3 else 0.86)
            # lit toward the centre-line so the cone reads as one rounded volume
            husk_plate(surf, int(px), int(by), int(pw), int(ph), s,
                       lit_left=(t <= 0), speckle_seed=seed)
            seed += 1

    # stubby fierce arms low on the cone (base ring height), thrust out + down —
    # a CLEAR stubby-arm silhouette break off the wide base
    arm_y = base_y - 44 * s
    stub_arm(surf, cx - int(46 * s), arm_y, -1, s)
    stub_arm(surf, cx + int(46 * s), arm_y, +1, s)

    # the apex notch: the small fierce face peeks out just below the lime tip,
    # framed by the topmost plate-ring's inner edge
    face_cy = base_y - int(102 * s)
    sprout_face(surf, cx, face_cy, int(13 * s), s)

    # the SOLE green: fresh lime node-tip emerging at the very crown
    lime_apex(surf, cx, base_y - int(126 * s), int(8 * s), s)


# ── the shoot-pillar (cap + clean top<->bottom mirror) ────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The shoot IS the pillar. Stacked sheath-plate RINGS = the repeatable shaft
    band. The gap-edge cap = the fresh green apex-tip with its tiny lime node-
    rings. The lower mirror = the torn soil-root ball. Bottom-rooted; mass low.

    `cap` names the END facing the GAP: 'top' = green apex-tip cap points up at
    the gap; 'bottom' = root ball faces down (the natural rooted base)."""
    shaft_w = int(36 * s)
    # central ink rod the sheath rings thread onto
    pygame.draw.rect(surf, INK, (cx - int(2 * s), top, int(4 * s), bot - top))

    cap_room = int(56 * s)
    if cap == "top":
        ring_lo, ring_hi = top + cap_room, bot - int(8 * s)
        root_y = bot - int(20 * s)
        apex_y = top + int(28 * s)
    else:
        ring_lo, ring_hi = top + int(8 * s), bot - cap_room
        root_y = bot - int(20 * s)
        apex_y = top + int(28 * s)

    # repeated sheath-plate rings down the shaft — each ring is one banded layer.
    # ROUND-2: bigger plates + wider pitch so the stacked-ring rhythm reads.
    pitch = int(40 * s)
    y = ring_hi
    seed = 50
    while y >= ring_lo:
        # a ring of 3 overlapping plates spanning the shaft width
        for i in range(3):
            t = (i - 1.0) / 1.0
            px = cx + t * shaft_w * 0.86
            husk_plate(surf, int(px), int(y), int(shaft_w * 0.74),
                       int(38 * s), s, lit_left=(t <= 0), speckle_seed=seed)
            seed += 1
        y -= pitch

    # the torn soil-root ball mirror at the rooted (bottom) end
    root_ball(surf, cx, root_y, shaft_w, s)

    # the fresh green apex-tip cap at the OTHER end (the gap-edge cap when cap=top)
    if cap == "top":
        lime_apex(surf, cx, apex_y, int(11 * s), s)
        # a couple of small node-rings just under the lime tip
        for k in range(2):
            ny = apex_y + int((16 + k * 12) * s)
            pygame.draw.line(surf, LIME_DK, (cx - shaft_w * 0.4, ny),
                             (cx + shaft_w * 0.4, ny), max(1, int(2.0 * s)))
    else:
        lime_apex(surf, cx, apex_y, int(11 * s), s)


# ── compose the review sheet ─────────────────────────────────────────────────
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
    sheet.blit(font_big.render("TAKENOKO-WARASHI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "armored sprout-child · SHEATH-SCALE CONE-WARRIOR · 3 BIG husk-plate rows · ligule BAND + bold fringe per plate · demoted in-band speckle · MATTE · round 2",
        True, LABEL_DIM), (330, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_takenoko(big, 178 * SS, 400 * SS, 2.5 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("Bottom-WIDE, apex-narrow CONE of 3 BIG overlapping husk-plate rows — 4-band stepped", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("facet (hi/base/mid/shade) carries the volume; pale CREAM ligule BAND + bold curling fringe", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("per plate (anti-pinecone). Clear stubby arms; single LIME node-tip = the ONLY green.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, clean tileable shaft ================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 0.95 * SS, cap="top")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    # the bottom segment is the top one mirrored vertically (proves clean mirror)
    bot_seg = grow_outline(pygame.transform.smoothscale(
        pygame.transform.flip(top_big, False, True), (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (48, 44, 38), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — the shoot", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked sheath-plate rings = repeat band;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("fresh lime apex-tip = gap-edge cap; torn", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("soil-root ball = lower mirror. Mirror visible.", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_takenoko(big, 48 * SS, 80 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky (weakest — sharpened)", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, night_y + 27))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blacked-out 32px silhouette — the CONE-read TEST: must read as a fat
    # bottom-wide apex-narrow cone-warrior, never a ball / pinecone / blob
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_takenoko(big, 48 * SS, 80 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        return mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))

    sil_y = night_y + 188
    sx = panel_x + 20
    pygame.draw.rect(sheet, (214, 206, 188), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 30))
    sheet.blit(font_sm.render("bottom-WIDE cone + arm break", True, LABEL_DIM), (sx + 104, sil_y + 48))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.30 * SS, cap="top")
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
        (HUSK_HI, "husk highlight"), (HUSK, "husk-tan base"),
        (HUSK_MID, "mid step"), (HUSK_SH, "umber shade"),
        (SPECK, "in-band speckle"), (LIGULE, "cream ligule"),
        (ROOT, "soil-umber root"), (LIME, "lime apex (sole green)"),
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
        "ELEVATED pipeline: SS=6 supersample -> smoothscale. REALISTIC (non-chibi) · 4-band HARD stepped facet per plate (hi/base/mid/shade, NO gradients) · "
        "ink keyline (28,22,30) + 1px grown outline · DEMOTED in-band speckle · ligule BAND + bold fringe per plate · lime apex = sole green · MATTE (no metallic glint).",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
