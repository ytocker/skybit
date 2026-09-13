"""Side-by-side comparison: hex-shield force-field at magnet radius (82)
and megamagnet radius (164). Design exploration only — does NOT touch
the live game render. Run from repo root:

    python tools/snapshot_magnet_megamagnet_comparison.py

Output: docs/screenshots/powerups/megamagnet/magnet_vs_megamagnet_hex.png
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
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


MEGAMAGNET_RADIUS = MAGNET_RADIUS * 2  # 164 — snapshot-local

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


def draw_hex_field(radius, t_pulse):
    """Hex-shield force-field, parameterized by radius. Lifted verbatim
    from snapshot_megamagnet_variants.draw_hex_shield with the radius
    + hex cell size made parameters. Cell radius scales with the field
    radius so density stays visually consistent at 82 and 164 px."""
    surf = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
    cx, cy = radius + 4, radius + 4

    BREATH = 0.30
    s_outer = math.sin(t_pulse + 0.0)
    u_outer = (s_outer + 1) / 2
    outer_factor = 1.0 - BREATH * (1.0 - u_outer)
    glow_rad = radius * outer_factor

    GLOW_COL = (245, 175, 40)
    for i in range(22, 0, -1):
        r = int(glow_rad * i / 22)
        inner_t = i / 22
        bell = math.exp(-((inner_t - 0.85) ** 2) / 0.15)
        a = int(72 * bell)
        if a > 0:
            pygame.draw.circle(surf, (*GLOW_COL, a), (cx, cy), r)

    # Hex grid scaled to the field radius.
    hex_r = max(5, int(radius * 0.085))
    hex_w = hex_r * math.sqrt(3)
    hex_h = hex_r * 1.5
    rows = int(radius * 2 / hex_h) + 3
    cols = int(radius * 2 / hex_w) + 3
    for ri in range(-rows // 2, rows // 2 + 1):
        for ci in range(-cols // 2, cols // 2 + 1):
            hx = cx + ci * hex_w + (hex_w / 2 if ri % 2 else 0)
            hy = cy + ri * hex_h
            dx = hx - cx
            dy = hy - cy
            d = math.hypot(dx, dy)
            if d > radius * 0.92:
                continue
            falloff = d / radius
            a = int(160 * (falloff ** 1.5))
            if a < 12:
                continue
            verts = []
            for v in range(6):
                ang = math.tau * v / 6 + math.pi / 6
                verts.append((hx + math.cos(ang) * hex_r,
                              hy + math.sin(ang) * hex_r))
            pygame.draw.polygon(surf, (255, 215, 100, a), verts, 1)

    AA_COL = (255, 240, 180)
    for rfac, phase, alpha, width, breath_scale, ring_col in (
            (1.00, 0.0, 200, 3, 1.00, (255, 220, 100)),
            (0.78, 0.6, 150, 2, 0.85, (255, 195,  60)),
            (0.55, 1.2, 110, 2, 0.70, (235, 165,  35))):
        amp = BREATH * breath_scale
        s = math.sin(t_pulse + phase)
        u = (s + 1) / 2
        rr = int(radius * rfac * (1.0 - amp * (1.0 - u)))
        pygame.draw.circle(surf, (*AA_COL, alpha // 3), (cx, cy), rr + 1, width)
        pygame.draw.circle(surf, (*AA_COL, alpha // 3), (cx, cy), rr - 1, width)
        pygame.draw.circle(surf, (*ring_col, alpha), (cx, cy), rr, width)
    return surf


def render_column(radius, coin_count):
    """Render a single 360x640 column with bird centred, coins inside
    the field, and the hex-shield force-field drawn at `radius`."""
    screen = pygame.Surface((W, H))
    draw_bg(screen)

    bird = Bird()
    bird.x = W // 2
    bird.y = 280

    # Coins arranged inside the field radius. For the smaller field
    # (magnet, r=82) a single ring of 6 reads cleanly; for the bigger
    # field (megamagnet, r=164) two staggered rings show off the
    # extra area.
    coins = []
    if coin_count <= 7:
        coin_r = radius * 0.62
        for i in range(coin_count):
            a = (i / coin_count) * math.tau + 0.4
            coins.append(Coin(bird.x + math.cos(a) * coin_r,
                              bird.y + math.sin(a) * coin_r))
    else:
        outer_r = radius * 0.78
        inner_r = radius * 0.42
        for i in range(7):
            a = (i / 7) * math.tau + 0.3
            coins.append(Coin(bird.x + math.cos(a) * outer_r,
                              bird.y + math.sin(a) * outer_r))
        for i in range(coin_count - 7):
            a = (i / (coin_count - 7)) * math.tau
            coins.append(Coin(bird.x + math.cos(a) * inner_r,
                              bird.y + math.sin(a) * inner_r))
    for i, c in enumerate(coins):
        c.spin = i * 0.5
    for c in coins:
        c.draw(screen)

    bird.draw(screen, 0, 0)

    t_pulse = 0.18 * 5.5
    field = draw_hex_field(radius, t_pulse)
    screen.blit(field, (int(bird.x) - (radius + 4),
                        int(bird.y) - (radius + 4)))
    return screen


def main():
    magnet_col = render_column(MAGNET_RADIUS, coin_count=6)
    mega_col = render_column(MEGAMAGNET_RADIUS, coin_count=12)

    margin = 24
    header_h = 56
    label_h = 36
    col_gap = 20
    sheet_w = 2 * W + col_gap + 2 * margin
    sheet_h = header_h + label_h + H + 2 * margin

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 22, 28))

    title_font = pygame.font.SysFont(None, 30, bold=True)
    label_font = pygame.font.SysFont(None, 26, bold=True)

    title = title_font.render(
        "Hex shield — magnet (r=82) vs megamagnet (r=164)",
        True, (240, 240, 245))
    sheet.blit(title, (margin, margin + 8))

    for col_idx, (label_text, col_surf) in enumerate((
            ("Magnet  ·  radius 82",     magnet_col),
            ("Megamagnet  ·  radius 164", mega_col))):
        x = margin + col_idx * (W + col_gap)
        y = margin + header_h
        pygame.draw.rect(sheet, (40, 40, 50), (x, y, W, label_h))
        lbl = label_font.render(label_text, True, (250, 220, 130))
        sheet.blit(lbl, (x + 12, y + 6))
        sheet.blit(col_surf, (x, y + label_h))

    out_path = os.path.join(OUT_DIR, "magnet_vs_megamagnet_hex.png")
    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
