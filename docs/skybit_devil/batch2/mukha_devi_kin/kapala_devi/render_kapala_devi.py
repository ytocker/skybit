"""
Round-1 concept renderer for KAPALA-DEVI — a grounded SISTER of the shipped
Mukha-Devi (six-armed wrathful bone-mother), Mukha-Devi-KIN brood concept #1.
She is NOT a new creature: body, six-arm radial fan, chibi skull-face, rose
third-eye, the LOW 3-skull tiara, palette, and sheet format are CLONED UNCHANGED
from render_mukha_devi.py. Headless Pygame; ELEVATED pipeline (SS=6 supersample
-> smoothscale).

WHY the ONLY edit is the arm-ends: the brood's distinctness lives in the
arm-end ornament SET, not the silhouette. Mukha's two alternating micro-relics
become SIX upturned skull-cups (kapala = skull-bowl): each hand cradles a
rim-up cranium BOWL with a gold rim-band at its mouth and a pooled rose
offering-glow inside. With the kept LOW 3-skull tiara that makes a halo of nine
skulls; the arm-ends literally ARE skulls — the skull-motif push.

WHY the offering-pools are capped a notch BELOW THIRD_BR: the brow third-eye
must stay the SINGLE brightest pixel, so six rim glows must never out-glow the
one focal. The A-B-A-B rhythm is carried by GLOW SIZE alone (A = fat bright
rose pool, B = small deep-rose ember), keeping the cups identical bone shapes so
the read at 32px is an even ring of skulls, not fussy weapons.

WHY skull-cups sit UP with internal glow (vs Mala's down-hanging inert beads):
the kin push-apart — these are offering BOWLS held aloft, evenly spaced, each
lit from within.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (cloned from Mukha-Devi) ───────────────────────────────────
BONE      = (224, 200, 196)   # dusty rose-bone (the dominant fill)
BONE_D    = (168, 134, 138)   # mauve-bone dark-core / shade
BONE_DD   = (120,  90,  98)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (248, 236, 234)   # bone top-left rim-sheen
ROSE      = (232,  86, 150)   # magenta-rose offering GLOW
ROSE_BR   = (255, 160, 200)   # hot offering-glow inner / sheen
ROSE_D    = (160,  40,  86)   # deep-rose shade (B-cup ember)
GOLD      = (224, 182,  84)   # gold rim-band accent
GOLD_BR   = (246, 214, 130)
GOLD_D    = (170, 134,  56)
TEAL      = ( 64, 170, 166)   # teal hairline (upper-pair rims only)
TEAL_BR   = (140, 222, 216)
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = (232,  86, 150)   # third-eye glow (rose so it reads as her power-focus)
THIRD_BR  = (255, 196, 224)   # third-eye hot core — the brightness CEILING for cups

BG        = ( 96,  92, 100)   # neutral grey review backdrop
PANEL     = ( 74,  72,  84)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 236, 240)
LABEL_DIM = (196, 190, 202)


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


# ── a single ornamental tiara-skull (reused for tiara + arm skull-cups) ───────
def tiara_skull(surf, cx, cy, r, s, lit=False):
    """Tiny rose-bone skull for the LOW 3-skull tiara — demonstrably fewer/lower
    than Citipati's 5-skull crown. WHY a domed cranium with two dark dots: it
    must punch a clean bone shape with two sockets at 32px and sit LOW on the
    brow so the face still reads under the arm-starburst."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.94)),
           (cx - int(r * 0.32), cy + int(r * 0.94))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.1 * s)))
    eye_c = ROSE_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.14)))


# ── the six arm-end SKULL-CUPS (the ONLY edit vs Mukha-Devi) ──────────────────
# the brightest a rose offering-pool may reach — a HARD notch under THIRD_BR so
# the brow third-eye stays the single brightest pixel even after smoothscale.
# (lum ~163 vs THIRD_BR's ~213 / the brow white core's 255 — a clear gap.)
POOL_HOT = lerp(ROSE_BR, ROSE_D, 0.30)   # capped hot core for the fat A-pools


def _rim_band(surf, cx, cy, mw, mh, s, ux, uy, teal_rim, kind):
    """Build the GOLD rim-band + pooled rose offering-glow on a canonical
    mouth-up tile, then ROTATE it so the cup mouth opens along the arm's OUTWARD
    vector (ux,uy). WHY rotate vs an axis-aligned ellipse: a near-vertical arm's
    rim must foreshorten along its own angle, or the cup reads as a flat
    front-facing disc instead of an up-facing BOWL (the lower-left horizontal
    cup is the correct reference). In the canonical tile the mouth's 'up' is
    -Y; the ellipse is WIDE (mw) and SHORT (mh) so it already reads foreshortened
    before rotation."""
    pad = int(mw * 0.7) + 4
    tile = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    cxl, cyl = pad, pad
    rim_rect = (cxl - mw // 2, cyl - mh // 2, mw, mh)
    pygame.draw.ellipse(tile, INK, rim_rect, max(2, int(2.2 * s)))
    pygame.draw.ellipse(tile, GOLD, rim_rect, max(1, int(1.8 * s)))
    # GOLD_BR only on the FAR rim-edge (the lit lip of an up-tilted bowl mouth)
    pygame.draw.arc(tile, GOLD_BR, rim_rect,
                    math.radians(200), math.radians(340), max(1, int(1.4 * s)))
    if teal_rim:   # a hairline teal accent on the upper-pair rims ONLY
        pygame.draw.arc(tile, TEAL, rim_rect,
                        math.radians(20), math.radians(160), max(1, int(1.2 * s)))

    # the pooled rose OFFERING-GLOW seated INSIDE the mouth ellipse. A = fat
    # bright pool (capped at POOL_HOT), B = small deep-ROSE_D ember (the A-B-A-B
    # rhythm by glow SIZE + VALUE) — both a clear notch under the brow third-eye.
    if kind % 2 == 0:   # TYPE A — fat bright rose pool
        pw, ph = int(mw * 0.66), int(mh * 0.62)
        pygame.draw.ellipse(tile, ROSE_D, (cxl - pw // 2, cyl - ph // 2, pw, ph))
        pygame.draw.ellipse(tile, ROSE,
                            (cxl - int(pw * 0.34), cyl - int(ph * 0.34),
                             int(pw * 0.68), max(2, int(ph * 0.68))))
        pygame.draw.circle(tile, POOL_HOT, (cxl, cyl), max(1, int(mh * 0.22)))
    else:               # TYPE B — small deep-rose ember
        pw, ph = int(mw * 0.40), int(mh * 0.44)
        pygame.draw.ellipse(tile, ROSE_D, (cxl - pw // 2, cyl - ph // 2, pw, ph))
        pygame.draw.circle(tile, ROSE, (cxl, cyl), max(1, int(mh * 0.16)))

    # rotate the canonical (mouth-up) tile so its -Y opening aligns with (ux,uy)
    deg = math.degrees(math.atan2(-uy, ux)) - 90.0
    rot = pygame.transform.rotate(tile, deg)
    rr = rot.get_rect(center=(int(cx), int(cy)))
    surf.blit(rot, rr.topleft)


def skull_cup(surf, kind, cx, cy, r, s, ang=0.0, teal_rim=False):
    """Draw ONE of the six upturned skull-cups (kapala). WHY a rim-up cranium
    BOWL: it reuses `tiara_skull`'s domed bone cranium as the bowl wall and adds
    a GOLD rim-band at the cup mouth with a pooled rose offering-glow inside, so
    the arm-end literally IS a skull — but held UP as an offering bowl, lit from
    within (vs Mala's inert down-beads).

    WHY the rim foreshortens to the ARM vector: each cup mouth opens away from
    the torso along its own arm, so a near-vertical arm's rim tilts with it and
    reads as an up-facing BOWL, not a flat floating disc.

    WHY the A-B-A-B rhythm rides GLOW SIZE + VALUE (A = fat bright rose pool,
    B = small deep-ROSE_D ember) on otherwise-identical bone domes: at 32px six
    even craniums read as a halo of skulls; the alternating glow gives rhythm
    without fussy per-cup shapes.

    CRITICAL: every offering-pool is capped a clear notch BELOW THIRD_BR
    (POOL_HOT) so the brow third-eye stays the single brightest pixel."""
    gx = cx + int(math.cos(ang) * r * 0.55)
    gy = cy + int(math.sin(ang) * r * 0.55)

    # the cranium bowl — domed bone wall + a stubby jaw chin (a rim-up skull)
    triad_circle(surf, BONE, (gx, gy), int(r * 0.95), ow=max(1, int(1.4 * s)), core=False)
    chin = [(gx - int(r * 0.5), gy + int(r * 0.5)),
            (gx + int(r * 0.5), gy + int(r * 0.5)),
            (gx + int(r * 0.30), gy + int(r * 0.92)),
            (gx - int(r * 0.30), gy + int(r * 0.92))]
    triad_blob(surf, BONE, chin, ow=max(1, int(1.0 * s)))
    # two dark sockets so the bone dome reads unmistakably as a SKULL even at 32px
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (gx + sgn * int(r * 0.36), gy + int(r * 0.12)),
                           max(1, int(r * 0.22)))

    # the cup mouth opens OUTWARD along the arm (away from torso); foreshorten
    # the rim + pool to that vector so vertical arms read as up-facing bowls.
    ox, oy = math.cos(ang), math.sin(ang)
    mouth = (gx + ox * r * 0.46, gy + oy * r * 0.46)
    mw, mh = int(r * 1.5), int(r * 0.72)
    _rim_band(surf, mouth[0], mouth[1], mw, mh, s, ox, oy, teal_rim, kind)


# ── the six-arm radial starburst (the KIND tell — cloned UNCHANGED) ───────────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr, relic_r):
    """Six fat bone arms splay in a wide symmetric STARBURST around the torso —
    the ONLY radial silhouette in the brood. Cloned UNCHANGED from Mukha-Devi:
    arms origin at a low SHOULDER line, topmost pair near-horizontal, spread
    ±100/64/28° off vertical so the fan FRAMES the face. Returns the six hand
    centres for skull-cup placement."""
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
        hands.append((sgn, d, hand))
    hands.sort(key=lambda h: (h[0], -h[1]))
    return [(int(h[2][0]), int(h[2][1]), h[1]) for h in hands]


# ── the wrathful bone-mother ──────────────────────────────────────────────────
def draw_kapala_devi(surf, cx, cy, s):
    """Pint-sized many-armed death-goddess: a tiny chibi torso under a wide
    six-arm radial starburst — but each hand now holds an upturned SKULL-CUP.
    A LOW 3-skull tiara + a glowing rose third eye keep the FACE reading inside
    the fan. `s` = unit scale around a ~130-unit figure."""

    head_c = (cx, cy - int(28 * s))
    hr = int(32 * s)
    cup_r = int(11 * s)   # the skull-cups read a touch larger than Mukha's relics

    # === SIX-ARM RADIAL FAN (drawn first → arms sit BEHIND torso & head) ======
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.82), s, hr, cup_r)

    # === LOWER BODY — a wide squat lotus-base (keeps mass low, not leggy) ======
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
    for k in range(-2, 3):
        px = cx + int(k * 11 * s)
        pygame.draw.line(surf, BONE_DD, (px, base_y - int(15 * s)),
                         (px, base_y + int(8 * s)), max(1, int(1.4 * s)))
    pygame.draw.circle(surf, ROSE_D, (cx, base_y - int(3 * s)), int(5 * s))
    pygame.draw.circle(surf, ROSE, (cx - int(1 * s), base_y - int(4 * s)), max(1, int(2 * s)))

    # === TORSO — a SHORT rib barrel (squat, so head + base hold the mass) =====
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
    for i in range(2):
        ry = rc_cy - rc_h // 2 + int(7 * s) + i * int(8 * s)
        bw = int(rc_w * (0.42 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(6 * s), bw * 2, int(14 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.2 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(5 * s)),
                     (rc_cx, rc_cy + int(3 * s)), max(1, int(2 * s)))
    pygame.draw.line(surf, ROSE, (rc_cx - int(rc_w * 0.42), rc_cy + int(2 * s)),
                     (rc_cx + int(rc_w * 0.42), rc_cy - int(2 * s)), max(1, int(2 * s)))
    pygame.draw.line(surf, ROSE_BR, (rc_cx - int(rc_w * 0.3), rc_cy + int(1 * s)),
                     (rc_cx, rc_cy - int(1 * s)), max(1, int(1 * s)))

    # === SIX SKULL-CUPS — one upturned in each hand (the brood edit) ==========
    # WHY drawn after torso, before head: they ride out at the fan tips so the
    # outer arc reads as six even skull domes; the head overdraws nothing of them.
    # The A-B-A-B rhythm tracks hand order; the upper-pair (largest spread, the
    # two near-horizontal top hands) get the teal-hairline rim accent.
    for i, (hx, hy, d) in enumerate(hands):
        oa = math.atan2(hy - rc_cy, hx - rc_cx)
        skull_cup(surf, i % 2, hx, hy, cup_r, s, ang=oa, teal_rim=(d == 100))

    # === SKULL HEAD — chibi, scary-cute, three-eyed (the framed FACE) =========
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.25))
        pygame.draw.circle(surf, ROSE_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.12))
    # THIRD EYE — the single BRIGHTEST pixel on the whole sprite (hard rule).
    tex, tey = head_c[0], head_c[1] - int(hr * 0.34)
    pygame.draw.ellipse(surf, INK, (tex - int(7 * s), tey - int(9 * s), int(14 * s), int(18 * s)))
    pygame.draw.ellipse(surf, ROSE, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, ROSE_BR, (tex - int(4 * s), tey - int(5 * s), int(8 * s), int(10 * s)))
    pygame.draw.circle(surf, THIRD_BR, (tex - int(1 * s), tey - int(2 * s)), max(2, int(3.2 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(2 * s)),
                       max(1, int(1.6 * s)))
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.48), my),
                     (head_c[0] + int(hr * 0.48), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.15), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.15), my + int(hr * 0.13)), max(1, int(1 * s)))
    for sgn in (-1, 1):
        fx = head_c[0] + sgn * int(hr * 0.40)
        pygame.draw.polygon(surf, BONE_SH,
                            [(fx - int(2 * s), my), (fx + int(2 * s), my),
                             (fx, my + int(hr * 0.22))])

    # === LOW 3-SKULL TIARA (kept UNCHANGED — the tight anchor) ================
    tiara_r = int(hr * 0.96)
    tiara_skull_r = int(hr * 0.30)
    band_pts = []
    for i in range(9):
        a = math.radians(235 + i * (70 / 8))
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(6 * s))
    pygame.draw.lines(surf, GOLD, False, band_pts, int(3 * s))
    pygame.draw.lines(surf, GOLD_BR, False, band_pts[:5], max(1, int(1.2 * s)))
    for i in range(3):
        a = math.radians(242 + i * (56 / 2))
        sx = head_c[0] + math.cos(a) * tiara_r
        sy = head_c[1] + math.sin(a) * tiara_r
        tiara_skull(surf, int(sx), int(sy), tiara_skull_r, s, lit=(i == 1))


# ── the pillar (skull-cup-staff mirror — cloned, relic-pendant → skull-cup) ───
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The skull-cup-staff IS the pillar: a banded bone shaft hung with six
    skull-cups as ring-pendants = the tileable shaft; the cap is a small
    radiating hand-fan / lotus-burst with a glowing bell at the gap — the
    creature's own radial language, symmetric and on-axis.

    `cap` names the END that faces the GAP."""
    shaft_w = int(13 * s)
    cup_r = int(7 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    band_pitch = int(22 * s)
    cap_room = int(34 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    idx = 0
    while y <= b1:
        bw = shaft_w
        band = [(cx - bw, y - int(8 * s)),
                (cx + bw, y - int(8 * s)),
                (cx + bw, y + int(8 * s)),
                (cx - bw, y + int(8 * s))]
        triad_blob(surf, BONE, band,
                   core_pts=[(cx, y - int(7 * s)), (cx + bw, y - int(7 * s)),
                             (cx + bw, y + int(7 * s)), (cx, y + int(7 * s))],
                   sheen_pts=[(cx - bw, y - int(7 * s)), (cx - int(bw * 0.3), y - int(7 * s)),
                              (cx - int(bw * 0.3), y + int(2 * s)), (cx - bw, y + int(2 * s))],
                   ow=max(1, int(1.4 * s)))
        pygame.draw.line(surf, BONE_DD, (cx - bw, y), (cx + bw, y), max(1, int(1.6 * s)))
        pygame.draw.line(surf, BONE_DD, (cx - bw, y + int(8 * s)),
                         (cx + bw, y + int(8 * s)), max(1, int(1.4 * s)))
        side = -1 if (idx % 2 == 0) else 1
        rx = cx + side * (bw + int(9 * s))
        ry = y + int(2 * s)
        pygame.draw.line(surf, GOLD, (cx + side * bw, y), (rx, ry), max(1, int(1.6 * s)))
        skull_cup(surf, idx % 2, rx, ry, cup_r, s, ang=math.radians(0 if side > 0 else 180))
        idx += 1
        y += band_pitch

    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    burst_r = int(16 * s)
    grow = +1 if cap == "bottom" else -1
    for k in range(7):
        a = math.radians(-90 + (k - 3) * 24) if grow > 0 else math.radians(90 + (k - 3) * 24)
        tip = (cx + math.cos(a) * burst_r, cap_y + math.sin(a) * burst_r)
        pygame.draw.line(surf, INK, (cx, cap_y), tip, max(2, int(4 * s)))
        pygame.draw.line(surf, BONE, (cx, cap_y), tip, max(1, int(2.4 * s)))
        triad_circle(surf, BONE, (int(tip[0]), int(tip[1])), max(1, int(2.4 * s)),
                     ow=max(1, int(1 * s)), core=False, sheen=False)
    collar_y = cap_y - grow * int(burst_r + int(4 * s))
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))
    triad_circle(surf, BONE, (cx, cap_y), int(7 * s), ow=max(1, int(1.4 * s)), core=False)
    pygame.draw.arc(surf, TEAL, (cx - int(6 * s), cap_y - int(6 * s), int(12 * s), int(12 * s)),
                    math.radians(200), math.radians(340), max(2, int(2.4 * s)))
    pygame.draw.circle(surf, ROSE, (cx, cap_y), int(3 * s))
    pygame.draw.circle(surf, ROSE_BR, (cx - int(1 * s), cap_y - int(1 * s)), max(1, int(1.6 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def _font(size, bold=True):
    """Prefer the vendored project face (deterministic across native + WASM);
    fall back to a SysFont so the sheet still renders if the asset is missing."""
    dirname = os.path.dirname(os.path.abspath(__file__))
    fpath = os.path.join(dirname, "..", "..", "..", "..", "..",
                         "game", "assets", "LiberationSans-Bold.ttf")
    if os.path.exists(fpath):
        return pygame.font.Font(fpath, size)
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_kapala_devi(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def make_chip32():
    big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
    draw_kapala_devi(big, 55 * SS, 58 * SS, (32 / 150.0) * SS)
    small = pygame.transform.smoothscale(big, (110, 110))
    return grow_outline(small, INK + (255,), 1)


def main():
    W, H = 1010, 820
    font_big = _font(30)
    font = _font(17)
    font_sm = _font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("KAPALA-DEVI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "six skull-cup wrath  ·  Mukha-Devi SISTER (TIGHT · skull-motif) · 6 upturned skull-cups + LOW 3-skull tiara = halo of nine · round 2",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 232, 1.55)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("Mukha's body + six-arm fan UNCHANGED; arm-ends are now upturned SKULL-CUPS.", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("Gold rim-band + pooled rose offering-glow inside each cup (capped under the third-eye).", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("A-B-A-B by GLOW SIZE; teal hairline on the upper-pair rims; halo of nine skulls total.", True, LABEL_DIM), (14, 622))

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
    pygame.draw.rect(sheet, (60, 58, 70), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — skull-cup-staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("banded bone shaft hung with 6 skull-cup pendants", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("= shaft; hand-fan / lotus-burst + glowing bell", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("caps the gap (mirrored top<->bottom, on-axis)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    chip = make_chip32()

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
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
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

    # === (d) BLACKED-OUT silhouette proof =====================================
    sil_y = night_y + 184
    sheet.blit(font_sm.render("silhouette proof", True, LABEL_DIM), (panel_x + 20, sil_y - 16))
    sil_big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
    draw_kapala_devi(sil_big, 55 * SS, 58 * SS, (40 / 150.0) * SS)
    sil_small = pygame.transform.smoothscale(sil_big, (110, 110))
    mask = pygame.mask.from_surface(sil_small)
    sil = mask.to_surface(setcolor=(20, 18, 24, 255), unsetcolor=(0, 0, 0, 0))
    pygame.draw.rect(sheet, (210, 206, 214), (panel_x + 20, sil_y, 110, 110))
    pygame.draw.rect(sheet, INK, (panel_x + 20, sil_y, 110, 110), 1)
    sheet.blit(sil, (panel_x + 20, sil_y))

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 150, sil_y - 16))
    swatches = [
        (BONE, "rose-bone"), (BONE_D, "bone shade"),
        (ROSE, "rose glow"), (ROSE_D, "deep-rose ember"),
        (GOLD, "gold rim-band"), (TEAL, "teal hairline"),
        (THIRD_BR, "third-eye core"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 150, sil_y + 6
    for i, (c, name) in enumerate(swatches):
        rx = sxp
        ry = syp + i * 13
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 12, 12))
        pygame.draw.rect(sheet, c, (rx, ry, 10, 10))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 16, ry - 1))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  ONLY edit vs Mukha-Devi: arm-end relics -> six upturned "
        "SKULL-CUPS (gold rim + pooled rose offering-glow). STAY: flat fills, ink keyline, triad, chibi, scary-cute.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    # ── self-check: brow third-eye must be the single brightest pixel on BOTH
    # the day and the night 32px chip (composite the chip over each sky so the
    # check sees exactly what the player sees, including any sky bleed-through).
    chip_big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
    draw_kapala_devi(chip_big, 55 * SS, 58 * SS, (32 / 150.0) * SS)
    chip32 = pygame.transform.smoothscale(chip_big, (110, 110))
    cx0, cy0 = 55, 58
    head_brow_y = cy0 - int((32 / 150.0) * 28) - int((32 / 150.0) * 32 * 0.34)

    def brightest_on(sky_t, sky_b, label):
        bg_ = pygame.Surface((110, 110))
        vgrad(bg_, (0, 0, 110, 110), sky_t, sky_b)
        comp = bg_.copy()
        comp.blit(chip32, (0, 0))
        b_xy, b_lum, b_rgb = None, -1.0, None
        brow_lum, pool_lum = -1.0, -1.0   # gap between focal + the hottest cup
        for yy in range(110):
            for xx in range(110):
                r, g, b = comp.get_at((xx, yy))[:3]
                if chip32.get_at((xx, yy))[3] < 40:
                    continue
                lum = 0.299 * r + 0.587 * g + 0.114 * b
                if lum > b_lum:
                    b_lum, b_xy, b_rgb = lum, (xx, yy), (r, g, b)
                if abs(xx - cx0) <= 6 and abs(yy - head_brow_y) <= 8:
                    brow_lum = max(brow_lum, lum)
                else:
                    pool_lum = max(pool_lum, lum)
        near_brow = (abs(b_xy[0] - cx0) <= 9 and abs(b_xy[1] - head_brow_y) <= 12)
        print(f"[{label}] brightest {b_rgb} lum={b_lum:.0f} at {b_xy}; "
              f"brow_max={brow_lum:.0f} hottest_cup={pool_lum:.0f} gap={brow_lum-pool_lum:.0f}; "
              f"brow-is-brightest={near_brow}")
        return near_brow

    ok_day = brightest_on(DAY_SKY_T, DAY_SKY_B, "DAY 32px")
    ok_night = brightest_on(NIGHT_T, NIGHT_B, "NIGHT 32px")
    print(f"SHIP-GATE brow-brightest both chips = {ok_day and ok_night}")


if __name__ == "__main__":
    main()
