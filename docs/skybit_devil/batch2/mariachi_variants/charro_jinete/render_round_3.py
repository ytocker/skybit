"""
El Charro Jinete — skeletal charro rider on a rearing alebrije bone-horse
(MARIACHI-LINEAGE warm-skeleton family, BLEND facet / grand-boss anchor).

ROUND 3 — FINAL pass. Round 2 fixed the rear, the hat-spike, the palette and
the night read, but welded the rider onto the horse's FRONT so the red sash read
as a chest-bib, not a body seated on the back. The one non-negotiable promise of
this entry — an unmistakable TWO-BODY horse-and-rider at color 32px — still did
not land. This round re-seats the rider ASTRIDE the spine:

  1. RIDER ON TOP, NOT IN FRONT. The rider pelvis sits ON the horse's spine/back
     line (hips over the barrel), pushed UP and slightly BACK toward the haunch.
     The red sash now reads as the rider's torso block sitting high, never as the
     mount's chest.
  2. A HARD HORIZONTAL INK CHANNEL UNDER THE SEAT. The dark negative-space gap is
     re-aimed to the seam that matters — between rider-pelvis and horse-back —
     running across the top of the barrel where the rider sits, so the two bodies
     cannot fuse into one fill at 32px.
  3. STRADDLING LEGS down the near flank. A bone leg drops from the seat down the
     near (right) side of the barrel — the unmistakable "seated astride" tell.
  4. VALUE STEP RE-AIMED to the BACK band. The deeper tan-core sits on the
     horse's back directly beneath the rider, so the lighter rider bone pops UP
     off a darker saddle zone (revises r2's generic neck-vs-barrel split).
  5. RIDER SKULL PULLED UP, clear of the horse withers, with sky/ink between the
     two skulls — horse muzzle stays low-left on the rear diagonal, rider skull
     high on the spike side. The two-skull ambiguity is resolved.
  6. BARREL SPECKLE THINNED. The mid-barrel is one bone mass with a single
     dark-core trough at 32px; woven banding lives only on the 160px render.

KEEP (AD locked): steep rearing diagonal · raised-sombrero arm lollipop spike ·
rust held in the brick/leather lane (176,70,56) riding with ochre + turquoise ·
house triad (dark-core -> flat-fill -> top-left sheen) · slim lance + on-axis
horse-skull finial pillar mirror.

Run headless:  SDL_VIDEODRIVER=dummy python render_round_3.py
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
BONE        = (236, 224, 198)   # warm bone (rider — kept light so it pops)
BONE_SHADE  = (176, 150, 108)   # tan-bone shade
MARIGOLD    = (240, 150,  46)   # marigold finial / browband flower
INK         = ( 28,  22,  22)   # keyline ink
SHEEN       = (250, 240, 216)   # top-left rim sheen

# Derived working tones (kept strictly inside the pinned families).
BONE_CORE   = (158, 134,  98)   # dark-core under bone
# The horse barrel sits a value-step DOWN from the rider's bone so the lighter
# rider reads as a separate body riding ON it (AD note: value step on the BACK).
HORSE_BODY  = (198, 180, 146)
HORSE_CORE  = (140, 116,  82)
HORSE_SHEEN = (228, 214, 184)
# The back band directly under the rider is pushed deeper still (~18% darker than
# HORSE_BODY) so the rider bone pops UP off a saddle-dark zone, not a generic
# barrel tone — this is the value seam that earns "rider on mount".
BACK_CORE   = (108,  88,  60)
BACK_SHADE  = (158, 138, 104)
OCHRE_CORE  = (158, 116,  50)
OCHRE_SHEEN = (244, 206, 138)
# Rust held in the brick lane: deep brown-brick core, muted brick sheen.
RUST_CORE   = (112,  42,  34)
RUST_SHEEN  = (208, 116,  96)
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
    if outline is not None:
        _ell(surf, outline, cx, cy, rx + SS, ry + SS)
    _ell(surf, core, cx, cy, rx, ry)
    _ell(surf, fill, cx, cy, rx - SS * 0.7, ry - SS * 0.7)
    _ell(surf, sheen, cx - rx * 0.34, cy - ry * 0.36, rx * 0.5, ry * 0.42)


def triad_poly(surf, pts, core, fill, sheen, outline=INK, sheen_pts=None,
               inset_amt=0.16):
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
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) > 2:
        pygame.draw.lines(surf, color, True, outline_pts, max(1, thickness * SS))


def bone_limb(surf, p0, p1, p2, w, body=BONE, core=BONE_CORE):
    for a, b in ((p0, p1), (p1, p2)):
        pygame.draw.line(surf, INK, a, b, int(w + SS * 1.7))
    for a, b in ((p0, p1), (p1, p2)):
        pygame.draw.line(surf, core, a, b, int(w))
        pygame.draw.line(surf, body, a, b, int(w * 0.5))
    for p in (p0, p1, p2):
        triad_ellipse(surf, p[0], p[1], w * 0.62, w * 0.62, core, body, SHEEN)


def _ink_channel(surf, pts, w):
    """Carve a hard INK negative-space channel along a polyline — the single
    most important fix: dark air UNDER the rider seat so the rider mass lands on
    top of a hard dark gap and the two bodies cannot fuse into one fill at 32px."""
    for a, b in zip(pts, pts[1:]):
        pygame.draw.line(surf, INK, a, b, int(w))
    for p in pts:
        pygame.draw.circle(surf, INK, (int(p[0]), int(p[1])), int(w * 0.5))


# ── the creature — LARGE / 160px construction (full incident detail) ─────────

def draw_jinete(target_size):
    """A chibi bone-HORSE REARING hard on its hind legs at a steep diagonal —
    arched cervical spine sweeping up-left to a big skull-muzzle, front hooves
    pawing high off the baseline — carrying a tiny charro skeleton RIDER seated
    ASTRIDE the spine: hips over the barrel, one leg straddling down the near
    flank, one bone arm thrust UP as a hat-lollipop spike. A hard horizontal ink
    channel under the seat separates the two bodies. The grand-boss of the
    family."""
    S = target_size * SS
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S * 0.5

    # ── HIND LEGS planted (weight-bearing base of the rear) ───────────────────
    haunch_x, haunch_y = cx + S * 0.20, S * 0.66
    legw = S * 0.052
    bone_limb(surf,
              (haunch_x - S * 0.02, haunch_y),
              (cx + S * 0.10, S * 0.81),
              (cx + S * 0.085, S * 0.955), legw * 0.92,
              body=HORSE_BODY, core=HORSE_CORE)
    bone_limb(surf,
              (haunch_x + S * 0.04, haunch_y),
              (cx + S * 0.27, S * 0.80),
              (cx + S * 0.30, S * 0.955), legw,
              body=HORSE_BODY, core=HORSE_CORE)
    for hx in (cx + S * 0.085, cx + S * 0.30):
        triad_ellipse(surf, hx, S * 0.955, S * 0.05, S * 0.034,
                      RUST_CORE, RUST, RUST_SHEEN)

    # ── HAUNCH + BARREL — one bone mass tilted back along the rear diagonal ────
    triad_ellipse(surf, haunch_x, haunch_y, S * 0.135, S * 0.155,
                  HORSE_CORE, HORSE_BODY, HORSE_SHEEN)
    chest_x, chest_y = cx - S * 0.075, S * 0.44
    triad_ellipse(surf, chest_x, chest_y, S * 0.150, S * 0.140,
                  HORSE_CORE, HORSE_BODY, HORSE_SHEEN)
    # Rib bands — large-render only (dropped at 32px).
    for i in range(4):
        ry = chest_y - S * 0.05 + i * S * 0.045
        pygame.draw.arc(surf, HORSE_CORE,
                        (int(chest_x - S * 0.13), int(ry - S * 0.05),
                         int(S * 0.26), int(S * 0.13)),
                        math.pi * 1.08, math.pi * 1.92, max(2, int(SS * 1.5)))
        pygame.draw.arc(surf, INK,
                        (int(chest_x - S * 0.13), int(ry - S * 0.05),
                         int(S * 0.26), int(S * 0.13)),
                        math.pi * 1.18, math.pi * 1.82, max(1, int(SS * 0.8)))

    # ── ARCHED CERVICAL SPINE — steep up-left sweep to the skull ──────────────
    neck_base = (chest_x - S * 0.06, chest_y - S * 0.10)
    neck_top  = (cx - S * 0.30, S * 0.215)
    neck_pts = [
        (neck_base[0] + S * 0.075, neck_base[1] + S * 0.02),
        (neck_base[0] - S * 0.045, neck_base[1] - S * 0.01),
        (neck_top[0] - S * 0.02, neck_top[1] + S * 0.03),
        (neck_top[0] + S * 0.07, neck_top[1] + S * 0.015),
    ]
    triad_poly(surf, neck_pts, HORSE_CORE, HORSE_BODY, HORSE_SHEEN)
    for t in range(5):
        tt = t / 4.0
        vx = neck_base[0] + (neck_top[0] - neck_base[0]) * tt + S * 0.012
        vy = neck_base[1] + (neck_top[1] - neck_base[1]) * tt
        triad_ellipse(surf, vx, vy, S * 0.026, S * 0.026,
                      HORSE_CORE, HORSE_BODY, HORSE_SHEEN)
    for t in range(6):
        tt = t / 5.0
        mx = neck_base[0] + (neck_top[0] - neck_base[0]) * tt - S * 0.05
        my = neck_base[1] + (neck_top[1] - neck_base[1]) * tt - S * 0.01
        pygame.draw.line(surf, INK, (mx, my),
                         (mx - S * 0.055, my - S * 0.03), max(2, int(SS * 1.8)))
        pygame.draw.line(surf, HORSE_BODY, (mx, my),
                         (mx - S * 0.05, my - S * 0.028), max(1, int(SS * 0.9)))

    # ── HORSE SKULL-MUZZLE (big, triad-lit, sugar-skull decorated) ────────────
    sk_x, sk_y = neck_top[0] - S * 0.01, neck_top[1] - S * 0.02
    triad_ellipse(surf, sk_x, sk_y, S * 0.10, S * 0.11, BONE_CORE, BONE, SHEEN)
    muzzle = [
        (sk_x - S * 0.085, sk_y + S * 0.02),
        (sk_x - S * 0.185, sk_y + S * 0.055),
        (sk_x - S * 0.185, sk_y + S * 0.115),
        (sk_x - S * 0.07,  sk_y + S * 0.11),
    ]
    triad_poly(surf, muzzle, BONE_CORE, BONE, SHEEN)
    pygame.draw.ellipse(surf, SOCKET_CORE,
                        (int(sk_x - S * 0.175), int(sk_y + S * 0.07),
                         int(S * 0.03), int(S * 0.022)))
    pygame.draw.line(surf, INK, (sk_x - S * 0.18, sk_y + S * 0.105),
                     (sk_x - S * 0.075, sk_y + S * 0.10), max(1, int(SS)))
    for k in range(4):
        txx = sk_x - S * 0.16 + k * S * 0.026
        pygame.draw.line(surf, BONE, (txx, sk_y + S * 0.108),
                         (txx, sk_y + S * 0.124), max(1, int(SS)))
        pygame.draw.line(surf, INK, (txx + S * 0.013, sk_y + S * 0.108),
                         (txx + S * 0.013, sk_y + S * 0.124), max(1, int(SS * 0.6)))
    for sgn, base in ((-1, sk_x + S * 0.02), (1, sk_x + S * 0.07)):
        ear = [
            (base, sk_y - S * 0.085),
            (base + S * 0.018, sk_y - S * 0.16),
            (base + S * 0.05, sk_y - S * 0.08),
        ]
        triad_poly(surf, ear, BONE_CORE, BONE, SHEEN, inset_amt=0.22)
    eye_x, eye_y = sk_x - S * 0.01, sk_y - S * 0.005
    triad_ellipse(surf, eye_x, eye_y, S * 0.038, S * 0.044,
                  SOCKET_CORE, SOCKET_FILL, SOCKET_SHEEN, outline=None)
    for k in range(8):
        a = k * math.tau / 8
        px = eye_x + math.cos(a) * S * 0.05
        py = eye_y + math.sin(a) * S * 0.056
        pygame.draw.circle(surf, OCHRE, (int(px), int(py)), max(1, int(SS * 1.2)))
    pygame.draw.circle(surf, INK, (int(eye_x), int(eye_y)), int(S * 0.017))
    pygame.draw.arc(surf, TURQ,
                    (int(sk_x - S * 0.055), int(sk_y - S * 0.075),
                     int(S * 0.13), int(S * 0.07)),
                    math.pi * 0.05, math.pi * 0.95, max(2, int(SS * 1.4)))
    for k in range(3):
        dx = sk_x - S * 0.03 + k * S * 0.03
        pygame.draw.circle(surf, RUST, (int(dx), int(sk_y - S * 0.05)),
                           max(1, int(SS * 1.1)))
    pygame.draw.line(surf, OCHRE, (sk_x - S * 0.07, sk_y + S * 0.035),
                     (sk_x + S * 0.085, sk_y + S * 0.005), max(3, int(SS * 3)))
    pygame.draw.line(surf, OCHRE_CORE, (sk_x - S * 0.07, sk_y + S * 0.045),
                     (sk_x + S * 0.085, sk_y + S * 0.015), max(1, int(SS)))
    triad_ellipse(surf, sk_x + S * 0.01, sk_y + S * 0.025, S * 0.026, S * 0.026,
                  MARI_CORE, MARIGOLD, MARI_SHEEN)

    # ── FRONT LEGS pawing HIGH off the baseline (the rear-motion tell) ────────
    shoulder = (chest_x - S * 0.04, chest_y - S * 0.01)
    bone_limb(surf, shoulder,
              (chest_x - S * 0.18, chest_y - S * 0.10),
              (chest_x - S * 0.27, chest_y - S * 0.205), legw * 0.86,
              body=HORSE_BODY, core=HORSE_CORE)
    bone_limb(surf, (shoulder[0] + S * 0.02, shoulder[1] + S * 0.05),
              (chest_x - S * 0.155, chest_y + S * 0.005),
              (chest_x - S * 0.245, chest_y - S * 0.075), legw * 0.86,
              body=HORSE_BODY, core=HORSE_CORE)
    for hx, hy in ((chest_x - S * 0.27, chest_y - S * 0.205),
                   (chest_x - S * 0.245, chest_y - S * 0.075)):
        triad_ellipse(surf, hx, hy, S * 0.044, S * 0.03,
                      RUST_CORE, RUST, RUST_SHEEN)

    # ── BACK / SADDLE LINE — the horse SPINE the rider sits ON ────────────────
    # A bone back-line arcs from the withers (top of chest) over the barrel to the
    # croup; the SADDLE/zarape rides on it. The rider seat lands ON this line, not
    # in front of the chest, so the two-body read is structural.
    withers = (chest_x + S * 0.02, chest_y - S * 0.135)
    croup   = (haunch_x + S * 0.02, haunch_y - S * 0.15)
    back_mid_x = (withers[0] + croup[0]) * 0.5
    back_mid_y = min(withers[1], croup[1]) - S * 0.015
    # The saddle-darkened back band: a deeper tan zone under where the rider sits,
    # so the lighter rider bone pops UP off it (value seam re-aimed to the BACK).
    back_band = [
        (withers[0] - S * 0.01, withers[1] + S * 0.02),
        (back_mid_x, back_mid_y),
        (croup[0] + S * 0.02, croup[1] + S * 0.02),
        (croup[0] - S * 0.02, croup[1] + S * 0.085),
        (back_mid_x, back_mid_y + S * 0.085),
        (withers[0] - S * 0.02, withers[1] + S * 0.10),
    ]
    triad_poly(surf, back_band, BACK_CORE, BACK_SHADE, HORSE_SHEEN, inset_amt=0.12)

    # ── ZARAPE saddle-blanket — draped OVER the back band (woven banding) ──────
    zar = [
        (withers[0] + S * 0.02, withers[1] + S * 0.05),
        (croup[0], croup[1] + S * 0.02),
        (croup[0] + S * 0.05, croup[1] + S * 0.14),
        (withers[0] + S * 0.04, withers[1] + S * 0.155),
    ]
    triad_poly(surf, zar, RUST_CORE, RUST, RUST_SHEEN, inset_amt=0.10)
    stripe_cols = [OCHRE, TURQ, BONE, TURQ, OCHRE]
    for i, col in enumerate(stripe_cols):
        tt = (i + 1) / (len(stripe_cols) + 1)
        a = (zar[0][0] + (zar[1][0] - zar[0][0]) * tt,
             zar[0][1] + (zar[1][1] - zar[0][1]) * tt)
        b = (zar[3][0] + (zar[2][0] - zar[3][0]) * tt,
             zar[3][1] + (zar[2][1] - zar[3][1]) * tt)
        pygame.draw.line(surf, col, a, b, max(2, int(SS * 1.6)))
    for k in range(5):
        tt = k / 4.0
        fx = zar[3][0] + (zar[2][0] - zar[3][0]) * tt
        fy = zar[3][1] + (zar[2][1] - zar[3][1]) * tt
        pygame.draw.line(surf, OCHRE, (fx, fy), (fx + S * 0.005, fy + S * 0.03),
                         max(1, int(SS)))

    # ── RIDER seat anchored ON the spine, hips over the barrel ────────────────
    # Pushed UP onto the back line and slightly BACK toward the croup — the seat
    # sits ABOVE the saddle, NOT on the chest front.
    rid_x = back_mid_x + S * 0.015
    seat_y = back_mid_y - S * 0.045

    # ── STRADDLING LEGS — the near (right) leg drops down the near flank, the
    # far (left) leg tucks behind the saddle. This is the "seated astride" tell:
    # a leg visibly hangs DOWN the side of the barrel.
    # Far leg (player-left, partly behind the zarape) — drawn first.
    bone_limb(surf, (rid_x - S * 0.02, seat_y + S * 0.04),
              (rid_x - S * 0.055, seat_y + S * 0.12),
              (rid_x - S * 0.04, seat_y + S * 0.20), S * 0.030)
    # Near leg (player-right) straddling DOWN the visible flank to a stirrup boot.
    bone_limb(surf, (rid_x + S * 0.045, seat_y + S * 0.035),
              (rid_x + S * 0.075, seat_y + S * 0.13),
              (rid_x + S * 0.055, seat_y + S * 0.215), S * 0.032)
    triad_ellipse(surf, rid_x + S * 0.055, seat_y + S * 0.225, S * 0.034, S * 0.022,
                  RUST_CORE, RUST, RUST_SHEEN)   # boot/stirrup
    # Stirrup leather strap from saddle down to the boot.
    pygame.draw.line(surf, OCHRE_CORE,
                     (rid_x + S * 0.055, seat_y + S * 0.02),
                     (rid_x + S * 0.06, seat_y + S * 0.205), max(2, int(SS * 1.2)))

    # ── HARD INK CHANNEL under the seat (AD #1/#2) — drawn AFTER straddle legs,
    # BEFORE the rider torso, so the rider torso lands above a hard dark break and
    # the two bodies cannot fuse. Runs horizontally across the saddle top.
    _ink_channel(surf, [
        (rid_x - S * 0.085, seat_y + S * 0.02),
        (rid_x, seat_y + S * 0.005),
        (rid_x + S * 0.085, seat_y + S * 0.02),
    ], int(S * 0.038))

    # ── RIDER TORSO — embroidered charro jacket block, ABOVE the channel ──────
    jacket = [
        (rid_x - S * 0.066, seat_y - S * 0.10),
        (rid_x + S * 0.066, seat_y - S * 0.10),
        (rid_x + S * 0.058, seat_y - S * 0.005),
        (rid_x - S * 0.058, seat_y - S * 0.005),
    ]
    triad_poly(surf, jacket, RUST_CORE, RUST, RUST_SHEEN,
               sheen_pts=[(rid_x - S * 0.052, seat_y - S * 0.085),
                          (rid_x - S * 0.008, seat_y - S * 0.09),
                          (rid_x - S * 0.02, seat_y - S * 0.025),
                          (rid_x - S * 0.052, seat_y - S * 0.025)])
    for side in (-1, 1):
        for i in range(3):
            byp = seat_y - S * 0.075 + i * S * 0.028
            bxp = rid_x + side * S * 0.034
            triad_ellipse(surf, bxp, byp, S * 0.012, S * 0.012,
                          OCHRE_CORE, OCHRE, OCHRE_SHEEN)
    pygame.draw.arc(surf, TURQ,
                    (int(rid_x - S * 0.062), int(seat_y - S * 0.085),
                     int(S * 0.04), int(S * 0.08)),
                    math.pi * 1.4, math.pi * 2.1, max(1, int(SS)))

    # Rein arm (low, reaches forward to the horse's neck) — large-render only.
    bone_limb(surf, (rid_x - S * 0.05, seat_y - S * 0.065),
              (rid_x - S * 0.12, seat_y - S * 0.03),
              (rid_x - S * 0.20, seat_y + S * 0.01), S * 0.022)
    pygame.draw.line(surf, TURQ,
                     (rid_x - S * 0.20, seat_y + S * 0.01),
                     (sk_x + S * 0.04, sk_y + S * 0.03), max(1, int(SS * 1.2)))

    # ── RIDER SKULL pulled UP clear of the withers (AD #3/#4) ─────────────────
    rh_y = seat_y - S * 0.175
    triad_ellipse(surf, rid_x, rh_y, S * 0.062, S * 0.068, BONE_CORE, BONE, SHEEN)
    triad_ellipse(surf, rid_x, rh_y + S * 0.045, S * 0.046, S * 0.030,
                  BONE_CORE, BONE, SHEEN)
    for ex in (rid_x - S * 0.023, rid_x + S * 0.023):
        triad_ellipse(surf, ex, rh_y - S * 0.004, S * 0.016, S * 0.018,
                      SOCKET_CORE, SOCKET_FILL, SOCKET_SHEEN, outline=None)
        pygame.draw.circle(surf, INK, (int(ex), int(rh_y - S * 0.004)),
                           int(S * 0.0075))
    pygame.draw.polygon(surf, SOCKET_CORE, [
        (rid_x, rh_y + S * 0.016),
        (rid_x - S * 0.0075, rh_y + S * 0.031),
        (rid_x + S * 0.0075, rh_y + S * 0.031)])
    sm_y = rh_y + S * 0.042
    pygame.draw.arc(surf, INK,
                    (int(rid_x - S * 0.032), int(sm_y - S * 0.020),
                     int(S * 0.064), int(S * 0.042)),
                    math.pi * 1.05, math.pi * 1.95, max(1, int(SS)))
    for k in range(-2, 3):
        txx = rid_x + k * S * 0.011
        pygame.draw.line(surf, INK, (txx, sm_y - S * 0.005),
                         (txx, sm_y + S * 0.007), max(1, int(SS * 0.7)))

    # ── WAVING ARM thrust UP as a hat-lollipop SPIKE (AD KEEP) ────────────────
    hand = (rid_x + S * 0.13, rh_y - S * 0.175)
    bone_limb(surf, (rid_x + S * 0.05, seat_y - S * 0.085),
              (rid_x + S * 0.10, rh_y - S * 0.05),
              hand, S * 0.024)
    _ell(surf, INK, hand[0] + S * 0.005, hand[1] + S * 0.004,
         S * 0.088, S * 0.032)
    triad_ellipse(surf, hand[0] + S * 0.005, hand[1] - S * 0.004,
                  S * 0.084, S * 0.028, OCHRE_CORE, OCHRE, OCHRE_SHEEN)
    crown = [
        (hand[0] - S * 0.024, hand[1] - S * 0.026),
        (hand[0] - S * 0.014, hand[1] - S * 0.066),
        (hand[0] + S * 0.030, hand[1] - S * 0.066),
        (hand[0] + S * 0.040, hand[1] - S * 0.026),
    ]
    triad_poly(surf, crown, OCHRE_CORE, OCHRE, OCHRE_SHEEN, inset_amt=0.20)
    pygame.draw.line(surf, RUST, (hand[0] - S * 0.020, hand[1] - S * 0.030),
                     (hand[0] + S * 0.036, hand[1] - S * 0.030), max(2, int(SS * 1.6)))

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (target_size, target_size))


# ── DEDICATED 32px CONSTRUCTION (the read that has to hold) ────────────────────

def draw_jinete_tiny(target_size):
    """A purpose-built small read: only the shapes that survive at gameplay size.
    The horse is arched-neck + skull-muzzle (up-left) / one barrel mass with a
    single dark trough / two planted hind legs / two pawing forelegs lifted off
    the baseline. The rider sits ASTRIDE on the spine — skull dot HIGH, brick
    torso block over the saddle, a leg straddling DOWN the near flank — landing on
    a HARD HORIZONTAL INK CHANNEL, with a thin arm + ochre disc lollipop spiking
    into the sky. No rib banding, no buttons — those are large-render only."""
    S = target_size * SS
    surf = pygame.Surface((S, S), pygame.SRCALPHA)

    cx = S * 0.5
    legw = S * 0.075

    haunch_x, haunch_y = cx + S * 0.18, S * 0.64
    chest_x, chest_y = cx - S * 0.085, S * 0.46

    # Hind legs — two planted, the diagonal base of the rear.
    bone_limb(surf, (haunch_x, haunch_y),
              (cx + S * 0.10, S * 0.81), (cx + S * 0.08, S * 0.965),
              legw, body=HORSE_BODY, core=HORSE_CORE)
    bone_limb(surf, (haunch_x + S * 0.04, haunch_y),
              (cx + S * 0.27, S * 0.80), (cx + S * 0.30, S * 0.965),
              legw, body=HORSE_BODY, core=HORSE_CORE)
    for hx in (cx + S * 0.08, cx + S * 0.30):
        triad_ellipse(surf, hx, S * 0.96, S * 0.055, S * 0.04,
                      RUST_CORE, RUST, RUST_SHEEN)

    # Barrel + haunch as ONE darker bone mass (single dark-core trough only).
    triad_ellipse(surf, haunch_x, haunch_y, S * 0.155, S * 0.165,
                  HORSE_CORE, HORSE_BODY, HORSE_SHEEN)
    triad_ellipse(surf, chest_x, chest_y, S * 0.16, S * 0.15,
                  HORSE_CORE, HORSE_BODY, HORSE_SHEEN)

    # Arched neck — fat tapered bone wedge sweeping steep up-left.
    sk_x, sk_y = cx - S * 0.31, S * 0.22
    neck = [
        (chest_x + S * 0.02, chest_y - S * 0.12),
        (chest_x - S * 0.10, chest_y - S * 0.11),
        (sk_x + S * 0.02, sk_y + S * 0.10),
        (sk_x + S * 0.12, sk_y + S * 0.07),
    ]
    triad_poly(surf, neck, HORSE_CORE, HORSE_BODY, HORSE_SHEEN)

    # Horse skull-muzzle — cranium + forward snout wedge (head stays LOW-LEFT).
    triad_ellipse(surf, sk_x, sk_y, S * 0.115, S * 0.125, BONE_CORE, BONE, SHEEN)
    muzzle = [
        (sk_x - S * 0.085, sk_y + S * 0.02),
        (sk_x - S * 0.22, sk_y + S * 0.075),
        (sk_x - S * 0.21, sk_y + S * 0.135),
        (sk_x - S * 0.07, sk_y + S * 0.12),
    ]
    triad_poly(surf, muzzle, BONE_CORE, BONE, SHEEN)
    for base in (sk_x + S * 0.03, sk_x + S * 0.09):
        ear = [(base, sk_y - S * 0.09),
               (base + S * 0.02, sk_y - S * 0.18),
               (base + S * 0.055, sk_y - S * 0.08)]
        triad_poly(surf, ear, BONE_CORE, BONE, SHEEN, inset_amt=0.22)
    triad_ellipse(surf, sk_x - S * 0.02, sk_y - S * 0.01, S * 0.045, S * 0.05,
                  SOCKET_CORE, SOCKET_FILL, SOCKET_SHEEN, outline=None)

    # Front legs PAWING HIGH — lifted well off the baseline (the rear tell).
    bone_limb(surf, (chest_x - S * 0.03, chest_y - S * 0.0),
              (chest_x - S * 0.17, chest_y - S * 0.13),
              (chest_x - S * 0.27, chest_y - S * 0.24), legw,
              body=HORSE_BODY, core=HORSE_CORE)
    bone_limb(surf, (chest_x - S * 0.01, chest_y + S * 0.06),
              (chest_x - S * 0.16, chest_y - S * 0.0),
              (chest_x - S * 0.255, chest_y - S * 0.09), legw,
              body=HORSE_BODY, core=HORSE_CORE)
    for hx, hy in ((chest_x - S * 0.27, chest_y - S * 0.24),
                   (chest_x - S * 0.255, chest_y - S * 0.09)):
        triad_ellipse(surf, hx, hy, S * 0.05, S * 0.035,
                      RUST_CORE, RUST, RUST_SHEEN)

    # ── BACK / SPINE line — withers to croup; the seat lands ON it ────────────
    withers = (chest_x + S * 0.05, chest_y - S * 0.13)
    croup   = (haunch_x + S * 0.0, haunch_y - S * 0.155)
    back_mid_x = (withers[0] + croup[0]) * 0.5
    back_mid_y = min(withers[1], croup[1]) - S * 0.01
    # Deeper saddle-dark back band: the value seam the rider pops off of.
    back_band = [
        (withers[0] - S * 0.02, withers[1] + S * 0.02),
        (back_mid_x, back_mid_y),
        (croup[0] + S * 0.02, croup[1] + S * 0.02),
        (croup[0] - S * 0.01, croup[1] + S * 0.10),
        (back_mid_x, back_mid_y + S * 0.10),
        (withers[0] - S * 0.02, withers[1] + S * 0.12),
    ]
    triad_poly(surf, back_band, BACK_CORE, BACK_SHADE, HORSE_SHEEN, inset_amt=0.10)

    # Zarape — a single rust wedge over the back band (no stripes at this size).
    zar = [(withers[0] + S * 0.0, withers[1] + S * 0.04),
           (croup[0] + S * 0.0, croup[1] + S * 0.02),
           (croup[0] + S * 0.04, croup[1] + S * 0.13),
           (withers[0] + S * 0.02, withers[1] + S * 0.15)]
    triad_poly(surf, zar, RUST_CORE, RUST, RUST_SHEEN, inset_amt=0.10)

    rid_x = back_mid_x + S * 0.01
    seat_y = back_mid_y - S * 0.04

    # STRADDLING LEG down the near flank — the seated-astride tell, drawn first.
    bone_limb(surf, (rid_x + S * 0.05, seat_y + S * 0.04),
              (rid_x + S * 0.085, seat_y + S * 0.15),
              (rid_x + S * 0.06, seat_y + S * 0.25), legw * 0.7,
              body=BONE, core=BONE_CORE)
    triad_ellipse(surf, rid_x + S * 0.06, seat_y + S * 0.26, S * 0.05, S * 0.032,
                  RUST_CORE, RUST, RUST_SHEEN)

    # HARD HORIZONTAL INK CHANNEL under the seat — drawn before the rider torso.
    _ink_channel(surf, [
        (rid_x - S * 0.10, seat_y + S * 0.03),
        (rid_x, seat_y + S * 0.01),
        (rid_x + S * 0.10, seat_y + S * 0.03),
    ], int(S * 0.06))

    # Rider torso — brick block ABOVE the channel, on the saddle.
    block = [(rid_x - S * 0.085, seat_y - S * 0.115),
             (rid_x + S * 0.085, seat_y - S * 0.115),
             (rid_x + S * 0.07, seat_y - S * 0.01),
             (rid_x - S * 0.07, seat_y - S * 0.01)]
    triad_poly(surf, block, RUST_CORE, RUST, RUST_SHEEN, inset_amt=0.12)

    # Rider skull pulled HIGH, clear of the withers and the horse muzzle.
    rh_y = seat_y - S * 0.20
    triad_ellipse(surf, rid_x, rh_y, S * 0.082, S * 0.088, BONE_CORE, BONE, SHEEN)
    for ex in (rid_x - S * 0.028, rid_x + S * 0.028):
        pygame.draw.circle(surf, SOCKET_CORE, (int(ex), int(rh_y)), int(S * 0.022))

    # SOMBRERO-ARM LOLLIPOP spike — thin arm into clear sky, ochre disc cap.
    hand = (rid_x + S * 0.155, rh_y - S * 0.20)
    pygame.draw.line(surf, INK, (rid_x + S * 0.06, seat_y - S * 0.10),
                     hand, int(legw + SS * 1.4))
    pygame.draw.line(surf, BONE, (rid_x + S * 0.06, seat_y - S * 0.10),
                     hand, int(legw * 0.55))
    _ell(surf, INK, hand[0], hand[1] + S * 0.004, S * 0.105, S * 0.04)
    triad_ellipse(surf, hand[0], hand[1] - S * 0.004, S * 0.10, S * 0.036,
                  OCHRE_CORE, OCHRE, OCHRE_SHEEN)
    crown = [(hand[0] - S * 0.03, hand[1] - S * 0.03),
             (hand[0] - S * 0.018, hand[1] - S * 0.085),
             (hand[0] + S * 0.04, hand[1] - S * 0.085),
             (hand[0] + S * 0.052, hand[1] - S * 0.03)]
    triad_poly(surf, crown, OCHRE_CORE, OCHRE, OCHRE_SHEEN, inset_amt=0.20)

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (target_size, target_size))


# ── the prop -> pillar mirror (kept as-is — AD signed it off) ────────────────

def draw_pillar(width, height, top_cap=True):
    W = width * SS
    H = height * SS
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W * 0.5

    shaft_w = W * 0.26
    shaft = pygame.Rect(int(cx - shaft_w / 2), 0, int(shaft_w), int(H))
    pygame.draw.rect(surf, OCHRE_CORE, shaft)
    inner = shaft.inflate(-int(SS * 3), 0)
    pygame.draw.rect(surf, OCHRE, inner)
    pygame.draw.rect(surf, OCHRE_SHEEN,
                     (int(cx - shaft_w / 2 + SS * 2), 0,
                      int(shaft_w * 0.26), int(H)))
    band_n = max(5, int(height / 12))
    for i in range(band_n):
        by = int(H * (i + 0.5) / band_n)
        col = RUST if i % 2 == 0 else TURQ
        pygame.draw.line(surf, col,
                         (cx - shaft_w / 2, by - SS),
                         (cx + shaft_w / 2, by + SS), max(2, int(SS * 1.4)))

    if top_cap:
        sk_r = shaft_w * 0.92
        by = H - sk_r - W * 0.05
        triad_ellipse(surf, cx, by, sk_r, sk_r * 1.05, BONE_CORE, BONE, SHEEN)
        muzzle = [
            (cx - sk_r * 0.5, by + sk_r * 0.35),
            (cx, by + sk_r * 1.45),
            (cx + sk_r * 0.5, by + sk_r * 0.35),
        ]
        triad_poly(surf, muzzle, BONE_CORE, BONE, SHEEN, inset_amt=0.18)
        for sgn in (-1, 1):
            ear = [
                (cx + sgn * sk_r * 0.35, by - sk_r * 0.7),
                (cx + sgn * sk_r * 0.6, by - sk_r * 1.25),
                (cx + sgn * sk_r * 0.72, by - sk_r * 0.55),
            ]
            triad_poly(surf, ear, BONE_CORE, BONE, SHEEN, inset_amt=0.22)
        for ex in (cx - sk_r * 0.4, cx + sk_r * 0.4):
            triad_ellipse(surf, ex, by - sk_r * 0.05, sk_r * 0.26, sk_r * 0.3,
                          SOCKET_CORE, SOCKET_FILL, SOCKET_SHEEN, outline=None)
            pygame.draw.circle(surf, INK, (int(ex), int(by - sk_r * 0.05)),
                               max(1, int(sk_r * 0.1)))
        pygame.draw.arc(surf, TURQ,
                        (int(cx - sk_r * 0.55), int(by - sk_r * 0.55),
                         int(sk_r * 1.1), int(sk_r * 0.6)),
                        math.pi * 0.08, math.pi * 0.92, max(2, int(SS * 1.4)))
        triad_ellipse(surf, cx, by + sk_r * 0.05, sk_r * 0.22, sk_r * 0.22,
                      MARI_CORE, MARIGOLD, MARI_SHEEN)

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (width, height))


# ── pure-black silhouette read (the AD ship test) ────────────────────────────

def draw_silhouette(target_size, tiny=False):
    rgba = draw_jinete_tiny(target_size) if tiny else draw_jinete(target_size)
    sil = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(rgba)
    surf = mask.to_surface(setcolor=(14, 12, 16, 255), unsetcolor=(0, 0, 0, 0))
    sil.blit(surf, (0, 0))
    return sil


# ── sky-backed crop helper ───────────────────────────────────────────────────

def sky_crop(sheet, x, y, size, surf32, top, bot, label_small, caption_fn,
             txt1, txt2):
    for yy in range(size):
        t = yy / size
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(sheet, col, (x, y + yy), (x + size, y + yy))
    pygame.draw.rect(sheet, (24, 20, 26), (x, y, size, size), 2)
    sheet.blit(pygame.transform.scale(surf32, (size, size)), (x, y))
    caption_fn(txt1, x, y + size + 4)
    caption_fn(txt2, x, y + size + 20)


# ── sheet composition ─────────────────────────────────────────────────────────

def build_sheet():
    W, H = 1000, 790
    sheet = pygame.Surface((W, H))
    sheet.fill((46, 40, 52))

    font = pygame.font.SysFont("arial", 18, bold=True)
    small = pygame.font.SysFont("arial", 13)

    def label(txt, x, y, col=(245, 238, 226)):
        sheet.blit(font.render(txt, True, col), (x, y))

    def caption(txt, x, y, col=(208, 200, 210)):
        sheet.blit(small.render(txt, True, col), (x, y))

    label("EL CHARRO JINETE — rearing bone-horse + charro rider  ·  round 3 (FINAL)",
          18, 12, (252, 224, 150))
    caption("ROUND 3 — rider LIFTED onto the spine (hips over the barrel, leg "
            "straddling the near flank), HARD ink channel UNDER the seat, "
            "saddle-dark back band, rider skull pulled clear of the horse muzzle",
            18, 36)

    # Large creature.
    big = draw_jinete(320)
    sheet.blit(big, (20, 58))
    caption("creature · large (rider seated ASTRIDE the spine)", 20, 382)

    # Mid-scale legibility ramp.
    mid = draw_jinete(160)
    sheet.blit(mid, (352, 58))
    caption("creature · 160px (full detail)", 352, 224)

    # 32px dedicated build + 4x zoom (color).
    tiny = draw_jinete_tiny(32)
    sheet.blit(tiny, (352, 250))
    caption("32px", 352, 284)
    zoom = pygame.transform.scale(tiny, (128, 128))
    sheet.blit(zoom, (392, 250))
    caption("32px @4x (dedicated build)", 392, 382)

    # Pure-black silhouette read — large + 32px.
    sil_big = draw_silhouette(160)
    sheet.blit(sil_big, (20, 408))
    caption("silhouette · 160px", 20, 574)
    sil_tiny = draw_silhouette(32, tiny=True)
    sil_zoom = pygame.transform.scale(sil_tiny, (128, 128))
    sheet.blit(sil_zoom, (192, 408))
    caption("BLACK SILHOUETTE 32px @4x", 192, 538)
    caption("read: rider astride a reared horse, hat-arm spike", 192, 554)

    # 32px on OCHRE DAY sky and on NIGHT sky.
    sky_crop(sheet, 352, 408, 128, tiny,
             (236, 196, 120), (210, 158, 92), small, caption,
             "32px @4x · ochre DAY sky", "two bodies separate at the seat")
    sky_crop(sheet, 500, 408, 128, tiny,
             (40, 44, 84), (22, 26, 54), small, caption,
             "32px @4x · NIGHT sky", "bone rider pops off saddle-dark back")

    # Prop -> pillar mirror (unchanged — AD signed off).
    px = 690
    py = 58
    cap_h = 84
    shaft_h = 150
    big_w = 60
    bot_cap = draw_pillar(big_w, cap_h, top_cap=True)
    bot_shaft = draw_pillar(big_w, shaft_h, top_cap=False)
    top_cap = pygame.transform.flip(bot_cap, False, True)
    top_shaft = pygame.transform.flip(bot_shaft, False, True)

    gap = 56
    sheet.blit(top_shaft, (px, py))
    sheet.blit(top_cap, (px, py + shaft_h))
    gap_y = py + shaft_h + cap_h
    sheet.blit(bot_cap, (px, gap_y + gap))
    sheet.blit(bot_shaft, (px, gap_y + gap + cap_h))
    caption("prop->pillar mirror", px - 4, py + shaft_h * 2 + cap_h * 2 + gap + 4)
    caption("slim lance + on-axis skull finial", px - 4,
            py + shaft_h * 2 + cap_h * 2 + gap + 20)

    # 32px pillar cap.
    tcap = draw_pillar(28, 40, top_cap=True)
    sheet.blit(tcap, (px + 130, py + 20))
    czoom = pygame.transform.scale(tcap, (96, 138))
    sheet.blit(czoom, (px + 168, py + 20))
    caption("cap 28px / @4x", px + 130, py + 168)

    # Red-split reference.
    rx0 = px + 130
    ry0 = py + 206
    caption("three warm reds split (this=brick H):", rx0, ry0 - 18)
    for i, (nm, col) in enumerate([
            ("B chile (214,86,44)", (214, 86, 44)),
            ("E rose (214,72,86)", (214, 72, 86)),
            ("H rust (176,70,56)", RUST)]):
        pygame.draw.rect(sheet, col, (rx0, ry0 + i * 30, 40, 24))
        pygame.draw.rect(sheet, (20, 18, 22), (rx0, ry0 + i * 30, 40, 24), 2)
        caption(nm, rx0 + 48, ry0 + i * 30 + 5)
    pygame.draw.rect(sheet, SHEEN, (rx0, ry0 + 2 * 30, 40, 24), 3)

    # Two-body annotation callout.
    ay0 = py + 320
    caption("two-BODY read forced by:", rx0, ay0)
    for i, t in enumerate([
            "1 rider hips ON the spine (not chest)",
            "2 hard ink channel UNDER the seat",
            "3 leg straddles DOWN the near flank",
            "4 saddle-dark back band value step",
            "5 rider skull HIGH, off horse muzzle"]):
        caption(t, rx0, ay0 + 18 + i * 18, (224, 214, 200))

    # Palette swatch strip.
    sw_y = H - 50
    swatches = [
        ("rust", RUST), ("ochre", OCHRE), ("turq", TURQ), ("bone", BONE),
        ("barrel", HORSE_BODY), ("back", BACK_SHADE), ("marigold", MARIGOLD),
        ("ink", INK), ("sheen", SHEEN),
    ]
    for i, (nm, col) in enumerate(swatches):
        sx = 20 + i * 72
        pygame.draw.rect(sheet, col, (sx, sw_y, 60, 28))
        pygame.draw.rect(sheet, (20, 18, 22), (sx, sw_y, 60, 28), 2)
        caption(nm, sx + 2, sw_y + 30)

    return sheet


if __name__ == "__main__":
    out = build_sheet()
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(out, dst)
    print("wrote", dst)
