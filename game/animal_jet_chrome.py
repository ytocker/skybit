"""RETRO CHROME — secret JET FIGHTER redesign (round 2, production build).

Concept: a polished BARE-METAL Cold-War jet (F-86 Sabre vibe) read VALUE-FIRST.
The winning take is V3 · BLUE-ANGEL TRIM, converged to a single ship-ready
build. The chrome read is the whole game: a hot top-highlight compressed into
the top ~25% of the fuselage, a HARD transition to the mid body, then a
genuinely DARK belly. At 40px the top edge glints and the belly drops to near
silhouette — that value swing is what reads CHROME instead of flat grey. ONE
cool accent rides the value break (the blue spine) so the jet is never
identified by hue alone; silhouette + value carry it for colour-blind reads.

Drawn NOSE-RIGHT, UPRIGHT, LEVEL on a 64×84 SRCALPHA canvas with the fuselage
mass centred at (32,44). The game applies the inverted nose-up spin later, so
this build does NOT bake rotation.

Contract mirrors game/animal_jet_fighter.py so the winner lifts straight in:

  * `build_chrome(wing_angle_deg) -> Surface`  one flat 64×84 frame.
  * `get_chrome = _make_prebuilt_skin(build_chrome)` — cached
    `(frame_idx, tilt_deg) -> Surface` getter (4 flat poses + per-(frame,3°)
    rotation cache, each run through the house silhouette outline = baked
    self-rim).
  * `BUILDERS = {"skin_chrome": get_chrome}` — the production registry key.

Why the geometry sits where it does: collision is a fixed 14px circle at the
fuselage centre (32,44), so the body mass stays anchored there for fairness
even when the wingspan runs wider.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + body anchor (mirror animal_jet_fighter layout) ──────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY          # fuselage centre → (32, 44)


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a build_fn(angle):
    lazy 4-frame build + per-(frame, 3°) rotation cache, each frame run
    through the house silhouette outline (the baked self-rim)."""
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


def _blit_c(surf, src, center):
    surf.blit(src, src.get_rect(center=center).topleft)


# ── afterburner pulse (identical maths to production) ────────────────────────
def _pulse(angle_deg):
    """0..1 throttle from the wing pose: brightest on the middle two frames,
    dimmest at the ends — a heartbeat the eye reads as thrust at 40px."""
    t = (50 - angle_deg) / 90.0
    return 1.0 - abs(t * 2.0 - 1.0)


def _pitch(angle_deg):
    """±1px nose pitch so the jet 'breathes' with the burner instead of sitting
    dead-still."""
    return int(round((_pulse(angle_deg) - 0.5) * 2.4))


def _baked_flame(length, width, core, mid, outer):
    """Bake ONE afterburner plume (outer haze → mid → white-hot core + shock
    beads) onto its own surface so both build targets stay identical and cheap.
    LEFT edge is the nozzle mouth; the plume streams RIGHT (aft)."""
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
    """Soft radial halo baked once — the warm aura behind the burner. Concentric
    fading rings so glow supports the silhouette, never swallows it."""
    d = radius * 2
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    steps = 8
    for i in range(steps, 0, -1):
        a = int(alpha * (i / steps) ** 2)
        r = int(radius * i / steps)
        pygame.draw.circle(s, (*color, a), (radius, radius), r)
    return s


def _burner(surf, tail_x, nozzles, p, *, hot=(255, 255, 244),
            mid=(255, 168, 60), outer=(236, 72, 36), glow_col=(255, 150, 64)):
    """Common afterburner: per-nozzle tight halo + plume + glowing mouth, peak
    radius capped to the rear. The warm burner must never out-value the bright
    metal nose top-band — so the flame length / halo are held short and the hot
    core stays a narrow seed rather than a fat orange mass."""
    flame_len = int(12 + p * 9)
    halo_r = int((9 + p * 4) * 0.84)
    glow = _glow(halo_r, glow_col, alpha=int(54 + p * 52))
    flame = _baked_flame(flame_len, 8, hot, mid, outer)
    for ny in nozzles:
        _blit_c(surf, glow, (tail_x + flame_len // 2 - 2, ny))
        surf.blit(flame, (tail_x - 2, ny - flame.get_height() // 2))


def _nozzle_mouths(surf, tail_x, nozzles):
    for ny in nozzles:
        pygame.draw.circle(surf, (255, 206, 130), (tail_x, ny), 2)
        pygame.draw.circle(surf, (255, 255, 245), (tail_x - 1, ny), 1)


# ── chrome value palette ─────────────────────────────────────────────────────
# The whole read rides on VALUE: a hot top band, a mid body, a DARK belly.
# Belly pushed ~18% darker than round 1 so the silhouette holds on bright day
# sky without crushing solid black at night (it stays clearly above the
# self-rim outline value, so the underside still reads as metal, not a hole).
_AL_HI   = (240, 244, 252)       # hot top-highlight band (chrome glint)
_AL_BODY = (172, 180, 196)       # mid aluminium
_AL_LO   = (74, 80, 96)          # DARK belly / underside (near-silhouette @40px)
_AL_EDGE = (48, 54, 68)          # panel/outline shadow (value tell)

# Anti-glare matte block ahead of the canopy (stolen from V4): a small dark
# non-specular panel that frames the cool canopy and plants hard value contrast
# at the focal point — a touch warmer/greener than _AL_EDGE so it reads as flat
# paint, not just more shadow.
_MATTE   = (34, 38, 44)

# Cool canopy anchor — the only cool constant vs the warm burner. Saturated so
# the 1-2px centre dot survives the 40px downscale.
_CANOPY  = (46, 134, 196)
_CANOPY_H = (190, 232, 252)
_CANOPY_DOT = (34, 110, 210)     # saturated cool dot that holds at 40px

# ONE accent: the blue spine stripe riding the value break.
_BLUE   = (40, 86, 196)
_BLUE_H = (110, 156, 248)


def build_chrome(wing_angle_deg):
    """V3 · BLUE-ANGEL TRIM, converged. Value-band chrome body + a single blue
    spine accent on the value break + a V4 anti-glare matte block framing the
    cool canopy. Swept wing, big bubble canopy. Nose-RIGHT, upright, level."""
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 9 + pit
    tail_x = 50
    noz = (BCY - 7, BCY + 7)

    _burner(surf, tail_x, noz, p, glow_col=(255, 150, 64))

    # ── Swept tail fins (ONE accent rule: no yellow tip flashes here) ──
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _AL_LO, [
            (tail_x - 5, BCY + sgn * 3), (tail_x + 7, BCY + sgn * 13),
            (tail_x + 9, BCY + sgn * 12), (tail_x + 1, BCY + sgn * 2)])
        # A single lit facet on each fin's top edge keeps the chrome value read
        # without adding a coloured accent.
        pygame.draw.line(surf, _AL_BODY, (tail_x - 4, BCY + sgn * 4),
                         (tail_x + 7, BCY + sgn * 12), 1)

    # ── Swept wings: dark belly band → mid facet → hot top facet ──
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _AL_LO, [
            (nose_x + 22, BCY + sgn * 2), (tail_x - 2, BCY + sgn * 22),
            (tail_x + 3, BCY + sgn * 22), (tail_x - 7, BCY + sgn * 6)])
        pygame.draw.polygon(surf, _AL_BODY, [
            (nose_x + 23, BCY + sgn * 2), (tail_x - 4, BCY + sgn * 20),
            (tail_x - 8, BCY + sgn * 6)])
        # Hot top facet compressed to the leading edge so the wing glints on top
        # and goes dark toward the trailing edge (the chrome value swing).
        pygame.draw.polygon(surf, _AL_HI, [
            (nose_x + 24, BCY + sgn * 2), (nose_x + 33, BCY + sgn * 7),
            (tail_x - 9, BCY + sgn * 8), (tail_x - 8, BCY + sgn * 6)])
        pygame.draw.line(surf, _AL_EDGE, (nose_x + 23, BCY + sgn * 2),
                         (tail_x - 4, BCY + sgn * 20), 1)

    # ── Fuselage: hot top band (~top 25%) → HARD break → mid → DARK belly ──
    body = [(nose_x, BCY), (nose_x + 14, BCY - 6), (tail_x + 3, BCY - 5),
            (tail_x + 6, BCY), (tail_x + 3, BCY + 5), (nose_x + 14, BCY + 6)]
    pygame.draw.polygon(surf, _AL_BODY, body)
    # Dark belly: everything below the centreline drops to _AL_LO so the
    # underside reads near-silhouette at 40px (the CHROME tell, not flat grey).
    pygame.draw.polygon(surf, _AL_LO,
                        [(nose_x + 6, BCY + 1), (tail_x + 3, BCY + 1),
                         (tail_x + 5, BCY + 5), (nose_x + 14, BCY + 6),
                         (nose_x, BCY)])
    # Hot top-highlight band squeezed into the top ~25% of the fuselage, with a
    # HARD lower edge (a drawn dark seam) so the transition to mid body is a
    # crisp value step rather than a smear.
    pygame.draw.polygon(surf, _AL_HI,
                        [(nose_x + 5, BCY - 2), (nose_x + 14, BCY - 5),
                         (tail_x, BCY - 4), (tail_x, BCY - 3)])
    pygame.draw.line(surf, _AL_EDGE, (nose_x + 5, BCY - 2), (tail_x, BCY - 3), 1)
    pygame.draw.polygon(surf, _AL_EDGE, body, 1)

    # ── ONE accent: blue spine stripe riding the value break (nose→tail) ──
    # No yellow pinstripe (it was sub-pixel and flickered); the blue alone
    # carries the team-jet identity, and value carries it for colour-blind reads.
    pygame.draw.line(surf, _BLUE, (nose_x + 6, BCY - 1), (tail_x + 2, BCY), 2)
    pygame.draw.line(surf, _BLUE_H, (nose_x + 8, BCY - 1), (tail_x - 2, BCY - 1), 1)

    # Bare-metal nose cone (the dominant bright read on both skies).
    pygame.draw.polygon(surf, _AL_HI,
                        [(nose_x, BCY), (nose_x + 8, BCY - 3),
                         (nose_x + 8, BCY + 3)])
    pygame.draw.polygon(surf, _AL_LO,
                        [(nose_x, BCY), (nose_x + 8, BCY + 1),
                         (nose_x + 8, BCY + 3)])

    # ── V4 anti-glare matte block immediately ahead of the canopy ──
    pygame.draw.polygon(surf, _MATTE,
                        [(nose_x + 10, BCY - 3), (nose_x + 14, BCY - 4),
                         (nose_x + 14, BCY - 1), (nose_x + 10, BCY - 1)])

    # ── BIG bubble canopy (cool anchor) with a saturated centre dot ──
    _aaellipse(surf, _BLUE, (nose_x + 18, BCY - 1), 6, 4)
    _aaellipse(surf, _CANOPY, (nose_x + 18, BCY - 1), 5, 3)
    _aaellipse(surf, _CANOPY_H, (nose_x + 16, BCY - 3), 2, 1)
    # Saturated cool dot — the lone cool constant that must hold at 40px against
    # the warm burner; drawn last so nothing overpaints it.
    pygame.draw.circle(surf, _CANOPY_DOT, (nose_x + 18, BCY - 1), 1)

    _nozzle_mouths(surf, tail_x, noz)
    return surf


# ─────────────────────────────────────────────────────────────────────────────
# Production registry: the single registered skin lifts into
# game/animal_jet_fighter.py as get_chrome under the key `skin_chrome`.
# ─────────────────────────────────────────────────────────────────────────────
get_chrome = _make_prebuilt_skin(build_chrome)

BUILDERS = {"skin_chrome": get_chrome}
