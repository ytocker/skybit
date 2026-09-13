"""COSMIC JELLY production skin (skin_cosmic_jelly) — round-2 final.

A LEGENDARY spectacle skin, and the ANIMALS set's only NON-winged creature:
a galaxy-filled translucent jellyfish bell trailing star-streamer tentacles —
a jellyfish made of deep space. This module exposes the SINGLE primary
production build that won the round-1 review (V4 SOLID VOID-CORE), perfected
against the art-director's round-1 punch list so it lifts straight into
game/animal_skins.py.

Contract (mirrors game/animal_skins.py):

  * `build_cosmic_jelly(wing_angle_deg) -> pygame.Surface`  draws one flat frame.
  * the bell DOME (body mass) is centred at (32,44) = (BCX,BCY); tentacles
    trail DOWN into the lower canvas. Collision is a fixed 14px circle at the
    body centre, so the bell stays anchored there for fairness.
  * there are NO wings: the 4 base wing poses (`_WING_ANGLES = 50,20,-10,-40`,
    down→up) are reinterpreted as the JELLY PULSE — on the down-pose the bell
    CONTRACTS (squashes wide + short) and tentacles bunch; on the up-pose it
    BILLOWS open (tall + narrow) and tentacles stream long. A slow nebula
    drift rotates the internal swirl/stars across the 4 frames.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)`.

Legendary-spectacle constraint: the skin returns ONE static sprite per frame —
there is no live particle system. The nebula glow, stars and core are BAKED
into each of the 4 frames; the pulse + drift are expressed purely by varying
the swirl/core/tentacle positions frame to frame.

Round-2 punch list (art-director directives), all baked here:
  1. A 1px DARKER-VIOLET rim is stamped UNDER the additive halo so the bell has
     a hard edge that survives a bright-day sky — the halo blooms OUTSIDE that
     edge instead of dissolving it.
  2. A star-DIADEM (one dominant white-gold spike-star + two tiny flankers)
     grafted onto the dome top breaks the silhouette like a crest — the
     legendary "one high-value point", grown/dimmed on the contract pose so it
     never competes with the breathing core.
  3. The UPPER dome is ~18% more translucent (a brighter, see-through cap) over
     a near-solid void lower body — it reads as JELLY, not a planet.
  4. The white core BREATHES across the 4 frames: largest+brightest on the
     billow (up-pose), small+dense on the contract (down-pose); the swirl
     drifts ~26°/frame.
  5. FIVE constellation tentacles, joined as 1px star-lines with a brighter
     tip-node: bunched/short on the down-pose, streamed/long on the up-pose.
  6. Two-hue swirl only — cyan + a BLUE-biased magenta (cold, distinct from the
     phoenix's warm red) — over the white core.
"""
import math
import random as _random

import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants ────────────────────────────────────────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # headroom; tentacles trail into the lower half
DY          = 12

# Body (bell dome) centre in composite space — the collision anchor.
BCX, BCY = 32, 32 + DY          # → (32, 44)


# ── shared factory (local copy of animal_skins._make_prebuilt_skin) ──────────
def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle). Lazy 4-frame build + per-(frame, 3°) rotation cache,
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


# ── tiny shared drawing helpers ──────────────────────────────────────────────
def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _rng(seed):
    """Per-frame deterministic RNG so baked star positions twinkle/drift across
    the 4 frames but stay stable within a frame."""
    return _random.Random(seed)


def _pulse(angle_deg):
    """Map a base wing angle to the jelly PULSE phase, 0..1.

    `_WING_ANGLES` runs 50→-40 (down-pose → up-pose). At 0 the bell is
    CONTRACTED (squashed wide+short, tentacles bunched); at 1 it BILLOWS open
    (tall+narrow, tentacles streaming long)."""
    return (angle_deg + 40) / 90.0


def _frame_idx(angle_deg):
    """Which of the 4 baked frames this angle is — drives the slow nebula DRIFT
    and core breathing so the cosmos appears alive though each sprite is static."""
    return _WING_ANGLES.index(angle_deg) if angle_deg in _WING_ANGLES else 0


def _glow_blob(surf, cx, cy, r, color, layers=4, peak=120):
    """A baked soft radial glow — concentric translucent rings, brightest at
    the core, blitted ADD. The legendary halo with no live particle system."""
    for i in range(layers, 0, -1):
        a = int(peak * (i / layers) ** 2)
        rr = int(r * i / layers)
        if rr <= 0:
            continue
        g = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (rr + 1, rr + 1), rr)
        surf.blit(g, (cx - rr - 1, cy - rr - 1),
                  special_flags=pygame.BLEND_RGBA_ADD)


def _star(surf, cx, cy, r, color=(255, 255, 255)):
    """A baked twinkle: bright dot + a faint cross sparkle for the big ones."""
    pygame.draw.circle(surf, color, (cx, cy), r)
    if r >= 2:
        pygame.draw.line(surf, (*color, 150), (cx - r - 1, cy), (cx + r + 1, cy), 1)
        pygame.draw.line(surf, (*color, 150), (cx, cy - r - 1), (cx, cy + r + 1), 1)


def _swirl(surf, cx, cy, rx, ry, phase, colors, arms=2, steps=26):
    """A baked spiral-galaxy swirl inside the bell: `arms` log-spiral arcs of
    fading dots, rotated by `phase` (radians) so successive frames look like
    the nebula slowly turns. Drawn ADD so it glows over the void."""
    for arm in range(arms):
        a0 = phase + arm * (2 * math.pi / arms)
        col = colors[arm % len(colors)]
        for s in range(steps):
            t = s / steps
            ang = a0 + t * 3.0                       # ~1.5 turns per arm
            rad = 1.0 + t * 1.0                      # log-ish outward spiral
            x = cx + math.cos(ang) * rx * rad * 0.5
            y = cy + math.sin(ang) * ry * rad * 0.5
            a = int(210 * (1.0 - t))
            dot = max(1, int(2.4 * (1.0 - t * 0.6)))
            g = pygame.Surface((dot * 2 + 2, dot * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(g, (*col, a), (dot + 1, dot + 1), dot)
            surf.blit(g, (int(x) - dot - 1, int(y) - dot - 1),
                      special_flags=pygame.BLEND_RGBA_ADD)


# ── COSMIC JELLY palette ─────────────────────────────────────────────────────
# Two-hue cold swirl + white core. The magenta is biased BLUE (not red) so the
# whole creature stays cold and never confuses with the warm phoenix.
VOID       = (24, 10, 50)       # near-black violet body — the void core
VOID_DEEP  = (12, 5, 30)        # darkest under-belly shade
RIM_VIOLET = (58, 26, 110)      # the hard 1px silhouette rim baked UNDER the halo
HALO       = (130, 70, 255)     # additive violet bloom that blooms OUTSIDE the rim
CAP_LIGHT  = (150, 110, 255)    # translucent upper-dome cap (the "jelly" glass)
CYAN       = (60, 200, 255)     # swirl hue A
MAGENTA    = (190, 90, 255)     # swirl hue B — blue-biased magenta, cold
WHITE      = (255, 255, 255)
GOLD       = (255, 222, 140)    # the diadem's regal accent


# ═════════════════════════════════════════════════════════════════════════════
# build_cosmic_jelly — the single production build (perfected V4 SOLID VOID-CORE)
# ═════════════════════════════════════════════════════════════════════════════
def build_cosmic_jelly(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)                       # 0 contract → 1 billow
    fi = _frame_idx(wing_angle_deg)
    drift = fi * math.radians(26)                    # ~26°/frame nebula spin

    # Pulse geometry: contracted = wide+short, billowed = tall+narrow.
    rx = int(round(19 - p * 3))
    ry = int(round(14 + p * 4))
    top_y = BCY - ry
    rim_y = BCY + ry - 4

    # 1. HARD SILHOUETTE FIRST. Stamp a darker-violet rim ring that is a touch
    #    larger than the body, THEN bloom the additive halo OUTSIDE it. Painting
    #    the rim before the halo means the bloom adds light around a defined
    #    edge instead of dissolving it — the bell keeps a crisp lip on day sky.
    _aaellipse(surf, (*RIM_VIOLET, 255), (BCX, BCY), rx + 2, ry + 2)
    _glow_blob(surf, BCX, BCY, 28, HALO, layers=6, peak=92)
    # Re-stamp the rim over the inner halo edge so the lip stays hard-edged.
    _aaellipse(surf, (*RIM_VIOLET, 255), (BCX, BCY), rx + 1, ry + 1)

    # 3. JELLY BODY: a solid void LOWER mass with a brighter, see-through UPPER
    #    cap so it reads as gelatinous glass, not an opaque planet.
    _aaellipse(surf, (*VOID, 255), (BCX, BCY), rx, ry)
    # Darken the under-belly for bottom-weighted volume.
    belly = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(belly, (*VOID_DEEP, 200), (BCX, BCY + ry // 2), rx, ry)
    _clip_to_bell(belly, rx, ry)
    surf.blit(belly, (0, 0))
    # Upper-dome translucent cap: a brighter half-ellipse clipped to the top of
    # the bell — ~18% lighter glass over the void so light reads "through" it.
    cap = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(cap, (*CAP_LIGHT, 95), (BCX, BCY - ry // 3), rx - 1, ry)
    _clip_to_bell(cap, rx, ry)
    surf.blit(cap, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # 6. TWO-HUE SWIRL (cyan + blue-magenta) drifting over the breathing core.
    _swirl(surf, BCX, BCY, rx, ry, drift, (CYAN, MAGENTA), arms=2, steps=26)

    # 4. BREATHING WHITE CORE: largest + brightest on the billow, small + dense
    #    on the contract. The swirl arms converge on it, so it reads as the
    #    galactic heart pumping with each pulse.
    core_r = 4 + int(round(p * 3))                   # 4 (contract) → 7 (billow)
    core_peak = 170 + int(round(p * 70))             # 170 → 240
    _glow_blob(surf, BCX, BCY, core_r, WHITE, layers=4, peak=core_peak)
    _star(surf, BCX, BCY, 2 + int(round(p)), WHITE)

    # A few bright stars riding the swirl path, jittered per frame to twinkle.
    rng = _rng(fi * 29 + 7)
    for _ in range(5):
        ang = rng.uniform(0, 2 * math.pi) + drift
        d = rng.uniform(0.45, 0.9)
        sx = int(BCX + math.cos(ang) * rx * d)
        sy = int(BCY + math.sin(ang) * ry * d)
        _star(surf, sx, sy, rng.choice([1, 1, 2]),
              rng.choice([WHITE, CYAN, MAGENTA]))

    # Glassy crown glint on the cap — sells the translucent dome.
    _aaellipse(surf, (*WHITE, 70), (BCX - 4, BCY - ry + 3), 3, 4)

    # 2. STAR-DIADEM: ONE dominant white-gold spike-star + two tiny flankers,
    #    grafted onto the dome top to break the silhouette like a crest. Grown
    #    and brightened on the billow, shrunk on the contract, so it pulses with
    #    the body but never out-shouts the breathing core.
    _diadem(surf, BCX, top_y, p)

    # 5. FIVE constellation tentacles — 1px joined star-lines with a brighter
    #    tip-node. Bunched + short on the contract, streamed + long on billow.
    length = int(round(16 + p * 9))
    # Roots fan WIDER as the bell billows so the 5 strands separate cleanly on
    # the up-pose and bunch tight on the contract — and start just below the rim
    # lip so the hard edge never swallows the strand roots.
    step = 3.4 + p * 1.6
    root_y = rim_y + 1
    for k, base in enumerate((-2.0, -1.0, 0.0, 1.0, 2.0)):
        tx0 = int(round(BCX + base * step))
        _tentacle_constellation(surf, tx0, root_y, length, k, fi, p)
    return surf


def _clip_to_bell(layer, rx, ry):
    """Multiply a working layer by the bell ellipse so interior shading/cap
    light stays inside the dome silhouette (no rectangular spill)."""
    mask = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(mask, (255, 255, 255, 255), (BCX, BCY), rx, ry)
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


def _diadem(surf, cx, top_y, p):
    """The legendary crest: one dominant spike-star centred on the dome apex,
    flanked by two tiny stars. Scaled by the pulse so it breathes with the bell
    yet stays a single high-value point that reads at 40px."""
    big_h = 8 + int(round(p * 3))                    # 8 (contract) → 11 (billow)
    apex_y = top_y - (3 + int(round(p * 2)))         # lifts higher when billowed
    # Soft gold aura so the crest glows off the dark dome.
    _glow_blob(surf, cx, apex_y, 6, GOLD, layers=3, peak=120 + int(p * 40))
    # Vertical white spike (the dominant point) over a gold horizontal cross.
    pygame.draw.polygon(surf, WHITE,
                        [(cx, apex_y - big_h // 2), (cx + 2, apex_y),
                         (cx, apex_y + big_h // 2), (cx - 2, apex_y)])
    pygame.draw.polygon(surf, (*GOLD, 230),
                        [(cx - big_h // 2, apex_y), (cx, apex_y + 2),
                         (cx + big_h // 2, apex_y), (cx, apex_y - 2)])
    pygame.draw.circle(surf, WHITE, (cx, apex_y), 1)
    # Two tiny flankers — kept small so the centre stays dominant.
    for fx, fy in ((cx - 8, top_y + 1), (cx + 8, top_y + 1)):
        _glow_blob(surf, fx, fy, 3, GOLD, layers=2, peak=90)
        _star(surf, fx, fy, 1, WHITE)


# ── tentacle style (joined constellation star-line) ──────────────────────────
def _wave_x(base_x, j, k, fi, p):
    """Horizontal offset of a trailing tentacle point at depth fraction `j`
    (0=rim, 1=tip). Sways with a sine whose phase shifts per frame (drift) and
    whose amplitude grows when the bell BILLOWS (p high) — the trailing-stardust
    read on each pulse."""
    amp = 1.2 + p * 2.6 + (k % 3)
    phase = fi * 0.8 + k * 1.3
    return base_x + int(math.sin(j * 3.2 + phase) * amp * j)


def _tentacle_constellation(surf, x0, y0, length, k, fi, p):
    """Dots JOINED by a faint 1px line so they read as a star-line, not loose
    dust, even small — with a brighter, larger TIP-NODE anchoring each strand."""
    n = max(3, length // 4)
    pts = []
    for s in range(n + 1):
        j = s / n
        pts.append((_wave_x(x0, j, k, fi, p), y0 + int(j * length)))
    # Faint joining line (cyan, fading) so the dots read as one strand.
    if len(pts) >= 2:
        line = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        pygame.draw.lines(line, (*CYAN, 90), False, pts, 1)
        surf.blit(line, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # Star nodes alternating the two swirl hues, dimming toward the tip.
    for s, (x, y) in enumerate(pts):
        j = s / n
        col = (WHITE, CYAN, MAGENTA)[s % 3]
        r = 2 if s % 2 == 0 else 1
        a = int(235 * (1 - j * 0.45))
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*col, a), (r + 1, r + 1), r)
        surf.blit(g, (x - r - 1, y - r - 1), special_flags=pygame.BLEND_RGBA_ADD)
    # Brighter glowing tip-node so each strand has a defined end-point.
    tx, ty = pts[-1]
    _glow_blob(surf, tx, ty, 3, CYAN, layers=2, peak=150)
    _star(surf, tx, ty, 2, WHITE)


# ─────────────────────────────────────────────────────────────────────────────
# Production registry — the single primary build, liftable into animal_skins.py.
# ─────────────────────────────────────────────────────────────────────────────
get_cosmic_jelly = _make_prebuilt_skin(build_cosmic_jelly)

BUILDERS = {"skin_cosmic_jelly": get_cosmic_jelly}
