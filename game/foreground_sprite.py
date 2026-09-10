"""Shared bake-and-cache for sidewalk sprites (far + near lanes).

A drawer paints its figure onto a scratch at an authoring resolution, then the
result is resampled to the on-screen footprint and cached. Two resample modes:

  * NEAREST  — crisp pixel-art enlargement (the legacy near-lane look).
  * smoothscale — bilinear; used to DOWNSAMPLE a richly-drawn supersampled
    scratch to the footprint, which anti-aliases the extra detail (the
    "higher-resolution" path).

The caller supplies a `render(scratch)` callback (so this module stays decoupled
from the lane modules — no import cycle) and a fully-formed cache `key`. The dim
multiply, when used, is applied to the scratch BEFORE resampling so a smoothscale
averages already-dimmed pixels (the order a bilinear downscale needs; for NEAREST
it is equivalent). Pygbag-safe: only Surface + transform.scale/smoothscale.
"""
from __future__ import annotations

import pygame

# A sprite is identical for a given (fn, footprint, mode, palette-bucket,
# animation-frame, variant, ...) wherever it's placed, so one bake serves every
# instance on a frame and across frames within an animation bucket. Variants ×
# biome buckets × gait frames grow the working set, so the cache is larger than
# the old 384 and evicts OLDEST-FIRST (a full clear would wipe the live working
# set every few frames under festival density and thrash).
_SPRITE_CACHE: dict = {}
_CACHE_CAP = 1536


def _evict():
    # Dicts preserve insertion order; drop the oldest entries past the cap.
    while len(_SPRITE_CACHE) > _CACHE_CAP:
        _SPRITE_CACHE.pop(next(iter(_SPRITE_CACHE)))


def baked_sprite(key, render_box, footprint, render, *, dim=None, smooth=False,
                 flip=False):
    """Return the cached sprite for `key`, baking it on a miss.

    `render(scratch)` paints the figure onto a fresh `render_box` SRCALPHA surface
    (feet at the bottom edge). The scratch is dimmed (optional) then resampled to
    `footprint` — smoothscale for supersampled detail, else NEAREST. `flip`
    mirrors the baked sprite horizontally (for facing) once, so the flip is cached
    under `key` (the caller must fold `flip` into the key). The returned surface's
    feet sit on its bottom edge; the caller blits it to the deck."""
    sp = _SPRITE_CACHE.get(key)
    if sp is not None:
        return sp
    scratch = pygame.Surface(render_box, pygame.SRCALPHA)
    render(scratch)
    if dim is not None:
        scratch.fill((dim[0], dim[1], dim[2], 255),
                     special_flags=pygame.BLEND_RGBA_MULT)
    fw = max(1, int(footprint[0]))
    fh = max(1, int(footprint[1]))
    if smooth:
        sp = pygame.transform.smoothscale(scratch, (fw, fh))
    else:
        sp = pygame.transform.scale(scratch, (fw, fh))
    if flip:
        sp = pygame.transform.flip(sp, True, False)
    _SPRITE_CACHE[key] = sp
    _evict()
    return sp


def cache_stats():
    """(entries, cap) — for perf checks."""
    return len(_SPRITE_CACHE), _CACHE_CAP
