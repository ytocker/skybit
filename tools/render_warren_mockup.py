"""Look-dev mockup for the "Pagoda Warren" concept.

The corridor is STRUCTURAL: neighbouring pagoda-pillars are packed so tight
that their curved eaves and bodies abut / overlap, fusing the top pagodas
into ONE continuous serrated wall and the bottom pagodas into another. The
only negative space left is the single winding central slot — so the
warren read survives with every highlight turned OFF (see the bottom
"structure check" strip, which renders the route from silhouette alone).

This script renders a candidate sheet — 5 corridor archetypes (rows) x 3
times of day (columns) — and overlays the REAL parrot sprite plus a
parabolic dotted flight path so a reviewer can SEE the corridor is
threadable by a one-button flapper.

The single goal is to prove PASSABILITY: every corridor is generated from a
small set of gap centres, and the asserts below reject any layout that the
real bird physics couldn't fly. No game/ files are touched and no game
state is mutated — we only call the existing draw entry points and pass
locally-tinted copies of the biome palette.

    PYTHONPATH=. python tools/render_warren_mockup.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import (
    W, H, GROUND_Y, PIPE_W, GAP_START, BIRD_R, PIPE_HITBOX_SHRINK,
    FLAP_V, GRAVITY, SCROLL_BASE,
)
from game.biome import palette_for_phase, lerp_color
from game.pillar_pagodas import draw_pillar_pair
from game.parrot import get_parrot


# ── physics-derived passability budget ───────────────────────────────────────
# One flap rises FLAP_V**2 / (2*GRAVITY) px before gravity wins. That is the
# hard ceiling on how much altitude the bird can buy per tap, and it anchors
# every "is this slope flyable" check below.
FLAP_RISE = (FLAP_V * FLAP_V) / (2.0 * GRAVITY)          # ~84 px
EFFECTIVE_R = BIRD_R - PIPE_HITBOX_SHRINK                # forgiven hitbox = 10 px
PARROT_H = 2 * BIRD_R                                    # ~28 px scale ruler

GAP_H_MIN, GAP_H_MAX = 150, 185        # per-pagoda gap height window
DRIFT_MAX = 56                         # per-pagoda gap-centre vertical step
# Spacing is now driven DOWN toward / below the eave span. A pagoda body is
# ~0.94*PIPE_W (~54 px) and each cached tier-eave overhangs ~10-15 px, so the
# painted silhouette is ~78-84 px wide. Centre-to-centre below that forces
# neighbours' eaves to abut / overlap into one fused wall, pooling all sky
# into the single central slot — the corridor becomes carved negative space
# instead of a faked paint ribbon.
SPACING_MIN, SPACING_MAX = 62, 84

# The flight channel must stay a generous, near-constant tube as it winds —
# never pinching below ~2.5 parrot-heights even where neighbours overlap most.
CHANNEL_MIN = int(2.5 * PARROT_H)      # ~70 px clear threadable width

# Keep the threaded corridor off the sky ceiling and off the ground band so
# the parrot always has real estate above and below the path.
CEIL_PAD = 72
FLOOR_PAD = 72
GAP_CY_MIN = CEIL_PAD + GAP_H_MAX // 2
GAP_CY_MAX = GROUND_Y - FLOOR_PAD - GAP_H_MAX // 2


# ── corridor archetypes ──────────────────────────────────────────────────────
# Each returns a list of pagodas: (x_centre, gap_cy, gap_h, seed). x_centre is
# the pillar centre; spacing is tight enough that the eaves of neighbouring
# towers touch, so the union of [gap_cy-gap_h/2, gap_cy+gap_h/2] is the ONLY
# open space — the winding passage. Seeds pick the pagoda variant (seed % 11)
# so each row owns a coherent architectural family.

def _gentle_sine_tube(x0):
    """LEAD design — one smooth rounded tube, the welcoming intro warren.

    Instantly-readable designed route (chevron's clarity) but every apex is
    a soft cosine crest, so the path is a sequence of fair parabolic hops a
    one-button flapper can actually fly. Wide gaps, gentle sweep, fused
    masonry above and below.
    """
    out, x = [], x0
    base = 308                                     # apex nudged up ~4px so the
    n = 9                                          # sunset pinch has symmetric
    for i in range(n):                             # clear air above and below
        # Cosine crest gives rounded tops/bottoms (no kinked apex) and the
        # per-step delta stays well under one flap's climb.
        cy = base + math.cos(i * 0.62) * 52        # 52 px sweep < DRIFT_MAX
        out.append((x, cy, 184, 0))                # stupa_canopy family, big gaps
        x += 70
    return out


def _terraced_staircase(x0):
    """Re-cut stepped landings: gap descends to a mid plateau then climbs,
    in fair treads inside one flap. Tight spacing fuses every tread's towers
    into a continuous stepped wall, so the staircase reads from silhouette."""
    out, x = [], x0
    # Each step ≤ DRIFT_MAX and ≤ FLAP_RISE so a single tap buys the climb.
    treads = [248, 248, 300, 300, 352, 352, 300, 300, 248]
    for i, cy in enumerate(treads):
        out.append((x, cy, 174, 3))                # horyuji family
        x += 74
    return out


def _chevron_zigzag(x0):
    """Alternating diagonal designed route — the clearest 'go here' read.
    Apexes are softened by a 1-pagoda landing so the corridor rounds over
    each peak instead of kinking. Tight spacing welds the legs into a single
    saw-tooth wall."""
    out, x = [], x0
    # Amplitude pulled in from 64px to 40px swing: the zig now reads as a
    # gentle characterful wave (still the "challenging" archetype) instead of
    # a saw-tooth that mimics brick texture. Gap height bumped to 174 so the
    # channel stays the same generous tube even with the calmer wander.
    lo, mid, hi = 290, 310, 330               # 40 px swing < drift ceiling
    pattern = [lo, mid, hi, hi, mid, lo, lo, mid, hi]
    for i, cy in enumerate(pattern):
        out.append((x, cy, 174, 5))                # toji family
        x += 76
    return out


def _woven_offset(x0):
    """Re-cut 'braided' as a tightly WOVEN tube — alternating high/low towers
    overlap heavily so their eaves interlace into one wall, while the gap
    centre wanders gently on a single sine so the flight channel stays a
    constant generous width. Parrot gets clear air above and below."""
    out, x = [], x0
    base = 318
    n = 9
    for i in range(n):
        cy = base + math.sin(i * 0.78) * 44        # smooth 44 px wander
        out.append((x, cy, 176, 8))                # baoen family
        x += 66                                    # tightest weave spacing
    return out


def _straight_undulating(x0):
    """Tight near-uniform corridor with a slight wander — the classic
    'thread the needle' tunnel, now built from fully fused masonry."""
    out, x = [], x0
    base = 322
    n = 10
    for i in range(n):
        cy = base + math.sin(i * 1.05) * 26        # shallow 26 px wander
        out.append((x, cy, 168, 10))               # palsangjeon family
        x += 64                                    # snug uniform spacing
    return out


# `dense=True` rows over-read in round 2 as a "brick wall with a slot": their
# tighter spacing packs more high-frequency masonry on screen. We flag them so
# the renderer flattens their brick-coursing contrast (one calm recessive wall
# value) and strengthens the lighter tube-interior band — WITHOUT touching the
# channel width / passability asserts.
DESIGNS = [
    ("Gentle Sine Tube", _gentle_sine_tube, False),
    ("Terraced Staircase", _terraced_staircase, False),
    ("Chevron Zig-Zag", _chevron_zigzag, True),
    ("Woven Offset", _woven_offset, True),
    ("Straight Undulating Tunnel", _straight_undulating, True),
]

TIMES = [("DAY", 0.05), ("SUNSET", 0.36), ("NIGHT", 0.64)]


# ── passability proof ────────────────────────────────────────────────────────

def assert_passable(name, pagodas):
    """Reject any corridor the real bird physics couldn't fly. Asserts mirror
    the brief's budget exactly so the rendered sheet is provably fair. The
    tighter (fused) spacing means fewer taps between pillars, so the per-step
    climb stays inside one flap and the channel never pinches below the
    minimum threadable width."""
    prev = None
    for i, (x, cy, gap_h, _seed) in enumerate(pagodas):
        assert GAP_H_MIN <= gap_h <= GAP_H_MAX, \
            f"{name}: gap_h {gap_h} outside [{GAP_H_MIN},{GAP_H_MAX}]"
        assert GAP_CY_MIN <= cy <= GAP_CY_MAX, \
            f"{name}: gap centre {cy} too close to ceiling/ground"
        if prev is not None:
            px, pcy, pgap_h, _ = prev
            spacing = x - px
            assert SPACING_MIN <= spacing <= SPACING_MAX, \
                f"{name}: spacing {spacing} outside fused-warren window"
            drift = abs(cy - pcy)
            assert drift <= DRIFT_MAX, \
                f"{name}: drift {drift} > {DRIFT_MAX}"
            # Consecutive gaps must share enough vertical room that the union
            # is one continuous tube the bird never has to leave AND that the
            # narrowest point stays a generous threadable channel.
            top = max(cy - gap_h / 2, pcy - pgap_h / 2)
            bot = min(cy + gap_h / 2, pcy + pgap_h / 2)
            overlap = bot - top
            assert overlap >= CHANNEL_MIN + 2 * EFFECTIVE_R, \
                f"{name}: channel pinch {overlap:.0f}px < " \
                f"{CHANNEL_MIN + 2 * EFFECTIVE_R}px between gaps {i-1}->{i}"
            # The centre-line climb between two pillars must be buyable inside
            # the travel time (spacing / SCROLL_BASE). Tighter spacing yields
            # FEWER taps, so this is the binding constraint now.
            travel_s = spacing / SCROLL_BASE
            taps = max(1, math.floor(travel_s / 0.34))   # ~0.34 s per useful tap
            climb_budget = FLAP_RISE * taps
            rise = max(0.0, pcy - cy)                     # upward demand
            assert rise <= climb_budget, \
                f"{name}: needs {rise:.0f}px climb, budget {climb_budget:.0f}px"
        prev = (x, cy, gap_h, _seed)
    return True


# ── palette shaping per time-of-day ──────────────────────────────────────────
# The corridor must read from the carved silhouette, so we nudge the REAL
# biome palette per phase before handing it to draw_pillar_pair: SUNSET goes
# a value cooler/darker so pale stone doesn't wash into the pink sky; NIGHT
# keeps its moonlit stone (we add an explicit rim-light pass on top).

def _shift(c, dr, dg, db):
    return (max(0, min(255, c[0] + dr)),
            max(0, min(255, c[1] + dg)),
            max(0, min(255, c[2] + db)))


def _toward(c, target, t):
    """Blend colour c a fraction t toward target — used to collapse the brick
    AO/edge value gap without changing hue families."""
    return (int(round(c[0] + (target[0] - c[0]) * t)),
            int(round(c[1] + (target[1] - c[1]) * t)),
            int(round(c[2] + (target[2] - c[2]) * t)))


def shaped_palette(phase, dense=False):
    """A local copy of the biome palette tuned so the carved corridor reads
    at every time of day. Never mutates the cached biome dict.

    `dense=True` flattens the brick-coursing CONTRAST: the dark edge/AO tone
    (`stone_dark`) is lifted ~35% toward the mid body and the light tone
    pulled gently down, so the masonry collapses into one calm recessive
    value instead of a high-frequency lattice. This changes only how the wall
    READS — the corridor geometry / asserts are untouched."""
    pal = dict(palette_for_phase(phase))
    if 0.30 < phase < 0.45:        # SUNSET — darken + cool the stone
        for k in ('stone_light', 'stone_mid', 'stone_dark', 'stone_accent'):
            r, g, b = pal[k]
            pal[k] = _shift((r, g, b), -28, -14, +8)
    if dense:
        mid = pal['stone_mid']
        # Collapse the AO/edge darkness ~35% toward the body so per-brick
        # coursing recedes; ease the light tone down a touch so the lit faces
        # stop sparkling. Net: lower wall contrast, calmer recessive mass.
        pal['stone_dark'] = _toward(pal['stone_dark'], mid, 0.38)
        pal['stone_light'] = _toward(pal['stone_light'], mid, 0.20)
        pal['stone_accent'] = _toward(pal['stone_accent'], mid, 0.22)
    return pal


# ── rendering ────────────────────────────────────────────────────────────────

def draw_sky_ground(surf, w, h, palette):
    """Self-contained vertical sky gradient + ground band, sized to the wide
    strip cell (the cached helpers assume the 360px canvas width)."""
    top = palette['sky_top']
    mid = palette['sky_mid']
    bot = palette['sky_bot']
    for y in range(GROUND_Y):
        t = y / GROUND_Y
        if t < 0.5:
            c = lerp_color(top, mid, t * 2)
        else:
            c = lerp_color(mid, bot, (t - 0.5) * 2)
        pygame.draw.line(surf, c, (0, y), (w, y))
    # Ground band.
    for y in range(GROUND_Y, h):
        t = (y - GROUND_Y) / max(1, h - GROUND_Y)
        c = lerp_color(palette['ground_top'], palette['ground_mid'], t)
        pygame.draw.line(surf, c, (0, y), (w, y))
    # Soft horizon seam so the ground reads as grounded, not pasted.
    pygame.draw.line(surf, palette['ground_top'], (0, GROUND_Y), (w, GROUND_Y))


def _channel_polys(pagodas):
    """Top + bottom rims of the threadable channel, densely sampled along a
    smoothstep so the carved tube has soft parabolic walls (no kinks)."""
    xs = [p[0] for p in pagodas]
    tops = [p[1] - p[2] / 2 + EFFECTIVE_R for p in pagodas]
    bots = [p[1] + p[2] / 2 - EFFECTIVE_R for p in pagodas]
    pts_top, pts_bot = [], []
    steps = 12
    for i in range(len(pagodas) - 1):
        for s in range(steps):
            t = s / steps
            tt = t * t * (3 - 2 * t)
            x = xs[i] + (xs[i + 1] - xs[i]) * t
            pts_top.append((x, tops[i] + (tops[i + 1] - tops[i]) * tt))
            pts_bot.append((x, bots[i] + (bots[i + 1] - bots[i]) * tt))
    pts_top.append((xs[-1], tops[-1]))
    pts_bot.append((xs[-1], bots[-1]))
    return pts_top, pts_bot


def _channel_fill_poly(pts_top, pts_bot):
    """Closed polygon covering the whole threadable interior (top rim across,
    bottom rim back) — the negative-space slot, used as a mask boundary."""
    return pts_top + pts_bot[::-1]


def draw_wall_recede(surf, pagodas, palette, phase):
    """Mat a thin recessive veil over the WALL masonry of dense rows so the
    brick coursing collapses into one calm value and the corridor becomes the
    only high-contrast event. We paint a full-cell veil tinted toward the
    sky/ground value, then punch the channel interior back out so the route
    keeps its full contrast."""
    pts_top, pts_bot = _channel_polys(pagodas)
    veil = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    # Tint the veil toward the local sky value so walls drift back into the
    # atmosphere rather than going muddy — keeps the warren airy.
    if 0.55 < phase < 0.75:           # NIGHT — pull walls toward dim sky-blue
        tint, a = (40, 52, 80), 70
    elif 0.30 < phase < 0.45:         # SUNSET — cool the masonry back
        tint, a = (120, 110, 130), 58
    else:                              # DAY — gentle haze
        tint, a = (205, 200, 195), 56
    veil.fill((*tint, a))
    # Punch the channel interior fully transparent so only the WALLS recede.
    interior = _channel_fill_poly(pts_top, pts_bot)
    if len(interior) >= 3:
        pygame.draw.polygon(veil, (0, 0, 0, 0), interior)
    surf.blit(veil, (0, 0))


def draw_corridor_glow(surf, pagodas, phase, *, dense=False):
    """Carve the slot into a TUBE, not a gap: a clear lighter-value interior
    band hugs BOTH channel walls (top + bottom) so the parrot reads as flying
    INSIDE a corridor, plus a floor-pooled inner glow for depth. SUNSET gets a
    cooler tint to separate from the warm sky; NIGHT pushes the interior value
    up so the ROUTE is the brightest thing on screen. Dense rows get the band
    pushed brighter/wider so packed walls can't out-read the corridor."""
    pts_top, pts_bot = _channel_polys(pagodas)
    band = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)

    # Tint + strength per phase.
    if 0.30 < phase < 0.45:           # SUNSET — cool cyan-white separation
        tint = (200, 235, 245)
        layers = 5
        base_a = 18
        rim_tint, rim_a = (225, 245, 250), 40
    elif 0.55 < phase < 0.75:         # NIGHT — bright moonlit channel floor
        tint = (200, 230, 255)
        layers = 7
        base_a = 26
        rim_tint, rim_a = (215, 235, 255), 52
    else:                              # DAY — gentle warm pooling
        tint = (255, 248, 210)
        layers = 4
        base_a = 14
        rim_tint, rim_a = (255, 250, 225), 34

    if dense:
        # On packed rows the walls compete hardest, so the tube band needs to
        # win: brighter interior + an extra ~15% value at NIGHT per the brief.
        base_a += 8
        rim_a += 14

    # Interior "tube" band hugging BOTH walls: a lit lining a fixed fraction in
    # from each rim. Lighting both sides (not just the floor) is what turns a
    # "gap between two objects" into a corridor the bird flies down the middle
    # of — the single fix for the Woven-Offset 'two walls' read.
    inset = 0.30                       # band depth as fraction of channel height
    upper_in = [(xt, yt + (yb - yt) * inset)
                for (xt, yt), (xb, yb) in zip(pts_top, pts_bot)]
    lower_in = [(xb, yb - (yb - yt) * inset)
                for (xt, yt), (xb, yb) in zip(pts_top, pts_bot)]
    # Top lining: between the top rim and its inset edge.
    top_band = pts_top + upper_in[::-1]
    # Bottom lining: between the bottom rim and its inset edge.
    bot_band = lower_in + pts_bot[::-1]
    for poly in (top_band, bot_band):
        if len(poly) >= 3:
            pygame.draw.polygon(band, (*rim_tint, rim_a), poly)

    # Floor-pooled inner glow: stack progressively thinner polys hugging the
    # floor so alpha accumulates toward the channel bottom (depth, not a flat
    # fill).
    for li in range(layers):
        f = (li + 1) / layers            # 1.0 = whole channel, small = near floor
        upper = [(xb, yb + (yt - yb) * f)
                 for (xt, yt), (xb, yb) in zip(pts_top, pts_bot)]
        floor = [(xb, yb) for (xt, yt), (xb, yb)
                 in zip(pts_top[::-1], pts_bot[::-1])]
        poly = upper + floor
        a = base_a if li == layers - 1 else base_a + 6
        if len(poly) >= 3:
            pygame.draw.polygon(band, (*tint, a), poly)
    surf.blit(band, (0, 0))


def draw_rim_light(surf, pagodas, palette, *, dense=False):
    """Cool moonlit rim along the carved channel walls — a 1-2 px lit edge that
    traces the serrated silhouette so the corridor walls read crisply at
    NIGHT instead of dissolving into the dark sky. On dense rows the wall rim
    is knocked down (thinner + dimmer) so the bright channel interior, not the
    serrated wall edge, stays the brightest thing on screen."""
    pts_top, pts_bot = _channel_polys(pagodas)
    rim = palette.get('stone_accent', (200, 225, 255))
    rim = _shift(rim, 0, 6, 20)
    if dense:
        rim = _shift(rim, -55, -45, -25)     # dimmer edge on packed walls
        width = 1
    else:
        width = 2
    if len(pts_top) >= 2:
        pygame.draw.lines(surf, rim, False,
                          [(int(x), int(y)) for x, y in pts_top], width)
        pygame.draw.lines(surf, rim, False,
                          [(int(x), int(y)) for x, y in pts_bot], width)


def draw_flight_path(surf, pagodas):
    """Cyan dotted centre-line — parabolic hops between gap centres so it
    matches what a one-button flapper actually flies. Colourblind-safe cyan
    over a white core, drawn at every time of day."""
    xs = [p[0] for p in pagodas]
    cys = [p[1] for p in pagodas]
    samples = []
    steps = 16
    for i in range(len(pagodas) - 1):
        x0, x1 = xs[i], xs[i + 1]
        y0, y1 = cys[i], cys[i + 1]
        for s in range(steps):
            t = s / steps
            x = x0 + (x1 - x0) * t
            # A real flap is a parabola: rise fast off the tap, ease at the
            # crest, fall under gravity. Blend a smoothstep base with a small
            # parabolic sag so the dotted line reads as a hop, not a ramp.
            tt = t * t * (3 - 2 * t)
            sag = math.sin(t * math.pi) * (-10 if y1 >= y0 else 10) * 0.45
            y = y0 + (y1 - y0) * tt + sag
            samples.append((x, y))
    samples.append((xs[-1], cys[-1]))
    for i, (x, y) in enumerate(samples):
        if i % 2 == 0:
            pygame.draw.circle(surf, (240, 255, 255), (int(x), int(y)), 3)
            pygame.draw.circle(surf, (0, 200, 230), (int(x), int(y)), 2)


def _path_y_at(pagodas, bx):
    """Smoothstep-interpolated channel-centre y at world x — used to seat the
    parrot ON the flight line with clear air above and below."""
    xs = [p[0] for p in pagodas]
    cys = [p[1] for p in pagodas]
    for i in range(len(pagodas) - 1):
        if xs[i] <= bx <= xs[i + 1]:
            t = (bx - xs[i]) / (xs[i + 1] - xs[i])
            tt = t * t * (3 - 2 * t)
            return cys[i] + (cys[i + 1] - cys[i]) * tt
    return cys[-1]


def render_cell(cell_w, cell_h, design_fn, phase, *, highlight=True,
                dense=False):
    """One gameplay strip: sky/ground + fused pagoda walls + (optional) carved
    inner glow + parabolic dotted path + the real parrot threading the slot.

    `highlight=False` is the structure-check mode: glow, rim-light and path
    are suppressed so the corridor must read from silhouette alone.
    `dense=True` flattens the masonry contrast (recessive wall) and strengthens
    the tube-interior band, so packed rows read as a corridor not a brick wall."""
    palette = shaped_palette(phase, dense=dense)
    is_night = 0.55 < phase < 0.75
    surf = pygame.Surface((cell_w, cell_h))
    draw_sky_ground(surf, cell_w, cell_h, palette)

    # First pagoda offset in from the left so the warren reads as on-screen.
    pagodas = design_fn(64)
    assert_passable(design_fn.__name__, pagodas)

    for idx, (x, cy, gap_h, seed) in enumerate(pagodas):
        top_h = cy - gap_h / 2
        bot_y = cy + gap_h / 2
        top_rect = pygame.Rect(int(x - PIPE_W / 2), 0, PIPE_W, int(top_h))
        bot_rect = pygame.Rect(int(x - PIPE_W / 2), int(bot_y),
                               PIPE_W, int(GROUND_Y - bot_y))
        draw_pillar_pair(surf, top_rect, bot_rect, palette, seed,
                         phase=phase, is_rush=False, pillar_index=idx + 1)

    # Dense rows get a thin recessive veil matted over the WALL mass only (the
    # channel interior is cut back out below), settling the high-frequency
    # coursing into one calm value so the corridor becomes the contrast event.
    if dense:
        draw_wall_recede(surf, pagodas, palette, phase)

    if highlight:
        draw_corridor_glow(surf, pagodas, phase, dense=dense)
        if is_night:
            draw_rim_light(surf, pagodas, palette, dense=dense)
        draw_flight_path(surf, pagodas)

    # Parrot seated ON the path near mid-corridor, with deliberate clear
    # daylight above and below it so it reads as a scale ruler with room to
    # manoeuvre. We pick a pillar whose gap is roomy and centre the bird in it.
    px_idx = len(pagodas) // 2
    bx = (pagodas[px_idx][0] + pagodas[px_idx + 1][0]) / 2 \
        if px_idx + 1 < len(pagodas) else pagodas[px_idx][0]
    by = _path_y_at(pagodas, bx)
    if highlight:
        nxt = _path_y_at(pagodas, bx + 24)
        tilt = -12 if nxt > by else 12
        bird = get_parrot(1, tilt)
        surf.blit(bird, (int(bx - bird.get_width() / 2),
                         int(by - bird.get_height() / 2)))
    return surf


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))   # video context for convert/blit paths

    CELL_W, CELL_H = 960, 640
    SCALE = 0.42                      # shrink wide strips into a tidy grid
    sw, sh = int(CELL_W * SCALE), int(CELL_H * SCALE)

    cols = len(TIMES)
    rows = len(DESIGNS)
    PAD = 22
    GAP = 12
    ROW_LBL = 150     # left gutter for design names
    COL_LBL = 26
    TITLE_H = 46
    STRIP_GAP = 30    # breathing room before the structure-check band
    STRIP_LBL = 24

    grid_h = rows * sh + (rows - 1) * GAP

    canvas_w = ROW_LBL + cols * sw + (cols - 1) * GAP + PAD * 2
    # Structure-check strip: all 5 designs across the full grid span, so the
    # tile width is the available span / 5 and the height follows the cell
    # aspect. Reserve the strip's true height in the canvas up front.
    strip_x0 = PAD + ROW_LBL
    strip_avail = canvas_w - strip_x0 - PAD
    scw = (strip_avail - (rows - 1) * GAP) // rows
    sch = int(scw * CELL_H / CELL_W)
    CAP_H = 22
    strip_h = STRIP_LBL + sch + CAP_H

    canvas_h = (TITLE_H + COL_LBL + grid_h + STRIP_GAP + strip_h + PAD * 2)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((22, 24, 32))

    f_title = pygame.font.SysFont(None, 36, bold=True)
    f_col = pygame.font.SysFont(None, 24, bold=True)
    f_row = pygame.font.SysFont(None, 22, bold=True)
    f_strip = pygame.font.SysFont(None, 26, bold=True)
    f_cap = pygame.font.SysFont(None, 18, bold=True)

    title = f_title.render(
        "PAGODA WARREN — fused-masonry corridor look-dev", True,
        (240, 240, 245))
    canvas.blit(title, (PAD, PAD - 4))

    x0 = PAD + ROW_LBL
    y0 = PAD + TITLE_H + COL_LBL

    for c, (tname, _phase) in enumerate(TIMES):
        cx = x0 + c * (sw + GAP)
        lbl = f_col.render(tname, True, (210, 215, 225))
        canvas.blit(lbl, (cx + (sw - lbl.get_width()) // 2,
                          y0 - COL_LBL + 2))

    for r, (dname, design_fn, dense) in enumerate(DESIGNS):
        ry = y0 + r * (sh + GAP)
        # design name in the left gutter, vertically centred on the row
        for li, line in enumerate(_wrap(dname, 14)):
            lbl = f_row.render(line, True, (235, 225, 160))
            canvas.blit(lbl, (PAD, ry + sh // 2 - 12 + li * 18))
        for c, (tname, phase) in enumerate(TIMES):
            cell = render_cell(CELL_W, CELL_H, design_fn, phase, dense=dense)
            scaled = pygame.transform.smoothscale(cell, (sw, sh))
            cx = x0 + c * (sw + GAP)
            pygame.draw.rect(canvas, (70, 78, 100),
                             pygame.Rect(cx - 1, ry - 1, sw + 2, sh + 2), 1)
            canvas.blit(scaled, (cx, ry))

    # ── structure-check strip — DAY, highlight OFF ──────────────────────────
    # Proves the winding route reads from the carved silhouette alone: no
    # glow, no rim-light, no dotted path, no parrot.
    strip_y = y0 + grid_h + STRIP_GAP
    strip_lbl = f_strip.render(
        "STRUCTURE CHECK — all 5 designs, highlight off (DAY)", True,
        (255, 210, 150))
    canvas.blit(strip_lbl, (PAD, strip_y))
    sy = strip_y + STRIP_LBL
    day_phase = TIMES[0][1]
    # All 5 designs across the full grid span (scw/sch computed up front) — the
    # two recuts (Woven Offset and Straight Undulating) most need the
    # silhouette test, so none is dropped for width.
    for r, (dname, design_fn, dense) in enumerate(DESIGNS):
        scol = strip_x0 + r * (scw + GAP)
        cell = render_cell(CELL_W, CELL_H, design_fn, day_phase,
                           highlight=False, dense=dense)
        scaled = pygame.transform.smoothscale(cell, (scw, sch))
        pygame.draw.rect(canvas, (70, 78, 100),
                         pygame.Rect(scol - 1, sy - 1, scw + 2, sch + 2), 1)
        canvas.blit(scaled, (scol, sy))
        cap = f_cap.render(dname[:16], True, (200, 205, 215))
        canvas.blit(cap, (scol + (scw - cap.get_width()) // 2, sy + sch + 2))

    out_dir = os.path.join("docs", "pagoda_warren")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_3.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")
    print("all passability asserts passed")


def _wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    main()
