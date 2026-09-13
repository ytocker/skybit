"""
Round-1 concept renderer for TATSU-NO-TAKEMURA — the coiling grove-serpent, the
ONE beast of the Kadomatsu brood (epic bamboo-PLANT bosses spun off
Kadomatsu-Shin). Headless Pygame; ELEVATED-REALISM pipeline (supersample SS=6 ->
smoothscale) cloned from the parent so the cut-disc maw + node geometry stay
crisp at downscale.

NORTH STAR (verbatim): "MAKE IT RELIABLE TO BAMBOO. IT IS A BOSS BAMBOO PLANT."
So the serpent's BODY *is* a stacked culm — node-collar rings ride the coil as
belly-scales, never a plain green tube. Mythic motion is flavor layered on top.

WHY this is the set's ONE BEAST and the only KINETIC/COILING form: it is a
VERTICAL COILING S/Ω-SERPENT — a thick ribboning culm-body looping up the frame
with the head reared at the top. Nothing else in the brood or the bamboo-v2
siblings coils (the Take-Tsuchigumo spider is a STAR of STRAIGHT legs, the literal
opposite). The epic hook is motion + length: the dragon of prosperity climbing
the gate. We keep to 2-3 GENEROUS loops (NOT tight spaghetti) so at true 32px the
silhouette reads as a winding S pinned by ONE bright cut-disc head.

HELD-APART ACCENT: a jade-teal whisker / dorsal-fin glint (70,150,140) — DARKER +
COOLER than CULM, deployed THREAD-THIN as filament-only accents (whiskers + a thin
fin-fringe). WHY never a body fill and never a soft glow: it must stay off the
Haedung jade lane and out of the fresh-culm green so the body still reads as
fresh-cut bamboo, with the teal a cool electric filigree riding the spine.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the helpers cloned
verbatim from the parent kadomatsu_shin/render_round_2.py harness.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE — cloned verbatim from the parent (brood DNA, non-negotiable) ─
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
CAVITY    = (118, 128,  92)   # the hollow inner cavity / open maw
CAVITY_DD = ( 86,  98,  70)   # cavity floor / maw throat
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

# ── THE held-apart accent (this concept ONLY) ────────────────────────────────
# Jade-teal whisker / dorsal-fin glint — DARKER + COOLER than CULM so it never
# washes into the fresh-green body and stays off the Haedung jade lane. Used as
# THREAD-THIN filament line-work ONLY (whiskers + a thin fin-fringe), never a fill.
TEAL      = ( 70, 150, 140)   # jade-teal filament accent
TEAL_HI   = (122, 200, 186)   # lit teal glint (filament catch-light, hairline)

BG        = ( 60,  74,  58)   # muted grove-green review backdrop
PANEL     = ( 46,  58,  46)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)
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
    pale-gold blessing glow at the coiled foot, never as a body fill."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


# ── a fresh madake CULM segment — HARD STEPPED bands (cloned for the PILLAR) ──
def culm_shaft(surf, cx, top, bot, half_w, s, node_pitch, body_col=CULM,
               shade_col=CULM_D, deep_col=CULM_DD):
    """A vertical living-bamboo shaft built as a stack of node-segments, each lit
    with 4 HARD STEPPED value bands across its width (no gradient). Node rings are
    the two-ring madake collar. Cloned verbatim from the parent so the straight
    PILLAR body-segment matches the brood exactly."""
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


# ── the DIAGONAL-CUT MOUTH — the signature (cloned; here it is the reared MAW) ─
def diagonal_cut(surf, cx, top, half_w, s, lean=0.62, dominance=1.0):
    """The steep sogi slant-cut culm-mouth: a bright OVAL of cut-CREAM ring-wall
    around a SMALL inner CAVITY, lit upper-left. Cloned verbatim from the parent.

    WHY it is the hero of this concept too: the reared serpent HEAD reads as a
    fresh-cut culm-end, the dark CAVITY = the open dragon MAW, and the CUT_HI
    sheen is the single BRIGHTEST value on the whole form — so at 32px the head
    collapses to one unmissable bright cream disc atop the winding coil. The same
    helper also seeds the small overlap cut-nubs (low `dominance`)."""
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


# ── a woven straw-rope COLLAR band (cloned) ──────────────────────────────────
def straw_collar(surf, cx, cy, half_w, h, s):
    """The woven rice-straw rope binding the base, cloned verbatim. Here it cinches
    the coiled tail-foot so the New-Year kit stays base-anchored, never top-heavy."""
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


# ── a pine NEEDLE-FAN (cloned) ───────────────────────────────────────────────
def pine_fan(surf, root, base_ang, spread, n, length, s, sign=1):
    """A fan of hard tapered pine needle-blades, cloned verbatim — base-mass + the
    pillar cap sprig."""
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


# ── a vermilion PLUM blossom (cloned) ────────────────────────────────────────
def plum_blossom(surf, cx, cy, r, s):
    """A five-petal red-plum blossom, cloned verbatim — the auspicious vermilion
    accent, base-anchored at the coiled foot only."""
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


# ── the serene bound FACE (cloned) ───────────────────────────────────────────
def bound_face(surf, cx, cy, r, s, lit=True):
    """The serene Toshigami face glowing where a binding crosses, cloned verbatim.
    Here it rides the coiled foot as the auspicious blessing-mark below the beast."""
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


# ── the fresh diagonal-CUT pillar gap-cap (cloned for the PILLAR) ─────────────
def cut_cap(surf, cx, cut_y, half_w, s):
    """The pillar's gap-edge cap: an explicit FRESH diagonal cut across the culm
    top, cloned verbatim. Here it stands in for the reared-head cut-MAW at the
    pillar's gap edge."""
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


# ══════════════════════════════════════════════════════════════════════════════
#  THE BEAST — a coiling culm-body swept along an S/Ω path, NODE-COLLARS as
#  belly-scales bent along the coil. This is the concept's own construction.
# ══════════════════════════════════════════════════════════════════════════════
def _coil_path(cx, head_y, tail_y, amp, n):
    """The serpent spine: a VERTICAL winding S that climbs the frame. Two generous
    sine lobes (NOT tight spaghetti) so at 32px the blackout reads as a clean
    winding S, never a blob. Returns a list of (x, y) centre-points head->tail.

    WHY a sine in y (vertical climb) with a gentle width taper: the body must be a
    continuous winding TUBE reading top-to-bottom — the dragon of prosperity
    climbing the gate — with the reared head at the very top."""
    pts = []
    for i in range(n + 1):
        t = i / n                       # 0 at head (top), 1 at tail (bottom)
        y = head_y + (tail_y - head_y) * t
        # 2 lobes over the run; amplitude eases out near head + tail so the ends
        # tuck in (reared head centred, tail coiling back to centre at the foot)
        env = math.sin(t * math.pi) ** 0.6
        x = cx + math.sin(t * math.pi * 2.0) * amp * env
        pts.append((x, y))
    return pts


def _band_color(t, body_col, shade_col):
    """4 HARD STEPPED value bands across the tube cross-section (no gradient),
    matching culm_shaft's lighting so the swept body still reads as a turned
    cylinder of fresh green. t in [-1,1] across the tube (left=sun, right=shade)."""
    hi_col = CULM_HI if body_col is CULM else lerp(body_col, CULM_HI, 0.45)
    if t < -0.46:
        return CULM_HOT if body_col is CULM else CULM_HI
    if t < -0.16:
        return hi_col
    if t < 0.42:
        return body_col
    return shade_col


def _serpent_body(surf, pts, half_w, s, body_col=CULM, shade_col=CULM_D,
                  deep_col=CULM_DD):
    """Sweep the culm-body along the coil path as a stack of short quad ribs, each
    lit with the 4 hard bands, then lay NODE-COLLAR rings ACROSS the tube at a
    steady pitch — the rings bend to follow the spine so they read as bamboo
    belly-SCALES, not a plain green tube. INK keyline + warm rim ride both flanks.

    WHY ribs+collars instead of one polygon: the node-collar rhythm is the gate
    (every coil-segment must show clear rings). Banding the cross-section keeps
    the cylinder read; the per-pitch collars keep the bamboo read; both survive
    the SS=6 downscale."""
    n = len(pts) - 1
    # perpendiculars + per-step half-width (taper head->tail a touch for a neck)
    norms, hws = [], []
    for i in range(len(pts)):
        a = pts[max(0, i - 1)]
        b = pts[min(n, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        norms.append((-dy / L, dx / L))
        t = i / n
        hws.append(half_w * (0.82 + 0.18 * math.sin(t * math.pi) + 0.12 * (1 - t)))

    # ink the full underlay so the keyline reads as one continuous tube
    left = [(pts[i][0] + norms[i][0] * (hws[i] + 1.6 * s),
             pts[i][1] + norms[i][1] * (hws[i] + 1.6 * s)) for i in range(len(pts))]
    right = [(pts[i][0] - norms[i][0] * (hws[i] + 1.6 * s),
              pts[i][1] - norms[i][1] * (hws[i] + 1.6 * s)) for i in range(len(pts))]
    pygame.draw.polygon(surf, INK, left + right[::-1])

    # 4 hard longitudinal bands: draw the tube 4 times, each band a narrow strip
    # of the cross-section swept the whole length (left=sun rail ... right=shade)
    band_edges = [(-1.00, -0.46, CULM_HOT if body_col is CULM else CULM_HI),
                  (-0.46, -0.16, CULM_HI if body_col is CULM else lerp(body_col, CULM_HI, 0.45)),
                  (-0.16,  0.42, body_col),
                  ( 0.42,  1.00, shade_col)]
    for u0, u1, col in band_edges:
        strip_l = [(pts[i][0] + norms[i][0] * hws[i] * u0,
                    pts[i][1] + norms[i][1] * hws[i] * u0) for i in range(len(pts))]
        strip_r = [(pts[i][0] + norms[i][0] * hws[i] * u1,
                    pts[i][1] + norms[i][1] * hws[i] * u1) for i in range(len(pts))]
        pygame.draw.polygon(surf, col, strip_l + strip_r[::-1])

    # NODE-COLLAR rings ACROSS the tube — bent to the spine (the belly-scales).
    # A hard CULM_DD groove + a pale swollen ring just "above" it (toward head),
    # repeated at a steady arc-length pitch so EVERY coil-segment shows rings.
    seg_len = []
    acc = 0.0
    for i in range(1, len(pts)):
        acc += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        seg_len.append(acc)
    total = seg_len[-1] if seg_len else 1.0
    pitch = 16.0 * s                      # collar spacing along the spine
    ring_col = CULM_HOT if body_col is CULM else CULM_HI
    groove_w = max(2, int(2.6 * s))
    bulge_w = max(2, int(2.2 * s))
    d = pitch
    while d < total - pitch * 0.4:
        # find the path index nearest arc-length d
        i = 1
        while i < len(seg_len) and seg_len[i] < d:
            i += 1
        i = min(i, len(pts) - 1)
        cxp, cyp = pts[i]
        nx, ny = norms[i]
        hw = hws[i]
        # the pale swollen ring (toward the head = toward lower index)
        bp = pts[max(0, i - 1)]
        tdx, tdy = (cxp - bp[0]), (cyp - bp[1])
        tl = math.hypot(tdx, tdy) or 1.0
        ox, oy = tdx / tl * bulge_w * 1.4, tdy / tl * bulge_w * 1.4
        pygame.draw.line(surf, ring_col,
                         (cxp + nx * hw - ox, cyp + ny * hw - oy),
                         (cxp - nx * hw - ox, cyp - ny * hw - oy), bulge_w)
        # the hard dark groove (the node ring proper)
        pygame.draw.line(surf, deep_col,
                         (cxp + nx * hw, cyp + ny * hw),
                         (cxp - nx * hw, cyp - ny * hw), groove_w)
        d += pitch

    # warm rim-keyline on both flanks (night-hold) + final ink keyline
    rim = max(1, int(1.2 * s))
    pygame.draw.lines(surf, CULM_RIM, False, left, rim)
    pygame.draw.lines(surf, CULM_RIM, False, right, rim)
    lw = max(2, int(1.5 * s))
    pygame.draw.lines(surf, INK, False, left, lw)
    pygame.draw.lines(surf, INK, False, right, lw)
    return norms, hws


def _whisker(surf, root, ang, length, s, curl=0.5):
    """A single THREAD-THIN jade-teal whisker filament — a gently curling hairline
    with a brighter catch-light core. Filament-only: 1-2px so it never reads as a
    fill and stays off the green body."""
    pts = []
    n = 10
    for k in range(n + 1):
        t = k / n
        a = ang + curl * t
        L = length * t
        pts.append((root[0] + math.cos(a) * L, root[1] + math.sin(a) * L))
    pygame.draw.lines(surf, INK, False, pts, max(2, int(1.8 * s)))
    pygame.draw.lines(surf, TEAL, False, pts, max(1, int(1.4 * s)))
    # a hairline catch-light along the first third
    pygame.draw.lines(surf, TEAL_HI, False, pts[:n // 3 + 1], max(1, int(s)))


def _dorsal_fin(surf, pts, norms, hws, s, head_frac=0.42):
    """A THIN jade-teal fin-fringe riding the OUTER (sun-side) flank of the upper
    body — a row of small hard teal spikes on a hairline ridge. Filament-only: the
    teal is the spike EDGES + ridge line, never a filled membrane, so the accent
    stays a cool electric glint and the body stays fresh-cut bamboo."""
    n = len(pts) - 1
    i0 = int(n * 0.06)
    i1 = int(n * head_frac)
    ridge = []
    spikes = []
    k = 0
    for i in range(i0, i1, 2):
        nx, ny = norms[i]
        hw = hws[i]
        base = (pts[i][0] + nx * hw, pts[i][1] + ny * hw)
        ridge.append(base)
        if k % 1 == 0:
            sl = (6.0 + 3.0 * math.sin(i * 0.5)) * s
            tip = (base[0] + nx * sl, base[1] + ny * sl - 1.5 * s)
            spikes.append((base, tip))
        k += 1
    # the spikes — thin teal triangles outlined in ink, hollow-ish (edge accent)
    for base, tip in spikes:
        nxt = (base[0] + 4 * s, base[1])
        pygame.draw.polygon(surf, INK,
                            [base, tip, nxt])
        pygame.draw.line(surf, TEAL, base, tip, max(1, int(1.6 * s)))
        pygame.draw.line(surf, TEAL, tip, nxt, max(1, int(1.4 * s)))
    if len(ridge) >= 2:
        pygame.draw.lines(surf, TEAL_HI, False, ridge, max(1, int(s)))


def draw_tatsu(surf, cx, cy, s):
    """The coiling grove-serpent: a culm-body winding up the frame as a vertical
    S, head reared at the top as the hero cream cut-disc MAW, node-collar rings
    riding every coil-segment as belly-scales; a thread-thin jade-teal dorsal-fin
    + whisker glint; a straw-cinched coiled tail-foot with plum + blessing-face at
    the base. `s` = unit scale around a ~150-unit figure (matches the parent).

    Built back-to-front: tail-foot kit -> overlap cut-nubs (back) -> the swept
    coiling body -> the dorsal fin -> the reared head maw -> whiskers -> the
    base kit drawn last so it sits in front of the lowest coil."""
    head_y = cy - int(96 * s)
    tail_y = cy + int(62 * s)
    amp = int(40 * s)
    half_w = int(15 * s)
    pts = _coil_path(cx, head_y, tail_y, amp, 48)

    # === 1-2 small overlap CUT-NUBS where the coils cross (seed cream rhythm) ===
    # WHY behind the body: a cut-end peeking from behind a forward loop reads as a
    # coil passing over itself, and salts the cream signature down the length so
    # the head isn't the only cream note. Placed at the lobe crossings.
    nub_a = pts[int(len(pts) * 0.30)]
    nub_b = pts[int(len(pts) * 0.66)]
    diagonal_cut(surf, int(nub_a[0] + 16 * s), int(nub_a[1]), int(7 * s), s,
                 lean=0.6, dominance=0.18)
    diagonal_cut(surf, int(nub_b[0] - 16 * s), int(nub_b[1]), int(6 * s), s,
                 lean=0.6, dominance=0.14)

    # === THE COILING CULM-BODY (the silhouette spine) ==========================
    norms, hws = _serpent_body(surf, pts, half_w, s)

    # === the THIN jade-teal DORSAL FIN riding the upper outer flank ============
    _dorsal_fin(surf, pts, norms, hws, s)

    # === THE REARED HEAD — the hero cream cut-disc MAW (brightest value) =======
    # The head is a short culm-end tipped up; the diagonal_cut cavity = the open
    # dragon maw. A small jaw-ledge below grounds it as a head, not just a stump.
    hx, hy = pts[0]
    hw_head = int(17 * s)
    # a short neck-stub of culm so the disc sits on a real culm end
    pygame.draw.polygon(surf, INK, [
        (hx - hw_head - int(2 * s), hy + int(20 * s)),
        (hx - hw_head, hy - int(2 * s)),
        (hx + hw_head, hy - int(2 * s)),
        (hx + hw_head + int(2 * s), hy + int(20 * s))])
    pygame.draw.polygon(surf, CULM, [
        (hx - hw_head, hy + int(20 * s)),
        (hx - hw_head, hy + int(2 * s)),
        (hx + hw_head, hy + int(2 * s)),
        (hx + hw_head, hy + int(20 * s))])
    # a couple of brow node-rings so the head still reads bamboo
    for ny in (hy + int(7 * s), hy + int(15 * s)):
        pygame.draw.rect(surf, CULM_DD, (hx - hw_head, ny, hw_head * 2, max(2, int(2.2 * s))))
        pygame.draw.rect(surf, CULM_HOT, (hx - hw_head, ny - max(1, int(2 * s)),
                                          hw_head * 2, max(1, int(1.6 * s))))
    # tiny vermilion eye-mark each side (kept minimal so head reads serene)
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK, (int(hx + sgn * 9 * s), int(hy + 9 * s)),
                           max(2, int(2.4 * s)))
        pygame.draw.circle(surf, PLUM, (int(hx + sgn * 9 * s), int(hy + 9 * s)),
                           max(1, int(1.6 * s)))
    # THE MAW — the dominant bright cream cut-disc (the hero, brightest value)
    diagonal_cut(surf, int(hx), int(hy), hw_head, s, lean=0.66, dominance=1.0)

    # === jade-teal WHISKERS sweeping back off the maw (thread-thin filaments) ===
    _whisker(surf, (hx - hw_head, hy + int(4 * s)), math.radians(168),
             34 * s, s, curl=0.9)
    _whisker(surf, (hx + hw_head, hy + int(4 * s)), math.radians(12),
             34 * s, s, curl=-0.9)
    _whisker(surf, (hx - hw_head + int(2 * s), hy + int(11 * s)), math.radians(176),
             24 * s, s, curl=0.7)
    _whisker(surf, (hx + hw_head - int(2 * s), hy + int(11 * s)), math.radians(4),
             24 * s, s, curl=-0.7)

    # === the coiled TAIL-FOOT kit — straw bind + plum + blessing-face (base) ===
    fx, fy = pts[-1]
    straw_collar(surf, int(fx), int(fy + 8 * s), int(24 * s), int(17 * s), s)
    bound_face(surf, int(fx), int(fy - int(4 * s)), int(9 * s), s, lit=True)
    plum_blossom(surf, int(fx - 26 * s), int(fy + 14 * s), int(7 * s), s)
    plum_blossom(surf, int(fx + 28 * s), int(fy + 16 * s), int(6 * s), s)
    plum_blossom(surf, int(fx + 6 * s), int(fy + 24 * s), int(5 * s), s)
    # a low pine sprig at the very foot so the base reads planted (never top-heavy)
    pine_fan(surf, (int(fx - 12 * s), int(fy + 18 * s)), math.radians(210),
             math.radians(56), 5, 26 * s, s, sign=-1)
    pine_fan(surf, (int(fx + 12 * s), int(fy + 18 * s)), math.radians(-30),
             math.radians(56), 5, 26 * s, s, sign=1)


# ── a straight body-segment → PILLAR mirror ──────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """A STRAIGHT body-segment of the serpent IS the pillar: node-collar rings =
    the tileable repeat band; the reared-head cut-MAW (cut_cap, with a teal whisker
    pair off the lip) = the gap-edge cap; the straw-bound coiled tail-foot with
    plum = the lower mirror. `cap` names the END that faces the GAP.

    WHY the body reads identical to the coil: the same culm_shaft node geometry
    runs the pillar, so the brood's body-is-bamboo gate holds when a straight
    length of the serpent tiles into a Skybit pillar."""
    half_w = int(13 * s)
    node = int(26 * s)
    cap_room = int(46 * s)
    base_room = int(40 * s)

    if cap == "bottom":
        shaft_top = top + base_room
        shaft_bot = bot - cap_room
        culm_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, node)
        cut_y = bot - int(22 * s)
        culm_shaft(surf, cx, shaft_bot, cut_y + int(2 * s), half_w, s, node)
        cut_cap(surf, cx, cut_y, half_w, s)
        # teal whisker pair off the maw lip (the held-apart accent on the pillar)
        _whisker(surf, (cx - half_w, cut_y - int(2 * s)), math.radians(150),
                 22 * s, s, curl=0.8)
        _whisker(surf, (cx + half_w, cut_y - int(2 * s)), math.radians(30),
                 22 * s, s, curl=-0.8)
        straw_collar(surf, cx, top + int(20 * s), int(18 * s), int(15 * s), s)
        _plum_cap(surf, cx, top + int(13 * s), half_w, s)
    else:
        shaft_top = top + cap_room
        shaft_bot = bot - base_room
        culm_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, node)
        cut_y = top + int(22 * s)
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        Hs = surf.get_height()
        culm_shaft(tmp, cx, Hs - (cut_y + int(2 * s)), Hs - shaft_top, half_w, s, node)
        cut_cap(tmp, cx, Hs - cut_y, half_w, s)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, 0))
        # whiskers off the (now upward-facing) maw, drawn after the flip
        _whisker(surf, (cx - half_w, cut_y + int(2 * s)), math.radians(210),
                 22 * s, s, curl=-0.8)
        _whisker(surf, (cx + half_w, cut_y + int(2 * s)), math.radians(-30),
                 22 * s, s, curl=0.8)
        straw_collar(surf, cx, bot - int(20 * s), int(18 * s), int(15 * s), s)
        _plum_cap(surf, cx, bot - int(13 * s), half_w, s)


def _plum_cap(surf, cx, cy, half_w, s):
    """The lower-mirror plum cap, value-anchored — cloned from the parent. A fat
    cream cut-ring disc behind a vermilion plum keeps the lower mirror reading as
    a distinct cap at the pillar chip on day AND night."""
    disc = pygame.Rect(cx - int(half_w * 1.3), cy - int(half_w * 0.9),
                       int(half_w * 2.6), int(half_w * 1.8))
    pygame.draw.ellipse(surf, INK, disc.inflate(int(2 * s), int(2 * s)))
    pygame.draw.ellipse(surf, CUT_CREAM, disc)
    pygame.draw.ellipse(surf, CUT_HI, disc.inflate(-int(half_w * 0.9), -int(half_w * 0.6)))
    plum_blossom(surf, cx - int(half_w * 0.45), cy, int(half_w * 0.62), s)
    plum_blossom(surf, cx + int(half_w * 0.55), cy + int(2 * s), int(half_w * 0.52), s)


# ── compose the review sheet (parent layout) ─────────────────────────────────
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
    sheet.blit(font_big.render("TATSU-NO-TAKEMURA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "the coiling grove-serpent  ·  set's ONE beast · VERTICAL COILING S-SERPENT · body IS a stacked culm "
        "(node-collars = belly-scales) · reared cream cut-disc MAW · jade-teal filament glint · round 1",
        True, LABEL_DIM), (330, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_tatsu(big, 178 * SS, 232 * SS, 1.5 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Body-is-bamboo — hero", True, LABEL), (96, 566))
    sheet.blit(font_sm.render("A culm-body winds up the frame as a vertical S (2 generous loops); node-collar rings ride", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("EVERY coil-segment as belly-scales. Reared HEAD = the hero bright CREAM cut-disc MAW", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("(cavity = open mouth, brightest value). Jade-teal whiskers + dorsal fin = thread-thin glint.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored straight body-segment ================
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
    sheet.blit(font.render("Pillar — body-segment", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("node-collars = repeat band; reared-head", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("cut-MAW + teal whisker = gap cap; coiled", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("tail-foot + plum-on-cream = lower mirror", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips + silhouette + palette ===========================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_tatsu(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
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
    sheet.blit(font_sm.render("32px on night sky — winding S +", True, LABEL_DIM), (panel_x + 20, night_y + 156))
    sheet.blit(font_sm.render("one bright cream MAW must hold", True, LABEL_DIM), (panel_x + 20, night_y + 170))

    # blacked-out 32px silhouette — the coil-read TEST: a winding S/coil tube
    # with ONE bright head, never tight spaghetti / a blob
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_tatsu(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        return mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))

    sil_y = night_y + 198
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 214, 200), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 24))
    sheet.blit(font_sm.render("a winding S/coil tube with ONE", True, LABEL_DIM), (sx + 104, sil_y + 42))
    sheet.blit(font_sm.render("bright head — never a blob", True, LABEL_DIM), (sx + 104, sil_y + 58))

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
        (CULM, "fresh-culm green"), (CULM_DD, "node-collar shadow"),
        (CUT_CREAM, "cut-ring cream"), (CUT_HI, "cut sheen (brightest)"),
        (TEAL, "jade-teal glint (accent)"), (PLUM, "vermilion plum"),
        (STRAW, "straw-rope"), (INK, "ink keyline"),
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
        "1px grown outline · radial glow ACCENT only.  R1: coiling culm-body · node-collar belly-scales · reared cream cut-MAW · teal filament glint.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
