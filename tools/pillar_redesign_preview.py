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

def sil_stout_neck(w, h):
    # fat body with a clear narrow "neck" (shimenawa would wrap around it)
    return [(0, 0), (w, 0), (w, int(h * 0.28)), (int(w * 0.74), int(h * 0.44)),
            (int(w * 0.74), int(h * 0.58)), (w, int(h * 0.72)),
            (int(w * 0.80), h), (int(w * 0.20), h),
            (0, int(h * 0.72)), (int(w * 0.26), int(h * 0.58)),
            (int(w * 0.26), int(h * 0.44)), (0, int(h * 0.28))]


def sil_stepped(w, h):
    # 3 stepped terraces (bottom pillar form — wider steps cascading up)
    return [(0, 0), (w, 0), (w, int(h * 0.28)),
            (int(w * 0.84), int(h * 0.30)), (int(w * 0.84), int(h * 0.52)),
            (int(w * 0.70), int(h * 0.54)), (int(w * 0.70), int(h * 0.78)),
            (int(w * 0.56), int(h * 0.80)), (int(w * 0.52), h),
            (int(w * 0.48), int(h * 0.80)), (int(w * 0.30), int(h * 0.78)),
            (int(w * 0.30), int(h * 0.54)), (int(w * 0.16), int(h * 0.52)),
            (int(w * 0.16), int(h * 0.30)), (0, int(h * 0.28))]


def sil_leaning(w, h):
    # slender spire with slight rightward tilt
    return [(0, 0), (w, 0), (int(w * 0.72), int(h * 0.50)),
            (int(w * 0.68), int(h * 0.78)), (int(w * 0.60), h),
            (int(w * 0.48), int(h * 0.78)), (int(w * 0.36), int(h * 0.50))]


def sil_waisted(w, h):
    # stout column with a subtle waist bulge below a narrower mid
    return [(0, 0), (w, 0), (int(w * 0.92), int(h * 0.24)),
            (int(w * 0.78), int(h * 0.50)), (int(w * 0.88), int(h * 0.74)),
            (int(w * 0.80), h), (int(w * 0.20), h),
            (int(w * 0.12), int(h * 0.74)), (int(w * 0.22), int(h * 0.50)),
            (int(w * 0.08), int(h * 0.24))]


def sil_eroded(w, h):
    # wider column with soft erosion bulges — temple-ruin shape
    return [(0, 0), (w, 0), (int(w * 0.98), int(h * 0.20)),
            (int(w * 0.84), int(h * 0.44)), (w, int(h * 0.64)),
            (int(w * 0.90), int(h * 0.84)), (int(w * 0.74), h),
            (int(w * 0.26), h), (int(w * 0.10), int(h * 0.84)),
            (0, int(h * 0.64)), (int(w * 0.16), int(h * 0.44)),
            (int(w * 0.02), int(h * 0.20))]


def sil_bulbous(w, h):
    # fat bulbous standing-stone / menhir shape, slight tilt
    return [(0, 0), (w, 0), (w, int(h * 0.46)),
            (int(w * 0.94), int(h * 0.70)), (int(w * 0.82), int(h * 0.88)),
            (int(w * 0.60), h), (int(w * 0.34), h),
            (int(w * 0.14), int(h * 0.88)), (int(w * 0.04), int(h * 0.70)),
            (0, int(h * 0.46))]


def overlay_flutes(surf, cx, pw):
    # faint vertical fluting dark stripes on both top and bottom pillar
    left = cx - pw // 2 + 6
    for i in range(5):
        x = left + i * ((pw - 12) // 4)
        pygame.draw.line(surf, (60, 48, 40), (x, 18), (x, TOP_H - 14), 1)
        pygame.draw.line(surf, (60, 48, 40), (x, BOT_TOP + 14), (x, GROUND_Y - 14), 1)


OPTIONS = [
    dict(name="01 Lung-ta Pass"),
    dict(name="02 Shimenawa Stone", bot_sil=sil_stout_neck),
    dict(name="03 Darchog Sentinel"),
    dict(name="04 Babylon Terrace",  bot_sil=sil_stepped),
    dict(name="05 Monastery Perch",  bot_sil=sil_leaning),
    dict(name="06 Lantern Festival", bot_sil=sil_waisted),
    dict(name="07 Basalt Organ",     overlay=overlay_flutes),
    dict(name="08 Hermit's Retreat", bot_sil=sil_leaning),
    dict(name="09 Overgrown Ruin",   bot_sil=sil_eroded),
    dict(name="10 Menhir Shrine",    bot_sil=sil_bulbous),
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


def decorate(cell, cx, palette, name, idx):
    peak_x, peak_y = cx + 4, BOT_TOP
    if "Lung-ta" in name:
        draw_wuling_pine(cell, peak_x, peak_y + 2, 82, palette, lean=12, layers=6)
        draw_wuling_pine(cell, peak_x - 18, peak_y + 22, 48, palette, lean=-6, layers=4)
        draw_moss_strand(cell, cx - 18, TOP_H - 14, 18, palette, jitter_seed=idx)
        draw_moss_strand(cell, cx + 14, TOP_H - 14, 14, palette, jitter_seed=idx + 1)
        draw_side_shrub(cell, cx + 34, BOT_TOP + 70, palette, scale=1.0)
        draw_prayer_flags(cell, cx - 38, TOP_H - 56, peak_x + 20, peak_y - 60, n=9)
        draw_prayer_flags(cell, cx + 38, TOP_H - 42, peak_x - 6, peak_y - 38, n=6)
        draw_cairn(cell, peak_x - 22, peak_y + 4, n=3, pennant=False)
        # smoke bowl at base
        pygame.draw.ellipse(cell, (80, 60, 45), (cx - 8, GROUND_Y - 10, 16, 6))
        draw_incense_smoke(cell, cx, GROUND_Y - 14, length=40)
        return
    if "Shimenawa" in name:
        draw_wuling_pine(cell, peak_x, peak_y + 2, 70, palette, lean=8, layers=5)
        # rope around top pillar's fang and around bottom pillar's neck
        draw_shimenawa(cell, cx, TOP_H - 24, width=58)
        draw_shimenawa(cell, cx, BOT_TOP + 115, width=46)  # at the neck of sil_stout_neck
        draw_torii(cell, cx, GROUND_Y - 2)
        draw_side_shrub(cell, cx + 32, BOT_TOP + 70, palette, scale=1.0)
        draw_moss_strand(cell, cx - 22, TOP_H - 14, 12, palette, jitter_seed=idx)
        # fern cluster
        for fx, fy in [(cx - 28, BOT_TOP + 200), (cx + 22, BOT_TOP + 210)]:
            for k in range(5):
                pygame.draw.line(cell, (50, 140, 60), (fx + k, fy), (fx + k - 2, fy - 6), 1)
        return
    if "Darchog" in name:
        draw_wuling_pine(cell, peak_x, peak_y + 2, 80, palette, lean=10, layers=6)
        draw_wuling_pine(cell, peak_x - 20, peak_y + 24, 48, palette, lean=-6, layers=5)
        draw_darchog_pole(cell, peak_x + 14, peak_y - 4, height=90, banner_color=(200, 90, 40))
        draw_stupa(cell, cx - 10, GROUND_Y - 10)
        for off in (-22, -8, 8, 20):
            draw_moss_strand(cell, cx + off, TOP_H - 14, 16, palette, jitter_seed=idx + off)
        draw_side_shrub(cell, cx - 34, BOT_TOP + 70, palette, scale=1.0)
        draw_side_shrub(cell, cx + 30, BOT_TOP + 150, palette, scale=0.9)
        # small butter-lamp on the base ledge
        pygame.draw.rect(cell, (200, 170, 120), (cx + 22, GROUND_Y - 6, 6, 4))
        g = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(g, (255, 220, 120, 180), (5, 5), 4)
        cell.blit(g, (cx + 20, GROUND_Y - 12))
        for bx, by in [(cx - 100, 60), (cx + 90, 90)]:
            draw_bird_sil(cell, bx, by, size=5)
        return
    if "Babylon" in name:
        draw_wuling_pine(cell, peak_x, peak_y + 2, 52, palette, lean=6, layers=4)
        # terrace walls at each step (matching sil_stepped breakpoints roughly)
        draw_terrace_wall(cell, cx, BOT_TOP + 80, width=60)
        draw_terrace_wall(cell, cx, BOT_TOP + 160, width=80)
        draw_terrace_wall(cell, cx, BOT_TOP + 230, width=100)
        # cascading vines + flowers dripping over terrace edges
        for vx, vl in [(-22, 50), (0, 46), (20, 54), (-34, 40), (30, 44)]:
            draw_cascading_vine(cell, cx + vx, BOT_TOP + 86, length=vl, palette=palette)
        draw_cascading_vine(cell, cx - 18, BOT_TOP + 166, length=60, palette=palette)
        draw_cascading_vine(cell, cx + 16, BOT_TOP + 166, length=50, palette=palette)
        # ferns on top ledge
        for fx in (-24, 0, 20):
            for k in range(4):
                pygame.draw.line(cell, (50, 140, 60), (cx + fx + k, BOT_TOP + 78), (cx + fx + k - 2, BOT_TOP + 72), 1)
        # wooden ladder between two terraces
        draw_ladder(cell, cx + 18, BOT_TOP + 82, BOT_TOP + 158)
        return
    if "Monastery" in name:
        # 3 alpine pines staggered on the peak
        draw_wuling_pine(cell, peak_x, peak_y + 2, 72, palette, lean=10, layers=5)
        draw_wuling_pine(cell, peak_x - 18, peak_y + 22, 50, palette, lean=-4, layers=4)
        draw_wuling_pine(cell, peak_x + 14, peak_y + 42, 36, palette, lean=4, layers=4)
        # monastery building perched on mid-face ledge (bottom pillar)
        draw_monastery(cell, cx - 22, BOT_TOP + 140)
        # short prayer-flag line from balcony to pine
        draw_prayer_flags(cell, cx - 22, BOT_TOP + 140, peak_x + 4, peak_y - 20, n=6)
        for off in (-24, -8, 6, 18):
            draw_moss_strand(cell, cx + off, TOP_H - 14, 14, palette, jitter_seed=idx + off)
        draw_side_shrub(cell, cx + 30, BOT_TOP + 60, palette, scale=1.0)
        draw_side_shrub(cell, cx + 28, BOT_TOP + 210, palette, scale=0.9)
        return
    if "Lantern" in name:
        draw_wuling_pine(cell, peak_x, peak_y + 2, 72, palette, lean=8, layers=5)
        draw_wuling_pine(cell, peak_x - 18, peak_y + 24, 46, palette, lean=-6, layers=4)
        # hero lantern + lantern string
        draw_paper_lantern(cell, cx - 14, TOP_H - 4, strand=26, scale=1.4, color='red')
        draw_paper_lantern(cell, cx + 18, TOP_H - 6, strand=34, scale=0.9, color='gold')
        for i, dx in enumerate((-36, -14, 10, 32)):
            draw_paper_lantern(cell, cx + dx, TOP_H + 36, strand=6, scale=0.55,
                               color=['red', 'gold', 'red', 'gold'][i])
        # gilded calligraphy plaque at base
        pygame.draw.rect(cell, (160, 125, 55), (cx - 10, GROUND_Y - 20, 20, 20))
        pygame.draw.rect(cell, (220, 180, 80), (cx - 9, GROUND_Y - 19, 18, 18))
        for i in range(3):
            pygame.draw.line(cell, (120, 85, 25), (cx - 6, GROUND_Y - 14 + i * 4), (cx + 6, GROUND_Y - 14 + i * 4), 1)
        # bamboo + bougainvillea (magenta dots climbing the face)
        for i in range(10):
            dy = BOT_TOP + 40 + i * 16
            dx = (-1) ** i * (PILLAR_W // 2 - 10)
            pygame.draw.circle(cell, (220, 60, 140), (cx + dx, dy), 2)
            pygame.draw.circle(cell, (245, 130, 180), (cx + dx + 1, dy - 1), 1)
        draw_incense_smoke(cell, cx - 20, GROUND_Y - 22, length=22)
        draw_incense_smoke(cell, cx + 20, GROUND_Y - 22, length=22)
        return
    if "Basalt" in name:
        # single stunted leaning pine on the cap
        draw_wuling_pine(cell, peak_x, peak_y + 2, 58, palette, lean=14, layers=4)
        # marker pole with faded orange cloth flag on peak
        pygame.draw.line(cell, (80, 60, 40), (peak_x - 14, peak_y + 4), (peak_x - 14, peak_y - 28), 2)
        pygame.draw.polygon(cell, (210, 130, 60), [(peak_x - 14, peak_y - 28), (peak_x + 2, peak_y - 24), (peak_x - 14, peak_y - 20)])
        draw_cairn(cell, peak_x + 14, peak_y + 6, n=3, pennant=False)
        draw_raven(cell, cx + 2, 22)
        # lichen patches (greenish-yellow) + tiny cushion flowers
        rng = random.Random(idx)
        for _ in range(12):
            dx = rng.randint(-PILLAR_W // 2 + 8, PILLAR_W // 2 - 8)
            dy = rng.randint(60, BOT_TOP + 220)
            col = rng.choice([(170, 180, 90), (180, 200, 110), (255, 220, 100)])
            pygame.draw.circle(cell, col, (cx + dx, dy), 2)
        # two carved rune notches in the stone
        for ny in (BOT_TOP + 80, BOT_TOP + 160):
            pygame.draw.line(cell, (60, 48, 40), (cx - 16, ny), (cx - 10, ny - 4), 2)
            pygame.draw.line(cell, (60, 48, 40), (cx - 10, ny - 4), (cx - 4, ny), 2)
        return
    if "Hermit" in name:
        # painterly twisted pines at different angles
        draw_wuling_pine(cell, peak_x, peak_y + 2, 74, palette, lean=18, layers=5)
        draw_wuling_pine(cell, peak_x - 22, peak_y + 36, 48, palette, lean=-12, layers=4)
        draw_wuling_pine(cell, peak_x + 18, peak_y + 80, 34, palette, lean=8, layers=4)
        # hermit hut on mid-face ledge
        draw_hermit_hut(cell, cx - 18, BOT_TOP + 170)
        # rope bridge stub dangling off the right side of bottom pillar
        draw_rope_bridge_stub(cell, cx + PILLAR_W // 2 - 4, BOT_TOP + 120, dir=1)
        # bamboo cluster at base
        for k in range(5):
            pygame.draw.line(cell, (90, 140, 70), (cx + 18 + k * 3, GROUND_Y), (cx + 18 + k * 3, GROUND_Y - 20), 2)
            pygame.draw.ellipse(cell, (120, 180, 90), (cx + 16 + k * 3, GROUND_Y - 22, 6, 4))
        # mist wrap around the column — soft alpha bands
        for y in (BOT_TOP + 50, BOT_TOP + 130, BOT_TOP + 210):
            m = pygame.Surface((PILLAR_W + 40, 8), pygame.SRCALPHA)
            m.fill((255, 255, 255, 60))
            cell.blit(m, (cx - (PILLAR_W + 40) // 2, y))
        # walking stick leaning against hut
        pygame.draw.line(cell, (100, 70, 40), (cx - 22, BOT_TOP + 170), (cx - 28, BOT_TOP + 200), 2)
        return
    if "Overgrown" in name:
        # broadleaf tree instead of pine on peak — wider ellipses for canopy
        for i, (dx, dy, sz) in enumerate([(0, 0, 40), (-12, 6, 28), (14, 8, 30), (-4, -10, 24)]):
            pygame.draw.circle(cell, (30, 90, 45), (peak_x + dx, peak_y - 30 + dy), sz // 2 + 2)
            pygame.draw.circle(cell, (60, 150, 70), (peak_x + dx, peak_y - 30 + dy), sz // 2)
            pygame.draw.circle(cell, (130, 210, 100), (peak_x + dx - 2, peak_y - 32 + dy), max(4, sz // 2 - 6))
        pygame.draw.line(cell, (90, 60, 35), (peak_x, peak_y + 2), (peak_x, peak_y - 24), 3)
        # masonry + stone face + strangler fig
        draw_masonry_blocks(cell, cx, BOT_TOP + 40, GROUND_Y - 10, PILLAR_W)
        draw_stone_face(cell, cx + 16, BOT_TOP + 170)
        draw_strangler_fig(cell, cx - PILLAR_W // 2 + 8, BOT_TOP + 30, GROUND_Y - 10)
        # ferns on 3 ledges
        for fy in (BOT_TOP + 60, BOT_TOP + 130, BOT_TOP + 200):
            for k in range(6):
                fx = cx - 18 + k * 6
                pygame.draw.line(cell, (40, 130, 55), (fx, fy), (fx - 3, fy - 8), 1)
                pygame.draw.line(cell, (60, 160, 70), (fx + 1, fy), (fx + 3, fy - 7), 1)
        # orchid spots
        for ox, oy in [(cx - 28, BOT_TOP + 90), (cx + 26, BOT_TOP + 140), (cx - 20, BOT_TOP + 180)]:
            pygame.draw.circle(cell, (220, 150, 200), (ox, oy), 2)
            pygame.draw.circle(cell, (250, 200, 230), (ox + 1, oy - 1), 1)
        # weathered urn at base
        pygame.draw.ellipse(cell, (110, 80, 55), (cx - 26, GROUND_Y - 12, 12, 10))
        pygame.draw.ellipse(cell, (150, 115, 80), (cx - 25, GROUND_Y - 11, 10, 7))
        # butterfly drifting
        draw_bird_sil(cell, cx + 40, TOP_H + 50, size=4)
        return
    if "Menhir" in name:
        # rowan tree on cap (darker red berries instead of pine)
        pygame.draw.line(cell, (90, 60, 40), (peak_x, peak_y + 2), (peak_x + 2, peak_y - 24), 2)
        for rx, ry in [(-6, -10), (8, -14), (-2, -22), (12, -8), (-10, -18)]:
            pygame.draw.circle(cell, (40, 120, 55), (peak_x + rx, peak_y + ry), 6)
            pygame.draw.circle(cell, (80, 170, 80), (peak_x + rx - 1, peak_y + ry - 1), 4)
            pygame.draw.circle(cell, (200, 40, 40), (peak_x + rx + 2, peak_y + ry + 1), 1)
        # spiral glow carvings on bulbous bottom pillar
        draw_spiral_glow(cell, cx, BOT_TOP + 130, radius=14)
        draw_spiral_glow(cell, cx - 24, BOT_TOP + 80, radius=8)
        draw_spiral_glow(cell, cx + 20, BOT_TOP + 210, radius=9)
        # tied ribbons around the narrowest neck (top of bulb)
        draw_ribbons_tied(cell, cx, BOT_TOP + 8, n=5, width=30, seed=idx)
        # offering cairn at base + candle + heather tufts
        draw_cairn(cell, cx - 22, GROUND_Y - 4, n=3, pennant=False)
        pygame.draw.rect(cell, (240, 230, 210), (cx + 22, GROUND_Y - 10, 4, 8))
        g = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(g, (255, 220, 120, 180), (5, 5), 4)
        cell.blit(g, (cx + 19, GROUND_Y - 16))
        for hx in (cx - 36, cx + 38, cx + 10, cx - 12):
            for k in range(3):
                pygame.draw.line(cell, (150, 90, 140), (hx + k, GROUND_Y - 2), (hx + k - 1, GROUND_Y - 8), 1)
        draw_raven(cell, cx - 10, 28)
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
