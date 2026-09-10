"""Round-2 look-dev sheet for the A7 TWINFACE devil-reaper boss.

One head split vertically down a hard gold seam: a pale bone SKULL half on the
left, a hot vermilion DEVIL half (single curved horn, slit eye, fang, goatee)
on the right -- the set's only asymmetric/two-natured head. Its signature prop
is a DOUBLE-BIT pole (a bone reaper-blade finial on one end, a devil spade-fork
finial on the other of the SAME banded shaft), which is symmetric by design and
therefore the cleanest top<->bottom pillar mirror in the whole devil set.

This is a headless review render only -- it imports the real game draw helpers
(_shade_c, lerp_color, blit_glow, make_glow_surface) so the explorations carry
the same triad/glow grammar as shipped art, supersamples then smoothscales for
crisp 1px keylines, and saves a labeled sheet. Nothing here is wired into the
live game.
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.draw import (
    _shade_c, lerp_color, blit_glow, make_glow_surface,
    make_gradient_surface,
)
from game.config import PIPE_W

# ── TWINFACE palette (from the A7 spec; the two halves are the two bases) ─────
INK        = (26, 20, 26)            # hard keyline ink shared with the set
# Bone / skull half -- Dante's between-white-and-yellow face, recast cream.
BONE       = (238, 230, 208)
BONE_SH    = (176, 156, 116)         # bone under-shade (dark-core)
BONE_HI    = (255, 250, 236)         # top-left rim sheen
SOCKET     = (54, 44, 52)            # hollow eye socket void
SULPHUR    = (244, 214, 70)          # the skull eye-spark / sulphur pinprick
# Devil half -- Dante's forward RED face, the hot vermilion. SH dropped deep so
# inked features and the horn read as crisp dark marks on the red (~30% more
# internal value range than round 1).
DEVIL      = (216, 48, 38)
DEVIL_SH   = (104, 16, 18)           # devil-skin dark-core (deepened)
DEVIL_HI   = (250, 150, 124)         # warm rim sheen -- now a small top tick only
HORN_BONE  = (236, 214, 168)         # the single horn keratin (lit edge only)
HORN_SH    = (118, 86, 44)           # horn body -- dark so it carries the silhouette
FANG       = (250, 246, 236)         # one bright fang
GOATEE     = (40, 30, 34)            # little devil chin-goatee
SLIT_EYE   = (250, 226, 96)          # hot slit pupil (matches sulphur family)
# The unifying accent: a GOLD seam running the centre divide + the pole bands.
GOLD       = (228, 184, 72)
GOLD_HI    = (255, 234, 158)
GOLD_SH    = (160, 120, 38)

OVERHANG = 12                        # guards may spill past the column edge


# ── helpers ───────────────────────────────────────────────────────────────────

def _outline_from_alpha(surf, color=INK, grow=1):
    """Grow a 1px silhouette keyline from the surface's own alpha mask so the
    figure POPS off any sky -- the house silhouette-pop discipline. Returns a NEW
    surface with the outline composited under the original art."""
    mask = pygame.mask.from_surface(surf, 8)
    out = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    olay = mask.to_surface(setcolor=(*color, 255), unsetcolor=(0, 0, 0, 0))
    for dx in range(-grow, grow + 1):
        for dy in range(-grow, grow + 1):
            if dx == 0 and dy == 0:
                continue
            out.blit(olay, (dx, dy))
    out.blit(surf, (0, 0))
    return out


def _triad_circle(surf, cx, cy, r, base, *, ss):
    """The dark-core -> flat-fill -> top-left rim-sheen triad on a round mass."""
    pygame.draw.circle(surf, _shade_c(base, -46), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, base, (int(cx), int(cy)), int(r - ss))
    pygame.draw.circle(surf, _shade_c(base, 40),
                       (int(cx - r * 0.34), int(cy - r * 0.34)),
                       max(1, int(r * 0.36)))


# ── the split head ─────────────────────────────────────────────────────────────

def _twin_head(surf, cx, cy, hr, ss, *, wink=True):
    """One chibi head, hard vertical GOLD seam down the middle. LEFT = bone skull
    (socket + sulphur spark + bone cheek), RIGHT = vermilion devil (slit eye, one
    curved horn, fang, goatee). The two halves pull opposite expressions -- the
    skull calm, the devil winking -- so it reads 'can't agree with itself'."""
    seam_x = cx
    # Draw the whole head as two flat half-discs split at the seam, each with its
    # own dark-core under-disc so neither half muddies into the other.
    left_rect = pygame.Rect(int(cx - hr - ss), int(cy - hr - ss),
                            int(hr + ss), int(2 * (hr + ss)))
    right_rect = pygame.Rect(int(cx), int(cy - hr - ss),
                             int(hr + ss), int(2 * (hr + ss)))

    # BONE half (clip to the left of the seam).
    prev = surf.get_clip()
    surf.set_clip(left_rect)
    pygame.draw.circle(surf, BONE_SH, (int(cx), int(cy)), int(hr))
    pygame.draw.circle(surf, BONE, (int(cx), int(cy)), int(hr - ss))
    pygame.draw.circle(surf, BONE_HI,
                       (int(cx - hr * 0.32), int(cy - hr * 0.40)),
                       max(1, int(hr * 0.34)))
    # DEVIL half (clip to the right of the seam).
    surf.set_clip(right_rect)
    pygame.draw.circle(surf, DEVIL_SH, (int(cx), int(cy)), int(hr))
    pygame.draw.circle(surf, DEVIL, (int(cx), int(cy)), int(hr - ss))
    # the warm sheen is now a SMALL top-far tick (pulled to the outer top corner,
    # away from the seam) so it stops reading as a soft red wound.
    pygame.draw.circle(surf, DEVIL_HI,
                       (int(cx + hr * 0.52), int(cy - hr * 0.54)),
                       max(1, int(hr * 0.16)))
    surf.set_clip(prev)

    # ── the GOLD seam: the second-loudest thing after the eyes -- a bold ridge
    # that visually CUTS the head in two at gameplay scale. Built as a wide dark
    # valley, a bright gold ridge on top, and a thin GOLD_HI catch-light. ~2x the
    # round-1 width; nothing else is allowed to sit beside it.
    valley_w = max(4, int(6 * ss))
    ridge_w  = max(3, int(3.4 * ss))
    pygame.draw.line(surf, GOLD_SH,
                     (int(seam_x), int(cy - hr + ss)),
                     (int(seam_x), int(cy + hr - ss)), valley_w)
    pygame.draw.line(surf, GOLD,
                     (int(seam_x), int(cy - hr + ss)),
                     (int(seam_x), int(cy + hr - ss)), ridge_w)
    pygame.draw.line(surf, GOLD_HI,
                     (int(seam_x - ridge_w * 0.28), int(cy - hr + 2 * ss)),
                     (int(seam_x - ridge_w * 0.28), int(cy + hr * 0.2)),
                     max(1, int(1.2 * ss)))

    # ── BONE half: a CALM hollow dark socket -- the value anchor that the devil
    # wink disagrees with. The sulphur spark stays a tiny pinprick deep in the
    # void (round 1's big glow filled the socket into a loud yellow disc); the
    # socket must read mostly dark + hollow so the two eyes are two moods.
    sk_ex = cx - hr * 0.42
    sk_ey = cy - hr * 0.12
    socket_r = max(2, int(hr * 0.32))
    pygame.draw.circle(surf, SOCKET, (int(sk_ex), int(sk_ey)), socket_r)
    pygame.draw.circle(surf, INK, (int(sk_ex), int(sk_ey)), socket_r, max(2, int(2 * ss)))
    # a small, contained spark deep in the lower socket -- glow kept tight so the
    # surrounding void stays dark.
    spark_y = sk_ey + socket_r * 0.34
    blit_glow(surf, int(sk_ex), int(spark_y), max(2, int(hr * 0.12)), SULPHUR, 120)
    pygame.draw.circle(surf, SULPHUR, (int(sk_ex), int(spark_y)),
                       max(1, int(hr * 0.07)))
    # bone cheekbone shade-line under the socket
    pygame.draw.line(surf, BONE_SH,
                     (int(cx - hr * 0.74), int(cy + hr * 0.18)),
                     (int(cx - hr * 0.16), int(cy + hr * 0.34)), max(1, int(1.4 * ss)))
    # skull teeth on the bone half of the jaw -- bright bone with dark separators
    jaw_y = cy + hr * 0.50
    for k in range(3):
        tx = cx - hr * (0.62 - 0.20 * k)
        tw = max(2, int(hr * 0.13))
        pygame.draw.rect(surf, BONE,
                         (int(tx - tw / 2), int(jaw_y), tw, max(2, int(hr * 0.22))))
        pygame.draw.rect(surf, BONE_SH,
                         (int(tx - tw / 2), int(jaw_y), tw, max(2, int(hr * 0.22))),
                         max(1, int(ss)))

    # ── DEVIL half: ONE horn (set guardrail = a single asymmetric profile horn,
    # NOT a curved-ram pair). Built as a SOLID tapering triangle that sweeps
    # steeply UP-and-back off the right brow with a thick base, so the lopsided
    # one-horn head reads in the blackout silhouette. Dark HORN_SH body carries
    # the read; HORN_BONE is only the lit front edge. Kept inside frame.
    hb_x = cx + hr * 0.46          # base sits just inside the head crown
    hb_y = cy - hr * 0.62
    base_half = hr * 0.30          # thick base
    tip = (cx + hr * 0.74, cy - hr * 1.46)   # steep, mostly-up tip (in frame)
    mid = (cx + hr * 0.74, cy - hr * 1.02)   # slight outward belly
    # solid horn body (dark) -- a curved tapering wedge
    body = [(hb_x - base_half, hb_y),
            (hb_x + base_half, hb_y - hr * 0.06),
            (mid[0], mid[1]),
            (tip[0], tip[1])]
    pygame.draw.polygon(surf, HORN_SH, [(int(p[0]), int(p[1])) for p in body])
    # lit keratin edge down the front (skull-facing) side only
    pygame.draw.lines(surf, HORN_BONE, False,
                      [(int(hb_x - base_half), int(hb_y)),
                       (int(mid[0] - hr * 0.10), int(mid[1])),
                       (int(tip[0]), int(tip[1]))], max(2, int(2 * ss)))
    # the back ink keyline so the horn pops off the red
    pygame.draw.lines(surf, INK, False,
                      [(int(hb_x + base_half), int(hb_y - hr * 0.06)),
                       (int(mid[0]), int(mid[1])),
                       (int(tip[0]), int(tip[1]))], max(2, int(2 * ss)))
    # two BOLD keratin nicks across the horn so it reads ridged, not a smooth tusk
    for ridge_t, span in ((0.34, 0.24), (0.62, 0.17)):
        rx = hb_x + (tip[0] - hb_x) * ridge_t * 0.5
        ry = hb_y + (tip[1] - hb_y) * ridge_t
        pygame.draw.line(surf, INK,
                         (int(rx - hr * span), int(ry)),
                         (int(rx + hr * span), int(ry - hr * 0.07)),
                         max(2, int(1.8 * ss)))

    # devil eye -- the WINK that disagrees with the calm hollow skull socket. A
    # bold INK closed downward-curl arc (a happy/sly shut lid), NO yellow disc.
    # If `wink` is off, a clear vertical INK slit on a lit lid -- still a crisp
    # dark mark, never a full yellow circle.
    dv_ex = cx + hr * 0.42
    dv_ey = cy - hr * 0.10
    if wink:
        # a smiling closed-eye curl: a thick ink arc bowing downward
        arc_w = max(3, int(2.8 * ss))
        pygame.draw.arc(surf, INK,
                        (int(dv_ex - hr * 0.34), int(dv_ey - hr * 0.30),
                         int(hr * 0.68), int(hr * 0.52)),
                        math.pi * 1.12, math.pi * 1.88, arc_w)
        # one cheeky upward lash flick on the outer corner
        pygame.draw.line(surf, INK,
                         (int(dv_ex + hr * 0.30), int(dv_ey - hr * 0.02)),
                         (int(dv_ex + hr * 0.44), int(dv_ey - hr * 0.12)),
                         max(2, int(1.6 * ss)))
    else:
        # a small lit almond lid with a hot vertical slit -- bold dark slit, no disc
        pygame.draw.ellipse(surf, DEVIL_HI,
                            (int(dv_ex - hr * 0.22), int(dv_ey - hr * 0.14),
                             int(hr * 0.44), int(hr * 0.28)))
        pygame.draw.ellipse(surf, INK,
                            (int(dv_ex - hr * 0.22), int(dv_ey - hr * 0.14),
                             int(hr * 0.44), int(hr * 0.28)), max(2, int(2 * ss)))
        pygame.draw.line(surf, INK,
                         (int(dv_ex), int(dv_ey - hr * 0.13)),
                         (int(dv_ex), int(dv_ey + hr * 0.13)), max(3, int(3 * ss)))
    # a sly cocked devil brow, INKED so it reads as a crisp dark mark on the red
    pygame.draw.line(surf, INK,
                     (int(dv_ex - hr * 0.30), int(dv_ey - hr * 0.30)),
                     (int(dv_ex + hr * 0.36), int(dv_ey - hr * 0.50)),
                     max(2, int(2.2 * ss)))

    # devil-side mouth: a grinning curl with ONE bright fang dropping below the
    # lip; the skull side keeps the flat tooth row, so the smile is two-natured.
    mly = cy + hr * 0.42
    mouth = []
    for k in range(9):
        t = k / 8.0
        mxp = cx + hr * (0.05 + 0.62 * t)
        # an upward-curling smirk: a shallow parabola that dips at the centre and
        # lifts the far (outer) corner so the devil half reads sly, not grim.
        myp = mly - hr * 0.14 * (1.0 - 4.0 * (t - 0.5) ** 2) - hr * 0.06 * t
        mouth.append((mxp, myp))
    # smirk INKED (was DEVIL_SH -- sank into the red and read grim); a crisp dark
    # sly curl now.
    pygame.draw.lines(surf, INK, False,
                      [(int(p[0]), int(p[1])) for p in mouth], max(2, int(2.4 * ss)))
    # the fang
    fx = cx + hr * 0.20
    fang_tri = [(fx - hr * 0.07, mly), (fx + hr * 0.10, mly),
                (fx, mly + hr * 0.26)]
    pygame.draw.polygon(surf, FANG, [(int(p[0]), int(p[1])) for p in fang_tri])
    pygame.draw.polygon(surf, INK,
                        [(int(p[0]), int(p[1])) for p in fang_tri], max(1, int(ss)))
    # little chin goatee tuft on the devil side
    goatee = [(cx + hr * 0.10, cy + hr * 0.74), (cx + hr * 0.40, cy + hr * 0.70),
              (cx + hr * 0.24, cy + hr * 1.02)]
    pygame.draw.polygon(surf, INK, [(int(p[0]), int(p[1])) for p in goatee])


def _split_robe(surf, cx, neck_y, body_w, body_h, ss):
    """A small chibi robe echoing the head's divide -- bone-cowl LEFT, vermilion
    RIGHT, gold seam down the centre -- so the whole figure reads two-natured."""
    top = neck_y
    bot = neck_y + body_h
    # trapezoid robe silhouette points
    pts_l = [(cx, top), (cx - body_w * 0.42, top + body_h * 0.30),
             (cx - body_w * 0.58, bot), (cx, bot)]
    pts_r = [(cx, top), (cx + body_w * 0.42, top + body_h * 0.30),
             (cx + body_w * 0.58, bot), (cx, bot)]
    pygame.draw.polygon(surf, BONE_SH, [(int(p[0]), int(p[1])) for p in pts_l])
    pygame.draw.polygon(surf, DEVIL_SH, [(int(p[0]), int(p[1])) for p in pts_r])
    # lit inner faces
    pygame.draw.polygon(surf, BONE,
                        [(int(cx - ss), int(top)), (int(cx - body_w * 0.30), int(top + body_h * 0.34)),
                         (int(cx - body_w * 0.40), int(bot - ss)), (int(cx - ss), int(bot - ss))])
    pygame.draw.polygon(surf, DEVIL,
                        [(int(cx + ss), int(top)), (int(cx + body_w * 0.30), int(top + body_h * 0.34)),
                         (int(cx + body_w * 0.40), int(bot - ss)), (int(cx + ss), int(bot - ss))])
    # gold seam + a gold clasp at the throat
    pygame.draw.line(surf, GOLD, (int(cx), int(top)), (int(cx), int(bot)), max(1, int(1.6 * ss)))
    pygame.draw.circle(surf, GOLD_SH, (int(cx), int(top + body_h * 0.12)), max(2, int(3 * ss)))
    pygame.draw.circle(surf, GOLD, (int(cx), int(top + body_h * 0.12)), max(2, int(2.2 * ss)))
    pygame.draw.circle(surf, GOLD_HI,
                       (int(cx - ss), int(top + body_h * 0.12 - ss)), max(1, int(ss)))


# ── the double-bit pole prop ────────────────────────────────────────────────────

def _skull_finial(surf, cx, tip_y, scale, ss, *, point_up):
    """The BONE end of the double-bit pole: a single bold REAPER CRESCENT blade.
    Deliberately NOT a skull -- round 1's twin-socket knob read as a second face
    competing with the boss head. Now it is one clean scythe crescent with a small
    gold collar at the haft; one dark slot only, never two eye-sockets. `point_up`
    flips the blade for the top cap vs the mirrored bottom cap."""
    d = -1 if point_up else 1
    kr = max(4, int(8 * scale))
    haft_y = tip_y + d * kr
    # gold collar where the blade meets the shaft (reads as a fitting, not a head)
    pygame.draw.circle(surf, GOLD_SH, (int(cx), int(haft_y)), max(2, int(kr * 0.55)))
    pygame.draw.circle(surf, GOLD, (int(cx), int(haft_y)), max(1, int(kr * 0.42)))
    # the crescent BLADE: a bold scythe sweeping out and curling to a point. Outer
    # arc then a tighter inner arc carve the concave hook.
    blade = []
    n = 16
    span = math.pi * 0.95
    for k in range(n):                      # outer (cutting) edge
        t = k / (n - 1)
        ang = math.pi * 0.08 + span * t
        rad = kr * 3.0
        bx = cx + math.cos(ang) * rad
        by = haft_y - d * (math.sin(ang) * rad * 0.78)
        blade.append((bx, by))
    for k in range(n):                      # inner (back) edge returning to haft
        t = 1 - k / (n - 1)
        ang = math.pi * 0.08 + span * t
        rad = kr * (3.0 - 1.25 - 0.55 * math.sin(math.pi * t))
        bx = cx + math.cos(ang) * rad
        by = haft_y - d * (math.sin(ang) * rad * 0.78)
        blade.append((bx, by))
    pygame.draw.polygon(surf, BONE_SH, [(int(p[0]), int(p[1])) for p in blade])
    # lit cutting edge along the outer arc
    pygame.draw.lines(surf, BONE, False,
                      [(int(p[0]), int(p[1])) for p in blade[:n]], max(2, int(2 * ss)))
    # a bright sulphur glint at the scythe point
    pygame.draw.circle(surf, SULPHUR, (int(blade[n - 1][0]), int(blade[n - 1][1])),
                       max(2, int(scale * 1.8)))


def _fork_finial(surf, cx, tip_y, scale, ss, *, point_up):
    """The DEVIL end of the double-bit pole: a bold, obvious TWO-PRONG spade fork.
    Mirror-twin of the skull crescent on the same shaft. Two clean straight prongs
    rising from a gold collar -- reads as a fork in silhouette at 1x."""
    d = -1 if point_up else 1
    base_y = tip_y
    # gold collar matching the skull haft so both ends read as a fitted pole
    cr = max(3, int(6 * scale))
    pygame.draw.circle(surf, GOLD_SH, (int(cx), int(base_y + d * cr)), max(2, int(cr * 0.7)))
    pygame.draw.circle(surf, GOLD, (int(cx), int(base_y + d * cr)), max(1, int(cr * 0.52)))
    prong_len = int(20 * scale)
    spread = int(9 * scale)
    half_w = max(2, int(3 * scale))
    for s in (-1, 1):
        root_x = cx + s * int(3 * scale)
        tipx = cx + s * spread
        tipy = base_y + d * prong_len
        # a tapering blade: wide root -> sharp barbed tip
        prong = [(root_x - half_w, base_y + d * cr),
                 (root_x + half_w, base_y + d * cr),
                 (tipx + s * half_w, base_y + d * int(prong_len * 0.55)),
                 (tipx, tipy)]
        pygame.draw.polygon(surf, DEVIL_SH, [(int(p[0]), int(p[1])) for p in prong])
        pygame.draw.polygon(surf, DEVIL,
                            [(int(p[0]), int(p[1])) for p in prong[:-1]], 0)
        # gold barb tip
        pygame.draw.circle(surf, GOLD, (int(tipx), int(tipy)), max(2, int(scale * 1.8)))
    # a centre spade-tail spike between the prongs (shorter, so two prongs dominate)
    spade = [(cx, base_y + d * cr),
             (cx + int(4 * scale), base_y + d * int(prong_len * 0.42)),
             (cx, base_y + d * int(prong_len * 0.72)),
             (cx - int(4 * scale), base_y + d * int(prong_len * 0.42))]
    pygame.draw.polygon(surf, DEVIL_SH, [(int(p[0]), int(p[1])) for p in spade])


def _double_bit_pole(surf, cx, top_y, bot_y, scale, ss, *, cap="skull"):
    """The banded pole BODY (the repeatable pillar shaft) running top_y..bot_y.
    Bone-and-gold barber bands wrap a dark core. `cap` chooses which finial sits at
    `top_y` (the other end gets the opposite finial, so the SAME pole is symmetric
    by design -- the cleanest top<->bottom mirror in the set)."""
    hw = max(3, int(6 * scale))
    # dark-core shaft
    pygame.draw.rect(surf, _shade_c(BONE_SH, -60),
                     (int(cx - hw), int(top_y), int(2 * hw), int(bot_y - top_y)))
    pygame.draw.rect(surf, BONE_SH,
                     (int(cx - hw + ss), int(top_y), int(2 * hw - 2 * ss), int(bot_y - top_y)))
    # gold banding rings down the shaft -- these ARE the repeatable pillar-body
    # texture (read at 1x).
    band_step = max(6, int(13 * scale))
    yy = top_y + band_step
    while yy < bot_y - band_step * 0.4:
        pygame.draw.rect(surf, GOLD_SH,
                         (int(cx - hw - ss), int(yy - 1.6 * ss), int(2 * hw + 2 * ss), max(2, int(3.4 * ss))))
        pygame.draw.rect(surf, GOLD,
                         (int(cx - hw - ss), int(yy - 0.6 * ss), int(2 * hw + 2 * ss), max(1, int(1.8 * ss))))
        yy += band_step
    # a lit rail down the bone side so the pole reads round
    pygame.draw.line(surf, BONE_HI,
                     (int(cx - hw * 0.5), int(top_y + ss)), (int(cx - hw * 0.5), int(bot_y - ss)),
                     max(1, int(ss)))


# ── sky backdrops (so explorations read like the real game) ─────────────────────

def _day_sky(w, h):
    return make_gradient_surface(w, h, [
        (0.0, (66, 150, 220)), (0.55, (120, 195, 235)), (1.0, (186, 226, 244))])


def _night_sky(w, h):
    s = make_gradient_surface(w, h, [
        (0.0, (12, 18, 55)), (0.45, (25, 40, 90)), (1.0, (44, 60, 120))])
    rng = __import__("random").Random(99)
    for _ in range(46):
        sx, sy = rng.randint(0, w - 1), rng.randint(0, int(h * 0.8))
        pygame.draw.circle(s, (255, 255, 255, 220), (sx, sy), rng.choice((1, 1, 2)))
    return s


# ── boss render (free-standing figure) ──────────────────────────────────────────

def render_boss(out_h, ss, *, wink=True):
    """Render the full TWINFACE figure (head + split robe + held double-bit pole)
    into a free-standing supersampled bitmap, then outline-pop + smoothscale."""
    out_w = int(out_h * 0.62)
    surf = pygame.Surface((out_w * ss, out_h * ss), pygame.SRCALPHA)
    cx = out_w * ss // 2
    hr = int(out_h * 0.20 * ss)
    head_cy = int(out_h * 0.30 * ss)
    # held pole leaning behind the figure (skull bit up, fork bit down)
    pole_x = cx + int(out_w * 0.30 * ss)
    _double_bit_pole(surf, pole_x, int(out_h * 0.12 * ss), int(out_h * 0.94 * ss),
                     ss * (out_h / 150.0), ss, cap="skull")
    _skull_finial(surf, pole_x, int(out_h * 0.12 * ss), ss * (out_h / 150.0), ss, point_up=True)
    _fork_finial(surf, pole_x, int(out_h * 0.94 * ss), ss * (out_h / 150.0), ss, point_up=False)
    # body robe under the head
    _split_robe(surf, cx, head_cy + hr - int(2 * ss),
                int(out_w * 0.74 * ss), int(out_h * 0.52 * ss), ss)
    # the split head on top
    _twin_head(surf, cx, head_cy, hr, ss, wink=wink)
    small = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _outline_from_alpha(small, INK, grow=1)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────────

def render_pillar_tile(h, ss, *, flip):
    """One PILLAR obstacle tile built straight from the double-bit pole: the banded
    shaft is the repeatable mid-body, a finial is the gap-edge cap. `flip` mirrors
    it top<->bottom -- because the pole is symmetric by design, both ends are clean
    caps (the cleanest mirror in the set)."""
    w = PIPE_W + 2 * OVERHANG
    surf = pygame.Surface((w * ss, h * ss), pygame.SRCALPHA)
    cx = w * ss // 2
    scale = ss * 1.05
    # The cap faces the gap. For a TOP pillar (flip), the gap is at the BOTTOM, so
    # the skull blade caps the bottom; for the BOTTOM pillar the skull caps the top.
    _double_bit_pole(surf, cx, int(8 * ss), int(h * ss - 8 * ss), scale, ss)
    _skull_finial(surf, cx, int(h * ss - 10 * ss), scale, ss, point_up=False)
    small = pygame.transform.smoothscale(surf, (w, h))
    out = _outline_from_alpha(small, INK, grow=1)
    if flip:
        out = pygame.transform.flip(out, False, True)
    return out


# ── sheet assembly ──────────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, *, color=(245, 240, 230)):
    surf.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def main():
    pygame.init()
    W, H = 1180, 760
    sheet = pygame.Surface((W, H))
    sheet.fill((30, 28, 38))
    title = pygame.font.SysFont("arial", 26, bold=True)
    lab = pygame.font.SysFont("arial", 16, bold=True)
    small = pygame.font.SysFont("arial", 13)

    _label(sheet, title, "A7  TWINFACE  -  the two-faced reaper-devil  (round 2)", 24, 16,
           color=(255, 224, 120))
    _label(sheet, small,
           "split head: bone SKULL half | gold seam | vermilion DEVIL half (single horn).  "
           "prop = symmetric DOUBLE-BIT pole -> cleanest pillar mirror.", 24, 48)

    # (a) boss at showcase scale -- on a neutral panel
    panel = pygame.Rect(24, 80, 320, 640)
    pygame.draw.rect(sheet, (46, 44, 56), panel, border_radius=8)
    pygame.draw.rect(sheet, (90, 86, 104), panel, 2, border_radius=8)
    boss = render_boss(560, 6, wink=True)
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2, panel.y + 36))
    _label(sheet, lab, "(a) boss @ showcase scale", panel.x + 12, panel.y + 8)

    # (b) the double-bit pole AS a tileable pillar pair (top cap + repeatable mid)
    bx = 372
    _label(sheet, lab, "(b) double-bit pole  ->  PILLAR pair", bx, 88)
    _label(sheet, small, "top cap + repeatable mid; symmetric mirror", bx, 108)
    gap_y = 300
    pil_w = PIPE_W + 2 * OVERHANG
    # TOP pillar (skull blade faces DOWN into the gap)
    top_pil = render_pillar_tile(gap_y - 132, 4, flip=True)
    sheet.blit(top_pil, (bx + 30, 132))
    # BOTTOM pillar (skull blade faces UP into the gap)
    bot_pil = render_pillar_tile(H - 24 - (gap_y + 96), 4, flip=False)
    sheet.blit(bot_pil, (bx + 30, gap_y + 96))
    # the gap band annotation
    pygame.draw.rect(sheet, (70, 66, 80),
                     (bx + 16, gap_y - 30, pil_w + 28, 120), 0, border_radius=6)
    _label(sheet, small, "GAP", bx + 16 + (pil_w + 28) // 2 - 14, gap_y + 22,
           color=(255, 220, 120))
    # re-blit the pillar ends over the gap band edges for clarity
    sheet.blit(top_pil, (bx + 30, 132))
    sheet.blit(bot_pil, (bx + 30, gap_y + 96))

    # (c) 1x insets on BOTH day and night skies
    cx0 = 620
    _label(sheet, lab, "(c) 1x insets  -  day  /  night sky", cx0, 88)
    inset_h = 300
    boss_1x = render_boss(140, 4, wink=True)
    pil_top_1x = render_pillar_tile(120, 4, flip=True)
    pil_bot_1x = render_pillar_tile(120, 4, flip=False)

    def _inset(x, y, sky_surf, name):
        panel = pygame.Rect(x, y, 250, inset_h)
        sheet.blit(sky_surf, (x, y))
        # ground strip
        pygame.draw.rect(sheet, (74, 150, 70) if name == "day" else (28, 60, 40),
                         (x, y + inset_h - 30, 250, 30))
        # boss + a tight pillar pair forming a gap, at TRUE 1x
        sheet.blit(boss_1x, (x + 26, y + inset_h - 30 - boss_1x.get_height()))
        sheet.blit(pil_top_1x, (x + 150, y - 6))
        sheet.blit(pil_bot_1x, (x + 150, y + 150))
        pygame.draw.rect(sheet, (255, 255, 255), panel, 2)
        _label(sheet, small, name.upper(), x + 8, y + 6,
               color=(20, 20, 30) if name == "day" else (240, 240, 255))

    _inset(cx0, 116, _day_sky(250, inset_h), "day")
    _inset(cx0 + 268, 116, _night_sky(250, inset_h), "night")

    # scary-cute / construction note panel
    note_y = 116 + inset_h + 18
    pygame.draw.rect(sheet, (44, 42, 54), (cx0, note_y, 518, 286), 0, border_radius=8)
    notes = [
        "CHIBI house style: flat fills + 1-2px ink keylines (26,20,26);",
        "dark-core -> fill -> top-left rim-sheen triad on every mass;",
        "silhouette POP via a 1px outline grown from the alpha mask.",
        "",
        "SCARY-CUTE: the two halves disagree -- the skull side stays",
        "calm (hollow socket, sulphur spark), the devil side WINKS",
        "(bold INK closed-arc, no yellow disc) with a sly cocked brow,",
        "one fang + ONE bold UP-swept horn. Menace, never grim.",
        "",
        "PROP -> PILLAR: the double-bit pole is symmetric by design,",
        "so the banded bone+gold shaft tiles as the pillar mid-body",
        "and EITHER finial caps the gap edge -- the set's cleanest",
        "top<->bottom mirror.",
        "",
        "GUARDRAIL: the devil half carries ONE curved horn only",
        "(no second ram pair); hard gold seam keeps the halves from",
        "muddying into a lumpy red skull.",
    ]
    for i, ln in enumerate(notes):
        _label(sheet, small, ln, cx0 + 14, note_y + 12 + i * 17,
               color=(225, 222, 232))

    out_dir = "/home/user/skybit/docs/skybit_devil/reapy_devil/twinface"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
