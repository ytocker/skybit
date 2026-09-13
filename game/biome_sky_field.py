"""
Sky color-field engine — the shared "stop looking like a flat gradient" layer.

A plain vertical sRGB lerp between four evenly-spaced stops reads as a cheap
"PowerPoint gradient": midpoints slump through the muddy grey middle of sRGB,
the steps land unevenly to the eye, and 8-bit quantization bands visibly across
a ~600px-tall sky. This module fixes all three at bake time so every sky
treatment is built on the same high-end foundation:

  * Perceptual interpolation in OKLab — midpoints stay vibrant instead of going
    grey, and equal positional steps read as equal visual steps.
  * Arbitrary count + non-uniform placement of stops with smoothstep easing, so
    a sky can compress most of its change into the horizon the way real air does.
  * Ordered (Bayer 8x8) dithering to dissolve banding into a sub-pixel grain —
    the "higher-resolution"/10-bit feel without a real 10-bit surface.

Everything here runs on the cache-miss (bake) path only — never per pixel per
frame — so it is free on the per-frame budget and safe on the pygbag/WASM
target (pure Python + standard SDL blits; no numpy/surfarray/native calls).
"""
import math
import pygame

# ── OKLab perceptual color (Björn Ottosson) ──────────────────────────────────
# We interpolate sky stops in OKLab rather than sRGB because a straight sRGB
# lerp between, say, a dawn blue and a peach horizon dips through a desaturated
# grey at the midpoint; OKLab keeps the arc vivid and perceptually even.

def _srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
    c = 0.0 if c < 0.0 else (1.0 if c > 1.0 else c)
    v = c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1.0 / 2.4)) - 0.055
    return int(v * 255.0 + 0.5)


def srgb_to_oklab(rgb):
    r = _srgb_to_linear(rgb[0])
    g = _srgb_to_linear(rgb[1])
    b = _srgb_to_linear(rgb[2])
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = l ** (1.0 / 3.0), m ** (1.0 / 3.0), s ** (1.0 / 3.0)
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_srgb(lab):
    L, a, b = lab
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return (_linear_to_srgb(r), _linear_to_srgb(g), _linear_to_srgb(bb))


def oklab_lerp(c0, c1, t):
    """Perceptually-even blend between two sRGB colors via OKLab."""
    a, b = srgb_to_oklab(c0), srgb_to_oklab(c1)
    return oklab_to_srgb((a[0] + (b[0] - a[0]) * t,
                          a[1] + (b[1] - a[1]) * t,
                          a[2] + (b[2] - a[2]) * t))


def _smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def oklab_ramp(stops, n, *, ease=True):
    """Bake `n` sRGB rows from positional OKLab `stops` = [(pos, (r,g,b)), ...]
    sorted ascending on pos in [0,1]. Within each segment the blend is eased
    (smoothstep) so stop boundaries are soft rather than visibly kinked."""
    stops = sorted(stops, key=lambda s: s[0])
    lab = [(p, srgb_to_oklab(c)) for p, c in stops]
    out = []
    seg = 0
    for i in range(n):
        u = i / max(1, n - 1)
        while seg < len(lab) - 2 and u > lab[seg + 1][0]:
            seg += 1
        p0, a = lab[seg]
        p1, b = lab[seg + 1]
        span = p1 - p0
        t = (u - p0) / span if span > 1e-6 else 0.0
        t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
        if ease:
            t = _smoothstep(t)
        out.append(oklab_to_srgb((a[0] + (b[0] - a[0]) * t,
                                  a[1] + (b[1] - a[1]) * t,
                                  a[2] + (b[2] - a[2]) * t)))
    return out


# ── ordered dithering ─────────────────────────────────────────────────────────
# Classic 8x8 Bayer threshold matrix. Tiled across the sky and applied as a
# tiny signed offset, it scatters the 8-bit rounding error into a fixed grain
# the eye averages out — the single biggest "this isn't a cheap gradient" cue.
_BAYER8 = (
    ( 0, 32,  8, 40,  2, 34, 10, 42),
    (48, 16, 56, 24, 50, 18, 58, 26),
    (12, 44,  4, 36, 14, 46,  6, 38),
    (60, 28, 52, 20, 62, 30, 54, 22),
    ( 3, 35, 11, 43,  1, 33,  9, 41),
    (51, 19, 59, 27, 49, 17, 57, 25),
    (15, 47,  7, 39, 13, 45,  5, 37),
    (63, 31, 55, 23, 61, 29, 53, 21),
)

# Cache the tiled add/sub dither overlays per (w, h, amp) — they are independent
# of palette, so all 32 phase buckets at a given size reuse one pair.
_dither_cache: dict = {}


def _dither_overlays(w, h, amp):
    key = (w, h, amp)
    cached = _dither_cache.get(key)
    if cached is not None:
        return cached
    # Build two 8x8 tiles: `pos` brightens, `neg` darkens. A threshold of 0..63
    # maps to a signed offset in roughly [-amp, +amp).
    pos_tile = pygame.Surface((8, 8))
    neg_tile = pygame.Surface((8, 8))
    for ty in range(8):
        for tx in range(8):
            off = ((_BAYER8[ty][tx] + 0.5) / 64.0 - 0.5) * 2.0 * amp
            p = max(0, int(round(off)))
            n = max(0, int(round(-off)))
            pos_tile.set_at((tx, ty), (p, p, p))
            neg_tile.set_at((tx, ty), (n, n, n))
    # Tile each 8x8 into a full (w, h) overlay via a strip-then-stack blit so we
    # never touch individual pixels at sky resolution.
    def _tile(t):
        strip = pygame.Surface((w, 8))
        for x in range(0, w, 8):
            strip.blit(t, (x, 0))
        full = pygame.Surface((w, h))
        for y in range(0, h, 8):
            full.blit(strip, (0, y))
        return full
    overlays = (_tile(pos_tile), _tile(neg_tile))
    _dither_cache[key] = overlays
    return overlays


# ── the field builder ─────────────────────────────────────────────────────────

def make_sky_field(w, h, stops, *, dither=True, dither_amp=2.0, ease=True):
    """Bake an opaque w x h sky from positional OKLab `stops`.

    `stops` = [(pos, (r,g,b)), ...] with pos in [0,1] top→bottom; 5–7 non-
    uniformly placed stops read far richer than four evenly-spaced ones. The
    result is dithered to kill banding unless `dither=False`."""
    surf = pygame.Surface((w, h))
    rows = oklab_ramp(stops, h, ease=ease)
    for y, c in enumerate(rows):
        pygame.draw.line(surf, c, (0, y), (w - 1, y))
    if dither and dither_amp > 0:
        pos, neg = _dither_overlays(w, h, dither_amp)
        surf.blit(pos, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        surf.blit(neg, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
    return surf


# ── art-direction helpers shared by several treatments ───────────────────────

def shift_temperature(rgb, k):
    """Nudge a color warm (k>0: toward amber) or cool (k<0: toward blue) by an
    OKLab-space push along the b/a axes — used to author counter-change and the
    warm horizon wedge without leaving the perceptual space."""
    L, a, b = srgb_to_oklab(rgb)
    return oklab_to_srgb((L, a + 0.010 * k * 0.0, b + 0.060 * k))


def with_value(rgb, dL):
    """Return `rgb` lightened (dL>0) or darkened (dL<0) in OKLab lightness."""
    L, a, b = srgb_to_oklab(rgb)
    L = max(0.0, min(1.0, L + dL))
    return oklab_to_srgb((L, a, b))


def radial_glow(w, h, cx, cy, radius, color, alpha):
    """A soft additive glow blob for horizon bloom / mesh light pools. Returns an
    SRCALPHA surface to blit with BLEND_RGB_ADD over the baked field."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    # Many thin rings so the falloff is smooth — too few and the additive edge
    # reads as a hard arc/object over a dark sky.
    steps = max(48, radius // 2)
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(alpha * (1.0 - i / steps) ** 2.0)
        if a > 0:
            pygame.draw.circle(s, (*color, a), (int(cx), int(cy)), r)
    return s
