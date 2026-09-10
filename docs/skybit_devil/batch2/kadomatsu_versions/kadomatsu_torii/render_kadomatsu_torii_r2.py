"""
Round-2 concept renderer for KADOMATSU-TORII — the living gate of stacked cut
culms (Kadomatsu brood, concept #2). Headless Pygame; ELEVATED-REALISM pipeline
(supersample SS=6 -> smoothscale) cloned VERBATIM from the parent KADOMATSU-SHIN
harness so the slant-cut hollow-ring mouths and node geometry stay crisp at the
true-32px downscale.

WHY this is the GATE direction of the brood: it is the ONLY negative-space form
in the brood or the four bamboo-v2 siblings. The read is an OPEN ⛩-frame —
two BOUND-CULM-BUNDLE uprights + a heavy horizontal LINTEL + a smaller TIE-BEAM
below it — with a WIDE OPEN DOORWAY between the legs as the silhouette.
Everything else in the set is a solid mass; this banks its distinctness on the
hole, so openness is pushed HARD (wide doorway, relatively thin members).

ROUND 2 — driven by the art-director ITERATE verdict. Banked from R1 and kept:
the negative-space doorway + the blackout open-gate read. The two HARD-GATE
fixes this round are deployment-and-material:

  1. BOUND-BAMBOO, NOT TIMBER. Each upright leg is now a BUNDLE seen side-on —
     2-3 VERTICAL value-stepped culm STRIPES, each with its own node collars +
     branch-stub nubs, plus a straw lashing band at each lintel-to-leg joint.
     R1's smooth single-shaft legs read as painted dowels; that failed the
     "it is a bamboo plant" north star.
  2. FOUR-CORNER disc DEPLOYMENT. Two discs now terminate the upright LEG-TOPS
     (each bundle ends in its own cut disc BEFORE it meets the lintel) and two
     ride the LINTEL ENDS → the form reads "open rectangle pinned by four cream
     nodes." R1 bunched all four on the lintel line with zero cream at the feet.

Plus: discs enlarged + spread + CUT_HI pushed to the brightest value (four
discrete cream dots at 32px, not one horizontal blob); discs re-cut as steep
SOGI slants (offset bright cavity, hard steps — matching the parent
`diagonal_cut`) so they stop reading as glossy buttons; the vermilion narrowed
to a TRUE cord/sash band so the cream out-ranks it as focal; the stray white
nubs under the beams removed; and the single-leg pillar's lower-mirror foot
tidied so its gap-cap cream disc stays the brightest point.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the helpers
cloned from the parent kadomatsu_shin harness.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE — cloned VERBATIM from kadomatsu_shin/render_round_2.py ─────
# Same warm fresh-cut festive green family, same cut-CREAM focal POP, same
# auspicious New-Year accent kit. The held-apart shrine-cord red reuses the PLUM
# family so the gate stays inside the brood palette (no new hue lane).
CULM      = (124, 188, 104)   # fresh-culm green (lifted warmer/brighter)
CULM_D    = ( 74, 138,  72)   # deep node-green shade
CULM_DD   = ( 50, 102,  56)   # deepest groove / node-collar shadow band
CULM_HI   = (172, 216, 130)   # sun-side fresh-green highlight band (warm/yellow)
CULM_HOT  = (208, 232, 158)   # hottest green sheen rail (top-left sun)
CULM_RIM  = (158, 206, 116)   # thin WARM rim-keyline on culm edges (night hold)
CULM_BACK = ( 58, 116,  62)   # back-culm body green, darkened a step (stepping)
CUT_CREAM = (224, 214, 170)   # pale diagonal-cut ring-wall (the signature POP)
# R2: CUT_HI pushed to the brightest value on the entire form so the four corner
# discs out-rank the vermilion sash and survive the 32px downscale as four dots.
CUT_HI    = (252, 248, 224)   # lit cut-rim sheen — BRIGHTEST value on the form
CUT_D     = (180, 166, 120)   # cut-ring shade (cavity-side lip)
CAVITY    = (118, 128,  92)   # the hollow inner cavity (lightened — a disc, not hole)
CAVITY_DD = ( 86,  98,  70)   # cavity floor (lightened so the cream still dominates)
STRAW     = (206, 176, 104)   # woven straw-rope collar
STRAW_D   = (150, 120,  62)   # straw shade between strands
STRAW_HI  = (234, 210, 144)   # straw highlight strand
PLUM      = (216,  80,  60)   # auspicious vermilion plum + shrine-cord (accent)
PLUM_D    = (158,  48,  40)   # plum shade
PLUM_HI   = (248, 138, 116)   # plum petal highlight
PINE      = ( 58, 104,  62)   # pine needle-fan green (cooler/darker than culm)
PINE_D    = ( 38,  74,  46)   # pine shade
PINE_HI   = ( 96, 142,  88)   # pine lit needle
GLOW      = (244, 224, 150)   # soft pale-gold blessing glow (radial, accent only)
FACE      = (240, 230, 188)   # serene bound-face plane (gold-touched cream)
FACE_D    = (196, 178, 132)   # face shade band
INK       = ( 28,  22,  30)   # hard ink keyline

BG        = ( 60,  74,  58)   # muted grove-green review backdrop
PANEL     = ( 46,  58,  46)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 230)
LABEL_DIM = (196, 204, 184)

SS = 6


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ── outline grown from the alpha mask (the house keyline) ────────────────────
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


def radial_glow(radius, color, alpha_center=200, falloff=2.0):
    """Necrarch precedent — accent-only soft bloom. Here it warms the OPEN
    doorway (the monumental gold-lit threshold) and backs the blessing-face,
    never a body fill."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


# ── one single madake CULM STRIPE — HARD STEPPED bands, no gradient ───────────
def culm_stripe(surf, cx, top, bot, half_w, s, node_pitch, body_col=CULM,
                shade_col=CULM_D, deep_col=CULM_DD, nub_side=-1):
    """ONE living-bamboo culm seen side-on: a vertical shaft lit with 4 HARD
    STEPPED value bands across its width (sheen rail | hi | fill | deep) — NO
    smooth gradient — so it reads as a turned cylinder of fresh green. Node
    rings are the two-ring madake collar, with a branch-stub NUB thrown to
    `nub_side` so each stripe reads as an individual culm, not a panel.

    WHY split out of the old single-shaft builder (R2 GATE #1): each leg is now
    a BUNDLE of 2-3 of these stripes side by side, so the legs read as bound
    bamboo seen side-on rather than one smooth painted dowel."""
    lw = max(2, int(1.4 * s))
    body = [(cx - half_w, top), (cx + half_w, top),
            (cx + half_w, bot), (cx - half_w, bot)]
    pygame.draw.polygon(surf, INK, body)
    pygame.draw.polygon(surf, body_col, body)
    hi_col = CULM_HI if body_col is CULM else lerp(body_col, CULM_HI, 0.45)
    bands = ((-1.00, -0.42, hi_col), (-0.42, -0.10, body_col),
             (-0.10, 0.46, body_col), (0.46, 1.00, shade_col))
    for x0, x1, col in bands:
        bx0 = cx + int(half_w * x0)
        bx1 = cx + int(half_w * x1)
        pygame.draw.polygon(surf, col, [
            (bx0, top), (bx1, top), (bx1, bot), (bx0, bot)])
    rail = max(1, int(half_w * 0.22))
    rail_col = CULM_HOT if body_col is CULM else CULM_HI
    pygame.draw.rect(surf, rail_col, (cx - half_w, top, rail, bot - top))
    # node collars — two-ring madake band + a side branch-stub nub per node
    ring_col = CULM_HOT if body_col is CULM else CULM_HI
    y = bot - node_pitch
    while y > top + node_pitch * 0.3:
        pygame.draw.rect(surf, deep_col,
                         (cx - half_w, y, half_w * 2, max(2, int(2.2 * s))))
        pygame.draw.rect(surf, ring_col,
                         (cx - half_w, y - max(2, int(2.4 * s)),
                          half_w * 2, max(1, int(1.6 * s))))
        nub = max(2, int(2.0 * s))
        nx = cx + nub_side * half_w
        pygame.draw.polygon(surf, shade_col, [
            (nx, y - int(0.5 * s)),
            (nx + nub_side * nub, y - nub),
            (nx + nub_side * nub, y + int(1.0 * s))])
        y -= node_pitch
    rim = max(1, int(1.0 * s))
    pygame.draw.line(surf, CULM_RIM, (cx - half_w, top), (cx - half_w, bot), rim)
    pygame.draw.line(surf, CULM_RIM, (cx + half_w, top), (cx + half_w, bot), rim)
    pygame.draw.polygon(surf, INK, body, lw)


def culm_bundle(surf, cx, top, bot, half_w, s, node_pitch):
    """A BOUND BUNDLE of culms seen side-on — the gate's upright leg (R2 GATE
    #1). Three vertical stripes packed across the leg width: a slightly recessed
    BACK stripe between two front stripes, value-stepped so the seam between
    culms reads. Returns the centre-x of each stripe so the caller can terminate
    each one in its own cut disc at the leg-top.

    WHY three not one: the brief's north star is "it IS a bamboo plant" and the
    AD flagged the R1 single shaft as a smooth painted dowel. A side-on bundle
    of discrete culms with seams + per-culm nodes + per-culm nubs is the read
    that proves bound bamboo."""
    # geometry: a wider front-left, a recessed back-centre, a front-right
    sw = int(half_w * 0.46)               # per-stripe half-width
    seam = int(sw * 0.62)
    left_cx  = cx - seam
    right_cx = cx + seam
    back_cx  = cx
    # back stripe first (drawn behind, darker, slightly shorter so the fronts
    # read as overlapping it)
    culm_stripe(surf, back_cx, top + int(2 * s), bot, int(sw * 0.86), s,
                node_pitch, body_col=CULM_BACK, shade_col=CULM_DD,
                deep_col=(40, 84, 48), nub_side=1)
    # two front stripes, nodes offset by half a pitch so the bundle reads
    # hand-bound (culms never line up perfectly)
    culm_stripe(surf, left_cx, top, bot, sw, s, node_pitch, nub_side=-1)
    culm_stripe(surf, right_cx, top, bot, sw, s, int(node_pitch * 1.06),
                nub_side=1)
    return (left_cx, back_cx, right_cx, sw)


def culm_shaft_h(surf, left, right, cy, half_h, s, node_pitch, body_col=CULM,
                 shade_col=CULM_D, deep_col=CULM_DD):
    """A HORIZONTAL bound-culm beam (the lintel + the tie-beam) — the same
    stepped-band madake construction, rotated 90°. WHY a dedicated horizontal
    builder: the beam ends are capped by their own diagonal-cut discs (the two
    LINTEL-END corner nodes) and must sit on the same surface coordinate frame
    as the uprights for the corner nodes to register. Sun lands on the TOP rail;
    the deep band is the underside so the beam reads as a turned cylinder lying
    on its side."""
    lw = max(2, int(1.6 * s))
    body = [(left, cy - half_h), (right, cy - half_h),
            (right, cy + half_h), (left, cy + half_h)]
    pygame.draw.polygon(surf, INK, body)
    pygame.draw.polygon(surf, body_col, body)
    hi_col = CULM_HI if body_col is CULM else lerp(body_col, CULM_HI, 0.45)
    bands = ((-1.00, -0.46, hi_col), (-0.46, -0.16, body_col),
             (-0.16, 0.42, body_col), (0.42, 1.00, shade_col))
    for y0, y1, col in bands:
        by0 = cy + int(half_h * y0)
        by1 = cy + int(half_h * y1)
        pygame.draw.polygon(surf, col, [
            (left, by0), (right, by0), (right, by1), (left, by1)])
    rail = max(2, int(half_h * 0.16))
    pygame.draw.rect(surf, CULM_HOT if body_col is CULM else CULM_HI,
                     (left, cy - half_h, right - left, rail))
    x = left + node_pitch
    while x < right - node_pitch * 0.3:
        pygame.draw.rect(surf, deep_col,
                         (x, cy - half_h, max(2, int(2.4 * s)), half_h * 2))
        pygame.draw.rect(surf, CULM_HOT if body_col is CULM else CULM_HI,
                         (x - max(2, int(2.6 * s)), cy - half_h,
                          max(1, int(1.8 * s)), half_h * 2))
        x += node_pitch
    rim = max(1, int(1.1 * s))
    pygame.draw.line(surf, CULM_RIM, (left, cy - half_h), (right, cy - half_h), rim)
    pygame.draw.line(surf, CULM_RIM, (left, cy + half_h), (right, cy + half_h), rim)
    pygame.draw.polygon(surf, INK, body, lw)


# ── the DIAGONAL-CUT MOUTH — the signature: steep sogi cream slant-cut ────────
def diagonal_cut(surf, cx, cy, half_w, s, dominance=1.0, lean=1):
    """The steep SOGI slant-cut culm-mouth — rebuilt for R2 to match the parent
    `diagonal_cut` cavity treatment (the AD flagged R1's pillowed glossy domes
    that read as buttons/grommets). NOT a centred glossy disc: a cut culm seen
    on a steep diagonal plane, so:

      · the cream ring-wall is an OVAL leaning along the cut (high lip one side);
      · the bright CUT_HI sheen is a hard CRESCENT on the high lip — NOT a
        concentric centred dome;
      · the inner CAVITY is OFFSET toward the LOW side (you look down into the
        hollow), with a hard-stepped dark floor — no smooth shading;
      · steps are HARD (no gradient) so it reads as a real cut, not a button.

    At 32px the downscale collapses it to one BRIGHT CREAM DOT — and these four
    are deployed at the four corners, sized large (dominance) + spread so the
    form reads "open rectangle pinned by four cream nodes." `lean` flips the
    high lip left(+1)/right(-1) so the two sides of the gate mirror."""
    ew = int((half_w + int(1.8 * s)) * (1.0 + 0.78 * dominance))
    eh = int((half_w + int(1.8 * s)) * (1.0 + 0.70 * dominance))
    outer = pygame.Rect(cx - ew, cy - eh, ew * 2, eh * 2)
    # ink seat then the full cream ring-wall
    pygame.draw.ellipse(surf, INK, outer.inflate(int(2.6 * s), int(2.6 * s)))
    pygame.draw.ellipse(surf, CUT_D, outer)
    pygame.draw.ellipse(surf, CUT_CREAM, outer.inflate(-int(1.6 * s), -int(1.6 * s)))
    # the HARD bright sheen CRESCENT riding the high lip (offset, not centred)
    hx = cx - lean * int(ew * 0.30)
    hy = cy - int(eh * 0.30)
    sheen = pygame.Rect(hx - int(ew * 0.72), hy - int(eh * 0.72),
                        int(ew * 1.44), int(eh * 1.44))
    pygame.draw.ellipse(surf, CUT_HI, sheen)
    # bite the sheen back to a crescent with the cream body offset the other way
    bite = sheen.move(lean * int(ew * 0.42), int(eh * 0.42))
    pygame.draw.ellipse(surf, CUT_CREAM, bite.inflate(-int(ew * 0.10), -int(eh * 0.10)))
    # the OFFSET inner cavity (looking down into the hollow on the LOW side)
    iw, ih = int(ew * 0.46), int(eh * 0.46)
    ccx = cx + lean * int(ew * 0.22)
    ccy = cy + int(eh * 0.24)
    cav = pygame.Rect(ccx - iw, ccy - ih, iw * 2, ih * 2)
    pygame.draw.ellipse(surf, INK, cav.inflate(int(1.6 * s), int(1.6 * s)))
    pygame.draw.ellipse(surf, CAVITY, cav)
    # hard-stepped cavity floor on the very low side — no gradient
    floor = pygame.Rect(ccx - int(iw * 0.55) + lean * int(iw * 0.18),
                        ccy - int(ih * 0.45) + int(ih * 0.55),
                        int(iw * 1.0), int(ih * 0.85))
    pygame.draw.ellipse(surf, CAVITY_DD, floor)
    pygame.draw.ellipse(surf, INK, outer, max(1, int(1.5 * s)))


# ── a woven straw-rope COLLAR band (the waist / lashing binding) ──────────────
def straw_collar(surf, cx, cy, half_w, h, s, tails=True):
    """The woven rice-straw rope: a fat band of diagonal STRANDS (alternating
    lit/shade so it reads woven, not a smooth ring). HARD STEPPED. A short paired
    knot-tail hangs straight DOWN at the centre. Here it doubles as the LASHING
    where the lintel meets each leg — the joint that proves the gate is bound
    culm, not jointed timber. `tails` suppressed on the high lashings so the
    knot-tails stay base-anchored (never top-heavy)."""
    band = pygame.Rect(cx - half_w - int(3 * s), cy - h // 2,
                       (half_w + int(3 * s)) * 2, h)
    pygame.draw.rect(surf, INK, band.inflate(int(2 * s), int(2 * s)))
    pygame.draw.rect(surf, STRAW_D, band)
    strand_w = max(3, int(4.2 * s))
    x = band.left - h
    i = 0
    while x < band.right + h:
        col = STRAW_HI if i % 3 == 0 else (STRAW if i % 3 == 1 else STRAW_D)
        pygame.draw.polygon(surf, col, [
            (x, band.bottom), (x + strand_w, band.bottom),
            (x + strand_w + h, band.top), (x + h, band.top)])
        x += strand_w
        i += 1
    pygame.draw.rect(surf, STRAW_D, (band.left, band.top, band.width, max(2, int(2 * s))))
    pygame.draw.rect(surf, INK, (band.left, band.bottom - max(2, int(2 * s)),
                                 band.width, max(2, int(2 * s))))
    pygame.draw.rect(surf, INK, band, max(1, int(1.4 * s)))
    if tails:
        for sgn in (-1, 1):
            tx = cx + sgn * int(4 * s)
            pygame.draw.polygon(surf, STRAW, [
                (tx - int(3 * s), band.bottom),
                (tx + int(3 * s), band.bottom),
                (tx + int(2 * s), band.bottom + int(11 * s)),
                (tx - int(2 * s), band.bottom + int(11 * s))])
            pygame.draw.polygon(surf, STRAW_D, [
                (tx, band.bottom),
                (tx + int(3 * s), band.bottom),
                (tx + int(2 * s), band.bottom + int(11 * s))])


# ── a pine NEEDLE-FAN (base mass + pillar cap sprig) ──────────────────────────
def pine_fan(surf, root, base_ang, spread, n, length, s, sign=1):
    """A fan of pine needles: n hard tapered needle-blades radiating from `root`,
    graded in length, alternating lit/shade so the fan reads as discrete clumps
    (NOT fuzz). Bottom-anchored base mass; a small sprig for the pillar cap."""
    for k in range(n):
        t = k / max(1, n - 1)
        a = base_ang + sign * (t - 0.5) * spread
        L = length * (0.78 + 0.22 * math.sin(t * math.pi))
        ca, sa = math.cos(a), math.sin(a)
        px, py = -sa, ca
        hw = max(2, int(2.0 * s))
        tip = (root[0] + ca * L, root[1] + sa * L)
        nd = [(root[0] + px * hw, root[1] + py * hw),
              (tip[0] + px * hw * 0.3, tip[1] + py * hw * 0.3),
              (tip[0] - px * hw * 0.3, tip[1] - py * hw * 0.3),
              (root[0] - px * hw, root[1] - py * hw)]
        col = PINE_HI if k % 2 == 0 else PINE
        pygame.draw.polygon(surf, PINE_D, [(x + 1, y + 1) for (x, y) in nd])
        pygame.draw.polygon(surf, col, nd)


# ── a vermilion PLUM blossom (base accent) ────────────────────────────────────
def plum_blossom(surf, cx, cy, r, s):
    """A five-petal red-plum blossom: HARD STEPPED petals (shade ring -> petal ->
    highlight pip) with a pale-gold pip centre. The auspicious vermilion accent,
    base-anchored only."""
    for k in range(5):
        a = math.radians(-90 + k * 72)
        px = cx + math.cos(a) * r
        py = cy + math.sin(a) * r
        pygame.draw.circle(surf, INK, (int(px), int(py)), int(r * 0.62) + 1)
        pygame.draw.circle(surf, PLUM_D, (int(px), int(py)), int(r * 0.62))
        pygame.draw.circle(surf, PLUM, (int(px), int(py)), int(r * 0.48))
        pygame.draw.circle(surf, PLUM_HI,
                           (int(px - r * 0.12), int(py - r * 0.12)), int(r * 0.18))
    pygame.draw.circle(surf, GLOW, (int(cx), int(cy)), max(2, int(r * 0.3)))


# ── the held-apart SHRINE-CORD / shimenawa-red sash across the top beam ───────
def shimenawa_cord(surf, left, right, cy, s):
    """The single vermilion shrine-cord slung across the top beam — the ONLY
    high horizontal red sash in the brood, the held-apart accent. Built in the
    PLUM family (no new hue) as a woven twist: a plum band with a hard highlight
    twist-rail + paired short shide (the zigzag paper streamers) drop at the
    thirds, so it reads as a shimenawa, not a painted stripe.

    R2: NARROWED to a true cord/sash band (the AD flagged the R1 red slab
    dominating the cream). Roughly a third of its old height, so its area sits
    UNDER the four corner cream discs and they out-rank it as the focal. Still
    base-balanced by straw + plum + pine at the feet so the figure stays
    base-anchored, never top-heavy."""
    h = int(3 * s)                         # half-height — a CORD, not a slab
    band = pygame.Rect(left, cy - h, right - left, h * 2)
    pygame.draw.rect(surf, INK, band.inflate(int(2 * s), int(2 * s)))
    pygame.draw.rect(surf, PLUM_D, band)
    # woven twist read: alternating diagonal plum highlights along the cord
    seg = max(4, int(8 * s))
    x = left
    i = 0
    while x < right:
        col = PLUM_HI if i % 2 == 0 else PLUM
        pygame.draw.polygon(surf, col, [
            (x, cy + h), (x + seg, cy + h),
            (x + seg + int(3 * s), cy - h), (x + int(3 * s), cy - h)])
        x += seg
        i += 1
    pygame.draw.rect(surf, PLUM, (band.left, cy - int(0.6 * s), band.width, max(2, int(1.6 * s))))
    pygame.draw.rect(surf, INK, band, max(1, int(1.2 * s)))
    # paired shide paper-streamer drops at the thirds (the shrine tell, kept
    # short so the cord stays a thin band)
    span = right - left
    for fx in (0.32, 0.5, 0.68):
        sx = int(left + span * fx)
        pts = [(sx - int(2.5 * s), cy + h),
               (sx + int(2.5 * s), cy + h),
               (sx + int(2.5 * s), cy + h + int(5 * s)),
               (sx - int(1 * s), cy + h + int(5 * s)),
               (sx + int(1.5 * s), cy + h + int(10 * s)),
               (sx - int(3.5 * s), cy + h + int(10 * s))]
        pygame.draw.polygon(surf, INK, [(x + 1, y + 1) for (x, y) in pts])
        pygame.draw.polygon(surf, FACE, pts)


# ── THE HERO: the open ⛩-frame gate of bound cut culms ────────────────────────
def draw_torii(surf, cx, cy, s):
    """The living torii gate: two BOUND-CULM-BUNDLE uprights + a heavy
    horizontal LINTEL capping them + a smaller TIE-BEAM below the lintel,
    framing a WIDE OPEN doorway. `s` = unit scale around a ~150-unit figure.

    R2 build order banks the negative-space read AND the four-corner deployment:
    (1) a soft gold glow fills the OPEN doorway first so the threshold reads lit;
    (2) the two BOUND-BUNDLE uprights (each = 3 striped culms side-on), stopping
    SHORT of the lintel so each bundle's tops are free to be capped;
    (3) the TWO upright LEG-TOP cut discs — each culm terminates in its own cut
    BEFORE meeting the lintel;
    (4) the lintel + tie-beam horizontals laid across the capped legs;
    (5) the TWO LINTEL-END cut discs off the beam ends → with (3) the four
    corners are now spread to the four corners, large + bright, pinning the open
    rectangle;
    (6) the NARROW vermilion shrine-cord sash on the lintel (held-apart accent,
    out-ranked by the cream);
    (7) straw lashings where the lintel meets each leg (bound-culm proof);
    (8) the base kit — pine + plum at the feet — to keep the figure base-balanced.

    Openness is pushed HARD: the doorway gap between the legs is wide and the
    members are relatively thin, so the blackout reads as an OPEN frame — the
    one negative-space silhouette in the brood."""
    # gate proportions — wide doorway, thin BUNDLED members (push openness)
    leg_hw   = int(11 * s)            # upright bundle half-width (thin)
    beam_hh  = int(11 * s)            # lintel half-height (heavy crossbar)
    tie_hh   = int(6 * s)             # tie-beam half-height (smaller)
    span     = int(58 * s)            # half-distance between the two legs (wide)
    lx, rx   = cx - span, cx + span   # leg centre-x
    top_y    = cy - int(98 * s)       # bundle culm-top (the upper corner discs)
    base_y   = cy + int(78 * s)       # foot of the legs
    lintel_y = top_y + int(26 * s)    # lintel centreline (sits below the capped tops)
    tie_y    = lintel_y + int(34 * s) # tie-beam centreline (the lower crossbar)
    node     = int(20 * s)

    # === (1) OPEN DOORWAY — faintly gold-lit threshold (the epic hook) ========
    door_w = (span - leg_hw) * 2
    gl = radial_glow(int(door_w * 0.62), GLOW, alpha_center=64, falloff=1.7)
    surf.blit(gl, (cx - gl.get_width() // 2,
                   (tie_y + base_y) // 2 - gl.get_height() // 2),
              special_flags=pygame.BLEND_ADD)

    # === (2) the two BOUND-CULM-BUNDLE UPRIGHTS (3 stripes each, side-on) ======
    # bundles stop just under the lintel so the leg-tops are free to be capped
    # by their own cut discs (the upper corner pair).
    leg_top_cut = top_y + int(8 * s)
    bundles = {}
    for legx in (lx, rx):
        bundles[legx] = culm_bundle(surf, legx, leg_top_cut, base_y, leg_hw, s, node)

    # === (3) the TWO UPRIGHT LEG-TOP cut discs (the upper corner pair) =========
    # each leg's culms terminate in a cut disc at the bundle top — the cream now
    # lives at the TOP corners (away from the lintel line), pinning the rectangle.
    for legx, lean in ((lx, 1), (rx, -1)):
        l_cx, b_cx, r_cx, sw = bundles[legx]
        diagonal_cut(surf, legx, leg_top_cut, leg_hw, s, dominance=0.86, lean=lean)

    # === (4) the HORIZONTAL beams — lintel (heavy) + tie-beam (smaller) ========
    # the lintel overhangs the legs (its ends carry the lower-OUTER corner discs)
    beam_l = lx - int(24 * s)
    beam_r = rx + int(24 * s)
    culm_shaft_h(surf, beam_l, beam_r, lintel_y, beam_hh, s, node)
    # the tie-beam runs only between the legs (a tighter inner crossbar)
    culm_shaft_h(surf, lx - int(2 * s), rx + int(2 * s), tie_y, tie_hh, s,
                 node, body_col=CULM_BACK, shade_col=CULM_DD)

    # === (5) the TWO LINTEL-END cut discs (the outer corner pair) ==============
    # facing outward off the beam ends — with (3) the four discs now sit at the
    # four corners of the open rectangle, large + bright + spread.
    diagonal_cut(surf, beam_l, lintel_y, beam_hh, s, dominance=0.94, lean=1)
    diagonal_cut(surf, beam_r, lintel_y, beam_hh, s, dominance=0.94, lean=-1)

    # === (6) the held-apart NARROW VERMILION shrine-cord sash on the lintel ====
    shimenawa_cord(surf, lx - int(2 * s), rx + int(2 * s), lintel_y + int(2 * s), s)

    # === (7) STRAW LASHINGS where the lintel meets each leg ====================
    # the bound joint that proves bamboo-culm construction, not jointed timber
    for legx in (lx, rx):
        straw_collar(surf, legx, lintel_y + int(13 * s), int(12 * s),
                     int(12 * s), s, tails=False)

    # === (8) BASE KIT — pine + plum at the feet (base-balances the red sash) ===
    for legx, sgn in ((lx, -1), (rx, 1)):
        pine_fan(surf, (legx, base_y - int(2 * s)),
                 math.radians(90 + sgn * 36), math.radians(58), 6, 30 * s, s, sign=sgn)
        pine_fan(surf, (legx + sgn * int(6 * s), base_y),
                 math.radians(90), math.radians(64), 5, 22 * s, s)
    plum_blossom(surf, lx - int(9 * s),  base_y - int(2 * s), int(7 * s), s)
    plum_blossom(surf, lx + int(9 * s),  base_y + int(6 * s), int(5 * s), s)
    plum_blossom(surf, rx + int(9 * s),  base_y - int(2 * s), int(7 * s), s)
    plum_blossom(surf, rx - int(9 * s),  base_y + int(6 * s), int(5 * s), s)


# ── the fresh diagonal-CUT pillar gap-cap (an explicit slant cut, not a point) ─
def cut_cap(surf, cx, cut_y, half_w, s):
    """The pillar's gap-edge cap: an explicit FRESH diagonal cut across the
    bundle top — here it IS one of the corner discs detached. Uses the SAME
    steep-sogi `diagonal_cut` treatment as the gate corners (R2: no more pillowed
    button), thrown large + bright so it stays the brightest point of the pillar
    chip, with a pine tuft to one side. Caller has drawn the bundle up to cut_y."""
    diagonal_cut(surf, cx, cut_y, half_w, s, dominance=0.70, lean=1)
    pine_fan(surf, (cx - half_w, cut_y - int(4 * s)), math.radians(202),
             math.radians(44), 5, 24 * s, s, sign=-1)


# ── one UPRIGHT LEG → PILLAR mirror (the leg IS the pillar verbatim) ──────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """One upright leg of the gate IS the pillar: the SAME bound-culm BUNDLE (3
    striped culms side-on) tiles the shaft; the cut bundle-end (an explicit fresh
    diagonal CUT + side pine sprig) is the detachable gap-edge cap; the straw
    lashing + plum-on-cream is the value-anchored lower mirror. `cap` names the
    END that faces the GAP.

    R2: the shaft is now the bundle builder (matching the hero legs), and the
    lower-mirror foot is tidied (`_plum_cap`) so its single gap-cap cream disc
    stays the brightest point — no competing bright blobs."""
    half_w = int(14 * s)
    node = int(24 * s)
    cap_room = int(40 * s)
    base_room = int(38 * s)

    if cap == "bottom":
        shaft_top = top + base_room
        cut_y = bot - int(20 * s)
        culm_bundle(surf, cx, shaft_top, cut_y + int(2 * s), half_w, s, node)
        cut_cap(surf, cx, cut_y, half_w, s)
        straw_collar(surf, cx, top + int(20 * s), int(18 * s), int(14 * s), s)
        _plum_cap(surf, cx, top + int(13 * s), half_w, s)
    else:
        shaft_bot = bot - base_room
        cut_y = top + int(20 * s)
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        H = surf.get_height()
        culm_bundle(tmp, cx, H - shaft_bot, H - (cut_y + int(2 * s)), half_w, s, node)
        cut_cap(tmp, cx, H - cut_y, half_w, s)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, 0))
        straw_collar(surf, cx, bot - int(20 * s), int(18 * s), int(14 * s), s)
        _plum_cap(surf, cx, bot - int(13 * s), half_w, s)


def _plum_cap(surf, cx, cy, half_w, s):
    """The lower-mirror plum cap, value-ANCHORED: a SMALL cream-rimmed disc under
    a brightened vermilion plum so the lower mirror reads as a distinct cap at
    the pillar chip on day AND night.

    R2: shrunk + its cream pulled below CUT_HI (it uses CUT_CREAM only, no sheen)
    so the GAP-CAP disc up top stays the single brightest point of the pillar —
    the AD asked that the gap-cap cream stay the brightest. Just one plum here,
    not a competing cluster."""
    disc = pygame.Rect(cx - int(half_w * 1.0), cy - int(half_w * 0.72),
                       int(half_w * 2.0), int(half_w * 1.44))
    pygame.draw.ellipse(surf, INK, disc.inflate(int(2 * s), int(2 * s)))
    pygame.draw.ellipse(surf, CUT_D, disc)
    pygame.draw.ellipse(surf, CUT_CREAM, disc.inflate(-int(half_w * 0.4), -int(half_w * 0.3)))
    plum_blossom(surf, cx, cy, int(half_w * 0.6), s)


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
    sheet.blit(font_big.render("KADOMATSU-TORII", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "Living gate of stacked cut culms  ·  OPEN ⛩-FRAME · BOUND-BUNDLE legs (3 striped culms each) · "
        "FOUR corner CREAM discs at FOUR corners · narrow shrine-cord · round 2",
        True, LABEL_DIM), (310, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_torii(big, 180 * SS, 232 * SS, 1.55 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Body-is-bamboo — hero gate", True, LABEL), (78, 566))
    sheet.blit(font_sm.render("OPEN ⛩-frame: two BOUND-BUNDLE uprights (3 striped culms, node collars + nubs each) + heavy", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("lintel + tie-beam, framing a WIDE gold-lit doorway. FOUR cut-discs SPREAD to four corners:", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("two LEG-TOPS + two LINTEL-ENDS. Narrow vermilion shrine-cord; straw lashings + base kit anchor it.", True, LABEL_DIM), (14, 622))

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
    pygame.draw.rect(sheet, (40, 50, 40), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — one upright leg", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("bound-culm BUNDLE (3 stripes) = repeat shaft;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("slant CUT bundle-end + side pine = gap cap;", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("straw + small plum-cream = lower mirror (cap stays brightest)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_torii(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
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
    sheet.blit(font_sm.render("32px night — FOUR discrete cream", True, LABEL_DIM), (panel_x + 20, night_y + 156))
    sheet.blit(font_sm.render("dots at four corners must hold", True, LABEL_DIM), (panel_x + 20, night_y + 170))

    # blacked-out 32px silhouette — the negative-space TEST: it must read as an
    # OPEN gate-frame doorway, never a solid slab
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_torii(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
        return sil

    sil_y = night_y + 198
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 214, 200), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 24))
    sheet.blit(font_sm.render("must read as an OPEN gate-frame", True, LABEL_DIM), (sx + 104, sil_y + 42))
    sheet.blit(font_sm.render("DOORWAY (negative space) AFTER", True, LABEL_DIM), (sx + 104, sil_y + 58))
    sheet.blit(font_sm.render("the corner-disc move", True, LABEL_DIM), (sx + 104, sil_y + 74))

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

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 646))
    swatches = [
        (CULM, "fresh-culm green"), (CULM_BACK, "back-culm (bundle seam)"),
        (CUT_CREAM, "cut-ring cream"), (CUT_HI, "cut sheen (BRIGHTEST)"),
        (STRAW, "straw-rope lashing"), (PLUM, "vermilion (cord+plum)"),
        (GLOW, "gold doorway glow"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 672
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 850, W - 28, 40))
    sheet.blit(font_sm.render(
        "REALISM pipeline: SS=6 supersample -> smoothscale.  4 HARD STEPPED bands · NO gradients · ink keyline (28,22,30) · 1px grown outline.  "
        "R2 fixes: BOUND-BUNDLE legs (GATE#1) · discs spread to 4 corners + enlarged + brighter CUT_HI · steep-sogi cuts (no buttons) · narrow cord · nubs removed.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
