"""Convergence harness for the Stage-B PLANT FAMILY UPGRADE — round 2.

The art-director picked CELADON SERENE as the base (best pot + night ramp)
and asked for a convergence round rather than five new themes. So every
candidate here keeps Celadon's foliage value-discipline and its night ramp,
and varies only the POT idiom and the BONSAI trunk gesture:

  A  porcelain (blue-and-white) pot
  B  terracotta pot
  C  ink-wash gnarled S-trunk bonsai (celadon pot)
  D  porcelain pot + ink-wash trunk
  E  celadon glaze + ink-wash trunk

The round-1 failures are fixed across ALL candidates: a stricter night ramp
(value AND chroma drop so nothing reads above mid-gray), a redesigned
cascading vine with a clear draped silhouette over the front-left lip, a
two-value blossom system (dark base mass + distinct lighter clusters),
segmented bamboo canes with nodes + a leaf tuft and NO umbrella crown, and
bonsai cloud-pads separated by a 1px darker valley.

Nothing here is written into game/ — this is a review-sheet generator. The
retint follows the live `_nightf(pal)` convention so plants DARKEN and never
out-glow the coin or the parrot; a coin + a parrot silhouette are dropped
into each night frame as a brightness yardstick.
"""
from __future__ import annotations

import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

# ── biome keyframes lifted from game/biome.py (DAY = keyframe 0, NIGHT) ────────
PAL_DAY = dict(
    stone_mid=(175, 140, 105), stone_dark=(95, 70, 55),
    foliage_top=(140, 220, 110), foliage_mid=(70, 170, 75),
    foliage_dark=(30, 100, 50), sky_top=(40, 110, 200),
)
PAL_NIGHT = dict(
    stone_mid=(80, 100, 150), stone_dark=(30, 45, 85),
    foliage_top=(80, 130, 130), foliage_mid=(35, 80, 90),
    foliage_dark=(10, 35, 55), sky_top=(5, 8, 30),
)


def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _nightf(pal):
    r, g, b = pal.get('sky_top', (60, 120, 200))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return max(0.0, min(1.0, (95.0 - lum) / 75.0))


# Cool night target for foliage — the same blue the live foreground mixes to.
_NIGHT_BLUE = (40, 56, 86)

# Mid-gray ceiling for ANY plant pixel at full night — nothing may read above
# this so the coin/parrot always stay the brightest actors on the deck.
_NIGHT_VALUE_CAP = 132


def _night_cap(c, n):
    """Clamp a colour's luminance below the night ceiling, scaled by `n`."""
    if n <= 0.02:
        return c
    cap = 255 - (255 - _NIGHT_VALUE_CAP) * n
    lum = _lum(c)
    if lum > cap and lum > 0:
        f = cap / lum
        c = (int(c[0] * f), int(c[1] * f), int(c[2] * f))
    return c


def _fol(pal):
    """Foliage sub-palette: at night it loses BOTH value and chroma so no leaf
    out-reads mid-gray. Celadon's value discipline is the shared base."""
    n = _nightf(pal)
    # Pull toward the cool night blue AND desaturate toward its own gray.
    def cool(c, t):
        m = _mix(c, _NIGHT_BLUE, t * n)
        g = (_lum(m),) * 3
        m = _mix(m, g, 0.22 * n)            # chroma drop
        return _night_cap(m, n)
    return {
        'dark': cool(pal['foliage_dark'], 0.34),
        'mid':  cool(pal['foliage_mid'], 0.34),
        'top':  cool(pal['foliage_top'], 0.34),
    }


def _bloom(color, pal, *, day_lift=0):
    """A bloom colour. Day keeps its saturated pop (optionally lifted a value
    for the brighter cluster tier). Night desaturates ~35% AND darkens ~35% so
    a red blossom never rivals the coin."""
    n = _nightf(pal)
    if n <= 0.02:
        return _shade(color, day_lift)
    c = _mix(color, _shade(color, -78), 0.40 * n)      # darken ~35-40%
    g = (_lum(c),) * 3
    c = _mix(c, g, 0.36 * n)                            # desaturate ~35%
    c = _mix(c, (62, 70, 96), 0.22 * n)                # cool toward night
    return _night_cap(c, n)


# ══════════════════════════════════════════════════════════════════════════
# Shared POT primitives — glazed ceramic vessels.
# ══════════════════════════════════════════════════════════════════════════

def _pot_glaze(surf, sx, by, w, h, base, *, rim=True, motif=None, night=0.0):
    """A glazed ceramic pot: tapered body, a lit rim lip, a soft vertical
    sheen. `base` is the day glaze colour; it is cooled + value-capped by
    `night`. Feet rest at `by`."""
    base = _night_cap(_mix(base, (62, 70, 100), 0.34 * night), night)
    top_w = w
    bot_w = max(6, int(w * 0.72))
    x0t, x1t = sx - top_w // 2, sx + top_w // 2
    x0b, x1b = sx - bot_w // 2, sx + bot_w // 2
    body = [(x0t, by - h), (x1t, by - h), (x1b, by), (x0b, by)]
    pygame.draw.polygon(surf, _shade(base, -26), body)
    inner = [(x0t + 1, by - h + 1), (x1t - 1, by - h + 1),
             (x1b, by - 1), (x0b, by - 1)]
    pygame.draw.polygon(surf, base, inner)
    # A soft vertical sheen on the left third — the wet-glaze highlight, but
    # capped at night so it never spikes above the ceiling.
    sheen = _night_cap(_mix(base, (255, 255, 255), 0.22 * (1.0 - 0.5 * night)),
                       night)
    pygame.draw.line(surf, sheen, (x0t + 2, by - h + 2), (x0b + 2, by - 2), 2)
    pygame.draw.line(surf, _shade(base, -34), (x1t - 1, by - h + 1),
                     (x1b - 1, by - 1), 1)
    if rim:
        rim_c = _night_cap(
            _mix(base, (255, 255, 255), 0.30 * (1.0 - 0.55 * night)), night)
        pygame.draw.rect(surf, _shade(base, -22),
                         (x0t - 1, by - h - 2, top_w + 2, 3))
        pygame.draw.line(surf, rim_c, (x0t, by - h - 2), (x1t, by - h - 2), 1)
    if motif is not None:
        my = by - int(h * 0.55)
        mw = int(top_w * 0.86)
        mc = _night_cap(_mix(motif, (40, 50, 80), 0.4 * night), night)
        for i in range(-mw // 2, mw // 2, 4):
            pygame.draw.line(surf, mc, (sx + i, my), (sx + i + 2, my), 1)


def _pot_porcelain(surf, sx, by, w, h, night):
    """Scholar's blue-and-white porcelain: cool white body + a painted RIM BAND
    (the strongest theme cue from round 1) plus a faint body motif. The rim
    band is two pixels of cobalt under the lit lip — protected at night by the
    value cap but kept distinctly cooler/darker than the body so it survives."""
    body = (230, 234, 242)
    _pot_glaze(surf, sx, by, w, h, body, rim=True, night=night)
    top_w = w
    x0, x1 = sx - top_w // 2, sx + top_w // 2
    # Cobalt rim band — the signature. Darker + saturated so it reads at 1x.
    cobalt = _night_cap(_mix((42, 78, 168), (40, 50, 86), 0.42 * night), night)
    pygame.draw.line(surf, cobalt, (x0, by - h + 1), (x1, by - h + 1), 1)
    pygame.draw.line(surf, _shade(cobalt, -18), (x0 + 1, by - h + 2),
                     (x1 - 1, by - h + 2), 1)
    # A couple of cobalt brush dabs on the belly — landscape-motif hint.
    dab = _night_cap(_mix((54, 92, 178), (40, 50, 86), 0.42 * night), night)
    my = by - int(h * 0.5)
    for dx in (-3, 1, 4):
        pygame.draw.line(surf, dab, (sx + dx, my), (sx + dx, my + 2), 1)


def _pot_terracotta(surf, sx, by, w, h, night):
    """Temple terracotta: warm clay body for value contrast against celadon."""
    _pot_glaze(surf, sx, by, w, h, (182, 98, 56), rim=True, night=night)
    # A darker clay collar to ground the warm pot.
    top_w = w
    x0, x1 = sx - top_w // 2, sx + top_w // 2
    band = _night_cap(_mix((132, 64, 38), (40, 50, 86), 0.40 * night), night)
    pygame.draw.line(surf, band, (x0, by - h + 2), (x1, by - h + 2), 1)


def _pot_celadon(surf, sx, by, w, h, night):
    """Celadon glaze — the base family's own soft sage vessel."""
    _pot_glaze(surf, sx, by, w, h, (152, 188, 160), rim=True, night=night)


# ══════════════════════════════════════════════════════════════════════════
# PLANT BUILDING BLOCKS — shared across candidates (Celadon foliage discipline)
# ══════════════════════════════════════════════════════════════════════════

def _leaf_spray(surf, ox, oy, ang, length, col, *, n=4, spread=0.5, lw=1):
    for i in range(n):
        a = ang + (i - (n - 1) / 2) * spread / max(1, n - 1)
        ex = ox + int(math.cos(a) * length)
        ey = oy - int(math.sin(a) * length)
        mx = ox + int(math.cos(a) * length * 0.5)
        my = oy - int(math.sin(a) * length * 0.5) - 1
        pygame.draw.lines(surf, col, False, [(ox, oy), (mx, my), (ex, ey)], lw)


def draw_bamboo(surf, sx, by, pal, pot_fn):
    """Vertical SEGMENTED canes with visible node bands + a small leaf tuft at
    each top. NO umbrella/mushroom canopy — the round-1 Glazed Parade failure."""
    f = _fol(pal)
    n = _nightf(pal)
    pot_fn(surf, sx, by, 18, 12, n)
    cane = _night_cap(_mix((150, 178, 108), (60, 74, 100), 0.34 * n), n)
    cane_dk = _shade(cane, -36)
    cane_lt = _night_cap(_shade(cane, 18), n)
    top = by - 12
    for dx, htop, lean in ((-4, 31, -1), (1, 38, 1), (5, 28, 2)):
        cx = sx + dx
        ct = top - htop
        segs = 5
        # Segmented cane drawn segment-by-segment with a darker NODE band.
        for s in range(segs):
            y0 = top - htop * s // segs
            y1 = top - htop * (s + 1) // segs
            nx0 = cx + int(lean * (s / segs))
            nx1 = cx + int(lean * ((s + 1) / segs))
            pygame.draw.line(surf, cane, (nx0, y0), (nx1, y1 + 1), 2)
            pygame.draw.line(surf, cane_lt, (nx0, y0), (nx1, y1 + 1), 1)
            pygame.draw.line(surf, cane_dk, (nx1 - 1, y1), (nx1 + 1, y1), 2)
        # A small leaf tuft ONLY at the very top of each cane.
        _leaf_spray(surf, cx + lean, ct, 1.55, 9, f['mid'], n=3, spread=0.7)
        _leaf_spray(surf, cx + lean, ct, 1.95, 7, f['top'], n=2, spread=0.5)
        _leaf_spray(surf, cx + lean, ct + 4, 1.25, 6, f['dark'], n=2, spread=0.6)


def _bonsai_pads(surf, pads, f, n):
    """Cloud-pads each ringed with a 1px DARKER valley so neighbours don't
    merge into a blob at 1x (the Scholar's-Courtyard separation trick)."""
    valley = _night_cap(_shade(f['dark'], -22), n)
    for (cx, cy), tw, th in pads:
        # Darker valley ring first, slightly larger, to carve the gap.
        pygame.draw.ellipse(surf, valley,
                            (cx - tw - 1, cy - th - 1, tw * 2 + 2, th * 2 + 2))
        pygame.draw.ellipse(surf, f['dark'], (cx - tw, cy - th, tw * 2, th * 2))
        pygame.draw.ellipse(surf, f['mid'],
                            (cx - tw + 1, cy - th + 1, tw * 2 - 3, th * 2 - 2))
        pygame.draw.ellipse(surf, f['top'],
                            (cx - tw + 2, cy - th, max(2, tw - 2), max(2, th)))


def draw_bonsai_tiered(surf, sx, by, pal, pot_fn):
    """Celadon's tiered literati pine: a leaning trunk with separated pads."""
    f = _fol(pal)
    n = _nightf(pal)
    pot_fn(surf, sx, by, 24, 9, n)
    trunk = _night_cap(_mix((104, 78, 54), (58, 62, 92), 0.32 * n), n)
    top = by - 9
    pts = [(sx - 2, top), (sx + 2, top - 11), (sx + 7, top - 19),
           (sx + 4, top - 28)]
    pygame.draw.lines(surf, _shade(trunk, -26), False, pts, 4)
    pygame.draw.lines(surf, trunk, False, pts, 2)
    pads = (((sx - 8, top - 16), 10, 4), ((sx + 9, top - 21), 8, 3),
            ((sx + 3, top - 29), 7, 3), ((sx - 3, top - 25), 6, 3))
    _bonsai_pads(surf, pads, f, n)


def draw_bonsai_inkwash(surf, sx, by, pal, pot_fn):
    """The donated ink-wash gesture: a gnarled zig-zag S-trunk that kinks left,
    right, left as it climbs — calligraphic. Same separated pads on top."""
    f = _fol(pal)
    n = _nightf(pal)
    pot_fn(surf, sx, by, 24, 9, n)
    trunk = _night_cap(_mix((92, 66, 44), (56, 60, 90), 0.34 * n), n)
    top = by - 9
    # Strong gnarled zig-zag — the elegant ink-wash S.
    pts = [(sx + 1, top), (sx - 5, top - 8), (sx + 4, top - 15),
           (sx - 3, top - 22), (sx + 5, top - 29)]
    pygame.draw.lines(surf, _shade(trunk, -28), False, pts, 4)
    pygame.draw.lines(surf, trunk, False, pts, 2)
    # A bare jutting deadwood twig — the literati signature.
    pygame.draw.line(surf, _shade(trunk, -12),
                     (sx - 5, top - 8), (sx - 9, top - 11), 1)
    pads = (((sx - 8, top - 20), 9, 3), ((sx + 8, top - 26), 8, 3),
            ((sx + 4, top - 31), 6, 3))
    _bonsai_pads(surf, pads, f, n)


def draw_flower(surf, sx, by, pal, pot_fn):
    """Two-value BLOSSOM SYSTEM: a darker-green lobed base mass, then 3-5
    DISTINCT lighter blossom CLUSTERS (not scattered single pixels). Day lifts
    the cluster a value; night desaturates so reds never rival the coin."""
    f = _fol(pal)
    n = _nightf(pal)
    pot_fn(surf, sx, by, 20, 11, n)
    top = by - 11
    # Lobed dark base mass — two overlapping domes for a natural shrub read.
    for cx, cy, rw, rh in ((sx - 5, top - 12, 9, 8), (sx + 5, top - 14, 9, 8),
                           (sx, top - 17, 8, 7)):
        pygame.draw.ellipse(surf, f['dark'], (cx - rw, cy - rh, rw * 2, rh * 2))
        pygame.draw.ellipse(surf, f['mid'],
                            (cx - rw + 1, cy - rh + 1, rw * 2 - 3, rh * 2 - 2))
    # 4 distinct blossom CLUSTERS — each a tight rosette (dark core + lit cap),
    # placed at recognizable points, not random confetti.
    clusters = (((sx - 6, top - 15), (228, 96, 132)),
                ((sx + 6, top - 17), (236, 120, 158)),
                ((sx, top - 21, ), (222, 78, 104)),
                ((sx + 2, top - 12), (240, 150, 178)))
    for spot, base in clusters:
        bx, byp = spot[0], spot[1]
        core = _bloom(base, pal)
        cap = _bloom(base, pal, day_lift=34)            # +1 value brighter (day)
        # A 5-petal rosette: dark ring of petals, lighter centre cap.
        for k in range(5):
            a = k * (math.tau / 5) - 0.3
            px = bx + int(math.cos(a) * 2)
            py = byp + int(math.sin(a) * 1.6)
            pygame.draw.circle(surf, _shade(core, -34), (px, py), 1)
        pygame.draw.circle(surf, core, (bx, byp), 1)
        pygame.draw.circle(surf, cap, (bx, byp), 0)
        # A tiny golden stamen centre, also night-capped via _bloom.
        pygame.draw.circle(surf, _bloom((255, 226, 150), pal), (bx, byp), 0)


def draw_vine(surf, sx, by, pal, pot_fn):
    """Cascading vine — a CLEAR draped silhouette over the FRONT-LEFT lip:
    one thicker primary strand + one secondary, 3-4 readable leaf nodes, the
    strand breaking the rim so the shape reads asymmetric in one glance."""
    f = _fol(pal)
    n = _nightf(pal)
    pot_fn(surf, sx, by, 16, 12, n)
    top = by - 12
    lip_x = sx - 8                                       # front-LEFT lip
    leaf_dk = f['dark']
    leaf_md = f['mid']
    leaf_lt = f['top']

    def strand(x0, y0, length, sway, width, nodes):
        # A draped curve falling and curling outward, leaf node pairs along it.
        pts = [(x0, y0)]
        node_pts = []
        for i in range(1, length + 1):
            t = i / length
            px = x0 - int(math.sin(t * 2.0) * sway) - int(t * 3)
            py = y0 + int(t * (length + 6))
            pts.append((px, py))
        pygame.draw.lines(surf, _shade(leaf_dk, -14), False, pts, width + 1)
        pygame.draw.lines(surf, leaf_dk, False, pts, width)
        # Place a few BIG readable leaves at evenly spaced nodes.
        for ni in range(nodes):
            idx = 1 + (ni + 1) * (len(pts) - 2) // (nodes + 1)
            px, py = pts[idx]
            side = -1 if ni % 2 == 0 else 1
            # A filled teardrop leaf (3px) with a lit upper face.
            lx = px + side * 3
            pygame.draw.polygon(surf, leaf_md,
                                [(px, py - 1), (lx, py - 2),
                                 (lx + side, py + 1), (px, py + 2)])
            pygame.draw.line(surf, leaf_lt, (px, py - 1), (lx, py - 1), 1)
            node_pts.append((px, py))
        return pts, node_pts

    # Primary thicker strand — longest, draped furthest over the lip.
    primary, _ = strand(lip_x, top, 13, 4, 2, 3)
    # Secondary thinner strand starting just behind, shorter, slight offset.
    strand(lip_x + 3, top + 1, 9, 3, 1, 2)
    # A curling tendril tip at the very end of the primary strand.
    ex, ey = primary[-1]
    pygame.draw.lines(surf, leaf_dk, False,
                      [(ex, ey), (ex + 2, ey + 2), (ex, ey + 3)], 1)
    # One small bloom tucked at the top node where the vine breaks the rim.
    c = _bloom((240, 196, 124), pal)
    pygame.draw.circle(surf, c, (lip_x - 1, top + 3), 1)


# ══════════════════════════════════════════════════════════════════════════
# CANDIDATES — each is (pot_fn, bonsai_fn); bamboo/flower/vine are shared.
# ══════════════════════════════════════════════════════════════════════════

CANDIDATES = [
    ("A  Celadon foliage + PORCELAIN pot (refined cobalt rim band)",
     _pot_porcelain, draw_bonsai_tiered),
    ("B  Celadon foliage + TERRACOTTA pot (warm value contrast)",
     _pot_terracotta, draw_bonsai_tiered),
    ("C  Celadon base + INK-WASH S-trunk bonsai (celadon pot)",
     _pot_celadon, draw_bonsai_inkwash),
    ("D  PORCELAIN pot + INK-WASH trunk (scholar-literati mix)",
     _pot_porcelain, draw_bonsai_inkwash),
    ("E  CELADON glaze + INK-WASH trunk (the base, gnarled)",
     _pot_celadon, draw_bonsai_inkwash),
]


def draw_set(surf, sx_list, by, pal, pot_fn, bonsai_fn):
    draw_bamboo(surf, sx_list[0], by, pal, pot_fn)
    bonsai_fn(surf, sx_list[1], by, pal, pot_fn)
    draw_flower(surf, sx_list[2], by, pal, pot_fn)
    draw_vine(surf, sx_list[3], by, pal, pot_fn)


# ══════════════════════════════════════════════════════════════════════════
# Reference actors for the night glow-check — coin + parrot silhouette.
# ══════════════════════════════════════════════════════════════════════════

def draw_coin(surf, cx, cy):
    """The gameplay coin (COIN palette from draw.py) — the brightness yardstick.
    Drawn at full saturation; it must out-glow every plant at night."""
    pygame.draw.circle(surf, (200, 140, 0), (cx, cy), 7)
    pygame.draw.circle(surf, (255, 210, 20), (cx, cy), 6)
    pygame.draw.circle(surf, (255, 245, 120), (cx - 2, cy - 2), 2)
    # A faint glow halo.
    halo = pygame.Surface((28, 28), pygame.SRCALPHA)
    pygame.draw.circle(halo, (255, 220, 80, 60), (14, 14), 13)
    surf.blit(halo, (cx - 14, cy - 14))


def draw_parrot(surf, cx, cy):
    """A compact scarlet-macaw silhouette using the BIRD_* palette — the second
    bright actor the plants must not rival."""
    body = (240, 55, 55)
    belly = (255, 170, 50)
    wing = (40, 100, 255)
    beak = (255, 185, 0)
    pygame.draw.ellipse(surf, body, (cx - 8, cy - 7, 16, 14))
    pygame.draw.ellipse(surf, belly, (cx - 3, cy - 1, 9, 8))
    pygame.draw.polygon(surf, wing, [(cx - 2, cy - 3), (cx + 7, cy - 8),
                                     (cx + 9, cy - 1), (cx + 1, cy + 3)])
    pygame.draw.polygon(surf, (50, 220, 100), [(cx + 7, cy - 8),
                                               (cx + 11, cy - 5),
                                               (cx + 9, cy - 1)])
    pygame.draw.circle(surf, (255, 255, 255), (cx - 5, cy - 3), 2)   # eye patch
    pygame.draw.circle(surf, (20, 20, 30), (cx - 5, cy - 3), 1)
    pygame.draw.polygon(surf, beak, [(cx - 8, cy - 2), (cx - 12, cy),
                                     (cx - 8, cy + 2)])


# ══════════════════════════════════════════════════════════════════════════
# Sheet layout
# ══════════════════════════════════════════════════════════════════════════

def _deck_strip(surf, x, y, w, h, pal):
    night = _nightf(pal)
    base = _night_cap(_mix((182, 168, 146), (66, 74, 104), 0.42 * night), night)
    pygame.draw.rect(surf, base, (x, y, w, h))
    pygame.draw.rect(surf, _shade(base, 14), (x, y, w, 2))
    pygame.draw.rect(surf, _shade(base, -22), (x, y + h - 3, w, 3))
    for jx in range(x + 24, x + w, 48):
        pygame.draw.line(surf, _shade(base, -16), (jx, y + 2), (jx, y + h - 2), 1)


def _bg(pal):
    return _mix(pal['sky_top'], (255, 255, 255), 0.15)


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 13, bold=True)
    small = pygame.font.SysFont("dejavusans", 10)
    tiny = pygame.font.SysFont("dejavusans", 9)

    zoom = 3                              # upscale factor for the zoomed view
    base_slot = 56                        # native px per plant slot
    plant_slots = 4
    deck_h = 16
    names = ("bamboo", "bonsai", "flower", "vine")

    # Zoomed cell (per phase) is the native set upscaled.
    nat_w = base_slot * plant_slots
    nat_h = 64
    cell_w = nat_w * zoom // 2            # keep sheet width manageable
    # Render native then scale, so we keep crisp nearest-neighbour zoom.

    ref_w = nat_w                         # true 1x reference strip width
    gap = 8
    margin = 14
    label_h = 22

    rows = len(CANDIDATES)
    # Width: DAY zoom | NIGHT zoom | 1x-DAY ref | 1x-NIGHT ref
    zoom_w = nat_w * 2                    # 2x upscale, readable
    body_w = margin * 2 + zoom_w * 2 + gap * 3 + ref_w
    sheet_w = max(body_w, 760)
    cell_h = nat_h * 2
    row_h = cell_h + label_h + gap + 8
    sheet_h = margin * 2 + label_h + 14 + rows * row_h + 30

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((28, 28, 34))

    title = font.render(
        "PLANT FAMILY UPGRADE — CONVERGENCE on Celadon base   "
        "(DAY zoom | NIGHT zoom | 1x ref)   round 2", True, (236, 236, 240))
    sheet.blit(title, (margin, 10))
    sub = small.render(
        "All candidates share Celadon foliage discipline + standardized night "
        "ramp (value+chroma drop). Coin & parrot in night frame = glow yardstick.",
        True, (170, 172, 182))
    sheet.blit(sub, (margin, 28))

    def render_native(pal, with_actors):
        """Draw one full set at native resolution onto a small surface."""
        surf = pygame.Surface((nat_w, nat_h))
        surf.fill(_bg(pal))
        deck_y = nat_h - deck_h
        _deck_strip(surf, 0, deck_y, nat_w, deck_h, pal)
        by = deck_y + 2
        sx_list = [si * base_slot + base_slot // 2 for si in range(plant_slots)]
        return surf, sx_list, by, deck_y

    y = margin + label_h + 22
    for ci, (name, pot_fn, bonsai_fn) in enumerate(CANDIDATES):
        lbl = font.render(name, True, (226, 222, 210))
        sheet.blit(lbl, (margin, y - 18))

        x = margin
        # Two zoomed phases.
        for pi, pal in enumerate((PAL_DAY, PAL_NIGHT)):
            surf, sx_list, by, deck_y = render_native(pal, pi == 1)
            draw_set(surf, sx_list, by, pal, pot_fn, bonsai_fn)
            if pi == 1:
                # Drop the coin + parrot into the night frame as a yardstick.
                draw_coin(surf, nat_w - 16, deck_y - 18)
                draw_parrot(surf, nat_w - 40, deck_y - 22)
            big = pygame.transform.scale(surf, (zoom_w, cell_h))
            sheet.blit(big, (x, y))
            pygame.draw.rect(sheet, (70, 70, 80), (x, y, zoom_w, cell_h), 1)
            # Slot tags + phase label.
            ph = small.render("DAY" if pi == 0 else "NIGHT", True,
                              (210, 210, 215))
            sheet.blit(ph, (x + 4, y + 2))
            for si in range(plant_slots):
                tx = x + (sx_list[si]) * 2
                tag = tiny.render(names[si], True, (200, 200, 210))
                sheet.blit(tag, (tx - tag.get_width() // 2, y + cell_h + 2))
            x += zoom_w + gap

        # True 1x reference strip (un-upscaled): both phases stacked.
        ref = pygame.Surface((ref_w, nat_h * 2 + 4))
        ref.fill((20, 20, 26))
        for pi, pal in enumerate((PAL_DAY, PAL_NIGHT)):
            surf, sx_list, by, deck_y = render_native(pal, pi == 1)
            draw_set(surf, sx_list, by, pal, pot_fn, bonsai_fn)
            if pi == 1:
                draw_coin(surf, nat_w - 16, deck_y - 18)
                draw_parrot(surf, nat_w - 40, deck_y - 22)
            ref.blit(surf, (0, pi * (nat_h + 4)))
        sheet.blit(ref, (x, y))
        pygame.draw.rect(sheet, (70, 70, 80), (x, y, ref_w, nat_h * 2 + 4), 1)
        rlbl = tiny.render("TRUE 1x  (ships at this size)", True, (180, 182, 196))
        sheet.blit(rlbl, (x, y + nat_h * 2 + 6))

        y += row_h

    foot = small.render(
        "A=porcelain  B=terracotta  C=ink-trunk+celadon  D=porcelain+ink-trunk  "
        "E=celadon+ink-trunk.  Vine drapes front-left lip; flowers = 2-value "
        "clusters; bamboo segmented (no crown); bonsai pads have valley gaps.",
        True, (150, 150, 158))
    sheet.blit(foot, (margin, sheet_h - 22))

    out = "/home/user/skybit/docs/foreground_redesign/plants/round_2.png"
    pygame.image.save(sheet, out)
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
