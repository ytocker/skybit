"""Production CHAMELEON skin for the ANIMALS Store — round-2 (converged).

Round-1 winner was v3 SPOTTED PANTHER. This is the single ship build that
addresses the art-director punch list. A chameleon has no wings, so the
"flap" is reinterpreted as the creature's signature MOOD-SHIFT: across the 4
base wing poses the body's COLOUR BAND walks through one hue stop per frame
(teal → violet → coral → amber) so the live skin reads as colour-changing in
motion, and a coral tongue darts out on the up-pose as the flap accent.

The mood-shift is deliberately concentrated into ONE legible ~6-8px band so it
survives the 40px downscale: the three white vertical bars AND the spot cluster
flush to the SAME frame hue together, instead of scattered 1px dots that wash
out. A constant teal anchor (base ellipse + dark rim + casque-shadow) holds the
silhouette steady through the whole cycle so it never disappears mid-shift on
either bright-day or night skies.

Contract mirrors game/animal_skins.py so the winner lifts straight in:
  * `build_chameleon(wing_angle_deg) -> pygame.Surface` draws one flat frame on
    a 64×84 SRCALPHA canvas; body mass centred at (32,44), head near (44,34).
  * `get_chameleon = _make_prebuilt_skin(build_chameleon)` cached getter.
  * `BUILDERS = {"skin_chameleon": get_chameleon}` registry at the bottom.

Key light is top-left to match the roster (highlights pushed up-and-left:
belly sheen, casque leading edge, eye catchlight at (-1,-1)).
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (headroom is for the casque crest) ─────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter (local copy)."""
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


def _flap(angle_deg):
    """0..1 'up' factor. _WING_ANGLES runs 50→-40 (down→up)."""
    return (angle_deg + 40) / 90.0


def _frame_index(angle_deg):
    """Map a wing angle back to its 0..3 frame ordinal so the mood-shift can
    take exactly one discrete hue stop per frame (no in-between blends that
    would smear the band)."""
    best, bi = 1e9, 0
    for i, a in enumerate(_WING_ANGLES):
        d = abs(a - angle_deg)
        if d < best:
            best, bi = d, i
    return bi


# ── constant teal anchor (never shifts — holds the silhouette every frame) ───
_BASE   = (46, 156, 156)        # teal body fill, kept across all 4 frames
_BASE_D = (22, 96, 100)         # dark teal rim / shadow, the steady anchor
_BASE_H = (118, 222, 214)       # top-left sheen
_BAR    = (228, 246, 244)       # neutral fallback (bars now take MOOD hue)

# ── the ONE mood band: teal → violet → coral → amber, one stop per frame ─────
# Index 0 stays a teal-leaning cyan so the "lightest"/coolest pose still anchors
# to the base; later stops swing warm. Each is picked to clear BOTH a bright-day
# sky and a night sky as a value (mid-to-light, never near-black, never white).
_MOOD = [
    (96, 226, 220),             # frame 0 · teal-cyan  (anchor-cool)
    (168, 120, 236),            # frame 1 · violet
    (255, 110, 128),            # frame 2 · coral
    (255, 188, 72),             # frame 3 · amber
]
_MOOD_D = [                     # matched darker rims for the spots/bars
    (40, 150, 150),
    (104, 64, 168),
    (190, 56, 78),
    (200, 130, 30),
]

_CASQUE   = (255, 200, 60)      # warm casque crest (constant gold)
_CASQUE_D = (196, 138, 34)
_CASQUE_H = (255, 236, 150)
_TONGUE   = (255, 96, 120)
_TONGUE_T = (255, 60, 100)


def _turret_eye(surf, cx, cy, r, *, look_x=0.0, look_y=0.0):
    """The signature swivel turret: a teal scaly cone capped by a pivoting
    pupil. The pupil is aimed per pose via (look_x, look_y) and ALWAYS carries a
    1px pure-white catchlight at the top-left so the eye stays alive in every
    pose, dive included."""
    pygame.draw.circle(surf, _BASE_D, (cx, cy), r)
    pygame.draw.circle(surf, _BASE, (cx, cy), r - 1)
    for rr in (r - 1, r - 3):                    # concentric scale rings
        if rr > 0:
            pygame.draw.circle(surf, _BASE_D, (cx, cy), rr, 1)
    pygame.draw.circle(surf, _BASE_H, (cx - 1, cy - 1), max(1, r - 4), 1)
    px = cx + int(round(look_x * (r - 3)))
    py = cy + int(round(look_y * (r - 3)))
    pygame.draw.circle(surf, (250, 248, 240), (cx, cy), max(2, r - 4))
    pygame.draw.circle(surf, (26, 30, 26), (px, py), max(1, r - 5))
    # Catchlight guaranteed in EVERY pose: anchored top-left of the aperture,
    # not the pupil, so a dive-aimed pupil can never push it off the white.
    pygame.draw.circle(surf, (255, 255, 255), (cx - 1, cy - 1), 1)


def _coil_tail(surf, cx, cy, turns, r0, dr, width, start):
    """A spiral-coiled prehensile tail. Drawn outer→inner but stopped one ring
    short of the centre so a single pixel of negative space survives at the
    core — it reads as a COIL, not a blob, even at 40px."""
    pts = []
    steps = int(turns * 16)
    inner_cut = 0.84                              # leave the very centre open
    for i in range(steps + 1):
        t = (i / steps) * inner_cut
        ang = start + t * turns * 2 * math.pi
        rad = r0 - dr * t
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    if len(pts) >= 2:
        pygame.draw.lines(surf, _BASE_D, False, pts, width)
        pygame.draw.lines(surf, _BASE_H, False, pts[:max(2, len(pts) // 2)],
                          max(1, width - 2))


def build_chameleon(wing_angle_deg):
    """One flat mood-shift frame. The hue stop is keyed to the discrete frame
    ordinal so the band walks teal→violet→coral→amber across the 4 poses."""
    surf = _new()
    f = _flap(wing_angle_deg)
    fi = _frame_index(wing_angle_deg)
    mood = _MOOD[fi]
    mood_d = _MOOD_D[fi]

    # Fat, tight coil curling under the rear — one pixel of open centre.
    _coil_tail(surf, 13, BCY + 11, 2.2, 9, 7, 4, math.radians(0))

    # Constant teal body mass (the steady anchor under the shifting band).
    _aaellipse(surf, _BASE_D, (BCX, BCY + 1), 17, 14)
    _aaellipse(surf, _BASE, (BCX - 1, BCY), 16, 13)
    # Top-left sheen (key light) so the form never reads flat.
    _aaellipse(surf, _BASE_H, (BCX - 6, BCY - 6), 7, 4)

    # ── THE mood band: three vertical bars + a spot cluster, all flushing to
    # the SAME frame hue so the shift reads as ONE ~7px band. The bar CORE is
    # the mood hue (so the colour dominates at 40px); a thin white edge keeps
    # the panther-banding tell without bleaching the shift. ──
    for bx in (BCX - 9, BCX - 2, BCX + 5):
        pygame.draw.line(surf, mood, (bx, BCY - 11), (bx, BCY + 11), 3)
        pygame.draw.line(surf, _BAR, (bx - 1, BCY - 10), (bx - 1, BCY + 10), 1)
    spots = [(-10, -3), (-3, 5), (4, -5), (9, 2), (1, -1)]
    for sx, sy in spots:
        pygame.draw.circle(surf, mood, (BCX + sx, BCY + sy), 3)
        pygame.draw.circle(surf, mood_d, (BCX + sx, BCY + sy), 3, 1)
    pygame.draw.ellipse(surf, _BASE_D, (BCX - 17, BCY - 14, 33, 27), 1)

    # Zygodactyl gripping feet (constant teal; toe tip carries the mood hue).
    for fx in (28, 36):
        pygame.draw.line(surf, _BASE_D, (fx, BCY + 12), (fx, BCY + 16), 3)
        pygame.draw.circle(surf, mood, (fx, BCY + 16), 2)

    # Head (constant teal so the face never washes out mid-cycle).
    _aaellipse(surf, _BASE_D, (HCX, HCY + 1), 11, 10)
    _aaellipse(surf, _BASE, (HCX - 1, HCY), 10, 9)

    # ── Casque crest: a HEAD-crest, not a dorsal fin. Wider base + a small
    # scallop notch on the trailing edge so it reads as a helmet ridge. ──
    casque = [
        (HCX - 7, HCY - 3),                      # wide base, front
        (HCX - 8, HCY - 8),
        (HCX - 4, CROWN_Y),                      # peak
        (HCX + 1, CROWN_Y - 3),                  # scallop dip
        (HCX + 4, CROWN_Y - 1),                  # second lobe
        (HCX + 8, HCY - 3),                      # wide base, rear
        (HCX + 7, HCY + 1),
    ]
    pygame.draw.polygon(surf, _CASQUE, casque)
    pygame.draw.polygon(surf, _BASE_D, casque, 1)
    # Top-left leading edge bright so the crest survives the downscale.
    pygame.draw.line(surf, _CASQUE_H, (HCX - 8, HCY - 7), (HCX - 4, CROWN_Y), 1)
    pygame.draw.line(surf, _CASQUE_D, (HCX + 4, CROWN_Y - 1), (HCX + 7, HCY), 1)

    # Big characterful turret — pupil aimed per pose, catchlight guaranteed.
    # Up-poses look up/forward; the dive (handled via tilt) keeps the aperture
    # catchlight regardless, and we aim the pupil slightly down as f drops.
    look_x = 0.35 + f * 0.4
    look_y = 0.45 - f * 0.9                       # up on the up-pose, down low
    _turret_eye(surf, HCX + 1, HCY - 2, 7, look_x=look_x, look_y=look_y)

    # Snout (constant teal).
    pygame.draw.polygon(surf, _BASE,
                        [(HCX + 7, HCY + 1), (HCX + 13, HCY + 2),
                         (HCX + 12, HCY + 6), (HCX + 7, HCY + 6)])
    pygame.draw.line(surf, _BASE_D, (HCX + 8, HCY + 5), (HCX + 12, HCY + 5), 1)

    # ── Tongue flick: a clear horizontal coral dart on the UP-pose only, the
    # single warm accent. Longer + flatter than round-1 so it reads at 40px. ──
    if fi == 3:
        x0 = HCX + 12
        tip = x0 + 11
        pygame.draw.line(surf, _TONGUE, (x0, HCY + 3), (tip, HCY + 3), 2)
        pygame.draw.circle(surf, _TONGUE_T, (tip, HCY + 3), 3)
        pygame.draw.circle(surf, (255, 200, 210), (tip - 1, HCY + 2), 1)
    return surf


get_chameleon = _make_prebuilt_skin(build_chameleon)


# ─────────────────────────────────────────────────────────────────────────────
# Production registry (liftable into game/animal_skins.py).
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {"skin_chameleon": get_chameleon}
