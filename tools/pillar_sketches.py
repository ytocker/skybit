"""
Generate 20 pillar-variant sketches (10 top + 10 bottom) as two 5×2 PNG grids.
Reuses helpers from tools/pillar_preview.py.

Run:
    SDL_VIDEODRIVER=dummy python tools/pillar_sketches.py
Output:
    docs/sketches/top_pillars.png
    docs/sketches/bottom_pillars.png
    docs/sketches/README.md
"""
import os, sys, math, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(__file__))
from pillar_preview import (
    lerp, stone_body, silhouette_blit, draw_pine, draw_mist,
    STONE_LT, STONE_MID, STONE_DK, STONE_ACC,
    PINE_DK, PINE_MID, PINE_LT, TRUNK, MOSS, RUST, LICHEN, FOG,
    SKY_TOP, SKY_MID, SKY_BOT,
)
import pygame

# ── Grid layout ───────────────────────────────────────────────────────────────
TILE_W = 220
TILE_H = 390
DRAW_H = 355
GRID_COLS = 5
CANVAS_W = TILE_W * GRID_COLS
CANVAS_H = TILE_H * 2

PW = 80
TOP_H = 220
BOT_TOP = 85
BOT_H = DRAW_H - BOT_TOP


def _sky_bg(surf, ox, oy):
    """Paint per-tile sky + slim ground strip."""
    for ly in range(DRAW_H):
        t = ly / (DRAW_H - 1)
        if t < 0.6:
            c = lerp(SKY_TOP, SKY_MID, t / 0.6)
        else:
            c = lerp(SKY_MID, SKY_BOT, (t - 0.6) / 0.4)
        pygame.draw.line(surf, c, (ox, oy + ly), (ox + TILE_W - 1, oy + ly))
    for ly in range(max(0, DRAW_H - 20), DRAW_H):
        t = (ly - (DRAW_H - 20)) / 19
        c = lerp((80, 160, 80), (40, 100, 50), t)
        pygame.draw.line(surf, c, (ox, oy + ly), (ox + TILE_W - 1, oy + ly))


def _label(surf, text, ox, oy, font):
    """Draw label bar at bottom of tile."""
    lbl = font.render(text, True, (230, 220, 200))
    bg = pygame.Surface((TILE_W, TILE_H - DRAW_H), pygame.SRCALPHA)
    bg.fill((25, 20, 35, 245))
    surf.blit(bg, (ox, oy + DRAW_H))
    surf.blit(lbl, (ox + TILE_W // 2 - lbl.get_width() // 2, oy + DRAW_H + 6))


# ── TOP VARIANTS ──────────────────────────────────────────────────────────────

def top_t1(surf, ox, oy, seed):
    """T1 — Slender Fang: single narrow tapering spire."""
    cx = ox + TILE_W // 2
    th, pw = TOP_H, PW
    body = stone_body(pw, th, seed)
    poly = [
        (0, 0), (pw, 0),
        (pw - 4, th - 60), (pw - 14, th - 30), (pw // 2 + 10, th - 8),
        (pw // 2 - 4, th), (pw // 2 - 16, th - 8),
        (16, th - 30), (4, th - 60),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, oy))
    draw_pine(surf, cx - 4, oy + th - 4, 35, lean=-10, direction='down', layers=4)


def top_t2(surf, ox, oy, seed):
    """T2 — Twin Fork: body splits into two uneven fangs."""
    cx = ox + TILE_W // 2
    th, pw = TOP_H, PW
    body = stone_body(pw, th, seed)
    poly = [
        (0, 0), (pw, 0),
        (pw - 4, th - 80), (pw - 12, th - 45),
        (pw // 2 + 22, th - 18), (pw // 2 + 16, th), (pw // 2 + 6, th - 22),
        (pw // 2 - 2, th - 30), (pw // 2 - 14, th - 12), (pw // 2 - 20, th - 2),
        (pw // 2 - 28, th - 18), (14, th - 45), (4, th - 80),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, oy))
    draw_pine(surf, cx - 18, oy + th - 6, 28, lean=-6, direction='down', layers=3)
    draw_pine(surf, cx + 14, oy + th - 6, 22, lean=6, direction='down', layers=3)


def top_t3(surf, ox, oy, seed):
    """T3 — Curved Sabre: body leans right; moss cascade on left side."""
    cx = ox + TILE_W // 2
    th = TOP_H
    pw2 = PW + 20
    body = stone_body(pw2, th, seed)
    mid = pw2 // 2
    poly = [
        (0, 0), (pw2, 0),
        (pw2 - 2, th - 80), (pw2 + 8, th - 40),
        (pw2, th - 15), (mid + 18, th),
        (mid - 2, th), (mid - 28, th - 15),
        (8, th - 40), (2, th - 80),
    ]
    silhouette_blit(surf, body, poly, (cx - PW // 2 - 10, oy))
    rng = random.Random(seed + 5)
    for i in range(6):
        x0 = cx - PW // 2 + i * 6
        h = rng.randint(18, 32)
        for j in range(h):
            col = lerp(PINE_DK, MOSS, j / h)
            pygame.draw.line(surf, col, (x0, oy + th + j), (x0, oy + th + j + 1), 1)
        pygame.draw.circle(surf, PINE_MID, (x0, oy + th + h), 2)


def top_t4(surf, ox, oy, seed):
    """T4 — Stepped Terraces: three staircase ledges."""
    cx = ox + TILE_W // 2
    th, pw = TOP_H, PW
    s1, s2 = th // 3, 2 * th // 3
    body = stone_body(pw, th, seed)
    poly = [
        (0, 0), (pw, 0),
        (pw, s1), (pw // 2 + 22, s1),
        (pw // 2 + 22, s2), (pw // 2 + 12, s2),
        (pw // 2 + 12, th - 14), (pw // 2 + 4, th), (pw // 2 - 4, th), (pw // 2 - 12, th - 14),
        (pw // 2 - 12, s2), (pw // 2 - 22, s2),
        (pw // 2 - 22, s1), (0, s1),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, oy))
    for ledge_y in [s1 + 2, s2 + 2]:
        pygame.draw.ellipse(surf, PINE_DK, (cx - 14, oy + ledge_y - 5, 28, 8))
        pygame.draw.ellipse(surf, PINE_MID, (cx - 10, oy + ledge_y - 4, 20, 6))


def top_t5(surf, ox, oy, seed):
    """T5 — Hollow Arch: rectangular window cut through mid-body."""
    cx = ox + TILE_W // 2
    th, pw = TOP_H, PW
    body = stone_body(pw, th, seed)
    poly = [
        (0, 0), (pw, 0),
        (pw - 2, th - 55), (pw - 10, th - 28),
        (pw // 2 + 14, th - 8), (pw // 2 - 4, th), (pw // 2 - 18, th - 8),
        (12, th - 28), (2, th - 55),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, oy))
    ax1, ax2 = pw // 2 - 12, pw // 2 + 12
    ay1, ay2 = th // 3, th // 2 + 10
    win = pygame.Surface((ax2 - ax1, ay2 - ay1))
    for ly in range(win.get_height()):
        t = ly / max(1, win.get_height() - 1)
        pygame.draw.line(win, lerp(SKY_TOP, SKY_MID, t * 0.8), (0, ly), (win.get_width() - 1, ly))
    surf.blit(win, (cx - pw // 2 + ax1, oy + ay1))
    for dx in range(ax1 + 3, ax2 - 3, 5):
        x0 = cx - pw // 2 + dx
        for j in range(14):
            pygame.draw.line(surf, lerp(MOSS, PINE_DK, j / 14), (x0, oy + ay2 + j), (x0, oy + ay2 + j + 1), 1)


def top_t6(surf, ox, oy, seed):
    """T6 — Vine Drape: cylindrical body with ≥6 heavy moss vines."""
    cx = ox + TILE_W // 2
    th, pw = TOP_H, PW
    body = stone_body(pw, th, seed)
    poly = [
        (4, 0), (pw - 4, 0),
        (pw - 2, th - 50), (pw - 6, th - 25),
        (pw // 2 + 8, th - 8), (pw // 2 - 2, th),
        (pw // 2 - 12, th - 8), (6, th - 25), (2, th - 50),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, oy))
    rng = random.Random(seed + 77)
    for i in range(8):
        x0 = cx - pw // 2 + 6 + i * (pw - 12) // 7
        vh = rng.randint(22, 44)
        for j in range(vh):
            jit = int(math.sin(j * 0.4 + i) * 1.5)
            pygame.draw.line(surf, lerp(MOSS, PINE_DK, j / vh), (x0 + jit, oy + th + j), (x0 + jit, oy + th + j + 1), 1)
        pygame.draw.circle(surf, PINE_MID, (x0, oy + th + vh), 3)


def top_t7(surf, ox, oy, seed):
    """T7 — Moss-Crown Bell: wide flat top, thin neck, broad moss mat."""
    cx = ox + TILE_W // 2
    th = TOP_H
    cap_w = PW + 28
    body = stone_body(cap_w, th, seed)
    poly = [
        (0, 0), (cap_w, 0),
        (cap_w, th // 3), (cap_w - 10, th // 3 + 12),
        (cap_w // 2 + 10, th // 3 + 22), (cap_w // 2 + 6, th - 20),
        (cap_w // 2 + 2, th), (cap_w // 2 - 6, th),
        (cap_w // 2 - 12, th - 20), (cap_w // 2 - 16, th // 3 + 22),
        (10, th // 3 + 12), (0, th // 3),
    ]
    silhouette_blit(surf, body, poly, (cx - cap_w // 2, oy))
    moss_y = oy + th // 3 + 16
    for dx in range(-cap_w // 2 + 6, cap_w // 2 - 6, 7):
        x0 = cx + dx
        pygame.draw.line(surf, MOSS, (x0, moss_y), (x0, moss_y + 10), 2)
        pygame.draw.circle(surf, PINE_MID, (x0, moss_y + 10), 3)


def top_t8(surf, ox, oy, seed):
    """T8 — Chipped Needle: fracture at mid-height with accent stripe."""
    cx = ox + TILE_W // 2
    th = TOP_H
    pw = PW - 12
    body = stone_body(pw, th, seed)
    bk = th // 2 + 8
    poly_up = [
        (0, 0), (pw, 0),
        (pw - 2, bk - 10), (pw - 10, bk - 2),
        (pw // 2 + 6, bk + 2), (pw // 2 - 4, bk + 2),
        (8, bk - 2), (2, bk - 10),
    ]
    silhouette_blit(surf, body, poly_up, (cx - pw // 2, oy))
    poly_dn = [
        (2, bk - 2), (pw + 2, bk - 2),
        (pw - 4, th - 20), (pw // 2 + 8, th - 4),
        (pw // 2 - 2, th), (pw // 2 - 12, th - 4), (6, th - 20),
    ]
    body2 = stone_body(pw + 4, th - bk + 4, seed + 3)
    silhouette_blit(surf, body2, poly_dn, (cx - pw // 2 - 2, oy + bk - 2))
    pygame.draw.line(surf, STONE_ACC, (cx - pw // 2 + 2, oy + bk), (cx + pw // 2 - 2, oy + bk + 4), 3)


def top_t9(surf, ox, oy, seed):
    """T9 — Fortress Rampart: squared profile with crenellations."""
    cx = ox + TILE_W // 2
    th = TOP_H
    pw = PW + 14
    body = stone_body(pw, th, seed)
    m_w, c_w = 18, 14
    x = pw - 2
    poly = [(2, 0), (pw - 2, 0), (pw - 2, th - 50)]
    # Build crenellations from right to left
    for step in range(3):
        poly.append((x, th - 50))
        x -= m_w
        poly.append((x, th - 50))
        poly.append((x, th))
        x -= c_w
        poly.append((x, th))
        poly.append((x, th - 50))
    poly.append((2, th - 50))
    poly.append((2, 0))
    silhouette_blit(surf, body, poly, (cx - pw // 2, oy))
    # Tiny pines in crenel gaps
    for gap_x in [cx - pw // 2 + 25, cx - pw // 2 + 57]:
        draw_pine(surf, gap_x, oy + th, 16, lean=0, direction='down', layers=2)


def top_t10(surf, ox, oy, seed):
    """T10 — Crystal Tip: slender spire with amber quartz at the point."""
    cx = ox + TILE_W // 2
    th = TOP_H
    pw = PW - 16
    body = stone_body(pw, th, seed)
    poly = [
        (0, 0), (pw, 0),
        (pw - 2, th - 72), (pw - 8, th - 42),
        (pw // 2 + 6, th - 16), (pw // 2, th),
        (pw // 2 - 6, th - 16), (8, th - 42), (2, th - 72),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, oy))
    tip_x, tip_y = cx, oy + th
    for ang, size in [(0, 10), (45, 8), (90, 7), (135, 9), (-45, 6), (-90, 8)]:
        rad = math.radians(ang)
        ex = int(tip_x + math.cos(rad) * 8)
        ey = int(tip_y + math.sin(rad) * 8)
        pts = [
            (tip_x, tip_y - 2), (ex - size // 3, ey),
            (tip_x, tip_y + 2), (ex + size // 3, ey),
        ]
        pygame.draw.polygon(surf, (255, 200, 80), pts)
    pygame.draw.circle(surf, (255, 230, 120), (tip_x, tip_y), 4)


# ── BOTTOM VARIANTS ───────────────────────────────────────────────────────────

def bot_b1(surf, ox, oy, seed):
    """B1 — Primary Peak: single tall spire."""
    cx = ox + TILE_W // 2
    pw, bt, bh = PW, oy + BOT_TOP, BOT_H
    body = stone_body(pw, bh, seed)
    poly = [
        (pw // 2 - 8, 0), (pw // 2 + 12, 0),
        (pw - 18, 18), (pw - 6, 40), (pw - 4, 80), (pw, 130),
        (pw, bh), (0, bh), (0, 130), (8, 80), (14, 40), (24, 18),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, bt))
    draw_pine(surf, cx + 2, bt + 2, 68, lean=16, direction='up', layers=6)
    draw_pine(surf, cx - pw // 2 + 8, bt + 36, 28, lean=-5, direction='up', layers=4)
    draw_mist(surf, cx, oy + DRAW_H - 4, pw)


def bot_b2(surf, ox, oy, seed):
    """B2 — Twin Peak: two uneven summits."""
    cx = ox + TILE_W // 2
    pw, bt, bh = PW, oy + BOT_TOP, BOT_H
    body = stone_body(pw, bh, seed)
    poly = [
        (pw // 2 - 26, 6), (pw // 2 - 18, 0), (pw // 2 - 8, 4),
        (pw // 2 - 2, 22), (pw // 2 + 6, 18), (pw // 2 + 18, 14), (pw // 2 + 26, 22),
        (pw // 2 + 32, 30), (pw - 6, 50), (pw, 90), (pw, bh),
        (0, bh), (0, 90), (6, 50), (pw // 2 - 30, 24),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, bt))
    draw_pine(surf, cx - 22, bt + 6, 55, lean=-12, direction='up', layers=5)
    draw_pine(surf, cx + 22, bt + 18, 42, lean=10, direction='up', layers=4)
    pygame.draw.ellipse(surf, PINE_DK, (cx - 8, bt + 16, 18, 8))
    pygame.draw.ellipse(surf, PINE_MID, (cx - 6, bt + 17, 14, 6))
    draw_mist(surf, cx, oy + DRAW_H - 4, pw)


def bot_b3(surf, ox, oy, seed):
    """B3 — Forested Mesa: flat tabletop with 3–4 pines."""
    cx = ox + TILE_W // 2
    pw, bt, bh = PW + 20, oy + BOT_TOP, BOT_H
    body = stone_body(pw, bh, seed)
    poly = [(14, 0), (pw - 14, 0), (pw, 20), (pw, bh), (0, bh), (0, 20)]
    silhouette_blit(surf, body, poly, (cx - pw // 2, bt))
    for dx, h, lean in [(-24, 52, -5), (-8, 64, -2), (8, 56, 4), (24, 44, 7)]:
        draw_pine(surf, cx + dx, bt + 2, h, lean=lean, direction='up', layers=4)
    draw_mist(surf, cx, oy + DRAW_H - 4, pw)


def bot_b4(surf, ox, oy, seed):
    """B4 — Ancient Sentinel: broad squat base, one enormous old pine."""
    cx = ox + TILE_W // 2
    pw = PW + 12
    bt = oy + BOT_TOP + 45
    bh = BOT_H - 45
    body = stone_body(pw, bh, seed)
    poly = [
        (pw // 2 - 8, 0), (pw // 2 + 8, 0), (pw // 2 + 20, 10),
        (pw - 8, 28), (pw, 70), (pw, bh), (0, bh), (0, 70), (8, 28), (pw // 2 - 20, 10),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, bt))
    draw_pine(surf, cx, bt, 88, lean=24, direction='up', layers=7)
    for dx in [-32, -14, 18, 34]:
        pygame.draw.ellipse(surf, PINE_DK, (cx + dx - 9, bt + bh - 22, 20, 10))
        pygame.draw.ellipse(surf, PINE_MID, (cx + dx - 7, bt + bh - 21, 16, 8))
    draw_mist(surf, cx, oy + DRAW_H - 4, pw)


def bot_b5(surf, ox, oy, seed):
    """B5 — Stepped Plateau: stair-stepped terraces."""
    cx = ox + TILE_W // 2
    pw, bt, bh = PW, oy + BOT_TOP, BOT_H
    s1, s2 = bh // 3, 2 * bh // 3
    body = stone_body(pw, bh, seed)
    poly = [
        (pw // 2 - 6, 0), (pw // 2 + 6, 0),
        (pw // 2 + 18, s1), (pw, s1), (pw, s1 + 8), (pw // 2 + 18, s1 + 8),
        (pw // 2 + 18, s2), (pw, s2), (pw, s2 + 8), (pw, bh),
        (0, bh), (0, s2 + 8), (0, s2), (pw // 2 - 18, s2),
        (pw // 2 - 18, s1 + 8), (0, s1 + 8), (0, s1), (pw // 2 - 18, s1),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, bt))
    draw_pine(surf, cx, bt + 2, 52, lean=10, direction='up', layers=5)
    draw_pine(surf, cx + 12, bt + s1 + 10, 38, lean=6, direction='up', layers=4)
    draw_pine(surf, cx - 10, bt + s2 + 10, 28, lean=-5, direction='up', layers=3)
    draw_mist(surf, cx, oy + DRAW_H - 4, pw)


def bot_b6(surf, ox, oy, seed):
    """B6 — Arched Gateway: window at mid-height."""
    cx = ox + TILE_W // 2
    pw = PW + 8
    bt, bh = oy + BOT_TOP, BOT_H
    wy1, wy2 = bh // 3, bh // 2 + 10
    wx1, wx2 = 12, pw - 12
    body = stone_body(pw, bh, seed)
    poly = [
        (pw // 2 - 6, 0), (pw // 2 + 6, 0), (pw - 14, 16), (pw, 50),
        (pw, bh), (0, bh), (0, 50), (14, 16),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, bt))
    win = pygame.Surface((wx2 - wx1, wy2 - wy1))
    for ly in range(win.get_height()):
        pygame.draw.line(win, lerp(SKY_MID, SKY_BOT, ly / max(1, win.get_height() - 1)), (0, ly), (win.get_width() - 1, ly))
    surf.blit(win, (cx - pw // 2 + wx1, bt + wy1))
    for dx in range(wx1 + 4, wx2 - 4, 8):
        x0 = cx - pw // 2 + dx
        for j in range(14):
            pygame.draw.line(surf, lerp(MOSS, PINE_DK, j / 14), (x0, bt + wy2 + j), (x0, bt + wy2 + j + 1), 1)
    draw_pine(surf, cx, bt + 2, 52, lean=12, direction='up', layers=5)
    draw_mist(surf, cx, oy + DRAW_H - 4, pw)


def bot_b7(surf, ox, oy, seed):
    """B7 — Stalagmite Cluster: 3 thin parallel spires."""
    cx = ox + TILE_W // 2
    bt = oy + BOT_TOP
    bh = BOT_H
    for i, (dx, spw, sph) in enumerate([(-28, 24, bh), (0, 20, bh - 20), (28, 22, bh - 8)]):
        body = stone_body(spw, sph, seed + i)
        poly = [
            (spw // 2 - 4, 0), (spw // 2 + 4, 0),
            (spw - 4, 20), (spw, 50), (spw, sph), (0, sph), (0, 50), (4, 20),
        ]
        silhouette_blit(surf, body, poly, (cx + dx - spw // 2, bt + (bh - sph)))
        draw_pine(surf, cx + dx, bt + (bh - sph) + 2, 32 + abs(dx) // 4, lean=dx // 6, direction='up', layers=3)
    draw_mist(surf, cx, oy + DRAW_H - 4, PW)


def bot_b8(surf, ox, oy, seed):
    """B8 — Mushroom Rock: narrow stem, wider overhanging cap."""
    cx = ox + TILE_W // 2
    bt = oy + BOT_TOP
    bh = BOT_H
    cap_w = PW + 32
    stem_w = 20
    cap_h = bh // 3
    stem_h = bh - cap_h
    body_s = stone_body(stem_w, stem_h, seed)
    poly_s = [(0, 0), (stem_w, 0), (stem_w - 2, stem_h), (0, stem_h)]
    silhouette_blit(surf, body_s, poly_s, (cx - stem_w // 2, bt + cap_h))
    body_c = stone_body(cap_w, cap_h + 8, seed + 5)
    poly_c = []
    for bx in range(0, cap_w + 1, 4):
        t = bx / cap_w
        cy = int(cap_h // 3 * (1 - (2 * t - 1) ** 2))
        poly_c.append((bx, cy))
    poly_c += [
        (cap_w, cap_h + 8), (cap_w // 2 + stem_w // 2 + 2, cap_h),
        (cap_w // 2 - stem_w // 2 - 2, cap_h), (0, cap_h + 8),
    ]
    silhouette_blit(surf, body_c, poly_c, (cx - cap_w // 2, bt))
    draw_pine(surf, cx - 18, bt + cap_h // 3 + 6, 44, lean=-8, direction='up', layers=4)
    draw_pine(surf, cx + 16, bt + cap_h // 3 + 6, 38, lean=8, direction='up', layers=4)
    for dx in range(-cap_w // 2 + 6, cap_w // 2 - 6, 8):
        x0 = cx + dx
        pygame.draw.line(surf, MOSS, (x0, bt + cap_h), (x0, bt + cap_h + 8), 1)
    draw_mist(surf, cx, oy + DRAW_H - 4, cap_w // 2)


def bot_b9(surf, ox, oy, seed):
    """B9 — Shrine Ziggurat: trapezoidal tiered plinth."""
    cx = ox + TILE_W // 2
    bt = oy + BOT_TOP
    bh = BOT_H
    pw = PW + 20
    body = stone_body(pw, bh, seed)
    th = bh // 4
    poly = [
        (44, 0), (56, 0),
        (56, th), (66, th), (66, th * 2), (76, th * 2),
        (76, th * 3), (86, th * 3), (pw, bh), (0, bh),
        (14, th * 3), (24, th * 3), (24, th * 2), (34, th * 2),
        (34, th), (44, th),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, bt))
    draw_pine(surf, cx + 4, bt + 2, 64, lean=10, direction='up', layers=5)
    for t in range(1, 4):
        y = th * t + 4
        for dx in [-22 + t * 8, 22 - t * 8]:
            pygame.draw.ellipse(surf, PINE_DK, (cx + dx - 10, bt + y - 5, 16, 8))
            pygame.draw.ellipse(surf, PINE_MID, (cx + dx - 8, bt + y - 4, 12, 6))
    draw_mist(surf, cx, oy + DRAW_H - 4, pw)


def bot_b10(surf, ox, oy, seed):
    """B10 — Waterfall Face: silver streak, pine + thick mist."""
    cx = ox + TILE_W // 2
    pw, bt, bh = PW, oy + BOT_TOP, BOT_H
    body = stone_body(pw, bh, seed)
    poly = [
        (pw // 2 - 10, 0), (pw // 2 + 10, 0), (pw - 14, 18), (pw, 60),
        (pw, bh), (0, bh), (0, 60), (14, 18),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, bt))
    wx = cx + 6
    for j in range(bh - 10):
        if j > bh * 0.7:
            break
        sw = max(1, 5 - j // 35)
        col = lerp((240, 245, 255), SKY_MID, j / bh)
        pygame.draw.line(surf, col, (wx - sw // 2, bt + j), (wx + sw // 2, bt + j), sw)
    draw_pine(surf, cx - 8, bt + 2, 62, lean=-10, direction='up', layers=5)
    draw_mist(surf, cx, oy + DRAW_H - 4, pw + 20)
    draw_mist(surf, cx, oy + DRAW_H - 14, pw)


# ── Grid renderer ─────────────────────────────────────────────────────────────

TOP_VARIANTS = [
    (top_t1, "T1 Slender Fang"),
    (top_t2, "T2 Twin Fork"),
    (top_t3, "T3 Curved Sabre"),
    (top_t4, "T4 Stepped Terraces"),
    (top_t5, "T5 Hollow Arch"),
    (top_t6, "T6 Vine Drape"),
    (top_t7, "T7 Moss-Crown Bell"),
    (top_t8, "T8 Chipped Needle"),
    (top_t9, "T9 Fortress Rampart"),
    (top_t10, "T10 Crystal Tip"),
]

BOT_VARIANTS = [
    (bot_b1, "B1 Primary Peak"),
    (bot_b2, "B2 Twin Peak"),
    (bot_b3, "B3 Forested Mesa"),
    (bot_b4, "B4 Ancient Sentinel"),
    (bot_b5, "B5 Stepped Plateau"),
    (bot_b6, "B6 Arched Gateway"),
    (bot_b7, "B7 Stalagmite Cluster"),
    (bot_b8, "B8 Mushroom Rock"),
    (bot_b9, "B9 Shrine Ziggurat"),
    (bot_b10, "B10 Waterfall Face"),
]


def render_grid(variants, out_path):
    surf = pygame.Surface((CANVAS_W, CANVAS_H))
    surf.fill((15, 12, 22))
    font = pygame.font.SysFont("arial", 16, bold=True)
    for idx, (fn, label) in enumerate(variants):
        row = idx // GRID_COLS
        col = idx % GRID_COLS
        ox = col * TILE_W
        oy = row * TILE_H
        _sky_bg(surf, ox, oy)
        fn(surf, ox, oy, seed=(idx + 1) * 31)
        _label(surf, label, ox, oy, font)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pygame.image.save(surf, out_path)
    print("wrote", out_path)


def main():
    pygame.init()
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "sketches")
    render_grid(TOP_VARIANTS, os.path.join(out_dir, "top_pillars.png"))
    render_grid(BOT_VARIANTS, os.path.join(out_dir, "bottom_pillars.png"))
    print("\nNow write docs/sketches/README.md with embedded images")


if __name__ == "__main__":
    main()
