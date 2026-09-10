"""
Round-3 (FINAL) concept renderer for KADOMATSU-TORII — the living gate of
stacked cut culms (Kadomatsu brood, concept #2). Headless Pygame;
ELEVATED-REALISM pipeline (supersample SS=6 -> smoothscale) cloned from the
parent KADOMATSU-SHIN harness so the slant-cut hollow-ring mouths and node
geometry stay crisp at the true-32px downscale.

WHY this is the GATE direction of the brood: it is the ONLY negative-space form
in the brood or the four bamboo-v2 siblings. The read is an OPEN ⛩-frame —
two BOUND-CULM-BUNDLE uprights + a heavy horizontal LINTEL + a smaller TIE-BEAM
below it — with a WIDE OPEN DOORWAY between the legs as the silhouette.

ROUND 3 is a focused DISC-DEPLOYMENT + DOWNSCALE pass (NOT a rebuild). The
round-2 critique cleared the material, cut treatment, narrowed cord and gold
doorway — those are kept verbatim. The four-corner-disc THESIS failed at 32px:
the four discs merged into a single cream top-BAR, with zero cream at the
bottom corners, and the blackout top fused into one black blob. The fixes,
items 1+2 being the ship-gate:

  1. The four discs are now FOUR DISCRETE NODES, never a top bar. The two
     LINTEL-END discs are pulled OUTBOARD so they overhang well past the legs;
     the two LEG-TOP discs are pulled INBOARD + DOWN, opening a clear green/sky
     GAP between each pair. At true 32px you can count four cream blobs.
  2. Each leg FOOT is now capped by its own small diagonal-cut CREAM disc (a cut
     culm-base) sitting above the plum, so the read is top-discs + foot-discs =
     a true rectangle pinned at FOUR corners. The plum stays as base life but is
     value-pulled BELOW the foot cream so it never out-brights it.
  3. The lintel is THINNED and a sliver of negative space sits between the
     disc-tops and the lintel line, so the blackout reads as an OPEN frame with
     distinct corner lobes, not one fused top mass.
  4. CULM_DD (the inter-culm seam) is DEEPENED and the bundle seam WIDENED ~1px
     so the leg never collapses to a flat post at 32px.
  5. The last under-beam cream nubs are removed (no more teeth/noise).
  6. The top is de-weighted (the foot discs do most of this) so the gate is not
     top-heavy at hero.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the helpers
cloned from the parent kadomatsu_shin harness.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE — cloned from kadomatsu_shin/render_round_2.py ──────────────
# Same warm fresh-cut festive green family, same cut-CREAM focal POP, same
# auspicious New-Year accent kit. The held-apart shrine-cord red reuses the PLUM
# family so the gate stays inside the brood palette (no new hue lane).
CULM      = (124, 188, 104)   # fresh-culm green (lifted warmer/brighter)
CULM_D    = ( 74, 138,  72)   # deep node-green shade
# R3 #4: deepened a step from R2 (50,102,56) so the inter-culm bundle seam holds
# its value through the 32px downscale (a leg must never read as a flat post).
CULM_DD   = ( 40,  88,  48)   # deepest groove / node-collar / bundle-seam shadow
CULM_HI   = (172, 216, 130)   # sun-side fresh-green highlight band (warm/yellow)
CULM_HOT  = (208, 232, 158)   # hottest green sheen rail (top-left sun)
CULM_RIM  = (158, 206, 116)   # thin WARM rim-keyline on culm edges (night hold)
CULM_BACK = ( 58, 116,  62)   # back-culm body green, darkened a step (stepping)
CUT_CREAM = (224, 214, 170)   # pale diagonal-cut ring-wall (the signature POP)
# CUT_HI is the BRIGHTEST value on the entire form so the four corner discs
# out-rank the vermilion sash and survive the 32px downscale as four dots.
CUT_HI    = (252, 248, 224)   # lit cut-rim sheen — BRIGHTEST value on the form
CUT_D     = (180, 166, 120)   # cut-ring shade (cavity-side lip)
CAVITY    = (118, 128,  92)   # the hollow inner cavity (lightened — a disc, not hole)
CAVITY_DD = ( 86,  98,  70)   # cavity floor (lightened so the cream still dominates)
STRAW     = (206, 176, 104)   # woven straw-rope collar
STRAW_D   = (150, 120,  62)   # straw shade between strands
STRAW_HI  = (234, 210, 144)   # straw highlight strand
# R3 #2: foot-cream must out-bright the base plum, so the plum is pulled a step
# darker than R2 (216,80,60) — it stays auspicious base life, never a focal.
PLUM      = (196,  66,  50)   # auspicious vermilion plum + shrine-cord (accent)
PLUM_D    = (146,  42,  36)   # plum shade
PLUM_HI   = (224, 110,  92)   # plum petal highlight (pulled below foot cream)
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

    Each leg is a BUNDLE of 2-3 of these stripes side by side, so the legs read
    as bound bamboo seen side-on rather than one smooth painted dowel."""
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
    """A BOUND BUNDLE of culms seen side-on — the gate's upright leg. Three
    vertical stripes packed across the leg width: a recessed BACK stripe between
    two front stripes, value-stepped so the seam between culms reads. Returns the
    centre-x of each stripe so the caller can terminate each one in its own cut
    disc at the leg-top.

    R3 #4: the front pair is pulled slightly further apart and the back-stripe
    seam is filled with a WIDER, DEEPER CULM_DD trench (drawn here, not just the
    per-stripe deep band) so the bundle seam survives the 32px downscale instead
    of melting into a flat post."""
    sw = int(half_w * 0.44)               # per-stripe half-width
    seam = int(sw * 0.74)                 # R3: widened gap between the front pair
    left_cx  = cx - seam
    right_cx = cx + seam
    back_cx  = cx
    # R3 #4: a deep seam trench down the bundle centre, ~1px wider at 32px, so
    # the inter-culm shadow reads as a stripe seam after downscale.
    seam_hw = max(2, int(2.6 * s))
    pygame.draw.rect(surf, CULM_DD,
                     (cx - seam_hw, top + int(2 * s), seam_hw * 2, bot - top - int(2 * s)))
    # back stripe (drawn behind, darker, slightly shorter so the fronts overlap)
    culm_stripe(surf, back_cx, top + int(2 * s), bot, int(sw * 0.82), s,
                node_pitch, body_col=CULM_BACK, shade_col=CULM_DD,
                deep_col=(32, 72, 42), nub_side=1)
    # two front stripes, nodes offset by half a pitch so the bundle reads
    # hand-bound (culms never line up perfectly)
    culm_stripe(surf, left_cx, top, bot, sw, s, node_pitch, nub_side=-1)
    culm_stripe(surf, right_cx, top, bot, sw, s, int(node_pitch * 1.06),
                nub_side=1)
    return (left_cx, back_cx, right_cx, sw)


def culm_shaft_h(surf, left, right, cy, half_h, s, node_pitch, body_col=CULM,
                 shade_col=CULM_D, deep_col=CULM_DD):
    """A HORIZONTAL bound-culm beam (the lintel + the tie-beam) — the same
    stepped-band madake construction, rotated 90°. Sun lands on the TOP rail; the
    deep band is the underside so the beam reads as a turned cylinder lying on
    its side."""
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
    """The steep SOGI slant-cut culm-mouth (matching the parent `diagonal_cut`
    cavity treatment). NOT a centred glossy disc: a cut culm seen on a steep
    diagonal plane, so:

      · the cream ring-wall is an OVAL leaning along the cut (high lip one side);
      · the bright CUT_HI sheen is a hard CRESCENT on the high lip — NOT a
        concentric centred dome;
      · the inner CAVITY is OFFSET toward the LOW side (you look down into the
        hollow), with a hard-stepped dark floor — no smooth shading;
      · steps are HARD (no gradient) so it reads as a real cut, not a button.

    At 32px the downscale collapses it to one BRIGHT CREAM DOT. `lean` flips the
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
    base-anchored only. R3: pulled a step darker (palette) so it never out-brights
    the new foot-cream cut-disc above it."""
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
    """The single vermilion shrine-cord slung across the top beam — the ONLY high
    horizontal red sash in the brood, the held-apart accent. Built in the PLUM
    family (no new hue) as a woven twist: a plum band with a hard highlight
    twist-rail + paired short shide (the zigzag paper streamers) drop at the
    thirds, so it reads as a shimenawa, not a painted stripe.

    NARROWED to a true cord/sash band — its area sits UNDER the four corner cream
    discs and they out-rank it as the focal. Still base-balanced by straw + plum
    + pine at the feet so the figure stays base-anchored, never top-heavy.

    R3 #5: the shide drops are SHORTENED so no streamer hangs below the tie-beam
    line — the last under-beam cream nubs that read as teeth are gone."""
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
    # a single short shide knot-fold at the centre only — kept ABOVE the tie-beam
    # so nothing hangs below as a nub
    span = right - left
    sx = int(left + span * 0.5)
    pts = [(sx - int(2.5 * s), cy + h),
           (sx + int(2.5 * s), cy + h),
           (sx + int(2.0 * s), cy + h + int(4 * s)),
           (sx - int(2.0 * s), cy + h + int(4 * s))]
    pygame.draw.polygon(surf, INK, [(x + 1, y + 1) for (x, y) in pts])
    pygame.draw.polygon(surf, FACE, pts)


# ── a small cut culm-BASE foot disc (the FOUR-corner bottom pair) ─────────────
def foot_cut(surf, cx, cy, half_w, s, lean=1):
    """R3 #2: a SMALL diagonal-cut cream disc capping each leg FOOT — a cut
    culm-base sitting above the plum. With the two leg-top discs this puts cream
    at the bottom corners so the form reads top-discs + foot-discs = a true
    rectangle pinned at FOUR corners. Sized below the top discs (dominance low)
    and CUT_HI'd so it stays brighter than the base plum below it."""
    diagonal_cut(surf, cx, cy, half_w, s, dominance=0.42, lean=lean)


# ── THE HERO: the open ⛩-frame gate of bound cut culms ────────────────────────
def draw_torii(surf, cx, cy, s):
    """The living torii gate: two BOUND-CULM-BUNDLE uprights + a heavy horizontal
    LINTEL capping them + a smaller TIE-BEAM below the lintel, framing a WIDE OPEN
    doorway. `s` = unit scale around a ~150-unit figure.

    R3 deployment (the ship-gate) separates the four discs into FOUR DISCRETE
    NODES and pins the bottom corners:
    (1) a soft gold glow fills the OPEN doorway first so the threshold reads lit;
    (2) the two BOUND-BUNDLE uprights (each = 3 striped culms side-on, R3 wider
    seam), stopping SHORT of the lintel so each bundle's tops are free to cap;
    (3) the TWO upright LEG-TOP cut discs — pulled INBOARD + DOWN so a clear
    gap opens between them and the outboard lintel-end discs;
    (4) the THINNED lintel + tie-beam laid across the capped legs, with a sliver
    of negative space left between the disc-tops and the lintel line (blackout);
    (5) the TWO LINTEL-END cut discs pulled OUTBOARD so they OVERHANG past the
    legs → four discrete cream nodes, never one top bar;
    (6) the NARROW vermilion shrine-cord sash on the lintel (held-apart accent);
    (7) straw lashings where the lintel meets each leg (bound-culm proof);
    (8) the base kit — pine + plum at the feet — PLUS a foot-cut cream disc per
    leg so cream pins the BOTTOM corners too.

    Openness is pushed HARD: the doorway gap between the legs is wide and the
    members are relatively thin, so the blackout reads as an OPEN frame — the one
    negative-space silhouette in the brood."""
    # gate proportions — wide doorway, thin BUNDLED members (push openness)
    leg_hw   = int(11 * s)            # upright bundle half-width (thin)
    beam_hh  = int(9 * s)             # R3 #3: lintel THINNED (was 11) for blackout
    tie_hh   = int(6 * s)             # tie-beam half-height (smaller)
    span     = int(58 * s)            # half-distance between the two legs (wide)
    lx, rx   = cx - span, cx + span   # leg centre-x
    top_y    = cy - int(96 * s)       # bundle culm-top (the upper leg-top discs)
    base_y   = cy + int(74 * s)       # foot of the legs (R3 #6: raised a touch)
    # R3 #3: lintel pushed DOWN so a sliver of green/sky sits between the leg-top
    # disc crowns and the lintel line — breaks the fused top mass at blackout.
    lintel_y = top_y + int(34 * s)
    tie_y    = lintel_y + int(32 * s)
    node     = int(20 * s)

    # === (1) OPEN DOORWAY — faintly gold-lit threshold (the epic hook) ========
    door_w = (span - leg_hw) * 2
    gl = radial_glow(int(door_w * 0.62), GLOW, alpha_center=64, falloff=1.7)
    surf.blit(gl, (cx - gl.get_width() // 2,
                   (tie_y + base_y) // 2 - gl.get_height() // 2),
              special_flags=pygame.BLEND_ADD)

    # === (2) the two BOUND-CULM-BUNDLE UPRIGHTS (3 stripes each, side-on) ======
    leg_top_cut = top_y + int(10 * s)
    bundles = {}
    for legx in (lx, rx):
        bundles[legx] = culm_bundle(surf, legx, leg_top_cut, base_y, leg_hw, s, node)

    # === (3) the TWO UPRIGHT LEG-TOP cut discs (the upper-INNER corner pair) ===
    # R3 #1: pulled slightly INBOARD + DOWN so they do NOT sit on the lintel line
    # and a clear gap opens between them and the outboard lintel-end discs.
    for legx, lean in ((lx, 1), (rx, -1)):
        disc_x = legx + (-lean) * int(5 * s)      # nudge inboard (toward doorway)
        diagonal_cut(surf, disc_x, leg_top_cut + int(2 * s), leg_hw, s,
                     dominance=0.74, lean=lean)

    # === (4) the HORIZONTAL beams — lintel (THINNED) + tie-beam (smaller) ======
    # R3: the lintel overhangs the legs a long way so its ends carry the OUTBOARD
    # corner discs well clear of the leg-top discs.
    beam_l = lx - int(34 * s)
    beam_r = rx + int(34 * s)
    culm_shaft_h(surf, beam_l, beam_r, lintel_y, beam_hh, s, node)
    # the tie-beam runs only between the legs (a tighter inner crossbar)
    culm_shaft_h(surf, lx - int(2 * s), rx + int(2 * s), tie_y, tie_hh, s,
                 node, body_col=CULM_BACK, shade_col=CULM_DD)

    # === (5) the TWO LINTEL-END cut discs (the upper-OUTER corner pair) ========
    # R3 #1: pulled OUTBOARD to OVERHANG past the legs → four discrete cream nodes
    # with clear gaps, never one merged top bar.
    diagonal_cut(surf, beam_l, lintel_y, beam_hh, s, dominance=0.92, lean=1)
    diagonal_cut(surf, beam_r, lintel_y, beam_hh, s, dominance=0.92, lean=-1)

    # === (6) the held-apart NARROW VERMILION shrine-cord sash on the lintel ====
    shimenawa_cord(surf, lx - int(2 * s), rx + int(2 * s), lintel_y + int(2 * s), s)

    # === (7) STRAW LASHINGS where the lintel meets each leg ====================
    for legx in (lx, rx):
        straw_collar(surf, legx, lintel_y + int(12 * s), int(12 * s),
                     int(11 * s), s, tails=False)

    # === (8) BASE KIT — pine + plum + FOOT-CUT cream at the feet ===============
    # R3 #6: pine/plum tucked lower + tighter so the base reads as life without
    # adding top weight; the foot-cut discs are the FOUR-corner bottom pair.
    for legx, sgn in ((lx, -1), (rx, 1)):
        pine_fan(surf, (legx, base_y + int(2 * s)),
                 math.radians(90 + sgn * 36), math.radians(56), 6, 27 * s, s, sign=sgn)
        pine_fan(surf, (legx + sgn * int(6 * s), base_y + int(4 * s)),
                 math.radians(90), math.radians(62), 5, 20 * s, s)
    # plum as base LIFE only (value-pulled below the foot cream)
    plum_blossom(surf, lx - int(11 * s), base_y + int(8 * s), int(6 * s), s)
    plum_blossom(surf, rx + int(11 * s), base_y + int(8 * s), int(6 * s), s)
    plum_blossom(surf, lx + int(11 * s), base_y + int(12 * s), int(4 * s), s)
    plum_blossom(surf, rx - int(11 * s), base_y + int(12 * s), int(4 * s), s)
    # R3 #2: the FOOT cut-disc per leg — cream pinned at the BOTTOM corners,
    # drawn LAST so it stays the brightest point at each foot, above the plum.
    foot_cut(surf, lx, base_y - int(2 * s), leg_hw, s, lean=1)
    foot_cut(surf, rx, base_y - int(2 * s), leg_hw, s, lean=-1)


# ── the fresh diagonal-CUT pillar gap-cap (an explicit slant cut, not a point) ─
def cut_cap(surf, cx, cut_y, half_w, s):
    """The pillar's gap-edge cap: an explicit FRESH diagonal cut across the bundle
    top — here it IS one of the corner discs detached. Uses the SAME steep-sogi
    `diagonal_cut` treatment as the gate corners, thrown large + bright so it
    stays the brightest point of the pillar chip, with a pine tuft to one side."""
    diagonal_cut(surf, cx, cut_y, half_w, s, dominance=0.70, lean=1)
    pine_fan(surf, (cx - half_w, cut_y - int(4 * s)), math.radians(202),
             math.radians(44), 5, 24 * s, s, sign=-1)


# ── one UPRIGHT LEG → PILLAR mirror (the leg IS the pillar verbatim) ──────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """One upright leg of the gate IS the pillar: the SAME bound-culm BUNDLE (3
    striped culms side-on) tiles the shaft; the cut bundle-end (an explicit fresh
    diagonal CUT + side pine sprig) is the detachable gap-edge cap; the straw
    lashing + foot-cut-cream + plum is the value-anchored lower mirror. `cap`
    names the END that faces the GAP.

    R3: the lower-mirror foot now carries the SAME foot-cut cream disc the hero
    feet do (above a darker plum), so the pillar's bottom corner reads cream too —
    the gap-cap disc stays brightest, the foot disc is a clear step below it."""
    half_w = int(14 * s)
    node = int(24 * s)
    cap_room = int(40 * s)
    base_room = int(38 * s)

    if cap == "bottom":
        shaft_top = top + base_room
        cut_y = bot - int(20 * s)
        culm_bundle(surf, cx, shaft_top, cut_y + int(2 * s), half_w, s, node)
        cut_cap(surf, cx, cut_y, half_w, s)
        straw_collar(surf, cx, top + int(22 * s), int(18 * s), int(13 * s), s, tails=False)
        _foot_mirror(surf, cx, top + int(13 * s), half_w, s, lean=1)
    else:
        shaft_bot = bot - base_room
        cut_y = top + int(20 * s)
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        H = surf.get_height()
        culm_bundle(tmp, cx, H - shaft_bot, H - (cut_y + int(2 * s)), half_w, s, node)
        cut_cap(tmp, cx, H - cut_y, half_w, s)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, 0))
        straw_collar(surf, cx, bot - int(22 * s), int(18 * s), int(13 * s), s, tails=False)
        _foot_mirror(surf, cx, bot - int(13 * s), half_w, s, lean=1)


def _foot_mirror(surf, cx, cy, half_w, s, lean=1):
    """The lower-mirror foot, value-ANCHORED: two small base plum blossoms (base
    life) PLUS the same foot-cut cream disc the hero feet carry, drawn last so the
    foot cream pins the corner without out-brighting the gap-cap disc up top.

    R3 #2: replaces R2's bright plum-on-cream blob with the consistent foot-cut
    treatment, so the pillar and the hero read the same pinned-rectangle corner."""
    plum_blossom(surf, cx - int(half_w * 0.5), cy + int(4 * s), int(half_w * 0.42), s)
    plum_blossom(surf, cx + int(half_w * 0.5), cy + int(4 * s), int(half_w * 0.42), s)
    foot_cut(surf, cx, cy - int(2 * s), half_w, s, lean=lean)


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
        "Living gate of stacked cut culms  ·  OPEN ⛩-FRAME · BOUND-BUNDLE legs · FOUR DISCRETE cream nodes "
        "(2 leg-top INBOARD + 2 lintel-end OUTBOARD) + 2 FOOT-cut discs = rectangle pinned at 4 corners · round 3 FINAL",
        True, LABEL_DIM), (310, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_torii(big, 180 * SS, 232 * SS, 1.55 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Body-is-bamboo — hero gate", True, LABEL), (78, 566))
    sheet.blit(font_sm.render("OPEN ⛩-frame: two BOUND-BUNDLE uprights (3 striped culms, wider seam) + THINNED", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("lintel + tie-beam, framing a WIDE gold-lit doorway. FOUR DISCRETE corner discs (leg-tops", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("INBOARD, lintel-ends OUTBOARD) + TWO foot-cut discs pin the rectangle at all four corners.", True, LABEL_DIM), (14, 622))

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
    sheet.blit(font_sm.render("straw + foot-cut-cream + plum = lower mirror (cap stays brightest)", True, LABEL_DIM), (pcx - 4, 746))

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
    sheet.blit(font_sm.render("32px night — COUNT FOUR cream", True, LABEL_DIM), (panel_x + 20, night_y + 156))
    sheet.blit(font_sm.render("nodes + cream at BOTH bottom corners", True, LABEL_DIM), (panel_x + 20, night_y + 170))

    # blacked-out 32px silhouette — the negative-space TEST: it must read as an
    # OPEN gate-frame doorway with distinct corner lobes, never a solid slab
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
    sheet.blit(font_sm.render("OPEN gate-frame DOORWAY with", True, LABEL_DIM), (sx + 104, sil_y + 42))
    sheet.blit(font_sm.render("DISTINCT corner lobes (top sliver", True, LABEL_DIM), (sx + 104, sil_y + 58))
    sheet.blit(font_sm.render("of negative space breaks the mass)", True, LABEL_DIM), (sx + 104, sil_y + 74))

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
        (CULM, "fresh-culm green"), (CULM_DD, "deep bundle-seam (R3)"),
        (CUT_CREAM, "cut-ring cream"), (CUT_HI, "cut sheen (BRIGHTEST)"),
        (STRAW, "straw-rope lashing"), (PLUM, "vermilion (darkened R3)"),
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
        "R3 (FINAL): discs SEPARATED to 4 discrete nodes · FOOT-cut cream pins bottom corners · THINNED lintel + top sliver · deeper+wider seam · nubs gone.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
