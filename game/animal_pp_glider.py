"""WIDE GLIDER — production build for the secret PAPER PLANE skin (KEEL GLIDER).

Converged from Round-1 winner V5 · KEEL GLIDER: a broad FLAT-WING paper glider
seen 3/4 from above-behind, nosing RIGHT, built around a BOLD raised central keel
(fuselage ridge) flanked by two wide flat wing shelves. This is deliberately a
DIFFERENT silhouette from the production dollar-bill DART — the dart is a narrow
forward triangle; the glider is a WIDE planform reading as a slow soaring craft,
and the chunky lit-spine-vs-shadow-shelf keel is what gives it the 3D structure
that flat deltas lack.

Contract (mirrors game/animal_paper_plane.py so this lifts straight into a
standalone game/animal_paper_plane.py module):

  * `build_glider_wide(wing_angle_deg) -> pygame.Surface`  one flat frame on a
    64x84 SRCALPHA canvas, mass centred at (32, 44).
  * NOSE POINTS RIGHT (forward): the rightmost, narrowest pixel cluster is the
    nose; the wide wing span sits LEFT/behind. The keel is the forward-right
    spine. It must never read as a backward kite — the wide end is the tail.
  * No wings — the 4 base poses (_WING_ANGLES 50..-40) become a gentle
    BANK/FLUTTER + slow nose-bob + a soaring pitch sway, since a wide glider
    rides air rather than flaps.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_glider_wide": get_glider_wide}` registry at the bottom.

North star: "a skin lives or dies at 40px in motion." The keel is the hero — a
tall, chunky lit ridge against a hard-darkened shadow shelf, with two crisp rear
points so the silhouette reads as a deliberate WIDE wing (not a narrow dart, not
a frayed blob). The brightest manila is held a notch below white so it never
flares against bright day sky, and a baked 1px self-rim hugs the whole planform
(tightened on the shadow side) so it holds on day AND night with no host outline.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, _WING_ANGLES, _add_outline,
)


# canvas constants (match game/animal_paper_plane.py)
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY          # mass centre -> (32, 44)


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle). Lazy 4-frame build + per-(frame, 3deg) rotation cache,
    each frame outlined with the house silhouette outline."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flutter(angle_deg):
    """Map a base wing angle (_WING_ANGLES runs 50->-40) to a centred -1..+1
    'catching air' factor that drives the soaring bank + nose-bob. No wings, so
    all the flap energy goes into the whole sheet swaying as it rides air."""
    return ((angle_deg + 40) / 90.0 - 0.5) * 2.0


def _poly(surf, color, pts, width=0):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts], width)


def _bank(pts, cx, cy, roll_deg, bob, pitch=0.0):
    """Roll a point list about (cx, cy), lift by `bob`, and add a slow forward
    `pitch` shear (nose lifts/drops) so the whole rigid folded sheet sways as
    one — the most paper-honest read of 'flap' for a wingless glider.

    Pitch shears y by horizontal distance from the mass centre, so the nose
    (positive dx, right) rises/falls opposite the tail. Roll is clamped by the
    caller so the wide planform never rolls far enough to read as a backward
    kite — the forward-right nose stays the rightmost cluster at all poses."""
    r = math.radians(roll_deg)
    cos_r, sin_r = math.cos(r), math.sin(r)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * cos_r - dy * sin_r,
                    cy + dx * sin_r + dy * cos_r + bob + dx * pitch))
    return out


def _self_rim(surf, rim_color):
    """Bake a tight 1px self-rim hugging the painted silhouette so the planform
    reads on any sky without leaning on the host outline. Built from the alpha
    mask and stamped UNDER the art (4-neighbour only, no diagonals) so it stays a
    consistent 1px lip — on night it is what carries the shadow-shelf rear edge,
    where the soft trailing corners would otherwise drop into the dark sky."""
    mask = pygame.mask.from_surface(surf, threshold=8)
    rim = mask.to_surface(setcolor=rim_color, unsetcolor=(0, 0, 0, 0))
    out = _new()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(rim, (dx, dy))
    out.blit(surf, (0, 0))
    return out


# Roll clamp keeps the wide planform from rolling so far it collapses edge-on or
# rotates the keel into a backward-kite read; intentionally tight for a glider.
_ROLL_MAX = 4.0


# =============================================================================
# KEEL GLIDER (manila) — production
#
# Wide flat wings flanking a BOLD raised central keel/fuselage strip that runs
# the full length nose->tail and stands proud as its own lit-vs-shadow ridge.
# The keel is the hero: a chunky paper spine the eye locks onto, with the wings
# as broad flat shelves either side. Two crisp rear points pin the WIDE wing
# read. Warm manila, held a notch below white so it never flares on day sky.
#
# Value structure (the work happens here, not in hue) at 40px:
#   * lit wing shelf (near/lower, faces light) vs a hard-darkened shadow shelf
#     (far/upper, tilts away) — the split is widened ~15% from Round 1 so the
#     central ridge reads as a 3D crease, not a soft gradient,
#   * the keel itself is a taller/wider dual-facet ridge: a bright lit top and a
#     distinctly darker shadow side, so the spine dominates the silhouette,
#   * a hard crease line caps the keel ridge,
#   * a baked 1px self-rim, tightened on the shadow side, guarantees the wide
#     planform on day AND night.
# =============================================================================
# Brightest manila held a notch below white (max ~238) so it never flares out
# against bright day sky or a pale pillar — verified against both.
_WING    = (210, 188, 142)        # lit wing shelf (near/lower, manila)
_WING_D  = (138, 116, 78)         # shadow wing shelf (far/upper) — ~15% darker
                                  #   value split than R1 so the ridge pops hard
_WING_DD = (120, 100, 66)         # deepest shadow wedge under the keel shoulder
_KEEL_L  = (238, 222, 184)        # raised keel ridge — lit top (held below white)
_KEEL_LH = (250, 240, 214)        # narrow nose-spine catch-light (not full white)
_KEEL_S  = (132, 110, 74)         # raised keel ridge — shadow side (hard-darkened)
_KEEL_C  = (96, 78, 50)           # keel crease (hard value break / hero ridge cap)
_RIM     = (84, 68, 46)           # baked self-rim — silhouette guarantee


def build_glider_wide(wing_angle_deg):
    """One flat KEEL GLIDER frame, nose RIGHT, on the 64x84 canvas.

    Geometry is locked so the nose is always the rightmost, narrowest cluster
    and the wide trailing span sits left/behind — the forward read the flat
    deltas lost. The keel is built taller/wider than the Round-1 take so the
    lit-spine-vs-shadow-shelf ridge is the dominant structure at gameplay scale."""
    surf = _new()
    f = _flutter(wing_angle_deg)
    # Tight roll + bob + pitch: a slow soaring sway. Clamped so the dive pose
    # never rotates the keel off its forward-right spine into a backward kite.
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 3.6))
    bob = -f * 1.1
    pitch = f * 0.05

    # ── Planform anchors ─────────────────────────────────────────────────────
    # Nose is a tight forward-RIGHT point (rightmost, narrowest). The two rear
    # corners are pulled to CRISP points and splayed wide (the trailing span) so
    # the silhouette reads as a deliberate WIDE wing, not a narrow dart.
    nose      = (BCX + 23, BCY)
    far_tip   = (BCX - 19, BCY - 19)        # upper (shadow) rear point — crisp
    near_tip  = (BCX - 19, BCY + 19)        # lower (lit) rear point — crisp
    tail_in   = (BCX - 13, BCY)             # trailing notch toward the keel

    def bk(pts):
        return _bank(pts, BCX, BCY, roll, bob, pitch)

    # ── Wing shelves (the wide flats either side of the keel) ────────────────
    # Far (upper) shelf in shadow — tilts away from light. Near (lower) shelf
    # lit — faces the viewer/light. Hard value split so the ridge is a crease.
    _poly(surf, _WING_D, bk([nose, far_tip, tail_in]))
    _poly(surf, _WING,   bk([nose, near_tip, tail_in]))
    # Deepest wedge in the shadow shelf right under the keel shoulder, so the
    # crease has a dark floor to pop against at 40px.
    _poly(surf, _WING_DD, bk([(BCX + 4, BCY), far_tip, tail_in]))

    # ── BOLD raised central keel (the hero ridge), nose -> tail ──────────────
    # Built ~20% taller/wider than Round 1 as two facets so the spine carries
    # its own lit top + shadow side and DOMINATES the silhouette. The lit top is
    # the upper half of the ridge (catches light); the shadow side is the lower
    # half (turns away) and is hard-darkened so the spine reads 3D, not flat.
    keel_back = BCX - 16
    keel_sh  = bk([nose, (keel_back, BCY),     (keel_back, BCY + 5),
                   (BCX + 18, BCY + 2)])
    keel_top = bk([nose, (keel_back, BCY - 6), (keel_back, BCY),
                   (BCX + 18, BCY)])
    _poly(surf, _KEEL_S, keel_sh)
    _poly(surf, _KEEL_L, keel_top)

    # Hard crease capping the very top of the keel ridge — the hero fold line.
    a, b = bk([nose, (keel_back, BCY - 6)])
    pygame.draw.line(surf, _KEEL_C, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 2)
    # Second crease at the keel-to-shelf shoulder on the shadow side, so the
    # ridge reads as a raised box, not a painted stripe.
    c, d = bk([nose, (keel_back, BCY + 5)])
    pygame.draw.line(surf, _KEEL_C, (int(c[0]), int(c[1])),
                     (int(d[0]), int(d[1])), 1)

    # Narrow nose-spine catch-light: a short bright run along the lit keel top
    # at the forward point — held below white so it never flares on day sky.
    e, g = bk([(BCX + 18, BCY - 2), (BCX + 4, BCY - 3)])
    pygame.draw.line(surf, _KEEL_LH, (int(e[0]), int(e[1])),
                     (int(g[0]), int(g[1])), 2)

    return _self_rim(surf, _RIM)


get_glider_wide = _make_prebuilt_skin(build_glider_wide)


# label -> getter dict (mirrors creature_skins.BUILDERS shape). Single
# production build, liftable into game/animal_paper_plane.py as the skin entry.
BUILDERS = {"skin_glider_wide": get_glider_wide}
