"""
Round-1 concept renderer for NAGARAJA — the bone-cobra serpent-king
(Batch 2 / Citipati-versions set, concept #1). Headless Pygame; ELEVATED
pipeline (supersample SS=6 → smoothscale) so the coil banding + rib-splines
stay crisp at downscale. Keeps the shipped house grammar: flat saturated
fills, hard 1-2px ink keyline, dark-core → flat-fill → top-left rim-sheen
triad, 1px alpha-grown outline, chibi, scary-CUTE; procedural-only.

WHY this is the anti-Citipati / the brood's ONLY serpentine kind: every other
spin-off (and the source) is a limbed upright skeleton-figure. Nagaraja has NO
arms and NO legs — it is one long bone SPINE reared into an S-coil, crowned by
a hooded cobra-skull. That legless/armless coil is the protected silhouette
tell; nothing else in the roster can be confused for it at 32px.

WHY the hood is RIGID, not bushy: a soft tail-fan would read as the Kitsune
fan or Garuda quills. So the hood is exactly seven STRAIGHT rib-splines — hard
bone struts splayed in a flat shield behind the skull, ink-keyed and slim, with
a brass trim arc tying their tips. Count-able, architectural, unmistakably a
cobra hood and not a brush.

WHY the brow-gem is a single cabochon: a facet-field would shimmer into noise
at 1×. The gem is ONE domed emerald cabochon on the brow — a single focal lit
spot — so the head reads "crowned by a glowing jewel" even at thumbnail.

WHY the vertebra coil IS the pillar: the boss's own stacked spine discs (the
same banded vertebra unit as the body) tile as the repeatable shaft; a single
hooded gap-skull with the rib-splines splayed at the gap is the creature-derived
cap — bottom-rooted, mirrored top↔bottom, never top-heavy.

WHY standalone under docs/: review art never enters the shipped bundle, so this
re-implements the triad/outline helpers rather than importing runtime modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Cool-pearl bone is the LIGHTEST of the five spin-offs — emerald is the single
# saturated accent so the figure reads "pearl-and-jade," recognisably cool.
BONE      = (214, 222, 224)   # cool-pearl bone (the dominant fill)
BONE_D    = (162, 174, 182)   # bone dark-core
BONE_DD   = (118, 132, 142)   # deepest bone hollow (sockets, disc foramen)
BONE_SH   = (244, 250, 250)   # bone top-left rim-sheen
SLATE     = (150, 166, 176)   # slate-pearl shade (banding grooves, undersides)
EMERALD   = ( 72, 196, 142)   # emerald serpent-glow — the accent (gem, eyes)
EM_BR     = (146, 236, 196)   # hot emerald inner / cabochon hot-spot
EM_HOT    = (214, 252, 234)   # hottest gem core (lightest, the lit pin)
JADE      = ( 34, 118,  92)   # deep-jade — gem rim, glow underbase, deep grooves
BRASS     = (206, 170,  86)   # brass hood-rib trim (the rib-spline tips/arc)
BRASS_BR  = (236, 208, 132)
BRASS_D   = (158, 126,  56)
INK       = ( 26,  30,  32)   # hard ink keyline
SHEEN     = (244, 250, 250)   # sheen highlight

BG        = ( 94, 100, 104)   # neutral grey review backdrop
PANEL     = ( 72,  78,  84)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (188, 196, 208)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


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


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.4), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    """Round equivalent of triad_blob — dark core bottom-right, sheen top-left."""
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.45),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


# ── a single vertebra disc — the repeated coil unit (body + pillar shaft) ─────
def vertebra_disc(surf, cx, cy, rw, rh, s, ang=0.0, lit=False):
    """One stacked bone vertebra: an oval disc with a slate banding groove and a
    dark central foramen. WHY an oval, not a hexagon (anti-Citipati bead): the
    serpent reads as a smooth tubular SPINE of stacked rings, not an architectural
    column — the disc banding is the coil texture. `ang` tilts the disc so the
    coil can bend; `lit` pops the foramen emerald on the body's lit segments."""
    pts = []
    for i in range(14):
        a = (i / 14) * 2 * math.pi
        px = math.cos(a) * rw
        py = math.sin(a) * rh
        # rotate the disc to follow the coil tangent
        rx = px * math.cos(ang) - py * math.sin(ang)
        ry = px * math.sin(ang) + py * math.cos(ang)
        pts.append((cx + rx, cy + ry))
    # top-left sheen wedge of the disc
    sheen = [pts[8], pts[9], pts[10], pts[11],
             (cx + (pts[10][0]-cx)*0.4, cy + (pts[10][1]-cy)*0.4)]
    triad_blob(surf, BONE, pts, sheen_pts=sheen, ow=max(1, int(1.4 * s)))
    # slate banding groove ring just inside the rim (the stacked-disc read)
    gpts = []
    for i in range(14):
        a = (i / 14) * 2 * math.pi
        px = math.cos(a) * rw * 0.66
        py = math.sin(a) * rh * 0.66
        rx = px * math.cos(ang) - py * math.sin(ang)
        ry = px * math.sin(ang) + py * math.cos(ang)
        gpts.append((cx + rx, cy + ry))
    pygame.draw.polygon(surf, SLATE, gpts, max(1, int(1.6 * s)))
    # central foramen hollow — emerald-lit on lit segments
    fr = int(min(rw, rh) * 0.30)
    pygame.draw.circle(surf, BONE_DD, (int(cx), int(cy)), fr)
    if lit:
        pygame.draw.circle(surf, JADE, (int(cx), int(cy)), max(1, int(fr * 0.72)))
        pygame.draw.circle(surf, EMERALD, (int(cx), int(cy)), max(1, int(fr * 0.46)))
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), fr, max(1, int(1 * s)))


# ── the rigid 7-spline cobra HOOD (the hard top tell — NOT a bushy fan) ────────
def cobra_hood(surf, cx, cy, span, height, s):
    """A FRONT-FLARED cobra hood: a single wide bone shield (wider than tall) that
    flares out and UP behind the skull, ribbed by exactly SEVEN straight bone
    rib-splines fanning from the neck root, each brass-tipped, with a brass trim
    arc tying the tips. WHY rigid + count-able + front-flared: the classic cobra
    read is the spread hood seen head-on; a soft or overlapping fan would read as
    Kitsune's tail-fan or Garuda's quills, so the splines are hard straight struts
    with ink gaps you can count to seven. `cy` is the SKULL centre — the hood root
    sits just below it so the skull sits IN FRONT of the hood. Drawn BEHIND skull."""
    n = 7
    root = (cx, cy + int(height * 0.46))      # the neck point all splines spring from
    # the outer hood shield outline: a wide flared cobra-hood lobe
    shield = [(root[0] - int(span * 0.30), root[1]),
              (cx - span,               cy + int(height * 0.10)),
              (cx - int(span * 0.86),   cy - int(height * 0.74)),
              (cx - int(span * 0.34),   cy - int(height * 1.05)),
              (cx,                      cy - int(height * 1.12)),
              (cx + int(span * 0.34),   cy - int(height * 1.05)),
              (cx + int(span * 0.86),   cy - int(height * 0.74)),
              (cx + span,               cy + int(height * 0.10)),
              (root[0] + int(span * 0.30), root[1])]
    triad_blob(surf, BONE, shield,
               core_pts=[(cx - int(span*0.5), cy + int(height*0.06)),
                         (cx + int(span*0.5), cy + int(height*0.06)),
                         (cx + int(span*0.5), cy - int(height*0.7)),
                         (cx - int(span*0.5), cy - int(height*0.7))],
               sheen_pts=[(cx - int(span*0.84), cy - int(height*0.70)),
                          (cx - int(span*0.30), cy - int(height*1.0)),
                          (cx - int(span*0.20), cy - int(height*0.40)),
                          (cx - int(span*0.74), cy - int(height*0.10))],
               ow=max(2, int(2 * s)))
    # the seven rib-spline tips ride the upper hood arc — collect for the trim arc
    tip = []
    for i in range(n):
        t = i / (n - 1)
        ang = math.radians(-168 + t * 156)    # fan across the wide upper arc
        tx = cx + math.cos(ang) * span * 0.92
        ty = cy + int(height * 0.04) + math.sin(ang) * height * 1.04
        tip.append((tx, ty))
    # seven RIGID rib-splines drawn as a WIDE ink groove with a slate valley and a
    # thinner bone crest on top — so the inter-spline grooves are deep enough that
    # 3-4 rib divisions survive the 32px downscale (the hood must read RIBBED, not
    # a smooth platter that could drift to a Catrina brim or Mukha-Devi fan).
    for (tx, ty) in tip:
        pygame.draw.line(surf, INK, root, (tx, ty), max(3, int(4.4 * s)))
    for (tx, ty) in tip:
        pygame.draw.line(surf, SLATE, root, (tx, ty), max(2, int(2.6 * s)))
        # a slim cool-pearl crest rides each rib so the divisions read as raised
        # struts against the deep ink grooves, not painted lines on a flat shield
        pygame.draw.line(surf, BONE_SH, root, (tx, ty), max(1, int(1.0 * s)))
    # brass bead caps at each rib tip + a thin brass trim arc tying them
    pygame.draw.lines(surf, BRASS, False, tip, max(2, int(2.4 * s)))
    pygame.draw.lines(surf, BRASS_BR, False, tip[:4], max(1, int(1.2 * s)))
    for (tx, ty) in tip:
        triad_circle(surf, BRASS, (int(tx), int(ty)), max(2, int(span * 0.060)),
                     ow=max(1, int(1 * s)), core=False)


# ── the cobra SKULL head — front-on, chibi, scary-cute, single brow-gem ───────
def cobra_skull(surf, cx, cy, r, s, lit=True):
    """A front-facing hooded serpent skull: a rounded cranium narrowing to a short
    blunt snout below, two big round emerald scary-cute eyes, a single domed
    brow-gem cabochon crowning it, and two tiny down-fangs. WHY front-on: the
    head-on hooded cobra is the most iconic + most legible serpent read at 32px,
    and it keeps the brow-gem dead-centre as the crown focal. The brow-gem is ONE
    cabochon — not a facet-field."""
    # cranium: a rounded shield narrowing to a snout (taller than wide, snout down)
    skull = [(cx - int(r*0.82), cy - int(r*0.30)),
             (cx - int(r*0.70), cy - int(r*0.92)),
             (cx,               cy - int(r*1.04)),
             (cx + int(r*0.70), cy - int(r*0.92)),
             (cx + int(r*0.82), cy - int(r*0.30)),
             (cx + int(r*0.56), cy + int(r*0.52)),    # cheek down to snout
             (cx + int(r*0.24), cy + int(r*0.96)),    # snout tip (blunt)
             (cx - int(r*0.24), cy + int(r*0.96)),
             (cx - int(r*0.56), cy + int(r*0.52))]
    triad_blob(surf, BONE, skull,
               core_pts=[(cx + int(r*0.10), cy - int(r*0.30)),
                         (cx + int(r*0.80), cy - int(r*0.28)),
                         (cx + int(r*0.52), cy + int(r*0.50)),
                         (cx + int(r*0.20), cy + int(r*0.90))],
               sheen_pts=[(cx - int(r*0.66), cy - int(r*0.86)),
                          (cx - int(r*0.04), cy - int(r*0.98)),
                          (cx - int(r*0.10), cy - int(r*0.20)),
                          (cx - int(r*0.74), cy - int(r*0.24))],
               ow=max(2, int(2 * s)))
    # two big almond eye-sockets — FLAT DEEP-JADE, matte, NO glow halo, NO emerald,
    # NO hot pin. WHY desaturated jade not glowing emerald: at 32px three equal
    # emerald glows (two eyes + brow gem) bloom into a single green smear and the
    # crown jewel stops being the one focal. Matte jade drops the eyes out of the
    # glow tier so the brow cabochon alone blooms — a CROWNED king, not a bug. The
    # sockets stay clearly almond-shaped so the FACE reads on SHAPE at 32px, never
    # depending on the glow (jade keeps the socket structure visible vs. pure ink).
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.42)
        ey = cy + int(r * 0.04)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(r * 0.34))
        pygame.draw.circle(surf, INK, (ex, ey), int(r * 0.28))
        pygame.draw.circle(surf, JADE, (ex, ey), int(r * 0.22))
        # a single recessed darker-jade core gives the socket depth without a glow
        pygame.draw.circle(surf, lerp(JADE, INK, 0.45), (ex, ey), int(r * 0.13))
        # vertical reptilian slit pupil keeps the cute-menace read at hero scale
        pygame.draw.line(surf, INK, (ex, ey - int(r*0.14)), (ex, ey + int(r*0.14)),
                         max(1, int(1.6 * s)))
    # nostril ticks on the snout
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_DD,
                           (cx + sgn * int(r*0.13), cy + int(r*0.52)),
                           max(1, int(r * 0.07)))
    # hissing mouth line + two tiny down-fangs (scary-CUTE small)
    my = cy + int(r * 0.74)
    pygame.draw.line(surf, INK, (cx - int(r*0.22), my), (cx + int(r*0.22), my),
                     max(1, int(1.6 * s)))
    # tiny down-fangs — a hero-scale charm beat only; kept slim + INSIDE the snout
    # silhouette so they never blob the jaw read at 32px (they contribute nothing
    # at gameplay scale and must not cost jaw/hood clarity per the critique).
    for sgn in (-1, 1):
        fx = cx + sgn * int(r * 0.12)
        fang = [(fx - int(r*0.05), my), (fx + int(r*0.05), my),
                (fx, my + int(r*0.24))]
        pygame.draw.polygon(surf, INK, fang)
        pygame.draw.polygon(surf, SHEEN, [(fang[0][0]+1, fang[0][1]+1),
                                          (fang[1][0]-1, fang[1][1]+1),
                                          (fang[2][0], fang[2][1]-int(r*0.07))])
    # === the single BROW-GEM CABOCHON (the crown-jewel focal) ================
    # WHY one domed cabochon in a BRASS bezel, lifted to the crown: a facet-field
    # shimmers into noise at 1×, and a bare emerald dome sitting between the eyes
    # reads as a third eye. The brass setting ring + the higher crown position
    # (riding the cranium/hood join) make it read as a SET crown jewel, distinct
    # from the two eye-gems below it. One emerald dome, jade rim, hot inner, sheen
    # pip — survives the 32px downscale as the brightest single focal.
    gx, gy = cx, cy - int(r * 0.86)
    gr = int(r * 0.34)
    # the brow cabochon is now the ONLY emerald glow in the figure (eyes are matte
    # jade) — push its halo a touch harder so it is unambiguously the single bloom
    # that survives the 32px downscale as the one bright focal point.
    if lit:
        halo = pygame.Surface((gr*8, gr*8), pygame.SRCALPHA)
        pygame.draw.circle(halo, JADE + (110,), (gr*4, gr*4), int(gr*2.6))
        pygame.draw.circle(halo, EMERALD + (110,), (gr*4, gr*4), int(gr*1.6))
        pygame.draw.circle(halo, EM_BR + (90,), (gr*4, gr*4), int(gr*0.9))
        surf.blit(halo, (gx - gr*4, gy - gr*4), special_flags=pygame.BLEND_RGBA_ADD)
    # brass bezel setting (the "crown" mount that separates it from the eyes)
    triad_circle(surf, BRASS, (gx, gy), int(gr * 1.32), ow=max(1, int(1.4 * s)),
                 core=False)
    pygame.draw.circle(surf, INK, (gx, gy), gr + max(1, int(1 * s)))
    pygame.draw.circle(surf, JADE, (gx, gy), gr)
    pygame.draw.circle(surf, EMERALD, (gx, gy), int(gr * 0.78))
    pygame.draw.circle(surf, EM_BR, (gx, gy), int(gr * 0.46))
    pygame.draw.circle(surf, EM_HOT, (gx - int(gr*0.26), gy - int(gr*0.30)),
                       max(1, int(gr * 0.26)))


# ── the reared bone-cobra (hero) ──────────────────────────────────────────────
def draw_nagaraja(surf, cx, cy, s):
    """A reared cobra of ONE long bone spine, S-coiled, hood splayed, head hissing
    at the top. No arms, no legs — the only serpentine silhouette. `s` = unit
    scale around a ~130-unit-tall figure."""

    # === the coiled SPINE path — bottom-rooted base loop rising to a reared neck =
    # WHY a base coil + an S-neck: the bottom loop roots the mass low (anti
    # top-heavy) and gives the unmistakable serpent-coil read; the neck rears
    # straight UP out of the coil so the hood + head crown the silhouette head-on.
    head_y = cy - int(50 * s)
    head_x = cx
    hr = int(20 * s)

    base_cx = cx - int(4 * s)
    base_cy = cy + int(48 * s)
    coil_r = int(30 * s)

    # build an ordered list of (x, y) spine samples from tail-tip → neck-base
    spine = []
    # 1) the grounded base coil — almost a full loop, bottom-rooted
    for i in range(22):
        t = i / 21.0
        a = math.radians(40 + t * 300)        # sweep most of a circle
        rr = coil_r * (0.55 + 0.45 * t)        # spiral opening outward
        sx = base_cx + math.cos(a) * rr
        sy = base_cy + math.sin(a) * rr * 0.78  # squash so it sits as a coil
        spine.append((sx, sy))
    # 2) the reared NECK — a gentle S rising from the coil top to the hood root
    neck0 = spine[-1]
    neck_pts = [neck0,
                (cx - int(16 * s), cy + int(12 * s)),
                (cx + int(8 * s), cy - int(14 * s)),
                (head_x, head_y + int(16 * s))]   # land INSIDE the hood root (no gap)
    for i in range(1, 17):
        t = i / 16.0
        x = ((1-t)**3*neck_pts[0][0] + 3*(1-t)**2*t*neck_pts[1][0]
             + 3*(1-t)*t**2*neck_pts[2][0] + t**3*neck_pts[3][0])
        y = ((1-t)**3*neck_pts[0][1] + 3*(1-t)**2*t*neck_pts[1][1]
             + 3*(1-t)*t**2*neck_pts[2][1] + t**3*neck_pts[3][1])
        spine.append((x, y))

    # draw discs along the spine — taper from fat coil → slim neck. The discs are
    # stacked so close they read as one tubular banded serpent body.
    nseg = len(spine)
    for i, (sx, sy) in enumerate(spine):
        t = i / (nseg - 1)
        j = min(i + 1, nseg - 1)
        k = max(i - 1, 0)
        ang = math.atan2(spine[j][1] - spine[k][1], spine[j][0] - spine[k][0])
        body = (14.0 - 7.0 * t) * s            # widest in the lower coil
        rw = body * 0.66
        rh = body
        lit = (i % 3 == 0) and t > 0.25
        vertebra_disc(surf, sx, sy, rw, rh, s, ang=ang + math.pi/2, lit=lit)

    # === HOOD (behind/around skull) then SKULL on top, both at the neck top ====
    cobra_hood(surf, head_x, head_y, span=int(42 * s), height=int(30 * s), s=s)
    cobra_skull(surf, head_x, head_y, hr, s, lit=True)


# ── the vertebra-coil column → pillar mirror ──────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The vertebral coil IS the pillar: a stacked column of vertebra discs (the
    same body unit) = the tileable shaft; a single hooded cobra-skull with the
    7-spline hood splayed at the gap = the creature-derived cap. Bottom-rooted,
    on-axis, mirrored top↔bottom, never top-heavy. `cap` names the gap-facing end."""
    # the shaft: a tight stack of vertebra discs reading as a banded bone spine.
    disc_pitch = int(15 * s)
    cap_room = int(56 * s)        # widened cap hood needs more clearance from the shaft
    if cap == "bottom":
        d0, d1 = top + int(8 * s), bot - cap_room
    else:
        d0, d1 = top + cap_room, bot - int(8 * s)
    y = d0
    idx = 0
    while y <= d1:
        rw = int(15 * s)
        rh = int(10 * s)
        lit = (idx % 3 == 1)
        vertebra_disc(surf, cx, y, rw, rh, s, ang=0.0, lit=lit)
        y += disc_pitch
        idx += 1

    # === gap-edge cap: hooded skull + splayed 7-spline hood ===================
    # WHY a BIG cap hood: the cap must MIRROR the hero's hood mass, not read as a
    # tiny knob on a bead-string. The shaft disc full-width is ~30*s, so the cap
    # hood spans wider than the shaft (+~40%) and the cap skull is enlarged to sit
    # in front of it — the gap edge clearly echoes the reared cobra's broad hood.
    cap_y = (bot - int(34 * s)) if cap == "bottom" else (top + int(34 * s))
    cap_hr = int(17 * s)
    cap_span = int(44 * s)        # > shaft full-width (~30*s), mirrors hero hood mass
    cap_height = int(30 * s)
    # mirror the whole cap vertically when it faces UP (cap == "top")
    flip = (cap == "top")
    if flip:
        sub = pygame.Surface((int(150 * s), int(120 * s)), pygame.SRCALPHA)
        scx, scy = int(75 * s), int(82 * s)
        cobra_hood(sub, scx, scy, span=cap_span, height=cap_height, s=s)
        cobra_skull(sub, scx, scy, cap_hr, s, lit=True)
        sub = pygame.transform.flip(sub, False, True)
        surf.blit(sub, (cx - scx, cap_y - (int(120 * s) - scy)))
    else:
        cobra_hood(surf, cx, cap_y, span=cap_span, height=cap_height, s=s)
        cobra_skull(surf, cx, cap_y, cap_hr, s, lit=True)


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def main():
    W, H = 1010, 820
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("NAGARAJA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "bone-cobra serpent-king  ·  KIND: serpent-coil  ·  the ONLY legless/armless coil  ·  round 2",
        True, LABEL_DIM), (240, 26))

    # === (a) BIG HERO =========================================================
    def hero_chip(boxw, boxh, dcx, dcy, scale):
        big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
        draw_nagaraja(big, dcx * SS, dcy * SS, scale * SS)
        small = pygame.transform.smoothscale(big, (boxw, boxh))
        return grow_outline(small, INK + (255,), 1)

    hero = hero_chip(360, 470, 178, 232, 1.85)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("ONE long bone SPINE reared into an S-coil — no arms, no legs (the only", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("serpentine silhouette). Bottom-rooted base loop; reared hissing neck.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("7 RIGID rib-splines (deep ink grooves); SINGLE emerald brow-gem = the only glow;", True, LABEL_DIM), (14, 622))
    sheet.blit(font_sm.render("matte deep-jade eye-sockets (no halo) so the crown cabochon is the sole focal.", True, LABEL_DIM), (14, 638))

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
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — vertebral coil", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked vertebra discs = tileable shaft;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("hooded skull + 7-spline hood caps each gap edge", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top↔bottom, on-axis, bottom-rooted)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    # render the hero at a genuine 32px-tall figure
    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_nagaraja(big, 46 * SS, 48 * SS, (32 / 130.0) * SS)
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

    # a 32px pillar gap-cap chip beside, on both skies
    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.30 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 192
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (BONE, "cool-pearl bone"), (SLATE, "slate-pearl sh"),
        (EMERALD, "emerald glow"), (JADE, "deep-jade"),
        (BRASS, "brass hood-trim"), (BONE_DD, "bone hollow"),
        (SHEEN, "sheen"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    # bottom note strip
    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample → smoothscale.  STAY: flat triad fills · hard ink keyline (26,30,32) · "
        "dark-core→fill→top-left sheen · 1px grown outline · chibi · scary-cute · pearl-and-jade · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
