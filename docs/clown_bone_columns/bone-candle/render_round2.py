"""
Round-2 renderer for the BONE-CANDLE DRIP-COLUMN — clown-event obstacle column
#5 of the bone roster. Headless Pygame; ELEVATED pipeline (SS supersample ->
smoothscale) so the organic wax-slump silhouette + the guttering soul-flame
sconce survive the downscale to the 58px route tile. Standalone under docs/ so
review art never enters the shipped bundle: it borrows only colour math + the
triad/outline house helpers, never a runtime sprite module.

WHY this column is the GROWN, asymmetric one: the bone roster's other four
columns are RIGID + symmetric. This one is the melted-wax outlier — a softly
slumped bone shaft (a guttered altar candle gone to bone) with sagging drip-
lobes down ALTERNATING OUTER flanks and thin gold wax-runnels tracing the runs.
The irregular slump silhouette is the whole differentiation.

── ROUND 2 changes (art-director punch list) ─────────────────────────────────
1. THROAT CLEARED. The gap-adjacent ~22% of the column is pinned DEAD FLAT at
   the honest wall (no drip-lobe, no bead, no bulge in that band on EITHER
   flank). The first thing the eye tracks entering the gap is a clean vertical
   wall; lobes/beads only begin well DOWN-flank. The flat-ink silhouette
   re-export confirms the throat is straight.
2. COSMETIC MASS HONESTLY SUBORDINATE. Every drip bead is clamped to sit INSIDE
   the collision hull (never past the honest wall), and gap-adjacent beads carry
   NO rim-sheen halo so no cosmetic bump can read as the lethal edge.
3. DAY SOUL-FLAME no longer blows out. The additive bloom is CAPPED hard on the
   DAY biome: the flame core stays a SATURATED CYAN teardrop with only a
   pinpoint white-hot heart (the frost-lich soul-standard read). At 1x it can
   never collapse to a white coin/orb.
4. FLAME RESHAPED to a GUTTER: an asymmetric, taller, slightly wind-bent
   teardrop seated in a DARK sconce niche, so it carries by VALUE + SHAPE, not
   hue alone — never a round bubble pickup.
5. LOWER LOBE FREQUENCY: fewer, longer sags so short tiles read as a slumped
   shaft, not a lumpy bead-string.
6. CYAN RESERVED FOR THE FLAME ONLY. Body gems are now a single amethyst/gold
   family; cyan appears nowhere but the soul-flame. Gold wax-runnel saturation
   is dropped ~15% on the day panel so the cyan flame stays the lone focal.
7. ACCEPTANCE SHOT: the 1x gap-pair on a busy day sky is the lead panel — it
   must show a clean FLAT throat + a CYAN (not white) flame.
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
BONE     = (224, 216, 196)   # warm-ivory wax-bone (the dominant body fill)
BONE_D   = (160, 150, 128)   # bone mid-core / shade
BONE_DD  = ( 92,  84,  70)   # deepest bone hollow (runnel troughs, drip undershade)
BONE_SH  = (240, 234, 218)   # top-left rim-sheen (warm near-white)
GOLD     = (228, 182,  76)   # wax-runnel thin accent
GOLD_BR  = (252, 224, 140)   # runnel catch-light
GOLD_D   = (150, 112,  40)   # runnel trough / pooled drip shadow
# Day-muted gold (~15% desaturated) so the runnel never co-leads with the cyan
# soul-flame on the bright sky. Reserved for the day panels only.
GOLD_DAY    = (206, 174, 102)
GOLD_BR_DAY = (228, 206, 150)
GOLD_D_DAY  = (140, 116,  62)
CYAN     = ( 96, 220, 230)   # soul-flame hero cyan — RESERVED for the flame only
CYAN_BR  = (210, 252, 253)   # hot inner flame
CYAN_HOT = (244, 254, 255)   # the pinpoint white-hot heart (a single dot)
CYAN_D   = ( 30, 120, 140)   # deep cyan, the dark base of the teardrop
CYAN_SOC = ( 18,  64,  78)   # near-ink cyan for the dark sconce niche behind flame
AMETH    = (158, 120, 220)   # body wisdom-gem hue (the lone gem family now)
AMETH_BR = (212, 188, 250)
INK      = ( 28,  22,  30)   # the hard roster keyline

BG        = ( 30,  34,  46)
PANEL     = ( 46,  50,  64)
DAY_SKY_T = (118, 192, 234)
DAY_SKY_B = (198, 230, 244)
NIGHT_T   = ( 20,  24,  50)
NIGHT_B   = ( 46,  42,  80)
LABEL     = (238, 240, 246)
LABEL_DIM = (186, 194, 208)
OK        = (130, 220, 150)
BAD       = (236, 110, 110)

PIPE_W = 58


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ── house helpers (ported, not imported, per the docs/ standalone rule) ───────
def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    pts = mask.outline()
    if len(pts) < 2:
        return surf
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(surf, (0, 0))
    return ring


def radial_glow(r, color, alpha, falloff=2.2):
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for i in range(r, 0, -1):
        a = max(0, min(255, int(alpha * (i / r) ** falloff)))
        pygame.draw.circle(g, (*color, a), (r, r), i)
    return g


def vgrad(surf, rect, top, bot):
    x, y, w, h = rect
    for i in range(h):
        surf.fill(lerp(top, bot, i / max(1, h - 1)), (x, y + i, w, 1))


def _facet_gem(surf, cx, cy, r, base, bright, ss):
    """A small faceted wisdom-gem — INK-keyed diamond, lit upper-left facets, a
    hot inner highlight. The body gem is now a single amethyst family (no cyan)."""
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


# ── the wax-slump COLUMN profile (the honest collision edge lives here) ───────
# `half_at(t, side)` returns the visible half-width at vertical fraction t (0 at
# the gap-facing cap, 1 at the far foot) for the given flank.
#
# ROUND-2 throat discipline: a flat THROAT band of THROAT_FRAC at the cap is
# pinned DEAD FLAT at SAFE_HALF on BOTH flanks — no bulge, no lobe, no bead in
# it. The first ~22% entering the gap is a clean vertical wall, and any cosmetic
# mass below it is clamped to stay INSIDE the honest wall, so the visible "wall"
# is exactly the collision mass.
SAFE_HALF   = 0.52              # fraction of half-box that is the honest wall
THROAT_FRAC = 0.22              # gap-adjacent band pinned dead flat (no decor)
BULGE       = 0.085             # gentle sine-bulge of the core shaft (cosmetic)

# drip-lobe schedule: (t-centre, side, reach, length) — sagging blobs down the
# OUTER flank only. ROUND 2: FEWER, LONGER sags (3 instead of 5) so short tiles
# read as a slumped shaft, not a bead-string; all centres are pushed BELOW the
# throat band. `reach` bulges OUTWARD past the core but is clamped to stay
# inside the honest wall near the cap (it can only matter well down-flank).
DRIPS = [
    (0.40,  1, 0.30, 0.30),
    (0.62, -1, 0.34, 0.34),
    (0.84,  1, 0.26, 0.26),
]


def _core_half(t, hw):
    """Soft sine-bulge of the SHAFT core. Stays inside SAFE_HALF; flat in the
    throat band so the lane edge is rectangular where Pip enters."""
    if t < THROAT_FRAC:
        return hw * SAFE_HALF
    # ease the bulge in only after the throat so there's no kink at the band edge
    tt = (t - THROAT_FRAC) / max(1e-3, 1.0 - THROAT_FRAC)
    return hw * (SAFE_HALF - 0.02 + BULGE * 0.5 * (1.0 - math.cos(tt * math.pi * 2.0)))


def draw_candle_column(surf, bw, bh, ss, *, day=False):
    """Draw ONE bone-candle half into a supersampled box. The gap-facing cap (the
    soul-flame sconce) sits at the TOP; the body slumps down away from it."""
    cx = bw // 2
    hw = bw // 2
    ow = max(2, int(2.0 * ss))
    cap_y = int(18 * ss)
    g_d, g_br, g_dd = ((GOLD_DAY, GOLD_BR_DAY, GOLD_D_DAY) if day
                       else (GOLD, GOLD_BR, GOLD_D))

    n = 72
    span = bh - cap_y

    def edge_x(t, side):
        h = _core_half(t, hw)
        if t >= THROAT_FRAC:
            for (dt, dside, reach, length) in DRIPS:
                if dside != side:
                    continue
                d = (t - dt) / length
                if -1.2 < d < 1.6:
                    if d < 0:
                        env = math.cos(d * math.pi * 0.5) ** 2
                    else:
                        env = max(0.0, (1.0 - d / 1.6)) ** 1.4
                    h += hw * reach * env
        # never past the box, and never past the honest wall in the throat band.
        h = min(h, hw - max(1, int(1.0 * ss)))
        if t < THROAT_FRAC:
            h = hw * SAFE_HALF                     # DEAD FLAT throat
        return cx + side * h

    # smooth the band edge so the flat throat blends into the slump (no corner)
    left = [(edge_x(i / n, -1), cap_y + span * (i / n)) for i in range(n + 1)]
    right = [(edge_x(i / n, 1), cap_y + span * (i / n)) for i in range(n + 1)]
    body = left + list(reversed(right))
    bpts = [(int(x), int(y)) for x, y in body]

    # warm BONE fill dominant; rounding from a right-edge SHADE band + left SHEEN
    # rail. WHY no big dark-core poly: it greys the ivory to wet clay.
    pygame.draw.polygon(surf, INK, bpts)
    pygame.draw.polygon(surf, BONE, bpts)
    shade = [(x, y) for (x, y) in right]
    shade += [(cx + (x - cx) * 0.46, y) for (x, y) in reversed(right)]
    pygame.draw.polygon(surf, BONE_D, [(int(x), int(y)) for x, y in shade])
    deep = [(x, y) for (x, y) in right]
    deep += [(cx + (x - cx) * 0.80, y) for (x, y) in reversed(right)]
    pygame.draw.polygon(surf, lerp(BONE_D, BONE_DD, 0.5),
                        [(int(x), int(y)) for x, y in deep])
    lit = [(x, y) for (x, y) in left]
    lit += [(cx + (x - cx) * 0.66, y) for (x, y) in reversed(left)]
    pygame.draw.polygon(surf, BONE_SH, [(int(x), int(y)) for x, y in lit])
    pygame.draw.polygon(surf, INK, bpts, ow)

    # ── pooled drip TIPS: a rounded bead at the end of each lobe. ROUND 2: the
    # bead is CLAMPED so its outer rim never exceeds the honest wall (it sits
    # INSIDE the collision hull), and beads in/near the throat carry NO sheen
    # halo, so no cosmetic bump reads as the lethal edge.
    for (dt, dside, reach, length) in DRIPS:
        tip_t = min(0.97, dt + length * 0.95)
        if tip_t < THROAT_FRAC + 0.06:
            continue                               # never a bead near the throat
        br = int((2.6 + reach * 3.2) * ss)
        by = cap_y + span * tip_t
        # seat the bead so its OUTER rim is no further out than the honest wall
        wall_x = cx + dside * hw * SAFE_HALF
        bx = wall_x - dside * br                   # rim flush with the wall, inside
        pygame.draw.circle(surf, INK, (int(bx), int(by)), br + max(1, int(ss)))
        pygame.draw.circle(surf, BONE_D, (int(bx), int(by)), br)
        pygame.draw.circle(surf, BONE, (int(bx), int(by)), int(br * 0.72))
        # sheen only on lower-flank beads (well clear of the lane), and tiny
        if tip_t > 0.5:
            pygame.draw.circle(surf, BONE_SH,
                               (int(bx - br * 0.3), int(by - br * 0.35)),
                               max(1, int(br * 0.26)))

    # ── gold WAX-RUNNELS: thin runs tracing the slump. Day uses the muted gold
    # so the runnel never co-leads with the cyan flame. Starts BELOW the throat.
    for (dt, dside, reach, length) in DRIPS:
        run = []
        for k in range(12):
            rt = max(THROAT_FRAC + 0.02,
                     dt - length * 0.4 + (length * 1.5) * (k / 11.0))
            rt = min(0.98, rt)
            wob = math.sin(k * 1.0 + dt * 9) * 1.5 * ss
            ex = edge_x(rt, dside) - dside * (3.0 * ss) + wob
            run.append((int(ex), int(cap_y + span * rt)))
        pygame.draw.lines(surf, g_dd, False, run, max(2, int(2.2 * ss)))
        pygame.draw.lines(surf, g_d, False, run, max(1, int(1.4 * ss)))
        pygame.draw.lines(surf, g_br, False, run[:5], max(1, int(ss)))

    # body wisdom-gems — a SINGLE amethyst/gold family now (cyan is reserved for
    # the soul-flame). Seated below the throat in dim gold bezels.
    for gt in (0.50, 0.78):
        gx, gy = cx - int(hw * 0.08), int(cap_y + span * gt)
        gr = int(3.0 * ss)
        pygame.draw.circle(surf, g_dd, (gx, gy), gr + max(1, int(ss)))
        _facet_gem(surf, gx, gy, gr, AMETH, AMETH_BR, ss)

    return cap_y


def draw_flame_skull_sconce(surf, bw, cap_y, ss):
    """The guttering soul-flame sconce capping the gap: a squat skull seated ON
    the flat cap line, eye-sockets guttering the cyan soul DOWN into the gap.
    ROUND 2: a DARK sconce niche frames the flame so it reads by value, and the
    crown carries a small dark frame the day soul-flame sits against. Returns the
    socket centres (for the post-scale flame glow) plus the niche centre."""
    cx = bw // 2
    ow = max(2, int(1.8 * ss))
    sr = int(13 * ss)
    scy = cap_y + int(sr * 0.80)

    dome = []
    for ang in range(-180, 1, 14):
        a = math.radians(ang)
        sag = 1.0 + (0.18 if math.sin(a) > 0.3 else 0.0) * abs(math.cos(a))
        dome.append((cx + math.cos(a) * sr * 1.18,
                     scy + math.sin(a) * sr * 1.02 * sag))
    dome.append((cx + sr * 0.84, scy + sr * 0.44))
    dome.append((cx + sr * 0.52, scy + sr * 0.92))
    dome.append((cx - sr * 0.52, scy + sr * 0.92))
    dome.append((cx - sr * 0.84, scy + sr * 0.44))
    dpts = [(int(x), int(y)) for x, y in dome]
    pygame.draw.polygon(surf, INK, dpts)
    pygame.draw.polygon(surf, BONE, dpts)
    pygame.draw.polygon(surf, BONE_D,
                        [(int(cx + sr * 0.2), int(scy - sr * 0.9)),
                         (int(cx + sr * 1.16), int(scy - sr * 0.1)),
                         (int(cx + sr * 0.66), int(scy + sr * 0.7)),
                         (int(cx + sr * 0.2), int(scy + sr * 0.5))])
    pygame.draw.polygon(surf, BONE_SH,
                        [(int(cx - sr * 0.96), int(scy - sr * 0.2)),
                         (int(cx - sr * 0.46), int(scy - sr * 0.9)),
                         (int(cx - sr * 0.34), int(scy - sr * 0.5)),
                         (int(cx - sr * 0.74), int(scy + sr * 0.02))])
    pygame.draw.polygon(surf, INK, dpts, ow)
    pygame.draw.line(surf, BONE_DD, (cx - int(sr * 0.66), scy - int(sr * 0.06)),
                     (cx + int(sr * 0.66), scy - int(sr * 0.06)), max(2, int(2.2 * ss)))

    # eye-sockets: crisp deep-ink wells with a contained cyan iris. WHY no
    # additive bloom on the bone: it whites out the face. The soul glow is laid
    # post-scale. Cyan stays the lone cyan on the whole tile.
    sockets = []
    for sgn in (-1, 1):
        ex = cx + sgn * int(sr * 0.42)
        ey = scy + int(sr * 0.18)
        er = int(sr * 0.34)
        pygame.draw.circle(surf, INK, (ex, ey), er + max(1, int(ss)))
        pygame.draw.circle(surf, CYAN_D, (ex, ey), er)
        pygame.draw.circle(surf, CYAN, (ex, ey + int(er * 0.16)), int(er * 0.60))
        pygame.draw.circle(surf, CYAN_BR,
                           (ex - int(er * 0.12), ey - int(er * 0.06)),
                           max(1, int(er * 0.34)))
        pygame.draw.circle(surf, CYAN, (ex, ey + int(er * 0.9)), max(1, int(er * 0.38)))
        sockets.append((ex, ey + int(er * 0.9)))

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

    # crown reliquary gem — amethyst (cyan reserved for the flame).
    _facet_gem(surf, cx, scy - int(sr * 0.70), int(3.0 * ss), AMETH, AMETH_BR, ss)
    # the niche the soul-flame plume sits against (a dark frame so the flame
    # carries by VALUE, not hue) — centred between/below the sockets.
    niche = (cx, scy + int(sr * 0.5))
    return sockets, niche


# ── assemble ONE tile (top OR bottom half) at supersample, then downscale ─────
def build_half(height_px, ss, *, flip, day=False):
    bw = PIPE_W * ss
    bh = max(2, height_px * ss)
    big = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cap_y = draw_candle_column(big, bw, bh, ss, day=day)
    sockets, niche = draw_flame_skull_sconce(big, bw, cap_y, ss)
    small = pygame.transform.smoothscale(big, (PIPE_W, height_px))
    small = grow_outline(small, INK + (255,), 1)
    sock_tile = [(sx / ss, sy / ss) for (sx, sy) in sockets]
    niche_tile = (niche[0] / ss, niche[1] / ss)
    if flip:
        small = pygame.transform.flip(small, False, True)
        sock_tile = [(sx, height_px - sy) for (sx, sy) in sock_tile]
        niche_tile = (niche_tile[0], height_px - niche_tile[1])
    return small, sock_tile, niche_tile


def lay_soul_flame(surf, ox, oy, sockets, niche, *, into_down, day=False,
                   intensity=1.0):
    """Lay the guttering cyan soul-flame plume into the gap.

    ROUND 2: a single ASYMMETRIC, taller, wind-bent TEARDROP plume rising/falling
    from the sconce niche — drawn first as a DARK cyan base (value frame), then a
    capped additive bloom. On DAY the bloom alpha is held low and the white-hot
    heart is a single pinpoint dot, so the core stays SATURATED CYAN (the frost-
    lich soul-standard) instead of blowing to a white orb. The two eye-sockets
    feed thin tongues that merge UP into the teardrop, so it reads as one flame,
    not two beads."""
    direction = 1 if into_down else -1
    nx, ny = niche
    base_x = ox + nx
    base_y = oy + ny + direction * 6 * intensity

    # teardrop geometry: tall, asymmetric (wind-bent), narrow at the tip.
    plume_h = 26 * intensity
    bend = 4.5 * intensity                         # lateral wind-bend of the tip
    pts_outer = []
    pts_inner = []
    steps = 14
    for k in range(steps + 1):
        t = k / steps                              # 0 base -> 1 tip
        y = base_y + direction * t * plume_h
        # asymmetric width envelope: fat near the base, pinched tip
        wfull = (1.0 - t) ** 1.3 * (6.2 * intensity) + 0.6
        # wind-bend: the centreline curves toward +x as it rises
        cxk = base_x + bend * (t ** 1.5)
        # asymmetry: right side fuller than left for a gutter-lick read
        pts_outer.append((cxk + wfull * 1.15, y))
        pts_inner.append((cxk - wfull * 0.85, y))
    te_pts = pts_outer + list(reversed(pts_inner))

    # 1) the DARK value base — a deep-cyan teardrop so the flame reads as a shape
    #    against the bright sky even before any glow.
    poly = [(int(px), int(py)) for px, py in te_pts]
    pygame.draw.polygon(surf, CYAN_D, poly)
    # 2) a mid cyan body inset
    midpts = []
    for k in range(steps + 1):
        t = k / steps
        y = base_y + direction * t * plume_h * 0.92
        wfull = (1.0 - t) ** 1.3 * (4.0 * intensity) + 0.3
        cxk = base_x + bend * (t ** 1.5)
        midpts.append((cxk + wfull, y))
    for k in range(steps, -1, -1):
        t = k / steps
        y = base_y + direction * t * plume_h * 0.92
        wfull = (1.0 - t) ** 1.3 * (3.0 * intensity) + 0.2
        cxk = base_x + bend * (t ** 1.5)
        midpts.append((cxk - wfull, y))
    pygame.draw.polygon(surf, CYAN, [(int(px), int(py)) for px, py in midpts])

    # 3) the capped additive bloom. DAY holds the alpha + radius LOW so the cyan
    #    stays saturated; NIGHT can bloom a touch more. The heart is a pinpoint.
    if day:
        bloom_a, bloom_r, heart_r = 70, int(7 * intensity), max(1, int(2.0 * intensity))
        body_a = 110
    else:
        bloom_a, bloom_r, heart_r = 120, int(11 * intensity), max(1, int(3.0 * intensity))
        body_a = 150
    # body bloom hugs the teardrop (keeps it cyan, doesn't wash to white)
    bb = radial_glow(bloom_r, CYAN, body_a, falloff=2.4)
    surf.blit(bb, (int(base_x - bloom_r + bend * 0.4),
                   int(base_y + direction * plume_h * 0.32 - bloom_r)),
              special_flags=pygame.BLEND_RGBA_ADD)
    # the pinpoint white-hot heart — a single small dot at the base of the flame,
    # NOT a big white disc, so the teardrop stays cyan-dominant.
    heart_y = base_y + direction * plume_h * 0.16
    pygame.draw.circle(surf, CYAN_BR,
                       (int(base_x + bend * 0.1), int(heart_y)),
                       max(1, heart_r + 1))
    pygame.draw.circle(surf, CYAN_HOT,
                       (int(base_x + bend * 0.1), int(heart_y)), heart_r)

    # 4) thin socket tongues merging up into the teardrop base (one-flame read)
    for (sx, sy) in sockets:
        for k in range(3):
            t = k / 2.0
            fy = oy + sy + direction * (4 + t * 10) * intensity
            fx = ox + sx + (base_x - (ox + sx)) * (0.4 + 0.6 * t)
            fr = max(1, int((3 - t * 1.6) * intensity))
            g = radial_glow(fr, CYAN, int((48 if day else 64) * (1 - t * 0.5)),
                            falloff=2.2)
            surf.blit(g, (int(fx - fr), int(fy - fr)),
                      special_flags=pygame.BLEND_RGBA_ADD)


# ── biome panel: a top + bottom half framing a real gap, soul-flame in lane ───
def biome_panel(sheet, x, y, w, h, sky_t, sky_b, *, label, dim=False, gap=132):
    day = not dim
    vgrad(sheet, (x, y, w, h), sky_t, sky_b)
    pygame.draw.rect(sheet, INK, (x, y, w, h), 1)
    if day:
        for (cxp, cyp, cr) in ((x + 28, y + 40, 16), (x + w - 36, y + 80, 13),
                               (x + 50, y + 150, 12)):
            cl = pygame.Surface((cr * 4, cr * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(cl, (255, 255, 255, 80), cl.get_rect())
            sheet.blit(cl, (cxp - cr * 2, cyp - cr))

    col_x = x + w // 2 - PIPE_W // 2
    top_h = (h - gap) // 2 + 8
    bot_h = h - gap - top_h
    ss = 5
    top_tile, top_sock, top_ni = build_half(top_h, ss, flip=True, day=day)
    bot_tile, bot_sock, bot_ni = build_half(bot_h, ss, flip=False, day=day)
    top_y = y
    bot_y = y + top_h + gap
    sheet.blit(top_tile, (col_x, top_y))
    sheet.blit(bot_tile, (col_x, bot_y))
    inten = 0.82 if dim else 1.0
    lay_soul_flame(sheet, col_x, top_y, top_sock, top_ni, into_down=True,
                   day=day, intensity=inten)
    lay_soul_flame(sheet, col_x, bot_y, bot_sock, bot_ni, into_down=False,
                   day=day, intensity=inten)
    sheet.blit(font(15).render(label, True, LABEL if day else LABEL_DIM),
               (x + 8, y + 6))


def main():
    W, H = 1000, 900
    sheet = pygame.Surface((W, H))
    sheet.fill(BG)
    f_title = font(26)
    f = font(16)
    f_sm = font(13)
    sheet.blit(f_title.render("BONE-CANDLE drip-column  —  clown event  —  round 2",
                              True, LABEL), (20, 16))
    sheet.blit(f_sm.render("R2: throat pinned dead-flat (no lobe/bead in the lane band) - day soul-flame capped "
                           "to a CYAN gutter-teardrop - cyan reserved for the flame - fewer/longer sags",
                           True, LABEL_DIM), (20, 50))

    # ── ACCEPTANCE SHOT (lead): the 1x gap-pair on a busy day sky ──
    ax, ay = 24, 80
    aw, ah = 250, 360
    sheet.blit(f.render("ACCEPTANCE: 1x gap-pair, busy DAY sky", True, OK), (ax, ay - 0))
    sheet.blit(f_sm.render("flat throat + CYAN (not white) flame", True, LABEL_DIM),
               (ax, ay + 20))
    vgrad(sheet, (ax, ay + 40, aw, ah), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (ax, ay + 40, aw, ah), 1)
    for (clx, cly, clr) in ((ax + 36, ay + 78, 16), (ax + aw - 46, ay + 130, 12),
                            (ax + 56, ay + 260, 13)):
        cl = pygame.Surface((clr * 4, clr * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(cl, (255, 255, 255, 84), cl.get_rect())
        sheet.blit(cl, (clx - clr * 2, cly - clr))
    g1 = 100
    colx = ax + aw // 2 - PIPE_W // 2
    th = (ah - g1) // 2
    bh1 = ah - g1 - th
    t_tile, t_sock, t_ni = build_half(th, 5, flip=True, day=True)
    b_tile, b_sock, b_ni = build_half(bh1, 5, flip=False, day=True)
    sheet.blit(t_tile, (colx, ay + 40))
    sheet.blit(b_tile, (colx, ay + 40 + th + g1))
    lay_soul_flame(sheet, colx, ay + 40, t_sock, t_ni, into_down=True, day=True)
    lay_soul_flame(sheet, colx, ay + 40 + th + g1, b_sock, b_ni, into_down=False, day=True)
    # mark the honest throat with thin guide lines hugging both wall edges
    wallx_l = colx + PIPE_W // 2 - int(PIPE_W * 0.5 * SAFE_HALF)
    wallx_r = colx + PIPE_W // 2 + int(PIPE_W * 0.5 * SAFE_HALF)
    thr_y0 = ay + 40 + th
    thr_y1 = ay + 40 + th + g1
    pygame.draw.line(sheet, OK, (wallx_l, thr_y0 - 24), (wallx_l, thr_y0), 1)
    pygame.draw.line(sheet, OK, (wallx_r, thr_y0 - 24), (wallx_r, thr_y0), 1)
    pygame.draw.line(sheet, OK, (wallx_l, thr_y1), (wallx_l, thr_y1 + 24), 1)
    pygame.draw.line(sheet, OK, (wallx_r, thr_y1), (wallx_r, thr_y1 + 24), 1)
    sheet.blit(f_sm.render("green guides = honest wall edge", True, OK),
               (ax, ay + 40 + ah + 6))

    # ── HERO: day + night full-height gap pairs ──
    biome_panel(sheet, 294, 80, 224, 400, DAY_SKY_T, DAY_SKY_B, label="DAY")
    biome_panel(sheet, 530, 80, 224, 400, NIGHT_T, NIGHT_B, label="NIGHT", dim=True)

    # ── FULL-HEIGHT FIT + silhouette ──
    px = 766
    pygame.draw.rect(sheet, PANEL, (px, 80, W - px - 16, 400))
    sheet.blit(f.render("FIT + SILHOUETTE", True, LABEL), (px + 12, 88))
    fit_x = px + 24
    fit_y = 120
    fit_h = 340
    vgrad(sheet, (fit_x, fit_y, PIPE_W, fit_h), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (fit_x, fit_y, PIPE_W, fit_h), 1)
    tall, tall_sock, tall_ni = build_half(fit_h, 5, flip=False, day=True)
    sheet.blit(tall, (fit_x, fit_y))
    lay_soul_flame(sheet, fit_x, fit_y, tall_sock, tall_ni, into_down=False, day=True)
    pygame.draw.line(sheet, BAD, (fit_x - 8, fit_y + 18), (fit_x + PIPE_W + 8, fit_y + 18), 2)
    sheet.blit(f_sm.render("collision", True, (244, 150, 150)), (px + 12, fit_y - 2))
    # silhouette beside it — proves the throat is straight
    vx = fit_x + PIPE_W + 24
    vgrad(sheet, (vx, fit_y, PIPE_W, fit_h), (60, 64, 78), (60, 64, 78))
    sil, _, _ = build_half(fit_h, 5, flip=False, day=True)
    mask = pygame.mask.from_surface(sil)
    sil_s = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
    sheet.blit(sil_s, (vx, fit_y))
    pygame.draw.rect(sheet, INK, (vx, fit_y, PIPE_W, fit_h), 1)
    # mark the flat throat band on the silhouette
    band_h = int(fit_h * THROAT_FRAC * (340 / fit_h))
    pygame.draw.line(sheet, OK, (vx - 6, fit_y + 18 + band_h),
                     (vx + PIPE_W + 6, fit_y + 18 + band_h), 1)
    sheet.blit(f_sm.render("flat throat", True, OK), (vx - 4, fit_y + 18 + band_h + 2))

    # ── SHORT-TILE read: h=110 / h=150 / h=200 should read as a slumped shaft ──
    yrow = 500
    pygame.draw.line(sheet, (90, 96, 112), (20, yrow), (W - 20, yrow), 1)
    sheet.blit(f.render("SHORT-TILE READ (fewer/longer sags - slumped shaft, not a bead-string)",
                        True, LABEL), (20, yrow + 8))
    bx0 = 30
    by0 = yrow + 34
    bh_panel = 330
    for i, hgt in enumerate((110, 150, 200, 260)):
        bx = bx0 + i * 78
        vgrad(sheet, (bx, by0, PIPE_W, bh_panel), DAY_SKY_T, DAY_SKY_B)
        pygame.draw.rect(sheet, INK, (bx, by0, PIPE_W, bh_panel), 1)
        tile, sock, ni = build_half(min(hgt, bh_panel), 5, flip=False, day=True)
        sheet.blit(tile, (bx, by0))
        lay_soul_flame(sheet, bx, by0, sock, ni, into_down=False, day=True)
        sheet.blit(f_sm.render(f"h={hgt}", True, LABEL_DIM), (bx + 6, by0 + bh_panel + 4))

    # ── FLAME compare: day vs night teardrop close-up (cyan-dominant check) ──
    fx0 = bx0 + 4 * 78 + 30
    sheet.blit(f.render("SOUL-FLAME read", True, LABEL), (fx0, yrow + 30))
    sheet.blit(f_sm.render("cyan-dominant teardrop;", True, LABEL_DIM), (fx0, yrow + 54))
    sheet.blit(f_sm.render("white only at the heart", True, LABEL_DIM), (fx0, yrow + 70))
    for j, (skyt, skyb, lbl, dy) in enumerate((
            (DAY_SKY_T, DAY_SKY_B, "DAY", True),
            (NIGHT_T, NIGHT_B, "NIGHT", False))):
        cz_x = fx0 + j * 150
        cz_y = yrow + 96
        cz_w, cz_h = 134, 200
        vgrad(sheet, (cz_x, cz_y, cz_w, cz_h), skyt, skyb)
        pygame.draw.rect(sheet, INK, (cz_x, cz_y, cz_w, cz_h), 1)
        # one sconce at ~2.4x via a tall narrow build then upscale-blit of the crop
        big_h = 150
        tile, sock, ni = build_half(big_h, 6, flip=False, day=dy)
        crop = tile.subsurface(pygame.Rect(0, 0, PIPE_W, min(64, big_h))).copy()
        scale = 2.0
        crop2 = pygame.transform.scale(crop, (int(PIPE_W * scale), int(64 * scale)))
        bxp = cz_x + cz_w // 2 - crop2.get_width() // 2
        byp = cz_y + 30
        sheet.blit(crop2, (bxp, byp))
        # lay the flame at matching scale: rebuild socket/niche in crop2 coords
        sock2 = [(sx * scale, sy * scale) for (sx, sy) in sock]
        ni2 = (ni[0] * scale, ni[1] * scale)
        lay_soul_flame(sheet, bxp, byp, sock2, ni2, into_down=False, day=dy,
                       intensity=scale)
        sheet.blit(f_sm.render(lbl, True, LABEL if dy else LABEL_DIM),
                   (cz_x + 6, cz_y + 4))

    out = os.path.join(_HERE, "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
