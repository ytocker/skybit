"""Render 5 pillar variant options side-by-side — built in small steps."""
import os, math, random, sys, pathlib
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import pygame

from game.draw import (
    get_stone_pillar_body,
    silhouette_bottom_spire, silhouette_top_spire, silhouette_blit,
    draw_wuling_pine, draw_moss_strand, draw_side_shrub, draw_pillar_mist,
)

W, H = 1500, 820
COLS = 5
COL_W = W // COLS
TOP_H = 240
GAP_H = 230
BOT_TOP = TOP_H + GAP_H
GROUND_Y = H - 40
PILLAR_W = 92

FOLIAGE = dict(foliage_top=(140, 220, 110), foliage_mid=(70, 170, 75),
               foliage_dark=(30, 100, 50), foliage_accent=(255, 240, 120))

VARIANTS = [
    dict(name="1. Pilgrim's Peak",  stone=(240, 205, 150, 180, 140,  95, 100, 65, 45, 255, 230, 175)),
    dict(name="2. Ribbon Pine",     stone=(195, 195, 185, 140, 140, 125,  65, 70, 72, 220, 225, 210)),
    dict(name="3. Lantern Ledge",   stone=(250, 235, 210, 210, 190, 160, 125, 105, 85, 255, 245, 220)),
    dict(name="4. Crane's Rest",    stone=(210, 205, 150, 150, 155,  95,  75, 90, 50, 235, 235, 160)),
    dict(name="5. Cairn Marker",    stone=(240, 160, 115, 195, 100,  65, 110,  48, 32, 255, 180, 125)),
]


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t), int(a[2] + (b[2] - a[2]) * t))


def draw_grass_tuft(surf, cx, cy, palette, seed=0):
    rng = random.Random(seed)
    mid, top = palette['foliage_mid'], palette['foliage_top']
    for i in range(5):
        dx = -4 + i * 2
        tip_y = cy - 4 - rng.randint(0, 3)
        pygame.draw.line(surf, mid, (cx + dx, cy), (cx + dx + rng.randint(-2, 2), tip_y), 1)
    pygame.draw.line(surf, top, (cx, cy), (cx, cy - 6), 1)


def draw_wildflowers(surf, cx, cy, seed=0):
    rng = random.Random(seed)
    for _ in range(10):
        dx, dy = rng.randint(-14, 14), rng.randint(-3, 2)
        col = rng.choice([(255, 230, 90), (255, 255, 245), (255, 210, 80), (255, 180, 200)])
        pygame.draw.circle(surf, col, (cx + dx, cy + dy), rng.choice([1, 2]))


def draw_berry_cluster(surf, cx, cy, seed=0):
    rng = random.Random(seed)
    for _ in range(6):
        dx, dy = rng.randint(-5, 5), rng.randint(-3, 3)
        col = rng.choice([(200, 40, 40), (230, 70, 50), (170, 30, 30)])
        pygame.draw.circle(surf, (70, 20, 20), (cx + dx, cy + dy), 2)
        pygame.draw.circle(surf, col, (cx + dx, cy + dy), 1)


def draw_flower_shrub(surf, x, y, palette, scale=1.0, seed=0):
    draw_side_shrub(surf, x, y, palette, scale=scale)
    rng = random.Random(seed)
    for _ in range(int(8 * scale)):
        dx = rng.randint(-int(13 * scale), int(13 * scale))
        dy = rng.randint(-int(10 * scale), 0)
        col = rng.choice([(255, 230, 90), (255, 255, 245), (255, 180, 200), (255, 160, 120)])
        pygame.draw.circle(surf, col, (x + dx, y + dy), rng.choice([1, 2]))


def draw_mushrooms(surf, cx, cy, n=3, seed=0):
    rng = random.Random(seed)
    for i in range(n):
        dx = (i - n // 2) * 6 + rng.randint(-1, 1)
        # stem + red cap with a white dot
        pygame.draw.rect(surf, (250, 240, 225), (cx + dx - 1, cy - 2, 2, 3))
        pygame.draw.ellipse(surf, (180, 30, 30), (cx + dx - 3, cy - 5, 6, 4))
        pygame.draw.ellipse(surf, (225, 60, 50), (cx + dx - 2, cy - 5, 4, 3))
        pygame.draw.circle(surf, (255, 255, 255), (cx + dx, cy - 4), 1)


def draw_pom_pom_vine(surf, x, y, length, palette, seed=0):
    dark, mid, top = palette['foliage_dark'], palette['foliage_mid'], palette['foliage_top']
    pts = []
    for i in range(length):
        t = i / max(1, length - 1)
        off = int(math.sin(t * 3.6 + seed) * 2)
        pts.append((x + off, y + i))
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, dark, pts[i], pts[i + 1], 1)
    for i, frac in enumerate((0.28, 0.58, 0.86)):
        px, py = pts[int(frac * (len(pts) - 1))]
        r = 3 + (i % 2)
        pygame.draw.circle(surf, dark, (px, py), r + 1)
        pygame.draw.circle(surf, mid, (px, py), r)
        pygame.draw.circle(surf, top, (px - 1, py - 1), max(1, r - 2))


def draw_firefly(surf, cx, cy):
    g = pygame.Surface((24, 24), pygame.SRCALPHA)
    pygame.draw.circle(g, (255, 230, 120, 70), (12, 12), 11)
    pygame.draw.circle(g, (255, 245, 180, 150), (12, 12), 6)
    pygame.draw.circle(g, (255, 255, 230, 255), (12, 12), 2)
    surf.blit(g, (cx - 12, cy - 12))


def draw_moth(surf, cx, cy):
    pygame.draw.polygon(surf, (210, 195, 170), [(cx, cy), (cx - 5, cy - 3), (cx - 6, cy + 1)])
    pygame.draw.polygon(surf, (230, 215, 190), [(cx, cy), (cx + 5, cy - 3), (cx + 6, cy + 1)])
    pygame.draw.line(surf, (70, 55, 45), (cx, cy - 1), (cx, cy + 3), 1)


def draw_butterfly(surf, cx, cy, wing_col=(230, 130, 60)):
    dark = (60, 40, 20)
    pygame.draw.ellipse(surf, wing_col, (cx - 6, cy - 3, 5, 5))
    pygame.draw.ellipse(surf, wing_col, (cx + 1, cy - 3, 5, 5))
    pygame.draw.ellipse(surf, dark, (cx - 6, cy - 3, 5, 5), 1)
    pygame.draw.ellipse(surf, dark, (cx + 1, cy - 3, 5, 5), 1)
    pygame.draw.line(surf, dark, (cx, cy - 2), (cx, cy + 2), 1)


def draw_bird_silhouette(surf, cx, cy, size=6):
    col = (45, 40, 55)
    pygame.draw.line(surf, col, (cx - size, cy + size // 2), (cx, cy - size // 3), 2)
    pygame.draw.line(surf, col, (cx, cy - size // 3), (cx + size, cy + size // 2), 2)


def draw_paper_lantern(surf, hang_x, hang_y, strand_len=16, scale=1.0):
    pygame.draw.line(surf, (40, 30, 25), (hang_x, hang_y), (hang_x, hang_y + strand_len), 1)
    cx, cy = hang_x, hang_y + strand_len
    lw, lh = max(8, int(16 * scale)), max(10, int(20 * scale))
    cap = max(2, int(3 * scale))
    pygame.draw.rect(surf, (55, 35, 25), (cx - lw // 2 + 1, cy, lw - 2, cap))
    pygame.draw.rect(surf, (55, 35, 25), (cx - lw // 2 + 1, cy + lh - cap, lw - 2, cap))
    body = pygame.Rect(cx - lw // 2, cy + cap - 1, lw, lh - 2 * cap + 2)
    pygame.draw.ellipse(surf, (170, 30, 35), body)
    pygame.draw.ellipse(surf, (230, 80, 65), body.inflate(-max(2, int(4 * scale)), -max(1, int(3 * scale))))
    rib = max(2, int(4 * scale))
    pygame.draw.line(surf, (130, 20, 25), (cx - rib, cy + cap), (cx - rib, cy + lh - cap - 1), 1)
    pygame.draw.line(surf, (130, 20, 25), (cx + rib, cy + cap), (cx + rib, cy + lh - cap - 1), 1)
    gsz = max(8, int(22 * scale))
    g = pygame.Surface((gsz * 2, gsz * 2), pygame.SRCALPHA)
    pygame.draw.circle(g, (255, 215, 120, 110), (gsz, gsz), int(gsz * 0.55))
    pygame.draw.circle(g, (255, 240, 200, 180), (gsz, gsz), max(2, int(gsz * 0.28)))
    surf.blit(g, (cx - gsz, cy + lh // 2 - gsz))
    pygame.draw.line(surf, (200, 160, 40), (cx, cy + lh), (cx, cy + lh + max(3, int(5 * scale))), 1)
    pygame.draw.circle(surf, (220, 180, 60), (cx, cy + lh + max(4, int(6 * scale))), max(1, int(2 * scale)))


def draw_lantern_string(surf, x1, y1, x2, y2, n=3):
    mx, my = (x1 + x2) // 2, max(y1, y2) + 12
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
        lx, ly = pts[int((i + 1) / (n + 1) * steps)]
        draw_paper_lantern(surf, lx, ly, strand_len=3, scale=0.45)


def draw_ledge_lantern(surf, x, y):
    pygame.draw.rect(surf, (70, 50, 35), (x - 1, y - 12, 2, 12))
    pygame.draw.circle(surf, (80, 55, 40), (x, y - 12), 3)
    lw, lh = 10, 12
    pygame.draw.rect(surf, (55, 35, 25), (x - lw // 2 + 1, y - 12 - lh, lw - 2, 2))
    pygame.draw.rect(surf, (55, 35, 25), (x - lw // 2 + 1, y - 12 - 2, lw - 2, 2))
    body = pygame.Rect(x - lw // 2, y - 12 - lh + 2, lw, lh - 4)
    pygame.draw.ellipse(surf, (175, 35, 40), body)
    pygame.draw.ellipse(surf, (235, 110, 80), body.inflate(-4, -3))
    g = pygame.Surface((24, 24), pygame.SRCALPHA)
    pygame.draw.circle(g, (255, 220, 140, 110), (12, 12), 10)
    pygame.draw.circle(g, (255, 245, 210, 190), (12, 12), 4)
    surf.blit(g, (x - 12, y - 12 - lh + 2 + (lh - 4) // 2 - 12))


FLAG_COLORS = [(70, 140, 230), (245, 245, 245), (230, 70, 70), (80, 180, 90), (245, 210, 70)]


def draw_prayer_flags(surf, x1, y1, x2, y2, n=7, bells=True):
    mx, my = (x1 + x2) // 2, max(y1, y2) + 18
    steps = 40
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
        col = FLAG_COLORS[i % 5]
        r = pygame.Rect(px - 4, py, 8, 11)
        pygame.draw.rect(surf, col, r)
        pygame.draw.rect(surf, (40, 30, 20), r, 1)
        if bells and i % 3 == 2:
            pygame.draw.circle(surf, (200, 150, 30), (px, py + 13), 2)


def draw_bell(surf, cx, cy):
    pygame.draw.polygon(surf, (200, 150, 30), [(cx - 3, cy), (cx + 3, cy), (cx + 2, cy + 5), (cx - 2, cy + 5)])
    pygame.draw.ellipse(surf, (230, 180, 60), (cx - 3, cy - 2, 6, 3))
    pygame.draw.circle(surf, (150, 100, 20), (cx, cy + 6), 1)


def draw_stupa(surf, cx, cy):
    pygame.draw.rect(surf, (240, 235, 225), (cx - 8, cy - 6, 16, 6))
    pygame.draw.ellipse(surf, (245, 240, 230), (cx - 7, cy - 16, 14, 12))
    pygame.draw.rect(surf, (240, 235, 225), (cx - 2, cy - 22, 4, 7))
    pygame.draw.polygon(surf, (220, 180, 60), [(cx, cy - 26), (cx - 3, cy - 22), (cx + 3, cy - 22)])
    pygame.draw.rect(surf, (80, 60, 50), (cx - 2, cy, 4, 3))


def draw_incense_smoke(surf, x, y, length=30):
    for i in range(length):
        t = i / length
        off = int(math.sin(t * 6) * 3)
        alpha = int(160 * (1 - t))
        s = pygame.Surface((6, 3), pygame.SRCALPHA)
        s.fill((230, 230, 230, alpha))
        surf.blit(s, (x + off - 3, y - i))


def draw_trunk_ribbon(surf, x, y, seed=0):
    rng = random.Random(seed)
    pygame.draw.ellipse(surf, (180, 30, 40), (x - 4, y - 3, 8, 6))
    pygame.draw.ellipse(surf, (230, 60, 60), (x - 3, y - 2, 6, 4))
    for side, col in ((-1, (210, 40, 50)), (1, (230, 80, 80))):
        tail = []
        for i in range(7):
            t = i / 6
            tx = x + side * int(4 + t * 16)
            ty = y + int(math.sin(t * 3.3 + rng.random()) * 3) + int(t * 5)
            tail.append((tx, ty))
        poly = tail + [(tx, ty + 4) for tx, ty in reversed(tail)]
        pygame.draw.polygon(surf, col, poly)
        pygame.draw.polygon(surf, (120, 20, 30), poly, 1)


def draw_wish_plaque(surf, hang_x, hang_y, cord_len=10):
    pygame.draw.line(surf, (60, 45, 30), (hang_x, hang_y), (hang_x, hang_y + cord_len), 1)
    cx, cy = hang_x, hang_y + cord_len
    pygame.draw.rect(surf, (150, 110, 70), (cx - 5, cy, 10, 14))
    pygame.draw.rect(surf, (200, 160, 110), (cx - 4, cy + 1, 8, 12))
    pygame.draw.rect(surf, (80, 55, 35), (cx - 5, cy, 10, 14), 1)
    for i in range(3):
        pygame.draw.line(surf, (70, 45, 25), (cx - 2, cy + 3 + i * 3), (cx + 2, cy + 3 + i * 3), 1)


def draw_cairn(surf, cx, base_y, stones=4, pennant=True):
    sizes = [(18, 8), (14, 6), (10, 5), (7, 4), (5, 3)][:stones]
    cols = [(130, 115, 95), (155, 140, 115), (180, 160, 130), (200, 180, 145), (215, 195, 160)]
    y = base_y
    for (w, h), col in zip(sizes, cols):
        r = pygame.Rect(cx - w // 2, y - h, w, h)
        pygame.draw.ellipse(surf, (60, 45, 35), r.inflate(2, 1))
        pygame.draw.ellipse(surf, col, r)
        y -= h - 1
    if pennant:
        pygame.draw.line(surf, (60, 45, 30), (cx, y), (cx, y - 14), 1)
        pygame.draw.polygon(surf, (200, 40, 45), [(cx, y - 14), (cx + 9, y - 11), (cx, y - 8)])


def draw_pennant_string(surf, x1, y1, x2, y2, n=6):
    cols = [(230, 60, 60), (240, 150, 40), (245, 210, 70), (80, 180, 90), (70, 140, 230)]
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((int(x1 + (x2 - x1) * t), int(y1 + (y2 - y1) * t + math.sin(t * 3) * 6)))
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, (60, 45, 30), pts[i], pts[i + 1], 1)
    for i in range(n):
        px, py = pts[i]
        c = cols[i % 5]
        pygame.draw.polygon(surf, c, [(px, py), (px + 6, py), (px + 3, py + 7)])


def draw_signpost(surf, x, base_y):
    pygame.draw.rect(surf, (80, 55, 35), (x - 1, base_y - 28, 2, 28))
    for i, (y, sgn) in enumerate([(base_y - 24, 1), (base_y - 16, -1)]):
        w = 14
        rect = pygame.Rect(x if sgn > 0 else x - w, y, w, 5)
        pygame.draw.rect(surf, (160, 115, 75), rect)
        pygame.draw.rect(surf, (90, 60, 35), rect, 1)
        tip_x = rect.right + 3 if sgn > 0 else rect.left - 3
        pygame.draw.polygon(surf, (160, 115, 75),
                            [(rect.right if sgn > 0 else rect.left, y), (tip_x, y + 2), (rect.right if sgn > 0 else rect.left, y + 5)])


def draw_walking_stick(surf, x, base_y, lean=8):
    top = (x - lean, base_y - 36)
    pygame.draw.line(surf, (90, 60, 35), (x, base_y), top, 2)
    pygame.draw.circle(surf, (130, 90, 50), top, 3)


def draw_campfire(surf, cx, base_y):
    pygame.draw.line(surf, (80, 55, 35), (cx - 6, base_y), (cx + 6, base_y - 2), 3)
    pygame.draw.line(surf, (80, 55, 35), (cx - 6, base_y - 2), (cx + 6, base_y), 3)
    g = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(g, (255, 150, 50, 160), (10, 10), 9)
    pygame.draw.circle(g, (255, 220, 120, 220), (10, 10), 4)
    surf.blit(g, (cx - 10, base_y - 14))
    for i in range(12):
        t = i / 12
        off = int(math.sin(t * 5) * 3)
        s = pygame.Surface((5, 3), pygame.SRCALPHA)
        s.fill((220, 220, 220, int(140 * (1 - t))))
        surf.blit(s, (cx + off - 2, base_y - 20 - i * 2))


def draw_crane(surf, cx, base_y):
    pygame.draw.ellipse(surf, (250, 250, 250), (cx - 7, base_y - 10, 14, 8))
    pygame.draw.ellipse(surf, (210, 215, 220), (cx - 6, base_y - 9, 12, 6))
    pygame.draw.ellipse(surf, (40, 40, 50), (cx - 3, base_y - 9, 8, 4))
    for i, (a, b) in enumerate([((cx - 1, base_y - 9), (cx - 4, base_y - 13)),
                                 ((cx - 4, base_y - 13), (cx - 3, base_y - 17)),
                                 ((cx - 3, base_y - 17), (cx + 1, base_y - 20))]):
        pygame.draw.line(surf, (250, 250, 250), a, b, 2)
    pygame.draw.circle(surf, (250, 250, 250), (cx + 1, base_y - 20), 2)
    pygame.draw.line(surf, (230, 150, 60), (cx + 2, base_y - 20), (cx + 6, base_y - 19), 1)
    pygame.draw.circle(surf, (220, 40, 50), (cx + 1, base_y - 21), 1)
    pygame.draw.line(surf, (40, 30, 30), (cx - 3, base_y - 3), (cx - 3, base_y + 3), 1)
    pygame.draw.line(surf, (40, 30, 30), (cx + 2, base_y - 3), (cx + 2, base_y + 3), 1)


def draw_raven(surf, cx, cy):
    pygame.draw.ellipse(surf, (25, 25, 35), (cx - 5, cy - 3, 10, 6))
    pygame.draw.circle(surf, (20, 20, 30), (cx + 5, cy - 4), 3)
    pygame.draw.polygon(surf, (40, 35, 25), [(cx + 8, cy - 4), (cx + 11, cy - 3), (cx + 8, cy - 2)])


def draw_rabbit_silhouette(surf, cx, base_y):
    pygame.draw.ellipse(surf, (170, 150, 125), (cx - 6, base_y - 6, 12, 7))
    pygame.draw.circle(surf, (170, 150, 125), (cx + 5, base_y - 7), 3)
    pygame.draw.line(surf, (170, 150, 125), (cx + 5, base_y - 10), (cx + 4, base_y - 14), 2)
    pygame.draw.line(surf, (170, 150, 125), (cx + 7, base_y - 10), (cx + 8, base_y - 14), 2)
    pygame.draw.circle(surf, (40, 30, 30), (cx + 6, base_y - 7), 1)


def draw_bird_nest(surf, cx, cy):
    pygame.draw.ellipse(surf, (90, 65, 40), (cx - 5, cy - 2, 10, 5))
    pygame.draw.ellipse(surf, (120, 90, 55), (cx - 4, cy - 1, 8, 3))
    for dx in (-1, 1, 3):
        pygame.draw.circle(surf, (245, 230, 180), (cx + dx, cy), 1)


def paint_bg(surf):
    for y in range(H):
        t = y / (H - 1)
        c = (int(40 + 130 * t), int(110 + 110 * t), int(200 + 45 * t))
        pygame.draw.line(surf, (min(255, c[0]), min(255, c[1]), min(255, c[2])), (0, y), (W - 1, y))
    pygame.draw.rect(surf, (60, 120, 60), (0, GROUND_Y, W, H - GROUND_Y))


def draw_pair(surf, col, variant):
    cx = col * COL_W + COL_W // 2
    sl, sm, sd, sa = variant['stone'][0:3], variant['stone'][3:6], variant['stone'][6:9], variant['stone'][9:12]
    palette = dict(FOLIAGE, stone_light=sl, stone_mid=sm, stone_dark=sd, stone_accent=sa)
    top_body = get_stone_pillar_body(PILLAR_W, TOP_H, sl, sm, sd, sa, body_seed=col * 3 + 1)
    silhouette_blit(surf, top_body, silhouette_top_spire(PILLAR_W, TOP_H), (cx - PILLAR_W // 2, 0))
    bot_h = GROUND_Y - BOT_TOP
    bot_body = get_stone_pillar_body(PILLAR_W, bot_h, sl, sm, sd, sa, body_seed=col * 3 + 2)
    silhouette_blit(surf, bot_body, silhouette_bottom_spire(PILLAR_W, bot_h), (cx - PILLAR_W // 2, BOT_TOP))
    decorate(surf, cx, palette, variant['name'], col)
    draw_pillar_mist(surf, cx, GROUND_Y - 4, PILLAR_W, alpha=110)
    return cx, palette


def decorate(surf, cx, palette, name, col):
    peak_x, peak_y = cx + 4, BOT_TOP
    if "Pilgrim" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 80, palette, lean=12, layers=5)
        draw_wuling_pine(surf, peak_x - 18, peak_y + 18, 48, palette, lean=-6, layers=4)
        draw_side_shrub(surf, cx - PILLAR_W // 2 + 10, BOT_TOP + 40, palette, scale=1.0)
        draw_side_shrub(surf, cx + PILLAR_W // 2 - 12, BOT_TOP + 80, palette, scale=0.9)
        draw_moss_strand(surf, cx - 18, TOP_H - 18, 14, palette, jitter_seed=col)
        draw_grass_tuft(surf, cx - 26, BOT_TOP + 130, palette, seed=col)
        draw_grass_tuft(surf, cx + 22, BOT_TOP + 60, palette, seed=col + 1)
        draw_prayer_flags(surf, cx - 36, TOP_H - 52, peak_x + 18, peak_y - 58, n=7, bells=True)
        draw_stupa(surf, cx - 10, GROUND_Y - 10)
        draw_incense_smoke(surf, cx - 10, GROUND_Y - 36, length=30)
        draw_wildflowers(surf, cx + 12, GROUND_Y - 6, seed=col + 3)
        for bx, by in [(cx - 110, 60), (cx + 90, 90), (cx - 80, 120)]:
            draw_bird_silhouette(surf, bx, by, size=5)
        return
    if "Ribbon" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 86, palette, lean=10, layers=6)
        draw_wuling_pine(surf, peak_x - 16, peak_y + 30, 48, palette, lean=-4, layers=4)
        for off in (-22, -10, 2, 14, 24):
            draw_moss_strand(surf, cx + off, TOP_H - 14, 18 + (off % 5), palette, jitter_seed=col * 7 + off)
        draw_trunk_ribbon(surf, peak_x + 1, peak_y - 12, seed=col)
        draw_trunk_ribbon(surf, peak_x - 12, peak_y + 22, seed=col + 1)
        draw_trunk_ribbon(surf, peak_x + 14, peak_y + 4, seed=col + 2)
        draw_wish_plaque(surf, peak_x - 22, peak_y - 30, cord_len=8)
        draw_bell(surf, peak_x + 20, peak_y - 38)
        draw_berry_cluster(surf, peak_x + 4, peak_y - 54, seed=col)
        draw_mushrooms(surf, cx - 20, GROUND_Y - 6, n=3, seed=col)
        draw_side_shrub(surf, cx + PILLAR_W // 2 - 12, BOT_TOP + 70, palette, scale=0.9)
        for i in range(8):
            dy = BOT_TOP + 40 + i * 18
            dx = cx - PILLAR_W // 2 + 6 + (i % 2) * 4
            pygame.draw.circle(surf, (220, 110, 200), (dx, dy), 2)
            pygame.draw.circle(surf, (240, 160, 220), (dx + 1, dy - 1), 1)
        return
    if "Lantern" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 72, palette, lean=10, layers=5)
        draw_flower_shrub(surf, cx - PILLAR_W // 2 + 14, BOT_TOP + 48, palette, scale=1.1, seed=col)
        draw_flower_shrub(surf, cx + PILLAR_W // 2 - 14, BOT_TOP + 110, palette, scale=0.95, seed=col + 3)
        draw_pom_pom_vine(surf, cx + 22, TOP_H - 10, 60, palette, seed=col)
        draw_grass_tuft(surf, cx - 28, TOP_H - 18, palette, seed=col)
        draw_grass_tuft(surf, cx + 18, BOT_TOP + 80, palette, seed=col + 1)
        draw_grass_tuft(surf, cx - 24, BOT_TOP + 150, palette, seed=col + 2)
        draw_moss_strand(surf, cx - 18, TOP_H - 18, 14, palette, jitter_seed=col + 5)
        draw_paper_lantern(surf, cx - 14, TOP_H - 4, strand_len=22, scale=1.3)
        draw_lantern_string(surf, cx - 48, TOP_H - 2, cx + 38, TOP_H + 2, n=3)
        draw_ledge_lantern(surf, cx - PILLAR_W // 2 + 24, BOT_TOP + 160)
        for fx, fy in [(cx - 54, TOP_H + 60), (cx + 50, TOP_H + 110),
                        (cx - 22, TOP_H + 160), (cx + 24, TOP_H + 40)]:
            draw_firefly(surf, fx, fy)
        draw_moth(surf, cx + 10, TOP_H + 24)
        return
    if "Crane" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 78, palette, lean=14, layers=5)
        draw_wuling_pine(surf, peak_x - 18, peak_y + 28, 42, palette, lean=-4, layers=4)
        draw_side_shrub(surf, cx + PILLAR_W // 2 - 12, BOT_TOP + 45, palette, scale=1.1)
        draw_wildflowers(surf, cx - 10, BOT_TOP + 70, seed=col)
        draw_wildflowers(surf, cx + 14, BOT_TOP + 140, seed=col + 2)
        draw_berry_cluster(surf, peak_x + 6, peak_y - 50, seed=col)
        draw_bird_nest(surf, peak_x - 6, peak_y - 42)
        draw_pom_pom_vine(surf, cx - 22, TOP_H - 10, 40, palette, seed=col + 4)
        draw_pom_pom_vine(surf, cx + 18, TOP_H - 14, 36, palette, seed=col + 7)
        draw_crane(surf, peak_x - 16, peak_y + 6)
        draw_bird_silhouette(surf, cx + 100, 80, size=8)
        draw_bird_silhouette(surf, cx + 120, 110, size=6)
        draw_butterfly(surf, cx - 18, BOT_TOP + 100, wing_col=(230, 130, 60))
        draw_butterfly(surf, cx + 26, BOT_TOP + 160, wing_col=(90, 150, 230))
        draw_butterfly(surf, cx - 32, BOT_TOP + 200, wing_col=(210, 90, 180))
        draw_rabbit_silhouette(surf, cx + 18, GROUND_Y - 6)
        draw_mushrooms(surf, cx - 22, GROUND_Y - 6, n=4, seed=col)
        return
    if "Cairn" in name:
        draw_wuling_pine(surf, peak_x + 10, peak_y + 6, 72, palette, lean=-8, layers=5)
        draw_moss_strand(surf, cx - 14, TOP_H - 16, 16, palette, jitter_seed=col)
        draw_side_shrub(surf, cx - PILLAR_W // 2 + 10, BOT_TOP + 46, palette, scale=1.2)
        draw_grass_tuft(surf, cx - 22, BOT_TOP + 150, palette, seed=col)
        draw_grass_tuft(surf, cx + 16, BOT_TOP + 90, palette, seed=col + 1)
        draw_cairn(surf, peak_x - 18, peak_y + 6, stones=4, pennant=True)
        draw_cairn(surf, cx + PILLAR_W // 2 - 8, BOT_TOP + 130, stones=3, pennant=False)
        draw_pennant_string(surf, peak_x - 14, peak_y - 18, peak_x + 34, peak_y - 40, n=6)
        draw_signpost(surf, cx - 30, GROUND_Y - 2)
        draw_walking_stick(surf, cx + 18, GROUND_Y - 2, lean=8)
        draw_campfire(surf, cx + 2, GROUND_Y - 4)
        draw_wish_plaque(surf, peak_x + 6, peak_y - 28, cord_len=6)
        draw_raven(surf, peak_x - 18, peak_y - 16)
        return


def label(surf, col, title, font):
    cx = col * COL_W + COL_W // 2
    t = font.render(title, True, (18, 18, 26))
    pad = 8
    w = t.get_width() + pad * 2
    h = t.get_height() + pad
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill((255, 255, 255, 225))
    surf.blit(bg, (cx - w // 2, 10))
    surf.blit(t, (cx - t.get_width() // 2, 10 + pad // 2))


def main():
    pygame.init()
    surf = pygame.Surface((W, H))
    paint_bg(surf)
    for i, v in enumerate(VARIANTS):
        draw_pair(surf, i, v)
    font = pygame.font.SysFont("arial", 18, bold=True)
    for i, v in enumerate(VARIANTS):
        label(surf, i, v['name'], font)
    out = "/home/user/Claude_test/docs/sketches/pillar_variants.png"
    pygame.image.save(surf, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
