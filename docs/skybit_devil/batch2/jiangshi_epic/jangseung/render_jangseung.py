"""
Round-1 concept renderer for JANGSEUNG — the Korean carved guardian TOTEM-POST
(Jiangshi-epic set, concept #4). Headless Pygame; supersample at SS=6 then
smoothscale to match the elevated house grammar (chibi, flat saturated fills,
hard 1-2px ink keyline, dark-core -> flat-fill -> top-left rim-sheen triad, 1px
alpha-grown outline).

WHY jangseung is the purest creature=prop=pillar mirror in the set: a real
jangseung IS a carved wooden post — the creature and the pillar are the same
object. So the shaft is literally "more of the same carved-wood column" with the
cinnabar hanja column + moss patches continuing, and the gap-edge cap is the
folklore-true partner-face (jangseung stand in mirrored male/female pairs). That
makes a clean on-axis top<->bottom mirror trivially true rather than forced.

WHY a cooler SLATE-WOOD base than Zhenmushou's warm cream-wood: the cross-set
fix separates the red->amber arc bosses by VALUE/SATURATION. Jangseung owns a
COOL grey-brown driftwood mass so its thin cinnabar hanja reads as a LINEAR
accent, never a second saturated red mass; moss-teal is the aged-jade lineage
tell; warm-cream eye glow is the one warm focal.

WHY a standalone script: review art must never enter the shipped bundle, so it
lives under docs/ and reuses only colour math, not runtime sprite modules.
"""
import os
import math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Cool weathered slate-wood — clearly greyer/cooler than a warm cream-wood.
WOOD      = (118, 116, 108)   # weathered slate-wood base
# WHY ~10% darker than round 1: on a bright day sky the body value crept toward
# the pale blue and the silhouette edge softened — a darker core re-separates it.
WOOD_D    = ( 64,  64,  64)   # deep slate-wood shade (dark core)
WOOD_T    = (162, 158, 146)   # bleached driftwood rim-sheen helper
WOOD_GRV  = ( 50,  50,  52)   # carved bevel-groove shadow

CINNABAR  = (208,  54,  42)   # cinnabar hanja / face-paint focal (LINEAR accent)
CINNA_D   = (150,  34,  30)   # deep cinnabar shade
CINNA_T   = (236, 110,  92)   # cinnabar rim-sheen

MOSS      = ( 70, 138, 122)   # aged moss-teal patch (jade lineage tell)
MOSS_D    = ( 44,  96,  86)   # deep moss-teal
MOSS_T    = (118, 178, 158)   # moss rim-sheen

EYEGLOW   = (250, 236, 188)   # warm-cream eye glow (the one warm focal)
EYEGLOW_D = (214, 180, 110)   # eye-glow shade ring
TOOTH     = (236, 232, 218)   # bone-cream fangs

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


# ── deterministic moss-patch stipple (procedural, no PRNG state leak) ─────────
def moss_patch(surf, cx, cy, rad, s, seed):
    """A single COMPACT moss-teal cluster centred on (cx, cy) within radius `rad`.
    WHY a tight clustered disc rather than a scattered field: round 1's moss
    drifted OFF the silhouette and read as detached particles. Clustering every
    lobe inside one small radius and anchoring the call site to a groove/glyph
    edge keeps the moss reading as carved-on aged jade, not floating noise. A few
    BIG flat lobes survive 1x downscale where stipple fuzzes to grey."""
    n = 4
    lobes = []
    for i in range(n):
        # cheap hash -> jitter so clusters differ without importing random
        ha = ((seed * 73 + i * 137) % 360) * 3.14159 / 180.0
        hd = ((seed * 51 + i *  29) % 100) / 100.0
        hr = ((seed * 97 + i *  17) % 100) / 100.0
        lx = cx + int(math.cos(ha) * hd * rad * 0.55)
        ly = cy + int(math.sin(ha) * hd * rad * 0.55)
        lr = int((0.34 + 0.30 * hr) * rad)
        lobes.append((lx, ly, lr))
    for (lx, ly, lr) in lobes:
        pygame.draw.circle(surf, INK, (lx, ly), lr + max(1, int(1*s)))
    for (lx, ly, lr) in lobes:
        pygame.draw.circle(surf, MOSS, (lx, ly), lr)
        pygame.draw.circle(surf, MOSS_D, (lx + int(lr*0.3), ly + int(lr*0.3)),
                           int(lr*0.55))
        pygame.draw.circle(surf, MOSS_T, (lx - int(lr*0.35), ly - int(lr*0.35)),
                           max(1, int(lr*0.28)))


# ── one bold cinnabar HANJA glyph-block (the spine unit) ──────────────────────
def hanja_block(surf, cx, cy, w, h, s, motif):
    """ONE chunky keylined cinnabar glyph mark. WHY rebuild from round 1's thin
    tick-ladder: at 32px the ladder smeared to faint red mud. A FEW bold blocks
    (strokes ~+35% thicker) each on a recessed groove with its own 1px INK
    keyline hold their edge on downscale, so the column persists as a rhythmic
    cinnabar SPINE even when the glyph shapes themselves stop resolving. Four
    simple stroke motifs read as 'hanja' tiny without being literal characters."""
    x0, y0 = cx - w // 2, cy - h // 2
    sw = max(3, int(4.0*s))          # bold stroke (~+35% vs round 1's 2-3px)
    # recessed dark groove the glyph sits in (carved-in look) + ink keyline
    pad = max(2, int(3*s))
    pygame.draw.rect(surf, INK, (x0 - pad, y0 - pad, w + pad*2, h + pad*2))
    pygame.draw.rect(surf, WOOD_GRV, (x0 - pad + max(1, int(1*s)),
                                      y0 - pad + max(1, int(1*s)),
                                      w + pad*2 - max(2, int(2*s)),
                                      h + pad*2 - max(2, int(2*s))))

    def hline(yy, x_a=0.0, x_b=1.0):
        pygame.draw.line(surf, CINNABAR, (x0 + int(w*x_a), yy),
                         (x0 + int(w*x_b), yy), sw)

    def vline(xx, y_a=0.0, y_b=1.0):
        pygame.draw.line(surf, CINNABAR, (xx, y0 + int(h*y_a)),
                         (xx, y0 + int(h*y_b)), sw)

    midx, midy = cx, cy
    if motif == 0:        # 王-like: three bars + spine
        hline(y0 + int(h*0.12)); hline(midy); hline(y0 + int(h*0.88))
        vline(midx, 0.12, 0.88)
    elif motif == 1:      # 田-like: box + cross
        pygame.draw.rect(surf, CINNABAR, (x0, y0, w, h), sw)
        hline(midy); vline(midx)
    elif motif == 2:      # 大/天-like: top bar + splayed legs
        hline(y0 + int(h*0.20))
        pygame.draw.line(surf, CINNABAR, (midx, y0 + int(h*0.20)),
                         (x0, y0 + h), sw)
        pygame.draw.line(surf, CINNABAR, (midx, y0 + int(h*0.20)),
                         (x0 + w, y0 + h), sw)
        vline(midx, 0.0, 0.55)
    else:                 # 止-like: spine + foot + side bars
        vline(midx, 0.05, 0.95)
        hline(y0 + int(h*0.40), 0.05, 0.95)
        hline(y0 + int(h*0.95))
        vline(x0 + int(w*0.18), 0.40, 0.95)
    # one top-left rim-sheen fleck so the spine catches the triad light
    pygame.draw.line(surf, CINNA_T, (x0 + int(w*0.08), y0 + int(h*0.10)),
                     (x0 + int(w*0.45), y0 + int(h*0.10)), max(1, int(1.5*s)))


# ── carved-wood column band (the repeatable shaft unit) ───────────────────────
def carved_shaft(surf, cx, top, bot, half_w, s, with_eyes_at=None):
    """One stretch of the totem POST: a slate-wood column with vertical bevel
    grooves, faint grain, a centred cinnabar HANJA column, and moss patches.
    This is what tiles — the creature IS this. `with_eyes_at` (optional y) lights
    a single carved hanja stamp as the gap-mouth glow when used as a cap edge."""
    w = half_w * 2
    x0 = cx - half_w

    # main wood mass — flat fill + cool dark core on the right + bleached sheen
    body = [(x0, top), (x0 + w, top), (x0 + w, bot), (x0, bot)]
    triad_blob(
        surf, WOOD, body,
        core_pts=[(cx + int(half_w*0.25), top), (x0 + w, top),
                  (x0 + w, bot), (cx + int(half_w*0.25), bot)],
        sheen_pts=[(x0, top), (x0 + int(half_w*0.32), top),
                   (x0 + int(half_w*0.32), bot), (x0, bot)],
        ow=max(2, int(2*s)),
    )

    # carved vertical bevel grooves — a few BIG ones so they survive downscale.
    # WHY pulled to the OUTER thirds (not crossing the centre): they now frame
    # the cinnabar spine instead of competing with it, reinforcing the carved
    # WOOD read that separates this totem from a smooth stone-mask survivor.
    groove_xs = (-int(half_w*0.66), -int(half_w*0.34),
                 int(half_w*0.34), int(half_w*0.66))
    for gx in groove_xs:
        pygame.draw.line(surf, WOOD_GRV, (cx + gx, top + int(4*s)),
                         (cx + gx, bot - int(4*s)), max(1, int(2*s)))
        pygame.draw.line(surf, WOOD_T, (cx + gx - max(1, int(2*s)), top + int(4*s)),
                         (cx + gx - max(1, int(2*s)), bot - int(4*s)),
                         max(1, int(1*s)))

    # sparse hard-edged horizontal grain ticks — short flecks against the grooves
    # so the wood reads grained without piling a hatch field that fuzzes at 1x.
    gy = top + int(24*s)
    tick = 0
    while gy < bot - int(12*s):
        gx = groove_xs[tick % 4]
        gw = int(half_w * 0.16)
        pygame.draw.line(surf, WOOD_D, (cx + gx - gw, gy), (cx + gx + gw, gy),
                         max(1, int(1*s)))
        gy += int(40*s)
        tick += 1

    # 1-2 carved horizontal BANDING SEAMS — full-width triad-lit channels that
    # break the long shaft into stacked carved courses (totem wood, not a bar).
    course_h = int(96*s)
    sy = top + course_h
    while sy < bot - int(30*s):
        pygame.draw.line(surf, WOOD_GRV, (x0 + int(3*s), sy),
                         (x0 + w - int(3*s), sy), max(2, int(3*s)))
        pygame.draw.line(surf, WOOD_T, (x0 + int(3*s), sy - max(1, int(2*s))),
                         (x0 + w - int(3*s), sy - max(1, int(2*s))),
                         max(1, int(1*s)))
        sy += course_h

    # centred CINNABAR HANJA spine — a FEW BOLD keylined glyph-BLOCKS (not a thin
    # tick ladder). Spaced so the column reads as a rhythmic cinnabar spine that
    # persists at 32px; kept narrow so red stays a LINEAR accent, never a mass.
    block_w = int(half_w * 0.62)
    block_h = int(34*s)
    pitch   = int(58*s)
    gy = top + int(34*s)
    motif = (int(top) // max(1, pitch)) % 4
    while gy < bot - int(34*s):
        hanja_block(surf, cx, gy, block_w, block_h, s, motif % 4)
        gy += pitch
        motif += 1

    # 2 deliberate moss clusters anchored INSIDE the silhouette at groove/seam
    # edges (where moss actually collects). WHY anchor + clamp: round 1's lobes
    # drifted off the post edge; centring inside the body keeps them carved-on.
    inset = int(half_w * 0.30)
    mr = max(int(5*s), int(half_w * 0.34))
    moss_patch(surf, x0 + inset, top + int(course_h*0.65), mr, s,
               seed=int(top) % 97 + 3)
    moss_patch(surf, cx + half_w - inset, bot - int(course_h*0.5), mr, s,
               seed=int(bot) % 89 + 7)


# ── the gap-edge cap: twin mirrored partner-face ─────────────────────────────
def guardian_face(surf, cx, cy, s, lit=False):
    """The oversized comic-fierce guardian face that fills the post's top third:
    huge BUG EYES, a fat BULB-NOSE, a fanged snaggle GRIN, framed by carved brow
    ridges and topped by the official's HAT-BLOCK. `lit` brightens the eye-glow +
    mouth so the same face works as the GAP-EDGE cap (the partner-face, lit at
    the gap). Big-and-few features = a single clean face read at 1x. WHY no
    limbs: a jangseung is a post — the face IS the whole creature."""

    # face block — a broad slate-wood plaque slightly wider than the shaft
    fw, fh = int(96*s), int(104*s)
    fx0, fy0 = cx - fw // 2, cy - fh // 2
    face = [(fx0 + int(6*s), fy0), (fx0 + fw - int(6*s), fy0),
            (fx0 + fw, fy0 + int(14*s)), (fx0 + fw, fy0 + fh - int(10*s)),
            (fx0 + fw - int(10*s), fy0 + fh), (fx0 + int(10*s), fy0 + fh),
            (fx0, fy0 + fh - int(10*s)), (fx0, fy0 + int(14*s))]
    triad_blob(
        surf, WOOD, face,
        core_pts=[(cx + int(8*s), fy0 + int(6*s)), (fx0 + fw, fy0 + int(14*s)),
                  (fx0 + fw, fy0 + fh - int(10*s)),
                  (fx0 + fw - int(10*s), fy0 + fh), (cx + int(8*s), fy0 + fh)],
        sheen_pts=[(fx0 + int(4*s), fy0 + int(4*s)), (cx - int(6*s), fy0 + int(4*s)),
                   (cx - int(6*s), fy0 + fh - int(16*s)),
                   (fx0 + int(4*s), fy0 + fh - int(18*s))],
        ow=max(2, int(2*s)),
    )

    # heavy carved BROW ridge — one bold furrow that frames the eyes (fierce)
    brow_y = fy0 + int(26*s)
    brow = [(fx0 + int(8*s), brow_y), (cx - int(4*s), brow_y - int(8*s)),
            (cx + int(4*s), brow_y - int(8*s)), (fx0 + fw - int(8*s), brow_y),
            (fx0 + fw - int(8*s), brow_y + int(9*s)),
            (cx, brow_y + int(2*s)),
            (fx0 + int(8*s), brow_y + int(9*s))]
    triad_blob(surf, WOOD_D, brow,
               sheen_pts=[(fx0 + int(10*s), brow_y - int(2*s)),
                          (cx - int(8*s), brow_y - int(7*s)),
                          (cx - int(8*s), brow_y + int(1*s)),
                          (fx0 + int(10*s), brow_y + int(4*s))],
               ow=max(1, int(1.5*s)))
    # cinnabar face-paint stroke down the brow centre (the focal mark)
    pygame.draw.line(surf, CINNABAR, (cx, fy0 + int(2*s)), (cx, brow_y - int(2*s)),
                     max(2, int(3*s)))
    pygame.draw.line(surf, CINNA_T, (cx - int(1*s), fy0 + int(3*s)),
                     (cx - int(1*s), brow_y - int(6*s)), max(1, int(1*s)))

    # huge BUG EYES — bulging domes, warm-cream glow, big & few for the read
    eye_dx = int(24*s)
    eye_y = fy0 + int(46*s)
    er = int(18*s)
    glow_a = 150 if lit else 90
    glow_r = int(er * (2.2 if lit else 1.6))
    glow = pygame.Surface((glow_r*4, glow_r*4), pygame.SRCALPHA)
    for r in range(glow_r, 0, -1):
        a = int(glow_a * (1 - r/glow_r))
        pygame.draw.circle(glow, (*EYEGLOW, a), (glow_r*2, glow_r*2), r)
    for sgn in (-1, 1):
        ex = cx + sgn * eye_dx
        surf.blit(glow, (ex - glow_r*2, eye_y - glow_r*2),
                  special_flags=pygame.BLEND_ADD)
    for sgn in (-1, 1):
        ex = cx + sgn * eye_dx
        # bulging eye socket rim (carved wood ring)
        pygame.draw.circle(surf, INK, (ex, eye_y), er + max(1, int(2*s)))
        pygame.draw.circle(surf, WOOD_D, (ex, eye_y), er)
        pygame.draw.circle(surf, WOOD_T, (ex - int(er*0.4), eye_y - int(er*0.4)),
                           int(er*0.5))
        pygame.draw.circle(surf, INK, (ex, eye_y), er, max(1, int(2*s)))
        # the warm-cream glowing eyeball
        eb = int(er * (0.74 if lit else 0.66))
        pygame.draw.circle(surf, EYEGLOW_D, (ex, eye_y), eb + max(1, int(1*s)))
        pygame.draw.circle(surf, EYEGLOW, (ex, eye_y), eb)
        # ink pupil + tiny hot highlight
        pygame.draw.circle(surf, INK, (ex + int(2*s), eye_y + int(1*s)),
                           int(eb*0.45))
        pygame.draw.circle(surf, (255, 252, 244),
                           (ex - int(eb*0.3), eye_y - int(eb*0.3)),
                           max(1, int(eb*0.22)))

    # fat BULB-NOSE — one big rounded mass dead-centre (the comic anchor)
    ny = fy0 + int(70*s)
    nr = int(15*s)
    pygame.draw.circle(surf, INK, (cx, ny), nr + max(1, int(2*s)))
    pygame.draw.circle(surf, WOOD, (cx, ny), nr)
    pygame.draw.circle(surf, WOOD_D, (cx + int(nr*0.3), ny + int(nr*0.35)),
                       int(nr*0.6))
    pygame.draw.circle(surf, WOOD_T, (cx - int(nr*0.35), ny - int(nr*0.4)),
                       int(nr*0.42))
    pygame.draw.circle(surf, INK, (cx, ny), nr, max(1, int(2*s)))
    # nostril dots
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK, (cx + sgn*int(nr*0.42), ny + int(nr*0.45)),
                           max(1, int(2.5*s)))

    # fanged snaggle GRIN — a wide cinnabar-lined mouth with a few BIG fangs
    my = fy0 + int(92*s)
    mw = int(34*s)
    mh = int(16*s) if lit else int(13*s)
    mouth = [(cx - mw, my - int(3*s)), (cx + mw, my - int(3*s)),
             (cx + int(mw*0.7), my + mh), (cx - int(mw*0.7), my + mh)]
    if lit:
        # gap-lit mouth glows warm from inside
        mglow = pygame.Surface((mw*4, mh*6), pygame.SRCALPHA)
        for r in range(int(mw*1.4), 0, -1):
            a = int(120 * (1 - r/(mw*1.4)))
            pygame.draw.circle(mglow, (*EYEGLOW, a), (mw*2, mh*3), r)
        surf.blit(mglow, (cx - mw*2, my - mh*3 + int(6*s)),
                  special_flags=pygame.BLEND_ADD)
    pygame.draw.polygon(surf, INK, mouth)
    inner = lerp(EYEGLOW, CINNA_D, 0.4) if lit else (40, 26, 30)
    pygame.draw.polygon(surf, inner,
                        [(cx - mw + int(3*s), my - int(1*s)),
                         (cx + mw - int(3*s), my - int(1*s)),
                         (cx + int(mw*0.6), my + mh - int(2*s)),
                         (cx - int(mw*0.6), my + mh - int(2*s))])
    # cinnabar lip lines (the red accent that turns the fang-row into a GRIN).
    # WHY a bolder lip + matching LOWER lip on the lit cap: round 1's cap mouth
    # read as a muddy fang-bone smear at 32px because the warm gap-glow washed
    # out its single thin top lip. Bracketing the row in two bold cinnabar lips
    # gives the cap face the same grin legibility as the hero face.
    lip_w = max(3, int(4*s)) if lit else max(2, int(3*s))
    pygame.draw.line(surf, CINNABAR, (cx - mw, my - int(3*s)),
                     (cx + mw, my - int(3*s)), lip_w)
    pygame.draw.line(surf, CINNA_T, (cx - mw, my - int(4*s)),
                     (cx, my - int(4*s)), max(1, int(1*s)))
    pygame.draw.line(surf, CINNABAR, (cx - int(mw*0.74), my + mh),
                     (cx + int(mw*0.74), my + mh), lip_w)
    # BIG snaggle fangs — top row down, two bottom up, few & chunky
    for fx in (-int(mw*0.62), -int(mw*0.18), int(mw*0.30)):
        tri = [(cx + fx, my - int(2*s)),
               (cx + fx + int(7*s), my - int(2*s)),
               (cx + fx + int(3*s), my + int(8*s))]
        pygame.draw.polygon(surf, TOOTH, tri)
        pygame.draw.polygon(surf, INK, tri, max(1, int(1*s)))
    for fx in (-int(mw*0.40), int(mw*0.18)):
        tri = [(cx + fx, my + mh - int(1*s)),
               (cx + fx + int(7*s), my + mh - int(1*s)),
               (cx + fx + int(3*s), my + mh - int(9*s))]
        pygame.draw.polygon(surf, TOOTH, tri)
        pygame.draw.polygon(surf, INK, tri, max(1, int(1*s)))

    # the tall official's HAT-BLOCK on top (the aristocrat headpiece tell)
    hat_base_y = fy0 - int(2*s)
    hb_w = int(58*s)
    block = [(cx - hb_w//2, hat_base_y),
             (cx + hb_w//2, hat_base_y),
             (cx + int(hb_w*0.34), hat_base_y - int(40*s)),
             (cx - int(hb_w*0.34), hat_base_y - int(40*s))]
    triad_blob(
        surf, WOOD_D, block,
        sheen_pts=[(cx - hb_w//2 + int(2*s), hat_base_y - int(2*s)),
                   (cx - int(hb_w*0.22), hat_base_y - int(2*s)),
                   (cx - int(hb_w*0.20), hat_base_y - int(38*s)),
                   (cx - int(hb_w*0.32), hat_base_y - int(38*s))],
        ow=max(2, int(2*s)),
    )
    # hat brim ledge + a single cinnabar rank-band
    pygame.draw.rect(surf, WOOD, (cx - hb_w//2 - int(4*s), hat_base_y - int(4*s),
                                  hb_w + int(8*s), int(8*s)))
    pygame.draw.rect(surf, INK, (cx - hb_w//2 - int(4*s), hat_base_y - int(4*s),
                                 hb_w + int(8*s), int(8*s)), max(1, int(1.5*s)))
    pygame.draw.line(surf, CINNABAR,
                     (cx - int(hb_w*0.28), hat_base_y - int(22*s)),
                     (cx + int(hb_w*0.28), hat_base_y - int(22*s)), max(2, int(3*s)))
    pygame.draw.line(surf, CINNA_T,
                     (cx - int(hb_w*0.28), hat_base_y - int(23*s)),
                     (cx + int(hb_w*0.10), hat_base_y - int(23*s)), max(1, int(1*s)))
    # tiny finial knob
    pygame.draw.circle(surf, CINNABAR, (cx, hat_base_y - int(40*s)), int(5*s))
    pygame.draw.circle(surf, INK, (cx, hat_base_y - int(40*s)), int(5*s),
                       max(1, int(1*s)))
    pygame.draw.circle(surf, CINNA_T, (cx - int(2*s), hat_base_y - int(42*s)),
                       max(1, int(2*s)))


# ── the full hero creature: face-topped carved post ──────────────────────────
def draw_jangseung(surf, cx, cy, s):
    """The whole guardian: oversized fierce face in the top third atop the tall
    narrow carved POST (the body = the pillar shaft). No limbs. `s` is a unit
    scale around a ~250-unit-tall figure."""
    half_w = int(40*s)
    post_top = cy - int(58*s)
    post_bot = cy + int(150*s)
    # the carved-wood body shaft (continues the same column the pillar tiles)
    carved_shaft(surf, cx, post_top, post_bot, half_w, s)
    # a wider plinth foot grounds the post (bottom-rooted, not top-heavy)
    foot = [(cx - half_w - int(8*s), post_bot - int(4*s)),
            (cx + half_w + int(8*s), post_bot - int(4*s)),
            (cx + half_w + int(4*s), post_bot + int(14*s)),
            (cx - half_w - int(4*s), post_bot + int(14*s))]
    triad_blob(surf, WOOD_D, foot,
               sheen_pts=[(cx - half_w - int(6*s), post_bot - int(2*s)),
                          (cx - int(4*s), post_bot - int(2*s)),
                          (cx - int(4*s), post_bot + int(10*s)),
                          (cx - half_w - int(4*s), post_bot + int(10*s))],
               ow=max(2, int(2*s)))
    # the oversized guardian face filling the top third
    guardian_face(surf, cx, cy - int(96*s), s, lit=False)


# ── the pillar: same carved post, mirrored, with a partner-face gap-cap ──────
def draw_pillar_segment(surf, cx, top, bot, half_w, s, cap="bottom"):
    """A shaft stretch of the totem POST that meets the gap with a twin mirrored
    PARTNER-FACE cap (eyes + mouth LIT at the gap). The shaft is the same carved
    column as the creature body, so creature == pillar. `cap` end faces the gap."""
    # reserve room for the partner-face at the gap end
    face_room = int(118*s)
    if cap == "bottom":
        shaft_top, shaft_bot = top, bot - face_room
        face_cy = bot - face_room // 2 + int(6*s)
        face_dir = 1
    else:
        shaft_top, shaft_bot = top + face_room, bot
        face_cy = top + face_room // 2 - int(6*s)
        face_dir = -1
    carved_shaft(surf, cx, shaft_top, shaft_bot, half_w, s)

    # the partner-face — same guardian face, drawn into a scratch surface so it
    # can be FLIPPED for the top cap (proving the true top<->bottom mirror)
    fsz = int(150*s)
    fbuf = pygame.Surface((fsz, fsz), pygame.SRCALPHA)
    guardian_face(fbuf, fsz//2, fsz//2, s, lit=True)
    if face_dir < 0:
        fbuf = pygame.transform.flip(fbuf, False, True)
    surf.blit(fbuf, (cx - fsz//2, int(face_cy) - fsz//2))


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
    sheet.blit(font_big.render("JANGSEUNG", True, LABEL), (22, 12))
    sheet.blit(font_sm.render(
        "carved guardian totem-post  ·  slate-wood + cinnabar hanja + moss-teal + warm-cream eye glow  ·  round 2  ·  creature IS the pillar",
        True, LABEL_DIM), (210, 26))

    # (a) BIG hero sprite ------------------------------------------------------
    hb_w, hb_h = 300, 470
    big = pygame.Surface((hb_w*SS, hb_h*SS), pygame.SRCALPHA)
    draw_jangseung(big, hb_w*SS//2, int(hb_h*SS*0.46), 1.30*SS)
    hero = pygame.transform.smoothscale(big, (hb_w, hb_h))
    hero = grow_outline(hero, INK + (255,), 1)
    sheet.blit(hero, (10, 72))
    sheet.blit(font.render("(a) Hero — face-topped carved post", True, LABEL), (16, 548))
    sheet.blit(font_sm.render("bug-eyes + bulb-nose + fanged grin fill the top third; cinnabar", True, LABEL_DIM), (16, 572))
    sheet.blit(font_sm.render("hanja column down the front; moss-teal patches; no limbs; rooted plinth", True, LABEL_DIM), (16, 588))

    # (b) pillar assembled — top segment + gap + bottom segment, MIRRORED ------
    pcx = 460
    seg_half = int(34)
    seg_h = 250
    seg_top_y = 72
    gap_px = 96
    # top segment (cap faces DOWN toward the gap = flipped partner-face)
    topbuf = pygame.Surface((150*SS, seg_h*SS), pygame.SRCALPHA)
    draw_pillar_segment(topbuf, 75*SS, 4*SS, (seg_h-4)*SS, seg_half*SS, 1.0*SS, cap="top")
    topimg = pygame.transform.smoothscale(topbuf, (150, seg_h))
    topimg = grow_outline(topimg, INK + (255,), 1)
    sheet.blit(topimg, (pcx - 75, seg_top_y))
    # bottom segment (cap faces UP toward the gap = upright partner-face)
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
    sheet.blit(font_sm.render("tileable carved shaft (hanja + moss); twin", True, LABEL_DIM), (pcx - 92, by + 24))
    sheet.blit(font_sm.render("partner-face cap, eyes/mouth lit at gap", True, LABEL_DIM), (pcx - 92, by + 40))

    # (c) TRUE 32px gameplay-scale chips — day sky + night sky -----------------
    panel_x = 660
    pw = W - panel_x - 14
    pygame.draw.rect(sheet, PANEL, (panel_x, 72, pw, 372))
    sheet.blit(font.render("(c) True 32px gameplay chip", True, LABEL), (panel_x + 14, 82))
    sheet.blit(font_sm.render("one big bulb-nose / bug-eye face read", True, LABEL_DIM), (panel_x + 14, 104))

    # render at a true ~32px FACE read — the gameplay collision shows the
    # face-topped cap end, so the chip frames the FACE (not the long shaft).
    def chip32():
        cs = 44  # chip canvas (px) — face + a sliver of post under it
        buf = pygame.Surface((cs*SS, cs*SS), pygame.SRCALPHA)
        # centre the FACE in the chip; scale so the face spans ~32px
        draw_jangseung(buf, cs*SS//2, int(cs*SS*1.06), (32/96.0)*SS)
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
        # true-size chip centred in the sky tile
        sheet.blit(chip, (sx + sw//2 - cs//2, sy + sh//2 - cs//2))
        sheet.blit(font_sm.render(lbl, True, lbl_col), (sx + 4, sy + sh - 16))
        # 4x zoom to the right, clamped inside the panel
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
    sheet.blit(font_sm.render("warm-cream eyes/mouth anchor the night read",
                              True, LABEL_DIM), (panel_x + 22, cy1 + 138))

    # palette swatch row -------------------------------------------------------
    pal_y = 458
    pygame.draw.rect(sheet, PANEL, (panel_x, pal_y, pw, 196))
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 14, pal_y + 10))
    swatches = [
        (WOOD, "slate-wood"), (WOOD_D, "deep slate"),
        (WOOD_T, "driftwood sheen"), (WOOD_GRV, "bevel groove"),
        (CINNABAR, "cinnabar"), (CINNA_D, "deep cinnabar"),
        (MOSS, "moss-teal"), (MOSS_D, "deep moss"),
        (EYEGLOW, "eye-glow cream"), (TOOTH, "fang bone"),
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
        "• Cooler/greyer SLATE-WOOD vs Zhenmushou's warm cream-wood —",
        "  the cross-set value/saturation separation.",
        "• Cinnabar is a thin LINEAR accent only: brow stroke, hanja",
        "  column, lip line, hat band — never a second red mass.",
        "• Moss-teal = the aged-jade lineage tell (clustered lobes,",
        "  not noise, so it survives downscale).",
    ]
    notes_r = [
        "• Warm-cream EYE GLOW is the one warm focal; it lifts the",
        "  partner-face cap so the gap reads at night.",
        "• Big & few face features (2 eyes, 1 nose, 5 fangs) = one",
        "  clean face read at 32px; no crack-fuzz piled on.",
        "• Creature IS the pillar: the hero post body == the shaft the",
        "  pillar tiles; cap = folklore-true mirrored partner-face.",
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
