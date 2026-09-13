"""
Round-1 concept renderer for ASTHI-SAMRAT — the temple-pylon colossus
(Mukha-Devi brood, concept #5). Headless Pygame; ELEVATED pipeline
(supersample SS=5 -> smoothscale) so the rigid arm-GRID + the 12 skull-pole
finials stay crisp at downscale. Keeps the shipped house grammar: flat fills,
hard 1-2px ink keyline (28,22,26), dark-core -> flat-fill -> top-left rim-sheen
triad, 1px alpha-grown outline, chibi-scary-CUTE face; procedural-only.

WHY this is the rigid-architectural-arm-GRID KIND (and the MONUMENTAL + PURE-
bone poles of the brood): twelve arms are stacked in THREE tiers of FOUR, each
tier strictly SHORTER than the one below, so the blackout silhouette is a
STEPPED vertical monolith with hard horizontal cornice-lines — a temple-pylon,
not a radial fan (Mukha), not a tapering armless stupa (Stupika). The base is
the heaviest in the brood and the whole figure is bottom-rooted like a gate
column. Square/austere cornices, never curved ornate eaves.

WHY pure BONE, no thematic glow: this is the PURE pole of the theme axis. The
austerity IS the accent. The ONLY non-bone notes allowed are the ink keyline
and a COLD socket-pin (steel-grey iris + faint cold-white socket glow at the
gap). There is deliberately no coloured hue anywhere — resisting it is the
whole identity. The deep cold socket-glow is the single focal.

WHY the arm-end-skull DNA survives as skull-poles: each of the twelve hands
grips a vertical bone-banner STANDARD topped with a tiny-skull FINIAL — a
colonnade of skull-poles. That carries Mukha's "tiny skulls among the arm-end
ornaments" without needing a thematic accent.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief — the PURE bone pole) ────────────────────────
# Bone is the ONLY mass colour. Everything else is the ink keyline plus a COLD
# steel-grey / cold-white socket-pin. NO thematic hue anywhere — austerity is
# the accent. Bone is kept a touch COOL/neutral (not Mukha's warm rose-bone and
# not Leyak ash-white) so this pole reads "carved stone temple", not "flesh".
BONE      = (214, 206, 190)   # cool ivory-bone — the dominant carved-stone mass
BONE_D    = (158, 150, 134)   # bone dark-core / shade
BONE_DD   = (104,  98,  86)   # deepest bone hollow (cornice grooves, sockets)
BONE_DDD  = ( 66,  62,  56)   # hardest groove shadow (the must-survive steps)
BONE_SH   = (244, 240, 228)   # bone top-left rim-sheen

STEEL     = (150, 162, 176)   # COLD steel-grey socket-pin (the only non-bone note)
STEEL_BR  = (210, 224, 236)   # cold-white socket glow inner
STEEL_D   = ( 78,  92, 108)   # cold socket shade
INK       = ( 28,  22,  26)   # hard ink keyline

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


def hard_groove(surf, x0, x1, y, s, depth=2.4):
    """A hard horizontal cornice groove — the MUST-SURVIVE read at 32px. Two
    stacked dark lines (deepest shadow under a softer shade) so the tier
    separation reads as a STEP, not a slab seam, even after downscale."""
    pygame.draw.line(surf, BONE_DDD, (x0, y), (x1, y), max(2, int(depth * s)))
    pygame.draw.line(surf, BONE_DD, (x0, y - max(1, int(1.4 * s))),
                     (x1, y - max(1, int(1.4 * s))), max(1, int(1.2 * s)))


def cornice_lip(surf, cx, hw, y, s, overhang):
    """An OVERHANGING cornice lip that JUTS PAST the tier wall it crowns, so the
    blackout OUTLINE notches OUT-then-IN at every tier boundary — a true ziggurat
    edge, not a smooth taper. The lip is a flat bone shelf whose half-width is
    hw+overhang (it sticks out `overhang` px beyond the `hw` wall below it); under
    its underside runs the single DARKEST ink groove (the undercut notch that the
    silhouette reads as a hard step and that survives at 32px), and across its
    top-face a 1px COLD-WHITE sheen (the light-over-dark partner that keeps the
    separation alive on the dark night biome). Returns the lip half-width so the
    caller can chain the wider tier below it flush under the overhang."""
    lip_hw = hw + overhang
    lip_h = max(2, int(4 * s))
    # the jutting shelf (bone), keylined so its overhanging edge is crisp downscaled
    pygame.draw.rect(surf, INK, (cx - lip_hw, y - lip_h, lip_hw * 2, lip_h + max(1, int(s))))
    pygame.draw.rect(surf, BONE, (cx - lip_hw, y - lip_h, lip_hw * 2, lip_h))
    # cold-white sheen on the lip top-face (light-over-dark survivor at 32px night)
    pygame.draw.line(surf, STEEL_BR, (cx - lip_hw, y - lip_h),
                     (cx + lip_hw, y - lip_h), max(1, int(1.4 * s)))
    # the dark UNDERCUT groove beneath the overhang — the notch in the blackout
    pygame.draw.line(surf, BONE_DDD, (cx - lip_hw, y), (cx + lip_hw, y), max(2, int(3 * s)))
    return lip_hw


def arm_bracket(surf, sx, sy, hx, hy, s, side):
    """A visible bone ARM that reads as shoulder -> elbow -> hand: a short upper-arm
    stub jutting OUT from the central monolith, a HARD RIGHT-ANGLE elbow joint, then
    the forearm rising VERTICALLY into the hand that grips a banner-pole at (hx,hy).
    WHY a rigid 2-segment L-bracket (never a curve): the right angle is the whole
    point — it flips the read from "colonnade of posts on a slab" to "twelve ARMS
    holding skull-standards", and the squared joint reinforces the architectural,
    temple-pylon thesis (cf. Mukha's smooth radial limbs). `side` = -1 left, +1 right.

    sx,sy = shoulder root on the monolith;  hx,hy = the gripping hand."""
    upper_w = max(3, int(6.5 * s))      # upper-arm stub thickness
    fore_w = max(3, int(5.5 * s))       # forearm thickness
    elbow_x = hx                        # elbow sits directly under the hand
    elbow_y = sy                        # ... at shoulder height -> hard right angle

    # --- upper-arm stub: horizontal, shoulder -> elbow (the OUT segment) --------
    ua = [(sx, sy - upper_w), (elbow_x, elbow_y - upper_w),
          (elbow_x, elbow_y + upper_w), (sx, sy + upper_w)]
    triad_blob(surf, BONE, ua,
               core_pts=[(sx, sy), (elbow_x, elbow_y),
                         (elbow_x, elbow_y + upper_w), (sx, sy + upper_w)],
               ow=max(1, int(1.2 * s)))
    # --- the forearm: vertical, elbow -> hand (the UP segment) ------------------
    fa = [(elbow_x - fore_w, elbow_y + upper_w), (elbow_x + fore_w, elbow_y + upper_w),
          (elbow_x + fore_w, hy), (elbow_x - fore_w, hy)]
    triad_blob(surf, BONE, fa,
               core_pts=[(elbow_x, elbow_y), (elbow_x + fore_w, elbow_y),
                         (elbow_x + fore_w, hy), (elbow_x, hy)],
               sheen_pts=[(elbow_x - fore_w, elbow_y + upper_w),
                          (elbow_x - int(fore_w * 0.4), elbow_y + upper_w),
                          (elbow_x - int(fore_w * 0.4), hy),
                          (elbow_x - fore_w, hy)],
               ow=max(1, int(1.2 * s)))
    # --- the squared ELBOW knuckle (a hard joint block at the right angle) ------
    eb = max(3, int(7 * s))
    triad_blob(surf, BONE, [(elbow_x - eb, elbow_y - eb), (elbow_x + eb, elbow_y - eb),
                            (elbow_x + eb, elbow_y + eb), (elbow_x - eb, elbow_y + eb)],
               core_pts=[(elbow_x, elbow_y), (elbow_x + eb, elbow_y),
                         (elbow_x + eb, elbow_y + eb), (elbow_x, elbow_y + eb)],
               ow=max(1, int(1.2 * s)))
    # a dark ink dot in the elbow = the joint socket (reads as a knuckle, not a box)
    pygame.draw.circle(surf, BONE_DDD, (elbow_x, elbow_y), max(1, int(eb * 0.4)))
    # --- the HAND gripping the pole: a small bone cuff with finger nicks --------
    hand_hw = max(3, int(7 * s))
    hand_h = max(3, int(7 * s))
    triad_blob(surf, BONE, [(hx - hand_hw, hy - hand_h), (hx + hand_hw, hy - hand_h),
                            (hx + hand_hw, hy + int(hand_h * 0.4)),
                            (hx - hand_hw, hy + int(hand_h * 0.4))],
               ow=max(1, int(1.2 * s)))
    # finger nicks wrapping the pole (two dark verticals reading as a grip)
    for fk in (-0.45, 0.45):
        fxn = hx + int(hand_hw * fk)
        pygame.draw.line(surf, BONE_DDD, (fxn, hy - hand_h + int(s)),
                         (fxn, hy + int(hand_h * 0.3)), max(1, int(1.4 * s)))


# ── a single tiny skull-pole finial (the arm-end-skull DNA, pure bone) ────────
def skull_finial(surf, cx, cy, r, s):
    """Tiny bone skull crowning a banner-standard pole. WHY a domed cranium with
    two COLD steel pinpricks: the arm-end ornament must read as a skull at the
    pole tips without any thematic colour — the only non-bone note is the cold
    socket-pin, consistent with the pure-bone theme."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.2 * s)), core=False)
    jaw = [(cx - int(r * 0.46), cy + int(r * 0.5)),
           (cx + int(r * 0.46), cy + int(r * 0.5)),
           (cx + int(r * 0.3), cy + int(r * 0.92)),
           (cx - int(r * 0.3), cy + int(r * 0.92))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.0 * s)))
    for ex in (cx - int(r * 0.36), cx + int(r * 0.36)):
        pygame.draw.circle(surf, INK, (ex, cy), max(1, int(r * 0.24)))
        pygame.draw.circle(surf, STEEL, (ex, cy), max(1, int(r * 0.12)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.4)), max(1, int(r * 0.12)))


def banner_standard(surf, hx, hy, pole_h, pole_w, s, finial_r):
    """A vertical bone-banner standard gripped in one hand: a square austere
    pole topped by a tiny-skull finial. WHY strictly VERTICAL and square-edged:
    twelve of these in three tiers form the colonnade of skull-poles, and the
    verticals + the cornice grooves between tiers are what make the blackout
    read as a stepped temple-pylon rather than a noisy candelabra."""
    # the pole shaft (square, austere — never curved)
    pole = [(hx - pole_w, hy - pole_h),
            (hx + pole_w, hy - pole_h),
            (hx + pole_w, hy),
            (hx - pole_w, hy)]
    triad_blob(surf, BONE, pole,
               core_pts=[(hx, hy - pole_h), (hx + pole_w, hy - pole_h),
                         (hx + pole_w, hy), (hx, hy)],
               sheen_pts=[(hx - pole_w, hy - pole_h),
                          (hx - int(pole_w * 0.3), hy - pole_h),
                          (hx - int(pole_w * 0.3), hy),
                          (hx - pole_w, hy)],
               ow=max(1, int(1.0 * s)))
    # the skull-pole FINIAL on top
    skull_finial(surf, hx, hy - pole_h - finial_r, finial_r, s)


# ── the rigid three-tier arm-GRID (the KIND tell) ─────────────────────────────
def draw_arm_grid(surf, cx, top_y, s, body_w):
    """Twelve ARMS in THREE stacked tiers of FOUR, built as a true ZIGGURAT so the
    three steps live in the SILHOUETTE itself (round-2 had them only as interior
    grooves — invisible in the blackout). Each tier is a SOLID bone WALL whose
    half-width drops in two hard stages going UP: bottom 100% -> mid 78% -> top 58%
    of body_w. At the TOP of each wider lower tier an OVERHANGING cornice lip juts
    `overhang` px PAST the narrower wall above it, so the outline notches OUT (the
    jutting lip) then IN (the setback up to the wall above) — a stepped ziggurat
    edge, NOT a continuous taper. WHY solid walls, not a slim spine: round-2's slim
    spine let the cornice courses sit at the same outer extent on every tier, so the
    blackout read as one post; making the WALL itself carry the tier-width mass is
    what puts the three different widths into the outline.

    The FOUR L-bracket arms of each tier root on the wall and grip skull-standards
    but stay strictly INSIDE the wall half-width, so the arms never fill the notches
    — the cornice lips own the silhouette edge. Returns (hands, bottom_wall_hw,
    bottom_y) so the base plinth can chain flush under the widest tier."""
    hands = []
    # widest tier at the BOTTOM; the two hard width drops the blackout must show.
    tier_hw = [int(body_w * 1.00), int(body_w * 0.78), int(body_w * 0.58)]
    tier_h = int(50 * s)              # full height of each tier (wall + its cornice)
    cornice_h = int(12 * s)           # the crowning cornice course at each tier TOP
    overhang = max(3, int(12 * s))    # how far the cornice lip juts PAST the wall above
    pole_h = int(16 * s)              # banner-pole height above the gripping hand
    finial_r = int(5.0 * s)

    y = top_y
    for ti in range(3):               # ti 0 = TOP (narrowest), 2 = BOTTOM (widest)
        hw = tier_hw[2 - ti]          # invert: draw top-down, width grows downward
        wall_top = y
        wall_bot = y + tier_h
        cornice_top = wall_top
        cornice_bot = wall_top + cornice_h   # the cornice crowns this tier's TOP

        # --- the OVERHANGING cornice lip at this tier's TOP (the notch maker) ----
        # On every tier below the top one, the lip juts PAST the narrower wall above,
        # so the silhouette jumps OUT here then steps IN up to that wall. The lip
        # half-width is THIS tier's wall + overhang; its undercut groove + cold sheen
        # are the 32px-survivor light-over-dark pair (see cornice_lip).
        if ti > 0:
            cornice_lip(surf, cx, hw, cornice_top, s, overhang)

        # --- the SOLID tier WALL (its half-width IS the tier width -> the step) --
        # face fill a touch LIGHTER than the cornice/grooves so the horizontal
        # step-lines beat the vertical poles (round-2 de-clutter note).
        wall_face = lerp(BONE, BONE_SH, 0.22)
        wall = [(cx - hw, cornice_bot), (cx + hw, cornice_bot),
                (cx + hw, wall_bot), (cx - hw, wall_bot)]
        triad_blob(surf, wall_face, wall,
                   core_pts=[(cx, cornice_bot), (cx + hw, cornice_bot),
                             (cx + hw, wall_bot), (cx, wall_bot)],
                   sheen_pts=[(cx - hw, cornice_bot), (cx - int(hw * 0.30), cornice_bot),
                              (cx - int(hw * 0.30), wall_bot), (cx - hw, wall_bot)],
                   ow=max(1, int(1.6 * s)))
        # the DARK under-cornice groove on the wall just below the lip — the interior
        # partner that keeps the tier line crisp where the lip overhang meets wall.
        pygame.draw.line(surf, BONE_DDD, (cx - hw, cornice_bot + max(1, int(s))),
                         (cx + hw, cornice_bot + max(1, int(s))), max(2, int(2.2 * s)))

        # --- FOUR L-bracket arms reach out of this tier, two per side -----------
        # hands sit well INSIDE hw so the cornice lip stays the widest mass at the
        # boundary and the arms never bleed into / fill the silhouette notches.
        sh_top = wall_bot - int(tier_h * 0.46)
        sh_bot = wall_bot - int(tier_h * 0.22)
        spine_root = int(hw * 0.20)               # arms root near the wall centre
        hand_offsets = [hw * 0.40, hw * 0.70]     # both inside the wall edge
        pole_xs = []
        for side in (-1, 1):
            for hi, hox in enumerate(hand_offsets):
                hx = int(cx + side * hox)
                sy = sh_top if hi == 0 else sh_bot      # stagger shoulders vertically
                sx = cx + side * spine_root
                hand_y = wall_bot - int(tier_h * 0.34)
                arm_bracket(surf, sx, sy, hx, hand_y, s, side)
                pole_xs.append((hx, hand_y))
        # --- the banner-standards the hands grip (drawn over the arms) ----------
        pole_w = int(3.4 * s)
        for (hx, hand_y) in pole_xs:
            banner_standard(surf, hx, hand_y, pole_h, pole_w, s, finial_r)
            hands.append((hx, hand_y - pole_h))
        # --- recover the lowest tier's 4-arm gaps (round-2 minor note) ----------
        # the widest bottom tier let its four poles merge into the dark mass above
        # the plinth; cut a 1-2px cold negative gap between adjacent poles so the
        # bottom tier still reads as FOUR discrete arms, like the tiers above.
        if ti == 2:
            ordered = sorted(px for (px, _) in pole_xs)
            for a, b in zip(ordered, ordered[1:]):
                mid = (a + b) // 2
                pygame.draw.line(surf, BONE_DDD, (mid, wall_bot - int(tier_h * 0.30)),
                                 (mid, wall_bot - max(1, int(2 * s))), max(2, int(2 * s)))
        y = wall_bot
    # the THIRD jutting lip: crown the widest bottom tier just above the plinth, so
    # the blackout shows three overhanging cornices between crown and plinth (the
    # mid + bottom tier TOPS gave two; this gives the body->plinth step its lip too).
    cornice_lip(surf, cx, tier_hw[0], y, s, overhang)
    return hands, tier_hw[0], y + max(2, int(4 * s))  # bottom wall hw + plinth start


# ── the temple-pylon colossus ─────────────────────────────────────────────────
def draw_asthi_samrat(surf, cx, cy, s):
    """Towering pure-bone colossus: a chibi-scary skull face crowned by a square
    skull-tiara, atop a rigid three-tier twelve-arm cornice grid, rooted on the
    heaviest base in the brood. `s` = unit scale around a ~150-unit-tall figure.

    WHY the head sits ON TOP of the grid (not framed inside it): this is the
    architectural KIND — the face is the pylon's keystone/capital, the grid is
    the body of the gate, the base is the plinth. Vertical stacking IS the
    monumental silhouette."""

    head_c = (cx, cy - int(52 * s))
    hr = int(26 * s)
    body_w = int(30 * s)

    # === THREE-TIER ARM GRID (the body of the pylon) ==========================
    # drawn first so the head + base overlap its top/bottom edges cleanly.
    grid_top = head_c[1] + int(hr * 0.6)
    hands, base_hw, grid_bot = draw_arm_grid(surf, cx, grid_top, s, body_w)

    # === HEAVIEST BASE in the brood — a square stepped plinth (bottom-rooted) ==
    # WHY a wide stepped plinth, widest at the very bottom: it roots the colossus
    # like a temple-gate footing and gives the silhouette its heaviest, most
    # ground-planted mass — the monumental pole of the proportion axis. Its first
    # step starts at the bottom-tier lip width so the plinth continues the ziggurat
    # outward (never narrower than the body it carries -> no waist under the lip).
    base_top = grid_bot - int(2 * s)
    steps = [(int(body_w * 1.34), int(12 * s)),
             (int(body_w * 1.56), int(13 * s)),
             (int(body_w * 1.82), int(15 * s))]
    by = base_top
    for hw, h in steps:
        block = [(cx - hw, by), (cx + hw, by),
                 (cx + hw, by + h), (cx - hw, by + h)]
        triad_blob(surf, BONE, block,
                   core_pts=[(cx, by), (cx + hw, by),
                             (cx + hw, by + h), (cx, by + h)],
                   sheen_pts=[(cx - hw, by), (cx - int(hw * 0.3), by),
                              (cx - int(hw * 0.3), by + int(h * 0.5)),
                              (cx - hw, by + int(h * 0.5))],
                   ow=max(1, int(1.8 * s)))
        hard_groove(surf, cx - hw, cx + hw, by + h - max(1, int(2 * s)), s)
        by += h
    # austere vertical fluting on the widest plinth step (carved-stone read)
    for k in range(-3, 4):
        fx = cx + int(k * body_w * 0.46)
        pygame.draw.line(surf, BONE_DD, (fx, base_top + int(6 * s)),
                         (fx, by - int(4 * s)), max(1, int(1.4 * s)))

    # === SKULL HEAD — chibi, scary-cute, the pylon's capital/keystone =========
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # the two big eye sockets — the COLD socket-glow is the single focal of the
    # whole sprite (the only non-bone note carrying any "light"). Dark hollow +
    # steel iris + a faint cold-white pin so the face reads "looking at you"
    # without any thematic hue.
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.40)
        ey = head_c[1] + int(hr * 0.04)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.32))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.27))
        pygame.draw.circle(surf, STEEL_D, (ex, ey), int(hr * 0.18))
        pygame.draw.circle(surf, STEEL, (ex - int(1 * s), ey - int(1 * s)), int(hr * 0.12))
        pygame.draw.circle(surf, STEEL_BR, (ex - int(2 * s), ey - int(2 * s)),
                           max(1, int(hr * 0.06)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.13), head_c[1] + int(hr * 0.34)),
                         (head_c[0] + int(hr * 0.13), head_c[1] + int(hr * 0.34)),
                         (head_c[0], head_c[1] + int(hr * 0.58))])
    # grinning tooth row (cute, not gory)
    my = head_c[1] + int(hr * 0.74)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.46), my),
                     (head_c[0] + int(hr * 0.46), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.14), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.14), my + int(hr * 0.12)), max(1, int(1 * s)))

    # === SQUARE SKULL-TIARA (Mukha DNA, made architectural/austere) ===========
    # WHY a flat SQUARE crenellated band rather than a curved arc: it keeps the
    # tiara reading as part of the temple-pylon language (square cornices), and
    # carries the skull-crown DNA with three tiny skull merlons across a hard
    # horizontal lintel above the brow.
    lintel_w = int(hr * 1.05)
    lintel_y = head_c[1] - int(hr * 0.78)
    pygame.draw.rect(surf, INK, (head_c[0] - lintel_w, lintel_y - int(3 * s),
                                 lintel_w * 2, int(7 * s)))
    pygame.draw.rect(surf, BONE, (head_c[0] - lintel_w, lintel_y - int(3 * s) + max(1, int(s)),
                                  lintel_w * 2, int(4 * s)))
    pygame.draw.line(surf, BONE_DD, (head_c[0] - lintel_w, lintel_y + int(3 * s)),
                     (head_c[0] + lintel_w, lintel_y + int(3 * s)), max(1, int(1.2 * s)))
    # three tiny skull merlons across the lintel (the crown skulls)
    ts_r = int(hr * 0.26)
    for k in (-1, 0, 1):
        sx = head_c[0] + int(k * lintel_w * 0.66)
        sy = lintel_y - ts_r - int(1 * s)
        skull_finial(surf, sx, sy, ts_r, s)


# ── the pylon-gate column → pillar mirror ─────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The pylon-gate column IS the pillar: a heavy banded bone shaft with hard
    SQUARE cornice grooves (the same stepped-temple language) and the heaviest
    footing at the rooted end; the GAP end caps with a recessed niche holding a
    single COLD socket-glow — the creature's own pure-bone focal, on-axis and
    austere (never a second face, never a coloured burst).

    `cap` names the END that faces the GAP."""
    shaft_hw = int(15 * s)
    # central austere ink seam the courses thread onto
    pygame.draw.rect(surf, INK, (cx - int(2 * s), top, int(4 * s), bot - top))

    # === heavy banded stone shaft (square cornice courses = the tile) =========
    course_pitch = int(20 * s)
    cap_room = int(38 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
        foot_y = bot              # heaviest footing roots at the bottom
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
        foot_y = top
    y = b0
    while y <= b1:
        block = [(cx - shaft_hw, y - int(9 * s)),
                 (cx + shaft_hw, y - int(9 * s)),
                 (cx + shaft_hw, y + int(9 * s)),
                 (cx - shaft_hw, y + int(9 * s))]
        triad_blob(surf, BONE, block,
                   core_pts=[(cx, y - int(8 * s)), (cx + shaft_hw, y - int(8 * s)),
                             (cx + shaft_hw, y + int(8 * s)), (cx, y + int(8 * s))],
                   sheen_pts=[(cx - shaft_hw, y - int(8 * s)),
                              (cx - int(shaft_hw * 0.32), y - int(8 * s)),
                              (cx - int(shaft_hw * 0.32), y + int(2 * s)),
                              (cx - shaft_hw, y + int(2 * s))],
                   ow=max(1, int(1.4 * s)))
        # the hard square cornice groove between courses (the stepped read)
        hard_groove(surf, cx - shaft_hw, cx + shaft_hw, y + int(9 * s), s)
        # a thin vertical flute pair so the shaft reads carved-stone, not pipe
        for fx in (cx - int(shaft_hw * 0.5), cx + int(shaft_hw * 0.5)):
            pygame.draw.line(surf, BONE_DD, (fx, y - int(8 * s)), (fx, y + int(7 * s)),
                             max(1, int(1.2 * s)))
        y += course_pitch

    # === heaviest FOOTING at the rooted end (bottom-rooted plinth) ============
    fdir = -1 if cap == "bottom" else 1   # footing grows AWAY from the gap
    foot_steps = [(int(shaft_hw * 1.4), int(11 * s)),
                  (int(shaft_hw * 1.7), int(12 * s))]
    fy = foot_y
    for hw, h in foot_steps:
        if fdir < 0:
            blk = [(cx - hw, fy - h), (cx + hw, fy - h),
                   (cx + hw, fy), (cx - hw, fy)]
            gy = fy - h
        else:
            blk = [(cx - hw, fy), (cx + hw, fy),
                   (cx + hw, fy + h), (cx - hw, fy + h)]
            gy = fy + h
        triad_blob(surf, BONE, blk,
                   sheen_pts=[(cx - hw, gy), (cx - int(hw * 0.3), gy),
                              (cx - int(hw * 0.3), gy + int(h * 0.5) * (1 if fdir > 0 else 1)),
                              (cx - hw, gy + int(h * 0.5))] if fdir > 0 else None,
                   ow=max(1, int(1.6 * s)))
        hard_groove(surf, cx - hw, cx + hw,
                    (fy - max(1, int(2 * s))) if fdir < 0 else (fy + h - max(1, int(2 * s))), s)
        fy += fdir * h

    # === gap-edge cap: recessed niche with a single COLD socket-glow ==========
    # WHY a recessed square niche + cold socket-glow: it mirrors the creature's
    # one focal (the cold eye-socket) at the gap, on-axis and austere. No hue,
    # no radial burst — the pure-bone identity holds even at the gap.
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    niche_w = int(13 * s)
    niche_h = int(20 * s)
    # a square lintel head over the niche (austere cornice cap)
    lin_hw = int(20 * s)
    lin_y = cap_y - (niche_h // 2 + int(8 * s)) * (1 if cap == "bottom" else 1)
    if cap == "bottom":
        lin_y = cap_y - niche_h // 2 - int(8 * s)
    else:
        lin_y = cap_y + niche_h // 2 + int(8 * s)
    block = [(cx - lin_hw, lin_y - int(7 * s)), (cx + lin_hw, lin_y - int(7 * s)),
             (cx + lin_hw, lin_y + int(7 * s)), (cx - lin_hw, lin_y + int(7 * s))]
    triad_blob(surf, BONE, block, ow=max(1, int(1.6 * s)))
    hard_groove(surf, cx - lin_hw, cx + lin_hw, lin_y + int(7 * s), s)
    # the recessed niche (dark) holding the cold socket-glow
    pygame.draw.rect(surf, INK,
                     (cx - niche_w, cap_y - niche_h // 2, niche_w * 2, niche_h))
    pygame.draw.rect(surf, BONE_DDD,
                     (cx - niche_w + max(1, int(s)), cap_y - niche_h // 2 + max(1, int(s)),
                      niche_w * 2 - max(2, int(2 * s)), niche_h - max(2, int(2 * s))))
    pygame.draw.circle(surf, STEEL_D, (cx, cap_y), int(7 * s))
    pygame.draw.circle(surf, STEEL, (cx, cap_y), int(4.5 * s))
    pygame.draw.circle(surf, STEEL_BR, (cx - int(1 * s), cap_y - int(1 * s)), max(1, int(2.4 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 5


def grow(surf, px=1):
    return grow_outline(surf, INK + (255,), px)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def main():
    W, H = 1010, 820
    FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "..", "..", "..", "game", "assets",
                        "LiberationSans-Bold.ttf")
    FONT = os.path.normpath(FONT)
    font_big = pygame.font.Font(FONT, 28)
    font = pygame.font.Font(FONT, 16)
    font_sm = pygame.font.Font(FONT, 11)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("ASTHI-SAMRAT", True, LABEL), (24, 14))
    sheet.blit(font_sm.render(
        "temple-pylon colossus  ·  KIND: rigid arm-GRID (3 tiers x 4 arms) · MONUMENTAL + PURE-bone poles · "
        "cold socket-pin ONLY · round 3",
        True, LABEL_DIM), (300, 30))

    # === (1) EPIC HERO ========================================================
    big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
    draw_asthi_samrat(big, 180 * SS, 225 * SS, 1.32 * SS)
    hero = grow(pygame.transform.smoothscale(big, (360, 470)))
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature - EPIC hero", True, LABEL), (100, 566))
    sheet.blit(font_sm.render("12 ARMS: each a shoulder->RIGHT-ANGLE elbow->hand bone L-bracket gripping a skull-standard.", True, LABEL_DIM), (14, 588))
    sheet.blit(font_sm.render("3 tiers x 4 arms; tier width 100%->78%->58% w/ OVERHANGING cornice lips = stepped pylon.", True, LABEL_DIM), (14, 604))
    sheet.blit(font_sm.render("PURE bone; ONLY non-bone = ink keyline + COLD steel socket-pin (no thematic hue).", True, LABEL_DIM), (14, 620))

    # === (2) PILLAR assembled — mirrored, bottom-rooted =======================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow(pygame.transform.smoothscale(top_big, (150, 250)))
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow(pygame.transform.smoothscale(bot_big, (150, 250)))
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (60, 58, 70), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar - pylon-gate column", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("heavy stone shaft, hard SQUARE cornice grooves =", True, LABEL_DIM), (pcx - 4, 712))
    sheet.blit(font_sm.render("the tile; heaviest footing at the rooted end;", True, LABEL_DIM), (pcx - 4, 727))
    sheet.blit(font_sm.render("recessed niche + cold socket-glow caps the gap", True, LABEL_DIM), (pcx - 4, 742))

    # === (3) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 472))
    sheet.blit(font.render("True 32px gameplay chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        # the colossus is ~104 units WIDE; a true gameplay chip sizes it to a 32px
        # FOOTPRINT WIDTH (its on-screen pillar-creature width), ~76px tall — the
        # tall monument honestly occupies more vertical than a square 32px tile.
        b = pygame.Surface((110 * SS, 130 * SS), pygame.SRCALPHA)
        draw_asthi_samrat(b, 55 * SS, 64 * SS, (32 / 104.0) * SS)
        return grow(pygame.transform.smoothscale(b, (110, 130)))

    chip = chip32()
    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 130, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 130, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 10, day_y + 12))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 154))

    night_y = day_y + 182
    vgrad(sheet, (panel_x + 20, night_y, 130, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 130, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 10, night_y + 12))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 154))

    def pillar_chip32():
        b = pygame.Surface((48 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(b, 24 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        return grow(pygame.transform.smoothscale(b, (48, 130)))

    pc = pillar_chip32()
    px2 = panel_x + 168
    vgrad(sheet, (px2, day_y, 60, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 60, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 10))
    vgrad(sheet, (px2, night_y, 60, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 60, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 6, day_y - 14))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 + 2, night_y - 14))

    # === (4) BLACKED-OUT silhouette proof =====================================
    sil_x = panel_x + 250
    sheet.blit(font_sm.render("silhouette proof", True, LABEL), (sil_x - 2, day_y - 14))
    sil_big = pygame.Surface((90 * SS, 150 * SS), pygame.SRCALPHA)
    draw_asthi_samrat(sil_big, 45 * SS, 72 * SS, (138 / 246.0) * SS)
    sil = pygame.transform.smoothscale(sil_big, (90, 150))
    # flatten any opaque pixel to pure ink — the stepped-monolith blackout test
    mask = pygame.mask.from_surface(sil)
    blk = mask.to_surface(setcolor=(20, 18, 22, 255), unsetcolor=(0, 0, 0, 0))
    pygame.draw.rect(sheet, (170, 168, 178), (sil_x, day_y, 90, 150))
    pygame.draw.rect(sheet, INK, (sil_x, day_y, 90, 150), 1)
    sheet.blit(blk, (sil_x, day_y))
    sheet.blit(font_sm.render("ziggurat edge: 3", True, LABEL_DIM), (sil_x - 2, day_y + 154))
    sheet.blit(font_sm.render("jutting cornice lips", True, LABEL_DIM), (sil_x - 2, day_y + 167))

    # === (5) PALETTE strip ====================================================
    sheet.blit(font.render("Pinned palette - PURE bone", True, LABEL), (panel_x + 16, 470))
    swatches = [
        (BONE, "ivory-bone (mass)"), (BONE_D, "bone shade"),
        (BONE_DD, "groove shade"), (BONE_DDD, "deep groove"),
        (STEEL, "cold socket-pin"), (STEEL_BR, "cold-white glow"),
        (STEEL_D, "socket shade"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 496
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 22
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 18, 18))
        pygame.draw.rect(sheet, c, (rx, ry, 16, 16))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 22, ry + 2))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=5 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (28,22,26) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi-scary-cute · procedural-only · PURE bone, austerity IS the accent.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
