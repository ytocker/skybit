"""Look-dev mockup: 10 NEW Court Jester power-up dice presenters (ROUND 6).

The user loved the Court Jester from the dice-clown sheet for its sly,
"up-to-something / NAUGHTY" read. This sheet explores TEN higher-quality
takes on that ONE archetype — each a large hero jester standing in the day
clearing (sky + grass + the real parrot for scale), presenting a glowing
power-up die. Everything is drawn from pygame primitives; we import the REAL
game helpers (biome palette, glow cache, live parrot) and the chunky body
kit from the dice-clown mockup, and mutate no game state.

THE POSE (identical on all ten): the die floats HIGH in the upper-LEFT sky,
the viewer's-LEFT arm (`cx - …`) is raised diagonally up and POINTS toward the
airborne die (gesturing at it), and the viewer's-RIGHT arm (`cx + …`) hangs
down with a visible mitt and a slight outward bow. This MIRRORS the original
jester (which raised its right arm to a die at upper-right).

Prior ROUND-5 direction (kept for lineage; everything below the chin still ships
unchanged — bodies, lean, pose-arms, caps, costumes, collars, shoes, palettes,
the parrot, the 1x inset and 2x supersample are all kept). Four "pump it up"
changes that landed, now refined by the round-6 notes further below:
  - HAPPY-with-a-MEAN-SMILE face: round-4 still read SAD (heavy hooded almond
    eyes + a thin smirk line). Reworked into a GLEEFUL villain GRIN — the mouth
    is now the dominant feature: a WIDE, upturned, OPEN grin with a row of teeth
    and ONE pointed fang for the mean edge; cheeks pushed up. Eyes opened up
    bright + lively with a happy-squint lower lid and a catchlight (pupils still
    glancing sidelong at the die). Brows lifted into a light sly arch (happy +
    cheeky, not a worried frown). The big red ball nose shrunk + seated higher
    so it no longer crowds the grin. Cheek blush kept.
  - DIE FLOATS HIGHER, up in the top-left sky (clearly airborne): `die_base_y`
    dropped and `die_x` pulled further left; the LEFT arm now POINTS up at it
    rather than cupping under it.
  - YELLOW power-up AURA: the gold halo is replaced by a brighter, larger,
    PULSING yellow aura (layered BLEND_ADD glow — wide soft outer + hot
    yellow-white core, breathing with the bob). Orbiting sparkles kept; the
    under-die contact-glow dropped (it's airborne, not cupped).
  - 3D ISOMETRIC CUBE: the flat die square is replaced by an axonometric cube
    (top rhombus + left + right faces in three shades, dark edge keylines,
    top-left lit) with pips on the visible faces (different counts per face like
    a real die). The "27" roll-result inset is the same cube with the number on
    the top face. Consistent across all ten.

ROUND-6 direction (bodies, lean, pose-arms, caps, costumes, palettes, the 3D
cube FORM and the high top-left float all LANDED and ship unchanged). Two
blockers + polish, all confined to the FACE, the DIE and its PLACEMENT:
  - UN-ANGRY the grin: round-5's brows had swung to a hard inner-DOWN "V" (the
    universal anger shape). The brow is rebuilt to RAISE the INNER end into a
    cheeky arch (crest over the nose-side half), matching the gleeful tile #1
    read, applied to ALL ten. The brow stays UP, never lowering toward the nose.
  - DE-STACK the red around the eyes: the heavy rosy eye-rim is replaced by a
    thin soft NEUTRAL ink-brown squint crease, and the cheek blush is eased, so
    the red nose + cheeks no longer reinforce into a feverish/angry look.
  - REAL power-up AURA: round-5's pure BLEND_ADD halo washed to white on the day
    sky and effectively vanished. It is rebuilt as an explicit alpha-blended
    near-WHITE core → bright YELLOW → warm AMBER falloff at ~1.8x the die
    footprint (reads on VALUE, so it survives night + colourblind), with a light
    additive bloom on top for the glow pop. Orbiting sparkles kept.
  - Cube PIPS cleaned: crisper high-contrast dark pips with a light separation
    halo + more spacing, and simpler per-face counts (top 4, sides 1 + 2) so
    they read clean at 1x. The cube FORM is unchanged.
  - The die is nudged ~12px IN from the top-left corner so at 1x it clears the
    HUD/score gutter, and the cheeky tongue-tip is tightened so it stops reading
    as a smudge/drip.

Each cell is supersampled 2x then smoothscaled for crisp anti-aliasing.

    PYTHONPATH=. python tools/render_jester_variants.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H
from game.draw import lerp_color, blit_glow
from game.parrot import get_parrot
from tools.render_warren_mockup import shaped_palette

# Reuse the chunky mascot body kit + the consistent floating-die prop from the
# dice-clown mockup so these jesters read as the SAME family of casual mascots
# and the power-up die is pixel-identical to the approved treatment.
from tools.render_clown_dice import (
    _shade, _poly, _facet_body, _round_head, _nose, _arm, _leg, _shoes,
    _shadow, RIM, WHITE, INK, ROSY,
    DAY_PHASE, SS, VIEW_W, VIEW_H, VIEW_FEET_Y,
    HERO_PIPS, _PIP_LAYOUT,
)


# ── the HAPPY-MEAN face kit (ONE locked recipe on all ten) ───────────────────
# The signature is a SINGLE recipe applied to every jester: a wide OPEN happy
# GRIN (the dominant feature) with a row of teeth and one pointed fang for the
# mean edge, bright OPEN smiling eyes with a sidelong glance toward the die,
# and lifted sly brows — gleeful + up-to-no-good, never sad/droopy/pleading.
# Variants layer on a single cocked brow and a tongue-tip at the grin corner
# for variety.

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


# ── per-cell gameplay scene (mirrored: die upper-LEFT) ───────────────────────

def render_cell(spec, idx, show_inset):
    """One tight day-clearing scene at SS supersample: sky + a sliver of grass
    + cast shadow, the chunky jester filling ~70-80% of the cell, the head-sized
    power-up die floating high in the upper-LEFT focal slot with the raised LEFT
    arm pointing up at it, and the real parrot for scale. Returns VIEW_W x VIEW_H."""
    # `no_shadow` is a per-tile spec flag (popped here so it never reaches
    # build_jester) that suppresses the ground cast-shadow under the figure.
    spec = dict(spec)
    no_shadow = spec.pop('no_shadow', False)
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * SS, VIEW_H * SS
    big = pygame.Surface((bw, bh))

    g_y = int(VIEW_FEET_Y * SS) + 6 * SS
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        c = lerp_color(palette['sky_mid'], palette['sky_bot'], t)
        pygame.draw.line(big, c, (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        c = lerp_color(palette['ground_top'], palette['ground_mid'], t)
        pygame.draw.line(big, c, (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    hill = pygame.Surface((bw, 30 * SS), pygame.SRCALPHA)
    hc = _shade(palette['ground_mid'], 22)
    for hx, hw, hh in ((40, 90, 18), (130, 110, 22), (185, 80, 16)):
        pygame.draw.ellipse(hill, (*hc, 160),
                            ((hx - hw) * SS, 0, hw * 2 * SS, hh * 2 * SS))
    big.blit(hill, (0, g_y - 14 * SS))
    tuft = _shade(palette['ground_top'], 22)
    rng = __import__('random').Random(idx * 131 + 7)
    for _ in range(10):
        tx = rng.randint(8, VIEW_W - 8) * SS
        ty = g_y + rng.randint(3, max(4, bh // SS - VIEW_FEET_Y - 4)) * SS
        for k in (-3, 0, 3):
            pygame.draw.line(big, tuft, (tx + k * SS, ty),
                             (tx + k * SS, ty - rng.randint(4, 7) * SS),
                             max(1, SS))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    # Figure nudged RIGHT of centre so the die has clear sky in the upper-LEFT
    # to float in, fully off the head silhouette (mirror of the original).
    jester_cx = VIEW_W // 2 + 12
    feet_y = VIEW_FEET_Y
    if not no_shadow:
        _shadow(layer, jester_cx, feet_y, 96)

    # The die floats HIGH in the upper-LEFT sky, clearly airborne. The raised
    # LEFT arm no longer cups it — it POINTS diagonally UP toward the floating
    # die (gesturing "look at THIS"). `hand_up` sits well below + right of the
    # die so the pointing arm reads as aiming up at it across open sky, never
    # touching it, and stays clear of the head silhouette.
    # Nudged ~12px IN from the very top-left corner (round-5 jammed the aura into
    # the corner / off-canvas, where at 1x it would collide with the HUD score
    # gutter). It still floats HIGH and clearly upper-LEFT, just clear of the edge
    # so the bright aura sits fully over the open sky clearing.
    die_x = jester_cx - 66
    die_base_y = 36
    # Round-4 raised-arm target: a shorter, steeper presenting gesture toward the
    # die rather than a long out-stretched point. The die stays HIGH up-left; only
    # the hand target reverts so the arm reads as round 4's tucked raise.
    hand_up = (die_x + 6, 76)

    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    pulse = idx * 1.7 + 2.0
    draw_cupped_die(layer, die_x, die_base_y, pulse, show_inset=show_inset)

    # Real parrot flying in low from the RIGHT for scale, clear of the figure
    # and the upper-left die.
    bird = get_parrot(1, -10)
    bird = pygame.transform.smoothscale(
        bird, (int(bird.get_width() * 0.92), int(bird.get_height() * 0.92)))
    layer.blit(bird, (VIEW_W - 22 - bird.get_width() // 2,
                      (feet_y - 64) - bird.get_height() // 2))

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


CAPTIONS = [
    "plum/lime · 3-point cap · grin+fang · cube up-left",
    "ruby/cream · SPLAYED 4-point · cocked-brow grin",
    "royal-blue/gold · donkey-EAR cap · fang grin",
    "teal/magenta · ANCHORED coxcomb · grin + tongue",
    "charcoal-plum · IMPISH horned hood · grin + tongue",
    "violet/orange · ANCHORED coxcomb · grin + tongue",
    "emerald/gold · 3-point cap · happy-mean grin",
    "wine/teal · curled-bell hood · cocked-brow grin",
    "slate/ice · SPLAYED 4-point · fang grin",
    "scarlet/gold · 3-point cap · grin + tongue",
    "plum/lime · SPLAYED 4-point · cocked-brow (= #2 in #1's colours)",
    "plum/lime · 4-point · GOLD scalloped ruff (= #11, yellow collar circles)",
    "FINAL PICK · = #12 with NO ground shadow beneath the figure",
]


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))

    cols, rows = 5, 3          # 11 tiles: 5 + 5 + 1 (the new #11 leads row 3)
    sw, sh = int(VIEW_W * 1.88), int(VIEW_H * 1.88)

    PAD = 44
    GAP = 22
    TITLE_H = 92
    CAP_H = 64
    FOOT_H = VIEW_H + 28

    canvas_w = PAD * 2 + cols * sw + (cols - 1) * GAP
    canvas_h = (PAD * 2 + TITLE_H + rows * (sh + CAP_H) + (rows - 1) * GAP
                + FOOT_H)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((24, 22, 30))

    f_title = pygame.font.SysFont(None, 70, bold=True)
    f_sub = pygame.font.SysFont(None, 32, bold=True)
    f_cap = pygame.font.SysFont(None, 38, bold=True)
    f_caps = pygame.font.SysFont(None, 28, bold=True)

    title = f_title.render("COURT JESTER — naughty dice presenter (round 12)",
                           True, (250, 240, 210))
    canvas.blit(title, (PAD, PAD - 2))
    sub = f_sub.render(
        "FIXED (tile #1 ONLY): added belled GOLD shoulder POMS / epaulets at both "
        "shoulders so the raised LEFT arm now reads CONNECTED to the body — the "
        "belled-collar seam at the exposed raised shoulder is bridged by the "
        "costume's own bell/pom vocabulary. All other 9 tiles unchanged from round 8.",
        True, (190, 195, 205))
    canvas.blit(sub, (PAD, PAD + 50))

    # Show the rolled-result inset in a couple of cells to hint the mechanic.
    inset_cells = {0, 9}

    y0 = PAD + TITLE_H
    template_cell = None
    for i, (name, spec) in enumerate(JESTERS):
        r, c = divmod(i, cols)
        cx = PAD + c * (sw + GAP)
        cy = y0 + r * (sh + CAP_H + GAP)
        cell = render_cell(spec, i, show_inset=(i in inset_cells))
        if i == 0:  # Plum & Lime — the LEAD/template face; showcase it at 1x.
            template_cell = cell
        scaled = pygame.transform.smoothscale(cell, (sw, sh))
        pygame.draw.rect(canvas, (70, 76, 96),
                         pygame.Rect(cx - 1, cy - 1, sw + 2, sh + 2), 1)
        canvas.blit(scaled, (cx, cy))
        cap = f_cap.render(f"{i + 1}. {name}", True, (235, 225, 165))
        canvas.blit(cap, (cx + (sw - cap.get_width()) // 2, cy + sh + 6))
        sub2 = f_caps.render(CAPTIONS[i], True, (190, 196, 206))
        canvas.blit(sub2, (cx + (sw - sub2.get_width()) // 2, cy + sh + 38))

    # ONE 1x legibility inset proving the design reads at in-game scale.
    if template_cell is not None:
        foot_y = y0 + rows * (sh + CAP_H) + (rows - 1) * GAP + 14
        ix = PAD
        pygame.draw.rect(canvas, (70, 76, 96),
                         pygame.Rect(ix - 2, foot_y - 2, VIEW_W + 4,
                                     VIEW_H + 4), 1)
        canvas.blit(template_cell, (ix, foot_y))
        tag = f_cap.render(
            "1x in-game scale (Plum & Lime, the lead) — NEW belled gold shoulder "
            "poms now bridge the belled-collar seam so the raised LEFT arm reads "
            "CONNECTED to the body; raised brow + bright eyes + smooth sly grin "
            "read HAPPY/cheeky; die reads as a glowing YELLOW-aura 3D CUBE high "
            "upper-left with the LEFT arm pointing up at it",
            True, (200, 206, 216))
        canvas.blit(tag, (ix + VIEW_W + 24, foot_y + VIEW_H // 2 - 14))

    out_dir = os.path.join("docs", "jester")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_12.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
