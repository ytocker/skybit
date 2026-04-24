"""
Render 5 pillar variant options side-by-side for visual review.

Each variant keeps the current Zhangjiajie-style sandstone pillar
(same silhouette, same stone body, same pine / moss helpers from
game.draw) and adds ONLY:
  - a slight stone palette tweak
  - a vegetation mix change
  - one signature "lively" ornament (flags, ribbon, lantern, crane, cairn)

Run:
    python tools/pillar_variants_preview.py
Output:
    docs/sketches/pillar_variants.png   (1500x820, five columns)
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
W, H = 1500, 820
COLS = 5
COL_W = W // COLS
TOP_H = 240
GAP_H = 230
BOT_TOP = TOP_H + GAP_H
GROUND_Y = H - 40
PILLAR_W = 90

# Day-biome palette (matches game/biome.py DAY keyframe) ─ foliage reused for all
FOLIAGE = dict(
    foliage_top=(140, 220, 110),
    foliage_mid=(70, 170, 75),
    foliage_dark=(30, 100, 50),
    foliage_accent=(255, 240, 120),
)

SKY_TOP, SKY_MID, SKY_BOT = (40, 110, 200), (90, 170, 230), (170, 220, 245)
HORIZON = (255, 240, 200)
GROUND_T, GROUND_B = (80, 200, 80), (60, 100, 50)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ── Background ───────────────────────────────────────────────────────────────

def paint_bg(surf):
    for y in range(H):
        t = y / (H - 1)
        if t < 0.45:
            c = lerp(SKY_TOP, SKY_MID, t / 0.45)
        else:
            c = lerp(SKY_MID, SKY_BOT, (t - 0.45) / 0.55)
        pygame.draw.line(surf, c, (0, y), (W - 1, y))
    glow = pygame.Surface((W, 90), pygame.SRCALPHA)
    for y in range(90):
        a = int(110 * (1 - y / 89))
        pygame.draw.line(glow, (*HORIZON, a), (0, y), (W - 1, y))
    surf.blit(glow, (0, GROUND_Y - 90))
    # Distant mountains
    pts = [(0, GROUND_Y)]
    for x in range(0, W + 1, 8):
        h = int(60 + math.sin(x * 0.012) * 26 + math.sin(x * 0.04) * 12)
        pts.append((x, GROUND_Y - h))
    pts.append((W, GROUND_Y))
    pygame.draw.polygon(surf, (90, 110, 150), pts)
    # Ground
    for y in range(GROUND_Y, H):
        t = (y - GROUND_Y) / max(1, H - GROUND_Y - 1)
        pygame.draw.line(surf, lerp(GROUND_T, GROUND_B, t), (0, y), (W - 1, y))


# ── Ornaments ────────────────────────────────────────────────────────────────

FLAG_COLORS = [(70, 140, 230), (245, 245, 245), (230, 70, 70), (80, 180, 90), (245, 210, 70)]


def draw_prayer_flags(surf, x1, y1, x2, y2, seed=0):
    """String of 5 small rectangular flags on a curved line from (x1,y1) to (x2,y2)."""
    rng = random.Random(seed)
    # Sagging curve control point
    mx = (x1 + x2) // 2
    my = max(y1, y2) + 18
    # Sample points along quadratic bezier for the string
    steps = 40
    pts = []
    for i in range(steps + 1):
        t = i / steps
        bx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2
        by = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2
        pts.append((int(bx), int(by)))
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, (90, 70, 55), pts[i], pts[i + 1], 1)
    # Place ~7 flags across the string
    n_flags = 7
    for i in range(n_flags):
        t = (i + 0.5) / n_flags
        idx = int(t * steps)
        px, py = pts[idx]
        col = FLAG_COLORS[i % len(FLAG_COLORS)]
        flag_w, flag_h = 9, 13
        flag_rect = pygame.Rect(px - flag_w // 2, py, flag_w, flag_h)
        pygame.draw.rect(surf, col, flag_rect)
        pygame.draw.rect(surf, (40, 30, 20), flag_rect, 1)
        # Subtle highlight
        pygame.draw.line(surf, lerp(col, (255, 255, 255), 0.4),
                         (flag_rect.x + 1, flag_rect.y + 1),
                         (flag_rect.x + 1, flag_rect.bottom - 2), 1)


def draw_trunk_ribbon(surf, trunk_x, trunk_y, seed=0):
    """Red silk ribbon tied around a pine trunk with two fluttering tails."""
    rng = random.Random(seed)
    # Knot
    pygame.draw.ellipse(surf, (180, 30, 40), (trunk_x - 4, trunk_y - 3, 8, 6))
    pygame.draw.ellipse(surf, (230, 60, 60), (trunk_x - 3, trunk_y - 2, 6, 4))
    # Two fluttering tails — sinuous polygon
    for side, col in ((-1, (210, 40, 50)), (1, (230, 80, 80))):
        tail = []
        for i in range(7):
            t = i / 6
            x = trunk_x + side * int(4 + t * 18)
            y = trunk_y + int(math.sin(t * 3.3 + rng.random()) * 3) + int(t * 6)
            tail.append((x, y))
        # Back-edge offset to give width
        tail_back = [(x, y + 4) for x, y in reversed(tail)]
        poly = tail + tail_back
        pygame.draw.polygon(surf, col, poly)
        pygame.draw.polygon(surf, (120, 20, 30), poly, 1)


def draw_paper_lantern(surf, hang_x, hang_y, strand_len=16):
    """Red paper lantern hanging from a short cord."""
    # Cord
    pygame.draw.line(surf, (50, 40, 30), (hang_x, hang_y), (hang_x, hang_y + strand_len), 1)
    cx = hang_x
    cy = hang_y + strand_len
    lw, lh = 18, 22
    # Top & bottom caps (dark wood)
    pygame.draw.rect(surf, (55, 35, 25), (cx - 7, cy, 14, 3))
    pygame.draw.rect(surf, (55, 35, 25), (cx - 7, cy + lh - 3, 14, 3))
    # Body — rounded red with vertical ribs
    body_rect = pygame.Rect(cx - lw // 2, cy + 2, lw, lh - 4)
    pygame.draw.ellipse(surf, (170, 30, 35), body_rect)
    pygame.draw.ellipse(surf, (230, 70, 65), body_rect.inflate(-4, -3))
    # Two vertical ribs
    pygame.draw.line(surf, (130, 20, 25), (cx - 4, cy + 3), (cx - 4, cy + lh - 5), 1)
    pygame.draw.line(surf, (130, 20, 25), (cx + 4, cy + 3), (cx + 4, cy + lh - 5), 1)
    # Glowing flame center
    glow = pygame.Surface((24, 24), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 220, 120, 90), (12, 12), 10)
    pygame.draw.circle(glow, (255, 240, 180, 160), (12, 12), 5)
    surf.blit(glow, (cx - 12, cy + lh // 2 - 12))
    # Tassel below
    pygame.draw.line(surf, (200, 160, 40), (cx, cy + lh), (cx, cy + lh + 5), 1)
    pygame.draw.circle(surf, (220, 180, 60), (cx, cy + lh + 6), 2)


def draw_crane(surf, cx, base_y):
    """Small white crane silhouette perched on a ledge."""
    # Body oval
    pygame.draw.ellipse(surf, (250, 250, 250), (cx - 7, base_y - 10, 14, 8))
    pygame.draw.ellipse(surf, (210, 215, 220), (cx - 6, base_y - 9, 12, 6))
    # Folded wing shadow
    pygame.draw.ellipse(surf, (40, 40, 50), (cx - 3, base_y - 9, 8, 4))
    # Neck — curved polyline
    neck_pts = [(cx - 1, base_y - 9), (cx - 4, base_y - 13),
                (cx - 3, base_y - 17), (cx + 1, base_y - 20)]
    for i in range(len(neck_pts) - 1):
        pygame.draw.line(surf, (250, 250, 250), neck_pts[i], neck_pts[i + 1], 2)
    # Head + beak
    pygame.draw.circle(surf, (250, 250, 250), (cx + 1, base_y - 20), 2)
    pygame.draw.line(surf, (230, 150, 60), (cx + 2, base_y - 20), (cx + 6, base_y - 19), 1)
    # Red crown
    pygame.draw.circle(surf, (220, 40, 50), (cx + 1, base_y - 21), 1)
    # Two thin legs
    pygame.draw.line(surf, (40, 30, 30), (cx - 3, base_y - 3), (cx - 3, base_y + 3), 1)
    pygame.draw.line(surf, (40, 30, 30), (cx + 2, base_y - 3), (cx + 2, base_y + 3), 1)


def draw_cairn(surf, cx, base_y):
    """Stack of balanced stones topped with a small red pennant on a pole."""
    stones = [
        (18, 8, (130, 115, 95)),
        (14, 6, (155, 140, 115)),
        (10, 5, (180, 160, 130)),
        (7,  4, (200, 180, 145)),
    ]
    y = base_y
    for w, h, col in stones:
        r = pygame.Rect(cx - w // 2, y - h, w, h)
        pygame.draw.ellipse(surf, (60, 45, 35), r.inflate(2, 1))
        pygame.draw.ellipse(surf, col, r)
        pygame.draw.ellipse(surf, lerp(col, (255, 240, 220), 0.3),
                            (r.x + 2, r.y + 1, max(2, w - 4), max(1, h // 2)))
        y -= h - 1
    # Pennant pole
    pole_top = y - 16
    pygame.draw.line(surf, (60, 45, 30), (cx, y), (cx, pole_top), 1)
    # Red triangular pennant
    pygame.draw.polygon(surf, (200, 40, 45),
                        [(cx, pole_top), (cx + 10, pole_top + 3), (cx, pole_top + 6)])
    pygame.draw.polygon(surf, (140, 20, 25),
                        [(cx, pole_top), (cx + 10, pole_top + 3), (cx, pole_top + 6)], 1)


def draw_wildflowers(surf, cx, base_y, seed=0):
    """Small cluster of yellow + white specks on a ledge to suggest wildflowers."""
    rng = random.Random(seed)
    for _ in range(10):
        dx = rng.randint(-14, 14)
        dy = rng.randint(-3, 2)
        col = rng.choice([(255, 230, 90), (255, 255, 245), (255, 210, 80)])
        pygame.draw.circle(surf, col, (cx + dx, base_y + dy), rng.choice([1, 2]))


# ── Variant palettes ────────────────────────────────────────────────────────

VARIANTS = [
    dict(
        name="1. Pilgrim's Peak",
        subtitle="prayer-flag string",
        stone=dict(light=(225, 195, 155), mid=(175, 140, 105),
                   dark=(95, 70, 55),    accent=(255, 220, 170)),
    ),
    dict(
        name="2. Ribbon Pine",
        subtitle="red silk ribbon on trunk",
        stone=dict(light=(215, 200, 175), mid=(160, 140, 115),
                   dark=(85, 72, 60),     accent=(240, 225, 185)),
    ),
    dict(
        name="3. Lantern Ledge",
        subtitle="hanging paper lantern",
        stone=dict(light=(240, 222, 190), mid=(195, 165, 130),
                   dark=(110, 85, 65),    accent=(255, 235, 195)),
    ),
    dict(
        name="4. Crane's Rest",
        subtitle="perched crane + wildflowers",
        stone=dict(light=(220, 195, 155), mid=(175, 140, 105),
                   dark=(95, 75, 55),     accent=(255, 220, 170)),
    ),
    dict(
        name="5. Cairn Marker",
        subtitle="stacked cairn + red pennant",
        stone=dict(light=(230, 185, 140), mid=(180, 128, 90),
                   dark=(100, 60, 45),    accent=(255, 205, 150)),
    ),
]


# ── Draw one variant ─────────────────────────────────────────────────────────

def draw_variant(surf, col_idx, variant):
    cx = COL_W * col_idx + COL_W // 2
    pw = PILLAR_W
    stone = variant['stone']
    s_light, s_mid, s_dark, s_accent = stone['light'], stone['mid'], stone['dark'], stone['accent']

    palette = dict(FOLIAGE,
                   stone_light=s_light, stone_mid=s_mid,
                   stone_dark=s_dark, stone_accent=s_accent)

    # ── Top pillar ──
    top_body = get_stone_pillar_body(pw, TOP_H, s_light, s_mid, s_dark, s_accent,
                                     body_seed=col_idx * 3 + 1)
    top_poly = silhouette_top_spire(pw, TOP_H)
    silhouette_blit(surf, top_body, top_poly, (cx - pw // 2, 0))

    # Top-pillar tip approximately at (cx + 3, TOP_H - 2)
    top_tip_x = cx + 3
    top_tip_y = TOP_H - 2

    # ── Bottom pillar ──
    bot_h = GROUND_Y - BOT_TOP
    bot_body = get_stone_pillar_body(pw, bot_h, s_light, s_mid, s_dark, s_accent,
                                     body_seed=col_idx * 3 + 2)
    bot_poly = silhouette_bottom_spire(pw, bot_h)
    silhouette_blit(surf, bot_body, bot_poly, (cx - pw // 2, BOT_TOP))

    # Peak of bottom pillar (cx + ~4, BOT_TOP)
    peak_x = cx + 4
    peak_y = BOT_TOP

    # ── Vegetation + ornament per variant ──
    name = variant['name']

    if "Pilgrim" in name:
        # One dominant pine + small side shrub + moss on top pillar
        draw_wuling_pine(surf, peak_x, peak_y + 2, 74, palette,
                         lean=14, direction='up', layers=5)
        draw_side_shrub(surf, cx - pw // 2 + 10, BOT_TOP + 40, palette, scale=1.0)
        draw_moss_strand(surf, cx - 18, TOP_H - 18, 14, palette, jitter_seed=col_idx)
        # Prayer flags strung diagonally across the gap: from the top-pillar's
        # left shoulder (still inside the silhouette) down to a bough of the pine.
        flag_start = (cx - 36, TOP_H - 52)
        flag_end = (peak_x + 18, peak_y + 2 - 62)
        draw_prayer_flags(surf, flag_start[0], flag_start[1],
                          flag_end[0], flag_end[1], seed=col_idx)

    elif "Ribbon" in name:
        # Big pine + heavier moss cascade
        draw_wuling_pine(surf, peak_x, peak_y + 2, 82, palette,
                         lean=12, direction='up', layers=6)
        # Extra moss strands from top pillar
        for off, jl in ((-20, 16), (-6, 22), (10, 18)):
            draw_moss_strand(surf, cx + off, TOP_H - 14, jl, palette,
                             jitter_seed=col_idx * 5 + off)
        draw_side_shrub(surf, cx + pw // 2 - 12, BOT_TOP + 60, palette, scale=0.9)
        # Red ribbon tied low on the trunk, below the canopy so it's fully visible
        ribbon_y = peak_y + 2 - 10
        ribbon_x = peak_x + int(12 * (10 / 82))
        draw_trunk_ribbon(surf, ribbon_x, ribbon_y, seed=col_idx)

    elif "Lantern" in name:
        # Small pine + a side shrub
        draw_wuling_pine(surf, peak_x, peak_y + 2, 70, palette,
                         lean=12, direction='up', layers=5)
        draw_side_shrub(surf, cx - pw // 2 + 12, BOT_TOP + 48, palette, scale=1.0)
        draw_side_shrub(surf, cx + pw // 2 - 14, BOT_TOP + 80, palette, scale=0.8)
        # Paper lantern hanging from the top pillar's underside
        draw_paper_lantern(surf, cx - 8, TOP_H - 6, strand_len=18)

    elif "Crane" in name:
        # Pine + wildflower patch
        draw_wuling_pine(surf, peak_x, peak_y + 2, 74, palette,
                         lean=16, direction='up', layers=5)
        draw_side_shrub(surf, cx + pw // 2 - 12, BOT_TOP + 45, palette, scale=1.0)
        # Wildflowers on a low ledge
        draw_wildflowers(surf, cx - 10, BOT_TOP + 70, seed=col_idx * 7)
        # Crane perched on the bottom pillar's peak ledge, off to the side
        draw_crane(surf, peak_x - 14, peak_y + 4)

    elif "Cairn" in name:
        # Pine + 2 moss strands + 1 bigger shrub
        draw_wuling_pine(surf, peak_x + 8, peak_y + 6, 72, palette,
                         lean=14, direction='up', layers=5)
        draw_moss_strand(surf, cx - 12, TOP_H - 16, 18, palette, jitter_seed=col_idx)
        draw_side_shrub(surf, cx - pw // 2 + 10, BOT_TOP + 38, palette, scale=1.1)
        # Stone cairn on the left side of the peak
        draw_cairn(surf, peak_x - 16, peak_y + 4)

    # Mist halo on the ground
    draw_pillar_mist(surf, cx, GROUND_Y - 4, pw, alpha=110)


# ── Label ───────────────────────────────────────────────────────────────────

def label(surf, col_idx, title, subtitle, title_font, sub_font):
    cx = COL_W * col_idx + COL_W // 2
    t_surf = title_font.render(title, True, (18, 18, 26))
    s_surf = sub_font.render(subtitle, True, (60, 60, 74))
    pad = 8
    w = max(t_surf.get_width(), s_surf.get_width()) + pad * 2
    h = t_surf.get_height() + s_surf.get_height() + pad + 2
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill((255, 255, 255, 225))
    surf.blit(bg, (cx - w // 2, 14))
    surf.blit(t_surf, (cx - t_surf.get_width() // 2, 14 + pad // 2))
    surf.blit(s_surf, (cx - s_surf.get_width() // 2,
                       14 + pad // 2 + t_surf.get_height() + 1))


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    surf = pygame.Surface((W, H))
    paint_bg(surf)

    title_font = pygame.font.SysFont("arial", 20, bold=True)
    sub_font = pygame.font.SysFont("arial", 14)

    for i, variant in enumerate(VARIANTS):
        draw_variant(surf, i, variant)
    for i, variant in enumerate(VARIANTS):
        label(surf, i, variant['name'], variant['subtitle'], title_font, sub_font)

    out = "/home/user/Claude_test/docs/sketches/pillar_variants.png"
    pygame.image.save(surf, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
