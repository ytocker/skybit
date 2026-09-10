"""
Round-2 concept renderer for the RIB-CAGE HYBRID clown-event bone column.

WHY this column: half built monument, half skeletal anatomy. A CONTINUOUS
thick spine rope runs the shaft; paired curving ribs sweep out to the 58px
edge in repeating clusters; each half is capped at Pip's gap by the locked
Asthi-Dakini SWITCHED+BIG focal (faceted cyan cut-gem third-eye in a gold
ring, white-hot core, warm-ivory skull) staring jaw-into-the-gap.

ROUND-2 silhouette-solidity rebuild (per art-director ITERATE). Round 1
failed the solid-at-58px contract: thin curved fins floated beside a hairline
spine with sky channels on both sides of every rib pair. The material, the
focal, and the continuous-spine concept all passed and are kept. The fix is
purely silhouette mass:

  * Each rib CLUSTER half is now ONE solid lobed bone-BLOCK — a filled
    triangular wedge from the thick spine out to the full half-column edge,
    its OUTER boundary bulging (mid ribs reach furthest) then pinching at the
    inter-cluster waist. The rib SEAMS are carved INTO that block as shallow
    notches (the vertebra-spine trick), never left as open sky. So there is no
    continuous top-to-bottom sky channel anywhere except the focal gap.
  * Rib interior is FILLED toward the spine (>=80% of the half-width across a
    cluster body) — a mass, not a crescent.
  * Spine core is THICK (~7px at 58px) with a darker ink-keyed center so it
    never reads as a cloud edge; vertebra notches stay carved seams, not gaps.
  * The 3/gap/3 read is rebuilt as a genuine bulge-then-pinch silhouette that
    survives downsampling; bare-spine runs beside the focal are tightened to
    ~1 cluster height.

Distinctness from the marrow-skewer now lives in CURVED RIB LOBES vs. flat
horizontal discs — safe once the ribs are honest occluding mass.

House grammar (bone roster): warm-ivory bone, hard 1-2px ink keyline (28,22,30),
dark-core -> flat-fill -> top-left rim-sheen triad, gold thin-accent tracing,
faceted cyan wisdom gem, supersample->smoothscale + alpha-grown 1px silhouette
outline.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math inline, not runtime sprite modules.
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

PIPE_W = 58

_FONT_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "game", "assets", "LiberationSans-Bold.ttf"))


def font(sz):
    if os.path.exists(_FONT_PATH):
        return pygame.font.Font(_FONT_PATH, sz)
    return pygame.font.SysFont("DejaVu Sans", sz, bold=True)


# ── PINNED PALETTE (locked Asthi bone-roster house style) ─────────────────────
BONE      = (212, 202, 186)   # warm aged ivory-bone (dominant light field)
BONE_D    = (158, 148, 130)   # bone shade / mid-core
BONE_DD   = ( 96,  88,  76)   # deepest bone hollow / carved seam
BONE_SH   = (240, 234, 222)   # bone top-left rim-sheen (warm near-white)
CYAN      = ( 86, 214, 226)
CYAN_BR   = (188, 248, 252)
CYAN_D    = ( 40, 132, 150)
GOLD      = (212, 162,  60)   # warm gold thin-accent tracing
GOLD_BR   = (246, 208, 110)
GOLD_D    = (158, 112,  40)
INK       = ( 28,  22,  30)   # hard ink keyline (bone-roster house ink)

BG        = ( 92,  96, 108)
PANEL     = ( 70,  74,  86)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 18,  20,  44)
NIGHT_B   = ( 54,  44,  82)
LABEL     = (238, 240, 246)
LABEL_DIM = (190, 198, 212)


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


def triad_blob(surf, color, pts, sheen_pts=None, ow=2):
    pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.4), sheen_pts)
    pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
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


# ── a FACETED cyan cut-stone GEM — the locked Asthi third-eye focal ───────────
def cyan_gem(surf, c, r, s, focal=False, bg=None, hot=None):
    """A CUT cyan jewel built from FLAT FACET PLANES (a facet rosette): a flat
    angular octagonal TABLE at the crown, ringed by crown facets in stepped cyan
    values meeting at sharp corners. `focal` (the third-eye) alone gets the
    white-hot core + extra glints. Lifted faithfully from the locked Asthi
    SWITCHED+BIG render so the focal matches exactly."""
    cx, cy = int(c[0]), int(c[1])
    show_bg = (not focal) if bg is None else bg
    show_hot = focal if hot is None else hot
    if show_bg:
        pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(1.4 * s)))

    def gpt(ang_deg, rad):
        a = math.radians(ang_deg)
        return (cx + math.cos(a) * rad, cy + math.sin(a) * rad)
    n_crown = 8
    girdle = [gpt(-90 + i * (360 / n_crown), r) for i in range(n_crown)]
    pygame.draw.polygon(surf, CYAN_D, girdle)

    table_r = r * 0.46
    tcx, tcy = cx, cy - int(r * 0.10)
    table = [(tcx + math.cos(math.radians(-90 + i * (360 / n_crown))) * table_r,
              tcy + math.sin(math.radians(-90 + i * (360 / n_crown))) * table_r)
             for i in range(n_crown)]

    for i in range(n_crown):
        g0, g1 = girdle[i], girdle[(i + 1) % n_crown]
        t0, t1 = table[i], table[(i + 1) % n_crown]
        mx = (g0[0] + g1[0]) * 0.5 - cx
        my = (g0[1] + g1[1]) * 0.5 - cy
        facing = -(mx * 0.7 + my * 0.7) / max(1.0, r)
        if facing > 0.35:
            fc = CYAN_BR
        elif facing > -0.15:
            fc = CYAN
        else:
            fc = lerp(CYAN, CYAN_D, 0.6)
        pygame.draw.polygon(surf, fc, [g0, g1, t1, t0])
        pygame.draw.polygon(surf, INK, [g0, g1, t1, t0], max(1, int(0.9 * s)))

    pygame.draw.polygon(surf, lerp(CYAN, CYAN_BR, 0.55), table)
    pygame.draw.polygon(surf, INK, table, max(1, int(0.9 * s)))
    pygame.draw.line(surf, CYAN_BR, table[0], table[n_crown // 2], max(1, int(0.8 * s)))

    def glint(px, py, sz):
        pygame.draw.polygon(surf, (255, 255, 255),
                            [(px, py - sz), (px + sz, py + sz * 0.5),
                             (px - sz, py + sz * 0.5)])

    g = max(1, int(r * 0.16))
    glint(table[6][0], table[6][1], g)
    if show_hot:
        pygame.draw.polygon(surf, CYAN_BR,
                            [(tcx, tcy - int(r * 0.22)), (tcx + int(r * 0.20), tcy),
                             (tcx, tcy + int(r * 0.20)), (tcx - int(r * 0.20), tcy)])
        pygame.draw.circle(surf, (240, 255, 255), (tcx, tcy), max(2, int(r * 0.15)))
        pygame.draw.circle(surf, (255, 255, 255), (tcx - int(r * 0.04), tcy - int(r * 0.04)),
                           max(1, int(r * 0.08)))
        glint(girdle[1][0], girdle[1][1], max(1, int(r * 0.12)))
        glint(table[3][0], table[3][1], max(1, int(r * 0.11)))


# ── the Asthi gem-eye/gold-ring focal skull (capping each half at the gap) ────
def asthi_skull(surf, cx, cy, r, s, facing_down=True):
    """The locked Asthi SWITCHED+BIG head: warm-ivory cranium with a faceted cyan
    third-eye (white-hot core) seated in a GOLD RING at the brow, two deep cyan-lit
    sockets, nasal pit, tooth row. `facing_down`/up orients the jaw so each half's
    cap stares INTO the gap toward Pip. The single brightest pixel of the whole
    column lives in this gem so the eye lands at the gap, never on the shaft."""
    ow1 = max(2, int(2.0 * s))
    ow_thin = max(1, int(1.2 * s))
    flip = 1 if facing_down else -1

    # cranium dome (jaw points toward the gap) — an ink-keyed bone polygon.
    dome = []
    for ang_deg in range(-180, 1, 16):
        a = math.radians(ang_deg)
        dome.append((cx + math.cos(a) * r * 1.06, cy - flip * math.sin(a) * r * 1.12))
    dome.append((cx + r * 0.80, cy + flip * r * 0.40))
    dome.append((cx + r * 0.52, cy + flip * r * 0.86))
    dome.append((cx - r * 0.52, cy + flip * r * 0.86))
    dome.append((cx - r * 0.80, cy + flip * r * 0.40))
    triad_blob(surf, BONE, [(int(x), int(y)) for x, y in dome], ow=ow1)

    # top-left bone sheen wedge (the triad highlight)
    sheen = [(cx - r * 0.66, cy - flip * r * 0.34),
             (cx - r * 0.14, cy - flip * r * 0.82),
             (cx - r * 0.04, cy - flip * r * 0.44),
             (cx - r * 0.52, cy - flip * r * 0.04)]
    pygame.draw.polygon(surf, BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # cranial suture median line (the carved-bone read)
    pygame.draw.line(surf, BONE_DD, (int(cx), int(cy - flip * r * 0.86)),
                     (int(cx), int(cy - flip * r * 0.18)), ow_thin)

    # deep ink sockets with carved bone rims, dim cyan-lit pupils
    socket_r = r * 0.30
    for sgn in (-1, 1):
        ex = int(cx + sgn * r * 0.42)
        ey = int(cy + flip * r * 0.14)
        pygame.draw.circle(surf, BONE_D, (ex, ey), int(socket_r + max(1, 1.4 * s)))
        pygame.draw.circle(surf, INK, (ex, ey), int(socket_r))
        pygame.draw.circle(surf, CYAN_D, (ex, ey), int(socket_r * 0.46))

    # nasal pit
    pygame.draw.polygon(surf, INK, [
        (int(cx), int(cy + flip * r * 0.40)),
        (int(cx - r * 0.13), int(cy + flip * r * 0.66)),
        (int(cx + r * 0.13), int(cy + flip * r * 0.66))])

    # tooth row — short jaw bar with slits, facing the gap
    ty = cy + flip * r * 0.74
    pygame.draw.line(surf, INK, (int(cx - r * 0.36), int(ty)),
                     (int(cx + r * 0.36), int(ty)), max(2, int(1.6 * s)))
    for j in range(5):
        tx = int(cx - r * 0.30 + j * (r * 0.60 / 4))
        pygame.draw.line(surf, INK, (tx, int(ty - flip * r * 0.02)),
                         (tx, int(ty + flip * r * 0.16)), max(1, int(1.2 * s)))

    # ── the GOLD RING bezel + faceted cyan THIRD-EYE at the brow (the focal) ──
    bx, by = int(cx), int(cy - flip * r * 0.40)
    gem_r = int(r * 0.42)
    ring_r = gem_r + max(2, int(3.2 * s))
    pygame.draw.circle(surf, GOLD_D, (bx, by), ring_r + max(1, int(1.0 * s)))
    pygame.draw.circle(surf, GOLD, (bx, by), ring_r)
    pygame.draw.circle(surf, GOLD_BR, (bx - int(ring_r * 0.30), by - int(ring_r * 0.34)),
                       max(1, int(ring_r * 0.22)))
    pygame.draw.circle(surf, INK, (bx, by), gem_r + max(1, int(1.0 * s)))
    cyan_gem(surf, (bx, by), gem_r, s, focal=True, bg=False, hot=True)


# ── the continuous spine rope (NOT beaded), now THICK-cored ───────────────────
def spine_rope(surf, x, y0, y1, th, s):
    """A CONTINUOUS thick bone spine rope down the shaft — a solid ink-keyed bone
    column, NOT a bead chain. ROUND 2: core widened to ~7px at 58px with a darker
    ink-keyed center band so it never reads as a cloud edge. Vertebra seams are
    SHALLOW notches carved into the one rope, not gaps between beads."""
    ow = max(2, int(2.0 * s))
    half = th // 2
    pygame.draw.rect(surf, INK, (int(x - half - ow), int(y0), int(th + 2 * ow), int(y1 - y0)))
    pygame.draw.rect(surf, BONE, (int(x - half), int(y0), int(th), int(y1 - y0)))
    # round the shaft: dark hollow on the right flank, a bright bone crown down
    # the centre, sheen rail on the left. The exposed centre sliver between the
    # two rib blocks must read as a lit ROUNDED bone shaft, never a black wire.
    pygame.draw.rect(surf, BONE_D, (int(x + half * 0.18), int(y0), int(half * 0.62), int(y1 - y0)))
    pygame.draw.rect(surf, BONE_DD, (int(x + half * 0.55), int(y0), int(half * 0.45), int(y1 - y0)))
    pygame.draw.rect(surf, BONE_SH, (int(x - half + ow), int(y0), max(1, int(half * 0.42)), int(y1 - y0)))
    # a bright bone crown right down the middle so the visible sliver stays bone
    pygame.draw.rect(surf, lerp(BONE, BONE_SH, 0.5),
                     (int(x - half * 0.22), int(y0), max(2, int(half * 0.40)), int(y1 - y0)))
    pygame.draw.line(surf, INK, (int(x - half), int(y0)), (int(x - half), int(y1)), ow)
    pygame.draw.line(surf, INK, (int(x + half), int(y0)), (int(x + half), int(y1)), ow)
    # shallow vertebra seam notches carved across the rope (NOT bead gaps)
    seam = int(13 * s)
    yy = int(y0 + seam * 0.5)
    while yy < y1:
        pygame.draw.line(surf, BONE_DD, (int(x - half + ow), yy), (int(x + half - ow), yy),
                         max(1, int(1.4 * s)))
        pygame.draw.line(surf, BONE_SH, (int(x - half + ow), yy + max(1, int(1.4 * s))),
                         (int(x + half - ow), yy + max(1, int(1.4 * s))), max(1, int(1.0 * s)))
        yy += seam


# ── one rib CLUSTER half as a single solid lobed bone-block ───────────────────
def rib_cluster_block(surf, spine_x, sgn, y_top, reaches, pitch, droop, th, s,
                      spine_half):
    """Draw ONE half (left or right) of a rib cluster as a SINGLE SOLID lobed
    bone-block, then carve the rib seams INTO it as incised lines.

    WHY this construction (round-2 ship-blocker fix): the round-1 ribs (and the
    first round-2 attempt) drew rib arcs that DROOPED away from the spine, which
    left open sky biting in toward the spine between every rib root — a fly-through
    void. The fix is to define the block by a single closed boundary whose INNER
    edge runs FLUSH down the spine with NO concave bite, and whose OUTER edge is a
    lobed curve `reach(y)` that BULGES at each rib centre and only mildly pinches
    between ribs — and never pinches inboard of the spine. So every horizontal
    slice from spine to outer edge is FILLED bone: a 1px vertical scan hits no sky.
    The rib lobes are then read purely from (a) the bulge-then-pinch of the outer
    silhouette and (b) carved dark seam arcs incised on top — curved relief, not
    open gaps. This keeps it distinct from the skewer's flat discs while occluding
    as aggressively as the skewer's near-full-width discs.

    `reaches` is the per-rib outward reach (px, already scaled); `pitch` is the
    vertical spacing between rib centres; `droop` only curves the seam/lobe arcs;
    `spine_half` is the spine half-width so the inner edge sits flush to it."""
    ow = max(1, int(1.6 * s))
    n = len(reaches)
    rib_ys = [y_top + i * pitch for i in range(n)]
    y_lo = rib_ys[0] - pitch * 0.60
    y_hi = rib_ys[-1] + pitch * 0.62

    def reach_at(y):
        """Outer-edge reach (signed-magnitude, px) at vertical position y: the
        widest of per-rib lobes centred on each rib. Each lobe is ASYMMETRIC —
        fatter on its lower flank — so a lobe reads as a rib that swells then
        curves down, not a symmetric pill. An inter-rib floor keeps dips above the
        spine so the block stays one continuous mass with no waist to the spine."""
        best = 0.0
        for i in range(n):
            dy = (y - rib_ys[i])
            # skew the falloff: tighter above the rib centre, looser below, so the
            # lobe's belly sits low like an anatomical rib curving downward.
            span = pitch * (0.62 if dy < 0 else 0.95)
            d = dy / span
            lobe = reaches[i] * math.exp(-d * d * 0.95)
            best = max(best, lobe)
        # floor keeps the inter-rib dips wide enough to stay solid + occluding
        floor = max(reaches) * 0.62
        return max(best, floor)

    # ── boundary: down the OUTER lobed edge (top->bottom), then back up the spine.
    steps = 30
    outer = []
    for k in range(steps + 1):
        y = y_lo + (y_hi - y_lo) * (k / steps)
        # a gentle overall droop bows the whole block outward-down (anatomical)
        bow = droop * ((y - y_lo) / max(1.0, (y_hi - y_lo)))
        x = spine_x + sgn * (spine_half * 0.5 + reach_at(y))
        outer.append((x, y + bow * 0.25))
    inner = [(spine_x + sgn * spine_half * 0.35, y_hi),
             (spine_x + sgn * spine_half * 0.35, y_lo)]
    boundary = outer + inner
    ipoly = [(int(x), int(y)) for x, y in boundary]

    # solid filled block: ink key, bone fill
    pygame.draw.polygon(surf, INK, ipoly)
    pygame.draw.polygon(surf, BONE, ipoly)

    # top-left rim sheen: a thin band hugging the OUTER edge near the top lobe,
    # and dark-core shade hugging the bottom lobe (the triad on the block as one).
    sheen_band = []
    for k in range(steps + 1):
        x, y = outer[k]
        sheen_band.append((x - sgn * th * 0.30, y))
    sheen_poly = outer[: steps // 2 + 1] + sheen_band[: steps // 2 + 1][::-1]
    if len(sheen_poly) >= 3:
        pygame.draw.polygon(surf, BONE_SH, [(int(x), int(y)) for x, y in sheen_poly])
    shade_band = []
    for k in range(steps + 1):
        x, y = outer[k]
        shade_band.append((x - sgn * th * 0.34, y))
    shade_poly = outer[steps // 2:] + shade_band[steps // 2:][::-1]
    if len(shade_poly) >= 3:
        pygame.draw.polygon(surf, BONE_D, [(int(x), int(y)) for x, y in shade_poly])

    # ── carve the rib SEAMS as incised dark arcs (the curved-lobe read) ──
    # one seam between adjacent ribs, arcing from the spine out to the waist dip
    # of the outer edge so the eye reads three stacked curved ribs in the mass.
    for i in range(n - 1):
        ymid = (rib_ys[i] + rib_ys[i + 1]) * 0.5
        seam = []
        sm_steps = 12
        for k in range(sm_steps + 1):
            t = k / sm_steps
            x = spine_x + sgn * (spine_half * 0.5 + reach_at(ymid) * (t ** 0.85))
            # the seam bows down toward the rib below (curved relief)
            y = ymid + droop * 0.16 * (t * t) * (1 if droop >= 0 else 1)
            seam.append((x, y))
        ipts = [(int(x), int(y)) for x, y in seam]
        if len(ipts) >= 2:
            pygame.draw.lines(surf, BONE_DD, False, ipts, max(2, int(2.2 * s)))
            lip = [(x, y - max(1, 1.8 * s)) for (x, y) in seam]
            pygame.draw.lines(surf, BONE_SH, False,
                              [(int(x), int(y)) for x, y in lip], max(1, int(1.0 * s)))

    # gold thin cap-trace tracing the outer lobed silhouette (monument accent)
    pygame.draw.lines(surf, GOLD, False,
                      [(int(x), int(y)) for x, y in outer], max(1, int(1.4 * s)))

    # re-stroke the silhouette keyline last so the block edge stays crisp
    pygame.draw.polygon(surf, INK, ipoly, ow)


# ── one half of the rib-cage column (top OR bottom) ───────────────────────────
def draw_half(surf, cx, cap_y, shaft_y0, shaft_y1, s, facing_down, w_units):
    """Draw one half: a continuous thick spine rope + repeating rib-cluster
    BLOCKS + the Asthi focal skull at `cap_y` (the gap edge).

    ROUND 2: each cluster is a single solid lobed block (see rib_cluster_block);
    the inter-cluster waist pinches the silhouette to ~spine width so the column
    reads as bulge-then-pinch repeating BONE MASS, distinct from the skewer's flat
    discs. The first cluster starts close to the focal so there is never more than
    ~one cluster height of bare spine beside the lane."""
    edge = (w_units * 0.5 - 1) * s          # full half-column the rib tips reach
    spine_th = int(8.0 * s)                 # thick spine core (~7-8px at 58px)
    spine_half = spine_th * 0.5
    rib_th = int(9.0 * s)                   # incised seam relief thickness

    # spine first (behind the rib blocks)
    spine_rope(surf, cx, shaft_y0, shaft_y1, spine_th, s)

    sign = 1 if facing_down else -1          # +1 = shaft runs below the cap
    pitch = int(12 * s)                      # vertical spacing of ribs inside a block
    max_reach = edge - spine_half * 0.5      # longest rib hits the full half-column

    # Per the art-director's directive-4 alternative (allowed now that the body is
    # solid): a denser, slightly-irregular rib-STACK rather than a fragile 3/gap/3
    # rhythm that averages to even fins at 1x. Each cluster is 3 ribs whose reach
    # tapers head-to-tail (long-mid-short) so the cluster bulges then PINCHES into
    # a short pinch-rib before the next cluster — a bulge-then-pinch silhouette
    # that survives downsampling, with the pinch rib keeping the body continuous.
    cluster_reaches = (1.0, 0.92, 0.78)      # long → short within a cluster
    pinch_reach = 0.60                        # the short rib that marks the waist
    droop = sign * int(8 * s)                 # gentle anatomical bow of each block

    # build a single tall ordered list of rib reaches (clusters + pinch ribs),
    # with mild per-rib jitter so the stack reads organic, not machined.
    import random
    jr = random.Random(int(abs(cx) + (0 if sign > 0 else 999)))

    lead = int(6 * s)                         # first rib hugs the focal cap

    def stamp(yy_top, reaches):
        rib_cluster_block(surf, cx, +1, yy_top, reaches, pitch, droop, rib_th, s, spine_half)
        rib_cluster_block(surf, cx, -1, yy_top, reaches, pitch, droop, rib_th, s, spine_half)

    # one "segment" = a 3-rib cluster block + a pinch rib; both are solid lobes,
    # so the whole run is continuous mass with a periodic narrowing.
    seg_h = (len(cluster_reaches)) * pitch
    if sign > 0:
        yy = shaft_y0 + lead
        far = shaft_y1
    else:
        yy = shaft_y1 - lead - seg_h
        far = shaft_y0
    while (sign > 0 and yy + seg_h * 0.4 < far) or (sign < 0 and yy + seg_h * 0.6 > far):
        jit = 1.0 + jr.uniform(-0.05, 0.05)
        reaches = tuple(r * max_reach * jit for r in cluster_reaches) + \
                  (pinch_reach * max_reach,)
        stamp(yy, reaches)
        yy += sign * seg_h

    # the focal skull caps the half at the gap edge (drawn last → on top)
    skull_r = int(21 * s)
    asthi_skull(surf, cx, cap_y, skull_r, s, facing_down=facing_down)


# ── render one full column (top half + gap + bottom half) at supersample ──────
def render_column(col_h, gap_top, gap_bot, s):
    margin = 14
    W = (PIPE_W + 2 * margin) * s
    H = col_h * s
    big = pygame.Surface((int(W), int(H)), pygame.SRCALPHA)
    cx = int(W // 2)

    top_cap_y = gap_top * s - int(4 * s)
    draw_half(big, cx, top_cap_y, 0, top_cap_y - int(16 * s), s,
              facing_down=True, w_units=PIPE_W)

    bot_cap_y = gap_bot * s + int(4 * s)
    draw_half(big, cx, bot_cap_y, bot_cap_y + int(16 * s), H, s,
              facing_down=False, w_units=PIPE_W)

    return big, margin, top_cap_y, bot_cap_y


def downscale(big, out_w):
    src_w = big.get_width()
    scale = out_w / src_w
    out = pygame.transform.smoothscale(
        big, (int(out_w), int(big.get_height() * scale)))
    out = grow_outline(out, INK, 1)
    return out


def downscale_crop(big, out_w, y0_frac, y1_frac):
    out = downscale(big, out_w)
    h = out.get_height()
    y0, y1 = int(h * y0_frac), int(h * y1_frac)
    return out.subsurface((0, y0, out.get_width(), y1 - y0)).copy()


# ── busy sky backdrops (day + night) ──────────────────────────────────────────
def day_sky(w, h):
    sky = pygame.Surface((w, h))
    for yy in range(h):
        sky.fill(lerp(DAY_SKY_T, DAY_SKY_B, yy / max(1, h)), (0, yy, w, 1))
    import random
    rng = random.Random(7)
    for _ in range(9):
        cxp = rng.randint(0, w)
        cyp = rng.randint(int(h * 0.08), int(h * 0.7))
        for k in range(5):
            r = rng.randint(10, 24)
            c = lerp(DAY_SKY_T, (255, 255, 255), 0.6)
            puff = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(puff, (*c, 150), (r, r), r)
            sky.blit(puff, (cxp + k * 12 - 24, cyp + (k % 2) * 6))
    ridge = lerp(DAY_SKY_B, (120, 170, 110), 0.5)
    pts = [(0, h)]
    for i in range(0, w + 20, 20):
        pts.append((i, int(h * 0.82 + math.sin(i * 0.05) * 10)))
    pts.append((w, h))
    pygame.draw.polygon(sky, ridge, pts)
    return sky


def night_sky(w, h):
    """Night biome backdrop — cyan-on-dark changes how the gem + sockets punch."""
    sky = pygame.Surface((w, h))
    for yy in range(h):
        sky.fill(lerp(NIGHT_T, NIGHT_B, yy / max(1, h)), (0, yy, w, 1))
    import random
    rng = random.Random(11)
    for _ in range(60):
        sx = rng.randint(0, w)
        sy = rng.randint(0, int(h * 0.85))
        b = rng.randint(120, 230)
        sky.set_at((sx, sy), (b, b, lerp((b, b, b), (200, 220, 255), 0.5)[2]))
    # a couple of dim cloud bands so the silhouette still gets a busy test
    for _ in range(4):
        cxp = rng.randint(0, w)
        cyp = rng.randint(int(h * 0.2), int(h * 0.7))
        for k in range(5):
            r = rng.randint(12, 26)
            puff = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(puff, (90, 96, 130, 90), (r, r), r)
            sky.blit(puff, (cxp + k * 12 - 24, cyp + (k % 2) * 6))
    ridge = lerp(NIGHT_B, (40, 40, 64), 0.6)
    pts = [(0, h)]
    for i in range(0, w + 20, 20):
        pts.append((i, int(h * 0.82 + math.sin(i * 0.05) * 10)))
    pts.append((w, h))
    pygame.draw.polygon(sky, ridge, pts)
    return sky


def vscan_sky_count(col_surf):
    """ACCEPTANCE TEST: a 1px-wide vertical scan down the column centre body,
    counting rows whose centre pixel is transparent (sky) within the body band
    between the two focal caps. Returns the count — target 0 sky rows."""
    w, h = col_surf.get_size()
    xc = w // 2
    sky_rows = 0
    for yy in range(h):
        a = col_surf.get_at((xc, yy))[3]
        if a < 40:
            sky_rows += 1
    return sky_rows


# ── assemble the review sheet ─────────────────────────────────────────────────
def build_sheet():
    SS = 8
    COL_H = 600
    GAP_TOP = 270
    GAP_BOT = 270 + 150

    big, _, top_cap_y, bot_cap_y = render_column(COL_H, GAP_TOP, GAP_BOT, SS)
    big_h = big.get_height()

    gap_lo = max(0.0, (top_cap_y - 150 * SS) / big_h)
    gap_hi = min(1.0, (bot_cap_y + 150 * SS) / big_h)

    hero = downscale_crop(big, (PIPE_W + 28) * 5, gap_lo, gap_hi)
    mid = downscale_crop(big, (PIPE_W + 28) * 3, gap_lo, gap_hi)
    gameplay = downscale(big, PIPE_W + 28)
    gp_full_w = gameplay.get_width()
    crop_x = (gp_full_w - PIPE_W) // 2
    gp_crop = gameplay.subsurface((crop_x, 0, PIPE_W, gameplay.get_height())).copy()

    # ── layout ──
    SHEET_W, SHEET_H = 1100, 800
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill(BG)

    title = font(30).render("RIB-CAGE HYBRID — clown-event bone column (round 2)",
                            True, LABEL)
    sheet.blit(title, (28, 18))
    sub = font(15).render(
        "SOLID lobed rib-cluster BLOCKS (carved seams, no sky channels) on a THICK "
        "continuous spine · 1x day+night are the acceptance test · locked Asthi gem-eye focal",
        True, LABEL_DIM)
    sheet.blit(sub, (28, 56))

    def panel(x, y, w, h, label):
        pygame.draw.rect(sheet, PANEL, (x, y, w, h), border_radius=8)
        pygame.draw.rect(sheet, lerp(PANEL, INK, 0.4), (x, y, w, h), 2, border_radius=8)
        lab = font(15).render(label, True, LABEL)
        sheet.blit(lab, (x + 12, y + 8))

    PANEL_Y, PANEL_H = 92, 690

    def fit_v(clip, max_h):
        if clip.get_height() > max_h:
            sc = max_h / clip.get_height()
            return pygame.transform.smoothscale(
                clip, (int(clip.get_width() * sc), max_h))
        return clip

    # 1) HERO (left) — gap region, 5x
    hx, hw = 28, 320
    panel(hx, PANEL_Y, hw, PANEL_H, "HERO 5x — gap + clusters + both focal caps")
    hclip = fit_v(hero, PANEL_H - 50)
    sheet.blit(hclip, hclip.get_rect(center=(hx + hw // 2, PANEL_Y + 36 + (PANEL_H - 50) // 2)))

    # 2) 3x detail (center) — shows the carved seams + bulge-then-pinch
    mx, mw = 360, 190
    panel(mx, PANEL_Y, mw, PANEL_H, "3x — carved seams")
    mclip = fit_v(mid, PANEL_H - 50)
    sheet.blit(mclip, mclip.get_rect(center=(mx + mw // 2, PANEL_Y + 36 + (PANEL_H - 50) // 2)))

    # 3) 1x DAY over busy sky — THE acceptance test
    def sky_panel(gx, gw, label, sky):
        pygame.draw.rect(sheet, PANEL, (gx, PANEL_Y, gw, PANEL_H), border_radius=8)
        pygame.draw.rect(sheet, lerp(PANEL, INK, 0.4), (gx, PANEL_Y, gw, PANEL_H), 2, border_radius=8)
        sheet.blit(font(15).render(label, True, LABEL), (gx + 12, PANEL_Y + 8))
        sky_w, sky_h = gw - 24, PANEL_H - 64
        sky_x, sky_y = gx + 12, PANEL_Y + 40
        sheet.blit(sky, (sky_x, sky_y))
        gpc = fit_v(gp_crop, sky_h)
        sheet.blit(gpc, gpc.get_rect(center=(sky_x + sky_w // 2, sky_y + sky_h // 2)))
        cap = font(13).render("← 58px →", True, LABEL_DIM)
        sheet.blit(cap, (gx + gw // 2 - cap.get_width() // 2, PANEL_Y + PANEL_H - 22))

    gx, gw = 560, 170
    sky_w, sky_h = gw - 24, PANEL_H - 64
    sky_panel(gx, gw, "1x · busy DAY sky", day_sky(sky_w, sky_h))

    nx, nw = 738, 170
    sky_panel(nx, nw, "1x · busy NIGHT sky", night_sky(sky_w, sky_h))

    # 4) far-right: focal close-up + acceptance numbers
    fx, fw = 916, 156
    panel(fx, PANEL_Y, fw, PANEL_H, "focal + test")
    fbig = pygame.Surface((240, 240), pygame.SRCALPHA)
    asthi_skull(fbig, 120, 110, 76, 3.4, facing_down=True)
    fsm = grow_outline(pygame.transform.smoothscale(fbig, (132, 132)), INK, 1)
    sheet.blit(fsm, (fx + (fw - 132) // 2, PANEL_Y + 44))

    # vertical-scan acceptance test on the BODY (between the caps), reported here.
    body_lo = int(gp_crop.get_height() * ((top_cap_y) / big_h + 0.04))
    body_hi = int(gp_crop.get_height() * ((bot_cap_y) / big_h - 0.04))
    # top body run
    top_body = gp_crop.subsurface((0, 0, PIPE_W, max(1, body_lo))).copy()
    bot_body = gp_crop.subsurface((0, body_hi, PIPE_W,
                                   max(1, gp_crop.get_height() - body_hi))).copy()
    sky_top = vscan_sky_count(top_body)
    sky_bot = vscan_sky_count(bot_body)

    note = [
        "Asthi focal:",
        "cyan third-eye,",
        "white-hot core,",
        "GOLD RING —",
        "brightest point.",
        "",
        "Ribs = SOLID",
        "lobed BLOCKS;",
        "seams carved,",
        "not open sky.",
        "",
        "Thick spine",
        "core (~7px).",
        "",
        "1px vscan, col",
        "body (sky rows):",
        f"  top  {sky_top}",
        f"  bot  {sky_bot}",
        "  target 0",
    ]
    ny = PANEL_Y + 188
    for ln in note:
        sheet.blit(font(14).render(ln, True, LABEL_DIM), (fx + 12, ny))
        ny += 19

    return sheet, (sky_top, sky_bot)


if __name__ == "__main__":
    sheet, scan = build_sheet()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out, "vscan(top,bot sky rows)=", scan)
