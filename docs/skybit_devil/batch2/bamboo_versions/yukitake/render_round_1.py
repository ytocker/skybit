"""
Round-1 concept renderer for YUKITAKE — the snow-bowed bamboo spirit
(Bamboo-versions set, concept #4). Headless Pygame; ELEVATED pipeline
(supersample SS=6 → smoothscale) so the snow-loaf ridges + icicle drips stay
crisp at downscale. Keeps the shipped house grammar: flat fills, hard 1-2px ink
keyline, dark-core → flat-fill → top-left rim-sheen triad, 1px alpha-grown
outline, chibi proportions, scary-CUTE pushed EPIC; procedural-only (no
gradients/PNGs/soft raster halos).

WHY this is the BOWED-SNOW-STALK of the set: the roster has no winter boss and
no non-vertical posture. Yukitake is the ONLY bowed one — but the bow is a TRAP
for the pillar repeat, so the locked AD pin is structural: the SHAFT is drawn
DEAD STRAIGHT and the entire bow lives in the snow-loaf CAP (cap tilt + heavy
snow mass leaning to one side). A curved shaft would break the tileable mirror;
a straight shaft under a heavy lopsided snow-loaf reads "bowed under snow" while
staying mirror-clean. The pillar-tile panel exists to PROVE the straight shaft
tiles.

WHY the palette is the most distinct in the set: snow-white/blue is the body,
held FAR from every roster green. Green appears ONLY as a small COLD accent
(the culm peeking out from under the snow, frost-green node bands) — never the
body. The glow is snow-blue, deliberately held clear of Yurei cyan and Kitsune
mint so the two glow bosses never collide.

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
# Snow-white/blue is the DOMINANT mass. Green is a small COLD accent only — the
# culm glimpsed under the snow + frost node bands — and never the body. The glow
# is snow-blue, held clear of Yurei cyan and Kitsune mint.
SNOW      = (232, 238, 244)   # snow-white base (the dominant fill)
SNOW_SH   = (150, 176, 200)   # blue-shadow snow shade / dark-core
SNOW_DD   = (108, 138, 170)   # deepest blue snow hollow (under-loaf, drip roots)
SHEEN     = (248, 252, 255)   # hottest snow sheen / highlight
ICE       = (198, 232, 242)   # icicle-cyan (the drip bodies)
GLOW      = (170, 212, 236)   # snow-blue glow (the SOLE glow)
GLOW_HOT  = (214, 238, 250)   # hottest snow-blue glow core
CULM      = (120, 178, 150)   # frost-green culm accent (the ONLY green; small + COLD)
CULM_D    = ( 72, 122, 100)   # deep frost-green node shade
CULM_HI   = (176, 214, 188)   # pale frost-green culm sheen
CHEEK     = (224, 156, 168)   # rosy cold cheek (a tiny warm life-spark)
INK       = ( 28,  34,  40)   # hard ink keyline (cooled toward the brief's note)

BG        = ( 74,  88, 104)   # neutral cool-slate review backdrop
PANEL     = ( 58,  72,  88)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
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


# ── a single ICICLE drip (the cold tell that fringes the snow-loaf) ──────────
def icicle(surf, root, length, width, s):
    """One hanging icicle: a fat tapered cyan spike rooted at `root`, narrowing
    to a sharp point straight DOWN. WHY fat & triad-lit: a thread-thin drip
    dissolves at 32px — the icicle fringe is part of the WINTER read, so each
    drip is a solid stepped spike (cyan body, snow-blue dark side, white sheen
    rail) that survives the downscale."""
    rx, ry = root
    hw = width * 0.5
    tip = (rx, ry + length)
    spike = [
        (rx - hw, ry),
        (rx + hw, ry),
        (rx + hw * 0.18, ry + length * 0.72),
        tip,
        (rx - hw * 0.18, ry + length * 0.72),
    ]
    pygame.draw.polygon(surf, INK, spike)
    pygame.draw.polygon(surf, ICE, spike)
    # dark blue side (right) for volume
    pygame.draw.polygon(surf, SNOW_DD, [
        (rx + hw * 0.2, ry),
        (rx + hw, ry),
        (rx + hw * 0.18, ry + length * 0.72),
        tip,
    ])
    # white sheen rail down the left
    pygame.draw.line(surf, SHEEN, (rx - hw * 0.4, ry + length * 0.1),
                     (rx - hw * 0.05, ry + length * 0.6), max(1, int(width * 0.22)))
    pygame.draw.polygon(surf, INK, spike, max(1, int(width * 0.14)))


# ── a lopsided heavy SNOW-LOAF (the cap — the entire bow lives HERE) ─────────
def snow_loaf(surf, cx, cy, w, h, s, lean, drip_n=5, lit=True, face=True):
    """The heavy snow-loaf cap. WHY this is where the bow lives: the AD pin is
    that the SHAFT stays dead straight, so ALL the bowed read is carried by this
    cap — its silhouette is a fat snow pillow that BULGES and SAGS to one side
    (`lean` > 0 pushes the mass right/down) as if the weight is dragging the
    whole spirit over. Rounded ridges of snow stepped on top (flat stepped, no
    gradient), an icicle fringe hanging below, and a chubby spirit-face nestled
    in the bend. This single drawable IS the gap-edge cap.

    `lean` shifts the loaf's mass sideways (the sag direction). Positive leans
    the mass to the +x side."""
    lx = int(lean * w * 0.32)                  # how far the mass sags sideways
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
    # two pale arcs of packed snow sitting on top of the loaf — the "drifted"
    # read. Stepped flat fills only.
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

    # === ICICLE fringe hanging off the heavy (sagging) underbelly ==============
    # drips cluster toward the lean side (where the snow is heaviest) — reinforces
    # that the mass is dragging that way.
    base_y = cy + int(h * 0.14)
    span_l = cx - int(w * 0.34)
    span_r = cx + lx + int(w * 0.52)
    for i in range(drip_n):
        t = i / max(1, drip_n - 1)
        dx = int(span_l + (span_r - span_l) * t)
        # longer drips on the heavy (right/lean) side
        dl = (10 + 16 * t) * s + (4 * s if lean > 0 else 0)
        dw = (5.5 - 1.5 * abs(t - 0.5)) * s
        dy = base_y + int((0.06 + 0.10 * t) * h)
        icicle(surf, (dx, dy), dl, dw, s)

    # === the chubby spirit-FACE nestled in the bend (closed gentle eyes) =======
    # WHY tucked under the loaf on the lean side: the face peeks from where the
    # bow happens — the brief's "gentle spirit-face peeking from the bend." Big
    # head, tiny calm features = chibi + scary-CUTE held gentle (a serene winter
    # spirit, not a snarl).
    if face:
        fx = cx + int(lx * 0.55) + int(w * 0.06)
        fy = cy + int(h * 0.04)
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
        # a small snow-blue glow pip on the brow (the SOLE glow — flat stepped)
        gy = fy - int(fr * 0.52)
        pygame.draw.circle(surf, GLOW, (fx, gy), max(2, int(fr * 0.18)))
        pygame.draw.circle(surf, GLOW_HOT, (fx - int(fr * 0.05), gy - int(fr * 0.05)),
                           max(1, int(fr * 0.09)))


# ── one straight node-segment of the pale culm shaft (the tileable band) ─────
def culm_segment(surf, cx, y0, y1, w, s, snow_cap=True):
    """One DEAD-STRAIGHT node segment of the pale culm. WHY perfectly vertical:
    the shaft is the repeat band and MUST stay mirror-clean — the bow is not
    allowed to live here (locked AD pin). Each segment is a snow-sleeved pale
    culm barrel: a frost-green culm core glimpsed at the sides, sleeved in snow
    on the top-left (the lit, snow-catching face), with a packed snow ridge on
    its upper node shoulder. Triad-lit so it reads as a round culm, not a flat
    bar."""
    hw = w * 0.5
    # === the culm barrel (frost-green core — the ONLY green, kept small) =======
    barrel = [(cx - hw, y0), (cx + hw, y0), (cx + hw, y1), (cx - hw, y1)]
    pygame.draw.polygon(surf, INK, barrel)
    pygame.draw.polygon(surf, CULM, barrel)
    # dark frost-green core down the right (shadow side)
    pygame.draw.polygon(surf, CULM_D, [
        (cx + hw * 0.18, y0), (cx + hw, y0), (cx + hw, y1), (cx + hw * 0.18, y1)])
    # === snow sleeve sheeting the top-left face (snow clings to the lit side) ==
    # this keeps the SHAFT reading snow-white-dominant while the green is only a
    # cold sliver at the right edge.
    sleeve = [(cx - hw, y0), (cx + hw * 0.22, y0),
              (cx + hw * 0.10, y1), (cx - hw, y1)]
    pygame.draw.polygon(surf, SNOW, sleeve)
    pygame.draw.polygon(surf, SHEEN, [
        (cx - hw, y0), (cx - hw * 0.32, y0),
        (cx - hw * 0.42, y1), (cx - hw, y1)])
    # thin frost-green sliver line where culm meets snow sleeve (the cold accent)
    pygame.draw.line(surf, CULM_HI, (cx + hw * 0.16, y0 + int(2 * s)),
                     (cx + hw * 0.04, y1 - int(2 * s)), max(1, int(1.2 * s)))
    pygame.draw.polygon(surf, INK, barrel, max(1, int(1.6 * s)))

    # === the NODE ring at the top of the segment (packed snow ridge) ==========
    # a node = a frost-green raised ring + a packed-snow loaf sitting ON it. This
    # snow-cap ridge per node IS the brief's repeat-band tell.
    ny = y0
    node = [(cx - hw - int(2 * s), ny + int(3 * s)),
            (cx - hw - int(2 * s), ny - int(3 * s)),
            (cx + hw + int(2 * s), ny - int(3 * s)),
            (cx + hw + int(2 * s), ny + int(3 * s))]
    pygame.draw.polygon(surf, INK, node)
    pygame.draw.polygon(surf, CULM_D, node)
    pygame.draw.line(surf, CULM_HI, (cx - hw, ny - int(2 * s)),
                     (cx + hw * 0.1, ny - int(2 * s)), max(1, int(1.2 * s)))
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
    tip. WHY: the brief calls for icicle drips at the leaf-tips; a few snow-laden
    leaf shoots breaking the straight shaft's edge add winter silhouette without
    curving the culm itself."""
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
    pygame.draw.polygon(surf, CULM, leaf)
    # snow sheeting the top of the blade
    pygame.draw.polygon(surf, SNOW, [
        (rx, ry),
        (rx + ca * length * 0.4 + px * bw, ry + sa * length * 0.4 + py * bw),
        tip,
        (rx + ca * length * 0.6, ry + sa * length * 0.6)])
    pygame.draw.line(surf, CULM_HI, (rx, ry), tip, max(1, int(1.2 * s)))
    pygame.draw.polygon(surf, INK, leaf, max(1, int(1.4 * s)))
    # an icicle hanging straight down off the tip
    icicle(surf, tip, 11 * s, 4.0 * s, s)


# ── the bowed-snow-stalk hero ─────────────────────────────────────────────────
def draw_yukitake(surf, cx, cy, s):
    """The winter bamboo spirit: a DEAD-STRAIGHT pale snow-sleeved culm whose
    heavy lopsided snow-loaf cap (with the spirit-face) leans hard to one side —
    so the WHOLE reads 'bowed under snow' while the body never curves. `s` = unit
    scale around a ~150-unit figure. Drawn bottom-to-top: rooted base → straight
    stacked node segments → side snow-leaf shoots → the heavy snow-loaf crown."""
    # straight column geometry — the spine is perfectly vertical
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

    # a couple of snow-laden leaf shoots drooping off the upper shaft (icicle
    # tips) — winter silhouette without curving the culm
    snow_leaf(surf, (cx - int(col_w * 0.5), top_y + int(seg_h * 0.6)),
              math.radians(150), 28 * s, s, -1)
    snow_leaf(surf, (cx + int(col_w * 0.5), top_y + int(seg_h * 1.4)),
              math.radians(34), 24 * s, s, +1)

    # the heavy snow-loaf crown — the entire BOW lives here. It sits centred on
    # the straight shaft top but its mass sags hard to the right, dragging the
    # spirit-face with it.
    snow_loaf(surf, cx, top_y - int(10 * s), int(96 * s), int(58 * s), s,
              lean=1.0, drip_n=6, lit=True, face=True)


# ── the snow-culm → pillar mirror ─────────────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The snow-laden culm IS the pillar: a STRAIGHT pale culm shaft of stacked
    node segments (snow-cap ridge per node) = the tileable repeat band; the heavy
    snow-loaf + icicle fringe = the gap-edge cap. WHY the shaft stays dead
    straight here: this panel exists to PROVE the AD pin — a curved body could not
    tile, so the bow is confined to the cap and the segments mirror cleanly.

    `cap` names the END that faces the GAP."""
    col_w = int(22 * s)
    seg_h = int(30 * s)
    cap_room = int(54 * s)

    if cap == "bottom":
        b0, b1 = top + int(4 * s), bot - cap_room
        # stack segments downward from the top; the cap hangs at the bottom edge
        y = b1
        while y - seg_h >= b0:
            culm_segment(surf, cx, y - seg_h, y, col_w, s, snow_cap=True)
            y -= seg_h
        # gap-edge cap: the snow-loaf hangs at the bottom, mass sagging toward gap
        snow_loaf(surf, cx, bot - int(30 * s), int(74 * s), int(46 * s), s,
                  lean=1.0, drip_n=5, lit=True, face=True)
    else:
        # mirror: draw the whole pillar with a bottom cap onto a temp surface and
        # flip it vertically — proves the straight shaft + cap mirror cleanly.
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
    W, H = 1010, 900
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("YUKITAKE", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "snow-bowed bamboo spirit  ·  DEAD-STRAIGHT culm shaft · bow lives ONLY in the lopsided snow-loaf CAP · "
        "snow-white/blue body · green = cold accent · round 1",
        True, LABEL_DIM), (215, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_yukitake(big, 188 * SS, 250 * SS, 1.75 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("STRAIGHT snow-sleeved culm; heavy snow-loaf cap sags hard to one side (the", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("whole BOW) with the gentle spirit-face nestled in the bend. Icicle fringe +", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("snow-leaf drips. Green is a cold sliver at the culm edges only — body is snow.", True, LABEL_DIM), (14, 622))

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
    sheet.blit(font_sm.render("STRAIGHT node segments (snow-cap ridge", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("per node) = shaft; snow-loaf + icicle", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("fringe caps each edge — clean mirror, bow stays in the CAP", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) right column: 32px chips on day+night, silhouette, palette, tile =
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_yukitake(big, 48 * SS, 52 * SS, (32 / 152.0) * SS)
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

    # blacked-out 32px silhouette — the BOWED-SNOW-STALK read TEST: a straight
    # stalk with a heavy lopsided cap, never a vertical column or a ball.
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_yukitake(big, 48 * SS, 52 * SS, (32 / 152.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
        return sil

    sil_y = night_y + 188
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 220, 226), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 24))
    sheet.blit(font_sm.render("straight stalk, heavy lopsided", True, LABEL_DIM), (sx + 104, sil_y + 42))
    sheet.blit(font_sm.render("snow-loaf cap (the bow)", True, LABEL_DIM), (sx + 104, sil_y + 60))

    # pillar-tile chip — the PROOF the straight shaft tiles cleanly (3 stacked
    # body bands, no cap) on day + night
    def pillar_tile_chip():
        # render a tall band of pure shaft (no cap), repeated, to show the seam
        big = pygame.Surface((44 * SS, 150 * SS), pygame.SRCALPHA)
        col_w = int(22 * (0.34 * SS))
        seg_h = int(30 * (0.34 * SS))
        ccx = 22 * SS
        y = 146 * SS
        while y - seg_h >= 4 * SS:
            culm_segment(big, ccx, y - seg_h, y, col_w, 0.34 * SS, snow_cap=True)
            y -= seg_h
        small = pygame.transform.smoothscale(big, (44, 150))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_tile_chip()
    px2 = panel_x + 192
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y))
    sheet.blit(font_sm.render("tile", True, LABEL_DIM), (px2 + 14, day_y - 16))
    sheet.blit(font_sm.render("shaft", True, LABEL_DIM), (px2 + 10, night_y - 16))

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 636))
    swatches = [
        (SNOW, "snow-white base"), (SNOW_SH, "blue-shadow sh"),
        (GLOW, "snow-blue glow"), (ICE, "icicle-cyan"),
        (CULM, "frost-green accent"), (CULM_D, "deep frost-green"),
        (CHEEK, "rosy cheek"), (INK, "ink keyline"),
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
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (28,34,40) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-CUTE · procedural-only · "
        "SHAFT dead-straight, BOW in the CAP only · green = cold accent.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
