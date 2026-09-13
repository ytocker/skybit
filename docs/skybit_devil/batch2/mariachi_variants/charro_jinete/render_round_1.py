"""
El Charro Jinete — skeletal charro rider on a rearing alebrije bone-horse
(MARIACHI-LINEAGE warm-skeleton family, BLEND facet / grand-boss anchor).

A two-body parade "centaur of bones": the only multi-body, rearing-horse+rider
KIND in the family. The BLEND reads at once — exposed anatomy (mount AND rider
are bone), painted calaca decoration (embroidered charro suit + sugar-skull
horse + woven zarape), and performance motion (the horse rears, the rider waves
a sombrero). It is the tallest, most dramatic top-action silhouette of the set.

House style (inherited from the Mariachi anchor): CHIBI proportions, FLAT
saturated fills + hard 1-2px ink keylines, form via the dark-core -> flat-fill
-> top-left rim-sheen TRIAD (never a soft gradient), silhouette POP via a 1px
outline grown from the alpha mask, supersample SS=4 -> smoothscale.

CRITICAL red-split pin: the rust is HELD in a desaturated BRICK/LEATHER lane
(176,70,56) — never brightened toward Zapateada's pink-rose or Comelona's
orange-chile. It rides WITH ochre + turquoise as the full house triad, so the
boss reads as the richest warm palette of the family while the red stays the
darkest/brownest of the three warm reds.

Two-body TOP-HEAVY guard: the action lives ENTIRELY in the creature. The
prop->pillar stays SLIM + SYMMETRIC on-axis — a single narrow lance shaft with
a compact horse-skull finial seated tight on the shaft axis (NOT a second
rider-and-mount). The mirror reads balanced.

Run headless:  SDL_VIDEODRIVER=dummy python render_round_1.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (locked brief, exact hexes) ───────────────────────────────
RUST        = (176,  70,  56)   # BRICK/LEATHER zarape + jacket (DESATURATED)
OCHRE       = (214, 162,  76)   # ochre saddle + hat
TURQ        = ( 58, 172, 164)   # turquoise zarape-stripe + browband (co-lead)
BONE        = (236, 224, 198)   # warm bone (both bodies)
BONE_SHADE  = (176, 150, 108)   # tan-bone shade
MARIGOLD    = (240, 150,  46)   # marigold finial / browband flower
INK         = ( 28,  22,  22)   # keyline ink
SHEEN       = (250, 240, 216)   # top-left rim sheen

# Derived working tones (kept strictly inside the pinned families).
BONE_CORE   = (158, 134,  98)   # dark-core under bone
OCHRE_CORE  = (158, 116,  50)   # dark-core under ochre
OCHRE_SHEEN = (244, 206, 138)   # ochre top-left sheen
# Rust held in the brick lane: a deep brown-brick core (not a chile/rose core)
# and a muted brick sheen — never a bright-rose highlight.
RUST_CORE   = (112,  42,  34)
RUST_SHEEN  = (208, 116,  96)   # muted brick sheen, stays brown-leaning
TURQ_CORE   = ( 32, 110, 106)
TURQ_SHEEN  = (132, 216, 206)
MARI_CORE   = (176,  96,  26)
MARI_SHEEN  = (252, 200, 110)
SOCKET_CORE = ( 40,  30,  26)
SOCKET_FILL = ( 56,  42,  36)
SOCKET_SHEEN= ( 94,  72,  60)

SS = 4   # supersample factor


# ── geometry / triad helpers (house grammar, shared with the anchor) ─────────

def _ell(surf, color, cx, cy, rx, ry):
    pygame.draw.ellipse(surf, color,
                        (int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2)))


def triad_ellipse(surf, cx, cy, rx, ry, core, fill, sheen, outline=INK):
    """dark-core -> flat-fill -> top-left rim-sheen on an ellipse mass, with a
    hard ink keyline. Reads as form without any soft gradient."""
    if outline is not None:
        _ell(surf, outline, cx, cy, rx + SS, ry + SS)
    _ell(surf, core, cx, cy, rx, ry)
    _ell(surf, fill, cx, cy, rx - SS * 0.7, ry - SS * 0.7)
    _ell(surf, sheen, cx - rx * 0.34, cy - ry * 0.36, rx * 0.5, ry * 0.42)


def triad_poly(surf, pts, core, fill, sheen, outline=INK, sheen_pts=None,
               inset_amt=0.16):
    """Triad on an arbitrary polygon: ink keyline (fat stroke), core fill, inset
    fill, then an optional top-left sheen sliver polygon."""
    if outline is not None:
        pygame.draw.polygon(surf, outline, pts)
        pygame.draw.polygon(surf, outline, pts, SS * 2)
    pygame.draw.polygon(surf, core, pts)
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    inset = [(p[0] + (cx - p[0]) * inset_amt, p[1] + (cy - p[1]) * inset_amt)
             for p in pts]
    pygame.draw.polygon(surf, fill, inset)
    if sheen_pts:
        pygame.draw.polygon(surf, sheen, sheen_pts)


def grow_outline(surf, color=INK, thickness=1):
    """1px (post-scale) outline grown from the alpha mask — the silhouette POP.
    Run at supersample scale so it survives smoothscale."""
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) > 2:
        pygame.draw.lines(surf, color, True, outline_pts, max(1, thickness * SS))


def _rot(pts, cx, cy, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return out


def bone_limb(surf, p0, p1, p2, w):
    """A two-segment bone limb with chunky chibi joint knobs — the family's
    exposed-anatomy leg unit, reused for horse legs and the rider."""
    for a, b in ((p0, p1), (p1, p2)):
        pygame.draw.line(surf, INK, a, b, int(w + SS * 1.7))
    for a, b in ((p0, p1), (p1, p2)):
        pygame.draw.line(surf, BONE_SHADE, a, b, int(w))
        pygame.draw.line(surf, BONE, a, b, int(w * 0.5))
    for p in (p0, p1, p2):
        triad_ellipse(surf, p[0], p[1], w * 0.62, w * 0.62, BONE_CORE, BONE, SHEEN)


# ── the creature ─────────────────────────────────────────────────────────────

def draw_jinete(target_size):
    """A chibi bone-HORSE rearing up on its hind legs — front hooves pawing the
    air, arched cervical spine, big triad-lit skull-muzzle with a painted
    sugar-skull brow + marigold browband, exposed ribcage barrel, a woven rust
    zarape saddle-blanket — carrying a tiny charro skeleton RIDER seated high,
    one bone arm thrust up waving a small sombrero, the other on the rein. The
    rear + the raised arm carry the action; two clearly skeletal stacked bodies
    make the grandest boss silhouette in the family."""
    S = target_size * SS
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S * 0.5

    # ── HIND LEGS planted (drawn first, behind the barrel) ────────────────────
    # The horse is reared, so the hind legs are the weight-bearing base, splayed
    # for a stable stance; the haunch sits low-centre.
    haunch_x, haunch_y = cx + S * 0.085, S * 0.66
    legw = S * 0.052
    # Far hind leg (player-left, slightly tucked).
    bone_limb(surf,
              (haunch_x - S * 0.04, haunch_y),
              (cx - S * 0.085, S * 0.80),
              (cx - S * 0.045, S * 0.945), legw * 0.92)
    # Near hind leg (player-right, planted out for the rear balance).
    bone_limb(surf,
              (haunch_x + S * 0.02, haunch_y),
              (cx + S * 0.16, S * 0.79),
              (cx + S * 0.225, S * 0.945), legw)
    # Hooves — small rust hoof-caps so the planted feet read in the silhouette.
    for hx in (cx - S * 0.045, cx + S * 0.225):
        triad_ellipse(surf, hx, S * 0.95, S * 0.05, S * 0.034,
                      RUST_CORE, RUST, RUST_SHEEN)

    # ── HAUNCH + BARREL (the horse body, rearing back at a diagonal) ──────────
    # Big rounded rump tilting back, leading up the arched spine to the chest.
    triad_ellipse(surf, haunch_x, haunch_y, S * 0.135, S * 0.155,
                  BONE_CORE, BONE, SHEEN)
    # Exposed ribcage barrel — the chest mass, raised and forward as it rears.
    chest_x, chest_y = cx - S * 0.05, S * 0.50
    triad_ellipse(surf, chest_x, chest_y, S * 0.155, S * 0.145,
                  BONE_CORE, BONE, SHEEN)
    # Visible rib bands curving over the barrel (anatomy tell).
    for i in range(4):
        ry = chest_y - S * 0.06 + i * S * 0.045
        pygame.draw.arc(surf, BONE_SHADE,
                        (int(chest_x - S * 0.135), int(ry - S * 0.05),
                         int(S * 0.27), int(S * 0.13)),
                        math.pi * 1.08, math.pi * 1.92, max(2, int(SS * 1.5)))
        pygame.draw.arc(surf, INK,
                        (int(chest_x - S * 0.135), int(ry - S * 0.05),
                         int(S * 0.27), int(S * 0.13)),
                        math.pi * 1.18, math.pi * 1.82, max(1, int(SS * 0.8)))

    # ── ARCHED CERVICAL SPINE rising up-left to the skull-muzzle ──────────────
    neck_base = (chest_x - S * 0.06, chest_y - S * 0.09)
    neck_top  = (cx - S * 0.215, S * 0.305)
    # Neck as a tapered bone column; vertebra knobs march up the arch.
    neck_pts = [
        (neck_base[0] + S * 0.075, neck_base[1] + S * 0.02),
        (neck_base[0] - S * 0.045, neck_base[1] - S * 0.01),
        (neck_top[0] - S * 0.03, neck_top[1] + S * 0.02),
        (neck_top[0] + S * 0.055, neck_top[1] + S * 0.01),
    ]
    triad_poly(surf, neck_pts, BONE_CORE, BONE, SHEEN)
    for t in range(5):
        tt = t / 4.0
        vx = neck_base[0] + (neck_top[0] - neck_base[0]) * tt + S * 0.012
        vy = neck_base[1] + (neck_top[1] - neck_base[1]) * tt
        triad_ellipse(surf, vx, vy, S * 0.026, S * 0.026, BONE_CORE, BONE, SHEEN)
    # Bone mane — a row of short ink+bone tufts along the back of the neck arch.
    for t in range(6):
        tt = t / 5.0
        mx = neck_base[0] + (neck_top[0] - neck_base[0]) * tt - S * 0.05
        my = neck_base[1] + (neck_top[1] - neck_base[1]) * tt - S * 0.01
        pygame.draw.line(surf, INK, (mx, my),
                         (mx - S * 0.055, my - S * 0.03), max(2, int(SS * 1.8)))
        pygame.draw.line(surf, BONE, (mx, my),
                         (mx - S * 0.05, my - S * 0.028), max(1, int(SS * 0.9)))

    # ── HORSE SKULL-MUZZLE (big, triad-lit, sugar-skull decorated) ────────────
    sk_x, sk_y = neck_top[0] - S * 0.02, neck_top[1] - S * 0.02
    # Long cranium + a forward muzzle snout — horse-skull read, not a round head.
    triad_ellipse(surf, sk_x, sk_y, S * 0.10, S * 0.11, BONE_CORE, BONE, SHEEN)
    muzzle = [
        (sk_x - S * 0.085, sk_y + S * 0.02),
        (sk_x - S * 0.185, sk_y + S * 0.055),
        (sk_x - S * 0.185, sk_y + S * 0.115),
        (sk_x - S * 0.07,  sk_y + S * 0.11),
    ]
    triad_poly(surf, muzzle, BONE_CORE, BONE, SHEEN)
    # Nostril slit + jaw line.
    pygame.draw.ellipse(surf, SOCKET_CORE,
                        (int(sk_x - S * 0.175), int(sk_y + S * 0.07),
                         int(S * 0.03), int(S * 0.022)))
    pygame.draw.line(surf, INK, (sk_x - S * 0.18, sk_y + S * 0.105),
                     (sk_x - S * 0.075, sk_y + S * 0.10), max(1, int(SS)))
    # Bone teeth row along the muzzle underside.
    for k in range(4):
        txx = sk_x - S * 0.16 + k * S * 0.026
        pygame.draw.line(surf, BONE, (txx, sk_y + S * 0.108),
                         (txx, sk_y + S * 0.124), max(1, int(SS)))
        pygame.draw.line(surf, INK, (txx + S * 0.013, sk_y + S * 0.108),
                         (txx + S * 0.013, sk_y + S * 0.124), max(1, int(SS * 0.6)))
    # Pricked bone EARS at the top of the cranium (rearing alert).
    for sgn, base in ((-1, sk_x + S * 0.02), (1, sk_x + S * 0.07)):
        ear = [
            (base, sk_y - S * 0.085),
            (base + S * 0.018, sk_y - S * 0.16),
            (base + S * 0.05, sk_y - S * 0.08),
        ]
        triad_poly(surf, ear, BONE_CORE, BONE, SHEEN, inset_amt=0.22)
    # Sugar-skull socket — a big DotD eye with an ochre marigold-petal ring.
    eye_x, eye_y = sk_x - S * 0.01, sk_y - S * 0.005
    triad_ellipse(surf, eye_x, eye_y, S * 0.038, S * 0.044,
                  SOCKET_CORE, SOCKET_FILL, SOCKET_SHEEN, outline=None)
    for k in range(8):
        a = k * math.tau / 8
        px = eye_x + math.cos(a) * S * 0.05
        py = eye_y + math.sin(a) * S * 0.056
        pygame.draw.circle(surf, OCHRE, (int(px), int(py)), max(1, int(SS * 1.2)))
    pygame.draw.circle(surf, INK, (int(eye_x), int(eye_y)), int(S * 0.017))
    # Painted sugar-skull brow scroll (turquoise + rust filigree dots).
    pygame.draw.arc(surf, TURQ,
                    (int(sk_x - S * 0.055), int(sk_y - S * 0.075),
                     int(S * 0.13), int(S * 0.07)),
                    math.pi * 0.05, math.pi * 0.95, max(2, int(SS * 1.4)))
    for k in range(3):
        dx = sk_x - S * 0.03 + k * S * 0.03
        pygame.draw.circle(surf, RUST, (int(dx), int(sk_y - S * 0.05)),
                           max(1, int(SS * 1.1)))
    # MARIGOLD BROWBAND across the forehead (ochre + marigold flower at centre).
    pygame.draw.line(surf, OCHRE, (sk_x - S * 0.07, sk_y + S * 0.035),
                     (sk_x + S * 0.085, sk_y + S * 0.005), max(3, int(SS * 3)))
    pygame.draw.line(surf, OCHRE_CORE, (sk_x - S * 0.07, sk_y + S * 0.045),
                     (sk_x + S * 0.085, sk_y + S * 0.015), max(1, int(SS)))
    triad_ellipse(surf, sk_x + S * 0.01, sk_y + S * 0.025, S * 0.026, S * 0.026,
                  MARI_CORE, MARIGOLD, MARI_SHEEN)

    # ── FRONT LEGS pawing the air (the rear-motion tell) ──────────────────────
    # Both front legs lifted and curled up under the chest, hooves pawing forward
    # — the unmistakable rearing-horse gesture, the silhouette's mid-left action.
    shoulder = (chest_x - S * 0.06, chest_y - S * 0.02)
    bone_limb(surf, shoulder,
              (chest_x - S * 0.175, chest_y + S * 0.02),
              (chest_x - S * 0.255, chest_y - S * 0.055), legw * 0.86)
    bone_limb(surf, (shoulder[0] + S * 0.03, shoulder[1] + S * 0.04),
              (chest_x - S * 0.13, chest_y + S * 0.10),
              (chest_x - S * 0.215, chest_y + S * 0.055), legw * 0.86)
    for hx, hy in ((chest_x - S * 0.255, chest_y - S * 0.055),
                   (chest_x - S * 0.215, chest_y + S * 0.055)):
        triad_ellipse(surf, hx, hy, S * 0.044, S * 0.03,
                      RUST_CORE, RUST, RUST_SHEEN)

    # ── ZARAPE saddle-blanket (woven rust + turquoise + ochre stripe banding) ─
    # Draped over the barrel/haunch where the rider sits — the decoration facet,
    # held in the brick-rust lane with hard woven-stripe banding.
    zar = [
        (chest_x + S * 0.02, chest_y - S * 0.05),
        (haunch_x + S * 0.11, haunch_y - S * 0.10),
        (haunch_x + S * 0.135, haunch_y + S * 0.05),
        (chest_x + S * 0.06, chest_y + S * 0.115),
    ]
    triad_poly(surf, zar, RUST_CORE, RUST, RUST_SHEEN, inset_amt=0.10)
    # Hard woven stripes across the blanket — alternate ochre / turquoise / bone,
    # the full house triad reading as a serape weave.
    stripe_cols = [OCHRE, TURQ, BONE, TURQ, OCHRE]
    for i, col in enumerate(stripe_cols):
        tt = (i + 1) / (len(stripe_cols) + 1)
        a = (zar[0][0] + (zar[1][0] - zar[0][0]) * tt,
             zar[0][1] + (zar[1][1] - zar[0][1]) * tt)
        b = (zar[3][0] + (zar[2][0] - zar[3][0]) * tt,
             zar[3][1] + (zar[2][1] - zar[3][1]) * tt)
        pygame.draw.line(surf, col, a, b, max(2, int(SS * 1.8)))
    # Fringe ticks along the lower hem.
    for k in range(5):
        tt = k / 4.0
        fx = zar[3][0] + (zar[2][0] - zar[3][0]) * tt
        fy = zar[3][1] + (zar[2][1] - zar[3][1]) * tt
        pygame.draw.line(surf, OCHRE, (fx, fy), (fx + S * 0.005, fy + S * 0.03),
                         max(1, int(SS)))

    # ── RIDER: tiny charro skeleton seated high on the zarape ─────────────────
    rid_x = haunch_x - S * 0.01
    seat_y = haunch_y - S * 0.115
    # Rider legs straddling the barrel — short bone limbs hugging the horse side.
    bone_limb(surf, (rid_x, seat_y + S * 0.02),
              (rid_x + S * 0.07, seat_y + S * 0.08),
              (rid_x + S * 0.04, seat_y + S * 0.15), S * 0.034)
    bone_limb(surf, (rid_x - S * 0.01, seat_y + S * 0.02),
              (rid_x - S * 0.085, seat_y + S * 0.075),
              (rid_x - S * 0.055, seat_y + S * 0.145), S * 0.034)
    # Embroidered short charro JACKET (bolero) — brick-rust torso with botonadura.
    jacket = [
        (rid_x - S * 0.075, seat_y - S * 0.085),
        (rid_x + S * 0.075, seat_y - S * 0.085),
        (rid_x + S * 0.065, seat_y + S * 0.04),
        (rid_x - S * 0.065, seat_y + S * 0.04),
    ]
    triad_poly(surf, jacket, RUST_CORE, RUST, RUST_SHEEN,
               sheen_pts=[(rid_x - S * 0.06, seat_y - S * 0.07),
                          (rid_x - S * 0.01, seat_y - S * 0.075),
                          (rid_x - S * 0.025, seat_y + S * 0.02),
                          (rid_x - S * 0.06, seat_y + S * 0.02)])
    # Botonadura: twin ochre button rows down the jacket front (charro signature).
    for side in (-1, 1):
        for i in range(3):
            byp = seat_y - S * 0.055 + i * S * 0.035
            bxp = rid_x + side * S * 0.04
            triad_ellipse(surf, bxp, byp, S * 0.013, S * 0.013,
                          OCHRE_CORE, OCHRE, OCHRE_SHEEN)
    # Turquoise embroidery scroll on the lapel edge (decoration accent).
    pygame.draw.arc(surf, TURQ,
                    (int(rid_x - S * 0.07), int(seat_y - S * 0.07),
                     int(S * 0.04), int(S * 0.09)),
                    math.pi * 1.4, math.pi * 2.1, max(1, int(SS)))

    # Rein arm (player-left, low) holding a turquoise rein down to the browband.
    bone_limb(surf, (rid_x - S * 0.055, seat_y - S * 0.05),
              (rid_x - S * 0.11, seat_y + S * 0.01),
              (rid_x - S * 0.165, seat_y + S * 0.055), S * 0.026)
    pygame.draw.line(surf, TURQ,
                     (rid_x - S * 0.165, seat_y + S * 0.055),
                     (sk_x + S * 0.04, sk_y + S * 0.02), max(1, int(SS * 1.2)))

    # RIDER SKULL (small, grinning, painted) above the jacket collar.
    rh_y = seat_y - S * 0.155
    triad_ellipse(surf, rid_x, rh_y, S * 0.07, S * 0.075, BONE_CORE, BONE, SHEEN)
    triad_ellipse(surf, rid_x, rh_y + S * 0.05, S * 0.052, S * 0.034,
                  BONE_CORE, BONE, SHEEN)
    for ex in (rid_x - S * 0.026, rid_x + S * 0.026):
        triad_ellipse(surf, ex, rh_y - S * 0.004, S * 0.018, S * 0.02,
                      SOCKET_CORE, SOCKET_FILL, SOCKET_SHEEN, outline=None)
        pygame.draw.circle(surf, INK, (int(ex), int(rh_y - S * 0.004)),
                           int(S * 0.008))
    pygame.draw.polygon(surf, SOCKET_CORE, [
        (rid_x, rh_y + S * 0.018),
        (rid_x - S * 0.008, rh_y + S * 0.036),
        (rid_x + S * 0.008, rh_y + S * 0.036)])
    sm_y = rh_y + S * 0.046
    pygame.draw.arc(surf, INK,
                    (int(rid_x - S * 0.036), int(sm_y - S * 0.022),
                     int(S * 0.072), int(S * 0.044)),
                    math.pi * 1.05, math.pi * 1.95, max(1, int(SS)))
    for k in range(-2, 3):
        txx = rid_x + k * S * 0.012
        pygame.draw.line(surf, INK, (txx, sm_y - S * 0.006),
                         (txx, sm_y + S * 0.008), max(1, int(SS * 0.7)))
    # Painted rust moustache on the rider — keeps the charro read at the rider.
    for side in (-1, 1):
        pygame.draw.arc(surf, RUST,
                        (int(rid_x + side * S * 0.004 - (side < 0) * S * 0.03),
                         int(rh_y + S * 0.03), int(S * 0.03), int(S * 0.026)),
                        math.pi * (0.0 if side > 0 else 0.5),
                        math.pi * (0.5 if side > 0 else 1.0), max(1, int(SS)))

    # WAVING ARM thrust up (player-right) — the rider's salute, the top action.
    hand = (rid_x + S * 0.155, rh_y - S * 0.13)
    bone_limb(surf, (rid_x + S * 0.055, seat_y - S * 0.06),
              (rid_x + S * 0.115, rh_y - S * 0.02),
              hand, S * 0.026)
    # Small SOMBRERO held aloft in the raised hand — ochre disc + low crown,
    # the salute prop that tops the silhouette.
    _ell(surf, INK, hand[0] + S * 0.01, hand[1] - S * 0.02 + S * 0.006,
         S * 0.092, S * 0.034)
    triad_ellipse(surf, hand[0] + S * 0.01, hand[1] - S * 0.02,
                  S * 0.088, S * 0.03, OCHRE_CORE, OCHRE, OCHRE_SHEEN)
    crown = [
        (hand[0] - S * 0.022, hand[1] - S * 0.026),
        (hand[0] - S * 0.012, hand[1] - S * 0.064),
        (hand[0] + S * 0.032, hand[1] - S * 0.064),
        (hand[0] + S * 0.042, hand[1] - S * 0.026),
    ]
    triad_poly(surf, crown, OCHRE_CORE, OCHRE, OCHRE_SHEEN, inset_amt=0.20)
    pygame.draw.line(surf, RUST, (hand[0] - S * 0.018, hand[1] - S * 0.03),
                     (hand[0] + S * 0.038, hand[1] - S * 0.03), max(2, int(SS * 1.6)))

    grow_outline(surf, INK, 1)
    out = pygame.transform.smoothscale(surf, (target_size, target_size))
    return out


# ── the prop -> pillar mirror (slim lance + compact horse-skull finial) ──────

def draw_pillar(width, height, top_cap=True):
    """Charro lance / reata-pole pillar. A wrapped narrow lance shaft = the
    repeatable shaft body (binding banding); a compact horse-skull finial with a
    marigold = the detachable gap-edge cap.

    TWO-BODY guard: the creature is the only stacked-mass body in the family, so
    the prop must NOT echo that double mass. The action stays in the creature;
    here the shaft is deliberately SLIM and the finial is a single compact
    horse-skull seated tight on the shaft axis (NOT a second rider-and-mount),
    so the top<->bottom mirror reads balanced and on-axis."""
    W = width * SS
    H = height * SS
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W * 0.5

    # Slim wrapped lance shaft (kept narrow — the slimness IS the top-heavy fix).
    shaft_w = W * 0.26
    shaft = pygame.Rect(int(cx - shaft_w / 2), 0, int(shaft_w), int(H))
    pygame.draw.rect(surf, OCHRE_CORE, shaft)
    inner = shaft.inflate(-int(SS * 3), 0)
    pygame.draw.rect(surf, OCHRE, inner)
    pygame.draw.rect(surf, OCHRE_SHEEN,
                     (int(cx - shaft_w / 2 + SS * 2), 0,
                      int(shaft_w * 0.26), int(H)))
    # Diagonal binding wraps (rust + turquoise) march down the shaft = banding.
    band_n = max(5, int(height / 12))
    for i in range(band_n):
        by = int(H * (i + 0.5) / band_n)
        col = RUST if i % 2 == 0 else TURQ
        pygame.draw.line(surf, col,
                         (cx - shaft_w / 2, by - SS),
                         (cx + shaft_w / 2, by + SS), max(2, int(SS * 1.4)))

    # Gap-edge cap: compact horse-skull finial seated tight on the shaft axis.
    if top_cap:
        sk_r = shaft_w * 0.92   # compact — modest mass kept on-axis
        by = H - sk_r - W * 0.05
        # Cranium.
        triad_ellipse(surf, cx, by, sk_r, sk_r * 1.05, BONE_CORE, BONE, SHEEN)
        # Short forward muzzle (on-axis, symmetric stub so the mirror stays balanced).
        muzzle = [
            (cx - sk_r * 0.55, by + sk_r * 0.2),
            (cx - sk_r * 0.55, by + sk_r * 0.78),
            (cx + sk_r * 0.55, by + sk_r * 0.78),
            (cx + sk_r * 0.55, by + sk_r * 0.2),
        ]
        muzzle = [(cx, by + sk_r * 1.5)] + muzzle  # narrow snout point at axis
        muzzle = [
            (cx - sk_r * 0.5, by + sk_r * 0.35),
            (cx, by + sk_r * 1.45),
            (cx + sk_r * 0.5, by + sk_r * 0.35),
        ]
        triad_poly(surf, muzzle, BONE_CORE, BONE, SHEEN, inset_amt=0.18)
        # Pricked ears (symmetric, on-axis).
        for sgn in (-1, 1):
            ear = [
                (cx + sgn * sk_r * 0.35, by - sk_r * 0.7),
                (cx + sgn * sk_r * 0.6, by - sk_r * 1.25),
                (cx + sgn * sk_r * 0.72, by - sk_r * 0.55),
            ]
            triad_poly(surf, ear, BONE_CORE, BONE, SHEEN, inset_amt=0.22)
        # Twin sugar-skull sockets with ochre + a turquoise brow scroll.
        for ex in (cx - sk_r * 0.4, cx + sk_r * 0.4):
            triad_ellipse(surf, ex, by - sk_r * 0.05, sk_r * 0.26, sk_r * 0.3,
                          SOCKET_CORE, SOCKET_FILL, SOCKET_SHEEN, outline=None)
            pygame.draw.circle(surf, INK, (int(ex), int(by - sk_r * 0.05)),
                               max(1, int(sk_r * 0.1)))
        pygame.draw.arc(surf, TURQ,
                        (int(cx - sk_r * 0.55), int(by - sk_r * 0.55),
                         int(sk_r * 1.1), int(sk_r * 0.6)),
                        math.pi * 0.08, math.pi * 0.92, max(2, int(SS * 1.4)))
        # Marigold at the brow centre — the finial flower, on-axis.
        triad_ellipse(surf, cx, by + sk_r * 0.05, sk_r * 0.22, sk_r * 0.22,
                      MARI_CORE, MARIGOLD, MARI_SHEEN)

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (width, height))


# ── pure-black silhouette read (accessibility / outline test) ─────────────────

def draw_silhouette(target_size):
    """Flatten the creature to a near-black mask — proves the unique read
    survives in outline alone: a rearing horse + a small rider with a raised arm
    topping the silhouette (the only multi-body KIND in the family)."""
    rgba = draw_jinete(target_size)
    sil = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(rgba)
    surf = mask.to_surface(setcolor=(18, 16, 20, 255), unsetcolor=(0, 0, 0, 0))
    sil.blit(surf, (0, 0))
    return sil


# ── sheet composition ─────────────────────────────────────────────────────────

def build_sheet():
    W, H = 1000, 720
    sheet = pygame.Surface((W, H))
    sheet.fill((46, 40, 52))   # warm-dark neutral review backdrop

    font = pygame.font.SysFont("arial", 18, bold=True)
    small = pygame.font.SysFont("arial", 13)

    def label(txt, x, y, col=(245, 238, 226)):
        sheet.blit(font.render(txt, True, col), (x, y))

    def caption(txt, x, y, col=(208, 200, 210)):
        sheet.blit(small.render(txt, True, col), (x, y))

    label("EL CHARRO JINETE — skeletal charro rider on a rearing bone-horse  ·  round 1",
          18, 12, (252, 224, 150))
    caption("BLEND facet (anatomy + decoration + motion) · grand-boss anchor · "
            "rust HELD in the desaturated brick/leather lane (176,70,56)",
            18, 36)

    # Large creature.
    big = draw_jinete(320)
    sheet.blit(big, (20, 60))
    caption("creature · large (rearing horse + rider, raised hat)", 20, 384)

    # Mid-scale legibility ramp.
    mid = draw_jinete(160)
    sheet.blit(mid, (360, 60))
    caption("creature · 160px", 360, 226)

    # 32px creature + 4x zoom.
    tiny = draw_jinete(32)
    sheet.blit(tiny, (360, 256))
    caption("32px", 360, 290)
    zoom = pygame.transform.scale(tiny, (128, 128))
    sheet.blit(zoom, (400, 256))
    caption("32px @4x", 400, 386)

    # Pure-black silhouette read (creature scale + 32px@4x) — the AD ship test.
    sil_big = draw_silhouette(160)
    sheet.blit(sil_big, (20, 412))
    caption("silhouette · 160px", 20, 578)
    sil_tiny = draw_silhouette(32)
    sil_zoom = pygame.transform.scale(sil_tiny, (128, 128))
    sheet.blit(sil_zoom, (192, 412))
    caption("silhouette 32px @4x", 192, 542)
    caption("read: reared horse + rider, arm up", 192, 558)

    # Warm OCHRE-DAY-SKY verification — confirm the brick-rust + bone read holds
    # on a warm desert biome, not only on the dark review mat.
    tiny_w = draw_jinete(32)
    panel_x = 360
    for yy in range(128):
        t = yy / 128.0
        sky_top, sky_bot = (236, 196, 120), (210, 158, 92)
        col = tuple(int(sky_top[i] + (sky_bot[i] - sky_top[i]) * t) for i in range(3))
        pygame.draw.line(sheet, col, (panel_x, 412 + yy), (panel_x + 128, 412 + yy))
    pygame.draw.rect(sheet, (24, 20, 26), (panel_x, 412, 128, 128), 2)
    sheet.blit(pygame.transform.scale(tiny_w, (128, 128)), (panel_x, 412))
    caption("32px @4x on ochre day sky", panel_x, 542)
    caption("brick-rust stays brown vs warm", panel_x, 558)

    # Prop -> pillar mirror (slim lance + compact horse-skull finial).
    px = 580
    py = 60
    cap_h = 84
    shaft_h = 150
    big_w = 60
    bot_cap = draw_pillar(big_w, cap_h, top_cap=True)
    bot_shaft = draw_pillar(big_w, shaft_h, top_cap=False)
    top_cap = pygame.transform.flip(bot_cap, False, True)
    top_shaft = pygame.transform.flip(bot_shaft, False, True)

    gap = 60
    sheet.blit(top_shaft, (px, py))
    sheet.blit(top_cap, (px, py + shaft_h))
    gap_y = py + shaft_h + cap_h
    sheet.blit(bot_cap, (px, gap_y + gap))
    sheet.blit(bot_shaft, (px, gap_y + gap + cap_h))
    caption("prop->pillar mirror", px - 4, py + shaft_h * 2 + cap_h * 2 + gap + 6)
    caption("slim lance + on-axis horse-skull finial", px - 4,
            py + shaft_h * 2 + cap_h * 2 + gap + 22)

    # 32px pillar cap (judge the gap-edge read small).
    tcap = draw_pillar(28, 40, top_cap=True)
    sheet.blit(tcap, (px + 130, py + 20))
    czoom = pygame.transform.scale(tcap, (112, 160))
    sheet.blit(czoom, (px + 172, py + 20))
    caption("cap 28px / @4x", px + 130, py + 188)
    caption("slim + on-axis (no double mass)", px + 130, py + 204)

    # Red-split reference: the three warm reds side by side so the brick lane is
    # visibly the darkest/brownest — never converging with chile or rose.
    rx0 = px + 130
    ry0 = py + 236
    caption("three warm reds split (this = brick H):", rx0, ry0 - 18)
    for i, (nm, col) in enumerate([
            ("B chile (214,86,44)", (214, 86, 44)),
            ("E rose (214,72,86)", (214, 72, 86)),
            ("H rust (176,70,56)", RUST)]):
        pygame.draw.rect(sheet, col, (rx0, ry0 + i * 34, 44, 28))
        pygame.draw.rect(sheet, (20, 18, 22), (rx0, ry0 + i * 34, 44, 28), 2)
        caption(nm, rx0 + 52, ry0 + i * 34 + 7)
    pygame.draw.rect(sheet, SHEEN, (rx0, ry0 + 2 * 34, 44, 28), 3)

    # Palette swatch strip (pinned palette, exact hexes).
    sw_y = H - 52
    swatches = [
        ("rust", RUST), ("ochre", OCHRE), ("turq", TURQ), ("bone", BONE),
        ("tan", BONE_SHADE), ("marigold", MARIGOLD), ("ink", INK), ("sheen", SHEEN),
    ]
    for i, (nm, col) in enumerate(swatches):
        sx = 360 + i * 78
        pygame.draw.rect(sheet, col, (sx, sw_y, 64, 30))
        pygame.draw.rect(sheet, (20, 18, 22), (sx, sw_y, 64, 30), 2)
        caption(nm, sx + 2, sw_y + 32)

    return sheet


if __name__ == "__main__":
    out = build_sheet()
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(out, dst)
    print("wrote", dst)
