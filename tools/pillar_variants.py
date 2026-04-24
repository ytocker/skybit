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

W_CELL, H_CELL = 300, 820
COLS, ROWS = 5, 4
W, H = W_CELL * COLS, H_CELL * ROWS
TOP_H = 240
GAP_H = 230
BOT_TOP = TOP_H + GAP_H
GROUND_Y = H_CELL - 40
PILLAR_W = 92

FOLIAGE = dict(foliage_top=(140, 220, 110), foliage_mid=(70, 170, 75),
               foliage_dark=(30, 100, 50), foliage_accent=(255, 240, 120))

STONE_L = (225, 195, 155)
STONE_M = (175, 140, 105)
STONE_D = (95, 70, 55)
STONE_A = (255, 220, 170)
PALETTE = dict(FOLIAGE, stone_light=STONE_L, stone_mid=STONE_M,
               stone_dark=STONE_D, stone_accent=STONE_A)

VARIANTS = []  # populated near main()


def sil_spike(w, h):
    # narrow sharp descending spire — tip at bottom, wide at top, sharply tapered
    return [(0, 0), (w, 0), (int(w * 0.72), int(h * 0.55)),
            (int(w * 0.58), int(h * 0.82)), (int(w * 0.5), h),
            (int(w * 0.42), int(h * 0.82)), (int(w * 0.28), int(h * 0.55))]


def sil_flat(w, h):
    # wide flat-bottomed cap — barely tapered, truncated blunt at the bottom
    return [(0, 0), (w, 0), (w, int(h * 0.84)),
            (int(w * 0.82), h), (int(w * 0.18), h), (0, int(h * 0.84))]


def sil_twin(w, h):
    # two uneven fangs descending from a shared top
    return [(0, 0), (w, 0), (w, int(h * 0.35)), (int(w * 0.78), int(h * 0.55)),
            (int(w * 0.68), h), (int(w * 0.58), int(h * 0.72)),
            (int(w * 0.50), int(h * 0.55)), (int(w * 0.42), int(h * 0.82)),
            (int(w * 0.30), int(h * 0.50)), (0, int(h * 0.35))]


def sil_notched(w, h):
    # rectangular column with a chunk notched out of the side mid-height
    return [(0, 0), (w, 0), (w, int(h * 0.40)),
            (int(w * 0.78), int(h * 0.42)), (int(w * 0.78), int(h * 0.56)),
            (w, int(h * 0.58)), (w, h), (0, h), (0, 0)]


def sil_bell(w, h):
    # wide flaring cap + narrower stem → bell / mushroom-cap hanging pillar
    return [(0, 0), (w, 0), (w, int(h * 0.32)),
            (int(w * 0.70), int(h * 0.40)), (int(w * 0.70), h),
            (int(w * 0.30), h), (int(w * 0.30), int(h * 0.40)),
            (0, int(h * 0.32))]


def sil_stepped(w, h):
    # staircase of three terraces tapering to a point
    return [(0, 0), (w, 0), (w, int(h * 0.28)),
            (int(w * 0.82), int(h * 0.30)), (int(w * 0.82), int(h * 0.52)),
            (int(w * 0.66), int(h * 0.54)), (int(w * 0.66), int(h * 0.78)),
            (int(w * 0.52), int(h * 0.80)), (int(w * 0.50), h),
            (int(w * 0.48), int(h * 0.80)), (int(w * 0.34), int(h * 0.78)),
            (int(w * 0.34), int(h * 0.54)), (int(w * 0.18), int(h * 0.52)),
            (int(w * 0.18), int(h * 0.30)), (0, int(h * 0.28))]


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


LANTERN_COLORS = {
    'red':    ((170, 30, 35),  (230, 80, 65)),
    'gold':   ((190, 140, 40), (245, 210, 100)),
    'white':  ((200, 200, 190), (245, 240, 225)),
    'blue':   ((50, 90, 170),  (110, 160, 220)),
    'pink':   ((200, 90, 130), (245, 160, 190)),
    'green':  ((60, 130, 70),  (130, 200, 130)),
}


def draw_paper_lantern(surf, hang_x, hang_y, strand_len=16, scale=1.0, color='red'):
    dark, light = LANTERN_COLORS.get(color, LANTERN_COLORS['red'])
    pygame.draw.line(surf, (40, 30, 25), (hang_x, hang_y), (hang_x, hang_y + strand_len), 1)
    cx, cy = hang_x, hang_y + strand_len
    lw, lh = max(8, int(16 * scale)), max(10, int(20 * scale))
    cap = max(2, int(3 * scale))
    pygame.draw.rect(surf, (55, 35, 25), (cx - lw // 2 + 1, cy, lw - 2, cap))
    pygame.draw.rect(surf, (55, 35, 25), (cx - lw // 2 + 1, cy + lh - cap, lw - 2, cap))
    body = pygame.Rect(cx - lw // 2, cy + cap - 1, lw, lh - 2 * cap + 2)
    pygame.draw.ellipse(surf, dark, body)
    pygame.draw.ellipse(surf, light, body.inflate(-max(2, int(4 * scale)), -max(1, int(3 * scale))))
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


def draw_banner(surf, hang_x, hang_y, length=40, color=(200, 40, 50), seed=0):
    rng = random.Random(seed)
    pygame.draw.line(surf, (60, 45, 30), (hang_x - 6, hang_y), (hang_x + 6, hang_y), 2)
    bw = 12
    pts = [(hang_x - bw // 2, hang_y), (hang_x + bw // 2, hang_y)]
    for i in range(length // 3):
        y = hang_y + (i + 1) * 3
        wobble = int(math.sin((i + seed) * 0.7) * 1.5)
        pts = [(hang_x - bw // 2 + wobble, hang_y)] + pts[1:] + [(hang_x + bw // 2 + wobble, y)]
    pygame.draw.polygon(surf, color, [(hang_x - bw // 2, hang_y), (hang_x + bw // 2, hang_y),
                                       (hang_x + bw // 2 + int(math.sin((length // 3) * 0.7) * 2),
                                        hang_y + length),
                                       (hang_x - bw // 2 + int(math.sin((length // 3) * 0.7) * 2),
                                        hang_y + length)])
    pygame.draw.line(surf, (255, 230, 150), (hang_x, hang_y + 5), (hang_x, hang_y + length - 5), 1)
    for i in range(2, length // 6):
        y = hang_y + i * 6
        pygame.draw.circle(surf, (255, 230, 180), (hang_x, y), 1)


def draw_wind_chime(surf, hang_x, hang_y):
    pygame.draw.line(surf, (60, 45, 30), (hang_x, hang_y), (hang_x, hang_y + 6), 1)
    pygame.draw.ellipse(surf, (150, 110, 60), (hang_x - 6, hang_y + 6, 12, 4))
    for dx, ln, col in ((-4, 14, (200, 160, 80)), (0, 18, (180, 140, 70)), (4, 12, (220, 180, 100))):
        pygame.draw.line(surf, col, (hang_x + dx, hang_y + 10), (hang_x + dx, hang_y + 10 + ln), 2)
        pygame.draw.circle(surf, col, (hang_x + dx, hang_y + 10 + ln + 1), 2)


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
        cy = y % H_CELL
        if cy >= H_CELL - 40:
            c = (60, 120, 60)
        else:
            t = cy / max(1, H_CELL - 41)
            c = (min(255, int(40 + 130 * t)), min(255, int(110 + 110 * t)), min(255, int(200 + 45 * t)))
        pygame.draw.line(surf, c, (0, y), (W - 1, y))


def draw_pair(cell, idx, variant):
    cx = W_CELL // 2
    sl, sm, sd, sa = STONE_L, STONE_M, STONE_D, STONE_A
    top_sil = variant.get('top_sil', silhouette_top_spire)
    top_body = get_stone_pillar_body(PILLAR_W, TOP_H, sl, sm, sd, sa, body_seed=idx * 3 + 1)
    silhouette_blit(cell, top_body, top_sil(PILLAR_W, TOP_H), (cx - PILLAR_W // 2, 0))
    bot_h = GROUND_Y - BOT_TOP
    bot_body = get_stone_pillar_body(PILLAR_W, bot_h, sl, sm, sd, sa, body_seed=idx * 3 + 2)
    silhouette_blit(cell, bot_body, silhouette_bottom_spire(PILLAR_W, bot_h), (cx - PILLAR_W // 2, BOT_TOP))
    decorate(cell, cx, PALETTE, variant['name'], idx)
    draw_pillar_mist(cell, cx, GROUND_Y - 4, PILLAR_W, alpha=110)


def decorate(surf, cx, palette, name, col):
    peak_x, peak_y = cx + 4, BOT_TOP
    if "Pilgrim" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 86, palette, lean=12, layers=6)
        draw_wuling_pine(surf, peak_x - 18, peak_y + 16, 54, palette, lean=-8, layers=5)
        draw_wuling_pine(surf, peak_x + 16, peak_y + 28, 42, palette, lean=6, layers=4)
        for sx, sy, sc in [(-34, 40, 1.0), (30, 70, 0.9), (-24, 110, 0.8), (30, 150, 1.0)]:
            draw_side_shrub(surf, cx + sx, BOT_TOP + sy, palette, scale=sc)
        for off, ln in ((-22, 18), (-8, 22), (6, 16), (18, 14)):
            draw_moss_strand(surf, cx + off, TOP_H - 14, ln, palette, jitter_seed=col + off)
        for gx, gy in [(-26, 60), (22, 100), (-32, 170), (28, 200), (0, 30)]:
            draw_grass_tuft(surf, cx + gx, BOT_TOP + gy, palette, seed=col + gy)
        draw_prayer_flags(surf, cx - 38, TOP_H - 58, peak_x + 22, peak_y - 68, n=9, bells=True)
        draw_prayer_flags(surf, cx + 36, TOP_H - 44, peak_x + 4, peak_y - 40, n=5, bells=False)
        draw_stupa(surf, cx - 10, GROUND_Y - 10)
        draw_stupa(surf, cx + 24, GROUND_Y - 6)
        draw_incense_smoke(surf, cx - 10, GROUND_Y - 36, length=34)
        draw_incense_smoke(surf, cx + 24, GROUND_Y - 30, length=24)
        draw_wildflowers(surf, cx - 28, GROUND_Y - 4, seed=col + 3)
        draw_wildflowers(surf, cx + 12, GROUND_Y - 5, seed=col + 9)
        draw_bell(surf, peak_x + 20, peak_y - 30)
        for bx, by in [(cx - 110, 40), (cx + 90, 70), (cx - 80, 100), (cx + 110, 130), (cx - 60, 160)]:
            draw_bird_silhouette(surf, bx, by, size=5)
        return
    if "Ribbon" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 94, palette, lean=10, layers=7)
        draw_wuling_pine(surf, peak_x - 16, peak_y + 30, 54, palette, lean=-4, layers=5)
        draw_wuling_pine(surf, peak_x + 18, peak_y + 44, 40, palette, lean=6, layers=4)
        for off in (-28, -18, -8, 2, 12, 22, 32):
            draw_moss_strand(surf, cx + off, TOP_H - 14, 18 + abs(off) % 8, palette, jitter_seed=col * 7 + off)
        for rx, ry, sd in [(1, -12, col), (-12, 22, col + 1), (14, 4, col + 2),
                            (-6, -40, col + 3), (22, -22, col + 4)]:
            draw_trunk_ribbon(surf, peak_x + rx, peak_y + ry, seed=sd)
        draw_wish_plaque(surf, peak_x - 22, peak_y - 30, cord_len=8)
        draw_wish_plaque(surf, peak_x + 18, peak_y - 52, cord_len=10)
        draw_bell(surf, peak_x + 20, peak_y - 38)
        draw_bell(surf, peak_x - 24, peak_y - 12)
        draw_berry_cluster(surf, peak_x + 4, peak_y - 60, seed=col)
        draw_berry_cluster(surf, peak_x - 14, peak_y - 30, seed=col + 2)
        draw_mushrooms(surf, cx - 22, GROUND_Y - 6, n=4, seed=col)
        draw_mushrooms(surf, cx + 18, GROUND_Y - 5, n=3, seed=col + 5)
        for sy, sc in [(50, 1.0), (90, 0.9), (140, 1.0), (190, 0.8)]:
            side = 1 if sy % 2 == 0 else -1
            draw_side_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc)
        for i in range(14):
            dy = BOT_TOP + 30 + i * 14
            side = 1 if i % 2 == 0 else -1
            dx = cx + side * (PILLAR_W // 2 - 6 - (i % 3) * 4)
            pygame.draw.circle(surf, (220, 110, 200), (dx, dy), 2)
            pygame.draw.circle(surf, (240, 160, 220), (dx + 1, dy - 1), 1)
        return
    if "Lantern" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 78, palette, lean=10, layers=5)
        draw_wuling_pine(surf, peak_x - 18, peak_y + 24, 44, palette, lean=-6, layers=4)
        for sy, sc, s in [(38, 1.2, col), (88, 1.0, col + 1), (140, 1.1, col + 2), (190, 0.9, col + 3)]:
            side = -1 if sy % 2 == 0 else 1
            draw_flower_shrub(surf, cx + side * (PILLAR_W // 2 - 14), BOT_TOP + sy, palette, scale=sc, seed=s)
        draw_pom_pom_vine(surf, cx + 22, TOP_H - 10, 72, palette, seed=col)
        draw_pom_pom_vine(surf, cx - 30, TOP_H - 8, 50, palette, seed=col + 7)
        for gx, gy in [(-30, 40), (22, 80), (-18, 130), (28, 170), (-26, 210)]:
            draw_grass_tuft(surf, cx + gx, (BOT_TOP if gy >= 40 else TOP_H) + gy, palette, seed=col + gy)
        for off in (-22, -10, 6, 18):
            draw_moss_strand(surf, cx + off, TOP_H - 16, 14 + abs(off) % 6, palette, jitter_seed=col + off)
        draw_paper_lantern(surf, cx - 14, TOP_H - 4, strand_len=22, scale=1.4, color='red')
        draw_paper_lantern(surf, cx + 16, TOP_H - 6, strand_len=32, scale=0.9, color='gold')
        draw_lantern_string(surf, cx - 56, TOP_H - 2, cx + 46, TOP_H + 2, n=4)
        for lx, ly, clr in [(cx - 44, TOP_H + 44, 'gold'), (cx + 40, TOP_H + 82, 'white'),
                             (cx - 20, TOP_H + 120, 'blue'), (cx + 18, TOP_H + 168, 'pink')]:
            draw_paper_lantern(surf, lx, ly, strand_len=6, scale=0.55, color=clr)
        draw_ledge_lantern(surf, cx - PILLAR_W // 2 + 24, BOT_TOP + 160)
        draw_ledge_lantern(surf, cx + PILLAR_W // 2 - 24, BOT_TOP + 100)
        for fx, fy in [(cx - 58, TOP_H + 60), (cx + 54, TOP_H + 110), (cx - 24, TOP_H + 160),
                        (cx + 24, TOP_H + 40), (cx + 70, TOP_H + 190), (cx - 70, TOP_H + 200)]:
            draw_firefly(surf, fx, fy)
        draw_moth(surf, cx + 10, TOP_H + 24)
        draw_moth(surf, cx - 30, TOP_H + 80)
        return
    if "Crane" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 80, palette, lean=14, layers=6)
        draw_wuling_pine(surf, peak_x - 18, peak_y + 24, 46, palette, lean=-4, layers=4)
        draw_wuling_pine(surf, peak_x + 16, peak_y + 44, 36, palette, lean=6, layers=4)
        draw_side_shrub(surf, cx + PILLAR_W // 2 - 12, BOT_TOP + 45, palette, scale=1.1)
        draw_side_shrub(surf, cx - PILLAR_W // 2 + 12, BOT_TOP + 110, palette, scale=1.0)
        draw_side_shrub(surf, cx + PILLAR_W // 2 - 14, BOT_TOP + 170, palette, scale=0.9)
        for wx, wy in [(-10, 70), (14, 140), (-20, 200), (22, 220)]:
            draw_wildflowers(surf, cx + wx, BOT_TOP + wy, seed=col + wy)
        draw_berry_cluster(surf, peak_x + 6, peak_y - 50, seed=col)
        draw_berry_cluster(surf, peak_x - 14, peak_y - 22, seed=col + 5)
        draw_bird_nest(surf, peak_x - 6, peak_y - 42)
        for vx, vy, vl in [(-30, -10, 50), (18, -14, 46), (28, -6, 38)]:
            draw_pom_pom_vine(surf, cx + vx, TOP_H + vy, vl, palette, seed=col + vy)
        draw_crane(surf, peak_x - 20, peak_y + 10)
        draw_crane(surf, cx + PILLAR_W // 2 - 8, BOT_TOP + 200)
        for bx, by, sz in [(cx + 100, 70, 8), (cx + 120, 100, 6), (cx - 90, 60, 6), (cx - 110, 120, 7)]:
            draw_bird_silhouette(surf, bx, by, size=sz)
        for bf in [(cx - 18, BOT_TOP + 100, (230, 130, 60)), (cx + 26, BOT_TOP + 160, (90, 150, 230)),
                    (cx - 32, BOT_TOP + 200, (210, 90, 180)), (cx + 30, BOT_TOP + 80, (240, 190, 60))]:
            draw_butterfly(surf, bf[0], bf[1], wing_col=bf[2])
        draw_rabbit_silhouette(surf, cx + 18, GROUND_Y - 6)
        draw_mushrooms(surf, cx - 22, GROUND_Y - 6, n=5, seed=col)
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
        draw_wuling_pine(surf, peak_x + 10, peak_y + 6, 78, palette, lean=-8, layers=6)
        draw_wuling_pine(surf, peak_x - 16, peak_y + 30, 44, palette, lean=-4, layers=4)
        for off in (-18, -6, 8, 18):
            draw_moss_strand(surf, cx + off, TOP_H - 16, 12 + abs(off) % 5, palette, jitter_seed=col + off)
        for sy, sc in [(46, 1.2), (110, 0.9), (170, 1.0), (210, 0.8)]:
            side = -1 if sy % 2 == 0 else 1
            draw_side_shrub(surf, cx + side * (PILLAR_W // 2 - 10), BOT_TOP + sy, palette, scale=sc)
        for gx, gy in [(-22, 150), (16, 90), (-28, 80), (24, 40), (-12, 210)]:
            draw_grass_tuft(surf, cx + gx, BOT_TOP + gy, palette, seed=col + gy)
        draw_cairn(surf, peak_x - 18, peak_y + 6, stones=4, pennant=True)
        draw_cairn(surf, cx + PILLAR_W // 2 - 8, BOT_TOP + 130, stones=3, pennant=False)
        draw_cairn(surf, cx - PILLAR_W // 2 + 8, BOT_TOP + 200, stones=3, pennant=True)
        draw_pennant_string(surf, peak_x - 14, peak_y - 18, peak_x + 34, peak_y - 40, n=6)
        draw_pennant_string(surf, peak_x + 8, peak_y - 60, peak_x - 24, peak_y - 30, n=5)
        draw_signpost(surf, cx - 30, GROUND_Y - 2)
        draw_walking_stick(surf, cx + 18, GROUND_Y - 2, lean=8)
        draw_campfire(surf, cx + 2, GROUND_Y - 4)
        draw_wish_plaque(surf, peak_x + 6, peak_y - 28, cord_len=6)
        draw_wish_plaque(surf, peak_x - 10, peak_y + 18, cord_len=8)
        draw_raven(surf, peak_x - 18, peak_y - 16)
        draw_raven(surf, cx + PILLAR_W // 2 - 16, BOT_TOP + 40)
        return
    if "Bell Tower" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 74, palette, lean=10, layers=5)
        draw_wuling_pine(surf, peak_x - 18, peak_y + 26, 44, palette, lean=-6, layers=4)
        for ox in (-30, -18, -6, 6, 18, 30):
            draw_bell(surf, cx + ox, TOP_H - 6)
        draw_wind_chime(surf, cx - 20, TOP_H - 30)
        draw_wind_chime(surf, cx + 22, TOP_H - 30)
        for off in (-22, -8, 6, 20):
            draw_moss_strand(surf, cx + off, TOP_H - 14, 14 + abs(off) % 6, palette, jitter_seed=col + off)
        for sy, sc in [(60, 1.1), (120, 0.9), (180, 1.0)]:
            side = -1 if sy % 2 == 0 else 1
            draw_side_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc)
        draw_paper_lantern(surf, cx - 14, TOP_H - 2, strand_len=20, scale=1.0, color='gold')
        draw_paper_lantern(surf, cx + 16, TOP_H - 2, strand_len=20, scale=1.0, color='red')
        draw_pennant_string(surf, cx - 40, TOP_H + 10, cx + 40, TOP_H + 30, n=5)
        draw_stupa(surf, cx - 4, GROUND_Y - 10)
        draw_grass_tuft(surf, cx + 22, GROUND_Y - 4, palette, seed=col)
        return
    if "Twin Fangs" in name:
        for px, py, h, ly in [(peak_x - 8, peak_y + 2, 80, 6), (peak_x + 14, peak_y + 12, 62, 5),
                                (peak_x - 22, peak_y + 26, 42, 4)]:
            draw_wuling_pine(surf, px, py, h, palette, lean=(px - peak_x) // 3, layers=ly)
        for off, ln in ((-26, 26), (-10, 32), (6, 28), (22, 20), (32, 18)):
            draw_moss_strand(surf, cx + off, TOP_H - 10, ln, palette, jitter_seed=col + off)
        draw_pom_pom_vine(surf, cx + 34, TOP_H - 12, 56, palette, seed=col)
        draw_pom_pom_vine(surf, cx - 36, TOP_H - 18, 42, palette, seed=col + 3)
        for sy, sc in [(50, 1.1), (110, 1.0), (170, 0.9), (220, 0.8)]:
            side = 1 if sy % 2 == 0 else -1
            draw_flower_shrub(surf, cx + side * (PILLAR_W // 2 - 14), BOT_TOP + sy, palette, scale=sc, seed=col + sy)
        draw_berry_cluster(surf, peak_x + 8, peak_y - 50, seed=col)
        draw_berry_cluster(surf, peak_x - 12, peak_y - 10, seed=col + 3)
        draw_raven(surf, peak_x - 26, peak_y - 4)
        draw_raven(surf, peak_x + 14, peak_y - 22)
        return
    if "Fortress" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 72, palette, lean=8, layers=5)
        draw_wuling_pine(surf, peak_x - 18, peak_y + 20, 50, palette, lean=-6, layers=4)
        draw_wuling_pine(surf, peak_x + 18, peak_y + 34, 38, palette, lean=6, layers=4)
        for bx in (-30, -12, 8, 28):
            draw_banner(surf, cx + bx, TOP_H - 4, length=42,
                        color=[(180, 40, 50), (40, 80, 170), (200, 150, 40), (60, 140, 60)][(bx + 30) // 20 % 4],
                        seed=col + bx)
        for off in (-24, -10, 6, 22):
            draw_moss_strand(surf, cx + off, TOP_H - 14, 14, palette, jitter_seed=col + off)
        draw_cairn(surf, peak_x - 24, peak_y + 6, stones=3, pennant=False)
        draw_pennant_string(surf, peak_x - 14, peak_y - 22, peak_x + 34, peak_y - 44, n=6)
        for sy, sc in [(50, 1.2), (110, 0.9), (170, 1.1), (220, 0.8)]:
            side = -1 if sy % 2 == 0 else 1
            draw_side_shrub(surf, cx + side * (PILLAR_W // 2 - 10), BOT_TOP + sy, palette, scale=sc)
        draw_signpost(surf, cx - 28, GROUND_Y - 2)
        draw_walking_stick(surf, cx + 20, GROUND_Y - 2, lean=6)
        draw_campfire(surf, cx + 4, GROUND_Y - 4)
        return
    if "Stepped Shrine" in name:
        draw_wuling_pine(surf, peak_x - 2, peak_y + 6, 70, palette, lean=6, layers=5)
        draw_wuling_pine(surf, peak_x + 18, peak_y + 28, 42, palette, lean=-4, layers=4)
        for lx, ly, clr in [(cx - 36, TOP_H + 2, 'red'), (cx - 12, TOP_H + 2, 'gold'),
                             (cx + 12, TOP_H + 2, 'white'), (cx + 36, TOP_H + 2, 'blue')]:
            draw_paper_lantern(surf, lx, ly, strand_len=8, scale=0.7, color=clr)
        draw_prayer_flags(surf, cx - 38, TOP_H - 40, cx + 38, TOP_H - 50, n=7, bells=True)
        for sy, sc in [(40, 1.1), (100, 1.0), (150, 0.9), (200, 1.0)]:
            side = -1 if sy % 2 == 0 else 1
            draw_flower_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc, seed=col + sy)
        for off in (-28, -14, 4, 18, 30):
            draw_moss_strand(surf, cx + off, TOP_H - 14, 14 + abs(off) % 5, palette, jitter_seed=col + off)
        draw_stupa(surf, cx - 6, GROUND_Y - 10)
        draw_incense_smoke(surf, cx - 6, GROUND_Y - 34, length=30)
        draw_wish_plaque(surf, peak_x + 10, peak_y - 24, cord_len=8)
        draw_bell(surf, peak_x - 18, peak_y - 10)
        return
    if "Night Market" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 74, palette, lean=10, layers=5)
        draw_wuling_pine(surf, peak_x - 18, peak_y + 24, 44, palette, lean=-8, layers=4)
        colors = ['red', 'gold', 'white', 'blue', 'pink', 'green']
        for i, dx in enumerate((-40, -24, -8, 8, 24, 40)):
            draw_paper_lantern(surf, cx + dx, TOP_H - 4, strand_len=12 + (i % 3) * 6,
                               scale=0.7 + (i % 2) * 0.2, color=colors[i])
        draw_lantern_string(surf, cx - 56, TOP_H + 30, cx + 56, TOP_H + 40, n=5)
        draw_lantern_string(surf, cx - 50, TOP_H + 110, cx + 50, TOP_H + 120, n=4)
        for lx, ly, clr in [(cx - 34, TOP_H + 170, 'gold'), (cx + 32, TOP_H + 200, 'pink'),
                             (cx - 10, TOP_H + 160, 'red'), (cx + 16, TOP_H + 140, 'blue')]:
            draw_paper_lantern(surf, lx, ly, strand_len=6, scale=0.5, color=clr)
        draw_ledge_lantern(surf, cx - PILLAR_W // 2 + 24, BOT_TOP + 80)
        draw_ledge_lantern(surf, cx + PILLAR_W // 2 - 24, BOT_TOP + 140)
        for fx, fy in [(cx - 62, TOP_H + 50), (cx + 60, TOP_H + 150), (cx - 24, TOP_H + 210)]:
            draw_firefly(surf, fx, fy)
        for sy, sc in [(60, 1.0), (170, 0.9)]:
            side = -1 if sy % 2 == 0 else 1
            draw_side_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc)
        return
    if "Mushroom Grotto" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 72, palette, lean=10, layers=5)
        draw_wuling_pine(surf, peak_x - 14, peak_y + 24, 44, palette, lean=-6, layers=4)
        for off in (-28, -14, 0, 14, 28):
            draw_moss_strand(surf, cx + off, TOP_H - 12, 22 + abs(off) % 8, palette, jitter_seed=col + off)
        for mx, n in [(-30, 4), (-10, 5), (14, 4), (32, 3)]:
            draw_mushrooms(surf, cx + mx, GROUND_Y - 6, n=n, seed=col + mx)
        for sy, sc in [(44, 1.2), (90, 1.0), (140, 1.1), (190, 1.0), (220, 0.8)]:
            side = -1 if sy % 2 == 0 else 1
            draw_flower_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc, seed=col + sy)
        draw_pom_pom_vine(surf, cx + 30, TOP_H - 10, 76, palette, seed=col)
        draw_pom_pom_vine(surf, cx - 36, TOP_H - 10, 56, palette, seed=col + 7)
        draw_berry_cluster(surf, peak_x + 4, peak_y - 50, seed=col)
        draw_rabbit_silhouette(surf, cx - 10, GROUND_Y - 6)
        for fx, fy in [(cx - 20, TOP_H + 90), (cx + 30, TOP_H + 160), (cx - 30, TOP_H + 200)]:
            draw_firefly(surf, fx, fy)
        return
    if "Moss Cascade" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 86, palette, lean=8, layers=7)
        draw_wuling_pine(surf, peak_x - 20, peak_y + 28, 52, palette, lean=-6, layers=5)
        draw_wuling_pine(surf, peak_x + 18, peak_y + 50, 36, palette, lean=4, layers=4)
        for off in range(-34, 36, 4):
            draw_moss_strand(surf, cx + off, TOP_H - 8, 28 + abs(off) % 14, palette, jitter_seed=col + off)
        for sy, sc in [(40, 1.2), (90, 1.0), (140, 1.1), (190, 0.9), (230, 0.8)]:
            side = -1 if sy % 2 == 0 else 1
            draw_side_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc)
        draw_berry_cluster(surf, peak_x + 6, peak_y - 50, seed=col)
        draw_berry_cluster(surf, peak_x - 14, peak_y - 20, seed=col + 3)
        draw_mushrooms(surf, cx - 20, GROUND_Y - 6, n=4, seed=col)
        for gx, gy in [(-30, 70), (26, 150), (-18, 210)]:
            draw_grass_tuft(surf, cx + gx, BOT_TOP + gy, palette, seed=col + gy)
        return
    if "Butterfly Garden" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 74, palette, lean=10, layers=5)
        draw_wuling_pine(surf, peak_x - 18, peak_y + 26, 44, palette, lean=-6, layers=4)
        for sy, sc in [(44, 1.3), (90, 1.1), (140, 1.2), (180, 1.0), (220, 0.9)]:
            side = -1 if sy % 2 == 0 else 1
            draw_flower_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc, seed=col + sy)
        for wx, wy in [(-10, 60), (14, 120), (-20, 170), (22, 220), (0, 240)]:
            draw_wildflowers(surf, cx + wx, BOT_TOP + wy, seed=col + wy)
        for bf in [(cx - 30, TOP_H + 40, (230, 130, 60)), (cx + 30, TOP_H + 80, (90, 150, 230)),
                    (cx - 18, TOP_H + 130, (210, 90, 180)), (cx + 26, TOP_H + 180, (240, 190, 60)),
                    (cx - 38, TOP_H + 200, (150, 100, 200)), (cx + 14, TOP_H + 60, (230, 150, 150)),
                    (cx - 8, BOT_TOP + 60, (90, 200, 150)), (cx + 34, BOT_TOP + 140, (250, 160, 90))]:
            draw_butterfly(surf, bf[0], bf[1], wing_col=bf[2])
        draw_bird_nest(surf, peak_x - 6, peak_y - 40)
        draw_berry_cluster(surf, peak_x + 8, peak_y - 54, seed=col)
        for bx, by, sz in [(cx + 100, 70, 7), (cx - 90, 110, 6)]:
            draw_bird_silhouette(surf, bx, by, size=sz)
        return
    if "Banner Keep" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 72, palette, lean=8, layers=5)
        draw_wuling_pine(surf, peak_x - 18, peak_y + 26, 42, palette, lean=-6, layers=4)
        banner_colors = [(200, 40, 50), (40, 80, 170), (220, 160, 40), (60, 140, 60), (160, 60, 160)]
        for i, dx in enumerate((-38, -20, -2, 16, 34)):
            draw_banner(surf, cx + dx, TOP_H - 2, length=50 + (i % 3) * 8,
                        color=banner_colors[i], seed=col + i)
        draw_pennant_string(surf, cx - 38, TOP_H + 30, cx + 38, TOP_H + 50, n=7)
        draw_pennant_string(surf, cx - 34, TOP_H + 80, cx + 34, TOP_H + 100, n=6)
        for off in (-24, -8, 8, 24):
            draw_moss_strand(surf, cx + off, TOP_H - 14, 12, palette, jitter_seed=col + off)
        for sy, sc in [(50, 1.1), (110, 1.0), (170, 0.9), (220, 0.8)]:
            side = -1 if sy % 2 == 0 else 1
            draw_side_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc)
        draw_wish_plaque(surf, peak_x + 14, peak_y - 16, cord_len=8)
        draw_bell(surf, peak_x - 18, peak_y - 12)
        draw_signpost(surf, cx - 20, GROUND_Y - 2)
        return
    if "Raven Cliff" in name:
        draw_wuling_pine(surf, peak_x - 4, peak_y + 4, 72, palette, lean=4, layers=5)
        draw_wuling_pine(surf, peak_x + 18, peak_y + 24, 44, palette, lean=-6, layers=4)
        for off in (-24, -10, 4, 18):
            draw_moss_strand(surf, cx + off, TOP_H - 10, 16 + abs(off) % 8, palette, jitter_seed=col + off)
        for rx, ry in [(-24, -12), (10, -22), (20, -4), (-14, 8), (28, 14), (-28, -28), (4, -40)]:
            draw_raven(surf, peak_x + rx, peak_y + ry)
        draw_cairn(surf, peak_x - 14, peak_y + 10, stones=4, pennant=True)
        draw_cairn(surf, cx + PILLAR_W // 2 - 10, BOT_TOP + 170, stones=3, pennant=False)
        for sy, sc in [(52, 1.0), (120, 0.9), (180, 1.0)]:
            side = -1 if sy % 2 == 0 else 1
            draw_side_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc)
        for bx, by, sz in [(cx - 100, 60, 7), (cx + 110, 90, 6), (cx - 80, 130, 6), (cx + 90, 160, 5)]:
            draw_bird_silhouette(surf, bx, by, size=sz)
        draw_walking_stick(surf, cx + 14, GROUND_Y - 2, lean=6)
        draw_campfire(surf, cx - 8, GROUND_Y - 4)
        return
    if "Firefly Hollow" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 76, palette, lean=10, layers=5)
        draw_wuling_pine(surf, peak_x - 20, peak_y + 24, 46, palette, lean=-6, layers=4)
        for off in (-22, -8, 6, 20):
            draw_moss_strand(surf, cx + off, TOP_H - 12, 16 + abs(off) % 6, palette, jitter_seed=col + off)
        for sy, sc in [(48, 1.1), (100, 0.9), (150, 1.0), (200, 0.9)]:
            side = -1 if sy % 2 == 0 else 1
            draw_flower_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc, seed=col + sy)
        draw_pom_pom_vine(surf, cx + 28, TOP_H - 10, 68, palette, seed=col)
        draw_pom_pom_vine(surf, cx - 32, TOP_H - 12, 52, palette, seed=col + 4)
        positions = [(-60, 40), (-40, 80), (-20, 60), (10, 100), (30, 70), (50, 130),
                     (-50, 150), (-20, 180), (20, 180), (40, 210), (-70, 220), (60, 200),
                     (-30, 120), (40, 40)]
        for fx, fy in positions:
            draw_firefly(surf, cx + fx, TOP_H + fy)
        draw_moth(surf, cx + 10, TOP_H + 30)
        draw_moth(surf, cx - 20, TOP_H + 100)
        draw_rabbit_silhouette(surf, cx + 14, GROUND_Y - 6)
        draw_mushrooms(surf, cx - 20, GROUND_Y - 6, n=4, seed=col)
        return
    if "Forest Summit" in name:
        for px, py, h, ly in [(peak_x, peak_y + 2, 96, 7), (peak_x - 22, peak_y + 20, 64, 6),
                                (peak_x + 22, peak_y + 34, 50, 5), (peak_x - 10, peak_y + 58, 40, 4),
                                (peak_x + 6, peak_y + 80, 32, 4)]:
            draw_wuling_pine(surf, px, py, h, palette, lean=(px - peak_x) // 4, layers=ly)
        for off in (-28, -12, 4, 18, 30):
            draw_moss_strand(surf, cx + off, TOP_H - 12, 14 + abs(off) % 6, palette, jitter_seed=col + off)
        for sy, sc in [(60, 1.1), (130, 1.0), (190, 0.9), (230, 0.8)]:
            side = -1 if sy % 2 == 0 else 1
            draw_side_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc)
        draw_berry_cluster(surf, peak_x + 6, peak_y - 60, seed=col)
        draw_berry_cluster(surf, peak_x - 14, peak_y - 30, seed=col + 3)
        draw_bird_nest(surf, peak_x - 4, peak_y - 48)
        draw_mushrooms(surf, cx - 22, GROUND_Y - 6, n=4, seed=col)
        draw_mushrooms(surf, cx + 18, GROUND_Y - 5, n=3, seed=col + 5)
        for bx, by, sz in [(cx + 110, 60, 6), (cx - 100, 80, 7), (cx + 90, 140, 5)]:
            draw_bird_silhouette(surf, bx, by, size=sz)
        return
    if "Chime Pagoda" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 72, palette, lean=8, layers=5)
        draw_wuling_pine(surf, peak_x - 18, peak_y + 24, 44, palette, lean=-6, layers=4)
        for cx_off in (-36, -18, 0, 18, 36):
            draw_wind_chime(surf, cx + cx_off, TOP_H - 6)
        for bx in (-28, -8, 10, 26):
            draw_bell(surf, cx + bx, TOP_H + 44)
        draw_pennant_string(surf, cx - 38, TOP_H + 70, cx + 38, TOP_H + 80, n=6)
        for off in (-22, -6, 10, 22):
            draw_moss_strand(surf, cx + off, TOP_H - 14, 14, palette, jitter_seed=col + off)
        for sy, sc in [(60, 1.1), (130, 1.0), (190, 0.9)]:
            side = -1 if sy % 2 == 0 else 1
            draw_side_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc)
        draw_stupa(surf, cx - 6, GROUND_Y - 10)
        draw_incense_smoke(surf, cx - 6, GROUND_Y - 34, length=30)
        draw_wish_plaque(surf, peak_x + 14, peak_y - 20, cord_len=8)
        return
    if "Festival Arch" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 72, palette, lean=8, layers=5)
        draw_wuling_pine(surf, peak_x - 18, peak_y + 26, 42, palette, lean=-6, layers=4)
        colors = ['red', 'gold', 'pink', 'blue', 'white', 'green']
        for i, dx in enumerate((-42, -26, -10, 6, 22, 38)):
            draw_paper_lantern(surf, cx + dx, TOP_H - 2, strand_len=10 + (i % 3) * 8,
                               scale=0.8 + (i % 2) * 0.1, color=colors[i])
        draw_lantern_string(surf, cx - 58, TOP_H + 38, cx + 58, TOP_H + 52, n=6)
        draw_prayer_flags(surf, cx - 56, TOP_H + 90, cx + 56, TOP_H + 100, n=8, bells=True)
        draw_pennant_string(surf, cx - 50, TOP_H + 140, cx + 50, TOP_H + 150, n=7)
        for i in range(5):
            dy = TOP_H + 180 + i * 10
            draw_banner(surf, cx - 40 + i * 20, dy, length=28,
                        color=[(200, 40, 50), (220, 160, 40), (60, 140, 60), (40, 100, 180), (180, 80, 160)][i],
                        seed=col + i)
        for sy, sc in [(60, 1.0), (140, 0.9), (200, 1.0)]:
            side = -1 if sy % 2 == 0 else 1
            draw_flower_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc, seed=col + sy)
        return
    if "Wildflower Crest" in name:
        draw_wuling_pine(surf, peak_x, peak_y + 2, 80, palette, lean=10, layers=6)
        draw_wuling_pine(surf, peak_x - 18, peak_y + 22, 50, palette, lean=-6, layers=5)
        draw_wuling_pine(surf, peak_x + 18, peak_y + 40, 38, palette, lean=6, layers=4)
        for sy, sc in [(40, 1.3), (90, 1.2), (140, 1.1), (190, 1.0), (230, 0.9)]:
            side = -1 if sy % 2 == 0 else 1
            draw_flower_shrub(surf, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc, seed=col + sy)
        for wx, wy in [(-20, 50), (14, 100), (-26, 160), (22, 200), (-10, 230), (30, 60), (-30, 130)]:
            draw_wildflowers(surf, cx + wx, BOT_TOP + wy, seed=col + wy)
        for off in (-22, -8, 8, 22):
            draw_moss_strand(surf, cx + off, TOP_H - 12, 14, palette, jitter_seed=col + off)
        draw_berry_cluster(surf, peak_x + 6, peak_y - 50, seed=col)
        draw_berry_cluster(surf, peak_x - 14, peak_y - 22, seed=col + 3)
        for bf in [(cx - 24, BOT_TOP + 120, (230, 130, 60)), (cx + 26, BOT_TOP + 170, (90, 150, 230)),
                    (cx - 34, BOT_TOP + 210, (210, 90, 180)), (cx + 14, TOP_H + 60, (240, 190, 60))]:
            draw_butterfly(surf, bf[0], bf[1], wing_col=bf[2])
        draw_pom_pom_vine(surf, cx + 30, TOP_H - 10, 56, palette, seed=col)
        draw_mushrooms(surf, cx - 20, GROUND_Y - 6, n=3, seed=col)
        for bx, by, sz in [(cx + 100, 60, 6), (cx - 90, 90, 7)]:
            draw_bird_silhouette(surf, bx, by, size=sz)
        return


def label(surf, col, row, title, font):
    cx = col * W_CELL + W_CELL // 2
    y_base = row * H_CELL + 6
    t = font.render(title, True, (18, 18, 26))
    pad = 6
    w = t.get_width() + pad * 2
    h = t.get_height() + pad
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill((255, 255, 255, 225))
    surf.blit(bg, (cx - w // 2, y_base))
    surf.blit(t, (cx - t.get_width() // 2, y_base + pad // 2))


VARIANTS.extend([
    dict(name="01 Pilgrim's Peak",   top_sil=silhouette_top_spire),
    dict(name="02 Ribbon Pine",      top_sil=sil_spike),
    dict(name="03 Lantern Ledge",    top_sil=silhouette_top_spire),
    dict(name="04 Crane's Rest",     top_sil=sil_flat),
    dict(name="05 Cairn Marker",     top_sil=sil_spike),
    dict(name="06 Bell Tower",       top_sil=sil_bell),
    dict(name="07 Twin Fangs",       top_sil=sil_twin),
    dict(name="08 Fortress Notch",   top_sil=sil_notched),
    dict(name="09 Stepped Shrine",   top_sil=sil_stepped),
    dict(name="10 Night Market",     top_sil=sil_flat),
    dict(name="11 Mushroom Grotto",  top_sil=sil_bell),
    dict(name="12 Moss Cascade",     top_sil=silhouette_top_spire),
    dict(name="13 Butterfly Garden", top_sil=sil_flat),
    dict(name="14 Banner Keep",      top_sil=sil_notched),
    dict(name="15 Raven Cliff",      top_sil=sil_twin),
    dict(name="16 Firefly Hollow",   top_sil=sil_spike),
    dict(name="17 Forest Summit",    top_sil=sil_stepped),
    dict(name="18 Chime Pagoda",     top_sil=sil_bell),
    dict(name="19 Festival Arch",    top_sil=sil_flat),
    dict(name="20 Wildflower Crest", top_sil=silhouette_top_spire),
])


def main():
    pygame.init()
    surf = pygame.Surface((W, H))
    paint_bg(surf)
    for idx, v in enumerate(VARIANTS):
        col, row = idx % COLS, idx // COLS
        cell = pygame.Surface((W_CELL, H_CELL), pygame.SRCALPHA)
        draw_pair(cell, idx, v)
        surf.blit(cell, (col * W_CELL, row * H_CELL))
    font = pygame.font.SysFont("arial", 14, bold=True)
    for idx, v in enumerate(VARIANTS):
        col, row = idx % COLS, idx // COLS
        label(surf, col, row, v['name'], font)
    out = "/home/user/Claude_test/docs/sketches/pillar_variants.png"
    pygame.image.save(surf, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
