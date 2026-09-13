"""5-design picker for the Skybit 3,000-games-played celebration image.

Round 2: top-notch redesign. Same five conceptual directions as round 1
(bucket cake / gold trophy / coin shower / pip podium / newspaper) but
with proper game-poster polish - hero focal points, layered depth,
ribbon banners, motion streaks, gold-dust particles, multi-tone
gradients, embossed text.

Each variant is 360x640 portrait (game canvas). Run from repo root:

    PYTHONPATH=. python tools/render_3k_celebration.py

Output:
    docs/celebrations/3k_games/v1.png    Bucket Party
    docs/celebrations/3k_games/v2.png    Trophy Spotlight
    docs/celebrations/3k_games/v3.png    Coin Storm
    docs/celebrations/3k_games/v4.png    Pip Podium
    docs/celebrations/3k_games/v5.png    Extra Extra
    docs/celebrations/3k_games/compare.png   5-column strip with labels
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H
from game import parrot
from game import biome as _biome
from game.draw import (
    COIN_GOLD, UI_RED,
    get_sky_surface_biome,
)
from game.pillar_kfc import KFC_RED, KFC_RED_D, KFC_WHITE


# --- Palette ---------------------------------------------------------------

OUTLINE       = (24, 12, 6)
DEEP_BLACK    = (10,  6,  3)

# 5-stop gold ramp for trophy + coin + bucket label
GOLD_5 = (
    (255, 240, 160),   # highlight
    (252, 206,  72),   # mid-light
    (220, 160,  30),   # mid
    (158,  98,  12),   # shadow
    ( 70,  38,   4),   # deep
)

GOLD_HI       = GOLD_5[0]
GOLD_MID      = GOLD_5[1]
GOLD_LO       = GOLD_5[2]
GOLD_DK       = GOLD_5[3]

PAPER_BG      = (244, 232, 200)
PAPER_INK     = (28, 18, 12)
PAPER_RULE    = (120, 96, 56)

INDIGO        = ( 28,  18,  82)
MAGENTA       = (102,  36, 108)

CONFETTI_COLS = ((242, 90, 90), (90, 200, 80), (90, 160, 250),
                 (252, 206, 56), (236, 110, 220), (250, 130, 60))


# --- Fonts -----------------------------------------------------------------

def _font(size, bold=True):
    fname = "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"
    return pygame.font.Font(os.path.join("game", "assets", fname), size)


# --- Outlined text (used by every headline) --------------------------------

def draw_big_text(surf, text, center, size, *, fill=COIN_GOLD,
                  outline=OUTLINE, outline_w=4, shadow=True,
                  sparkles=0):
    """Bold text with thick outline + drop shadow."""
    font = _font(size, bold=True)
    text_surf = font.render(text, True, fill)
    tw, th = text_surf.get_size()
    cx, cy = center

    layer = pygame.Surface((tw + outline_w * 4, th + outline_w * 4),
                           pygame.SRCALPHA)
    outline_surf = font.render(text, True, outline)
    for dx in range(-outline_w, outline_w + 1):
        for dy in range(-outline_w, outline_w + 1):
            if dx * dx + dy * dy <= outline_w * outline_w:
                layer.blit(outline_surf,
                           (outline_w * 2 + dx, outline_w * 2 + dy))
    layer.blit(text_surf, (outline_w * 2, outline_w * 2))

    if shadow:
        dark = font.render(text, True, DEEP_BLACK)
        dark.set_alpha(140)
        surf.blit(dark,
                  (cx - layer.get_width() // 2 + outline_w * 2 + 2,
                   cy - layer.get_height() // 2 + outline_w * 2 + 3))

    rect = layer.get_rect(center=(cx, cy))
    surf.blit(layer, rect.topleft)

    if sparkles:
        rng = random.Random(hash(text) & 0xffff)
        for _ in range(sparkles):
            sx = rng.randint(rect.left - 6, rect.right + 6)
            sy = rng.randint(rect.top - 6, rect.bottom + 6)
            r = rng.randint(2, 4)
            pygame.draw.circle(surf, OUTLINE, (sx, sy), r + 1)
            pygame.draw.circle(surf, GOLD_HI, (sx, sy), r)
            pygame.draw.circle(surf, (255, 255, 255), (sx - 1, sy - 1),
                               max(1, r - 2))
    return rect


def draw_tagline(surf, text, y, size=20, color=(255, 255, 255)):
    font = _font(size, bold=True)
    out = font.render(text, True, OUTLINE)
    fill = font.render(text, True, color)
    cx = W // 2
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                surf.blit(out, (cx - out.get_width() // 2 + dx, y + dy))
    surf.blit(fill, (cx - fill.get_width() // 2, y))


# --- Shared visual helpers -------------------------------------------------

def draw_gold_gradient_rect(surf, rect, *, stops=GOLD_5, border_radius=0):
    """Multi-stop vertical gold gradient inside `rect`."""
    grad = pygame.Surface(rect.size, pygame.SRCALPHA)
    n = len(stops) - 1
    h = rect.height
    for y in range(h):
        u = (y / max(1, h - 1)) * n
        i0 = int(u)
        i1 = min(i0 + 1, n)
        t = u - i0
        c = tuple(int(stops[i0][k] + (stops[i1][k] - stops[i0][k]) * t)
                  for k in range(3))
        pygame.draw.line(grad, c, (0, y), (rect.width - 1, y))
    if border_radius > 0:
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                          mask.get_rect(), border_radius=border_radius)
        grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, rect.topleft)


def draw_indigo_magenta_bg(surf):
    """Premium deep-indigo to magenta vertical gradient."""
    for y in range(H):
        u = y / (H - 1)
        c = tuple(int(INDIGO[k] + (MAGENTA[k] - INDIGO[k]) * u)
                  for k in range(3))
        pygame.draw.line(surf, c, (0, y), (W - 1, y))


def draw_dawn_bg(surf):
    """Deep-blue top -> warm-orange bottom (sunrise streak)."""
    stops = ((18, 24, 70), (52, 36, 110), (180, 64, 80),
             (240, 140, 60), (250, 192, 96))
    n = len(stops) - 1
    for y in range(H):
        u = (y / (H - 1)) * n
        i0 = int(u)
        i1 = min(i0 + 1, n)
        t = u - i0
        c = tuple(int(stops[i0][k] + (stops[i1][k] - stops[i0][k]) * t)
                  for k in range(3))
        pygame.draw.line(surf, c, (0, y), (W - 1, y))


def draw_spotlight_beam(surf, top_anchor, *, length, half_width_top,
                        half_width_bot, color=(255, 240, 200), alpha=70):
    """Soft volumetric spotlight cone fading downward through stacked
    triangular layers of decreasing alpha."""
    cx, cy = top_anchor
    n_layers = 5
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(n_layers):
        u = (i + 1) / n_layers   # 0.2, 0.4, ..., 1.0
        a = int(alpha * (1.0 - u * 0.6))
        wt = half_width_top * (0.5 + 0.5 * u)
        wb = half_width_bot * (0.5 + 0.5 * u)
        pts = [
            (cx - wt, cy),
            (cx + wt, cy),
            (cx + wb, cy + length),
            (cx - wb, cy + length),
        ]
        pygame.draw.polygon(layer, (*color, a), pts)
    surf.blit(layer, (0, 0))


def draw_confetti_layered(surf, n_back=80, n_front=30, seed=11):
    """Two-layer confetti for depth: small/dim background + larger/sharper
    foreground with motion-blur tails."""
    rng = random.Random(seed)
    # Background layer - small dots, dim
    for _ in range(n_back):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        col = rng.choice(CONFETTI_COLS)
        r = rng.choice((1, 1, 2))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col, 160), (r + 1, r + 1), r)
        surf.blit(s, (x, y))
    # Foreground layer - rectangular pieces, motion-blurred
    for _ in range(n_front):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        col = rng.choice(CONFETTI_COLS)
        w = rng.choice((4, 5, 6))
        h = rng.choice((8, 10, 12))
        ang = rng.uniform(-45, 45)
        piece = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
        # 3 alpha-stacked offsets for motion trail
        for tr_i, tr_a in enumerate(((0, 60), (-2, 90), (-4, 140))):
            pygame.draw.rect(
                piece, (*col, tr_a[1]),
                pygame.Rect(2, 2 - tr_a[0], w, h),
                border_radius=2)
        # Final crisp body
        pygame.draw.rect(piece, OUTLINE,
                         pygame.Rect(2, 2, w, h), border_radius=2, width=1)
        pygame.draw.rect(piece, col,
                         pygame.Rect(3, 3, w - 2, h - 2), border_radius=2)
        rot = pygame.transform.rotate(piece, ang)
        surf.blit(rot, (x - rot.get_width() // 2,
                          y - rot.get_height() // 2))


def draw_streamer(surf, p0, p1, p2, color, *, width=4, segments=24):
    """Quadratic-bezier streamer from p0 to p2 with control p1."""
    pts = []
    for i in range(segments + 1):
        t = i / segments
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((int(x), int(y)))
    pygame.draw.lines(surf, OUTLINE, False, pts, width + 2)
    pygame.draw.lines(surf, color, False, pts, width)
    # Subtle highlight strand on one side
    pygame.draw.lines(surf, (255, 255, 255, 180), False,
                      [(x, y - 1) for (x, y) in pts], max(1, width // 3))


def draw_dust_particles(surf, n, color, seed, *, area=None, rise=0):
    """Tiny soft dust circles drifting upward."""
    rng = random.Random(seed)
    if area is None:
        area = pygame.Rect(0, 0, W, H)
    for _ in range(n):
        x = rng.randint(area.x, area.x + area.width - 1)
        y = rng.randint(area.y, area.y + area.height - 1) - rise
        r = rng.randint(1, 3)
        a = rng.randint(120, 220)
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, a), (r + 1, r + 1), r)
        surf.blit(s, (x, y))


def draw_speed_lines(surf, anchor, n=12, *, direction=(-1, 0),
                     length_range=(40, 90), color=(255, 255, 255), seed=3):
    """Streaks behind a focal point - white fading to transparent."""
    rng = random.Random(seed)
    ax, ay = anchor
    for _ in range(n):
        dy = rng.randint(-60, 60)
        sx = ax + dy * 0.0
        sy = ay + dy
        L = rng.randint(*length_range)
        ex = sx + direction[0] * L
        ey = sy + direction[1] * L
        # Tapering streak: thicker near anchor, thinner / fainter far
        n_seg = 6
        for k in range(n_seg):
            t0 = k / n_seg
            t1 = (k + 1) / n_seg
            a = int(220 * (1 - t0))
            w = max(1, 4 - k)
            x0 = sx + (ex - sx) * t0
            y0 = sy + (ey - sy) * t0
            x1 = sx + (ex - sx) * t1
            y1 = sy + (ey - sy) * t1
            seg_surf = pygame.Surface(
                (int(abs(x1 - x0)) + 4, int(abs(y1 - y0)) + 4),
                pygame.SRCALPHA)
            pygame.draw.line(seg_surf, (*color, a),
                             (2, 2), (int(abs(x1 - x0)) + 1,
                                      int(abs(y1 - y0)) + 1), w)
            surf.blit(seg_surf, (min(x0, x1) - 2, min(y0, y1) - 2))


def draw_ribbon_banner(surf, center, *, w, h, text, color=KFC_RED,
                       text_color=(255, 255, 255), font_size=22,
                       tilt_deg=0):
    """Tilted parallelogram banner with two triangular tails + chunky outline."""
    bw, bh = w, h
    tail = bh
    layer = pygame.Surface((bw + tail * 2 + 6, bh + 12), pygame.SRCALPHA)
    body = pygame.Rect(tail + 3, 6, bw, bh)
    # Body
    pygame.draw.rect(layer, OUTLINE, body.inflate(6, 6), border_radius=4)
    # Inner shadow band - darker base color
    pygame.draw.rect(layer, _shade(color, -40), body.inflate(4, 4),
                     border_radius=4)
    pygame.draw.rect(layer, color, body, border_radius=4)
    # Highlight stripe
    pygame.draw.rect(layer, _shade(color, +40),
                     pygame.Rect(body.x + 2, body.y + 2, bw - 4,
                                 max(2, bh // 4)),
                     border_radius=3)
    # Left tail (notched triangle)
    left_tail = [
        (body.x, body.y),
        (body.x - tail, body.y + bh // 2),
        (body.x, body.bottom),
        (body.x + bh // 2, body.centery),
    ]
    pygame.draw.polygon(layer, OUTLINE,
                        [(p[0] - 2, p[1]) for p in left_tail])
    pygame.draw.polygon(layer, _shade(color, -40),
                        [(p[0] - 1, p[1]) for p in left_tail])
    pygame.draw.polygon(layer, color, left_tail)
    # Right tail
    right_tail = [
        (body.right, body.y),
        (body.right + tail, body.y + bh // 2),
        (body.right, body.bottom),
        (body.right - bh // 2, body.centery),
    ]
    pygame.draw.polygon(layer, OUTLINE,
                        [(p[0] + 2, p[1]) for p in right_tail])
    pygame.draw.polygon(layer, _shade(color, -40),
                        [(p[0] + 1, p[1]) for p in right_tail])
    pygame.draw.polygon(layer, color, right_tail)
    # Text on body
    fnt = _font(font_size, bold=True)
    txt = fnt.render(text, True, text_color)
    txt_o = fnt.render(text, True, OUTLINE)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                layer.blit(txt_o, (body.centerx - txt.get_width() // 2 + dx,
                                    body.centery - txt.get_height() // 2 + dy))
    layer.blit(txt, (body.centerx - txt.get_width() // 2,
                       body.centery - txt.get_height() // 2))
    if tilt_deg:
        layer = pygame.transform.rotate(layer, tilt_deg)
    rect = layer.get_rect(center=center)
    surf.blit(layer, rect.topleft)


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


# --- Coin renderer (V3 hero) ----------------------------------------------

def draw_coin(surf, cx, cy, r, *, edge_on=False, tilt=1.0, label=None,
              seed=0):
    """Proper coin with rim, gradient body, embossed label, specular shine.

    `tilt` (0..1) vertically squashes the coin so a value of 1.0 is a
    full face-on circle and 0.4 is a heavily-tilted perspective ellipse.
    `edge_on=True` overrides tilt and draws the coin as a thin vertical
    stripe (seen exactly edge-on).
    """
    if edge_on:
        ew = max(2, r // 3)
        rect = pygame.Rect(cx - ew, cy - r, ew * 2, r * 2)
        pygame.draw.ellipse(surf, OUTLINE, rect.inflate(2, 2))
        pygame.draw.ellipse(surf, GOLD_DK, rect.inflate(0, 0))
        # Vertical highlight stripe (specular along the edge)
        stripe = pygame.Rect(cx - 1, cy - r + 2, max(1, ew // 2),
                              max(2, r * 2 - 4))
        pygame.draw.rect(surf, GOLD_HI, stripe)
        return
    # Face-on coin - rendered onto a dedicated coin_surf so we can apply
    # vertical squash at the end for perspective tilt without re-running
    # the gradient math.
    pad = 6
    csize = r * 2 + pad * 2
    coin_surf = pygame.Surface((csize, csize), pygame.SRCALPHA)
    lcx, lcy = csize // 2, csize // 2
    # Outer rim shadow
    pygame.draw.circle(coin_surf, OUTLINE, (lcx + 1, lcy + 2), r + 1)
    # Rim
    pygame.draw.circle(coin_surf, GOLD_DK, (lcx, lcy), r + 1)
    pygame.draw.circle(coin_surf, GOLD_LO, (lcx, lcy), r)
    # Inner body with vertical gradient
    inner_r = max(1, r - 2)
    body = pygame.Surface((inner_r * 2 + 2, inner_r * 2 + 2), pygame.SRCALPHA)
    for y in range(inner_r * 2):
        u = y / max(1, inner_r * 2 - 1)
        if u < 0.5:
            t = (0.5 - u) / 0.5
            c = tuple(int(GOLD_MID[k] + (GOLD_HI[k] - GOLD_MID[k]) * t)
                      for k in range(3))
        else:
            t = (u - 0.5) / 0.5
            c = tuple(int(GOLD_MID[k] + (GOLD_LO[k] - GOLD_MID[k]) * t)
                      for k in range(3))
        dx = math.sqrt(max(0, inner_r * inner_r - (y - inner_r) ** 2))
        pygame.draw.line(body, c,
                          (inner_r - dx + 1, y + 1),
                          (inner_r + dx + 1, y + 1))
    coin_surf.blit(body, (lcx - inner_r, lcy - inner_r))
    # Specular crescent (upper-left)
    if r >= 8:
        spec = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(spec, (255, 255, 255, 200),
                            (r + 1, r + 1), r - 1)
        spec_clip = pygame.Surface((r * 2 + 2, r * 2 + 2),
                                    pygame.SRCALPHA)
        pygame.draw.circle(spec_clip, (255, 255, 255, 255),
                            (r + 1, r + 1), r - 1)
        spec.blit(spec_clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        crop = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        crop.blit(spec, (0, 0))
        # Mask out lower-right quadrant so only the upper-left crescent shows
        pygame.draw.rect(crop, (0, 0, 0, 0),
                          pygame.Rect(r + 1, r + 1, r + 1, r + 1))
        coin_surf.blit(crop, (lcx - r - 1, lcy - r - 1))
    # Embossed label "$" / "3K"
    eff_label = label if label is not None else "$"
    if r >= 11 and eff_label == "$":
        # Use a chunky bold $ that renders cleanly at small sizes
        fsize = max(12, int(r * 1.3))
        fnt = _font(fsize, bold=True)
        dark = fnt.render(eff_label, True, GOLD_DK)
        light = fnt.render(eff_label, True, GOLD_HI)
        coin_surf.blit(dark, (lcx - dark.get_width() // 2 + 1,
                              lcy - dark.get_height() // 2 + 1))
        coin_surf.blit(light, (lcx - light.get_width() // 2 - 1,
                                lcy - light.get_height() // 2 - 1))
    elif r >= 12 and eff_label == "3K":
        fsize = max(11, int(r * 1.0))
        fnt = _font(fsize, bold=True)
        dark = fnt.render(eff_label, True, GOLD_DK)
        light = fnt.render(eff_label, True, (255, 252, 220))
        coin_surf.blit(dark, (lcx - dark.get_width() // 2 + 1,
                              lcy - dark.get_height() // 2 + 1))
        coin_surf.blit(light, (lcx - light.get_width() // 2 - 1,
                                lcy - light.get_height() // 2 - 1))
    # Apply perspective squash if needed
    if tilt < 0.95:
        new_h = max(2, int(csize * tilt))
        coin_surf = pygame.transform.smoothscale(coin_surf, (csize, new_h))
    surf.blit(coin_surf, (cx - coin_surf.get_width() // 2,
                            cy - coin_surf.get_height() // 2))


# --- Backgrounds -----------------------------------------------------------

def night_sky(phase=0.05):
    buckets = _biome.PHASE_BUCKETS
    pal = _biome.palette_for_phase(phase)
    sky = get_sky_surface_biome(W, H, H, pal, int(phase * buckets))
    return sky, pal


def starfield(surf, n=60, seed=7):
    rng = random.Random(seed)
    for _ in range(n):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, int(H * 0.6))
        r = rng.choice((1, 1, 1, 2))
        a = rng.randint(120, 255)
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, a), (r + 1, r + 1), r)
        surf.blit(s, (x, y))


# ===========================================================================
# V1 - "BUCKET PARTY"
# ===========================================================================

def draw_v1(surf):
    # Warm dusk biome backdrop
    sky, pal = night_sky(0.62)
    surf.blit(sky, (0, 0))

    # ---- Big warm radial glow behind the bucket (stage-spotlight feel) ----
    glow_cx, glow_cy = W // 2, H // 2 + 60
    for i, (r, a) in enumerate(((260, 24), (200, 36), (140, 50), (90, 70))):
        glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 200, 110, a), (r, r), r)
        surf.blit(glow, (glow_cx - r, glow_cy - r))

    starfield(surf, n=20, seed=1)

    # Streamers - thicker, two layers of curls
    draw_streamer(surf, (-10, 30), (W // 2, -10), (W + 10, 70),
                  (242, 90, 90), width=6)
    draw_streamer(surf, (24, 90), (W // 2, 210), (W - 24, 60),
                  (252, 206, 56), width=5)
    draw_streamer(surf, (-10, 140), (W // 3, 50), (W - 30, 150),
                  (90, 200, 80), width=5)
    draw_streamer(surf, (40, 190), (W * 2 // 3, 70), (W + 10, 170),
                  (90, 160, 250), width=5)
    draw_streamer(surf, (200, 30), (60, 110), (300, 200),
                  (236, 110, 220), width=4)

    # ---- Big bucket (hero) ----
    bucket_top_w = 280
    bucket_bot_w = 200
    bucket_top_y = 250
    bucket_bot_y = H - 50
    bh = bucket_bot_y - bucket_top_y

    # Drop shadow ellipse underneath
    sh = pygame.Surface((bucket_bot_w + 70, 32), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 110), sh.get_rect())
    surf.blit(sh, (W // 2 - sh.get_width() // 2, H - 58))

    tl = (W // 2 - bucket_top_w // 2, bucket_top_y)
    tr = (W // 2 + bucket_top_w // 2, bucket_top_y)
    br = (W // 2 + bucket_bot_w // 2, bucket_bot_y)
    bl = (W // 2 - bucket_bot_w // 2, bucket_bot_y)
    poly = [tl, tr, br, bl]
    # Body outline
    pygame.draw.polygon(surf, OUTLINE,
                        [(px, py + 2) for (px, py) in poly])
    pygame.draw.polygon(surf, KFC_WHITE, poly)
    # Stripes - 7 evenly spaced, each shaded based on horizontal position
    # (left = bright, centre = mid, right = dark) for 3D-cylinder feel
    n_stripes = 7
    for i in range(n_stripes):
        u0 = (i + 0.12) / n_stripes
        u1 = (i + 0.58) / n_stripes
        # Horizontal position of stripe centre (0..1)
        u_mid = (u0 + u1) / 2
        # Shading: brighter on the lit side (left), darker on the right
        if u_mid < 0.25:
            sd = +25
        elif u_mid < 0.5:
            sd = +8
        elif u_mid < 0.75:
            sd = -12
        else:
            sd = -32
        c = _shade(KFC_RED, sd)
        sx0_top = tl[0] + (tr[0] - tl[0]) * u0
        sx1_top = tl[0] + (tr[0] - tl[0]) * u1
        sx0_bot = bl[0] + (br[0] - bl[0]) * u0
        sx1_bot = bl[0] + (br[0] - bl[0]) * u1
        pygame.draw.polygon(
            surf, c,
            [(sx0_top, tl[1]), (sx1_top, tl[1]),
             (sx1_bot, br[1]), (sx0_bot, br[1])])
    # Shade the WHITE areas similarly - lay an alpha gradient sweep over
    # the whole bucket trapezoid so the unshaded stripes pick up the
    # cylinder shading too
    body_overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    for x in range(int(tl[0]), int(tr[0])):
        u = (x - tl[0]) / max(1, bucket_top_w)
        if u < 0.5:
            a = int(40 * (0.5 - u) / 0.5 * (1 - 1))   # no overlay left
            a = 0
        else:
            a = int(70 * (u - 0.5) / 0.5)
        if a > 0:
            pygame.draw.line(body_overlay, (40, 16, 12, a),
                              (x, int(tl[1])), (x, int(bl[1])))
    surf.blit(body_overlay, (0, 0))
    pygame.draw.polygon(surf, OUTLINE, poly, 3)
    # Top rim band
    rim = pygame.Rect(tl[0] - 4, tl[1] - 8, bucket_top_w + 8, 16)
    pygame.draw.rect(surf, OUTLINE, rim.inflate(2, 2), border_radius=6)
    pygame.draw.rect(surf, KFC_RED_D, rim, border_radius=6)
    pygame.draw.rect(surf, KFC_RED, rim.inflate(-6, -4), border_radius=4)
    # Rim inner shadow line (suggests the bucket has an inside)
    pygame.draw.line(surf, _shade(KFC_RED_D, -30),
                     (tl[0] + 4, tl[1] + 1),
                     (tr[0] - 4, tl[1] + 1), 2)

    # Gold-foil "3,000 GAMES" label band - elevated above bucket centre
    label_w = 210
    label_h = 56
    label = pygame.Rect(W // 2 - label_w // 2,
                        bucket_top_y + bh // 2 - label_h // 2,
                        label_w, label_h)
    # Drop shadow for label
    pygame.draw.rect(surf, (0, 0, 0, 90),
                     label.inflate(8, 8).move(3, 4), border_radius=8)
    # Outer red border
    pygame.draw.rect(surf, OUTLINE, label.inflate(6, 6), border_radius=8)
    pygame.draw.rect(surf, KFC_RED_D, label.inflate(4, 4), border_radius=7)
    pygame.draw.rect(surf, KFC_RED, label.inflate(2, 2), border_radius=6)
    # Gold inner panel
    draw_gold_gradient_rect(surf, label.inflate(-6, -6),
                            border_radius=5)
    pygame.draw.rect(surf, OUTLINE, label.inflate(-6, -6),
                     border_radius=5, width=2)
    # Diagonal sheen overlay on the gold (lighter band sweeping across)
    sheen = pygame.Surface(label.inflate(-6, -6).size, pygame.SRCALPHA)
    sw, sh_ = sheen.get_size()
    for y in range(sh_):
        for x in range(sw):
            # diagonal band
            d = (x + y) % 64
            if 24 < d < 36:
                sheen.set_at((x, y), (255, 248, 220, 50))
    surf.blit(sheen, label.inflate(-6, -6).topleft)
    # Embossed "3,000 GAMES"
    fnt_label = _font(22, bold=True)
    eng_dk = fnt_label.render("3,000 GAMES", True, GOLD_DK)
    eng_hi = fnt_label.render("3,000 GAMES", True, (255, 248, 220))
    surf.blit(eng_dk, (label.centerx - eng_dk.get_width() // 2 + 1,
                       label.centery - eng_dk.get_height() // 2 + 1))
    surf.blit(eng_hi, (label.centerx - eng_hi.get_width() // 2 - 1,
                       label.centery - eng_hi.get_height() // 2 - 1))
    # Tiny crown above the label
    crown_cx = W // 2
    crown_y = label.top - 14
    crown_pts = [
        (crown_cx - 16, crown_y + 10),
        (crown_cx - 16, crown_y + 2),
        (crown_cx - 8, crown_y + 8),
        (crown_cx, crown_y - 6),
        (crown_cx + 8, crown_y + 8),
        (crown_cx + 16, crown_y + 2),
        (crown_cx + 16, crown_y + 10),
    ]
    pygame.draw.polygon(surf, OUTLINE,
                        [(p[0], p[1] + 1) for p in crown_pts])
    pygame.draw.polygon(surf, GOLD_LO,
                        [(p[0], p[1]) for p in crown_pts])
    # crown highlight
    pygame.draw.polygon(surf, GOLD_HI,
                        [(crown_cx - 14, crown_y + 4),
                         (crown_cx, crown_y - 3),
                         (crown_cx + 14, crown_y + 4),
                         (crown_cx + 10, crown_y + 6),
                         (crown_cx, crown_y + 2),
                         (crown_cx - 10, crown_y + 6)])
    # crown jewels
    pygame.draw.circle(surf, OUTLINE, (crown_cx, crown_y - 2), 3)
    pygame.draw.circle(surf, KFC_RED, (crown_cx, crown_y - 2), 2)
    pygame.draw.circle(surf, (255, 255, 255), (crown_cx, crown_y - 3), 1)
    for jx in (crown_cx - 8, crown_cx + 8):
        pygame.draw.circle(surf, OUTLINE, (jx, crown_y + 8), 2)
        pygame.draw.circle(surf, (90, 160, 250), (jx, crown_y + 8), 1)

    # ---- Two candles flanking Pip ----
    def _draw_candle(cx_i):
        cand_h = 48
        cand = pygame.Rect(cx_i - 6, rim.top - cand_h - 2, 12, cand_h)
        # Candle drop shadow
        pygame.draw.rect(surf, (0, 0, 0, 80),
                         cand.move(2, 2).inflate(2, 2), border_radius=4)
        pygame.draw.rect(surf, OUTLINE, cand.inflate(2, 2), border_radius=4)
        pygame.draw.rect(surf, (220, 215, 200), cand, border_radius=4)
        # Highlight stripe
        pygame.draw.rect(surf, KFC_WHITE,
                         pygame.Rect(cand.x + 2, cand.y + 2, 4,
                                     cand.height - 4),
                         border_radius=2)
        # Wax drips
        pygame.draw.line(surf, OUTLINE,
                          (cand.centerx + 3, cand.bottom - 6),
                          (cand.centerx + 5, cand.bottom + 5), 3)
        pygame.draw.line(surf, (200, 195, 180),
                          (cand.centerx + 3, cand.bottom - 6),
                          (cand.centerx + 5, cand.bottom + 5), 2)
        # Wick
        pygame.draw.line(surf, OUTLINE, (cand.centerx, cand.top - 2),
                         (cand.centerx, cand.top - 8), 2)
        # Flame halo (soft glow)
        for r_g, a_g in ((24, 50), (16, 90), (10, 140)):
            halo = pygame.Surface((r_g * 2, r_g * 2), pygame.SRCALPHA)
            pygame.draw.circle(halo, (255, 200, 80, a_g),
                                (r_g, r_g), r_g)
            surf.blit(halo, (cand.centerx - r_g, cand.top - 20 - r_g))
        # Flame layers (taller)
        flame_outer = [(cand.centerx, cand.top - 34),
                        (cand.centerx - 9, cand.top - 10),
                        (cand.centerx - 4, cand.top - 4),
                        (cand.centerx + 4, cand.top - 4),
                        (cand.centerx + 9, cand.top - 10)]
        pygame.draw.polygon(surf, (180, 50, 20), flame_outer)
        flame_mid = [(cand.centerx, cand.top - 26),
                      (cand.centerx - 6, cand.top - 10),
                      (cand.centerx, cand.top - 6),
                      (cand.centerx + 6, cand.top - 10)]
        pygame.draw.polygon(surf, (250, 160, 30), flame_mid)
        flame_inner = [(cand.centerx, cand.top - 18),
                        (cand.centerx - 4, cand.top - 10),
                        (cand.centerx, cand.top - 6),
                        (cand.centerx + 4, cand.top - 10)]
        pygame.draw.polygon(surf, (255, 220, 100), flame_inner)
        pygame.draw.polygon(surf, (255, 255, 230),
                            [(cand.centerx, cand.top - 12),
                             (cand.centerx - 2, cand.top - 8),
                             (cand.centerx, cand.top - 6),
                             (cand.centerx + 2, cand.top - 8)])

    candle_xs = (tl[0] + bucket_top_w * 0.20,
                 tl[0] + bucket_top_w * 0.80)
    for cx_f in candle_xs:
        _draw_candle(int(cx_f))

    # ---- Pip on the rim, 1.5x scaled, wings up, hopping victorious ----
    pip = parrot.get_parrot(0, 22)
    pip_scaled = pygame.transform.smoothscale(
        pip, (int(pip.get_width() * 1.5),
              int(pip.get_height() * 1.5)))
    pip_x = W // 2 - pip_scaled.get_width() // 2
    pip_y = rim.top - pip_scaled.get_height() + 12
    surf.blit(pip_scaled, (pip_x, pip_y))
    # Sparkle burst around Pip
    rng = random.Random(7)
    for _ in range(10):
        sx = rng.randint(pip_x - 18, pip_x + pip_scaled.get_width() + 18)
        sy = rng.randint(pip_y - 12, pip_y + pip_scaled.get_height() + 12)
        r = rng.randint(2, 5)
        pygame.draw.circle(surf, OUTLINE, (sx, sy), r + 1)
        pygame.draw.circle(surf, GOLD_HI, (sx, sy), r)
        pygame.draw.circle(surf, (255, 255, 255), (sx - 1, sy - 1),
                           max(1, r - 2))

    # ---- Headline + tagline ----
    draw_big_text(surf, "3,000", (W // 2, 78), size=80,
                  fill=COIN_GOLD, outline_w=6, sparkles=12)
    draw_tagline(surf, "Next bucket's on you. Keep flying.",
                 H - 30, size=16, color=(255, 240, 200))

    # ---- Confetti rain (front layer ON TOP of everything) ----
    draw_confetti_layered(surf, n_back=80, n_front=32, seed=3)


# ===========================================================================
# V2 - "TROPHY SPOTLIGHT"
# ===========================================================================

def draw_v2(surf):
    draw_indigo_magenta_bg(surf)

    # Faint stars
    starfield(surf, n=35, seed=2)

    # Wider, more dramatic spotlight beam - bright top, gentle splash at base
    draw_spotlight_beam(surf,
                        top_anchor=(W // 2, 20),
                        length=H - 100,
                        half_width_top=70,
                        half_width_bot=210,
                        color=(255, 240, 200),
                        alpha=120)

    # Soft warm glow halo where the spotlight lands on the trophy
    halo_cx, halo_cy = W // 2, H // 2 + 30
    for r_g, a_g in ((220, 30), (160, 50), (110, 75)):
        halo = pygame.Surface((r_g * 2, r_g * 2), pygame.SRCALPHA)
        pygame.draw.circle(halo, (255, 230, 150, a_g),
                            (r_g, r_g), r_g)
        surf.blit(halo, (halo_cx - r_g, halo_cy - r_g))

    cx = W // 2
    cy = H // 2 + 50

    # ---- Trophy (goblet shape: wide top, narrows toward base) ----
    cup_top_w = 210
    cup_bot_w = 130
    cup_h = 150
    cup_top_y = cy - cup_h - 10
    cup_bot_y = cy - 10
    # Trapezoid points (top corners squarer, bottom rounded)
    t_tl = (cx - cup_top_w // 2, cup_top_y + 6)
    t_tr = (cx + cup_top_w // 2, cup_top_y + 6)
    t_br = (cx + cup_bot_w // 2, cup_bot_y)
    t_bl = (cx - cup_bot_w // 2, cup_bot_y)
    # Build the goblet body on its own layer so the gradient + specular
    # can be masked to its shape.
    body_layer = pygame.Surface((cup_top_w + 16, cup_h + 16),
                                pygame.SRCALPHA)
    local_pts = [(p[0] - (cx - cup_top_w // 2 - 8),
                   p[1] - (cup_top_y - 2))
                  for p in (t_tl, t_tr, t_br, t_bl)]
    # Outline (dark) drawn at +2px offset for chunky border
    pygame.draw.polygon(body_layer, OUTLINE,
                        [(p[0], p[1] + 2) for p in local_pts])
    pygame.draw.polygon(body_layer, OUTLINE,
                        [(p[0] - 2, p[1]) for p in local_pts])
    pygame.draw.polygon(body_layer, OUTLINE,
                        [(p[0] + 2, p[1]) for p in local_pts])
    # Gold gradient body filling the trapezoid - now combined with a
    # HORIZONTAL shading pass so the trophy reads as a 3D cylinder
    # (left side lit, right side in shadow)
    grad_rect = pygame.Rect(0, 0, body_layer.get_width(),
                              body_layer.get_height())
    grad_full = pygame.Surface(grad_rect.size, pygame.SRCALPHA)
    draw_gold_gradient_rect(grad_full, grad_rect)
    # Horizontal cylinder shading overlay: dark band on the right, bright
    # band on the left third
    bw = grad_full.get_width()
    cyl = pygame.Surface(grad_full.get_size(), pygame.SRCALPHA)
    for x in range(bw):
        u = x / max(1, bw - 1)
        # u<0.20 bright lit; u>0.65 darker shadow
        if u < 0.22:
            a = int(110 * (0.22 - u) / 0.22)
            pygame.draw.line(cyl, (255, 248, 220, a),
                              (x, 0), (x, grad_full.get_height()))
        elif u > 0.55:
            a = int(140 * (u - 0.55) / 0.45)
            pygame.draw.line(cyl, (40, 18, 4, a),
                              (x, 0), (x, grad_full.get_height()))
    grad_full.blit(cyl, (0, 0))
    # Mask gradient + shading to trapezoid
    mask = pygame.Surface(grad_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), local_pts)
    grad_full.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    body_layer.blit(grad_full, (0, 0))
    # Soft specular highlight ribbon on upper-left
    spec = pygame.Surface(grad_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(spec, (255, 255, 240, 130),
                        pygame.Rect(local_pts[0][0] + 8, local_pts[0][1] + 6,
                                    cup_top_w // 4, cup_h // 4))
    spec.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    body_layer.blit(spec, (0, 0))
    surf.blit(body_layer, (cx - cup_top_w // 2 - 8, cup_top_y - 2))

    # Rim-light: bright pixel-line along the top edge of the trophy cup
    pygame.draw.line(surf, (255, 248, 220),
                     (t_tl[0] + 4, t_tl[1] + 1),
                     (t_tr[0] - 4, t_tr[1] + 1), 2)
    # Compute cup rect for downstream positioning (rim, engraving, base)
    cup = pygame.Rect(t_tl[0], t_tl[1] - 6, cup_top_w, cup_h)
    # Rim band (slightly darker gold at the top)
    rim = pygame.Rect(cup.x - 4, cup.y - 4, cup.width + 8, 18)
    pygame.draw.rect(surf, OUTLINE, rim.inflate(2, 2), border_radius=8)
    pygame.draw.rect(surf, GOLD_DK, rim, border_radius=8)
    pygame.draw.rect(surf, GOLD_LO, rim.inflate(-6, -4), border_radius=6)

    # Engraved "3000" - multi-pass chisel for real carved depth.
    # Stack: darkest inset (lower-right) -> dark -> midtone -> highlight
    # (upper-left) -> brightest highlight pinpoint. Reads as a deep groove
    # with a polished bright lip on the lit side.
    fnt_engrave = _font(64, bold=True)
    ex = cup.centerx
    ey = cup.centery + 8
    chisel_passes = (
        (+2, +2, (40, 18, 4)),       # deep shadow well-bottom
        (+1, +1, GOLD_DK),           # transitional shadow
        ( 0,  0, (180, 120, 30)),    # midtone
        (-1, -1, (255, 230, 130)),   # lit lip
        (-2, -2, (255, 252, 220)),   # brightest highlight pinpoint
    )
    for dx, dy, col in chisel_passes:
        pass_surf = fnt_engrave.render("3000", True, col)
        surf.blit(pass_surf,
                  (ex - pass_surf.get_width() // 2 + dx,
                   ey - pass_surf.get_height() // 2 + dy))

    # Handles - proper open rings flanking the cup rim. Positioned to
    # visually attach at the upper edge of the goblet.
    for sgn in (-1, 1):
        hx = cx + sgn * (cup_top_w // 2 + 6)
        handle_rect = pygame.Rect(0, 0, 32, 64)
        if sgn == -1:
            handle_rect.topright = (hx, cup.y + 16)
        else:
            handle_rect.topleft = (hx, cup.y + 16)
        # Build the ring on an alpha layer
        ring = pygame.Surface(handle_rect.inflate(8, 8).size,
                              pygame.SRCALPHA)
        local = pygame.Rect(4, 4, handle_rect.width, handle_rect.height)
        # Outer outline
        pygame.draw.ellipse(ring, OUTLINE, local.inflate(4, 4))
        # Gold ring
        pygame.draw.ellipse(ring, GOLD_DK, local.inflate(2, 2))
        pygame.draw.ellipse(ring, GOLD_LO, local)
        # Highlight on outer top-left
        pygame.draw.ellipse(ring, GOLD_HI, local.inflate(-2, -2))
        # Punch out interior to make it a ring (transparent)
        inner = local.inflate(-12, -28)
        pygame.draw.ellipse(ring, (0, 0, 0, 0), inner)
        # Inner outline (dark band around the hole)
        pygame.draw.ellipse(ring, OUTLINE, inner.inflate(2, 2), width=2)
        surf.blit(ring,
                  (handle_rect.x - 4, handle_rect.y - 4))

    # Stem
    stem = pygame.Rect(cx - 22, cup.bottom - 4, 44, 36)
    pygame.draw.rect(surf, OUTLINE, stem.inflate(4, 4))
    draw_gold_gradient_rect(surf, stem)

    # Base
    base = pygame.Rect(cx - 85, stem.bottom, 170, 32)
    pygame.draw.rect(surf, OUTLINE, base.inflate(6, 4), border_radius=4)
    pygame.draw.rect(surf, GOLD_DK, base.inflate(4, 2), border_radius=4)
    draw_gold_gradient_rect(surf, base.inflate(-2, -2),
                             border_radius=3)
    # Plaque on base
    plaque = pygame.Rect(base.x + 16, base.y + 8, base.width - 32, 14)
    pygame.draw.rect(surf, OUTLINE, plaque.inflate(2, 2), border_radius=2)
    pygame.draw.rect(surf, (40, 22, 8), plaque, border_radius=2)
    fnt_p = _font(11, bold=True)
    pl = fnt_p.render("GAMES PLAYED", True, GOLD_HI)
    surf.blit(pl, (plaque.centerx - pl.get_width() // 2,
                    plaque.centery - pl.get_height() // 2))

    # Ribbon around the stem
    draw_ribbon_banner(surf, (cx, stem.centery + 8),
                       w=120, h=24,
                       text="WINNER",
                       color=KFC_RED, text_color=(255, 245, 230),
                       font_size=16, tilt_deg=-6)

    # ---- Pip rising out of the cup, wings raised triumphantly ----
    pip = parrot.get_hat_parrot(0, -12)
    pip_scaled = pygame.transform.smoothscale(
        pip, (int(pip.get_width() * 1.5),
              int(pip.get_height() * 1.5)))
    # Position so the bottom third of Pip is hidden behind the cup rim
    pip_x = cx - pip_scaled.get_width() // 2
    pip_y = cup.y - pip_scaled.get_height() + 26
    # Drop shadow behind Pip for separation against the trophy
    pip_sh = pygame.Surface(
        (pip_scaled.get_width() + 8, pip_scaled.get_height() + 4),
        pygame.SRCALPHA)
    pygame.draw.ellipse(pip_sh, (0, 0, 0, 110),
                        pygame.Rect(0, pip_scaled.get_height() // 2,
                                    pip_sh.get_width(),
                                    pip_sh.get_height() // 2 - 4))
    surf.blit(pip_sh, (pip_x - 4, pip_y - 2))
    surf.blit(pip_scaled, (pip_x, pip_y))
    # Sparkle burst around Pip
    rng = random.Random(4)
    for _ in range(8):
        sx = rng.randint(pip_x - 14, pip_x + pip_scaled.get_width() + 14)
        sy = rng.randint(pip_y - 10, pip_y + 30)
        r = rng.randint(2, 4)
        pygame.draw.circle(surf, OUTLINE, (sx, sy), r + 1)
        pygame.draw.circle(surf, GOLD_HI, (sx, sy), r)
        pygame.draw.circle(surf, (255, 255, 255), (sx - 1, sy - 1),
                           max(1, r - 2))

    # Gold-dust particles drifting upward
    draw_dust_particles(surf, n=35, color=GOLD_HI, seed=4,
                        area=pygame.Rect(20, 110, W - 40, H - 240),
                        rise=0)

    # ---- Headline + tagline ----
    # Thin rule above + small caps subhead
    pygame.draw.line(surf, GOLD_LO, (W // 2 - 90, 56),
                     (W // 2 + 90, 56), 1)
    fnt_sub = _font(16, bold=True)
    sub = fnt_sub.render("ACHIEVEMENT UNLOCKED", True, GOLD_HI)
    sub_o = fnt_sub.render("ACHIEVEMENT UNLOCKED", True, OUTLINE)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                surf.blit(sub_o, (W // 2 - sub.get_width() // 2 + dx,
                                   42 + dy))
    surf.blit(sub, (W // 2 - sub.get_width() // 2, 42))
    pygame.draw.line(surf, GOLD_LO, (W // 2 - 90, 76),
                     (W // 2 + 90, 76), 1)
    draw_big_text(surf, "3,000 GAMES", (W // 2, 110), size=38,
                  fill=COIN_GOLD, outline_w=4, sparkles=6)
    draw_tagline(surf, "Now do 5K.", H - 30, size=22,
                 color=(255, 240, 200))


# ===========================================================================
# V3 - "COIN STORM"
# ===========================================================================

def draw_v3(surf):
    draw_dawn_bg(surf)

    # ---- Soft sun rays streaming from the upper-right corner ----
    ray_origin = (W + 20, -20)
    n_rays = 14
    rays_layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(n_rays):
        # Angle sweep from straight-down to straight-left
        ang = math.pi * (0.55 + i * 0.30 / n_rays)
        L = max(W, H) + 50
        ex = ray_origin[0] + math.cos(ang) * L
        ey = ray_origin[1] + math.sin(ang) * L
        # Wedge polygon for each ray (thin triangle)
        spread = 0.022
        pts = [
            ray_origin,
            (ray_origin[0] + math.cos(ang - spread) * L,
             ray_origin[1] + math.sin(ang - spread) * L),
            (ray_origin[0] + math.cos(ang + spread) * L,
             ray_origin[1] + math.sin(ang + spread) * L),
        ]
        a = 28 if i % 2 == 0 else 18
        pygame.draw.polygon(rays_layer, (255, 230, 150, a), pts)
    # Bright glow near the ray origin (sun)
    for r_g, a_g in ((180, 60), (110, 100), (60, 160)):
        pygame.draw.circle(rays_layer, (255, 240, 180, a_g),
                            ray_origin, r_g)
    surf.blit(rays_layer, (0, 0))

    # ---- Pip mid-flap, big, tilted aggressively forward ----
    pip = parrot.get_parrot(0, 18)
    pip_scaled = pygame.transform.smoothscale(
        pip,
        (int(pip.get_width() * 2.4),
         int(pip.get_height() * 2.4)))
    pip_cx = W // 3 - 16
    pip_cy = H // 2 + 60
    pip_x = pip_cx - pip_scaled.get_width() // 2
    pip_y = pip_cy - pip_scaled.get_height() // 2

    # ---- Diagonal coin storm (drawn in BG behind Pip) ----
    rng = random.Random(13)
    bg_coins = []
    for _ in range(48):
        cx = rng.randint(-30, W + 30)
        cy = rng.randint(-20, H + 20)
        cy = int(cy * 0.4 + cx * 0.7 - 40)
        if not (-30 <= cy <= H + 30):
            continue
        r = rng.randint(6, 18)
        edge_on = rng.random() < 0.16
        tilt = rng.uniform(0.45, 1.0) if not edge_on else 1.0
        is_3k = (rng.random() < 0.16 and not edge_on and r >= 13)
        label = "3K" if is_3k else ("$" if r >= 11 else None)
        bg_coins.append((cx, cy, r, edge_on, tilt, label, is_3k))
    for cx, cy, r, edge_on, tilt, label, is_3k in bg_coins:
        # Halo behind featured 3K coins
        if is_3k:
            halo = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            for hr, ha in ((r * 2, 50), (int(r * 1.5), 90)):
                pygame.draw.circle(halo, (255, 240, 130, ha),
                                    (r * 2, r * 2), hr)
            surf.blit(halo, (cx - r * 2, cy - r * 2))
        draw_coin(surf, cx, cy, r, edge_on=edge_on,
                   tilt=tilt, label=label, seed=cx * 7 + cy)

    # Speed-line tails behind Pip
    speed_layer = pygame.Surface((W, H), pygame.SRCALPHA)
    rng2 = random.Random(21)
    for _ in range(18):
        sy = rng2.randint(pip_cy - 60, pip_cy + 60)
        sx_start = pip_cx + 30
        L = rng2.randint(70, 150)
        sx_end = sx_start - L
        # Tapered streak
        for k in range(6):
            t0 = k / 6
            t1 = (k + 1) / 6
            a = int(220 * (1 - t0))
            w = max(1, 5 - k)
            x0 = sx_start + (sx_end - sx_start) * t0
            x1 = sx_start + (sx_end - sx_start) * t1
            pygame.draw.line(speed_layer, (255, 255, 255, a),
                              (x0, sy), (x1, sy), w)
    surf.blit(speed_layer, (0, 0))

    # Drop shadow + Pip
    pip_sh = pygame.Surface(
        (pip_scaled.get_width() + 16, 20), pygame.SRCALPHA)
    pygame.draw.ellipse(pip_sh, (0, 0, 0, 90), pip_sh.get_rect())
    surf.blit(pip_sh,
              (pip_x - 8, pip_y + pip_scaled.get_height() - 10))
    surf.blit(pip_scaled, (pip_x, pip_y))

    # ---- Foreground coins overlapping Pip on the right for depth ----
    for _ in range(10):
        cx_f = rng.randint(W // 2 - 20, W + 20)
        cy_f = rng.randint(30, H - 60)
        r_f = rng.randint(10, 18)
        edge_on = rng.random() < 0.2
        is_3k = (rng.random() < 0.18 and not edge_on and r_f >= 13)
        label = "3K" if is_3k else ("$" if r_f >= 11 else None)
        if is_3k:
            halo = pygame.Surface((r_f * 4, r_f * 4), pygame.SRCALPHA)
            for hr, ha in ((r_f * 2, 60), (int(r_f * 1.5), 100)):
                pygame.draw.circle(halo, (255, 240, 130, ha),
                                    (r_f * 2, r_f * 2), hr)
            surf.blit(halo, (cx_f - r_f * 2, cy_f - r_f * 2))
        draw_coin(surf, cx_f, cy_f, r_f, edge_on=edge_on,
                   label=label, seed=cx_f * 11)

    # ---- Hero ribbon banner ----
    draw_ribbon_banner(surf, (W // 2 + 30, 95),
                       w=200, h=58,
                       text="3,000!",
                       color=KFC_RED, text_color=GOLD_HI,
                       font_size=36, tilt_deg=-10)
    draw_tagline(surf, "GAMES PLAYED", 165, size=18,
                  color=(255, 240, 200))

    # ---- Tagline ----
    draw_tagline(surf, "Can't stop. Won't stop.",
                  H - 56, size=22, color=(255, 255, 255))
    draw_tagline(surf, "One more run?", H - 28, size=18,
                  color=(255, 220, 160))


# ===========================================================================
# V4 - "PIP PODIUM"
# ===========================================================================

def draw_v4(surf):
    draw_indigo_magenta_bg(surf)
    starfield(surf, n=35, seed=4)

    # Two converging spotlight cones from upper corners
    draw_spotlight_beam(surf,
                        top_anchor=(60, 40),
                        length=H - 200,
                        half_width_top=20,
                        half_width_bot=130,
                        color=(255, 240, 200), alpha=60)
    draw_spotlight_beam(surf,
                        top_anchor=(W - 60, 40),
                        length=H - 200,
                        half_width_top=20,
                        half_width_bot=130,
                        color=(255, 240, 200), alpha=60)

    # Stage floor: dark gradient strip at bottom
    floor_h = 80
    floor = pygame.Surface((W, floor_h), pygame.SRCALPHA)
    for y in range(floor_h):
        u = y / (floor_h - 1)
        a = int(200 * u)
        floor.fill((10, 6, 20, a), pygame.Rect(0, y, W, 1))
    surf.blit(floor, (0, H - floor_h))
    # Audience silhouette (gentle humps)
    aud_y = H - 28
    for hx in range(-10, W + 20, 18):
        bump_w = 16
        bump_h = 10
        pygame.draw.ellipse(surf, (5, 4, 16),
                            pygame.Rect(hx, aud_y, bump_w, bump_h * 2))

    # ---- Podiums ----
    # Center (gold) - tallest
    center_x = W // 2
    podium_w = 78
    podium_top_y = 360
    podium_bot_y = H - 50

    def _draw_podium(cx_in, top_y, label, base_color):
        rect = pygame.Rect(cx_in - podium_w // 2, top_y,
                            podium_w, podium_bot_y - top_y)
        pygame.draw.rect(surf, OUTLINE, rect.inflate(4, 4),
                         border_radius=4)
        # Body gradient
        pad = pygame.Surface(rect.size, pygame.SRCALPHA)
        for y in range(rect.height):
            u = y / max(1, rect.height - 1)
            c = tuple(int(base_color[k] + (_shade(base_color, -50)[k]
                                            - base_color[k]) * u)
                      for k in range(3))
            pad.fill(c, pygame.Rect(0, y, rect.width, 1))
        surf.blit(pad, rect.topleft)
        # Top face highlight
        pygame.draw.rect(surf, _shade(base_color, +30),
                         pygame.Rect(rect.x + 4, rect.y + 4,
                                     rect.width - 8, 8))
        # Plaque
        plq = pygame.Rect(rect.x + 8, rect.bottom - 32,
                           rect.width - 16, 22)
        pygame.draw.rect(surf, OUTLINE, plq.inflate(2, 2),
                         border_radius=3)
        pygame.draw.rect(surf, (40, 22, 8), plq, border_radius=2)
        fnt = _font(13, bold=True)
        txt = fnt.render(label, True, GOLD_HI)
        surf.blit(txt, (plq.centerx - txt.get_width() // 2,
                        plq.centery - txt.get_height() // 2))

    # 3 physical podiums on the stage. Ghost-Pip floats in the air
    # above (no podium - it's a ghost) so the composition stays clean.
    _draw_podium(center_x - 90, podium_top_y + 40,
                 "KFC", (220, 200, 200))   # silver
    _draw_podium(center_x + 90, podium_top_y + 56,
                 "HAT", (180, 100, 50))    # bronze
    _draw_podium(center_x, podium_top_y, "PIP",
                  (240, 200, 80))          # centre gold

    # ---- Pip variants on each podium ----
    def _blit_centered(img, cx_in, y_top, alpha=255):
        if alpha < 255:
            img = img.copy()
            img.set_alpha(alpha)
        surf.blit(img,
                  (cx_in - img.get_width() // 2,
                   y_top - img.get_height() + 6))

    pip_normal = parrot.get_parrot(0, -8)
    pip_kfc    = parrot.get_fried_parrot(1, -6)
    pip_hat    = parrot.get_hat_parrot(1, -6)
    pip_ghost  = parrot.get_ghost_parrot(1, -4)

    _blit_centered(pip_kfc,    center_x - 90, podium_top_y + 40)
    _blit_centered(pip_hat,    center_x + 90, podium_top_y + 56)
    _blit_centered(pip_normal, center_x,      podium_top_y)
    # Ghost-Pip floats above the stage, between the spotlights.
    ghost_layer = pip_ghost.copy()
    ghost_layer.set_alpha(200)
    surf.blit(ghost_layer,
              (center_x + 80, podium_top_y - 90))
    # Ghost label tag
    g_fnt = _font(11, bold=True)
    g_lbl = g_fnt.render("GHOST", True, (200, 210, 240))
    g_lbl_o = g_fnt.render("GHOST", True, OUTLINE)
    g_cx = center_x + 80 + pip_ghost.get_width() // 2
    g_cy = podium_top_y - 90 + pip_ghost.get_height() + 6
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                surf.blit(g_lbl_o, (g_cx - g_lbl.get_width() // 2 + dx,
                                     g_cy + dy))
    surf.blit(g_lbl, (g_cx - g_lbl.get_width() // 2, g_cy))

    # Tiny flag in normal Pip's wing
    flag_pole_x = center_x + 14
    flag_pole_top = podium_top_y - 32
    pygame.draw.line(surf, OUTLINE,
                      (flag_pole_x, flag_pole_top),
                      (flag_pole_x, podium_top_y), 3)
    flag = [(flag_pole_x, flag_pole_top),
            (flag_pole_x + 22, flag_pole_top + 4),
            (flag_pole_x + 18, flag_pole_top + 10),
            (flag_pole_x + 22, flag_pole_top + 16),
            (flag_pole_x, flag_pole_top + 14)]
    pygame.draw.polygon(surf, OUTLINE,
                        [(p[0] + 1, p[1] + 1) for p in flag])
    pygame.draw.polygon(surf, KFC_RED, flag)
    fnt_flag = _font(11, bold=True)
    fl = fnt_flag.render("3K", True, KFC_WHITE)
    surf.blit(fl, (flag_pole_x + 2, flag_pole_top + 2))

    # ---- Banner across top ----
    draw_ribbon_banner(surf, (W // 2, 70),
                       w=240, h=42,
                       text="HALL OF FAME",
                       color=KFC_RED, text_color=GOLD_HI,
                       font_size=22, tilt_deg=0)

    # ---- Big number below banner ----
    draw_big_text(surf, "3,000 RUNS", (W // 2, 138),
                   size=32, fill=COIN_GOLD,
                   outline_w=4, sparkles=6)

    # Confetti spilling from top
    draw_confetti_layered(surf,
                           n_back=50, n_front=14, seed=8)

    # Tagline
    draw_tagline(surf, "Dodge. Dip. Dive.", H - 62, size=20,
                 color=(255, 255, 255))
    draw_tagline(surf, "Your turn.", H - 34, size=22,
                 color=(255, 220, 160))


# ===========================================================================
# V5 - "EXTRA EXTRA"
# ===========================================================================

def draw_v5(surf):
    # Render to a slightly oversized surface so we can rotate at the end
    # without clipping the corners.
    pad = 28
    paper = pygame.Surface((W + pad * 2, H + pad * 2))
    paper.fill(PAPER_BG)

    # Halftone-ish dot grain - 4px grid with subtle alpha noise
    rng = random.Random(99)
    grain_layer = pygame.Surface((W + pad * 2, H + pad * 2), pygame.SRCALPHA)
    for y in range(0, H + pad * 2, 4):
        for x in range(0, W + pad * 2, 4):
            if rng.random() < 0.35:
                a = rng.randint(8, 26)
                pygame.draw.circle(grain_layer, (140, 100, 50, a),
                                    (x, y), 1)
    paper.blit(grain_layer, (0, 0))

    # Darker edge grain (vignette - heavier dots near edges)
    edge_layer = pygame.Surface((W + pad * 2, H + pad * 2),
                                 pygame.SRCALPHA)
    for _ in range(900):
        # bias to near edges
        if rng.random() < 0.5:
            x = rng.randint(0, 40) if rng.random() < 0.5 \
                else rng.randint(W + pad * 2 - 40, W + pad * 2 - 1)
            y = rng.randint(0, H + pad * 2 - 1)
        else:
            y = rng.randint(0, 40) if rng.random() < 0.5 \
                else rng.randint(H + pad * 2 - 40, H + pad * 2 - 1)
            x = rng.randint(0, W + pad * 2 - 1)
        a = rng.randint(20, 80)
        pygame.draw.circle(edge_layer, (100, 70, 30, a), (x, y), 1)
    paper.blit(edge_layer, (0, 0))

    inner_origin = (pad, pad)

    def to_paper(x, y):
        return (x + inner_origin[0], y + inner_origin[1])

    # ---- Masthead ----
    mast_fnt = _font(36, bold=True)
    mast_txt = mast_fnt.render("SKYBIT TIMES", True, PAPER_INK)
    mast_x = to_paper(W // 2 - mast_txt.get_width() // 2, 18)
    paper.blit(mast_txt, mast_x)
    # Flourish asterisks
    a_fnt = _font(20, bold=True)
    for sgn, x_off in ((-1, -20), (1, 20)):
        a = a_fnt.render("*", True, PAPER_INK)
        paper.blit(a, to_paper(W // 2 - a.get_width() // 2
                                + (mast_txt.get_width() // 2 + x_off) * sgn,
                                24))
    # Double rules
    p_y1 = inner_origin[1] + 60
    p_y2 = inner_origin[1] + 66
    pygame.draw.line(paper, PAPER_RULE,
                      (inner_origin[0] + 16, p_y1),
                      (inner_origin[0] + W - 16, p_y1), 3)
    pygame.draw.line(paper, PAPER_RULE,
                      (inner_origin[0] + 16, p_y2),
                      (inner_origin[0] + W - 16, p_y2), 1)
    iss_fnt = _font(11, bold=False)
    iss = iss_fnt.render("VOL. 1 | ISSUE 3000 | LATE EDITION",
                          True, PAPER_RULE)
    paper.blit(iss, to_paper(W // 2 - iss.get_width() // 2, 72))
    pygame.draw.line(paper, PAPER_RULE,
                      (inner_origin[0] + 16, inner_origin[1] + 90),
                      (inner_origin[0] + W - 16, inner_origin[1] + 90), 1)

    # ---- BREAKING NEWS stamp - red, rotated, overlapping ----
    stamp_layer = pygame.Surface((180, 70), pygame.SRCALPHA)
    stamp_rect = pygame.Rect(0, 0, 180, 50)
    pygame.draw.rect(stamp_layer, KFC_RED_D, stamp_rect.inflate(-4, -4),
                     border_radius=4, width=3)
    pygame.draw.rect(stamp_layer, (180, 30, 30, 30),
                     stamp_rect.inflate(-12, -12),
                     border_radius=4)
    st_fnt = _font(22, bold=True)
    st_top = st_fnt.render("BREAKING", True, KFC_RED_D)
    st_bot = st_fnt.render("NEWS", True, KFC_RED_D)
    stamp_layer.blit(st_top, ((180 - st_top.get_width()) // 2, 4))
    stamp_layer.blit(st_bot, ((180 - st_bot.get_width()) // 2, 24))
    stamp_layer = pygame.transform.rotate(stamp_layer, -10)
    # Stamp lives BELOW the masthead rules so it doesn't eat the title
    paper.blit(stamp_layer,
                to_paper(W - stamp_layer.get_width() + 18, 84))

    # ---- Headline ----
    hd_fnt = _font(54, bold=True)
    line1 = hd_fnt.render("PIP HITS", True, PAPER_INK)
    line2 = hd_fnt.render("3,000!", True, PAPER_INK)
    paper.blit(line1, to_paper(W // 2 - line1.get_width() // 2, 106))
    paper.blit(line2, to_paper(W // 2 - line2.get_width() // 2, 158))

    # ---- Subhead ----
    sub_fnt = _font(15, bold=True)
    sub_lines = ("Scarlet macaw shatters four-figure mark",
                 "(again) - city left in disbelief")
    for i, sl in enumerate(sub_lines):
        s = sub_fnt.render(sl, True, PAPER_INK)
        paper.blit(s, to_paper(W // 2 - s.get_width() // 2, 218 + i * 18))

    # ---- Hero photo of Pip ----
    photo_w = 220
    photo_h = 200
    photo = pygame.Rect(0, 0, photo_w, photo_h)
    photo.center = (W // 2, 358)
    photo_paper = pygame.Rect(photo.x + inner_origin[0],
                               photo.y + inner_origin[1],
                               photo.width, photo.height)
    # Frame
    pygame.draw.rect(paper, PAPER_INK,
                      photo_paper.inflate(8, 8))
    pygame.draw.rect(paper, (245, 235, 205),
                      photo_paper.inflate(2, 2))
    # Sky inside photo
    photo_sky_pal = _biome.palette_for_phase(0.55)
    photo_sky = get_sky_surface_biome(
        photo.width, photo.height, photo.height,
        photo_sky_pal,
        int(0.55 * _biome.PHASE_BUCKETS))
    paper.blit(photo_sky, photo_paper.topleft)
    # Pip - larger
    pip = parrot.get_parrot(0, -8)
    pip_b = pygame.transform.smoothscale(
        pip, (int(pip.get_width() * 2.0),
              int(pip.get_height() * 2.0)))
    paper.blit(pip_b,
               (photo_paper.centerx - pip_b.get_width() // 2,
                photo_paper.centery - pip_b.get_height() // 2 + 6))
    # Halftone-dot overlay on photo
    dot_layer = pygame.Surface(photo.size, pygame.SRCALPHA)
    for y in range(0, photo.height, 3):
        for x in range(0, photo.width, 3):
            if (x + y) % 6 == 0:
                pygame.draw.circle(dot_layer, (0, 0, 0, 30), (x, y), 1)
    paper.blit(dot_layer, photo_paper.topleft)
    # Photo caption strip below photo
    cap_strip = pygame.Rect(photo_paper.x, photo_paper.bottom + 2,
                             photo.width, 16)
    pygame.draw.rect(paper, (235, 222, 188), cap_strip)
    cap_fnt = _font(10, bold=False)
    cap = cap_fnt.render("PHOTO: Pip, mid-victory-flap. STAFF.",
                          True, PAPER_RULE)
    paper.blit(cap, (cap_strip.centerx - cap.get_width() // 2,
                      cap_strip.centery - cap.get_height() // 2))

    # ---- Body taunt ----
    body_fnt = _font(18, bold=True)
    body = body_fnt.render("Can YOU help him reach 5K?",
                            True, PAPER_INK)
    paper.blit(body, to_paper(W // 2 - body.get_width() // 2, 488))

    # ---- Pull-quote box with dashed border ----
    pq_rect = pygame.Rect(0, 0, 280, 60)
    pq_rect.center = (W // 2, 552)
    pq_paper = pygame.Rect(pq_rect.x + inner_origin[0],
                            pq_rect.y + inner_origin[1],
                            pq_rect.width, pq_rect.height)
    # Dashed border
    for x in range(pq_paper.left, pq_paper.right, 6):
        pygame.draw.line(paper, PAPER_RULE,
                          (x, pq_paper.top),
                          (min(x + 3, pq_paper.right), pq_paper.top), 1)
        pygame.draw.line(paper, PAPER_RULE,
                          (x, pq_paper.bottom),
                          (min(x + 3, pq_paper.right), pq_paper.bottom), 1)
    for y in range(pq_paper.top, pq_paper.bottom, 6):
        pygame.draw.line(paper, PAPER_RULE,
                          (pq_paper.left, y),
                          (pq_paper.left, min(y + 3, pq_paper.bottom)), 1)
        pygame.draw.line(paper, PAPER_RULE,
                          (pq_paper.right, y),
                          (pq_paper.right, min(y + 3, pq_paper.bottom)), 1)
    q_fnt = _font(17, bold=True)
    q = q_fnt.render('"Just one more run."', True, PAPER_INK)
    paper.blit(q, (pq_paper.centerx - q.get_width() // 2,
                    pq_paper.top + 8))
    qa_fnt = _font(12, bold=False)
    qa = qa_fnt.render("- witness, mid-flap", True, PAPER_RULE)
    paper.blit(qa, (pq_paper.centerx - qa.get_width() // 2,
                     pq_paper.top + 34))

    # Fold-crease diagonal line for paper-folded effect
    crease = pygame.Surface((W + pad * 2, H + pad * 2), pygame.SRCALPHA)
    pygame.draw.line(crease, (110, 80, 30, 22),
                      (inner_origin[0] + 40, inner_origin[1] + H - 4),
                      (inner_origin[0] + W - 40, inner_origin[1] + 4), 2)
    paper.blit(crease, (0, 0))

    # ---- Rotate the whole paper slightly + composite onto surf ----
    rotated = pygame.transform.rotate(paper, 1.6)
    # Center the rotated paper on the surf
    surf.fill((40, 28, 12))   # dark backing visible at edges
    rx = (W - rotated.get_width()) // 2
    ry = (H - rotated.get_height()) // 2
    surf.blit(rotated, (rx, ry))


# --- Variant registry + main -----------------------------------------------

VARIANTS = (
    ("v1", "V1 Bucket Party",     draw_v1),
    ("v2", "V2 Trophy Spotlight", draw_v2),
    ("v3", "V3 Coin Storm",       draw_v3),
    ("v4", "V4 Pip Podium",       draw_v4),
    ("v5", "V5 Extra Extra",      draw_v5),
)


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((W, H))
    out_dir = os.path.join("docs", "celebrations", "3k_games")
    os.makedirs(out_dir, exist_ok=True)

    frames = {}
    for key, label, fn in VARIANTS:
        screen.fill((0, 0, 0))
        fn(screen)
        frames[key] = screen.copy()
        path = os.path.join(out_dir, f"{key}.png")
        pygame.image.save(screen, path)
        print(f"saved {path}  ({label})")

    # 5-column compare strip
    GAP, LABEL_H, PAD = 14, 30, 18
    cell_w, cell_h = W, H
    canvas_w = cell_w * len(VARIANTS) + GAP * (len(VARIANTS) - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((230, 232, 235))
    label_font = pygame.font.SysFont(None, 22, bold=True)
    for i, (key, label, _) in enumerate(VARIANTS):
        x = PAD + i * (cell_w + GAP)
        y = PAD
        pygame.draw.rect(canvas, (60, 70, 100),
                         pygame.Rect(x - 1, y - 1, cell_w + 2, cell_h + 2),
                         width=1)
        canvas.blit(frames[key], (x, y))
        lbl = label_font.render(label, True, (30, 35, 55))
        canvas.blit(lbl, (x + (cell_w - lbl.get_width()) // 2,
                          y + cell_h + 8))
    out_path = os.path.join(out_dir, "compare.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  {canvas.get_size()}")


if __name__ == "__main__":
    sys.exit(main() or 0)
