"""Production KITSUNE skin — round-2 convergence for the ANIMALS store.

KITSUNE (`skin_kitsune`, LEGENDARY) is the crown-jewel showpiece: a celestial
nine-tailed fox (NON-bird). The flying "wings" are the nine-tail FAN — it
sweeps wide on the down-pose and gathers back-and-up on the up-pose across the
4 base wing poses (`parrot._WING_ANGLES = 50,20,-10,-40`). There is no live
particle system for a legendary spectacle, so the foxfire glow + tip flames are
BAKED into each of the 4 frames; the flicker is expressed by varying tail
spread between frames.

This round folds the art-director's winner (v3 CURLED ORACLE) together with
v5's gold→violet gradient fan and v1's brow-placed blaze, then pushes each to
"most-expensive" clarity. Why these specific choices, per the punch list:

  * The fan reads GOLD at the base/inner plumes and cools to a bright VIOLET
    crown at the nine tips. The violet is pushed brighter/larger than a smooth
    ramp would give — at 40px it lands as 2-3 bold value STEPS (banded), which
    is what survives the downscale and signals "premium" over a muddy gradient.
  * The forehead blaze is the signature: a small pure-WHITE moon-disc with a
    tight violet glow ring, one crisp center dot. Head + blaze alone read
    "kitsune" on BOTH day and night.
  * The fan gathers back-AND-up on the up-pose so the collision-centred body
    stays the dominant mass; the large vertical-spread delta between frames 0
    and 3 is the visible "flap".
  * Eyes are OPEN with a catchlight (closed eyes read dead at 40px).
  * A baked gold AURA RING behind the body is only drawn at hero scale (the
    store card) — kept out of the 40px gameplay frames so it never costs
    legibility.

Contract (mirrors game/animal_skins.py so this lifts straight in):

  * `build_kitsune(wing_angle_deg) -> pygame.Surface`  one flat 64×84 frame.
  * `get_kitsune = _make_prebuilt_skin(build_kitsune)` cached getter.
  * `BUILDERS = {"skin_kitsune": get_kitsune}` registry.

Geometry: collision is a fixed 14px circle at the BODY centre, so the fox body
mass stays anchored at BCX,BCY=(32,44). The head sits at HCX,HCY≈(44,34); the
nine-tail fan spreads BEHIND the body and may go wide, but the body stays put.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (tail fan + foxfire need headroom) ─────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre → (44, 34)
CROWN_Y  = 12 + DY              # top of head → 24


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
    """0..1 'tail-fan is GATHERED (up-pose)' factor. _WING_ANGLES runs 50→-40,
    so down-pose (50) → 0 (wide spread) and up-pose (-40) → 1 (gathered)."""
    return (angle_deg + 40) / 90.0


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _eye(surf, cx, cy, r, *, iris=(46, 28, 60), white=(252, 250, 248)):
    """Open eye + one bright catchlight pixel — the cute half of the read.
    Closed/arc eyes vanish to a dead smudge at 40px, so the production fox
    keeps wide oracle eyes."""
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 1))
    pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                       max(1, r // 3))


def _soft_glow(surf, center, radius, color, alpha):
    """A baked radial glow blob: cheap, additive foxfire warmth that survives
    the downscale as a halo. Pre-multiplied falloff in 3 rings."""
    cx, cy = center
    glow = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
    gc = radius + 1
    for frac in (1.0, 0.66, 0.34):
        a = int(alpha * (0.4 + 0.6 * (1 - frac)))
        pygame.draw.circle(glow, (*color, a), (gc, gc), int(radius * frac))
    surf.blit(glow, (cx - gc, cy - gc), special_flags=pygame.BLEND_RGBA_ADD)


# ── palette: GOLD base → VIOLET crown is the legendary signature ─────────────
FUR        = (255, 244, 214)        # #FFF4D6 celestial white-gold fur
FUR_D      = (224, 206, 168)
FUR_H      = (255, 252, 240)
TIP        = (255, 122, 26)         # #FF7A1A ear tip
BLAZE      = (255, 255, 255)        # #FFFFFF moon-disc blaze
NOSE       = (60, 40, 56)

# Fan banding: warm gold roots/inner plumes → cool violet tips. Three bold
# value STEPS (not a smooth ramp) so the gradient survives 40px as banding,
# which reads richer/"more expensive" than a muddy blend.
FAN_GOLD     = (255, 206, 96)       # inner plume body — warm gold
FAN_GOLD_HOT = (255, 234, 168)      # inner spine highlight
FAN_MID      = (214, 150, 196)      # mid plume — gold cooling toward violet
FAN_VIOLET   = (168, 96, 244)       # outer plume body — violet crown
FAN_VIOLET_H = (210, 158, 255)      # crown spine highlight

TIP_GOLD     = (255, 224, 120)      # inner flame tip
TIP_GOLD_HOT = (255, 248, 210)
TIP_VIOLET   = (196, 128, 255)      # crown flame tip — pushed bright
TIP_VIOLET_H = (236, 206, 255)      # near-white violet hotspot (survives 40px)

AURA         = (255, 210, 77)       # #FFD24D hero aura ring
RIM          = (58, 30, 70)         # baked violet-dark rim for day-sky survival


def _band(t):
    """Map RADIAL band position t∈[0,1] (0 = inner/base, 1 = outer tip) to a
    banded gold→violet plume colour set. Three discrete steps, not a smooth
    lerp, so the eye counts warm-vs-cool plumes instead of seeing a wash.
    Returns (body, spine_hi, tip, tip_hot).

    Banding is radial, NOT arc-symmetric: gold owns the base/inner third and
    violet owns the upper outer tips of EVERY plume, so the violet crown rings
    the TOP of the fan on every flank instead of pooling on one side."""
    if t < 0.34:
        return FAN_GOLD, FAN_GOLD_HOT, TIP_GOLD, TIP_GOLD_HOT
    if t < 0.62:
        return FAN_MID, FAN_VIOLET_H, _lerp(TIP_GOLD, TIP_VIOLET, 0.6), TIP_VIOLET_H
    return FAN_VIOLET, FAN_VIOLET_H, TIP_VIOLET, TIP_VIOLET_H


def _plume(surf, base, ang_deg, length, width, curl):
    """One tail plume: a LONG tapering quill from `base` swept to `ang_deg`,
    coloured RADIALLY — gold at the root, cooling to a violet crown at the tip.
    Returns the tip point so the caller can stamp the flame on top. A 1px dark
    separator down each side keeps adjacent plumes from bleeding into one mass
    — that's the 'nine' tell. The plume narrows to a point; the flame puff is
    drawn small + bright by the caller so the SHAPE survives 40px.

    The radial fill is the round-3 fix: every plume — including the low,
    back-swept flank plumes on the dive — carries GOLD at its base and only
    turns VIOLET at the outer/upper tip, so violet always crowns the TOP of the
    fan and never pools as a purple paw/wing on one flank."""
    bx, by = base
    a = math.radians(ang_deg)
    ax, ay = math.cos(a), -math.sin(a)
    px, py = -ay, ax                       # perpendicular
    # Curl hooks the tip sideways for a soft S-flame silhouette, not a spoke.
    tipx = bx + ax * length + px * curl * length
    tipy = by + ay * length + py * curl * length
    b1x, b1y = bx + ax * length * 0.40, by + ay * length * 0.40
    b2x, b2y = bx + ax * length * 0.72 + px * curl * length * 0.5, \
        by + ay * length * 0.72 + py * curl * length * 0.5
    half = width / 2
    pts = [
        (bx + px * half * 0.7, by + py * half * 0.7),
        (b1x + px * half, b1y + py * half),
        (b2x + px * half * 0.55, b2y + py * half * 0.55),
        (tipx, tipy),
        (b2x - px * half * 0.55, b2y - py * half * 0.55),
        (b1x - px * half, b1y - py * half),
        (bx - px * half * 0.7, by - py * half * 0.7),
    ]
    ipts = [(int(x), int(y)) for x, y in pts]
    # Baked dark separator: outline the plume first, fill on top → a 1px rim
    # that survives the bright-day sky AND splits this tail from its neighbour.
    pygame.draw.polygon(surf, RIM, ipts)
    inner = [
        (bx + px * (half - 1) * 0.7, by + py * (half - 1) * 0.7),
        (b1x + px * (half - 1), b1y + py * (half - 1)),
        (b2x + px * (half - 1) * 0.55, b2y + py * (half - 1) * 0.55),
        (tipx - ax, tipy - ay),
        (b2x - px * (half - 1) * 0.55, b2y - py * (half - 1) * 0.55),
        (b1x - px * (half - 1), b1y - py * (half - 1)),
        (bx - px * (half - 1) * 0.7, by - py * (half - 1) * 0.7),
    ]
    ipts_inner = [(int(x), int(y)) for x, y in inner]
    # Base coat the whole quill gold, then over-paint the OUTER segments with the
    # cooling mid/violet bands as radial wedges. Banding (not a smooth ramp) is
    # what survives 40px and signals "expensive."
    pygame.draw.polygon(surf, FAN_GOLD, ipts_inner)
    for lo, hi, col in ((0.36, 0.66, FAN_MID), (0.62, 1.04, FAN_VIOLET)):
        seg = _quill_segment(bx, by, ax, ay, px, py, half - 1, length,
                             curl, lo, hi)
        if len(seg) >= 3:
            pygame.draw.polygon(surf, col, seg)
    # Lighter spine: gold up the root, violet up the crown, so each plume reads
    # as a distinct quill AND the gold-base/violet-tip axis stays legible.
    pygame.draw.line(surf, FAN_GOLD_HOT, (int(bx), int(by)),
                     (int(b2x), int(b2y)), max(1, width // 3))
    pygame.draw.line(surf, FAN_VIOLET_H, (int(b2x), int(b2y)),
                     (int(tipx), int(tipy)), max(1, width // 3))
    return (tipx, tipy)


def _quill_segment(bx, by, ax, ay, px, py, half, length, curl, lo, hi):
    """A radial wedge of the quill between fractional positions lo..hi along its
    length, used to over-paint the cooling colour bands on the outer plume. The
    wedge tapers like the quill itself so the bands narrow toward the tip."""
    def edge(f, sgn):
        # Width tapers linearly from base to tip; curl shifts the spine over.
        w = half * (1.0 - 0.78 * f)
        cx = bx + ax * length * f + px * curl * length * min(1.0, f / 0.72)
        cy = by + ay * length * f + py * curl * length * min(1.0, f / 0.72)
        return (int(cx + px * w * sgn), int(cy + py * w * sgn))
    hi = min(hi, 1.0)
    return [edge(lo, 1), edge(hi, 1), edge(hi, -1), edge(lo, -1)]


# ═════════════════════════════════════════════════════════════════════════════
# PRODUCTION BUILD — CURLED ORACLE refined: gold-base/violet-crown vertical
# nine-tail fan, white moon-disc brow blaze, open oracle eyes.
# ═════════════════════════════════════════════════════════════════════════════
AURA_CORE = (255, 246, 214)         # near-white warm-gold core
AURA_MID  = (255, 214, 110)         # radiant gold body
AURA_R    = 47                      # blooms PAST the fan tips → emitted light


def build_kitsune_aura():
    """The baked radiant warm-GOLD aura for the store card, on its own surface
    so it composites BEHIND the already-outlined fox — otherwise the sprite
    outline pass would trace the soft halo and ring it in dark. Kept out of the
    40px gameplay frames entirely so it never costs legibility at scale.

    Round-3 rebuild: a genuine emitted-light radial — a bright near-white-gold
    CORE ramping smoothly out to fully transparent, blooming slightly past the
    fan tips. Painted per-pixel as a single monotonic falloff (NO stacked
    additive amber blobs, which previously over-summed into a muddy mid-brown
    olive band and cheapened the most-expensive store card)."""
    surf = _new()
    cx, cy = BCX - 1, BCY - 5
    glow = pygame.Surface((AURA_R * 2 + 2, AURA_R * 2 + 2), pygame.SRCALPHA)
    gc = AURA_R + 1
    # Outer→inner so the brighter near rings overwrite the dim outer ones; the
    # colour warms toward white at the core, never passing through brown.
    for r in range(AURA_R, 0, -1):
        f = r / AURA_R                          # 1 = rim, 0 = core
        # Smooth ease-out falloff to transparent so there is no hard band edge.
        a = int(150 * (1.0 - f) ** 1.6)
        if a <= 0:
            continue
        col = _lerp(AURA_CORE, AURA_MID, f)
        pygame.draw.circle(glow, (*col, a), (gc, gc), r)
    surf.blit(glow, (cx - gc, cy - gc))
    return surf


def build_kitsune(wing_angle_deg):
    """One 64×84 gameplay frame (no aura ring — see build_kitsune_aura)."""
    surf = _new()
    g = _flap(wing_angle_deg)               # 1 = gathered (up-pose)
    spread = 1.0 - g                         # 1 = wide fan (down-pose)

    # Soft body-anchored warmth on every frame (cheap, survives downscale).
    _soft_glow(surf, (BCX - 2, BCY - 2), 24, AURA, 70)

    # NINE-TAIL FAN. The fan sweeps UP + BACK behind the curled body (the
    # oracle silhouette), and on the up-pose gathers BACK-AND-UP rather than
    # straight up so the body stays the dominant mass. The large vertical
    # delta between the wide down-pose and the gathered up-pose IS the flap.
    base = (BCX - 4, BCY + 3)
    # Wide low fan on the down-pose; narrow + lifted/back on the up-pose.
    fan = 96 + spread * 78                     # arc widens hard on down-pose
    centre = 118 - g * 26                      # gathers back-left as it lifts
    n = 9
    tips = []
    # Draw outer→inner so the gold inner plumes sit ON TOP, reinforcing the
    # gold-base read; the radial fill (see _plume) keeps violet at every TIP.
    order = sorted(range(n), key=lambda i: -abs(i / (n - 1) - 0.5))
    for i in order:
        t = i / (n - 1)
        ang = centre + (t - 0.5) * fan
        length = 33 + 6 * math.sin(t * math.pi) + spread * 3
        tx, ty = _plume(surf, base, ang, length, 9,
                        curl=0.10 + 0.08 * spread)
        tips.append((tx, ty))
    # Crown by HEIGHT, not arc symmetry: the highest tips get the bright violet
    # flame; the lowest (the back-swept flank roots near the body) stay gold —
    # so the violet rings the TOP of the fan instead of pooling on one flank.
    ty_vals = [p[1] for p in tips]
    top_y, bot_y = min(ty_vals), max(ty_vals)
    span = max(1.0, bot_y - top_y)
    flame_tips = []
    for tx, ty in tips:
        crown = 1.0 - (ty - top_y) / span      # 1 = top of fan, 0 = lowest tip
        _, _, tipc, tiph = _band(0.20 + crown * 0.80)
        flame_tips.append((tx, ty, crown, tipc, tiph))
    # Stamp tight flame tips on top — gold low, bright violet crown. 1-2px glow
    # only, so tips read as distinct sparks, not a soft halo that bleeds the
    # nine tails into one cloud.
    for tx, ty, crown, tipc, tiph in flame_tips:
        if crown > 0.50:
            # Crown tips get a 1px violet glow ring — pushed bright/larger so
            # the violet edge survives 40px as the "most-expensive" crown.
            _soft_glow(surf, (int(tx), int(ty)), 4, FAN_VIOLET, 150)
        pygame.draw.circle(surf, tipc, (int(tx), int(ty)), 3)
        pygame.draw.circle(surf, tiph, (int(tx), int(ty)), 2)

    # ── Dive-pose rim separator ──
    # On the bright-day dive the back-swept violet cluster overlaps the body and
    # loses its lower edge into the body shadow. Lay 1px of the dark RIM along
    # the fan↔body seam (only when gathered/lifting) so the fan stays distinct
    # from the body on light sky.
    if g > 0.45:
        seam = pygame.Rect(0, 0, 26, 22)
        seam.center = (BCX - 6, BCY - 6)
        pygame.draw.arc(surf, RIM, seam,
                        math.radians(40), math.radians(190), 2)

    # ── Curled seated oracle body — a calm rounded mass, tail wrapping front ──
    _aaellipse(surf, RIM, (BCX + 1, BCY + 3), 16, 14)        # baked dark rim
    _aaellipse(surf, FUR_D, (BCX + 1, BCY + 2), 15, 13)
    _aaellipse(surf, FUR, (BCX, BCY), 14, 12)
    _aaellipse(surf, FUR_H, (BCX - 3, BCY - 3), 8, 6)
    # A single curled tail-tuft wrapping over the front paws (the oracle read),
    # gold-cored to tie the body to the fan base.
    pygame.draw.arc(surf, FUR_D, (BCX - 4, BCY + 4, 22, 16),
                    math.radians(200), math.radians(20), 5)
    pygame.draw.circle(surf, FAN_GOLD, (BCX + 16, BCY + 8), 4)
    pygame.draw.circle(surf, FAN_GOLD_HOT, (BCX + 16, BCY + 7), 2)
    for px in (BCX + 4, BCX + 9):               # front paws together
        pygame.draw.circle(surf, FUR, (px, BCY + 12), 3)
        pygame.draw.circle(surf, FUR_D, (px, BCY + 12), 3, 1)

    # ── Calm upright head + pointed ears ──
    _aaellipse(surf, RIM, (HCX, HCY + 1), 11, 10)            # baked dark rim
    _aaellipse(surf, FUR_D, (HCX, HCY + 1), 10, 9)
    _aaellipse(surf, FUR, (HCX - 1, HCY), 9, 8)
    for sgn, ex in ((-1, HCX - 5), (1, HCX + 6)):
        pygame.draw.polygon(surf, FUR_D,
                            [(ex - 3, CROWN_Y + 5), (ex, CROWN_Y - 7),
                             (ex + 4, CROWN_Y + 5)])
        pygame.draw.polygon(surf, TIP,
                            [(ex, CROWN_Y + 2), (ex, CROWN_Y - 6),
                             (ex + 3, CROWN_Y + 2)])
    # Snout wedge.
    pygame.draw.polygon(surf, FUR,
                        [(HCX + 4, HCY), (HCX + 12, HCY + 2),
                         (HCX + 4, HCY + 5)])
    pygame.draw.circle(surf, NOSE, (HCX + 11, HCY + 2), 2)

    # ── SIGNATURE BLAZE: pure-white moon-disc + tight violet glow ring ──
    # One crisp bright dot dead-centre on the brow — pops on day AND night.
    _soft_glow(surf, (HCX - 1, HCY - 5), 5, FAN_VIOLET, 170)
    pygame.draw.circle(surf, (224, 196, 255), (HCX - 1, HCY - 5), 4)   # ring
    pygame.draw.circle(surf, BLAZE, (HCX - 1, HCY - 5), 3)             # moon
    pygame.draw.circle(surf, (255, 255, 255), (HCX - 1, HCY - 6), 1)   # crisp dot

    # ── Open oracle eyes + catchlight ──
    _eye(surf, HCX - 2, HCY, 3)
    return surf


get_kitsune = _make_prebuilt_skin(build_kitsune)


# ─────────────────────────────────────────────────────────────────────────────
# Label → getter registry (production single build; liftable into game/).
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {"skin_kitsune": get_kitsune}
