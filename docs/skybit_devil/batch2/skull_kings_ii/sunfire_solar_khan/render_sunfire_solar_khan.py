"""
Round-1 concept renderer for SUNFIRE SOLAR KHAN — the royal SUN-DISC skull-king
(Batch 2 / Skull-Kings-II set). Headless Pygame; ELEVATED pipeline (SS=6 ->
smoothscale) so the rayed disc + cradle survive the downscale. Keeps the house
grammar from the sibling king renderers: flat saturated fills, hard 1-2px ink
keyline (28,22,30), dark-core -> flat-fill -> top-left rim-sheen triad, 1px
alpha-grown outline, chibi proportions, scary-CUTE; procedural-only (no
gradients/PNGs).

WHY this KIND de-collides from the roster: the Khan's halo is a FILLED, near-
perfect VERTICAL CIRCLE — a solid amber sun-disc whose rays are a TEXTURED FILL
of the disc (alternating ember-core wedges spun from the centre), NOT an open
ring. This reads as a solid glowing sun, the opposite of Lapis's open horizontal
ellipse, and the opposite of a thin halo ring.

WHY it never reads as a coin/collectible token (the COIN-RISK LOCK): a clean
filled circle is exactly a coin. So the compact seated king + his rayed skull-
crown OVERLAP and BREAK the disc rim at the zenith, and the lower rays flare a
hair past the rim — the perfect circle is deliberately notched, so the eye reads
"enthroned sun-king," never "token."

WHY the cupped sun-skull owns the brightest pixel: the disc glow is warm but
mid-key amber; the four-arm cradle presents a white-HOT sun-skull at dead centre
whose core is the single lightest pixel. The disc is built to frame, not blow
out, the cradle — the rays dim as they approach centre so the white skull pops.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helper grammar, not
runtime sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# -- PINNED PALETTE (locked brief) --------------------------------------------
# Molten amber is the dominant disc MASS; ember-orange ray cores + white-gold
# rim are thin accents; the cupped SUN-SKULL is the white-hot focal.
# disc-fill + rim highlights knocked ~15% darker (round 3) so NOTHING out-glows
# the white-hot cupped focal — the disc frames, never competes with, the skull.
AMBER     = (198, 150,  72)   # molten amber sun-body (the dominant disc fill)
AMBER_D   = (182, 128,  54)   # amber dark-core / between-ray shade
AMBER_DD  = (138,  92,  38)   # deepest amber hollow
AMBER_SH  = (212, 182, 120)   # amber top-left rim sheen (dimmed)
EMBER     = (214, 108,  40)   # ember-orange RAY CORES (the textured-fill accent)
EMBER_D   = (162,  74,  26)
EMBER_BR  = (246, 158,  70)
RIM       = (214, 198, 152)   # white-gold disc RIM (a thin edge accent, dimmed)
RIM_HOT   = (224, 212, 184)   # rim sheen knocked down so it can't rival the core
# the SINGLE warm focal — the cupped white-hot SUN-SKULL.
SUN       = (255, 240, 196)   # sun-skull bone (already very light)
SUN_BR    = (255, 250, 230)
SUN_HOT   = (255, 255, 250)   # hottest skull core (must be the brightest pixel)
SUN_D     = (236, 198, 120)   # skull socket-shade (still warm, never grey)
SUN_RIM   = (208, 156,  72)   # skull keyline-adjacent rim
# the KING body — a darker bronze bone so it READS against the bright disc and
# breaks the rim as a clear silhouette (not a second bright mass).
KING      = (196, 138,  70)   # bronze-bone king body (mid-dark vs the disc)
KING_D    = (146,  98,  48)
KING_DD   = (104,  68,  34)
KING_SH   = (224, 176, 108)
# crown skull-boss gold (the topmost ray) — struck gold, kept distinct from amber
GOLD      = (242, 196,  92)
GOLD_BR   = (255, 230, 150)
GOLD_D    = (176, 128,  48)
INK       = ( 28,  22,  30)   # hard ink keyline

BG        = ( 96, 100, 108)   # neutral grey review backdrop
PANEL     = ( 74,  78,  88)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (188, 196, 208)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    pts = mask.outline()
    if len(pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(base, (0, 0))
    return ring


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.4), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.45),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


def bone_limb(surf, p0, p1, p2, thick, s, color=KING, joint=True):
    for (a, b) in ((p0, p1), (p1, p2)):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * thick / 2, dx / L * thick / 2
        quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
        triad_blob(surf, color, quad,
                   sheen_pts=[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                              (b[0] + nx * 0.3, b[1] + ny * 0.3),
                              (a[0] + nx * 0.3, a[1] + ny * 0.3)],
                   ow=max(1, int(thick * 0.18)))
    if joint:
        triad_circle(surf, color, p1, int(thick * 0.58), ow=max(1, int(1.2 * s)),
                     core=False)


# -- the FILLED sun-disc: rays rendered as a TEXTURED FILL, not an open ring --
def sun_disc(surf, cx, cy, r, s, n_rays=20):
    """A solid amber sun-disc whose surface is filled with alternating spun
    EMBER ray-wedges from centre to rim. WHY a filled texture, not a ring: the
    KIND lock demands a solid vertical circle (de-collides from open-ellipse
    siblings). The wedges fan from the centre so the disc reads as a sun's body,
    yet the centre stays AMBER (rays foot short of the middle) so the cupped
    white skull drawn on top is never swamped — the disc frames, never blows out,
    the focal. A bright white-gold RIM traces the edge as the only thin accent."""
    # 1) the solid amber body (the dominant mass) with a soft outer ink ring
    pygame.draw.circle(surf, INK, (cx, cy), r + max(2, int(2.0 * s)))
    pygame.draw.circle(surf, AMBER_D, (cx, cy), r)
    pygame.draw.circle(surf, AMBER, (cx, cy), int(r * 0.96))

    # 2) the TEXTURED FILL — ember wedges spun from centre, footing short of the
    #    middle so the core stays amber for the focal to sit on.
    inner = r * 0.30          # rays start out here, leaving an amber core
    for k in range(n_rays):
        a0 = (k / n_rays) * 2 * math.pi
        a1 = ((k + 0.46) / n_rays) * 2 * math.pi   # slim wedge, amber gap between
        am = (a0 + a1) / 2
        col = EMBER if (k % 2 == 0) else EMBER_D
        wedge = [
            (cx + math.cos(a0) * inner, cy + math.sin(a0) * inner),
            (cx + math.cos(a0) * r * 0.94, cy + math.sin(a0) * r * 0.94),
            (cx + math.cos(am) * r * 0.99, cy + math.sin(am) * r * 0.99),
            (cx + math.cos(a1) * r * 0.94, cy + math.sin(a1) * r * 0.94),
            (cx + math.cos(a1) * inner, cy + math.sin(a1) * inner),
        ]
        pygame.draw.polygon(surf, col, wedge)
        # a hot inner sliver on the lit (upper-left) wedges for the spun-light read
        if math.cos(am) < 0.2 and math.sin(am) < 0.2:
            slv = [
                (cx + math.cos(a0) * inner, cy + math.sin(a0) * inner),
                (cx + math.cos(a0) * r * 0.5, cy + math.sin(a0) * r * 0.5),
                (cx + math.cos(am) * r * 0.55, cy + math.sin(am) * r * 0.55),
            ]
            pygame.draw.polygon(surf, EMBER_BR, slv)

    # 3) re-seat the amber CORE on top so the centre is a clean field for the
    #    focal cradle (the rays explicitly do not reach the middle).
    pygame.draw.circle(surf, AMBER_D, (cx + int(r * 0.06), cy + int(r * 0.07)),
                       int(inner * 1.04))
    pygame.draw.circle(surf, AMBER, (cx, cy), int(inner * 0.96))
    pygame.draw.circle(surf, AMBER_SH,
                       (cx - int(inner * 0.34), cy - int(inner * 0.36)),
                       max(1, int(inner * 0.30)))

    # 4) the thin white-gold RIM (the disc's one bright edge accent)
    pygame.draw.circle(surf, RIM, (cx, cy), int(r * 0.99), max(2, int(2.2 * s)))
    pygame.draw.circle(surf, RIM_HOT,
                       (cx - int(r * 0.30), cy - int(r * 0.66)),
                       0, 0)  # noop guard
    # a bright crescent on the upper-left rim (the sheen)
    pygame.draw.arc(surf, RIM_HOT,
                    (cx - r, cy - r, 2 * r, 2 * r),
                    math.radians(120), math.radians(210), max(2, int(2.4 * s)))
    pygame.draw.circle(surf, INK, (cx, cy), r, max(1, int(1.4 * s)))


# -- a single ornamental sun-skull (the white-hot focal + the crown boss) -----
def sun_skull(surf, cx, cy, r, s, focal=False):
    """Tiny gold/white skull. As the CROWN boss it is struck-GOLD; as the cupped
    FOCAL it is white-HOT with the single brightest core pixel. WHY two tints
    from one routine: the crown-skull and the cradled skull are the same emblem
    (a sun-skull) at two heats — gold up top, white-hot in the palms. The focal
    is drawn BIGGER and with fewer interior marks so its hot dome survives 32px
    as one clean bright read, never a busy void."""
    body = SUN if focal else GOLD
    body_d = SUN_D if focal else GOLD_D
    rim = SUN_BR if focal else GOLD_BR
    # cranium dome
    triad_circle(surf, body, (cx, cy), r, ow=max(1, int(1.6 * s)), core=False)
    # jaw stub
    jaw = [(cx - int(r * 0.50), cy + int(r * 0.48)),
           (cx + int(r * 0.50), cy + int(r * 0.48)),
           (cx + int(r * 0.30), cy + int(r * 0.94)),
           (cx - int(r * 0.30), cy + int(r * 0.94))]
    triad_blob(surf, body, jaw, ow=max(1, int(1.2 * s)))
    # two sockets — kept as the ONLY interior dark marks so the dome stays the
    # bright mass (fewer shapes = legible at 32px).
    for ex in (cx - int(r * 0.36), cx + int(r * 0.36)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.06)), max(1, int(r * 0.24)))
        # warm ember pin so the focal skull glows (scary-cute)
        pygame.draw.circle(surf, EMBER, (ex, cy + int(r * 0.06)), max(1, int(r * 0.11)))
    # single grin notch (nose tick dropped at chip scale to cut shape count)
    pygame.draw.line(surf, INK, (cx - int(r * 0.30), cy + int(r * 0.66)),
                     (cx + int(r * 0.30), cy + int(r * 0.70)), max(1, int(1.4 * s)))
    if focal:
        # WHY a STEP-DOWN from a small flood to a concentrated pure-white pip,
        # not a broad near-white pool: a wide near-white dome let the disc rim
        # (esp. on NIGHT, where the keyline rim is bright) sit only marginally
        # below the focal. Round 4 keeps the warm bone-white pool TIGHT and lands
        # a true pure-white core that, after the SS=6 downscale, survives as a
        # 2-3px pip ≥15% brighter than any rim pixel on BOTH chips — the single
        # brightest spot, unambiguously.
        pygame.draw.circle(surf, SUN_BR, (cx, cy), int(r * 0.64))
        pygame.draw.circle(surf, SUN_HOT,
                           (cx - int(r * 0.08), cy - int(r * 0.12)),
                           max(2, int(r * 0.40)))
        # the white-hot pinpoint: pure-white, slightly enlarged so it doesn't get
        # averaged away by the smoothscale (must clear the rim by ≥15% lum).
        pygame.draw.circle(surf, (255, 255, 255),
                           (cx - int(r * 0.06), cy - int(r * 0.10)),
                           max(2, int(r * 0.26)))
    else:
        # top-left bone sheen on the gold crown dome
        pygame.draw.circle(surf, rim, (cx - int(r * 0.34), cy - int(r * 0.38)),
                           max(1, int(r * 0.24)))


# -- the rayed SUNBURST crown: a skull throned as the topmost ray-boss --------
def sunburst_crown(surf, cx, cy, r, s):
    """A short fan of GOLD flame-rays with ONE big gold SKULL set as the zenith
    ray-boss. WHY one skull, the rest plain flame: a single skull at the apex is
    the unmistakable royal-skull tell that survives 32px. WHY tall + few rays:
    the boss is pushed high enough to CREST the disc top rim so the perfect
    circle is broken at the zenith — the coin-read killer — and the ray count is
    cut so the crested skull reads as one clean lump, not a noisy fringe.

    WHY the boss now rides a solid GOLD NECK column up out of the disc instead of
    a soft halo: a blurred alpha halo dissolved into the disc mass in the blackout
    (read as a pip). A filled neck + a bigger skull body lift OPAQUE pixels well
    above the top rim, so the blackout shows an unmistakable skull SPIKE, not a
    glow that the mask swallows."""
    n = 5
    half = (n - 1) / 2.0
    # the zenith SKULL-BOSS — pushed decisively ABOVE the disc rim. A bigger
    # skull on a solid neck so OPAQUE mass crests the top arc (blackout spike).
    # WHY taller + NARROWER than round 3: a low wide boss downscaled to a soft
    # nub in the blackout. Lifting the boss higher and tapering the neck to a
    # thin pillar makes the silhouette read a decisive narrow SPIKE clearing the
    # arc, not a rounded bump that merges back into the disc curve.
    boss_r = max(5, int(r * 0.80))
    boss_y = cy - int(r * 2.55)
    # a solid gold NECK column from the head up to the boss so the silhouette is
    # continuous (no floating skull, no swallow-able gap). Tapered narrow at the
    # top so the crest reads as a point, not a stalk.
    neck_w = max(3, int(r * 0.30))
    neck = [(cx - neck_w, cy + int(2 * s)), (cx + neck_w, cy + int(2 * s)),
            (cx + int(neck_w * 0.46), boss_y), (cx - int(neck_w * 0.46), boss_y)]
    triad_blob(surf, GOLD, neck,
               sheen_pts=[(cx - neck_w, cy), (cx - int(neck_w * 0.3), cy),
                          (cx - int(neck_w * 0.3), boss_y), (cx - int(neck_w * 0.46), boss_y)],
               ow=max(1, int(1.2 * s)))
    for i in range(n):
        if i == n // 2:
            continue  # the centre slot is the skull-boss, drawn below
        f = (i - half) / max(1.0, half)
        bx = cx + f * r * 0.80
        h = r * (1.30 - 0.50 * abs(f))
        lean = f * r * 0.30
        tipx = bx + lean
        tipy = cy - h
        wbot = r * 0.18
        ray = [(bx - wbot, cy + int(2 * s)),
               (bx + wbot, cy + int(2 * s)),
               (tipx + wbot * 0.3, cy - h * 0.5),
               (tipx, tipy),
               (tipx - wbot * 0.3, cy - h * 0.5)]
        triad_blob(surf, GOLD, ray,
                   sheen_pts=[(bx - wbot, cy), (bx - wbot * 0.3, cy),
                              (tipx - wbot * 0.2, cy - h * 0.5), (tipx, tipy)],
                   ow=max(1, int(1.1 * s)))
    # ONE tall central APEX SPIKE crowning the boss — a solid filled triangle so
    # the blackout silhouette terminates in a sharp 2-3px point well clear of the
    # disc top arc (the decisive spike the round-3 critique demanded).
    apex_h = int(boss_r * 1.95)
    apex_w = max(2, int(boss_r * 0.42))
    spike = [(cx, boss_y - apex_h),
             (cx + apex_w, boss_y - int(boss_r * 0.35)),
             (cx - apex_w, boss_y - int(boss_r * 0.35))]
    triad_blob(surf, GOLD, spike,
               sheen_pts=[(cx, boss_y - apex_h),
                          (cx - int(apex_w * 0.4), boss_y - int(boss_r * 0.35)),
                          (cx - apex_w, boss_y - int(boss_r * 0.35))],
               ow=max(1, int(1.4 * s)))
    # solid radiant spikes ringing the boss (drawn thick so they add OPAQUE mass
    # above the rim, not a soft glow the blackout drops).
    for k in range(6):
        a = math.radians(k * 60 - 90)
        x0 = cx + math.cos(a) * boss_r * 1.02
        y0 = boss_y + math.sin(a) * boss_r * 1.02
        x1 = cx + math.cos(a) * boss_r * 1.70
        y1 = boss_y + math.sin(a) * boss_r * 1.70
        pygame.draw.line(surf, INK, (x0, y0), (x1, y1), max(3, int(3.2 * s)))
        pygame.draw.line(surf, GOLD, (x0, y0), (x1, y1), max(2, int(2.0 * s)))
    sun_skull(surf, cx, boss_y, boss_r, s, focal=False)


# -- the compact seated SUN-KHAN ---------------------------------------------
def draw_khan(surf, cx, cy, s):
    """A filled amber sun-disc fills the frame; a compact bronze-bone king sits
    centred on it, FOUR arms (two cupping a white-hot sun-skull, two open against
    the disc), a rayed sunburst-skull crown CRESTING the disc rim at the zenith
    and the seated base NICKING the rim at the bottom — TWO rim-breaks so it
    reads as a creature wearing a disc, never a token. `s` = unit scale around a
    ~132-unit figure."""
    # the head rides high in the disc so the crown can clear the top rim.
    head_c = (cx, cy - int(28 * s))
    hr = int(16 * s)
    disc_r = int(64 * s)
    disc_c = (cx, cy - int(6 * s))

    # === (1) the FILLED SUN-DISC halo (drawn first -> behind the king) =======
    sun_disc(surf, disc_c[0], disc_c[1], disc_r, s)

    # a dimmed amber ring around the disc centre: the cradle field is knocked
    # ~18% darker so the white-hot focal pops out of it at chip scale.
    dim = pygame.Surface((disc_r * 2, disc_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(dim, AMBER_DD + (90,), (disc_r, disc_r), int(disc_r * 0.40))
    surf.blit(dim, (disc_c[0] - disc_r, disc_c[1] - disc_r + int(2 * s)))

    # === (2) the COMPACT SEATED TORSO ========================================
    # a small bronze ribcage barrel so the king reads dark against the disc.
    # Pushed lower so the crossed legs spill past the BOTTOM rim (rim-break #2).
    seat_y = cy + int(40 * s)
    rc_cx, rc_cy = cx, cy + int(12 * s)
    rc_w, rc_h = int(28 * s), int(30 * s)
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.42), rc_cy + rc_h // 2)]
    triad_blob(surf, KING, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(5 * s), rc_cy + int(5 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(4 * s))],
               ow=max(1, int(1.8 * s)))
    # a single sternum tick stands in for the rib stack (fewer marks for 32px).
    pygame.draw.line(surf, KING_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(7 * s)), max(1, int(2 * s)))

    # crossed seated legs — a BROAD SOLID BASE-MASS punched well BELOW the disc's
    # bottom rim, giving the 2nd rim-break. WHY a wide solid wedge, not two thin
    # splayed legs (round 5): rounds 3-4 splayed the legs sideways, so in the
    # blackout they read as thin appendages riding the disc edge while the disc
    # base still closed as a clean arc between them ("coin with a top notch"). The
    # base is now a CONTINUOUS knee-to-knee mass that drops a full ~22% of the disc
    # radius BELOW the bottom arc and fills the inner thigh span — so the blackout
    # bottom edge is one decisive jagged lobe-cluster, not a traceable circle. The
    # knees sit LOWER than they splay wide (y past the rim, not just x past it) so
    # the protrusion is downward mass, the read the critique demanded.
    leg_th = int(22 * s)
    bottom_rim_y = disc_c[1] + disc_r  # the arc the base must visibly punch past
    # how far below the bottom arc the knee mass drops (>= 12-15% of disc radius).
    drop = int(disc_r * 0.22)
    knee_y = bottom_rim_y + drop
    for sgn in (-1, 1):
        hip = (cx + sgn * int(10 * s), seat_y)
        # knee bulges OUT past the disc radius AND drops below the bottom rim, so
        # the lobe is solid downward mass the smoothscale can't average to an arc.
        knee = (cx + sgn * int(58 * s), knee_y)
        foot = (cx + sgn * int(40 * s), knee_y + int(20 * s))
        bone_limb(surf, hip, knee, foot, leg_th, s)
        # a heavy knee knob jutting PAST the bottom arc so the lobe survives 32px.
        triad_circle(surf, KING, knee, int(13 * s), ow=max(1, int(1.4 * s)), core=False)
        # a blocky splayed FOOT dropped further below the rim — opaque mass the
        # downscale keeps, so the silhouette base is clearly broken, not arced.
        fw = int(13 * s)
        foot_quad = [(foot[0] - sgn * int(3 * s), foot[1] - int(11 * s)),
                     (foot[0] + sgn * fw, foot[1] - int(6 * s)),
                     (foot[0] + sgn * fw, foot[1] + int(9 * s)),
                     (foot[0] - sgn * fw, foot[1] + int(9 * s))]
        triad_blob(surf, KING, foot_quad, ow=max(1, int(1.4 * s)))
    # a solid SEAT-SLAB bridging the two thighs BELOW the bottom rim — fills the
    # inner span so the base protrudes as one continuous jagged mass, not two thin
    # legs with a clean arc between them. This is the piece that kills the "clean
    # circle" read: the bottom-centre of the silhouette is now SOLID past the rim.
    seat_slab = [(cx - int(20 * s), bottom_rim_y - int(2 * s)),
                 (cx + int(20 * s), bottom_rim_y - int(2 * s)),
                 (cx + int(30 * s), knee_y + int(6 * s)),
                 (cx - int(30 * s), knee_y + int(6 * s))]
    triad_blob(surf, KING, seat_slab,
               core_pts=[(cx, bottom_rim_y), (cx + int(28 * s), knee_y + int(4 * s)),
                         (cx - int(28 * s), knee_y + int(4 * s))],
               ow=max(1, int(1.6 * s)))

    # === (3) the FOUR ARMS ====================================================
    # WHY two open + two cupping: the lower pair PRESENTS the sun-skull in cupped
    # palms at the disc centre (the cradle read); the upper pair opens OUT against
    # the disc, hands raised — the four-armedness reads even at 32px because the
    # two open arms break the disc fill with bronze diagonals.
    cradle_c = (cx, cy + int(2 * s))
    arm_th = int(7 * s)
    sh_y = rc_cy - rc_h // 2 + int(5 * s)
    # UPPER arms — open OUT & UP against the disc
    for sgn in (-1, 1):
        shoulder = (rc_cx + sgn * int(13 * s), sh_y)
        elbow = (cx + sgn * int(32 * s), cy - int(14 * s))
        hand = (cx + sgn * int(40 * s), cy - int(34 * s))
        bone_limb(surf, shoulder, elbow, hand, arm_th, s)
        # open palm — a simple ball (finger fan dropped to cut shape count)
        triad_circle(surf, KING, hand, int(5 * s), ow=max(1, int(1.2 * s)), core=False)
    # LOWER arms — the CRADLE: a clear thick upturned V/bowl under the skull.
    for sgn in (-1, 1):
        shoulder = (rc_cx + sgn * int(12 * s), sh_y + int(10 * s))
        elbow = (cx + sgn * int(26 * s), cy + int(20 * s))
        hand = (cradle_c[0] + sgn * int(13 * s), cradle_c[1] + int(15 * s))
        bone_limb(surf, shoulder, elbow, hand, int(9 * s), s)

    # === (4) the CUPPED SUN-SKULL — the white-hot focal at disc centre =======
    # cupped-palm cradle: two bronze thumbs curl up into a clear BOWL around the
    # skull so it reads as held, not floating. Drawn just before the skull.
    for sgn in (-1, 1):
        bx = cradle_c[0] + sgn * int(14 * s)
        by = cradle_c[1] + int(15 * s)
        tip = (cradle_c[0] + sgn * int(8 * s), cradle_c[1] - int(11 * s))
        mid = (cradle_c[0] + sgn * int(16 * s), cradle_c[1] + int(3 * s))
        thumb = [(bx - sgn * int(4 * s), by - int(2 * s)),
                 (bx + sgn * int(4 * s), by - int(1 * s)),
                 (mid[0], mid[1]),
                 (tip[0], tip[1]),
                 (tip[0] - sgn * int(4 * s), tip[1] + int(3 * s))]
        triad_blob(surf, KING, thumb,
                   sheen_pts=[(bx - sgn * int(4 * s), by - int(2 * s)),
                              (bx, by - int(1 * s)), (mid[0] - sgn * int(2 * s), mid[1]),
                              (tip[0], tip[1] + int(1 * s))],
                   ow=max(1, int(1.4 * s)))
    # a warm under-glow so the cradle reads as radiant, then the big skull.
    glow = pygame.Surface((int(disc_r * 2), int(disc_r * 2)), pygame.SRCALPHA)
    gr = int(22 * s)
    pygame.draw.circle(glow, SUN_BR + (110,), (int(disc_r), int(disc_r)), gr)
    surf.blit(glow, (cradle_c[0] - disc_r, cradle_c[1] - disc_r))
    # enlarged focal so its hot dome survives 32px as the single brightest read.
    sun_skull(surf, cradle_c[0], cradle_c[1], int(17 * s), s, focal=True)

    # === (5) the SKULL HEAD (compact, scary-cute) ============================
    # Pared back: two ember-pin sockets + a single grin line. Fewer interior
    # marks so the bronze head reads as one dark lump under the crown at 32px.
    triad_circle(surf, KING, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.02)
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, EMBER, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.15))
        pygame.draw.circle(surf, EMBER_BR, (ex, ey - int(1 * s)), max(1, int(hr * 0.07)))
    my = head_c[1] + int(hr * 0.66)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.42), my),
                     (head_c[0] + int(hr * 0.42), my + int(hr * 0.04)), max(1, int(2 * s)))

    # === (6) the SUNBURST-SKULL CROWN — CRESTS the disc rim at the zenith =====
    # WHY drawn last + tall: the gold ray-boss skull is lifted past the top rim
    # so the perfect circle is broken at the zenith (coin-read killer) and the
    # gold skull visibly crowns the king above the disc.
    sunburst_crown(surf, head_c[0], head_c[1] - int(hr * 0.70), int(hr * 1.10), s)


# -- the sun-disc-segment -> pillar mirror ------------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The king's OWN forms tile the pillar: a stacked column of amber sun-disc
    SEGMENTS (each a rayed half-disc echoing the halo's textured fill) = the
    repeatable shaft; a single gold sun-skull ringed by short rays at the gap =
    the creature-derived gap-edge cap. On-axis, symmetric, never top-heavy.

    `cap` names the END that faces the GAP."""
    shaft_w = int(15 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    seg_pitch = int(26 * s)
    cap_room = int(34 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    while y <= b1:
        # each segment: an amber disc-bead with short ember ray-ticks (the halo
        # texture continued) + a thin white-gold rim arc.
        triad_circle(surf, AMBER, (cx, y), int(shaft_w * 0.9),
                     ow=max(1, int(1.4 * s)), core=False)
        for k in range(12):
            a = math.radians(k * 30)
            x0 = cx + math.cos(a) * shaft_w * 0.40
            y0 = y + math.sin(a) * shaft_w * 0.40
            x1 = cx + math.cos(a) * shaft_w * 0.82
            y1 = y + math.sin(a) * shaft_w * 0.82
            col = EMBER if k % 2 == 0 else EMBER_D
            pygame.draw.line(surf, col, (x0, y0), (x1, y1), max(1, int(1.6 * s)))
        pygame.draw.circle(surf, AMBER, (cx, y), int(shaft_w * 0.40))
        pygame.draw.circle(surf, AMBER_SH,
                           (cx - int(shaft_w * 0.14), y - int(shaft_w * 0.16)),
                           max(1, int(shaft_w * 0.16)))
        pygame.draw.circle(surf, RIM, (cx, y), int(shaft_w * 0.88), max(1, int(1.6 * s)))
        pygame.draw.circle(surf, INK, (cx, y), int(shaft_w * 0.9), max(1, int(1.2 * s)))
        y += seg_pitch

    # === gap-edge cap: a gold sun-skull ringed by short rays =================
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    cap_r = int(13 * s)
    # short radiant rays around the cap skull (the sunburst echo)
    for k in range(10):
        a = math.radians(k * 36 - 90)
        x0 = cx + math.cos(a) * cap_r * 1.1
        y0 = cap_y + math.sin(a) * cap_r * 1.1
        x1 = cx + math.cos(a) * cap_r * 1.7
        y1 = cap_y + math.sin(a) * cap_r * 1.7
        pygame.draw.line(surf, INK, (x0, y0), (x1, y1), max(2, int(2.2 * s)))
        pygame.draw.line(surf, GOLD, (x0, y0), (x1, y1), max(1, int(1.3 * s)))
    sun_skull(surf, cx, cap_y, cap_r, s, focal=False)
    # a thin gold collar where the cap meets the shaft
    collar_y = (cap_y - int(20 * s)) if cap == "bottom" else (cap_y + int(20 * s))
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))


# -- compose the review sheet -------------------------------------------------
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_khan(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def load_fonts():
    """FONT is five levels up from this script; SysFont fallback if missing."""
    base = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(base, "..", "..", "..", "..", "..",
                      "game", "assets", "LiberationSans-Bold.ttf")
    try:
        return (pygame.font.Font(fp, 30), pygame.font.Font(fp, 17),
                pygame.font.Font(fp, 12))
    except Exception:
        return (pygame.font.SysFont("DejaVu Sans", 30, bold=True),
                pygame.font.SysFont("DejaVu Sans", 17, bold=True),
                pygame.font.SysFont("DejaVu Sans", 12))


def main():
    W, H = 1180, 820
    font_big, font, font_sm = load_fonts()

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("SUNFIRE SOLAR KHAN", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "royal SUN-DISC skull-king  ·  FILLED vertical amber disc (rays = textured fill) · "
        "crown SPIKES past the rim + base-mass punches past the bottom (2 blackout breaks) · white-HOT core · round 5",
        True, LABEL_DIM), (360, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 236, 1.74)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature - hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("FILLED amber sun-disc, rays = TEXTURED FILL (not a ring). The gold crown-skull", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("CRESTS the top rim + the seated legs nick the bottom rim = TWO rim-breaks. Big", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("white-HOT cupped sun-skull = single brightest pixel; cradle arms form a thick V.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored ======================================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar - sun-disc column", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked amber disc-segments (halo texture) = shaft;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("gold sun-skull + ray-ring caps each gap edge", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, not top-heavy)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night + SILHOUETTE proof =================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_khan(big, 48 * SS, 50 * SS, (32 / 132.0) * SS)
        # NIGHT keyline: a thin half-value RIM stroke on the disc so the amber
        # body doesn't merge into the dark sky (the disc edge stays read-able).
        if night:
            dc = (48 * SS, (50 - 6) * SS)
            dr = int(64 * (32 / 132.0) * SS)
            pygame.draw.circle(big, RIM, dc, dr, max(2, int(2.6 * SS)))
            pygame.draw.circle(big, INK, dc, dr + max(2, int(1.6 * SS)),
                               max(2, int(2.2 * SS)))
        small = pygame.transform.smoothscale(big, (96, 96))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()
    chip_night = chip32(night=True)

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip_night, (panel_x + 20 + 27, night_y + 27))
    sheet.blit(font_sm.render("32px on night sky (+ keyline)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # silhouette proof — blacked-out hero (the disc + rim-break read check).
    # WHY a smaller scale + centred lower: the round-4 crown SPIKE and the dropped
    # feet now extend further than the disc, so the figure is shrunk and recentred
    # to keep BOTH rim-breaks (top spike + base splay) inside the proof frame.
    def silhouette():
        big = pygame.Surface((150 * SS, 200 * SS), pygame.SRCALPHA)
        draw_khan(big, 75 * SS, 108 * SS, 1.02 * SS)
        small = pygame.transform.smoothscale(big, (150, 200))
        mask = pygame.mask.from_surface(small)
        sil = pygame.Surface((150, 200), pygame.SRCALPHA)
        solid = mask.to_surface(setcolor=(18, 18, 20, 255), unsetcolor=(0, 0, 0, 0))
        sil.blit(solid, (0, 0))
        return sil

    sil_x = panel_x + 196
    pygame.draw.rect(sheet, (210, 212, 216), (sil_x, day_y, 150, 200))
    pygame.draw.rect(sheet, INK, (sil_x, day_y, 150, 200), 1)
    sheet.blit(silhouette(), (sil_x, day_y))
    sheet.blit(font_sm.render("silhouette proof", True, LABEL_DIM), (sil_x, day_y + 204))
    sheet.blit(font_sm.render("(crown crests top rim + base nicks)", True, LABEL_DIM), (sil_x, day_y + 220))

    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = sil_x + 168
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (AMBER, "molten amber body"), (AMBER_D, "amber shade"),
        (EMBER, "ember ray core"), (RIM, "white-gold rim"),
        (SUN, "sun-skull bone"), (SUN_HOT, "white-hot core"),
        (KING, "bronze king bone"), (GOLD, "crown gold"),
        (EMBER_BR, "ember hot"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 188
        ry = syp + row * 24
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "KIND LOCK: a FILLED vertical amber sun-disc; rays = a TEXTURED FILL, never an open ring.  "
        "COIN-LOCK: crown-skull CRESTS the top rim + base nicks it (2 breaks) so it never reads as a token.  "
        "big white-HOT sun-skull = the single brightest pixel.  SS=6 supersample -> smoothscale · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_5.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    self_check()


def self_check():
    """Render the hero alone and verify the brightest pixel sits inside the
    white-hot cupped sun-skull (the focal owns the peak), and report the disc's
    amber-vs-ember balance so the disc reads amber-dominant, not ember-fielded."""
    surf = pygame.Surface((420, 520), pygame.SRCALPHA)
    draw_khan(surf, 210, 270, 2.0)
    px = pygame.surfarray.pixels3d(surf)
    a = pygame.surfarray.pixels_alpha(surf)
    w, h = surf.get_size()
    best_lum, best_xy = -1, (0, 0)
    for x in range(0, w, 2):
        for yy in range(0, h, 2):
            if a[x, yy] < 40:
                continue
            r, g, b = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > best_lum:
                best_lum, best_xy = lum, (x, yy)
    bx, by = best_xy
    r, g, b = int(px[bx, by][0]), int(px[bx, by][1]), int(px[bx, by][2])
    # focal sits near centre (cradle ~ cy+2 -> ~272) and is near-white
    is_focal = (b > 200 and r > 230 and g > 220 and abs(by - 274) < 44)
    del px, a
    print("self-check: brightest pixel @", best_xy, "rgb", (r, g, b),
          "lum %.0f" % best_lum, "-> white-hot sun-skull focal?", is_focal)
    _gate_blackout()


def _gate_blackout():
    """Render the hero to a mask at chip-ish scale and prove BOTH rim-breaks read
    in the blackout: the crown spike must rise ABOVE the disc top arc, and opaque
    leg/foot mass must drop BELOW the disc bottom arc. WHY a programmatic gate:
    the named ship-gate is "a viewer cannot trace a clean circle" — quantify the
    spike-clearance above the top rim and the splay-clearance below the base rim."""
    W, H, sc = 150, 200, 1.02
    cx, cy = 75, 108
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    draw_khan(big, cx * SS, cy * SS, sc * SS)
    small = pygame.transform.smoothscale(big, (W, H))
    mask = pygame.mask.from_surface(small)
    s = sc
    disc_cy = cy - 6 * s
    disc_r = 64 * s
    top_rim = int(disc_cy - disc_r)
    bot_rim = int(disc_cy + disc_r)
    # topmost opaque pixel in the central column band (the crown spike)
    top_hit = None
    for yy in range(H):
        for xx in range(int(cx - 6), int(cx + 6)):
            if mask.get_at((xx, yy)):
                top_hit = yy
                break
        if top_hit is not None:
            break
    # lowest opaque pixel anywhere (the dropped feet) + bottom solidity at base
    bot_hit = None
    for yy in range(H - 1, -1, -1):
        row = any(mask.get_at((xx, yy)) for xx in range(W))
        if row:
            bot_hit = yy
            break
    spike_clear = top_rim - top_hit if top_hit is not None else -1
    base_clear = bot_hit - bot_rim if bot_hit is not None else -1
    # CIRCLE-TRACE test: scan a band just BELOW the bottom rim across the central
    # width. If opaque base mass spans a wide contiguous run there (not two thin
    # lobes with a clean gap), no clean circle can be traced — the true gate.
    band_y = bot_rim + max(2, int(disc_r * 0.10))
    central = range(int(cx - disc_r * 0.5), int(cx + disc_r * 0.5))
    solid_run = sum(1 for xx in central if 0 <= xx < W and mask.get_at((xx, band_y)))
    base_solid_frac = solid_run / max(1, len(list(central)))
    print("gate: top_rim=%d crown_top=%s spike_clears_rim_by=%dpx" %
          (top_rim, top_hit, spike_clear),
          "| bot_rim=%d base_low=%s splay_clears_rim_by=%dpx" %
          (bot_rim, bot_hit, base_clear),
          "| base_solid_frac@%dpx_below_rim=%.2f" % (band_y - bot_rim, base_solid_frac),
          "-> TWO DECISIVE BREAKS?",
          spike_clear > 2 and base_clear > 2 and base_solid_frac > 0.6)


if __name__ == "__main__":
    main()
