"""
Round-3 (FINAL) concept renderer for SHISHI-KADOMATSU — the bound-culm guardian
lion (Kadomatsu brood, concept #5, the set's creature-centrality entry).
Headless Pygame; ELEVATED-REALISM pipeline cloned VERBATIM from the parent
KADOMATSU-SHIN harness (SS=6 -> smoothscale; ZERO gradients, hard stepped value
bands only; ink keyline (28,22,30) + 1px grown outline; radial glow for ACCENTS
only).

ROUND-3 is the BUDGET-ENDING pass and is judged on the BLACKOUT FIRST. Round 2
recovered the concept in COLOR (planted green-culm quadruped, forward cream
crown) but FAILED the blackout: it domed into a temple-bell with a bright center
window, no four-post count, the crown rim went solid black. The color pose is
KEPT verbatim (body raft, four bound-culm legs, cut-disc crown technique, indigo
brow-cord, base plum/straw). The targeted blackout wins:

  1. CROWN RIM SURVIVES BLACKOUT. Negative space, not value, is what survives a
     mask. The OUTER cut-discs are now drawn with a 1px INK GAP between adjacent
     discs (the outer contour is scalloped) and a bright-cream 1px lip rides the
     outermost ring, so when everything collapses to black the crown reads as a
     NOTCHED / SCALLOPED arc — not a solid dome cap. (Highest-value fix.)
  2. FOUR LEGS CARVED INTO THE BLACK SKIRT. Three sky-colored negative-space
     SLOTS are punched THROUGH the bottom — an outer-left gap, a center
     front/back gap, an outer-right gap — so the blackout shows FOUR separate
     black posts in a row. Round 2 had only one central notch -> one mass.
  3. BODY BLOCK LOWERED + WIDENED. The crown is dropped so it sits forward/low
     over the body (not a high halo), and the horizontal lashed-culm raft is
     extended a touch WIDER than the crown so the black shape is wider-than-tall
     (komainu stance, not a dome). Crown <=45% of total mass.
  4. CENTER FACE-WINDOW KILLED IN BLACKOUT. The lit blessing glow is suppressed
     in the reduced read and the bright cut-disc RIM out-values the face, so the
     eye reads the RING of cut-tips, not a central jewel/medallion.
  5. A node-ring collar still steps each of the four leg-posts in the COLOR chips
     once separated (the load-bearing bamboo cue).
  6. The recessed back leg-pair is lifted ~12% value so it contributes to the
     black skirt without flattening front/back depth in color.

KEEP CONDITION: the mane is still mane_ring() — a discrete RING OF CREAM
CUT-DISCS, never fur. The held-apart accent is the indigo mane-cord + brow.

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
# WHY lifted ~12% (was (58,116,62)): the recessed back legs must still read as
# solid black mass in the blackout skirt without flattening front/back depth.
CULM_BACK = ( 70, 130,  74)   # back-culm body green, lifted a step (blackout mass)
CUT_CREAM = (224, 214, 170)   # pale diagonal-cut ring-wall (the signature POP)
CUT_HI    = (244, 238, 206)   # lit cut-rim sheen — BRIGHTEST value on the form
CUT_D     = (180, 166, 120)   # cut-ring shade (cavity-side lip)
CUT_LIP   = (250, 244, 220)   # outermost-ring bright lip (survives blackout rim)
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
# WHY the face plane is stepped DOWN (was (240,230,188)/(196,178,132)): in the
# blackout it must NOT out-value the cream crown rim — the signature is the RING
# of cut-tips, not a central glowing jewel. It still reads serene-cream in color.
FACE      = (208, 198, 158)   # serene bound-face plane (gold-touched cream, calmer)
FACE_D    = (158, 144, 106)   # face shade band
INK       = ( 28,  22,  30)   # hard ink keyline

# ── the ONE held-apart accent for THIS concept: indigo-cobalt (heraldic blue) ──
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


# ── a fresh madake CULM segment laid HORIZONTAL (the body-raft culms) ─────────
def culm_shaft_h(surf, left, right, cy, half_h, s, node_pitch, body_col=CULM,
                 shade_col=CULM_D, deep_col=CULM_DD):
    """The same node-segmented madake culm as `culm_shaft`, but rotated to run
    LEFT->RIGHT — the front-to-back culms that make up the body raft. 4 HARD
    STEPPED value bands across its HEIGHT (top sheen | hi | fill | deep belly)
    so it reads as a turned horizontal cylinder; the two-ring madake node
    collars run VERTICALLY across it at node_pitch."""
    lw = max(2, int(1.6 * s))
    body = pygame.Rect(left, cy - half_h, right - left, half_h * 2)
    pygame.draw.rect(surf, INK, body, border_radius=int(half_h))
    pygame.draw.rect(surf, body_col, body, border_radius=int(half_h))
    hi_col = CULM_HI if body_col is CULM else lerp(body_col, CULM_HI, 0.45)
    bands = ((-1.00, -0.50, hi_col), (-0.50, -0.10, body_col),
             (-0.10, 0.46, body_col), (0.46, 1.00, shade_col))
    for y0, y1, col in bands:
        by0 = cy + int(half_h * y0)
        by1 = cy + int(half_h * y1)
        pygame.draw.rect(surf, col, (left, by0, right - left, max(1, by1 - by0)))
    rail = max(2, int(half_h * 0.18))
    rail_col = CULM_HOT if body_col is CULM else CULM_HI
    pygame.draw.rect(surf, rail_col, (left + int(2 * s), cy - half_h, right - left - int(4 * s), rail))
    x = left + node_pitch
    while x < right - node_pitch * 0.3:
        pygame.draw.rect(surf, deep_col,
                         (x, cy - half_h, max(2, int(2.4 * s)), half_h * 2))
        ring_col = CULM_HOT if body_col is CULM else CULM_HI
        pygame.draw.rect(surf, ring_col,
                         (x - max(2, int(2.6 * s)), cy - half_h,
                          max(1, int(1.8 * s)), half_h * 2))
        x += node_pitch
    pygame.draw.rect(surf, INK, body, lw, border_radius=int(half_h))


# ── the DIAGONAL-CUT MOUTH — the signature: bright cream DISC + small cavity ──
def diagonal_cut(surf, cx, top, half_w, s, lean=0.62, dominance=1.0,
                 bright_lip=False):
    """The steep sogi slant-cut culm-mouth: a bright OVAL of cut-CREAM ring-wall
    surrounding a SMALL inner CAVITY, tilted so the high lip is on the left. The
    dominant small-scale read is a BRIGHT CREAM DISC that pops on day AND night.

    `bright_lip` (used by the OUTER crown discs): rides a 1px CUT_LIP rim around
    the disc so the crown's outermost contour holds bright in the blackout
    instead of collapsing to a solid black dome cap."""
    ew = int((half_w + int(1.4 * s)) * (1.0 + 0.62 * dominance))
    eh = int((half_w * lean + int(2 * s)) * (1.0 + 0.55 * dominance))
    ccx, ccy = cx, top
    outer = pygame.Rect(ccx - ew, ccy - eh, ew * 2, eh * 2)
    pygame.draw.ellipse(surf, INK, outer.inflate(int(2.4 * s), int(2.4 * s)))
    if bright_lip:
        pygame.draw.ellipse(surf, CUT_LIP, outer.inflate(int(1.2 * s), int(1.2 * s)))
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


# ── a woven straw-rope COLLAR band (the waist / anklet / lashing binding) ─────
def straw_collar(surf, cx, cy, half_w, h, s, knot=True):
    """The woven rice-straw rope: a fat band of diagonal STRANDS (alternating
    lit/shade so it reads woven) wrapping the bundle, with an optional short
    paired knot-tail dropping straight DOWN at centre. HARD STEPPED — no blur."""
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
    if not knot:
        return
    for sgn in (-1, 1):
        tx = cx + sgn * int(4 * s)
        pygame.draw.polygon(surf, STRAW, [
            (tx - int(3 * s), band.bottom),
            (tx + int(3 * s), band.bottom),
            (tx + int(2 * s), band.bottom + int(9 * s)),
            (tx - int(2 * s), band.bottom + int(9 * s))])
        pygame.draw.polygon(surf, STRAW_D, [
            (tx, band.bottom),
            (tx + int(3 * s), band.bottom),
            (tx + int(2 * s), band.bottom + int(9 * s))])


# ── a horizontal straw LASHING band wrapping the body raft ────────────────────
def straw_lashing(surf, cx, top, bot, half_w, s):
    """A VERTICAL straw band wrapping ACROSS the three horizontal body culms so
    the raft reads bound. Narrow + clean (no dangling knot) so green still
    dominates the body silhouette — straw is ONLY the binding bands here."""
    band = pygame.Rect(cx - half_w, top, half_w * 2, bot - top)
    pygame.draw.rect(surf, INK, band.inflate(int(2 * s), int(2 * s)))
    pygame.draw.rect(surf, STRAW_D, band)
    strand_h = max(3, int(4.0 * s))
    y = band.top - half_w
    i = 0
    while y < band.bottom + half_w:
        col = STRAW_HI if i % 3 == 0 else (STRAW if i % 3 == 1 else STRAW_D)
        pygame.draw.polygon(surf, col, [
            (band.left, y), (band.left, y + strand_h),
            (band.right, y + strand_h + half_w), (band.right, y + half_w)])
        y += strand_h
        i += 1
    pygame.draw.rect(surf, INK, (band.left, band.top, max(2, int(2 * s)), band.height))
    pygame.draw.rect(surf, STRAW_D, (band.right - max(2, int(2 * s)), band.top,
                                     max(2, int(2 * s)), band.height))
    pygame.draw.rect(surf, INK, band, max(1, int(1.4 * s)))


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
    """The serene Toshigami face glowing where the bindings cross. ROUND-3: the
    face plane is stepped DOWN in value (FACE/FACE_D) and the pale-gold blessing
    glow is dialed WAY back, so in the blackout the face never out-values the
    cream crown rim — the signature is the RING of cut-tips, not a central jewel.
    It still reads serene-cream against the crown in color."""
    if lit:
        # WHY a small, low-alpha bloom (was 1.9r / alpha 150): a big bright glow
        # is exactly the "lit center window" the blackout failed on. Keep it a
        # quiet warmth that does not dominate the reduced read.
        g = radial_glow(int(r * 1.0), GLOW, alpha_center=70, falloff=2.6)
        surf.blit(g, (cx - g.get_width() // 2, cy - g.get_height() // 2),
                  special_flags=pygame.BLEND_ADD)
    face = pygame.Rect(cx - r, cy - int(r * 1.04), r * 2, int(r * 2.08))
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
    pygame.draw.circle(surf, PLUM, (cx, cy - int(r * 0.6)), max(1, int(r * 0.16)))
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


# ══ SHISHI construction — round 3 (WIN THE BLACKOUT) ══════════════════════════

def leg_bundle(surf, cx, top, bot, half_w, s, recessed=False):
    """A planted leg = a SHORT VERTICAL CULM STACK (parent culm_shaft node
    treatment, ported verbatim) with >=1 node-ring collar + a straw anklet at the
    planted paw. The gate is FOUR clearly-separate green-stepped POSTS in the
    blackout; a fat single node-segmented culm reads as one clean post at 32px.
    `recessed` darkens the back pair a value-step (lifted CULM_BACK) so the front
    pair reads in front of them yet the back pair still carries black mass.

    node_pitch is set so each short leg shows >=1 madake collar even at 32px, so
    a separated blackout leg reads BAMBOO POST."""
    body_col = CULM_BACK if recessed else CULM
    shade_col = CULM_DD if recessed else CULM_D
    node = max(int(10 * s), int((bot - top) * 0.42))
    culm_shaft(surf, cx, top, bot, half_w, s, node,
               body_col=body_col, shade_col=shade_col)
    straw_collar(surf, cx, bot - int(7 * s), int(half_w * 1.1), int(9 * s), s, knot=True)


def mane_ring(surf, cx, cy, R, s, n=11, blue_cord=True):
    """THE KEEP CONDITION — the mane as a RING OF DISCRETE CREAM CUT-DISCS, not
    fur. ROUND-3 blackout fix: each OUTER disc is drawn with a bright CUT_LIP rim
    (`bright_lip=True`) AND the dark inner-ring fills stop SHORT of the disc tips
    so a 1px INK GAP sits between adjacent outer discs — the outer contour is
    SCALLOPED, so the blackout reads a notched arc of cut-tips, never a solid
    dome cap. The crown is ~42-45% of total mass (it FRAMES the head).

    Built as: a dark culm-stub spoke in to the face ring -> a chunky diagonal_cut
    cream disc at each scallop with a bright outer lip. A thin INDIGO brow-cord
    arcs across the TOP of the ring (the held-apart heraldic accent — line-work
    only, never a fill)."""
    inner = R * 0.50
    # WHY the back fills are pulled IN to R*0.78 (was R*1.04): the old CUT_D ring
    # at R*1.04 bridged the gaps between the outer discs, so the blackout outer
    # contour fused into a solid dome. Holding the dark fills inside the disc
    # tips leaves an INK GAP between adjacent discs -> a scalloped contour.
    pygame.draw.circle(surf, INK, (cx, cy), int(R * 0.84))
    pygame.draw.circle(surf, CULM_DD, (cx, cy), int(R * 0.80))
    pygame.draw.circle(surf, CULM_D, (cx, cy), int(inner * 1.06))
    spoke_w = max(2, int(3.0 * s))
    disc_pts = []
    for k in range(n):
        a = math.radians(-90) + k * (2 * math.pi / n)
        ca, sa = math.cos(a), math.sin(a)
        rx, ry = cx + ca * inner, cy + sa * inner
        tx, ty = cx + ca * R, cy + sa * R
        px, py = -sa, ca
        # spokes stop SHORT of the disc tip so dark mass never bridges the gaps
        ex, ey = cx + ca * (R * 0.82), cy + sa * (R * 0.82)
        pygame.draw.polygon(surf, INK, [
            (rx + px * (spoke_w + 1), ry + py * (spoke_w + 1)),
            (ex + px * (spoke_w + 1), ey + py * (spoke_w + 1)),
            (ex - px * (spoke_w + 1), ey - py * (spoke_w + 1)),
            (rx - px * (spoke_w + 1), ry - py * (spoke_w + 1))])
        pygame.draw.polygon(surf, CULM_BACK, [
            (rx + px * spoke_w, ry + py * spoke_w),
            (ex + px * spoke_w, ey + py * spoke_w),
            (ex - px * spoke_w, ey - py * spoke_w),
            (rx - px * spoke_w, ry - py * spoke_w)])
        disc_pts.append((tx, ty, k))
    # CHUNKY cream discs AFTER the spokes — each with a bright outer LIP so the
    # outermost ring holds bright in the blackout (scalloped, not solid-black)
    for (tx, ty, k) in disc_pts:
        dom = 0.92 if k % 2 == 0 else 0.74   # alternating size = ring rhythm
        hw = int(R * (0.200 if k % 2 == 0 else 0.170))
        diagonal_cut(surf, int(tx), int(ty), hw, s, lean=0.80, dominance=dom,
                     bright_lip=True)
    # the INDIGO BROW-CORD arcing across the TOP of the ring (held-apart accent)
    if blue_cord:
        bw = max(2, int(2.8 * s))
        brow = pygame.Rect(cx - int(R * 0.70), cy - int(R * 0.78),
                           int(R * 1.40), int(R * 1.00))
        pygame.draw.arc(surf, INDIGO_D, brow.inflate(int(2 * s), int(2 * s)),
                        math.radians(20), math.radians(160), bw + max(1, int(s)))
        pygame.draw.arc(surf, INDIGO, brow,
                        math.radians(20), math.radians(160), bw)
        for sgn in (-1, 1):
            nx = cx + sgn * int(R * 0.66)
            ny = cy - int(R * 0.28)
            pygame.draw.circle(surf, INDIGO_HI, (nx, ny), max(2, int(2.2 * s)))
            pygame.draw.circle(surf, INDIGO_D, (nx, ny), max(1, int(1.1 * s)))


# ── THE HERO: the squat crouched bound-culm guardian lion ─────────────────────
def draw_shishi(surf, cx, cy, s, sky_slot=None):
    """The bound-culm guardian lion as a true squat QUADRUPED (komainu / foo-dog
    stance): a LOW WIDE horizontal body BLOCK — a lashed raft of three horizontal
    green culms — sitting on FOUR planted leg-bundles; a forward-set RING-CROWN
    of chunky cream cut-discs is the head/face on top of the forelegs.

    ROUND-3 blackout wins, judged FIRST:
      · body raft EXTENDED WIDER than the crown + crown DROPPED low/forward so
        the black shape is WIDER-THAN-TALL (komainu, not a dome). Crown <=45%.
      · THREE negative-space SLOTS punched through the bottom (outer-L gap,
        center front/back gap, outer-R gap) so the black skirt resolves to FOUR
        separate posts. `sky_slot` is the backdrop color carved through (the chip
        passes its sky color; None = transparent erase for the blackout mask).
      · the crown rim is scalloped + bright-lipped (see mane_ring); the face is
        value-stepped-down so the eye reads the RING, not a center window.

    `s` = unit scale around a ~150-unit figure.
    KEEP CONDITION: the mane is mane_ring() — discrete cream cut-discs, never fur.
    The held-apart accent is the indigo brow-cord."""
    ground_y = cy + int(50 * s)
    # WHY widened (body_w 50 -> 58) + shallower (body_h 26 -> 22): the black mass
    # must be wider-than-tall. The raft is now WIDER than the crown radius.
    body_w = int(58 * s)
    body_h = int(22 * s)
    body_cy = cy + int(8 * s)
    body_top = body_cy - body_h // 2
    body_bot = body_cy + body_h // 2

    leg_hw = int(7 * s)
    leg_top = body_bot - int(3 * s)
    leg_bot = ground_y
    # WHY pushed outboard (front 38->44, back 20->17): the front/back posts must
    # sit in FOUR clearly-separated columns so the carved sky-slots leave four
    # standing black posts. Back pair inboard of the front pair, front pair wide.
    front_x = int(44 * s)
    back_x = int(17 * s)

    # === BASE PINE MASS + PLUM (broad, bottom-anchored — the grounded crouch) ==
    for sgn, ang in ((-1, math.radians(208)), (1, math.radians(-28)),
                     (-1, math.radians(232)), (1, math.radians(-52))):
        pine_fan(surf, (cx + sgn * int(46 * s), ground_y + int(1 * s)),
                 ang, math.radians(56), 5, 24 * s, s, sign=sgn)

    # === BACK LEG PAIR (recessed a lifted value-step; drawn first) =============
    leg_bundle(surf, cx - back_x, leg_top - int(2 * s), leg_bot - int(2 * s),
               int(leg_hw * 0.92), s, recessed=True)
    leg_bundle(surf, cx + back_x, leg_top - int(2 * s), leg_bot - int(2 * s),
               int(leg_hw * 0.92), s, recessed=True)

    # === the LASHED-CULM BODY RAFT (three horizontal green culms, GREEN-dominant)
    raft_left = cx - body_w
    raft_right = cx + body_w
    n_culm = 3
    ch = body_h / n_culm
    half_h = int(ch * 0.56)
    node = int(22 * s)
    for i in range(n_culm):
        yy = int(body_top + (i + 0.5) * ch)
        bc = CULM if i == 0 else (CULM if i == 1 else CULM_BACK)
        sc = CULM_D if i < 2 else CULM_DD
        culm_shaft_h(surf, raft_left, raft_right, yy, half_h, s, node,
                     body_col=bc, shade_col=sc)
    for lx in (cx - int(28 * s), cx + int(26 * s)):
        straw_lashing(surf, lx, body_top - int(2 * s), body_bot + int(2 * s),
                      int(5 * s), s)

    # === FRONT LEG PAIR (overlap the body front edge — the planted forelegs) ===
    leg_bundle(surf, cx - front_x, leg_top, leg_bot, leg_hw, s)
    leg_bundle(surf, cx + front_x, leg_top, leg_bot, leg_hw, s)

    # === CARVE THE THREE NEGATIVE-SPACE SLOTS (the four-post blackout fix) ======
    # WHY carve sky THROUGH the skirt after the legs are down: negative space —
    # not value — is what survives a blackout mask. Three gaps (outer-L between
    # body-edge and the left front post is left open by geometry; here we punch
    # the INTER-POST gaps) split the bottom into FOUR standing black posts:
    #   gap A = between left front post and left/center mass
    #   gap B = the deep CENTER gap between the two back posts (front/back split)
    #   gap C = between right front post and right/center mass
    # The slots run from below the body raft down to the ground, leaving the
    # anklet paws intact so each post still terminates in a planted foot.
    slot_top = body_bot + int(2 * s)
    slot_bot = ground_y - int(6 * s)            # stop above the anklets/paws
    slot_w_outer = int(8 * s)
    slot_w_center = int(13 * s)                 # deepest split = front/back read
    erase = (sky_slot is None)
    slot_specs = [
        (cx - int(30 * s), slot_w_outer),       # gap A (left, between posts)
        (cx,               slot_w_center),      # gap B (center front/back split)
        (cx + int(30 * s), slot_w_outer),       # gap C (right, between posts)
    ]
    for scx, sw in slot_specs:
        rect = pygame.Rect(scx - sw // 2, slot_top, sw, slot_bot - slot_top)
        if erase:
            surf.fill((0, 0, 0, 0), rect)
        else:
            pygame.draw.rect(surf, sky_slot, rect)

    # === the forward RING-CROWN head + face (sits LOW/FORWARD over the body) ====
    # WHY dropped (was body_top-14 -> body_top-8) + radius trimmed (30 -> 27): the
    # crown must sit low/forward as the head, not a high halo, and stay <=45% of
    # total mass so the blackout is body-and-legs-dominant with a crown ON it.
    mane_cx = cx
    mane_cy = body_top - int(8 * s)
    mane_R = int(27 * s)
    mane_ring(surf, mane_cx, mane_cy, mane_R, s, n=11, blue_cord=True)
    bound_face(surf, mane_cx, mane_cy + int(1 * s), int(9 * s), s, lit=True)

    # === RED PLUM at the broad base (auspicious vermilion accent) ==============
    plum_blossom(surf, cx - int(54 * s), ground_y - int(2 * s), int(6 * s), s)
    plum_blossom(surf, cx + int(56 * s), ground_y, int(6 * s), s)
    plum_blossom(surf, cx, ground_y + int(8 * s), int(5 * s), s)


# ── the foreleg-bundle culm → PILLAR mirror ───────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """A FORELEG-BUNDLE culm IS the pillar: a bound node-segment shaft = the
    tileable body; a MANE cut-disc = the detachable gap-edge cap; the planted paw
    + straw anklet + plum = the lower mirror. `cap` names the END that faces the
    GAP."""
    half_w = int(13 * s)
    node = int(26 * s)
    cap_room = int(46 * s)
    base_room = int(40 * s)

    if cap == "bottom":
        shaft_top = top + base_room
        shaft_bot = bot - cap_room
        for off in (-int(5 * s), int(5 * s)):
            culm_shaft(surf, cx + off, shaft_top, shaft_bot,
                       int(half_w * 0.72), s, node,
                       body_col=CULM_BACK, shade_col=CULM_DD)
        culm_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, node)
        cut_y = bot - int(22 * s)
        culm_shaft(surf, cx, shaft_bot, cut_y + int(2 * s), half_w, s, node)
        cut_cap(surf, cx, cut_y, half_w, s)
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
    the lower mirror reads as a distinct planted-paw cap on day AND night."""
    disc = pygame.Rect(cx - int(half_w * 1.4), cy - int(half_w * 0.9),
                       int(half_w * 2.8), int(half_w * 1.8))
    pygame.draw.ellipse(surf, INK, disc.inflate(int(2 * s), int(2 * s)))
    pygame.draw.ellipse(surf, CUT_CREAM, disc)
    pygame.draw.ellipse(surf, CUT_HI, disc.inflate(-int(half_w * 1.0), -int(half_w * 0.6)))
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
        "bound-culm GUARDIAN LION  ·  R3 FINAL — WIN THE BLACKOUT: scalloped bright-lipped crown rim · THREE carved sky-slots = FOUR black posts · "
        "low WIDE raft (wider-than-tall) · value-stepped face (no center window) · indigo brow-cord",
        True, LABEL_DIM), (310, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_shishi(big, 178 * SS, 250 * SS, 1.55 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Squat quadruped — guardian hero", True, LABEL), (52, 566))
    sheet.blit(font_sm.render("LOW WIDE lashed-culm RAFT body (wider than the crown); FOUR bound culm-stack legs", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("w/ node rings + straw anklets, split by THREE carved gaps (front pair wide + recessed back).", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("LOW FORWARD ring-crown head = cream cut-discs, scalloped + bright-lipped rim; indigo brow-cord.", True, LABEL_DIM), (14, 622))

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

    # WHY pass a sky color into the chip: the negative-space slots are carved as
    # the actual sky behind the figure on day/night, exactly as they will read in
    # the live game over the biome backdrop (four posts visible against sky).
    def chip32(sky_col):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_shishi(big, 48 * SS, 50 * SS, (32 / 132.0) * SS, sky_slot=sky_col)
        small = pygame.transform.smoothscale(big, (96, 96))
        return grow_outline(small, INK + (255,), 1)

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip32(DAY_SKY_B), (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky — slots carve sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip32(NIGHT_B), (panel_x + 20 + 27, night_y + 27))
    sheet.blit(font_sm.render("32px night — FOUR green posts +", True, LABEL_DIM), (panel_x + 20, night_y + 156))
    sheet.blit(font_sm.render("scalloped cream crown must hold", True, LABEL_DIM), (panel_x + 20, night_y + 170))

    # blacked-out 32px silhouette — the ACCEPTANCE GATE: must read FOUR separate
    # black posts under a low wide body, crowned with a SCALLOPED bright ring of
    # cut-tips — NOT a domed bell with a lit center window. The slots are erased
    # (transparent), so the mask shows them as genuine negative space.
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_shishi(big, 48 * SS, 50 * SS, (32 / 132.0) * SS, sky_slot=None)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
        return sil

    # a SECOND blackout proof that PRESERVES the bright crown rim so the scallop
    # is visible: re-color the silhouette but paint the cream tones white. We do
    # this by masking only the cream-bright pixels separately.
    def silhouette32_rimlit():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_shishi(big, 48 * SS, 50 * SS, (32 / 132.0) * SS, sky_slot=None)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        # full mass -> black; then the brightest (cream rim) pixels -> bright lip
        mask = pygame.mask.from_surface(small, 24)
        sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
        out = sil.copy()
        w, hgt = small.get_size()
        small.lock()
        for yy in range(hgt):
            for xx in range(w):
                r, g, b, a = small.get_at((xx, yy))
                if a > 24 and (r + g + b) > 600:   # the cream rim / cut-tips
                    out.set_at((xx, yy), CUT_LIP + (255,))
        small.unlock()
        return out

    sil_y = night_y + 198
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 214, 200), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    # the rim-lit proof beside it so the scallop + four-post read is legible
    pygame.draw.rect(sheet, (212, 214, 200), (sx + 104, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx + 104, sil_y, 96, 96), 1)
    sheet.blit(silhouette32_rimlit(), (sx + 104, sil_y))
    sheet.blit(font_sm.render("BLACKOUT (left) + rim-lit (right):", True, LABEL), (sx, sil_y + 100))
    sheet.blit(font_sm.render("FOUR black posts (3 sky-slots) under a", True, LABEL_DIM), (sx, sil_y + 116))
    sheet.blit(font_sm.render("LOW WIDE body + SCALLOPED bright crown", True, LABEL_DIM), (sx, sil_y + 132))
    sheet.blit(font_sm.render("rim — NOT a domed bell w/ a lit window.", True, LABEL_DIM), (sx, sil_y + 148))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 220
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
        (CULM, "fresh-culm green"), (CULM_BACK, "back-culm (lifted)"),
        (CUT_CREAM, "cut-ring cream"), (CUT_LIP, "outer rim lip (blackout)"),
        (STRAW, "straw-rope"), (PLUM, "vermilion plum"),
        (INDIGO, "indigo brow-cord"), (INK, "ink keyline"),
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
        "1px grown outline · radial glow ACCENTS only.  R3 FINAL: scalloped bright-lipped crown rim · 3 carved sky-slots = 4 black posts · wider-than-tall raft.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
