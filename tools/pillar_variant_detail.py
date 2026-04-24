"""
Render ONE enriched pillar variant at a larger scale for detail review.

Usage:
    python tools/pillar_variant_detail.py 3

Outputs:
    docs/sketches/pillar_variant_<N>.png   (600x820)
"""
import os, math, random, sys, pathlib
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import pygame

from game.draw import (
    get_stone_pillar_body,
    silhouette_bottom_spire, silhouette_top_spire, silhouette_blit,
    draw_wuling_pine, draw_moss_strand, draw_side_shrub, draw_pillar_mist,
)

# ── Canvas ───────────────────────────────────────────────────────────────────
W, H = 600, 820
TOP_H = 260
GAP_H = 220
BOT_TOP = TOP_H + GAP_H
GROUND_Y = H - 40
PILLAR_W = 170
CX = W // 2

FOLIAGE = dict(
    foliage_top=(140, 220, 110),
    foliage_mid=(70, 170, 75),
    foliage_dark=(30, 100, 50),
    foliage_accent=(255, 240, 120),
)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ── Dusk background (warmer, lanterns pop) ───────────────────────────────────

def paint_bg_dusk(surf):
    top, mid, bot = (30, 40, 90), (130, 110, 150), (255, 180, 130)
    for y in range(H):
        t = y / (H - 1)
        c = lerp(top, mid, t / 0.55) if t < 0.55 else lerp(mid, bot, (t - 0.55) / 0.45)
        pygame.draw.line(surf, c, (0, y), (W - 1, y))
    # warm horizon glow
    glow = pygame.Surface((W, 120), pygame.SRCALPHA)
    for y in range(120):
        a = int(140 * (1 - y / 119))
        pygame.draw.line(glow, (255, 210, 150, a), (0, y), (W - 1, y))
    surf.blit(glow, (0, GROUND_Y - 120))
    # distant ridges
    pts = [(0, GROUND_Y)]
    for x in range(0, W + 1, 8):
        h = int(70 + math.sin(x * 0.013) * 26 + math.sin(x * 0.05) * 10)
        pts.append((x, GROUND_Y - h))
    pts.append((W, GROUND_Y))
    pygame.draw.polygon(surf, (70, 75, 120), pts)
    # ground
    for y in range(GROUND_Y, H):
        t = (y - GROUND_Y) / max(1, H - GROUND_Y - 1)
        pygame.draw.line(surf, lerp((60, 100, 60), (35, 55, 35), t), (0, y), (W - 1, y))


# ── Decoration helpers ───────────────────────────────────────────────────────

def draw_paper_lantern(surf, hang_x, hang_y, strand_len=16, scale=1.0):
    pygame.draw.line(surf, (40, 30, 25), (hang_x, hang_y), (hang_x, hang_y + strand_len), 1)
    cx = hang_x
    cy = hang_y + strand_len
    lw = max(8, int(18 * scale))
    lh = max(10, int(22 * scale))
    cap = max(2, int(3 * scale))
    pygame.draw.rect(surf, (55, 35, 25), (cx - lw // 2 + 1, cy, lw - 2, cap))
    pygame.draw.rect(surf, (55, 35, 25), (cx - lw // 2 + 1, cy + lh - cap, lw - 2, cap))
    body = pygame.Rect(cx - lw // 2, cy + cap - 1, lw, lh - 2 * cap + 2)
    pygame.draw.ellipse(surf, (170, 30, 35), body)
    pygame.draw.ellipse(surf, (230, 80, 65), body.inflate(-max(2, int(4 * scale)), -max(1, int(3 * scale))))
    rib_dx = max(2, int(4 * scale))
    pygame.draw.line(surf, (130, 20, 25),
                     (cx - rib_dx, cy + cap), (cx - rib_dx, cy + lh - cap - 1), 1)
    pygame.draw.line(surf, (130, 20, 25),
                     (cx + rib_dx, cy + cap), (cx + rib_dx, cy + lh - cap - 1), 1)
    # glow
    gsz = max(8, int(24 * scale))
    glow = pygame.Surface((gsz * 2, gsz * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 215, 120, 110), (gsz, gsz), int(gsz * 0.55))
    pygame.draw.circle(glow, (255, 240, 200, 180), (gsz, gsz), max(2, int(gsz * 0.28)))
    surf.blit(glow, (cx - gsz, cy + lh // 2 - gsz))
    # tassel
    pygame.draw.line(surf, (200, 160, 40), (cx, cy + lh), (cx, cy + lh + max(3, int(5 * scale))), 1)
    pygame.draw.circle(surf, (220, 180, 60), (cx, cy + lh + max(4, int(6 * scale))), max(1, int(2 * scale)))


def draw_lantern_string(surf, x1, y1, x2, y2, n=3):
    """Sagging cord between two anchor points, with n small lanterns along it."""
    mx = (x1 + x2) // 2
    my = max(y1, y2) + 14
    steps = 30
    pts = []
    for i in range(steps + 1):
        t = i / steps
        bx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2
        by = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2
        pts.append((int(bx), int(by)))
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, (45, 30, 20), pts[i], pts[i + 1], 1)
    for i in range(n):
        t = (i + 1) / (n + 1)
        idx = int(t * steps)
        lx, ly = pts[idx]
        draw_paper_lantern(surf, lx, ly, strand_len=3, scale=0.55)


def draw_ledge_lantern(surf, x, y):
    """Small lantern sitting atop a short wooden post on a ledge."""
    pygame.draw.rect(surf, (70, 50, 35), (x - 1, y - 14, 2, 14))
    pygame.draw.circle(surf, (80, 55, 40), (x, y - 14), 3)
    lw, lh = 11, 14
    pygame.draw.rect(surf, (55, 35, 25), (x - lw // 2 + 1, y - 14 - lh, lw - 2, 2))
    pygame.draw.rect(surf, (55, 35, 25), (x - lw // 2 + 1, y - 14 - 2, lw - 2, 2))
    body = pygame.Rect(x - lw // 2, y - 14 - lh + 2, lw, lh - 4)
    pygame.draw.ellipse(surf, (175, 35, 40), body)
    pygame.draw.ellipse(surf, (235, 110, 80), body.inflate(-4, -3))
    glow = pygame.Surface((26, 26), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 220, 140, 110), (13, 13), 11)
    pygame.draw.circle(glow, (255, 245, 210, 190), (13, 13), 4)
    gcy = y - 14 - lh + 2 + (lh - 4) // 2
    surf.blit(glow, (x - 13, gcy - 13))


def draw_firefly(surf, cx, cy):
    g = pygame.Surface((24, 24), pygame.SRCALPHA)
    pygame.draw.circle(g, (255, 230, 120, 70), (12, 12), 11)
    pygame.draw.circle(g, (255, 245, 180, 150), (12, 12), 6)
    pygame.draw.circle(g, (255, 255, 230, 255), (12, 12), 2)
    surf.blit(g, (cx - 12, cy - 12))


def draw_moth(surf, cx, cy):
    pygame.draw.polygon(surf, (210, 195, 170),
                        [(cx, cy), (cx - 5, cy - 3), (cx - 6, cy + 1)])
    pygame.draw.polygon(surf, (230, 215, 190),
                        [(cx, cy), (cx + 5, cy - 3), (cx + 6, cy + 1)])
    pygame.draw.line(surf, (70, 55, 45), (cx, cy - 1), (cx, cy + 3), 1)


def draw_grass_tuft(surf, cx, cy, palette, seed=0):
    rng = random.Random(seed)
    mid = palette['foliage_mid']
    top = palette['foliage_top']
    for i in range(5):
        dx = -4 + i * 2
        tip_y = cy - 4 - rng.randint(0, 3)
        lean = rng.randint(-2, 2)
        pygame.draw.line(surf, mid, (cx + dx, cy), (cx + dx + lean, tip_y), 1)
    pygame.draw.line(surf, top, (cx, cy), (cx, cy - 6), 1)


def draw_pom_pom_vine(surf, x, y, length, palette, seed=0):
    rng = random.Random(seed)
    dark = palette['foliage_dark']
    mid = palette['foliage_mid']
    top = palette['foliage_top']
    pts = []
    for i in range(length):
        t = i / max(1, length - 1)
        off = int(math.sin(t * 3.6 + seed) * 3)
        pts.append((x + off, y + i))
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, dark, pts[i], pts[i + 1], 1)
    for i, frac in enumerate((0.28, 0.58, 0.86)):
        idx = int(frac * (len(pts) - 1))
        px, py = pts[idx]
        r = 4 if i == 1 else 3
        pygame.draw.circle(surf, dark, (px, py), r + 1)
        pygame.draw.circle(surf, mid, (px, py), r)
        pygame.draw.circle(surf, top, (px - 1, py - 1), max(1, r - 2))


def draw_flower_shrub(surf, x, y, palette, scale=1.0, seed=0):
    draw_side_shrub(surf, x, y, palette, scale=scale)
    rng = random.Random(seed)
    n = int(9 * scale)
    for _ in range(n):
        dx = rng.randint(-int(15 * scale), int(15 * scale))
        dy = rng.randint(-int(12 * scale), 0)
        col = rng.choice([(255, 235, 100), (255, 255, 245), (255, 205, 110), (255, 180, 200)])
        pygame.draw.circle(surf, col, (x + dx, y + dy), rng.choice([1, 2]))


# ── Variant 3: Lantern Ledge ─────────────────────────────────────────────────

STONE_V3 = dict(
    light=(252, 236, 210),
    mid=(208, 180, 145),
    dark=(120, 98, 75),
    accent=(255, 246, 218),
)


def draw_variant_3(surf):
    s = STONE_V3
    palette = dict(FOLIAGE,
                   stone_light=s['light'], stone_mid=s['mid'],
                   stone_dark=s['dark'], stone_accent=s['accent'])

    # ── Top pillar ──
    top_body = get_stone_pillar_body(PILLAR_W, TOP_H,
                                     s['light'], s['mid'], s['dark'], s['accent'],
                                     body_seed=7)
    top_poly = silhouette_top_spire(PILLAR_W, TOP_H)
    silhouette_blit(surf, top_body, top_poly, (CX - PILLAR_W // 2, 0))

    # ── Bottom pillar ──
    bot_h = GROUND_Y - BOT_TOP
    bot_body = get_stone_pillar_body(PILLAR_W, bot_h,
                                     s['light'], s['mid'], s['dark'], s['accent'],
                                     body_seed=8)
    bot_poly = silhouette_bottom_spire(PILLAR_W, bot_h)
    silhouette_blit(surf, bot_body, bot_poly, (CX - PILLAR_W // 2, BOT_TOP))

    peak_x = CX + 6
    peak_y = BOT_TOP

    # ── Vegetation ──
    # Pine (larger) on the peak
    draw_wuling_pine(surf, peak_x, peak_y + 2, 108, palette,
                     lean=10, direction='up', layers=6)
    # 2 flower-blooming shrubs at different ledge heights
    draw_flower_shrub(surf, CX - PILLAR_W // 2 + 22, BOT_TOP + 58,
                      palette, scale=1.5, seed=11)
    draw_flower_shrub(surf, CX + PILLAR_W // 2 - 24, BOT_TOP + 140,
                      palette, scale=1.2, seed=19)
    # Hanging pom-pom vine draped from the top pillar underside
    draw_pom_pom_vine(surf, CX + 42, TOP_H - 10, 82, palette, seed=3)
    # Grass tufts in crevices
    draw_grass_tuft(surf, CX - 44, TOP_H - 20, palette, seed=1)
    draw_grass_tuft(surf, CX + 30, BOT_TOP + 100, palette, seed=2)
    draw_grass_tuft(surf, CX - 40, BOT_TOP + 200, palette, seed=3)
    # Moss strand on the top pillar's underside
    draw_moss_strand(surf, CX - 28, TOP_H - 18, 18, palette, jitter_seed=5)

    # ── Lights: main + string of smaller lanterns + ledge lantern ──
    # Main red paper lantern dangling from top-pillar underside (bigger — hero)
    draw_paper_lantern(surf, CX - 18, TOP_H - 4, strand_len=28, scale=1.5)
    # String of 3 smaller lanterns across the underside
    draw_lantern_string(surf, CX - 68, TOP_H - 2, CX + 56, TOP_H + 2, n=3)
    # Ledge lantern on a mid-face ledge on the bottom pillar
    draw_ledge_lantern(surf, CX - PILLAR_W // 2 + 34, BOT_TOP + 180)

    # ── Night atmosphere: fireflies in the gap + moth near the main lantern ──
    for fx, fy in [(CX - 72, TOP_H + 60), (CX + 70, TOP_H + 120),
                   (CX - 32, TOP_H + 180), (CX + 38, TOP_H + 40),
                   (CX + 86, TOP_H + 200), (CX - 96, TOP_H + 140)]:
        draw_firefly(surf, fx, fy)
    draw_moth(surf, CX + 24, TOP_H + 24)
    draw_moth(surf, CX - 40, TOP_H + 90)

    # Mist halo at the ground
    draw_pillar_mist(surf, CX, GROUND_Y - 4, PILLAR_W, alpha=110)


# ── Label ───────────────────────────────────────────────────────────────────

def label(surf, title, subtitle, title_font, sub_font):
    t_surf = title_font.render(title, True, (18, 18, 26))
    s_surf = sub_font.render(subtitle, True, (60, 60, 74))
    pad = 10
    w = max(t_surf.get_width(), s_surf.get_width()) + pad * 2
    h = t_surf.get_height() + s_surf.get_height() + pad + 4
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill((255, 255, 255, 230))
    surf.blit(bg, (CX - w // 2, 16))
    surf.blit(t_surf, (CX - t_surf.get_width() // 2, 16 + pad // 2))
    surf.blit(s_surf, (CX - s_surf.get_width() // 2,
                       16 + pad // 2 + t_surf.get_height() + 2))


# ── Main ────────────────────────────────────────────────────────────────────

VARIANT_DRAWERS = {
    3: ("3. Lantern Ledge", "pale ivory stone · festival lights at dusk", draw_variant_3),
}


def main():
    try:
        idx = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    except ValueError:
        idx = 3
    if idx not in VARIANT_DRAWERS:
        print(f"variant {idx} not implemented yet; available: {sorted(VARIANT_DRAWERS)}")
        sys.exit(1)

    title, subtitle, drawer = VARIANT_DRAWERS[idx]

    pygame.init()
    surf = pygame.Surface((W, H))
    paint_bg_dusk(surf)
    drawer(surf)
    title_font = pygame.font.SysFont("arial", 22, bold=True)
    sub_font = pygame.font.SysFont("arial", 14)
    label(surf, title, subtitle, title_font, sub_font)

    out = f"/home/user/Claude_test/docs/sketches/pillar_variant_{idx}.png"
    pygame.image.save(surf, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
