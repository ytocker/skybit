"""
Round-1 concept renderer for the BONE-CANDLE DRIP-COLUMN — clown-event obstacle
column #5 of the bone roster. Headless Pygame; ELEVATED pipeline (SS supersample
-> smoothscale) so the organic wax-slump silhouette + the guttering flame-skull
sconce survive the downscale to the 58px route tile. Standalone under docs/ so
review art never enters the shipped bundle: it borrows only colour math + the
triad/outline house helpers, never a runtime sprite module.

WHY this column is the GROWN, asymmetric one: the bone roster's other four
columns are RIGID + symmetric (stacked totem, skewer-threaded vertebrae, woven
femur lattice, hybrid cage). This one is the melted-wax outlier — a softly
bulging, organically slumped bone shaft (a guttered altar candle gone to bone)
with sagging drip-lobes down ALTERNATING sides and thin gold wax-runnels tracing
the runs. The irregular lump silhouette is the whole differentiation: it must
read as a different KIND of object from the others, not the same shaft re-dressed.

CRITICAL hitbox discipline (the AD's hard note): the asymmetric wax-slump is
COSMETIC ONLY. The actual gap-framing collision silhouette is a clean, honest
column — a gentle sine-bulge profile that NEVER swells past a fixed safe
half-width near the gap, and a FLAT, read-clear cap edge at Pip's gap. The
drip-lobes only ever sag DOWN the OUTER flanks (away from the lane), and they
taper to nothing well before the gap-facing cap. So the visible mass the player
reads as "wall" is exactly the mass that kills — no pale wax bleeds
unpredictably into the flight gap.

WHY the pale wax still holds on a busy day sky: warm-ivory bone is low-contrast
against the bright day gradient, so a HARD 1-2px ink keyline (28,22,30) carries
the silhouette, the dark-core triad keeps the body reading SOLID (never a washed
pale blob), and the gold wax-runnels inject a warm hue so the column never
collapses to a grey smear. An alpha-grown 1px outline rings the whole tile.

WHY the flame-skull sconce caps the gap: the column's mouth at Pip's lane is a
guttering skull whose eye-sockets gutter a CYAN SOUL-FLAME down INTO the gap,
lighting the lane — the Verdigris Drowned-King soul-flame / wisdom-flame motif
ported across. The flame is drawn from additive radial glow caches behind a
faceted cyan/purple wisdom gem, so it reads as light, not paint.
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

_HERE = os.path.dirname(os.path.abspath(__file__))
_FONT_PATH = os.path.abspath(os.path.join(_HERE, "..", "..", "..",
                                          "game", "assets",
                                          "LiberationSans-Bold.ttf"))


def font(sz):
    if os.path.exists(_FONT_PATH):
        return pygame.font.Font(_FONT_PATH, sz)
    return pygame.font.SysFont("DejaVu Sans", sz, bold=True)


# ── PALETTE (bone-roster house grammar, candle-warm) ──────────────────────────
# Warm-ivory bone field, R>=G>=B so it reads as real altar-wax bone, not steel.
# Body is the dark-core -> flat-fill -> top-left rim-sheen triad. Gold is the
# thin-accent wax-runnel only. Cyan + purple are the faceted wisdom-gem / soul-
# flame focal. INK is the one hard keyline value across the whole roster.
BONE     = (224, 216, 196)   # warm-ivory wax-bone (the dominant body fill)
BONE_D   = (160, 150, 128)   # bone mid-core / shade
BONE_DD  = ( 92,  84,  70)   # deepest bone hollow (runnel troughs, drip undershade)
BONE_SH  = (240, 234, 218)   # top-left rim-sheen (warm near-white)
GOLD     = (228, 182,  76)   # wax-runnel thin accent
GOLD_BR  = (252, 224, 140)   # runnel catch-light
GOLD_D   = (150, 112,  40)   # runnel trough / pooled drip shadow
CYAN     = ( 96, 220, 230)   # soul-flame / wisdom gem hero cyan
CYAN_BR  = (198, 250, 252)   # hot inner flame (white-cyan core)
CYAN_D   = ( 40, 132, 150)
PURPLE   = (158, 120, 220)   # the second faceted gem hue (cyan/purple pair)
PURPLE_BR = (212, 188, 250)
INK      = ( 28,  22,  30)   # the hard roster keyline

# review-sheet chrome + biome skies (matched to the bone-roster review sheets).
BG        = ( 30,  34,  46)
PANEL     = ( 46,  50,  64)
DAY_SKY_T = (118, 192, 234)
DAY_SKY_B = (198, 230, 244)
NIGHT_T   = ( 20,  24,  50)
NIGHT_B   = ( 46,  42,  80)
LABEL     = (238, 240, 246)
LABEL_DIM = (186, 194, 208)

# Pillar geometry (mirrors game/config.py — the route tile is tall + narrow).
PIPE_W = 58


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ── house helpers (ported, not imported, per the docs/ standalone rule) ───────
def grow_outline(surf, color, px):
    """The alpha-grown 1px silhouette outline — the roster's read-anchor on the
    bright day sky. Rings the finished tile in INK so the pale wax never floats."""
    mask = pygame.mask.from_surface(surf)
    pts = mask.outline()
    if len(pts) < 2:
        return surf
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(surf, (0, 0))
    return ring


def triad_blob(surf, color, pts, *, core_pts=None, sheen_pts=None, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + hard ink keyline."""
    pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.42), sheen_pts)
    pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, *, ow=2, core=True, sheen=True):
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.40),
                           (c[0] + int(r * 0.26), c[1] + int(r * 0.30)),
                           int(r * 0.76))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.45),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


def radial_glow(r, color, alpha):
    """An additive radial soul-glow cache — bright core falling to transparent.
    The soul-flame reads as LIGHT (blitted BLEND_RGBA_ADD), never flat paint."""
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for i in range(r, 0, -1):
        a = max(0, min(255, int(alpha * (i / r) ** 2.2)))
        pygame.draw.circle(g, (*color, a), (r, r), r - (r - i))
    return g


def vgrad(surf, rect, top, bot):
    x, y, w, h = rect
    for i in range(h):
        surf.fill(lerp(top, bot, i / max(1, h - 1)), (x, y + i, w, 1))


# ── the wax-slump COLUMN profile (the honest collision edge lives here) ───────
# `half_at(t, side)` returns the visible half-width of the column at vertical
# fraction t (0 at the gap-facing cap, 1 at the far end), for the given flank.
# WHY split by side: the COSMETIC drip-lobes sag down ONE flank at a time
# (alternating), but they are clamped so they can swell only on the OUTER body,
# never past SAFE_HALF near the cap. The collision silhouette the engine would
# use is the SAFE rectangle (SAFE_HALF wide) — and because the drawn mass never
# exceeds SAFE_HALF near the gap and tapers in before the cap, the visible "wall"
# always matches an honest, read-clear collision edge at the lane.
SAFE_HALF = 0.5                 # fraction of half-box that is the honest wall
BULGE = 0.10                    # gentle sine-bulge of the core shaft (cosmetic)


def _core_half(t, hw):
    """The soft sine-bulge of the SHAFT core — a slow organic breathing of the
    body width. Stays well inside SAFE_HALF so it never touches the lane edge."""
    return hw * (SAFE_HALF - 0.02 + BULGE * 0.5 * (1.0 - math.cos(t * math.pi * 2.4)))


# drip-lobe schedule: (t-centre, side, reach, length) — sagging blobs down the
# OUTER flank. `reach` is how far the lobe bulges OUTWARD past the core (the lump
# silhouette); it never extends toward the lane because lobes only grow outward.
DRIPS = [
    (0.16, -1, 0.30, 0.12),
    (0.30,  1, 0.40, 0.18),
    (0.50, -1, 0.34, 0.20),
    (0.66,  1, 0.46, 0.15),
    (0.82, -1, 0.30, 0.16),
]


def draw_candle_column(surf, bw, bh, ss, *, half_seed=0):
    """Draw ONE bone-candle half into a supersampled box. The gap-facing cap (the
    flame-skull sconce) sits at the TOP of the box; the column body slumps down
    away from it. The caller flips for the top-of-gap half."""
    cx = bw // 2
    hw = bw // 2
    ow = max(2, int(2.0 * ss))
    cap_y = int(18 * ss)         # honest collision line: flat sconce base at gap

    # ── the GROWN body silhouette: a single asymmetric wax-slumped polygon ──
    # Built as a left edge + right edge walked from cap to foot. The core uses the
    # sine-bulge; the drip-lobes ADD outward bumps on their flank only. The cap
    # band (t < cap fraction) is forced FLAT + at SAFE_HALF so the gap edge stays
    # rectangular and read-clear — the slump can never eat the lane.
    n = 64
    span = bh - cap_y
    cap_t = (cap_y) / max(1, bh)

    def edge_x(t, side):
        h = _core_half(t, hw)
        # cosmetic drip-lobes — outward bumps on the matching flank only
        for (dt, dside, reach, length) in DRIPS:
            if dside != side:
                continue
            d = (t - dt) / length
            if -1.2 < d < 1.6:
                # an asymmetric tear: swells in, peaks, then a long lower sag tail
                if d < 0:
                    env = math.cos(d * math.pi * 0.5) ** 2
                else:
                    env = max(0.0, (1.0 - d / 1.6)) ** 1.4
                h += hw * reach * env
        # clamp so the visible mass NEVER exceeds the box and, crucially, near the
        # cap it is pinned to the honest SAFE wall so the lane edge is rectangular.
        h = min(h, hw - max(1, int(1.0 * ss)))
        if t < cap_t * 2.2:
            h = max(h, hw * SAFE_HALF)            # cap band: flat honest wall
            h = min(h, hw * SAFE_HALF + 1)
        return cx + side * h

    left = [(edge_x(i / n, -1), cap_y + span * (i / n)) for i in range(n + 1)]
    right = [(edge_x(i / n, 1), cap_y + span * (i / n)) for i in range(n + 1)]
    body = left + list(reversed(right))
    bpts = [(int(x), int(y)) for x, y in body]

    # WHY a CYLINDER shade, not a big dark-core poly: a 42%-toward-ink core covering
    # most of the body greys out the warm ivory and reads as wet clay. Instead the
    # flat warm BONE fill stays DOMINANT, and rounding comes from a thin right-edge
    # SHADE band + a thin left-edge SHEEN rail — the body reads as a lit warm candle.
    pygame.draw.polygon(surf, INK, bpts)
    pygame.draw.polygon(surf, BONE, bpts)
    # right-flank shade band (the dark side of the cylinder), hugging the right edge
    shade = []
    for (x, y) in right:                       # right edge, top->foot
        shade.append((x, y))
    for (x, y) in reversed(right):             # pulled inward to make a band
        shade.append((cx + (x - cx) * 0.46, y))
    pygame.draw.polygon(surf, BONE_D, [(int(x), int(y)) for x, y in shade])
    # a deeper trough hugging the very right keyline so the round read is honest
    deep = []
    for (x, y) in right:
        deep.append((x, y))
    for (x, y) in reversed(right):
        deep.append((cx + (x - cx) * 0.80, y))
    pygame.draw.polygon(surf, lerp(BONE_D, BONE_DD, 0.5),
                        [(int(x), int(y)) for x, y in deep])
    # left-flank rim-sheen rail (the lit side), a narrow warm-white band
    lit = []
    for (x, y) in left:
        lit.append((x, y))
    for (x, y) in reversed(left):
        lit.append((cx + (x - cx) * 0.66, y))
    pygame.draw.polygon(surf, BONE_SH, [(int(x), int(y)) for x, y in lit])
    pygame.draw.polygon(surf, INK, bpts, ow)

    # ── pooled drip TIPS: a fat rounded bead hangs off the end of each lobe ──
    # The lump read survives downscale because each drip ends in a circle, not a
    # thin point. The bead is bone with a dark undershade + a gold runnel kiss.
    for (dt, dside, reach, length) in DRIPS:
        tip_t = min(0.98, dt + length * 1.05)
        bx = edge_x(tip_t, dside)
        by = cap_y + span * tip_t
        br = int((3.0 + reach * 4.0) * ss)
        pygame.draw.circle(surf, INK, (int(bx), int(by)), br + max(1, int(ss)))
        pygame.draw.circle(surf, BONE_D, (int(bx), int(by)), br)
        pygame.draw.circle(surf, BONE, (int(bx), int(by)), int(br * 0.78))
        pygame.draw.circle(surf, BONE_SH,
                           (int(bx - br * 0.3), int(by - br * 0.35)),
                           max(1, int(br * 0.32)))

    # ── gold WAX-RUNNELS: thin runs tracing the slump down each drip flank ──
    # WHY gold + thin: the runnel is the warm hue separator that keeps the pale
    # wax off a grey smear, and it visually CONFIRMS the slump direction (a
    # candle that ran). Drawn as a trough shadow + a bright catch-line.
    for (dt, dside, reach, length) in DRIPS:
        run = []
        for k in range(10):
            rt = dt - length * 0.4 + (length * 1.45) * (k / 9.0)
            rt = max(0.0, min(0.99, rt))
            wob = math.sin(k * 1.1 + dt * 9) * 1.6 * ss
            ex = edge_x(rt, dside) - dside * (3.0 * ss) + wob
            run.append((int(ex), int(cap_y + span * rt)))
        pygame.draw.lines(surf, GOLD_D, False, run, max(2, int(2.2 * ss)))
        pygame.draw.lines(surf, GOLD, False, run, max(1, int(1.4 * ss)))
        pygame.draw.lines(surf, GOLD_BR, False, run[:5], max(1, int(ss)))

    # a couple of faceted wisdom-gems studding the shaft (cyan + purple), seated
    # in dim gold bezels — the roster's gem motif, scattered down the body.
    for (gt, gh) in ((0.40, PURPLE), (0.72, CYAN)):
        gx, gy = cx - int(hw * 0.10), int(cap_y + span * gt)
        gr = int(3.2 * ss)
        pygame.draw.circle(surf, GOLD_D, (gx, gy), gr + max(1, int(ss)))
        _facet_gem(surf, gx, gy, gr, gh, ss)

    return cap_y


def _facet_gem(surf, cx, cy, r, base, ss):
    """A small faceted wisdom-gem — INK-keyed diamond, lit upper-left facets, a
    hot inner highlight. Cyan or purple per the roster's gem pair."""
    bright = CYAN_BR if base is CYAN else PURPLE_BR
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, base, [(cx, cy - r + ss), (cx + r - ss, cy),
                                     (cx, cy + r - ss), (cx - r + ss, cy)])
    pygame.draw.polygon(surf, lerp(base, INK, 0.4),
                        [(cx, cy + r - ss), (cx + r - ss, cy), (cx, cy)])
    pygame.draw.polygon(surf, bright,
                        [(cx, cy - r + ss), (cx - r + ss, cy), (cx, cy)])
    pygame.draw.circle(surf, (255, 255, 255),
                       (cx - int(r * 0.3), cy - int(r * 0.3)), max(1, int(r * 0.22)))


def draw_flame_skull_sconce(surf, bw, cap_y, ss):
    """The guttering flame-skull sconce capping the gap. A wide squat skull seated
    ON the flat cap line, its eye-sockets guttering a cyan soul-flame DOWNWARD into
    the gap. The skull mass sits ABOVE the honest collision line so the soul-flame
    licking into the lane is pure light (additive glow), framing Pip's path without
    adding collision mass below the wall. Returns the two socket centres so the
    caller can lay the flame glow into the gap after the smoothscale."""
    cx = bw // 2
    ow = max(2, int(1.8 * ss))
    # skull cranium — a broad squat dome. WHY seated BELOW the flat cap line (the
    # crown nearly touches cap_y and the face hangs down INTO the body): the gap-
    # facing edge stays the flat honest wall, while the skull is the lit feature
    # the player reads at the lane. The wide dome fills the ~26px box width so the
    # face reads SOLID at 58px, not as a small lost bead.
    sr = int(13 * ss)
    scy = cap_y + int(sr * 0.80)         # face hangs below the cap, fully visible
    # a broad ROUND cranium — wide enough to nearly fill the 26px box so the face
    # reads SOLID at 58px. A light wax-gutter only at the lower temples, not a deep
    # sag that would lump the silhouette into a non-skull blob.
    dome = []
    for ang in range(-180, 1, 14):
        a = math.radians(ang)
        sag = 1.0 + (0.22 if math.sin(a) > 0.3 else 0.0) * abs(math.cos(a))
        dome.append((cx + math.cos(a) * sr * 1.18,
                     scy + math.sin(a) * sr * 1.02 * sag))
    # cheeks taper down to a short jaw stub
    dome.append((cx + sr * 0.84, scy + sr * 0.44))
    dome.append((cx + sr * 0.52, scy + sr * 0.92))
    dome.append((cx - sr * 0.52, scy + sr * 0.92))
    dome.append((cx - sr * 0.84, scy + sr * 0.44))
    dpts = [(int(x), int(y)) for x, y in dome]
    pygame.draw.polygon(surf, INK, dpts)
    pygame.draw.polygon(surf, BONE, dpts)
    # cylinder-style right-flank shade (keeps the warm ivory dominant, adds round)
    pygame.draw.polygon(surf, BONE_D,
                        [(int(cx + sr * 0.2), int(scy - sr * 0.9)),
                         (int(cx + sr * 1.16), int(scy - sr * 0.1)),
                         (int(cx + sr * 0.66), int(scy + sr * 0.7)),
                         (int(cx + sr * 0.2), int(scy + sr * 0.5))])
    # a thin top-left sheen rail (BONE_D->sheen kept narrow — no white blowout)
    pygame.draw.polygon(surf, BONE_SH,
                        [(int(cx - sr * 0.96), int(scy - sr * 0.2)),
                         (int(cx - sr * 0.46), int(scy - sr * 0.9)),
                         (int(cx - sr * 0.34), int(scy - sr * 0.5)),
                         (int(cx - sr * 0.74), int(scy + sr * 0.02))])
    pygame.draw.polygon(surf, INK, dpts, ow)
    # brow ridge — a strong dark bar so the eye-sockets read as a SKULL
    pygame.draw.line(surf, BONE_DD, (cx - int(sr * 0.66), scy - int(sr * 0.06)),
                     (cx + int(sr * 0.66), scy - int(sr * 0.06)), max(2, int(2.2 * ss)))
    # the two eye-sockets: CRISP deep ink wells with a contained cyan soul iris.
    # WHY no additive bloom here: an additive glow drawn onto the supersampled bone
    # whited out the whole face into one disc. The soul GLOW is laid post-scale by
    # lay_soul_flame so it lights the gap without erasing the skull. These stay as
    # hard-edged painted wells so the SKULL reads at 58px.
    sockets = []
    for sgn in (-1, 1):
        ex = cx + sgn * int(sr * 0.42)
        ey = scy + int(sr * 0.18)
        er = int(sr * 0.34)
        pygame.draw.circle(surf, INK, (ex, ey), er + max(1, int(ss)))
        pygame.draw.circle(surf, CYAN_D, (ex, ey), er)
        pygame.draw.circle(surf, CYAN, (ex, ey + int(er * 0.16)), int(er * 0.66))
        pygame.draw.circle(surf, CYAN_BR,
                           (ex - int(er * 0.12), ey - int(er * 0.06)),
                           max(1, int(er * 0.38)))
        # the soul GUTTERS down out of the lower socket rim — a short hot tongue
        pygame.draw.circle(surf, CYAN, (ex, ey + int(er * 0.9)), max(1, int(er * 0.4)))
        sockets.append((ex, ey + int(er * 0.9)))
    # nasal pit + a short clenched tooth row so it reads SKULL at the cap
    pygame.draw.polygon(surf, INK, [(cx, scy + int(sr * 0.34)),
                                    (cx - int(sr * 0.12), scy + int(sr * 0.58)),
                                    (cx + int(sr * 0.12), scy + int(sr * 0.58))])
    ty = scy + int(sr * 0.78)
    pygame.draw.line(surf, BONE_DD, (cx - int(sr * 0.38), ty),
                     (cx + int(sr * 0.38), ty), max(1, int(1.4 * ss)))
    for j in range(-2, 3):
        gx = cx + int(j * sr * 0.19)
        pygame.draw.line(surf, BONE_DD, (gx, ty - int(sr * 0.06)),
                         (gx, ty + int(sr * 0.16)), max(1, int(ss)))
    # a single crown wisdom-gem (the soul reliquary), seated high above the brow
    _facet_gem(surf, cx, scy - int(sr * 0.70), int(3.0 * ss), PURPLE, ss)
    return sockets


# ── assemble ONE tile (top OR bottom half) at supersample, then downscale ─────
def build_half(height_px, ss, *, flip):
    """Render one bone-candle half (sconce + slumped body) at supersample, return
    the smoothscaled 58px-wide tile + the socket centres (in tile coords) so the
    soul-flame glow can be laid into the gap after scaling."""
    bw = PIPE_W * ss
    bh = max(2, height_px * ss)
    big = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cap_y = draw_candle_column(big, bw, bh, ss)
    sockets = draw_flame_skull_sconce(big, bw, cap_y, ss)
    small = pygame.transform.smoothscale(big, (PIPE_W, height_px))
    small = grow_outline(small, INK + (255,), 1)
    sock_tile = [(sx / ss, sy / ss) for (sx, sy) in sockets]
    if flip:
        small = pygame.transform.flip(small, False, True)
        sock_tile = [(sx, height_px - sy) for (sx, sy) in sock_tile]
    return small, sock_tile


def lay_soul_flame(surf, ox, oy, sockets, *, into_down, intensity=1.0):
    """Lay the guttering cyan soul-flame from each socket INTO the gap (additive).
    `into_down` streams the flame downward (a bottom-of-gap cap looking up streams
    UP). This is pure light — no collision mass — so it lights the lane without
    touching the honest wall edge."""
    direction = 1 if into_down else -1
    # a soft pooled wash where both tongues meet in the lane — the lane-lighting.
    # WHY a single low-alpha blob in pure CYAN: stacking many additive glows
    # saturates to white and erases the cyan hue; one gentle wash keeps the lane
    # tinted cyan without blowing out. Seated WELL into the gap, clear of the skull.
    # WHY the flame CLEARS the cranium: the eye-sockets sit mid-face, so a tongue
    # rising/falling straight out of them would wash over the crown/jaw and erase
    # the skull. The soul-flame instead arcs OUT past the gap-facing edge of the
    # skull (clearance) and pools in OPEN sky in the lane — lighting Pip's path
    # while the skull face below stays fully read-clear.
    clear = 16 * intensity
    midx = sum(s[0] for s in sockets) / len(sockets)
    midy = sum(s[1] for s in sockets) / len(sockets) + direction * (clear + 14 * intensity)
    wash = radial_glow(int(13 * intensity), CYAN, 34)
    surf.blit(wash, (int(ox + midx - 13 * intensity), int(oy + midy - 13 * intensity)),
              special_flags=pygame.BLEND_RGBA_ADD)
    for (sx, sy) in sockets:
        # the tongue starts at the gap-facing skull edge (past `clear`), pulling in
        # toward the lane centre as it rises — two soul-tongues meeting in the gap.
        for k in range(5):
            t = k / 4.0
            fy = sy + direction * (clear + t * 18)
            fx = sx + (midx - sx) * (0.3 + 0.7 * t)
            fr = max(2, int((6 - t * 4) * intensity))
            g = radial_glow(fr, CYAN, int(64 * (1 - t * 0.6)))
            surf.blit(g, (int(ox + fx - fr), int(oy + fy - fr)),
                      special_flags=pygame.BLEND_RGBA_ADD)


# ── biome panel: a top + bottom half framing a real gap, soul-flame in lane ───
def biome_panel(sheet, x, y, w, h, sky_t, sky_b, *, label, dim=False):
    vgrad(sheet, (x, y, w, h), sky_t, sky_b)
    pygame.draw.rect(sheet, INK, (x, y, w, h), 1)
    # a couple of soft day clouds so the "busy sky" read is honest
    if not dim:
        for (cxp, cyp, cr) in ((x + 28, y + 40, 16), (x + w - 36, y + 80, 13),
                               (x + 50, y + 150, 12)):
            cl = pygame.Surface((cr * 4, cr * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(cl, (255, 255, 255, 80), cl.get_rect())
            sheet.blit(cl, (cxp - cr * 2, cyp - cr))

    gap = 132
    col_x = x + w // 2 - PIPE_W // 2
    top_h = (h - gap) // 2 + 8
    bot_h = h - gap - top_h
    ss = 5
    top_tile, top_sock = build_half(top_h, ss, flip=True)
    bot_tile, bot_sock = build_half(bot_h, ss, flip=False)
    top_y = y
    bot_y = y + top_h + gap
    sheet.blit(top_tile, (col_x, top_y))
    sheet.blit(bot_tile, (col_x, bot_y))
    inten = 0.8 if dim else 1.0
    lay_soul_flame(sheet, col_x, top_y, top_sock, into_down=True, intensity=inten)
    lay_soul_flame(sheet, col_x, bot_y, bot_sock, into_down=False, intensity=inten)
    sheet.blit(font(15).render(label, True, LABEL if not dim else LABEL_DIM),
               (x + 8, y + 6))


def main():
    W, H = 1000, 880
    sheet = pygame.Surface((W, H))
    sheet.fill(BG)
    f_title = font(26)
    f = font(16)
    f_sm = font(13)
    sheet.blit(f_title.render("BONE-CANDLE drip-column  —  clown event  —  round 1",
                              True, LABEL), (20, 16))
    sheet.blit(f_sm.render("the GROWN / asymmetric outlier of the bone roster: melted-wax slump, "
                           "alternating drip-lobes, gold wax-runnels, guttering flame-skull sconce",
                           True, LABEL_DIM), (20, 50))

    # ── HERO: day + night full-height gap pairs ──
    biome_panel(sheet, 24, 80, 300, 470, DAY_SKY_T, DAY_SKY_B, label="DAY")
    biome_panel(sheet, 340, 80, 300, 470, NIGHT_T, NIGHT_B, label="NIGHT", dim=True)

    # ── PILLAR-FIT strip: a tall bottom-half showing the slump tiles down a run ──
    px = 664
    pygame.draw.rect(sheet, PANEL, (px, 80, W - px - 16, 470))
    sheet.blit(f.render("FULL-HEIGHT FIT", True, LABEL), (px + 14, 90))
    sheet.blit(f_sm.render("body tiles via the sine-bulge;", True, LABEL_DIM), (px + 14, 112))
    sheet.blit(f_sm.render("honest wall edge stays clean", True, LABEL_DIM), (px + 14, 128))
    fit_x = px + 70
    fit_y = 150
    fit_h = 380
    vgrad(sheet, (fit_x, fit_y, PIPE_W, fit_h), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (fit_x, fit_y, PIPE_W, fit_h), 1)
    tall, tall_sock = build_half(fit_h, 5, flip=False)
    sheet.blit(tall, (fit_x, fit_y))
    lay_soul_flame(sheet, fit_x, fit_y, tall_sock, into_down=False)
    # honest collision-edge marker: a thin red line at the flat cap base
    pygame.draw.line(sheet, (236, 84, 84),
                     (fit_x - 10, fit_y + 18), (fit_x + PIPE_W + 10, fit_y + 18), 2)
    sheet.blit(f_sm.render("honest collision edge", True, (244, 150, 150)),
               (px + 6, fit_y + fit_h + 6))

    # ── 1x IN-GAME SIZE: true 58px-wide gameplay crops on a busy day sky ──
    yrow = 568
    pygame.draw.line(sheet, (90, 96, 112), (20, yrow), (W - 20, yrow), 1)
    sheet.blit(f.render("1x  IN-GAME SIZE  (player view, true 58px tile on a busy day sky)",
                        True, LABEL), (20, yrow + 8))
    # a single 58px gap-pair shown at exact 1x, no scaling, on the day gradient.
    cx0 = 40
    cy0 = yrow + 40
    cw, ch = 200, 270
    vgrad(sheet, (cx0, cy0, cw, ch), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (cx0, cy0, cw, ch), 1)
    for (clx, cly, clr) in ((cx0 + 30, cy0 + 30, 14), (cx0 + cw - 40, cy0 + 70, 11),
                            (cx0 + 50, cy0 + 200, 12)):
        cl = pygame.Surface((clr * 4, clr * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(cl, (255, 255, 255, 80), cl.get_rect())
        sheet.blit(cl, (clx - clr * 2, cly - clr))
    g1 = 96
    colx = cx0 + cw // 2 - PIPE_W // 2
    th = (ch - g1) // 2
    bh1 = ch - g1 - th
    t_tile, t_sock = build_half(th, 5, flip=True)
    b_tile, b_sock = build_half(bh1, 5, flip=False)
    sheet.blit(t_tile, (colx, cy0))
    sheet.blit(b_tile, (colx, cy0 + th + g1))
    lay_soul_flame(sheet, colx, cy0, t_sock, into_down=True)
    lay_soul_flame(sheet, colx, cy0 + th + g1, b_sock, into_down=False)
    sheet.blit(f_sm.render("58px gap-pair @ 1x", True, LABEL_DIM), (cx0, cy0 + ch + 6))

    # a column of single 1x sconce crops at different heights — reads at size?
    sx = cx0 + cw + 50
    sheet.blit(f_sm.render("1x sconce reads SOLID at size:", True, LABEL_DIM),
               (sx, cy0 - 2))
    hh = 14
    for i, hgt in enumerate((150, 110, 200)):
        bx = sx + i * 78
        vgrad(sheet, (bx, cy0 + 16, PIPE_W, ch - 30), DAY_SKY_T, DAY_SKY_B)
        pygame.draw.rect(sheet, INK, (bx, cy0 + 16, PIPE_W, ch - 30), 1)
        tile, sock = build_half(min(hgt, ch - 30), 5, flip=False)
        sheet.blit(tile, (bx, cy0 + 16))
        lay_soul_flame(sheet, bx, cy0 + 16, sock, into_down=False)
        sheet.blit(f_sm.render(f"h={hgt}", True, LABEL_DIM), (bx, cy0 + ch - 8))

    # a value-check strip: the tile silhouette in flat INK, proving it reads solid
    vx = sx + 3 * 78 + 24
    sheet.blit(f_sm.render("silhouette", True, LABEL_DIM), (vx, cy0 - 2))
    vgrad(sheet, (vx, cy0 + 16, PIPE_W, ch - 30), DAY_SKY_T, DAY_SKY_B)
    sil, _ = build_half(ch - 30, 5, flip=False)
    mask = pygame.mask.from_surface(sil)
    sil_s = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
    sheet.blit(sil_s, (vx, cy0 + 16))
    pygame.draw.rect(sheet, INK, (vx, cy0 + 16, PIPE_W, ch - 30), 1)

    out = os.path.join(_HERE, "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
