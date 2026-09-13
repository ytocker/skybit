"""GRIFFIN skin — round-2 SINGLE production build (the converged V4).

The griffin tops the late-game ANIMALS tier: an eagle-headed forebody fused to
a tawny lion hindquarter with a tufted tail. The whole job is to read as a
MYTHIC HYBRID at 40px in motion — and, above all, to read CLEARLY DISTINCT from
the plain bald-eagle skin that already ships (game/animal_skins.py:get_eagle).

The eagle alone is "white head + dark-brown body + hooked yellow beak." The
griffin's separation is built from four tells that survive the downscale:

  1. A lion HINDQUARTER + trailing TAIL kept OUTSIDE the wing footprint on every
     frame, so the rear never collapses into the eagle's brown body. The rump
     sits lower/rearward of the wing root and the inner near-wing edge is held
     clear of it — even on the wide down-pose.
  2. A real feather→fur VALUE STEP: the wing feathers are darkened + cooled
     (toward #6E4416) while the rump fur stays warm gold (#E8C24A), so the seam
     is a value break, not just a hue shift, and survives at 40px.
  3. A permanent chunky 3-blob dark-tipped TAIL TUFT trailing off the rear in
     ALL poses (not an up-pose-only flick) — the back-end lion anchor.
  4. A darker fur NECK-RUFF where the eagle head meets the lion body — the
     literal "two creatures joined" seam.

Contract mirrors game/animal_skins.py so this lifts straight in:

  * `build_griffin(wing_angle_deg) -> pygame.Surface`  one flat 64×84 frame.
  * `get_griffin = _make_prebuilt_skin(build_griffin)`  cached getter.
  * `BUILDERS = {"skin_griffin": get_griffin}`  registry at the bottom.

Body mass stays centred at (32,44); head near (44,34); collision is a fixed
14px circle at the body centre, so the lion body stays anchored there while the
wings/head/tail break the silhouette around that fixed mass.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (headroom for ear-tufts + upswept wings) ───────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # headroom for tufts / raised wings
DY          = 12                # body offset down into the tall canvas

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24


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


# ── tiny shared helpers ──────────────────────────────────────────────────────
def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(angle_deg):
    """0..1 'wing is up' factor. _WING_ANGLES runs 50→-40 (down→up)."""
    return (angle_deg + 40) / 90.0


def _rot_blit(surf, wing, anchor):
    surf.blit(wing, wing.get_rect(center=anchor).topleft)


# ── griffin palette ──────────────────────────────────────────────────────────
# Warm-gold lion fur vs darkened+cooled wing feathers: the value step between
# these two is THE 40px chimera tell, so the wing is pushed materially darker
# than the rump rather than a neighbouring brown.
FUR        = (232, 194, 74)         # #E8C24A warm tawny lion fur
FUR_D      = (176, 138, 40)
FUR_H      = (250, 224, 132)
FUR_RUFF   = (120, 84, 28)          # dark mane ruff at the eagle→lion join
WING       = (110, 68, 22)          # #6E4416 darkened, cooler wing feathers
WING_D     = (74, 44, 14)
WING_H     = (158, 110, 52)
HEAD       = (244, 228, 184)        # pale head feather underlay
HEAD_WHITE = (248, 248, 244)        # bald-eagle-style white head
HEAD_D     = (196, 198, 204)        # cool grey head shadow (holds a day edge)
HEAD_EDGE  = (118, 110, 96)         # dark edge ticked under the pale head
BEAK       = (255, 198, 56)         # gold raptor beak
BEAK_D     = (200, 142, 24)
DARK       = (58, 42, 18)           # #3A2A12 beak detail / eye / tuft tip
TUFT_TIP   = (46, 32, 14)           # near-black dark tail-tuft tip
RIM        = (201, 162, 58)         # #C9A23A rim


# ═════════════════════════════════════════════════════════════════════════════
# Raptor wing — darkened, cooled feathers with splayed primaries. Bigger span
# than the eagle's so the SOARING WIDE-WING flight read dominates the front.
# ═════════════════════════════════════════════════════════════════════════════
def _griffin_wing(angle_deg, *, span=58):
    w = pygame.Surface((span + 6, 48), pygame.SRCALPHA)
    s = span / 48.0
    tipx = int(20 + 26 * s)
    pygame.draw.polygon(w, WING_D, [(22, 24), (int(20 + 26 * s), 11),
                                    (int(23 + 26 * s), 24), (28, 39), (13, 32)])
    pygame.draw.polygon(w, WING, [(22, 24), (int(20 + 24 * s), 13),
                                  (int(20 + 24 * s), 26), (24, 35)])
    # Splayed primary feather tips (the raptor-wing read).
    for tx, ty in ((int(20 + 24 * s), 13), (int(22 + 25 * s), 18),
                   (int(20 + 24 * s), 25)):
        pygame.draw.polygon(w, WING_D,
                            [(tx - 4, ty), (tx + 3, ty - 1), (tx - 2, ty + 4)])
    # Two covert highlight strokes — feather grain catches light.
    pygame.draw.line(w, WING_H, (23, 25), (int(18 + 24 * s), 16), 1)
    pygame.draw.line(w, WING_H, (24, 31), (int(16 + 22 * s), 24), 1)
    return pygame.transform.rotate(w, angle_deg)


def _lion_rump(surf, cx, cy):
    """Tawny lion hindquarter: a warm-gold haunch with a thigh swirl + furred
    paw. Drawn so its rear bulge + tail root sit OUTSIDE the wing footprint —
    this is the silhouette tell that keeps the griffin off the eagle read."""
    _aaellipse(surf, FUR_D, (cx + 1, cy + 2), 16, 14)
    _aaellipse(surf, FUR, (cx, cy + 1), 15, 13)
    # Haunch / thigh swirl on the rear, catching the warm highlight.
    _aaellipse(surf, FUR_H, (cx - 8, cy - 1), 7, 7)
    pygame.draw.arc(surf, FUR_D, (cx - 14, cy - 6, 15, 18),
                    math.radians(40), math.radians(225), 2)


def _tail_tuft(surf, x, y):
    """Lion tail: a furred whip ending in a CHUNKY 3-blob dark-tipped tuft.
    Permanent in every pose (no up-pose-only flick) and drawn well clear of the
    rear so it always trails outside the wing footprint — the back-end tell that
    must survive 40px, so it is solid blobs, not thin radiating strokes."""
    # Whip from the haunch out to the low-rear tip.
    pygame.draw.line(surf, FUR_D, (x + 9, y - 3), (x - 4, y + 8), 4)
    pygame.draw.line(surf, FUR, (x + 9, y - 3), (x - 4, y + 8), 2)
    # Three stacked dark-tipped blobs make a fat club the downscale keeps.
    tx, ty = x - 4, y + 8
    for bx, by, r in ((tx + 2, ty - 3, 3), (tx - 1, ty + 1, 4), (tx + 1, ty + 5, 3)):
        pygame.draw.circle(surf, TUFT_TIP, (bx, by), r)
    pygame.draw.circle(surf, DARK, (tx, ty + 1), 2)


def _ear_tufts(surf, hx, crown):
    """Two short feather/fur ear-tufts breaking the crown — a griffin grace
    note, kept short so the beak stays the dominant head read."""
    for sgn, ex in ((-1, hx - 6), (1, hx + 5)):
        pygame.draw.polygon(surf, FUR_D,
                            [(ex, crown + 5), (ex + sgn * 2, crown - 4),
                             (ex + sgn * 4, crown + 4)])
        pygame.draw.line(surf, FUR, (ex + sgn * 1, crown + 4),
                         (ex + sgn * 2, crown - 3), 1)


def _hooked_beak(surf, hx, hy):
    """Sharp 2–3px hooked raptor beak. Outlined in dark beak color (#3A2A12)
    so the hook stays a crisp predator point on bright sky, not a gold smear."""
    upper = [(hx + 3, hy - 3), (hx + 15, hy), (hx + 13, hy + 5), (hx + 4, hy + 4)]
    pygame.draw.polygon(surf, BEAK, upper)
    # The down-hook — a sharp dark talon-tip.
    pygame.draw.polygon(surf, DARK,
                        [(hx + 12, hy + 2), (hx + 15, hy), (hx + 12, hy + 7)])
    pygame.draw.polygon(surf, DARK, upper, 1)
    pygame.draw.line(surf, (255, 235, 160), (hx + 5, hy), (hx + 12, hy + 1), 1)


def _raptor_eye(surf, hx, hy):
    pygame.draw.polygon(surf, (150, 110, 40),
                        [(hx - 6, hy - 4), (hx + 6, hy - 6),
                         (hx + 6, hy - 3), (hx - 5, hy - 1)])
    pygame.draw.circle(surf, (255, 220, 120), (hx + 2, hy - 1), 4)
    pygame.draw.circle(surf, DARK, (hx + 3, hy - 1), 2)
    pygame.draw.circle(surf, (255, 255, 255), (hx + 1, hy - 2), 1)


# ═════════════════════════════════════════════════════════════════════════════
# THE GRIFFIN — converged V4 SOARING WIDE-WING.
# Enormous swept raptor wings dominate the front; a warm-gold lion hindquarter
# rides LOW + REARWARD behind the wing root with a permanent dark-tipped tail;
# the pale eagle head thrusts forward over a dark fur neck-ruff. Big slow raptor
# beat: both wings swing through a wide arc deep-down → high-up.
# ═════════════════════════════════════════════════════════════════════════════
def build_griffin(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    beat = (f - 0.5) * 30           # symmetric raptor beat through a wide arc

    # Far wing — huge, sweeps opposite the near wing for depth.
    _rot_blit(surf, _griffin_wing(28 + beat, span=56), (BCX + 14, BCY - 5))

    # ── Lion hindquarter — pushed LOW + REARWARD so its rump bulge and the
    #    tail root sit OUTSIDE the near-wing footprint on every frame (esp. the
    #    wide down-pose). This is what keeps the back half unmistakably lion.
    rump_cx, rump_cy = BCX - 4, BCY + 3
    _lion_rump(surf, rump_cx, rump_cy)

    # Permanent chunky dark-tipped tail trailing off the low rear, in all poses.
    _tail_tuft(surf, 12, BCY + 6)

    # Feathered pale forebody patch — the eagle chest over the front, with a
    # crisp diagonal seam against the warm rump (the material split).
    chest = [(BCX + 3, BCY - 10), (BCX + 16, BCY - 4),
             (BCX + 15, BCY + 9), (BCX + 1, BCY + 11), (BCX - 1, BCY)]
    pygame.draw.polygon(surf, HEAD_D, chest)
    pygame.draw.polygon(surf, HEAD_WHITE,
                        [(BCX + 4, BCY - 8), (BCX + 14, BCY - 3),
                         (BCX + 13, BCY + 5), (BCX + 2, BCY + 6)])
    # Dark ticks down the seam so the feather→fur boundary reads as an edge.
    for sy in (BCY - 4, BCY + 2, BCY + 8):
        pygame.draw.line(surf, FUR_RUFF, (BCX - 2, sy), (BCX + 2, sy + 1), 1)

    # ── Dark fur NECK-RUFF where the eagle head meets the lion body — the
    #    literal two-creature join, a small radiating mane collar.
    ruff_cx, ruff_cy = BCX + 8, BCY - 8
    for ang in range(-70, 120, 24):
        ex = ruff_cx + int(math.cos(math.radians(ang)) * 9)
        ey = ruff_cy + int(math.sin(math.radians(ang)) * 8)
        pygame.draw.line(surf, FUR_RUFF, (ruff_cx, ruff_cy), (ex, ey), 3)
    _aaellipse(surf, FUR_RUFF, (ruff_cx, ruff_cy), 5, 4)
    _aaellipse(surf, FUR_D, (ruff_cx, ruff_cy), 3, 3)

    # ── Pale eagle head thrust forward, with a dark internal edge so it holds
    #    a silhouette on bright day sky (the house outline pass handles the
    #    outer edge; this ticks the head off the sky from the inside too).
    _aaellipse(surf, HEAD_EDGE, (HCX, HCY + 1), 12, 12)
    _aaellipse(surf, HEAD_D, (HCX, HCY + 1), 11, 11)
    _aaellipse(surf, HEAD_WHITE, (HCX - 1, HCY), 10, 10)
    _ear_tufts(surf, HCX, CROWN_Y)
    _raptor_eye(surf, HCX, HCY)
    _hooked_beak(surf, HCX, HCY)

    # Near wing — the hero, enormous, swings through the big beat. The inner
    # root is anchored forward/high so its lower-inner edge clears the lion
    # rump + tail that ride behind it.
    _rot_blit(surf, _griffin_wing(-28 - beat, span=60), (BCX - 8, BCY - 1))

    # Furred lion fore-paws (front legs) tucked under the chest.
    for fx in (29, 37):
        pygame.draw.line(surf, FUR_D, (fx, BCY + 12), (fx, BCY + 16), 2)
        pygame.draw.circle(surf, DARK, (fx, BCY + 16), 1)
    return surf


get_griffin = _make_prebuilt_skin(build_griffin)


# ─────────────────────────────────────────────────────────────────────────────
# Production registry (liftable into game/animal_skins.py).
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_griffin": get_griffin,
}
