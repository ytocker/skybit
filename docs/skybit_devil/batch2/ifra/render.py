"""IFRA — round 2 design sheet (Batch-2 Devilish, smokeless-fire genie devil).

Renders the ONE locked concept: an ifrit cuted to a cocky ember-imp whose legs
dissolve into a billowing violet smoke-flame curl. Round 2 resolves the AD
blocker — the round-1 render read as a bodiless floating HEAD (drifting into
Leyak's lane). It now has the pinned construction: a SHRUNKEN smug head over a
BROAD crossed-beefy-arms ember TORSO (shoulders wider than the head, two fat
forearms folded X across the chest), nipping in at the waist into the smoke
blob; two back-swept FLAME-horns (not elf-ears); ember COAL-eyes (no spectacle
ink rings); a single clean brass nose-ring on the septum. Lamp-pillar fluting
deepened for the obstacle-scale read.

Sheet grammar (brimstone sibling): (a) BOSS showcase scale, (b) PROP -> PILLAR
at true obstacle scale + a 2x gap zoom, (c) 1x in-game day/night legibility +
a grayscale silhouette check + a true-32px read row. House style: chibi, FLAT
triad fills (dark-core -> flat-fill -> top-left rim-sheen), hard ink keyline
grown 1px from the alpha mask, supersample -> smoothscale.

Run:  SDL_VIDEODRIVER=dummy python docs/skybit_devil/batch2/ifra/render.py
Out:  docs/skybit_devil/batch2/ifra/round_2.png

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
      • SMUG HEAD (~58% of torso width) with two back-swept flame-horns,
        ember coal-eyes, a clean septum nose-ring.
      • BROAD crossed-beefy-arms TORSO: shoulders wider than the head, two fat
        forearms folded X across the chest (the classic genie fold) — the
        horizontal arm-band is Ifra's 32px distinguisher vs every floating sibling.
      • WAIST nips in and dissolves into a compact, billowing VIOLET smoke-curl
        base (the legless blob) — kept SHORT/rounded so it never reads as
        Leyak's long descending trail.
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
    plume_top = Y(0.64)
    for sgn in (-1, 1):
        curl = [
            (cx + sgn * X(0.05), plume_top),
            (cx + sgn * X(0.28), Y(0.78)),
            (cx + sgn * X(0.30), Y(0.90)),
            (cx + sgn * X(0.12), Y(0.985)),
            (cx, Y(0.93)),
        ]
        _triad_lobe(s, curl, VIOLET, VIOLET_D, VIOLET_L, core_inset=0.34, sink=0.28)
    # a small inner saffron ember tongue licking up through the smoke (focal)
    tongue = [
        (cx, Y(0.66)),
        (cx + X(0.10), Y(0.80)),
        (cx, Y(0.90)),
        (cx - X(0.10), Y(0.80)),
    ]
    _triad_lobe(s, tongue, EMBER, RUST, SHEEN, core_inset=0.30, sink=0.30)
    _fire_heart(s, tongue)

    # ---- 2) Crossed-arm TORSO ----------------------------------------------
    # Heavy upper body: wide shoulders, hard nip at the waist (the genie "V").
    sh_y = Y(0.40)            # shoulder line — raised so it meets the chin
    sh_w = X(0.42)           # half shoulder width (wider than the head)
    waist_y = Y(0.64)
    waist_w = X(0.15)
    torso = [
        (cx - sh_w, sh_y),
        (cx - X(0.46), Y(0.47)),       # deltoid bulge
        (cx - X(0.30), Y(0.58)),
        (cx - waist_w, waist_y),
        (cx + waist_w, waist_y),
        (cx + X(0.30), Y(0.58)),
        (cx + X(0.46), Y(0.47)),
        (cx + sh_w, sh_y),
    ]
    pygame.draw.polygon(s, EMBER, torso)
    # dark-core pooled low (belly), TL chest sheen
    pygame.draw.polygon(s, RUST, [
        (cx - X(0.26), Y(0.52)), (cx + X(0.26), Y(0.52)),
        (cx + waist_w, waist_y), (cx - waist_w, waist_y),
    ])
    pygame.draw.polygon(s, SHEEN, [
        (cx - X(0.40), sh_y + 2 * S),
        (cx - X(0.16), Y(0.44)),
        (cx - X(0.22), Y(0.54)),
        (cx - X(0.42), Y(0.49)),
    ])

    # ---- 3) Crossed beefy arms (classic genie fold) ------------------------
    # Two fat forearms lying X across the chest; round biceps cap the shoulders.
    # Drawn so the FAR arm sits behind, the NEAR arm overlaps it — the X-fold
    # plus its under-shadow makes the horizontal arm band read at 32px.
    bicep_y = Y(0.44)
    # biceps (shoulder caps) — far first so near overlaps cleanly
    for sgn in (-1, 1):
        col = EMBER_D if sgn < 0 else EMBER
        pygame.draw.circle(s, col, (cx + sgn * X(0.36), bicep_y), X(0.14))
    # the two forearms: each runs from its shoulder diagonally DOWN to the
    # OPPOSITE lower ribs, fists tucked under the far elbow. Drawn FAR-then-NEAR
    # with a hard ink seam between them so the X-crossing reads as two arms, not
    # one bar. The near (front-left) arm overlaps the far at the crossing point.
    order = (-1, 1)   # far (right-origin) first, near (left-origin) last
    for sgn in order:
        near = sgn < 0   # the left-origin arm reads as the front one
        col = EMBER if near else EMBER_D
        # forearm as a thick tapering bar shoulder -> opposite hip
        fa = [
            (cx + sgn * X(0.42), Y(0.435)),      # outer shoulder
            (cx + sgn * X(0.30), Y(0.475)),
            (cx - sgn * X(0.24), Y(0.595)),      # crossing to far ribs
            (cx - sgn * X(0.36), Y(0.575)),
            (cx + sgn * X(0.18), Y(0.455)),
        ]
        pygame.draw.polygon(s, col, fa)
        # forearm dark-core underside (the shadow band the AD asked to confirm)
        pygame.draw.polygon(s, RUST, [
            (cx + sgn * X(0.30), Y(0.50)),
            (cx - sgn * X(0.24), Y(0.60)),
            (cx - sgn * X(0.36), Y(0.575)),
            (cx - sgn * X(0.12), Y(0.525)),
        ])
        # chunky fist tucked under the opposite bicep
        pygame.draw.circle(s, col, (cx - sgn * X(0.33), Y(0.555)), X(0.078))
        pygame.draw.circle(s, RUST, (cx - sgn * X(0.305), Y(0.578)), X(0.034))
        # TL sheen highlight along the top of each forearm bar
        pygame.draw.polygon(s, SHEEN, [
            (cx + sgn * X(0.38), Y(0.45)),
            (cx + sgn * X(0.10), Y(0.50)),
            (cx + sgn * X(0.14), Y(0.525)),
            (cx + sgn * X(0.40), Y(0.47)),
        ])
        if near:
            # hard ink seam where the near arm crosses OVER the far one
            pygame.draw.line(s, INK,
                             (cx + X(0.40), Y(0.455)),
                             (cx - X(0.20), Y(0.59)), max(2, _OW))
    # bicep sheen pip (TL light)
    pygame.draw.circle(s, SHEEN, (cx - X(0.40), Y(0.41)), X(0.045))

    # ---- 4) HEAD — shrunk to ~58% torso width, softly-cornered, smug -------
    hw = int(W * 0.24) * S        # head half-width (< shoulder half-width 0.42)
    hh = int(H * 0.155) * S
    hcx = cx
    hcy = Y(0.21)

    # Flame-HORNS: two flat, back-swept saffron-tipped lobes behind the head
    # (drawn first so the head overlaps their roots). NOT elf-ears.
    for sgn in (-1, 1):
        horn = [
            (hcx + sgn * int(hw * 0.55), hcy - int(hh * 0.30)),   # root at the temple
            (hcx + sgn * X(0.30), hcy - int(hh * 1.55)),          # swept up/back
            (hcx + sgn * X(0.40), hcy - int(hh * 0.55)),          # tip flicks back
            (hcx + sgn * int(hw * 0.85), hcy + int(hh * 0.10)),
        ]
        _triad_lobe(s, horn, EMBER, RUST, SHEEN, core_inset=0.30, sink=0.10)
        # saffron flame-tip (the lit point of the horn)
        pygame.draw.polygon(s, SAFFRON, [horn[1],
                                         (hcx + sgn * X(0.235), hcy - int(hh * 1.35)),
                                         (hcx + sgn * X(0.34), hcy - int(hh * 0.85))])

    # softly-cornered head block
    head_rect = pygame.Rect(hcx - hw, hcy - hh, hw * 2, hh * 2)
    pygame.draw.rect(s, EMBER, head_rect, border_radius=int(W * 0.10) * S)
    # jaw dark-core + TL cheek sheen
    pygame.draw.rect(s, RUST, pygame.Rect(hcx - int(hw * 0.78), hcy + int(hh * 0.20),
                                          int(hw * 1.56), int(hh * 0.70)),
                     border_radius=int(W * 0.06) * S)
    pygame.draw.polygon(s, SHEEN, [
        (hcx - hw + 3 * S, hcy - hh + 3 * S),
        (hcx - int(hw * 0.15), hcy - hh + 4 * S),
        (hcx - int(hw * 0.45), hcy - int(hh * 0.1)),
        (hcx - hw + 3 * S, hcy - int(hh * 0.25)),
    ])

    # heavy smug brow (single hard ink stroke, cocked)
    pygame.draw.line(s, INK,
                     (hcx - int(hw * 0.72), hcy - int(hh * 0.14)),
                     (hcx + int(hw * 0.72), hcy - int(hh * 0.34)), max(2, _OW + S // 2))

    # COAL-eyes: saffron-core ember lobes, NO full ink ring — only a partial
    # LOWER ink keyline so they read as glowing coals, not spectacles/goggles.
    for sgn in (-1, 1):
        ex = hcx + sgn * int(hw * 0.40)
        ey = hcy + int(hh * 0.08)
        r = int(W * 0.062) * S
        # outer ember halo (in the fire family), then saffron-hot core
        pygame.draw.circle(s, COAL_GLOW, (ex, ey), r)
        pygame.draw.circle(s, SAFFRON, (ex - 1 * S, ey - 1 * S), int(r * 0.6))
        # partial lower keyline only (an arc under the coal), not a ring
        pygame.draw.arc(s, INK, pygame.Rect(ex - r, ey - r, r * 2, r * 2),
                        math.pi * 1.05, math.pi * 1.95, max(2, _OW))

    # cocky asymmetric smirk
    pygame.draw.lines(s, INK, False, [
        (hcx - int(hw * 0.36), hcy + int(hh * 0.52)),
        (hcx + int(hw * 0.06), hcy + int(hh * 0.62)),
        (hcx + int(hw * 0.42), hcy + int(hh * 0.40)),
    ], max(2, _OW))

    # single gold nose-ring on the SEPTUM (clear of the mouth line)
    nrx = hcx
    nry = hcy + int(hh * 0.22)
    nr = int(W * 0.05) * S
    pygame.draw.circle(s, BRASS, (nrx, nry + nr), nr, max(2, _OW))
    pygame.draw.arc(s, BRASS_L, pygame.Rect(nrx - nr, nry, nr * 2, nr * 2),
                    math.pi * 0.6, math.pi * 1.4, max(1, _OW - 1))

    # ---- hard keyline grown from the assembled alpha -----------------------
    _outline_from_alpha(s, INK, grow=1)
    # re-light the coal-eyes ON TOP of the keyline so they stay hot embers
    for sgn in (-1, 1):
        ex = hcx + sgn * int(hw * 0.40)
        ey = hcy + int(hh * 0.08)
        pygame.draw.circle(s, COAL_GLOW, (ex, ey), int(W * 0.05) * S)
        pygame.draw.circle(s, SAFFRON, (ex - 1 * S, ey - 1 * S), int(W * 0.026) * S)
    return pygame.transform.smoothscale(s, (W, H))


# ── LAMP-PILLAR (the prop -> pillar mirror) ─────────────────────────────────
def build_lamp_shaft(W, H):
    """Fluted oil-lamp body = repeatable shaft. Vertical flutes (banding) with
    DEEPENED groove lines so the fluting reads at obstacle scale (not a plain
    gold tube). Symmetric column that tiles top<->bottom."""
    s = _raw(W, H)
    S = _SS
    cx = W * S // 2
    half = int(W * 0.34) * S
    pygame.draw.rect(s, BRASS, pygame.Rect(cx - half, 0, half * 2, H * S))
    # flute grooves: deepened deep-rust/brass-dark valleys between lit ridges so
    # the banding pops ~10-15% darker than round 1.
    n = 5
    span = (half * 2 - 6 * S)
    for i in range(n):
        fx = int(cx - half + 3 * S + span * (i + 0.5) / n)
        # darker valley groove
        pygame.draw.line(s, BRASS_D, (fx, 0), (fx, H * S), max(3, int(W * 0.045) * S))
    for i in range(n + 1):
        rx = int(cx - half + 3 * S + span * i / n)
        # lit ridge highlight between grooves
        pygame.draw.line(s, BRASS_L, (rx, 0), (rx, H * S), max(2, int(W * 0.022) * S))
    # bright lit left edge
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
    # lamp shoulder dome
    pygame.draw.rect(s, BRASS, pygame.Rect(cx - half, int(H * 0.34) * S, half * 2, int(H * 0.66) * S))
    pygame.draw.ellipse(s, BRASS, pygame.Rect(cx - int(half * 1.15), int(H * 0.28) * S,
                                              int(half * 2.3), int(H * 0.30) * S))
    pygame.draw.ellipse(s, BRASS_D, pygame.Rect(cx - int(half * 0.7), int(H * 0.40) * S,
                                                int(half * 1.4), int(H * 0.20) * S))
    pygame.draw.ellipse(s, BRASS_L, pygame.Rect(cx - int(half * 1.0), int(H * 0.29) * S,
                                                int(half * 0.8), int(H * 0.12) * S))
    # curved spout (classic oil-lamp, off one side)
    spout = [
        (cx, int(H * 0.30) * S), (cx + int(half * 1.1), int(H * 0.24) * S),
        (cx + int(half * 1.4), int(H * 0.14) * S), (cx + int(half * 1.15), int(H * 0.18) * S),
        (cx + int(half * 0.6), int(H * 0.30) * S),
    ]
    pygame.draw.polygon(s, BRASS, spout)
    pygame.draw.polygon(s, BRASS_L, [spout[0], spout[1], spout[4]])
    # fire-curl puffing from the spout (live-fire signature, INTO the gap)
    flame = [
        (cx + int(half * 1.25), int(H * 0.16) * S),
        (cx + int(half * 1.55), int(H * 0.02) * S),
        (cx + int(half * 1.20), int(H * 0.05) * S),
        (cx + int(half * 1.05), int(H * 0.14) * S),
    ]
    _triad_lobe(s, flame, EMBER, RUST, SHEEN, core_inset=0.25, sink=0.15)
    _fire_heart(s, flame)
    # a violet smoke wisp curling off the flame (cool counterweight, even here)
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

    sheet.blit(f_title.render("IFRA  —  Batch-2 Devilish  —  smokeless-fire genie devil  —  round 2",
                              True, (240, 240, 248)), (22, 14))
    sheet.blit(f_sub.render("smug head + BROAD crossed-beefy-arms ember TORSO over a compact violet "
                            "smoke-curl base; back-swept flame-horns; ember coal-eyes; septum nose-ring",
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
    sheet.blit(f_small.render("crossed-arm fire TORSO (shoulders > head), waist", True, (200, 200, 210)),
               (p1.x + 12, p1.bottom - 56))
    sheet.blit(f_small.render("tapers into a compact violet smoke-curl; flame-horns.", True, (200, 200, 210)),
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
    # 2x zoom of the gap-cap
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

    # true 32px row
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

    # grayscale silhouette check
    sheet.blit(f_small.render("grayscale: crossed-arm band + smoke blob carry the read",
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
    sheet.blit(f_sub.render("round 2 fixes: built the crossed-beefy-arms TORSO (blocker) so Ifra is a "
                            "genie, not a floating head; shrank the head (~58% torso w);",
                            True, (200, 200, 210)), (22, fy))
    sheet.blit(f_sub.render("swapped elf-ears -> back-swept flame-horns; coal-eyes lost the spectacle "
                            "rings (partial lower keyline only); nose-ring re-seated on the septum; deepened lamp flutes.",
                            True, (200, 200, 210)), (22, fy + 22))
    sheet.blit(f_sub.render("KEPT: pinned palette exact (coral+violet+saffron live-fire); FLAT triad lobes; "
                            "compact smoke-curl stays SHORT so it never drifts into Leyak's long trail.",
                            True, (200, 200, 210)), (22, fy + 44))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
