"""Round-18 EMBEDDED ground detail — environmental marks painted INTO the
paving body, beneath the r17 promenade.

Round 17 dressed the promenade with props + living characters ON TOP of the
floor. Round 18 adds the missing read: detail that lives IN the paving surface
itself (the ~45px floor body y=595..640) — hairline cracks tracking the bond,
weeds sprouting from mortar gaps, moss nestled at joints, a scatter of fallen
leaves and pebbles, an inlaid medallion on the big honey slabs, the odd storm
grate, and after-rain damp. It reads as part of the ground, not a sticker on it.

The contract that makes it belong rather than float:

  * WORLD-ANCHORED to the SAME lattice the base floor uses. Each element marches
    on `_scatter` (foreground_grounded._scatter) with the per-course speed the
    bases use (`0.18 + 0.08*depth_t`) and the brick/slab WIDTH as the step, so a
    mark pins to a real mortar joint and tiles seamlessly through the scroll wrap
    — no jitter, no seam doubling.
  * COURSE-EDGE RECOMPUTE. We mirror the exact weighted course-edge accumulation
    the running-bond / flagstone painters do, so a crack stays inside its course
    band and a weed roots at the real joint, never across a brick face.
  * RETINTED PER BASE off the same body/mortar helpers (`_clay` / `_paver_cool_body`
    / `_honey_body` -> `_brick_tones` mortar), so the detail is ONE system that
    matches whichever base it sits on.

Glow / seam / day gates (the art-director's gate list):
  * No continuous horizontal line: every element jitters its y by ±1-2px per
    anchor and the densest read is the FRONT courses; the y=595 lit lip is never
    touched.
  * Night: retint each colour toward a cool night-dark by ~0.6*night; NO additive
    blends except a single capped puddle glint under 16 alpha that fades by
    (1-0.8*night). Detail stays DARKER than the night sky and far under the coin.
  * Day: any highlight luma is capped <=220 (no white pooling).
  * The MID band (bird/pillar lanes) is quieted toward the mortar mean at lower
    density so the play lanes stay calm; the front courses carry the read.

Pure-Pygame / pygbag-safe (draw.*, SRCALPHA, capped BLEND_RGB_ADD only).
"""
from __future__ import annotations

import math
import random

import pygame

from game import foreground_floor as fg

# Reuse the base helpers READ-ONLY so detail tones track each base exactly.
_mix = fg._mix
_shade = fg._shade
_sat = fg._sat
_luma = fg._luma
_nightf = fg._nightf
_scatter = fg._scatter
_clamp = fg._clamp


# The cool night-dark every element retints toward — matches the brick night
# floor family so a mark reads as wet/dark ground after dusk, never a fresh
# bright daytime colour glowing against the night sky.
_NIGHT_DK = (30, 38, 56)

# Day highlight ceiling (mirrors _brick_tones' no-white-pool idiom): any lit lip
# we add is capped here so detail can never pool toward white in daylight.
_DAY_HI_CAP = 220


def _nretint(color, night, k=0.6):
    """Pull a detail colour toward the cool night-dark by k*night so every mark
    cools + darkens as the stage darkens. This is the no-glow gate: detail must
    sit BELOW the night sky, never emit. Value-only mix, never additive."""
    return _mix(color, _NIGHT_DK, k * night)


def _cap_hi(color):
    """Hold a highlight under the day white-pool ceiling (luma<=220)."""
    if _luma(color) * 255.0 > _DAY_HI_CAP:
        return _mix(color, _shade(color, -14), 0.5)
    return color


# ── per-base body / mortar resolve (mirrors the base painters) ────────────────

def _body_for(kind, pal):
    # Live game ships the buff sidewalk; detail tracks the buff body tone so the
    # marks read as part of THIS floor (the same _brick_tones path it painted).
    return fg._buff_body(pal), False


def _tones(kind, pal):
    """Return (front, back, mortar, night) for a base, straight from the same
    `_brick_tones` path the floor used — detail then derives crack/moss/leaf
    tones off these so it matches the exact body it sits on."""
    body, cool = _body_for(kind, pal)
    night = _nightf(pal)
    front, back, mortar, _bl, _bd = fg._brick_tones(pal, body, night=night, cool=cool)
    return front, back, mortar, night


# ── course-edge recompute (mirror the base painters' weighted accumulation) ───

def _course_edges(top_y, region_h, n_course, w0, w1):
    """Reproduce the exact edge list the running-bond / flagstone painters build:
    weights ramp from w0 (back) to w1 (front), summed to region_h, so detail
    course bands line up pixel-for-pixel with the real brick rows."""
    edges = [top_y]
    weights = [w0 + (w1 - w0) * (c / max(1, n_course - 1)) for c in range(n_course)]
    wsum = sum(weights)
    acc = 0.0
    for c in range(n_course):
        acc += weights[c] / wsum * region_h
        edges.append(top_y + int(round(acc)))
    return edges


def _bond_layout(kind, top_y, region_h):
    """Per-base course count + the (brick/slab width, bond-shift, course edges)
    the floor used. Detail anchors to THESE so weeds pin to the real joints."""
    if kind == "honey":
        n_course = 3
        edges = _course_edges(top_y, region_h, n_course, 0.82, 0.96)
        def width(c, depth_t):
            return int(70 + 36 * depth_t)
    else:
        n_course = 5
        edges = _course_edges(top_y, region_h, n_course, 0.78, 0.94)
        def width(c, depth_t):
            return int(34 + 24 * depth_t)
    return n_course, edges, width


# ── lane quieting: pull mid-band detail toward the mortar mean, lower density ──

def _mid_band(top_y, region_h):
    return top_y + region_h * 0.30, top_y + region_h * 0.72


# ══════════════════════════════════════════════════════════════════════════
# Elements. Each takes the resolved (front, back, mortar, night) + the course
# lattice and paints into the floor body. Densest in the FRONT courses.
# ══════════════════════════════════════════════════════════════════════════


def _cracks(surf, w, top_y, region_h, scroll, front, back, mortar, night,
            n_course, edges, width, mid_lo, mid_hi):
    """Hairline chips tracking the bond — short 2-segment branching stubs CONFINED
    inside a course band so a crack never bridges a mortar joint. Adapted from
    fg_cracked_earth's kinked-line logic. The crack is a notch below the mortar so
    it reads as a recessed chip; a faint lit lip on FRONT courses in daylight only."""
    crack = _shade(mortar, -8)
    crack = _nretint(crack, night)
    for c in range(n_course):
        depth_t = (c + 0.5) / n_course
        y_back, y_front = edges[c], edges[c + 1]
        if y_front <= y_back + 3:
            continue
        # Front courses carry the read; the back course gets few, faint cracks.
        front_w = depth_t
        step = width(c, depth_t)
        speed = 1.0  # locked to the floor bricks (full world-speed scroll)
        for sx, k, srng in _scatter(scroll, w, speed, step, 0x2C7 + c):
            # Density falls off toward the back; sparse everywhere.
            if srng.random() > 0.18 + 0.34 * front_w:
                continue
            in_mid = mid_lo <= (y_back + y_front) * 0.5 <= mid_hi
            if in_mid and srng.random() < 0.6:
                continue
            # Anchor inside the band with a ±1px jitter so no two cracks share a
            # row -> no horizontal line can form across a course.
            ny = srng.randint(y_back + 2, max(y_back + 2, y_front - 2))
            ny += srng.choice((-1, 0, 1))
            ny = max(y_back + 1, min(y_front - 1, ny))
            n_arms = srng.randint(1, 2)
            col = crack if not in_mid else _mix(crack, mortar, 0.45)
            for _a in range(n_arms):
                ang = srng.uniform(-0.5, 0.5) + srng.choice((0.0, math.pi))
                seg = srng.randint(4, 9)
                mx = sx + int(math.cos(ang) * seg * 0.6)
                my = ny + int(math.sin(ang) * seg * 0.45)
                ang2 = ang + srng.uniform(-0.6, 0.6)
                ex = mx + int(math.cos(ang2) * seg * 0.5)
                ey = my + int(math.sin(ang2) * seg * 0.4)
                my = max(y_back + 1, min(y_front - 1, my))
                ey = max(y_back + 1, min(y_front - 1, ey))
                pts = [(sx, ny), (mx, my), (ex, ey)]
                pygame.draw.lines(surf, col, False, pts, 1)
                # Faint sunlit lip only on the front courses in daylight, capped.
                if depth_t > 0.6 and night < 0.55 and not in_mid:
                    lip = _cap_hi(_mix(front, (255, 240, 214), 0.18))
                    pygame.draw.line(surf, lip, (pts[0][0], pts[0][1] - 1),
                                     (pts[1][0], pts[1][1] - 1), 1)


def _weeds(surf, w, top_y, region_h, scroll, front, back, mortar, night,
           n_course, edges, width, mid_lo, mid_hi, pal, accent):
    """Grass tufts / weeds sprouting from a VERTICAL mortar gap, leaning out.
    Adapted from _flower_tulip / _flower_lavender: a 1px stem + 1-2 leaf flicks,
    foliage palette, night-cooled. Roots are pinned to a real joint x (the brick
    edge), front courses denser."""
    fol_dk = _nretint(_sat(pal.get('foliage_dark', (35, 75, 35)), 0.85), night)
    fol_mid = _nretint(_sat(pal.get('foliage_mid', (60, 115, 50)), 0.82), night)
    fol_top = _nretint(_cap_hi(_sat(pal.get('foliage_top', (90, 150, 70)), 0.80)), night)
    for c in range(max(1, n_course - 3), n_course):  # front 2-3 courses only
        depth_t = (c + 0.5) / n_course
        y_back, y_front = edges[c], edges[c + 1]
        step = width(c, depth_t)
        bond = (c % 2) * (step // 2)
        speed = 1.0  # locked to the floor bricks (full world-speed scroll)
        for sx, k, srng in _scatter(scroll, w, speed, step, 0x5EED + c):
            if srng.random() > 0.20 + 0.18 * depth_t:
                continue
            in_mid = mid_lo <= (y_back + y_front) * 0.5 <= mid_hi
            if in_mid and srng.random() < 0.7:
                continue
            # Root at the joint (brick left edge) so the weed sprouts from mortar.
            rx = sx + bond
            # Sit the root near the course's FRONT joint with a small jitter.
            base_y = y_front - srng.randint(0, 2)
            lean = srng.choice((-1, 1)) * srng.randint(1, 3)
            ht = srng.randint(3, 6) + int(2 * depth_t)
            tip = (rx + lean, base_y - ht)
            pygame.draw.line(surf, fol_dk, (rx, base_y), tip, 1)
            pygame.draw.line(surf, fol_mid, (rx + 1, base_y), (tip[0] + 1, tip[1] + 1), 1)
            # One or two leaf flicks splaying out.
            for _l in range(srng.randint(1, 2)):
                lf = srng.uniform(0.35, 0.8)
                jx = rx + int(lean * lf)
                jy = base_y - int(ht * lf)
                flick = srng.choice((-2, -1, 1, 2))
                pygame.draw.line(surf, fol_mid, (jx, jy), (jx + flick, jy - 1), 1)
            # A tiny lit tip on the nearest weeds in daylight (foliage top, capped).
            # Skip (don't clamp) an off-surface tip: clamping smeared a spurious
            # green pixel onto the left edge for weeds scrolling off, and that
            # edge-only artifact also broke the strip-cache's origin invariance.
            if depth_t > 0.7 and night < 0.55:
                tx, ty = tip
                if 0 <= tx < w and 0 <= ty < surf.get_height():
                    surf.set_at((tx, ty), fol_top)


def _moss(surf, w, top_y, region_h, scroll, front, back, mortar, night,
          n_course, edges, width, mid_lo, mid_hi, pal, heavy):
    """Moss / lichen nestled at joints — a small soft dome of muted foliage,
    adapted from draw_side_shrub at small scale. `heavy` (the cool base) gets a
    denser, damper moss read. Night-cooled; front courses favoured."""
    dark = _nretint(_mix(_sat(pal.get('foliage_dark', (35, 75, 35)), 0.7),
                         mortar, 0.35), night)
    mid = _nretint(_mix(_sat(pal.get('foliage_mid', (60, 115, 50)), 0.66),
                        mortar, 0.30), night)
    top = _nretint(_cap_hi(_mix(_sat(pal.get('foliage_top', (90, 150, 70)), 0.62),
                                front, 0.18)), night)
    chance = 0.16 if not heavy else 0.30
    for c in range(max(1, n_course - 3), n_course):
        depth_t = (c + 0.5) / n_course
        y_back, y_front = edges[c], edges[c + 1]
        step = width(c, depth_t)
        bond = (c % 2) * (step // 2)
        speed = 1.0  # locked to the floor bricks (full world-speed scroll)
        for sx, k, srng in _scatter(scroll, w, speed, step, 0x4A33 + c):
            if srng.random() > chance * (0.5 + depth_t):
                continue
            in_mid = mid_lo <= (y_back + y_front) * 0.5 <= mid_hi
            if in_mid and srng.random() < 0.65:
                continue
            cx = sx + bond + srng.choice((-1, 0, 1))
            cy = y_front - srng.randint(0, 2)
            rw = max(2, int((2 + srng.randint(0, 2)) * (0.7 + 0.4 * depth_t)))
            rh = max(1, rw // 2)
            d = dark if not in_mid else _mix(dark, mortar, 0.4)
            pygame.draw.ellipse(surf, d, (cx - rw, cy - rh, rw * 2, rh * 2))
            pygame.draw.ellipse(surf, mid, (cx - rw + 1, cy - rh, rw * 2 - 2, max(1, rh * 2 - 1)))
            if depth_t > 0.6 and night < 0.6 and not in_mid:
                pygame.draw.ellipse(surf, top, (cx - rw + 2, cy - rh, max(1, rw * 2 - 4), 1))


def _litter(surf, w, top_y, region_h, scroll, front, back, mortar, night,
            n_course, edges, width, mid_lo, mid_hi, leaf_tint):
    """Fallen leaves / petals / pebbles — sparse 2px ochre/tan dots + tiny angled
    leaf-lines + a few grey pebble dots, FRONT band only. Adapted from
    _flower_mixed petal circles. `leaf_tint` flavours the leaf colour per base."""
    leaf = _nretint(_cap_hi(leaf_tint), night)
    leaf_dk = _nretint(_shade(leaf_tint, -34), night)
    pebble = _nretint(_mix(_sat(mortar, 0.7), (150, 150, 150), 0.35), night)
    pebble_hi = _cap_hi(_nretint(_shade(pebble, 26), night))
    # Front courses only (the ground litter collects near the eye).
    for c in range(max(1, n_course - 2), n_course):
        depth_t = (c + 0.5) / n_course
        y_back, y_front = edges[c], edges[c + 1]
        step = width(c, depth_t)
        speed = 1.0  # locked to the floor bricks (full world-speed scroll)
        for sx, k, srng in _scatter(scroll, w, speed, max(10, step // 2), 0x1EAF + c):
            roll = srng.random()
            if roll > 0.42:
                continue
            in_mid = mid_lo <= (y_back + y_front) * 0.5 <= mid_hi
            if in_mid and srng.random() < 0.6:
                continue
            py = srng.randint(y_back + 2, max(y_back + 2, y_front - 2))
            py += srng.choice((-1, 0, 1))
            py = max(y_back + 1, min(y_front - 1, py))
            if roll < 0.16:
                # A little fallen leaf: a short angled line + a 2px blob.
                ang = srng.uniform(0, math.pi)
                ex = sx + int(math.cos(ang) * 3)
                ey = py + int(math.sin(ang) * 2)
                col = leaf if not in_mid else _mix(leaf, mortar, 0.4)
                pygame.draw.line(surf, leaf_dk, (sx, py), (ex, ey), 1)
                pygame.draw.circle(surf, col, ((sx + ex) // 2, (py + ey) // 2), 1)
            elif roll < 0.30:
                # A petal/ochre dot.
                col = leaf if not in_mid else _mix(leaf, mortar, 0.45)
                pygame.draw.circle(surf, col, (sx, py), 1)
            else:
                # A grey pebble half-sunk: a dot with a 1px lit top.
                pygame.draw.circle(surf, pebble, (sx, py), 1)
                if (depth_t > 0.65 and night < 0.6 and not in_mid
                        and 0 <= sx < w and 0 < py < 640):
                    surf.set_at((sx, py - 1), pebble_hi)


def _medallion(surf, w, top_y, region_h, scroll, front, back, mortar, night,
               n_course, edges, width, pal):
    """ONE small inlaid temple medallion — a beveled diamond-fret accent set into
    a big honey slab. Adapted from fg_inlaid_mosaic_v8's diamond tessellation +
    a fret hatch. Placed at a chosen world-x on the front course so it tiles with
    scroll and reads as INLAID stone, not painted on. Honey base only."""
    c = n_course - 1                                   # front course (biggest slab)
    depth_t = (c + 0.5) / n_course
    y_back, y_front = edges[c], edges[c + 1]
    step = width(c, depth_t)
    speed = 1.0  # locked to the floor bricks (full world-speed scroll)
    # One medallion per long stretch: fire only on the cell whose world-index is
    # a multiple of 4, so they sit ~4 slabs apart and ride the scroll.
    bond = (c % 2) * (step // 2)
    tess = _nretint(_mix(_sat(mortar, 0.85), (150, 120, 78), 0.5), night)
    tess_lt = _cap_hi(_nretint(_mix(front, (255, 238, 206), 0.22 * (1 - 0.5 * night)), night))
    tess_dk = _nretint(_shade(mortar, -10), night)
    for sx, k, srng in _scatter(scroll, w, speed, step, 0xC0DE + c):
        if k % 4 != 0:
            continue
        cx = sx + bond + step // 2
        cy = (y_back + y_front) // 2
        r = 7 + (k % 3)
        cy = max(y_back + r, min(y_front - r, cy))
        # Beveled outer diamond.
        outer = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        pygame.draw.polygon(surf, tess, outer)
        pygame.draw.line(surf, tess_lt, (cx - r, cy), (cx, cy - r), 1)
        pygame.draw.line(surf, tess_lt, (cx, cy - r), (cx + r, cy), 1)
        pygame.draw.line(surf, tess_dk, (cx + r, cy), (cx, cy + r), 1)
        pygame.draw.line(surf, tess_dk, (cx, cy + r), (cx - r, cy), 1)
        # Inner fret diamond (a smaller inlaid core).
        ir = r // 2
        inner = [(cx, cy - ir), (cx + ir, cy), (cx, cy + ir), (cx - ir, cy)]
        pygame.draw.polygon(surf, _mix(tess, front, 0.4), inner)
        pygame.draw.polygon(surf, tess_dk, inner, 1)


def _grate(surf, w, top_y, region_h, scroll, front, back, mortar, night,
           n_course, edges, width):
    """ONE storm grate per long stretch — a small dark-iron grid (parallel + cross
    bars) set into the front course. Adapted from a cobble-curb bar grid. Iron
    stays dark + cool; night-retinted, no glow."""
    c = n_course - 1
    depth_t = (c + 0.5) / n_course
    y_back, y_front = edges[c], edges[c + 1]
    step = width(c, depth_t)
    speed = 1.0  # locked to the floor bricks (full world-speed scroll)
    iron = _nretint(_shade(_sat(mortar, 0.5), -28), night)
    iron_lt = _cap_hi(_nretint(_shade(iron, 22), night))
    iron_dk = _nretint(_shade(iron, -16), night)
    for sx, k, srng in _scatter(scroll, w, speed, step, 0x9D7A + 31 + c):
        if k % 5 != 2:                                 # one per ~5 cells
            continue
        gw = 14 + (k % 3) * 2
        gh = min(9, y_front - y_back - 2)
        if gh < 5:
            continue
        gx = sx
        gy = y_front - gh - 1
        # Recessed iron frame.
        pygame.draw.rect(surf, iron_dk, (gx - 1, gy - 1, gw + 2, gh + 2))
        pygame.draw.rect(surf, iron, (gx, gy, gw, gh))
        # A 1px inset shadow on the inner top edge so the grate reads as a slot
        # SUNK below the paving lip, not a plate laid on top — the eye reads the
        # darker hairline under the front lip as a recess.
        pygame.draw.line(surf, _shade(iron_dk, -10), (gx + 1, gy), (gx + gw - 2, gy), 1)
        # Parallel slot bars (the open grid) — dark gaps with lit bar tops.
        for bx in range(gx + 2, gx + gw - 1, 3):
            pygame.draw.line(surf, iron_dk, (bx, gy + 1), (bx, gy + gh - 1), 1)
            if night < 0.6:
                pygame.draw.line(surf, iron_lt, (bx + 1, gy + 1), (bx + 1, gy + gh - 1), 1)
        # Two cross bars frame it as a real grate.
        pygame.draw.line(surf, iron_lt if night < 0.6 else iron, (gx, gy + 1), (gx + gw - 1, gy + 1), 1)
        pygame.draw.line(surf, iron_dk, (gx, gy + gh - 1), (gx + gw - 1, gy + gh - 1), 1)


def _damp(surf, w, top_y, region_h, scroll, front, back, mortar, night,
          n_course, edges, width):
    """After-rain damp / puddle patches — ultra-low-alpha cool-dark smears in the
    FRONT band, leaning into DUSK/NIGHT for a wet promenade. Adapted from
    fg_wet_shore soft blots. An optional tiny specular glint (alpha<16) fades HARD
    toward day-dry AND toward night so it never glows after dark."""
    # Puddles read strongest at dusk (~night 0.45) and ease back at full night so
    # the festival ground is damp, not a mirror. Almost dry by full day.
    wet = max(0.0, min(1.0, (night - 0.18) * 1.7))
    wet *= (1.0 - 0.35 * max(0.0, night - 0.7) / 0.3) if night > 0.7 else 1.0
    if wet <= 0.02:
        return
    damp = _mix(mortar, (24, 30, 46), 0.55)
    for c in range(max(1, n_course - 2), n_course):
        depth_t = (c + 0.5) / n_course
        y_back, y_front = edges[c], edges[c + 1]
        step = width(c, depth_t)
        speed = 1.0  # locked to the floor bricks (full world-speed scroll)
        for sx, k, srng in _scatter(scroll, w, speed, max(16, step), 0x9D7A + c):
            if srng.random() > 0.22 * wet + 0.08:
                continue
            py = srng.randint(y_back + 2, max(y_back + 2, y_front - 2))
            sw = srng.randint(12, 26)
            sh = srng.randint(2, 4)
            a = int((10 + 9 * depth_t) * wet)
            if a <= 1:
                continue
            blot = pygame.Surface((sw, sh), pygame.SRCALPHA)
            blot.fill((*damp, a))
            surf.blit(blot, (sx - sw // 2, py - sh // 2))
            # A tiny specular glint that fades HARD toward day-dry and goes FULLY
            # MATTE by full night — the only additive in the whole system, capped
            # <16 alpha. The damp at the festival peak is wet-dark stone with no
            # specular catch (a glint at full night would read as a stray sparkle
            # rivalling the lit props), so it's clamped to zero above ~0.85 night.
            ga = int(13 * wet * max(0.0, 1.0 - 1.18 * night))
            if ga >= 2 and depth_t > 0.6:
                glint = pygame.Surface((max(2, sw // 3), 1), pygame.SRCALPHA)
                glint.fill((200, 210, 220, ga))
                surf.blit(glint, (sx - sw // 6, py - 1),
                          special_flags=pygame.BLEND_RGB_ADD)


# ══════════════════════════════════════════════════════════════════════════
# Public entry — dispatch the embedded-detail subset per base.
# ══════════════════════════════════════════════════════════════════════════

def add_embedded_detail(kind, surf, w, gy, h, scroll, pal):
    """Paint the embedded ground-surface detail INTO the buff sidewalk body,
    AFTER the floor painter and BEFORE the promenade props. One shared system,
    retinted off the buff body/mortar tones, weighted to the front courses near
    the screen bottom; the lit y=595 lip is never touched."""
    top_y = gy
    region_h = h - top_y
    if region_h <= 0:
        return
    front, back, mortar, night = _tones(kind, pal)
    n_course, edges, width = _bond_layout(kind, top_y, region_h)
    mid_lo, mid_hi = _mid_band(top_y, region_h)

    common = (surf, w, top_y, region_h, scroll, front, back, mortar, night,
              n_course, edges, width, mid_lo, mid_hi)

    # Damp first (under the marks), then cracks (the surface), organic growth,
    # loose litter on top, and the odd storm grate — a worn warm sandstone walk.
    _damp(surf, w, top_y, region_h, scroll, front, back, mortar, night,
          n_course, edges, width)
    _cracks(*common)
    _weeds(*common, pal, accent="warm")
    _moss(*common, pal, heavy=False)
    _litter(*common, leaf_tint=(170, 140, 95))
    _grate(surf, w, top_y, region_h, scroll, front, back, mortar, night,
           n_course, edges, width)
    # A sparse inlaid medallion set into the front course — re-tinted off the buff
    # body via the tones above so it reads as inlaid sandstone, not a sticker.
    _medallion(surf, w, top_y, region_h, scroll, front, back, mortar, night,
               n_course, edges, width, pal)
