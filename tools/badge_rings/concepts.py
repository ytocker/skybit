"""Five PAIRED outer-RING concepts for the achievement medallions.

Each concept is a MATCHED PAIR sharing ONE prestige motif and palette:

  * ``fame_<name>``  — the pristine GOLD trophy: a real honour (wreath /
    sash-and-star / sunburst / gilded cog / gemmed coronet) struck in warm
    gold under the family's one upper-left light.
  * ``shame_<name>`` — the SAME motif fallen from grace: the identical
    construction DEGRADED so it reads as the award gone wrong, never an
    unrelated badge. Laurel browns & sheds leaves; sash tears, frays and
    bleaches to grey; sunburst rays bend, snap and soot over; cog rusts and
    loses teeth; coronet cracks and its gems drop out of empty sockets.

The CENTER emblem is NOT redesigned — every composer stamps the real engraved
glyph through the live ``_stamp_glyph`` (``pillar_100`` in Fame samples, a
shame emblem in Shame samples), so only the ring/frame changes. NO diagonal
crack on any Shame ring (that cue was retired).

Distinctness is BETWEEN the five concepts — different silhouettes and shape
languages (organic wreath, draped fabric, radial spikes, mechanical teeth,
faceted regalia). WITHIN a pair the Fame & Shame are tightly bound: Shame is
literally how THAT concept's shared motif decays.

Every composer draws a COMPLETE medallion at supersample scale (caller
smoothscales down), reusing the live module's ``_draw_step`` / ``_draw_face`` /
``_stamp_glyph`` / ``lerp_color`` / ``blit_glow`` low-level helpers while giving
each concept its own bottom-up frame construction.

WRITE-ONLY scratch — never bundled. Imports ``game`` read-only.
"""
from __future__ import annotations

import math
import pygame

import game.achievement_icons as ai
from game.draw import lerp_color, blit_glow

_LIGHT = ai._LIGHT  # share the family's one upper-left light source


# ── shared low-level helpers ────────────────────────────────────────────────

def _center(surf, glyph_key, cx, cy, R, gly, gly_sh, sheen=None):
    gr = int(R * 0.56)
    ai._stamp_glyph(surf, glyph_key, cx, cy, gr, gly, gly_sh, sheen)


def _metal_band(surf, cx, cy, R, inner, hi, lo, spec=None,
                spec_span=0.55, light=_LIGHT, edge=None):
    """A lit metal rim band from R inward to ``inner`` under the one upper-left
    light — shared bevel math; each concept feeds its own palette so the band
    MATERIAL (gold, tarnished pewter, rust) differs while the strike reads the
    same. Optional ``edge`` paints the thin outer keyline."""
    for i in range(R, inner, -1):
        t = (R - i) / max(1, R - inner)
        pygame.draw.circle(surf, lerp_color(hi, lo, t * 0.6 + 0.2), (cx, cy), i)
    steps = 56
    band = (R - inner)
    for seg in range(steps):
        a0 = seg / steps * math.tau
        a1 = (seg + 1) / steps * math.tau
        d = (math.cos(a0 - light) + 1) * 0.5
        col = lerp_color(lo, hi, d ** 1.4)
        rect = pygame.Rect(cx - R + band // 3, cy - R + band // 3,
                           (R - band // 3) * 2, (R - band // 3) * 2)
        pygame.draw.arc(surf, col, rect, -a1, -a0, max(2, band - band // 3))
    if spec is not None:
        mid_r = (R + inner) // 2
        hot = pygame.Rect(cx - mid_r, cy - mid_r, mid_r * 2, mid_r * 2)
        pygame.draw.arc(surf, spec, hot, light - spec_span, light + spec_span,
                        max(2, band // 2))
    if edge is not None:
        pygame.draw.circle(surf, edge, (cx, cy), R, max(1, R // 36))


def _oxide_mottle(surf, cx, cy, r0, r1, cols, seed, n=26):
    """Deterministic rust/grime mottle ring — irregular oxide blots scattered in
    the band so a degraded frame reads as corroded metal, not a clean recolour.
    Fixed pseudo-random from ``seed`` so the badge is stable across renders."""
    s = seed
    for i in range(n):
        s = (s * 1103515245 + 12345) & 0x7fffffff
        a = (s / 0x7fffffff) * math.tau
        s = (s * 1103515245 + 12345) & 0x7fffffff
        rad = r0 + (r1 - r0) * (s / 0x7fffffff)
        px = cx + int(math.cos(a) * rad)
        py = cy + int(math.sin(a) * rad)
        col = cols[i % len(cols)]
        sz = max(2, int((r1 - r0) * (0.18 + 0.22 * ((i * 7) % 3) / 2)))
        pygame.draw.circle(surf, col, (px, py), sz)


# ═══════════════════════════════════════════════════════════════════════════
# 1) WREATH — the classic twin-laurel victory wreath.
#    Fame: two full sprigs of glossy gold laurel encircling the disc up to a
#    crowning bow at the top — the timeless honour. Shame: the same wreath
#    WILTED — leaves browned and curled, the sprigs drooping, several leaves
#    shed and tumbling off the lower rim, the bow undone.
# ═══════════════════════════════════════════════════════════════════════════
_WR_RIM_HI  = (255, 234, 168)
_WR_RIM_MID = (236, 186,  72)
_WR_RIM_LO  = (150, 102,  20)
_WR_EDGE    = ( 70,  44,   8)
_WR_SPEC    = (255, 250, 222)
_WR_LEAF_HI = (250, 214, 110)     # lit gold leaf
_WR_LEAF_LO = (150, 100,  24)     # shadowed gold leaf
_WR_FACE_TOP = ( 44,  32,  92)
_WR_FACE_BOT = ( 16,  10,  44)
_WR_RECESS   = ( 10,   6,  28)
_WR_GLY      = (255, 236, 184)
_WR_GLY_SH   = ( 32,  18,  44)

# Wilted palette — the SAME leaves gone autumn-brown and lifeless.
_WD_RIM_HI  = (150, 150, 156)
_WD_RIM_MID = ( 98,  96, 100)
_WD_RIM_LO  = ( 54,  52,  56)
_WD_EDGE    = ( 26,  24,  26)
_WD_LEAF_HI = (150, 112,  56)     # dry tan leaf, lit
_WD_LEAF_LO = ( 78,  52,  28)     # rotted brown leaf, shadow
_WD_LEAF_DEAD = ( 96,  84,  56)   # grey-brown dead leaf
_WD_FACE_TOP = ( 50,  48,  54)
_WD_FACE_BOT = ( 26,  24,  30)
_WD_RECESS   = ( 16,  14,  20)
_WD_GLY      = (176, 168, 156)
_WD_GLY_SH   = ( 18,  16,  18)


def _leaf(surf, bx, by, ang, ln, wd, fill, edge, R):
    """One almond laurel leaf: a pointed ellipse swept along ``ang`` from a base
    at (bx,by). Drawn as a filled lens with a midrib so it reads as a real leaf,
    not a spike."""
    ca, sa = math.cos(ang), math.sin(ang)
    nx, ny = -sa, ca
    pts = []
    for f, w in ((0.0, 0.0), (0.30, wd), (0.62, wd * 0.8), (1.0, 0.0)):
        px = bx + ca * ln * f
        py = by + sa * ln * f
        pts.append((px + nx * w, py + ny * w))
    for f, w in ((1.0, 0.0), (0.62, wd * 0.8), (0.30, wd), (0.0, 0.0)):
        px = bx + ca * ln * f
        py = by + sa * ln * f
        pts.append((px - nx * w, py - ny * w))
    pygame.draw.polygon(surf, fill, [(int(x), int(y)) for x, y in pts])
    pygame.draw.line(surf, edge, (int(bx), int(by)),
                     (int(bx + ca * ln), int(by + sa * ln)), max(1, R // 60))


def _laurel_sprig(surf, cx, cy, R, leaf_hi, leaf_lo, leaves, droop, curl,
                  shed_lo=None):
    """Twin laurel sprigs — two arcs of overlapping almond leaves sweeping UP
    the flanks from the base toward the top, the classic victory wreath. Each
    leaf is a filled lens (``_leaf``) so the wreath reads as foliage, not
    spikes. ``droop`` (0 fame .. 1 wilt) sags the leaves down/in and shrinks
    them; ``curl`` bends each tip limply downward. ``shed_lo`` drops the lowest
    leaves of a wilted sprig (gaps where leaves have fallen)."""
    for sgn in (-1, 1):
        base_a = math.radians(252 if sgn < 0 else 288)
        spread = math.radians(150)                  # arc up toward the top
        for i in range(leaves):
            f = i / (leaves - 1)
            a = base_a - sgn * spread * f
            sag = droop * 0.20 * (f ** 1.3)
            rr = R * (1.04 - sag)
            bx = cx + math.cos(a) * rr
            by = cy + math.sin(a) * rr + droop * R * 0.12 * (0.3 + f)
            d = (math.cos(a - _LIGHT) + 1) * 0.5
            lc = lerp_color(leaf_lo, leaf_hi, d ** 1.2)
            ln = R * (0.34 - 0.05 * f) * (1.0 - 0.28 * droop)
            wd = R * (0.13 - 0.02 * f) * (1.0 - 0.20 * droop)
            # leaf lies back along the wreath (tangential), tip swept up-out;
            # curl drags the tip downward for a wilted limp leaf
            ang = a - sgn * math.radians(52) + curl * sgn * math.radians(40)
            if curl:
                ang += math.radians(28)             # droop tips toward the ground
            # A wilted sprig sheds leaves as a GAP in the silhouette, not a
            # uniform thinning: the right flank loses its whole lower half so the
            # wreath visibly comes apart on one side even at 44px.
            if shed_lo is not None:
                if f < 0.22:
                    continue
                if sgn > 0 and f < 0.62:
                    continue
            _leaf(surf, bx, by, ang, ln, wd, lc, leaf_lo, R)


def _laurel_bow(surf, cx, cy, R, hi, lo, undone=False):
    """The crowning knot where the two sprigs meet at the top. Fame: a tidy
    twin-loop bow. ``undone``: the loops sag open and a tail droops down."""
    topy = int(cy - R * 1.04)
    if not undone:
        for sgn in (-1, 1):
            loop = pygame.Rect(cx + sgn * int(R * 0.04) - int(R * 0.20),
                               topy - int(R * 0.14),
                               int(R * 0.22), int(R * 0.28))
            pygame.draw.ellipse(surf, lerp_color(hi, lo, 0.3), loop)
            pygame.draw.ellipse(surf, lo, loop, max(1, R // 40))
        pygame.draw.circle(surf, hi, (cx, topy), max(2, R // 16))
    else:
        # a slumped, half-untied bow with a single long tail UNRAVELLING far
        # down the left flank — a bold dangling streamer that survives 44px.
        loop = pygame.Rect(cx - int(R * 0.24), topy - int(R * 0.04),
                           int(R * 0.26), int(R * 0.20))
        pygame.draw.ellipse(surf, lerp_color(hi, lo, 0.5), loop)
        pygame.draw.ellipse(surf, lo, loop, max(1, R // 44))
        tail = [(cx, topy),
                (cx - int(R * 0.20), topy + int(R * 0.34)),
                (cx - int(R * 0.42), topy + int(R * 0.78)),
                (cx - int(R * 0.34), topy + int(R * 0.82)),
                (cx - int(R * 0.12), topy + int(R * 0.38)),
                (cx + int(R * 0.06), topy + int(R * 0.04))]
        pygame.draw.polygon(surf, lerp_color(hi, lo, 0.4), tail)
        pygame.draw.line(surf, lo, (cx, topy),
                         (cx - int(R * 0.40), topy + int(R * 0.80)), max(1, R // 40))
        pygame.draw.circle(surf, lerp_color(hi, lo, 0.5), (cx, topy),
                           max(2, R // 18))


def _fallen_leaf(surf, x, y, ln, ang, col, edge, R):
    # a shed laurel leaf tumbling free — the same almond lens as on the sprig
    _leaf(surf, x, y, ang, ln, ln * 0.34, col, edge, R)


def fame_wreath(surf, cx, cy, R, glyph_key):
    _laurel_sprig(surf, cx, cy, R, _WR_LEAF_HI, _WR_LEAF_LO,
                  leaves=8, droop=0.0, curl=0.0)
    _laurel_bow(surf, cx, cy, R, _WR_RIM_HI, _WR_EDGE, undone=False)
    _metal_band(surf, cx, cy, R, int(R * 0.74), _WR_RIM_HI, _WR_RIM_LO,
                spec=_WR_SPEC, edge=_WR_EDGE)
    pygame.draw.circle(surf, _WR_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _WR_RIM_HI, _WR_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _WR_FACE_TOP, _WR_FACE_BOT, _WR_RECESS)
    _center(surf, glyph_key, cx, cy, R, _WR_GLY, _WR_GLY_SH, ai._GLYPH_SHEEN)


def shame_wreath(surf, cx, cy, R, glyph_key):
    # the dull rim FIRST so the browned leaves sit on top of it and stay legible
    _metal_band(surf, cx, cy, R, int(R * 0.74), _WD_RIM_HI, _WD_RIM_LO,
                spec=None, edge=_WD_EDGE)
    _oxide_mottle(surf, cx, cy, int(R * 0.82), int(R * 0.96),
                  (_WD_LEAF_LO, _WD_RIM_LO), seed=11, n=16)
    pygame.draw.circle(surf, _WD_RIM_MID, (cx, cy), R, max(2, R // 24))
    # THREE large, well-separated shed leaves peeling off the lower rim — fewer
    # and bigger than before so each stays a clear leaf silhouette at 44px
    # instead of blurring into a fuzzy brown fringe.
    for fx, fy, fl, fa in ((-0.40, 1.14, 0.46, 1.6),
                           (0.16, 1.30, 0.42, 2.2),
                           (0.62, 1.06, 0.44, 2.6)):
        _fallen_leaf(surf, cx + R * fx, cy + R * fy, R * fl, fa,
                     _WD_LEAF_DEAD, _WD_LEAF_LO, R)
    # the wilted sprigs themselves — browned, drooping, shedding lowest leaves
    _laurel_sprig(surf, cx, cy, R, _WD_LEAF_HI, _WD_LEAF_LO,
                  leaves=8, droop=1.0, curl=0.6, shed_lo=True)
    _laurel_bow(surf, cx, cy, R, _WD_LEAF_HI, _WD_LEAF_LO, undone=True)
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _WD_RIM_HI, _WD_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _WD_FACE_TOP, _WD_FACE_BOT, _WD_RECESS)
    _center(surf, glyph_key, cx, cy, R, _WD_GLY, _WD_GLY_SH)


def shame_wreath_fit(surf, cx, cy, R, glyph_key):
    """Identical to ``shame_wreath`` EXCEPT the three shed leaves are pulled in to
    nestle on the lower rim band — within ~0.49*size of center — so none clip the
    badge edge under the real ``_build`` geometry (R = 0.46*size)."""
    _metal_band(surf, cx, cy, R, int(R * 0.74), _WD_RIM_HI, _WD_RIM_LO,
                spec=None, edge=_WD_EDGE)
    _oxide_mottle(surf, cx, cy, int(R * 0.82), int(R * 0.96),
                  (_WD_LEAF_LO, _WD_RIM_LO), seed=11, n=16)
    pygame.draw.circle(surf, _WD_RIM_MID, (cx, cy), R, max(2, R // 24))
    # pulled inside: lower-rim radius ~0.66-0.80*R instead of 1.06-1.30*R
    for fx, fy, fl, fa in ((-0.42, 0.70, 0.38, 1.6),
                           (0.06, 0.80, 0.36, 2.2),
                           (0.46, 0.66, 0.38, 2.6)):
        _fallen_leaf(surf, cx + R * fx, cy + R * fy, R * fl, fa,
                     _WD_LEAF_DEAD, _WD_LEAF_LO, R)
    _laurel_sprig(surf, cx, cy, R, _WD_LEAF_HI, _WD_LEAF_LO,
                  leaves=8, droop=1.0, curl=0.6, shed_lo=True)
    _laurel_bow(surf, cx, cy, R, _WD_LEAF_HI, _WD_LEAF_LO, undone=True)
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _WD_RIM_HI, _WD_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _WD_FACE_TOP, _WD_FACE_BOT, _WD_RECESS)
    _center(surf, glyph_key, cx, cy, R, _WD_GLY, _WD_GLY_SH)


# ═══════════════════════════════════════════════════════════════════════════
# 2) SASH — a star-medal hung on a draped ribbon sash + suspension bar.
#    Fame: a crisp gold suspension bar at the top, two bright royal-blue ribbon
#    tails draping down behind, and a five-point gold star pinned over the rim.
#    Shame: the SAME sash TORN — ribbon frayed and ripped half through, colour
#    bleached to washed grey, hanging crooked off a bent bar; the star sags
#    with a snapped point.
# ═══════════════════════════════════════════════════════════════════════════
_SA_RIM_HI  = (255, 232, 162)
_SA_RIM_MID = (232, 182,  70)
_SA_RIM_LO  = (150, 102,  20)
_SA_EDGE    = ( 70,  44,   8)
_SA_SPEC    = (255, 250, 222)
_SA_RIB_HI  = (108, 150, 232)     # royal-blue ribbon, lit
_SA_RIB_LO  = ( 40,  70, 150)     # ribbon shadow
_SA_BAR_HI  = (255, 226, 150)
_SA_BAR_LO  = (160, 110,  30)
_SA_FACE_TOP = ( 40,  30,  86)
_SA_FACE_BOT = ( 16,  10,  44)
_SA_RECESS   = ( 10,   6,  28)
_SA_GLY      = (255, 236, 184)
_SA_GLY_SH   = ( 32,  18,  44)

_SH_RIM_HI  = (150, 148, 150)
_SH_RIM_MID = ( 96,  94,  96)
_SH_RIM_LO  = ( 52,  50,  52)
_SH_EDGE    = ( 24,  22,  24)
_SH_RIB_HI  = (140, 138, 144)     # bleached-grey ribbon, lit
_SH_RIB_LO  = ( 78,  76,  82)     # ribbon shadow
_SH_BAR_HI  = (132, 130, 132)
_SH_BAR_LO  = ( 70,  68,  70)
_SH_FACE_TOP = ( 48,  46,  52)
_SH_FACE_BOT = ( 24,  22,  28)
_SH_RECESS   = ( 14,  12,  18)
_SH_GLY      = (172, 168, 158)
_SH_GLY_SH   = ( 16,  14,  16)


def _sash_tail(surf, x0, y0, length, w, hi, lo, sgn, torn=False, splay=0.30):
    """A ribbon tail draping down-out from the suspension bar. ``splay`` sets how
    far it fans outward (Fame keeps it tight so it never crowds the centre).
    ``torn`` rips it raggedly so the surviving stub hangs limp and crooked with a
    frayed end."""
    pts_l, pts_r = [], []
    steps = 11
    for i in range(steps + 1):
        f = i / steps
        yy = y0 + int(length * f)
        sp = int(f * length * splay * sgn)
        wave = int(math.sin(f * math.pi * 1.2) * w * 0.18 * sgn)
        if torn:
            # a torn tail necks in then dangles limp — width wobbles unevenly and
            # the whole stub drifts to one side (a slack hanging shred)
            taper = max(0.22, 1.0 - 0.5 * f - 0.18 * math.sin(f * 7))
            sp += int(f * f * w * 1.1 * sgn)        # drifts crooked as it falls
        else:
            taper = 1.0
        off = sp + wave
        pts_l.append((x0 - w * taper / 2 + off, yy))
        pts_r.append((x0 + w * taper / 2 + off, yy))
    poly = pts_l + pts_r[::-1]
    pygame.draw.polygon(surf, lerp_color(hi, lo, 0.4),
                        [(int(a), int(b)) for a, b in poly])
    pygame.draw.lines(surf, hi, False,
                      [(int(a), int(b)) for a, b in pts_l], max(2, w // 7))
    if not torn:
        # tidy fishtail notch at the end
        bx, by = pts_l[-1]
        ex = pts_r[-1][0]
        pygame.draw.polygon(surf, lo, [(int(bx), int(by)), (int(ex), int(by)),
                                       (int((bx + ex) / 2), int(by - w * 0.5))])
    else:
        # ragged frayed rip — several long uneven threads dangling off the cut so
        # the torn end reads even at small sizes
        bx, by = pts_l[-1]
        ex = pts_r[-1][0]
        for k in range(6):
            tx = bx + (ex - bx) * (k / 5)
            tl = w * (0.40 + 0.55 * ((k * 5) % 3) / 2)
            pygame.draw.line(surf, lo, (int(tx), int(by)),
                             (int(tx + sgn * w * 0.12), int(by + tl)),
                             max(1, w // 9))


def _suspension_bar(surf, cx, cy, R, hi, lo, edge, bent=False):
    bw = int(R * 0.92)
    bh = int(R * 0.26)
    by = int(cy - R * 1.14)
    rect = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for yy in range(bh):
        t = yy / max(1, bh - 1)
        pygame.draw.line(rect, lerp_color(hi, lo, t), (0, yy), (bw, yy))
    pygame.draw.rect(rect, edge, rect.get_rect(), max(1, R // 40),
                     border_radius=max(2, R // 14))
    if bent:
        # a dramatic crooked tilt + a sideways shove so the whole hanger reads as
        # knocked askew, a clear silhouette break vs. the level Fame bar
        rect = pygame.transform.rotate(rect, 19)
        cx = cx - int(R * 0.10)
    surf.blit(rect, rect.get_rect(center=(cx, by)))


def _sash_star(surf, cx, cy, R, hi, lo, edge, snapped=False):
    """A five-point star pinned at the top of the rim. ``snapped`` lops one
    point short so the medal star reads as damaged."""
    sy = int(cy - R * 0.82)
    sr = int(R * 0.40)
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = sr if i % 2 == 0 else sr * 0.42
        if snapped and i == 4:                      # one outer point broken off
            rad = sr * 0.5
        pts.append((cx + math.cos(ang) * rad, sy + math.sin(ang) * rad))
    pygame.draw.polygon(surf, lerp_color(hi, lo, 0.25),
                        [(int(x), int(y)) for x, y in pts])
    pygame.draw.polygon(surf, edge, [(int(x), int(y)) for x, y in pts],
                        max(1, R // 34))


def fame_sash(surf, cx, cy, R, glyph_key):
    _suspension_bar(surf, cx, cy, R, _SA_BAR_HI, _SA_BAR_LO, _SA_EDGE)
    # ribbons hang from the OUTER ends of the bar and stay tight (low splay) so
    # they drape past the rim's flanks instead of bunching behind the emblem
    for sgn in (-1, 1):
        _sash_tail(surf, cx + sgn * int(R * 0.44), int(cy - R * 1.04),
                   int(R * 1.90), int(R * 0.40),
                   _SA_RIB_HI, _SA_RIB_LO, sgn, torn=False, splay=0.16)
    _metal_band(surf, cx, cy, R, int(R * 0.74), _SA_RIM_HI, _SA_RIM_LO,
                spec=_SA_SPEC, edge=_SA_EDGE)
    pygame.draw.circle(surf, _SA_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _SA_RIM_HI, _SA_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _SA_FACE_TOP, _SA_FACE_BOT, _SA_RECESS)
    _sash_star(surf, cx, cy, R, _SA_BAR_HI, _SA_BAR_LO, _SA_EDGE, snapped=False)
    _center(surf, glyph_key, cx, cy, R, _SA_GLY, _SA_GLY_SH, ai._GLYPH_SHEEN)


def shame_sash(surf, cx, cy, R, glyph_key):
    _suspension_bar(surf, cx, cy, R, _SH_BAR_HI, _SH_BAR_LO, _SH_EDGE, bent=True)
    # one tail ripped to a short crooked stub, the other a long shred DROOPING
    # well past the bottom of the ring — the lopsided dangle breaks the outline
    _sash_tail(surf, cx - int(R * 0.30), int(cy - R * 1.02),
               int(R * 0.92), int(R * 0.42), _SH_RIB_HI, _SH_RIB_LO, -1,
               torn=True, splay=0.20)
    _sash_tail(surf, cx + int(R * 0.34), int(cy - R * 1.02),
               int(R * 2.40), int(R * 0.42), _SH_RIB_HI, _SH_RIB_LO, 1,
               torn=True, splay=0.22)
    _metal_band(surf, cx, cy, R, int(R * 0.74), _SH_RIM_HI, _SH_RIM_LO,
                spec=None, edge=_SH_EDGE)
    _oxide_mottle(surf, cx, cy, int(R * 0.78), int(R * 0.98),
                  (_SH_RIM_LO, _SH_EDGE), seed=23)
    pygame.draw.circle(surf, _SH_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _SH_RIM_HI, _SH_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _SH_FACE_TOP, _SH_FACE_BOT, _SH_RECESS)
    _sash_star(surf, cx, cy, R, _SH_BAR_HI, _SH_BAR_LO, _SH_EDGE, snapped=True)
    _center(surf, glyph_key, cx, cy, R, _SH_GLY, _SH_GLY_SH)


# ═══════════════════════════════════════════════════════════════════════════
# 3) SUNBURST — a radiant honour: pointed gold rays blazing out behind a struck
#    medal. Fame: a clean alternating long/short ray crown, every spike sharp
#    and gilded. Shame: the SAME rays DIMMED & MANGLED — bent and kinked,
#    several snapped to stubs, the tips soot-blackened so the radiance is dead.
# ═══════════════════════════════════════════════════════════════════════════
_SB_RIM_HI  = (255, 232, 160)
_SB_RIM_MID = (236, 184,  72)
_SB_RIM_LO  = (150, 102,  20)
_SB_EDGE    = ( 70,  44,   8)
_SB_SPEC    = (255, 250, 222)
_SB_RAY_HI  = (255, 222, 120)     # blazing ray crest
_SB_RAY_LO  = (196, 138,  40)     # ray shadow flank
_SB_FACE_TOP = ( 44,  32,  92)
_SB_FACE_BOT = ( 16,  10,  44)
_SB_RECESS   = ( 10,   6,  28)
_SB_GLY      = (255, 236, 184)
_SB_GLY_SH   = ( 32,  18,  44)

_DB_RIM_HI  = (146, 144, 148)
_DB_RIM_MID = ( 94,  92,  96)
_DB_RIM_LO  = ( 50,  48,  52)
_DB_EDGE    = ( 22,  20,  22)
_DB_RAY_HI  = (118, 112, 104)     # dead grey-brown ray, lit
_DB_RAY_LO  = ( 64,  58,  52)     # ray shadow
_DB_SOOT    = ( 30,  26,  26)     # soot-blackened ray tip
_DB_FACE_TOP = ( 48,  46,  52)
_DB_FACE_BOT = ( 24,  22,  28)
_DB_RECESS   = ( 14,  12,  18)
_DB_GLY      = (170, 164, 152)
_DB_GLY_SH   = ( 16,  14,  16)


def _sunburst(surf, cx, cy, R, ray_hi, ray_lo, n=16, base=None,
              mangled=False, soot=None):
    """A crown of pointed rays radiating from behind the rim. ``mangled`` bends
    each ray off-axis, snaps a deterministic subset to short stubs, and tips the
    survivors with ``soot`` so the burst reads dead rather than blazing."""
    base = base if base is not None else R * 1.04
    # On a mangled burst a few rays are SNAPPED to short stubs and a few clearly
    # DROOP (a big sideways bend) — a silhouette break, not just a grey recolour,
    # so the dead-burst read survives the shrink to 44px.
    snapped_set = {0, 6, 11} if mangled else set()
    droop_set = {3, 9, 14} if mangled else set()
    for i in range(n):
        a = i / n * math.tau - math.pi / 2
        long_ray = (i % 2 == 0)
        tip_len = (R * 0.46 if long_ray else R * 0.26)
        snapped = i in snapped_set
        drooped = i in droop_set
        kink = 0
        if snapped:
            tip_len *= 0.28                 # broken off near the root
        elif drooped:
            kink = math.radians(26)         # ray bent hard down to one side
            tip_len *= 0.86
        elif mangled:
            kink = math.radians(((i * 53) % 13) - 6)
        ad = a + kink
        tip = (cx + math.cos(ad) * (base + tip_len),
               cy + math.sin(ad) * (base + tip_len))
        half = math.radians(360 / n * (0.34 if long_ray else 0.24))
        b0 = (cx + math.cos(a - half) * base, cy + math.sin(a - half) * base)
        b1 = (cx + math.cos(a + half) * base, cy + math.sin(a + half) * base)
        d = (math.cos(a - _LIGHT) + 1) * 0.5
        col = lerp_color(ray_lo, ray_hi, d ** 1.3)
        pygame.draw.polygon(surf, col, [(int(b0[0]), int(b0[1])),
                                        (int(tip[0]), int(tip[1])),
                                        (int(b1[0]), int(b1[1]))])
        if soot is not None and not snapped:
            # soot the outer third of each surviving ray — a small dark wedge at
            # the (possibly bent) tip, narrowing toward the burnt point
            m0 = (cx + math.cos(ad - half * 0.5) * (base + tip_len * 0.58),
                  cy + math.sin(ad - half * 0.5) * (base + tip_len * 0.58))
            m1 = (cx + math.cos(ad + half * 0.5) * (base + tip_len * 0.58),
                  cy + math.sin(ad + half * 0.5) * (base + tip_len * 0.58))
            pygame.draw.polygon(surf, soot, [(int(m0[0]), int(m0[1])),
                                             (int(tip[0]), int(tip[1])),
                                             (int(m1[0]), int(m1[1]))])


def fame_sunburst(surf, cx, cy, R, glyph_key):
    blit_glow(surf, cx, cy, int(R * 1.5), (255, 210, 120), 70)
    _sunburst(surf, cx, cy, R, _SB_RAY_HI, _SB_RAY_LO, n=16)
    _metal_band(surf, cx, cy, R, int(R * 0.74), _SB_RIM_HI, _SB_RIM_LO,
                spec=_SB_SPEC, edge=_SB_EDGE)
    pygame.draw.circle(surf, _SB_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _SB_RIM_HI, _SB_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _SB_FACE_TOP, _SB_FACE_BOT, _SB_RECESS)
    _center(surf, glyph_key, cx, cy, R, _SB_GLY, _SB_GLY_SH, ai._GLYPH_SHEEN)


def shame_sunburst(surf, cx, cy, R, glyph_key):
    _sunburst(surf, cx, cy, R, _DB_RAY_HI, _DB_RAY_LO, n=16,
              mangled=True, soot=_DB_SOOT)
    _metal_band(surf, cx, cy, R, int(R * 0.74), _DB_RIM_HI, _DB_RIM_LO,
                spec=None, edge=_DB_EDGE)
    _oxide_mottle(surf, cx, cy, int(R * 0.78), int(R * 0.98),
                  (_DB_RAY_LO, _DB_RIM_LO), seed=37)
    pygame.draw.circle(surf, _DB_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _DB_RIM_HI, _DB_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _DB_FACE_TOP, _DB_FACE_BOT, _DB_RECESS)
    _center(surf, glyph_key, cx, cy, R, _DB_GLY, _DB_GLY_SH)


# ═══════════════════════════════════════════════════════════════════════════
# 4) COG — a gilded industrial gear medal: the disc set inside a toothed gear
#    wheel with bolt-studs and a hub ring. Fame: bright brass, crisp teeth, all
#    bolts present. Shame: the SAME gear RUSTED — orange oxide bleeding across
#    the teeth, several teeth chipped or broken clean off, bolts missing,
#    grime in the hub.
# ═══════════════════════════════════════════════════════════════════════════
_CG_RIM_HI  = (255, 226, 158)
_CG_RIM_MID = (228, 178,  74)
_CG_RIM_LO  = (150, 104,  26)
_CG_EDGE    = ( 78,  50,  12)
_CG_SPEC    = (255, 248, 218)
_CG_TOOTH_HI = (250, 210, 124)
_CG_TOOTH_LO = (158, 110,  34)
_CG_BOLT    = (255, 236, 176)
_CG_FACE_TOP = ( 44,  32,  92)
_CG_FACE_BOT = ( 16,  10,  44)
_CG_RECESS   = ( 10,   6,  28)
_CG_GLY      = (255, 236, 184)
_CG_GLY_SH   = ( 32,  18,  44)

_RG_RIM_HI  = (150, 120,  92)
_RG_RIM_MID = (108,  78,  54)
_RG_RIM_LO  = ( 64,  44,  30)
_RG_EDGE    = ( 32,  20,  14)
_RG_TOOTH_HI = (140,  96,  58)    # rusted tooth, lit
_RG_TOOTH_LO = ( 86,  52,  30)    # rust shadow
_RG_RUST    = (160,  78,  36)     # bright orange oxide bleed
_RG_RUST_DK = ( 96,  44,  22)
_RG_BOLT    = (120,  92,  64)
_RG_FACE_TOP = ( 50,  42,  38)
_RG_FACE_BOT = ( 26,  22,  20)
_RG_RECESS   = ( 16,  12,  10)
_RG_GLY      = (172, 150, 124)
_RG_GLY_SH   = ( 18,  14,  12)


def _gear(surf, cx, cy, R, tooth_hi, tooth_lo, n=12, broken=False,
          rust=None, rust_dk=None):
    """A toothed gear wheel sitting behind/around the disc. ``broken`` chips a
    deterministic subset of teeth down to stubs; ``rust`` mottles oxide across
    the ring so the gear reads corroded."""
    rin = int(R * 0.96)            # tooth root sits just outside the rim band
    rout = int(R * 1.20)
    # broken gear: two teeth are GONE entirely (flat notches in the outline) and
    # two more are sheared to jagged half-stubs — a real SILHOUETTE break that
    # survives a dark sky and 44px where the rust colour alone would not read.
    missing = {2, 9} if broken else set()
    half_stub = {5, 11} if broken else set()
    for i in range(n):
        if i in missing:
            continue
        a0 = (i + 0.18) / n * math.tau
        a1 = (i + 0.82) / n * math.tau
        am = (a0 + a1) / 2
        d = (math.cos(am - _LIGHT) + 1) * 0.5
        col = lerp_color(tooth_lo, tooth_hi, d ** 1.3)
        if i in half_stub:
            # one corner sheared off at root height — a jagged snapped tooth
            top = rin + int((rout - rin) * 0.45)
            pts = [
                (cx + math.cos(a0) * rin, cy + math.sin(a0) * rin),
                (cx + math.cos(a0 + 0.04) * top, cy + math.sin(a0 + 0.04) * top),
                (cx + math.cos(am) * rin, cy + math.sin(am) * rin),
                (cx + math.cos(a1) * rin, cy + math.sin(a1) * rin),
            ]
        else:
            top = rout
            pts = [
                (cx + math.cos(a0) * rin, cy + math.sin(a0) * rin),
                (cx + math.cos(a0 + 0.04) * top, cy + math.sin(a0 + 0.04) * top),
                (cx + math.cos(a1 - 0.04) * top, cy + math.sin(a1 - 0.04) * top),
                (cx + math.cos(a1) * rin, cy + math.sin(a1) * rin),
            ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])
    # the solid wheel body the teeth ride on
    pygame.draw.circle(surf, lerp_color(tooth_lo, tooth_hi, 0.4), (cx, cy), rin)
    if rust is not None:
        _oxide_mottle(surf, cx, cy, int(R * 0.80), rout, (rust, rust_dk),
                      seed=59, n=40)


def fame_cog(surf, cx, cy, R, glyph_key):
    _gear(surf, cx, cy, R, _CG_TOOTH_HI, _CG_TOOTH_LO, n=12)
    _metal_band(surf, cx, cy, R, int(R * 0.74), _CG_RIM_HI, _CG_RIM_LO,
                spec=_CG_SPEC, edge=_CG_EDGE)
    # bolt-studs riding the rim band
    for i in range(8):
        a = i / 8 * math.tau + math.radians(22)
        bx = cx + int(math.cos(a) * R * 0.86)
        by = cy + int(math.sin(a) * R * 0.86)
        pygame.draw.circle(surf, _CG_BOLT, (bx, by), max(2, R // 18))
        pygame.draw.circle(surf, _CG_EDGE, (bx, by), max(2, R // 18), max(1, R // 48))
    pygame.draw.circle(surf, _CG_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _CG_RIM_HI, _CG_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _CG_FACE_TOP, _CG_FACE_BOT, _CG_RECESS)
    _center(surf, glyph_key, cx, cy, R, _CG_GLY, _CG_GLY_SH, ai._GLYPH_SHEEN)


def shame_cog(surf, cx, cy, R, glyph_key):
    _gear(surf, cx, cy, R, _RG_TOOTH_HI, _RG_TOOTH_LO, n=12, broken=True,
          rust=_RG_RUST, rust_dk=_RG_RUST_DK)
    _metal_band(surf, cx, cy, R, int(R * 0.74), _RG_RIM_HI, _RG_RIM_LO,
                spec=None, edge=_RG_EDGE)
    _oxide_mottle(surf, cx, cy, int(R * 0.76), int(R * 0.98),
                  (_RG_RUST, _RG_RUST_DK), seed=71)
    # most bolts missing — only a couple cling on, the rest empty sockets
    for i in range(8):
        a = i / 8 * math.tau + math.radians(22)
        bx = cx + int(math.cos(a) * R * 0.86)
        by = cy + int(math.sin(a) * R * 0.86)
        if i in (1, 5):                          # surviving rusty bolts
            pygame.draw.circle(surf, _RG_BOLT, (bx, by), max(2, R // 18))
            pygame.draw.circle(surf, _RG_EDGE, (bx, by), max(2, R // 18), max(1, R // 48))
        else:                                    # empty oxide-stained hole
            pygame.draw.circle(surf, _RG_RUST_DK, (bx, by), max(2, R // 20))
            pygame.draw.circle(surf, _RG_EDGE, (bx, by), max(2, R // 20), max(1, R // 54))
    pygame.draw.circle(surf, _RG_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _RG_RIM_HI, _RG_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _RG_FACE_TOP, _RG_FACE_BOT, _RG_RECESS)
    _center(surf, glyph_key, cx, cy, R, _RG_GLY, _RG_GLY_SH)


# ═══════════════════════════════════════════════════════════════════════════
# 5) CORONET — a gemmed crown ring: the disc framed by a band of upswept crown
#    arches tipped with jewels. Fame: bright gold arches, each crowned with a
#    glinting ruby/sapphire/emerald, a beaded base band. Shame: the SAME
#    coronet WRECKED — gold dulled to grey, arches cracked and bent, the gems
#    fallen OUT leaving dark empty sockets, the bead band crumbled.
# ═══════════════════════════════════════════════════════════════════════════
_CR_RIM_HI  = (255, 232, 160)
_CR_RIM_MID = (236, 184,  72)
_CR_RIM_LO  = (150, 102,  20)
_CR_EDGE    = ( 70,  44,   8)
_CR_SPEC    = (255, 250, 222)
_CR_ARCH_HI = (252, 216, 118)
_CR_ARCH_LO = (160, 112,  34)
_CR_GEMS    = [(228, 64, 72), (72, 120, 228), (72, 200, 130),
               (228, 64, 72), (72, 120, 228), (72, 200, 130)]
_CR_GEM_HI  = (255, 244, 240)
_CR_FACE_TOP = ( 44,  32,  92)
_CR_FACE_BOT = ( 16,  10,  44)
_CR_RECESS   = ( 10,   6,  28)
_CR_GLY      = (255, 236, 184)
_CR_GLY_SH   = ( 32,  18,  44)

_WC_RIM_HI  = (148, 146, 150)
_WC_RIM_MID = ( 96,  94,  98)
_WC_RIM_LO  = ( 52,  50,  54)
_WC_EDGE    = ( 24,  22,  24)
_WC_ARCH_HI = (126, 122, 118)     # dulled grey-gold arch, lit
_WC_ARCH_LO = ( 72,  68,  64)     # arch shadow
_WC_SOCKET  = ( 22,  20,  24)     # empty dark gem socket
_WC_FACE_TOP = ( 48,  46,  52)
_WC_FACE_BOT = ( 24,  22,  28)
_WC_RECESS   = ( 14,  12,  18)
_WC_GLY      = (170, 164, 152)
_WC_GLY_SH   = ( 16,  14,  16)


def _coronet(surf, cx, cy, R, arch_hi, arch_lo, edge, n=7, gems=None,
             gem_hi=None, socket=None, wrecked=False):
    """A band of upswept crown arches around the top ~270deg of the rim, each
    tipped with a jewel (Fame) or an empty socket (Shame). ``wrecked`` cracks /
    bends the arches and drops the gems out."""
    band_r = int(R * 0.98)
    span = math.radians(244)        # leaves the base of the disc open
    a_start = math.radians(-212)    # sweep across the top
    # ASYMMETRIC wreckage so the crown's outline itself looks broken: one point
    # is snapped clean off (gone), two are sheared to jagged half-height stubs,
    # the rest survive but bent. The damage is uneven left-vs-right on purpose.
    gone = {4} if wrecked else set()
    snapped = {1, 5} if wrecked else set()
    gem_r = max(3, int(R * 0.11))
    for i in range(n):
        f = i / (n - 1)
        a = a_start + span * f
        half = math.radians(360 / n * 0.30)
        b0 = (cx + math.cos(a - half) * band_r, cy + math.sin(a - half) * band_r)
        b1 = (cx + math.cos(a + half) * band_r, cy + math.sin(a + half) * band_r)
        if i in gone:
            # the whole point broke off — a raw dark stump notch in the silhouette
            stump = (cx + math.cos(a) * (band_r + R * 0.06),
                     cy + math.sin(a) * (band_r + R * 0.06))
            pygame.draw.polygon(surf, edge, [(int(b0[0]), int(b0[1])),
                                             (int(stump[0]), int(stump[1])),
                                             (int(b1[0]), int(b1[1]))])
            continue
        # a triangular crown point (fleuron) rising off the rim band — a filled
        # merlon, not a stick, so the frame reads as regalia
        peak_h = R * (0.34 if i % 2 == 0 else 0.22)
        if i in snapped:
            peak_h *= 0.42                      # sheared to a jagged stub
        bend = math.radians(((i * 41) % 17) - 8) if wrecked else 0
        ad = a + bend
        peak = (cx + math.cos(ad) * (band_r + peak_h),
                cy + math.sin(ad) * (band_r + peak_h))
        d = (math.cos(a - _LIGHT) + 1) * 0.5
        col = lerp_color(arch_lo, arch_hi, d ** 1.3)
        if i in snapped:
            # a chunk knocked off one upper corner so the stub reads as broken
            mid = (cx + math.cos(ad) * (band_r + peak_h * 0.55),
                   cy + math.sin(ad) * (band_r + peak_h * 0.55))
            pygame.draw.polygon(surf, col, [(int(b0[0]), int(b0[1])),
                                            (int(peak[0]), int(peak[1])),
                                            (int(mid[0]), int(mid[1])),
                                            (int(b1[0]), int(b1[1]))])
        else:
            pygame.draw.polygon(surf, col, [(int(b0[0]), int(b0[1])),
                                            (int(peak[0]), int(peak[1])),
                                            (int(b1[0]), int(b1[1]))])
        pygame.draw.line(surf, edge, (int(b0[0]), int(b0[1])),
                         (int(peak[0]), int(peak[1])), max(1, R // 50))
        pygame.draw.line(surf, edge, (int(b1[0]), int(b1[1])),
                         (int(peak[0]), int(peak[1])), max(1, R // 50))
        if wrecked:
            # gem fallen out → a hollow dark socket: a dark cup with a lit lower
            # lip so it reads as an EMPTY hole, not a black gem
            pygame.draw.circle(surf, socket, (int(peak[0]), int(peak[1])), gem_r)
            pygame.draw.circle(surf, edge, (int(peak[0]), int(peak[1])),
                               gem_r, max(2, R // 30))
            pygame.draw.arc(surf, arch_hi,
                            (int(peak[0]) - gem_r, int(peak[1]) - gem_r,
                             gem_r * 2, gem_r * 2),
                            math.radians(200), math.radians(340), max(1, R // 40))
        else:
            gc = gems[i % len(gems)]
            pygame.draw.circle(surf, gc, (int(peak[0]), int(peak[1])), gem_r)
            pygame.draw.circle(surf, gem_hi,
                               (int(peak[0] - gem_r * 0.3), int(peak[1] - gem_r * 0.3)),
                               max(1, gem_r // 2))
            pygame.draw.circle(surf, edge, (int(peak[0]), int(peak[1])),
                               gem_r, max(1, R // 44))


def fame_coronet(surf, cx, cy, R, glyph_key):
    _coronet(surf, cx, cy, R, _CR_ARCH_HI, _CR_ARCH_LO, _CR_EDGE, n=7,
             gems=_CR_GEMS, gem_hi=_CR_GEM_HI)
    _metal_band(surf, cx, cy, R, int(R * 0.74), _CR_RIM_HI, _CR_RIM_LO,
                spec=_CR_SPEC, edge=_CR_EDGE)
    # beaded base band around the lower rim
    for i in range(11):
        a = math.radians(20) + i / 10 * math.radians(140)
        bx = cx + int(math.cos(a) * R * 0.90)
        by = cy + int(math.sin(a) * R * 0.90)
        pygame.draw.circle(surf, _CR_ARCH_HI, (bx, by), max(2, R // 24))
    pygame.draw.circle(surf, _CR_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _CR_RIM_HI, _CR_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _CR_FACE_TOP, _CR_FACE_BOT, _CR_RECESS)
    _center(surf, glyph_key, cx, cy, R, _CR_GLY, _CR_GLY_SH, ai._GLYPH_SHEEN)


def shame_coronet(surf, cx, cy, R, glyph_key):
    # The dropped gems first, tumbling at the lower rim — dimmed jewel tones so
    # they read as the SAME stones that fell out of the empty sockets above.
    for gx, gy, gr, gc in ((-0.42, 1.16, 0.10, (150, 56, 60)),    # dim ruby
                           (0.10, 1.30, 0.085, (52, 84, 150)),    # dim sapphire
                           (0.50, 1.10, 0.095, (54, 132, 92))):   # dim emerald
        cx2, cy2 = cx + int(R * gx), cy + int(R * gy)
        rr = max(2, int(R * gr))
        pygame.draw.circle(surf, gc, (cx2, cy2), rr)
        pygame.draw.circle(surf, _WC_EDGE, (cx2, cy2), rr, max(1, R // 50))
        pygame.draw.circle(surf, (210, 210, 218),
                           (cx2 - rr // 3, cy2 - rr // 3), max(1, rr // 3))
    _coronet(surf, cx, cy, R, _WC_ARCH_HI, _WC_ARCH_LO, _WC_EDGE, n=7,
             socket=_WC_SOCKET, wrecked=True)
    _metal_band(surf, cx, cy, R, int(R * 0.74), _WC_RIM_HI, _WC_RIM_LO,
                spec=None, edge=_WC_EDGE)
    _oxide_mottle(surf, cx, cy, int(R * 0.78), int(R * 0.98),
                  (_WC_RIM_LO, _WC_EDGE), seed=83)
    # crumbled bead band — most beads gone, a couple chipped survivors
    for i in range(11):
        a = math.radians(20) + i / 10 * math.radians(140)
        bx = cx + int(math.cos(a) * R * 0.90)
        by = cy + int(math.sin(a) * R * 0.90)
        if i in (2, 6, 9):
            pygame.draw.circle(surf, _WC_ARCH_LO, (bx, by), max(2, R // 28))
    pygame.draw.circle(surf, _WC_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _WC_RIM_HI, _WC_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _WC_FACE_TOP, _WC_FACE_BOT, _WC_RECESS)
    _center(surf, glyph_key, cx, cy, R, _WC_GLY, _WC_GLY_SH)


# Each concept pairs a Fame composer with its degraded Shame twin.
CONCEPTS = [
    ("wreath", fame_wreath, shame_wreath),
    ("sash", fame_sash, shame_sash),
    ("sunburst", fame_sunburst, shame_sunburst),
    ("cog", fame_cog, shame_cog),
    ("coronet", fame_coronet, shame_coronet),
]
