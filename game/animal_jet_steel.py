"""STEEL RAPTOR jet design — one of the secret JET FIGHTER pool.

Sleek gunmetal fighter: arrowhead body, swept delta wings, twin canted tails,
twin afterburner, with a thin warm rim-light as the premium tell and a constant
cool canopy anchor. The 4 base wing poses are an AFTERBURNER PULSE (baked glow
flares/shrinks; no live particles).

Drawn NOSE-RIGHT, UPRIGHT — the planform is laid out nose-left/canopy-up, then a
single horizontal flip faces it forward (the bird flies right). It carries NO
baked pitch rotation: the bird's velocity tilt is applied by the getter, so the
jet noses up when you flap and gradually noses down as it falls.

Exposes `build_steel` / `get_steel` / `BUILDERS = {"skin_steel": get_steel}`.
The fuselage mass stays at (32,44) on the 64×84 canvas (fixed 14px collision
circle); wings may span wider.
"""
import math
import pygame

from game import parrot
from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + body anchor (mirror animal_skins composite layout) ──────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # matches the creature composite height
DY          = 12
BCX, BCY = 32, 32 + DY          # fuselage centre → (32, 44)


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle): lazy 4-frame build + per-(frame, 3°) rotation cache,
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


def _pulse(angle_deg):
    """Afterburner pulse phase from the wing angle: the 4 poses (50→-40) map
    to a 0..1 'throttle' so the baked flame flares brightest on the middle
    two frames and shrinks at the ends — a heartbeat the eye reads as thrust."""
    t = (50 - angle_deg) / 90.0          # 50→0, 20→.33, -10→.67, -40→1
    return 1.0 - abs(t * 2.0 - 1.0)


def _pitch(angle_deg):
    """Tiny nose pitch (px) across the 4 frames so the jet visibly 'breathes'
    with the burner instead of sitting dead-still. ±1px is enough at 40px."""
    return int(round((_pulse(angle_deg) - 0.5) * 2.4))


def _baked_flame(length, width, core, mid, outer):
    """Bake ONE afterburner plume onto its own SRCALPHA surface: a layered
    teardrop — outer haze → mid → white-hot core — with shock-diamond beads
    down the centre. The core layer is kept NARROW so the twin white cores stay
    separate at 40px. Left edge is the nozzle mouth; the plume streams right."""
    pad = 6
    w = length + pad * 2
    h = width + pad * 2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cy = h // 2

    def teardrop(col, ln, hw, alpha):
        pts = []
        n = 14
        for i in range(n + 1):
            t = i / n
            x = pad + t * ln
            r = hw * math.sin(math.pi * (0.15 + 0.85 * (1.0 - t))) * (1.0 - 0.15 * t)
            pts.append((x, cy - r))
        for i in range(n + 1):
            t = (n - i) / n
            x = pad + t * ln
            r = hw * math.sin(math.pi * (0.15 + 0.85 * (1.0 - t))) * (1.0 - 0.15 * t)
            pts.append((x, cy + r))
        layer = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(layer, (*col, alpha), pts)
        surf.blit(layer, (0, 0))

    teardrop(outer, length,             width / 2.0,  140)
    teardrop(mid,   int(length * 0.74), width / 3.0,  210)
    teardrop(core,  int(length * 0.46), width / 5.0,  255)
    pygame.draw.circle(surf, (255, 255, 255, 255), (pad + 2, cy), max(1, width // 8))
    for k in range(1, 3):
        dx = pad + int(length * 0.16 * k) + 2
        rad = max(1, width // 10 - (k - 1))
        pygame.draw.circle(surf, (255, 250, 232, 235), (dx, cy), rad)
    return surf


def _glow(radius, color, alpha=120):
    """Soft radial halo baked once — the warm aura behind the burner, capped to
    the rear third so the nose stays dominant."""
    d = radius * 2
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    steps = 8
    for i in range(steps, 0, -1):
        a = int(alpha * (i / steps) ** 2)
        r = int(radius * i / steps)
        pygame.draw.circle(s, (*color, a), (radius, radius), r)
    return s


def _blit_c(surf, src, center):
    surf.blit(src, src.get_rect(center=center).topleft)


# ── STEEL RAPTOR palette ─────────────────────────────────────────────────────
_BODY    = (120, 128, 140)
_BODY_D  = (74, 80, 92)
_BODY_H  = (182, 190, 202)
_EDGE    = (44, 48, 58)          # darker-than-body gunmetal outline (value tell)
_RED     = (216, 60, 54)         # small warm accent only
_RIM     = (255, 196, 120)       # warm hot rim-light — THE premium signature
_RIM_HOT = (255, 232, 190)
_CANOPY  = (58, 150, 200)        # constant cool anchor
_CANOPY_H = (176, 228, 250)

# Twin nozzles sit on a WIDE vertical gap so the two white-hot cores never fuse.
_NOZ_DY = 8


def build_steel(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    # Planform laid out nose-LEFT here; a horizontal flip at the end faces it
    # nose-RIGHT (forward). Exhaust streams to +x (which becomes aft after flip).
    nose_x = 12 + pit
    tail_x = 50

    # ── Twin afterburner ─────────────────────────────────────────────────
    flame_len = int(13 + p * 11)
    halo_r = int((10 + p * 5) * 0.84)
    glow = _glow(halo_r, (255, 150, 64), alpha=int(60 + p * 60))
    flame = _baked_flame(flame_len, 8, (255, 255, 244), (255, 168, 60),
                         (236, 72, 36))
    for ny in (BCY - _NOZ_DY, BCY + _NOZ_DY):
        _blit_c(surf, glow, (tail_x + flame_len // 2 - 2, ny))
        surf.blit(flame, (tail_x - 2, ny - flame.get_height() // 2))

    # ── Twin canted tail fins ─────────────────────────────────────────────
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _BODY_D, [
            (tail_x - 6, BCY + sgn * 4), (tail_x + 6, BCY + sgn * 13),
            (tail_x + 9, BCY + sgn * 12), (tail_x + 2, BCY + sgn * 3)])

    # ── Delta wing pair, swept hard back from mid-fuselage ────────────────
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _BODY_D, [
            (nose_x + 18, BCY + sgn * 2), (tail_x - 2, BCY + sgn * 20),
            (tail_x + 4, BCY + sgn * 20), (tail_x - 6, BCY + sgn * 6)])
        pygame.draw.polygon(surf, _BODY, [
            (nose_x + 19, BCY + sgn * 2), (tail_x - 4, BCY + sgn * 18),
            (tail_x - 7, BCY + sgn * 6)])
        pygame.draw.polygon(surf, _BODY_H, [
            (nose_x + 20, BCY + sgn * 2), (nose_x + 30, BCY + sgn * 7),
            (tail_x - 8, BCY + sgn * 7), (tail_x - 7, BCY + sgn * 6)])
        pygame.draw.line(surf, _EDGE, (nose_x + 19, BCY + sgn * 2),
                         (tail_x - 4, BCY + sgn * 18), 1)
        pygame.draw.line(surf, _BODY_H, (tail_x - 4, BCY + sgn * 18),
                         (tail_x + 4, BCY + sgn * 18), 2)
        pygame.draw.circle(surf, _RED, (tail_x + 4, BCY + sgn * 18), 1)

    # ── Dart fuselage: long arrowhead ─────────────────────────────────────
    body = [(nose_x, BCY), (nose_x + 16, BCY - 6), (tail_x + 4, BCY - 5),
            (tail_x + 6, BCY), (tail_x + 4, BCY + 5), (nose_x + 16, BCY + 6)]
    pygame.draw.polygon(surf, _BODY, body)
    pygame.draw.polygon(surf, _EDGE, body, 1)
    pygame.draw.polygon(surf, _BODY_H,
                        [(nose_x + 4, BCY - 1), (nose_x + 16, BCY - 4),
                         (tail_x, BCY - 3), (tail_x, BCY - 1)])
    pygame.draw.polygon(surf, _BODY_D,
                        [(nose_x, BCY), (nose_x + 7, BCY - 2),
                         (nose_x + 7, BCY + 2)])
    pygame.draw.circle(surf, _RED, (nose_x + 1, BCY), 1)

    # ── Premium signature: thin WARM rim-light on the delta leading edges ──
    for sgn in (-1, 1):
        pygame.draw.line(surf, _RIM, (nose_x + 20, BCY + sgn * 2),
                         (tail_x - 5, BCY + sgn * 17), 1)
    for sgn in (-1, 1):
        pygame.draw.circle(surf, _RIM_HOT, (nose_x + 20, BCY + sgn * 2), 1)
    pygame.draw.line(surf, _RIM, (nose_x + 2, BCY - 1), (nose_x + 15, BCY - 5), 1)

    # ── Bubble canopy: the CONSTANT cool anchor across all 4 frames ───────
    _aaellipse(surf, _CANOPY, (nose_x + 14, BCY), 5, 3)
    _aaellipse(surf, _CANOPY_H, (nose_x + 12, BCY - 1), 2, 1)
    pygame.draw.circle(surf, _CANOPY_H, (nose_x + 12, BCY - 1), 1)
    for ny in (BCY - _NOZ_DY, BCY + _NOZ_DY):
        pygame.draw.circle(surf, (255, 206, 130), (tail_x, ny), 2)
        pygame.draw.circle(surf, (255, 255, 245), (tail_x - 1, ny), 1)

    # Face the jet NOSE-RIGHT (forward), upright. No baked pitch — the bird's
    # velocity tilt pitches the nose up on a flap and down on a fall.
    return pygame.transform.flip(surf, True, False)


get_steel = _make_prebuilt_skin(build_steel)

BUILDERS = {"skin_steel": get_steel}
