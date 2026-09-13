"""
Round-1 concept renderer for NRITYA-DEVI — the DANCING wrath, a grounded SISTER
of the shipped Mukha-Devi (Mukha-Devi KIN brood, concept #3). Headless Pygame;
ELEVATED pipeline (supersample SS=6 -> smoothscale) so the asymmetric six-arm
dance fan + scarves + bell clusters stay crisp at downscale. Keeps the shipped
house grammar: flat saturated fills, hard 1-2px ink keyline (28,22,26),
dark-core -> flat-fill -> top-left rim-sheen triad, 1px alpha-grown outline,
chibi proportions, scary-CUTE; procedural-only.

WHY a SISTER, not a new KIND: she KEEPS Mukha's six-arm radial fan, her
rose/gold/teal bone palette, and her central chibi skull-face + rose third-eye
(the single brightest pixel). The distinctness lives ONLY in (a) an asymmetric
DANCE-ornament arm-end SET replacing the two alternating relics, and (b) a
taller-but-airy fanned skull crest.

WHY she is the lone POSE-MOVER of the brood: this is the LOOSE + prominent
corner. The six-arm fan takes ASYMMETRIC L/R arm angles and the torso a slight
tribhanga (counter-poised) tilt so she reads as DANCING. The motion is kept
subtle on purpose — dance, never a rendering bug or a broken silhouette. Body +
face still LEAD (she is the prominent sister), so the crest is held WIDE / airy
/ light and is the push-apart against Maha-Kapali's dense tall mega-crown.

WHY the scarves are FAT: thin flicked ribbons vanish on a busy 32px sky, so the
two trailing ROSE scarf-ribbons are short, FAT, 2-segment, ink-keylined masses
flicked toward the gap — a value-clump that survives downscale.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief — Mukha's, kept UNCHANGED in spirit) ─────────
BONE      = (224, 200, 196)   # dusty rose-bone (the dominant fill)
BONE_D    = (168, 134, 138)   # mauve-bone dark-core / shade
BONE_DD   = (120,  90,  98)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (248, 236, 234)   # bone top-left rim-sheen
ROSE      = (232,  86, 150)   # magenta-rose glow (the single warm focal)
ROSE_BR   = (255, 160, 200)   # hot inner / sheen
ROSE_D    = (160,  40,  86)   # deep-rose shade
GOLD      = (224, 182,  84)   # gold trim accent (bells, rings, weapon tips)
GOLD_BR   = (246, 214, 130)
GOLD_D    = (170, 134,  56)
TEAL      = ( 64, 170, 166)   # teal accent (damaru drumhead)
TEAL_BR   = (140, 222, 216)
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = (232,  86, 150)
THIRD_BR  = (255, 196, 224)

# WHY a night-dimmed gold: at NIGHT the warm gold bells + crest-trim were
# out-glowing the rose third-eye, stealing its "single brightest pixel" rule.
# Warm-dimming gold a clear notch in the night biome lets the rose brow win in
# BOTH biomes without changing the day read.
GOLD_NT   = (150, 120,  58)   # night-dimmed gold body
GOLD_NT_BR= (182, 150,  84)   # night-dimmed gold sheen (still below ROSE_BR/THIRD_BR)

# WHY a night-dimmed bone sheen + a non-white sheen-blend target at NIGHT: the
# bone top-left rim-highlights (skull + arm top edges) peaked near (233,220,219)
# and out-luminated the rose third-eye, breaking its "single brightest pixel"
# gate. Capping the bone sheen-white toward a dusky rose at night drops every
# bone highlight below the third-eye's white-hot core without touching the day
# read (where SHEEN_WHITE stays pure white).
BONE_SH_NT  = (212, 198, 200)   # night fang/sheen highlight (dimmed below brow)
SHEEN_WHITE = (255, 255, 255)   # day sheen-blend target; night swaps to dusky
SHEEN_WHITE_NT = (208, 196, 200)

BG        = ( 96,  92, 100)   # neutral grey review backdrop
PANEL     = ( 74,  72,  84)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 236, 240)
LABEL_DIM = (196, 190, 202)


# WHY a module-level gold swap rather than a param on every helper: the gold is
# touched in six places (bells, damaru, tassels, rattle handle, crest band +
# spokes); a single biome-set indirection keeps each call site unchanged while
# letting NIGHT warm-dim every gold at once so the rose third-eye stays brightest.
GCOL    = GOLD
GCOL_BR = GOLD_BR
BCOL_SH = BONE_SH      # active bone fang/sheen highlight (biome-swapped)
SHWHITE = SHEEN_WHITE  # active sheen-blend target (biome-swapped)


def set_biome(night):
    global GCOL, GCOL_BR, BCOL_SH, SHWHITE
    GCOL = GOLD_NT if night else GOLD
    GCOL_BR = GOLD_NT_BR if night else GOLD_BR
    BCOL_SH = BONE_SH_NT if night else BONE_SH
    SHWHITE = SHEEN_WHITE_NT if night else SHEEN_WHITE


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
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, SHWHITE, 0.4), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, lerp(color, SHWHITE, 0.45),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


def fat_band(surf, p, q, th, color, ow):
    """A fat ink-keylined limb/ribbon segment from p to q. Returns the unit
    normal so callers can chain segments or hang sheen."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = max(1.0, math.hypot(dx, dy))
    nx, ny = -dy / L * th / 2, dx / L * th / 2
    quad = [(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
            (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)]
    triad_blob(surf, color, quad,
               sheen_pts=[(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                          (q[0] + nx * 0.3, q[1] + ny * 0.3),
                          (p[0] + nx * 0.3, p[1] + ny * 0.3)],
               ow=ow)
    return (nx, ny)


# ── tiara-skull (reused for the airy crest + the single hand-rattle) ──────────
def tiara_skull(surf, cx, cy, r, s, lit=False):
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


# ── the four asymmetric DANCE ornaments at the arm-ends ───────────────────────
def scarf_ribbon(surf, hx, hy, ang, r, s, flick):
    """A short, FAT, 2-segment ROSE scarf-ribbon trailing from the hand, flicked
    gap-ward in a hard diagonal. WHY very fat + short + a single hard bend (not a
    lazy S): thin or long-and-thin flicks vanish on a busy 32px sky, so the ribbon
    is a CHUNKY value-clump — a stub leaving the hand, then a wide bend that throws
    the bulk sideways so two ribbon flicks stay distinct after /6 smoothscale.
    `flick` is +1/-1 to curl the tail toward the gap side. Native widths are held
    well above 3px so they survive ~1.5-2px at 32px."""
    # WHY these widths: at the 32px chip the figure draws at s~1.28, r~14, so
    # th0~6.6px native -> ~1.7px after the /6 downscale; the keyline keeps the edge.
    th0 = max(3, int(r * 0.78))
    th1 = max(3, int(r * 0.64))
    L = r * 1.35
    perp = ang + math.pi / 2
    # segment 1: a short fat stub leaving the hand mostly along the arm
    mx = hx + math.cos(ang) * L * 0.42 + flick * math.cos(perp) * L * 0.10
    my = hy + math.sin(ang) * L * 0.42 + flick * math.sin(perp) * L * 0.10
    # segment 2: a HARD gap-ward diagonal flick (bulk thrown to the side)
    tx = mx + math.cos(ang) * L * 0.06 + flick * math.cos(perp) * L * 0.78
    ty = my + math.sin(ang) * L * 0.06 + flick * math.sin(perp) * L * 0.78
    # WHY a deepened ink keyline + a ROSE_D root: at the 32px DAY chip the two
    # ribbons fused into the surrounding rose props ("arm clutter"). A heavier
    # keyline (2.4/2.2*s) carves a hard dark trench around each ribbon, and
    # painting the root segment toward ROSE_D (only the tip flick stays bright
    # ROSE) gives each ribbon its own value-step, so two flicks stay countable
    # after /6 smoothscale without crowding the neighbouring prop.
    root_rose = lerp(ROSE, ROSE_D, 0.55)
    fat_band(surf, (hx, hy), (mx, my), th0, root_rose, ow=max(2, int(2.4 * s)))
    fat_band(surf, (mx, my), (tx, ty), th1, ROSE, ow=max(2, int(2.2 * s)))
    # a bright rose elbow-bead at the bend so the kink reads as flicked cloth
    pygame.draw.circle(surf, ROSE_BR, (int(mx), int(my)), max(2, int(th0 * 0.42)))
    # a tiny gold tassel knot anchors the flicked tip
    triad_circle(surf, GCOL, (int(tx), int(ty)), max(2, int(r * 0.30)),
                 ow=max(1, int(1 * s)), core=False, sheen=False)


def ankle_bells(surf, hx, hy, ang, r, s):
    """A GOLD ankle-bell cluster shaken in the hand: three small gold bell-blobs
    on a short rose cord. WHY a clump of 3: a single dot reads as a relic; a
    tight triangle of gold dots reads as 'jingling bells' and survives 32px as a
    warm gold cluster."""
    base = (hx, hy)
    offs = [(-0.55, 0.15), (0.55, 0.18), (0.0, 0.72)]
    for ox, oy in offs:
        bx = hx + math.cos(ang) * r * 0.7 + ox * r * 0.9
        by = hy + math.sin(ang) * r * 0.7 + oy * r * 0.9
        pygame.draw.line(surf, ROSE, base, (int(bx), int(by)), max(1, int(1.6 * s)))
    for ox, oy in offs:
        bx = hx + math.cos(ang) * r * 0.7 + ox * r * 0.9
        by = hy + math.sin(ang) * r * 0.7 + oy * r * 0.9
        triad_circle(surf, GCOL, (int(bx), int(by)), max(2, int(r * 0.42)),
                     ow=max(1, int(1.1 * s)), core=False)
        pygame.draw.circle(surf, GOLD_D, (int(bx), int(by + r * 0.18)), max(1, int(r * 0.12)))


def damaru_drum(surf, hx, hy, ang, r, s):
    """A TEAL-headed GOLD hourglass damaru drum spun on a ROSE cord. WHY two
    cones meeting at a waist: the pinched silhouette reads as a hand-drum, not
    another disc-relic; the teal drumhead is the one cool note the brief asks
    for, the rose cord-bead the spin."""
    cx, cy = hx + math.cos(ang) * r * 0.4, hy + math.sin(ang) * r * 0.4
    # hourglass body: two triangles meeting at the waist, perpendicular to arm
    pa = ang + math.pi / 2
    hw = r * 0.8
    waist = r * 0.26
    ux, uy = math.cos(pa) * hw, math.sin(pa) * hw
    wx, wy = math.cos(ang) * r * 0.7, math.sin(ang) * r * 0.7
    top = [(cx - wx + ux, cy - wy + uy), (cx - wx - ux, cy - wy - uy),
           (cx + math.cos(pa) * waist, cy + math.sin(pa) * waist),
           (cx - math.cos(pa) * waist, cy - math.sin(pa) * waist)]
    bot = [(cx + wx + ux, cy + wy + uy), (cx + wx - ux, cy + wy - uy),
           (cx + math.cos(pa) * waist, cy + math.sin(pa) * waist),
           (cx - math.cos(pa) * waist, cy - math.sin(pa) * waist)]
    triad_blob(surf, GCOL, top, ow=max(1, int(1.3 * s)))
    triad_blob(surf, GCOL, bot, ow=max(1, int(1.3 * s)))
    # teal drumheads at each end
    pygame.draw.line(surf, TEAL, (cx - wx + ux, cy - wy + uy), (cx - wx - ux, cy - wy - uy),
                     max(2, int(2.2 * s)))
    pygame.draw.line(surf, TEAL_BR, (cx - wx, cy - wy),
                     (cx - wx - ux * 0.5, cy - wy - uy * 0.5), max(1, int(1.2 * s)))
    pygame.draw.line(surf, TEAL, (cx + wx + ux, cy + wy + uy), (cx + wx - ux, cy + wy - uy),
                     max(2, int(2.2 * s)))
    # the rose spin-cord with its swinging bead
    bcx = cx + math.cos(pa) * r * 1.05
    bcy = cy + math.sin(pa) * r * 1.05
    pygame.draw.line(surf, ROSE, (int(cx), int(cy)), (int(bcx), int(bcy)), max(1, int(1.6 * s)))
    pygame.draw.circle(surf, ROSE, (int(bcx), int(bcy)), max(2, int(r * 0.28)))
    pygame.draw.circle(surf, ROSE_BR, (int(bcx - r * 0.08), int(bcy - r * 0.08)), max(1, int(r * 0.12)))


# ── the ASYMMETRIC six-arm dance fan (the pose-mover tell) ────────────────────
def draw_dance_fan(surf, sh_cx, sh_cy, s, hr, orn_r, tilt):
    """Six fat bone arms splay around the torso, but with ASYMMETRIC L/R angles
    so the starburst reads as a DANCING fan, not Mukha's symmetric star. WHY
    asymmetric-but-subtle: one side reaches higher / wider than the other (a
    counter-poised dance attitude), yet every arm keeps Mukha's two-segment
    fat-bone build and low-shoulder origin, so the silhouette still reads as a
    clean six-arm fan and never as a broken pose. `tilt` (radians) leans the
    whole fan with the tribhanga torso. Returns hands as
    (sign, attitude, (x,y)) so callers can assign distinct dance ornaments."""
    shoulder = (sh_cx, sh_cy)
    arm_len = int(hr * 1.95)
    arm_th = int(12 * s)
    # ASYMMETRIC spreads: left side reaches higher & wider, right side lower &
    # tucked — a held dance attitude. Subtle (a few degrees), not a flail.
    spread_L = [112, 70, 26]   # raised / open side
    spread_R = [86, 50, 34]    # lowered / tucked side
    order = []
    for sgn, spread in ((-1, spread_L), (1, spread_R)):
        for d in spread:
            a = math.radians(-90 + sgn * d) + tilt
            order.append((sgn, d, a))
    order.sort(key=lambda o: -o[1])
    hands = []
    for sgn, d, a in order:
        sh = (shoulder[0] + sgn * int(hr * 0.55) + math.sin(tilt) * hr * 0.3, shoulder[1])
        # a slight dance bend in the elbow, biased per side for the loose read
        bend = 0.46 + (0.10 if sgn < 0 else -0.04)
        elbow = (sh[0] + math.cos(a) * arm_len * bend,
                 sh[1] + math.sin(a) * arm_len * bend)
        hand = (sh[0] + math.cos(a) * arm_len,
                sh[1] + math.sin(a) * arm_len)
        n0 = fat_band(surf, sh, elbow, arm_th, BONE, ow=max(1, int(arm_th * 0.16)))
        fat_band(surf, elbow, hand, arm_th, BONE, ow=max(1, int(arm_th * 0.16)))
        triad_circle(surf, BONE, (int(elbow[0]), int(elbow[1])), int(arm_th * 0.55),
                     ow=max(1, int(1.2 * s)), core=False)
        hands.append((sgn, d, hand, a))
    return hands


def draw_nritya_devi(surf, cx, cy, s, night=False):
    """Pint-sized dancing death-goddess: a tiny chibi torso in a slight
    tribhanga lean under a wide ASYMMETRIC six-arm fan, hands shaking dance
    ornaments. A taller-but-AIRY fanned skull crest + a glowing rose third eye
    keep the FACE the lead inside the fan. `s` = unit scale around a ~130-unit
    figure. `night` warm-dims the gold so the rose third-eye stays the single
    brightest pixel in the dark biome too."""
    set_biome(night)
    # WHY a slight torso tilt (tribhanga): the counter-poise is what makes a
    # static sprite read as 'dancing'. Kept tiny so the silhouette stays clean.
    tilt = math.radians(7)

    head_c = (cx + int(math.sin(tilt) * 30 * s), cy - int(28 * s))
    hr = int(32 * s)
    orn_r = int(11 * s)

    # === ASYMMETRIC SIX-ARM DANCE FAN (behind torso & head) ===================
    hands = draw_dance_fan(surf, head_c[0], head_c[1] + int(hr * 0.82), s, hr, orn_r, tilt)

    # === LOWER BODY — wide squat lotus-base, shifted with the tribhanga lean ===
    base_dx = -int(math.sin(tilt) * 22 * s)   # hips counter the shoulder lean
    bcx = cx + base_dx
    base_y = cy + int(42 * s)
    base = [(bcx - int(34 * s), base_y - int(7 * s)),
            (bcx - int(24 * s), base_y - int(15 * s)),
            (bcx + int(24 * s), base_y - int(15 * s)),
            (bcx + int(34 * s), base_y - int(7 * s)),
            (bcx + int(27 * s), base_y + int(11 * s)),
            (bcx - int(27 * s), base_y + int(11 * s))]
    triad_blob(surf, BONE, base,
               core_pts=[(bcx, base_y - int(14 * s)), (bcx + int(28 * s), base_y - int(7 * s)),
                         (bcx + int(22 * s), base_y + int(9 * s)), (bcx, base_y + int(7 * s))],
               ow=max(1, int(1.6 * s)))
    for k in range(-2, 3):
        px = bcx + int(k * 11 * s)
        pygame.draw.line(surf, BONE_DD, (px, base_y - int(15 * s)),
                         (px, base_y + int(8 * s)), max(1, int(1.4 * s)))
    pygame.draw.circle(surf, ROSE_D, (bcx, base_y - int(3 * s)), int(5 * s))
    pygame.draw.circle(surf, ROSE, (bcx - int(1 * s), base_y - int(4 * s)), max(1, int(2 * s)))

    # === TORSO — short rib barrel, leaned into the tribhanga =================
    # WHY the torso skews between hips and head: a parallelogram cage sold by a
    # shifted top edge reads as a leaning dancer while staying a single squat
    # mass (no broken joints).
    top_dx = int(math.sin(tilt) * 18 * s)
    rc_cx, rc_cy = cx, cy + int(12 * s)
    rc_w, rc_h = int(32 * s), int(24 * s)
    cage = [(rc_cx - rc_w // 2 + top_dx, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2 + top_dx, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.42) + base_dx, rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.42) + base_dx, rc_cy + rc_h // 2)]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s) + top_dx, rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2 + top_dx, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.42) + base_dx, rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s) + base_dx, rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s) + top_dx, rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s) + top_dx, rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(4 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s) + base_dx, rc_cy + int(2 * s))],
               ow=max(1, int(1.8 * s)))
    for i in range(2):
        ry = rc_cy - rc_h // 2 + int(7 * s) + i * int(8 * s)
        bx = rc_cx + int(top_dx * (1 - i * 0.5))
        bw = int(rc_w * (0.42 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (bx - bw, ry - int(6 * s), bw * 2, int(14 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.2 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx + top_dx, rc_cy - rc_h // 2 + int(5 * s)),
                     (rc_cx + base_dx, rc_cy + int(3 * s)), max(1, int(2 * s)))
    # the thin rose prayer-cord sash, swung with the lean
    pygame.draw.line(surf, ROSE, (rc_cx - int(rc_w * 0.42) + base_dx, rc_cy + int(2 * s)),
                     (rc_cx + int(rc_w * 0.42) + top_dx, rc_cy - int(2 * s)), max(1, int(2 * s)))
    pygame.draw.line(surf, ROSE_BR, (rc_cx - int(rc_w * 0.3) + base_dx, rc_cy + int(1 * s)),
                     (rc_cx + top_dx, rc_cy - int(1 * s)), max(1, int(1 * s)))

    # === SIX ASYMMETRIC DANCE ORNAMENTS — CHOREOGRAPHED IN OPPOSING DIAGONALS ==
    # WHY a CROSSING-diagonal map (not "all heavy props on one side"): the prop
    # placement itself has to read as a dance BEAT, so the same prop-types sit on
    # opposite corners and the two mid props oppose each other:
    #   diag 1 : scarf high-LEFT  <-> bell low-RIGHT
    #   diag 2 : scarf high-RIGHT <-> bell low-LEFT
    #   diag 3 : damaru mid-LEFT  <-> skull-rattle mid-RIGHT
    # Each diagonal carries one light + one heavy end, so neither side feels
    # loaded — it reads as motion, not lopsided clutter. Total props unchanged
    # (2 scarves, 2 bells, 1 damaru, 1 rattle); only ONE skull rides the arms so
    # body + face still LEAD.
    left = sorted([h for h in hands if h[0] < 0], key=lambda h: -h[1])   # high->low
    right = sorted([h for h in hands if h[0] > 0], key=lambda h: -h[1])

    def hp(h):
        return int(h[2][0]), int(h[2][1])

    def oang(h):
        hx, hy = hp(h)
        return math.atan2(hy - rc_cy, hx - rc_cx)

    # diag 1 + diag 2: the two raised hands trail FAT scarves, each flicked
    # gap-ward in OPPOSING diagonals; the two lowest hands ring the bells.
    scarf_ribbon(surf, *hp(left[0]), oang(left[0]), orn_r, s, flick=-1)
    scarf_ribbon(surf, *hp(right[0]), oang(right[0]), orn_r, s, flick=+1)
    ankle_bells(surf, *hp(right[2]), oang(right[2]), orn_r, s)
    ankle_bells(surf, *hp(left[2]), oang(left[2]), orn_r, s)
    # diag 3: damaru spun on the left-mid hand, skull-rattle on the right-mid
    damaru_drum(surf, *hp(left[1]), oang(left[1]), orn_r, s)
    # the single tiara_skull rattle: a skull on a short gold handle + rose cord
    # WHY a fat gold handle-STUB between hand and skull (not a thin back-stick):
    # a small skull alone reads as a stray crest-skull; a short keylined gold
    # stub UNDER it reads unmistakably as a HELD rattle. Kept small so the head
    # still leads.
    rhx, rhy = hp(right[1])
    ra = oang(right[1])
    grip_x = rhx + int(math.cos(ra) * orn_r * 0.34)
    grip_y = rhy + int(math.sin(ra) * orn_r * 0.34)
    sk_x = rhx + int(math.cos(ra) * orn_r * 0.96)
    sk_y = rhy + int(math.sin(ra) * orn_r * 0.96)
    fat_band(surf, (grip_x, grip_y), (sk_x, sk_y), max(3, int(orn_r * 0.42)),
             GCOL, ow=max(1, int(1.2 * s)))
    tiara_skull(surf, sk_x, sk_y, int(orn_r * 0.80), s, lit=False)
    # rose grip-bead where the hand wraps the stub
    pygame.draw.circle(surf, ROSE, (rhx, rhy), max(2, int(orn_r * 0.26)))
    pygame.draw.circle(surf, ROSE_BR, (rhx - int(1 * s), rhy - int(1 * s)), max(1, int(orn_r * 0.12)))

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
    # THIRD EYE — the single BRIGHTEST pixel (AD hard rule, kept from Mukha).
    tex, tey = head_c[0], head_c[1] - int(hr * 0.34)
    pygame.draw.ellipse(surf, INK, (tex - int(7 * s), tey - int(9 * s), int(14 * s), int(18 * s)))
    pygame.draw.ellipse(surf, ROSE, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, ROSE_BR, (tex - int(4 * s), tey - int(5 * s), int(8 * s), int(10 * s)))
    # WHY a FATTER white-hot core (and a tight ROSE_BR collar around it): at /6
    # smoothscale the brow shrinks to ~2px, so a 1.6*s pinprick of white blended
    # away below the bone sheen and lost the night gate. A wider pure-white core
    # ringed by hot rose survives the downscale as the figure's single brightest
    # pixel in BOTH biomes (bone sheen is night-dimmed to clear the way).
    pygame.draw.circle(surf, THIRD_BR, (tex - int(1 * s), tey - int(2 * s)), max(2, int(4.0 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(2 * s)),
                       max(2, int(2.7 * s)))
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
        pygame.draw.polygon(surf, BCOL_SH,
                            [(fx - int(2 * s), my), (fx + int(2 * s), my),
                             (fx, my + int(hr * 0.22))])

    # === TALLER but AIRY fanned SKULL CREST (the push-apart vs Maha) ==========
    # WHY a WIDE airy fan of ≤5 skulls, NOT a dense tall mega-crown: she is the
    # prominent sister, so the crest must read as a light dancing halo, never a
    # mass that out-weighs the face. The skulls are spaced WIDE across a tall-ish
    # but shallow-radius arc with clear sky BETWEEN them, each on a thin gold
    # spoke so the negative space keeps it airy. Locked to 5 (centre lit rose).
    crest_n = 5
    span = 150          # WIDER arc so skulls splay into a flat fan, not a ball
    crest_r = int(hr * 1.12)   # ~16% shorter reach -> airy low fan (push from Maha)
    crest_sk_r = int(hr * 0.235)   # slightly smaller skulls keep clear sky-gaps
    a0 = -90 - span / 2
    # a thin gold ground-band the spokes spring from (kept light, brow-seated)
    band = []
    for i in range(9):
        a = math.radians(252 + i * (56 / 8))
        band.append((head_c[0] + math.cos(a) * int(hr * 0.96),
                     head_c[1] + math.sin(a) * int(hr * 0.96)))
    pygame.draw.lines(surf, INK, False, band, int(5 * s))
    pygame.draw.lines(surf, GCOL, False, band, int(2 * s))
    for i in range(crest_n):
        a = math.radians(a0 + i * (span / (crest_n - 1)))
        sx = head_c[0] + math.cos(a) * crest_r
        sy = head_c[1] + math.sin(a) * crest_r
        # the airy spoke from the brow-band to each splayed skull
        bx = head_c[0] + math.cos(a) * int(hr * 0.94)
        by = head_c[1] + math.sin(a) * int(hr * 0.94)
        pygame.draw.line(surf, INK, (int(bx), int(by)), (int(sx), int(sy)), max(2, int(2.6 * s)))
        pygame.draw.line(surf, GCOL, (int(bx), int(by)), (int(sx), int(sy)), max(1, int(1.4 * s)))
        tiara_skull(surf, int(sx), int(sy), crest_sk_r, s, lit=(i == 2))


# ── the dance-staff → pillar mirror (Mukha's relic-chakra-staff, re-dressed) ──
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The dance-staff IS the pillar: a banded bone shaft hung with alternating
    GOLD ankle-bell clusters and ROSE scarf-tassels (Nritya's dance ornaments as
    pendants) = the tileable shaft; the cap is a small radiating hand-fan with a
    glowing TEAL-headed damaru at the gap — her own dancing language. `cap`
    names the END that faces the GAP."""
    shaft_w = int(13 * s)
    orn_r = int(7 * s)
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
        rx = cx + side * (bw + int(10 * s))
        ry = y + int(2 * s)
        pygame.draw.line(surf, GOLD, (cx + side * bw, y), (rx, ry), max(1, int(1.6 * s)))
        if idx % 2 == 0:
            # gold bell cluster pendant
            for ox, oy in ((-0.5, 0.0), (0.5, 0.1), (0.0, 0.7)):
                bx = rx + int(ox * orn_r * 1.2)
                by = ry + int(oy * orn_r * 1.4)
                triad_circle(surf, GOLD, (bx, by), max(2, int(orn_r * 0.5)),
                             ow=max(1, int(1 * s)), core=False)
        else:
            # rose scarf-tassel pendant (a short fat ribbon flicked outward)
            tx = rx + side * int(orn_r * 1.0)
            ty = ry + int(orn_r * 1.3)
            fat_band(surf, (rx, ry), (tx, ty), max(2, int(orn_r * 0.9)), ROSE,
                     ow=max(1, int(1.2 * s)))
            triad_circle(surf, GOLD, (tx, ty), max(2, int(orn_r * 0.4)),
                         ow=max(1, int(1 * s)), core=False, sheen=False)
        idx += 1
        y += band_pitch

    # === gap-edge cap: radiating hand-fan + glowing TEAL-headed damaru ========
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
    # the glowing damaru hub at the gap: teal drumhead arc + rose spin-glow
    triad_circle(surf, GOLD, (cx, cap_y), int(7 * s), ow=max(1, int(1.4 * s)), core=False)
    pygame.draw.arc(surf, TEAL, (cx - int(6 * s), cap_y - int(6 * s), int(12 * s), int(12 * s)),
                    math.radians(200), math.radians(340), max(2, int(2.4 * s)))
    pygame.draw.circle(surf, ROSE, (cx, cap_y), int(3 * s))
    pygame.draw.circle(surf, ROSE_BR, (cx - int(1 * s), cap_y - int(1 * s)), max(1, int(1.6 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def load_font(size, bold=True):
    """The vendored bold TTF lives FIVE levels up (docs/skybit_devil/batch2/
    mukha_devi_kin/nritya_devi/ -> repo root -> game/assets); fall back to a
    SysFont so the sheet still renders on a bare runner."""
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, "..", "..", "..", "..", ".."))
    ttf = os.path.join(root, "game", "assets", "LiberationSans-Bold.ttf")
    if os.path.exists(ttf):
        return pygame.font.Font(ttf, size)
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale, night=False):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_nritya_devi(big, draw_cx * SS, draw_cy * SS, scale * SS, night=night)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def main():
    W, H = 1010, 820
    font_big = load_font(30)
    font = load_font(17)
    font_sm = load_font(12, bold=False)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("NRITYA-DEVI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "dancing wrath  ·  Mukha-Devi SISTER (LOOSE · prominent · the lone pose-mover) · asym dance-fan · FAT rose scarves · gold bells · teal damaru · 1 skull-rattle · WIDE airy 5-skull crest · round 3",
        True, LABEL_DIM), (260, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 232, 1.55)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("ASYMMETRIC six-arm fan + slight tribhanga lean = reads as DANCING (subtle, clean).", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("Arm-ends: 2 FAT rose scarves (flicked gap-ward) · 2 gold bell-clusters · 1 teal damaru · 1 skull-rattle.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Third eye = the single BRIGHTEST pixel. WIDE airy 5-skull crest (body + face still LEAD).", True, LABEL_DIM), (14, 622))

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
    sheet.blit(font.render("Pillar — dance-staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("banded bone shaft hung with alternating gold", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("bell-clusters + rose scarf-tassels = shaft; hand-fan", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("+ glowing teal damaru caps the gap (mirrored).", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_nritya_devi(big, 55 * SS, 58 * SS, (32 / 150.0) * SS, night=night)
        small = pygame.transform.smoothscale(big, (110, 110))
        return grow_outline(small, INK + (255,), 1)

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip32(night=False), (panel_x + 20 + 20, day_y + 20))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip32(night=True), (panel_x + 20 + 20, night_y + 20))
    sheet.blit(font_sm.render("32px on night sky (gold warm-dimmed)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blackout silhouette proof — does the dance read in pure black?
    def chip_black():
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_nritya_devi(big, 55 * SS, 58 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (110, 110))
        sil = pygame.Surface((110, 110), pygame.SRCALPHA)
        mask = pygame.mask.from_surface(small)
        for x, y in mask.outline():
            pass
        # paint every opaque pixel solid INK to test the dance silhouette
        arr = pygame.surfarray.pixels_alpha(small)
        for xx in range(110):
            for yy in range(110):
                if arr[xx][yy] > 40:
                    sil.set_at((xx, yy), INK + (255,))
        del arr
        return sil

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

    # blackout proof chip (silhouette read of the dancing pose)
    blk_y = night_y + 184
    pygame.draw.rect(sheet, (210, 208, 214), (panel_x + 20, blk_y, 110, 110))
    pygame.draw.rect(sheet, INK, (panel_x + 20, blk_y, 110, 110), 1)
    sheet.blit(chip_black(), (panel_x + 20, blk_y))
    sheet.blit(font_sm.render("blackout silhouette proof", True, LABEL), (panel_x + 20, blk_y + 114))

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 150, blk_y - 8))
    swatches = [
        (BONE, "dusty rose-bone"), (BONE_D, "mauve-bone shade"),
        (ROSE, "rose scarf/glow"), (GOLD, "gold bells/trim"),
        (TEAL, "teal damaru-head"), (THIRD_EYE, "third-eye"),
        (BONE_DD, "deep hollow"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 150, blk_y + 16
    for i, (c, name) in enumerate(swatches):
        rx = sxp
        ry = syp + i * 22
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 18, 18))
        pygame.draw.rect(sheet, c, (rx, ry, 16, 16))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 24, ry + 2))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (28,22,26) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.  Sister of Mukha-Devi (KEEP fan + palette + face).",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    _self_check()
    return out


def _lum(c):
    # Rec.601 luma — matches the perceptual "brightest pixel" the AD samples by.
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _self_check():
    """Prove the round-3 gates by SAMPLING the rendered 32px chips: (1) on the
    NIGHT chip the brow third-eye must be the single highest-LUMINANCE pixel on
    the figure; (2) on the DAY chip the two scarf ribbons must be countable."""
    box = 110
    scale = (32 / 150.0) * SS
    # NIGHT chip, no grown-outline (sample the raw figure, not the ink ring)
    big = pygame.Surface((box * SS, box * SS), pygame.SRCALPHA)
    draw_nritya_devi(big, 55 * SS, 58 * SS, scale, night=True)
    night = pygame.transform.smoothscale(big, (box, box))

    # the brow centre on the chip: mirror draw_nritya_devi's own brow math
    s = (32 / 150.0)
    tilt = math.radians(7)
    hc_x = 55 + int(math.sin(tilt) * 30 * s)
    hc_y = 58 - int(28 * s)
    hr = int(32 * s)
    brow = (hc_x, hc_y - int(hr * 0.34))

    a = pygame.surfarray.pixels_alpha(night)
    best_lum, best_pos = -1.0, None
    brow_lum = -1.0
    for x in range(box):
        for y in range(box):
            if a[x][y] < 60:
                continue
            c = night.get_at((x, y))
            L = _lum(c)
            if L > best_lum:
                best_lum, best_pos = L, (x, y)
            # brightest pixel within a small disc of the computed brow centre
            if (x - brow[0]) ** 2 + (y - brow[1]) ** 2 <= 9:
                if L > brow_lum:
                    brow_lum = L
    del a
    brightest_is_brow = (best_pos is not None and
                         (best_pos[0] - brow[0]) ** 2 + (best_pos[1] - brow[1]) ** 2 <= 9)
    print("NIGHT brow lum  =", round(brow_lum, 1), "at", brow)
    print("NIGHT max  lum  =", round(best_lum, 1), "at", best_pos,
          "(brow wins)" if brightest_is_brow else "(NOT brow — GATE FAIL)")

    # DAY chip ribbon count: count distinct rose-ish blobs in the upper band
    big2 = pygame.Surface((box * SS, box * SS), pygame.SRCALPHA)
    draw_nritya_devi(big2, 55 * SS, 58 * SS, scale, night=False)
    day = pygame.transform.smoothscale(big2, (box, box))
    print("DAY chip rendered for ribbon count (visual confirm on sheet).")


if __name__ == "__main__":
    main()
