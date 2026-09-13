"""
Round-1 concept renderer for MALA-MATA — the skull-garland mother, a GROUNDED
SISTER of the shipped Mukha-Devi (Mukha-Devi KIN brood, concept #4, slug
mala_mata). Headless Pygame; ELEVATED pipeline (supersample SS=6 -> smoothscale)
so the radial arm-fan + the connected skull-garland stay crisp at downscale.
Keeps the shipped house grammar: flat saturated fills, hard 1-2px ink keyline
(28,22,26), dark-core -> flat-fill -> top-left rim-sheen triad, 1px alpha-grown
outline, chibi proportions, scary-CUTE; procedural-only.

WHY she is Mukha's SISTER, not a new KIND: she KEEPS the six-arm radial fan, the
warm rose/gold/teal bone palette, the chibi skull-face + rose third-eye (the
single brightest pixel). The distinctness lives ONLY in the arm-end ornament SET
and a pushed-up skull treatment — the doctrine is relaxed here by the user's
direction (sisters, not divergent silhouettes).

WHY the CONNECTED rim is her one tell: instead of six free-floating relics, every
hand holds a small GOLD ring-clasp and the clasps are JOINED hand-to-hand by a
sagging ROSE-cord garland (a mundamala) strung with tiny gold spacer-dots. A
tiara_skull hangs DOWN off each clasp as an inert bead. The three UPPER swags dip
into the open sky beside the crown so the garland FRAMES the face in a hammock of
skulls — "she wears the dead." This is the hard push-apart from her sister Kapala:
Mala's skulls hang DOWN as inert beads on a VISIBLE cord with NO internal glow;
Kapala's sit UP as glowing offering-cups. The cord is the loud element here.

WHY the skull-garland-strand IS the pillar: a banded bone shaft with a sagging
rose-cord garland of hung skull-beads draped down its length tiles as the
repeatable shaft; the cap is a clasp-knot with a glowing bell relic at the gap.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief — UNCHANGED from Mukha-Devi) ─────────────────
BONE      = (224, 200, 196)   # dusty rose-bone (the dominant fill)
BONE_D    = (168, 134, 138)   # mauve-bone dark-core / shade
BONE_DD   = (120,  90,  98)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (248, 236, 234)   # bone top-left rim-sheen
ROSE      = (232,  86, 150)   # magenta-rose GLOW / cord (the single warm focal)
ROSE_BR   = (255, 160, 200)   # hot inner / sheen
ROSE_D    = (160,  40,  86)   # deep-rose shade
GOLD      = (224, 182,  84)   # gold ring-clasps + spacer-dots
GOLD_BR   = (246, 214, 130)
GOLD_D    = (170, 134,  56)
TEAL      = ( 64, 170, 166)   # teal bell-sliver — a literal sliver
TEAL_BR   = (140, 222, 216)
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = (232,  86, 150)   # third-eye glow (rose so it reads as her power-focus)
THIRD_BR  = (255, 196, 224)

BG        = ( 96,  92, 100)   # neutral grey review backdrop
PANEL     = ( 74,  72,  84)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 236, 240)
LABEL_DIM = (196, 190, 202)


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


# ── a single ornamental tiara-skull (reused for tiara + garland beads) ────────
def tiara_skull(surf, cx, cy, r, s, lit=False):
    """Tiny rose-bone skull. WHY a domed cranium with two dark dots: it must
    punch a clean bone shape with two sockets at 32px. Reused for the LOW 3-skull
    tiara AND for the hung garland beads. WHY the garland skulls pass lit=False
    always: Mala's beads are INERT (no internal glow) — that is the hard tell vs
    sister Kapala's glowing cups."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False)
    # a thin BONE_SH rim-arc on the cranium top-left — a VALUE lift (not a glow)
    # so the inert bead still separates from a dark night sky at 32px.
    pygame.draw.arc(surf, BONE_SH,
                    (cx - r, cy - r, r * 2, r * 2),
                    math.radians(110), math.radians(210), max(1, int(1.4 * s)))
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.94)),
           (cx - int(r * 0.32), cy + int(r * 0.94))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.1 * s)))
    eye_c = ROSE_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.14)))


# ── the six-arm radial starburst (the KIND tell — UNCHANGED from Mukha) ───────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr, relic_r):
    """Six fat bone arms splay in a wide symmetric STARBURST around the torso.
    UNCHANGED from Mukha-Devi: ±100/64/28° off vertical, two-segment limbs from a
    LOW shoulder origin, drawn lowest-first so the upper splay overlaps cleanly.
    Returns the six hand centres for clasp + garland placement, sorted so a left-
    to-right neighbour chain can be strung between them."""
    shoulder = (sh_cx, sh_cy)
    arm_len = int(hr * 1.95)
    arm_th = int(12 * s)
    spread = [100, 64, 28]   # degrees off the vertical for the 3 arms per side
    order = []
    for sgn in (-1, 1):
        for d in spread:
            a = math.radians(-90 + sgn * d)
            order.append((sgn, d, a))
    order.sort(key=lambda o: -o[1])
    hands = []
    for sgn, d, a in order:
        sh = (shoulder[0] + sgn * int(hr * 0.55), shoulder[1])
        elbow = (sh[0] + math.cos(a) * arm_len * 0.52,
                 sh[1] + math.sin(a) * arm_len * 0.52)
        hand = (sh[0] + math.cos(a) * arm_len,
                sh[1] + math.sin(a) * arm_len)
        for (p, q) in ((sh, elbow), (elbow, hand)):
            dx, dy = q[0] - p[0], q[1] - p[1]
            L = max(1.0, math.hypot(dx, dy))
            nx, ny = -dy / L * arm_th / 2, dx / L * arm_th / 2
            quad = [(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                    (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)]
            triad_blob(surf, BONE, quad,
                       sheen_pts=[(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                                  (q[0] + nx * 0.3, q[1] + ny * 0.3),
                                  (p[0] + nx * 0.3, p[1] + ny * 0.3)],
                       ow=max(1, int(arm_th * 0.16)))
        triad_circle(surf, BONE, (int(elbow[0]), int(elbow[1])), int(arm_th * 0.55),
                     ow=max(1, int(1.2 * s)), core=False)
        hands.append((sgn, d, hand))
    # order the hands into a LEFT->RIGHT neighbour chain so the garland can be
    # strung swag-by-swag: left side top->down, then right side down->top, so the
    # three UPPER swags sit at the two ends (beside the crown) and dip into sky.
    left = sorted([h for h in hands if h[0] < 0], key=lambda h: -h[1])   # top->low
    right = sorted([h for h in hands if h[0] > 0], key=lambda h: h[1])   # low->top
    chain = left + right
    return [(int(h[2][0]), int(h[2][1])) for h in chain]


# ── the CONNECTED skull-garland (mundamala) — Mala's distinguishing rim ───────
def _sag_point(p0, p1, t, sag):
    """A point along a catenary-ish swag between two hands. WHY a quadratic dip
    rather than a straight chord: a hung cord SAGS, and the sag is what reads as
    'a garland' rather than 'spokes'. `sag` is the extra droop at the swag's
    midpoint, in surface units."""
    x = p0[0] + (p1[0] - p0[0]) * t
    y = p0[1] + (p1[1] - p0[1]) * t
    y += sag * 4.0 * t * (1.0 - t)   # 0 at the ends, max at t=0.5
    return (x, y)


def draw_garland(surf, hands, head_c, hr, relic_r, s):
    """String a CONNECTED rose-cord garland between the six hands, hang ONE inert
    skull-bead off each hand's gold ring-clasp (six beads total), and ROUTE the
    two crown-flanking swags OUTWARD so they drape BESIDE the crown and leave an
    open triangular sky-wedge above the tiara — skulls FRAME, never roof, the face.

    WHY the BEADS carry the silhouette, not the cord: at 32px a fat rose cord
    mushes into the beads. So the cord is drawn THIN (1-2px) and DARK (toward
    ROSE_D, capped well below the brow third-eye), while the six skull-beads are
    fattened and value-lifted so the read is 'a sag of skull-DOTS'. NEVER an
    internal bead glow — that is sister Kapala's identity; night is solved by
    value + a bone keyline only.

    WHY the cord is routed up-and-out past the two top hands rather than chorded
    straight across the crown: a straight chord between the highest left + right
    hands would cut OVER the tiara and close the wedge (the r1 failure). Instead
    the top swag is split — each top hand's cord rises OUTWARD to an off-screen-ish
    anchor up and to the side, so the garland opens like a curtain pulled aside."""
    n = len(hands)
    bead_r = int(relic_r * 1.30)            # FATTER bead so it carries the read
    clasp_r = max(1, int(relic_r * 0.40))   # the gold ring at each hand

    # the two crown-flanking hands are the chain ends (left[0] = top-left,
    # right[-1] = top-right) thanks to the L->R neighbour ordering in the fan.
    top_l, top_r = hands[0], hands[-1]

    def draw_cord(pts, deep=False):
        """A THIN, dark rose cord. WHY ink under a 1px rose: the beads must win
        the silhouette — the cord is a hint of connection, not a rose ribbon. On
        a deep swag (the crown-flanking ones) push toward ROSE_D so it recedes."""
        col = ROSE_D if deep else lerp(ROSE, ROSE_D, 0.45)
        pygame.draw.lines(surf, INK, False, pts, max(2, int(2.6 * s)))
        pygame.draw.lines(surf, col, False, pts, max(1, int(1.4 * s)))

    # --- the inter-hand swags, but SKIP the chord across the crown gap ----------
    for i in range(n - 1):
        p0, p1 = hands[i], hands[i + 1]
        # the single widest gap in the chain straddles the crown (left-end ->
        # right-end wrap is not drawn; this is the under-face swag set). Give the
        # under-arm swags a gentle, even sag so they read as one taut mundamala.
        sag = relic_r * 1.9
        cord = [_sag_point(p0, p1, t / 14.0, sag) for t in range(15)]
        draw_cord(cord)
        # ONE small gold spacer-dot at the swag midpoint — capped a clear notch
        # below the brow: tiny, GOLD (not rose), no bright-white pip.
        sp = _sag_point(p0, p1, 0.5, sag)
        pygame.draw.circle(surf, GOLD_D, (int(sp[0]), int(sp[1])), max(1, int(1.6 * s)))
        pygame.draw.circle(surf, GOLD, (int(sp[0]), int(sp[1])), max(1, int(1.0 * s)))

    # --- the crown-flanking curtains: route each top hand's cord UP and OUT ------
    # WHY anchors above + outside the head: the cord rises beside the crown to a
    # high outboard point, opening a clean V of sky over the tiara at 32px.
    for hand, sgn in ((top_l, -1), (top_r, +1)):
        anchor = (head_c[0] + sgn * int(hr * 2.05), head_c[1] - int(hr * 1.15))
        # a shallow OUTWARD bow so the curtain bulges away from the face.
        bow = relic_r * -2.4
        cord = [_sag_point(hand, anchor, t / 12.0, bow) for t in range(13)]
        draw_cord(cord, deep=True)
        # a single gold spacer near the hand end to echo the mundamala beadwork.
        sp = _sag_point(hand, anchor, 0.35, bow)
        pygame.draw.circle(surf, GOLD_D, (int(sp[0]), int(sp[1])), max(1, int(1.6 * s)))
        pygame.draw.circle(surf, GOLD, (int(sp[0]), int(sp[1])), max(1, int(1.0 * s)))
        # a small gold knot CAPS the curtain end so the up-and-out cord reads as a
        # garland tie-back, not a loose wire — and stays a clear notch below the brow.
        ax, ay = int(anchor[0]), int(anchor[1])
        triad_circle(surf, GOLD, (ax, ay), max(1, int(2.2 * s)),
                     ow=max(1, int(1.0 * s)), core=False, sheen=False)
        pygame.draw.circle(surf, INK, (ax, ay), max(1, int(1.0 * s)))

    # --- at each hand: gold ring-clasp, short drop-link, ONE hung skull-bead ----
    for (hx, hy) in hands:
        drop = int(bead_r * 1.40)
        bx, by = hx, hy + drop
        # the drop-link — thin + dark so the BEAD, not the link, reads.
        pygame.draw.line(surf, INK, (hx, hy), (bx, by - bead_r), max(2, int(2.6 * s)))
        pygame.draw.line(surf, lerp(ROSE, ROSE_D, 0.45), (hx, hy), (bx, by - bead_r),
                         max(1, int(1.3 * s)))
        # the gold ring-clasp at the hand (no bright pip — capped below the brow)
        triad_circle(surf, GOLD, (hx, hy), clasp_r, ow=max(1, int(1.2 * s)),
                     core=False, sheen=False)
        pygame.draw.circle(surf, INK, (hx, hy), max(1, int(clasp_r * 0.45)))
        # the hung skull — INERT (lit=False): no internal glow, the hard tell.
        tiara_skull(surf, bx, by, bead_r, s, lit=False)


# ── the wrathful skull-garland mother ─────────────────────────────────────────
def draw_mala_mata(surf, cx, cy, s):
    """Pint-sized many-armed death-goddess wearing a hammock of skulls: a tiny
    chibi torso under a wide six-arm radial starburst, the six hands JOINED by a
    sagging rose-cord garland of inert skull-beads. A LOW 3-skull tiara + a
    glowing rose third eye keep the FACE reading inside the fan + garland.
    Body, fan, face, third-eye, palette are UNCHANGED from Mukha-Devi; only the
    arm-end ornament (relics -> connected garland) and skull count differ.
    `s` = unit scale around a ~130-unit figure."""

    head_c = (cx, cy - int(28 * s))
    hr = int(32 * s)
    relic_r = int(10 * s)

    # === SIX-ARM RADIAL FAN (drawn first -> arms sit BEHIND torso & head) ======
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.82), s, hr, relic_r)

    # === LOWER BODY — a wide squat lotus-base (UNCHANGED) =====================
    base_y = cy + int(42 * s)
    base = [(cx - int(34 * s), base_y - int(7 * s)),
            (cx - int(24 * s), base_y - int(15 * s)),
            (cx + int(24 * s), base_y - int(15 * s)),
            (cx + int(34 * s), base_y - int(7 * s)),
            (cx + int(27 * s), base_y + int(11 * s)),
            (cx - int(27 * s), base_y + int(11 * s))]
    triad_blob(surf, BONE, base,
               core_pts=[(cx, base_y - int(14 * s)), (cx + int(28 * s), base_y - int(7 * s)),
                         (cx + int(22 * s), base_y + int(9 * s)), (cx, base_y + int(7 * s))],
               ow=max(1, int(1.6 * s)))
    for k in range(-2, 3):
        px = cx + int(k * 11 * s)
        pygame.draw.line(surf, BONE_DD, (px, base_y - int(15 * s)),
                         (px, base_y + int(8 * s)), max(1, int(1.4 * s)))
    # base lotus pip nudged toward BONE_D so no rose mass below competes with the
    # brow third-eye for the DAY-chip focal — the eye must win the gaze.
    pygame.draw.circle(surf, lerp(ROSE_D, BONE_D, 0.45), (cx, base_y - int(3 * s)), int(5 * s))
    pygame.draw.circle(surf, lerp(ROSE_D, BONE_D, 0.25),
                       (cx - int(1 * s), base_y - int(4 * s)), max(1, int(2 * s)))

    # === TORSO — a SHORT rib barrel (UNCHANGED) ===============================
    rc_cx, rc_cy = cx, cy + int(12 * s)
    rc_w, rc_h = int(32 * s), int(24 * s)
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
                          (rc_cx - int(6 * s), rc_cy + int(4 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(2 * s))],
               ow=max(1, int(1.8 * s)))
    for i in range(2):
        ry = rc_cy - rc_h // 2 + int(7 * s) + i * int(8 * s)
        bw = int(rc_w * (0.42 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(6 * s), bw * 2, int(14 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.2 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(5 * s)),
                     (rc_cx, rc_cy + int(3 * s)), max(1, int(2 * s)))
    # chest sash — dropped a notch toward BONE_D (a dusty mauve-rose, not a hot
    # rose) so it stops being the loudest rose mass on the DAY chip; the brow
    # third-eye is then the only saturated rose and wins the focal.
    pygame.draw.line(surf, lerp(ROSE_D, BONE_D, 0.4),
                     (rc_cx - int(rc_w * 0.42), rc_cy + int(2 * s)),
                     (rc_cx + int(rc_w * 0.42), rc_cy - int(2 * s)), max(1, int(2 * s)))

    # === CONNECTED SKULL-GARLAND — the arm-end ornament (Mala's tell) =========
    # WHY drawn after torso, before head: the hung beads + cord ride out at the
    # fan tips and curtain down beside the head; the head still overdraws nothing
    # of them, and the open wedge above the crown stays clear for the tiara.
    draw_garland(surf, hands, head_c, hr, relic_r, s)

    # === SKULL HEAD — chibi, scary-cute, three-eyed (UNCHANGED) ===============
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.25))
        pygame.draw.circle(surf, ROSE_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.12))
    # THIRD EYE — the single BRIGHTEST pixel (AD hard rule). Lifted ~1px higher on
    # the brow (0.34 -> 0.42) so a clear vertical gap opens between it and the eye-
    # socket row; at 32px the face stops reading as a flat 3-pink-dot row.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.42)
    pygame.draw.ellipse(surf, INK, (tex - int(7 * s), tey - int(9 * s), int(14 * s), int(18 * s)))
    pygame.draw.ellipse(surf, ROSE, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, ROSE_BR, (tex - int(4 * s), tey - int(5 * s), int(8 * s), int(10 * s)))
    pygame.draw.circle(surf, THIRD_BR, (tex - int(1 * s), tey - int(2 * s)), max(2, int(3.2 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(2 * s)),
                       max(1, int(1.6 * s)))
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.48), my),
                     (head_c[0] + int(hr * 0.48), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.15), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.15), my + int(hr * 0.13)), max(1, int(1 * s)))
    for sgn in (-1, 1):
        fx = head_c[0] + sgn * int(hr * 0.40)
        pygame.draw.polygon(surf, BONE_SH,
                            [(fx - int(2 * s), my), (fx + int(2 * s), my),
                             (fx, my + int(hr * 0.22))])

    # === LOW 3-SKULL TIARA (splayed to PUNCH a sky-wedge over the crown) =======
    # WHY a wider band arc + outward/down outer skulls + a dropped centre apex:
    # at 32px the three skulls + cord arcs had closed the top into a solid dome
    # (no sky bit into the silhouette). Splaying the two OUTER skulls down-and-out
    # and lowering the CENTRE skull's apex ~2px opens a clean triangular notch of
    # sky between them, so the crown FRAMES beside the face rather than roofing it.
    tiara_r = int(hr * 0.96)
    tiara_skull_r = int(hr * 0.30)
    # WHY the band is drawn as TWO arcs with an apex GAP (not one arc over the
    # crown): a continuous gold band over 270deg roofed the silhouette — on the
    # blackout no sky bit in. Splitting it (left 240->262, right 278->300) leaves
    # an open notch of sky at the apex; the centre skull then rides BELOW that
    # gap on a short radius so it frames beside, never over.
    def _band_arc(d0, d1, sheen):
        pts = []
        steps = 6
        for i in range(steps + 1):
            a = math.radians(d0 + (d1 - d0) * i / steps)
            pts.append((head_c[0] + math.cos(a) * tiara_r,
                        head_c[1] + math.sin(a) * tiara_r))
        pygame.draw.lines(surf, INK, False, pts, int(6 * s))
        pygame.draw.lines(surf, GOLD, False, pts, int(3 * s))
        if sheen:
            pygame.draw.lines(surf, GOLD_BR, False, pts, max(1, int(1.2 * s)))
    _band_arc(240, 262, sheen=True)
    _band_arc(278, 300, sheen=False)
    # the centre skull rides a shorter radius (apex dropped, sits under the gap);
    # the two outer skulls sit at wider angles AND push out past the band ends so
    # a clean V of sky opens between centre and each outer skull.
    tiara_place = [(230, tiara_r * 1.08), (270, tiara_r * 0.82), (310, tiara_r * 1.08)]
    for i, (deg, rr) in enumerate(tiara_place):
        a = math.radians(deg)
        sx = head_c[0] + math.cos(a) * rr
        sy = head_c[1] + math.sin(a) * rr
        tiara_skull(surf, int(sx), int(sy), tiara_skull_r, s, lit=(i == 1))


# ── the skull-garland-strand → pillar mirror ──────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The skull-garland-strand IS the pillar: a banded bone shaft draped with a
    sagging rose-cord garland of hung skull-beads (with gold spacer-dots) = the
    tileable shaft; the cap is a clasp-knot with a glowing bell relic at the gap
    — the creature's own mundamala language, symmetric and on-axis.

    `cap` names the END that faces the GAP."""
    shaft_w = int(13 * s)
    bead_r = int(7 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    band_pitch = int(24 * s)
    cap_room = int(34 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    idx = 0
    prev_clasp = None
    while y <= b1:
        bw = shaft_w
        band = [(cx - bw, y - int(8 * s)),
                (cx + bw, y - int(8 * s)),
                (cx + bw, y + int(8 * s)),
                (cx - bw, y + int(8 * s))]
        triad_blob(surf, BONE, band,
                   core_pts=[(cx, y - int(7 * s)), (cx + bw, y - int(7 * s)),
                             (cx + bw, y + int(7 * s)), (cx, y + int(7 * s))],
                   sheen_pts=[(cx - bw, y - int(7 * s)), (cx - int(bw * 0.3), y - int(7 * s)),
                              (cx - int(bw * 0.3), y + int(2 * s)), (cx - bw, y + int(2 * s))],
                   ow=max(1, int(1.4 * s)))
        pygame.draw.line(surf, BONE_DD, (cx - bw, y), (cx + bw, y), max(1, int(1.6 * s)))
        # a gold ring-clasp on an alternating side, a hung skull-bead under it,
        # and a sagging rose cord joining this clasp to the previous one — the
        # connected garland draped down the shaft.
        side = -1 if (idx % 2 == 0) else 1
        clx = cx + side * (bw + int(7 * s))
        cly = y
        if prev_clasp is not None:
            sag = int(10 * s)
            cord = [_sag_point(prev_clasp, (clx, cly), t / 10.0, sag) for t in range(11)]
            pygame.draw.lines(surf, INK, False, cord, max(2, int(3.0 * s)))
            pygame.draw.lines(surf, ROSE, False, cord, max(1, int(2.0 * s)))
            mid = _sag_point(prev_clasp, (clx, cly), 0.5, sag)
            pygame.draw.circle(surf, GOLD, (int(mid[0]), int(mid[1])), max(1, int(1.4 * s)))
        triad_circle(surf, GOLD, (clx, cly), max(1, int(3 * s)), ow=max(1, int(1 * s)),
                     core=False, sheen=False)
        pygame.draw.circle(surf, INK, (clx, cly), max(1, int(1.4 * s)))
        # the inert hung skull-bead (no glow)
        tiara_skull(surf, clx, cly + int(bead_r * 1.5), bead_r, s, lit=False)
        prev_clasp = (clx, cly)
        idx += 1
        y += band_pitch

    # === gap-edge cap: clasp-knot + glowing bell ==============================
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    grow = +1 if cap == "bottom" else -1
    # a fanned clasp-knot of short bone struts (echoes the six-arm fan in mini)
    burst_r = int(15 * s)
    for k in range(5):
        a = math.radians(-90 + (k - 2) * 30) if grow > 0 else math.radians(90 + (k - 2) * 30)
        tip = (cx + math.cos(a) * burst_r, cap_y + math.sin(a) * burst_r)
        pygame.draw.line(surf, INK, (cx, cap_y), tip, max(2, int(4 * s)))
        pygame.draw.line(surf, BONE, (cx, cap_y), tip, max(1, int(2.4 * s)))
        triad_circle(surf, BONE, (int(tip[0]), int(tip[1])), max(1, int(2.4 * s)),
                     ow=max(1, int(1 * s)), core=False, sheen=False)
    collar_y = cap_y - grow * int(burst_r + int(4 * s))
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))
    triad_circle(surf, BONE, (cx, cap_y), int(7 * s), ow=max(1, int(1.4 * s)), core=False)
    pygame.draw.arc(surf, TEAL, (cx - int(6 * s), cap_y - int(6 * s), int(12 * s), int(12 * s)),
                    math.radians(200), math.radians(340), max(2, int(2.4 * s)))
    pygame.draw.circle(surf, ROSE, (cx, cap_y), int(3 * s))
    pygame.draw.circle(surf, ROSE_BR, (cx - int(1 * s), cap_y - int(1 * s)), max(1, int(1.6 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_mala_mata(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def _load_font(size, bold=True):
    """FONT path FIVE levels up from this script (repo game/assets), SysFont
    fallback so the sheet renders on any host."""
    here = os.path.dirname(os.path.abspath(__file__))
    root = here
    for _ in range(5):
        root = os.path.dirname(root)
    path = os.path.join(root, "game", "assets", "LiberationSans-Bold.ttf")
    if os.path.exists(path):
        return pygame.font.Font(path, size)
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)


def main():
    W, H = 1010, 820
    font_big = _load_font(30)
    font = _load_font(17)
    font_sm = _load_font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("MALA-MATA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "skull-garland mother  ·  Mukha-Devi SISTER · MID tight-loose · CONNECTED rim · 6 garland + 3 tiara skulls · round 3",
        True, LABEL_DIM), (250, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 232, 1.55)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("Six hands JOINED by a thin dark rose cord; ONE fat inert skull-bead hangs off each.", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("Crown-flanking cords route UP-and-OUT — an open V of sky sits above the tiara.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("6 beads carry the sag; cord is a hint. Brow third-eye is the single brightest pixel.", True, LABEL_DIM), (14, 622))

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
    pygame.draw.rect(sheet, (60, 58, 70), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — skull-garland strand", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("banded bone shaft draped with a sagging rose-", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("cord garland of hung skull-beads = shaft;", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("clasp-knot + glowing bell caps the gap (mirrored)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_mala_mata(big, 55 * SS, 58 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (110, 110))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 20, day_y + 20))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 20, night_y + 20))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blackout silhouette proof — the connected garland sag must still read.
    def chip_black():
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_mala_mata(big, 55 * SS, 58 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (110, 110))
        mask = pygame.mask.from_surface(small)
        out = pygame.Surface((110, 110), pygame.SRCALPHA)
        for (ox, oy) in mask.outline():
            pass
        # fill the whole mask flat-black to prove the silhouette
        sil = mask.to_surface(setcolor=(20, 16, 22, 255), unsetcolor=(0, 0, 0, 0))
        out.blit(sil, (0, 0))
        return out

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
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

    # blackout silhouette proof tile
    bx = px2 + 70
    pygame.draw.rect(sheet, (210, 210, 214), (bx, day_y, 70, 70))
    pygame.draw.rect(sheet, INK, (bx, day_y, 70, 70), 1)
    sheet.blit(pygame.transform.smoothscale(chip_black(), (70, 70)), (bx, day_y))
    sheet.blit(font_sm.render("blackout", True, LABEL_DIM), (bx + 2, day_y - 16))

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (BONE, "dusty rose-bone"), (BONE_D, "mauve-bone shade"),
        (ROSE, "rose cord/glow"), (ROSE_D, "deep-rose"),
        (GOLD, "gold clasp/spacer"), (TEAL, "teal bell-sliver"),
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

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  SISTER tell = CONNECTED rim: skulls hang DOWN as "
        "INERT beads on a visible rose cord (NO glow) vs Kapala's up-facing glowing cups.  procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
