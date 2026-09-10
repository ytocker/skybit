"""
Round-1 concept renderer for NAGA-KAPALI — the serpent-thread skull-priest,
sister #3 of the mukha_citipati_court brood. Headless Pygame; ELEVATED pipeline
(supersample SS=8 → smoothscale) so the serpent coil, scale texture, and six
palm-skulls stay crisp at downscale. Keeps the shipped house grammar: flat
saturated fills, hard 1-2px ink keyline (28,22,26), dark-core → flat-fill →
top-left rim-sheen triad, 1px alpha-grown outline, chibi proportions,
scary-CUTE; procedural-only (no gradients/PNGs).

WHY this sister is the serpent priest: she fuses the Mukha-Devi SIX-ARM radial
fan (every palm an open hand cradling a TINY SKULL) onto the CITIPATI tall
rib-barrel dancing torso (cocked hip). Her ornament SET is naga: a GREEN naga
sacred-thread (the diagonal upavita) crossing the torso, a SECOND snake worn as
a choker, gold-rimmed kapala skull-cups knotted at the thread joints, and scale
texture. The crown FUSES the Citipati 5-skull arc-sweep AND the Mukha
tiara-band, with a rearing-NAGA hood reared over the centre skull — the hood is
the keeper tell and the element that carries the 32px serpent read.

WHY DARKENED jade + verdigris (the AD note): the coil must read by VALUE, not
hue alone — colourblind-safe. The bone mass stays the warm dominant field; the
green thread is a thin SATURATED diagonal that contrasts against it by both
value and chroma. Gold rims the kapala cups; amber is the third-eye slit + the
crown-centre glow ONLY (glow restraint = professional).

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief: jade + verdigris DARKENED, gold, amber) ─────
# Warm bone is the dominant MASS so the green thread reads as a saturated accent
# against it (value + chroma separation, not hue alone).
BONE      = (236, 224, 200)   # warm bone (the dominant fill)
BONE_D    = (182, 166, 138)   # bone dark-core / shade
BONE_DD   = (132, 116,  92)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (252, 244, 226)   # bone top-left rim-sheen
# crown skulls sit one NOTCH DARKER than the body bone — the dimmest rung of the
# value ladder (below the mid-value palm-skulls, far below the amber third-eye).
BONE_CR   = (196, 182, 152)   # crown-skull bone (dimmest rung)
BONE_CR_D = (146, 132, 104)   # crown-skull shade
# DARKENED so the snake reads by value: jade is a deep mid-dark green, verdigris
# is darker still — the coil never washes out to a single light-green hue.
JADE      = ( 30, 120,  82)   # naga sacred-thread (the bold diagonal upavita)
JADE_BR   = ( 96, 200, 140)   # jade scale-highlight / sheen
JADE_D    = ( 14,  68,  50)   # deep jade shade / underside
# the carrier stripe is darker/more saturated still — at true 32px the thread
# must read as a SOLID dark-jade diagonal by value, not a pale-green sliver.
# pushed DARKER + more saturated still (the gate fix): at true 32px the thread is
# the ONE ornament that must survive the smoothscale, so the carrier fill is a deep
# saturated jade that holds a hard value gap below the warm bone after downscale —
# it reads as a directional stripe, never averaging out to a pale mid-green.
JADE_CAR  = ( 16,  82,  56)   # the 32px thread-carrier fill (bold, dark stripe)
VERD      = ( 26,  96,  86)   # verdigris (darker, the choker + 2nd snake body)
VERD_BR   = ( 70, 160, 146)
VERD_D    = ( 14,  58,  52)
GOLD      = (220, 178,  82)   # gold kapala-cup rims + thread knots
GOLD_BR   = (246, 212, 124)
GOLD_D    = (164, 128,  54)
AMBER     = (250, 168,  56)   # amber third-eye slit + crown-centre glow ONLY
AMBER_BR  = (255, 218, 138)   # hottest amber core (single brightest pixel)
AMBER_D   = (196, 110,  28)
INK       = ( 28,  22,  26)   # hard ink keyline

BG        = ( 92,  98,  94)   # neutral grey-green review backdrop
PANEL     = ( 70,  78,  74)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 236)
LABEL_DIM = (190, 200, 194)


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


# ── a single ornamental crown-skull (cloned from Citipati crown_skull) ────────
def crown_skull(surf, cx, cy, r, s, lit=False, bone=BONE):
    """Tiny bone skull — domed cranium, two dark sockets, a stub jaw. WHY small
    high-contrast sockets: each crown skull must punch a clean bone shape with
    two dark dots at 32px so the dome stays the dominant value. `lit` swaps the
    eye-pins to amber for the crown-centre skull (the only crown glow). `bone`
    lets the arc skulls render a NOTCH DARKER (BONE_CR) than palm/cap skulls so
    they sit at the dimmest rung of the value ladder."""
    triad_circle(surf, bone, (cx, cy), r, ow=max(1, int(1.6 * s)), core=False)
    jaw = [(cx - int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.34), cy + int(r * 1.0)),
           (cx - int(r * 0.34), cy + int(r * 1.0))]
    triad_blob(surf, bone, jaw, ow=max(1, int(1.2 * s)))
    eye_c = AMBER_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.04)), max(1, int(r * 0.13)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))
    pygame.draw.line(surf, INK,
                     (cx - int(r * 0.34), cy + int(r * 0.70)),
                     (cx + int(r * 0.34), cy + int(r * 0.70)),
                     max(1, int(1.2 * s)))


# ── a tiny palm-skull cradled in an open hand (the brood motif) ───────────────
def palm_skull(surf, hx, hy, r, s, ang):
    """An OPEN palm cradling a TINY SKULL — replaces Mukha's relic discs and is
    the locked motif. The five fingers fan from the wrist; the skull rests in the
    cup. WHY mid-value: the palm-skulls sit BELOW the third-eye and ABOVE the
    crown skulls on the value ladder, so they read as the second-brightest tier.
    `ang` points outward from the torso so the open palm faces away."""
    # the open palm cup — a small bone fan behind the skull
    fingers = []
    for k in range(-2, 3):
        fa = ang + math.radians(k * 22)
        fingers.append((hx + math.cos(fa) * r * 1.45, hy + math.sin(fa) * r * 1.45))
    palm = [(hx + math.cos(ang + math.pi) * r * 0.7,
             hy + math.sin(ang + math.pi) * r * 0.7)] + fingers
    triad_blob(surf, BONE, palm, ow=max(1, int(1.2 * s)))
    # individual finger ticks for the open-hand read at hero scale
    for fa_k in range(-2, 3):
        fa = ang + math.radians(fa_k * 22)
        base = (hx + math.cos(ang) * r * 0.3, hy + math.sin(ang) * r * 0.3)
        tip = (hx + math.cos(fa) * r * 1.5, hy + math.sin(fa) * r * 1.5)
        pygame.draw.line(surf, BONE_DD, base, tip, max(1, int(1.0 * s)))
    # the cradled tiny skull — domed bone with two dark pits, sits in the cup.
    # WHY enlarged + pulled toward the palm centre (the LOCKED-miss fix): in round
    # 1 the near-horizontal lower arms let the fan dominate and two skulls read as
    # bare discs. The skull is now ≈0.92× the cup radius and seated dead-centre on
    # the wrist so all SIX cradled skulls punch the same mid-value bone shape.
    sk = (int(hx), int(hy))
    sr = int(r * 0.92)
    triad_circle(surf, BONE, sk, sr, ow=max(1, int(1.5 * s)), core=False)
    for ex in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (sk[0] + ex * int(sr * 0.34), sk[1] - int(sr * 0.06)),
                           max(1, int(sr * 0.24)))
    # a stub jaw below the dome so the skull reads as a skull, not a bead
    jaw = [(sk[0] - int(sr * 0.5), sk[1] + int(sr * 0.48)),
           (sk[0] + int(sr * 0.5), sk[1] + int(sr * 0.48)),
           (sk[0] + int(sr * 0.32), sk[1] + int(sr * 0.95)),
           (sk[0] - int(sr * 0.32), sk[1] + int(sr * 0.95))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.1 * s)))
    pygame.draw.circle(surf, INK, (sk[0], sk[1] + int(sr * 0.26)), max(1, int(sr * 0.12)))
    pygame.draw.line(surf, INK,
                     (sk[0] - int(sr * 0.3), sk[1] + int(sr * 0.62)),
                     (sk[0] + int(sr * 0.3), sk[1] + int(sr * 0.62)),
                     max(1, int(1.0 * s)))


# ── the six-arm radial starburst (cloned from Mukha draw_arm_fan) ─────────────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr):
    """Six fat bone arms splay in a wide symmetric STARBURST around the torso —
    the Mukha radial KIND tell. Low origin, spread ≈ ±[100,64,28]° off vertical,
    NO arm aimed straight up so the crown sky stays open. Returns the six hand
    centres + their outward angles for palm-skull placement."""
    shoulder = (sh_cx, sh_cy)
    arm_len = int(hr * 1.95)
    arm_th = int(12 * s)
    spread = [100, 64, 28]
    order = []
    for sgn in (-1, 1):
        for d in spread:
            a = math.radians(-90 + sgn * d)
            order.append((sgn, d, a))
    order.sort(key=lambda o: -o[1])
    hands = []
    for sgn, d, a in order:
        sh = (shoulder[0] + sgn * int(hr * 0.55), shoulder[1])
        elbow = (sh[0] + math.cos(a) * arm_len * 0.52,
                 sh[1] + math.sin(a) * arm_len * 0.52)
        hand = (sh[0] + math.cos(a) * arm_len,
                sh[1] + math.sin(a) * arm_len)
        for (p, q) in ((sh, elbow), (elbow, hand)):
            dx, dy = q[0] - p[0], q[1] - p[1]
            L = max(1.0, math.hypot(dx, dy))
            nx, ny = -dy / L * arm_th / 2, dx / L * arm_th / 2
            quad = [(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                    (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)]
            triad_blob(surf, BONE, quad,
                       sheen_pts=[(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                                  (q[0] + nx * 0.3, q[1] + ny * 0.3),
                                  (p[0] + nx * 0.3, p[1] + ny * 0.3)],
                       ow=max(1, int(arm_th * 0.16)))
        triad_circle(surf, BONE, (int(elbow[0]), int(elbow[1])), int(arm_th * 0.55),
                     ow=max(1, int(1.2 * s)), core=False)
        hands.append((sgn, d, hand, a))
    hands.sort(key=lambda h: (h[0], -h[1]))
    return [(int(h[2][0]), int(h[2][1]), h[3]) for h in hands]


# ── a coiling serpent body segment (the naga ornament — value-graded scales) ──
def serpent_band(surf, pts, width, s, body=JADE, body_d=JADE_D, body_br=JADE_BR,
                 scales=True):
    """A thick snake body following a poly-line, with a DARK underside core and a
    light top sheen so the coil reads by VALUE (the AD note). Optional scale-pip
    texture (hero-only — drops out cleanly at 32px). The band is the green
    diagonal that carries the silhouette."""
    # ribbon polygon: offset each point by the segment normal
    top, bot = [], []
    for i in range(len(pts)):
        if i == 0:
            dx, dy = pts[1][0]-pts[0][0], pts[1][1]-pts[0][1]
        elif i == len(pts)-1:
            dx, dy = pts[-1][0]-pts[-2][0], pts[-1][1]-pts[-2][1]
        else:
            dx, dy = pts[i+1][0]-pts[i-1][0], pts[i+1][1]-pts[i-1][1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * width / 2, dx / L * width / 2
        top.append((pts[i][0] + nx, pts[i][1] + ny))
        bot.append((pts[i][0] - nx, pts[i][1] - ny))
    poly = top + bot[::-1]
    pygame.draw.polygon(surf, INK, poly)
    pygame.draw.polygon(surf, body, poly)
    # dark underside core — over HALF the ribbon, so the band stays a dark stripe
    # by VALUE at downscale (the carrier read), not a hue that averages to pale.
    core = [( (top[i][0]+bot[i][0])/2 + (bot[i][0]-top[i][0])*0.02,
              (top[i][1]+bot[i][1])/2 + (bot[i][1]-top[i][1])*0.02 )
            for i in range(len(pts))] + bot[::-1]
    pygame.draw.polygon(surf, body_d, core)
    # top sheen kept a THIN sliver (top ~22%) so it never washes the stripe pale
    # at 32px — value contrast must survive the smoothscale.
    sh_poly = top + [((top[i][0]*0.78+bot[i][0]*0.22), (top[i][1]*0.78+bot[i][1]*0.22))
                     for i in range(len(pts)-1, -1, -1)]
    pygame.draw.polygon(surf, body_br, sh_poly)
    pygame.draw.polygon(surf, INK, poly, max(1, int(1.6 * s)))
    # scale pips along the spine (hero-only — sub-pixel at 32px, drops out)
    if scales and width > 7 * s:
        for i in range(len(pts) - 1):
            seg = 3
            for j in range(seg):
                t = (i + j / seg) / (len(pts) - 1)
                # interpolate centre-line position
                idx = min(len(pts) - 2, int(t * (len(pts) - 1)))
                ft = t * (len(pts) - 1) - idx
                cxp = pts[idx][0] + (pts[idx+1][0]-pts[idx][0]) * ft
                cyp = pts[idx][1] + (pts[idx+1][1]-pts[idx][1]) * ft
                pygame.draw.circle(surf, body_d, (int(cxp), int(cyp)),
                                   max(1, int(width * 0.16)), max(1, int(1 * s)))


def serpent_head(surf, cx, cy, r, s, ang, body=JADE, body_br=JADE_BR,
                 body_d=JADE_D):
    """A small naga head terminating a coil end — wedge skull, two amber-less
    dark eyes, a flicking tongue. Used at the choker's snake mouth and the
    thread-tail."""
    # wedge head pointing along ang
    nose = (cx + math.cos(ang) * r * 1.3, cy + math.sin(ang) * r * 1.3)
    l = (cx + math.cos(ang + 2.2) * r, cy + math.sin(ang + 2.2) * r)
    rr = (cx + math.cos(ang - 2.2) * r, cy + math.sin(ang - 2.2) * r)
    triad_blob(surf, body, [nose, l, (cx, cy), rr], ow=max(1, int(1.3 * s)))
    pygame.draw.circle(surf, body_d, (int(cx), int(cy)), max(1, int(r * 0.4)))
    # eye dots
    ex = cx + math.cos(ang + 1.4) * r * 0.5
    ey = cy + math.sin(ang + 1.4) * r * 0.5
    pygame.draw.circle(surf, INK, (int(ex), int(ey)), max(1, int(r * 0.22)))
    # forked tongue flick
    tt = (nose[0] + math.cos(ang) * r * 0.6, nose[1] + math.sin(ang) * r * 0.6)
    pygame.draw.line(surf, AMBER_D, nose, tt, max(1, int(1.4 * s)))


# ── the rearing NAGA hood crown-piece (the keeper tell + 32px serpent read) ───
def naga_hood(surf, cx, cy, r, s):
    """A cobra hood reared OVER the centre crown skull — a fanned green cowl with
    a dark spine ridge and an amber-touched serpent face. WHY this is the keeper
    tell: at 32px the broad green hood fan + the bold green diagonal thread are
    the two shapes that say 'serpent', so the silhouette stays unmistakably the
    naga sister. The hood seats in the open crown sky above the tiara-band."""
    # the broad fanned cowl (wider than tall, dark verdigris with jade sheen)
    hood = [(cx, cy - int(r * 1.65)),
            (cx + int(r * 1.35), cy - int(r * 0.65)),
            (cx + int(r * 1.05), cy + int(r * 0.35)),
            (cx, cy + int(r * 0.1)),
            (cx - int(r * 1.05), cy + int(r * 0.35)),
            (cx - int(r * 1.35), cy - int(r * 0.65))]
    triad_blob(surf, VERD, hood,
               core_pts=[(cx, cy - int(r * 0.2)),
                         (cx + int(r * 0.9), cy - int(r * 0.55)),
                         (cx + int(r * 0.85), cy + int(r * 0.25)),
                         (cx, cy + int(r * 0.05))],
               sheen_pts=[(cx, cy - int(r * 1.5)),
                          (cx - int(r * 0.5), cy - int(r * 0.9)),
                          (cx - int(r * 1.1), cy - int(r * 0.6)),
                          (cx - int(r * 0.6), cy - int(r * 0.7))],
               ow=max(1, int(1.7 * s)))
    # hood ribs (the cobra spread markings) — value grooves, read at 32px as fan
    for k in (-1, 0, 1):
        rx = cx + int(k * r * 0.72)
        pygame.draw.line(surf, VERD_D, (cx, cy - int(r * 0.1)),
                         (rx, cy - int(r * 1.35)), max(2, int(2.2 * s)))
    # the serpent face on the hood — a small wedge with an amber eye-dot pair
    face = [(cx, cy + int(r * 0.5)),
            (cx + int(r * 0.42), cy - int(r * 0.05)),
            (cx, cy - int(r * 0.2)),
            (cx - int(r * 0.42), cy - int(r * 0.05))]
    triad_blob(surf, JADE, face, ow=max(1, int(1.3 * s)))
    for ex in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (cx + ex * int(r * 0.2), cy + int(r * 0.05)),
                           max(1, int(r * 0.13)))
        pygame.draw.circle(surf, AMBER, (cx + ex * int(r * 0.2), cy + int(r * 0.05)),
                           max(1, int(r * 0.06)))


# ── a gold-rimmed kapala skull-cup (the thread-knot ornament) ─────────────────
def kapala_cup(surf, cx, cy, r, s):
    """A small skull-cup bowl rimmed in gold — knotted at the thread joints.
    HERO-only ornament (collapses out at 32px). Dark bowl, gold rim band, a tiny
    bone skull-face on the front."""
    bowl = [(cx - r, cy - int(r * 0.4)), (cx + r, cy - int(r * 0.4)),
            (cx + int(r * 0.6), cy + int(r * 0.7)), (cx - int(r * 0.6), cy + int(r * 0.7))]
    triad_blob(surf, BONE_D, bowl, ow=max(1, int(1.2 * s)))
    # gold rim band across the top
    pygame.draw.line(surf, INK, (cx - r, cy - int(r * 0.4)),
                     (cx + r, cy - int(r * 0.4)), max(2, int(3 * s)))
    pygame.draw.line(surf, GOLD, (cx - r, cy - int(r * 0.4)),
                     (cx + r, cy - int(r * 0.4)), max(1, int(2 * s)))
    pygame.draw.line(surf, GOLD_BR, (cx - int(r * 0.7), cy - int(r * 0.4)),
                     (cx + int(r * 0.1), cy - int(r * 0.4)), max(1, int(1 * s)))
    # two socket dots on the bowl face
    for ex in (-1, 1):
        pygame.draw.circle(surf, INK, (cx + ex * int(r * 0.34), cy + int(r * 0.05)),
                           max(1, int(r * 0.16)))


# ── the serpent-thread skull-priest ──────────────────────────────────────────
def draw_naga_kapali(surf, cx, cy, s):
    """Cocked-hip dancing chibi skeleton (CITIPATI body) under a Mukha SIX-ARM
    radial fan; each open palm cradles a tiny skull. A green naga sacred-thread
    crosses the torso diagonally, a second snake rings the throat as a choker,
    gold kapala cups knot the thread. The crown fuses the 5-skull arc + the
    Mukha tiara-band, with a rearing-naga hood over the centre skull. The amber
    third-eye slit is the single brightest pixel. `s` = unit around ~130 units."""

    # vertical anchors (chibi: big head, short torso, springy legs, cocked hip)
    head_c = (cx, cy - int(34 * s))
    hr = int(26 * s)
    hip_y = cy + int(26 * s)
    hip_cx = cx + int(7 * s)

    # === SIX-ARM RADIAL FAN (drawn first → arms sit BEHIND torso & head) ======
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.92), s, hr)

    # === LEGS — cocked-hip dance: one knee kicked OUT (CITIPATI bottom read) ===
    def bone_limb(p0, p1, p2, thick, joint=True):
        for (a, b) in ((p0, p1), (p1, p2)):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = max(1.0, math.hypot(dx, dy))
            nx, ny = -dy / L * thick / 2, dx / L * thick / 2
            quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                    (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
            triad_blob(surf, BONE, quad,
                       sheen_pts=[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                                  (b[0] + nx * 0.3, b[1] + ny * 0.3),
                                  (a[0] + nx * 0.3, a[1] + ny * 0.3)],
                       ow=max(1, int(thick * 0.18)))
        if joint:
            triad_circle(surf, BONE, p1, int(thick * 0.62), ow=max(1, int(1.2 * s)),
                         core=False)

    leg_th = int(14 * s)
    hipL = (hip_cx - int(13 * s), hip_y)
    kneeL = (hip_cx - int(20 * s), hip_y + int(26 * s))
    footL = (hip_cx - int(22 * s), hip_y + int(52 * s))
    bone_limb(hipL, kneeL, footL, leg_th)
    hipR = (hip_cx + int(11 * s), hip_y)
    kneeR = (hip_cx + int(30 * s), hip_y + int(8 * s))
    footR = (hip_cx + int(20 * s), hip_y + int(34 * s))
    bone_limb(hipR, kneeR, footR, leg_th)
    for (fx, fy), sgn in ((footL, -1), (footR, +1)):
        foot = [(fx - int(4 * s), fy - int(2 * s)), (fx + sgn * int(16 * s), fy + int(2 * s)),
                (fx + sgn * int(15 * s), fy + int(10 * s)), (fx - int(5 * s), fy + int(8 * s))]
        triad_blob(surf, BONE, foot, ow=max(1, int(1.4 * s)))

    # === PELVIS + tall RIBCAGE barrel (CITIPATI torso) ========================
    pelvis = [(hip_cx - int(17 * s), hip_y - int(4 * s)),
              (hip_cx + int(17 * s), hip_y - int(6 * s)),
              (hip_cx + int(14 * s), hip_y + int(10 * s)),
              (hip_cx, hip_y + int(13 * s)),
              (hip_cx - int(15 * s), hip_y + int(9 * s))]
    triad_blob(surf, BONE, pelvis,
               core_pts=[(hip_cx - int(6 * s), hip_y + int(2 * s)),
                         (hip_cx + int(14 * s), hip_y - int(2 * s)),
                         (hip_cx + int(13 * s), hip_y + int(9 * s)),
                         (hip_cx, hip_y + int(12 * s))],
               ow=max(1, int(1.6 * s)))
    pygame.draw.circle(surf, BONE_DD, (hip_cx, hip_y + int(2 * s)), int(4 * s))

    spine_top_y = cy - int(14 * s)
    spine = [(hip_cx, hip_y - int(2 * s)),
             (cx + int(2 * s), cy + int(6 * s)),
             (cx - int(1 * s), spine_top_y)]
    pygame.draw.lines(surf, INK, False, spine, int(8 * s))
    pygame.draw.lines(surf, BONE, False, spine, int(5 * s))

    rc_cx, rc_cy = cx, cy - int(2 * s)
    rc_w, rc_h = int(34 * s), int(40 * s)
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.40), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.40), rc_cy + rc_h // 2)]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.40), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(6 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(4 * s))],
               ow=max(1, int(1.8 * s)))
    # 4 hard rib bands (the CITIPATI motif the pillar continues)
    for i in range(4):
        ry = rc_cy - rc_h // 2 + int(8 * s) + i * int(8 * s)
        bw = int(rc_w * (0.46 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(7 * s), bw * 2, int(16 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.4 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(6 * s)), max(1, int(2 * s)))

    # === NAGA SACRED-THREAD — the bold green diagonal upavita (32px CARRIER) ==
    # WHY this is the silhouette-carrier: a single thick green BAR running the FULL
    # torso, from the LEFT SHOULDER (top of the ribcage) straight down to the
    # OPPOSITE (right) HIP, then continuing unbroken across the pelvis into the
    # wrap. It is the ONE ornament that survives the downscale (the gate), so it is
    # drawn as one continuous fat dark-jade coil — a TRUE corner-to-corner diagonal,
    # not a mid-chest stub.
    # WHY the geometry change (the gate fix): round 2's band started inside the
    # ribcage and drifted only to mid-chest, so at 32px it collapsed to a hip blob
    # with no diagonal. The top anchor now sits at the OUTER TOP of the left
    # shoulder and the path runs as a near-straight ramp to the far hip — a single
    # directional ramp that smoothscale can't flatten into a blob.
    th_top = (rc_cx - int(rc_w * 0.74), rc_cy - rc_h // 2 - int(7 * s))
    th_mid = (rc_cx + int(rc_w * 0.04), rc_cy + int(3 * s))
    th_bot = (hip_cx + int(20 * s), hip_y + int(11 * s))
    th_tail = (hip_cx + int(15 * s), hip_y + int(34 * s))   # carries onto the thigh
    thread_pts = [th_top,
                  (rc_cx - int(rc_w * 0.36), rc_cy - int(14 * s)),
                  th_mid,
                  (rc_cx + int(rc_w * 0.32), rc_cy + int(16 * s)),
                  th_bot,
                  (hip_cx + int(18 * s), hip_y + int(22 * s)),
                  th_tail]
    # WHY a single unbroken band through the hip (items #1 + #2 in one stroke): the
    # diagonal and the hip-wrap are now ONE poly-line, so the jade reads as a
    # continuous line down the whole lower body — no seam, no bare hip zone at 32px.
    # WHY wider still (~17 units, ≈1px more at gameplay scale than round 2's 14) and
    # filled with the darker JADE_CAR: at true 32px the band must occupy a clear
    # diagonal corridor of dark pixels that beats the warm bone by value.
    serpent_band(surf, thread_pts, int(17 * s), s,
                 body=JADE_CAR, body_d=JADE_D, body_br=JADE_BR, scales=True)
    # serpent-tail terminus flicking off the thigh (end of the unbroken line)
    serpent_head(surf, th_tail[0], th_tail[1], int(7 * s), s,
                 math.radians(58), body=JADE, body_br=JADE_BR, body_d=JADE_D)

    # === SECOND SNAKE as a CHOKER + gold kapala cups (HERO-only ornament) =====
    # the choker rings the throat just under the jaw — verdigris (darker) so it
    # reads as a SEPARATE snake from the jade thread by value.
    neck_y = head_c[1] + int(hr * 0.96)
    choker_pts = [(rc_cx - int(rc_w * 0.42), neck_y + int(2 * s)),
                  (rc_cx - int(rc_w * 0.18), neck_y - int(3 * s)),
                  (rc_cx + int(rc_w * 0.12), neck_y - int(3 * s)),
                  (rc_cx + int(rc_w * 0.40), neck_y + int(3 * s))]
    serpent_band(surf, choker_pts, int(8 * s), s,
                 body=VERD, body_d=VERD_D, body_br=VERD_BR, scales=False)
    serpent_head(surf, rc_cx + int(rc_w * 0.40), neck_y + int(3 * s), int(6 * s), s,
                 math.radians(20), body=VERD, body_br=VERD_BR, body_d=VERD_D)
    # gold kapala skull-cups knotted at the thread joints (hero-only)
    kapala_cup(surf, th_mid[0] + int(2 * s), th_mid[1] + int(2 * s), int(7 * s), s)
    kapala_cup(surf, th_top[0], th_top[1], int(6 * s), s)
    # gold knot beads where the thread crosses (kept on the upper + mid run so the
    # gold cup-knot stays the hero accent the AD signed off on)
    for (kx, ky) in (th_top, th_mid, th_bot):
        triad_circle(surf, GOLD, (kx, ky), max(2, int(3 * s)),
                     ow=max(1, int(1 * s)), core=False)

    # === SIX PALM-SKULLS — one cradled in each open hand (the brood motif) ====
    for (hx, hy, a) in hands:
        palm_skull(surf, hx, hy, int(9 * s), s, a)

    # === SKULL HEAD — chibi, scary-cute, amber third eye (the framed FACE) ====
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two lower sockets — SHRUNK + rimmed so the amber third-eye clearly tops the
    # value ladder (the focal fix). Round 1's big black voids out-massed the amber
    # pixel; now each socket is smaller, carries a mid-value bone rim around the
    # void, and holds only a tiny dark-jade glint (no hot core) so at 32px the
    # single amber slit is the unmistakable brightest mark. WHY one more notch down
    # (~13%): at true 32px the orbit voids still rivalled the amber for area and
    # could split the focal in motion, so the void/rim shrink one step so the amber
    # third-eye clearly OUT-SIZES each socket.
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.46)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, BONE_D, (ex, ey), int(hr * 0.235))  # mid-value rim
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.19))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.148))     # smaller void
        pygame.draw.circle(surf, JADE_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           max(1, int(hr * 0.06)))
    # THIRD EYE — the single BRIGHTEST pixel: a vertical AMBER slit on the brow
    tex, tey = head_c[0], head_c[1] - int(hr * 0.40)
    pygame.draw.ellipse(surf, INK, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, AMBER, (tex - int(5 * s), tey - int(7 * s), int(10 * s), int(14 * s)))
    pygame.draw.ellipse(surf, AMBER_BR, (tex - int(3 * s), tey - int(4 * s), int(6 * s), int(8 * s)))
    pygame.draw.circle(surf, (255, 252, 232), (tex, tey - int(1 * s)), max(2, int(2.6 * s)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.24)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.24)),
                         (head_c[0], head_c[1] + int(hr * 0.52))])
    # grinning tooth row (cute, not gory)
    my = head_c[1] + int(hr * 0.68)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.5), my),
                     (head_c[0] + int(hr * 0.5), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.16), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.16), my + int(hr * 0.14)), max(1, int(1 * s)))

    # === FUSED CROWN: three layers must ALL read ==============================
    # WHY a strict draw ORDER (the LOCKED-miss fix): round 1 drew the hood LAST
    # and so wide it swallowed the 5-skull arc, reading hood-only. Now it is built
    # back-to-front as the reference does — (1) gold tiara-BAND on the brow, (2)
    # the wide Citipati 5-SKULL arc-sweep riding the OUTER arc so each dome breaks
    # the outline and is countable, then (3) a NARROW rearing naga-HOOD seated
    # over the CENTRE skull only, sized so the flanking skulls peek out either
    # side. The result reads three layers top-to-bottom: skull-arc, then hood at
    # centre, then tiara-band — the genuine fusion. Crown skulls use BONE_CR (a
    # notch darker = dimmest rung); only the centre skull glows amber.
    # -- (1) the Mukha tiara-band (gold, seated LOW on the brow) --
    tiara_r = int(hr * 1.06)
    band_pts = []
    for i in range(13):
        a = math.radians(220 + i * (100 / 12))
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(8 * s))
    pygame.draw.lines(surf, GOLD, False, band_pts, int(4 * s))
    pygame.draw.lines(surf, GOLD_BR, False, band_pts[:7], max(1, int(1.4 * s)))
    # tiny gold tiara prongs between the skulls (Mukha-band tell, hero-only detail)
    for i in range(13):
        if i % 3 != 1:
            continue
        a = math.radians(220 + i * (100 / 12))
        px = head_c[0] + math.cos(a) * tiara_r
        py = head_c[1] + math.sin(a) * tiara_r
        pygame.draw.line(surf, GOLD, (px, py),
                         (px + math.cos(a) * int(5 * s), py + math.sin(a) * int(5 * s)),
                         max(1, int(2 * s)))
    # -- (2) the Citipati 5-skull arc-sweep (WIDE, rides OUTSIDE the band) --
    # the arc sweeps a full ~150° so the two flank skulls sit well to either side
    # of where the centre hood will land — they are never covered.
    skull_cr = hr * 1.58
    skull_r = int(hr * 0.36)
    skull_pos = []
    for i in range(5):
        a = math.radians(206 + i * (128 / 4))
        sx = head_c[0] + math.cos(a) * skull_cr
        sy = head_c[1] + math.sin(a) * skull_cr
        skull_pos.append((int(sx), int(sy)))
    # draw the FLANK skulls first (they sit beside/behind the hood)
    for i in (0, 1, 3, 4):
        crown_skull(surf, skull_pos[i][0], skull_pos[i][1], skull_r, s,
                    lit=False, bone=BONE_CR)
    # -- (3) the rearing NAGA HOOD over the CENTRE skull (narrow keeper tell) --
    # seated just above the centre skull and kept narrow (≈1.1× the head-skull
    # span) so flank skulls #0/#1 and #3/#4 stay fully visible either side.
    cx_c, cy_c = skull_pos[2]
    crown_skull(surf, cx_c, cy_c, skull_r, s, lit=True, bone=BONE_CR)
    hood_y = cy_c - int(skull_r * 1.15)
    naga_hood(surf, cx_c, hood_y, int(hr * 0.40), s)


# ── the coiling-naga shaft → pillar mirror (built from the sister's own forms) ─
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The COILING NAGA itself IS the pillar: a thick serpent body winds the full
    length of the shaft — a sinuous dark-jade coil whose scale segments alternate
    in VALUE (lit jade vs. deep-jade shade) so it reads unmistakably as a winding
    snake, not a bead column. The gap end rears up into a naga-HOOD cradling a
    gold-rimmed KAPALA cup — the creature-derived gap cap, mirrored top↔bottom on
    the axis. WHY this rebuild (the pillar fix): round 1's vertebra/bead column
    was too close to Citipati's khatvanga; the sister's OWN ornament is the naga,
    so her pillar is literally her serpent. The bold dark-jade body is the
    pillar's 32px carrier, mirroring the figure's sacred-thread.

    `cap` names the END that faces the GAP."""
    # the sinuous centre-line of the snake winding down the shaft
    cap_room = int(40 * s)
    if cap == "bottom":
        s0, s1 = top + int(4 * s), bot - cap_room
    else:
        s0, s1 = top + cap_room, bot - int(4 * s)
    amp = int(11 * s)            # how far the coil swings off-axis
    body_w = int(16 * s)         # thick snake body (the carrier mass)
    coil_pts = []
    span = max(1, s1 - s0)
    steps = max(6, span // max(1, int(7 * s)))
    seg_centres = []
    for i in range(steps + 1):
        t = i / steps
        y = s0 + t * span
        # a swinging sine winds the body side to side (the coil read)
        x = cx + math.sin(t * math.pi * 3.4) * amp
        coil_pts.append((x, y))
        seg_centres.append((x, y, t))

    # the thick serpent body — dark-jade carrier with a thin top sheen
    serpent_band(surf, coil_pts, body_w, s,
                 body=JADE_CAR, body_d=JADE_D, body_br=JADE_BR, scales=False)

    # alternating-value SCALE SEGMENTS banded across the body (the value rhythm
    # that makes it read as a coiling snake at hero; collapses cleanly at 32px to
    # leave the bold dark-jade band carrying alone).
    for (x, y, t) in seg_centres:
        # segment banding ring — every other one a notch lighter for the rhythm
        idx = int(t * steps)
        seg_col = JADE if (idx % 2 == 0) else JADE_D
        pygame.draw.circle(surf, seg_col, (int(x), int(y)), max(1, int(body_w * 0.32)))
        # a tiny diamond scale-pip on the lit segments (hero-only fine detail)
        if idx % 2 == 0 and body_w > 7 * s:
            d = int(body_w * 0.2)
            pygame.draw.polygon(surf, JADE_BR,
                                [(x, y - d), (x + d, y), (x, y + d), (x - d, y)])
            pygame.draw.polygon(surf, JADE_D,
                                [(x, y - d), (x + d, y), (x, y + d), (x - d, y)],
                                max(1, int(1 * s)))

    # === gap-edge cap: a rearing naga-HOOD cradling a gold KAPALA cup =========
    # the snake rears its head at the gap edge — the creature tell on the pillar.
    cap_y = (bot - int(22 * s)) if cap == "bottom" else (top + int(22 * s))
    cap_hood_r = int(16 * s)
    # gold kapala skull-cup seated at the throat of the rearing hood
    kapala_cup(surf, cx, cap_y + (int(6 * s) if cap == "bottom" else -int(6 * s)),
               int(8 * s), s)
    # the rearing naga-hood faces the gap
    hood_y = (cap_y - int(cap_hood_r * 0.4)) if cap == "bottom" \
        else (cap_y + int(cap_hood_r * 0.4))
    naga_hood(surf, cx, hood_y, cap_hood_r, s)
    # a gold collar where the rearing neck meets the coiling shaft
    collar_y = (cap_y + int(20 * s)) if cap == "bottom" else (cap_y - int(20 * s))
    pygame.draw.rect(surf, INK, (cx - int(11 * s), collar_y - int(3 * s), int(22 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(2 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 8


def _font(size, bold=True):
    """Prefer the vendored Liberation face (five `..` up to game/assets); fall
    back to a system face so the script runs anywhere."""
    here = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.normpath(os.path.join(here, "..", "..", "..", "..", "..",
                                       "game", "assets", "LiberationSans-Bold.ttf"))
    if os.path.exists(fp):
        return pygame.font.Font(fp, size)
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_naga_kapali(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def render_hero_png(path):
    """Standalone hi-res hero (~1024px tall) at SS=8 on its own canvas."""
    FH = 1024
    canvas_units = 200
    sc = (FH / 256.0)
    big = pygame.Surface((int(canvas_units * SS), int(256 * SS)), pygame.SRCALPHA)
    draw_naga_kapali(big, int(canvas_units * 0.5 * SS), int(150 * SS), 1.0 * SS)
    out = pygame.transform.smoothscale(big, (int(canvas_units * 4), 1024))
    out = grow_outline(out, INK + (255,), 2)
    pygame.image.save(out, path)
    print("wrote", path)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    render_hero_png(os.path.join(here, "round_3_hero.png"))

    W, H = 1040, 860
    font_big = _font(30)
    font = _font(17)
    font_sm = _font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("NAGA-KAPALI", True, LABEL), (24, 12))
    sheet.blit(font_sm.render(
        "serpent-thread skull-priest  ·  CITIPATI body + Mukha 6-arm fan · jade naga-thread + verdigris · "
        "amber third-eye · 3-layer fusion crown · round 3 (FINAL)",
        True, LABEL_DIM), (250, 24))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(370, 500, 185, 250, 1.7)
    sheet.blit(hero, (14, 88))
    sheet.blit(font.render("Creature — hero (SS=8)", True, LABEL), (96, 590))
    sheet.blit(font_sm.render("Mukha 6-arm fan, each open palm cradling a TINY SKULL; CITIPATI cocked-hip torso.", True, LABEL_DIM), (14, 614))
    sheet.blit(font_sm.render("ONE unbroken dark-jade diagonal: shoulder -> opposite hip -> thigh + verdigris choker + gold kapala cups.", True, LABEL_DIM), (14, 630))
    sheet.blit(font_sm.render("3-LAYER crown: 5-skull arc (top) + tiara-band (brow) + rearing naga-hood (centre). Amber 3-eye wins.", True, LABEL_DIM), (14, 646))

    # === (b) PILLAR assembled — mirrored, from the sister's own forms =========
    pcx = 430
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 82))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 82 + 250 + 92))
    pygame.draw.rect(sheet, (58, 66, 62), (pcx + 8, 82 + 250, 134, 92))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 82 + 250 + 38))
    sheet.blit(font.render("Pillar — the coiling naga", True, LABEL), (pcx - 4, 682))
    sheet.blit(font_sm.render("a winding dark-jade snake (alternating scale-", True, LABEL_DIM), (pcx - 4, 706))
    sheet.blit(font_sm.render("value segments) = shaft; rearing naga-hood +", True, LABEL_DIM), (pcx - 4, 722))
    sheet.blit(font_sm.render("kapala cup caps the gap (mirrored, on-axis)", True, LABEL_DIM), (pcx - 4, 738))

    # === (c) TRUE 32px chips (day + night) + blackout proof + palette =========
    panel_x = 624
    pygame.draw.rect(sheet, PANEL, (panel_x, 82, W - panel_x - 14, 604))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 92))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_naga_kapali(big, 48 * SS, 50 * SS, (32 / 134.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 124
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, night_y + 27))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # 32px pillar chip beside, on both skies
    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
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

    # blackout / silhouette proof — fill the alpha mask flat to read the shape
    sheet.blit(font.render("Silhouette proof", True, LABEL), (panel_x + 16, night_y + 178))
    sil_y = night_y + 198
    big_sil = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
    draw_naga_kapali(big_sil, 48 * SS, 50 * SS, (40 / 134.0) * SS)
    sil_small = pygame.transform.smoothscale(big_sil, (120, 120))
    mask = pygame.mask.from_surface(sil_small)
    sil = mask.to_surface(setcolor=(20, 22, 24, 255), unsetcolor=(0, 0, 0, 0))
    vgrad(sheet, (panel_x + 20, sil_y, 120, 120), (196, 200, 206), (150, 156, 164))
    pygame.draw.rect(sheet, INK, (panel_x + 20, sil_y, 120, 120), 1)
    sheet.blit(sil, (panel_x + 20, sil_y))
    sheet.blit(font_sm.render("6-arm fan + diagonal", True, LABEL_DIM), (panel_x + 150, sil_y + 40))
    sheet.blit(font_sm.render("thread + naga-hood read", True, LABEL_DIM), (panel_x + 150, sil_y + 56))

    # palette strip
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, sil_y + 132))
    swatches = [
        (BONE, "warm bone"), (BONE_CR, "crown-skull (dimmest)"),
        (JADE_CAR, "jade thread-carrier"), (JADE_D, "deep jade"),
        (VERD, "verdigris snake"), (GOLD, "gold cup-rim"),
        (AMBER, "amber third-eye"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, sil_y + 158
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 192
        ry = syp + row * 24
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    # bottom note strip
    pygame.draw.rect(sheet, PANEL, (14, 800, W - 28, 44))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=8 supersample -> smoothscale + standalone 1024px hero export.  STAY: flat fills · "
        "hard ink keyline (28,22,26) · dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 815))
    sheet.blit(font_sm.render(
        "VALUE LADDER: amber third-eye (brightest) -> 6 palm-skulls (mid) -> crown skulls (dimmest).  "
        "32px CARRIER: the bold dark-jade FULL-TORSO diagonal naga-thread (shoulder->opposite hip->thigh) + the dark naga-hood crown.",
        True, LABEL_DIM), (26, 831))

    out = os.path.join(here, "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
