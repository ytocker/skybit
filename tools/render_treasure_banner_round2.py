"""Treasure Box cycle-finale banner — Round 2 exploration sheet.

Round 1 (flat-gold notched ribbon, 4 corner pearls, red velvet bottom rim)
shipped but the user wanted MORE celebration — a higher-resolution ribbon
with festive elements around it, and 5 distinct motifs to choose from.

This script bakes a 2 × 3 grid:

  V1 sunburst   V2 confetti
  V3 fireworks  V4 garland
  V5 laurel     legend / palette / thumbnail row

Each motif keeps the Round-1 notched-ribbon silhouette but bumps quality:
  * 2× internal render then smoothscale (kills outline aliasing)
  * 4-stop gold gradient (cream → hot gold → saturated gold → deep amber)
  * 2 px embossed bevel inside the dark outline (white top, dark bottom)
  * 1 px embossed text drop (white top + dark bottom under the cream fill)
  * Velvet rim gains a 1 px scarlet highlight along its top edge

Output: docs/treasure_box/banner_designs.png (overwrites Round 1).

Re-runnable; doc-only — not bundled into the WASM/desktop builds."""
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

# ── Palette — explicit per the brief so it never drifts from the spec ───────

GOLD_HIGHLIGHT = (255, 244, 188)    # 0-15 % ribbon (cream specular)
GOLD_HOT       = (255, 220, 110)    # 15-55 % (bright body)
GOLD_SAT       = (240, 188,  56)    # 55-92 % (saturated belly)
GOLD_AMBER     = (196, 132,  28)    # 92-100 % (deep underside)
GOLD_INK       = ( 72,  48,  12)    # dark outline
VELVET         = (168,  32,  16)    # bottom rim
VELVET_HI      = (220,  64,  32)    # 1 px scarlet rim highlight
STAR_CREAM     = (252, 244, 218)
CONFETTI_RED   = (236,  72,  64)
CONFETTI_BLUE  = ( 96, 168, 240)
CONFETTI_GOLD  = (255, 220, 110)
CONFETTI_PINK  = (236,  92, 168)
CONFETTI_CREAM = (252, 244, 218)
FIRE_RED       = (248,  96,  88)
FIRE_CYAN      = ( 96, 200, 232)
FIRE_GOLD      = (255, 220, 110)
BULB_WARM      = (255, 240, 200)
THREAD_DARK    = ( 32,  28,  36)
LEAF_AMBER     = (196, 152,  44)

# Twilight sky — cycle-finale phase per spec.
SKY_TOP = (255, 168,  96)
SKY_BOT = (168, 132, 188)

# Banner silhouette (Round 1 values, scaled 2× internally and smoothscaled).
BANNER_W = 340
BANNER_H = 78
NOTCH    = 20
OUTLINE  = 3
SHADOW_DX = 4
SHADOW_DY = 5
SS = 2                            # 2× internal supersample for clean edges

# Final on-sheet banner size matches what the player sees in-game.
# (BANNER_W stays as the canonical width; the 2× SS just kills aliasing.)


# ── Helpers ────────────────────────────────────────────────────────────────


def _ribbon_polygon(bw: int, bh: int, notch: int) -> list[tuple[int, int]]:
    """Notched forked-end ribbon — chevron cuts on left + right."""
    return [
        (0, 0), (bw, 0),
        (bw - notch, bh // 2),
        (bw, bh), (0, bh),
        (notch, bh // 2),
    ]


def _multi_stop_gradient(bw: int, bh: int) -> pygame.Surface:
    """4-stop vertical gold gradient. Interp inside each stop's band so
    the highlight reads as a thin specular at the top instead of a wash."""
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
        # Find the bracketing stop pair.
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
    """Bake one banner at SS× supersample then smoothscale to final.

    The whole baking pipeline matches game/entities.py::TreasureBanner._build
    so the chosen motif drops straight in — only the additions (4-stop
    gradient, bevel, embossed text, velvet highlight) need porting later."""
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

    # Drop shadow — same silhouette, offset, soft black.
    shadow_pts = [(x + sdx, y + sdy) for (x, y) in ribbon]
    pygame.draw.polygon(comp, (0, 0, 0, 170), shadow_pts)

    # Mask + 4-stop gold gradient body.
    body = _multi_stop_gradient(bw, bh)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), ribbon)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    comp.blit(body, (0, 0))

    # Red velvet bottom rim — masked to the notched silhouette so it
    # inherits the chevron cuts cleanly.
    rim_h = 8 * SS
    rim = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(rim, VELVET, (0, bh - rim_h, bw, rim_h))
    # 1 px scarlet highlight along the rim's TOP edge — reads as a fabric
    # crease catching the light instead of flat paint.
    pygame.draw.line(rim, VELVET_HI, (0, bh - rim_h),
                     (bw, bh - rim_h), max(1, SS))
    rim.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    comp.blit(rim, (0, 0))

    # Embossed bevel INSIDE the dark outline.
    # White-alpha top-inner edge + dark-alpha bottom-inner edge fake a
    # chiseled metal lip without re-doing the polygon math.
    bevel_top = pygame.Surface((bw, bh), pygame.SRCALPHA)
    bevel_bot = pygame.Surface((bw, bh), pygame.SRCALPHA)
    inner_pts_top = [(x, y + max(1, SS)) for (x, y) in ribbon]
    inner_pts_bot = [(x, y - max(1, SS)) for (x, y) in ribbon]
    pygame.draw.polygon(bevel_top, (255, 255, 255, 110),
                        inner_pts_top, max(1, 2 * SS))
    pygame.draw.polygon(bevel_bot, (0, 0, 0, 120),
                        inner_pts_bot, max(1, 2 * SS))
    # Mask both so the bevel rides INSIDE the ribbon silhouette.
    bevel_top.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    bevel_bot.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    comp.blit(bevel_top, (0, 0))
    comp.blit(bevel_bot, (0, 0))

    # Dark outline tracing the ribbon polygon (on top of the bevel so it
    # reads as the "edge" with the bevel as the "inner chamfer").
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

    # Text — embossed: white-alpha top drop, dark-alpha bottom drop, then
    # the cream fill on top. The two drops only show along the letter
    # edges where the centre fill doesn't cover them, so letters feel
    # etched into the gold.
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

    # Thick dark outline (Round 1's safety net so the cream stays legible
    # on the gold body).
    o = max(2, 2 * SS)
    for ox, oy in ((-o, 0), (o, 0), (0, -o), (0, o),
                   (-o, -o), (o, -o), (-o, o), (o, o)):
        comp.blit(out_render, (tx + ox, ty + oy))
    # 1 px embossed drops UNDER the cream fill — the cream covers them
    # except along the outer edge of each letter, leaving a thin chiseled
    # highlight on the top + a thin engraving line on the bottom.
    comp.blit(text_white, (tx, ty - max(1, SS)))
    comp.blit(text_dark,  (tx, ty + max(1, SS)))
    comp.blit(text_cream, (tx, ty))

    # Smoothscale down to the canonical (player-facing) size.
    final_w = BANNER_W + SHADOW_DX
    final_h = BANNER_H + SHADOW_DY
    return pygame.transform.smoothscale(comp, (final_w, final_h))


# ── Motif decorators — drawn AROUND a banner blitted at (bx, by) ───────────


def _draw_glow_disc(surf, cx, cy, radius, color, alpha):
    """Soft glow disc — stacked concentric circles with alpha falloff.
    Plain alpha blit (NOT additive) so the halo reads as warm haze
    instead of a blown-out white disc on the twilight bg."""
    disc = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    steps = 18
    for i in range(steps):
        f = 1.0 - i / steps
        r = int(radius * f)
        # Cubic falloff keeps the bulk of the halo soft + lets the rim
        # fade smoothly into the sky instead of cliff-edging.
        a = int(alpha * (f ** 3) * 1.4)
        if r <= 0 or a <= 0:
            continue
        pygame.draw.circle(disc, (*color, min(a, 255)),
                           (radius, radius), r)
    surf.blit(disc, (cx - radius, cy - radius))


def _draw_sunburst_halo(surf, cx, cy):
    """V1 — 18 alternating cream/amber rays + soft cream glow disc."""
    _draw_glow_disc(surf, cx, cy, 160, (255, 230, 170), 80)
    rays = 18
    long_len  = 175
    short_len = 130
    half_w_long  = 12
    half_w_short = 8
    for k in range(rays):
        ang = -math.pi / 2 + k * (math.tau / rays)
        long_ray = (k % 2 == 0)
        col = STAR_CREAM if long_ray else (252, 200, 88)
        tip_r = long_len if long_ray else short_len
        half = half_w_long if long_ray else half_w_short
        tip = (cx + math.cos(ang) * tip_r,
               cy + math.sin(ang) * tip_r)
        a = (cx + math.cos(ang + math.pi / 2) * half,
             cy + math.sin(ang + math.pi / 2) * half)
        b = (cx + math.cos(ang - math.pi / 2) * half,
             cy + math.sin(ang - math.pi / 2) * half)
        pygame.draw.polygon(surf, col, [tip, a, b])


def _draw_confetti_storm(surf, cx, cy, rng: random.Random):
    """V2 — ~80 confetti rects + 6 tickertape streamers. Confetti is
    seeded so the sheet is reproducible across runs (review pass)."""
    palette = [CONFETTI_RED, CONFETTI_CREAM, CONFETTI_BLUE,
               CONFETTI_GOLD, CONFETTI_PINK]
    for _ in range(80):
        # Cluster around the banner — gaussian distance keeps most pieces
        # near the ribbon and bleeds a few out toward the edges.
        dx = rng.gauss(0, 110)
        dy = rng.gauss(0, 70)
        px = cx + dx
        py = cy + dy
        w = rng.randint(6, 9)
        h = rng.randint(6, 9)
        ang = rng.uniform(0, 360)
        col = rng.choice(palette)
        piece = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
        pygame.draw.rect(piece, col, (2, 2, w, h))
        # Motion-blur ghost on ~25 % of pieces so the storm reads as in-
        # motion instead of pinned to the air.
        if rng.random() < 0.25:
            ghost = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
            pygame.draw.rect(ghost, (*col, 120), (2, 2, w, h))
            ghost_rot = pygame.transform.rotate(ghost, ang)
            gx = int(px - ghost_rot.get_width() / 2 - 1)
            gy = int(py - ghost_rot.get_height() / 2 + 1)
            surf.blit(ghost_rot, (gx, gy))
        rot = pygame.transform.rotate(piece, ang)
        rx = int(px - rot.get_width() / 2)
        ry = int(py - rot.get_height() / 2)
        surf.blit(rot, (rx, ry))

    # Tickertape streamers — long curvy ribbons curling over the top
    # edges of the banner. Each is a chain of short rotated segments so
    # the curve reads as a single continuous tape.
    streamers = [
        (cx - 150, cy - 60, CONFETTI_RED,   -0.6),
        (cx - 80,  cy - 80, CONFETTI_CREAM,  0.4),
        (cx - 20,  cy - 90, CONFETTI_BLUE,  -0.5),
        (cx + 40,  cy - 88, CONFETTI_GOLD,   0.5),
        (cx + 110, cy - 75, CONFETTI_RED,   -0.4),
        (cx + 160, cy - 50, CONFETTI_CREAM,  0.6),
    ]
    for sx, sy, col, curl in streamers:
        prev = (sx, sy)
        for step in range(28):
            t = step / 27.0
            # Sine-wave curl decaying in amplitude so the tape tapers off.
            ang = curl + math.sin(t * 6.0) * 0.9
            length = 6
            nx = prev[0] + math.cos(ang) * length
            ny = prev[1] + math.sin(ang) * length + t * 4
            width = max(2, int(4 - t * 2))
            pygame.draw.line(surf, col, prev, (nx, ny), width)
            prev = (nx, ny)


def _draw_starburst(surf, cx, cy, color, scale=1.0):
    """3-burst motif's single firework — matches treasure_box._build_starburst
    vocabulary so the family stays visually coherent."""
    rays = 16
    r_long  = int(70 * scale)
    r_short = int(r_long * 0.55)
    long_half  = int(r_long * 0.085)
    short_half = int(r_long * 0.06)
    for k in range(rays):
        ang = -math.pi / 2 + k * (math.tau / rays)
        long_ray = (k % 2 == 0)
        r_tip = r_long if long_ray else r_short
        half = long_half if long_ray else short_half
        col = color if long_ray else STAR_CREAM
        tip = (cx + math.cos(ang) * r_tip,
               cy + math.sin(ang) * r_tip)
        a = (cx + math.cos(ang + math.pi / 2) * half,
             cy + math.sin(ang + math.pi / 2) * half)
        b = (cx + math.cos(ang - math.pi / 2) * half,
             cy + math.sin(ang - math.pi / 2) * half)
        pygame.draw.polygon(surf, col, [tip, a, b])
    # 24 sparkle dots — half scattered along the rays, half past the tips.
    rng = random.Random(int(cx * 13 + cy * 7))
    for k in range(0, rays, 2):
        ang = -math.pi / 2 + k * (math.tau / rays)
        # Past-the-tip sparkle pip.
        tip_x = cx + math.cos(ang) * r_long * 1.12
        tip_y = cy + math.sin(ang) * r_long * 1.12
        pygame.draw.circle(surf, STAR_CREAM, (int(tip_x), int(tip_y)), 2)
        pygame.draw.circle(surf, (255, 255, 255),
                           (int(tip_x) - 1, int(tip_y) - 1), 1)
    for _ in range(16):
        ang = rng.uniform(0, math.tau)
        d = rng.uniform(r_short * 0.6, r_long * 0.95)
        sx = cx + math.cos(ang) * d
        sy = cy + math.sin(ang) * d
        pygame.draw.circle(surf, STAR_CREAM, (int(sx), int(sy)), 1)


def _draw_firework_bursts(surf, cx, cy):
    """V3 — 3 starburst fireworks (red top-left, cyan top-right, gold centre)."""
    # Behind-banner gold burst first so the other two sit on top.
    _draw_glow_disc(surf, cx, cy, 120, FIRE_GOLD, 70)
    _draw_starburst(surf, cx, cy, FIRE_GOLD, scale=1.15)
    # Top-left red.
    _draw_glow_disc(surf, cx - 145, cy - 55, 80, FIRE_RED, 80)
    _draw_starburst(surf, cx - 145, cy - 55, FIRE_RED, scale=0.85)
    # Top-right cyan.
    _draw_glow_disc(surf, cx + 145, cy - 55, 80, FIRE_CYAN, 80)
    _draw_starburst(surf, cx + 145, cy - 55, FIRE_CYAN, scale=0.85)


def _draw_garland(surf, cell_w, cx, cy_banner):
    """V4 — string across the top, 7 pennant flags + 8 festoon bulbs,
    banner hangs from the string via 2 thin thread lines."""
    string_y_left = 22
    string_y_right = 22
    string_sag = 14            # midpoint catenary drop in px
    string_mid_x = cell_w // 2
    string_mid_y = string_y_left + string_sag

    # Quadratic Bezier-ish catenary approximation — sample 60 points.
    def _string_y(px):
        t = px / cell_w
        # Symmetric parabola peaking at the middle.
        return string_y_left + 4 * string_sag * t * (1 - t)

    pts = [(x, _string_y(x)) for x in range(0, cell_w + 1, 4)]
    pygame.draw.lines(surf, THREAD_DARK, False, pts, 1)

    # 7 pennant flags, alternating cream / red / gold, hanging FROM the
    # string. Triangle: two top corners on the string, tip 26 px below.
    flag_palette = [CONFETTI_CREAM, CONFETTI_RED, CONFETTI_GOLD,
                    CONFETTI_CREAM, CONFETTI_RED, CONFETTI_GOLD,
                    CONFETTI_CREAM]
    flag_xs = [int(cell_w * (i + 1) / 8) for i in range(7)]
    for i, fx in enumerate(flag_xs):
        sy = _string_y(fx)
        col = flag_palette[i]
        flag = [
            (fx - 11, sy + 2),
            (fx + 11, sy + 2),
            (fx, sy + 26),
        ]
        pygame.draw.polygon(surf, col, flag)
        pygame.draw.polygon(surf, GOLD_INK, flag, 1)

    # 8 festoon bulbs between/around the pennants — warm-white with a
    # soft additive halo so they read as glowing not painted.
    bulb_xs = [int(cell_w * (i + 0.5) / 8) for i in range(8)]
    for bx in bulb_xs:
        by = _string_y(bx) + 4
        # Soft warm halo (plain alpha) so the bulb glows on the twilight
        # bg without bleaching out the surrounding sky.
        halo = pygame.Surface((22, 22), pygame.SRCALPHA)
        for ri, ai in ((10, 28), (8, 48), (6, 80)):
            pygame.draw.circle(halo, (255, 230, 170, ai), (11, 11), ri)
        surf.blit(halo, (bx - 11, by - 11))
        pygame.draw.circle(surf, BULB_WARM, (bx, by), 4)
        pygame.draw.circle(surf, GOLD_INK, (bx, by), 4, 1)
        pygame.draw.circle(surf, (255, 255, 255), (bx - 1, by - 1), 1)
        # 1 px dark thread connecting bulb to the string.
        pygame.draw.line(surf, THREAD_DARK, (bx, _string_y(bx)),
                         (bx, by - 4), 1)

    # Two thread lines anchoring the banner's TOP corners up to the
    # string. The banner corners sit BANNER_W wide centered on cx, banner
    # top at cy_banner - BANNER_H / 2.
    bx_left = cx - BANNER_W // 2 + 6
    bx_right = cx + BANNER_W // 2 - 6
    banner_top = cy_banner - BANNER_H // 2
    pygame.draw.line(surf, THREAD_DARK,
                     (bx_left, _string_y(bx_left)),
                     (bx_left, banner_top), 1)
    pygame.draw.line(surf, THREAD_DARK,
                     (bx_right, _string_y(bx_right)),
                     (bx_right, banner_top), 1)


def _bake_laurel_leaf(lw: int, lh: int) -> pygame.Surface:
    """A single laurel leaf — pointed almond shape, 2-stop cream→amber
    gradient, ink outline + centre vein. Baked once per draw call."""
    pad = 4
    leaf = pygame.Surface((lw + pad * 2, lh + pad * 2), pygame.SRCALPHA)
    # 2-stop gradient — base (left, cream) → tip (right, amber).
    for xx in range(lw):
        t = xx / max(1, lw - 1)
        c = (
            int(STAR_CREAM[0] + (LEAF_AMBER[0] - STAR_CREAM[0]) * t),
            int(STAR_CREAM[1] + (LEAF_AMBER[1] - STAR_CREAM[1]) * t),
            int(STAR_CREAM[2] + (LEAF_AMBER[2] - STAR_CREAM[2]) * t),
        )
        pygame.draw.line(leaf, c, (pad + xx, pad),
                         (pad + xx, pad + lh))
    # Pointed-almond shape: a polygon with rounded base + sharp tip.
    # Defined in leaf-local coords (base-left, tip-right) so rotation
    # places the base on the stem cleanly.
    cy_mid = pad + lh // 2
    almond = [
        (pad, cy_mid),
        (pad + lw // 5, pad),
        (pad + lw - 2, cy_mid),
        (pad + lw // 5, pad + lh),
    ]
    mask = pygame.Surface((lw + pad * 2, lh + pad * 2), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), almond)
    leaf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # 1 px dark ink vein along the long axis.
    pygame.draw.line(leaf, GOLD_INK, (pad + 3, cy_mid),
                     (pad + lw - 4, cy_mid), 1)
    # Outline stroke so adjacent leaves stay readable on overlap.
    pygame.draw.polygon(leaf, GOLD_INK, almond, 1)
    return leaf


def _draw_laurel_branch(surf, base_x, base_y, side: int):
    """V5 — one laurel branch arching up + over the banner's top corner.
    `side` is -1 (left branch, curves up-right) or +1 (right, up-left).
    9 leaves attach along the stem with their BASES on the curve and
    tips fanning outward, alternating up/down rows."""
    leaves = 9
    # Arc — start at the banner's bottom-outer corner, sweep up + over
    # the top-outer corner, terminate above + just inside it. Reads
    # like a wreath half on a championship plaque.
    ctrl_x = base_x + side * 8
    ctrl_y = base_y - 100
    tip_x  = base_x + side * -85
    tip_y  = base_y - 90
    pts = []
    for i in range(leaves + 1):
        t = i / leaves
        x = (1 - t) ** 2 * base_x + 2 * (1 - t) * t * ctrl_x + t ** 2 * tip_x
        y = (1 - t) ** 2 * base_y + 2 * (1 - t) * t * ctrl_y + t ** 2 * tip_y
        pts.append((x, y))

    # Stem — warm amber under-stroke + dark ink over-stroke gives the
    # vine a 3-D feel without a true bevel.
    pygame.draw.lines(surf, (146, 96, 28), False, pts, 3)
    pygame.draw.lines(surf, (90, 60, 18), False, pts, 1)

    lw, lh = 30, 12
    leaf_sprite = _bake_laurel_leaf(lw, lh)

    for i in range(leaves):
        # Anchor each leaf at the stem sample.
        ax, ay = pts[i]
        bx_, by_ = pts[i + 1]
        # Stem tangent — direction the leaf points "out from" the stem.
        dx = bx_ - ax
        dy = by_ - ay
        stem_ang = math.degrees(math.atan2(dy, dx))
        # Alternating outward angle off the stem — first leaf TOP side,
        # second BOTTOM side, etc. 70° looks like a real laurel sprig.
        outward = 75 if (i % 2 == 0) else -75
        leaf_ang = stem_ang + outward
        # Translate the leaf so its BASE sits exactly on the stem sample
        # by walking half its length along the leaf's long axis.
        along_ang = math.radians(leaf_ang)
        ox = math.cos(along_ang) * (lw / 2)
        oy = math.sin(along_ang) * (lw / 2)
        rotated = pygame.transform.rotate(leaf_sprite, -leaf_ang)
        rr = rotated.get_rect(center=(int(ax + ox), int(ay + oy)))
        surf.blit(rotated, rr.topleft)

    # Tip cap — one leaf pointing further along the stem direction so
    # the branch terminates in a clean point rather than mid-air.
    tip_dx = pts[-1][0] - pts[-2][0]
    tip_dy = pts[-1][1] - pts[-2][1]
    tip_ang = math.degrees(math.atan2(tip_dy, tip_dx))
    along_ang = math.radians(tip_ang)
    ox = math.cos(along_ang) * (lw / 2)
    oy = math.sin(along_ang) * (lw / 2)
    rotated = pygame.transform.rotate(leaf_sprite, -tip_ang)
    rr = rotated.get_rect(center=(int(pts[-1][0] + ox),
                                  int(pts[-1][1] + oy)))
    surf.blit(rotated, rr.topleft)


def _draw_5pt_star(surf, cx, cy, r, fill=STAR_CREAM, ink=GOLD_INK):
    """5-point star — alternating outer + inner vertices."""
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * (math.tau / 10)
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    pygame.draw.polygon(surf, fill, pts)
    pygame.draw.polygon(surf, ink, pts, 1)


def _draw_laurel_motif(surf, cx, cy):
    """V5 — two mirrored laurel branches + 5 star pips above the banner."""
    # Branches root just outside the banner's outer-bottom corners; the
    # arc sweeps up + over each top corner so the wreath frames the
    # ribbon like a championship plaque.
    _draw_laurel_branch(surf, cx - BANNER_W // 2 - 4, cy + 28, side=-1)
    _draw_laurel_branch(surf, cx + BANNER_W // 2 + 4, cy + 28, side=+1)
    # 5 white-star pips spread across the top in a gentle arc.
    star_specs = [
        (cx - 95, cy - 78, 7),
        (cx - 48, cy - 86, 8),
        (cx,      cy - 92, 9),
        (cx + 48, cy - 86, 8),
        (cx + 95, cy - 78, 7),
    ]
    for sx, sy, sr in star_specs:
        _draw_5pt_star(surf, sx, sy, sr)


# ── Cell composition ──────────────────────────────────────────────────────


CELL_W = 520
CELL_H = 200
TITLE_H = 40
COLS, ROWS = 2, 3
PAD = 8


def _twilight_bg(w, h) -> pygame.Surface:
    """Cycle-finale dawn/dusk gradient."""
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


def _render_cell(label: str, motif_fn, rng_seed: int) -> pygame.Surface:
    """One cell — twilight bg, motif decoration, banner @ hold-snapshot,
    label in the top-left corner."""
    cell = _twilight_bg(CELL_W, CELL_H)

    cx = CELL_W // 2
    cy = CELL_H // 2 + 4              # nudge down for banner+motif balance

    # Motif decorations FIRST so the banner sits cleanly on top.
    if motif_fn is _draw_confetti_storm:
        motif_fn(cell, cx, cy, random.Random(rng_seed))
    elif motif_fn is _draw_garland:
        motif_fn(cell, CELL_W, cx, cy)
    elif motif_fn is not None:
        motif_fn(cell, cx, cy)

    # Banner — bake hires, blit centered (the bake already includes its
    # own drop shadow so we don't add one here).
    banner = _build_banner_hires(day=1)
    br = banner.get_rect(center=(cx, cy))
    cell.blit(banner, br.topleft)

    # Cell label — cream alpha 200, 14 px.
    label_font = _font(14, bold=True)
    label_text = label_font.render(label, True, STAR_CREAM)
    label_text.set_alpha(200)
    # Tiny shadow so the label survives over bright sunburst rays.
    label_shadow = label_font.render(label, True, (0, 0, 0))
    label_shadow.set_alpha(140)
    cell.blit(label_shadow, (10, 9))
    cell.blit(label_text, (9, 8))

    # 1 px dark cell frame for visual separation in the sheet.
    pygame.draw.rect(cell, (24, 20, 28), (0, 0, CELL_W, CELL_H), 1)
    return cell


# ── 6th cell — legend / palette swatch + tiny stacked thumbnails ───────────


def _render_legend_cell() -> pygame.Surface:
    cell = _twilight_bg(CELL_W, CELL_H)

    # Cell label.
    label_font = _font(14, bold=True)
    label = label_font.render("legend  /  palette  /  thumbnails", True,
                              STAR_CREAM)
    label.set_alpha(200)
    cell.blit(label, (9, 8))

    # Top half: palette swatches with hex labels.
    swatch_font = _font(11, bold=True)
    palette = [
        ("highlight", GOLD_HIGHLIGHT),
        ("hot gold",  GOLD_HOT),
        ("sat gold",  GOLD_SAT),
        ("amber",     GOLD_AMBER),
        ("ink",       GOLD_INK),
        ("velvet",    VELVET),
        ("scarlet",   VELVET_HI),
        ("cream",     STAR_CREAM),
    ]
    sw_w = 50
    sw_h = 32
    sw_gap = 4
    total_w = len(palette) * sw_w + (len(palette) - 1) * sw_gap
    sx0 = (CELL_W - total_w) // 2
    sy0 = 32
    for i, (name, col) in enumerate(palette):
        sx = sx0 + i * (sw_w + sw_gap)
        pygame.draw.rect(cell, col, (sx, sy0, sw_w, sw_h))
        pygame.draw.rect(cell, (24, 20, 28), (sx, sy0, sw_w, sw_h), 1)
        nm = swatch_font.render(name, True, (24, 20, 28))
        nx = sx + (sw_w - nm.get_width()) // 2
        cell.blit(nm, (nx, sy0 + sw_h + 3))
        hex_str = "#%02X%02X%02X" % col
        hx = swatch_font.render(hex_str, True, STAR_CREAM)
        hx.set_alpha(220)
        cell.blit(hx, (sx + (sw_w - hx.get_width()) // 2, sy0 + sw_h + 16))

    # Bottom half: a single "ALL 5 stacked at small in-game size" thumbnail
    # row so the user sees how each motif reads at the size the banner
    # actually ships at (~280-340 px wide on a 360-px-virtual canvas, so
    # ~100 px wide on this sheet preserves the same pixel density).
    thumb_w = 90
    thumb_h = 34
    banner = _build_banner_hires(day=1)
    thumb = pygame.transform.smoothscale(banner, (thumb_w, thumb_h))

    thumb_y = 138
    thumb_gap = 8
    total_thumb_w = 5 * thumb_w + 4 * thumb_gap
    tx0 = (CELL_W - total_thumb_w) // 2
    motif_labels = ["sunburst", "confetti", "fireworks", "garland", "laurel"]
    for i, ml in enumerate(motif_labels):
        tx = tx0 + i * (thumb_w + thumb_gap)
        cell.blit(thumb, (tx, thumb_y))
        lab = swatch_font.render(ml, True, (24, 20, 28))
        lab_bg = pygame.Surface((lab.get_width() + 6, lab.get_height() + 2),
                                pygame.SRCALPHA)
        lab_bg.fill((252, 244, 218, 200))
        cell.blit(lab_bg, (tx + (thumb_w - lab_bg.get_width()) // 2,
                           thumb_y + thumb_h + 4))
        cell.blit(lab, (tx + (thumb_w - lab.get_width()) // 2 + 3,
                        thumb_y + thumb_h + 5))

    pygame.draw.rect(cell, (24, 20, 28), (0, 0, CELL_W, CELL_H), 1)
    return cell


# ── Sheet ──────────────────────────────────────────────────────────────────


def render_sheet() -> pygame.Surface:
    sheet_w = COLS * CELL_W + (COLS + 1) * PAD
    sheet_h = TITLE_H + ROWS * CELL_H + (ROWS + 1) * PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 18, 30))

    # Title strip.
    title_font = _font(18, bold=True)
    title = title_font.render(
        "TREASURE BOX  cycle-finale banner — Round 2  pick a celebration motif",
        True, STAR_CREAM,
    )
    sheet.blit(title, (PAD + 8, (TITLE_H - title.get_height()) // 2 + 2))

    # Render each cell.
    cells = [
        _render_cell("V1  sunburst",   _draw_sunburst_halo,    1001),
        _render_cell("V2  confetti",   _draw_confetti_storm,   1337),
        _render_cell("V3  fireworks",  _draw_firework_bursts,  2025),
        _render_cell("V4  garland",    _draw_garland,          4040),
        _render_cell("V5  laurel",     _draw_laurel_motif,     5050),
        _render_legend_cell(),
    ]
    for i, cell in enumerate(cells):
        col = i % COLS
        row = i // COLS
        x = PAD + col * (CELL_W + PAD)
        y = TITLE_H + PAD + row * (CELL_H + PAD)
        sheet.blit(cell, (x, y))

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
