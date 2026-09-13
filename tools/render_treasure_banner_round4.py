"""Treasure Box cycle-finale reveal — Round 4 exploration sheet.

Round 3 was ITERATE. The critic's blocker: the hero panel drew pillars at
3× hero scale, divorced from real PIPE_W / GROUND_Y geometry, so the
"does the celebration READ in the actual game" question couldn't be
answered. Round 4 rebuilds the hero AND the 1× thumbnail from a single
ground-truth render that uses the real config constants — PIPE_W = 58,
GROUND_Y = 595, gap_y ≈ 325, gap_h ≈ 170 — then upscales the same surface
for the hero panel. Identical pixels, two viewing sizes.

Cell map (unchanged from round 3 shape):

  ┌────────────── Cell 1 (HERO, 2-wide) ──────────────┐
  │  REAL game geometry, upscaled 3×                   │
  │  pillars, open chest, banner, garland, confetti    │
  ├──────────────────────────┬─────────────────────────┤
  │ Cell 2  banner zoom       │ Cell 3  garland zoom    │
  │ V3 firework polish        │ 8 bulbs, hot-yellow     │
  │ + ray-clip vs ribbon      │ filament cores          │
  ├──────────────────────────┼─────────────────────────┤
  │ Cell 4  asymmetric        │ Cell 5  1× ACTUAL game  │
  │ pillar heights            │ canvas thumb (360 wide) │
  ├──────────────────────────┼─────────────────────────┤
  │ Cell 6 motion check  chest pillar scrolled 30 px L │
  └────────────────────────────────────────────────────┘

Re-runnable; doc-only — never bundled into the WASM/desktop builds.

Output: docs/treasure_box/banner_designs.png (overwrites Round 3)."""
from __future__ import annotations

import math
import os
import random
import sys

# Headless so this runs in CI / over SSH / inside the design loop.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

pygame.init()
pygame.display.set_mode((1, 1))

from game.hud import _font
from game.config import PIPE_W, GROUND_Y

# ── Locked palette — round-2 critic notes finalised these ──────────────────

GOLD_HIGHLIGHT = (255, 244, 188)
GOLD_HOT       = (255, 220, 110)
GOLD_SAT       = (240, 188,  56)
GOLD_AMBER     = (196, 132,  28)
GOLD_INK       = ( 72,  48,  12)
VELVET         = (168,  32,  16)
VELVET_HI      = (220,  64,  32)
STAR_CREAM     = (252, 244, 218)

# V3 firework warm-accent trio (round 3 locked).
FIRE_RED       = (248,  96,  88)
FIRE_GOLD      = (255, 220, 110)
FIRE_ORANGE    = (255, 128,  48)

# Festoon bulb spec.
# Round-4 filament decision: Option A — replace the 1-px scarlet bar
# with a 1-px hot-yellow centre dot. The scarlet bar was the same colour
# family as the velvet rim under the banner and visually disappeared at
# game scale; a hot-yellow core sits well inside the warm-white bulb
# body and reads as a LIT filament glow even when the outer halo dims
# to match the twilight sky. Keeps the "Edison bulb" silhouette intact.
BULB_BODY      = (255, 240, 200)
BULB_FILAMENT  = (255, 236, 128)         # hot-yellow lit core (round-4 Option A)
BULB_HALO      = (255, 220, 110)
CATENARY       = ( 48,  32,  12)

# Twilight sky — cycle-finale phase.
SKY_TOP = (255, 168,  96)
SKY_BOT = (168, 132, 188)

# Pillar sandstone.
PILLAR_BODY    = (118,  78,  36)
PILLAR_DARK    = ( 64,  40,  18)
PILLAR_LIGHT   = (160, 108,  48)

CHEST_WOOD     = (132,  72,  28)
CHEST_DARK     = ( 60,  32,  10)
CHEST_GOLD     = (244, 188,  56)
COIN_GOLD      = (255, 208,  72)
COIN_RIM       = (152,  92,  16)

# Confetti palette (round-4 spec).
CONFETTI_COLOURS = (
    (255, 220, 110),    # GOLD
    (220,  64,  32),    # SCARLET
    (255, 128,  48),    # ORANGE
    (252, 244, 218),    # CREAM
)

# Banner silhouette dims — round-2 locked, supersampled 2×.
BANNER_W = 340
BANNER_H = 78
NOTCH    = 20
OUTLINE  = 3
SHADOW_DX = 4
SHADOW_DY = 5
SS = 2


# ── Banner construction (round-3 locked) ───────────────────────────────────


def _ribbon_polygon(bw: int, bh: int, notch: int) -> list[tuple[int, int]]:
    """Notched forked-end ribbon — chevron cuts on left + right."""
    return [
        (0, 0), (bw, 0),
        (bw - notch, bh // 2),
        (bw, bh), (0, bh),
        (notch, bh // 2),
    ]


def _multi_stop_gradient(bw: int, bh: int) -> pygame.Surface:
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    stops = (
        (0.00, GOLD_HIGHLIGHT),
        (0.15, GOLD_HOT),
        (0.55, GOLD_SAT),
        (0.92, GOLD_AMBER),
        (1.00, GOLD_AMBER),
    )
    for yy in range(bh):
        t = yy / max(1, bh - 1)
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
                col = (
                    int(c0[0] + (c1[0] - c0[0]) * f),
                    int(c0[1] + (c1[1] - c0[1]) * f),
                    int(c0[2] + (c1[2] - c0[2]) * f),
                )
                break
        else:
            col = stops[-1][1]
        pygame.draw.line(surf, col, (0, yy), (bw, yy))
    return surf


def _build_banner_hires(day: int) -> pygame.Surface:
    """Bake one banner at SS× supersample then smoothscale to canonical.
    Round-3 lock; not re-tuned this pass."""
    bw = BANNER_W * SS
    bh = BANNER_H * SS
    notch = NOTCH * SS
    sdx = SHADOW_DX * SS
    sdy = SHADOW_DY * SS
    outline = max(2, OUTLINE * SS)

    comp_w = bw + sdx
    comp_h = bh + sdy
    comp = pygame.Surface((comp_w, comp_h), pygame.SRCALPHA)

    ribbon = _ribbon_polygon(bw, bh, notch)

    shadow_pts = [(x + sdx, y + sdy) for (x, y) in ribbon]
    pygame.draw.polygon(comp, (0, 0, 0, 170), shadow_pts)

    body = _multi_stop_gradient(bw, bh)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), ribbon)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    comp.blit(body, (0, 0))

    rim_h = 8 * SS
    rim = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(rim, VELVET, (0, bh - rim_h, bw, rim_h))
    pygame.draw.line(rim, VELVET_HI, (0, bh - rim_h),
                     (bw, bh - rim_h), max(1, SS))
    rim.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    comp.blit(rim, (0, 0))

    bevel_top = pygame.Surface((bw, bh), pygame.SRCALPHA)
    bevel_bot = pygame.Surface((bw, bh), pygame.SRCALPHA)
    inner_pts_top = [(x, y + max(1, SS)) for (x, y) in ribbon]
    inner_pts_bot = [(x, y - max(1, SS)) for (x, y) in ribbon]
    pygame.draw.polygon(bevel_top, (255, 255, 255, 78),
                        inner_pts_top, max(1, 2 * SS))
    pygame.draw.polygon(bevel_bot, (0, 0, 0, 120),
                        inner_pts_bot, max(1, 2 * SS))
    bevel_top.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    bevel_bot.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    comp.blit(bevel_top, (0, 0))
    comp.blit(bevel_bot, (0, 0))

    pygame.draw.polygon(comp, GOLD_INK, ribbon, outline)

    for (sx, sy) in (
        (notch + 14 * SS,         14 * SS),
        (bw - notch - 14 * SS,    14 * SS),
        (notch + 14 * SS,         bh - 14 * SS),
        (bw - notch - 14 * SS,    bh - 14 * SS),
    ):
        pygame.draw.circle(comp, STAR_CREAM, (sx, sy), 3 * SS)
        pygame.draw.circle(comp, (255, 255, 255),
                           (sx - SS, sy - SS), max(1, SS))

    text_str = (f"DAY {day} COMPLETE!"
                if 1 <= day <= 99 else "DAY COMPLETE!")
    font_size = 34 * SS
    font = _font(font_size, bold=True)
    margin = notch + 22 * SS
    while font.size(text_str)[0] > bw - margin * 2 and font_size > 22 * SS:
        font_size -= 2 * SS
        font = _font(font_size, bold=True)

    text_cream = font.render(text_str, True, STAR_CREAM)
    text_white = font.render(text_str, True, (255, 255, 255))
    text_white.set_alpha(180)
    text_dark  = font.render(text_str, True, GOLD_INK)
    text_dark.set_alpha(220)
    out_render = font.render(text_str, True, GOLD_INK)

    tw, th = text_cream.get_size()
    tx = (bw - tw) // 2
    ty = (bh - th) // 2 - 3 * SS

    o = max(2, 2 * SS)
    for ox, oy in ((-o, 0), (o, 0), (0, -o), (0, o),
                   (-o, -o), (o, -o), (-o, o), (o, o)):
        comp.blit(out_render, (tx + ox, ty + oy))
    comp.blit(text_white, (tx, ty - 1))
    comp.blit(text_dark,  (tx, ty + 1))
    comp.blit(text_cream, (tx, ty))

    final_w = BANNER_W + SHADOW_DX
    final_h = BANNER_H + SHADOW_DY
    return pygame.transform.smoothscale(comp, (final_w, final_h))


def _ribbon_screen_polygon(bw: int, bh: int, notch: int,
                            origin_x: int, origin_y: int) -> list[tuple[int, int]]:
    """Same ribbon outline as `_build_banner_hires` but at canonical
    (un-supersampled) coords and translated to where it sits on the scene
    surface — used as the mask for the firework-ray clip (fix #6)."""
    base = _ribbon_polygon(bw, bh, notch)
    return [(x + origin_x, y + origin_y) for (x, y) in base]


# ── Firework motif (round-3 locked) ────────────────────────────────────────


def _draw_glow_disc(surf, cx, cy, radius, color, alpha):
    disc = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    steps = 18
    for i in range(steps):
        f = 1.0 - i / steps
        r = int(radius * f)
        a = int(alpha * (f ** 3) * 1.4)
        if r <= 0 or a <= 0:
            continue
        pygame.draw.circle(disc, (*color, min(a, 255)),
                           (radius, radius), r)
    surf.blit(disc, (cx - radius, cy - radius))


def _draw_starburst(surf, cx, cy, color, scale=1.0, opacity=255):
    rays = 16
    r_long  = int(70 * scale)
    r_short = int(r_long * 0.55)
    long_half  = max(1, int(r_long * 0.085))
    short_half = max(1, int(r_long * 0.06))

    if opacity < 255:
        pad = r_long + 16
        layer = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
        ox, oy = pad, pad
        target = layer
    else:
        ox, oy = cx, cy
        target = surf

    for k in range(rays):
        ang = -math.pi / 2 + k * (math.tau / rays)
        long_ray = (k % 2 == 0)
        r_tip = r_long if long_ray else r_short
        half = long_half if long_ray else short_half
        col = color if long_ray else STAR_CREAM
        tip = (ox + math.cos(ang) * r_tip,
               oy + math.sin(ang) * r_tip)
        a = (ox + math.cos(ang + math.pi / 2) * half,
             oy + math.sin(ang + math.pi / 2) * half)
        b = (ox + math.cos(ang - math.pi / 2) * half,
             oy + math.sin(ang - math.pi / 2) * half)
        pygame.draw.polygon(target, col, [tip, a, b])

    rng = random.Random(int(cx * 13 + cy * 7 + scale * 991))
    for k in range(0, rays, 2):
        ang = -math.pi / 2 + k * (math.tau / rays)
        tx = ox + math.cos(ang) * r_long * 1.12
        ty = oy + math.sin(ang) * r_long * 1.12
        pygame.draw.circle(target, STAR_CREAM, (int(tx), int(ty)), 2)
        pygame.draw.circle(target, (255, 255, 255),
                           (int(tx) - 1, int(ty) - 1), 1)
    for _ in range(16):
        ang = rng.uniform(0, math.tau)
        d = rng.uniform(r_short * 0.6, r_long * 0.95)
        sx = ox + math.cos(ang) * d
        sy = oy + math.sin(ang) * d * 0.75
        pygame.draw.circle(target, STAR_CREAM, (int(sx), int(sy)), 1)

    if opacity < 255:
        layer.set_alpha(opacity)
        surf.blit(layer, (cx - pad, cy - pad))


def _bake_firework_bursts(w: int, h: int, cx: int, cy: int) -> pygame.Surface:
    """Render the V3 firework cluster onto its own SRCALPHA layer so we
    can mask it against the ribbon silhouette before compositing. The
    bake takes the same (cx, cy) and palette as the in-place version
    used in round 3."""
    layer = pygame.Surface((w, h), pygame.SRCALPHA)
    # Outer demoted bursts FIRST so their wisps duck under centre burst.
    _draw_glow_disc(layer, cx - 165, cy - 58, 70, FIRE_RED, 50)
    _draw_starburst(layer, cx - 165, cy - 58, FIRE_RED,
                    scale=0.78, opacity=102)
    _draw_glow_disc(layer, cx + 165, cy - 58, 70, FIRE_ORANGE, 50)
    _draw_starburst(layer, cx + 165, cy - 58, FIRE_ORANGE,
                    scale=0.78, opacity=102)
    # Dominant centre gold burst.
    _draw_glow_disc(layer, cx, cy, 170, FIRE_GOLD, 95)
    _draw_starburst(layer, cx, cy, FIRE_GOLD, scale=1.6, opacity=255)
    return layer


def _draw_firework_bursts_clipped(surf, cx: int, cy: int,
                                  ribbon_poly: list[tuple[int, int]] | None,
                                  ribbon_inset: int = 2):
    """Round-4 fix #6: bake the firework cluster, then carve a hole in
    it shaped like the ribbon (slightly inset so rays don't kiss the
    outline either) before blitting to the scene. Rays that previously
    crossed the ribbon notch now stop at the ribbon edge — the cleanest
    silhouette in the composition stays clean.

    `ribbon_poly` may be None for cells where there is no banner (the
    garland-only cells). In that case we render without clipping."""
    w, h = surf.get_size()
    bursts = _bake_firework_bursts(w, h, cx, cy)
    if ribbon_poly is not None:
        # Inflate the polygon slightly inward so the ray fade-out doesn't
        # graze the outline pixel. Approximate by shrinking around the
        # bounding box centroid — accurate enough for the chevron cut.
        cx_p = sum(x for x, _ in ribbon_poly) / len(ribbon_poly)
        cy_p = sum(y for _, y in ribbon_poly) / len(ribbon_poly)
        inflated = []
        for (px, py) in ribbon_poly:
            dx = px - cx_p
            dy = py - cy_p
            mag = math.hypot(dx, dy) or 1.0
            inflated.append((int(px + dx / mag * ribbon_inset),
                             int(py + dy / mag * ribbon_inset)))
        # Punch a transparent hole in the bursts layer at the ribbon shape.
        hole = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(hole, (255, 255, 255, 255), inflated)
        # BLEND_RGBA_SUB on the alpha channel zeros out the bursts under
        # the hole, leaving only the rays OUTSIDE the ribbon silhouette.
        bursts.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    surf.blit(bursts, (0, 0))


# ── Festoon garland (round-3 locked + Option-A filament) ───────────────────


def _catenary_y(x: float, x0: float, x1: float, y0: float, y1: float,
                sag: float) -> float:
    if x1 == x0:
        return y0
    t = (x - x0) / (x1 - x0)
    base = y0 + (y1 - y0) * t
    return base + 4.0 * sag * t * (1.0 - t)


def _draw_festoon_string(surf, x0: float, y0: float, x1: float, y1: float,
                         sag: float, n_bulbs: int = 8):
    """Round-4 lock-in: 8 bulbs is the canonical count for the in-game
    festoon. The round-3 hero secretly cheated to 14; this implementation
    uses whatever the caller passes — and every caller in this file now
    passes 8 (per critic fix #3).

    Filament: Option A — 1-px hot-yellow centre dot inside the bulb body
    so the bulb reads as LIT even when the warm halo blends into the
    lavender sky bottom. Replaces the round-3 scarlet bar."""
    pts = []
    x = x0
    while x <= x1:
        y = _catenary_y(x, x0, x1, y0, y1, sag)
        pts.append((x, y))
        x += 3.0
    pts.append((x1, y1))
    if len(pts) >= 2:
        pygame.draw.lines(surf, CATENARY, False,
                          [(int(px), int(py)) for px, py in pts], 1)

    for i in range(1, n_bulbs + 1):
        t = i / (n_bulbs + 1)
        bx = x0 + (x1 - x0) * t
        by = _catenary_y(bx, x0, x1, y0, y1, sag) + 3.0
        ibx, iby = int(bx), int(by)

        halo = pygame.Surface((22, 22), pygame.SRCALPHA)
        for ri, ai in ((10, 30), (8, 60), (6, 95)):
            pygame.draw.circle(halo, (*BULB_HALO, ai), (11, 11), ri)
        surf.blit(halo, (ibx - 11, iby - 11))

        pygame.draw.circle(surf, BULB_BODY, (ibx, iby), 4)
        pygame.draw.circle(surf, CATENARY,  (ibx, iby), 4, 1)

        # Round-4 Option A: 1-px hot-yellow centre dot (the lit core).
        pygame.draw.circle(surf, BULB_FILAMENT, (ibx, iby), 1)
        # Top-left specular pip stays — it sits diagonally off centre so
        # it doesn't fight the new central filament dot.
        pygame.draw.circle(surf, (255, 255, 255), (ibx - 2, iby - 2), 1)

        sy = _catenary_y(bx, x0, x1, y0, y1, sag)
        pygame.draw.line(surf, CATENARY,
                         (ibx, int(sy)), (ibx, iby - 4), 1)


# ── Confetti (round-4 NEW per critic fix #4) ───────────────────────────────


def _draw_confetti(surf, count: int, *, seed: int,
                   bounds_rect: pygame.Rect,
                   exclude_ellipse: tuple[int, int, int, int] | None = None):
    """Procedural confetti scatter — small rotated rectangles falling with
    a static motion-blur tail on a fraction of them.

    `bounds_rect`: where confetti is allowed to land.
    `exclude_ellipse`: (cx, cy, rx, ry) — a forbidden ellipse, used to
    keep flakes off the banner text glyphs and the chest pile."""
    rng = random.Random(seed)
    rect_w, rect_h = 3, 5
    for _ in range(count):
        # Re-roll position until it lands outside the exclusion ellipse —
        # cheap rejection sampling, ~5 retries worst-case for a half-area
        # exclusion. Bounded so a pathological seed can't hang the bake.
        for _try in range(8):
            cx = rng.randint(bounds_rect.x, bounds_rect.right)
            cy = rng.randint(bounds_rect.y, bounds_rect.bottom)
            if exclude_ellipse is None:
                break
            ex, ey, erx, ery = exclude_ellipse
            dx = (cx - ex) / max(1, erx)
            dy = (cy - ey) / max(1, ery)
            if dx * dx + dy * dy >= 1.0:
                break
        else:
            continue

        ang_deg = rng.uniform(0, 360)
        colour = rng.choice(CONFETTI_COLOURS)

        # Bake an oriented rect onto a small SRCALPHA surface, then
        # rotozoom + blit. Cheap and pixel-clean at 3×5.
        pad = 4
        sw = sh = rect_w + rect_h + pad * 2
        flake = pygame.Surface((sw, sh), pygame.SRCALPHA)
        pygame.draw.rect(
            flake, colour,
            (sw // 2 - rect_w // 2, sh // 2 - rect_h // 2, rect_w, rect_h),
        )
        rotated = pygame.transform.rotate(flake, ang_deg)
        surf.blit(rotated,
                  (cx - rotated.get_width() // 2,
                   cy - rotated.get_height() // 2))

        # Motion-blur ghost on ~1/4 of flakes: a 1-2 px tail biased upward
        # and slightly to the side, drawn at lower alpha. Sells gravity +
        # horizontal drift without animating.
        if rng.random() < 0.25:
            tail_len = rng.randint(1, 2)
            drift_x = rng.choice((-1, 0, 1))
            for step in range(1, tail_len + 1):
                ghost = rotated.copy()
                ghost.set_alpha(80 - step * 25)
                surf.blit(
                    ghost,
                    (cx - rotated.get_width() // 2 + drift_x * step,
                     cy - rotated.get_height() // 2 - step * 2),
                )


# ── Chest + coin pile (round-3 locked) ─────────────────────────────────────


def _draw_open_chest(surf, cx: int, cy: int, scale: float = 1.0):
    w = int(56 * scale)
    h = int(40 * scale)
    body = pygame.Rect(cx - w // 2, cy - h // 4, w, int(h * 0.75))

    pygame.draw.rect(surf, CHEST_WOOD, body)
    pygame.draw.rect(surf, CHEST_DARK, body, 2)
    for ty in (body.y + 5, body.bottom - 7):
        pygame.draw.rect(surf, CHEST_DARK, (body.x - 1, ty, body.w + 2, 3))
    lock = pygame.Rect(body.centerx - 5, body.y + body.h // 2 - 5, 10, 10)
    pygame.draw.rect(surf, CHEST_GOLD, lock)
    pygame.draw.rect(surf, CHEST_DARK, lock, 1)

    lid_h = int(h * 0.40)
    lid = [
        (body.x - 2,         body.y - 2),
        (body.right + 2,     body.y - 2),
        (body.right - 4,     body.y - lid_h),
        (body.x + 4,         body.y - lid_h - 2),
    ]
    pygame.draw.polygon(surf, CHEST_WOOD, lid)
    pygame.draw.polygon(surf, CHEST_DARK, lid, 2)
    pygame.draw.line(surf, CHEST_GOLD,
                     (body.x + 4, body.y - lid_h - 2),
                     (body.right - 4, body.y - lid_h), 1)

    coin_specs = [
        (cx - 18, cy + 6, 6),
        (cx -  6, cy + 9, 7),
        (cx +  8, cy + 7, 6),
        (cx + 20, cy + 4, 5),
        (cx - 12, cy + 2, 5),
        (cx +  2, cy - 1, 6),
        (cx + 14, cy - 2, 5),
        (cx -  2, cy + 14, 6),
        (cx + 10, cy + 13, 5),
        (cx - 16, cy + 13, 5),
    ]
    for (cxx, cyy, cr) in coin_specs:
        pygame.draw.circle(surf, COIN_GOLD, (cxx, cyy), cr)
        pygame.draw.circle(surf, COIN_RIM,  (cxx, cyy), cr, 1)
        pygame.draw.circle(surf, GOLD_HIGHLIGHT, (cxx, cyy), max(1, cr // 3))


# ── Twilight sky ───────────────────────────────────────────────────────────


def _twilight_bg(w: int, h: int) -> pygame.Surface:
    bg = pygame.Surface((w, h))
    for yy in range(h):
        t = yy / max(1, h - 1)
        col = (
            int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t),
            int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t),
            int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t),
        )
        pygame.draw.line(bg, col, (0, yy), (w, yy))
    return bg


# ── Single source of truth: REAL-geometry game canvas ──────────────────────
#
# This is the round-4 rebuild. Everything is drawn at the actual
# 360×640 game canvas with the real PIPE_W (58) and GROUND_Y (595).
# Two pillars at typical cycle-finale gap_y ≈ 325 / gap_h ≈ 170. The
# chest sits at gap_y of the chest pillar. The banner is screen-locked
# above the chest, the garland strings between the two pillar caps.
#
# The hero panel upscales THIS surface 3×. The 1× thumbnail in cell 5
# crops a vertical band out of it. Identical pixels, two viewing sizes
# — so what cell 5 shows IS what the player sees in-game.


def _draw_pillar_real(surf, x: int, gap_y: int, gap_h: int):
    """Draw one pillar pair at REAL game scale.

    `x` is the pillar's screen x (its left edge). `gap_y` is the gap's
    vertical centre; `gap_h` is the gap's height. The upper segment goes
    from y=0 down to `gap_y - gap_h/2`; the lower goes from
    `gap_y + gap_h/2` down to GROUND_Y. PIPE_W from config.

    Returns the cap-record tuple (cap_left_x, cap_right_x, cap_y) where
    the garland anchors — explicitly the BOTTOM of the upper segment so
    the festoon strings across the gap, not over the world ceiling."""
    w = PIPE_W
    top_bottom = gap_y - gap_h // 2
    bot_top    = gap_y + gap_h // 2

    # Upper segment.
    top_rect = pygame.Rect(x, 0, w, top_bottom)
    for yy in range(top_rect.h):
        t = yy / max(1, top_rect.h - 1)
        # Light-cap at the bottom edge (the gap-facing edge); dark body
        # gradient up the rest of the column. Faithful to the lit-edge
        # convention in pillar_variants.
        if t > 0.92:
            f = (1.0 - t) / 0.08
            col = tuple(int(PILLAR_LIGHT[k] + (PILLAR_BODY[k] - PILLAR_LIGHT[k]) * f)
                        for k in range(3))
        else:
            f = 1.0 - t / 0.92
            col = tuple(int(PILLAR_BODY[k] + (PILLAR_DARK[k] - PILLAR_BODY[k]) * f)
                        for k in range(3))
        pygame.draw.line(surf, col,
                         (top_rect.x, top_rect.y + yy),
                         (top_rect.right - 1, top_rect.y + yy))
    # Cap slab at the BOTTOM edge of the upper pillar (the lip the bird
    # flies under). +3 px overhang on each side per pillar_variants.
    cap_top = pygame.Rect(top_rect.x - 3, top_rect.bottom - 6, w + 6, 6)
    pygame.draw.rect(surf, PILLAR_LIGHT, cap_top)
    pygame.draw.rect(surf, PILLAR_DARK, cap_top, 1)
    pygame.draw.rect(surf, PILLAR_DARK, top_rect, 1)
    # Faint banding lines so the column reads as stacked sandstone.
    for band_t in (0.28, 0.52, 0.76):
        band_y = top_rect.y + int(top_rect.h * band_t)
        pygame.draw.line(surf, PILLAR_DARK,
                         (top_rect.x + 2, band_y),
                         (top_rect.right - 3, band_y), 1)

    # Lower segment.
    bot_rect = pygame.Rect(x, bot_top, w, GROUND_Y - bot_top)
    for yy in range(bot_rect.h):
        t = yy / max(1, bot_rect.h - 1)
        if t < 0.08:
            f = t / 0.08
            col = tuple(int(PILLAR_LIGHT[k] + (PILLAR_BODY[k] - PILLAR_LIGHT[k]) * f)
                        for k in range(3))
        else:
            f = (t - 0.08) / 0.92
            col = tuple(int(PILLAR_BODY[k] + (PILLAR_DARK[k] - PILLAR_BODY[k]) * f)
                        for k in range(3))
        pygame.draw.line(surf, col,
                         (bot_rect.x, bot_rect.y + yy),
                         (bot_rect.right - 1, bot_rect.y + yy))
    cap_bot = pygame.Rect(bot_rect.x - 3, bot_rect.y, w + 6, 6)
    pygame.draw.rect(surf, PILLAR_LIGHT, cap_bot)
    pygame.draw.rect(surf, PILLAR_DARK, cap_bot, 1)
    pygame.draw.rect(surf, PILLAR_DARK, bot_rect, 1)
    for band_t in (0.28, 0.52, 0.76):
        band_y = bot_rect.y + int(bot_rect.h * band_t)
        pygame.draw.line(surf, PILLAR_DARK,
                         (bot_rect.x + 2, band_y),
                         (bot_rect.right - 3, band_y), 1)

    # Garland anchor record: garland anchors at the BOTTOM of the upper
    # cap (i.e. cap_top.top edge centre approx; expose left/right of the
    # cap so callers can pick which side they're stringing from).
    return (cap_top.x, cap_top.right, cap_top.y)


def _render_real_canvas(*, chest_pillar_dx: int = 0,
                        include_confetti: bool = True) -> pygame.Surface:
    """The ground-truth render. 360×640 game canvas, real PIPE_W,
    real GROUND_Y, typical cycle-finale gap geometry.

    Layout: TWO pillars. The chest sits in the gap between the LEFT
    pillar (the chest pillar) and the RIGHT pillar (the next pillar
    after it). This matches world.py's chest spawn: `bx = pillar.x +
    PIPE_W + spacing*0.5` puts the chest in the inter-pillar gap, NOT
    on top of the chest pillar. The garland anchors at both pillar caps.

    `chest_pillar_dx`: world-space x-offset applied to BOTH pillars + the
    chest + the garland. Used by the motion-check cell to scroll the
    whole setup ~30 px left to prove the garland tracks world-space."""
    W, H = 360, 640
    canvas = _twilight_bg(W, H)

    # Pillar positions (canonical cycle-finale layout).
    # Two pillars spaced so the chest gap reads as a coin-rush-style
    # widened gap and the garland spans ~200 px (in-game cap-to-cap
    # distance during cycle-finale).
    chest_pillar_x = 110 + chest_pillar_dx       # LEFT pillar
    next_pillar_x  = 250 + chest_pillar_dx       # RIGHT pillar
    gap_y_chest    = 325
    gap_y_next     = 325                         # level for the hero
    gap_h          = 170

    # Draw pillars, capture cap records (left edge, right edge, top y).
    left_cap  = _draw_pillar_real(canvas, chest_pillar_x, gap_y_chest, gap_h)
    right_cap = _draw_pillar_real(canvas, next_pillar_x,  gap_y_next,  gap_h)

    # Chest in the inter-pillar gap. `bx` matches world.py spawn formula:
    # `pillar.x + PIPE_W + spacing*0.5`. With spacing ~140 between the
    # two pillars here, chest sits at the midpoint of the gap.
    spacing = next_pillar_x - chest_pillar_x
    chest_cx = int(chest_pillar_x + PIPE_W + (spacing - PIPE_W) // 2)
    chest_cy = gap_y_chest
    _draw_open_chest(canvas, chest_cx, chest_cy, scale=1.0)

    # Banner — SCREEN-LOCKED, centred horizontally above the chest. The
    # screen-lock is the in-game spec: even when the chest pillar scrolls
    # left, the banner stays at screen centre. So we anchor on canvas
    # centre x, NOT on chest_cx (which moves with chest_pillar_dx).
    banner = _build_banner_hires(day=7)
    banner_x = W // 2 - banner.get_width() // 2
    banner_y = 95                                # canonical banner band
    bw, bh = banner.get_width(), banner.get_height()

    # Fireworks behind the banner. Centre on the banner centre. Mask
    # against the ribbon silhouette so no ray crosses the chevron notch
    # (fix #6).
    ribbon_poly = _ribbon_screen_polygon(
        BANNER_W, BANNER_H, NOTCH,
        banner_x, banner_y,
    )
    _draw_firework_bursts_clipped(canvas,
                                  banner_x + bw // 2,
                                  banner_y + bh // 2,
                                  ribbon_poly)

    canvas.blit(banner, (banner_x, banner_y))

    # Garland — anchors at the BOTTOM of each upper pillar's cap. The
    # bottoms of the upper segments are gap_y - gap_h/2 ≈ 240 px from
    # the canvas top, which is exactly the y the brief's punch list
    # called out. Confirms the anchor is at the cap the bird flies under.
    a_lx = left_cap[1]              # right edge of LEFT pillar's cap
    a_ly = left_cap[2]
    a_rx = right_cap[0]             # left edge of RIGHT pillar's cap
    a_ry = right_cap[2]
    # Sag so the catenary mid drops cleanly below the banner. With the
    # banner sitting at y ≈ 95..175 and the anchors at y ≈ 240, the
    # natural string passes through y ≈ 240; we add a touch of sag so
    # the bulbs hang into the gap zone (where the chest celebration is
    # actually happening).
    sag = 36
    _draw_festoon_string(canvas, a_lx, a_ly, a_rx, a_ry,
                         sag=sag, n_bulbs=8)

    # Coin sparkles around the chest (sells the POP moment).
    rng = random.Random(7777)
    for _ in range(14):
        ang = rng.uniform(-math.pi + 0.4, -0.4)
        d = rng.uniform(28, 70)
        sx = chest_cx + math.cos(ang) * d
        sy = chest_cy + math.sin(ang) * d * 0.75
        cr = rng.choice((2, 3, 4))
        pygame.draw.circle(canvas, COIN_GOLD, (int(sx), int(sy)), cr)
        pygame.draw.circle(canvas, COIN_RIM,  (int(sx), int(sy)), cr, 1)

    # Confetti scatter across the upper half of the canvas, masked off
    # the ribbon body and the chest pile (fix #4). Confetti is
    # world-space — sits in the scene, not pinned to the banner. The
    # exclusion ellipse covers the banner glyph band.
    if include_confetti:
        confetti_bounds = pygame.Rect(0, 30, W, 280)
        # Exclude the ribbon body so flakes don't paint over text glyphs.
        exclude = (
            banner_x + bw // 2,
            banner_y + bh // 2,
            bw // 2 + 8,
            bh // 2 + 16,
        )
        _draw_confetti(canvas, count=16,
                       seed=4 + chest_pillar_dx,
                       bounds_rect=confetti_bounds,
                       exclude_ellipse=exclude)

    return canvas


# ── Cells ──────────────────────────────────────────────────────────────────


def _render_hero_cell(w: int, h: int,
                      *, chest_pillar_dx: int = 0,
                      include_confetti: bool = True) -> pygame.Surface:
    """Cell 1 — hero. UNIFORM upscale of a celebration-band crop from
    the real 360×640 canvas. Source crop is sized so that a uniform
    horizontal scale to the cell width also fills the cell height —
    no aspect-distortion stretching that would lie about the design.

    What you see IS what ships, just larger."""
    canvas = _render_real_canvas(chest_pillar_dx=chest_pillar_dx,
                                 include_confetti=include_confetti)

    # Uniform scale factor — pin to the cell width so the band fills
    # the panel horizontally.
    scale = w / 360.0
    band_h_px = int(round(h / scale))
    # Crop band: anchored at the TOP of the banner (y ≈ 75) so the full
    # banner + garland + chest + coin pile + a thin ground hint are
    # visible. With HERO_H sized so band_h_px ≈ 192-200 we cover
    # y=75..275 of the canvas — which lands just short of the chest
    # bottom; HERO_H is intentionally tall enough that the band can run
    # banner-top to chest-bottom in a single uniform scale.
    band_top = 75
    src_band = pygame.Rect(0, band_top, 360, band_h_px)
    if src_band.bottom > 640:
        src_band.height = 640 - src_band.y

    band = pygame.Surface((src_band.w, src_band.h))
    band.blit(canvas, (0, 0), src_band)
    # Uniform scale — no distortion.
    scaled_h = int(round(src_band.h * scale))
    hero_render = pygame.transform.smoothscale(band, (w, scaled_h))

    # Compose onto a cell-sized surface (centred vertically if scaled_h
    # < h; cropped if greater — but the band size was chosen so it
    # matches within ±1 px).
    hero = pygame.Surface((w, h))
    hero.fill((22, 18, 30))
    y_off = (h - scaled_h) // 2
    hero.blit(hero_render, (0, y_off))
    pygame.draw.rect(hero, (24, 20, 28), (0, 0, w, h), 1)
    return hero


def _render_banner_zoom_cell(w: int, h: int) -> pygame.Surface:
    """Cell 2 — banner zoom with the polished firework treatment. Ray
    clip applied (fix #6) so no ray crosses the ribbon notch."""
    cell = _twilight_bg(w, h)
    cx = w // 2
    cy = h // 2 + 4

    banner = _build_banner_hires(day=7)
    bz_scale = 1.25
    bw = int(banner.get_width() * bz_scale)
    bh = int(banner.get_height() * bz_scale)
    banner_zoom = pygame.transform.smoothscale(banner, (bw, bh))
    banner_x = (w - bw) // 2
    banner_y = cy - bh // 2

    # Build the zoomed ribbon polygon at the same scale + position.
    ribbon_poly = []
    base = _ribbon_polygon(BANNER_W, BANNER_H, NOTCH)
    for (rx, ry) in base:
        ribbon_poly.append((int(rx * bz_scale + banner_x),
                            int(ry * bz_scale + banner_y)))

    _draw_firework_bursts_clipped(cell, cx, cy, ribbon_poly)
    cell.blit(banner_zoom, (banner_x, banner_y))

    pygame.draw.rect(cell, (24, 20, 28), (0, 0, w, h), 1)
    return cell


def _render_garland_zoom_cell(w: int, h: int) -> pygame.Surface:
    """Cell 3 — garland zoom with hot-yellow filament cores (Option A)."""
    cell = _twilight_bg(w, h)

    pillar_w = 44
    pillar_h = h - 50
    pillar_y_top = 40
    px_left  = 60
    px_right = w - 60 - pillar_w
    for px in (px_left, px_right):
        rect = pygame.Rect(px, pillar_y_top, pillar_w, pillar_h)
        for yy in range(rect.h):
            t = yy / max(1, rect.h - 1)
            col = tuple(int(PILLAR_BODY[k] + (PILLAR_DARK[k] - PILLAR_BODY[k]) * t)
                        for k in range(3))
            pygame.draw.line(cell, col,
                             (rect.x, rect.y + yy),
                             (rect.right - 1, rect.y + yy))
        cap = pygame.Rect(rect.x - 4, rect.y, rect.w + 8, 10)
        pygame.draw.rect(cell, PILLAR_LIGHT, cap)
        pygame.draw.rect(cell, PILLAR_DARK, cap, 2)
        pygame.draw.rect(cell, PILLAR_DARK, rect, 2)

    a_lx = px_left + pillar_w + 4
    a_rx = px_right - 4
    a_y  = pillar_y_top + 6
    span = a_rx - a_lx
    _draw_festoon_string(cell, a_lx, a_y, a_rx, a_y,
                         sag=max(40, int(span * 0.20)), n_bulbs=8)

    cap_font = _font(11, bold=True)
    cap = cap_font.render(
        "8 bulbs  /  hot-yellow filament core (Option A)  /  catenary thread",
        True, STAR_CREAM,
    )
    cap.set_alpha(220)
    cell.blit(cap, ((w - cap.get_width()) // 2, h - 22))

    pygame.draw.rect(cell, (24, 20, 28), (0, 0, w, h), 1)
    return cell


def _render_asymmetric_cell(w: int, h: int) -> pygame.Surface:
    """Cell 4 — kept from round 3."""
    cell = _twilight_bg(w, h)

    pillar_w = 44
    left_cap_y  = 30
    left_h      = h - 50 - 60
    right_cap_y = 130
    right_h     = h - 50 - 130

    px_left  = 60
    px_right = w - 60 - pillar_w

    for px, py, ph in ((px_left, left_cap_y, left_h),
                       (px_right, right_cap_y, right_h)):
        rect = pygame.Rect(px, py, pillar_w, ph)
        for yy in range(rect.h):
            t = yy / max(1, rect.h - 1)
            col = tuple(int(PILLAR_BODY[k] + (PILLAR_DARK[k] - PILLAR_BODY[k]) * t)
                        for k in range(3))
            pygame.draw.line(cell, col,
                             (rect.x, rect.y + yy),
                             (rect.right - 1, rect.y + yy))
        cap = pygame.Rect(rect.x - 4, rect.y, rect.w + 8, 10)
        pygame.draw.rect(cell, PILLAR_LIGHT, cap)
        pygame.draw.rect(cell, PILLAR_DARK, cap, 2)
        pygame.draw.rect(cell, PILLAR_DARK, rect, 2)

    a_lx = px_left + pillar_w + 4
    a_ly = left_cap_y + 6
    a_rx = px_right - 4
    a_ry = right_cap_y + 6
    span = a_rx - a_lx
    _draw_festoon_string(cell, a_lx, a_ly, a_rx, a_ry,
                         sag=max(40, int(span * 0.20)), n_bulbs=8)

    cap_font = _font(11, bold=True)
    cap = cap_font.render(
        "asymmetric anchors  delta ~= 100 px  — catenary tilts cleanly",
        True, STAR_CREAM,
    )
    cap.set_alpha(220)
    cell.blit(cap, ((w - cap.get_width()) // 2, h - 22))

    pygame.draw.rect(cell, (24, 20, 28), (0, 0, w, h), 1)
    return cell


def _render_thumbnail_cell(w: int, h: int) -> pygame.Surface:
    """Cell 5 — TRUE 1× thumbnail at 360 × 200 px, lifted directly from
    the same real-geometry render the hero uses. If the banner collides
    with the upper pipe at typical gap_h, we'll see it HERE."""
    cell = _twilight_bg(w, h)
    canvas = _render_real_canvas(chest_pillar_dx=0)

    # 1× crop band — 360 × 200 covering the banner + chest + gap zone.
    # The crop starts a touch above the banner so banner top has air,
    # and ends right at the bottom of the chest pile.
    crop_y0 = 60
    crop_h  = 200
    thumb = pygame.Surface((360, crop_h))
    thumb.blit(canvas, (0, 0), pygame.Rect(0, crop_y0, 360, crop_h))

    # Centre the 360-wide thumbnail in the cell (no scaling — TRUE 1×).
    cell.blit(thumb, ((w - 360) // 2, (h - crop_h) // 2 - 8))

    cap_font = _font(11, bold=True)
    cap = cap_font.render(
        "TRUE 1x — 360 x 200 px crop from the SAME real-geometry render as the hero",
        True, STAR_CREAM,
    )
    cap.set_alpha(220)
    cell.blit(cap, ((w - cap.get_width()) // 2, h - 18))

    pygame.draw.rect(cell, (24, 20, 28), (0, 0, w, h), 1)
    return cell


def _render_motion_check_cell(w: int, h: int) -> pygame.Surface:
    """Cell 6 — motion check (per critic's optional fix #7). Chest pillar
    scrolled ~30 px LEFT of its hero position; banner stays screen-locked
    centred; garland tracks world-space and shifts with the pillars."""
    cell = _twilight_bg(w, h)
    canvas = _render_real_canvas(chest_pillar_dx=-30)

    crop_y0 = 60
    crop_h  = 200
    thumb = pygame.Surface((360, crop_h))
    thumb.blit(canvas, (0, 0), pygame.Rect(0, crop_y0, 360, crop_h))

    cell.blit(thumb, ((w - 360) // 2, (h - crop_h) // 2 - 8))

    cap_font = _font(11, bold=True)
    cap = cap_font.render(
        "MOTION CHECK — chest pillar scrolled 30 px LEFT; banner screen-locked, garland tracks world",
        True, STAR_CREAM,
    )
    cap.set_alpha(220)
    cell.blit(cap, ((w - cap.get_width()) // 2, h - 18))

    pygame.draw.rect(cell, (24, 20, 28), (0, 0, w, h), 1)
    return cell


# ── Sheet layout ───────────────────────────────────────────────────────────


CELL_W   = 520
CELL_H   = 220
HERO_W   = CELL_W * 2 + 8
# Uniform 360->1048 scale = ~2.91x. HERO_H sized so the source crop
# (y=75..y=355) covers the FULL celebration band — banner above, garland
# strung across cap-bottoms at y~240, chest at gap_y=325, coin pile to
# y~355. 280 source px × 2.91 scale = ~815 cell px → HERO_H=820 leaves
# a 5-px breathing strip top + bottom. No aspect distortion — the
# upscale lies about nothing.
HERO_H   = 820
TITLE_H  = 40
PAD      = 8


def render_sheet() -> pygame.Surface:
    sheet_w = 2 * CELL_W + 3 * PAD
    # 3 sub-rows (hero, then 2×2 = 2 rows, plus motion check 3rd row).
    sheet_h = TITLE_H + HERO_H + 3 * CELL_H + 5 * PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 18, 30))

    title_font = _font(18, bold=True)
    title = title_font.render(
        "TREASURE BOX  cycle-finale reveal — Round 4   V3 fireworks + V4 garland + confetti (real geometry)",
        True, STAR_CREAM,
    )
    sheet.blit(title, (PAD + 8, (TITLE_H - title.get_height()) // 2 + 2))

    label_font = _font(14, bold=True)

    def _label(cell, text):
        s = label_font.render(text, True, (0, 0, 0))
        s.set_alpha(160)
        t = label_font.render(text, True, STAR_CREAM)
        t.set_alpha(220)
        cell.blit(s, (11, 11))
        cell.blit(t, (10, 10))

    # Hero cell — real geometry, upscaled 3×.
    hero = _render_hero_cell(HERO_W, HERO_H, chest_pillar_dx=0)
    _label(hero, "HERO  upscaled 3x from the SAME real-geometry render as cell 5")
    sheet.blit(hero, (PAD, TITLE_H + PAD))

    # Detail row 1: banner zoom + garland zoom.
    bz = _render_banner_zoom_cell(CELL_W, CELL_H)
    gz = _render_garland_zoom_cell(CELL_W, CELL_H)
    _label(bz, "Cell 2  banner zoom  V3 firework + ribbon ray-clip")
    _label(gz, "Cell 3  garland zoom  8 bulbs + hot-yellow filament core (A)")

    # Detail row 2: asymmetric + 1x thumbnail.
    az = _render_asymmetric_cell(CELL_W, CELL_H)
    tz = _render_thumbnail_cell(CELL_W, CELL_H)
    _label(az, "Cell 4  asymmetric pillar heights")
    _label(tz, "Cell 5  TRUE 1x thumbnail  (REAL game geometry)")

    # Detail row 3: motion check (full width — let it breathe).
    mc = _render_motion_check_cell(CELL_W * 2 + PAD, CELL_H)
    _label(mc, "Cell 6  motion check  garland tracks world, banner screen-locked")

    row1_y = TITLE_H + HERO_H + 2 * PAD
    row2_y = row1_y + CELL_H + PAD
    row3_y = row2_y + CELL_H + PAD
    sheet.blit(bz, (PAD,                   row1_y))
    sheet.blit(gz, (PAD + CELL_W + PAD,    row1_y))
    sheet.blit(az, (PAD,                   row2_y))
    sheet.blit(tz, (PAD + CELL_W + PAD,    row2_y))
    sheet.blit(mc, (PAD,                   row3_y))

    return sheet


def main():
    sheet = render_sheet()
    out_dir = os.path.join(os.path.dirname(THIS_DIR), "docs", "treasure_box")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "banner_designs.png")
    pygame.image.save(sheet, out_path)
    print(f"wrote {out_path}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
