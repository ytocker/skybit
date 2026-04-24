"""Render the 10 pillar-redesign options side-by-side (5 columns x 2 rows)."""
import os, math, random, sys, pathlib
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import pygame

from game.draw import (
    get_stone_pillar_body,
    silhouette_bottom_spire, silhouette_top_spire, silhouette_blit,
    draw_wuling_pine, draw_moss_strand, draw_side_shrub, draw_pillar_mist,
    lerp_color,
)

W_CELL, H_CELL = 300, 820
COLS, ROWS = 5, 2
W, H = W_CELL * COLS, H_CELL * ROWS
TOP_H = 240
GAP_H = 230
BOT_TOP = TOP_H + GAP_H
GROUND_Y = H_CELL - 40
PILLAR_W = 96

FOLIAGE = dict(foliage_top=(140, 220, 110), foliage_mid=(70, 170, 75),
               foliage_dark=(30, 100, 50), foliage_accent=(255, 240, 120))
STONE_L, STONE_M, STONE_D, STONE_A = (225, 195, 155), (175, 140, 105), (95, 70, 55), (255, 220, 170)
PALETTE = dict(FOLIAGE, stone_light=STONE_L, stone_mid=STONE_M, stone_dark=STONE_D, stone_accent=STONE_A)

def sil_bot_stout(w, h):
    # realistic stout column: subtle taper only, natural pillar proportions
    return [(0, 0), (w, 0), (int(w * 0.94), int(h * 0.20)),
            (int(w * 0.90), int(h * 0.50)), (int(w * 0.86), int(h * 0.80)),
            (int(w * 0.80), h), (int(w * 0.20), h),
            (int(w * 0.14), int(h * 0.80)), (int(w * 0.10), int(h * 0.50)),
            (int(w * 0.06), int(h * 0.20))]


def sil_bot_slender(w, h):
    # realistic slender spire: stronger taper, natural pointed-ish top
    return [(0, 0), (w, 0), (int(w * 0.80), int(h * 0.25)),
            (int(w * 0.74), int(h * 0.60)), (int(w * 0.66), int(h * 0.85)),
            (int(w * 0.60), h), (int(w * 0.40), h),
            (int(w * 0.34), int(h * 0.85)), (int(w * 0.26), int(h * 0.60)),
            (int(w * 0.20), int(h * 0.25))]


def sil_bot_lean(w, h):
    # realistic column with slight 6-degree lean (natural weathering drift)
    lean = int(w * 0.06)
    return [(lean, 0), (w, 0), (int(w * 0.92), int(h * 0.25)),
            (int(w * 0.88), int(h * 0.55)), (int(w * 0.82), int(h * 0.82)),
            (int(w * 0.78), h), (int(w * 0.22), h),
            (int(w * 0.12) - lean, int(h * 0.82)), (int(w * 0.06) - lean, int(h * 0.55)),
            (int(w * 0.00), int(h * 0.25))]


def sil_bot_eroded(w, h):
    # realistic weathered column: subtle asymmetric bulges + a shelf break
    return [(0, 0), (w, 0), (int(w * 0.96), int(h * 0.18)),
            (int(w * 0.88), int(h * 0.40)), (w, int(h * 0.55)),
            (int(w * 0.92), int(h * 0.68)), (int(w * 0.84), int(h * 0.82)),
            (int(w * 0.78), h), (int(w * 0.22), h),
            (int(w * 0.14), int(h * 0.82)), (int(w * 0.08), int(h * 0.68)),
            (0, int(h * 0.55)), (int(w * 0.10), int(h * 0.40)),
            (int(w * 0.04), int(h * 0.18))]


def sil_bot_blunt(w, h):
    # realistic stout column with broader flat-ish top (menhir-ish but natural)
    return [(0, 0), (w, 0), (w, int(h * 0.18)),
            (int(w * 0.94), int(h * 0.45)), (int(w * 0.90), int(h * 0.75)),
            (int(w * 0.82), h), (int(w * 0.18), h),
            (int(w * 0.10), int(h * 0.75)), (int(w * 0.06), int(h * 0.45)),
            (0, int(h * 0.18))]


def sil_bot_shelf(w, h):
    # realistic column with a small lower shelf (one natural break, not a staircase)
    return [(0, 0), (w, 0), (int(w * 0.92), int(h * 0.22)),
            (int(w * 0.86), int(h * 0.50)), (int(w * 0.82), int(h * 0.62)),
            (int(w * 0.96), int(h * 0.66)), (int(w * 0.88), int(h * 0.85)),
            (int(w * 0.80), h), (int(w * 0.20), h),
            (int(w * 0.12), int(h * 0.85)), (int(w * 0.04), int(h * 0.66)),
            (int(w * 0.18), int(h * 0.62)), (int(w * 0.14), int(h * 0.50)),
            (int(w * 0.08), int(h * 0.22))]


def overlay_flutes(surf, cx, pw):
    # faint vertical fluting dark stripes on both top and bottom pillar
    left = cx - pw // 2 + 6
    for i in range(5):
        x = left + i * ((pw - 12) // 4)
        pygame.draw.line(surf, (60, 48, 40), (x, 18), (x, TOP_H - 14), 1)
        pygame.draw.line(surf, (60, 48, 40), (x, BOT_TOP + 14), (x, GROUND_Y - 14), 1)


OPTIONS = [
    dict(name="01 Lung-ta Pass"),
    dict(name="02 Shimenawa Stone", bot_sil=sil_bot_stout),
    dict(name="03 Darchog Sentinel", bot_sil=sil_bot_slender),
    dict(name="04 Babylon Terrace",  bot_sil=sil_bot_shelf),
    dict(name="05 Monastery Perch",  bot_sil=sil_bot_lean),
    dict(name="06 Lantern Festival", bot_sil=sil_bot_stout),
    dict(name="07 Basalt Organ",     overlay=overlay_flutes),
    dict(name="08 Hermit's Retreat", bot_sil=sil_bot_lean),
    dict(name="09 Overgrown Ruin",   bot_sil=sil_bot_eroded),
    dict(name="10 Menhir Shrine",    bot_sil=sil_bot_blunt),
]


def paint_bg(surf):
    for y in range(H):
        cy = y % H_CELL
        if cy >= H_CELL - 40:
            c = (60, 120, 60)
        else:
            t = cy / max(1, H_CELL - 41)
            c = (min(255, int(40 + 130 * t)), min(255, int(110 + 110 * t)), min(255, int(200 + 45 * t)))
        pygame.draw.line(surf, c, (0, y), (W - 1, y))


def draw_pair(cell, idx, opt):
    cx = W_CELL // 2
    top_sil = opt.get('top_sil', silhouette_top_spire)
    bot_sil = opt.get('bot_sil', silhouette_bottom_spire)
    pw = opt.get('pw', PILLAR_W)
    top_body = get_stone_pillar_body(pw, TOP_H, STONE_L, STONE_M, STONE_D, STONE_A, body_seed=idx * 3 + 1)
    silhouette_blit(cell, top_body, top_sil(pw, TOP_H), (cx - pw // 2, 0))
    bot_h = GROUND_Y - BOT_TOP
    bot_body = get_stone_pillar_body(pw, bot_h, STONE_L, STONE_M, STONE_D, STONE_A, body_seed=idx * 3 + 2)
    silhouette_blit(cell, bot_body, bot_sil(pw, bot_h), (cx - pw // 2, BOT_TOP))
    overlay = opt.get('overlay')
    if overlay:
        overlay(cell, cx, pw)
    decorate(cell, cx, PALETTE, opt['name'], idx)
    draw_pillar_mist(cell, cx, GROUND_Y - 4, pw, alpha=110)


FLAG_COLORS = [(70, 140, 230), (245, 245, 245), (230, 70, 70), (80, 180, 90), (245, 210, 70)]


def draw_prayer_flags(surf, x1, y1, x2, y2, n=8):
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
        pygame.draw.rect(surf, FLAG_COLORS[i % 5], (px - 4, py, 8, 11))
        pygame.draw.rect(surf, (40, 30, 20), (px - 4, py, 8, 11), 1)


def draw_bird_sil(surf, cx, cy, size=6):
    col = (45, 40, 55)
    pygame.draw.line(surf, col, (cx - size, cy + size // 2), (cx, cy - size // 3), 2)
    pygame.draw.line(surf, col, (cx, cy - size // 3), (cx + size, cy + size // 2), 2)


LANTERN = {'red': ((170, 30, 35), (230, 80, 65)), 'gold': ((190, 140, 40), (245, 210, 100))}


def draw_paper_lantern(surf, x, y, strand=16, scale=1.0, color='red'):
    dark, light = LANTERN.get(color, LANTERN['red'])
    pygame.draw.line(surf, (40, 30, 25), (x, y), (x, y + strand), 1)
    cy = y + strand
    lw, lh = max(8, int(16 * scale)), max(10, int(20 * scale))
    cap = max(2, int(3 * scale))
    pygame.draw.rect(surf, (55, 35, 25), (x - lw // 2 + 1, cy, lw - 2, cap))
    pygame.draw.rect(surf, (55, 35, 25), (x - lw // 2 + 1, cy + lh - cap, lw - 2, cap))
    body = pygame.Rect(x - lw // 2, cy + cap - 1, lw, lh - 2 * cap + 2)
    pygame.draw.ellipse(surf, dark, body)
    pygame.draw.ellipse(surf, light, body.inflate(-max(2, int(4 * scale)), -max(1, int(3 * scale))))
    gsz = max(8, int(22 * scale))
    g = pygame.Surface((gsz * 2, gsz * 2), pygame.SRCALPHA)
    pygame.draw.circle(g, (255, 215, 120, 100), (gsz, gsz), int(gsz * 0.55))
    pygame.draw.circle(g, (255, 240, 200, 170), (gsz, gsz), max(2, int(gsz * 0.28)))
    surf.blit(g, (x - gsz, cy + lh // 2 - gsz))


def draw_cairn(surf, cx, base_y, n=4, pennant=True):
    sizes = [(20, 9), (15, 7), (11, 5), (8, 4), (5, 3)][:n]
    cols = [(130, 115, 95), (155, 140, 115), (180, 160, 130), (200, 180, 145), (215, 195, 160)]
    y = base_y
    for (w, h), col in zip(sizes, cols):
        pygame.draw.ellipse(surf, (60, 45, 35), pygame.Rect(cx - w // 2, y - h, w, h).inflate(2, 1))
        pygame.draw.ellipse(surf, col, (cx - w // 2, y - h, w, h))
        y -= h - 1
    if pennant:
        pygame.draw.line(surf, (60, 45, 30), (cx, y), (cx, y - 14), 1)
        pygame.draw.polygon(surf, (200, 40, 45), [(cx, y - 14), (cx + 9, y - 11), (cx, y - 8)])


def draw_stupa(surf, cx, base_y):
    pygame.draw.rect(surf, (240, 235, 225), (cx - 9, base_y - 7, 18, 7))
    pygame.draw.ellipse(surf, (245, 240, 230), (cx - 8, base_y - 18, 16, 13))
    pygame.draw.rect(surf, (240, 235, 225), (cx - 2, base_y - 24, 4, 7))
    pygame.draw.polygon(surf, (220, 180, 60), [(cx, base_y - 28), (cx - 3, base_y - 24), (cx + 3, base_y - 24)])
    pygame.draw.rect(surf, (80, 60, 50), (cx - 2, base_y, 4, 3))


def draw_raven(surf, cx, cy):
    pygame.draw.ellipse(surf, (25, 25, 35), (cx - 5, cy - 3, 10, 6))
    pygame.draw.circle(surf, (20, 20, 30), (cx + 5, cy - 4), 3)
    pygame.draw.polygon(surf, (40, 35, 25), [(cx + 8, cy - 4), (cx + 11, cy - 3), (cx + 8, cy - 2)])


def draw_ribbons_tied(surf, cx, cy, n=4, width=14, seed=0):
    rng = random.Random(seed)
    colors = [(170, 90, 40), (140, 30, 50), (70, 110, 50), (200, 160, 90)]
    for i in range(n):
        col = colors[i % len(colors)]
        dx = rng.randint(-width // 2, width // 2)
        ty = cy + rng.randint(-2, 2)
        pygame.draw.rect(surf, col, (cx + dx - 1, ty, 2, 3))
        for j in range(6):
            t = j / 5
            tx = cx + dx + int(math.sin(t * 3 + seed) * 3)
            py = ty + 3 + j * 2
            pygame.draw.rect(surf, col, (tx - 1, py, 2, 2))


def draw_incense_smoke(surf, x, y, length=28):
    for i in range(length):
        t = i / length
        off = int(math.sin(t * 6) * 3)
        a = int(150 * (1 - t))
        s = pygame.Surface((5, 3), pygame.SRCALPHA)
        s.fill((230, 230, 230, a))
        surf.blit(s, (x + off - 2, y - i))


def draw_shimenawa(surf, cx, cy, width=54):
    # thick twisted rice-straw rope wrapped horizontally
    rope_h = 10
    pygame.draw.ellipse(surf, (130, 105, 60), (cx - width // 2, cy - rope_h // 2, width, rope_h))
    pygame.draw.ellipse(surf, (175, 145, 80), (cx - width // 2 + 2, cy - rope_h // 2 + 1, width - 4, rope_h - 2))
    for i in range(5):
        x = cx - width // 2 + 6 + i * ((width - 12) // 4)
        pygame.draw.line(surf, (95, 75, 40), (x, cy - rope_h // 2 + 2), (x + 4, cy + rope_h // 2 - 2), 1)
    # shide zigzag paper streamers hanging below
    for dx in (-width // 3, 0, width // 3):
        px = cx + dx
        py = cy + rope_h // 2
        pts = [(px, py), (px - 3, py + 4), (px + 3, py + 8), (px - 3, py + 12), (px + 3, py + 16)]
        for i in range(len(pts) - 1):
            pygame.draw.line(surf, (250, 250, 250), pts[i], pts[i + 1], 2)


def draw_torii(surf, cx, base_y):
    # two vertical pillars, two crossbeams — small red gate
    red = (190, 55, 50)
    pygame.draw.rect(surf, red, (cx - 14, base_y - 24, 3, 24))
    pygame.draw.rect(surf, red, (cx + 11, base_y - 24, 3, 24))
    pygame.draw.rect(surf, red, (cx - 18, base_y - 26, 36, 3))  # top beam
    pygame.draw.polygon(surf, red, [(cx - 20, base_y - 26), (cx + 20, base_y - 26), (cx + 18, base_y - 22), (cx - 18, base_y - 22)])
    pygame.draw.rect(surf, (60, 45, 30), (cx - 12, base_y - 18, 24, 2))  # cross-tie


def draw_darchog_pole(surf, cx, base_y, height=60, banner_color=(220, 120, 40)):
    # vertical pole with a tall cloth banner attached on the left
    top = base_y - height
    pygame.draw.line(surf, (60, 45, 30), (cx, base_y), (cx, top), 2)
    pygame.draw.circle(surf, (220, 180, 60), (cx, top), 2)
    bw = 10
    pts = [(cx, top + 4), (cx + bw, top + 6), (cx + bw + 1, base_y - 6),
            (cx - 1, base_y - 8)]
    pygame.draw.polygon(surf, banner_color, pts)
    pygame.draw.polygon(surf, (130, 60, 20), pts, 1)


def draw_terrace_wall(surf, cx, y, width=40):
    # short horizontal stone-block wall sitting on a ledge
    pygame.draw.rect(surf, (130, 105, 75), (cx - width // 2, y - 5, width, 5))
    pygame.draw.rect(surf, (170, 140, 105), (cx - width // 2, y - 5, width, 2))
    for i in range(1, 4):
        x = cx - width // 2 + i * (width // 4)
        pygame.draw.line(surf, (80, 60, 45), (x, y - 5), (x, y - 1), 1)


def draw_cascading_vine(surf, x, y, length=60, palette=None):
    col_dark = (30, 100, 50) if palette is None else palette['foliage_dark']
    col_mid = (70, 170, 75) if palette is None else palette['foliage_mid']
    col_top = (140, 220, 110) if palette is None else palette['foliage_top']
    for i in range(length):
        t = i / max(1, length - 1)
        off = int(math.sin(t * 4) * 2)
        pygame.draw.line(surf, col_dark, (x + off, y + i), (x + off, y + i + 1), 2)
    for frac, r in ((0.20, 3), (0.45, 4), (0.70, 3), (0.90, 5)):
        py = y + int(frac * length)
        px = x + int(math.sin(frac * 4) * 2)
        pygame.draw.circle(surf, col_dark, (px, py), r + 1)
        pygame.draw.circle(surf, col_mid, (px, py), r)
        pygame.draw.circle(surf, col_top, (px - 1, py - 1), max(1, r - 2))
        pygame.draw.circle(surf, (255, 180, 120), (px + 1, py + 1), 1)  # flower speck


def draw_ladder(surf, x, top_y, bot_y):
    # two uprights + rungs, leaning
    pygame.draw.line(surf, (110, 75, 45), (x - 2, top_y), (x + 4, bot_y), 2)
    pygame.draw.line(surf, (110, 75, 45), (x + 6, top_y), (x + 12, bot_y), 2)
    rungs = max(3, (bot_y - top_y) // 6)
    for i in range(1, rungs):
        t = i / rungs
        y = int(top_y + (bot_y - top_y) * t)
        pygame.draw.line(surf, (130, 90, 55), (x - 2 + int(6 * t), y), (x + 6 + int(6 * t), y), 1)


def draw_monastery(surf, cx, base_y):
    # 2-storey whitewashed building with red sloped roof + small windows (glow)
    body = pygame.Rect(cx - 14, base_y - 26, 28, 26)
    pygame.draw.rect(surf, (245, 240, 230), body)
    pygame.draw.rect(surf, (80, 60, 45), body, 1)
    # red sloped roof
    pygame.draw.polygon(surf, (170, 60, 45), [(cx - 17, base_y - 26), (cx + 17, base_y - 26), (cx + 13, base_y - 32), (cx - 13, base_y - 32)])
    pygame.draw.polygon(surf, (110, 40, 30), [(cx - 17, base_y - 26), (cx + 17, base_y - 26), (cx + 13, base_y - 32), (cx - 13, base_y - 32)], 1)
    # windows with warm glow
    for wx in (-6, 2):
        pygame.draw.rect(surf, (255, 210, 120), (cx + wx, base_y - 20, 3, 4))
        pygame.draw.rect(surf, (255, 210, 120), (cx + wx, base_y - 11, 3, 4))
    # floor divider line
    pygame.draw.line(surf, (80, 60, 45), (cx - 14, base_y - 16), (cx + 14, base_y - 16), 1)
    # small balcony underneath
    pygame.draw.rect(surf, (140, 100, 60), (cx - 15, base_y, 30, 2))
    # chimney smoke
    for i in range(14):
        s = pygame.Surface((4, 3), pygame.SRCALPHA)
        s.fill((230, 230, 230, int(140 * (1 - i / 14))))
        surf.blit(s, (cx + 8 + int(math.sin(i * 0.6) * 2), base_y - 34 - i * 2))


def draw_hermit_hut(surf, cx, base_y):
    # small wooden cabin with warm interior glow, thatched roof
    pygame.draw.rect(surf, (150, 110, 75), (cx - 10, base_y - 14, 20, 14))
    pygame.draw.rect(surf, (80, 55, 35), (cx - 10, base_y - 14, 20, 14), 1)
    pygame.draw.polygon(surf, (165, 135, 80), [(cx - 12, base_y - 14), (cx + 12, base_y - 14), (cx + 9, base_y - 21), (cx - 9, base_y - 21)])
    pygame.draw.polygon(surf, (95, 70, 40), [(cx - 12, base_y - 14), (cx + 12, base_y - 14), (cx + 9, base_y - 21), (cx - 9, base_y - 21)], 1)
    # open door with warm glow behind
    pygame.draw.rect(surf, (50, 35, 20), (cx - 3, base_y - 11, 6, 11))
    g = pygame.Surface((14, 14), pygame.SRCALPHA)
    pygame.draw.circle(g, (255, 210, 130, 130), (7, 7), 6)
    pygame.draw.circle(g, (255, 240, 200, 200), (7, 7), 3)
    surf.blit(g, (cx - 7, base_y - 13))


def draw_rope_bridge_stub(surf, x, y, dir=1):
    # two slack ropes dangling off a ledge with one remaining plank near top
    for i in range(14):
        t = i / 13
        rope_y = y + int(t * t * 30)
        pygame.draw.line(surf, (110, 80, 50), (x + dir * i, rope_y), (x + dir * (i + 1), rope_y + 1), 1)
        pygame.draw.line(surf, (110, 80, 50), (x + dir * i, rope_y + 4), (x + dir * (i + 1), rope_y + 5), 1)
    pygame.draw.rect(surf, (140, 95, 55), (x + dir * 2, y + 2, dir * 8, 3))


def draw_masonry_blocks(surf, cx, y_top, y_bot, pw):
    # 4 rectangular carved blocks visible through erosion, randomly placed
    rng = random.Random(42)
    for _ in range(5):
        bw = rng.randint(10, 18)
        bh = rng.randint(6, 10)
        bx = cx - pw // 2 + rng.randint(6, pw - bw - 6)
        by = rng.randint(y_top + 10, y_bot - bh - 10)
        pygame.draw.rect(surf, (80, 60, 45), (bx, by, bw, bh))
        pygame.draw.rect(surf, (130, 100, 75), (bx + 1, by + 1, bw - 2, bh - 2))
        pygame.draw.line(surf, (60, 45, 30), (bx + bw // 2, by), (bx + bw // 2, by + bh), 1)


def draw_stone_face(surf, cx, cy):
    # small carved serene face silhouette (Angkor-style), half overgrown
    pygame.draw.ellipse(surf, (135, 110, 80), (cx - 9, cy - 11, 18, 22))
    pygame.draw.ellipse(surf, (105, 85, 60), (cx - 9, cy - 11, 18, 22), 1)
    # eyes
    pygame.draw.arc(surf, (60, 45, 30), (cx - 7, cy - 4, 5, 3), math.pi, 2 * math.pi, 1)
    pygame.draw.arc(surf, (60, 45, 30), (cx + 2, cy - 4, 5, 3), math.pi, 2 * math.pi, 1)
    # mouth
    pygame.draw.arc(surf, (60, 45, 30), (cx - 3, cy + 2, 6, 4), 0, math.pi, 1)
    # moss overlay
    for i in range(5):
        pygame.draw.circle(surf, (60, 130, 60), (cx - 8 + i * 4, cy - 10), 2)


def draw_strangler_fig(surf, x, y_top, y_bot):
    # whitish root cascade — multiple wavy vertical lines bundled
    for j in range(5):
        dx = j * 3
        for i in range(y_bot - y_top):
            wob = int(math.sin((i + j * 5) * 0.18) * 3)
            px = x + dx + wob
            py = y_top + i
            pygame.draw.line(surf, (220, 210, 190), (px, py), (px + 1, py), 1)
    # gnarly roots at base
    pygame.draw.ellipse(surf, (200, 190, 165), (x - 4, y_bot - 6, 22, 8))


def draw_spiral_glow(surf, cx, cy, radius=12):
    # faint radial glow + spiral stroke on top of it
    g = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
    pygame.draw.circle(g, (255, 210, 150, 80), (radius * 3 // 2, radius * 3 // 2), radius + 2)
    pygame.draw.circle(g, (255, 230, 180, 150), (radius * 3 // 2, radius * 3 // 2), radius // 2)
    surf.blit(g, (cx - radius * 3 // 2, cy - radius * 3 // 2))
    pts = []
    for i in range(30):
        t = i / 29
        r = radius * (1 - t)
        a = t * 4 * math.pi
        pts.append((cx + int(math.cos(a) * r), cy + int(math.sin(a) * r)))
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, (255, 180, 80), pts[i], pts[i + 1], 1)


def draw_moss_patch(cell, cx, cy, w, h, palette, seed=0):
    # irregular moss coverage — layered blobs
    rng = random.Random(seed)
    dark, mid, top = palette['foliage_dark'], palette['foliage_mid'], palette['foliage_top']
    for _ in range(max(6, (w * h) // 50)):
        dx = rng.randint(-w // 2, w // 2)
        dy = rng.randint(-h // 2, h // 2)
        r = rng.randint(3, 6)
        pygame.draw.circle(cell, dark, (cx + dx, cy + dy), r + 1)
        pygame.draw.circle(cell, mid, (cx + dx, cy + dy), r)
        pygame.draw.circle(cell, top, (cx + dx - 1, cy + dy - 1), max(1, r - 2))


def draw_fern_cluster(cell, cx, cy, n=6, palette=None, seed=0):
    rng = random.Random(seed)
    dark = (30, 110, 50) if palette is None else palette['foliage_dark']
    mid = (70, 170, 75) if palette is None else palette['foliage_mid']
    top = (140, 220, 110) if palette is None else palette['foliage_top']
    for i in range(n):
        dx = (i - n // 2) * 3 + rng.randint(-1, 1)
        lean = rng.randint(-3, 3)
        length = rng.randint(10, 18)
        stem_bot = (cx + dx, cy)
        stem_top = (cx + dx + lean, cy - length)
        pygame.draw.line(cell, dark, stem_bot, stem_top, 2)
        # pinnae along the stem
        for j in range(1, 5):
            t = j / 5
            px = int(stem_bot[0] + (stem_top[0] - stem_bot[0]) * t)
            py = int(stem_bot[1] + (stem_top[1] - stem_bot[1]) * t)
            plen = 4 - j
            pygame.draw.line(cell, mid, (px, py), (px - plen, py - 1), 1)
            pygame.draw.line(cell, mid, (px, py), (px + plen, py - 1), 1)
        pygame.draw.line(cell, top, stem_top, (stem_top[0], stem_top[1] - 2), 2)


def draw_pine_trio(cell, peak_x, peak_y, palette, seed=0):
    rng = random.Random(seed)
    draw_wuling_pine(cell, peak_x, peak_y + 2, 86, palette, lean=10, layers=6)
    draw_wuling_pine(cell, peak_x - 20, peak_y + 22, 56, palette, lean=-6, layers=5)
    draw_wuling_pine(cell, peak_x + 18, peak_y + 36, 42, palette, lean=6, layers=4)
    # small companion sapling / bushy foliage
    for dx, dy, sz in [(-34, 44, 12), (28, 60, 10), (-10, 68, 8)]:
        pygame.draw.ellipse(cell, palette['foliage_dark'], (peak_x + dx - sz, peak_y + dy - sz // 2, sz * 2, sz))
        pygame.draw.ellipse(cell, palette['foliage_mid'], (peak_x + dx - sz + 2, peak_y + dy - sz // 2 + 1, sz * 2 - 4, sz - 2))


def draw_climbing_vine(cell, x, y_top, y_bot, palette, seed=0):
    rng = random.Random(seed)
    dark, mid, top = palette['foliage_dark'], palette['foliage_mid'], palette['foliage_top']
    for i in range(y_bot - y_top):
        wob = int(math.sin((i + seed) * 0.16) * 3)
        px = x + wob
        py = y_top + i
        pygame.draw.line(cell, dark, (px, py), (px + 1, py), 2)
        if i % 5 == 0:
            side = 1 if (i // 5) % 2 == 0 else -1
            leaf_x = px + side * 3
            pygame.draw.ellipse(cell, dark, (leaf_x - 3, py - 2, 6, 4))
            pygame.draw.ellipse(cell, mid, (leaf_x - 2, py - 1, 4, 3))
            pygame.draw.ellipse(cell, top, (leaf_x - 1, py - 1, 2, 2))


def draw_grass_bed(cell, cx, cy, width=60, density=14, palette=None, seed=0):
    rng = random.Random(seed)
    mid = (70, 170, 75) if palette is None else palette['foliage_mid']
    top = (140, 220, 110) if palette is None else palette['foliage_top']
    for _ in range(density):
        dx = rng.randint(-width // 2, width // 2)
        h = rng.randint(4, 9)
        lean = rng.randint(-2, 2)
        pygame.draw.line(cell, mid, (cx + dx, cy), (cx + dx + lean, cy - h), 1)
        pygame.draw.line(cell, top, (cx + dx, cy), (cx + dx + lean, cy - h + 2), 1)


def draw_flower_bed(cell, cx, cy, width=50, n=14, seed=0):
    rng = random.Random(seed)
    cols = [(255, 230, 100), (250, 250, 240), (255, 180, 200), (200, 120, 230), (255, 140, 80)]
    for _ in range(n):
        dx = rng.randint(-width // 2, width // 2)
        dy = rng.randint(-5, 2)
        col = rng.choice(cols)
        pygame.draw.circle(cell, col, (cx + dx, cy + dy), rng.choice([1, 2]))


def draw_ground_ferns(cell, cx, cy, width=50, n=5, palette=None, seed=0):
    rng = random.Random(seed)
    for i in range(n):
        dx = rng.randint(-width // 2, width // 2)
        draw_fern_cluster(cell, cx + dx, cy, n=rng.randint(4, 7), palette=palette, seed=seed + i)


def decorate(cell, cx, palette, name, idx):
    peak_x, peak_y = cx + 4, BOT_TOP
    if "Lung-ta" in name:
        # dense pine crown with companions
        draw_pine_trio(cell, peak_x, peak_y, palette, seed=idx)
        draw_wuling_pine(cell, peak_x - 30, peak_y + 54, 36, palette, lean=-4, layers=4)
        draw_wuling_pine(cell, peak_x + 26, peak_y + 72, 30, palette, lean=4, layers=3)
        # heavy moss cascade across the whole underside of top pillar
        for off in range(-36, 38, 4):
            draw_moss_strand(cell, cx + off, TOP_H - 12, 14 + abs(off) % 10, palette, jitter_seed=idx + off)
        draw_moss_patch(cell, cx + 22, TOP_H - 40, 30, 12, palette, seed=idx)
        # side shrubs on multiple ledges
        for sy, sc in [(70, 1.0), (120, 0.9), (180, 1.0), (220, 0.8)]:
            side = 1 if sy % 2 == 0 else -1
            draw_side_shrub(cell, cx + side * (PILLAR_W // 2 - 14), BOT_TOP + sy, palette, scale=sc)
        # climbing vine + ground bed
        draw_climbing_vine(cell, cx - PILLAR_W // 2 + 10, BOT_TOP + 40, GROUND_Y - 20, palette, seed=idx)
        draw_grass_bed(cell, cx, GROUND_Y - 2, width=80, density=18, palette=palette, seed=idx)
        draw_flower_bed(cell, cx, GROUND_Y - 3, width=70, n=18, seed=idx)
        draw_ground_ferns(cell, cx - 40, GROUND_Y - 4, width=20, n=3, palette=palette, seed=idx)
        # DOUBLED ornaments: 4 flag strings, 2 cairns, 2 incense bowls, extra bells
        draw_prayer_flags(cell, cx - 40, TOP_H - 60, peak_x + 22, peak_y - 64, n=9)
        draw_prayer_flags(cell, cx + 40, TOP_H - 46, peak_x - 6, peak_y - 42, n=7)
        draw_prayer_flags(cell, cx - 30, TOP_H - 80, cx + 32, TOP_H - 88, n=6)
        draw_prayer_flags(cell, cx - 44, TOP_H - 24, cx + 44, TOP_H - 20, n=5)
        draw_cairn(cell, peak_x - 26, peak_y + 4, n=4, pennant=False)
        draw_cairn(cell, cx + PILLAR_W // 2 + 4, GROUND_Y - 4, n=3, pennant=True)
        for bx in (cx - 18, cx + 14):
            pygame.draw.ellipse(cell, (80, 60, 45), (bx - 6, GROUND_Y - 10, 12, 6))
            draw_incense_smoke(cell, bx, GROUND_Y - 14, length=36)
        return
    if "Shimenawa" in name:
        # dense pine cluster
        draw_pine_trio(cell, peak_x, peak_y, palette, seed=idx + 1)
        # 6 moss strands + moss patches
        for off in (-28, -16, -4, 8, 20, 32):
            draw_moss_strand(cell, cx + off, TOP_H - 14, 16 + abs(off) % 8, palette, jitter_seed=idx + off)
        draw_moss_patch(cell, cx - 16, BOT_TOP + 60, 28, 14, palette, seed=idx)
        draw_moss_patch(cell, cx + 20, BOT_TOP + 140, 22, 12, palette, seed=idx + 2)
        # 2 shimenawa ropes + 1 extra on top pillar
        draw_shimenawa(cell, cx, TOP_H - 30, width=60)
        draw_shimenawa(cell, cx, BOT_TOP + 30, width=70)
        draw_shimenawa(cell, cx, BOT_TOP + 170, width=56)
        # 2 torii + a hanging ema plaque (paper charm)
        draw_torii(cell, cx - 22, GROUND_Y - 2)
        draw_torii(cell, cx + 22, GROUND_Y - 2)
        # paper shide charms hanging from top pillar extras
        for dx in (-20, 0, 20):
            pygame.draw.line(cell, (70, 50, 30), (cx + dx, TOP_H - 8), (cx + dx, TOP_H + 6), 1)
            pygame.draw.line(cell, (250, 250, 250), (cx + dx - 2, TOP_H + 6), (cx + dx + 2, TOP_H + 10), 2)
        # dense vegetation: 4 side shrubs + climbing vine + fern beds + grass + flowers
        for sy, sc in [(60, 1.0), (110, 0.9), (160, 1.0), (200, 0.8)]:
            side = -1 if sy % 2 == 0 else 1
            draw_side_shrub(cell, cx + side * (PILLAR_W // 2 - 14), BOT_TOP + sy, palette, scale=sc)
        draw_climbing_vine(cell, cx + PILLAR_W // 2 - 8, BOT_TOP + 30, GROUND_Y - 10, palette, seed=idx + 3)
        draw_ground_ferns(cell, cx, GROUND_Y - 4, width=80, n=5, palette=palette, seed=idx)
        draw_grass_bed(cell, cx, GROUND_Y - 2, width=90, density=20, palette=palette, seed=idx)
        return
    if "Darchog" in name:
        # dense pine cluster + companions
        draw_pine_trio(cell, peak_x, peak_y, palette, seed=idx)
        draw_wuling_pine(cell, peak_x - 28, peak_y + 60, 38, palette, lean=-4, layers=4)
        # dense moss across the underside
        for off in range(-32, 34, 5):
            draw_moss_strand(cell, cx + off, TOP_H - 14, 14 + abs(off) % 8, palette, jitter_seed=idx + off)
        draw_moss_patch(cell, cx, TOP_H - 40, 40, 14, palette, seed=idx)
        # 2 darchog poles with different banner colors + 2 stupas
        draw_darchog_pole(cell, peak_x + 14, peak_y - 4, height=100, banner_color=(200, 90, 40))
        draw_darchog_pole(cell, peak_x - 20, peak_y + 10, height=80, banner_color=(180, 40, 60))
        draw_stupa(cell, cx - 22, GROUND_Y - 10)
        draw_stupa(cell, cx + 22, GROUND_Y - 10)
        # 2 butter-lamps with glow
        for bx in (cx - 4, cx + 40):
            pygame.draw.rect(cell, (200, 170, 120), (bx - 3, GROUND_Y - 6, 6, 4))
            g = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(g, (255, 220, 120, 180), (6, 6), 5)
            cell.blit(g, (bx - 6, GROUND_Y - 14))
        # dense side vegetation: 5 shrubs + climbing vine + grass + flowers + ferns
        for sy, sc in [(50, 1.1), (100, 0.9), (150, 1.0), (200, 0.9), (240, 0.8)]:
            side = 1 if sy % 2 == 0 else -1
            draw_side_shrub(cell, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc)
        draw_climbing_vine(cell, cx - PILLAR_W // 2 + 10, BOT_TOP + 40, GROUND_Y - 20, palette, seed=idx + 1)
        draw_grass_bed(cell, cx, GROUND_Y - 2, width=80, density=18, palette=palette, seed=idx)
        draw_flower_bed(cell, cx, GROUND_Y - 3, width=70, n=16, seed=idx)
        for bx, by in [(cx - 100, 50), (cx + 90, 80), (cx - 80, 110), (cx + 110, 130)]:
            draw_bird_sil(cell, bx, by, size=5)
        return
    if "Babylon" in name:
        # small pine + 2 companion shrubs on peak
        draw_wuling_pine(cell, peak_x, peak_y + 2, 54, palette, lean=4, layers=4)
        draw_wuling_pine(cell, peak_x - 16, peak_y + 22, 40, palette, lean=-4, layers=4)
        # 4 terrace walls at natural shelf heights
        for ty in (BOT_TOP + 70, BOT_TOP + 140, BOT_TOP + 200, BOT_TOP + 240):
            draw_terrace_wall(cell, cx, ty, width=70)
        # MANY cascading vines + flowers spilling over each terrace
        for base_y in (BOT_TOP + 76, BOT_TOP + 146, BOT_TOP + 206):
            for vx, vl in [(-30, 44), (-18, 52), (-6, 58), (6, 50), (18, 46), (30, 40)]:
                draw_cascading_vine(cell, cx + vx, base_y, length=vl, palette=palette)
        # dense fern banks on each terrace top
        for ty in (BOT_TOP + 66, BOT_TOP + 136, BOT_TOP + 196):
            draw_ground_ferns(cell, cx, ty, width=70, n=6, palette=palette, seed=idx + ty)
        # flower beds on each terrace
        for ty in (BOT_TOP + 68, BOT_TOP + 138, BOT_TOP + 198):
            draw_flower_bed(cell, cx, ty, width=60, n=12, seed=idx + ty)
        # 2 ladders at different levels + a clay pot + a broken column stub (extra ornaments)
        draw_ladder(cell, cx + 18, BOT_TOP + 82, BOT_TOP + 138)
        draw_ladder(cell, cx - 28, BOT_TOP + 152, BOT_TOP + 200)
        pygame.draw.ellipse(cell, (110, 80, 55), (cx + 22, GROUND_Y - 14, 14, 12))
        pygame.draw.ellipse(cell, (150, 115, 80), (cx + 23, GROUND_Y - 13, 12, 9))
        pygame.draw.rect(cell, (130, 110, 85), (cx - 34, GROUND_Y - 22, 10, 22))
        pygame.draw.rect(cell, (160, 140, 110), (cx - 33, GROUND_Y - 21, 8, 20))
        draw_grass_bed(cell, cx, GROUND_Y - 2, width=90, density=22, palette=palette, seed=idx)
        return
    if "Monastery" in name:
        # 5+ alpine pines staggered for a dense mountain-top forest
        draw_pine_trio(cell, peak_x, peak_y, palette, seed=idx)
        draw_wuling_pine(cell, peak_x - 32, peak_y + 60, 38, palette, lean=-4, layers=4)
        draw_wuling_pine(cell, peak_x + 28, peak_y + 72, 34, palette, lean=4, layers=4)
        # 2 monastery buildings (main + annex) on different ledges
        draw_monastery(cell, cx - 24, BOT_TOP + 150)
        draw_monastery(cell, cx + 22, BOT_TOP + 220)
        # prayer-flag lines from both buildings to pine
        draw_prayer_flags(cell, cx - 24, BOT_TOP + 150, peak_x + 4, peak_y - 20, n=7)
        draw_prayer_flags(cell, cx + 22, BOT_TOP + 220, cx - 24, BOT_TOP + 200, n=6)
        draw_prayer_flags(cell, cx - 24, BOT_TOP + 190, cx + 22, BOT_TOP + 180, n=5)
        # heavy moss cascade
        for off in range(-28, 30, 4):
            draw_moss_strand(cell, cx + off, TOP_H - 14, 12 + abs(off) % 8, palette, jitter_seed=idx + off)
        draw_moss_patch(cell, cx, TOP_H - 42, 36, 14, palette, seed=idx)
        # dense shrubs + climbing vine + ground cover
        for sy, sc in [(50, 1.1), (100, 1.0), (170, 0.9), (240, 0.8)]:
            side = 1 if sy % 2 == 0 else -1
            draw_side_shrub(cell, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc)
        draw_climbing_vine(cell, cx + PILLAR_W // 2 - 8, BOT_TOP + 30, GROUND_Y - 30, palette, seed=idx)
        draw_flower_bed(cell, cx, GROUND_Y - 4, width=70, n=14, seed=idx)
        draw_grass_bed(cell, cx, GROUND_Y - 2, width=90, density=18, palette=palette, seed=idx)
        return
    if "Lantern" in name:
        # denser pine cluster
        draw_pine_trio(cell, peak_x, peak_y, palette, seed=idx)
        draw_wuling_pine(cell, peak_x - 30, peak_y + 54, 36, palette, lean=-4, layers=4)
        draw_wuling_pine(cell, peak_x + 26, peak_y + 70, 32, palette, lean=4, layers=3)
        # hero + many lanterns (DOUBLED): 2 hero, 8 small
        draw_paper_lantern(cell, cx - 14, TOP_H - 4, strand=26, scale=1.4, color='red')
        draw_paper_lantern(cell, cx + 18, TOP_H - 6, strand=34, scale=0.9, color='gold')
        for i, (dx, dy, clr) in enumerate([(-40, 36, 'red'), (-18, 48, 'gold'), (8, 36, 'red'), (32, 48, 'gold'),
                                             (-36, 78, 'gold'), (-8, 82, 'red'), (22, 78, 'red'), (40, 90, 'gold')]):
            draw_paper_lantern(cell, cx + dx, TOP_H + dy, strand=6, scale=0.55, color=clr)
        # 2 plaques + garland + incense
        for pl_y in (GROUND_Y - 22, BOT_TOP + 100):
            pygame.draw.rect(cell, (160, 125, 55), (cx - 10, pl_y, 20, 18))
            pygame.draw.rect(cell, (220, 180, 80), (cx - 9, pl_y + 1, 18, 16))
            for i in range(3):
                pygame.draw.line(cell, (120, 85, 25), (cx - 6, pl_y + 4 + i * 4), (cx + 6, pl_y + 4 + i * 4), 1)
        # dense bougainvillea wall along the pillar face
        for i in range(22):
            dy = BOT_TOP + 30 + i * 10
            for dx in (-PILLAR_W // 2 + 8, -PILLAR_W // 2 + 14, PILLAR_W // 2 - 10, PILLAR_W // 2 - 18):
                pygame.draw.circle(cell, (220, 60, 140), (cx + dx, dy), 2)
                pygame.draw.circle(cell, (245, 130, 180), (cx + dx + 1, dy - 1), 1)
        # bamboo cluster + ferns + grass
        for k in range(7):
            pygame.draw.line(cell, (90, 140, 70), (cx - 36 + k * 3, GROUND_Y - 4), (cx - 36 + k * 3, GROUND_Y - 24), 2)
            pygame.draw.ellipse(cell, (120, 180, 90), (cx - 38 + k * 3, GROUND_Y - 26, 6, 4))
        draw_ground_ferns(cell, cx + 28, GROUND_Y - 4, width=26, n=4, palette=palette, seed=idx)
        draw_grass_bed(cell, cx, GROUND_Y - 2, width=90, density=16, palette=palette, seed=idx)
        for smoke_x in (cx - 22, cx + 22, cx - 4):
            draw_incense_smoke(cell, smoke_x, GROUND_Y - 24, length=22)
        return
    if "Basalt" in name:
        # 3 stunted alpine pines clinging to the cap
        draw_wuling_pine(cell, peak_x, peak_y + 2, 62, palette, lean=14, layers=5)
        draw_wuling_pine(cell, peak_x - 22, peak_y + 24, 44, palette, lean=-8, layers=4)
        draw_wuling_pine(cell, peak_x + 18, peak_y + 46, 32, palette, lean=6, layers=3)
        # 2 marker poles with colored cloths
        pygame.draw.line(cell, (80, 60, 40), (peak_x - 16, peak_y + 6), (peak_x - 16, peak_y - 32), 2)
        pygame.draw.polygon(cell, (210, 130, 60), [(peak_x - 16, peak_y - 32), (peak_x + 0, peak_y - 28), (peak_x - 16, peak_y - 24)])
        pygame.draw.line(cell, (80, 60, 40), (peak_x + 20, peak_y + 8), (peak_x + 20, peak_y - 20), 2)
        pygame.draw.polygon(cell, (170, 50, 60), [(peak_x + 20, peak_y - 20), (peak_x + 32, peak_y - 16), (peak_x + 20, peak_y - 14)])
        # 2 cairns (peak + base) + raven + carved rune
        draw_cairn(cell, peak_x + 6, peak_y + 6, n=4, pennant=False)
        draw_cairn(cell, cx - 22, GROUND_Y - 4, n=3, pennant=True)
        draw_raven(cell, cx + 2, 22)
        draw_raven(cell, peak_x + 6, peak_y - 24)
        # heavy lichen MATS (not dots) in alpine greens + yellows
        rng = random.Random(idx)
        for _ in range(22):
            dx = rng.randint(-PILLAR_W // 2 + 8, PILLAR_W // 2 - 8)
            dy = rng.randint(60, BOT_TOP + 240)
            col = rng.choice([(170, 180, 90), (180, 200, 110), (220, 200, 80)])
            r = rng.randint(2, 4)
            pygame.draw.circle(cell, col, (cx + dx, dy), r)
        # carved runes in 3 spots
        for ny in (BOT_TOP + 80, BOT_TOP + 160, BOT_TOP + 220):
            pygame.draw.line(cell, (60, 48, 40), (cx - 18, ny), (cx - 10, ny - 5), 2)
            pygame.draw.line(cell, (60, 48, 40), (cx - 10, ny - 5), (cx - 2, ny), 2)
            pygame.draw.circle(cell, (60, 48, 40), (cx + 10, ny - 3), 2)
        # moss strands on the underside + sparse side shrubs + alpine grass+flowers at base
        for off in (-20, -8, 4, 16):
            draw_moss_strand(cell, cx + off, TOP_H - 12, 14, palette, jitter_seed=idx + off)
        for sy, sc in [(80, 0.8), (180, 0.9), (240, 0.7)]:
            side = 1 if sy % 2 == 0 else -1
            draw_side_shrub(cell, cx + side * (PILLAR_W // 2 - 12), BOT_TOP + sy, palette, scale=sc)
        draw_grass_bed(cell, cx, GROUND_Y - 2, width=80, density=14, palette=palette, seed=idx)
        draw_flower_bed(cell, cx, GROUND_Y - 3, width=60, n=10, seed=idx)
        return
    if "Hermit" in name:
        # dense grove of 6 painterly pines at varied angles
        draw_wuling_pine(cell, peak_x, peak_y + 2, 80, palette, lean=18, layers=6)
        draw_wuling_pine(cell, peak_x - 22, peak_y + 36, 54, palette, lean=-14, layers=5)
        draw_wuling_pine(cell, peak_x + 18, peak_y + 70, 40, palette, lean=8, layers=4)
        draw_wuling_pine(cell, peak_x - 32, peak_y + 92, 32, palette, lean=-6, layers=3)
        draw_wuling_pine(cell, peak_x + 26, peak_y + 110, 28, palette, lean=6, layers=3)
        draw_wuling_pine(cell, peak_x - 8, peak_y + 130, 24, palette, lean=-2, layers=3)
        # hermit hut + 2nd tiny storage shed
        draw_hermit_hut(cell, cx - 18, BOT_TOP + 170)
        pygame.draw.rect(cell, (130, 95, 60), (cx + 20, BOT_TOP + 218, 14, 14))
        pygame.draw.polygon(cell, (160, 120, 75), [(cx + 18, BOT_TOP + 218), (cx + 36, BOT_TOP + 218), (cx + 32, BOT_TOP + 212), (cx + 22, BOT_TOP + 212)])
        # rope bridge stub + hanging scroll + walking stick
        draw_rope_bridge_stub(cell, cx + PILLAR_W // 2 - 4, BOT_TOP + 120, dir=1)
        pygame.draw.rect(cell, (240, 230, 200), (cx - 34, BOT_TOP + 80, 8, 30))
        pygame.draw.rect(cell, (100, 75, 50), (cx - 35, BOT_TOP + 78, 10, 2))
        pygame.draw.line(cell, (100, 70, 40), (cx - 22, BOT_TOP + 170), (cx - 28, BOT_TOP + 200), 2)
        # mist wrap bands
        for y in (BOT_TOP + 40, BOT_TOP + 110, BOT_TOP + 190, BOT_TOP + 240):
            m = pygame.Surface((PILLAR_W + 60, 10), pygame.SRCALPHA)
            m.fill((255, 255, 255, 70))
            cell.blit(m, (cx - (PILLAR_W + 60) // 2, y))
        # 2 bamboo groves + ferns + moss patches + flower bed
        for gx in (18, -42):
            for k in range(6):
                pygame.draw.line(cell, (90, 140, 70), (cx + gx + k * 3, GROUND_Y - 2), (cx + gx + k * 3, GROUND_Y - 26), 2)
                pygame.draw.ellipse(cell, (120, 180, 90), (cx + gx - 2 + k * 3, GROUND_Y - 30, 7, 5))
        draw_moss_patch(cell, cx, TOP_H - 30, 40, 16, palette, seed=idx)
        draw_moss_patch(cell, cx - 14, BOT_TOP + 60, 24, 12, palette, seed=idx + 4)
        draw_ground_ferns(cell, cx, GROUND_Y - 4, width=60, n=4, palette=palette, seed=idx)
        return
    if "Overgrown" in name:
        # 2 broadleaf trees replacing pines — canopies overlapping
        for tx, ty in [(peak_x, peak_y), (peak_x - 22, peak_y + 22)]:
            pygame.draw.line(cell, (90, 60, 35), (tx, ty + 2), (tx, ty - 30), 3)
            for (dx, dy, sz) in [(0, 0, 40), (-12, 6, 28), (14, 8, 30), (-4, -10, 24)]:
                pygame.draw.circle(cell, (30, 90, 45), (tx + dx, ty - 34 + dy), sz // 2 + 2)
                pygame.draw.circle(cell, (60, 150, 70), (tx + dx, ty - 34 + dy), sz // 2)
                pygame.draw.circle(cell, (130, 210, 100), (tx + dx - 2, ty - 36 + dy), max(4, sz // 2 - 6))
        # 2 strangler fig root systems + more masonry + 2 stone faces + broken column
        draw_strangler_fig(cell, cx - PILLAR_W // 2 + 8, BOT_TOP + 30, GROUND_Y - 10)
        draw_strangler_fig(cell, cx + PILLAR_W // 2 - 20, BOT_TOP + 60, GROUND_Y - 12)
        draw_masonry_blocks(cell, cx, BOT_TOP + 40, GROUND_Y - 10, PILLAR_W)
        draw_stone_face(cell, cx + 16, BOT_TOP + 170)
        draw_stone_face(cell, cx - 18, BOT_TOP + 90)
        # broken column stub at base
        pygame.draw.rect(cell, (130, 110, 85), (cx - 36, GROUND_Y - 24, 10, 24))
        pygame.draw.ellipse(cell, (150, 125, 95), (cx - 38, GROUND_Y - 26, 14, 4))
        pygame.draw.rect(cell, (160, 140, 110), (cx - 35, GROUND_Y - 23, 8, 22))
        # dense fern banks on every ledge + orchid clusters + moss patches
        for fy in (BOT_TOP + 50, BOT_TOP + 110, BOT_TOP + 170, BOT_TOP + 230):
            draw_fern_cluster(cell, cx - 16, fy, n=8, palette=palette, seed=idx + fy)
            draw_fern_cluster(cell, cx + 20, fy - 4, n=7, palette=palette, seed=idx + fy + 1)
        draw_moss_patch(cell, cx, TOP_H - 30, 50, 20, palette, seed=idx)
        draw_moss_patch(cell, cx - 18, BOT_TOP + 140, 24, 12, palette, seed=idx + 2)
        for ox, oy in [(cx - 28, BOT_TOP + 90), (cx + 26, BOT_TOP + 140), (cx - 20, BOT_TOP + 180),
                        (cx + 18, BOT_TOP + 220), (cx - 34, BOT_TOP + 60), (cx + 30, BOT_TOP + 210)]:
            pygame.draw.circle(cell, (220, 150, 200), (ox, oy), 2)
            pygame.draw.circle(cell, (250, 200, 230), (ox + 1, oy - 1), 1)
        # 2 urns + butterfly
        for ux in (-26, 26):
            pygame.draw.ellipse(cell, (110, 80, 55), (cx + ux - 6, GROUND_Y - 12, 12, 10))
            pygame.draw.ellipse(cell, (150, 115, 80), (cx + ux - 5, GROUND_Y - 11, 10, 7))
        draw_bird_sil(cell, cx + 40, TOP_H + 50, size=4)
        draw_ground_ferns(cell, cx, GROUND_Y - 4, width=80, n=6, palette=palette, seed=idx)
        draw_flower_bed(cell, cx, GROUND_Y - 3, width=80, n=16, seed=idx)
        return
    if "Menhir" in name:
        # 3 rowan trees with red berries
        for tx, ty in [(peak_x, peak_y), (peak_x - 20, peak_y + 20), (peak_x + 18, peak_y + 34)]:
            pygame.draw.line(cell, (90, 60, 40), (tx, ty + 2), (tx + 2, ty - 26), 2)
            for rx, ry in [(-6, -12), (8, -16), (-2, -24), (12, -10), (-10, -20), (4, -8)]:
                pygame.draw.circle(cell, (40, 120, 55), (tx + rx, ty + ry), 6)
                pygame.draw.circle(cell, (80, 170, 80), (tx + rx - 1, ty + ry - 1), 4)
                pygame.draw.circle(cell, (200, 40, 40), (tx + rx + 2, ty + ry + 1), 1)
        # 5 spiral glow carvings
        for (sx, sy, r) in [(0, 130, 14), (-24, 80, 8), (20, 210, 10), (-14, 180, 9), (24, 140, 8)]:
            draw_spiral_glow(cell, cx + sx, BOT_TOP + sy, radius=r)
        # 2 ribbon knots + carved rune pairs
        draw_ribbons_tied(cell, cx - 10, BOT_TOP + 14, n=5, width=26, seed=idx)
        draw_ribbons_tied(cell, cx + 12, BOT_TOP + 110, n=5, width=24, seed=idx + 1)
        # 2 cairns + 2 candles
        draw_cairn(cell, cx - 24, GROUND_Y - 4, n=4, pennant=False)
        draw_cairn(cell, cx + 26, GROUND_Y - 4, n=3, pennant=True)
        for (candle_x, candle_y) in [(cx - 4, GROUND_Y - 10), (cx + 8, GROUND_Y - 10)]:
            pygame.draw.rect(cell, (240, 230, 210), (candle_x - 2, candle_y, 4, 8))
            g = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(g, (255, 220, 120, 190), (6, 6), 5)
            cell.blit(g, (candle_x - 6, candle_y - 6))
        # dense heather field + moss + ferns + grass at base
        for hx_base in range(-42, 46, 7):
            for k in range(3):
                pygame.draw.line(cell, (150, 90, 140), (cx + hx_base + k, GROUND_Y - 2),
                                  (cx + hx_base + k - 1, GROUND_Y - 8 - (k % 3)), 1)
                pygame.draw.circle(cell, (200, 140, 190), (cx + hx_base + k, GROUND_Y - 10), 1)
        draw_moss_patch(cell, cx, TOP_H - 28, 40, 14, palette, seed=idx)
        draw_ground_ferns(cell, cx, GROUND_Y - 4, width=80, n=4, palette=palette, seed=idx)
        draw_grass_bed(cell, cx, GROUND_Y - 2, width=100, density=18, palette=palette, seed=idx)
        draw_raven(cell, cx - 10, 28)
        draw_raven(cell, cx + 20, 42)
        return
    return


def label(surf, col, row, title, font):
    cx = col * W_CELL + W_CELL // 2
    y = row * H_CELL + 6
    t = font.render(title, True, (18, 18, 26))
    pad = 6
    w = t.get_width() + pad * 2
    h = t.get_height() + pad
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill((255, 255, 255, 225))
    surf.blit(bg, (cx - w // 2, y))
    surf.blit(t, (cx - t.get_width() // 2, y + pad // 2))


def main():
    pygame.init()
    surf = pygame.Surface((W, H))
    paint_bg(surf)
    for idx, opt in enumerate(OPTIONS):
        col, row = idx % COLS, idx // COLS
        cell = pygame.Surface((W_CELL, H_CELL), pygame.SRCALPHA)
        draw_pair(cell, idx, opt)
        surf.blit(cell, (col * W_CELL, row * H_CELL))
    font = pygame.font.SysFont("arial", 14, bold=True)
    for idx, opt in enumerate(OPTIONS):
        label(surf, idx % COLS, idx // COLS, opt['name'], font)
    out = "/home/user/Claude_test/docs/pillar_redesign_options.png"
    pygame.image.save(surf, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
