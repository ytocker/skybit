"""Live buff-sandstone sidewalk floor — the play-scene ground (replaces grass).

Closure-extracted verbatim from the foreground design exploration
(`archive/foreground_redesign/foreground_grounded.py` on branch
`claude/skybit-graphics-sky-variant-eTxX7`): the chosen `fg_swatch_buff_running_bond`
painter plus its transitive helper closure (colour math, grain, running-bond
courses). Procedural only; safe on native + web.
"""
from __future__ import annotations

import math
import random

import pygame

# Cache of grain tile surfaces keyed by amplitude — the per-frame floor grain
# reuses these so the scrolling stays cheap.
_GRAIN_CACHE: dict = {}

def _clamp(c):
    return max(0, min(255, int(c)))

def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))

def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))

def _luma(c):
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255.0

def _sat(c, f):
    g = _luma(c) * 255.0
    return (_clamp(g + (c[0] - g) * f),
            _clamp(g + (c[1] - g) * f),
            _clamp(g + (c[2] - g) * f))

def _nightf(pal):
    """Continuous 0..1 night-ness from sky_top luminance, so a plane can cool its
    surface and add lantern/edge warmth as the stage darkens without a hard step."""
    r, g, b = pal.get('sky_top', (60, 120, 200))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return max(0.0, min(1.0, (95.0 - lum) / 75.0))

def _scatter(scroll, w, speed, step, seed_off, margin=24):
    """Yield (screen_x, cell_index, rng) for jittered points marching in world
    space, so any near-plane detail scrolls seamlessly with the world and tiles
    deterministically per cell. The plane itself is static; this only places
    surface marks (pebbles, stones, reeds) that ride the scroll."""
    phase = scroll * speed
    # A placed element extends RIGHT of its cell x by up to ~the cell size (a full
    # running-bond brick tile is `step` wide and can sit a half-brick to the right
    # of `sx`). Keep a cell live on the LEFT until it is FULLY past the edge —
    # culling at -margin dropped tiles whose right half was still on screen, which
    # flickered the sidewalk's left edge as tiles scrolled off.
    left = 2 * step + margin
    first = int((phase - left) // step) - 1
    last = int((phase + w + margin) // step) + 2
    for k in range(first, last + 1):
        rng = random.Random((k * 2654435761 ^ seed_off) & 0xFFFFFFFF)
        wx = k * step + rng.uniform(-step * 0.25, step * 0.25)
        # floor (not int truncation): truncation rounds toward zero, so a mark
        # straddling x=0 hops 1px as it crosses the origin AND lands differently
        # when the same world content is baked at a shifted origin. floor is
        # origin-invariant, so a strip baked at any anchor matches the live draw.
        sx = math.floor(wx - phase)
        if -left < sx < w + margin:
            yield sx, k, rng

def _flat_slab(surf, w, h, top_y, top_col, bot_col, ease=1.0):
    """Paint an opaque vertical-gradient land plane from a FLAT top edge at
    `top_y` down to the true frame bottom h. No silhouette, no wave — just a
    solid grounded surface. `ease`>1 keeps it lighter near the front lip and
    darkens toward the foot for a near->far value fall under the eye."""
    depth = h - top_y
    if depth <= 0:
        return
    span = max(1, depth - 1)
    for i in range(depth):
        t = (i / span) ** ease
        pygame.draw.line(surf, _mix(top_col, bot_col, t),
                         (0, top_y + i), (w, top_y + i))

def _grain_tiles(amp):
    """Two 4x4 ordered-dither tiles (brighten / darken) for cheap surface grain.
    A compact ordered matrix avoids per-pixel work at blit time — tile, then
    blit ADD/SUB over the plane. Cached per amp."""
    cached = _GRAIN_CACHE.get(amp)
    if cached is not None:
        return cached
    m = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))
    pos = pygame.Surface((4, 4))
    neg = pygame.Surface((4, 4))
    for ty in range(4):
        for tx in range(4):
            off = ((m[ty][tx] + 0.5) / 16.0 - 0.5) * 2.0 * amp
            p = max(0, int(round(off)))
            n = max(0, int(round(-off)))
            pos.set_at((tx, ty), (p, p, p))
            neg.set_at((tx, ty), (n, n, n))
    _GRAIN_CACHE[amp] = (pos, neg)
    return pos, neg

def _apply_grain_scroll(surf, x0, y0, w, hh, amp, scroll, speed=0.22):
    """Scroll-LOCKED grain: the dither tile is phase-shifted by the world scroll
    so the speckle rides the surface as it moves instead of crawling in screen
    space (the screen-space _apply_grain shimmers under motion). The 4px tile
    wraps on its own period, so a sub-tile phase offset is all that's needed to
    anchor the grain to world-x; sand uses this so the tooth tracks the dunes."""
    if amp <= 0 or hh <= 0:
        return
    pos, neg = _grain_tiles(amp)
    # Build a w+4 strip so a 0..3px horizontal phase can slide without a gap.
    strip_p = pygame.Surface((w + 4, 4))
    strip_n = pygame.Surface((w + 4, 4))
    for x in range(0, w + 4, 4):
        strip_p.blit(pos, (x, 0))
        strip_n.blit(neg, (x, 0))
    ox = -int(scroll * speed) % 4
    for y in range(0, hh, 4):
        surf.blit(strip_p, (x0 - ox, y0 + y), special_flags=pygame.BLEND_RGB_ADD)
        surf.blit(strip_n, (x0 - ox, y0 + y), special_flags=pygame.BLEND_RGB_SUB)

def _sandstone(pal):
    """Worn warm-sandstone paving tone tied to the Songyue brick family (the same
    stone_dark->tan mix the pillar candidate uses), so the courtyard reads as the
    same masonry as the pagoda standing on it."""
    return _mix(pal.get('stone_dark', (95, 70, 55)), (206, 170, 124), 0.62)

def _premium_base_v8(surf, w, gy, h, pal, front, back, *, ease=1.0,
                     lip_warm=(255, 244, 222), lip_a=70):
    """The round-8 grounded plane on the 45px hero strip. Identical opaque
    value-fall slab from the FLAT top edge at GROUND_Y (y=595) down to h as
    round 7 — but the back-edge treatment is inverted: instead of a BLEND_SUB
    near-black contact line that read as a dark seam against the sky, the top
    row gets a soft WARM-LIT 1px lip (a low-alpha warm tone, value-only) so the
    floor's topmost opaque pixels read as a lit bevel meeting the mountains.
    A single faint shadow hairline sits one row BELOW the lit lip to still set
    the plane apart as its own object, but it never touches the y=595 edge.
    No additive sheen here — concepts add their own controlled, capped light so
    nothing can pool toward white. Returns (top_y, region_h, night)."""
    night = _nightf(pal)
    top_y = gy                       # FLUSH with the mountain bases at y=595.
    region_h = h - top_y             # exactly 45px on the live canvas.
    _flat_slab(surf, w, h, top_y, back, front, ease=ease)

    # Soft warm-lit top lip RIGHT AT y=595: the opaque top row reads lit, not as
    # a dark seam. Warmth fades toward night so the lip cools with the stage but
    # never goes dark (the seam read). Value-only alpha blend, never additive.
    lip = pygame.Surface((w, 1), pygame.SRCALPHA)
    lit = _mix(front, lip_warm, 0.45)
    # The lip cools AND DARKENS toward night so the topmost opaque row sits
    # below the night-sky luma instead of floating bright (a lit lip that stayed
    # warm at night would glow at the seam). At full night it sits at the night
    # surface value, not above it.
    lit = _mix(lit, _shade(front, -10), night)
    lip.fill((*lit, int(lip_a * (1.0 - 0.55 * night)) + int(18 * (1.0 - night))))
    surf.blit(lip, (0, top_y))
    # A faint object-defining shadow hairline ONE row below the lit lip — keeps
    # the floor reading as its own plane sitting in front of the mountains,
    # without ever darkening the y=595 edge itself.
    sh = pygame.Surface((w, 1), pygame.SRCALPHA)
    sh.fill((*_shade(_sat(back, 0.92), -16 - int(6 * night)), 90))
    surf.blit(sh, (0, top_y + 1))
    return top_y, region_h, night

def _brick_tones(pal, body, *, night, cool=False):
    """Shared LIT-PLANE brick palette. Returns (front, back, mortar, bevel_lt,
    bevel_dk) all retinted toward a cool dark night ground so the walkway sits
    BELOW the night sky (the round's gate) with DARK mortar and no glow. `cool`
    swaps the day warmth out for a stone-grey cast (the paver counterpoint).
    Mortar is a desaturated, shaded body so a running-bond course can never
    read as a bright/dark seam line across the screen."""
    front = _shade(_sat(body, 1.05 if not cool else 0.92), 4)
    if _luma(front) * 255.0 > 222:                # never approach white in DAY
        front = _mix(front, _shade(body, -8), 0.5)
    back = _shade(_sat(body, 0.88), -22)
    # Night ground: cool + dark, so even the lit front lands under the ~89-luma
    # night sky. Pavers pull to a slightly cooler blue than warm clay.
    night_dk = (34, 42, 62) if not cool else (30, 40, 58)
    front = _mix(front, night_dk, 0.72 * night)
    back = _mix(back, _shade(night_dk, -8), 0.78 * night)
    # Mortar: low-contrast, desaturated, a notch darker than the body — and
    # night-cooled so it stays the darkest read on the plane after dark.
    mortar = _shade(_sat(body, 0.74), -34 - int(8 * night))
    mortar = _mix(mortar, _shade(night_dk, -12), 0.80 * night)
    # Per-brick bevel: a lit upper-left lip + a shadow lower-right. Kept value-
    # only and LOW-CONTRAST (close to the face) so that even where many bricks
    # in a running-bond course share a top-edge y, the aligned lit lips never
    # sum into a bright continuous horizontal seam across the screen. Per-brick
    # face value variation, not the bevel, carries the primary relief read.
    # The lit lip blend is nudged DOWN ~14% from the round-11 0.16 so the bevel
    # peaks sit closer to the brick body value — kills any residual bright-line
    # read where a course of left-edge lips would otherwise sum under scroll.
    bevel_lt = _mix(front, (255, 246, 224) if not cool else (236, 240, 248),
                    0.138 * (1.0 - 0.5 * night))
    # Shadow bevel kept moderate (not deep) so an aligned course of brick
    # bottoms reads as a soft recessed joint, never a hard dark seam line.
    bevel_dk = _shade(_sat(body, 0.85), -20 - int(8 * night))
    bevel_dk = _mix(bevel_dk, _shade(night_dk, -10), 0.78 * night)
    return front, back, mortar, bevel_lt, bevel_dk

def _brick_face(pal, base, srng, *, night, cool=False, spread=12):
    """Per-brick worn value variation around `base`: a small deterministic value
    drift so no two bricks read identical (the worn-clay charm), kept tonal so
    the field never sparkles. Capped under the day white-pool ceiling. `spread`
    widens the worn light/dark band (a few more notably lighter/darker bricks)
    without moving the mean — the field never looks like a flat repeat under
    fast scroll."""
    d = srng.randint(-spread, spread)
    c = _shade(base, d)
    # An occasional cooler/warmer clay so a course carries a few stand-out
    # bricks, like a real reclaimed-brick walkway. A second rarer roll pushes a
    # handful of bricks notably further off the mean (both ways) so the worn
    # spread reads wider without lifting the average.
    if srng.random() < 0.22:
        tgt = (150, 70, 50) if not cool else (120, 126, 138)
        c = _mix(c, _mix(tgt, (40, 48, 66), 0.7 * night), 0.28)
    if srng.random() < 0.14:
        c = _shade(c, srng.choice((-1, 1)) * srng.randint(spread, spread + 7))
    if _luma(c) * 255.0 > 222:
        c = _mix(c, _shade(base, -10), 0.5)
    return c

def _running_bond_courses(surf, w, gy, h, scroll, pal, *, body, cool,
                          lip_warm, lip_a, stray_tgt):
    """Shared tuned running-bond painter for both the warm clay lead and its cool
    paver counterpoint. The two differ ONLY by palette (`body`/`cool`/`lip_*`),
    so the geometry — flush first course at the v8 lip, longer paver-ratio
    bricks, recessed-dark mortar with a held-down bevel, wide per-brick worn
    spread — tunes once and stays identical between the warm/cool pair.

    The first course is anchored FLUSH at the warm-lit lip (y=595): the painter
    walks courses DOWN from top_y by an explicit course pitch rather than the
    foreshortened _perspective_y back-edge (which packed the first course into an
    ~11px sliver that read as starting low). Each course foreshortens only mildly
    so the brick FIELD itself begins at the lip, not a few px below it."""
    front, back, mortar, bevel_lt, bevel_dk = _brick_tones(
        pal, body, night=_nightf(pal), cool=cool)
    top_y, region_h, night = _premium_base_v8(
        surf, w, gy, h, pal, front, back, ease=0.95,
        lip_warm=lip_warm, lip_a=lip_a)

    # Bedding mortar behind the bricks so every gap reads as a recessed joint —
    # kept a hair DARKER than the brick body (a set-in mortar course, never a
    # raised bright line) at a slightly higher alpha than round 11 so the joint
    # never lifts toward the brick value under scroll.
    bed = pygame.Surface((w, region_h), pygame.SRCALPHA)
    bed.fill((*mortar, 150))
    surf.blit(bed, (0, top_y))

    mid_lo = top_y + region_h * 0.30
    mid_hi = top_y + region_h * 0.72
    # Explicit course pitch anchored at the lip: courses step DOWN from top_y so
    # the first brick row's top edge lands ON y=595, foreshortening only gently
    # toward the back (the near courses sit a touch taller). 5 courses over 45px
    # gives a true sidewalk-paver row height, not the chunky round-11 6-course
    # stack.
    n_course = 5
    edges = [top_y]
    acc = 0.0
    # Course heights grow toward the front (near) for a mild perspective; summed
    # to exactly region_h so the last course foot lands on h.
    weights = [0.78 + 0.16 * (c / max(1, n_course - 1)) for c in range(n_course)]
    wsum = sum(weights)
    for c in range(n_course):
        acc += weights[c] / wsum * region_h
        edges.append(top_y + int(round(acc)))
    for c in range(n_course):
        y_back = edges[c]
        y_front = edges[c + 1]
        if y_front <= y_back + 1:
            continue
        depth_t = (c + 0.5) / n_course
        # Paver-ratio bricks: ~10% LONGER than the round-11 30..52px so the tile
        # reads as a real sidewalk paver, not a chunky stock brick.
        brick_w = int(34 + 24 * depth_t)
        # Running bond: alternate courses shift a half-brick. The shift is part
        # of the world lattice (added to the world index) so it wraps with scroll.
        bond = (c % 2) * (brick_w // 2)
        # The sidewalk IS the ground plane the pillars stand on → it scrolls at
        # the full world speed (1.0), locked to the props so a planter stays on
        # its brick. (Was a slow ~0.2 parallax that read as "not moving".)
        speed = 1.0
        in_mid = mid_lo <= (y_back + y_front) * 0.5 <= mid_hi
        bh = y_front - y_back
        # Mortar gap is the 1px between the bedding band and each brick face;
        # inset the brick by 1px on all sides so the dark bedding shows as joints.
        # Continuous near->far value ramp keyed off the course's actual screen-y
        # (not the discrete course index): consecutive courses no longer plate to
        # one flat value with a value STEP at each boundary — the only row-to-row
        # drop left at a course line is the intended recessed-dark mortar joint,
        # never a bright step UP into a brighter plate. Kills the round-12 seam
        # the discrete per-course base produced.
        cy_t = ((y_back + y_front) * 0.5 - top_y) / max(1, region_h)
        # Compress the front->back ramp toward the mid value so the per-course
        # value STEP at a course boundary stays small (a gentle depth fall, not a
        # plate jump): the only strong row-to-row drop left is the recessed-dark
        # mortar joint, not a bright step onto a brighter course.
        cy_t = 0.5 + (cy_t - 0.5) * 0.55
        for sx, k, srng in _scatter(scroll, w, speed, brick_w, 0xB21 + c):
            bx = sx + bond
            base = _mix(back, front, cy_t)
            # Wider worn value spread (~10% past round 11) so a few more bricks
            # read notably lighter/darker and the field never looks like a flat
            # repeat under fast scroll — value-only, mean held.
            fr = _brick_face(pal, base, srng, night=night, cool=cool, spread=14)
            if in_mid:
                fr = _mix(fr, base, 0.16)
            rect = (bx + 1, y_back + 1, brick_w - 2, bh - 2)
            if rect[2] <= 0 or rect[3] <= 0:
                continue
            pygame.draw.rect(surf, fr, rect)
            # Bevel only on the VERTICAL edges (lit left / shadow right) so the
            # relief reads per-brick without ever forming a bright HORIZONTAL
            # line: in running bond every brick in a course shares one top-edge
            # y, so a lit top lip would sum into a continuous bright seam. The
            # horizontal course joint instead reads softly from the recessed
            # dark bedding gap alone — a low-contrast mortar course, not a seam.
            pygame.draw.line(surf, bevel_lt, (rect[0], rect[1]),
                             (rect[0], rect[1] + rect[3] - 1), 1)
            pygame.draw.line(surf, bevel_dk, (rect[0] + rect[2] - 1, rect[1]),
                             (rect[0] + rect[2] - 1, rect[1] + rect[3] - 1), 1)
            # No additive glint on either palette: the front already sits bright,
            # and an ADD dab there risks a single clipped-white pixel where it
            # stacks with the grain. The crisp vertical bevel + the recessed
            # bedding joint carry the premium read.

    _apply_grain_scroll(surf, 0, top_y, w, region_h, 3, scroll, 1.0)

def _buff_body(pal):
    """Pale buff / warm sandstone — a light, low-chroma cream-tan pulled from the
    sandstone family, lifted toward bone so it reads tone-on-tone with the cream
    pagoda. Warm (cool=False); the day cap in `_brick_tones` keeps it under the
    white-pool ceiling."""
    # Bone-lift target pulled a notch DOWN from a pure cream so the night retint
    # (the lightest body resists the night_dk mix the most) lands the night body
    # clearly UNDER the night-sky band — keeps the day buff light/tone-on-tone
    # with the cream pagoda while clearing the no-glow night gate.
    base = _mix(_sandstone(pal), pal.get('stone_light', (188, 170, 146)), 0.55)
    return _mix(_sat(base, 0.82), (196, 178, 144), 0.45)

def fg_swatch_buff_running_bond(surf, w, gy, h, scroll, pal):
    _running_bond_courses(
        surf, w, gy, h, scroll, pal,
        body=_buff_body(pal), cool=False,
        lip_warm=(255, 244, 224), lip_a=60, stray_tgt=(176, 150, 112))
