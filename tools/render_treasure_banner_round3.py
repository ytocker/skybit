"""Treasure Box cycle-finale reveal — Round 3 exploration sheet.

Round 2 narrowed the field to V3 (firework banner) + V4 (festoon garland).
The user picked a HYBRID: V3 banner overhead, V4 garland strung between the
two pillars flanking the chest pillar — so the festoon physically drapes
over the gap the player just flew through.

This script bakes a 3 × 2 grid (cell-1 = full-width hero spanning the top
two cells) on top of a 40-px title strip:

  ┌────────────── Cell 1 (HERO, 2-wide) ──────────────┐
  │  twilight sky, 2 flanking pillars, open chest +    │
  │  coin pile, V3 firework banner, V4 garland strung  │
  │  between pillar tops                               │
  ├──────────────────────────┬─────────────────────────┤
  │ Cell 2  banner zoom       │ Cell 3  garland zoom    │
  │ V3 firework motif         │ 8 bulbs + catenary +    │
  │ polished per round-2 crit │ scarlet filaments       │
  ├──────────────────────────┼─────────────────────────┤
  │ Cell 4  garland under     │ Cell 5  1× in-game-     │
  │ asymmetric pillar heights │ scale thumbnail of hero │
  └──────────────────────────┴─────────────────────────┘

Re-runnable; doc-only — never bundled into the WASM/desktop builds.

Output: docs/treasure_box/banner_designs.png (overwrites Round 2)."""
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

# ── Locked palette — round-2 critic notes finalised these ──────────────────

GOLD_HIGHLIGHT = (255, 244, 188)
GOLD_HOT       = (255, 220, 110)
GOLD_SAT       = (240, 188,  56)
GOLD_AMBER     = (196, 132,  28)
GOLD_INK       = ( 72,  48,  12)
VELVET         = (168,  32,  16)
VELVET_HI      = (220,  64,  32)
STAR_CREAM     = (252, 244, 218)

# V3 firework warm-accent trio — cyan dropped per critique; hot ORANGE
# chosen over magenta because the lavender sky bottom would shove magenta
# back toward chroma-clash territory the round-2 cyan suffered from,
# whereas orange stays inside the warm dawn family the banner already
# inhabits.
FIRE_RED       = (248,  96,  88)
FIRE_GOLD      = (255, 220, 110)
FIRE_ORANGE    = (255, 128,  48)

# Festoon bulb spec — warm-white body, scarlet filament so each dot reads
# as an actual lit bulb instead of a glow blob.
BULB_BODY      = (255, 240, 200)
BULB_FILAMENT  = (220,  64,  32)
BULB_HALO      = (255, 220, 110)         # additive amber halo
CATENARY       = ( 48,  32,  12)

# Twilight sky — cycle-finale phase (matches game/biome.py at finale window).
SKY_TOP = (255, 168,  96)
SKY_BOT = (168, 132, 188)

# Pillar sandstone (silhouette only — the hero cell sketches the pillar
# vocabulary in dark gold so the real `pillar_variants.py` look is felt
# without re-exporting its body texture).
PILLAR_BODY    = (118,  78,  36)
PILLAR_DARK    = ( 64,  40,  18)
PILLAR_LIGHT   = (160, 108,  48)

CHEST_WOOD     = (132,  72,  28)
CHEST_DARK     = ( 60,  32,  10)
CHEST_GOLD     = (244, 188,  56)
COIN_GOLD      = (255, 208,  72)
COIN_RIM       = (152,  92,  16)

# Banner silhouette — round-2 dims, supersampled 2× then smoothscale.
BANNER_W = 340
BANNER_H = 78
NOTCH    = 20
OUTLINE  = 3
SHADOW_DX = 4
SHADOW_DY = 5
SS = 2


# ── Banner construction (round-2 locked + critic-note tweaks) ──────────────


def _ribbon_polygon(bw: int, bh: int, notch: int) -> list[tuple[int, int]]:
    """Notched forked-end ribbon — chevron cuts on left + right."""
    return [
        (0, 0), (bw, 0),
        (bw - notch, bh // 2),
        (bw, bh), (0, bh),
        (notch, bh // 2),
    ]


def _multi_stop_gradient(bw: int, bh: int) -> pygame.Surface:
    """4-stop vertical gold gradient. Highlight reads as a thin specular
    at top, amber undertow at the bottom of the fold."""
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

    Critic-note diffs vs. round 2:
      * Bevel highlight alpha: 110 → 78 (≈70% of round 2's 110)
      * Embossed text drops: from max(1, SS) px → exactly 1 px (per critic
        "reduce 2 px → 1 px"); the round-2 build was already 1 px in
        canonical space but SS-scaled to 2 px in the bake, which is what
        the critic was seeing as too hot; we lock it to a single bake-px."""
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

    # Drop shadow.
    shadow_pts = [(x + sdx, y + sdy) for (x, y) in ribbon]
    pygame.draw.polygon(comp, (0, 0, 0, 170), shadow_pts)

    # Body + 4-stop gold mask.
    body = _multi_stop_gradient(bw, bh)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), ribbon)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    comp.blit(body, (0, 0))

    # Red velvet bottom rim — chevron-cut by the mask.
    rim_h = 8 * SS
    rim = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(rim, VELVET, (0, bh - rim_h, bw, rim_h))
    pygame.draw.line(rim, VELVET_HI, (0, bh - rim_h),
                     (bw, bh - rim_h), max(1, SS))
    rim.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    comp.blit(rim, (0, 0))

    # Embossed bevel INSIDE the dark outline — round-2 critic asked for
    # 70% of the previous highlight intensity (110 → ~78).
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

    # Dark outline.
    pygame.draw.polygon(comp, GOLD_INK, ribbon, outline)

    # Four cream "+" sparkles at the inner corners.
    for (sx, sy) in (
        (notch + 14 * SS,         14 * SS),
        (bw - notch - 14 * SS,    14 * SS),
        (notch + 14 * SS,         bh - 14 * SS),
        (bw - notch - 14 * SS,    bh - 14 * SS),
    ):
        pygame.draw.circle(comp, STAR_CREAM, (sx, sy), 3 * SS)
        pygame.draw.circle(comp, (255, 255, 255),
                           (sx - SS, sy - SS), max(1, SS))

    # Embossed text — 1 bake-px drop on each side (per critic).
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

    # Outline for legibility on gold body.
    o = max(2, 2 * SS)
    for ox, oy in ((-o, 0), (o, 0), (0, -o), (0, o),
                   (-o, -o), (o, -o), (-o, o), (o, o)):
        comp.blit(out_render, (tx + ox, ty + oy))
    # Embossed drops — exactly 1 bake-px per critic.
    comp.blit(text_white, (tx, ty - 1))
    comp.blit(text_dark,  (tx, ty + 1))
    comp.blit(text_cream, (tx, ty))

    final_w = BANNER_W + SHADOW_DX
    final_h = BANNER_H + SHADOW_DY
    return pygame.transform.smoothscale(comp, (final_w, final_h))


# ── Firework motif (V3, polished per critic notes) ─────────────────────────


def _draw_glow_disc(surf, cx, cy, radius, color, alpha):
    """Soft glow disc — concentric circles with cubic alpha falloff. Plain
    alpha so the halo reads as warm haze on the twilight bg rather than a
    blown-out white disc."""
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
    """A single firework burst — alternating long/short rays + sparkle pips.
    `opacity` lets demoted outer bursts fade to 40% per critic note while
    keeping their geometry identical to the dominant centre burst (family
    coherence)."""
    rays = 16
    r_long  = int(70 * scale)
    r_short = int(r_long * 0.55)
    long_half  = max(1, int(r_long * 0.085))
    short_half = max(1, int(r_long * 0.06))

    # If demoted, draw onto a temp surface so we can apply a single alpha
    # pass without re-coloring every primitive.
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

    # Sparkle pips past each tip + scattered along the rays. Seeded by
    # centre coords so the sheet reproduces across runs.
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
        sy = oy + math.sin(ang) * d
        pygame.draw.circle(target, STAR_CREAM, (int(sx), int(sy)), 1)

    if opacity < 255:
        layer.set_alpha(opacity)
        surf.blit(layer, (cx - pad, cy - pad))


def _draw_firework_bursts(surf, cx, cy):
    """V3 polished per critic:
      * Centre gold burst dominant @ 1.6× scale.
      * Outer bursts demoted to 40% opacity background sparks.
      * Red kept; cyan REPLACED by hot orange to stay in the warm family.
      * No centred vertical element so nothing splits the banner."""
    # Outer demoted bursts FIRST so their wisps duck under the centre burst.
    _draw_glow_disc(surf, cx - 165, cy - 58, 70, FIRE_RED, 50)
    _draw_starburst(surf, cx - 165, cy - 58, FIRE_RED,
                    scale=0.78, opacity=102)
    _draw_glow_disc(surf, cx + 165, cy - 58, 70, FIRE_ORANGE, 50)
    _draw_starburst(surf, cx + 165, cy - 58, FIRE_ORANGE,
                    scale=0.78, opacity=102)

    # Dominant centre gold burst — 1.6× scale, full opacity, fat warm halo.
    _draw_glow_disc(surf, cx, cy, 170, FIRE_GOLD, 95)
    _draw_starburst(surf, cx, cy, FIRE_GOLD, scale=1.6, opacity=255)


# ── World-space festoon garland ────────────────────────────────────────────


def _catenary_y(x: float, x0: float, x1: float, y0: float, y1: float,
                sag: float) -> float:
    """Parabolic approximation of a hanging string between two anchors.

    True catenaries cosh-out which is overkill at 200 px spans; a tilted
    parabola is visually indistinguishable and 10× cheaper. The tilt
    handles asymmetric anchor heights (cell 4 covers this case).
    `sag` is the midpoint drop from the straight line in px."""
    if x1 == x0:
        return y0
    t = (x - x0) / (x1 - x0)
    base = y0 + (y1 - y0) * t
    return base + 4.0 * sag * t * (1.0 - t)


def _draw_festoon_string(surf, x0: float, y0: float, x1: float, y1: float,
                         sag: float, n_bulbs: int = 8):
    """One festoon — dark catenary thread + n warm-white bulbs with soft
    halos + scarlet filaments. Anchors at (x0,y0) → (x1,y1).

    Polish chosen per critic:
      * NO pennant flags (their triangular silhouette duplicated the
        ribbon's chevron notch — visual stutter).
      * 1-px dark catenary in INK (48,32,12), not the cooler thread-dark
        used in round 2 — keeps it inside the warm family.
      * Each bulb gets a tiny 1-px scarlet filament so they read as LIT
        bulbs at close range, not glow blobs."""
    # Catenary string — sample every 3 px for a smooth curve.
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

    # Bulbs distributed evenly along the string (in x parameter, NOT arc
    # length — close enough for an 8-bulb spread and avoids a slow numeric
    # integration on every render). Skipping the exact endpoints so the
    # bulbs sit on the string proper, not on the anchor knots.
    for i in range(1, n_bulbs + 1):
        t = i / (n_bulbs + 1)
        bx = x0 + (x1 - x0) * t
        by = _catenary_y(bx, x0, x1, y0, y1, sag) + 3.0
        ibx, iby = int(bx), int(by)

        # Plain-alpha halo — additive would bleach the lavender sky bottom
        # into white at finale time. Layered radii give a soft edge.
        halo = pygame.Surface((22, 22), pygame.SRCALPHA)
        for ri, ai in ((10, 30), (8, 60), (6, 95)):
            pygame.draw.circle(halo, (*BULB_HALO, ai), (11, 11), ri)
        surf.blit(halo, (ibx - 11, iby - 11))

        # Bulb body — warm-white disc with a dark ink rim so it reads
        # silhouette-first against bright sky bands.
        pygame.draw.circle(surf, BULB_BODY, (ibx, iby), 4)
        pygame.draw.circle(surf, CATENARY,  (ibx, iby), 4, 1)

        # Scarlet filament — single bake-px inside the bulb, the detail
        # that converts a generic glow dot into a believable Edison bulb.
        pygame.draw.line(surf, BULB_FILAMENT,
                         (ibx - 1, iby), (ibx + 1, iby), 1)
        # Top-left specular pip — keeps the bulb from feeling matte.
        pygame.draw.circle(surf, (255, 255, 255), (ibx - 1, iby - 1), 1)

        # Tiny socket cap — a 2-px dark dash where the bulb meets the
        # string, sells the "hanging from" attachment.
        sy = _catenary_y(bx, x0, x1, y0, y1, sag)
        pygame.draw.line(surf, CATENARY,
                         (ibx, int(sy)), (ibx, iby - 4), 1)


# ── Pillar + chest silhouettes for the hero shot ───────────────────────────


def _draw_pillar(surf, x: int, gap_y: int, gap_h: int, surface_h: int,
                 *, top_h_extend: int = 280, bot_h_extend: int = 280):
    """Sandstone pillar silhouette — top + bottom sections framing the
    flight gap. This is a faithful stand-in for `pillar_variants` styling
    (capped top, faint horizontal banding, lit edge) baked at hero scale.

    Returns the (top_post_x_left, top_post_x_right, top_post_y) so the
    garland anchor coords are derived from the same geometry the player
    sees — no separate hard-coded numbers to drift."""
    w = 58                                # matches PIPE_W in config.py
    top_bottom = gap_y - gap_h // 2
    bot_top    = gap_y + gap_h // 2

    # ── Bottom pillar ──
    bot_rect = pygame.Rect(x, bot_top, w, surface_h - bot_top)
    # Body gradient (dark base → mid → light shoulder).
    for yy in range(bot_rect.h):
        t = yy / max(1, bot_rect.h - 1)
        # Cap = lighter shoulder fading into the dark base.
        if t < 0.10:
            f = t / 0.10
            col = tuple(int(PILLAR_LIGHT[i] + (PILLAR_BODY[i] - PILLAR_LIGHT[i]) * f)
                        for i in range(3))
        else:
            f = (t - 0.10) / 0.90
            col = tuple(int(PILLAR_BODY[i] + (PILLAR_DARK[i] - PILLAR_BODY[i]) * f)
                        for i in range(3))
        pygame.draw.line(surf, col,
                         (bot_rect.x, bot_rect.y + yy),
                         (bot_rect.right - 1, bot_rect.y + yy))
    # Cap slab — slightly wider lip at the top.
    cap = pygame.Rect(bot_rect.x - 3, bot_rect.y, w + 6, 8)
    pygame.draw.rect(surf, PILLAR_LIGHT, cap)
    pygame.draw.rect(surf, PILLAR_DARK, cap, 1)
    # Body outline.
    pygame.draw.rect(surf, PILLAR_DARK, bot_rect, 1)
    # 3 faint horizontal banding lines — reads as stacked sandstone.
    for band_t in (0.30, 0.55, 0.78):
        band_y = bot_rect.y + int(bot_rect.h * band_t)
        pygame.draw.line(surf, PILLAR_DARK,
                         (bot_rect.x + 2, band_y),
                         (bot_rect.right - 3, band_y), 1)

    # ── Top pillar ──
    top_rect = pygame.Rect(x, 0, w, top_bottom)
    for yy in range(top_rect.h):
        t = yy / max(1, top_rect.h - 1)
        # Cap = lighter shoulder near the GAP edge (bottom of top pillar)
        if t > 0.90:
            f = (1.0 - t) / 0.10
            col = tuple(int(PILLAR_LIGHT[i] + (PILLAR_BODY[i] - PILLAR_LIGHT[i]) * f)
                        for i in range(3))
        else:
            f = 1.0 - t / 0.90
            col = tuple(int(PILLAR_BODY[i] + (PILLAR_DARK[i] - PILLAR_BODY[i]) * f)
                        for i in range(3))
        pygame.draw.line(surf, col,
                         (top_rect.x, top_rect.y + yy),
                         (top_rect.right - 1, top_rect.y + yy))
    # Cap slab at BOTTOM edge of top pillar — wider lip facing the gap.
    cap = pygame.Rect(top_rect.x - 3, top_rect.bottom - 8, w + 6, 8)
    pygame.draw.rect(surf, PILLAR_LIGHT, cap)
    pygame.draw.rect(surf, PILLAR_DARK, cap, 1)
    pygame.draw.rect(surf, PILLAR_DARK, top_rect, 1)
    for band_t in (0.22, 0.45, 0.70):
        band_y = top_rect.y + int(top_rect.h * band_t)
        pygame.draw.line(surf, PILLAR_DARK,
                         (top_rect.x + 2, band_y),
                         (top_rect.right - 3, band_y), 1)

    # Garland anchor = TOP-pillar's BOTTOM-edge corners (cap top edge).
    # The brief specifies "the natural post-top the player perceives as
    # the pillar tops above the flight gap" — that's the cap slab the
    # bird flies under.
    anchor_left  = top_rect.x - 3
    anchor_right = top_rect.right + 3
    anchor_y     = top_rect.bottom - 8
    return anchor_left, anchor_right, anchor_y


def _draw_open_chest(surf, cx: int, cy: int, scale: float = 1.0):
    """Open chest mid-pile of coins — hero-cell shorthand for the
    `treasure_box.draw_open_sprite` look. Doesn't import that module so
    the doc tool stays self-contained against future treasure_box
    rewrites."""
    w = int(56 * scale)
    h = int(40 * scale)
    body = pygame.Rect(cx - w // 2, cy - h // 4, w, int(h * 0.75))

    # Chest body (front face) with banded sides.
    pygame.draw.rect(surf, CHEST_WOOD, body)
    pygame.draw.rect(surf, CHEST_DARK, body, 2)
    # Two horizontal iron straps.
    for ty in (body.y + 5, body.bottom - 7):
        pygame.draw.rect(surf, CHEST_DARK, (body.x - 1, ty, body.w + 2, 3))
    # Central lock plate.
    lock = pygame.Rect(body.centerx - 5, body.y + body.h // 2 - 5, 10, 10)
    pygame.draw.rect(surf, CHEST_GOLD, lock)
    pygame.draw.rect(surf, CHEST_DARK, lock, 1)

    # Open lid — tipped back, suggested with a tilted trapezoid sitting
    # above the body.
    lid_h = int(h * 0.40)
    lid = [
        (body.x - 2,         body.y - 2),
        (body.right + 2,     body.y - 2),
        (body.right - 4,     body.y - lid_h),
        (body.x + 4,         body.y - lid_h - 2),
    ]
    pygame.draw.polygon(surf, CHEST_WOOD, lid)
    pygame.draw.polygon(surf, CHEST_DARK, lid, 2)
    # Lid inner-rim highlight — thin gold line along the open edge.
    pygame.draw.line(surf, CHEST_GOLD,
                     (body.x + 4, body.y - lid_h - 2),
                     (body.right - 4, body.y - lid_h), 1)

    # Coin pile spilling over the front edge — overlapping discs.
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
        # Tiny "$" hint — one bright dot in the centre.
        pygame.draw.circle(surf, GOLD_HIGHLIGHT, (cxx, cyy), max(1, cr // 3))


# ── Twilight sky background ────────────────────────────────────────────────


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


# ── Hero scene (used at full scale in cell 1, then downscaled for cell 5) ──


def _render_hero_scene(canvas_w: int, canvas_h: int,
                       *, gap_y_offsets=(0, 0, 0),
                       day: int = 7) -> pygame.Surface:
    """Compose the cycle-finale moment as the player sees it.

    `gap_y_offsets` is (left_pillar, chest_pillar, right_pillar) offset
    from the centerline gap_y. Cell 1 uses zeros for the canonical look;
    cell 4 uses an asymmetric (+50, 0, -50) split to stress-test that the
    catenary still drapes correctly across mismatched anchor heights.

    Renders at hero scale (3× the actual 360 px canvas width)."""
    surf = _twilight_bg(canvas_w, canvas_h)

    # Layout — 3 pillars across the width, gap at mid-height. The chest
    # pillar is the centre one; the garland strings between the LEFT
    # and RIGHT flanking pillars.
    pipe_w_hero = 58 * 3                  # 3× hero scale of PIPE_W
    spacing = canvas_w // 3
    centers = [spacing * 0.5, spacing * 1.5, spacing * 2.5]
    base_gap_y = canvas_h // 2
    base_gap_h = 220                      # generous coin-rush hero gap

    # Pillar geometry — record anchor points for the garland.
    anchors = []
    for i, ccx in enumerate(centers):
        px_left = int(ccx - pipe_w_hero // 2)
        gap_y = base_gap_y + gap_y_offsets[i]
        # Hero-scale pillars need a proportionally fatter look — _draw_pillar
        # assumes the canonical 58 px width so scale a sub-surface.
        sub_w = pipe_w_hero
        sub_h = canvas_h
        sub = pygame.Surface((sub_w + 8, sub_h), pygame.SRCALPHA)
        a_l, a_r, a_y = _draw_pillar(
            sub, 4,                       # +4 leaves room for the cap lip
            gap_y, base_gap_h, sub_h,
        )
        # Scale UP by 3× horizontally to match hero proportions? No — the
        # _draw_pillar above already used w=58 in its body; we want hero
        # scale so do it differently: re-render with explicit hero width.
        # Simpler: redraw the pillar directly at hero scale inline.
        # (Discarding the sub_surface; using it only for the anchor calc
        # would be wasted work.)

        # Hero-scale pillar — duplicate body draw inline at the wider w.
        w = pipe_w_hero
        top_bottom = gap_y - base_gap_h // 2
        bot_top    = gap_y + base_gap_h // 2

        # Bottom pillar.
        bot_rect = pygame.Rect(px_left, bot_top, w, canvas_h - bot_top)
        for yy in range(bot_rect.h):
            t = yy / max(1, bot_rect.h - 1)
            if t < 0.06:
                f = t / 0.06
                col = tuple(int(PILLAR_LIGHT[k] + (PILLAR_BODY[k] - PILLAR_LIGHT[k]) * f)
                            for k in range(3))
            else:
                f = (t - 0.06) / 0.94
                col = tuple(int(PILLAR_BODY[k] + (PILLAR_DARK[k] - PILLAR_BODY[k]) * f)
                            for k in range(3))
            pygame.draw.line(surf, col,
                             (bot_rect.x, bot_rect.y + yy),
                             (bot_rect.right - 1, bot_rect.y + yy))
        cap = pygame.Rect(bot_rect.x - 6, bot_rect.y, w + 12, 14)
        pygame.draw.rect(surf, PILLAR_LIGHT, cap)
        pygame.draw.rect(surf, PILLAR_DARK, cap, 2)
        pygame.draw.rect(surf, PILLAR_DARK, bot_rect, 2)
        for band_t in (0.28, 0.50, 0.72):
            band_y = bot_rect.y + int(bot_rect.h * band_t)
            pygame.draw.line(surf, PILLAR_DARK,
                             (bot_rect.x + 4, band_y),
                             (bot_rect.right - 5, band_y), 2)
            pygame.draw.line(surf, PILLAR_LIGHT,
                             (bot_rect.x + 4, band_y - 1),
                             (bot_rect.right - 5, band_y - 1), 1)

        # Top pillar.
        top_rect = pygame.Rect(px_left, 0, w, top_bottom)
        for yy in range(top_rect.h):
            t = yy / max(1, top_rect.h - 1)
            if t > 0.94:
                f = (1.0 - t) / 0.06
                col = tuple(int(PILLAR_LIGHT[k] + (PILLAR_BODY[k] - PILLAR_LIGHT[k]) * f)
                            for k in range(3))
            else:
                f = 1.0 - t / 0.94
                col = tuple(int(PILLAR_BODY[k] + (PILLAR_DARK[k] - PILLAR_BODY[k]) * f)
                            for k in range(3))
            pygame.draw.line(surf, col,
                             (top_rect.x, top_rect.y + yy),
                             (top_rect.right - 1, top_rect.y + yy))
        cap = pygame.Rect(top_rect.x - 6, top_rect.bottom - 14, w + 12, 14)
        pygame.draw.rect(surf, PILLAR_LIGHT, cap)
        pygame.draw.rect(surf, PILLAR_DARK, cap, 2)
        pygame.draw.rect(surf, PILLAR_DARK, top_rect, 2)
        for band_t in (0.25, 0.50, 0.75):
            band_y = top_rect.y + int(top_rect.h * band_t)
            pygame.draw.line(surf, PILLAR_DARK,
                             (top_rect.x + 4, band_y),
                             (top_rect.right - 5, band_y), 2)
            pygame.draw.line(surf, PILLAR_LIGHT,
                             (top_rect.x + 4, band_y - 1),
                             (top_rect.right - 5, band_y - 1), 1)

        anchors.append((
            top_rect.x - 6,                    # cap left edge
            top_rect.right + 6,                # cap right edge
            top_rect.bottom - 14,              # cap top edge
            gap_y,                             # gap centre y
        ))

    # ── Chest + coin pile in the GAP between pillar #2 (centre) and #3
    # (right) — chest is RIGHT of the centre pillar per world.py
    # (`bx = pillar.x + PIPE_W + spacing*0.5`), so it sits in the
    # right-hand gap, not on top of the centre pillar.
    chest_cx = int(centers[1] + pipe_w_hero // 2 + (centers[2] - centers[1] - pipe_w_hero) // 2)
    chest_cy = anchors[1][3]
    _draw_open_chest(surf, chest_cx, chest_cy, scale=1.7)

    # ── Banner above chest ──
    # Hero scale 1.35× so the banner reads "celebration" without spanning
    # so wide it engulfs the garland anchors and forces the festoon to
    # duck under it. Sits well above the chest so chest + banner occupy
    # distinct vertical bands.
    banner = _build_banner_hires(day=day)
    bw_hero = int(banner.get_width() * 1.35)
    bh_hero = int(banner.get_height() * 1.35)
    banner_hero = pygame.transform.smoothscale(banner, (bw_hero, bh_hero))
    banner_y = chest_cy - 165
    banner_x = chest_cx - bw_hero // 2

    # Firework bursts radiate FROM the banner centre. Order: bursts first,
    # then banner on top so the dominant gold burst hugs the ribbon
    # silhouette like a real celebration backdrop.
    _draw_firework_bursts(surf, chest_cx, banner_y + bh_hero // 2)

    surf.blit(banner_hero, (banner_x, banner_y))

    # ── Garland between LEFT (anchors[0]) and RIGHT (anchors[2]) ──
    # Drawn AFTER the banner so the catenary's endpoints (rising up to
    # the pillar caps) sit IN FRONT of the banner's outer corners — that
    # parallax cue sells the festoon as world-space foreground.
    # Sag is tuned so the catenary midpoint sits ABOVE the banner top —
    # the string drapes through the pillar-cap zone, the banner reigns
    # below it. This avoids the "midpoint disappears into the gold body"
    # collision while still letting the rising endpoints overlap the
    # banner corners for foreground depth.
    left_anchor_x  = anchors[0][1]        # right edge of LEFT pillar cap
    left_anchor_y  = anchors[0][2]
    right_anchor_x = anchors[2][0]        # left edge of RIGHT pillar cap
    right_anchor_y = anchors[2][2]
    cap_y = max(left_anchor_y, right_anchor_y)
    # Aim the midpoint ~20 px above the banner top so the festoon body
    # rides in the upper-gap "celebration band" while the rising ends
    # arc behind the banner's outer corners.
    target_mid_y = banner_y - 20
    sag = max(40, target_mid_y - cap_y)
    _draw_festoon_string(surf, left_anchor_x, left_anchor_y,
                         right_anchor_x, right_anchor_y,
                         sag=sag, n_bulbs=14)

    # A handful of extra coin sparkle particles arcing up around the
    # chest — sells the "POP" moment the actual world.py spawns.
    rng = random.Random(7777)
    for _ in range(22):
        ang = rng.uniform(-math.pi + 0.3, -0.3)
        d = rng.uniform(40, 180)
        sx = chest_cx + math.cos(ang) * d
        sy = chest_cy + math.sin(ang) * d * 0.75
        cr = rng.choice((3, 4, 5))
        pygame.draw.circle(surf, COIN_GOLD, (int(sx), int(sy)), cr)
        pygame.draw.circle(surf, COIN_RIM,  (int(sx), int(sy)), cr, 1)

    return surf


# ── Detail cells ───────────────────────────────────────────────────────────


def _render_banner_zoom_cell(w: int, h: int) -> pygame.Surface:
    """Cell 2 — banner zoom at hero size with the polished firework
    treatment around it. The 'isolated banner' read so the critic can
    inspect the V3-polish work cleanly."""
    cell = _twilight_bg(w, h)
    cx = w // 2
    cy = h // 2 + 4

    # Bursts first so banner sits on top.
    _draw_firework_bursts(cell, cx, cy)
    banner = _build_banner_hires(day=7)
    # Use a 1.25× zoom for the banner inspection cell — bigger than
    # canonical so the embossed text + bevel changes show up at review
    # scale without needing a 100% crop.
    bw = int(banner.get_width() * 1.25)
    bh = int(banner.get_height() * 1.25)
    banner_zoom = pygame.transform.smoothscale(banner, (bw, bh))
    cell.blit(banner_zoom, ((w - bw) // 2, cy - bh // 2))

    pygame.draw.rect(cell, (24, 20, 28), (0, 0, w, h), 1)
    return cell


def _render_garland_zoom_cell(w: int, h: int) -> pygame.Surface:
    """Cell 3 — garland zoom. Two stubby pillar silhouettes at equal
    height + the catenary draped between with 8 bulbs (per spec)."""
    cell = _twilight_bg(w, h)

    # Two stubby pillar silhouettes — just enough to read the festoon as
    # "anchored to a thing" rather than floating mid-air.
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

    # Catenary anchors at INNER edge of each cap (where the bulb chain
    # naturally hangs free of the pillar body).
    a_lx = px_left + pillar_w + 4
    a_rx = px_right - 4
    a_y  = pillar_y_top + 6
    span = a_rx - a_lx
    _draw_festoon_string(cell, a_lx, a_y, a_rx, a_y,
                         sag=max(40, int(span * 0.20)), n_bulbs=8)

    # Caption.
    cap_font = _font(11, bold=True)
    cap = cap_font.render("8 bulbs  /  scarlet filaments  /  catenary thread",
                          True, STAR_CREAM)
    cap.set_alpha(220)
    cell.blit(cap, ((w - cap.get_width()) // 2, h - 22))

    pygame.draw.rect(cell, (24, 20, 28), (0, 0, w, h), 1)
    return cell


def _render_asymmetric_cell(w: int, h: int) -> pygame.Surface:
    """Cell 4 — asymmetric pillar heights (one tall, one short) so the
    critic can verify the catenary stays elegant when the bird flew
    through a steep gap rather than a level one."""
    cell = _twilight_bg(w, h)

    pillar_w = 44
    # LEFT pillar — short (cap high in the frame).
    left_cap_y  = 30
    left_h      = h - 50 - 60     # short
    # RIGHT pillar — taller (cap low in the frame, ~100 px lower than left).
    right_cap_y = 130
    right_h     = h - 50 - 130    # shorter from its cap down

    px_left  = 60
    px_right = w - 60 - pillar_w

    # Draw both pillars.
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

    # Asymmetric catenary — anchor heights differ by 100 px per brief.
    a_lx = px_left + pillar_w + 4
    a_ly = left_cap_y + 6
    a_rx = px_right - 4
    a_ry = right_cap_y + 6
    span = a_rx - a_lx
    _draw_festoon_string(cell, a_lx, a_ly, a_rx, a_ry,
                         sag=max(40, int(span * 0.20)), n_bulbs=8)

    cap_font = _font(11, bold=True)
    cap = cap_font.render("asymmetric anchors  Δ ≈ 100 px  — catenary tilts cleanly",
                          True, STAR_CREAM)
    cap.set_alpha(220)
    cell.blit(cap, ((w - cap.get_width()) // 2, h - 22))

    pygame.draw.rect(cell, (24, 20, 28), (0, 0, w, h), 1)
    return cell


def _render_thumbnail_cell(w: int, h: int) -> pygame.Surface:
    """Cell 5 — in-game-scale thumbnail of the hero shot.

    The hero scene was rendered at 3× game canvas; here we render it at
    1× actual game canvas (360 px wide) and centre it. This is the panel
    that decides whether the celebration READS at the player's viewing
    scale — every previous round's biggest risk was 'looks great big,
    invisible at game size'."""
    cell = _twilight_bg(w, h)

    # Real game canvas size (game/config.py — virtual canvas).
    game_w = 360
    game_h = 200                  # cropped vertical slice for the strip

    # Render a 1× game-canvas hero. Pillar widths + banner widths use
    # the canonical pixel counts (58 px pillars, 340 px banner), so
    # everything is true to what ships in-game.
    #
    # Composition: chest is CENTERED on the canvas (so the banner +
    # garland fit). The chest pillar (#2) is to the LEFT of the chest,
    # the right-flank pillar (#3) to the right. A trim of the left-flank
    # pillar (#1) shows on the canvas's left edge, just enough to anchor
    # the garland's far end.
    hero_1x = _twilight_bg(game_w, game_h)

    pipe_w = 58
    # In the real game the chest spawns at pillar.x + PIPE_W + spacing*0.5.
    # `spacing` between consecutive pillars in cycle-finale is ~PIPE_W + ~80.
    # Use 140 px between pillar centers for the thumbnail — that puts the
    # chest 70 px right of the chest-pillar centre.
    pillar_gap = 140
    chest_cx = game_w // 2
    # Chest pillar center is 70 px LEFT of chest, right-flank 70 px RIGHT.
    centers = [chest_cx - pillar_gap - pillar_gap // 2,
               chest_cx - pillar_gap // 2,
               chest_cx + pillar_gap // 2]
    base_gap_y = game_h // 2
    base_gap_h = 110

    cap_records = []
    for i, ccx in enumerate(centers):
        px = int(ccx - pipe_w // 2)
        top_bottom = base_gap_y - base_gap_h // 2
        bot_top    = base_gap_y + base_gap_h // 2

        # Bottom.
        bot_rect = pygame.Rect(px, bot_top, pipe_w, game_h - bot_top)
        for yy in range(bot_rect.h):
            t = yy / max(1, bot_rect.h - 1)
            if t < 0.10:
                f = t / 0.10
                col = tuple(int(PILLAR_LIGHT[k] + (PILLAR_BODY[k] - PILLAR_LIGHT[k]) * f)
                            for k in range(3))
            else:
                f = (t - 0.10) / 0.90
                col = tuple(int(PILLAR_BODY[k] + (PILLAR_DARK[k] - PILLAR_BODY[k]) * f)
                            for k in range(3))
            pygame.draw.line(hero_1x, col,
                             (bot_rect.x, bot_rect.y + yy),
                             (bot_rect.right - 1, bot_rect.y + yy))
        cap = pygame.Rect(bot_rect.x - 3, bot_rect.y, pipe_w + 6, 6)
        pygame.draw.rect(hero_1x, PILLAR_LIGHT, cap)
        pygame.draw.rect(hero_1x, PILLAR_DARK, cap, 1)
        pygame.draw.rect(hero_1x, PILLAR_DARK, bot_rect, 1)

        # Top.
        top_rect = pygame.Rect(px, 0, pipe_w, top_bottom)
        for yy in range(top_rect.h):
            t = yy / max(1, top_rect.h - 1)
            if t > 0.90:
                f = (1.0 - t) / 0.10
                col = tuple(int(PILLAR_LIGHT[k] + (PILLAR_BODY[k] - PILLAR_LIGHT[k]) * f)
                            for k in range(3))
            else:
                f = 1.0 - t / 0.90
                col = tuple(int(PILLAR_BODY[k] + (PILLAR_DARK[k] - PILLAR_BODY[k]) * f)
                            for k in range(3))
            pygame.draw.line(hero_1x, col,
                             (top_rect.x, top_rect.y + yy),
                             (top_rect.right - 1, top_rect.y + yy))
        cap = pygame.Rect(top_rect.x - 3, top_rect.bottom - 6, pipe_w + 6, 6)
        pygame.draw.rect(hero_1x, PILLAR_LIGHT, cap)
        pygame.draw.rect(hero_1x, PILLAR_DARK, cap, 1)
        pygame.draw.rect(hero_1x, PILLAR_DARK, top_rect, 1)
        cap_records.append((cap.x, cap.right, cap.y, base_gap_y))

    # Chest centred; banner sits 80 px above it so chest reads first.
    chest_cy = base_gap_y
    _draw_open_chest(hero_1x, chest_cx, chest_cy, scale=1.0)

    banner = _build_banner_hires(day=7)
    banner_y = chest_cy - 80
    banner_x = chest_cx - banner.get_width() // 2
    _draw_firework_bursts(hero_1x, chest_cx,
                          banner_y + banner.get_height() // 2)
    hero_1x.blit(banner, (banner_x, banner_y))

    # Garland between LEFT-flank (cap_records[0]) and RIGHT-flank
    # (cap_records[2]). Same layering as the hero: sag midpoint sits
    # ABOVE the banner top so the festoon body never collides with
    # gold; rising endpoints arc behind the banner's outer corners for
    # foreground depth.
    left  = cap_records[0]
    right = cap_records[2]
    a_lx = left[1]
    a_ly = left[2]
    a_rx = right[0]
    a_ry = right[2]
    cap_y_1x = max(a_ly, a_ry)
    target_mid_1x = banner_y - 10
    sag_1x = max(15, target_mid_1x - cap_y_1x)
    _draw_festoon_string(hero_1x, a_lx, a_ly, a_rx, a_ry,
                         sag=sag_1x, n_bulbs=8)

    # Centre the 360-wide hero on the (wider) cell.
    cell.blit(hero_1x, ((w - game_w) // 2, (h - game_h) // 2))

    # Caption.
    cap_font = _font(11, bold=True)
    cap = cap_font.render("1× actual game canvas (360 × 200 px crop)  — does the moment READ at play scale?",
                          True, STAR_CREAM)
    cap.set_alpha(220)
    cell.blit(cap, ((w - cap.get_width()) // 2, h - 18))

    pygame.draw.rect(cell, (24, 20, 28), (0, 0, w, h), 1)
    return cell


# ── Sheet layout ───────────────────────────────────────────────────────────


CELL_W   = 520
CELL_H   = 220
HERO_W   = CELL_W * 2 + 8        # full-width hero spans both columns + gap
HERO_H   = 320                   # taller hero so the chest + banner breathe
TITLE_H  = 40
PAD      = 8


def render_sheet() -> pygame.Surface:
    sheet_w = 2 * CELL_W + 3 * PAD
    sheet_h = TITLE_H + HERO_H + 2 * CELL_H + 4 * PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 18, 30))

    # Title strip.
    title_font = _font(18, bold=True)
    title = title_font.render(
        "TREASURE BOX  cycle-finale reveal — Round 3   V3 fireworks + V4 garland across flanking pillars",
        True, STAR_CREAM,
    )
    sheet.blit(title, (PAD + 8, (TITLE_H - title.get_height()) // 2 + 2))

    # Cell 1 — full-width hero (spans cols).
    hero = _render_hero_scene(HERO_W, HERO_H)
    pygame.draw.rect(hero, (24, 20, 28), (0, 0, HERO_W, HERO_H), 1)
    # Label.
    label_font = _font(14, bold=True)
    lbl_shadow = label_font.render("HERO  full scene at hero scale (~3× game canvas)",
                                   True, (0, 0, 0))
    lbl_shadow.set_alpha(160)
    lbl = label_font.render("HERO  full scene at hero scale (~3× game canvas)",
                            True, STAR_CREAM)
    lbl.set_alpha(220)
    hero.blit(lbl_shadow, (11, 11))
    hero.blit(lbl, (10, 10))
    sheet.blit(hero, (PAD, TITLE_H + PAD))

    # Cells 2–5 (2×2 grid below).
    bz = _render_banner_zoom_cell(CELL_W, CELL_H)
    gz = _render_garland_zoom_cell(CELL_W, CELL_H)
    az = _render_asymmetric_cell(CELL_W, CELL_H)
    tz = _render_thumbnail_cell(CELL_W, CELL_H)

    # Cell labels — top-left corner, drop-shadowed.
    def _label(cell, text):
        s = label_font.render(text, True, (0, 0, 0))
        s.set_alpha(160)
        t = label_font.render(text, True, STAR_CREAM)
        t.set_alpha(220)
        cell.blit(s, (11, 11))
        cell.blit(t, (10, 10))

    _label(bz, "Cell 2  banner zoom  V3 firework motif (polished)")
    _label(gz, "Cell 3  garland zoom  8 bulbs + catenary, no flags")
    _label(az, "Cell 4  asymmetric pillar heights")
    _label(tz, "Cell 5  1× thumbnail  does it READ at play scale?")

    row1_y = TITLE_H + HERO_H + 2 * PAD
    row2_y = row1_y + CELL_H + PAD
    sheet.blit(bz, (PAD,                   row1_y))
    sheet.blit(gz, (PAD + CELL_W + PAD,    row1_y))
    sheet.blit(az, (PAD,                   row2_y))
    sheet.blit(tz, (PAD + CELL_W + PAD,    row2_y))

    return sheet


def main():
    sheet = render_sheet()
    out_dir = os.path.join(os.path.dirname(THIS_DIR), "docs", "treasure_box")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "banner_designs.png")
    pygame.image.save(sheet, out_path)
    print(f"wrote {out_path}  ({sheet.get_width()}×{sheet.get_height()})")


if __name__ == "__main__":
    main()
