"""Production PAPER PLANE skin — concept CLASSIC DART (round-2, ship build).

The iconic crisp WHITE printer-paper dart: sharp needle nose, a deep central
keel fold, clean swept facets. Timeless and minimal — the paper stays white /
steel-cream, that is the whole point of this concept. There are no wings; the 4
base wing poses (`parrot._WING_ANGLES`) are reinterpreted as a gentle
BANK/FLUTTER: the dart rolls a few degrees about its mass centre and the nose
bobs as it catches air, the way a real paper plane sways in flight.

This is the single converged build of the art-director's winner **v3 ·
DEEP-KEEL RAZOR**, with its round-2 punch list folded in:

  * Fuller trailing chord — the rear third of the wing now carries real body
    (the needle point stays razor-sharp, the mass behind it is thickened,
    borrowing v2's silhouette weight) so the dart never reads as a thread.
  * The keel stays DARK so the bright-wing / near-charcoal-keel value step is
    the fold that reads at 40px (rim alone is NOT relied on). A single 1px
    LIGHTER inner lip sits just below the crease where keel meets wing, so the
    fold reads as a connected fold (not a detached wedge) on a dark NIGHT sky
    too — that lip is a baked geometry detail, target-agnostic, so the one
    build is correct on day AND night with no runtime branch.
  * The crease is a HARD 1px value step (bright facet → dark keel), painted by
    polygon adjacency, never an anti-aliased ramp (a ramp greys out at 40px).
  * The bright upper facet always stays up-and-forward (nose-RIGHT) through the
    whole bank-roll/dive set, so the dart never reads as nosing backward.

Contract (mirrors game/animal_paper_plane.py so this lifts straight in):

  * `build_dart_classic(wing_angle_deg) -> pygame.Surface` draws one flat frame
    on a 64×84 SRCALPHA canvas (COMPOSITE_W=64, COMPOSITE_H=84), craft mass
    centred at (32, 44) — collision is a fixed 14px circle there.
  * NOSE POINTS RIGHT (forward) — drawn as-is, no host flip.
  * `get_dart_classic = _make_prebuilt_skin(build_dart_classic)` — a cached
    `(frame_idx, tilt_deg) -> Surface` getter.
  * `BUILDERS = {"skin_dart_classic": get_dart_classic}` registry.

North star: "a skin lives or dies at 40px in motion." The whole skin leans on
ONE bold triangular paper-airplane silhouette + a HARD-VALUE FOLD (bright upper
facet vs a distinctly darker under-keel meeting at a crisp central crease), and
bakes a 1px self-rim so the silhouette holds on day AND night without leaning on
a host outline.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── canvas constants (match game/animal_paper_plane.py) ──────────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body / mass centre → (32, 44)


# ── shared factory (local copy of animal_paper_plane._make_prebuilt_skin) ────
def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle). Lazy 4-frame build + per-(frame, 3°) rotation cache, each
    frame outlined with the house silhouette outline."""
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
    """Map a base wing angle (_WING_ANGLES runs 50→-40) to a centred −1..+1
    'catching air' factor. Drives the gentle bank-roll + nose-bob; there are no
    wings, so the flap energy goes entirely into the craft swaying."""
    return ((angle_deg + 40) / 90.0 - 0.5) * 2.0


def _poly(surf, color, pts, width=0):
    pygame.draw.polygon(surf, color, pts, width)


def _bank(pts, cx, cy, roll_deg, bob):
    """Roll a point list a few degrees about (cx, cy) and lift it by `bob`.

    The whole craft pivots about its mass centre so the silhouette banks as one
    rigid folded sheet — the cheapest, most paper-plane-honest read of 'flap'."""
    r = math.radians(roll_deg)
    cos_r, sin_r = math.cos(r), math.sin(r)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * cos_r - dy * sin_r,
                    cy + dx * sin_r + dy * cos_r + bob))
    return out


def _hardline(surf, color, p0, p1, width=1):
    """A crisp value-step line with NO anti-aliasing — a soft/AA crease washes
    to grey at 40px, so the fold must be a hard 1px step."""
    pygame.draw.line(surf, color, (int(round(p0[0])), int(round(p0[1]))),
                     (int(round(p1[0])), int(round(p1[1]))), width)


def _self_rim(surf, rim_color):
    """Bake a 1px rim hugging the painted silhouette so the dart stays legible
    on day AND night skies without leaning on the host outline. Built from the
    alpha mask so it traces the TRUE outer edge, stamped UNDER the art so it
    only shows as a clean lip."""
    mask = pygame.mask.from_surface(surf, threshold=8)
    rim = mask.to_surface(setcolor=rim_color, unsetcolor=(0, 0, 0, 0))
    out = _new()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(rim, (dx, dy))
    out.blit(surf, (0, 0))
    return out


# Roll clamp — the bank "flap" must never flatten the dart to a sliver (the
# under-keel collapses if the craft rolls too far edge-on).
_ROLL_MAX = 5.5


# ═════════════════════════════════════════════════════════════════════════════
# CLASSIC DART — DEEP-KEEL RAZOR (production)
#
# A long razor side profile: a sharp needle nose far right, a bright upper wing
# facet that keeps a FULL trailing chord (the rear third still carries body so
# the dart isn't a thread at 40px), and a DEEP near-charcoal under-keel hanging
# below the wing line. Bright wing vs dark keel = the fold, broken by a hard 1px
# crease + a 1px lighter inner lip so the keel reads as a connected fold on
# night, not a detached wedge. Cool steel-paper palette, fast & sharp.
# ═════════════════════════════════════════════════════════════════════════════
_TOP   = (248, 250, 253)            # lit upper wing facet (bright paper white)
_TOP_H = (255, 255, 255)            # leading-edge / nose specular
_KEEL  = (104, 116, 136)            # deep under-keel (dark — carries the fold)
_KEEL_D = (84, 96, 116)             # keel floor (deepest wedge)
_LIP   = (150, 162, 182)            # 1px lighter inner lip below the crease
_CREASE = (70, 82, 102)             # hard central crease (bright facet → keel)
_RIM   = (74, 86, 106)              # baked self-rim


def build_dart_classic(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3

    # Extra-long needle nose; tail held wide so the trailing chord stays full.
    nose       = (BCX + 30, BCY - 1)
    # Fuller trailing chord — the upper wing's back edge now spans tail_top→
    # crease_back, so the rear third still carries ~4px of body (borrowing v2's
    # silhouette mass) while the nose stays a razor point.
    tail_top   = (BCX - 14, BCY - 10)
    crease_back = (BCX - 16, BCY + 1)   # where the crease meets the tail
    keel_back  = (BCX - 15, BCY + 4)    # keel trailing edge (slightly below)
    keel_deep  = (BCX - 2, BCY + 16)    # the dramatic deep keel point

    # Deep keel triangle — a tall dark fold hanging below the wing line.
    _poly(surf, _KEEL, _bank([nose, keel_deep, keel_back], BCX, BCY, roll, bob))
    _poly(surf, _KEEL_D, _bank([nose, keel_deep, (BCX + 5, BCY + 6)],
                               BCX, BCY, roll, bob))

    # Bright upper wing facet — full trailing chord, razor nose.
    _poly(surf, _TOP, _bank([nose, tail_top, crease_back], BCX, BCY, roll, bob))
    _poly(surf, _TOP_H, _bank([nose, (BCX + 9, BCY - 5), (BCX + 11, BCY - 1)],
                              BCX, BCY, roll, bob))

    # 1px lighter inner lip just BELOW the crease (top of the keel) — lifts the
    # keel's upper edge ~12% so on night the keel reads as a connected fold, not
    # a detached wedge, without softening the bright-wing / dark-keel value step.
    la, lb = _bank([nose, keel_back], BCX, BCY, roll, bob)
    _hardline(surf, _LIP, la, lb, 1)

    # Hard 1px crease nose→tail — a value step (bright facet → dark keel), drawn
    # by adjacency so it never anti-aliases to grey at gameplay scale.
    a, b = _bank([nose, crease_back], BCX, BCY, roll, bob)
    _hardline(surf, _CREASE, a, b, 1)
    return _self_rim(surf, _RIM)


# ── getter + registry ────────────────────────────────────────────────────────
get_dart_classic = _make_prebuilt_skin(build_dart_classic)

BUILDERS = {"skin_dart_classic": get_dart_classic}
