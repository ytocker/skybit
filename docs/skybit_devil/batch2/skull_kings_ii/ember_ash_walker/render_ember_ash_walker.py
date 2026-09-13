"""
Round-1 concept renderer for EMBER ASH WALKER — the only skull-KING in MOTION
(Skull Kings II brood). Headless Pygame; ELEVATED pipeline (SS=6 -> smoothscale)
so the ember cracks + ash-rime ticks survive the downscale. Procedural-only
(no PNGs); clones the sibling REGENT KOSCHEI structure + helpers (SS supersample,
grow_outline, triad_blob/triad_circle, bone_limb, draw_pillar, flat triad, 1-2px
ink keyline) and the same 5-region SHEET LAYOUT.

WHY a WALKER, not another enthroned/standing king: every other king in the brood
is static — seated, standing, cradling. This one is the brood's ONE figure in
forward MOTION. The whole identity rides on the STRIDE reading in blackout: one
leg LIFTED forward + the trailing ash-cloak streaming off the back shoulder make
an asymmetric, leaning silhouette that says "walking" with zero colour. The
swung staff rakes forward to complete the lean. Lock the asymmetry hard — a
symmetric pose kills the only thing that separates this king from the others.

WHY a SKULL war-helm worn crest-FORWARD over the brow (not a spike crown): the
brood tell is "a great skull above the head." Here it is ONE oversized charred
skull tipped low and forward over the figure's own brow like a war-helm — the
forward tilt doubles as a motion cue (leaning into the stride). It is the single
above-head silhouette landmark that must read DAY and NIGHT at 32px.

WHY a SINGLE bright ember crack at the chest is the focal: matte charcoal body
with ember cracks risks "uniform glow-mush" if every crack glows equally. So ONE
chest crack is the hottest pixel (the named focal) and all other cracks are
dimmer embers — a clear value hierarchy, one dominant warm point.

NIGHT LOCK: charcoal (72,68,74) nearly vanishes on a dark night sky. The ember
cracks + a grey ash-rime RIM carry the silhouette there — the night chip widens
the ash-rime halo (not the ember) so the SHAPE survives without turning the
figure into a second fireball.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + triad/outline helpers, not runtime sprite
modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# -- PINNED PALETTE -----------------------------------------------------------
# matte charcoal body is the ONE dominant mass; ember + ash-rime are thin accents.
CHAR      = ( 72,  68,  74)   # matte charcoal body (dominant fill)
CHAR_D    = ( 46,  43,  50)   # charcoal shade / recessed
CHAR_DD   = ( 30,  28,  34)   # deepest charcoal hollow
CHAR_SH   = ( 98,  94, 100)   # charcoal top-left rim sheen
# the EMBER-orange cracks glowing through the charcoal.
EMBER     = (232, 120,  48)   # ember-orange crack base
EMBER_BR  = (252, 176,  92)   # brighter ember
EMBER_HOT = (255, 232, 170)   # hottest ember core (the chest focal = brightest px)
EMBER_D   = (150,  62,  26)   # dim/dying ember (the non-focal cracks)
# grey ash-rime ticks + rim (the cool structural accent that carries night).
RIME      = (170, 166, 172)   # ash-rime grey
RIME_BR   = (212, 210, 216)   # ash-rime highlight
RIME_D    = (118, 114, 122)   # ash-rime shade
INK       = ( 28,  22,  30)   # 1-2px ink keyline

BG        = ( 96, 100, 108)
PANEL     = ( 74,  78,  88)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (188, 196, 208)


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
        pygame.draw.polygon(surf, lerp(color, CHAR_SH, 0.7), sheen_pts)
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
        pygame.draw.circle(surf, lerp(color, CHAR_SH, 0.6),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


def char_limb(surf, p0, p1, p2, thick, s, joint=True):
    """A charcoal limb (clone of bone_limb, charcoal triad). Top-left sheen so
    the matte body still has a readable light direction without ember help."""
    for (a, b) in ((p0, p1), (p1, p2)):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * thick / 2, dx / L * thick / 2
        quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
        triad_blob(surf, CHAR, quad,
                   sheen_pts=[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                              (b[0] + nx * 0.3, b[1] + ny * 0.3),
                              (a[0] + nx * 0.3, a[1] + ny * 0.3)],
                   ow=max(1, int(thick * 0.18)))
    if joint:
        triad_circle(surf, CHAR, p1, int(thick * 0.60), ow=max(1, int(1.2 * s)),
                     core=False)


def ember_crack(surf, pts, s, hot=False, dim=False):
    """A jagged ember crack drawn as a glowing polyline through the charcoal.
    WHY only ONE call passes hot=True: the chest crack must own the single
    brightest pixel; the rest are EMBER_D dying embers so the figure reads as
    one focal + dim filigree, never uniform glow-mush."""
    if hot:
        core, edge, halo = EMBER_HOT, EMBER_BR, EMBER
    elif dim:
        core, edge, halo = EMBER_D, EMBER_D, EMBER_D
    else:
        core, edge, halo = EMBER_BR, EMBER, EMBER_D
    lw = max(1, int(2.0 * s))
    if not dim:
        # a soft outer glow so the crack reads as light from within the charcoal
        glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.lines(glow, halo + (70,), False, pts, lw + max(2, int(3 * s)))
        surf.blit(glow, (0, 0))
    pygame.draw.lines(surf, edge, False, pts, lw + max(1, int(1 * s)))
    pygame.draw.lines(surf, core, False, pts, lw)
    if hot:
        # the hottest core node = the single brightest pixel of the whole figure
        mid = pts[len(pts) // 2]
        pygame.draw.circle(surf, EMBER_HOT, mid, max(2, int(2.4 * s)))
        glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(glow, EMBER_BR + (110,), mid, max(3, int(6 * s)))
        surf.blit(glow, (0, 0))


def rime_tick(surf, p, s, ln=4.0, ang=0.0):
    """A short grey ash-rime tick — the cool accent that carries the night rim.
    Drawn as a tiny dash so it reads as crusted ash on the charcoal."""
    dx, dy = math.cos(ang) * ln * s, math.sin(ang) * ln * s
    pygame.draw.line(surf, RIME, (p[0] - dx, p[1] - dy), (p[0] + dx, p[1] + dy),
                     max(1, int(1.4 * s)))
    pygame.draw.circle(surf, RIME_BR, (int(p[0]), int(p[1])), max(1, int(0.9 * s)))


# -- the great charred SKULL war-helm, worn crest-FORWARD over the brow --------
def skull_helm(surf, cx, cy, r, s):
    """ONE oversized charred skull as a war-helm tilted low + FORWARD over the
    figure's own brow. WHY forward-tilt: it is both the brood's above-head skull
    tell AND a motion cue — the helm leans into the stride. Ember veins thread
    the cranium (dimmer than the chest focal); the eye sockets glow a low ember
    so the helm reads at 32px without stealing the chest focal."""
    # The SKULL silhouette is cut by the MASS outline alone (so it survives the
    # blackout gate). WHY one DEEPLY-notched profile, not an ellipse + ticks: round
    # 3's blackout crown still read as a lumpy potato — one smooth lobe with no
    # unambiguous jaw/cheek hollow and no brow stepping out from the crest. The
    # three skull cues that survive blackout are SILHOUETTE notches, not interior
    # shading, so they are cut HARD into the outline here:
    #   (1) a clean forward CREST ridge jutting up+fwd, then a sharp inward DIP so
    #       the crest reads as its own mass;
    #   (2) a BROW that juts forward as a SEPARATE step below that dip (brow != crest);
    #   (3) the most important cue — a HARD concave V CHEEK HOLLOW biting straight
    #       inward under the cheekbone (the DEEPEST concavity in the whole crop, not a
    #       smooth scallop), pinching the face so a JAW steps back OUT below it as its
    #       own mass (wide cranium over a pinched waist over a forward jaw). The front
    #       edge top->bottom reads four events: crest lobe -> dip -> brow shelf (OUT)
    #       -> cheek HOLLOW (bites IN) -> jaw/chin (steps OUT, tapers).
    tilt = int(r * 0.16)
    bx = cx + tilt                         # forward (motion) bias of the whole skull
    # ---- the skull MASS profile, traced clockwise from the back of the crown ----
    # forward (+x) is to the RIGHT. Extra intermediate points hold the sharp notches
    # so the SS=6 -> smoothscale downscale can't round them back into a smooth lobe.
    skull = [
        (bx - int(r * 0.62), cy - int(r * 0.46)),   # back of crown (rounded)
        (bx - int(r * 0.48), cy - int(r * 0.74)),
        (bx - int(r * 0.18), cy - int(r * 0.94)),
        (bx + int(r * 0.16), cy - int(r * 1.00)),   # cranium dome top (one clean round dome)
        (bx + int(r * 0.46), cy - int(r * 0.94)),
        (bx + int(r * 0.66), cy - int(r * 1.12)),   # >>> forward CREST horn juts up+fwd
        (bx + int(r * 0.82), cy - int(r * 0.92)),   #     crest front face drops sharply
        (bx + int(r * 0.64), cy - int(r * 0.64)),   # >>> DEEP dip behind the brow
        (bx + int(r * 0.50), cy - int(r * 0.54)),   #     (separates crest from brow)
        (bx + int(r * 0.94), cy - int(r * 0.42)),   # >>> BROW shelf steps OUT (own mass)
        (bx + int(r * 1.16), cy - int(r * 0.22)),   #     brow / cheekbone juts AHEAD
        (bx + int(r * 1.20), cy + int(r * 0.04)),   #     CHEEKBONE tip (forward, widest corner)
        (bx + int(r * 1.12), cy + int(r * 0.14)),   #     cheekbone underside — sharp corner
        # >>> the SKULL cue: a HARD concave V biting straight IN to the deepest point
        # of the whole crop, directly under the cheekbone. The lip dives almost
        # HORIZONTALLY back to a deep apex (kept tight so smoothscale can't relax it
        # into a scallop), then the jaw PUNCHES back out — the single deepest bite,
        # deeper than any back-of-skull or jaw-hinge concavity, so it OWNS the read.
        (bx + int(r * 0.22), cy + int(r * 0.18)),   #     hollow lip — sharp horizontal dive in
        (bx + int(r * 0.10), cy + int(r * 0.34)),   # >>> HOLLOW APEX — deepest bite of the crop
        (bx + int(r * 0.26), cy + int(r * 0.48)),   #     hollow exits down (jaw begins, pinched)
        (bx + int(r * 1.00), cy + int(r * 0.62)),   # >>> JAW ANGLE punches back OUT (own mass)
        (bx + int(r * 0.84), cy + int(r * 0.94)),   #     jaw front, forward
        (bx + int(r * 0.54), cy + int(r * 1.06)),   #     chin juts down + forward (tapered point)
        (bx + int(r * 0.28), cy + int(r * 0.92)),
        (bx + int(r * 0.16), cy + int(r * 0.54)),   # jaw underside, tucked UNDER the face
        (bx + int(r * 0.10), cy + int(r * 0.30)),   # >>> back jaw hinge pinches IN hard
        (bx - int(r * 0.18), cy + int(r * 0.04)),   # back cheek (steep — no down-left lobe)
        (bx - int(r * 0.50), cy - int(r * 0.10)),   # back of skull sweeps cleanly up (smooth)
        (bx - int(r * 0.66), cy - int(r * 0.30)),   # back of skull rounds up to the crown
    ]
    triad_blob(surf, CHAR, skull,
               core_pts=[(bx + int(r * 0.16), cy - int(r * 0.06)),
                         (bx + int(r * 0.92), cy - int(r * 0.04)),
                         (bx + int(r * 0.62), cy + int(r * 0.50)),
                         (bx + int(r * 0.04), cy + int(r * 0.44))],
               sheen_pts=[(bx - int(r * 0.62), cy - int(r * 0.20)),
                          (bx - int(r * 0.06), cy - int(r * 0.90)),
                          (bx + int(r * 0.06), cy - int(r * 0.50)),
                          (bx - int(r * 0.54), cy + int(r * 0.04))],
               ow=max(1, int(1.6 * s)))
    # CREST RIDGE highlight — a clean charcoal-sheen spine riding the crown, kept
    # INSIDE the profile (the crest is already cut by the silhouette above). WHY a
    # sheen ridge not a spiky fan: round 2's frizzy ticks read as a mop; this is a
    # single clean ridge that catches the light along the forward crest.
    crest = [(bx - int(r * 0.02), cy - int(r * 0.92)),
             (bx + int(r * 0.32), cy - int(r * 0.96)),
             (bx + int(r * 0.62), cy - int(r * 1.06)),
             (bx + int(r * 0.74), cy - int(r * 0.78)),
             (bx + int(r * 0.40), cy - int(r * 0.68)),
             (bx + int(r * 0.06), cy - int(r * 0.68))]
    pygame.draw.polygon(surf, CHAR_SH, crest)
    pygame.draw.polygon(surf, INK, crest, max(1, int(1.0 * s)))
    # forward-jutting BROW RIDGE — a hard dark band over the sockets, seated on the
    # silhouette's brow step so the brow reads as its own mass below the crest dip.
    brow = [(bx - int(r * 0.12), cy - int(r * 0.42)),
            (bx + int(r * 1.06), cy - int(r * 0.30)),
            (bx + int(r * 1.04), cy + int(r * 0.06)),
            (bx - int(r * 0.08), cy - int(r * 0.08))]
    triad_blob(surf, CHAR_D, brow, ow=max(1, int(1.3 * s)))
    # deep cheek-HOLLOW under the eye — recessed value inside the face, seated right
    # on the silhouette's concave cheek bite so the pinch reads even when lit.
    cheek = [(bx + int(r * 0.30), cy + int(r * 0.20)),
             (bx + int(r * 0.92), cy + int(r * 0.22)),
             (bx + int(r * 0.70), cy + int(r * 0.56)),
             (bx + int(r * 0.30), cy + int(r * 0.44))]
    pygame.draw.polygon(surf, CHAR_DD, cheek)
    # two eye sockets — ink pits with a LOW ember glow (dimmer than chest focal),
    # tucked under the brow band.
    for (ox, scale) in ((0.36, 1.0), (0.82, 0.86)):
        ex = bx + int(r * ox)
        ey = cy - int(r * 0.10)
        er = int(r * 0.26 * scale)
        pygame.draw.circle(surf, INK, (ex, ey), er + max(1, int(1.2 * s)))
        pygame.draw.circle(surf, EMBER_D, (ex, ey), er)
        pygame.draw.circle(surf, EMBER, (ex, ey + int(er * 0.2)), int(er * 0.55))
    # nasal pit
    pygame.draw.polygon(surf, INK,
                        [(bx + int(r * 0.58), cy + int(r * 0.06)),
                         (bx + int(r * 0.70), cy + int(r * 0.06)),
                         (bx + int(r * 0.64), cy + int(r * 0.32))])
    # a few ember veins threading the cranium (DIM — not the focal)
    ember_crack(surf, [(bx - int(r * 0.24), cy - int(r * 0.66)),
                       (bx + int(r * 0.08), cy - int(r * 0.46)),
                       (bx + int(r * 0.36), cy - int(r * 0.60))], s, dim=True)
    ember_crack(surf, [(bx + int(r * 0.50), cy - int(r * 0.58)),
                       (bx + int(r * 0.78), cy - int(r * 0.32))], s, dim=True)
    # teeth row set on the NARROWED jaw (inboard of the cheek hollow) — a short rime
    # row so the skull's grin reads against the dark cheek hollow.
    jy = cy + int(r * 0.70)
    pygame.draw.line(surf, INK, (bx + int(r * 0.40), jy),
                     (bx + int(r * 0.70), jy - int(r * 0.02)),
                     max(1, int(1.6 * s)))
    for k in range(4):
        tx = bx + int(r * (0.40 + k * 0.09))
        pygame.draw.line(surf, RIME, (tx, jy - int(r * 0.05)),
                         (tx, jy + int(r * 0.09)), max(1, int(1.0 * s)))


# -- the streaming ash-CLOAK off the trailing shoulder ------------------------
def ash_cloak(surf, sx, sy, s, length, drop):
    """ONE backward-streaming ash-cloak mass with a long tapering tail off the
    trailing (back) shoulder. WHY a single tapering pennant, not a ragged fan:
    in round 1 the cloak split into separate shards that read as extra spider
    legs. Here it is one solid wedge that starts wide at the shoulder and tapers
    to a single point streaming up-and-back — an unmistakable rearward banner
    that says MOTION and never multiplies the limb count in blackout."""
    # one solid cloak wedge: anchored wide at the shoulder, tapering BACK (left)
    # and slightly UP (a banner caught by the forward run), to a single tail tip.
    tail = (sx - length * 1.18, sy - drop * 0.10)   # the single far tail point
    top = [(sx + length * 0.06, sy - drop * 0.18),  # upper shoulder anchor
           (sx - length * 0.34, sy - drop * 0.22),
           (sx - length * 0.74, sy - drop * 0.18),
           tail]
    bot = [tail,
           (sx - length * 0.70, sy + drop * 0.34),
           (sx - length * 0.30, sy + drop * 0.44),
           (sx + length * 0.10, sy + drop * 0.30)]  # lower shoulder anchor
    hem = top + bot[1:]
    triad_blob(surf, CHAR_D, hem,
               core_pts=[(sx - length * 0.06, sy - drop * 0.02),
                         (sx - length * 0.56, sy - drop * 0.04),
                         (sx - length * 0.52, sy + drop * 0.22),
                         (sx - length * 0.04, sy + drop * 0.18)],
               ow=max(1, int(1.6 * s)))
    # two interior FOLD lines down the cloak's length — read as drapery sweeping
    # back, reinforce the single rearward direction (no shard ambiguity).
    for fy in (-0.04, 0.18):
        pygame.draw.line(surf, CHAR_DD,
                         (sx - length * 0.04, sy + drop * fy),
                         (sx - length * 0.92, sy + drop * (fy * 0.4 - 0.04)),
                         max(1, int(1.3 * s)))
    # one dim ember crack tracing the upper fold (NOT hot)
    ember_crack(surf, [(sx - length * 0.10, sy - drop * 0.02),
                       (sx - length * 0.46, sy - drop * 0.06),
                       (sx - length * 0.82, sy - drop * 0.10)], s, dim=True)
    # ash-rime ticks strung along the trailing top edge (carries the night rim)
    for fx in (0.30, 0.56, 0.82, 1.04):
        rime_tick(surf, (sx - length * fx, sy - drop * 0.16), s, ln=3.4,
                  ang=math.radians(-8))


# -- the bone/charcoal STAFF swung forward ------------------------------------
def staff(surf, hand, tip, s):
    """A staff thrust FORWARD-DOWN along the travel line past the leading hand —
    a low forward diagonal that rakes ahead of the stride (NOT a near-vertical
    fifth limb, which in round 1 added to the spider read). Charcoal shaft,
    ember-cracked, capped by a small skull knob with a low ember glow (a quiet
    echo of the helm, kept dim)."""
    dx, dy = tip[0] - hand[0], tip[1] - hand[1]
    L = max(1.0, math.hypot(dx, dy))
    nx, ny = -dy / L * 3.4 * s, dx / L * 3.4 * s
    shaft = [(hand[0] + nx, hand[1] + ny), (tip[0] + nx, tip[1] + ny),
             (tip[0] - nx, tip[1] - ny), (hand[0] - nx, hand[1] - ny)]
    triad_blob(surf, CHAR, shaft,
               sheen_pts=[(hand[0] + nx, hand[1] + ny), (tip[0] + nx, tip[1] + ny),
                          (tip[0] + nx * 0.3, tip[1] + ny * 0.3),
                          (hand[0] + nx * 0.3, hand[1] + ny * 0.3)],
               ow=max(1, int(1.2 * s)))
    ember_crack(surf, [(hand[0], hand[1]),
                       ((hand[0] + tip[0]) / 2, (hand[1] + tip[1]) / 2),
                       (tip[0], tip[1])], s, dim=True)
    # small skull knob finial with a low ember glow (quiet echo of the helm)
    triad_circle(surf, CHAR, (int(tip[0]), int(tip[1])), int(5 * s),
                 ow=max(1, int(1.2 * s)), core=False)
    for sgn in (-1, 1):
        pygame.draw.circle(surf, EMBER_D,
                           (int(tip[0] + sgn * 2 * s), int(tip[1] - 1 * s)),
                           max(1, int(1.2 * s)))


# -- the mid-stride EMBER ASH WALKER ------------------------------------------
def draw_walker(surf, cx, cy, s):
    """WHY the whole pose leans forward-right: this is the ONE king in motion.
    The leading (right) leg plants ahead, the trailing (left) leg LIFTS off the
    ground bent back, the torso pitches forward, the helm juts ahead, the staff
    rakes forward, and the ash-cloak streams back-left off the trailing shoulder.
    Asymmetry is the identity — keep it loud in blackout."""
    # anchor points of the leaning skeleton. WHY hips sit RAISED + stacked OVER
    # the planted front foot: round 2 read as a deep track-start LUNGE because the
    # hips sat too low and the front shin raked too far. Lifting the pelvis and
    # carrying it forward over the plant turns the diagonal into a confident,
    # near-upright forward WALK while keeping the forward lean (the motion cue).
    pelvis = (cx + int(11 * s), cy + int(10 * s))  # hips RAISED + carried over the plant
    chest = (cx + int(14 * s), cy - int(18 * s))   # torso pitched forward (right)
    neck = (cx + int(17 * s), cy - int(30 * s))
    head_c = (cx + int(20 * s), cy - int(42 * s))  # head ahead of pelvis (the lean)
    hr = int(13 * s)

    # === ASH-CLOAK first — ONE mass streaming BEHIND (drawn under the body) ===
    # anchored at the BACK (trailing) shoulder and swept up-and-back.
    ash_cloak(surf, chest[0] - int(10 * s), chest[1] + int(2 * s), s,
              length=int(74 * s), drop=int(46 * s))

    # === THE WALKING DIAGONAL — built leading-LOWER to trailing-UPPER =========
    # This single line IS the lock. Front (leading) leg plants AHEAD and DOWN
    # with the hips stacked above it; the trailing leg LIFTS off the ground and
    # bends BACK. Drawn trailing-first so the planted front leg reads on top.
    leg_th = int(11 * s)

    # --- TRAILING leg: lifted + bent back, knee high, toe trailing (one clean
    #     bent limb, no splay) -------------------------------------------------
    t_hip = (pelvis[0] - int(4 * s), pelvis[1])
    t_knee = (pelvis[0] - int(24 * s), pelvis[1] + int(2 * s))   # knee swept back
    t_foot = (pelvis[0] - int(34 * s), pelvis[1] - int(18 * s))  # foot LIFTED up+back
    char_limb(surf, t_hip, t_knee, t_foot, int(leg_th * 0.92), s)
    # lifted foot/toe pointing up-and-back (clearly off the ground)
    tf = [(t_foot[0] - int(11 * s), t_foot[1] - int(5 * s)),
          (t_foot[0] + int(2 * s), t_foot[1] - int(6 * s)),
          (t_foot[0] + int(4 * s), t_foot[1] + int(3 * s)),
          (t_foot[0] - int(9 * s), t_foot[1] + int(5 * s))]
    triad_blob(surf, CHAR, tf, ow=max(1, int(1.2 * s)))

    # --- LEADING leg: planted near-straight DOWN with the hips stacked above it.
    #     WHY a short shin rake (foot barely ahead of the knee): a long forward
    #     rake reads as a sprinter's lunge; a near-vertical plant under the raised
    #     hip reads as an upright WALK while the torso lean still carries motion.
    l_hip = (pelvis[0] + int(3 * s), pelvis[1])
    l_knee = (pelvis[0] + int(8 * s), pelvis[1] + int(26 * s))    # mostly straight down
    l_foot = (pelvis[0] + int(11 * s), pelvis[1] + int(52 * s))   # planted near under the hip
    char_limb(surf, l_hip, l_knee, l_foot, leg_th, s)
    lf = [(l_foot[0] - int(5 * s), l_foot[1] - int(3 * s)),
          (l_foot[0] + int(18 * s), l_foot[1] - int(1 * s)),
          (l_foot[0] + int(17 * s), l_foot[1] + int(8 * s)),
          (l_foot[0] - int(6 * s), l_foot[1] + int(7 * s))]
    triad_blob(surf, CHAR, lf, ow=max(1, int(1.2 * s)))
    ember_crack(surf, [(l_knee[0] - int(3 * s), l_knee[1]),
                       (l_foot[0] - int(4 * s), l_foot[1] - int(10 * s))],
                s, dim=True)

    # === PELVIS ==============================================================
    pel = [(pelvis[0] - int(13 * s), pelvis[1] - int(6 * s)),
           (pelvis[0] + int(13 * s), pelvis[1] - int(6 * s)),
           (pelvis[0] + int(10 * s), pelvis[1] + int(8 * s)),
           (pelvis[0] - int(10 * s), pelvis[1] + int(8 * s))]
    triad_blob(surf, CHAR, pel, ow=max(1, int(1.5 * s)))

    # === SPINE + TORSO (pitched forward) =====================================
    spine = [pelvis, (cx + int(2 * s), cy + int(4 * s)), chest]
    pygame.draw.lines(surf, INK, False, spine, int(9 * s))
    pygame.draw.lines(surf, CHAR, False, spine, int(6 * s))
    torso = [(pelvis[0] - int(11 * s), pelvis[1] - int(4 * s)),
             (chest[0] - int(12 * s), chest[1] + int(4 * s)),
             (chest[0] + int(13 * s), chest[1]),
             (pelvis[0] + int(12 * s), pelvis[1] - int(2 * s))]
    triad_blob(surf, CHAR, torso,
               core_pts=[(chest[0] - int(2 * s), chest[1] + int(2 * s)),
                         (chest[0] + int(12 * s), chest[1] + int(1 * s)),
                         (pelvis[0] + int(11 * s), pelvis[1] - int(3 * s)),
                         (pelvis[0] + int(2 * s), pelvis[1] - int(3 * s))],
               sheen_pts=[(pelvis[0] - int(11 * s), pelvis[1] - int(4 * s)),
                          (chest[0] - int(12 * s), chest[1] + int(4 * s)),
                          (chest[0] - int(6 * s), chest[1] + int(5 * s)),
                          (pelvis[0] - int(6 * s), pelvis[1] - int(5 * s))],
               ow=max(1, int(1.7 * s)))
    # dim rib-like cracks across the torso (filigree, NOT the focal)
    for i in range(3):
        ry = chest[1] + int((6 + i * 7) * s)
        ember_crack(surf, [(cx - int(8 * s), ry + int(2 * s)),
                           (cx + int(2 * s), ry),
                           (cx + int(11 * s), ry + int(3 * s))], s, dim=True)

    # === ARMS — TWO, kept TIGHT to the body so they never fan into extra legs ==
    arm_th = int(6 * s)
    # trailing (back) arm — bent and tucked CLOSE along the ribs as a subtle
    # counter-swing; it stays inside the torso mass in blackout (no extra limb).
    t_sh = (chest[0] - int(9 * s), chest[1] + int(2 * s))
    t_el = (chest[0] - int(13 * s), chest[1] + int(16 * s))
    t_hand = (chest[0] - int(6 * s), chest[1] + int(26 * s))
    char_limb(surf, t_sh, t_el, t_hand, arm_th, s)
    # leading (front) arm — reaches FORWARD-DOWN to drive the staff along the
    # travel line (the arm + staff read as ONE forward thrust, not two limbs).
    l_sh = (chest[0] + int(12 * s), chest[1] + int(1 * s))
    l_el = (chest[0] + int(26 * s), chest[1] + int(10 * s))
    l_hand = (chest[0] + int(34 * s), chest[1] + int(22 * s))
    char_limb(surf, l_sh, l_el, l_hand, arm_th, s)
    # the staff thrust FORWARD-DOWN past the leading hand, low along the travel
    # line — extends the front arm's reach ahead of the stride.
    staff(surf, l_hand, (l_hand[0] + int(40 * s), l_hand[1] + int(20 * s)), s)

    # === THE SINGLE BRIGHT EMBER FOCAL — one chest crack, the hottest pixel ===
    # WHY drawn AFTER the torso filigree + body: it must own the foreground +
    # the brightest pixel; everything else is dim ember or cool rime.
    ember_crack(surf, [(chest[0] - int(6 * s), chest[1] - int(4 * s)),
                       (chest[0] + int(1 * s), chest[1] + int(2 * s)),
                       (chest[0] - int(2 * s), chest[1] + int(9 * s)),
                       (chest[0] + int(5 * s), chest[1] + int(15 * s))],
                s, hot=True)

    # === HEAD (the figure's own skull, under the helm) =======================
    triad_circle(surf, CHAR, head_c, hr, ow=max(2, int(1.8 * s)), core=False)
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (head_c[0] + sgn * int(hr * 0.42), head_c[1] + int(hr * 0.10)),
                           int(hr * 0.26))
        pygame.draw.circle(surf, EMBER_D,
                           (head_c[0] + sgn * int(hr * 0.42), head_c[1] + int(hr * 0.10)),
                           int(hr * 0.16))

    # === SKULL WAR-HELM worn crest-FORWARD over the brow (above-head tell) ====
    skull_helm(surf, head_c[0] + int(2 * s), head_c[1] - int(hr * 0.92),
               int(hr * 1.30), s)


# -- a charred-bone pillar that mirrors the walker's forms --------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """Charcoal pillar with ember-veined lashings + a skull-helm cap that mirrors
    the walker. Top<->bottom mirrored; bottom-rooted. Ember stays dim here so the
    pillars never out-glow the king's chest focal in play."""
    shaft_w = int(16 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    pitch = int(28 * s)
    cap_room = int(42 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    while y <= b1:
        for sgn in (-1, 1):
            fx = cx + sgn * int(7 * s)
            top_y = y - int(9 * s)
            bot_y = y + int(9 * s)
            shaft = [(fx - int(4 * s), top_y), (fx + int(4 * s), top_y),
                     (fx + int(3 * s), y), (fx + int(4 * s), bot_y),
                     (fx - int(4 * s), bot_y), (fx - int(3 * s), y)]
            triad_blob(surf, CHAR, shaft,
                       sheen_pts=[(fx - int(4 * s), top_y), (fx - int(1 * s), top_y),
                                  (fx - int(1 * s), bot_y), (fx - int(4 * s), bot_y)],
                       ow=max(1, int(1.2 * s)))
        # ember-veined lashing band cinching the pair (dim ember + rime ticks)
        band = [(cx - shaft_w * 0.66, y - int(4 * s)),
                (cx + shaft_w * 0.66, y - int(4 * s)),
                (cx + shaft_w * 0.66, y + int(4 * s)),
                (cx - shaft_w * 0.66, y + int(4 * s))]
        triad_blob(surf, CHAR_D, band, ow=max(1, int(1.1 * s)))
        ember_crack(surf, [(cx - shaft_w * 0.5, y), (cx, y - int(2 * s)),
                           (cx + shaft_w * 0.5, y)], s, dim=True)
        rime_tick(surf, (cx - shaft_w * 0.4, y - int(3 * s)), s, ln=3.0)
        rime_tick(surf, (cx + shaft_w * 0.4, y + int(3 * s)), s, ln=3.0)
        y += pitch

    cap_y = (bot - int(26 * s)) if cap == "bottom" else (top + int(26 * s))
    fan_dir = -1 if cap == "bottom" else 1
    # a skull-helm cap echoing the walker's crest (charcoal + low ember sockets)
    skull_helm(surf, cx - int(int(13 * s) * 0.16), cap_y + fan_dir * int(2 * s),
               int(13 * s), s)


# -- compose the review sheet -------------------------------------------------
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_walker(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def load_fonts():
    """FONT is five levels up from this script; SysFont fallback if missing."""
    base = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(base, "..", "..", "..", "..", "..",
                      "game", "assets", "LiberationSans-Bold.ttf")
    try:
        return (pygame.font.Font(fp, 30), pygame.font.Font(fp, 17),
                pygame.font.Font(fp, 12))
    except Exception:
        return (pygame.font.SysFont("DejaVu Sans", 30, bold=True),
                pygame.font.SysFont("DejaVu Sans", 17, bold=True),
                pygame.font.SysFont("DejaVu Sans", 12))


def main():
    W, H = 1180, 820
    font_big, font, font_sm = load_fonts()

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("EMBER ASH WALKER", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "Skull Kings II  ·  the ONE king in MOTION · mid-stride forward walker · charred skull war-helm crest-forward · "
        "streaming ash-cloak + forward staff thrust · single chest-ember focal · round 5",
        True, LABEL_DIM), (360, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 168, 236, 1.78)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("mid-STRIDE: leading leg planted ahead, trailing leg LIFTED + bent back,", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("ash-cloak streaming off the back shoulder, staff swung forward. Charred", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("SKULL war-helm crest-forward over the brow. ONE hot chest ember = focal.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored ======================================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — charred femur", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("paired charcoal column, ember-veined lashings +", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("ash-rime ticks; skull-helm cap echoes the walker", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, bottom-rooted)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) PROOF column — re-shot in round-4 order: the CROWN crop is the LEAD
    # gate (the round-3 blocker), THEN the full-figure blackout, THEN the 32px
    # day+night chips. The head fix is checked in isolation BEFORE anything else.
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("Read-order proof: crown -> figure -> 32px", True, LABEL), (panel_x + 16, 96))

    day_y = 122
    sil_x = panel_x + 196
    chips_y = 392                          # the 32px row sits below both blackout proofs

    # --- PROOF 1 (LEAD GATE): CROWN blackout crop — the skull-helm ALONE, blacked
    # out, NO body context, so "the crown alone must say SKULL, not ball/potato" is
    # checkable directly. Enlarged in round 4 so the three silhouette cues read.
    def crown_blackout(box):
        # render JUST the skull-helm at the SAME proportions the walker uses
        # (r = hr*1.30), centred so the whole crown is framed with margin.
        sc = 2.3
        r = int(int(13 * sc) * 1.30)
        big = pygame.Surface((box * SS, box * SS), pygame.SRCALPHA)
        rS = r * SS
        # the profile spans x in [bx-0.64r, bx+1.14r], y in [cy-1.12r, cy+1.04r];
        # centre that bounding box (x mid ~ +0.25r off bx, y mid ~ -0.04r off cy).
        # skull_helm derives bx = cx + int(r*0.16), so back the tilt out of cx to
        # land the mass centre at the box centre.
        cy = box // 2 * SS + int(0.04 * rS)
        bx = box // 2 * SS - int(0.25 * rS)
        skull_helm(big, bx - int(rS * 0.16), cy, rS, sc * SS)
        small = pygame.transform.smoothscale(big, (box, box))
        mask = pygame.mask.from_surface(small)
        sil = pygame.Surface((box, box), pygame.SRCALPHA)
        sil.blit(mask.to_surface(setcolor=(18, 18, 20, 255),
                                 unsetcolor=(0, 0, 0, 0)), (0, 0))
        return sil

    crown_box = 150
    pygame.draw.rect(sheet, (210, 212, 216), (panel_x + 20, day_y, crown_box, crown_box))
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, crown_box, crown_box), 1)
    sheet.blit(crown_blackout(crown_box), (panel_x + 20, day_y))
    sheet.blit(font_sm.render("1) CROWN crop ALONE = the gate", True, LABEL), (panel_x + 20, day_y + 154))
    sheet.blit(font_sm.render("no body: crest horn + brow step", True, LABEL_DIM), (panel_x + 20, day_y + 170))
    sheet.blit(font_sm.render("+ cheek HOLLOW + jaw = SKULL", True, LABEL_DIM), (panel_x + 20, day_y + 186))

    # --- PROOF 2: full-figure blackout — the WALK + above-head SKULL crest read
    def silhouette():
        big = pygame.Surface((150 * SS, 200 * SS), pygame.SRCALPHA)
        draw_walker(big, 70 * SS, 100 * SS, 1.28 * SS)
        small = pygame.transform.smoothscale(big, (150, 200))
        mask = pygame.mask.from_surface(small)
        sil = pygame.Surface((150, 200), pygame.SRCALPHA)
        solid = mask.to_surface(setcolor=(18, 18, 20, 255), unsetcolor=(0, 0, 0, 0))
        sil.blit(solid, (0, 0))
        return sil

    pygame.draw.rect(sheet, (210, 212, 216), (sil_x, day_y, 150, 200))
    pygame.draw.rect(sheet, INK, (sil_x, day_y, 150, 200), 1)
    sheet.blit(silhouette(), (sil_x, day_y))
    sheet.blit(font_sm.render("2) full-figure blackout", True, LABEL), (sil_x, day_y + 204))
    sheet.blit(font_sm.render("planted front + lifted back leg = WALK,", True, LABEL_DIM), (sil_x, day_y + 220))
    sheet.blit(font_sm.render("big skull crest above the head", True, LABEL_DIM), (sil_x, day_y + 236))

    # --- PROOF 3: true 32px chips on day + night sky
    def chip32(night=False):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_walker(big, 46 * SS, 56 * SS, (32 / 128.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        # WHY a widened ASH-RIME (grey) rim on the night chip, NOT a brighter
        # ember: the charcoal body dissolves into a dark night sky; a grey rim
        # carries the SHAPE while keeping the chest ember the single bright tell
        # (a brighter ember rim would turn the figure into a fireball blob).
        if night:
            base = grow_outline(small, RIME_D + (255,), 2)
            return grow_outline(base, INK + (200,), 1)
        return grow_outline(small, INK + (255,), 1)

    day_chip = chip32(night=False)
    night_chip = chip32(night=True)

    sheet.blit(font.render("3) true 32px gameplay-scale chip", True, LABEL), (panel_x + 16, chips_y - 26))
    vgrad(sheet, (panel_x + 20, chips_y, 96, 96), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, chips_y, 96, 96), 1)
    sheet.blit(day_chip, (panel_x + 20, chips_y))
    sheet.blit(font_sm.render("day", True, LABEL_DIM), (panel_x + 50, chips_y + 98))
    vgrad(sheet, (sil_x, chips_y, 96, 96), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (sil_x, chips_y, 96, 96), 1)
    sheet.blit(night_chip, (sil_x - 1, chips_y - 1))
    sheet.blit(font_sm.render("night (ash-rime rim)", True, LABEL_DIM), (sil_x, chips_y + 98))

    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = sil_x + 168
    pday_y = day_y
    pnight_y = day_y + 168
    vgrad(sheet, (px2, pday_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, pday_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, pday_y + 10))
    vgrad(sheet, (px2, pnight_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, pnight_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, pnight_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, pday_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, pnight_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (CHAR, "matte charcoal body"), (CHAR_D, "charcoal shade"),
        (EMBER, "ember-orange crack"), (EMBER_HOT, "chest focal (hottest)"),
        (EMBER_D, "dim/dying ember"), (RIME, "ash-rime grey"),
        (RIME_BR, "ash-rime highlight"), (RIME_D, "ash-rime / night rim"),
        (INK, "ink keyline"), (CHAR_SH, "charcoal sheen"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 188
        ry = syp + row * 24
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "EMBER ASH WALKER — the brood's ONE king in MOTION.  Stride read = planted front leg + lifted back leg (a clean walking diagonal, loud in blackout) + ONE streaming cloak.  "
        "ONE matte-charcoal mass; ember + ash-rime are thin accents; the single hot chest ember is the focal.  Night carried by ash-rime rim.  SS=6 -> smoothscale · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_5.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    self_check()


def self_check():
    """Verify (1) the brightest pixel sits in the hot chest ember (the focal owns
    the peak), and (2) ember reads as a thin accent — strongly-ember pixels stay a
    small fraction of charcoal-body pixels (one focal, not glow-mush)."""
    surf = pygame.Surface((400, 520), pygame.SRCALPHA)
    draw_walker(surf, 200, 250, 2.0)
    px = pygame.surfarray.pixels3d(surf)
    a = pygame.surfarray.pixels_alpha(surf)
    w, h = surf.get_size()
    best_lum, best_xy = -1, (0, 0)
    ember_n, char_n = 0, 0
    for x in range(0, w, 2):
        for yy in range(0, h, 2):
            if a[x, yy] < 40:
                continue
            r, g, b = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > best_lum:
                best_lum, best_xy = lum, (x, yy)
            # crude ember detector: warm, red-dominant, low blue
            if r > 180 and g > 90 and b < 140 and r > b + 50 and r >= g:
                ember_n += 1
            # crude charcoal detector: dark near-neutral
            if r < 120 and g < 120 and b < 130 and abs(r - g) < 30:
                char_n += 1
    bx, by = best_xy
    r, g, b = int(px[bx, by][0]), int(px[bx, by][1]), int(px[bx, by][2])
    is_ember = (r > 200 and g > 150 and b < 220 and r >= b)
    del px, a
    print("self-check: brightest pixel @", best_xy, "rgb", (r, g, b),
          "lum %.0f" % best_lum, "-> ember-core?", is_ember)
    print("self-check: ember px ~%d  vs charcoal px ~%d  -> ember fraction %.2f"
          % (ember_n, char_n, ember_n / max(1, ember_n + char_n)))


if __name__ == "__main__":
    main()
