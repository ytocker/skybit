"""Render 5 design variants of the megamagnet force-field for selection.

The megamagnet power-up is a planned successor to `magnet` with 2x
radius and an extended visual treatment. Each variant freezes the
field at a representative pulse phase so the static PNG reads cleanly.

Run from repo root:

    python tools/snapshot_megamagnet_variants.py

Outputs 5 PNGs under docs/screenshots/powerups/megamagnet/.
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import random
import pygame
pygame.init()

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import W, H, GROUND_Y, MAGNET_RADIUS
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.entities import Bird, Coin


# Snapshot-local. Promotes to game/config.py in Step 2 once a variant
# is selected.
MEGAMAGNET_RADIUS = MAGNET_RADIUS * 2  # 164


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "screenshots", "powerups", "megamagnet",
)
os.makedirs(OUT_DIR, exist_ok=True)


def draw_bg(surf, scroll=0.0, phase=0.62):
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    b = (a + 1) % buckets
    t = bucket_f - int(bucket_f)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
    sky_a.set_alpha(None)
    surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255))
        surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)
    for i, (bx, by, sc, variant) in enumerate((
            (20,  90, 0.9, 0),
            (180, 140, 1.1, 2),
            (60,  220, 0.8, 3),
            (230, 60, 0.7, 1),
            (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2 + i) * 3, sc, variant=variant)
    draw_mountains(surf, scroll, GROUND_Y, W,
                   pal_a['mtn_far'], pal_a['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                pal_a['ground_top'], pal_a['ground_mid'], (60, 40, 25))


# ── per-variant field draws ─────────────────────────────────────────────────
# All variants render into a per-call SRCALPHA surface sized to the
# doubled radius, then blit centred on the bird. Pulse phase is the
# `t_pulse` value the in-game code derives from `_cloud_phase * 5.5`.

def _new_field_surf():
    rad = MEGAMAGNET_RADIUS
    surf = pygame.Surface((rad * 2 + 8, rad * 2 + 8), pygame.SRCALPHA)
    return surf, rad + 4, rad + 4


def _inner_glow(surf, cx, cy, glow_rad, color):
    for i in range(22, 0, -1):
        r = int(glow_rad * i / 22)
        inner_t = i / 22
        bell = math.exp(-((inner_t - 0.85) ** 2) / 0.15)
        a = int(72 * bell)
        if a > 0:
            pygame.draw.circle(surf, (*color, a), (cx, cy), r)


def _aa_ring(surf, cx, cy, r, width, ring_col, alpha):
    AA_COL = (255, 240, 180)
    pygame.draw.circle(surf, (*AA_COL, alpha // 3), (cx, cy), r + 1, width)
    pygame.draw.circle(surf, (*AA_COL, alpha // 3), (cx, cy), r - 1, width)
    pygame.draw.circle(surf, (*ring_col, alpha), (cx, cy), r, width)


# Variant 1 — dense rings (5 rings instead of 3, family palette)
def draw_dense_rings(t_pulse):
    surf, cx, cy = _new_field_surf()
    rad = MEGAMAGNET_RADIUS

    BREATH = 0.30
    s_outer = math.sin(t_pulse + 0.0)
    u_outer = (s_outer + 1) / 2
    outer_factor = 1.0 - BREATH * (1.0 - u_outer)
    glow_rad = rad * outer_factor
    _inner_glow(surf, cx, cy, glow_rad, (245, 175, 40))

    for rfac, phase, alpha, width, breath_scale, ring_col in (
            (1.00, 0.0, 190, 3, 1.00, (255, 220, 100)),
            (0.86, 0.4, 170, 3, 0.94, (255, 210,  85)),
            (0.70, 0.8, 145, 2, 0.86, (255, 195,  60)),
            (0.54, 1.2, 120, 2, 0.78, (245, 175,  40)),
            (0.38, 1.6, 100, 2, 0.70, (220, 155,  30))):
        amp = BREATH * breath_scale
        s = math.sin(t_pulse + phase)
        u = (s + 1) / 2
        rr = int(rad * rfac * (1.0 - amp * (1.0 - u)))
        _aa_ring(surf, cx, cy, rr, width, ring_col, alpha)
    return surf


# Variant 2 — chromatic (3 gold rings + counter-rotating purple+cyan shimmer)
def draw_chromatic(t_pulse):
    surf, cx, cy = _new_field_surf()
    rad = MEGAMAGNET_RADIUS

    BREATH = 0.30
    s_outer = math.sin(t_pulse + 0.0)
    u_outer = (s_outer + 1) / 2
    outer_factor = 1.0 - BREATH * (1.0 - u_outer)
    glow_rad = rad * outer_factor
    _inner_glow(surf, cx, cy, glow_rad, (245, 175, 40))

    for rfac, phase, alpha, width, breath_scale, ring_col in (
            (1.00, 0.0, 180, 3, 1.00, (255, 220, 100)),
            (0.78, 0.6, 140, 2, 0.85, (255, 195,  60)),
            (0.55, 1.2, 100, 2, 0.70, (235, 165,  35))):
        amp = BREATH * breath_scale
        s = math.sin(t_pulse + phase)
        u = (s + 1) / 2
        rr = int(rad * rfac * (1.0 - amp * (1.0 - u)))
        _aa_ring(surf, cx, cy, rr, width, ring_col, alpha)

    # Counter-rotating chromatic shimmer: 32 short arcs spread around
    # a ring at 0.92 * rad, hue cycling per-arc through violet-cyan.
    shimmer_r = rad * 0.92
    rot = -t_pulse * 0.4
    N = 32
    for i in range(N):
        a0 = rot + (i / N) * math.tau
        a1 = a0 + (math.tau / N) * 0.55
        hue_t = (i / N + t_pulse * 0.08) % 1.0
        col = _hsv_to_rgb(hue_t * 0.55 + 0.55, 0.8, 1.0)
        steps = 7
        for s in range(steps):
            ang = a0 + (a1 - a0) * (s / max(1, steps - 1))
            px = cx + math.cos(ang) * shimmer_r
            py = cy + math.sin(ang) * shimmer_r
            pygame.draw.circle(surf, (*col, 170), (int(px), int(py)), 2)
    return surf


def _hsv_to_rgb(h, s, v):
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    i %= 6
    r, g, b = [(v, t, p), (q, v, p), (p, v, t),
               (p, q, v), (t, p, v), (v, p, q)][i]
    return int(r * 255), int(g * 255), int(b * 255)


# Variant 3 — arcs (3 rings + 6 lightning arcs jumping between them)
def draw_arcs(t_pulse):
    surf, cx, cy = _new_field_surf()
    rad = MEGAMAGNET_RADIUS

    BREATH = 0.30
    s_outer = math.sin(t_pulse + 0.0)
    u_outer = (s_outer + 1) / 2
    outer_factor = 1.0 - BREATH * (1.0 - u_outer)
    glow_rad = rad * outer_factor
    _inner_glow(surf, cx, cy, glow_rad, (245, 175, 40))

    ring_radii = []
    for rfac, phase, alpha, width, breath_scale, ring_col in (
            (1.00, 0.0, 180, 3, 1.00, (255, 220, 100)),
            (0.78, 0.6, 140, 2, 0.85, (255, 195,  60)),
            (0.55, 1.2, 100, 2, 0.70, (235, 165,  35))):
        amp = BREATH * breath_scale
        s = math.sin(t_pulse + phase)
        u = (s + 1) / 2
        rr = int(rad * rfac * (1.0 - amp * (1.0 - u)))
        ring_radii.append(rr)
        _aa_ring(surf, cx, cy, rr, width, ring_col, alpha)

    # 6 procedural lightning arcs jumping outer ring → mid ring →
    # inner ring. Each arc is a jagged polyline; seeded per-arc so the
    # snapshot is deterministic.
    rng = random.Random(int(t_pulse * 1000) & 0xFFFF)
    ARC_COUNT = 6
    for k in range(ARC_COUNT):
        base_ang = (k / ARC_COUNT) * math.tau + t_pulse * 0.3
        r_outer = ring_radii[0]
        r_inner = ring_radii[2]
        segs = 10
        points = []
        for s in range(segs + 1):
            t = s / segs
            r = r_outer * (1 - t) + r_inner * t
            jitter_ang = base_ang + (rng.random() - 0.5) * 0.55 * (1 - abs(2 * t - 1))
            px = cx + math.cos(jitter_ang) * r
            py = cy + math.sin(jitter_ang) * r
            points.append((px, py))
        # bright core
        pygame.draw.lines(surf, (255, 250, 220, 230), False, points, 2)
        # warm halo
        pygame.draw.lines(surf, (255, 200,  80, 110), False, points, 4)
    return surf


# Variant 4 — vortex (3 rings + rotating polar spiral inside)
def draw_vortex(t_pulse):
    surf, cx, cy = _new_field_surf()
    rad = MEGAMAGNET_RADIUS

    BREATH = 0.30
    s_outer = math.sin(t_pulse + 0.0)
    u_outer = (s_outer + 1) / 2
    outer_factor = 1.0 - BREATH * (1.0 - u_outer)
    glow_rad = rad * outer_factor
    _inner_glow(surf, cx, cy, glow_rad, (245, 175, 40))

    # 5 spiral arms, each a sequence of dots from centre outward,
    # twisted by an exponential factor so the arms curl in.
    ARMS = 5
    rot = t_pulse * 0.6
    for k in range(ARMS):
        base_ang = (k / ARMS) * math.tau + rot
        for s_i in range(40):
            t = s_i / 39
            r = t * rad * 0.92
            twist = base_ang + t * 2.4
            px = cx + math.cos(twist) * r
            py = cy + math.sin(twist) * r
            # Brighter near outer arc, fading inward.
            a = int(40 + 180 * t)
            col = (255, 215, 90)
            pygame.draw.circle(surf, (*col, a), (int(px), int(py)), 2)

    for rfac, phase, alpha, width, breath_scale, ring_col in (
            (1.00, 0.0, 180, 3, 1.00, (255, 220, 100)),
            (0.78, 0.6, 140, 2, 0.85, (255, 195,  60)),
            (0.55, 1.2, 100, 2, 0.70, (235, 165,  35))):
        amp = BREATH * breath_scale
        s = math.sin(t_pulse + phase)
        u = (s + 1) / 2
        rr = int(rad * rfac * (1.0 - amp * (1.0 - u)))
        _aa_ring(surf, cx, cy, rr, width, ring_col, alpha)
    return surf


# Variant 5 — hex shield (3 rings + procedural hex grid overlay)
def draw_hex_shield(t_pulse):
    surf, cx, cy = _new_field_surf()
    rad = MEGAMAGNET_RADIUS

    BREATH = 0.30
    s_outer = math.sin(t_pulse + 0.0)
    u_outer = (s_outer + 1) / 2
    outer_factor = 1.0 - BREATH * (1.0 - u_outer)
    glow_rad = rad * outer_factor
    _inner_glow(surf, cx, cy, glow_rad, (245, 175, 40))

    # Honeycomb grid. Hex with flat-top orientation, cell radius 14 px.
    # Cells dim sharply toward the centre so the bird is the focal
    # point; cells outside MEGAMAGNET_RADIUS are clipped.
    hex_r = 14
    hex_w = hex_r * math.sqrt(3)
    hex_h = hex_r * 1.5
    rows = int(rad * 2 / hex_h) + 3
    cols = int(rad * 2 / hex_w) + 3
    for ri in range(-rows // 2, rows // 2 + 1):
        for ci in range(-cols // 2, cols // 2 + 1):
            hx = cx + ci * hex_w + (hex_w / 2 if ri % 2 else 0)
            hy = cy + ri * hex_h
            dx = hx - cx
            dy = hy - cy
            d = math.hypot(dx, dy)
            if d > rad * 0.92:
                continue
            # Edge-emphasis falloff: dim hub, bright rim.
            falloff = d / rad
            a = int(160 * (falloff ** 1.5))
            if a < 12:
                continue
            verts = []
            for v in range(6):
                ang = math.tau * v / 6 + math.pi / 6
                verts.append((hx + math.cos(ang) * hex_r,
                              hy + math.sin(ang) * hex_r))
            pygame.draw.polygon(surf, (255, 215, 100, a), verts, 1)

    for rfac, phase, alpha, width, breath_scale, ring_col in (
            (1.00, 0.0, 200, 3, 1.00, (255, 220, 100)),
            (0.78, 0.6, 150, 2, 0.85, (255, 195,  60)),
            (0.55, 1.2, 110, 2, 0.70, (235, 165,  35))):
        amp = BREATH * breath_scale
        s = math.sin(t_pulse + phase)
        u = (s + 1) / 2
        rr = int(rad * rfac * (1.0 - amp * (1.0 - u)))
        _aa_ring(surf, cx, cy, rr, width, ring_col, alpha)
    return surf


VARIANTS = (
    ("01_dense_rings", draw_dense_rings),
    ("02_chromatic",   draw_chromatic),
    ("03_arcs",        draw_arcs),
    ("04_vortex",      draw_vortex),
    ("05_hex_shield",  draw_hex_shield),
)


def main():
    # Centred bird so the doubled-radius field doesn't clip on the
    # left edge of the canvas; in-game bird sits further left, but
    # the snapshot's job is to show the field at native scale.
    bird = Bird()
    bird.x = W // 2
    bird.y = 280

    # 12 coins arranged in two staggered rings inside the doubled
    # radius so the wider pull area reads visually.
    coin_positions = []
    inner_r = MEGAMAGNET_RADIUS * 0.42
    outer_r = MEGAMAGNET_RADIUS * 0.78
    for i in range(7):
        a = (i / 7) * math.tau + 0.3
        coin_positions.append((
            bird.x + math.cos(a) * outer_r,
            bird.y + math.sin(a) * outer_r,
        ))
    for i in range(5):
        a = (i / 5) * math.tau
        coin_positions.append((
            bird.x + math.cos(a) * inner_r,
            bird.y + math.sin(a) * inner_r,
        ))

    # Mid-pulse phase chosen so the rings sit cleanly between
    # contracted and expanded — same value used by snapshot_magnet_field.py.
    t_pulse = 0.18 * 5.5

    rendered = []
    for name, draw_fn in VARIANTS:
        screen = pygame.Surface((W, H))
        draw_bg(screen)

        coins = [Coin(cx, cy) for cx, cy in coin_positions]
        for i, c in enumerate(coins):
            c.spin = i * 0.5
        for c in coins:
            c.draw(screen)

        bird.draw(screen, 0, 0)

        field = draw_fn(t_pulse)
        rad = MEGAMAGNET_RADIUS
        screen.blit(field, (int(bird.x) - (rad + 4),
                            int(bird.y) - (rad + 4)))

        out_path = os.path.join(OUT_DIR, f"variant_{name}.png")
        pygame.image.save(screen, out_path)
        print(f"saved {out_path}")
        rendered.append((name, screen))

    _write_combined_sheet(rendered)


def _write_combined_sheet(rendered):
    """3-column / 2-row comparison sheet. Bottom row has 2 cells
    centred, since 5 variants leave one cell empty."""
    cell_label_h = 36
    pad = 16
    margin = 24
    header_h = 56

    cell_w, cell_h = W, H + cell_label_h
    cols, rows = 3, 2
    sheet_w = cols * cell_w + (cols - 1) * pad + 2 * margin
    sheet_h = header_h + rows * cell_h + (rows - 1) * pad + 2 * margin

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 22, 28))

    title_font = pygame.font.SysFont(None, 30, bold=True)
    label_font = pygame.font.SysFont(None, 26, bold=True)

    title = title_font.render(
        "Megamagnet force-field — 5 design variants (2x magnet radius)",
        True, (240, 240, 245))
    sheet.blit(title, (margin, margin + 6))

    positions = (
        (0, 0), (1, 0), (2, 0),
        (0, 1), (1, 1),
    )
    for (name, surf), (col, row) in zip(rendered, positions):
        # Centre the 2-cell bottom row.
        if row == 1:
            col_offset = (cols - 2) / 2  # 0.5 → half-cell shift right
            x = int(margin + (col + col_offset) * (cell_w + pad))
        else:
            x = margin + col * (cell_w + pad)
        y = margin + header_h + row * (cell_h + pad)

        # Label strip.
        pygame.draw.rect(sheet, (40, 40, 50),
                         (x, y, cell_w, cell_label_h))
        pretty = name.split("_", 1)[1].replace("_", " ").title()
        idx = name.split("_", 1)[0]
        lbl = label_font.render(f"#{idx}  {pretty}", True, (250, 220, 130))
        sheet.blit(lbl, (x + 12, y + 6))

        # Variant image below label.
        sheet.blit(surf, (x, y + cell_label_h))

    out_path = os.path.join(OUT_DIR, "all_variants.png")
    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
