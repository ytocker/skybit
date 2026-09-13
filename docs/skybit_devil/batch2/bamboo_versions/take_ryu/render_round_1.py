"""
Round-1 concept renderer for TAKE-RYU — the grove-coiling bamboo dragon
(bamboo-versions set, concept #1). Headless Pygame; ELEVATED pipeline
(supersample SS=6 -> smoothscale) so the jointed coil + whiskered head stay
crisp at downscale. Keeps the shipped house grammar: flat fills, hard 1-2px ink
keyline, dark-core -> flat-fill -> top-left rim-sheen triad, 1px alpha-grown
outline, chibi proportions, scary-CUTE; procedural-only (no gradients/PNGs/
soft halos).

WHY this is the NODE-SERPENT-COIL of the set: the whole serpentine body IS one
living green culm. The top read is a large whiskered dragon HEAD finial (a
clearly CRANIAL silhouette bump — stag-brow, snout, beard, lacquer-red whisker
beads) crowning an ACTIVE S-COIL of fat jointed node-segments, with asymmetric
leaf-fin flares bursting off the joints. NEVER a straight column — the cranial
head + live coil is exactly what separates Take-Ryu from Kaguya's straight
split-stalk at 32px. The jade body is held more saturated / heavier-value than
Kaguya's pale pearl, and a saturated lacquer-RED focal (whisker beads,
sheath-collars) pulls the cool jade clear of Kappa's pure yellow-green.

WHY the culm-body IS the pillar: a jointed node-segment tiles as the repeatable
shaft band (dark-core groove at each node-ring, flat jade bulge, top-left
sheen); the gap-edge cap is the whiskered dragon-head finial (top mirror) or a
single curled leaf-shoot finial (bottom mirror). A jointed culm is a pillar by
nature — the cleanest mirror in the set; bottom-rooted.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the triad/outline
helpers cloned from the lineage template.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# -- PINNED PALETTE (locked brief, take-ryu lane) -----------------------------
# Fresh-jade culm held COOL, with a saturated lacquer-RED focal. The red beads +
# sheath-collars are what pull the cool jade clear of Kappa's pure yellow-green;
# the jade is heavier-value than Kaguya's pale pearl so the two never converge.
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
    focal). Returns the (top, bottom) ring centres for chaining the coil."""
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
    leaf-fins off the joints (asymmetric, not paired): the brief pins asymmetric
    leaf-fin flares so the coil reads ALIVE and never a straight column — they
    break the silhouette outward at each node, the dragon-fin tell."""
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


# -- the whiskered dragon-HEAD finial (the load-bearing cranial read) ----------
def dragon_head(surf, cx, cy, r, s, lit=True, face_dir=1):
    """A large whiskered bamboo-dragon head: a clearly CRANIAL silhouette bump —
    a domed jade skull with a swept-back culm-node CROWN/horn pair (stag-brow),
    a blunt snout, an under-beard, lacquer-RED whisker beads streaming off the
    cheeks, and gold-rimmed eyes. WHY pushed HARD & large: the AD pin makes the
    cranial head the thing that separates Take-Ryu from Kaguya at 32px — it must
    be a big unmistakable HEAD bump at the top, not a node knot. `face_dir`
    (+1 right) turns the snout slightly off-axis so the head reads ALIVE."""
    fd = face_dir
    # === swept-back node-horns (the stag brow — first, behind the skull) =====
    for hx, ha, hl in ((-1, 232, 1.0), (1, -52, 1.0)):
        a = math.radians(ha)
        root = (cx + hx * int(r * 0.46), cy - int(r * 0.46))
        # a short jointed culm-horn = two stacked mini node-segments tapering
        tipx = root[0] + math.cos(a) * r * 1.05 * hl
        tipy = root[1] + math.sin(a) * r * 1.05 * hl
        horn = [(root[0] - hx * int(r * 0.20), root[1] + int(r * 0.04)),
                (root[0] + hx * int(r * 0.22), root[1] - int(r * 0.10)),
                ((tipx + root[0]) / 2 + hx * r * 0.10, (tipy + root[1]) / 2),
                (tipx, tipy),
                ((tipx + root[0]) / 2 - hx * r * 0.06, (tipy + root[1]) / 2 + r * 0.06)]
        triad_blob(surf, JADE, horn,
                   core_pts=[(root[0], root[1]), ((tipx+root[0])/2, (tipy+root[1])/2), (tipx, tipy)],
                   ow=max(1, int(1.2 * s)))
        # node-ring pinch on the horn (bamboo tell) + mint tip
        pygame.draw.line(surf, JADE_DD,
                         ((tipx+root[0])/2 - hx*r*0.10, (tipy+root[1])/2),
                         ((tipx+root[0])/2 + hx*r*0.10, (tipy+root[1])/2),
                         max(1, int(1.6 * s)))
        triad_circle(surf, MINT, (int(tipx), int(tipy)), max(2, int(r * 0.12)),
                     ow=max(1, int(1.0 * s)), sheen=False, core=False)

    # === whisker beads streaming off the cheeks (the lacquer-RED focal) ======
    # WHY long red-beaded whiskers: the unmistakable EASTERN-DRAGON tell + the
    # saturated red focal in one stroke; they trail outward & down so the head
    # silhouette grows tendrils, never a plain ball.
    for wx, wa, wn in ((-1, 150, 3), (1, 30, 3)):
        bx0 = cx + wx * int(r * 0.74)
        by0 = cy + int(r * 0.30)
        a = math.radians(wa)
        prev = (bx0, by0)
        for k in range(wn):
            nx = bx0 + math.cos(a) * r * (0.5 + k * 0.46) * wx * (1 if wx > 0 else -1) * abs(1)
            # march outward along the whisker arc, drooping down as it goes
            nx = bx0 + (k + 1) * wx * int(r * 0.42)
            ny = by0 + (k + 1) * int(r * 0.30) + int(math.sin((k + 1)) * r * 0.05)
            pygame.draw.line(surf, INK, prev, (nx, ny), max(2, int(2.6 * s)))
            pygame.draw.line(surf, RED_D, prev, (nx, ny), max(1, int(1.6 * s)))
            prev = (nx, ny)
        # lacquer-red bead at the whisker tip (gold-pinned)
        triad_circle(surf, RED, prev, max(2, int(r * 0.16)),
                     ow=max(1, int(1.0 * s)), sheen=False, core=True)
        pygame.draw.circle(surf, GOLD_HI, (prev[0] - int(r*0.05), prev[1] - int(r*0.05)),
                           max(1, int(r * 0.05)))

    # === the cranial dome (the big rounded skull mass owning the centre) =====
    triad_circle(surf, JADE, (cx, cy), r, ow=max(1, int(1.8 * s)), core=False)
    # a heavy ridged brow band above the eyes (breaks the plain-disc read)
    brow = [(cx - int(r * 0.92), cy - int(r * 0.10)),
            (cx + int(r * 0.92), cy - int(r * 0.10)),
            (cx + int(r * 0.70), cy + int(r * 0.16)),
            (cx, cy + int(r * 0.06)),
            (cx - int(r * 0.70), cy + int(r * 0.16))]
    triad_blob(surf, JADE_D, brow,
               sheen_pts=[(cx - int(r * 0.86), cy - int(r * 0.08)),
                          (cx - int(r * 0.20), cy - int(r * 0.06)),
                          (cx - int(r * 0.30), cy + int(r * 0.08)),
                          (cx - int(r * 0.80), cy + int(r * 0.10))],
               ow=max(1, int(1.2 * s)))

    # === the blunt SNOUT jutting down-forward (the muzzle bump) ==============
    sx = cx + fd * int(r * 0.10)
    snout_top = cy + int(r * 0.18)
    snout = [(sx - int(r * 0.50), snout_top),
             (sx + int(r * 0.50), snout_top),
             (sx + int(r * 0.42), cy + int(r * 0.78)),
             (sx + fd * int(r * 0.14), cy + int(r * 0.98)),   # nostril ridge
             (sx - int(r * 0.42), cy + int(r * 0.78))]
    triad_blob(surf, JADE, snout,
               core_pts=[(sx + int(r * 0.06), snout_top + int(r * 0.04)),
                         (sx + int(r * 0.46), snout_top),
                         (sx + int(r * 0.40), cy + int(r * 0.74)),
                         (sx + int(r * 0.06), cy + int(r * 0.92))],
               sheen_pts=[(sx - int(r * 0.44), snout_top + int(r * 0.04)),
                          (sx - int(r * 0.08), snout_top + int(r * 0.02)),
                          (sx - int(r * 0.18), cy + int(r * 0.66)),
                          (sx - int(r * 0.40), cy + int(r * 0.58))],
               ow=max(1, int(1.6 * s)))
    # nostril flare + a dark mouth-line set into a small toothy grin
    for ng in (-1, 1):
        pygame.draw.circle(surf, JADE_DD,
                           (sx + ng * int(r * 0.20), cy + int(r * 0.84)),
                           max(1, int(r * 0.07)))
    mouth = [(sx - int(r * 0.40), cy + int(r * 0.50)),
             (sx + int(r * 0.40), cy + int(r * 0.50)),
             (sx + int(r * 0.28), cy + int(r * 0.66)),
             (sx - int(r * 0.28), cy + int(r * 0.66))]
    pygame.draw.polygon(surf, INK, mouth)
    pygame.draw.polygon(surf, JADE_DD, mouth)
    # a couple of cute little fangs (scary-CUTE)
    for tx in (sx - int(r * 0.26), sx + int(r * 0.22)):
        pygame.draw.polygon(surf, SHEEN, [
            (tx, cy + int(r * 0.50)),
            (tx + int(r * 0.10), cy + int(r * 0.50)),
            (tx + int(r * 0.05), cy + int(r * 0.62))])

    # === a small under-BEARD tuft below the chin (dragon tell) ===============
    beard = [(sx - int(r * 0.26), cy + int(r * 0.96)),
             (sx + int(r * 0.26), cy + int(r * 0.96)),
             (sx + int(r * 0.10), cy + int(r * 1.30)),
             (sx - int(r * 0.04), cy + int(r * 1.18)),
             (sx - int(r * 0.18), cy + int(r * 1.30))]
    triad_blob(surf, JADE_D, beard,
               sheen_pts=[(sx - int(r * 0.22), cy + int(r * 0.98)),
                          (sx - int(r * 0.02), cy + int(r * 0.98)),
                          (sx - int(r * 0.12), cy + int(r * 1.16))],
               ow=max(1, int(1.2 * s)))

    # === eyes — gold-rimmed, glowing focal (scary-CUTE big pupils) ===========
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.46)
        ey = cy + int(r * 0.06)
        triad_circle(surf, GOLD, (ex, ey), max(2, int(r * 0.30)),
                     ow=max(1, int(1.2 * s)), sheen=False, core=False)
        if lit:
            pygame.draw.circle(surf, RED_D, (ex, ey), max(2, int(r * 0.22)))
            pygame.draw.circle(surf, INK,
                               (ex + sgn * int(r * 0.04), ey + int(r * 0.02)),
                               max(2, int(r * 0.16)))
            # hot catch-light (alive)
            pygame.draw.circle(surf, GOLD_HI,
                               (ex - sgn * int(r * 0.06), ey - int(r * 0.06)),
                               max(1, int(r * 0.07)))
        else:
            pygame.draw.circle(surf, INK, (ex, ey), max(2, int(r * 0.16)))


# -- the reared S-COIL hero ----------------------------------------------------
def draw_take_ryu(surf, cx, cy, s):
    """The grove woke up and reared: an ACTIVE S-COIL of fat jointed culm-segments
    crowned by the big whiskered dragon HEAD, leaf-fins bursting asymmetrically
    off the joints. `s` = unit scale around a ~150-unit-tall figure. Drawn
    bottom (root) -> up the coil -> head last so the cranial bump owns the top."""

    # an S-COIL spine: a serpentine path of node centres from the rooted base up
    # to the neck. WHY an active S (not a straight stack): the brief pins a live
    # coil — the body weaves left/right so it reads as a reared dragon, never a
    # column. Asymmetric leaf-fins flare off alternating joints.
    seg_h = 26.0 * s
    seg_w = 30.0 * s
    n = 6
    # x-offsets carve the S: down low it leans right, mid leans left, neck centres
    sway = (0.0, 0.62, 0.30, -0.55, -0.30, 0.18)
    fin_side = (1, -1, 1, -1, 1, -1)   # alternating asymmetric flares
    pts = []
    for i in range(n):
        seg_cy = cy + int((2.4 - i) * seg_h)
        seg_cx = cx + int(sway[i] * seg_w)
        pts.append((seg_cx, seg_cy, i))

    # rooted base flare (bottom segment widens into the ground/grove)
    base_cx, base_cy, _ = pts[0]
    triad_blob(surf, JADE_D,
               [(base_cx - int(seg_w * 0.78), base_cy + int(seg_h * 0.30)),
                (base_cx + int(seg_w * 0.78), base_cy + int(seg_h * 0.30)),
                (base_cx + int(seg_w * 1.02), base_cy + int(seg_h * 0.74)),
                (base_cx - int(seg_w * 1.02), base_cy + int(seg_h * 0.74))],
               ow=max(1, int(1.4 * s)))

    # draw the coil bottom -> up; leaf-fins first (behind) so the culm overlaps
    for (scx, scy, i) in pts:
        side = fin_side[i]
        if i < n - 1:
            ang = math.radians(20 if side > 0 else 160)
            leaf_fin(surf, (scx + side * int(seg_w * 0.42), scy - int(seg_h * 0.10)),
                     ang, 34 * s, 13 * s, s)
            # a second smaller fin lower on the same joint (clustered burst)
            leaf_fin(surf, (scx + side * int(seg_w * 0.40), scy + int(seg_h * 0.20)),
                     math.radians(40 if side > 0 else 140), 22 * s, 9 * s, s)

    for idx, (scx, scy, i) in enumerate(pts):
        culm_segment(surf, scx, scy, seg_w, seg_h, s, collar=(i % 2 == 1))
        # a short connective node-link to the segment above (keeps the coil
        # continuous as it sways) — a dark groove rod under the joint
        if idx < n - 1:
            nx, ny, _ = pts[idx + 1]
            pygame.draw.line(surf, JADE_D, (scx, scy - int(seg_h * 0.5)),
                             (nx, ny + int(seg_h * 0.5)), max(3, int(8 * s)))
            pygame.draw.line(surf, JADE_DD, (scx, scy - int(seg_h * 0.5)),
                             (nx, ny + int(seg_h * 0.5)), max(1, int(2.4 * s)))

    # head crowns the top segment, turned slightly off-axis
    neck_cx, neck_cy, _ = pts[-1]
    head_r = int(28 * s)
    head_cx = neck_cx + int(6 * s)
    head_cy = neck_cy - int(seg_h * 0.5) - int(head_r * 0.7)
    dragon_head(surf, head_cx, head_cy, head_r, s, lit=True, face_dir=1)


# -- the culm-body pillar mirror ----------------------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The culm-body IS the pillar: a stack of jointed node-segments = the
    tileable shaft (dark-core groove at each node-ring, flat jade bulge, top-left
    sheen, every other ring red-sheathed + gold-collared); the gap-edge cap is
    the whiskered dragon-HEAD finial (the end that faces the GAP) — or, on the
    mirror, the same head proving the clean top<->bottom mirror. Bottom-rooted,
    on-axis, symmetric. `cap` names the END that faces the GAP."""
    seg_h = int(30 * s)
    seg_w = int(30 * s)
    cap_room = int(58 * s)
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

    head_r = int(20 * s)
    if cap == "bottom":
        # whiskered dragon-head finial facing DOWN into the gap
        cap_cy = bot - int(26 * s)
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        dragon_head(tmp, cx, surf.get_height() - cap_cy, head_r, s, lit=True, face_dir=1)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, 0))
    else:
        # mirror edge: dragon-head finial facing UP toward the gap (proves mirror)
        cap_cy = top + int(26 * s)
        dragon_head(surf, cx, cap_cy, head_r, s, lit=True, face_dir=1)


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
        "grove-coiling bamboo dragon  ·  WHISKERED dragon-HEAD finial · ACTIVE S-COIL of node-segments · "
        "leaf-fin flares · lacquer-red focal · round 1",
        True, LABEL_DIM), (250, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_take_ryu(big, 180 * SS, 250 * SS, 1.55 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("Large whiskered dragon-HEAD (stag node-horns, lacquer-red beaded whiskers,", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("gold eyes) crowning an ACTIVE S-COIL of fat jointed culm node-segments —", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("asymmetric leaf-fin flares off the joints, red-sheath/gold-collar node-rings. NOT a column.", True, LABEL_DIM), (14, 622))

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
    sheet.blit(font_sm.render("(red-sheath/gold-collar rings); whiskered", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("dragon-head finial caps each gap edge — mirror visible", True, LABEL_DIM), (pcx - 4, 746))

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

    # blacked-out 32px silhouette — the read TEST: must read CRANIAL HEAD over a
    # coil, never a straight column / plain ball
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
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 34))
    sheet.blit(font_sm.render("CRANIAL head over a live S-coil,", True, LABEL_DIM), (sx + 104, sil_y + 52))
    sheet.blit(font_sm.render("never a straight column", True, LABEL_DIM), (sx + 104, sil_y + 70))

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

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
