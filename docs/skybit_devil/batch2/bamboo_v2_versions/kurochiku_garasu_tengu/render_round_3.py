"""
Round-3 (FINAL) concept renderer for KUROCHIKU-GARASU-TENGU — the black-bamboo
crow-tengu of the mountain grove (bamboo v2 REALISTIC set, concept #5). Headless
Pygame; ELEVATED pipeline (supersample SS=6 -> smoothscale) so the split-culm
quill geometry and node-rings stay crisp at downscale.

WHY this departs from the chibi house grammar: bamboo v2 is a DELIBERATE
departure toward REALISM and botanical accuracy — true tall-thin proportions,
NO chibi big-head. Shading is hard-edged FLAT but pushed to 4-6 HARD STEPPED
value bands per form for a sculpted near-volumetric read; NEVER smooth gradients
(they boil at true-32px). Radial glow is for accents ONLY. Hard ink keyline
(28,22,30) + a 1px alpha-mask outline for silhouette POP.

WHY this is the WINGED BEAKED TENGU — the ONLY winged form in the set: a hunched
crow-headed mountain-guardian yokai feathered in glossy black kurochiku, sharp
beak, a tall single feather-tuft, two angular SPLIT-CULM quill-wings spread,
gripping a black-bamboo staff. Black-on-black NIGHT legibility is the real risk.

WHY round-3 (the FINAL budget-ending pass — AD verdict was SHIP-READY: both
binding gates, night legibility + bamboo quills, are CLEARED and PRESERVED here).
This pass fixes the one real soft-spot the AD flagged: round 2's hero drifted to
a bilateral INSECT / dragonfly read instead of a hunched crow-tengu. Punch list:
 1. CROW-TENGU over insect: the head + shoulders are HUNCHED forward (the skull
    cranes ahead of the torso on a forward-pitched neck) and the wing posture is
    now ASYMMETRIC — the left wing is held HIGHER and more swept-back, the right
    drops lower and rakes wider — breaking the bilateral dragonfly symmetry. The
    night silhouette stays one connected winged mass (re-verified on the chip).
 2. PUSHED BEAK: the beak is rebuilt as a sharp hard-STEPPED chisel point carved
    forward off the vermilion cere — a true crow bill, not a soft round wattle-
    oval — so "crow-billed" is unmistakable at hero.
 3. The WING-slat node-ring contrast is lifted ~12% (a darker ridge + a hotter
    sheath-scar) ONLY on the wing quills, NOT the pillar (the pillar is perfect),
    so the wing slats read as split CULM at 32px as convincingly as the pillar.
 4. The lower-body chevron band is BROKEN UP — the lowest abdomen-segment-like
    chevron is dropped and the two remaining rows are offset/asymmetric so the
    breast no longer reads as stacked insect abdomen segments.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the triad/outline
helpers cloned from the lineage template, plus the necrarch radial_glow.
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (locked brief #5) ─────────────────────────────────────────
# Blackened kurochiku re-keyed COOLER/steelier than the old Nushi. The black is
# the dominant feathered mass; the steely blue-grey quill-sheen is the legibility
# anchor (a FIRM band, not a whisper) so the wing edges read on a night sky. The
# two WARM accents (vermilion beak-wattle + thin gold staff-band) carry the focal.
BLACK      = ( 46,  40,  50)   # black-culm base (the dominant feathered mass)
INKVIO     = ( 28,  24,  36)   # ink-violet shade / deepest feather hollow
SHEEN      = (132, 140, 162)   # steely blue-grey quill-sheen (FIRM value band)
SHEEN_MID  = (104, 112, 134)   # cooler mid step between black + steely sheen
SHEEN_HI   = (176, 184, 204)   # hottest quill-sheen edge (rim only)
BLOOM      = ( 84,  78,  98)   # faint violet waxy-bloom mid-band on the culm
RIMVIO     = ( 96,  86, 128)   # violet-bloom containing rim (night keyline glow)
VERM       = (206,  68,  52)   # vermilion tengu beak-wattle (THE warm focal)
VERM_HI    = (236, 132,  96)   # hot vermilion highlight
VERM_D     = (150,  44,  36)   # vermilion shade
GOLD       = (214, 176,  90)   # thin gold staff-band / ferrule
GOLD_HI    = (244, 216, 150)   # hot gold edge
GOLD_D     = (150, 116,  52)   # gold shade
SHOOT      = (134, 176,  96)   # fresh green node-shoot collar (tiny, the only green)
SHOOT_D    = ( 84, 124,  66)   # shoot shade
SHIDE      = (224, 224, 232)   # paper shide (white zigzag streamer) on the staff
INK        = ( 28,  22,  30)   # hard ink keyline

# WHY two node-ring keys: the PILLAR node-ring (cleared the 32px bamboo gate, do
# NOT touch) keeps INKVIO/SHEEN_HI. The WING slats get a ~12% hotter contrast
# pair — a deeper ridge + a brighter sheath-scar — so the wing reads as split
# culm at 32px as convincingly as the pillar (punch-list #3, wing-only).
WING_NODE_D  = ( 18,  16,  26)   # deeper wing-slat node ridge (darker than INKVIO)
WING_NODE_HI = (200, 208, 226)   # hotter wing-slat sheath-scar (brighter than SHEEN_HI)

BG         = ( 60,  58,  72)   # neutral cool-grey review backdrop
PANEL      = ( 46,  44,  58)
DAY_SKY_T  = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B  = (196, 232, 244)
NIGHT_T    = ( 18,  20,  44)   # night biome sky (top) — the real legibility test
NIGHT_B    = ( 40,  38,  72)
LABEL      = (238, 240, 244)
LABEL_DIM  = (186, 192, 206)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ── outline grown from the alpha mask (the house keyline / silhouette POP) ────
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


# ── a containing RIM grown OUTSIDE the silhouette (the night-edge keeper) ─────
def grow_rim(surf, color, px):
    """Grow a coloured ring OUTSIDE the alpha mask so the figure carries its OWN
    edge against the night biome — without this the black mass dissolves into a
    dark sky. WHY a steel/violet rim (not pure ink): it stays a HAIR brighter
    than the night sky so the silhouette holds even on the darkest biome phase,
    while the figure paints back ON TOP so interior bands are untouched."""
    mask = pygame.mask.from_surface(surf)
    pts = mask.outline()
    if len(pts) < 2:
        return surf
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(surf, (0, 0))
    return ring


# ── radial accent glow (necrarch precedent) — accents ONLY, never a fill ──────
def radial_glow(radius, color, alpha_center=200, falloff=2.0):
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


def hard_blob(surf, base, pts, shade=None, shade_pts=None,
              band=None, band_pts=None, hi=None, hi_pts=None, ow=2):
    """HARD STEPPED flat shading: ink keyline -> flat base fill -> a discrete
    SHADE band -> an optional mid-tone band -> a discrete rim HIGHLIGHT band.
    Each band is its OWN closed polygon (a hard step), NEVER an interpolated
    gradient — this is the bamboo-v2 sculpted-but-flat read that protects
    true-32px legibility."""
    if ow:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, base, pts)
    if shade and shade_pts:
        pygame.draw.polygon(surf, shade, shade_pts)
    if band and band_pts:
        pygame.draw.polygon(surf, band, band_pts)
    if hi and hi_pts:
        pygame.draw.polygon(surf, hi, hi_pts)
    if ow:
        pygame.draw.polygon(surf, INK, pts, ow)


# ── a single SPLIT-CULM QUILL — a fat blackened bamboo-slat feather ───────────
def split_culm_quill(surf, root, ang, length, width, s, node_at=0.5,
                     wing_node=False):
    """ONE quill = a split blackened culm-slat: a FAT near-parallel-sided plank
    swept along `ang` to a chisel tip. The steely sheen is a FIRM FILL BAND
    across the whole LEADING HALF of the slat face (not a sliver — the night
    legibility gate, KEPT), and the slat carries exactly ONE hard-STEPPED
    NODE-RING — a hard VALUE STEP across the plank at `node_at` (a dark swollen
    ridge then a pale sheath-scar band, both with real width) — so the quill
    reads unmistakably as a SPLIT CULM-SLAT, not a feather, even at 32px.

    WHY `wing_node` (round-3 punch-list #3): when this slat is part of a WING
    (not the staff crook / pillar), the node-ring is drawn with a ~12% hotter
    contrast pair — a DEEPER ridge (WING_NODE_D) + a BRIGHTER sheath-scar
    (WING_NODE_HI) and a hair more ridge width — so the wing slats read as split
    culm at 32px as convincingly as the pillar already does. The PILLAR keeps
    its own (perfect) node key untouched."""
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca                       # perpendicular = quill width axis
    hw = width * 0.5
    tip = (root[0] + ca * length, root[1] + sa * length)
    tw = hw * 0.40                         # blunt chisel tip half-width
    belly = 0.72 * length
    bx = (root[0] + ca * belly, root[1] + sa * belly)

    def w_at(f):                           # half-width tapering root->belly->tip
        return hw if f <= belly / length else hw + (tw - hw) * (
            (f - belly / length) / (1 - belly / length))

    def edge(f, k):                        # point on the slat edge, k in [-1,1]
        cx = root[0] + ca * length * f
        cy = root[1] + sa * length * f
        w = w_at(f)
        return (cx + px * w * k, cy + py * w * k)

    quill = [edge(0.0, 0.92), edge(belly / length, 1.0), edge(1.0, 1.0),
             edge(1.0, -1.0), edge(belly / length, -1.0), edge(0.0, -0.92)]
    pygame.draw.polygon(surf, INK, quill)
    pygame.draw.polygon(surf, BLACK, quill)

    # FIRM STEELY-SHEEN FILL BAND across the whole LEADING HALF of the face.
    # This is the night-legibility anchor (KEPT): a solid steel plane, not a rim.
    lead = [edge(0.0, 0.92), edge(belly / length, 1.0), edge(1.0, 1.0),
            edge(1.0, 0.06), edge(belly / length, 0.10), edge(0.0, 0.10)]
    pygame.draw.polygon(surf, SHEEN, lead)
    # a cool mid step between black + steel so the two planes don't ring harshly
    midb = [edge(0.0, 0.12), edge(belly / length, 0.10), edge(1.0, 0.06),
            edge(1.0, -0.18), edge(belly / length, -0.16), edge(0.0, -0.14)]
    pygame.draw.polygon(surf, SHEEN_MID, midb)

    # ONE hard-STEPPED NODE-RING crossing the slat — the bamboo tell, with WIDTH.
    ridge_col = WING_NODE_D if wing_node else INKVIO
    scar_col = WING_NODE_HI if wing_node else SHEEN_HI
    f = node_at
    nx = root[0] + ca * length * f
    ny = root[1] + sa * length * f
    nw = w_at(f)
    # wing slats get a hair wider ridge so the split-culm step survives downscale
    ridge_fac = 0.36 if wing_node else 0.30
    ridge = max(3, int(width * ridge_fac))   # a band, not a hairline
    a0 = (nx + px * nw, ny + py * nw)
    a1 = (nx - px * nw, ny - py * nw)
    # dark swollen node ridge (a hard value step DOWN across the slat)
    pygame.draw.line(surf, ridge_col, a0, a1, ridge)
    # pale sheath-scar band just up-slat of the ridge (a hard value step UP)
    scar_w = max(2, int(width * (0.18 if wing_node else 0.16)))
    s0 = (nx + ca * ridge * 0.5 + px * nw, ny + sa * ridge * 0.5 + py * nw)
    s1 = (nx + ca * ridge * 0.5 - px * nw, ny + sa * ridge * 0.5 - py * nw)
    pygame.draw.line(surf, scar_col, s0, s1, scar_w)

    # a hot rim on the very leading edge (rim only) — final hard step
    pygame.draw.line(surf, SHEEN_HI, edge(0.04, 0.98), edge(0.96, 0.98),
                     max(1, int(width * 0.10)))
    pygame.draw.polygon(surf, INK, quill, max(2, int(width * 0.14)))


def quill_wing(surf, root, base_ang, s, sign, n=3, big=True, spread=1.0,
               length_fac=1.0):
    """ONE crow-tengu wing per side = a fan of ~3 BIG split-culm quills. Fewer,
    bigger slats let each node-ring survive at 32px; the fan's bases OVERLAP
    through a shared root MANTLE + a base WEB polygon so there are NO 1px light
    pinpricks between quills (the side reads as ONE connected drooping crow-wing).

    WHY `spread` + `length_fac` (round-3 punch-list #1): the two wings are now
    drawn ASYMMETRIC — the LEFT wing is held higher and tighter-swept (smaller
    spread, slightly longer leading primary), the RIGHT wing rakes wider and
    drops lower (bigger spread). This breaks the bilateral dragonfly symmetry
    that made round 2 read as an insect, so the figure reads as a hunched crow-
    tengu mantling its wings. The wing slats pass `wing_node=True` for the lifted
    node-ring contrast (#3)."""
    L = (66.0 if big else 32.0) * s * length_fac
    bw = (19.0 if big else 11.0) * s
    # (downward-sweep°, length-fac, width-fac, node-position) — graded long->short
    # the per-rank sweep is scaled by `spread` so the wide wing rakes further.
    ranks = (
        (0,   1.00, 1.00, 0.48),   # P1 — longest leading primary (the wing tip)
        (40,  0.80, 0.92, 0.52),   # P2 — mid
        (78,  0.58, 0.84, 0.56),   # covert — short, folded under, trailing edge
    )[:n]

    # base WEB: a filled wedge spanning the whole fan so the inter-quill sky gaps
    # are closed at the root — the connecting membrane of the spread wing.
    ca0, sa0 = math.cos(base_ang), math.sin(base_ang)
    aN = base_ang + sign * math.radians(ranks[-1][0] * spread)
    caN, saN = math.cos(aN), math.sin(aN)
    web = [
        (root[0] - sign * int(2 * s), root[1] - int(2 * s)),
        (root[0] + ca0 * L * 0.62, root[1] + sa0 * L * 0.62),
        (root[0] + math.cos(base_ang + sign * math.radians(20 * spread)) * L * 0.5,
         root[1] + math.sin(base_ang + sign * math.radians(20 * spread)) * L * 0.5),
        (root[0] + caN * L * 0.46, root[1] + saN * L * 0.46),
        (root[0] + sign * int(8 * s), root[1] + int(10 * s)),
    ]
    pygame.draw.polygon(surf, INK, web)
    pygame.draw.polygon(surf, BLACK, web)
    # a steely sheen wash on the web's leading edge keeps the membrane on the sky
    pygame.draw.line(surf, SHEEN_MID,
                     (root[0] + ca0 * L * 0.18, root[1] + sa0 * L * 0.18),
                     (root[0] + ca0 * L * 0.60, root[1] + sa0 * L * 0.60),
                     max(2, int(4 * s)))

    # the slats themselves, drawn trailing-first so the leading primary sits on top
    for off, fac, wfac, node_at in reversed(ranks):
        a = base_ang + sign * math.radians(off * spread)
        # nudge each root slightly outward so bases OVERLAP rather than gap
        rt = (root[0] + math.cos(a) * bw * 0.18,
              root[1] + math.sin(a) * bw * 0.18)
        split_culm_quill(surf, rt, a, L * fac, bw * wfac, s, node_at=node_at,
                         wing_node=True)


# ── the black-bamboo STAFF (a real culm — reused for hero grip + pillar shaft) ─
def bamboo_segment(surf, cx, y0, y1, half_w, s, branch=True):
    """One black-bamboo node-segment: a glossy purple-black barrel between two
    swollen NODE rings, banded hard (ink-violet hollow -> black base -> violet
    waxy-bloom mid -> steely vertical sheen rail), with a white sheath-scar ring
    under the node and PAIRED branch-whorl stubs (Phyllostachys = paired). The
    pillar repeat band is built from a stack of these. UNCHANGED in round 3 —
    the pillar cleared the bamboo gate and must be preserved."""
    seg = [(cx - half_w, y0), (cx + half_w, y0),
           (cx + half_w, y1), (cx - half_w, y1)]
    pygame.draw.polygon(surf, INK, seg)
    pygame.draw.polygon(surf, BLACK, seg)
    # violet waxy-bloom mid-band (a hard vertical step, not a gradient)
    pygame.draw.rect(surf, BLOOM,
                     (cx - int(half_w * 0.18), y0, int(half_w * 0.5), y1 - y0))
    # ink-violet shade rail on the right (rounded-culm dark step)
    pygame.draw.rect(surf, INKVIO,
                     (cx + int(half_w * 0.42), y0, int(half_w * 0.58), y1 - y0))
    # steely vertical sheen rail on the left (the legibility band on the culm)
    pygame.draw.rect(surf, SHEEN,
                     (cx - int(half_w * 0.72), y0, int(half_w * 0.30), y1 - y0))
    pygame.draw.rect(surf, SHEEN_HI,
                     (cx - int(half_w * 0.72), y0, max(1, int(half_w * 0.10)), y1 - y0))
    pygame.draw.polygon(surf, INK, seg, max(2, int(2.0 * s)))
    # NODE ring at the TOP of the segment: swollen ridge + pale sheath-scar
    nodes_h = max(3, int(5 * s))
    node = [(cx - int(half_w * 1.12), y0 + nodes_h), (cx - half_w, y0 - nodes_h),
            (cx + half_w, y0 - nodes_h), (cx + int(half_w * 1.12), y0 + nodes_h)]
    pygame.draw.polygon(surf, INK, node)
    pygame.draw.polygon(surf, INKVIO, node)
    # white sheath-scar ring just under the node ridge (the kurochiku tell)
    pygame.draw.line(surf, SHIDE,
                     (cx - half_w, y0 + nodes_h), (cx + half_w, y0 + nodes_h),
                     max(1, int(1.6 * s)))
    pygame.draw.line(surf, SHEEN_HI,
                     (cx - int(half_w * 0.9), y0 - int(nodes_h * 0.4)),
                     (cx + int(half_w * 0.4), y0 - int(nodes_h * 0.4)),
                     max(1, int(1.2 * s)))
    if branch:
        # PAIRED branch-whorl stubs at the node (Phyllostachys signature)
        for sgn in (-1, 1):
            bx = cx + sgn * half_w
            for dy in (-int(3 * s), int(2 * s)):
                tip = (bx + sgn * int(7 * s), y0 + dy - int(4 * s))
                pygame.draw.line(surf, INK, (bx, y0 + dy), tip, max(2, int(2.6 * s)))
                pygame.draw.line(surf, BLACK, (bx, y0 + dy), tip, max(1, int(1.6 * s)))
                pygame.draw.line(surf, SHEEN, (bx, y0 + dy),
                                 (bx + sgn * int(4 * s), y0 + dy - int(2 * s)),
                                 max(1, int(1.0 * s)))


def gold_band(surf, cx, y, half_w, s, h=None):
    """A thin gold staff-band/ferrule ring — one of the two warm focal accents."""
    h = h or max(3, int(5 * s))
    pygame.draw.rect(surf, INK, (cx - half_w - 1, y - 1, half_w * 2 + 2, h + 2))
    pygame.draw.rect(surf, GOLD_D, (cx - half_w, y, half_w * 2, h))
    pygame.draw.rect(surf, GOLD, (cx - half_w, y, half_w * 2, int(h * 0.66)))
    pygame.draw.rect(surf, GOLD_HI, (cx - half_w, y, half_w * 2, max(1, int(h * 0.24))))


def feather_tuft_crook(surf, cx, y, ang, scale, s):
    """The detachable gap-edge CROOK = a tight raked tuft of 3 BIG split-culm
    quills curling toward the gap, given the steel sheen so the cap reads at
    32px. Shared with the head crown. WHY these stay on the PILLAR node key
    (no wing_node): the pillar / gap-cap is perfect and must not be re-keyed."""
    for off, fac, wf, node in ((-26, 0.82, 0.80, 0.5), (0, 1.0, 1.0, 0.5),
                               (22, 0.80, 0.78, 0.5)):
        a = ang + math.radians(off)
        split_culm_quill(surf, (cx, y), a, scale * fac, scale * 0.30 * wf, s,
                         node_at=node)


# ── the crow-tengu HEAD (sharp beak + vermilion wattle + tall feather-tuft) ───
def tengu_head(surf, cx, cy, r, s, lit=True):
    """A hunched crow-tengu skull: a glossy black feathered cranium hard-stepped
    for volume, a tall single FEATHER-TUFT spiking up off the crown (the karasu
    tell + the silhouette breaker), a sharp downward crow BEAK, a hooked vermilion
    NOSE/beak-WATTLE that is the warm focal, and a steely-glinting eye. Realistic
    crow proportions — NOT a chibi big-head.

    WHY round-3 (punch-list #2): the BEAK is rebuilt as a sharp hard-STEPPED
    chisel that juts FORWARD off the vermilion cere (not a soft round oval) so
    'crow-billed' is unmistakable at hero — a long lower mandible carved to a
    fine down-hooked point, two hard value steps along it, and the vermilion
    wattle clamped tight at its base so the warm focal frames the bill."""
    # --- tall single FEATHER-TUFT off the crown (drawn first, behind the dome) -
    # three raked black split-culm blades, longest centre, so the crown notches
    # the outline as a clear spike at 32px (the karasu-tengu read). Raked slightly
    # BACK so it trails behind the hunched/craned head (reinforces the lunge).
    feather_tuft_crook(surf, cx - int(r * 0.22), cy - int(r * 0.7),
                       math.radians(-104), r * 1.7, s)

    # --- cranium dome: a hunched crow head, hard-stepped black ---------------
    # WHY shifted FORWARD (left/-x) vs round 2: the skull now cranes ahead of the
    # torso on the forward-pitched neck so the figure HUNCHES and lunges like a
    # crow, not a centred symmetric bug.
    head = [(cx - int(r * 0.98), cy - int(r * 0.06)),
            (cx - int(r * 0.84), cy - int(r * 0.74)),
            (cx - int(r * 0.14), cy - int(r * 0.98)),
            (cx + int(r * 0.58), cy - int(r * 0.74)),
            (cx + int(r * 0.90), cy - int(r * 0.10)),   # back of skull
            (cx + int(r * 0.78), cy + int(r * 0.50)),
            (cx + int(r * 0.22), cy + int(r * 0.66)),   # cheek toward beak
            (cx - int(r * 0.48), cy + int(r * 0.58)),
            (cx - int(r * 0.92), cy + int(r * 0.32))]
    hard_blob(surf, BLACK, head,
              shade=INKVIO,
              shade_pts=[(cx + int(r * 0.26), cy - int(r * 0.30)),
                         (cx + int(r * 0.90), cy - int(r * 0.10)),
                         (cx + int(r * 0.78), cy + int(r * 0.50)),
                         (cx + int(r * 0.22), cy + int(r * 0.52))],
              band=BLOOM,
              band_pts=[(cx - int(r * 0.14), cy - int(r * 0.40)),
                        (cx + int(r * 0.36), cy - int(r * 0.20)),
                        (cx + int(r * 0.24), cy + int(r * 0.30)),
                        (cx - int(r * 0.14), cy + int(r * 0.20))],
              hi=SHEEN,
              hi_pts=[(cx - int(r * 0.96), cy - int(r * 0.02)),
                      (cx - int(r * 0.80), cy - int(r * 0.66)),
                      (cx - int(r * 0.34), cy - int(r * 0.52)),
                      (cx - int(r * 0.58), cy + int(r * 0.12)),
                      (cx - int(r * 0.88), cy + int(r * 0.24))],
              ow=max(1, int(1.8 * s)))

    # --- sharp downward crow BEAK (black upper) — REBUILT, pushed forward ------
    # WHY (#2): a long, narrow, hard-STEPPED chisel bill that juts forward-down
    # off the cere to a fine down-hooked point — a true crow mandible, not the
    # round wattle-oval of round 2. Two hard value bands run its length.
    beak_root_y = cy + int(r * 0.26)
    beak = [(cx - int(r * 0.48), beak_root_y),               # upper-base, forward
            (cx + int(r * 0.30), beak_root_y + int(r * 0.10)),  # gape behind
            (cx + int(r * 0.06), cy + int(r * 0.66)),        # mid lower mandible
            (cx - int(r * 0.34), cy + int(r * 1.30)),        # sharp tip, forward
            (cx - int(r * 0.66), cy + int(r * 1.22)),        # down-hook curl
            (cx - int(r * 0.56), cy + int(r * 0.62))]        # under-cere, forward
    hard_blob(surf, BLACK, beak,
              shade=INKVIO,
              # dark trailing/upper plane of the bill (the shaded back face)
              shade_pts=[(cx - int(r * 0.06), beak_root_y + int(r * 0.04)),
                         (cx + int(r * 0.30), beak_root_y + int(r * 0.10)),
                         (cx + int(r * 0.06), cy + int(r * 0.66)),
                         (cx - int(r * 0.22), cy + int(r * 1.10))],
              hi=SHEEN,
              # lit leading edge of the bill (the front cutting face)
              hi_pts=[(cx - int(r * 0.46), beak_root_y + int(r * 0.02)),
                      (cx - int(r * 0.30), beak_root_y + int(r * 0.04)),
                      (cx - int(r * 0.40), cy + int(r * 1.10)),
                      (cx - int(r * 0.58), cy + int(r * 0.74))],
              ow=max(1, int(1.6 * s)))
    # the beak's cutting edge — a hard steely glint along the leading mandible
    pygame.draw.line(surf, SHEEN_HI,
                     (cx - int(r * 0.50), beak_root_y + int(r * 0.06)),
                     (cx - int(r * 0.40), cy + int(r * 1.18)), max(1, int(1.6 * s)))
    # a hard nostril notch step where the bill meets the cere (crow tell)
    pygame.draw.line(surf, INKVIO,
                     (cx - int(r * 0.28), beak_root_y + int(r * 0.16)),
                     (cx - int(r * 0.04), cy + int(r * 0.50)), max(2, int(2.0 * s)))

    # --- vermilion NOSE / beak-WATTLE: a hooked fleshy ridge clamping the cere -
    # THE warm focal. Now sits TIGHT at the bill base (the cere), framing the
    # pushed beak rather than reading as the beak itself.
    wat = [(cx - int(r * 0.44), cy + int(r * 0.04)),
           (cx + int(r * 0.30), cy + int(r * 0.10)),
           (cx + int(r * 0.16), cy + int(r * 0.34)),
           (cx - int(r * 0.50), cy + int(r * 0.30))]
    hard_blob(surf, VERM, wat,
              shade=VERM_D,
              shade_pts=[(cx + int(r * 0.0), cy + int(r * 0.10)),
                         (cx + int(r * 0.30), cy + int(r * 0.10)),
                         (cx + int(r * 0.16), cy + int(r * 0.34)),
                         (cx + int(r * 0.0), cy + int(r * 0.30))],
              hi=VERM_HI,
              hi_pts=[(cx - int(r * 0.42), cy + int(r * 0.08)),
                      (cx - int(r * 0.16), cy + int(r * 0.10)),
                      (cx - int(r * 0.22), cy + int(r * 0.22)),
                      (cx - int(r * 0.40), cy + int(r * 0.22))],
              ow=max(1, int(1.4 * s)))
    if lit:
        # a small vermilion accent glow so the focal reads at distance (accent only)
        g = radial_glow(max(3, int(r * 0.5)), VERM, alpha_center=120, falloff=2.4)
        surf.blit(g, (cx - int(r * 0.1) - g.get_width() // 2,
                      cy + int(r * 0.26) - g.get_height() // 2),
                  special_flags=pygame.BLEND_ADD)

    # --- eye: a steely glint set in the black brow (the bird stare) -----------
    # WHY shifted forward over the bill: a hunched crow eye sits ahead, glaring
    # down the pushed beak.
    ex, ey = cx + int(r * 0.16), cy - int(r * 0.10)
    pygame.draw.circle(surf, INK, (ex, ey), max(2, int(r * 0.20)))
    pygame.draw.circle(surf, SHEEN, (ex, ey), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, SHEEN_HI, (ex - int(r * 0.04), ey - int(r * 0.04)),
                       max(1, int(r * 0.06)))
    pygame.draw.circle(surf, INK, (ex, ey), max(1, int(r * 0.05)))   # hard pupil


# ── the spread-wing hero ──────────────────────────────────────────────────────
def draw_tengu(surf, cx, cy, s):
    """Hunched black-bamboo crow-tengu: REALISTIC (non-chibi) proportions — a tall
    hunched torso, two angular split-culm quill-wings spread, a crow head with a
    tall feather-tuft on top, gripping a black-bamboo staff held on-axis. `s` =
    unit scale around a ~150-unit-tall figure. Drawn back-to-front: wings ->
    staff -> torso -> arms/claws -> head last so the beak owns the read.

    WHY round-3 (punch-list #1): the head + shoulders are HUNCHED forward (head
    craned ahead on a forward-pitched neck) and the two wings are ASYMMETRIC —
    the LEFT wing is held higher and tighter (smaller spread, longer leading
    primary), the RIGHT drops lower and rakes wider — so the bilateral dragonfly
    symmetry of round 2 is broken and the figure reads as a hunched, mantling
    crow-tengu. Re-verified on the 32px chip: the wings stay one connected mass."""
    # WHY a forward neck lean: the whole upper body cants forward (head + shoulder
    # forward of the hips) so the pose hunches like a perched crow about to strike.
    lean = int(8 * s)                       # forward (−x) cant of the head/neck
    shoulder_y = cy - int(26 * s)
    shoulder_dx = int(16 * s)
    head_c = (cx - lean, cy - int(56 * s))   # head craned ahead + slightly higher
    hr = int(20 * s)

    # === WINGS — two ASYMMETRIC spread crow-wings of ~3 BIG split-culm quills ==
    # LEFT wing roots higher on the hunched shoulder; RIGHT roots a touch lower.
    wL = (cx - shoulder_dx, shoulder_y - int(6 * s))
    wR = (cx + shoulder_dx, shoulder_y + int(4 * s))
    # LEFT: held HIGHER + tighter-swept (smaller spread) + slightly longer tip.
    quill_wing(surf, wL, math.radians(214), s, sign=-1, n=3, big=True,
               spread=0.78, length_fac=1.08)
    # RIGHT: drops lower + rakes WIDER (bigger spread) + a hair shorter.
    quill_wing(surf, wR, math.radians(-18), s, sign=+1, n=3, big=True,
               spread=1.22, length_fac=0.94)

    # === STAFF — a black-bamboo culm held vertically, slightly off the centre =
    stx = cx - int(20 * s)
    s_top = cy - int(64 * s)
    s_bot = cy + int(64 * s)
    hw = max(3, int(4.2 * s))
    seg_h = int(26 * s)
    y = s_top
    while y < s_bot:
        bamboo_segment(surf, stx, y, min(y + seg_h, s_bot), hw, s, branch=True)
        y += seg_h
    # gold ferrule near the grip + a fresh green node-shoot collar at the top
    gold_band(surf, stx, cy + int(2 * s), hw + int(2 * s), s)
    for sgn in (-1, 1):
        leaf = [(stx, s_top + int(2 * s)),
                (stx + sgn * int(10 * s), s_top - int(8 * s)),
                (stx + sgn * int(4 * s), s_top - int(1 * s))]
        pygame.draw.polygon(surf, INK, leaf)
        pygame.draw.polygon(surf, SHOOT_D, leaf)
        pygame.draw.polygon(surf, SHOOT,
                            [(stx, s_top + int(1 * s)),
                             (stx + sgn * int(7 * s), s_top - int(5 * s)),
                             (stx + sgn * int(3 * s), s_top)])

    # === TORSO — a tall hunched feathered body (REALISTIC, not chibi) =========
    # WHY the top of the torso leans forward: the shoulders pitch toward the
    # craned head so the spine hunches (not a vertical bug thorax).
    torso = [(cx - int(15 * s) - lean, shoulder_y - int(2 * s)),
             (cx + int(17 * s) - lean, shoulder_y - int(4 * s)),   # hunched shoulder, forward
             (cx + int(15 * s), cy + int(26 * s)),
             (cx + int(6 * s), cy + int(46 * s)),
             (cx - int(8 * s), cy + int(44 * s)),
             (cx - int(16 * s), cy + int(22 * s))]
    hard_blob(surf, BLACK, torso,
              shade=INKVIO,
              shade_pts=[(cx + int(2 * s) - lean, shoulder_y),
                         (cx + int(16 * s) - lean, shoulder_y - int(3 * s)),
                         (cx + int(14 * s), cy + int(26 * s)),
                         (cx + int(4 * s), cy + int(40 * s))],
              band=BLOOM,
              band_pts=[(cx - int(6 * s), cy - int(6 * s)),
                        (cx + int(6 * s), cy - int(4 * s)),
                        (cx + int(4 * s), cy + int(28 * s)),
                        (cx - int(6 * s), cy + int(26 * s))],
              hi=SHEEN,
              hi_pts=[(cx - int(15 * s) - lean, shoulder_y),
                      (cx - int(6 * s) - lean, shoulder_y - int(1 * s)),
                      (cx - int(8 * s), cy + int(14 * s)),
                      (cx - int(15 * s), cy + int(16 * s))],
              ow=max(1, int(1.8 * s)))
    # breast-feather chevrons — round-3 punch-list #4: the stacked abdomen-segment
    # read is BROKEN. The lowest chevron row is DROPPED (2 rows, not 3) and the
    # two survivors are OFFSET / asymmetric (different x-centres + widths) so they
    # read as loose mantle feathers, not stacked insect segments.
    chevs = ((shoulder_y + int(11 * s), int(12 * s), -int(2 * s)),
             (shoulder_y + int(23 * s), int(8 * s),  int(3 * s)))
    for fy, fw, cxo in chevs:
        bx = cx + cxo
        pygame.draw.lines(surf, INKVIO, False,
                          [(bx - fw, fy), (bx + int(1 * s), fy + int(5 * s)),
                           (bx + fw, fy)], max(1, int(1.6 * s)))
        pygame.draw.lines(surf, SHEEN, False,
                          [(bx - fw, fy - int(2 * s)), (bx + int(1 * s), fy + int(3 * s)),
                           (bx + fw, fy - int(2 * s))], max(1, int(1.0 * s)))

    # === ARM/HAND gripping the staff (a clawed black hand on the culm) ========
    hand_y = cy + int(4 * s)
    arm = [(cx - int(8 * s) - lean, shoulder_y + int(6 * s)),
           (cx - int(20 * s), cy - int(6 * s)),
           (cx - int(22 * s), hand_y),
           (cx - int(14 * s), hand_y + int(4 * s)),
           (cx - int(6 * s), cy)]
    hard_blob(surf, BLACK, arm,
              shade=INKVIO,
              shade_pts=[(cx - int(8 * s) - lean, shoulder_y + int(8 * s)),
                         (cx - int(14 * s), cy - int(4 * s)),
                         (cx - int(14 * s), hand_y + int(2 * s)),
                         (cx - int(7 * s), cy)],
              hi=SHEEN,
              hi_pts=[(cx - int(18 * s), cy - int(4 * s)),
                      (cx - int(20 * s), cy - int(6 * s)),
                      (cx - int(22 * s), hand_y),
                      (cx - int(20 * s), hand_y)],
              ow=max(1, int(1.6 * s)))
    # three small claw-toes curling onto the staff
    for k in range(3):
        ty = hand_y - int(4 * s) + k * int(5 * s)
        tip = (stx - hw - int(1 * s), ty + int(2 * s))
        pygame.draw.line(surf, INK, (cx - int(20 * s), ty), tip, max(2, int(2.6 * s)))
        pygame.draw.line(surf, SHEEN, (cx - int(20 * s), ty), tip, max(1, int(1.2 * s)))

    # === scapula feather-mantle where the wings root (covers the join) ========
    # WHY enlarged + asymmetric: it bridges the two wings' base WEBs into the torso
    # so the whole spread reads as one connected feathered mass (no root pinpricks).
    # The LEFT mantle rides higher to match the higher-held left wing.
    for sgn in (-1, 1):
        kx = cx + sgn * shoulder_dx
        ky = shoulder_y - (int(6 * s) if sgn < 0 else -int(4 * s))
        mant = [(kx - sgn * int(10 * s), ky + int(8 * s)),
                (kx - sgn * int(7 * s), ky - int(9 * s)),
                (kx + sgn * int(7 * s), ky - int(11 * s)),
                (kx + sgn * int(13 * s), ky - int(1 * s)),
                (kx + sgn * int(8 * s), ky + int(10 * s))]
        hard_blob(surf, BLACK, mant,
                  shade=INKVIO,
                  shade_pts=[(kx, ky + int(7 * s)),
                             (kx + sgn * int(11 * s), ky),
                             (kx + sgn * int(6 * s), ky + int(8 * s))],
                  hi=SHEEN,
                  hi_pts=[(kx - sgn * int(6 * s), ky - int(8 * s)),
                          (kx + sgn * int(2 * s), ky - int(10 * s)),
                          (kx - sgn * int(1 * s), ky - int(1 * s))],
                  ow=max(1, int(1.2 * s)))

    # === HEAD last — beak + vermilion wattle own the focal ====================
    # the neck now runs at a forward slant (craned head ahead of the shoulder) so
    # the hunch reads — a hard ink/black/sheen banded column on the diagonal.
    neck_top = (head_c[0], head_c[1] + int(hr * 0.9))
    neck_bot = (cx - int(2 * s), shoulder_y - int(2 * s))
    pygame.draw.line(surf, INK, neck_top, neck_bot, max(2, int(7 * s)))
    pygame.draw.line(surf, BLACK, neck_top, neck_bot, max(1, int(4 * s)))
    pygame.draw.line(surf, SHEEN,
                     (neck_top[0] - int(2 * s), neck_top[1]),
                     (neck_bot[0] - int(2 * s), neck_bot[1]), max(1, int(1.2 * s)))
    tengu_head(surf, head_c[0], head_c[1], hr, s, lit=True)


# ── the black-bamboo STAFF → pillar mirror ────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The black-bamboo STAFF IS the pillar: a black node-segment shaft = the
    tileable repeat band; the gap-edge cap = a feather-tuft CROOK hung with a
    small white shide (paper streamer); the lower mirror = the gold ferrule + a
    curled fresh shoot. Slim, on-axis, bottom-rooted. `cap` names the END facing
    the GAP. UNCHANGED in round 3 — the pillar + gap-cap cleared both gates and
    is preserved exactly (the node-ring lift is wing-only, not here)."""
    half_w = int(11 * s)
    seg_h = int(30 * s)
    cap_room = int(54 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    # === tileable black node-segment shaft ===================================
    y = b0
    while y < b1:
        bamboo_segment(surf, cx, y, min(y + seg_h, b1), half_w, s, branch=True)
        y += seg_h

    if cap == "bottom":
        # === gap-edge cap: ENLARGED feather-tuft CROOK hung with a shide ======
        crook_y = bot - int(34 * s)
        gold_band(surf, cx, crook_y - int(8 * s), half_w + int(3 * s), s,
                  h=int(7 * s))
        # the crook = a bigger tight raked tuft of 3 sheened quills toward the gap
        feather_tuft_crook(surf, cx, crook_y, math.radians(90 - 6), 44 * s, s)
        # a small white shide (zigzag paper streamer) hanging off the crook
        sx0 = cx + int(11 * s)
        zig = [(sx0, crook_y), (sx0 + int(6 * s), crook_y + int(9 * s)),
               (sx0, crook_y + int(16 * s)), (sx0 + int(6 * s), crook_y + int(24 * s)),
               (sx0, crook_y + int(30 * s))]
        pygame.draw.lines(surf, INK, False, zig, max(2, int(3 * s)))
        pygame.draw.lines(surf, SHIDE, False, zig, max(1, int(2.0 * s)))
    else:
        # === lower mirror: gold ferrule + a curled fresh shoot (TRIMMED) ======
        ferrule_y = top + int(20 * s)
        gold_band(surf, cx, ferrule_y, half_w + int(3 * s), s, h=int(8 * s))
        cxs = cx
        cys = top + int(10 * s)
        shoot = [(cxs - int(3 * s), ferrule_y),
                 (cxs - int(6 * s), cys + int(5 * s)),
                 (cxs - int(1 * s), cys),
                 (cxs + int(4 * s), cys + int(3 * s)),
                 (cxs + int(2 * s), ferrule_y)]
        pygame.draw.polygon(surf, INK, shoot)
        pygame.draw.polygon(surf, SHOOT_D, shoot)
        pygame.draw.polygon(surf, SHOOT,
                            [(cxs - int(2 * s), ferrule_y),
                             (cxs - int(5 * s), cys + int(5 * s)),
                             (cxs - int(1 * s), cys + int(2 * s))])


# ── compose the review sheet (asthi_garuda multi-panel convention) ────────────
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
    sheet.blit(font_big.render("KUROCHIKU-GARASU-TENGU", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "black-bamboo crow-tengu  ·  WINGED BEAKED TENGU · HUNCHED + ASYMMETRIC wings (anti-insect) · pushed crow beak · lifted wing node-rings · bamboo v2 REALISTIC · round 3 (FINAL)",
        True, LABEL_DIM), (24, 42))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_tengu(big, 184 * SS, 250 * SS, 1.78 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        # containing rim first (the night-edge keeper), then the ink keyline pop
        small = grow_rim(small, RIMVIO + (235,), 1)
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("HUNCHED crow-tengu (head craned forward), ASYMMETRIC wings (L higher/tighter, R", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("lower/wider) breaking the dragonfly read; pushed sharp crow beak off the vermilion", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("cere; broken 2-row breast mantle (no abdomen bands). Grips a black-bamboo staff.", True, LABEL_DIM), (14, 622))

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
    pygame.draw.rect(sheet, (40, 38, 52), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — bamboo staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("black node-segment shaft = repeat band;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("feather-tuft crook + shide = gap-cap;", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("gold ferrule + shoot = even mirror (UNCHANGED).", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_tengu(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_rim(small, RIMVIO + (235,), 1)
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
    sheet.blit(font_sm.render("32px on night sky (black-on-black test)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blacked-out 32px silhouette — must read ONLY as a winged beaked tengu
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_tengu(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        return mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))

    sil_y = night_y + 188
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 214, 220), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 30))
    sheet.blit(font_sm.render("HUNCHED + ASYMMETRIC winged tengu", True, LABEL_DIM), (sx + 104, sil_y + 48))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.30 * SS, cap="bottom")
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
        (BLACK, "black-culm"), (INKVIO, "ink-violet sh"),
        (SHEEN, "steely sheen"), (RIMVIO, "violet rim"),
        (VERM, "vermilion wattle"), (GOLD, "gold band"),
        (SHOOT, "fresh shoot"), (INK, "ink keyline"),
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
        "bamboo v2 REALISTIC (FINAL): SS=6 supersample -> smoothscale.  4-6 HARD STEPPED value bands (NO gradients) · hard ink keyline (28,22,30) + 1px outline + violet rim · "
        "firm steel-sheen quill FACES + ONE hard node-ring/slat (wing-slat contrast +12%) · radial glow accents only · pillar/gap-cap UNCHANGED · procedural-only.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
