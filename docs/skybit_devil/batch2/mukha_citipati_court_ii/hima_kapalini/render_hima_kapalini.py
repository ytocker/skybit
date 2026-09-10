"""
Round-1 concept renderer for HIMA-KAPALINI — the hoar-frost crystal mother,
sister #5 of the mukha_citipati_court_ii brood (charnel-ascetic / mountain-cave
register). Headless Pygame; ELEVATED pipeline (supersample SS=8 → smoothscale)
so the matte ice-shard sheathing and the six palm-skulls stay crisp at downscale.
Keeps the shipped house grammar: flat saturated fills, hard 1-2px ink keyline
(28,22,26), dark-core → flat-fill → top-left rim-sheen triad, 1px alpha-grown
outline, chibi proportions, scary-CUTE; procedural-only (no gradients/PNGs).

WHY this sister is the frost mother: she fuses the Mukha-Devi SIX-ARM radial fan
(every palm an open hand cradling a TINY SKULL) onto the MUKHA squat rib-barrel
+ wide 6-petal lotus base. Her ornament SET is RIME ICE — not hoar-frost: an
opaque, milky, lumpy, plaster-like sheathing with a rough sugar texture. That is
the whole distinctness play vs Bismuth / Amethyst / Opal (cut, polished, faceted
GEM crystal): the shards here are ABSOLUTELY MATTE — irregular, frost-rimed,
with NO facet planes, NO refraction/rainbow, NO geometric regularity, and NO
specular glint (any glint would collide with the cut-gem sisters). The bone is
sheathed in these rough ice masses; the shoulder/rib shard clusters route
BETWEEN the six arms so all six palm-skulls stay legible.

WHY frost-white + slate-blue + DRIED-BLOOD PLUM: the cold-blue palette zone is
the most crowded in the whole roster (asthi / Obsidian / Verdigris / Starlit /
Opal / Bismuth / Lapis). The single thing that saves this sister is the plum — a
DELIBERATE, VISIBLE second note: a plum lip, a plum prayer-cord wrap, and plum
socket-shadows. The brood-read must be "frost + a wound of dried blood," and the
warm-dark plum is the colour-tell that survives the downscale because it is the
only warm mark in an otherwise cold field.

WHY the matte ice-shard CROWN-CLUSTER rises from BEHIND: the fused crown is the
Citipati 5-skull arc-sweep AND the Mukha tiara-band, TOGETHER and FRONTMOST. The
upthrust shard cluster springs from behind the centre skull and never swallows
the arc — three layers read top-to-bottom: shard cluster (back), skull-arc +
band (front).

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

# ── PINNED PALETTE (locked brief: frost-white + slate-blue + dried-blood plum) ─
# Frost-white bone is the dominant cold MASS; everything reads cold EXCEPT the
# plum, which is the deliberate warm-dark wound that separates this sister from
# the crowded cold-blue zone.
BONE      = (224, 234, 242)   # frost-white bone (the dominant cold fill)
BONE_D    = (170, 188, 206)   # slate-frost dark-core / shade
BONE_DD   = (112, 134, 158)   # deepest frost hollow (sockets, rib gaps)
BONE_SH   = (244, 250, 254)   # bone top-left rim-sheen (soft, never a hot glint)
# crown skulls one NOTCH DARKER than the body bone — the dimmest rung of the
# value ladder (below the mid-value palm-skulls, far below the third-eye).
BONE_CR   = (182, 200, 216)   # crown-skull frost-bone (dimmest rung)
BONE_CR_D = (130, 152, 174)   # crown-skull shade
# RIME ICE — the matte sheathing. WHY a milky opaque mid-blue (NOT a bright glassy
# cyan, NOT a saturated sapphire): rime is plaster/sugar, opaque and dull, so the
# fill sits a value DOWN from the frost-bone and reads as a rough crust, never a
# polished gem. The "highlight" is a soft frost-rime crumb, never a specular line.
ICE       = (158, 196, 222)   # rime-ice shard body (matte milky slate-blue)
ICE_D     = (108, 148, 182)   # rime-ice shade / underside
ICE_DD    = ( 72, 108, 146)   # deepest rime crevice (the rough crust read)
ICE_FROST = (206, 226, 240)   # soft matte frost-crumb (diffuse, NEVER a glint)
# the CROWN frost-rime pips sit a value DOWN from the arm-shard crumbs so even
# the brightest crown pixel stays dimmer than the mid-value palm-skulls — the
# matte crown must never out-value the cradled skulls (locked value ladder).
ICE_FROST_CR = (170, 198, 220) # crown-spur frost-rime stipple (dim, matte)
# the carrier shard mass is darker/more saturated so the 32px crown cluster +
# shoulder crust survive the smoothscale as a clear cold mass against the sky.
ICE_CAR   = ( 96, 138, 174)   # the 32px ice-shard carrier fill (matte, holds value)
# DRIED-BLOOD PLUM — the deliberate visible second note (lip + cord + sockets).
# WHY a desaturated warm maroon, not a hot red: it must read as old, dried,
# clotted blood — a wound, not a jewel — so it is dark and muddy-warm, and at
# 32px it is the ONE warm pixel cluster in a cold field.
PLUM      = (122,  44,  58)   # dried-blood plum (lip + cord + socket-shadow)
PLUM_BR   = (168,  72,  84)   # plum highlight (still muted, never glossy)
PLUM_D    = ( 78,  26,  40)   # deep plum shade
INK       = ( 28,  22,  26)   # hard ink keyline
# the focal: a pale cyan-white third-eye — the single BRIGHTEST pixel. Cool, so
# it sits in the frost family yet out-values every frost mark by a wide gap.
EYE       = (180, 236, 248)   # pale-cyan third-eye glow
EYE_BR    = (224, 250, 255)   # hottest cyan-white core (single brightest pixel)

BG        = ( 86,  96, 108)   # neutral cool-grey review backdrop
PANEL     = ( 66,  76,  88)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 242, 246)
LABEL_DIM = (190, 200, 210)


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


# ── a single MATTE rime-ice shard (the ornament unit — absolutely no facets) ──
def ice_shard(surf, cx, cy, length, width, ang, s, body=ICE, body_d=ICE_D,
              body_dd=ICE_DD, frost=ICE_FROST, jag=0.30):
    """One rough, lumpy RIME-ice shard pointing along `ang`. WHY built this way
    (the whole distinctness play): the shards must read as OPAQUE rime/plaster —
    irregular, frost-rimed, matte — and NEVER as a cut gem. So each shard is an
    IRREGULAR jagged sliver (no two edges parallel, no clean facet planes), filled
    flat matte, with a DIFFUSE frost crumb at the base and a rough dark crevice
    down one flank. Crucially there is NO specular line, NO bright tip glint, and
    NO rainbow — those would collide with the Bismuth/Amethyst/Opal cut-gem
    sisters. `jag` perturbs the silhouette so the edge stays bumpy/sugar-like.

    The shape is a long lopsided wedge with a kink partway up its longer flank so
    it reads as a snapped, irregular ice spur rather than a regular triangle."""
    ca, sa = math.cos(ang), math.sin(ang)
    # perpendicular unit (for the two base corners + the flank kink)
    px, py = -sa, ca
    tip = (cx + ca * length, cy + sa * length)
    # asymmetric base — one flank wider than the other (irregular, never iso)
    bl = (cx + px * width * (0.62 + jag), cy + py * width * (0.62 + jag))
    br = (cx - px * width * (0.46 + jag * 0.5), cy - py * width * (0.46 + jag * 0.5))
    # a kink partway up the long flank so the edge bends (snapped-spur read)
    kx = cx + ca * length * 0.52 + px * width * (0.30 - jag * 0.6)
    ky = cy + sa * length * 0.52 + py * width * (0.30 - jag * 0.6)
    # a second, lower kink on the other flank — keeps both edges irregular
    k2x = cx + ca * length * 0.34 - px * width * (0.22 + jag * 0.3)
    k2y = cy + sa * length * 0.34 - py * width * (0.22 + jag * 0.3)
    # full lumpy outline: base-left, flank kink, tip, other flank low-kink, base-right
    poly = [(bl[0], bl[1]), (kx, ky), (tip[0], tip[1]), (k2x, k2y), (br[0], br[1])]
    triad_blob(surf, body, poly, ow=max(1, int(1.3 * s)))
    # rough dark crevice down the shaded flank — the OPAQUE crust read, a matte
    # value step (NOT a clean facet edge): a thin irregular wedge of deep crevice.
    crev = [(br[0], br[1]),
            (cx + ca * length * 0.30 - px * width * 0.10,
             cy + sa * length * 0.30 - py * width * 0.10),
            (tip[0], tip[1])]
    pygame.draw.polygon(surf, body_d, crev)
    pygame.draw.polygon(surf, body_dd, [
        (br[0], br[1]),
        (cx + ca * length * 0.16 - px * width * 0.18,
         cy + sa * length * 0.16 - py * width * 0.18),
        (cx + ca * length * 0.55 - px * width * 0.04,
         cy + sa * length * 0.55 - py * width * 0.04)])
    # DIFFUSE frost crumb dusted near the base — a soft matte speckle, never a
    # specular streak. A few small dim dots so it reads as sugar/rime, not gloss.
    if length > 9 * s:
        for fk in range(3):
            ft = 0.18 + fk * 0.16
            fx = cx + ca * length * ft + px * width * (0.10 - fk * 0.08)
            fy = cy + sa * length * ft + py * width * (0.10 - fk * 0.08)
            pygame.draw.circle(surf, frost, (int(fx), int(fy)),
                               max(1, int(width * 0.12)))


# ── an ABSOLUTELY MATTE crown rime-spur (NO facet plane, NO glint) ────────────
def matte_shard(surf, cx, cy, length, width, ang, s, body=ICE_CAR, jag=0.30,
                snap=0.0, notch=False, seed=0, frost=ICE_FROST_CR):
    """One upthrust CROWN rime-spur rendered as flat MATTE accreted ice — the
    fix for the round-1 facet collision. WHY no internal value planes: a clean
    light-to-dark ridge running tip-to-base reads as a CUT crystal facet (the
    Bismuth/Amethyst/Opal grammar). So this spur has exactly ONE flat slate-blue
    fill, an irregular lumpy outline, and the SAME scattered pale frost-rime pips
    used on the arm shards — clustered dense at the base/edges and thinning to
    the tip — and NOTHING else: no crevice wedge, no directional sheen, no tip
    glint, no specular dot. `snap` lops the tip flat (a broken spur); `notch`
    bites a step out of one flank; `seed` drives a deterministic stipple scatter
    so the rime crumbs look accreted, never gridded."""
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca
    # tip is either a point or, when snapped, a short flat broken edge
    if snap > 0.0:
        tlen = length * (1.0 - snap)
        ta = (cx + ca * tlen + px * width * 0.30, cy + sa * tlen + py * width * 0.30)
        tb = (cx + ca * tlen * 0.92 - px * width * 0.24,
              cy + sa * tlen * 0.92 - py * width * 0.24)
    else:
        tip = (cx + ca * length, cy + sa * length)
    bl = (cx + px * width * (0.66 + jag), cy + py * width * (0.66 + jag))
    br = (cx - px * width * (0.48 + jag * 0.5), cy - py * width * (0.48 + jag * 0.5))
    # irregular kinks up each flank so no edge is a straight facet line
    kx = cx + ca * length * 0.50 + px * width * (0.34 - jag * 0.6)
    ky = cy + sa * length * 0.50 + py * width * (0.34 - jag * 0.6)
    k2x = cx + ca * length * 0.30 - px * width * (0.26 + jag * 0.3)
    k2y = cy + sa * length * 0.30 - py * width * (0.26 + jag * 0.3)
    poly = [(bl[0], bl[1]), (kx, ky)]
    if notch:
        # bite a stepped notch out of the upper long flank (broken accretion)
        nx = cx + ca * length * 0.70 + px * width * 0.06
        ny = cy + sa * length * 0.70 + py * width * 0.06
        nx2 = cx + ca * length * 0.66 + px * width * 0.26
        ny2 = cy + sa * length * 0.66 + py * width * 0.26
        poly += [(nx2, ny2), (nx, ny)]
    if snap > 0.0:
        poly += [(ta[0], ta[1]), (tb[0], tb[1])]
    else:
        poly += [(tip[0], tip[1])]
    poly += [(k2x, k2y), (br[0], br[1])]
    # ONE flat fill + the house ink keyline — no core, no sheen plane
    triad_blob(surf, body, poly, ow=max(1, int(1.3 * s)))
    # FROST-RIME STIPPLE: scattered pale pips, dense at base/edges, fading up —
    # the only texture, identical in character to the arm-shard frost crumbs.
    npip = max(4, int(length / (3.0 * s)))
    for fk in range(npip):
        t = fk / max(1, npip - 1)
        # bias the scatter toward the base so the tip stays clean/dim
        ft = 0.10 + (t * t) * 0.74
        # deterministic lateral wobble (no RNG → reproducible across targets)
        w = math.sin(fk * 2.114 + seed * 1.7) * (0.52 - 0.30 * t)
        fx = cx + ca * length * ft + px * width * w
        fy = cy + sa * length * ft + py * width * w
        rr = max(1, int(width * (0.16 - 0.09 * t)))
        pygame.draw.circle(surf, frost, (int(fx), int(fy)), rr)


def ice_cluster(surf, cx, cy, base_ang, spread, n, scale_len, scale_w, s,
                carrier=False):
    """A fan of MATTE rime shards sprouting from a point — the sheathing crust.
    WHY irregular lengths/angles (no regularity): a real rime crust is a clump of
    uneven spurs, so each shard varies in length, width, and jag. `carrier=True`
    uses the darker ICE_CAR fill so the crown cluster + shoulder crust hold a cold
    mass at 32px. Returns nothing — purely decorative crust."""
    body = ICE_CAR if carrier else ICE
    body_d = ICE_DD if carrier else ICE_D
    # deterministic-but-irregular jitter from the index (no RNG → reproducible)
    for i in range(n):
        t = i / max(1, n - 1)
        a = base_ang + (t - 0.5) * spread
        # irregular wobble per shard so the fan is lumpy, not a clean radial
        wob = math.sin(i * 2.399) * 0.16
        a += wob
        L = scale_len * (0.7 + 0.6 * abs(math.sin(i * 1.7 + 0.5)))
        W = scale_w * (0.7 + 0.5 * abs(math.cos(i * 2.1)))
        jag = 0.22 + 0.18 * abs(math.sin(i * 3.1))
        ice_shard(surf, cx, cy, L, W, a, s, body=body, body_d=body_d,
                  body_dd=ICE_DD, frost=ICE_FROST, jag=jag)


# ── a single ornamental crown-skull (cloned from Citipati crown_skull) ────────
def crown_skull(surf, cx, cy, r, s, lit=False, bone=BONE):
    """Tiny bone skull — domed cranium, two dark sockets, a stub jaw. `lit` swaps
    the eye-pins to pale-cyan for the crown-centre skull (the only crown glow).
    `bone` lets the arc skulls render a NOTCH DARKER (BONE_CR) so they sit at the
    dimmest rung of the value ladder."""
    triad_circle(surf, bone, (cx, cy), r, ow=max(1, int(1.6 * s)), core=False)
    jaw = [(cx - int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.34), cy + int(r * 1.0)),
           (cx - int(r * 0.34), cy + int(r * 1.0))]
    triad_blob(surf, bone, jaw, ow=max(1, int(1.2 * s)))
    eye_c = EYE_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        # WHY a faint plum socket-shadow even on crown skulls: the dried-blood note
        # must recur subtly across the figure (lip + cord + sockets), so the void
        # carries a thin plum ring — the wound read echoes into the crown.
        pygame.draw.circle(surf, PLUM_D, (ex, cy + int(r * 0.04)), max(1, int(r * 0.27)))
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.22)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.04)), max(1, int(r * 0.13)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))
    pygame.draw.line(surf, INK,
                     (cx - int(r * 0.34), cy + int(r * 0.70)),
                     (cx + int(r * 0.34), cy + int(r * 0.70)),
                     max(1, int(1.2 * s)))


# ── a tiny palm-skull cradled in an open hand (the brood motif) ───────────────
def palm_skull(surf, hx, hy, r, s, ang):
    """An OPEN palm cradling a TINY SKULL — the locked brood motif. The five
    fingers fan from the wrist; the skull rests in the cup. Mid-value: palm-skulls
    sit BELOW the third-eye and ABOVE the crown skulls on the value ladder."""
    fingers = []
    for k in range(-2, 3):
        fa = ang + math.radians(k * 22)
        fingers.append((hx + math.cos(fa) * r * 1.45, hy + math.sin(fa) * r * 1.45))
    palm = [(hx + math.cos(ang + math.pi) * r * 0.7,
             hy + math.sin(ang + math.pi) * r * 0.7)] + fingers
    triad_blob(surf, BONE, palm, ow=max(1, int(1.2 * s)))
    for fa_k in range(-2, 3):
        fa = ang + math.radians(fa_k * 22)
        base = (hx + math.cos(ang) * r * 0.3, hy + math.sin(ang) * r * 0.3)
        tip = (hx + math.cos(fa) * r * 1.5, hy + math.sin(fa) * r * 1.5)
        pygame.draw.line(surf, BONE_DD, base, tip, max(1, int(1.0 * s)))
    # the cradled tiny skull — seated dead-centre on the wrist so all six punch
    # the same mid-value frost-bone shape.
    sk = (int(hx), int(hy))
    sr = int(r * 0.92)
    triad_circle(surf, BONE, sk, sr, ow=max(1, int(1.5 * s)), core=False)
    for ex in (-1, 1):
        # faint plum socket-shadow ring so the dried-blood note recurs on the palms
        pygame.draw.circle(surf, PLUM_D,
                           (sk[0] + ex * int(sr * 0.34), sk[1] - int(sr * 0.06)),
                           max(1, int(sr * 0.28)))
        pygame.draw.circle(surf, INK,
                           (sk[0] + ex * int(sr * 0.34), sk[1] - int(sr * 0.06)),
                           max(1, int(sr * 0.22)))
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
    centres + their outward angles for palm-skull placement, AND the six elbow
    points so the shoulder/rib shard crust can route BETWEEN the arms."""
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
    elbows = []
    for sgn, d, a in order:
        sh = (shoulder[0] + sgn * int(hr * 0.55), shoulder[1])
        # WHY the LOWEST pair (100°) reaches further: at 32px the two lowest palm-
        # skulls fused into the cord/torso mass. Extending their arms outward (and
        # the elbow's lateral cock) walks those two skulls clear of the centre so
        # all SIX read separately at gameplay scale.
        al = arm_len * (1.16 if d == 100 else 1.0)
        elbow = (sh[0] + math.cos(a) * al * 0.52 + sgn * (int(hr * 0.16) if d == 100 else 0),
                 sh[1] + math.sin(a) * al * 0.52)
        hand = (sh[0] + math.cos(a) * al + sgn * (int(hr * 0.10) if d == 100 else 0),
                sh[1] + math.sin(a) * al)
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
        elbows.append((sgn, d, sh, elbow, a))
    hands.sort(key=lambda h: (h[0], -h[1]))
    elbows.sort(key=lambda h: (h[0], -h[1]))
    return ([(int(h[2][0]), int(h[2][1]), h[3]) for h in hands],
            [(int(e[2][0]), int(e[2][1]), int(e[3][0]), int(e[3][1]), e[4],
              e[1]) for e in elbows])


# ── the hoar-frost crystal mother (MUKHA body) ────────────────────────────────
def draw_hima_kapalini(surf, cx, cy, s):
    """Squat chibi MUKHA bone-mother on a wide 6-petal lotus base, under a Mukha
    SIX-ARM radial fan; each open palm cradles a tiny skull. Her bone is sheathed
    in MATTE rime-ice shard crust (shoulder + rib clusters routed BETWEEN the
    arms), with a dried-blood PLUM lip + prayer-cord + socket-shadows as the warm
    second note. The fused crown = 5-skull arc + tiara-band (frontmost), with an
    upthrust matte ice-shard cluster rising from BEHIND. A pale-cyan third-eye is
    the single brightest pixel. `s` = unit around a ~130-unit figure."""

    # vertical anchors (MUKHA: BIG head over a SHORT torso + wide lotus base)
    head_c = (cx, cy - int(28 * s))
    hr = int(32 * s)

    # === SIX-ARM RADIAL FAN (drawn first → arms sit BEHIND torso & head) ======
    hands, elbows = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.82), s, hr)

    # === RIB-SHARD CRUST routed BETWEEN the arms (drawn behind the torso) ======
    # WHY between the arms: the locked rule says costume mass must not occlude the
    # palm-skulls, so the rime crust sprouts from the shoulder line in the GAPS
    # between adjacent arm origins, pointing outward along the inter-arm angle.
    sh_y = head_c[1] + int(hr * 0.82)
    # the three inter-arm gap directions per side (between the 100/64/28° arms)
    for sgn in (-1, 1):
        for gap_deg in (82, 46):
            a = math.radians(-90 + sgn * gap_deg)
            ox = head_c[0] + sgn * int(hr * 0.62) + math.cos(a) * int(hr * 0.55)
            oy = sh_y + math.sin(a) * int(hr * 0.55)
            ice_cluster(surf, ox, oy, a, math.radians(40), 3,
                        int(hr * 0.7), int(8 * s), s, carrier=False)

    # === LOWER BODY — wide squat 6-petal LOTUS base (MUKHA, keeps mass low) ====
    base_y = cy + int(42 * s)
    base = [(cx - int(34 * s), base_y - int(7 * s)),
            (cx - int(24 * s), base_y - int(15 * s)),
            (cx + int(24 * s), base_y - int(15 * s)),
            (cx + int(34 * s), base_y - int(7 * s)),
            (cx + int(27 * s), base_y + int(11 * s)),
            (cx - int(27 * s), base_y + int(11 * s))]
    triad_blob(surf, BONE, base,
               core_pts=[(cx, base_y - int(14 * s)), (cx + int(28 * s), base_y - int(7 * s)),
                         (cx + int(22 * s), base_y + int(9 * s)), (cx, base_y + int(7 * s))],
               ow=max(1, int(1.6 * s)))
    # lotus petal grooves
    for k in range(-2, 3):
        px = cx + int(k * 11 * s)
        pygame.draw.line(surf, BONE_DD, (px, base_y - int(15 * s)),
                         (px, base_y + int(8 * s)), max(1, int(1.4 * s)))
    # rime-ice rime along the lotus rim — short matte spurs hugging the petals so
    # the base reads frost-encrusted, not bare bone.
    for k in range(-2, 3):
        px = cx + int(k * 13 * s)
        ice_shard(surf, px, base_y - int(15 * s), int(11 * s), int(6 * s),
                  math.radians(-90 + k * 12), s, jag=0.26)
    # a plum seed at the lotus heart — kept deeper than the third eye so it stays
    # a SECONDARY focal (the dried-blood note recurring low on the figure).
    pygame.draw.circle(surf, PLUM_D, (cx, base_y - int(3 * s)), int(5 * s))
    pygame.draw.circle(surf, PLUM, (cx - int(1 * s), base_y - int(4 * s)), max(1, int(2 * s)))

    # === TORSO — a SHORT rib barrel (squat MUKHA proportion) ==================
    rc_cx, rc_cy = cx, cy + int(12 * s)
    rc_w, rc_h = int(32 * s), int(24 * s)
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.42), rc_cy + rc_h // 2)]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(4 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(2 * s))],
               ow=max(1, int(1.8 * s)))
    # hard rib bands
    for i in range(2):
        ry = rc_cy - rc_h // 2 + int(7 * s) + i * int(8 * s)
        bw = int(rc_w * (0.42 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(6 * s), bw * 2, int(14 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.2 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(5 * s)),
                     (rc_cx, rc_cy + int(3 * s)), max(1, int(2 * s)))

    # === RIME-ICE SHEATHING over the ribcage — matte crust climbing the cage ==
    # WHY a low crust hugging the torso flanks (not a mass over the chest): the
    # ice sheathes the bone, so short irregular spurs grow UP the cage sides; the
    # plum cord crosses on top so the wound-note is read against the frost crust.
    for sgn in (-1, 1):
        ice_cluster(surf, rc_cx + sgn * int(rc_w * 0.40), rc_cy + int(2 * s),
                    math.radians(-90 + sgn * 58), math.radians(34), 3,
                    int(13 * s), int(6 * s), s, carrier=False)

    # === PLUM PRAYER-CORD — the dried-blood diagonal wrap (a visible 2nd note) ==
    # WHY a thick plum cord across the cage + a knot tail: the plum must be a
    # deliberate, legible second note, not a sliver — so it is a fat dried-blood
    # band crossing the frost torso, the clearest warm mark on the figure.
    cord = [(rc_cx - int(rc_w * 0.5), rc_cy - int(rc_h * 0.28)),
            (rc_cx + int(rc_w * 0.12), rc_cy + int(2 * s)),
            (rc_cx + int(rc_w * 0.5), rc_cy + int(rc_h * 0.30))]
    # WHY a FATTER continuous cord (min ~2px at 32px): the dried-blood diagonal is
    # half the "wound" read and must survive downscale on the DAY chip as a solid
    # line, never a dotted dim trail. The PLUM core is floored so it holds at 32px.
    pygame.draw.lines(surf, INK, False, cord, max(3, int(11 * s)))
    pygame.draw.lines(surf, PLUM, False, cord, max(2, int(8 * s)))
    pygame.draw.lines(surf, PLUM_BR, False, cord[:2], max(1, int(2 * s)))
    # a plum tassel knot where the cord meets the lower cage
    triad_circle(surf, PLUM, (rc_cx + int(rc_w * 0.5), rc_cy + int(rc_h * 0.30)),
                 max(2, int(4 * s)), ow=max(1, int(1.2 * s)), core=False)
    for tk in (-1, 0, 1):
        tx = rc_cx + int(rc_w * 0.5) + tk * int(3 * s)
        pygame.draw.line(surf, PLUM_D,
                         (rc_cx + int(rc_w * 0.5), rc_cy + int(rc_h * 0.30)),
                         (tx, rc_cy + int(rc_h * 0.30) + int(10 * s)), max(1, int(2 * s)))

    # === SIX PALM-SKULLS — one cradled in each open hand (the brood motif) ====
    for (hx, hy, a) in hands:
        palm_skull(surf, hx, hy, int(9 * s), s, a)

    # === SKULL HEAD — chibi, scary-cute, pale-cyan third eye (the framed FACE) =
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two lower sockets — rimmed bone void with a DRIED-BLOOD PLUM shadow ring so
    # the wound-note reads on the face itself. Kept dimmer than the cyan third-eye
    # (no hot core) so the focal clearly tops the value ladder at 32px.
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, BONE_D, (ex, ey), int(hr * 0.235))
        pygame.draw.circle(surf, PLUM_D, (ex, ey), int(hr * 0.20))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.15))
        pygame.draw.circle(surf, PLUM, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           max(1, int(hr * 0.06)))
    # THIRD EYE — the single BRIGHTEST pixel: a vertical pale-cyan slit on the brow
    tex, tey = head_c[0], head_c[1] - int(hr * 0.34)
    pygame.draw.ellipse(surf, INK, (tex - int(7 * s), tey - int(9 * s), int(14 * s), int(18 * s)))
    pygame.draw.ellipse(surf, EYE, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, EYE_BR, (tex - int(4 * s), tey - int(5 * s), int(8 * s), int(10 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(2 * s)),
                       max(2, int(3.0 * s)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    # === PLUM LIP — the dried-blood mouth (the loudest, clearest warm note) ====
    # WHY a filled plum lip instead of a bare tooth line: the brood-read is "frost
    # + a wound of dried blood," so the mouth IS the wound — a dark dried-blood lip
    # band with a few frost-bone teeth biting through it. The single largest warm
    # mark on the face, central, so it survives the downscale.
    # WHY a FULLER lip BLOCK (≈2-3px tall at 32px): round-1's lip nearly dropped on
    # the busy DAY chip, leaving the figure reading cool-monochrome (the crowded
    # cold-blue failure mode). The lip is now a taller solid dried-blood block, and
    # the frost-bone teeth are FEWER + only bite the LOWER half — so even at 32px a
    # continuous plum band survives across the top, the single loudest warm note.
    my = head_c[1] + int(hr * 0.70)
    lip = [(head_c[0] - int(hr * 0.52), my - int(hr * 0.08)),
           (head_c[0] + int(hr * 0.52), my - int(hr * 0.08)),
           (head_c[0] + int(hr * 0.44), my + int(hr * 0.26)),
           (head_c[0] - int(hr * 0.44), my + int(hr * 0.26))]
    triad_blob(surf, PLUM, lip, ow=max(1, int(1.4 * s)))
    pygame.draw.line(surf, PLUM_BR, (head_c[0] - int(hr * 0.44), my - int(hr * 0.04)),
                     (head_c[0] + int(hr * 0.12), my - int(hr * 0.04)), max(1, int(1.6 * s)))
    # fewer frost-bone teeth, biting only the lower band so the plum top survives
    for k in (-2, 0, 2):
        tx = head_c[0] + int(k * hr * 0.18)
        pygame.draw.line(surf, BONE_SH, (tx, my + int(hr * 0.06)),
                         (tx, my + int(hr * 0.24)), max(1, int(1.6 * s)))
    # two small fangs at the corners (wrathful tell)
    for sgn in (-1, 1):
        fx = head_c[0] + sgn * int(hr * 0.42)
        pygame.draw.polygon(surf, BONE_SH,
                            [(fx - int(2 * s), my), (fx + int(2 * s), my),
                             (fx, my + int(hr * 0.24))])

    # === FUSED CROWN: shard cluster (back) + 5-skull arc + tiara-band (front) ==
    # WHY a strict back-to-front order (the locked rule): the upthrust ice-shard
    # cluster is drawn FIRST so it rises from BEHIND; then the gold tiara-band on
    # the brow, then the wide Citipati 5-skull arc-sweep riding the OUTER arc so
    # every dome is countable and the arc reads FRONTMOST. The shard cluster must
    # NOT swallow the arc — it is sized to peek up BETWEEN and ABOVE the skulls.
    # -- (0) upthrust ABSOLUTELY-MATTE rime CROWN-CLUSTER rising from BEHIND --
    # WHY matte_shard (NOT ice_shard) here: round-1's crown spurs carried a
    # tip-to-base crevice plane that read as a CUT facet (the gem collision). The
    # crown is now flat slate fill + frost-rime stipple only — the same matte
    # material as the arm shards. WHY irregular & hand-placed: rime is ACCRETED &
    # broken, not a symmetric grown crystal, so each spur differs in length /
    # width / angle, two clump together, one leans off-axis, and a couple are
    # snapped or notched. The carrier fill keeps the cluster a clear cold mass at
    # 32px (the 32px tell), peeking up BETWEEN and ABOVE the skull arc.
    cl_cx, cl_cy = head_c[0], head_c[1] - int(hr * 1.06)
    # (length-mult, width-mult, angle°, jag, snap, notch, x-nudge, y-nudge, seed)
    # WHY fatter spurs + a tighter near-vertical spread: round-1's facet-fix left
    # them spindly/twig-like. Rime accretes into a chunky upthrust CREST, so the
    # spurs are now wide wedges clustered close to vertical, two clumping into the
    # tallest core, one leaning well off-axis — a dense cold mass, still irregular
    # and broken (snaps/notch), still absolutely matte.
    crown_spurs = [
        (1.46, 1.55, -90, 0.16, 0.00, False, 0.0, 0.00, 1),  # tallest core
        (1.30, 1.35, -82, 0.20, 0.00, False, 0.06, 0.04, 6),  # clumps w/ tallest
        (1.18, 1.20, -100, 0.18, 0.18, False, -0.05, 0.04, 2),  # snapped, clumps
        (1.06, 1.30, -72, 0.22, 0.00, True, 0.14, 0.10, 3),  # notched, right
        (1.00, 1.15, -110, 0.24, 0.00, False, -0.16, 0.10, 5),  # left mid
        (0.78, 1.05, -56, 0.30, 0.20, False, 0.26, 0.20, 4),  # short lean right
        (0.86, 1.00, -124, 0.30, 0.00, False, -0.30, 0.22, 7),  # the off-axis lean
        (0.66, 0.92, -44, 0.34, 0.16, False, 0.34, 0.30, 8),  # stubby outer snap
    ]
    for (lm, wm, deg, jg, snp, ntc, nx, ny, sd) in crown_spurs:
        ox = cl_cx + int(hr * nx)
        oy = cl_cy + int(hr * ny)
        matte_shard(surf, ox, oy, int(hr * lm), int(11 * s * wm),
                    math.radians(deg), s, body=ICE_CAR, jag=jg, snap=snp,
                    notch=ntc, seed=sd)

    # -- (1) the Mukha tiara-band (gold→frost-silver, seated LOW on the brow) --
    # WHY silver-frost not gold: in a frost palette a warm gold band would steal
    # the plum's job as the warm note, so the band is a cold frost-silver value
    # step, keeping the plum the sole warm mark.
    tiara_r = int(hr * 1.06)
    band_pts = []
    for i in range(13):
        a = math.radians(220 + i * (100 / 12))
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    # WHY a SLATE value-step (BONE_DD), not a thin pale line: round-1's band sat
    # at near-forehead value and vanished into the frost-white brow. The band is
    # now a fat darker-slate arc with a crisp deep-frost LOWER edge so it reads as
    # a distinct frontmost BAND across the brow (the locked Mukha tiara), then a
    # mid-slate top face + a thin sheen so it still reads as carved bone.
    pygame.draw.lines(surf, INK, False, band_pts, int(9 * s))
    pygame.draw.lines(surf, BONE_DD, False, band_pts, int(6 * s))   # slate step
    pygame.draw.lines(surf, BONE_D, False, band_pts, max(2, int(3 * s)))
    pygame.draw.lines(surf, BONE_SH, False, band_pts[:7], max(1, int(1.4 * s)))
    # tiny frost prongs between the skull seats (Mukha-band tell, hero-only)
    for i in range(13):
        if i % 3 != 1:
            continue
        a = math.radians(220 + i * (100 / 12))
        px = head_c[0] + math.cos(a) * tiara_r
        py = head_c[1] + math.sin(a) * tiara_r
        pygame.draw.line(surf, BONE_SH, (px, py),
                         (px + math.cos(a) * int(5 * s), py + math.sin(a) * int(5 * s)),
                         max(1, int(2 * s)))
    # -- (2) the Citipati 5-skull arc-sweep (WIDE, rides OUTSIDE the band) --
    skull_cr = hr * 1.58
    skull_r = int(hr * 0.36)
    skull_pos = []
    for i in range(5):
        a = math.radians(206 + i * (128 / 4))
        sx = head_c[0] + math.cos(a) * skull_cr
        sy = head_c[1] + math.sin(a) * skull_cr
        skull_pos.append((int(sx), int(sy)))
    for i in (0, 1, 3, 4):
        crown_skull(surf, skull_pos[i][0], skull_pos[i][1], skull_r, s,
                    lit=False, bone=BONE_CR)
    # centre skull last, lit cyan (the only crown glow — drawn value, not bloom)
    cx_c, cy_c = skull_pos[2]
    crown_skull(surf, cx_c, cy_c, skull_r, s, lit=True, bone=BONE_CR)


# ── the rime-ice shard shaft → pillar mirror (built from the sister's own forms) ─
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The RIME-ICE column itself IS the pillar: a stacked spine of bone vertebra
    nodes SHEATHED in matte rime-ice shard clusters — the same crust that
    sheathes the figure, tiling down the shaft. The gap end rears into the
    upthrust ice-shard CROWN-CLUSTER over a single crown-skull, with a plum cord
    band — the creature-derived gap cap, mirrored top↔bottom on the axis. The bold
    cold ICE_CAR shard mass + the plum band are the pillar's 32px carriers,
    mirroring the figure's frost crust + dried-blood note.

    `cap` names the END that faces the GAP."""
    cap_room = int(40 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    node_pitch = int(22 * s)
    shaft_w = int(13 * s)
    # central ink rod the nodes thread onto
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))
    y = b0
    idx = 0
    while y <= b1:
        # a bone vertebra node
        bw = shaft_w
        node = [(cx - bw, y + int(2 * s)),
                (cx - int(bw * 0.5), y - int(7 * s)),
                (cx + int(bw * 0.5), y - int(7 * s)),
                (cx + bw, y + int(2 * s)),
                (cx + int(bw * 0.5), y + int(11 * s)),
                (cx - int(bw * 0.5), y + int(11 * s))]
        triad_blob(surf, BONE, node,
                   core_pts=[(cx, y - int(1 * s)), (cx + bw, y + int(2 * s)),
                             (cx + int(bw * 0.5), y + int(11 * s)), (cx, y + int(9 * s))],
                   ow=max(1, int(1.4 * s)))
        pygame.draw.circle(surf, BONE_DD, (cx, y + int(2 * s)), int(4 * s))
        # rime-ice shard clusters sheathing the node — sprout off alternating
        # sides so the shaft reads as a frost-encrusted spine (the carrier mass).
        side = -1 if (idx % 2 == 0) else 1
        ice_cluster(surf, cx + side * int(bw * 0.7), y + int(2 * s),
                    math.radians(0 if side > 0 else 180), math.radians(70), 3,
                    int(15 * s), int(7 * s), s, carrier=True)
        # a small upward frost spur on the other flank (keeps both sides crusted)
        ice_shard(surf, cx - side * int(bw * 0.5), y - int(4 * s),
                  int(11 * s), int(6 * s), math.radians(-90 - side * 20), s,
                  body=ICE, body_d=ICE_D, jag=0.26)
        # a thin plum cord tick wrapping the node (the dried-blood note on the shaft)
        pygame.draw.line(surf, PLUM, (cx - bw, y + int(8 * s)),
                         (cx + bw, y + int(6 * s)), max(2, int(2.4 * s)))
        idx += 1
        y += node_pitch

    # === gap-edge cap: upthrust ice-shard crown-cluster + crown-skull + plum ===
    cap_y = (bot - int(22 * s)) if cap == "bottom" else (top + int(22 * s))
    grow = +1 if cap == "bottom" else -1
    # the MATTE rime-spur cap fans toward the gap (mirrors the figure's crown) —
    # same flat-fill + frost-stipple material as the head crest, irregular spurs.
    cl_y = cap_y + grow * int(6 * s)
    base_deg = 90 if grow > 0 else -90
    cap_spurs = [(1.00, 1.0, -52, 0.18, 0.00, False, 11),
                 (0.74, 0.8, -24, 0.26, 0.16, False, 12),
                 (0.88, 0.9, 0, 0.20, 0.00, True, 13),
                 (0.70, 0.8, 24, 0.30, 0.00, False, 14),
                 (0.96, 0.9, 52, 0.18, 0.20, False, 15)]
    for (lm, wm, off, jg, snp, ntc, sd) in cap_spurs:
        matte_shard(surf, cx, cl_y, int(18 * s * lm), int(8 * s * wm),
                    math.radians(base_deg + off * grow), s, body=ICE_CAR,
                    jag=jg, snap=snp, notch=ntc, seed=sd)
    # a single crown-skull seated at the cluster heart (lit cyan toward the gap)
    crown_skull(surf, cx, cap_y, int(13 * s), s, lit=True, bone=BONE_CR)
    # a plum cord collar where the cap meets the crusted shaft
    collar_y = (cap_y - int(20 * s)) if cap == "bottom" else (cap_y + int(20 * s))
    pygame.draw.rect(surf, INK, (cx - int(11 * s), collar_y - int(3 * s), int(22 * s), int(7 * s)))
    pygame.draw.rect(surf, PLUM, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(5 * s)))
    pygame.draw.rect(surf, PLUM_BR, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(2 * s)))


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
    draw_hima_kapalini(big, draw_cx * SS, draw_cy * SS, scale * SS)
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
    big = pygame.Surface((int(canvas_units * SS), int(256 * SS)), pygame.SRCALPHA)
    draw_hima_kapalini(big, int(canvas_units * 0.5 * SS), int(150 * SS), 1.0 * SS)
    out = pygame.transform.smoothscale(big, (int(canvas_units * 4), 1024))
    out = grow_outline(out, INK + (255,), 2)
    pygame.image.save(out, path)
    print("wrote", path)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    render_hero_png(os.path.join(here, "round_2_hero.png"))

    W, H = 1040, 860
    font_big = _font(30)
    font = _font(17)
    font_sm = _font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("HIMA-KAPALINI", True, LABEL), (24, 12))
    sheet.blit(font_sm.render(
        "hoar-frost crystal mother  ·  MUKHA body + 6-arm fan · MATTE rime-ice shards · "
        "frost-white + slate-blue + DRIED-BLOOD PLUM · pale-cyan third-eye · round 2",
        True, LABEL_DIM), (262, 24))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(370, 500, 185, 250, 1.7)
    sheet.blit(hero, (14, 88))
    sheet.blit(font.render("Creature — hero (SS=8)", True, LABEL), (96, 590))
    sheet.blit(font_sm.render("Mukha 6-arm fan, each open palm cradling a TINY SKULL; squat MUKHA torso + wide lotus base.", True, LABEL_DIM), (14, 614))
    sheet.blit(font_sm.render("ABSOLUTELY MATTE crown rime-spurs — flat slate fill + frost-rime stipple, NO facet ridge / glint; irregular, accreted.", True, LABEL_DIM), (14, 630))
    sheet.blit(font_sm.render("DRIED-BLOOD PLUM lip + cord + socket-shadows = the wound. 3-layer crown: shard cluster (back) + arc + band.", True, LABEL_DIM), (14, 646))

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
    pygame.draw.rect(sheet, (58, 66, 74), (pcx + 8, 82 + 250, 134, 92))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 82 + 250 + 38))
    sheet.blit(font.render("Pillar — the frost spine", True, LABEL), (pcx - 4, 682))
    sheet.blit(font_sm.render("a bone spine sheathed in matte rime-ice shard", True, LABEL_DIM), (pcx - 4, 706))
    sheet.blit(font_sm.render("clusters = shaft; upthrust ice cluster + crown-", True, LABEL_DIM), (pcx - 4, 722))
    sheet.blit(font_sm.render("skull + plum cord caps the gap (mirrored, on-axis)", True, LABEL_DIM), (pcx - 4, 738))

    # === (c) TRUE 32px chips (day + night) + blackout proof + palette =========
    panel_x = 624
    pygame.draw.rect(sheet, PANEL, (panel_x, 82, W - panel_x - 14, 604))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 92))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_hima_kapalini(big, 48 * SS, 50 * SS, (32 / 134.0) * SS)
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
    draw_hima_kapalini(big_sil, 48 * SS, 50 * SS, (40 / 134.0) * SS)
    sil_small = pygame.transform.smoothscale(big_sil, (120, 120))
    mask = pygame.mask.from_surface(sil_small)
    sil = mask.to_surface(setcolor=(20, 22, 24, 255), unsetcolor=(0, 0, 0, 0))
    vgrad(sheet, (panel_x + 20, sil_y, 120, 120), (196, 204, 212), (150, 160, 170))
    pygame.draw.rect(sheet, INK, (panel_x + 20, sil_y, 120, 120), 1)
    sheet.blit(sil, (panel_x + 20, sil_y))
    sheet.blit(font_sm.render("6-arm fan + lotus base", True, LABEL_DIM), (panel_x + 150, sil_y + 40))
    sheet.blit(font_sm.render("+ upthrust shard cluster", True, LABEL_DIM), (panel_x + 150, sil_y + 56))

    # palette strip
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, sil_y + 132))
    swatches = [
        (BONE, "frost-white bone"), (BONE_CR, "crown-skull (dimmest)"),
        (ICE, "rime-ice shard"), (ICE_CAR, "ice carrier (32px)"),
        (PLUM, "dried-blood plum"), (PLUM_D, "deep plum"),
        (EYE, "pale-cyan third-eye"), (INK, "ink keyline"),
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
        "VALUE LADDER: pale-cyan third-eye (brightest) -> 6 palm-skulls (mid) -> crown skulls (dimmest).  MATTE rime (no facets/glint).  "
        "32px CARRIER: the dried-blood PLUM colour-tell (lip+cord) + the upthrust matte ice-shard CROWN cluster.",
        True, LABEL_DIM), (26, 831))

    out = os.path.join(here, "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
