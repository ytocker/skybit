"""LIVING PROMENADE — one Chinese-market street told as a full day's arc.

The sidewalk is driven by a DAY-ARC DIRECTOR (see `draw_promenade` below): a single
continuous story rather than a loop of interchangeable styles. Two signals from the
caller drive it — `phase` (biome day-cycle position) selects the dressing + cast
vocabulary and a crowd-density curve; `t` (= biome_time, 0 at run-start) ramps the
street in from empty as a run opens (the market "opening"). The arc:

  DAY    Morning market — prayer-flag bunting + a kiosk; vendors setting up
         (crate stacks), a songbird-cage stand, kids, a dog, a wish-tree.
  GOLDEN Afternoon — lamp posts + lantern garland go up; the elder on a bench.
  DUSK   Lamps lighting — a LAMPLIGHTER kindling the lanterns, strollers.
  NIGHT  Festival PEAK — garland + fairy lights + lamps glowing (capped), a
         campfire, a busy kiosk, full crowd. Then a near-empty PRE-DAWN teardown.

Dressing primitives (lamp posts, lantern garland, fairy lights, planters) come from
game.foreground_props; prayer-flag bunting from game.pillar_variants. The kids, the
elder, the kiosk, and the re-themed cast (wish-tree, songbird cage, lamplighter,
dawn set-up) are drawn here.

Glow contract preserved: capped under the coin (NIGHT_LUMA_CAP), gated to a dark
sky, and given a gentle dusk->night fade-in so dusk reads "lamps just lighting"
rather than dead-then-on. DAY/GOLDEN are unlit shells.

Pure-Pygame / pygbag-safe (fill, blit, draw.*, SRCALPHA, BLEND_RGB_ADD only).
No numpy / gfxdraw / per-frame surfarray. Nothing here is written into game/.
"""
from __future__ import annotations

import math
import random

import pygame

from game import foreground_props as sp
from game import biome as _biome
from game.config import (W, H, WEATHER_CROWD_RAIN_MIN, WEATHER_CROWD_SNOW_MIN,
                         WEATHER_UMBRELLA_RAIN_AT)
from game.weather import rain_intensity, storm_intensity, wind_intensity
from game.pillar_variants import draw_prayer_flags
from game import foreground_zbuffer as _zbuf
from game.foreground_zbuffer import TB_STRUCTURE, TB_FIXTURE, TB_CAST
from game import foreground_variants as _fv
from game import ped_cast as _ped
from game import day_cast as _day
from game import food_stalls as _food
from game import animals_cast as _animals
from game import greenery_cast as _green
from game import props_cast as _props

# Read-only access to the live ambient characters — instantiated, stepped a few
# frames to a pleasant gait, then drawn at a chosen world-x.
from game.ambient import (
    _WishingWell, _Bench, _Napper,
)

GROUND_Y = sp.GROUND_Y  # 595 — the sidewalk top edge; feet rest here.

# ── weather the street reacts to ─────────────────────────────────────────────
#
# Live rain/snow/wind for the current frame, set by draw_promenade/draw_near_lane
# from the same phase-driven curves the sky uses. Exposed as module state (the
# _CUR_* idiom) so the figure drawers can raise umbrellas / hurry / bundle up
# without threading a weather arg through every cast signature. 0 in clear skies.
_CUR_RAIN = 0.0
_CUR_SNOW = 0.0
_CUR_WIND = 0.0
_CUR_PHASE = 0.0    # live biome phase — drives the day-arc beat for variant picks


def _weather_crowd_factor(phase):
    """Crowd-density multiplier for the weather: 1.0 in clear skies, falling as
    rain/snow worsen — the street empties out in a storm. Takes the HARSHER of
    the two so a downpour and a squall don't compound into a ghost town earlier
    than intended; the snow squall bottoms out near-empty."""
    ri = rain_intensity(phase)
    wi = storm_intensity(phase)
    rain_f = 1.0 - (1.0 - WEATHER_CROWD_RAIN_MIN) * ri
    snow_f = 1.0 - (1.0 - WEATHER_CROWD_SNOW_MIN) * wi
    return min(rain_f, snow_f)


# A small festive palette so brollies pop against the muted shan-shui street;
# the per-figure pick is a stable index (clothing slot), capped under the coin
# at night like every other lit/bright element here.
_UMBRELLA_COLORS = (
    (212, 76, 76),    # red
    (74, 122, 198),   # blue
    (228, 182, 64),   # gold
    (96, 162, 112),   # green
    (180, 96, 172),   # violet
)


def _wants_umbrella():
    """True when the weather is wet/snowy enough that a walking figure would put
    up a brolly. A single frame-wide gate (not a per-figure random) so umbrellas
    appear together as the rain crosses in — no per-figure strobing."""
    return _CUR_RAIN >= WEATHER_UMBRELLA_RAIN_AT or _CUR_SNOW >= 0.35


def _draw_umbrella(surf, cx, canopy_y, color_idx, *, night=0.0, scale=1.0,
                   pole_len=9):
    """A small held umbrella: a domed, gently-scalloped canopy with a top nub, a
    couple of ribs, and a pole running down to the hand. Leans into the wind by
    `_CUR_WIND`. Opaque draws (no alpha) so it composites straight onto the deck;
    colour capped under the coin at night."""
    color = _UMBRELLA_COLORS[color_idx % len(_UMBRELLA_COLORS)]
    if night > 0.05:
        color = _cap150(_mix(color, (54, 64, 96), min(0.5, 0.4 * night + 0.15)))
    dark = _shade(color, -46)
    r = max(5, int(8 * scale))
    tilt = int(round(_CUR_WIND * 3.0)) + 1          # lean downwind (rain drives left→ canopy right)
    apex_x = cx + tilt
    cy = int(canopy_y)
    # Dome + scalloped hem as one filled fan.
    canopy = [
        (cx - r, cy),
        (apex_x - int(r * 0.55), cy - int(r * 0.55)),
        (apex_x, cy - r),
        (apex_x + int(r * 0.55), cy - int(r * 0.55)),
        (cx + r, cy),
        (cx + int(r * 0.6), cy + 2),
        (cx, cy + 1),
        (cx - int(r * 0.6), cy + 2),
    ]
    pygame.draw.polygon(surf, color, canopy)
    pygame.draw.polygon(surf, dark, canopy, 1)
    # Ribs from the apex out to the hem scallops, and a top nub.
    pygame.draw.line(surf, dark, (apex_x, cy - r), (cx, cy + 1), 1)
    pygame.draw.line(surf, dark, (apex_x, cy - r), (cx - int(r * 0.6), cy + 2), 1)
    pygame.draw.line(surf, dark, (apex_x, cy - r), (cx + int(r * 0.6), cy + 2), 1)
    pygame.draw.circle(surf, dark, (apex_x, cy - r), 1)
    # Pole down to the hand (slightly off the canopy centre so the figure "holds" it).
    hand_x = cx - 1
    pygame.draw.line(surf, (96, 74, 52), (cx, cy + 1),
                     (hand_x, cy + int(pole_len * scale)), 1)


# A reused bounding-box scratch for the faint catenary wires. Each wire used to
# allocate a full W×H SRCALPHA layer just to draw a single 1px curve (~7/frame);
# a small shared scratch sized to the span's bounds keeps the alpha blend but
# drops the per-wire allocation. Wires draw sequentially, so one buffer serves.
_WIRE_SCRATCH = pygame.Surface((1, 1), pygame.SRCALPHA)


def _wire_scratch(w, h):
    global _WIRE_SCRATCH
    w = max(1, int(w)); h = max(1, int(h))
    sw, sh = _WIRE_SCRATCH.get_size()
    if w > sw or h > sh:
        _WIRE_SCRATCH = pygame.Surface((max(w, sw), max(h, sh)), pygame.SRCALPHA)
    _WIRE_SCRATCH.fill((0, 0, 0, 0), (0, 0, w, h))
    return _WIRE_SCRATCH

_mix = sp._mix
_shade = sp._shade
_clamp = sp._clamp
_nightf = sp._nightf

# The festival's hard luma ceiling. The shared pillar-ornament cap is 153
# (0.60×coin), but the art-director measured a coin reading ~206 with isolated
# promenade lights hitting 255, so the promenade clamps every emitted core/glow
# colour a hair lower at 150 — comfortably under the coin, leaving the gold
# pickup the single brightest object anywhere on the night ground.
NIGHT_GLOW_CAP = 150


def _cap150(color):
    """Clamp each RGB channel to NIGHT_GLOW_CAP so no promenade light can rival
    the coin. Applied to every lit core, bulb and additive-halo colour."""
    return (min(int(color[0]), NIGHT_GLOW_CAP),
            min(int(color[1]), NIGHT_GLOW_CAP),
            min(int(color[2]), NIGHT_GLOW_CAP))


# ── glow gate: one monotonic dusk->night fade-in for the whole festival ───────
#
# r15's _add_lamp_glow only begins above night-ness 0.45 (dead at dusk) while its
# lit bulb FACES snapped to full brightness the instant the sky went dark — so
# dusk blew out (faces near-full, no halo) instead of "lamps just beginning".
# The promenade now drives BOTH the lit-face colour AND the halo from one shared
# intensity curve so the ramp is monotonic: dusk lands at ~45% of night, night
# at 100%, and nothing is lit by day. Every emitted colour is then clamped to
# NIGHT_GLOW_CAP so the coin stays the brightest object.

def _lit_intensity(pal):
    """0 by day, ~0.40 at dusk (lamps JUST beginning to glow), 1.0 at full night.
    Monotonic in night-ness. Drives lit faces and halos in lockstep.

    The dusk floor is held a notch under night so EVERY emitter face is dimmer at
    dusk than at night (per-element, not just on average) — the dusk bulb/lamp
    faces were landing marginally hotter than the full-night set, so the floor was
    pulled from 0.45 to 0.40 (~10% down) while night stays pinned at 1.0."""
    if not sp._is_dark_sky(pal):
        return 0.0
    night = _nightf(pal)
    # Map the dusk night-ness (~0.38) to 0.40 and full night (~1.0) to 1.0 with a
    # gentle floor so the first lit phase reads as "coming on", not dead.
    return 0.40 + 0.60 * max(0.0, min(1.0, (night - 0.38) / 0.62))


def _glow_strength(pal):
    """Halo strength shares the lit-intensity curve (kept as a name for the
    primitives), so a dusk halo is a soft ~45% of the full night bloom."""
    return _lit_intensity(pal)


def _glow(surf, cx, cy, pal, *, radius=14, color=(255, 196, 110), scale=1.0):
    """Capped warm halo with the promenade's monotonic dusk->night curve. The
    halo colour is capped at NIGHT_GLOW_CAP before the peak ratio so even a halo
    landing on a lit face can't sum past the coin."""
    s = _glow_strength(pal)
    if s <= 0.02:
        return
    peak = int(sp._GLOW_PEAK * scale * s)
    if peak <= 1:
        return
    g = sp._warm_glow(radius, _cap150(color), peak)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)


# ── retrofit the borrowed r15 primitives to the 150 cap + dusk ramp ───────────
#
# The lamp posts, lantern garland and fairy lights are r15 helpers that bake in
# the old 153 cap and the dead-at-dusk halo gate. Rather than fork them, the
# promenade rebinds the two seams they share — the night-luma clamp and the halo
# blitter — so every borrowed light obeys NIGHT_GLOW_CAP and the monotonic
# dusk->night intensity. _CUR_PAL is set by each phase painter so the seam funcs
# (which don't receive `pal`) can read the current intensity.

_CUR_PAL = None

# Additive halos sum onto whatever they sit over, so the peak is held LOW and the
# lit faces underneath are capped well below 150 (see _LIT_FACE_CAP) — base-face +
# full halo must still land ≤150 luma so no promenade light can rival the coin.
sp._GLOW_PEAK = 24

# Lit faces (bulbs, lantern panels) are capped here, BELOW NIGHT_GLOW_CAP, so a
# warm additive halo summed on top still clears the 150 ceiling.
_LIT_FACE_CAP = 122


def _capped_clamp_night(color, alpha=255):
    """Replacement for sp._clamp_night: clamp each lit face to _LIT_FACE_CAP (under
    NIGHT_GLOW_CAP, leaving headroom for an additive halo), then pull the face
    toward a dark ember by the dusk ramp so dusk faces are clearly dimmer than
    night faces (no snap-to-bright at first dark)."""
    r, g, b = color[:3]
    lit = (min(int(r), _LIT_FACE_CAP),
           min(int(g), _LIT_FACE_CAP),
           min(int(b), _LIT_FACE_CAP))
    s = _lit_intensity(_CUR_PAL) if _CUR_PAL is not None else 1.0
    # Unlit ember the face fades toward when the lamps are only "coming on".
    ember = (int(lit[0] * 0.42), int(lit[1] * 0.34), int(lit[2] * 0.30))
    out = _mix(ember, lit, s)
    return (out[0], out[1], out[2], alpha)


def _capped_add_glow(surf, cx, cy, pal, *, radius=16, alpha=120, color=(255, 196, 110)):
    """Replacement for sp._add_lamp_glow using the promenade's monotonic intensity
    (alive from dusk) and the 150-capped halo colour."""
    if not sp._is_dark_sky(pal):
        return 0.0
    s = _lit_intensity(pal)
    if s <= 0.02:
        return 0.0
    peak = int(min(sp._GLOW_PEAK, sp._GLOW_PEAK * (alpha / 120.0)) * s)
    if peak <= 1:
        return s
    g = sp._warm_glow(radius, _cap150(color), peak)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)
    return s


sp._clamp_night = _capped_clamp_night
sp._add_lamp_glow = _capped_add_glow


# ── hung STRING lights stay lit all cycle (unlike the dusk-gated lamp posts) ───
#
# The festival lantern garland + fairy lights are strung to read "on" day AND
# night and to cast a gentle warm wash on the promenade. Their lit faces + halos
# follow a daytime FLOOR under the normal dusk->night curve, so they never drop
# dark the way the street lamps (which only kindle at dusk) correctly do. At full
# night the floor is moot (intensity is already 1.0), so the night-cap behaviour
# — capped faces + capped additive halos staying under the coin — is unchanged.
_STRING_DAY_FLOOR = 0.40


def _string_intensity(pal):
    return max(_STRING_DAY_FLOOR, _lit_intensity(pal))


def _string_glow(surf, cx, cy, pal, *, radius=8, alpha=66, color=(255, 196, 110)):
    """A capped warm halo for the always-on string lights — same peak math + 150
    cap as _capped_add_glow, but alive by day (no dark-sky gate) via the string
    floor, so the hung bulbs light the scene a little even in daylight."""
    s = _string_intensity(pal)
    peak = int(min(sp._GLOW_PEAK, sp._GLOW_PEAK * (alpha / 120.0)) * s)
    if peak < 1:
        return
    g = sp._warm_glow(radius, _cap150(color), peak)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)


# ── lighten the festival WIRE so the eye reads "bulbs on a line" ──────────────
#
# The r15 garland rope / fairy wire were dark (≈62,52,44) so at night the strung
# spans read as black scribble crisscrossing the upper band. The promenade draws
# the wire as ONE thin catenary per span lifted toward the sky value (a faint
# semi-transparent line), so only the bulbs carry weight. Both strand drawers are
# re-bound to use this faint-wire variant; only the rope colour changes.

def _faint_wire_color(pal):
    """A single hairline wire tinted toward the night sky so it nearly dissolves —
    the bulbs, not the string, should read."""
    sky = pal.get('sky_top', (60, 120, 200))
    # Lift a dark cord most of the way to the sky value; semi-transparent on top.
    # Pulled one step further toward sky (0.55 -> 0.64) so the whole catenary set
    # reads at one uniform faint value — no single span squiggles darker than the
    # rest where it crosses a darker patch of sky.
    return _mix((60, 54, 50), sky, 0.64)


def _draw_faint_catenary(surf, xl, xr, top_y, sag, steps, pal):
    col = _faint_wire_color(pal)
    pts = [(int(x), int(y)) for x, y in sp._catenary_pts(xl, xr, top_y, sag, steps)]
    ox = min(p[0] for p in pts) - 1
    oy = min(p[1] for p in pts) - 1
    sw = max(p[0] for p in pts) - ox + 2
    sh = max(p[1] for p in pts) - oy + 2
    layer = _wire_scratch(sw, sh)
    pygame.draw.lines(layer, (*col, 150), False,
                      [(x - ox, y - oy) for x, y in pts], 1)
    surf.blit(layer, (ox, oy), (0, 0, sw, sh))


def _garland_faint(surf, w, scroll, pal, *, top_y, period=120, sag=24,
                   per_span=3, colors=('red', 'gold'), span_gate=None):
    """r15 lantern garland with the faint single-catenary wire. The hung lanterns
    stay lit + cast a soft warm halo across the WHOLE cycle (string-light floor,
    not the dusk lamp gate), so the strand never reads 'off'."""
    for xl, xr, k in sp._garland_spans(scroll, w, period, x0=12):
        if span_gate is not None and not span_gate(k):
            continue
        _draw_faint_catenary(surf, xl, xr, top_y, sag, 16, pal)
        for j in range(per_span):
            tt = (j + 0.5) / per_span
            bx, by = sp._span_point(xl, xr, top_y, sag, tt)
            color = colors[j % len(colors)]
            # Halo via _string_glow (alive by day), so suppress the head's own
            # dusk-gated halo to avoid double-counting it at night.
            sp._draw_lantern_head(surf, int(bx), int(by), pal,
                                  color=color, scale=0.6,
                                  glow_radius=7, glow_alpha=0)
            glow_col = (255, 150, 110) if color == 'red' else (255, 205, 120)
            _string_glow(surf, int(bx), int(by) + 5, pal, radius=7, alpha=52,
                         color=glow_col)


def _fairy_faint(surf, w, scroll, pal, *, top_y, period=200, sag=26, per_span=5,
                 span_gate=None):
    """r15 fairy lights with the faint single-catenary wire. The hung bulbs stay
    LIT all cycle (a warm bulb + a capped halo via the string-light floor) instead
    of dropping to dead grey beads by day, so the strand always reads 'on' and
    lights the scene a little."""
    dark = sp._is_dark_sky(pal)
    warm = (250, 200, 120)
    for xl, xr, k in sp._garland_spans(scroll, w, period, x0=8):
        if span_gate is not None and not span_gate(k):
            continue
        _draw_faint_catenary(surf, xl, xr, top_y, sag, 20, pal)
        for j in range(per_span):
            tt = (j + 0.5) / per_span
            bx, by = sp._span_point(xl, xr, top_y, sag, tt)
            bx, by = int(bx), int(by) + 2
            # night: the shipped capped+dusk-ramped warm bulb (night-cap safe);
            # day: a full warm paper-bulb so the strand stays clearly lit.
            face = sp._clamp_night(warm)[:3] if dark else warm
            pygame.draw.circle(surf, _mix(face, (110, 78, 46), 0.4), (bx, by), 3)
            pygame.draw.circle(surf, face, (bx, by), 2)
            _string_glow(surf, bx, by, pal, radius=7, alpha=54, color=warm)


sp._draw_lantern_garland = _garland_faint
sp._draw_fairy_lights = _fairy_faint


# ══════════════════════════════════════════════════════════════════════════
# NEW characters
# ══════════════════════════════════════════════════════════════════════════
#
# All live in the lower promenade band (feet at GROUND_Y) and are kept clear of
# the bird lane (x≈48..188) and the pillar lane (x≈212..320) by their chosen
# world-x anchors. They borrow the _draw_bench_person body idiom so the new
# people match the existing bench couple in scale and palette.


def _retint_person(col, night):
    """Cool a clothing colour toward the night ground band so a new figure sits
    in the same value family as the retinted floor (matches the bench tint)."""
    if night <= 0.05:
        return col
    # A firm floor on the cool so even at dusk a bright skin/cloth face is pulled
    # well under the festival lights; ramps further toward full night.
    return _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))


def _draw_bench_person(surf, x_base, body_y, shirt, shirt_dk, hair, *, night=0.0):
    """A small seated/standing figure, mirroring the live game body idiom but with
    the skin RETINTED at night so a face never reads brighter than 150 luma (the
    live helper hardcodes a (235,195,150) skin that out-shone the cap after dusk)."""
    skin = _retint_person((235, 195, 150), night)
    pygame.draw.rect(surf, shirt, (x_base, body_y, 6, 8))
    pygame.draw.rect(surf, shirt_dk, (x_base, body_y, 6, 8), 1)
    head_y = body_y - 3
    pygame.draw.circle(surf, skin, (x_base + 3, head_y), 3)
    pygame.draw.polygon(surf, hair,
                        [(x_base, head_y), (x_base + 6, head_y),
                         (x_base + 3, head_y - 4)])
    pygame.draw.circle(surf, (30, 20, 15), (x_base + 2, head_y + 1), 0)
    pygame.draw.circle(surf, (30, 20, 15), (x_base + 4, head_y + 1), 0)


def draw_kids(surf, sx, pal, *, t=0.0, n=3, variant=0):
    """`n` small children drawn from the 6-strong 'kid' variety pool (day_cast),
    feet on GROUND_Y. `variant` is a resolved base pool index; each of the n kids
    takes the next pool member (variant, variant+1, …) so a group reads as several
    different children, not one cloned thrice."""
    night = _nightf(pal)
    cnt = _fv.variant_count("kid")
    if not cnt:
        return
    spread = (-13, 9, 26, 40, -28)
    for i in range(n):
        v = _fv.get("kid", (variant + i) % cnt)
        _day.draw_kid(surf, sx + spread[i % len(spread)], GROUND_Y - 1, v, night, t + i * 0.6)


def draw_vendor(surf, sx, pal, *, t=0.0, variant=0):
    """One standing market vendor/worker from the 7-strong 'vendor' pool
    (day_cast), feet on GROUND_Y, centred on `sx`. `variant` is a resolved pool
    index; the near lane passes it as a kwarg so it enters the bake cache key."""
    v = _fv.get("vendor", variant)
    if v is None:
        return
    _day.draw_vendor(surf, sx, GROUND_Y - 1, v, _nightf(pal), t)


def draw_old_man(surf, sx, pal, *, t=0.0, seated_bench=False, variant=0):
    """A TEMPLE ELDER from the 6-strong 'elder' variety pool (day_cast) — varied
    stance (stoop+cane / tai-chi / birdcage / hands-behind / seated+tea / feeding
    birds), feet on GROUND_Y. `variant` is a resolved pool index. The legacy
    seated-on-bench companion pose is kept as a fallback for `seated_bench`."""
    if not seated_bench:
        v = _fv.get("elder", variant)
        if v is not None:
            _day.draw_elder(surf, sx + 3, GROUND_Y - 1, v, _nightf(pal), t)
            return
    night = _nightf(pal)
    skin = _retint_person((222, 186, 148), night)
    # A muted plum/indigo robe — a cool violet that sits apart from the kids'
    # warm primaries and the bench couple's reds, so the elder owns his own hue.
    robe = _retint_person((92, 72, 108), night)
    robe_dk = _retint_person((58, 44, 74), night)
    grey = _retint_person((212, 210, 202), night)      # grey hair/beard, near-white
    cane_c = _retint_person((118, 80, 48), night)

    feet_y = GROUND_Y - 1
    # A TALLER robe block than the adults so the stoop has room to curve, and a
    # wider hem so the bent-over posture reads as a heavy robe, not a thin coat.
    body_h = 11 if not seated_bench else 9
    body_w = 7
    body_y = feet_y - body_h - (2 if not seated_bench else 0)
    # PRONOUNCED forward stoop: the shoulders lean a full 3-4px over the feet so
    # the silhouette is a clear hunched curve, the universal "elder" read.
    lean = 4 if not seated_bench else 2
    # Robe as a bent-over wedge: narrow stooped shoulders up front, broad hem.
    pygame.draw.polygon(surf, robe, [
        (sx + lean, body_y + 2), (sx + body_w + lean - 1, body_y),
        (sx + body_w + 1, body_y + body_h), (sx - 1, body_y + body_h)])
    pygame.draw.polygon(surf, robe_dk, [
        (sx + lean, body_y + 2), (sx + body_w + lean - 1, body_y),
        (sx + body_w + 1, body_y + body_h), (sx - 1, body_y + body_h)], 1)
    # A hunched upper-back hump where the stoop bends — extra elder cue.
    pygame.draw.circle(surf, robe_dk, (sx + 1, body_y + 2), 2)
    # Head tipped forward over the stoop. BALD/grey dome (a thin grey skull-cap of
    # hair, no peak) so it can never read as a kid's conical hat.
    hx, hy = sx + body_w // 2 + lean, body_y - 2
    pygame.draw.circle(surf, skin, (hx, hy), 3)
    # Domed grey hair fringe — a flat semicircle hugging the skull, not a cone.
    pygame.draw.arc(surf, grey, (hx - 3, hy - 4, 7, 7),
                    math.radians(0), math.radians(180), 2)
    # LONG wispy beard — a tapering grey wedge reaching well down the chest, the
    # clearest temple-elder cue at 1×.
    pygame.draw.polygon(surf, grey, [
        (hx - 2, hy + 2), (hx + 2, hy + 2), (hx + 1, hy + 8), (hx - 1, hy + 8)])
    pygame.draw.circle(surf, _shade(grey, -30), (hx, hy + 6), 1)  # beard tip wisp
    pygame.draw.circle(surf, (30, 20, 15), (hx, hy), 0)
    # The CANE — drawn for both standing and seated so the elder always carries
    # it. A long shaft from the leading hand all the way DOWN to the deck plus a
    # clear hooked crook, so the silhouette plainly says "old man with a cane".
    tap = int(round(math.sin(t * 1.3) * 1)) if not seated_bench else 0
    cx0 = sx + body_w + lean + 2
    hand_y = body_y + 3
    pygame.draw.line(surf, cane_c, (cx0, hand_y), (cx0 + tap, feet_y), 2)
    # Hooked crook curling back toward the hand.
    pygame.draw.line(surf, cane_c, (cx0, hand_y), (cx0 - 3, hand_y), 2)
    pygame.draw.line(surf, cane_c, (cx0 - 3, hand_y), (cx0 - 3, hand_y + 2), 2)
    if not seated_bench:
        # Two robe-hem feet shuffling.
        pygame.draw.line(surf, robe_dk, (sx + 1, body_y + body_h),
                         (sx + 1, feet_y), 1)
        pygame.draw.line(surf, robe_dk, (sx + body_w - 1, body_y + body_h),
                         (sx + body_w - 1 + tap, feet_y), 1)


def draw_flock(surf, sx, pal, *, t=0.0, n=3):
    """A grazing flock of WOOLLY sheep. The live _SheepPack sprite reads at 1× as
    a small dark-headed blob on thin tall legs — ambiguous, almost a bird on a
    post. These are unmistakably sheep: each body is a fat rounded woolly OVAL
    (clearly wider than tall) with a bumpy fleece top, SHORT stubby legs, and one
    dark head bump at the front. A trailing lamb closes the group."""
    night = _nightf(pal)
    wool = _retint_person((238, 234, 226), night)
    wool_sh = _retint_person((205, 198, 188), night)
    wool_hi = _retint_person((250, 248, 244), night)
    face = _retint_person((70, 62, 60), night)         # dark head + legs
    spread = (-26, -6, 16, 32)   # 3 ewes + a trailing lamb
    for i in range(n + 1):
        adult = i < n
        dx = spread[i]
        bw = 16 if adult else 11        # body WIDER than tall -> reads woolly
        bh = 9 if adult else 6
        bx = sx + dx
        # A gentle grazing bob so the still frame still feels alive.
        bob = int(round(max(0.0, math.sin(t * 2.0 + i * 1.3)) * 1.0))
        feet_y = GROUND_Y - 1
        body_y = feet_y - bh - 2 - bob
        # SHORT stubby legs (2px) — not the thin tall posts that read as a bird perch.
        for lx in (bx + 3, bx + bw - 4):
            pygame.draw.line(surf, face, (lx, body_y + bh - 1), (lx, feet_y), 1)
        # Fat woolly body oval.
        pygame.draw.ellipse(surf, wool_sh, (bx, body_y, bw, bh))
        pygame.draw.ellipse(surf, wool, (bx, body_y, bw, bh - 1))
        # Bumpy fleece across the top so it clearly reads as wool, not a smooth egg.
        br = 2
        cx = bx + br + 1
        while cx <= bx + bw - br - 1:
            pygame.draw.circle(surf, wool_hi, (cx, body_y + br), br)
            cx += br + 1
        # One clear DARK head bump at the front (right) — the "this is a sheep" cue.
        hx = bx + bw - 1
        pygame.draw.circle(surf, face, (hx, body_y + 2), 3 if adult else 2)
        pygame.draw.circle(surf, _shade(face, 18), (hx + 1, body_y + 1), 1)  # ear/snout nub


def draw_strollers(surf, sx, pal, *, t=0.0, umbrella=None, variant=0):
    """Draw ONE adult pedestrian from the 50-strong variety pool (ped_cast),
    feet on GROUND_Y, centred on `sx`. `variant` is a resolved pool index; the
    near lane passes it as a kwarg so it enters the bake cache key. Umbrella/hood/
    coat looks now come from weather-weighted pool variants, so the old `umbrella`
    flag is accepted only for signature compatibility and ignored."""
    v = _fv.get("pedestrian", variant)
    if v is None:
        return
    _ped._draw_one(surf, sx, GROUND_Y - 1, pal, v, _nightf(pal), t)


def _shelter_figures(surf, w, scroll, pal, t):
    """A few people standing huddled under umbrellas at stable world slots, shown
    only once the open deck has emptied (heavy rain / real snow) — so the street
    still feels lived-in at the storm's worst instead of dead. Sparse + world-
    anchored (a fixed per-slot hash admits ~1 in 4), so they scroll past without
    flicker and pop in/out only as the weather crosses the threshold."""
    sev = max(_CUR_RAIN, _CUR_SNOW)
    if sev < 0.45:
        return
    night = _nightf(pal)
    for sx, k in sp._world_xs(scroll, w, 250, x0=30, mult=sp.GROUND_MULT, margin=40):
        h = (k * 0x9E3779B1) & 0xFFFFFFFF
        if (h & 3) != 0:                       # ~1 in 4 slots is occupied
            continue
        bx = sx + 6 + (h >> 4 & 7)
        base = (78 + (h >> 6 & 63), 84 + (h >> 9 & 55), 108 + (h >> 12 & 47))
        shirt = _retint_person(base, night)
        shirt_dk = _shade(shirt, -34)
        hair = _retint_person((60, 45, 38), night)
        # Standing still (sheltering) — no gait, feet planted on the kerb.
        body_y = GROUND_Y - 1 - 8 - 3
        def _figure(s, bx=bx, body_y=body_y, shirt=shirt, shirt_dk=shirt_dk,
                    hair=hair, h=h):
            _draw_bench_person(s, bx, body_y, shirt, shirt_dk, hair, night=night)
            _draw_umbrella(s, bx + 3, body_y - 6, (h >> 2), night=night)
        _zbuf.enqueue(GROUND_Y - 1, TB_CAST, _figure)


# ── KIOSK / vendor stall: a pagoda-roofed market stall ───────────────────────
#
# Net-new. A small temple-market stall: a tiered curved pagoda roof, a striped
# awning, a counter with goods, a hanging paper lantern, and (optionally) a tiny
# vendor head behind the counter. World-anchored on the sidewalk at GROUND_Y,
# kept narrow so it slots into a clear strip without crowding the bird/pillar
# lanes. Its "open-ness" escalates: shutter down by day, goods + awning by
# golden, the lantern lit at dusk/night.

def _pagoda_roof(surf, cx, ridge_y, half_w, pal, *, tiers=2):
    """A tiered, upswept temple roof. Each tier is a low trapezoid with curled
    eave tips drawn as short up-flicks, in the stage stone tones so it belongs to
    the pagoda pillar's masonry family."""
    night = _nightf(pal)
    tile = _mix(pal.get('stone_dark', (95, 80, 70)), (120, 96, 78), 0.5)
    tile = _mix(tile, (54, 60, 86), 0.32 * night)
    tile_lt = _shade(tile, 18)
    ridge = _shade(tile, -22)
    y = ridge_y
    hw = half_w
    for ti in range(tiers):
        eave_y = y + 7
        # Roof slab as a trapezoid wider at the eave.
        pygame.draw.polygon(surf, tile, [
            (cx - hw * 0.4, y), (cx + hw * 0.4, y),
            (cx + hw, eave_y), (cx - hw, eave_y)])
        pygame.draw.line(surf, tile_lt, (cx - hw * 0.4, y), (cx + hw * 0.4, y), 1)
        # Upswept eave tips (the temple curl).
        pygame.draw.line(surf, ridge, (cx - hw, eave_y), (cx - hw - 2, eave_y - 3), 2)
        pygame.draw.line(surf, ridge, (cx + hw, eave_y), (cx + hw + 2, eave_y - 3), 2)
        y = eave_y - 1
        hw = int(hw * 0.78)
    # A small finial knob on the ridge.
    pygame.draw.circle(surf, _shade(tile_lt, 10), (int(cx), int(ridge_y - 2)), 1)


def draw_kiosk(surf, sx, pal, *, t=0.0, openness=1.0):
    """A pagoda-roofed vendor stall on the sidewalk. `openness` 0..1 escalates
    the read: 0 -> just opening (low shutter, no goods), 1 -> fully open (awning
    out, goods on the counter, a vendor, a lit hanging lantern at night)."""
    night = _nightf(pal)
    base_y = GROUND_Y - 1
    half_w = 22
    counter_h = 16
    post_top = base_y - 34   # counter + a head-height opening under the roof

    # Two corner posts (timber).
    post = _mix((92, 64, 40), (60, 66, 92), 0.30 * night)
    post_dk = _shade(post, -20)
    for px in (sx - half_w + 3, sx + half_w - 3):
        pygame.draw.rect(surf, post, (px - 1, post_top, 3, base_y - post_top))
        pygame.draw.line(surf, post_dk, (px + 1, post_top), (px + 1, base_y), 1)

    # Back wall panel between posts (so the stall reads as enclosed, not a frame).
    wall = _mix(pal.get('stone_mid', (150, 132, 110)), (150, 124, 96), 0.5)
    wall = _mix(wall, (56, 62, 88), 0.32 * night)
    pygame.draw.rect(surf, _shade(wall, -10),
                     (sx - half_w + 4, post_top + 2, (half_w - 4) * 2, 14))

    # The pagoda roof crowning the posts.
    _pagoda_roof(surf, sx, post_top - 8, half_w + 2, pal, tiers=2)

    # Counter / shop front.
    counter = _mix((120, 84, 52), (60, 66, 92), 0.30 * night)
    counter_lt = _shade(counter, 16)
    cy = base_y - counter_h
    pygame.draw.rect(surf, counter, (sx - half_w + 1, cy, (half_w - 1) * 2, counter_h))
    pygame.draw.rect(surf, counter_lt, (sx - half_w + 1, cy, (half_w - 1) * 2, 2))
    pygame.draw.rect(surf, _shade(counter, -22),
                     (sx - half_w + 1, base_y - 4, (half_w - 1) * 2, 4))

    if openness > 0.25:
        # A striped awning rolled out over the counter (the "open for business"
        # cue). Two-tone scalloped valance.
        aw = half_w + 1
        ay = cy - 5
        # The cream stripe is pulled HARD toward the night ground from dusk on so
        # the unlit awning never reads brighter than the festival lights or coin.
        dimk = min(0.72, 1.3 * night)
        stripe_a = _mix((210, 70, 60), (70, 70, 96), min(0.6, 0.9 * night))
        stripe_b = _mix((240, 228, 210), (74, 80, 104), dimk)
        for i, ax in enumerate(range(sx - aw, sx + aw, 6)):
            col = stripe_a if i % 2 == 0 else stripe_b
            pygame.draw.polygon(surf, col, [
                (ax, ay), (ax + 6, ay), (ax + 6, ay + 4), (ax + 3, ay + 6), (ax, ay + 4)])

    if openness > 0.5:
        # Goods on the counter — a few coloured produce/jar lumps so it reads as
        # a market stall, not an empty booth.
        goods = [((230, 120, 60), 3), ((90, 160, 90), 2), ((220, 200, 90), 3),
                 ((200, 80, 90), 2)]
        gx = sx - half_w + 6
        for col, r in goods:
            col = _mix(col, (58, 66, 96), min(0.6, 0.85 * night))
            pygame.draw.circle(surf, _shade(col, -16), (gx, cy - 1), r)
            pygame.draw.circle(surf, col, (gx, cy - 2), r - 1)
            gx += r + 5
        # A tiny vendor head peeking over the counter behind the goods.
        vx = sx + half_w - 9
        skin = _retint_person((226, 190, 150), night)
        pygame.draw.circle(surf, skin, (vx, cy - 4), 3)
        pygame.draw.polygon(surf, _retint_person((70, 50, 40), night),
                            [(vx - 3, cy - 4), (vx + 3, cy - 4), (vx, cy - 8)])

    # A hanging paper lantern under the eave — lit (capped) once the sky darkens.
    lx = sx + half_w - 7
    ly = post_top - 1
    # Drive the WHOLE lantern (dark shell + lit face) off the shared dusk->night
    # intensity so the kiosk lantern is strictly dimmer at dusk than at night,
    # per-element — the dark shell no longer brightens as the sky lightens.
    s = _lit_intensity(pal)
    lan_dark = _mix((96, 28, 28), (150, 38, 38), s)
    lan_lit = (sp._clamp_night((250, 110, 80))[:3] if sp._is_dark_sky(pal)
               else (210, 110, 80))
    pygame.draw.line(surf, (50, 35, 25), (lx, ly), (lx, ly + 4), 1)
    body = pygame.Rect(lx - 4, ly + 4, 8, 10)
    pygame.draw.ellipse(surf, lan_dark, body)
    pygame.draw.ellipse(surf, lan_lit, body.inflate(-3, -2))
    _glow(surf, lx, ly + 9, pal, radius=10, color=(255, 150, 110), scale=0.7)


# ── capped campfire + capped napper Z's ───────────────────────────────────────
#
# The live _Campfire and _Napper paint pure-white hot pixels (flame tip
# (255,250,220), sparks (255,240,200), sleep-"z" (215,215,235)) that blew past
# the coin at night. They live in game/ and must not be edited, so the promenade
# reuses their cached tent/logs/halo geometry but repaints the LIT parts with a
# warm amber core and capped sparks of its own, and draws its own dimmed Z's.

import game.ambient as _amb

# A warm amber spark palette in place of the live white-ish set; kept dim so even
# an additive spark summed over the warm halo + floor stays under the 150 ceiling.
_CAMP_SPARKS = ((92, 60, 26), (92, 70, 32), (84, 52, 24))


def draw_campfire(surf, sx, pal, *, t=0.0):
    """A world-anchored campfire matching the live one's silhouette, but with a
    warm amber (capped) core instead of a white-hot centre and amber sparks, so
    no fire pixel exceeds NIGHT_GLOW_CAP and the coin stays brightest."""
    x = sx
    y = GROUND_Y - 24
    s = _lit_intensity(pal)
    # Cached tent + logs (unlit geometry) and the warm radial halo. The halo is
    # scaled DOWN hard (and by the dusk->night intensity) so that even where it
    # sums onto the solid amber flame the total stays ≤150 luma — additive light
    # cannot push the fire past the coin.
    if s > 0.02:
        halo = _amb._build_campfire_halo().copy()
        k = int(255 * 0.12 * s)
        halo.fill((k, k, k, 255), special_flags=pygame.BLEND_RGBA_MULT)
        hr = _amb._CAMPFIRE_HALO_RADIUS
        surf.blit(halo, (x - hr, y - 4 - hr), special_flags=pygame.BLEND_RGB_ADD)
    solid = _amb._get_campfire_solid()
    surf.blit(solid, (x - _amb._CAMP_FIRE_LX, y - _amb._CAMP_FIRE_LY))
    # Amber flame — warm amber core, NOT the live white tip. Channels kept low so
    # base flame + the (already small) additive halo above stays under 150 luma.
    flicker = (math.sin(t * 12.0) * 0.5 + math.sin(t * 7.5 * 1.3) * 0.5)
    h_off = int(round(flicker * 1.5))
    amber_lo = (110, 48, 26)
    amber_mid = (128, 72, 36)
    amber_hi = (138, 96, 46)   # warm amber core (luma ≈101), never white
    pygame.draw.ellipse(surf, amber_lo, (x - 5, y - 7 - h_off, 10, 8 + h_off))
    pygame.draw.ellipse(surf, amber_mid, (x - 4, y - 8 - h_off, 8, 8 + h_off))
    pygame.draw.ellipse(surf, amber_hi, (x - 2, y - 8 - h_off, 5, 7 + h_off))
    pygame.draw.ellipse(surf, amber_hi, (x - 1, y - 6 - h_off, 3, 4 + h_off))
    # Amber sparks rising — capped and started ABOVE the flame tip so an additive
    # spark never sums onto the solid flame core (which would blow the cap).
    for i in range(6):
        ph = (t * 0.9 + i * 0.37) % 1.0
        spx = x + int(math.sin(i * 1.7 + t) * 6)
        spy = y - 12 - int(ph * 20)   # origin above the flame, rising into dark sky
        a = int(120 * (1.0 - ph) * max(0.2, s))
        if a > 6:
            layer = pygame.Surface((2, 2), pygame.SRCALPHA)
            layer.fill((*_CAMP_SPARKS[i % 3], a))
            surf.blit(layer, (spx, spy), special_flags=pygame.BLEND_RGB_ADD)


def draw_napper(surf, sx, pal, *, t=0.0):
    """The live napper sprite (a sleeping figure on a mat) plus dimmed, warm-grey
    sleep-Z's. The live Z colour (215,215,235) is a near-white that blew the dusk
    luma cap, so the promenade redraws the Z's at <=150 luma in a cool grey that
    matches the night ground rather than glowing."""
    night = _nightf(pal)
    obj = _stepped(_Napper, pal, 24, sx)
    breath = math.sin(t * 1.0)
    # Cool the cached napper sprite toward night so its hardcoded bright skin
    # (235,195,150) doesn't out-shine the dressing once the sky darkens.
    if night > 0.05 and obj._sprite is not None:
        obj._sprite = obj._sprite.copy()
        k = int(255 * (1 - 0.42 * night))
        kb = int(255 * (1 - 0.30 * night))
        obj._sprite.fill((k, k, kb, 255), special_flags=pygame.BLEND_RGBA_MULT)
    obj._blit_sprite(surf, y_off=-max(0, int(round(breath * 1.2))))
    # Two dimmed Z's rising + fading; capped so no pixel exceeds NIGHT_GLOW_CAP.
    zc = _cap150((150, 150, 150))
    for i in range(2):
        cycle = ((t * 0.45) + i * 0.55) % 1.0
        zy = GROUND_Y - 14 - int(cycle * 16)
        zx = int(sx) - 4 + i * 5 + int(math.sin(cycle * math.pi * 2) * 1)
        a = int(170 * (1.0 - cycle))
        if a <= 8:
            continue
        layer = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.line(layer, (*zc, a), (0, 0), (3, 0), 1)
        pygame.draw.line(layer, (*zc, a), (3, 0), (0, 3), 1)
        pygame.draw.line(layer, (*zc, a), (0, 3), (3, 3), 1)
        surf.blit(layer, (zx, zy))


# ── bring the literal glow cap home on the cream pillar's BASE trim ───────────
#
# The pillar art (painted into the scene before any phase painter runs) carries
# two warm highlights at its foot that read brighter than the 150 ceiling — a
# small gold base sill (~rgb 255,230,100, luma 223) and a doorway-shrine trim
# band (~rgb 208,187,131, luma 187). The pillar itself is praised and must NOT be
# dulled, so this clamp touches ONLY the two narrow foot bands: any over-cap pixel
# there is pulled DOWN to NIGHT_GLOW_CAP luma while keeping its hue, so the coin
# stays the single brightest object even at the frame edge. The pillar body and
# its lit niches higher up are untouched.

# (x0, x1, y0, y1) — the cream pillar's FOOT, where its gold base sill and the
# golden doorway-shrine trim band carry warm highlights that ran past 150 luma.
# The tower's praised silhouette and lit niches live higher up (y < ~530) and are
# left untouched; only the ground-level foot trim (which sits closest to the coin)
# is clamped, so the coin stays the single brightest object even at the corner.
_TRIM_BANDS = (
    (244, 302, 530, GROUND_Y),
)


def _clamp_pillar_base_trim(surf, pal=None, cap=NIGHT_GLOW_CAP):
    """Pull any pillar-foot trim pixel above `cap` luma down to it, hue-preserved,
    so no static masonry highlight competes with the gold coin. Gated to a dark
    sky — by day the foot is legitimately lit stone and is left alone; the cap is
    a NIGHT contract, so only dusk/night foot trim is brought home."""
    if pal is not None and not sp._is_dark_sky(pal):
        return
    for x0, x1, y0, y1 in _TRIM_BANDS:
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                r, g, b, a = surf.get_at((xx, yy))
                lum = 0.299 * r + 0.587 * g + 0.114 * b
                if lum > cap:
                    k = cap / lum
                    surf.set_at((xx, yy), (int(r * k), int(g * k), int(b * k), a))


# ══════════════════════════════════════════════════════════════════════════
# Phase events — each recombines dressing layers + a living cast. Painters take
# (surf, w, gy, h, scroll, pal, t) so the characters can show a gait frame.
# ══════════════════════════════════════════════════════════════════════════
#
# Anchor strategy: the cream pillar sits at the right (base x≈244); the bird
# flies at x≈90. Static dressing uses r15's lane gates. Characters are placed by
# their own clear-zone anchors in the lower band — most live left of the bird
# lane (far left, x<46) or in the mid promenade gap (x≈150..200), never on the
# bird column or the pillar base.

# Character clear zones in the lower band. The bird-lane character ban is a touch
# narrower than the tall-prop ban (characters are short and sit below the bird),
# but we still keep their CENTRES out of x≈70..110 and the pillar base.
def _char_x_ok(sx, half=14):
    if 70 - half < sx < 116 + half:        # bird column
        return False
    if 222 - half < sx < 312 + half:       # pillar base
        return False
    return True


# Cached borrowed-ambient characters: rebuilt only when the biome bucket changes
# (so they retint), pinned to screen-x, and animated from the live clock. The
# pristine sprite is restored each frame so callers that tint it (draw_napper)
# don't compound the tint. `frames` is vestigial (kept for the call sites).
_CHAR_CACHE: dict = {}
_CUR_BUCKET = 0
_CUR_T = 0.0

def _stepped(cls, pal, frames, x, *, rng_seed=7):
    ent = _CHAR_CACHE.get(cls)
    if ent is None or ent[1] != _CUR_BUCKET:
        obj = cls(pal, random.Random(rng_seed))
        pristine = obj._sprite.copy() if getattr(obj, "_sprite", None) is not None else None
        ent = [obj, _CUR_BUCKET, pristine]
        _CHAR_CACHE[cls] = ent
    obj, _bk, pristine = ent
    if pristine is not None:
        obj._sprite = pristine.copy()
    obj.x = float(x)
    obj.t = float(_CUR_T)
    return obj


def _ground_furniture(surf, w, scroll, pal, fd=1.0):
    """World-anchored ground FIXTURES — a barrel, a cairn, a planter trailing a
    cascading vine, and a sparse bamboo planter. Part of the street, not the crowd:
    FIXED spacing so they stay pinned to the sidewalk and scroll at world speed.
    `fd` is the furniture density: each lane is thinned by a STABLE per-slot gate
    (keyed to the world slot, not t/scroll) so the deck reads scattered, never a
    wall — yet stays present from t=0 and never flickers. Wide periods + the gate
    keep the average scene open. Clears the bird column; drawn behind the cast."""
    # Each lane's inclusion is latched at entry (off-screen) so a fixture never
    # blinks out in view when `fd` dips — it scrolls in and out like the deck it
    # sits on.
    fy = GROUND_Y - 1
    for sx, k in sp._world_xs(scroll, w, 440, x0=14):
        if sp._slot_latch(('furn', 11), k, lambda k=k: _slot_on(k, 11, fd)):
            _zbuf.enqueue(fy, TB_FIXTURE,
                          lambda s, sx=sx: sp._draw_barrel(s, sx, pal))
    sp._latch_prune(('furn', 11))
    for sx, k in sp._world_xs(scroll, w, 440, x0=118):
        if sp._slot_latch(('furn', 12), k, lambda k=k: _slot_on(k, 12, fd)):
            _zbuf.enqueue(fy, TB_FIXTURE,
                          lambda s, sx=sx: sp._draw_cairn(s, sx, pal, scale=1.2))
    sp._latch_prune(('furn', 12))
    # Greenery as static cluster beds — one row of planting beds (see
    # _draw_greenery_cluster). A wide period + the stable per-slot gate leave open
    # stretches between beds so the planted street breathes rather than walling up.
    for sx, k in sp._world_xs(scroll, w, 330, x0=70):
        if sp._slot_latch(('furn', 13), k, lambda k=k: _slot_on(k, 13, fd)):
            _zbuf.enqueue(fy, TB_FIXTURE,
                          lambda s, sx=sx, k=k: _draw_greenery_cluster(s, sx, pal, k))
    sp._latch_prune(('furn', 13))
    for sx, k in sp._world_xs(scroll, w, 700, x0=330):
        on, dv = sp._slot_latch(('furn', 15), k, lambda k=k: (
            _slot_on(k, 15, fd), _prop_latch('prop_dress', k, 15)))
        if on:
            _zbuf.enqueue(fy, TB_FIXTURE,
                          lambda s, sx=sx, dv=dv: draw_prop_dress(s, sx, pal, t=_CUR_T, variant=dv))
    sp._latch_prune(('furn', 15))


# ── grouped scenarios ─────────────────────────────────────────────────────────
#
# Coherent little scenes placed at world-x slots: the bird passes one, then open
# road, then the next. Each scene's contents are seeded by its slot index `k`
# (NOT by `scroll`), so a scene is identical frame-to-frame as it scrolls past —
# world-anchored, no flicker (same idiom as the mountain-ornament fix). Members
# animate in place from the live clock `t`; positions ride the scroll.

_SCENARIO_PERIOD = 640          # world-px between scene SLOTS -> lots of open road;
                                # most calm slots are also empty (density gate), so a
                                # vignette is an occasional event, not a metronome.
_SCENE_MARGIN = 220             # wide enough to slide a whole scene in/out smoothly

# ── re-themed cast + hero beats (Chinese market) ──────────────────────────────

def draw_wish_tree(surf, sx, pal, *, t=0.0):
    """A potted WISH-TREE hung with red prayer ribbons — the market's answer to the
    old European wishing well. Gnarled trunk + a tiered canopy in a glazed pot, with
    fluttering red wish-cards; a couple catch a capped warm glint once the sky darks."""
    night = _nightf(pal)
    feet = GROUND_Y - 1
    pot = _mix((150, 96, 70), (60, 70, 100), 0.34 * night)
    pygame.draw.rect(surf, _shade(pot, -20), (sx - 8, feet - 8, 16, 8))
    pygame.draw.rect(surf, pot, (sx - 7, feet - 8, 14, 6))
    pygame.draw.rect(surf, _shade(pot, 18), (sx - 7, feet - 8, 14, 1))
    trunk = _mix((96, 66, 42), (60, 66, 92), 0.30 * night)
    ty0 = feet - 8
    pygame.draw.line(surf, trunk, (sx, ty0), (sx - 1, ty0 - 9), 2)
    pygame.draw.line(surf, trunk, (sx - 1, ty0 - 9), (sx + 1, ty0 - 18), 2)
    fol = _mix((72, 122, 72), (44, 60, 92), 0.42 * night)
    fol_d = _shade(fol, -16)
    cy = ty0 - 22
    for ox, oy, r in ((-6, 4, 6), (6, 4, 6), (0, -2, 8), (0, 6, 7)):
        pygame.draw.circle(surf, fol_d, (sx + ox, cy + oy + 1), r)
        pygame.draw.circle(surf, fol, (sx + ox, cy + oy), r)
    pygame.draw.circle(surf, _shade(fol, 14), (sx - 2, cy - 3), 2)
    rib = _mix((210, 60, 56), (70, 64, 96), 0.40 * night)
    rib_l = _shade(rib, 22)
    for i, (rx, ry) in enumerate(((-7, -2), (5, 0), (-2, 8), (8, 6), (-9, 6))):
        flut = int(round(math.sin(t * 2.2 + i * 1.4) * 1.5))
        x = sx + rx
        y0 = cy + ry
        pygame.draw.line(surf, rib, (x, y0), (x + flut, y0 + 6), 2)
        pygame.draw.line(surf, rib_l, (x, y0), (x + flut, y0 + 2), 1)
    if night > 0.5:
        _glow(surf, sx, cy + 2, pal, radius=11, color=(230, 120, 90), scale=0.5)


def draw_birdcage_stand(surf, sx, pal, *, t=0.0):
    """A market SONGBIRD CAGE on a tall stand — the Chinese-market replacement for
    the grazing flock. A domed bamboo cage with a hopping finch sways gently; a seed
    dish sits at the foot."""
    night = _nightf(pal)
    feet = GROUND_Y - 1
    sway = math.sin(t * 1.6) * 1.0
    pole = _mix((110, 78, 46), (60, 66, 92), 0.30 * night)
    pygame.draw.line(surf, pole, (sx, feet), (sx, feet - 20), 2)
    pygame.draw.line(surf, _shade(pole, -18), (sx + 1, feet), (sx + 1, feet - 20), 1)
    pygame.draw.rect(surf, _shade(pole, -10), (sx - 4, feet - 2, 8, 2))
    cgx = sx + int(round(sway))
    cgy = feet - 32
    bar = _mix((188, 168, 116), (60, 70, 100), 0.42 * night)
    bar_d = _shade(bar, -26)
    pygame.draw.line(surf, pole, (sx, feet - 20), (cgx, cgy + 3), 1)
    pygame.draw.arc(surf, bar, (cgx - 7, cgy, 14, 9), 0.0, math.pi, 2)
    body = pygame.Rect(cgx - 7, cgy + 4, 14, 13)
    pygame.draw.rect(surf, _mix((205, 188, 150), (58, 66, 96), 0.45 * night), body)
    pygame.draw.rect(surf, bar_d, body, 1)
    for bxv in range(cgx - 5, cgx + 6, 3):
        pygame.draw.line(surf, bar_d, (bxv, cgy + 4), (bxv, cgy + 16), 1)
    pygame.draw.line(surf, bar_d, (cgx - 7, cgy + 10), (cgx + 6, cgy + 10), 1)
    hop = int(round(max(0.0, math.sin(t * 5.0)) * 2))
    bird = _retint_person((240, 180, 70), night)
    by = cgy + 14 - hop
    pygame.draw.circle(surf, bird, (cgx, by), 2)
    pygame.draw.circle(surf, _shade(bird, -20), (cgx + 1, by + 1), 1)
    pygame.draw.circle(surf, (40, 30, 20), (cgx + 1, by - 1), 0)
    pygame.draw.ellipse(surf, _mix((150, 140, 120), (60, 70, 100), 0.40 * night),
                        (sx - 5, feet - 3, 10, 3))


def draw_lamplighter(surf, sx, pal, *, t=0.0):
    """A LAMPLIGHTER reaching a long pole up to a street lantern, kindling it at
    dusk — the 'lights coming on' beat. The pole tip carries a capped flame; the
    lantern above blooms a capped warm glow once touched."""
    night = _nightf(pal)
    feet = GROUND_Y - 1
    coat = _retint_person((124, 92, 152), night)
    coat_d = _shade(coat, -18)
    hair = _retint_person((60, 45, 35), night)
    body_y = feet - 11
    _draw_bench_person(surf, sx, body_y, coat, coat_d, hair, night=night)
    leg = _shade(coat_d, -14)
    pygame.draw.line(surf, leg, (sx + 1, body_y + 8), (sx, feet), 1)
    pygame.draw.line(surf, leg, (sx + 4, body_y + 8), (sx + 6, feet), 1)
    px0, py0 = sx + 5, body_y + 1
    px1, py1 = sx + 16, body_y - 16
    pygame.draw.line(surf, _mix((110, 80, 50), (60, 66, 92), 0.30 * night),
                     (px0, py0), (px1, py1), 1)
    flick = int(round(math.sin(t * 8.0)))
    pygame.draw.circle(surf, sp._clamp_night((250, 170, 90))[:3], (px1, py1 - 1 + flick), 1)
    lan = pygame.Rect(px1 - 3, py1 - 9, 7, 8)
    pygame.draw.ellipse(surf, _mix((150, 40, 40), (150, 38, 38), 0.5), lan)
    lit = (sp._clamp_night((250, 120, 90))[:3] if sp._is_dark_sky(pal) else (220, 120, 90))
    pygame.draw.ellipse(surf, lit, lan.inflate(-2, -2))
    _glow(surf, px1, py1 - 5, pal, radius=10, color=(255, 160, 110), scale=0.6)


def draw_market_setup(surf, sx, pal, *, t=0.0):
    """DAWN MARKET SET-UP — stacked produce crates and a vendor hoisting a basket
    overhead as the stalls are raised. The 'morning assembly' beat that opens the day."""
    night = _nightf(pal)
    feet = GROUND_Y - 1
    crate = _mix((150, 110, 66), (60, 70, 100), 0.34 * night)
    for cx, cy, w, h in ((-2, 0, 12, 8), (11, 0, 9, 6), (4, 8, 10, 7)):
        r = pygame.Rect(sx + cx, feet - cy - h, w, h)
        pygame.draw.rect(surf, _shade(crate, -16), r)
        pygame.draw.rect(surf, crate, r.inflate(-2, -2))
        pygame.draw.line(surf, _shade(crate, -24),
                         (r.left, r.centery), (r.right, r.centery), 1)
    shirt = _retint_person((90, 140, 120), night)
    shirt_d = _shade(shirt, -16)
    hair = _retint_person((50, 40, 30), night)
    vx = sx + 24
    body_y = feet - 11
    _draw_bench_person(surf, vx, body_y, shirt, shirt_d, hair, night=night)
    lift = int(round(max(0.0, math.sin(t * 2.0)) * 1))
    bk = _mix((160, 120, 70), (60, 70, 100), 0.34 * night)
    by = body_y - 6 - lift
    pygame.draw.ellipse(surf, _shade(bk, -14), (vx, by, 10, 5))
    pygame.draw.ellipse(surf, bk, (vx + 1, by, 8, 4))
    pygame.draw.line(surf, shirt_d, (vx + 2, body_y + 1), (vx + 1, by + 3), 1)
    pygame.draw.line(surf, shirt_d, (vx + 5, body_y + 1), (vx + 8, by + 3), 1)
    leg = _shade(shirt_d, -12)
    pygame.draw.line(surf, leg, (vx + 1, body_y + 8), (vx + 1, feet), 1)
    pygame.draw.line(surf, leg, (vx + 4, body_y + 8), (vx + 5, feet), 1)


# Each scene EMITS its sub-objects into the depth buffer (emit(tier, fn)) instead
# of painting directly, so a free-standing figure (CAST) sorts in front of a fixed
# back-structure (STRUCTURE) on the same ground line — fixing e.g. a kid drawn
# behind its own kiosk. `emit` fixes the far-lane feet line; tier breaks the tie.

def _scene_market(emit, bx, pal, t, rng, pick=None):
    """Food/market stall with a vendor working it, a songbird-cage stand and kids."""
    vv = pick('vendor', 31) if pick else 0
    kv = pick('kid', 32) if pick else 0
    emit(TB_STRUCTURE, lambda s: draw_kiosk(s, bx, pal, t=t, openness=0.9))
    emit(TB_CAST, lambda s, vv=vv: draw_vendor(s, bx + 10, pal, t=t, variant=vv))
    emit(TB_STRUCTURE, lambda s: draw_birdcage_stand(s, bx + 84, pal, t=t))
    emit(TB_CAST, lambda s, kv=kv: draw_kids(s, bx + 152, pal, t=t, n=2, variant=kv))


def draw_food_stall(surf, sx, pal, *, t=0.0, kind="steamer"):
    """One food-market stall structure (steamer/cauldron/grill/wok/tea) from
    food_stalls, feet/base on GROUND_Y, centred on `sx`. A far-lane STRUCTURE; the
    working vendor is placed separately (CAST) so it sorts in front of the booth."""
    fn, _pose = _food.STALLS.get(kind, _food.STALLS["steamer"])
    fn(surf, sx, GROUND_Y - 1, _nightf(pal), t)


def _scene_food(emit, bx, pal, t, kind, vendor_variant, rng, *, pick=None, cust_salt=0):
    """A food stall + the vendor working it (fixed pose: fanner at the grill,
    ladler at the cauldron, etc.) + a browsing customer, and critters foraging the
    scraps (pigeons mostly, sometimes a market cat or a hen) so it reads alive."""
    cust = pick('pedestrian', cust_salt) if pick else 0
    crit = rng.choice(('pigeons', 'pigeons', 'cat', 'hen'))
    emit(TB_STRUCTURE, lambda s: draw_food_stall(s, bx, pal, t=t, kind=kind))
    emit(TB_CAST, lambda s: draw_vendor(s, bx - 6, pal, t=t, variant=vendor_variant))
    emit(TB_CAST, lambda s, crit=crit: draw_critter(s, bx + 16, pal, t=t, kind=crit))
    emit(TB_CAST, lambda s, cust=cust: draw_strollers(s, bx + 36, pal, t=t, variant=cust))


def _scene_food_grill(emit, bx, pal, t, rng, pick=None):
    """A barbecue skewer-grill stall, a vendor fanning the coals, a hungry customer."""
    _scene_food(emit, bx, pal, t, 'grill', _food.STALLS['grill'][1], rng, pick=pick, cust_salt=61)


def _scene_food_soup(emit, bx, pal, t, rng, pick=None):
    """A big soup-cauldron stall with a vendor ladling broth + a customer."""
    _scene_food(emit, bx, pal, t, 'cauldron', _food.STALLS['cauldron'][1], rng, pick=pick, cust_salt=62)


def _scene_food_steamer(emit, bx, pal, t, rng, pick=None):
    """A bamboo-steamer dim-sum stall with a vendor + a customer."""
    _scene_food(emit, bx, pal, t, 'steamer', _food.STALLS['steamer'][1], rng, pick=pick, cust_salt=63)


def _scene_food_tea(emit, bx, pal, t, rng, pick=None):
    """A tea/drinks-urn stall with a vendor + a customer pausing for a cup."""
    _scene_food(emit, bx, pal, t, 'tea', _food.STALLS['tea'][1], rng, pick=pick, cust_salt=64)

def draw_dog(surf, sx, pal, *, t=0.0, variant=0):
    """One street dog from the 5-strong 'dog' pool (animals_cast), feet on
    GROUND_Y, centred on `sx`, ambling/facing the scroll direction. `variant` is a
    resolved pool index; the near lane passes it as a kwarg into the bake cache."""
    v = _fv.get("dog", variant)
    if v is None:
        return
    _animals.draw_dog(surf, sx, GROUND_Y - 1, v, _nightf(pal), t)


def draw_critter(surf, sx, pal, *, t=0.0, kind="pigeons"):
    """One street critter (pigeons/hen/cat/duck) from the 'critter' pool, feet on
    GROUND_Y, centred on `sx`. Placed near the food stalls so the market reads as
    alive (birds pecking scraps, a market cat, a hen)."""
    v = _fv.get("critter", _animals.critter_index(kind))
    if v is None:
        return
    _animals.draw_critter(surf, sx, GROUND_Y - 1, v, _nightf(pal), t)


def draw_greenery(surf, sx, pal, *, t=0.0, variant=0):
    """One potted plant / tree from the 'greenery' pool (greenery_cast),
    feet on GROUND_Y, centred on `sx`. `variant` is a resolved pool index; the near
    lane passes it as a kwarg into the bake cache. Replaces the fixed planter.

    Greenery is STATIC street furniture: it travels only with the world scroll, never
    animating in place. The live clock `t` is therefore ignored in favour of a frozen
    per-variant pose (a golden-angle stride gives each design its own fixed micro-lean),
    which also keeps the near lane's bake cache to one surface per variant."""
    v = _fv.get("greenery", variant)
    if v is None:
        return
    _green.draw_greenery(surf, sx, GROUND_Y - 1, v, _nightf(pal), variant * 2.39996)


# Greenery is placed as STATIC street planting in small, deliberate CLUSTERS rather
# than lone pots: a tall centre + a short flanker stand directly on the sidewalk, with
# a low filler tucked behind for depth. Count (2 vs 3) and footprint alternate off the
# stable world-slot key so a repeat reads as a fresh streetscape, not a loop. Centres
# stay cool/green and flankers pink/green so nothing on the deck rivals the warm gold
# coin. (Art-directed — see docs/sidewalk_overhaul/greenery_clusters.)
_GRN_TALL = (1, 21, 6, 17, 2, 26, 9, 18)     # cool/green tall centres
_GRN_SHORT = (0, 20, 10, 11, 4, 23, 16)      # low flankers (shrub/peony/mum/pink-flower/fern)
_GRN_LOW = (16, 14, 7, 0)                    # ground/back fillers


def _grn_pick(pool, k, salt):
    return pool[(k * salt + salt) % len(pool)]


def _draw_greenery_cluster(surf, sx, pal, k):
    """One static planting bed centred on `sx`; deterministic in `k` (no flicker).
    The pots stand directly on the sidewalk (same ground line as a lone planter)."""
    # Greenery holds its daytime look the whole cycle: greenery_cast's night retint
    # cooled the foliage to a muddy blue-green after dusk, which read worse than just
    # leaving the plants their clean day colour. `pal` is kept for call-site uniformity.
    night = 0.0
    triad = (k % 2 == 0)
    spread = 23 if (k % 3) else 16
    soil = GROUND_Y - 1

    def _g(idx, x):
        v = _fv.get("greenery", idx)
        if v is not None:
            _green.draw_greenery(surf, x, soil, v, night, idx * 2.39996)

    if triad:
        _g(_grn_pick(_GRN_LOW, k, 7), sx + spread - 5)    # back filler (drawn first)
        _g(_grn_pick(_GRN_TALL, k, 1), sx - 2)            # tall centre
        _g(_grn_pick(_GRN_SHORT, k, 5), sx - spread)      # front flanker
    else:
        _g(_grn_pick(_GRN_TALL, k, 1), sx - spread // 2)
        _g(_grn_pick(_GRN_SHORT, k, 5), sx + spread // 2)


def _prop_latch(family, k, salt):
    """Freeze a prop-pool variant (lamp/banner/fire/...) at slot entry, same reason
    as the greenery latch — no flicker as the beat/weather seed shifts."""
    return _fv.select_variant(family, _fv.slot_seed(k, salt),
                              _fv.beat_for_phase(_CUR_PHASE),
                              _fv.weather_bucket(_CUR_RAIN, _CUR_SNOW))


def draw_prop_lamp(surf, sx, pal, *, t=0.0, variant=0):
    """One street lamp/lantern from the 'prop_lamp' pool (slim-post / paired /
    stone-shrine), feet on GROUND_Y. Lit head capped under the night ceiling."""
    v = _fv.get("prop_lamp", variant)
    if v is not None:
        _props.draw_lamp(surf, sx, GROUND_Y - 1, v, _nightf(pal), t)


def draw_prop_banner(surf, sx, pal, *, t=0.0, variant=0):
    """One hanging banner/sign from the 'prop_banner' pool (cloth / pennant /
    signboard), feet on GROUND_Y."""
    v = _fv.get("prop_banner", variant)
    if v is not None:
        _props.draw_banner(surf, sx, GROUND_Y - 1, v, _nightf(pal), t)


def draw_prop_fire(surf, sx, pal, *, t=0.0, variant=0):
    """One brazier/censer from the 'prop_fire' pool (tripod / coal-basket / temple
    censer), feet on GROUND_Y. Capped ember glow + thin smoke wisp."""
    v = _fv.get("prop_fire", variant)
    if v is not None:
        _props.draw_fire(surf, sx, GROUND_Y - 1, v, _nightf(pal), t)


def draw_prop_dress(surf, sx, pal, *, t=0.0, variant=0):
    """One piece of market clutter from the 'prop_dress' pool (produce crates /
    woven baskets / rolled-mat + sacks), feet on GROUND_Y."""
    v = _fv.get("prop_dress", variant)
    if v is not None:
        _props.draw_dressing(surf, sx, GROUND_Y - 1, v, _nightf(pal), t)


def _scene_pastoral(emit, bx, pal, t, rng, pick=None):
    """Wish-tree + a varied dog ambling with the street + a foraging critter."""
    dv = pick('dog', 71) if pick else 0
    emit(TB_STRUCTURE, lambda s: draw_wish_tree(s, bx, pal, t=t))
    emit(TB_CAST, lambda s, dv=dv: draw_dog(s, bx + 66, pal, t=t, variant=dv))
    emit(TB_CAST, lambda s: draw_critter(s, bx + 96, pal, t=t,
                                         kind=rng.choice(('pigeons', 'cat', 'hen', 'duck'))))

def _scene_lamplighter(emit, bx, pal, t, rng, pick=None):
    """A lamplighter kindling the street lanterns at dusk."""
    emit(TB_CAST, lambda s: draw_lamplighter(s, bx, pal, t=t))

def _scene_dawn_setup(emit, bx, pal, t, rng, pick=None):
    """Vendors assembling the morning market."""
    emit(TB_FIXTURE, lambda s: draw_market_setup(s, bx, pal, t=t))

def _scene_vendor(emit, bx, pal, t, rng, pick=None):
    """A songbird-cage seller working the stand."""
    vv = pick('vendor', 33) if pick else 0
    emit(TB_STRUCTURE, lambda s: draw_birdcage_stand(s, bx, pal, t=t))
    emit(TB_CAST, lambda s, vv=vv: draw_vendor(s, bx + 12, pal, t=t, variant=vv))

def _scene_quiet(emit, bx, pal, t, rng, pick=None):
    """The temple elder pausing — a quiet, near-empty-street beat."""
    ev = pick('elder', 14) if pick else 0
    emit(TB_CAST, lambda s, ev=ev: draw_old_man(s, bx + 30, pal, t=t, variant=ev))


def _scene_bench(emit, bx, pal, t, rng, pick=None):
    """The temple elder beside a bench with a seated companion."""
    night = _nightf(pal)
    comp = tuple(_retint_person(c, night) for c in
                 ((215, 85, 100), (175, 50, 70), (80, 50, 30)))
    seat_y = (GROUND_Y - 27) + 19            # match _Bench.draw seat geometry

    def _bench(s):
        bench = _stepped(_Bench, pal, 20, bx)
        bench._blit_sprite(s)
    emit(TB_FIXTURE, _bench)
    ev = pick('elder', 15) if pick else 0
    emit(TB_CAST, lambda s: _draw_bench_person(s, bx + 8, seat_y - 8, *comp, night=night))
    emit(TB_CAST, lambda s, ev=ev: draw_old_man(s, bx + 44, pal, t=t, variant=ev))

def _scene_stroll(emit, bx, pal, t, rng, pick=None):
    """Two strolling adults from the variety pool + a varied elder on a slow walk."""
    v1 = pick('pedestrian', 11) if pick else 0
    v2 = pick('pedestrian', 12) if pick else 0
    ev = pick('elder', 13) if pick else 0
    emit(TB_CAST, lambda s, v1=v1: draw_strollers(s, bx - 7, pal, t=t, variant=v1))
    emit(TB_CAST, lambda s, v2=v2: draw_strollers(s, bx + 9, pal, t=t, variant=v2))
    emit(TB_CAST, lambda s, ev=ev: draw_old_man(s, bx + 48, pal, t=t, variant=ev))

def _scene_rest(emit, bx, pal, t, rng, pick=None):
    """A napper on a mat."""
    emit(TB_CAST, lambda s: draw_napper(s, bx, pal, t=t))

def _scene_campfire(emit, bx, pal, t, rng, pick=None):
    """A campfire with cozy pool adults + kids gathered (lit by the drawer at night)."""
    v1 = pick('pedestrian', 21) if pick else 0
    v2 = pick('pedestrian', 22) if pick else 0
    kv = pick('kid', 23) if pick else 0
    emit(TB_FIXTURE, lambda s: draw_campfire(s, bx, pal, t=t))
    emit(TB_CAST, lambda s, v1=v1: draw_strollers(s, bx + 50, pal, t=t, variant=v1))
    emit(TB_CAST, lambda s, v2=v2: draw_strollers(s, bx + 64, pal, t=t, variant=v2))
    emit(TB_CAST, lambda s, kv=kv: draw_kids(s, bx + 100, pal, t=t, n=2, variant=kv))

def _scenarios(surf, w, scroll, pal, t, roster, x0=40):
    """Place the beat's scene roster at world-x slots, scrolling at world speed.

    Legacy gallery path (PHASES_R17): scenes now EMIT their sub-objects, so give
    them an emit that paints immediately in submission order — no depth buffer."""
    def _emit(_tier, fn):
        fn(surf)
    for bx, k in sp._world_xs(scroll, w, _SCENARIO_PERIOD, x0,
                              mult=sp.GROUND_MULT, margin=_SCENE_MARGIN):
        rng = random.Random((k * 0x9E3779B1) & 0xFFFFFFFF)
        roster[k % len(roster)](_emit, bx, pal, t, rng)


def phase_day(surf, w, gy, h, scroll, pal, t):
    """DAY · Pastoral Morning. Prayer-flag bunting overhead; pastoral/market
    scenes scroll past. Bright, calm, unlit."""
    global _CUR_PAL
    _CUR_PAL = pal
    _ground_furniture(surf, w, scroll, pal)
    for xl, xr, _k in sp._garland_spans(scroll, w, period=150, x0=20):
        draw_prayer_flags(surf, int(xl), GROUND_Y - 118, int(xr), GROUND_Y - 116, n=5)
    _scenarios(surf, w, scroll, pal, t, (_scene_market, _scene_pastoral), x0=40)


def phase_golden(surf, w, gy, h, scroll, pal, t):
    """GOLDEN HOUR · lamp posts up + a lantern garland; bench/market scenes."""
    global _CUR_PAL
    _CUR_PAL = pal
    _ground_furniture(surf, w, scroll, pal)
    sp._draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 96,
                             period=150, sag=22, per_span=2)
    for sx, k in sp._world_xs(scroll, w, 250, x0=20):
        sp._draw_lamp_post(surf, sx, pal, style='ornate', height=96, lantern='red')
    for sx, k in sp._world_xs(scroll, w, 250, x0=160):
        sp._draw_lamp_post(surf, sx, pal, style='ornate', height=90, lantern='gold')
    _scenarios(surf, w, scroll, pal, t, (_scene_bench, _scene_market), x0=70)


def phase_dusk(surf, w, gy, h, scroll, pal, t):
    """DUSK · lamps + fairy lights lighting (gated to the dark sky); rest/stroll
    scenes. Lavender, quieter."""
    global _CUR_PAL
    _CUR_PAL = pal
    _ground_furniture(surf, w, scroll, pal)
    sp._draw_fairy_lights(surf, w, scroll, pal, top_y=GROUND_Y - 92,
                          period=210, sag=26, per_span=5)
    for sx, k in sp._world_xs(scroll, w, 250, x0=24):
        sp._draw_lamp_post(surf, sx, pal, style='ornate', height=94, lantern='red')
    for sx, k in sp._world_xs(scroll, w, 250, x0=158):
        sp._draw_lamp_post(surf, sx, pal, style='ornate', height=88, lantern='glass')
    _scenarios(surf, w, scroll, pal, t, (_scene_rest, _scene_stroll), x0=55)


def phase_night(surf, w, gy, h, scroll, pal, t):
    """NIGHT · Festival. Lantern garland + fairy lights + lamp posts all glowing
    (capped); campfire/market scenes. The payoff."""
    global _CUR_PAL
    _CUR_PAL = pal
    _ground_furniture(surf, w, scroll, pal)
    sp._draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 98,
                             period=118, sag=24, per_span=3)
    sp._draw_fairy_lights(surf, w, scroll, pal, top_y=GROUND_Y - 78,
                          period=200, sag=22, per_span=5)
    for sx, k in sp._world_xs(scroll, w, 250, x0=18):
        sp._draw_lamp_post(surf, sx, pal, style='ornate', height=96, lantern='red')
    for sx, k in sp._world_xs(scroll, w, 250, x0=152):
        sp._draw_lamp_post(surf, sx, pal, style='ornate', height=90, lantern='gold')
    _scenarios(surf, w, scroll, pal, t, (_scene_campfire, _scene_market), x0=30)


# (label, painter)
PHASES_R17 = [
    ("DAY · Pastoral Morning", phase_day),
    ("GOLDEN HOUR · Afternoon Promenade", phase_golden),
    ("DUSK · Lamps Lighting", phase_dusk),
    ("NIGHT · Festival", phase_night),
]


# ── live composition: the day-arc DIRECTOR ────────────────────────────────────
#
# Replaces the old 4 interchangeable crossfade beats (which read as an artificial,
# evenly-packed loop) with ONE continuous story of a market street's day: it
# ASSEMBLES at run-start, builds through the day, PEAKS as a night festival, then
# tears down to a near-empty pre-dawn before the next day. Two signals drive it,
# both already in hand: `phase` (the biome day-cycle position) picks the dressing +
# cast vocabulary and the crowd density; `t` (= world.biome_time, 0 at run-start,
# monotonic) ramps the street from empty as the run opens. Dressing is drawn in a
# SINGLE pass (no per-frame double-beat layer) — also cheaper than the old crossfade.

# Crowd-density curve over the day (piecewise-linear keypoints, phase -> 0..1).
# Two NAMED PEAK EVENTS rise out of an otherwise-CALM ("lightly populated") day:
# the early-Day FOOD-MARKET rush (the run opens on it) and the NIGHT FESTIVAL.
# Everything between is a quiet ~0.25 stroll, and pre-dawn is near-empty. Keeping
# the floor this low is also the main lag win (object count dominates the cost).
_POP_KEYS = [
    (0.00, 0.58),   # run-start: the market is already opening (peak fills via _run_fill)
    (0.06, 0.85),   # FOOD-MARKET peak
    (0.14, 0.50),   # market winding down
    (0.20, 0.26),   # calm late-morning
    (0.34, 0.24),   # golden lull — just strolling
    (0.50, 0.30),   # dusk, lamps starting to light
    (0.58, 0.55),   # festival ramp
    (0.66, 1.00),   # NIGHT FESTIVAL peak
    (0.74, 0.94),
    (0.80, 0.22),   # teardown
    (0.86, 0.06),   # pre-dawn — near-empty
    (0.93, 0.22),   # sunrise — first vendors return
    (1.00, 0.58),   # wrap back to the opener
]

def _population(phase):
    p = phase % 1.0
    for i in range(len(_POP_KEYS) - 1):
        a, va = _POP_KEYS[i]
        b, vb = _POP_KEYS[i + 1]
        if a <= p <= b:
            f = (p - a) / (b - a) if b > a else 0.0
            return va + (vb - va) * f
    return _POP_KEYS[-1][1]

_FILL_SECONDS = 7.0   # the market "opens" over the first few seconds of a run

def _run_fill(t):
    x = max(0.0, min(1.0, t / _FILL_SECONDS))
    return x * x * (3.0 - 2.0 * x)   # smoothstep: street starts empty, fills in

def _slot_on(k, salt, density):
    """Stable per-slot inclusion gate: hash (slot index, salt) to [0,1) and admit
    the slot iff that fixed threshold is below `density`. Because the threshold is
    keyed to the WORLD slot (not the frame), a slot pops in exactly once as the
    density curve rises and never flickers — and its x never moves."""
    h = ((k * 0x9E3779B1) ^ (salt * 0x85EBCA77)) & 0xFFFF
    return (h / 65535.0) < density

def _slot_pick(k, n):
    """Stable per-slot choice in [0, n): which roster entry a world slot uses. Keyed
    to the slot index so the choice is identical as the slot scrolls (no flicker)."""
    return ((k * 0x9E3779B1) >> 16) % n

def _furn_density(phase):
    """Fixture density (planters/cairns/greenery). Gentle and PHASE-ONLY — NOT
    multiplied by `_run_fill` — so the static deck dressing is present from t=0 and
    never flickers; just sparser off-peak and a touch fuller at the peak events."""
    return 0.34 + 0.22 * _population(phase)

def _roster_for(phase):
    """The cast vocabulary by time of day. The early-Day window is the FOOD-MARKET
    rush (busy, market-heavy); the rest of the day is light (strolling/quiet beats)
    until the NIGHT festival. Pre-dawn is near-empty. Bigger, more varied rosters
    (4–5 options) + the no-repeat rule in _place_scenarios kill the short loop."""
    p = phase % 1.0
    if p < 0.14:                       # DAY — FOOD-MARKET rush (the run opener)
        return (_scene_food_grill, _scene_food_soup, _scene_market, _scene_food_steamer,
                _scene_food_tea, _scene_dawn_setup, _scene_vendor)
    if p < 0.25 or p >= 0.85:          # DAY / SUNRISE — calm morning
        return (_scene_pastoral, _scene_vendor, _scene_quiet, _scene_stroll)
    if p < 0.40:                       # GOLDEN — afternoon stroll
        return (_scene_stroll, _scene_pastoral, _scene_quiet, _scene_bench)
    if p < 0.58:                       # DUSK — lamps lighting
        return (_scene_lamplighter, _scene_stroll, _scene_bench, _scene_rest)
    if p < 0.80:                       # NIGHT — festival (food stalls glow nicely)
        return (_scene_campfire, _scene_food_grill, _scene_food_soup, _scene_stroll, _scene_bench)
    return (_scene_quiet, _scene_rest) # PRE-DAWN — near-empty teardown

def _dressing(surf, w, scroll, pal, phase):
    """Phase-gated street fixtures in one pass (glow follows the palette). Lamps +
    lanterns are installed for the evening and stay as fixtures; the prayer-flag
    bunting is the daytime look."""
    p = phase % 1.0
    # Garland strands are continuous, so each SPAN latches its window membership at
    # entry: the strand scrolls in/out span-by-span instead of the whole row
    # flashing at the phase-window edge.
    bunting_win = (p >= 0.85 or p < 0.28)                        # daytime bunting
    for xl, xr, k in sp._garland_spans(scroll, w, period=150, x0=20):
        if sp._slot_latch(('bunting',), k, lambda: bunting_win):
            draw_prayer_flags(surf, int(xl), GROUND_Y - 118,
                              int(xr), GROUND_Y - 116, n=5)
    sp._latch_prune(('bunting',))
    lantern_win = True                  # hung lantern garland stays strung + lit all cycle
    sp._draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 97,
                             period=128, sag=23, per_span=3,
                             span_gate=lambda k: sp._slot_latch(('lantgar',), k,
                                                                lambda: lantern_win))
    sp._latch_prune(('lantgar',))
    # Lamp posts: a discrete world-slot row. Latch each post's "is the evening
    # window open?" at entry so the row scrolls IN when dusk arrives and scrolls
    # OUT after dawn, instead of the whole on-screen row blinking at the window edge.
    lamp_win = (0.20 <= p < 0.93)
    fy = GROUND_Y - 1
    for sx, k in sp._world_xs(scroll, w, 250, x0=18):
        on, lv = sp._slot_latch(('lampR',), k, lambda k=k: (
            lamp_win, _prop_latch('prop_lamp', k, 31)))
        if on:
            _zbuf.enqueue(fy, TB_STRUCTURE, lambda s, sx=sx, lv=lv: draw_prop_lamp(
                s, sx, pal, t=_CUR_T, variant=lv))
    sp._latch_prune(('lampR',))
    for sx, k in sp._world_xs(scroll, w, 250, x0=152):
        on, lv = sp._slot_latch(('lampG',), k, lambda k=k: (
            lamp_win, _prop_latch('prop_lamp', k, 32)))
        if on:
            _zbuf.enqueue(fy, TB_STRUCTURE, lambda s, sx=sx, lv=lv: draw_prop_lamp(
                s, sx, pal, t=_CUR_T, variant=lv))
    sp._latch_prune(('lampG',))
    fairy_win = True                    # hung fairy lights stay strung + lit all cycle
    sp._draw_fairy_lights(surf, w, scroll, pal, top_y=GROUND_Y - 84,
                          period=205, sag=24, per_span=5,
                          span_gate=lambda k: sp._slot_latch(('fairy',), k,
                                                             lambda: fairy_win))
    sp._latch_prune(('fairy',))

def _place_scenarios(surf, w, scroll, pal, t, roster, density, x0=40):
    """Place the time-appropriate cast at FIXED world-x slots, THINNED by `density`:
    each slot is admitted only with probability `density` (seeded by slot index so
    it's stable as it scrolls). The spacing is constant — only the per-slot gate
    changes with density — so a figure pops in once instead of sliding when the
    crowd fills in. Off-peak the street is mostly open paving; at night it fills."""
    if not roster:
        return
    n = len(roster)
    row = ('scenario', x0)
    for bx, k in sp._world_xs(scroll, w, _SCENARIO_PERIOD, x0,
                              mult=sp.GROUND_MULT, margin=_SCENE_MARGIN):
        # Decide ONCE, while the slot is still off-screen to the right: whether it
        # is occupied (density gate) and WHICH vignette it holds (roster choice +
        # no-repeat). Latched for the whole traversal so a slot never blinks on/off
        # or morphs as the day-density curve and roster shift under it — it only
        # scrolls in and out. New slots entering later read the new density/roster.
        def _decide(k=k):
            r = random.Random((k * 0x9E3779B1) & 0xFFFFFFFF)
            if r.random() > density:        # stable per-slot inclusion
                return None
            idx = _slot_pick(k, n)
            if n > 1 and idx == _slot_pick(k - 1, n):
                idx = (idx + 1) % n
            jit = (((k * 0x85EBCA77) >> 13) % 97) - 48
            # Freeze the day-arc beat + weather bucket at slot ENTRY so the cast's
            # variant choices stay fixed for the whole on-screen traversal (a slot
            # that entered in clear weather keeps its clear dress even if rain
            # starts while it crosses; new slots entering in rain get brollies).
            beat0 = _fv.beat_for_phase(_CUR_PHASE)
            wb0 = _fv.weather_bucket(_CUR_RAIN, _CUR_SNOW)
            return (roster[idx], jit, beat0, wb0)
        dec = sp._slot_latch(row, k, _decide)
        if dec is not None:
            scene_fn, jit, beat0, wb0 = dec
            # Recreate the per-slot RNG and consume the inclusion draw so the scene's
            # internal variety matches the pre-latch behaviour exactly.
            r = random.Random((k * 0x9E3779B1) & 0xFFFFFFFF)
            r.random()
            # Each scene enqueues its sub-objects on the far-lane feet line; the tier
            # it passes orders props/cast vs structures at that shared line.
            def _emit(tier, fn):
                _zbuf.enqueue(GROUND_Y - 1, tier, fn)
            # Stable per-figure variant picker for this slot, frozen to the entry
            # beat/weather — scenes call pick(family, salt) for each figure they
            # place (family one of 'pedestrian'/'kid'/'elder'/'vendor').
            def _pick(family, salt, k=k, beat0=beat0, wb0=wb0):
                return _fv.select_variant(family, _fv.slot_seed(k, salt), beat0, wb0)
            scene_fn(_emit, bx + jit, pal, t, r, _pick)
    sp._latch_prune(row)

def draw_promenade(surf, scroll, pal, phase, t):
    """Draw the promenade as a living day-arc: fixtures by phase, cast thinned by a
    crowd-density curve, and the whole street filling in from empty at run-start."""
    global _CUR_BUCKET, _CUR_T, _CUR_PAL, _CUR_RAIN, _CUR_SNOW, _CUR_WIND, _CUR_PHASE
    _CUR_BUCKET = _biome.phase_bucket(phase)
    _CUR_T = t
    _CUR_PAL = pal
    _CUR_PHASE = phase
    _CUR_RAIN = rain_intensity(phase)
    _CUR_SNOW = storm_intensity(phase)
    _CUR_WIND = wind_intensity(phase)
    # The crowd thins in bad weather: the day-arc density is scaled down by rain/
    # snow. Multiplying only lowers each slot's stable inclusion gate, so figures
    # walk off ONCE as the storm builds (no flicker) and the survivors get brollies.
    density = _population(phase) * _run_fill(t) * _weather_crowd_factor(phase)
    _ground_furniture(surf, W, scroll, pal, fd=_furn_density(phase))
    _dressing(surf, W, scroll, pal, phase)
    _place_scenarios(surf, W, scroll, pal, t, _roster_for(phase), density)
    # A few souls shelter near the dressing (kiosk awnings / lamp posts) when the
    # open deck has emptied — keeps the street alive at the storm's worst.
    _shelter_figures(surf, W, scroll, pal, t)
