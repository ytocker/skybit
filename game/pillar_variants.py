"""
Pillar visual variants (7 styles selected from the sketch options).

Each Pipe picks a variant deterministically from its seed. Silhouettes and
decorations are visual-only; collision stays axis-aligned via Pipe.top_rect
and Pipe.bot_rect. Stone palette and foliage are biome-tinted by the caller.
"""
import math, random
import pygame

from game.draw import (
    get_stone_pillar_body,
    silhouette_top_spire, silhouette_bottom_spire, silhouette_blit,
    draw_wuling_pine, draw_moss_strand, draw_side_shrub,
)


# ── Bottom-pillar silhouette shapes ─────────────────────────────────────────

def sil_bot_stout(w, h):
    return [(0, 0), (w, 0), (int(w * 0.94), int(h * 0.20)),
            (int(w * 0.90), int(h * 0.50)), (int(w * 0.86), int(h * 0.80)),
            (int(w * 0.80), h), (int(w * 0.20), h),
            (int(w * 0.14), int(h * 0.80)), (int(w * 0.10), int(h * 0.50)),
            (int(w * 0.06), int(h * 0.20))]


def sil_bot_slender(w, h):
    return [(0, 0), (w, 0), (int(w * 0.80), int(h * 0.25)),
            (int(w * 0.74), int(h * 0.60)), (int(w * 0.66), int(h * 0.85)),
            (int(w * 0.60), h), (int(w * 0.40), h),
            (int(w * 0.34), int(h * 0.85)), (int(w * 0.26), int(h * 0.60)),
            (int(w * 0.20), int(h * 0.25))]


def sil_bot_lean(w, h):
    lean = int(w * 0.06)
    return [(lean, 0), (w, 0), (int(w * 0.92), int(h * 0.25)),
            (int(w * 0.88), int(h * 0.55)), (int(w * 0.82), int(h * 0.82)),
            (int(w * 0.78), h), (int(w * 0.22), h),
            (int(w * 0.12) - lean, int(h * 0.82)), (int(w * 0.06) - lean, int(h * 0.55)),
            (int(w * 0.00), int(h * 0.25))]


def sil_bot_shelf(w, h):
    return [(0, 0), (w, 0), (int(w * 0.92), int(h * 0.22)),
            (int(w * 0.86), int(h * 0.50)), (int(w * 0.82), int(h * 0.62)),
            (int(w * 0.96), int(h * 0.66)), (int(w * 0.88), int(h * 0.85)),
            (int(w * 0.80), h), (int(w * 0.20), h),
            (int(w * 0.12), int(h * 0.85)), (int(w * 0.04), int(h * 0.66)),
            (int(w * 0.18), int(h * 0.62)), (int(w * 0.14), int(h * 0.50)),
            (int(w * 0.08), int(h * 0.22))]


def sil_bot_eroded(w, h):
    return [(0, 0), (w, 0), (int(w * 0.96), int(h * 0.18)),
            (int(w * 0.88), int(h * 0.40)), (w, int(h * 0.55)),
            (int(w * 0.92), int(h * 0.68)), (int(w * 0.84), int(h * 0.82)),
            (int(w * 0.78), h), (int(w * 0.22), h),
            (int(w * 0.14), int(h * 0.82)), (int(w * 0.08), int(h * 0.68)),
            (0, int(h * 0.55)), (int(w * 0.10), int(h * 0.40)),
            (int(w * 0.04), int(h * 0.18))]


def sil_bot_blunt(w, h):
    return [(0, 0), (w, 0), (w, int(h * 0.18)),
            (int(w * 0.94), int(h * 0.45)), (int(w * 0.90), int(h * 0.75)),
            (int(w * 0.82), h), (int(w * 0.18), h),
            (int(w * 0.10), int(h * 0.75)), (int(w * 0.06), int(h * 0.45)),
            (0, int(h * 0.18))]


# ── Density vegetation helpers ──────────────────────────────────────────────

def draw_moss_patch(surf, cx, cy, w, h, palette, seed=0):
    rng = random.Random(seed)
    dark, mid, top = palette['foliage_dark'], palette['foliage_mid'], palette['foliage_top']
    for _ in range(max(5, (w * h) // 80)):
        dx = rng.randint(-w // 2, w // 2)
        dy = rng.randint(-h // 2, h // 2)
        r = rng.randint(2, 5)
        pygame.draw.circle(surf, dark, (cx + dx, cy + dy), r + 1)
        pygame.draw.circle(surf, mid, (cx + dx, cy + dy), r)
        pygame.draw.circle(surf, top, (cx + dx - 1, cy + dy - 1), max(1, r - 2))


def draw_fern_cluster(surf, cx, cy, n, palette, seed=0):
    rng = random.Random(seed)
    dark, mid, top = palette['foliage_dark'], palette['foliage_mid'], palette['foliage_top']
    for i in range(n):
        dx = (i - n // 2) * 3 + rng.randint(-1, 1)
        lean = rng.randint(-3, 3)
        length = rng.randint(8, 14)
        stem_bot = (cx + dx, cy)
        stem_top = (cx + dx + lean, cy - length)
        pygame.draw.line(surf, dark, stem_bot, stem_top, 2)
        for j in range(1, 4):
            t = j / 4
            px = int(stem_bot[0] + (stem_top[0] - stem_bot[0]) * t)
            py = int(stem_bot[1] + (stem_top[1] - stem_bot[1]) * t)
            plen = 3 - j // 2
            pygame.draw.line(surf, mid, (px, py), (px - plen, py - 1), 1)
            pygame.draw.line(surf, mid, (px, py), (px + plen, py - 1), 1)


def draw_climbing_vine(surf, x, y_top, y_bot, palette, seed=0):
    dark, mid, top = palette['foliage_dark'], palette['foliage_mid'], palette['foliage_top']
    for i in range(y_bot - y_top):
        wob = int(math.sin((i + seed) * 0.16) * 2)
        px = x + wob
        py = y_top + i
        pygame.draw.line(surf, dark, (px, py), (px + 1, py), 2)
        if i % 6 == 0:
            side = 1 if (i // 6) % 2 == 0 else -1
            leaf_x = px + side * 3
            pygame.draw.ellipse(surf, dark, (leaf_x - 2, py - 1, 4, 3))
            pygame.draw.ellipse(surf, mid, (leaf_x - 1, py, 2, 2))


def draw_grass_bed(surf, cx, cy, width, density, palette, seed=0):
    rng = random.Random(seed)
    mid, top = palette['foliage_mid'], palette['foliage_top']
    for _ in range(density):
        dx = rng.randint(-width // 2, width // 2)
        h = rng.randint(3, 7)
        lean = rng.randint(-2, 2)
        pygame.draw.line(surf, mid, (cx + dx, cy), (cx + dx + lean, cy - h), 1)
        pygame.draw.line(surf, top, (cx + dx, cy), (cx + dx + lean, cy - h + 1), 1)


def draw_flower_bed(surf, cx, cy, width, n, seed=0):
    rng = random.Random(seed)
    cols = [(255, 230, 100), (250, 250, 240), (255, 180, 200), (200, 120, 230), (255, 140, 80)]
    for _ in range(n):
        dx = rng.randint(-width // 2, width // 2)
        dy = rng.randint(-3, 1)
        pygame.draw.circle(surf, rng.choice(cols), (cx + dx, cy + dy), rng.choice([1, 2]))


def draw_ground_ferns(surf, cx, cy, width, n, palette, seed=0):
    rng = random.Random(seed)
    for i in range(n):
        dx = rng.randint(-width // 2, width // 2)
        draw_fern_cluster(surf, cx + dx, cy, rng.randint(4, 6), palette, seed + i)


def draw_pine_trio(surf, peak_x, peak_y, palette, seed=0):
    draw_wuling_pine(surf, peak_x, peak_y + 2, 58, palette, lean=10, layers=6)
    draw_wuling_pine(surf, peak_x - 14, peak_y + 18, 38, palette, lean=-6, layers=5)
    draw_wuling_pine(surf, peak_x + 12, peak_y + 30, 28, palette, lean=6, layers=4)


# ── Ornament helpers ────────────────────────────────────────────────────────

_FLAG_COLORS = [(70, 140, 230), (245, 245, 245), (230, 70, 70), (80, 180, 90), (245, 210, 70)]


def draw_prayer_flags(surf, x1, y1, x2, y2, n=7):
    mx, my = (x1 + x2) // 2, max(y1, y2) + 14
    steps = 30
    pts = []
    for i in range(steps + 1):
        t = i / steps
        bx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2
        by = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2
        pts.append((int(bx), int(by)))
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, (90, 70, 55), pts[i], pts[i + 1], 1)
    for i in range(n):
        px, py = pts[int((i + 0.5) / n * steps)]
        pygame.draw.rect(surf, _FLAG_COLORS[i % 5], (px - 3, py, 6, 8))
        pygame.draw.rect(surf, (40, 30, 20), (px - 3, py, 6, 8), 1)


def draw_cairn(surf, cx, base_y, n=3, pennant=False):
    sizes = [(16, 7), (12, 5), (8, 4), (6, 3)][:n]
    cols = [(130, 115, 95), (165, 145, 120), (190, 170, 140), (210, 190, 155)]
    y = base_y
    for (w, h), col in zip(sizes, cols):
        pygame.draw.ellipse(surf, (60, 45, 35), pygame.Rect(cx - w // 2, y - h, w, h).inflate(2, 1))
        pygame.draw.ellipse(surf, col, (cx - w // 2, y - h, w, h))
        y -= h - 1
    if pennant:
        pygame.draw.line(surf, (60, 45, 30), (cx, y), (cx, y - 10), 1)
        pygame.draw.polygon(surf, (200, 40, 45), [(cx, y - 10), (cx + 7, y - 8), (cx, y - 6)])


def draw_darchog_pole(surf, cx, base_y, height, banner_color):
    top = base_y - height
    pygame.draw.line(surf, (60, 45, 30), (cx, base_y), (cx, top), 2)
    pygame.draw.circle(surf, (220, 180, 60), (cx, top), 2)
    bw = 8
    pts = [(cx, top + 3), (cx + bw, top + 5),
           (cx + bw + 1, base_y - 4), (cx - 1, base_y - 6)]
    pygame.draw.polygon(surf, banner_color, pts)
    pygame.draw.polygon(surf, (130, 60, 20), pts, 1)


def draw_stupa(surf, cx, base_y):
    pygame.draw.rect(surf, (240, 235, 225), (cx - 7, base_y - 5, 14, 5))
    pygame.draw.ellipse(surf, (245, 240, 230), (cx - 6, base_y - 13, 12, 10))
    pygame.draw.rect(surf, (240, 235, 225), (cx - 2, base_y - 18, 4, 5))
    pygame.draw.polygon(surf, (220, 180, 60), [(cx, base_y - 22), (cx - 3, base_y - 18), (cx + 3, base_y - 18)])


def draw_incense_smoke(surf, x, y, length=20):
    for i in range(length):
        t = i / max(1, length)
        off = int(math.sin(t * 6) * 2)
        a = int(140 * (1 - t))
        s = pygame.Surface((4, 2), pygame.SRCALPHA)
        s.fill((230, 230, 230, a))
        surf.blit(s, (x + off - 2, y - i))


def draw_bird_sil(surf, cx, cy, size=5):
    col = (45, 40, 55)
    pygame.draw.line(surf, col, (cx - size, cy + size // 2), (cx, cy - size // 3), 2)
    pygame.draw.line(surf, col, (cx, cy - size // 3), (cx + size, cy + size // 2), 2)


def draw_raven(surf, cx, cy):
    pygame.draw.ellipse(surf, (25, 25, 35), (cx - 4, cy - 3, 9, 5))
    pygame.draw.circle(surf, (20, 20, 30), (cx + 4, cy - 4), 3)
    pygame.draw.polygon(surf, (40, 35, 25), [(cx + 7, cy - 4), (cx + 10, cy - 3), (cx + 7, cy - 2)])


_LANTERN_COLORS = {
    'red':  ((170, 30, 35),  (230, 80, 65)),
    'gold': ((190, 140, 40), (245, 210, 100)),
}


def draw_paper_lantern(surf, x, y, strand=14, scale=1.0, color='red'):
    dark, light = _LANTERN_COLORS.get(color, _LANTERN_COLORS['red'])
    pygame.draw.line(surf, (40, 30, 25), (x, y), (x, y + strand), 1)
    cy = y + strand
    lw, lh = max(7, int(14 * scale)), max(9, int(18 * scale))
    cap = max(2, int(3 * scale))
    pygame.draw.rect(surf, (55, 35, 25), (x - lw // 2 + 1, cy, lw - 2, cap))
    pygame.draw.rect(surf, (55, 35, 25), (x - lw // 2 + 1, cy + lh - cap, lw - 2, cap))
    body = pygame.Rect(x - lw // 2, cy + cap - 1, lw, lh - 2 * cap + 2)
    pygame.draw.ellipse(surf, dark, body)
    pygame.draw.ellipse(surf, light, body.inflate(-max(2, int(3 * scale)), -max(1, int(2 * scale))))
    gsz = max(6, int(18 * scale))
    g = pygame.Surface((gsz * 2, gsz * 2), pygame.SRCALPHA)
    pygame.draw.circle(g, (255, 215, 120, 100), (gsz, gsz), int(gsz * 0.55))
    pygame.draw.circle(g, (255, 240, 200, 170), (gsz, gsz), max(2, int(gsz * 0.28)))
    surf.blit(g, (x - gsz, cy + lh // 2 - gsz))


def draw_terrace_wall(surf, cx, y, width=36):
    pygame.draw.rect(surf, (130, 105, 75), (cx - width // 2, y - 4, width, 4))
    pygame.draw.rect(surf, (170, 140, 105), (cx - width // 2, y - 4, width, 2))
    for i in range(1, 4):
        x = cx - width // 2 + i * (width // 4)
        pygame.draw.line(surf, (80, 60, 45), (x, y - 4), (x, y - 1), 1)


def draw_cascading_vine(surf, x, y, length, palette):
    dark, mid, top = palette['foliage_dark'], palette['foliage_mid'], palette['foliage_top']
    for i in range(length):
        t = i / max(1, length - 1)
        off = int(math.sin(t * 4) * 2)
        pygame.draw.line(surf, dark, (x + off, y + i), (x + off, y + i + 1), 2)
    for frac, r in ((0.25, 3), (0.55, 4), (0.85, 4)):
        py = y + int(frac * length)
        px = x + int(math.sin(frac * 4) * 2)
        pygame.draw.circle(surf, dark, (px, py), r + 1)
        pygame.draw.circle(surf, mid, (px, py), r)
        pygame.draw.circle(surf, top, (px - 1, py - 1), max(1, r - 2))
        pygame.draw.circle(surf, (255, 180, 120), (px + 1, py + 1), 1)


def draw_ladder(surf, x, top_y, bot_y):
    pygame.draw.line(surf, (110, 75, 45), (x - 1, top_y), (x + 3, bot_y), 2)
    pygame.draw.line(surf, (110, 75, 45), (x + 5, top_y), (x + 9, bot_y), 2)
    rungs = max(3, (bot_y - top_y) // 7)
    for i in range(1, rungs):
        t = i / rungs
        ry = int(top_y + (bot_y - top_y) * t)
        pygame.draw.line(surf, (130, 90, 55),
                         (x - 1 + int(4 * t), ry), (x + 5 + int(4 * t), ry), 1)


def draw_monastery(surf, cx, base_y):
    body = pygame.Rect(cx - 11, base_y - 22, 22, 22)
    pygame.draw.rect(surf, (245, 240, 230), body)
    pygame.draw.rect(surf, (80, 60, 45), body, 1)
    pygame.draw.polygon(surf, (170, 60, 45),
                        [(cx - 14, base_y - 22), (cx + 14, base_y - 22),
                         (cx + 10, base_y - 28), (cx - 10, base_y - 28)])
    pygame.draw.polygon(surf, (110, 40, 30),
                        [(cx - 14, base_y - 22), (cx + 14, base_y - 22),
                         (cx + 10, base_y - 28), (cx - 10, base_y - 28)], 1)
    for wx in (-5, 2):
        pygame.draw.rect(surf, (255, 210, 120), (cx + wx, base_y - 17, 3, 4))
        pygame.draw.rect(surf, (255, 210, 120), (cx + wx, base_y - 9, 3, 4))
    pygame.draw.line(surf, (80, 60, 45), (cx - 11, base_y - 13), (cx + 11, base_y - 13), 1)
    for i in range(10):
        s = pygame.Surface((3, 2), pygame.SRCALPHA)
        s.fill((230, 230, 230, int(130 * (1 - i / 10))))
        surf.blit(s, (cx + 6 + int(math.sin(i * 0.6) * 2), base_y - 30 - i * 2))


def draw_strangler_fig(surf, x, y_top, y_bot):
    for j in range(4):
        dx = j * 3
        for i in range(y_bot - y_top):
            wob = int(math.sin((i + j * 5) * 0.18) * 3)
            py = y_top + i
            pygame.draw.line(surf, (220, 210, 190), (x + dx + wob, py), (x + dx + wob + 1, py), 1)
    pygame.draw.ellipse(surf, (200, 190, 165), (x - 4, y_bot - 5, 18, 7))


def draw_stone_face(surf, cx, cy):
    pygame.draw.ellipse(surf, (135, 110, 80), (cx - 8, cy - 10, 16, 20))
    pygame.draw.ellipse(surf, (105, 85, 60), (cx - 8, cy - 10, 16, 20), 1)
    pygame.draw.arc(surf, (60, 45, 30), (cx - 6, cy - 3, 4, 3), math.pi, 2 * math.pi, 1)
    pygame.draw.arc(surf, (60, 45, 30), (cx + 2, cy - 3, 4, 3), math.pi, 2 * math.pi, 1)
    pygame.draw.arc(surf, (60, 45, 30), (cx - 3, cy + 2, 6, 3), 0, math.pi, 1)
    for i in range(4):
        pygame.draw.circle(surf, (60, 130, 60), (cx - 7 + i * 4, cy - 9), 2)


def draw_masonry_blocks(surf, cx, y_top, y_bot, pw, seed=0):
    rng = random.Random(seed)
    for _ in range(4):
        bw = rng.randint(8, 14)
        bh = rng.randint(5, 8)
        bx = cx - pw // 2 + rng.randint(4, max(6, pw - bw - 4))
        by = rng.randint(y_top + 6, max(y_top + 8, y_bot - bh - 6))
        pygame.draw.rect(surf, (80, 60, 45), (bx, by, bw, bh))
        pygame.draw.rect(surf, (130, 100, 75), (bx + 1, by + 1, bw - 2, bh - 2))
        pygame.draw.line(surf, (60, 45, 30), (bx + bw // 2, by), (bx + bw // 2, by + bh), 1)


def draw_spiral_glow(surf, cx, cy, radius=10):
    g = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
    pygame.draw.circle(g, (255, 210, 150, 80), (radius * 3 // 2, radius * 3 // 2), radius + 2)
    pygame.draw.circle(g, (255, 230, 180, 150), (radius * 3 // 2, radius * 3 // 2), radius // 2)
    surf.blit(g, (cx - radius * 3 // 2, cy - radius * 3 // 2))
    pts = []
    for i in range(24):
        t = i / 23
        r = radius * (1 - t)
        a = t * 4 * math.pi
        pts.append((cx + int(math.cos(a) * r), cy + int(math.sin(a) * r)))
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, (255, 180, 80), pts[i], pts[i + 1], 1)


def draw_ribbons_tied(surf, cx, cy, n=4, width=12, seed=0):
    rng = random.Random(seed)
    cols = [(170, 90, 40), (140, 30, 50), (70, 110, 50), (200, 160, 90)]
    for i in range(n):
        col = cols[i % len(cols)]
        dx = rng.randint(-width // 2, width // 2)
        ty = cy + rng.randint(-2, 2)
        pygame.draw.rect(surf, col, (cx + dx - 1, ty, 2, 2))
        for j in range(5):
            t = j / 4
            tx = cx + dx + int(math.sin(t * 3 + seed) * 2)
            py = ty + 2 + j * 2
            pygame.draw.rect(surf, col, (tx - 1, py, 2, 2))


# ── Variant decoration scripts ──────────────────────────────────────────────
#
# Each variant receives:
#   surf            target surface
#   top_rect        top pillar axis-aligned rect (y starts at 0)
#   bot_rect        bottom pillar axis-aligned rect
#   palette         full biome palette (stone_* + foliage_* keys)
#   seed            per-pipe deterministic seed
#
# Positions inside the decoration are computed relative to rect y-coords so
# the same variant works across every gap height the game can spawn.


def _veg_pattern_walk(surf, rect, palette, seed, is_top):
    """Original-style distributed vegetation walk along a pillar."""
    pattern = ((32, -1, 'pine_med'), (62, +1, 'moss'), (92, -1, 'pine_small'),
               (122, +1, 'shrub'), (152, -1, 'moss'), (185, +1, 'pine_small'),
               (215, -1, 'shrub'), (248, +1, 'moss'), (282, -1, 'pine_small'),
               (315, +1, 'shrub'), (348, -1, 'moss'))
    rng = random.Random(seed)
    tip_y = rect.bottom if is_top else rect.y
    sign = -1 if is_top else +1
    for offset, side, kind in pattern:
        y = tip_y + sign * offset
        if not (rect.y + 6 < y < rect.bottom - 6):
            break
        if side < 0:
            ax = rect.x + 2
        else:
            ax = rect.x + rect.width - 2
        ledge_w = 12 if kind in ('pine_med', 'shrub') else 9
        ledge_rect = pygame.Rect(ax - (ledge_w if side > 0 else 0), y - 2, ledge_w, 4)
        pygame.draw.ellipse(surf, palette['stone_dark'], ledge_rect.inflate(2, 1))
        pygame.draw.ellipse(surf, palette['stone_light'], ledge_rect.inflate(-2, -1))
        h_wobble = rng.randint(-6, 8)
        lean_jitter = rng.randint(-4, 4)
        if kind == 'pine_med':
            draw_wuling_pine(surf, ax, y - 1, height=24 + h_wobble, palette=palette,
                             lean=side * 5 + lean_jitter, direction='up', layers=4)
        elif kind == 'pine_small':
            draw_wuling_pine(surf, ax, y, height=15 + h_wobble // 2, palette=palette,
                             lean=side * 3 + lean_jitter, direction='up', layers=3)
        elif kind == 'shrub':
            draw_side_shrub(surf, ax, y - 1, palette, scale=0.85 + rng.random() * 0.45)
        elif kind == 'moss':
            draw_moss_strand(surf, ax, y, length=16 + rng.randint(0, 10),
                             palette=palette, jitter_seed=offset + seed)


def decorate_original(surf, top_rect, bot_rect, palette, seed):
    # Preserves the current in-game look exactly.
    top_cx = top_rect.x + top_rect.width // 2
    bot_cx = bot_rect.x + bot_rect.width // 2
    # Hanging pine on top-pillar fang
    draw_wuling_pine(surf, top_cx - 4, top_rect.bottom - 4, height=34,
                     palette=palette, lean=-12, direction='down', layers=4)
    # Peak pine + secondary side pine on bottom pillar
    draw_wuling_pine(surf, bot_cx + 2, bot_rect.y + 2, height=58,
                     palette=palette, lean=14, direction='up', layers=6)
    draw_wuling_pine(surf, bot_rect.x + 6, bot_rect.y + 28, height=26,
                     palette=palette, lean=-5, direction='up', layers=4)
    _veg_pattern_walk(surf, top_rect, palette, seed, is_top=True)
    _veg_pattern_walk(surf, bot_rect, palette, seed, is_top=False)


def decorate_lungta(surf, top_rect, bot_rect, palette, seed):
    tcx = top_rect.x + top_rect.width // 2
    bcx = bot_rect.x + bot_rect.width // 2
    peak_x, peak_y = bcx + 2, bot_rect.y
    draw_pine_trio(surf, peak_x, peak_y, palette, seed=seed)
    # Heavy moss cascade along the top pillar's underside
    for off in range(-22, 24, 4):
        draw_moss_strand(surf, tcx + off, top_rect.bottom - 10,
                         12 + abs(off) % 8, palette, jitter_seed=seed + off)
    if top_rect.height > 60:
        draw_moss_patch(surf, tcx, top_rect.bottom - 34, 28, 10, palette, seed=seed)
    # Side shrubs along the bottom pillar
    if bot_rect.height > 120:
        for i, sc in enumerate((1.0, 0.9, 1.0)):
            y = bot_rect.y + 70 + i * 60
            if y > bot_rect.bottom - 20: break
            side = -1 if i % 2 == 0 else 1
            sx = bcx + side * (bot_rect.width // 2 - 10)
            draw_side_shrub(surf, sx, y, palette, scale=sc)
    # Prayer flag strings across the gap
    draw_prayer_flags(surf, tcx - 28, top_rect.bottom - 48,
                      peak_x + 12, peak_y - 48, n=8)
    if top_rect.height > 80:
        draw_prayer_flags(surf, tcx + 28, top_rect.bottom - 32,
                          peak_x - 4, peak_y - 28, n=5)
    # Peak cairn + base cairn
    draw_cairn(surf, peak_x - 18, peak_y + 4, n=3, pennant=False)
    if bot_rect.height > 80:
        draw_cairn(surf, bcx + bot_rect.width // 2 - 4, bot_rect.bottom - 4,
                   n=3, pennant=True)
    # Climbing vine + ground cover
    if bot_rect.height > 100:
        draw_climbing_vine(surf, bot_rect.x + 8, bot_rect.y + 40,
                           bot_rect.bottom - 16, palette, seed=seed)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 2, bot_rect.width - 10,
                       14, palette, seed=seed)


def decorate_darchog(surf, top_rect, bot_rect, palette, seed):
    tcx = top_rect.x + top_rect.width // 2
    bcx = bot_rect.x + bot_rect.width // 2
    peak_x, peak_y = bcx + 2, bot_rect.y
    draw_pine_trio(surf, peak_x, peak_y, palette, seed=seed)
    # Heavy moss cascade
    for off in range(-20, 22, 4):
        draw_moss_strand(surf, tcx + off, top_rect.bottom - 10,
                         12 + abs(off) % 8, palette, jitter_seed=seed + off)
    # 2 darchog poles on peak (hero + companion)
    draw_darchog_pole(surf, peak_x + 8, peak_y - 4, height=70, banner_color=(200, 90, 40))
    if bot_rect.height > 80:
        draw_darchog_pole(surf, peak_x - 14, peak_y + 8, height=58, banner_color=(180, 40, 60))
    # 2 stupas at base
    if bot_rect.height > 110:
        draw_stupa(surf, bcx - 12, bot_rect.bottom - 4)
        draw_stupa(surf, bcx + 12, bot_rect.bottom - 4)
    # Side shrubs
    if bot_rect.height > 120:
        for i, sc in enumerate((1.0, 0.9, 1.0, 0.8)):
            y = bot_rect.y + 52 + i * 48
            if y > bot_rect.bottom - 20: break
            side = 1 if i % 2 == 0 else -1
            sx = bcx + side * (bot_rect.width // 2 - 10)
            draw_side_shrub(surf, sx, y, palette, scale=sc)
    # Climbing vine + grass
    if bot_rect.height > 100:
        draw_climbing_vine(surf, bot_rect.x + 6, bot_rect.y + 36,
                           bot_rect.bottom - 14, palette, seed=seed + 3)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 2, bot_rect.width - 10,
                       12, palette, seed=seed)
    # Distant bird silhouettes
    for dx, dy in [(-44, 20), (38, 36), (-32, 56)]:
        if tcx + dx > 2 and tcx + dx < tcx * 2 - 2 and dy < top_rect.bottom - 10:
            draw_bird_sil(surf, tcx + dx, dy, size=4)


def decorate_babylon(surf, top_rect, bot_rect, palette, seed):
    tcx = top_rect.x + top_rect.width // 2
    bcx = bot_rect.x + bot_rect.width // 2
    peak_x, peak_y = bcx + 2, bot_rect.y
    # Smaller pine crown + companion
    draw_wuling_pine(surf, peak_x, peak_y + 2, 38, palette, lean=4, layers=4)
    draw_wuling_pine(surf, peak_x - 12, peak_y + 16, 28, palette, lean=-4, layers=3)
    # Terraces at roughly 1/3 and 2/3 of the bottom pillar
    if bot_rect.height > 100:
        for frac in (0.30, 0.58, 0.82):
            ty = int(bot_rect.y + bot_rect.height * frac)
            draw_terrace_wall(surf, bcx, ty, width=min(bot_rect.width - 8, 58))
            # Cascading vines spilling over each terrace
            for vx in (-22, -8, 8, 22):
                vl = int(bot_rect.height * 0.15)
                draw_cascading_vine(surf, bcx + vx, ty + 2, vl, palette)
            # Fern bed on top of the terrace
            draw_ground_ferns(surf, bcx, ty - 2, width=bot_rect.width - 12,
                              n=3, palette=palette, seed=seed + ty)
        # Ladder between two terraces
        top_frac_y = int(bot_rect.y + bot_rect.height * 0.32)
        mid_frac_y = int(bot_rect.y + bot_rect.height * 0.56)
        draw_ladder(surf, bcx + 14, top_frac_y, mid_frac_y)
    # Small pine hanging on top pillar's fang
    draw_wuling_pine(surf, tcx - 4, top_rect.bottom - 4, 28, palette,
                     lean=-10, direction='down', layers=4)
    # Flowers + grass at base
    if bot_rect.height > 80:
        draw_flower_bed(surf, bcx, bot_rect.bottom - 2, bot_rect.width - 10,
                        14, seed=seed)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 2, bot_rect.width - 10,
                       14, palette, seed=seed)


def decorate_monastery(surf, top_rect, bot_rect, palette, seed):
    tcx = top_rect.x + top_rect.width // 2
    bcx = bot_rect.x + bot_rect.width // 2
    peak_x, peak_y = bcx + 2, bot_rect.y
    # Dense pine cluster at peak
    draw_pine_trio(surf, peak_x, peak_y, palette, seed=seed)
    # Monastery on a ledge mid-pillar
    monastery_y = bot_rect.y + max(80, bot_rect.height // 2)
    if monastery_y < bot_rect.bottom - 30:
        draw_monastery(surf, bcx - 14, monastery_y)
        # Prayer flag line from balcony to pine
        draw_prayer_flags(surf, bcx - 14, monastery_y, peak_x, peak_y - 16, n=6)
    # Second short flag line at top if room
    if bot_rect.height > 160:
        draw_prayer_flags(surf, bcx - 18, monastery_y + 40,
                          bcx + 18, monastery_y + 30, n=5)
    # Moss cascade on top pillar
    for off in range(-20, 22, 4):
        draw_moss_strand(surf, tcx + off, top_rect.bottom - 10,
                         12 + abs(off) % 6, palette, jitter_seed=seed + off)
    if top_rect.height > 50:
        draw_moss_patch(surf, tcx, top_rect.bottom - 32, 28, 10, palette, seed=seed)
    # Side shrubs
    if bot_rect.height > 110:
        for i, sc in enumerate((1.0, 0.9, 0.9)):
            y = bot_rect.y + 50 + i * 60
            if y >= bot_rect.bottom - 20 or y >= monastery_y - 10: continue
            side = 1 if i % 2 == 0 else -1
            sx = bcx + side * (bot_rect.width // 2 - 10)
            draw_side_shrub(surf, sx, y, palette, scale=sc)
    # Ground cover
    if bot_rect.height > 80:
        draw_climbing_vine(surf, bot_rect.x + bot_rect.width - 8, bot_rect.y + 30,
                           bot_rect.bottom - 14, palette, seed=seed + 1)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 2, bot_rect.width - 10,
                       12, palette, seed=seed)
        draw_flower_bed(surf, bcx, bot_rect.bottom - 3, bot_rect.width - 16,
                        10, seed=seed)


def decorate_lantern(surf, top_rect, bot_rect, palette, seed):
    tcx = top_rect.x + top_rect.width // 2
    bcx = bot_rect.x + bot_rect.width // 2
    peak_x, peak_y = bcx + 2, bot_rect.y
    draw_pine_trio(surf, peak_x, peak_y, palette, seed=seed)
    # Hero + gold lantern from top pillar
    draw_paper_lantern(surf, tcx - 8, top_rect.bottom - 4, strand=18, scale=1.2, color='red')
    draw_paper_lantern(surf, tcx + 12, top_rect.bottom - 6, strand=26, scale=0.8, color='gold')
    # String of small lanterns below top pillar
    for i, (dx, strand, clr) in enumerate([(-28, 6, 'red'), (-10, 12, 'gold'),
                                             (8, 6, 'red'), (26, 12, 'gold')]):
        lx = tcx + dx
        ly = top_rect.bottom + 18
        if ly < bot_rect.y - 6:
            draw_paper_lantern(surf, lx, ly, strand=strand, scale=0.55, color=clr)
    # Moss strands
    for off in range(-18, 20, 4):
        draw_moss_strand(surf, tcx + off, top_rect.bottom - 12,
                         10 + abs(off) % 6, palette, jitter_seed=seed + off)
    # Bougainvillea / magenta climbing specks along bottom pillar sides
    if bot_rect.height > 80:
        steps = max(6, bot_rect.height // 14)
        for i in range(steps):
            dy = bot_rect.y + 20 + i * 14
            if dy > bot_rect.bottom - 8: break
            for dx in (bot_rect.x + 6, bot_rect.x + bot_rect.width - 8):
                pygame.draw.circle(surf, (220, 60, 140), (dx, dy), 2)
                pygame.draw.circle(surf, (245, 130, 180), (dx + 1, dy - 1), 1)
    # Plaque + incense at base
    if bot_rect.height > 100:
        plaque_rect = pygame.Rect(bcx - 8, bot_rect.bottom - 18, 16, 16)
        pygame.draw.rect(surf, (160, 125, 55), plaque_rect)
        pygame.draw.rect(surf, (220, 180, 80), plaque_rect.inflate(-2, -2))
        for i in range(3):
            pygame.draw.line(surf, (120, 85, 25),
                             (bcx - 5, bot_rect.bottom - 14 + i * 4),
                             (bcx + 5, bot_rect.bottom - 14 + i * 4), 1)
        draw_incense_smoke(surf, bcx - 16, bot_rect.bottom - 20, length=18)
        draw_incense_smoke(surf, bcx + 16, bot_rect.bottom - 20, length=18)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 2, bot_rect.width - 10,
                       12, palette, seed=seed)


def decorate_overgrown(surf, top_rect, bot_rect, palette, seed):
    tcx = top_rect.x + top_rect.width // 2
    bcx = bot_rect.x + bot_rect.width // 2
    peak_x, peak_y = bcx + 2, bot_rect.y
    # Broadleaf canopy on peak (replaces the pine)
    pygame.draw.line(surf, (90, 60, 35), (peak_x, peak_y + 2), (peak_x, peak_y - 22), 3)
    for (dx, dy, sz) in [(0, 0, 34), (-10, 6, 24), (12, 8, 26), (-4, -8, 20)]:
        pygame.draw.circle(surf, (30, 90, 45), (peak_x + dx, peak_y - 26 + dy), sz // 2 + 2)
        pygame.draw.circle(surf, (60, 150, 70), (peak_x + dx, peak_y - 26 + dy), sz // 2)
        pygame.draw.circle(surf, (130, 210, 100), (peak_x + dx - 2, peak_y - 28 + dy),
                           max(3, sz // 2 - 5))
    # Strangler fig cascading down one side
    if bot_rect.height > 100:
        draw_strangler_fig(surf, bot_rect.x + 4, bot_rect.y + 24, bot_rect.bottom - 8)
    # Masonry blocks + stone face + ferns on ledges
    if bot_rect.height > 80:
        draw_masonry_blocks(surf, bcx, bot_rect.y + 20, bot_rect.bottom - 10,
                            bot_rect.width, seed=seed)
    if bot_rect.height > 120:
        draw_stone_face(surf, bcx + 10, bot_rect.y + bot_rect.height // 2)
    # Fern banks at intervals
    if bot_rect.height > 100:
        for frac in (0.35, 0.60, 0.85):
            fy = int(bot_rect.y + bot_rect.height * frac)
            if fy > bot_rect.bottom - 10: continue
            draw_fern_cluster(surf, bcx - 12, fy, 6, palette, seed=seed + fy)
            draw_fern_cluster(surf, bcx + 14, fy - 2, 5, palette, seed=seed + fy + 1)
    # Orchid specks
    rng = random.Random(seed)
    for _ in range(6):
        ox = bcx + rng.randint(-bot_rect.width // 2 + 6, bot_rect.width // 2 - 6)
        oy = rng.randint(bot_rect.y + 30, bot_rect.bottom - 10)
        pygame.draw.circle(surf, (220, 150, 200), (ox, oy), 2)
        pygame.draw.circle(surf, (250, 200, 230), (ox + 1, oy - 1), 1)
    # Moss on top pillar
    if top_rect.height > 40:
        draw_moss_patch(surf, tcx, top_rect.bottom - 20, 32, 14, palette, seed=seed)
    # Drifting bird
    draw_bird_sil(surf, tcx + 30, max(20, top_rect.y + 40), size=4)


def decorate_menhir(surf, top_rect, bot_rect, palette, seed):
    tcx = top_rect.x + top_rect.width // 2
    bcx = bot_rect.x + bot_rect.width // 2
    peak_x, peak_y = bcx + 2, bot_rect.y
    # Small rowan tree with red-berry accents on peak
    pygame.draw.line(surf, (90, 60, 40), (peak_x, peak_y + 2), (peak_x + 2, peak_y - 22), 2)
    for rx, ry in [(-6, -10), (8, -14), (-2, -20), (10, -8), (-8, -18)]:
        pygame.draw.circle(surf, (40, 120, 55), (peak_x + rx, peak_y + ry), 5)
        pygame.draw.circle(surf, (80, 170, 80), (peak_x + rx - 1, peak_y + ry - 1), 4)
        pygame.draw.circle(surf, (200, 40, 40), (peak_x + rx + 2, peak_y + ry + 1), 1)
    # Spiral glow carvings scaled to pillar height
    if bot_rect.height > 70:
        centres = [(0, 0.45, 12), (-16, 0.28, 7), (14, 0.70, 9)]
        for dx, frac, r in centres:
            sy = int(bot_rect.y + bot_rect.height * frac)
            if sy > bot_rect.bottom - 10: continue
            draw_spiral_glow(surf, bcx + dx, sy, radius=r)
    # Tied ribbons at upper body
    draw_ribbons_tied(surf, bcx, bot_rect.y + 10, n=4, width=20, seed=seed)
    if bot_rect.height > 110:
        draw_ribbons_tied(surf, bcx + 10, bot_rect.y + bot_rect.height // 2 - 20,
                          n=4, width=18, seed=seed + 1)
    # Offering cairn + candle at base
    if bot_rect.height > 80:
        draw_cairn(surf, bcx - 14, bot_rect.bottom - 2, n=3, pennant=False)
        pygame.draw.rect(surf, (240, 230, 210), (bcx + 14, bot_rect.bottom - 10, 4, 8))
        g = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(g, (255, 220, 120, 180), (5, 5), 4)
        surf.blit(g, (bcx + 11, bot_rect.bottom - 16))
    # Heather tufts + moss + raven
    if bot_rect.height > 60:
        for dx in range(-bot_rect.width // 2 + 6, bot_rect.width // 2 - 4, 5):
            for k in range(2):
                pygame.draw.line(surf, (150, 90, 140),
                                 (bcx + dx + k, bot_rect.bottom - 2),
                                 (bcx + dx + k - 1, bot_rect.bottom - 8), 1)
                pygame.draw.circle(surf, (200, 140, 190),
                                   (bcx + dx + k, bot_rect.bottom - 10), 1)
    if top_rect.height > 40:
        draw_moss_patch(surf, tcx, top_rect.bottom - 20, 28, 12, palette, seed=seed)
    draw_raven(surf, tcx - 6, max(20, top_rect.y + 24))


# ── Variant registry + dispatcher ───────────────────────────────────────────

_VARIANTS = (
    # (bottom-pillar silhouette, decorate function)
    (silhouette_bottom_spire, decorate_original),
    (silhouette_bottom_spire, decorate_lungta),
    (sil_bot_slender,         decorate_darchog),
    (sil_bot_shelf,            decorate_babylon),
    (sil_bot_lean,             decorate_monastery),
    (sil_bot_stout,            decorate_lantern),
    (sil_bot_eroded,           decorate_overgrown),
    (sil_bot_blunt,            decorate_menhir),
)

VARIANT_COUNT = len(_VARIANTS)


def _paint_stone(surf, rect, polygon_fn, palette, body_seed):
    if rect.height <= 0:
        return
    body = get_stone_pillar_body(
        rect.width, max(1, rect.height),
        palette['stone_light'], palette['stone_mid'],
        palette['stone_dark'], palette['stone_accent'],
        body_seed=body_seed,
    )
    polygon = polygon_fn(rect.width, rect.height)
    silhouette_blit(surf, body, polygon, rect.topleft, shadow_alpha=110)


def draw_pillar_pair(surf, top_rect, bot_rect, palette, seed):
    """Paint both pillar bodies + decorate according to the variant keyed by seed."""
    variant_id = seed % VARIANT_COUNT
    bot_sil, decorate = _VARIANTS[variant_id]
    _paint_stone(surf, top_rect, silhouette_top_spire, palette, seed)
    _paint_stone(surf, bot_rect, bot_sil, palette, seed + 1)
    decorate(surf, top_rect, bot_rect, palette, seed)

