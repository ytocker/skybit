"""RED PANDA Store skin — round-2 production build (single primary design).

Round 1 fielded five takes; the art-director picked **v3 BIG-TAIL HERO** to
iterate. This round folds the whole punch list into ONE ship candidate
`build_red_panda` and drops the exploration variants — the gacha sheet now
shows the refined design, not a chooser.

A round russet fluffball with a giant cream-and-rust RINGED TAIL looming
behind a slightly-shrunk body, and a bright white face-mask lifted clear of
the tail base. The skin is the player's flappy bird: it animates over the 4
base wing poses (`parrot._WING_ANGLES`, 50→-40) and is rotated by dive/climb
tilt by the shared getter factory.

Contract mirrors game/animal_skins.py so the winner lifts straight in:

  * `build_red_panda(wing_angle_deg) -> pygame.Surface`  one flat 64×84 frame.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)` — 4 flat frames + per-(frame, 3°) rotation
    cache, each run through `parrot._add_outline` (the house 1-px dark keyline
    that keeps the russet edge alive on near-white day skies).
  * `BUILDERS = {"skin_red_panda": get_red_panda}` — liftable label→getter.

Why the geometry sits where it does: collision is a fixed 14px circle at the
BODY centre, so the body mass stays anchored at BCX/BCY (32,44) regardless of
how far the tail arcs — the fat tail is silhouette flourish, never collision
mass. The tall canvas gives ear/tail headroom while the body keeps the base
anchor so the in-game centre-blit rotation maths still holds.

North star: "a skin lives or dies at 40px in motion." The ringed-tail arc +
white face-mask are the two reads engineered to survive 40px NEAREST.

There is NO red panda flight in nature, so the "flap" is reinterpreted as a
LEAP-AND-BALANCE: the big tail sweeps UP on the down-pose (counterweight for
lift) and the paws tuck on the up-pose. Crucially the tail-arc geometry and
the mask are pose-INVARIANT (only the paw drop + a few-degree arc flex move),
so the two 40px reads are identical across all four frames.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (ear + tail-arc headroom) ──────────────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12                # body offset down into the tall canvas

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter — lazy 4-frame build +
    per-(frame, 3°) rotation cache, each frame house-outlined."""
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


# ── red-panda palette ─────────────────────────────────────────────────────────
# Three tail values are deliberately spread so the rings hold in grayscale
# (CREAM ≈ 0.95 luma · FUR ≈ 0.40 · SEAM ≈ 0.18) — the colourblind/value test.
FUR     = (193, 68, 14)         # #C1440E russet body + tail base band
FUR_D   = (150, 48, 8)          # body shade
FUR_H   = (224, 110, 44)        # body highlight
RING    = (122, 42, 12)         # #7A2A0C dark tail ring + belly/feature rim
SEAM    = (74, 36, 16)          # #4A2410 near-black hard separation seam + legs
CREAM   = (255, 244, 230)       # #FFF4E6 mask + belly + ring-spots + tail tip
CREAM_W = (255, 252, 248)       # near-pure white terminal tail-tip punctuation
CREAM_D = (224, 200, 176)       # mask warmth shade (borrowed from v1)
EYEDK   = (58, 26, 12)          # #3A1A0C eyes + nose


def _eye(surf, cx, cy, r, *, iris=(58, 26, 12), white=(255, 250, 244)):
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 1))
    pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                       max(1, r // 3))


def _flap(angle_deg):
    """0..1 'pose is up'. _WING_ANGLES runs 50→-40, so 0 = deep down-pose
    (tail swept high), 1 = up-pose (paws tucked)."""
    return (angle_deg + 40) / 90.0


def _paw_pair(surf, by, f, col=SEAM):
    """Two little forepaws that TUCK up on the up-pose (f→1) and hang on the
    down-pose (f→0) — the only body element that animates, so the 40px tail +
    mask reads stay identical across poses."""
    drop = int(6 - f * 5)
    for fx in (28, 38):
        pygame.draw.line(surf, col, (fx, by), (fx, by + drop), 3)
        pygame.draw.circle(surf, col, (fx, by + drop), 2)


# ── the giant ringed tail (the brand) ─────────────────────────────────────────
def _ringed_tail_arc(surf, cx, cy, r, width, start, span, n_spots):
    """Fat ringed tail laid along a circular arc, drawn in three passes so the
    rings read as separated cream SPOTS rather than a continuous blur:

      1. a SEAM under-stroke (slightly larger radius bias toward the body) so a
         hard dark edge sits between the arc and the back — punch-list item 2.
      2. the solid russet plume body.
      3. ~`n_spots` clearly separated cream ring-spots at fixed arc fractions,
         each ringed in dark for a crisp edge — punch-list item 3 / 8.

    The terminal end gets a near-WHITE bright tip as the high-contrast arc
    punctuation (borrowed from v5) — punch-list item 7."""
    # 1 · dark separation seam on the INNER (body-facing) flank of the plume.
    steps = 26
    for i in range(steps + 1):
        a = start + span * (i / steps)
        px = cx + math.cos(a) * (r - width * 0.55)
        py = cy + math.sin(a) * (r - width * 0.55)
        pygame.draw.circle(surf, SEAM, (int(px), int(py)), width)

    # 2 · solid russet plume body laid over the seam.
    for i in range(steps + 1):
        a = start + span * (i / steps)
        px = cx + math.cos(a) * r
        py = cy + math.sin(a) * r
        pygame.draw.circle(surf, FUR, (int(px), int(py)), width)
    # A darker outer shade rim on the lit upper flank gives the plume depth.
    for i in range(steps + 1):
        a = start + span * (i / steps)
        px = cx + math.cos(a) * (r + width * 0.5)
        py = cy + math.sin(a) * (r + width * 0.5)
        pygame.draw.circle(surf, FUR_D, (int(px), int(py)), max(1, width // 2))

    # 3 · separated cream ring-spots at fixed fractions (skip the very base so
    #     the spots don't crowd the body). Each cream spot is dark-ringed so it
    #     holds an edge against the russet and survives grayscale.
    spot_r = max(2, int(width * 0.62))
    for k in range(n_spots):
        t = (k + 0.7) / (n_spots + 0.3)        # bias toward the tip half
        a = start + span * t
        px = cx + math.cos(a) * r
        py = cy + math.sin(a) * r
        pygame.draw.circle(surf, RING, (int(px), int(py)), spot_r + 1)
        pygame.draw.circle(surf, CREAM, (int(px), int(py)), spot_r)

    # Bright near-white terminal tip — the loud end-punctuation of the arc.
    a = start + span
    tx = cx + math.cos(a) * r
    ty = cy + math.sin(a) * r
    pygame.draw.circle(surf, SEAM, (int(tx), int(ty)), width + 1)
    pygame.draw.circle(surf, CREAM_W, (int(tx), int(ty)), width)


def _ear(surf, cx, cy, r, sgn):
    pygame.draw.circle(surf, FUR_D, (cx, cy), r)
    pygame.draw.circle(surf, CREAM_D, (cx + sgn, cy + 1), max(1, r - 2))


def _mask(surf, hx, hy, w, h):
    """White panda face-mask: warm cream cheek blobs + a centre blaze with a
    warm shade underside (v1 warmth), and rust tear-tracks back to the eyes.
    Sized up ~18% from round 1 so the face reads, not just the tail."""
    # Warm shade pass first, offset down, then the bright cream over it.
    _aaellipse(surf, CREAM_D, (hx - 5, hy + 4), w, h)
    _aaellipse(surf, CREAM_D, (hx + 6, hy + 4), w, h)
    _aaellipse(surf, CREAM,   (hx - 5, hy + 2), w, h)
    _aaellipse(surf, CREAM,   (hx + 6, hy + 2), w, h)
    _aaellipse(surf, CREAM,   (hx, hy + 3), 5, h)
    for dx in (-6, 7):                          # rust tear-tracks to the eyes
        pygame.draw.line(surf, FUR_D, (hx + dx, hy - 4),
                         (hx + dx + (1 if dx > 0 else -1), hy + 4), 2)


def build_red_panda(wing_angle_deg):
    """Single production BIG-TAIL HERO red-panda frame (64×84 SRCALPHA)."""
    surf = _new()
    f = _flap(wing_angle_deg)
    lift = (1 - f)                              # tail sweeps up on the down-pose

    # GIANT ringed tail arc sweeping from low-back up over the upper-left. Drawn
    # FIRST so the body + dark seam overlap it and lift the head clear of it.
    tcx, tcy = BCX + 3, BCY + 9
    _ringed_tail_arc(
        surf, tcx, tcy, r=26, width=9,
        start=math.radians(138),
        span=math.radians(150) + lift * math.radians(16),
        n_spots=5,
    )

    # Hard dark seam stamped where the body meets the tail arc — a clean value
    # break so the russet back doesn't muddy into the russet plume at 40px.
    pygame.draw.circle(surf, SEAM, (BCX - 2, BCY - 2), 15)

    # Body — slightly smaller than the head so the tail dominates, sat low-right
    # and lifted clear of the tail base.
    bcy = BCY + 2
    _aaellipse(surf, FUR_D, (BCX + 5, bcy + 1), 14, 13)
    _aaellipse(surf, FUR,   (BCX + 4, bcy), 13, 12)
    # White belly anchor with a 1-px dark rim so it holds an edge on day skies.
    _aaellipse(surf, RING,  (BCX + 6, bcy + 5), 9, 8)
    _aaellipse(surf, CREAM, (BCX + 6, bcy + 5), 8, 7)
    _aaellipse(surf, FUR_H, (BCX + 1, bcy - 4), 5, 3)

    _paw_pair(surf, bcy + 11, f)

    # Head — grown ~18% and lifted clear of the tail base so the face reads as
    # the second loud element (not just stripe pattern). Drawn last so it sits
    # cleanly over both tail and body.
    hcx, hcy = HCX, HCY - 1
    _aaellipse(surf, FUR_D, (hcx + 1, hcy + 1), 14, 13)
    _aaellipse(surf, FUR,   (hcx, hcy), 13, 12)
    _ear(surf, hcx - 8, CROWN_Y + 3, 6, -1)
    _ear(surf, hcx + 9, CROWN_Y + 3, 6, +1)
    _mask(surf, hcx, hcy, 7, 8)

    _eye(surf, hcx - 4, hcy, 3)
    _eye(surf, hcx + 6, hcy, 3)
    pygame.draw.circle(surf, EYEDK, (hcx + 1, hcy + 6), 2)        # nose
    pygame.draw.line(surf, EYEDK, (hcx + 1, hcy + 7), (hcx + 1, hcy + 9), 1)
    return surf


# ── getter + label→getter registry (mirrors animal_skins.BUILDERS) ───────────
get_red_panda = _make_prebuilt_skin(build_red_panda)

BUILDERS = {"skin_red_panda": get_red_panda}
