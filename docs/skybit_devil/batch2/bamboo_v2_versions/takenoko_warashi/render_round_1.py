"""
Round-1 concept renderer for TAKENOKO-WARASHI — the armored sprout-child that
erupts from the earth (bamboo v2 set, concept #1). Headless Pygame; ELEVATED
pipeline (supersample SS=6 -> smoothscale) so the layered husk-plate facets stay
crisp at downscale.

This set is a DELIBERATE DEPARTURE from the chibi/flat first bamboo set: it must
read REALISTIC and botanically accurate. So the technique is REALISTIC
proportions (no chibi big-head), PROCEDURAL only (no PNGs), and the house triad
is pushed to 4-6 HARD STEPPED value bands per form for a sculpted, near-
volumetric read — NEVER smooth gradients (smooth ramps boil to mud at true
32px). Radial glow accents only. Hard ink keyline + 1px alpha-grown outline.

WHY this is the SHEATH-SCALE CONE-WARRIOR of the set: it is the ONLY upward-
tapering CONE of overlapping pointed husk-plates — a fat, bottom-WIDE, apex-
narrow rocket of lacquered takenoko sheath-armor, a fierce little face peeking
from the apex notch, two stubby arms. Bottom-weighted (the torn soil-root ball
hugs the ground); never top-heavy.

WHY the palette is takenoko sprout-tan/cream, warm-earth, MATTE: it holds clear
of Madake's gold-leaf straw by being cooler/earthier and MATTE (no metallic
glint). A SINGLE fresh-shoot lime apex node-ring is the ONLY green in the whole
form — tiny, at the crown — so the eye locks there.

AD HARD CONSTRAINT honoured: must NOT drift toward "pinecone." Every husk-plate
KEEPS a curling hair-fringe along its tip and a pale CREAM ligule line at the
scale-top; the speckle is texture stippled INSIDE a fill band, NEVER its own
value step (it boils into noise at 32px); the lime apex node-ring is the sole
green eye-lock.

WHY the shoot IS the pillar: stacked sheath-plate rings = the repeatable shaft
band; the gap-edge cap = the fresh green apex-tip with its tiny lime node-rings;
the lower mirror = the torn soil-root ball. Bottom-rooted, mass low.

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
# 4-6 hard stepped bands per form are mixed FROM these anchors so the whole form
# reads as one warm-earth family. No metallic glint anywhere (the Madake gap).
HUSK      = (198, 168, 112)   # husk-tan base fill (the dominant mass)
HUSK_SH   = (140, 104,  58)   # umber-speckle shade (the deep facet step)
HUSK_MID  = (170, 134,  82)   # derived mid step between base + shade
LIGULE    = (236, 222, 176)   # cream ligule-edge / scale-top line (pale band)
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
    """Dark brown speckle stippled INSIDE a fill band — texture, NEVER its own
    value step (the AD ruling: a discrete speckle band boils into noise at 32px).
    Seeded so the texture is stable across renders. Dots are clipped to the
    polygon by point-in-polygon so they never leak past the facet edge."""
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
    while placed < n and tries < n * 8:
        tries += 1
        px = rng.uniform(x0, x1)
        py = rng.uniform(y0, y1)
        if inside(px, py):
            pygame.draw.circle(surf, color, (int(px), int(py)),
                               max(1, int(1.1 * s)))
            placed += 1


# ── ONE husk sheath-plate — the core repeated form (a discrete stepped facet) ─
def husk_plate(surf, cx, base_y, half_w, height, s, lit_left=True,
               speckle_seed=0, fringe=True):
    """A broad triangular overlapping sheath-scale: wide rounded base, tapering
    to a blunt point, lit as 4 HARD stepped value bands (no gradient) for a
    sculpted facet — dark shade flank, mid body, base fill, and a pale CREAM
    LIGULE line capping the scale-top. A curling HAIR-FRINGE sprouts from the
    tip. Dark speckle is stippled INSIDE the body band only. These two botanical
    tells (ligule line + hair-fringe) on EVERY plate are what keep the form from
    drifting to a pinecone."""
    apex = (cx, base_y - height)
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
    # BAND 1 (darkest) — the whole plate floored in umber shade (right flank read)
    pygame.draw.polygon(surf, HUSK_SH, plate)
    # BAND 2 (mid) — a left-weighted facet covering most of the plate
    side = -1 if lit_left else 1
    mid = [
        (cx - half_w * 0.86, base_y - height * 0.02),
        (cx - half_w * 0.80, base_y - height * 0.44),
        (cx - half_w * 0.26, base_y - height * 0.86),
        apex,
        (cx + half_w * 0.10, base_y - height * 0.84),
        (cx + half_w * 0.40, base_y - height * 0.40),
        (cx + half_w * 0.46, base_y - height * 0.02),
    ]
    pygame.draw.polygon(surf, HUSK_MID, mid)
    # BAND 3 (base fill) — the broad lit body, the dominant tan
    body = [
        (cx - half_w * 0.74, base_y - height * 0.04),
        (cx - half_w * 0.66, base_y - height * 0.46),
        (cx - half_w * 0.20, base_y - height * 0.82),
        (cx, base_y - height * 0.90),
        (cx + half_w * 0.04, base_y - height * 0.78),
        (cx + half_w * 0.22, base_y - height * 0.40),
        (cx + half_w * 0.20, base_y - height * 0.04),
    ]
    pygame.draw.polygon(surf, HUSK, body)
    # speckle INSIDE the body band only (texture, not a value step)
    speckle(surf, body, HUSK_SH, max(5, int(half_w * 0.16)), s, speckle_seed)
    speckle(surf, body, ROOT, max(3, int(half_w * 0.08)), s, speckle_seed + 7)
    # BAND 4 (pale CREAM LIGULE line) — a discrete bright sliver capping the
    # scale-top, the botanical signature that says "sheath," not "cone-scale"
    lig = [
        (cx - half_w * 0.30, base_y - height * 0.86),
        (cx, base_y - height * 0.965),
        (cx + half_w * 0.30, base_y - height * 0.86),
        (cx + half_w * 0.18, base_y - height * 0.80),
        (cx, base_y - height * 0.88),
        (cx - half_w * 0.18, base_y - height * 0.80),
    ]
    pygame.draw.polygon(surf, LIGULE, lig)
    # curling HAIR-FRINGE sprouting from the plate tip — short hooked bristles
    # that arc to one side (the curl), the anti-pinecone tell on every plate
    if fringe:
        n = 3
        for i in range(n):
            t = (i - (n - 1) / 2.0) / max(1, (n - 1) / 2.0)
            root = (cx + t * half_w * 0.22, base_y - height * 0.94)
            ln = height * (0.20 + 0.05 * (1 - abs(t)))
            # a curling hook: two segments, the second kinked sideways
            mid_pt = (root[0] + t * half_w * 0.10, root[1] - ln * 0.6)
            tip = (mid_pt[0] + (0.45 + 0.2 * t) * half_w * 0.30,
                   mid_pt[1] - ln * 0.35)
            pygame.draw.line(surf, INK, root, mid_pt, max(2, int(1.6 * s)))
            pygame.draw.line(surf, INK, mid_pt, tip, max(2, int(1.4 * s)))
            pygame.draw.line(surf, HUSK_SH, root, mid_pt, max(1, int(0.9 * s)))
            pygame.draw.line(surf, LIGULE, mid_pt, tip, max(1, int(0.8 * s)))


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
    """A short stubby arm thrust out from the lower cone — a fist of bound husk,
    stepped, with a small ligule cuff. Stubby + low so the figure never reads
    top-heavy."""
    ex = sx + sign * 16 * s
    ey = sy + 10 * s
    arm = [
        (sx, sy - 7 * s),
        (ex, ey - 9 * s),
        (ex + sign * 9 * s, ey),
        (ex, ey + 9 * s),
        (sx, sy + 9 * s),
    ]
    pygame.draw.polygon(surf, INK, arm)
    pygame.draw.polygon(surf, HUSK_SH, arm)
    pygame.draw.polygon(surf, HUSK, inset(arm, 0.78))
    # a small fist knot at the end (stepped)
    fist = (int(ex + sign * 6 * s), int(ey))
    pygame.draw.circle(surf, INK, fist, int(8 * s))
    pygame.draw.circle(surf, HUSK_SH, fist, int(7 * s))
    pygame.draw.circle(surf, HUSK, (fist[0] - sign * int(2 * s),
                                    fist[1] - int(2 * s)), int(5 * s))
    # ligule cuff line at the shoulder
    pygame.draw.line(surf, LIGULE, (sx, sy - 6 * s), (sx, sy + 8 * s),
                     max(1, int(1.4 * s)))


# ── the fresh-green apex node-ring — the SOLE green eye-lock ──────────────────
def lime_apex(surf, cx, cy, r, s):
    """The single fresh-shoot LIME apex node — the ONLY green in the whole form,
    tiny, at the crown, with a soft radial glow so the eye locks there. A short
    emerging shoot-tip with one or two node-rings."""
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
    `s` = unit scale around a ~150-unit-tall figure."""
    # geometry of the cone: 5 overlapping rings of plates, bottom-wide -> narrow
    # each ring: (centre y above base, ring half-width, plate height, plate count)
    rings = [
        (12 * s,  46 * s, 30 * s, 5),   # widest base ring
        (34 * s,  40 * s, 30 * s, 5),
        (56 * s,  32 * s, 28 * s, 4),
        (78 * s,  24 * s, 26 * s, 3),
        (98 * s,  15 * s, 24 * s, 3),   # narrow apex ring (face sits just above)
    ]

    # root ball FIRST (behind the lowest plate ring)
    root_ball(surf, cx, base_y - 2 * s, 40 * s, s)

    # plate rings bottom-to-top; within a ring lay plates left-to-right with
    # slight overlap so the whole ring reads as one banded sheath layer
    seed = 1
    for ri, (yc, hw, ph, count) in enumerate(rings):
        by = base_y - yc
        # plates fanned across the ring width, slightly splayed at the edges
        for i in range(count):
            t = (i - (count - 1) / 2.0) / max(1, (count - 1) / 2.0)
            px = cx + t * hw * 0.92
            # outer plates lean outward (the splayed sheath look); plate width
            # scales so they overlap into one continuous banded ring
            pw = hw * (0.62 if count > 3 else 0.74)
            # alternate which side is lit per plate for a faceted, sculpted read
            husk_plate(surf, int(px), int(by), int(pw), int(ph), s,
                       lit_left=(t <= 0), speckle_seed=seed)
            seed += 1

    # stubby fierce arms low on the cone (ring 2 height), thrust outward
    arm_y = base_y - 40 * s
    stub_arm(surf, cx - int(38 * s), arm_y, -1, s)
    stub_arm(surf, cx + int(38 * s), arm_y, +1, s)

    # the apex notch: the small fierce face peeks out just below the lime tip,
    # framed by the topmost plate-ring's inner edge
    face_cy = base_y - int(104 * s)
    sprout_face(surf, cx, face_cy, int(12 * s), s)

    # the SOLE green: fresh lime node-tip emerging at the very crown
    lime_apex(surf, cx, base_y - int(126 * s), int(8 * s), s)


# ── the shoot-pillar (cap + clean top<->bottom mirror) ────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The shoot IS the pillar. Stacked sheath-plate RINGS = the repeatable shaft
    band. The gap-edge cap = the fresh green apex-tip with its tiny lime node-
    rings. The lower mirror = the torn soil-root ball. Bottom-rooted; mass low.

    `cap` names the END facing the GAP: 'top' = green apex-tip cap points up at
    the gap; 'bottom' = root ball faces down (the natural rooted base)."""
    shaft_w = int(34 * s)
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

    # repeated sheath-plate rings down the shaft — each ring is one banded layer
    pitch = int(30 * s)
    y = ring_hi
    seed = 50
    while y >= ring_lo:
        # a ring of 4 overlapping plates spanning the shaft width
        for i in range(4):
            t = (i - 1.5) / 1.5
            px = cx + t * shaft_w * 0.92
            husk_plate(surf, int(px), int(y), int(shaft_w * 0.62),
                       int(26 * s), s, lit_left=(t <= 0), speckle_seed=seed)
            seed += 1
        y -= pitch

    # the torn soil-root ball mirror at the rooted (bottom) end
    if cap == "top":
        root_ball(surf, cx, root_y, shaft_w, s)
    else:
        # root faces the gap below: draw at the bottom too (rooted base toward gap)
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
        "armored sprout-child  ·  SHEATH-SCALE CONE-WARRIOR · husk-plate cone · ligule line + hair-fringe per plate · lime apex (sole green) · round 1",
        True, LABEL_DIM), (330, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        # base near the bottom so the bottom-wide cone sits rooted
        draw_takenoko(big, 178 * SS, 400 * SS, 2.5 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("Bottom-WIDE, apex-narrow CONE of overlapping husk-plates — every plate keeps a", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("pale CREAM ligule line + curling hair-fringe (anti-pinecone). Fierce face peeks from", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("the apex notch; single LIME node-tip is the ONLY green (eye-lock); torn soil-root base.", True, LABEL_DIM), (14, 622))

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
        # figure ~150 units tall -> fit into 32px chip
        draw_takenoko(big, 48 * SS, 80 * SS, (32 / 150.0) * SS)
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
    sheet.blit(font_sm.render("must read bottom-WIDE CONE-warrior", True, LABEL_DIM), (sx + 104, sil_y + 48))

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
        (HUSK, "husk-tan base"), (HUSK_SH, "umber-speckle sh"),
        (LIGULE, "cream ligule"), (ROOT, "soil-umber root"),
        (LIME, "lime apex (sole green)"), (SKIN, "sprout face"),
        (HUSK_MID, "mid step"), (INK, "ink keyline"),
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
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  REALISTIC (non-chibi) · 4-6 HARD stepped value bands per form (NO gradients) · "
        "hard ink keyline (28,22,30) · 1px grown outline · speckle INSIDE a fill band · lime apex = sole green · procedural-only · MATTE (no metallic glint).",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
