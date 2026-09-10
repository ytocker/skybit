"""
Registry over the 10 biome sky designs + the live-sky activation path.

A single catalog behind one signature — `render(surf, w, h, ground_y, palette,
phase)` — so the live sky can be swapped for any of these designs. Each design
carries its OWN per-biome day/night palette (via its keyframes) and keys off
`phase` (0..1) — the same phase the live biome clock already produces — so it
ignores the live `palette` argument entirely.

`ACTIVE_SKY_DESIGN` selects which design (if any) is live. `render_active` paints
that design's sky using the SAME per-phase-bucket bake + two-bucket alpha blend
as the live biome path (`scenes._draw_background`), so a slowly-changing phase
reads as a continuous fade rather than 32 discrete steps. `active_cloud_palette`
hands the design's per-phase sky palette to the cloud painter so clouds retint to
match the active sky. While `ACTIVE_SKY_DESIGN is None` both short-circuit and the
live render path is untouched.
"""
from collections import OrderedDict

from game import biome as _biome
from game.biome_sky import paint_sky
from game.biome_sky_keyframes import BIOMES, BIOME_NAMES, BIOME_NOTES

import pygame


# The active switch. Set to a CATALOG design id to make that sky live; None keeps
# the original shan-shui biome sky.
ACTIVE_SKY_DESIGN = "alpine_haze"


def _make_render(design_id):
    """Bind one biome spec into the shared render signature. Designs supply
    their own palette, so the live `palette` arg is intentionally ignored."""
    spec = BIOMES[design_id]

    def render(surf, w, h, ground_y, palette, phase):
        paint_sky(surf, spec, w, h, phase, stars=True, ground_y=ground_y)

    return render


def render(surf, w, h, ground_y, palette, phase):
    """Render the currently-active design's sky. Caller must ensure
    `ACTIVE_SKY_DESIGN` is set; use `render_active` for the guarded form."""
    _CATALOG_BY_ID[ACTIVE_SKY_DESIGN](surf, w, h, ground_y, palette, phase)


# (design_id, human_name, note, render_fn) for the 10 biome designs, sheet order.
CATALOG = [
    (bid, BIOME_NAMES[bid], BIOME_NOTES[bid], _make_render(bid))
    for bid in BIOMES
]

_CATALOG_BY_ID = {bid: fn for bid, _name, _note, fn in CATALOG}


# Per-(design, size, bucket) baked sky surfaces. `paint_sky` is an OKLab bake, so
# we bake once per phase bucket and reuse, keeping the per-frame cost to two
# cached blits. Bounded LRU: only the two adjacent buckets are needed per frame,
# so a handful of resident surfaces covers the active pair plus hysteresis — this
# keeps RAM flat (~6 x ~0.9 MB) no matter how fine PHASE_BUCKETS gets.
_SKY_CACHE_MAX = 6
_sky_cache: "OrderedDict[tuple, pygame.Surface]" = OrderedDict()


def _design_sky(design_id, w, h, ground_y, bucket):
    key = (design_id, w, h, bucket)
    surf = _sky_cache.get(key)
    if surf is not None:
        _sky_cache.move_to_end(key)
        return surf
    surf = pygame.Surface((w, h))
    paint_sky(surf, BIOMES[design_id], w, h, bucket / _biome.PHASE_BUCKETS,
              stars=True, ground_y=ground_y)
    _sky_cache[key] = surf
    if len(_sky_cache) > _SKY_CACHE_MAX:
        _sky_cache.popitem(last=False)
    return surf


def render_active(surf, w, h, ground_y, palette, phase) -> bool:
    """Paint the active design's sky onto `surf`, blending two adjacent phase
    buckets for a continuous fade. Returns True when a design painted; False
    (without touching `surf`) when the registry is dormant, so the caller can
    fall through to the live biome sky."""
    if ACTIVE_SKY_DESIGN is None or ACTIVE_SKY_DESIGN not in BIOMES:
        return False
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    b = (a + 1) % buckets
    t = bucket_f - int(bucket_f)
    sky_a = _design_sky(ACTIVE_SKY_DESIGN, w, h, ground_y, a)
    sky_b = _design_sky(ACTIVE_SKY_DESIGN, w, h, ground_y, b)
    sky_a.set_alpha(None)
    surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255))
        surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)
    return True


def active_cloud_palette(phase, base_palette):
    """The palette clouds should tint from while a design is active: the live
    palette with the design's per-phase sky keys (`sky_top/mid/bot`, `horizon`,
    `star_alpha`) layered on top. Returns None when dormant so callers keep the
    live palette. The merge keeps every non-sky key present, so no cloud variant
    can KeyError on the sky-only design palette."""
    if ACTIVE_SKY_DESIGN is None or ACTIVE_SKY_DESIGN not in BIOMES:
        return None
    return {**base_palette, **BIOMES[ACTIVE_SKY_DESIGN].palette_for_phase(phase)}
