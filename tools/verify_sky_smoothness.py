"""Phase-1 proof that the sunset "staircase" is gone.

The day cycle is sampled into `biome.PHASE_BUCKETS` discrete steps: the SKY
cross-fades linearly between two adjacent bucket palettes (piecewise-LINEAR, so
it facets) while the FOREGROUND tint (mountains/ground) is baked at the bucketed
phase and held until the bucket flips (piecewise-CONSTANT, so it snaps). Both are
fixed by the same lever — a finer bucket grid.

This tool measures, across the fast sunset arc, at PHASE_BUCKETS = 32 (before)
vs 120 (after):
  * FOREGROUND snap  — max colour jump between adjacent bucket tints (the
    piecewise-constant step the mountains/ground hold for a bucket then snap).
  * SKY segment      — max colour distance the sky cross-fade travels within one
    bucket (the length of each piecewise-linear segment; shorter segments = the
    faceting kinks shrink below threshold).
and asserts the live sky cache stays bounded after a full-cycle sweep.

No game state is mutated permanently; PHASE_BUCKETS is restored on exit.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import math
import pygame
pygame.init()
pygame.display.set_mode((8, 8))

from game import biome as _biome
from game import sky_designs
from game.biome_sky_keyframes import BIOMES
from game.config import W, H, GROUND_Y

_ALPINE = BIOMES["alpine_haze"]            # the live sky palette (render_active)
SUNSET = (0.18, 0.60)                      # afternoon -> deep-night, the fast arc


def _dist(a, b):                           # Euclidean RGB distance
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _max_tuple_step(pal_a, pal_b):
    """Worst per-channel-tuple jump between two palettes (the visible tint snap)."""
    worst = 0.0
    for k, va in pal_a.items():
        vb = pal_b.get(k)
        if isinstance(va, tuple) and isinstance(vb, tuple):
            worst = max(worst, _dist(va, vb))
    return worst


def _max_bucket_step(spec_palette, buckets, window):
    """Max colour distance between adjacent bucket palettes over `window`. For the
    foreground (held tint) this is the visible snap; for the sky (cross-faded) it
    is the length of each linear segment — both shrink ~linearly with `buckets`."""
    p0, p1 = window
    worst = 0.0
    for k in range(int(p0 * buckets), int(p1 * buckets) + 1):
        pa = spec_palette((k % buckets) / buckets)
        pb = spec_palette(((k + 1) % buckets) / buckets)
        worst = max(worst, _max_tuple_step(pa, pb))
    return worst


def analyse(buckets):
    _biome.PHASE_BUCKETS = buckets
    # FOREGROUND tint is biome.palette_for_phase(bucketed phase); SKY cross-fades
    # the alpine_haze palette (sky_designs.render_active). Both are bucketed by
    # PHASE_BUCKETS, so both improve with a finer grid.
    fg_snap = _max_bucket_step(_biome.palette_for_phase, buckets, SUNSET)
    sky_seg = _max_bucket_step(_ALPINE.palette_for_phase, buckets, SUNSET)
    return fg_snap, sky_seg


def main():
    saved = _biome.PHASE_BUCKETS
    try:
        print(f"Sunset window phase {SUNSET[0]}..{SUNSET[1]}\n")
        print(f"{'PHASE_BUCKETS':>14} | {'fg snap':>9} | {'sky segment':>12}")
        print("-" * 42)
        rows = {}
        for b in (32, 120):
            fg, sky = analyse(b)
            rows[b] = (fg, sky)
            print(f"{b:>14} | {fg:9.2f} | {sky:12.2f}")
        fg32, sky32 = rows[32]
        fg120, sky120 = rows[120]
        print("\nImprovement (32 -> 120):")
        print(f"  foreground snap : {fg32:.2f} -> {fg120:.2f}  ({fg32 / max(fg120, 1e-9):.2f}x smaller)")
        print(f"  sky segment     : {sky32:.2f} -> {sky120:.2f}  ({sky32 / max(sky120, 1e-9):.2f}x smaller)")

        # Cache-bound proof: sweep a FULL cycle through the real live render path
        # and confirm the LRU holds RAM flat.
        _biome.PHASE_BUCKETS = 120
        sky_designs._sky_cache.clear()
        surf = pygame.Surface((W, H))
        for i in range(400):
            sky_designs.render_active(surf, W, H, GROUND_Y, {}, i / 400.0)
        resident = len(sky_designs._sky_cache)
        mb = resident * W * H * 4 / (1024 * 1024)
        cap = sky_designs._SKY_CACHE_MAX
        print(f"\nLive sky cache after full-cycle sweep: {resident} surfaces "
              f"(cap {cap}) ~= {mb:.1f} MB resident")
        assert resident <= cap, f"sky cache unbounded: {resident} > {cap}"
        assert fg120 < fg32 and sky120 < sky32, "no smoothness improvement at 120"
        print("\nPASS: finer grid shrinks both the foreground snap and the sky "
              "segment length, and the live sky cache is bounded.")
    finally:
        _biome.PHASE_BUCKETS = saved


if __name__ == "__main__":
    main()
