"""IFRA — round 3 design sheet (Batch-2 Devilish, smokeless-fire genie devil).

FINAL pass. Folds in the round-2 AD critique in full (it was already past the
round-1 blocker — reads as a cocky crossed-arm fire-jinn, not a floating head).
Four finishing notes resolved:

  1. Crossed-arm fold no longer reads as a smooth horizontal SAUSAGE. The two
     forearms now cross with a HARD ink overlap seam + a value step between the
     over-arm (near) and under-arm (far), and the near fist nub sits proud of the
     silhouette — so the X-crossing reads as two arms at the 32px chip, not a bar.
  2. Head bumped back UP (~62% torso width, was ~58% and sunk) and LIFTED a few
     px clear of the shoulder line so the smug face — the charm carrier — gets
     breathing room and isn't pinched out small.
  3. Flame-horns sharpened from soft nubs to crisp back-swept FLAME shapes: a
     clear pointed tip with a concave back-edge flick + a saffron lit top-edge,
     so they read as flame (a silhouette tell) at the chip.
  4. Nose-ring re-seated UP onto a small defined SEPTUM nub, clear of the mouth
     line below it — so the single-gold-nose-ring tell is unambiguous, not a lip
     ring.

KEPT per critique: crossed-arm torso construction, short rounded smoke-curl
(Leyak separation), pinned palette exact (coral+violet+saffron live-fire), FLAT
hard-edged triad, the lamp-pillar mirror (already ship-ready).

Sheet grammar (brimstone sibling): (a) BOSS showcase scale, (b) PROP -> PILLAR
at true obstacle scale + a 2x gap zoom, (c) 1x in-game day/night legibility +
a grayscale silhouette check + a true-32px read row. House style: chibi, FLAT
triad fills (dark-core -> flat-fill -> top-left rim-sheen), hard ink keyline
grown 1px from the alpha mask, supersample -> smoothscale.

Run:  SDL_VIDEODRIVER=dummy python docs/skybit_devil/batch2/ifra/render_round3.py
Out:  docs/skybit_devil/batch2/ifra/round_3.png

Exploration only — nothing is wired into the live game.
"""

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

# ── PINNED PALETTE (exact hexes from the locked brief) ──────────────────────
EMBER      = (238, 108, 72)    # coral-ember body
RUST       = (176, 62, 42)     # deep-rust shade (dark core)
VIOLET     = (118, 86, 150)    # violet smoke-plume accent — cool counterweight
SAFFRON    = (255, 196, 96)    # hot-saffron flame-core
BRASS      = (214, 168, 72)    # brass lamp + nose-ring
INK        = (34, 20, 24)      # keyline ink
SHEEN      = (255, 182, 138)   # top-left rim sheen

# Derived working tints (value/sat steps of the pinned hues — never new hues).
EMBER_D    = (212, 90, 58)     # near-shade of the body, for the far (back) arm
EMBER_DD   = (188, 74, 48)     # one step deeper still — under-arm separation
VIOLET_D   = (76, 54, 104)     # deep smoke core
VIOLET_L   = (164, 134, 196)   # smoke top-left sheen
BRASS_D    = (138, 100, 38)    # lamp shade / deepened flute groove
BRASS_L    = (244, 214, 140)   # lamp sheen
COAL_GLOW  = (255, 150, 96)    # coal-eye inner glow (still in the fire family)

# ── Supersample kit (mirrors the project's buff-emblem / pillar conventions) ─
_SS = 4
_OW = max(2, 3 * _SS // 2)     # ~1.5px keyline at footprint after downsample


def _lerp(a, b, t):
    return a + (b - a) * t


def _mix(c1, c2, t):
    return (int(_lerp(c1[0], c2[0], t)),
            int(_lerp(c1[1], c2[1], t)),
            int(_lerp(c1[2], c2[2], t)))


def _shade(c, f):
    return (max(0, min(255, int(c[0] * f))),
            max(0, min(255, int(c[1] * f))),
            max(0, min(255, int(c[2] * f))))


def _raw(w, h):
    return pygame.Surface((w * _SS, h * _SS), pygame.SRCALPHA)


def _outline_from_alpha(surf, color, grow=1):
    """Grow a hard keyline OUTSIDE the alpha silhouette — the house POP trick.
    Built from the mask so it traces whatever shape we drew, not per-poly."""
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) < 2:
        return
    line = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(line, color, outline_pts, max(2, grow * _SS))
    base = surf.copy()
    surf.fill((0, 0, 0, 0))
    surf.blit(line, (0, 0))
    surf.blit(base, (0, 0))


def _triad_lobe(surf, pts, fill, core_color, sheen, core_inset=0.30, sink=0.20):
    """A hard flat flame/smoke lobe with the dark-core / flat-fill / TL-sheen
    triad — never a soft gradient. `core_color` is the lobe's OWN dark core
    (violet lobes get a violet-dark core; fire lobes get rust)."""
    pygame.draw.polygon(surf, fill, pts)
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    ymax = max(p[1] for p in pts)
    # Dark core: shrink toward centroid, biased DOWN (heat/shade pools low).
    core_pts = [(_lerp(px, cx, core_inset),
                 _lerp(py, cy + (ymax - cy) * sink, core_inset)) for (px, py) in pts]
    pygame.draw.polygon(surf, core_color, core_pts)
    # Top-left rim sheen: a thin bright shard along the upper-left edge.
    sx, sy = min(p[0] for p in pts), min(p[1] for p in pts)
    sheen_pts = [(_lerp(px, sx, 0.34), _lerp(py, sy, 0.34)) for (px, py) in pts]
    pygame.draw.polygon(surf, sheen, sheen_pts[:max(3, len(sheen_pts) // 2 + 1)])


def _fire_heart(surf, pts):
    """Nest a saffron live-fire heart deepest inside a fire lobe."""
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    heart = [(_lerp(px, cx, 0.58), _lerp(py, cy, 0.58)) for (px, py) in pts]
    pygame.draw.polygon(surf, SAFFRON, heart)


# ── IFRA the creature ───────────────────────────────────────────────────────
def build_ifra(W, H, bob=0):
    """Layout (top -> bottom), brimstone-sibling proportions:
      • SMUG HEAD (~62% of torso width, lifted clear of the shoulders) with two
        SHARP back-swept flame-horns, ember coal-eyes, a septum nose-ring nub.
      • BROAD crossed-beefy-arms TORSO: shoulders wider than the head, two fat
        forearms folded X across the chest — drawn far-then-near with a HARD ink
        overlap seam + value step so the X-crossing reads as two arms, not a bar.
      • WAIST nips in and dissolves into a compact billowing VIOLET smoke-curl
        base — kept SHORT/rounded so it never reads as Leyak's long trail.
    Drawn in a local SS surface; the hard keyline is grown from the final alpha.
    """
    s = _raw(W, H)
    S = _SS
    cx = W * S // 2
    yb = bob * S

    def X(f):  # width fraction -> SS px offset from center
        return int(W * f) * S

    def Y(f):  # height fraction -> SS px (absolute) with bob
        return int(H * f) * S + yb

    # ---- 1) Violet smoke-curl base (the no-legs blob) ----------------------
    # Compact + billowing, widening toward the floor then pinching back — a fat
    # CURL, not a long streamer. Sits below the waist; cool counterweight.
    plume_top = Y(0.66)
    for sgn in (-1, 1):
        curl = [
            (cx + sgn * X(0.05), plume_top),
            (cx + sgn * X(0.28), Y(0.79)),
            (cx + sgn * X(0.30), Y(0.91)),
            (cx + sgn * X(0.12), Y(0.985)),
            (cx, Y(0.94)),
        ]
        _triad_lobe(s, curl, VIOLET, VIOLET_D, VIOLET_L, core_inset=0.34, sink=0.28)
    # a small inner saffron ember tongue licking up through the smoke (focal)
    tongue = [
        (cx, Y(0.68)),
        (cx + X(0.10), Y(0.81)),
        (cx, Y(0.91)),
        (cx - X(0.10), Y(0.81)),
    ]
    _triad_lobe(s, tongue, EMBER, RUST, SHEEN, core_inset=0.30, sink=0.30)
    _fire_heart(s, tongue)

    # ---- 2) Crossed-arm TORSO ----------------------------------------------
    # Heavy upper body: wide shoulders, hard nip at the waist (the genie "V").
    sh_y = Y(0.42)            # shoulder line — sits below the lifted head
    sh_w = X(0.42)           # half shoulder width (wider than the head)
    waist_y = Y(0.66)
    waist_w = X(0.15)
    torso = [
        (cx - sh_w, sh_y),
        (cx - X(0.46), Y(0.49)),       # deltoid bulge
        (cx - X(0.30), Y(0.60)),
        (cx - waist_w, waist_y),
        (cx + waist_w, waist_y),
        (cx + X(0.30), Y(0.60)),
        (cx + X(0.46), Y(0.49)),
        (cx + sh_w, sh_y),
    ]
    pygame.draw.polygon(s, EMBER, torso)
    # dark-core pooled low (belly), TL chest sheen
    pygame.draw.polygon(s, RUST, [
        (cx - X(0.26), Y(0.54)), (cx + X(0.26), Y(0.54)),
        (cx + waist_w, waist_y), (cx - waist_w, waist_y),
    ])
    pygame.draw.polygon(s, SHEEN, [
        (cx - X(0.40), sh_y + 2 * S),
        (cx - X(0.16), Y(0.46)),
        (cx - X(0.22), Y(0.56)),
        (cx - X(0.42), Y(0.51)),
    ])

    # ---- 3) Crossed beefy arms (classic genie fold) ------------------------
    # Two fat forearms lying X across the chest; round biceps cap the shoulders.
    # FIX #1: drawn FAR-then-NEAR with (a) the far/under arm one value step DARKER
    # than the near/over arm, (b) a hard ink overlap SEAM where the near arm
    # crosses over the far, and (c) the near fist nub pushed PROUD of the
    # silhouette — so the X-fold reads as two crossed arms at 32px, not a sausage.
    bicep_y = Y(0.46)
    # biceps (shoulder caps) — far first so near overlaps cleanly
    for sgn in (-1, 1):
        col = EMBER_D if sgn < 0 else EMBER
        pygame.draw.circle(s, col, (cx + sgn * X(0.36), bicep_y), X(0.14))

    def _forearm(sgn, near):
        # forearm as a thick tapering bar shoulder -> opposite hip
        col = EMBER if near else EMBER_DD          # value STEP: under-arm darker
        core = RUST if near else _shade(RUST, 0.82)
        fa = [
            (cx + sgn * X(0.42), Y(0.455)),        # outer shoulder
            (cx + sgn * X(0.30), Y(0.495)),
            (cx - sgn * X(0.24), Y(0.615)),        # crossing to far ribs
            (cx - sgn * X(0.36), Y(0.595)),
            (cx + sgn * X(0.18), Y(0.475)),
        ]
        pygame.draw.polygon(s, col, fa)
        # forearm dark-core underside (the shadow band the AD confirmed reads)
        pygame.draw.polygon(s, core, [
            (cx + sgn * X(0.30), Y(0.52)),
            (cx - sgn * X(0.24), Y(0.62)),
            (cx - sgn * X(0.36), Y(0.595)),
            (cx - sgn * X(0.12), Y(0.545)),
        ])
        # chunky fist tucked under the opposite bicep
        pygame.draw.circle(s, col, (cx - sgn * X(0.33), Y(0.575)), X(0.082))
        pygame.draw.circle(s, core, (cx - sgn * X(0.305), Y(0.598)), X(0.036))
        # TL sheen highlight along the top of each forearm bar
        pygame.draw.polygon(s, SHEEN, [
            (cx + sgn * X(0.38), Y(0.47)),
            (cx + sgn * X(0.10), Y(0.52)),
            (cx + sgn * X(0.14), Y(0.545)),
            (cx + sgn * X(0.40), Y(0.49)),
        ])

    # FAR / under arm first (right-origin, darker), then the NEAR / over arm.
    _forearm(1, near=False)
    # Hard ink overlap SEAM: the silhouette edge of the near arm cast onto the
    # far arm at the crossing, so the eye reads two distinct stacked bars.
    pygame.draw.line(s, INK,
                     (cx + X(0.40), Y(0.475)),
                     (cx - X(0.22), Y(0.615)), max(3, _OW + S // 2))
    _forearm(-1, near=True)
    # a short second ink tick on the underside of the near arm where it tops the
    # far one, reinforcing the over/under step at small scale.
    pygame.draw.line(s, INK,
                     (cx - X(0.40), Y(0.47)),
                     (cx + X(0.22), Y(0.61)), max(2, _OW))
    # the near (front-left) fist sits PROUD — a small extra ember nub breaking
    # the silhouette so the crossed-arm geometry survives at 1x.
    pygame.draw.circle(s, EMBER, (cx + X(0.345), Y(0.585)), X(0.072))
    pygame.draw.circle(s, RUST, (cx + X(0.325), Y(0.605)), X(0.032))
    pygame.draw.circle(s, SHEEN, (cx + X(0.315), Y(0.56)), X(0.024))
    # bicep sheen pip (TL light)
    pygame.draw.circle(s, SHEEN, (cx - X(0.40), Y(0.43)), X(0.045))

    # ---- 4) HEAD — bumped to ~62% torso width, LIFTED clear, smug ----------
    # FIX #2: bigger + lifted so the smug face carries; was sunk between shoulders.
    hw = int(W * 0.26) * S        # head half-width (~62% of shoulder half 0.42)
    hh = int(H * 0.165) * S
    hcx = cx
    hcy = Y(0.195)                # lifted a few px clear of the shoulder line

    # Flame-HORNS: FIX #3 — crisp back-swept FLAME shapes (sharp pointed tip with
    # a concave back-edge flick + a saffron lit top-edge), NOT soft nubs/ears.
    for sgn in (-1, 1):
        root_x = hcx + sgn * int(hw * 0.50)
        root_y = hcy - int(hh * 0.20)
        tip_x = hcx + sgn * X(0.235)          # back-swept pointed flame tip
        tip_y = hcy - int(hh * 1.85)
        horn = [
            (root_x, root_y),                                  # front root
            (hcx + sgn * int(hw * 0.18), hcy - int(hh * 0.95)),# inner concave waist
            (tip_x, tip_y),                                    # SHARP tip
            (hcx + sgn * X(0.45), hcy - int(hh * 0.65)),       # outer concave flick
            (hcx + sgn * int(hw * 0.92), hcy + int(hh * 0.05)),# outer root
        ]
        _triad_lobe(s, horn, EMBER, RUST, SHEEN, core_inset=0.28, sink=0.08)
        # saffron flame-tip + lit top-edge so it reads as flame, not a knob
        pygame.draw.polygon(s, SAFFRON, [
            (tip_x, tip_y),
            (hcx + sgn * X(0.18), hcy - int(hh * 1.10)),
            (hcx + sgn * X(0.345), hcy - int(hh * 0.95)),
        ])
        # a thin saffron sheen running up the lit (back) edge to the tip
        pygame.draw.line(s, SAFFRON,
                         (hcx + sgn * X(0.45), hcy - int(hh * 0.65)),
                         (tip_x, tip_y), max(2, _OW))

    # softly-cornered head block
    head_rect = pygame.Rect(hcx - hw, hcy - hh, hw * 2, hh * 2)
    pygame.draw.rect(s, EMBER, head_rect, border_radius=int(W * 0.10) * S)
    # jaw dark-core + TL cheek sheen
    pygame.draw.rect(s, RUST, pygame.Rect(hcx - int(hw * 0.78), hcy + int(hh * 0.22),
                                          int(hw * 1.56), int(hh * 0.68)),
                     border_radius=int(W * 0.06) * S)
    pygame.draw.polygon(s, SHEEN, [
        (hcx - hw + 3 * S, hcy - hh + 3 * S),
        (hcx - int(hw * 0.15), hcy - hh + 4 * S),
        (hcx - int(hw * 0.45), hcy - int(hh * 0.1)),
        (hcx - hw + 3 * S, hcy - int(hh * 0.25)),
    ])

    # heavy smug brow (single hard ink stroke, cocked)
    pygame.draw.line(s, INK,
                     (hcx - int(hw * 0.72), hcy - int(hh * 0.16)),
                     (hcx + int(hw * 0.72), hcy - int(hh * 0.36)), max(2, _OW + S // 2))

    # COAL-eyes: saffron-core ember lobes, NO full ink ring — only a partial
    # LOWER ink keyline so they read as glowing coals, not spectacles/goggles.
    for sgn in (-1, 1):
        ex = hcx + sgn * int(hw * 0.40)
        ey = hcy + int(hh * 0.06)
        r = int(W * 0.065) * S
        pygame.draw.circle(s, COAL_GLOW, (ex, ey), r)
        pygame.draw.circle(s, SAFFRON, (ex - 1 * S, ey - 1 * S), int(r * 0.6))
        pygame.draw.arc(s, INK, pygame.Rect(ex - r, ey - r, r * 2, r * 2),
                        math.pi * 1.05, math.pi * 1.95, max(2, _OW))

    # single gold nose-ring on the SEPTUM — FIX #4: a small defined septum nub
    # the hoop hangs FROM, clear above the mouth line below.
    nrx = hcx
    sep_y = hcy + int(hh * 0.30)                     # septum sits above the mouth
    # tiny ember septum nub the ring pierces
    pygame.draw.circle(s, RUST, (nrx, sep_y), int(W * 0.022) * S)
    nr = int(W * 0.05) * S
    pygame.draw.circle(s, BRASS, (nrx, sep_y + nr), nr, max(2, _OW))
    pygame.draw.arc(s, BRASS_L, pygame.Rect(nrx - nr, sep_y, nr * 2, nr * 2),
                    math.pi * 0.6, math.pi * 1.4, max(1, _OW - 1))

    # cocky asymmetric smirk — pushed DOWN, clear below the septum ring
    pygame.draw.lines(s, INK, False, [
        (hcx - int(hw * 0.36), hcy + int(hh * 0.66)),
        (hcx + int(hw * 0.06), hcy + int(hh * 0.76)),
        (hcx + int(hw * 0.42), hcy + int(hh * 0.54)),
    ], max(2, _OW))

    # ---- hard keyline grown from the assembled alpha -----------------------
    _outline_from_alpha(s, INK, grow=1)
    # re-light the coal-eyes ON TOP of the keyline so they stay hot embers
    for sgn in (-1, 1):
        ex = hcx + sgn * int(hw * 0.40)
        ey = hcy + int(hh * 0.06)
        pygame.draw.circle(s, COAL_GLOW, (ex, ey), int(W * 0.052) * S)
        pygame.draw.circle(s, SAFFRON, (ex - 1 * S, ey - 1 * S), int(W * 0.028) * S)
    return pygame.transform.smoothscale(s, (W, H))


# ── LAMP-PILLAR (the prop -> pillar mirror — kept; AD called it ship-ready) ─
def build_lamp_shaft(W, H):
    """Fluted oil-lamp body = repeatable shaft. Vertical flutes (banding) with
    DEEPENED groove lines so the fluting reads at obstacle scale (not a plain
    gold tube). Symmetric column that tiles top<->bottom."""
    s = _raw(W, H)
    S = _SS
    cx = W * S // 2
    half = int(W * 0.34) * S
    pygame.draw.rect(s, BRASS, pygame.Rect(cx - half, 0, half * 2, H * S))
    n = 5
    span = (half * 2 - 6 * S)
    for i in range(n):
        fx = int(cx - half + 3 * S + span * (i + 0.5) / n)
        pygame.draw.line(s, BRASS_D, (fx, 0), (fx, H * S), max(3, int(W * 0.045) * S))
    for i in range(n + 1):
        rx = int(cx - half + 3 * S + span * i / n)
        pygame.draw.line(s, BRASS_L, (rx, 0), (rx, H * S), max(2, int(W * 0.022) * S))
    pygame.draw.line(s, BRASS_L, (cx - half + 2 * S, 0), (cx - half + 2 * S, H * S),
                     max(2, int(W * 0.04) * S))
    _outline_from_alpha(s, INK, grow=1)
    return pygame.transform.smoothscale(s, (W, H))


def build_lamp_cap(W, H, flip=False):
    """Wick-spout puffing a fire-curl = gap-edge cap. Lamp shoulder + curved
    spout + a triad-lit ember curl licking INTO the gap. Symmetric on-axis."""
    s = _raw(W, H)
    S = _SS
    cx = W * S // 2
    half = int(W * 0.34) * S
    pygame.draw.rect(s, BRASS, pygame.Rect(cx - half, int(H * 0.34) * S, half * 2, int(H * 0.66) * S))
    pygame.draw.ellipse(s, BRASS, pygame.Rect(cx - int(half * 1.15), int(H * 0.28) * S,
                                              int(half * 2.3), int(H * 0.30) * S))
    pygame.draw.ellipse(s, BRASS_D, pygame.Rect(cx - int(half * 0.7), int(H * 0.40) * S,
                                                int(half * 1.4), int(H * 0.20) * S))
    pygame.draw.ellipse(s, BRASS_L, pygame.Rect(cx - int(half * 1.0), int(H * 0.29) * S,
                                                int(half * 0.8), int(H * 0.12) * S))
    spout = [
        (cx, int(H * 0.30) * S), (cx + int(half * 1.1), int(H * 0.24) * S),
        (cx + int(half * 1.4), int(H * 0.14) * S), (cx + int(half * 1.15), int(H * 0.18) * S),
        (cx + int(half * 0.6), int(H * 0.30) * S),
    ]
    pygame.draw.polygon(s, BRASS, spout)
    pygame.draw.polygon(s, BRASS_L, [spout[0], spout[1], spout[4]])
    flame = [
        (cx + int(half * 1.25), int(H * 0.16) * S),
        (cx + int(half * 1.55), int(H * 0.02) * S),
        (cx + int(half * 1.20), int(H * 0.05) * S),
        (cx + int(half * 1.05), int(H * 0.14) * S),
    ]
    _triad_lobe(s, flame, EMBER, RUST, SHEEN, core_inset=0.25, sink=0.15)
    _fire_heart(s, flame)
    smoke = [
        (cx + int(half * 1.40), int(H * 0.06) * S),
        (cx + int(half * 1.50), int(H * -0.06) * S),
        (cx + int(half * 1.30), int(H * 0.0) * S),
    ]
    pygame.draw.polygon(s, VIOLET, smoke)
    pygame.draw.polygon(s, VIOLET_L, [smoke[0], smoke[1], (cx + int(half * 1.42), int(H * 0.0) * S)])
    out = pygame.transform.smoothscale(s, (W, H))
    if flip:
        out = pygame.transform.flip(out, False, True)
    return out


# ── Sky helpers (day/night biome legibility) ────────────────────────────────
def day_sky(w, h):
    s = pygame.Surface((w, h))
    top, bot = (118, 196, 246), (206, 240, 252)
    for y in range(h):
        pygame.draw.line(s, _mix(top, bot, y / max(1, h - 1)), (0, y), (w, y))
    return s


def night_sky(w, h):
    import random
    s = pygame.Surface((w, h))
    top, bot = (18, 22, 46), (52, 40, 78)
    for y in range(h):
        pygame.draw.line(s, _mix(top, bot, y / max(1, h - 1)), (0, y), (w, y))
    rnd = random.Random(9)
    for _ in range(60):
        x, y = rnd.randint(0, w - 1), rnd.randint(0, h - 1)
        b = rnd.randint(120, 230)
        s.set_at((x, y), (b, b, min(255, b + 20)))
    return s


def to_grayscale(surf):
    g = surf.copy()
    arr = pygame.surfarray.pixels3d(g)
    lum = (arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114).astype('uint8')
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    return g


def _font(sz, bold=True):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


def main():
    SHEET_W, SHEET_H = 1180, 760
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((30, 32, 40))

    f_title = _font(24)
    f_sub = _font(15, bold=False)
    f_panel = _font(18)
    f_small = _font(14, bold=False)

    sheet.blit(f_title.render("IFRA  —  Batch-2 Devilish  —  smokeless-fire genie devil  —  round 3 (final)",
                              True, (240, 240, 248)), (22, 14))
    sheet.blit(f_sub.render("crossed-arm fold now reads as TWO arms (ink overlap + value step + proud fist); "
                            "head bumped up & lifted clear; sharp flame-horns; septum nose-ring",
                            True, (190, 190, 200)), (22, 40))

    PANEL_Y = 66
    PANEL_H = 540
    p1 = pygame.Rect(14, PANEL_Y, 384, PANEL_H)
    p2 = pygame.Rect(406, PANEL_Y, 360, PANEL_H)
    p3 = pygame.Rect(774, PANEL_Y, 392, PANEL_H)
    for p in (p1, p2, p3):
        pygame.draw.rect(sheet, (44, 46, 56), p, border_radius=8)
        pygame.draw.rect(sheet, (70, 74, 84), p, 2, border_radius=8)

    # ---- (a) BOSS showcase scale -------------------------------------------
    sheet.blit(f_panel.render("(a) BOSS  showcase scale", True, (230, 220, 160)), (p1.x + 12, p1.y + 8))
    big = build_ifra(180, 240)
    big = pygame.transform.scale(big, (270, 360))
    sheet.blit(big, (p1.centerx - big.get_width() // 2, p1.y + 70))
    sheet.blit(f_small.render("two crossed arms (over/under ink seam + value step),", True, (200, 200, 210)),
               (p1.x + 12, p1.bottom - 56))
    sheet.blit(f_small.render("bigger smug head, sharp flame-horns, septum ring.", True, (200, 200, 210)),
               (p1.x + 12, p1.bottom - 38))

    # ---- (b) PROP -> PILLAR @ true obstacle scale --------------------------
    sheet.blit(f_panel.render("(b) PROP -> PILLAR  @ obstacle scale", True, (230, 220, 160)), (p2.x + 12, p2.y + 8))
    sky_b = night_sky(p2.w - 24, p2.h - 40)
    sheet.blit(sky_b, (p2.x + 12, p2.y + 34))
    COL_W = 82
    cap = build_lamp_cap(COL_W, 90, flip=False)
    shaft = build_lamp_shaft(COL_W, 150)
    cap_top = build_lamp_cap(COL_W, 90, flip=True)
    col_x = p2.x + 36
    base_y = p2.bottom - 18
    sheet.blit(shaft, (col_x, base_y - 150))
    sheet.blit(cap, (col_x, base_y - 150 - 80))
    top_y = p2.y + 44
    sheet.blit(shaft, (col_x, top_y))
    sheet.blit(cap_top, (col_x, top_y + 150 - 10))
    sheet.blit(f_small.render("1x native (~82px):", True, (210, 215, 225)), (col_x - 4, base_y + 2))
    sheet.blit(f_small.render("fluted lamp = shaft", True, (210, 215, 225)), (col_x - 4, base_y + 18))
    zoom = pygame.transform.scale(cap, (COL_W * 2, 180))
    zx = p2.right - COL_W * 2 - 22
    zy = p2.centery - 40
    pygame.draw.rect(sheet, (28, 30, 38), (zx - 6, zy - 6, COL_W * 2 + 12, 192), border_radius=8)
    sheet.blit(zoom, (zx, zy))
    sheet.blit(f_small.render("2x cap zoom:", True, (210, 215, 225)), (zx - 4, zy - 24))
    sheet.blit(f_small.render("fire-curl + violet", True, (210, 215, 225)), (zx - 4, zy + 186))
    sheet.blit(f_small.render("wisp puff INTO gap", True, (210, 215, 225)), (zx - 4, zy + 202))

    # ---- (c) 1x in-game legibility + grayscale silhouette ------------------
    sheet.blit(f_panel.render("(c) 1x in-game  —  day / night + silhouette", True, (230, 220, 160)),
               (p3.x + 12, p3.y + 8))
    sprite_day = build_ifra(64, 84)
    sprite_night = build_ifra(64, 84)
    half_w = (p3.w - 36) // 2
    dsky = day_sky(half_w, 150)
    sheet.blit(dsky, (p3.x + 12, p3.y + 36))
    sheet.blit(f_small.render("DAY", True, (30, 50, 80)), (p3.x + 18, p3.y + 40))
    sheet.blit(pygame.transform.scale(sprite_day, (96, 126)),
               (p3.x + 12 + half_w // 2 - 48, p3.y + 44))
    nsky = night_sky(half_w, 150)
    sheet.blit(nsky, (p3.x + 24 + half_w, p3.y + 36))
    sheet.blit(f_small.render("NIGHT", True, (200, 210, 230)), (p3.x + 30 + half_w, p3.y + 40))
    sheet.blit(pygame.transform.scale(sprite_night, (96, 126)),
               (p3.x + 24 + half_w + half_w // 2 - 48, p3.y + 44))

    sheet.blit(f_small.render("true 32px (creature / pillar):", True, (220, 220, 230)),
               (p3.x + 12, p3.y + 200))
    s32 = build_ifra(32, 42)
    cap32 = build_lamp_cap(32, 36)
    shaft32 = build_lamp_shaft(32, 50)
    for i, mk in enumerate((day_sky, night_sky)):
        chip = mk(46, 56)
        cxp = p3.x + 16 + i * 58
        sheet.blit(chip, (cxp, p3.y + 222))
        sheet.blit(s32, (cxp + 7, p3.y + 226))
    px = p3.x + 16 + 2 * 58 + 14
    nchip = night_sky(48, 110)
    sheet.blit(nchip, (px, p3.y + 222))
    sheet.blit(shaft32, (px + 8, p3.y + 270))
    sheet.blit(cap32, (px + 8, p3.y + 236))
    sheet.blit(f_small.render("pillar", True, (210, 215, 225)), (px, p3.y + 334))

    sheet.blit(f_small.render("grayscale: two-arm fold + bigger head + horns carry",
                              True, (210, 210, 218)), (p3.x + 12, p3.y + 352))
    gray = to_grayscale(pygame.transform.scale(build_ifra(112, 148), (112, 148)))
    gplate = pygame.Surface((p3.w - 24, 150))
    gplate.fill((150, 150, 156))
    sheet.blit(gplate, (p3.x + 12, p3.y + 374))
    sheet.blit(gray, (p3.centerx - 56, p3.y + 374))
    g32 = to_grayscale(build_ifra(32, 42))
    sheet.blit(pygame.transform.scale(g32, (60, 80)), (p3.right - 88, p3.y + 410))
    sheet.blit(f_small.render("32px", True, (60, 60, 66)), (p3.right - 84, p3.y + 492))

    # ---- footer notes -------------------------------------------------------
    fy = PANEL_Y + PANEL_H + 14
    sheet.blit(f_sub.render("round 3 (final) fixes: (1) crossed-arm fold breaks into TWO arms — hard ink "
                            "overlap seam + value step (under-arm darker) + a proud near fist nub;",
                            True, (200, 200, 210)), (22, fy))
    sheet.blit(f_sub.render("(2) head bumped to ~62% torso width and lifted clear of the shoulders so the smug "
                            "face carries; (3) flame-horns sharpened to crisp back-swept saffron-tipped flames;",
                            True, (200, 200, 210)), (22, fy + 22))
    sheet.blit(f_sub.render("(4) nose-ring re-seated UP on a defined septum nub, clear above the mouth. KEPT: "
                            "torso construction, short smoke-curl (Leyak gap), pinned palette, lamp-pillar mirror.",
                            True, (200, 200, 210)), (22, fy + 44))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
