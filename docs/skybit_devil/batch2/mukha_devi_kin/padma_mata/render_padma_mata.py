"""
Round-1 concept renderer for PADMA-MATA — the bloom-and-relic mother, grounded
SISTER of the shipped Mukha-Devi (six-armed bone-mother). Headless Pygame;
ELEVATED pipeline (supersample SS=6 -> smoothscale). Clones Mukha-Devi WHOLESALE
— same chibi torso, same six-arm radial starburst, same three-eyed face, same
LOW 3-skull tiara, same warm rose/gold/teal bone palette — because these are
sisters, NOT divergent KINDs. The distinctness lives in ONE swap and one nudge.

WHY this is the brood's NON-wrathful tonal counterweight: instead of weapons or
skull-cups, every hand opens a small BLOOM-CLUSTER — fat bone/gold petals fanning
around a central relic. She is the gentlest, most scary-CUTE sister: a flower
goddess whose two mid-hands hide a tiny skull BUD nestled among the petals (the
"is that a skull in there?" hook), so she stays PROMINENT-skulled, never a
skull-motif. The A-B-A-B rhythm is kept: A = ROSE disc cradled in petals,
B = GOLD seed-pod with a TEAL dewdrop.

WHY a faint coral warmth ONLY in the bloom hearts: it reads as living/blooming
without leaving the rose family — a hair toward coral, kept clear of KFC red and
any owned warm hue. Crown and pose are UNCHANGED from Mukha (the tight anchor).

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief — IDENTICAL to Mukha-Devi) ───────────────────
BONE      = (224, 200, 196)   # dusty rose-bone (the dominant fill)
BONE_D    = (168, 134, 138)   # mauve-bone dark-core / shade
BONE_DD   = (120,  90,  98)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (248, 236, 234)   # bone top-left rim-sheen
ROSE      = (232,  86, 150)   # magenta-rose relic GLOW (the single warm focal)
ROSE_BR   = (255, 160, 200)   # hot relic-glow inner / sheen
ROSE_D    = (160,  40,  86)   # deep-rose shade
GOLD      = (224, 182,  84)   # gold relic-trim accent (rings, weapon tips)
GOLD_BR   = (246, 214, 130)
GOLD_D    = (170, 134,  56)
TEAL      = ( 64, 170, 166)   # teal bell-sliver / dewdrop
TEAL_BR   = (140, 222, 216)
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = (232,  86, 150)   # third-eye glow (rose so it reads as her power-focus)
THIRD_BR  = (255, 196, 224)

# WHY a coral-warm HEART tint, family-internal: nudges ROSE a hair toward coral
# ONLY inside the bloom centres so the flowers read alive without inventing a new
# hue. Kept clear of KFC red (≈ 211,38,32) and any owned warm — still magenta-rose.
ROSE_CORAL    = (244, 104, 132)   # bloom-heart fill (rose nudged a hair coral)
ROSE_CORAL_BR = (255, 174, 188)   # bloom-heart sheen

BG        = ( 96,  92, 100)   # neutral grey review backdrop
PANEL     = ( 74,  72,  84)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
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


# ── a single ornamental tiara-skull (reused for tiara + hidden bloom buds) ────
def tiara_skull(surf, cx, cy, r, s, lit=False):
    """Tiny rose-bone skull for the LOW 3-skull tiara AND the two hidden bloom
    buds. WHY a domed cranium with two dark dots: it must punch a clean bone
    shape with two sockets at 32px. As a hidden bud it is sized >= the tiara
    skull so it survives peeking above the petals."""
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


# ── one FAT teardrop petal — the building block of every bloom ────────────────
def fat_petal(surf, hx, hy, pa, plen, pw, color, s, sheen=True):
    """A single CHUNKY rounded petal: a wide ink-keylined teardrop seated AT the
    heart and bulging outward, capped by a fat round lobe so its far end is
    rounded (never spiky). WHY a polygon body + a circle tip: the polygon gives
    the petal a believable taper from the heart, the round cap keeps the silhouette
    a soft blob at 32px — together they read as 'a fat little petal', not a spoke."""
    dx, dy = math.cos(pa), math.sin(pa)
    nx, ny = -dy, dx
    base = pw * 0.55                 # narrow-ish where it meets the heart
    midx, midy = hx + dx * plen * 0.62, hy + dy * plen * 0.62
    tipx, tipy = hx + dx * plen, hy + dy * plen
    body = [(hx + nx * base, hy + ny * base),
            (midx + nx * pw, midy + ny * pw),
            (tipx + nx * pw * 0.5, tipy + ny * pw * 0.5),
            (tipx - nx * pw * 0.5, tipy - ny * pw * 0.5),
            (midx - nx * pw, midy - ny * pw),
            (hx - nx * base, hy - ny * base)]
    # ink keyline first (a hair fatter), then fill, then a round tip-lobe so the
    # far end is a rounded mass; finally a slim sheen down the lit (upper) flank.
    pygame.draw.polygon(surf, INK, body)
    pygame.draw.circle(surf, INK, (int(tipx), int(tipy)), int(pw * 0.62))
    pygame.draw.polygon(surf, color, body)
    pygame.draw.circle(surf, color, (int(tipx), int(tipy)), int(pw * 0.5))
    # a darker valley-shade on the trailing flank gives the petal a fold
    pygame.draw.polygon(surf, lerp(color, INK, 0.30),
                        [(hx - nx * base * 0.6, hy - ny * base * 0.6),
                         (midx - nx * pw * 0.8, midy - ny * pw * 0.8),
                         (tipx - nx * pw * 0.3, tipy - ny * pw * 0.3),
                         (tipx, tipy), (hx, hy)])
    if sheen:
        pygame.draw.line(surf, lerp(color, (255, 255, 255), 0.5),
                         (int(hx + nx * base * 0.4), int(hy + ny * base * 0.4)),
                         (int(midx + nx * pw * 0.4), int(midy + ny * pw * 0.4)),
                         max(1, int(1.6 * s)))


# ── the six bloom-clusters — A-B-A-B-A-B, two NEST a skull bud ────────────────
def bloom(surf, kind, hx, hy, r, s, ang=0.0, hidden_skull=False):
    """Draw ONE arm-end bloom-cluster as a real FAT 5-petal flower-mass. WHY a LOW
    petal count of chunky teardrops (not a many-petal rosette): at 32px a dense
    rosette blurs to noise, so five thick `fat_petal` lobes radiate around a
    central relic HEART and overlap into one rounded blob — reads at 1× as 'a fat
    little flower', at 32px as 'a chunky rounded mass'.

    A and B are SIBLINGS of one bloom — same petal count + near-equal footprint —
    differing ONLY in the heart:
      A (even) = BONE petals around a ROSE/coral disc heart (coral-warm);
      B (odd)  = GOLD petals around a GOLD seed-pod with an attached TEAL dewdrop.

    When `hidden_skull` is set (the two mid arms), a `tiara_skull` BUD is NESTED
    INSIDE the bloom: its cranium sits BEHIND/among the petals with only the dome
    + eye-sockets peeking ABOVE the petal line while the petals overlap its lower
    jaw — composed as emerging-FROM-the-bloom, the scary-CUTE 'is that a skull in
    there?' discovery. The petals fan around `ang` (pointing outward) so the bloom
    opens like a hand away from the torso."""
    petal_col = BONE if kind % 2 == 0 else GOLD
    n_pet = 5
    plen = r * 1.18           # petal reach from heart — generous, makes a fat fan
    pw = r * 0.52             # petal half-width — fat lobes that overlap into a mass

    # WHY a nested skull is built in LAYERS, and the petals fan only DOWN-AND-OUT
    # (a CUP, not a full ring) on those two arms: r2's full ring buried the skull
    # so it died at 32px. The cranium BACK is laid down FIRST (behind petals); the
    # petals next, cupping BELOW/around the skull so they overlap only its lower
    # jaw; the skull FACE (lit dome + dark socket pair) LAST so its upper half peeks
    # clearly ABOVE the petal line — read as the skull EMERGING from the bloom.
    bud_dir = ang                 # the skull rises along the outward arm direction
    if hidden_skull:
        bx = hx + math.cos(bud_dir) * r * 0.46
        by = hy + math.sin(bud_dir) * r * 0.46
        bud_r = int(r * 0.92)            # >= tiara-skull footprint so it survives 32px
        # WHY the cranium BACK is laid in two values BEFORE the petals (a lit upper
        # dome over a darker lower cranium, the `tiara_skull` value structure): the
        # r2 bud was a flat BONE disc with a bright cap + flat sockets on top — a
        # scared-emoji read. Seating a BONE_D lower-cranium shadow under a BONE dome
        # makes the bud round like real bone instead of a sticker. Sheen kept off so
        # the third-eye stays the single brightest pixel.
        triad_circle(surf, BONE, (int(bx), int(by)), bud_r,
                     ow=max(1, int(1.4 * s)), core=False, sheen=False)
        lcx = bx + math.cos(bud_dir) * bud_r * 0.10   # lower cranium = toward torso
        lcy = by + math.sin(bud_dir) * bud_r * 0.10 + bud_r * 0.20
        pygame.draw.circle(surf, BONE_D, (int(lcx), int(lcy)), int(bud_r * 0.84))
        # petals fan a WIDER 240° cup that climbs HIGHER up the cranium flanks so the
        # upper petals OVERLAP onto the dome — the skull reads as half-buried/EMERGING
        # from the bloom, not perched on top of a full clear disc.
        span = math.radians(240)
        centre = bud_dir + math.pi
    else:
        span = math.radians(300)  # plain blooms: near-full ring with a torso notch
        centre = bud_dir

    for k in range(n_pet):
        pa = centre - span / 2 + span * (k / (n_pet - 1))
        fat_petal(surf, hx, hy, pa, plen, pw, petal_col, s)

    # central relic at the bloom HEART (coral-warm). On the two nested-skull arms
    # the heart shrinks and seats toward the petal-cup (opposite the skull).
    heart_k = 0.58 if hidden_skull else 1.0
    if hidden_skull:
        hcx = hx + math.cos(bud_dir + math.pi) * r * 0.30
        hcy = hy + math.sin(bud_dir + math.pi) * r * 0.30
        hx = int(hcx)
        hcy = int(hcy)
    else:
        hcy = hy
    if kind % 2 == 0:   # TYPE A — ROSE/coral disc heart in a gold collar
        triad_circle(surf, GOLD, (hx, hcy), int(r * 0.50 * heart_k), ow=max(1, int(1.2 * s)), core=False)
        triad_circle(surf, ROSE_CORAL, (hx, hcy), int(r * 0.38 * heart_k), ow=max(1, int(1 * s)), core=False, sheen=False)
        pygame.draw.circle(surf, ROSE_CORAL, (hx, hcy), max(1, int(r * 0.30 * heart_k)))
        pygame.draw.circle(surf, ROSE_CORAL_BR, (hx - int(r * 0.10), hcy - int(r * 0.11)),
                           max(1, int(r * 0.15 * heart_k)))
    else:   # TYPE B — GOLD seed-pod + an ATTACHED teal dewdrop
        triad_circle(surf, GOLD, (hx, hcy), int(r * 0.46 * heart_k), ow=max(1, int(1.2 * s)), core=True)
        for sgn in (-1, 1):
            pygame.draw.circle(surf, GOLD_D, (hx + sgn * int(r * 0.18 * heart_k), hcy + int(r * 0.04)),
                               max(1, int(r * 0.09 * heart_k)))
        # the teal dewdrop bead OVERLAPS the pod rim (attached, not a stray dot);
        # placed up-left on the pod so it clusters with the seed-pod mass.
        ddx = hx - int(r * 0.30 * heart_k)
        ddy = hcy - int(r * 0.30 * heart_k)
        pygame.draw.circle(surf, INK, (ddx, ddy), max(1, int(r * 0.21 * heart_k)))
        pygame.draw.circle(surf, TEAL, (ddx, ddy), max(1, int(r * 0.15 * heart_k)))
        pygame.draw.circle(surf, TEAL_BR, (ddx - int(r * 0.05), ddy - int(r * 0.05)),
                           max(1, int(r * 0.06 * heart_k)))

    # skull FACE drawn LAST: the LIT dome + paired eye-SOCKETS peek above the petal
    # line. WHY this now mirrors `tiara_skull` value handling instead of the r2
    # bright-cap-plus-flat-eyes treatment: the dome highlight is a SOFT off-centre
    # BONE_SH crescent (matching the lit upper cranium of the tiara skulls), the
    # sockets are SMALLER and filled BONE_DD/BONE_D (not solid INK) under a crisp
    # ink keyline — so the bud reads 'a little half-buried skull', tone gentle, and
    # the sockets no longer out-pull the rose third-eye. Drawn after the petals so
    # the emerging upper half stays clear while the upper petals overlap its flanks.
    if hidden_skull:
        # soft lit dome crescent toward the outward/up side — a HIGHLIGHT, not a
        # second bright disc; sized like the tiara skull's lit upper cranium so the
        # bud's value reads consistent with the 3 skulls directly above it.
        dcx = bx - math.cos(bud_dir) * bud_r * 0.20
        dcy = by - math.sin(bud_dir) * bud_r * 0.36 - bud_r * 0.12
        pygame.draw.circle(surf, BONE_SH, (int(dcx), int(dcy)), max(2, int(bud_r * 0.30)))
        # the eye-SOCKET pair — the 32px tell. Shrunk ~18% from r2 and seated close
        # so on downscale they still fuse into one dark eye-mass, but filled BONE_DD
        # under a thin INK keyline (no solid-black flat eyes) so the tone stays soft.
        pnx, pny = -math.sin(bud_dir), math.cos(bud_dir)
        for sgn in (-1, 1):
            ex = int(bx + sgn * pnx * bud_r * 0.34 + math.cos(bud_dir) * bud_r * 0.06)
            ey = int(by + sgn * pny * bud_r * 0.34 + math.sin(bud_dir) * bud_r * 0.06)
            pygame.draw.circle(surf, INK, (ex, ey), max(2, int(bud_r * 0.31)))
            pygame.draw.circle(surf, BONE_DD, (ex, ey), max(1, int(bud_r * 0.22)))
            pygame.draw.circle(surf, BONE_D, (ex - int(bud_r * 0.05), ey - int(bud_r * 0.05)),
                               max(1, int(bud_r * 0.10)))
        # nasal notch just inward of the socket line to finish the skull read —
        # also lightened to BONE_DD so the whole face holds one gentle value.
        nx2 = int(bx + math.cos(bud_dir) * bud_r * 0.26)
        ny2 = int(by + math.sin(bud_dir) * bud_r * 0.26)
        pygame.draw.circle(surf, INK, (nx2, ny2), max(1, int(bud_r * 0.13)))
        pygame.draw.circle(surf, BONE_DD, (nx2, ny2), max(1, int(bud_r * 0.07)))


# ── the six-arm radial starburst (the KIND tell — UNCHANGED from Mukha) ───────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr, relic_r):
    """Six fat bone arms splay in a wide symmetric STARBURST around the torso —
    cloned UNCHANGED from Mukha-Devi (sister, not a new KIND). Origin at a low
    shoulder line, top pair near-horizontal so a clean wedge of open sky stays
    above the crown. Returns the six hand centres for bloom placement."""
    shoulder = (sh_cx, sh_cy)
    arm_len = int(hr * 1.95)
    arm_th = int(12 * s)
    spread = [100, 64, 28]   # degrees off the vertical for the 3 arms per side
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


# ── the bloom-and-relic mother ────────────────────────────────────────────────
def draw_padma_mata(surf, cx, cy, s):
    """Pint-sized many-armed flower-goddess: Mukha's tiny chibi torso under the
    same six-arm radial starburst, but each hand opens a BLOOM-CLUSTER instead of
    juggling a weapon. A LOW 3-skull tiara + a glowing rose third eye keep the
    FACE reading inside the fan. Two mid blooms hide a tiny skull bud.
    `s` = unit scale around a ~130-unit figure."""

    head_c = (cx, cy - int(28 * s))
    hr = int(32 * s)
    relic_r = int(10 * s)
    bloom_r = int(11 * s)   # a touch fatter than Mukha's relic — petals need room

    # === SIX-ARM RADIAL FAN (drawn first → arms sit BEHIND torso & head) ======
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.82), s, hr, relic_r)

    # === LOWER BODY — a wide squat lotus-base (UNCHANGED) =====================
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

    # === TORSO — a SHORT rib barrel (UNCHANGED) ===============================
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

    # === SIX BLOOM-CLUSTERS — one in each hand (A-B-A-B-A-B) ===================
    # WHY drawn after torso, before head: they open at the fan tips so the outer
    # arc is six chunky flower-masses; the two MID arms (spread == 64°, one per
    # side) hide a skull bud — the only skull-bearing blooms.
    # WHY a clean A-B-A-B-A-B walk by radial index (not by spread-rank): r1 keyed
    # A/B off the arm angle, which read as A-B-A-A-B-A. Walking the six hands in
    # order alternates A/B cleanly around the fan. The two MID arms (spread 64°)
    # NEST a skull-bud regardless of their A/B heart — a bud reads in either heart.
    for i, (hx, hy, d) in enumerate(hands):
        oa = math.atan2(hy - rc_cy, hx - rc_cx)
        kind = i % 2
        hidden = (d == 64)
        # WHY the two skull-buds get a slightly LARGER footprint: at true 32px the
        # only way the buds beat the four plain blooms is a bigger, brighter mass
        # carrying the dark socket pair — so the mid arms read 'skull', not 'flower'.
        br = int(bloom_r * (1.22 if hidden else 1.0))
        bloom(surf, kind, hx, hy, br, s, ang=oa, hidden_skull=hidden)

    # === SKULL HEAD — chibi, scary-cute, three-eyed (UNCHANGED) ===============
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

    # === LOW 3-SKULL TIARA (UNCHANGED — the tight anchor) =====================
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


# ── the bloom-staff → pillar mirror ────────────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The bloom-staff IS the pillar: a banded bone shaft hung with bloom-clusters
    as side-pendants (mirroring her arm-ends) = the tileable shaft; the cap is a
    radiating petal-burst with a glowing rose bloom-heart at the gap — her own
    flowering language, symmetric and on-axis. `cap` names the END facing the GAP."""
    shaft_w = int(13 * s)
    bloom_pr = int(8 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    band_pitch = int(24 * s)
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
        rx = cx + side * (bw + int(11 * s))
        ry = y + int(2 * s)
        pygame.draw.line(surf, GOLD, (cx + side * bw, y), (rx, ry), max(1, int(1.6 * s)))
        # alternate A/B blooms hung as pendants; one band tucks a hidden bud.
        bloom(surf, idx % 2, rx, ry, bloom_pr, s,
              ang=math.radians(0 if side > 0 else 180),
              hidden_skull=(idx == 1))
        idx += 1
        y += band_pitch

    # === gap-edge cap: radiating petal-burst + glowing rose bloom-heart =======
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    burst_r = int(16 * s)
    grow = +1 if cap == "bottom" else -1
    for k in range(7):
        a = math.radians(-90 + (k - 3) * 24) if grow > 0 else math.radians(90 + (k - 3) * 24)
        tip = (cx + math.cos(a) * burst_r, cap_y + math.sin(a) * burst_r)
        # a fat bone petal instead of a thin finger (her flowering tell)
        nx, ny = -math.sin(a), math.cos(a)
        pw = burst_r * 0.26
        mid = (cx + math.cos(a) * burst_r * 0.55, cap_y + math.sin(a) * burst_r * 0.55)
        quad = [(cx, cap_y),
                (mid[0] + nx * pw, mid[1] + ny * pw),
                tip,
                (mid[0] - nx * pw, mid[1] - ny * pw)]
        triad_blob(surf, BONE, quad,
                   sheen_pts=[(cx, cap_y), (mid[0] + nx * pw, mid[1] + ny * pw), tip],
                   ow=max(1, int(1.2 * s)))
    collar_y = cap_y - grow * int(burst_r + int(4 * s))
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))
    # the glowing rose bloom-heart at the burst hub (the gap glow), coral-warm
    triad_circle(surf, GOLD, (cx, cap_y), int(7 * s), ow=max(1, int(1.4 * s)), core=False)
    pygame.draw.circle(surf, ROSE, (cx, cap_y), int(4 * s))
    pygame.draw.circle(surf, ROSE_CORAL, (cx, cap_y), int(3 * s))
    pygame.draw.circle(surf, ROSE_CORAL_BR, (cx - int(1 * s), cap_y - int(1 * s)), max(1, int(1.6 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_padma_mata(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def _load_font(size, bold=True):
    # FONT path FIVE levels up: padma_mata/ -> mukha_devi_kin/ -> batch2/ ->
    # skybit_devil/ -> docs/ -> <repo root>/game/assets. SysFont fallback so the
    # sheet still renders if the vendored TTF ever moves.
    here = os.path.dirname(os.path.abspath(__file__))
    root = here
    for _ in range(5):
        root = os.path.dirname(root)
    ttf = os.path.join(root, "game", "assets", "LiberationSans-Bold.ttf")
    if os.path.exists(ttf):
        return pygame.font.Font(ttf, size)
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)


def main():
    W, H = 1010, 820
    font_big = _load_font(30)
    font = _load_font(17)
    font_sm = _load_font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("PADMA-MATA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "bloom-and-relic mother  ·  Mukha-Devi SISTER (clone) · TIGHT · prominent · six FAT 5-petal blooms (A-B-A-B) · 2 half-buried skull-buds · round 3",
        True, LABEL_DIM), (270, 28))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 232, 1.55)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("Mukha's body/fan/face/tiara UNCHANGED; arm-ends open FAT 5-PETAL flower-masses.", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("A = rose/coral disc heart · B = gold seed-pod + ATTACHED teal dewdrop. Same footprint.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Two MID arms NEST a HALF-BURIED skull-bud: lit dome over darker cranium, eye-sockets,", True, LABEL_DIM), (14, 622))
    sheet.blit(font_sm.render("upper petals overlapping it (tiara-skull value, NOT a flat emoji). 3 tiara + 2 buds = 5.", True, LABEL_DIM), (14, 638))

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
    sheet.blit(font.render("Pillar — bloom-staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("banded bone shaft hung with bloom-pendants =", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("shaft; petal-burst + glowing rose heart caps", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("the gap (mirrored top↔bottom, symmetric on-axis)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky + blackout proof =====
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_padma_mata(big, 55 * SS, 58 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (110, 110))
        return grow_outline(small, INK + (255,), 1)

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

    # blackout silhouette proof beside the night chip
    def blackout(src):
        sil = src.copy()
        arr = pygame.surfarray.pixels_alpha(sil)
        del arr
        mask = pygame.mask.from_surface(src)
        out = pygame.Surface(src.get_size(), pygame.SRCALPHA)
        for x in range(src.get_width()):
            for yy in range(src.get_height()):
                if mask.get_at((x, yy)):
                    out.set_at((x, yy), (12, 10, 14, 255))
        return out

    bo = blackout(chip)
    box_x = panel_x + 192
    pygame.draw.rect(sheet, (210, 210, 216), (box_x, night_y, 110, 110))
    pygame.draw.rect(sheet, INK, (box_x, night_y, 110, 110), 1)
    sheet.blit(bo, (box_x, night_y))
    sheet.blit(font_sm.render("blackout", True, LABEL_DIM), (box_x + 2, night_y - 16))
    sheet.blit(font_sm.render("(silhouette)", True, LABEL_DIM), (box_x - 2, night_y + 114))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 192
    vgrad(sheet, (px2, day_y, 56, 110), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 110), 1)
    sheet.blit(pc, (px2 + 6, day_y - 4))
    sheet.blit(font_sm.render("pillar 32px", True, LABEL_DIM), (px2 - 2, day_y - 16))

    sheet.blit(font.render("Pinned palette (+ coral heart)", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (BONE, "dusty rose-bone"), (BONE_D, "mauve-bone shade"),
        (ROSE, "magenta relic-glow"), (ROSE_CORAL, "coral bloom-heart"),
        (GOLD, "gold petal-trim"), (TEAL, "teal dewdrop"),
        (THIRD_EYE, "third-eye"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  SISTER of Mukha-Devi (clone): same fan/face/tiara/palette; "
        "arm-ends swapped to bloom-clusters + 2 hidden skull-buds; coral nudge in bloom hearts only. procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
