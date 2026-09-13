"""
Round-1 concept renderer for VERDIGRIS DROWNED-KING — the slumped drowned
undersea monarch (Batch 2 / KING SKULL royal brood, concept #5). Headless
Pygame; ELEVATED pipeline (supersample SS=6 -> smoothscale) so the extra
organic geometry stays crisp at downscale. Keeps the shipped house grammar:
flat saturated fills, hard 1-2px ink keyline (28,22,30), dark-core -> flat-fill
-> top-left rim-sheen triad, 1px alpha-grown outline, chibi proportions,
scary-CUTE; procedural-only (no gradients/PNGs).

WHY this king is the anti-court: every other monarch stands rigid and
symmetric on a hard architectural axis. The drowned king is the ONLY soft,
organic, asymmetric silhouette — he SLUMPS, weight collapsed onto one
shoulder, the whole outline trailing sideways like a body settled on the
seabed. The slump has to read as a posture before any frond resolves, so the
spine is a sagging diagonal and the head lolls off-axis.

WHY the fronds + coral antlers steal the "open ring" lesson from Citipati's
flame_halo: organic detail muds into a fringe at 32px. So the weed tendrils
are 2-3 FAT, clearly-SEPARATED tongues with sky showing BETWEEN them (never a
hairy fringe), and the coral crown is 3-4 FAT forks (not fine filigree). The
single baroque PEARL finial is the high-contrast crown-tell that survives the
downscale; the outer silhouette carries the rest.

WHY teal stays a thin accent: the cross-court rule bans a second saturated
mass. Sea-bleached grey-green bone is the dominant FIELD; verdigris-copper
teal lives only in the antler veining, barnacle crust, socket glow and a thin
sash; pearl-cream is the single bright focal. He is the ONLY teal king — and
his bone is pushed clearly LIGHTER + GREENER than Koschei's tallow grey-green
(190,192,158) so the two closest bone hues never collide — the gap is held on
value (luminance) FIRST, hue second (the safe colorblind read).

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers cloned from
the Citipati renderer, not runtime sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# -- PINNED PALETTE (locked brief) --------------------------------------------
# Sea-bleached grey-green bone is the dominant mass. WHY pushed LIGHTER + clearly
# GREENER than Koschei's tallow (190,192,158): those are the two closest bone
# hues in the court, so the gap is held on BOTH axes — luminance ~9% above the
# tallow (perceptual ~191 vs ~175) AND green pulled clearly ahead of R/B so it
# tilts cool-green where tallow tilts warm-grey. Leans on value first (the safe
# colorblind read), hue second.
BONE      = (200, 220, 198)   # sea-bleached grey-green bone (dominant fill)
BONE_D    = (138, 166, 144)   # bone dark-core (still green-dominant)
BONE_DD   = ( 96, 122, 106)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (232, 244, 226)   # bone top-left rim-sheen (sea-bleached highlight)
# verdigris-copper TEAL — the only teal in the court; a THIN accent never a mass
TEAL      = ( 42, 158, 152)   # verdigris-copper teal accent
TEAL_D    = ( 24, 104, 102)
TEAL_BR   = (118, 214, 200)   # bright verdigris (antler veining / glow)
TEAL_HOT  = (188, 244, 230)   # hottest verdigris (socket pin core)
# pearl-cream — the single high-contrast focal (the baroque finial)
PEARL     = (242, 240, 226)   # pearl-cream body
PEARL_SH  = (245, 248, 250)   # pearl hot highlight (the single brightest pixel)
PEARL_D   = (196, 198, 188)   # pearl shade
PEARL_RIM = (160, 196, 188)   # cool nacre rim on the pearl (teal-tinted)
CORAL     = (208, 224, 206)   # bleached coral antler bone (a touch warmer/lighter)
CORAL_D   = (150, 178, 162)
BARNACLE  = (122, 150, 138)   # crusted barnacle grey-teal (texture tell)
INK       = ( 28,  22,  30)   # hard ink keyline

BG        = ( 60,  84,  86)   # neutral sea-grey review backdrop
PANEL     = ( 46,  66,  70)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 244, 240)
LABEL_DIM = (188, 208, 202)


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


def night_rim(surf, color, px):
    """A cool pearl/teal RIM-sheen grown OUTSIDE the silhouette. WHY: the sea-
    bone mass loses value against the night sky, so the slump silhouette goes
    mushy (the Obsidian/Koschei night lesson). A wide bright rim painted under
    the ink keyline re-draws the whole outline in a luminous teal-pearl, so the
    posture carries on dark sky without touching the day read."""
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
    c = (int(c[0]), int(c[1]))
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


# -- a single FAT, separated weed tendril (the open-ring lesson) ---------------
def weed_tendril(surf, x0, y0, length, sway, width, s, droop=1.0):
    """One FAT trailing weed tendril, drawn as a broad tapering blade.
    WHY fat + separated + NO thin midrib (the flame_halo lesson, hardened for
    round 2): the round-1 blades muddied because a thin teal midrib + barnacle
    nubs added per-pixel noise that smeared at 32px. Round 2 makes the blade a
    single chunky leaf — wide root, soft rounded tip, a generous interior teal
    SHEEN (not a hairline) — so each of the 2-3 tongues survives downscale as a
    countable shape with sky on both sides. `sway` bows the blade for the
    underwater drift; `droop` pulls the tip down."""
    segs = 7
    width = width * 2.15                       # round 2b: genuinely fat tongue
    length = length * 0.58                      # stubby fat leaf, never a whip
    left, right = [], []
    cline = []
    for i in range(segs + 1):
        t = i / segs
        bx = x0 + math.sin(t * math.pi * 0.7) * sway
        by = y0 + length * t * droop + math.sin(t * 2.2) * (4 * s)
        # fat belly the whole length, rounding to a broad blunt tip (never a
        # point), so the blade keeps real mass and reads countable at 32px.
        w = width * (1.0 - 0.40 * max(0.0, t - 0.5) / 0.5)
        ang = math.pi / 2 + (sway / max(1.0, length)) * math.cos(t * math.pi * 0.7)
        nx, ny = math.cos(ang) * w * 0.5, -math.sin(ang) * w * 0.5
        left.append((bx + nx, by + ny))
        right.append((bx - nx, by - ny))
        cline.append((bx, by))
    blade = left + right[::-1]
    pygame.draw.polygon(surf, INK, blade)
    pygame.draw.polygon(surf, lerp(BONE, TEAL_D, 0.34), blade)   # weed-tinted bone
    # broad interior teal sheen down the windward half — a SHAPE not a hairline,
    # so the blade reads as living weed even after the downscale flattens detail.
    inner = [left[i] for i in range(segs + 1)]
    inner += [( (left[i][0] + cline[i][0]) / 2, (left[i][1] + cline[i][1]) / 2 )
              for i in range(segs, -1, -1)]
    pygame.draw.polygon(surf, lerp(TEAL, TEAL_D, 0.2), inner)
    pygame.draw.polygon(surf, INK, blade, max(1, int(1.6 * s)))


# -- one FAT coral-antler fork (3-4 of these = the crown) ----------------------
def coral_fork(surf, x0, y0, ang, length, width, s, depth=2):
    """A FAT branching coral fork. WHY fat forks not filigree: fine coral lace
    muds at 32px. Each fork is a chunky tapering bone-coral spur that splits
    once or twice into thick prongs, with clear sky between prongs. Verdigris
    veining + bleached coral fill keep it reading as living coral, not horn."""
    x1 = x0 + math.cos(ang) * length
    y1 = y0 + math.sin(ang) * length
    nx, ny = -math.sin(ang), math.cos(ang)
    w0, w1 = width, width * 0.5
    quad = [(x0 + nx * w0, y0 + ny * w0), (x1 + nx * w1, y1 + ny * w1),
            (x1 - nx * w1, y1 - ny * w1), (x0 - nx * w0, y0 - ny * w0)]
    triad_blob(surf, CORAL, quad,
               core_pts=[(x0 + nx * w0 * 0.2, y0 + ny * w0 * 0.2),
                         (x1, y1), (x0 - nx * w0, y0 - ny * w0)],
               ow=max(1, int(1.3 * s)))
    # verdigris vein up the spine of the fork
    pygame.draw.line(surf, TEAL, (x0, y0), (x1, y1), max(1, int(1.6 * s)))
    pygame.draw.line(surf, TEAL_BR, (x0, y0),
                     ((x0 + x1) / 2, (y0 + y1) / 2), max(1, int(1.0 * s)))
    if depth > 0:
        # wider split + fatter terminal prongs so each survives the 32px blackout
        spread = math.radians(34)
        coral_fork(surf, x1, y1, ang - spread, length * 0.70, width * 0.72, s, depth - 1)
        coral_fork(surf, x1, y1, ang + spread, length * 0.66, width * 0.68, s, depth - 1)
    else:
        # rounded coral knob tip so the prong reads soft, with a barnacle fleck
        triad_circle(surf, CORAL, (x1, y1), max(2, int(width * 0.5)),
                     ow=max(1, int(1.2 * s)), core=False)
        pygame.draw.circle(surf, BARNACLE, (int(x1), int(y1)), max(1, int(width * 0.22)))


# -- the baroque PEARL finial (the single high-contrast crown-tell) ------------
def baroque_pearl(surf, cx, cy, r, s):
    """A lumpy baroque pearl — the brightest pixel in the whole figure and the
    crown-tell that survives 32px. WHY a fat irregular blob not a clean circle:
    a baroque pearl is asymmetric, and the lump + offset hot highlight keep it
    reading as a luminous orb rather than a bone bead at any scale."""
    lump = []
    for i in range(11):
        a = i / 11 * 2 * math.pi
        rr = r * (1.0 + 0.14 * math.sin(a * 3 + 0.6))   # gentle baroque lumps
        lump.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(surf, INK, lump)
    pygame.draw.polygon(surf, PEARL_RIM, lump)            # cool nacre rim
    triad_circle(surf, PEARL, (cx, cy), int(r * 0.86), ow=max(1, int(1.4 * s)),
                 core=False, sheen=False)
    # offset top-left sheen = the single brightest mass in the whole figure.
    # WHY a BIG near-white cap (round 2): pearl/bone/teal all sat in one value
    # band, so the eye had no anchor. A broad ~(245,248,250) sheen covering most
    # of the upper-left pearl makes it unambiguously the brightest pixel cluster
    # at both 32px chips, so the eye lands on the crown finial first.
    pygame.draw.circle(surf, PEARL_SH,
                       (int(cx - r * 0.24), int(cy - r * 0.28)), max(2, int(r * 0.52)))
    pygame.draw.circle(surf, (252, 254, 255),
                       (int(cx - r * 0.32), int(cy - r * 0.36)), max(1, int(r * 0.24)))
    pygame.draw.polygon(surf, INK, lump, max(1, int(1.4 * s)))


# -- a two-segment bone limb (cloned from the house grammar) -------------------
def bone_limb(surf, p0, p1, p2, thick, s, joint=True):
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


# -- the slumped drowned king -------------------------------------------------
def draw_king(surf, cx, cy, s):
    """The drowned monarch SLUMPED on the seabed: weight collapsed onto the
    figure's left, head lolled off-axis, the whole outline trailing soft and
    asymmetric (the only organic silhouette in the court). Branching coral-
    antler crown + a baroque pearl finial crown the lolling head; 2-3 FAT weed
    tendrils trail off the shoulders and hem. `s` = unit scale around a ~130-
    unit figure."""

    # vertical anchors — the SLUMP is baked into the skeleton:
    # spine sags as a diagonal, head rides off-axis to the figure's left.
    lean = int(16 * s)                       # how far the mass collapses sideways
    head_c = (cx - lean - int(2 * s), cy - int(34 * s))
    hr = int(23 * s)
    hip_y = cy + int(26 * s)
    hip_cx = cx + int(4 * s)                  # hips drift the opposite way (settled)

    # === TRAILING WEED TENDRILS (drawn first -> behind the body) =============
    # WHY behind + only 2-3 FAT blades: they read as a soft trailing skirt of
    # weed with SKY between them, the organic-silhouette tell, without muddying
    # the body. Placed off the low-shoulder + the hem, sweeping the slump way.
    # TWO FAT blades only (brief allows 2-3) — anchored at the hips and swept
    # apart so BOTH hang fully clear of the torso as countable fat tongues with
    # a wide wedge of sky between them. A third would only peek out as an
    # occluded sliver, which is exactly the fringe-mush the gate forbids.
    weed_tendril(surf, hip_cx - int(26 * s), hip_y + int(6 * s),
                 int(76 * s), -int(20 * s), int(16 * s), s, droop=1.16)
    weed_tendril(surf, hip_cx + int(28 * s), hip_y + int(6 * s),
                 int(72 * s),  int(22 * s), int(16 * s), s, droop=1.06)

    # === LEGS — folded/settled, not a wide dance stance ======================
    # WHY tucked + soft: a drowned body slumps, it does not plant; the legs fold
    # under so the silhouette pools downward rather than striding.
    leg_th = int(13 * s)
    hipL = (hip_cx - int(12 * s), hip_y)
    kneeL = (hip_cx - int(24 * s), hip_y + int(20 * s))
    footL = (hip_cx - int(12 * s), hip_y + int(40 * s))
    bone_limb(surf, hipL, kneeL, footL, leg_th, s)
    hipR = (hip_cx + int(12 * s), hip_y)
    kneeR = (hip_cx + int(22 * s), hip_y + int(16 * s))
    footR = (hip_cx + int(28 * s), hip_y + int(36 * s))
    bone_limb(surf, hipR, kneeR, footR, leg_th, s)
    for (fx, fy), sgn in ((footL, -1), (footR, +1)):
        foot = [(fx - int(4 * s), fy - int(2 * s)), (fx + sgn * int(14 * s), fy + int(2 * s)),
                (fx + sgn * int(13 * s), fy + int(9 * s)), (fx - int(5 * s), fy + int(7 * s))]
        triad_blob(surf, BONE, foot, ow=max(1, int(1.3 * s)))

    # === PELVIS — a soft settled wing-block, tilted with the slump ===========
    pelvis = [(hip_cx - int(17 * s), hip_y - int(3 * s)),
              (hip_cx + int(16 * s), hip_y - int(6 * s)),
              (hip_cx + int(13 * s), hip_y + int(10 * s)),
              (hip_cx, hip_y + int(13 * s)),
              (hip_cx - int(15 * s), hip_y + int(9 * s))]
    triad_blob(surf, BONE, pelvis,
               core_pts=[(hip_cx - int(6 * s), hip_y + int(2 * s)),
                         (hip_cx + int(13 * s), hip_y - int(2 * s)),
                         (hip_cx + int(12 * s), hip_y + int(9 * s)),
                         (hip_cx, hip_y + int(12 * s))],
               ow=max(1, int(1.5 * s)))
    pygame.draw.circle(surf, BONE_DD, (hip_cx, hip_y + int(2 * s)), int(4 * s))

    # spine — a SAGGING diagonal from pelvis up to the lolled chest (the slump)
    spine_top = (cx - lean + int(2 * s), cy - int(16 * s))
    spine = [(hip_cx, hip_y - int(2 * s)),
             (cx - int(4 * s), cy + int(8 * s)),
             spine_top]
    pygame.draw.lines(surf, INK, False, spine, int(8 * s))
    pygame.draw.lines(surf, BONE, False, spine, int(5 * s))

    # === RIBCAGE — barrel tilted/collapsed toward the low shoulder ===========
    rc_cx, rc_cy = cx - int(lean * 0.5), cy - int(4 * s)
    rc_w, rc_h = int(33 * s), int(40 * s)
    # the cage leans: top edge shifted toward the lolling head for the slump
    cage = [(rc_cx - rc_w // 2 - int(3 * s), rc_cy - rc_h // 2 + int(4 * s)),
            (rc_cx + rc_w // 2 - int(2 * s), rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.40), rc_cy + rc_h // 2 + int(2 * s))]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(4 * s)),
                         (rc_cx + rc_w // 2 - int(2 * s), rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 - int(1 * s), rc_cy - rc_h // 2 + int(5 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(6 * s)),
                          (rc_cx - rc_w // 2 - int(1 * s), rc_cy + int(4 * s))],
               ow=max(1, int(1.7 * s)))
    # rib bands — drooping arcs (the body sagged) + a barnacle crust patch
    for i in range(4):
        ry = rc_cy - rc_h // 2 + int(9 * s) + i * int(8 * s)
        bw = int(rc_w * (0.46 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(6 * s), bw * 2, int(16 * s)),
                        math.radians(200), math.radians(340), max(2, int(2.2 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(7 * s)),
                     (rc_cx, rc_cy + int(7 * s)), max(1, int(2 * s)))
    # barnacle crust on the lower cage (texture tell — clustered nubs)
    for (ox, oy, rr) in ((-9, 12, 3.0), (-5, 16, 2.0), (-12, 8, 2.0), (6, 14, 2.4)):
        bx, by = rc_cx + int(ox * s), rc_cy + int(oy * s)
        pygame.draw.circle(surf, BARNACLE, (bx, by), max(1, int(rr * s)))
        pygame.draw.circle(surf, INK, (bx, by), max(1, int(rr * s)), 1)
        pygame.draw.circle(surf, TEAL_BR, (bx - int(s), by - int(s)), max(1, int(rr * s * 0.4)))

    # === ARMS — a SLUMP, not a flourish: one arm hangs slack, the other ======
    # props the king up on the seabed (asymmetric organic posture).
    arm_th = int(8 * s)
    shoulderL = (rc_cx - int(15 * s), rc_cy - rc_h // 2 + int(7 * s))
    shoulderR = (rc_cx + int(15 * s), rc_cy - rc_h // 2 + int(6 * s))
    # both arms tuck CLOSE to the torso (slack/folded) so they don't sprout
    # competing thin whips that tangle with the FAT weed tongues at 32px.
    elbowL = (rc_cx - int(22 * s), rc_cy + int(8 * s))
    handL = (rc_cx - int(16 * s), rc_cy + int(26 * s))
    bone_limb(surf, shoulderL, elbowL, handL, arm_th, s)
    elbowR = (rc_cx + int(21 * s), rc_cy + int(10 * s))
    handR = (rc_cx + int(14 * s), rc_cy + int(28 * s))
    bone_limb(surf, shoulderR, elbowR, handR, arm_th, s)
    for (hx, hy), splay in ((handL, -1), (handR, +1)):
        triad_circle(surf, BONE, (hx, hy), int(5 * s), ow=max(1, int(1.2 * s)), core=False)
        for k in range(-1, 3):
            ang = math.radians(70 + k * 24) if splay > 0 else math.radians(70 + k * 24)
            ex = hx + math.cos(ang) * int(8 * s)
            ey = hy + math.sin(ang) * int(8 * s)
            pygame.draw.line(surf, INK, (hx, hy), (ex, ey), max(1, int(1.5 * s)))
            pygame.draw.line(surf, BONE, (hx, hy), (ex, ey), max(1, int(1 * s)))

    # === SASH — a thin verdigris ribbon across the chest (accent, not mass) ==
    sash = [(rc_cx - int(19 * s), rc_cy - int(2 * s)),
            (rc_cx + int(15 * s), rc_cy + int(8 * s)),
            (hip_cx + int(18 * s), hip_y + int(4 * s)),
            (hip_cx + int(16 * s), hip_y + int(10 * s)),
            (rc_cx + int(13 * s), rc_cy + int(14 * s)),
            (rc_cx - int(19 * s), rc_cy + int(5 * s))]
    triad_blob(surf, TEAL, sash,
               sheen_pts=[(rc_cx - int(18 * s), rc_cy - int(1 * s)),
                          (rc_cx + int(13 * s), rc_cy + int(9 * s)),
                          (rc_cx + int(12 * s), rc_cy + int(12 * s)),
                          (rc_cx - int(18 * s), rc_cy + int(2 * s))],
               ow=max(1, int(1.3 * s)))
    pygame.draw.line(surf, TEAL_BR, (rc_cx - int(18 * s), rc_cy + int(3 * s)),
                     (hip_cx + int(16 * s), hip_y + int(7 * s)), max(1, int(1.4 * s)))

    # === SKULL HEAD — chibi scary-cute, LOLLED off-axis (the slump tell) =====
    # the head tilts: render sockets/jaw rotated slightly so it reads as lolling.
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    tilt = -0.18      # radians — head lolled toward the collapsed shoulder
    def rot(px, py):
        dx, dy = px - head_c[0], py - head_c[1]
        return (head_c[0] + dx * math.cos(tilt) - dy * math.sin(tilt),
                head_c[1] + dx * math.sin(tilt) + dy * math.cos(tilt))
    # cheek hollows
    for sgn in (-1, 1):
        cxp, cyp = rot(head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.30))
        pygame.draw.circle(surf, BONE_D, (int(cxp), int(cyp)), int(hr * 0.25))
    # big round sockets — scary-CUTE with verdigris pin-lights (the only glow)
    for sgn in (-1, 1):
        ex, ey = rot(head_c[0] + sgn * int(hr * 0.44), head_c[1] - int(hr * 0.02))
        ex, ey = int(ex), int(ey)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.34))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.28))
        pygame.draw.circle(surf, TEAL, (ex + sgn * int(1 * s), ey + int(1 * s)), int(hr * 0.15))
        pygame.draw.circle(surf, TEAL_HOT, (ex, ey - int(1 * s)), max(1, int(hr * 0.08)))
    # nose triangle
    n0 = rot(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.24))
    n1 = rot(head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.24))
    n2 = rot(head_c[0], head_c[1] + int(hr * 0.52))
    pygame.draw.polygon(surf, BONE_DD, [n0, n1, n2])
    # grin row (cute, slightly slack/open for the drowned look)
    m0 = rot(head_c[0] - int(hr * 0.5), head_c[1] + int(hr * 0.68))
    m1 = rot(head_c[0] + int(hr * 0.5), head_c[1] + int(hr * 0.68))
    pygame.draw.line(surf, INK, m0, m1, max(1, int(2 * s)))
    for k in range(-3, 4):
        t0 = rot(head_c[0] + int(k * hr * 0.16), head_c[1] + int(hr * 0.58))
        t1 = rot(head_c[0] + int(k * hr * 0.16), head_c[1] + int(hr * 0.80))
        pygame.draw.line(surf, INK, t0, t1, max(1, int(1 * s)))
    # a single barnacle on the temple (texture tell instead of an ear ornament)
    bx, by = rot(head_c[0] - int(hr * 0.9), head_c[1] - int(hr * 0.1))
    pygame.draw.circle(surf, BARNACLE, (int(bx), int(by)), max(2, int(hr * 0.16)))
    pygame.draw.circle(surf, INK, (int(bx), int(by)), max(2, int(hr * 0.16)), max(1, int(1 * s)))
    pygame.draw.circle(surf, TEAL_BR, (int(bx - s), int(by - s)), max(1, int(hr * 0.06)))

    # === CORAL-ANTLER CROWN (the top tell) — 3-4 FAT forks + the PEARL =======
    # WHY forks fan ASYMMETRICALLY: even the crown obeys the slump — the antlers
    # rake toward the collapsed side, reinforcing the organic lean. The forks
    # are FAT with clear sky between prongs (the open-ring lesson). The baroque
    # pearl finial caps the centre as the single brightest, high-contrast tell.
    crown_y = head_c[1] - int(hr * 0.86)
    # base circlet the antlers spring from — a thin verdigris band
    band_pts = []
    for i in range(11):
        a = math.radians(208 + i * (124 / 10))
        band_pts.append(rot(head_c[0] + math.cos(a) * hr * 1.02,
                            head_c[1] + math.sin(a) * hr * 1.02))
    pygame.draw.lines(surf, INK, False, band_pts, int(6 * s))
    pygame.draw.lines(surf, TEAL, False, band_pts, int(4 * s))
    pygame.draw.lines(surf, TEAL_BR, False, band_pts[:6], max(1, int(1.4 * s)))
    # 4 FAT coral forks raking across the top, leaning toward the slump side
    # Round 2: 4 FATTER forks splayed WIDER so each terminal prong keeps clear
    # sky around it and survives the blackout as a separate antler, not a blob.
    fork_specs = [
        (math.radians(232), int(36 * s), int(8.6 * s)),   # far collapsed-side fork
        (math.radians(256), int(43 * s), int(9.4 * s)),
        (math.radians(286), int(41 * s), int(9.0 * s)),
        (math.radians(310), int(32 * s), int(7.8 * s)),   # short bracing-side fork
    ]
    for ang, length, width in fork_specs:
        bx = head_c[0] + math.cos(ang) * hr * 0.92
        by = head_c[1] + math.sin(ang) * hr * 0.92
        bx, by = rot(bx, by)
        # rake every fork toward the collapsed (left) side for the asymmetry
        coral_fork(surf, bx, by, ang - 0.12, length, width, s, depth=1)
    # the baroque PEARL finial — single brightest pixel, riding the centre fork
    px = head_c[0] + math.cos(math.radians(270)) * hr * 1.62
    py = head_c[1] + math.sin(math.radians(270)) * hr * 1.62
    px, py = rot(px, py)
    baroque_pearl(surf, px, py, int(hr * 0.52), s)


# -- pillar: the drowned king's own forms tiled (coral + vertebra + weed) ------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The pillar IS the king's reef-throne: a stacked column of barnacle-
    crusted vertebra beads (the rib-band motif) = the tileable shaft; a single
    FAT coral fork + baroque pearl at the gap edge = the creature-derived cap,
    with two FAT weed tendrils trailing off the gap so the soft organic
    language reads even on the pillar. On-axis, symmetric, never top-heavy.

    `cap` names the END that faces the GAP."""
    shaft_w = int(15 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    bead_pitch = int(20 * s)
    cap_room = int(34 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    bead_i = 0
    while y <= b1:
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
        pygame.draw.circle(surf, BONE_DD, (cx, y + int(2 * s)), int(4 * s))
        pygame.draw.circle(surf, INK, (cx, y + int(2 * s)), int(4 * s), max(1, int(1 * s)))
        # barnacle crust — round 2: only every OTHER bead and lower contrast, so
        # the crust reads as texture instead of strobing as it scrolls past.
        if bead_i % 2 == 0:
            for ox in (-int(bw * 0.7), int(bw * 0.6)):
                pygame.draw.circle(surf, lerp(BARNACLE, BONE, 0.18),
                                   (cx + ox, y + int(5 * s)), max(1, int(2.0 * s)))
        y += bead_pitch
        bead_i += 1

    # === gap-edge cap: FAT coral fork + pearl + two trailing weed tendrils ===
    if cap == "bottom":
        cap_y = bot - int(20 * s)
        grow_dir = 1     # antlers/weed reach DOWN toward the gap
    else:
        cap_y = top + int(20 * s)
        grow_dir = -1
    # two FAT weed tendrils trailing into the gap (drawn first). `droop` sign
    # alone steers direction so a top-cap's weed reaches UP into the gap.
    weed_tendril(surf, cx - int(11 * s), cap_y, int(30 * s),
                 -int(14 * s), int(11 * s), s, droop=1.0 * grow_dir)
    weed_tendril(surf, cx + int(11 * s), cap_y, int(28 * s),
                 int(12 * s), int(10 * s), s, droop=1.0 * grow_dir)
    # a verdigris collar where cap meets shaft
    collar_y = cap_y - int(16 * s) * grow_dir
    pygame.draw.rect(surf, INK, (cx - int(11 * s), collar_y - int(3 * s), int(22 * s), int(7 * s)))
    pygame.draw.rect(surf, TEAL, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(5 * s)))
    pygame.draw.rect(surf, TEAL_BR, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(2 * s)))
    # the FAT coral fork crowning the cap, reaching toward the gap
    ang = math.radians(90 if grow_dir > 0 else 270)
    coral_fork(surf, cx, collar_y, ang, int(24 * s), int(7 * s), s, depth=1)
    # baroque pearl at the very gap edge = the cap's high-contrast tell
    baroque_pearl(surf, cx, cap_y + int(8 * s) * grow_dir, int(8 * s), s)


# -- compose the review sheet -------------------------------------------------
SS = 6
FIG_UNITS = 130.0


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_king(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def load_font(size, bold=True):
    # FONT path is five levels up from this file -> repo-root game/assets.
    here = os.path.dirname(os.path.abspath(__file__))
    ttf = os.path.abspath(os.path.join(here, "..", "..", "..", "..", "..",
                                       "game", "assets", "LiberationSans-Bold.ttf"))
    try:
        if os.path.exists(ttf):
            return pygame.font.Font(ttf, size)
    except Exception:
        pass
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)


def main():
    W, H = 1010, 820
    font_big = load_font(30)
    font = load_font(17)
    font_sm = load_font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("VERDIGRIS DROWNED-KING", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "slumped undersea monarch  ·  sea-bone dominant · coral-antler crown + baroque PEARL · the only teal · round 2",
        True, LABEL_DIM), (360, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 244, 1.75)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero (SS=6)", True, LABEL), (90, 566))
    sheet.blit(font_sm.render("SLUMP: weight collapsed onto one shoulder, head lolled off-axis, soft", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("asymmetric trailing outline (the only organic king). Coral antlers +", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("baroque PEARL = crown tell. 2 FAT weed tendrils, sky between. Teal = accent.", True, LABEL_DIM), (14, 622))

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
    pygame.draw.rect(sheet, (40, 60, 64), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — reef-throne", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("barnacle vertebra beads = tileable shaft;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("coral fork + pearl + weed caps each gap edge", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top↔bottom, on-axis, not top-heavy)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_king(big, 48 * SS, 50 * SS, (32 / FIG_UNITS) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        if night:
            # wide cool pearl-teal rim FIRST, then the ink keyline on top of it,
            # so the luminous halo carries the slump on the dark sky.
            small = night_rim(small, (150, 198, 196, 255), 2)
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()
    chip_night = chip32(night=True)

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip_night, (panel_x + 20 + 27, night_y + 27))
    sheet.blit(font_sm.render("32px on night sky (cool rim-sheen)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blackout silhouette proof beside (slump must read as a shape)
    def chip_black():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_king(big, 48 * SS, 50 * SS, (32 / FIG_UNITS) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        mask = pygame.mask.from_surface(small)
        out = pygame.Surface((96, 96), pygame.SRCALPHA)
        for px, py in mask.outline():
            pass
        # fill the whole mask flat black to test the silhouette read
        sil = mask.to_surface(setcolor=(14, 16, 18, 255), unsetcolor=(0, 0, 0, 0))
        out.blit(sil, (0, 0))
        return out

    px2 = panel_x + 192
    vgrad(sheet, (px2, day_y, 56, 150), (210, 214, 210), (170, 178, 174))
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    blk = chip_black()
    sheet.blit(pygame.transform.smoothscale(blk, (52, 52)), (px2 + 2, day_y + 48))
    sheet.blit(font_sm.render("blackout", True, (60, 64, 64)), (px2 + 2, day_y - 16))

    # 32px pillar gap-cap chip below the blackout
    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 6, night_y - 16))

    # === Koschei-vs-sea-bone comparison swatch (the lock the AD audits) ======
    cmp_y = 440
    sheet.blit(font.render("Bone vs Koschei", True, LABEL), (panel_x + 16, cmp_y - 26))
    KOSCHEI = (190, 192, 158)
    def luma(c):
        return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    for i, (c, name) in enumerate(((KOSCHEI, "Koschei tallow"), (BONE, "sea-bone (this)"))):
        rx = panel_x + 16 + i * 158
        pygame.draw.rect(sheet, INK, (rx - 1, cmp_y - 1, 30, 30))
        pygame.draw.rect(sheet, c, (rx, cmp_y, 28, 28))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 34, cmp_y + 2))
        sheet.blit(font_sm.render("%s  L%d" % (c, int(luma(c))), True, LABEL_DIM),
                   (rx + 34, cmp_y + 16))
    sheet.blit(font_sm.render(
        "+%d%% luma, G ahead of R/B (value+hue step)" % int(100 * (luma(BONE) / luma(KOSCHEI) - 1)),
        True, LABEL_DIM), (panel_x + 16, cmp_y + 32))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (BONE, "sea-bone"), (BONE_D, "bone shade"),
        (TEAL, "verdigris teal"), (TEAL_BR, "bright verdigris"),
        (PEARL, "pearl-cream"), (PEARL_SH, "pearl hot"),
        (BARNACLE, "barnacle crust"), (INK, "ink keyline"),
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
        "ELEVATED pipeline: SS=6 supersample → smoothscale.  STAY: flat saturated fills · hard ink keyline (28,22,30) · "
        "dark-core→fill→top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
