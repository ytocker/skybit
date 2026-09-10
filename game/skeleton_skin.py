"""SKELETON store costume — an x-ray Pip in a hooded open-front cloak.

The dark body silhouette reads as a draped cloak (cowl over the back of the
skull, tattered hem where the tail was, open chest V); a COMPLETE bone skeleton
is painted *through* the open front in thick high-contrast white bone with a
dominant hooked beak bone. Day-of-the-Dead graphic clarity: the bones are the
brightest element and survive the 40px store/thumbnail downscale on day AND
night skies.

Self-contained on purpose: registered via `parrot._store_skin_builders()` like
the other sibling skin modules, so it imports helpers one-way from
`store_skins`/`parrot`/`dollar_parrot_ghost` and is never imported back.
"""
import math
import pygame

from game.store_skins import _make_skin, PARROT_DY
from game.dollar_parrot_ghost import _pal, _build_wing
from game.parrot import SPRITE_W, SPRITE_H


def _shade(c, f):
    """Multiply an RGB(A) toward black (f<1) or white (f>1), clamped."""
    return tuple(max(0, min(255, int(round(v * f)))) for v in c[:3])


# ── the cloak: the dark body mass as a draped hooded cloak ────────────────────
# In native 64×60 sprite space (same space as the recoloured body), so the
# composite skull/ribs/beak still land exactly. A cloak only reads by SILHOUETTE
# at 40px, so the hem is cut as hard triangular teeth on the OUTER edge (interior
# notches dissolve) and the bottom edge zig-zags so the outline traces a ragged
# hem; the hood is a peaked cowl with a shadow-crescent recess so the skull peers
# out of a hole.
_CLOAK_DRAPE = [                                   # back drape with a hard-toothed tattered hem
    (13, 28), (20, 24), (28, 22), (36, 22), (42, 24), (46, 28),   # shoulders → top
    (45, 34), (42, 40),                                          # front-right fall
    (37, 48), (33, 42), (28, 50), (24, 41), (19, 49), (15, 40),  # hem teeth (R→L)
    (10, 48), (8, 38),                                           # last tooth → back edge
]
_CLOAK_CHEST = [                                   # open-front V: dark interior the ribs show through
    (41, 24), (46, 31), (44, 41), (36, 47),
    (27, 47), (21, 40), (19, 29), (27, 24),
]
_HOOD_OUTER = [                                    # cowl cloth over crown/back/sides of skull, sharp peak
    (36, 31), (37, 16), (41, 8), (47, 4), (53, 8),
    (58, 15), (58, 24), (54, 30), (44, 32),
]
_HOOD_RIM = [(44, 32), (54, 30), (58, 24), (58, 15), (53, 8), (47, 4)]
# Hem highlight traces the toothed bottom edge so the rim catches the ragged hem.
_HEM_EDGE = [(8, 38), (10, 48), (15, 40), (19, 49), (24, 41), (28, 50),
             (33, 42), (37, 48), (42, 40)]
_FOLDS = [                                         # one long vertical fall + two shorter, all on the back drape
    [(29, 25), (26, 47)],
    [(21, 26), (17, 45)],
    [(14, 30), (12, 44)],
]


def cloak_base(angle_deg, palette, **opts):
    """Native 64×60 cloaked-Pip body: a hooded, open-front cloak in the given
    flesh `palette`'s dark cloth tones.

    opts:
      cloth  — override the main cloak cloth colour (lift it off near-navy so the
               mass reads on the night sky).
      edge   — override hood-rim/hem highlight colour.
      inner  — override chest-opening / hood-interior colour.
    """
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    cloth = opts.get('cloth') or palette['body_main']
    shadow = palette['tail_line']
    edge = opts.get('edge') or _shade(cloth, 2.4)
    inner = opts.get('inner') or _shade(palette['body_shadow'], 0.55)

    # back + bottom drape (the cloak mass), then fold shadows so it reads as cloth
    pygame.draw.polygon(surf, cloth, _CLOAK_DRAPE)
    for a, b in _FOLDS:
        pygame.draw.line(surf, shadow, a, b, 2)

    # open-front chest: dark recessed interior the ribcage/spine read against,
    # framed by a 2px shadow gap so the bright bones win the opening at 40px
    pygame.draw.polygon(surf, inner, _CLOAK_CHEST)
    pygame.draw.polygon(surf, shadow, _CLOAK_CHEST, 2)

    # wing flaps over the drape (dark backing for the wing-bone layer, and it
    # reads as the cloak swaying with the flap)
    wing = _build_wing(angle_deg, palette)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # hood cowl over the skull, with a dark interior so the skull sits recessed,
    # plus a hard shadow crescent rim so the skull "peers out of a hole"
    pygame.draw.polygon(surf, cloth, _HOOD_OUTER)
    face = pygame.Rect(38, 9, 20, 24)
    pygame.draw.ellipse(surf, inner, face)                         # face opening
    pygame.draw.ellipse(surf, shadow, face, 2)                     # recess crescent

    # crisp lighter rim on the hood + tattered hem so it reads as fabric
    pygame.draw.lines(surf, edge, False, _HOOD_RIM, 1)
    pygame.draw.lines(surf, edge, False, _HEM_EDGE, 1)

    # feet poking out below the hem
    pygame.draw.line(surf, palette['foot'], (28, 47), (26, 51), 2)
    pygame.draw.line(surf, palette['foot'], (34, 47), (36, 51), 2)

    return surf


# ── anatomy, in COMPOSITE space (base coords + PARROT_DY on y) ────────────────
# Original anchors (parrot.py): head centre (47,21) r~11; beak quad
# (55,21)(61,24)(58,28)(52,26); body centre (32,32); wing centre (34,28); feet
# (28,45)/(34,45). +PARROT_DY(20) on every y to reach composite space.
DY = PARROT_DY
HX, HY = 47, 21 + DY                       # skull centre → (47,41)
WING_CENTER = (34, 28 + DY)                # (34,48) — matches _build_wing blit

# Cervical → thoracic → lumbar → caudal vertebra centres (skull base to tail).
_SPINE = [(43, 23 + DY), (39, 25 + DY), (34, 27 + DY), (29, 29 + DY),
          (24, 31 + DY), (19, 33 + DY), (14, 34 + DY)]

# A bird ribcage reads as a rounded BASKET: each rib springs off the thoracic
# spine, bows OUT and DOWN around the chest, then curves FORWARD onto a deep
# breastbone (the keel/sternum). At 40px it only reads as a cage with ENOUGH
# ribs at an EVEN pitch and a clear top (spine) and bottom (keel) boundary.
# 6 rib roots, evenly pitched along the spine, spreading BACK from the shoulder
# (x 37) to the lumbar region (x 20) — the cage's top/back boundary.
_RIB_ROOTS = [(37, 25 + DY), (34, 26 + DY), (31, 28 + DY),
              (27, 29 + DY), (24, 31 + DY), (20, 32 + DY)]
# Sternum/keel: the ribs sweep forward-and-down to CONVERGE on a single deep keel
# tip (the hull point) rather than a flat shelf — the front ribs land at the tip,
# the back ribs progressively behind it along a keel line arcing UP toward the
# back, so the cage bottom reads as a boat hull rising to a clear breastbone.
_KEEL = [(37, 44 + DY), (37, 44 + DY), (35, 45 + DY),
         (33, 46 + DY), (31, 45 + DY), (29, 43 + DY)]

# Wing arm-bones + phalanges in the 50×50 WING-LOCAL space (so they rotate with
# the wing exactly like the feather polygon does).
_WING_LOCAL = {
    "humerus": [(24, 24), (35, 18)],
    "radius":  [(35, 18), (46, 25)],
    "phalanges": [
        [(46, 25), (45, 14)],
        [(46, 25), (49, 22)],
        [(46, 25), (40, 31)],
        [(42, 22), (45, 16)],
    ],
    "joints": [(24, 24), (35, 18), (46, 25)],
}


def _rib_curve(i):
    """Rib `i` as a smooth C-curve: springs off the spine root, bows OUT and
    DOWN around the chest, then sweeps FORWARD onto its keel landing. Quadratic
    Bézier root→belly-control→keel so the curve actually bends into a basket wall
    rather than reading as a straight slash."""
    n = len(_RIB_ROOTS)
    root = _RIB_ROOTS[i]
    keel = _KEEL[i]
    # Belly control point pushed DOWN and BACK of the root→keel chord so each rib
    # reads as a C-curve. The bulge is biased STRONGER on the front (beak-side,
    # low i) ribs so the cage's bottom edge arcs up to a clear sternum point.
    front_bias = (n - 1 - i) / (n - 1)          # 1 at the front rib, 0 at the back
    bulge = 5.0 + i * 0.7                        # deeper basket wall toward the back
    back = 2.0 + i * 0.9 + front_bias * 3.0      # forward sweep, stronger up front
    cx = (root[0] + keel[0]) / 2 - back
    cy = max(root[1], keel[1]) + bulge
    ctrl = (cx, cy)
    pts = []
    for s in range(9):
        t = s / 8.0
        u = 1 - t
        x = u * u * root[0] + 2 * u * t * ctrl[0] + t * t * keel[0]
        y = u * u * root[1] + 2 * u * t * ctrl[1] + t * t * keel[1]
        pts.append((x, y))
    return pts


# ── styled stroke primitives ─────────────────────────────────────────────────

def stroke(surf, color, p0, p1, w):
    """A bone shaft with rounded caps."""
    pygame.draw.line(surf, color, p0, p1, w)
    r = max(1, w // 2)
    pygame.draw.circle(surf, color, (int(round(p0[0])), int(round(p0[1]))), r)
    pygame.draw.circle(surf, color, (int(round(p1[0])), int(round(p1[1]))), r)


def polybone(surf, color, pts, w):
    for i in range(len(pts) - 1):
        stroke(surf, color, pts[i], pts[i + 1], w)


def knob(surf, color, p, r):
    pygame.draw.circle(surf, color, (int(round(p[0])), int(round(p[1]))), r)


# Default STYLE keys a design overrides:
#   bone — main bone colour; hi — highlight rim (None to skip); sh — keyline under
#   bone for day-sky legibility (None to skip); w_long/w_rib/w_fine — stroke
#   widths for long bones / ribs / fine bones; beak — dominant-beak fill (or bone).
DEFAULT_STYLE = dict(
    bone=(238, 240, 246), hi=(255, 255, 255), sh=(20, 22, 34),
    w_long=3, w_rib=2, w_fine=2, beak=None,
)


def _wing_bone_layer(angle_deg, style):
    """Render wing arm-bones + phalanges in local space, rotate by the wing
    angle, return the rotated surface and its blit topleft for WING_CENTER."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    col, sh, hi = style["bone"], style["sh"], style["hi"]
    wl, wf = style["w_long"], style["w_fine"]
    if sh is not None:
        stroke(w, sh, *_WING_LOCAL["humerus"], wl + 2)
        stroke(w, sh, *_WING_LOCAL["radius"], wl + 2)
        for ph in _WING_LOCAL["phalanges"]:
            stroke(w, sh, *ph, wf + 1)
    stroke(w, col, *_WING_LOCAL["humerus"], wl)
    stroke(w, col, *_WING_LOCAL["radius"], wl)
    for ph in _WING_LOCAL["phalanges"]:
        stroke(w, col, *ph, wf)
    for j in _WING_LOCAL["joints"]:
        knob(w, col, j, max(2, wl - 1))
        if hi is not None:
            knob(w, hi, (j[0] - 1, j[1] - 1), 1)
    rot = pygame.transform.rotate(w, angle_deg)
    tl = rot.get_rect(center=WING_CENTER).topleft
    return rot, tl


def paint_skeleton(surf, angle_deg, style=None):
    """Paint the COMPLETE bird skeleton onto the composite (over dark flesh).

    The STYLE dict controls the bone material; the anatomy is fixed here so no
    bone can go missing. Wing phalanges rotate in register with `angle_deg`.
    """
    st = dict(DEFAULT_STYLE)
    if style:
        st.update(style)
    bone, hi, sh = st["bone"], st["hi"], st["sh"]
    wl, wr, wf = st["w_long"], st["w_rib"], st["w_fine"]
    beak_col = st["beak"] or bone

    # keyline pass (drawn first, slightly fatter, for day-sky legibility)
    if sh is not None:
        for i in range(len(_RIB_ROOTS)):
            polybone(surf, sh, _rib_curve(i), wr + 1)
        polybone(surf, sh, _SPINE, wl + 1)
        polybone(surf, sh, _KEEL, wr + 1)

    # wing arm-bones + phalanges (behind the body bones, flapping)
    layer, tl = _wing_bone_layer(angle_deg, st)
    surf.blit(layer, tl)

    # ribcage
    for i in range(len(_RIB_ROOTS)):
        polybone(surf, bone, _rib_curve(i), wr)
    polybone(surf, bone, _KEEL, wr)                     # sternum/keel

    # spine + vertebra knobs
    polybone(surf, bone, _SPINE, wl)
    for v in _SPINE:
        knob(surf, bone, v, max(2, wl - 1))
        if hi is not None:
            knob(surf, hi, (v[0] - 1, v[1] - 1), 1)

    # pelvis + two legs + clawed feet
    pelvis = (22, 33 + DY)
    knob(surf, bone, pelvis, wl)
    for hipx, foot, splay in ((25, (26, 49 + DY), -3), (30, (36, 49 + DY), 3)):
        knee = (hipx + splay, 45 + DY)
        stroke(surf, bone, pelvis, knee, wl)            # femur
        stroke(surf, bone, knee, foot, wf)              # tibia
        for dx in (-3, 0, 3):                           # 3-toe claw
            stroke(surf, bone, foot, (foot[0] + dx, foot[1] + 3), max(1, wf - 1))

    # tail bones (caudal vertebrae fanning into the original tail)
    tail_root = _SPINE[-1]
    for tip in ((3, 35 + DY), (4, 41 + DY), (9, 42 + DY), (15, 39 + DY)):
        stroke(surf, bone, tail_root, tip, wf)

    # skull + hollow eye-socket
    skull_r = 11
    if sh is not None:
        pygame.draw.circle(surf, sh, (HX, HY), skull_r + 1, wf + 1)
    pygame.draw.circle(surf, bone, (HX, HY), skull_r, wf)
    pygame.draw.circle(surf, bone, (HX - 1, HY - 4), 5, max(1, wf - 1))  # cranium dome
    pygame.draw.circle(surf, (8, 9, 16), (HX + 3, HY - 1), 4)            # hollow socket
    pygame.draw.circle(surf, bone, (HX + 3, HY - 1), 4, max(1, wf - 1))
    knob(surf, bone, (HX + 2, HY - 2), 1)

    # DOMINANT beak bone (the signature element): an oversized hooked avian
    # beak-bone projecting FORWARD — long upper mandible curving to a downward
    # raptor hook, hinged lower jaw, nostril notch.
    upper = [(54, 37), (66, 42), (67, 47), (62, 47), (57, 44), (54, 42)]
    lower = [(55, 45), (63, 46), (62, 49), (55, 47)]
    if sh is not None:
        pygame.draw.polygon(surf, sh, [(p[0], p[1] + 1) for p in upper])
    pygame.draw.polygon(surf, beak_col, upper)
    pygame.draw.polygon(surf, beak_col, lower)
    pygame.draw.line(surf, st["sh"] or beak_col, (55, 44), (63, 45), 1)  # mandible gap
    knob(surf, (8, 9, 16), (57, 41), 1)                 # nostril
    if hi is not None:
        pygame.draw.line(surf, hi, (55, 39), (65, 43), 1)  # culmen gloss


# ── BOLD CARTOON BONE design ─────────────────────────────────────────────────
# Thick chunky PURE WHITE bones with crisp dark keylines (Day-of-the-Dead clean).
# Structural bones stay fat; fill bones (ribs, keel) are thinned so dark flesh
# survives between them at thumbnail size.
STYLE = dict(
    bone=(250, 252, 255), hi=(255, 255, 255), sh=(12, 13, 22),
    w_long=5, w_rib=2, w_fine=4, beak=(255, 255, 255),
)

# Pure-dark flesh tone used to CARVE negative space back between bones.
_VOID = (8, 9, 16)

# Darker flesh than the default — sinks the body so chunky white bone carries the
# entire read at thumbnail size.
_FLESH = _pal(
    tail=[(14, 15, 26), (18, 20, 32), (22, 24, 38), (26, 28, 44)],
    tail_line=(8, 9, 16),
    body_shadow=(8, 9, 16),
    body_main=(18, 20, 32),
    body_chest=(22, 24, 38),
    body_belly=(28, 31, 48),
    sheen=None,
    wing_main=(15, 17, 28),
    wing_dark=(9, 10, 18),
    wing_tip=(21, 23, 36),
    wing_secondary=None,
    wing_highlight=None,
    head_shadow=(11, 12, 20),
    head_main=(21, 23, 36),
    head_cheek=(27, 30, 46),
    head_crown=(30, 33, 50),
    lens_frame=(0, 0, 0), lens_body=(0, 0, 0),
    lens_tint=None, lens_glint=None,
    beak_main=(17, 18, 30),
    beak_dark=(9, 10, 18),
    beak_gloss=(24, 26, 40),
    foot=(14, 15, 26),
)

# One crisp, clearly-lighter cool-steel edge so the hood + tattered hem read as a
# single bold clean shape against the near-black cloth — same graphic register as
# the thick high-contrast bones.
_CLOAK_EDGE = (192, 200, 226)
# The cloak cloth itself must out-value navy, not just its rim: a desaturated cool
# grey-violet (luma ~63) lifts the cowl + drape into a distinct mid-dark mass
# against the night sky while staying clearly darker than the white bones; the day
# read stays a flat cool grey shape, not a distraction from the white-bone hero.
_CLOAK_CLOTH = (66, 62, 90)
# Interior of the open-front V + hood face: darker than the lifted cloth so the
# ribcage/spine/skull win their opening — "skeleton seen THROUGH an open cloak".
_CLOAK_INNER = (16, 17, 30)


def _flesh_base(angle_deg):
    # Shared cloak shape on the lifted grey-violet cloth, a darker recessed
    # interior so the open-front ribcage wins, then re-strike the hood-rim and
    # tattered-hem keylines one step thicker so the cloak reads as a single bold
    # graphic shape matching the chunky bones, not a hairline rim.
    surf = cloak_base(angle_deg, _FLESH, cloth=_CLOAK_CLOTH,
                      inner=_CLOAK_INNER, edge=_CLOAK_EDGE)
    pygame.draw.lines(surf, _CLOAK_EDGE, False, _HOOD_RIM, 2)
    pygame.draw.lines(surf, _CLOAK_EDGE, False, _HEM_EDGE, 2)
    return surf


def _rib_gaps(surf):
    """Carve pure-dark flesh BETWEEN the white rib arcs so each rib of the basket
    reads SEPARATELY top-to-bottom — white-on-white floods them into one slab.
    Each gap traces the negative space between two consecutive rib curves and is
    carried UP to within ~1px of the spine (leaving only a hairline white
    attachment point per rib) so the top of the cage stops fusing into one block.
    A hard dark moat under the keel walls the cage off from the pelvis/legs."""
    ribs = [_rib_curve(i) for i in range(len(_RIB_ROOTS))]
    spine_y = lambda x: DY + 23 + (43 - x) * (11.0 / 29.0)  # spine line at x
    for a, b in zip(ribs, ribs[1:]):
        gap = [((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2 + 0.5)
               for pa, pb in zip(a, b)]
        gx = gap[0][0]
        # Start the gap just below the spine stroke's lower edge, leaving a ~1px
        # white attachment so each rib still hangs off the spine but is
        # individuated from its neighbour from the attachment down.
        gap[0] = (gx, spine_y(gx) + 3.0)
        pygame.draw.lines(surf, _VOID, False,
                          [(round(x), round(y)) for x, y in gap], 2)
    moat = [(x, y + 3) for x, y in _KEEL]
    pygame.draw.lines(surf, _VOID, False,
                      [(round(x), round(y)) for x, y in moat], 3)


def _eye_socket(surf):
    """Re-stamp an enlarged pure-dark eye-hole so even the 40px thumbnail keeps
    one skull eye — the dot that sells 'skull'."""
    cx, cy = HX + 2, HY - 1
    pygame.draw.circle(surf, STYLE["bone"], (cx, cy), 6, 2)   # bone rim
    pygame.draw.circle(surf, _VOID, (cx, cy), 5)              # hollow socket


def _beak_post(surf):
    """The DOMINANT beak bone: one big clean forward-projecting triangular wedge,
    hook tip below the jawline, framed top + bottom by pure-dark flesh so it
    detaches as its own bone at 40px (no commissure ticks — they read as a gaping
    mouth at 1x; the dark frame does the separation)."""
    bone = STYLE["bone"]
    key = STYLE["sh"]
    pygame.draw.line(surf, _VOID, (55, 35), (66, 39), 2)     # over the culmen
    pygame.draw.line(surf, _VOID, (55, 47), (62, 50), 2)     # under the jaw
    wedge = [(56, 38), (72, 44), (70, 50), (63, 49), (59, 46), (56, 44)]
    pygame.draw.polygon(surf, key, [(x, y + 1) for x, y in wedge])  # drop keyline
    pygame.draw.polygon(surf, bone, wedge)
    pygame.draw.polygon(surf, key, wedge, 2)                 # crisp dark outline
    knob(surf, bone, (56, 41), 2)                            # skull/beak knuckle
    pygame.draw.circle(surf, _VOID, (60, 42), 1)            # nostril


def _paint(surf, angle):
    paint_skeleton(surf, angle, style=STYLE)
    # Carve the negative space the base's white fill destroyed.
    _rib_gaps(surf)
    _eye_socket(surf)
    _beak_post(surf)


build = _make_skin(_paint, base_fn=_flesh_base)

BUILDERS = {"skin_skeleton": build}
