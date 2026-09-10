"""
Round-1 concept renderer for KUROCHIKU-NUSHI — the blackened-bamboo lacquer
noble (bamboo-versions set, concept #3). Headless Pygame; ELEVATED pipeline
(supersample SS=6 -> smoothscale) so the slim courtly geometry stays crisp at
downscale. Keeps the shipped house grammar: flat fills, hard 1-2px ink keyline,
dark-core -> flat-fill -> top-left rim-sheen triad, 1px alpha-grown outline,
chibi proportions, scary-CUTE pushed EPIC; procedural-only (no gradients/PNGs/
soft raster halos).

WHY this is the SLIM-DARK-NOBLE-STACK of the set: the bamboo brood is built on
straw / jade / pearl / snow lanes — Kurochiku-Nushi is the SOLE near-black body
(blackened kurochiku). A tall narrow figure: a small smooth black-bamboo head
with half-lidded calm eyes, a body that is a STACK of polished black node-
segments, long thin leaf-blade-fingered arms, a trailing split-culm hakama hem.
A dark vertical pillar of a creature, regal and sinister-serene.

WHY the triad must NOT collapse to a black blob: on a DARK body the house triad
reads charcoal-core groove -> blackened-violet fill -> COOL violet-white rim
sheen. The violet-white sheen + gold node-bands + lacquer-red obi/tassel are the
THREE load-bearing rim accents that carve the silhouette out of a bright sky —
they are structure, not decoration. The most prominent legibility card is a
BRIGHT NOON sky so the dark body is proven against the worst-case lightest
background.

WHY the staff/flute IS the pillar: the polished black-culm staff the noble leans
on tiles as the repeatable shaft (a black node-segment = one repeat band, gold
node-ring at each joint); a gold-capped culm-cut + red tassel is the detachable
gap-edge cap. Slim and symmetric — clean bottom-rooted top<->bottom mirror.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the triad/outline
helpers cloned from the lineage template.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# -- PINNED PALETTE (locked brief, kurochiku-nushi) ---------------------------
# The SOLE dark body in the set. The triad on a DARK base must read
# charcoal-core -> blackened-violet fill -> cool violet-white sheen.
CULM      = ( 48,  42,  52)   # near-black kurochiku culm base (the dominant fill)
CULM_D    = ( 30,  26,  38)   # ink-violet shade / dark-core groove
CULM_DD   = ( 20,  17,  26)   # deepest hollow (segment grooves, eye recess)
SHEEN     = (168, 156, 196)   # violet-white sheen accent (the cool rim — load-bearing)
SHEEN_HOT = (208, 200, 226)   # hottest violet-white catch-light
OBI       = (196,  52,  56)   # lacquer-red obi / tassel (load-bearing accent)
OBI_D     = (128,  34,  40)   # deep lacquer-red shade
GOLD      = (220, 182,  92)   # gold node-band (load-bearing accent)
GOLD_HI   = (244, 218, 150)   # hot gold edge sheen
GOLD_D    = (150, 116,  52)   # gold shade
INK       = ( 20,  16,  22)   # hard ink keyline

BG        = ( 84,  82,  96)   # neutral grey-violet review backdrop
PANEL     = ( 64,  62,  76)
# BRIGHT NOON sky — the worst-case lightest background, used for the PROMINENT
# legibility card so the dark body is shown surviving the brightest sky.
NOON_T    = (120, 200, 240)
NOON_B    = (212, 240, 250)
DAY_SKY_T = (120, 196, 236)   # standard day biome sky
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 240, 246)
LABEL_DIM = (196, 198, 212)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# -- outline grown from the alpha mask (the house keyline) --------------------
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


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True,
               ow=2, sheen_col=None):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline. On the
    dark body the default sheen lerps toward the COOL violet-white SHEEN, not
    pure white — that is what keeps the black mass from going to a flat blob."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.5), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, sheen_col or lerp(color, SHEEN, 0.7), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True, sheen_col=None):
    """Round equivalent — dark core bottom-right, cool violet-white sheen
    top-left. On the black head the sheen MUST be the violet-white accent so the
    smooth dome reads as polished lacquer, not a hole."""
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.5),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, sheen_col or lerp(color, SHEEN, 0.75),
                           (c[0] - int(r * 0.36), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.30)))
    pygame.draw.circle(surf, INK, c, r, ow)


# -- one polished black node-SEGMENT (the repeat band + body unit) ------------
def node_segment(surf, cx, cy, w, h, s, gold_top=True, gold_bot=True):
    """One polished black-bamboo node-segment: a slightly barrel-bulged dark
    culm cylinder with a charcoal-core groove down the body-side, a COOL violet-
    white sheen rail up the top-left, and a GOLD node-band ring at the joint(s).
    WHY this unit: it is simultaneously the creature's stacked body vertebra AND
    the pillar's tileable repeat band — so the mirror is structural, not faked.
    The gold band + the violet-white rail are what carve a black cylinder out of
    a bright sky."""
    hw = w * 0.5
    bulge = w * 0.10                       # gentle barrel so it reads as a culm
    top = cy - h * 0.5
    bot = cy + h * 0.5
    body = [
        (cx - hw,         top + h * 0.10),
        (cx - hw - bulge, cy),
        (cx - hw,         bot - h * 0.10),
        (cx + hw,         bot - h * 0.10),
        (cx + hw + bulge, cy),
        (cx + hw,         top + h * 0.10),
    ]
    pygame.draw.polygon(surf, INK, body)
    pygame.draw.polygon(surf, CULM, body)
    # charcoal-core groove down the right (body-side) third
    pygame.draw.polygon(surf, CULM_D, [
        (cx + hw * 0.20, top + h * 0.12),
        (cx + hw + bulge, cy),
        (cx + hw * 0.20, bot - h * 0.12),
        (cx + hw * 0.62, bot - h * 0.14),
        (cx + hw * 0.62, top + h * 0.14),
    ])
    # COOL violet-white sheen rail up the top-left — the load-bearing rim accent
    pygame.draw.polygon(surf, SHEEN, [
        (cx - hw * 0.86, top + h * 0.12),
        (cx - hw - bulge * 0.7, cy),
        (cx - hw * 0.86, bot - h * 0.16),
        (cx - hw * 0.50, bot - h * 0.22),
        (cx - hw * 0.50, top + h * 0.16),
    ])
    pygame.draw.line(surf, SHEEN_HOT, (cx - hw * 0.66, top + h * 0.18),
                     (cx - hw * 0.66, bot - h * 0.26), max(1, int(1.4 * s)))
    pygame.draw.polygon(surf, INK, body, max(1, int(1.6 * s)))

    # GOLD node-bands at the joints — hard flat ring with a hot top edge
    def gold_band(by):
        bh = max(3, int(4.0 * s))
        ring = [(cx - hw - bulge * 0.5, by + bh),
                (cx - hw - bulge * 0.5, by - bh),
                (cx + hw + bulge * 0.5, by - bh),
                (cx + hw + bulge * 0.5, by + bh)]
        pygame.draw.polygon(surf, INK, ring)
        pygame.draw.polygon(surf, GOLD, ring)
        pygame.draw.line(surf, GOLD_HI, (cx - hw, by - bh + max(1, int(1.0*s))),
                         (cx + hw, by - bh + max(1, int(1.0*s))), max(1, int(1.4*s)))
        pygame.draw.line(surf, GOLD_D, (cx - hw, by + bh - max(1, int(1.0*s))),
                         (cx + hw, by + bh - max(1, int(1.0*s))), max(1, int(1.4*s)))
        pygame.draw.polygon(surf, INK, ring, max(1, int(1.2 * s)))
    if gold_top:
        gold_band(top + h * 0.06)
    if gold_bot:
        gold_band(bot - h * 0.06)


# -- a leaf-blade finger / thin arm (the courtly long fingers) ----------------
def leaf_blade(surf, root, ang, length, width, s):
    """A long thin black leaf-blade — the noble's slender finger/arm. A lance
    polygon, charcoal-core down the trailing half, violet-white sheen up the
    leading edge, gold-flecked tip. WHY thin lance, not a fat plank: the noble
    KIND is SLIM and courtly — the long blade-fingers are the elegant tell,
    distinct from Madake's thick brute club."""
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca
    hw = width * 0.5
    tip = (root[0] + ca * length, root[1] + sa * length)
    belly = (root[0] + ca * length * 0.42, root[1] + sa * length * 0.42)
    blade = [
        (root[0] + px * hw * 0.5, root[1] + py * hw * 0.5),
        (belly[0] + px * hw, belly[1] + py * hw),
        tip,
        (belly[0] - px * hw, belly[1] - py * hw),
        (root[0] - px * hw * 0.5, root[1] - py * hw * 0.5),
    ]
    pygame.draw.polygon(surf, INK, blade)
    pygame.draw.polygon(surf, CULM, blade)
    pygame.draw.polygon(surf, CULM_D, [
        (root[0] - px * hw * 0.4, root[1] - py * hw * 0.4),
        (belly[0] - px * hw * 0.7, belly[1] - py * hw * 0.7),
        tip,
    ])
    pygame.draw.line(surf, SHEEN, (root[0] + px * hw * 0.4, root[1] + py * hw * 0.4),
                     (belly[0] + px * hw * 0.7, belly[1] + py * hw * 0.7),
                     max(1, int(1.6 * s)))
    pygame.draw.line(surf, SHEEN, (belly[0] + px * hw * 0.7, belly[1] + py * hw * 0.7),
                     tip, max(1, int(1.2 * s)))
    pygame.draw.polygon(surf, INK, blade, max(1, int(1.3 * s)))
    # gold node-fleck at the knuckle root
    pygame.draw.circle(surf, GOLD, (int(root[0]), int(root[1])), max(1, int(2.2 * s)))
    pygame.draw.circle(surf, INK, (int(root[0]), int(root[1])), max(1, int(2.2 * s)), 1)


# -- the smooth black-bamboo noble head (half-lidded calm eyes) ---------------
def noble_head(surf, cx, cy, r, s, lit=True):
    """A small smooth black-bamboo head: a polished dark dome (violet-white
    sheen up top-left so it reads lacquered, not a hole), a single gold node-band
    as a coronet across the brow, and two HALF-LIDDED calm eyes — long narrow
    violet-white slivers under a heavy lid, sinister-serene. The calm half-lid is
    the scary-CUTE-pushed-EPIC tell: it is unbothered by you."""
    triad_circle(surf, CULM, (cx, cy), r, ow=max(1, int(1.8 * s)), core=False)

    # gold coronet node-band across the brow (the noble's circlet) — a flat ring
    by = cy - int(r * 0.46)
    bh = max(2, int(3.4 * s))
    ring = [(cx - int(r * 0.96), by + bh), (cx - int(r * 0.96), by - bh),
            (cx + int(r * 0.96), by - bh), (cx + int(r * 0.96), by + bh)]
    pygame.draw.polygon(surf, INK, ring)
    pygame.draw.polygon(surf, GOLD, ring)
    pygame.draw.line(surf, GOLD_HI, (cx - int(r * 0.9), by - bh + 1),
                     (cx + int(r * 0.9), by - bh + 1), max(1, int(1.2 * s)))
    pygame.draw.line(surf, GOLD_D, (cx - int(r * 0.9), by + bh - 1),
                     (cx + int(r * 0.9), by + bh - 1), max(1, int(1.2 * s)))
    pygame.draw.polygon(surf, INK, ring, max(1, int(1.0 * s)))
    # a small gold node-jewel cresting the coronet centre
    pygame.draw.circle(surf, INK, (cx, by - bh - int(r * 0.06)), max(2, int(r * 0.16)))
    pygame.draw.circle(surf, GOLD, (cx, by - bh - int(r * 0.06)), max(1, int(r * 0.13)))
    pygame.draw.circle(surf, GOLD_HI, (cx - int(r*0.04), by - bh - int(r*0.10)),
                       max(1, int(r * 0.05)))

    # === HALF-LIDDED calm eyes — long narrow violet-white slivers ============
    # WHY half-lidded slivers: the noble is sinister-SERENE; wide eyes would read
    # cute-scared, round eyes read cartoonish. Heavy upper lid (charcoal core)
    # over a thin glowing violet-white sliver = unhurried menace, and the cool
    # sliver carves the eye out of the black face on a bright sky.
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.40)
        ey = cy + int(r * 0.18)
        ew = int(r * 0.34)
        # the heavy lid socket (deep recess)
        socket = [(ex - ew, ey - int(r * 0.06)),
                  (ex + ew, ey - int(r * 0.10)),
                  (ex + ew, ey + int(r * 0.10)),
                  (ex - ew, ey + int(r * 0.14))]
        pygame.draw.polygon(surf, CULM_DD, socket)
        # the calm half-lid sliver of violet-white (lower half of the socket)
        sliver = [(ex - ew * 0.86, ey + int(r * 0.02)),
                  (ex + ew * 0.86, ey - int(r * 0.01)),
                  (ex + ew * 0.70, ey + int(r * 0.09)),
                  (ex - ew * 0.70, ey + int(r * 0.11))]
        pygame.draw.polygon(surf, SHEEN, sliver)
        if lit:
            pygame.draw.line(surf, SHEEN_HOT,
                             (ex - ew * 0.5, ey + int(r * 0.05)),
                             (ex + ew * 0.5, ey + int(r * 0.03)),
                             max(1, int(1.2 * s)))
        # the heavy upper lid pressing down (charcoal wedge) — the half-lid read
        pygame.draw.polygon(surf, CULM_D, [
            (ex - ew, ey - int(r * 0.08)),
            (ex + ew, ey - int(r * 0.11)),
            (ex + ew * 0.7, ey + int(r * 0.01)),
            (ex - ew * 0.7, ey + int(r * 0.03))])
        pygame.draw.line(surf, INK, (ex - ew, ey - int(r * 0.06)),
                         (ex + ew, ey - int(r * 0.10)), max(1, int(1.4 * s)))

    # a thin lacquer-red lip line — a calm closed mouth, the obi colour echoed up
    pygame.draw.line(surf, OBI, (cx - int(r * 0.22), cy + int(r * 0.56)),
                     (cx + int(r * 0.22), cy + int(r * 0.54)), max(1, int(1.8 * s)))
    # the violet-white dome catch-light (re-asserted over the brow band)
    pygame.draw.circle(surf, SHEEN, (cx - int(r * 0.42), cy - int(r * 0.62)),
                       max(1, int(r * 0.13)))


# -- the slim courtly noble hero ----------------------------------------------
def draw_kurochiku_nushi(surf, cx, cy, s):
    """The blackened-bamboo lacquer noble: a tall narrow figure — small smooth
    black head over a STACK of polished node-segments, a lacquer-red OBI sash at
    the waist, long thin leaf-blade arms folded courtly, a trailing split-culm
    hakama hem flaring at the base. `s` = unit scale around a ~150-unit-tall
    figure. Drawn back-to-front: hem -> body stack -> obi -> arms -> head."""

    head_r = int(20 * s)
    head_c = (cx, cy - int(54 * s))
    # the body stack runs from just under the head down to the waist
    seg_w = int(26 * s)
    seg_h = int(20 * s)
    stack_top = cy - int(30 * s)

    # === trailing split-culm HAKAMA hem (drawn first, behind the stack) =======
    # WHY a split-culm hem: it gives the slim figure a grounded, robe-like base
    # and a clean bottom-root for the pillar mirror — a black skirt of culm
    # blades fanning out, each tipped with a violet-white sheen so the dark hem
    # doesn't dissolve into the gap.
    hem_top = cy + int(28 * s)
    for sgn in (-1, 1):
        for k, (off, ln) in enumerate(((0.0, 1.0), (0.42, 0.92), (0.84, 0.78))):
            ang = math.radians(90 + sgn * (14 + off * 30))
            leaf_blade(surf, (cx + sgn * int(2 * s), hem_top),
                       ang, int(46 * s) * ln, int(13 * s) * (1 - 0.12 * k), s)
    # a centre culm tail straight down
    leaf_blade(surf, (cx, hem_top), math.radians(90), int(50 * s), int(14 * s), s)

    # === BODY — a STACK of polished black node-segments (the noble torso) =====
    # three stacked segments, narrowing slightly upward (courtly tapering robe)
    seg_ys = [stack_top + int(14 * s) + i * int(seg_h + 4 * s) for i in range(3)]
    for i, sy in enumerate(seg_ys):
        w = seg_w - i * int(2 * s)
        node_segment(surf, cx, sy, w, seg_h, s,
                     gold_top=(i == 0), gold_bot=True)

    # === lacquer-red OBI sash at the waist (the load-bearing red accent) ======
    # a wide flat red band wrapping the lowest segment joint, with a knot + two
    # short hanging tails — the strongest warm note, anchoring the silhouette
    obi_y = seg_ys[-1] + int(seg_h * 0.5) + int(2 * s)
    obi_h = max(4, int(8 * s))
    obi_rect = [(cx - seg_w * 0.62, obi_y + obi_h),
                (cx - seg_w * 0.62, obi_y - obi_h),
                (cx + seg_w * 0.62, obi_y - obi_h),
                (cx + seg_w * 0.62, obi_y + obi_h)]
    pygame.draw.polygon(surf, INK, obi_rect)
    pygame.draw.polygon(surf, OBI, obi_rect)
    pygame.draw.polygon(surf, OBI_D, [
        (cx - seg_w * 0.62, obi_y + obi_h),
        (cx + seg_w * 0.62, obi_y + obi_h),
        (cx + seg_w * 0.62, obi_y + obi_h * 0.2),
        (cx - seg_w * 0.62, obi_y + obi_h * 0.2)])
    pygame.draw.line(surf, lerp(OBI, SHEEN_HOT, 0.4),
                     (cx - seg_w * 0.55, obi_y - obi_h + max(1, int(1.4*s))),
                     (cx + seg_w * 0.55, obi_y - obi_h + max(1, int(1.4*s))),
                     max(1, int(1.6 * s)))
    pygame.draw.polygon(surf, INK, obi_rect, max(1, int(1.4 * s)))
    # obi knot (centre) + two short tails
    knot = [(cx - int(7 * s), obi_y - int(7 * s)), (cx + int(7 * s), obi_y - int(7 * s)),
            (cx + int(5 * s), obi_y + int(8 * s)), (cx - int(5 * s), obi_y + int(8 * s))]
    pygame.draw.polygon(surf, INK, knot)
    pygame.draw.polygon(surf, OBI, knot)
    pygame.draw.line(surf, lerp(OBI, SHEEN_HOT, 0.5),
                     (cx - int(4 * s), obi_y - int(5 * s)),
                     (cx - int(4 * s), obi_y + int(6 * s)), max(1, int(1.4 * s)))
    pygame.draw.polygon(surf, INK, knot, max(1, int(1.2 * s)))

    # === long thin leaf-blade ARMS folded courtly across the body =============
    # WHY folded across, not spread: the noble does not hurry — arms tucked,
    # long blade-fingers crossed at the waist over the obi, an unhurried courtly
    # posture. Thin lance blades distinguish him from the brute ogre.
    shoulder_y = seg_ys[0] + int(2 * s)
    for sgn in (-1, 1):
        sh = (cx + sgn * int(seg_w * 0.5), shoulder_y)
        # upper arm down-and-in toward the obi
        leaf_blade(surf, sh, math.radians(90 + sgn * 58), int(34 * s), int(10 * s), s)
        # long blade-fingers fanning over the obi (three slender tips)
        wrist = (cx + sgn * int(10 * s), obi_y - int(4 * s))
        for fo in (-10, 4, 18):
            leaf_blade(surf, wrist, math.radians(90 - sgn * 50 + sgn * fo),
                       int(22 * s), int(5 * s), s)

    # === HEAD last — short culm neck linking head to the top segment ==========
    pygame.draw.line(surf, INK, (cx, head_c[1] + int(head_r * 0.9)),
                     (cx, stack_top + int(6 * s)), max(2, int(7 * s)))
    pygame.draw.line(surf, CULM, (cx, head_c[1] + int(head_r * 0.9)),
                     (cx, stack_top + int(6 * s)), max(1, int(4 * s)))
    pygame.draw.line(surf, SHEEN, (cx - int(2 * s), head_c[1] + int(head_r * 0.9)),
                     (cx - int(2 * s), stack_top + int(6 * s)), max(1, int(1.2 * s)))
    noble_head(surf, head_c[0], head_c[1], head_r, s, lit=True)


# -- the black-culm staff/flute -> pillar mirror ------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The polished black-culm STAFF the noble leans on IS the pillar: a stack of
    black node-segments (gold ring at each joint, violet-white sheen rail) = the
    tileable shaft; a gold-capped culm-cut + lacquer-red TASSEL is the detachable
    gap-edge cap. Slim and symmetric — clean bottom-rooted mirror.

    `cap` names the END that faces the GAP."""
    seg_w = int(24 * s)
    seg_h = int(26 * s)
    # central ink rod the segments thread onto (kills any sky gap between bands)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    cap_room = int(46 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)

    # stack the node-segments down the shaft
    y = b0 + seg_h * 0.5
    while y <= b1:
        node_segment(surf, cx, int(y), seg_w, seg_h, s, gold_top=True, gold_bot=True)
        y += seg_h

    # === gap-edge cap: gold-capped culm-cut + lacquer-red tassel =============
    # WHY a culm-cut + tassel cap: a cut black-culm flute end reads as a clean
    # gold-rimmed mouth; the red tassel hangs toward the GAP so the heavy warm
    # mass sits at the gap edge, never top-heavy.
    if cap == "bottom":
        cut_y = bot - int(34 * s)
        tassel_y = bot - int(16 * s)
        td = 1
    else:
        cut_y = top + int(34 * s)
        tassel_y = top + int(16 * s)
        td = -1

    # the culm-cut: a final node-segment with a gold-rimmed open mouth facing gap
    node_segment(surf, cx, cut_y, seg_w + int(2 * s), seg_h, s,
                 gold_top=(cap == "top"), gold_bot=(cap == "bottom"))
    # gold-capped open mouth (an ellipse of gold ring with a dark bore)
    mouth_y = cut_y + td * int(seg_h * 0.42)
    mw = seg_w * 0.5
    pygame.draw.ellipse(surf, INK, (cx - mw - int(2*s), mouth_y - int(6*s),
                                    (mw + int(2*s)) * 2, int(12 * s)))
    pygame.draw.ellipse(surf, GOLD, (cx - mw, mouth_y - int(5*s), mw * 2, int(10 * s)))
    pygame.draw.ellipse(surf, GOLD_HI, (cx - mw, mouth_y - int(5*s), mw * 2, int(10 * s)),
                        max(1, int(1.4 * s)))
    pygame.draw.ellipse(surf, CULM_DD, (cx - mw * 0.6, mouth_y - int(3*s),
                                        mw * 1.2, int(6 * s)))

    # the lacquer-red TASSEL hanging toward the gap — a knot + three cords
    tk = (cx, tassel_y)
    pygame.draw.circle(surf, INK, tk, max(3, int(5 * s)))
    pygame.draw.circle(surf, OBI, tk, max(2, int(4 * s)))
    pygame.draw.circle(surf, lerp(OBI, SHEEN_HOT, 0.45),
                       (tk[0] - int(1.4 * s), tk[1] - int(1.4 * s)), max(1, int(1.6 * s)))
    pygame.draw.circle(surf, INK, tk, max(2, int(4 * s)), 1)
    for dx_c in (-0.5, 0.0, 0.5):
        ex = cx + dx_c * int(9 * s)
        ey = tassel_y + td * int(16 * s)
        pygame.draw.line(surf, INK, tk, (ex, ey), max(2, int(3 * s)))
        pygame.draw.line(surf, OBI, tk, (ex, ey), max(1, int(1.8 * s)))
        pygame.draw.line(surf, OBI_D, ((tk[0]+ex)//2, (tk[1]+ey)//2), (ex, ey),
                         max(1, int(1.2 * s)))


# -- compose the review sheet -------------------------------------------------
SS = 6


def vgrad(surf, rect, top_col, bot_col):
    # review-sheet backdrop only (NOT shipped art) — fine to gradient the card.
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def main():
    W, H = 1010, 900
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("KUROCHIKU-NUSHI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "blackened-bamboo lacquer noble  ·  SLIM-DARK-NOBLE-STACK · sole DARK body · violet-white sheen + gold bands + lacquer-red obi · round 1",
        True, LABEL_DIM), (320, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_kurochiku_nushi(big, 178 * SS, 232 * SS, 1.78 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("Slim courtly noble: small smooth black head (gold coronet, HALF-LIDDED calm eyes)", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("over a STACK of black node-segments; lacquer-red OBI at the waist; long thin", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("leaf-blade arms folded courtly; trailing split-culm hakama hem. Sinister-serene.", True, LABEL_DIM), (14, 622))

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
    pygame.draw.rect(sheet, (52, 50, 64), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — black-culm staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked black node-segments (gold ring +", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("violet-white rail) = shaft; gold culm-cut +", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("red tassel caps each gap edge — mirror visible", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) legibility panel: BRIGHT NOON (prominent) + day + night ==========
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("DARK-BODY legibility test", True, LABEL), (panel_x + 16, 96))

    def chip32(size=96, scale=(32 / 150.0)):
        big = pygame.Surface((size * SS, size * SS), pygame.SRCALPHA)
        draw_kurochiku_nushi(big, (size // 2) * SS, int(size * 0.52) * SS, scale * SS)
        small = pygame.transform.smoothscale(big, (size, size))
        return grow_outline(small, INK + (255,), 1)

    # The PROMINENT card: a BRIGHT NOON sky, worst-case lightest background. Made
    # the largest so the dark body is proven against the lightest sky FIRST.
    noon_y = 124
    noon_sz = 150
    vgrad(sheet, (panel_x + 20, noon_y, noon_sz, noon_sz), NOON_T, NOON_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, noon_y, noon_sz, noon_sz), 1)
    big_noon = chip32(size=110, scale=(48 / 150.0))   # a touch larger, the focal card
    sheet.blit(big_noon, (panel_x + 20 + 20, noon_y + 20))
    sheet.blit(font.render("BRIGHT NOON sky (worst case)", True, LABEL), (panel_x + 20, noon_y + 156))
    sheet.blit(font_sm.render("violet-white sheen + gold bands + red obi carve the black body clear", True, LABEL_DIM), (panel_x + 20, noon_y + 174))

    # true 32px chips: noon / day / night side by side
    row_y = noon_y + 200
    chip = chip32()
    cards = [(NOON_T, NOON_B, "32px NOON"),
             (DAY_SKY_T, DAY_SKY_B, "32px day"),
             (NIGHT_T, NIGHT_B, "32px night")]
    for i, (ct, cb, lab) in enumerate(cards):
        cxp = panel_x + 20 + i * 104
        vgrad(sheet, (cxp, row_y, 96, 96), ct, cb)
        pygame.draw.rect(sheet, INK, (cxp, row_y, 96, 96), 1)
        sheet.blit(chip, (cxp, row_y))
        sheet.blit(font_sm.render(lab, True, LABEL if i < 2 else LABEL_DIM),
                   (cxp + 4, row_y + 98))

    # blacked-out 32px silhouette — must read a TALL SLENDER NOBLE-STACK, never a
    # blob (the KIND test), and a pillar chip on a bright sky beside it
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_kurochiku_nushi(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        return mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))

    sil_y = row_y + 134
    sx = panel_x + 20
    pygame.draw.rect(sheet, (214, 216, 222), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT —", True, LABEL), (sx + 104, sil_y + 26))
    sheet.blit(font_sm.render("tall slender NOBLE-STACK,", True, LABEL_DIM), (sx + 104, sil_y + 44))
    sheet.blit(font_sm.render("never a black blob", True, LABEL_DIM), (sx + 104, sil_y + 62))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 212
    vgrad(sheet, (px2, sil_y - 18, 56, 130), NOON_T, NOON_B)
    pygame.draw.rect(sheet, INK, (px2, sil_y - 18, 56, 130), 1)
    sheet.blit(pc, (px2 + 6, sil_y - 18))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, sil_y - 34))
    sheet.blit(font_sm.render("on noon", True, LABEL_DIM), (px2 + 2, sil_y + 114))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, sil_y + 134))
    swatches = [
        (CULM, "near-black culm"), (CULM_D, "ink-violet shade"),
        (SHEEN, "violet-white sheen"), (SHEEN_HOT, "sheen hot"),
        (OBI, "lacquer-red obi"), (GOLD, "gold node-band"),
        (CULM_DD, "deep hollow"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, sil_y + 162
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 162
        ry = syp + row * 24
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 18, 18))
        pygame.draw.rect(sheet, c, (rx, ry, 16, 16))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 24, ry + 2))

    pygame.draw.rect(sheet, PANEL, (14, 850, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (20,16,22) · "
        "charcoal-core->blackened-violet fill->cool violet-white sheen triad · 1px grown outline · chibi · scary-CUTE · procedural-only · NO black blob.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
