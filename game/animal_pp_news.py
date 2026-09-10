"""Production PAPER-PLANE skin — concept NEWSPRINT / COMIC (V3 · SUNDAY COMIC).

A secret premium NON-creature flyer: the player's flapping bird becomes a dart
folded from a sheet of SUNDAY-COMIC print. There are no wings — the 4 base wing
poses are reinterpreted as a gentle BANK/FLUTTER + nose-bob, exactly like the
production dollar-bill dart it would replace.

Contract (mirrors game/animal_paper_plane.py so this lifts straight back into
that standalone module):

  * `build_newsprint(wing_angle_deg) -> pygame.Surface`  draws ONE flat frame on
    a 64×84 SRCALPHA canvas, mass centred at the BODY anchor (32, 44).
  * NOSE POINTS RIGHT (forward) — the bird faces right, so the dart noses right.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_newsprint": get_newsprint}` at the bottom.

North star: "a skin lives or dies at 40px in motion." Newsprint is a trap — a
faithful grey page turns to mush at 40px. So the design leans on the SAME
load-bearing structure as the production dart, tuned for the comic read:

  * a HARD value FOLD: a bright upper facet meets a distinctly darker under-fold
    at a crisp 1px value-step crease, so the triangular dart silhouette survives
    even if the eye misses the colour;
  * the forward NOSE third stays clean light paper with an inked point, so the
    nose-RIGHT direction reads in a single frame;
  * the comic TELL lives in the TRAILING two-thirds: a warm Ben-Day halftone
    field framing exactly ONE saturated red POW starburst with ONE white-hot
    core dot — a value-and-shape mark (the colourblind anchor), not hue-only;
  * the dot field is a warm-print field (golden yellow + a capped warm-red
    minority) that never averages to muddy salmon at 40px;
  * a baked 1px self-rim so the dart holds on day AND night skies with no host
    outline.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline


# ── canvas constants (match game/animal_paper_plane.py) ──────────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY    = 32, 32 + DY       # body / mass centre → (32, 44)

# Roll is clamped so the bank-roll "flap" never flattens the dart to a sliver:
# at 3/4 view the under-fold collapses if the craft rolls too far edge-on.
_ROLL_MAX = 5.5


# ── shared factory (local copy of animal_paper_plane._make_prebuilt_skin) ────
def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle). Lazy 4-frame build + per-(frame, 3°) rotation cache,
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


def _clip_dots(surf, color, region_pts, x0, y0, x1, y1, step, r, roll, bob):
    """Stamp a Ben-Day halftone dot grid (rolled with the facet), clipped to a
    polygon region via a temp surface masked by the region. Hero-scale texture
    that frames the POW; it does NOT flood the lit nose facet."""
    tmp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    yy = y0
    row = 0
    while yy <= y1:
        xx = x0 + (step // 2 if row % 2 else 0)
        while xx <= x1:
            p = _bank([(xx, yy)], BCX, BCY, roll, bob)[0]
            pygame.draw.circle(tmp, color, (int(p[0]), int(p[1])), r)
            xx += step
        yy += step
        row += 1
    # Clip to the facet polygon so dots never spill past the fold/edge.
    clip = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(clip, (255, 255, 255, 255), region_pts)
    tmp.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(tmp, (0, 0))


def _rim(surf, color):
    """Bake a 1px self-rim hugging the painted silhouette, stamped UNDER the art
    so it shows only as a clean lip — the silhouette guarantee on any sky."""
    mask = pygame.mask.from_surface(surf, threshold=8)
    rim = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    out = _new()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(rim, (dx, dy))
    out.blit(surf, (0, 0))
    return out


# ═════════════════════════════════════════════════════════════════════════════
# V3 · SUNDAY COMIC — the winner. The lit facet is bright comic newsprint; the
# TRAILING two-thirds carry a warm Ben-Day halftone field that frames exactly
# ONE saturated red POW starburst with ONE white-hot core. The forward nose
# third stays clean light paper with an inked point so nose-RIGHT reads in a
# single frame. Hard 1px value fold guarantees the dart silhouette even mono.
# ═════════════════════════════════════════════════════════════════════════════
_TOP      = (240, 238, 228)         # bright comic newsprint (lit upper facet)
_TOP_H    = (252, 250, 244)         # nose / leading-edge highlight
_UNDER    = (150, 142, 126)         # shadowed under-fold (hard value break)
_UNDER_D  = (118, 110,  96)         # deepest under-fold wedge
_CREASE   = ( 58,  54,  46)         # central fold spine — crisp value step
_CREASE_LO = (96,  90,  78)         # 1px lit lip riding the crest of the fold
_RIM      = ( 50,  46,  40)         # baked self-rim — silhouette guarantee
# Warm-print Ben-Day field. Golden yellow dominates; the minority accent is a
# warm RED-ORANGE (never magenta) so yellow + accent average to "warm bright
# print", not a salmon/pink mush, when the facet collapses to ~16px at 40px.
_DOT      = (250, 204,  64)         # golden Ben-Day halftone (majority)
_DOT_WARM = (236, 132,  56)         # warm orange minority dot (stays warm small)
_INK      = ( 22,  20,  18)         # POW black outline / inked nose point
_BURST    = (218,  44,  40)         # POW red fill — the ONE saturated red mass
_CORE     = (252, 246, 226)         # ONE white-hot core dot (value anchor)


# Shared dart geometry. Top swept edge runs nose→far_tip as one straight line so
# the triangular dart silhouette is unambiguous; the nose is a tight point well
# past the mass centre.
def _geometry(roll, bob):
    nose        = (BCX + 25, BCY - 1)
    far_tip     = (BCX - 14, BCY - 13)
    near_tip    = (BCX - 12, BCY + 14)
    centre_back = (BCX - 16, BCY)
    far  = _bank([nose, far_tip, centre_back], BCX, BCY, roll, bob)   # lit top
    near = _bank([nose, near_tip, centre_back], BCX, BCY, roll, bob)  # under
    crease = _bank([nose, centre_back], BCX, BCY, roll, bob)
    return far, near, crease, nose


def build_newsprint(wing_angle_deg):
    """One flat Sunday-comic dart frame. Nose RIGHT, mass centred (32,44)."""
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3
    far, near, crease, nose = _geometry(roll, bob)

    # ── UNDER-fold first (lower facet, in shadow) ────────────────────────────
    _poly(surf, _UNDER, near)
    _poly(surf, _UNDER_D, _bank([nose, (BCX - 12, BCY + 14), (BCX - 5, BCY + 5)],
                                BCX, BCY, roll, bob))

    # ── TOP facet (lit upper wing) ───────────────────────────────────────────
    _poly(surf, _TOP, far)
    # Leading-edge highlight at the nose point — clean lit paper owns the front.
    _poly(surf, _TOP_H, _bank([nose, (BCX + 8, BCY - 7), (BCX + 10, BCY - 1)],
                              BCX, BCY, roll, bob))

    # ── Ben-Day halftone field — TRAILING two-thirds only ────────────────────
    # The region polygon stops well short of the nose so the front point stays
    # clean light paper; the field frames the POW from behind. Shrunk ~18% from
    # round 1 (tighter window + slightly smaller dots) so it never floods the
    # lit nose facet.
    field = _bank([(BCX + 8, BCY - 4), (BCX + 5, BCY - 9),
                   (BCX - 13, BCY - 12), (BCX - 15, BCY)], BCX, BCY, roll, bob)
    _clip_dots(surf, _DOT, field, BCX - 12, BCY - 11, BCX + 5, BCY - 1,
               4, 2, roll, bob)
    # Capped warm-orange minority pass — sparse + small so it tints the field
    # warm without ever averaging the golden field into pink at downscale.
    _clip_dots(surf, _DOT_WARM, field, BCX - 9, BCY - 9, BCX + 2, BCY - 3,
               7, 1, roll, bob)

    # ── HARD central crease (the fold spine) ─────────────────────────────────
    # A dark 2px spine with a 1px lit lip riding its upper crest = a crisp value
    # STEP, not a smear: the dart silhouette survives even if the eye misses the
    # red and even in pure value (the colourblind read).
    a, b = crease
    pygame.draw.line(surf, _CREASE, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 2)
    pygame.draw.line(surf, _CREASE_LO, (int(a[0]), int(a[1] - 1)),
                     (int(b[0]), int(b[1] - 1)), 1)

    # ── THE TELL: ONE black-outlined red POW starburst, pulled TRAILING ──────
    # Sat in the trailing third (left of mass centre) so the forward nose stays
    # a clean inked point and the dart's heading reads in one frame. Exactly one
    # saturated red mass + one white-hot core — a value-and-shape mark.
    cx, cy = _bank([(BCX - 6, BCY - 6)], BCX, BCY, roll, bob)[0]
    burst = []
    for i in range(10):
        ang = math.radians(i * 36 - 90)
        rr = 7 if i % 2 == 0 else 3.4
        burst.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr * 0.8))
    _poly(surf, _INK, burst)
    inner = [(cx + (p[0] - cx) * 0.74, cy + (p[1] - cy) * 0.74) for p in burst]
    _poly(surf, _BURST, inner)
    # ONE bright core so the star holds a hard centre highlight at downscale.
    pygame.draw.circle(surf, _CORE, (int(cx), int(cy - 1)), 2)

    # Inked nose point — a tight dark tick at the very tip so the clean light
    # nose still reads as a crisp folded POINT (direction cue) against bright sky.
    npx, npy = nose
    pygame.draw.line(surf, _INK, (int(npx), int(npy)),
                     (int(npx - 4), int(npy - 1)), 1)

    return _rim(surf, _RIM)


# ── getter + production registry ─────────────────────────────────────────────
get_newsprint = _make_prebuilt_skin(build_newsprint)

# Production registry (lifts straight into game/animal_paper_plane.py).
BUILDERS = {"skin_newsprint": get_newsprint}
