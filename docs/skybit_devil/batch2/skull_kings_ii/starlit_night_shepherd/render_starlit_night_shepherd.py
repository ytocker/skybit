"""
Round-1 concept renderer for the STARLIT NIGHT SHEPHERD — royal skull-KING of
the second skull-king brood (mandatory-cradle / 4-arm slot). Headless Pygame;
ELEVATED pipeline (SS=6 -> smoothscale) so the star-tick detail and the cupped
moon-skull glow survive the downscale. Clones the sibling king grammar wholesale
(flat triad fill, 1-2px ink keyline (28,22,30), alpha-grown outline, chibi
scary-cute, ONE dominant mass + thin accents) and applies the brood lineage tell
(an above-head skull crown + a single cupped focal).

WHY this KIND de-collides from the rest of the brood: the body is a tall TEARDROP
/ candle-flame BELL — a narrow head/shoulders that bells smoothly into a ROUNDED
teardrop hem with NO shoulder-flare. That rounded hem is the hard lock: it reads
opposite to a straight triangular A-frame (Frost), so the two never look alike in
silhouette.

WHY the crown reads at 32px: it is a HOVERING HALO-RING above the head carrying
ONE dominant zenith skull at its apex — NOT seven tiny skulls (which would mush
at 32px). A studded thin circlet + one big skull = a clean "ring + zenith skull"
tell that downscales cleanly.

WHY the moon-skull owns the focal: the lower two of the four arms CRADLE a glowing
pale-cyan moon-skull at the chest — it is the single brightest pixel. The indigo
cloak is the dominant cool MASS; the cool-silver star-ticks are CLUSTERED (a
constellation patch on the cloak, not coin-sparkle FX scattered everywhere); the
upper two arms hold a star-map scroll + an astrolabe as thin accents only.

NIGHT LOCK: deep-indigo would vanish on a night sky, so the silhouette is carried
by the cool blue-bone limbs/skull, the glowing moon-skull, and a cool-bone night
rim grown on the 32px chip.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + triad/outline helpers, not runtime sprites.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# -- PINNED PALETTE (locked brief) --------------------------------------------
# Deep-INDIGO cloak is the dominant cool MASS; everything else is a thin accent.
INDIGO    = ( 52,  58, 112)    # deep indigo cloak (dominant fill); lifted ~1
                               # value step from (40,44,92) so the bell body
                               # doesn't dissolve into a dark night sky
INDIGO_D  = ( 26,  28,  62)    # cloak dark-core / hollow
INDIGO_DD = ( 16,  18,  42)    # deepest cloak shadow (hem under-folds)
INDIGO_SH = ( 78,  84, 140)    # cloak top-left rim-sheen
# DEMOTED cool-bone — crown skull, head, limbs, ring circlet. WHY darker than
# round 1: three skulls at near-equal value mushed the focal hierarchy at 32px,
# so the head + crown skull are pushed down into a cooler, dimmer bone band and
# only the cradled moon-skull is allowed to read bright.
BONE      = (132, 146, 178)    # was (176,188,214) — pulled down so it loses to MOON
BONE_D    = ( 92, 104, 138)
BONE_DD   = ( 58,  68,  98)
BONE_SH   = (170, 182, 210)    # was (224,232,246) — a quiet rim, not a highlight
# HEAD skull is pushed a further 2-3 value steps BELOW the limb bone into a cool
# dark-bone band. WHY a dedicated darker pair: the head must NOT compete with the
# cradled moon focal — at 32px a near-equal head skull read as a second cyan dot.
HEAD_BONE   = ( 78,  88, 120)
HEAD_BONE_D = ( 52,  60,  88)
# cool-silver star-ticks — CLUSTERED constellation studs; deliberately DIMMER
# and COOLER than the moon focal so they never read as coin-sparkle FX.
STAR      = (158, 172, 206)
STAR_D    = (104, 118, 156)
# the SINGLE warm/bright focal — the cradled MOON-SKULL (pale-cyan glow). It is
# the ONLY element pushed to near-white; everything else is held below it.
MOON      = (206, 234, 244)
MOON_BR   = (232, 248, 252)
MOON_HOT  = (250, 254, 255)    # hottest moon-skull core (the brightest pixel)
MOON_D    = (120, 162, 190)
MOON_RIM  = ( 86, 124, 154)
# the skull-glow SPILL tint dropped onto the cradling cloak/hands (cool-cyan)
SPILL     = (108, 168, 196)
# crisp cool-silver/pewter RIM on the bell's lit edge. WHY a dedicated bright
# pewter (above BONE_SH): a true rim-light is what carries the teardrop mass on
# a dark night sky — round 2's dim BONE_SH edge lost ~40% of the silhouette.
RIM_LIT   = (196, 210, 236)
RIM_LIT_D = (146, 162, 196)
# astrolabe is now COOL pewter (no warm brass) so the cyan focal owns the only
# warm/bright read at 32px.
BRASS     = (118, 134, 150)
BRASS_BR  = (162, 178, 192)
BRASS_D   = ( 80,  94, 110)
INK       = ( 28,  22,  30)    # hard ink keyline

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
    for (a, b) in ((p0, p1), (p1, p2)):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * thick / 2, dx / L * thick / 2
        quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
        triad_blob(surf, BONE, quad,
                   sheen_pts=[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                              (b[0] + nx * 0.3, b[1] + ny * 0.3),
                              (a[0] + nx * 0.3, a[1] + ny * 0.3)],
                   ow=max(1, int(thick * 0.18)))
    if joint:
        triad_circle(surf, BONE, p1, int(thick * 0.62), ow=max(1, int(1.2 * s)),
                     core=False)


# -- the CLUSTERED constellation star-ticks (the cloak tell) ------------------
def star_tick(surf, cx, cy, r, s):
    """A tiny 4-point cool-silver star stud. WHY a 4-point glyph, not a dot:
    a stud reads as a STAR up close yet collapses to a clean light pip at 32px;
    clustered into a constellation patch it never looks like scattered coin FX."""
    pygame.draw.circle(surf, STAR_D, (int(cx), int(cy)), max(1, int(r * 0.7)))
    pygame.draw.circle(surf, STAR, (int(cx), int(cy)), max(1, int(r * 0.45)))
    # thin cross rays
    rr = max(1, int(r * 1.4))
    lw = max(1, int(0.8 * s))
    pygame.draw.line(surf, STAR, (cx - rr, cy), (cx + rr, cy), lw)
    pygame.draw.line(surf, STAR, (cx, cy - rr), (cx, cy + rr), lw)


def constellation_patch(surf, cx, cy, s):
    """TWO tight constellations on the cloak skirt — fixed offsets so each reads
    as a deliberate little star-map cluster. WHY two tight groups (not 11 spread
    studs) and dimmer/cooler ink: scattered bright pips read as the game's
    coin-sparkle FX; a couple of compact, low-key clusters read as drawn stars."""
    # two compact clusters, each kept clear of the low-center moon glow
    clusters = [
        # left-skirt triangle
        [(-18, 6, 1.3), (-13, 14, 1.0), (-21, 16, 1.0)],
        # right-skirt small dipper
        [(15, 10, 1.3), (20, 16, 1.0), (14, 19, 1.0), (21, 22, 0.9)],
    ]
    links = [[(0, 1), (1, 2)], [(0, 1), (1, 2), (2, 3)]]
    for pts, link in zip(clusters, links):
        for (i, j) in link:
            ax, ay = cx + pts[i][0] * s, cy + pts[i][1] * s
            bx, by = cx + pts[j][0] * s, cy + pts[j][1] * s
            pygame.draw.line(surf, lerp(INDIGO_SH, STAR_D, 0.3),
                             (ax, ay), (bx, by), max(1, int(0.6 * s)))
        for (dx, dy, m) in pts:
            star_tick(surf, cx + dx * s, cy + dy * s, max(1.0, m * s), s)


# -- the cradled MOON-SKULL (the single brightest focal) ----------------------
def moon_skull(surf, cx, cy, r, s):
    """A glowing pale-cyan skull cupped at the chest. WHY a strong layered aura +
    a hot near-white core + a tight bloom ring: it must own the single brightest
    pixel and win the value contest against the demoted crown/head so the focal
    hierarchy survives the downscale to 32px, day and night, without ballooning
    into a second large mass."""
    for (rr, a) in ((r * 2.3, 30), (r * 1.8, 52), (r * 1.35, 96), (r * 1.06, 150)):
        halo = pygame.Surface((int(rr * 2) + 4, int(rr * 2) + 4), pygame.SRCALPHA)
        pygame.draw.circle(halo, MOON_BR + (a,), (int(rr) + 2, int(rr) + 2), int(rr))
        surf.blit(halo, (cx - int(rr) - 2, cy - int(rr) - 2))
    # a tight near-white bloom ring hugging the cranium (the 1px-at-32px bloom)
    bloom = pygame.Surface((int(r * 2.6), int(r * 2.6)), pygame.SRCALPHA)
    pygame.draw.circle(bloom, MOON_HOT + (120,),
                       (int(r * 1.3), int(r * 1.3)), int(r * 1.12))
    surf.blit(bloom, (cx - int(r * 1.3), cy - int(r * 1.3)))
    # cranium
    pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(1.4 * s)))
    pygame.draw.circle(surf, MOON_RIM, (cx, cy), r)
    pygame.draw.circle(surf, MOON, (cx, cy), int(r * 0.9))
    # jaw bulge
    jaw = [(cx - int(r * 0.42), cy + int(r * 0.62)),
           (cx + int(r * 0.42), cy + int(r * 0.62)),
           (cx + int(r * 0.30), cy + int(r * 0.98)),
           (cx - int(r * 0.30), cy + int(r * 0.98))]
    pygame.draw.polygon(surf, INK, jaw)
    pygame.draw.polygon(surf, MOON, jaw)
    # cool crescent sheen makes it read as a MOON
    pygame.draw.circle(surf, MOON_BR, (cx - int(r * 0.18), cy - int(r * 0.20)),
                       int(r * 0.62))
    pygame.draw.circle(surf, MOON_HOT, (cx - int(r * 0.26), cy - int(r * 0.28)),
                       max(1, int(r * 0.30)))
    # eye-pits (kept dark so the skull reads, but small so glow dominates)
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.40)
        ey = cy + int(r * 0.06)
        pygame.draw.circle(surf, MOON_D, (ex, ey), int(r * 0.26))
        pygame.draw.circle(surf, INK, (ex, ey), int(r * 0.19))
    pygame.draw.polygon(surf, INK,
                        [(cx - int(r * 0.10), cy + int(r * 0.26)),
                         (cx + int(r * 0.10), cy + int(r * 0.26)),
                         (cx, cy + int(r * 0.46))])
    # tiny grin teeth
    my = cy + int(r * 0.72)
    pygame.draw.line(surf, INK, (cx - int(r * 0.30), my), (cx + int(r * 0.30), my),
                     max(1, int(1.4 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, INK, (cx + int(k * r * 0.14), my - int(r * 0.05)),
                         (cx + int(k * r * 0.14), my + int(r * 0.08)),
                         max(1, int(0.9 * s)))


# -- the HOVERING HALO-RING crown with ONE dominant zenith skull --------------
def halo_crown(surf, cx, cy, r, s, dome_c=None, dome_r=0):
    """A thin studded circlet welded onto the head + a single big zenith
    skull at its apex. WHY one big skull (not 7 tiny): seven micro-skulls mush
    at 32px; one dominant zenith skull on a thin studded ring reads cleanly as
    'a ring + a crown-skull' all the way down to gameplay scale."""
    rx, ry = r, int(r * 0.42)
    # WELD the ring to the dome: two short cool-bone struts bridge the ring's
    # side extremes down to the cranium. WHY: round 2's ring floated free and the
    # silhouette read as a top-left "lollipop" arm; the struts fuse ring + head
    # into ONE bump so the figure stays a single teardrop mass.
    if dome_c is not None:
        for sgn in (-1, 1):
            sx = cx + sgn * int(rx * 0.92)
            top = (sx, cy + int(ry * 0.2))
            bot = (dome_c[0] + sgn * int(dome_r * 0.78),
                   dome_c[1] - int(dome_r * 0.42))
            pygame.draw.line(surf, INK, top, bot, max(3, int(4.0 * s)))
            pygame.draw.line(surf, BONE_D, top, bot, max(2, int(2.6 * s)))
    # the ring drawn as a flattened ellipse (a halo seen near edge-on)
    ring_rect = (cx - rx, cy - ry, rx * 2, ry * 2)
    pygame.draw.ellipse(surf, INK, ring_rect, max(2, int(3.0 * s)))
    pygame.draw.ellipse(surf, BONE, ring_rect, max(1, int(2.2 * s)))
    pygame.draw.ellipse(surf, BONE_SH,
                        (cx - rx, cy - ry - int(0.8 * s), rx * 2, ry * 2),
                        max(1, int(1.0 * s)))
    # studded gems on the circlet — tiny star-silver pips around the front arc
    for k in range(7):
        a = math.radians(180 + k * (180 / 6))
        gx = cx + math.cos(a) * rx
        gy = cy + math.sin(a) * ry
        star_tick(surf, gx, gy, max(1.0, 1.3 * s), s)
    # ONE zenith skull seated at the ring apex (the crown tell). WHY no bright
    # aura and a cool-bone fill: this skull must stay DARKER than the cradled moon
    # focal so the value hierarchy reads — it is the "crown" beat, not a light.
    zr = int(r * 0.40)
    zx, zy = cx, cy - ry - zr + int(6 * s)   # tucked onto the ring, no detached gap
    triad_circle(surf, BONE_D, (zx, zy), zr, ow=max(1, int(1.6 * s)), core=False,
                 sheen=False)
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_DD, (zx + sgn * int(zr * 0.40),
                           zy + int(zr * 0.04)), int(zr * 0.28))
        pygame.draw.circle(surf, INK, (zx + sgn * int(zr * 0.40),
                           zy + int(zr * 0.04)), int(zr * 0.21))
    pygame.draw.polygon(surf, BONE_DD,
                        [(zx - int(zr * 0.12), zy + int(zr * 0.30)),
                         (zx + int(zr * 0.12), zy + int(zr * 0.30)),
                         (zx, zy + int(zr * 0.52))])
    zmy = zy + int(zr * 0.68)
    pygame.draw.line(surf, INK, (zx - int(zr * 0.32), zmy), (zx + int(zr * 0.32), zmy),
                     max(1, int(1.2 * s)))


# -- the scroll + astrolabe held by the upper two arms (thin accents) ---------
def star_scroll(surf, cx, cy, s):
    """A small rolled star-map scroll. WHY kept dull-brass + tiny: an upper-arm
    prop must stay a thin accent so neither it nor the astrolabe steals heat
    from the moon-skull focal."""
    w, h = int(11 * s), int(20 * s)
    body = [(cx - w, cy - h), (cx + w, cy - h),
            (cx + w, cy + h), (cx - w, cy + h)]
    triad_blob(surf, BONE, body,
               sheen_pts=[(cx - w, cy - h), (cx - int(w * 0.2), cy - h),
                          (cx - int(w * 0.2), cy + h), (cx - w, cy + h)],
               ow=max(1, int(1.0 * s)))
    # rolled caps
    for ry in (cy - h, cy + h):
        triad_circle(surf, BONE_D, (cx, ry), int(w * 1.05),
                     ow=max(1, int(1.0 * s)), core=False, sheen=False)
    # a couple of star marks inked on the parchment
    for (dx, dy) in ((-3, -6), (2, -1), (4, 6), (-2, 5)):
        star_tick(surf, cx + dx * s, cy + dy * s, max(1.0, 1.0 * s), s)


def astrolabe(surf, cx, cy, r, s):
    """A thin dull-brass ring disc with a cross-rule + a star pip. WHY a thin
    ring not a filled disc: keeps it a line-work accent at hero scale and a
    near-invisible thread at 32px so the moon-skull owns the read."""
    pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(1.0 * s)))
    pygame.draw.circle(surf, BRASS, (cx, cy), r, max(2, int(2.4 * s)))
    pygame.draw.circle(surf, BRASS_BR, (cx - int(r * 0.3), cy - int(r * 0.3)),
                       max(1, int(1.2 * s)))
    pygame.draw.line(surf, BRASS_D, (cx - r, cy), (cx + r, cy), max(1, int(1.4 * s)))
    pygame.draw.line(surf, BRASS_D, (cx, cy - r), (cx, cy + r), max(1, int(1.4 * s)))
    # rotating alidade arm + a star pip at the rim
    pygame.draw.line(surf, BRASS_BR, (cx - int(r * 0.8), cy + int(r * 0.5)),
                     (cx + int(r * 0.8), cy - int(r * 0.5)), max(1, int(1.4 * s)))
    star_tick(surf, cx + int(r * 0.7), cy - int(r * 0.44), max(1.0, 1.2 * s), s)


# -- the teardrop / candle-flame BELL body, four arms, skull head -------------
def draw_shepherd(surf, cx, cy, s):
    head_c = (cx, cy - int(40 * s))
    hr = int(20 * s)
    hem_y = cy + int(58 * s)

    # === TEARDROP / CANDLE-FLAME BELL CLOAK ==================================
    # WHY a high vertex count smooth bell: the hard lock is a ROUNDED hem with
    # NO shoulder-flare — narrow at the shoulders, swelling to a rounded
    # teardrop base, so the silhouette never reads as a triangular A-frame.
    top_y = head_c[1] + int(hr * 0.7)
    bell = []
    N = 48
    half_w = int(46 * s)           # widest belly of the teardrop
    neck_w = int(13 * s)           # narrow shoulders (no flare)
    for k in range(N + 1):
        t = k / N                  # 0..1 down one side
        # candle-flame profile: pinched at the top, bellying low, rounded base
        prof = math.sin(math.pi * (0.18 + 0.82 * t))     # 0 at very top
        belly = (1 - (1 - t) ** 2.2)                      # push fullness downward
        w = neck_w + (half_w - neck_w) * prof * (0.35 + 0.65 * belly)
        y = top_y + t * (hem_y - top_y)
        bell.append((cx - w, y))
    # rounded hem across the bottom, then back up the right side
    for k in range(N + 1):
        t = 1 - k / N
        prof = math.sin(math.pi * (0.18 + 0.82 * t))
        belly = (1 - (1 - t) ** 2.2)
        w = neck_w + (half_w - neck_w) * prof * (0.35 + 0.65 * belly)
        y = top_y + t * (hem_y - top_y)
        bell.append((cx + w, y))
    triad_blob(surf, INDIGO, bell,
               core_pts=[(cx - int(6 * s), top_y + int(20 * s)),
                         (cx + int(half_w * 0.7), hem_y - int(20 * s)),
                         (cx + int(half_w * 0.4), hem_y - int(2 * s)),
                         (cx - int(6 * s), hem_y - int(2 * s))],
               sheen_pts=[(cx - neck_w, top_y + int(2 * s)),
                          (cx - int(8 * s), top_y + int(2 * s)),
                          (cx - int(half_w * 0.62), hem_y - int(16 * s)),
                          (cx - int(half_w * 0.78), hem_y - int(10 * s))],
               ow=max(1, int(1.8 * s)))
    # a couple of deep hem under-folds so the rounded base reads as cloth
    for sgn in (-1, 0, 1):
        fx = cx + sgn * int(20 * s)
        pygame.draw.line(surf, INDIGO_DD, (fx, hem_y - int(20 * s)),
                         (fx, hem_y - int(2 * s)), max(1, int(2.0 * s)))

    # === COOL-SILVER RIM-LIGHT down the lit (left) edge + around the hem =====
    # WHY a real 2-layer rim that wraps from the shoulder down the lit edge and
    # AROUND the rounded hem: round 2's single dim line lost ~40% of the night
    # silhouette. A soft pewter underlay + a crisp bright top line reads as a
    # moonlit edge and holds the full teardrop mass against a dark night sky.
    rim_pts = []
    rN = 40
    for k in range(rN + 1):
        t = 0.08 + 0.90 * k / rN
        prof = math.sin(math.pi * (0.18 + 0.82 * t))
        belly = (1 - (1 - t) ** 2.2)
        w = neck_w + (half_w - neck_w) * prof * (0.35 + 0.65 * belly)
        y = top_y + t * (hem_y - top_y)
        rim_pts.append((cx - w + int(1.4 * s), y))
    # carry the rim across the rounded hem so the base edge stays lit, not lost.
    # WHY the hem points stay set ~5px ABOVE hem_y: a rim that touched the very
    # base edge spilled a stray spur past the mask in the silhouette.
    rim_full = rim_pts + [(cx - int(half_w * 0.58), hem_y - int(7 * s)),
                          (cx - int(half_w * 0.30), hem_y - int(5 * s))]
    if len(rim_full) > 1:
        pygame.draw.lines(surf, RIM_LIT_D, False, rim_full, max(2, int(2.6 * s)))
        pygame.draw.lines(surf, RIM_LIT, False, rim_pts, max(1, int(1.8 * s)))

    # === SKULL-GLOW SPILL on the cloak where the moon is cradled =============
    # WHY a wider, brighter cyan wash low-center: the focal must visibly light the
    # cloth around it, both to tie the brightest element to the dominant indigo
    # mass AND to keep a glowing cool core in the silhouette on a dark night sky.
    spill_c = (cx, cy + int(10 * s))
    for (rr, a) in ((int(44 * s), 34), (int(32 * s), 60),
                    (int(22 * s), 92), (int(14 * s), 120)):
        sp = pygame.Surface((rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(sp, SPILL + (a,), (rr + 2, rr + 2), rr)
        surf.blit(sp, (spill_c[0] - rr - 2, spill_c[1] - rr - 2))

    # === CLUSTERED CONSTELLATION on the cloak (the tell, not scattered FX) ===
    constellation_patch(surf, cx - int(4 * s), cy + int(8 * s), s * 0.92)

    # === UPPER TWO ARMS — scroll (left) + astrolabe (right) ==================
    arm_th = int(6 * s)
    # left upper arm reaching up holding the scroll
    sh_l = (cx - int(11 * s), top_y + int(8 * s))
    el_l = (cx - int(30 * s), cy - int(12 * s))
    hand_l = (cx - int(34 * s), cy - int(26 * s))
    bone_limb(surf, sh_l, el_l, hand_l, arm_th, s)
    star_scroll(surf, hand_l[0] - int(2 * s), hand_l[1] - int(8 * s), s)
    # right upper arm holding the astrolabe out
    sh_r = (cx + int(11 * s), top_y + int(8 * s))
    el_r = (cx + int(30 * s), cy - int(10 * s))
    hand_r = (cx + int(36 * s), cy - int(22 * s))
    bone_limb(surf, sh_r, el_r, hand_r, arm_th, s)
    # shrunk + cooled (pewter, not brass) so the only warm/bright read is the moon
    astrolabe(surf, hand_r[0] + int(7 * s), hand_r[1] - int(5 * s), int(9 * s), s)

    # === LOWER TWO ARMS — CRADLING the moon-skull at the chest ===============
    moon_c = (cx, cy + int(6 * s))
    moon_r = int(17 * s)
    sh_ll = (cx - int(12 * s), top_y + int(16 * s))
    el_ll = (cx - int(24 * s), cy + int(2 * s))
    hand_ll = (moon_c[0] - int(11 * s), moon_c[1] + int(13 * s))
    bone_limb(surf, sh_ll, el_ll, hand_ll, arm_th, s)
    sh_rr = (cx + int(12 * s), top_y + int(16 * s))
    el_rr = (cx + int(24 * s), cy + int(2 * s))
    hand_rr = (moon_c[0] + int(11 * s), moon_c[1] + int(13 * s))
    bone_limb(surf, sh_rr, el_rr, hand_rr, arm_th, s)

    # the cupped MOON-SKULL drawn AFTER the cradling hands -> it owns foreground
    moon_skull(surf, moon_c[0], moon_c[1], moon_r, s)
    # cupping finger blades over the lower rim of the moon
    for sgn in (-1, 1):
        bx = moon_c[0] + sgn * int(12 * s)
        by = moon_c[1] + int(12 * s)
        tip = (moon_c[0] + sgn * int(3 * s), moon_c[1] + int(moon_r * 1.10))
        mid = (moon_c[0] + sgn * int(10 * s), moon_c[1] + int(moon_r * 1.22))
        finger = [(bx - sgn * int(3 * s), by - int(3 * s)),
                  (bx + sgn * int(4 * s), by - int(1 * s)),
                  (mid[0], mid[1]), (tip[0], tip[1]),
                  (tip[0] - sgn * int(2 * s), tip[1] - int(4 * s))]
        triad_blob(surf, BONE, finger,
                   sheen_pts=[(bx - sgn * int(3 * s), by - int(3 * s)),
                              (bx + sgn * int(1 * s), by - int(2 * s)),
                              (mid[0] - sgn * int(2 * s), mid[1] - int(1 * s)),
                              (tip[0], tip[1] - int(2 * s))],
                   ow=max(1, int(1.2 * s)))

    # === SKULL HEAD (cool DARK-bone — deliberately demoted) ==================
    # WHY the head is drawn in HEAD_BONE/HEAD_BONE_D (a band BELOW the limb bone)
    # with NO sheen and NO cyan socket glint: round 2 left the head skull near the
    # chest skull's value, so DAY blink-tested as TWO cyan dots. Sinking the head
    # 2-3 steps into cool dark-bone makes the cradled moon-skull the single
    # brightest pixel by a clear margin — ONE focal, not two.
    triad_circle(surf, HEAD_BONE, head_c, hr, ow=max(2, int(2 * s)),
                 sheen=False, core=False)
    # a quiet form-shadow only — no highlight that could mistake for a second focal
    pygame.draw.circle(surf, HEAD_BONE_D,
                       (head_c[0] + int(hr * 0.30), head_c[1] + int(hr * 0.34)),
                       int(hr * 0.74))
    pygame.draw.circle(surf, HEAD_BONE, head_c, int(hr * 0.80))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, HEAD_BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.30)),
                           int(hr * 0.28))
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.06)
        # sockets stay ink-dark (no cyan glint) so the head reads as a quiet skull
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.34))
        pygame.draw.circle(surf, lerp(HEAD_BONE_D, INK, 0.5), (ex, ey),
                           int(hr * 0.20))
    pygame.draw.polygon(surf, INK,
                        [(head_c[0] - int(hr * 0.13), head_c[1] + int(hr * 0.32)),
                         (head_c[0] + int(hr * 0.13), head_c[1] + int(hr * 0.32)),
                         (head_c[0], head_c[1] + int(hr * 0.58))])
    my = head_c[1] + int(hr * 0.74)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.42), my - int(hr * 0.02)),
                     (head_c[0] + int(hr * 0.42), my + int(hr * 0.06)),
                     max(1, int(2 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, INK,
                         (head_c[0] + int(k * hr * 0.18), my - int(hr * 0.06)),
                         (head_c[0] + int(k * hr * 0.18), my + int(hr * 0.10)),
                         max(1, int(1 * s)))

    # === HALO-RING CROWN + ZENITH SKULL, WELDED TO THE DOME ==================
    # WHY tucked LOWER (hr*0.58, was hr*0.72) AND fused with weld-struts: a ring
    # that floated above the dome read as a top-left lollipop arm in the
    # silhouette; sitting it on the crown and bridging it down keeps the figure
    # ONE teardrop mass while still reading "ring + zenith skull".
    halo_crown(surf, head_c[0], head_c[1] - int(hr * 0.58), int(hr * 1.00), s,
               dome_c=head_c, dome_r=hr)


# -- the moon-pillar mirror, derived from the king's forms --------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """A stacked-bone moon-shepherd column: a slim cool-bone shaft cinched by
    indigo bands carrying tiny star studs, capped at the gap edge by a cradled
    moon-skull echoing the king's focal. Mirrors top<->bottom, on-axis."""
    shaft_w = int(16 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    pitch = int(26 * s)
    cap_room = int(38 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    while y <= b1:
        for sgn in (-1, 1):
            fx = cx + sgn * int(7 * s)
            top_y = y - int(8 * s)
            bot_y = y + int(8 * s)
            shaft = [(fx - int(4 * s), top_y), (fx + int(4 * s), top_y),
                     (fx + int(3 * s), y), (fx + int(4 * s), bot_y),
                     (fx - int(4 * s), bot_y), (fx - int(3 * s), y)]
            triad_blob(surf, BONE, shaft,
                       sheen_pts=[(fx - int(4 * s), top_y), (fx - int(1 * s), top_y),
                                  (fx - int(1 * s), bot_y), (fx - int(4 * s), bot_y)],
                       ow=max(1, int(1.2 * s)))
            for ky in (top_y, bot_y):
                triad_circle(surf, BONE, (fx - int(3 * s), ky), int(3 * s),
                             ow=max(1, int(1.0 * s)), core=False)
                triad_circle(surf, BONE, (fx + int(3 * s), ky), int(3 * s),
                             ow=max(1, int(1.0 * s)), core=False)
        # indigo cinch band carrying a star stud (the cloak tell, miniaturised)
        band = [(cx - shaft_w * 0.66, y - int(4 * s)),
                (cx + shaft_w * 0.66, y - int(4 * s)),
                (cx + shaft_w * 0.66, y + int(4 * s)),
                (cx - shaft_w * 0.66, y + int(4 * s))]
        triad_blob(surf, INDIGO, band,
                   sheen_pts=[(cx - shaft_w * 0.66, y - int(4 * s)),
                              (cx, y - int(4 * s)), (cx, y - int(1 * s)),
                              (cx - shaft_w * 0.66, y - int(1 * s))],
                   ow=max(1, int(1.0 * s)))
        star_tick(surf, cx, y, max(1.0, 1.4 * s), s)
        y += pitch

    cap_y = (bot - int(24 * s)) if cap == "bottom" else (top + int(24 * s))
    fan_dir = -1 if cap == "bottom" else 1
    lip = [(cx - int(18 * s), cap_y - fan_dir * int(2 * s)),
           (cx + int(18 * s), cap_y - fan_dir * int(2 * s)),
           (cx + int(14 * s), cap_y - fan_dir * int(11 * s)),
           (cx - int(14 * s), cap_y - fan_dir * int(11 * s))]
    triad_blob(surf, INDIGO, lip, ow=max(1, int(1.2 * s)))
    # a thin halo-ring arc echoing the crown sits above the cap moon
    ring_cy = cap_y + fan_dir * int(10 * s)
    pygame.draw.ellipse(surf, INK,
                        (cx - int(15 * s), ring_cy - fan_dir * int(16 * s) - int(4 * s),
                         int(30 * s), int(12 * s)), max(1, int(1.6 * s)))
    pygame.draw.ellipse(surf, BONE,
                        (cx - int(15 * s), ring_cy - fan_dir * int(16 * s) - int(4 * s),
                         int(30 * s), int(12 * s)), max(1, int(1.2 * s)))
    # the cradled moon-skull cap (the king's focal, echoed at the gap edge)
    moon_y = cap_y + fan_dir * int(13 * s)
    moon_skull(surf, cx, moon_y, int(12 * s), s)


# -- compose the review sheet -------------------------------------------------
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_shepherd(big, draw_cx * SS, draw_cy * SS, scale * SS)
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
    sheet.blit(font_big.render("STARLIT NIGHT SHEPHERD", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "skull-KING (mandatory-cradle, 4 arms)  ·  teardrop candle-flame BELL · hovering halo-ring + zenith skull crown · "
        "cradled glowing MOON-SKULL focal · clustered star-ticks · round 3",
        True, LABEL_DIM), (320, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 226, 1.55)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("Teardrop candle-flame BELL (rounded hem, NO shoulder-flare). FOUR arms: upper", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("two hold a star-scroll + an astrolabe; lower two CRADLE the glowing moon-skull.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Crown = hovering halo-ring + ONE zenith skull. Moon-skull = single brightest pixel.", True, LABEL_DIM), (14, 622))

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
    sheet.blit(font.render("Pillar — moon-shepherd", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("cool-bone shaft, indigo star-studded cinch bands;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("halo-ring arc + cradled moon-skull cap at the gap", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, bottom-rooted)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night sky + SILHOUETTE proof =============
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_shepherd(big, 48 * SS, 54 * SS, (32 / 138.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        # WHY a cool blue-bone rim on the night chip: the deep-indigo cloak
        # dissolves into a dark night sky; a cool-bone halo carries the
        # silhouette while the pale moon-skull stays the unambiguous focal.
        # BONE_D (not the now-darker BONE_DD) keeps the rim readable on night.
        if night:
            base = grow_outline(small, BONE_D + (255,), 2)
            return grow_outline(base, INK + (200,), 1)
        return grow_outline(small, INK + (255,), 1)

    day_chip = chip32(night=False)
    night_chip = chip32(night=True)

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(day_chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(night_chip, (panel_x + 20 + 27 - 1, night_y + 27 - 1))
    sheet.blit(font_sm.render("32px on night sky (cool-bone rim)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # silhouette proof — blacked-out hero so the teardrop-bell read is checked
    def silhouette():
        big = pygame.Surface((150 * SS, 200 * SS), pygame.SRCALPHA)
        draw_shepherd(big, 75 * SS, 96 * SS, 1.12 * SS)
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
    sheet.blit(font_sm.render("(teardrop bell + ring crown)", True, LABEL_DIM), (sil_x, day_y + 220))

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
        (INDIGO, "deep indigo cloak"), (INDIGO_D, "indigo dark-core"),
        (BONE, "cool blue-bone"), (BONE_SH, "bone rim-sheen"),
        (MOON, "moon-skull glow"), (MOON_HOT, "moon hot core"),
        (STAR, "cool-silver star-tick"), (BRASS, "cool pewter prop"),
        (INDIGO_SH, "cloak sheen"), (INK, "ink keyline"),
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
        "Teardrop candle-flame BELL (rounded hem, no flare).  ONE dominant indigo mass + thin cool-bone/star accents.  "
        "Crown = hovering halo-ring + ONE zenith skull.  Cradled MOON-SKULL = single brightest focal, day + night.  SS=6 supersample -> smoothscale · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    self_check()


def self_check():
    """Render the hero alone and verify the brightest pixel sits inside the
    cradled moon-skull (the focal owns the peak)."""
    surf = pygame.Surface((400, 520), pygame.SRCALPHA)
    draw_shepherd(surf, 200, 250, 1.9)
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
    # moon-skull core hue: very bright, near-white cool (blue >= green-ish)
    is_moon = (r > 200 and g > 210 and b > 220)
    del px, a
    print("self-check: brightest pixel @", best_xy, "rgb", (r, g, b),
          "lum %.0f" % best_lum, "-> moon-skull core?", is_moon)


if __name__ == "__main__":
    main()
