"""Round-19 NEAR / FRONT ACTIVITY LANE — a second, CLOSER lane of promenade life.

Round 17 set the promenade cast at the FAR edge of the sidewalk (feet at
GROUND_Y=595). Round 18 embedded surface detail into the floor body. The walk now
has depth to spend: this round populates the NEAR / FRONT edge of the sidewalk —
feet at y≈636-640, down at the screen bottom — with a LARGER, closer band of life
that scrolls a touch FASTER and OCCLUDES the far lane, so the promenade reads as a
busy thing seen at multiple distances rather than a single flat row.

What makes the depth read (the contract the art-director gates):

  * SCALE — near figures are rendered ~1.6-1.8x the far cast, so a near pedestrian
    beside a far one instantly says "closer", not "a second identical row".
  * FEET LOWER — the near band's deck sits at NEAR_GROUND_Y (≈638), a full ~43px
    below the far deck; near figures (and the near dog) clip naturally at the
    screen bottom, the way a foreground subject does.
  * FASTER PARALLAX — the far props track at PROP_MULT=0.20; the near lane anchors
    at NEAR_MULT=0.35 so it slides past faster, the classic near-vs-far cue.
  * OCCLUSION — the near lane is painted AFTER the far lane / props and BEFORE the
    gameplay actors, so near figures cover the far cast's feet (real depth, not a
    transparent overlay). Within the near lane we still draw back-to-front.

The cast functions are the pooled ones (`draw_kids`, `draw_old_man`,
`draw_strollers`, `draw_dog`) and `draw_flock`, rendered onto a
scratch surface that we scale up with NEAREST so the pixels stay crisp, then drop
at the near deck. The PERFORMANCES — a day busker/juggler, a golden-hour street
musician + watching arc, a dusk stilt-walker, and the NIGHT festival LION DANCE +
drummer — are net-new procedural, built from the bench-person body idiom and
lift-only `max(0,sin)` gaits, kept on-theme (Chinese temple festival).

Lane clearance: TALL near elements (banner pole, lion head, stilt-walker) are kept
OUT of the bird lane (x≈48-188) and the pillar lane (x≈212-320); SHORT near life
(pedestrians, dog, low plants) may sit under those lanes since it stays low and the
bird flies high (y≈30-430). Coin + parrot draw last and stay on top / brightest.

Night glow is capped ≤ NIGHT_GLOW_CAP (150) and gated to a dark sky, reusing the
promenade's `_cap150` / `_lit_intensity`; day/golden emit no glow (no white pool).
Everything is retinted per biome `pal`. World-anchored on the same `_world_xs`
idiom as the far props (no jitter / seam at the scroll wrap).

Pure-Pygame / pygbag-safe (fill, blit, draw.*, SRCALPHA, BLEND_RGB_ADD, and
transform.scale with NEAREST). No numpy / gfxdraw / per-frame surfarray. Nothing
here is written into game/.
"""
from __future__ import annotations

import math
import random

import pygame

from game import foreground_props as sp
from game import foreground_promenade as pr
from game import biome as _biome
from game.config import W, H
from game.draw import draw_side_shrub, draw_wuling_pine
from game.pillar_variants import (
    draw_cascading_vine, draw_paper_lantern, draw_cairn,
    draw_darchog_pole, draw_incense_smoke,
)
from game import foreground_zbuffer as _zbuf
from game.foreground_zbuffer import TB_STRUCTURE, TB_FIXTURE, TB_CAST
from game import foreground_sprite as _spr
from game import foreground_variants as _fv
from game import performers_cast as _pf

GROUND_Y = sp.GROUND_Y               # 595 — the FAR deck (r17 cast feet).
NEAR_GROUND_Y = GROUND_Y + 43        # 638 — the NEAR deck; figures clip at bottom.
NEAR_MULT = 1.15                     # closest layer: a touch faster than the far
                                     # ground plane (1.0) for parallax depth.

# Reuse the promenade's night contract verbatim so the near lights obey the same
# ceiling and the coin stays the single brightest object.
_cap150 = pr._cap150
_lit_intensity = pr._lit_intensity
_is_dark = sp._is_dark_sky
_nightf = sp._nightf
_mix = sp._mix
_shade = sp._shade

NIGHT_GLOW_CAP = pr.NIGHT_GLOW_CAP   # 150


# ── lane-clearance gates for TALL near props ──────────────────────────────────
#
# The bird flies at x≈90 with the coin out to ~168; the cream pillar base sits at
# x≈244. A tall near element (banner pole, lion head crest, stilt-walker) must not
# climb into either corridor. SHORT near life is exempt — it lives below the bird
# and is allowed to pass under the lanes.

_BIRD_LANE = (48, 188)
_PILLAR_LANE = (212, 320)


def _tall_ok(sx, half_w=10):
    # Full-speed scroll: tall near elements scroll through freely; gating would
    # wink them mid-screen, and the bird/pipes draw on top of the foreground.
    return True


# ── near-anchored placement: same world-x idiom as the far props, faster mult ──

def _near_xs(scroll, w, period, x0, margin=80):
    """Screen-x of a near element repeated every `period` world-px at NEAR_MULT,
    so the near lane parallaxes faster than the far lane and tiles seamlessly at
    the scroll wrap (no jitter / seam)."""
    yield from sp._world_xs(scroll, w, period, x0, mult=NEAR_MULT, margin=margin)


# STATIC near-lane dressing (greenery, benches, banners, braziers, performers)
# rides world speed exactly (×1.0), same as the floor bricks + pillars, so it
# reads as PLANTED — not sliding faster than the ground. Depth still reads via the
# near lane's larger scale + lower feet line; only the parallax rate is dropped.
NEAR_STATIC_MULT = 1.0


def _near_static_xs(scroll, w, period, x0, margin=80):
    """Screen-x for PLANTED near dressing: world speed (×1.0), tiling seamlessly."""
    yield from sp._world_xs(scroll, w, period, x0, mult=NEAR_STATIC_MULT,
                            margin=margin)


# ── warm capped glow for the near performers (drum / lantern halos) ───────────
#
# Net-new lit accents (festival drum face, performer lanterns) need their own
# halo since they aren't r15 lamp heads. Reuse the promenade's cached warm-glow +
# the 150 cap + the dusk->night intensity so a near light can never rival the coin.

# Performer SOLID highlights (lion sclera, drum heads, lit cores) are not glow
# blits — they're opaque pixels that out-shone the coin when left near-white. This
# pulls any such highlight to <= NIGHT_GLOW_CAP *luma* (not per-channel) at night
# while keeping a warm/ivory hue, so the brightest near-life pixel stays under the
# coin yet still reads as a lit accent rather than flat grey.

def _cap_lum(color, pal, *, cap=NIGHT_GLOW_CAP, warm=True):
    # The cap is set BELOW NIGHT_GLOW_CAP so that when a capped highlight also takes
    # the performer's additive warm halo on top, the summed pixel still lands under
    # the ceiling and the coin stays the single brightest object.
    cap = min(cap, 138)
    if not _is_dark(pal):
        return color
    r, g, b = color
    if warm:
        # An ivory/amber target so a capped highlight reads warm, never blue-white.
        r, g, b = min(r, 150), min(g, 134), min(b, 112)
    lum = 0.2126 * r + 0.7152 * g + 0.1145 * b
    if lum > cap and lum > 0:
        f = cap / lum
        r, g, b = int(r * f), int(g * f), int(b * f)
    return (r, g, b)


# The lion's IVORY fangs + mouth lip are the one near-life accent the art-director
# gates to read crisp on EVERY base. The generic _cap_lum path caps at 138 luma and
# leaves the fangs reading flat against the cool grey-taupe scene. These two helpers
# hold a WARM ivory at the fang allowance (~145 luma — still far under the coin's
# ~248) and do NOT over-retint toward the cool night, so the fangs/lip pop the same
# on terracotta and grey-taupe. Day/golden are untouched (returned verbatim).

def _warm_ivory_cap(color, pal, cap):
    if not _is_dark(pal):
        return color
    r, g, b = color
    # A warmer ivory clamp than _cap_lum (higher green/blue ceiling) so the fang
    # stays ivory, not olive, when it lands at the slightly higher fang luma.
    r, g, b = min(r, 168), min(g, 150), min(b, 126)
    lum = 0.2126 * r + 0.7152 * g + 0.1145 * b
    if lum > cap and lum > 0:
        f = cap / lum
        r, g, b = int(r * f), int(g * f), int(b * f)
    return (r, g, b)


def _fang_ivory(pal):
    # A WARMER ivory source (more red, less green/blue) so that at the SAME ~144
    # luma cap the fang reads as a warm tooth that separates from the cool grey-
    # taupe surroundings just as crisply as it does on terracotta — the flat read
    # on the cool base was a hue/contrast issue, not a value one, so the cap stays.
    return _warm_ivory_cap((196, 170, 138), pal, cap=144)


def _lip_ivory(pal):
    return _warm_ivory_cap((186, 162, 128), pal, cap=142)


def _near_glow(surf, cx, cy, pal, *, radius=12, color=(255, 170, 110)):
    if not _is_dark(pal):
        return
    s = _lit_intensity(pal)
    if s <= 0.02:
        return
    # A touch below the promenade peak so the bloom CORE (its centre add summed onto
    # the lit prop beneath) still lands under the cap and the coin stays brightest.
    peak = int(sp._GLOW_PEAK * 0.46 * s)
    if peak <= 1:
        return
    g = sp._warm_glow(radius, _cap150(color), peak)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)


# ── scale an r17 cast fn up to near size by rendering it onto a scratch deck ───
#
# The r17 cast fns (draw_kids/old_man/strollers/flock) draw at the fixed module
# GROUND_Y onto whatever surface they're handed. To get a LARGER, NEAREST-crisp
# near figure we render the fn onto a tall scratch surface whose own GROUND_Y line
# sits near the bottom, scale the result up, and blit so the figure's feet land at
# the near deck. NEAREST keeps the pixel art crisp at the enlarged size.

# A scratch tile tall enough to hold a standing cast figure (heads reach ~30px
# above the deck) plus headroom for a raised arm / cane.
_SCRATCH_H = 56
_SCRATCH_W = 96


# A near cast sprite is identical for a given (fn, scale, palette, animation-frame,
# kwargs) regardless of WHERE it's placed — the fns draw at the scratch centre and
# don't depend on sx. So we bake it ONCE and reuse: every same-kind near figure on a
# frame (and across frames within an animation bucket) shares one cached surface,
# instead of allocating + redrawing + scaling a scratch deck per figure per frame.
# That per-figure alloc was the dominant near-lane cost; this is the perf safeguard.
_CAST_FPS = 8                            # animation buckets/sec for background figures

# Per-drawer authoring box (w, h). Default fits a standing cast figure; taller/
# wider acts (performers) get their own box so the supersample bake never clips.
_NATIVE_BOX = {}
_DEFAULT_BOX = (_SCRATCH_W, _SCRATCH_H)


def _scaled_cast(surf, cast_fn, sx, pal, scale, *, t=0.0, feet_y=NEAR_GROUND_Y,
                 ss=1, smooth=False, flip=False, **kw):
    """Bake a cast fn (feet on a scratch deck) to a footprint `scale`× its box and
    blit so the feet land on `feet_y`. Served from the shared sprite cache, keyed
    by (fn, footprint, mode, palette bucket, gait frame, facing, kwargs) — so a
    `variant=` kwarg or a `flip` bakes distinctly without flicker. `flip` mirrors
    the figure horizontally (walk facing). NEAREST by default (crisp pixels); a
    drawer authored at higher detail can pass ss>1 + smooth=True to supersample
    then anti-alias down. The cast fns read pr.GROUND_Y; we point that at the
    scratch deck while baking so the figure crops cleanly."""
    box_w, box_h = _NATIVE_BOX.get(cast_fn.__name__, _DEFAULT_BOX)
    render_box = (box_w * ss, box_h * ss)
    foot_w = max(1, int(box_w * scale))
    foot_h = max(1, int(box_h * scale))
    tb = int(t * _CAST_FPS)              # quantise the gait clock -> bounded cache
    # Key on the biome phase BUCKET (set per frame by draw_near_lane), not id(pal):
    # the play palette is a fresh dict every frame, so id(pal) only ever hits within
    # a frame -- bucketing lets the bake survive across frames.
    key = (cast_fn.__name__, foot_w, foot_h, ss, smooth, pr._CUR_BUCKET, tb, flip,
           tuple(sorted(kw.items())))

    def _render(scratch):
        deck = render_box[1] - 1         # scratch deck near the bottom edge
        saved = pr.GROUND_Y
        pr.GROUND_Y = deck
        try:
            cast_fn(scratch, render_box[0] // 2, pal, t=tb / _CAST_FPS, **kw)
        finally:
            pr.GROUND_Y = saved

    # A LARGE near figure shouldn't pull focus from the parrot: knock its
    # brightest fabric down ~6% (applied pre-resample so a smoothscale averages
    # already-dimmed pixels).
    big = _spr.baked_sprite(key, render_box, (foot_w, foot_h), _render,
                            dim=(240, 240, 240), smooth=smooth, flip=flip)
    sw, _sh = big.get_size()
    surf.blit(big, (sx - sw // 2, feet_y - foot_h))


# ── near greenery / ornaments (parametric game helpers, retinted, night-capped)─

def _fol(pal, night):
    """Foliage sub-palette cooled toward night so near plants match the deck."""
    return {
        'foliage_dark': _mix(pal.get('foliage_dark', (35, 75, 35)), (40, 56, 86), 0.3 * night),
        'foliage_mid': _mix(pal.get('foliage_mid', (60, 115, 50)), (46, 64, 94), 0.3 * night),
        'foliage_top': _mix(pal.get('foliage_top', (90, 150, 70)), (60, 80, 110), 0.3 * night),
    }


def _near_pine(surf, sx, pal, *, feet_y=NEAR_GROUND_Y, height=34):
    """A near Wuling pine in a tub — a taller piece of front greenery. Only placed
    in a clear horizontal zone since it climbs higher than a planter."""
    night = _nightf(pal)
    by = feet_y
    tub = _mix((120, 84, 52), (70, 76, 96), 0.32 * night)
    pygame.draw.rect(surf, _shade(tub, -20), (sx - 7, by - 9, 14, 9))
    pygame.draw.rect(surf, tub, (sx - 6, by - 9, 12, 7))
    draw_wuling_pine(surf, sx, by - 8, height, _fol(pal, night))


def _near_vine_lantern(surf, sx, pal, *, feet_y=NEAR_GROUND_Y):
    """A near tub with a cascading vine spilling over the front edge — pure decor
    that reads as a closer detail than the far vine trails."""
    night = _nightf(pal)
    by = feet_y
    pot = _mix((120, 84, 52), (70, 76, 96), 0.32 * night)
    pygame.draw.rect(surf, _shade(pot, -18), (sx - 7, by - 11, 14, 11))
    pygame.draw.rect(surf, pot, (sx - 6, by - 11, 12, 9))
    if _is_dark(pal):
        # draw_cascading_vine paints a hardcoded (255,180,120) leaf-tip highlight
        # that out-spiked the night cap. Render it on a scratch and knock its
        # brightness down so no decor leaf rivals the coin at night.
        sc = pygame.Surface((40, 36), pygame.SRCALPHA)
        draw_cascading_vine(sc, 20, 4, 16, _fol(pal, night))
        sc.fill((150, 150, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(sc, (sx - 20, by - 16))
    else:
        draw_cascading_vine(surf, sx, by - 12, 16, _fol(pal, night))


def _near_brazier(surf, sx, pal, *, feet_y=NEAR_GROUND_Y, t=0.0):
    """A festival incense urn / brazier on the front edge — a squat stone bowl with
    a thread of incense smoke (and a small capped ember glow at night). On-theme
    temple dressing; kept short so it can sit under the lanes."""
    night = _nightf(pal)
    by = feet_y
    bowl = _mix(pal.get('stone_dark', (95, 80, 70)), (120, 96, 78), 0.5)
    bowl = _mix(bowl, (54, 60, 86), 0.32 * night)
    pygame.draw.ellipse(surf, _shade(bowl, -22), (sx - 9, by - 12, 18, 12))
    pygame.draw.ellipse(surf, bowl, (sx - 8, by - 12, 16, 9))
    pygame.draw.ellipse(surf, _shade(bowl, -30), (sx - 6, by - 11, 12, 4))
    if _is_dark(pal):
        # Ember core kept low (cap_lum) so the additive halo over it never spikes.
        ember = _cap_lum((150, 78, 46), pal)
        pygame.draw.ellipse(surf, ember, (sx - 4, by - 11, 8, 3))
        _near_glow(surf, sx, by - 10, pal, radius=9, color=(255, 150, 90))
    draw_incense_smoke(surf, sx, by - 12, length=18)


# ══════════════════════════════════════════════════════════════════════════
# Net-new PERFORMERS. All are built from the bench-person body idiom + lift-only
# gaits so they belong to the r17 cast's value family but read at the larger near
# scale. Each takes (surf, sx, pal, t) with feet on the near deck.
# ══════════════════════════════════════════════════════════════════════════

def _perf_body(surf, x, feet_y, robe, robe_dk, hair, pal, *, h=18, w=9,
               lean=0, arms='down', arm_t=0.0):
    """A larger standing performer torso + head with posable arms. Mirrors the
    bench-person idiom (block torso, round head, hair cap) at near scale, retinted
    per night so a face never out-shines the cap. Returns (head_x, head_y) so a
    caller can add a hat / crest. `arms`: 'down' | 'up' | 'drum' | 'juggle'."""
    night = _nightf(pal)
    skin = pr._retint_person((232, 192, 150), night)
    body_y = feet_y - h
    # Robe as a wedge so the near figure has weight; lean tips the shoulders.
    pygame.draw.polygon(surf, robe, [
        (x - w // 2 + lean, body_y), (x + w // 2 + lean, body_y),
        (x + w // 2 + 1, feet_y), (x - w // 2 - 1, feet_y)])
    pygame.draw.polygon(surf, robe_dk, [
        (x - w // 2 + lean, body_y), (x + w // 2 + lean, body_y),
        (x + w // 2 + 1, feet_y), (x - w // 2 - 1, feet_y)], 1)
    hx, hy = x + lean, body_y - 4
    pygame.draw.circle(surf, skin, (hx, hy), 4)
    pygame.draw.arc(surf, hair, (hx - 4, hy - 5, 9, 9),
                    math.radians(0), math.radians(180), 3)
    pygame.draw.circle(surf, (30, 20, 15), (hx - 1, hy), 0)
    pygame.draw.circle(surf, (30, 20, 15), (hx + 1, hy), 0)
    # Legs.
    leg = _shade(robe_dk, -14)
    pygame.draw.line(surf, leg, (x - 2 + lean, feet_y - 5), (x - 3, feet_y), 2)
    pygame.draw.line(surf, leg, (x + 2 + lean, feet_y - 5), (x + 3, feet_y), 2)
    # Arms per pose.
    sh_y = body_y + 3
    swing = max(0.0, math.sin(arm_t))
    if arms == 'up':
        for dx in (-1, 1):
            ax = x + (w // 2) * dx + lean
            pygame.draw.line(surf, robe, (ax, sh_y),
                             (ax + dx * 4, sh_y - 7 - int(swing * 3)), 2)
    elif arms == 'drum':
        for dx, ph in ((-1, 0.0), (1, math.pi)):
            ax = x + (w // 2) * dx + lean
            lift = int(max(0.0, math.sin(arm_t + ph)) * 4)
            pygame.draw.line(surf, robe, (ax, sh_y),
                             (ax + dx * 5, sh_y + 4 - lift), 2)
    elif arms == 'juggle':
        for dx in (-1, 1):
            ax = x + (w // 2) * dx + lean
            pygame.draw.line(surf, robe, (ax, sh_y), (ax + dx * 5, sh_y - 4), 2)
    else:  # down
        for dx in (-1, 1):
            ax = x + (w // 2) * dx + lean
            pygame.draw.line(surf, robe, (ax, sh_y), (ax + dx * 3, sh_y + 6), 2)
    return hx, hy


def _watch_arc(surf, sx, pal, t, *, feet_y=NEAR_GROUND_Y):
    """A small head-bobbing crowd watching a near performer — scaled r17 cast
    arranged in a shallow arc facing inward. Reused for golden/dusk/night so the
    'crowd grows' escalation reads. Kept SHORT so it may sit under the lanes."""
    # A few kids + an elder + strollers, spread either side of the performer.
    _scaled_cast(surf, pr.draw_kids, sx - 30, pal, 1.45, t=t, n=2, feet_y=feet_y)
    _scaled_cast(surf, pr.draw_old_man, sx + 30, pal, 1.5, t=t,
                 seated_bench=False, variant=1, feet_y=feet_y)


def _seated_spectator(surf, x, feet_y, robe, robe_dk, hair, pal, *,
                      lean=0, raise_arm=False, t=0.0, face=1, gesture='cheer'):
    """A small spectator SEATED on the deck (knees forward), used to give a gathered
    crowd a couple of LOWER figures so it reads 'an audience sat watching the act'
    rather than people walking past. `lean` tips the torso/head toward the act and
    `raise_arm` adds an arm lifted toward the performer (direction `face`: +1=right)
    so the pose reads unambiguously as 'audience facing the act'. `gesture`:
    'cheer' (high bobbing arm) | 'point' (a lower forearm reaching toward the act)
    — two distinct silhouettes so the pair don't read as identical clones."""
    night = _nightf(pal)
    skin = pr._retint_person((232, 192, 150), night)
    seat_y = feet_y - 2
    # Folded legs as a low wedge on the deck.
    pygame.draw.polygon(surf, _shade(robe_dk, -10), [
        (x - 6, seat_y), (x + 6, seat_y), (x + 4, seat_y - 4), (x - 4, seat_y - 4)])
    # Compact torso + head, sitting low; the torso top shifts by `lean` so the
    # shoulders + head tip toward the act (a clear facing cue, not a flat block).
    pygame.draw.polygon(surf, robe, [
        (x - 4 + lean, seat_y - 12), (x + 4 + lean, seat_y - 12),
        (x + 4, seat_y - 3), (x - 4, seat_y - 3)])
    pygame.draw.polygon(surf, robe_dk, [
        (x - 4 + lean, seat_y - 12), (x + 4 + lean, seat_y - 12),
        (x + 4, seat_y - 3), (x - 4, seat_y - 3)], 1)
    hx = x + lean
    pygame.draw.circle(surf, skin, (hx, seat_y - 15), 3)
    pygame.draw.arc(surf, hair, (hx - 3, seat_y - 19, 7, 7),
                    math.radians(0), math.radians(180), 2)
    if raise_arm:
        sh_y = seat_y - 10
        if gesture == 'point':
            # A lower forearm reaching out toward the performer with a skin-toned
            # hand at the tip — a clear "looking that way" cue distinct from a
            # raised cheer, so the two seated figures read as separate poses.
            ex, ey = hx + face * 7, sh_y - 1
            pygame.draw.line(surf, robe, (hx, sh_y), (ex, ey), 2)
            pygame.draw.circle(surf, skin, (ex, ey), 1)
        else:
            # An arm lifted toward the performer (a small cheer), bobbing gently so
            # the gathered crowd reads as actively watching the act.
            wave = int(max(0.0, math.sin(t * 3.0)) * 2)
            ex, ey = hx + face * 5, sh_y - 6 - wave
            pygame.draw.line(surf, robe, (hx, sh_y), (ex, ey), 2)
            pygame.draw.circle(surf, skin, (ex, ey), 1)


def _gathered_crowd(surf, sx, pal, t, *, feet_y=NEAR_GROUND_Y):
    """A TIGHT, performer-FACING audience clustered to the LEFT of the act (so all
    heads turn toward the performer on the right). The differentiator from the
    day/dusk foot traffic is the CLUSTERING + uniform facing + a couple of LOWER
    seated figures. Built from scaled r17 cast + two seated spectators."""
    night = _nightf(pal)
    rb = pr._retint_person((120, 110, 150), night)
    rb_dk = pr._retint_person((78, 72, 108), night)
    hr = pr._retint_person((58, 46, 42), night)
    # Back row: standing figures packed close, all on the performer's left, so the
    # group leans/looks toward the act rather than spreading symmetrically.
    _scaled_cast(surf, pr.draw_kids, sx - 40, pal, 1.5, t=t, n=2, feet_y=feet_y)
    _scaled_cast(surf, pr.draw_old_man, sx - 22, pal, 1.55, t=t,
                 seated_bench=False, variant=2, feet_y=feet_y)
    _scaled_cast(surf, pr.draw_strollers, sx - 56, pal, 1.45, t=t, feet_y=feet_y,
                 variant=3)
    # Front row: two LOWER seated spectators close in, reading as the near edge of
    # a gathered audience facing the performer. Both lean RIGHT toward the act (it
    # sits at sx, to their right) with a stronger head-tip, and EACH gestures toward
    # the performer in a DISTINCT pose (one high cheer, one reaching point) so the
    # "audience facing the act" read lands instantly and the pair don't clone.
    _seated_spectator(surf, sx - 30, feet_y, rb, rb_dk, hr, pal,
                      lean=3, raise_arm=True, t=t, face=1, gesture='cheer')
    _seated_spectator(surf, sx - 14,
                      feet_y, pr._retint_person((150, 90, 80), night),
                      pr._retint_person((100, 56, 50), night), hr, pal,
                      lean=3, raise_arm=True, t=t, face=1, gesture='point')


def perf_juggler(surf, sx, pal, t):
    """DAY · a casual daytime BUSKER / juggler — a single performer tossing three
    balls in a small arc, with 1-2 near onlookers half-facing him so it reads
    'busking', not a lone figure. Low-key morning act; no crowd, no glow."""
    night = _nightf(pal)
    robe = pr._retint_person((196, 92, 70), night)     # warm terracotta tunic
    robe_dk = pr._retint_person((150, 60, 52), night)
    hair = pr._retint_person((70, 50, 40), night)
    feet = NEAR_GROUND_Y
    # A couple of onlookers stand to the RIGHT, half-facing the juggler, so the act
    # reads as busking. Kept tight beside him, clear of the gameplay lanes.
    _scaled_cast(surf, pr.draw_old_man, sx + 30, pal, 1.45, t=t,
                 seated_bench=False, variant=3, feet_y=feet)
    _scaled_cast(surf, pr.draw_kids, sx + 46, pal, 1.4, t=t, n=2, feet_y=feet)
    hx, hy = _perf_body(surf, sx, feet, robe, robe_dk, hair, pal,
                        h=20, w=9, arms='juggle', arm_t=t * 3.0)
    # Three balls on a small juggling cascade above the hands. Sized a touch
    # bigger (r=5 outer / 4 fill) and pushed to hot, fully-saturated primaries so
    # the arc reads as juggling MOTION at 1x rather than as stray confetti — a
    # juggling ball wants to read as a deliberate prop, not a paving fleck.
    ball_cols = ((255, 176, 16), (240, 44, 40), (32, 132, 248))
    for i, col in enumerate(ball_cols):
        ph = (t * 1.6 + i / 3.0) % 1.0
        bx = sx + int(math.sin(ph * math.tau) * 9)
        by = hy - 4 - int(math.sin(ph * math.pi) * 13)
        col = pr._retint_person(col, night)
        pygame.draw.circle(surf, _shade(col, -24), (bx, by), 5)
        pygame.draw.circle(surf, col, (bx, by), 4)
        # A hot 2px highlight so each ball reads round, lit and tracking through
        # the cascade rather than as a flat dot.
        pygame.draw.circle(surf, _shade(col, 48), (bx - 1, by - 1), 2)


def perf_musician(surf, sx, pal, t):
    """GOLDEN HOUR · a street MUSICIAN pulled INTO the near lane (forward + larger),
    SEATED behind a visible barrel drum, with a TIGHT performer-FACING crowd
    gathered to his left. The clustering + uniform facing distinguishes this act
    from the day/dusk foot traffic."""
    night = _nightf(pal)
    robe = pr._retint_person((90, 110, 160), night)    # indigo musician robe
    robe_dk = pr._retint_person((58, 74, 116), night)
    hair = pr._retint_person((60, 45, 40), night)
    feet = NEAR_GROUND_Y
    # The gathered audience (behind), clustered on the performer's left + facing in.
    _gathered_crowd(surf, sx, pal, t, feet_y=feet)
    # A SEATED musician (lower torso, knees forward) on the deck behind a big drum.
    skin = pr._retint_person((232, 192, 150), night)
    seat_y = feet - 2
    pygame.draw.polygon(surf, _shade(robe_dk, -10), [
        (sx + 2, seat_y), (sx + 14, seat_y), (sx + 12, seat_y - 5), (sx + 4, seat_y - 5)])
    pygame.draw.rect(surf, robe, (sx + 3, seat_y - 16, 9, 12))
    pygame.draw.rect(surf, robe_dk, (sx + 3, seat_y - 16, 9, 12), 1)
    hx, hy = sx + 7, seat_y - 19
    pygame.draw.circle(surf, skin, (hx, hy), 4)
    pygame.draw.arc(surf, hair, (hx - 4, hy - 5, 9, 9),
                    math.radians(0), math.radians(180), 3)
    # A LARGER barrel drum/gong stood on the deck in front of the seated musician.
    dx, dy = sx - 4, feet
    drum = _mix((150, 60, 45), (70, 70, 96), 0.30 * night)
    pygame.draw.ellipse(surf, _shade(drum, -24), (dx - 11, dy - 20, 22, 20))
    pygame.draw.ellipse(surf, drum, (dx - 10, dy - 19, 20, 18))
    head_col = _cap_lum((205, 182, 145), pal)
    pygame.draw.ellipse(surf, head_col, (dx - 9, dy - 19, 18, 6))
    pygame.draw.ellipse(surf, _shade(head_col, -26), (dx - 9, dy - 19, 18, 6), 1)
    tack = _cap_lum((180, 150, 90), pal)
    for ti in range(-2, 3):
        pygame.draw.circle(surf, tack, (dx + ti * 5, dy - 12), 1)
    # His hands beat the near drum head (mid-swing).
    for ph in (0.0, math.pi):
        lift = int(max(0.0, math.sin(t * 4.5 + ph)) * 5)
        hxh = dx + (4 if ph else -4)
        pygame.draw.line(surf, robe, (sx + 5, seat_y - 12),
                         (hxh, dy - 18 - lift), 2)
    _near_glow(surf, dx, dy - 12, pal, radius=10, color=(255, 150, 90))


def perf_stilt(surf, sx, pal, t):
    """DUSK · the crowd grows and a STILT-WALKER warms up as the lamps light — a
    tall robed figure on stilts (kept in a clear zone since it's tall). A small
    watching arc gathers below."""
    night = _nightf(pal)
    robe = pr._retint_person((150, 70, 130), night)    # festival magenta
    robe_dk = pr._retint_person((100, 44, 92), night)
    hair = pr._retint_person((60, 45, 40), night)
    feet = NEAR_GROUND_Y
    _watch_arc(surf, sx, pal, t, feet_y=feet)
    # Stilts: two tall poles from the deck up to a raised body.
    stilt_h = 24
    sway = int(math.sin(t * 1.6) * 1)
    body_feet = feet - stilt_h
    pole = _shade((110, 78, 48), -10)
    for dx in (-3, 3):
        pygame.draw.line(surf, pole, (sx + dx + sway, body_feet),
                         (sx + dx, feet), 2)
    _perf_body(surf, sx + sway, body_feet, robe, robe_dk, hair, pal,
               h=18, w=8, arms='up', arm_t=t * 2.0)


def perf_lion_dance(surf, sx, pal, t):
    """NIGHT · the festival peak — a two-person LION DANCE + a drummer + a bigger
    crowd. The lion is a bulbous decorated head (carried high by a front dancer)
    trailing a flowing cloth body over a rear dancer; a drummer keeps time beside
    it. Net-new procedural, on-theme, lit accents capped + gated."""
    night = _nightf(pal)
    feet = NEAR_GROUND_Y
    # The bigger crowd flanks the act (behind, drawn first).
    _scaled_cast(surf, pr.draw_strollers, sx - 44, pal, 1.5, t=t, feet_y=feet,
                 variant=13)
    _scaled_cast(surf, pr.draw_kids, sx - 64, pal, 1.55, t=t, n=3, feet_y=feet)
    _scaled_cast(surf, pr.draw_old_man, sx + 48, pal, 1.55, t=t,
                 seated_bench=False, variant=4, feet_y=feet)

    # Drummer + drum to the right of the lion — an EXPLICIT round drum stood in
    # FRONT of the elder with a stick caught mid-swing, so the lion dance's audio
    # source is legible rather than a robed bystander.
    drx = sx + 32
    robe = pr._retint_person((110, 60, 70), night)
    robe_dk = pr._retint_person((74, 40, 50), night)
    hair = pr._retint_person((50, 40, 38), night)
    _perf_body(surf, drx, feet, robe, robe_dk, hair, pal,
               h=21, w=9, arms='drum', arm_t=t * 6.0)
    # The drum body sits on the deck in front of the drummer (round shell + heads).
    ddx, ddy = drx - 10, feet - 1
    shell = _mix((160, 55, 45), (70, 70, 96), 0.34 * night)
    pygame.draw.ellipse(surf, _shade(shell, -28), (ddx - 9, ddy - 17, 18, 17))
    pygame.draw.ellipse(surf, shell, (ddx - 8, ddy - 16, 16, 15))
    for hy in (ddy - 16, ddy - 3):
        head = _cap_lum((200, 178, 140), pal)
        pygame.draw.ellipse(surf, head, (ddx - 8, hy, 16, 5))
        pygame.draw.ellipse(surf, _shade(shell, -34), (ddx - 8, hy, 16, 5), 1)
    # Brass tacks around the rim — capped so they never spike over the cap.
    tack = _cap_lum((180, 150, 90), pal)
    for ti in range(-2, 3):
        pygame.draw.circle(surf, tack, (ddx + ti * 4, ddy - 9), 1)
    # A drumstick caught mid-swing above the near head.
    stick = pr._retint_person((180, 140, 95), night)
    swing = int(max(0.0, math.sin(t * 6.0)) * 6)
    pygame.draw.line(surf, stick, (ddx + 4, ddy - 16),
                     (ddx + 10, ddy - 20 - swing), 2)
    _near_glow(surf, ddx, ddy - 9, pal, radius=11, color=(255, 150, 90))

    # ── the LION DANCE (two dancers under a flowing body) ─────────────────────
    # The silhouette must read as a Chinese temple lion, not a round mascot: a
    # ridged horned head, a scalloped frilled mane, a gaping lip-lined mouth, and
    # a long trailing cloth body with a SECOND pair of legs behind the front pair.
    bob = int(max(0.0, math.sin(t * 3.2)) * 3)        # the lion's bouncy lift
    body_y = feet - 16 - bob
    cloth = pr._retint_person((205, 70, 55), night)   # festive red drape
    cloth_dk = pr._retint_person((150, 45, 42), night)
    trim = _cap_lum((230, 195, 90), pal)              # gold hem (capped at night)
    # The trailing cloth body runs from BEHIND (tail, left) up to the head (right);
    # a long undulating drape so the two dancers clearly share one costume.
    bx0 = sx - 36                                      # tail end (behind head)
    seg_pts = []
    for i in range(8):
        tt = i / 7.0
        px = bx0 + int(tt * 36)
        wave = int(math.sin(t * 3.0 + tt * 4.0) * 3)
        py = body_y + 7 + wave + int(tt * 3)
        seg_pts.append((px, py))
    top = [(p[0], p[1] - 7) for p in seg_pts]
    bot = [(p[0], p[1] + 7) for p in reversed(seg_pts)]
    pygame.draw.polygon(surf, cloth_dk, top + bot)
    pygame.draw.polygon(surf, cloth, [(p[0], p[1] - 5) for p in seg_pts] +
                        [(p[0], p[1] + 5) for p in reversed(seg_pts)])
    # A scalloped gold hem (a run of small arcs) so the drape reads "costume".
    for px, py in seg_pts:
        pygame.draw.circle(surf, trim, (px, py + 6), 2)
        pygame.draw.circle(surf, _shade(trim, -30), (px, py + 6), 2, 1)
    # A frilled tail tuft at the back end.
    for fa in (-30, 0, 30):
        fx = bx0 - 3 + int(math.cos(math.radians(fa)) * 5)
        fy = seg_pts[0][1] + int(math.sin(math.radians(fa)) * 5)
        pygame.draw.circle(surf, trim, (fx, fy), 2)
    # TWO pairs of dancer legs from under the cloth: a REAR pair (back/left) and a
    # FRONT pair (under the head), so it clearly reads "two people in one costume".
    leg = pr._retint_person((58, 48, 58), night)
    legpx = _cap_lum((150, 120, 70), pal)             # gold trouser cuffs (capped)
    for lx, ph, back in ((sx - 26, 0.0, True), (sx - 20, math.pi, True),
                         (sx + 6, 0.7, False), (sx + 12, math.pi + 0.7, False)):
        step = int(max(0.0, math.sin(t * 4.0 + ph)) * 3)
        fy = feet - (10 if back else 9)
        pygame.draw.line(surf, leg, (lx, fy), (lx + (1 if step else -1), feet - 1), 3)
        pygame.draw.line(surf, legpx, (lx, feet - 2), (lx + (1 if step else -1), feet), 3)

    # ── the lion HEAD — a wide ridged horned mask with a scalloped frill mane and
    # a gaping mouth, held high at the FRONT (right) of the body. ───────────────
    head_cx = sx + 22
    head_cy = body_y - 7 - bob
    # Festival accents are routed through _cap_lum so even the bright gold/ivory
    # mask never spikes a near-life pixel over the cap at night (warm bloom only).
    horn = _cap_lum((235, 200, 90), pal)
    horn_dk = _cap_lum((180, 145, 60), pal)
    face = _cap_lum((225, 205, 170), pal)   # ivory mask, not white
    face_dk = _cap_lum((175, 150, 120), pal)
    green = _cap_lum((70, 150, 110), pal)
    red = _cap_lum((210, 70, 60), pal)
    gold = _cap_lum((230, 190, 90), pal)
    # (b) the SCALLOPED MANE — an arc of small gold/green/red frill triangles
    # ringing the face (front-facing half-ring, densest over the brow).
    frill_cols = (gold, green, red)
    for k, ang in enumerate(range(-150, 151, 22)):
        rad = math.radians(ang)
        mx = head_cx + int(math.cos(rad) * 13)
        my = head_cy + int(math.sin(rad) * 12)
        c = frill_cols[k % 3]
        pygame.draw.polygon(surf, _shade(c, -28), [
            (mx - 3, my + 2), (mx + 3, my + 2),
            (mx + int(math.cos(rad) * 5), my + int(math.sin(rad) * 5))])
        pygame.draw.polygon(surf, c, [
            (mx - 2, my + 1), (mx + 2, my + 1),
            (mx + int(math.cos(rad) * 4), my + int(math.sin(rad) * 4))])
    # (a) a WIDER ridged head: a flat-topped dome wider than tall, with a raised
    # brow bump, not a soft circle.
    pygame.draw.ellipse(surf, face_dk, (head_cx - 12, head_cy - 9, 24, 19))
    pygame.draw.ellipse(surf, face, (head_cx - 11, head_cy - 8, 22, 16))
    # The brow ridge — a darker raised band across the upper face.
    pygame.draw.arc(surf, face_dk, (head_cx - 11, head_cy - 9, 22, 14),
                    math.radians(195), math.radians(345), 3)
    # A central HORN/brow bump on top (gold, ridged).
    pygame.draw.polygon(surf, horn_dk, [
        (head_cx - 3, head_cy - 7), (head_cx + 3, head_cy - 7),
        (head_cx + 1, head_cy - 16), (head_cx - 1, head_cy - 16)])
    pygame.draw.polygon(surf, horn, [
        (head_cx - 2, head_cy - 8), (head_cx + 2, head_cy - 8),
        (head_cx, head_cy - 15)])
    pygame.draw.circle(surf, horn, (head_cx, head_cy - 15), 2)
    # Two side ear/horn nubs flanking the brow.
    for ex in (-9, 9):
        pygame.draw.circle(surf, gold, (head_cx + ex, head_cy - 6), 2)
        pygame.draw.circle(surf, _shade(gold, -30), (head_cx + ex, head_cy - 6), 2, 1)
    # The eyes — capped IVORY/amber sclera (never white) under a heavy brow, with a
    # dark pupil so they read as carved festival-mask eyes.
    eye = _cap_lum((150, 138, 112), pal)
    for ex in (-5, 5):
        pygame.draw.circle(surf, _shade(eye, -34), (head_cx + ex, head_cy - 2), 3)
        pygame.draw.circle(surf, eye, (head_cx + ex, head_cy - 2), 2)
        pygame.draw.circle(surf, (28, 22, 26), (head_cx + ex, head_cy - 1), 1)
    # (c) a GAPING MOUTH — a dark notch with a red/gold lip line; the jaw bounces a
    # touch with the bob so it reads "snapping".
    jaw = 2 + int(max(0.0, math.sin(t * 3.2 + 0.5)) * 2)
    pygame.draw.polygon(surf, (26, 18, 22), [
        (head_cx - 8, head_cy + 4), (head_cx + 8, head_cy + 4),
        (head_cx + 6, head_cy + 6 + jaw), (head_cx - 6, head_cy + 6 + jaw)])
    pygame.draw.line(surf, red, (head_cx - 8, head_cy + 4),
                     (head_cx + 8, head_cy + 4), 2)
    pygame.draw.line(surf, _lip_ivory(pal), (head_cx - 6, head_cy + 6 + jaw),
                     (head_cx + 6, head_cy + 6 + jaw), 1)
    # Two ivory fangs at the lip. The plain _cap_lum path over-retints these toward
    # the cool night and lands them ~138 luma, which reads crisp on terracotta but
    # flat on the cool base. _fang_ivory holds a warm ivory at the fang allowance
    # (~145 luma, still well under the coin's ~248) and seats each fang on a dark
    # gum line so it pops the same on the grey-taupe base.
    fang = _fang_ivory(pal)
    # A deep, near-black warm gum seat (independent of the fang shade so it bites
    # the same on the cool base) plus a 1px warm tip highlight, so each ivory fang
    # carries its OWN value range and stays crisp against cool-grey surroundings —
    # not just relying on the mask behind it for contrast.
    fang_sh = (30, 20, 18)
    fang_lt = _warm_ivory_cap((214, 188, 152), pal, cap=144)
    for fx in (-4, 4):
        pts = [(head_cx + fx - 1, head_cy + 4), (head_cx + fx + 1, head_cy + 4),
               (head_cx + fx, head_cy + 6)]
        pygame.draw.polygon(surf, fang_sh, [
            (p[0], p[1] + 1) for p in pts])     # dark seat for crisp separation
        pygame.draw.polygon(surf, fang, pts)
        # A 1px brighter ivory along the fang's lit top edge gives it internal
        # value range so it reads carved, not a flat blob, on either base.
        pygame.draw.line(surf, fang_lt, (head_cx + fx - 1, head_cy + 4),
                         (head_cx + fx + 1, head_cy + 4), 1)
    # A red nose bridge above the mouth.
    pygame.draw.circle(surf, red, (head_cx, head_cy + 2), 2)
    # A capped warm glow off the lit mask at night so it reads festive, not flat.
    _near_glow(surf, head_cx, head_cy, pal, radius=14, color=(255, 160, 100))


# ══════════════════════════════════════════════════════════════════════════
# perf_dragon_dance — the night festival's MARQUEE act, a SIBLING of the lion
# dance (same warm red/gold value key, the same capped-glow / _cap_lum / _nightf
# contract) but LONGER and SERPENTINE: a 7-segment dragon carried on poles by a
# distinct per-pole dancer crew, undulating across the front edge.
#
# Read contract (survives the near-lane shrink): a right-facing PROFILE head with
# a snout LIFTED forward into the scroll, ONE dominant eye, tall regal antlers, a
# ROARING drop-jaw, one continuous trailing whisker; a body that RISES into the
# head over a CONTINUOUS sawtooth dorsal ridge; a light-gold belly against a
# dark-red back on every segment (the colour-blind value split); ONE flame locus
# (the head) and a tail tapering to a single wisp. Glow is amber/lacquer-orange —
# cooled AWAY from coin-gold — and capped so no dorsal tooth reads as a coin.
# ══════════════════════════════════════════════════════════════════════════

# Distinct festival robe palettes for the dancer crew (crowd energy, retinted at
# night). V2's set is the locked phase/colour ordering from the convergence sheet.
_DRAGON_ROBES = [(60, 110, 160), (180, 70, 120), (70, 140, 90), (200, 150, 60)]

# An amber / lacquer-orange glow source, pulled ~12% off the lion's warm halo and
# AWAY from coin-gold so a head sparkle or dorsal tooth is never read as a coin.
_DRAGON_GLOW = (255, 150, 78)


def _dragon_kit(pal, skin):
    """Colour kit for the serpent. `skin='red'` is the shipped red/gold festival
    dragon; `skin='jade'` is candidate V5's jade ALT (kept selectable, not default).
    Every channel routes through _cap_lum so no accent spikes over the night cap."""
    if skin == 'jade':
        return dict(
            scale=_cap_lum((54, 146, 104), pal), scale_dk=_cap_lum((36, 100, 74), pal),
            outline=_cap_lum((22, 64, 50), pal),
            belly=_cap_lum((236, 200, 98), pal), belly_dk=_cap_lum((190, 152, 64), pal),
            hi=_cap_lum((150, 196, 142), pal),
            ridge=_cap_lum((226, 188, 92), pal), ridge_dk=_cap_lum((30, 88, 64), pal),
            face=_cap_lum((216, 204, 170), pal), face_dk=_cap_lum((160, 148, 120), pal),
            horn=_cap_lum((232, 196, 96), pal), horn_dk=_cap_lum((172, 136, 56), pal),
            gold=_cap_lum((234, 200, 108), pal), red=_cap_lum((210, 84, 64), pal),
            eye=_cap_lum((248, 196, 72), pal),
            jaw=_lip_ivory(pal), fang=_fang_ivory(pal),
            whisk=_cap_lum((214, 200, 118), pal))
    return dict(
        scale=_cap_lum((196, 58, 50), pal), scale_dk=_cap_lum((140, 38, 36), pal),
        outline=_cap_lum((96, 24, 26), pal),
        belly=_cap_lum((238, 198, 92), pal), belly_dk=_cap_lum((196, 150, 60), pal),
        hi=_cap_lum((216, 146, 96), pal),       # snout/plate accent, pulled ~15%
                                                # in value so the eye + gold antler
                                                # stay the brightest forward accents
        ridge=_cap_lum((230, 190, 88), pal), ridge_dk=_cap_lum((150, 46, 42), pal),
        face=_cap_lum((222, 200, 164), pal), face_dk=_cap_lum((170, 144, 114), pal),
        horn=_cap_lum((236, 200, 94), pal), horn_dk=_cap_lum((176, 138, 56), pal),
        gold=_cap_lum((240, 206, 110), pal), red=_cap_lum((214, 70, 58), pal),
        eye=_cap_lum((250, 196, 70), pal),
        jaw=_lip_ivory(pal), fang=_fang_ivory(pal),
        whisk=_cap_lum((226, 182, 104), pal))


def _dragon_spine(sx, feet_y, n, length, amp, t, *, head_rise=16, sag=18):
    """A single undulating sine spine sampled tail(left)->head(right). The head end
    RISES so the dragon reads as a climbing serpent; amplitude eases UP toward the
    head so the front dances more than the dragged tail. 2x oversampling keeps the
    discs overlapping into one ribbon."""
    pts = []
    span = max(1, (n - 1) * 2)
    for i in range(span + 1):
        tt = i / span
        x = sx - length // 2 + int(tt * length)
        wave = math.sin(t * 3.0 - tt * 5.6) * amp * (0.55 + 0.45 * tt)
        float_y = feet_y - sag - int(tt * head_rise)
        pts.append((x, int(float_y + wave)))
    return pts


def _dragon_dancers(surf, pts, feet_y, pal, t, *, robes, leg_stagger):
    """Each real segment centre gets a dancer holding a pole up to the body. Distinct
    robe per pole (festival crowd), a clear 2-leg silhouette, and a leg phase
    staggered down the line so the crew reads MARCHING. Legs are clamped to the
    ground baseline so the rear-most dancer never kicks below the deck on a down-beat."""
    night = _nightf(pal)
    j = 0
    for i, (px, py) in enumerate(pts):
        if i % 2:                       # dancers stand under REAL centres only
            continue
        robe = pr._retint_person(robes[j % len(robes)], night)
        robe_dk = _shade(robe, -36)
        sash = _cap_lum((232, 196, 96), pal)
        skin = pr._retint_person((232, 192, 150), night)
        feet = feet_y
        mph = t * 5.0 + (j * leg_stagger)
        bob = int(max(0.0, math.sin(mph)) * 2)
        body_y = feet - 14 + bob
        pygame.draw.polygon(surf, robe, [
            (px - 4, body_y), (px + 4, body_y), (px + 5, feet - 4), (px - 5, feet - 4)])
        pygame.draw.polygon(surf, robe_dk, [
            (px - 4, body_y), (px + 4, body_y), (px + 5, feet - 4), (px - 5, feet - 4)], 1)
        pygame.draw.line(surf, sash, (px - 4, body_y + 5), (px + 4, body_y + 5), 1)
        pygame.draw.circle(surf, skin, (px, body_y - 4), 3)
        pygame.draw.arc(surf, robe_dk, (px - 3, body_y - 8, 7, 7),
                        math.radians(0), math.radians(180), 2)
        # TWO legs, each lifting on opposite halves of the march phase. The lifted
        # foot is clamped to `feet` so no shin ever extends BELOW the ground
        # baseline (the rear dancer was the one clipping on a down-beat).
        for dx, ph in ((-2, 0.0), (2, math.pi)):
            step = int(max(0.0, math.sin(mph + ph)) * 3)
            foot_y = min(feet, feet - step)
            pygame.draw.line(surf, robe_dk, (px + dx, feet - 5),
                             (px + dx + (1 if step else -1), foot_y), 2)
        lift = int(max(0.0, math.sin(t * 3.0 + i)) * 2)
        pygame.draw.line(surf, robe, (px, body_y + 1), (px - 2, body_y - 5 - lift), 2)
        pygame.draw.line(surf, pr._retint_person((120, 90, 56), night),
                         (px - 2, body_y - 5 - lift), (px, py + 5), 2)
        j += 1


def _dragon_body(surf, pts, pal, *, kit):
    """Draw tail->head: a 1px darker OUTLINE sheath, the deep-red scaled back, a
    bright GOLD belly band (the colour-blind value split kept on EVERY segment), a
    CONTINUOUS low sawtooth dorsal ridge with a tooth on every seam (no flat spot
    at the curve apex), and a small per-plate bead."""
    seg_r = 8
    scale = kit['scale']
    belly = kit['belly']; belly_dk = kit['belly_dk']; hi = kit['hi']
    outline = kit['outline']
    for (x, y) in pts:
        pygame.draw.circle(surf, outline, (x, y), seg_r + 1)
    for (x, y) in pts:
        pygame.draw.circle(surf, scale, (x, y), seg_r)
    # Bright GOLD belly discs on the lower arc of EVERY sample so a light belly /
    # dark back value split survives on every segment (never flattens to mid-red).
    for (x, y) in pts:
        pygame.draw.circle(surf, belly_dk, (x, y + seg_r - 3), seg_r - 3)
        pygame.draw.circle(surf, belly, (x, y + seg_r - 3), seg_r - 4)
    # CONTINUOUS dorsal SAWTOOTH: one zigzag polyline along the top edge tail->head.
    # A tooth peak is inserted at EVERY interval (not every other) so the ridge runs
    # unbroken across each segment seam, including the curve apex at the 4th-5th join
    # where the old every-other cadence left a flat spot.
    top = [(x, y - seg_r) for (x, y) in pts]
    ridge = []
    for i in range(0, len(top) - 1):
        x0, y0 = top[i]
        x1, y1 = top[i + 1]
        ridge.append((x0, y0))
        ridge.append(((x0 + x1) // 2, (y0 + y1) // 2 - 4))
    ridge.append(top[-1])
    pygame.draw.lines(surf, kit['ridge_dk'], False, ridge, 2)
    pygame.draw.lines(surf, kit['ridge'], False, ridge, 1)
    for i in range(0, len(pts), 2):
        x, y = pts[i]
        pygame.draw.circle(surf, hi, (x - 2, y - 1), 1)


def _dragon_tail(surf, pt, nxt, pal, *, kit, t):
    """Taper to a single point with ONE small trailing wisp — the head holds the
    only flame locus. A thin pointed fin that sways with the dance."""
    x, y = pt
    sway = int(math.sin(t * 3.0) * 3)
    dx = x - nxt[0]; dy = y - nxt[1]
    tip = (x + (dx if dx else -10), y + dy + sway)
    pygame.draw.polygon(surf, kit['outline'], [(x, y - 6), (x, y + 6), tip])
    pygame.draw.polygon(surf, kit['scale'], [(x, y - 5), (x, y + 5), (tip[0] + 1, tip[1])])
    pygame.draw.line(surf, kit['ridge'], (tip[0], tip[1]),
                     (tip[0] - 4, tip[1] - 3 + sway), 1)


def _dragon_antlers(surf, hx, hy, kit):
    """Two TALL swept-back prongs — regal, the V2 antler. A small ember tip on the
    back prong is one of the two allowed crest glow sources (gold, capped)."""
    horn = kit['horn']; horn_dk = kit['horn_dk']
    base_x, base_y = hx + 1, hy - 6
    for off in (0, 3):
        pygame.draw.line(surf, horn_dk, (base_x - off, base_y),
                         (base_x - off - 4, base_y - 14), 3)
        pygame.draw.line(surf, horn, (base_x - off, base_y),
                         (base_x - off - 4, base_y - 14), 2)
    pygame.draw.circle(surf, kit['gold'], (base_x - 7, base_y - 11), 1)


def _dragon_whisker(surf, jx, jy, pal, t, kit):
    """A SINGLE continuous 1px whisker anchored at the JAW, flicking forward off the
    snout then trailing BACK over the body and TAPERING TO NOTHING — no detached
    endpoint / dotted specks (that was V4's small-size failure). Drawn as a chain of
    overlapping short segments whose width steps 2px->1px->hairline so it fades out
    instead of ending on a bright bead."""
    drift = math.sin(t * 2.2) * 3
    whisk = kit['whisk']
    length = 12
    pts = [(jx, jy)]
    pts.append((jx + 2, jy - 3 + int(drift)))          # a short forward flick
    for s in range(1, 6):
        frac = s / 5.0
        wx = jx + 2 - int(frac * length)
        wy = jy - 3 + int(frac * 7) + int(math.sin(t * 2.2 + s) * 2 + drift)
        pts.append((wx, wy))
    # Step the width down along the trail so it tapers to a hairline; the final
    # link is 1px and lands ON the body, never as a separate glowing dot.
    for i in range(len(pts) - 1):
        w = 2 if i < 2 else 1
        pygame.draw.line(surf, whisk, pts[i], pts[i + 1], w)


def _dragon_head(surf, pt, pal, t, kit):
    """The V2 PROFILE head: domed brow, a snout LIFTED forward (its tip the forward-
    most pixel), tall antlers, ONE dominant 3/4 eye, a ROARING drop-jaw, one trailing
    whisker. A 1px dark line separates the back of the jowl from body segment 1 so
    the head never fuses into the body at the arc apex. ONE amber flame locus."""
    hx, hy = pt
    hy -= 6                                              # SNOUT-LIFT (V2 lift=6)
    hy -= int(max(0.0, math.sin(t * 3.2)) * 2)          # bob
    face = kit['face']; face_dk = kit['face_dk']
    gold = kit['gold']; red = kit['red']; outline = kit['outline']

    # A short scalloped neck-mane behind the head ties it into the body.
    for k, ang in enumerate(range(120, 241, 20)):
        rad = math.radians(ang)
        mx = hx + int(math.cos(rad) * 11)
        my = hy + int(math.sin(rad) * 11)
        c = (gold, red)[k % 2]
        pygame.draw.circle(surf, _shade(c, -26), (mx, my), 3)
        pygame.draw.circle(surf, c, (mx, my), 2)

    # A 1px dark separation line between the back of the head/jowl and the first body
    # segment so the head reads as a distinct mass at the arc apex.
    pygame.draw.line(surf, outline, (hx - 11, hy - 6), (hx - 10, hy + 7), 1)

    snout_tip_x = hx + 18
    skull = [
        (hx - 9, hy - 7), (hx + 3, hy - 8), (hx + 9, hy - 6),
        (snout_tip_x, hy - 4), (snout_tip_x - 2, hy + 1),
        (hx + 9, hy + 3), (hx - 8, hy + 6)]
    pygame.draw.polygon(surf, outline, skull)
    pygame.draw.polygon(surf, face_dk, skull)
    pygame.draw.polygon(surf, face, [
        (hx - 8, hy - 6), (hx + 3, hy - 7), (hx + 8, hy - 5),
        (snout_tip_x - 1, hy - 3), (snout_tip_x - 3, hy), (hx + 8, hy + 2),
        (hx - 7, hy + 4)])
    pygame.draw.line(surf, face_dk, (hx - 6, hy - 5), (hx + 6, hy - 5), 2)

    _dragon_antlers(surf, hx, hy, kit)

    # ONE dominant 3/4 eye under the brow + a much smaller far-eye hint so the read
    # is profile, not frontal. The eye stays one of the two brightest forward accents.
    ex, ey = hx + 3, hy - 1
    pygame.draw.circle(surf, outline, (ex, ey), 3)
    pygame.draw.circle(surf, kit['eye'], (ex, ey), 2)
    pygame.draw.circle(surf, (24, 18, 22), (ex + 1, ey), 1)
    pygame.draw.circle(surf, _shade(kit['eye'], -40), (hx - 2, hy - 2), 1)

    # The ROARING wide drop-jaw (V2 mouth='roar').
    jaw = 3 + int(max(0.0, math.sin(t * 3.2 + 0.4)) * 3)
    mouth_x0, mouth_x1 = hx + 9, snout_tip_x - 2
    pygame.draw.polygon(surf, (22, 14, 18), [
        (mouth_x0, hy + 2), (mouth_x1, hy + 1),
        (mouth_x1 - 1, hy + 2 + jaw), (mouth_x0, hy + 3 + jaw)])
    pygame.draw.line(surf, red, (mouth_x0, hy + 2), (mouth_x1, hy + 1), 1)
    pygame.draw.line(surf, kit['jaw'], (mouth_x0, hy + 3 + jaw),
                     (mouth_x1 - 1, hy + 2 + jaw), 1)
    fx = hx + 11
    pygame.draw.polygon(surf, kit['fang'], [
        (fx - 1, hy + 2), (fx + 1, hy + 2), (fx, hy + 5)])
    pygame.draw.circle(surf, red, (snout_tip_x - 3, hy), 1)

    # One continuous trailing whisker anchored at the JAW hinge.
    _dragon_whisker(surf, hx + 8, hy + 3, pal, t, kit)

    # GLOW: a SINGLE amber/lacquer-orange ember on the crest — cooled away from
    # coin-gold and capped so a head sparkle is never mistaken for a collectible.
    _near_glow(surf, hx + 2, hy - 6, pal, radius=8, color=_DRAGON_GLOW)


def perf_dragon_dance(surf, sx, pal, t, *, skin='red'):
    """NIGHT · the festival's MARQUEE act — a 7-segment serpent DRAGON DANCE carried
    on poles by a distinct per-pole dancer crew, undulating across the front edge.
    A longer, more serpentine SIBLING of perf_lion_dance: same warm red/gold night
    value key and the same capped-glow contract. `skin='red'` (default) ships the
    red/gold dragon; `skin='jade'` selects candidate V5's jade ALT colorway."""
    feet = NEAR_GROUND_Y
    # The bigger festival crowd flanks the act (behind, drawn first) — same cast +
    # placement family as the lion dance so the two acts read as one festival.
    _scaled_cast(surf, pr.draw_strollers, sx - 60, pal, 1.5, t=t, feet_y=feet,
                 variant=4)
    _scaled_cast(surf, pr.draw_kids, sx - 80, pal, 1.55, t=t, n=3, feet_y=feet)
    _scaled_cast(surf, pr.draw_old_man, sx + 70, pal, 1.55, t=t,
                 seated_bench=False, variant=0, feet_y=feet)

    kit = _dragon_kit(pal, skin)
    # 7 segments, V3 body rhythm; the LOCKED V2 dancer phasing (leg_stagger=1.4).
    pts = _dragon_spine(sx, feet, 7, 156, amp=10, t=t)
    _dragon_dancers(surf, pts, feet, pal, t, robes=_DRAGON_ROBES, leg_stagger=1.4)
    _dragon_tail(surf, pts[0], pts[1], pal, kit=kit, t=t)
    _dragon_body(surf, pts, pal, kit=kit)
    _dragon_head(surf, pts[-1], pal, t, kit)


# ── a tall festival BANNER pole for the night/dusk near edge (clear zone only) ─

def _near_banner(surf, sx, pal, *, feet_y=NEAR_GROUND_Y):
    """A near darchog-style banner pole at the front edge — a vertical accent that
    only stands in a clear horizontal zone (it's tall). Banner colour warms by
    biome; lantern at the top is capped + gated at night."""
    night = _nightf(pal)
    banner = _mix((190, 60, 50), (70, 64, 96), 0.30 * night)
    draw_darchog_pole(surf, sx, feet_y, 40, banner)
    if _is_dark(pal):
        # draw_darchog_pole tops the pole with an uncapped gold finial (220,180,60)
        # that spiked over the night cap; overpaint it capped at night.
        pygame.draw.circle(surf, _cap_lum((210, 175, 90), pal), (sx, feet_y - 40), 2)
        # A small paper lantern hung at the pole top, drawn from scratch with a
        # CAPPED warm shell so its core never out-shines the coin (the game helper
        # paints an uncapped near-white core + bright body that spiked the cap).
        lcy = feet_y - 40
        shell = _cap_lum((150, 70, 60), pal)
        shell_lt = _cap_lum((150, 96, 80), pal)
        pygame.draw.line(surf, (40, 30, 25), (sx, lcy), (sx, lcy + 3), 1)
        pygame.draw.ellipse(surf, shell, (sx - 4, lcy + 3, 8, 11))
        pygame.draw.ellipse(surf, shell_lt, (sx - 3, lcy + 4, 6, 9))
        pygame.draw.rect(surf, (50, 34, 26), (sx - 3, lcy + 3, 6, 2))
        pygame.draw.rect(surf, (50, 34, 26), (sx - 3, lcy + 12, 6, 2))
        _near_glow(surf, sx, lcy + 8, pal, radius=10, color=(255, 150, 100))


# ══════════════════════════════════════════════════════════════════════════
# Per-phase near-lane painters. General near life in every phase + the phase's
# performance, drawn back-to-front within the lane. World-anchored at NEAR_MULT.
# ══════════════════════════════════════════════════════════════════════════

def _general_pedestrians(surf, w, scroll, pal, t, density=1.0):
    """A couple of LARGER pedestrians + the near dog on the front edge, at FIXED
    world spacing so they stay pinned to the deck (no per-frame slide). `density`
    thins them via a STABLE per-slot gate — each slot pops in/out once as the
    crowd curve rises/falls, but never changes x. Short, so they may pass under
    the bird/pillar lanes; world-anchored, tiling at the wrap."""
    # Inclusion AND the pool variant are latched together at entry (off-screen):
    # the variant is frozen to the slot's entry beat/weather so it never re-rolls
    # mid-screen, and it rides into _scaled_cast's cache key (smooth=True gives the
    # near figure light anti-aliasing; the FAR lane stays crisp).
    ny = NEAR_GROUND_Y

    def _ped_decide(k):
        return (pr._slot_on(k, 1, density),
                _fv.select_variant('pedestrian', _fv.slot_seed(k, 31),
                                   _fv.beat_for_phase(pr._CUR_PHASE),
                                   _fv.weather_bucket(pr._CUR_RAIN, pr._CUR_SNOW)))
    for sx, k in _near_xs(scroll, w, 196, x0=20):
        on, var = sp._slot_latch(('ped', 1), k, lambda k=k: _ped_decide(k))
        if on:
            _zbuf.enqueue(ny, TB_CAST, lambda s, sx=sx, var=var: _scaled_cast(
                s, pr.draw_strollers, sx, pal, 1.6, t=t, variant=var))
    sp._latch_prune(('ped', 1))
    def _kid_decide(k):
        return (pr._slot_on(k, 2, density),
                _fv.select_variant('kid', _fv.slot_seed(k, 41),
                                   _fv.beat_for_phase(pr._CUR_PHASE), _fv.WB_CLEAR))
    for sx, k in _near_xs(scroll, w, 224, x0=150):
        on, kvar = sp._slot_latch(('ped', 2), k, lambda k=k: _kid_decide(k))
        if on:
            _zbuf.enqueue(ny, TB_CAST, lambda s, sx=sx, kvar=kvar: _scaled_cast(
                s, pr.draw_kids, sx, pal, 1.55, t=t, n=2, variant=kvar))
    sp._latch_prune(('ped', 2))
    # A varied pooled dog ambles across the front on its own anchor — breed frozen
    # per slot so it doesn't re-roll mid-screen, and rides the bake cache key.
    def _dog_decide(k):
        return (pr._slot_on(k, 3, density),
                _fv.select_variant('dog', _fv.slot_seed(k, 51),
                                   _fv.beat_for_phase(pr._CUR_PHASE), _fv.WB_CLEAR))
    for sx, k in _near_xs(scroll, w, 300, x0=96):
        on, dvar = sp._slot_latch(('ped', 3), k, lambda k=k: _dog_decide(k))
        if on:
            _zbuf.enqueue(ny, TB_CAST, lambda s, sx=sx, dvar=dvar: _scaled_cast(
                s, pr.draw_dog, sx, pal, 1.5, t=t, variant=dvar))
    sp._latch_prune(('ped', 3))


# The LIVING near crowd is now driven by the stateful game.sidewalk_crowd sim so
# each figure walks at its own pace (two-way facing, pauses, dogs darting) instead
# of the uniform world-locked tiling above (kept as `_general_pedestrians`, the
# fallback when no crowd is wired). Draw scale/drawer per kind; the entity's
# world_x maps to sx via the SAME `world_x - scroll` the planted statics use, so a
# standing entity is pixel-locked to the ground.
_CROWD_DRAW = {
    "stroller": (pr.draw_strollers, 1.6, {}),
    "kids":     (pr.draw_kids, 1.55, {"n": 2}),
    "dog":      (pr.draw_dog, 1.5, {}),
}


def _emit_near_crowd(surf, crowd, scroll, pal):
    ny = NEAR_GROUND_Y
    for e in crowd.near:
        drawer, scale, kw = _CROWD_DRAW[e.kind]
        sx = int(round(e.world_x - scroll))
        flip = e.facing > 0
        _zbuf.enqueue(ny, TB_CAST, lambda s, drawer=drawer, sx=sx, scale=scale,
                      g=e.gait, flip=flip, kw=kw: _scaled_cast(
                          s, drawer, sx, pal, scale, t=g, flip=flip, **kw))


def _general_greenery(surf, w, scroll, pal, t, fd=1.0):
    """Near-lane greenery accents — a vine tub + the odd pine. The pooled potted
    plants now live in the far-band cluster beds on the sidewalk (see
    foreground_promenade._draw_greenery_cluster), so the front edge is kept open
    rather than jammed with large low pots. Fixtures, so thinned by the phase-only
    furniture density `fd` via a stable per-slot gate (present from t=0, no flicker)
    and spaced on wide periods; the taller pine is gated to a clear zone."""
    ny = NEAR_GROUND_Y

    for sx, k in _near_static_xs(scroll, w, 520, x0=200):
        if sp._slot_latch(('grn', 22), k, lambda k=k: pr._slot_on(k, 22, fd)):
            _zbuf.enqueue(ny, TB_FIXTURE, lambda s, sx=sx: _near_vine_lantern(s, sx, pal))
    sp._latch_prune(('grn', 22))
    for sx, k in _near_static_xs(scroll, w, 480, x0=12):
        if sp._slot_latch(('grn', 23), k, lambda k=k: pr._slot_on(k, 23, fd)):
            _zbuf.enqueue(ny, TB_FIXTURE, lambda s, sx=sx: _near_pine(s, sx, pal))
    sp._latch_prune(('grn', 23))


# A performance (performer + its own crowd) is itself a scene cluster; place it at
# world-x slots so it scrolls past at the near-lane speed and recycles, instead of
# riding the camera. Sparser than the general near life so a performance reads as a
# distinct event the bird passes.
_PERF_PERIOD = 720
_PERF_MARGIN = 220
_PERF_X0 = 120          # single unified performer grid (all acts share it)

# ── DEAD per-phase painter path — NOT in the live call chain ───────────────────
# `_perform`, `_perform_festival`, the `phase_*` painters, and `add_near_lane`
# below are the OLD per-phase dispatch, superseded by the live `draw_near_lane`
# director (which routes through `foreground.draw_near_lane`). Nothing calls
# `add_near_lane` anywhere in the project. Kept only as reference scaffolding.
# IMPORTANT: their placement loops are UNLATCHED — they would reintroduce the
# in-place pop/morph bug. Do not wire this path back in without converting every
# loop to `sp._slot_latch` / `sp._latch_prune` like the live director does.

def _perform(surf, w, scroll, pal, t, perf_fn, x0):
    """A single-act busker (juggler/musician/stilt) — placed at only ~1 in 4
    performance slots (stable per-slot gate), so it reads as a lucky encounter the
    bird happens to pass, NOT a metronome. The NIGHT festival uses _perform_festival
    instead and stays frequent — that density IS the headline event."""
    for bx, k in _near_xs(scroll, w, _PERF_PERIOD, x0=x0, margin=_PERF_MARGIN):
        if not pr._slot_on(k, 7, 0.25):
            continue
        perf_fn(surf, bx, pal, t)


def _perform_festival(surf, w, scroll, pal, t, x0):
    """The NIGHT festival's headline run — the LION dance and the marquee DRAGON
    dance ALTERNATE per world-anchored performance slot (by slot index `k`), so the
    bird passes a lion, then a dragon, then a lion… The slot index is world-anchored,
    so which act sits in a slot is stable across the scroll wrap (no flicker)."""
    for bx, k in _near_xs(scroll, w, _PERF_PERIOD, x0=x0, margin=_PERF_MARGIN):
        if k % 2:
            perf_dragon_dance(surf, bx, pal, t)   # the marquee act
        else:
            perf_lion_dance(surf, bx, pal, t)


def phase_day(surf, w, gy, h, scroll, pal, t):
    """DAY · Pastoral Morning. Front edge: larger pedestrians + dog + planters; a
    casual BUSKER / juggler performs as the bird passes. No glow."""
    _general_greenery(surf, w, scroll, pal, t)
    _general_pedestrians(surf, w, scroll, pal, t)
    _perform(surf, w, scroll, pal, t, perf_juggler, x0=40)


def phase_golden(surf, w, gy, h, scroll, pal, t):
    """GOLDEN HOUR · Promenade. Front edge fills out: a STREET MUSICIAN with a small
    head-bobbing watching arc. Warm, still unlit."""
    _general_greenery(surf, w, scroll, pal, t)
    _general_pedestrians(surf, w, scroll, pal, t)
    _perform(surf, w, scroll, pal, t, perf_musician, x0=200)


def phase_dusk(surf, w, gy, h, scroll, pal, t):
    """DUSK · Lamps Lighting. The crowd grows and a STILT-WALKER warms up as the
    lamps come on; near banner poles + braziers glow as they pass."""
    _general_greenery(surf, w, scroll, pal, t)
    _general_pedestrians(surf, w, scroll, pal, t)
    for sx, k in _near_xs(scroll, w, 340, x0=30):
        _near_banner(surf, sx, pal)
    for sx, k in _near_xs(scroll, w, 300, x0=120):
        _near_brazier(surf, sx, pal, t=t)
    _perform(surf, w, scroll, pal, t, perf_stilt, x0=120)


def phase_night(surf, w, gy, h, scroll, pal, t):
    """NIGHT · Festival. The peak: a full LION DANCE + drummer + crowd passes on the
    front edge, with braziers + banners glowing (all capped). The coin + parrot
    still draw after this and stay brightest."""
    _general_greenery(surf, w, scroll, pal, t)
    _general_pedestrians(surf, w, scroll, pal, t)
    for sx, k in _near_xs(scroll, w, 340, x0=30):
        _near_banner(surf, sx, pal)
    for sx, k in _near_xs(scroll, w, 280, x0=110):
        _near_brazier(surf, sx, pal, t=t)
    _perform_festival(surf, w, scroll, pal, t, x0=320)


# Dispatch by phase NAME (day/golden/dusk/night) — the render harness derives the
# name per column from the PHASES list.
_DISPATCH = {
    "day": phase_day,
    "golden": phase_golden,
    "dusk": phase_dusk,
    "night": phase_night,
}


def add_near_lane(surf, w, gy, h, scroll, pal, phase_name, t):
    """Paint the NEAR / FRONT activity lane on top of the far lane (and under the
    gameplay actors). Dispatches general near life + the phase's performance."""
    painter = _DISPATCH.get(phase_name, phase_day)
    painter(surf, w, gy, h, scroll, pal, t)


# ── live composition: the day-arc DIRECTOR (mirrors the promenade) ─────────────
#
# One performance act per time-of-day, the front crowd thinned by the same
# crowd-density curve + run-start fill the promenade uses, in a single pass (no
# crossfade double-draw). The performer escalation IS the night build-up:
# juggler (day) -> musician (golden) -> stilt-walker (dusk) -> the NIGHT festival
# (LION dance + the marquee DRAGON dance, alternating per slot — handled inline in
# draw_near_lane via _perform_festival, not here, since that window runs TWO acts).

def _perf_for(phase):
    """(performer_fn, x0) for the SINGLE-act phases (day/golden/dusk), else None.
    The NIGHT festival window (0.58..0.80) is handled by the caller (`_perf_decide`),
    and 0.80..0.85 is the pre-dawn teardown (no act) — both return None here."""
    p = phase % 1.0
    if p >= 0.85 or p < 0.25:
        return (perf_juggler, 40)
    if p < 0.40:
        return (perf_musician, 200)
    if p < 0.58:
        return (perf_stilt, 120)
    return None                          # 0.58..0.85: festival (caller) / pre-dawn

def _perf_band(p):
    """The performer beat-band for a day-arc phase (festival 0.58..0.80 + the
    0.80..0.85 teardown are handled by the caller and return None here)."""
    if p >= 0.85 or p < 0.25:
        return "day"
    if p < 0.40:
        return "golden"
    if p < 0.58:
        return "dusk"
    return None


def _pooled_perf(variant):
    """Wrap a frozen 'performer' pool index as the act callable the director invokes
    — draws the shared draw_act at the near deck with the live night factor."""
    v = _fv.get("performer", variant)

    def _draw(s, bx, pal, t):
        if v is not None:
            _pf.draw_act(s, bx, NEAR_GROUND_Y, v, _nightf(pal), t)
    return _draw


def _perf_decide(k, phase, density):
    """The act a performer slot holds (or None) — sampled ONCE at slot entry and
    latched. Festival window: lion/dragon alternate every slot; otherwise a busker
    FROZEN from the time-appropriate beat band of the 8-act 'performer' pool (so the
    bird passes a varied cast, not the same act on a metronome), at the sparse
    1-in-4 gate. The busy-street gate (density>0.25) is captured here too, so a slot
    that opened during a busy stretch keeps its act as the street empties around it."""
    if density <= 0.25:
        return None
    p = phase % 1.0
    if 0.58 <= p < 0.80:
        return perf_dragon_dance if (k % 2) else perf_lion_dance
    if not pr._slot_on(k, 7, 0.25):
        return None
    band = _perf_band(p)
    if band is None:
        return None
    idxs = _pf.PERFORMERS_BY_BEAT[band]
    variant = idxs[_fv.slot_seed(k, 73) % len(idxs)]
    return _pooled_perf(variant)

def draw_near_lane(surf, scroll, pal, phase, t, crowd=None):
    """Draw the near/front activity lane + the time-appropriate performance, thinned
    by the day-arc crowd density and filling in from empty at run-start. When a
    `crowd` (game.sidewalk_crowd.SidewalkCrowd) is wired, the living pedestrians/
    dogs come from that stateful sim (independent walking); otherwise the legacy
    world-locked `_general_pedestrians` is used as a fallback."""
    # _scaled_cast borrows pr._stepped, so keep the cache clock current.
    pr._CUR_BUCKET = _biome.phase_bucket(phase)
    pr._CUR_T = t
    pr._CUR_PAL = pal
    pr._CUR_PHASE = phase
    # Same day-arc density as the far lane, thinned by the weather so the near
    # edge empties out in a storm too (promenade sets pr._CUR_RAIN/SNOW/WIND just
    # before this call, so the umbrella gate downstream reads the live weather).
    density = pr._population(phase) * pr._run_fill(t) * pr._weather_crowd_factor(phase)
    _general_greenery(surf, W, scroll, pal, t, pr._furn_density(phase))  # fixtures, sparse
    if crowd is not None:
        _emit_near_crowd(surf, crowd, scroll, pal)
    else:
        _general_pedestrians(surf, W, scroll, pal, t, density)
    p = phase % 1.0
    # Festival banners + braziers: discrete world slots, each latching its window
    # membership at entry so the row scrolls in/out instead of the on-screen ones
    # blinking when the festival window opens/closes.
    banner_win = (0.45 <= p < 0.86)
    ny = NEAR_GROUND_Y
    for sx, k in _near_static_xs(scroll, W, 340, x0=30):
        on, bv = sp._slot_latch(('banner',), k, lambda k=k: (
            banner_win, pr._prop_latch('prop_banner', k, 41)))
        if on:
            _zbuf.enqueue(ny, TB_STRUCTURE, lambda s, sx=sx, bv=bv: _scaled_cast(
                s, pr.draw_prop_banner, sx, pal, 1.5, t=t, variant=bv))
    sp._latch_prune(('banner',))
    for sx, k in _near_static_xs(scroll, W, 290, x0=115):
        on, fvar = sp._slot_latch(('brazier',), k, lambda k=k: (
            banner_win, pr._prop_latch('prop_fire', k, 42)))
        if on:
            _zbuf.enqueue(ny, TB_FIXTURE, lambda s, sx=sx, fvar=fvar: _scaled_cast(
                s, pr.draw_prop_fire, sx, pal, 1.5, t=t, variant=fvar))
    sp._latch_prune(('brazier',))
    # Performers: ONE world-anchored grid. Each slot latches at entry both whether
    # it is occupied (busy-street gate) and WHICH act it holds, so a busker never
    # morphs (juggler->musician etc.) or blinks (density crossing 0.25, day<->festival)
    # while on screen — it performs its act for the whole pass and scrolls off.
    for bx, k in _near_static_xs(scroll, W, _PERF_PERIOD, x0=_PERF_X0, margin=_PERF_MARGIN):
        act = sp._slot_latch(('perf',), k,
                             lambda k=k: _perf_decide(k, phase, density))
        if act is not None:
            _zbuf.enqueue(ny, TB_CAST, lambda s, act=act, bx=bx: act(s, bx, pal, t))
    sp._latch_prune(('perf',))
