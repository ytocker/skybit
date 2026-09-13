"""
Round-2 concept renderer for the OPAL PEARL-DIVER QUEEN — a royal skull-KING of
the second skull-kings brood (Skull Kings II). Headless Pygame; ELEVATED pipeline
(SS=6 supersample -> smoothscale) so the layered shell detail survives downscale.
Clones the house grammar from the sibling king renderers: flat triad fills
(dark-core -> flat fill -> top-left sheen), a hard 1-2px ink keyline, 1px
alpha-grown outline, chibi scary-CUTE proportions; procedural-only (no PNGs/
gradients).

WHY this KIND is de-collided from its siblings: the queen is a FLOATING
TIER-STACK with NO feet — soft scalloped nacre shell-rings that WIDEN DOWNWARD
like an inverted mother-of-pearl pagoda over a rounded base. The downward-widen
is the critical lock: it reads opposite to the up-narrowing stupa kings and to
any asymmetric slump — this stack stays symmetric, buoyant, tiered. The boss is
royalty via a SKULL-CROWN that frames the head, not via gilt.

WHY the cupped OPAL SKULL owns the focal: the single hard gate is one dominant
mass (the pale nacre tier-stack body) + thin accents, with the named focal as
the single brightest pixel. Four lower hands CUP a luminous shifting-pastel opal
skull at the belly — that opal skull is pushed to near-white at its core so it
is the unambiguous brightest point. The two flanking nacre crown-skulls are kept
SMALL and dim so they never compete. Body iridescence is a FIXED 3-fleck pattern
(pink/teal/gold), never animated — tiny chips of chroma on a cool pale field, so
the body stays one calm mass and the opal skull keeps all the glow.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# -- PINNED PALETTE -----------------------------------------------------------
# Pale nacre body is the dominant cool mass; everything bright is reserved for
# the cupped opal skull so it owns the single brightest pixel.
# WHY the whole body is dropped a notch below round 2: the nacre tiers + the
# white face-disc were tying the opal skull on value at 32px. Holding the
# dominant mass in the upper-mid range (not near-white) reserves the top of the
# value scale for the gem alone, so the cupped opal skull wins the brightest-
# pixel test outright instead of by a hair.
NACRE     = (210, 208, 220)   # pale mother-of-pearl body (the dominant fill)
NACRE_D   = (170, 168, 186)   # nacre dark-core / tier shade
NACRE_DD  = (132, 130, 152)   # deepest nacre hollow (ring undersides)
NACRE_SH  = (230, 230, 240)   # cool top-left rim-sheen (kept below the gem core)
# WHY a FIXED mid-value grey-lilac nacre for the FACE-DISC: rounds 1-5 kept the
# head at or near the top of the value scale, so at 32px the face-disc + the gem
# were two near-white masses that merged into one white blob and the eye picked
# the LARGER one (the disc). Pinning the head to a mid-nacre value (lum ~168, a
# clear step BELOW the pale body's ~210 and far below the gem's ~211 luminous
# teal) demotes the disc to quiet body — it can no longer tie or out-mass the gem
# on the brightest-pixel test, so the cupped opal skull becomes the SOLE focal.
MID_NACRE = (168, 164, 188)   # the demoted FACE-DISC fill — quiet mid grey-lilac
MID_NACRE_SH = (188, 184, 206) # gentle cool sheen for the demoted disc (NOT white)
RIM       = (208, 214, 222)   # mother-of-pearl cool rim edge
# WHY a cool, slightly-blue rim-light distinct from the warm sheen: on a light
# day sky the warm top-left sheen alone is too close to the sky value, so a cool
# bluish mother-of-pearl rim wrapped along the LOWER/RIGHT edge keeps the body
# detached from the sky regardless of which way the light falls.
RIMLIGHT  = (172, 196, 224)   # cool blue mother-of-pearl rim-light
SEAM_SH   = ( 96,  98, 124)   # cool drop-shadow under each scallop tier seam
# the FIXED 3-fleck iridescence — tiny static chips of chroma on the body.
# WHY exactly three pinned hues, never animated: a calm scatter of pink/teal/gold
# specks reads as nacre shimmer without becoming a second mass; an animated or
# dense fleck field would muddy the body and steal glow from the opal skull.
FLECK_PINK = (196, 170, 214)
FLECK_TEAL = (150, 212, 206)
FLECK_GOLD = (214, 184,  96)
# the SOLE luminous focal — the cupped OPAL SKULL. WHY one SATURATED TEAL hue,
# not a multi-pastel shimmer: with the face-disc demoted to mid-nacre, the gem is
# the only thing allowed at the top of the value scale, and it must ALSO be the
# single most-saturated pixel. A pearl-diver-queen's opal reads as deep-sea
# fire-teal; pinning the whole gem to ONE saturated teal family (rather than a
# pink+teal+gold scatter that averages to muddy pale on the downscale) keeps the
# core's chroma intact at 32px — it lands high-luminance AND high-saturation, so
# nothing else on the creature can tie it.
OPAL      = (120, 226, 212)   # opal skull mid (saturated teal shell)
OPAL_PINK = (138, 240, 222)   # secondary teal flush (kept in the teal family)
OPAL_TEAL = (110, 236, 214)   # primary teal flush
OPAL_BR   = (150, 250, 230)   # opal bright teal (kept saturated, never near-white)
# WHY the hottest core is a SATURATED LUMINOUS TEAL, not pure white: pure white
# (sat 0) can only TIE every other near-white shape on the downscale and then
# lose on size to the larger disc (the round-4/5 failure). A high-luminance
# saturated teal core (lum ~211, sat ~135) ranks #1 in BOTH luminance AND
# saturation: it out-brights the demoted mid-nacre face-disc (lum ~168) and the
# night chip's teal RIM is gated out (it is a dark edge, not a bright fill), so
# the gem is the single brightest+most-saturated point on day and night alike.
OPAL_HOT  = (138, 255, 232)   # hottest opal core — luminous saturated teal
OPAL_FIRE = ( 70, 236, 206)   # deep teal under-ring driving the core's chroma
# WHY a dedicated strongly-green-dominant additive bloom tint (low R+B): repeated
# additive passes sum their channels, so a tint with high R or B clamps the core
# to 253-253-253 (a white pinpoint) on the downscale. Holding R+B low keeps the
# summed bloom green-biased, so the brightest pixel itself stays a saturated teal.
OPAL_BLOOM = ( 24, 210, 150)  # additive bloom tint (green-dominant, low R+B)
OPAL_D    = ( 60, 150, 150)   # opal shade / socket rim (teal-deep)
OPAL_RIM  = ( 40, 108, 112)
# WHY a dedicated near-black cradle: the tier directly behind the gem is darkened
# to this so the bloom reads as one bright bead against shadow, not a pale lump
# floating on a pale belly.
OPAL_BACK = ( 54,  56,  78)   # darkened nacre tier directly behind the gem
PEARL     = (244, 240, 234)   # the strand + flanking crown pearls (warm-white)
PEARL_D   = (196, 190, 184)
CONCH     = (236, 214, 206)   # conch shell (soft warm pink-cream accent)
CONCH_D   = (198, 164, 158)
CONCH_BR  = (250, 236, 230)
INK       = ( 28,  22,  30)   # hard ink keyline

BG        = ( 96, 100, 108)
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


def bone_limb(surf, p0, p1, p2, thick, s, joint=True):
    """A two-segment nacre arm; reused for the six arms. Pale shell, not bone."""
    for (a, b) in ((p0, p1), (p1, p2)):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * thick / 2, dx / L * thick / 2
        quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
        triad_blob(surf, NACRE, quad,
                   sheen_pts=[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                              (b[0] + nx * 0.3, b[1] + ny * 0.3),
                              (a[0] + nx * 0.3, a[1] + ny * 0.3)],
                   ow=max(1, int(thick * 0.16)))
    if joint:
        triad_circle(surf, NACRE, p1, int(thick * 0.58), ow=max(1, int(1.1 * s)),
                     core=False)


# -- FIXED iridescent fleck pattern -------------------------------------------
# WHY a deterministic offset list, not random: the shimmer must be IDENTICAL on
# every render so it reads as worked nacre inlay, not noise. Each fleck is a tiny
# 3-px chip. WHY clustered tight to the rim arc + the tier seam (top + lower
# lip) and NEVER the flat centre or the base: a scatter spread evenly across the
# body reads as loose coin-sparkles; hugging the rim and seam reads as light
# catching the worked edges of nacre — the shimmer becomes a tell of the shell
# layering instead of a competing speckle field.
_FLECKS = [
    # upper rim-arc cluster
    (-0.30, -0.40, FLECK_PINK), (-0.06, -0.46, FLECK_TEAL),
    (0.22, -0.40, FLECK_GOLD),
    # lower-lip seam cluster
    (-0.34, 0.34, FLECK_TEAL), (-0.10, 0.40, FLECK_GOLD),
    (0.18, 0.38, FLECK_PINK), (0.40, 0.30, FLECK_TEAL),
]


def scatter_flecks(surf, cx, cy, w, h, s, density=1.0):
    """Stamp the clustered fleck pattern hugging the rim + seam of a tier."""
    for (fx, fy, col) in _FLECKS:
        px = int(cx + fx * w * 0.5)
        py = int(cy + fy * h * 0.5)
        r = max(1, int(1.6 * s * density))
        pygame.draw.circle(surf, lerp(col, NACRE_SH, 0.2), (px, py), r)
        pygame.draw.circle(surf, col, (px, py), max(1, r - max(1, int(s))))


def nacre_tier(surf, cx, cy, w, h, s, flecks=True):
    """One soft scalloped shell-tier ring. A flattened blob with a scalloped
    lower lip and a cool mother-of-pearl rim. Tiers stack so each lower ring is
    WIDER (the inverted-pagoda lock).

    WHY a fat full-perimeter ink keyline + a cool rim-light wrapping the
    lower/right edge: on a light day sky the pale body alone washes out, so a
    thick dark edge all the way around detaches every tier from the sky and the
    cool rim-light re-asserts the bottom/right contour the warm top-left sheen
    leaves dark."""
    rect = (cx - w // 2, cy - h // 2, w, h)
    # cool drop-shadow cast UNDER this tier's seam — a fat dark crescent below the
    # lower lip so the downward-widening rings read as distinctly stacked shells.
    # WHY pushed deeper + taller again in round 4: at 32px the round-3 seam was
    # still too pale a cool — the downward-widening shells averaged into one
    # smooth column. Driving the trench most of the way to ink (and taller) is
    # what makes each shell resolve as a separate stacked bead on the downscale.
    pygame.draw.ellipse(surf, lerp(SEAM_SH, INK, 0.55),
                        (rect[0], int(cy + h * 0.06),
                         rect[2], int(h * 0.78)))
    pygame.draw.ellipse(surf, lerp(SEAM_SH, INK, 0.25),
                        (rect[0] + int(2 * s), int(cy + h * 0.14),
                         rect[2] - int(4 * s), int(h * 0.56)))
    # fat full-perimeter ink keyline
    kpx = max(2, int(2.2 * s))
    pygame.draw.ellipse(surf, INK, (rect[0] - kpx, rect[1] - kpx,
                                    rect[2] + 2 * kpx, rect[3] + 2 * kpx))
    pygame.draw.ellipse(surf, NACRE_DD, rect)
    pygame.draw.ellipse(surf, NACRE, (rect[0], rect[1], rect[2], int(rect[3] * 0.82)))
    # warm top-left sheen band
    pygame.draw.ellipse(surf, NACRE_SH,
                        (cx - int(w * 0.40), cy - int(h * 0.42),
                         int(w * 0.46), int(h * 0.40)))
    # cool mother-of-pearl RIM-LIGHT wrapping the lower/right contour (a bright
    # cool arc inside the ink edge so the body never melts into a light sky)
    pygame.draw.arc(surf, RIMLIGHT,
                    (rect[0] + int(1.4 * s), rect[1] + int(2 * s),
                     rect[2] - int(2.8 * s), rect[3] - int(2 * s)),
                    math.radians(300), math.radians(150), max(2, int(2.0 * s)))
    # scalloped lower lip — soft rounded bumps reading as shell layering
    n = 7
    for i in range(n):
        t = (i + 0.5) / n
        sx = cx - w * 0.46 + t * w * 0.92
        sy = cy + h * 0.30
        br = w * (0.072)
        pygame.draw.circle(surf, NACRE_D, (int(sx), int(sy)), max(1, int(br)))
        pygame.draw.circle(surf, lerp(NACRE, NACRE_SH, 0.4),
                           (int(sx - br * 0.3), int(sy - br * 0.3)), max(1, int(br * 0.45)))
    # cool mother-of-pearl rim arc along the top
    pygame.draw.arc(surf, RIM, (rect[0] + int(2 * s), rect[1] + int(1 * s),
                                rect[2] - int(4 * s), int(rect[3] * 0.7)),
                    math.radians(200), math.radians(340), max(1, int(1.6 * s)))
    if flecks:
        scatter_flecks(surf, cx, cy - int(h * 0.06), w, h, s)


def small_crown_skull(surf, cx, cy, r, s):
    """A small flanking nacre crown-skull. WHY kept small + low-contrast: it
    frames the head as a paired tell but must never out-bright the cupped opal
    skull — so its dome is pale nacre and its sockets are soft, not punched."""
    triad_circle(surf, NACRE, (cx, cy), r, ow=max(1, int(1.2 * s)), core=False)
    for sgn in (-1, 1):
        pygame.draw.circle(surf, NACRE_DD,
                           (cx + sgn * int(r * 0.42), cy - int(r * 0.02)),
                           max(1, int(r * 0.26)))
        pygame.draw.circle(surf, INK,
                           (cx + sgn * int(r * 0.42), cy - int(r * 0.02)),
                           max(1, int(r * 0.18)))
    # stub jaw
    pygame.draw.polygon(surf, NACRE_D,
                        [(cx - int(r * 0.30), cy + int(r * 0.46)),
                         (cx + int(r * 0.30), cy + int(r * 0.46)),
                         (cx, cy + int(r * 0.78))])


def shell_horn(surf, cx, cy, r, sgn, s):
    """A curved nacre shell-horn flanking the head, carrying a small crown-skull
    at its tip. The horn sweeps up-and-outward like a spiral shell rib."""
    pts = []
    for k in range(9):
        t = k / 8.0
        ang = math.radians(-90 + sgn * (20 + t * 70))
        rr = r * (0.4 + t * 1.05)
        pts.append((cx + math.cos(ang) * rr * 0.7,
                    cy + math.sin(ang) * rr))
    # build a tapering ribbon along the spine points
    th0, th1 = r * 0.34, r * 0.10
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        t = i / (len(pts) - 1)
        th = th0 + (th1 - th0) * t
        if i < len(pts) - 1:
            nx, ny = pts[i + 1][0] - x, pts[i + 1][1] - y
        else:
            nx, ny = x - pts[i - 1][0], y - pts[i - 1][1]
        L = max(1.0, math.hypot(nx, ny))
        px, py = -ny / L * th, nx / L * th
        left.append((x + px, y + py))
        right.append((x - px, y - py))
    poly = left + right[::-1]
    triad_blob(surf, NACRE, poly,
               sheen_pts=left + [left[-1]],
               ow=max(1, int(1.2 * s)))
    # a thin teal-fleck spiral ridge line down the horn
    pygame.draw.lines(surf, lerp(FLECK_TEAL, NACRE, 0.3), False,
                      [(int(x), int(y)) for x, y in pts], max(1, int(1.2 * s)))
    tip = pts[-1]
    small_crown_skull(surf, int(tip[0]), int(tip[1]), int(r * 0.36), s)
    return tip


def conch(surf, cx, cy, r, s):
    """A soft warm conch shell held in an upper hand — a thin warm accent."""
    pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(s)))
    pygame.draw.circle(surf, CONCH_D, (cx, cy), r)
    pygame.draw.circle(surf, CONCH, (cx - int(r * 0.1), cy - int(r * 0.1)), int(r * 0.82))
    # spiral whorl
    for k in range(3):
        rr = r * (0.66 - k * 0.18)
        pygame.draw.arc(surf, CONCH_D,
                        (cx - int(rr), cy - int(rr), int(rr * 2), int(rr * 2)),
                        math.radians(20 + k * 40), math.radians(250 + k * 40),
                        max(1, int(1.4 * s)))
    pygame.draw.circle(surf, CONCH_BR, (cx - int(r * 0.32), cy - int(r * 0.34)),
                       max(1, int(r * 0.22)))
    # spout lip
    pygame.draw.polygon(surf, CONCH,
                        [(cx + int(r * 0.5), cy - int(r * 0.2)),
                         (cx + int(r * 1.05), cy + int(r * 0.05)),
                         (cx + int(r * 0.5), cy + int(r * 0.35))])
    pygame.draw.polygon(surf, INK,
                        [(cx + int(r * 0.5), cy - int(r * 0.2)),
                         (cx + int(r * 1.05), cy + int(r * 0.05)),
                         (cx + int(r * 0.5), cy + int(r * 0.35))], max(1, int(1.1 * s)))


def pearl_strand(surf, x0, y0, x1, y1, n, r, s):
    """A draped strand of small pearls held by an upper hand — thin accent."""
    pygame.draw.line(surf, PEARL_D, (x0, y0), (x1, y1), max(1, int(1.2 * s)))
    for i in range(n):
        t = i / max(1, n - 1)
        # gentle catenary sag
        sag = math.sin(t * math.pi) * (10 * s)
        px = int(x0 + (x1 - x0) * t)
        py = int(y0 + (y1 - y0) * t + sag)
        pygame.draw.circle(surf, INK, (px, py), r + max(1, int(0.7 * s)))
        pygame.draw.circle(surf, PEARL_D, (px, py), r)
        pygame.draw.circle(surf, PEARL, (px, py), max(1, int(r * 0.82)))
        pygame.draw.circle(surf, NACRE_SH, (px - int(r * 0.3), py - int(r * 0.3)),
                           max(1, int(r * 0.32)))


def opal_socket(surf, cx, cy, r, s):
    """The dark cradle the opal skull sits in (so the glow reads against shadow).
    WHY a wide darkened back-disc, not just a thin rim: the tier directly behind
    the gem is painted near-black here so the bloom reads as one bright bead
    against shadow instead of a pale lump on a pale belly tier."""
    # darkened back-disc that locally shades the belly tier behind the gem.
    # WHY a still-WIDER + DARKER cool pocket than round 3: at 32px the round-3
    # halo collapsed — the bright bloom ate its own dark ring on the downscale.
    # Pushing the outer pocket to 2.6·r and driving the whole stack deeper toward
    # ink keeps a visible dark halo surviving AROUND the gem at gameplay scale, so
    # the bead still reads as one bright point sitting in shadow, not a pale lump.
    for (rr, col) in ((2.6, lerp(OPAL_BACK, NACRE_DD, 0.30)),
                      (2.15, lerp(OPAL_BACK, INK, 0.30)),
                      (1.7, lerp(OPAL_BACK, INK, 0.55)),
                      (1.35, lerp(OPAL_BACK, INK, 0.72))):
        pygame.draw.circle(surf, col, (cx, cy), int(r * rr))
    sr = int(r * 1.22)
    socket = []
    for k in range(24):
        a = math.radians(k * 15)
        socket.append((cx + math.cos(a) * sr, cy + math.sin(a) * sr * 1.10))
    pygame.draw.polygon(surf, INK, socket)
    pygame.draw.polygon(surf, OPAL_RIM, [(p[0], p[1]) for p in socket])


def opal_skull(surf, cx, cy, r, s):
    """The cupped luminous OPAL SKULL — the SOLE bright focal. One saturated teal
    family around a luminous teal hot core. WHY teal halos + a saturated teal core
    (not white): the focal must win BOTH the brightest- AND most-saturated-pixel
    test at 32px, so the core is a high-luminance saturated teal, surrounded by
    teal light, never bleached to a desaturated white pinpoint."""
    # additive TEAL bloom — wide + bright, but tinted teal so it does NOT wash the
    # core to pure white. WHY teal-additive, not white-additive: a white additive
    # bloom drives every channel to 255, killing the gem's saturation on the
    # downscale. A teal bloom (G high, R+B held lower) raises luminance while
    # keeping a wide chroma spread, so the averaged core lands high-luminance AND
    # high-saturation — the single brightest AND most-saturated point that beats
    # the demoted mid-nacre face-disc on day and the dark teal rim on night.
    for (rr, a) in ((r * 2.6, 30), (r * 1.9, 50), (r * 1.35, 76),
                    (r * 0.9, 96), (r * 0.55, 110)):
        halo = pygame.Surface((int(rr * 2) + 4, int(rr * 2) + 4), pygame.SRCALPHA)
        pygame.draw.circle(halo, OPAL_BLOOM + (a,), (int(rr) + 2, int(rr) + 2), int(rr))
        surf.blit(halo, (cx - int(rr) - 2, cy - int(rr) - 2),
                  special_flags=pygame.BLEND_RGBA_ADD)
    # cranium dome
    pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(1.4 * s)))
    pygame.draw.circle(surf, OPAL_D, (cx, cy), r)
    pygame.draw.circle(surf, OPAL, (cx, cy), int(r * 0.92))
    # pastel flushes (fixed placement, the opal's shifting-colour read)
    pygame.draw.circle(surf, OPAL_PINK, (cx - int(r * 0.30), cy - int(r * 0.18)),
                       int(r * 0.42))
    pygame.draw.circle(surf, OPAL_TEAL, (cx + int(r * 0.34), cy + int(r * 0.10)),
                       int(r * 0.38))
    pygame.draw.circle(surf, OPAL_BR, (cx - int(r * 0.10), cy - int(r * 0.06)),
                       int(r * 0.46))
    # jaw
    jaw = [(cx - int(r * 0.46), cy + int(r * 0.42)),
           (cx + int(r * 0.46), cy + int(r * 0.42)),
           (cx + int(r * 0.30), cy + int(r * 0.92)),
           (cx - int(r * 0.30), cy + int(r * 0.92))]
    pygame.draw.polygon(surf, INK, jaw)
    pygame.draw.polygon(surf, OPAL, jaw)
    pygame.draw.polygon(surf, OPAL_BR,
                        [(cx - int(r * 0.30), cy + int(r * 0.46)),
                         (cx + int(r * 0.10), cy + int(r * 0.46)),
                         (cx, cy + int(r * 0.80))])
    # eye sockets — kept as soft dark pits so the bright dome stays the read
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.42)
        ey = cy - int(r * 0.04)
        pygame.draw.circle(surf, OPAL_RIM, (ex, ey), int(r * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(r * 0.24))
        pygame.draw.circle(surf, OPAL_TEAL, (ex, ey + int(r * 0.02)), max(1, int(r * 0.10)))
    # tooth gaps
    my = cy + int(r * 0.64)
    for k in range(-2, 3):
        pygame.draw.line(surf, OPAL_RIM,
                         (cx + int(k * r * 0.16), my - int(r * 0.10)),
                         (cx + int(k * r * 0.16), my + int(r * 0.16)),
                         max(1, int(1.0 * s)))
    # the HOTTEST core pip — the single brightest AND most-saturated pixel of the
    # whole creature. WHY a FAT solid SATURATED-TEAL core (≥0.6·r) laid last over a
    # deep-teal under-ring, with only a GENTLE teal additive top-bloom: a pure-white
    # core can only TIE the other near-white shapes and lose on size. A saturated
    # teal core that still spans 2-3 solid pixels after the downscale — kept just
    # shy of white so the red+blue channels stay held down under green — wins both
    # tests outright: no other shape on the creature carries this much chroma at
    # this much luminance, and the demoted mid-nacre disc can't approach it.
    core_c = (cx - int(r * 0.06), cy - int(r * 0.06))
    pygame.draw.circle(surf, OPAL_PINK, (core_c[0] - int(r * 0.20), core_c[1]),
                       max(3, int(r * 0.50)))
    pygame.draw.circle(surf, OPAL_TEAL, (core_c[0] + int(r * 0.20), core_c[1] + int(r * 0.06)),
                       max(3, int(r * 0.44)))
    pygame.draw.circle(surf, OPAL_FIRE, core_c, max(3, int(r * 0.60)))
    pygame.draw.circle(surf, OPAL_HOT, core_c, max(3, int(r * 0.48)))
    # a final TEAL additive top-bloom — kept gentle and NOT stacked tight on the
    # centre, so it lifts the halo's luminance without three additive passes
    # summing the core's channels past 255 (which would bleach the teal chroma
    # back to white). The saturated teal core, not a white pinpoint, stays the
    # brightest read.
    for (rr, a) in ((r * 0.95, 70), (r * 0.65, 96), (r * 0.42, 110)):
        halo = pygame.Surface((int(rr * 2) + 4, int(rr * 2) + 4), pygame.SRCALPHA)
        pygame.draw.circle(halo, OPAL_BLOOM + (a,), (int(rr) + 2, int(rr) + 2), int(rr))
        surf.blit(halo, (core_c[0] - int(rr) - 2, core_c[1] - int(rr) - 2),
                  special_flags=pygame.BLEND_RGBA_ADD)


# -- the floating tier-stack queen --------------------------------------------
def draw_queen(surf, cx, cy, s):
    head_c = (cx, cy - int(46 * s))
    hr = int(20 * s)

    # === FLOATING TIER-STACK BODY (drawn first, behind arms) =================
    # Rings WIDEN DOWNWARD (inverted-nacre-pagoda lock). No feet; a soft rounded
    # base closes the stack so it reads as buoyant, hovering.
    # (cy offset from head, widths, heights) — top-narrow -> bottom-wide.
    tiers = [
        (cy - int(20 * s), int(34 * s), int(20 * s)),
        (cy - int(4 * s),  int(48 * s), int(24 * s)),
        (cy + int(16 * s), int(64 * s), int(28 * s)),
        (cy + int(40 * s), int(82 * s), int(32 * s)),
    ]
    for (ty, tw, th) in tiers:
        nacre_tier(surf, cx, ty, tw, th, s)
    # soft rounded base cap closing the bottom of the stack (fat ink keyline +
    # cool rim-light along its lower edge; WHY no flecks here: clustering shimmer
    # only at rims/seams keeps it reading as nacre, not loose coin-sparkles).
    base_y = cy + int(58 * s)
    pygame.draw.ellipse(surf, INK,
                        (cx - int(42 * s), base_y - int(11 * s),
                         int(84 * s), int(30 * s)))
    pygame.draw.ellipse(surf, NACRE_D,
                        (cx - int(38 * s), base_y - int(9 * s),
                         int(76 * s), int(24 * s)))
    pygame.draw.ellipse(surf, NACRE,
                        (cx - int(36 * s), base_y - int(9 * s),
                         int(72 * s), int(16 * s)))
    pygame.draw.arc(surf, RIMLIGHT,
                    (cx - int(37 * s), base_y - int(8 * s),
                     int(74 * s), int(22 * s)),
                    math.radians(190), math.radians(350), max(2, int(2.0 * s)))
    # a faint shadow ellipse below to sell that it floats (separated from base)
    shadow = pygame.Surface((int(70 * s), int(16 * s)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (40, 40, 56, 60), shadow.get_rect())
    surf.blit(shadow, (cx - int(35 * s), base_y + int(20 * s)))

    # === UPPER TWO ARMS — conch (left) + pearl-strand (right) ================
    arm_th = int(6 * s)
    # left upper arm holds the conch out to the side
    sh_l = (cx - int(20 * s), cy - int(26 * s))
    el_l = (cx - int(40 * s), cy - int(20 * s))
    hd_l = (cx - int(52 * s), cy - int(6 * s))
    bone_limb(surf, sh_l, el_l, hd_l, arm_th, s)
    conch(surf, hd_l[0] - int(2 * s), hd_l[1] + int(6 * s), int(11 * s), s)
    # right upper arm holds the pearl-strand
    sh_r = (cx + int(20 * s), cy - int(26 * s))
    el_r = (cx + int(40 * s), cy - int(20 * s))
    hd_r = (cx + int(50 * s), cy - int(8 * s))
    bone_limb(surf, sh_r, el_r, hd_r, arm_th, s)
    pearl_strand(surf, hd_r[0], hd_r[1] + int(2 * s),
                 cx + int(20 * s), cy + int(6 * s), 6, int(3 * s), s)

    # === OPAL SOCKET + the FOUR LOWER HANDS that CUP the opal skull ===========
    opal_c = (cx, cy + int(8 * s))
    opal_r = int(15 * s)
    # WHY a WIDE ink negative-space basin around + below the cradle before the
    # arms: at 32px the four cupping hands merged into the belly tier in round 2
    # because the round-2 trench was too small. A broad opaque dark cup — a wide
    # lower ellipse plus a flanking dark notch on each side of the gem — gives the
    # fingers a deep shadow to read against on all sides, so the "four hands
    # holding a bright bead" silhouette survives the downscale.
    # WHY a BIGGER + fully-opaque basin than round 3, plus a vertical ink wedge
    # splitting the left pair from the right pair: at 32px the four hands smeared
    # back into one pale belly-mass because the negative space between them was
    # too thin to survive the downscale. A broad opaque dark cup, deep flanking
    # notches, AND a central dark trench between the two hand-pairs give every
    # finger a thick shadow gap on all sides — so the "four hands cupping a bead"
    # cradle stays separated at gameplay scale.
    cup_gap = pygame.Surface((int(opal_r * 6.4), int(opal_r * 5.0)), pygame.SRCALPHA)
    pygame.draw.ellipse(cup_gap, (12, 10, 18, 255), cup_gap.get_rect())
    surf.blit(cup_gap, (opal_c[0] - int(opal_r * 3.2),
                        opal_c[1] - int(opal_r * 0.7)))
    # flanking dark notches that bite IN between the belly tier and each pair of
    # hands so the cradle's outer edges separate from the body at 32px
    for sgn in (-1, 1):
        notch = pygame.Surface((int(opal_r * 2.2), int(opal_r * 3.1)),
                               pygame.SRCALPHA)
        pygame.draw.ellipse(notch, (12, 10, 18, 255), notch.get_rect())
        surf.blit(notch, (opal_c[0] + sgn * int(opal_r * 2.05) - int(opal_r * 1.10),
                          opal_c[1] - int(opal_r * 1.0)))
    # central ink wedge below the gem — separates the left hand-pair from the
    # right so the cradle reads as TWO cupping pairs, not one solid lower lump.
    # WHY thickened + carried still deeper in round 6: with the gem now the SOLE
    # focal, the cradle must unambiguously read as hands-around-a-skull at 32px —
    # so the negative-space trench under + between the four hands is fattened (a
    # wider mouth, deeper drop) to a genuine dark gap the downscale cannot smear
    # shut, locking the four-hands silhouette instead of a merge into the belly.
    wedge = [(opal_c[0] - int(opal_r * 0.66), opal_c[1] + int(opal_r * 0.74)),
             (opal_c[0] + int(opal_r * 0.66), opal_c[1] + int(opal_r * 0.74)),
             (opal_c[0], opal_c[1] + int(opal_r * 2.95))]
    pygame.draw.polygon(surf, (12, 10, 18), wedge)
    # a horizontal ink shelf UNDER the gem tying the two flanking notches to the
    # central wedge into one continuous dark trench beneath the cradle — so the
    # whole base of the four-hand cup reads as one shadow band the downscale keeps.
    pygame.draw.ellipse(surf, (12, 10, 18),
                        (opal_c[0] - int(opal_r * 1.7), opal_c[1] + int(opal_r * 1.15),
                         int(opal_r * 3.4), int(opal_r * 1.5)))
    opal_socket(surf, opal_c[0], opal_c[1], opal_r, s)
    # four lower arms reaching in from both sides to cradle the skull from below
    lower = [
        ((cx - int(26 * s), cy - int(14 * s)), (cx - int(24 * s), cy + int(4 * s)),
         (opal_c[0] - int(13 * s), opal_c[1] + int(8 * s))),
        ((cx - int(20 * s), cy - int(8 * s)),  (cx - int(16 * s), cy + int(10 * s)),
         (opal_c[0] - int(6 * s), opal_c[1] + int(15 * s))),
        ((cx + int(26 * s), cy - int(14 * s)), (cx + int(24 * s), cy + int(4 * s)),
         (opal_c[0] + int(13 * s), opal_c[1] + int(8 * s))),
        ((cx + int(20 * s), cy - int(8 * s)),  (cx + int(16 * s), cy + int(10 * s)),
         (opal_c[0] + int(6 * s), opal_c[1] + int(15 * s))),
    ]
    for (sho, elb, hand) in lower:
        bone_limb(surf, sho, elb, hand, max(4, int(5 * s)), s)
    # cupping fingers under the skull
    for (sho, elb, hand) in lower:
        sgn = 1 if hand[0] >= opal_c[0] else -1
        tip = (opal_c[0] + sgn * int(2 * s), opal_c[1] + int(opal_r * 1.12))
        finger = [(hand[0], hand[1] - int(3 * s)),
                  (hand[0] + sgn * int(3 * s), hand[1]),
                  (tip[0], tip[1]),
                  (tip[0] - sgn * int(3 * s), tip[1] - int(4 * s))]
        # fat ink keyline + a cool rim-light edge so each cupping finger detaches
        # from the dark trench and reads as a distinct curled hand under the gem
        triad_blob(surf, NACRE, finger, ow=max(2, int(1.8 * s)))
        pygame.draw.line(surf, RIMLIGHT, finger[0], finger[3], max(1, int(1.3 * s)))

    # the opal skull LAST so it owns the foreground + the brightest focal
    opal_skull(surf, opal_c[0], opal_c[1], opal_r, s)

    # === SKULL HEAD (the demoted FACE-DISC) ==================================
    # WHY the face-disc is pinned to a FIXED MID-NACRE shade (lum ~168) and NOT
    # near-white: a glowing white disc the size of the body always out-masses a
    # 2-3px gem at 32px, so the two near-white focals competed by design (the
    # round-5 RE-ROLL). Sitting the head at a fixed mid grey-lilac value — a clear
    # step below the pale body and far below the luminous teal gem — turns the
    # disc into quiet body, not a focal. Only the gem now sits at the top of the
    # value scale, so the cupped opal owns the brightest read outright.
    triad_circle(surf, MID_NACRE, head_c, hr,
                 ow=max(2, int(2 * s)), sheen=False)
    # a gentle COOL rim-light (NOT near-white) along the lower/right contour so the
    # mid-nacre dome still detaches from a light day sky without re-lifting toward
    # white — the rim is a contour tell, not a bright mass.
    pygame.draw.arc(surf, lerp(RIMLIGHT, MID_NACRE, 0.25),
                    (head_c[0] - hr, head_c[1] - hr, hr * 2, hr * 2),
                    math.radians(300), math.radians(110), max(2, int(1.8 * s)))
    # WHY cheek + socket-rim shades sit between the mid-nacre disc and ink: the
    # disc is now mid-value, so features must read against it without re-lifting
    # the whole head — a single mid-to-ink step keeps the face legible while the
    # disc stays a quiet mass.
    CHEEK_SH = lerp(MID_NACRE, INK, 0.42)
    for sgn in (-1, 1):
        pygame.draw.circle(surf, CHEEK_SH,
                           (head_c[0] + sgn * int(hr * 0.64), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] + int(hr * 0.06)
        pygame.draw.circle(surf, lerp(MID_NACRE, INK, 0.3), (ex, ey), int(hr * 0.34))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.28))
        # a tiny teal iridescent pin in each socket (the queen's cool eye-glint)
        pygame.draw.circle(surf, FLECK_TEAL, (ex, ey + int(1 * s)), max(1, int(hr * 0.10)))
    # nose
    pygame.draw.polygon(surf, CHEEK_SH,
                        [(head_c[0] - int(hr * 0.12), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.12), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.54))])
    # mouth
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.40), my),
                     (head_c[0] + int(hr * 0.40), my + int(hr * 0.04)),
                     max(1, int(2 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, INK,
                         (head_c[0] + int(k * hr * 0.17), my - int(hr * 0.06)),
                         (head_c[0] + int(k * hr * 0.17), my + int(hr * 0.10)),
                         max(1, int(1 * s)))
    # a single central pearl set on the brow (framed by the crown skulls)
    pygame.draw.circle(surf, INK, (head_c[0], head_c[1] - int(hr * 0.92)),
                       max(2, int(hr * 0.26)))
    pygame.draw.circle(surf, lerp(PEARL, NACRE_D, 0.18),
                       (head_c[0], head_c[1] - int(hr * 0.92)),
                       max(2, int(hr * 0.22)))
    # WHY the brow-pearl highlight is a COOL low-chroma pip held SMALL: the pearl
    # may rank near the top on luminance, but it is near-grey (sat ~12), so it can
    # never tie the saturated teal gem core (sat ~135) on the most-saturated test
    # that decides the focal — and it is a single sub-pixel point at 32px, so it
    # cannot out-mass the gem either.
    pygame.draw.circle(surf, lerp(PEARL, NACRE_SH, 0.4),
                       (head_c[0] - int(hr * 0.06), head_c[1] - int(hr * 0.98)),
                       max(1, int(hr * 0.09)))

    # === SKULL-CROWN — paired flanking nacre skulls on shell-horns ============
    # WHY shell-horns sweeping outward with a small skull at each tip: this is
    # the above-head royal tell and the lineage signature; kept SMALL + pale so
    # the cupped opal skull stays the brightest read.
    shell_horn(surf, head_c[0] - int(hr * 0.5), head_c[1] - int(hr * 0.2), int(hr * 1.1), -1, s)
    shell_horn(surf, head_c[0] + int(hr * 0.5), head_c[1] - int(hr * 0.2), int(hr * 1.1), 1, s)


# -- the pillar: a stacked nacre-tier column (the queen's own forms) ----------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """A repeatable column of stacked nacre rings (the tier-stack tiled) with a
    crown-skull + central pearl gap-cap. Mirrors top<->bottom on-axis."""
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    pitch = int(26 * s)
    cap_room = int(40 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    while y <= b1:
        nacre_tier(surf, cx, y, int(30 * s), int(20 * s), s, flecks=False)
        # a thin teal rim line cinching each ring (shell layering tell)
        pygame.draw.arc(surf, FLECK_TEAL,
                        (cx - int(15 * s), y - int(8 * s), int(30 * s), int(16 * s)),
                        math.radians(202), math.radians(338), max(1, int(1.2 * s)))
        # two small fleck chips per ring (fixed)
        pygame.draw.circle(surf, FLECK_PINK, (cx - int(8 * s), y - int(2 * s)), max(1, int(1.4 * s)))
        pygame.draw.circle(surf, FLECK_GOLD, (cx + int(8 * s), y + int(2 * s)), max(1, int(1.4 * s)))
        y += pitch

    # gap-cap: a crown-skull cradling a small pearl, the creature-derived edge
    cap_y = (bot - int(24 * s)) if cap == "bottom" else (top + int(24 * s))
    fan_dir = -1 if cap == "bottom" else 1
    # a widening final tier toward the gap (the inverted-pagoda lip)
    nacre_tier(surf, cx, cap_y, int(40 * s), int(22 * s), s, flecks=True)
    skull_y = cap_y + fan_dir * int(16 * s)
    small_crown_skull(surf, cx, skull_y, int(9 * s), s)
    # a small bright opal pearl set in the cap mouth (the focal echo)
    pearl_y = skull_y + fan_dir * int(11 * s)
    pygame.draw.circle(surf, INK, (cx, pearl_y), max(2, int(5 * s)))
    pygame.draw.circle(surf, OPAL, (cx, pearl_y), max(2, int(4 * s)))
    pygame.draw.circle(surf, OPAL_HOT, (cx - int(1 * s), pearl_y - int(1 * s)),
                       max(1, int(2 * s)))


# -- compose the review sheet -------------------------------------------------
SS = 6


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_queen(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


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
    sheet.blit(font_big.render("OPAL PEARL-DIVER QUEEN", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "royal skull-KING (Skull Kings II)  ·  FLOATING nacre tier-stack (rings WIDEN downward, no feet) · paired shell-horn crown-skulls + brow pearl · "
        "FIXED 3-fleck iridescence · 4 hands CUP the SOLE-luminous TEAL OPAL SKULL focal (face-disc demoted to mid-nacre) · round 6",
        True, LABEL_DIM), (360, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 220, 1.55)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("KIND: a buoyant inverted-nacre-pagoda — scalloped shell-rings widen DOWNWARD,", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("no feet, soft rounded base. SIX arms: upper two hold conch + pearl-strand;", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("four lower hands CUP the luminous OPAL SKULL (the single brightest focal).", True, LABEL_DIM), (14, 622))

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
    sheet.blit(font.render("Pillar — nacre tier-column", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked shell-rings (the body tiled); each cinched", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("with a teal rim + fixed flecks; crown-skull + bright", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("opal-pearl gap-cap (mirrored top<->bottom, on-axis)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night sky + SILHOUETTE proof =============
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_queen(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        # WHY a cool RIM on the night chip: the pale nacre body actually reads
        # well on the dark night sky already; a thin teal rim just re-asserts the
        # silhouette edge without adding a competing bright mass, so the opal
        # skull stays the unambiguous brightest point on both backdrops.
        if night:
            base = grow_outline(small, lerp(FLECK_TEAL, INK, 0.4) + (255,), 2)
            return grow_outline(base, INK + (200,), 1)
        # WHY a 2px ink ring on the DAY chip too: the headline round-1 blocker was
        # pale-on-pale — a hard dark perimeter is what stops the pale tiers + crown
        # washing into a light-blue sky, so the day chip earns the same fat ring.
        return grow_outline(small, INK + (255,), 2)

    day_chip = chip32(night=False)
    night_chip = chip32(night=True)

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(day_chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky (ink keyline + cool rim-light)", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(night_chip, (panel_x + 20 + 27 - 1, night_y + 27 - 1))
    sheet.blit(font_sm.render("32px on night sky (teal rim)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # silhouette proof — blacked-out hero so the tier-stack read is checked
    def silhouette():
        big = pygame.Surface((150 * SS, 210 * SS), pygame.SRCALPHA)
        draw_queen(big, 75 * SS, 100 * SS, 1.20 * SS)
        small = pygame.transform.smoothscale(big, (150, 210))
        mask = pygame.mask.from_surface(small)
        sil = pygame.Surface((150, 210), pygame.SRCALPHA)
        solid = mask.to_surface(setcolor=(18, 18, 20, 255), unsetcolor=(0, 0, 0, 0))
        sil.blit(solid, (0, 0))
        return sil

    sil_x = panel_x + 196
    pygame.draw.rect(sheet, (210, 212, 216), (sil_x, day_y, 150, 210))
    pygame.draw.rect(sheet, INK, (sil_x, day_y, 150, 210), 1)
    sheet.blit(silhouette(), (sil_x, day_y))
    sheet.blit(font_sm.render("silhouette proof", True, LABEL_DIM), (sil_x, day_y + 214))
    sheet.blit(font_sm.render("(floating downward-wide stack)", True, LABEL_DIM), (sil_x, day_y + 230))

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
        (NACRE, "pale nacre body"), (MID_NACRE, "face-disc (mid-nacre)"),
        (OPAL, "opal skull (teal)"), (OPAL_HOT, "opal hot core (teal)"),
        (FLECK_PINK, "fleck pink"), (FLECK_TEAL, "fleck teal"),
        (FLECK_GOLD, "fleck gold"), (PEARL, "pearl / strand"),
        (CONCH, "conch shell"), (INK, "ink keyline"),
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
        "FLOATING tier-stack KIND: rings WIDEN downward (inverted nacre pagoda), no feet, symmetric + buoyant.  ONE pale mass + thin accents; "
        "FIXED (non-animated) 3-fleck shimmer; cupped OPAL SKULL = single brightest pixel; crown-skulls kept small.  SS=6 supersample -> smoothscale · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_6.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    self_check()


def _peaks_in(surf):
    """Scan opaque pixels; return the brightest and the most-saturated, each as
    ((x,y), rgb, lum, sat). Saturation is the simple max-min chroma spread, the
    same quantity the critique's pixel analysis used to flag the white blob."""
    px = pygame.surfarray.pixels3d(surf)
    a = pygame.surfarray.pixels_alpha(surf)
    w, h = surf.get_size()
    best_lum, lum_xy, lum_rgb = -1.0, (0, 0), (0, 0, 0)
    best_sat, sat_xy, sat_rgb, sat_lum = -1, (0, 0), (0, 0, 0), 0.0
    for x in range(w):
        for yy in range(h):
            if a[x, yy] < 40:
                continue
            r, g, b = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            sat = max(r, g, b) - min(r, g, b)
            if lum > best_lum:
                best_lum, lum_xy, lum_rgb = lum, (x, yy), (r, g, b)
            # only count a pixel as the saturation peak if it is genuinely bright
            # (lum > 150) — a dark saturated edge pixel must not win the focal test
            if lum > 150 and sat > best_sat:
                best_sat, sat_xy, sat_rgb, sat_lum = sat, (x, yy), (r, g, b), lum
    del px, a
    return (lum_xy, lum_rgb, best_lum), (sat_xy, sat_rgb, best_sat, sat_lum)


def self_check():
    """Verify the GATE at TRUE 32px on BOTH backdrops: the brightest AND the
    most-saturated bright opaque pixel of the creature chip must both sit inside
    the cupped opal skull (a warm-saturated, low-centre point), proving the gem
    beats the now-dimmed face-disc on DAY and the teal rim on NIGHT. The creature
    pixels are identical on day + night (only the rim-outline tint differs), so
    one chip scan settles both backdrops; the rim is excluded by the lum>150 gate
    on the saturation peak."""
    big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
    draw_queen(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
    chip = pygame.transform.smoothscale(big, (96, 96))
    (lxy, lrgb, llum), (sxy, srgb, ssat, slum) = _peaks_in(chip)

    # the opal cradle sits below the head centre; a peak in the lower-centre band
    # = the gem won. The head dome sits well above this band.
    def in_gem(xy):
        return (28 <= xy[0] <= 68) and (46 <= xy[1] <= 78)

    bright_in_gem = in_gem(lxy)
    sat_in_gem = in_gem(sxy)
    sr, sg, sb = srgb
    teal = (sg >= sr) and (sg >= sb)  # the gem core is luminous teal: G dominant
    print("self-check 32px chip:")
    print("  brightest      @ (%d,%d) rgb %s lum %.0f  -> in gem band? %s"
          % (lxy[0], lxy[1], lrgb, llum, bright_in_gem))
    print("  most-saturated @ (%d,%d) rgb %s sat %d lum %.0f  -> in gem band? %s teal? %s"
          % (sxy[0], sxy[1], srgb, ssat, slum, sat_in_gem, teal))
    print("  GATE: opal wins BOTH brightest+most-saturated at 32px? ->",
          (bright_in_gem and sat_in_gem))

    # hero-scale peaks, as a coarse confirmation
    hero = pygame.Surface((420, 520), pygame.SRCALPHA)
    draw_queen(hero, 210, 250, 1.7)
    (hlxy, hlrgb, hllum), (hsxy, hsrgb, hssat, hslum) = _peaks_in(hero)
    print("self-check hero: brightest @ %s rgb %s lum %.0f ; most-sat @ %s rgb %s sat %d"
          % (hlxy, hlrgb, hllum, hsxy, hsrgb, hssat))


if __name__ == "__main__":
    main()
