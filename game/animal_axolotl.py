"""AXOLOTL Store skin — round-2 production build (leucistic antler lead).

Round 1 explored five morphs; the art-director picked **v3 ANTLER LEUCISTIC**
and asked to converge to one ship-ready design. This file now exposes a single
primary build, `build_axolotl`, that lifts straight into game/animal_skins.py
via the `BUILDERS` dict at the bottom. The melanoid + gold morphs are kept as
commented alt palettes so a future re-skin can swap them in.

Design language (the 40px tell):
  * A near-white leucistic body with a permanent dot-eyed face — three dots
    (two eyes + a mouth dot) so it stays charming and legible even mid-dive,
    the only "shouldn't-fly amphibian" in the roster.
  * A bold gill CROWN of 5 forks (3 one side / 2 the other) ringing the head.
    The negative SKY-GAP between forks is the tell — not the pink itself — so
    it survives both a bright cyan day sky and a near-black night sky.
  * The flap is a frilled fin-stroke: forks sweep TIGHT (~30° total) on the
    down-pose and BLOOM into a CAPPED ~98° fan on the up-pose, so the crown
    visibly pulses in motion even at 40px without the outer forks splaying
    down into the body outline.

Why a hard 1px dark-coral rim (#A03A5E): the leucistic body is near-white and
would dissolve into a pale-blue day sky without it. The rim is grown from the
alpha mask AFTER the frame is built, so body AND crown share one continuous
silhouette outline. We test on a white field, not the dark review card.

Contract mirrors game/animal_skins.py so the winner lifts straight in:
  * `build_axolotl(wing_angle_deg) -> pygame.Surface` — one flat frame on a
    64×84 SRCALPHA canvas (COMPOSITE_W=64, COMPOSITE_H=84).
  * body mass centred at (32,44); head near (44,34); ~24px top headroom for the
    crown; collision stays a fixed 14px circle at the body centre.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter via `_make_prebuilt_skin`.
  * `BUILDERS = {"skin_axolotl": get_axolotl}` for the lift.
"""
import math
import pygame


# ── tall-canvas constants (mirrors game/animal_skins.py) ─────────────────────
SPRITE_W = 64
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # headroom for the gill crown
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24

_WING_ANGLES = (50, 20, -10, -40)


# ── leucistic lead palette ───────────────────────────────────────────────────
# Body is near-white so it reads as the canonical leucistic morph; the rim
# carries the contrast. Crown holds to ONE pink in exactly two values.
_BODY   = (250, 244, 247)        # near-white leucistic body
_BODY_D = (224, 210, 220)        # soft shade for the back/underlap
_BODY_H = (255, 255, 255)        # belly highlight
_GILL   = (255, 110, 150)        # #FF6E96  crown core (the one pink)
_GILL_H = (255, 178, 200)        # single lighter tip value
_FACE   = (74, 40, 56)           # #4A2838 closed smile + dot eyes
_BLUSH  = (255, 168, 190)        # one soft cheek pixel
_OUTLINE = (160, 58, 94, 255)    # #A03A5E permanent dark-coral rim


# ── permanent silhouette outline ─────────────────────────────────────────────
def _add_outline(src, outline_color=_OUTLINE):
    """Grow a solid 1px dark-coral rim from the alpha mask so the near-white
    body + crown read as one shape against a bright/pale day sky as well as a
    dark night sky. 8-neighbour so diagonal frond tips don't leak."""
    mask = pygame.mask.from_surface(src)
    outline = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    pts = mask.outline()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        for px, py in pts:
            ox, oy = px + dx, py + dy
            if 0 <= ox < src.get_width() and 0 <= oy < src.get_height():
                outline.set_at((ox, oy), outline_color)
    outline.blit(src, (0, 0))
    return outline


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


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    rect = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
    pygame.draw.ellipse(surf, color, rect)


def _flap(angle_deg):
    """bloom 0 = down-pose (crown swept tight), 1 = up-pose (crown bloomed wide).

    Wing 50° is the down-pose (frame 0) and -40° is the up-pose (frame 3), so
    the bloom is inverted relative to the raw angle: tight on the down-stroke,
    full fan on the up-stroke — the frill pulses open as the wing lifts."""
    return 1.0 - (angle_deg + 40) / 90.0


def _legs(surf, color, *, splay=0):
    """Two little forward limbs + two rear; they paddle out on the up-pose."""
    for fx, sgn in ((BCX - 6, -1), (BCX + 8, 1)):
        ex = fx + sgn * (2 + splay)
        pygame.draw.line(surf, color, (fx, BCY + 11), (ex, BCY + 18), 3)
        for t in (-2, 0, 2):
            pygame.draw.line(surf, color, (ex, BCY + 18),
                             (ex + t, BCY + 21), 1)


# ═════════════════════════════════════════════════════════════════════════════
# The CROWN — exactly 5 bold forks ringing the head (3 left, 2 right). Each
# fork is a short stalk that splits into two tines, so the silhouette branches
# like an antler. Forks fan TIGHT on the down-pose and bloom WIDE on the up-
# pose; the constant-angle spacing keeps a clear sky-gap between every fork.
# ═════════════════════════════════════════════════════════════════════════════
def _fork(surf, base, ang, length):
    """One bold gill fork: a thick stalk that TAPERS to a thin tip. The stalk is
    3px at the root and the tine pair narrows to 1px at the tip, so the fan's
    WIDEST point (the tips) carries the thinnest pink — that is what lets a clear
    sky-gap survive between neighbours after the dive rotate→NEAREST downsample,
    where a constant-2px tip would have bled into its neighbour and fused the
    whole crown into a solid paddle. The root stays fat (2–3px) so a fork never
    reads as a frayed tendril; only the LAST pixel of each tine is the lighter
    `_GILL_H` value (the second and only other pink)."""
    bx, by = base
    # split the stalk so it tapers 3px → 2px before the tines branch
    mx0 = bx + math.cos(ang) * (length * 0.55)
    my0 = by + math.sin(ang) * (length * 0.55)
    mx = bx + math.cos(ang) * length
    my = by + math.sin(ang) * length
    pygame.draw.line(surf, _GILL, (bx, by), (mx0, my0), 3)
    pygame.draw.line(surf, _GILL, (mx0, my0), (mx, my), 2)
    # Each tine: a 2px mid then a 1px outer reach, so the tip is a single pink
    # pixel with sky on either side — the inter-fork gap reads even at 40px.
    for da in (-0.30, 0.30):
        tang = ang + da
        midx = mx + math.cos(tang) * (length * 0.30)
        midy = my + math.sin(tang) * (length * 0.30)
        tx = mx + math.cos(tang) * (length * 0.58)
        ty = my + math.sin(tang) * (length * 0.58)
        pygame.draw.line(surf, _GILL, (mx, my), (midx, midy), 2)
        pygame.draw.line(surf, _GILL, (midx, midy), (tx, ty), 1)
        # one lighter pixel at each tine tip — the second (and only other) value
        surf.set_at((int(round(tx)), int(round(ty))), _GILL_H)


def _crown(surf, bloom):
    """Five forks ringing the head. `bloom` 0→1 widens the fan from a tight
    ~30° sweep (down-pose, forks nearly parallel) to a CAPPED ~98° bloom (up-
    pose) so the crown visibly PULSES at 40px in motion. The cap is the fix:
    a 120° fan splayed the two OUTER forks down INTO the body outline, so they
    fused with the head rim and the crown read as 6–7 frayed tendrils. ~98°
    keeps the outer forks above the brow with a clean sky-gap in every pose.

    Two things sell the pulse and the sky-gap:
      * each fork's ANGLE is a fixed fraction of the fan, so the angular gap
        between neighbours stays even and opens up as the fan blooms;
      * each fork's BASE also slides along the brow by the same fraction, so the
        roots separate too — a clear pixel of sky between every fork at 40px.
    Three forks lean left of the head's up-axis, two lean right (3/2 crown).
    Longer stalks (the antler read) so the tips clear the head when bloomed.

    The splay FLOOR was raised (was 15°+bloom*34 → 30°..98°): the DIVE pose sits
    near bloom 0.33, and at the old ~53° spread the five tips packed inside ~13°
    each and the rotate→NEAREST downsample fused them into a solid coral paddle.
    A 46°-floor fan (≈18° per gap even on the dive) keeps five distinct fronds
    after rotation; the pulse still reads because the up-pose still blooms ~2×
    wider than the down-pose."""
    half = math.radians(23 + bloom * 27)          # 46°→100° total spread (capped)
    # Root spread scales with the fan so the five roots separate as it blooms but
    # never slide so far along the brow that the outer coral rim merges with the
    # head rim — every fork still launches from clear scalp on the night dive.
    spread_px = 1.6 + bloom * 2.2
    # Non-linear fractions push the OUTER forks proportionally further apart than
    # the inner pair, so the widest part of the fan opens its sky-gaps first —
    # that is the gap that has to survive the dive downsample. Three lean left,
    # two lean right (3/2 crown).
    fracs = (-1.0, -0.46, 0.0, 0.46, 1.0)
    for i, fr in enumerate(fracs):
        ang = -math.pi / 2 + fr * half             # measured off straight-up
        bx = HCX - 2 + fr * spread_px
        by = HCY - 7 + abs(fr) * 1.5               # outer roots ride a touch up
        length = 14 - abs(fr) * 1.5                 # outer forks slightly shorter
        _fork(surf, (bx, by), ang, length)


# ═════════════════════════════════════════════════════════════════════════════
# Body + face
# ═════════════════════════════════════════════════════════════════════════════
def _face(surf):
    """Closed dot-smile: two dot eyes + a small dot mouth, plus one soft blush
    pixel per cheek.

    The mouth is a 2px DOT, not an upturned arc, and the eyes sit ~1px wider
    apart. A drawn arc plus the lower eye used to land in the same column once
    the dive frame rotated, collapsing the whole face into a dark vertical
    smudge. Three separated dots can't merge under rotation, so the face stays
    legible as dot-eyes + dot-smile in the dive pose."""
    pygame.draw.circle(surf, _FACE, (HCX - 2, HCY - 1), 2)
    pygame.draw.circle(surf, _FACE, (HCX + 9, HCY - 1), 2)
    pygame.draw.circle(surf, _FACE, (HCX + 4, HCY + 6), 1)   # 2px mouth dot
    surf.set_at((HCX - 5, HCY + 3), _BLUSH)
    surf.set_at((HCX + 12, HCY + 3), _BLUSH)


def build_axolotl(wing_angle_deg):
    """The single production AXOLOTL frame — leucistic antler-crown morph."""
    surf = _new()
    bloom = _flap(wing_angle_deg)

    # Crown drawn first so the body overlaps the fork bases (rooted in the head).
    _crown(surf, bloom)

    # Plump near-white body.
    _aaellipse(surf, _BODY_D, (BCX + 1, BCY + 1), 18, 15)
    _aaellipse(surf, _BODY, (BCX, BCY), 17, 14)
    _aaellipse(surf, _BODY_H, (BCX - 1, BCY + 4), 11, 8)

    # Fat tapering tail off the back.
    pygame.draw.polygon(surf, _BODY_D,
                        [(BCX - 14, BCY - 4), (BCX - 26, BCY),
                         (BCX - 14, BCY + 5)])
    pygame.draw.polygon(surf, _BODY,
                        [(BCX - 14, BCY - 2), (BCX - 22, BCY),
                         (BCX - 14, BCY + 3)])

    _legs(surf, _BODY_D, splay=int(bloom * 3))

    # Head fused to the body (axolotls have no neck).
    _aaellipse(surf, _BODY_D, (HCX, HCY + 1), 13, 12)
    _aaellipse(surf, _BODY, (HCX - 1, HCY), 12, 11)
    _aaellipse(surf, _BODY_H, (HCX - 2, HCY + 3), 6, 4)

    _face(surf)
    return surf


get_axolotl = _make_prebuilt_skin(build_axolotl)


# ── liftable registry (drops into game/animal_skins.py) ──────────────────────
BUILDERS = {"skin_axolotl": get_axolotl}


# ── review-sheet hooks ───────────────────────────────────────────────────────
VARIANTS = {"skin_axolotl  ANTLER LEUCISTIC": get_axolotl}
FEATURES = {"skin_axolotl  ANTLER LEUCISTIC":
            "5-fork pink crown (3/2) · closed dot-smile · 1px #A03A5E rim"}


# ═════════════════════════════════════════════════════════════════════════════
# Alt palettes (kept for a future re-skin; not part of the production build).
# Swap these into the _BODY/_GILL/_FACE constants above to retint build_axolotl.
#
#   MELANOID DARK   body (78,64,92) shade (52,42,66) hi (118,100,138)
#                   crown (255,64,150)/(255,150,210) · bright eyes (250,244,250)
#   GOLDEN GILD     body (255,214,120) shade (228,168,70) hi (255,244,196)
#                   crown (255,150,96)/(255,206,150) · face (90,54,30)
# ═════════════════════════════════════════════════════════════════════════════
