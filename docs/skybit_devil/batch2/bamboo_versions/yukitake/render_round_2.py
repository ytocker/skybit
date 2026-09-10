"""
Round-2 concept renderer for YUKITAKE — the snow-bowed bamboo spirit
(Bamboo-versions set, concept #4). Headless Pygame; ELEVATED pipeline
(supersample SS=6 → smoothscale). Keeps the shipped house grammar: flat fills,
hard 1-2px ink keyline, dark-core → flat-fill → top-left rim-sheen triad, 1px
alpha-grown outline, chibi proportions, scary-CUTE pushed EPIC; procedural-only.

WHY this is the BOWED-SNOW-STALK of the set: the roster has no winter boss and
no non-vertical posture. Yukitake is the ONLY bowed one — but the bow is a TRAP
for the pillar repeat, so the locked AD pin is structural: the SHAFT is drawn
DEAD STRAIGHT and the entire bow lives in the snow-loaf CAP. (KEPT from r1 — AD
said the structural pin is nailed; don't touch.)

WHY round 2 flips the palette thesis (the binding gate): in round 1 the culm
shaft read as a solid GREEN column with white node rings — so the prop read
GREEN-first, not WINTER-first. Round 2 SNOW-SLEEVES the culm: the shaft fill is
now SNOW-WHITE base with blue-shadow as the form shade — it reads white/pale-blue
like the cap. Frost-green survives ONLY as a thin COLD SLIVER: a hairline at the
node-groove and at the very edge of the side leaf-shoots — a 1px cold seam
peeking from under snow (≈2-3 green pixels total at 32px). The dark-core node
GROOVE now does the silhouette-internal work the green rings did, so the white
culm doesn't melt into one blob on a bright noon sky. The frost-green is also
cooled OFF mint toward a desaturated blue-green so it can't read as Kitsune mint.
The snow-blue glow (round 1 had NONE) returns as FLAT STEPPED concentric rings
hugging the cap/face — the signature accent and the foil to Kaguya's moon-gold.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the triad/outline
helpers cloned from the lineage template.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief, section 4 — yukitake) ──────────────────────
# Snow-white/blue is the DOMINANT mass — INCLUDING the culm shaft now. Green is a
# THIN cold sliver only (node-groove hairline + leaf-shoot edge). The glow is
# snow-blue, held clear of Yurei cyan and Kitsune mint.
SNOW      = (232, 238, 244)   # snow-white base (the dominant fill — cap AND culm)
SNOW_SH   = (150, 176, 200)   # blue-shadow snow shade (the culm/cap form shade)
SNOW_DD   = (108, 138, 170)   # deepest blue snow hollow (under-loaf, drip roots)
SHEEN     = (248, 252, 255)   # hottest snow sheen / highlight
ICE       = (198, 232, 242)   # icicle-cyan (the drip bodies)
GLOW      = (170, 212, 236)   # snow-blue glow (the SOLE glow)
GLOW_HOT  = (214, 238, 250)   # hottest snow-blue glow core
# frost-green cooled OFF mint (r1 (120,178,150) read jade/mint at 32px) — pulled
# toward a desaturated cold blue-green so it can't collide with Kitsune mint.
CULM      = (140, 180, 168)   # frost-green accent (the ONLY green; now a SLIVER)
CULM_D    = ( 80, 124, 116)   # deep cold blue-green (node-groove sliver)
CHEEK     = (224, 156, 168)   # rosy cold cheek (a tiny warm life-spark)
INK       = ( 28,  34,  40)   # hard ink keyline (cooled toward the brief's note)
GROOVE    = ( 28,  34,  40)   # dark-core node groove (does the body-internal work)

BG        = ( 74,  88, 104)   # neutral cool-slate review backdrop
PANEL     = ( 58,  72,  88)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NOON_T    = (150, 210, 244)   # bright NOON sky (the worst-case bright card)
NOON_B    = (224, 244, 252)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 244, 250)
LABEL_DIM = (192, 204, 216)


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
        pygame.draw.polygon(surf, lerp(color, SNOW_DD, 0.55), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, SHEEN, 0.7), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True,
                 core_col=None, sheen_col=None):
    """Round equivalent of triad_blob — dark core bottom-right, sheen top-left."""
    core_col = core_col or lerp(color, SNOW_DD, 0.5)
    sheen_col = sheen_col or lerp(color, SHEEN, 0.7)
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, core_col,
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, sheen_col,
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


# ── FLAT STEPPED snow-blue glow rings (the SIGNATURE accent — round 1 lacked it)
def stepped_glow(surf, cx, cy, rx, ry, s, rings=3):
    """Concentric FLAT-STEPPED snow-blue rings hugging a mass — NO soft halo, NO
    gradient (procedural-only house rule). WHY this is load-bearing: it is the
    foil to Kaguya's moon-GOLD halo and what keeps Yukitake distinct from Kaguya
    at 32px now that both are pale props — and it is held clear of Yurei cyan /
    Kitsune mint. Each ring is a hard-edged ellipse outline of a single flat
    snow-blue value, stepping out and cooling as it goes."""
    cols = [GLOW_HOT, GLOW, lerp(GLOW, SNOW_DD, 0.35)]
    for k in range(rings, 0, -1):
        col = cols[min(k - 1, len(cols) - 1)]
        ex = int(rx + k * 7 * s)
        ey = int(ry + k * 7 * s)
        rect = (cx - ex, cy - ey, ex * 2, ey * 2)
        pygame.draw.ellipse(surf, col, rect, max(2, int(2.2 * s)))


# ── a single ICICLE drip (the cold tell that fringes the snow-loaf) ──────────
def icicle(surf, root, length, width, s):
    """One hanging icicle TOOTH: a fat tapered cyan spike rooted at `root`,
    narrowing to a sharp point straight DOWN. WHY fat & 1px-keylined: a thread-
    thin drip dissolves at 32px — round 1's 1px spikes vanished. Round 2 drops to
    fewer, CHUNKIER teeth (cyan body, snow-blue dark side, white sheen rail, hard
    1px ink keyline) so the frill survives the downscale as a readable winter
    tell."""
    rx, ry = root
    hw = width * 0.5
    tip = (rx, ry + length)
    spike = [
        (rx - hw, ry),
        (rx + hw, ry),
        (rx + hw * 0.22, ry + length * 0.70),
        tip,
        (rx - hw * 0.22, ry + length * 0.70),
    ]
    pygame.draw.polygon(surf, INK, spike)
    pygame.draw.polygon(surf, ICE, spike)
    # dark blue side (right) for volume
    pygame.draw.polygon(surf, SNOW_DD, [
        (rx + hw * 0.16, ry),
        (rx + hw, ry),
        (rx + hw * 0.22, ry + length * 0.70),
        tip,
    ])
    # white sheen rail down the left
    pygame.draw.line(surf, SHEEN, (rx - hw * 0.42, ry + length * 0.10),
                     (rx - hw * 0.06, ry + length * 0.58), max(1, int(width * 0.26)))
    pygame.draw.polygon(surf, INK, spike, max(1, int(1.2 * s)))


# ── a lopsided heavy SNOW-LOAF (the cap — the entire bow lives HERE) ─────────
def snow_loaf(surf, cx, cy, w, h, s, lean, drip_n=4, lit=True, face=True):
    """The heavy snow-loaf cap. WHY this is where the bow lives: the AD pin is
    that the SHAFT stays dead straight (KEPT — AD said nailed), so ALL the bowed
    read is carried by this cap — a fat snow pillow that BULGES and SAGS to one
    side (`lean` > 0 pushes the mass right/down) as if the weight is dragging the
    whole spirit over. Rounded stepped ridges of snow on top, a chunky icicle
    fringe below, a chubby spirit-face nestled in the bend.

    Round 2: the snow-blue glow rings hug this cap (round 1 had none), and the
    face is nudged toward the HEAVY (lean) side so weight + gaze agree ("the
    weight makes it bow and watch you")."""
    lx = int(lean * w * 0.32)                  # how far the mass sags sideways

    # === FLAT STEPPED snow-blue glow hugging the loaf (drawn FIRST, behind) ====
    if lit:
        stepped_glow(surf, cx + lx + int(w * 0.04), cy - int(h * 0.06),
                     int(w * 0.54), int(h * 0.52), s, rings=3)

    # === the snow pillow — a fat asymmetric dome sagging toward `lean` =========
    loaf = [
        (cx - int(w * 0.52), cy + int(h * 0.10)),          # left underbelly
        (cx - int(w * 0.50), cy - int(h * 0.30)),
        (cx - int(w * 0.28), cy - int(h * 0.54)),
        (cx + lx - int(w * 0.02), cy - int(h * 0.62)),     # crown pulled toward lean
        (cx + lx + int(w * 0.30), cy - int(h * 0.50)),
        (cx + lx + int(w * 0.54), cy - int(h * 0.18)),     # heavy sagging shoulder
        (cx + lx + int(w * 0.58), cy + int(h * 0.16)),     # the mass droops lowest here
        (cx + int(w * 0.30), cy + int(h * 0.24)),
        (cx - int(w * 0.12), cy + int(h * 0.20)),
    ]
    triad_blob(surf, SNOW, loaf,
               core_pts=[(cx + lx + int(w * 0.06), cy + int(h * 0.02)),
                         (cx + lx + int(w * 0.52), cy - int(h * 0.12)),
                         (cx + lx + int(w * 0.50), cy + int(h * 0.14)),
                         (cx + int(w * 0.18), cy + int(h * 0.20))],
               sheen_pts=[(cx - int(w * 0.46), cy - int(h * 0.26)),
                          (cx - int(w * 0.20), cy - int(h * 0.50)),
                          (cx - int(w * 0.02), cy - int(h * 0.46)),
                          (cx - int(w * 0.30), cy - int(h * 0.18))],
               ow=max(1, int(1.8 * s)))

    # === stepped snow RIDGES on the crown (flat stepped, never a gradient) =====
    for k, (yo, wf, col) in enumerate(((0.42, 0.78, SHEEN), (0.20, 0.52, SNOW))):
        ridge = [
            (cx + lx - int(w * 0.30 * wf), cy - int(h * yo)),
            (cx + lx - int(w * 0.10 * wf), cy - int(h * (yo + 0.18))),
            (cx + lx + int(w * 0.16 * wf), cy - int(h * (yo + 0.16))),
            (cx + lx + int(w * 0.34 * wf), cy - int(h * yo)),
            (cx + lx + int(w * 0.12 * wf), cy - int(h * (yo - 0.10))),
            (cx + lx - int(w * 0.12 * wf), cy - int(h * (yo - 0.10))),
        ]
        pygame.draw.polygon(surf, col, ridge)
        pygame.draw.polygon(surf, lerp(SNOW, SNOW_SH, 0.5), ridge, max(1, int(1.0 * s)))

    # === CHUNKY ICICLE fringe hanging off the heavy (sagging) underbelly =======
    # Round 2: fewer (3-4), fatter TEETH so they survive the downscale; clustered
    # toward the lean side where the snow is heaviest.
    base_y = cy + int(h * 0.14)
    span_l = cx - int(w * 0.30)
    span_r = cx + lx + int(w * 0.50)
    for i in range(drip_n):
        t = i / max(1, drip_n - 1)
        dx = int(span_l + (span_r - span_l) * t)
        # longer, fatter teeth on the heavy (right/lean) side
        dl = (12 + 18 * t) * s + (5 * s if lean > 0 else 0)
        dw = (9.0 - 2.5 * abs(t - 0.5)) * s
        dy = base_y + int((0.06 + 0.10 * t) * h)
        icicle(surf, (dx, dy), dl, dw, s)

    # === the chubby spirit-FACE nestled in the bend (closed gentle eyes) =======
    # Round 2: nudged toward the HEAVY (lean) side so the bow narrative reads —
    # weight and gaze on the same side. Features themselves UNCHANGED (AD said
    # keep the closed gentle eyes + rosy cold cheeks exactly).
    if face:
        fx = cx + int(lx * 0.95) + int(w * 0.10)     # was 0.55/0.06 — pushed to the heavy side
        fy = cy + int(h * 0.05)
        fr = int(w * 0.30)
        # snow-rounded face mass (slightly bluer than the loaf so it separates)
        triad_circle(surf, lerp(SNOW, ICE, 0.35), (fx, fy), fr,
                     ow=max(1, int(1.6 * s)), core=True, sheen=True)
        # closed gentle eyes — two downward arcs (peaceful, sleeping-in-the-cold)
        for sg in (-1, 1):
            ex = fx + sg * int(fr * 0.42)
            ey = fy - int(fr * 0.06)
            pygame.draw.arc(surf, INK,
                            (ex - int(fr * 0.26), ey - int(fr * 0.10),
                             int(fr * 0.52), int(fr * 0.34)),
                            math.radians(200), math.radians(340),
                            max(2, int(2.4 * s)))
            # tiny lash tick at the outer corner → reads as a closed eye, alive
            pygame.draw.line(surf, INK,
                             (ex + sg * int(fr * 0.24), ey + int(fr * 0.02)),
                             (ex + sg * int(fr * 0.34), ey + int(fr * 0.08)),
                             max(1, int(1.6 * s)))
        # rosy cold cheeks (the one tiny warm spark — flat stepped, no glow)
        for sg in (-1, 1):
            cxx = fx + sg * int(fr * 0.56)
            cyy = fy + int(fr * 0.26)
            pygame.draw.circle(surf, CHEEK, (cxx, cyy), max(2, int(fr * 0.16)))
            pygame.draw.circle(surf, lerp(CHEEK, SHEEN, 0.5),
                               (cxx - int(fr * 0.05), cyy - int(fr * 0.05)),
                               max(1, int(fr * 0.07)))
        # a calm tiny mouth — a soft closed curve
        pygame.draw.arc(surf, INK,
                        (fx - int(fr * 0.18), fy + int(fr * 0.30),
                         int(fr * 0.36), int(fr * 0.26)),
                        math.radians(20), math.radians(160), max(1, int(2.0 * s)))
        # a small snow-blue glow pip on the brow (echoes the cap rings — flat)
        gy = fy - int(fr * 0.52)
        pygame.draw.circle(surf, GLOW, (fx, gy), max(2, int(fr * 0.18)))
        pygame.draw.circle(surf, GLOW_HOT, (fx - int(fr * 0.05), gy - int(fr * 0.05)),
                           max(1, int(fr * 0.09)))


# ── one straight node-segment of the SNOW-SLEEVED culm shaft (tileable band) ──
def culm_segment(surf, cx, y0, y1, w, s, snow_cap=True):
    """One DEAD-STRAIGHT node segment of the SNOW-SLEEVED culm. WHY perfectly
    vertical: the shaft is the repeat band and MUST stay mirror-clean — the bow is
    not allowed to live here (locked AD pin, KEPT).

    Round 2 FLIPS the palette thesis (the binding gate): the barrel fill is now
    SNOW-WHITE with a blue-shadow form shade — the culm is snow-SLEEVED and reads
    white/pale-blue like the cap, NOT a green column. Frost-green survives ONLY as
    a 1px COLD SLIVER at the node-groove and the segment's right edge — a cold seam
    peeking from under snow. The dark-core node GROOVE now carries the silhouette-
    internal value work the green rings did in round 1, so a white culm doesn't
    melt into one blob against a bright noon sky."""
    hw = w * 0.5
    # === the snow-sleeved barrel (WHITE body — the palette flip) ===============
    barrel = [(cx - hw, y0), (cx + hw, y0), (cx + hw, y1), (cx - hw, y1)]
    pygame.draw.polygon(surf, INK, barrel)
    pygame.draw.polygon(surf, SNOW, barrel)
    # blue-shadow form shade down the right (the round-culm shadow side)
    pygame.draw.polygon(surf, SNOW_SH, [
        (cx + hw * 0.30, y0), (cx + hw, y0), (cx + hw, y1), (cx + hw * 0.30, y1)])
    # deepest blue at the very right rim (turns the form)
    pygame.draw.polygon(surf, SNOW_DD, [
        (cx + hw * 0.74, y0), (cx + hw, y0), (cx + hw, y1), (cx + hw * 0.74, y1)])
    # TOP-LEFT rim-sheen rail (house triad — sheen on the lit top-left)
    pygame.draw.polygon(surf, SHEEN, [
        (cx - hw, y0), (cx - hw * 0.34, y0),
        (cx - hw * 0.44, y1), (cx - hw, y1)])
    # THIN frost-green cold sliver at the right form-edge (the ONLY green here) —
    # a 1px cold seam peeking from under the snow sleeve.
    pygame.draw.line(surf, CULM, (cx + hw * 0.92, y0 + int(2 * s)),
                     (cx + hw * 0.92, y1 - int(2 * s)), max(1, int(1.0 * s)))
    pygame.draw.polygon(surf, INK, barrel, max(1, int(1.6 * s)))

    # === the NODE GROOVE at the top of the segment (the value tell) ============
    # Round 2: a CRISP dark-core groove per node does the body-internal work the
    # green ring did in round 1 — so the white culm reads as stacked segments, not
    # one blob, on a bright sky. A thin frost-green hairline tucks INTO the groove
    # as the cold sliver; a packed-snow ridge perches on the node shoulder.
    ny = y0
    groove = [(cx - hw - int(1 * s), ny + int(3 * s)),
              (cx - hw - int(1 * s), ny - int(3 * s)),
              (cx + hw + int(1 * s), ny - int(3 * s)),
              (cx + hw + int(1 * s), ny + int(3 * s))]
    pygame.draw.polygon(surf, GROOVE, groove)
    # frost-green cold hairline inside the dark groove (the sliver, not the body)
    pygame.draw.line(surf, CULM, (cx - hw, ny + int(1 * s)),
                     (cx + hw, ny + int(1 * s)), max(1, int(1.0 * s)))
    if snow_cap:
        # a little packed snow ridge perched on the node shoulder — stepped flat
        ridge = [(cx - hw, ny - int(2 * s)),
                 (cx - int(hw * 0.5), ny - int(8 * s)),
                 (cx + int(hw * 0.2), ny - int(9 * s)),
                 (cx + hw, ny - int(3 * s)),
                 (cx + int(hw * 0.3), ny - int(1 * s)),
                 (cx - int(hw * 0.4), ny - int(1 * s))]
        pygame.draw.polygon(surf, INK, ridge)
        pygame.draw.polygon(surf, SNOW, ridge)
        pygame.draw.polygon(surf, SHEEN, [
            (cx - hw, ny - int(2 * s)),
            (cx - int(hw * 0.5), ny - int(7 * s)),
            (cx - int(hw * 0.05), ny - int(6 * s)),
            (cx - int(hw * 0.4), ny - int(2 * s))])
        pygame.draw.polygon(surf, INK, ridge, max(1, int(1.2 * s)))


# ── a single hanging snow-leaf shoot with an icicle drip (shaft side fringe) ──
def snow_leaf(surf, root, ang, length, s, sign):
    """A drooping bamboo leaf-blade sheeted in snow, an icicle hanging off its
    tip. Round 2: the blade body is now SNOW-WHITE too — frost-green survives only
    as a 1px cold sliver along the leaf's lower EDGE (the cold seam under snow),
    matching the culm's flipped palette."""
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca
    rx, ry = root
    tip = (rx + ca * length, ry + sa * length)
    bw = 6.5 * s
    leaf = [(rx, ry),
            (rx + ca * length * 0.4 + px * bw, ry + sa * length * 0.4 + py * bw),
            tip,
            (rx + ca * length * 0.4 - px * bw, ry + sa * length * 0.4 - py * bw)]
    pygame.draw.polygon(surf, INK, leaf)
    pygame.draw.polygon(surf, SNOW, leaf)
    # blue-shadow underside of the blade (form shade)
    pygame.draw.polygon(surf, SNOW_SH, [
        (rx, ry),
        tip,
        (rx + ca * length * 0.4 - px * bw, ry + sa * length * 0.4 - py * bw)])
    # snow sheen sheeting the top of the blade
    pygame.draw.polygon(surf, SHEEN, [
        (rx, ry),
        (rx + ca * length * 0.4 + px * bw, ry + sa * length * 0.4 + py * bw),
        (rx + ca * length * 0.6, ry + sa * length * 0.6)])
    # thin frost-green cold sliver along the lower leaf edge (the ONLY green)
    pygame.draw.line(surf, CULM,
                     (rx + ca * length * 0.42 - px * bw, ry + sa * length * 0.42 - py * bw),
                     tip, max(1, int(1.0 * s)))
    pygame.draw.polygon(surf, INK, leaf, max(1, int(1.4 * s)))
    # a chunky icicle hanging straight down off the tip
    icicle(surf, tip, 12 * s, 5.0 * s, s)


# ── the bowed-snow-stalk hero ─────────────────────────────────────────────────
def draw_yukitake(surf, cx, cy, s):
    """The winter bamboo spirit: a DEAD-STRAIGHT SNOW-SLEEVED culm whose heavy
    lopsided snow-loaf cap (with the spirit-face) leans hard to one side — so the
    WHOLE reads 'bowed under snow' while the body never curves. `s` = unit scale
    around a ~150-unit figure."""
    seg_h = int(30 * s)
    col_w = int(26 * s)
    base_y = cy + int(72 * s)
    n_seg = 4
    top_y = base_y - n_seg * seg_h

    # rooted base clump of snow at the foot
    triad_blob(surf, SNOW,
               [(cx - int(col_w * 0.9), base_y - int(4 * s)),
                (cx - int(col_w * 1.2), base_y + int(14 * s)),
                (cx + int(col_w * 1.3), base_y + int(16 * s)),
                (cx + int(col_w * 0.9), base_y - int(4 * s))],
               core_pts=[(cx + int(col_w * 0.2), base_y),
                         (cx + int(col_w * 1.2), base_y + int(14 * s)),
                         (cx + int(col_w * 0.4), base_y + int(12 * s))],
               sheen_pts=[(cx - int(col_w * 0.8), base_y),
                          (cx - int(col_w * 1.0), base_y + int(10 * s)),
                          (cx - int(col_w * 0.3), base_y + int(8 * s))],
               ow=max(1, int(1.6 * s)))

    # straight stacked node segments — perfectly vertical (the tileable body)
    for i in range(n_seg):
        y1 = base_y - i * seg_h
        y0 = y1 - seg_h
        culm_segment(surf, cx, y0, y1, col_w, s, snow_cap=True)

    # a couple of snow-laden leaf shoots drooping off the upper shaft (icicle tips)
    snow_leaf(surf, (cx - int(col_w * 0.5), top_y + int(seg_h * 0.6)),
              math.radians(150), 28 * s, s, -1)
    snow_leaf(surf, (cx + int(col_w * 0.5), top_y + int(seg_h * 1.4)),
              math.radians(34), 24 * s, s, +1)

    # the heavy snow-loaf crown — the entire BOW lives here.
    snow_loaf(surf, cx, top_y - int(10 * s), int(96 * s), int(58 * s), s,
              lean=1.0, drip_n=4, lit=True, face=True)


# ── the snow-culm → pillar mirror ─────────────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The snow-laden culm IS the pillar: a STRAIGHT snow-sleeved culm shaft of
    stacked node segments = the tileable repeat band; the heavy snow-loaf + icicle
    fringe = the gap-edge cap. WHY the shaft stays dead straight here: this panel
    PROVES the AD pin — a curved body could not tile, so the bow is confined to the
    cap and the segments mirror cleanly. (Glow disabled on the body bands so the
    repeat stays clean; the cap carries the glow.)"""
    col_w = int(22 * s)
    seg_h = int(30 * s)
    cap_room = int(54 * s)

    if cap == "bottom":
        b0, b1 = top + int(4 * s), bot - cap_room
        y = b1
        while y - seg_h >= b0:
            culm_segment(surf, cx, y - seg_h, y, col_w, s, snow_cap=True)
            y -= seg_h
        snow_loaf(surf, cx, bot - int(30 * s), int(74 * s), int(46 * s), s,
                  lean=1.0, drip_n=4, lit=True, face=True)
    else:
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        h = surf.get_height()
        draw_pillar(tmp, cx, h - bot, h - top, s, cap="bottom")
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
    W, H = 1010, 920
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("YUKITAKE", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "snow-bowed bamboo spirit  ·  ROUND 2 — palette FLIPPED: snow-WHITE body (culm snow-sleeved) · green = thin cold SLIVER · "
        "snow-blue glow added · top-left node sheen · chunky icicle teeth",
        True, LABEL_DIM), (215, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_yukitake(big, 188 * SS, 250 * SS, 1.75 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("STRAIGHT SNOW-SLEEVED culm (white body, blue-shadow form shade); heavy snow-loaf", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("cap sags hard right (the whole BOW) with the face nudged onto the HEAVY side.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Snow-blue stepped glow rings on the cap. Green = a cold sliver in node grooves only.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, clean tileable STRAIGHT shaft =======
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (44, 56, 70), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — snow culm", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("STRAIGHT node segments (dark groove +", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("snow ridge per node) = shaft; snow-loaf", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("+ icicle teeth caps each edge — clean mirror, bow stays in the CAP", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) right column: 32px chips on day+night+NOON, silhouette, palette ==
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 740))
    sheet.blit(font.render("True 32px — WINTER-first gate", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_yukitake(big, 48 * SS, 52 * SS, (32 / 152.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 124
    # day sky chip
    vgrad(sheet, (panel_x + 20, day_y, 100, 100), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 100, 100), 1)
    sheet.blit(chip, (panel_x + 22, day_y + 2))
    sheet.blit(font_sm.render("day sky", True, LABEL), (panel_x + 20, day_y + 102))
    # bright NOON sky chip (the worst-case bright card — does the white still read?)
    vgrad(sheet, (panel_x + 130, day_y, 100, 100), NOON_T, NOON_B)
    pygame.draw.rect(sheet, INK, (panel_x + 130, day_y, 100, 100), 1)
    sheet.blit(chip, (panel_x + 132, day_y + 2))
    sheet.blit(font_sm.render("bright NOON sky", True, LABEL), (panel_x + 130, day_y + 102))

    night_y = day_y + 132
    vgrad(sheet, (panel_x + 20, night_y, 100, 100), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 100, 100), 1)
    sheet.blit(chip, (panel_x + 22, night_y + 2))
    sheet.blit(font_sm.render("night sky", True, LABEL_DIM), (panel_x + 20, night_y + 102))

    # blacked-out 32px silhouette — the BOWED-SNOW-STALK read TEST
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_yukitake(big, 48 * SS, 52 * SS, (32 / 152.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
        return sil

    sil_x = panel_x + 130
    pygame.draw.rect(sheet, (212, 220, 226), (sil_x, night_y, 100, 100))
    pygame.draw.rect(sheet, INK, (sil_x, night_y, 100, 100), 1)
    sheet.blit(silhouette32(), (sil_x + 2, night_y + 2))
    sheet.blit(font_sm.render("silhouette", True, LABEL_DIM), (sil_x, night_y + 102))

    # 4x-zoom 32px chip — so the reviewer can count green pixels (should be ≈2-3)
    zoom_y = night_y + 130
    z = pygame.transform.scale(chip, (96 * 2, 96 * 2))   # 2x of the 96 (which is 3x of 32)
    # actually show the 32px render at honest 6x for pixel counting:
    big32 = pygame.Surface((32 * SS, 32 * SS), pygame.SRCALPHA)
    draw_yukitake(big32, 16 * SS, 17 * SS, (32 / 152.0) * SS)
    true32 = pygame.transform.smoothscale(big32, (32, 32))
    true32 = grow_outline(true32, INK + (255,), 1)
    zoom = pygame.transform.scale(true32, (192, 192))
    vgrad(sheet, (panel_x + 20, zoom_y, 192, 192), NOON_T, NOON_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, zoom_y, 192, 192), 1)
    sheet.blit(zoom, (panel_x + 20, zoom_y))
    sheet.blit(font_sm.render("true 32px @6x on NOON sky — count the green: a sliver only", True, LABEL), (panel_x + 20, zoom_y + 194))

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, zoom_y + 218))
    swatches = [
        (SNOW, "snow-white BODY"), (SNOW_SH, "blue-shadow shade"),
        (GLOW, "snow-blue glow"), (ICE, "icicle-cyan"),
        (CULM, "frost-green sliver"), (CULM_D, "deep cold green"),
        (CHEEK, "rosy cheek"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, zoom_y + 246
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 872, W - 28, 40))
    sheet.blit(font_sm.render(
        "ROUND 2 vs r1: culm flipped GREEN->SNOW-WHITE body (green now a 1px sliver in node grooves) · cooled green off mint · "
        "dark node GROOVE carries the value · snow-blue STEPPED glow added · node sheen moved TOP-LEFT · chunky icicle TEETH · "
        "face on the heavy side. KEPT: straight shaft + bow-in-cap (pin) · cap mass · chibi face.",
        True, LABEL_DIM), (26, 879))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
