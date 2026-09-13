"""SNOWGLOBE parcel cosmetic (PREMIUM — legendary/secret tier).

A glass dome holding a tiny swirling cosmos on a WIDE gold pedestal: a
collectible miniature universe. At 22px the read is an orb-on-a-stand — a
glowing DOME sitting on an unmistakable flat gold BASE, with a hard dark SEAM
between the foot and the glass. Pip's red body occludes the TOP of the dome, so
the BASE is the strongest non-occluded identity cue: a round thing sitting ON a
stand still reads from the visible lower half alone.

Built at 2× (44px) then smoothscaled to 22 so the dark glass outline, the wide
gold base, the seam, and the inner star specks survive the tiny read. The dome
is weighted to the lower/visible half: the DAY orb carries a BAKED inner glow
(an off-centre cool-white specular hotspot + a brighter violet core over a dark
rim) so it has internal light + focal pop even without the night halo. A single
strong glass-highlight crescent on the LOWER-LEFT arc — the visible side, not
the occluded top — sells "glass, not a solid ball". The NIGHT showpiece keeps
the additive violet bloom under the dome on top of the baked day glow.

Carry context: the deep-violet interior and warm gold base are both far from red
on the wheel, so the parcel never merges into Pip; the round-on-a-stand read
survives even with his body over the top of the globe."""
import math
import pygame

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp glass edge at 22px

# DAY palette — pale glass dome over a deep-violet interior; warm gold base.
GLASS = (0xCF, 0xE3, 0xF2)        # pale cool glass tint
GLASS_HI = (0xEA, 0xF2, 0xFF)     # bright rim/crescent catch-light
INTERIOR_RIM = (0x24, 0x18, 0x4C)  # dark sphere rim — widens the day value gap
INTERIOR = (0x3A, 0x2A, 0x6E)     # deep-violet contained cosmos (day read)
INTERIOR_CORE = (0x7A, 0x5C, 0xD6)  # brighter violet lit CORE (day focal pop)
SPEC = (0xF4, 0xF0, 0xFF)         # cool-white specular HOTSPOT (day inner light)
GOLD = (0xE8, 0xB2, 0x3C)         # gold pedestal
GOLD_HI = (0xFB, 0xDF, 0x8E)      # base top sheen
GOLD_D = (0xB0, 0x83, 0x22)       # base underside / rim shadow
STAR = (0xFF, 0xF4, 0xD0)         # warm star specks inside the glass
OUTLINE = (0x16, 0x10, 0x2E)      # dark high-value edge to hold the silhouette
SEAM = (0x0C, 0x08, 0x1C)         # hard dark line where glass meets the foot

# NIGHT baked nebula — violet core blooming to magenta; bright rim highlight.
NEB_CORE = (0x6A, 0x4F, 0xD0)     # violet heart of the contained cosmos
NEB_EDGE = (0xC7, 0x7F, 0xE8)     # magenta falloff toward the glass
RIM = (0xEA, 0xF2, 0xFF)          # cool glass rim highlight


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def _halo(s, cx, cy, R):
    """Soft additive bloom around the dome so the contained cosmos emits light.
    Drawn UNDER the glass — a faint violet aura in daylight that BLOOMS against
    the night sky, the showpiece moment of this legendary parcel."""
    glow = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    for i in range(R, 0, -1):
        t = i / R                       # 1 at the rim, 0 at the core
        col = _lerp(NEB_CORE, NEB_EDGE, t)
        a = int(64 * (1.0 - t) ** 2) + 3
        pygame.draw.circle(glow, col + (a,), (R, R), i)
    s.blit(glow, (cx - R, cy - R), special_flags=pygame.BLEND_RGBA_ADD)


def build(mode="normal", icon_size: int = 0):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2

    # Layout (2× space): dome riding a WIDE short pedestal. Centred a touch high
    # so the visible LOWER half — lit lower cosmos + the wide gold base — carries
    # the read where Pip's body occludes the top of the dome.
    orb_cy = 19
    orb_r = 13            # dome/sphere radius

    # ---- NIGHT HALO first, baked UNDER the dome so the cosmos looks luminous.
    _halo(s, cx, orb_cy, 20)

    # ---- GLASS DOME outline — a full sphere; the dark high-value edge holds the
    # orb silhouette against both skies and keeps the round read after rotation.
    pygame.draw.circle(s, OUTLINE, (cx, orb_cy), orb_r + 2)

    # ---- CONTAINED COSMOS — a soft radial nebula filling the sphere with a wide
    # DAY value gap: a dark sphere RIM falling in to a brighter violet CORE, so
    # the orb reads volumetric (a lit ball) instead of a flat violet disc. The
    # lit core is biased toward the lower/visible half. Clipped to the orb.
    cosmos = pygame.Surface((orb_r * 2, orb_r * 2), pygame.SRCALPHA)
    ccx = orb_r
    # Core sits off-centre toward the lower-visible half so the lit pop survives
    # Pip's top occlusion.
    core_x, core_y = ccx - 1, ccx + 2
    for i in range(orb_r, 0, -1):
        t = i / orb_r                   # 1 at glass wall, 0 at core
        # Night nebula colour for the bloom read…
        neb = _lerp(NEB_CORE, NEB_EDGE, t)
        # …pushed toward a DAY ramp dark-RIM → mid → bright-CORE so the day orb
        # has a real value gradient and a focal lit centre.
        if t > 0.55:
            day = _lerp(INTERIOR, INTERIOR_RIM, (t - 0.55) / 0.45)
        else:
            day = _lerp(INTERIOR_CORE, INTERIOR, t / 0.55)
        col = _lerp(neb, day, 0.55)
        pygame.draw.circle(cosmos, col + (255,), (core_x, core_y), i)
    mask = pygame.Surface((orb_r * 2, orb_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (ccx, ccx), orb_r)
    cosmos.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(cosmos, (cx - orb_r, orb_cy - orb_r))

    # ---- BAKED DAY SPECULAR HOTSPOT — a small off-centre cool-white catch-light
    # in the lower-left visible arc. This is the day's internal-light cue: a
    # tight bright speck reads as light caught inside the glass, giving the orb
    # focal pop against the blue sky without relying on the night additive halo.
    hot_x, hot_y = cx - 4, orb_cy + 3
    pygame.draw.circle(s, (*SPEC, 60), (hot_x, hot_y), 4)
    pygame.draw.circle(s, (*SPEC, 150), (hot_x, hot_y), 2)
    pygame.draw.circle(s, SPEC, (hot_x, hot_y), 1)

    # ---- STAR DOTS — 3 bigger, higher-contrast specks placed in the central +
    # LOWER visible zone (kept well within the rim so rotation can never strand
    # one on the glass edge). A bright core + a faint twinkle ring per star.
    stars = ((cx + 4, orb_cy + 1, 2), (cx - 2, orb_cy + 6, 2),
             (cx + 2, orb_cy - 3, 1))
    for sx, sy, rad in stars:
        pygame.draw.circle(s, (*STAR, 80), (sx, sy), rad + 2)
        pygame.draw.circle(s, STAR, (sx, sy), rad)

    # ---- GLASS-HIGHLIGHT CRESCENT on the LOWER-LEFT dome — the VISIBLE arc, not
    # the occluded top. This single strong curved catch-light is the cheapest
    # "glass, not a solid ball" cue and it lives where Pip never covers it.
    pygame.draw.arc(s, GLASS_HI,
                    pygame.Rect(cx - orb_r, orb_cy - orb_r,
                                orb_r * 2, orb_r * 2),
                    math.radians(190), math.radians(255), 2)
    # A cooler secondary glass tint just inside the rim, all the way round, so
    # the edge reads as transparent glass catching the sky.
    pygame.draw.circle(s, (*GLASS, 55), (cx, orb_cy), orb_r, 1)

    # ---- GOLD PEDESTAL — a WIDE, FLAT foot, clearly wider than the dome so the
    # lower/visible half always reads "round thing sitting ON a stand". A hard
    # dark SEAM separates the foot from the glass even when the top is occluded.
    base_top_y = orb_cy + orb_r - 1
    top_hw = 13           # ≥ orb radius so the foot reads wider than the dome
    bot_hw = 18           # flares out into an unmistakable flat pedestal
    base_h = 8            # flatter + taller-footed than a stubby trapezoid
    foot = [(cx - top_hw, base_top_y), (cx + top_hw, base_top_y),
            (cx + bot_hw, base_top_y + base_h),
            (cx - bot_hw, base_top_y + base_h)]
    out_foot = [(cx - top_hw - 2, base_top_y - 1),
                (cx + top_hw + 2, base_top_y - 1),
                (cx + bot_hw + 2, base_top_y + base_h + 2),
                (cx - bot_hw - 2, base_top_y + base_h + 2)]
    pygame.draw.polygon(s, OUTLINE, out_foot)
    # Vertical gold gradient on the trapezoid for a turned-metal foot feel.
    for ry in range(base_h):
        t = ry / max(1, base_h - 1)
        col = _lerp(GOLD, GOLD_D, t)
        hw = top_hw + (bot_hw - top_hw) * (ry / base_h)
        y = base_top_y + ry
        pygame.draw.line(s, col, (cx - hw, y), (cx + hw, y), 1)
    # HARD SEAM — a dark band where the glass meets the foot, the keyline that
    # makes the dome read as a separate object sitting ON the pedestal.
    pygame.draw.line(s, SEAM, (cx - top_hw, base_top_y - 1),
                     (cx + top_hw, base_top_y - 1), 2)
    # Bright top sheen just under the seam + a dark underside lip for thickness.
    pygame.draw.line(s, GOLD_HI, (cx - top_hw + 1, base_top_y + 1),
                     (cx + top_hw - 1, base_top_y + 1), 1)
    pygame.draw.line(s, GOLD_D, (cx - bot_hw + 1, base_top_y + base_h - 1),
                     (cx + bot_hw - 1, base_top_y + base_h - 1), 1)

    if icon_size:
        return pygame.transform.smoothscale(s, (icon_size, icon_size))
    return pygame.transform.smoothscale(s, (SIZE, SIZE))
