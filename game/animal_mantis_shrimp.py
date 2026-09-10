"""Production MANTIS SHRIMP skin (`skin_mantis_shrimp`) — round-2 build.

Round 1 explored five takes; the art-director picked **v3 DUOTONE BRUISER**
and asked for one ship-ready convergence. This module now exposes the SINGLE
primary production build so it lifts straight into game/animal_skins.py:

  * `build_mantis_shrimp(wing_angle_deg) -> pygame.Surface` on a 64×84
    SRCALPHA canvas; body mass centred at (32,44), head/eye-stalks near
    (44,34) and up into the headroom.
  * `get_mantis_shrimp = _make_prebuilt_skin(build_mantis_shrimp)` — a cached
    `(frame_idx, tilt_deg) -> Surface` getter (4 frames, per-3° rotation
    cache, each house-outlined for the day-sky contour).
  * `BUILDERS = {"skin_mantis_shrimp": get_mantis_shrimp}`.

THE FLAP IS A STRIKE: the small raptorial clubs cock BACK on the down-pose
(_WING_ANGLES starts at 50) and PUNCH FORWARD on the up-pose (ends at -40).
`_strike()` maps a wing angle to a 0..1 punch and the body recoils a touch — the
punch is a tidy secondary detail so the FACE stays the focus.

The FACE is a clear cartoon shrimp: a big-eyed googly face + two long trailing
antennae (the unmistakable "this is a shrimp" tell) over a teal duotone shield
that carries two bold orange load-bearing stripes plus one thin banded
mid-stripe as a third accent. The night biome borrows a faint glow on ONLY the
club-tips so the silhouette stays bold on dark skies without lighting the body.

North star: "a skin lives or dies at 40px in motion." The 40px tell is the
friendly googly-eyed face + antennae over the teal/orange striped shield.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (eye-stalks reach up into the headroom) ─────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter — lazy 4-frame build
    + per-(frame, 3°) rotation cache, each frame house-outlined (the 1px dark
    contour the day-sky read needs)."""
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


def _strike(angle_deg):
    """0 = clubs cocked back (down-pose, wing=50), 1 = punched fully forward
    (up-pose, wing=-40). The reverse sense of a flap: lift the bird by
    throwing the punch, so the strike reads on the up-stroke."""
    return 1.0 - (angle_deg + 40) / 90.0


# ═════════════════════════════════════════════════════════════════════════════
# DUOTONE BRUISER palette — teal armoured shield + hot-orange hero.
#   Colour is load-bearing structure: the teal body and TWO bold orange
#   stripes are the read; the thin banded mid-stripe + jewel eyes are the
#   controlled third accent. No rainbow noise.
# ═════════════════════════════════════════════════════════════════════════════
_CARA   = (38, 178, 168)
_CARA_D = (20, 116, 110)
_CARA_H = (138, 236, 224)
_BAND   = (255, 124, 48)            # the two load-bearing orange stripes
_BAND_D = (206, 82, 26)
_BAND_H = (255, 192, 120)
_MID_A  = (255, 214, 70)            # thin banded mid-stripe — third accent
_MID_B  = (90, 210, 240)
_CLUB   = (255, 112, 56)
_CLUB_H = (255, 206, 140)
_CLUB_D = (182, 60, 24)
_CLUB_TIP = (255, 232, 188)         # club striking-face spark (night glow seed)
_STALK  = (36, 18, 58)
_STALK_RIM = (12, 8, 24)
_RIM    = (16, 86, 84)              # in-body dark rim that separates the fists
_EYE_HUE  = (118, 236, 216)
_EYE_HUE2 = (96, 150, 250)          # iridescent shift toward the jewel rim
_GLOW   = (120, 240, 220)


def _glow_dot(surf, cx, cy, r, col):
    """Soft additive halo for the night biome — used ONLY on eye-jewels and
    club-tips so the body stays a flat duotone silhouette."""
    g = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    for rr, a in ((r * 2, 40), (int(r * 1.4), 70), (r, 120)):
        pygame.draw.circle(g, (*col, a), (r * 2, r * 2), rr)
    surf.blit(g, (cx - r * 2, cy - r * 2), special_flags=pygame.BLEND_RGBA_ADD)


def _jewel_eye(surf, cx, cy, r, *, glow):
    """Iridescent compound eye on a thick periscope stalk tip: a teal jewel
    that shifts blue toward the rim, the famous equatorial mid-band of
    ommatidia, a bright specular pixel, and (night only) a soft halo.

    The jewel reads as the head's brightest mass so the twin periscopes carry
    the silhouette on both bright-day and dark-night skies."""
    if glow:
        # Keep the halo tighter than the jewel so the close-set twins stay
        # two distinct periscope lamps, not one goggle band, on night skies.
        _glow_dot(surf, cx, cy, max(2, r - 2), _GLOW)
    # Thin dark seat ring so the jewel pops off any sky (day-contour assist)
    # without bloating into a goggle when the twin eyes sit close.
    pygame.draw.circle(surf, _STALK_RIM, (cx, cy), r + 1, 1)
    # Iridescent body: blue-shifted rim, teal core.
    pygame.draw.circle(surf, _EYE_HUE2, (cx, cy), r)
    pygame.draw.circle(surf, _EYE_HUE, (cx, cy), max(1, r - 1))
    # Equatorial midband of ommatidia (the signature stripe across the eye).
    pygame.draw.line(surf, (250, 252, 250), (cx - r, cy), (cx + r, cy), 1)
    # One hot specular pixel so the eye snaps to attention at 40px.
    pygame.draw.circle(surf, (255, 255, 255), (cx - max(1, r // 3), cy - max(1, r // 3)),
                       max(1, r // 3))


# ═════════════════════════════════════════════════════════════════════════════
# Raptorial club arm — a "boxing-glove" dactyl club on a folded arm.
#   Drawn in ABSOLUTE world coordinates straight onto the body surface so the
#   two fists can be aimed at independent targets: the lead fist drives UP +
#   FORWARD to OVERLAP the snout vector on the punch, the rear fist parks as a
#   separate orange mass with a clear gap to the lead fist. Aiming in world
#   space (not nested local offsets) is what keeps both reads honest at 40px.
# ═════════════════════════════════════════════════════════════════════════════
def _club_arm(surf, shoulder, elbow, fist, *, club_col, club_hi, arm_col,
              club_r, lead, glow, glow_r=None):
    """Draw one raptorial club arm (shoulder→elbow→fist) at world coordinates.

    The striking face points along the shoulder→fist vector so the club reads
    as a hammer thrown in the punch direction, not a static ball. Each fist
    keeps a dark heel rim so the twin fists never visually merge."""
    # Thin segmented limb so the small clubs read as a tidy minor detail and the
    # face keeps focus.
    pygame.draw.line(surf, _RIM, shoulder, elbow, 3)
    pygame.draw.line(surf, arm_col, shoulder, elbow, 1)
    pygame.draw.line(surf, _RIM, elbow, fist, 3)
    pygame.draw.line(surf, arm_col, elbow, fist, 1)

    # The dactyl club — a chunky rounded fist with a dark heel rim so the two
    # fists keep a 1px dark separation even when they sit close in depth.
    pygame.draw.circle(surf, _STALK_RIM, fist, club_r + 1)
    pygame.draw.circle(surf, club_col, fist, club_r)
    pygame.draw.circle(surf, club_hi, (fist[0] - 1, fist[1] - 1), max(1, club_r - 2))

    # Striking-face spark + ridge oriented along the throw so the hammer face
    # leads. dx,dy is the unit-ish punch direction from the shoulder.
    dx, dy = fist[0] - shoulder[0], fist[1] - shoulder[1]
    mag = max(1.0, math.hypot(dx, dy))
    ux, uy = dx / mag, dy / mag
    fx, fy = int(fist[0] + ux * (club_r - 1)), int(fist[1] + uy * (club_r - 1))
    pygame.draw.line(surf, _CLUB_D,
                     (int(fist[0] + ux * club_r - uy * club_r),
                      int(fist[1] + uy * club_r + ux * club_r)),
                     (int(fist[0] + ux * club_r + uy * club_r),
                      int(fist[1] + uy * club_r - ux * club_r)), 1)
    pygame.draw.circle(surf, _CLUB_TIP, (fx, fy), 1)
    if glow and lead:
        # Caller can pull the halo in (cocked/level pose) so the lead club-tip
        # bloom doesn't swallow the rear fist into one hot ball — the two-mass
        # read has to survive the night biome too.
        _glow_dot(surf, fx, fy, glow_r if glow_r is not None else max(2, club_r - 3), _CLUB)


def _segmented_tail(surf, cx, cy, *, count, span):
    """Armoured teal abdomen sweeping back from the body with orange-banded
    plate edges, ending in an orange tail-fan (telson + uropods)."""
    step = span / count
    for i in range(count):
        x = cx - int(i * step)
        rx = 8 - i
        ry = 11 - i
        pygame.draw.ellipse(surf, _CARA_D, (x - rx, cy - ry + 1, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, _CARA, (x - rx, cy - ry, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, _BAND, (x - rx, cy - ry, rx * 2, ry * 2), 1)
    tx = cx - int(span)
    for dy, dx in ((-7, -6), (0, -9), (7, -6)):
        pygame.draw.polygon(surf, _BAND, [
            (tx, cy), (tx + dx, cy + dy), (tx + dx + 3, cy + dy)])
        pygame.draw.polygon(surf, _BAND_D, [
            (tx, cy), (tx + dx, cy + dy), (tx + dx + 3, cy + dy)], 1)


def _lerp_pt(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t))


def _build(wing_angle_deg, *, glow):
    surf = _new()
    s = _strike(wing_angle_deg)

    # Body recoils slightly on the punch (shifts back + down) so the haymaker
    # has weight — the whole bruiser rocks with the strike.
    rcx = -int(s * 2)
    rcy = int(s * 1)
    bcx, bcy = BCX + rcx, BCY + rcy
    hcx, hcy = HCX + rcx, HCY + rcy

    # Shared front-lower shoulder for both arms. World-space targets below are
    # tuned so (a) the rear fist is ALWAYS a separate orange mass parked below
    # the lead fist with a sky gap, and (b) the lead fist drives UP+FORWARD to
    # OVERLAP the snout vector on the punch — the single dominant diagonal that
    # sells "strike" at 40px.
    sh = (bcx + 7, bcy + 3)

    # ── REAR fist: the SECOND of the two fists, and the read that has to survive
    #    the common cocked/level state. Cocked (s=0) it is parked LOW + BACK —
    #    dropped well below the shield's bottom edge and pulled left of the lead
    #    fist — so a clear band of sky sits between it and BOTH the lead club
    #    AND the orange body stripes; two distinct orange masses then read at
    #    40px. Punch (s=1) endpoints are FROZEN (the haymaker is ship-quality).
    far_shoulder = _lerp_pt((bcx + 2, bcy + 11), (bcx + 4, bcy + 6), s)
    far_elbow = _lerp_pt((bcx + 3, bcy + 16), (bcx + 13, bcy + 8), s)
    far_fist  = _lerp_pt((bcx + 4, bcy + 20), (bcx + 21, bcy + 10), s)
    _club_arm(surf, far_shoulder, far_elbow, far_fist,
              club_col=_CLUB_D, club_hi=_CLUB, arm_col=_CARA_D,
              club_r=3, lead=False, glow=glow)

    # Segmented abdomen + orange tail-fan.
    _segmented_tail(surf, bcx - 7, bcy + 1, count=3, span=18)

    # ── Carapace shield — broad torpedo body, dark-rimmed for the day contour.
    _aaellipse(surf, _CARA_D, (bcx + 1, bcy + 1), 17, 14)
    _aaellipse(surf, _CARA, (bcx, bcy), 16, 13)
    _aaellipse(surf, _CARA_H, (bcx - 3, bcy - 4), 8, 4)

    # TWO bold orange load-bearing stripes across the shield (duotone signature).
    for off in (-5, 5):
        pygame.draw.line(surf, _BAND_D, (bcx + off - 1, bcy - 11),
                         (bcx + off - 1, bcy + 11), 4)
        pygame.draw.line(surf, _BAND, (bcx + off, bcy - 11),
                         (bcx + off, bcy + 11), 3)
        pygame.draw.line(surf, _BAND_H, (bcx + off, bcy - 9),
                         (bcx + off, bcy - 3), 1)
    # ONE thin banded mid-stripe between them — the controlled third accent
    # (alternating gold/cyan ticks), the only technicolor on the body.
    midx = bcx
    for k, ty in enumerate(range(bcy - 9, bcy + 10, 3)):
        pygame.draw.line(surf, (_MID_A, _MID_B)[k % 2], (midx, ty), (midx, ty + 1), 1)
    # Re-rim so the bands clamp inside the shield silhouette.
    pygame.draw.ellipse(surf, _CARA_D, (bcx - 16, bcy - 13, 32, 26), 1)

    # ── Head.
    _aaellipse(surf, _CARA_D, (hcx, hcy + 1), 11, 10)
    _aaellipse(surf, _CARA, (hcx - 1, hcy), 10, 9)
    _aaellipse(surf, _CARA_H, (hcx - 2, hcy - 3), 4, 2)

    # ── FACE: a clear cartoon-shrimp read — two long trailing ANTENNAE (the
    #    "this is a shrimp" tell the periscope-only face lacked) + big expressive
    #    googly eyes + a friendly smile.
    for pts in (
        [(hcx + 5, hcy - 2), (hcx, CROWN_Y + rcy),
         (hcx - 9, CROWN_Y - 3 + rcy), (hcx - 16, CROWN_Y - 7 + rcy)],
        [(hcx + 6, hcy), (hcx + 2, CROWN_Y + 5 + rcy),
         (hcx - 7, CROWN_Y + 3 + rcy), (hcx - 14, CROWN_Y + 1 + rcy)],
    ):
        pygame.draw.lines(surf, _STALK_RIM, False, pts, 2)
        pygame.draw.lines(surf, _BAND, False, pts[:-1], 1)   # warm-tipped feeler
    for sgn, tx in ((-1, hcx - 4), (1, hcx + 5)):
        base = (hcx + sgn * 2, hcy - 2)
        tip = (tx, hcy - 7 + rcy)
        pygame.draw.line(surf, _STALK_RIM, base, tip, 4)
        pygame.draw.line(surf, _STALK, base, tip, 2)
        pygame.draw.circle(surf, _STALK_RIM, tip, 7)
        pygame.draw.circle(surf, (255, 255, 255), tip, 6)
        pygame.draw.circle(surf, (32, 26, 44), (tip[0] + 1, tip[1] + 1), 4)
        pygame.draw.circle(surf, (255, 255, 255), (tip[0] - 1, tip[1] - 1), 2)
    pygame.draw.arc(surf, _STALK_RIM, (hcx - 3, hcy + 3, 10, 8), 3.5, 6.0, 2)
    pygame.draw.line(surf, _STALK_RIM, (hcx - 2, hcy + 5), (hcx + 5, hcy + 5), 1)

    # ── HERO: OVERSIZED lead club — the haymaker, drawn IN FRONT of head+shield.
    #    Cocked (s=0): pulled low+forward, clear of the face. Punched (s=1): the
    #    fist drives UP + FORWARD to land OVER the snout — the orange mass clearly
    #    overlaps the snout vector (hcx,hcy → eye-jewels), reading as a punch
    #    thrown past the face, never a leg dangling under the gut.
    near_elbow = _lerp_pt((bcx + 12, bcy + 7), (hcx + 3, hcy + 2), s)
    near_fist  = _lerp_pt((bcx + 16, bcy + 11), (hcx + 10, hcy - 3), s)
    # Tight halo when cocked; widen a touch toward the punch.
    lead_glow_r = int(round(1 + s * 2))
    _club_arm(surf, sh, near_elbow, near_fist,
              club_col=_CLUB, club_hi=_CLUB_H, arm_col=_CARA_D,
              club_r=4, lead=True, glow=glow, glow_r=lead_glow_r)
    return surf


def build_mantis_shrimp(wing_angle_deg):
    """Day/standard build — flat duotone, no body glow (the 1px house outline
    supplies the day-sky contour)."""
    return _build(wing_angle_deg, glow=False)


def build_mantis_shrimp_night(wing_angle_deg):
    """Night-biome build — identical silhouette with a faint glow on ONLY the
    eye-jewels and the lead club-tip. For review parity; the live skin can
    branch on biome phase to swap builds."""
    return _build(wing_angle_deg, glow=True)


get_mantis_shrimp = _make_prebuilt_skin(build_mantis_shrimp)
get_mantis_shrimp_night = _make_prebuilt_skin(build_mantis_shrimp_night)

# Liftable into game/animal_skins.py.
BUILDERS = {"skin_mantis_shrimp": get_mantis_shrimp}
