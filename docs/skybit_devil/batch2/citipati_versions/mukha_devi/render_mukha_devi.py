"""
Round-1 concept renderer for MUKHA-DEVI — the six-armed wrathful bone-mother
(Citipati-versions set, concept #3). Headless Pygame; ELEVATED pipeline
(supersample SS=6 → smoothscale) so the radial arm-fan + six micro-relics stay
crisp at downscale. Keeps the shipped house grammar: flat saturated fills, hard
1-2px ink keyline (28,22,26), dark-core → flat-fill → top-left rim-sheen triad,
1px alpha-grown outline, chibi proportions, scary-CUTE; procedural-only.

WHY this is the radial-fan KIND (the ONLY many-armed silhouette in the brood):
six fat bone arms splay in a wide symmetric STARBURST around a tiny chibi torso —
a shape no single-pair humanoid skeleton can collide with. Each hand cradles ONE
holy weapon, so the outer arc reads as six DISTINCT micro-relic blobs, never a
fringe. The radial fan FRAMES the face; it must not swallow it — so the third
eye + a LOW 3-skull tiara are pinned forward, demonstrably fewer skulls and a
shallower arc than Citipati's 5-skull crown.

WHY warm-dusty rose-bone, NOT white: the cross-set pin bans echoing Leyak's
ash-white. The bone mass is pushed clearly warm-mauve; magenta-rose is the
single relic GLOW, gold a thin relic-trim, teal a literal bell sliver.

WHY the relic-chakra-staff IS the pillar: a banded bone shaft hung with the six
micro-relics as ring-pendants tiles as the repeatable shaft; the cap is a small
radiating hand-fan / lotus-burst with a glowing bell relic at the gap — a
symmetric continuation of the creature's own radial language.

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
# Dusty rose-bone is the dominant mass — clearly WARM-dusty, NOT white (anti-Leyak
# ash). Everything else is a thin accent so the relic-glow magenta reads focal.
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
TEAL      = ( 64, 170, 166)   # teal bell-sliver — a literal sliver
TEAL_BR   = (140, 222, 216)
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = (232,  86, 150)   # third-eye glow (rose so it reads as her power-focus)
THIRD_BR  = (255, 196, 224)

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


# ── the six holy relics — only TWO alternating TYPES (A-B-A-B-A-B) ────────────
def relic(surf, kind, cx, cy, r, s, ang=0.0):
    """Draw ONE of the six micro-relics. WHY only TWO alternating TYPES (a round
    rose disc-relic and a gold flame/triangle-relic), not six distinct weapons:
    at 32px six fussy silhouettes blur to mush and pull visual weight out to the
    rim, starving the face — the AD ruling. Six even GLOW-CAPS in a ring is the
    radial read that survives, so each is a clean chunky mass with the same
    footprint, rose-vs-gold giving rhythm instead of per-weapon detail. `kind`
    is taken mod 2 so the arc reads A-B-A-B-A-B."""
    gx = cx + int(math.cos(ang) * r * 0.55)
    gy = cy + int(math.sin(ang) * r * 0.55)
    if kind % 2 == 0:   # TYPE A — round rose disc-relic in a gold ring
        triad_circle(surf, GOLD, (gx, gy), int(r * 0.95), ow=max(1, int(1.4 * s)), core=False)
        triad_circle(surf, ROSE, (gx, gy), int(r * 0.6), ow=max(1, int(1 * s)), core=False)
        pygame.draw.circle(surf, ROSE_BR, (gx - int(r * 0.18), gy - int(r * 0.2)),
                           max(1, int(r * 0.26)))
    else:   # TYPE B — gold flame / triangle-relic with a rose ember at its heart
        tip = [(gx + math.cos(ang - math.pi / 2) * r * 1.15,
                gy + math.sin(ang - math.pi / 2) * r * 1.15),
               (gx + math.cos(ang + math.pi / 2 + 0.55) * r * 0.95,
                gy + math.sin(ang + math.pi / 2 + 0.55) * r * 0.95),
               (gx + math.cos(ang + math.pi / 2 - 0.55) * r * 0.95,
                gy + math.sin(ang + math.pi / 2 - 0.55) * r * 0.95)]
        triad_blob(surf, GOLD, tip, ow=max(1, int(1.4 * s)))
        pygame.draw.circle(surf, ROSE, (gx, gy), max(1, int(r * 0.4)))
        pygame.draw.circle(surf, ROSE_BR, (gx - int(r * 0.12), gy - int(r * 0.14)),
                           max(1, int(r * 0.18)))


# ── a single ornamental tiara-skull (reused for tiara + pillar relics) ────────
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


# ── the six-arm radial starburst (the KIND tell) ──────────────────────────────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr, relic_r):
    """Six fat bone arms splay in a wide symmetric STARBURST around the torso —
    the ONLY radial silhouette in the brood. WHY few-and-FAT: at 32px thin arms
    tangle; six chunky bone limbs hold a clean star, and each hand cradles one
    micro-relic so the outer arc reads as six even glow-caps in a ring.

    WHY the arms now ORIGIN at a low SHOULDER line and the topmost pair splays
    near-HORIZONTAL: the AD ruling is that the fan must FRAME the face, not cap
    it. With the origin dropped below the head and NO arm aimed straight up, a
    clean wedge of negative space opens ABOVE the tiara — the fan brackets the
    skull like a peacock tail behind it. The arc spans ≈ ±100° off vertical
    (top arms near-horizontal, mid-diagonal, low-down), three per side, so the
    silhouette stays a peripheral star and never reaches over the crown.
    Returns the six hand centres for relic placement."""
    shoulder = (sh_cx, sh_cy)
    arm_len = int(hr * 1.95)
    arm_th = int(12 * s)
    # NO near-vertical arm: top arm is near-horizontal so the crown stays open.
    spread = [100, 64, 28]   # degrees off the vertical for the 3 arms per side
    order = []
    for sgn in (-1, 1):
        for d in spread:
            a = math.radians(-90 + sgn * d)
            order.append((sgn, d, a))
    # draw the lowest (most-down) arms first so the upper splay overlaps cleanly
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
    return [(int(h[2][0]), int(h[2][1])) for h in hands]


# ── the wrathful bone-mother ──────────────────────────────────────────────────
def draw_mukha_devi(surf, cx, cy, s):
    """Pint-sized many-armed death-goddess: a tiny chibi torso under a wide
    six-arm radial starburst, each hand juggling a holy weapon. A LOW 3-skull
    tiara + a glowing rose third eye keep the FACE reading inside the fan.
    `s` = unit scale around a ~130-unit figure."""

    # WHY a BIG head (≈40% of body height) over a short torso: the AD ruling is
    # that at 32px the six arms swallow a small skull. A chibi-large head plus a
    # squat torso + wide base keeps the FACE the dominant mass and reads as a
    # pint-sized deity, not a candelabra/totem.
    head_c = (cx, cy - int(28 * s))
    hr = int(32 * s)
    relic_r = int(10 * s)

    # === SIX-ARM RADIAL FAN (drawn first → arms sit BEHIND torso & head) ======
    # WHY behind, and WHY the origin sits LOW at the shoulder/temple line: the fan
    # must FRAME the face, so it sprouts from below the head and splays sideways,
    # leaving open sky above the crown for the tiara to read against.
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.82), s, hr, relic_r)

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
    # lotus petal grooves
    for k in range(-2, 3):
        px = cx + int(k * 11 * s)
        pygame.draw.line(surf, BONE_DD, (px, base_y - int(15 * s)),
                         (px, base_y + int(8 * s)), max(1, int(1.4 * s)))
    # a rose seed-glow at the lotus heart — kept a touch deeper than the third
    # eye so it stays a SECONDARY focal and never competes for "brightest pixel."
    pygame.draw.circle(surf, ROSE_D, (cx, base_y - int(3 * s)), int(5 * s))
    pygame.draw.circle(surf, ROSE, (cx - int(1 * s), base_y - int(4 * s)), max(1, int(2 * s)))

    # === TORSO — a SHORT rib barrel (squat, so head + base hold the mass) =====
    # WHY shortened: a tall columnar torso reads as a candelabra; a stubby cage
    # tucked under the big head shifts weight low for chibi proportion.
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
    # a thin rose prayer-cord sash (linear accent, never a mass)
    pygame.draw.line(surf, ROSE, (rc_cx - int(rc_w * 0.42), rc_cy + int(2 * s)),
                     (rc_cx + int(rc_w * 0.42), rc_cy - int(2 * s)), max(1, int(2 * s)))
    pygame.draw.line(surf, ROSE_BR, (rc_cx - int(rc_w * 0.3), rc_cy + int(1 * s)),
                     (rc_cx, rc_cy - int(1 * s)), max(1, int(1 * s)))

    # === SIX MICRO-RELICS — one in each hand (six DISTINCT blobs) =============
    # WHY drawn after torso, before head: they ride out at the fan tips so the
    # outer arc is six even shapes; the head still overdraws nothing of them.
    for i, (hx, hy) in enumerate(hands):
        # relic points outward from torso centre
        oa = math.atan2(hy - rc_cy, hx - rc_cx)
        relic(surf, i % 6, hx, hy, relic_r, s, ang=oa)

    # === SKULL HEAD — chibi, scary-cute, three-eyed (the framed FACE) =========
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two big lower sockets — scary-CUTE, kept a NOTCH DIMMER than the third eye
    # (dark hollow + small deep-rose pin, NO hot-bright core) so the 3-eye
    # triangle reads as a triangle pointing UP to the brightest brow-eye.
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.25))
        pygame.draw.circle(surf, ROSE_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.12))
    # THIRD EYE — the single BRIGHTEST pixel on the whole sprite (AD hard rule).
    # WHY a fat vertical rose slit with a hot white-rose core, central on the
    # brow: it must survive at 32px as the one magenta dot that says "looking at
    # you" and anchor the face inside the arm-fan. Sized bigger than the sockets
    # so the three-eye triangle holds; sockets stay deliberately dimmer.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.34)
    pygame.draw.ellipse(surf, INK, (tex - int(7 * s), tey - int(9 * s), int(14 * s), int(18 * s)))
    pygame.draw.ellipse(surf, ROSE, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, ROSE_BR, (tex - int(4 * s), tey - int(5 * s), int(8 * s), int(10 * s)))
    pygame.draw.circle(surf, THIRD_BR, (tex - int(1 * s), tey - int(2 * s)), max(2, int(3.2 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(2 * s)),
                       max(1, int(1.6 * s)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    # grinning tooth row (cute, not gory) — a wrathful bared grin
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.48), my),
                     (head_c[0] + int(hr * 0.48), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.15), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.15), my + int(hr * 0.13)), max(1, int(1 * s)))
    # two small fangs at the corners (wrathful tell)
    for sgn in (-1, 1):
        fx = head_c[0] + sgn * int(hr * 0.40)
        pygame.draw.polygon(surf, BONE_SH,
                            [(fx - int(2 * s), my), (fx + int(2 * s), my),
                             (fx, my + int(hr * 0.22))])

    # === LOW 3-SKULL TIARA (the hard tell — fewer + lower than Citipati's 5) ==
    # WHY it now seats in the OPEN SKY above the crown: with no arm aimed up, a
    # clean wedge of negative space sits over the head, so the 3-skull band reads
    # as a low dark-toothed crown ON the head against the sky — not buried in the
    # arm cluster. A SHALLOW ~70° arc + only THREE skulls keeps it demonstrably
    # lower/fewer than Citipati's wide 5-skull crown. Centre skull lit rose.
    tiara_r = int(hr * 0.96)
    tiara_skull_r = int(hr * 0.30)
    band_pts = []
    for i in range(9):
        a = math.radians(235 + i * (70 / 8))   # shallow ~70° arc, seated on brow
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(6 * s))
    pygame.draw.lines(surf, GOLD, False, band_pts, int(3 * s))
    pygame.draw.lines(surf, GOLD_BR, False, band_pts[:5], max(1, int(1.2 * s)))
    # exactly THREE skulls, evenly across the shallow arc, sitting up in open sky
    for i in range(3):
        a = math.radians(242 + i * (56 / 2))
        sx = head_c[0] + math.cos(a) * tiara_r
        sy = head_c[1] + math.sin(a) * tiara_r
        tiara_skull(surf, int(sx), int(sy), tiara_skull_r, s, lit=(i == 1))


# ── the relic-chakra-staff → pillar mirror ────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The relic-chakra-staff IS the pillar: a banded bone shaft hung with the
    six micro-relics as ring-pendants = the tileable shaft; the cap is a small
    radiating hand-fan / lotus-burst with a glowing bell relic at the gap — the
    creature's own radial language, symmetric and on-axis.

    `cap` names the END that faces the GAP."""
    shaft_w = int(13 * s)
    relic_r = int(7 * s)
    # central ink rod the bands thread onto
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    # === banded bone shaft + six relic ring-pendants =========================
    band_pitch = int(22 * s)
    cap_room = int(34 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    idx = 0
    while y <= b1:
        # a fat bone band segment with a hard groove (the shaft tile)
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
        # a relic ring-pendant hung off alternating sides (the six relics)
        side = -1 if (idx % 2 == 0) else 1
        rx = cx + side * (bw + int(9 * s))
        ry = y + int(2 * s)
        # the hanging ring
        pygame.draw.line(surf, GOLD, (cx + side * bw, y), (rx, ry), max(1, int(1.6 * s)))
        relic(surf, idx % 6, rx, ry, relic_r, s, ang=math.radians(0 if side > 0 else 180))
        idx += 1
        y += band_pitch

    # === gap-edge cap: radiating hand-fan / lotus-burst + glowing bell ========
    # WHY a small radial burst with a lit bell at the gap: it mirrors the
    # creature's six-arm fan in miniature and glows toward the gap, symmetric and
    # never wider than the shaft's pendant span (not top-heavy).
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    burst_r = int(16 * s)
    grow = +1 if cap == "bottom" else -1   # the fan opens toward the gap
    # the radiating bone fingers / petals
    for k in range(7):
        a = math.radians(-90 + (k - 3) * 24) if grow > 0 else math.radians(90 + (k - 3) * 24)
        tip = (cx + math.cos(a) * burst_r, cap_y + math.sin(a) * burst_r)
        mid = (cx + math.cos(a) * burst_r * 0.5, cap_y + math.sin(a) * burst_r * 0.5)
        pygame.draw.line(surf, INK, (cx, cap_y), tip, max(2, int(4 * s)))
        pygame.draw.line(surf, BONE, (cx, cap_y), tip, max(1, int(2.4 * s)))
        triad_circle(surf, BONE, (int(tip[0]), int(tip[1])), max(1, int(2.4 * s)),
                     ow=max(1, int(1 * s)), core=False, sheen=False)
    # a thin gold collar where the burst meets the shaft
    collar_y = cap_y - grow * int(burst_r + int(4 * s))
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))
    # the glowing bell relic at the burst hub (the gap glow)
    triad_circle(surf, BONE, (cx, cap_y), int(7 * s), ow=max(1, int(1.4 * s)), core=False)
    pygame.draw.arc(surf, TEAL, (cx - int(6 * s), cap_y - int(6 * s), int(12 * s), int(12 * s)),
                    math.radians(200), math.radians(340), max(2, int(2.4 * s)))
    pygame.draw.circle(surf, ROSE, (cx, cap_y), int(3 * s))
    pygame.draw.circle(surf, ROSE_BR, (cx - int(1 * s), cap_y - int(1 * s)), max(1, int(1.6 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_mukha_devi(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


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
    sheet.blit(font_big.render("MUKHA-DEVI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "six-armed wrathful bone-mother  ·  KIND: radial-fan · warm rose-bone · LOW 3-skull tiara · 6 glow-caps (2 alt types) · round 2",
        True, LABEL_DIM), (260, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 232, 1.55)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("BIG chibi head FRAMED by a low-origin six-arm fan (no arm over the crown).", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("Third eye = the single BRIGHTEST pixel; sockets a notch dimmer (3-eye triangle).", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Six glow-caps = TWO alternating types. LOW 3-skull tiara in open sky over head.", True, LABEL_DIM), (14, 622))

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
    sheet.blit(font.render("Pillar — relic-chakra-staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("banded bone shaft hung with 6 relic-pendants =", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("shaft; hand-fan / lotus-burst + glowing bell caps", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("the gap (mirrored top↔bottom, symmetric on-axis)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_mukha_devi(big, 55 * SS, 58 * SS, (32 / 150.0) * SS)
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

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (BONE, "dusty rose-bone"), (BONE_D, "mauve-bone shade"),
        (ROSE, "magenta relic-glow"), (ROSE_D, "deep-rose"),
        (GOLD, "gold relic-trim"), (TEAL, "teal bell-sliver"),
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
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (28,22,26) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
