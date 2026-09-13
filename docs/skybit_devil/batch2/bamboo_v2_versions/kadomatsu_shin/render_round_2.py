"""
Round-2 concept renderer for KADOMATSU-SHIN — the New-Year gate-god of three
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
diagonal-cut mouth rendered in cut-CREAM so it POPS against the green at 32px.

ROUND-2 CHANGES (AD verdict ITERATE — hero is cleanest in set, KEEP it; but the
diagonal-cut signature + tri-culm stepping collapse at 32px). The signature has
to survive the downscale BLUR, so:
  1. The FRONT (centre) culm's cut-mouth is now a dominant BRIGHT CREAM DISC —
     the cut-oval is enlarged ~1.7x relative diameter and the dark cavity is
     shrunk + lightened so the small-scale read is a bright disc, not a hole.
     The cream ring is the single brightest value on the form.
  2. Front-back hierarchy: the front mouth is big+bright; the two stepped-back
     mouths are smaller cream nubs (one cut + two hints = a cluster, not noise).
  3. Night read: the green body is lifted ~15% in value/warmth and a thin warm
     rim-keyline rides the culm edges so the three-culm stepping survives 32px
     on a night sky (round 1 lost everything but the gold face-glow at night).
  4. Stepping widened at small scale: the horizontal offset between the three
     culms is increased and the back-culm green darkened a step so the back
     culms don't merge into the centre — the stepped-cluster KIND survives blur.
  5. Pillar gap-cap reworked as an explicit fresh diagonal CUT: a fatter cream
     cut-oval on a clear SLANT across the culm top (not a symmetric spear-point),
     pine tuft thrown to ONE side.
  6. Lower-mirror plum cap anchored in value: vermilion plum + cream cut-ring
     brightened/enlarged so it doesn't vanish into the green pillar on day.
  7. The straw bind reads as a horizontal BIND (no protruding arms) — protects
     body-is-bamboo + the silhouette KIND.

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
# WHY the greens are lifted ~15% in value+warmth vs round 1: the night biome
# washed the body to mud and the three-culm stepping disappeared — a warmer,
# brighter living-green holds its bands against the dark sky.
CULM      = (124, 188, 104)   # fresh-culm green (lifted warmer/brighter)
CULM_D    = ( 74, 138,  72)   # deep node-green shade (lifted a step)
CULM_DD   = ( 50, 102,  56)   # deepest groove / node-collar shadow band
CULM_HI   = (172, 216, 130)   # sun-side fresh-green highlight band (warm/yellow)
CULM_HOT  = (208, 232, 158)   # hottest green sheen rail (top-left sun)
CULM_RIM  = (158, 206, 116)   # thin WARM rim-keyline on culm edges (night hold)
CULM_BACK = ( 58, 116,  62)   # back-culm body green, darkened a step (stepping)
CUT_CREAM = (224, 214, 170)   # pale diagonal-cut ring-wall (the signature POP)
CUT_HI    = (244, 238, 206)   # lit cut-rim sheen — BRIGHTEST value on the form
CUT_D     = (180, 166, 120)   # cut-ring shade (cavity-side lip)
CAVITY    = (118, 128,  92)   # the hollow inner cavity (lightened — a disc, not hole)
CAVITY_DD = ( 86,  98,  70)   # cavity floor (lightened so the cream still dominates)
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
def culm_shaft(surf, cx, top, bot, half_w, s, node_pitch, body_col=CULM,
               shade_col=CULM_D, deep_col=CULM_DD):
    """A vertical living-bamboo shaft built as a stack of node-segments, each
    lit with 4 HARD STEPPED value bands across its width (sheen rail | hi | fill
    | deep) — NO smooth gradient — so it reads as a turned cylinder of fresh
    green at 32px. Node rings are the two-ring madake collar: a hard CULM_DD
    groove with a pale swollen ring above it.

    WHY a thin WARM rim-keyline (CULM_RIM) rides the two long edges: on a night
    biome the green body collapses toward the dark sky and the three stepped
    culms merge; a bright warm rim holds each culm's edge so the stepping reads.
    `body_col` lets the back culms render a step darker so they don't merge into
    the centre at small scale. Caller caps the top with the diagonal cut."""
    lw = max(2, int(1.6 * s))
    # body fill column (rounded top so the cut/cap sits on a real culm end)
    body = [(cx - half_w, bot), (cx - half_w, top + half_w),
            (cx, top), (cx + half_w, top + half_w), (cx + half_w, bot)]
    pygame.draw.polygon(surf, INK, body)
    pygame.draw.polygon(surf, body_col, body)
    # 4 HARD vertical value bands across the cylinder (right = shade, left = sun)
    # WHY the bands track body_col: a darkened back culm keeps its own internal
    # shading so it still reads as a turned cylinder, just a value-step recessed.
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
    # NODE RINGS — two-ring madake collar, repeated at node_pitch
    y = bot - node_pitch
    while y > top + half_w + node_pitch * 0.3:
        # hard dark groove
        pygame.draw.rect(surf, deep_col,
                         (cx - half_w, y, half_w * 2, max(2, int(2.4 * s))))
        # swollen pale ring just above the groove (the node bulge)
        ring_col = CULM_HOT if body_col is CULM else CULM_HI
        pygame.draw.rect(surf, ring_col,
                         (cx - half_w, y - max(2, int(2.6 * s)),
                          half_w * 2, max(1, int(1.8 * s))))
        # tiny paired branch-stub nub at the node (Phyllostachys/madake tell)
        nub = max(2, int(2.2 * s))
        pygame.draw.polygon(surf, shade_col, [
            (cx - half_w, y - int(0.5 * s)),
            (cx - half_w - nub, y - nub),
            (cx - half_w - nub, y + int(1.0 * s))])
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
    surrounding a SMALL inner CAVITY, tilted so the high lip is on the left.

    WHY a bright cream DISC (not a ring around a hole): at 32px the downscale
    blur swallows the thin ring and the dark cavity dominates — the mouth read
    as a smudge in round 1. So the cut-oval is enlarged (~1.7x relative
    diameter via `dominance`), the cavity is shrunk to ~0.42 of the oval and
    LIGHTENED toward green-cream, and the lit upper-left sheen (CUT_HI) is the
    single BRIGHTEST value on the whole form. The dominant small-scale read is
    therefore a BRIGHT CREAM DISC that pops on day AND night.

    `dominance` scales the whole cut: 1.0 for the hero/front culm (big+bright),
    ~0.66 for the stepped-back culms (smaller cream nubs — hints, not equals)."""
    # the cut plane is an ellipse: wider than the culm (overhangs the rim) and
    # tall by `lean`; `dominance` pushes the front mouth dramatically larger.
    ew = int((half_w + int(1.4 * s)) * (1.0 + 0.62 * dominance))
    eh = int((half_w * lean + int(2 * s)) * (1.0 + 0.55 * dominance))
    ccx, ccy = cx, top
    # outer ink rim of the cut oval
    outer = pygame.Rect(ccx - ew, ccy - eh, ew * 2, eh * 2)
    pygame.draw.ellipse(surf, INK, outer.inflate(int(2.4 * s), int(2.4 * s)))
    # the pale cut-CREAM ring-WALL (the bright signature band, now fat)
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
    knot-tail hangs straight DOWN at the centre.

    WHY no out-flung side knot-tails any more: round 1's two tails read as
    protruding ARMS, which fights body-is-bamboo and muddies the silhouette
    KIND. The bind must read as a tight horizontal BIND across the bundle."""
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
    # a single short paired knot-tail dropping STRAIGHT down at centre (a knot,
    # not arms) — kept inside the bundle width so it never reads as a limb
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
    flanks at stepped heights) -> straw collar over the waist -> face + plum.

    ROUND-2 hierarchy: the FRONT (centre, tallest) culm carries the dominant
    big+bright cream cut-DISC (dominance=1.0); the two stepped-back culms carry
    smaller cream nubs (dominance~0.6) in a darker body-green and a WIDER
    horizontal offset so the stepped-cluster KIND survives the 32px blur."""
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
    # WHY a WIDER horizontal step + a darker back-culm green: the AD pin — the
    # cluster must read as THREE separate slant-cut culms; round 1's back culms
    # merged into the centre at 32px. Pushing them further out and a value-step
    # back keeps the stepped trio legible through the downscale blur. Drawn back
    # culm first so the front two overlap it.
    hw_c = int(11 * s)   # centre culm half-width
    hw_s = int(9 * s)    # side culm half-width
    node = int(20 * s)

    # back-left short culm (peeks behind, shortest) — darker body, small cream nub
    bl_x = cx - int(24 * s)
    bl_top = cy - int(46 * s)
    culm_shaft(surf, bl_x, bl_top, base_y - int(6 * s), hw_s, s, node,
               body_col=CULM_BACK, shade_col=CULM_DD)
    diagonal_cut(surf, bl_x, bl_top, hw_s, s, lean=0.60, dominance=0.55)

    # right culm (medium height) — darker body, small cream nub
    r_x = cx + int(25 * s)
    r_top = cy - int(78 * s)
    culm_shaft(surf, r_x, r_top, base_y - int(4 * s), hw_s, s, node,
               body_col=CULM_BACK, shade_col=CULM_DD)
    diagonal_cut(surf, r_x, r_top, hw_s, s, lean=0.62, dominance=0.62)

    # centre culm — TALLEST (heaven), the pillar source — DOMINANT bright cut-disc
    c_top = cy - int(110 * s)
    culm_shaft(surf, cx, c_top, base_y - int(2 * s), hw_c, s, node)
    diagonal_cut(surf, cx, c_top, hw_c, s, lean=0.64, dominance=1.0)

    # === STRAW COLLAR at the waist, binding all three ========================
    straw_collar(surf, cx, waist_y, int(30 * s), int(20 * s), s)

    # === the serene blessing-FACE where the bindings cross ====================
    bound_face(surf, cx, waist_y - int(1 * s), int(11 * s), s, lit=True)

    # === RED PLUM at the base (auspicious vermilion accent, base-anchored) ====
    plum_blossom(surf, cx - int(26 * s), base_y - int(6 * s), int(7 * s), s)
    plum_blossom(surf, cx + int(28 * s), base_y - int(2 * s), int(6 * s), s)
    plum_blossom(surf, cx + int(8 * s), base_y + int(8 * s), int(5 * s), s)


# ── the fresh diagonal-CUT pillar gap-cap (an explicit slant cut, not a point) ─
def cut_cap(surf, cx, cut_y, half_w, s):
    """The pillar's gap-edge cap: an explicit FRESH diagonal cut across the culm
    top. WHY a clear SLANT (not the symmetric spear-point of round 1): the cap
    must read as a freshly-cut culm-mouth at the gap chip. A fat cream cut-oval
    rides a visible diagonal plane (high lip left, low right), a pine tuft thrown
    to ONE side. Caller has already drawn the shaft up to cut_y."""
    # a slanted cream cut-plane: a fat tilted ellipse straddling the culm top
    ew = int((half_w + int(2 * s)) * 1.5)
    eh = int(half_w * 0.64 + int(3 * s))
    slant = int(half_w * 0.5)   # the cut rises to the left (the diagonal tell)
    # ink the slanted plane first
    plane = [(cx - ew, cut_y + slant), (cx + ew, cut_y - slant),
             (cx + ew, cut_y - slant + eh), (cx - ew, cut_y + slant + eh)]
    pygame.draw.polygon(surf, INK, [(x, y + 2) for (x, y) in plane])
    # the bright cream cut-oval on the slant (high-left lip)
    outer = pygame.Rect(cx - ew, cut_y - eh + slant, ew * 2, eh * 2)
    pygame.draw.ellipse(surf, INK, outer.inflate(int(2 * s), int(2 * s)))
    pygame.draw.ellipse(surf, CUT_CREAM, outer)
    sheen = pygame.Rect(cx - ew, cut_y - eh + slant, int(ew * 1.4), int(eh * 1.4))
    pygame.draw.ellipse(surf, CUT_HI, sheen)
    pygame.draw.ellipse(surf, CUT_CREAM, sheen.inflate(-int(ew * 0.5), -int(eh * 0.5)))
    # small cavity, offset to the low (right) side of the slant
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


# ── the centre culm → PILLAR mirror (the cleanest mirror in the set) ──────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The centre culm IS the pillar: fresh node-segments = the tileable shaft;
    the bright diagonal-CUT mouth + a pine sprig = the detachable gap-edge cap;
    the straw-bound base with plum = the lower mirror. AD PIN: protect this as
    the CLEANEST mirror in the set.

    ROUND-2: the gap cap is an explicit fresh diagonal CUT (cut_cap) and the
    lower-mirror plum cap is enlarged + value-anchored so it doesn't vanish into
    the green pillar on day. `cap` names the END that faces the GAP."""
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
        # gap-edge cap: explicit fresh diagonal-CUT mouth + a side pine sprig
        cut_y = bot - int(22 * s)
        culm_shaft(surf, cx, shaft_bot, cut_y + int(2 * s), half_w, s, node)
        cut_cap(surf, cx, cut_y, half_w, s)
        # lower mirror at TOP: straw collar + a value-anchored plum cap
        straw_collar(surf, cx, top + int(20 * s), int(18 * s), int(15 * s), s)
        _plum_cap(surf, cx, top + int(13 * s), half_w, s)
    else:
        shaft_top = top + cap_room
        shaft_bot = bot - base_room
        culm_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, node)
        cut_y = top + int(22 * s)
        # build the cut on a temp surface and flip so the mouth faces UP the gap
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        H = surf.get_height()
        culm_shaft(tmp, cx, H - (cut_y + int(2 * s)), H - shaft_top, half_w, s, node)
        cut_cap(tmp, cx, H - cut_y, half_w, s)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, 0))
        straw_collar(surf, cx, bot - int(20 * s), int(18 * s), int(15 * s), s)
        _plum_cap(surf, cx, bot - int(13 * s), half_w, s)


def _plum_cap(surf, cx, cy, half_w, s):
    """The lower-mirror plum cap, value-ANCHORED. WHY bigger + a bright cream
    cut-ring behind it: round 1's small plums vanished into the green pillar on
    day. A fatter cream disc behind a larger vermilion plum keeps the lower
    mirror reading as a distinct cap at the pillar chip on day AND night."""
    # a fat cream cut-ring disc anchors the cap against the green body
    disc = pygame.Rect(cx - int(half_w * 1.3), cy - int(half_w * 0.9),
                       int(half_w * 2.6), int(half_w * 1.8))
    pygame.draw.ellipse(surf, INK, disc.inflate(int(2 * s), int(2 * s)))
    pygame.draw.ellipse(surf, CUT_CREAM, disc)
    pygame.draw.ellipse(surf, CUT_HI, disc.inflate(-int(half_w * 0.9), -int(half_w * 0.6)))
    # the brightened vermilion plum sits on the cream disc
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
    sheet.blit(font_big.render("KADOMATSU-SHIN", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "New-Year gate-god of three diagonal-cut culms  ·  TRI-CULM CUT CLUSTER · stepped heights · "
        "BRIGHT CREAM cut-DISC front mouth · warm rim night-hold · round 2",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_kadomatsu(big, 178 * SS, 230 * SS, 1.55 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Body-is-bamboo — hero", True, LABEL), (96, 566))
    sheet.blit(font_sm.render("FRONT culm = dominant big+bright CREAM cut-DISC (brightest value); two stepped-", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("back culms = smaller cream nubs, darker body, wider offset — one cut + two hints.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Warm rim-keyline holds the culm edges; horizontal straw BIND (no protruding arms).", True, LABEL_DIM), (14, 622))

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
    sheet.blit(font_sm.render("node-segments = repeat shaft; explicit fresh", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("diagonal-CUT + side pine = gap cap; value-", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("anchored plum-on-cream = lower mirror", True, LABEL_DIM), (pcx - 4, 746))

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
    sheet.blit(font_sm.render("32px on night sky — stepping + cream", True, LABEL_DIM), (panel_x + 20, night_y + 156))
    sheet.blit(font_sm.render("disc must hold (round-1 fail point)", True, LABEL_DIM), (panel_x + 20, night_y + 170))

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

    sil_y = night_y + 198
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 214, 200), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 30))
    sheet.blit(font_sm.render("THREE STEPPED culms (wider", True, LABEL_DIM), (sx + 104, sil_y + 48))
    sheet.blit(font_sm.render("offset), bound at the waist", True, LABEL_DIM), (sx + 104, sil_y + 64))

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
        (STRAW, "straw-rope"), (PLUM, "vermilion plum"),
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
        "REALISM pipeline (NOT chibi): SS=6 supersample -> smoothscale.  4-6 HARD STEPPED value bands · NO gradients · ink keyline (28,22,30) · "
        "1px grown outline · radial glow ACCENTS only.  R2: bright cream cut-DISC front mouth · warm rim night-hold · wider stepping · slant gap-cut.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
