"""DESIGN EXPLORATION — Pip gets buried in a squall and ends as a SNOWMAN (the
full-cover end state). Throwaway sheet tool; touches NO game code.

ROUND 8. The lead is round-7 Variant 4 (2-ball - top-hat - arms-up). The
art-director signed off the face cluster (2 coal eyes, HORIZONTAL carrot
below-and-between them, coal smile arc), the W2 snow recipe on the contour, and
the flat-brim top hat — those are KEPT verbatim. This round POLISHES the lead
and settles ball-count by putting a clean 2-ball next to a *properly-necked*
3-ball at equal dressing quality.

Round-7 ITERATE fixes applied here:
  1. Ball-count A/B at equal quality. The 3-ball now reads as THREE distinct
     stacked spheres: classic ratio head:middle:base = 0.6 : 0.85 : 1.0 with a
     visible NECKING pinch at BOTH junctions. Round 7's 3-ball pear came from
     unioning two near-equal lower balls into one blob; we now CARVE an explicit
     inward pinch at each junction y-band so both seams read.
  2. Scarf slimmed ~30-40%: one wrap + a single hanging tail, thinner band so
     the neck pinch reads through it and the chin isn't crowded.
  3. Twig arms re-rooted on the UPPER THIRD of the body ball contour (not the
     gut), trunk thickened ~1px, with a fork so the tips don't dissolve.
  4. Button column tightened: 3-4 coal buttons with even, tight spacing down the
     true centreline of the lowest ball.
  5. Blue W2 under-edge confined to the bottom ~26% of EACH ball (not the whole
     lower body) so the cool shading SEPARATES the spheres instead of fusing
     them into a pear.
  6. Coal-cap direction cut entirely (read as a dirty/damaged crown).

CLEAN sheet: the lead front-and-centre, ~2-3 LARGE well-spaced variants, each
with a compact whiteout chip beneath proving the silhouette + value-carriers
(dark hat, warm carrot, cool-blue under-edge) survive a white sky.

numpy-free / pure pygame so the contour + recipe port straight into snow_fx.py.

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_snow_fullcover
Output: docs/snow_full_cover/round_8.png
"""
from __future__ import annotations

import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game import snow_fx
from game.draw import make_gradient_surface

OUT_DIR = os.path.join(ROOT, "docs", "snow_full_cover")
os.makedirs(OUT_DIR, exist_ok=True)

# Snow palette — VERBATIM from snow_fx so the snowman body is the shipped look.
WHITE = snow_fx.WHITE
OFF = snow_fx.OFF
BLUE = snow_fx.BLUE

# Snowman material palette (drawn ON TOP of the finished snow body). These are
# the value-contrast carriers against the white snow / white sky: a near-black
# hat + coal, a warm carrot, and the cool-blue snow under-edge.
CARROT = (240, 130, 32)
CARROT_HI = (255, 176, 92)
CARROT_RIDGE = (196, 92, 18)
COAL = (28, 30, 38)
COAL_HI = (96, 100, 112)
GLINT = (236, 244, 252)
TWIG = (110, 78, 48)
TWIG_HI = (150, 112, 74)
SCARF_RED = (210, 58, 62)
SCARF_DARK = (168, 40, 46)
SCARF_WHITE = (244, 248, 252)
HAT_BLACK = (32, 34, 44)
HAT_HI = (74, 78, 96)
HAT_BAND = (196, 60, 64)


# ── stacked-ball snowman contour (numpy-free) ────────────────────────────────
# A snowman is a column of vertically-aligned balls, each higher one smaller.
# We union the circles into one per-column (top, bot) envelope, then CARVE an
# inward necking pinch at each ball junction so the spheres stay distinct rather
# than fusing into a pear. `balls` is a list of (cy_fraction, radius_fraction) in
# cell-height units, ordered bottom-first (largest first). Returning the analytic
# ball list lets every kit element seat on a real centre — nothing floats.
def _snowman_contour(cw, ch, balls):
    cx = cw * 0.5
    circles = [(cx, ch * fy, ch * fr) for (fy, fr) in balls]

    top = [-1.0] * cw
    bot = [-1.0] * cw
    x_min, x_max = -1, -1
    for x in range(cw):
        ys = []
        for (ccx, ccy, rr) in circles:
            dx = x - ccx
            if abs(dx) <= rr:
                dy = math.sqrt(max(0.0, rr * rr - dx * dx))
                ys.append((ccy - dy, ccy + dy))
        if not ys:
            continue
        top[x] = min(y0 for y0, _ in ys)
        bot[x] = max(y1 for _, y1 in ys)
        if x_min < 0:
            x_min = x
        x_max = x
    if x_min < 0:
        return None

    # NECKING: a smooth union of two stacked balls bulges OUTWARD at the seam
    # (the circles overlap there), so without a carve two near-equal lower balls
    # fuse into one pear. We rebuild the silhouette so the body may never be wider
    # than a per-height "waist profile" — the max ball half-width at that y, but
    # tucked inward over a short band around each junction. Recomputing top/bot
    # against this profile (rather than nudging the union) guarantees a clean
    # pinch on the side view at every seam, and the smoothing pass below rounds
    # the tuck into a natural waist instead of a hard notch.
    def _max_half(yy):
        """Widest the body may be at height yy: the radius of whichever ball
        reaches farthest sideways here, minus a seam tuck near each junction."""
        half = 0.0
        for (ccx, ccy, rr) in circles:
            dy = abs(yy - ccy)
            if dy < rr:
                half = max(half, math.sqrt(rr * rr - dy * dy))
        for i in range(len(circles) - 1):
            ux, uy, ur = circles[i + 1]
            lx, ly, lr = circles[i]
            jy = (uy + ur + (ly - lr)) * 0.5
            band_y = (ur + lr) * 0.30
            d = abs(yy - jy)
            if d <= band_y:
                k = math.cos(d / band_y * math.pi) * 0.5 + 0.5   # 1 seam → 0 edge
                half = min(half, min(ur, lr) * (1.0 - 0.42 * k))
        return half

    for x in range(x_min, x_max + 1):
        if top[x] < 0:
            continue
        ex = abs(x - cx)
        # walk this column down; keep only the y-span where the waist profile is
        # wide enough to include this column. The kept span is the new silhouette.
        kept_top, kept_bot = -1.0, -1.0
        y = top[x]
        while y <= bot[x]:
            if _max_half(y) >= ex:
                if kept_top < 0:
                    kept_top = y
                kept_bot = y
            y += 1.0
        top[x] = kept_top
        bot[x] = kept_bot if kept_top >= 0 else -1.0

    # smooth the union seams so the column reads as one snow body, not stacked
    # discs — but the carve above keeps the waist visible.
    for _ in range(2):
        st, sb = list(top), list(bot)
        for x in range(x_min, x_max + 1):
            if top[x] < 0:
                continue
            ts = [top[k] for k in (x - 1, x, x + 1) if 0 <= k < cw and top[k] >= 0]
            bs = [bot[k] for k in (x - 1, x, x + 1) if 0 <= k < cw and bot[k] >= 0]
            if ts:
                st[x] = sum(ts) / len(ts)
            if bs:
                sb[x] = sum(bs) / len(bs)
        top, bot = st, sb
    return top, bot, x_min, x_max, circles


def _ball_bottom_at(circles, x):
    """The bottom y of whichever ball owns column x's lowest edge — lets the W2
    blue under-edge be confined to the bottom of EACH ball, so the shading marks
    every sphere's underside and helps separate the stack."""
    best = None
    for (ccx, ccy, rr) in circles:
        dx = x - ccx
        if abs(dx) <= rr:
            dy = math.sqrt(max(0.0, rr * rr - dx * dx))
            b = ccy + dy
            r = rr
            if best is None or b > best[0]:
                best = (b, r)
    return best  # (bottom_y, radius) or None


def _snow_body(ov, contour):
    """Run the faithful snow_fx W2 recipe per-column down the stacked contour:
    OFF fill + bright WHITE crest over the top 18% + cool-blue BLUE under-edge
    over the bottom 26% + a soft cornice overhang + the sine ripple.

    The blue under-edge is now confined PER BALL: it hugs the bottom 26% of the
    ball that owns each column, so each sphere gets its own shaded underside and
    the stack separates instead of reading as a single pear."""
    top, bot, x_min, x_max, circles = contour
    cw = len(top)
    taper_w = 14.0
    for x in range(cw):
        yt = top[x]
        yb = bot[x]
        if yt < 0 or yb < 0 or yb <= yt:
            continue
        # rear-weight the cornice from the left edge, as snow_fx does (the
        # tailwind drives accumulation onto the back/left shoulder).
        rear = 1.0 - (x - x_min) / max(1.0, x_max - x_min)
        te = snow_fx._smooth((x - x_min) / taper_w)
        over = snow_fx.CORNICE * rear * te
        nb = (math.sin(x * 1.26) + math.sin(x * 0.34)) * 0.25 + 0.5
        y0 = yt - over
        y1 = yb + (nb - 0.5) * 2.4
        d = y1 - y0
        if d < 1.0:
            continue
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.18)), 1)
        # per-ball blue under-edge: anchor the band to the owning ball's bottom
        owner = _ball_bottom_at(circles, x)
        if owner is not None:
            bb, br = owner
            band = max(2.0, br * 0.52)            # ≈ bottom 26% of the ball's diameter
            ub_top = min(y1 - 1, bb - band)
            ub_top = max(ub_top, y0 + d * 0.18 + 1)
            if y1 - ub_top >= 1.0:
                pygame.draw.line(ov, (*BLUE, 255), (x, int(ub_top)), (x, int(y1)), 1)
        else:
            pygame.draw.line(ov, (*BLUE, 255),
                             (x, int(y1 - d * 0.26)), (x, int(y1)), 1)


# ── classic-snowman kit, every element seated on an analytic ball centre ─────
def _coal_dot(ov, x, y, r, *, glint=False):
    pygame.draw.circle(ov, COAL, (int(round(x)), int(round(y))), int(r))
    if r >= 2:
        pygame.draw.circle(ov, COAL_HI, (int(round(x)), int(round(y))), int(r), 1)
    if glint:
        pygame.draw.circle(ov, GLINT,
                           (int(round(x - r * 0.4)), int(round(y - r * 0.4))), 1)


def _coal_eyes(ov, hx, hy, hr):
    """Two coal dots side by side, symmetric about the vertical axis, on the
    UPPER-FRONT of the head ball. (SIGNED OFF — unchanged.)"""
    r = max(2.0, hr * 0.16)
    sep = hr * 0.34
    ey = hy - hr * 0.30
    for s in (-1, +1):
        _coal_dot(ov, hx + s * sep, ey, r, glint=True)


def _carrot(ov, hx, hy, hr):
    """HORIZONTAL carrot nose, pointing forward (right), rooted on the head
    FRONT below-and-between the eyes. (SIGNED OFF — DO NOT TOUCH.)"""
    droop = math.radians(6.0)                    # barely-there droop, not up-cheek
    fx, fy = math.cos(droop), math.sin(droop)
    rx = hx - hr * 0.04
    ry = hy - hr * 0.04
    length = hr * 0.95
    half = max(2.4, hr * 0.20)                    # base half-height
    nx, ny = -fy, fx
    tip = (rx + fx * length, ry + fy * length)
    b1 = (rx + nx * half, ry + ny * half)
    b2 = (rx - nx * half, ry - ny * half)
    pygame.draw.polygon(ov, CARROT, [b1, tip, b2])
    pygame.draw.polygon(ov, CARROT_RIDGE, [b1, tip, b2], 1)
    for t in (0.34, 0.60, 0.82):
        cx = rx + (tip[0] - rx) * t
        cy = ry + (tip[1] - ry) * t
        hw = half * (1.0 - t) + 0.4
        pygame.draw.line(ov, CARROT_RIDGE,
                         (cx + nx * hw, cy + ny * hw),
                         (cx - nx * hw, cy - ny * hw), 1)
    pygame.draw.line(ov, CARROT_HI, b1, tip, 1)


def _coal_smile(ov, hx, hy, hr, *, n=5):
    """A short downward ARC of small coal dots BELOW the carrot — a smile that
    curves with the head ball. (SIGNED OFF — unchanged.)"""
    cy = hy + hr * 0.34
    span = hr * 0.92
    n = max(4, n)
    for i in range(n):
        t = i / (n - 1)
        px = hx + (t - 0.5) * span
        py = cy + math.sin(t * math.pi) * (hr * 0.20)   # downward curve
        _coal_dot(ov, px, py, max(1.2, hr * 0.075))


def _buttons(ov, bx, by, br, *, n=4, top_frac=-0.34, bot_frac=0.66):
    """EXACTLY n coal buttons evenly spaced down the TRUE centreline of the lowest
    ball, fully contained inside that ball: the column runs from by+top_frac*br to
    by+bot_frac*br. Defaults keep the top button well BELOW the scarf/neck pinch
    and the bottom button well ABOVE the ground-shadow edge, so neither end reads
    as a stray coal nor merges with the face smile-arc above."""
    r = max(2, int(br * 0.11))
    y_top = by + top_frac * br
    y_bot = by + bot_frac * br
    step = (y_bot - y_top) / max(1, n - 1)
    for i in range(n):
        _coal_dot(ov, bx, y_top + i * step, r)


def _twig_arms(ov, mx, my, mr, *, pose="up", overlap=4.0):
    """Two thin bare twigs rooted ON the body-ball snow, each ending in a fork so
    the tips don't dissolve. Trunk ~3px for legibility against snow.

    The root must sit ON the silhouette, never floating in the sky. We pick a root
    HEIGHT `ry` in the UPPER THIRD of the body ball — just below the neck pinch
    where the body is already WIDE — then measure the ACTUAL horizontal edge of
    the circle at that height (`dx = sqrt(r^2 - (ry-cy)^2)`) and plant the trunk a
    few px INSIDE that measured edge. Rooting from the true edge (not the ball's
    max radius `mr`, which it only reaches at the equator) guarantees the first
    branch segment starts on solid snow with zero daylight on either side."""
    # rise angle: arms go UP-and-out.
    ang = math.radians(40) if pose == "up" else math.radians(8)
    # root height: upper third of the body ball — below the neck pinch, where the
    # silhouette is still broad, so the measured edge sits deep in the snow.
    ry = my - mr * 0.45
    dx = math.sqrt(max(0.0, mr * mr - (ry - my) ** 2))
    for s in (-1, +1):
        # plant the root just INSIDE the measured circle edge at this height
        rx = mx + s * (dx - overlap)
        ln = mr * 1.10
        ex = rx + s * math.cos(ang) * ln
        ey = ry - math.sin(ang) * ln
        pygame.draw.line(ov, TWIG, (rx, ry), (ex, ey), 3)
        pygame.draw.line(ov, TWIG_HI, (rx, ry),
                         ((rx + ex) / 2, (ry + ey) / 2), 1)
        # forked fingers: a two-prong split at the tip + one branch midway, all
        # drawn thick enough to survive scaling.
        for fk, spread in ((1.0, (22, -26)), (0.60, (30,))):
            mxp = rx + (ex - rx) * fk
            myp = ry + (ey - ry) * fk
            for dd in spread:
                fa = ang + math.radians(dd)
                fr = ln * 0.40
                pygame.draw.line(ov, TWIG, (mxp, myp),
                                 (mxp + s * math.cos(fa) * fr,
                                  myp - math.sin(fa) * fr), 2)


def _scarf(ov, hx, neck_y, neck_w, *, style="single"):
    """Slimmed scarf (~30-40% less vertical coverage than round 7): ONE wrap band
    hugging the neck + a SINGLE hanging tail. Keeps the red/white stripe but the
    band is thin enough that the neck pinch still reads through it and it doesn't
    crowd the chin. `style` toggles a single short tail vs a longer two-tier tail
    for the dressing-alt variant."""
    band_h = neck_w * 0.23                        # thinned slightly at the neck pinch
    neck_y = neck_y + 1.5                          # drop the wrap ~1-2px off the chin
    nseg = max(3, int(band_h + 1))
    for i in range(nseg):
        t = i / max(1, nseg - 1)
        col = SCARF_RED if (i // 2) % 2 == 0 else SCARF_WHITE
        yy = neck_y - band_h * 0.5 + t * band_h
        hw = neck_w * (0.70 + 0.24 * math.sin(t * math.pi))   # hug the neck
        pygame.draw.line(ov, col, (hx - hw, yy), (hx + hw, yy), 1)
    pygame.draw.line(ov, SCARF_DARK, (hx - neck_w * 0.70, neck_y),
                     (hx + neck_w * 0.70, neck_y), 1)
    # ONE tail hanging down the right side
    tx = hx + neck_w * 0.58
    ty = neck_y + band_h * 0.4
    tail_len = neck_w * (1.25 if style == "long" else 0.85)
    seg = max(5, int(tail_len))
    for j in range(seg):
        t = j / seg
        x0 = tx + math.sin(t * 3.0) * 1.3                 # gentle flutter
        y0 = ty + t * tail_len
        col = SCARF_RED if (j // 2) % 2 == 0 else SCARF_WHITE
        pygame.draw.line(ov, col, (x0 - neck_w * 0.14, y0),
                         (x0 + neck_w * 0.14, y0), 2)


def _hat_top(ov, hx, hy, hr, *, tilt=0.0):
    """Black top hat sitting FLAT ON TOP of the head ball (SIGNED OFF): a
    horizontal brim of ~head-ball width on the crown, a vertical crown box and a
    red band. `tilt` (radians) gives the optional dressing-alt a jaunty lean
    without lifting the brim off the crown."""
    seat_y = hy - hr * 0.66                       # rests on the head crown
    brim_w = hr * 1.18
    brim_h = max(2.0, hr * 0.14)
    crown_w = hr * 0.78
    crown_h = hr * 1.25
    # brim (horizontal slab) — stays flat on the crown regardless of tilt
    pygame.draw.ellipse(ov, HAT_BLACK,
                        (hx - brim_w, seat_y - brim_h, brim_w * 2, brim_h * 2.2))
    # crown — optionally sheared sideways for a jaunty tilt
    cy_top = seat_y - crown_h
    shear = math.tan(tilt) * crown_h
    crown_pts = [
        (hx - crown_w, seat_y),
        (hx + crown_w, seat_y),
        (hx + crown_w + shear, cy_top),
        (hx - crown_w + shear, cy_top),
    ]
    pygame.draw.polygon(ov, HAT_BLACK, crown_pts)
    # red band at the crown base
    band_y = seat_y - crown_h * 0.20
    band_shear = shear * 0.16
    band_pts = [
        (hx - crown_w, band_y),
        (hx + crown_w, band_y),
        (hx + crown_w + band_shear, band_y - crown_h * 0.20),
        (hx - crown_w + band_shear, band_y - crown_h * 0.20),
    ]
    pygame.draw.polygon(ov, HAT_BAND, band_pts)
    # lit left + top edges so the felt reads as a solid block, not a void
    pygame.draw.line(ov, HAT_HI, (hx - crown_w, seat_y),
                     (hx - crown_w + shear, cy_top), 1)
    pygame.draw.line(ov, HAT_HI, (hx - crown_w + shear, cy_top),
                     (hx + crown_w + shear, cy_top), 1)


# ── face cluster shared by every variant (SIGNED-OFF placement) ──────────────
def _classic_face(ov, hx, hy, hr):
    _coal_eyes(ov, hx, hy, hr)
    _carrot(ov, hx, hy, hr)
    _coal_smile(ov, hx, hy, hr)


# ── junction helper (where the scarf wraps) ──────────────────────────────────
def _neck_y(circles, upper_i, lower_i):
    ux, uy, ur = circles[upper_i]
    lx, ly, lr = circles[lower_i]
    return (uy + ur + (ly - lr)) * 0.5


# ── the variant builders ─────────────────────────────────────────────────────
# Lead = 2-ball - top-hat - arms-up, fully polished. Alternate = a properly
# necked 3-ball at the classic head:middle:base = 0.6:0.85:1.0 ratio. Optional
# dressing-alt reuses the lead proportions with a jauntier hat + long tail.
def build_variant(cw, ch, key):
    if key == "2ball_lead":
        # head:body radius = 0.165:0.255 ≈ 0.65 : 1.0 — classic 2-ball.
        balls = [(0.70, 0.255), (0.345, 0.165)]
        contour = _snowman_contour(cw, ch, balls)
        circles = contour[4]
        body, head = circles
        def kit(ov, c):
            # arms rooted high on the body ball (upper third) — _twig_arms seats
            # them on the contour itself, so pass the body centre directly.
            _twig_arms(ov, body[0], body[1], body[2], pose="up")
            _buttons(ov, body[0], body[1], body[2], n=4)
            _classic_face(ov, head[0], head[1], head[2])
            _scarf(ov, head[0], _neck_y(circles, 1, 0), head[2] * 1.02, style="single")
            _hat_top(ov, head[0], head[1], head[2])
        return contour, kit

    if key == "3ball_alt":
        # classic ratio head:middle:base = 0.6:0.85:1.0. Base radius 0.205.
        # base=0.205, middle=0.205*0.85=0.174, head=0.205*0.60=0.123.
        # Centres spaced so neighbouring balls overlap only ~30% (room to pinch).
        rb, rm, rh = 0.205, 0.174, 0.123
        cyb = 0.80
        cym = cyb - (rb + rm) * 0.74                  # ~26% overlap → visible neck
        cyh = cym - (rm + rh) * 0.74
        balls = [(cyb, rb), (cym, rm), (cyh, rh)]
        contour = _snowman_contour(cw, ch, balls)
        circles = contour[4]
        base, mid, head = circles
        def kit(ov, c):
            _twig_arms(ov, mid[0], mid[1], mid[2], pose="up")
            # spread 4 buttons UP from the upper base into the empty mid-belly so
            # the front isn't unbuttoned; the top button still clears the mid-ball
            # waist and the bottom clears the ground shadow.
            _buttons(ov, base[0], base[1], base[2], n=4,
                     top_frac=-0.72, bot_frac=0.58)
            _classic_face(ov, head[0], head[1], head[2])
            _scarf(ov, head[0], _neck_y(circles, 2, 1), head[2] * 1.02, style="single")
            _hat_top(ov, head[0], head[1], head[2])
        return contour, kit

    if key == "2ball_dressalt":
        # same lead proportions, jauntier hat tilt + a longer single tail.
        balls = [(0.70, 0.255), (0.345, 0.165)]
        contour = _snowman_contour(cw, ch, balls)
        circles = contour[4]
        body, head = circles
        def kit(ov, c):
            _twig_arms(ov, body[0], body[1], body[2], pose="up")
            _buttons(ov, body[0], body[1], body[2], n=4)
            _classic_face(ov, head[0], head[1], head[2])
            _scarf(ov, head[0], _neck_y(circles, 1, 0), head[2] * 1.02, style="long")
            _hat_top(ov, head[0], head[1], head[2], tilt=math.radians(7.7))
        return contour, kit

    raise KeyError(key)


def render_snowman(cw, ch, key):
    """Full snowman cell: stacked snow body + classic kit, on a transparent
    surface so it can drop on any backdrop."""
    contour, kit = build_variant(cw, ch, key)
    body = pygame.Surface((cw, ch), pygame.SRCALPHA)
    _snow_body(body, contour)
    kit(body, contour)
    return body


# ── backdrops ────────────────────────────────────────────────────────────────
def sky_panel(w, h):
    return make_gradient_surface(w, h, [(0.0, (150, 192, 232)), (1.0, (206, 226, 244))])


def whiteout_panel(w, h):
    s = make_gradient_surface(w, h, [(0.0, (224, 232, 242)), (1.0, (204, 216, 232))])
    for i in range(int(w * h / 70)):
        x = (math.sin(i * 12.9898) * 43758.5) % 1.0 * w
        y = (math.sin(i * 78.233) * 12543.7) % 1.0 * h
        r = 1 + int((math.sin(i * 3.1) * 0.5 + 0.5) * 2)
        a = 130 + int((math.sin(i * 1.7) * 0.5 + 0.5) * 90)
        fl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(fl, (255, 255, 255, a), (r, r), r)
        s.blit(fl, (int(x), int(y)))
    return s


def ground_shadow(panel, cx, base_y, w):
    """A soft elliptical ground shadow so the snowman is planted, not floating."""
    sh = pygame.Surface((int(w), int(w * 0.22)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (40, 60, 90, 70), sh.get_rect())
    panel.blit(sh, (int(cx - w / 2), int(base_y - sh.get_height() * 0.5)))


# ── CLEAN sheet: the lead front-and-centre, well-spaced, whiteout chip each ──
VARIANTS = [
    ("LEAD  -  2-ball - top-hat - arms up", "2ball_lead", True),
    ("3-ball - necked (0.6:0.85:1.0) - top-hat", "3ball_alt", False),
    ("dressing alt - jaunty hat - long tail", "2ball_dressalt", False),
]


def main():
    # Render each snowman at a generous native resolution, then scale up. The
    # snowman is deliberately LARGER than the bird; we do NOT optimise for tiny
    # legibility. The LEAD gets the biggest tile, front-and-centre.
    CW, CH = 120, 168

    pad = 48
    gap = 52
    title_h = 110

    lead_w = 360                      # biggest — the hero
    alt_w = 280                       # supporting tiles a step smaller

    def hh(w):
        return int(w * CH / CW)

    chip_w = 156
    chip_h = hh(chip_w)
    label_h = 32
    chip_label_h = 22

    widths = [lead_w if is_lead else alt_w for _, _, is_lead in VARIANTS]
    col_ws = [max(w, chip_w) for w in widths]
    hero_hs = [hh(w) for w in widths]
    max_hero_h = max(hero_hs)

    n = len(VARIANTS)
    sheet_w = pad * 2 + sum(col_ws) + (n - 1) * gap
    sheet_h = (title_h + label_h + max_hero_h + 18 + chip_label_h + chip_h + pad)

    sheet = make_gradient_surface(sheet_w, sheet_h,
                                  [(0.0, (24, 30, 44)), (1.0, (16, 20, 30))])

    ftitle = pygame.font.SysFont("Arial", 30, bold=True)
    fsub = pygame.font.SysFont("Arial", 15)
    flabel = pygame.font.SysFont("Arial", 17, bold=True)
    fchip = pygame.font.SysFont("Arial", 12)

    GOLD = (242, 208, 122)
    WLBL = (230, 238, 250)
    DIM = (168, 182, 204)

    sheet.blit(ftitle.render(
        "Pip - SNOW FULL COVER -> SNOWMAN   *   ROUND 10: twig arms re-rooted on the silhouette edge",
        True, GOLD), (pad, 26))
    sheet.blit(fsub.render(
        "LEAD = 2-ball - top-hat - arms-up (SHIP). ONE fix this round: each twig arm is now rooted from the ACTUAL circle edge at its root height (dx = sqrt(r^2-(ry-cy)^2)) with a 4px inward overlap,",
        True, DIM), (pad, 62))
    sheet.blit(fsub.render(
        "planted in the UPPER THIRD of the lower body ball where the snow is wide - so there is zero sky gap on either side. Buttons, face, carrot, scarf, hat and W2 snow are UNCHANGED.",
        True, DIM), (pad, 82))

    natives = {key: render_snowman(CW, CH, key) for _, key, _ in VARIANTS}

    row_top = title_h + label_h
    x = pad
    for (label, key, is_lead), col_w, hero_w, hero_h in zip(
            VARIANTS, col_ws, widths, hero_hs):
        nat = natives[key]
        cx_col = x + col_w / 2

        # label centred over the column
        lbl = flabel.render(label, True, GOLD if is_lead else WLBL)
        sheet.blit(lbl, (int(cx_col - lbl.get_width() / 2), row_top - label_h + 4))

        # baseline-align the hero tiles so every snowman stands on one ground line
        row_y = row_top + (max_hero_h - hero_h)

        hero = sky_panel(hero_w, hero_h)
        big = pygame.transform.smoothscale(nat, (hero_w, hero_h))
        ground_shadow(hero, hero_w / 2, hero_h - hero_h * 0.06, hero_w * 0.46)
        hero.blit(big, (0, 0))
        hx0 = int(cx_col - hero_w / 2)
        sheet.blit(hero, (hx0, row_y))
        frame = (244, 210, 124) if is_lead else (96, 112, 140)
        pygame.draw.rect(sheet, frame, (hx0 - 2, row_y - 2, hero_w + 4, hero_h + 4),
                         2 if is_lead else 1)

        # whiteout chip below, baseline-anchored to the tallest column
        chip_label_y = row_top + max_hero_h + 14
        clbl = fchip.render("whiteout silhouette test", True, GOLD)
        sheet.blit(clbl, (int(cx_col - clbl.get_width() / 2), chip_label_y))
        chip = whiteout_panel(chip_w, chip_h)
        small = pygame.transform.smoothscale(nat, (chip_w, chip_h))
        chip.blit(small, (0, 0))
        cx0 = int(cx_col - chip_w / 2)
        cy0 = chip_label_y + chip_label_h
        sheet.blit(chip, (cx0, cy0))
        pygame.draw.rect(sheet, (130, 146, 172), (cx0 - 1, cy0 - 1, chip_w + 2, chip_h + 2), 1)

        x += col_w + gap

    out = os.path.join(OUT_DIR, "round_10.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
