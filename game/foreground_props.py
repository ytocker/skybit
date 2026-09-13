"""Round-15 SIDEWALK DRESSING — composition pass over the round-14 props.

Round 14 dialled in the dressing concept (promenade furniture drawn from
existing game/ primitives, world-anchored, capped night glow). The art-director
verdict was ITERATE: the concept + night-glow cap read right, but the
SILHOUETTE / COMPOSITION needed surgery. Round 15 applies that punch list and
leaves the luminance contract untouched:

  1. DOUBLED-TOWER — the dark vertical mass that abutted the cream pillar's left
     shoulder was a BACKGROUND near-pagoda from the mountain band, not a prop.
     The r15 harness slides the world scroll so that near-pagoda clears the
     pillar lane, leaving a clean sky gap. Props themselves are also kept out of
     a WIDER pillar-lane quiet zone so nothing of ours abuts x≈244 either.
  2. POSTS OUT OF THE BIRD LANE — the bird flies at x≈BIRD_X=90 with the coin a
     little ahead. Every vertical post anchor is moved to x<55 or into the
     x≈140..180 dead zone, and posts are SHORT (head in the lower band, y≥~490)
     so no tall thin vertical ever sits at the bird's altitude.
  3-6. Per-style fixes: a single clean fairy-light catenary with fewer/larger
     bulbs; a present-but-dim night core on the serene stone lamp + a larger
     cairn; a truly minimal Elegant row (one lantern lamp + bench + planter);
     and the Temple prayer-flags CUT in favour of the legible lantern garland.

The night-glow contract is preserved exactly: lit props are gated to a dark sky
and capped under the coin (NIGHT_LUMA_CAP), day cells are unlit shells.

Pure-Pygame / pygbag-safe: fill, blit, draw.*, SRCALPHA, BLEND_RGB_ADD only.
No numpy / gfxdraw / per-frame surfarray. Nothing here is written into game/.
"""
from __future__ import annotations

import math

import pygame

# Read-only imports of the live game's procedural primitives.
from game.ambient import _build_bench_sprite
from game.pillar_variants import draw_cascading_vine, draw_cairn
from game.draw import draw_side_shrub, draw_wuling_pine

# The night-luma contract + dark-sky gate live in the pillar-redesign archive.
# Night-luma helpers live with the promoted pagoda art on the live branch.
from game.pillar_pagodas import _is_dark_sky
from game.pagoda_ornaments import _clamp_night


# ── shared colour helpers (mirror foreground_grounded so tones harmonise) ─────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _nightf(pal):
    """Continuous 0..1 night-ness off sky_top luma (matches foreground_grounded
    so props cool in lockstep with the floor they sit on)."""
    r, g, b = pal.get('sky_top', (60, 120, 200))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return max(0.0, min(1.0, (95.0 - lum) / 75.0))


# ── world-anchored placement ──────────────────────────────────────────────────
#
# A prop pinned to a world-x appears at screen-x = (world_x - scroll*mult) %
# period, so it tracks the pavement with no jitter and wraps seamlessly. `mult`
# matches the near-floor parallax the running-bond courses use (~0.20).

GROUND_Y = 595  # sidewalk top edge; props' feet rest here.
# The foreground IS the ground plane the pillars stand on, so it scrolls at the
# full world speed (1.0×) — props/people pass at the same rate pillars approach.
GROUND_MULT = 1.0
PROP_MULT = GROUND_MULT


def _world_xs(scroll, w, period, x0, mult=PROP_MULT, margin=70):
    """Yield screen-x for a prop repeated every `period` world-px, anchored at
    world-offset `x0`, scroll-locked. `margin` lets a wide prop spill off-edge
    without popping."""
    phase = scroll * mult
    first = int((phase - margin - x0) // period) - 1
    last = int((phase + w + margin - x0) // period) + 1
    for k in range(first, last + 1):
        sx = int(x0 + k * period - phase)
        if -margin < sx < w + margin:
            yield sx, k


# ── per-slot decision latch ───────────────────────────────────────────────────
#
# A world-anchored slot is first yielded by `_world_xs`/`_near_xs` while it is
# still OFF-SCREEN to the right (the window runs out to sx < w+margin) and stops
# being yielded once OFF-SCREEN to the left (sx <= -margin). So if every
# time-varying decision for a slot (is it shown? which scene/act? is its phase
# window open?) is computed ONCE the first frame the slot appears and then held,
# nothing can pop, vanish, or morph while any part of it is on screen — objects
# only ever scroll in from the right and scroll off the left. The day-arc still
# changes the street: it just takes effect for slots that haven't entered yet.

_LATCH: dict = {}        # {row_id: {k: decision}}
_LATCH_SEEN: dict = {}   # {row_id: set(k seen this frame)}


def _slot_latch(row_id, k, compute):
    """Return slot `k`'s decision for `row_id`, computed once at first sighting
    (off-screen) and reused until the slot scrolls out (then dropped by
    `_latch_prune`). `compute` is a 0-arg callable evaluated at most once."""
    row = _LATCH.get(row_id)
    if row is None:
        row = _LATCH[row_id] = {}
    if k not in row:
        row[k] = compute()
    seen = _LATCH_SEEN.get(row_id)
    if seen is None:
        seen = _LATCH_SEEN[row_id] = set()
    seen.add(k)
    return row[k]


def _latch_prune(row_id):
    """Drop latched slots not seen this frame — they've scrolled off (or out of
    the placement window), so a far-future re-entry is re-decided fresh. Call once
    after a row's placement loop."""
    seen = _LATCH_SEEN.pop(row_id, None)
    row = _LATCH.get(row_id)
    if not row:
        return
    if not seen:
        row.clear()
        return
    for k in [k for k in row if k not in seen]:
        del row[k]


# ── lane quiet zones ──────────────────────────────────────────────────────────
#
# The bird flies at x≈BIRD_X=90 with the coin a little ahead (~x168). Keep that
# whole corridor AND a generous band in front of the pillar base free of tall
# furniture so nothing reads as an obstacle. The bird lane is widened from r14
# to swallow the coin's leading position; the pillar lane is widened so props
# never abut the cream shaft at x≈244.

_BIRD_LANE = (48, 188)        # bird at 90 + coin out to ~168
_PILLAR_LANE = (212, 320)     # in front of the pillar base x ≈ 244

# A narrow "dead zone" between the two lanes where a SHORT post may stand.
_POST_DEADZONE = (138, 182)


def _in_quiet_zone(sx, half_w=10):
    # Full-speed scroll: gating an element out at the bird column would make it
    # WINK as it scrolled through mid-screen. The bird + pipes draw on top of the
    # foreground, so nothing needs a clear lane — let everything scroll cleanly.
    return False


# Short ground furniture (benches, planters, cairns, barrels — all ≤~28px tall)
# sits on the pavement well BELOW the bird's altitude, so it only needs to clear
# the PILLAR base, not the whole bird corridor. This narrower gate lets the
# sparse rows place a single bench in-frame without it vanishing behind the
# wide tall-obstacle bird lane.
_GROUND_PILLAR_LANE = (222, 312)


def _ground_clear(sx, half_w=10):
    # Short furniture sits below the bird; with no fixed pillar it can stand
    # anywhere (a scrolling pillar simply occludes it where they overlap).
    return True


def _post_ok(sx, half_w=6):
    # Posts scroll through freely; the bird/pipes draw on top so a post passing
    # behind the bird is fine, and gating it would make it wink mid-screen.
    return True


# ── warm lit halo, night-only, capped ────────────────────────────────────────
#
# The single source of festive light. Daylight => no glow. Dark sky => a soft
# additive halo whose colour is clamped well under NIGHT_LUMA_CAP so the lamps
# can never out-shine a coin. Strength scales with night-ness for a smooth
# dusk->night fade-in rather than a hard pop.

_GLOW_CACHE: dict = {}

# The additive PEAK is held well under NIGHT_LUMA_CAP (153) so even where a halo
# lands on the brightest lit lantern face, base+halo stays below the coin.
_GLOW_PEAK = 92


def _warm_glow(radius, color, peak):
    """A cached radial halo for BLEND_RGB_ADD whose RGB falls off to zero at the
    rim. `peak` is the centre add (capped); ratios preserve the warm hue. `peak`
    is bucketed to 8-steps so the dusk->night night-ness ramp (which slides peak
    continuously) reuses ~12 cached halos per (radius,colour) instead of baking a
    fresh gradient each step — and the cache stays bounded (8-step quantisation is
    imperceptible on an additive halo)."""
    peak = (max(0, int(peak)) // 8) * 8
    key = (radius, color, peak)
    g = _GLOW_CACHE.get(key)
    if g is not None:
        return g
    if len(_GLOW_CACHE) >= 256:          # FIFO bound — never grows unboundedly
        del _GLOW_CACHE[next(iter(_GLOW_CACHE))]
    size = radius * 2 + 2
    surf = pygame.Surface((size, size))
    surf.fill((0, 0, 0))
    cx = cy = radius + 1
    mx = max(1, max(color))
    base = tuple(int(peak * c / mx) for c in color)
    for r in range(radius, 0, -1):
        f = 1.0 - (r / radius)
        f = f * f
        col = (int(base[0] * f), int(base[1] * f), int(base[2] * f))
        pygame.draw.circle(surf, col, (cx, cy), r)
    _GLOW_CACHE[key] = surf
    return surf


def _add_lamp_glow(surf, cx, cy, pal, *, radius=16, alpha=120, color=(255, 196, 110)):
    """Blit a capped warm halo at (cx, cy) ONLY when the sky is dark. `alpha`
    scales the peak add (0..~_GLOW_PEAK). Returns the night strength (0 by day)."""
    if not _is_dark_sky(pal):
        return 0.0
    night = _nightf(pal)
    strength = max(0.0, min(1.0, (night - 0.45) / 0.55))
    if strength <= 0.02:
        return 0.0
    peak = int(min(_GLOW_PEAK, _GLOW_PEAK * (alpha / 120.0)) * strength)
    if peak <= 1:
        return strength
    g = _warm_glow(radius, color, peak)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)
    return strength


# ── prop primitives built on the game helpers ─────────────────────────────────

def _draw_bench(surf, sx, pal, tint=None):
    """Place the cached 42×28 park-bench sprite with its feet at GROUND_Y,
    cooled toward night so it sits in the same value band as the pavement."""
    sprite = _build_bench_sprite()
    night = _nightf(pal)
    if tint is not None or night > 0.05:
        sprite = sprite.copy()
        if tint is not None:
            sprite.fill((*tint, 255), special_flags=pygame.BLEND_RGBA_MULT)
        if night > 0.05:
            k = int(255 * (1 - 0.34 * night))
            kb = int(255 * (1 - 0.28 * night))
            sprite.fill((k, k, kb, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sw, sh = sprite.get_size()
    surf.blit(sprite, (sx - sw // 2, GROUND_Y - sh + 1))


def _draw_planter(surf, sx, pal, *, w=18, kind='shrub', color=None):
    """A small stone/terracotta planter box with greenery, feet at GROUND_Y."""
    night = _nightf(pal)
    box_h = 9
    by = GROUND_Y - 1
    box = color or _mix(pal.get('stone_mid', (150, 132, 110)), (150, 120, 92), 0.5)
    box = _mix(box, (60, 70, 100), 0.30 * night)
    pygame.draw.rect(surf, _shade(box, -18), (sx - w // 2, by - box_h, w, box_h))
    pygame.draw.rect(surf, box, (sx - w // 2 + 1, by - box_h, w - 2, box_h - 2))
    pygame.draw.rect(surf, _shade(box, 16), (sx - w // 2 + 1, by - box_h, w - 2, 2))
    fol = {
        'foliage_dark': _mix(pal.get('foliage_dark', (40, 80, 55)), (40, 56, 86), 0.3 * night),
        'foliage_mid': _mix(pal.get('foliage_mid', (60, 110, 75)), (46, 64, 94), 0.3 * night),
        'foliage_top': _mix(pal.get('foliage_top', (96, 150, 100)), (60, 80, 110), 0.3 * night),
    }
    if kind == 'conifer':
        # The plant family's tiered ink-wash bonsai-pine, planted in the box.
        draw_wuling_pine(surf, sx, by - box_h - 1, 30, fol)
    elif kind == 'bamboo':
        _draw_bamboo_canes(surf, sx, by - box_h, fol, night)
    else:
        draw_side_shrub(surf, sx, by - box_h - 2, fol, scale=1.15)


def _draw_bamboo_canes(surf, sx, top_y, fol, night):
    """Three vertical SEGMENTED bamboo canes with visible node bands + a small
    leaf tuft at each top — NO umbrella crown. Cane colour is the warm green of
    the foliage mid, cooled toward night so it stays in the deck value band."""
    dark, mid, top = fol['foliage_dark'], fol['foliage_mid'], fol['foliage_top']
    cane = _mix((150, 178, 108), (60, 74, 100), 0.34 * night)
    cane_dk = _shade(cane, -36)
    cane_lt = _shade(cane, 18)
    for dx, htop, lean in ((-4, 31, -1), (1, 38, 1), (5, 28, 2)):
        cx = sx + dx
        ct = top_y - htop
        segs = 5
        for s in range(segs):
            y0 = top_y - htop * s // segs
            y1 = top_y - htop * (s + 1) // segs
            nx0 = cx + int(lean * (s / segs))
            nx1 = cx + int(lean * ((s + 1) / segs))
            pygame.draw.line(surf, cane, (nx0, y0), (nx1, y1 + 1), 2)
            pygame.draw.line(surf, cane_lt, (nx0, y0), (nx1, y1 + 1), 1)
            pygame.draw.line(surf, cane_dk, (nx1 - 1, y1), (nx1 + 1, y1), 2)
        _leaf_tuft(surf, cx + lean, ct, 1.55, 9, mid, n=3, spread=0.7)
        _leaf_tuft(surf, cx + lean, ct, 1.95, 7, top, n=2, spread=0.5)
        _leaf_tuft(surf, cx + lean, ct + 4, 1.25, 6, dark, n=2, spread=0.6)


def _leaf_tuft(surf, ox, oy, ang, length, col, *, n=4, spread=0.5):
    for i in range(n):
        a = ang + (i - (n - 1) / 2) * spread / max(1, n - 1)
        ex = ox + int(math.cos(a) * length)
        ey = oy - int(math.sin(a) * length)
        mx = ox + int(math.cos(a) * length * 0.5)
        my = oy - int(math.sin(a) * length * 0.5) - 1
        pygame.draw.lines(surf, col, False, [(ox, oy), (mx, my), (ex, ey)], 1)


# Lamp posts are SHORT in r15: the head sits in the lower band (~y490+) so a
# thin vertical never climbs to the bird's altitude. `head_y` is computed from a
# capped height budget.
LAMP_HEAD_Y_FLOOR = 488  # head never higher than this (kept in the lower band).


def _draw_lamp_post(surf, sx, pal, *, style='ornate', height=98, lantern='red'):
    """A slim, SHORT street-lamp: a dark post topped with a lantern head carrying
    a capped warm glow at night. The head is clamped into the lower band so the
    post never reads as a tall obstacle at the bird's altitude."""
    night = _nightf(pal)
    base_y = GROUND_Y - 1
    top_y = max(LAMP_HEAD_Y_FLOOR, base_y - height)
    height = base_y - top_y
    if style == 'stone':
        post = _mix(pal.get('stone_mid', (150, 132, 110)), (120, 110, 96), 0.5)
        pw = 4
    elif style == 'minimal':
        post = _mix((60, 56, 60), (90, 84, 80), 0.4)
        pw = 3
    else:  # ornate wrought-iron
        post = (54, 48, 46)
        pw = 3
    post = _mix(post, (54, 60, 86), 0.32 * night)
    pygame.draw.rect(surf, _shade(post, -14), (sx - pw, base_y - 5, pw * 2, 5))
    pygame.draw.rect(surf, _shade(post, 10), (sx - pw, base_y - 5, pw * 2, 1))
    pygame.draw.rect(surf, post, (sx - pw // 2, top_y + 6, max(2, pw - 1), height - 6))
    pygame.draw.line(surf, _shade(post, 20), (sx - pw // 2, top_y + 6),
                     (sx - pw // 2, base_y - 5), 1)
    if style == 'ornate':
        pygame.draw.arc(surf, post, (sx - 9, top_y + 4, 18, 14), math.radians(20), math.radians(160), 2)
        pygame.draw.circle(surf, _shade(post, 14), (sx, top_y + 4), 2)
    if lantern in ('red', 'gold'):
        _draw_lantern_head(surf, sx, top_y + 8, pal, color=lantern, scale=0.85,
                           glow_radius=12, glow_alpha=64)
    else:
        _draw_glass_head(surf, sx, top_y + 8, pal, style=style)


def _draw_lantern_head(surf, cx, cy, pal, *, color='red', scale=0.85,
                       glow_radius=None, glow_alpha=None):
    """A hanging paper-lantern head with a night-gated, capped warm halo. The
    painted body is dimmed HARD at night so face + additive halo stay under the
    coin; the halo scales with the lantern so a dense garland can't sum into a
    bright band."""
    night = _nightf(pal)
    dark = (170, 30, 35) if color == 'red' else (190, 140, 40)
    light = (230, 80, 65) if color == 'red' else (245, 210, 100)
    if night > 0.3:
        k = min(1.0, night)
        dark = _mix(dark, _shade(dark, -40), 0.6 * k)
        light = _clamp_night(_mix(light, _shade(light, -55), 0.55 * k))[:3]
    lw, lh = max(8, int(15 * scale)), max(10, int(19 * scale))
    cap = max(2, int(3 * scale))
    body = pygame.Rect(cx - lw // 2, cy + cap - 1, lw, lh - 2 * cap + 2)
    pygame.draw.rect(surf, (55, 35, 25), (cx - lw // 2 + 1, cy, lw - 2, cap))
    pygame.draw.rect(surf, (55, 35, 25), (cx - lw // 2 + 1, cy + lh - cap, lw - 2, cap))
    pygame.draw.ellipse(surf, dark, body)
    pygame.draw.ellipse(surf, light, body.inflate(-max(2, int(3 * scale)), -max(1, int(2 * scale))))
    gr = glow_radius if glow_radius is not None else max(7, int(11 * scale))
    ga = glow_alpha if glow_alpha is not None else 70
    _add_lamp_glow(surf, cx, cy + lh // 2, pal, radius=gr, alpha=ga,
                   color=(255, 150, 110) if color == 'red' else (255, 205, 120))


def _draw_glass_head(surf, cx, cy, pal, *, style='minimal', warm_core=False):
    """A clean four-pane glass lantern head for the refined/stone lamps. With
    `warm_core` the head carries a small, present-but-dim lit pane at night even
    for the quiet styles, so the serene/minimal lamps aren't dead after dusk."""
    night = _nightf(pal)
    frame = _mix((50, 46, 48), (80, 76, 72), 0.4)
    frame = _mix(frame, (54, 60, 86), 0.3 * night)
    glass_day = _mix(pal.get('horizon', (250, 226, 184)), (210, 220, 230), 0.5)
    lit = _clamp_night((255, 210, 150))[:3] if _is_dark_sky(pal) else glass_day
    gw, gh = 11, 14
    box = pygame.Rect(cx - gw // 2, cy, gw, gh)
    pygame.draw.polygon(surf, frame, [(cx - gw // 2 - 2, cy), (cx + gw // 2 + 2, cy), (cx, cy - 6)])
    # With a warm_core the lit pane leans further toward the warm lamp colour at
    # night so the serene/minimal lamp clearly reads as lit (still dimmer than the
    # festive paper lanterns, just no longer a cold dead pane).
    pane_t = 0.10 if (warm_core and _is_dark_sky(pal)) else 0.25
    pygame.draw.rect(surf, _mix(lit, glass_day, pane_t), box)
    pygame.draw.rect(surf, frame, box, 1)
    pygame.draw.line(surf, frame, (cx, cy), (cx, cy + gh), 1)
    pygame.draw.line(surf, frame, (cx - gw // 2, cy + gh // 2), (cx + gw // 2, cy + gh // 2), 1)
    pygame.draw.rect(surf, frame, (cx - 2, cy + gh, 4, 3))
    # The serene/minimal styles get a dimmer halo than the festive lanterns but a
    # NON-zero one at night so the lamp still reads as a light source.
    alpha = 60 if warm_core else 50
    _add_lamp_glow(surf, cx, cy + gh // 2, pal, radius=12, alpha=alpha,
                   color=(255, 208, 150))


def _catenary_pts(x1, x2, top_y, sag, steps):
    """A quadratic sag arc from (x1,top_y) to (x2,top_y) dipping `sag` at centre."""
    mx = (x1 + x2) * 0.5
    my = top_y + sag
    out = []
    for i in range(steps + 1):
        t = i / steps
        bx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2
        by = (1 - t) ** 2 * top_y + 2 * (1 - t) * t * my + t * t * top_y
        out.append((bx, by))
    return out


def _garland_spans(scroll, w, period, x0, mult=PROP_MULT):
    """Yield (x_left, x_right) screen spans for a festive strand repeated every
    `period` world-px, scroll-locked, so the bunting wraps seamlessly across the
    whole promenade regardless of which posts happen to be on screen."""
    phase = scroll * mult
    first = int((phase - x0) // period) - 1
    last = int((phase + w - x0) // period) + 1
    for k in range(first, last + 1):
        xl = x0 + k * period - phase
        xr = xl + period
        if xr > -10 and xl < w + 10:
            yield xl, xr, k


def _span_point(xl, xr, top_y, sag, t):
    mx = (xl + xr) * 0.5
    bx = (1 - t) ** 2 * xl + 2 * (1 - t) * t * mx + t * t * xr
    by = (1 - t) ** 2 * top_y + 2 * (1 - t) * t * (top_y + sag) + t * t * top_y
    return bx, by


def _draw_lantern_garland(surf, w, scroll, pal, *, top_y, period=120, sag=24,
                          per_span=3, colors=('red', 'gold'), span_gate=None):
    """A self-contained, world-anchored strand of paper lanterns slung in
    repeating catenary spans across the whole pavement. Each lantern carries a
    capped night halo; the rope sags on a quadratic arc between hook points a
    `period` apart, so it reads as continuous festive bunting independent of the
    lamp posts. `span_gate(k)` (optional) latches each span in/out at entry so the
    strand scrolls in/out span-by-span instead of the whole row flashing."""
    night = _nightf(pal)
    rope = _mix((62, 52, 44), (40, 44, 60), 0.3 * night)
    for xl, xr, k in _garland_spans(scroll, w, period, x0=12):
        if span_gate is not None and not span_gate(k):
            continue
        pts = _catenary_pts(xl, xr, top_y, sag, 16)
        pygame.draw.lines(surf, rope, False, [(int(x), int(y)) for x, y in pts], 1)
        for j in range(per_span):
            t = (j + 0.5) / per_span
            bx, by = _span_point(xl, xr, top_y, sag, t)
            _draw_lantern_head(surf, int(bx), int(by), pal,
                               color=colors[j % len(colors)], scale=0.6,
                               glow_radius=7, glow_alpha=52)


def _draw_fairy_lights(surf, w, scroll, pal, *, top_y, period=200, sag=26,
                       per_span=5, span_gate=None):
    """Warm fairy-light bunting redrawn for r15 as ONE clean catenary with FEWER,
    LARGER, brighter bulbs (3px lit nodes + a soft per-bulb halo) so it reads as
    a festive string rather than a scribbly wire crossing the lane. The wire is a
    single thin arc; only the bulbs carry weight. `span_gate(k)` (optional) latches
    each span in/out at entry so the strand scrolls rather than flashing."""
    night = _nightf(pal)
    wire = _mix((78, 70, 62), (46, 50, 66), 0.35 * night)
    dark = _is_dark_sky(pal)
    warm = (250, 200, 120)
    bead = _mix(warm, (118, 108, 94), 0.55)
    for xl, xr, k in _garland_spans(scroll, w, period, x0=8):
        if span_gate is not None and not span_gate(k):
            continue
        pts = _catenary_pts(xl, xr, top_y, sag, 20)
        pygame.draw.lines(surf, wire, False, [(int(x), int(y)) for x, y in pts], 1)
        for j in range(per_span):
            t = (j + 0.5) / per_span
            bx, by = _span_point(xl, xr, top_y, sag, t)
            bx, by = int(bx), int(by) + 2
            if dark:
                lit = _clamp_night(warm)[:3]
                # A larger bulb body so it reads at 1×, with a tiny hot centre.
                pygame.draw.circle(surf, _mix(lit, (180, 120, 70), 0.4), (bx, by), 3)
                pygame.draw.circle(surf, lit, (bx, by), 2)
                _add_lamp_glow(surf, bx, by, pal, radius=7, alpha=54, color=warm)
            else:
                pygame.draw.circle(surf, _shade(bead, -10), (bx, by), 3)
                pygame.draw.circle(surf, bead, (bx, by), 2)


def _draw_glass_post_clean(surf, sx, pal, *, height=84):
    """The Holiday-Lights post simplified to an instantly-readable silhouette:
    a short minimal pole + a single clean glass-lantern head (no wreath clutter),
    head in the lower band."""
    _draw_lamp_post(surf, sx, pal, style='minimal', height=height, lantern='glass')


def _draw_cairn(surf, sx, pal, *, scale=1.0):
    """A stacked-stone cairn. r15 can enlarge it so it doesn't vanish as a tiny
    dark lump at night; the soft night cool wash is shaped as stacked ellipses
    (not a visible box) so it cools with the stage cleanly."""
    night = _nightf(pal)
    n = 4 if scale > 1.05 else 3
    draw_cairn(surf, sx, GROUND_Y - 1, n=n)
    if scale > 1.05:
        # Re-stack a slightly larger crown stone on top so the cairn gains height
        # without a second helper, using the helper's own warm tones.
        pygame.draw.ellipse(surf, (60, 45, 35), (sx - 6, GROUND_Y - 28, 12, 6))
        pygame.draw.ellipse(surf, (200, 178, 146), (sx - 5, GROUND_Y - 27, 10, 5))
    if night > 0.1:
        a = int(58 * night)
        wash = pygame.Surface((22, 30), pygame.SRCALPHA)
        for (ew, eh, dy) in ((18, 8, 20), (14, 6, 13), (10, 5, 7), (8, 4, 2)):
            pygame.draw.ellipse(wash, (44, 54, 84, a), (11 - ew // 2, dy, ew, eh))
        surf.blit(wash, (sx - 11, GROUND_Y - 31))


def _draw_barrel(surf, sx, pal):
    """A wooden planter-barrel — a chunkier far-left anchor for the serene row so
    the left edge isn't a single tiny lump."""
    night = _nightf(pal)
    by = GROUND_Y - 1
    bw, bh = 16, 16
    wood = _mix((120, 84, 52), (70, 76, 96), 0.32 * night)
    pygame.draw.ellipse(surf, _shade(wood, -22), (sx - bw // 2, by - bh, bw, bh))
    pygame.draw.ellipse(surf, wood, (sx - bw // 2 + 1, by - bh, bw - 2, bh - 1))
    band = _mix((60, 56, 56), (40, 46, 64), 0.3 * night)
    for dy in (bh - 4, bh // 2):
        pygame.draw.arc(surf, band, (sx - bw // 2, by - dy - 3, bw, 6), math.radians(200), math.radians(340), 2)
    fol = {
        'foliage_dark': _mix(pal.get('foliage_dark', (40, 80, 55)), (40, 56, 86), 0.3 * night),
        'foliage_mid': _mix(pal.get('foliage_mid', (60, 110, 75)), (46, 64, 94), 0.3 * night),
        'foliage_top': _mix(pal.get('foliage_top', (96, 150, 100)), (60, 80, 110), 0.3 * night),
    }
    draw_side_shrub(surf, sx, by - bh + 1, fol, scale=1.25)


def _draw_vine_trail(surf, sx, pal):
    """A cascading vine draped over a planter's front-left lip onto the sidewalk.
    The attachment sits at the box rim so the vine visibly grips the edge (its
    grip leaf tucks at the lip) rather than floating above the pavement."""
    night = _nightf(pal)
    fol = {
        'foliage_dark': _mix(pal.get('foliage_dark', (40, 80, 55)), (40, 56, 86), 0.3 * night),
        'foliage_mid': _mix(pal.get('foliage_mid', (60, 110, 75)), (46, 64, 94), 0.3 * night),
        'foliage_top': _mix(pal.get('foliage_top', (96, 150, 100)), (60, 80, 110), 0.3 * night),
    }
    # The planter box rim is ~9px tall with feet at GROUND_Y-1; attach at the rim.
    draw_cascading_vine(surf, sx, GROUND_Y - 10, 14, fol)


# ══════════════════════════════════════════════════════════════════════════
# Style rows. Each lays a coherent set of furniture across the pavement,
# world-anchored, clearing the bird + pillar lanes. Vertical posts are gated
# through `_post_ok` so they only stand at the far left or in the mid dead zone.
# ══════════════════════════════════════════════════════════════════════════

def _bench_tint(pal):
    return None


def props_temple_festival(surf, w, gy, h, scroll, pal):
    """Ornate wrought-iron lamp posts + a red/gold paper-lantern garland strung
    between them + a stone bench + a planter. The prayer-flag bunting from r14 is
    CUT — it was the noisy, illegible element; the lantern garland now carries
    the whole festive read."""
    period = 250
    _draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 96, period=118,
                          sag=24, per_span=3)
    for sx, k in _world_xs(scroll, w, period, x0=20):
        if _post_ok(sx):
            _draw_lamp_post(surf, sx, pal, style='ornate', height=100, lantern='red')
    for sx, k in _world_xs(scroll, w, period, x0=160):
        if _post_ok(sx):
            _draw_lamp_post(surf, sx, pal, style='ornate', height=92, lantern='gold')
    for sx, k in _world_xs(scroll, w, period, x0=95):
        if _ground_clear(sx, 22):
            _draw_bench(surf, sx, pal, tint=_bench_tint(pal))
    for sx, k in _world_xs(scroll, w, period, x0=120):
        if _ground_clear(sx, 12):
            _draw_planter(surf, sx, pal, kind='shrub')


def props_holiday_lights(surf, w, gy, h, scroll, pal):
    """ONE clean fairy-light catenary (fewer/larger/brighter bulbs) + a single
    clean glass-lantern post (no wreath clutter) + a classic park bench + potted
    mini-evergreens."""
    period = 240
    _draw_fairy_lights(surf, w, scroll, pal, top_y=GROUND_Y - 92, period=210, sag=28, per_span=5)
    for sx, k in _world_xs(scroll, w, period, x0=28):
        if _post_ok(sx):
            _draw_glass_post_clean(surf, sx, pal, height=86)
    for sx, k in _world_xs(scroll, w, period, x0=150):
        if _post_ok(sx):
            _draw_glass_post_clean(surf, sx, pal, height=82)
    for sx, k in _world_xs(scroll, w, period, x0=108):
        if _ground_clear(sx, 22):
            _draw_bench(surf, sx, pal, tint=_bench_tint(pal))
    for sx, k in _world_xs(scroll, w, period, x0=120):
        if _ground_clear(sx, 12):
            _draw_planter(surf, sx, pal, kind='conifer')


def props_serene_garden(surf, w, gy, h, scroll, pal):
    """Minimal festivity: a stone lamp with a small present-but-dim night core +
    a chunky barrel-planter + a cairn + a cascading vine + a bench. Natural,
    contemplative, but no longer dead after dusk."""
    period = 260
    for sx, k in _world_xs(scroll, w, period, x0=24):
        if _post_ok(sx):
            # Stone post with a glass head carrying a soft warm core at night.
            night = _nightf(pal)
            base_y = GROUND_Y - 1
            top_y = max(LAMP_HEAD_Y_FLOOR, base_y - 84)
            post = _mix(_mix(pal.get('stone_mid', (150, 132, 110)), (120, 110, 96), 0.5),
                        (54, 60, 86), 0.32 * night)
            pygame.draw.rect(surf, _shade(post, -14), (sx - 4, base_y - 5, 8, 5))
            pygame.draw.rect(surf, post, (sx - 2, top_y + 6, 3, base_y - 5 - (top_y + 6)))
            _draw_glass_head(surf, sx, top_y + 8, pal, style='stone', warm_core=True)
    # A chunky barrel at far left so it doesn't vanish; a cairn at mid dead zone.
    for sx, k in _world_xs(scroll, w, period, x0=14):
        if sx + 8 < 52:
            _draw_barrel(surf, sx, pal)
    for sx, k in _world_xs(scroll, w, period, x0=155):
        if _ground_clear(sx, 12):
            _draw_planter(surf, sx, pal, kind='shrub')
            _draw_vine_trail(surf, sx + 11, pal)
    for sx, k in _world_xs(scroll, w, period, x0=118):
        if _ground_clear(sx, 12):
            _draw_cairn(surf, sx, pal, scale=1.2)
    for sx, k in _world_xs(scroll, w, period, x0=95):
        if _ground_clear(sx, 22):
            _draw_bench(surf, sx, pal, tint=_bench_tint(pal))


def props_elegant_minimal(surf, w, gy, h, scroll, pal):
    """ACTUALLY minimal: exactly ONE refined glass-lantern lamp + ONE bench + ONE
    small planter per period. No tiered tower, no second post — negative space
    sells the elegance. The glass-lantern lamp was the nicest single prop on the
    r14 sheet; it carries this row."""
    # A long period keeps the row sparse — one refined set per stretch of
    # pavement. Anchors are chosen so that, at any scroll, the lamp / bench /
    # planter land in clear zones (far-left, the mid dead zone, or the strip just
    # left of the pillar) rather than the bird or pillar lanes.
    period = 300
    for sx, k in _world_xs(scroll, w, period, x0=20):
        if _post_ok(sx):
            _draw_lamp_post(surf, sx, pal, style='ornate', height=88, lantern='glass')
    for sx, k in _world_xs(scroll, w, period, x0=215):
        if _ground_clear(sx, 22):
            _draw_bench(surf, sx, pal, tint=_bench_tint(pal))
    for sx, k in _world_xs(scroll, w, period, x0=160):
        if _ground_clear(sx, 12):
            _draw_planter(surf, sx, pal, kind='shrub')


def props_the_works(surf, w, gy, h, scroll, pal):
    """The fully-dressed promenade: lamp posts + a lantern garland + a bench +
    planters + a cairn — dense but balanced, the likely shippable target. Posts
    stay out of the bird lane and short; the garland carries the festive read."""
    period = 230
    _draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 94, period=112,
                          sag=22, per_span=3)
    for sx, k in _world_xs(scroll, w, period, x0=18):
        if _post_ok(sx):
            _draw_lamp_post(surf, sx, pal, style='ornate', height=96, lantern='red')
    for sx, k in _world_xs(scroll, w, period, x0=152):
        if _post_ok(sx):
            _draw_lamp_post(surf, sx, pal, style='ornate', height=88, lantern='gold')
    for sx, k in _world_xs(scroll, w, period, x0=92):
        if _ground_clear(sx, 22):
            _draw_bench(surf, sx, pal, tint=_bench_tint(pal))
    for sx, k in _world_xs(scroll, w, period, x0=120):
        if _ground_clear(sx, 12):
            _draw_planter(surf, sx, pal, kind='conifer')
    for sx, k in _world_xs(scroll, w, period, x0=40):
        if sx + 8 < 52:
            _draw_cairn(surf, sx, pal, scale=1.1)


# Style rows in render order. (label, painter)
STYLES_R15 = [
    ("Temple Festival", props_temple_festival),
    ("Holiday Lights", props_holiday_lights),
    ("Serene Garden", props_serene_garden),
    ("Elegant Minimal", props_elegant_minimal),
    ("The Works", props_the_works),
]
