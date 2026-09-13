"""
Round-1 concept renderer for SASA-YUKI-ONNA — the snow-grass drift-spirit of
the dwarf bamboo (bamboo-v2 REALISTIC set, concept #3). Headless Pygame;
ELEVATED-REALISM pipeline (supersample SS=6 -> smoothscale) so the fanned
leaf-tiers + hard powder-caps stay crisp at downscale.

WHY this set is a DEPARTURE from the chibi bamboo 1: realistic non-chibi
proportions and botanical accuracy are the whole point. The house triad is
pushed to 4-6 HARD STEPPED value bands per form (NO smooth gradients) for a
sculpted near-volumetric read that still survives at true 32px. Radial glow is
for ACCENTS only. Hard ink keyline (28,22,30) + 1px alpha-grown outline.

WHY this is the WIDE-LOW DRIFT-MOUND of the set: the cross-set KIND spread needs
exactly one broad horizontal silhouette, so Sasa-Yuki-Onna is deliberately a low
billowing MOUND of snow-laden sasa fanning out sideways — the opposite of a tall
stalk. The whole margin vs the old Yukitake lives in FLIPPED DOMINANCE: the
muted SAGE-GREEN sasa body is held as the visible mass; snow appears only as
discrete HARD powder-caps perched on each leaf-tier, NEVER a blanket. If snow
ever read dominant we'd have rebuilt Yukitake. Fanning blades are capped at
5-7 readable clumps so the mound never dissolves into fuzz at 32px. The cold
PERIWINKLE frost-glow on the face is the identity anchor (radial, face-only) —
no roster green pairs with periwinkle — and the temperature leans HARD cool
winter-spirit (the gap-widener vs #7's warm ambush spider).

WHY the single tall culm IS the pillar: a lone sasa culm rising from the mound
gives thin single-branch node-segments as the repeat band; a snow-capped
leaf-fan tuft is the detachable gap-edge cap; the drift-mound base is the lower
mirror. Wide creature at the bottom; culm tiles upward.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the triad/outline
helpers cloned from the lineage template.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief, snow-on-sage lane) ─────────────────────────
# Muted SAGE-GREEN is the dominant BODY mass (the flipped-dominance anchor);
# cool blue-white snow rides on top as discrete powder-caps only.
SAGE       = (120, 156, 118)   # muted sage-green sasa body — the DOMINANT mass
SAGE_D     = ( 78, 110,  82)   # deep node/under-leaf shade (stepped band 2)
SAGE_DD    = ( 52,  78,  62)   # deepest grove-shadow hollow (stepped band 3)
SAGE_HI    = (158, 188, 150)   # sunlit-leaf top sheen (stepped band up)
MARGIN     = (214, 220, 194)   # dry pale leaf-margin "snow-edge" necrosis (real sasa)
SNOW       = (230, 238, 244)   # snow-powder white (caps only)
SNOW_SH    = (158, 182, 206)   # blue-shadow snow (under-cap stepped band)
SNOW_HI    = (244, 248, 252)   # hottest snow sheen pip
PERI       = (176, 200, 236)   # cold periwinkle frost-glow — IDENTITY ANCHOR
PERI_HOT   = (214, 228, 250)   # hot periwinkle core
EYE_DK     = ( 70, 100, 132)   # cool slate eye-hollow (not warm)
INK        = ( 28,  22,  30)   # hard ink keyline

BG         = ( 86,  96, 104)   # neutral cool-grey review backdrop
PANEL      = ( 66,  76,  84)
DAY_SKY_T  = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B  = (196, 232, 244)
NIGHT_T    = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B    = ( 48,  44,  82)
LABEL      = (238, 240, 244)
LABEL_DIM  = (190, 196, 208)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


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


def radial_glow(radius, color, alpha_center=200, falloff=2.0):
    """Periwinkle frost-glow for the FACE accent ONLY (precedent: necrarch r3).
    Never used as a fill — additive bloom that keeps the face the cold focal."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


# ── one SASA LEAF-BLADE — broad lance, dry pale snow-edge margin, hard bands ──
def sasa_leaf(surf, root, ang, length, width, s, curl=0.0, snow_cap=True):
    """ONE broad lance sasa leaf rooted at `root`, swept along `ang`, bowed by
    `curl` (positive = droops under powder weight). Botanically a wide lance with
    a slight recurve, NOT a needle. Built as flat STEPPED value bands (no
    gradient): SAGE_D under-shade -> SAGE flat fill -> SAGE_HI top sheen ->
    MARGIN pale dry-margin "snow-edge" rim down both edges (the real winter
    sasa tell), with an optional discrete HARD snow powder-cap perched on the
    upper face near the base — never a blanket coating the whole blade."""
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca                      # perpendicular = width axis
    hw = width * 0.5
    # midrib bows: the tip pulls toward the droop direction by `curl`
    tip = (root[0] + ca * length + px * curl * length,
           root[1] + sa * length + py * curl * length)
    # belly of the lance sits ~40% out so it is widest near the base (true lance)
    bx = (root[0] + ca * length * 0.40 + px * curl * length * 0.40,
          root[1] + sa * length * 0.40 + py * curl * length * 0.40)
    # closed lance polygon: narrow root -> wide belly -> pointed recurved tip
    leaf = [
        (root[0] + px * hw * 0.30, root[1] + py * hw * 0.30),
        (bx[0]   + px * hw,        bx[1]   + py * hw),
        tip,
        (bx[0]   - px * hw,        bx[1]   - py * hw),
        (root[0] - px * hw * 0.30, root[1] - py * hw * 0.30),
    ]
    pygame.draw.polygon(surf, INK, leaf)
    pygame.draw.polygon(surf, SAGE, leaf)
    # STEPPED band: under-leaf shade on the trailing (away-from-light) half
    pygame.draw.polygon(surf, SAGE_D, [
        (root[0] - px * hw * 0.20, root[1] - py * hw * 0.20),
        (bx[0]   - px * hw * 0.92, bx[1]   - py * hw * 0.92),
        tip,
        (bx[0]   - px * hw * 0.10, bx[1]   - py * hw * 0.10),
    ])
    # STEPPED band: top-light sheen on the leading half
    pygame.draw.polygon(surf, SAGE_HI, [
        (root[0] + px * hw * 0.10, root[1] + py * hw * 0.10),
        (bx[0]   + px * hw * 0.86, bx[1]   + py * hw * 0.86),
        tip,
        (bx[0]   + px * hw * 0.16, bx[1]   + py * hw * 0.16),
    ])
    # hard midrib groove (a confident dark line, the lance's spine)
    pygame.draw.line(surf, SAGE_DD, (root[0], root[1]), tip, max(2, int(width * 0.10)))
    # dry pale "snow-edge" MARGIN rim down BOTH edges — the real winter-sasa tell,
    # a discrete pale stepped band, never a soft fade
    mw = max(2, int(width * 0.16))
    pygame.draw.line(surf, MARGIN, (bx[0] + px * hw, bx[1] + py * hw), tip, mw)
    pygame.draw.line(surf, MARGIN, (bx[0] - px * hw, bx[1] - py * hw), tip, mw)
    pygame.draw.line(surf, MARGIN,
                     (root[0] + px * hw * 0.30, root[1] + py * hw * 0.30),
                     (bx[0] + px * hw, bx[1] + py * hw), mw)
    # one discrete HARD powder-cap perched near the base of the blade-face only
    if snow_cap:
        c0 = (root[0] + ca * length * 0.22, root[1] + sa * length * 0.22)
        cw = hw * 0.78
        cl = length * 0.20
        cap = [
            (c0[0] + px * cw,             c0[1] + py * cw),
            (c0[0] + px * cw + ca * cl,   c0[1] + py * cw + sa * cl),
            (c0[0] - px * cw * 0.2 + ca * cl, c0[1] - py * cw * 0.2 + sa * cl),
            (c0[0] - px * cw * 0.6,       c0[1] - py * cw * 0.6),
        ]
        pygame.draw.polygon(surf, SNOW_SH, [(x + s * 0.4, y + s * 0.4) for (x, y) in cap])
        pygame.draw.polygon(surf, SNOW, cap)
        pygame.draw.line(surf, SNOW_HI,
                         (c0[0] + px * cw * 0.4, c0[1] + py * cw * 0.4),
                         (c0[0] + px * cw * 0.4 + ca * cl * 0.8,
                          c0[1] + py * cw * 0.4 + sa * cl * 0.8), max(1, int(width * 0.10)))
    pygame.draw.polygon(surf, INK, leaf, max(2, int(width * 0.10)))


# ── a soft cool FACE forming in the drift (periwinkle frost-glow accent) ──────
def drift_face(surf, cx, cy, r, s, lit=True):
    """A soft yuki-onna face FORMING in the snow-drift — not a hard mask: a pale
    cool oval of packed snow with two slate eye-hollows and a faint mouth, lit by
    the periwinkle frost-glow (the identity anchor, radial + face-only). Kept
    low-contrast and centred in the mound so it reads as a presence in the drift,
    not a cartoon face."""
    if lit:
        g = radial_glow(int(r * 1.7), PERI, alpha_center=150, falloff=2.2)
        surf.blit(g, (cx - g.get_width() // 2, cy - g.get_height() // 2),
                  special_flags=pygame.BLEND_ADD)
    # packed-snow face oval, hard stepped: blue-shadow under -> snow -> peri sheen
    face = [(cx - int(r * 0.92), cy - int(r * 0.30)),
            (cx - int(r * 0.66), cy - int(r * 0.86)),
            (cx, cy - int(r * 1.00)),
            (cx + int(r * 0.66), cy - int(r * 0.86)),
            (cx + int(r * 0.92), cy - int(r * 0.30)),
            (cx + int(r * 0.62), cy + int(r * 0.72)),
            (cx, cy + int(r * 0.98)),
            (cx - int(r * 0.62), cy + int(r * 0.72))]
    pygame.draw.polygon(surf, INK, face)
    pygame.draw.polygon(surf, SNOW_SH, face)
    pygame.draw.polygon(surf, SNOW, [
        (cx - int(r * 0.74), cy - int(r * 0.24)),
        (cx, cy - int(r * 0.84)),
        (cx + int(r * 0.74), cy - int(r * 0.24)),
        (cx + int(r * 0.50), cy + int(r * 0.58)),
        (cx, cy + int(r * 0.78)),
        (cx - int(r * 0.50), cy + int(r * 0.58))])
    # top-left periwinkle sheen step (cool, not warm)
    pygame.draw.polygon(surf, lerp(SNOW, PERI, 0.55), [
        (cx - int(r * 0.66), cy - int(r * 0.20)),
        (cx - int(r * 0.30), cy - int(r * 0.70)),
        (cx, cy - int(r * 0.50)),
        (cx - int(r * 0.34), cy - int(r * 0.08))])
    # two cool slate eye-hollows pinned with a periwinkle frost-pip
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.40)
        ey = cy - int(r * 0.08)
        eye = [(ex - int(r * 0.22), ey - int(r * 0.06)),
               (ex + int(r * 0.22), ey - int(r * 0.14)),
               (ex + int(r * 0.16), ey + int(r * 0.16)),
               (ex - int(r * 0.18), ey + int(r * 0.12))]
        pygame.draw.polygon(surf, INK, eye)
        pygame.draw.polygon(surf, EYE_DK, eye)
        if lit:
            pygame.draw.circle(surf, PERI, (ex, ey), max(1, int(r * 0.10)))
            pygame.draw.circle(surf, PERI_HOT, (ex - int(r * 0.04), ey - int(r * 0.04)),
                               max(1, int(r * 0.05)))
    # a faint cool mouth line (calm, watching — the hook)
    pygame.draw.line(surf, EYE_DK,
                     (cx - int(r * 0.26), cy + int(r * 0.48)),
                     (cx + int(r * 0.26), cy + int(r * 0.44)), max(1, int(r * 0.06)))


# ── one thin SINGLE-BRANCH sasa NODE-SEGMENT (botany: Sasa = single branch) ───
def culm_segment(surf, cx, y0, y1, w, s, branch_sign=1):
    """One thin sasa culm node-segment from y0 to y1 with a raised node-RING at
    the top and a SINGLE branch stub (true Sasa habit: one branch per node, vs
    Phyllostachys' pair). Hard stepped bands: SAGE_D shade side -> SAGE fill ->
    SAGE_HI lit edge; node-ring is a discrete darker band, never a gradient."""
    half = w * 0.5
    seg = [(cx - half, y1), (cx - half, y0), (cx + half, y0), (cx + half, y1)]
    pygame.draw.polygon(surf, INK, seg)
    pygame.draw.polygon(surf, SAGE, seg)
    # stepped shade band on the right third, lit sliver on the left edge
    pygame.draw.rect(surf, SAGE_D, (cx + int(half * 0.2), min(y0, y1),
                                    max(1, int(half * 0.8)), abs(y1 - y0)))
    pygame.draw.rect(surf, SAGE_HI, (cx - half, min(y0, y1),
                                     max(1, int(half * 0.30)), abs(y1 - y0)))
    # raised node-ring at the top of the segment (discrete dark band + lit lip)
    nr = max(2, int(w * 0.7))
    pygame.draw.rect(surf, SAGE_DD, (cx - half - int(w * 0.10), y0 - nr // 2,
                                     w + int(w * 0.20), nr))
    pygame.draw.line(surf, SAGE_HI, (cx - half, y0 - nr // 2),
                     (cx + half, y0 - nr // 2), max(1, int(s * 0.6)))
    # SINGLE branch stub angling off the node (the Sasa tell)
    bx = cx + branch_sign * int(half + w * 1.4)
    by = y0 - int(w * 1.2)
    pygame.draw.line(surf, INK, (cx + branch_sign * half, y0), (bx, by), max(2, int(w * 0.5)))
    pygame.draw.line(surf, SAGE, (cx + branch_sign * half, y0), (bx, by), max(1, int(w * 0.3)))


# ── the WIDE-LOW DRIFT-MOUND hero ─────────────────────────────────────────────
def draw_sasa_yuki_onna(surf, cx, cy, s):
    """The snow-grass drift-spirit: a broad low billowing MOUND of muted-sage
    sasa, bristling with 5-7 upswept leaf-blade CLUMPS bowed under discrete hard
    powder-caps, a cool periwinkle-lit face forming in the centre. `s` = unit
    scale around a ~150-wide x 90-tall WIDE footprint (the deliberate horizontal
    silhouette). Drawn back-to-front: mound body -> rear leaf-tier -> face ->
    front fanning clumps overlapping so the sage mass reads dominant."""

    base_y = cy + int(40 * s)

    # === the DRIFT-MOUND body — a broad low sage hump (the dominant mass) =====
    # WHY wide & low: this is the only horizontal silhouette in the set. The mound
    # is a fat shallow dome of packed sasa, hard-stepped sage with a snow-dusted
    # crest — sage held as the visible body, snow only crowning the very top ridge.
    mound = [(cx - int(82 * s), base_y),
             (cx - int(74 * s), cy + int(8 * s)),
             (cx - int(48 * s), cy - int(18 * s)),
             (cx - int(18 * s), cy - int(30 * s)),
             (cx + int(16 * s), cy - int(30 * s)),
             (cx + int(50 * s), cy - int(16 * s)),
             (cx + int(76 * s), cy + int(10 * s)),
             (cx + int(82 * s), base_y)]
    pygame.draw.polygon(surf, INK, mound)
    pygame.draw.polygon(surf, SAGE, mound)
    # stepped shade band along the lower mound (grove-shadow), discrete not faded
    pygame.draw.polygon(surf, SAGE_D, [
        (cx - int(78 * s), base_y),
        (cx - int(60 * s), cy + int(14 * s)),
        (cx - int(20 * s), cy - int(2 * s)),
        (cx + int(30 * s), cy + int(2 * s)),
        (cx + int(64 * s), cy + int(16 * s)),
        (cx + int(78 * s), base_y)])
    pygame.draw.polygon(surf, SAGE_DD, [
        (cx - int(70 * s), base_y),
        (cx - int(36 * s), cy + int(24 * s)),
        (cx + int(40 * s), cy + int(24 * s)),
        (cx + int(70 * s), base_y)])
    # discrete hard powder-caps along the mound CREST (snow crowns, no blanket)
    for fx, fw in ((-0.62, 0.16), (-0.30, 0.18), (0.04, 0.20), (0.38, 0.17)):
        crest_x = cx + int(fx * 150 * s)
        crest_y = cy - int(24 * s) + int(abs(fx) * 26 * s)
        cap = [(crest_x - int(fw * 80 * s), crest_y + int(6 * s)),
               (crest_x - int(fw * 50 * s), crest_y - int(8 * s)),
               (crest_x + int(fw * 40 * s), crest_y - int(6 * s)),
               (crest_x + int(fw * 70 * s), crest_y + int(8 * s))]
        pygame.draw.polygon(surf, SNOW_SH, [(x, y + s * 0.5) for (x, y) in cap])
        pygame.draw.polygon(surf, SNOW, cap)
        pygame.draw.line(surf, SNOW_HI,
                         (crest_x - int(fw * 40 * s), crest_y - int(5 * s)),
                         (crest_x + int(fw * 30 * s), crest_y - int(4 * s)),
                         max(1, int(s * 1.0)))

    # === REAR leaf-tier (behind the face) — a few blades fanning up-and-back ===
    rear = [(-0.70, 200, 0.86, 0.10), (-0.42, 207, 0.78, -0.04),
            (0.40, 207, 0.78, 0.04), (0.66, 200, 0.86, -0.10)]
    for fx, deg, fac, curl in rear:
        root = (cx + int(fx * 70 * s), cy - int(8 * s))
        sasa_leaf(surf, root, math.radians(deg), 64 * s * fac, 22 * s, s,
                  curl=curl, snow_cap=True)

    # === the FACE forming in the drift (periwinkle frost-glow — identity) =====
    drift_face(surf, cx, cy + int(2 * s), int(22 * s), s, lit=True)

    # === FRONT fanning leaf-CLUMPS — capped at a readable 5-7 (no fuzz) ========
    # WHY only 5-7 upswept clumps: more dissolves to fuzz at 32px. Each clump is a
    # broad bowed lance drooping under its own discrete powder-cap, sweeping out
    # sideways to reinforce the WIDE silhouette; sage stays the visible mass.
    # (left-out, left, low-left, low-right, right, right-out) + 1 short centre.
    clumps = [
        (-0.92, 168, 1.00, 0.22),   # far-left, sweeps out + droops
        (-0.58, 150, 0.90, 0.16),
        (-0.26, 128, 0.74, 0.08),
        (0.30, 52,  0.74, -0.08),
        (0.60, 32,  0.90, -0.16),
        (0.94, 14,  1.00, -0.22),   # far-right, sweeps out + droops
    ]
    for fx, deg, fac, curl in clumps:
        root = (cx + int(fx * 60 * s), cy + int(6 * s))
        sasa_leaf(surf, root, math.radians(deg), 78 * s * fac, 26 * s, s,
                  curl=curl, snow_cap=True)
    # one short upright centre blade nested just behind/above the face crown
    sasa_leaf(surf, (cx, cy - int(20 * s)), math.radians(-90), 44 * s, 22 * s, s,
              curl=0.0, snow_cap=True)


# ── the single-culm pillar (node-segments = repeat; leaf-tuft cap; mound base) ─
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """A single tall sasa CULM rising from the drift-mound IS the pillar: thin
    single-branch node-segments tile as the repeat band; a snow-capped leaf-fan
    TUFT is the detachable gap-edge cap; the wide drift-mound base is the lower
    mirror. `cap` names the END that faces the GAP. Bottom-rooted, never
    top-heavy: the heavy mound mass always sits away from the gap."""
    seg_pitch = int(30 * s)
    cap_room = int(54 * s)
    base_room = int(46 * s)
    culm_w = int(11 * s)

    if cap == "bottom":
        # mound base sits at TOP (away from the down-facing gap); culm runs down;
        # leaf-tuft cap hangs at the bottom toward the gap.
        base_cy = top + int(20 * s)
        b0, b1 = top + base_room, bot - cap_room
        tuft_y = bot - int(26 * s)
        branch_dir = 1
    else:
        base_cy = bot - int(20 * s)
        b0, b1 = top + cap_room, bot - base_room
        tuft_y = top + int(26 * s)
        branch_dir = -1

    # === tileable node-segment shaft ==========================================
    y = b0
    flip = 1
    while y <= b1:
        culm_segment(surf, cx, y, min(y + seg_pitch, b1), culm_w, s,
                     branch_sign=flip)
        flip = -flip
        y += seg_pitch

    # === drift-mound base (the lower mirror = the wide creature footprint) =====
    mb = [(cx - int(40 * s), base_cy + int(16 * s)),
          (cx - int(30 * s), base_cy - int(8 * s)),
          (cx - int(10 * s), base_cy - int(18 * s)),
          (cx + int(10 * s), base_cy - int(18 * s)),
          (cx + int(30 * s), base_cy - int(8 * s)),
          (cx + int(40 * s), base_cy + int(16 * s))]
    pygame.draw.polygon(surf, INK, mb)
    pygame.draw.polygon(surf, SAGE, mb)
    pygame.draw.polygon(surf, SAGE_D, [
        (cx - int(36 * s), base_cy + int(16 * s)),
        (cx - int(16 * s), base_cy + int(2 * s)),
        (cx + int(16 * s), base_cy + int(2 * s)),
        (cx + int(36 * s), base_cy + int(16 * s))])
    # a discrete snow cap on the mound base crest (no blanket)
    pygame.draw.polygon(surf, SNOW, [
        (cx - int(18 * s), base_cy - int(10 * s)),
        (cx - int(8 * s), base_cy - int(18 * s)),
        (cx + int(10 * s), base_cy - int(16 * s)),
        (cx + int(16 * s), base_cy - int(8 * s))])
    # a couple of side leaf-blades flaring off the base so it reads sasa-mound
    sasa_leaf(surf, (cx - int(20 * s), base_cy - int(4 * s)),
              math.radians(200 if cap == "bottom" else 160),
              40 * s, 16 * s, s, curl=0.10, snow_cap=True)
    sasa_leaf(surf, (cx + int(20 * s), base_cy - int(4 * s)),
              math.radians(-20 if cap == "bottom" else 20),
              40 * s, 16 * s, s, curl=-0.10, snow_cap=True)

    # === gap-edge cap: a snow-capped leaf-fan TUFT ============================
    # WHY a tuft caps the gap: it is the creature-derived signature (the fanning
    # snow-laden sasa) detached and pointed at the gap, while the heavy mound
    # stays at the far end — bottom-rooted, never top-heavy.
    tuft_dir = -1 if cap == "bottom" else 1   # blades point AWAY from gap into culm? no — toward gap
    # fan of 5 blades splaying toward the gap, each snow-capped
    fan = [(-0.9, 0.78), (-0.45, 0.92), (0.0, 1.00), (0.45, 0.92), (0.9, 0.78)]
    for fx, fac in fan:
        if cap == "bottom":
            ang = math.radians(90) + fx * math.radians(46)   # splay downward
        else:
            ang = math.radians(-90) + fx * math.radians(46)  # splay upward
        sasa_leaf(surf, (cx, tuft_y), ang, 40 * s * fac, 14 * s, s,
                  curl=0.0, snow_cap=True)
    # a tiny periwinkle frost-pip at the tuft heart so the cap carries identity
    g = radial_glow(int(10 * s), PERI, alpha_center=130, falloff=2.4)
    surf.blit(g, (cx - g.get_width() // 2, tuft_y - g.get_height() // 2),
              special_flags=pygame.BLEND_ADD)


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
    sheet.blit(font_big.render("SASA-YUKI-ONNA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "snow-grass drift-spirit  ·  WIDE-LOW sasa DRIFT-MOUND · sage body dominant · snow = hard caps only · periwinkle face-glow · round 1",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((400 * SS, 360 * SS), pygame.SRCALPHA)
        draw_sasa_yuki_onna(big, 200 * SS, 190 * SS, 1.95 * SS)
        small = pygame.transform.smoothscale(big, (400, 360))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (12, 86))
    sheet.blit(font.render("Creature — hero", True, LABEL), (150, 452))
    sheet.blit(font_sm.render("WIDE-LOW drift-mound of muted-SAGE sasa (the dominant mass); 5-7 broad lance", True, LABEL_DIM), (14, 476))
    sheet.blit(font_sm.render("leaf-clumps fan out sideways, bowed under DISCRETE hard powder-caps (no blanket).", True, LABEL_DIM), (14, 492))
    sheet.blit(font_sm.render("Dry pale snow-edge leaf-margins (real winter sasa). Cool PERIWINKLE frost-glow", True, LABEL_DIM), (14, 508))
    sheet.blit(font_sm.render("on the face forming in the drift = identity anchor. Cool winter-spirit temperature.", True, LABEL_DIM), (14, 524))

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
    pygame.draw.rect(sheet, (52, 62, 70), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — single culm", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("single-branch node-segments = repeat band;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("snow-capped leaf-fan tuft = gap-edge cap;", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("drift-mound base = lower mirror (visible above)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    # WHY chip footprint is 110 wide: this is a WIDE creature, so the 32px chip
    # fits the broad horizontal silhouette into the cell (height ~70).
    def chip32():
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_sasa_yuki_onna(big, 55 * SS, 60 * SS, (32 / 168.0) * SS)
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

    # blacked-out 32px silhouette — the WIDE-MOUND read TEST: it must read ONLY
    # as a broad low horizontal mound bristling with upswept blades, never a tall
    # stalk and never the old Yukitake's bowed single stem.
    def silhouette32():
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_sasa_yuki_onna(big, 55 * SS, 60 * SS, (32 / 168.0) * SS)
        small = pygame.transform.smoothscale(big, (110, 110))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
        return sil

    sil_y = night_y + 188
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 218, 220), (sx, sil_y, 110, 110))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 110, 110), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT —", True, LABEL), (sx + 118, sil_y + 28))
    sheet.blit(font_sm.render("must read WIDE-LOW MOUND,", True, LABEL_DIM), (sx + 118, sil_y + 46))
    sheet.blit(font_sm.render("never a tall stalk", True, LABEL_DIM), (sx + 118, sil_y + 64))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 196
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
        (SAGE, "sage body (mass)"), (SAGE_D, "node shade"),
        (SNOW, "snow powder-cap"), (SNOW_SH, "blue-shadow snow"),
        (MARGIN, "dry snow-edge"), (PERI, "periwinkle glow"),
        (SAGE_DD, "grove hollow"), (INK, "ink keyline"),
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
        "ELEVATED-REALISM: SS=6 supersample -> smoothscale. 4-6 HARD STEPPED value bands per form (NO gradients) · hard ink keyline (28,22,30) · "
        "1px grown outline · radial periwinkle glow = FACE accent only · procedural-only · FLIPPED dominance: sage body, snow as caps (not a blanket).",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
