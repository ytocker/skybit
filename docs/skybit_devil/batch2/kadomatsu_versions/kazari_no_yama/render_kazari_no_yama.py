"""
ROUND-1 concept renderer for KAZARI-NO-YAMA — the offering-mound pyre of
bundled cut culms (Kadomatsu brood, direction #4, rank 4). Headless Pygame;
ELEVATED-REALISM pipeline cloned verbatim from the parent kadomatsu_shin
harness (SS=6 supersample -> smoothscale; ZERO gradients, hard stepped value
bands only; ink keyline (28,22,30) + 1px alpha-grown outline; radial glow for
ACCENTS only). All palette constants + helpers (diagonal_cut, culm_shaft,
straw_collar, pine_fan, plum_blossom, bound_face, cut_cap, grow_outline,
radial_glow) are cloned from kadomatsu_shin/render_round_2.py.

WHY this is the "sheer mass / abundance" register of the brood: where the
parent is a slim stepped TRIO, Kazari is a FAT TRIANGULAR MOUND-PYRE — a
broad-based peaked PILE of DOZENS of DISCRETE bound culms, hard culm-tips
bristling the upper slopes, TRIPLE straw bands cinching the tiers. The epic
hook is the most culms of any direction — a mountain of offerings.

WHY the MUST-FIX (the set's one real watch) drives every choice here: the
Takenoko sibling is ONE smooth tapering husk-SHELL of continuous plates. To
separate Kazari HARD from that cone twin, the mound must read as a PACKED
CLUSTER of MANY discrete culms with:
  - a bristling, BROKEN upper edge (hard culm-tips poking the peak — the
    blackout silhouette must read JAGGED/many-tipped, NEVER a smooth solid
    triangle),
  - a CONSTELLATION of cream cut-discs (one big APEX hero disc + a graded
    scatter of smaller discs down the flanks), and
  - TRIPLE horizontal straw bands cinching the tiers (a cone has none).
The triple bands + the disc constellation are what kill the cone twin.

WHY the held-apart accent is mikan-orange daidai + rice-ear gold tucked in the
lashings: it is the ONLY warm-orange in the brood — a single tonal lane no
sibling owns, kept small (base/band-anchored) so it accents, never fills.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the cloned
helpers.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (cloned from kadomatsu_shin/render_round_2.py) ─────────────
CULM      = (124, 188, 104)   # fresh-culm green (lifted warmer/brighter)
CULM_D    = ( 74, 138,  72)   # deep node-green shade
CULM_DD   = ( 50, 102,  56)   # deepest groove / node-collar shadow band
CULM_HI   = (172, 216, 130)   # sun-side fresh-green highlight band
CULM_HOT  = (208, 232, 158)   # hottest green sheen rail (top-left sun)
CULM_RIM  = (158, 206, 116)   # thin WARM rim-keyline on culm edges (night hold)
CULM_BACK = ( 58, 116,  62)   # back-culm body green, darkened a step (depth)
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
PINE      = ( 58, 104,  62)   # pine needle-fan green (cooler/darker than culm)
PINE_D    = ( 38,  74,  46)   # pine shade
PINE_HI   = ( 96, 142,  88)   # pine lit needle
GLOW      = (244, 224, 150)   # soft pale-gold blessing glow (radial, accent only)
FACE      = (240, 230, 188)   # serene bound-face plane (gold-touched cream)
FACE_D    = (196, 178, 132)   # face shade band
INK       = ( 28,  22,  30)   # hard ink keyline

# ── HELD-APART ACCENT (this direction's only new tones) ───────────────────────
# WHY a NEW warm-orange lane: the brood holds every direction's accent apart —
# Kazari owns the ONLY warm-orange. Daidai (bitter-orange) is the New-Year
# fruit tucked in real kadomatsu lashings; rice-ear gold is the harvest-bundle
# tell. Both stepped (no gradient) and kept band/base-anchored so they accent.
DAIDAI     = (230, 142,  58)  # mikan-orange daidai fruit (the held-apart accent)
DAIDAI_D   = (176,  96,  36)  # daidai shade band
DAIDAI_HI  = (248, 188, 110)  # daidai lit pip
RICE_GOLD  = (220, 196, 118)  # rice-ear gold (harvest sheaf tucked in the bands)
RICE_GOLD_D= (168, 144,  76)  # rice-ear shade

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


# ── outline grown from the alpha mask (the house keyline) — cloned ───────────
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
    """Necrarch precedent — accent-only soft bloom. Used ONLY for the auspicious
    pale-gold blessing glow at the lashing crossing, never as a fill."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


# ── a fresh madake CULM segment — HARD STEPPED bands, no gradient — cloned ────
def culm_shaft(surf, cx, top, bot, half_w, s, node_pitch, body_col=CULM,
               shade_col=CULM_D, deep_col=CULM_DD):
    """A vertical living-bamboo shaft built as a stack of node-segments, each
    lit with 4 HARD STEPPED value bands across its width (sheen rail | hi | fill
    | deep) — NO smooth gradient — so it reads as a turned cylinder of fresh
    green at 32px. `body_col` lets back culms render a step darker so they don't
    merge. A thin WARM rim-keyline rides the two long edges for the night-hold.

    WHY this is the same shaft as the parent: in Kazari MANY of these are stacked
    into the mound, but each individual culm is the identical madake segment —
    abundance is many of the SAME unit, not a different material."""
    lw = max(2, int(1.6 * s))
    body = [(cx - half_w, bot), (cx - half_w, top + half_w),
            (cx, top), (cx + half_w, top + half_w), (cx + half_w, bot)]
    pygame.draw.polygon(surf, INK, body)
    pygame.draw.polygon(surf, body_col, body)
    hi_col = CULM_HI if body_col is CULM else lerp(body_col, CULM_HI, 0.45)
    bands = ((-1.00, -0.46, hi_col), (-0.46, -0.16, body_col),
             (-0.16, 0.42, body_col), (0.42, 1.00, shade_col))
    for x0, x1, col in bands:
        bx0 = cx + int(half_w * x0)
        bx1 = cx + int(half_w * x1)
        pygame.draw.polygon(surf, col, [
            (bx0, top + half_w), (bx1, top + half_w), (bx1, bot), (bx0, bot)])
    rail = max(2, int(half_w * 0.16))
    rail_col = CULM_HOT if body_col is CULM else CULM_HI
    pygame.draw.rect(surf, rail_col,
                     (cx - half_w, top + half_w, rail, bot - (top + half_w)))
    # NODE RINGS — two-ring madake collar, repeated at node_pitch
    y = bot - node_pitch
    while y > top + half_w + node_pitch * 0.3:
        pygame.draw.rect(surf, deep_col,
                         (cx - half_w, y, half_w * 2, max(2, int(2.4 * s))))
        ring_col = CULM_HOT if body_col is CULM else CULM_HI
        pygame.draw.rect(surf, ring_col,
                         (cx - half_w, y - max(2, int(2.6 * s)),
                          half_w * 2, max(1, int(1.8 * s))))
        nub = max(2, int(2.2 * s))
        pygame.draw.polygon(surf, shade_col, [
            (cx - half_w, y - int(0.5 * s)),
            (cx - half_w - nub, y - nub),
            (cx - half_w - nub, y + int(1.0 * s))])
        y -= node_pitch
    rim = max(1, int(1.1 * s))
    pygame.draw.line(surf, CULM_RIM, (cx - half_w, top + half_w),
                     (cx - half_w, bot), rim)
    pygame.draw.line(surf, CULM_RIM, (cx + half_w, top + half_w),
                     (cx + half_w, bot), rim)
    pygame.draw.polygon(surf, INK, body, lw)


# ── the DIAGONAL-CUT MOUTH — the signature: bright cream DISC — cloned ────────
def diagonal_cut(surf, cx, top, half_w, s, lean=0.62, dominance=1.0):
    """The steep sogi slant-cut culm-mouth: a bright OVAL of cut-CREAM ring-wall
    around a SMALL inner CAVITY, tilted so the high lip is on the left. The
    cut-oval is enlarged via `dominance`, the cavity shrunk + lightened, the
    upper-left sheen (CUT_HI) the single BRIGHTEST value — so at 32px the read is
    a BRIGHT CREAM DISC, not a hole. `dominance` 1.0 = apex hero, smaller for the
    flank scatter (the constellation)."""
    ew = int((half_w + int(1.4 * s)) * (1.0 + 0.62 * dominance))
    eh = int((half_w * lean + int(2 * s)) * (1.0 + 0.55 * dominance))
    ccx, ccy = cx, top
    outer = pygame.Rect(ccx - ew, ccy - eh, ew * 2, eh * 2)
    pygame.draw.ellipse(surf, INK, outer.inflate(int(2.4 * s), int(2.4 * s)))
    pygame.draw.ellipse(surf, CUT_CREAM, outer)
    sheen = pygame.Rect(ccx - ew, ccy - eh, int(ew * 1.5), int(eh * 1.5))
    pygame.draw.ellipse(surf, CUT_HI, sheen)
    pygame.draw.ellipse(surf, CUT_CREAM,
                        sheen.inflate(-int(ew * 0.42), -int(eh * 0.42)))
    pygame.draw.arc(surf, CUT_D, outer.inflate(-int(1.5 * s), -int(1.5 * s)),
                    math.radians(250), math.radians(20), max(2, int(2.6 * s)))
    iw, ih = int(ew * 0.42), int(eh * 0.42)
    cav = pygame.Rect(ccx - iw, ccy - ih + int(eh * 0.20), iw * 2, ih * 2)
    pygame.draw.ellipse(surf, INK, cav.inflate(int(1.4 * s), int(1.4 * s)))
    pygame.draw.ellipse(surf, CAVITY, cav)
    floor = pygame.Rect(ccx - int(iw * 0.5) + int(iw * 0.3),
                        ccy - int(ih * 0.5) + int(eh * 0.20) + int(ih * 0.5),
                        int(iw * 1.0), int(ih * 0.9))
    pygame.draw.ellipse(surf, CAVITY_DD, floor)
    pygame.draw.ellipse(surf, INK, outer, max(1, int(1.4 * s)))


# ── a woven straw-rope COLLAR band (the waist binding) — cloned ───────────────
def straw_collar(surf, cx, cy, half_w, h, s, knot_tail=True):
    """The woven rice-straw rope band: diagonal STRANDS alternating lit/shade so
    it reads woven (not a smooth ring), HARD STEPPED. A short paired knot-tail
    hangs straight DOWN at the centre (a knot, not protruding arms).

    WHY `knot_tail` is now optional: Kazari cinches THREE tiers; only the lowest
    (waist) band drops a knot-tail. The upper two read as taut binds so the
    stack reads as cinched tiers, not three hanging knots."""
    band = pygame.Rect(cx - half_w - int(3 * s), cy - h // 2,
                       (half_w + int(3 * s)) * 2, h)
    pygame.draw.rect(surf, INK, band.inflate(int(2 * s), int(2 * s)))
    pygame.draw.rect(surf, STRAW_D, band)
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
    pygame.draw.rect(surf, STRAW_D, (band.left, band.top, band.width, max(2, int(2 * s))))
    pygame.draw.rect(surf, INK, (band.left, band.bottom - max(2, int(2 * s)),
                                 band.width, max(2, int(2 * s))))
    pygame.draw.rect(surf, INK, band, max(1, int(1.4 * s)))
    if knot_tail:
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


# ── a pine NEEDLE-FAN — cloned ────────────────────────────────────────────────
def pine_fan(surf, root, base_ang, spread, n, length, s, sign=1):
    """A fan of pine needles: n hard tapered blades radiating from `root` across
    `spread`, graded in length, alternating lit/shade so the fan reads as
    discrete clumps (NOT fuzz). Bottom-anchored base mass."""
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


# ── a vermilion PLUM blossom — cloned ─────────────────────────────────────────
def plum_blossom(surf, cx, cy, r, s):
    """A five-petal red-plum blossom: HARD STEPPED petals (shade ring -> petal ->
    highlight pip) with a pale-gold pip centre. Base-anchored vermilion accent."""
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


# ── the serene bound FACE (where the lashing crosses) — cloned ────────────────
def bound_face(surf, cx, cy, r, s, lit=True):
    """The serene Toshigami face glowing where the bindings cross. A calm oval
    plane (cream, gold-touched) with closed-arc eyes + a small vermilion mark.
    The pale-gold blessing glow is the SOLE radial accent, behind the face."""
    if lit:
        g = radial_glow(int(r * 1.9), GLOW, alpha_center=150, falloff=2.4)
        surf.blit(g, (cx - g.get_width() // 2, cy - g.get_height() // 2),
                  special_flags=pygame.BLEND_ADD)
    face = pygame.Rect(cx - r, cy - int(r * 1.12), r * 2, int(r * 2.24))
    pygame.draw.ellipse(surf, INK, face.inflate(int(2 * s), int(2 * s)))
    pygame.draw.ellipse(surf, FACE, face)
    sh = pygame.Rect(cx - int(r * 0.2), cy - int(r * 0.2), int(r * 1.2), int(r * 1.3))
    pygame.draw.ellipse(surf, FACE_D, sh)
    pygame.draw.ellipse(surf, FACE, face.inflate(-int(r * 0.7), -int(r * 0.7)))
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.42)
        pygame.draw.arc(surf, INK,
                        (ex - int(r * 0.3), cy - int(r * 0.2),
                         int(r * 0.6), int(r * 0.5)),
                        math.radians(200), math.radians(340), max(1, int(1.8 * s)))
    pygame.draw.circle(surf, PLUM, (cx, cy - int(r * 0.62)), max(1, int(r * 0.16)))
    pygame.draw.ellipse(surf, INK, face, max(1, int(1.4 * s)))


# ── the fresh diagonal-CUT pillar gap-cap — cloned ────────────────────────────
def cut_cap(surf, cx, cut_y, half_w, s):
    """The pillar's gap-edge cap: an explicit FRESH diagonal cut across the culm
    top — a fat cream cut-oval on a visible diagonal plane (high lip left, low
    right), a pine tuft thrown to ONE side. Caller has drawn the shaft to cut_y."""
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
    pine_fan(surf, (cx - half_w, cut_y + slant - int(4 * s)), math.radians(202),
             math.radians(44), 5, 24 * s, s, sign=-1)


# ── NEW: a daidai (mikan-orange) fruit — the held-apart accent ────────────────
def daidai_fruit(surf, cx, cy, r, s):
    """A single mikan-orange daidai bitter-orange tucked into a lashing. HARD
    STEPPED (shade ring -> body -> lit pip) so it matches the no-gradient house
    pipeline. The ONLY warm-orange in the brood — kept band-anchored + small so
    it accents the cool greens, never competes with the cream cut-discs.

    A tiny leaf-nub of PINE rides the top so it reads as fruit-on-a-twig, the
    real kadomatsu daidai tell."""
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), int(r) + max(1, int(1.4 * s)))
    pygame.draw.circle(surf, DAIDAI_D, (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, DAIDAI, (int(cx - r * 0.18), int(cy - r * 0.10)),
                       int(r * 0.78))
    pygame.draw.circle(surf, DAIDAI_HI,
                       (int(cx - r * 0.34), int(cy - r * 0.30)), int(r * 0.30))
    # a small navel pip on the lower-right (the citrus tell), stepped dark
    pygame.draw.circle(surf, DAIDAI_D,
                       (int(cx + r * 0.40), int(cy + r * 0.40)), max(1, int(r * 0.16)))
    # tiny pine leaf-nub on the crown
    pygame.draw.polygon(surf, PINE, [
        (cx, cy - r), (cx - r * 0.4, cy - r * 1.5), (cx + r * 0.2, cy - r * 1.2)])
    pygame.draw.polygon(surf, PINE_HI, [
        (cx, cy - r), (cx - r * 0.2, cy - r * 1.3), (cx + r * 0.1, cy - r * 1.1)])


# ── NEW: a rice-ear gold sheaf — the harvest tell tucked in a band ────────────
def rice_ear(surf, root, ang, length, s, sign=1):
    """A drooping rice-ear sheaf: a slim arched stalk hung with paired grain
    pips, HARD STEPPED gold (rice-ear is the harvest-bundle tell of an offering
    mound). Tucked in the lashings beside the daidai — the warm-gold half of the
    held-apart accent. Kept thin + short so it never reads as a pine fan."""
    ca, sa = math.cos(ang), math.sin(ang)
    # the arched stalk
    tip = (root[0] + ca * length, root[1] + sa * length)
    pygame.draw.line(surf, RICE_GOLD_D, root, tip, max(2, int(1.6 * s)))
    pygame.draw.line(surf, RICE_GOLD, root, tip, max(1, int(1.0 * s)))
    # paired grain pips down the upper half of the stalk (the laden ear)
    n = 5
    for k in range(1, n + 1):
        t = 0.45 + 0.55 * (k / n)
        gx = root[0] + ca * length * t
        gy = root[1] + sa * length * t
        for psgn in (-1, 1):
            ox = -sa * psgn * (2.2 * s)
            oy = ca * psgn * (2.2 * s)
            pygame.draw.circle(surf, RICE_GOLD_D,
                               (int(gx + ox), int(gy + oy)), max(2, int(1.8 * s)))
            pygame.draw.circle(surf, RICE_GOLD,
                               (int(gx + ox - s * 0.4), int(gy + oy - s * 0.4)),
                               max(1, int(1.1 * s)))


# ── THE HERO: the offering-mound pyre of dozens of discrete bound culms ───────
def draw_kazari(surf, cx, cy, s):
    """The living offering-mound: a FAT TRIANGULAR PEAKED PILE of DOZENS of
    DISCRETE bound culms, hard culm-tips BRISTLING the upper slopes, TRIPLE
    straw bands cinching three tiers, an APEX hero cut-disc crowning the peak
    with a graded scatter of smaller cut-discs down the flanks (the
    constellation), daidai-orange + rice-gold tucked in the lashings, and a
    pine + plum foot. `s` = unit scale around a ~150-unit figure.

    WHY the mound is built as explicit per-culm strokes (not one filled
    triangle): the set's one real watch is separating Kazari HARD from the
    Takenoko cone (one smooth husk-SHELL). So each culm is its OWN narrow shaft
    drawn back-to-front in tiers, packed shoulder-to-shoulder with a slight tilt
    so the heads splay — the upper edge is therefore BROKEN by individual
    culm-tips, never a smooth slope. The triple bands + the disc constellation
    finish the separation.

    Built back-to-front: foot pine -> three packed culm TIERS (widest/lowest
    first) -> the triple cinch bands over the tier seams -> apex hero culm +
    cut-disc -> the flank cut-disc constellation -> face + daidai/rice + plum."""
    base_y = cy + int(74 * s)
    apex_y = cy - int(94 * s)

    # === FOOT PINE MASS (bottom-anchored, broad — the mound is planted) =======
    for sgn, ang in ((-1, math.radians(206)), (1, math.radians(-26)),
                     (-1, math.radians(230)), (1, math.radians(-50)),
                     (-1, math.radians(250)), (1, math.radians(-70))):
        pine_fan(surf, (cx + sgn * int(16 * s), base_y - int(2 * s)),
                 ang, math.radians(58), 6, 40 * s, s, sign=sgn)
    pine_fan(surf, (cx, base_y + int(3 * s)), math.radians(90),
             math.radians(72), 6, 26 * s, s)

    # === THE PACKED CULM TIERS — dozens of DISCRETE shafts ====================
    # WHY a triangular layout of decreasing rows: a mound-pyre is a stacked
    # pile that narrows to a peak. Each TIER is a horizontal row of many narrow
    # culms; higher tiers hold fewer + shorter culms (the triangle). Culms tilt
    # outward toward the edges (a leaned-against-each-other lashed bundle) so the
    # heads SPLAY and the upper edge bristles — the cone-killer.
    #
    # tier = (row_center_y, top_y, half_span, n_culms, hw, body_col)
    tiers = [
        # back/lowest WIDE tier — darkest body so it recedes (depth + mass)
        (base_y - int(4 * s),  cy + int(18 * s), int(58 * s), 11,
         int(5.2 * s), CULM_BACK),
        # middle tier — mid green, stepped narrower
        (base_y - int(4 * s),  cy - int(26 * s), int(42 * s),  9,
         int(5.4 * s), CULM_D),
        # upper-front tier — brightest fresh green, narrowest, tallest splay
        (base_y - int(4 * s),  cy - int(70 * s), int(26 * s),  7,
         int(5.6 * s), CULM),
    ]
    # remember each culm head (x, top_y, hw) so the disc constellation can sit
    # on REAL culm-tips, not arbitrary points
    heads = []
    for row_bot, row_top, span, n, hw, body in tiers:
        node = int(15 * s)
        for k in range(n):
            t = (k / max(1, n - 1)) * 2 - 1   # -1 .. +1 across the row
            culm_x = int(cx + t * span)
            # outward tilt: edge culms lean away from centre -> splayed heads
            tilt = int(t * 14 * s)
            top_x = culm_x + tilt
            # graded height: centre culms tallest, edges shorter (the peak rise)
            rise = int((1.0 - abs(t)) * 18 * s)
            top_y = row_top - rise
            shade = CULM_DD if body is CULM_BACK else (CULM_DD if body is CULM_D else CULM_D)
            culm_shaft(surf, top_x, top_y, row_bot, hw, s, node,
                       body_col=body, shade_col=shade)
            heads.append((top_x, top_y, hw, body))

    # === TRIPLE STRAW BANDS cinching the three tier seams =====================
    # WHY THREE bands (the cone-killer half #1): a smooth husk-cone has NO
    # horizontal binding. Three taut straw bands across the mound declare it a
    # BOUND PILE of tiers. Only the lowest (waist) band drops a knot-tail; the
    # upper two read as taut cinches so the stack reads as cinched tiers.
    band_lo_y = cy + int(28 * s)
    band_mid_y = cy - int(16 * s)
    band_hi_y = cy - int(56 * s)
    straw_collar(surf, cx, band_lo_y, int(58 * s), int(17 * s), s, knot_tail=True)
    straw_collar(surf, cx, band_mid_y, int(40 * s), int(14 * s), s, knot_tail=False)
    straw_collar(surf, cx, band_hi_y, int(23 * s), int(12 * s), s, knot_tail=False)

    # === APEX HERO CULM + its dominant cut-disc (crown of the constellation) ==
    apex_x = cx + int(2 * s)
    culm_shaft(surf, apex_x, apex_y, band_hi_y + int(4 * s), int(7 * s), s,
               int(16 * s))
    heads.append((apex_x, apex_y, int(7 * s), CULM))
    # the big apex disc — dominance 1.0, the brightest+largest cream on the form
    diagonal_cut(surf, apex_x, apex_y, int(7 * s), s, lean=0.64, dominance=1.0)

    # === THE CUT-DISC CONSTELLATION — graded scatter down the flanks ==========
    # WHY a graded constellation (the cone-killer half #2 + the signature): the
    # mouths are the brood's focal signature. A cone offers one smooth tip;
    # Kazari offers MANY cut-tips. Each tier's splayed culm-heads get a cut-disc,
    # graded smaller + dimmer toward the base so the eye climbs to the apex hero.
    # Discs sit on REAL heads (collected above), so the cream rides actual
    # culm-tips and the upper edge reads as a field of cut-mouths.
    # pick a subset of heads (skip some so it's a scatter, not a solid cream rim)
    for i, (hx, hy, hw, body) in enumerate(heads[:-1]):
        if i % 2 == 1:            # every other head -> a scatter, not a wall
            continue
        # higher (smaller y) heads get bigger/brighter discs
        height_t = max(0.0, min(1.0, (base_y - hy) / float(base_y - apex_y)))
        dom = 0.34 + 0.42 * height_t
        diagonal_cut(surf, hx, hy, hw, s, lean=0.60, dominance=dom)

    # === the serene blessing-FACE where the lower lashing crosses =============
    bound_face(surf, cx, band_lo_y - int(1 * s), int(12 * s), s, lit=True)

    # === HELD-APART ACCENT: daidai-orange + rice-gold tucked in the lashings ==
    # WHY tucked at the band crossings (not scattered): the daidai is the real
    # kadomatsu fruit lashed into the binding; rice-ears are the harvest sheaf.
    # Keeping both AT the straw bands anchors the only warm-orange so it reads
    # as part of the offering kit, never a competing focal vs the cream discs.
    daidai_fruit(surf, cx - int(40 * s), band_lo_y + int(3 * s), int(7 * s), s)
    daidai_fruit(surf, cx + int(30 * s), band_mid_y + int(2 * s), int(5.5 * s), s)
    rice_ear(surf, (cx + int(44 * s), band_lo_y - int(2 * s)),
             math.radians(58), 30 * s, s, sign=1)
    rice_ear(surf, (cx - int(26 * s), band_mid_y - int(1 * s)),
             math.radians(118), 24 * s, s, sign=-1)

    # === RED PLUM at the foot (auspicious vermilion accent, base-anchored) ====
    plum_blossom(surf, cx - int(30 * s), base_y - int(4 * s), int(7 * s), s)
    plum_blossom(surf, cx + int(34 * s), base_y - int(1 * s), int(6 * s), s)
    plum_blossom(surf, cx + int(6 * s), base_y + int(9 * s), int(5 * s), s)


# ── one tier-culm → PILLAR mirror ─────────────────────────────────────────────
def _band_cap(surf, cx, cy, half_w, s):
    """The lower-mirror foot of the pillar: a broad LASHED foot — a fat straw
    band with a value-anchored daidai-on-gold tuck + a plum, so the pillar's
    lower mirror reads as the mound's broad lashed base, distinct on day AND
    night."""
    straw_collar(surf, cx, cy, int(half_w * 1.5), int(15 * s), s, knot_tail=True)
    daidai_fruit(surf, cx - int(half_w * 0.7), cy - int(2 * s), int(half_w * 0.5), s)
    plum_blossom(surf, cx + int(half_w * 0.8), cy + int(2 * s), int(half_w * 0.5), s)
    rice_ear(surf, (cx + int(half_w * 1.1), cy - int(3 * s)),
             math.radians(56), 16 * s, s, sign=1)


def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """One tier-culm IS the pillar: fresh node-segments = the tileable shaft;
    the apex diagonal-CUT mouth = the detachable gap-edge cap; the broad lashed
    straw foot (daidai + plum) = the lower mirror. The TIERED straw bands of the
    mound become repeat collars riding the shaft so the pillar still reads as a
    cinched offering-culm, not a bare stalk.

    `cap` names the END that faces the GAP."""
    half_w = int(13 * s)
    node = int(26 * s)
    cap_room = int(46 * s)
    base_room = int(42 * s)

    if cap == "bottom":
        shaft_top = top + base_room
        shaft_bot = bot - cap_room
        culm_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, node)
        # repeat-collar straw bands ride the shaft (the mound's tier cinches)
        straw_collar(surf, cx, top + int(86 * s), int(half_w * 1.2),
                     int(12 * s), s, knot_tail=False)
        straw_collar(surf, cx, top + int(150 * s), int(half_w * 1.2),
                     int(12 * s), s, knot_tail=False)
        # gap-edge cap: explicit fresh diagonal-CUT mouth + a side pine sprig
        cut_y = bot - int(22 * s)
        culm_shaft(surf, cx, shaft_bot, cut_y + int(2 * s), half_w, s, node)
        cut_cap(surf, cx, cut_y, half_w, s)
        # lower mirror at TOP: the broad lashed foot
        _band_cap(surf, cx, top + int(20 * s), half_w, s)
    else:
        shaft_top = top + cap_room
        shaft_bot = bot - base_room
        culm_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, node)
        straw_collar(surf, cx, bot - int(86 * s), int(half_w * 1.2),
                     int(12 * s), s, knot_tail=False)
        straw_collar(surf, cx, bot - int(150 * s), int(half_w * 1.2),
                     int(12 * s), s, knot_tail=False)
        cut_y = top + int(22 * s)
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        H = surf.get_height()
        culm_shaft(tmp, cx, H - (cut_y + int(2 * s)), H - shaft_top, half_w, s, node)
        cut_cap(tmp, cx, H - cut_y, half_w, s)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, 0))
        _band_cap(surf, cx, bot - int(20 * s), half_w, s)


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
    sheet.blit(font_big.render("KAZARI-NO-YAMA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "Offering-mound pyre of bundled cut culms  ·  FAT TRIANGULAR MANY-CULM PYRE · triple straw bands · "
        "cream cut-disc CONSTELLATION · daidai-orange accent · round 1",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_kazari(big, 178 * SS, 232 * SS, 1.42 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Body-is-bamboo — hero", True, LABEL), (96, 566))
    sheet.blit(font_sm.render("DOZENS of DISCRETE bound culms in 3 packed tiers — splayed heads BRISTLE the", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("upper slopes (BROKEN edge, never a smooth cone). APEX hero cut-disc + a graded", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("scatter of smaller discs = the constellation. TRIPLE straw bands cinch the tiers.", True, LABEL_DIM), (14, 622))

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
    pygame.draw.rect(sheet, (40, 50, 40), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — one tier-culm", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("node-segments = repeat shaft; tier straw", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("bands = repeat collars; apex CUT = gap cap;", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("broad lashed foot (daidai+plum) = mirror", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_kazari(big, 48 * SS, 50 * SS, (32 / 178.0) * SS)
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
    sheet.blit(font_sm.render("32px night — bristle + disc", True, LABEL_DIM), (panel_x + 20, night_y + 156))
    sheet.blit(font_sm.render("constellation must hold", True, LABEL_DIM), (panel_x + 20, night_y + 170))

    # blacked-out 32px silhouette — the cone-killer TEST: must read JAGGED /
    # MANY-TIPPED peaked mass with a bristling broken upper edge, NEVER a smooth
    # solid triangle (the Takenoko husk-cone)
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_kazari(big, 48 * SS, 50 * SS, (32 / 178.0) * SS)
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
    sheet.blit(font_sm.render("BLACKOUT silhouette — JAGGED,", True, LABEL), (sx + 104, sil_y + 24))
    sheet.blit(font_sm.render("MANY-TIPPED peaked mass (the", True, LABEL_DIM), (sx + 104, sil_y + 42))
    sheet.blit(font_sm.render("cone-killer: a bristling broken", True, LABEL_DIM), (sx + 104, sil_y + 58))
    sheet.blit(font_sm.render("edge, never a smooth triangle)", True, LABEL_DIM), (sx + 104, sil_y + 74))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
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

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 646))
    swatches = [
        (CULM, "fresh-culm green"), (CULM_BACK, "back-culm green"),
        (CUT_CREAM, "cut-ring cream"), (CUT_HI, "cut sheen (brightest)"),
        (STRAW, "straw-rope"), (DAIDAI, "daidai-orange (accent)"),
        (RICE_GOLD, "rice-ear gold (accent)"), (PLUM, "vermilion plum"),
        (GLOW, "pale-gold glow"), (INK, "ink keyline"),
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
        "REALISM pipeline (cloned from kadomatsu_shin): SS=6 supersample -> smoothscale.  4-6 HARD STEPPED value bands · NO gradients · "
        "ink keyline (28,22,30) · 1px grown outline · radial glow ACCENT only.  R1: many DISCRETE culms · bristling broken peak · triple bands · disc constellation · daidai.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
