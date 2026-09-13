"""
Round-2 concept renderer for TAKE-RYU — the grove-coiling bamboo dragon
(bamboo-versions set, concept #1). Headless Pygame; ELEVATED pipeline
(supersample SS=6 -> smoothscale) so the jointed coil + cranial head stay
crisp at downscale. Keeps the shipped house grammar: flat fills, hard 1-2px ink
keyline, dark-core -> flat-fill -> top-left rim-sheen triad, 1px alpha-grown
outline, chibi proportions, scary-CUTE; procedural-only (no gradients/PNGs/
soft halos).

WHY R2 vs R1 (AD verdict ITERATE — binding punch list):
1. The finial is now a CRANIAL DRAGON head in PROFILE, not a bug. R1 read as a
   beetle/mantis (round disc + upward ball-tip antennae + concentric goggle-
   eyes). R2 gives it a forward-jutting WEDGE SNOUT facing LEFT into motion
   (the profile has a real jaw line — a dragon skull is a wedge, not a ball),
   KILLS the upward antennae entirely, adds a BACK-SWEPT stag node-horn pair
   for the cranial bump, and swaps the round goggle-rings for an ANGLED ALMOND
   dragon-eye with a hard ink upper lid.
2. The lacquer-red beaded whiskers now route LOW and trail BACK from the snout
   — long sweeping barbels, never stiff sideways/upward antennae (the single
   biggest thing that sold "bug" in R1).
3. The S-COIL now lives in the OUTER SILHOUETTE — a real left-right swing where
   one cluster swings out one side and the next swings back, with the body
   TAPERED (fat near the head/upper coil, narrowing as it descends) so the
   blacked-out chip SNAKES instead of stacking.
4. Leaf-fin flares are now HARD-staggered asymmetrically (big flare one side at
   a joint, none at the next) to sell weight-shift.
5. The 32px day + night + blacked-out chips are the GATE: a forward-snout head-
   bump + a snaking outline must both survive.
6. The gap-edge head-cap is regenerated as a dragon SKULL profile; the lower-
   mirror curled-leaf-shoot alternate cap is present.

KEEP (AD said working, unchanged): shaft node-rhythm + clean pillar tile; the
dark-core groove -> flat jade -> top-left rim-sheen triad (procedural, no
gradients/halos); jade saturation (86,170,108) held heavier-value than Kaguya's
pearl; the lacquer-red focal lane. The sheen on the head is now a HARD stepped
facet on the top-left of the snout/brow, not a centered soft ball-patch.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the triad/outline
helpers cloned from the lineage template.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# -- PINNED PALETTE (locked brief, take-ryu lane — UNCHANGED) -----------------
JADE      = ( 86, 170, 108)   # culm-jade base (the dominant fill)
JADE_D    = ( 46, 120,  72)   # deep node-green shade / dark-core groove
JADE_DD   = ( 30,  84,  54)   # deepest culm hollow (node grooves, mouth)
MINT      = (168, 222, 170)   # pale leaf-mint sheen / highlight
SHEEN     = (210, 244, 206)   # hottest leaf sheen
RED       = (204,  64,  52)   # lacquer-red accent (whisker beads, sheath-collars)
RED_D     = (150,  40,  36)   # red shade
GOLD      = (222, 186,  90)   # gold node-collar
GOLD_HI   = (248, 224, 150)   # gold sheen
INK       = ( 24,  32,  26)   # hard ink keyline

BG        = ( 60,  78,  64)   # deep-grove review backdrop
PANEL     = ( 46,  60,  50)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (236, 244, 236)
LABEL_DIM = (188, 206, 192)


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


# -- one jointed CULM node-segment (the fat jade bulge + node-ring groove) -----
def culm_segment(surf, cx, cy, w, h, s, collar=False):
    """A fat jointed bamboo node-segment: a barrel of jade that bulges between
    two pinched node-rings, triad-lit (dark-core groove at the bottom ring, flat
    jade body, top-left sheen rail). WHY a bulged barrel and not a plain box:
    the node-ring pinch + bulge is the unmistakable BAMBOO tell — it must survive
    at 32px so the coil never reads as a plain rope/snake. `collar` bands the
    upper node-ring with a lacquer-red sheath + gold node-collar (the saturated
    focal). Returns the (top, bottom) ring centres for chaining the coil. The
    per-segment WIDTH is taper-controlled by the caller so the body reads as a
    serpent, not a uniform bead stack."""
    hw = w * 0.5
    hh = h * 0.5
    # the barrel — pinched at top & bottom rings, bulged at the belly
    barrel = [
        (cx - hw * 0.74, cy - hh),          # top ring left (pinched)
        (cx + hw * 0.74, cy - hh),          # top ring right
        (cx + hw,        cy - hh * 0.20),   # belly right
        (cx + hw,        cy + hh * 0.30),
        (cx + hw * 0.78, cy + hh),          # bottom ring right (pinched)
        (cx - hw * 0.78, cy + hh),          # bottom ring left
        (cx - hw,        cy + hh * 0.30),
        (cx - hw,        cy - hh * 0.20),   # belly left
    ]
    triad_blob(surf, JADE, barrel,
               core_pts=[(cx + hw * 0.10, cy - hh * 0.10),
                         (cx + hw,        cy - hh * 0.10),
                         (cx + hw,        cy + hh * 0.30),
                         (cx + hw * 0.78, cy + hh),
                         (cx + hw * 0.05, cy + hh)],
               sheen_pts=[(cx - hw * 0.66, cy - hh * 0.78),
                          (cx - hw * 0.10, cy - hh * 0.84),
                          (cx - hw * 0.20, cy + hh * 0.40),
                          (cx - hw * 0.78, cy + hh * 0.30)],
               ow=max(1, int(1.6 * s)))
    # bottom node-ring: a dark-core groove pinch (the joint) — the bamboo read
    pygame.draw.line(surf, JADE_DD, (cx - hw * 0.78, cy + hh),
                     (cx + hw * 0.78, cy + hh), max(2, int(2.6 * s)))
    pygame.draw.line(surf, JADE_D, (cx - hw * 0.70, cy + hh * 0.82),
                     (cx + hw * 0.70, cy + hh * 0.82), max(1, int(1.4 * s)))
    if collar:
        # lacquer-red sheath wrap + gold node-collar at the top ring — the
        # saturated focal that holds the jade clear of pure yellow-green
        ry = cy - hh
        sheath = [(cx - hw * 0.82, ry + hh * 0.06),
                  (cx + hw * 0.82, ry + hh * 0.06),
                  (cx + hw * 0.64, ry + hh * 0.40),
                  (cx - hw * 0.64, ry + hh * 0.40)]
        triad_blob(surf, RED, sheath,
                   core_pts=[(cx, ry + hh * 0.10), (cx + hw * 0.80, ry + hh * 0.08),
                             (cx + hw * 0.62, ry + hh * 0.40), (cx, ry + hh * 0.40)],
                   ow=max(1, int(1.2 * s)))
        pygame.draw.line(surf, GOLD, (cx - hw * 0.80, ry + hh * 0.02),
                         (cx + hw * 0.80, ry + hh * 0.02), max(2, int(2.4 * s)))
        pygame.draw.line(surf, GOLD_HI, (cx - hw * 0.74, ry - hh * 0.02),
                         (cx - hw * 0.10, ry - hh * 0.04), max(1, int(1.2 * s)))
    return (cx, cy - hh), (cx, cy + hh)


# -- an asymmetric leaf-fin flare bursting off a joint -------------------------
def leaf_fin(surf, root, ang, length, width, s):
    """One bamboo leaf-fin: a long lance-shaped blade swept along `ang`, triad-lit
    (dark-core lower half, flat jade, pale mint leading edge + a central rib). WHY
    leaf-fins off the joints (HARD-staggered, not paired): the brief pins
    asymmetric leaf-fin flares so the coil reads ALIVE and never a straight
    column — a big flare on the OUTSIDE of one swing, none at the next, sells the
    weight-shift the AD asked for."""
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca
    hw = width * 0.5
    tip = (root[0] + ca * length, root[1] + sa * length)
    belly = 0.42 * length
    bx = (root[0] + ca * belly, root[1] + sa * belly)
    leaf = [
        (root[0] + px * hw * 0.30, root[1] + py * hw * 0.30),
        (bx[0]   + px * hw,        bx[1]   + py * hw),
        tip,
        (bx[0]   - px * hw,        bx[1]   - py * hw),
        (root[0] - px * hw * 0.30, root[1] - py * hw * 0.30),
    ]
    pygame.draw.polygon(surf, INK, leaf)
    pygame.draw.polygon(surf, JADE, leaf)
    # dark-core trailing half (volume)
    pygame.draw.polygon(surf, JADE_D, [
        (root[0] - px * hw * 0.22, root[1] - py * hw * 0.22),
        (bx[0]   - px * hw,        bx[1]   - py * hw),
        tip,
        (bx[0]   - px * hw * 0.08, bx[1]   - py * hw * 0.08),
    ])
    # pale mint leading edge + central rib (the leaf tell)
    pygame.draw.line(surf, MINT, (bx[0] + px * hw * 0.7, bx[1] + py * hw * 0.7),
                     tip, max(1, int(width * 0.16)))
    pygame.draw.line(surf, JADE_DD, (bx[0], bx[1]), tip, max(1, int(width * 0.14)))
    pygame.draw.polygon(surf, INK, leaf, max(1, int(width * 0.14)))


# -- a low, back-trailing beaded whisker barbel --------------------------------
def whisker_barbel(surf, root, back_dir, r, s, n=3):
    """A long lacquer-RED beaded barbel that springs LOW off the snout and sweeps
    BACK and DOWN in a drooping arc (NEVER a stiff sideways/upward antenna — that
    was the R1 bug-tell). `back_dir` is the trailing direction (-1 = back/right,
    away from the leftward snout). Each barbel is an inked rope of red beads with
    a gold-pinned lacquer bead at the tip. The droop + back-sweep is the
    unmistakable EASTERN-DRAGON whisker read and carries the saturated red focal
    away from the head so the silhouette grows trailing tendrils."""
    bx0, by0 = root
    prev = (bx0, by0)
    # march back-and-down in a sagging arc; small beads along the rope
    for k in range(1, n + 1):
        t = k / n
        # back-sweep grows with t, droop accelerates (a hanging catenary feel)
        nx = bx0 + back_dir * int(r * (0.55 + 1.35 * t))
        ny = by0 + int(r * (0.34 + 1.05 * t * t))
        pygame.draw.line(surf, INK, prev, (nx, ny), max(2, int(3.0 * s)))
        pygame.draw.line(surf, RED_D, prev, (nx, ny), max(1, int(1.9 * s)))
        # a small mid-bead so it reads BEADED, not a plain string
        if k < n:
            triad_circle(surf, RED, (nx, ny), max(1, int(r * 0.10)),
                         ow=max(1, int(0.9 * s)), sheen=False, core=False)
        prev = (nx, ny)
    # fat lacquer-red bead at the trailing tip, gold catch-light
    triad_circle(surf, RED, prev, max(2, int(r * 0.18)),
                 ow=max(1, int(1.1 * s)), sheen=False, core=True)
    pygame.draw.circle(surf, GOLD_HI, (prev[0] + back_dir * int(r * 0.05),
                                       prev[1] - int(r * 0.05)),
                       max(1, int(r * 0.06)))


# -- the CRANIAL dragon-HEAD finial in PROFILE (the load-bearing read) ---------
def dragon_head(surf, cx, cy, r, s, lit=True, face_dir=-1):
    """A whiskered bamboo-dragon head in PROFILE — a clearly CRANIAL silhouette:
    a WEDGE SKULL whose snout JUTS forward (face_dir=-1 => left, into motion) so
    the profile has a real JAW LINE, a BACK-SWEPT stag node-horn/crest pair for
    the cranial bump, an ANGLED ALMOND eye with a hard ink upper lid, an under-
    beard, and long lacquer-RED beaded whiskers trailing LOW off the snout.

    WHY a wedge profile and not R1's round disc: a dragon skull is a WEDGE, never
    a ball — the forward muzzle + back-swept crest is exactly the cranial bump
    that must survive at 32px and separate Take-Ryu from Kaguya. `face_dir` -1
    points the snout left; +1 mirrors it. NO upward antennae, NO goggle-rings —
    those were the R1 bug-tells and are gone."""
    fd = face_dir          # -1 snout faces LEFT (into scroll); back is +x
    bk = -fd               # the BACK direction (crest/whiskers trail this way)

    # === BACK-SWEPT stag node-horn + crest pair (drawn first, behind skull) ===
    # WHY back-swept: a forward bug-antenna read is killed; horns sweeping BACK
    # over the nape are the cranial-bump tell of an eastern dragon.
    crest_root = (cx + bk * int(r * 0.20), cy - int(r * 0.62))
    # WHY tapered PRONGS with sharp jade tips (not round mint balls): a ball tip
    # is exactly what read as a bug-antenna in R1; a back-raked horn tapers to a
    # POINT. The longer/lower of the pair is the dominant crest spike.
    for hl, spread in ((1.30, 0.0), (0.95, 0.40)):
        # each horn is a short jointed culm-prong raking up-and-BACK, tapering
        a = math.atan2(-1.0, bk * (1.15 + spread))   # shallower rake, more BACK
        rx = crest_root[0] + bk * int(r * spread * 0.7)
        ry = crest_root[1] + int(r * spread * 0.22)
        tipx = rx + math.cos(a) * r * 1.25 * hl
        tipy = ry + math.sin(a) * r * 1.25 * hl
        midx = (rx + tipx) / 2 + bk * r * 0.08
        midy = (ry + tipy) / 2
        # a wide base tapering to a SHARP point (a horn, not a stalk+ball)
        horn = [(rx - bk * int(r * 0.26), ry + int(r * 0.12)),
                (rx + bk * int(r * 0.24), ry - int(r * 0.10)),
                (midx + bk * r * 0.10, midy),
                (tipx, tipy),                              # sharp point
                (midx - bk * r * 0.12, midy + r * 0.08)]
        triad_blob(surf, JADE, horn,
                   core_pts=[(rx, ry), (midx, midy), (tipx, tipy)],
                   ow=max(1, int(1.3 * s)))
        # node-ring pinch on the horn (the bamboo tell) — no round tip-bead
        pygame.draw.line(surf, JADE_DD,
                         (midx - bk * r * 0.12, midy),
                         (midx + bk * r * 0.12, midy),
                         max(1, int(1.8 * s)))
        # a tiny mint glint ON the inner edge near the tip (a facet, not a ball)
        pygame.draw.line(surf, MINT,
                         (midx, midy), (tipx, tipy), max(1, int(1.4 * s)))

    # === the WEDGE SKULL — a forward-tapering muzzle, not a disc ==============
    # Anatomy laid out in profile: high domed cranium at the BACK, tapering down
    # into a long jaw + jutting snout at the FRONT (the fd side). Built as one
    # silhouette polygon so the JAW LINE lives in the outer contour.
    L = fd                 # shorthand: front (snout) sign
    B = bk                 # back (cranium) sign
    skull = [
        (cx + B * int(r * 0.86), cy - int(r * 0.42)),   # back of cranium (high)
        (cx + B * int(r * 0.30), cy - int(r * 0.78)),   # top dome (brow ridge)
        (cx + L * int(r * 0.18), cy - int(r * 0.64)),   # brow over the eye
        (cx + L * int(r * 0.62), cy - int(r * 0.36)),   # bridge of the snout
        (cx + L * int(r * 1.02), cy - int(r * 0.10)),   # snout tip (FORWARD jut)
        (cx + L * int(r * 0.98), cy + int(r * 0.20)),   # nostril / upper lip
        (cx + L * int(r * 0.60), cy + int(r * 0.30)),   # mouth corner
        (cx + L * int(r * 0.20), cy + int(r * 0.50)),   # under-jaw forward
        (cx + B * int(r * 0.34), cy + int(r * 0.54)),   # jaw hinge (low back)
        (cx + B * int(r * 0.80), cy + int(r * 0.22)),   # cheek / nape
    ]
    triad_blob(surf, JADE, skull,
               # dark core sits on the BACK/under side (volume)
               core_pts=[(cx + B * int(r * 0.86), cy - int(r * 0.30)),
                         (cx + B * int(r * 0.10), cy - int(r * 0.40)),
                         (cx + L * int(r * 0.30), cy + int(r * 0.10)),
                         (cx + B * int(r * 0.34), cy + int(r * 0.52)),
                         (cx + B * int(r * 0.80), cy + int(r * 0.20))],
               ow=max(1, int(1.8 * s)))
    # HARD stepped sheen FACET on the top-left of the brow/snout (not a soft ball)
    sheen = [(cx + B * int(r * 0.18), cy - int(r * 0.70)),
             (cx + L * int(r * 0.14), cy - int(r * 0.58)),
             (cx + L * int(r * 0.50), cy - int(r * 0.34)),
             (cx + L * int(r * 0.30), cy - int(r * 0.30)),
             (cx + B * int(r * 0.10), cy - int(r * 0.48))]
    pygame.draw.polygon(surf, lerp(JADE, (255, 255, 255), 0.42), sheen)

    # === the JAW + toothy grin set into the wedge (scary-CUTE) ================
    mouth = [(cx + L * int(r * 0.96), cy + int(r * 0.14)),
             (cx + L * int(r * 0.58), cy + int(r * 0.26)),
             (cx + L * int(r * 0.24), cy + int(r * 0.42)),
             (cx + L * int(r * 0.30), cy + int(r * 0.30)),
             (cx + L * int(r * 0.60), cy + int(r * 0.16))]
    pygame.draw.polygon(surf, INK, mouth)
    pygame.draw.polygon(surf, JADE_DD, mouth)
    # a couple of little fangs along the upper lip (scary-CUTE)
    for tt in (0.78, 0.50):
        fx = cx + L * int(r * tt)
        fy = cy + int(r * (0.20 + (0.78 - tt) * 0.4))
        pygame.draw.polygon(surf, SHEEN, [
            (fx, fy),
            (fx + L * int(r * 0.10), fy),
            (fx + L * int(r * 0.05), fy + int(r * 0.14))])

    # nostril flare at the snout tip
    pygame.draw.circle(surf, JADE_DD,
                       (cx + L * int(r * 0.84), cy + int(r * 0.04)),
                       max(1, int(r * 0.08)))

    # === ANGLED ALMOND eye with a hard ink upper lid (NOT a goggle-ring) ======
    ex = cx + L * int(r * 0.30)
    ey = cy - int(r * 0.30)
    ew = int(r * 0.40)
    eh = int(r * 0.24)
    # almond outline: a leaf-shape canted along the brow, point toward the snout
    almond = [(ex - L * ew, ey),
              (ex, ey - eh),
              (ex + L * ew, ey - int(eh * 0.2)),
              (ex, ey + eh)]
    pygame.draw.polygon(surf, INK, almond)
    if lit:
        pygame.draw.polygon(surf, GOLD, almond)
        # angled gold sclera, hot ember pupil, gold catch-light
        pygame.draw.circle(surf, RED_D, (ex, ey), max(2, int(r * 0.15)))
        pygame.draw.circle(surf, INK,
                           (ex - L * int(r * 0.03), ey + int(r * 0.02)),
                           max(2, int(r * 0.10)))
        pygame.draw.circle(surf, GOLD_HI,
                           (ex + L * int(r * 0.05), ey - int(r * 0.05)),
                           max(1, int(r * 0.05)))
    else:
        pygame.draw.polygon(surf, INK, almond)
    # HARD ink upper lid — a heavy brow stroke over the eye (the menace tell)
    pygame.draw.line(surf, INK,
                     (ex - L * int(r * 0.50), ey - int(eh * 0.7)),
                     (ex + L * int(r * 0.40), ey - int(eh * 0.1)),
                     max(2, int(2.6 * s)))

    # === under-BEARD tuft below the jaw hinge (dragon tell) ===================
    beard = [(cx + B * int(r * 0.10), cy + int(r * 0.46)),
             (cx + L * int(r * 0.18), cy + int(r * 0.50)),
             (cx + L * int(r * 0.06), cy + int(r * 0.92)),
             (cx + B * int(r * 0.16), cy + int(r * 0.78)),
             (cx + B * int(r * 0.34), cy + int(r * 0.92))]
    triad_blob(surf, JADE_D, beard,
               sheen_pts=[(cx + B * int(r * 0.06), cy + int(r * 0.50)),
                          (cx + L * int(r * 0.10), cy + int(r * 0.52)),
                          (cx, cy + int(r * 0.74))],
               ow=max(1, int(1.2 * s)))

    # === LOW, back-trailing lacquer-RED beaded whiskers (the focal) ===========
    # WHY two, both LOW and trailing BACK: the R1 sideways/upward antennae are
    # gone; these spring from the snout corner + cheek and sweep back-and-down.
    whisker_barbel(surf, (cx + L * int(r * 0.88), cy + int(r * 0.18)),
                   back_dir=bk, r=r, s=s, n=3)
    whisker_barbel(surf, (cx + L * int(r * 0.40), cy + int(r * 0.34)),
                   back_dir=bk, r=r, s=s, n=3)


# -- a single curled leaf-shoot finial (the LOWER-mirror alternate cap) --------
def leaf_shoot_cap(surf, cx, cy, r, s, up=True):
    """The lower-mirror gap-edge cap: a single tender curled bamboo leaf-shoot
    (a young shoot tip), not the head. WHY the brief asks for this alternate: the
    head caps one gap edge, the curled shoot caps the mirror so the pillar repeat
    has two distinct ends like Big Reapy's bone-bident. A spiral-furled blade
    with a red sheath base + gold node-ring + mint tip."""
    d = -1 if up else 1    # the shoot grows toward the gap (d = vertical dir)
    base = (cx, cy)
    # red sheath at the base + gold node-ring (the focal carried to the shoot)
    sheath = [(cx - int(r * 0.5), cy),
              (cx + int(r * 0.5), cy),
              (cx + int(r * 0.34), cy + d * int(r * 0.5)),
              (cx - int(r * 0.34), cy + d * int(r * 0.5))]
    triad_blob(surf, RED, sheath, ow=max(1, int(1.2 * s)))
    pygame.draw.line(surf, GOLD, (cx - int(r * 0.48), cy),
                     (cx + int(r * 0.48), cy), max(2, int(2.2 * s)))
    # the furled blade — a lance that hooks into a curl at the tip
    tipx = cx + int(r * 0.30)
    tipy = cy + d * int(r * 1.7)
    blade = [(cx - int(r * 0.30), cy + d * int(r * 0.3)),
             (cx + int(r * 0.10), cy + d * int(r * 0.2)),
             (cx + int(r * 0.46), cy + d * int(r * 1.0)),
             (tipx + int(r * 0.18), tipy),               # curl-out
             (tipx - int(r * 0.20), tipy + d * int(r * 0.1)),  # hook back in
             (cx - int(r * 0.06), cy + d * int(r * 0.9))]
    triad_blob(surf, JADE, blade,
               core_pts=[(cx + int(r * 0.10), cy + d * int(r * 0.3)),
                         (cx + int(r * 0.46), cy + d * int(r * 1.0)),
                         (cx, cy + d * int(r * 0.9))],
               sheen_pts=[(cx - int(r * 0.26), cy + d * int(r * 0.34)),
                          (cx, cy + d * int(r * 0.30)),
                          (cx - int(r * 0.04), cy + d * int(r * 0.86))],
               ow=max(1, int(1.4 * s)))
    pygame.draw.line(surf, MINT, (cx, cy + d * int(r * 0.4)),
                     (tipx, tipy), max(1, int(1.6 * s)))
    triad_circle(surf, MINT, (tipx, tipy), max(2, int(r * 0.14)),
                 ow=max(1, int(1.0 * s)), sheen=False, core=False)


# -- the reared S-COIL hero ----------------------------------------------------
def draw_take_ryu(surf, cx, cy, s):
    """The grove woke up and reared: an ACTIVE S-COIL of fat jointed culm-segments
    crowned by the cranial dragon HEAD, leaf-fins bursting in a HARD-staggered
    pattern off the joints. `s` = unit scale around a ~150-unit-tall figure.

    WHY R2's coil lives in the OUTER SILHOUETTE: R1 was a vertical lump-stack on a
    near-straight axis. R2 swings the segment cluster hard out one side, then back
    the other, so the contour itself SNAKES; and the body TAPERS (fat at the
    head/upper coil, narrowing as it descends) so the blacked-out chip reads as a
    serpent, not a uniform bead column. Drawn root -> up -> head last."""

    seg_h = 25.0 * s
    seg_w0 = 34.0 * s      # widest segment (top, just under the head)
    n = 6
    # x-offsets carve a REAL left-right S: the contour swings out and back.
    # Big amplitude so the OUTER silhouette snakes (the AD gate).
    sway = (0.05, -1.05, -0.30, 0.95, 0.45, -0.20)   # bottom -> top
    # body taper: narrowest at the rooted base, fattest just below the head
    taper = (0.62, 0.74, 0.86, 0.98, 1.06, 1.08)     # bottom -> top
    # HARD-staggered fins: a BIG flare on the OUTSIDE of a swing, none next.
    # 0 = no fin, +/-1 = side, magnitude scales the flare.
    fin_plan = (0, ('R', 1.0), 0, ('L', 1.0), ('R', 0.6), 0)

    pts = []
    for i in range(n):
        seg_cy = cy + int((2.6 - i) * seg_h)
        seg_cx = cx + int(sway[i] * seg_w0 * 0.62)
        pts.append((seg_cx, seg_cy, i, seg_w0 * taper[i]))

    # rooted base flare (bottom segment widens into the ground/grove)
    base_cx, base_cy, _, base_w = pts[0]
    triad_blob(surf, JADE_D,
               [(base_cx - int(base_w * 0.86), base_cy + int(seg_h * 0.30)),
                (base_cx + int(base_w * 0.86), base_cy + int(seg_h * 0.30)),
                (base_cx + int(base_w * 1.10), base_cy + int(seg_h * 0.78)),
                (base_cx - int(base_w * 1.10), base_cy + int(seg_h * 0.78))],
               ow=max(1, int(1.4 * s)))

    # connective neck-rods first (behind), so culm bulges overlap the joints and
    # the swaying centres still read as ONE continuous serpent body.
    for idx in range(n - 1):
        scx, scy, _, _ = pts[idx]
        nx, ny, _, _ = pts[idx + 1]
        pygame.draw.line(surf, JADE_D, (scx, scy - int(seg_h * 0.5)),
                         (nx, ny + int(seg_h * 0.5)), max(4, int(11 * s)))
        pygame.draw.line(surf, JADE_DD, (scx, scy - int(seg_h * 0.5)),
                         (nx, ny + int(seg_h * 0.5)), max(2, int(3.0 * s)))

    # HARD-staggered leaf-fins (behind the culm bulges)
    for (scx, scy, i, sw) in pts:
        plan = fin_plan[i]
        if plan == 0:
            continue
        side_lbl, mag = plan
        side = 1 if side_lbl == 'R' else -1
        ang = math.radians(18 if side > 0 else 162)
        leaf_fin(surf, (scx + side * int(sw * 0.46), scy - int(seg_h * 0.06)),
                 ang, (40 * mag) * s, (15 * mag) * s, s)
        # a clustered second blade lower on the SAME joint (one-sided burst)
        leaf_fin(surf, (scx + side * int(sw * 0.44), scy + int(seg_h * 0.24)),
                 math.radians(42 if side > 0 else 138), (26 * mag) * s,
                 (10 * mag) * s, s)

    # draw the coil bottom -> up; collar every other ring
    for idx, (scx, scy, i, sw) in enumerate(pts):
        culm_segment(surf, scx, scy, sw, seg_h, s, collar=(i % 2 == 1))

    # head crowns the top segment, snout facing LEFT into motion
    neck_cx, neck_cy, _, neck_w = pts[-1]
    head_r = int(30 * s)
    # set the head back over the nape side of the last swing so the neck reads
    head_cx = neck_cx + int(head_r * 0.16)
    head_cy = neck_cy - int(seg_h * 0.5) - int(head_r * 0.72)
    dragon_head(surf, head_cx, head_cy, head_r, s, lit=True, face_dir=-1)


# -- the culm-body pillar mirror ----------------------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The culm-body IS the pillar: a stack of jointed node-segments = the
    tileable shaft (dark-core groove at each node-ring, flat jade bulge, top-left
    sheen, every other ring red-sheathed + gold-collared); the gap-edge cap is
    the cranial dragon-HEAD finial (the end facing the GAP) on the top mirror, and
    the single curled LEAF-SHOOT finial on the bottom mirror. Bottom-rooted,
    on-axis, symmetric. `cap` names the END that faces the GAP."""
    seg_h = int(30 * s)
    seg_w = int(30 * s)
    cap_room = int(64 * s)
    # central ink rod the node segments thread onto
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)

    # tile the node-segment shaft straight & on-axis (the clean repeat)
    y = b0
    k = 0
    while y <= b1:
        culm_segment(surf, cx, y + seg_h // 2, seg_w, seg_h, s, collar=(k % 2 == 0))
        y += seg_h
        k += 1

    head_r = int(22 * s)
    if cap == "bottom":
        # cranial dragon-head finial facing DOWN into the gap (snout into gap)
        cap_cy = bot - int(30 * s)
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        dragon_head(tmp, cx, surf.get_height() - cap_cy, head_r, s,
                    lit=True, face_dir=-1)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, 0))
    else:
        # mirror edge: the curled LEAF-SHOOT alternate cap reaching UP to the gap
        cap_cy = top + int(20 * s)
        leaf_shoot_cap(surf, cx, cap_cy, int(20 * s), s, up=True)


# -- compose the review sheet -------------------------------------------------
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
    sheet.blit(font_big.render("TAKE-RYU", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "grove-coiling bamboo dragon  ·  CRANIAL wedge-snout HEAD finial (faces left) · real left-right S-COIL · "
        "HARD-staggered leaf-fins · low trailing red whiskers · round 2",
        True, LABEL_DIM), (250, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_take_ryu(big, 180 * SS, 250 * SS, 1.55 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("CRANIAL wedge-skull head (forward-jutting snout facing LEFT, back-swept stag", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("node-horns, angled almond eye + hard ink lid, low trailing lacquer-red beaded", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("whiskers) crowning a REAL left-right S-COIL — tapered body, HARD-staggered fins.", True, LABEL_DIM), (14, 622))

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
    pygame.draw.rect(sheet, (44, 58, 48), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — culm-body", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("jointed node-segments = tileable shaft", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("(red-sheath/gold-collar rings); dragon-SKULL", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("head caps the top gap edge, curled leaf-shoot caps the mirror", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 110 * SS), pygame.SRCALPHA)
        draw_take_ryu(big, 48 * SS, 64 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 110))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, day_y + 20))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, night_y + 20))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blacked-out 32px silhouette — the GATE: must read a CRANIAL forward-snout
    # head-bump over a SNAKING coil, never a straight column / plain ball.
    def silhouette32():
        big = pygame.Surface((96 * SS, 110 * SS), pygame.SRCALPHA)
        draw_take_ryu(big, 48 * SS, 64 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 110))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        return mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))

    sil_y = night_y + 188
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 220, 214), (sx, sil_y, 96, 110))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 110), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 30))
    sheet.blit(font_sm.render("forward-snout CRANIAL bump", True, LABEL_DIM), (sx + 104, sil_y + 48))
    sheet.blit(font_sm.render("over a SNAKING outline —", True, LABEL_DIM), (sx + 104, sil_y + 66))
    sheet.blit(font_sm.render("the GATE", True, LABEL_DIM), (sx + 104, sil_y + 84))

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
    sheet.blit(font_sm.render("skull-cap", True, LABEL_DIM), (px2 - 6, night_y - 16))

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 636))
    swatches = [
        (JADE, "culm-jade base"), (JADE_D, "deep node-green"),
        (RED, "lacquer-red focal"), (GOLD, "gold node-collar"),
        (MINT, "leaf-mint sheen"), (SHEEN, "leaf sheen"),
        (JADE_DD, "deep culm hollow"), (INK, "ink keyline"),
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
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (24,32,26) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-CUTE · procedural-only · "
        "saturated jade heavier than Kaguya's pearl.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
