"""
Shared pillar vegetation + ornament helpers.

These draw_* primitives (moss, ferns, vines, prayer flags, cairns, lanterns,
ribbons, …) are biome-tinted, collision-free decoration drawn by the pagoda
pillars (game/pillar_pagodas.py + game/pagoda_ornaments.py) and by the
archived sandstone variants (archive/sandstone_pillars.py).
"""
import math, random
import pygame

from game.draw import (
    draw_wuling_pine, _shade_c, _accent_under_foliage,
)


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


_INCENSE_CACHE: dict = {}


def _incense_smoke_sprite(length):
    """The incense wisp is a fixed sin-curve fade (no time/palette input), so it
    bakes once per `length` rather than allocating ~`length` tiny surfaces every
    call (this ran ~32 allocations/frame across the night braziers)."""
    spr = _INCENSE_CACHE.get(length)
    if spr is None:
        spr = pygame.Surface((8, length + 1), pygame.SRCALPHA)
        ry = length - 1
        puff = pygame.Surface((4, 2), pygame.SRCALPHA)
        for i in range(length):
            t = i / max(1, length)
            off = int(math.sin(t * 6) * 2)
            a = int(140 * (1 - t))
            puff.fill((230, 230, 230, a))
            spr.blit(puff, (off + 2, ry - i))
        _INCENSE_CACHE[length] = spr
    return spr


def draw_incense_smoke(surf, x, y, length=20):
    surf.blit(_incense_smoke_sprite(length), (x - 4, y - (length - 1)))


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
    """A CLEAR draped silhouette spilling over a front-left lip: one thicker
    primary strand + one shorter secondary, 3-4 readable teardrop leaf nodes, a
    curling tendril tip, and one small bloom where the vine grips the rim. `(x,y)`
    is the rim attachment point; the strand falls and curls outward. The bloom +
    leaf-tip highlight are routed through _accent_under_foliage so no decor leaf
    out-glows the coin at night. Signature unchanged (the near-lane caller still
    draws it on a scratch + dims it, which now stacks safely under the cap)."""
    dark = palette['foliage_dark']
    mid  = palette['foliage_mid']
    top  = palette['foliage_top']
    leaf_lt = _accent_under_foliage(top, palette)

    def strand(x0, y0, ln, sway, width, nodes):
        pts = [(x0, y0)]
        for i in range(1, ln + 1):
            t = i / ln
            px = x0 - int(math.sin(t * 2.0) * sway) - int(t * 3)
            py = y0 + int(t * (ln + 6))
            pts.append((px, py))
        pygame.draw.lines(surf, _shade_c(dark, -14), False, pts, width + 1)
        pygame.draw.lines(surf, dark, False, pts, width)
        for ni in range(nodes):
            idx = 1 + (ni + 1) * (len(pts) - 2) // (nodes + 1)
            px, py = pts[idx]
            side = -1 if ni % 2 == 0 else 1
            lx = px + side * 3
            pygame.draw.polygon(surf, mid,
                                [(px, py - 1), (lx, py - 2),
                                 (lx + side, py + 1), (px, py + 2)])
            pygame.draw.line(surf, leaf_lt, (px, py - 1), (lx, py - 1), 1)
        return pts

    # Primary draped strand — longest, spilling furthest over the lip. Length
    # tracks the `length` arg so the pillar eaves and the near-lane both scale.
    ln = max(8, length)
    primary = strand(x, y, ln, 4, 2, 3)
    strand(x + 3, y + 1, max(5, ln - 4), 3, 1, 2)
    # The top two leaf pixels tuck just behind/at the rim so the vine visibly
    # grips the edge with no floating gap (handled here by anchoring the strand
    # AT (x, y); a small grip leaf sits right at the attachment).
    pygame.draw.polygon(surf, mid, [(x, y), (x - 3, y - 1), (x - 2, y + 2)])
    pygame.draw.line(surf, leaf_lt, (x, y - 1), (x - 3, y - 1), 1)
    # Curling tendril tip at the very end of the primary strand.
    ex, ey = primary[-1]
    pygame.draw.lines(surf, dark, False,
                      [(ex, ey), (ex + 2, ey + 2), (ex, ey + 3)], 1)
    # One small bloom tucked at the rim attachment, value-capped under foliage.
    pygame.draw.circle(surf, _accent_under_foliage((240, 196, 124), palette),
                       (x - 1, y + 2), 1)


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

