"""
Round-1 concept renderer for KADOMATSU-SHIN — the New-Year gate-god of three
diagonal-cut culms (bamboo-v2 REALISTIC set, concept #6). Headless Pygame;
ELEVATED-REALISM pipeline (supersample SS=6 -> smoothscale) so the slant-cut
hollow-ring mouths and node geometry stay crisp at downscale.

WHY this set is a DELIBERATE DEPARTURE from chibi: bamboo-v2 must read REALISTIC
and botanically accurate. So instead of the lineage's smooth dark-core->fill->
sheen triad we push the house triad to 4-6 HARD STEPPED value bands per form
(NO smooth gradients) for a sculpted near-volumetric read that survives true
32px. Hard ink keyline (28,22,30) + 1px alpha-grown outline for silhouette POP.
Radial glow for ACCENTS only (the auspicious face-glow where bindings cross).

WHY this is the TRI-CULM DIAGONAL-CUT CLUSTER of the set: it is the ONLY
three-separate-slant-cut-culms bundle. The top read is THREE fresh-green culms
of clearly STEPPED heights (never one fat stalk), each ending in a bright OVAL
diagonal-cut mouth rendered in cut-CREAM so it POPS against the green at 32px —
the signature shows the hollow ring-wall + inner cavity (real kadomatsu sogi
cuts reveal the hollow). A woven straw collar binds the waist; pine fans + red
plum sit at the base as bottom-anchored mass, NEVER top-heavy.

WHY the centre culm IS the pillar: fresh node-segments tile as the repeatable
shaft; the bright diagonal-CUT mouth + a pine sprig is the detachable gap-edge
cap; the straw-bound base with plum is the lower mirror. AD PIN: this is the
CLEANEST pillar mirror in the set — protect it.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the helpers
cloned from the asthi_garuda harness + the necrarch radial_glow.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief #6) ──────────────────────────────────────────
# Fresh-cut festive green held WARMER/yellower than the old Take-Ryu cool jade.
# 4-6 HARD STEPPED bands per form (no smooth gradients). The cut-CREAM mouth is
# the focal POP; vermilion plum/face + soft pale-gold blessing glow the accents.
CULM      = (110, 176,  96)   # fresh-culm green (the dominant living-green fill)
CULM_D    = ( 64, 124,  66)   # deep node-green shade
CULM_DD   = ( 44,  92,  52)   # deepest groove / node-collar shadow band
CULM_HI   = (158, 206, 120)   # sun-side fresh-green highlight band (warm/yellow)
CULM_HOT  = (196, 224, 150)   # hottest green sheen rail (top-left sun)
CUT_CREAM = (222, 212, 168)   # pale diagonal-cut ring-wall (the signature POP)
CUT_HI    = (240, 234, 200)   # lit cut-rim sheen
CUT_D     = (176, 162, 116)   # cut-ring shade (cavity-side lip)
CAVITY    = ( 78,  92,  62)   # the hollow inner cavity (a green-shadowed hole)
CAVITY_DD = ( 40,  54,  38)   # deepest cavity floor
STRAW     = (206, 176, 104)   # woven straw-rope collar
STRAW_D   = (150, 120,  62)   # straw shade between strands
STRAW_HI  = (234, 210, 144)   # straw highlight strand
PLUM      = (212,  76,  58)   # auspicious vermilion plum + face-mark (accent)
PLUM_D    = (158,  48,  40)   # plum shade
PLUM_HI   = (244, 132, 110)   # plum petal highlight
PINE      = ( 58, 104,  62)   # pine needle-fan green (cooler/darker than culm)
PINE_D    = ( 38,  74,  46)   # pine shade
PINE_HI   = ( 96, 142,  88)   # pine lit needle
GLOW      = (244, 224, 150)   # soft pale-gold blessing glow (radial, accent only)
FACE      = (240, 230, 188)   # serene bound-face plane (gold-touched cream)
FACE_D    = (196, 178, 132)   # face shade band
INK       = ( 28,  22,  30)   # hard ink keyline

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
    """Necrarch precedent — accent-only soft bloom. Used ONLY for the auspicious
    pale-gold blessing glow where the straw bindings cross, never as a fill."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


# ── a fresh madake CULM segment — HARD STEPPED bands, no gradient ─────────────
def culm_shaft(surf, cx, top, bot, half_w, s, node_pitch):
    """A vertical living-bamboo shaft built as a stack of node-segments, each
    lit with 4 HARD STEPPED value bands across its width (sheen rail | hi | fill
    | deep) — NO smooth gradient — so it reads as a turned cylinder of fresh
    green at 32px. Node rings are the two-ring madake collar: a hard CULM_DD
    groove with a pale swollen ring above it. Returns nothing; caller caps it."""
    lw = max(2, int(1.6 * s))
    # body fill column (rounded top so the cut/cap sits on a real culm end)
    body = [(cx - half_w, bot), (cx - half_w, top + half_w),
            (cx, top), (cx + half_w, top + half_w), (cx + half_w, bot)]
    pygame.draw.polygon(surf, INK, body)
    pygame.draw.polygon(surf, CULM, body)
    # 4 HARD vertical value bands across the cylinder (right = shade, left = sun)
    bands = ((-1.00, -0.46, CULM_HI), (-0.46, -0.16, CULM),
             (-0.16, 0.42, CULM), (0.42, 1.00, CULM_D))
    for x0, x1, col in bands:
        bx0 = cx + int(half_w * x0)
        bx1 = cx + int(half_w * x1)
        pygame.draw.polygon(surf, col, [
            (bx0, top + half_w), (bx1, top + half_w), (bx1, bot), (bx0, bot)])
    # hottest sun rail down the far-left edge (a thin hard band, not a blur)
    rail = max(2, int(half_w * 0.16))
    pygame.draw.rect(surf, CULM_HOT,
                     (cx - half_w, top + half_w, rail, bot - (top + half_w)))
    # NODE RINGS — two-ring madake collar, repeated at node_pitch
    y = bot - node_pitch
    while y > top + half_w + node_pitch * 0.3:
        # hard dark groove
        pygame.draw.rect(surf, CULM_DD,
                         (cx - half_w, y, half_w * 2, max(2, int(2.4 * s))))
        # swollen pale ring just above the groove (the node bulge)
        pygame.draw.rect(surf, CULM_HOT,
                         (cx - half_w, y - max(2, int(2.6 * s)),
                          half_w * 2, max(1, int(1.8 * s))))
        # tiny paired branch-stub nub at the node (Phyllostachys/madake tell)
        nub = max(2, int(2.2 * s))
        pygame.draw.polygon(surf, CULM_D, [
            (cx - half_w, y - int(0.5 * s)),
            (cx - half_w - nub, y - nub),
            (cx - half_w - nub, y + int(1.0 * s))])
        y -= node_pitch
    pygame.draw.polygon(surf, INK, body, lw)


# ── the DIAGONAL-CUT MOUTH — the signature: hollow ring-wall + inner cavity ───
def diagonal_cut(surf, cx, top, half_w, s, lean=0.62):
    """The steep sogi slant-cut culm-mouth: a bright OVAL of cut-CREAM ring-wall
    surrounding a dark inner CAVITY, tilted so the high lip is on the left. WHY
    cut-CREAM bright against the green: it is THE signature and must POP at 32px.
    Built as concentric ellipses on the slant plane with HARD STEPPED bands (lit
    rim -> ring-wall -> shade lip -> cavity -> cavity floor) — no gradient. The
    ellipse height (`lean`) sells the steep diagonal angle; the real cut also
    reads as the auspicious 'smile'."""
    # the cut plane is an ellipse: wide as the culm, tall by `lean`
    ew = half_w + int(1.4 * s)
    eh = int(half_w * lean) + int(2 * s)
    ccx, ccy = cx, top
    # outer ink rim of the cut oval
    outer = pygame.Rect(ccx - ew, ccy - eh, ew * 2, eh * 2)
    pygame.draw.ellipse(surf, INK, outer.inflate(int(2.4 * s), int(2.4 * s)))
    # the pale cut-CREAM ring-WALL (the bright signature band)
    pygame.draw.ellipse(surf, CUT_CREAM, outer)
    # lit upper-left sheen on the ring-wall (a hard crescent band)
    sheen = pygame.Rect(ccx - ew, ccy - eh, int(ew * 1.4), int(eh * 1.4))
    pygame.draw.ellipse(surf, CUT_HI, sheen)
    pygame.draw.ellipse(surf, CUT_CREAM, sheen.inflate(-int(ew * 0.5), -int(eh * 0.5)))
    # shade lip on the lower-right of the ring-wall (cavity-side)
    pygame.draw.arc(surf, CUT_D, outer.inflate(-int(1.5 * s), -int(1.5 * s)),
                    math.radians(250), math.radians(20), max(2, int(2.6 * s)))
    # the INNER CAVITY — a smaller dark oval inset (the hollow read)
    iw, ih = int(ew * 0.56), int(eh * 0.56)
    cav = pygame.Rect(ccx - iw, ccy - ih + int(eh * 0.10), iw * 2, ih * 2)
    pygame.draw.ellipse(surf, INK, cav.inflate(int(1.6 * s), int(1.6 * s)))
    pygame.draw.ellipse(surf, CAVITY, cav)
    # deepest cavity floor offset down-right (the hollow has depth)
    floor = pygame.Rect(ccx - int(iw * 0.6) + int(iw * 0.3),
                        ccy - int(ih * 0.6) + int(eh * 0.25) + int(ih * 0.4),
                        int(iw * 1.2), int(ih * 1.0))
    pygame.draw.ellipse(surf, CAVITY_DD, floor)
    pygame.draw.ellipse(surf, INK, outer, max(1, int(1.4 * s)))


# ── a woven straw-rope COLLAR band (the waist binding) ────────────────────────
def straw_collar(surf, cx, cy, half_w, h, s):
    """The woven rice-straw rope at the waist: a fat band of diagonal STRANDS
    (alternating lit/shade so it reads woven, not a smooth ring) wrapping the
    bundle. HARD STEPPED — each strand its own value, no blur. Slightly belled
    so it reads as a real cinch, with two knot-tails dropping below."""
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
    # two knot-tails dropping below the cinch
    for sgn in (-1, 1):
        tx = cx + sgn * int(half_w * 0.5)
        pygame.draw.polygon(surf, STRAW, [
            (tx - int(3 * s), band.bottom),
            (tx + int(3 * s), band.bottom),
            (tx + sgn * int(5 * s), band.bottom + int(12 * s)),
            (tx + sgn * int(2 * s), band.bottom + int(13 * s))])
        pygame.draw.polygon(surf, STRAW_D, [
            (tx + sgn * int(1 * s), band.bottom),
            (tx + sgn * int(3 * s), band.bottom),
            (tx + sgn * int(5 * s), band.bottom + int(12 * s))])


# ── a pine NEEDLE-FAN (base mass + pillar cap sprig) ──────────────────────────
def pine_fan(surf, root, base_ang, spread, n, length, s, sign=1):
    """A fan of pine needles: n hard tapered needle-blades radiating from `root`
    across `spread`, graded in length, alternating lit/shade so the fan reads as
    discrete clumps (NOT fuzz). Bottom-anchored mass for the base; a small sprig
    for the pillar cap."""
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
    highlight pip) with a pale-gold pip centre. The auspicious vermilion accent,
    base-anchored only."""
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
    plane (cream, gold-touched) with closed-arc eyes + a small vermilion mark —
    minimal so it reads serene, not busy, at 32px. The pale-gold blessing glow
    is the SOLE radial accent, behind the face."""
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


# ── THE HERO: tri-culm diagonal-cut cluster ───────────────────────────────────
def draw_kadomatsu(surf, cx, cy, s):
    """The living kadomatsu: THREE fresh-green culms of clearly STEPPED heights,
    each capped by a bright diagonal-cut hollow-ring mouth; a woven straw collar
    binds the waist with the serene blessing-face where it crosses; pine fans +
    red plum mass at the base. `s` = unit scale around a ~150-unit figure.

    Built back-to-front: base pine mass -> the three culms (tallest centre, then
    flanks at stepped heights) -> straw collar over the waist -> face + plum."""
    base_y = cy + int(58 * s)
    waist_y = cy + int(12 * s)

    # === BASE PINE MASS (bottom-anchored, never top-heavy) ===================
    # broad low pine fans sweeping out to both sides at the foot of the bundle
    for sgn, ang in ((-1, math.radians(208)), (1, math.radians(-28)),
                     (-1, math.radians(232)), (1, math.radians(-52))):
        pine_fan(surf, (cx + sgn * int(10 * s), base_y - int(2 * s)),
                 ang, math.radians(60), 6, 34 * s, s, sign=sgn)
    # a central down-fan so the foot reads as a planted cluster
    pine_fan(surf, (cx, base_y + int(2 * s)), math.radians(90),
             math.radians(70), 6, 24 * s, s)

    # === THE THREE CULMS — clearly STEPPED heights (never one fat stalk) ======
    # WHY a hard height step: the AD pin — the cluster must read as THREE
    # separate slant-cut culms, so the back culm is shortest, the centre tallest
    # (heaven), a flank in between. Each is a distinct thin shaft with its own
    # cut mouth. Drawn back culm first so the front two overlap it.
    hw_c = int(11 * s)   # centre culm half-width
    hw_s = int(9 * s)    # side culm half-width
    node = int(20 * s)

    # back-left short culm (peeks behind, shortest)
    bl_x = cx - int(15 * s)
    bl_top = cy - int(48 * s)
    culm_shaft(surf, bl_x, bl_top, base_y - int(6 * s), hw_s, s, node)
    diagonal_cut(surf, bl_x, bl_top, hw_s, s, lean=0.60)

    # right culm (medium height)
    r_x = cx + int(16 * s)
    r_top = cy - int(78 * s)
    culm_shaft(surf, r_x, r_top, base_y - int(4 * s), hw_s, s, node)
    diagonal_cut(surf, r_x, r_top, hw_s, s, lean=0.62)

    # centre culm — TALLEST (heaven), the pillar source
    c_top = cy - int(110 * s)
    culm_shaft(surf, cx, c_top, base_y - int(2 * s), hw_c, s, node)
    diagonal_cut(surf, cx, c_top, hw_c, s, lean=0.64)

    # === STRAW COLLAR at the waist, binding all three ========================
    straw_collar(surf, cx, waist_y, int(30 * s), int(20 * s), s)

    # === the serene blessing-FACE where the bindings cross ====================
    bound_face(surf, cx, waist_y - int(1 * s), int(11 * s), s, lit=True)

    # === RED PLUM at the base (auspicious vermilion accent, base-anchored) ====
    plum_blossom(surf, cx - int(26 * s), base_y - int(6 * s), int(7 * s), s)
    plum_blossom(surf, cx + int(28 * s), base_y - int(2 * s), int(6 * s), s)
    plum_blossom(surf, cx + int(8 * s), base_y + int(8 * s), int(5 * s), s)


# ── the centre culm → PILLAR mirror (the cleanest mirror in the set) ──────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The centre culm IS the pillar: fresh node-segments = the tileable shaft;
    the bright diagonal-CUT mouth + a pine sprig = the detachable gap-edge cap;
    the straw-bound base with plum = the lower mirror. AD PIN: protect this as
    the CLEANEST mirror in the set — same culm-shaft band logic top and bottom,
    a clean cap that reads at the pillar chip.

    `cap` names the END that faces the GAP."""
    half_w = int(13 * s)
    node = int(26 * s)
    cap_room = int(46 * s)
    base_room = int(40 * s)

    if cap == "bottom":
        # shaft tiles from the top; the CUT mouth caps the bottom (gap) edge;
        # the straw-bound plum base mirrors at the very top.
        shaft_top = top + base_room
        shaft_bot = bot - cap_room
        culm_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, node)
        # gap-edge cap: diagonal-cut mouth + a pine sprig leaning off it
        cut_y = bot - int(20 * s)
        culm_shaft(surf, cx, shaft_bot, cut_y + int(2 * s), half_w, s, node)
        pine_fan(surf, (cx - half_w, cut_y - int(6 * s)), math.radians(196),
                 math.radians(46), 5, 26 * s, s, sign=-1)
        diagonal_cut(surf, cx, cut_y, half_w, s, lean=0.64)
        # lower mirror at TOP: straw collar + plum base
        straw_collar(surf, cx, top + int(20 * s), int(18 * s), int(15 * s), s)
        plum_blossom(surf, cx - int(14 * s), top + int(12 * s), int(6 * s), s)
        plum_blossom(surf, cx + int(13 * s), top + int(16 * s), int(5 * s), s)
    else:
        shaft_top = top + cap_room
        shaft_bot = bot - base_room
        culm_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, node)
        cut_y = top + int(20 * s)
        # build the cut on a temp surface and flip so the mouth faces UP the gap
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        H = surf.get_height()
        culm_shaft(tmp, cx, H - (cut_y + int(2 * s)), H - shaft_top, half_w, s, node)
        pine_fan(tmp, (cx - half_w, H - (cut_y - int(6 * s))), math.radians(196),
                 math.radians(46), 5, 26 * s, s, sign=-1)
        diagonal_cut(tmp, cx, H - cut_y, half_w, s, lean=0.64)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, 0))
        straw_collar(surf, cx, bot - int(20 * s), int(18 * s), int(15 * s), s)
        plum_blossom(surf, cx - int(14 * s), bot - int(12 * s), int(6 * s), s)
        plum_blossom(surf, cx + int(13 * s), bot - int(16 * s), int(5 * s), s)


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
    sheet.blit(font_big.render("KADOMATSU-SHIN", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "New-Year gate-god of three diagonal-cut culms  ·  TRI-CULM CUT CLUSTER · stepped heights · "
        "cut-cream hollow mouths · straw collar · pine+plum base · round 1",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_kadomatsu(big, 178 * SS, 230 * SS, 1.55 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Body-is-bamboo — hero", True, LABEL), (96, 566))
    sheet.blit(font_sm.render("THREE fresh-green culms at clearly STEPPED heights (never one fat stalk), each", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("ending in a bright OVAL diagonal-cut CREAM mouth — hollow ring-wall + inner cavity.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Woven straw collar binds the waist; serene gold-glow face; pine+plum base mass.", True, LABEL_DIM), (14, 622))

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
    sheet.blit(font.render("Pillar — centre culm", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("fresh node-segments = repeat shaft; cut", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("mouth + pine sprig = gap-edge cap; straw", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("base + plum = lower mirror — clean mirror visible", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_kadomatsu(big, 48 * SS, 52 * SS, (32 / 150.0) * SS)
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

    # blacked-out 32px silhouette — the cluster-read TEST: it must read as THREE
    # stepped culms bound at the waist, never one fat stalk / a blob
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_kadomatsu(big, 48 * SS, 52 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
        return sil

    sil_y = night_y + 188
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 214, 200), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 30))
    sheet.blit(font_sm.render("must read THREE STEPPED culms,", True, LABEL_DIM), (sx + 104, sil_y + 48))
    sheet.blit(font_sm.render("bound at the waist (never 1 stalk)", True, LABEL_DIM), (sx + 104, sil_y + 64))

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

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 636))
    swatches = [
        (CULM, "fresh-culm green"), (CULM_D, "deep node-green"),
        (CUT_CREAM, "cut-ring cream"), (STRAW, "straw-rope"),
        (PLUM, "vermilion plum"), (GLOW, "pale-gold glow"),
        (PINE, "pine green"), (INK, "ink keyline"),
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
        "REALISM pipeline (NOT chibi): SS=6 supersample -> smoothscale.  4-6 HARD STEPPED value bands per form · NO smooth gradients · "
        "hard ink keyline (28,22,30) · 1px grown outline · radial glow ACCENTS only · fresh-cut green WARMER than old Take-Ryu jade.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
