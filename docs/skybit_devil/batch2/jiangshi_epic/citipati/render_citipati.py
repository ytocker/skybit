"""
Round-1 concept renderer for CITIPATI — the dancing charnel skeleton-lord
(Batch 2 / Jiangshi-epic set, concept #1). Headless Pygame; ELEVATED pipeline
(supersample SS=6 → smoothscale) so the extra geometry stays crisp at downscale.
Keeps the shipped house grammar: flat saturated fills, hard 1-2px ink keyline
(28,22,30), dark-core → flat-fill → top-left rim-sheen triad, 1px alpha-grown
outline, chibi proportions, scary-CUTE; procedural-only (no gradients/PNGs).

WHY this concept is the anti-Jiangshi: the lineage anchor is RIGID (arms-out
hopping, frozen). Citipati is the ONLY motion silhouette in the roster — a
cocked-hip dancing skeleton in a flamenco flourish, one knee kicked out. The
unmistakable top read is a FIVE-SKULL CROWN ARC + a thin lobed FLAME-HALO RING
behind the head. The cross-set red rule is honoured by VALUE/SATURATION, not
hue: warm-IVORY bone is the dominant MASS; cinnabar is a thin LINEAR accent
(crown band, sash sliver) only; ember-orange lives solely as the thin halo
RING, never a fire field. So the figure reads ivory-and-fire, leaving the one
saturated-red MASS to Xinniang.

WHY the khatvanga IS the pillar: the boss's own spine-staff (stacked vertebra
beads, a continuation of the torso's rib bands) tiles as the repeatable shaft;
a single crown-skull with a small flame-ring at the gap is the creature-derived
gap-edge cap — symmetric, on-axis, never top-heavy.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Warm-IVORY bone is the dominant mass; everything else is a thin accent.
# WHY pushed brighter than round 1: ivory must be the dominant FIELD at 32px
# (critique FIX #3) and hold value on the dark night sky — a high-key bone keeps
# the figure reading "ivory-and-fire," not "orange thing."
BONE      = (246, 236, 210)   # warm-ivory bone (the dominant fill)
BONE_D    = (190, 172, 138)   # bone dark-core
BONE_DD   = (140, 122,  94)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (255, 250, 234)   # bone top-left rim-sheen
CINNABAR  = (200,  48,  40)   # cinnabar — crown band + sash sliver ACCENT only
CINNA_D   = (146,  32,  28)
CINNA_BR  = (224,  86,  64)
# WHY hotter/lighter than round 1: the halo must read as a separate value/chroma
# band from the gold scepter (critique FIX #4) and stay a thin accent, never a
# warm clump — so the flame is pushed toward a hot yellow-orange tip.
EMBER     = (250, 138,  46)   # ember-orange — the thin HALO RING only
EMBER_BR  = (255, 214, 120)   # hot ember inner / lobe tip
EMBER_HOT = (255, 240, 178)   # hottest flame core (lightest, separates from gold)
EMBER_D   = (200,  88,  30)
GOLD      = (224, 186,  88)   # gold scepter / crown-jewel accent
GOLD_BR   = (246, 210, 118)
GOLD_D    = (170, 134,  56)
TURQ      = ( 70, 176, 168)   # turquoise sash-trim — a literal sliver
TURQ_BR   = (138, 220, 208)
INK       = ( 28,  22,  30)   # hard ink keyline
THIRD_EYE = (120,  84, 196)   # wisdom third-eye glow (cool sliver, scary-cute)

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


# ── a single ornamental crown-skull (reused for the arc + the pillar cap) ─────
def crown_skull(surf, cx, cy, r, s, lit=False):
    """Tiny ivory skull — domed cranium, two dark sockets, a stub jaw. WHY the
    sockets are SMALL and high-contrast (critique FIX #2): each crown skull must
    punch a clean IVORY shape with two dark dots at 32px, so the bone dome stays
    the dominant value and the sockets don't merge into a dark blob. `lit` swaps
    the eye-pins to hot ember for the gap-cap so it glows toward the gap."""
    # cranium dome — the dominant ivory mass that breaks the silhouette
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.6 * s)), core=False)
    # jaw stub below (kept short so the dome dominates)
    jaw = [(cx - int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.34), cy + int(r * 1.0)),
           (cx - int(r * 0.34), cy + int(r * 1.0))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.2 * s)))
    # two small sockets — just enough to read as eyes, never a mass
    eye_c = EMBER_HOT if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.04)), max(1, int(r * 0.13)))
    # nose tick
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))
    # one grin line on the jaw (teeth read as a single notch at scale)
    pygame.draw.line(surf, INK,
                     (cx - int(r * 0.34), cy + int(r * 0.70)),
                     (cx + int(r * 0.34), cy + int(r * 0.70)),
                     max(1, int(1.2 * s)))


# ── the lobed flame-halo RING (the top tell — a clean OPEN ring, no fire field) ─
def flame_halo(surf, cx, cy, rad, s, lobes=11, gap_bottom=0.50, angles=None, reach=1.0):
    """A THIN, OPEN lobed ember ring behind the head. WHY this rebuild (critique
    FIX #1/#3/#4): round 1 drew an under-glow disc + fat overlapping tongues that
    fused into a solid orange sunflower, swamping ivory and erasing the crown.
    The ring is now NEGATIVE-SPACE-first — sky shows THROUGH the gap between the
    head and the flame band, and BETWEEN the separated flame tongues. Each tongue
    is a slim isolated flame (no overlap, no backing disc), value-graded hot-light
    at the tip so it stays a thin accent that separates from the gold scepter.

    `rad` is the head radius; the flame band floats well outside it so the bone
    cranium and the crown skulls own the centre. `gap_bottom` widens the open
    bottom arc so neck/shoulders/crown stay clean."""
    # the ring floats clearly OFF the head — the visible gap is the whole point.
    # `reach` scales tongue length so tips poke OUT past the crown skull arc.
    base_r = rad * 0.86        # inner foot of each tongue, just outside the head
    tip_r  = rad * (1.06 + 0.30 * reach)   # tongue tip — pokes past the skulls
    half_w = (math.pi / lobes) * 0.42   # SLIM tongues with sky between them
    # WHY explicit angles: when the crown skulls own the outer arc the flame must
    # peek through the GAPS between them, so the caller can hand in interleaved
    # angles; otherwise fall back to an even ring across the open top arc.
    if angles is None:
        angles = [-math.pi / 2 + (i / lobes) * 2 * math.pi for i in range(lobes)]
    for ang in angles:
        # leave the whole bottom arc open (neck + crown band live there)
        if math.sin(ang) > gap_bottom:
            continue
        a0 = ang - half_w
        a1 = ang + half_w
        base0 = (cx + math.cos(a0) * base_r, cy + math.sin(a0) * base_r)
        base1 = (cx + math.cos(a1) * base_r, cy + math.sin(a1) * base_r)
        tipp  = (cx + math.cos(ang) * tip_r, cy + math.sin(ang) * tip_r)
        # a slim two-step flicker: outer half kinks for the flame-tongue read
        kink  = (cx + math.cos(ang + half_w * 0.5) * (base_r + (tip_r - base_r) * 0.55),
                 cy + math.sin(ang + half_w * 0.5) * (base_r + (tip_r - base_r) * 0.55))
        tongue = [base0, kink, tipp, base1]
        pygame.draw.polygon(surf, INK, tongue)
        pygame.draw.polygon(surf, EMBER, tongue)
        # hot inner gradient kept to the LOWER half so the tip reads light
        mid0 = (base0[0] + (tipp[0] - base0[0]) * 0.50, base0[1] + (tipp[1] - base0[1]) * 0.50)
        mid1 = (base1[0] + (tipp[0] - base1[0]) * 0.50, base1[1] + (tipp[1] - base1[1]) * 0.50)
        pygame.draw.polygon(surf, EMBER_BR, [base0, mid0, tipp, mid1])
        pygame.draw.polygon(surf, EMBER_HOT, [mid0, tipp, mid1])
        pygame.draw.polygon(surf, INK, tongue, max(1, int(1.1 * s)))


# ── the dancing skeleton-lord ─────────────────────────────────────────────────
def draw_citipati(surf, cx, cy, s):
    """Cocked-hip dancing chibi skeleton: hips shifted to one side, one knee
    kicked OUT, arms in a raised flamenco flourish (asymmetric — the ONLY motion
    silhouette). Five-skull crown arc + lobed flame-halo ring crown the head.
    `s` = unit scale around a ~120-unit figure."""

    # vertical anchors (a chibi has a big head, short torso, springy legs)
    head_c = (cx, cy - int(30 * s))
    hr = int(24 * s)
    hip_y = cy + int(22 * s)
    hip_cx = cx + int(7 * s)          # hips cocked to the figure's right

    # === FLAME-HALO RING (drawn first → behind everything) ===================
    # WHY interleaved with the crown: the five skulls (drawn last) own the outer
    # arc; the thin flame tongues are placed in the GAPS between skull positions
    # so fire peeks BETWEEN bone domes with sky showing through — a clean open
    # ring, not a field. Flame angles = the inter-skull gaps + two flank tips.
    skull_degs = [214 + i * 28 for i in range(5)]
    gap_degs = [200] + [(skull_degs[i] + skull_degs[i + 1]) / 2 for i in range(4)] + [340]
    flame_angles = [math.radians(d) for d in gap_degs]
    flame_halo(surf, head_c[0], head_c[1] - int(hr * 0.10), int(hr * 1.50), s,
               gap_bottom=0.55, angles=flame_angles, reach=1.18)

    # === LEGS — wide cocked-hip dance: one knee kicked OUT, weight on far leg =
    # standing leg (figure's left): nearly straight, planted, slight outward set
    def bone_limb(p0, p1, p2, thick, joint=True):
        """Two-segment ivory bone limb with ink keyline + bulbous joint."""
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

    # WHY thicker than round 1 (critique FIX #5): at 32px the kicked-out legs
    # collapsed into a thin tangle; fatter bone masses keep the cocked-hip stance
    # the clear bottom-silhouette tell.
    leg_th = int(14 * s)
    # standing leg — planted out to the left
    hipL = (hip_cx - int(13 * s), hip_y)
    kneeL = (hip_cx - int(20 * s), hip_y + int(26 * s))
    footL = (hip_cx - int(22 * s), hip_y + int(52 * s))
    bone_limb(hipL, kneeL, footL, leg_th)
    # kicked-out leg (figure's right) — knee thrust high & OUT, the dance read
    hipR = (hip_cx + int(11 * s), hip_y)
    kneeR = (hip_cx + int(30 * s), hip_y + int(8 * s))
    footR = (hip_cx + int(20 * s), hip_y + int(34 * s))
    bone_limb(hipR, kneeR, footR, leg_th)
    # bony foot blocks — chunkier so the stance reads at 32px
    for (fx, fy), sgn in ((footL, -1), (footR, +1)):
        foot = [(fx - int(4 * s), fy - int(2 * s)), (fx + sgn * int(16 * s), fy + int(2 * s)),
                (fx + sgn * int(15 * s), fy + int(10 * s)), (fx - int(5 * s), fy + int(8 * s))]
        triad_blob(surf, BONE, foot, ow=max(1, int(1.4 * s)))

    # === PELVIS + RIBCAGE torso (the rib bands the pillar continues) =========
    # pelvis — a wing-shaped ivory block, cocked
    pelvis = [(hip_cx - int(17 * s), hip_y - int(4 * s)),
              (hip_cx + int(17 * s), hip_y - int(6 * s)),
              (hip_cx + int(14 * s), hip_y + int(10 * s)),
              (hip_cx, hip_y + int(13 * s)),
              (hip_cx - int(15 * s), hip_y + int(9 * s))]
    triad_blob(surf, BONE, pelvis,
               core_pts=[(hip_cx - int(6 * s), hip_y + int(2 * s)),
                         (hip_cx + int(14 * s), hip_y - int(2 * s)),
                         (hip_cx + int(13 * s), hip_y + int(9 * s)),
                         (hip_cx, hip_y + int(12 * s))],
               ow=max(1, int(1.6 * s)))
    pygame.draw.circle(surf, BONE_DD, (hip_cx, hip_y + int(2 * s)), int(4 * s))  # sacral hollow

    # spine column from pelvis up to the chest (slight S for the dance)
    spine_top_y = cy - int(14 * s)
    spine = [(hip_cx, hip_y - int(2 * s)),
             (cx + int(2 * s), cy + int(6 * s)),
             (cx - int(1 * s), spine_top_y)]
    pygame.draw.lines(surf, INK, False, spine, int(8 * s))
    pygame.draw.lines(surf, BONE, False, spine, int(5 * s))

    # ribcage — an ivory barrel with hard rib bands (the motif the pillar tiles)
    rc_cx, rc_cy = cx, cy - int(2 * s)
    rc_w, rc_h = int(34 * s), int(40 * s)
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.40), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.40), rc_cy + rc_h // 2)]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.40), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(6 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(4 * s))],
               ow=max(1, int(1.8 * s)))
    # sternum hollow + hard rib bands (curved dark grooves)
    for i in range(4):
        ry = rc_cy - rc_h // 2 + int(8 * s) + i * int(8 * s)
        bw = int(rc_w * (0.46 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(7 * s), bw * 2, int(16 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.4 * s)))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(7 * s), bw * 2, int(16 * s)),
                        math.radians(0), math.radians(-25) % (2 * math.pi) + math.radians(0),
                        max(1, int(1 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(6 * s)), max(1, int(2 * s)))   # sternum

    # === ARMS — raised flamenco flourish (asymmetric = the motion read) =======
    arm_th = int(8 * s)
    shoulderL = (rc_cx - int(16 * s), rc_cy - rc_h // 2 + int(6 * s))
    shoulderR = (rc_cx + int(16 * s), rc_cy - rc_h // 2 + int(5 * s))
    # left arm sweeps UP & OUT high (flourish overhead)
    elbowL = (rc_cx - int(34 * s), rc_cy - int(20 * s))
    handL = (rc_cx - int(30 * s), rc_cy - int(44 * s))
    bone_limb(shoulderL, elbowL, handL, arm_th)
    # right arm curves DOWN & OUT low (counter-flourish)
    elbowR = (rc_cx + int(34 * s), rc_cy - int(2 * s))
    handR = (rc_cx + int(44 * s), rc_cy + int(16 * s))
    bone_limb(shoulderR, elbowR, handR, arm_th)
    # bony hands — small fans of finger ticks
    for (hx, hy), sgn, up in ((handL, -1, True), (handR, +1, False)):
        triad_circle(surf, BONE, (hx, hy), int(5 * s), ow=max(1, int(1.2 * s)), core=False)
        for k in range(-1, 3):
            ang = math.radians(-90 + k * 26) if up else math.radians(40 + k * 26)
            ex = hx + math.cos(ang) * int(9 * s)
            ey = hy + math.sin(ang) * int(9 * s)
            pygame.draw.line(surf, INK, (hx, hy), (ex, ey), max(1, int(1.6 * s)))
            pygame.draw.line(surf, BONE, (hx, hy), (ex, ey), max(1, int(1 * s)))

    # === SASH — turquoise sliver + cinnabar accent looping across the hips ====
    # WHY thin: the cross-set rule bans a second saturated mass; the sash is a
    # diagonal ribbon, not a block — cinnabar core with a turquoise trim sliver.
    sash = [(rc_cx - int(20 * s), rc_cy + int(10 * s)),
            (rc_cx + int(14 * s), rc_cy + int(2 * s)),
            (hip_cx + int(22 * s), hip_y + int(6 * s)),
            (hip_cx + int(20 * s), hip_y + int(12 * s)),
            (rc_cx + int(12 * s), rc_cy + int(9 * s)),
            (rc_cx - int(20 * s), rc_cy + int(17 * s))]
    triad_blob(surf, CINNABAR, sash,
               sheen_pts=[(rc_cx - int(19 * s), rc_cy + int(11 * s)),
                          (rc_cx + int(12 * s), rc_cy + int(4 * s)),
                          (rc_cx + int(11 * s), rc_cy + int(7 * s)),
                          (rc_cx - int(19 * s), rc_cy + int(14 * s))],
               ow=max(1, int(1.4 * s)))
    # turquoise trim sliver along the lower sash edge
    pygame.draw.line(surf, TURQ, (rc_cx - int(20 * s), rc_cy + int(16 * s)),
                     (hip_cx + int(20 * s), hip_y + int(11 * s)), max(1, int(2 * s)))
    pygame.draw.line(surf, TURQ_BR, (rc_cx - int(18 * s), rc_cy + int(15 * s)),
                     (rc_cx + int(10 * s), rc_cy + int(9 * s)), max(1, int(1 * s)))
    # sash tail flaring out (the dance flutter)
    tail = [(hip_cx + int(20 * s), hip_y + int(8 * s)),
            (hip_cx + int(40 * s), hip_y + int(20 * s)),
            (hip_cx + int(34 * s), hip_y + int(26 * s)),
            (hip_cx + int(19 * s), hip_y + int(14 * s))]
    triad_blob(surf, CINNABAR, tail, ow=max(1, int(1.2 * s)))
    pygame.draw.line(surf, TURQ, (hip_cx + int(21 * s), hip_y + int(13 * s)),
                     (hip_cx + int(36 * s), hip_y + int(24 * s)), max(1, int(1.4 * s)))

    # === SKULL HEAD — chibi, scary-cute, with a wisdom third eye =============
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    # cheek hollows
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # big round sockets — scary-CUTE with warm ember pin-lights
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] - int(hr * 0.02)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.34))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.28))
        pygame.draw.circle(surf, EMBER, (ex + sgn * int(1 * s), ey + int(1 * s)), int(hr * 0.14))
        pygame.draw.circle(surf, EMBER_HOT, (ex, ey - int(1 * s)), max(1, int(hr * 0.08)))
    # third eye of wisdom — a small cool vertical slit on the brow (the deity tell).
    # WHY a touch bigger/brighter (critique FIX #7): it must still register as the
    # one cool pin at 32px on both biomes.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.46)
    pygame.draw.ellipse(surf, INK, (tex - int(4 * s), tey - int(6 * s), int(8 * s), int(12 * s)))
    pygame.draw.ellipse(surf, THIRD_EYE, (tex - int(3 * s), tey - int(5 * s), int(6 * s), int(10 * s)))
    pygame.draw.circle(surf, (228, 210, 255), (tex, tey - int(1 * s)), max(1, int(1.6 * s)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.22)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.22)),
                         (head_c[0], head_c[1] + int(hr * 0.5))])
    # grinning tooth row (cute, not gory)
    my = head_c[1] + int(hr * 0.66)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.5), my),
                     (head_c[0] + int(hr * 0.5), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.16), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.16), my + int(hr * 0.14)), max(1, int(1 * s)))
    # fan-shaped ear ornaments (the Citipati distinguishing tell) — cinnabar sliver
    for sgn in (-1, 1):
        ear_x = head_c[0] + sgn * int(hr * 1.02)
        fan = [(ear_x - sgn * int(2 * s), head_c[1] - int(2 * s)),
               (ear_x + sgn * int(9 * s), head_c[1] - int(8 * s)),
               (ear_x + sgn * int(11 * s), head_c[1] + int(2 * s)),
               (ear_x + sgn * int(9 * s), head_c[1] + int(9 * s))]
        triad_blob(surf, CINNABAR, fan, ow=max(1, int(1.2 * s)))
        pygame.draw.line(surf, GOLD_BR, (ear_x + sgn * int(2 * s), head_c[1]),
                         (ear_x + sgn * int(9 * s), head_c[1] - int(6 * s)), max(1, int(1.2 * s)))

    # === FIVE-SKULL CROWN ARC (the top tell) — the OUTER silhouette arc =======
    # WHY skulls own the outer arc (critique FIX #2): each skull is pushed OUTSIDE
    # the flame band and enlarged so it BREAKS the outline — at 32px the five bone
    # domes punch ivory holes into the orange, so you can count skulls and the
    # crown survives the downscale. The thin cinnabar band sits behind them.
    band_r  = int(hr * 1.18)
    skull_cr = hr * 1.62          # skull centres ride OUTSIDE the flame tips
    skull_r = int(hr * 0.40)      # big enough to read as a dome at 32px
    # cinnabar crown band the skulls sit on (kept a thin linear accent)
    band_pts = []
    for i in range(13):
        a = math.radians(205 + i * (130 / 12))
        band_pts.append((head_c[0] + math.cos(a) * band_r,
                         head_c[1] + math.sin(a) * band_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(6 * s))
    pygame.draw.lines(surf, CINNABAR, False, band_pts, int(4 * s))
    pygame.draw.lines(surf, CINNA_BR, False, band_pts[:7], max(1, int(1.4 * s)))
    # five distinct ivory skulls fanned across the top arc
    for i in range(5):
        a = math.radians(214 + i * (112 / 4))
        sx = head_c[0] + math.cos(a) * skull_cr
        sy = head_c[1] + math.sin(a) * skull_cr
        crown_skull(surf, int(sx), int(sy), skull_r, s, lit=(i == 2))


# ── the khatvanga spine-staff → pillar mirror ─────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The khatvanga spine-staff IS the pillar: a stacked column of vertebra
    beads (the torso rib-band motif continued) = the tileable shaft; a single
    ivory crown-skull with a small flame-ring at the gap = the creature-derived
    gap-edge cap. On-axis, symmetric, never top-heavy — the cap is one skull the
    same scale as a body part, not a wider crown.

    `cap` names the END that faces the GAP."""
    shaft_w = int(15 * s)
    # central ink rod the beads thread onto
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    # === stacked VERTEBRA BEADS — the repeatable shaft unit ==================
    bead_pitch = int(20 * s)
    # leave room at the gap-end for the crown-skull cap
    cap_room = int(30 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
        step = bead_pitch
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
        step = bead_pitch
    y = b0
    while y <= b1:
        # each vertebra: a hexagonal ivory bead with two transverse wings + a
        # dark central foramen (the rib-band groove echo)
        bw = shaft_w
        bead = [(cx - bw, y + int(2 * s)),
                (cx - int(bw * 0.5), y - int(7 * s)),
                (cx + int(bw * 0.5), y - int(7 * s)),
                (cx + bw, y + int(2 * s)),
                (cx + int(bw * 0.5), y + int(11 * s)),
                (cx - int(bw * 0.5), y + int(11 * s))]
        triad_blob(surf, BONE, bead,
                   core_pts=[(cx, y - int(1 * s)), (cx + bw, y + int(2 * s)),
                             (cx + int(bw * 0.5), y + int(11 * s)), (cx, y + int(9 * s))],
                   sheen_pts=[(cx - bw, y + int(2 * s)), (cx - int(bw * 0.5), y - int(6 * s)),
                              (cx - int(bw * 0.2), y - int(4 * s)), (cx - int(bw * 0.7), y + int(5 * s))],
                   ow=max(1, int(1.4 * s)))
        # central foramen hollow
        pygame.draw.circle(surf, BONE_DD, (cx, y + int(2 * s)), int(4 * s))
        pygame.draw.circle(surf, INK, (cx, y + int(2 * s)), int(4 * s), max(1, int(1 * s)))
        # transverse spinous tip ticks (rib-band echo)
        pygame.draw.line(surf, BONE_DD, (cx - int(bw * 0.5), y - int(5 * s)),
                         (cx + int(bw * 0.5), y - int(5 * s)), max(1, int(1.2 * s)))
        y += step

    # === gap-edge cap: a single crown-skull + small OPEN flame-ring ==========
    # WHY bumped ~15% with the same open-ring flame (critique FIX #6): the cap was
    # faint on the night chip; a larger skull and the shared thin-ring flame keep
    # one flame language across shaft and cap and make the gap-edge cap legible.
    cap_y = (bot - int(18 * s)) if cap == "bottom" else (top + int(18 * s))
    cap_skull_r = int(14 * s)
    flame_halo(surf, cx, cap_y - int(cap_skull_r * 0.18), int(cap_skull_r * 0.96), s, lobes=9)
    crown_skull(surf, cx, cap_y, cap_skull_r, s, lit=True)
    # a small gold ferrule collar where the cap meets the shaft (scepter accent)
    collar_y = (cap_y - int(18 * s)) if cap == "bottom" else (cap_y + int(18 * s))
    pygame.draw.rect(surf, INK, (cx - int(11 * s), collar_y - int(3 * s), int(22 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(2 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_citipati(big, draw_cx * SS, draw_cy * SS, scale * SS)
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
    sheet.blit(font_big.render("CITIPATI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "dancing charnel skeleton-lord  ·  ivory-dominant · 5 skulls = outer arc · OPEN flame-ring · round 2",
        True, LABEL_DIM), (220, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 250, 1.85)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("cocked-hip DANCE: one knee kicked out, flamenco-flourish arms (the only", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("motion silhouette). 5 skulls = OUTER arc; OPEN flame-ring inside = the top tell.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("third eye + fan ears = Citipati. Ivory-and-fire; red only as crown/sash sliver.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, clean tileable shaft ================
    pcx = 470
    # top segment (cap faces DOWN toward the gap)
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    # bottom segment (cap faces UP toward the gap) — proves the top↔bottom mirror
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))   # 96px gameplay gap between
    # gap callout
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — khatvanga", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked vertebra beads = tileable shaft;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("crown-skull + flame-ring caps each gap edge", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top↔bottom, on-axis, not top-heavy)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    # render the hero at a genuine 32px tall figure
    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_citipati(big, 48 * SS, 50 * SS, (32 / 130.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    # day sky
    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    # night sky
    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, night_y + 27))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # a 32px pillar gap-cap chip beside, on both skies
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
        (BONE, "warm-ivory bone"), (BONE_D, "bone shade"),
        (CINNABAR, "cinnabar accent"), (EMBER, "ember halo"),
        (GOLD, "gold scepter"), (TURQ, "turquoise trim"),
        (THIRD_EYE, "third-eye"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    # bottom note strip
    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample → smoothscale.  STAY: flat saturated fills · hard ink keyline (28,22,30) · "
        "dark-core→fill→top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
