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
  NIGHT  Festival PEAK — lantern garland + lamps glowing (capped), a
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
from game import foreground_weekend as _wk
from game import weekend_kit as _wkit
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


def _sunk(surf, dy):
    """A view of the frame shifted `dy` px down. Far-lane drawers hard-code
    their geometry off GROUND_Y, so depth is applied by handing them a
    subsurface whose origin sits `dy` lower — the whole figure lands deeper in
    the walk with no drawer changes, and the z-buffer sorts on the shifted
    feet line. Shares pixels with the frame; creation is O(1)."""
    return surf.subsurface((0, dy, surf.get_width(), surf.get_height() - dy))


# ── the band's one perspective law ───────────────────────────────────────────
#
# Every figure in the 45 px walk follows the same size-for-depth ramp,
# calibrated so the front kerb matches the shipped near-lane size: s(dy) =
# 1 + 0.0134·dy, dy measured down from the back kerb (594). Far-lane cast
# quantises to three tiers on a 9 px pitch; the near lane continues the same
# pitch to the front kerb — so there is no dead zone mid-walk and no scale
# cliff at the lane seam.
_FAR_TIER_DY = (0, 9, 18)


def _far_tier(dy):
    """Authored role-depth → tier index (0 back kerb / 1 mid / 2 walk)."""
    return 0 if dy < 5 else (1 if dy < 12 else 2)


_SHADOW_CACHE = {}


def _shadow(surf, cx, feet_y, wpx, night):
    """Soft contact pool under a cast figure — the grounding cue that separates
    a low-contrast figure from the paving without touching either's colour. By
    day it is a dark cast shadow; after dusk the cue INVERTS to a faint pale
    pool (lantern spill), because a dark ellipse does nothing on dark wet
    stone — exactly the frames that need grounding most. The two polarities
    CROSSFADE over night 0.40-0.60 (a hard switch left the dusk band, where
    ground and figures share one mid value, with neither cue). Height tracks
    width (~5:1) so a wide figure gets a pool, not a smear."""
    wl = min(1.0, max(0.0, (night - 0.40) / 0.20))     # pale-pool weight
    h = max(3, wpx // 5)
    key = (wpx, int(wl * 8))
    sp_ = _SHADOW_CACHE.get(key)
    if sp_ is None:
        sp_ = pygame.Surface((wpx, h), pygame.SRCALPHA)
        if wl < 1.0:
            pygame.draw.ellipse(sp_, (18, 20, 30, int(55 * (1.0 - wl))),
                                (0, 0, wpx, h))
        if wl > 0.0:
            pygame.draw.ellipse(sp_, (216, 224, 240, int(34 * wl)),
                                (wpx // 6, h // 4, wpx - wpx // 3, h - h // 2))
        _SHADOW_CACHE[key] = sp_
    surf.blit(sp_, (cx - wpx // 2, feet_y - h // 2 - 1))

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
    than intended; the snow squall bottoms out near-empty.

    The RAIN term is concave (sqrt), because a linear one emptied the street
    only at the very peak: at rain 0.35 it still kept 73% of the crowd and at
    0.53 — visibly heavy — 59%, so every second of rain except the crest read
    as a busy street wearing umbrellas. People leave at the first real rain,
    not at the worst of it. SNOW stays LINEAR on purpose: its ramp covers the
    dragon dancing through the first flakes, and the same curve there would
    thin the festival's closing crowd from ~13 to ~9 figures."""
    ri = rain_intensity(phase)
    wi = storm_intensity(phase)
    rain_f = 1.0 - (1.0 - WEATHER_CROWD_RAIN_MIN) * math.sqrt(ri)
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



def _draw_umbrella(surf, cx, canopy_y, color_idx, *, night=0.0, scale=1.0,
                   pole_len=9):
    """A small held umbrella: a domed, gently-scalloped canopy with a top nub, a
    couple of ribs, and a pole running down to the hand. Leans into the wind by
    `_CUR_WIND`. Opaque draws (no alpha) so it composites straight onto the deck;
    colour capped under the coin at night."""
    # Canopy geometry lives in the kit now (the ribbed oil-paper build — panel
    # value alternation + hem scallops that count the ribs); wind lean preserved.
    _wkit.draw_umbrella8(surf, cx, canopy_y, color_idx, night=night, scale=scale,
                         pole_len=pole_len, wind=_CUR_WIND)


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


# ── the hung lantern garland reads "on" for its whole window ───────────────────
#
# The garland is strung from market setup (0.416) through the small hours, so the
# front of that window is still daylight. Its lit faces + halos follow a daytime
# FLOOR under the normal dusk->night curve, so a lantern hung in the afternoon
# still reads lit instead of as a dead grey shell. At full night the floor is moot
# (intensity is already 1.0), so the night-cap behaviour — capped faces + capped
# additive halos staying under the coin — is unchanged.
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
# The r15 garland rope was dark (≈62,52,44) so at night the strung spans read as
# black scribble crisscrossing the upper band. The promenade draws the wire as ONE
# thin catenary per span lifted toward the sky value (a faint semi-transparent
# line), so only the bulbs carry weight. The strand drawer is re-bound to use this
# faint-wire variant; only the rope colour changes.

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
                   per_span=3, colors=('red', 'gold'), span_gate=None, x0=12):
    """r15 lantern garland with the faint single-catenary wire. The hung lanterns
    stay lit + cast a soft warm halo across the WHOLE cycle (string-light floor,
    not the dusk lamp gate), so the strand never reads 'off'. `x0` anchors the
    span lattice so a second row can interleave offset from the first."""
    for xl, xr, k in sp._garland_spans(scroll, w, period, x0=x0):
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
            # The night market's signature light. The halo ran at alpha 52 —
            # 43% of the available peak — which read as a dim bead rather than
            # a lantern throwing light; it now carries a wider, stronger pool
            # so the strung lanterns actually light the street under them.
            _string_glow(surf, int(bx), int(by) + 5, pal, radius=12, alpha=86,
                         color=glow_col)
            if _nightf(pal) > 0.25:
                add_light_spot(int(bx), glow_col)
            snowc = _SIG.get('snow_cover', 0.0) or 0.0
            if snowc > 0.12:
                # a white cap settling on the lantern's crown
                cap = (238, 243, 249)
                aa = int(min(200, 90 + 130 * snowc))
                capw = 6
                caps = pygame.Surface((capw + 2, 3), pygame.SRCALPHA)
                pygame.draw.ellipse(caps, (*cap, aa), (0, 0, capw + 2, 3))
                surf.blit(caps, (int(bx) - capw // 2 - 1, int(by) - 7))


sp._draw_lantern_garland = _garland_faint


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
    return _mix(col, (78, 88, 118), min(0.38, 0.28 * night + 0.14))


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


def draw_kids(surf, sx, pal, *, t=0.0, n=3, variant=0, masks=False):
    """`n` small children drawn from the 10-strong 'kid' variety pool (day_cast),
    feet on GROUND_Y. `variant` is a resolved base pool index; each of the n kids
    takes the next pool member (variant, variant+1, …) so a group reads as several
    different children, not one cloned thrice. With `masks`, ~1 kid in 3 wears
    the paper monkey mask (worn / pushed-up mix) — the troupe's souvenir
    spreading through the crowd after the act."""
    night = _nightf(pal)
    cnt = _fv.variant_count("kid")
    if not cnt:
        return
    spread = (-13, 9, 26, 40, -28)
    for i in range(n):
        v = _fv.get("kid", (variant + i) % cnt)
        kx = sx + spread[i % len(spread)]
        _day.draw_kid(surf, kx, GROUND_Y - 1, v, night, t + i * 0.6)
        if masks:
            _kid_mask_overlay(surf, kx, v, variant + i, night, t + i * 0.6)


def _kid_mask_overlay(surf, kx, v, salt, night, t):
    """Seat the souvenir mask on the drawn kid's own head circle, recomputing
    the day_cast head geometry for the poses where it is stable (standing,
    squat). ~1 in 3 wears one; the worn/pushed-up split is hashed with it so a
    kid never flickers between the two."""
    h = _mix32(salt * 0x9E3779B1)
    if h % 3:
        return
    pose = v.pose
    if any(k in pose for k in ('carried', 'chase', 'tiptoe')):
        return
    A = v.attrs
    age = A.get("age", 0.6)
    total = max(7, int(13 * (0.62 + 0.38 * age)))
    squat = 'squat' in pose
    head_bias = 0.10 if squat else 0.0
    head_r = max(2, int(total * (0.34 + head_bias - 0.06 * age)))
    body_h = max(3, int(total * 0.32))
    ground = GROUND_Y - 1
    if squat:
        body_y = ground - body_h - 1
    else:
        body_y = (ground - max(2, int(total * 0.30))) - body_h
    hy = body_y - head_r + 1
    from game import festival as _fest
    if (h >> 8) & 1:
        _fest.draw_monkey_mask(surf, kx, hy, night, r=head_r + 1, plume=t * 2.0)
    else:
        _fest.draw_monkey_mask(surf, kx, hy - head_r - 1, night, r=head_r,
                               plume=t * 2.0, worn=False)


def draw_vendor(surf, sx, pal, *, t=0.0, variant=0):
    """One standing market vendor/worker from the 10-strong 'vendor' pool
    (day_cast), feet on GROUND_Y, centred on `sx`. `variant` is a resolved pool
    index; the near lane passes it as a kwarg so it enters the bake cache key."""
    v = _fv.get("vendor", variant)
    if v is None:
        return
    _day.draw_vendor(surf, sx, GROUND_Y - 1, v, _nightf(pal), t)


def draw_old_man(surf, sx, pal, *, t=0.0, seated_bench=False, variant=0):
    """A TEMPLE ELDER from the 10-strong 'elder' variety pool (day_cast) — varied
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
    """Draw ONE adult pedestrian from the 57-strong variety pool (ped_cast),
    feet on GROUND_Y, centred on `sx`. `variant` is a resolved pool index; the
    near lane passes it as a kwarg so it enters the bake cache key. Umbrella/hood/
    coat looks now come from weather-weighted pool variants, so the old `umbrella`
    flag is accepted only for signature compatibility and ignored."""
    v = _fv.get("pedestrian", variant)
    if v is None:
        return
    night = _nightf(pal)
    # Weather-dress substitution: in a real storm/snow, weather-locked rows may
    # trade their look for the kit's suoyi cape / padded winter figure.
    dress = _wkit.weekend_dress(variant, _CUR_RAIN, _CUR_SNOW)
    if dress == "suoyi":
        _wkit.draw_suoyi(surf, sx, GROUND_Y - 1, night, t,
                         carry=("crate" if variant % 3 else "pole"))
        return
    if dress == "winter":
        _wkit.draw_winter_figure(surf, sx, GROUND_Y - 1, night, t,
                                 coat=("indigo" if variant % 2 else "rust"),
                                 scarf=("stream" if variant % 3 else "drape"),
                                 storm=max(0.4, _CUR_SNOW), phase=variant * 0.73)
        return
    _ped._draw_one(surf, sx, GROUND_Y - 1, pal, v, night, t)


def _draw_shelterer(surf, sx, pal, *, t=0.0, h=0):
    """One huddled umbrella-holder under the standard far-cast drawer contract
    (colours dealt from the slot hash `h`), so shelterers ride the depth law's
    bake like the rest of the cast."""
    night = _nightf(pal)
    base = (78 + (h >> 2 & 63), 84 + (h >> 5 & 55), 108 + (h >> 8 & 47))
    shirt = _retint_person(base, night)
    body_y = GROUND_Y - 1 - 8 - 3
    _draw_bench_person(surf, sx, body_y, shirt, _shade(shirt, -34),
                       _retint_person((60, 45, 38), night), night=night)
    _draw_umbrella(surf, sx + 3, body_y - 6, (h >> 2), night=night)


def _shelter_figures(surf, w, scroll, pal, t):
    """A few people standing huddled under umbrellas at stable world slots, shown
    only once the open deck has emptied (heavy rain / real snow) — so the street
    still feels lived-in at the storm's worst instead of dead. Sparse + world-
    anchored (a fixed per-slot hash admits ~1 in 4), so they scroll past without
    flicker and pop in/out only as the weather crosses the threshold."""
    sev = max(_CUR_RAIN, _CUR_SNOW)
    if sev < 0.45:
        return
    for sx, k in sp._world_xs(scroll, w, 250, x0=30, mult=sp.GROUND_MULT, margin=40):
        h = (k * 0x9E3779B1) & 0xFFFFFFFF
        if (h & 3) != 0:                       # ~1 in 4 slots is occupied
            continue
        bx = sx + 6 + (h >> 4 & 7)
        # Shelterers spread through the walk's depth on the band's tier pitch
        # and ride the shared bake so they scale, dim, and shadow like any
        # other cast.
        d_eff = _FAR_TIER_DY[(h >> 16) % 3]
        fyc = GROUND_Y - 1 + d_eff

        def _fig(s, bx=bx, h=h, fyc=fyc, d_eff=d_eff):
            from game import foreground_near_lane as _nl
            _nl._scaled_cast(s, _draw_shelterer, bx, _CUR_PAL,
                             1.0 + 0.0134 * d_eff, feet_y=fyc, h=h & 0xFFFF)
        _zbuf.enqueue(fyc, TB_CAST, _fig)


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
    """World-anchored ground FIXTURES — barrels, cairns, market clutter, plus
    the town's PLANTING (tree line + beds). Part of the street, not the crowd:
    FIXED spacing so they stay pinned to the sidewalk and scroll at world speed.
    `fd` thins the loose clutter rows (barrel/cairn/dress) via a STABLE
    per-slot gate (keyed to the world slot, not t/scroll) so the deck reads
    scattered, never a wall — yet stays present from t=0 and never flickers.
    The planting rows deliberately ignore `fd`: they follow the per-run,
    day-stable plant_scheme instead, because street trees and kept beds don't
    come and go with the decor curve. Drawn behind the cast."""
    # Each lane's inclusion is latched at entry (off-screen) so a fixture never
    # blinks out in view when `fd` dips — it scrolls in and out like the deck it
    # sits on.
    fy = GROUND_Y - 1

    def _enq_sunk(dy, tier, fn):
        # Fixtures sink into the walk like the cast; dy=0 keeps the back kerb.
        if dy:
            _zbuf.enqueue(fy + dy, tier, lambda s, f=fn, d=dy: f(_sunk(s, d)))
        else:
            _zbuf.enqueue(fy, tier, fn)

    for sx, k in sp._world_xs(scroll, w, 439, x0=14):
        if sp._slot_latch(('furn', 11), k, lambda k=k: _slot_on(k, 11, fd)):
            _enq_sunk((_mix32(k * 0x9E3779B1) >> 3) % 9, TB_FIXTURE,
                      lambda s, sx=sx: sp._draw_barrel(s, sx, pal))
    sp._latch_prune(('furn', 11))
    for sx, k in sp._world_xs(scroll, w, 443, x0=118):
        if sp._slot_latch(('furn', 12), k, lambda k=k: _slot_on(k, 12, fd)):
            _enq_sunk((_mix32(k * 0x85EBCA77) >> 5) % 9, TB_FIXTURE,
                      lambda s, sx=sx: sp._draw_cairn(s, sx, pal, scale=1.2))
    sp._latch_prune(('furn', 12))
    # PLANTING BEDS — only on the blocks the plan marks as garden stretches,
    # so a bed reads as a kept front-garden rather than a random pot drop. The
    # bed's soil rectangle + stone edging draw first (back line, structure
    # tier); its plants enqueue on their own feet lines so passers-by sort
    # between the rows while the rectangle ties them into ONE bed.
    for sx, k in sp._world_xs(scroll, w, 331, x0=70):
        if _wk.plant_scheme(k * 331 + 70)[2]:
            _zbuf.enqueue(fy, TB_STRUCTURE,
                          lambda s, sx=sx, k=k: _bed_base(s, sx, k, pal))
            for idx, xo, dy in _bed_layout(k):
                _zbuf.enqueue(fy + dy, TB_FIXTURE,
                              lambda s, x=sx + xo, idx=idx, dy=dy: _grn_at(s, x, idx, dy))
    for sx, k in sp._world_xs(scroll, w, 701, x0=330):
        on, dv = sp._slot_latch(('furn', 15), k, lambda k=k: (
            _slot_on(k, 15, fd), _prop_latch('prop_dress', k, 15)))
        if on:
            _enq_sunk((_mix32(k * 0xC2B2AE35) >> 4) % 7, TB_FIXTURE,
                      lambda s, sx=sx, dv=dv: draw_prop_dress(s, sx, pal, t=_CUR_T, variant=dv))
    sp._latch_prune(('furn', 15))


# ── grouped scenarios ─────────────────────────────────────────────────────────
#
# Coherent little scenes placed at world-x slots: the bird passes one, then open
# road, then the next. Each scene's contents are seeded by its slot index `k`
# (NOT by `scroll`), so a scene is identical frame-to-frame as it scrolls past —
# world-anchored, no flicker (same idiom as the mountain-ornament fix). Members
# animate in place from the live clock `t`; positions ride the scroll.

_SCENARIO_PERIOD = 384          # world-px between scene SLOTS — dense enough that a
                                # busy hour keeps ~1 vignette on screen (the depth
                                # ladder needs bodies to sort); calm hours still read
                                # open because the density gate empties most slots.
_SCENE_MARGIN = 420             # wide enough to slide a whole STRIP in/out smoothly

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
    emit(TB_CAST, dy=9, cast=(draw_vendor, bx + 10, dict(t=t, variant=vv)))
    emit(TB_STRUCTURE, lambda s: draw_birdcage_stand(s, bx + 84, pal, t=t))
    emit(TB_CAST, dy=18, cast=(draw_kids, bx + 152, dict(t=t, n=2, variant=kv)))


def draw_food_stall(surf, sx, pal, *, t=0.0, kind="steamer", openness=1.0):
    """One food-market stall structure (steamer/cauldron/grill/wok/tea) from
    food_stalls, feet/base on GROUND_Y, centred on `sx`. A far-lane STRUCTURE; the
    working vendor is placed separately (CAST) so it sorts in front of the booth."""
    fn, _pose = _food.STALLS.get(kind, _food.STALLS["steamer"])
    fn(surf, sx, GROUND_Y - 1, _nightf(pal), t, openness=openness)


def _stall_openness(phase, u):
    """The market-assembly timeline: how built a stall is at `phase`, with `u` in
    [0,1) the stall's dealt stagger so the market closes raggedly from both ends
    rather than on one frame. By day a placed stall is simply open; from sunset
    the frames go up bare, dress through the rain (the vendors carted everything
    here — they work through it), peak open in the clear night window, then run a
    visible staggered close as the flakes arrive."""
    p = phase % 1.0
    if p < 0.416 or p >= 0.924:
        return 1.0                     # daytime / first-light stalls: open
    if p < 0.452:
        return 0.35                    # carts arrive — bare frames, rolled awnings
    if p < 0.483:
        return 0.6                     # dressing: awnings unrolled, goods going on
    if p < 0.680:
        return 0.7                     # rained-on setup: open, working under it
    if p < 0.820:
        return 1.0                     # the festival peak
    start = 0.820 + u * 0.035          # staggered close-down (~0-14 s spread)
    if p < start:
        return 1.0
    return max(0.0, 1.0 - (p - start) / 0.02)


def _scene_food(emit, bx, pal, t, kind, vendor_variant, rng, *, pick=None, cust_salt=0):
    """A food stall + the vendor working it (fixed pose: fanner at the grill,
    ladler at the cauldron, etc.) + a browsing customer, and critters foraging the
    scraps (pigeons mostly, sometimes a market cat or a hen) so it reads alive.
    The stall's assembly state follows the market timeline; its people follow the
    state (a bare frame has its builder, an open stall has its trade)."""
    u = rng.random()
    openness = _stall_openness(_CUR_PHASE, u)
    if openness <= 0.05:
        return                          # struck and carried off
    # In a real downpour the stall doesn't close — the vendor pitched a tarp
    # over it (the sheet sheds toward the downwind corner, the brazier and the
    # steam keep going, the vendor sits it out underneath). Open despite rain.
    if _CUR_RAIN > 0.35 and openness >= 0.5:
        emit(TB_STRUCTURE, lambda s: _wkit.draw_stall_tarp(
            s, bx, GROUND_Y - 1, _nightf(pal), t, kind=kind, rain=_CUR_RAIN))
        return
    cust = pick('pedestrian', cust_salt) if pick else 0
    crit_pool = ('pigeons', 'pigeons', 'cat', 'hen')
    if _fv.beat_for_phase(_CUR_PHASE) == _fv.BEAT_MARKET:
        # The piglet arrives with the produce — market beat only, so it never
        # turns up at dusk with nobody to own it.
        crit_pool += ('piglet',)
    crit = rng.choice(crit_pool)
    emit(TB_STRUCTURE, lambda s: draw_food_stall(s, bx, pal, t=t, kind=kind,
                                                 openness=openness))
    if openness < 0.65:
        # the market being assembled or struck: the handcart stands alongside
        load = "loaded" if openness < 0.45 else "half"
        emit(TB_FIXTURE, lambda s, load=load: _wkit.draw_cart_folded(
            s, bx + 34, GROUND_Y - 1, _nightf(pal), t, load=load), dy=6)
    if openness >= 0.30:
        emit(TB_CAST, dy=9, cast=(draw_vendor, bx - 6, dict(t=t, variant=vendor_variant)))
    if openness >= 0.80:
        emit(TB_CAST, dy=18, cast=(draw_critter, bx + 16, dict(t=t, kind=crit)))
        emit(TB_CAST, dy=9, cast=(draw_strollers, bx + 36, dict(t=t, variant=cust)))


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


def _scene_food_wok(emit, bx, pal, t, rng, pick=None):
    """The flared wok stall — a vendor tossing over the flame + a customer."""
    _scene_food(emit, bx, pal, t, 'wok', _food.STALLS['wok'][1], rng, pick=pick, cust_salt=65)


def _scene_food_duck(emit, bx, pal, t, rng, pick=None):
    """The roast-duck cabinet — birds on the hook rail, a cleaver at work."""
    _scene_food(emit, bx, pal, t, 'duck', _food.STALLS['duck'][1], rng, pick=pick, cust_salt=66)


def _scene_food_griddle(emit, bx, pal, t, rng, pick=None):
    """The flat griddle — batter raked into a crepe, a low sheet of steam."""
    _scene_food(emit, bx, pal, t, 'griddle', _food.STALLS['griddle'][1], rng, pick=pick, cust_salt=67)


def _scene_food_claypot(emit, bx, pal, t, rng, pick=None):
    """The clay-pot bank — five lids chattering over their own burners."""
    _scene_food(emit, bx, pal, t, 'claypot', _food.STALLS['claypot'][1], rng, pick=pick, cust_salt=68)


def _scene_food_roaster(emit, bx, pal, t, rng, pick=None):
    """The chestnut drum — the only turning machine on the street."""
    _scene_food(emit, bx, pal, t, 'roaster', _food.STALLS['roaster'][1], rng, pick=pick, cust_salt=69)


def _scene_food_ice(emit, bx, pal, t, rng, pick=None):
    """Shaved ice — no fire, no steam; the row's cold breath."""
    _scene_food(emit, bx, pal, t, 'ice', _food.STALLS['ice'][1], rng, pick=pick, cust_salt=70)


def _scene_food_boiler(emit, bx, pal, t, rng, pick=None):
    """The noodle boiler — strainer baskets dipping on a gantry rail."""
    _scene_food(emit, bx, pal, t, 'boiler', _food.STALLS['boiler'][1], rng, pick=pick, cust_salt=71)


# FIRE-TREE NIGHT's market strip: the festival's signature block. One scene
# slot becomes a ROW of stalls at market pitch — the thing a single-stall
# scene on a wider-than-screen lattice could never produce (measured 0.23
# stalls per frame at the old "peak"). Kinds are dealt with no repeat inside
# a strip, kiosk included, so a night shows every structure the town owns.
_STRIP_KINDS = ('steamer', 'cauldron', 'grill', 'wok', 'tea', 'kiosk',
                'duck', 'griddle', 'claypot', 'roaster', 'ice', 'boiler')
_STRIP_PITCH = 104
# The two crest sub-windows get a second, mid-deck rank — the "spine" that
# lifts the frame to the plan's 5+ structures.
_SPINE_WINS = ((0.715, 0.735), (0.765, 0.785))


def _eat_deal(bx, salt):
    """Stable walk-and-eat deal for one strip figure: ~half the festival crowd
    grazes as it strolls (night-market seating is sparse, so supper is a
    stroll). Hash-keyed to the strip + figure so it never re-rolls mid-screen
    and never disturbs the scene's rng sequence."""
    h = _mix32((int(bx) * 0x9E3779B1) ^ (salt * 0x85EBCA77))
    if (h & 0xFFFF) / 65535.0 >= 0.5:
        return None
    from game import festival as _fest
    return _fest.HAND_FOODS[(h >> 16) % len(_fest.HAND_FOODS)]


def draw_stroller_eating(surf, sx, pal, *, t=0.0, variant=0, prop='tanghulu'):
    """A strolling customer with a hand-held supper at chest height — the
    festival's dominant crowd behaviour, carried by a 3-9 px prop."""
    draw_strollers(surf, sx, pal, t=t, variant=variant)
    from game import festival as _fest
    _fest.draw_hand_food(surf, sx + 7, GROUND_Y - 10, _nightf(pal), prop)


def draw_vendor_stepout_cast(surf, sx, pal, *, t=0.0):
    """The market-pause pose under the standard far-cast drawer contract."""
    from game import festival as _fest
    _fest.draw_vendor_stepout(surf, sx, _nightf(pal), t, feet=GROUND_Y - 1)


def _scene_stall_strip(emit, bx, pal, t, rng, pick=None):
    """Four stalls at market pitch + their vendors, customers and critters —
    plus, at the crests, a spine rank behind the walk. One stall per strip is
    a THEATRE stall (its overlay performs over the structure), the queue forms
    at it (people queue for the show, not the food), and during the dragon
    parade the customers melt away while the vendors step out to watch."""
    p = _CUR_PHASE % 1.0
    deck = list(_STRIP_KINDS)
    rng.shuffle(deck)
    q_at = rng.randrange(4)          # ONE stall per strip grows a queue
    # The theatre stall + its act are dealt unconditionally so the rng
    # sequence never depends on live state (openness, the parade).
    th_at = rng.randrange(4)
    th_kind = rng.choice(('noodle', 'sugar', 'tanghulu'))
    parade = _wk.happening_active('festival_dragon')
    for i in range(4):
        x = bx + i * _STRIP_PITCH
        kind = deck[i]
        # Draw ALL of this stall's randoms up front, unconditionally — the
        # rng sequence must not depend on live state (openness thresholds,
        # the parade) or later slots would re-roll mid-screen.
        u = rng.random()
        r_cust = rng.random()
        r_crit = rng.random()
        crit_kind = rng.choice(('pigeons', 'cat', 'hen'))
        openness = _stall_openness(p, u)
        if openness <= 0.05:
            continue
        theatre = (i == th_at and kind != 'kiosk' and openness >= 0.80)
        if kind == 'kiosk':
            emit(TB_STRUCTURE, lambda s, x=x, op=openness:
                 draw_kiosk(s, x, pal, t=t, openness=op))
        else:
            emit(TB_STRUCTURE, lambda s, x=x, kind=kind, op=openness:
                 draw_food_stall(s, x, pal, t=t, kind=kind, openness=op))
        if theatre:
            # Food theatre: the overlay draws AFTER the stall structure, so
            # the performer works over the shipped counter.
            def _theatre(s, x=x, tk=th_kind):
                from game import festival as _fest
                _fest.THEATRE_OVERLAYS[tk](s, x, _nightf(pal), _CUR_T,
                                           base_y=GROUND_Y - 1)
            emit(TB_STRUCTURE, _theatre)
        if openness >= 0.30:
            if parade:
                # Market pause: the vendor is out front watching the dragon,
                # not behind the counter working.
                emit(TB_CAST, dy=9, cast=(draw_vendor_stepout_cast,
                                          x + _food.HALF_W + 6, dict(t=t)))
            elif not (theatre and th_kind in ('noodle', 'sugar')):
                # The noodle/sugar overlays bring their own performer — a
                # second vendor behind the same counter would double-cast it.
                vv = pick('vendor', 80 + i) if pick else 0
                emit(TB_CAST, dy=9, cast=(draw_vendor, x - 8, dict(t=t, variant=vv)))
        if openness >= 0.80 and not parade:
            if r_cust < 0.55:
                cust = pick('pedestrian', 84 + i) if pick else 0
                ek = _eat_deal(bx, 84 + i)
                emit(TB_CAST, dy=18,
                     cast=((draw_stroller_eating, x + 34,
                            dict(t=t, variant=cust, prop=ek)) if ek else
                           (draw_strollers, x + 34, dict(t=t, variant=cust))))
            if r_crit < 0.30:
                emit(TB_CAST, dy=18, cast=(draw_critter, x + 18,
                     dict(t=t, kind=crit_kind)))
            if i == (th_at if theatre else q_at):
                # The queue — three more waiting their turn behind the
                # customer spot, stepped through the walk's depth so the
                # line reads as a line, not a wall. It forms at the theatre
                # stall when the strip has one: people queue for the show.
                for qi, (qx, qdy) in enumerate(((48, 18), (61, 9), (73, 9))):
                    qv = pick('pedestrian', 88 + qi) if pick else 0
                    ek = _eat_deal(bx, 88 + qi)
                    emit(TB_CAST, dy=qdy,
                         cast=((draw_stroller_eating, x + qx,
                                dict(t=t, variant=qv, prop=ek)) if ek else
                               (draw_strollers, x + qx, dict(t=t, variant=qv))))
    # Spine rank: two more stalls on the walk's mid-deck, scaled by the depth
    # law and z-sorted into the front pass, so the crest frame reads as a
    # market with ROWS — the festival's "5 structures, 7 plumes" image.
    if any(a <= p < b for a, b in _SPINE_WINS):
        for j, xo in enumerate((52, 52 + 2 * _STRIP_PITCH)):
            kind = deck[(4 + j) % len(deck)]
            if kind == 'kiosk':
                kind = 'tea'          # the kiosk's pagoda roof is too tall mid-walk
            u2 = rng.random()

            def _spine(s, x=bx + xo, kind=kind, op=_stall_openness(p, u2)):
                from game import foreground_near_lane as _nl
                _nl._scaled_cast(s, draw_food_stall, x, _CUR_PAL, 1.28,
                                 feet_y=GROUND_Y + 21, kind=kind, openness=op)
            _zbuf.enqueue(GROUND_Y + 21, TB_STRUCTURE, _spine)

def draw_dog(surf, sx, pal, *, t=0.0, variant=0):
    """One street dog from the 9-strong 'dog' pool (animals_cast), feet on
    GROUND_Y, centred on `sx`, ambling/facing the scroll direction. `variant` is a
    resolved pool index; the near lane passes it as a kwarg into the bake cache."""
    v = _fv.get("dog", variant)
    if v is None:
        return
    if _CUR_SNOW >= 0.35:
        # every dog bundles into its winter self (breath puffs and all)
        _wkit.draw_winter_dog(surf, sx, GROUND_Y - 1, _nightf(pal), t,
                              variant=variant, phase=variant * 0.61)
        return
    _animals.draw_dog(surf, sx, GROUND_Y - 1, v, _nightf(pal), t)


def draw_critter(surf, sx, pal, *, t=0.0, kind="pigeons"):
    """One street critter (pigeons/hen/cat/duck/crane/piglet/rabbit) from the
    'critter' pool, feet on GROUND_Y, centred on `sx`. Placed near the food
    stalls so the market reads as alive (birds pecking scraps, a market cat)."""
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
# Role pools cover the ENTIRE 30-design greenery registry exactly once, classed
# by measured rendered height (tall ≥34 px centres / 27–33 px flankers / <27 px
# ground fillers) so every authored plant is actually placed somewhere.
_GRN_TALL = (1, 2, 3, 6, 9, 10, 12, 13, 17, 18, 19, 21, 22, 25, 26, 29)
_GRN_SHORT = (0, 4, 5, 8, 11, 16, 20, 23)
# 7 (trough/vine) and 24 (bamboo/vine) cascade 12-15 px BELOW their soil line,
# so as back fillers they'd paint past figures that sort in front of them —
# they live in the front-flanker pool instead, where the spill points at the
# camera.
_GRN_LOW = (14, 15, 27, 28)
_GRN_SPILL = (7, 24)


def _grn_pick(pool, k, salt):
    # Avalanche hash, NOT a linear stride: (k*salt+salt) % n marched the pool in
    # strict order, so planting beds read as a repeating loop of the same few
    # plants. Still pure in (k, salt) — no flicker — and adjacent beds never
    # place identical twins (a hash collision with bed k-1 is nudged aside).
    n = len(pool)
    h = _mix32((k * 0x9E3779B1) ^ (salt * 0x85EBCA77))
    i = h % n
    if n > 1 and (_mix32(((k - 1) * 0x9E3779B1) ^ (salt * 0x85EBCA77)) % n) == i:
        i = (i + 1 + (h >> 8) % (n - 1)) % n
    return pool[i]


def _grn_at(surf, x, idx, dy):
    """One pooled plant with its soil line sunk `dy` into the walk. Greenery
    holds its daytime look the whole cycle: greenery_cast's night retint cooled
    the foliage to a muddy blue-green after dusk, which read worse than just
    leaving the plants their clean day colour."""
    v = _fv.get("greenery", idx)
    if v is not None:
        _green.draw_greenery(surf, x, GROUND_Y - 1 + dy, v, 0.0, idx * 2.39996)


def _bed_layout(k):
    """A planting bed's plants as (pool_idx, x_off, dy) — deterministic in `k`.
    dy staggers the rows through the walk's depth (back filler on the kerb,
    front flanker into the walk), and each plant enqueues on its own feet line
    so the cast can pass BETWEEN the bed's rows. The front role draws from the
    flankers PLUS the two cascading vines (their spill points at the camera —
    as back fillers it painted over anything sorted in front of them)."""
    triad = (k % 2 == 0)
    spread = 23 if (k % 3) else 16
    front = _GRN_SHORT + _GRN_SPILL
    if triad:
        return ((_grn_pick(_GRN_LOW, k, 7), spread - 5, 0),
                (_grn_pick(_GRN_TALL, k, 1), -2, 3),
                (_grn_pick(front, k, 5), -spread, 10))
    return ((_grn_pick(_GRN_TALL, k, 1), -spread // 2, 1),
            (_grn_pick(front, k, 5), spread // 2, 8))


def _bed_base(surf, sx, k, pal):
    """The bed itself — a soil rectangle with a stone edging spanning the
    plants' footprint. A kept garden reads from its edge, not its plants; the
    rectangle also visually ties the depth-staggered rows into ONE bed."""
    night = _nightf(pal)
    spread = 23 if (k % 3) else 16
    left = sx - spread - 10
    w = spread * 2 + 18
    soil = _mix((86, 64, 46), (52, 56, 76), 0.4 * night)
    edge = _mix((168, 158, 142), (92, 98, 118), 0.4 * night)
    top = GROUND_Y - 2
    pygame.draw.rect(surf, soil, (left, top, w, 13))
    pygame.draw.rect(surf, _shade(soil, -14), (left, top, w, 13), 1)
    # stone edging along the front lip, the "kept" cue
    pygame.draw.rect(surf, edge, (left - 1, top + 12, w + 2, 2))
    pygame.draw.rect(surf, _shade(edge, -22), (left - 1, top + 13, w + 2, 1))


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
    emit(TB_CAST, dy=9, cast=(draw_dog, bx + 66, dict(t=t, variant=dv)))
    emit(TB_CAST, dy=18, cast=(draw_critter, bx + 96,
                               dict(t=t, kind=rng.choice(('pigeons', 'cat', 'hen',
                                                          'duck', 'crane', 'rabbit')))))

def _scene_lamplighter(emit, bx, pal, t, rng, pick=None):
    """A lamplighter kindling the street lanterns at dusk — on the back kerb,
    where the lamps stand."""
    emit(TB_CAST, dy=0, cast=(draw_lamplighter, bx, dict(t=t)))

def _scene_dawn_setup(emit, bx, pal, t, rng, pick=None):
    """Vendors assembling the morning market. Through the evening setup and
    the rain, some slots also park the draped dragon-head handcart beside the
    work — the festival's covered plant, arriving long before it dances."""
    r_cart = rng.random()            # dealt unconditionally: the rng sequence
                                     # must not depend on the phase window
    emit(TB_FIXTURE, lambda s: draw_market_setup(s, bx, pal, t=t), dy=3)
    p = _CUR_PHASE % 1.0
    if 0.43 <= p < 0.680 and r_cart < 0.20:
        def _plant(s):
            from game import festival as _fest
            _fest.draw_draped_cart(s, bx + 58, _nightf(pal), _CUR_T,
                                   feet=GROUND_Y - 1)
        emit(TB_FIXTURE, _plant, dy=6)

def _scene_vendor(emit, bx, pal, t, rng, pick=None):
    """A songbird-cage seller working the stand."""
    vv = pick('vendor', 33) if pick else 0
    emit(TB_STRUCTURE, lambda s: draw_birdcage_stand(s, bx, pal, t=t))
    emit(TB_CAST, dy=9, cast=(draw_vendor, bx + 12, dict(t=t, variant=vv)))

def _scene_quiet(emit, bx, pal, t, rng, pick=None):
    """The temple elder pausing — a quiet, near-empty-street beat."""
    ev = pick('elder', 14) if pick else 0
    emit(TB_CAST, dy=9, cast=(draw_old_man, bx + 30, dict(t=t, variant=ev)))


def _draw_pigeon_flush(surf, sx, pal, k):
    """Seven pigeons burst off the paving and fan up-and-right — the one moment
    street birds fly. Held inside the band (never past y=562)."""
    night = _nightf(pal)
    body = _retint_person((88, 92, 104), night)
    wing = _retint_person((132, 136, 148), night)
    for i in range(7):
        lift = k * (18 + i * 3.5)
        px = sx - 12 + i * 5 + int(k * (26 + i * 4))
        py = max(563, int(GROUND_Y - 5 - lift))
        flick = int(k * 24 + i) % 2
        pygame.draw.rect(surf, body, (px, py, 2, 2))
        if flick:
            pygame.draw.line(surf, wing, (px - 1, py), (px + 2, py - 1), 1)


def _happenings(surf, scroll, pal, phase, t):
    """The once-per-day charming beats (weekend-scale, never epic). Each fires
    the first time its window opens, plays out planted at a latched world-x,
    and never repeats this run."""
    if calm_now():
        return
    h = _wk.happening('pigeon_flush', (0.06, 0.28), phase, t, 2.5,
                      anchor=scroll + W * 0.62)
    if h:
        k, wx = h
        sx = int(wx - scroll)
        if -40 < sx < W + 40:
            _zbuf.enqueue(GROUND_Y - 1, TB_CAST,
                          lambda s, k=k, sx=sx: _draw_pigeon_flush(s, sx, pal, k))
    h = _wk.happening('noodles_dog', (0.70, 0.78), phase, t, 4.0,
                      anchor=scroll + W * 0.72)
    if h:
        # a spill at a stall corner; a dog arrives within seconds; the dog wins
        k, wx = h
        sx = int(wx - scroll)
        if -60 < sx < W + 60:
            spill = _retint_person((214, 178, 120), _nightf(pal))
            dog_x = int(sx - 52 + min(1.0, k * 1.6) * 44)
            bob = 1 if (k > 0.62 and int(t * 6) % 2) else 0
            _zbuf.enqueue(GROUND_Y + 8, TB_CAST, lambda s, sx=sx, spill=spill: (
                pygame.draw.rect(s, spill, (sx - 2, GROUND_Y + 6, 4, 2))))

            def _hdog(s, dog_x=dog_x, bob=bob):
                from game import foreground_near_lane as _nl
                _nl._scaled_cast(s, draw_dog, dog_x, pal, 1.0 + 0.0134 * 9,
                                 feet_y=GROUND_Y + 8, t=t, variant=2 + bob)
            _zbuf.enqueue(GROUND_Y + 8, TB_CAST, _hdog)


def draw_sweeper_cast(surf, sx, pal, *, t=0.0, ph=0.0):
    """Signature adapter: the weekend kit's sweeper under the standard far-cast
    drawer contract, so it rides the depth law's bake like everyone else."""
    _wkit.draw_sweeper(surf, sx, GROUND_Y - 1, _nightf(pal), t, phase=ph, pal=pal)


def _scene_sweeper(emit, bx, pal, t, rng, pick=None):
    """The first inhabitant of the morning: the sweeper working a besom over
    yesterday's street, pile inching ahead of the twigs."""
    ph = rng.random() * 1.3
    emit(TB_CAST, dy=9, cast=(draw_sweeper_cast, bx, dict(t=t, ph=round(ph, 2))))


def _scene_bench(emit, bx, pal, t, rng, pick=None):
    """The temple elder beside a bench with a seated companion."""
    night = _nightf(pal)
    comp = tuple(_retint_person(c, night) for c in
                 ((215, 85, 100), (175, 50, 70), (80, 50, 30)))
    seat_y = (GROUND_Y - 27) + 19            # match _Bench.draw seat geometry

    def _bench(s):
        bench = _stepped(_Bench, pal, 20, bx)
        bench._blit_sprite(s)
    emit(TB_FIXTURE, _bench, dy=2)
    ev = pick('elder', 15) if pick else 0
    # The seated companion shares the bench's depth so it stays ON the seat.
    emit(TB_CAST, lambda s: _draw_bench_person(s, bx + 8, seat_y - 8, *comp, night=night),
         dy=2)
    emit(TB_CAST, dy=9, cast=(draw_old_man, bx + 44, dict(t=t, variant=ev)))

def _scene_stroll(emit, bx, pal, t, rng, pick=None):
    """Two strolling adults from the variety pool + a varied elder on a slow walk."""
    v1 = pick('pedestrian', 11) if pick else 0
    v2 = pick('pedestrian', 12) if pick else 0
    ev = pick('elder', 13) if pick else 0
    emit(TB_CAST, dy=0, cast=(draw_strollers, bx - 7, dict(t=t, variant=v1)))
    emit(TB_CAST, dy=18, cast=(draw_strollers, bx + 9, dict(t=t, variant=v2)))
    emit(TB_CAST, dy=9, cast=(draw_old_man, bx + 48, dict(t=t, variant=ev)))

def _scene_rest(emit, bx, pal, t, rng, pick=None):
    """A napper on a mat."""
    emit(TB_CAST, dy=9, cast=(draw_napper, bx, dict(t=t)))

def _scene_campfire(emit, bx, pal, t, rng, pick=None):
    """A campfire with cozy pool adults + kids gathered (lit by the drawer at night)."""
    v1 = pick('pedestrian', 21) if pick else 0
    v2 = pick('pedestrian', 22) if pick else 0
    kv = pick('kid', 23) if pick else 0
    emit(TB_FIXTURE, lambda s: draw_campfire(s, bx, pal, t=t), dy=4)
    emit(TB_CAST, dy=9, cast=(draw_strollers, bx + 50, dict(t=t, variant=v1)))
    emit(TB_CAST, dy=18, cast=(draw_strollers, bx + 64, dict(t=t, variant=v2)))
    emit(TB_CAST, dy=9, cast=(draw_kids, bx + 100, dict(t=t, n=2, variant=kv)))

def _scenarios(surf, w, scroll, pal, t, roster, x0=40):
    """Place the beat's scene roster at world-x slots, scrolling at world speed.

    Legacy gallery path (PHASES_R17): scenes now EMIT their sub-objects, so give
    them an emit that paints immediately in submission order — no depth buffer."""
    def _emit(_tier, fn=None, dy=0, cast=None):
        if cast is not None:
            drawer, x, kw = cast
            drawer(surf if not dy else _sunk(surf, min(dy, 12)), x, pal, **kw)
            return
        fn(surf if not dy else _sunk(surf, dy))
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
    for xl, xr, _k in sp._garland_spans(scroll, w, period=149, x0=20):
        draw_prayer_flags(surf, int(xl), GROUND_Y - 118, int(xr), GROUND_Y - 116, n=5)
    _scenarios(surf, w, scroll, pal, t, (_scene_market, _scene_pastoral), x0=40)


def phase_golden(surf, w, gy, h, scroll, pal, t):
    """GOLDEN HOUR · lamp posts up + a lantern garland; bench/market scenes."""
    global _CUR_PAL
    _CUR_PAL = pal
    _ground_furniture(surf, w, scroll, pal)
    sp._draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 96,
                             period=149, sag=22, per_span=2)
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
    for sx, k in sp._world_xs(scroll, w, 251, x0=18):
        sp._draw_lamp_post(surf, sx, pal, style='ornate', height=96, lantern='red')
    for sx, k in sp._world_xs(scroll, w, 253, x0=152):
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
# FAIR-WEATHER intent, authored against the REMAPPED biome keyframes (biome.py
# shifts every keyframe by DAY_EXTRA/NIGHT_BORROW, so window literals here must
# match the shifted day, not the pre-extension one). The weather crowd factor
# multiplies on top exactly once — never pre-dip these keys for weather, or the
# storm empties the street twice. The curve deliberately KEEPS RISING through
# the rain (the market is still being set up under it), so when the rain ends
# the crowd floods back instead of ramping; the night-market crest sits in the
# clear dark window between rain-end and the snow squall.
_POP_KEYS = [
    (0.000, 0.30),  # street opening — calm mandate window
    (0.030, 0.34),
    (0.055, 0.58),  # market waking
    (0.090, 0.86),  # MORNING MARKET peak
    (0.130, 0.78),
    (0.160, 0.55),  # winding down (day-hold expires here)
    (0.215, 0.34),  # lazy midday
    (0.280, 0.31),  # the long middle — authored daytime floor
    (0.309, 0.40),  # golden hour; people come back out
    (0.330, 0.30),  # clown-gauntlet calm dip (clamped live by the event too)
    (0.375, 0.44),  # the refill wave
    (0.396, 0.62),  # median run ends here — warm, full, golden
    (0.416, 0.66),  # sunset; night-market setup begins under it
    # The rain is the day's LULL, not a busy street wearing umbrellas. This
    # stretch used to climb (0.60 -> 0.90) straight through the storm, which
    # cancelled the weather multiplier and left the deck as full as golden
    # hour for all but ~16 s of the ~75 s of rain. It now falls with the
    # weather and climbs back out, so the festival is arrived at rather than
    # merely continued.
    (0.470, 0.58),  # the sky goes heavy — shoppers start heading in
    (0.483, 0.46),  # first drops — weather factor takes over from here
    (0.510, 0.32),  # drizzle settles in; the browsing crowd gives up
    (0.560, 0.24),  # only the setup crew and the tea stall hold out
    (0.629, 0.22),  # storm peak — the open deck is down to the shelterers
    (0.660, 0.32),  # the rain eases; the first few venture back
    (0.680, 0.52),  # rain done — lanterns lit, the crowd starts returning
    (0.700, 0.78),  # filling fast now
    (0.724, 1.00),  # FIRE-TREE NIGHT crest #1 (clear, dark, drying)
    (0.755, 0.95),
    (0.775, 0.98),  # crest #2 — the food-theatre spine
    (0.790, 0.85),  # the breath, then the parade crowd
    (0.820, 0.72),  # afterglow — first flakes land in the dragon's tail
    (0.840, 0.34),  # closing under the squall
    (0.875, 0.10),  # small hours
    (0.900, 0.07),  # the floor
    (0.924, 0.10),  # sunrise begins
    (0.955, 0.24),  # squall gone; sweepers + the first tea stall
    (0.985, 0.36),  # early vendors; the chest approaches
    (1.000, 0.30),  # wrap — matches phase 0.000 exactly
]

def _interp_keys(keys, p):
    for i in range(len(keys) - 1):
        a, va = keys[i]
        b, vb = keys[i + 1]
        if a <= p <= b:
            f = (p - a) / (b - a) if b > a else 0.0
            return va + (vb - va) * f
    return keys[-1][1]

def _population(phase):
    return _interp_keys(_POP_KEYS, phase % 1.0)


# ── world→street signals + the calm mandates ─────────────────────────────────
# Gameplay state the street reacts to (clown gauntlet, newbie opening, score…),
# pushed once per frame by scenes via foreground.set_world_signals — the same
# module-state idiom as _CUR_*/set_crowd. The street must never read gameplay
# objects directly.
_SIG = {}
_CALM_UNTIL = -1.0   # biome_time until which the post-gauntlet hold keeps the hush


def set_signals(**kw):
    _SIG.update(kw)


def signal(name, default=None):
    return _SIG.get(name, default)


def reset_run():
    """Per-run street state reset (called from World.__init__)."""
    global _CALM_UNTIL
    _CALM_UNTIL = -1.0
    _SIG.clear()


def street_calm(t):
    """The calm mandates: the whole strip goes quiet during the clown gauntlet
    (plus a 2 s hold after it clears, so the refill reads as relief rather than a
    snap) and through the newbie opening. Mutates the hold timer — call once per
    frame from draw_promenade; everyone else reads calm_now()."""
    global _CALM_UNTIL
    if _SIG.get('clown_active'):
        _CALM_UNTIL = t + 2.0
        return True
    return t < _CALM_UNTIL or bool(_SIG.get('newbie_calm'))


def calm_now():
    return (bool(_SIG.get('clown_active') or _SIG.get('newbie_calm'))
            or _CUR_T < _CALM_UNTIL)


# ── light-spot collector (for the wet-paving reflections) ────────────────────
# Every lit hung/standing light on the street reports itself here per frame;
# the ground-weather painter mirrors LAST frame's spots as vertical smears in
# the wet sheen (one frame of lag at 160 px/s is under 3 px — invisible).
LIGHT_SPOTS: list = []
_CUR_SCROLL = 0.0


def add_light_spot(screen_x, color):
    LIGHT_SPOTS.append((screen_x + _CUR_SCROLL, color))


def street_density(phase, t):
    """THE density authority — the one place the cast curve, run fill, weather
    factor and calm clamp combine. Promenade, near lane and the crowd sim all
    read this, so the street can never double-dip a multiplier."""
    pop = _population(phase)
    if calm_now():
        pop = min(pop, 0.30)
    return pop * _run_fill(t) * _weather_crowd_factor(phase)

_FILL_SECONDS = 7.0   # the market "opens" over the first few seconds of a run

def _run_fill(t):
    x = max(0.0, min(1.0, t / _FILL_SECONDS))
    return x * x * (3.0 - 2.0 * x)   # smoothstep: street starts empty, fills in

def _mix32(h):
    """Finalising avalanche (xorshift-multiply): a bare k*CONST is an arithmetic
    ramp in k, so thresholding or reducing it produces evenly-spaced combs and
    strict cycles — the 'scattered' street turns into a metronome. Mixing kills
    the ramp while staying pure in the inputs (no flicker)."""
    h &= 0xFFFFFFFF
    h ^= h >> 15
    h = (h * 0x2C1B3C6D) & 0xFFFFFFFF
    h ^= h >> 12
    h = (h * 0x297A2D39) & 0xFFFFFFFF
    h ^= h >> 15
    return h

def _slot_on(k, salt, density):
    """Stable per-slot inclusion gate: hash (slot index, salt) to [0,1) and admit
    the slot iff that fixed threshold is below `density`. Because the threshold is
    keyed to the WORLD slot (not the frame), a slot pops in exactly once as the
    density curve rises and never flickers — and its x never moves."""
    h = _mix32((k * 0x9E3779B1) ^ (salt * 0x85EBCA77)) & 0xFFFF
    return (h / 65535.0) < density

def _slot_pick(k, n):
    """Stable per-slot choice in [0, n): which roster entry a world slot uses. Keyed
    to the slot index so the choice is identical as the slot scrolls (no flicker)."""
    return (_mix32(k * 0x9E3779B1) >> 8) % n

# Decoration density is PHASE-ONLY and decoupled from the cast curve: a street
# stripped of people at 3 a.m. keeps its dressing (a dressed, empty street reads
# as late-night; a bare one reads as unbuilt). Shape: steady by day, climbs as
# the night market is dressed at sunset, full through the market AND the small
# hours (nobody takes bunting down at 3 a.m.), back to the day look at sunrise.
_DECOR_KEYS = [
    (0.000, 0.45), (0.157, 0.45), (0.309, 0.42), (0.416, 0.42),
    (0.483, 0.55), (0.537, 0.62), (0.644, 0.72), (0.900, 0.72),
    (0.940, 0.55), (1.000, 0.45),
]

def _furn_density(phase):
    """Fixture density (planters/cairns/greenery). PHASE-ONLY — NOT multiplied by
    `_run_fill` or the cast curve — so the static deck dressing is present from
    t=0 and never flickers."""
    return _interp_keys(_DECOR_KEYS, phase % 1.0)

def _roster_for(phase):
    """The cast vocabulary by time of day. The early-Day window is the FOOD-MARKET
    rush (busy, market-heavy); the rest of the day is light (strolling/quiet beats)
    until the NIGHT festival. Pre-dawn is near-empty. Bigger, more varied rosters
    (4–5 options) + the no-repeat rule in _place_scenarios kill the short loop."""
    p = phase % 1.0
    if p < 0.157:                      # MORNING MARKET (the run opener; day-hold)
        return (_scene_food_grill, _scene_food_soup, _scene_market, _scene_food_steamer,
                _scene_food_tea, _scene_food_griddle, _scene_food_claypot,
                _scene_food_boiler, _scene_dawn_setup, _scene_vendor)
    if p < 0.309:                      # THE LONG MIDDLE — lazy, green, quiet
        return (_scene_pastoral, _scene_vendor, _scene_quiet, _scene_stroll)
    if p < 0.416:                      # GOLDEN STROLL — pairs, benches, warmth
        return (_scene_stroll, _scene_pastoral, _scene_quiet, _scene_bench)
    if p < 0.483:                      # LAMPS & SETUP — the market being assembled
        return (_scene_lamplighter, _scene_dawn_setup, _scene_stroll, _scene_vendor)
    if p < 0.680:                      # THE RAIN — setup pushes on; tea never closes
        return (_scene_food_tea, _scene_dawn_setup, _scene_stroll, _scene_rest)
    if p < 0.820:                      # FIRE-TREE NIGHT — the festival window
        return (_scene_stall_strip, _scene_food_grill, _scene_food_soup,
                _scene_food_steamer, _scene_food_tea, _scene_food_wok,
                _scene_food_duck, _scene_food_griddle, _scene_food_claypot,
                _scene_food_roaster, _scene_food_ice, _scene_food_boiler,
                _scene_market, _scene_stroll, _scene_bench)
    if p < 0.924:                      # SMALL HOURS — near-empty, braziers warm
        return (_scene_quiet, _scene_rest, _scene_campfire)
    return (_scene_food_tea, _scene_sweeper, _scene_quiet, _scene_vendor)  # FIRST LIGHT — tea + brooms first

def _overhead_busy(world_x, phase):
    """True unless the owning block's personality is one of the quiet/green/works
    lows. The hanging decorations (bunting, lantern garland) used to draw
    over every stretch of sidewalk unconditionally, with no per-block variation
    at all — this gives quiet blocks a real gap in the overhead ornament, the
    same way `foreground_weekend` already varies cast density block by block."""
    return _wk.personality(_wk.block_at(world_x), phase) not in _wk._LOW


def _dressing(surf, w, scroll, pal, phase):
    """Phase-gated street fixtures in one pass (glow follows the palette). Lamps +
    lanterns are installed for the evening and stay as fixtures; the prayer-flag
    bunting is the daytime look."""
    p = phase % 1.0
    # Garland strands are continuous, so each SPAN latches its window membership at
    # entry: the strand scrolls in/out span-by-span instead of the whole row
    # flashing at the phase-window edge.
    bunting_win = (p >= 0.924 or p < 0.416)                      # daytime bunting
    for xl, xr, k in sp._garland_spans(scroll, w, period=149, x0=20):
        if sp._slot_latch(('bunting',), k, lambda k=k: (
                bunting_win and _overhead_busy(20 + k * 149, phase))):
            draw_prayer_flags(surf, int(xl), GROUND_Y - 118,
                              int(xr), GROUND_Y - 116, n=5)
    sp._latch_prune(('bunting',))
    # Exactly one hanging layer is possible at any hour: this window is the
    # complement of the bunting's, so the street wears cloth flags by day and
    # paper lanterns by night, never both. The lanterns go up as the market is
    # set up (0.416) and come down at first light, the way the lamp posts do —
    # a lit paper lantern at noon read as clutter, not atmosphere.
    lantern_win = (0.416 <= p < 0.924)
    sp._draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 97,
                             period=127, sag=23, per_span=3,
                             span_gate=lambda k: sp._slot_latch(('lantgar',), k,
                                 lambda k=k: (lantern_win
                                              and _overhead_busy(12 + k * 127, phase))))
    sp._latch_prune(('lantgar',))
    # A SECOND lantern row interleaves through the night market only, on the
    # same festival stall-row blocks the lantern arch itself gates to — the
    # overhead ceiling doubles where the market actually is, not everywhere.
    market_win = (0.680 <= p < 0.840)
    sp._draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 112,
                             period=127, sag=20, per_span=4, x0=63,
                             span_gate=lambda k: sp._slot_latch(('lantgar2',), k,
                                 lambda k=k: (market_win and _wk.personality(
                                     _wk.block_at(63 + k * 127), phase) == _wk.STALL_ROW)))
    sp._latch_prune(('lantgar2',))
    # Lamp posts: a discrete world-slot row. Latch each post's "is the evening
    # window open?" at entry so the row scrolls IN when dusk arrives and scrolls
    # OUT after dawn, instead of the whole on-screen row blinking at the window edge.
    lamp_win = (0.20 <= p < 0.924)   # installed by golden, gutter out at sunrise
    fy = GROUND_Y - 1
    lamps_lit = _nightf(pal) > 0.25
    for sx, k in sp._world_xs(scroll, w, 251, x0=18):
        on, lv = sp._slot_latch(('lampR',), k, lambda k=k: (
            lamp_win, _prop_latch('prop_lamp', k, 31)))
        if on:
            _zbuf.enqueue(fy, TB_STRUCTURE, lambda s, sx=sx, lv=lv: draw_prop_lamp(
                s, sx, pal, t=_CUR_T, variant=lv))
            if lamps_lit:
                add_light_spot(sx, (250, 210, 140))
    sp._latch_prune(('lampR',))
    # Gold row shares the red row's 251 lattice at the even half-offset (143)
    # so both lamp gaps are ~125 px and each holds a tree slot with a fixed
    # ≥62 px clearance — the old 253 period drifted through every phase
    # against the trees, and the old 185 offset left the short gap treeless.
    for sx, k in sp._world_xs(scroll, w, 251, x0=143):
        on, lv = sp._slot_latch(('lampG',), k, lambda k=k: (
            lamp_win, _prop_latch('prop_lamp', k, 32)))
        if on:
            _zbuf.enqueue(fy, TB_STRUCTURE, lambda s, sx=sx, lv=lv: draw_prop_lamp(
                s, sx, pal, t=_CUR_T, variant=lv))
            if lamps_lit:
                add_light_spot(sx, (250, 210, 140))
    sp._latch_prune(('lampG',))
    _festival_dressing(surf, w, scroll, pal, p)


def _festival_dressing(surf, w, scroll, pal, p):
    """FIRE-TREE NIGHT's block-anchored fixtures, all on the 900 px block
    lattice: the lantern arch gating each festival stall-row block, the dark
    iron-flower scaffold standing in the rain (the show's set, seen before it
    ever lights), and the small-hours residue (the cold smoking rig, the
    scorch fan, the swept masks). Slot-latched so nothing blinks at a phase
    edge — fixtures only ever scroll in and out."""
    fy = GROUND_Y - 1
    night = _nightf(pal)
    # A gateway arch at each festival stall-row block's entry edge.
    arch_win = (0.680 <= p < 0.820)
    for sx, k in sp._world_xs(scroll, w, _wk.BLOCK_PX, x0=72, margin=110):
        on = sp._slot_latch(('arch',), k, lambda k=k: (
            arch_win and _wk.personality(k, _CUR_PHASE) == _wk.STALL_ROW))
        if on:
            def _arch(s, sx=sx):
                from game import festival as _fest
                _fest.draw_lantern_arch(s, sx, night, _CUR_T)
            _zbuf.enqueue(fy, TB_STRUCTURE, _arch)
    sp._latch_prune(('arch',))
    # The plant: the scaffold stands dark and draped through the rain, roughly
    # one block in three, so the player has seen the fire show's set before it
    # lights.
    plant_win = (0.483 <= p < 0.680)
    for sx, k in sp._world_xs(scroll, w, _wk.BLOCK_PX, x0=402, margin=110):
        on = sp._slot_latch(('firerig',), k, lambda k=k: (
            plant_win and _mix32((k * 0xA24BAED4) ^ 0x1F7) % 3 == 0))
        if on:
            def _rig(s, sx=sx):
                from game import festival as _fest
                _fest.draw_scaffold(s, sx, night, _CUR_T, state='bare')
            _zbuf.enqueue(fy, TB_STRUCTURE, _rig)
    sp._latch_prune(('firerig',))
    # The residue: the festival hands the street back with evidence, not a
    # fade — a cold smoking rig with a fresh scorch fan and swept masks on
    # some blocks, a thinned-out speckle field with one mask on others.
    res_win = (0.820 <= p < 0.924)
    for sx, k in sp._world_xs(scroll, w, _wk.BLOCK_PX, x0=402, margin=110):
        on = sp._slot_latch(('resid',), k, lambda k=k: (
            0 if not res_win else
            {0: 1, 1: 2, 2: 3}.get(_mix32((k * 0xC13FA9A9) ^ 0x9E3) % 8, 0)))
        if on:
            def _res(s, sx=sx, mode=on):
                from game import festival as _fest
                if mode == 1:
                    _fest.draw_scorch_fan(s, sx, night, decay=0.0)
                    _fest.draw_scaffold(s, sx, night, _CUR_T, state='cold')
                    _fest.draw_dropped_mask(s, sx + 54, night)
                    _fest.draw_dropped_mask(s, sx - 62, night, flipped=True)
                elif mode == 2:
                    _fest.draw_scorch_fan(s, sx, night, decay=0.55)
                    _fest.draw_dropped_mask(s, sx + 10, night)
                else:
                    _fest.draw_scorch_fan(s, sx, night, decay=0.9)
            _zbuf.enqueue(fy, TB_FIXTURE, _res)
    sp._latch_prune(('resid',))

def _place_scenarios(surf, w, scroll, pal, t, roster, density, x0=40):
    """Place the time-appropriate cast at FIXED world-x slots, THINNED by `density`:
    each slot is admitted only with probability `density` (seeded by slot index so
    it's stable as it scrolls). The spacing is constant — only the per-slot gate
    changes with density — so a figure pops in once instead of sliding when the
    crowd fills in. Off-peak the street is mostly open paving; at night it fills."""
    if not roster:
        return
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
            # The block layer: this slot's world block multiplies the day density
            # (a stall row runs hot, a green walk runs sparse) and reorders the
            # hour's roster to the block's taste — the spatial ebb and flow.
            wx = k * _SCENARIO_PERIOD + x0
            # A crossing is busy because people cross there and a stall row
            # because people shop there — in a downpour they do neither, so
            # the block multiplier (up to 2.05x) relaxes toward 1.0 as the
            # rain builds. Without this the emptiest stretch of the storm
            # still had one busy block re-inflating an effective 0.15 to 0.29.
            bm = _wk.density_mult(wx, _CUR_PHASE)
            wet = min(1.0, _CUR_RAIN)
            if wet > 0.0 and bm > 1.0:
                bm = 1.0 + (bm - 1.0) * (1.0 - wet)
            d_here = min(1.0, density * bm)
            if r.random() > d_here:         # stable per-slot inclusion
                return None
            roster_b = _wk.filter_roster(wx, _CUR_PHASE, roster)
            nb = len(roster_b)
            idx = _slot_pick(k, nb)
            if nb > 1 and idx == _slot_pick(k - 1, nb):
                idx = (idx + 1) % nb
            jit = (((k * 0x85EBCA77) >> 13) % 97) - 48
            # Freeze the day-arc beat + weather bucket at slot ENTRY so the cast's
            # variant choices stay fixed for the whole on-screen traversal (a slot
            # that entered in clear weather keeps its clear dress even if rain
            # starts while it crosses; new slots entering in rain get brollies).
            beat0 = _fv.beat_for_phase(_CUR_PHASE)
            wb0 = _fv.weather_bucket(_CUR_RAIN, _CUR_SNOW)
            return (roster_b[idx], jit, beat0, wb0)
        dec = sp._slot_latch(row, k, _decide)
        if dec is not None:
            scene_fn, jit, beat0, wb0 = dec
            # Recreate the per-slot RNG and consume the inclusion draw so the scene's
            # internal variety matches the pre-latch behaviour exactly.
            r = random.Random((k * 0x9E3779B1) & 0xFFFFFFFF)
            r.random()
            # Each scene enqueues its sub-objects with a per-figure depth.
            # Fixtures/structures pass an opaque `fn` and sink by translation
            # (`dy` via the shifted subsurface). CAST figures instead pass
            # cast=(drawer, x, kwargs): their authored dy quantises to the
            # band's tier pitch, shifted ±1 tier per slot so two instances of
            # a scene never share one depth arrangement, and figures sunk past
            # the back tier bake through the shared depth law's scale — walking
            # forward means growing, not just dropping. Every cast figure gets
            # a contact shadow so it stays separable from the paving.
            tshift = (_mix32(k * 0x51ED2701) % 3) - 1

            def _emit(tier, fn=None, dy=0, cast=None, tshift=tshift):
                if cast is not None:
                    drawer, x, kw = cast
                    d_eff = _FAR_TIER_DY[max(0, min(2, _far_tier(dy) + tshift))]
                    fyc = GROUND_Y - 1 + d_eff
                    sc = 1.0 + 0.0134 * d_eff

                    def _draw(s, drawer=drawer, x=x, kw=kw, fyc=fyc, sc=sc):
                        # _scaled_cast draws the contact shadow + aerial dim +
                        # outline itself; the back kerb goes through the same
                        # bake at scale 1.0 so the band's value ladder has no
                        # native/baked seam.
                        from game import foreground_near_lane as _nl
                        _nl._scaled_cast(s, drawer, x, _CUR_PAL, sc,
                                         feet_y=fyc, **kw)
                    _zbuf.enqueue(fyc, tier, _draw)
                    return
                if dy:
                    _zbuf.enqueue(GROUND_Y - 1 + dy, tier,
                                  lambda s, f=fn, d=dy: f(_sunk(s, d)))
                else:
                    _zbuf.enqueue(GROUND_Y - 1, tier, fn)
            # Stable per-figure variant picker for this slot, frozen to the entry
            # beat/weather — scenes call pick(family, salt) for each figure they
            # place (family one of 'pedestrian'/'kid'/'elder'/'vendor').
            def _pick(family, salt, k=k, beat0=beat0, wb0=wb0):
                return _fv.select_variant(family, _fv.slot_seed(k, salt), beat0, wb0)
            scene_fn(_emit, bx + jit, pal, t, r, _pick)
    sp._latch_prune(row)

# ── the IRON FLOWER — the fire show, once per festival night ─────────────────
# The rig rides the dragon's own parade-drift mechanic (+0.55x scroll), so the
# 2.5 s burst cycle fits three times inside one dwell instead of once: the
# player gets BURST -> DARK BEAT -> BURST rather than one burst glimpsed on
# the way past. It draws HERE, in the promenade pass, because the sparks
# belong behind the pillars, the coins and the bird — the near lane only adds
# the spark-watch crowd in front.
_FIRE_BEAT = (0.706, 0.727)
_FIRE_DUR = 8.0


def _festival_fire(surf, scroll, pal, phase, t, density):
    from game import festival as _fest
    p = phase % 1.0
    if not (0.680 <= p < 0.820):
        return
    if density <= 0.20 or calm_now():
        _fest.set_fire_state(None)
        return
    h = _wk.happening('festival_fire', _FIRE_BEAT, phase, t, _FIRE_DUR)
    if not h:
        _fest.set_fire_state(None)
        return
    k, _a = h
    show_t = k * _FIRE_DUR
    sx = int((W + 108) - k * (W + 216))
    night = _nightf(pal)
    _zbuf.enqueue(GROUND_Y - 1, TB_CAST,
                  lambda s, sx=sx, show_t=show_t: _fest.draw_fire_show(
                      s, sx, night, t, show_t))
    _fest.set_fire_state((sx, show_t))


def draw_promenade(surf, scroll, pal, phase, t):
    """Draw the promenade as a living day-arc: fixtures by phase, cast thinned by a
    crowd-density curve, and the whole street filling in from empty at run-start."""
    global _CUR_BUCKET, _CUR_T, _CUR_PAL, _CUR_RAIN, _CUR_SNOW, _CUR_WIND, _CUR_PHASE, _CUR_SCROLL
    _CUR_BUCKET = _biome.phase_bucket(phase)
    _CUR_T = t
    _CUR_SCROLL = scroll
    del LIGHT_SPOTS[:]   # the ground-weather pass consumed last frame's spots
    _CUR_PAL = pal
    _CUR_PHASE = phase
    _CUR_RAIN = rain_intensity(phase)
    _CUR_SNOW = storm_intensity(phase)
    _CUR_WIND = wind_intensity(phase)
    # The crowd thins in bad weather: the day-arc density is scaled down by rain/
    # snow. Multiplying only lowers each slot's stable inclusion gate, so figures
    # walk off ONCE as the storm builds (no flicker) and the survivors get brollies.
    street_calm(t)   # advance the calm-mandate hold once per frame
    density = street_density(phase, t)
    _ground_furniture(surf, W, scroll, pal, fd=_furn_density(phase))
    _dressing(surf, W, scroll, pal, phase)
    _place_scenarios(surf, W, scroll, pal, t, _roster_for(phase), density)
    _happenings(surf, scroll, pal, phase, t)
    _festival_fire(surf, scroll, pal, phase, t, density)
    # A few souls shelter near the dressing (kiosk awnings / lamp posts) when the
    # open deck has emptied — keeps the street alive at the storm's worst.
    _shelter_figures(surf, W, scroll, pal, t)
