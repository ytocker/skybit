"""
Round-1 concept renderer for SOTJANG — the sky-bird sentinel pole (Jangseung-
versions carved-WOOD spin-off, concept #5). Headless Pygame; supersample at
SS=6 then smoothscale to match the elevated house grammar (chibi, flat
saturated fills, hard 1-2px ink keyline, dark-core -> flat-fill -> top-left
rim-sheen triad, 1px alpha-grown outline).

WHY sotjang is the ONLY top-finial/bird read of its set: a real sotdae IS a
slim pole crowned by a carved guardian DUCK, so here the creature is a grumpy
sacred duck perched on a heaven-pole. That makes it the set's ONLY top-heavy
RISK, so the whole build is legibility-first: the body is a clean OVAL blob
with SPARSE feather-courses, and the slim turned-pine shaft is deliberately
BOTTOM-WEIGHTED by lathe ring-bands + prayer-cloth knots so the duck-crown can
never tip the silhouette. The gap-cap is a SECOND, clearly SMALLER (~70%)
mirrored duck tucked tight to the axis, bill lit.

WHY pale-bleached PINE + indigo flat PAINT mass + warm-amber eye, NO cinnabar:
the cross-set fix separates the wood bosses by VALUE/HUE. Sotjang owns the
palest, coolest-but-warm-bodied pine so the FLAT carved indigo neck-band reads
as a hard PAINT mass (never a glow — kept clear of Yurei's blue-cyan), the
honey-tan duck body is the warm focal mass, and the amber eye is the one glow.
Dropping cinnabar separates it cleanly from the source Jangseung.

WHY a standalone script: review art must never enter the shipped bundle, so it
lives under docs/ and reuses only colour math, not runtime sprite modules.
"""
import os
import math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Pale-bleached PINE pole — the palest, lightest-value wood of the set so the
# slim shaft stays a quiet support and the warm duck body reads as the mass.
PINE      = (196, 178, 140)   # pale-bleached pine pole base
PINE_D    = (150, 128,  92)   # pine shade (dark core)
PINE_T    = (224, 210, 178)   # bleached pine rim-sheen
PINE_GRV  = (120, 100,  72)   # carved lathe-groove shadow

# Honey-TAN duck body — warmer than the pole so the bird crown carries the mass.
BODY      = (206, 160,  96)   # honey-tan duck body
BODY_D    = (158, 116,  64)   # body shade (dark core)
BODY_T    = (236, 204, 152)   # body rim-sheen

# INDIGO neck-band + bill stripe — a FLAT carved PAINT mass, NOT a glow; hard
# edge, kept clear of any blue-cyan glow lineage.
INDIGO    = ( 58,  86, 138)   # flat indigo paint mass
INDIGO_D  = ( 36,  54,  92)   # indigo shade
INDIGO_T  = ( 96, 124, 176)   # indigo top-left sheen (still matte, not glow)

EYEGLOW   = (244, 200, 120)   # warm-amber eye glow (the one warm focal)
EYEGLOW_D = (206, 158,  86)   # eye-glow shade ring
BILL      = (224, 178,  98)   # bill horn (warm, between body + pine)
BILL_D    = (172, 128,  68)   # bill shade

LICHEN    = (176, 182, 156)   # pale lichen-grey patch
LICHEN_D  = (138, 146, 122)   # deep lichen
LICHEN_T  = (206, 210, 188)   # lichen rim-sheen

KNOT      = (188, 168, 120)   # prayer-cloth knot (pale cord, near pine)
KNOT_D    = (146, 124,  82)
KNOT_T    = (222, 206, 168)

INK       = ( 28,  22,  30)   # hard ink keyline (locked set ink)

BG        = ( 96, 100, 104)   # neutral grey review backdrop
PANEL     = ( 72,  76,  82)
DAY_SKY_T = (140, 206, 232)   # day biome sky (top)
DAY_SKY_B = (206, 232, 240)   # day biome sky (low)
NIGHT_T   = ( 22,  28,  52)   # night biome sky (top)
NIGHT_B   = ( 46,  44,  78)   # night biome sky (low)
LABEL     = (238, 240, 242)
LABEL_DIM = (188, 196, 204)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# ── outline grown from the alpha mask (the house keyline) ────────────────────
def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in outline_pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(base, (0, 0))
    return ring


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.45), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.35), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_ellipse(surf, color, cx, cy, rx, ry, s, ow=2):
    """A triad-shaded OVAL — flat fill + dark core (lower-right) + top-left
    rim-sheen + ink keyline. WHY an ellipse helper: the duck body must read as
    one clean OVAL blob, and a polygon oval fuzzes its own edge at downscale."""
    rect = pygame.Rect(0, 0, rx*2, ry*2)
    rect.center = (cx, cy)
    pygame.draw.ellipse(surf, INK, rect.inflate(ow*2, ow*2))
    pygame.draw.ellipse(surf, color, rect)
    core = pygame.Rect(0, 0, int(rx*1.2), int(ry*1.2))
    core.center = (cx + int(rx*0.34), cy + int(ry*0.36))
    pygame.draw.ellipse(surf, lerp(color, INK, 0.42), core)
    sh = pygame.Rect(0, 0, int(rx*0.9), int(ry*0.78))
    sh.center = (cx - int(rx*0.34), cy - int(ry*0.38))
    pygame.draw.ellipse(surf, lerp(color, (255, 255, 255), 0.32), sh)
    pygame.draw.ellipse(surf, color, rect.inflate(-ow*4, -ry))  # re-seat the fill mid-band
    pygame.draw.ellipse(surf, INK, rect, ow)


# ── deterministic lichen-patch stipple (procedural, no PRNG state leak) ───────
def lichen_patch(surf, cx, cy, rad, s, seed):
    """A single COMPACT lichen-grey cluster — a few BIG flat lobes that survive
    1x downscale, anchored INSIDE the silhouette on a groove edge so the lichen
    reads as carved-on aged growth, not floating noise."""
    n = 3
    for i in range(n):
        ha = ((seed * 73 + i * 137) % 360) * 3.14159 / 180.0
        hd = ((seed * 51 + i *  29) % 100) / 100.0
        hr = ((seed * 97 + i *  17) % 100) / 100.0
        lx = cx + int(math.cos(ha) * hd * rad * 0.5)
        ly = cy + int(math.sin(ha) * hd * rad * 0.5)
        lr = int((0.38 + 0.30 * hr) * rad)
        pygame.draw.circle(surf, INK, (lx, ly), lr + max(1, int(1*s)))
        pygame.draw.circle(surf, LICHEN, (lx, ly), lr)
        pygame.draw.circle(surf, LICHEN_D, (lx + int(lr*0.3), ly + int(lr*0.3)),
                           int(lr*0.52))
        pygame.draw.circle(surf, LICHEN_T, (lx - int(lr*0.34), ly - int(lr*0.34)),
                           max(1, int(lr*0.26)))


# ── the slim turned-pine shaft: lathe ring-bands + bottom-weighting knots ─────
def turned_shaft(surf, cx, top, bot, half_w, s, knots=True):
    """One stretch of the SLIM turned-pine pole. WHY this is the legibility
    spine of the whole concept: lathe RING-BANDS get denser toward the bottom
    and a couple of bulging prayer-cloth KNOTS sit low, so visual weight pools
    at the FOOT — the only way a bird-on-a-pole silhouette stays upright at
    thumbnail. The shaft is intentionally narrow so the duck crown owns the
    mass without the pole competing."""
    w = half_w * 2
    x0 = cx - half_w

    # main pine mass — flat fill + warm dark core on the right + bleached sheen
    body = [(x0, top), (x0 + w, top), (x0 + w, bot), (x0, bot)]
    triad_blob(
        surf, PINE, body,
        core_pts=[(cx + int(half_w*0.22), top), (x0 + w, top),
                  (x0 + w, bot), (cx + int(half_w*0.22), bot)],
        sheen_pts=[(x0, top), (x0 + int(half_w*0.34), top),
                   (x0 + int(half_w*0.34), bot), (x0, bot)],
        ow=max(2, int(2*s)),
    )

    # faint vertical grain — one or two short flecks, sparse so the slim pole
    # never crowds; centred so the eye still reads the band rhythm.
    span = bot - top
    gy = top + int(20*s)
    while gy < bot - int(16*s):
        pygame.draw.line(surf, PINE_GRV, (cx - int(half_w*0.18), gy),
                         (cx - int(half_w*0.18), gy + int(10*s)), max(1, int(1*s)))
        gy += int(70*s)

    # LATHE RING-BANDS — full-width turned rings. WHY denser AND DARKER toward
    # the bottom: round 1 filled every ring with PINE (the shaft tone), so the
    # rings carried no VALUE and washed out first at 32px — the exact marks that
    # are supposed to anchor the bottom vanished, leaving a top-heavy lollipop.
    # Now the low rings are filled DARK (PINE_D, ink groove cores, widening
    # bulge), so the bottom of the pole carries the highest-contrast, widest
    # mass on the whole figure and survives downscale as real dark weight.
    def ring(ry, h, dark=0.0, bulge_mul=1.0):
        rh = max(2, int(h*s))
        # rings read as turned beads; the low ones bulge wider for more mass
        bulge = int(half_w * (0.14 + 0.34*bulge_mul*dark))
        fill = lerp(PINE, PINE_D, dark)
        bead = [(x0 - bulge, ry), (x0 + w + bulge, ry),
                (x0 + w + bulge, ry + rh), (x0 - bulge, ry + rh)]
        pygame.draw.polygon(surf, INK, bead)
        pygame.draw.polygon(surf, fill, bead)
        # deep groove shadow along the BOTTOM edge — heavier on the dark rings
        gh = max(1, int((2 + 2*dark)*s))
        pygame.draw.line(surf, lerp(PINE_GRV, INK, dark*0.6),
                         (x0 - bulge, ry + rh - gh//2),
                         (x0 + w + bulge, ry + rh - gh//2), gh)
        pygame.draw.line(surf, PINE_T, (x0 - bulge, ry + max(1, int(1*s))),
                         (x0 + w + bulge, ry + max(1, int(1*s))), max(1, int(1.5*s)))
        pygame.draw.polygon(surf, INK, bead, max(1, int(1.5*s)))

    # graduated ring positions (fraction of span from the top) — clustered low
    # and graduating from pale (dark=0) at top to deep dark (dark=1) in the
    # foot-cluster, so visual VALUE-weight pools hard at the bottom.
    for frac, h, dk in ((0.30, 6, 0.0), (0.50, 7, 0.20),
                        (0.66, 8, 0.45), (0.78, 10, 0.72), (0.89, 13, 1.0)):
        ring(top + int(span*frac), h, dark=dk, bulge_mul=1.0)

    if knots:
        # a couple of PRAYER-CLOTH KNOTS bulging off the lower shaft — pale cord
        # wraps that add real silhouette mass low. Two knots, offset sides.
        for kfrac, kside in ((0.66, -1), (0.80, 1)):
            ky = top + int(span*kfrac)
            kw = int(half_w * 1.05)
            kh = int(half_w * 0.85)
            kx = cx + kside * (half_w + int(kw*0.2))
            # the bulging wrapped knot (rounded blob)
            pygame.draw.circle(surf, INK, (kx, ky), kw + max(1, int(2*s)))
            pygame.draw.circle(surf, KNOT, (kx, ky), kw)
            pygame.draw.circle(surf, KNOT_D, (kx + int(kw*0.3), ky + int(kw*0.3)),
                               int(kw*0.5))
            pygame.draw.circle(surf, KNOT_T, (kx - int(kw*0.34), ky - int(kw*0.34)),
                               int(kw*0.3))
            pygame.draw.circle(surf, INK, (kx, ky), kw, max(1, int(1.5*s)))
            # binding line across the knot + two short tails hanging down
            pygame.draw.line(surf, KNOT_D, (kx - int(kw*0.7), ky),
                             (kx + int(kw*0.7), ky), max(1, int(2*s)))
            for tdx in (-int(kw*0.3), int(kw*0.3)):
                pygame.draw.line(surf, INK,
                                 (kx + tdx, ky + int(kw*0.7)),
                                 (kx + tdx, ky + int(kw*0.7) + kh), max(2, int(3*s)))
                pygame.draw.line(surf, KNOT,
                                 (kx + tdx, ky + int(kw*0.7)),
                                 (kx + tdx, ky + int(kw*0.7) + kh - int(2*s)),
                                 max(1, int(2*s)))

    # lichen patch low on the shaft (aged growth pools at the damp foot)
    lr = max(int(5*s), int(half_w * 0.9))
    lichen_patch(surf, x0 + int(half_w*0.4), top + int(span*0.84), lr, s,
                 seed=int(bot) % 89 + 7)


# ── the duck crown: a grumpy sacred DUCK glaring down off the pole ────────────
def duck(surf, cx, cy, s, scale=1.0, lit=False, face_down=False, tuck=False):
    """The grumpy sacred duck. WHY a clean OVAL body with SPARSE feather-courses:
    this is the set's only top-heavy risk, so the body silhouette must read as
    one slim blob first; detail comes only after. The character lives in the
    comic UNDERBITE bill + the big saucer EYE + the heavy indigo neck-band. The
    duck looks DOWN the pole (toward the gap). `scale` shrinks the whole crown
    (the gap-cap duck is ~70%); `lit` brightens the bill + eye for the gap-cap;
    `face_down` flips the glare direction for the upright bottom segment.
    `tuck` pulls the underbite bill fully inside the shaft's vertical envelope —
    used for the gap-cap duck, where any bill overhang at the most-scrutinized
    gap-edge silhouette would read as a snag. Only the eye-glow may break the
    column width on the cap; the bill never does."""
    S = s * scale
    flip = -1 if face_down else 1
    bill_reach = 0.78 if tuck else 1.18   # how far the underbite juts past the head

    # ── body: one clean honey-tan OVAL blob, taller than wide, slim ──────────
    brx = int(34 * S)
    bry = int(46 * S)
    by = cy + int(6 * S)
    rect = pygame.Rect(0, 0, brx*2, bry*2)
    rect.center = (cx, by)
    pygame.draw.ellipse(surf, INK, rect.inflate(int(4*S), int(4*S)))
    pygame.draw.ellipse(surf, BODY, rect)
    # dark core lower-right
    core = pygame.Rect(0, 0, int(brx*1.25), int(bry*1.25))
    core.center = (cx + int(brx*0.36), by + int(bry*0.34))
    pygame.draw.ellipse(surf, BODY_D, core)
    pygame.draw.ellipse(surf, BODY, rect.inflate(-int(brx*1.0), -int(bry*0.4)))
    # top-left rim-sheen crescent
    sh = pygame.Rect(0, 0, int(brx*0.92), int(bry*0.8))
    sh.center = (cx - int(brx*0.36), by - int(bry*0.4))
    pygame.draw.ellipse(surf, BODY_T, sh)
    pygame.draw.ellipse(surf, INK, rect, max(2, int(2*S)))

    # ── SPARSE feather-courses: 3 hard chevron GROOVES down the breast ───────
    # WHY each seam is now an INK-core groove with a bright top-left sheen lip
    # (not a soft BODY_D band): at mid distance the round-1 lowest seam blurred
    # into the body-shade core and smudged. A hard ink core + a thin sheen lip
    # reads as a carved channel that survives downscale; the lowest seam is
    # lifted clear of the body's dark-core ellipse so it stays a crisp groove.
    seam_ys = (by - int(bry*0.26), by + int(bry*0.06), by + int(bry*0.34))
    for i, fy in enumerate(seam_ys):
        fw = int(brx * (0.70 - i*0.10))
        gw = max(2, int(3*S))
        # dark ink core groove (the carved channel)
        pygame.draw.line(surf, INK, (cx - fw, fy),
                         (cx, fy + int(7*S)), gw)
        pygame.draw.line(surf, INK, (cx, fy + int(7*S)),
                         (cx + fw, fy), gw)
        # thin bright sheen lip riding the top edge of the groove
        pygame.draw.line(surf, BODY_T, (cx - fw, fy - int(2*S)),
                         (cx, fy + int(5*S)), max(1, int(1.5*S)))
        pygame.draw.line(surf, BODY_T, (cx, fy + int(5*S)),
                         (cx + fw, fy - int(2*S)), max(1, int(1.5*S)))

    # ── a stubby folded tail-tip kicking off the lower-back (duck read) ──────
    tail_dir = 1
    tail = [(cx + int(brx*0.6), by + int(bry*0.5)),
            (cx + int(brx*1.15), by + int(bry*0.32)),
            (cx + int(brx*0.7), by + int(bry*0.82))]
    triad_blob(surf, BODY, tail,
               sheen_pts=[(cx + int(brx*0.62), by + int(bry*0.5)),
                          (cx + int(brx*0.92), by + int(bry*0.42)),
                          (cx + int(brx*0.7), by + int(bry*0.62))],
               ow=max(1, int(1.5*S)))

    # ── neck + head: head sits high, tucked tight to the axis ────────────────
    # WHY the head is slimmed ~10% from round 1 (hrx 26->23) and its outer
    # envelope pulled inside the shaft+body width: at 32px the head was reading
    # WIDER than the shaft and winning the value fight, so the silhouette tipped
    # toward a top-heavy "lollipop". A narrower dome keeps the top from out-
    # massing the bottom; the eye stays the same big saucer so the read survives.
    hy = cy - int(46 * S)
    hrx = int(23 * S)
    hry = int(23 * S)
    # neck column joining head to body
    neck = [(cx - int(hrx*0.62), hy + int(hry*0.4)),
            (cx + int(hrx*0.62), hy + int(hry*0.4)),
            (cx + int(brx*0.5), by - int(bry*0.5)),
            (cx - int(brx*0.5), by - int(bry*0.5))]
    triad_blob(surf, BODY, neck,
               core_pts=[(cx + int(hrx*0.1), hy + int(hry*0.4)),
                         (cx + int(hrx*0.62), hy + int(hry*0.4)),
                         (cx + int(brx*0.5), by - int(bry*0.5)),
                         (cx + int(brx*0.1), by - int(bry*0.5))],
               sheen_pts=[(cx - int(hrx*0.6), hy + int(hry*0.42)),
                          (cx - int(hrx*0.2), hy + int(hry*0.42)),
                          (cx - int(brx*0.3), by - int(bry*0.5)),
                          (cx - int(brx*0.5), by - int(bry*0.5))],
               ow=max(2, int(2*S)))

    # INDIGO neck-band — a FLAT carved paint mass wrapping the neck (hard edge).
    # WHY a deep-indigo dark CORE under the band: AD ruled the band fine as a
    # ~1px value notch at 32px, but it must downscale to a CRISP DARK separation,
    # never a muddy mid-grey dither. Seating the band's lower half on the deepest
    # indigo guarantees the compressed pixel reads dark; hue legibility is not
    # the band's job, value separation is.
    band_y = hy + int(hry*0.74)
    band_h = int(11 * S)
    band = [(cx - int(brx*0.5), band_y), (cx + int(brx*0.5), band_y),
            (cx + int(brx*0.44), band_y + band_h), (cx - int(brx*0.44), band_y + band_h)]
    triad_blob(surf, INDIGO, band,
               core_pts=[(cx - int(brx*0.5), band_y + int(band_h*0.42)),
                         (cx + int(brx*0.5), band_y + int(band_h*0.42)),
                         (cx + int(brx*0.44), band_y + band_h),
                         (cx - int(brx*0.44), band_y + band_h)],
               sheen_pts=[(cx - int(brx*0.48), band_y + max(1, int(1*S))),
                          (cx - int(brx*0.08), band_y + max(1, int(1*S))),
                          (cx - int(brx*0.1), band_y + int(band_h*0.4)),
                          (cx - int(brx*0.46), band_y + int(band_h*0.4))],
               ow=max(1, int(1.5*S)))
    # deepest-indigo notch line riding the band's lower edge — the value anchor
    pygame.draw.line(surf, INDIGO_D, (cx - int(brx*0.46), band_y + band_h - max(1, int(1*S))),
                     (cx + int(brx*0.46), band_y + band_h - max(1, int(1*S))),
                     max(1, int(2*S)))

    # head dome — honey-tan, sits above the band
    hrect = pygame.Rect(0, 0, hrx*2, hry*2)
    hrect.center = (cx, hy)
    pygame.draw.ellipse(surf, INK, hrect.inflate(int(4*S), int(4*S)))
    pygame.draw.ellipse(surf, BODY, hrect)
    hcore = pygame.Rect(0, 0, int(hrx*1.2), int(hry*1.2))
    hcore.center = (cx + int(hrx*0.34), hy + int(hry*0.3))
    pygame.draw.ellipse(surf, BODY_D, hcore)
    pygame.draw.ellipse(surf, BODY, hrect.inflate(-int(hrx*1.0), -int(hry*0.5)))
    hsh = pygame.Rect(0, 0, int(hrx*0.9), int(hry*0.8))
    hsh.center = (cx - int(hrx*0.36), hy - int(hry*0.4))
    pygame.draw.ellipse(surf, BODY_T, hsh)
    pygame.draw.ellipse(surf, INK, hrect, max(2, int(2*S)))

    # ── grumpy heavy BROW ridge over the eye (the glare) ─────────────────────
    brow_y = hy - int(hry*0.42)
    brow = [(cx - int(hrx*0.85), brow_y),
            (cx + int(hrx*0.5), brow_y - int(4*S)),
            (cx + int(hrx*0.5), brow_y + int(6*S)),
            (cx - int(hrx*0.85), brow_y + int(9*S))]
    triad_blob(surf, BODY_D, brow,
               sheen_pts=[(cx - int(hrx*0.8), brow_y),
                          (cx - int(hrx*0.2), brow_y - int(2*S)),
                          (cx - int(hrx*0.2), brow_y + int(3*S)),
                          (cx - int(hrx*0.8), brow_y + int(4*S))],
               ow=max(1, int(1.5*S)))

    # ── big saucer EYE with warm-amber glow (the soul) ───────────────────────
    ex = cx - int(hrx*0.18)
    ey = hy - int(hry*0.05)
    er = int(13 * S)
    glow_a = 165 if lit else 105
    glow_r = int(er * (2.3 if lit else 1.7))
    glow = pygame.Surface((glow_r*4, glow_r*4), pygame.SRCALPHA)
    for r in range(glow_r, 0, -1):
        a = int(glow_a * (1 - r/glow_r))
        pygame.draw.circle(glow, (*EYEGLOW, a), (glow_r*2, glow_r*2), r)
    surf.blit(glow, (ex - glow_r*2, ey - glow_r*2), special_flags=pygame.BLEND_ADD)
    # carved socket rim
    pygame.draw.circle(surf, INK, (ex, ey), er + max(1, int(2*S)))
    pygame.draw.circle(surf, BODY_D, (ex, ey), er)
    pygame.draw.circle(surf, INK, (ex, ey), er, max(1, int(2*S)))
    # the warm saucer eyeball
    eb = int(er * (0.82 if lit else 0.74))
    pygame.draw.circle(surf, EYEGLOW_D, (ex, ey), eb + max(1, int(1*S)))
    pygame.draw.circle(surf, EYEGLOW, (ex, ey), eb)
    # ink pupil pushed DOWN-forward (glaring down the pole) + hot fleck
    pygame.draw.circle(surf, INK, (ex - int(eb*0.2), ey + int(eb*0.35)),
                       int(eb*0.5))
    pygame.draw.circle(surf, (255, 248, 228),
                       (ex - int(eb*0.4), ey - int(eb*0.2)), max(1, int(eb*0.22)))

    # ── comic UNDERBITE BILL — the signature gag ─────────────────────────────
    # A wide flat duck bill where the LOWER mandible juts past the upper one;
    # bill points slightly DOWN (glaring down the pole). Bill lit on the cap.
    # On the gap-cap (`tuck`), seat the bill base closer to the axis so the
    # whole bill swings inside the shaft's vertical envelope at the gap edge.
    bx = cx - int(hrx*(0.55 if tuck else 0.7))
    bly = hy + int(hry*0.34)            # bill base y on the head
    blen = int(34 * S)
    ureach = blen * (0.86 if tuck else 1.0)
    bup = BILL if not lit else lerp(BILL, EYEGLOW, 0.35)
    # upper mandible (shorter)
    upper = [(bx, bly - int(7*S)),
             (bx - int(ureach), bly - int(2*S)),
             (bx - int(ureach*0.92), bly + int(3*S)),
             (bx, bly + int(2*S))]
    triad_blob(surf, bup, upper,
               core_pts=[(bx, bly - int(2*S)), (bx - int(ureach*0.6), bly + int(1*S)),
                         (bx - int(ureach*0.55), bly + int(3*S)), (bx, bly + int(2*S))],
               ow=max(1, int(1.5*S)))
    # lower mandible (the UNDERBITE — juts further + droops, fatter). On the
    # cap its reach is clamped (`bill_reach`) so the tip never crosses the shaft
    # edge; on the hero it keeps the full comic jut.
    lower = [(bx, bly + int(2*S)),
             (bx - int(blen*bill_reach), bly + int(6*S)),
             (bx - int(blen*(bill_reach-0.06)), bly + int(13*S)),
             (bx + int(2*S), bly + int(11*S))]
    triad_blob(surf, lerp(bup, BILL_D, 0.15), lower,
               sheen_pts=[(bx - int(blen*0.2), bly + int(3*S)),
                          (bx - int(blen*0.8), bly + int(6*S)),
                          (bx - int(blen*0.78), bly + int(8*S)),
                          (bx - int(blen*0.2), bly + int(6*S))],
               ow=max(1, int(1.5*S)))
    # INDIGO bill stripe — flat paint mark across the upper mandible
    pygame.draw.line(surf, INDIGO, (bx - int(2*S), bly - int(3*S)),
                     (bx - int(blen*0.82), bly), max(2, int(3*S)))
    pygame.draw.line(surf, INDIGO_T, (bx - int(2*S), bly - int(4*S)),
                     (bx - int(blen*0.5), bly - int(1*S)), max(1, int(1*S)))
    # nostril dot near the base
    pygame.draw.circle(surf, INK, (bx - int(blen*0.32), bly - int(1*S)),
                       max(1, int(2*S)))
    if lit:
        # gap-cap: a soft warm glow off the bill tip so the cap reads at night
        bglow = pygame.Surface((blen*3, blen*3), pygame.SRCALPHA)
        gr = int(blen*0.8)
        for r in range(gr, 0, -1):
            a = int(120 * (1 - r/gr))
            pygame.draw.circle(bglow, (*EYEGLOW, a), (blen*3//2, blen*3//2), r)
        surf.blit(bglow, (bx - blen - blen*3//2 + int(blen*0.5),
                          bly - blen*3//2 + int(6*S)),
                  special_flags=pygame.BLEND_ADD)


# ── the full hero creature: duck-crowned heaven-pole ──────────────────────────
def draw_sotjang(surf, cx, cy, s):
    """The whole sentinel: a grumpy sacred DUCK perched atop a slim turned-pine
    pole. The pole is BOTTOM-WEIGHTED (graduated lathe rings + low prayer knots)
    so the bird crown never tips the silhouette. `s` is a unit scale around a
    ~250-unit-tall figure."""
    half_w = int(20*s)                  # SLIM shaft (much narrower than its set)
    pole_top = cy - int(40*s)
    pole_bot = cy + int(180*s)
    turned_shaft(surf, cx, pole_top, pole_bot, half_w, s, knots=True)

    # a wide plinth foot grounds the pole (the heaviest bottom mass). WHY it is
    # widened ~18% and given an INK-dark core: at 32px the foot must out-mass
    # the head blob and be the WIDEST, darkest mark on the figure so the
    # silhouette reads as a rooted pole, not a top-heavy lollipop. A taller,
    # splayed plinth + a dark base shadow pool the value firmly at the ground.
    fy0 = pole_bot - int(4*s)
    fy1 = pole_bot + int(22*s)
    foot = [(cx - half_w - int(20*s), fy0),
            (cx + half_w + int(20*s), fy0),
            (cx + half_w + int(11*s), fy1),
            (cx - half_w - int(11*s), fy1)]
    triad_blob(surf, PINE_D, foot,
               core_pts=[(cx - half_w - int(20*s), fy0 + int((fy1-fy0)*0.5)),
                         (cx + half_w + int(20*s), fy0 + int((fy1-fy0)*0.5)),
                         (cx + half_w + int(11*s), fy1),
                         (cx - half_w - int(11*s), fy1)],
               sheen_pts=[(cx - half_w - int(18*s), fy0 + int(2*s)),
                          (cx - int(4*s), fy0 + int(2*s)),
                          (cx - int(4*s), fy0 + int((fy1-fy0)*0.5)),
                          (cx - half_w - int(16*s), fy0 + int((fy1-fy0)*0.5))],
               ow=max(2, int(2*s)))
    # a deep ink base-shadow line under the plinth — the darkest, widest mark,
    # the visual ground the whole pole sits on.
    pygame.draw.line(surf, INK, (cx - half_w - int(20*s), fy1 - max(1, int(2*s))),
                     (cx + half_w + int(20*s), fy1 - max(1, int(2*s))),
                     max(2, int(3*s)))

    # the grumpy duck crowning the pole — perched, glaring down
    duck(surf, cx, pole_top - int(36*s), s, scale=1.0, lit=False)


# ── the pillar: slim shaft + a SMALLER mirrored gap-cap duck ──────────────────
def draw_pillar_segment(surf, cx, top, bot, half_w, s, cap="bottom"):
    """A shaft stretch of the heaven-pole meeting the gap with a SECOND, clearly
    SMALLER (~70%) mirrored DUCK tucked tight to the axis, bill lit. The shaft
    is the same turned pine the creature stands on, so creature == pillar. `cap`
    end faces the gap. WHY the cap duck is shrunk + axis-tucked: this set's only
    top-heavy risk lives at the cap, so the partner-duck is deliberately small
    and centred so it never overhangs."""
    # `cap` names which assembled segment this is: the TOP segment's gap edge is
    # its BOTTOM, the BOTTOM segment's gap edge is its TOP. The lit partner-duck
    # always perches at the gap edge facing INTO the gap.
    duck_room = int(96*s)
    if cap == "top":
        # gap is below: shaft fills the upper reach, duck perches at the bottom
        # edge flipped so it looks DOWN toward the gap.
        shaft_top, shaft_bot = top, bot - duck_room
        duck_cy = bot - duck_room // 2 + int(28*s)
        face_down = True
    else:
        # gap is above: shaft fills the lower reach, duck perches at the top
        # edge upright so it looks UP toward the gap.
        shaft_top, shaft_bot = top + duck_room, bot
        duck_cy = top + duck_room // 2 - int(8*s)
        face_down = False
    turned_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, knots=True)

    # the partner-duck — same duck, drawn into a scratch surface so it can be
    # FLIPPED for the bottom cap (proving the true top<->bottom mirror)
    dsz = int(150*s)
    dbuf = pygame.Surface((dsz, dsz), pygame.SRCALPHA)
    duck(dbuf, dsz//2, dsz//2, s, scale=0.70, lit=True, tuck=True)
    if face_down:
        dbuf = pygame.transform.flip(dbuf, False, True)
    surf.blit(dbuf, (cx - dsz//2, int(duck_cy) - dsz//2))


# ── sky helpers (procedural vertical gradient via per-row fills) ─────────────
def sky(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        surf.fill(lerp(top_col, bot_col, j / max(1, h-1)), (x, y+j, w, 1))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def main():
    W, H = 1040, 900
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("SOTJANG", True, LABEL), (22, 12))
    sheet.blit(font_sm.render(
        "sky-bird sentinel pole  ·  bleached pine + honey-tan duck + flat indigo paint + warm-amber eye  ·  round 2  ·  DARK mass pushed low, head slimmed, bill tucked",
        True, LABEL_DIM), (200, 26))

    # (a) BIG hero sprite ------------------------------------------------------
    hb_w, hb_h = 300, 470
    big = pygame.Surface((hb_w*SS, hb_h*SS), pygame.SRCALPHA)
    draw_sotjang(big, hb_w*SS//2, int(hb_h*SS*0.42), 1.28*SS)
    hero = pygame.transform.smoothscale(big, (hb_w, hb_h))
    hero = grow_outline(hero, INK + (255,), 1)
    sheet.blit(hero, (10, 72))
    sheet.blit(font.render("(a) Hero — duck-crowned heaven-pole", True, LABEL), (16, 548))
    sheet.blit(font_sm.render("grumpy DUCK (underbite bill + saucer eye + indigo band) on a", True, LABEL_DIM), (16, 572))
    sheet.blit(font_sm.render("SLIM pine pole; lathe rings + low knots bottom-weight it; rooted plinth", True, LABEL_DIM), (16, 588))

    # (b) pillar assembled — top segment + gap + bottom segment, MIRRORED ------
    pcx = 460
    seg_half = int(20)
    seg_h = 250
    seg_top_y = 72
    gap_px = 96
    # top segment (cap-duck faces DOWN toward the gap = flipped)
    topbuf = pygame.Surface((150*SS, seg_h*SS), pygame.SRCALPHA)
    draw_pillar_segment(topbuf, 75*SS, 4*SS, (seg_h-4)*SS, seg_half*SS, 1.0*SS, cap="top")
    topimg = pygame.transform.smoothscale(topbuf, (150, seg_h))
    topimg = grow_outline(topimg, INK + (255,), 1)
    sheet.blit(topimg, (pcx - 75, seg_top_y))
    # bottom segment (cap-duck faces UP toward the gap = upright)
    botbuf = pygame.Surface((150*SS, seg_h*SS), pygame.SRCALPHA)
    draw_pillar_segment(botbuf, 75*SS, 4*SS, (seg_h-4)*SS, seg_half*SS, 1.0*SS, cap="bottom")
    botimg = pygame.transform.smoothscale(botbuf, (150, seg_h))
    botimg = grow_outline(botimg, INK + (255,), 1)
    sheet.blit(botimg, (pcx - 75, seg_top_y + seg_h + gap_px))

    # gap guide lines
    gap_y0, gap_y1 = seg_top_y + seg_h, seg_top_y + seg_h + gap_px
    for gy in (gap_y0, gap_y1):
        pygame.draw.line(sheet, (150, 154, 160), (pcx - 92, gy), (pcx + 92, gy), 1)
    sheet.blit(font_sm.render("← gap →", True, LABEL_DIM), (pcx - 24, (gap_y0+gap_y1)//2 - 7))
    by = seg_top_y + 2*seg_h + gap_px + 10
    sheet.blit(font.render("(b) Pillar — MIRRORED", True, LABEL), (pcx - 92, by))
    sheet.blit(font_sm.render("slim turned shaft (rings + knots); SMALLER", True, LABEL_DIM), (pcx - 92, by + 24))
    sheet.blit(font_sm.render("~70% partner-duck cap, bill lit, axis-tucked", True, LABEL_DIM), (pcx - 92, by + 40))

    # (c) TRUE 32px gameplay-scale chips — day sky + night sky -----------------
    panel_x = 660
    pw = W - panel_x - 14
    pygame.draw.rect(sheet, PANEL, (panel_x, 72, pw, 372))
    sheet.blit(font.render("(c) True 32px gameplay chip", True, LABEL), (panel_x + 14, 82))
    sheet.blit(font_sm.render("duck-on-pole silhouette must NOT tip", True, LABEL_DIM), (panel_x + 14, 104))

    # render the WHOLE figure scaled so the full duck+pole spans ~32px tall —
    # this is the true top-heaviness test of the silhouette.
    def chip32():
        cs = 48  # chip canvas (px) — full duck + pole
        buf = pygame.Surface((cs*SS, cs*SS), pygame.SRCALPHA)
        draw_sotjang(buf, cs*SS//2, int(cs*SS*0.46), (32/250.0)*SS)
        img = pygame.transform.smoothscale(buf, (cs, cs))
        return grow_outline(img, INK + (255,), 1)

    chip = chip32()
    cs = chip.get_width()
    chip4 = pygame.transform.scale(chip, (cs*4, cs*4))  # zoom to inspect read

    def chip_row(sky_top, sky_bot, sy, lbl, lbl_col):
        sw, sh = 130, 132
        sx = panel_x + 22
        sky(sheet, (sx, sy, sw, sh), sky_top, sky_bot)
        pygame.draw.rect(sheet, INK, (sx, sy, sw, sh), 1)
        sheet.blit(chip, (sx + sw//2 - cs//2, sy + sh//2 - cs//2))
        sheet.blit(font_sm.render(lbl, True, lbl_col), (sx + 4, sy + sh - 16))
        zx = sx + sw + 18
        zw = cs*4
        if zx + zw > panel_x + pw - 10:
            zw = panel_x + pw - 10 - zx
            chip_z = pygame.transform.scale(chip, (cs*4, cs*4)).subsurface((0, 0, zw, min(cs*4, sh+24)))
            sheet.blit(chip_z, (zx, sy))
        else:
            sheet.blit(chip4, (zx, sy - 6))
        return sx, zx

    cy0 = 132
    chip_row(DAY_SKY_T, DAY_SKY_B, cy0, "day sky", INK)
    sheet.blit(font_sm.render("4× zoom →", True, LABEL_DIM), (panel_x + 22 + 130 + 18, cy0 - 18))
    cy1 = cy0 + 168
    chip_row(NIGHT_T, NIGHT_B, cy1, "night sky", LABEL)
    sheet.blit(font_sm.render("warm-amber eye anchors the night read",
                              True, LABEL_DIM), (panel_x + 22, cy1 + 138))

    # palette swatch row -------------------------------------------------------
    pal_y = 458
    pygame.draw.rect(sheet, PANEL, (panel_x, pal_y, pw, 196))
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 14, pal_y + 10))
    swatches = [
        (PINE, "pale pine"), (PINE_D, "pine shade"),
        (BODY, "honey-tan body"), (BODY_D, "body shade"),
        (INDIGO, "indigo paint"), (INDIGO_D, "deep indigo"),
        (EYEGLOW, "amber eye glow"), (BILL, "bill horn"),
        (LICHEN, "lichen-grey"), (KNOT, "prayer cord"),
        (INK, "ink keyline"),
    ]
    sx, sy = panel_x + 14, pal_y + 40
    for i, (c, name) in enumerate(swatches):
        col = i % 2
        row = i // 2
        rx = sx + col*150
        ry = sy + row*28
        pygame.draw.rect(sheet, INK, (rx-1, ry-1, 22, 22))
        pygame.draw.rect(sheet, c, (rx, ry, 20, 20))
        sheet.blit(font_sm.render(name, True, LABEL), (rx+27, ry+4))

    # construction note panel — full-width strip across the bottom ------------
    note_y = 668
    pygame.draw.rect(sheet, PANEL, (10, note_y, W - 20, 222))
    sheet.blit(font.render("Construction notes", True, LABEL), (26, note_y + 10))
    notes_l = [
        "• Set's ONLY top-finial / bird read — and its only top-heavy RISK,",
        "  so built legibility-first.",
        "• SLIM pine pole bottom-weighted by GRADUATED lathe ring-bands",
        "  (denser low) + two low prayer-cloth KNOTS + plinth foot.",
        "• Body is one clean honey-tan OVAL blob; feather-courses SPARSE",
        "  (3 chevron seams) — slimmed before any detail was added.",
    ]
    notes_r = [
        "• INDIGO neck-band + bill stripe are a FLAT carved PAINT mass",
        "  (hard edge), NOT a glow — kept clear of Yurei blue-cyan.",
        "• Warm-AMBER eye is the one glow; anchors the night read.",
        "• NO cinnabar — separates cleanly from the source Jangseung.",
        "• Cap duck CLEARLY smaller (~70%), bill lit, tucked tight to the",
        "  axis so the gap-cap never overhangs / tips.",
    ]
    for i, line in enumerate(notes_l):
        sheet.blit(font_sm.render(line, True, LABEL_DIM), (26, note_y + 40 + i*19))
    for i, line in enumerate(notes_r):
        sheet.blit(font_sm.render(line, True, LABEL_DIM), (540, note_y + 40 + i*19))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
