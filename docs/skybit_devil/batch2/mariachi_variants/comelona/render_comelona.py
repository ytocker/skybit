"""
Calaca Comelona — the gluttonous Day-of-the-Dead street-food VENDOR whose
open ribcage is a literal pantry stuffed with food (BATCH 2 / mariachi-lineage
warm-skeleton family, lead facet: EXPOSED ANATOMY).

Procedural Pygame, house style: chibi proportions, flat saturated fills + hard
1-2px ink keylines, form via the dark-core -> flat-fill -> top-left rim-sheen
TRIAD (never soft gradient), silhouette POP via a 1px outline grown from the
alpha mask, supersample (SS=4) -> smoothscale.

Round 2 re-engineers the signature read so it survives to true 32px: the belly
is now a bold DARK interior CAVITY (a deep ink pocket, an arch of negative
space) framed by only ~3 THICK open ribs per side swung like cupboard doors,
with 3 HIGH-CONTRAST food lobes popping PROUD of the dark pocket. Negative
space carries the tell the way Risón's dropped jaw and Papelito's punched
sockets do — even rib-banding is gone. The figure is re-weighted bottom-heavy
(wide bowed femurs + broad planted feet + fuller pelvis) and the vendor hat is
pushed to a flat, wide, distinctly low brim so it reads OFF the Mariachi anchor.

Red-split pin (a clean PASS in round 1) is UNTOUCHED: chile-red `(214,86,44)`
stays a SMALL accent ONLY (hatband + the one cigar-chile in the jaw + the one
interior chile lobe). HERO mass stays masa-gold/bone.

Sheet shows the creature AND its prop->pillar mirror (market-pole ristra +
round comal cap) at large + 32px scales, a pure-black silhouette panel, the
true 32px chip on BOTH a day-ochre AND a night sky, and the pinned swatches.

Run headless:  SDL_VIDEODRIVER=dummy python render_comelona.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# -- PINNED PALETTE (locked brief, exact hexes) -------------------------------
MASA_GOLD   = (228, 186,  96)   # masa-gold tamale/pan -- HERO body/food mass
OCHRE_HAT   = (214, 156,  72)   # pumpkin-ochre straw vendor hat
BONE        = (236, 222, 194)   # warm-bone ribcage
BONE_SHADE  = (174, 148, 106)   # tan-bone shade
CHILE       = (214,  86,  44)   # chile-red ACCENT ONLY (hatband + one chile)
CILANTRO    = (120, 170,  80)   # cilantro-green garnish, tiny
INK         = ( 30,  22,  20)   # keyline ink
SHEEN       = (250, 240, 218)   # top-left rim sheen

# Derived working tones, all kept inside the pinned families (triad cores/sheens).
BONE_CORE   = (150, 126,  90)   # dark-core under bone (deeper than tan shade)
GOLD_CORE   = (162, 122,  52)   # dark-core under masa-gold
GOLD_SHEEN  = (246, 218, 142)   # masa-gold top-left sheen
OCHRE_CORE  = (152, 104,  44)   # dark-core under straw hat
OCHRE_SHEEN = (244, 198, 124)   # straw-hat top-left sheen
CHILE_CORE  = (132,  46,  24)   # dark-core under chile-red
CHILE_SHEEN = (236, 138,  92)   # chile-red top-left sheen
CILANTRO_D  = ( 80, 120,  52)   # cilantro garnish shade
# The cavity interior is a near-black warm ink so the food lobes read as "stuff
# in a dark cupboard" -- the negative-space tell. Deeper than the bone core.
CAVITY      = ( 26,  18,  18)
CAVITY_EDGE = ( 14,  10,  10)
# Pan-dulce concha gets a CREAM read (max value contrast against the dark
# cavity) with a faint warm tint, so the red read stays demoted.
PAN_CREAM   = (244, 234, 208)
PAN_CREAM_D = (196, 178, 144)
PAN_CREAM_S = (252, 246, 230)

SS = 4   # supersample factor


# -- geometry / triad helpers (house grammar) ---------------------------------

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


def triad_poly(surf, pts, core, fill, sheen, outline=INK, sheen_pts=None):
    """Triad on an arbitrary polygon: ink keyline, core fill, inset fill, then an
    optional top-left sheen sliver."""
    if outline is not None:
        pygame.draw.polygon(surf, outline, pts)
        pygame.draw.polygon(surf, outline, pts, SS * 2)
    pygame.draw.polygon(surf, core, pts)
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    inset = [(p[0] + (cx - p[0]) * 0.16, p[1] + (cy - p[1]) * 0.16) for p in pts]
    pygame.draw.polygon(surf, fill, inset)
    if sheen_pts:
        pygame.draw.polygon(surf, sheen, sheen_pts)


def grow_outline(surf, color=INK, thickness=1):
    """1px (post-scale) outline grown from the alpha mask -- the silhouette POP.
    Run at supersample scale so it survives smoothscale."""
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) > 2:
        pygame.draw.lines(surf, color, True, outline_pts, max(1, thickness * SS))


# -- the creature -------------------------------------------------------------

def draw_comelona(target_size):
    """Squat bottom-heavy pear vendor calaca. The signature read (round 2):
    a bold DARK interior CAVITY in the belly -- a deep ink pocket framed by only
    ~3 THICK ribs per side swung open like cupboard doors -- with 3 HIGH-CONTRAST
    food lobes (cream pan dulce, masa-gold tamale, one chile-red lobe) sitting
    PROUD of the pocket. Negative space (the dark hole) carries the tell at 32px,
    not even rib-banding. Wide bowed femurs + broad planted feet anchor the
    bottom-heavy mass; one bony hand offers a fat tamale (vendor + asymmetry)."""
    S = target_size * SS
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S * 0.5

    # Layout anchors (fractions of S). Bottom-heavy: small high skull, wide low
    # ribcage belly, short splayed legs -- the pear silhouette.
    hat_y   = S * 0.200
    head_y  = S * 0.270
    belly_y = S * 0.560   # centre of the open ribcage pantry (dominant mass)
    hip_y   = S * 0.740

    # ---- BONE LEGS: short, WIDELY bowed femurs for a heavy planted base -------
    def bone_limb(p0, p1, p2, w):
        for a, b in ((p0, p1), (p1, p2)):
            pygame.draw.line(surf, INK, a, b, int(w + SS * 1.6))
        for a, b in ((p0, p1), (p1, p2)):
            pygame.draw.line(surf, BONE_SHADE, a, b, int(w))
            pygame.draw.line(surf, BONE, a, b, int(w * 0.5))
        for p in (p0, p1, p2):
            triad_ellipse(surf, p[0], p[1], w * 0.62, w * 0.62,
                          BONE_CORE, BONE, SHEEN)

    legw = S * 0.072
    # Wide-bowed femurs splayed hard outward so the squat base out-widths the
    # chest -- bottom-heavy stance, not the round-1 spindly/top-heavy read.
    bone_limb((cx - S * 0.105, hip_y),
              (cx - S * 0.205, S * 0.855),
              (cx - S * 0.155, S * 0.95), legw)
    bone_limb((cx + S * 0.105, hip_y),
              (cx + S * 0.205, S * 0.855),
              (cx + S * 0.155, S * 0.95), legw)
    # Broad flat bone feet, toes outward -- wide footprint anchors the pear.
    for fx, sgn in ((cx - S * 0.155, -1), (cx + S * 0.155, 1)):
        triad_ellipse(surf, fx + sgn * S * 0.03, S * 0.958,
                      S * 0.094, S * 0.044, BONE_CORE, BONE, SHEEN)

    # ---- FULL PELVIS (broad, so the lower body carries weight) ----------------
    pelvis = [
        (cx - S * 0.150, hip_y - S * 0.06),
        (cx + S * 0.150, hip_y - S * 0.06),
        (cx + S * 0.120, hip_y + S * 0.060),
        (cx,             hip_y + S * 0.030),
        (cx - S * 0.120, hip_y + S * 0.060),
    ]
    triad_poly(surf, pelvis, BONE_CORE, BONE, SHEEN)
    # Pelvic eye-holes (iliac fossae) -- bone read.
    for sx in (-1, 1):
        _ell(surf, INK, cx + sx * S * 0.072, hip_y - S * 0.008,
             S * 0.030, S * 0.040)

    # ---- OPEN RIBCAGE PANTRY (the dominant mass + signature read, REBUILT) ----
    # Step 1: the bone barrel BACK WALL the cupboard doors swing off. Wider than
    # round 1 so the belly out-masses the head -> bottom-heavy.
    back = [
        (cx - S * 0.250, belly_y - S * 0.150),
        (cx + S * 0.250, belly_y - S * 0.150),
        (cx + S * 0.230, belly_y + S * 0.180),
        (cx,             belly_y + S * 0.225),
        (cx - S * 0.230, belly_y + S * 0.180),
    ]
    triad_poly(surf, back, BONE_CORE, BONE_SHADE, BONE,
               sheen_pts=[(cx - S * 0.225, belly_y - S * 0.12),
                          (cx - S * 0.07,  belly_y - S * 0.13),
                          (cx - S * 0.11,  belly_y + S * 0.10),
                          (cx - S * 0.20,  belly_y + S * 0.09)])

    # Step 2: the bold DARK interior CAVITY -- a single deep ink pocket carved
    # into the belly. This negative-space hole IS the silhouette tell; it must
    # read as a black pocket at 32px, framed by the bone barrel around it. Built
    # as a rounded arch (wide top, tapered bottom) so it reads as an open cupboard
    # mouth, not a rib gap.
    cav_w = S * 0.190
    cav_top = belly_y - S * 0.118
    cav_bot = belly_y + S * 0.175
    cavity = [
        (cx - cav_w, cav_top + S * 0.020),
        (cx - cav_w * 0.78, cav_top - S * 0.012),
        (cx,            cav_top - S * 0.022),
        (cx + cav_w * 0.78, cav_top - S * 0.012),
        (cx + cav_w, cav_top + S * 0.020),
        (cx + cav_w * 0.86, cav_bot - S * 0.05),
        (cx + cav_w * 0.40, cav_bot),
        (cx - cav_w * 0.40, cav_bot),
        (cx - cav_w * 0.86, cav_bot - S * 0.05),
    ]
    # Ink rim then the near-black cavity fill -- deep, flat, no gradient.
    pygame.draw.polygon(surf, INK, cavity)
    inner = [(cx + (p[0] - cx) * 0.90, p[1] + (belly_y - p[1]) * 0.06)
             for p in cavity]
    pygame.draw.polygon(surf, CAVITY_EDGE, inner)
    inner2 = [(cx + (p[0] - cx) * 0.82, p[1] + (belly_y - p[1]) * 0.10)
              for p in cavity]
    pygame.draw.polygon(surf, CAVITY, inner2)
    # A short vertical spine tick at the very back of the dark pocket so the
    # bone read persists inside the hole without breaking the dark mass.
    for i in range(3):
        sy = cav_top + S * 0.04 + i * S * 0.075
        _ell(surf, BONE_SHADE, cx, sy, S * 0.018, S * 0.014)

    # Step 3: 3 HIGH-CONTRAST food lobes sitting PROUD of the dark pocket. Each
    # is a fat round blob with max value contrast against the cavity + its own
    # sheen dot, so it reads as "stuff inside the chest" at 1x, not texture.
    # 3 lobes MAX (brief drops the 4th garnish -- hold that line).
    # Lobe A: CREAM pan-dulce concha, upper-left -- the brightest lobe (max pop).
    pcx, pcy = cx - S * 0.085, belly_y - S * 0.020
    triad_ellipse(surf, pcx, pcy, S * 0.090, S * 0.085,
                  PAN_CREAM_D, PAN_CREAM, PAN_CREAM_S)
    for k in (-1, 1):   # concha shell cross-score (few + bold so it survives)
        pygame.draw.line(surf, PAN_CREAM_D,
                         (pcx - S * 0.055, pcy + k * S * 0.030),
                         (pcx + S * 0.055, pcy + k * S * 0.030), max(1, int(SS)))
        pygame.draw.line(surf, PAN_CREAM_D,
                         (pcx + k * S * 0.030, pcy - S * 0.055),
                         (pcx + k * S * 0.030, pcy + S * 0.055), max(1, int(SS)))
    # Lobe B: masa-GOLD round tamale, lower-centre -- the biggest, hero hue.
    tax, tay = cx + S * 0.055, belly_y + S * 0.085
    triad_ellipse(surf, tax, tay, S * 0.108, S * 0.098,
                  GOLD_CORE, MASA_GOLD, GOLD_SHEEN)
    for k in (-1, 0, 1):   # husk ties so it reads wrapped, bold + few
        pygame.draw.line(surf, GOLD_CORE,
                         (tax + k * S * 0.035, tay - S * 0.085),
                         (tax + k * S * 0.05, tay + S * 0.085),
                         max(1, int(SS * 1.1)))
    # Lobe C: the ONE chile-red lobe, upper-right -- the single interior red
    # accent (oranger, stays off Zapateada's pink-rose), with a cilantro stem.
    chx, chy = cx + S * 0.108, belly_y - S * 0.058
    chile_pod = [
        (chx - S * 0.020, chy - S * 0.060),
        (chx + S * 0.050, chy - S * 0.030),
        (chx + S * 0.066, chy + S * 0.040),
        (chx + S * 0.020, chy + S * 0.085),
        (chx - S * 0.030, chy + S * 0.045),
        (chx - S * 0.048, chy - S * 0.012),
    ]
    triad_poly(surf, chile_pod, CHILE_CORE, CHILE, CHILE_SHEEN)
    pygame.draw.line(surf, CILANTRO,
                     (chx - S * 0.020, chy - S * 0.060),
                     (chx - S * 0.036, chy - S * 0.095), max(1, int(SS)))

    # Step 4: only ~3 THICK ribs per side, swung OPEN like cupboard doors, drawn
    # IN FRONT of the food so they FRAME the lit cluster against the dark hole.
    # Few + fat (vs round-1's even thin banding) so each rib is a distinct door
    # slat, not a stripe. Hinged at the rim, fanning outward top->bottom.
    def door_rib(side, i, n):
        t = i / (n - 1)
        ry0 = belly_y - S * 0.085 + t * S * 0.205
        # Lower ribs reach wider -- doors flung open from the top hinge.
        reach = S * (0.135 + 0.115 * t)
        hinge_x = cx + side * cav_w * 0.96
        tip_x = cx + side * (cav_w + reach * 0.55)
        curve = S * 0.040 * (1.0 - abs(t - 0.5) * 1.1)
        thick = S * 0.046   # THICK door slat
        pts = [
            (hinge_x, ry0 - thick),
            (cx + side * (cav_w + reach * 0.3), ry0 - thick - curve),
            (tip_x, ry0 - thick * 0.35 - curve * 0.4),
            (tip_x, ry0 + thick * 0.7 - curve * 0.4),
            (cx + side * (cav_w + reach * 0.3), ry0 + thick - curve),
            (hinge_x, ry0 + thick),
        ]
        triad_poly(surf, pts, BONE_CORE, BONE, SHEEN)
        # Bright sheen lip along the TOP edge so curvature reads in flat banding.
        pygame.draw.line(surf, SHEEN,
                         (hinge_x, ry0 - thick * 0.5),
                         (cx + side * (cav_w + reach * 0.35),
                          ry0 - thick * 0.5 - curve),
                         max(1, int(SS * 1.0)))

    for side in (-1, 1):
        for i in range(3):
            door_rib(side, i, 3)
    # The cavity mouth keeps a crisp dark ink rim so the pocket edge stays bold
    # against the framing ribs at 32px.
    pygame.draw.polygon(surf, INK, cavity, max(2, int(SS * 1.4)))

    # ---- SKULL head (small, grinning, chile clenched cigar-style) ------------
    triad_ellipse(surf, cx, head_y, S * 0.128, S * 0.135,
                  BONE_CORE, BONE, SHEEN)
    triad_ellipse(surf, cx, head_y + S * 0.085, S * 0.095, S * 0.058,
                  BONE_CORE, BONE, SHEEN)
    # Eye sockets -- DotD style with a tiny ochre marigold petal ring.
    for ex in (cx - S * 0.05, cx + S * 0.05):
        triad_ellipse(surf, ex, head_y - S * 0.008, S * 0.032, S * 0.036,
                      (40, 28, 24), (56, 40, 32), (92, 68, 52), outline=None)
        for k in range(8):
            a = k * math.tau / 8
            px = ex + math.cos(a) * S * 0.042
            py = (head_y - S * 0.008) + math.sin(a) * S * 0.048
            pygame.draw.circle(surf, OCHRE_HAT, (int(px), int(py)),
                               max(1, int(SS * 1.0)))
        pygame.draw.circle(surf, INK, (int(ex), int(head_y - S * 0.008)),
                           int(S * 0.015))
    # Nose triangle.
    pygame.draw.polygon(surf, (40, 28, 24), [
        (cx, head_y + S * 0.02),
        (cx - S * 0.015, head_y + S * 0.05),
        (cx + S * 0.015, head_y + S * 0.05),
    ])
    # Big toothy grin (vendor cheer).
    sm_y = head_y + S * 0.078
    pygame.draw.arc(surf, INK,
                    (cx - S * 0.07, sm_y - S * 0.038, S * 0.14, S * 0.076),
                    math.pi * 1.05, math.pi * 1.95, max(1, int(SS * 1.6)))
    for k in range(-3, 4):
        tx = cx + k * S * 0.019
        pygame.draw.line(surf, INK, (tx, sm_y - S * 0.012),
                         (tx, sm_y + S * 0.013), max(1, int(SS)))
    # Chile clenched like a CIGAR in the corner of the jaw (gluttony tell, the
    # second small chile-red face accent). Green stem flicks up.
    cgx, cgy = cx + S * 0.075, sm_y + S * 0.004
    cigar = [
        (cgx, cgy - S * 0.014),
        (cgx + S * 0.10, cgy - S * 0.028),
        (cgx + S * 0.11, cgy - S * 0.006),
        (cgx + S * 0.01, cgy + S * 0.014),
    ]
    triad_poly(surf, cigar, CHILE_CORE, CHILE, CHILE_SHEEN)
    pygame.draw.line(surf, CILANTRO,
                     (cgx + S * 0.105, cgy - S * 0.017),
                     (cgx + S * 0.13, cgy - S * 0.04), max(1, int(SS * 0.9)))

    # ---- FLAT WIDE VENDOR HAT (distinct from Mariachi: low flat brim + notch) --
    # Pushed flatter and wider than the anchor's domed sombrero, so the gap-read
    # between the two skeletons isn't just the body -- the hat silhouette differs
    # too. Crown is a low truncated band (a vendor's straw hat), not a tall cone.
    _ell(surf, INK, cx, hat_y + S * 0.014, S * 0.300, S * 0.060)
    triad_ellipse(surf, cx, hat_y, S * 0.295, S * 0.054,
                  OCHRE_CORE, OCHRE_HAT, OCHRE_SHEEN)
    # Woven straw radial ticks so the wide brim reads as straw, not felt.
    for k in range(-6, 7):
        bx = cx + k * S * 0.042
        pygame.draw.line(surf, OCHRE_CORE,
                         (bx, hat_y - S * 0.016), (bx, hat_y + S * 0.016),
                         max(1, int(SS * 0.7)))
    # LOW flat-topped crown (a short straw band, distinctly un-domed).
    crown = [
        (cx - S * 0.085, hat_y - S * 0.006),
        (cx - S * 0.072, hat_y - S * 0.052),
        (cx - S * 0.050, hat_y - S * 0.064),
        (cx + S * 0.050, hat_y - S * 0.064),
        (cx + S * 0.072, hat_y - S * 0.052),
        (cx + S * 0.085, hat_y - S * 0.006),
    ]
    triad_poly(surf, crown, OCHRE_CORE, OCHRE_HAT, OCHRE_SHEEN,
               sheen_pts=[(cx - S * 0.072, hat_y - S * 0.010),
                          (cx - S * 0.052, hat_y - S * 0.056),
                          (cx - S * 0.020, hat_y - S * 0.060),
                          (cx - S * 0.040, hat_y - S * 0.010)])
    # Chile-red HATBAND with a distinct front NOTCH (a V-dip) -- a hat tell that
    # differs from the anchor's plain band, and the one designated hat red.
    pygame.draw.line(surf, CHILE,
                     (cx - S * 0.075, hat_y - S * 0.012),
                     (cx + S * 0.075, hat_y - S * 0.012), max(2, int(SS * 2.0)))
    pygame.draw.polygon(surf, CHILE, [
        (cx - S * 0.018, hat_y - S * 0.012),
        (cx + S * 0.018, hat_y - S * 0.012),
        (cx,             hat_y + S * 0.014),
    ])
    pygame.draw.line(surf, CHILE_SHEEN,
                     (cx - S * 0.075, hat_y - S * 0.018),
                     (cx + S * 0.03, hat_y - S * 0.018), max(1, int(SS * 0.7)))

    # ---- OFFERED-TAMALE HAND thrust forward (vendor read + asymmetry tell) ----
    sh_x, sh_y = cx + S * 0.235, belly_y - S * 0.050
    el_x, el_y = cx + S * 0.335, belly_y + S * 0.010
    hd_x, hd_y = cx + S * 0.395, belly_y + S * 0.075
    for a, b in (((sh_x, sh_y), (el_x, el_y)), ((el_x, el_y), (hd_x, hd_y))):
        pygame.draw.line(surf, INK, a, b, int(S * 0.05 + SS * 1.6))
        pygame.draw.line(surf, BONE_SHADE, a, b, int(S * 0.05))
        pygame.draw.line(surf, BONE, a, b, int(S * 0.025))
    triad_ellipse(surf, el_x, el_y, S * 0.034, S * 0.034, BONE_CORE, BONE, SHEEN)
    triad_ellipse(surf, sh_x, sh_y, S * 0.04, S * 0.04, BONE_CORE, BONE, SHEEN)
    # Offered tamale on the palm.
    triad_ellipse(surf, hd_x + S * 0.02, hd_y - S * 0.01,
                  S * 0.078, S * 0.068, GOLD_CORE, MASA_GOLD, GOLD_SHEEN)
    for k in (-1, 0, 1):
        pygame.draw.line(surf, GOLD_CORE,
                         (hd_x + S * 0.02 + k * S * 0.022, hd_y - S * 0.07),
                         (hd_x + S * 0.02 + k * S * 0.03, hd_y + S * 0.04),
                         max(1, int(SS * 0.9)))
    # A few bony fingers cupping the tamale underneath.
    for f in range(3):
        fx = hd_x - S * 0.02 + f * S * 0.026
        pygame.draw.line(surf, INK, (fx, hd_y + S * 0.02),
                         (fx + S * 0.01, hd_y + S * 0.06), max(1, int(SS)))
        pygame.draw.line(surf, BONE, (fx, hd_y + S * 0.02),
                         (fx + S * 0.01, hd_y + S * 0.06), max(1, int(SS * 0.5)))

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (target_size, target_size))


# -- the prop -> pillar mirror (market-pole ristra + comal cap) ---------------

def draw_pillar(width, height, top_cap=True):
    """Market-stall vendor pole: a wooden pole strung with a ristra of dried
    chiles = repeatable shaft (chile banding); a wide round comal griddle topped
    with a stacked-tamale dome = detachable gap-edge cap. Mirror is clean -- the
    comal sits on-axis and symmetric (the creature is the bottom-heavy one; the
    prop is balanced), so the cap never goes top-heavy. The comal disc is now
    pushed WIDER than the shaft (a clear flat-griddle silhouette breaking the
    shaft round) so the gap-edge cap reads as a separate element, not a bead."""
    W = width * SS
    H = height * SS
    cx = W * 0.5
    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # Wooden pole shaft (warm tan-bone wood lane, so it reads as a market post).
    pole_w = W * 0.26
    pole = pygame.Rect(int(cx - pole_w / 2), 0, int(pole_w), int(H))
    pygame.draw.rect(surf, BONE_CORE, pole)
    pygame.draw.rect(surf, BONE_SHADE, pole.inflate(-int(SS * 3), 0))
    pygame.draw.rect(surf, BONE,
                     (int(cx - pole_w / 2 + SS * 2), 0,
                      int(pole_w * 0.26), int(H)))

    # RISTRA of dried chiles strung down BOTH sides of the pole = repeatable
    # shaft banding. Chile-red here is the prop's signature produce, paired with
    # masa-gold corn ears so the gold-led palette still leads the prop too.
    band = max(1, int(height / 7))
    for i in range(band + 1):
        by = int(H * i / band)
        for side in (-1, 1):
            chx = cx + side * pole_w * 0.62
            chile = [
                (chx, by - SS * 5),
                (chx + side * SS * 5, by - SS * 1),
                (chx + side * SS * 6, by + SS * 5),
                (chx + side * SS * 2, by + SS * 9),
                (chx - side * SS * 1, by + SS * 4),
            ]
            triad_poly(surf, chile, CHILE_CORE, CHILE, CHILE_SHEEN)
        # Masa-gold corn ear hung centre between chile pairs (gold leads).
        if i % 2 == 0:
            triad_ellipse(surf, cx, by + SS * 4, SS * 3.4, SS * 6,
                          GOLD_CORE, MASA_GOLD, GOLD_SHEEN)

    # Gap-edge cap: a WIDE flat comal griddle (on-axis, symmetric) clearly wider
    # than the shaft, with a stacked-tamale dome breaking its round -- so the cap
    # silhouette is unmistakably a separate flat-disc element, not body banding.
    if top_cap:
        comal_r = pole_w * 1.45   # pushed wide -- the disc out-widths the shaft
        cyp = H - comal_r * 0.42 - W * 0.06
        # Dark iron comal disc -- a flat, very oblate plate (low ry) so it reads
        # as a griddle seen edge-on, distinct from the round shaft beads.
        triad_ellipse(surf, cx, cyp, comal_r, comal_r * 0.30,
                      (38, 30, 26), (66, 54, 46), (118, 102, 88))
        # A bright iron rim highlight along the disc top so the flat plate pops.
        pygame.draw.arc(surf, (150, 132, 112),
                        (int(cx - comal_r), int(cyp - comal_r * 0.30),
                         int(comal_r * 2), int(comal_r * 0.60)),
                        math.pi * 1.05, math.pi * 1.95, max(1, int(SS * 1.4)))
        # Stacked-tamale dome (masa-gold) sitting on the comal -- gold hero mass,
        # narrower than the disc so the disc clearly frames it.
        triad_ellipse(surf, cx, cyp - comal_r * 0.40,
                      comal_r * 0.56, comal_r * 0.52,
                      GOLD_CORE, MASA_GOLD, GOLD_SHEEN)
        triad_ellipse(surf, cx, cyp - comal_r * 0.78,
                      comal_r * 0.38, comal_r * 0.38,
                      GOLD_CORE, MASA_GOLD, GOLD_SHEEN)
        # Husk ties on the dome.
        for k in (-1, 0, 1):
            pygame.draw.line(surf, GOLD_CORE,
                             (cx + k * comal_r * 0.20, cyp - comal_r * 0.95),
                             (cx + k * comal_r * 0.26, cyp - comal_r * 0.10),
                             max(1, int(SS * 0.9)))
        # A single chile-red garnish on the dome top (accent, on-axis).
        triad_ellipse(surf, cx, cyp - comal_r * 1.02,
                      comal_r * 0.12, comal_r * 0.20,
                      CHILE_CORE, CHILE, CHILE_SHEEN)

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (width, height))


# -- pure-black silhouette read (accessibility / outline test) ----------------

def draw_silhouette(target_size):
    """Flatten the creature to a pure-black mask -- proves the lead read survives
    in outline alone: bottom-heavy pear + open-cupboard ribcage gap + offered
    tamale hand asymmetry."""
    rgba = draw_comelona(target_size)
    sil = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(rgba)
    surf = mask.to_surface(setcolor=(18, 16, 18, 255), unsetcolor=(0, 0, 0, 0))
    sil.blit(surf, (0, 0))
    return sil


# -- sheet composition --------------------------------------------------------

def _sky_panel(sheet, x, y, w, h, top, bot):
    for yy in range(h):
        t = yy / float(h)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(sheet, col, (x, y + yy), (x + w, y + yy))
    pygame.draw.rect(sheet, (24, 20, 26), (x, y, w, h), 2)


def build_sheet():
    W, H = 1000, 760
    sheet = pygame.Surface((W, H))
    sheet.fill((46, 40, 50))   # warm-dark neutral review backdrop

    font = pygame.font.SysFont("arial", 18, bold=True)
    small = pygame.font.SysFont("arial", 13)

    def label(txt, x, y, col=(245, 238, 226)):
        sheet.blit(font.render(txt, True, col), (x, y))

    def caption(txt, x, y, col=(208, 200, 210)):
        sheet.blit(small.render(txt, True, col), (x, y))

    label("CALACA COMELONA — gluttonous Day-of-the-Dead street-food vendor  ·  round 2",
          18, 12, (250, 214, 130))
    caption("LEAD: EXPOSED ANATOMY — re-engineered as a DARK belly CAVITY + 3 lobes "
            "PROUD of the pocket · gold-led, chile-red accent only", 18, 36)

    # Large creature.
    big = draw_comelona(300)
    sheet.blit(big, (24, 60))
    caption("creature · large (300px)", 24, 362)

    # Mid-scale legibility ramp.
    mid = draw_comelona(150)
    sheet.blit(mid, (350, 60))
    caption("creature · 150px", 350, 214)

    # 32px creature + 4x zoom on the neutral mat.
    tiny = draw_comelona(32)
    sheet.blit(tiny, (350, 244))
    caption("32px", 350, 280)
    zoom = pygame.transform.scale(tiny, (128, 128))
    sheet.blit(zoom, (392, 244))
    caption("32px @4x (mat)", 392, 376)

    # Pure-black silhouette read.
    sil_big = draw_silhouette(150)
    sheet.blit(sil_big, (24, 408))
    caption("silhouette · 150px", 24, 560)
    sil_tiny = draw_silhouette(32)
    sil_zoom = pygame.transform.scale(sil_tiny, (128, 128))
    sheet.blit(sil_zoom, (188, 408))
    caption("silhouette 32px @4x", 188, 540)
    caption("read: bottom-heavy, open belly hole", 188, 556)

    # TRUE 32px chip on BOTH a day-ochre AND a night sky (AD: prove the
    # dark-cavity-plus-3-lobes read holds on both biome backdrops).
    day_x = 350
    _sky_panel(sheet, day_x, 408, 128, 128, (236, 196, 120), (210, 158, 92))
    sheet.blit(pygame.transform.scale(draw_comelona(32), (128, 128)), (day_x, 408))
    caption("32px @4x · ochre DAY sky", day_x, 540)

    night_x = 492
    _sky_panel(sheet, night_x, 408, 128, 128, (28, 30, 64), (52, 40, 78))
    sheet.blit(pygame.transform.scale(draw_comelona(32), (128, 128)), (night_x, 408))
    caption("32px @4x · NIGHT sky", night_x, 540)
    caption("dark cavity + 3 lobes hold on both", day_x, 556)

    # Prop -> pillar mirror (market-pole ristra + comal cap).
    px = 660
    py = 60
    cap_h = 100
    shaft_h = 150
    big_w = 64
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
    caption("market pole + ristra · WIDE comal cap", px - 4,
            py + shaft_h * 2 + cap_h * 2 + gap + 22)

    # 32px pillar cap (judge the gap-edge read small).
    tcap = draw_pillar(30, 46, top_cap=True)
    sheet.blit(tcap, (px + 150, py + 20))
    czoom = pygame.transform.scale(tcap, (120, 184))
    sheet.blit(czoom, (px + 196, py + 20))
    caption("cap 30px / @4x", px + 150, py + 212)
    caption("comal disc out-widths shaft", px + 150, py + 228)

    # Palette swatch strip.
    sw_y = H - 52
    swatches = [
        ("masa-gold", MASA_GOLD), ("ochre-hat", OCHRE_HAT), ("bone", BONE),
        ("tan-bone", BONE_SHADE), ("chile-red", CHILE), ("cilantro", CILANTRO),
        ("ink", INK), ("sheen", SHEEN),
    ]
    for i, (nm, col) in enumerate(swatches):
        sx = 430 + i * 70
        pygame.draw.rect(sheet, col, (sx, sw_y, 58, 28))
        pygame.draw.rect(sheet, (20, 18, 22), (sx, sw_y, 58, 28), 2)
        caption(nm, sx + 1, sw_y + 30)

    return sheet


if __name__ == "__main__":
    out = build_sheet()
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(out, dst)
    print("wrote", dst)
