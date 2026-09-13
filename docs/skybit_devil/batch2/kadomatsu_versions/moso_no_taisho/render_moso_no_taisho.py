"""
Round-1 concept renderer for MOSO-NO-TAISHO — the great single-culm bamboo
MONOLITH (Kadomatsu brood, direction #1, the set's spine). Headless Pygame;
ELEVATED-REALISM pipeline (supersample SS=6 -> smoothscale) cloned verbatim
from the parent KADOMATSU-SHIN harness so the slant-cut hollow-ring mouth,
node geometry and bands stay crisp at downscale.

WHY this is the DELIBERATE ANTI-PARENT: the parent is a slim STEPPED TRIO of
three separate culms. Moso is the inverse — ONE titanic standing-stone of
bamboo, WIDER than any single element in the brood, capped by a single
COLOSSAL slant-cut. The epic hook is awe through SCALE + RESTRAINT (a
megalith), so the form carries almost no incident detail: a fat shaft, 5-6
BIG node collars, one giant cream cut-disc, and just enough base-anchored
foot-kit (straw cinch + plum + ONE pine sprig) that the monolith isn't inert.
It is the purest, most unmistakable bamboo read of the set.

HELD-APART ACCENT — KINTSUGI GOLD-VEIN: a THIN ~2px hairline of gold
(212,180,96) tracing the node-collars ONLY. It is line-WORK, never a glow
fill — deliberately kept distinct from the soft pale-gold blessing GLOW that
sits at the foot. At 32px the veins must stay hairlines so they don't boil
into noise; they read as a faint warm seam at each node, not a texture.

MUST-FIX (the gate, per locked brief #1):
  - the giant cut-disc fills ~the TOP QUARTER of the column and stays the
    BRIGHTEST value on the whole form, so at true 32px it collapses to ONE
    unmissable cream disc;
  - the column carries 5-6 BIG node collars — this is the only direction with
    room for node geometry to read LARGE, so the collars are fat and widely
    spaced (the bamboo tell that survives the blur);
  - gold veins <=2px hairlines;
  - foot-kit base-anchored, never top-heavy.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the helpers
cloned from the parent KADOMATSU-SHIN harness.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (cloned verbatim from kadomatsu_shin/render_round_2.py) ────
# Warm fresh-cut festive green family; cut-CREAM mouth is the focal POP;
# vermilion plum + soft pale-gold blessing glow the base accents. 4-6 HARD
# stepped bands per form, ZERO gradients.
CULM      = (124, 188, 104)   # fresh-culm green
CULM_D    = ( 74, 138,  72)   # deep node-green shade
CULM_DD   = ( 50, 102,  56)   # deepest groove / node-collar shadow band
CULM_HI   = (172, 216, 130)   # sun-side fresh-green highlight band
CULM_HOT  = (208, 232, 158)   # hottest green sheen rail (top-left sun)
CULM_RIM  = (158, 206, 116)   # thin WARM rim-keyline on culm edges (night hold)
CULM_BACK = ( 58, 116,  62)   # back-culm body green (stepped depth; unused on a monolith but kept for palette parity)
CUT_CREAM = (224, 214, 170)   # pale diagonal-cut ring-wall (the signature POP)
CUT_HI    = (244, 238, 206)   # lit cut-rim sheen — BRIGHTEST value on the form
CUT_D     = (180, 166, 120)   # cut-ring shade (cavity-side lip)
CAVITY    = (118, 128,  92)   # the hollow inner cavity (lightened — a disc, not hole)
CAVITY_DD = ( 86,  98,  70)   # cavity floor
STRAW     = (206, 176, 104)   # woven straw-rope collar
STRAW_D   = (150, 120,  62)   # straw shade between strands
STRAW_HI  = (234, 210, 144)   # straw highlight strand
PLUM      = (216,  80,  60)   # auspicious vermilion plum + face-mark (accent)
PLUM_D    = (158,  48,  40)   # plum shade
PLUM_HI   = (248, 138, 116)   # plum petal highlight
PINE      = ( 58, 104,  62)   # pine needle-fan green
PINE_D    = ( 38,  74,  46)   # pine shade
PINE_HI   = ( 96, 142,  88)   # pine lit needle
GLOW      = (244, 224, 150)   # soft pale-gold blessing glow (radial, accent only)
FACE      = (240, 230, 188)   # serene bound-face plane (gold-touched cream)
FACE_D    = (196, 178, 132)   # face shade band
INK       = ( 28,  22,  30)   # hard ink keyline

# HELD-APART ACCENT: kintsugi gold-vein hairline. WHY a separate constant from
# GLOW: the vein is opaque metallic LINE-WORK at the node-collars; the blessing
# GLOW is a soft additive bloom at the foot — keeping them distinct colours
# stops the accent from reading as the same auspicious gold twice.
KINTSUGI  = (212, 180,  96)   # kintsugi gold-vein hairline (node-collars only)
KINTSUGI_HI = (240, 214, 150) # tiny lit fleck on a vein (a glint, not a glow)

BG        = ( 60,  74,  58)   # muted grove-green review backdrop
PANEL     = ( 46,  58,  46)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 230)
LABEL_DIM = (196, 204, 184)

SS = 6


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
    """Parent precedent — accent-only soft bloom. Used ONLY for the auspicious
    pale-gold blessing glow at the foot, never as a fill."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


# ── a fresh madake CULM segment — HARD STEPPED bands, no gradient ─────────────
# WHY this monolith variant adds a kintsugi gold-vein at each node-collar: the
# brief's held-apart accent is THIN line-work tracing the collars ONLY. The
# extra `node_y_out` channel lets the hero collect the world-space node Y's so
# the gold vein + (optional) big-collar emphasis is drawn ON TOP after the
# shaft, never buried under the bands. Kept opt-in so the pillar/chip paths can
# skip it cheaply.
def culm_shaft(surf, cx, top, bot, half_w, s, node_pitch, body_col=CULM,
               shade_col=CULM_D, deep_col=CULM_DD, kintsugi=False,
               node_y_out=None):
    """A vertical living-bamboo shaft built as a stack of node-segments, each
    lit with 4 HARD STEPPED value bands across its width (sheen rail | hi | fill
    | deep) — NO smooth gradient — so it reads as a turned cylinder of fresh
    green at 32px. Node rings are the two-ring madake collar: a hard CULM_DD
    groove with a pale swollen ring above it.

    On the MONOLITH the collars are deliberately FAT + widely spaced (the only
    direction with room for big node geometry); when `kintsugi` is set a <=2px
    gold hairline rides the groove of each collar (the held-apart accent). The
    cut mouth caps the top (caller)."""
    lw = max(2, int(1.6 * s))
    # body fill column (rounded top so the cut/cap sits on a real culm end)
    body = [(cx - half_w, bot), (cx - half_w, top + half_w),
            (cx, top), (cx + half_w, top + half_w), (cx + half_w, bot)]
    pygame.draw.polygon(surf, INK, body)
    pygame.draw.polygon(surf, body_col, body)
    # 4 HARD vertical value bands across the cylinder (right = shade, left = sun)
    hi_col = CULM_HI if body_col is CULM else lerp(body_col, CULM_HI, 0.45)
    bands = ((-1.00, -0.46, hi_col), (-0.46, -0.16, body_col),
             (-0.16, 0.42, body_col), (0.42, 1.00, shade_col))
    for x0, x1, col in bands:
        bx0 = cx + int(half_w * x0)
        bx1 = cx + int(half_w * x1)
        pygame.draw.polygon(surf, col, [
            (bx0, top + half_w), (bx1, top + half_w), (bx1, bot), (bx0, bot)])
    # hottest sun rail down the far-left edge (a thin hard band, not a blur)
    rail = max(2, int(half_w * 0.16))
    rail_col = CULM_HOT if body_col is CULM else CULM_HI
    pygame.draw.rect(surf, rail_col,
                     (cx - half_w, top + half_w, rail, bot - (top + half_w)))
    # NODE RINGS — two-ring madake collar, repeated at node_pitch. WHY the
    # groove + swollen ring are scaled up on the monolith: at this width the
    # node geometry is the bamboo tell that has to survive 32px, so the collar
    # is rendered FAT (a wide hard groove + a tall pale bulge above it).
    groove_h = max(2, int(3.4 * s))
    bulge_h = max(2, int(3.6 * s))
    y = bot - node_pitch
    while y > top + half_w + node_pitch * 0.3:
        if node_y_out is not None:
            node_y_out.append(y)
        # hard dark groove (fat)
        pygame.draw.rect(surf, deep_col,
                         (cx - half_w, y, half_w * 2, groove_h))
        # swollen pale ring just above the groove (the node bulge)
        ring_col = CULM_HOT if body_col is CULM else CULM_HI
        pygame.draw.rect(surf, ring_col,
                         (cx - half_w, y - bulge_h, half_w * 2,
                          max(1, int(2.2 * s))))
        # tiny paired branch-stub nub at the node (Phyllostachys/madake tell)
        nub = max(2, int(2.6 * s))
        pygame.draw.polygon(surf, shade_col, [
            (cx - half_w, y - int(0.5 * s)),
            (cx - half_w - nub, y - nub),
            (cx - half_w - nub, y + int(1.2 * s))])
        # KINTSUGI GOLD-VEIN: a <=2px hairline riding the groove. Drawn as a
        # main seam plus a couple of short branching fractures so it reads like
        # a repaired crack, not a painted stripe — but kept thin enough that
        # the 32px downscale renders one faint warm seam at the node.
        if kintsugi:
            vw = max(1, min(int(2 * s), int(2.0 * s)))
            gy = y + groove_h // 2
            pygame.draw.line(surf, KINTSUGI, (cx - half_w, gy),
                             (cx + half_w, gy), vw)
            # short branching fractures off the seam (the kintsugi tell)
            frac = int(half_w * 0.34)
            pygame.draw.line(surf, KINTSUGI,
                             (cx - int(half_w * 0.40), gy),
                             (cx - int(half_w * 0.40) + frac,
                              gy - max(2, int(3 * s))), max(1, int(1.2 * s)))
            pygame.draw.line(surf, KINTSUGI,
                             (cx + int(half_w * 0.30), gy),
                             (cx + int(half_w * 0.30) - frac,
                              gy + max(2, int(3 * s))), max(1, int(1.2 * s)))
            # a single lit fleck so the vein reads metallic, not flat paint
            pygame.draw.circle(surf, KINTSUGI_HI,
                               (cx - int(half_w * 0.18), gy),
                               max(1, int(1.2 * s)))
        y -= node_pitch
    # thin WARM rim-keyline on the two long edges (the night-hold)
    rim = max(1, int(1.1 * s))
    pygame.draw.line(surf, CULM_RIM, (cx - half_w, top + half_w),
                     (cx - half_w, bot), rim)
    pygame.draw.line(surf, CULM_RIM, (cx + half_w, top + half_w),
                     (cx + half_w, bot), rim)
    pygame.draw.polygon(surf, INK, body, lw)


# ── the DIAGONAL-CUT MOUTH — the signature: bright cream DISC + small cavity ──
def diagonal_cut(surf, cx, top, half_w, s, lean=0.62, dominance=1.0):
    """The steep sogi slant-cut culm-mouth: a bright OVAL of cut-CREAM ring-wall
    surrounding a SMALL inner CAVITY, tilted so the high lip is on the left. The
    lit upper-left sheen (CUT_HI) is the single BRIGHTEST value on the form. On
    the monolith `dominance` is pushed so the disc fills ~the top quarter of the
    column and collapses to ONE unmissable cream disc at 32px."""
    ew = int((half_w + int(1.4 * s)) * (1.0 + 0.62 * dominance))
    eh = int((half_w * lean + int(2 * s)) * (1.0 + 0.55 * dominance))
    ccx, ccy = cx, top
    # outer ink rim of the cut oval
    outer = pygame.Rect(ccx - ew, ccy - eh, ew * 2, eh * 2)
    pygame.draw.ellipse(surf, INK, outer.inflate(int(2.4 * s), int(2.4 * s)))
    # the pale cut-CREAM ring-WALL (the bright signature band, fat)
    pygame.draw.ellipse(surf, CUT_CREAM, outer)
    # lit upper-left sheen on the ring-wall — BRIGHTEST value (a hard crescent)
    sheen = pygame.Rect(ccx - ew, ccy - eh, int(ew * 1.5), int(eh * 1.5))
    pygame.draw.ellipse(surf, CUT_HI, sheen)
    pygame.draw.ellipse(surf, CUT_CREAM,
                        sheen.inflate(-int(ew * 0.42), -int(eh * 0.42)))
    # shade lip on the lower-right of the ring-wall (cavity-side)
    pygame.draw.arc(surf, CUT_D, outer.inflate(-int(1.5 * s), -int(1.5 * s)),
                    math.radians(250), math.radians(20), max(2, int(2.6 * s)))
    # the INNER CAVITY — a SMALL dark-green oval inset (hollow read kept subtle
    # so the cream disc stays dominant at 32px). ~0.42 of the oval, offset down.
    iw, ih = int(ew * 0.42), int(eh * 0.42)
    cav = pygame.Rect(ccx - iw, ccy - ih + int(eh * 0.20), iw * 2, ih * 2)
    pygame.draw.ellipse(surf, INK, cav.inflate(int(1.4 * s), int(1.4 * s)))
    pygame.draw.ellipse(surf, CAVITY, cav)
    # deepest cavity floor offset down-right (the hollow has just enough depth)
    floor = pygame.Rect(ccx - int(iw * 0.5) + int(iw * 0.3),
                        ccy - int(ih * 0.5) + int(eh * 0.20) + int(ih * 0.5),
                        int(iw * 1.0), int(ih * 0.9))
    pygame.draw.ellipse(surf, CAVITY_DD, floor)
    pygame.draw.ellipse(surf, INK, outer, max(1, int(1.4 * s)))


# ── a woven straw-rope COLLAR band (the waist binding) ────────────────────────
def straw_collar(surf, cx, cy, half_w, h, s):
    """The woven rice-straw rope at the waist: a fat band of diagonal STRANDS
    (alternating lit/shade so it reads woven, not a smooth ring) wrapping the
    bundle. HARD STEPPED — each strand its own value, no blur. A short paired
    knot-tail hangs straight DOWN at the centre (a knot, never out-flung arms,
    so the silhouette KIND stays a clean column)."""
    band = pygame.Rect(cx - half_w - int(3 * s), cy - h // 2,
                       (half_w + int(3 * s)) * 2, h)
    pygame.draw.rect(surf, INK, band.inflate(int(2 * s), int(2 * s)))
    pygame.draw.rect(surf, STRAW_D, band)
    # diagonal woven strands — alternating value bands (the woven tell)
    strand_w = max(3, int(4.2 * s))
    x = band.left - h
    i = 0
    while x < band.right + h:
        col = STRAW_HI if i % 3 == 0 else (STRAW if i % 3 == 1 else STRAW_D)
        pygame.draw.polygon(surf, col, [
            (x, band.bottom), (x + strand_w, band.bottom),
            (x + strand_w + h, band.top), (x + h, band.top)])
        x += strand_w
        i += 1
    # top + bottom rim grooves so the band reads bound tight
    pygame.draw.rect(surf, STRAW_D, (band.left, band.top, band.width, max(2, int(2 * s))))
    pygame.draw.rect(surf, INK, (band.left, band.bottom - max(2, int(2 * s)),
                                 band.width, max(2, int(2 * s))))
    pygame.draw.rect(surf, INK, band, max(1, int(1.4 * s)))
    # a single short paired knot-tail dropping STRAIGHT down at centre
    for sgn in (-1, 1):
        tx = cx + sgn * int(4 * s)
        pygame.draw.polygon(surf, STRAW, [
            (tx - int(3 * s), band.bottom),
            (tx + int(3 * s), band.bottom),
            (tx + int(2 * s), band.bottom + int(11 * s)),
            (tx - int(2 * s), band.bottom + int(11 * s))])
        pygame.draw.polygon(surf, STRAW_D, [
            (tx, band.bottom),
            (tx + int(3 * s), band.bottom),
            (tx + int(2 * s), band.bottom + int(11 * s))])


# ── a pine NEEDLE-FAN (base sprig) ────────────────────────────────────────────
def pine_fan(surf, root, base_ang, spread, n, length, s, sign=1):
    """A fan of pine needles: n hard tapered needle-blades radiating from `root`
    across `spread`, graded in length, alternating lit/shade so the fan reads as
    discrete clumps (NOT fuzz)."""
    for k in range(n):
        t = k / max(1, n - 1)
        a = base_ang + sign * (t - 0.5) * spread
        L = length * (0.78 + 0.22 * math.sin(t * math.pi))
        ca, sa = math.cos(a), math.sin(a)
        px, py = -sa, ca
        hw = max(2, int(2.0 * s))
        tip = (root[0] + ca * L, root[1] + sa * L)
        nd = [(root[0] + px * hw, root[1] + py * hw),
              (tip[0] + px * hw * 0.3, tip[1] + py * hw * 0.3),
              (tip[0] - px * hw * 0.3, tip[1] - py * hw * 0.3),
              (root[0] - px * hw, root[1] - py * hw)]
        col = PINE_HI if k % 2 == 0 else PINE
        pygame.draw.polygon(surf, PINE_D, [(x + 1, y + 1) for (x, y) in nd])
        pygame.draw.polygon(surf, col, nd)


# ── a vermilion PLUM blossom (base accent) ────────────────────────────────────
def plum_blossom(surf, cx, cy, r, s):
    """A five-petal red-plum blossom: HARD STEPPED petals (shade ring -> petal ->
    highlight pip) with a pale-gold pip centre. Base-anchored only."""
    for k in range(5):
        a = math.radians(-90 + k * 72)
        px = cx + math.cos(a) * r
        py = cy + math.sin(a) * r
        pygame.draw.circle(surf, INK, (int(px), int(py)), int(r * 0.62) + 1)
        pygame.draw.circle(surf, PLUM_D, (int(px), int(py)), int(r * 0.62))
        pygame.draw.circle(surf, PLUM, (int(px), int(py)), int(r * 0.48))
        pygame.draw.circle(surf, PLUM_HI,
                           (int(px - r * 0.12), int(py - r * 0.12)), int(r * 0.18))
    pygame.draw.circle(surf, GLOW, (int(cx), int(cy)), max(2, int(r * 0.3)))


# ── the serene bound FACE (where the straw crosses) ───────────────────────────
def bound_face(surf, cx, cy, r, s, lit=True):
    """The serene Toshigami face glowing where the bindings cross. A calm oval
    plane (cream, gold-touched) with closed-arc eyes + a small vermilion mark.
    The pale-gold blessing GLOW is the SOLE radial accent, behind the face —
    held distinct from the kintsugi gold LINE-WORK at the nodes above."""
    if lit:
        g = radial_glow(int(r * 1.9), GLOW, alpha_center=150, falloff=2.4)
        surf.blit(g, (cx - g.get_width() // 2, cy - g.get_height() // 2),
                  special_flags=pygame.BLEND_ADD)
    face = pygame.Rect(cx - r, cy - int(r * 1.12), r * 2, int(r * 2.24))
    pygame.draw.ellipse(surf, INK, face.inflate(int(2 * s), int(2 * s)))
    pygame.draw.ellipse(surf, FACE, face)
    # hard shade band on the lower-right (stepped, not blurred)
    sh = pygame.Rect(cx - int(r * 0.2), cy - int(r * 0.2), int(r * 1.2), int(r * 1.3))
    pygame.draw.ellipse(surf, FACE_D, sh)
    pygame.draw.ellipse(surf, FACE, face.inflate(-int(r * 0.7), -int(r * 0.7)))
    # calm closed-arc eyes
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.42)
        pygame.draw.arc(surf, INK,
                        (ex - int(r * 0.3), cy - int(r * 0.2),
                         int(r * 0.6), int(r * 0.5)),
                        math.radians(200), math.radians(340), max(1, int(1.8 * s)))
    # serene vermilion mark on the brow
    pygame.draw.circle(surf, PLUM, (cx, cy - int(r * 0.62)), max(1, int(r * 0.16)))
    pygame.draw.ellipse(surf, INK, face, max(1, int(1.4 * s)))


# ── THE HERO: the single fat monolithic culm ──────────────────────────────────
def draw_moso(surf, cx, cy, s):
    """The great single-culm MONOLITH: ONE titanic fresh-green shaft, WIDER than
    any single element in the brood, carrying 5-6 BIG node collars and capped by
    a single COLOSSAL diagonal-cut cream mouth (~the top quarter of the column,
    brightest value). A kintsugi gold-vein hairline traces every node-collar
    (the held-apart accent, line-work not fill). The foot carries just enough
    auspicious kit — straw cinch + plum + ONE pine sprig + the sole blessing
    glow — so the megalith isn't inert, but never top-heavy. `s` = unit scale
    around a ~150-unit figure.

    Built foot-to-crown so the cut mouth lands on top: a low pine sprig + plum
    foot -> the fat shaft (with fat collars + gold veins) -> the colossal cut
    mouth -> straw cinch + blessing-face at the foot waist.

    WHY a FAT half-width + a TALL shaft: the silhouette KIND is a lone
    standing-stone of bamboo — the anti-parent slim trio. The whole read is mass
    and verticality, with the giant cut-disc the one bright incident."""
    base_y = cy + int(64 * s)
    waist_y = base_y - int(26 * s)
    half_w = int(26 * s)           # FAT — wider than any single brood element
    shaft_top = cy - int(108 * s)  # tall titanic shaft
    # WHY a generous node pitch: 5-6 BIG collars across the shaft height — the
    # only direction with room for node geometry to read large, so the collars
    # are widely spaced and fat rather than a fine ladder that blurs to noise.
    node = int(31 * s)

    # === BASE LIFE (bottom-anchored, never top-heavy) ========================
    # ONE pine sprig thrown low to one side + a small back fan; the plum sits at
    # the foot. Deliberately sparse — restraint is the epic register here.
    pine_fan(surf, (cx - int(20 * s), base_y - int(2 * s)), math.radians(206),
             math.radians(58), 6, 36 * s, s, sign=-1)
    pine_fan(surf, (cx + int(16 * s), base_y + int(2 * s)), math.radians(-38),
             math.radians(46), 4, 24 * s, s, sign=1)

    # === THE MONOLITHIC SHAFT — fat collars + kintsugi gold veins ============
    node_ys = []
    culm_shaft(surf, cx, shaft_top, base_y, half_w, s, node,
               kintsugi=True, node_y_out=node_ys)

    # === THE COLOSSAL CUT MOUTH (~top quarter, brightest value) ==============
    # dominance pushed hard so the disc fills the top of the column and collapses
    # to ONE unmissable cream disc at 32px (the must-fix gate).
    diagonal_cut(surf, cx, shaft_top, half_w, s, lean=0.66, dominance=1.35)

    # === STRAW CINCH at the foot waist, binding the monolith =================
    straw_collar(surf, cx, waist_y, int(30 * s), int(20 * s), s)

    # === the serene blessing-FACE + sole pale-gold GLOW where the bind crosses
    bound_face(surf, cx, waist_y - int(1 * s), int(11 * s), s, lit=True)

    # === RED PLUM at the base (auspicious vermilion accent, base-anchored) ====
    plum_blossom(surf, cx - int(28 * s), base_y - int(4 * s), int(7 * s), s)
    plum_blossom(surf, cx + int(26 * s), base_y + int(2 * s), int(6 * s), s)


# ── the fresh diagonal-CUT pillar gap-cap (an explicit slant cut, not a point) ─
def cut_cap(surf, cx, cut_y, half_w, s):
    """The pillar's gap-edge cap: an explicit FRESH diagonal cut across the culm
    top — a fat cream cut-oval on a visible slant (high lip left, low right),
    with a pine tuft thrown to ONE side. Caller has drawn the shaft up to cut_y."""
    ew = int((half_w + int(2 * s)) * 1.5)
    eh = int(half_w * 0.64 + int(3 * s))
    slant = int(half_w * 0.5)
    plane = [(cx - ew, cut_y + slant), (cx + ew, cut_y - slant),
             (cx + ew, cut_y - slant + eh), (cx - ew, cut_y + slant + eh)]
    pygame.draw.polygon(surf, INK, [(x, y + 2) for (x, y) in plane])
    outer = pygame.Rect(cx - ew, cut_y - eh + slant, ew * 2, eh * 2)
    pygame.draw.ellipse(surf, INK, outer.inflate(int(2 * s), int(2 * s)))
    pygame.draw.ellipse(surf, CUT_CREAM, outer)
    sheen = pygame.Rect(cx - ew, cut_y - eh + slant, int(ew * 1.4), int(eh * 1.4))
    pygame.draw.ellipse(surf, CUT_HI, sheen)
    pygame.draw.ellipse(surf, CUT_CREAM, sheen.inflate(-int(ew * 0.5), -int(eh * 0.5)))
    iw, ih = int(ew * 0.40), int(eh * 0.42)
    cav = pygame.Rect(cx - iw + int(ew * 0.18), cut_y - ih + slant + int(eh * 0.18),
                      iw * 2, ih * 2)
    pygame.draw.ellipse(surf, CAVITY, cav)
    pygame.draw.ellipse(surf, CAVITY_DD,
                        cav.inflate(-int(iw * 0.7), -int(ih * 0.7)))
    pygame.draw.ellipse(surf, INK, outer, max(1, int(1.4 * s)))
    # a pine sprig thrown to ONE side off the high lip
    pine_fan(surf, (cx - half_w, cut_y + slant - int(4 * s)), math.radians(202),
             math.radians(44), 5, 24 * s, s, sign=-1)


# ── the monolith → PILLAR mirror (it already IS the hero pillar) ──────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The monolith IS the pillar verbatim — its fat node-segments are the
    tileable shaft, the colossal diagonal CUT is the gap-edge cap, and the
    straw-cinched plum-cream foot is the lower mirror. The cleanest mirror in
    the brood (the brief's claim). `cap` names the END that faces the GAP."""
    half_w = int(15 * s)
    node = int(30 * s)
    cap_room = int(46 * s)
    base_room = int(40 * s)

    if cap == "bottom":
        shaft_top = top + base_room
        shaft_bot = bot - cap_room
        culm_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, node, kintsugi=True)
        cut_y = bot - int(22 * s)
        culm_shaft(surf, cx, shaft_bot, cut_y + int(2 * s), half_w, s, node, kintsugi=True)
        cut_cap(surf, cx, cut_y, half_w, s)
        straw_collar(surf, cx, top + int(20 * s), int(20 * s), int(15 * s), s)
        _plum_cap(surf, cx, top + int(13 * s), half_w, s)
    else:
        shaft_top = top + cap_room
        shaft_bot = bot - base_room
        culm_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, node, kintsugi=True)
        cut_y = top + int(22 * s)
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        H = surf.get_height()
        culm_shaft(tmp, cx, H - (cut_y + int(2 * s)), H - shaft_top, half_w, s, node, kintsugi=True)
        cut_cap(tmp, cx, H - cut_y, half_w, s)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, 0))
        straw_collar(surf, cx, bot - int(20 * s), int(20 * s), int(15 * s), s)
        _plum_cap(surf, cx, bot - int(13 * s), half_w, s)


def _plum_cap(surf, cx, cy, half_w, s):
    """The lower-mirror plum cap, value-ANCHORED: a fat cream cut-ring disc
    behind a vermilion plum so the lower mirror reads as a distinct cap at the
    pillar chip on day AND night."""
    disc = pygame.Rect(cx - int(half_w * 1.3), cy - int(half_w * 0.9),
                       int(half_w * 2.6), int(half_w * 1.8))
    pygame.draw.ellipse(surf, INK, disc.inflate(int(2 * s), int(2 * s)))
    pygame.draw.ellipse(surf, CUT_CREAM, disc)
    pygame.draw.ellipse(surf, CUT_HI, disc.inflate(-int(half_w * 0.9), -int(half_w * 0.6)))
    plum_blossom(surf, cx - int(half_w * 0.45), cy, int(half_w * 0.62), s)
    plum_blossom(surf, cx + int(half_w * 0.55), cy + int(2 * s), int(half_w * 0.52), s)


# ── compose the review sheet ─────────────────────────────────────────────────
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
    sheet.blit(font_big.render("MOSO-NO-TAISHO", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "The great single-culm bamboo MONOLITH  ·  LONE FAT COLUMN (anti-parent trio) · colossal top "
        "CUT-DISC (top quarter, brightest) · 5-6 BIG node collars · kintsugi gold-vein · round 1",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_moso(big, 178 * SS, 224 * SS, 1.55 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Body-is-bamboo — hero monolith", True, LABEL), (60, 566))
    sheet.blit(font_sm.render("ONE titanic fat shaft (wider than any brood element); the COLOSSAL cut-disc fills", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("~the top quarter and is the BRIGHTEST value. 5-6 BIG node collars carry the bamboo", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("read; <=2px KINTSUGI gold-vein hairlines trace the collars (line-work, not glow).", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, the cleanest mirror in the set ======
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (40, 50, 40), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — IS the monolith", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("fat node-segments = repeat shaft; the", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("colossal slant-CUT = gap cap; straw-", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("cinched plum-on-cream foot = lower mirror", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_moso(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
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
    sheet.blit(font_sm.render("32px on night sky — ONE cream cut-disc", True, LABEL_DIM), (panel_x + 20, night_y + 156))
    sheet.blit(font_sm.render("crowning a fat column must hold", True, LABEL_DIM), (panel_x + 20, night_y + 170))

    # blacked-out 32px silhouette — the KIND test: it must read as ONE LONE FAT
    # COLUMN (distinct from the parent slim trio + the 4 siblings), never a blob.
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_moso(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
        return sil

    sil_y = night_y + 198
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 214, 200), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 26))
    sheet.blit(font_sm.render("ONE LONE FAT COLUMN (not the", True, LABEL_DIM), (sx + 104, sil_y + 44))
    sheet.blit(font_sm.render("parent slim trio, not the 4", True, LABEL_DIM), (sx + 104, sil_y + 60))
    sheet.blit(font_sm.render("siblings) — a standing-stone", True, LABEL_DIM), (sx + 104, sil_y + 76))

    def pillar_chip32():
        big = pygame.Surface((52 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 26 * SS, 2 * SS, 128 * SS, 0.36 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (52, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 192
    vgrad(sheet, (px2, day_y, 64, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 64, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 10))
    vgrad(sheet, (px2, night_y, 64, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 64, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 646))
    swatches = [
        (CULM, "fresh-culm green"), (CULM_DD, "node-collar shadow"),
        (CUT_CREAM, "cut-ring cream"), (CUT_HI, "cut sheen (brightest)"),
        (STRAW, "straw-rope"), (PLUM, "vermilion plum"),
        (KINTSUGI, "kintsugi gold-vein"), (GLOW, "pale-gold glow (foot)"),
    ]
    sxp, syp = panel_x + 16, 672
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 850, W - 28, 40))
    sheet.blit(font_sm.render(
        "REALISM pipeline (NOT chibi): SS=6 supersample -> smoothscale.  4-6 HARD STEPPED value bands · NO gradients · ink keyline (28,22,30) · "
        "1px grown outline · radial glow ACCENT only (foot).  R1: lone fat monolith · colossal cut-disc (top quarter, brightest) · fat node collars · kintsugi <=2px gold veins.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
