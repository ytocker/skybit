"""LOTERÍA PARROT PIÑATA secret flyer skin — "El Perico" concept build.

The Lotería card-deck parrot rebuilt as a crepe-paper piñata: a fat
round-bellied perched bird whose two tells are an oversized HOOKED-DOWN beak
and a long up-and-out crepe-fringe TAIL. It must read as a "parrot piñata"
at 40px and stay distinct from Skybit's existing toucan (a long FLAT beak) and
flamingo (long LEGS + neck): El Perico has a short hooked beak, a round body,
a big swinging tail, and NO long legs or neck.

The 4-frame tell is TAIL-FRINGE WAG + HEAD BOB (no wings, no particles): the
long crepe tail swings like a pendulum in OPEN SKY to the upper-RIGHT of the
body — clear of Pip's centred parcel — while the head gives a small
counter-bob. The wag survives grayscale because the tail is re-banded as a
VALUE paddle (a dark rib next to a cream rib) whose pale tip crosses the body's
vertical centreline frame-to-frame: a light/dark shape changing POSITION, not a
hue trick.

Contract mirrors game/animal_ufo.py so a winner lifts straight in:
  * `build(wing_angle_deg) -> pygame.Surface` — one flat 64x84 SRCALPHA frame,
    body mass centred at (BCX,BCY)=(32,41); drawn UPRIGHT (no baked rotation —
    velocity tilt is applied later by the cached getter).
  * driven by `game.parrot._WING_ANGLES = (50,20,-10,-40)` → tail sweep + bob.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 9                          # body lifted ~3px vs round 1 to buy tail room
BCX, BCY = 32, 32 + DY          # round body centre → (32, 41)

BODY_RX, BODY_RY = 16, 17       # fat round-bellied perched-bird mass
HEAD_RX, HEAD_RY = 11, 10       # chunky head, set high-right on the body

# The tail no longer hangs dead-centre (where the parcel occludes it). Its ROOT
# is welded DEEP INSIDE the lower-left flank (pulled up-and-in so the round body
# overlaps the root with NO sky between them) and the blade swings down-and-out
# into OPEN SKY to the LEFT of the parcel — the parcel hangs centred-low and the
# red head is upper-right, so the lower-left is clean sky the blade sweeps
# through. Only the wag TIP crosses centre in open sky; the root stays buried in
# the flank so tail and body read as one creature.
TAIL_PIVOT_X = 26               # pulled IN toward body-centre → root buried in flank
TAIL_PIVOT_Y = 43               # pulled UP into the flank so body mass overlaps it
TAIL_LEN = 25                   # long crepe tail (the moving line)
TAIL_HALF = 9                   # half-width of the tail blade — kept BOLD/WIDE


# ── palette ──────────────────────────────────────────────────────────────────
# Lotería festival colours: green body, red head, yellow+blue wing-band stripe,
# cream beak. The TAIL drops the same-value yellow/blue pairing and is re-banded
# as a VALUE paddle — a genuinely dark rib alternating with a cream rib — so the
# wag reads as a light/dark shape moving in grayscale alone. A cream
# crepe-fringe keyline rims the body so the saturated party colours survive the
# night sky.
BODY_GREEN   = ( 52, 178,  74)   # #34B24A green body
BODY_GREEN_D = ( 32, 126,  52)   # shaded lower body
BODY_GREEN_H = ( 96, 214, 116)   # upper-body sheen
BODY_CORE_D  = ( 20,  86,  40)   # darker core-shadow down the sky-facing belly
HEAD_RED     = (226,  58,  46)   # #E23A2E red head
HEAD_RED_D   = (170,  36,  30)   # shaded head underside
HEAD_RED_H   = (255, 118, 104)   # crown highlight

BAND_YELLOW  = (244, 193,  46)   # #F4C12E yellow wing-band stripe
BAND_BLUE    = ( 46, 111, 214)   # #2E6FD6 blue wing-band stripe
BEAK_CREAM   = (236, 218, 178)   # cream beak — pulled a notch down off pure white
BEAK_CREAM_D = (190, 166, 120)   # shaded beak underside
BEAK_HOOK_D  = (120, 100,  64)   # deep hook-tip notch shadow

FRINGE       = (255, 246, 222)   # cream crepe fringe rim / night keyline
FRINGE_DK    = (212, 192, 152)   # fringe shade so the rim has its own form

# TAIL value paddle: a DARK rib and a CREAM rib alternate down the blade so the
# tail is its own light/dark shape, never a continuation of the body bands.
# But the tail ROOT carries the body's own mid-green (TAIL_ROOT_GREEN) so one
# continuous green band flows out of the flank into the blade — the value bridge
# that welds tail to body. The dark/cream paddle only takes over past the root.
TAIL_ROOT_GREEN = ( 44, 158,  66)  # flank-matching green that fills the root → bridge
TAIL_DARK    = ( 22,  78,  40)   # deep dark rib — the value anchor of the paddle
TAIL_DARK_D  = ( 14,  54,  30)   # darkest tail shade (form under the dark ribs)
TAIL_CREAM   = (255, 244, 214)   # cream rib — the bright paddle band
EYE_DARK     = ( 28,  20,  24)   # eye pip
EYE_WHITE    = (255, 255, 255)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 wag-stage index. _WING_ANGLES runs 50→-40,
    so stage advances 0→3 across the four poses, driving the tail pendulum."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Tail sweep angle (deg, measured from horizontal-right, +CCW/up) per stage. The
# blade pivots from the left haunch and points DOWN-AND-LEFT (angles 200..270°,
# where 270° = straight down). The sweep rocks WIDE so the pale pom tip travels
# from well LEFT of the body's vertical centreline (stage 0, swung out left) to
# crossing UNDER the centreline (stage 2, near straight-down) — the bright tip
# is the obvious mover, visibly changing which side of centre it sits on across
# the loop. All four poses keep the blade clear of the centred parcel.
_TAIL_SWEEP_BY_STAGE = (214.0, 234.0, 262.0, 234.0)

# Head bob (px, +down) per stage — a small counter-bob opposite the tail so the
# whole body reads as "alive" without spreading a wing. Kept subtle so the head
# colour-block stays put and the red-head/green-body read never breaks.
_HEAD_BOB_BY_STAGE = (-1.0, 0.0, -1.0, 1.0)


def _tail(surf, sweep_deg):
    """The long up-and-out crepe-fringe tail — the signature moving line, swung
    into OPEN SKY to the upper-right of the body (clear of the centred parcel).

    Re-banded as a VALUE PADDLE: instead of same-value yellow/blue ribs, the
    blade alternates a DARK green-black rib with a CREAM rib, and the whole tip
    is a dominant scalloped cream pom. So in grayscale it is a clear light/dark
    paddle, and the wag reads as that paddle changing POSITION frame-to-frame.
    Kept BOLD and wide so it never mushes to a needle at 40px."""
    # sweep is measured from horizontal-right (+CCW/up). Convert to a screen
    # direction vector (screen-y grows DOWN, so up = negative dy).
    a = math.radians(sweep_deg)
    dx, dy = math.cos(a), -math.sin(a)
    px, py = -dy, dx                     # perpendicular = blade half-width axis

    # The blade ROOT is pushed BACK along the sweep axis past the pivot, up INTO
    # the body, so the quad's near end is buried under the green mass with no sky
    # seam. (root_back) is how far the root reaches back toward body-centre — kept
    # generous so even the extreme down-left swing keeps its root under the flank.
    root_back = 12
    cx = TAIL_PIVOT_X - dx * root_back
    cy = TAIL_PIVOT_Y - dy * root_back

    # blade quad: a wide root buried in the flank, tapering to a narrower tip,
    # long and bold — the largest moving shape, always against sky past the root.
    root_hw, tip_hw = TAIL_HALF + 2, TAIL_HALF - 1  # fatter root so the neck never thins to sky
    tip_x = cx + dx * (TAIL_LEN + root_back)
    tip_y = cy + dy * (TAIL_LEN + root_back)
    rl = (cx + px * root_hw, cy + py * root_hw)
    rr = (cx - px * root_hw, cy - py * root_hw)
    tl = (tip_x + px * tip_hw, tip_y + py * tip_hw)
    tr = (tip_x - px * tip_hw, tip_y - py * tip_hw)

    # full blade in the DARK value first so the paddle has a deep base; the dark
    # is what carries the "paddle" read in grayscale.
    pygame.draw.polygon(surf, TAIL_DARK_D, [rl, tl, tr, rr])
    pygame.draw.polygon(surf, TAIL_DARK, [rl, tl, tr, rr])

    # BRIDGE: flood the root third of the blade with the body's mid-green so one
    # continuous green band flows out of the flank into the tail. The body is
    # drawn AFTER the tail and overlaps this root, so flank→tail reads as one
    # creature with the dark/cream paddle only taking over past the body edge.
    bridge_t = 0.42
    bx2 = cx + dx * (TAIL_LEN + root_back) * bridge_t
    by2 = cy + dy * (TAIL_LEN + root_back) * bridge_t
    hwb = root_hw + (tip_hw - root_hw) * bridge_t
    pygame.draw.polygon(surf, TAIL_ROOT_GREEN, [
        rl, rr,
        (bx2 - px * hwb, by2 - py * hwb),
        (bx2 + px * hwb, by2 + py * hwb)])

    # alternating CREAM ribs banded across the blade — the bright half of the
    # value paddle. Start PAST the green bridge so the ribs belong to the swinging
    # outer blade, not the welded root. Dark base + cream ribs = a rhythmic
    # light/dark ladder that changes position as the blade swings.
    total = TAIL_LEN + root_back
    for i in range(2, 6):
        t = i / 6.0
        mx = cx + dx * total * t
        my = cy + dy * total * t
        hw = root_hw + (tip_hw - root_hw) * t
        if i % 2 == 0:                   # cream ribs on the even steps (past root)
            pygame.draw.line(surf, TAIL_CREAM, (mx + px * hw, my + py * hw),
                             (mx - px * hw, my - py * hw), 3)

    # cream crepe-fringe keyline only along the two OUTER long edges (sky-facing)
    # and the tip cap — NEVER across the root, so no keyline fences the tail off
    # from the flank. The root seam is left open to blend under the body.
    pygame.draw.line(surf, FRINGE, rl, tl, 2)
    pygame.draw.line(surf, FRINGE, rr, tr, 2)
    pygame.draw.line(surf, FRINGE, tl, tr, 2)

    # DOMINANT scalloped cream-pom tip — the tail's own signature, so it never
    # reads as a continuation of the flank bands. A fat row of cream poms with
    # dark cores makes the swinging tip the boldest, most obvious mover.
    for k in (-1, 0, 1):
        fx = tip_x + px * (k * 3.2)
        fy = tip_y + py * (k * 3.2)
        pygame.draw.circle(surf, FRINGE, (int(fx), int(fy)), 3)
        pygame.draw.circle(surf, TAIL_DARK, (int(fx), int(fy)), 1)
    # one big terminal pom dead-centre at the very tip so the paddle has a clear
    # bright "head" the eye tracks as it crosses the centreline
    pygame.draw.circle(surf, FRINGE, (int(tip_x), int(tip_y)), 3)
    pygame.draw.circle(surf, FRINGE_DK, (int(tip_x), int(tip_y)), 3, 1)


def _body(surf, cx, cy):
    """The fat round-bellied body — the dominant central green mass with a
    yellow+blue Lotería wing-band stripe wrapped across the flank, a darker
    green core-shadow down the sky-facing (lower-left) belly, and a cream
    crepe-fringe rim keyline so the green survives the night sky."""
    # A lower-LEFT haunch lobe extends the green mass down toward the tail pivot
    # so the flank physically reaches the tail root in the extreme swing — this is
    # what guarantees no sky seam between body and tail in any frame. Drawn under
    # the main body so it reads as one continuous flank, not a bolted-on bump.
    _aaellipse(surf, BODY_GREEN_D, (cx - 8, cy + 8), 9, 8)
    _aaellipse(surf, BODY_GREEN, (cx - 8, cy + 7), 9, 7)

    _aaellipse(surf, BODY_GREEN_D, (cx, cy + 2), BODY_RX, BODY_RY)       # shadow
    _aaellipse(surf, BODY_GREEN, (cx, cy), BODY_RX, BODY_RY)             # body
    _aaellipse(surf, BODY_GREEN_H, (cx - 4, cy - 6), BODY_RX - 7, BODY_RY - 9)

    # Darker green core-shadow crescent down the sky-facing lower-LEFT belly so
    # the body doesn't depend solely on the cream keyline to separate from the
    # bright blue day sky — it gets its own internal value step at the edge.
    _aaellipse(surf, BODY_CORE_D, (cx - 5, cy + 4), BODY_RX - 4, BODY_RY - 5)
    _aaellipse(surf, BODY_GREEN, (cx - 2, cy + 2), BODY_RX - 4, BODY_RY - 5)

    # Lotería wing-band stripe: a folded yellow→blue chevron across the flank,
    # the card-deck parrot's banded wing read without spreading an actual wing.
    band_y = cy + 1
    pygame.draw.line(surf, BAND_YELLOW, (cx - BODY_RX + 3, band_y - 3),
                     (cx + BODY_RX - 5, band_y - 1), 3)
    pygame.draw.line(surf, BAND_BLUE, (cx - BODY_RX + 3, band_y + 2),
                     (cx + BODY_RX - 5, band_y + 4), 3)
    # a couple of crepe seam ticks above the band so the body reads as layered
    # crepe paper, not a flat ball
    for tx in range(cx - BODY_RX + 5, cx + BODY_RX - 4, 5):
        pygame.draw.line(surf, FRINGE_DK, (tx, cy - 9), (tx, cy - 6), 1)

    # cream crepe-fringe rim keyline around the whole body (night survival)
    pygame.draw.ellipse(surf, FRINGE,
                        pygame.Rect(cx - BODY_RX, cy - BODY_RY,
                                    BODY_RX * 2, BODY_RY * 2), 2)
    # a 1px darker green inner line down the lower-LEFT sky-facing edge so the
    # silhouette has an internal contour against day sky, not just the keyline
    rect = pygame.Rect(cx - BODY_RX + 1, cy - BODY_RY + 1,
                       BODY_RX * 2 - 2, BODY_RY * 2 - 2)
    pygame.draw.arc(surf, BODY_GREEN_D, rect,
                    math.radians(170), math.radians(280), 2)


def _head_and_beak(surf, cx, cy, bob):
    """The chunky RED head set high-right on the body with the oversized
    HOOKED-DOWN beak — the two reads (red head colour-block + hooked beak) that
    separate El Perico from the long-flat-beaked toucan. The head sits high so
    its red block stays clear of the parcel and the green body below it. The
    beak is TIGHTER than round 1: a shorter, narrower lower mandible and a
    deeper hook-tip notch so the down-hook curve is unmistakably the read, and
    its brightest value is pulled down a notch so it stops out-shouting the red
    head on a bright day sky."""
    hx, hy = cx + 6, cy - 12 + int(bob)     # head high-right on the body

    _aaellipse(surf, HEAD_RED_D, (hx, hy + 1), HEAD_RX, HEAD_RY)   # head shadow
    _aaellipse(surf, HEAD_RED, (hx, hy), HEAD_RX, HEAD_RY)         # red head

    # NECK PINCH (the day-frame "head" read): a dark contour notch along the
    # lower-LEFT of the head where it meets the green shoulder, so the red head
    # steps off the body as a HEAD instead of a ball sunk into a green lump.
    # Drawn AFTER the head so it sits crisply on the seam — a short dark arc
    # hugging the head's underside plus a 1px shadow into the shoulder green.
    pinch = pygame.Rect(hx - HEAD_RX, hy - HEAD_RY + 3, HEAD_RX * 2, HEAD_RY * 2)
    pygame.draw.arc(surf, BODY_CORE_D, pinch,
                    math.radians(195), math.radians(265), 2)
    pygame.draw.line(surf, BODY_GREEN_D, (hx - HEAD_RX + 1, hy + HEAD_RY - 2),
                     (hx - HEAD_RX + 5, hy + HEAD_RY + 1), 2)
    _aaellipse(surf, HEAD_RED_H, (hx - 2, hy - 5), HEAD_RX - 5, 3) # crown sheen
    # cream rim keyline so the red head survives the night sky as its own block
    pygame.draw.ellipse(surf, FRINGE,
                        pygame.Rect(hx - HEAD_RX, hy - HEAD_RY,
                                    HEAD_RX * 2, HEAD_RY * 2), 1)

    # eye — a dark pip with a glint, set forward so it reads as a face at 40px
    ex, ey = hx + 3, hy - 1
    pygame.draw.circle(surf, FRINGE, (ex, ey), 3)
    pygame.draw.circle(surf, EYE_DARK, (ex + 1, ey), 2)
    pygame.draw.circle(surf, EYE_WHITE, (ex, ey - 1), 1)

    # ── oversized HOOKED-DOWN beak (the headline tell) ──
    # An upper mandible that juts forward then HOOKS sharply down over a SHORT,
    # NARROW lower mandible — a fat parrot hook, never a long flat toucan blade.
    # Cream (a night high-value anchor) but pulled off pure white, with a deep
    # hook-tip notch shadow so the down-hook curve is the dominant read.
    bx = hx + HEAD_RX - 2                 # beak root at the front of the head
    by = hy + 1
    upper = [
        (bx, by - 4),                     # top of the cere where it meets head
        (bx + 10, by - 2),                # juts forward
        (bx + 10, by + 5),                # then hooks sharply DOWN
        (bx + 6, by + 8),                 # the curved hook tip
        (bx + 5, by + 3),
        (bx, by + 2),
    ]
    pygame.draw.polygon(surf, BEAK_CREAM, upper)
    pygame.draw.polygon(surf, BEAK_CREAM_D, upper, 1)
    # SHORT, NARROW lower mandible tucked under the hook (tighter than round 1)
    lower = [(bx, by + 3), (bx + 4, by + 4), (bx + 3, by + 6), (bx, by + 5)]
    pygame.draw.polygon(surf, BEAK_CREAM_D, lower)
    # deep hook-tip notch shadow so the down-hook curve is the read, plus a
    # gloss line on the upper mandible
    pygame.draw.line(surf, FRINGE_DK, (bx + 1, by - 2), (bx + 8, by - 1), 1)
    pygame.draw.line(surf, BEAK_HOOK_D, (bx + 6, by + 8), (bx + 9, by + 4), 2)
    pygame.draw.circle(surf, BEAK_HOOK_D, (bx + 6, by + 7), 1)
    # a dark cere nostril where the beak meets the face
    pygame.draw.circle(surf, HEAD_RED_D, (bx + 1, by - 2), 1)


def _perch_feet(surf, cx, cy):
    """Two short stubby perch-claws tucked under the belly. Deliberately SHORT
    — El Perico is a perched piñata-bird with NO long legs (the flamingo's
    tell), so the feet are tiny cream nubs that don't add a vertical line."""
    for fx in (cx - 5, cx + 4):
        pygame.draw.line(surf, BEAK_CREAM_D, (fx, cy + BODY_RY - 4),
                         (fx, cy + BODY_RY), 2)
        pygame.draw.circle(surf, BEAK_CREAM, (fx, cy + BODY_RY), 2)
        pygame.draw.circle(surf, BEAK_CREAM_D, (fx, cy + BODY_RY), 2, 1)


def build_pinata_parrot(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    sweep = _TAIL_SWEEP_BY_STAGE[ph]
    bob = _HEAD_BOB_BY_STAGE[ph]
    cx, cy = BCX, BCY

    # 1) Tail FIRST (behind/below the body root) so the round body overlaps its
    #    root and the silhouette reads as one chunky bird with a long swinging
    #    tail. It swings out to the upper-RIGHT in open sky, clear of the
    #    centred parcel; it is the largest moving element across the loop.
    _tail(surf, sweep)

    # 2) Short perch-claws behind the belly so the body sits over their roots.
    _perch_feet(surf, cx, cy)

    # 3) Fat round green body — the dominant central mass.
    _body(surf, cx, cy)

    # 4) Red head + oversized hooked beak high-right, with the small head bob.
    _head_and_beak(surf, cx, cy, bob)

    return surf


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter (mirrors animal_ufo.py):
    a lazy 4-frame build through the house silhouette outline + a per-(frame, 3°)
    rotation cache, so the flyer animates and banks with the bird's tilt."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_pinata_parrot(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


get_pinata_parrot = _make_prebuilt_skin(build_pinata_parrot)

BUILDERS = {"skin_pinata_parrot": get_pinata_parrot}
