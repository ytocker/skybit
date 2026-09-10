"""CACTUS PINATA secret flyer skin — round-3 concept builder.

A prickly saguaro piñata in a tiny sombrero. The whole concept lives in the
SILHOUETTE: a tall green trunk with two upturned side-arms raised like a
classic saguaro, capped by a SMALL straw sombrero. It is the only top-heavy
two-armed vertical in the piñata set, so it must read "cactus" at 40px before
any colour resolves.

Round 2 won the grayscale saguaro read (carved arm notches KEPT) but two
problems remained at play-size, both judged on the live DAY/NIGHT gameplay
frame where the GAME composites Pip's fixed brown parcel centred ~12px below
the bird centre (skin-space ≈ (32, 56), a ~21px sprite spanning skin-y 45..67):

  1. PARCEL FUSION — the lower trunk sat directly behind the parcel, so the
     brown gift became the visual centre of mass and the whole thing re-read as
     "hat + arms + a brown torso". Pip's parcel can't move, so round 3 ADAPTS
     THE CACTUS: the green trunk mass is pushed UP into a rounded shoulder that
     shows a clear cool-green band ABOVE the parcel's top edge, and the two
     arms drop their risers DOWN the flanks so green BRACKETS the parcel left
     and right (outside its ~21..43 span). The trunk no longer trails down
     behind the gift — it reads "a cactus the gift sits in front of/below".
  2. WEAK FLUTTER + busy belt — at 40px the per-band sway was a whole-body
     micro-tip and the mid-band studs drifted toward screw-thread noise.

Round-3 fixes:
  * GREEN BRACKETS THE PARCEL — rounded shoulder above the gift, arm risers
    down its flanks (see point 1 above), judged ONLY on the gameplay frames.
  * STRONGER FRINGE WAVE — per-band horizontal amplitude up ~60% with a bigger
    phase shift between adjacent bands, so frame 1 vs frame 3 shows the fringe
    leaning OPPOSITE ways at DIFFERENT heights (a visible wave down the trunk),
    not a rigid whole-body tip. The small hat tilt is kept.
  * CHUNKY CREPE BLOCKS — the tiny gray belt studs are gone; each band carries
    a few fat hi/lo value blocks so it reads as a crepe-paper ring, not a
    threaded screw.
  * NIGHT HOLD — the trunk's low-value green is lifted and a faint cool rim is
    baked on the trunk edge so the silhouette holds against the deep-purple
    night sky instead of merging into it.

Mirrors the contract in game/animal_ufo.py so a winner lifts straight into a
production module: 64×84 SRCALPHA canvas, dominant trunk mass centred at
(32,44), `build(wing_angle_deg) -> Surface`, driven by parrot._WING_ANGLES.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + anchors (mirror animal_ufo.py / animal_skins.py) ────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # dominant trunk mass centre → (32, 44)

# Pip's parcel is composited by the GAME, fixed: a ~21px sprite centred ~12px
# below the bird centre → skin-space centre ≈ (32, 56), top edge ≈ y45, flanks
# at x≈21 (left) and x≈43 (right). Round 3 keeps the green trunk shoulder ABOVE
# PARCEL_TOP and runs the arm risers down OUTSIDE the parcel flanks so the gift
# is bracketed by green, never fused with it.
PARCEL_TOP   = 45
PARCEL_FLANK_L = 21
PARCEL_FLANK_R = 43


# ── palette (per brief) ──────────────────────────────────────────────────────
# Trunk green is pushed COOL + saturated so it never melts into the warm brown
# of Pip's parcel below — the two objects must separate by hue as well as gap.
# The LOW band + EDGE are lifted from round 2 so the silhouette holds at night.
GREEN_HI    = (78, 192, 92)     # #4EC05C lit band
GREEN_LO    = (44, 126, 58)     # #2C7E3A shadow band (lifted ~10% for night hold)
GREEN_EDGE  = (32, 92, 46)      # trunk edge for roundness + notch wall (lifted)
GREEN_RIM   = (120, 214, 150)   # faint cool rim baked on trunk edge (night key)
RIB_SHADE   = (38, 108, 52)     # vertical rib shading
STRAW       = (231, 197, 106)   # #E7C56A sombrero straw
STRAW_LO    = (196, 160, 78)    # sombrero shadow
STRAW_HI    = (247, 224, 156)   # sombrero highlight band
FRINGE      = (251, 243, 221)   # #FBF3DD cream crepe fringe (the night keyline)
FLOWER_PINK = (244, 138, 184)   # pink flower dot
FLOWER_CORE = (255, 246, 250)   # white flower centre
SPINE       = (250, 244, 222)   # pale spine ticks (double as fringe keyline)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle (_WING_ANGLES: 50→-40) to a 0..3 sway step. The flutter
    advances one notch per pose so the four frames read as a continuous wave."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Per-phase base lean of the whole body, in px. Phases 1 and 3 are NOT identical
# rest poses — they carry opposite micro-leans so frame 1 ≠ frame 3 and the loop
# reads left → mid-right → right → mid-left, a continuous orbit.
_LEAN = (-2.6, 0.9, 2.6, -0.9)
_HAT_TILT = (-8.0, 3.0, 8.0, -3.0)   # sombrero brim lean in degrees


def _band_flutter(band_i, ph):
    """Horizontal flutter offset (px) for one crepe band in one phase. Round 3
    pushes the amplitude up ~60% and widens the per-band phase step so the wave
    visibly travels DOWN the trunk: adjacent bands lean opposite ways and the
    crest moves between frames, instead of the whole column tipping as one. The
    quarter-cycle phase clock keeps the two 'centre-ish' poses (1 and 3)
    distinct — at frame 1 vs frame 3 the same band sits on opposite sides."""
    # A travelling sine: the band row carries a bigger spatial phase step (1.45
    # rad/band, was 0.9) so neighbouring bands diverge; the phase clock advances
    # the crest one quarter-turn per frame.
    arg = (band_i * 1.45) + (ph * math.pi / 2.0)
    amp = 2.8                       # was 1.7 → ~+65% so the wave reads at 40px
    return math.sin(arg) * amp


# ── geometry constants — tuned so ARM SPAN is the widest mass, brim is narrow ─
TRUNK_HALF   = 6                 # trunk half-width (slimmer than R1's 9)
ARM_SPAN     = 13                # arm reach — riser foot lands just outside the
                                 # parcel flank so green brackets without floating
NOTCH        = 3                 # transparent air-gap carved trunk↔arm (px)


def _flower(surf, x, y):
    """A small pink-and-white flower dot: 4 pink petals around a white core."""
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        pygame.draw.circle(surf, FLOWER_PINK, (int(x + dx), int(y + dy)), 1)
    pygame.draw.circle(surf, FLOWER_CORE, (int(x), int(y)), 1)


def _arm(surf, side, lean):
    """One upturned saguaro arm drawn as an L, but with the riser dropped DOWN
    the parcel flank so green brackets Pip's gift. The stub starts OUTSIDE the
    trunk wall by NOTCH px (the carved negative space that survives grayscale),
    bends UP into a tall riser for the saguaro read — and the riser's OUTER wall
    sits just outside the parcel flank so a column of green runs down beside the
    brown gift in the live composite.

    `side` is -1 (left) / +1 (right)."""
    drift = lean * 0.35                     # arms drift gently with the sway
    inner_x = BCX + side * (TRUNK_HALF + NOTCH) + drift   # leaves the notch gap
    tip_x = BCX + side * ARM_SPAN + drift
    stub_y = BCY + 6                         # arms attach low on the trunk
    top_y = BCY - 12                         # riser top — below the hat brim
    # The riser foot drops down the parcel flank (skin-y ≈ PARCEL_TOP+7) so the
    # green column visibly brackets the gift left and right in the composite,
    # while stopping short enough that the elbow above still reads as an arm.
    foot_y = PARCEL_TOP + 7

    th = 7                                   # arm thickness — fat enough at 40px
    # horizontal stub (low value base + lit top so the arm has its own roundness)
    pygame.draw.line(surf, GREEN_LO, (inner_x, stub_y), (tip_x, stub_y), th)
    pygame.draw.line(surf, GREEN_HI, (inner_x, stub_y - 1), (tip_x, stub_y - 1), th - 4)
    # vertical riser — runs from the dropped foot up past the stub to the top
    pygame.draw.line(surf, GREEN_LO, (tip_x, foot_y), (tip_x, top_y), th)
    pygame.draw.line(surf, GREEN_HI, (tip_x - side, foot_y), (tip_x - side, top_y), th - 4)
    # rounded elbow + rounded tip cap + rounded foot so the arm is a smooth L
    pygame.draw.circle(surf, GREEN_LO, (int(tip_x), int(stub_y)), th // 2)
    pygame.draw.circle(surf, GREEN_LO, (int(tip_x), int(foot_y)), th // 2)
    pygame.draw.circle(surf, GREEN_HI, (int(tip_x - side), int(top_y)), th // 2)
    pygame.draw.circle(surf, GREEN_EDGE, (int(tip_x), int(top_y)), th // 2, 1)
    # faint cool rim down the riser's OUTER wall — keylines green at night
    pygame.draw.line(surf, GREEN_RIM, (tip_x + side * 2, top_y + 1),
                     (tip_x + side * 2, foot_y - 1), 1)
    # pale spine ticks up the riser — also keyline the green at night
    pygame.draw.circle(surf, SPINE, (int(tip_x - side * 2), int(top_y)), 1)
    pygame.draw.circle(surf, SPINE, (int(tip_x - side * 2), int((top_y + stub_y) // 2)), 1)
    # a flower on the arm shoulder for the night pop
    _flower(surf, tip_x, top_y - 1)
    return tip_x


def _carve_notch(surf, side, lean):
    """Punch a TRANSPARENT vertical slot between the trunk wall and the arm
    riser so the negative space survives grayscale (and the house outline traces
    BOTH edges). Done after trunk + arms are drawn, as an explicit alpha cut —
    the read of 'two raised arms' depends on this gap, so we guarantee it rather
    than hope overlap leaves it. The slot runs the FULL riser so the bracketing
    green column reads as a separate arm beside the gift, not a fused mass."""
    drift = lean * 0.35
    inner = BCX + side * TRUNK_HALF + lean      # trunk outer wall
    outer = BCX + side * (TRUNK_HALF + NOTCH) + drift   # arm riser inner wall
    x0, x1 = sorted((int(inner), int(outer)))
    slot = pygame.Rect(x0, BCY - 11, max(1, x1 - x0), (PARCEL_TOP + 5) - (BCY - 11))
    surf.fill((0, 0, 0, 0), slot)


def _sombrero(surf, cx, cy, tilt):
    """A SMALL tilted straw sombrero. Narrower than round 1 (brim radius 11, was
    17) so the hat is NOT the widest mass — the arm span wins. A flat brim
    ellipse + a low crown, rotated by `tilt` so the hat leans with the sway."""
    pad = 20
    s = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    ox, oy = pad, pad
    brim_rx = 11
    # brim
    _aaellipse(s, STRAW_LO, (ox, oy + 2), brim_rx, 4)
    _aaellipse(s, STRAW, (ox, oy + 1), brim_rx, 4)
    # turned-up brim edge keyline (cream) — reads the hat at night
    pygame.draw.ellipse(s, FRINGE, pygame.Rect(ox - brim_rx, oy - 3, brim_rx * 2, 8), 1)
    # crown
    _aaellipse(s, STRAW_LO, (ox, oy - 3), 6, 5)
    _aaellipse(s, STRAW, (ox, oy - 4), 5, 4)
    _aaellipse(s, STRAW_HI, (ox - 1, oy - 5), 3, 2)
    # decorative band around the crown base
    pygame.draw.line(s, FLOWER_PINK, (ox - 5, oy - 2), (ox + 5, oy - 2), 2)
    rot = pygame.transform.rotozoom(s, tilt, 1.0)
    rr = rot.get_rect(center=(cx, cy))
    surf.blit(rot, rr.topleft)


def _crepe_blocks(surf, rect, hi):
    """Stamp a few CHUNKY hi/lo value blocks across a band so it reads as a
    crepe-paper ring at 40px. Round 3 drops round 2's tiny gray studs (which
    drifted to screw-thread noise) for 2 fat blocks of the opposite value — a
    clear paper-fold rhythm, not a belt of dots."""
    lo_val = GREEN_EDGE if hi else GREEN_HI
    bw = max(2, rect.width // 3)
    by = rect.top + 1
    bh = max(2, rect.height - 2)
    # two blocks: one left-of-centre, one right-of-centre, fat and few.
    for bx in (rect.left + 1, rect.right - bw - 1):
        pygame.draw.rect(surf, lo_val, pygame.Rect(bx, by, bw, bh), border_radius=1)


def build_pinata_cactus(wing_angle_deg):
    """One CACTUS PINATA frame on a 64×84 SRCALPHA canvas. Trunk + two raised
    arms (separated by carved notches) is the read; green brackets Pip's parcel
    (rounded shoulder above it, arm risers down its flanks); the per-band fringe
    flutter + leaning sombrero are the sway tell. Drawn UPRIGHT — no baked body
    rotation."""
    surf = _new()
    ph = _phase(wing_angle_deg)
    lean = _LEAN[ph]
    hat_tilt = _HAT_TILT[ph]

    # The trunk's green mass is concentrated ABOVE the parcel: it runs from just
    # under the hat down to a rounded SHOULDER that terminates just above the
    # parcel's top edge, so a clear cool-green band shows over the gift. The arm
    # risers (drawn in _arm) carry the green down the parcel's flanks. Net read
    # in the composite: green over + green either side of the brown gift.
    top_y = BCY - 17
    base_y = PARCEL_TOP - 1        # rounded shoulder ends just above the parcel
    n_bands = 4
    band_h = max(4, (base_y - top_y) // n_bands)

    # ── arms BEFORE the trunk so the trunk overlaps their inner roots, then we
    #    carve the notch back out for guaranteed negative space ───────────────
    _arm(surf, -1, lean)
    _arm(surf, +1, lean)

    # ── trunk as 4 stacked crepe bands, each with its own flutter offset so the
    #    fringe ripples down the body in a travelling wave ─────────────────────
    span = base_y - top_y
    last_cx = BCX
    for i in range(n_bands):
        t = i / (n_bands - 1)
        cy = top_y + span * t
        # base lean tapers toward the shoulder; flutter alternates per band.
        band_lean = lean * (1.0 - 0.55 * t) + _band_flutter(i, ph)
        cx = BCX + band_lean
        hi = (i % 2 == 0)
        color = GREEN_HI if hi else GREEN_LO
        # bottom band is the rounded SHOULDER — wider + fully rounded so the
        # trunk visibly TERMINATES above the gift instead of trailing into it.
        is_base = (i == n_bands - 1)
        hw = TRUNK_HALF + (2 if is_base else 0)
        bh = band_h + (2 if is_base else 1)
        rect = pygame.Rect(int(cx - hw), int(cy - bh / 2), int(hw * 2), int(bh))
        radius = hw if is_base else max(3, bh // 2)
        pygame.draw.rect(surf, color, rect, border_radius=radius)
        # chunky crepe blocks (replace the old gray studs)
        _crepe_blocks(surf, rect, hi)
        # vertical rib shading + lit edge for trunk roundness
        pygame.draw.line(surf, RIB_SHADE, (rect.centerx - 2, rect.top + 1),
                         (rect.centerx - 2, rect.bottom - 1), 1)
        # faint cool rim on BOTH trunk edges — keylines the green at night
        pygame.draw.line(surf, GREEN_RIM, (rect.right - 1, rect.top + 1),
                         (rect.right - 1, rect.bottom - 1), 1)
        pygame.draw.line(surf, GREEN_RIM, (rect.left, rect.top + 1),
                         (rect.left, rect.bottom - 1), 1)
        last_cx = rect.centerx

        # ── crepe fringe: a strong cream keyline + ticked lower edge at the seam
        #    between bands. This is the part that VISIBLY shifts frame to frame
        #    (the flutter) and the pale value that survives grayscale + keylines
        #    the green at night. Only between bands, not under the shoulder. ────
        if not is_base:
            fy = rect.bottom
            pygame.draw.line(surf, FRINGE, (rect.left + 1, fy), (rect.right - 1, fy), 1)
            for fx in range(rect.left + 1, rect.right, 3):
                pygame.draw.line(surf, FRINGE, (fx, fy), (fx, fy + 2), 1)

    # ── carve the negative-space notches between trunk wall and each arm ──────
    _carve_notch(surf, -1, lean)
    _carve_notch(surf, +1, lean)

    # ── flowers on the upper trunk for the night pop (arm flowers drawn in _arm)
    _flower(surf, last_cx - 3 + lean * 0.4, top_y + band_h)

    # ── small sombrero perched on top, leaning with the sway, with an air gap
    #    above the trunk crown so it reads as a separate hat ───────────────────
    _sombrero(surf, BCX + lean, top_y - 6, hat_tilt)

    return surf


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter (mirrors animal_ufo.py):
    a lazy 4-frame build through the house silhouette outline + a per-(frame, 3°)
    rotation cache, so the flyer animates and banks with the bird's tilt."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_pinata_cactus(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


get_pinata_cactus = _make_prebuilt_skin(build_pinata_cactus)

BUILDERS = {"skin_pinata_cactus": get_pinata_cactus}
