"""
Round-1 concept renderer for LAPIS NAVIGATOR KING — skull-KINGS II brood, the
celestial-cartographer king. Headless Pygame; ELEVATED pipeline (SS=6 ->
smoothscale) so the thin orrery bands survive the downscale. Procedural-only
(flat triad fills + 1-2px ink keyline; no gradients/PNGs).

WHY this KIND (the de-collision lock): the sibling Sunfire Solar-Khan is a
FILLED, VERTICAL, CIRCULAR sun-disc. This king is the deliberate inverse — an
OPEN, WIDE, HORIZONTAL lens of THIN crossing rings with SKY SHOWING THROUGH. The
silhouette is a flattened horizontal ellipse (aspect ~1.6:1, no rounder), so the
two read as opposites at a glance: a solid hot circle vs. an airy wide armillary.

WHY the rings stay FEW + THIN: the gate's focal is the white-gold STAR-SKULL the
two INNER arms cup at the chest. If the orrery bands crowded the lens they would
bury that focal; instead 3 thin ultramarine bands define the ellipse and leave
the centre open, so the cradled star is the single brightest pixel inside the
lens. Above the head, at the ring's APEX (the celestial pole-star), sits a small
LAPIS skull — the above-head crown tell.

WHY the gold-pyrite ticks are ROBE TEXTURE, not sparkles: they are laid in
ordered diagonal rows ACROSS the lapis robe (a star-chart weave), never scattered
like coin-glints, so the robe reads as flecked lapis cloth and the gold never
becomes a competing warm mass against the white-gold star.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helper idioms, not the
runtime sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# -- PINNED PALETTE ------------------------------------------------------------
LAPIS     = ( 36,  64, 148)   # deep lapis robe (the dominant cool mass)
LAPIS_D   = ( 22,  40, 102)   # lapis shade / robe folds
LAPIS_DD  = ( 14,  26,  70)   # deepest lapis hollow
LAPIS_SH  = ( 74, 110, 196)   # lapis top-left rim-sheen
PYRITE    = (228, 196, 108)   # gold-pyrite ticks (ROBE TEXTURE rows, not sparkle)
PYRITE_D  = (168, 138,  62)   # pyrite shade
BONE      = (200, 206, 216)   # cool bone (skull head, hands, ring-apex skull)
BONE_D    = (150, 158, 176)   # bone shade
BONE_DD   = ( 96, 104, 126)   # deepest bone hollow (sockets)
BONE_SH   = (236, 240, 248)   # bone top-left sheen
# ring band raised in value + saturation so the wide-lens OUTLINE survives the
# 32px downscale against BOTH skies (was too dim/thin -> vanished into a blob).
ULTRA     = ( 92, 142, 244)   # ultramarine ring band (the orrery metal), brighter
ULTRA_BR  = (180, 210, 255)   # ring sheen
ULTRA_D   = ( 30,  56, 132)   # ring shadow
ULTRA_RIM = (236, 244, 255)   # near-white rim-light edge (the 32px survival key)
# the SINGLE focal — the cradled STAR-SKULL (white-gold glow, brightest pixel).
STAR      = (250, 236, 168)   # star-skull warm base
STAR_BR   = (255, 248, 214)   # star-skull bright
STAR_HOT  = (255, 255, 246)   # hottest star core (must be the brightest pixel)
STAR_D    = (210, 180,  96)   # star rim / shade
# the ring-apex LAPIS skull crown (cool, NOT the focal — a small blue tell)
APEX      = ( 60,  96, 196)   # lapis-skull apex base
APEX_BR   = (118, 158, 236)   # apex sheen
APEX_D    = ( 30,  52, 122)   # apex socket
INK       = ( 28,  22,  30)   # ink keyline

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


def bone_limb(surf, p0, p1, p2, thick, s, joint=True, col=BONE):
    for (a, b) in ((p0, p1), (p1, p2)):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * thick / 2, dx / L * thick / 2
        quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
        triad_blob(surf, col, quad,
                   sheen_pts=[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                              (b[0] + nx * 0.3, b[1] + ny * 0.3),
                              (a[0] + nx * 0.3, a[1] + ny * 0.3)],
                   ow=max(1, int(thick * 0.18)))
    if joint:
        triad_circle(surf, col, p1, int(thick * 0.62), ow=max(1, int(1.2 * s)),
                     core=False)


# -- the bright cradled STAR-SKULL (the focal) ---------------------------------
def star_skull(surf, cx, cy, r, s):
    """The white-gold STAR-SKULL the two inner arms cup at the chest. WHY a
    skull rendered in radiant white-gold rather than a plain orb: it carries the
    skull-KINGS lineage tell AND is the single brightest point. Layered halos +
    a hot near-white core keep its peak luminance above every other element so
    the eye lands here first, inside the open lens."""
    # WHY a wider, brighter, more opaque halo stack now: at 32px the cradled
    # star is the warm focal that must still read as a bright POINT at the chest
    # centre; the round-1 halo was too faint/small to survive the downscale.
    for (rr, a) in ((r * 2.7, 44), (r * 1.95, 78), (r * 1.4, 130), (r * 1.06, 200)):
        halo = pygame.Surface((int(rr * 2) + 4, int(rr * 2) + 4), pygame.SRCALPHA)
        pygame.draw.circle(halo, STAR_BR + (a,), (int(rr) + 2, int(rr) + 2), int(rr))
        surf.blit(halo, (cx - int(rr) - 2, cy - int(rr) - 2))
    # cranium
    pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(1.2 * s)))
    pygame.draw.circle(surf, STAR_D, (cx, cy), r)
    pygame.draw.circle(surf, STAR, (cx, cy), int(r * 0.9))
    pygame.draw.circle(surf, STAR_BR, (cx - int(r * 0.2), cy - int(r * 0.24)),
                       int(r * 0.6))
    pygame.draw.circle(surf, STAR_HOT, (cx - int(r * 0.22), cy - int(r * 0.26)),
                       max(1, int(r * 0.30)))
    # jaw
    pygame.draw.polygon(surf, STAR_D,
                        [(cx - int(r * 0.5), cy + int(r * 0.55)),
                         (cx + int(r * 0.5), cy + int(r * 0.55)),
                         (cx + int(r * 0.34), cy + int(r * 0.98)),
                         (cx - int(r * 0.34), cy + int(r * 0.98))])
    # two ink sockets + nasal so it reads as a skull even when tiny
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (cx + sgn * int(r * 0.38), cy - int(r * 0.04)),
                           max(1, int(r * 0.24)))
    pygame.draw.polygon(surf, INK,
                        [(cx - int(r * 0.1), cy + int(r * 0.18)),
                         (cx + int(r * 0.1), cy + int(r * 0.18)),
                         (cx, cy + int(r * 0.42))])


# -- the small LAPIS skull at the ring-apex (the above-head crown tell) --------
def apex_skull(surf, cx, cy, r, s):
    """The cool blue pole-star skull crowning the orrery apex. WHY kept lapis +
    dim (never warm): it is the crown/tell, not the focal — the warmth belongs
    to the cradled star alone. A small cool skull above the head reads at 32px
    as 'a blue dot at the ring's top' without stealing the centre's heat.
    WHY a pale bone halo ring around it now: a bare lapis nub against the night
    sky (also bluish) dissolved at 32px; a thin near-white bone halo gives the
    apex skull a high-contrast edge so it survives as a distinct crown nub
    without going warm and competing with the cradled star."""
    halo_r = r + max(2, int(2.2 * s))
    hsurf = pygame.Surface((halo_r * 2 + 4, halo_r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(hsurf, BONE_SH + (225,), (halo_r + 2, halo_r + 2), halo_r)
    pygame.draw.circle(hsurf, (0, 0, 0, 0), (halo_r + 2, halo_r + 2),
                       max(1, halo_r - max(1, int(1.6 * s))))
    surf.blit(hsurf, (cx - halo_r - 2, cy - halo_r - 2))
    pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(1.0 * s)))
    pygame.draw.circle(surf, APEX_D, (cx, cy), r)
    pygame.draw.circle(surf, APEX, (cx, cy), int(r * 0.88))
    pygame.draw.circle(surf, APEX_BR, (cx - int(r * 0.26), cy - int(r * 0.3)),
                       max(1, int(r * 0.34)))
    pygame.draw.polygon(surf, APEX_D,
                        [(cx - int(r * 0.46), cy + int(r * 0.5)),
                         (cx + int(r * 0.46), cy + int(r * 0.5)),
                         (cx + int(r * 0.3), cy + int(r * 0.92)),
                         (cx - int(r * 0.3), cy + int(r * 0.92))])
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (cx + sgn * int(r * 0.38), cy),
                           max(1, int(r * 0.24)))


# -- one thin ultramarine orrery band (an open ring arc, sky showing through) --
def ring_band(surf, cx, cy, rx, ry, s, tilt=0.0, lw=None, hero=False):
    """A single ultramarine band of the wide armillary, drawn as an open
    elliptical ring (no fill) so sky shows through. WHY ellipses, not circles:
    each band reads as a great-circle of the celestial sphere seen edge-on,
    which is what makes the whole assembly a flattened HORIZONTAL lens rather
    than a filled disc. WHY it is now THICKER with a full near-white RIM-LIGHT
    (not a partial sheen): at 32px a thin low-value band is the first thing the
    downscale eats, leaving a blob that collides with the sun-Khan's filled
    disc. A bright rim run all the way around the band keeps the OPEN ellipse
    OUTLINE legible at gameplay scale while the band stays an open ring."""
    if lw is None:
        lw = max(3, int(3.6 * s))
    pts_out = []
    cos_t, sin_t = math.cos(tilt), math.sin(tilt)
    for k in range(72):
        a = math.radians(k * 5)
        ex, ey = math.cos(a) * rx, math.sin(a) * ry
        # rotate the ellipse by tilt so bands cross each other
        rxp = ex * cos_t - ey * sin_t
        ryp = ex * sin_t + ey * cos_t
        pts_out.append((cx + rxp, cy + ryp))
    # ink keyline under the band, the shadow body, the bright band, then a
    # near-white RIM run around the WHOLE ellipse so the outline survives 32px.
    rim = max(1, int(1.3 * s))
    pygame.draw.polygon(surf, INK, pts_out, lw + max(2, int(2.0 * s)))
    pygame.draw.polygon(surf, ULTRA_D, pts_out, lw + max(1, int(1.0 * s)))
    pygame.draw.polygon(surf, ULTRA, pts_out, lw)
    pygame.draw.polygon(surf, ULTRA_RIM, pts_out, rim)
    # an extra upper-left sheen run reinforces the 3-D read at hero scale only
    if hero:
        sheen = [p for p in pts_out if p[1] < cy and p[0] < cx + rx * 0.3]
        if len(sheen) >= 2:
            pygame.draw.lines(surf, ULTRA_BR, False, sheen, max(1, int(1.4 * s)))


# -- the gold-pyrite ROBE TEXTURE (ordered diagonal star-chart rows) -----------
def pyrite_weave(surf, pts, s, step):
    """Lay ordered diagonal rows of tiny pyrite ticks INSIDE a robe polygon.
    WHY a clipped, regular weave instead of random dots: scattered gold reads as
    coin-sparkle and competes with the star; rows of fixed-pitch ticks read as
    woven star-chart cloth — texture, not glints — so the robe stays one mass."""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    clip = pygame.Surface((int(x1 - x0) + 4, int(y1 - y0) + 4), pygame.SRCALPHA)
    local = [(p[0] - x0 + 2, p[1] - y0 + 2) for p in pts]
    diag = int(step)
    # diagonal grid of ticks, drawn onto a robe-shaped clip then blitted back
    y = 0
    row = 0
    while y < clip.get_height():
        off = (diag // 2) if row % 2 else 0
        x = off
        while x < clip.get_width():
            pygame.draw.circle(clip, PYRITE_D, (x + 1, y + 1), max(1, int(0.9 * s)))
            pygame.draw.circle(clip, PYRITE, (x, y), max(1, int(0.7 * s)))
            x += diag
        y += diag
        row += 1
    mask = pygame.Surface(clip.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), local)
    clip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(clip, (int(x0) - 2, int(y0) - 2))


# -- the navigator king inside his wide orrery lens ---------------------------
def draw_king(surf, cx, cy, s):
    # the WIDE HORIZONTAL ellipse — half-extents (rx clearly > ry => lens, ~1.6:1)
    rx = int(78 * s)
    ry = int(46 * s)
    apex = (cx, cy - ry)             # ring-apex = celestial pole-star
    pole_l = (cx - rx, cy)           # west pole (left arm grips)
    pole_r = (cx + rx, cy)           # east pole (right arm grips)

    # === BACK ARC of the lens (behind the body so the lens wraps the king) ====
    # WHY draw the far halves first, body next, near halves last: this is the
    # depth cue that sells an open 3-D armillary the body sits INSIDE of.
    # WHY only TWO bands now (one wide HORIZONTAL + one crossing) instead of
    # three: at 32px three crossing arcs muddy into a blob; cutting to the
    # fewest that still say "armillary" keeps the wide horizontal LENS the
    # single loudest silhouette element. The horizontal band is drawn thickest.
    back = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    ring_band(back, cx, cy, rx, ry, s, tilt=0.0,
              lw=max(3, int(4.4 * s)), hero=True)               # the loud lens
    ring_band(back, cx, cy, int(rx * 0.62), ry, s, tilt=math.radians(26),
              lw=max(3, int(3.0 * s)), hero=True)               # one crossing arc
    # clip the back surface to ABOVE the body waistline so its lower arcs hide
    surf.blit(back, (0, 0))

    # === TORSO / ROBE (the dominant lapis mass) ===============================
    head_c = (cx, cy - int(20 * s))
    hr = int(15 * s)
    shoulder_y = cy - int(4 * s)
    hem_y = cy + int(40 * s)
    robe = [(cx - int(10 * s), shoulder_y - int(2 * s)),
            (cx + int(10 * s), shoulder_y - int(2 * s)),
            (cx + int(30 * s), hem_y),
            (cx + int(16 * s), hem_y + int(6 * s)),
            (cx, hem_y + int(2 * s)),
            (cx - int(16 * s), hem_y + int(6 * s)),
            (cx - int(30 * s), hem_y)]
    triad_blob(surf, LAPIS, robe,
               core_pts=[(cx + int(2 * s), shoulder_y),
                         (cx + int(28 * s), hem_y - int(2 * s)),
                         (cx + int(14 * s), hem_y + int(4 * s)),
                         (cx + int(2 * s), hem_y)],
               sheen_pts=[(cx - int(10 * s), shoulder_y),
                          (cx - int(2 * s), shoulder_y),
                          (cx - int(18 * s), hem_y - int(4 * s)),
                          (cx - int(28 * s), hem_y - int(2 * s))],
               ow=max(1, int(1.8 * s)))
    # robe fold shadows (thin, keep the mass cohesive)
    for fx in (-12, 0, 12):
        pygame.draw.line(surf, LAPIS_DD,
                         (cx + int(fx * s), shoulder_y + int(6 * s)),
                         (cx + int(fx * 1.7 * s), hem_y - int(2 * s)),
                         max(1, int(1.4 * s)))
    # gold-pyrite weave laid across the robe (ROBE TEXTURE, ordered rows)
    pyrite_weave(surf, robe, s, step=int(9 * s))

    # === FOUR ARMS ============================================================
    # outer two GRIP the ring at its horizontal poles (the armspan);
    # inner two CUP the star-skull at the chest.
    arm_th = int(6 * s)
    chest = (cx, cy + int(8 * s))
    star_c = (cx, cy + int(6 * s))
    star_r = int(15 * s)   # enlarged so the warm focal point survives at 32px

    # OUTER arms -> reach to the poles (drawn first, behind robe edges read ok)
    for sgn in (-1, 1):
        sh = (cx + sgn * int(11 * s), shoulder_y + int(2 * s))
        el = (cx + sgn * int(40 * s), cy - int(8 * s))
        grip = (pole_r if sgn > 0 else pole_l)
        bone_limb(surf, sh, el, grip, arm_th, s, col=BONE)
        # a small gripping hand wrapping the pole
        triad_circle(surf, BONE, grip, int(4 * s), ow=max(1, int(1.0 * s)),
                     core=False)
        for fi in range(3):
            fa = -0.5 + fi * 0.5
            pygame.draw.line(surf, BONE_D,
                             (grip[0], grip[1]),
                             (grip[0] - sgn * int(3 * s),
                              grip[1] + int((fa - 0.2) * 5 * s)),
                             max(1, int(1.4 * s)))

    # === STAR-SKULL focal (cupped at the chest), drawn before inner hands =====
    star_skull(surf, star_c[0], star_c[1], star_r, s)

    # INNER arms -> cup the star from below/sides
    for sgn in (-1, 1):
        sh = (cx + sgn * int(8 * s), shoulder_y + int(6 * s))
        el = (cx + sgn * int(22 * s), cy + int(16 * s))
        hand = (star_c[0] + sgn * int(11 * s), star_c[1] + int(10 * s))
        bone_limb(surf, sh, el, hand, arm_th, s, col=BONE)
        # cupping fingers curling under the star
        cup = [(hand[0], hand[1] - int(3 * s)),
               (hand[0] - sgn * int(2 * s), hand[1] + int(2 * s)),
               (star_c[0] + sgn * int(4 * s), star_c[1] + int(star_r * 0.9)),
               (star_c[0] - sgn * int(1 * s), star_c[1] + int(star_r * 1.05)),
               (hand[0] - sgn * int(6 * s), hand[1] + int(4 * s))]
        triad_blob(surf, BONE, cup,
                   sheen_pts=[(hand[0], hand[1] - int(3 * s)),
                              (hand[0] - sgn * int(1 * s), hand[1]),
                              (star_c[0] + sgn * int(4 * s),
                               star_c[1] + int(star_r * 0.9))],
                   ow=max(1, int(1.1 * s)))

    # === SKULL HEAD ===========================================================
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.3)),
                           int(hr * 0.26))
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.06)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.36))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.30))
        # a faint ultramarine pin in the socket (cool eye-glint, not warm)
        pygame.draw.circle(surf, ULTRA_D, (ex, ey), int(hr * 0.16))
        pygame.draw.circle(surf, ULTRA, (ex, ey + int(1 * s)), max(1, int(hr * 0.09)))
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.13), head_c[1] + int(hr * 0.3)),
                         (head_c[0] + int(hr * 0.13), head_c[1] + int(hr * 0.3)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    my = head_c[1] + int(hr * 0.74)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.42), my),
                     (head_c[0] + int(hr * 0.42), my + int(hr * 0.06)),
                     max(1, int(2 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, INK,
                         (head_c[0] + int(k * hr * 0.18), my - int(hr * 0.04)),
                         (head_c[0] + int(k * hr * 0.18), my + int(hr * 0.1)),
                         max(1, int(1 * s)))

    # === NEAR ARC of the outer ring (in front of the body -> lens wraps king) =
    front = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    ring_band(front, cx, cy, rx, ry, s, tilt=0.0,
              lw=max(3, int(4.4 * s)), hero=True)
    # mask the front surface to only the LOWER half so it crosses in front of
    # the hem but the upper arc already sits behind the head.
    fmask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(fmask, (255, 255, 255, 255),
                     (0, cy + int(2 * s), surf.get_width(), surf.get_height()))
    front.blit(fmask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(front, (0, 0))

    # === RING-APEX LAPIS SKULL (the above-head crown) =========================
    apex_skull(surf, apex[0], apex[1] - int(2 * s), int(8 * s), s)


# -- the pillar: a stacked column of orrery-lens rings + robe band ------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """A vertical stack of the king's OWN forms made into a pillar: a paired
    ultramarine ring-stack threaded on a lapis core, capped by a wide ring-lens
    cradling a star at the gap end. WHY this clones the hero's vocabulary: the
    pillar must read as the same creature's architecture (rings + lapis + a
    glowing star tell), mirrored cleanly top<->bottom on a single axis."""
    pygame.draw.rect(surf, INK, (cx - int(4 * s), top, int(8 * s), bot - top))
    pygame.draw.rect(surf, LAPIS_D, (cx - int(3 * s), top, int(6 * s), bot - top))

    pitch = int(28 * s)
    cap_room = int(44 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    while y <= b1:
        # a wide ring rung threaded on the lapis core (an orrery band)
        ring_band(surf, cx, y, int(15 * s), int(7 * s), s, lw=max(3, int(3.0 * s)))
        # lapis bead at the core with a pyrite tick (robe-texture echo)
        triad_circle(surf, LAPIS, (cx, y), int(5 * s), ow=max(1, int(1.0 * s)),
                     core=False, sheen=False)
        pygame.draw.circle(surf, PYRITE, (cx, y - int(1 * s)), max(1, int(1.2 * s)))
        y += pitch

    cap_y = (bot - int(28 * s)) if cap == "bottom" else (top + int(28 * s))
    fan_dir = -1 if cap == "bottom" else 1
    # the wide ring-lens cap (the hero's signature) cradling a star
    ring_band(surf, cx, cap_y, int(22 * s), int(12 * s), s,
              lw=max(3, int(3.6 * s)), hero=True)
    ring_band(surf, cx, cap_y, int(15 * s), int(12 * s), s, tilt=math.radians(28),
              lw=max(3, int(2.6 * s)), hero=True)
    star_y = cap_y
    star_skull(surf, cx, star_y, int(9 * s), s)
    # a small lapis apex skull at the OUTWARD tip (mirrors the crown)
    apex_skull(surf, cx, cap_y + fan_dir * int(13 * s), int(5 * s), s)


# -- compose the review sheet -------------------------------------------------
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_king(big, draw_cx * SS, draw_cy * SS, scale * SS)
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
    sheet.blit(font_big.render("LAPIS NAVIGATOR KING", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "skull-KINGS II  ·  king inside a WIDE HORIZONTAL orrery-lens (open, thin rings, sky through) · "
        "4 arms: outer GRIP poles, inner CUP star-skull · gold-flecked lapis robe · lapis apex-skull crown · round 2",
        True, LABEL_DIM), (320, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(380, 470, 190, 240, 1.85)
    sheet.blit(hero, (8, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (120, 566))
    sheet.blit(font_sm.render("WIDE flattened horizontal ellipse of THIN ultramarine bands (sky shows through);", True, LABEL_DIM), (10, 590))
    sheet.blit(font_sm.render("outer 2 arms grip the poles, inner 2 CUP the white-gold STAR-SKULL = single focal;", True, LABEL_DIM), (10, 606))
    sheet.blit(font_sm.render("lapis robe with gold-pyrite WEAVE rows; small lapis skull at the ring-apex (crown).", True, LABEL_DIM), (10, 622))

    # === (b) PILLAR assembled — mirrored ======================================
    pcx = 480
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
    sheet.blit(font.render("Pillar — orrery ring-stack", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("lapis core threaded with thin ultramarine ring-rungs;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("wide ring-lens cap cradles a star + lapis apex-skull tip", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, bottom-rooted)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night sky + SILHOUETTE proof =============
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_king(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        if night:
            base = grow_outline(small, ULTRA_RIM + (235,), 2)
            return grow_outline(base, INK + (210,), 1)
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
    sheet.blit(font_sm.render("32px on night sky (bright rim)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # silhouette proof — blacked-out hero so the wide-lens read is checked
    def silhouette():
        big = pygame.Surface((180 * SS, 200 * SS), pygame.SRCALPHA)
        draw_king(big, 90 * SS, 100 * SS, 1.15 * SS)
        small = pygame.transform.smoothscale(big, (180, 200))
        mask = pygame.mask.from_surface(small)
        sil = pygame.Surface((180, 200), pygame.SRCALPHA)
        solid = mask.to_surface(setcolor=(18, 18, 20, 255), unsetcolor=(0, 0, 0, 0))
        sil.blit(solid, (0, 0))
        return sil

    sil_x = panel_x + 196
    pygame.draw.rect(sheet, (210, 212, 216), (sil_x, day_y, 180, 200))
    pygame.draw.rect(sheet, INK, (sil_x, day_y, 180, 200), 1)
    sheet.blit(silhouette(), (sil_x, day_y))
    sheet.blit(font_sm.render("silhouette proof", True, LABEL_DIM), (sil_x, day_y + 204))
    sheet.blit(font_sm.render("(wide horizontal ring-lens)", True, LABEL_DIM), (sil_x, day_y + 220))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = sil_x + 196
    if px2 + 56 < W - 14:
        vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
        pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
        sheet.blit(pc, (px2 + 6, day_y + 10))
        vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
        pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
        sheet.blit(pc, (px2 + 6, night_y + 10))
        sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (LAPIS, "deep lapis robe"), (LAPIS_D, "lapis shade"),
        (PYRITE, "gold-pyrite tick"), (ULTRA, "ultramarine ring"),
        (BONE, "cool bone"), (BONE_DD, "bone socket"),
        (STAR, "star-skull"), (STAR_HOT, "star hot core"),
        (APEX, "lapis apex-skull"), (INK, "ink keyline"),
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
        "LAPIS NAVIGATOR KING: OPEN wide-horizontal armillary lens (thin rings, sky through) — the inverse of a filled vertical sun-disc.  "
        "Inner hands CUP the white-gold star-skull (single brightest pixel); lapis apex-skull crowns the pole.  SS=6 supersample -> smoothscale · procedural-only.",
        True, LABEL_DIM), (24, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    self_check()


def self_check():
    """Verify (1) the brightest pixel sits inside the white-gold star-skull, and
    (2) the silhouette is a WIDE horizontal mass (bbox wider than tall) so it
    can't be confused with the filled vertical sun-disc sibling."""
    surf = pygame.Surface((460, 460), pygame.SRCALPHA)
    draw_king(surf, 230, 230, 2.0)
    px = pygame.surfarray.pixels3d(surf)
    a = pygame.surfarray.pixels_alpha(surf)
    w, h = surf.get_size()
    best_lum, best_xy = -1, (0, 0)
    minx, maxx, miny, maxy = w, 0, h, 0
    for x in range(0, w, 2):
        for yy in range(0, h, 2):
            if a[x, yy] < 40:
                continue
            minx, maxx = min(minx, x), max(maxx, x)
            miny, maxy = min(miny, yy), max(maxy, yy)
            r, g, b = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > best_lum:
                best_lum, best_xy = lum, (x, yy)
    bx, by = best_xy
    r, g, b = int(px[bx, by][0]), int(px[bx, by][1]), int(px[bx, by][2])
    is_star = (r > 220 and g > 210 and b > 150)  # near-white warm star core
    bw, bh = (maxx - minx), (maxy - miny)
    del px, a
    print("self-check: brightest pixel @", best_xy, "rgb", (r, g, b),
          "lum %.0f" % best_lum, "-> star-core?", is_star)
    print("self-check: bbox %dx%d  aspect %.2f  -> wide-horizontal? %s"
          % (bw, bh, bw / max(1, bh), bw > bh * 1.3))


if __name__ == "__main__":
    main()
