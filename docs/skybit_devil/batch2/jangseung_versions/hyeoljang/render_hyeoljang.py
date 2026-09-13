"""
Round-1 concept renderer for HYEOLJANG — the tongue-out warrior guardian post
(carved-WOOD spin-off boss off the shipped Jangseung). Headless Pygame;
supersample at SS=6 then smoothscale to match the elevated house grammar
(chibi + scary-CUTE, flat saturated triad fills, hard 1-2px ink keyline,
dark-core -> flat-fill -> top-left rim-sheen, 1px alpha-grown outline).

WHY hyeoljang is the funniest-fierce of its set: comedy IS the menace. A real
jangseung warrior-post wards demons by being uglier and scarier than they are —
so this one sticks its TONGUE out at them. The whole identity is a big flat
tongue flopping out of a wide grimace, crossed goggle-eyes, and a top-knot.
The stout warrior body IS the pillar shaft, so creature == prop == pillar and
the gap-cap is the same face, mirrored and smaller at the gap.

WHY the warmest-brown RED-TOTARA wood of the set: the cross-set fix separates
the carved-wood bosses by VALUE/SATURATION. Hyeoljang owns the ruddiest, most
SATURATED brown mass; the tongue-pink is its warm focal gag; the paua eye-ring
is the SMALLEST teal accent in the whole set — a flat two-tone PAINT inlay with
a HARD edge (never a glow, so it can't read as a Yurei/Kitsune cool glow), with
the violet inner kept to a sub-pixel sliver (anti-Necrarch). Eye glow stays warm.

WHY a standalone script: review art must never enter the shipped bundle, so it
lives under docs/ and reuses only colour math, not runtime sprite modules.
"""
import os
import math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Ruddy RED-TOTARA — the warmest, most saturated brown WOOD of the set.
WOOD      = (166,  96,  68)   # ruddy red-totara base
WOOD_D    = (120,  62,  44)   # deep red-totara shade (dark core)
WOOD_T    = (206, 146, 110)   # warm sun-lit rim-sheen helper
WOOD_GRV  = ( 92,  46,  34)   # carved spiral-groove shadow

# Paua EYE-RING — the SMALLEST teal accent of the set. A flat two-tone PAINT
# inlay with a HARD edge, NOT a glow. Violet inner stays a sub-pixel sliver.
# Deepened + cooled to the set's deepest, coolest, smallest teal so the tell
# survives the value collision against the bright cream goggle binding at 32px.
PAUA_RIM  = ( 48, 132, 134)   # paua teal ring (deepest/coolest brood teal, hard)
PAUA_RIM_D= ( 26,  88,  92)   # paua ring shade
PAUA_RIM_T= (110, 184, 184)   # paua ring rim-sheen fleck
PAUA_IN   = (110,  96, 160)   # paua violet inner (sub-pixel sliver only)

TONGUE    = (214, 108, 118)   # tongue-pink — the warm focal GAG
TONGUE_D  = (158,  70,  82)   # tongue shade (dark core)
TONGUE_T  = (240, 160, 168)   # tongue rim-sheen / wet highlight

CREAM     = (238, 224, 196)   # cream binding cord / top-knot wrap
CREAM_D   = (196, 178, 146)   # cream shade

EYEGLOW   = (250, 232, 184)   # warm-cream eye glow (the warm focal)
EYEGLOW_D = (216, 178, 110)   # eye-glow shade ring
TOOTH     = (236, 230, 214)   # bone-cream blunt teeth

INK       = ( 28,  22,  30)   # hard ink keyline (locked set ink)

BG        = ( 98,  90,  88)   # neutral warm-grey review backdrop
PANEL     = ( 78,  70,  70)
DAY_SKY_T = (140, 206, 232)   # day biome sky (top)
DAY_SKY_B = (206, 232, 240)   # day biome sky (low)
NIGHT_T   = ( 22,  28,  52)   # night biome sky (top)
NIGHT_B   = ( 46,  44,  78)   # night biome sky (low)
LABEL     = (240, 236, 230)
LABEL_DIM = (198, 190, 184)


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


# ── one carved SPIRAL groove (the repeatable cheek/body motif) ────────────────
def spiral_groove(surf, cx, cy, rad, s, turns=1.4):
    """A single shallow carved spiral — the warrior cheek/body curl. WHY sparse
    spirals instead of a dense field: the brief pins the grooves SPARSE so the
    ruddy wood stays a clean mass, and a few BIG carved curls survive 1x
    downscale where fine hatching just fuzzes to brown mud. Drawn as a dark
    bevel-shadow arc with a thin warm sheen lip so it reads carved-IN."""
    steps = 26
    pts_d = []
    pts_t = []
    for i in range(steps + 1):
        t = i / steps
        ang = t * turns * 2 * math.pi
        r = rad * (1.0 - 0.62 * t)
        pts_d.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        pts_t.append((cx + math.cos(ang) * r - max(1, int(1.4*s)),
                      cy + math.sin(ang) * r - max(1, int(1.4*s))))
    if len(pts_d) > 1:
        pygame.draw.lines(surf, WOOD_GRV, False, pts_d, max(1, int(2*s)))
        pygame.draw.lines(surf, WOOD_T, False, pts_t, max(1, int(1*s)))


# ── carved-wood column band (the repeatable shaft unit) ───────────────────────
def carved_shaft(surf, cx, top, bot, half_w, s):
    """One stretch of the stout warrior POST: a ruddy red-totara column with
    SPARSE carved spiral body grooves, faint grain, a couple of cream binding
    cords, and a centred soft body-seam. This is what tiles — the warrior body
    IS this column."""
    w = half_w * 2
    x0 = cx - half_w

    # main wood mass — flat fill + warm dark core on the right + sun-lit sheen
    body = [(x0, top), (x0 + w, top), (x0 + w, bot), (x0, bot)]
    triad_blob(
        surf, WOOD, body,
        core_pts=[(cx + int(half_w*0.22), top), (x0 + w, top),
                  (x0 + w, bot), (cx + int(half_w*0.22), bot)],
        sheen_pts=[(x0, top), (x0 + int(half_w*0.34), top),
                   (x0 + int(half_w*0.34), bot), (x0, bot)],
        ow=max(2, int(2*s)),
    )

    # a couple of carved vertical bevel grooves at the OUTER edges — frame the
    # body without crowding the sparse spirals. Kept few + big for downscale.
    for gx in (-int(half_w*0.72), int(half_w*0.72)):
        pygame.draw.line(surf, WOOD_GRV, (cx + gx, top + int(4*s)),
                         (cx + gx, bot - int(4*s)), max(1, int(2*s)))
        pygame.draw.line(surf, WOOD_T, (cx + gx - max(1, int(2*s)), top + int(4*s)),
                         (cx + gx - max(1, int(2*s)), bot - int(4*s)),
                         max(1, int(1*s)))

    # SPARSE carved spiral body grooves down the centre — the repeat motif. One
    # curl per ~tall course, alternating side-bias so the column reads turned.
    course_h = int(108*s)
    sy = top + int(58*s)
    flip = 0
    spr = max(int(7*s), int(half_w * 0.46))
    while sy < bot - int(40*s):
        offx = int(half_w * 0.18) * (1 if flip % 2 else -1)
        spiral_groove(surf, cx + offx, sy, spr, s,
                      turns=1.3 if flip % 2 else 1.5)
        sy += course_h
        flip += 1

    # 1-2 CREAM binding cords — full-width wrapped bands that break the long
    # shaft into stacked carved courses (a warrior's lashed post, not a bar).
    bind_h = max(3, int(7*s))
    by = top + course_h
    while by < bot - int(30*s):
        pygame.draw.rect(surf, INK, (x0 + int(2*s), by - bind_h//2 - max(1, int(1*s)),
                                     w - int(4*s), bind_h + max(2, int(2*s))))
        pygame.draw.rect(surf, CREAM, (x0 + int(3*s), by - bind_h//2,
                                       w - int(6*s), bind_h))
        pygame.draw.rect(surf, CREAM_D, (x0 + int(3*s), by + max(1, int(1*s)),
                                         w - int(6*s), max(1, int(2*s))))
        # warm sheen lip on the top-left of each cord
        pygame.draw.line(surf, lerp(CREAM, (255, 255, 255), 0.3),
                         (x0 + int(4*s), by - bind_h//2 + max(1, int(1*s))),
                         (cx, by - bind_h//2 + max(1, int(1*s))), max(1, int(1*s)))
        by += course_h


# ── the comic tongue-out warrior FACE (the whole identity) ────────────────────
def warrior_face(surf, cx, cy, s, lit=False):
    """The oversized funniest-fierce guardian face: crossed GOGGLE-EYES with a
    paua two-tone PAINT-inlay ring (hard edge, never a glow), a wide grimace,
    and a big flat TONGUE flopping out as the dominant lower-face mass — the
    gag. Topped by a cream-wrapped TOP-KNOT. `lit` brightens the warm eye glow
    + lights the tongue so the same face works as the GAP-EDGE cap. WHY no
    limbs: a jangseung is a post — the face IS the whole creature."""

    # face block — a broad ruddy-wood plaque a touch wider than the shaft
    fw, fh = int(100*s), int(104*s)
    fx0, fy0 = cx - fw // 2, cy - fh // 2
    face = [(fx0 + int(8*s), fy0), (fx0 + fw - int(8*s), fy0),
            (fx0 + fw, fy0 + int(16*s)), (fx0 + fw, fy0 + fh - int(12*s)),
            (fx0 + fw - int(12*s), fy0 + fh), (fx0 + int(12*s), fy0 + fh),
            (fx0, fy0 + fh - int(12*s)), (fx0, fy0 + int(16*s))]
    triad_blob(
        surf, WOOD, face,
        core_pts=[(cx + int(8*s), fy0 + int(6*s)), (fx0 + fw, fy0 + int(16*s)),
                  (fx0 + fw, fy0 + fh - int(12*s)),
                  (fx0 + fw - int(12*s), fy0 + fh), (cx + int(8*s), fy0 + fh)],
        sheen_pts=[(fx0 + int(5*s), fy0 + int(5*s)), (cx - int(6*s), fy0 + int(5*s)),
                   (cx - int(6*s), fy0 + fh - int(18*s)),
                   (fx0 + int(5*s), fy0 + fh - int(20*s))],
        ow=max(2, int(2*s)),
    )

    # heavy carved BROW ridge — one furrowed bar that frames the goggle-eyes,
    # angled down to the centre so the grimace reads fierce-but-goofy.
    brow_y = fy0 + int(28*s)
    brow = [(fx0 + int(8*s), brow_y - int(4*s)), (cx - int(6*s), brow_y + int(6*s)),
            (cx + int(6*s), brow_y + int(6*s)), (fx0 + fw - int(8*s), brow_y - int(4*s)),
            (fx0 + fw - int(8*s), brow_y + int(7*s)),
            (cx, brow_y + int(14*s)),
            (fx0 + int(8*s), brow_y + int(7*s))]
    triad_blob(surf, WOOD_D, brow,
               sheen_pts=[(fx0 + int(10*s), brow_y - int(2*s)),
                          (cx - int(10*s), brow_y + int(4*s)),
                          (cx - int(10*s), brow_y + int(8*s)),
                          (fx0 + int(10*s), brow_y + int(2*s))],
               ow=max(1, int(1.5*s)))

    # CROSSED GOGGLE-EYES — two bulging domes set wide so the warm eyeballs can
    # cross hard INWARD toward the nose-bridge (the comic warrior squint that is
    # the funniest-fierce beat). Warm-cream glow behind; paua PAINT-inlay ring is
    # a flat hard-edged two-tone band, NOT a glow.
    eye_dx = int(27*s)
    eye_y = fy0 + int(50*s)
    er = int(19*s)
    glow_a = 140 if lit else 80
    glow_r = int(er * (1.9 if lit else 1.4))
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
        # bulging carved-wood eye socket dome
        pygame.draw.circle(surf, INK, (ex, eye_y), er + max(1, int(2*s)))
        pygame.draw.circle(surf, WOOD_D, (ex, eye_y), er)
        pygame.draw.circle(surf, WOOD_T, (ex - int(er*0.4), eye_y - int(er*0.4)),
                           int(er*0.5))
        pygame.draw.circle(surf, INK, (ex, eye_y), er, max(1, int(2*s)))

        # PAUA EYE-RING — flat hard-edged two-tone PAINT inlay. WHY the OUTER arc
        # is fatter: a thin mid-teal sandwiched between the bright cream goggle
        # binding (inner) and the dark ink keyline dies at 32px — it averages into
        # the cream. So the rim is thickened on the OUTER/cheek-facing arc only,
        # where it borders the ruddy WOOD; wood-vs-teal is a real value+hue jump
        # that survives downscale, whereas teal-vs-cream does not. Still the
        # smallest teal of the brood — a hard flat PAINT ring, never a glow.
        ring_r = int(er * 0.80)
        # base shade ring (full circle, hard edge)
        pygame.draw.circle(surf, PAUA_RIM_D, (ex, eye_y), ring_r,
                           max(2, int(3.0*s)))
        # bright teal rim, full circle (the hard inlay band)
        pygame.draw.circle(surf, PAUA_RIM, (ex, eye_y), ring_r,
                           max(1, int(2.2*s)))
        # OUTER/cheek-facing arc — drawn 1px thicker against the wood so the tell
        # survives 32px. The cheek side is away from centre: -x for the right eye,
        # +x for the left. A fat arc swept over the outer ~150° of the ring.
        outer_sgn = -sgn                       # cheek direction (away from nose)
        fat_w = max(2, int(4.6*s))
        outer_rect = (ex - ring_r, eye_y - ring_r, ring_r*2, ring_r*2)
        if outer_sgn < 0:                      # outer arc faces LEFT
            a0, a1 = math.radians(115), math.radians(245)
        else:                                  # outer arc faces RIGHT
            a0, a1 = math.radians(-65), math.radians(65)
        pygame.draw.arc(surf, PAUA_RIM_D, outer_rect, a0, a1, fat_w + max(1, int(1*s)))
        pygame.draw.arc(surf, PAUA_RIM, outer_rect, a0, a1, fat_w)
        # violet inner stays a sub-pixel sliver just inside the rim, never a mass
        pygame.draw.circle(surf, PAUA_IN, (ex, eye_y), ring_r - max(1, int(2*s)),
                           max(1, int(1*s)))
        # top-left hard sheen fleck on the paua rim (inlay catches light)
        pygame.draw.line(surf, PAUA_RIM_T,
                         (ex - int(ring_r*0.55), eye_y - int(ring_r*0.62)),
                         (ex - int(ring_r*0.12), eye_y - int(ring_r*0.78)),
                         max(1, int(1.6*s)))

        # warm-cream glowing eyeball — shifted hard INWARD toward the nose so the
        # whites already sit near the bridge before the pupils cross further.
        eb = int(er * (0.56 if lit else 0.50))
        ball_x = ex - sgn * int(er * 0.30)        # crowd toward centre
        pygame.draw.circle(surf, EYEGLOW_D, (ball_x, eye_y), eb + max(1, int(1*s)))
        pygame.draw.circle(surf, EYEGLOW, (ball_x, eye_y), eb)
        # CROSSED ink pupils — jammed against the inner rim of each eyeball so the
        # two pupils nearly touch over the bulb-nose (the unmistakable cross-eyed
        # warrior gag). Both pushed toward centre regardless of which eye.
        pygame.draw.circle(surf, INK,
                           (ball_x - sgn*int(eb*0.46), eye_y + int(eb*0.18)),
                           int(eb*0.52))
        pygame.draw.circle(surf, (255, 252, 244),
                           (ball_x - sgn*int(eb*0.46) - int(eb*0.22), eye_y - int(eb*0.26)),
                           max(1, int(eb*0.22)))

    # fat BULB-NOSE — one rounded mass dead-centre between the eyes (chibi tell)
    ny = fy0 + int(66*s)
    nr = int(11*s)
    pygame.draw.circle(surf, INK, (cx, ny), nr + max(1, int(2*s)))
    pygame.draw.circle(surf, WOOD, (cx, ny), nr)
    pygame.draw.circle(surf, WOOD_D, (cx + int(nr*0.3), ny + int(nr*0.35)),
                       int(nr*0.6))
    pygame.draw.circle(surf, WOOD_T, (cx - int(nr*0.35), ny - int(nr*0.4)),
                       int(nr*0.42))
    pygame.draw.circle(surf, INK, (cx, ny), nr, max(1, int(2*s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK, (cx + sgn*int(nr*0.42), ny + int(nr*0.5)),
                           max(1, int(2*s)))

    # wide GRIMACE — a broad dark mouth pulled into a flat smirk-snarl, the
    # frame the tongue floods out of. Kept dark so the pink tongue pops.
    my = fy0 + int(82*s)
    mw = int(38*s)
    mh = int(20*s)
    mouth = [(cx - mw, my - int(4*s)), (cx + mw, my - int(4*s)),
             (cx + int(mw*0.82), my + mh), (cx - int(mw*0.82), my + mh)]
    pygame.draw.polygon(surf, INK, mouth)
    pygame.draw.polygon(surf, (38, 22, 26),
                        [(cx - mw + int(3*s), my - int(2*s)),
                         (cx + mw - int(3*s), my - int(2*s)),
                         (cx + int(mw*0.74), my + mh - int(2*s)),
                         (cx - int(mw*0.74), my + mh - int(2*s))])
    # a row of BLUNT warrior teeth across the top of the grimace. WHY only 3 fat
    # tooth-bone blocks with a clear ink gap between each: at 32px a 4-5 tooth
    # row collapses to a grey noise band; 3 big blocks keep the grimace reading
    # as a grimace, not a smear, when small.
    tw = int(15*s)
    for fx in (-int(mw*0.72), -int(mw*0.18), int(mw*0.36)):
        rect = (cx + fx, my - int(2*s), tw, int(9*s))
        pygame.draw.rect(surf, INK, (rect[0]-max(1,int(1*s)), rect[1]-max(1,int(1*s)),
                                     rect[2]+max(2,int(2*s)), rect[3]+max(1,int(1*s))))
        pygame.draw.rect(surf, TOOTH, rect)
        pygame.draw.rect(surf, INK, rect, max(1, int(1*s)))
    # cinnabar-free cream lip line bracketing the grimace top (warrior paint)
    pygame.draw.line(surf, CREAM, (cx - mw, my - int(4*s)),
                     (cx + mw, my - int(4*s)), max(2, int(3*s)))
    pygame.draw.line(surf, lerp(CREAM, (255, 255, 255), 0.3),
                     (cx - mw, my - int(5*s)), (cx, my - int(5*s)), max(1, int(1*s)))

    # the big flat TONGUE — the DOMINANT lower-face mass and the gag. A wide
    # rounded lobe flopping down and out of the grimace, lit warm when capped.
    tcx = cx + int(4*s)                       # lolls a touch off-centre (goofy)
    tt = my + mh - int(6*s)                   # tongue root inside the mouth
    tb = my + mh + int(46*s)                  # floppy tip well below the jaw
    tw = int(mw * 0.92)
    tongue = [
        (tcx - int(tw*0.62), tt),
        (tcx + int(tw*0.62), tt),
        (tcx + int(tw*0.78), tt + int((tb-tt)*0.30)),
        (tcx + int(tw*0.66), tb - int((tb-tt)*0.18)),
        (tcx + int(tw*0.26), tb),
        (tcx - int(tw*0.30), tb),
        (tcx - int(tw*0.70), tb - int((tb-tt)*0.20)),
        (tcx - int(tw*0.80), tt + int((tb-tt)*0.30)),
    ]
    if lit:
        # gap-lit tongue glows warm from inside the mouth
        tglow = pygame.Surface((tw*5, (tb-tt)*4), pygame.SRCALPHA)
        for r in range(int(tw*1.2), 0, -1):
            a = int(110 * (1 - r/(tw*1.2)))
            pygame.draw.circle(tglow, (*TONGUE_T, a),
                               (int(tw*2.5), int((tb-tt)*1.4)), r)
        surf.blit(tglow, (tcx - int(tw*2.5), tt - int((tb-tt)*0.4)),
                  special_flags=pygame.BLEND_ADD)
    tcol = lerp(TONGUE, (255, 255, 255), 0.10) if lit else TONGUE
    triad_blob(
        surf, tcol, tongue,
        core_pts=[(tcx + int(tw*0.10), tt + int((tb-tt)*0.22)),
                  (tcx + int(tw*0.78), tt + int((tb-tt)*0.30)),
                  (tcx + int(tw*0.66), tb - int((tb-tt)*0.18)),
                  (tcx + int(tw*0.26), tb),
                  (tcx + int(tw*0.05), tb)],
        sheen_pts=[(tcx - int(tw*0.50), tt + int((tb-tt)*0.10)),
                   (tcx - int(tw*0.02), tt + int((tb-tt)*0.08)),
                   (tcx - int(tw*0.06), tt + int((tb-tt)*0.46)),
                   (tcx - int(tw*0.52), tt + int((tb-tt)*0.42))],
        ow=max(2, int(2*s)),
    )
    # central tongue crease — the carved midline that sells the flat tongue
    pygame.draw.line(surf, TONGUE_D, (tcx, tt + int((tb-tt)*0.16)),
                     (tcx + int(tw*0.06), tb - int((tb-tt)*0.12)), max(2, int(2.5*s)))
    pygame.draw.line(surf, TONGUE_T, (tcx - max(1, int(2*s)), tt + int((tb-tt)*0.18)),
                     (tcx - max(1, int(2*s)) + int(tw*0.04), tb - int((tb-tt)*0.30)),
                     max(1, int(1*s)))
    # wet tip highlight blob
    pygame.draw.circle(surf, TONGUE_T,
                       (tcx - int(tw*0.10), tb - int((tb-tt)*0.30)),
                       max(1, int(3*s)))

    # the cream-wrapped TOP-KNOT on the crown (the warrior headpiece tell)
    knot_base_y = fy0 + int(2*s)
    # a hard ink NOTCH cinching where the knot meets the head — WHY: at 32px the
    # pink/cream wrap blurs into the wood crown and the knot reads as a vague
    # lump; a dark keyline groove pinches the silhouette so the thumbnail tells
    # "top-knot" not "bump".
    notch_w = int(30*s)
    pygame.draw.rect(surf, INK,
                     (cx - notch_w//2, knot_base_y - max(2, int(2*s)),
                      notch_w, max(3, int(4*s))))
    # a short tapered post rising from the crown
    stalk_w = int(20*s)
    stalk = [(cx - stalk_w//2, knot_base_y),
             (cx + stalk_w//2, knot_base_y),
             (cx + int(stalk_w*0.34), knot_base_y - int(26*s)),
             (cx - int(stalk_w*0.34), knot_base_y - int(26*s))]
    triad_blob(surf, WOOD_D, stalk,
               sheen_pts=[(cx - stalk_w//2 + int(2*s), knot_base_y - int(2*s)),
                          (cx - int(stalk_w*0.10), knot_base_y - int(2*s)),
                          (cx - int(stalk_w*0.08), knot_base_y - int(24*s)),
                          (cx - int(stalk_w*0.28), knot_base_y - int(24*s))],
               ow=max(1, int(1.5*s)))
    # cream binding wrap around the stalk
    for k in range(2):
        wy = knot_base_y - int(8*s) - k*int(9*s)
        pygame.draw.rect(surf, INK, (cx - int(stalk_w*0.42), wy - max(1, int(1*s)),
                                     int(stalk_w*0.84), max(3, int(5*s))))
        pygame.draw.rect(surf, CREAM, (cx - int(stalk_w*0.38), wy,
                                       int(stalk_w*0.76), max(2, int(3*s))))
    # the round top-knot ball at the crown
    kr = int(15*s)
    ky = knot_base_y - int(38*s)
    pygame.draw.circle(surf, INK, (cx, ky), kr + max(1, int(2*s)))
    pygame.draw.circle(surf, WOOD, (cx, ky), kr)
    pygame.draw.circle(surf, WOOD_D, (cx + int(kr*0.3), ky + int(kr*0.35)),
                       int(kr*0.6))
    pygame.draw.circle(surf, WOOD_T, (cx - int(kr*0.35), ky - int(kr*0.4)),
                       int(kr*0.45))
    pygame.draw.circle(surf, INK, (cx, ky), kr, max(1, int(2*s)))
    # a cream cross-binding over the knot ball
    pygame.draw.line(surf, CREAM, (cx - int(kr*0.7), ky - int(kr*0.2)),
                     (cx + int(kr*0.7), ky + int(kr*0.2)), max(2, int(2.5*s)))
    pygame.draw.line(surf, CREAM, (cx - int(kr*0.6), ky + int(kr*0.35)),
                     (cx + int(kr*0.6), ky - int(kr*0.05)), max(1, int(2*s)))


# ── the full hero creature: tongue-out warrior atop the carved post ──────────
def draw_hyeoljang(surf, cx, cy, s):
    """The whole guardian: oversized tongue-out warrior face in the top third
    atop the stout carved POST (the body = the pillar shaft). No limbs. `s` is
    a unit scale around a ~250-unit-tall figure."""
    half_w = int(44*s)
    post_top = cy - int(48*s)
    post_bot = cy + int(152*s)
    # the carved-wood warrior body shaft (continues the same column the pillar tiles)
    carved_shaft(surf, cx, post_top, post_bot, half_w, s)
    # a wider plinth foot grounds the post (bottom-rooted, not top-heavy)
    foot = [(cx - half_w - int(10*s), post_bot - int(4*s)),
            (cx + half_w + int(10*s), post_bot - int(4*s)),
            (cx + half_w + int(5*s), post_bot + int(16*s)),
            (cx - half_w - int(5*s), post_bot + int(16*s))]
    triad_blob(surf, WOOD_D, foot,
               sheen_pts=[(cx - half_w - int(8*s), post_bot - int(2*s)),
                          (cx - int(4*s), post_bot - int(2*s)),
                          (cx - int(4*s), post_bot + int(12*s)),
                          (cx - half_w - int(4*s), post_bot + int(12*s))],
               ow=max(2, int(2*s)))
    # the oversized tongue-out warrior face filling the top third
    warrior_face(surf, cx, cy - int(92*s), s, lit=False)


# ── the pillar: same carved post, mirrored, with a partner-face gap-cap ──────
def draw_pillar_segment(surf, cx, top, bot, half_w, s, cap="bottom", cap_scale=0.82):
    """A shaft stretch of the warrior POST that meets the gap with a SMALLER
    twin mirrored PARTNER-FACE cap (eyes + tongue LIT at the gap). The shaft is
    the same carved column as the creature body, so creature == pillar. `cap`
    end faces the gap; the cap face is drawn smaller so the gap stays bottom-
    rooted, never top-heavy."""
    face_room = int(132*s * cap_scale)
    if cap == "bottom":
        shaft_top, shaft_bot = top, bot - face_room
        face_cy = bot - face_room // 2 + int(8*s)
        face_dir = 1
    else:
        shaft_top, shaft_bot = top + face_room, bot
        face_cy = top + face_room // 2 - int(8*s)
        face_dir = -1
    carved_shaft(surf, cx, shaft_top, shaft_bot, half_w, s)

    # the partner-face — same warrior face but SMALLER, drawn into a scratch
    # surface so it can be FLIPPED for the top cap (proving the true mirror).
    fsz = int(190*s)
    fbuf = pygame.Surface((fsz, fsz), pygame.SRCALPHA)
    warrior_face(fbuf, fsz//2, fsz//2, s * cap_scale, lit=True)
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
    sheet.blit(font_big.render("HYEOLJANG", True, LABEL), (22, 12))
    sheet.blit(font_sm.render(
        "tongue-out warrior guardian post  ·  red-totara + paua eye-ring inlay + tongue-pink gag + cream binding  ·  round 2  ·  comedy IS the menace",
        True, LABEL_DIM), (212, 26))

    # (a) BIG hero sprite ------------------------------------------------------
    hb_w, hb_h = 300, 470
    big = pygame.Surface((hb_w*SS, hb_h*SS), pygame.SRCALPHA)
    draw_hyeoljang(big, hb_w*SS//2, int(hb_h*SS*0.44), 1.30*SS)
    hero = pygame.transform.smoothscale(big, (hb_w, hb_h))
    hero = grow_outline(hero, INK + (255,), 1)
    sheet.blit(hero, (10, 72))
    sheet.blit(font.render("(a) Hero — tongue-out warrior post", True, LABEL), (16, 548))
    sheet.blit(font_sm.render("eyes now CROSS inward; paua rim deepened + fattened on the OUTER", True, LABEL_DIM), (16, 572))
    sheet.blit(font_sm.render("cheek-arc (borders wood); 3 fat teeth; knot notch; sparse spirals", True, LABEL_DIM), (16, 588))

    # (b) pillar assembled — top segment + gap + bottom segment, MIRRORED ------
    pcx = 460
    seg_half = int(36)
    seg_h = 250
    seg_top_y = 72
    gap_px = 96
    # top segment (cap faces DOWN toward the gap = flipped partner-face)
    topbuf = pygame.Surface((170*SS, seg_h*SS), pygame.SRCALPHA)
    draw_pillar_segment(topbuf, 85*SS, 4*SS, (seg_h-4)*SS, seg_half*SS, 1.0*SS, cap="top")
    topimg = pygame.transform.smoothscale(topbuf, (170, seg_h))
    topimg = grow_outline(topimg, INK + (255,), 1)
    sheet.blit(topimg, (pcx - 85, seg_top_y))
    # bottom segment (cap faces UP toward the gap = upright partner-face)
    botbuf = pygame.Surface((170*SS, seg_h*SS), pygame.SRCALPHA)
    draw_pillar_segment(botbuf, 85*SS, 4*SS, (seg_h-4)*SS, seg_half*SS, 1.0*SS, cap="bottom")
    botimg = pygame.transform.smoothscale(botbuf, (170, seg_h))
    botimg = grow_outline(botimg, INK + (255,), 1)
    sheet.blit(botimg, (pcx - 85, seg_top_y + seg_h + gap_px))

    # gap guide lines
    gap_y0, gap_y1 = seg_top_y + seg_h, seg_top_y + seg_h + gap_px
    for gy in (gap_y0, gap_y1):
        pygame.draw.line(sheet, (158, 150, 148), (pcx - 96, gy), (pcx + 96, gy), 1)
    sheet.blit(font_sm.render("← gap →", True, LABEL_DIM), (pcx - 24, (gap_y0+gap_y1)//2 - 7))
    by = seg_top_y + 2*seg_h + gap_px + 10
    sheet.blit(font.render("(b) Pillar — MIRRORED", True, LABEL), (pcx - 96, by))
    sheet.blit(font_sm.render("tileable carved shaft (spirals + cords);", True, LABEL_DIM), (pcx - 96, by + 24))
    sheet.blit(font_sm.render("smaller twin face caps the gap, eyes/tongue lit", True, LABEL_DIM), (pcx - 96, by + 40))

    # (c) TRUE 32px gameplay-scale chips — day sky + night sky -----------------
    panel_x = 660
    pw = W - panel_x - 14
    pygame.draw.rect(sheet, PANEL, (panel_x, 72, pw, 372))
    sheet.blit(font.render("(c) True 32px gameplay chip", True, LABEL), (panel_x + 14, 82))
    sheet.blit(font_sm.render("one tongue-out / goggle-eye face read", True, LABEL_DIM), (panel_x + 14, 104))

    # render at a true ~32px FACE read — the gameplay collision shows the
    # face-topped cap end, so the chip frames the FACE (not the long shaft).
    def chip32():
        cs = 46  # chip canvas (px) — face + tongue + a sliver of post under it
        buf = pygame.Surface((cs*SS, cs*SS), pygame.SRCALPHA)
        # centre the FACE in the chip; scale so the face spans ~32px
        draw_hyeoljang(buf, cs*SS//2, int(cs*SS*1.04), (32/96.0)*SS)
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
    sheet.blit(font_sm.render("warm eyes + pink tongue anchor the night read",
                              True, LABEL_DIM), (panel_x + 22, cy1 + 138))

    # palette swatch row -------------------------------------------------------
    pal_y = 458
    pygame.draw.rect(sheet, PANEL, (panel_x, pal_y, pw, 196))
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 14, pal_y + 10))
    swatches = [
        (WOOD, "red-totara"), (WOOD_D, "deep totara"),
        (WOOD_T, "wood sheen"), (WOOD_GRV, "spiral groove"),
        (PAUA_RIM, "paua teal rim"), (PAUA_IN, "paua violet (sliver)"),
        (TONGUE, "tongue-pink"), (TONGUE_D, "deep tongue"),
        (CREAM, "cream binding"), (EYEGLOW, "eye-glow cream"),
        (TOOTH, "tooth bone"), (INK, "ink keyline"),
    ]
    sx, sy = panel_x + 14, pal_y + 40
    for i, (c, name) in enumerate(swatches):
        col = i % 2
        row = i // 2
        rx = sx + col*150
        ry = sy + row*26
        pygame.draw.rect(sheet, INK, (rx-1, ry-1, 22, 22))
        pygame.draw.rect(sheet, c, (rx, ry, 20, 20))
        sheet.blit(font_sm.render(name, True, LABEL), (rx+27, ry+4))

    # construction note panel — full-width strip across the bottom ------------
    note_y = 668
    pygame.draw.rect(sheet, PANEL, (10, note_y, W - 20, 222))
    sheet.blit(font.render("Construction notes", True, LABEL), (26, note_y + 10))
    notes_l = [
        "• Ruddy RED-TOTARA — warmest, most saturated brown wood of the",
        "  set; the cross-set value/saturation separation.",
        "• Big flat TONGUE-PINK tongue = the dominant lower-face mass +",
        "  the warm focal gag; comedy IS the menace.",
        "• Crossed GOGGLE-EYES + bulb-nose + top-knot = the funniest-",
        "  fierce warrior read; big & few features for the 32px read.",
    ]
    notes_r = [
        "• Paua EYE-RING deepened to (48,132,134) — deepest/coolest/smallest",
        "  brood teal; fattened on the OUTER cheek-arc (borders wood, survives",
        "  32px). Still a flat HARD PAINT inlay, NOT a glow (anti-Yurei/Kitsune).",
        "• Eyes now CROSS hard inward over the bulb-nose (the warrior gag).",
        "• Creature IS the pillar: hero post body == tiled shaft; cap =",
        "  SMALLER mirrored partner-face (eyes/tongue lit), bottom-rooted.",
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
