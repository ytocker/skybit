"""Secret SUN skin — a RANDOM one of two sun designs, LOCKED at unlock.

A mystery store item (masked ??? until bought). When the player unlocks it ONE
of two hand-designed suns is rolled and that pick is persisted, so the same sun
shows every run rather than re-rolling each launch:

  * CLASSIC — the iconic gold sun-face: a full even corona of alternating
    long/short rays + a cheerful round-eyed face.
  * KAWAII  — a soft pastel chibi sun: pointed rays interleaved with rounded
    bobbles, huge sparkly eyes, blush + sparkles.

The roll happens at PURCHASE time in ``store_data`` (uniform over the pool) and
is written into the saved inventory; this module reads that index back and
renders it. A surprise once, then yours for keeps.

Both suns are reborn from the original pufferfish star-burst art; the puffer's
inflate gag became a SHINE pulse (rays flare + the disc brightens on the
down-stroke). Self-contained so its private helpers never collide with the other
animal modules.
"""
import math
import random

import pygame

from game import store_data
from game.parrot import (
    SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse,
)

# ── canvas + cache (match game/animal_skins.py) ──────────────────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY          # disc centre → (32, 44)


def _make_prebuilt_skin(build_fn):
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


def _shine(angle_deg):
    """1.0 = fully radiant on the down-stroke → ~0.0 on the up-stroke."""
    return 1.0 - (angle_deg + 40) / 90.0


def _shade(col, f):
    return tuple(max(0, min(255, int(c * f))) for c in col)


def _eye(surf, cx, cy, r, *, iris=(58, 42, 18), white=(255, 250, 240)):
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 2))
    pygame.draw.circle(surf, (255, 255, 255),
                       (cx - r // 3, cy - r // 3), max(1, r // 2))


def _radial_body(surf, cx, cy, r, core, mid, edge):
    """Sun disc value structure: dark rim → mid → light core (up-left) + a
    crisp specular, so the disc reads as a sphere rather than a flat coin."""
    _aaellipse(surf, edge, (cx + 1, cy + 1), r, r)
    _aaellipse(surf, mid,  (cx, cy), r - 1, r - 1)
    _aaellipse(surf, core, (cx - 2, cy - 2), r - 5, r - 5)
    _aaellipse(surf, _shade(core, 1.10), (cx - 5, cy - 6), 4, 3)


def _spike_ring(surf, cx, cy, r_in, length, n, col_base, col_tip, start=0.0,
                taper=0.42):
    """Radial corona of two-tone triangular rays — a dark base wedge + a brighter
    tip so the value step survives the 40px downscale."""
    half = math.radians((360.0 / n) * taper) * 0.5
    for i in range(n):
        a = start + (2 * math.pi) * i / n
        bx, by = math.cos(a), math.sin(a)
        l_a, r_a = a - half, a + half
        p_l = (cx + math.cos(l_a) * r_in, cy + math.sin(l_a) * r_in)
        p_r = (cx + math.cos(r_a) * r_in, cy + math.sin(r_a) * r_in)
        tip = (cx + bx * (r_in + length), cy + by * (r_in + length))
        m_l = (cx + math.cos(l_a) * (r_in + length * 0.40),
               cy + math.sin(l_a) * (r_in + length * 0.40))
        m_r = (cx + math.cos(r_a) * (r_in + length * 0.40),
               cy + math.sin(r_a) * (r_in + length * 0.40))
        pygame.draw.polygon(surf, col_base, [p_l, p_r, m_r, m_l])
        pygame.draw.polygon(surf, col_tip, [m_l, m_r, tip])


def _ray_ring_alt(surf, cx, cy, r_in, long_len, short_len, n, col_base, col_tip,
                  start=0.0, taper=0.42):
    """The classic sun corona: a full even ring of rays ALTERNATING long/short."""
    _spike_ring(surf, cx, cy, r_in, long_len, n, col_base, col_tip,
                start=start, taper=taper)
    _spike_ring(surf, cx, cy, r_in, short_len, n, col_base, col_tip,
                start=start + math.pi / n, taper=taper * 0.8)


def _stub_ring(surf, cx, cy, r_in, length, n, col_base, col_tip, start=0.0):
    """A corona of soft ROUNDED bobble rays (circles) — gentle scallops."""
    for i in range(n):
        a = start + (2 * math.pi) * i / n
        bx, by = math.cos(a), math.sin(a)
        tx, ty = cx + bx * (r_in + length), cy + by * (r_in + length)
        pygame.draw.circle(surf, col_base, (int(tx), int(ty)), max(2, length - 1))
        pygame.draw.circle(surf, col_tip,
                           (int(tx - 1), int(ty - 1)), max(1, length - 3))


def _sun_face(surf, cx, cy, *, eye_dx, eye_r, iris, blush=None):
    """The cartoon sun face: two friendly eyes, a gentle 'tiny' upward smile, and
    optional cheek blush, locked to the disc centre so it never slides."""
    if blush:
        pygame.draw.circle(surf, blush, (cx - eye_dx - 2, cy + 4), 2)
        pygame.draw.circle(surf, blush, (cx + eye_dx + 2, cy + 4), 2)
    _eye(surf, cx - eye_dx, cy, eye_r, iris=iris)
    _eye(surf, cx + eye_dx, cy, eye_r, iris=iris)
    my = cy + 6
    pygame.draw.arc(surf, (110, 64, 34), (cx - 4, my - 2, 8, 7), 3.5, 5.95, 2)


# ═════════════════════════════════════════════════════════════════════════════
# CLASSIC — the iconic gold sun-face.
# ═════════════════════════════════════════════════════════════════════════════
_CL_CORE = (255, 232, 154)
_CL_MID  = (255, 210, 62)
_CL_EDGE = (200, 146, 36)
_CL_RAY_B = (224, 150, 44)
_CL_RAY_T = (255, 240, 176)


def build_sun_classic(wing_angle_deg):
    surf = _new()
    sh = _shine(wing_angle_deg)
    r = 13 + int(sh * 1)
    cx, cy = BCX, BCY
    bf = 0.92 + 0.16 * sh
    core, mid, edge = _shade(_CL_CORE, bf), _shade(_CL_MID, bf), _shade(_CL_EDGE, bf)
    rb, rt = _shade(_CL_RAY_B, bf), _shade(_CL_RAY_T, bf)

    long_len = 9 + int(sh * 3)
    _ray_ring_alt(surf, cx, cy, r - 1, long_len, long_len - 4, 10, rb, rt,
                  taper=0.5)
    _radial_body(surf, cx, cy, r, core, mid, edge)
    _aaellipse(surf, _shade(_CL_CORE, bf * 1.06), (cx - 1, cy - 1), r - 7, r - 7)
    _sun_face(surf, cx, cy - 1, eye_dx=5, eye_r=3, iris=(70, 40, 16),
              blush=(255, 150, 120))
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# KAWAII — a soft pastel chibi sun.
# ═════════════════════════════════════════════════════════════════════════════
_KW_CORE = (255, 241, 194)
_KW_MID  = (255, 221, 102)
_KW_EDGE = (228, 176, 70)
_KW_RAY_B = (255, 192, 77)
_KW_RAY_T = (255, 240, 190)
_KW_SPARK = (255, 251, 234)


def build_sun_kawaii(wing_angle_deg):
    surf = _new()
    sh = _shine(wing_angle_deg)
    r = 13 + int(sh * 1)
    cx, cy = BCX, BCY
    bf = 0.94 + 0.12 * sh
    core, mid, edge = _shade(_KW_CORE, bf), _shade(_KW_MID, bf), _shade(_KW_EDGE, bf)
    rb, rt = _shade(_KW_RAY_B, bf), _shade(_KW_RAY_T, bf)

    # Pointed rays interleaved between rounded bobbles so it spikes like a sun.
    _spike_ring(surf, cx, cy, r - 2, 9 + int(sh * 2), 8, rb, rt,
                start=math.pi / 8, taper=0.5)
    _stub_ring(surf, cx, cy, r - 3, 5 + int(sh * 1), 8, rb, rt)
    _radial_body(surf, cx, cy, r, core, mid, edge)
    _sun_face(surf, cx, cy + 1, eye_dx=6, eye_r=5, iris=(96, 56, 24),
              blush=(255, 158, 176))
    # Sparkle glints off the corona.
    for sxp, syp in ((cx + r + 5, cy - 8), (cx - r - 4, cy + 6)):
        pygame.draw.line(surf, _KW_SPARK, (sxp - 2, syp), (sxp + 2, syp), 1)
        pygame.draw.line(surf, _KW_SPARK, (sxp, syp - 2), (sxp, syp + 2), 1)
        pygame.draw.circle(surf, _KW_SPARK, (sxp, syp), 1)
    return surf


get_sun_classic = _make_prebuilt_skin(build_sun_classic)
get_sun_kawaii  = _make_prebuilt_skin(build_sun_kawaii)


# ── random-1-of-2 lock (mirrors the secret jet fighter) ──────────────────────
# POOL_SIZE is the single source of truth for the roll range — store_data reads
# it back when it locks the design at purchase.
_POOL = (get_sun_classic, get_sun_kawaii)
POOL_SIZE = len(_POOL)

_chosen = None


def _apply(idx) -> None:
    global _chosen
    if idx is None or not (0 <= int(idx) < POOL_SIZE):
        # No persisted roll yet (legacy save, or a render before the unlock
        # landed): fall back to a uniform pick so a sun always shows.
        idx = random.randrange(POOL_SIZE)
    _chosen = _POOL[int(idx)]


def sync_from_store() -> None:
    """Lock the look to the index rolled at unlock (persisted in store_data).
    Call right after a fresh purchase so the store preview and the next run both
    show the same sun the player just unlocked."""
    try:
        _apply(store_data.skin_variant("skin_sun"))
    except Exception:
        _apply(None)


def get_sun(frame_idx, tilt_deg):
    if _chosen is None:
        sync_from_store()
    return _chosen(frame_idx, tilt_deg)


BUILDERS = {"skin_sun": get_sun}
