"""THUNDERBIRD skin — round-2 convergence (legendary spectacle).

ONE production design: STORM-RAPTOR (v1's broad cloud-feather raptor) carrying
v4's cultural signature — an ASYMMETRIC lightning fork that crackles from
beneath a single wing's trailing edge and angles diagonally OUTWARD. That one
hanging fork (never both wingtips, never straight down) is the distinctiveness
vs a dragon or phoenix, and the diagonal keeps it from reading as legs/talons.

There is NO live particle system feeding the skin — each of the 4 frames is a
self-contained sprite, so the glow and lightning are baked ON the sprite. The
"thunderclap" is expressed by scaling the LIGHTNING (biggest/brightest on the
clap frame, faint stub on the up-pose) while the BODY silhouette mass stays
identical across all 4 frames — no silhouette-jump flicker.

Contract mirrors game/animal_skins.py so this lifts straight in:

  * `build_thunderbird(wing_angle_deg) -> pygame.Surface`  one flat frame on a
    64×84 SRCALPHA canvas; body centred at (32,44), head near (44,34).
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_thunderbird": get_thunderbird}` registry at the bottom.

North star: "a skin lives or dies at 40px in motion." The bird leans on one
bold raptor silhouette + two high-contrast tells that survive the downscale on
BOTH bright-day and night skies: the single blazing storm-blue/white-hot eye,
and the yellow under-wing fork (the yellow carries even if blue desaturates).
The legendary constraint forces restraint: the glow never buries the bird.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (crest plumes + lightning headroom) ────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre → (44, 34)
CROWN_Y  = 12 + DY              # top of head → 24


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for build_fn(angle).
    Lazy 4-frame build + per-(frame, 3°) rotation cache, each frame outlined
    with the house silhouette outline."""
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
    """0..1 'wing is up' factor. _WING_ANGLES runs 50→-40 (down→up)."""
    return (angle_deg + 40) / 90.0


def _strike(angle_deg):
    """0..1 'down-stroke' factor — peaks when wings are DOWN (angle 50). The
    thunderclap fires on the down-stroke, so lightning scales with this."""
    return 1.0 - _flap(angle_deg)


def _rot_blit(surf, wing, anchor):
    surf.blit(wing, wing.get_rect(center=anchor).topleft)


# ── shared palette ───────────────────────────────────────────────────────────
PLUME    = (58, 74, 107)        # #3A4A6B plumage
PLUME_D  = (26, 34, 56)         # #1A2238 storm shadow
PLUME_H  = (104, 124, 168)      # lifted plume highlight
PLUME_HH = (150, 170, 214)      # sharpened plume-tip highlight (survives day)
# Top-down value ramp: the raptor's back/top arc must read as the LIGHT side so
# the silhouette separates from a pale-blue day sky instead of going flat-dark.
PLUME_TOP = (92, 112, 156)      # lifted top-of-body value (~+18% on PLUME)
BODY_KEY  = (176, 196, 234)     # cool key-light top-rim edge (1px back arc)
BOLT     = (255, 225, 77)       # #FFE14D lightning
BOLT_HOT = (255, 244, 168)      # hot inner yellow
RIM      = (127, 208, 255)      # electric storm-blue rim
# Belly stripe pulled DOWN a value-step and shifted teal so the white-cored EYE
# stays the unambiguous single brightest blue point at 40px on bright day.
BELLY    = (78, 150, 168)       # teal belly rim (was full RIM cyan)
EYE_BLUE = (96, 196, 255)       # eye halo storm-blue
FLASH    = (255, 255, 255)      # flash core


def _glow_halo(surf, center, r, color, *, layers=5, peak=70):
    """A soft radial aura baked into the sprite. Kept restrained (low peak
    alpha, few layers) so the bird silhouette never drowns in glow at 40px."""
    cx, cy = center
    g = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    gc = (r + 2, r + 2)
    for i in range(layers, 0, -1):
        rr = int(r * i / layers)
        a = int(peak * (1 - (i - 1) / layers))
        pygame.draw.circle(g, (*color, a), gc, rr)
    surf.blit(g, (cx - r - 2, cy - r - 2), special_flags=pygame.BLEND_RGBA_ADD)


def _bolt(surf, pts, *, core=FLASH, glow=BOLT, halo=RIM, w=2):
    """A forked lightning stroke: a wide soft halo, a colored mid, a bright
    core — three passes so the fork reads as 'lit' not just a yellow line.
    The yellow mid is what carries the read if storm-blue desaturates."""
    if len(pts) < 2:
        return
    pygame.draw.lines(surf, (*halo, 90), False, pts, w + 4)
    pygame.draw.lines(surf, glow, False, pts, w + 1)
    pygame.draw.lines(surf, core, False, pts, max(1, w - 1))


# ── broad cloud-feather raptor wing (v1 silhouette) ──────────────────────────
def _tb_wing_cloud(angle_deg, sgn):
    """Broad raptor wing with a billowy cloud-feather trailing edge."""
    w = pygame.Surface((52, 46), pygame.SRCALPHA)
    base = [(24, 24), (46, 12), (50, 22), (44, 28), (50, 34),
            (38, 34), (40, 40), (26, 36), (14, 32)]
    pygame.draw.polygon(w, PLUME_D, base)
    pygame.draw.polygon(w, PLUME, [(24, 24), (44, 14), (46, 24), (28, 32),
                                   (16, 30)])
    # Cloud-puff highlights along the leading edge.
    for px, py in ((40, 16), (44, 21), (34, 20)):
        pygame.draw.circle(w, PLUME_H, (px, py), 3)
    pygame.draw.line(w, PLUME_H, (24, 25), (43, 15), 1)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


# ═════════════════════════════════════════════════════════════════════════════
# STORM-RAPTOR — broad eagle silhouette, soft cloud-feather plumage, two
# back-swept curved head plumes (the cultural tell that separates a thunderbird
# from an eagle), a single ASYMMETRIC lightning fork crackling from beneath the
# near wing and angled diagonally OUTWARD, restrained body aura.
# ═════════════════════════════════════════════════════════════════════════════
def build_thunderbird(wing_angle_deg):
    surf = _new()
    s = _strike(wing_angle_deg)          # 1 = down-stroke (thunderclap)
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 22

    # Restrained body aura — pulses brighter on the down-stroke. The body
    # ellipses below are drawn at a FIXED size every frame; only this aura and
    # the lightning vary, so the silhouette mass never jumps frame-to-frame.
    _glow_halo(surf, (BCX, BCY), 22, RIM, peak=int(36 + 30 * s))

    # Far wing behind.
    _rot_blit(surf, _tb_wing_cloud(20 + spread, +1), (BCX + 16, BCY - 4))

    # Fanned storm-cloud tail.
    pygame.draw.polygon(surf, PLUME_D,
                        [(13, BCY - 4), (2, BCY + 6), (16, BCY + 12)])
    pygame.draw.polygon(surf, PLUME,
                        [(14, BCY - 2), (5, BCY + 5), (16, BCY + 9)])

    # Broad body — fixed mass across all frames. A top-down value ramp keeps the
    # back/top arc light so the raptor separates from a pale day sky: dark base,
    # mid body, a lifted upper cap, then a 1px cool key-light rim on the back.
    _aaellipse(surf, PLUME_D, (BCX + 1, BCY + 1), 18, 16)
    _aaellipse(surf, PLUME, (BCX, BCY), 17, 15)
    _aaellipse(surf, PLUME_TOP, (BCX - 1, BCY - 5), 15, 9)
    _aaellipse(surf, PLUME_H, (BCX - 3, BCY - 4), 8, 5)
    # Cool key-light edge tracing the top-of-back arc — the 1px brighter stroke
    # that pulls the silhouette off a bright-blue sky (light-top, dark-belly).
    pygame.draw.arc(surf, BODY_KEY, (BCX - 17, BCY - 16, 34, 30),
                    math.radians(28), math.radians(172), 2)
    # Electric belly rim — pulled teal + a value-step down so it can't tie with
    # the white-cored eye for 'brightest point' on bright day.
    pygame.draw.arc(surf, BELLY, (BCX - 16, BCY - 12, 32, 30),
                    math.radians(200), math.radians(340), 2)

    # Head + two back-swept curved plumes (thunderbird crown). Sharpened tips:
    # a brighter highlight value + a hard 1px tip stroke so they survive the
    # downscale on bright-day.
    _aaellipse(surf, PLUME_D, (HCX, HCY + 1), 11, 11)
    _aaellipse(surf, PLUME, (HCX - 1, HCY), 10, 10)
    for sgn, hx in ((-1, HCX - 4), (1, HCX + 3)):
        tip = (hx - sgn * 6, CROWN_Y - 8)
        pygame.draw.polygon(surf, PLUME_D,
                            [(hx, CROWN_Y + 6), tip, (hx + sgn * 2, CROWN_Y - 6)])
        pygame.draw.polygon(surf, PLUME_HH,
                            [(hx + 1, CROWN_Y + 5), tip, (hx, CROWN_Y - 4)])
        # Hard plume-tip stroke — the +1px sharper edge that holds at day-sky.
        pygame.draw.line(surf, PLUME_HH, (hx, CROWN_Y + 2), tip, 1)
        # Cool-white tip edge — keeps the crest spiking against a pale day sky
        # where PLUME_HH alone nearly dissolved into the body value.
        pygame.draw.line(surf, BODY_KEY, (hx - sgn * 3, CROWN_Y - 2), tip, 1)
        pygame.draw.circle(surf, BODY_KEY, tip, 1)

    # THE blazing eye — one storm-blue eye with a white-hot core. Built as the
    # single brightest point on the sprite so it stays a tell at 40px on both
    # skies: dark socket → blue halo → white-hot core → tiny pure-white glint.
    pygame.draw.circle(surf, (16, 30, 60), (HCX + 1, HCY - 1), 6)
    pygame.draw.circle(surf, EYE_BLUE, (HCX + 1, HCY - 1), 5)
    pygame.draw.circle(surf, FLASH, (HCX + 1, HCY - 1), 3)
    pygame.draw.circle(surf, FLASH, (HCX, HCY - 2), 1)

    # Hooked beak.
    pygame.draw.polygon(surf, BOLT,
                        [(HCX + 4, HCY - 1), (HCX + 14, HCY + 1),
                         (HCX + 12, HCY + 5), (HCX + 4, HCY + 4)])
    pygame.draw.polygon(surf, (200, 150, 30),
                        [(HCX + 12, HCY + 2), (HCX + 14, HCY + 1),
                         (HCX + 11, HCY + 7)])

    # Near wing (hero).
    near = _tb_wing_cloud(-12 - spread, -1)
    _rot_blit(surf, near, (BCX - 12, BCY + 2))

    # HERO SIGNATURE: ONE asymmetric lightning fork crackling from beneath the
    # near (left) wing's trailing edge, angled diagonally OUTWARD (down-left,
    # away from the body) — never straight down, so it can't read as legs. The
    # fork ORIGIN sits forward at mid-wing (~x18) so on the up-pose nothing
    # trailing the body reads as a tail spike at dive tilt. Lightning SCALE —
    # not body mass — carries the thunderclap: full crackling fork on the clap,
    # a faint stub on the up-pose.
    ox, oy = 18, BCY + 6                  # forward, mid-wing origin
    if s > 0.5:
        # Clap: a single bold zig-zag driving DIAGONALLY down-and-OUT — each
        # segment now drifts more LEFT than it drops (steeper outward lean) so
        # the fork visibly leaves the body into open sky and can't read as a
        # near-vertical leg. It ends in ONE sharp zig-zag point (no lower split)
        # so the terminal is never a two-toe foot. One mid crackle branch peels
        # UP-and-out for spectacle — kept above the tip so it can't form a Y.
        reach = int((s - 0.5) * 2 * 10)
        _bolt(surf, [(ox, oy), (ox - 8, oy + 5), (ox - 4, oy + 9),
                     (ox - 15, oy + 13), (ox - 10, oy + 17),
                     (ox - 24 - reach, oy + 22 + reach)],
              core=FLASH, glow=BOLT, halo=RIM, w=2)
        _bolt(surf, [(ox - 15, oy + 13), (ox - 23 - reach, oy + 11)],
              core=BOLT_HOT, glow=BOLT, halo=RIM, w=1)
    elif s > 0.05:
        # Mid-stroke: shorter single zig-zag, same steeper diagonal-outward
        # read, ending in one sharp point.
        reach = int(s * 8)
        _bolt(surf, [(ox, oy), (ox - 8, oy + 5), (ox - 4, oy + 9),
                     (ox - 14 - reach, oy + 13 + reach)],
              core=FLASH, glow=BOLT, halo=RIM, w=2)
    else:
        # Up-pose: faint stub only, kept short + forward so it never trails as
        # a tail spike under dive tilt.
        _bolt(surf, [(ox, oy), (ox - 4, oy + 5), (ox - 1, oy + 7)],
              core=BOLT, glow=BOLT, halo=RIM, w=1)

    return surf


get_thunderbird = _make_prebuilt_skin(build_thunderbird)


# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_thunderbird": get_thunderbird,
}
