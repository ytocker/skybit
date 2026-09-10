"""BURRO PINATA — a flying donkey piñata flyer skin (Round-2 concept).

The piñata set needs five flyers that each read as their OWN distinct thing at
~40px. The burro's job is to be the only LEGGED CREATURE in the set: a boxy
crepe-fringe donkey body with a stubby upright head + two ear nubs and four
short tassel-tipped legs dangling on its festival rope. No bird, no wings.

Identity beats the contract has to protect at 40px:
  * SILHOUETTE — a side-profile 4-legged quadruped. Barrel body, short upright
    neck/head, two ear nubs, four little legs. The legs are SHORT, in a clearly
    SPLIT front-pair / back-pair (a wide gap between the pairs so FOUR nubs read,
    never a 3-leg "sitting dog"), and tassel-tipped so they survive downscale as
    bright blobs rather than vanishing into hairline mush.
  * TELL (no wings / no particles) — TROT-SWAY. The whole body bobs ±2px and the
    OUTERMOST legs (frontmost + rearmost) splay PAST the body width on the OUT
    frame then tuck under on the TUCK frame. Pip's parcel hangs over the body
    centre, so the swing is pushed to the outer leg edges where the parcel can't
    mask it. The delta is a pure SILHOUETTE change, so it survives grayscale.
  * COLOUR — tiered crepe-paper fringe bands: hot-pink / orange / turquoise,
    with a cream mane + cream legs. Cream keylines the dark body top AND bottom
    at night; each leg ends in a BRIGHT festival-hue tassel (orange/pink) so all
    four nubs read in grayscale and against the night sky.

Contract (mirrors game/animal_ufo.py so a winner lifts straight into a
production module):
  * `build(wing_angle_deg) -> pygame.Surface` — one flat frame, 64x84 SRCALPHA,
    body mass centred at (32,44), legs dangle below, drawn UPRIGHT (no tilt).
  * The 4 trot frames are driven by `_WING_ANGLES=(50,20,-10,-40)` → leg swing
    + body bob, consumed by `animal_ufo._make_prebuilt_skin`.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + anchors (mirror animal_ufo.py / animal_skins.py) ────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # donkey body centre → (32, 44); 14px hit circle


# ── crepe-fringe colourway ───────────────────────────────────────────────────
# The body is built from three tiered fringe BANDS top→bottom so the piñata read
# is unmistakable. Each band carries a slightly darker "shadow" tone for the
# scallop undersides and the body's rounded volume.
PINK        = (242, 73, 126)     # #F2497E  top band
PINK_D      = (196, 48, 96)
ORANGE      = (245, 139, 31)     # #F58B1F  middle band
ORANGE_D    = (200, 104, 18)
TURQ        = (35, 194, 168)     # #23C2A8  lower band
TURQ_D      = (22, 150, 130)

CREAM       = (255, 241, 214)    # #FFF1D6  mane + legs — the night keyline
CREAM_D     = (228, 206, 168)    # cream shadow / stitch
SNOUT       = (250, 232, 202)    # pale crepe snout tip
EAR_IN      = (255, 158, 120)    # warm inner-ear crepe
EYE         = (40, 26, 30)
EYE_GLINT   = (255, 255, 255)
HOOF        = (120, 86, 70)      # little hoof nub under each bright tassel

# Per-leg tassel colours: the OUTER (frontmost + rearmost) legs carry the two
# warmest festival hues so the splayed trot legs pop against day AND night sky;
# the inner pair carry pink/turquoise. Crucially the BACK pair is recoloured to
# BRIGHT hues (orange + pink) — round 1's dark-brown rear knots collapsed into
# one peg, so now both rear nubs glow as distinct festival blobs.
#   index → leg:  0 front-near, 1 front-far, 2 back-far, 3 back-near
TASSELS = (ORANGE, PINK, ORANGE, PINK)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 trot frame. `_WING_ANGLES` runs 50→-40, so
    the four poses step the legs out → tucked → out and the body bob cycles."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Per-frame trot drivers, indexed by phase 0..3.
#   bob   — vertical body offset (px); the head visibly rises/falls over the
#           parcel as the body bounces on its rope (±2px swing).
#   sway  — outer-leg swing amount; +out (frontmost/rearmost splay PAST the body
#           width), -tuck (gathered under). The parcel masks the body centre, so
#           the tell lives at the outer leg edges, not the inner swing.
_TROT = (
    # phase 0  legs splayed OUT, body LOW on the bounce
    {"bob":  2, "sway":  1.0},
    # phase 1  legs mid, body rising
    {"bob":  0, "sway":  0.0},
    # phase 2  legs TUCKED, body HIGH at the top of the bounce
    {"bob": -2, "sway": -1.0},
    # phase 3  legs mid, body dropping
    {"bob":  0, "sway":  0.0},
)


def _fringe_band(surf, cx, cy, rx, ry, color, shadow, n_scallop):
    """A tiered crepe-paper fringe band: a filled rounded slab whose lower edge
    is cut into scallop nubs (the cut crepe fringe). `n_scallop` little arcs
    along the bottom sell the layered-paper read; a thin shadow line under the
    band gives the tier its overlap depth."""
    # main slab
    _aaellipse(surf, color, (cx, cy), rx, ry)
    # scallop fringe along the lower edge of the band
    step = (2 * rx) / n_scallop
    r_sc = max(2, int(step * 0.6))
    fy = cy + ry - 1
    for i in range(n_scallop):
        sx = int(cx - rx + step * (i + 0.5))
        # depth of fringe follows the band's curvature so the tier hangs round
        t = (sx - (cx - rx)) / (2 * rx)
        curve = math.sin(math.pi * t)
        pygame.draw.circle(surf, color, (sx, int(fy + curve * 1.5)), r_sc)
        # shadow notch between scallops for the cut-paper read
        pygame.draw.circle(surf, shadow, (int(sx + step * 0.5), int(fy + curve * 1.0)),
                           max(1, r_sc - 1))


def _leg(surf, hip_x, hip_y, reach, swing, tassel_color, *, back=False, outer=False):
    """One short tassel-tipped leg. A stubby cream crepe stub ending in a fat
    BRIGHT tassel knot — short + tassel-tipped so it survives 40px as a nub.

    `reach` is the static splay (front pair reaches +x, back pair reaches -x; a
    wide gap between the pairs keeps FOUR nubs distinct). `swing` (+out / -tuck)
    drives the trot delta and only the OUTER legs swing far PAST the body width
    so the gait reads with the parcel over the body centre."""
    # Back legs swing opposite the front pair so the trot reads as a gait;
    # only the outer (frontmost/rearmost) legs swing the full amount so the
    # silhouette change happens at the body's edges, clear of the parcel.
    s = (-swing if back else swing) * (4.0 if outer else 1.5)
    foot_x = int(hip_x + reach + s)
    foot_y = int(hip_y + 11 - abs(swing) * 1.5)
    knee_x = int(hip_x + reach * 0.5 + s * 0.5)
    knee_y = int(hip_y + 6)
    # crepe leg stub — cream so it keylines the dark body at night
    pygame.draw.line(surf, CREAM_D, (hip_x, hip_y), (knee_x, knee_y), 5)
    pygame.draw.line(surf, CREAM, (hip_x, hip_y), (knee_x, knee_y), 3)
    pygame.draw.line(surf, CREAM_D, (knee_x, knee_y), (foot_x, foot_y), 5)
    pygame.draw.line(surf, CREAM, (knee_x, knee_y), (foot_x, foot_y), 3)
    # fat tassel knot at the foot (the part that reads at 40px). A bright crepe
    # bulb over a small hoof nub; the bright bulb is what survives night.
    pygame.draw.circle(surf, HOOF, (foot_x, foot_y), 2)
    _aaellipse(surf, tassel_color, (foot_x, foot_y + 2), 4, 4)
    # cream keyline rim under the tassel so the rear nubs glow off the night sky
    pygame.draw.circle(surf, CREAM, (foot_x, foot_y + 2), 1)
    # three little tassel strands fanned below the knot
    for dx in (-2, 0, 2):
        pygame.draw.line(surf, tassel_color, (foot_x, foot_y + 2),
                         (foot_x + dx, foot_y + 7), 1)


def _ear(surf, base_x, base_y, lean, color):
    """A donkey ear NUB — a tall cream crepe triangle raked slightly BACK (-x)
    with a warm inner. Two of these on the head are the donkey tell. `lean`
    tips the tip backward so the pair reads as alert-but-relaxed donkey ears,
    not forward-perky fox/corgi ears."""
    tip = (base_x + lean, base_y - 10)
    pts = [(base_x - 3, base_y), (base_x + 3, base_y), tip]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, EAR_IN, [(base_x - 1, base_y - 1),
                                       (base_x + 1, base_y - 1),
                                       (base_x + lean // 2, base_y - 6)])
    pygame.draw.polygon(surf, CREAM_D, pts, 1)


def build_pinata_burro(wing_angle_deg):
    """One trot frame. Body mass + head sit at/above (32,44); the four legs
    dangle below in a clearly split front-pair / back-pair to frame Pip's
    parcel. Drawn upright; velocity tilt applied downstream by the cached
    getter."""
    surf = _new()
    ph = _phase(wing_angle_deg)
    bob = _TROT[ph]["bob"]
    sway = _TROT[ph]["sway"]

    cx = BCX
    cy = BCY + bob                  # whole body bobs on the rope (±2px)

    # ── rope nub up top — the piñata hangs from a string ─────────────────────
    pygame.draw.line(surf, CREAM_D, (cx, cy - 22), (cx, cy - 16), 2)

    # ── LEGS first so the body slab overlaps the hips cleanly ────────────────
    # The body half-width is ~17px. Front pair reaches well toward +x, back pair
    # well toward -x, with a WIDE EMPTY GAP between the pairs so four nubs never
    # collapse to three. The outer legs (front-near / back-near) additionally
    # splay PAST the body edge on the OUT frame — that's the trot tell.
    hip_y = cy + 7
    # back pair (toward -x). back-near is the OUTER (rearmost) swinging leg.
    _leg(surf, cx - 6,  hip_y, -3, sway, TASSELS[2], back=True)               # back-far
    _leg(surf, cx - 10, hip_y, -7, sway, TASSELS[3], back=True, outer=True)   # back-near (rearmost)
    # front pair (toward +x). front-near is the OUTER (frontmost) swinging leg.
    _leg(surf, cx + 6,  hip_y,  3, sway, TASSELS[1])                          # front-far
    _leg(surf, cx + 10, hip_y,  7, sway, TASSELS[0], outer=True)             # front-near (frontmost)

    # ── BODY — three tiered crepe-fringe bands stacked into a barrel mass ─────
    # Barrel (wide, fairly flat) so it reads as a creature's body, not a ball.
    # Top pink band, middle orange, lower turquoise — each fringed.
    _fringe_band(surf, cx - 1, cy - 4, 17, 7, PINK,   PINK_D,   8)   # top
    _fringe_band(surf, cx - 1, cy + 1, 17, 6, ORANGE, ORANGE_D, 8)   # middle
    _fringe_band(surf, cx - 1, cy + 6, 16, 6, TURQ,   TURQ_D,   8)   # lower

    # rounded body keyline (cream) along the TOP so the dark crepe survives a
    # bright day sky and glows against night.
    top_rect = pygame.Rect(cx - 1 - 17, cy - 4 - 7, 34, 14)
    pygame.draw.arc(surf, CREAM, top_rect, math.radians(15), math.radians(165), 2)
    # NEW: a thin cream keyline along the BOTTOM edge of the turquoise band so
    # the lower body lifts off the night sky the same way the top edge already
    # does — the dark turquoise was vanishing into night in round 1.
    bot_rect = pygame.Rect(cx - 1 - 16, cy + 6 - 6, 32, 12)
    pygame.draw.arc(surf, CREAM, bot_rect, math.radians(200), math.radians(340), 2)

    # ── NECK + HEAD — stubby, upright, on the +x (front) shoulder ─────────────
    neck_x = cx + 13
    # short upright neck slab (orange crepe, fringed cream mane behind it)
    pygame.draw.polygon(surf, ORANGE, [
        (neck_x - 4, cy - 2), (neck_x + 5, cy - 9),
        (neck_x + 9, cy - 8), (neck_x + 4, cy + 3),
    ])
    pygame.draw.polygon(surf, ORANGE_D, [
        (neck_x - 4, cy - 2), (neck_x + 4, cy + 3), (neck_x - 1, cy + 2),
    ])

    # CREAM MANE — a fringed crest running up the back of the neck (the donkey
    # tell + the night keyline on the head).
    mane_pts = [(neck_x - 5, cy + 1), (neck_x - 1, cy - 10),
                (neck_x + 3, cy - 12), (neck_x + 1, cy - 4), (neck_x - 2, cy + 2)]
    pygame.draw.polygon(surf, CREAM, mane_pts)
    for k in range(4):
        my = cy - 9 + k * 3
        pygame.draw.line(surf, CREAM_D, (neck_x - 4 + k, my), (neck_x - 6 + k, my + 2), 1)

    # HEAD — a LONGER, blunter donkey muzzle block facing +x (forward). Round 1
    # read fennec/corgi; the muzzle is now extended and squared toward +x and
    # the pink cheek band shrunk so the long pale snout dominates the head.
    hx, hy = neck_x + 8, cy - 9
    # crepe head block — a smaller pink cheek so it doesn't dominate the muzzle
    _aaellipse(surf, PINK,  (hx, hy), 6, 5)
    _aaellipse(surf, PINK_D, (hx, hy + 2), 6, 3)             # lower-jaw shadow
    # LONG blunt muzzle extending forward (+x): a pale snout slab, blunt-capped.
    _aaellipse(surf, SNOUT, (hx + 6, hy + 1), 6, 4)          # muzzle barrel
    _aaellipse(surf, SNOUT, (hx + 10, hy + 1), 3, 3)         # blunt nose cap
    pygame.draw.circle(surf, CREAM_D, (hx + 12, hy + 1), 3, 1)  # nose keyline
    pygame.draw.circle(surf, EYE, (hx + 11, hy + 2), 1)     # nostril
    # cream keyline arc over the (longer) head top
    hrect = pygame.Rect(hx - 7, hy - 6, 22, 12)
    pygame.draw.arc(surf, CREAM, hrect, math.radians(0), math.radians(170), 2)

    # EARS — two tall nubs raked slightly BACK (the unmistakable donkey signal;
    # round 1's forward-perky nubs read fox/corgi). Both lean toward -x.
    _ear(surf, hx - 3, hy - 4, -4, CREAM)
    _ear(surf, hx + 1, hy - 5, -3, CREAM)

    # EYE — single side-profile eye with a glint, set back on the cheek.
    pygame.draw.circle(surf, EYE, (hx + 1, hy - 1), 2)
    pygame.draw.circle(surf, EYE_GLINT, (hx, hy - 2), 1)

    return surf


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter (mirrors animal_ufo.py):
    a lazy 4-frame build through the house silhouette outline + a per-(frame, 3°)
    rotation cache, so the flyer animates and banks with the bird's tilt."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_pinata_burro(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


get_pinata_burro = _make_prebuilt_skin(build_pinata_burro)

BUILDERS = {"skin_pinata_burro": get_pinata_burro}
