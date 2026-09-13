"""
Round-1 concept renderer for SHISHI-KADOMATSU — the bound-culm guardian lion
(Kadomatsu brood, concept #5, the set's creature-centrality entry). Headless
Pygame; ELEVATED-REALISM pipeline cloned VERBATIM from the parent
KADOMATSU-SHIN harness (SS=6 -> smoothscale; ZERO gradients, hard stepped value
bands only; ink keyline (28,22,30) + 1px grown outline; radial glow for ACCENTS
only). Palette + the construction helpers (diagonal_cut, culm_shaft,
straw_collar, pine_fan, plum_blossom, bound_face, cut_cap, grow_outline,
radial_glow) are imported by copy from the parent so the brood reads as one
botanically-consistent family of fresh-cut bamboo.

WHY a guardian LION that must NOT be a green lion: this is the only horizontal/
quadruped form in the brood or the 4 bamboo-v2 siblings — a SQUAT CROUCHED beast,
low/heavy/broad, four planted leg-bundles, a body of lashed culm. The KEEP
CONDITION (locked brief §5) is the MANE: it may never read as fur. So the mane
is rebuilt as a RADIAL SUNBURST OF CREAM CUT-DISCS — a halo ring of bright
`diagonal_cut` culm-ends radiating around a serene blessing-face, so the mane IS
the cut-mouth signature, not animal hair. Built BRIGHT + DISCRETE (separate
cream nubs, not a solid blob) so at true 32px the crown reads as a RING OF CREAM
NUBS and the blackout reads "bundle-bodied beast crowned with a ring of cut-
tips," NOT "lion."

Held-apart accent: an INDIGO-COBALT brow / mane-cord — the ONLY cool-blue in the
brood (heraldic; deliberately never washes into the greens). It rides the inner
mane-ring as a thin cord and marks the brow so the guardian reads regal.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the helpers
cloned from the parent harness.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE — cloned VERBATIM from the parent (locked brief inherited DNA)
CULM      = (124, 188, 104)   # fresh-culm green (lifted warmer/brighter)
CULM_D    = ( 74, 138,  72)   # deep node-green shade
CULM_DD   = ( 50, 102,  56)   # deepest groove / node-collar shadow band
CULM_HI   = (172, 216, 130)   # sun-side fresh-green highlight band
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

# ── the ONE held-apart accent for THIS concept: indigo-cobalt (heraldic blue) ──
# WHY a cool blue that never touches the greens: every brood member adds exactly
# one held-apart accent off the roster green lanes; Shishi's is a regal indigo
# brow / mane-cord. Kept as thin cord + brow line-work, NEVER a fill, so it stays
# heraldic and can't wash into the fresh-green culm body.
INDIGO    = ( 64,  86, 168)   # indigo-cobalt mane-cord / brow accent
INDIGO_HI = (108, 132, 214)   # lit indigo cord highlight
INDIGO_D  = ( 38,  52, 116)   # indigo cord shade

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
    pale-gold blessing glow behind the face, never as a fill."""
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
    """A vertical living-bamboo shaft built as a stack of node-segments, each lit
    with 4 HARD STEPPED value bands across its width (sheen rail | hi | fill |
    deep) — NO smooth gradient — so it reads as a turned cylinder of fresh green
    at 32px. Node rings are the two-ring madake collar: a hard CULM_DD groove
    with a pale swollen ring above it. `body_col` lets bundled back-culms render
    a step darker so they don't merge at small scale."""
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


# ── the DIAGONAL-CUT MOUTH — the signature: bright cream DISC + small cavity ──
def diagonal_cut(surf, cx, top, half_w, s, lean=0.62, dominance=1.0):
    """The steep sogi slant-cut culm-mouth: a bright OVAL of cut-CREAM ring-wall
    surrounding a SMALL inner CAVITY, tilted so the high lip is on the left. The
    dominant small-scale read is a BRIGHT CREAM DISC that pops on day AND night.
    `dominance` scales the whole cut (1.0 hero, ~0.6 for nubs/mane-ring tips)."""
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


# ── a woven straw-rope COLLAR band (the waist / anklet binding) ───────────────
def straw_collar(surf, cx, cy, half_w, h, s):
    """The woven rice-straw rope: a fat band of diagonal STRANDS (alternating
    lit/shade so it reads woven) wrapping the bundle, with a short paired knot-
    tail dropping straight DOWN at centre. HARD STEPPED — no blur."""
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
    highlight pip) with a pale-gold pip centre. Base-anchored auspicious accent."""
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


# ── the serene bound FACE (the blessing-face at the heart of the mane-ring) ───
def bound_face(surf, cx, cy, r, s, lit=True):
    """The serene Toshigami face glowing where the bindings cross. A calm oval
    plane (cream, gold-touched) with closed-arc eyes + a small vermilion mark —
    minimal so it reads serene at 32px. The pale-gold blessing glow is the SOLE
    radial accent, behind the face."""
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


# ── the fresh diagonal-CUT pillar gap-cap (an explicit slant cut, not a point) ─
def cut_cap(surf, cx, cut_y, half_w, s):
    """The pillar's gap-edge cap: an explicit FRESH diagonal cut across the culm
    top — a fat cream cut-oval on a visible diagonal plane (high lip left), pine
    tuft thrown to ONE side. Caller has drawn the shaft up to cut_y."""
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


# ══ NEW for SHISHI — the guardian-lion construction ═══════════════════════════

def leg_bundle(surf, cx, top, bot, half_w, s):
    """A planted FORE/HIND leg as a BOUND bundle of stepped-green culms — never a
    smooth limb. WHY three offset culm_shafts (front bright, two back darker):
    the brief's gate is that the four legs read OBVIOUSLY as bound stepped-green
    culm bundles with visible node rings, so a blackout leg reads "bundle," not
    "paw." A straw anklet cinches the bundle low; a small cream cut-nub caps the
    knee where the front culm pokes above the lashing so the cut signature seeds
    even on the legs."""
    node = int(15 * s)
    # two back culms a value-step recessed, fanned slightly so the bundle reads
    for off, hw_k in ((-int(4 * s), int(0.78)), (int(4 * s), int(0.82))):
        culm_shaft(surf, cx + off, top + int(4 * s), bot,
                   max(2, int(half_w * 0.78)), s, node,
                   body_col=CULM_BACK, shade_col=CULM_DD)
    # the front (brightest) culm of the bundle
    culm_shaft(surf, cx, top, bot, half_w, s, node)
    # straw anklet cinching the bundle near the planted foot
    straw_collar(surf, cx, bot - int(10 * s), int(half_w * 1.05), int(11 * s), s)


def mane_ring(surf, cx, cy, R, s, n=13, blue_cord=True):
    """THE KEEP CONDITION — the mane as a RADIAL SUNBURST OF CREAM CUT-DISCS, not
    fur. n bright `diagonal_cut` culm-ends radiate around the blessing-face on a
    halo ring; each is a SEPARATE cream nub (discrete, never a solid blob) so at
    true 32px the crown reads as a RING OF CREAM NUBS and the blackout reads "ring
    of cut-tips," not "lion hair."

    Built as: a dark culm-stub spoke from the inner ring out to each disc (so each
    tip reads as a fresh-cut culm-end, mane IS the cut-mouth signature) -> a
    bright diagonal_cut disc at the spoke tip. A thin INDIGO mane-CORD threads the
    inner ring (the held-apart heraldic accent — the only cool blue, never a fill)
    with paired indigo nodes so it reads as a bound cord, not a glow.

    Two disc sizes alternate so the ring has rhythm but every nub stays discrete;
    the discs slightly overlap the spoke roots only, never each other."""
    inner = R * 0.52
    spoke_w = max(2, int(3.2 * s))
    # back ink halo so the bright discs pop cleanly off any sky at 32px
    pygame.draw.circle(surf, INK, (cx, cy), int(R * 1.06))
    pygame.draw.circle(surf, CULM_DD, (cx, cy), int(R * 0.98))
    pygame.draw.circle(surf, CULM_D, (cx, cy), int(inner * 1.04))
    # the spokes + cream cut-disc tips
    disc_pts = []
    for k in range(n):
        a = math.radians(-90) + k * (2 * math.pi / n)
        ca, sa = math.cos(a), math.sin(a)
        rx, ry = cx + ca * inner, cy + sa * inner
        tx, ty = cx + ca * R, cy + sa * R
        # dark culm-stub spoke (a fresh-cut culm-end pointing out of the ring)
        px, py = -sa, ca
        pygame.draw.polygon(surf, INK, [
            (rx + px * (spoke_w + 1), ry + py * (spoke_w + 1)),
            (tx + px * (spoke_w + 1), ty + py * (spoke_w + 1)),
            (tx - px * (spoke_w + 1), ty - py * (spoke_w + 1)),
            (rx - px * (spoke_w + 1), ry - py * (spoke_w + 1))])
        pygame.draw.polygon(surf, CULM_BACK, [
            (rx + px * spoke_w, ry + py * spoke_w),
            (tx + px * spoke_w, ty + py * spoke_w),
            (tx - px * spoke_w, ty - py * spoke_w),
            (rx - px * spoke_w, ry - py * spoke_w)])
        disc_pts.append((tx, ty, k))
    # draw the cream discs AFTER all spokes so the cut-tips sit cleanly on top
    for (tx, ty, k) in disc_pts:
        dom = 0.62 if k % 2 == 0 else 0.40   # alternating size = ring rhythm
        hw = int(R * (0.165 if k % 2 == 0 else 0.135))
        diagonal_cut(surf, int(tx), int(ty), hw, s, lean=0.78, dominance=dom)
    # the INDIGO mane-cord threading the inner ring (held-apart heraldic accent)
    if blue_cord:
        cw = max(2, int(2.6 * s))
        pygame.draw.circle(surf, INDIGO_D, (cx, cy), int(inner * 1.02), cw + max(1, int(s)))
        pygame.draw.circle(surf, INDIGO, (cx, cy), int(inner * 1.02), cw)
        # paired indigo cord-nodes so it reads as a bound cord, not a ring-glow
        for k in range(n):
            a = math.radians(-90) + (k + 0.5) * (2 * math.pi / n)
            nx = cx + math.cos(a) * inner * 1.02
            ny = cy + math.sin(a) * inner * 1.02
            pygame.draw.circle(surf, INDIGO_HI, (int(nx), int(ny)), max(2, int(2.0 * s)))
            pygame.draw.circle(surf, INDIGO_D, (int(nx), int(ny)), max(1, int(1.0 * s)))


# ── THE HERO: the squat crouched bound-culm guardian lion ─────────────────────
def draw_shishi(surf, cx, cy, s):
    """The bound-culm guardian lion: a SQUAT CROUCHED QUADRUPED — low, heavy,
    broad. A lashed-culm BODY mass sits on FOUR planted leg-bundles (each an
    obvious bound stack of stepped-green culms with node rings + straw anklets);
    a round RADIAL SUNBURST of cream cut-discs crowns a serene blessing-face at
    the chest/head; pine fans + plum anchor the broad base. `s` = unit scale
    around a ~150-unit figure.

    Built back-to-front: base pine mass -> the four leg-bundles -> the lashed
    body mass + waist straps -> the mane cut-disc ring with the face at its
    heart. The only horizontal/quadruped form in the brood; the blackout must
    read "bundle-bodied beast crowned with a ring of cut-tips," NOT "lion."

    KEEP CONDITION: the mane is mane_ring() — a discrete RING OF CREAM CUT-DISCS,
    never fur. The held-apart accent is the indigo mane-cord + brow."""
    ground_y = cy + int(54 * s)
    body_w = int(58 * s)        # broad, heavy crouch
    body_h = int(34 * s)
    body_top = cy - int(6 * s)

    # === BASE PINE MASS (broad, bottom-anchored — the grounded crouch) ========
    for sgn, ang in ((-1, math.radians(206)), (1, math.radians(-26)),
                     (-1, math.radians(230)), (1, math.radians(-50))):
        pine_fan(surf, (cx + sgn * int(34 * s), ground_y - int(2 * s)),
                 ang, math.radians(58), 6, 30 * s, s, sign=sgn)
    pine_fan(surf, (cx, ground_y + int(3 * s)), math.radians(90),
             math.radians(72), 6, 20 * s, s)

    # === FOUR PLANTED LEG-BUNDLES (obvious bound stepped-green culm stacks) ====
    # WHY a clear front/back leg pair offset: the silhouette must read quadruped.
    # Back legs first (recessed), then front legs overlapping the body.
    leg_hw = int(9 * s)
    leg_top = body_top + int(20 * s)
    leg_bot = ground_y - int(2 * s)
    # back pair (slightly inboard + higher root so they read behind the body)
    leg_bundle(surf, cx - int(30 * s), leg_top + int(4 * s), leg_bot - int(2 * s),
               int(leg_hw * 0.92), s)
    leg_bundle(surf, cx + int(30 * s), leg_top + int(4 * s), leg_bot - int(2 * s),
               int(leg_hw * 0.92), s)

    # === the LASHED-CULM BODY MASS (a broad bound bundle, the crouched torso) ==
    body = pygame.Rect(cx - body_w, body_top, body_w * 2, body_h)
    pygame.draw.rect(surf, INK, body.inflate(int(3 * s), int(3 * s)),
                     border_radius=int(14 * s))
    # the body is itself a horizontal raft of lashed culms — draw stacked
    # horizontal culm-bands (rotated culm read) so the torso is bamboo, not hide
    n_culm = 5
    ch = body_h / n_culm
    for i in range(n_culm):
        yy = body_top + int(i * ch)
        # alternate fill/shade bands = stacked round culms catching light
        col = CULM if i % 2 == 0 else CULM_D
        pygame.draw.rect(surf, col, (body.left, yy, body.width, int(ch) + 1),
                         border_radius=int(10 * s))
        # hard sheen rail along the top of each stacked culm
        pygame.draw.rect(surf, CULM_HI if i % 2 == 0 else CULM,
                         (body.left + int(3 * s), yy + int(1 * s),
                          body.width - int(6 * s), max(2, int(2.2 * s))))
        # node groove ticks along each culm so the torso reads bamboo at 32px
        for nx in range(int(body.left + 12 * s), int(body.right - 8 * s), int(20 * s)):
            pygame.draw.rect(surf, CULM_DD, (nx, yy, max(2, int(2.2 * s)), int(ch)))
    pygame.draw.rect(surf, INK, body, max(2, int(1.6 * s)), border_radius=int(14 * s))
    # two vertical straw LASHINGS cinching the body raft (bound-bundle tell)
    for lx in (cx - int(26 * s), cx + int(22 * s)):
        straw_collar(surf, lx, body_top + body_h // 2, int(4 * s),
                     int(body_h + 6 * s), s)

    # front leg pair (overlap the body front edge — the crouched forelegs)
    leg_bundle(surf, cx - int(40 * s), leg_top, leg_bot, leg_hw, s)
    leg_bundle(surf, cx + int(40 * s), leg_top, leg_bot, leg_hw, s)

    # === the MANE — radial sunburst of cream cut-discs around the face ========
    # WHY at the front/top of the crouch (a reared head over planted forelegs):
    # the crown is the dominant focal; the face sits at its heart.
    mane_cx = cx
    mane_cy = body_top - int(20 * s)
    mane_R = int(40 * s)
    mane_ring(surf, mane_cx, mane_cy, mane_R, s, n=13, blue_cord=True)
    bound_face(surf, mane_cx, mane_cy + int(1 * s), int(13 * s), s, lit=True)
    # the INDIGO heraldic BROW arc across the face (the held-apart blue, marked
    # so the guardian reads regal — never a fill, just a cord-stroke)
    pygame.draw.arc(surf, INDIGO_D,
                    (mane_cx - int(11 * s), mane_cy - int(11 * s),
                     int(22 * s), int(16 * s)),
                    math.radians(20), math.radians(160), max(2, int(2.6 * s)))
    pygame.draw.arc(surf, INDIGO,
                    (mane_cx - int(11 * s), mane_cy - int(12 * s),
                     int(22 * s), int(16 * s)),
                    math.radians(20), math.radians(160), max(2, int(2.0 * s)))

    # === RED PLUM at the broad base (auspicious vermilion accent) ==============
    plum_blossom(surf, cx - int(46 * s), ground_y - int(4 * s), int(7 * s), s)
    plum_blossom(surf, cx + int(48 * s), ground_y - int(2 * s), int(6 * s), s)
    plum_blossom(surf, cx + int(6 * s), ground_y + int(9 * s), int(5 * s), s)


# ── the foreleg-bundle culm → PILLAR mirror ───────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """A FORELEG-BUNDLE culm IS the pillar: bound node-segments = the tileable
    shaft; a MANE cut-disc = the detachable gap-edge cap; the planted paw + straw
    anklet + plum = the lower mirror. `cap` names the END that faces the GAP."""
    half_w = int(13 * s)
    node = int(26 * s)
    cap_room = int(46 * s)
    base_room = int(40 * s)

    if cap == "bottom":
        shaft_top = top + base_room
        shaft_bot = bot - cap_room
        # the bound bundle: two recessed back culms + the bright front culm
        for off in (-int(5 * s), int(5 * s)):
            culm_shaft(surf, cx + off, shaft_top, shaft_bot,
                       int(half_w * 0.72), s, node,
                       body_col=CULM_BACK, shade_col=CULM_DD)
        culm_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, node)
        # gap-edge cap: a MANE cut-disc (the crown signature as the gap cap)
        cut_y = bot - int(22 * s)
        culm_shaft(surf, cx, shaft_bot, cut_y + int(2 * s), half_w, s, node)
        cut_cap(surf, cx, cut_y, half_w, s)
        # lower mirror at TOP: planted-paw straw anklet + plum
        straw_collar(surf, cx, top + int(20 * s), int(18 * s), int(15 * s), s)
        _paw_cap(surf, cx, top + int(13 * s), half_w, s)
    else:
        shaft_top = top + cap_room
        shaft_bot = bot - base_room
        for off in (-int(5 * s), int(5 * s)):
            culm_shaft(surf, cx + off, shaft_top, shaft_bot,
                       int(half_w * 0.72), s, node,
                       body_col=CULM_BACK, shade_col=CULM_DD)
        culm_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, node)
        cut_y = top + int(22 * s)
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        H = surf.get_height()
        for off in (-int(5 * s), int(5 * s)):
            culm_shaft(tmp, cx + off, H - (cut_y + int(2 * s)), H - shaft_top,
                       int(half_w * 0.72), s, node,
                       body_col=CULM_BACK, shade_col=CULM_DD)
        culm_shaft(tmp, cx, H - (cut_y + int(2 * s)), H - shaft_top, half_w, s, node)
        cut_cap(tmp, cx, H - cut_y, half_w, s)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, 0))
        straw_collar(surf, cx, bot - int(20 * s), int(18 * s), int(15 * s), s)
        _paw_cap(surf, cx, bot - int(13 * s), half_w, s)


def _paw_cap(surf, cx, cy, half_w, s):
    """The lower-mirror PLANTED PAW cap: a broad bound foot of stepped culm-ends
    cinched by a straw anklet, value-ANCHORED with a cream cut-ring + a plum so
    the lower mirror reads as a distinct planted-paw cap at the pillar chip on
    day AND night (it doesn't vanish into the green pillar)."""
    disc = pygame.Rect(cx - int(half_w * 1.4), cy - int(half_w * 0.9),
                       int(half_w * 2.8), int(half_w * 1.8))
    pygame.draw.ellipse(surf, INK, disc.inflate(int(2 * s), int(2 * s)))
    pygame.draw.ellipse(surf, CUT_CREAM, disc)
    pygame.draw.ellipse(surf, CUT_HI, disc.inflate(-int(half_w * 1.0), -int(half_w * 0.6)))
    # three planted toe-culms (stepped) so the foot reads as a bound bundle-paw
    for sgn in (-1, 0, 1):
        tx = cx + sgn * int(half_w * 0.72)
        pygame.draw.circle(surf, INK, (tx, cy + int(half_w * 0.3)), int(half_w * 0.42) + 1)
        pygame.draw.circle(surf, CULM, (tx, cy + int(half_w * 0.3)), int(half_w * 0.42))
        pygame.draw.circle(surf, CULM_HI,
                           (tx - int(half_w * 0.1), cy + int(half_w * 0.18)),
                           int(half_w * 0.18))
    plum_blossom(surf, cx, cy, int(half_w * 0.56), s)


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
    sheet.blit(font_big.render("SHISHI-KADOMATSU", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "bound-culm GUARDIAN LION  ·  SQUAT CROUCHED QUADRUPED · four bound leg-bundles · "
        "mane = RADIAL RING OF CREAM CUT-DISCS (not fur) · indigo brow-cord · round 1",
        True, LABEL_DIM), (310, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_shishi(big, 178 * SS, 250 * SS, 1.40 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Body-is-bamboo — guardian hero", True, LABEL), (60, 566))
    sheet.blit(font_sm.render("MANE = radial sunburst of DISCRETE cream cut-discs (the cut-mouth signature,", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("NOT fur); four PLANTED leg-bundles = bound stepped-green culms w/ node rings.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Lashed-culm body raft; indigo mane-cord + brow = the held-apart heraldic blue.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, foreleg-bundle shaft =================
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
    sheet.blit(font.render("Pillar — foreleg bundle", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("bound culm-segments = repeat shaft; mane", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("cut-disc = gap cap; planted paw + straw", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("anklet + plum = value-anchored lower mirror", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_shishi(big, 48 * SS, 52 * SS, (32 / 150.0) * SS)
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
    sheet.blit(font_sm.render("32px on night — mane ring of cream", True, LABEL_DIM), (panel_x + 20, night_y + 156))
    sheet.blit(font_sm.render("nubs must hold (the KEEP condition)", True, LABEL_DIM), (panel_x + 20, night_y + 170))

    # blacked-out 32px silhouette — the KEEP TEST: must read squat quadruped +
    # ring-crown of cut-tips, NEVER a furry lion blob
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_shishi(big, 48 * SS, 52 * SS, (32 / 150.0) * SS)
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
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 24))
    sheet.blit(font_sm.render("SQUAT QUADRUPED + RING-CROWN", True, LABEL_DIM), (sx + 104, sil_y + 42))
    sheet.blit(font_sm.render("of cut-tips — NOT a furry lion", True, LABEL_DIM), (sx + 104, sil_y + 58))

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
        (INDIGO, "indigo mane-cord"), (INK, "ink keyline"),
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
        "REALISM pipeline (cloned from KADOMATSU-SHIN): SS=6 supersample -> smoothscale.  4-6 HARD STEPPED value bands · NO gradients · ink keyline (28,22,30) · "
        "1px grown outline · radial glow ACCENTS only.  R1 KEEP CONDITION: mane = RING of DISCRETE cream cut-discs, never fur · indigo held-apart accent.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
