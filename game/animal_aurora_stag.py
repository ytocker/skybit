"""Production AURORA STAG skin for the ANIMALS Store — round-2 (v4 winner).

A LEGENDARY spectacle skin: a hooved land mammal (NOT a bird) as the flex.
The silhouette is a noble deer head/forebody crowned by two bold antler-beams
rendered as flowing northern-lights ribbons. Each antler is a SINGLE beam that
rises off the skull then curves FORWARD over the nose, with two short
forward-raked tines off its outer edge — a real stag rack, NOT a lyre/wishbone
— and each tip floats a 4-point star. A glowing crown that reads against
bright-day AND night skies.

There is NO live particle system feeding the sprite: the aurora glow + the
star-points are BAKED into each of the 4 flat frames. The "flap" (there are
no wings) is reinterpreted as the aurora beams rippling like curtains across
the 4 base wing poses — a coherent chroma PHASE travels up each beam frame-to
-frame so the crown shimmers — plus a small ear-flick on the up-pose.

Round-4 STRUCTURAL rebuild (art-director: the rack still read as a lyre):
  * The inward V is GONE. Beams no longer lean toward a shared centre knot;
    each beam throws FORWARD over the nose (+x), so no wishbone tell remains.
  * Each antler is ONE beam rising off the skull then curving forward, with
    TWO short forward-raked tines off its OUTER edge (brow + bez) — the
    forward throw is what makes it read "stag" instead of "lyre/horns".
  * Tip-stars rebuilt with ≥2px-thick N/S/E/W spokes + a 2px navy notch so
    each arm survives the 40px NEAREST downsample as a detached 4-point star
    instead of rounding to a blob.
  * Geometry re-anchored so under the dive rotation the beams stay OVER the
    head and the lower beam does not swing off-body as a loose green tail.
  * FROZEN: saturated violet #7A5CFF / green #3DF2C0 cores, the deep-navy
    #1E2A3A day-sky halo, the cool-spectrum-only palette (no pink/gold), and
    clip-safety inside 64×84 through the full dive rotation.

Contract mirrors game/animal_skins.py so this lifts straight in:

  * `build_aurora_stag(wing_angle_deg) -> pygame.Surface`  one flat frame on a
    64x84 SRCALPHA canvas. Body mass centred at (32,44); head near (44,34);
    the rack reaches UP into the top ~24px of headroom.
  * `get_aurora_stag = _make_prebuilt_skin(build_aurora_stag)` — cached
    `(frame_idx, tilt_deg) -> Surface` getter.
  * `BUILDERS = {"skin_aurora_stag": get_aurora_stag}` registry at the bottom.

Body anchoring: collision is a fixed 14px circle at the body centre, so the
body mass stays pinned at (32,44) even though the antlers are tall — the rack
never drags the body off-centre.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (rack reaches up into the headroom) ────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # headroom for the antler-rack
DY          = 12                # body offset down into the tall canvas

# Body / head anchors in composite space (base anchors + DY on y).
BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24


# ── aurora palette (cool full-spectrum violet↔green; NO pink/gold) ───────────
BODY      = (30, 42, 58)        # deep slate-blue
BODY_D    = (16, 24, 36)        # darker body for the fierce legendary read
BODY_DD   = (10, 16, 26)
BODY_H    = (58, 78, 104)
MUZZLE    = (10, 14, 22)
AUR_GREEN = (61, 242, 192)      # #3DF2C0  — saturated beam chroma
AUR_VIO   = (122, 92, 255)      # #7A5CFF  — saturated beam chroma
NAVY_HALO = (30, 42, 58)        # #1E2A3A  — dark contrast halo (day insurance)
STAR      = (255, 255, 255)


# ── shared factory (local copy of animal_skins._make_prebuilt_skin) ──────────
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


# ── tiny shared drawing helpers ──────────────────────────────────────────────
def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _eye(surf, cx, cy, r, *, iris=(14, 16, 24)):
    pygame.draw.circle(surf, (250, 250, 245), (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 2))
    pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                       max(1, r // 3))


def _flap(angle_deg):
    """0..1 'up' factor; _WING_ANGLES runs 50→-40 (down→up)."""
    return (angle_deg + 40) / 90.0


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _glow_dot(surf, color, pos, r, alpha=120):
    """Soft additive glow blob baked into the frame (no live particles)."""
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for rr in range(r, 0, -1):
        a = int(alpha * (1 - rr / r) ** 1.4)
        pygame.draw.circle(g, (*color, a), (r, r), rr)
    surf.blit(g, (int(pos[0] - r), int(pos[1] - r)),
              special_flags=pygame.BLEND_RGBA_ADD)


def _star(surf, pos, size, glow=AUR_GREEN, *, notch_from=None):
    """The signature floating star: a 4-point WHITE N/S/E/W cross whose spokes
    are drawn ≥2px THICK on a hot core, ringed by a coloured bloom and a soft
    halo. A 2px hard NAVY notch is punched between the star and the beam tip so
    the star reads as a DISCRETE detached point — the legendary tell — instead
    of a rounded blob fused to the beam.

    The 2px spoke width is the survival rule: at the in-game 40px NEAREST
    downsample a 1px spoke collapses to nothing and the star rounds to a blob;
    a 2px spoke keeps at least one lit pixel per arm so the cross still reads as
    a detached 4-point point after the nearest filter and the dive rotation.

    `notch_from` is the beam-tip pixel the star floats off; the navy notch is
    laid on the segment between it and the star so they separate at 1×."""
    x, y = int(round(pos[0])), int(round(pos[1]))
    # soft coloured halo so the star reads as a light source, not a dot.
    _glow_dot(surf, glow, (x, y), size * 2 + 2, alpha=120)
    # hard navy notch detaching the star from the beam tip (survives 1×).
    if notch_from is not None:
        fx, fy = int(round(notch_from[0])), int(round(notch_from[1]))
        pygame.draw.line(surf, NAVY_HALO, (fx, fy), (x, y), 2)
    # coloured bloom one pixel out from each white arm (the chroma rim).
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        pygame.draw.line(surf, (*glow, 220),
                         (x + dx * (size + 1), y + dy * (size + 1)),
                         (x + dx, y + dy), 1)
    # 4-point N/S/E/W cross with ≥2px-thick spokes so each arm survives the
    # nearest downsample as a detached point (the must-fix). Horizontal arms get
    # vertical thickness and vice-versa, with a 2px navy notch between the core
    # and the spoke tip so the four points stay individually legible.
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        tipx, tipy = x + dx * size, y + dy * size
        thick = 2 if size >= 3 else 2
        pygame.draw.line(surf, STAR, (x + dx, y + dy), (tipx, tipy), thick)
    # hot 2x2 white core anchoring the cross.
    pygame.draw.rect(surf, STAR, pygame.Rect(x - 1, y - 1, 3, 3))


def _aurora_ribbon(surf, pts, width, phase, *, hot=True):
    """A flowing aurora ribbon along a poly-spine.

    Drawn in THREE baked layers per segment so the beam owns a chroma read on
    a light sky AND separates from it:
      1. a deep-navy halo 1-2px wider than the core (dark contrast rim);
      2. the SATURATED violet↔green core (the beam mass — never near-white);
      3. an optional thin 1px white hot centerline (the only white in a beam).

    `phase` (0..1) slides the violet↔green blend up the ribbon frame-to-frame
    so a coherent chroma wave travels the beam — the baked-in 'ripple'."""
    n = len(pts)
    for i in range(n - 1):
        # coherent chroma phase travelling up the beam (not per-pixel jitter).
        t = (i / max(1, n - 2) + phase) % 1.0
        mix = 0.5 - 0.5 * math.cos(t * math.tau)        # smooth violet↔green
        col = _lerp(AUR_VIO, AUR_GREEN, mix)
        # taper width toward the tip.
        w = max(2, int(width * (1 - 0.45 * i / max(1, n - 1))))
        # 1) dark navy halo (baked day-sky separation).
        pygame.draw.line(surf, NAVY_HALO, pts[i], pts[i + 1], w + 3)
        # 2) saturated chroma core.
        pygame.draw.line(surf, col, pts[i], pts[i + 1], w)
        # 3) thin hot centerline — the only white inside the beam mass.
        if hot and w >= 3:
            pygame.draw.line(surf, (235, 245, 255), pts[i], pts[i + 1], 1)


def _ear(surf, base, sgn, flick, col, col_d):
    """A deer ear; `flick` lifts/rotates the tip on the up-pose."""
    bx, by = base
    tipx = bx + sgn * (6 + int(flick * 2))
    tipy = by - 9 + int(flick * 3)
    pygame.draw.polygon(surf, col_d,
                        [(bx, by), (tipx, tipy), (bx + sgn * 3, by - 2)])
    pygame.draw.polygon(surf, col,
                        [(bx + sgn, by - 1), (tipx - sgn, tipy + 2),
                         (bx + sgn * 3, by - 2)])


def _deer_head(surf, body, body_d, body_h):
    """Noble deer head/forebody anchored at the body centre.

    Returns the (skull-left, skull-right) ear-base x's so the rack grows from
    a consistent skull."""
    # Forebody / chest mass (kept centred at BCX,BCY for fair collision).
    _aaellipse(surf, body_d, (BCX + 1, BCY + 2), 16, 16)
    _aaellipse(surf, body, (BCX, BCY), 15, 15)
    _aaellipse(surf, body_h, (BCX - 4, BCY - 4), 7, 5)
    # Neck sweeping up to the head.
    pygame.draw.polygon(surf, body_d,
                        [(BCX + 4, BCY - 6), (BCX + 14, BCY - 12),
                         (HCX - 2, HCY + 8), (BCX + 2, BCY + 2)])
    pygame.draw.polygon(surf, body,
                        [(BCX + 5, BCY - 5), (BCX + 13, BCY - 11),
                         (HCX - 3, HCY + 7), (BCX + 4, BCY + 1)])

    # Long noble muzzle/head.
    _aaellipse(surf, body_d, (HCX, HCY + 1), 11, 9)
    _aaellipse(surf, body, (HCX - 1, HCY), 10, 8)
    snout = [(HCX + 4, HCY - 4), (HCX + 15, HCY + 1),
             (HCX + 13, HCY + 6), (HCX + 3, HCY + 6)]
    pygame.draw.polygon(surf, body, snout)
    pygame.draw.polygon(surf, body_d, snout, 1)
    pygame.draw.circle(surf, MUZZLE, (HCX + 13, HCY + 2), 2)   # nose
    _aaellipse(surf, body_h, (HCX - 3, HCY - 2), 4, 3)
    # Fierce regal almond eye + stern brow.
    _eye(surf, HCX + 2, HCY - 1, 3)
    pygame.draw.line(surf, body_d, (HCX - 1, HCY - 3), (HCX + 4, HCY - 3), 1)
    return (HCX - 6, HCX + 1)


# ═════════════════════════════════════════════════════════════════════════════
# AURORA STAG · FORWARD-THROW BEAM production build
#   Two antler beams, each rising off the skull then curving FORWARD over the
#   nose (never inward to a centre), with two short forward-raked tines off the
#   outer edge — a stag rack, not a lyre. Each beam is a saturated violet↔green
#   aurora ribbon with a baked navy halo and a big 4-point star crowning its
#   tip. A coherent chroma phase travels up the beams across the 4 frames; the
#   ears flick on the up-pose.
# ═════════════════════════════════════════════════════════════════════════════
def build_aurora_stag(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)                  # 0 down → 1 up
    phase = f * 0.5                            # chroma wave phase per frame

    skull_l, skull_r = _deer_head(surf, BODY_D, BODY_DD, BODY_H)
    flick = max(0.0, (f - 0.5) * 2)
    _ear(surf, (skull_l - 1, HCY - 4), -1, flick, BODY_D, BODY_DD)
    _ear(surf, (skull_r + 2, HCY - 5), +1, flick, BODY_D, BODY_DD)

    # TWO forward-throwing antler beams (NOT a lyre). This is the structural
    # fix: the old cut anchored both tines to a low inner arc that leaned the
    # tips inward toward a shared centre — a wishbone/heart. Here each antler is
    # ONE beam that rises UP off the skull then curves FORWARD over the nose
    # (toward +x), and its short tines branch off the OUTER edge throwing the
    # SAME forward way. Nothing points inward-down to a centre knot, so the pair
    # reads as a stag rack rather than a lyre. The near beam (right of skull)
    # rides forward over the muzzle; the far beam (left of skull) is the partner
    # behind it, given a tighter forward throw so the two never fuse.
    #
    #   beam_curve(): a beam rooted at (rx,ry) that sweeps up then leans FORWARD
    #   (always +x, regardless of which skull side) — the forward throw is the
    #   stag tell. `fwd` scales the over-the-nose lean; `rise` the height.
    def beam_curve(rx, ry, fwd, rise):
        pts = []
        steps = 8
        for i in range(steps + 1):
            t = i / steps
            # up first (the base is near-vertical), then a forward throw that
            # accelerates toward the tip (t**1.6) so the beam arcs OVER the nose
            # instead of leaning toward the midline.
            by = ry - rise * t
            bx = rx + fwd * (t ** 1.6) + 1.5 * math.sin(t * math.pi)
            pts.append((bx, by))
        return pts

    # The two beams are STAGGERED in depth so they read as a rack of two beams,
    # not a fused plume: the FAR (rear) beam roots further back/left, stands
    # taller and more upright behind; the NEAR (front) beam roots forward over
    # the muzzle, sits lower, and throws harder forward. Both lean +x — there is
    # no inward V — but their offset starts and unequal throws keep a clear gap
    # of sky between the two crowns. Far drawn first so near reads in front.
    beams = [
        ("far",  beam_curve(skull_l - 1, HCY - 6, fwd=6.0,  rise=30.0)),
        ("near", beam_curve(skull_r + 3, HCY - 3, fwd=13.0, rise=24.0)),
    ]
    for which, beam in beams:
        _aurora_ribbon(surf, beam, 5, phase)

        # TWO short forward-raked tines per beam off its OUTER (upper-forward)
        # edge, like real brow + bez tines — both throwing FORWARD (+x) and up,
        # never inward. Branch points sit a third and two-thirds up the beam.
        for bi in (3, 5):
            ax, ay = beam[bi]
            # spring off the outer/forward face of the beam core.
            bx0 = ax + 1
            by0 = ay - 1
            tine = [(bx0, by0),
                    (bx0 + 3, by0 - 3),       # forward + up
                    (bx0 + 6, by0 - 5)]       # forward + up tip
            _aurora_ribbon(surf, tine, 3, phase, hot=False)
            tine_glow = AUR_GREEN if which == "near" else AUR_VIO
            _star(surf, tine[-1], 2, glow=tine_glow, notch_from=tine[-2])

        # Big crowning 4-point tip-star — the signature, detached by a 2px navy
        # notch from the beam tip so it reads as a DISCRETE floating point at 1×
        # (the old blob fused to the beam). Seated a hair down the final segment
        # so the cross's north arm clears the canvas top.
        # Seat the star a touch inward (−1x) and down (+5y) from the apex so its
        # size-4 cross + bloom keep a clean ≥1px margin off the top/right canvas
        # edges through the dive rotation (the clip-safety contract).
        tipx, tipy = beam[-1]
        star_pos = (tipx - 1, tipy + 5)
        _star(surf, star_pos, 4,
              glow=(AUR_GREEN if which == "near" else AUR_VIO),
              notch_from=beam[-2])

    # Slim deer legs hinting the hooved body.
    for fx in (28, 37):
        pygame.draw.line(surf, BODY_DD, (fx, BCY + 13), (fx, BCY + 19), 2)
        pygame.draw.line(surf, MUZZLE, (fx, BCY + 19), (fx, BCY + 21), 2)
    return surf


get_aurora_stag = _make_prebuilt_skin(build_aurora_stag)


# ─────────────────────────────────────────────────────────────────────────────
# Production registry (lifts into game/animal_skins.py as "skin_aurora_stag").
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_aurora_stag": get_aurora_stag,
}
