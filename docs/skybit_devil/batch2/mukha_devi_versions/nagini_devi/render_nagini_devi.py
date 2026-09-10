"""
Round-1 concept renderer for NAGINI-DEVI — the serpent-hood-ring bone-naga-queen
(Mukha-Devi brood, concept #2). Headless Pygame; ELEVATED pipeline (supersample
SS=5-6 -> smoothscale) so the ring of reared hood-lobes + tiny in-jaw skulls stay
crisp at downscale. Keeps the shipped house grammar: flat saturated fills, hard
1-2px ink keyline (28,22,26), dark-core -> flat-fill -> top-left rim-sheen triad,
1px alpha-grown outline, chibi/scary-CUTE; procedural-only.

WHY this is the arms-as-snakes hood-RING KIND (the deliberate ANTITHESIS of
Mukha-Devi's straight radial spokes): six arms do NOT splay as clean rays — each
ends in a FAT reared cobra-HOOD, and the six hoods crowd around the skull as a
LUMPY LATERAL RING of bulbous blobs. The blackout read is a head ringed by
S-curved hood-lobes with clear negative gaps between them, never a starburst.
The DNA of the brood survives intact: six arms + a skull-crown tiara + arm-end
ornaments carrying TINY SKULLS (here the skulls sit in alternating hood-jaws).

WHY duller, greener-bronze, NOT teal-grown-up: the cross-set pin demands this
split from Nagaraja's bright emerald (72,196,142) AND from Mukha-Devi's clean
teal (64,170,166). So the verdigris-teal is desaturated and the AGED-BRONZE is
the DOMINANT mass — it must read as a tarnished bronze naga-queen, not "Mukha's
teal grown up." Teal is the cool patina shading; bronze owns the silhouette.

WHY the caduceus twin-snake staff IS the pillar: two bone-snakes wind up a
central bronze rod and rear into facing hoods at the cap — the creature's own
serpent language, bottom-rooted, tiling as the repeatable shaft.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Aged-bronze is the DOMINANT mass; verdigris-teal is the cool patina shading.
# Both are deliberately DULLER + GREENER-BRONZE than the siblings so this reads
# as a tarnished naga-queen, not Nagaraja emerald and not Mukha teal.
BONE      = (220, 206, 184)   # warm bone-core (skull, snake bellies)
BONE_D    = (158, 142, 116)   # bone dark-core / shade
BONE_DD   = (104,  90,  70)   # deepest bone hollow (sockets, jaw gaps)
BONE_SH   = (244, 236, 218)   # bone top-left rim-sheen
BRONZE    = (150, 110,  62)   # aged-bronze — the DOMINANT accent mass
BRONZE_BR = (196, 152,  92)   # bronze top-left sheen
BRONZE_D  = ( 90,  62,  34)   # deep-bronze shade / core (deepened for day-chip value)
# WHY duller + GREENER verdigris (chroma −25-30% vs r1): r1's teal read as a
# clean cyan jewel — "Mukha's teal grown up." Pushed toward oxidized-copper
# green-grey so it reads as TARNISH, not a gem. Used ONLY as the third-eye
# brightest pixel + thin oxide rims; bronze owns the mass.
TEAL      = ( 84, 138, 112)   # verdigris — oxidized-copper green-grey (dulled)
TEAL_BR   = (122, 170, 146)   # verdigris faint sheen
TEAL_D    = ( 48,  84,  70)   # deep verdigris oxide shade
EYE       = ( 92, 178, 142)   # serpent-eye glow — greener, less cyan than r1
EYE_BR    = (164, 224, 188)   # hot eye core (still the brightest pixel)
INK       = ( 28,  22,  26)   # hard ink keyline

BG        = ( 92,  96,  88)   # neutral green-grey review backdrop
PANEL     = ( 70,  76,  68)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 240, 234)
LABEL_DIM = (196, 200, 188)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


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


def thick_path(surf, color, pts, w, ow):
    """A fat tapering-free polyline rendered as a filled ribbon with ink keyline
    — used for the S-curved snake arms so each arm is a single chunky bone limb,
    not a thin line that smears at 32px."""
    if len(pts) < 2:
        return
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == len(pts) - 1:
            dx, dy = x - pts[-2][0], y - pts[-2][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * w / 2, dx / L * w / 2
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    poly = left + right[::-1]
    pygame.draw.polygon(surf, INK, poly)
    pygame.draw.polygon(surf, color, poly)
    # a thin top-left belly sheen along the leading edge (the inner half-ribbon)
    inner = [(0.62 * lp[0] + 0.38 * pts[k][0], 0.62 * lp[1] + 0.38 * pts[k][1])
             for k, lp in enumerate(left)]
    pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.3), left + inner[::-1])
    pygame.draw.polygon(surf, INK, poly, ow)


# ── ONE reared cobra-hood LOBE (the arm-end — replaces Mukha's hands) ─────────
def cobra_hood(surf, cx, cy, r, s, ang, with_skull, lit=False):
    """A FAT reared cobra-HOOD: a bulbous spade/teardrop hood-lobe — narrow at
    the neck, ballooning to a wide rounded crown — with an open snake-jaw at its
    tip and (on alternating lobes) a TINY SKULL clenched in the jaw. WHY a fat
    spade and not a flat shield: the silhouette tell is a RING OF DISCRETE
    BULBOUS LOBES, so each hood must blackout as one chunky teardrop with a clear
    air-gap to its neighbour — the antithesis of a flat relic-plaque or a spoke.
    `(cx,cy)` is the lobe CENTRE; `ang` points from neck → crown (outward from
    the skull). The brood's arm-end-ornament-with-tiny-skull DNA lives here."""
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca   # perpendicular = the lateral hood-flare axis

    def P(along, across):
        return (cx + ca * r * along + px * r * across,
                cy + sa * r * along + py * r * across)

    # SPADE/TEARDROP outline: pinched neck at the base, fat rounded crown at tip.
    # Sampled so the widest belly sits ~0.55 of the way out = the bulbous read.
    spade = [
        P(-0.95,  0.18), P(-0.55,  0.62), P(-0.05,  0.96),
        P( 0.55,  1.02), P( 1.02,  0.78), P( 1.30,  0.30),
        P( 1.36,  0.00),                                   # crown apex
        P( 1.30, -0.30), P( 1.02, -0.78), P( 0.55, -1.02),
        P(-0.05, -0.96), P(-0.55, -0.62), P(-0.95, -0.18),
    ]
    triad_blob(surf, BRONZE, spade,
               core_pts=[P(0.55, 0.20), P(1.05, 0.40), P(1.15, -0.10),
                         P(0.65, -0.30), P(0.20, 0.05)],
               sheen_pts=[P(0.10, -0.55), P(0.55, -0.78), P(0.78, -0.50),
                          P(0.30, -0.30)],
               ow=max(2, int(2.0 * s)))
    # thin verdigris OXIDE RIM hugging the crown edge (tarnish, not a mass)
    rim = [P(0.55, 0.96), P(1.0, 0.74), P(1.28, 0.28), P(1.34, 0.0),
           P(1.28, -0.28), P(1.0, -0.74), P(0.55, -0.96)]
    pygame.draw.lines(surf, TEAL_D, False,
                      [(int(x), int(y)) for x, y in rim], max(1, int(2.2 * s)))
    pygame.draw.lines(surf, TEAL, False,
                      [(int(x), int(y)) for x, y in rim[1:-1]], max(1, int(1.4 * s)))

    # a bronze hood-spine ridge running neck → crown (reads as the reared neck)
    pygame.draw.line(surf, BRONZE_D, (int(P(-0.6, 0)[0]), int(P(-0.6, 0)[1])),
                     (int(P(0.9, 0)[0]), int(P(0.9, 0)[1])), max(1, int(2.4 * s)))
    pygame.draw.line(surf, BRONZE_BR, (int(P(-0.4, -0.06)[0]), int(P(-0.4, -0.06)[1])),
                     (int(P(0.6, -0.06)[0]), int(P(0.6, -0.06)[1])), max(1, int(1.4 * s)))

    # OPEN SNAKE-JAW at the crown: a dark wedge mouth (the focal of each lobe)
    jaw = [P(1.10, 0.30), P(1.40, 0.06), P(1.10, -0.30)]
    pygame.draw.polygon(surf, BONE_DD, [(int(x), int(y)) for x, y in jaw])
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in jaw], max(1, int(1.4 * s)))

    if with_skull:
        # a TINY SKULL clenched in the open jaw (alternating lobes) — the brood's
        # arm-end-skull DNA, now punctuating the RING rhythmically.
        sk = P(1.16, 0.0)
        skr = int(r * 0.30)
        triad_circle(surf, BONE_SH, (int(sk[0]), int(sk[1])), skr,
                     ow=max(1, int(1.2 * s)), core=False, sheen=False)
        for off in (-0.40, 0.40):
            pygame.draw.circle(surf, INK,
                               (int(sk[0] + px * skr * off), int(sk[1] + py * skr * off)),
                               max(1, int(skr * 0.34)))
        pygame.draw.line(surf, INK,
                         (int(sk[0] - px * skr * 0.4 + ca * skr * 0.5),
                          int(sk[1] - py * skr * 0.4 + sa * skr * 0.5)),
                         (int(sk[0] + px * skr * 0.4 + ca * skr * 0.5),
                          int(sk[1] + py * skr * 0.4 + sa * skr * 0.5)), max(1, int(1 * s)))
    else:
        # twin serpent-fangs framing the open jaw when no skull rides it
        for off in (-0.30, 0.30):
            fa = P(1.18, off)
            fb = P(1.42, off * 0.5)
            pygame.draw.line(surf, BONE_SH, (int(fa[0]), int(fa[1])),
                             (int(fb[0]), int(fb[1])), max(1, int(1.4 * s)))
        # a faint verdigris glint deep in the throat
        gt = P(1.18, 0.0)
        ec = EYE_BR if lit else EYE
        pygame.draw.circle(surf, ec, (int(gt[0]), int(gt[1])), max(1, int(r * 0.12)))


# ── a single ornamental tiara-skull (the preserved skull-crown DNA) ───────────
def tiara_skull(surf, cx, cy, r, s, lit=False):
    """Tiny bone skull for the skull-crown tiara — the brood's preserved
    skull-crown DNA. A domed cranium + jaw with two dark sockets; centre skull
    lit verdigris so the crown carries a cool focal note distinct from siblings."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.94)),
           (cx - int(r * 0.32), cy + int(r * 0.94))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.1 * s)))
    eye_c = EYE_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.14)))


# ── the six-arm SERPENT hood-ring (the KIND tell) ─────────────────────────────
def draw_hood_ring(surf, head_cx, head_cy, s, hr, hood_r):
    """Six bone-snake necks rear out of a low collar and ARCH UP AND AROUND the
    skull, each terminating in a fat cobra-hood LOBE, so the six hoods HALO the
    head as a flower of bulbous petals. WHY a true ring (not a low cluster): the
    silhouette tell is a SKULL HALOED BY 6 LOBES, so the lobe-centres are placed
    on an arc that sweeps the upper hemisphere — 3 per side at top-lateral and
    mid-lateral stations — and every adjacent pair is spaced to leave ~1
    hood-width of AIR between them. Each neck is a short S-curve from the collar
    to its lobe; the lobe rears RADIALLY OUTWARD from head-centre. Returns the
    six (lobe-centre, outward-angle, carries-jaw-skull) for the over-draw pass."""
    # lobe-centre stations on a radius that arches the lobes up & around the head.
    # Measured CCW-from-screen-up so they sweep the UPPER hemisphere (mass goes
    # UP into the ring, NOT down onto a lap). Symmetric L/R, gaps between each.
    #   top-lateral (near the crown), upper-side, mid-lateral (cheek height)
    ring_deg = [-118, -64, -22, 22, 64, 118]   # 0deg = up; +/- = right/left lean
    radius = hr + hood_r * 0.95               # lobe-centre offset from head centre
    collar = (head_cx, head_cy + int(hr * 0.78))   # necks spring from a low collar
    arm_th = int(8.5 * s)
    hoods = []
    for k, d in enumerate(ring_deg):
        a = math.radians(d)
        sgn = 1 if d > 0 else -1
        # direction from head-centre out to the lobe (screen coords: up = -y)
        ux, uy = math.sin(a), -math.cos(a)
        lobe_c = (head_cx + ux * radius, head_cy + uy * radius)
        # outward orientation of the lobe: neck → crown points away from head
        out_ang = math.atan2(uy, ux)
        # short S-curve neck: collar → bowed mid → lobe base (just inside lobe_c)
        base = (lobe_c[0] - ux * hood_r * 0.5, lobe_c[1] - uy * hood_r * 0.5)
        mid = ((collar[0] + base[0]) * 0.5 + sgn * hr * 0.30,
               (collar[1] + base[1]) * 0.5 + hr * 0.10)
        thick_path(surf, BONE, [collar, mid, base], arm_th, max(1, int(arm_th * 0.18)))
        # bone scale-segment dots along the neck (cute serpent texture)
        for t in (0.45, 0.75):
            sx = collar[0] + (base[0] - collar[0]) * t
            sy = collar[1] + (base[1] - collar[1]) * t
            pygame.draw.circle(surf, BONE_DD, (int(sx), int(sy)), max(1, int(arm_th * 0.20)))
        # alternate which lobes clench a jaw-skull → 3 of 6 (k even)
        hoods.append((lobe_c, out_ang, k % 2 == 0))
    # a small bronze collar-boss where the six necks converge (roots the ring)
    triad_circle(surf, BRONZE, (int(collar[0]), int(collar[1])), int(hr * 0.40),
                 ow=max(1, int(1.6 * s)), core=False, sheen=False)
    return hoods, hood_r


# ── the bone-naga-queen ───────────────────────────────────────────────────────
def draw_nagini_devi(surf, cx, cy, s):
    """Mid-proportioned naga death-queen: a chibi three-eyed skull ringed by six
    reared cobra-hoods on bone-snake arms, crowned with a skull-tiara, rooted on
    a coiled-serpent base. `s` = unit scale around a ~140-unit figure."""

    # WHY a big chibi head: at 32px the ring of hoods crowds the skull, so the
    # FACE must be the dominant central mass to win the read. The head sits a
    # touch LOW in the frame so the ring of lobes haloes UP and AROUND it and the
    # gap UNDER the chin reads as open air, not a crouching torso.
    head_c = (cx, cy + int(6 * s))
    hr = int(31 * s)
    hood_r = int(15 * s)

    # === SIX SERPENT-NECK HOODS — necks behind, fat lobes over-drawn later =====
    hoods, hr_hood = draw_hood_ring(surf, head_c[0], head_c[1], s, hr, hood_r)

    # === LOWER BODY — only a SLIM coiled tail-knot tucked under the chin =======
    # WHY tiny + low: directive moves mass OFF the lap and UP into the ring, so
    # the body is just a small bronze coil that roots the figure without reading
    # as a torso. The blackout below the chin stays mostly open air.
    base_y = head_c[1] + int(hr * 1.18)
    coil = [(cx - int(16 * s), base_y - int(8 * s)),
            (cx + int(16 * s), base_y - int(8 * s)),
            (cx + int(12 * s), base_y + int(7 * s)),
            (cx - int(12 * s), base_y + int(7 * s))]
    triad_blob(surf, BRONZE, coil,
               core_pts=[(cx + int(2 * s), base_y - int(6 * s)), (cx + int(15 * s), base_y - int(6 * s)),
                         (cx + int(11 * s), base_y + int(6 * s)), (cx + int(2 * s), base_y + int(6 * s))],
               ow=max(1, int(1.8 * s)))
    # a couple verdigris scale-grooves so the knot reads as snake-tail, not a base
    for k in (-1, 0, 1):
        gx = cx + int(k * 9 * s)
        pygame.draw.line(surf, TEAL_D, (gx, base_y - int(8 * s)),
                         (gx, base_y + int(6 * s)), max(1, int(1.6 * s)))

    # === SIX COBRA-HOOD LOBES — the haloing ring (drawn over necks + body) =====
    # WHY drawn after necks/body, before head: the fat lobes ARCH around the
    # skull so the RING reads, while the big central head over-draws their inner
    # edges to keep the negative gaps between adjacent lobes clean.
    for (hood_c, a, with_skull) in hoods:
        cobra_hood(surf, int(hood_c[0]), int(hood_c[1]), hr_hood, s, a,
                   with_skull, lit=False)

    # === SKULL HEAD — chibi, scary-cute, three-eyed (the framed FACE) =========
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two big lower sockets — scary-CUTE, a NOTCH DIMMER than the third eye
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.25))
        pygame.draw.circle(surf, TEAL_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.12))
    # THIRD EYE — the single BRIGHTEST pixel: a vertical verdigris slit with a
    # hot mint-green core, central on the brow. WHY verdigris not magenta: this
    # is the owned focal hue that splits Nagini from Mukha's rose third-eye.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.34)
    pygame.draw.ellipse(surf, INK, (tex - int(7 * s), tey - int(9 * s), int(14 * s), int(18 * s)))
    pygame.draw.ellipse(surf, EYE, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, EYE_BR, (tex - int(4 * s), tey - int(5 * s), int(8 * s), int(10 * s)))
    pygame.draw.circle(surf, EYE_BR, (tex - int(1 * s), tey - int(2 * s)), max(2, int(3.2 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(2 * s)),
                       max(1, int(1.6 * s)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    # grinning tooth row (cute, not gory)
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.48), my),
                     (head_c[0] + int(hr * 0.48), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.15), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.15), my + int(hr * 0.13)), max(1, int(1 * s)))
    # two small fangs at the corners (wrathful + serpent tell)
    for sgn in (-1, 1):
        fx = head_c[0] + sgn * int(hr * 0.40)
        pygame.draw.polygon(surf, BONE_SH,
                            [(fx - int(2 * s), my), (fx + int(2 * s), my),
                             (fx, my + int(hr * 0.26))])

    # === SKULL-CROWN TIARA (preserved DNA — small bronze band + 3 skulls) =====
    # WHY a SHALLOW arc seated low on the brow in the gap between the upper hoods:
    # the two topmost hoods rear out to the sides, leaving a clean wedge above the
    # crown for the skull-tiara to read against sky.
    tiara_r = int(hr * 0.98)
    tsk_r = int(hr * 0.30)
    band_pts = []
    for i in range(9):
        a = math.radians(238 + i * (64 / 8))
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(6 * s))
    pygame.draw.lines(surf, BRONZE, False, band_pts, int(3 * s))
    pygame.draw.lines(surf, BRONZE_BR, False, band_pts[:5], max(1, int(1.2 * s)))
    for i in range(3):
        a = math.radians(244 + i * (52 / 2))
        sx = head_c[0] + math.cos(a) * tiara_r
        sy = head_c[1] + math.sin(a) * tiara_r
        tiara_skull(surf, int(sx), int(sy), tsk_r, s, lit=(i == 1))


# ── the caduceus twin-snake staff → pillar mirror ─────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The caduceus twin-snake staff IS the pillar: two bone-snakes wind up a
    central bronze rod and rear into facing cobra-hoods at the cap — the
    creature's own serpent language, bottom-rooted, symmetric on-axis.

    `cap` names the END that faces the GAP."""
    rod_w = int(6 * s)
    # central bronze rod the snakes wind around
    pygame.draw.rect(surf, INK, (cx - rod_w // 2 - int(1 * s), top, rod_w + int(2 * s), bot - top))
    pygame.draw.rect(surf, BRONZE, (cx - rod_w // 2, top, rod_w, bot - top))
    pygame.draw.rect(surf, BRONZE_BR, (cx - rod_w // 2, top, max(1, int(2 * s)), bot - top))

    cap_room = int(40 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
        cap_y = bot - int(22 * s)
        grow = +1
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
        cap_y = top + int(22 * s)
        grow = -1

    # === twin bone-snakes spiralling the rod (the tileable shaft) =============
    snake_w = int(7 * s)
    amp = int(13 * s)
    period = int(34 * s)
    for phase in (0.0, math.pi):   # the two crossing snakes
        pts = []
        y = b0
        while y <= b1:
            x = cx + math.sin((y - b0) / period * 2 * math.pi + phase) * amp
            pts.append((x, y))
            y += int(3 * s)
        thick_path(surf, BONE, pts, snake_w, max(1, int(1.2 * s)))
        # verdigris scale-dashes where the snake crosses the centre rod
        for k in range(len(pts)):
            if abs(pts[k][0] - cx) < int(2 * s):
                pygame.draw.circle(surf, TEAL_D, (int(pts[k][0]), int(pts[k][1])),
                                   max(1, int(1.6 * s)))

    # === gap-edge cap: two facing cobra-hoods rearing toward the gap ==========
    # WHY twin facing hoods at the gap: it mirrors the creature's hood language
    # and the symmetric pair stays on-axis, never wider than the snake span.
    hood_cap_r = int(9 * s)
    for sgn in (-1, 1):
        hc = (cx + sgn * int(11 * s), cap_y + grow * int(2 * s))
        # the hood rears toward the gap and flares outward to its side
        ang = math.atan2(grow, sgn * 0.6)
        cobra_hood(surf, int(hc[0]), int(hc[1]), hood_cap_r, s, ang, with_skull=False, lit=True)
    # a small bronze collar where the snakes meet the cap
    collar_y = cap_y - grow * int(20 * s)
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, BRONZE, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, BRONZE_BR, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))
    # a verdigris focal stone between the facing hoods (the gap glow)
    pygame.draw.circle(surf, INK, (cx, cap_y), int(4 * s))
    pygame.draw.circle(surf, EYE, (cx, cap_y), int(3 * s))
    pygame.draw.circle(surf, EYE_BR, (cx - int(1 * s), cap_y - int(1 * s)), max(1, int(1.6 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def grow1(surf):
    return grow_outline(surf, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def main():
    W, H = 1010, 820
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "..", "..", "..", "..", "game", "assets",
                            "LiberationSans-Bold.ttf")
    font_dir = os.path.normpath(font_dir)
    if os.path.exists(font_dir):
        font_big = pygame.font.Font(font_dir, 28)
        font = pygame.font.Font(font_dir, 16)
        font_sm = pygame.font.Font(font_dir, 12)
    else:  # headless fallback so the script never hard-fails on a missing font
        font_big = pygame.font.SysFont("DejaVu Sans", 28, bold=True)
        font = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
        font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("NAGINI-DEVI", True, LABEL), (24, 14))
    sheet.blit(font_sm.render(
        "serpent hood-ring bone-naga-queen  ·  KIND: arms-as-snakes hood-RING · mid · aged-bronze (dom) + dull-verdigris · 6 cobra-hood lobes haloing the skull · round 2",
        True, LABEL_DIM), (250, 26))

    # === (a) EPIC HERO ========================================================
    big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
    draw_nagini_devi(big, 178 * SS, 232 * SS, 1.5 * SS)
    hero = grow1(pygame.transform.smoothscale(big, (360, 470)))
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — EPIC hero", True, LABEL), (96, 566))
    sheet.blit(font_sm.render("Skull HALOED by six fat spade-hood lobes (S-necks arching up & around — a flower of petals).", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("Tiny skulls clenched in 3 of 6 open hood-jaws (alternating); chin-gap below reads open.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Dull-verdigris third-eye = brightest pixel + thin oxide rims; bronze = dominant mass; skull-tiara on top.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR — caduceus twin-snake staff, mirrored, bottom-rooted ======
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow1(pygame.transform.smoothscale(top_big, (150, 250)))
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow1(pygame.transform.smoothscale(bot_big, (150, 250)))
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (58, 64, 56), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — caduceus staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("twin bone-snakes spiral a bronze rod =", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("shaft; twin facing cobra-hoods + verdigris", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("stone cap the gap (mirrored, bottom-rooted)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        b = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_nagini_devi(b, 55 * SS, 56 * SS, (32 / 150.0) * SS)
        return grow1(pygame.transform.smoothscale(b, (110, 110)))

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

    def pillar_chip32():
        b = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(b, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        return grow1(pygame.transform.smoothscale(b, (44, 130)))

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

    # === (d) BLACKED-OUT SILHOUETTE PROOF =====================================
    sil_y = 432
    sheet.blit(font.render("Silhouette proof", True, LABEL), (panel_x + 16, sil_y - 8))
    big_sil = pygame.Surface((150 * SS, 170 * SS), pygame.SRCALPHA)
    draw_nagini_devi(big_sil, 75 * SS, 86 * SS, 0.5 * SS)
    sil = pygame.transform.smoothscale(big_sil, (150, 170))
    # flatten every non-transparent pixel to solid ink — the blackout read
    mask = pygame.mask.from_surface(sil)
    blk = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
    pygame.draw.rect(sheet, (180, 184, 176), (panel_x + 16, sil_y + 14, 150, 170))
    pygame.draw.rect(sheet, INK, (panel_x + 16, sil_y + 14, 150, 170), 1)
    sheet.blit(blk, (panel_x + 16, sil_y + 14))
    # a TRUE-32px blackout beside it: proves the lobes stay DISCRETE under the chip
    chip_sil = pygame.Surface((32, 32), pygame.SRCALPHA)
    chip_src = pygame.Surface((40 * SS, 40 * SS), pygame.SRCALPHA)
    draw_nagini_devi(chip_src, 20 * SS, 21 * SS, (32 / 150.0) * SS)
    chip_small = pygame.transform.smoothscale(chip_src, (32, 32))
    cmask = pygame.mask.from_surface(chip_small)
    chip_blk = cmask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
    chip_blk = pygame.transform.scale(chip_blk, (96, 96))   # nearest-neighbour zoom
    pygame.draw.rect(sheet, (180, 184, 176), (panel_x + 174, sil_y + 64, 96, 96))
    pygame.draw.rect(sheet, INK, (panel_x + 174, sil_y + 64, 96, 96), 1)
    sheet.blit(chip_blk, (panel_x + 174, sil_y + 64))
    sheet.blit(font_sm.render("flower of fat lobes", True, LABEL_DIM), (panel_x + 174, sil_y + 24))
    sheet.blit(font_sm.render("around a skull", True, LABEL_DIM), (panel_x + 174, sil_y + 40))
    sheet.blit(font_sm.render("32px blk (3x zoom)", True, LABEL_DIM), (panel_x + 174, sil_y + 164))

    # === (e) PALETTE STRIP ====================================================
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, sil_y + 196))
    swatches = [
        (BRONZE, "aged-bronze (dom)"), (BRONZE_D, "deep-bronze"),
        (TEAL, "verdigris-teal"), (TEAL_D, "deep verdigris"),
        (BONE, "bone-core"), (EYE, "serpent-eye glow"),
        (BONE_DD, "bone hollow"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, sil_y + 222
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 24
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 18, 18))
        pygame.draw.rect(sheet, c, (rx, ry, 16, 16))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 24, ry + 2))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (28,22,26) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
