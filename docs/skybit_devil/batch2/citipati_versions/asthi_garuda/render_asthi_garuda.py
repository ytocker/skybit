"""
Round-1 concept renderer for ASTHI-GARUDA — the bone-winged charnel sky-eater
(Citipati-versions set, concept #4). Headless Pygame; ELEVATED pipeline
(supersample SS=6 → smoothscale) so the tiered quill geometry stays crisp at
downscale. Keeps the shipped house grammar: flat fills, hard 1-2px ink keyline,
dark-core → flat-fill → top-left rim-sheen triad, 1px alpha-grown outline,
chibi proportions, scary-CUTE; procedural-only (no gradients/PNGs).

WHY this is the SPREAD-WING / BEAKED-SKULL of the brood: the roster is
skeleton-dense, so Asthi-Garuda is deliberately the ONLY aerial X-silhouette
and the ONLY beaked skull. The top read is a hard X — a beaked bone-skull
centred over two tiered fans of RIGID quill-BLADES (bone splines, never Pazul's
faceted membranes). The cross-set bone-cast rule is honoured by VALUE/HUE: the
bone carries a LAVENDER cast pushed up so the blood-orange beak pops, but it
stays DESATURATED so it never reads as Necrarch's saturated robe-violet — the
violet lives in the bone, never as a glow. Blood-orange is the SOLE glow, in the
beak gape + eye sockets only.

WHY the perch-totem IS the pillar: a banded bone perch-pole wound with quill
rings (a continuation of the wing-quill motif) tiles as the repeatable shaft; a
single wing-skull cap — wings half-FOLDED into a hard scalloped fan, beak/eye
glowing, talons gripping toward the gap line — is the creature-derived gap-edge
cap. Bottom-weighted (talons + beak hang toward the gap), on-axis, symmetric.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the triad/outline
helpers cloned from the lineage template.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Dusk-violet-grey bone is the dominant mass; lavender cast pushed UP so the
# blood-orange beak pops, but kept DESATURATED so it never tips into Necrarch's
# saturated robe-violet. The violet lives in the BONE, never in a glow.
BONE      = (186, 176, 196)   # dusk-violet-grey bone (the dominant fill)
BONE_D    = (118, 108, 134)   # deep-slate-violet bone shade / dark-core
BONE_DD   = ( 78,  70,  96)   # deepest bone hollow (sockets, quill gaps)
BONE_SH   = (232, 228, 238)   # pale-quill rim-sheen / highlight
QUILL_HI  = (232, 228, 238)   # pale-quill highlight (named for clarity at use)
SHEEN     = (244, 240, 248)   # hottest bone sheen
GLOW      = (238, 114,  52)   # blood-orange beak + eye glow (the SOLE glow)
GLOW_BR   = (255, 176,  96)   # hot inner glow
GLOW_HOT  = (255, 224, 168)   # hottest glow core
RUST      = (170,  66,  34)   # rust shade under the glow
INK       = ( 26,  24,  30)   # hard ink keyline

BG        = ( 92,  88, 100)   # neutral grey-violet review backdrop
PANEL     = ( 72,  68,  82)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (190, 196, 208)


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


# ── a single FAT RIGID bone-BLADE (the hard tell — a plank, never a thread) ───
def bone_blade(surf, root, ang, length, width, s, tip_blunt=0.34):
    """One FAT rigid bone-blade: a wide, near-parallel-sided plank rooted at
    `root`, swept along `ang`, ending in a stubby CHISEL tip (never a hair). WHY
    a fat plank and not a needle-quill: round-1 collapsed into a dandelion-puff
    at 32px — the AD ruling is fat rigid BLADES so the winged tell survives at
    gameplay scale. Each blade is triad-lit as its OWN form (dark-core spine →
    flat fill → top-left sheen) so it reads as a plank of bone, and is its own
    closed polygon so sky reads cleanly BETWEEN blades — the X stays an X."""
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca                     # perpendicular = blade width axis
    hw = width * 0.5
    # the chisel tip is a blunt flat edge (a stubby chisel), not a point
    tip_c = (root[0] + ca * length, root[1] + sa * length)
    tw = hw * tip_blunt                  # half-width at the chisel tip
    # belly sits most of the way out so the plank stays wide nearly to the tip
    belly = 0.72 * length
    bx = (root[0] + ca * belly, root[1] + sa * belly)
    # 6-point near-parallel plank: root edge → full-width belly → chisel tip edge
    blade = [
        (root[0] + px * hw * 0.86, root[1] + py * hw * 0.86),
        (bx[0]   + px * hw,        bx[1]   + py * hw),
        (tip_c[0] + px * tw,       tip_c[1] + py * tw),
        (tip_c[0] - px * tw,       tip_c[1] - py * tw),
        (bx[0]   - px * hw,        bx[1]   - py * hw),
        (root[0] - px * hw * 0.86, root[1] - py * hw * 0.86),
    ]
    pygame.draw.polygon(surf, INK, blade)
    pygame.draw.polygon(surf, BONE, blade)
    # dark-core spine down the trailing (body-side) half → the plank gets volume
    core = [
        (root[0] - px * hw * 0.62, root[1] - py * hw * 0.62),
        (bx[0]   - px * hw * 0.86, bx[1]   - py * hw * 0.86),
        (tip_c[0] - px * tw,       tip_c[1] - py * tw),
        (tip_c[0] + px * tw * 0.2, tip_c[1] + py * tw * 0.2),
        (bx[0]   - px * hw * 0.10, bx[1]   - py * hw * 0.10),
    ]
    pygame.draw.polygon(surf, BONE_D, core)
    # top-left leading-edge sheen — a fat pale rail, not a thread (rigid bone read)
    lead = [
        (root[0] + px * hw * 0.70, root[1] + py * hw * 0.70),
        (bx[0]   + px * hw * 0.92, bx[1]   + py * hw * 0.92),
        (tip_c[0] + px * tw * 0.8, tip_c[1] + py * tw * 0.8),
        (tip_c[0] + px * tw * 0.1, tip_c[1] + py * tw * 0.1),
        (bx[0]   + px * hw * 0.30, bx[1]   + py * hw * 0.30),
    ]
    pygame.draw.polygon(surf, QUILL_HI, lead)
    # central shaft groove — the hard quill rib, a confident line
    pygame.draw.line(surf, BONE_DD, (bx[0], bx[1]), tip_c, max(2, int(width * 0.18)))
    pygame.draw.polygon(surf, INK, blade, max(2, int(width * 0.16)))


def blade_wing(surf, root, base_ang, s, sign):
    """ONE bird wing per side as a TIERED quill-BLADE fan — NOT a 4-spoke cross.
    WHY a tiered bird-fan: round-2 read as a four-winged INSECT because the two
    upper and two lower fans were near-equal and symmetric. A bird has ONE wing
    per side: long PRIMARIES rising up-and-out at the leading edge, and a rank
    of SHORTER coverts/secondaries folding DOWN-and-under BEHIND them as the
    trailing edge — graded longest→shortest from leading to trailing. `sign`
    (+1 right / -1 left) sweeps the whole fan outward from the shoulder; the
    fan opens DOWNWARD off the leading primary so the wing droops like a real
    spread raptor wing (a fat V-arm), never a radial spoke-cross.

    `base_ang` points along the LONGEST leading primary (up-and-out). Successive
    blades rotate DOWNWARD (toward the body's lower-outer quadrant) and shorten,
    so the silhouette is one solid wing-fan: long top edge, short tucked bottom."""
    L = 60.0 * s
    bw = 13.0 * s
    # leading primaries → trailing coverts: each blade sweeps DOWN from the
    # leading edge by a growing angle and SHORTENS, so the bottom of the fan is
    # short folded coverts, not a second wing thrusting out. (off° measured
    # DOWNWARD from the leading primary, toward the lower-outer body quadrant.)
    ranks = (
        (0,   1.00, 1.00, 0.30),   # P1 — longest leading primary (the wing tip)
        (20,  0.92, 0.98, 0.32),   # P2
        (40,  0.80, 0.96, 0.36),   # P3
        (60,  0.66, 0.92, 0.42),   # secondary
        (82,  0.50, 0.88, 0.50),   # covert — short, folded under, trailing edge
        (104, 0.38, 0.82, 0.56),   # innermost covert hugging the shoulder
    )
    # `sign` rotates the downward sweep toward the OUTER-lower quadrant for each
    # side so both wings droop symmetrically away from the body centreline.
    for off, fac, wfac, blunt in ranks:
        a = base_ang + sign * math.radians(off)
        bone_blade(surf, root, a, L * fac, bw * wfac, s, tip_blunt=blunt)


# ── a single FAT triad-lit bone CLAW / toe (talons read at 32px) ──────────────
def fat_claw(surf, a, b, width, s, bend=0.0):
    """A fat tapered bone claw from `a` to `b`, optionally hooked by `bend`. WHY
    fat & triad-lit: round-1 talons read as scribbled thread-bundles; the AD
    note is 3 FAT triad-lit toes that survive at 32px. Built as a tapering
    polygon (wide root → clawed tip) with a dark-core underside + pale top sheen
    so each toe reads as a solid claw, not a line."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux                 # perpendicular (width axis)
    # a slight hook: pull the tip sideways by `bend`
    bx += nx * bend * width
    by += ny * bend * width
    hw = width * 0.5
    claw = [
        (ax + nx * hw, ay + ny * hw),
        (ax + nx * hw * 0.5 + ux * L * 0.5, ay + ny * hw * 0.5 + uy * L * 0.5),
        (bx, by),                     # clawed tip (point)
        (ax - nx * hw * 0.5 + ux * L * 0.5, ay - ny * hw * 0.5 + uy * L * 0.5),
        (ax - nx * hw, ay - ny * hw),
    ]
    pygame.draw.polygon(surf, INK, claw)
    pygame.draw.polygon(surf, BONE, claw)
    # dark-core underside (the lower/right of the toe) for volume
    pygame.draw.polygon(surf, BONE_D, [
        (ax - nx * hw * 0.6, ay - ny * hw * 0.6),
        (ax - nx * hw * 0.3 + ux * L * 0.5, ay - ny * hw * 0.3 + uy * L * 0.5),
        (bx, by),
    ])
    # pale top sheen rail
    pygame.draw.line(surf, QUILL_HI, (ax + nx * hw * 0.5, ay + ny * hw * 0.5),
                     (bx, by), max(1, int(width * 0.18)))
    pygame.draw.polygon(surf, INK, claw, max(1, int(width * 0.16)))


# ── a half-FOLDED wing = a tight hard SCALLOPED fan of fat blades (pillar cap) ─
def folded_fan(surf, root, base_ang, s, sign):
    """A half-FOLDED wing: FOUR fat bone-blades raked into a tight overlapping
    arc that sweeps DOWN the shaft, graded long→short, so the trailing edge
    reads as a hard SCALLOPED fan of layered quill-planks. WHY on the prop:
    round-1+2's cap read as 'another vertebra knot / small head'; the winged
    tell has to live on the pillar too. Tight raked overlap (not splayed) =
    folded wing, clearly off Nagaraja's splayed rib-spline hood. `sign` rakes
    the fan toward the outer-down quadrant for each side."""
    bw = max(4.0, 7.0 * s)
    # graded from the leading blade (longest, highest) down to a short folded
    # covert — each steps DOWN the shaft and shortens → scalloped folded edge
    for off, fac, wfac in ((0, 1.00, 1.00), (20, 0.82, 0.94),
                           (42, 0.64, 0.86), (66, 0.46, 0.78)):
        a = base_ang + sign * math.radians(off)
        bone_blade(surf, root, a, 34 * s * fac, bw * wfac, s, tip_blunt=0.40)


# ── the beaked bone-skull (vulture head — reused for hero + pillar cap) ───────
def bird_skull(surf, cx, cy, r, s, lit=True, agape=True):
    """A grumpy little bone-vulture skull: a domed lavender-grey cranium, a heavy
    hooked BEAK that is the unmistakable read (the ONLY beaked skull in the
    roster), and two deep sockets pinned with blood-orange glow. `agape` cracks
    the beak open (the sky-eater gape); `lit` lights the gape + sockets."""
    # cranium dome (the bone mass that owns the silhouette centre)
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.8 * s)), core=False)
    # a HEAVY brow ridge jutting forward and DOWN over the sockets — the grumpy
    # vulture scowl. It dips to a centre point above the beak (a frowning chevron)
    # so it overhangs each socket's top edge and breaks any round-disc symmetry:
    # the eyes read as recessed UNDER bone, not as a forward pair of lenses.
    brow = [(cx - int(r * 0.96), cy - int(r * 0.22)),
            (cx + int(r * 0.96), cy - int(r * 0.22)),
            (cx + int(r * 0.78), cy + int(r * 0.08)),
            (cx + int(r * 0.30), cy + int(r * 0.04)),
            (cx, cy + int(r * 0.20)),                       # centre dip (the frown)
            (cx - int(r * 0.30), cy + int(r * 0.04)),
            (cx - int(r * 0.78), cy + int(r * 0.08))]
    triad_blob(surf, BONE_D, brow,
               sheen_pts=[(cx - int(r * 0.90), cy - int(r * 0.20)),
                          (cx - int(r * 0.30), cy - int(r * 0.18)),
                          (cx - int(r * 0.40), cy - int(r * 0.02)),
                          (cx - int(r * 0.84), cy - int(r * 0.02))],
               ow=max(1, int(1.2 * s)))

    # === the HOOKED BEAK — the PROMINENT defining read =======================
    # WHY big & strongly hooked: round-2's beak was a tiny triangle the sockets
    # swamped — so the face didn't read BIRD. This is a heavy raptor beak: wide
    # at the cere where it meets the brow, hooking DOWN well past the cranium to
    # a sharp talon-like point that curls under, with a big blood-orange GAPE
    # cracked open mid-beak (the sky-eater). It is THE face focal; the gape is
    # the brightest thing on the head.
    beak_top = cy + int(r * 0.12)
    # UPPER MANDIBLE — a heavy SYMMETRIC bone hook: wide at the cere, narrowing
    # to a blunt point that curls DOWN-and-under. Built as a single clean wedge
    # so the silhouette reads "raptor beak," not a notched spur. The gape (below)
    # is cut into its lower face; the lower mandible closes underneath.
    hook_tip = (cx, cy + int(r * 1.36))                    # deep central hook point
    upper = [(cx - int(r * 0.50), beak_top),
             (cx + int(r * 0.50), beak_top),
             (cx + int(r * 0.40), cy + int(r * 0.66)),     # right cheek of beak
             (cx + int(r * 0.16), cy + int(r * 1.08)),
             hook_tip,                                     # blunt down-hook
             (cx - int(r * 0.16), cy + int(r * 1.08)),
             (cx - int(r * 0.40), cy + int(r * 0.66))]     # left cheek of beak
    triad_blob(surf, BONE, upper,
               core_pts=[(cx + int(r * 0.06), beak_top + int(r * 0.06)),
                         (cx + int(r * 0.46), beak_top + int(r * 0.02)),
                         (cx + int(r * 0.34), cy + int(r * 0.64)),
                         (cx + int(r * 0.12), cy + int(r * 1.04)),
                         hook_tip],
               sheen_pts=[(cx - int(r * 0.46), beak_top + int(r * 0.04)),
                          (cx - int(r * 0.12), beak_top + int(r * 0.02)),
                          (cx - int(r * 0.22), cy + int(r * 0.58)),
                          (cx - int(r * 0.40), cy + int(r * 0.50))],
               ow=max(1, int(1.6 * s)))
    # paired cere nostril slits high on the beak (the raptor tell)
    for sg in (-1, 1):
        pygame.draw.line(surf, BONE_DD,
                         (cx + sg * int(r * 0.18), beak_top + int(r * 0.12)),
                         (cx + sg * int(r * 0.26), cy + int(r * 0.40)),
                         max(1, int(1.5 * s)))

    if agape:
        # the GAPE — a big dark wedge cracked open low in the beak, glowing
        # blood-orange (the SOLE warm focal, the brightest mark on the head).
        # Centred and symmetric so it reads as an open maw, not a frown.
        gape = [(cx - int(r * 0.30), cy + int(r * 0.46)),
                (cx + int(r * 0.30), cy + int(r * 0.46)),
                (cx + int(r * 0.14), cy + int(r * 0.84)),
                (cx - int(r * 0.14), cy + int(r * 0.84))]
        pygame.draw.polygon(surf, INK, gape)
        if lit:
            pygame.draw.polygon(surf, RUST,
                [(cx - int(r * 0.24), cy + int(r * 0.49)),
                 (cx + int(r * 0.24), cy + int(r * 0.49)),
                 (cx + int(r * 0.10), cy + int(r * 0.80)),
                 (cx - int(r * 0.10), cy + int(r * 0.80))])
            pygame.draw.polygon(surf, GLOW,
                [(cx - int(r * 0.18), cy + int(r * 0.52)),
                 (cx + int(r * 0.18), cy + int(r * 0.52)),
                 (cx, cy + int(r * 0.76))])
            pygame.draw.polygon(surf, GLOW_BR,
                [(cx - int(r * 0.09), cy + int(r * 0.54)),
                 (cx + int(r * 0.09), cy + int(r * 0.54)),
                 (cx, cy + int(r * 0.68))])

    # === deep ANGULAR bone sockets pinned with blood-orange glow =============
    # WHY angular hollows, not round rims: round-1's round bone rings + a bridge
    # read as goggles/steampunk owl. A raptor's sockets are deep ANGULAR holes
    # bored straight into the skull bone under the brow — so each eye is a hard
    # keyhole hollow (no raised lens ring), the glow nested deep, with a WIDE
    # bony FOREHEAD KEEL between them (not a thin bridge bar). Reads raw
    # bone-vulture, not spectacles.
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.52)
        ey = cy + int(r * 0.02)
        # A deep ANGULAR keyhole hollow bored into the bone, TILTED so its long
        # axis runs from the high outer corner down toward the beak — a slanted
        # teardrop/triangle, NOT a forward round lens. The heavy brow above
        # overhangs the top edge; the glow is poured into the SAME angular shape
        # (not a circle) so it can never read as a compound-eye disc.
        socket = [
            (ex - sgn * int(r * 0.18), ey - int(r * 0.34)),   # inner top (under keel)
            (ex + sgn * int(r * 0.40), ey - int(r * 0.30)),   # outer top corner (sharp)
            (ex + sgn * int(r * 0.32), ey + int(r * 0.10)),   # outer bottom
            (ex - sgn * int(r * 0.08), ey + int(r * 0.36)),   # inner point (toward beak)
        ]
        pygame.draw.polygon(surf, INK, socket)
        pygame.draw.polygon(surf, BONE_DD, socket)
        if lit:
            # rust floor then blood-orange glow poured into the SAME angular
            # hollow (a scaled-in copy of the socket), nested deep — an inset
            # slit of fire, not a round lens.
            def inset(poly, t):
                gx = sum(p[0] for p in poly) / len(poly)
                gy = sum(p[1] for p in poly) / len(poly)
                return [(int(gx + (px - gx) * t), int(gy + (py - gy) * t))
                        for (px, py) in poly]
            pygame.draw.polygon(surf, RUST, inset(socket, 0.74))
            pygame.draw.polygon(surf, GLOW, inset(socket, 0.56))
            pygame.draw.polygon(surf, GLOW_BR, inset(socket, 0.30))
            # a tiny hot pin high in the hollow (catch-light, off-centre → alive)
            hx = ex + sgn * int(r * 0.06)
            hy = ey - int(r * 0.10)
            pygame.draw.circle(surf, GLOW_HOT, (hx, hy), max(1, int(r * 0.06)))
        else:
            pygame.draw.polygon(surf, INK, [
                (ex - int(r * 0.14), ey - int(r * 0.16)),
                (ex + sgn * int(r * 0.22), ey - int(r * 0.10)),
                (ex - sgn * int(r * 0.02), ey + int(r * 0.18))])
    # WIDE bony forehead keel between the sockets — a solid wedge of skull,
    # triad-lit, that physically SEPARATES the eyes (kills the bridge read)
    keel = [(cx - int(r * 0.16), cy - int(r * 0.34)),
            (cx + int(r * 0.16), cy - int(r * 0.34)),
            (cx + int(r * 0.12), cy + int(r * 0.30)),
            (cx - int(r * 0.12), cy + int(r * 0.30))]
    pygame.draw.polygon(surf, INK, keel)
    pygame.draw.polygon(surf, BONE, keel)
    pygame.draw.line(surf, QUILL_HI, (cx - int(r * 0.06), cy - int(r * 0.30)),
                     (cx - int(r * 0.04), cy + int(r * 0.24)), max(1, int(1.4 * s)))
    pygame.draw.line(surf, BONE_DD, (cx + int(r * 0.08), cy - int(r * 0.28)),
                     (cx + int(r * 0.06), cy + int(r * 0.24)), max(1, int(1.4 * s)))


# ── the spread-wing hero ──────────────────────────────────────────────────────
def draw_asthi_garuda(surf, cx, cy, s):
    """Bone-vulture spirit in a hard X: beaked skull centred over two tiered fans
    of rigid quill-blades flared wide, talons gripping below. `s` = unit scale
    around a ~130-unit figure. Drawn back-to-front: far quills → body → near
    quills overlap the shoulders → head last so the beak owns the centre."""

    head_c = (cx, cy - int(34 * s))
    hr = int(22 * s)
    shoulder_y = cy - int(8 * s)
    shoulder_dx = int(15 * s)

    # === WINGS — TWO tiered bird-wing fans (one per side) — NOT a 4-arm cross ==
    # WHY two wings not four: round-2 read as a four-winged INSECT. A bird has
    # ONE wing per side — long leading primaries rising up-and-out, a graded fan
    # of shorter coverts folding down-and-under behind. Drawn first/behind so the
    # breastbone overlaps the roots (anchored INTO the shoulders). The leading
    # primary of each side rises ABOVE the head and the fan droops to the lower-
    # outer quadrant, so the blacked-out chip reads as a beaked body between two
    # spread DROOPING wings (a bird Y/X), never a symmetric 4-spoke fly.
    wL = (cx - shoulder_dx, shoulder_y)
    wR = (cx + shoulder_dx, shoulder_y)
    # left leading primary up-and-out (~213°); fan sweeps DOWN (sign=-1 → toward
    # ~110°). right leading primary up-and-out (~-33°); fan sweeps DOWN (sign=+1).
    blade_wing(surf, wL, math.radians(213), s, sign=-1)
    blade_wing(surf, wR, math.radians(-33), s, sign=+1)

    # === BODY — a compact keeled breastbone (chibi, short) ===================
    body = [(cx - int(16 * s), shoulder_y - int(2 * s)),
            (cx + int(16 * s), shoulder_y - int(2 * s)),
            (cx + int(13 * s), cy + int(20 * s)),
            (cx, cy + int(28 * s)),                       # keel point
            (cx - int(13 * s), cy + int(20 * s))]
    triad_blob(surf, BONE, body,
               core_pts=[(cx + int(2 * s), shoulder_y),
                         (cx + int(15 * s), shoulder_y - int(1 * s)),
                         (cx + int(12 * s), cy + int(19 * s)),
                         (cx + int(1 * s), cy + int(26 * s))],
               sheen_pts=[(cx - int(15 * s), shoulder_y),
                          (cx - int(3 * s), shoulder_y - int(1 * s)),
                          (cx - int(6 * s), cy + int(12 * s)),
                          (cx - int(13 * s), cy + int(14 * s))],
               ow=max(1, int(1.8 * s)))
    # keel/sternum ridge + two rib-band grooves (the quill-ring motif echo)
    pygame.draw.line(surf, BONE_DD, (cx, shoulder_y + int(2 * s)),
                     (cx, cy + int(24 * s)), max(1, int(2 * s)))
    for i in range(2):
        ry = shoulder_y + int(8 * s) + i * int(9 * s)
        bw2 = int(13 * s) - i * int(2 * s)
        pygame.draw.arc(surf, BONE_DD, (cx - bw2, ry - int(6 * s), bw2 * 2, int(14 * s)),
                        math.radians(200), math.radians(340), max(1, int(2 * s)))

    # === TALONS — two fat bone feet, three CHISEL toes each, gripping below ===
    # WHY rebuilt fat: round-1+2 left these as thread-scribbles that dissolved to
    # fuzz at 32px. Each foot is a fat triad-lit SHANK dropping from the keel to
    # an ankle, then THREE wide chisel toes curling FORWARD (hooked tips) like a
    # talon clamped on an unseen perch — the same fat-blade construction as the
    # wings so the grip reads as solid bone, not noise, even tiny.
    ankle_y = cy + int(34 * s)
    for sgn in (-1, 1):
        ax = cx + sgn * int(8 * s)
        # fat shank from the keel base down-and-out to the ankle knuckle
        fat_claw(surf, (cx + sgn * int(4 * s), cy + int(22 * s)), (ax, ankle_y),
                 max(6.0, 8.0 * s), s, bend=0.0)
        # ankle knuckle — a small solid bone ball so toes look jointed, not stuck
        triad_circle(surf, BONE, (ax, ankle_y), max(2, int(4 * s)),
                     ow=max(1, int(1.2 * s)), sheen=True, core=False)
        # THREE fat chisel toes: front pair splay down-out, one rear toe curls
        # back-under (a raptor's gripping arrangement), each hooked at the tip
        toes = ((sgn * 0.50, 1.00, 0.45),   # outer front toe (down-and-out)
                (sgn * 0.05, 1.10, 0.30),   # centre front toe (longest, down)
                (-sgn * 0.42, 0.74, -0.40)) # rear toe curling back-under
        for dx_f, lf, bend in toes:
            tx = ax + dx_f * int(13 * s)
            ty = ankle_y + lf * int(13 * s)
            fat_claw(surf, (ax, ankle_y), (tx, ty), max(5.0, 6.5 * s), s, bend=bend)

    # === scapula KNOBS where the wings root into the shoulders ===============
    # WHY irregular bone wedges, not round rivets: round-2's two symmetric grey
    # ring-knuckles read as bolts/thorax-rivets (the insect tell again). These
    # are lumpy triad-lit scapula bones — an asymmetric pentagon tilted up-and-
    # out toward each wing, so the join reads SKELETAL, not mechanical.
    for sgn in (-1, 1):
        kx = cx + sgn * shoulder_dx
        knob = [(kx - sgn * int(7 * s), shoulder_y + int(4 * s)),
                (kx - sgn * int(6 * s), shoulder_y - int(6 * s)),
                (kx + sgn * int(4 * s), shoulder_y - int(8 * s)),
                (kx + sgn * int(9 * s), shoulder_y - int(1 * s)),
                (kx + sgn * int(5 * s), shoulder_y + int(6 * s))]
        triad_blob(surf, BONE, knob,
                   core_pts=[(kx, shoulder_y + int(5 * s)),
                             (kx + sgn * int(8 * s), shoulder_y),
                             (kx + sgn * int(4 * s), shoulder_y + int(5 * s))],
                   sheen_pts=[(kx - sgn * int(5 * s), shoulder_y - int(5 * s)),
                              (kx + sgn * int(2 * s), shoulder_y - int(6 * s)),
                              (kx - sgn * int(1 * s), shoulder_y - int(1 * s))],
                   ow=max(1, int(1.2 * s)))

    # === HEAD last — beak owns the centre ====================================
    # short neck vertebrae linking skull to keel
    pygame.draw.line(surf, INK, (cx, head_c[1] + int(hr * 0.9)),
                     (cx, shoulder_y - int(2 * s)), max(2, int(6 * s)))
    pygame.draw.line(surf, BONE, (cx, head_c[1] + int(hr * 0.9)),
                     (cx, shoulder_y - int(2 * s)), max(1, int(3.4 * s)))
    bird_skull(surf, head_c[0], head_c[1], hr, s, lit=True, agape=True)


# ── the perch-totem → pillar mirror ──────────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The perch-totem IS the pillar: a banded bone perch-pole wound with quill
    RINGS (the wing-quill motif continued) = the tileable shaft; a single
    wing-skull cap — wings half-FOLDED into a hard scalloped fan, beak/eye
    glowing, talons gripping toward the gap line — is the creature-derived
    gap-edge cap. Bottom-weighted toward the gap, on-axis, symmetric.

    `cap` names the END that faces the GAP."""
    shaft_w = int(14 * s)
    # central ink rod the bone segments thread onto
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    # === banded perch-pole segments wound with quill rings ===================
    seg_pitch = int(22 * s)
    cap_room = int(40 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    while y <= b1:
        # a bone barrel segment
        seg = [(cx - shaft_w, y + int(2 * s)),
               (cx - int(shaft_w * 0.7), y - int(8 * s)),
               (cx + int(shaft_w * 0.7), y - int(8 * s)),
               (cx + shaft_w, y + int(2 * s)),
               (cx + int(shaft_w * 0.7), y + int(12 * s)),
               (cx - int(shaft_w * 0.7), y + int(12 * s))]
        triad_blob(surf, BONE, seg,
                   core_pts=[(cx, y - int(1 * s)), (cx + shaft_w, y + int(2 * s)),
                             (cx + int(shaft_w * 0.7), y + int(12 * s)), (cx, y + int(10 * s))],
                   sheen_pts=[(cx - shaft_w, y + int(2 * s)),
                              (cx - int(shaft_w * 0.5), y - int(7 * s)),
                              (cx - int(shaft_w * 0.2), y - int(5 * s)),
                              (cx - int(shaft_w * 0.7), y + int(6 * s))],
                   ow=max(1, int(1.4 * s)))
        # a quill RING wound around the segment — short rigid quill ticks fanning
        # out either side (the wing-quill motif tiled down the pole)
        for sgn in (-1, 1):
            for k in range(3):
                a = math.radians(sgn * (110 + k * 30) if sgn > 0 else (250 - k * 30))
                rx = cx + sgn * shaft_w
                tip = (rx + sgn * int(9 * s), y + int(2 * s) - int((k - 1) * 5 * s))
                pygame.draw.line(surf, INK, (rx, y + int(2 * s)), tip, max(1, int(2.2 * s)))
                pygame.draw.line(surf, QUILL_HI if k == 1 else BONE,
                                 (rx, y + int(2 * s)), tip, max(1, int(1.2 * s)))
        # central foramen + transverse groove (the band)
        pygame.draw.circle(surf, BONE_DD, (cx, y + int(2 * s)), int(3 * s))
        pygame.draw.line(surf, BONE_DD, (cx - int(shaft_w * 0.6), y - int(6 * s)),
                         (cx + int(shaft_w * 0.6), y - int(6 * s)), max(1, int(1.4 * s)))
        y += seg_pitch

    # === gap-edge cap: wing-skull with half-FOLDED scalloped fan =============
    # WHY bottom-weighted: the beak + talons hang toward the gap so the heavy mass
    # sits at the gap edge, never top-heavy. Wings are half-folded into a tight
    # hard scalloped fan tucked back along the pole, not flared wide.
    cap_skull_r = int(16 * s)
    if cap == "bottom":
        cap_y = bot - int(26 * s)
        # half-FOLDED wings tucked UP the shaft (away from the down-facing gap):
        # leading blade rises up-and-out, the scalloped fan sweeps back along the
        # pole. Roots sit at the skull's shoulders. This is the WINGED tell on the
        # prop — clearly off Nagaraja's splayed rib-spline hood.
        fold_y = cap_y - int(6 * s)
        folded_fan(surf, (cx - int(11 * s), fold_y), math.radians(206), s, -1)
        folded_fan(surf, (cx + int(11 * s), fold_y), math.radians(-26), s, +1)
        talon_y = cap_y + int(cap_skull_r * 1.4)
        talon_dir = 1
    else:
        cap_y = top + int(26 * s)
        fold_y = cap_y + int(6 * s)
        folded_fan(surf, (cx - int(11 * s), fold_y), math.radians(154), s, +1)
        folded_fan(surf, (cx + int(11 * s), fold_y), math.radians(26), s, -1)
        talon_y = cap_y - int(cap_skull_r * 1.4)
        talon_dir = -1

    # two fat feet (three chisel toes each) gripping TOWARD the gap line — same
    # fat construction as the hero so the grip survives at pillar-chip scale
    for sgn in (-1, 1):
        gx = cx + sgn * int(8 * s)
        # short shank to an ankle knuckle, then three toes splaying toward the gap
        knuckle = (gx, talon_y)
        triad_circle(surf, BONE, knuckle, max(2, int(4 * s)),
                     ow=max(1, int(1.0 * s)), sheen=True, core=False)
        for dx_f, lf, bend in ((sgn * 0.55, 0.9, 0.4), (sgn * 0.08, 1.05, 0.25),
                               (-sgn * 0.42, 0.7, -0.35)):
            tx = gx + dx_f * int(13 * s)
            ty = talon_y + talon_dir * lf * int(13 * s)
            fat_claw(surf, knuckle, (tx, ty), max(4.0, 5.0 * s), s, bend=bend)

    # the skull caps the gap, beak + eyes glowing toward it
    # flip the skull so the beak points at the gap on the top segment
    if cap == "bottom":
        bird_skull(surf, cx, cap_y, cap_skull_r, s, lit=True, agape=True)
    else:
        # mirror vertically: draw onto a temp surface and flip so the beak/talons
        # point UP toward the gap, proving the clean top↔bottom mirror
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        bird_skull(tmp, cx, surf.get_height() - cap_y, cap_skull_r, s, lit=True, agape=True)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, 0))


# ── compose the review sheet ─────────────────────────────────────────────────
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
    sheet.blit(font_big.render("ASTHI-GARUDA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "bone-winged charnel sky-eater  ·  BEAKED bird-SKULL · TWO tiered quill-wings · bone sockets · fat talons · round 3",
        True, LABEL_DIM), (290, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_asthi_garuda(big, 178 * SS, 240 * SS, 1.95 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("BEAKED bird-skull (heavy hooked beak focal) between TWO tiered quill-wings —", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("long leading primaries, short coverts folding under (one wing/side, NOT 4-spoke).", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Angular BONE sockets + beak gape glow blood-orange. Fat 3-toe talons grip below.", True, LABEL_DIM), (14, 622))

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
    pygame.draw.rect(sheet, (58, 56, 68), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — perch-totem", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("banded bone perch-pole wound with quill", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("rings = shaft; wing-skull (half-folded fan,", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("talons gripping the gap) caps each edge — mirror visible", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_asthi_garuda(big, 48 * SS, 50 * SS, (32 / 132.0) * SS)
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

    # blacked-out 32px silhouette — the X-read TEST: it must read ONLY as a
    # spread-wing X, never a ball / radial fan / starburst
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_asthi_garuda(big, 48 * SS, 50 * SS, (32 / 132.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        # flatten every opaque pixel to solid ink → pure silhouette
        mask = pygame.mask.from_surface(small, 24)
        sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
        return sil

    sil_y = night_y + 188
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 214, 220), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 30))
    sheet.blit(font_sm.render("must read BEAKED BIRD, spread wings", True, LABEL_DIM), (sx + 104, sil_y + 48))

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
        (BONE, "violet-grey bone"), (BONE_D, "slate-violet sh"),
        (GLOW, "blood-orange glow"), (RUST, "rust shade"),
        (QUILL_HI, "pale-quill hi"), (SHEEN, "sheen"),
        (BONE_DD, "deep hollow"), (INK, "ink keyline"),
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
        "ELEVATED pipeline: SS=6 supersample → smoothscale.  STAY: flat fills · hard ink keyline (26,24,30) · "
        "dark-core→fill→top-left sheen triad · 1px grown outline · chibi · scary-CUTE · procedural-only · violet in BONE not glow.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
