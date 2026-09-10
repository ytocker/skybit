"""
Round-1 concept renderer for the OXBLOOD AUTOMATON KING — a royal skull-KING of
the Skull-Kings-II brood, rendered as a RIGID BLOCKY HUMANOID MACHINE. Headless
Pygame; ELEVATED pipeline (SS=6 supersample -> smoothscale) so the riveted plate
detail survives the downscale. Clones the sibling regent's house grammar wholesale:
flat triad fill (dark-core -> flat -> top-left sheen), a hard 1-2px ink keyline
(28,22,30), 1px alpha-grown outline, chibi proportions, scary-CUTE. Procedural-
only (no gradients/PNGs).

WHY this reads as a MACHINE, not a bone-lord: the whole figure is boxed —
riveted rectangular copper plates, a square torso, square pauldrons, PEG LEGS,
and CIRCULAR gear-rings at every joint. Two stiff geometric arms with gear-elbows;
no cradle. The de-collider from the sibling Bismuth Prism-Architect (a LIMBLESS
stepped-crystal mass) is the HUMANOID lock: peg legs + square pauldrons + visible
limbs + at least one prominent CIRCULAR gear-ring, so the two never twin.

WHY the heat stays WARM copper: the body is patinated copper-bronze (the dominant
mass); oxblood-lacquer panels are thin rectangular inlays; verdigris is kept to a
FEW thin ticks so the figure never cools toward green (it must NOT twin Malachite).
The single brightest pixel is the BRASS GEAR-EYE — a glowing toothed iris socket —
which owns the focal. Above the head: a brass skull finial on a clockwork
gear-spindle spire (the royal skull-crown tell).

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

# -- PINNED PALETTE (locked brief) --------------------------------------------
# Patinated copper-bronze is the DOMINANT warm mass; everything else is thin.
COPPER     = (178, 120,  78)   # patinated copper-bronze body (dominant fill)
COPPER_D   = (128,  82,  50)   # copper dark-core / recessed plate
COPPER_DD  = ( 92,  58,  36)   # deepest copper hollow (seams, joint gaps)
COPPER_SH  = (224, 168, 116)   # copper top-left rim-sheen
# oxblood-lacquer panel inlays — thin rectangular accents only
OXBLOOD    = (116,  36,  40)
OXBLOOD_BR = (158,  60,  58)
OXBLOOD_D  = ( 78,  24,  28)
# the SINGLE warm focal — the brass gear-eye iris (must stay brightest pixel).
BRASS      = (232, 196, 108)
BRASS_BR   = (252, 230, 168)   # hottest brass core (the brightest pixel)
BRASS_D    = (176, 142,  62)
# verdigris — kept MINIMAL (a few thin oxidation ticks) so body stays warm.
VERD       = (120, 168, 150)
VERD_D     = ( 84, 124, 110)
# dark structural iron (rivets, deep frame shadow)
IRON       = ( 58,  54,  56)
IRON_D     = ( 36,  34,  36)
# round 5: a COOLED copper used for shoulder + upper-arm EDGES so the mid-body
# stops reading as a warm mass at 32px — desaturated toward iron/grey-brown so
# r no longer dominates g,b. The crown brass is then the ONLY warm focal.
COPPER_COOL = (108,  96,  86)   # neutral grey-brown plate (body-center de-warm)
# round 6: a DAY-ONLY cool iron/brass-SHADE used for the MAIN TORSO BLOCK + peg
# legs + head plate on the day palette. WHY: the day squint still landed on the
# warm copper torso/neck (body warm-area 580 vs crown 244 in r5) because only the
# pauldrons/arms had been cooled — the big central torso plate, the legs and the
# head plate were still warm COPPER and formed the hottest warm pixel at the neck.
# Pushed to a cold blue-grey iron with b just over r so it CANNOT register as warm
# (r>g and r>b) under the squint test; the crown brass then owns every warm pixel.
DAY_TORSO  = ( 86,  88,  96)    # cold iron/brass-shade structure (day torso/legs/head)
DAY_TORSO_D= ( 56,  58,  66)    # its dark-core / recessed plate
INK        = ( 28,  22,  30)   # hard ink keyline

# round 6: a module-level DAY-cool switch. WHY a flag rather than new signatures
# on every helper: the torso/leg/head share one drawing path with night+hero, and
# only the DAY chip must cool. When set, the body-copper resolver below swaps the
# main copper mass to the cold DAY_TORSO iron so the day squint has no warm body —
# night/hero stay untouched (warm copper) so the already-passing night holds.
_DAY_COOL = False


def body_copper():
    """The fill used for the main torso/leg/head copper mass — cold iron on the
    day chip, warm patinated copper everywhere else (night, hero, silhouette)."""
    return DAY_TORSO if _DAY_COOL else COPPER


BG         = ( 96, 100, 108)   # neutral grey review backdrop
PANEL      = ( 74,  78,  88)
DAY_SKY_T  = (120, 196, 236)
DAY_SKY_B  = (196, 232, 244)
NIGHT_T    = ( 22,  26,  54)
NIGHT_B    = ( 48,  44,  82)
LABEL      = (238, 240, 244)
LABEL_DIM  = (188, 196, 208)


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
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline."""
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


def rivet_plate(surf, x, y, w, h, color, s, rivets=True, inlay=False):
    """A riveted rectangular copper plate — the machine's building block. WHY a
    boxed rect with corner rivet pips: the blocky-humanoid silhouette is built
    from stacked plates, and the rivet dots read as 'worked metal' at hero scale
    while dissolving cleanly at 32px. `inlay` swaps the fill to oxblood lacquer."""
    fill = OXBLOOD if inlay else color
    core = OXBLOOD_D if inlay else lerp(color, INK, 0.40)
    sh = OXBLOOD_BR if inlay else lerp(color, (255, 255, 255), 0.40)
    rect = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    triad_blob(surf, fill, rect,
               core_pts=[(x + w * 0.40, y + h * 0.42), (x + w, y + h * 0.30),
                         (x + w, y + h), (x + w * 0.40, y + h)],
               sheen_pts=[(x, y), (x + w * 0.55, y), (x + w * 0.30, y + h * 0.40),
                          (x, y + h * 0.50)],
               ow=max(1, int(1.3 * s)))
    if rivets:
        rr = max(1, int(1.6 * s))
        for rx in (x + w * 0.13, x + w * 0.87):
            for ry in (y + h * 0.16, y + h * 0.84):
                pygame.draw.circle(surf, IRON_D, (int(rx), int(ry)), rr + max(1, int(0.6 * s)))
                pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.25),
                                   (int(rx - rr * 0.3), int(ry - rr * 0.3)), rr)


def gear_ring(surf, cx, cy, r, s, teeth=10, color=COPPER, hub=True):
    """A prominent CIRCULAR toothed gear-ring — the de-collider from the sibling
    Bismuth's angular facets. WHY drawn as a notched disc with a dark hub: the
    round teeth read unmistakably as a cog at hero scale, and the circular
    silhouette stays legible (a clean dark ring) at 32px against any sky."""
    # toothed outer rim built as a star-ish polygon (alternating r / r*1.18)
    pts = []
    n = teeth * 2
    for k in range(n):
        a = math.radians(k * (360.0 / n))
        rr = r * (1.20 if k % 2 == 0 else 0.98)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, lerp(color, INK, 0.30), pts)
    # flat disc face
    triad_circle(surf, color, (cx, cy), int(r * 0.92), ow=max(1, int(1.3 * s)),
                 core=False)
    if hub:
        # dark recessed hub with a bolt pip. round 5: the bolt pip is BRASS only on
        # the WARM-key gears (waist/hip), but COLD iron on body gears tinted with
        # COPPER_COOL — so no stray warm dot leaks into the de-warmed mid-body and
        # competes with the crown on the squint.
        cool_hub = (color == COPPER_COOL)
        pygame.draw.circle(surf, IRON_D if cool_hub else COPPER_DD,
                           (cx, cy), max(2, int(r * 0.36)))
        pygame.draw.circle(surf, INK, (cx, cy), max(2, int(r * 0.36)), max(1, int(1.0 * s)))
        pip = IRON if cool_hub else BRASS
        pip_hi = lerp(IRON, (255, 255, 255), 0.2) if cool_hub else BRASS_BR
        pygame.draw.circle(surf, pip, (cx, cy), max(1, int(r * 0.18)))
        pygame.draw.circle(surf, pip_hi,
                           (cx - int(r * 0.07), cy - int(r * 0.08)), max(1, int(r * 0.09)))


def verd_ticks(surf, x, y, w, s, n=3):
    """A FEW verdigris PATINA ticks crusting ONE recessed seam. WHY chunkier +
    consolidated (round 3): the round-2 ticks were near-phantom, so verdigris now
    reads as 2-3 ACTUALLY-VISIBLE oxidation dabs grounded in a single dark seam —
    a short VERD_D base swab capped by a brighter VERD bloom — enough to register
    as patina without cooling the copper toward green (which would twin Malachite).
    Each dab is a small filled patch, not a hairline, so it survives at hero scale."""
    seam_dark = lerp(COPPER_DD, INK, 0.3)
    pygame.draw.line(surf, seam_dark, (int(x), int(y)), (int(x + w), int(y)),
                     max(1, int(1.2 * s)))
    for k in range(n):
        tx = int(x + (k + 0.5) * (w / n))
        ty = int(y)
        ww = max(2, int(2.4 * s))
        hh = max(2, int(3.4 * s))
        pygame.draw.ellipse(surf, VERD_D, (tx - ww, ty - hh // 2, ww * 2, hh))
        pygame.draw.ellipse(surf, VERD,
                            (tx - ww + max(1, int(0.5 * s)), ty - hh // 2,
                             max(2, int(ww * 1.2)), max(2, hh // 2)))


def peg_leg(surf, hip, s, sgn):
    """A stiff square-shouldered PEG LEG — a boxed thigh plate tapering to a
    tapered peg foot, with a gear-ring at the hip. WHY a peg (not a bone limb):
    pegs lock the silhouette as a rigid machine and read clean against the sky."""
    hx, hy = hip
    bc = body_copper()                       # round 6: cold iron on day, copper else
    thigh_w = int(13 * s)
    thigh_h = int(26 * s)
    rivet_plate(surf, hx - thigh_w // 2, hy, thigh_w, thigh_h, bc, s)
    # tapered peg shank below the thigh plate
    peg_top = hy + thigh_h
    peg = [(hx - int(6 * s), peg_top), (hx + int(6 * s), peg_top),
           (hx + int(4 * s), peg_top + int(22 * s)),
           (hx - int(4 * s), peg_top + int(22 * s))]
    triad_blob(surf, bc, peg,
               sheen_pts=[(hx - int(6 * s), peg_top), (hx - int(2 * s), peg_top),
                          (hx - int(2 * s), peg_top + int(22 * s)),
                          (hx - int(4 * s), peg_top + int(22 * s))],
               ow=max(1, int(1.2 * s)))
    # blocky foot pad
    foot = [(hx - int(9 * s), peg_top + int(22 * s)),
            (hx + int(10 * s), peg_top + int(22 * s)),
            (hx + int(10 * s), peg_top + int(30 * s)),
            (hx - int(9 * s), peg_top + int(30 * s))]
    triad_blob(surf, lerp(bc, INK, 0.30) if _DAY_COOL else COPPER_D, foot,
               ow=max(1, int(1.2 * s)))
    # gear-ring at the hip (joint tell) — cooled on day so the leg adds no warmth
    gear_ring(surf, hx, hy, int(7 * s), s, teeth=8,
              color=COPPER_COOL if _DAY_COOL else COPPER)


# -- the brass skull finial on a clockwork gear-spindle spire (royal crown) ----
def skull_spire(surf, cx, base_y, r, s, night_rim=False):
    """A CHUNKY brass SKULL on a clockwork gear-spindle spire rising from the head
    — the royal skull-KING crown tell, and the thematic identity. WHY rebuilt big
    + blocky for round 2: at 32px a small round finial collapsed to 2-3 dots, so
    the skull (the whole point of a Skull King) was lost. The cranium is now a
    chunky brass BLOCK with two dark socket pixels and a dark jaw notch so it reads
    as a SKULL SHAPE — not a bead — through the downscale, sitting as the brightest
    warm value above the head. The spire is ONE bold 3-4px vertical stroke with a
    SINGLE gear-ring node mid-shaft, so head→spindle→skull are three separable
    tiers that survive in motion. `night_rim` adds a faint brass rim-light on the
    skull+spire only, so the crown carries against a dim night sky."""
    # the bold spindle column rising from the crown — one clear vertical stroke
    spindle_h = int(r * 2.2)
    sw = max(2, int(3.4 * s) // 2)          # half-width: a fat 3-4px stroke at 32px
    spire_top = base_y - spindle_h
    spire_rect = [(cx - sw, base_y), (cx + sw, base_y),
                  (cx + sw, spire_top), (cx - sw, spire_top)]
    if night_rim:
        # faint warm rim on the spire stroke so it carries on dark night sky
        pygame.draw.polygon(surf, BRASS_D,
                            [(cx - sw - max(1, int(0.9 * s)), base_y),
                             (cx + sw + max(1, int(0.9 * s)), base_y),
                             (cx + sw + max(1, int(0.9 * s)), spire_top),
                             (cx - sw - max(1, int(0.9 * s)), spire_top)])
    triad_blob(surf, BRASS, spire_rect,
               sheen_pts=[(cx - sw, base_y), (cx, base_y),
                          (cx, spire_top), (cx - sw, spire_top)],
               ow=max(1, int(1.0 * s)))
    # ONE gear-ring node at mid-shaft (the clockwork tell, kept legible)
    node_y = base_y - int(spindle_h * 0.46)
    gear_ring(surf, cx, node_y, int(r * 0.52), s, teeth=7, color=BRASS, hub=False)

    # === the CHUNKY brass skull cranium block ================================
    # WHY a CLEAN 2-TONE skull (round 3): at 32px the cranium is only ~3px tall,
    # so interior shading muddies it. The skull now reads as a bright-brass DOME
    # punched by INK sockets + an INK jaw notch — a high-contrast brass/ink pair
    # that survives the downscale as a SKULL SHAPE, not a bead. It is filled
    # BRASS_BR (the hottest warm value in the whole figure) so it WINS the
    # brightest-warm tie against the now-dimmed torso eye + chest bolt.
    # round 4: the cranium is grown ~10% and the dome is squarer-shouldered so it
    # carries MORE warm mass than the (now iron) chest at 32px — the squint must
    # land here first, and warm AREA (not just peak brightness) is what wins a
    # squint tie. A jaw step is cut INTO the silhouette so the bottom edge is
    # asymmetric (stops it reading as a coin/orb through the downscale).
    skw = int(r * 1.72)                     # broad block grown for more warm mass
    skh = int(r * 1.44)
    skx = cx - skw // 2
    sky_top = spire_top - skh
    jaw_w = int(skw * 0.50)                  # the narrower jaw the dome steps down to
    jaw_top = sky_top + int(skh * 0.70)
    jaw_bot = sky_top + int(skh * 1.00)
    # ONE closed cranium-plus-jaw outline: wide dome shoulders -> a hard STEP IN at
    # the jaw line -> a narrower jaw block. The inward step on both sides is the
    # asymmetric bottom that survives smoothscale as a skull, not a bead.
    cranium = [(skx, sky_top + int(skh * 0.22)),
               (skx + int(skw * 0.20), sky_top),
               (skx + skw - int(skw * 0.20), sky_top),
               (skx + skw, sky_top + int(skh * 0.22)),
               (skx + skw, sky_top + int(skh * 0.56)),
               (skx + skw - int(skw * 0.10), sky_top + int(skh * 0.66)),
               (cx + jaw_w // 2, jaw_top),                # right step-in
               (cx + jaw_w // 2, jaw_bot),                # right jaw corner
               (cx - jaw_w // 2, jaw_bot),                # left jaw corner
               (cx - jaw_w // 2, jaw_top),                # left step-in
               (skx + int(skw * 0.10), sky_top + int(skh * 0.66)),
               (skx, sky_top + int(skh * 0.56))]
    if night_rim:
        # tight warm halo on the cranium so the skull stays the night focal even
        # once it is the brightest value (re-proven on the night chip in round 3)
        rim = grow_outline(_blob_surface(surf.get_size(), BRASS_BR, cranium),
                           BRASS_BR + (255,), max(2, int(1.6 * s)))
        surf.blit(rim, (0, 0))
    else:
        # round 6: a DARK INK keyline HALO around the whole crown-skull, grown
        # FIRST so it sits as an outer ring beneath the brass. WHY: night gets a
        # warm rim that tips the first-read for free, but brass-on-pale-blue is
        # low-contrast, so on day the crown lost the squint. A cool/ink rim is the
        # day opposite of night's warm rim — it pops the bright brass skull against
        # the pale-blue sky without enlarging the crown (the rim is dark, not brass,
        # so it adds NO warm area; it only sharpens the crown's edge against light).
        # WHY a FAT dark ring (not a hairline): the crown is ~3px at 32px on a BRIGHT
        # pale-blue sky, so a thin rim blurs straight into the sky and the brass loses
        # its red-dominance (the round-6 first attempt). A ~1px-at-32px dark moat —
        # several px on this SS=6 super-canvas — means the squint averages brass
        # against INK (dark), not against bright sky, so the crown stays warm-dominant
        # and pops. It is dark, so it adds zero warm area; it only frames the crown.
        ink_rim = grow_outline(_blob_surface(surf.get_size(), INK, cranium),
                               INK + (255,), max(3, int(3.6 * s)))
        surf.blit(ink_rim, (0, 0))
        # round 5: the DAY halo is TUCKED to the DOME ONLY. WHY: a uniform bloom
        # (round 4) padded warm pixels below the jaw line too, so at 32px it filled
        # the jaw-notch and merged the sockets — the day skull collapsed to a bead.
        # Now the halo is grown from a dome-only blob clipped ABOVE the jaw-step, so
        # the bright pad lands on the cranium (keeping it the warm focal) while the
        # jaw bottom edge stays dark — the notch survives the downscale.
        dome_only = [(skx, sky_top + int(skh * 0.22)),
                     (skx + int(skw * 0.20), sky_top),
                     (skx + skw - int(skw * 0.20), sky_top),
                     (skx + skw, sky_top + int(skh * 0.22)),
                     (skx + skw, sky_top + int(skh * 0.56)),
                     (skx, sky_top + int(skh * 0.56))]
        # round 6: the day dome-halo is grown a touch fatter (1.2 -> 1.7) so the
        # bright-brass pad rides just INSIDE the new ink rim. WHY: the dome is only
        # ~3px at 32px and the ink rim + sockets erode it under smoothscale, so the
        # surviving warm pixels were dropping to a near-neutral 165; the fatter brass
        # pad keeps the crown a SATURATED warm focal that pops out of the dark rim.
        rim = grow_outline(_blob_surface(surf.get_size(), BRASS_BR, dome_only),
                           BRASS_BR + (255,), max(1, int(1.7 * s)))
        surf.blit(rim, (0, 0))
    # the skull is the BRIGHTEST warm value — fill the cranium hot brass FLAT
    # (no dark interior core; only a faint top-left sheen) so the 2-tone holds.
    pygame.draw.polygon(surf, INK, cranium)
    pygame.draw.polygon(surf, BRASS_BR, cranium)
    pygame.draw.polygon(surf, lerp(BRASS_BR, (255, 255, 255), 0.35),
                        [(skx + int(skw * 0.14), sky_top + int(skh * 0.10)),
                         (skx + int(skw * 0.46), sky_top + int(skh * 0.04)),
                         (skx + int(skw * 0.30), sky_top + int(skh * 0.34)),
                         (skx + int(skw * 0.12), sky_top + int(skh * 0.30))])
    # one extra HOT brass pixel-cluster at the dome crest so the crown's single
    # brightest pixel beats anything below it with margin — kept BRASS-toned (not
    # white) so the brightest pixel stays the brass hot-core the brief pins.
    pygame.draw.circle(surf, lerp(BRASS_BR, (255, 255, 220), 0.4),
                       (cx - int(skw * 0.06), sky_top + int(skh * 0.16)),
                       max(1, int(skw * 0.12)))
    pygame.draw.polygon(surf, INK, cranium, max(1, int(1.2 * s)))
    # two INK socket holes. round 5: grown slightly + pushed a touch wider so that,
    # with the dome-only halo no longer flooding the gap, ONE dark pixel of socket
    # SEPARATION survives the DAY downscale (the sockets stopped merging). They sit
    # below the bright halo band so the dome above stays the warm focal.
    eye_r = max(2, int(skw * 0.155))
    ey = sky_top + int(skh * 0.40)
    for sg in (-1, 1):
        pygame.draw.circle(surf, INK, (cx + sg * int(skw * 0.33), ey), eye_r)
    # round 5: a DEEPER + WIDER ink jaw-notch biting UP into the lower edge. With the
    # halo tucked off the jaw, this dark bite now survives the DAY raster as a notch
    # on the bottom — the anti-coin / asymmetric-skull tell on day, matching night.
    jw = int(jaw_w * 0.58)
    jaw = [(cx - jw // 2, jaw_bot + 1), (cx + jw // 2, jaw_bot + 1),
           (cx + int(jw * 0.30), jaw_bot - int(skh * 0.22)),
           (cx - int(jw * 0.30), jaw_bot - int(skh * 0.22))]
    pygame.draw.polygon(surf, INK, jaw)


def _blob_surface(size, color, pts):
    """A throwaway surface holding just one filled polygon — used to build a
    tight rim-light halo around the skull cranium without rimming the whole sheet."""
    s2 = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.polygon(s2, color, pts)
    return s2


# -- the rigid blocky humanoid machine-king -----------------------------------
def draw_automaton(surf, cx, cy, s, night_rim=False):
    head_c = (cx, cy - int(34 * s))
    hr = int(20 * s)
    torso_y = cy - int(8 * s)

    # === PEG LEGS (behind torso) ============================================
    for sg in (-1, 1):
        peg_leg(surf, (cx + sg * int(15 * s), cy + int(26 * s)), s, sg)

    # === SQUARE BOXY TORSO ===================================================
    bc = body_copper()                       # round 6: cold iron on day, copper else
    tw = int(46 * s)
    th = int(40 * s)
    tx = cx - tw // 2
    rivet_plate(surf, tx, torso_y, tw, th, bc, s)
    # the central chest inlay — pushed to IRON-SHADE (round 4). WHY: on the day
    # 32px chip the warm oxblood chest mass was reading co-equal with the tiny
    # crown skull and stealing the squint by sheer area. A red lacquer panel is
    # inherently warm+saturated; no amount of darkening keeps it warm without
    # competing. So the chest now recedes as COOL DARK IRON STRUCTURE — a sunken
    # boiler hatch — leaving the crown skull the only bright-warm mass up top.
    cpx, cpy = cx - int(11 * s), torso_y + int(8 * s)
    cpw, cph = int(22 * s), int(22 * s)
    chest = [(cpx, cpy), (cpx + cpw, cpy), (cpx + cpw, cpy + cph), (cpx, cpy + cph)]
    triad_blob(surf, IRON, chest,
               core_pts=[(cpx + cpw * 0.32, cpy + cph * 0.34), (cpx + cpw, cpy + cph * 0.24),
                         (cpx + cpw, cpy + cph), (cpx + cpw * 0.32, cpy + cph)],
               ow=max(1, int(1.3 * s)))
    # a small boiler-bolt centred on the now-iron hatch — kept DIM IRON-D so the
    # chest carries NO warm spot at all (the crown owns every warm pixel up top).
    triad_circle(surf, IRON_D, (cx, torso_y + int(19 * s)), int(4 * s),
                 ow=max(1, int(1.0 * s)), core=False, sheen=False)
    # waist gear-ring (joint between torso and pelvis block) — cooled on day
    gear_ring(surf, cx, torso_y + th, int(8 * s), s, teeth=9,
              color=COPPER_COOL if _DAY_COOL else COPPER)
    # 3 verdigris PATINA ticks crusting ONE recessed lower-left seam (round 3):
    # consolidated into a single visible run (drawn AFTER the waist gear-ring so
    # the hub never overpaints them) — off-centre so it sits in the plate-edge
    # shadow and stays a seasoning that never twins Malachite's green mass.
    seam_y = torso_y + th - int(5 * s)
    verd_ticks(surf, tx + int(4 * s), seam_y, int(16 * s), s, n=3)

    # === SQUARE PAULDRONS + STIFF GEOMETRIC ARMS (gear-elbows) ===============
    arm_th = int(11 * s)
    # round 5: the shoulder pauldron + upper-arm + forearm + hand are recoloured
    # to COPPER_COOL (a neutral grey-brown) so the body's OUTER EDGES — the widest
    # warm band on the 32px chip — stop reading as warm. They're still riveted
    # plates with the same triad/sheen grammar (so the machine reads up close), but
    # their warm mass is killed so the crown is the lone warm focal on the squint.
    for sg in (-1, 1):
        # square pauldron plate capping the shoulder
        pw = int(16 * s)
        px = cx + sg * int(22 * s) - pw // 2
        py = torso_y - int(2 * s)
        rivet_plate(surf, px, py, pw, int(15 * s), COPPER_COOL, s)
        # shoulder gear-ring
        sh_c = (cx + sg * int(22 * s), torso_y + int(13 * s))
        # upper-arm boxed plate (straight down)
        ua_x = sh_c[0] - sg * 0 - arm_th // 2
        rivet_plate(surf, sh_c[0] - arm_th // 2, sh_c[1], arm_th, int(18 * s),
                    COPPER_COOL, s, rivets=False)
        # gear-elbow
        elbow = (sh_c[0], sh_c[1] + int(18 * s))
        gear_ring(surf, elbow[0], elbow[1], int(6 * s), s, teeth=8, color=COPPER_COOL)
        # forearm boxed plate angling inward to the hip (stiff, geometric)
        fa_top = elbow
        fa_bot = (cx + sg * int(14 * s), torso_y + th - int(2 * s))
        dx, dy = fa_bot[0] - fa_top[0], fa_bot[1] - fa_top[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * arm_th * 0.42, dx / L * arm_th * 0.42
        fa = [(fa_top[0] + nx, fa_top[1] + ny), (fa_bot[0] + nx, fa_bot[1] + ny),
              (fa_bot[0] - nx, fa_bot[1] - ny), (fa_top[0] - nx, fa_top[1] - ny)]
        triad_blob(surf, COPPER_COOL, fa,
                   sheen_pts=[(fa_top[0] + nx, fa_top[1] + ny),
                              (fa_bot[0] + nx, fa_bot[1] + ny),
                              (fa_bot[0] + nx * 0.3, fa_bot[1] + ny * 0.3),
                              (fa_top[0] + nx * 0.3, fa_top[1] + ny * 0.3)],
                   ow=max(1, int(1.2 * s)))
        # blocky three-finger claw hand
        hand = [(fa_bot[0] - sg * int(5 * s), fa_bot[1]),
                (fa_bot[0] + sg * int(6 * s), fa_bot[1]),
                (fa_bot[0] + sg * int(5 * s), fa_bot[1] + int(9 * s)),
                (fa_bot[0] - sg * int(4 * s), fa_bot[1] + int(9 * s))]
        triad_blob(surf, lerp(COPPER_COOL, INK, 0.25), hand, ow=max(1, int(1.1 * s)))
        # shoulder gear-ring drawn last so it caps the joint cleanly (cooled too)
        gear_ring(surf, sh_c[0], sh_c[1], int(7 * s), s, teeth=9, color=COPPER_COOL)

    # === SQUARE MACHINE SKULL HEAD ===========================================
    hw = int(40 * s)
    hx = head_c[0] - hw // 2
    hy = head_c[1] - int(18 * s)
    rivet_plate(surf, hx, hy, hw, int(36 * s), bc, s)
    # a thin oxblood brow band across the top of the face plate. round 6: on the
    # DAY path the brow is drawn in cold iron (not warm oxblood) — it sits directly
    # below the crown and a warm red brow here would re-seed a warm neck/upper-head
    # blob that competes with the crown on the squint. Night keeps the oxblood brow.
    if _DAY_COOL:
        rivet_plate(surf, hx + int(3 * s), hy + int(3 * s), hw - int(6 * s),
                    int(6 * s), DAY_TORSO_D, s, rivets=False)
    else:
        rivet_plate(surf, hx + int(3 * s), hy + int(3 * s), hw - int(6 * s),
                    int(6 * s), COPPER, s, rivets=False, inlay=True)
    # the torso/head gear-eye — demoted ALL THE WAY to cold iron structure
    # (round 5). WHY: through round 4 it still carried a small BRASS_D glint and a
    # copper-shade iris ring, which on the DAY 32px chip merged with the warm
    # shoulder/arm edges into a mid-body warm BLOB that stole the squint from the
    # crown. So the eye now has NO warm pixel at all: iron-shade iris ring, iron
    # pupil, and an IRON_D glint. It reads as a dark machine socket up close and
    # contributes ZERO warm mass to the body center — the crown owns every warm px.
    eye_c = (head_c[0], head_c[1] + int(4 * s))
    eye_r = int(7 * s)
    # dark recessed socket box (ink-rimmed, deep iron well — no copper warmth)
    pygame.draw.circle(surf, INK, eye_c, eye_r + max(1, int(1.6 * s)))
    pygame.draw.circle(surf, IRON_D, eye_c, eye_r)
    # toothed iris ring dropped to cold iron so it adds no warm pixel
    gear_ring(surf, eye_c[0], eye_c[1], int(eye_r * 0.72), s, teeth=10,
              color=IRON, hub=False)
    # iron pupil + a cold iron glint — no brass dot anywhere on the body
    pygame.draw.circle(surf, IRON, eye_c, int(eye_r * 0.44))
    pygame.draw.circle(surf, lerp(IRON, (255, 255, 255), 0.22),
                       (eye_c[0] - int(eye_r * 0.16), eye_c[1] - int(eye_r * 0.18)),
                       max(1, int(eye_r * 0.20)))
    # a small dark riveted jaw vent under the eye (mouth grille)
    grille_y = head_c[1] + int(15 * s)
    pygame.draw.rect(surf, IRON_D,
                     (head_c[0] - int(9 * s), grille_y, int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, INK,
                     (head_c[0] - int(9 * s), grille_y, int(18 * s), int(5 * s)),
                     max(1, int(1.0 * s)))
    for k in range(-2, 3):
        gx = head_c[0] + int(k * 4 * s)
        pygame.draw.line(surf, COPPER_DD, (gx, grille_y),
                         (gx, grille_y + int(5 * s)), max(1, int(1.0 * s)))
    # neck gear-ring between head and torso — cooled on day (this is exactly where
    # the round-5 hottest warm pixel sat, so it must carry no warmth on the squint)
    gear_ring(surf, head_c[0], hy + int(36 * s), int(6 * s), s, teeth=8,
              color=COPPER_COOL if _DAY_COOL else COPPER)

    # === ABOVE-HEAD royal CROWN — brass skull on clockwork gear-spire =========
    skull_spire(surf, head_c[0], hy + int(1 * s), int(13 * s), s, night_rim=night_rim)


# -- the boxed copper-column -> pillar mirror ---------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """A stacked riveted copper-plate column with periodic gear-ring lashings —
    a direct continuation of the king's torso plates + joint gears. WHY this
    tiles cleanly: each segment is a boxed plate pair cinched by a gear-ring, and
    the gap-cap fans into a small machine-head crowned by a brass gear-eye + a
    skull-spire stub (the creature-derived gap edge, mirrored top<->bottom)."""
    shaft_w = int(20 * s)
    pygame.draw.rect(surf, IRON_D, (cx - int(4 * s), top, int(8 * s), bot - top))

    pitch = int(30 * s)
    cap_room = int(46 * s)
    if cap == "bottom":
        b0, b1 = top + int(10 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(10 * s)
    y = b0
    while y <= b1:
        # a boxed copper plate segment
        rivet_plate(surf, cx - shaft_w // 2, int(y - pitch * 0.42),
                    shaft_w, int(pitch * 0.78), COPPER, s)
        # a thin oxblood inlay stripe down the centre of the plate
        rivet_plate(surf, cx - int(4 * s), int(y - pitch * 0.30),
                    int(8 * s), int(pitch * 0.54), COPPER, s, rivets=False, inlay=True)
        verd_ticks(surf, cx - shaft_w * 0.4, int(y + pitch * 0.30),
                   shaft_w * 0.8, s, n=3)
        # a gear-ring lashing cinching the segment joint
        gear_ring(surf, cx, int(y + pitch * 0.40), int(8 * s), s, teeth=9)
        y += pitch

    cap_y = (bot - int(30 * s)) if cap == "bottom" else (top + int(30 * s))
    fan_dir = -1 if cap == "bottom" else 1
    # the gap-cap machine-head block
    head_h = int(26 * s)
    hy = cap_y - (head_h if fan_dir < 0 else 0)
    rivet_plate(surf, cx - int(17 * s), hy, int(34 * s), head_h, COPPER, s)
    # a brass gear-eye on the cap (the creature focal echoed at the gap edge)
    # gap-cap eye demoted to match the king (round 3): copper-shade iris + a dim
    # BRASS_D pupil, so the cap SKULL-STUB stays the brightest warm value here too.
    eye_c = (cx, hy + head_h // 2)
    pygame.draw.circle(surf, INK, eye_c, int(8 * s))
    pygame.draw.circle(surf, COPPER_DD, eye_c, int(7 * s))
    gear_ring(surf, eye_c[0], eye_c[1], int(5 * s), s, teeth=9, color=COPPER_D, hub=False)
    pygame.draw.circle(surf, BRASS_D, eye_c, int(3 * s))
    # a small skull-spire stub pointing into the gap — echoes the king's crown:
    # one bold stroke + a chunky brass skull block with sockets + a jaw notch.
    spr_base = hy if fan_dir < 0 else hy + head_h
    sw = max(1, int(2.4 * s))
    sp = [(cx - sw, spr_base), (cx + sw, spr_base),
          (cx + sw, spr_base + fan_dir * int(11 * s)),
          (cx - sw, spr_base + fan_dir * int(11 * s))]
    triad_blob(surf, BRASS, sp, ow=max(1, int(1.0 * s)))
    sk_c_y = spr_base + fan_dir * int(16 * s)
    skw = int(11 * s)
    skh = int(9 * s)
    skull = [(cx - skw // 2, sk_c_y - skh // 2 + int(skh * 0.18)),
             (cx - int(skw * 0.32), sk_c_y - skh // 2),
             (cx + int(skw * 0.32), sk_c_y - skh // 2),
             (cx + skw // 2, sk_c_y - skh // 2 + int(skh * 0.18)),
             (cx + skw // 2, sk_c_y + int(skh * 0.10)),
             (cx + int(skw * 0.24), sk_c_y + skh // 2),
             (cx - int(skw * 0.24), sk_c_y + skh // 2),
             (cx - skw // 2, sk_c_y + int(skh * 0.10))]
    # clean 2-tone stub skull (round 3): bright-brass dome + INK sockets/jaw notch
    pygame.draw.polygon(surf, INK, skull)
    pygame.draw.polygon(surf, BRASS_BR, skull)
    pygame.draw.polygon(surf, INK, skull, max(1, int(1.0 * s)))
    er = max(1, int(skw * 0.18))
    for sg in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (cx + sg * int(skw * 0.22), sk_c_y - int(skh * 0.06)), er)
    jw = int(skw * 0.40)
    jy = sk_c_y + int(skh * 0.14)
    pygame.draw.polygon(surf, INK,
                        [(cx - jw // 2, jy), (cx + jw // 2, jy),
                         (cx + int(jw * 0.3), jy + int(skh * 0.34)),
                         (cx - int(jw * 0.3), jy + int(skh * 0.34))])


# -- compose the review sheet -------------------------------------------------
SS = 6


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


def render_hero():
    big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
    draw_automaton(big, 180 * SS, 250 * SS, 1.78 * SS)
    small = pygame.transform.smoothscale(big, (360, 470))
    return grow_outline(small, INK + (255,), 1)


def main():
    W, H = 1180, 820
    font_big, font, font_sm = load_fonts()

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("OXBLOOD AUTOMATON KING", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "Skull-Kings-II  ·  rigid BLOCKY humanoid machine · riveted copper plates + peg legs + square pauldrons · "
        "circular GEAR-RINGS at joints · DAY torso/legs/head COOLED to iron + DAY crown gets a dark ink rim · skull-on-gear-spire crown = the ONLY warm focal · round 6",
        True, LABEL_DIM), (360, 26))

    # === (a) BIG HERO =========================================================
    hero = render_hero()
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature - hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("Boxy copper machine: square torso + pauldrons, PEG LEGS, two stiff geometric", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("arms w/ gear-elbows. Circular GEAR-RINGS at every joint (the de-collider).", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("CLEAN 2-tone brass SKULL on a bold gear-spire = crown + BRIGHTEST warm value; torso gear-eye demoted HARD (iron/copper-shade).", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled - mirrored ======================================
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
    sheet.blit(font.render("Pillar - copper plate column", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked riveted plates + oxblood inlay stripe,", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("gear-ring lashings; gap-cap machine-head w/", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("gear-eye + skull-spire (mirrored top<->bottom)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night sky + SILHOUETTE proof =============
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        global _DAY_COOL
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        # WHY night_rim is targeted (round 2): the warm halo now rides the SKULL +
        # spire only (drawn inside skull_spire), so the crown survives the dim
        # night sky without globally bleaching the body — the skull, not the whole
        # figure, is what must stay legible as the brightest warm value.
        # round 6: cool the body copper to cold iron on the DAY chip only — night
        # keeps warm copper so its already-passing first-read is untouched.
        _DAY_COOL = not night
        draw_automaton(big, 48 * SS, 52 * SS, (32 / 124.0) * SS, night_rim=night)
        _DAY_COOL = False
        small = pygame.transform.smoothscale(big, (96, 96))
        if night:
            # a faint warm body-edge + crisp ink keyline so the dimmed copper mass
            # still parts from the night sky (the loud warm rim lives on the skull)
            base = grow_outline(small, COPPER_D + (210,), 1)
            return grow_outline(base, INK + (220,), 1)
        return grow_outline(small, INK + (255,), 1)

    day_chip = chip32(night=False)
    night_chip = chip32(night=True)

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(day_chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px day (iron body + dark-rim crown)", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(night_chip, (panel_x + 20 + 27 - 1, night_y + 27 - 1))
    sheet.blit(font_sm.render("32px night (warm rim on SKULL+spire)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # silhouette proof - blacked-out hero so the blocky machine read is checked
    def silhouette():
        big = pygame.Surface((150 * SS, 200 * SS), pygame.SRCALPHA)
        draw_automaton(big, 75 * SS, 96 * SS, 1.28 * SS)
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
    sheet.blit(font_sm.render("(blocky humanoid + spire)", True, LABEL_DIM), (sil_x, day_y + 220))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = sil_x + 168
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (COPPER, "patinated copper"), (COPPER_D, "copper shade"),
        (OXBLOOD, "oxblood lacquer"), (OXBLOOD_BR, "oxblood lit"),
        (BRASS, "brass gear-eye"), (BRASS_BR, "brass hot core"),
        (VERD, "verdigris tick"), (IRON, "iron rivet"),
        (COPPER_SH, "copper sheen"), (INK, "ink keyline"),
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
        "RIGID BLOCKY HUMANOID MACHINE: peg legs + square pauldrons + circular GEAR-RINGS (vs Bismuth's limbless angular crystal).  "
        "NIGHT keeps WARM copper mass (crown = brightest, warm rim); DAY cools torso/legs/head to IRON + adds a dark INK rim on the crown so the brass skull is the SOLE warm focal on pale-blue sky.  "
        "SS=6 supersample -> smoothscale · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_6.png")
    pygame.image.save(sheet, out)
    print("wrote", out)
    self_check()
    squint_proof()


def self_check():
    """Verify (round 3) that the CROWN SKULL — not the now-demoted torso gear-eye —
    owns the single brightest pixel AND that pixel is brass hot-core, since on a
    Skull King the skull must win the brightest-warm tie; and that the body stays
    WARM (copper) with verdigris a tiny fraction (never twins Malachite). The crown
    sits above the head, so the brightest pixel must land in the upper band."""
    cx, cy = 200, 280
    surf = pygame.Surface((400, 560), pygame.SRCALPHA)
    draw_automaton(surf, cx, cy, 2.0)
    px = pygame.surfarray.pixels3d(surf)
    a = pygame.surfarray.pixels_alpha(surf)
    w, h = surf.get_size()
    best_lum, best_xy = -1, (0, 0)
    warm_n, cool_n = 0, 0
    for x in range(0, w, 2):
        for yy in range(0, h, 2):
            if a[x, yy] < 40:
                continue
            r, g, b = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > best_lum:
                best_lum, best_xy = lum, (x, yy)
            if r > g and r > b and r > 90:        # warm: copper/brass/oxblood
                warm_n += 1
            if g > r and g > b and g > 90:        # cool: verdigris green
                cool_n += 1
    bx, by = best_xy
    r, g, b = int(px[bx, by][0]), int(px[bx, by][1]), int(px[bx, by][2])
    is_brass = (r > 220 and g > 175 and b < 215 and r >= b)
    # the crown skull sits well above the head centre; the torso eye is below it.
    head_top = cy - int(34 * 2.0) - int(18 * 2.0)     # top of the face plate
    in_crown = by < head_top
    # round 4: also weigh WARM MASS in the crown band vs the chest band, since the
    # day-chip tie was lost on AREA, not peak luminance. Crown warm mass must
    # clearly exceed the chest's (the chest is now iron, so it should be ~0).
    chest_top, chest_bot = cy - int(8 * 2.0), cy - int(8 * 2.0) + int(40 * 2.0)
    crown_warm = chest_warm = 0
    for x in range(0, w, 2):
        for yy in range(0, h, 2):
            if a[x, yy] < 40:
                continue
            rr, gg, bb = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            warm = (rr > gg and rr > bb and rr > 150 and gg > 100)   # bright warm
            if not warm:
                continue
            if yy < head_top:
                crown_warm += 1
            elif chest_top <= yy <= chest_bot and abs(x - cx) < int(13 * 2.0):
                chest_warm += 1
    del px, a
    print("self-check: brightest pixel @", best_xy, "rgb", (r, g, b),
          "lum %.0f" % best_lum, "-> brass-core?", is_brass,
          "-> in CROWN band (above head)?", in_crown)
    print("self-check: BRIGHT-WARM mass  crown ~%d  vs chest-centre ~%d  -> crown wins margin? %s"
          % (crown_warm, chest_warm, crown_warm > chest_warm * 3))
    print("self-check: warm px ~%d  vs cool px ~%d  -> cool fraction %.3f (must be small)"
          % (warm_n, cool_n, cool_n / max(1, warm_n + cool_n)))


def squint_proof():
    """Round-6 gate: render the TRUE 32px gameplay chip on day AND night, composite
    over the matching sky (so the measure sees real brass-vs-sky contrast), and count
    per-AREA warm pixels in the crown band (above the head) vs the torso band. This is
    the gameplay first-read pixel grid — the same per-area density the round-5 critique
    used (DAY body 580 vs crown 244). The brass crown must be the sole warm focal on
    BOTH palettes; on day the torso warm area must collapse so the crown now wins."""
    global _DAY_COOL
    for night in (False, True):
        _DAY_COOL = not night
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_automaton(big, 48 * SS, 52 * SS, (32 / 124.0) * SS, night_rim=night)
        _DAY_COOL = False
        chip = pygame.transform.smoothscale(big, (32, 32))
        sky = pygame.Surface((32, 32))
        for j in range(32):
            sky.fill(lerp(NIGHT_T if night else DAY_SKY_T,
                          NIGHT_B if night else DAY_SKY_B, j / 31.0),
                     (0, j, 32, 1))
        sky.blit(chip, (0, 0))
        px = pygame.surfarray.pixels3d(sky)
        # crown sits in the TOP band, torso mid. A pixel is warm if red leads both
        # other channels — copper/brass/oxblood; the cool iron body fails this.
        crown_warm = torso_warm = 0
        hottest_lum, hottest_y = -1, 0
        for x in range(32):
            for y in range(32):
                r, g, b = int(px[x, y][0]), int(px[x, y][1]), int(px[x, y][2])
                warm = (r > g + 4 and r > b + 8 and r > 110)
                if warm:
                    if y < 11:
                        crown_warm += 1
                    elif 11 <= y < 24:
                        torso_warm += 1
                    lum = 0.299 * r + 0.587 * g + 0.114 * b
                    if lum > hottest_lum:
                        hottest_lum, hottest_y = lum, y
        del px
        band = "CROWN" if hottest_y < 11 else ("TORSO" if hottest_y < 24 else "LEGS")
        # DAY gate (the round-6 fix): the body is cooled to iron, so the torso warm
        # area must be ~0 and the crown the lone warm focal. NIGHT gate (unchanged,
        # already passing): the body stays warm copper BY DESIGN, so the test is that
        # the HOTTEST warm pixel — the first-read — lands in the crown band (the warm
        # rim + brass hot-core tip it), not that the torso carries no warm area.
        if night:
            ok = (band == "CROWN")
            print("squint[NIGHT]: hottest warm pixel band = %s (y=%d) -> crown is "
                  "first-read? %s | (warm copper body by design: crown %d / torso %d)"
                  % (band, hottest_y, ok, crown_warm, torso_warm))
        else:
            ok = (crown_warm > 0 and torso_warm == 0 and band == "CROWN")
            print("squint[DAY]:   crown warm-area %d  vs torso warm-area %d  -> crown "
                  "is the SOLE warm focal? %s | hottest warm pixel band = %s (y=%d)"
                  % (crown_warm, torso_warm, ok, band, hottest_y))


if __name__ == "__main__":
    main()
