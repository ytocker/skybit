"""Carousel Barker jester-staff pillar art.

A fairground-barker scepter ported from the look-dev tool: a plum/gold
barber-twist shaft spiralling up to a grinning mini-clown under a four-point
cap, jewelled gold ferrule collars and a flared bell foot. Drawn dark-cored so
the silhouette holds value against the day sky. The staff carries its own fixed
jester palette rather than the biome palette so the cartoon read stays loud."""

import math

import pygame

from game.draw import _shade_c, lerp_color  # noqa: F401  (lerp_color kept for parity)
from game.config import PIPE_W, GROUND_Y

# Guards may spill this far past the 58-px column on each side.
OVERHANG = 12

# Supersample factor for the baked obstacle art. ss=3 is plenty for the ~58px
# scrolling route tile (ss=5 cost ~9ms/pillar and stuttered the route).
_SS = 3

# A clown warren spawns up to ~25 fused staff towers in a few seconds. Rendering
# each tower's jester art from scratch (supersample + smoothscale + a full-height
# mask scan) is fine on desktop but ~10-20x costlier under pygbag/WASM, where the
# burst stutters the tunnel AND grows linear memory that never shrinks (lingering
# lag). The obstacle art only depends on its HEIGHT and orientation, and a route's
# heights collapse to a handful of buckets — so bake each (height-bucket, flip)
# ONCE and share it across every tower. Heights are quantized UP to _HEIGHT_Q and
# the marotte head is anchored at the gap edge, so the <=_HEIGHT_Q surplus spills
# into the clipped ground / off-screen ceiling (invisible) while the gap edge —
# the only part collisions and the eye care about — stays exact.
_HEIGHT_Q = 24
_OBSTACLE_SURF_CACHE: "dict[tuple[int, bool], pygame.Surface]" = {}
_OBSTACLE_MASK_CACHE: "dict[tuple[int, bool], pygame.Mask]" = {}
_CACHE_CAP = 128  # far above the ~50 reachable buckets; a runaway guard only


def _bucket_h(H):
    """Round an obstacle height UP to the shared-cache grid, clamped to the
    playfield height (the per-tower cache clips anything past the ground)."""
    q = ((int(H) + _HEIGHT_Q - 1) // _HEIGHT_Q) * _HEIGHT_Q
    return max(_HEIGHT_Q, min(q, GROUND_Y))


def _obstacle_surf(hb, flip):
    key = (hb, flip)
    surf = _OBSTACLE_SURF_CACHE.get(key)
    if surf is None:
        if len(_OBSTACLE_SURF_CACHE) > _CACHE_CAP:
            _OBSTACLE_SURF_CACHE.clear()
        surf = _staff_obstacle(hb, _SS, flip=flip)
        _OBSTACLE_SURF_CACHE[key] = surf
    return surf


def _obstacle_mask(hb, flip):
    key = (hb, flip)
    m = _OBSTACLE_MASK_CACHE.get(key)
    if m is None:
        if len(_OBSTACLE_MASK_CACHE) > _CACHE_CAP:
            _OBSTACLE_MASK_CACHE.clear()
        m = pygame.mask.from_surface(_obstacle_surf(hb, flip), 50)
        _OBSTACLE_MASK_CACHE[key] = m
    return m


def _staff_pieces(top_rect, bot_rect):
    """(flip, bucket_height, x, y) for each obstacle, head anchored at the gap
    edge. Surface blit and mask draw MUST share these offsets so the baked art
    and the collision silhouette line up."""
    pieces = []
    if top_rect.height > 0:                       # head points DOWN to the gap
        hb = _bucket_h(top_rect.height)
        pieces.append((True, hb, top_rect.x - OVERHANG, top_rect.bottom - hb))
    if bot_rect.height > 0:                        # head points UP to the gap
        hb = _bucket_h(bot_rect.height)
        pieces.append((False, hb, bot_rect.x - OVERHANG, bot_rect.y))
    return pieces

# Macaw-glove palette for the hero clown's gripping/pointing hands (the hands are
# the only non-staff art this module draws — for the warren demo's settled hero).
# Resolved literals so this module stays free of the look-dev alias chains.
_GLOVE = (250, 250, 252)
_GLOVE_OUTLINE = (20, 12, 18)
_GLOVE_GROOVE = (172, 172, 174)        # 1-shade-darker inter-finger groove
_GLOVE_OCCLUDE = (154, 154, 156)       # darkest: shaft-behind-fingers band
_GLOVE_HI = (255, 255, 255)
_FOREARM_DEG = 47.0                    # raised-forearm continuation angle

# Plum & Lime clown world palette (so the staff ties to the hero clown).
PLUM = (96, 44, 150)
PLUM_DK = (66, 28, 110)
LIME = (132, 218, 116)
LIME_DK = (74, 150, 70)
GOLD = (250, 205, 72)
GOLD_HI = (255, 236, 150)
GOLD_DK = (176, 130, 30)
GOLD_SHADOW = (110, 78, 22)
CREAM = (255, 248, 224)
INK = (28, 22, 30)

# Warm clown-face inks ported from the hero recipe (render_jester_variants).
FACE_SHADOW = (212, 198, 168)          # cream head keyline / under-shade
EYE_WHITE = (252, 250, 244)
EYE_PUPIL = (44, 38, 60)
EYE_PUPIL_DK = (14, 12, 22)
BROW_COL = (76, 56, 60)                # soft warm brow (never heavy black)
NOSE_RED = (232, 72, 72)
MOUTH_THROAT = (120, 30, 42)
TEETH = (250, 248, 240)
LIP = (188, 56, 66)
TONGUE = (228, 110, 124)
CHEEK = (255, 150, 150)
DEAD_EYE = (196, 30, 44)               # the blank-stare "mean" variant's pinprick


def _box(H, ss):
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(H)) * ss
    return pygame.Surface((bw, bh), pygame.SRCALPHA), bw, bh


def _mini_clown_face(surf, cx, hy, hr, ss, *, expr="grin", look=None):
    """The hero clown's HAPPY-but-MEAN expression ported into ss-scaled marotte
    space: a cream head, bright open eyes glancing sidelong, lifted SLY brows,
    a warm ball nose, and a wide upturned OPEN grin with a tooth row + one fang.
    `expr` flavours the mouth — "grin" (base), "tongue" (tongue-tip licking the
    corner), or "stare" (the dead-eyed, blank-stare 'mean' read). All geometry
    keys off `hr` so it scales with the bauble, never the clown's fixed 1x grid."""
    # `u` is the DIMENSIONLESS head scale vs the round-6 head (hr already carries
    # the ss factor), so `u * ss` below yields proper supersampled pixels — the
    # face never double-scales by ss.
    u = hr / (11.0 * ss)
    look = (-2.0 * u * ss) if look is None else look
    # Cream head with a soft under-shade keyline (the clown's round face).
    pygame.draw.circle(surf, FACE_SHADOW, (cx, int(hy)), hr)
    pygame.draw.circle(surf, CREAM, (cx, int(hy)), int(hr - ss))
    # Warm cheek flush low + outward on the apple so it reads charming, not a tear.
    for s in (-1, 1):
        blush = pygame.Surface((int(7 * u * ss), int(5 * u * ss)), pygame.SRCALPHA)
        pygame.draw.ellipse(blush, (*CHEEK, 120), blush.get_rect())
        surf.blit(blush, (int(cx + s * hr * 0.46 - 3.5 * u * ss),
                          int(hy + hr * 0.28)))
    ex = hr * 0.42                         # eye spacing
    ew, eh = 2.0 * u, 2.5 * u              # tall round OPEN eye (alive, not hooded)
    # "smirk" shares the dead pinprick eyes with "stare" but carries a sly raised
    # brow + a one-corner-up closed mouth so it reads as a mischievous clown, not an
    # empty doll. `dead` drives the eye treatment; the mouth branch splits below.
    smirk = expr == "smirk"
    stare = expr == "stare" or smirk
    for s in (-1, 1):
        exx = cx + s * ex
        # White sclera — a tall bright open eye.
        rect = pygame.Rect(int(exx - ew * ss), int(hy - eh * ss + ss),
                           int(ew * 2 * ss), int(eh * 2 * ss))
        pygame.draw.ellipse(surf, EYE_WHITE, rect)
        if stare:
            # The 'mean' read: tiny dead pinprick pupils dead-centre — a vacant,
            # unsettling stare instead of the gleeful sidelong glance.
            pygame.draw.circle(surf, DEAD_EYE, (int(exx), int(hy + ss)),
                               max(1, int(1.4 * u * ss)))
            pygame.draw.circle(surf, EYE_PUPIL_DK, (int(exx), int(hy + ss)),
                               max(1, int(1.4 * u * ss)), max(1, int(ss)))
        else:
            px = exx + look
            py = hy + 0.6 * u * ss
            pr = max(2, int(2.0 * u * ss))
            pygame.draw.circle(surf, EYE_PUPIL, (int(px), int(py)), pr)
            pygame.draw.circle(surf, EYE_PUPIL_DK, (int(px), int(py)), pr, max(1, int(ss)))
            pygame.draw.circle(surf, (255, 255, 255),
                               (int(px - 0.7 * u * ss), int(py - 1.0 * u * ss)),
                               max(1, int(0.7 * u * ss)))
        # Thin LIGHT upper lid arched UP (a happy lifted lid), never a hooded bar.
        pygame.draw.arc(surf, INK, (int(exx - ew * ss - ss), int(hy - eh * ss),
                                    int(ew * 2 * ss + 2 * ss), int(eh * ss + 2 * ss)),
                        math.pi * 0.15, math.pi * 0.85, max(1, int(1.4 * ss)))
        # SLY raised brow — inner (nose-side) end HIGH, outer end lower, bowed up
        # at the mid: a lifted "oh-really" arch that can never knit into the angry
        # inner-down V. Drawn as a thin 3-point polyline so it reads arched, not a
        # heavy flat bar.
        inner = (exx - s * 1.0 * u * ss, hy - 5.4 * u * ss)
        mid = (exx + s * 1.8 * u * ss, hy - 5.6 * u * ss)
        outer = (exx + s * 4.6 * u * ss, hy - 3.6 * u * ss)
        if stare and not smirk:
            # A flatter, lower brow for the blank-stare so the calm reads colder.
            inner = (exx - s * 1.0 * u * ss, hy - 4.6 * u * ss)
            mid = (exx + s * 1.8 * u * ss, hy - 4.6 * u * ss)
            outer = (exx + s * 4.6 * u * ss, hy - 4.4 * u * ss)
        elif smirk:
            # ONE sly raised brow (the die-side / LEFT, s == -1) cocks up high; the
            # other stays flat + low — a single cocked brow over dead eyes is the
            # whole "knowing menace-glee" tell of the sinister smirk.
            if s < 0:
                inner = (exx - s * 1.0 * u * ss, hy - 6.4 * u * ss)
                mid = (exx + s * 1.8 * u * ss, hy - 6.8 * u * ss)
                outer = (exx + s * 4.6 * u * ss, hy - 5.0 * u * ss)
            else:
                inner = (exx - s * 1.0 * u * ss, hy - 4.4 * u * ss)
                mid = (exx + s * 1.8 * u * ss, hy - 4.4 * u * ss)
                outer = (exx + s * 4.6 * u * ss, hy - 4.4 * u * ss)
        pygame.draw.lines(surf, BROW_COL, False,
                          [(int(inner[0]), int(inner[1])), (int(mid[0]), int(mid[1])),
                           (int(outer[0]), int(outer[1]))], max(1, int(1.3 * ss)))
    # Red ball nose, lifted up between the eyes so the grin owns the lower face.
    # Bumped up again so the warm dot is the last face cue to survive at 30px, where
    # the eyes/brows dissolve and only "warm nose over dark smile" reads — the dot
    # has to win the silhouette fight against the cap clutter above it.
    nr = max(3, int(3.0 * u * ss))
    pygame.draw.circle(surf, _shade_c(NOSE_RED, -60), (cx, int(hy + 1.4 * u * ss)), nr + 1)
    pygame.draw.circle(surf, NOSE_RED, (cx, int(hy + 1.4 * u * ss)), nr)
    pygame.draw.circle(surf, _shade_c(NOSE_RED, 100),
                       (int(cx - nr * 0.4), int(hy + 1.4 * u * ss - nr * 0.4)),
                       max(1, int(nr * 0.4)))
    if smirk:
        # A closed-mouth SMIRK: a smooth lip curve with the die-side (LEFT) corner
        # cocked UP and the other corner held low — a sliver of menace-glee so the
        # dead eyes read as a sly clown, not a vacant doll. A short dimple tick seats
        # the raised corner so the asymmetry survives shrinking.
        my = hy + 5.0 * u * ss
        l_up = (cx - 4.2 * u * ss, my - 1.8 * u * ss)
        r_lo = (cx + 4.2 * u * ss, my + 1.2 * u * ss)
        smk = []
        for k in range(11):
            t = k / 10.0
            sx = l_up[0] + (r_lo[0] - l_up[0]) * t
            sy = l_up[1] + (r_lo[1] - l_up[1]) * t + (1.0 - (2.0 * t - 1.0) ** 2) * 1.2 * u * ss
            smk.append((int(sx), int(sy)))
        pygame.draw.lines(surf, LIP, False, smk, max(2, int(2.2 * ss)))
        pygame.draw.line(surf, _shade_c(LIP, -40),
                         (int(l_up[0]), int(l_up[1])),
                         (int(l_up[0] + 1.2 * u * ss), int(l_up[1] - 1.6 * u * ss)),
                         max(1, int(1.4 * ss)))
        return
    if stare:
        # A small flat closed line-mouth for the unsettling calm — no toothy grin.
        my = hy + 5.4 * u * ss
        pygame.draw.line(surf, LIP, (int(cx - 4.0 * u * ss), int(my)),
                         (int(cx + 4.0 * u * ss), int(my)), max(2, int(2.0 * ss)))
        pygame.draw.line(surf, _shade_c(LIP, -30),
                         (int(cx - 2.0 * u * ss), int(my + 1.6 * u * ss)),
                         (int(cx + 2.0 * u * ss), int(my + 1.6 * u * ss)), max(1, int(ss)))
        return
    # THE DOMINANT FEATURE: a WIDE OPEN happy grin, die-side (LEFT) corner highest
    # so it stays lopsided/sly, with a tooth row + one pointed fang for the edge.
    mw = 5.0 * u * ss
    my = hy + 4.6 * u * ss
    l_corner = (cx - mw - 0.6 * u * ss, my - 1.0 * u * ss)
    r_corner = (cx + mw, my)
    bottom = (cx, my + 3.6 * u * ss)
    mouth = [l_corner, (cx - 2.3 * u * ss, my + 0.5 * u * ss),
             (cx + 2.3 * u * ss, my + 0.5 * u * ss), r_corner,
             (cx + 2.7 * u * ss, my + 1.8 * u * ss), bottom,
             (cx - 2.7 * u * ss, my + 1.8 * u * ss)]
    # Throat darkened one step so the open grin reads as a solid dark smile-band
    # at route scale (the "dark smile under a warm dot" cue) once the teeth blur.
    pygame.draw.polygon(surf, _shade_c(MOUTH_THROAT, -34),
                        [(int(p[0]), int(p[1])) for p in mouth])
    # Bright tooth band across the top of the open grin + tooth separators.
    teeth = [l_corner, (cx - 2.3 * u * ss, my), (cx + 2.3 * u * ss, my), r_corner,
             (cx + 2.3 * u * ss, my + 1.4 * u * ss), (cx - 2.3 * u * ss, my + 1.4 * u * ss)]
    pygame.draw.polygon(surf, TEETH, [(int(p[0]), int(p[1])) for p in teeth])
    pygame.draw.polygon(surf, _shade_c(TEETH, -70),
                        [(int(p[0]), int(p[1])) for p in teeth], max(1, int(ss)))
    for k in range(-2, 3):
        gx = cx + k * 1.9 * u * ss
        pygame.draw.line(surf, _shade_c(TEETH, -70), (int(gx), int(my)),
                         (int(gx), int(my + 1.4 * u * ss)), max(1, int(ss)))
    # One pointed FANG dropping below the tooth row on the die-side (LEFT). It is the
    # MVP of the "mean" read and the FIRST thing to vanish when shrunk, so it is now
    # seated HIGH into the tooth band (base up at the tooth-band top) with a wider
    # base and a longer drop — a fat triangular spike that reads as a single dark-
    # rimmed tusk even after the tooth separators blur. Drawn against the dark throat
    # FIRST as a fat throat wedge so the fang silhouette persists, then the bright
    # tooth fang over it with a heavy keyline.
    fang = [(cx - 3.4 * u * ss, my), (cx + 0.2 * u * ss, my),
            (cx - 1.6 * u * ss, my + 4.8 * u * ss)]
    pygame.draw.polygon(surf, _shade_c(MOUTH_THROAT, -34),
                        [(int(p[0] - 0.5 * u * ss), int(p[1] + 0.6 * u * ss)) for p in fang])
    pygame.draw.polygon(surf, TEETH, [(int(p[0]), int(p[1])) for p in fang])
    pygame.draw.polygon(surf, _shade_c(TEETH, -70),
                        [(int(p[0]), int(p[1])) for p in fang], max(2, int(1.6 * ss)))
    # The lip line wrapping the grin — a single smooth up-curving crescent.
    lip = []
    for k in range(13):
        t = k / 12.0
        lx = (l_corner[0] - 1.0 * u * ss) + ((r_corner[0] + 1.0 * u * ss)
                                             - (l_corner[0] - 1.0 * u * ss)) * t
        ly = (l_corner[1] - 1.4 * u * ss) + ((r_corner[1] - 1.0 * u * ss)
                                             - (l_corner[1] - 1.4 * u * ss)) * t \
            + (1.0 - (2.0 * t - 1.0) ** 2) * 4.2 * u * ss
        lip.append((int(lx), int(ly)))
    pygame.draw.lines(surf, LIP, False, lip, max(2, int(1.6 * ss)))
    if expr == "tongue":
        # A small tongue-tip licking the raised (die-side) grin corner.
        tr = pygame.Rect(int(l_corner[0] - 1.0 * u * ss), int(my + 1.0 * u * ss),
                         int(3.0 * u * ss), int(2.6 * u * ss))
        pygame.draw.ellipse(surf, TONGUE, tr)
        pygame.draw.ellipse(surf, _shade_c(TONGUE, -60), tr, max(1, int(ss)))


def _marotte_ruff(surf, cx, ny, r, ss, col, *, lobes=9, bell_col=GOLD, fringe=None):
    """A scalloped ruff under the bauble (the clown's neck collar), ported into
    ss space: a row of overlapping lit lobes ringing the neck with a small bell
    dangling at each outer edge, so the mini-clown reads as a costumed head, not
    a bare ball. Drawn dark-cored so it holds value on the day sky. `fringe` (a
    gold) hangs a fat bell off the bottom of each lobe — the jingle density moved
    to the collar so it can't blur the head silhouette into a halo."""
    for i in range(lobes):
        t = i / (lobes - 1)
        lx = cx - r + 2 * r * t
        ly = ny + 2.0 * ss + math.sin(t * math.pi) * -2.0 * ss
        rad = max(3, int(r * 0.30))
        if fringe is not None:
            # A short thread + fat bell hanging off the lobe's lower edge — a tidy
            # belled fringe along the collar reads as "jingles" at any scale.
            by = ly + rad + int(4 * ss)
            pygame.draw.line(surf, _shade_c(fringe, -60), (int(lx), int(ly + rad)),
                             (int(lx), int(by)), max(2, int(2.0 * ss)))
            pygame.draw.circle(surf, _shade_c(fringe, -55), (int(lx), int(by)), max(3, int(3.6 * ss)))
            pygame.draw.circle(surf, fringe, (int(lx), int(by)), max(2, int(2.8 * ss)))
            pygame.draw.circle(surf, _shade_c(fringe, 80),
                               (int(lx - ss), int(by - ss)), max(1, int(1.2 * ss)))
        pygame.draw.circle(surf, _shade_c(col, -55), (int(lx), int(ly)), rad)
        pygame.draw.circle(surf, col, (int(lx), int(ly)), max(2, rad - int(ss)))
        pygame.draw.circle(surf, _shade_c(col, 55),
                           (int(lx - rad * 0.3), int(ly - rad * 0.3)),
                           max(1, int(rad * 0.34)))
    for s in (-1, 1):
        bx, by = int(cx + s * (r + 1.5 * ss)), int(ny + 4 * ss)
        pygame.draw.circle(surf, _shade_c(bell_col, -55), (bx, by), max(2, int(3 * ss)))
        pygame.draw.circle(surf, bell_col, (bx, by), max(2, int(2.4 * ss)))
        pygame.draw.circle(surf, _shade_c(bell_col, 80),
                           (int(bx - ss), int(by - ss)), max(1, int(ss)))


def _shaft_outline(surf, cx, top_y, bot_y, hw, ss, lo, *, taper=0.0):
    """The dark shaft mass + a hard keyline. `taper` pinches the foot so the
    scepter narrows toward the pommel for a finished, balanced read. Returns the
    left/right edge point lists so an ornament can ride the (possibly tapered)
    body without recomputing the silhouette."""
    span = max(1, bot_y - top_y)
    left, right = [], []
    n = 18
    for i in range(n + 1):
        t = i / n
        y = top_y + span * t
        w = hw * (1.0 - taper * t)
        left.append((cx - w, y))
        right.append((cx + w, y))
    body = left + list(reversed(right))
    pygame.draw.polygon(surf, lo, [(int(p[0]), int(p[1])) for p in body])
    pygame.draw.polygon(surf, _shade_c(lo, -45),
                        [(int(p[0]), int(p[1])) for p in body], max(2, int(2.0 * ss)))
    return left, right


def _shaft_twist(surf, cx, top_y, bot_y, hw, ss, col_a, col_b, lo):
    """A BARBER-POLE twist: bold diagonal plum/gold ribbons spiralling up a dark
    pole, clipped to the column so the stripes stay inside the body. The carousel-
    barker shaft."""
    left, right = _shaft_outline(surf, cx, top_y, bot_y, hw, ss, lo)
    stripe = max(4, int(7 * ss))
    n = int((bot_y - top_y) / stripe) + 4
    # Clip the diagonal ribbons to the (straight) shaft column with a cheap RECT
    # clip and draw them straight onto `surf`. The old path allocated TWO
    # full-size SRCALPHA surfaces and did a full-surface BLEND_RGBA_MULT mask
    # composite per call — O(box area), which dominated the per-pillar build and
    # stuttered the route. A rect clip is exact here (the marotte shaft is a
    # straight column, taper=0) and costs nothing.
    prev_clip = surf.get_clip()
    shaft_rect = pygame.Rect(int(cx - hw), int(top_y),
                             int(2 * hw) + 1, int(bot_y - top_y) + 1)
    surf.set_clip(shaft_rect.clip(prev_clip))
    # A 4-band cycle (plum x3, gold x1) so the dark plum dominates ~3:1 and the gold
    # ribbon reads as a bold spiral accent — the old 2:1 strobed/flickered at
    # distance, and the wider plum keeps the route median dark.
    for i in range(-2, n):
        y0 = top_y + i * stripe
        c = col_b if i % 4 == 3 else col_a
        quad = [(cx - hw, y0), (cx + hw, y0 - hw * 1.5),
                (cx + hw, y0 - hw * 1.5 + stripe), (cx - hw, y0 + stripe)]
        pygame.draw.polygon(surf, c, [(int(p[0]), int(p[1])) for p in quad])
    surf.set_clip(prev_clip)
    # A slim lit rail down the lit side reads the pole as round, not flat.
    pygame.draw.line(surf, _shade_c(col_a, 50), (int(cx - hw * 0.45), int(top_y)),
                     (int(cx - hw * 0.45), int(bot_y)), max(1, int(1.4 * ss)))
    pygame.draw.polygon(surf, _shade_c(lo, -45),
                        [(int(p[0]), int(p[1])) for p in (left + list(reversed(right)))],
                        max(2, int(2.0 * ss)))


def _ferrule(surf, cx, y, hw, ss, col, *, h=8, jewel=None):
    """A rich banded ferrule ring round the shaft: a dark base bead, a lit gold
    rim, an engraved mid-line — far richer than the old two thin lines. Optional
    `jewel` colour sets a centred cabochon for a jewelled collar."""
    hh = int(h * ss)
    over = int(2.0 * ss)
    pygame.draw.rect(surf, _shade_c(col, -45),
                     (int(cx - hw - over), int(y - hh * 0.5), int((hw + over) * 2), hh))
    pygame.draw.rect(surf, col,
                     (int(cx - hw - over), int(y - hh * 0.5), int((hw + over) * 2), hh),
                     max(1, int(1.4 * ss)))
    pygame.draw.line(surf, _shade_c(col, 70), (int(cx - hw - over), int(y - hh * 0.28)),
                     (int(cx + hw + over), int(y - hh * 0.28)), max(1, int(1.4 * ss)))
    pygame.draw.line(surf, _shade_c(col, -70), (int(cx - hw - over), int(y + hh * 0.28)),
                     (int(cx + hw + over), int(y + hh * 0.28)), max(1, int(ss)))
    if jewel is not None:
        jr = max(2, int(hh * 0.36))
        pygame.draw.circle(surf, _shade_c(jewel, -50), (cx, int(y)), jr + 1)
        pygame.draw.circle(surf, jewel, (cx, int(y)), jr)
        pygame.draw.circle(surf, _shade_c(jewel, 90),
                           (int(cx - jr * 0.3), int(y - jr * 0.3)), max(1, int(jr * 0.4)))


def _pommel_finial(surf, cx, bot_y, hw, ss, col, *, kind="ball", gem=None, bead=True):
    """A finished finial/pommel at the foot so the staff reads as a real scepter
    butt, not a sawn-off pole. `kind` picks the silhouette: a knobbed "ball", a
    spike-tipped "spike", or a flared collared "bell". `bead` adds the small
    collar bead above a ball pommel; drop it for a cleaner single-knob foot."""
    if kind == "spike":
        pr = int(hw * 1.5)
        pygame.draw.polygon(surf, _shade_c(col, -50),
                            [(int(cx - hw), int(bot_y - pr)), (int(cx + hw), int(bot_y - pr)),
                             (cx, int(bot_y + pr * 0.5))])
        pygame.draw.polygon(surf, col,
                            [(int(cx - hw + ss), int(bot_y - pr)),
                             (int(cx + hw - ss), int(bot_y - pr)),
                             (cx, int(bot_y + pr * 0.4))])
        pygame.draw.line(surf, _shade_c(col, 60), (int(cx - hw * 0.3), int(bot_y - pr)),
                         (cx, int(bot_y + pr * 0.3)), max(1, int(1.4 * ss)))
        return
    if kind == "bell":
        bw2 = int(hw * 1.7)
        pygame.draw.polygon(surf, _shade_c(col, -50),
                            [(int(cx - hw), int(bot_y - hw * 1.6)),
                             (int(cx + hw), int(bot_y - hw * 1.6)),
                             (int(cx + bw2), int(bot_y)), (int(cx - bw2), int(bot_y))])
        pygame.draw.polygon(surf, col,
                            [(int(cx - hw + ss), int(bot_y - hw * 1.6)),
                             (int(cx + hw - ss), int(bot_y - hw * 1.6)),
                             (int(cx + bw2 - ss), int(bot_y - ss)),
                             (int(cx - bw2 + ss), int(bot_y - ss))])
        pygame.draw.ellipse(surf, _shade_c(col, -40),
                            (int(cx - bw2), int(bot_y - 2 * ss), int(bw2 * 2), int(4 * ss)))
        return
    # Default: a fat knobbed ball pommel with a small bead beneath it.
    pr = int(hw * 1.5)
    pcy = int(bot_y - pr * 0.55)
    pygame.draw.circle(surf, _shade_c(col, -55), (cx, pcy), pr)
    pygame.draw.circle(surf, col, (cx, pcy), int(pr - ss))
    pygame.draw.circle(surf, _shade_c(col, 55),
                       (int(cx - pr * 0.3), int(pcy - pr * 0.3)), max(2, int(pr * 0.36)))
    if gem is not None:
        pygame.draw.circle(surf, _shade_c(gem, -40), (cx, pcy), max(2, int(pr * 0.4)))
        pygame.draw.circle(surf, gem, (cx, pcy), max(2, int(pr * 0.32)))
        pygame.draw.circle(surf, _shade_c(gem, 90),
                           (int(cx - pr * 0.16), int(pcy - pr * 0.16)), max(1, int(pr * 0.14)))
    if bead:
        pygame.draw.circle(surf, _shade_c(col, -45), (cx, int(bot_y - pr * 1.25)),
                           max(2, int(hw * 0.8)))


def prop_14l(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(13 * ss)
    hy = int(50 * ss)                      # seat the head lower so the tall cap +
                                           # its bell tips clear the box top (no clip)
    shaft_top = hy + hr
    hwid = int(7 * ss)
    _shaft_twist(surf, cx, shaft_top, bh - int(7 * ss), hwid, ss, PLUM, GOLD, PLUM_DK)
    _ferrule(surf, cx, bh * 0.5, hwid, ss, GOLD, h=9, jewel=PLUM)
    _ferrule(surf, cx, bh - int(20 * ss), hwid, ss, GOLD, h=8)
    # Foot planted ON the ground line (bot_y == bh): the flared bell ends at the
    # box bottom rather than 4 px above it, so the staff rests on the ground.
    _pommel_finial(surf, cx, bh, hwid, ss, GOLD, kind="bell")
    base_y = hy - hr + int(1 * ss)
    for (dx, dy, col) in [(-30, -8, PLUM_DK), (30, -6, PLUM_DK),
                          (-19, -29, LIME_DK), (19, -27, GOLD_DK)]:
        bxp, byp = cx + int(dx * ss), base_y + int(dy * ss)
        span = int(8 * ss)
        tri = [(cx - span, base_y + int(2 * ss)), (cx + span, base_y + int(2 * ss)), (bxp, byp)]
        pygame.draw.polygon(surf, col, tri)
        pygame.draw.polygon(surf, _shade_c(col, 50),
                            [(cx - span, base_y + int(2 * ss)), (cx, base_y + int(2 * ss)),
                             (bxp, byp)])
        pygame.draw.polygon(surf, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
        pygame.draw.circle(surf, GOLD, (int(bxp), int(byp)), max(2, int(3.4 * ss)))
        pygame.draw.circle(surf, GOLD_DK, (int(bxp), int(byp)), max(2, int(3.4 * ss)), max(1, int(ss)))
    _marotte_ruff(surf, cx, hy + hr - int(2 * ss), int(hr * 1.05), ss, LIME, lobes=9)
    _mini_clown_face(surf, cx, hy, hr, ss, expr="grin")


def _staff_obstacle(H, ss, *, flip):
    surf, bw, bh = _box(max(1, int(H)), ss)
    prop_14l(surf, bw, bh, ss)
    out_w = PIPE_W + 2 * OVERHANG
    small = pygame.transform.smoothscale(surf, (out_w, max(1, int(H))))
    if flip:
        small = pygame.transform.flip(small, False, True)
    return small


def draw_pillar_pair_staff(surf, top_rect, bot_rect, palette, seed):
    """Draw a TOP + BOTTOM staff obstacle pair (the marotte bauble/head faces the
    gap on each). Matches the pagoda candidate signature so Pipe can cache it.
    `palette`/`seed` are accepted for signature parity; the staff uses its own
    fixed jester colours. Blits shared, height-bucketed obstacle surfaces so a
    warren of towers bakes only a handful of distinct surfaces (see cache note)."""
    for flip, hb, x, y in _staff_pieces(top_rect, bot_rect):
        surf.blit(_obstacle_surf(hb, flip), (x, y))


def staff_collision_mask(size, top_rect, bot_rect):
    """Build a tower's collision mask by stamping the shared per-bucket obstacle
    masks at the SAME offsets draw_pillar_pair_staff blits them — a couple of fast
    bitwise mask.draw ops, instead of scanning the whole composited surface with
    mask.from_surface for every tower. `size` is (w, h) of the pillar cache."""
    m = pygame.mask.Mask(size)
    for flip, hb, x, y in _staff_pieces(top_rect, bot_rect):
        m.draw(_obstacle_mask(hb, flip), (int(x), int(y)))
    return m


# ── Hero clown hands (warren demo's settled-hero composition) ─────────────────
# The macaw-glove grip + pointing hands ported from the look-dev render, so the
# demo's hero clown holds the design-8 staff and points at the die without any
# tools/ import in shipped code. The grip is a three-z-pass build: the caller
# blits the shaft between the BEHIND pass (palm heel + knuckle ridge) and the
# FRONT pass (four banded fingers), with an occlusion band darkening the shaft
# where the whole grip crosses it.

def _r8_segment(surf, base, tip, w, *, rim=True, cap=True):
    """One finger SEGMENT capsule (base→tip) with the macaw-weight keyline, glove
    fill, rounded tip cap and the constant TOP-LEFT rim sheen. Grip segments read
    by their bounding GROOVES, not internal creases, so they don't muddy at 3-4px."""
    pygame.draw.line(surf, _GLOVE_OUTLINE, base, tip, w + 2)
    pygame.draw.line(surf, _GLOVE, base, tip, w)
    if cap:
        pygame.draw.circle(surf, _GLOVE, tip, max(1, w // 2))
        pygame.draw.circle(surf, _GLOVE_OUTLINE, tip, max(1, w // 2), 1)
    if rim:
        pygame.draw.line(surf, _GLOVE_HI,
                         (base[0] - 1, base[1] - 1), (tip[0] - 1, tip[1] - 1),
                         max(1, w // 3))


def _r8_palm(surf, cx, cy, rx, ry):
    """Rounded palm/cup mass — keyline ellipse, glove fill, top-left alpha sheen."""
    rect = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
    pygame.draw.ellipse(surf, _GLOVE_OUTLINE, rect)
    pygame.draw.ellipse(surf, _GLOVE, rect.inflate(-2, -2))
    sheen = pygame.Surface((rx, ry), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 90), sheen.get_rect())
    surf.blit(sheen, (cx - rx + 1, cy - ry + 1))


def _r8_grip_occlusion(surf, hand, shaft_w):
    """The dark band on the shaft spanning the full height of the FOUR banded
    fingers, so the wood reads as passing behind the whole grip rather than beside
    one digit."""
    hx, hy = hand
    pygame.draw.line(surf, _GLOVE_OCCLUDE,
                     (hx - shaft_w - 2, hy - 8), (hx - shaft_w - 2, hy + 11),
                     shaft_w + 2)


def _r11_grip_glove(surf, hand, shaft_w, *, behind):
    """LOCKED four-finger staff grip: the behind pass widens the back-of-hand mass
    into a tall knuckle ridge spanning the full -6..+9 finger band on the right, so
    ALL FOUR finger bases emerge from one continuous palm (no orphan bottom digit).
    The four banded fingers, their grooves, the looser top finger and the shaft
    occlusion behind are drawn in the FRONT pass; no thumb is added."""
    hx, hy = hand
    fw = 4
    dys = (-6, -1, 4, 9)
    palm_rx, palm_ry = 6, 8
    loose_top = 1
    reach = shaft_w + 5
    if behind:
        # Back of hand / palm heel behind the shaft, then a knuckle ridge down the
        # right side spanning every finger root so the bottom finger is no orphan.
        _r8_palm(surf, hx + 3, hy + 1, palm_rx, palm_ry)
        ridge = pygame.Rect(0, 0, fw + 4, (dys[-1] - dys[0]) + fw + 4)
        ridge.center = (hx + 4, hy + (dys[0] + dys[-1]) // 2)
        pygame.draw.rect(surf, _GLOVE_OUTLINE, ridge, border_radius=fw)
        pygame.draw.rect(surf, _GLOVE, ridge.inflate(-2, -2), border_radius=fw)
        pygame.draw.line(surf, _GLOVE_GROOVE,
                         (hx + 3, hy - palm_ry + 2), (hx + 3, hy + palm_ry - 2), 1)
        return
    # FRONT: four banded finger segments rooted in the knuckle ridge above. The top
    # one sits a touch looser (lifted + reaching further) to break the stack.
    for k, dy in enumerate(dys):
        loose = loose_top if k == 0 else 0
        if k > 0:
            pygame.draw.line(surf, _GLOVE_GROOVE,
                             (hx + 4, hy + dy - fw // 2 - 1),
                             (hx - reach + 1, hy + dy - fw // 2 - 1 - loose),
                             max(1, fw // 2))
        base = (hx + 4, hy + dy)
        tip = (hx - reach - loose, hy + dy - loose)
        _r8_segment(surf, base, tip, fw)


def _r17_die_hand(surf, hand, *, wrist, gesture="mitt", knuckles_up=False,
                  point_len=0.0, point_bow=0.0, base_w=4):
    """The die-side hand: a SIMPLE closed-glove gesture whose read comes from one
    strong silhouette plus 1-2 dark grooves — never from fine finger anatomy, which
    fizzes at ~16px. Heel-on-wrist `_proj` continues the raised forearm as one limb.
    `gesture` selects "mitt" (a clean rounded fist), "point" (the fist with ONE
    tapered digit extended toward the die) or "reach" (the digit curls up as a soft
    cupped grab). `point_len`/`point_bow` set the extended digit's reach and curve."""
    hx, hy = hand
    ang = math.radians(-wrist)
    ca, sa = math.cos(ang), math.sin(ang)

    def _proj(dx, dy):
        # Heel laid a hair up the hand so the forearm tip lands INSIDE the mitt mass.
        return (hx - int(round(dx * ca - dy * sa)),
                hy + int(round(-dx * sa - dy * ca)) - int(round(2 * ca)))

    crown = 9.6 + (1.2 if knuckles_up else 0.0)
    HALF = 6.2                          # half-width of the fist across the band
    body_local = [
        (-3.6, -3.6),                   # inner wrist corner (narrow heel)
        (-HALF, 3.0),                   # widen out toward the knuckle band
        (-HALF * 0.86, crown - 1.0),
        (-HALF * 0.30, crown),          # knuckle crown, viewer-left lobe
        ( HALF * 0.30, crown),          # knuckle crown, viewer-right lobe
        ( HALF * 0.86, crown - 1.0),
        ( HALF + 0.4, 3.0),
        ( 4.0, -3.6),                   # outer wrist corner (narrow heel)
    ]
    body_pts = [_proj(x, y) for (x, y) in body_local]

    # A short, low thumb wedge folded against the index side: enough to break the
    # pure-oval read, never an extended digit.
    thenar = [
        _proj(4.6, -1.4),               # wrist root, outside
        _proj(7.0, 1.6),                # thumb knuckle swell
        _proj(5.2, 4.4),                # tucks back into the fist
        _proj(3.2, 2.0),
    ]

    def _draw_blob():
        pygame.draw.polygon(surf, _GLOVE_OUTLINE, thenar)
        pygame.draw.polygon(surf, _GLOVE, [_proj(x * 0.9, y) for (x, y) in
                                           ((4.6, -1.4), (7.0, 1.6),
                                            (5.2, 4.4), (3.2, 2.0))])
        pygame.draw.polygon(surf, _GLOVE_OUTLINE, body_pts)
        pygame.draw.polygon(surf, _GLOVE,
                            [_proj(x * 0.9, y) for (x, y) in body_local])

    def _digit(reach_back):
        # Root just above the knuckle crown, on the die-facing edge of the fist.
        root_x, root_y = -HALF * 0.30, crown - 0.6
        segs = (0.0, 0.42, 0.76, 1.0)
        pts = []
        for t in segs:
            up = root_y + point_len * t
            bow = point_bow * (t * t)
            if reach_back:
                up = root_y + point_len * (t - 1.2 * t * t)
                bow = -point_bow * (t * t) - HALF * 0.30 * t
            pts.append((root_x + bow, up))
        return [_proj(x, y) for (x, y) in pts]

    def _taper_w(t):
        return max(2, int(round(base_w - 1.2 * t)))

    def _draw_digit(reach_back=False):
        pts = _digit(reach_back)
        for col, lw_off in ((_GLOVE_OUTLINE, 2), (_GLOVE, 0)):
            for i in range(len(pts) - 1):
                t = i / (len(pts) - 1)
                pygame.draw.line(surf, col, pts[i], pts[i + 1], _taper_w(t) + lw_off)
            pygame.draw.circle(surf, col, pts[-1],
                               max(1, (_taper_w(1.0) + lw_off) // 2))

    if gesture == "reach":
        _draw_digit(reach_back=True)
        _draw_blob()
    elif gesture == "point":
        _draw_blob()
        _draw_digit(reach_back=False)
    else:
        _draw_blob()

    # ONE curved dark knuckle groove + a hairline wrist crease + a single rim-sheen
    # lobe: the whole "anatomy" budget — sparse so it never fizzes at true 1x.
    band_y = crown - 2.4
    groove = [_proj(x, band_y + (0.8 if knuckles_up else 0.0))
              for x in (-HALF * 0.7, -HALF * 0.2, HALF * 0.3, HALF * 0.72)]
    if len(groove) >= 2:
        pygame.draw.lines(surf, _GLOVE_GROOVE, False, groove, 1)
    pygame.draw.line(surf, _GLOVE_GROOVE, _proj(-HALF * 0.6, 0.2),
                     _proj(HALF * 0.6, 0.2), 1)
    pygame.draw.circle(surf, _GLOVE_HI, _proj(-HALF * 0.25, crown - 3.4), 2)


def _held_staff_surface(total_px, bauble_px):
    """Render the design-8 Carousel-Barker staff (`prop_14l`) into a free-standing
    bitmap whose bauble reads `bauble_px` tall and whose whole figure is `total_px`
    tall, ready to be rotated + gripped. The internal supersample keys off the
    bauble so the mini-clown face stays crisp regardless of staff length."""
    f = bauble_px / 26.0
    p_ss = 6
    H = max(1, int(round(total_px / f)))
    surf, bw, bh = _box(H, p_ss)
    prop_14l(surf, bw, bh, p_ss)
    disp_w = max(1, int(round((PIPE_W + 2 * OVERHANG) * f)))
    disp_h = max(1, int(round(H * f)))
    return pygame.transform.smoothscale(surf, (disp_w, disp_h)), disp_w, disp_h


def draw_chosen_hero(surf, cx, feet_y, *, build_jester, spec):
    """Draw the settled hero clown onto `surf`: build_jester body + the pointing
    die-hand on the raised wrist + the design-8 Carousel-Barker staff (Taller,
    total_px=225) gripped in the down hand with its bell foot planted. Mirrors the
    look-dev render_clown_staff_r17 composition; the floating die is drawn
    separately by the demo."""
    ground_y = feet_y + 4

    # Body + raised arm reaching up-left toward the die. Drawn first so the hands
    # and staff layer over it.
    hand_up = (cx - 60, feet_y - 156)
    build_jester(surf, cx, feet_y, hand_up, **spec)

    # The pointing hand on the raised wrist — one tapered digit aimed at the die.
    _r17_die_hand(surf, hand_up, wrist=_FOREARM_DEG, gesture="point",
                  point_len=15.0, point_bow=-1.0)

    # The down hand grips the staff at the hip; the staff is rotated slightly and
    # planted so its bell foot touches the ground line. The grip fraction climbs
    # the shaft as needed so the foot lands at `foot_target` for any length.
    hip_y = feet_y - 84
    hip_cx = cx - 6
    r_hand = (hip_cx + 34, hip_y - 4)

    prop, p_w, p_h = _held_staff_surface(225, 15)
    rot = -7
    rad = math.radians(rot)
    foot_target = ground_y + 7
    grip_frac = max(0.16, 1.0 - (foot_target - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = r_hand[0] - grip_rx
    prop_oy = r_hand[1] - grip_ry
    rhi = (int(r_hand[0]), int(r_hand[1]))

    # Three z-passes: palm heel behind → shaft → occlusion band → fingers in front.
    _r11_grip_glove(surf, rhi, 2, behind=True)
    surf.blit(rotated, (int(round(prop_ox)), int(round(prop_oy))))
    _r8_grip_occlusion(surf, rhi, 2)
    _r11_grip_glove(surf, rhi, 2, behind=False)
