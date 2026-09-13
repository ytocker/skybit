"""Round-2 look-dev for the late-game EPIC event-boss concept `storm-wyrm`.

WHY: this is the ONE horizontal / non-humanoid entry in the boss set — epic by
LENGTH, not height. The whole sheet exists to prove three things the
art-director gated on: (1) the S-coil reads as ONE continuous menacing DRAGON
ribbon (head-end thickened, a clear spine-spike rhythm down the back) and not a
worm; (2) the head is a hard-browed dragon SKULL, not a cute snake; and (3) the
signature PROP resolves into a tall, top/bottom-mirrorable PILLAR.

Round-2 acts on the art-director's ITERATE notes, in order:
  (1) DAY SEPARATION — the slate thunderhead was the body's value, so the front
      half dissolved at 1x. The cloud bank is now dropped ~28% darker behind the
      front third of the body, AND a continuous 2px arc-white rim-light traces
      the dragon's TOP edge head→tail (also reads "charged").
  (2) ONE CONTINUOUS RIBBON — the bright beady belly chain (string-of-pearls /
      cute) is replaced by a single thin cyan under-glow line so the eye tracks
      one unbroken S; the top contour is one sweep skull→tail.
  (3) SPINE RHYTHM — a fixed 8 evenly-spaced spikes with a smooth large-at-
      shoulder → small-at-tail taper, all swept consistently back, reading as
      one serrated dorsal ridge.
  (4) TAIL TERMINUS — an authored brass-tipped barb + forked lightning fluke;
      the tail no longer fizzles into the under-glow.
  (5) HONEST LENGTH — the FULL creature is framed end-to-end inside one sky
      panel; the tail is NOT cropped at the frame edge.
  (6) 1x AT-SCALE INSET on BOTH day and night skies, drawn over the busy
      scrolling background with rain on — the true in-game pixel footprint and
      the SHIP gate for day legibility at real size.
  (7) the rearmost brass horn is raked well past 45° (run > rise) with a charged
      arc edge so it can never read as the vertical pillar-spine.

PROP DECISION (committed): the pillar is NOT a held glaive — a serpent gripping
a polearm never reads honestly. It is a vertical CHARGED LIGHTNING-SPINE SEGMENT
of the wyrm's own body: a forked, electrified spinal rod studded with brass
vertebra-knuckles, capped by a forked discharge crown at BOTH ends. A spine
segment is the one part of this creature that is intrinsically vertical and
end-symmetric, so an extracted segment mirrors top ↔ bottom into a clean pillar
pair with matching forked/charged ends — no handle/blade asymmetry to fake.

Headless + deterministic; touches nothing under game/. Output:
docs/epic_boss/storm-wyrm/round_2.png

    SDL_VIDEODRIVER=dummy python -m tools.render_epic_wyrm
"""
import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()

# ── palette (locked by the brief) ───────────────────────────────────────────
# Storm indigo body, electric cyan-white arc as the bright focal, brass trim.
INDIGO      = (60, 72, 140)
INDIGO_DEEP = (30, 38, 84)        # belly / underside shadow
INDIGO_LIT  = (96, 116, 196)      # top-lit ridge of each coil
ARC         = (180, 236, 255)     # high-key electric cyan-white — the focal
ARC_CORE    = (236, 250, 255)     # near-white bolt core
BRASS       = (214, 168, 72)
BRASS_LIT   = (248, 214, 128)
BRASS_DARK  = (150, 112, 44)
TOOTH       = (236, 240, 246)     # bone-white fangs / skull plate

DAY_SKY  = [(0.0, (96, 156, 212)), (0.55, (150, 196, 232)), (1.0, (206, 228, 244))]
NIGHT_SKY = [(0.0, (10, 14, 38)), (0.55, (22, 30, 66)), (1.0, (40, 52, 96))]
DAY_GROUND  = (58, 150, 70)
NIGHT_GROUND = (22, 54, 40)


def _clamp(v):
    return max(0, min(255, int(v)))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def grad_v(surf, rect, stops):
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        # piecewise multi-stop lerp
        for k in range(len(stops) - 1):
            t0, c0 = stops[k]
            t1, c1 = stops[k + 1]
            if t <= t1:
                seg = (t - t0) / (t1 - t0) if t1 > t0 else 0
                c = _mix(c0, c1, seg)
                break
        else:
            c = stops[-1][1]
        pygame.draw.line(surf, c, (x, y + i), (x + w - 1, y + i))


def glow(surf, cx, cy, radius, color, alpha=150, falloff=1.9):
    """Additive radial glow — the cyan arc carries legibility on both skies."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c0 = radius + 1
    for r in range(radius, 0, -1):
        a = int(alpha * (1 - (r / radius) ** falloff))
        pygame.draw.circle(s, (*color, max(0, a)), (c0, c0), r)
    surf.blit(s, (cx - c0, cy - c0), special_flags=pygame.BLEND_ADD)


# ── lightning ────────────────────────────────────────────────────────────────

def jagged(p0, p1, jag, segs, seed):
    """Midpoint-displaced polyline between two points — the bolt geometry."""
    rng = random.Random(seed)
    pts = [p0, p1]
    for _ in range(int(math.log2(max(2, segs)))):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            mx = (a[0] + b[0]) / 2
            my = (a[1] + b[1]) / 2
            nx = -(b[1] - a[1])
            ny = (b[0] - a[0])
            nl = math.hypot(nx, ny) or 1
            off = rng.uniform(-jag, jag)
            mx += nx / nl * off
            my += ny / nl * off
            out.append((mx, my))
            out.append(b)
        pts = out
        jag *= 0.55
    return pts


def bolt(surf, p0, p1, jag, seed, width=3, core=ARC_CORE, halo=ARC, glow_step=3):
    pts = jagged(p0, p1, jag, 32, seed)
    # outer cyan halo, then a hot near-white core stroke for the focal punch
    pygame.draw.lines(surf, halo, False, pts, width + 3)
    pygame.draw.lines(surf, core, False, pts, max(1, width - 1))
    if glow_step:
        for (x, y) in pts[::glow_step]:
            glow(surf, int(x), int(y), 4, ARC, alpha=95)


# ── the wyrm ──────────────────────────────────────────────────────────────────

def _spine_path(x0, x1, ymid, amp, waves, n):
    """Centreline of the S-body: a horizontal sine ribbon. Head-end (x1) sits a
    touch HIGHER so the creature rears its skull toward the player."""
    pts = []
    for i in range(n + 1):
        a = i / n
        x = x0 + (x1 - x0) * a
        # taper the wave amplitude toward the tail so the head end dominates
        amp_a = amp * (0.55 + 0.45 * a)
        rear = -22 * (a ** 2)        # head lifts
        y = ymid + math.sin(a * waves * math.tau + 0.4) * amp_a + rear
        pts.append((x, y))
    return pts


def _ribbon(path, half_at):
    """Build top + bottom edges of a variable-thickness ribbon from a centreline.
    `half_at(a)` gives the half-thickness at parameter a in [0,1]."""
    n = len(path) - 1
    top, bot = [], []
    for i, (x, y) in enumerate(path):
        a = i / n
        # local normal from neighbours
        px = path[max(0, i - 1)]
        nx = path[min(n, i + 1)]
        dx = nx[0] - px[0]
        dy = nx[1] - px[1]
        dl = math.hypot(dx, dy) or 1
        ox = -dy / dl
        oy = dx / dl
        h = half_at(a)
        top.append((x + ox * h, y + oy * h))
        bot.append((x - ox * h, y - oy * h))
    return top, bot


def _half_at_factory(base):
    """Thickness profile: needle tail tip → heavy bulk toward the head, with a
    slight neck pinch behind the skull. Shared so spikes/under-glow/rim/tail all
    sample the SAME contour and stay glued to one ribbon."""
    def half_at(a):
        swell = 0.10 + 1.18 * (a ** 1.6)
        pinch = 1.0 - 0.26 * math.exp(-((a - 0.88) ** 2) / 0.0014)
        tail = min(1.0, a / 0.09)           # taper the very tail to a whip point
        return base * swell * pinch * tail + 1.5
    return half_at


def draw_wyrm(surf, x0, x1, ymid, scale=1.0, t=0.0, lo_fi=False):
    """Draw the storm-wyrm sprawling left→right. The tail is the THIN end (x0),
    the SKULL is the THICK end (x1). t in [0,1] phases the spine-arc shimmer.

    `lo_fi` trims per-pixel glow passes for the tiny 1x at-scale inset, where
    they'd otherwise smear the whole footprint into a blob."""
    waves = 1.85
    amp = 50 * scale
    n = 140
    path = _spine_path(x0, x1, ymid, amp, waves, n)
    nn = len(path) - 1

    # Head-end thickening: a needle tail → HEAVY neck so the whole thing reads as
    # ONE menacing dragon ribbon, not a uniform worm.
    base = 30 * scale
    half_at = _half_at_factory(base)

    top, bot = _ribbon(path, half_at)
    body_poly = top + bot[::-1]

    # ── belly shadow underlay, then top-lit body ──
    shadow = [(x, y + 4 * scale) for (x, y) in body_poly]
    pygame.draw.polygon(surf, INDIGO_DEEP, shadow)
    pygame.draw.polygon(surf, INDIGO, body_poly)
    # a keyline so coils don't merge where the S overlaps itself
    pygame.draw.polygon(surf, _shade(INDIGO_DEEP, -10), body_poly,
                        max(1, int(2 * scale)))

    # top-lit ridge: a lighter band hugging the upper edge of the ribbon
    ridge = []
    for i, (x, y) in enumerate(path):
        a = i / nn
        ridge.append((x, y - half_at(a) * 0.62))
    if len(ridge) > 2:
        pygame.draw.lines(surf, INDIGO_LIT, False, ridge, max(2, int(3 * scale)))

    # ── ONE continuous cyan under-glow line (note 2) ──
    # Replaces the string-of-pearls belly orbs that chopped the body into cute
    # segments. A single thin charged line, traced just inside the belly contour,
    # pulls the eye along one unbroken S head→tail. Kept THIN (≈2px) so it shades
    # the underside rather than reading as discrete pearls.
    underglow = []
    for i, (x, y) in enumerate(path):
        a = i / nn
        underglow.append((x, y + half_at(a) * 0.50))
    if len(underglow) > 2:
        pygame.draw.lines(surf, _mix(INDIGO_DEEP, ARC, 0.40), False,
                          underglow, max(1, int(2.4 * scale)))
        pygame.draw.lines(surf, _mix(ARC, INDIGO, 0.15), False,
                          underglow, max(1, int(scale)))

    # ── top rim-light (note 1b): continuous 2px arc-white stroke, TOP edge ──
    # The single unbroken contour the eye reads as the dragon's silhouette
    # skull→tail; also the thing that lifts the front half OFF the slate cloud.
    rim = top[:]
    if len(rim) > 2:
        pygame.draw.lines(surf, _mix(INDIGO_LIT, ARC, 0.55), False,
                          rim, max(2, int(2.6 * scale)))
        pygame.draw.lines(surf, ARC, False, rim, max(1, int(1.5 * scale)))

    # ── spine-spike rhythm: ONE serrated dorsal ridge, regularized (note 3) ──
    # A FIXED count of evenly-PARAMETER-spaced spikes with a smooth length taper
    # (large at the shoulder → small at the tail), every spike swept the SAME
    # amount toward the tail (-x). Drawn front→back so nearer (shoulder) spikes
    # overlap farther ones, reinforcing a single ridge marching back.
    SPIKE_N = 8
    spikes = []
    for s in range(SPIKE_N):
        # behind the neck (0.80) to the base of the tail (0.14); off both ends
        a = 0.80 - (0.80 - 0.14) * (s / (SPIKE_N - 1))
        i = max(1, min(nn - 1, int(a * nn)))
        x, y = path[i]
        h = half_at(a)
        px = path[i - 1]
        nx = path[i + 1]
        dx = nx[0] - px[0]
        dy = nx[1] - px[1]
        dl = math.hypot(dx, dy) or 1
        ox, oy = -dy / dl, dx / dl        # outward (up) normal
        tx, ty = dx / dl, dy / dl         # tangent
        root_x = x + ox * h * 0.92
        root_y = y + oy * h * 0.92
        # smooth shoulder→tail length taper; a high at the shoulder
        sl = (8 + 24 * a) * scale
        sweep = 14 * scale                # identical rearward lean on every spike
        tip_x = root_x + ox * sl - sweep
        tip_y = root_y + oy * sl
        base_w = (3.5 + 4 * a) * scale
        bl = (root_x - tx * base_w, root_y - ty * base_w)
        br = (root_x + tx * base_w, root_y + ty * base_w)
        spikes.append((bl, br, (tip_x, tip_y), a))

    for bl, br, tip, a in spikes:
        col = _mix(INDIGO_LIT, BRASS_DARK, 0.4)
        pygame.draw.polygon(surf, _shade(col, -20), (bl, br, tip))
        pygame.draw.polygon(surf, BRASS, (bl, br, tip), 1)

    # ── lightning crackling ALONG the spine (the focal) ──
    tips = [s[2] for s in spikes]
    gstep = 0 if lo_fi else 3
    for k in range(len(tips) - 1):
        a = spikes[k][3]
        if (k + int(t * 3)) % 2 == 0 or a > 0.55:
            bolt(surf, tips[k], tips[k + 1], jag=6 * scale,
                 seed=k * 13 + int(t * 7), width=max(2, int(2 * scale)),
                 glow_step=gstep)
    # A faint, SMALL halo only — a big per-tip glow re-creates the very
    # string-of-pearls read note (2) killed, by bleeding bright discs along the
    # back. The lit bolt line already carries the charge.
    if not lo_fi:
        for (x, y) in tips:
            glow(surf, int(x), int(y), max(2, int(2.4 * scale)), ARC, alpha=70)

    # ── tail TERMINUS: brass-barbed forked lightning fluke (note 4) ──
    tx0, ty0 = path[0]
    txp, typ = path[1]
    ddx, ddy = tx0 - txp, ty0 - typ
    dl = math.hypot(ddx, ddy) or 1
    fx, fy = ddx / dl, ddy / dl           # forward along the tail (away from body)
    nx_, ny_ = -fy, fx                    # tail-tip normal
    bl_ = 18 * scale
    bw_ = 7 * scale
    barb_tip = (tx0 + fx * bl_, ty0 + fy * bl_)
    barb_l = (tx0 + nx_ * bw_, ty0 + ny_ * bw_)
    barb_r = (tx0 - nx_ * bw_, ty0 - ny_ * bw_)
    pygame.draw.polygon(surf, BRASS_DARK, (barb_l, barb_r, barb_tip))
    pygame.draw.polygon(surf, BRASS, (barb_l, barb_r, barb_tip), max(1, int(scale)))
    pygame.draw.line(surf, BRASS_LIT, (tx0, ty0), barb_tip, max(1, int(scale)))
    # two forked discharge lashes splaying off the barb tip
    bolt(surf, barb_tip,
         (barb_tip[0] + fx * 22 * scale + nx_ * 16 * scale,
          barb_tip[1] + fy * 22 * scale + ny_ * 16 * scale),
         jag=5 * scale, seed=99, width=max(1, int(2 * scale)), glow_step=gstep)
    bolt(surf, barb_tip,
         (barb_tip[0] + fx * 22 * scale - nx_ * 16 * scale,
          barb_tip[1] + fy * 22 * scale - ny_ * 16 * scale),
         jag=5 * scale, seed=100, width=max(1, int(2 * scale)), glow_step=gstep)
    if not lo_fi:
        glow(surf, int(barb_tip[0]), int(barb_tip[1]), max(3, int(3 * scale)),
             ARC, alpha=120)

    # ── the SKULL (drawn last so it crowns the heavy neck end) ──
    hx, hy = path[-1]
    _draw_skull(surf, hx, hy, scale * 1.35, t, lo_fi=lo_fi)


def _draw_skull(surf, cx, cy, scale, t, lo_fi=False):
    """Hard-browed dragon skull: angular brow plate, a single swept horn, a long
    jaw with bared fangs, and a cyan-furnace eye. Faces RIGHT (toward x1)."""
    s = scale
    # cranium / brow plate — angular, not round. Faces right.
    skull = [
        (cx - 34 * s, cy - 18 * s),   # back of skull top
        (cx - 6 * s,  cy - 30 * s),   # brow peak
        (cx + 18 * s, cy - 22 * s),   # over the eye
        (cx + 40 * s, cy - 6 * s),    # snout top
        (cx + 50 * s, cy + 4 * s),    # snout tip
        (cx + 40 * s, cy + 12 * s),   # upper lip
        (cx + 6 * s,  cy + 16 * s),   # cheek
        (cx - 30 * s, cy + 14 * s),   # jaw hinge
    ]
    pygame.draw.polygon(surf, INDIGO, skull)
    pygame.draw.polygon(surf, INDIGO_DEEP, skull, max(1, int(2 * s)))

    # bone brow ridge: a hard angular plate over the eye (the "hard-browed" read)
    brow = [(cx - 18 * s, cy - 20 * s), (cx + 4 * s, cy - 28 * s),
            (cx + 22 * s, cy - 18 * s), (cx + 8 * s, cy - 12 * s),
            (cx - 12 * s, cy - 12 * s)]
    pygame.draw.polygon(surf, _mix(INDIGO_LIT, TOOTH, 0.25), brow)
    pygame.draw.polygon(surf, BRASS, brow, 1)

    # lower jaw — long, dropped, angular
    jaw = [(cx - 28 * s, cy + 12 * s), (cx + 6 * s, cy + 14 * s),
           (cx + 36 * s, cy + 18 * s), (cx + 24 * s, cy + 26 * s),
           (cx - 24 * s, cy + 24 * s)]
    pygame.draw.polygon(surf, INDIGO_DEEP, jaw)
    pygame.draw.polygon(surf, _shade(INDIGO_DEEP, -12), jaw, 1)

    # bared fangs — two upper, two lower, bone-white
    for (fx, fy, dyf) in [(cx + 30 * s, cy + 12 * s, 8 * s),
                          (cx + 16 * s, cy + 13 * s, 7 * s)]:
        pygame.draw.polygon(surf, TOOTH,
                            [(fx - 3 * s, fy), (fx + 3 * s, fy), (fx, fy + dyf)])
    for (fx, fy, dyf) in [(cx + 26 * s, cy + 18 * s, -7 * s),
                          (cx + 10 * s, cy + 18 * s, -6 * s)]:
        pygame.draw.polygon(surf, TOOTH,
                            [(fx - 3 * s, fy), (fx + 3 * s, fy), (fx, fy + dyf)])

    # swept horn (note 7) — raked well past 45° (run > rise) over the neck so a
    # vertical pillar-spine sitting beside it can never read as one shaft; a thin
    # arc-white charged edge nails it as dragon-anatomy.
    horn = [(cx - 18 * s, cy - 22 * s), (cx - 56 * s, cy - 44 * s),
            (cx - 84 * s, cy - 58 * s), (cx - 80 * s, cy - 66 * s),
            (cx - 52 * s, cy - 50 * s), (cx - 10 * s, cy - 26 * s)]
    pygame.draw.polygon(surf, BRASS_DARK, horn)
    pygame.draw.polygon(surf, BRASS, horn, max(1, int(2 * s)))
    pygame.draw.line(surf, BRASS_LIT, (cx - 20 * s, cy - 24 * s),
                     (cx - 78 * s, cy - 60 * s), max(1, int(1 * s)))
    pygame.draw.line(surf, _mix(BRASS_LIT, ARC, 0.5), (cx - 22 * s, cy - 28 * s),
                     (cx - 80 * s, cy - 62 * s), max(1, int(1 * s)))
    # a second smaller cheek-horn, swept the SAME rearward direction (a pair)
    pygame.draw.polygon(surf, BRASS_DARK,
                        [(cx - 24 * s, cy - 4 * s), (cx - 50 * s, cy - 14 * s),
                         (cx - 26 * s, cy + 4 * s)])

    # cyan-furnace eye — a hot focal under the hard brow. The glow is kept TIGHT
    # (just hugging the slit) — a wide bloom reads as a blank clown-disc and
    # erases the mean angular slit the brief gates on.
    ex, ey = cx + 6 * s, cy - 8 * s
    if not lo_fi:
        glow(surf, int(ex), int(ey), max(3, int(5 * s)), ARC, alpha=150)
    pygame.draw.polygon(surf, ARC_CORE,
                        [(ex - 6 * s, ey), (ex + 6 * s, ey - 3 * s),
                         (ex + 4 * s, ey + 4 * s), (ex - 5 * s, ey + 3 * s)])
    pygame.draw.line(surf, INDIGO_DEEP, (ex - 5 * s, ey + 1 * s),
                     (ex + 5 * s, ey - 1 * s), max(2, int(2.4 * s)))  # slit pupil

    # nostril spark
    if not lo_fi:
        glow(surf, int(cx + 44 * s), int(cy + 2 * s), max(2, int(3 * s)),
             ARC, alpha=120)


# ── PILLAR: a vertical charged lightning-SPINE segment of the wyrm ────────────

def draw_spine_pillar(surf, cx, y_top, y_bot, w, flip=False, bg=False):
    """The signature prop, resolved as a PILLAR: a torn-off vertical segment of
    the wyrm's electrified SPINE. A central indigo spinal shaft, brass
    vertebra-knuckles runged up it, a cyan bolt crackling through the core, and a
    FORKED discharge crown at the END. End-symmetric by construction, so the
    top pillar and the (flipped) bottom pillar share identical forked/charged
    caps — a clean Flappy pillar pair.

    `flip=False` draws it as the TOP pillar (crown pointing DOWN into the gap);
    `flip=True` mirrors it vertically into the matching BOTTOM pillar."""
    h = y_bot - y_top
    half = w // 2

    def Y(yy):
        # vertical mirror about the segment's own span
        return (y_bot - (yy - y_top)) if flip else yy

    # shaft body gradient (deep at the rooted end → lit toward the gap end)
    seg = pygame.Surface((w, h), pygame.SRCALPHA)
    grad_v(seg, (0, 0, w, h),
           [(0.0, INDIGO_DEEP), (0.5, INDIGO), (1.0, INDIGO_LIT)])
    # round-ish vertebral silhouette: a column that bulges at each knuckle
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    n_knuck = 6
    for i in range(h):
        a = i / max(1, h - 1)
        bulge = 0.78 + 0.22 * abs(math.sin(a * n_knuck * math.pi))
        ww = int(half * bulge)
        pygame.draw.line(mask, (255, 255, 255, 255),
                         (half - ww, i), (half + ww, i))
    seg.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(seg, (cx - half, y_top))

    # brass vertebra-knuckles up the shaft
    for k in range(n_knuck):
        a = (k + 0.5) / n_knuck
        ky = Y(y_top + int(a * h))
        kr = int(half * 0.55)
        pygame.draw.ellipse(surf, BRASS_DARK,
                            (cx - kr, ky - kr // 2, kr * 2, kr))
        pygame.draw.ellipse(surf, BRASS,
                            (cx - kr + 1, ky - kr // 2 + 1, kr * 2 - 2, kr - 2), 1)
        pygame.draw.ellipse(surf, BRASS_LIT,
                            (cx - kr + 2, ky - kr // 2 + 1, kr - 2, max(1, kr // 2)))

    # `bg` pillars sit BEHIND the boss in the 1x inset — drawn quieter (no
    # per-segment bolt glow, dimmer crown) so they read as foreground clutter
    # the boss must out-read against, never as competing focals.
    gstep = 0 if bg else 3

    # the cyan bolt crackling up the spinal core (the focal that travels the rod)
    core_top = Y(y_top + 6)
    core_bot = Y(y_bot - 6)
    bolt(surf, (cx, core_top), (cx, core_bot), jag=w * 0.28, seed=7,
         width=3, core=ARC_CORE, halo=ARC, glow_step=gstep)

    # ── FORKED discharge crown at the GAP END (the end that faces the player) ──
    crown_y = Y(y_bot)
    direction = -1 if flip else 1     # forks point INTO the gap
    forks = [(-half, 1.4), (-half * 0.45, 1.9), (half * 0.45, 1.9), (half, 1.4)]
    for fx, fl in forks:
        ex = cx + fx
        ey = crown_y + direction * int(w * fl)
        bolt(surf, (cx, crown_y), (ex, ey), jag=w * 0.22,
             seed=int(fx) + 31, width=2, glow_step=gstep)
    # bright discharge node at the crown root — kept TIGHT (a hot bead, not a
    # halo) so a pillar pair flanking the boss can't wash the whole footprint
    # white in the 1x inset.
    node_a = 90 if bg else 140
    glow(surf, cx, crown_y, max(3, int(w * 0.45)), ARC, alpha=node_a)
    pygame.draw.circle(surf, ARC_CORE, (cx, crown_y), max(2, w // 6))
    # a brass collar ringing the crown root so it reads as a deliberate cap
    pygame.draw.ellipse(surf, BRASS,
                        (cx - half - 2, crown_y - w // 6, w + 4, w // 3), 2)


# ── busy scrolling background for the 1x at-scale insets ──────────────────────

def _busy_bg(w, h, sky_stops, ground_col, night, rain=True):
    """A miniature live-game backdrop (sky + thunderhead + scrolling pillars +
    ground + rain) so the 1x at-scale inset is judged in the conditions the boss
    actually ships in — the SHIP gate for day legibility at true size."""
    bg = pygame.Surface((w, h))
    grad_v(bg, (0, 0, w, h), sky_stops)
    gy = int(h * 0.86)

    # thunderhead bank behind the action (matches the panel cloud read)
    cloud = _mix(sky_stops[0][1], (30, 30, 50), 0.5) if not night else (12, 14, 30)
    for (ccx, ccy, crx, cry) in [(0.30, 0.30, 0.40, 0.18),
                                 (0.66, 0.26, 0.34, 0.15)]:
        pygame.draw.ellipse(bg, cloud,
                            (int((ccx - crx) * w), int((ccy - cry) * h),
                             int(crx * 2 * w), int(cry * 2 * h)))

    # a couple of scrolling spine-segment pillars so the inset has the real
    # foreground clutter the boss must out-read against
    pw = 26
    for px, gy_c, gh in [(int(w * 0.20), int(h * 0.50), 80),
                         (int(w * 0.82), int(h * 0.44), 92)]:
        gap_top = gy_c - gh // 2
        gap_bot = gy_c + gh // 2
        draw_spine_pillar(bg, px, -6, gap_top, pw, flip=False, bg=True)
        draw_spine_pillar(bg, px, gap_bot, gy, pw, flip=True, bg=True)

    # ground
    pygame.draw.rect(bg, ground_col, (0, gy, w, h - gy))
    pygame.draw.rect(bg, _shade(ground_col, 24), (0, gy, w, 3))

    # rain streaks
    if rain:
        rng = random.Random(4)
        rcol = _mix(ARC, sky_stops[0][1], 0.5)
        for _ in range(70):
            rx = rng.randint(0, w)
            ry = rng.randint(0, gy)
            pygame.draw.line(bg, rcol, (rx, ry), (rx - 2, ry + 7), 1)
    return bg


# ── compose the review sheet ──────────────────────────────────────────────────

def render():
    SS = 2                                # supersample for crisp curves
    PANEL_W, PANEL_H = 720, 560
    GAP = 24
    SIDE = 320                            # right column for scale + pillar-fit
    W = 24 + PANEL_W + GAP + SIDE + 24    # symmetric outer margins
    H = PANEL_H * 2 + GAP + 90
    sheet = pygame.Surface((W, H))
    sheet.fill((26, 28, 36))

    title_f = pygame.font.SysFont("dejavusans", 30, bold=True)
    lab_f = pygame.font.SysFont("dejavusans", 19, bold=True)
    sm_f = pygame.font.SysFont("dejavusans", 14)
    tiny_f = pygame.font.SysFont("dejavusans", 12)

    sheet.blit(title_f.render(
        "EPIC EVENT-BOSS  —  storm-wyrm  (round 2)", True, (236, 240, 246)), (24, 22))
    sheet.blit(sm_f.render(
        "Long sky-serpent DRAGON riding its thunderhead — epic by LENGTH. "
        "Indigo body / electric cyan-white arc / brass scale-trim.",
        True, (170, 200, 230)), (24, 58))

    # The in-game virtual canvas is 360x640; the 1x inset draws the boss at the
    # SAME pixel scale it ships at, so legibility is judged honestly.
    GAME_W, GAME_H = 360, 640
    INSET_W, INSET_H = 200, 356        # ~0.556x of the canvas, footprint-true

    def make_panel(sky_stops, ground_col, night):
        p = pygame.Surface((PANEL_W * SS, PANEL_H * SS))
        grad_v(p, (0, 0, PANEL_W * SS, PANEL_H * SS), sky_stops)
        gy = int(PANEL_H * SS * 0.86)
        pygame.draw.rect(p, ground_col, (0, gy, PANEL_W * SS, PANEL_H * SS - gy))
        pygame.draw.rect(p, _shade(ground_col, 24), (0, gy, PANEL_W * SS, 4 * SS))

        # thunderhead the wyrm rides. Note (1a): on DAY, the bank behind the
        # FRONT THIRD (where the head/neck sit) is dropped ~28% darker so the
        # bright-valued front half no longer dissolves into slate-on-slate.
        if night:
            cloud = (12, 14, 30)
            cloud_front = cloud
        else:
            cloud = _mix(sky_stops[0][1], (30, 30, 50), 0.5)
            cloud_front = _shade(cloud, -int(0.28 * 200))   # ~28% darker
        # rear / mid cloud puffs (normal value)
        for (ccx, ccy, crx, cry) in [(0.30, 0.40, 0.34, 0.17),
                                     (0.45, 0.46, 0.40, 0.14)]:
            pygame.draw.ellipse(p, cloud,
                                (int((ccx - crx) * PANEL_W * SS),
                                 int((ccy - cry) * PANEL_H * SS),
                                 int(crx * 2 * PANEL_W * SS),
                                 int(cry * 2 * PANEL_H * SS)))
        # the FRONT-THIRD darker bank, sitting under the head/neck end (right)
        for (ccx, ccy, crx, cry) in [(0.66, 0.34, 0.30, 0.16),
                                     (0.78, 0.40, 0.24, 0.13)]:
            pygame.draw.ellipse(p, cloud_front,
                                (int((ccx - crx) * PANEL_W * SS),
                                 int((ccy - cry) * PANEL_H * SS),
                                 int(crx * 2 * PANEL_W * SS),
                                 int(cry * 2 * PANEL_H * SS)))

        # the wyrm, full boss scale. Note (5): framed END-TO-END inside the
        # panel — the whip TAIL tip and the forked fluke sit well inside the
        # left edge, the skull well inside the right, so the full sprawl reads.
        draw_wyrm(p, x0=96 * SS, x1=(PANEL_W - 150) * SS,
                  ymid=PANEL_H * SS * 0.44, scale=2.0 * SS, t=0.0)
        return pygame.transform.smoothscale(p, (PANEL_W, PANEL_H))

    day = make_panel(DAY_SKY, DAY_GROUND, night=False)
    night = make_panel(NIGHT_SKY, NIGHT_GROUND, night=True)

    def make_inset(sky_stops, ground_col, night):
        """Note (6): the boss at its TRUE in-game pixel footprint, over the busy
        scrolling backdrop (rain on). No supersample — what ships at 360x640."""
        ins = _busy_bg(INSET_W, INSET_H, sky_stops, ground_col, night, rain=True)
        # at 1x the boss spans most of the playfield width; scale=1.0
        draw_wyrm(ins, x0=int(INSET_W * 0.16), x1=int(INSET_W * 0.86),
                  ymid=INSET_H * 0.40, scale=1.0, t=0.0, lo_fi=True)
        return ins

    y0 = 84

    # ── DAY panel + its 1x inset ──
    sheet.blit(day, (24, y0))
    pygame.draw.rect(sheet, (60, 64, 78), (24, y0, PANEL_W, PANEL_H), 1)
    sheet.blit(lab_f.render("DAY SKY  —  full length", True, (20, 30, 40)),
               (38, y0 + 12))
    day_inset = make_inset(DAY_SKY, DAY_GROUND, night=False)
    di_x = 24 + PANEL_W - INSET_W - 14
    di_y = y0 + PANEL_H - INSET_H - 14
    sheet.blit(day_inset, (di_x, di_y))
    pygame.draw.rect(sheet, (236, 240, 246), (di_x, di_y, INSET_W, INSET_H), 2)
    sheet.blit(tiny_f.render("1x AT-SCALE (rain on)", True, (236, 240, 246)),
               (di_x + 6, di_y + 4))

    # ── NIGHT panel + its 1x inset ──
    y1 = y0 + PANEL_H + GAP
    sheet.blit(night, (24, y1))
    pygame.draw.rect(sheet, (60, 64, 78), (24, y1, PANEL_W, PANEL_H), 1)
    sheet.blit(lab_f.render("NIGHT SKY  —  full length", True, (210, 230, 245)),
               (38, y1 + 12))
    night_inset = make_inset(NIGHT_SKY, NIGHT_GROUND, night=True)
    ni_x = 24 + PANEL_W - INSET_W - 14
    ni_y = y1 + PANEL_H - INSET_H - 14
    sheet.blit(night_inset, (ni_x, ni_y))
    pygame.draw.rect(sheet, (236, 240, 246), (ni_x, ni_y, INSET_W, INSET_H), 2)
    sheet.blit(tiny_f.render("1x AT-SCALE (rain on)", True, (236, 240, 246)),
               (ni_x + 6, ni_y + 4))

    # ── right column: skull detail + pillar-fit thumbnail ──
    rx = 24 + PANEL_W + GAP

    # skull close-up
    sk_h = 300
    sk = pygame.Surface((SIDE * SS, sk_h * SS))
    grad_v(sk, (0, 0, SIDE * SS, sk_h * SS), NIGHT_SKY)
    _draw_skull(sk, SIDE * SS * 0.42, sk_h * SS * 0.5, scale=3.0 * SS, t=0.0)
    sk = pygame.transform.smoothscale(sk, (SIDE, sk_h))
    sheet.blit(sk, (rx, y0))
    pygame.draw.rect(sheet, (60, 64, 78), (rx, y0, SIDE, sk_h), 1)
    sheet.blit(lab_f.render("SKULL — hard brow, swept horn", True, (210, 230, 245)),
               (rx + 10, y0 + 10))

    # pillar-fit thumbnail: the spine-segment prop mirrored top↔bottom
    pf_y = y0 + sk_h + GAP
    pf_h = PANEL_H * 2 + GAP - sk_h - GAP
    pf = pygame.Surface((SIDE * SS, pf_h * SS))
    grad_v(pf, (0, 0, SIDE * SS, pf_h * SS),
           [(0.0, (40, 52, 96)), (1.0, (10, 14, 38))])
    pw = 44 * SS
    midx = SIDE * SS * 0.5
    gap_top = pf_h * SS * 0.40
    gap_bot = pf_h * SS * 0.60
    # TOP pillar: rooted at panel top, forked crown discharging DOWN into gap
    draw_spine_pillar(pf, int(midx), 14 * SS, int(gap_top), pw, flip=False)
    # BOTTOM pillar: the SAME segment mirrored — forked crown discharging UP
    draw_spine_pillar(pf, int(midx), int(gap_bot), pf_h * SS - 14 * SS, pw,
                      flip=True)
    pf = pygame.transform.smoothscale(pf, (SIDE, pf_h))
    sheet.blit(pf, (rx, pf_y))
    pygame.draw.rect(sheet, (60, 64, 78), (rx, pf_y, SIDE, pf_h), 1)
    sheet.blit(lab_f.render("PILLAR-FIT", True, (210, 230, 245)), (rx + 10, pf_y + 8))
    sheet.blit(sm_f.render("charged SPINE segment,", True, (170, 200, 230)),
               (rx + 10, pf_y + 30))
    sheet.blit(sm_f.render("mirrored top <-> bottom", True, (170, 200, 230)),
               (rx + 10, pf_y + 46))

    out = "/home/user/skybit/docs/epic_boss/storm-wyrm/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    render()
