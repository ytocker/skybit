"""Production UFO Store skin — `skin_ufo` (LANDER POD design).

A secret ultra-premium NON-creature flyer: the player's flapping bird becomes a
stout three-legged Apollo-style descent capsule hovering on splayed landing
struts. The identity is the SILHOUETTE — a rounded trapezoid body (wide flat
top, narrower base) standing on THREE short A-frame legs with footpads. Nothing
else in the set has feet; the legs + the negative space under the body ARE the
read at 40px.

The "flap" is reinterpreted as a single round porthole "eye" that DILATES and
BRIGHTENS across the 4 life-cycle frames (a small dark dot → a hot bloom), as if
the pod is spinning up to lift off. The legs stay STATIC across all four frames
so the silhouette never wobbles, and the tell is a VALUE pop (dark dot vs bright
bloom) so it survives grayscale — not a hue shift. The porthole is parked in the
UPPER THIRD, hard against the flat top, so a dark band of metal always separates
the amber eye from Pip's parcel hanging below body centre.

Contract (mirrors game/animal_skins.py):

  * `build_ufo(wing_angle_deg) -> pygame.Surface`  one flat upright frame on a
    64x84 SRCALPHA canvas; body mass centred at (32,44), legs below.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_ufo": get_ufo}` registry at the bottom.
"""
import pygame

from game.parrot import _WING_ANGLES, _add_outline


# ── canvas + anchors (mirror animal_skins.py) ────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY           # body centre → (32, 44)

# Body trapezoid: wide flat TOP, narrower base. Half-widths + half-height.
# Kept compact so legs read at 40px without the body swallowing the frame.
TOP_HALF = 17                    # half-width of the wide flat top
BOT_HALF = 11                    # half-width of the narrower base
BODY_HALF_H = 13                 # half-height of the body block
TOP_Y = BCY - BODY_HALF_H        # y of the flat top edge
BOT_Y = BCY + BODY_HALF_H        # y of the base edge (legs hang below this)


# ── warm-metal palette ───────────────────────────────────────────────────────
# Body reads as forged warm metal: the gradient runs warm/lit at the top to a
# cooler shaded base (not flat grey), so the hull catches light like the legs'
# edges. Legs + footpads are near-black struts that carry the "it has feet" read
# against a bright day band. Porthole runs from a dark dot to a hot amber bloom.
BODY_TOP   = (214, 212, 210)     # #D6D4D2 warm-lit upper hull
BODY_MID   = (158, 162, 172)     # neutral transition band
BODY_BASE  = (112, 122, 140)     # #707A8C cooler shaded base
BODY_DARK  = ( 78,  85,  98)     # deepest shade under the base lip
HULL_SEAM  = ( 92,  98, 112)     # panel seam lines
HULL_SHEEN = (244, 246, 250)     # specular sheen-band highlight column
LEG_DARK   = ( 43,  48,  56)     # #2B3038 leg struts / footpads
LEG_EDGE   = ( 24,  27,  33)     # darker strut core for chunk
KEYLINE    = (238, 242, 250)     # baked high-value top lip (survives day sky)
RIVET_LIT  = (250, 250, 252)     # bright seam/rivet accent on the chamfers

PORT_RING     = ( 58,  62,  72)  # dark porthole bezel (always present)
PORT_BEZEL_LIT= (176, 182, 196)  # bezel-ring brighten — a secondary tell
PORT_GOLD     = (255, 210,  74)  # #FFD24A porthole glow
PORT_HOT      = (255, 243, 176)  # #FFF3B0 hot centre at full dilation

RCS_METAL  = (170, 176, 188)     # little thruster-quad nub highlights


# Porthole sits in the UPPER THIRD, hard against the flat top, so a dark metal
# band separates it from anything hanging below centre.
PORT_CY = TOP_Y + 6


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter, mirroring the
    production factory: lazy 4-frame build + per-(frame, 3°) rotation cache,
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


def _phase(angle_deg):
    """_WING_ANGLES runs 50→-40 over the 4 poses; map to a 0..3 dilation step
    so the porthole opens up one notch per frame (powering up to lift)."""
    return int(round((50 - angle_deg) / 30.0)) % 4


def _body_polygon():
    """Rounded trapezoid outline points (wide flat top, narrower base). The
    corners are clipped so the shape reads stout + machined, not a sharp wedge."""
    c = 4   # corner clip
    return [
        (BCX - TOP_HALF + c, TOP_Y),
        (BCX + TOP_HALF - c, TOP_Y),
        (BCX + TOP_HALF,     TOP_Y + c),
        (BCX + BOT_HALF,     BOT_Y - c),
        (BCX + BOT_HALF - c, BOT_Y),
        (BCX - BOT_HALF + c, BOT_Y),
        (BCX - BOT_HALF,     BOT_Y - c),
        (BCX - TOP_HALF,     TOP_Y + c),
    ]


def _leg(surf, foot_x, foot_y, hip_x, hip_y):
    """One chunky splayed A-frame leg: two struts from two hip anchors down to a
    shared footpad, plus a round footpad. Struts are ≥3px so they survive 40px;
    legs are baked identically in every frame so the silhouette never wobbles."""
    # outer + inner strut of the A-frame, both anchored under the base lip
    pygame.draw.line(surf, LEG_DARK, (hip_x, hip_y), (foot_x, foot_y), 4)
    pygame.draw.line(surf, LEG_DARK, (BCX, hip_y - 1), (foot_x, foot_y), 3)
    # darker core seam down the main strut for a machined read
    pygame.draw.line(surf, LEG_EDGE, (hip_x, hip_y), (foot_x, foot_y), 1)
    # round footpad — the "foot" that nothing else in the set has
    pygame.draw.circle(surf, LEG_EDGE, (foot_x, foot_y), 4)
    pygame.draw.circle(surf, LEG_DARK, (foot_x, foot_y), 3)
    pygame.draw.circle(surf, RCS_METAL, (foot_x - 1, foot_y - 1), 1)


def _porthole(surf, cx, cy, phase):
    """The single round porthole 'eye'. Across phase 0→3 it DILATES (radius
    grows) and BRIGHTENS (dark dot → hot bloom). A constant dark bezel keeps it
    legible against the bright day sky; a bezel-ring brighten on the high phases
    is a SECONDARY tell that survives even when the core blooms. The bloom is
    held back so the metal hull stays present and f2→f3 reads as 'brighter'."""
    t = phase / 3.0
    bezel_r = 6
    # always-present dark bezel ring (the dark porthole read on day)
    pygame.draw.circle(surf, (30, 33, 40), (cx, cy), bezel_r + 1)
    pygame.draw.circle(surf, PORT_RING, (cx, cy), bezel_r)

    # secondary tell: the bezel ring itself brightens on the upper phases, so the
    # "more powered" read survives even if the warm core bloom is muted by sky.
    if phase >= 2:
        ring_lit = tuple(int(PORT_RING[i] + (PORT_BEZEL_LIT[i] - PORT_RING[i])
                             * (0.55 + 0.45 * t)) for i in range(3))
        pygame.draw.circle(surf, ring_lit, (cx, cy), bezel_r, 1)
        pygame.draw.circle(surf, ring_lit, (cx, cy), bezel_r - 1, 1)

    if phase == 0:
        # closed: a small dark pupil sitting in the bezel (the "off" state)
        pygame.draw.circle(surf, (22, 24, 30), (cx, cy), 2)
        pygame.draw.circle(surf, (70, 74, 86), (cx - 1, cy - 1), 1)
        return

    # f1 is a small-but-clearly-lit amber dot; f2/f3 grow + warm toward white.
    pupil_r = (2, 3, 4)[phase - 1]
    core = tuple(int(PORT_GOLD[i] + (PORT_HOT[i] - PORT_GOLD[i]) * t)
                 for i in range(3))

    # additive bloom halo — held back so it never spans the hull or erases the
    # metal band; tied tight to the bezel so it reads as the eye getting
    # brighter, not a free-floating spark in mid-flight.
    halo_r = int(round(bezel_r * (0.85 + 0.55 * t)))
    g = pygame.Surface((halo_r * 2 + 2, halo_r * 2 + 2), pygame.SRCALPHA)
    gc = halo_r + 1
    for i in range(3, 0, -1):
        a = int((30 + (3 - i) * 26) * t)
        pygame.draw.circle(g, (*core, a), (gc, gc), int(halo_r * i / 3))
    surf.blit(g, (cx - gc, cy - gc), special_flags=pygame.BLEND_RGBA_ADD)

    # solid lit aperture + a hot pip so the centre always has a crisp value peak
    pygame.draw.circle(surf, core, (cx, cy), pupil_r)
    if pupil_r > 2:
        pygame.draw.circle(surf, PORT_HOT, (cx, cy), pupil_r - 2)
    # tiny dark catch-light keeps it reading as glass, not a flat disc
    pygame.draw.circle(surf, (120, 96, 30), (cx + max(1, pupil_r - 1), cy + 1), 1)


def build_ufo(wing_angle_deg):
    """Return the 64x84 upright LANDER POD frame for one of the 4 poses."""
    surf = _new()
    ph = _phase(wing_angle_deg)

    # ── LEGS FIRST so the body overlaps their hips (clean "sitting on" read) ──
    # Three splayed legs: two front (left/right) + one centre that splays further
    # forward + lower, all static. The wider tripod stance hardens the "three
    # feet, not two" read and the negative space under the body.
    foot_y = BOT_Y + 13
    hip_y = BOT_Y - 2
    # left + right A-frames splay outward; the centre leg fans forward + down
    _leg(surf, BCX - 18, foot_y, BCX - BOT_HALF + 2, hip_y)
    _leg(surf, BCX + 18, foot_y, BCX + BOT_HALF - 2, hip_y)
    # centre strut splayed forward to its own lower pad for a clear tripod read
    cfoot_y = foot_y + 5
    pygame.draw.line(surf, LEG_DARK, (BCX - 2, hip_y - 1), (BCX, cfoot_y), 4)
    pygame.draw.line(surf, LEG_DARK, (BCX + 2, hip_y - 1), (BCX, cfoot_y), 3)
    pygame.draw.line(surf, LEG_EDGE, (BCX - 2, hip_y - 1), (BCX, cfoot_y), 1)
    pygame.draw.circle(surf, LEG_EDGE, (BCX, cfoot_y), 5)
    pygame.draw.circle(surf, LEG_DARK, (BCX, cfoot_y), 4)
    pygame.draw.circle(surf, RCS_METAL, (BCX - 1, cfoot_y - 1), 1)

    # ── BODY — rounded trapezoid, warm-to-cool metal gradient (lit top → base) ─
    poly = _body_polygon()
    # soft drop shadow behind the base for a touch of depth
    pygame.draw.polygon(surf, (60, 64, 74),
                        [(x, y + 2) for (x, y) in poly])

    # vertical gradient fill clipped to the trapezoid: warm-lit top → cool base.
    # A restrained specular SHEEN band rides one highlight column offset from
    # centre so the hull reads forged + catches light, not stamped-flat.
    span = BOT_Y - TOP_Y
    sheen_cx = BCX - 6                 # highlight column offset left of centre
    for y in range(TOP_Y, BOT_Y + 1):
        u = (y - TOP_Y) / max(1, span)
        if u < 0.5:
            k = u / 0.5
            col = tuple(int(BODY_TOP[i] + (BODY_MID[i] - BODY_TOP[i]) * k)
                        for i in range(3))
        else:
            k = (u - 0.5) / 0.5
            col = tuple(int(BODY_MID[i] + (BODY_BASE[i] - BODY_MID[i]) * k)
                        for i in range(3))
        half = TOP_HALF + (BOT_HALF - TOP_HALF) * u
        pygame.draw.line(surf, col, (BCX - half, y), (BCX + half, y))
        # specular sheen: a soft brighter column blended over the base gradient
        sheen_half = 3
        for sx in range(int(sheen_cx - sheen_half), int(sheen_cx + sheen_half) + 1):
            if BCX - half <= sx <= BCX + half:
                d = 1.0 - abs(sx - sheen_cx) / (sheen_half + 1)
                w = max(0.0, d) * (1.0 - 0.5 * u)   # fades toward shaded base
                sc = tuple(int(col[i] + (HULL_SHEEN[i] - col[i]) * 0.5 * w)
                           for i in range(3))
                surf.set_at((sx, y), sc)

    # dark base lip so the body visually "sits" on the legs
    pygame.draw.line(surf, BODY_DARK, (BCX - BOT_HALF, BOT_Y),
                     (BCX + BOT_HALF, BOT_Y), 2)

    # two horizontal panel seams across the hull (machined descent-stage read)
    pygame.draw.line(surf, HULL_SEAM, (BCX - 13, BCY + 3),
                     (BCX + 13, BCY + 3), 1)
    pygame.draw.line(surf, HULL_SEAM, (BCX - BOT_HALF + 1, BOT_Y - 3),
                     (BCX + BOT_HALF - 1, BOT_Y - 3), 1)

    # tiny RCS thruster nubs on the upper shoulders (sci-fi descent-stage detail)
    for sx in (BCX - TOP_HALF + 1, BCX + TOP_HALF - 1):
        pygame.draw.circle(surf, BODY_DARK, (sx, TOP_Y + 3), 2)
        pygame.draw.circle(surf, RCS_METAL, (sx, TOP_Y + 2), 1)

    # ── baked high-value KEYLINE on the flat top edge (survives bright day) ──
    pygame.draw.line(surf, KEYLINE, (BCX - TOP_HALF + 4, TOP_Y),
                     (BCX + TOP_HALF - 4, TOP_Y), 2)
    # lit chamfers down the upper corners + bright rivet accents so the forged
    # metal edge reads hard, matching the legs' edge quality.
    pygame.draw.line(surf, KEYLINE, (BCX - TOP_HALF, TOP_Y + 4),
                     (BCX - TOP_HALF + 4, TOP_Y), 1)
    pygame.draw.line(surf, KEYLINE, (BCX + TOP_HALF, TOP_Y + 4),
                     (BCX + TOP_HALF - 4, TOP_Y), 1)
    for rx, ry in ((BCX - TOP_HALF + 3, TOP_Y + 1), (BCX + TOP_HALF - 3, TOP_Y + 1)):
        surf.set_at((rx, ry), RIVET_LIT)

    # ── PORTHOLE TELL — round 'eye' parked in the UPPER THIRD, hard against the
    # flat top, so a dark band of metal always separates it from Pip's parcel.
    _porthole(surf, BCX, PORT_CY, ph)

    return surf


# ── canonical getter + registry ──────────────────────────────────────────────
get_ufo = _make_prebuilt_skin(build_ufo)

BUILDERS = {"skin_ufo": get_ufo}
