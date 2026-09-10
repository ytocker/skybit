"""
Round-2 concept renderer for SASA-YUKI-ONNA — the snow-grass drift-spirit of
the dwarf bamboo (bamboo-v2 REALISTIC set, concept #3). Headless Pygame;
ELEVATED-REALISM pipeline (supersample SS=6 -> smoothscale) so the fanned
leaf-tiers + hard powder-caps stay crisp at downscale.

WHY this set is a DEPARTURE from the chibi bamboo 1: realistic non-chibi
proportions and botanical accuracy are the whole point. The house triad is
pushed to 4-6 HARD STEPPED value bands per form (NO smooth gradients) for a
sculpted near-volumetric read that still survives at true 32px. Radial glow is
for ACCENTS only. Hard ink keyline (28,22,30) + 1px alpha-grown outline.

WHY R2 over R1 — the AD gate failure was that R1's snow rebuilt a mini-Yukitake
(the central drift-core measured ~49% snow). R2 FLIPS the dominance the brief
demands: the muted-SAGE mound is now the visible creature BODY (target green
>=55% of mass), and snow appears ONLY as >=5 DISCRETE hard powder-caps riding
ON TOP of the sage mound + on leaf-tier tips — there is NO connected white
belly anymore. The face is rebuilt snow-RIMMED, not snow-filled: it is shrunk,
embedded INTO the sage drift, and its dominant value is the periwinkle
frost-glow (176,200,236), not white — the one place the eye lands. The day chip
is rescued with FEWER, BIGGER, more angular blade-clumps so the spiky-mound
KIND survives the 32px downsample (R1 read as a grey-white smudge). The dry
pale-margin (214,220,194) is now a HARD band on leaf edges (real-sasa tell +
a value step that helps leaves read as sasa small). The blacked-out silhouette
is re-verified WIDE-LOW + spiky after the sage body grew.

WHY this is the WIDE-LOW DRIFT-MOUND of the set: the cross-set KIND spread needs
exactly one broad horizontal silhouette, so Sasa-Yuki-Onna is deliberately a low
billowing MOUND of snow-laden sasa fanning out sideways — the opposite of a tall
stalk. The whole margin vs the old Yukitake lives in FLIPPED DOMINANCE: the
muted SAGE-GREEN sasa body is held as the visible mass; snow appears only as
discrete HARD powder-caps perched on the mound + each leaf-tier, NEVER a blanket.
Fanning blades are capped at ~5 readable clumps so the mound never dissolves
into fuzz at 32px. The cold PERIWINKLE frost-glow on the face is the identity
anchor (radial, face-only) — no roster green pairs with periwinkle — and the
temperature leans HARD cool winter-spirit (the gap-widener vs #7's warm ambush).

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


# ── one DISCRETE hard powder-cap (the snow vocabulary — caps, never a blanket) ─
def powder_cap(surf, cx, cy, w, h, s, tilt=0.0):
    """ONE discrete hard-edged snow powder-cap: a small angular wedge of packed
    snow that rides ON TOP of a sage surface. Built as three flat stepped bands
    (blue-shadow under-lip -> snow body -> hot sheen pip) with a faceted notched
    top so it reads as crusted powder, never a smooth dome. `tilt` skews the cap
    so caps perched on sloping mound/leaf faces sit believably. These are the
    ONLY place snow appears — there is no connected white belly."""
    tx = w * tilt
    cap = [(cx - w,            cy + h * 0.45),
           (cx - w * 0.55,     cy - h * 0.35 + tx * 0.4),
           (cx - w * 0.12,     cy - h * 0.85 + tx * 0.7),
           (cx + w * 0.30,     cy - h * 0.55 + tx),
           (cx + w * 0.70,     cy - h * 0.20 + tx * 0.7),
           (cx + w,            cy + h * 0.45)]
    # blue-shadow under-lip (offset down so the cap reads as raised volume)
    pygame.draw.polygon(surf, SNOW_SH, [(x, y + h * 0.30) for (x, y) in cap])
    # snow body
    pygame.draw.polygon(surf, SNOW, cap)
    # hot sheen pip on the catching facet (top-left)
    pygame.draw.polygon(surf, SNOW_HI, [
        (cx - w * 0.55, cy - h * 0.30 + tx * 0.4),
        (cx - w * 0.12, cy - h * 0.78 + tx * 0.7),
        (cx + w * 0.10, cy - h * 0.40 + tx * 0.7),
        (cx - w * 0.30, cy - h * 0.10 + tx * 0.4)])
    # crisp ink keyline so each cap reads DISCRETE at 32px (no merge into a belt)
    pygame.draw.polygon(surf, INK, cap, max(1, int(w * 0.10)))


# ── one SASA LEAF-BLADE — broad lance, dry pale snow-edge margin, hard bands ──
def sasa_leaf(surf, root, ang, length, width, s, curl=0.0, snow_cap=True):
    """ONE broad lance sasa leaf rooted at `root`, swept along `ang`, bowed by
    `curl` (positive = droops under powder weight). Botanically a wide lance with
    a slight recurve, NOT a needle. Built as flat STEPPED value bands (no
    gradient): SAGE_D under-shade -> SAGE flat fill -> SAGE_HI top sheen ->
    MARGIN dry pale-margin HARD band down both edges (the real winter sasa tell +
    a value step that helps the blade read as sasa at small scale), with an
    optional discrete HARD snow powder-cap perched on the TIP only — never a
    blanket coating the whole blade."""
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
    # dry pale "snow-edge" MARGIN — a HARD discrete pale band down BOTH lance
    # edges (real winter-sasa necrosis), never a soft fade; thickened in R2 so it
    # survives as a value step at 32px
    mw = max(2, int(width * 0.20))
    pygame.draw.line(surf, MARGIN, (bx[0] + px * hw, bx[1] + py * hw), tip, mw)
    pygame.draw.line(surf, MARGIN, (bx[0] - px * hw, bx[1] - py * hw), tip, mw)
    pygame.draw.line(surf, MARGIN,
                     (root[0] + px * hw * 0.30, root[1] + py * hw * 0.30),
                     (bx[0] + px * hw, bx[1] + py * hw), mw)
    pygame.draw.line(surf, MARGIN,
                     (root[0] - px * hw * 0.30, root[1] - py * hw * 0.30),
                     (bx[0] - px * hw, bx[1] - py * hw), mw)
    # one discrete HARD powder-cap perched on the TIP face only (snow sits where
    # it would catch on the recurve — never coating the blade body)
    if snow_cap:
        tipx = root[0] + ca * length * 0.78 + px * curl * length * 0.78
        tipy = root[1] + sa * length * 0.78 + py * curl * length * 0.78
        powder_cap(surf, tipx, tipy, hw * 0.62, length * 0.16, s,
                   tilt=curl * 0.6)
    pygame.draw.polygon(surf, INK, leaf, max(2, int(width * 0.10)))


# ── a cool SNOW-RIMMED FACE embedded INTO the sage drift (periwinkle-dominant) ─
def drift_face(surf, cx, cy, r, s, lit=True):
    """A small yuki-onna face EMBEDDED in the sage drift — snow-RIMMED, NOT
    snow-filled. R2 rebuild vs R1: the face is shrunk, set INTO a recessed sage
    socket (so it does not read as a white blob sitting on the mound), and its
    DOMINANT value is the periwinkle frost-glow (176,200,236), not white — the
    one place the eye is meant to land. Snow is only a thin crusted RIM around
    the edge; the inner face is cool periwinkle-lit pale, with two slate
    eye-hollows and a faint calm mouth. The radial glow stays face-only."""
    # recessed sage socket the face sits INTO (keeps the sage body reading as the
    # mass even right at the focal — the face is a hollow in the drift, not a lump)
    socket = [(cx - int(r * 1.18), cy - int(r * 0.10)),
              (cx - int(r * 0.86), cy - int(r * 0.98)),
              (cx, cy - int(r * 1.16)),
              (cx + int(r * 0.86), cy - int(r * 0.98)),
              (cx + int(r * 1.18), cy - int(r * 0.10)),
              (cx + int(r * 0.80), cy + int(r * 0.98)),
              (cx, cy + int(r * 1.22)),
              (cx - int(r * 0.80), cy + int(r * 0.98))]
    pygame.draw.polygon(surf, SAGE_DD, socket)            # dark sage hollow rim
    if lit:
        g = radial_glow(int(r * 1.5), PERI, alpha_center=170, falloff=2.0)
        surf.blit(g, (cx - g.get_width() // 2, cy - g.get_height() // 2),
                  special_flags=pygame.BLEND_ADD)
    # thin crusted SNOW RIM hugging the socket edge (a discrete band, not a fill)
    rim = [(cx - int(r * 0.98), cy - int(r * 0.06)),
           (cx - int(r * 0.72), cy - int(r * 0.82)),
           (cx, cy - int(r * 0.98)),
           (cx + int(r * 0.72), cy - int(r * 0.82)),
           (cx + int(r * 0.98), cy - int(r * 0.06)),
           (cx + int(r * 0.66), cy + int(r * 0.82)),
           (cx, cy + int(r * 1.02)),
           (cx - int(r * 0.66), cy + int(r * 0.82))]
    pygame.draw.polygon(surf, SNOW_SH, rim)
    pygame.draw.polygon(surf, SNOW, rim)
    # INNER face — PERIWINKLE is the dominant value here (not white). This is the
    # focal: the cold lit hollow where the spirit is forming.
    inner = [(cx - int(r * 0.66), cy + int(r * 0.02)),
             (cx - int(r * 0.46), cy - int(r * 0.58)),
             (cx, cy - int(r * 0.72)),
             (cx + int(r * 0.46), cy - int(r * 0.58)),
             (cx + int(r * 0.66), cy + int(r * 0.02)),
             (cx + int(r * 0.42), cy + int(r * 0.66)),
             (cx, cy + int(r * 0.80)),
             (cx - int(r * 0.42), cy + int(r * 0.66))]
    pygame.draw.polygon(surf, PERI, inner)
    # hot periwinkle core step (top-left catch) so the glow has a sculpted facet
    pygame.draw.polygon(surf, PERI_HOT, [
        (cx - int(r * 0.46), cy - int(r * 0.04)),
        (cx - int(r * 0.20), cy - int(r * 0.52)),
        (cx + int(r * 0.06), cy - int(r * 0.34)),
        (cx - int(r * 0.22), cy + int(r * 0.10))])
    # two cool slate eye-hollows pinned with a periwinkle frost-pip
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.34)
        ey = cy - int(r * 0.06)
        eye = [(ex - int(r * 0.18), ey - int(r * 0.04)),
               (ex + int(r * 0.18), ey - int(r * 0.12)),
               (ex + int(r * 0.13), ey + int(r * 0.14)),
               (ex - int(r * 0.15), ey + int(r * 0.10))]
        pygame.draw.polygon(surf, INK, eye)
        pygame.draw.polygon(surf, EYE_DK, eye)
        if lit:
            pygame.draw.circle(surf, PERI_HOT, (ex, ey), max(1, int(r * 0.08)))
    # a faint cool mouth line (calm, watching — the hook)
    pygame.draw.line(surf, EYE_DK,
                     (cx - int(r * 0.22), cy + int(r * 0.42)),
                     (cx + int(r * 0.22), cy + int(r * 0.38)), max(1, int(r * 0.06)))
    pygame.draw.polygon(surf, INK, socket, max(1, int(s * 0.7)))


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
    sasa, bristling with ~5 BIG angular leaf-blade CLUMPS bowed under DISCRETE
    hard powder-caps, a cool periwinkle-lit face embedded in the centre. `s` =
    unit scale around a ~150-wide x 90-tall WIDE footprint (the deliberate
    horizontal silhouette). Drawn back-to-front: SAGE mound body (the dominant
    mass) -> rear leaf-tier -> embedded face -> front fanning clumps -> discrete
    powder-caps riding on top — so sage reads as the body and snow as caps."""

    base_y = cy + int(40 * s)

    # === the DRIFT-MOUND body — a broad low SAGE hump (the DOMINANT mass) ======
    # WHY wide & low: this is the only horizontal silhouette in the set. R2 — the
    # ENTIRE mound body is now muted SAGE (R1 wrongly let a white drift-core eat
    # the centre). Snow does NOT live in the body; it is added LAST as discrete
    # caps. Four hard sage value-bands sculpt the dome (no gradient).
    mound = [(cx - int(84 * s), base_y),
             (cx - int(76 * s), cy + int(6 * s)),
             (cx - int(50 * s), cy - int(20 * s)),
             (cx - int(18 * s), cy - int(32 * s)),
             (cx + int(16 * s), cy - int(32 * s)),
             (cx + int(52 * s), cy - int(18 * s)),
             (cx + int(78 * s), cy + int(8 * s)),
             (cx + int(84 * s), base_y)]
    pygame.draw.polygon(surf, INK, mound)
    pygame.draw.polygon(surf, SAGE, mound)
    # top-light sage sheen band along the upper-left dome face (hard step UP)
    pygame.draw.polygon(surf, SAGE_HI, [
        (cx - int(70 * s), cy + int(2 * s)),
        (cx - int(44 * s), cy - int(20 * s)),
        (cx - int(12 * s), cy - int(30 * s)),
        (cx + int(6 * s), cy - int(20 * s)),
        (cx - int(20 * s), cy - int(2 * s)),
        (cx - int(48 * s), cy + int(6 * s))])
    # mid shade band along the lower mound (grove-shadow), discrete not faded
    pygame.draw.polygon(surf, SAGE_D, [
        (cx - int(80 * s), base_y),
        (cx - int(62 * s), cy + int(12 * s)),
        (cx - int(20 * s), cy - int(4 * s)),
        (cx + int(30 * s), cy + int(0 * s)),
        (cx + int(66 * s), cy + int(14 * s)),
        (cx + int(80 * s), base_y)])
    # deepest grove-hollow band at the base (the dark footing)
    pygame.draw.polygon(surf, SAGE_DD, [
        (cx - int(72 * s), base_y),
        (cx - int(38 * s), cy + int(22 * s)),
        (cx + int(42 * s), cy + int(22 * s)),
        (cx + int(72 * s), base_y)])

    # === REAR leaf-tier (behind the face) — a few blades fanning up-and-back ===
    rear = [(-0.66, 202, 0.84, 0.10), (-0.40, 208, 0.76, -0.04),
            (0.40, 208, 0.76, 0.04), (0.66, 202, 0.84, -0.10)]
    for fx, deg, fac, curl in rear:
        root = (cx + int(fx * 70 * s), cy - int(6 * s))
        sasa_leaf(surf, root, math.radians(deg), 60 * s * fac, 22 * s, s,
                  curl=curl, snow_cap=True)

    # === the FACE embedded in the drift (periwinkle frost-glow — identity) =====
    # R2: shrunk + embedded + periwinkle-dominant (was a white blob in R1).
    drift_face(surf, cx, cy - int(2 * s), int(17 * s), s, lit=True)

    # === FRONT fanning leaf-CLUMPS — DAY-CHIP RESCUE: ~5 BIG angular clumps =====
    # WHY only ~5 BIG clumps: R1's 7 thinner blades smudged to grey-white at 32px.
    # R2 drops to 5 BIGGER, more angular, longer lance-clumps so the SPIKY-MOUND
    # KIND survives the downsample — each clump a confident sage spike with one
    # discrete tip-cap, sweeping out sideways to reinforce the WIDE silhouette.
    clumps = [
        (-0.96, 166, 1.10, 0.20),   # far-left, sweeps out + droops
        (-0.52, 142, 0.96, 0.12),
        (0.00, -90, 0.78, 0.0),    # upright centre spike
        (0.52, 38,  0.96, -0.12),
        (0.96, 14,  1.10, -0.20),   # far-right, sweeps out + droops
    ]
    for fx, deg, fac, curl in clumps:
        root = (cx + int(fx * 58 * s), cy + int(4 * s))
        sasa_leaf(surf, root, math.radians(deg), 82 * s * fac, 30 * s, s,
                  curl=curl, snow_cap=True)

    # === DISCRETE hard powder-caps riding ON TOP of the sage mound ============
    # WHY caps last + on top: snow is a vocabulary of >=5 SEPARATE crusted caps
    # perched where powder would settle on the dome ridge — there is NO connected
    # white belly. With the leaf tip-caps above, the sheet carries well over 5
    # discrete caps while the sage body stays the visible mass.
    ridge = [(-0.58, 0.72), (-0.24, 0.92), (0.10, 1.00), (0.42, 0.86)]
    for fx, sz in ridge:
        rx = cx + int(fx * 132 * s)
        ry = cy - int(18 * s) + int(abs(fx) * 22 * s)
        powder_cap(surf, rx, ry, 16 * s * sz, 12 * s * sz, s, tilt=fx * 0.5)
    # one small cap nested just above the face crown (frost gathering on the spirit)
    powder_cap(surf, cx, cy - int(22 * s), 12 * s, 9 * s, s, tilt=0.0)


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
    else:
        base_cy = bot - int(20 * s)
        b0, b1 = top + cap_room, bot - base_room
        tuft_y = top + int(26 * s)

    # === tileable node-segment shaft ==========================================
    y = b0
    flip = 1
    while y <= b1:
        culm_segment(surf, cx, y, min(y + seg_pitch, b1), culm_w, s,
                     branch_sign=flip)
        flip = -flip
        y += seg_pitch

    # === drift-mound base (the lower mirror = the wide creature footprint) =====
    # R2: the base mirror is SAGE-bodied with a single discrete cap, matching the
    # flipped dominance of the hero (no white belly here either).
    mb = [(cx - int(40 * s), base_cy + int(16 * s)),
          (cx - int(30 * s), base_cy - int(8 * s)),
          (cx - int(10 * s), base_cy - int(18 * s)),
          (cx + int(10 * s), base_cy - int(18 * s)),
          (cx + int(30 * s), base_cy - int(8 * s)),
          (cx + int(40 * s), base_cy + int(16 * s))]
    pygame.draw.polygon(surf, INK, mb)
    pygame.draw.polygon(surf, SAGE, mb)
    pygame.draw.polygon(surf, SAGE_HI, [
        (cx - int(30 * s), base_cy - int(6 * s)),
        (cx - int(8 * s), base_cy - int(16 * s)),
        (cx + int(6 * s), base_cy - int(10 * s)),
        (cx - int(14 * s), base_cy - int(2 * s))])
    pygame.draw.polygon(surf, SAGE_D, [
        (cx - int(36 * s), base_cy + int(16 * s)),
        (cx - int(16 * s), base_cy + int(2 * s)),
        (cx + int(16 * s), base_cy + int(2 * s)),
        (cx + int(36 * s), base_cy + int(16 * s))])
    # a couple of side leaf-blades flaring off the base so it reads sasa-mound
    sasa_leaf(surf, (cx - int(20 * s), base_cy - int(4 * s)),
              math.radians(200 if cap == "bottom" else 160),
              42 * s, 18 * s, s, curl=0.10, snow_cap=True)
    sasa_leaf(surf, (cx + int(20 * s), base_cy - int(4 * s)),
              math.radians(-20 if cap == "bottom" else 20),
              42 * s, 18 * s, s, curl=-0.10, snow_cap=True)
    # ONE discrete snow cap on the mound-base crest (no blanket)
    powder_cap(surf, cx, base_cy - int(14 * s), 13 * s, 9 * s, s, tilt=0.0)

    # === gap-edge cap: a snow-capped leaf-fan TUFT ============================
    # WHY a tuft caps the gap: it is the creature-derived signature (the fanning
    # snow-laden sasa) detached and pointed at the gap, while the heavy mound
    # stays at the far end — bottom-rooted, never top-heavy.
    # fan of 5 blades splaying toward the gap, each with a discrete tip-cap
    fan = [(-0.9, 0.80), (-0.45, 0.94), (0.0, 1.00), (0.45, 0.94), (0.9, 0.80)]
    for fx, fac in fan:
        if cap == "bottom":
            ang = math.radians(90) + fx * math.radians(46)   # splay downward
        else:
            ang = math.radians(-90) + fx * math.radians(46)  # splay upward
        sasa_leaf(surf, (cx, tuft_y), ang, 42 * s * fac, 15 * s, s,
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
        "snow-grass drift-spirit · WIDE-LOW sasa DRIFT-MOUND · SAGE body DOMINANT · snow = >=5 DISCRETE caps · periwinkle-RIMMED face · round 2",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((400 * SS, 360 * SS), pygame.SRCALPHA)
        draw_sasa_yuki_onna(big, 200 * SS, 190 * SS, 1.95 * SS)
        small = pygame.transform.smoothscale(big, (400, 360))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (12, 86))
    sheet.blit(font.render("Creature — hero", True, LABEL), (150, 452))
    sheet.blit(font_sm.render("WIDE-LOW drift-mound: the muted-SAGE body is the DOMINANT mass; ~5 BIG angular", True, LABEL_DIM), (14, 476))
    sheet.blit(font_sm.render("lance-clumps fan out sideways. Snow = >=5 DISCRETE hard powder-caps riding ON TOP", True, LABEL_DIM), (14, 492))
    sheet.blit(font_sm.render("(no connected white belly). HARD dry pale-margin band on leaf edges (real sasa).", True, LABEL_DIM), (14, 508))
    sheet.blit(font_sm.render("Face is snow-RIMMED + PERIWINKLE-lit (not white-filled) — the focal. Cool winter.", True, LABEL_DIM), (14, 524))

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
    sheet.blit(font_sm.render("sage drift-mound base = lower mirror (above)", True, LABEL_DIM), (pcx - 4, 746))

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
    # stalk and never the old Yukitake's bowed single stem. R2 re-verifies this
    # holds WIDE-LOW + SPIKY after the sage body grew (must not round into a blob).
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
    sheet.blit(font_sm.render("must read WIDE-LOW + SPIKY,", True, LABEL_DIM), (sx + 118, sil_y + 46))
    sheet.blit(font_sm.render("never a tall stalk or blob", True, LABEL_DIM), (sx + 118, sil_y + 64))

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
        "1px grown outline · radial periwinkle glow = FACE accent only · procedural-only · R2 FLIP: SAGE body dominant, snow = >=5 discrete caps (no white belly).",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
