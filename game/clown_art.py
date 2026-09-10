"""Plum & Lime court-jester clown art — the inline clown event's character + die.

This is the SHIPPED, web-safe home of the clown body, face, cap, costume and the
3D power-up die cube. The art was developed under tools/ (render_clown_dice +
render_jester_variants, not bundled into the pygbag/web build); it is re-homed
here VERBATIM so the real clown renders on both native and web. The look-dev
sheets in tools/ import these same symbols back, so there is a single source of
truth and the rendered figure is pixel-identical to the approved "Plum & Lime —
FINAL" design (JESTERS[-1]).

`draw_chosen_hero` (game/pillar_staff.py) composes the clown by calling
`build_jester` here; `_draw_die_face_noshadow` renders the floating/rolling die.
Everything is pure pygame primitives — no game state, no tools/ imports.
"""
import math

import pygame

from game.draw import blit_glow


# ── chunky clown body-kit primitives (re-homed from the dice-clown mockup) ────
# The vocabulary every jester is composited from, so the figure reads as one
# family of casual-cute mascots: thick limbs, sculpted facet panels, a round
# friendly head and a big red ball nose. Colours are passed in by the caller.

INK = (28, 22, 30)
WHITE = (250, 248, 244)
IVORY = (248, 242, 230)          # warm face base — never dead chalk-white
ROSY = (255, 150, 150)
RIM = (255, 250, 235)            # top-left key light (matches coin/HUD lighting)


def _shade(c, d):
    return (max(0, min(255, int(c[0] + d))),
            max(0, min(255, int(c[1] + d))),
            max(0, min(255, int(c[2] + d))))


def _poly(surf, color, pts, oc=None, w=1):
    pygame.draw.polygon(surf, color, pts)
    if oc is not False:
        pygame.draw.polygon(surf, oc or _shade(color, -70), pts, w)


def _poly_mask(pts, minx, miny, maxx, maxy):
    m = pygame.Surface((maxx - minx + 2, maxy - miny + 2), pygame.SRCALPHA)
    pygame.draw.polygon(m, (255, 255, 255, 255),
                        [(p[0] - minx, p[1] - miny) for p in pts])
    return m


def _arm(surf, shoulder, hand, w, color, glove=(252, 250, 246), up=False):
    """A chunky tapered arm ending in a big round GLOVED hand. `up=True` is the
    presenting gesture: the hand opens toward the die above."""
    mx = (shoulder[0] + hand[0]) // 2
    my = (shoulder[1] + hand[1]) // 2 + (-2 if up else 4)
    pygame.draw.line(surf, _shade(color, -50), shoulder, (mx, my), w + 3)
    pygame.draw.line(surf, _shade(color, -50), (mx, my), hand, w + 1)
    pygame.draw.line(surf, color, shoulder, (mx, my), w)
    pygame.draw.line(surf, color, (mx, my), hand, w - 1)
    pygame.draw.circle(surf, _shade(color, 30), (mx, my), w // 2 + 1)
    pygame.draw.circle(surf, (250, 250, 252), hand, w - 1)
    gr = w
    pygame.draw.circle(surf, _shade(glove, -55), hand, gr + 1)
    pygame.draw.circle(surf, glove, hand, gr)
    pygame.draw.circle(surf, RIM, (hand[0] - 2, hand[1] - 2), max(1, gr // 3))
    if up:
        pygame.draw.circle(surf, glove, (hand[0] - gr, hand[1] + 1),
                           max(2, gr // 2))
        pygame.draw.circle(surf, _shade(glove, -55),
                           (hand[0] - gr, hand[1] + 1), max(2, gr // 2), 1)


def _facet_body(surf, pts, base, *, top_left_lift=40):
    """Fill a costume panel with sculpted shading: the body fill, a lighter
    top-left facet, a soft underside shadow, and a left-edge rim — so the
    costume reads dimensional instead of flat."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    pygame.draw.polygon(surf, base, pts)
    shade = pygame.Surface((maxx - minx + 2, maxy - miny + 2), pygame.SRCALPHA)
    band = pygame.Rect(0, (maxy - miny) * 2 // 3, maxx - minx + 2,
                       (maxy - miny) // 3 + 2)
    pygame.draw.rect(shade, (0, 0, 0, 55), band)
    shade.blit(_poly_mask(pts, minx, miny, maxx, maxy),
               (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (minx, miny))
    lit = pygame.Surface((maxx - minx + 2, maxy - miny + 2), pygame.SRCALPHA)
    lit_c = _shade(base, top_left_lift)
    pygame.draw.polygon(lit, (*lit_c, 150),
                        [(p[0] - minx, p[1] - miny) for p in pts])
    facet = pygame.Surface((maxx - minx + 2, maxy - miny + 2), pygame.SRCALPHA)
    pygame.draw.polygon(facet, (255, 255, 255, 255),
                        [(0, 0), ((maxx - minx) * 2 // 3, 0),
                         (0, (maxy - miny) * 2 // 3)])
    lit.blit(facet, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(lit, (minx, miny))
    pygame.draw.lines(surf, _shade(base, 55), False,
                      [(minx + 1, miny + 4), (minx + 1, maxy - 4)], 2)
    pygame.draw.polygon(surf, _shade(base, -65), pts, 2)


def _round_head(surf, cx, cy, r, skin, *, blush=True, white_face=False):
    """Round friendly head. Whiteface clowns get a warm IVORY base. Always
    rosy-cheeked + a top-left rim + 2px keyline."""
    base = IVORY if white_face else skin
    pygame.draw.circle(surf, _shade(base, -55), (cx, cy), r + 1)
    pygame.draw.circle(surf, base, (cx, cy), r)
    sheen = pygame.Surface((r, r), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 70), sheen.get_rect())
    surf.blit(sheen, (cx - r + 2, cy - r + 2))
    jaw = pygame.Surface((r * 2, r), pygame.SRCALPHA)
    pygame.draw.ellipse(jaw, (0, 0, 0, 35), (0, -r // 2, r * 2, r))
    surf.blit(jaw, (cx - r, cy + r // 3))
    pygame.draw.circle(surf, _shade(base, -55), (cx, cy), r, 2)
    if blush:
        for s in (-1, 1):
            pygame.draw.ellipse(surf, ROSY,
                                (cx + s * (r - 8) - 4, cy + 2, 9, 7))


def _nose(surf, cx, cy, r, color=(232, 56, 56)):
    """The signature round ball nose, always with a specular dot."""
    pygame.draw.circle(surf, _shade(color, -60), (cx, cy), r + 1)
    pygame.draw.circle(surf, color, (cx, cy), r)
    pygame.draw.circle(surf, _shade(color, 100),
                       (cx - r // 2, cy - r // 2), max(1, r // 3))


# The hero die always shows the same face so it reads as one consistent prop.
HERO_PIPS = 5

_PIP_LAYOUT = {
    1: [(0.5, 0.5)],
    2: [(0.30, 0.30), (0.70, 0.70)],
    3: [(0.28, 0.28), (0.5, 0.5), (0.72, 0.72)],
    4: [(0.30, 0.30), (0.70, 0.30), (0.30, 0.70), (0.70, 0.70)],
    5: [(0.28, 0.28), (0.72, 0.28), (0.5, 0.5), (0.28, 0.72), (0.72, 0.72)],
    6: [(0.30, 0.26), (0.70, 0.26), (0.30, 0.5), (0.70, 0.5),
        (0.30, 0.74), (0.70, 0.74)],
}


# ── the HAPPY-MEAN face kit + caps + costume + die (re-homed verbatim) ────────
MOUTH = (188, 56, 66)

# A DEEPER soft tier (opt-in, set only by the round-4 held-clown renderer) that
# pushes the friendly-mascot read further than `soft` alone: rounder approachable
# eyes (soft dark oval + a single white catch-light, ~30% less brow/lash mass) and
# a slightly narrower, softer-cornered grin. Kept module-level + default OFF so the
# ten power-up presenters and the round-3 held clown render unchanged.
_R4_SOFT = False


def _scheme_eye(surf, x, y, *, look, soft=False):
    """A BRIGHT, OPEN, lively eye that smiles — gleeful + sly, NOT droopy/weepy.
    Round-4's flat half-lidded almond still read SAD (heavy hooded down-slant
    lid + matte pupil). This rebuild opens the eye up: a tall round white sclera
    with a bright pupil + a real specular catchlight (alive, not glossy-teary),
    and the LOWER lid curved UP into the cheek (a genuine happy-squint arc) so
    the eye reads as laughing. The pupil still shoves hard toward the DIE-SIDE
    corner for the sly sidelong glance up at the floating die. NO heavy hooded
    top lid, NO down-slanted sad lid. `look` is the horizontal pupil shove
    (negative = toward the upper-left die)."""
    # The deepest (round-4) soft tier swaps the almond sclera + heavy ink lash for
    # a rounder approachable-mascot eye: a soft dark oval with a single white
    # catch-light and a much lighter lid, so the face reads Crossy-Road friendly
    # rather than circus-poster sly. Lash/brow mass is eased ~30% on this path.
    if _R4_SOFT and soft:
        er = 5                              # a round, gentle eye
        # A small white backing so the dark eye still pops off the skin, then a
        # fully ROUND soft dark eye (warm near-black, not pure ink) + a hot 1px
        # catch-light. A round disc (not the almond ellipse) reads as the
        # approachable mascot eye the brief asks for — Crossy-Road register.
        pygame.draw.circle(surf, WHITE, (x, y + 1), er + 1)
        px = x + look // 3                  # gaze nearly centred — warm + direct
        py = y + 1
        pygame.draw.circle(surf, (46, 40, 58), (px, py), er)
        pygame.draw.circle(surf, (255, 255, 255), (px - 2, py - 2), 1)
        # A whisper-thin upper lash arc only — ~30% lighter than the soft default,
        # no lower-lid crease, so the eye stays open and unguarded.
        pygame.draw.arc(surf, (96, 78, 84),
                        (x - er - 1, y - er, er * 2 + 2, er + 3),
                        math.pi * 0.18, math.pi * 0.82, 1)
        return
    # The soft read rounds the sclera toward a circle and softens the sidelong
    # shove so the eye reads round + open + friendly rather than a sly almond.
    ew, eh = (6, 6) if soft else (5, 6)
    # White sclera — a tall bright open eye. Big and round so the figure reads
    # wide-awake and delighted, never hooded or droopy.
    eye_rect = pygame.Rect(x - ew, y - eh + 2, ew * 2, eh * 2)
    pygame.draw.ellipse(surf, WHITE, eye_rect)
    # Bright pupil jammed into the DIE-SIDE corner (sidelong up-left glance) with
    # a real specular catchlight so the eye sparkles with mischief — placed top-
    # left of the pupil (lit, lively), not a watery centre tear. The soft read
    # nearly centres the pupil so the gaze is warm + direct, not sidelong-sly.
    px = x + (look // 2 if soft else look)
    py = y + 1
    pygame.draw.circle(surf, (44, 38, 60), (px, py), 4)
    pygame.draw.circle(surf, (14, 12, 22), (px, py), 4, 1)
    pygame.draw.circle(surf, (255, 255, 255), (px - 1, py - 2), 1)
    # Thin LIGHT upper lid arched UP (a happy lifted lid) — drawn as a shallow
    # up-curving arc over the top of the sclera, never a heavy hooded down-bar.
    pygame.draw.arc(surf, INK, (x - ew - 1, y - eh, ew * 2 + 2, eh + 2),
                    math.pi * 0.15, math.pi * 0.85, 2)
    # LOWER lid pushed UP into a happy-squint arc — the cheek crowding up under
    # the eye, the unmistakable "smiling eyes" cue. The art-director flagged the
    # round-5 RED eye-rim as stacking too much red into a feverish/angry look, so
    # the rim is now a SOFT NEUTRAL ink-brown crease (no rosy red), thin (1px), and
    # drawn shorter so it whispers "squint" without ringing the eye in red.
    pygame.draw.arc(surf, (118, 96, 96),
                    (x - ew + 1, y, ew * 2 - 2, eh),
                    math.pi * 1.18, math.tau * 0.92, 1)


def _cheek(surf, cx, cy, r, *, strong=False):
    """Warm cheek blush discs so the mischief always reads charming, not cold.
    Round-3 placed these high + narrow directly UNDER the inner eye, where they
    read as red TEAR streaks running down the cheek. They are now low, round and
    pushed OUTWARD onto the apple of the cheek (well below the eye/nose line) so
    they read unmistakably as a warm flush, never a tear."""
    # Softer alpha than round-5: the art-director flagged the red-stack (rimmed
    # eyes + red nose + strong blush) reading feverish/angry, so the blush is
    # eased to a gentle warm flush that supports "charming", not another red note.
    for s in (-1, 1):
        a = 140 if strong else 105
        blush = pygame.Surface((14, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(blush, (*ROSY, a), blush.get_rect())
        # Low on the cheek apple and well out toward the head edge.
        surf.blit(blush, (cx + s * (r - 5) - 7, cy + 6))


def naughty_face(surf, cx, hy, hr, *, nose_col=(232, 72, 72), variant="plain",
                 soft=False):
    """Paint the ONE locked HAPPY-with-a-MEAN-SMILE expression. The read is a
    gleeful, up-to-no-good villain GRIN — the dominant feature is a wide, open,
    upturned smile with teeth and ONE pointed fang. `variant` only layers small
    extra flavour on top of the shared recipe:

    `soft=True` warms the same grin toward FRIENDLY-CASUAL for a held-prop hero
    that wants to read welcoming rather than menacing: it drops the pointed fang
    and the red die-side dimple crease (which can read as a lip-drip at 1x), and
    lifts the smile so it sits a touch higher and rounder. Everything else (eyes,
    brows, nose, teeth, lip crescent) is shared so the figure stays on-model.
        "plain"   — the base recipe.
        "browcock"— one eyebrow cocked high (oh-really).
        "tongue"  — a tongue-tip licking the grin corner.
        "tonguecock" — both of the above.
    The whole head (face + cap) is rotated by the caller for the plotting lean,
    so the features always tilt WITH the body rather than floating level."""
    ex = max(6, hr // 2)
    # Pupils glance sidelong toward the die (upper-LEFT) — gleefully eyeing it.
    look = -3
    _cheek(surf, cx, hy + 5, hr, strong=True)

    cock_left = variant in ("browcock", "tonguecock")
    for s in (-1, 1):
        exx = cx + s * ex
        _scheme_eye(surf, exx, hy, look=look, soft=soft)
        # PLAYFUL RAISED brow — the cheeky-arch read from tile #1, applied to all
        # ten. The art-director flagged round-5 as ANGRY: the inner (nose-side)
        # ends had swung DOWN toward the nose into the universal anger "V". The
        # fix INVERTS that: the INNER end now rides HIGH (lifted, arched) and the
        # outer end tucks slightly lower/out — a raised, surprised, up-to-no-good
        # arch that can never knit into a frown. The whole brow also floats a row
        # higher above the open eye so it reads as a lifted "oh-really" smirk-brow.
        # A CLEAN raised brow: the inner (nose-side) end sits clearly HIGHER than
        # the outer end — a single straight up-and-in line that reads as a lifted,
        # quizzical "oh-really" arch and can NEVER knit into the angry inner-down V.
        # Drawn thin (2px) in a soft warm brown (not heavy black INK) so it stops
        # dominating the face into a scowl (art-director: reduce brow weight ~30%).
        inner = (exx - s * 2, hy - 20)       # inner end HIGH (anti-anger)
        outer = (exx + s * 9, hy - 12)       # outer end LOW — a clear 8px raise
        cock = cock_left and s < 0
        if cock:
            inner = (inner[0], inner[1] - 3)  # cocked brow rides even higher
        if _R4_SOFT and soft:
            # ~30% less brow mass for the friendly-mascot read: a shorter, thinner,
            # paler arch that reads as a gentle lifted brow, not a heavy stroke.
            inner = (exx - s * 1, hy - 19)
            outer = (exx + s * 7, hy - 13)
            pygame.draw.line(surf, (120, 102, 104), inner, outer, 1)
        else:
            pygame.draw.line(surf, (76, 56, 60), inner, outer, 2)

    # Big red ball nose — SHRUNK and seated UP between the eyes so it stops
    # crowding the grin below (round-4's r=6 nose at hy+6 sat on top of the
    # mouth). Smaller radius + lifted so the wide grin owns the lower face.
    _nose(surf, cx, hy + 3, 4, nose_col)

    # THE DOMINANT FEATURE: a WIDE, upturned, OPEN happy GRIN with a row of teeth
    # and one pointed fang for the mean edge. Built as a filled mouth shape: a
    # dark open interior arc bounded by an up-curved lip, the die-side (LEFT)
    # corner pulled highest so the grin still reads lopsided/sly. The grin is
    # large — it spans most of the lower face and pushes the cheeks up.
    # ~15% narrower on the deepest soft tier so the grin loses the wide jack-o'-
    # lantern span and reads as a warm, contained smile.
    mw = 9 if (_R4_SOFT and soft) else 11     # half-width of the grin
    # The soft read seats the grin a touch HIGHER so the smile lifts into a
    # rounder, friendlier curve rather than a low villain leer.
    my = hy + (10 if soft else 12)            # vertical seat of the mouth line
    # The smile baseline: corners up, centre dropped — a fat up-curving crescent.
    # The r4-soft tier rounds BOTH corners up evenly (no sly lopsided pull) so the
    # mouth reads as a symmetric friendly smile.
    if _R4_SOFT and soft:
        # Both corners lifted evenly AND a touch higher than the soft default, so
        # the grin curls up into a warm contained smile rather than a wide leer —
        # dropping the last of the jack-o'-lantern read.
        l_corner = (cx - mw - 1, my - 4)
        r_corner = (cx + mw, my - 4)
    else:
        l_corner = (cx - mw - 1, my - 2)      # die-side (LEFT) corner, highest
        r_corner = (cx + mw, my)              # far (RIGHT) corner, a touch lower
    bottom = (cx, my + 8)                     # open-mouth low point
    # Filled open mouth interior (dark warm throat) so it reads OPEN, not a line.
    mouth_poly = [l_corner, (cx - 5, my + 1), (cx + 5, my + 1), r_corner,
                  (cx + 6, my + 4), bottom, (cx - 6, my + 4)]
    pygame.draw.polygon(surf, (120, 30, 42), mouth_poly)
    # Top row of TEETH: a bright white band along the top of the open grin.
    teeth = [l_corner, (cx - 5, my), (cx + 5, my), r_corner,
             (cx + 5, my + 3), (cx - 5, my + 3)]
    pygame.draw.polygon(surf, (250, 248, 240), teeth)
    pygame.draw.polygon(surf, _shade((250, 248, 240), -70), teeth, 1)
    # Tooth separators so the white band reads as individual teeth.
    for tx in range(-2, 3):
        gx = cx + tx * 4
        pygame.draw.line(surf, _shade((250, 248, 240), -70),
                         (gx, my), (gx, my + 3), 1)
    # ONE pointed FANG dropping below the teeth row on the die-side (LEFT) for
    # the "mean" edge — a small white triangle hanging into the dark mouth. The
    # soft read drops the fang entirely so the grin is purely friendly.
    if not soft:
        fang = [(cx - 5, my + 3), (cx - 1, my + 3), (cx - 3, my + 7)]
        pygame.draw.polygon(surf, (252, 250, 244), fang)
        pygame.draw.polygon(surf, _shade((252, 250, 244), -70), fang, 1)
    # The LIP line wrapping the grin — a single SMOOTH up-curving crescent (a
    # parabola: corners high, centre dipped) so it reads as one clean happy smile
    # at 1x, never a jagged sawtooth/snarl. Corners flick UP for the lopsided sly
    # accent (die-side corner highest).
    lip = []
    for k in range(13):
        t = k / 12.0
        lx = l_corner[0] - 2 + (r_corner[0] + 2 - (l_corner[0] - 2)) * t
        ly = (l_corner[1] - 3) + ((r_corner[1] - 2) - (l_corner[1] - 3)) * t \
            + (1.0 - (2.0 * t - 1.0) ** 2) * 9.0
        lip.append((lx, ly))
    pygame.draw.lines(surf, MOUTH, False, lip, 3)
    # Cheek dimple creases on BOTH sides where the grin pushes the cheeks up —
    # the die-side (LEFT) one deeper for the lopsided sly accent. The deep RED
    # die-side crease can read as a lip-DRIP at 1x, so the soft read drops both
    # red creases for a clean, friendly smile corner.
    if not soft:
        pygame.draw.line(surf, _shade(nose_col, -40),
                         (l_corner[0] - 2, l_corner[1] - 1),
                         (l_corner[0] - 4, l_corner[1] + 4), 2)
        pygame.draw.line(surf, _shade(nose_col, -40),
                         (r_corner[0] + 2, r_corner[1]),
                         (r_corner[0] + 3, r_corner[1] + 3), 1)

    if variant in ("tongue", "tonguecock"):
        # Tongue tip licking out the raised (die-side / LEFT) grin corner — a
        # cheeky relish. Round-5's blob read as a smudge/drip at 1x; this is a
        # tighter, smaller rounded tip seated INSIDE the grin corner (not hanging
        # below the lip), with a crisp dark outline + a centre crease so it reads
        # as a tongue, not a drop.
        tx0 = l_corner[0] - 2
        ty0 = my + 2
        tongue = pygame.Rect(tx0, ty0, 6, 5)
        pygame.draw.ellipse(surf, (228, 110, 124), tongue)
        pygame.draw.ellipse(surf, _shade((228, 110, 124), -60), tongue, 1)
        pygame.draw.line(surf, _shade((228, 110, 124), -60),
                         (tx0 + 3, ty0 + 1), (tx0 + 3, ty0 + 4), 1)


# ── belled-cap kit ────────────────────────────────────────────────────────────
# The fool's cap is the jester's loudest silhouette cue. Each variation owns a
# distinct cap shape, every one finished with belled tips (a lit specular on
# each bell so they read as gold spheres, not flat discs).

def _bell(surf, x, y, r=4, col=(245, 240, 200)):
    pygame.draw.circle(surf, _shade(col, -55), (x, y), r + 1)
    pygame.draw.circle(surf, col, (x, y), r)
    pygame.draw.circle(surf, _shade(col, 80), (x - 1, y - 1), max(1, r // 2))


def _cap_point(surf, cx, base_y, hr, dx, dy, col, *, span=16):
    """One drooping cap point as a triangle from the head crown to a belled
    tip, with a lit top-left facet + dark keyline."""
    bx, by = cx + dx, base_y + dy
    pts = [(cx - span, base_y + 2), (cx + span, base_y + 2), (bx, by)]
    pygame.draw.polygon(surf, col, pts)
    pygame.draw.polygon(surf, _shade(col, 50),
                        [(cx - span, base_y + 2), (cx + span // 2, base_y + 2),
                         (bx, by)])
    pygame.draw.polygon(surf, _shade(col, -60), pts, 2)
    _bell(surf, bx, by)


def cap_three_point(surf, cx, base_y, hr, cols):
    """Classic drooping three-point belled cap — the reliable jester read."""
    a, b, c = cols[0], cols[1], cols[2]
    _cap_point(surf, cx, base_y, hr, -28, -26, a)
    _cap_point(surf, cx, base_y, hr, 2, -40, b)
    _cap_point(surf, cx, base_y, hr, 30, -24, c)


def cap_four_point(surf, cx, base_y, hr, cols):
    """Four belled points SPLAYED outward so the cluster reads as a floppy fool's
    cap, never an upright king's crown (round-2 #2 still read royal). The two
    outer points flop hard down-and-OUT past the head edges and the two inner
    points lean low and apart — a wide drooping fan, not vertical spikes."""
    a, b, c, _d = cols
    # Outer pair flops WAY out past the head silhouette and drops low; inner pair
    # leans outward too so nothing stands upright in the middle.
    _cap_point(surf, cx, base_y, hr, -42, -6, a, span=14)
    _cap_point(surf, cx, base_y, hr, 42, -4, a, span=14)
    _cap_point(surf, cx, base_y, hr, -16, -28, b, span=14)
    _cap_point(surf, cx, base_y, hr, 16, -26, c, span=14)


def cap_donkey(surf, cx, base_y, hr, cols):
    """A TRUE donkey-ear cap: two tall floppy ears (rounded, drooping outward at
    the tips), not a single cone. A low band ties them to the crown, each ear
    bell-tipped."""
    a, b = cols[0], cols[1]
    # Each ear is a long rounded lobe that bows outward then flops back with a
    # bell — built from a filled polygon spine + a rounded cap so it reads soft
    # and floppy, not as a stiff spike.
    for s, col in ((-1, a), (1, b)):
        tipx, tipy = cx + s * 30, base_y - 50
        spine = [(cx + s * 4, base_y - 2), (cx + s * 16, base_y - 2),
                 (cx + s * 26, base_y - 26), (tipx, tipy),
                 (cx + s * 22, base_y - 44), (cx + s * 10, base_y - 18)]
        pygame.draw.polygon(surf, col, spine)
        pygame.draw.polygon(surf, _shade(col, 45),
                            [(cx + s * 4, base_y - 2),
                             (cx + s * 12, base_y - 14),
                             (cx + s * 10, base_y - 18)])
        pygame.draw.polygon(surf, _shade(col, -60), spine, 2)
        # Soft rounded ear tip + an inner-ear lighter lobe.
        pygame.draw.circle(surf, _shade(col, 30), (tipx, tipy), 5)
        _bell(surf, tipx, tipy, r=3)
    # Low band cap joining the ears across the crown.
    pygame.draw.arc(surf, _shade(a, -20), (cx - 20, base_y - 16, 40, 24),
                    math.pi, math.tau, 5)
    pygame.draw.arc(surf, _shade(a, 35), (cx - 17, base_y - 14, 34, 18),
                    math.pi, math.tau, 2)


def cap_coxcomb(surf, cx, base_y, hr, cols):
    """Rooster-crest coxcomb: a row of scalloped lobes ATTACHED to the scalp by a
    base band along the hairline. Round-2 read as detached floating spheres; now
    a filled base band tucks under the lobes and the rearmost lobe sits BEHIND the
    head crown so the crest reads as growing out of the head, not hovering."""
    a, b = cols[0], cols[1]
    # Base band hugging the crown — a filled wedge along the hairline the lobes
    # all root into, so no lobe floats free of the head.
    band = [(cx - 24, base_y + 2), (cx - 14, base_y - 12),
            (cx + 2, base_y - 16), (cx + 18, base_y - 10),
            (cx + 22, base_y + 2)]
    pygame.draw.polygon(surf, _shade(a, -30), band)
    pygame.draw.polygon(surf, _shade(a, -70), band, 2)
    lobes = [(-22, -14), (-9, -28), (5, -32), (18, -20)]
    for i, (dx, dy) in enumerate(lobes):
        col = a if i % 2 == 0 else b
        bx, by = cx + dx, base_y + dy
        pygame.draw.circle(surf, _shade(col, -55), (bx, by), 9)
        pygame.draw.circle(surf, col, (bx, by), 8)
        pygame.draw.circle(surf, _shade(col, 55), (bx - 2, by - 2), 3)
    _bell(surf, cx + 22, base_y - 12)


def cap_hood(surf, cx, base_y, hr, cols):
    """Curled close hood with a single long forward-curling belled point — a
    real curled-bell hood (one of the featured cap shapes)."""
    a = cols[0]
    pygame.draw.ellipse(surf, _shade(a, -30), (cx - hr - 1, base_y - 18,
                                               hr * 2 + 2, 26))
    pygame.draw.ellipse(surf, a, (cx - hr, base_y - 18, hr * 2, 24))
    pygame.draw.arc(surf, _shade(a, 45), (cx - hr + 3, base_y - 16, hr, 14),
                    math.pi, math.tau, 2)
    # Long forward-curling point sweeping right then dropping a bell.
    pts = [(cx - 6, base_y - 14), (cx + 8, base_y - 16),
           (cx + 30, base_y - 30), (cx + 24, base_y - 14),
           (cx + 10, base_y - 6)]
    pygame.draw.polygon(surf, _shade(a, 20), pts)
    pygame.draw.polygon(surf, _shade(a, -55), pts, 2)
    _bell(surf, cx + 30, base_y - 30)


def cap_imp_hood(surf, cx, base_y, hr, cols):
    """The single surviving horned hood — but IMPISH, not menacing: the horns
    are rounded into soft bell-tipped NUBS (not sharp spikes) and the palette
    is warmed off pure black toward charcoal-plum by the caller. Reads playful-
    devilish, the cheeky kind."""
    a, b = cols[0], cols[1]
    pygame.draw.ellipse(surf, _shade(a, -30), (cx - hr - 1, base_y - 12,
                                               hr * 2 + 2, 20))
    pygame.draw.ellipse(surf, a, (cx - hr, base_y - 12, hr * 2, 18))
    pygame.draw.arc(surf, _shade(a, 40), (cx - hr + 3, base_y - 10, hr, 12),
                    math.pi, math.tau, 2)
    # Short fat rounded nubs that curl gently outward — drawn as stubby lobes
    # plus a soft bell on the tip so they read impish, not horned-menace.
    for s, col in ((-1, a), (1, b)):
        bx, by = cx + s * 18, base_y - 22
        pygame.draw.circle(surf, _shade(col, -45), (cx + s * 13, base_y - 8), 7)
        pygame.draw.circle(surf, col, (cx + s * 13, base_y - 8), 6)
        pygame.draw.circle(surf, _shade(col, -45), (bx, by), 6)
        pygame.draw.circle(surf, col, (bx, by), 5)
        pygame.draw.circle(surf, _shade(col, 55),
                           (cx + s * 11, base_y - 10), 2)
        _bell(surf, bx, by, r=3)


# ── collar kit ────────────────────────────────────────────────────────────────
# Round-1 critique: lift EVERY tile to the costume standard — a scalloped /
# pointed collar with a bell at each point, on all ten. The two collar styles
# below both finish with a bell per point/lobe; the builder gives every jester
# one of them (no bare necks).

def _collar_belled(surf, cx, neck_y, gold, n=5, tilt=0):
    """Drooping POINTED collar: a fan of dagged triangle points hanging off the
    neck, a bell at the tip of each point. `tilt` shears the fan with the body
    lean so the collar hangs with the shoulders, not bolt-level."""
    span = (n - 1) / 2
    for i in range(n):
        s = i - span
        tx = int(cx + s * 13 + tilt * 0.4)
        ty = neck_y + 4 + int(abs(s) * 1.5)  # outer points hang a touch lower
        _poly(surf, gold, [(cx + int(tilt), neck_y), (tx - 6, ty + 15),
                           (tx + 6, ty + 15)], oc=_shade(gold, -60))
        # Lit inner facet per point for the per-panel shaded read.
        _poly(surf, _shade(gold, 45),
              [(cx + int(tilt), neck_y), (tx - 6, ty + 15), (tx, ty + 8)],
              oc=False)
        _bell(surf, tx, ty + 16, r=3, col=(240, 235, 200))


def _collar_scalloped(surf, cx, neck_y, col, r=22, lobes=9, tilt=0):
    """A scalloped ruff-style collar: a row of overlapping lobes ringing the
    neck with lit tops + a small dangling bell at each outer edge. `tilt`
    shears the ruff so it follows the leaning shoulders."""
    for i in range(lobes):
        t = i / (lobes - 1)
        lx = int(cx - r + 2 * r * t + tilt * 0.5)
        ly = int(neck_y + 5 + math.sin(t * math.pi) * -3 + (t - 0.5) * tilt * 0.4)
        rad = 8
        pygame.draw.circle(surf, _shade(col, -50), (lx, ly), rad)
        pygame.draw.circle(surf, col, (lx, ly), rad - 1)
        pygame.draw.circle(surf, _shade(col, 55), (lx - 2, ly - 2), 3)
    for s in (-1, 1):
        _bell(surf, int(cx + s * (r + 2) + tilt * 0.5), neck_y + 8, r=3,
              col=(240, 235, 200))


def _shoulder_pom(surf, x, y, gold, *, lobes=3):
    """A small belled POM / epaulet tuft seated right where an arm meets the
    torso, to BRIDGE the shoulder seam on the narrower belled-collar tiles whose
    raised shoulder is otherwise exposed (the scalloped-ruff tiles already drape
    over the joint and need none). Built from the sheet's own ornament
    vocabulary — a cluster of soft gold lobes crowned by a lit bell — so it reads
    native to the costume's gold-accent / collar-bell language, not pasted on."""
    # A fan of small gold lobes packed over the joint so the cluster physically
    # overlaps both the upper arm and the torso edge, closing the visible seam.
    spread = (lobes - 1) / 2
    for i in range(lobes):
        s = i - spread
        lx = int(x + s * 5)
        ly = int(y + abs(s) * 2)            # outer lobes ride a touch lower
        pygame.draw.circle(surf, _shade(gold, -55), (lx, ly), 6)
        pygame.draw.circle(surf, gold, (lx, ly), 5)
        pygame.draw.circle(surf, _shade(gold, 70), (lx - 2, ly - 2), 2)
    # Crown the tuft with a lit cream bell, matching the collar/cap bell style.
    _bell(surf, x, y - 4, r=3, col=(245, 240, 200))


# ── belled curled-toe jester shoes + thumb-divided mitts ─────────────────────

def _jester_shoes(surf, cx, feet_y, sep, length, color, toe, *, lean=0):
    """Curled-toe pointed jester shoes with a bell on each toe — the costume
    standard on all ten (round-1 had plain shoes). `lean` cocks the stance so
    the weight reads on one leg."""
    for s in (-1, 1):
        bx = cx + s * sep + (lean if s > 0 else lean // 2)
        # Sole as a rounded wedge.
        sole = pygame.Rect(0, 0, length, 14)
        if s < 0:
            sole.topright = (bx + length // 3, feet_y)
        else:
            sole.topleft = (bx - length // 3, feet_y)
        pygame.draw.ellipse(surf, _shade(color, -55), sole)
        pygame.draw.ellipse(surf, color, sole.inflate(-3, -3))
        # Curled pointed toe sweeping up and out, ending in a bell.
        toe_base = (sole.right - 4, sole.centery) if s > 0 else (sole.left + 4,
                                                                 sole.centery)
        tipx = toe_base[0] + s * 11
        tipy = toe_base[1] - 12
        curl = [(toe_base[0], toe_base[1] + 4), (toe_base[0], toe_base[1] - 4),
                (toe_base[0] + s * 7, toe_base[1] - 9), (tipx, tipy)]
        pygame.draw.polygon(surf, toe, curl)
        pygame.draw.polygon(surf, _shade(toe, -55), curl, 2)
        _bell(surf, tipx, tipy, r=3)


def _mitt_thumb(surf, hand, gr, glove, *, side):
    """Add a single thumb-dividing line so the white mitt reads as a hand. The
    `_arm` glove already drew the round mitt; we just carve the thumb."""
    hx, hy = hand
    # Thumb nub on the inner side + a divider line so it reads as fingers-vs-
    # thumb rather than a featureless ball.
    tx = hx - side * (gr - 1)
    pygame.draw.circle(surf, glove, (tx, hy + 1), max(2, gr // 2))
    pygame.draw.circle(surf, _shade(glove, -55), (tx, hy + 1), max(2, gr // 2), 1)
    pygame.draw.line(surf, _shade(glove, -55),
                     (hx - side * gr // 2, hy - gr + 2),
                     (hx - side * gr // 3, hy + gr - 2), 1)


# ── the unified jester builder (fixed pose + plotting lean) ───────────────────
# Every variation funnels through ONE builder so the MIRRORED POSE is literally
# identical across all ten: die high in the upper-LEFT, LEFT arm raised POINTING
# UP at the die, RIGHT arm hanging down with a bowed mitt. On top of that pose, a shared
# "plotting" LEAN breaks the round-1 bolt-upright symmetry: the head tilts ~5°,
# one shoulder drops, the hip cocks, weight rests on one leg.

def build_jester(surf, cx, feet_y, hand_up, *, dark, light, gold,
                 cap_fn, motif, collar, variant, skin=(255, 209, 169),
                 nose_col=(232, 72, 72), imp=False, shoulder_orn=False,
                 collar_in_gold=False, soft_face=False):
    """Draw ONE chunky court jester in the fixed mirrored presenting pose with a
    plotting body lean. `variant` selects the small face flavour layered on the
    shared naughty recipe. `imp` is a spec marker for the single horned-hood
    variant — its impish read is carried by the warmed charcoal-plum palette in
    the spec plus the soft bell-nub `cap_imp_hood`, so it needs no extra branch.

    Build bias: a SHORTER, ROUNDER chibi proportion (round-1 #1/#4 read best
    small; the lanky long-legged tiles were reined in)."""
    _ = imp  # palette/cap already encode the impish read; kept for spec clarity
    # COMMITTED plotting lean (round-2 still read at-attention on most figures).
    # The whole figure shifts weight onto the die-side (LEFT) leg: the hip cocks
    # hard toward the die, the die-side shoulder DROPS 7px, the OTHER hip rides
    # up, the trailing (right) knee bends inward, and the head cocks. This is now
    # a clear contrapposto plot-stance, not a gentle nudge.
    hip_dx = -6          # hip cocked toward the die side (harder than round-2)
    head_tilt = -8       # degrees; head cocks toward the die
    drop = 7             # the die-side (left) shoulder drops a full 7px

    hip_y = feet_y - 84  # shorter build than round-1's 92
    hip_cx = cx + hip_dx

    # Curled-toe belled shoes, weight planted on the LEFT (die-side) leg, the
    # trailing RIGHT foot set back and turned out.
    _jester_shoes(surf, cx, feet_y, 15, 24, _shade(dark, -10),
                  _shade(gold, 10), lean=5)
    # Two-tone HARLEQUIN hose. The weight leg (LEFT) is planted nearly straight
    # under the cocked hip; the trailing (RIGHT) leg sets back with a BENT KNEE
    # (a mid-point kicked inward) so the stance reads as weight-shifted, never a
    # symmetric T. The hip anchors differ in height to sell the cocked pelvis.
    _harlequin_leg(surf, (hip_cx - 9, hip_y + 2), (cx - 12, feet_y - 8), 12,
                   light, dark)
    _harlequin_leg(surf, (hip_cx + 11, hip_y - 2), (cx + 15, feet_y - 8), 11,
                   dark, light, knee=(cx + 4, hip_y + 26))

    neck_y = hip_y - 50
    _draw_costume(surf, hip_cx, hip_y, dark, light, gold, motif, lean=4)

    # POSE — the hard requirement, now with the lean baked in. The LEFT (die-
    # side) shoulder DROPS; its arm reaches up and the mitt POINTS diagonally up
    # at the airborne die. The RIGHT arm hangs down with a slight outward BOW so
    # both hands read in silhouette.
    l_sh = (hip_cx - 25, hip_y - 46 + drop)
    r_sh = (hip_cx + 25, hip_y - 50)
    _arm(surf, l_sh, hand_up, 8, dark, up=True)
    # Right arm bows outward to a visible down mitt.
    r_hand = (hip_cx + 34, hip_y - 4)
    _arm(surf, r_sh, r_hand, 8, light)
    _mitt_thumb(surf, r_hand, 7, (250, 250, 252), side=-1)

    # Belled shoulder POMS — drawn AFTER the arms so they overlap the arm/torso
    # junction and close the exposed seam. Only the narrower belled-collar tiles
    # need this; the scalloped ruff already drapes over the joint. The die-side
    # (LEFT, raised) shoulder is the one whose seam shows, so its pom is mirrored
    # on the RIGHT shoulder for a balanced, intentional epaulet pair.
    if shoulder_orn:
        _shoulder_pom(surf, l_sh[0] + 4, l_sh[1] + 2, gold)
        _shoulder_pom(surf, r_sh[0] - 4, r_sh[1] + 2, gold)

    # Collar — every jester gets a belled, pointed/scalloped collar (no bare
    # necks), sheared to follow the leaning shoulders.
    if collar == "scalloped":
        # The scalloped ruff lobes are normally the costume `light` colour; when
        # `collar_in_gold` is set, recolour every lobe to the GOLD of the cap so
        # the "scarf of circles" matches the hat's bells.
        ruff_col = _shade(gold, 6) if collar_in_gold else _shade(light, 10)
        _collar_scalloped(surf, hip_cx, neck_y, ruff_col, tilt=4)
    else:
        _collar_belled(surf, hip_cx, neck_y, gold, tilt=4)

    hr = 22
    # The head sits on the neck but tilts toward the die. We draw the head +
    # cap + face onto a small surface and rotate the whole cluster so the tilt
    # is real, not just shoved features. The neck shifts toward the dropped
    # (die-side) shoulder so the head sits OVER the weight leg, not centred.
    head_cx = hip_cx - 4
    hy_center = neck_y - hr
    cap_cols = (dark, light, gold, dark)
    _draw_tilted_head(surf, head_cx, hy_center, hr, skin, cap_fn, cap_cols,
                      variant, nose_col, head_tilt, soft_face=soft_face)


def _draw_tilted_head(surf, cx, cy, hr, skin, cap_fn, cap_cols, variant,
                      nose_col, tilt_deg, *, soft_face=False):
    """Compose head + cap + naughty face on a scratch surface and rotate it by
    `tilt_deg` so the whole head cocks with the plotting lean. Drawing onto a
    padded scratch surface keeps the rotation clean and centred on the face."""
    pad = 70
    scratch = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    sx, sy = pad, pad
    _round_head(scratch, sx, sy, hr, skin, blush=False)
    # Cap BEFORE the face so droops never cover the eyes. Seat the cap base ~7px
    # DOWN into the crown so it hugs the skull instead of perching on top and
    # leaving a bald forehead gap; still clears the eyes for every cap style.
    cap_fn(scratch, sx, sy - hr + 7, hr, cap_cols)
    naughty_face(scratch, sx, sy, hr, nose_col=nose_col, variant=variant,
                 soft=soft_face)
    rot = pygame.transform.rotate(scratch, tilt_deg)
    surf.blit(rot, (cx - rot.get_width() // 2, cy - rot.get_height() // 2))


def _harlequin_leg(surf, hip, ankle, w, upper, lower, *, knee=None):
    """One two-tone harlequin leg: an upper band in `upper`, a lower band in
    `lower`, with a rounded cuff + a top-left rim. Replaces round-1's solid
    single-colour stick legs. Pass `knee` to BEND the leg at an explicit joint
    (the trailing weight-shifted leg) instead of running it straight."""
    if knee is not None:
        midx, midy = knee
    else:
        midx = (hip[0] + ankle[0]) // 2
        midy = (hip[1] + ankle[1]) // 2
    pygame.draw.line(surf, _shade(upper, -50), hip, (midx, midy), w + 3)
    pygame.draw.line(surf, _shade(lower, -50), (midx, midy), ankle, w + 3)
    pygame.draw.line(surf, upper, hip, (midx, midy), w)
    pygame.draw.line(surf, lower, (midx, midy), ankle, w)
    # Top-left rim on the planted (upper) band.
    pygame.draw.line(surf, _shade(upper, 35), (hip[0] - 1, hip[1]),
                     (midx - 1, midy), max(1, w // 3))
    # Banding seam ring + ankle cuff.
    pygame.draw.circle(surf, _shade(lower, -30), (midx, midy), w // 2 + 1)
    pygame.draw.circle(surf, _shade(lower, -40), ankle, w // 2 + 2)


def _draw_costume(surf, cx, hip_y, dark, light, gold, motif, *, lean=0):
    """The torso, varied by motif. Every motif now carries per-panel costume
    shading (a darker tone down one side of each panel + a lighter highlight
    strip) via `_facet_body`, plus a faint extra side-shadow band so the round-1
    flat blocks read sculpted. `lean` skews the silhouette slightly."""
    seam = (250, 248, 235)
    top = hip_y - 50
    lx = lean  # shoulder offset from the lean

    def _side_shadow(pts, side):
        """Darken one side of a panel so each panel reads dimensional."""
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
        band = pygame.Surface((maxx - minx + 2, maxy - miny + 2),
                              pygame.SRCALPHA)
        m = pygame.Surface(band.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(m, (255, 255, 255, 255),
                            [(p[0] - minx, p[1] - miny) for p in pts])
        w = maxx - minx
        if side < 0:
            rect = pygame.Rect(0, 0, w // 3 + 2, maxy - miny + 2)
        else:
            rect = pygame.Rect(w * 2 // 3, 0, w // 3 + 2, maxy - miny + 2)
        pygame.draw.rect(band, (0, 0, 0, 60), rect)
        band.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(band, (minx, miny))

    if motif == "split":
        left = [(cx - 28, hip_y + 10), (cx, hip_y + 10),
                (cx + lx, top), (cx - 18 + lx, top)]
        right = [(cx, hip_y + 10), (cx + 28, hip_y + 10),
                 (cx + 18 + lx, top), (cx + lx, top)]
        _facet_body(surf, left, light)
        _side_shadow(left, -1)
        _facet_body(surf, right, dark)
        _side_shadow(right, 1)
        pygame.draw.line(surf, seam, (cx + lx, top + 2), (cx, hip_y + 8), 2)
    elif motif == "quartered":
        midy = (top + hip_y + 10) // 2
        quads = [((cx - 28, hip_y + 10), (cx, hip_y + 10), (cx, midy),
                  (cx - 23, midy), dark, -1),
                 ((cx, hip_y + 10), (cx + 28, hip_y + 10), (cx + 23, midy),
                  (cx, midy), light, 1),
                 ((cx - 23, midy), (cx, midy), (cx + lx, top),
                  (cx - 18 + lx, top), light, -1),
                 ((cx, midy), (cx + 23, midy), (cx + 18 + lx, top),
                  (cx + lx, top), dark, 1)]
        for *pts, col, side in quads:
            _facet_body(surf, list(pts), col)
            _side_shadow(list(pts), side)
        pygame.draw.line(surf, seam, (cx + lx, top + 2), (cx, hip_y + 8), 2)
        pygame.draw.line(surf, seam, (cx - 25, midy), (cx + 25, midy), 2)
    elif motif == "panels":
        base = [(cx - 28, hip_y + 10), (cx + 28, hip_y + 10),
                (cx + 18 + lx, top), (cx - 18 + lx, top)]
        _facet_body(surf, base, dark)
        _side_shadow(base, 1)
        for i in range(-2, 3, 2):
            px = cx + i * 11 + lx // 2
            pygame.draw.polygon(surf, light,
                                [(px - 4, hip_y + 9), (px + 4, hip_y + 9),
                                 (px + 3, top + 1), (px - 3, top + 1)])
            # Highlight strip + shadow edge per stripe panel.
            pygame.draw.line(surf, _shade(light, 45), (px - 3, hip_y + 8),
                             (px - 2, top + 2), 1)
            pygame.draw.line(surf, _shade(light, -45), (px + 3, hip_y + 8),
                             (px + 2, top + 2), 1)
    else:  # "scalloped" hem split body
        left = [(cx - 28, hip_y + 6), (cx, hip_y + 6),
                (cx + lx, top), (cx - 18 + lx, top)]
        right = [(cx, hip_y + 6), (cx + 28, hip_y + 6),
                 (cx + 18 + lx, top), (cx + lx, top)]
        _facet_body(surf, left, dark)
        _side_shadow(left, -1)
        _facet_body(surf, right, light)
        _side_shadow(right, 1)
        pygame.draw.line(surf, seam, (cx + lx, top + 2), (cx, hip_y + 6), 2)
        for i in range(-3, 4):
            hx = cx + i * 8
            col = light if (i + hip_y) % 2 else dark
            pygame.draw.circle(surf, _shade(col, -30), (hx, hip_y + 7), 5)
            pygame.draw.circle(surf, col, (hx, hip_y + 7), 4)
    # Gold belt buttons along the waist on every motif.
    for i in range(7):
        bx = cx - 21 + i * 7
        pygame.draw.circle(surf, _shade(gold, -55), (bx, hip_y + 6), 3)
        pygame.draw.circle(surf, gold, (bx, hip_y + 6), 3)
        pygame.draw.circle(surf, _shade(gold, 70), (bx - 1, hip_y + 5), 1)


# ── the airborne power-up DIE (3D cube + real yellow aura) ───────────────────
# A 3D isometric cube in a large PULSING YELLOW power-up aura, floating high in
# the upper-left sky. The aura is an explicit alpha-blended near-white→yellow→
# amber halo (so the hue survives the pale day sky) topped by a light additive
# bloom + orbiting sparkles, reading as a magical takeable pickup; the LEFT arm
# points up at it. No cast shadow / no under-die contact-glow (it is airborne).

def _aura_surface(radius, breathe):
    """Build a REAL layered power-up halo as a single ALPHA-blended disc: a hot
    near-WHITE core → bright YELLOW → warm AMBER falloff drawn as concentric
    rings. The art-director flagged the round-5 BLEND_ADD-only aura as effectively
    absent — additive layers on the pale day sky just washed toward white and the
    yellow hue vanished at 1x. Alpha-blending these explicit colour stops keeps
    the YELLOW hue intact against a bright sky, AND the bright near-white core
    means it reads as a glowing object on VALUE (so it survives at night + reads
    colourblind-safe). A light additive bloom is layered on top by the caller for
    the extra glow pop. Colour stops by normalised radius t (0=core, 1=edge)."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    # (t_outer, colour, alpha) stops, drawn large→small so inner overpaints.
    stops = [
        (1.00, (255, 174, 26), 0),                # amber edge fades to nothing
        (0.84, (255, 188, 36), 130),              # amber body
        (0.60, (255, 206, 46), 215),              # SATURATED bright yellow (dominant)
        (0.36, (255, 224, 78), 245),              # bright yellow
        (0.17, (255, 242, 140), 255),             # hot pale-YELLOW core (NOT white)
    ]
    for t_out, col, a_in in stops:
        r = max(1, int(radius * t_out))
        # Per-stop soft falloff so each band feathers into the next, never a hard
        # disc edge. Brightens with the breathe pulse so the whole halo pulses.
        steps = max(3, r // 4)
        for k in range(steps):
            rr = int(r * (1 - k / steps))
            if rr < 1:
                break
            a = int((a_in * (k / steps) ** 0.4))
            a = min(255, int(a * (0.78 + 0.22 * breathe)))
            pygame.draw.circle(s, (*col, a), (c, c), rr)
    return s


def draw_cupped_die(surf, cx, base_y, pulse, *, show_inset=False):
    cy = int(base_y + math.sin(pulse * 1.1) * 3)
    size = 40

    # A bright, large, PULSING YELLOW power-up AURA behind the airborne die so it
    # unmistakably reads as a magical pickup floating in the sky (not a held
    # prop). Built as an explicit alpha-blended near-white→yellow→amber halo so
    # the yellow hue + bright core both survive the pale day sky (round-5's pure
    # BLEND_ADD washed to white and the signal vanished), at ~1.8x the die's
    # footprint, with a light additive bloom on top for the glow pop. The whole
    # halo breathes with the bob `pulse`. The under-die contact-glow is GONE (the
    # die is airborne, no cupping mitt beneath it).
    breathe = 0.5 + 0.5 * math.sin(pulse * 1.3)
    pr = 1.0 + 0.10 * breathe                      # radius pulse
    aura_r = int(50 * pr)                          # ~2.4x the ~42px die footprint
    aura = _aura_surface(aura_r, breathe)
    surf.blit(aura, (cx - aura_r - 1, cy - aura_r - 1))
    # A SMALL, tight additive core bloom only — lifts the core so it reads as
    # EMITTING light without washing the broad yellow halo to flat white on the
    # pale day sky (round-5/6's big additive bloom was the white-out culprit).
    blit_glow(surf, cx, cy, int(13 * pr), (255, 236, 110),
              alpha=55 + int(30 * breathe))

    # The 3D isometric cube prop, identical across all ten.
    _draw_die_face_noshadow(surf, cx, cy, size, pips=HERO_PIPS)

    if show_inset:
        ins = 24
        ix, iy = cx + 40, cy - 36
        for k in range(4):
            t = k / 4
            ax = int(cx + (ix - cx) * t)
            ay = int(cy + (iy - cy) * t) - int(9 * math.sin(t * math.pi))
            pygame.draw.circle(surf, (250, 225, 150), (ax, ay), max(1, 3 - k))
        _draw_die_face_noshadow(surf, ix, iy, ins, number=27,
                                body=(255, 246, 224), pip_col=(190, 70, 40))

    for i in range(4):
        a = i * math.tau / 4 + pulse * 0.4
        rr = 30 + 4 * math.sin(pulse * 0.9 + i)
        sx = int(cx + math.cos(a) * rr)
        sy = int(cy + math.sin(a) * rr * 0.85)
        tw = 0.5 + 0.5 * math.sin(pulse * 2.0 + i * 1.7)
        al = int(110 + 130 * tw)
        sz = 3 + int(2 * tw)
        spark = pygame.Surface((sz * 4, sz * 4), pygame.SRCALPHA)
        c = (255, 244, 200, al)
        pygame.draw.line(spark, c, (sz * 2, 0), (sz * 2, sz * 4), 1)
        pygame.draw.line(spark, c, (0, sz * 2), (sz * 4, sz * 2), 1)
        pygame.draw.circle(spark, (255, 255, 230, al), (sz * 2, sz * 2), sz)
        surf.blit(spark, (sx - sz * 2, sy - sz * 2),
                  special_flags=pygame.BLEND_ADD)


def _iso_face_pips(surf, quad, pips, pip_col, *, scale):
    """Map the flat unit-square pip layout onto an axonometric quad via bilinear
    interpolation of its 4 corners, so each pip sits correctly foreshortened on
    a tilted cube face. `quad` is [tl, tr, br, bl] in screen space (the face's
    own top-left, top-right, bottom-right, bottom-left)."""
    tl, tr, br, bl = quad
    for fx, fy in _PIP_LAYOUT[pips]:
        # Bilinear blend: top edge tl->tr at fx, bottom edge bl->br at fx, then
        # lerp those two by fy down the face.
        topx = tl[0] + (tr[0] - tl[0]) * fx
        topy = tl[1] + (tr[1] - tl[1]) * fx
        botx = bl[0] + (br[0] - bl[0]) * fx
        boty = bl[1] + (br[1] - bl[1]) * fx
        px = int(topx + (botx - topx) * fy)
        py = int(topy + (boty - topy) * fy)
        # Crisper, higher-contrast pips than round-5: a tiny light halo separates
        # each pip from the cube face, a solid DARK fill (no muddy mid-tone ring),
        # and a single specular dot. Reads clean + punchy at 1x rather than blurry.
        pr = max(2, int(3 * scale))
        pygame.draw.circle(surf, (255, 252, 244), (px, py), pr + 1)
        pygame.draw.circle(surf, _shade(pip_col, -45), (px, py), pr)
        pygame.draw.circle(surf, _shade(pip_col, 150), (px - 1, py - 1), 1)


def _draw_die_face_noshadow(surf, cx, cy, size, *, pips=None, number=None,
                            body=(252, 250, 244), pip_col=(44, 40, 58)):
    """A 3D AXONOMETRIC die CUBE (no longer a flat square): a top rhombus + a
    left side face + a right side face, in THREE shades for solid form (top
    lightest, left side mid, right side darkest), with thin dark keylines along
    every cube edge and the light reading from the top-left. PIPS are mapped onto
    each visible face foreshortened — a few faces show different counts like a
    real die. When `number` is given (the roll-result inset) the number is set on
    the TOP face instead of pips. The contact-glow/aura behind it replaces any
    cast shadow, so none is drawn here."""
    scale = size / 40.0
    # Cube half-extents. `w` is the horizontal reach of the top rhombus; `dz` is
    # how tall the rhombus diamond is (the iso "depth"); `h` is the side-face
    # height dropping from the front bottom corners.
    w = int(size * 0.52)
    dz = int(size * 0.26)
    h = int(size * 0.50)

    # TOP rhombus corners (clockwise from the back/top point).
    t_top = (cx, cy - dz - h // 2 + 2)            # far back point
    t_right = (cx + w, cy - h // 2 + 2)           # right point
    t_front = (cx, cy + dz - h // 2 + 2)          # near front point
    t_left = (cx - w, cy - h // 2 + 2)            # left point

    # Side faces drop straight down from the front edges by `h`.
    bl = (t_left[0], t_left[1] + h)               # bottom-left
    bf = (t_front[0], t_front[1] + h)             # bottom-front (centre)
    brr = (t_right[0], t_right[1] + h)            # bottom-right

    top_col = _shade(body, 26)                    # lit top, lightest
    left_col = _shade(body, -34)                  # mid side
    right_col = _shade(body, -74)                 # darkest side
    edge = _shade(body, -96)                      # keyline

    top_quad = [t_top, t_right, t_front, t_left]
    left_quad = [t_left, t_front, bf, bl]
    right_quad = [t_front, t_right, brr, bf]

    # Fill the three faces back-to-front (sides first, top last so its keyline
    # crowns the form).
    pygame.draw.polygon(surf, left_col, left_quad)
    pygame.draw.polygon(surf, right_col, right_quad)
    pygame.draw.polygon(surf, top_col, top_quad)

    # PIPS / number on the faces. Map each flat unit-square layout onto the
    # matching quad (corner order tl, tr, br, bl as the face sees it).
    if number is not None:
        f = pygame.font.SysFont(None, max(10, int(size * 0.42)), bold=True)
        txt = f.render(str(number), True, pip_col)
        # Seat the number on the TOP face, centred on the rhombus.
        tcx = (t_top[0] + t_front[0]) // 2
        tcy = (t_top[1] + t_front[1]) // 2
        surf.blit(txt, (tcx - txt.get_width() // 2,
                        tcy - txt.get_height() // 2))
        # Sides still get pips so it still reads as a die — LOW counts so they
        # stay clean at 1x.
        _iso_face_pips(surf, [t_left, t_front, bf, bl], 1, pip_col, scale=scale)
        _iso_face_pips(surf, [t_front, t_right, brr, bf], 2, pip_col,
                       scale=scale)
    else:
        # A real-die face triad with DELIBERATELY LOW counts (top 4, left 1,
        # right 2) so the pips read crisp + uncrowded at 1x rather than muddy.
        # Consistent across all ten so the prop is identical.
        _iso_face_pips(surf, [t_top, t_right, t_front, t_left], 4, pip_col,
                       scale=scale)
        _iso_face_pips(surf, [t_left, t_front, bf, bl], 1, pip_col, scale=scale)
        _iso_face_pips(surf, [t_front, t_right, brr, bf], 2, pip_col,
                       scale=scale)

    # Thin dark keylines on every cube edge so the 3D form reads crisply.
    pygame.draw.polygon(surf, edge, top_quad, 2)
    pygame.draw.line(surf, edge, t_left, bl, 2)
    pygame.draw.line(surf, edge, t_front, bf, 2)
    pygame.draw.line(surf, edge, t_right, brr, 2)
    pygame.draw.line(surf, edge, bl, bf, 2)
    pygame.draw.line(surf, edge, bf, brr, 2)
    # Top-left lit rim catch along the two top-back edges.
    pygame.draw.line(surf, RIM, t_left, t_top, 2)


# ── the ten jester variations ────────────────────────────────────────────────
# Deep two-tone split + gold accents; NO diamonds (those belong to the
# Harlequin). Round-2 rebalances OFF the purple/violet cluster: only ONE pure
# purple remains; the rest spread across distinct warm (ruby/gold, scarlet,
# orange) and cool (teal/cream, ocean, emerald, ice) families so the ten
# thumbnails read distinctly. Each carries the shared naughty recipe + lean;
# `variant` only tweaks the small face flavour (browcock / tongue).

JESTERS = [
    # 1 — classic 3-point, the reliable jester read; warm plum/lime kept as the
    # single purple anchor (shorter chibi build is the proportion north star).
    ("Plum & Lime", dict(
        dark=(96, 44, 150), light=(132, 218, 116), gold=(250, 205, 72),
        cap_fn=cap_three_point, motif="split", collar="belled",
        variant="plain", shoulder_orn=True)),
    # 2 — NOT-a-crown floppy four-point; ruby/cream warm family. Round-2 washed
    # out on the day sky, so the ruby is deepened to a darker mid-value and the
    # cream pulled off near-white toward a warm tan so the silhouette survives.
    ("Ruby & Cream", dict(
        dark=(158, 28, 48), light=(228, 206, 168), gold=(238, 186, 64),
        cap_fn=cap_four_point, motif="quartered", collar="scalloped",
        variant="browcock")),
    # 3 — TRUE two-eared donkey cap; royal-blue/gold (cool+warm).
    ("Royal Blue & Gold", dict(
        dark=(40, 78, 168), light=(248, 206, 88), gold=(252, 226, 130),
        cap_fn=cap_donkey, motif="panels", collar="belled",
        variant="plain")),
    # 4 — the NAUGHTY-FACE reference palette: teal/magenta, coxcomb crest.
    ("Teal & Magenta", dict(
        dark=(26, 134, 142), light=(224, 74, 152), gold=(250, 210, 90),
        cap_fn=cap_coxcomb, motif="split", collar="scalloped",
        variant="tongue")),
    # 5 — the single surviving IMPISH horned hood: charcoal-PLUM, soft nubs.
    ("Charcoal-Plum Imp", dict(
        dark=(58, 44, 64), light=(216, 70, 96), gold=(248, 206, 96),
        cap_fn=cap_imp_hood, motif="quartered", collar="belled",
        variant="tonguecock", imp=True)),
    # 6 — the COSTUME-QUALITY reference: violet/orange coxcomb (kept distinct as
    # the one violet, paired with a warm orange to break from #1's purple).
    ("Violet & Orange", dict(
        dark=(120, 58, 178), light=(246, 148, 58), gold=(250, 214, 96),
        cap_fn=cap_coxcomb, motif="panels", collar="scalloped",
        variant="tongue")),
    # 7 — emerald/gold warm-cool, classic 3-point (lifted off round-1 flat).
    ("Emerald & Gold", dict(
        dark=(28, 120, 76), light=(248, 206, 84), gold=(252, 224, 124),
        cap_fn=cap_three_point, motif="scalloped", collar="belled",
        variant="plain")),
    # 8 — wine/teal curled-bell hood (lankier round-1 legs reined in).
    ("Wine & Teal", dict(
        dark=(126, 32, 70), light=(56, 182, 182), gold=(250, 208, 86),
        cap_fn=cap_hood, motif="split", collar="scalloped",
        variant="browcock")),
    # 9 — COOL ice family pulled off the purple cluster: slate/ice four-point.
    # Round-2 washed out on the day sky; the slate is darkened to a deeper navy
    # mid-value and the ice pulled off near-white toward a cooler grey-blue so the
    # silhouette holds its value against the sky.
    ("Slate & Ice", dict(
        dark=(40, 66, 104), light=(176, 204, 226), gold=(244, 200, 78),
        cap_fn=cap_four_point, motif="panels", collar="belled",
        variant="plain")),
    # 10 — warm scarlet/gold three-point (was a 2nd horned hood; recast).
    ("Scarlet & Gold", dict(
        dark=(196, 52, 56), light=(250, 212, 96), gold=(246, 202, 92),
        cap_fn=cap_three_point, motif="quartered", collar="scalloped",
        variant="tongue")),
    # 11 — design #2's STRUCTURE (splayed four-point cap, quartered body,
    # scalloped collar, cocked-brow grin) recoloured in #1's plum/lime/gold.
    ("Plum & Lime 4-Point", dict(
        dark=(96, 44, 150), light=(132, 218, 116), gold=(250, 205, 72),
        cap_fn=cap_four_point, motif="quartered", collar="scalloped",
        variant="browcock")),
    # 12 — #11 with the scalloped "scarf of circles" collar recoloured to the
    # GOLD of the cap (every ruff lobe yellow, matching the hat bells).
    ("Plum & Lime — Gold Ruff", dict(
        dark=(96, 44, 150), light=(132, 218, 116), gold=(250, 205, 72),
        cap_fn=cap_four_point, motif="quartered", collar="scalloped",
        variant="browcock", collar_in_gold=True)),
    # 13 — THE FINAL PICK: exactly #12, but with the ground cast-shadow beneath
    # the figure removed (`no_shadow`).
    ("Plum & Lime — FINAL (no shadow)", dict(
        dark=(96, 44, 150), light=(132, 218, 116), gold=(250, 205, 72),
        cap_fn=cap_four_point, motif="quartered", collar="scalloped",
        variant="browcock", collar_in_gold=True, no_shadow=True)),
]
