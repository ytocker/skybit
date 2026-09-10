"""Production JET FIGHTER redesign — NAVAL INTERCEPTOR (`naval`) round-2.

ONE converged build: **JOLLY ROGERS** (the art-director's round-1 winner).
An F-14 Tomcat / Top Gun carrier interceptor whose identity is NAVY
structure — variable-sweep WINGS, WIDE twin canted tail fins, a long tandem
fuselage, wide-spaced engine nacelles with a twin afterburner.

Restraint is the whole point of this round: the jet is ONE dark mass, ONE
continuous gold structural rail, ONE cool canopy, ONE warm burner — and
nothing else (no modex, no chevrons, no skull decal). Each accent is a
distinct hue *and* value so the read survives the 40px downscale and stays
colourblind-separable (warm burner vs gold rail vs cool canopy).

Why NAVY (not pure sea-black) base: pure black crushes to a featureless
hole on the night sky AND swallows its own dark silhouette outline. A deep
naval blue holds the silhouette on night while staying dark enough to sit
as one mass against the warm day sandstone pillars — the two hardest
backgrounds the in-game jet must survive.

The gold is a CONTINUOUS leading-edge RAIL, not caps: a 1px rim runs the
full length of each wing's leading edge and the top of each tail fin, so
the planform shape itself is described by the gold even at 40px (caps read
as 2-3 disconnected dots and lose the shape). A second baked self-rim — a
1px cool light-grey edge along the top/nose contour — keeps the dark
airframe from melting into a warm pillar in daylight, independent of the
house dark outline.

There is no flapping. The 4 base wing poses (`parrot._WING_ANGLES`) are
reinterpreted as an AFTERBURNER PULSE (+ a touch of nose pitch): the baked
twin exhaust flares and shrinks across the 4 frames, the nozzle footprint
changing ~2px between frames so the pulse is legible at 40px on the dark
body. No live particle system — the spectacle is baked per frame so both
build targets stay identical and cheap.

Contract (mirrors game/animal_jet_fighter.py so this lifts straight into a
production game/animal_jet_fighter.py):

  * `build_naval(wing_angle_deg) -> pygame.Surface`  draws ONE flat frame
    on a 64×84 SRCALPHA canvas, fuselage mass centred at (32,44).
  * The jet is drawn NOSE-RIGHT, UPRIGHT, LEVEL (clean top-down planform).
    NO baked rotation/flip — the game applies the inverted nose-up
    presentation later; here it just nudges right.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_naval)` (4 flat frames + per-(frame, 3°)
    rotation cache, each outlined with the house silhouette outline).
  * `get_naval = _make_prebuilt_skin(build_naval)` and
    `BUILDERS = {"skin_naval": get_naval}` register the single production
    build so the review sheet + production registry agree on one key.

Why the geometry sits where it does: collision is a fixed 14px circle at the
BODY centre, so the fuselage mass stays at (32,44) on the 64×84 canvas for
fairness — wings/stabs may span wider, but the body stays anchored so the
in-game center-blit rotation maths still holds.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + body anchor (mirror animal_jet_fighter composite layout) ────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
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
    """Afterburner throttle 0..1 from the wing angle: the 4 poses (50→-40)
    triangle-wrap to bright-bright in the centre, dim-dim at the ends — a
    heartbeat the eye reads as thrust at 40px without strobing."""
    t = (50 - angle_deg) / 90.0          # 50→0, 20→.33, -10→.67, -40→1
    return 1.0 - abs(t * 2.0 - 1.0)


def _pitch(angle_deg):
    """Tiny nose pitch (px) across the 4 frames so the jet 'breathes' with
    the burner instead of sitting dead-still. ±1px is enough at 40px."""
    return int(round((_pulse(angle_deg) - 0.5) * 2.4))


def _blit_c(surf, src, center):
    surf.blit(src, src.get_rect(center=center).topleft)


def _glow(radius, color, alpha=120):
    """Soft radial halo baked once — the warm aura behind the burner.
    Concentric fading rings so the glow supports the silhouette, never
    swallows it. Caller caps the radius to the rear third of the jet."""
    d = radius * 2
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    steps = 8
    for i in range(steps, 0, -1):
        a = int(alpha * (i / steps) ** 2)
        r = int(radius * i / steps)
        pygame.draw.circle(s, (*color, a), (radius, radius), r)
    return s


def _baked_flame(length, width, core, mid, outer):
    """Bake ONE afterburner plume on its own SRCALPHA surface: layered
    teardrop (outer haze → mid → white-hot core) + shock-diamond beads. The
    core stays NARROW vs the haze so two plumes keep two distinct white
    cores at 40px even when their soft hazes kiss.

    The plume's LEFT edge is the nozzle mouth and it streams RIGHT, so a
    nose-RIGHT jet blits it pointing aft (off the tail to the right)."""
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
            x = w - pad - t * ln
            r = hw * math.sin(math.pi * (0.15 + 0.85 * (1.0 - t))) * (1.0 - 0.15 * t)
            pts.append((x, cy - r))
        for i in range(n + 1):
            t = (n - i) / n
            x = w - pad - t * ln
            r = hw * math.sin(math.pi * (0.15 + 0.85 * (1.0 - t))) * (1.0 - 0.15 * t)
            pts.append((x, cy + r))
        layer = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(layer, (*col, alpha), pts)
        surf.blit(layer, (0, 0))

    teardrop(outer, length,             width / 2.0,  140)
    teardrop(mid,   int(length * 0.74), width / 3.0,  210)
    teardrop(core,  int(length * 0.46), width / 5.0,  255)
    # White-hot pinch right at the nozzle mouth (tight bright core seed).
    pygame.draw.circle(surf, (255, 255, 255, 255), (w - pad - 2, cy),
                       max(1, width // 8))
    for k in range(1, 3):
        dx = w - pad - int(length * 0.16 * k) - 2
        rad = max(1, width // 10 - (k - 1))
        pygame.draw.circle(surf, (255, 250, 232, 235), (dx, cy), rad)
    return surf


def _twin_burner(surf, tail_x, p, noz_dy, *, core, mid, outer, halo):
    """Twin afterburner aft of the tail: each nozzle gets its OWN tight halo
    (not one fused blob), halo radius capped to the rear so peak glow stays
    behind the silhouette. The plume LENGTH (hence the lit footprint behind
    each nozzle) swings ~13→24px across the pulse, so the burner footprint
    changes well over 2px between adjacent frames and stays legible at 40px
    on the dark body. Returns the nozzle-mouth y-pair so the caller can paint
    glowing nozzle mouths to root the flames."""
    flame_len = int(13 + p * 11)
    halo_r = int((10 + p * 5) * 0.84)
    glow = _glow(halo_r, halo, alpha=int(60 + p * 60))
    flame = _baked_flame(flame_len, 8, core, mid, outer)
    ys = (BCY - noz_dy, BCY + noz_dy)
    for ny in ys:
        _blit_c(surf, glow, (tail_x + flame_len // 2 + 2, ny))
        surf.blit(flame, (tail_x - flame.get_width() + flame_len + 4,
                          ny - flame.get_height() // 2))
    return ys


# Warm afterburner colour temperature — the single warm accent. Constant so
# the thrust tell is consistent; only the dark airframe carries the livery.
_F_CORE  = (255, 255, 244)
_F_MID   = (255, 168, 60)
_F_OUTER = (236, 72, 36)
_F_HALO  = (255, 150, 64)
_NOZ_HOT = (255, 206, 130)
_NOZ_WHT = (255, 255, 245)


def _nozzles(surf, tail_x, ys):
    for ny in ys:
        pygame.draw.circle(surf, _NOZ_HOT, (tail_x, ny), 2)
        pygame.draw.circle(surf, _NOZ_WHT, (tail_x - 1, ny), 1)


# ═════════════════════════════════════════════════════════════════════════════
# JOLLY ROGERS production livery.
#
# ONE dark mass — a deep NAVAL blue, dark enough to read as a single
# silhouette against warm day sandstone, light-holding enough not to crush on
# night. ONE gold structural rail. ONE cool canopy. ONE warm burner. Nothing
# else: restraint is the brief.
# ═════════════════════════════════════════════════════════════════════════════
_BODY    = (32, 38, 58)               # deep naval blue (the one dark mass)
_BODY_D  = (18, 22, 38)               # shadowed underside / nacelles
_BODY_H  = (66, 76, 104)              # spine catch-light
_EDGE    = (10, 12, 22)               # internal panel shade
_WING    = (28, 34, 52)
_WING_D  = (16, 20, 34)
_WING_H  = (58, 68, 96)
_SELFRIM = (176, 188, 206)            # cool light-grey baked self-rim (top/nose)
_GOLD    = (244, 198, 64)             # continuous structural leading-edge rail
_GOLD_H  = (255, 226, 138)            # rail catch-light at the wing root
_CANOPY  = (78, 150, 196)             # the single cool accent
_CANOPY_H = (180, 224, 248)


def _tandem_canopy(surf, x):
    """Two-seat tandem canopy: a stretched bubble with a faint frame split —
    the cool CONSTANT anchor across all 4 frames, colourblind-distinct from
    the warm burner and the gold rail. Drawn identically every frame so it
    stays a fixed landmark the eye locks onto."""
    _aaellipse(surf, _CANOPY, (x, BCY), 6, 3)
    pygame.draw.line(surf, _CANOPY_H, (x, BCY - 2), (x, BCY + 2), 1)
    _aaellipse(surf, _CANOPY_H, (x + 2, BCY - 1), 2, 1)
    pygame.draw.circle(surf, _CANOPY_H, (x + 3, BCY - 1), 1)


def build_naval(wing_angle_deg):
    """Draw ONE flat NAVAL INTERCEPTOR frame (nose-right, upright, level) for
    the given wing pose angle. Layer order is rear→front so the spine overlaps
    the nacelle tunnel and the gold rail + self-rim sit on top of everything."""
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)

    # Twin afterburner first (it lives behind the tail).
    ys = _twin_burner(surf, 14 - pit, p, 7, core=_F_CORE, mid=_F_MID,
                      outer=_F_OUTER, halo=_F_HALO)

    tail_x = 14 - pit
    nose_base_x = 46
    nose = 10
    nose_tip_x = nose_base_x + nose
    sweep = 0.45                      # mid-sweep: tails always clear the wings

    # ── Wide-spaced engine nacelles (the F-14 "tunnel" body) drawn first so
    #    the central fuselage spine overlaps their inner edges. ──────────────
    nac_dy = 7
    for sgn in (-1, 1):
        ny = BCY + sgn * nac_dy
        pygame.draw.polygon(surf, _BODY_D, [
            (tail_x, ny - 3), (nose_base_x - 6, ny - 4),
            (nose_base_x - 6, ny + 4), (tail_x, ny + 3)])
        pygame.draw.polygon(surf, _BODY, [
            (tail_x + 2, ny - 2), (nose_base_x - 8, ny - 3),
            (nose_base_x - 8, ny + 2), (tail_x + 2, ny + 2)])

    # ── WIDE twin canted tail fins — the navy identity. Spread to ±13px so
    #    the swing-wing (which tucks to tip_x at mid-sweep, well forward of
    #    the fins) can NEVER occlude them: at every pose the two tails read
    #    as two. The gold rail tops each fin so the twin-tail shape is told
    #    in gold. ───────────────────────────────────────────────────────────
    tail_geo = []
    for sgn in (-1, 1):
        outer_top = (tail_x - 6, BCY + sgn * 13)
        inner_top = (tail_x + 6, BCY + sgn * 4)
        pygame.draw.polygon(surf, _BODY_D, [
            inner_top, outer_top,
            (tail_x - 9, BCY + sgn * 12), (tail_x - 2, BCY + sgn * 3)])
        pygame.draw.polygon(surf, _BODY, [
            (tail_x + 5, BCY + sgn * 5), (tail_x - 4, BCY + sgn * 11),
            (tail_x - 1, BCY + sgn * 4)])
        tail_geo.append((inner_top, outer_top))

    # ── Horizontal stabilators (small all-moving rear tailplanes). ──────────
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _BODY_D, [
            (tail_x + 4, BCY + sgn * 3), (tail_x - 5, BCY + sgn * 9),
            (tail_x + 1, BCY + sgn * 4)])

    # ── Variable-sweep wings. Forward (sweep 0) the tip sits ahead + wide;
    #    back (sweep 1) it tucks aft. Each wing: dark underside, lit top
    #    facet. The LEADING EDGE coords are captured so the gold rail traces
    #    them exactly. ───────────────────────────────────────────────────────
    root_x = nose_base_x - 16
    tip_x = root_x - 2 - sweep * 22
    tip_dy = 22 - sweep * 5
    glove_x = root_x + 8
    wing_lead = []
    for sgn in (-1, 1):
        # Fixed wing-glove fairing root that stays put as the wing swings.
        pygame.draw.polygon(surf, _BODY_D, [
            (root_x, BCY + sgn * 4), (glove_x + 4, BCY + sgn * 8),
            (glove_x + 6, BCY + sgn * 5), (root_x + 2, BCY + sgn * 2)])
        pygame.draw.polygon(surf, _WING_D, [
            (root_x, BCY + sgn * 3), (tip_x - 1, BCY + sgn * tip_dy),
            (tip_x + 5, BCY + sgn * tip_dy), (root_x + 9, BCY + sgn * 5)])
        pygame.draw.polygon(surf, _WING, [
            (root_x + 1, BCY + sgn * 3), (tip_x + 1, BCY + sgn * (tip_dy - 2)),
            (root_x + 8, BCY + sgn * 5)])
        pygame.draw.polygon(surf, _WING_H, [
            (root_x + 2, BCY + sgn * 3), (root_x + 11, BCY + sgn * 6),
            (tip_x + 4, BCY + sgn * (tip_dy - 5)),
            (tip_x + 2, BCY + sgn * (tip_dy - 4))])
        wing_lead.append(((root_x, BCY + sgn * 3), (tip_x, BCY + sgn * tip_dy)))

    # ── Long tandem fuselage: nacelle tunnel + central radar nose spear. ────
    body_pts = [
        (nose_tip_x, BCY),
        (nose_base_x, BCY - 4),
        (root_x + 4, BCY - 6),
        (tail_x + 2, BCY - 5),
        (tail_x, BCY),
        (tail_x + 2, BCY + 5),
        (root_x + 4, BCY + 6),
        (nose_base_x, BCY + 4),
    ]
    pygame.draw.polygon(surf, _BODY, body_pts)
    pygame.draw.polygon(surf, _EDGE, body_pts, 1)
    # Spine highlight catching light down the centreline.
    pygame.draw.polygon(surf, _BODY_H, [
        (nose_base_x - 2, BCY - 3), (root_x + 4, BCY - 4),
        (tail_x + 4, BCY - 3), (tail_x + 4, BCY - 1),
        (root_x + 4, BCY - 1), (nose_base_x - 2, BCY - 1)])
    # Radar nose-cone shade so the long spear reads as a cone, not a needle.
    pygame.draw.polygon(surf, _BODY_D, [
        (nose_tip_x, BCY), (nose_base_x + 2, BCY - 2),
        (nose_base_x + 2, BCY + 2)])

    # ── CONTINUOUS GOLD STRUCTURAL RAIL ─────────────────────────────────────
    # A single unbroken 1px gold rim along the FULL wing leading edge of each
    # wing AND the top of each tail fin, so the planform shape itself is
    # described by the gold even when the body crushes to one value at 40px.
    # The root end gets one brighter pixel as a catch-light seed.
    for (root_pt, tip_pt) in wing_lead:
        pygame.draw.line(surf, _GOLD, root_pt, tip_pt, 1)
        pygame.draw.circle(surf, _GOLD_H, root_pt, 1)
    for (inner_top, outer_top) in tail_geo:
        pygame.draw.line(surf, _GOLD, inner_top, outer_top, 1)

    # ── BAKED COOL SELF-RIM ─────────────────────────────────────────────────
    # A 1px cool light-grey edge along the TOP and NOSE contour of the
    # fuselage, INSIDE the house dark outline. On a warm day sandstone pillar
    # the dark body + dark outline can sink into the pillar's shadow side;
    # this cool rim keeps the airframe's top edge crisp so it never melts in.
    # Only the upper/nose contour is rimmed (a single keyed light direction),
    # leaving the underside dark so the jet still reads as a solid volume.
    rim_pts = [
        (nose_tip_x, BCY),
        (nose_base_x, BCY - 4),
        (root_x + 4, BCY - 6),
        (tail_x + 2, BCY - 5),
    ]
    pygame.draw.lines(surf, _SELFRIM, False, rim_pts, 1)

    # ── The single cool canopy accent. ──────────────────────────────────────
    _tandem_canopy(surf, nose_base_x - 6)
    _nozzles(surf, tail_x, ys)
    return surf


# ─────────────────────────────────────────────────────────────────────────────
# Production registry. ONE build, keyed `skin_naval` to match the production
# registry shape; this whole module lifts into game/animal_jet_fighter.py.
# ─────────────────────────────────────────────────────────────────────────────
get_naval = _make_prebuilt_skin(build_naval)

BUILDERS = {"skin_naval": get_naval}
