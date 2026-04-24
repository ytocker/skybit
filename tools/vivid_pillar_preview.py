"""
Render the three VIVID pillar options side-by-side for visual review.

Run:
    python tools/vivid_pillar_preview.py
Output:
    docs/sketches/vivid_pillars.png   (1200x760, three columns)

Each column shows a full top+bottom pillar pair rendered in one of the
three concepts from docs/sketches/vivid_pillars.md:
  1. Aurora Crystal — cool / luminous
  2. Sakura Cascade — warm / joyful
  3. Emberforge     — hot / dramatic

This script is standalone — it does NOT modify game code.
"""
import os, math, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

# ── Canvas ───────────────────────────────────────────────────────────────────
W, H = 1200, 760
COLS = 3
COL_W = W // COLS
TOP_H = 240
GAP_H = 200
BOT_TOP = TOP_H + GAP_H
GROUND_Y = H - 40

SKY_TOP  = (40, 110, 200)
SKY_MID  = (90, 170, 230)
SKY_BOT  = (170, 220, 245)
HORIZON  = (255, 240, 200)
GROUND_T = (80, 200, 80)
GROUND_B = (60, 100, 50)
FOG_WHITE = (255, 255, 255)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ── Background ───────────────────────────────────────────────────────────────

def paint_sky(surf):
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


def paint_ground(surf):
    for y in range(GROUND_Y, H):
        t = (y - GROUND_Y) / max(1, H - GROUND_Y - 1)
        c = lerp(GROUND_T, GROUND_B, t)
        pygame.draw.line(surf, c, (0, y), (W - 1, y))


def paint_mountains(surf):
    pts = [(0, GROUND_Y)]
    for x in range(0, W + 1, 8):
        h = int(60 + math.sin(x * 0.012) * 26 + math.sin(x * 0.04) * 12)
        pts.append((x, GROUND_Y - h))
    pts.append((W, GROUND_Y))
    pygame.draw.polygon(surf, (90, 110, 150), pts)


# ── Stone body — generic (palette-driven) ────────────────────────────────────

def stone_body(w, h, pal, seed=0, glow_cracks=False):
    """Gradient stone surface with erosion cracks.
    If glow_cracks=True, cracks are drawn as emissive orange/gold lines
    (used by the Emberforge option)."""
    light, mid, dark, accent = pal['light'], pal['mid'], pal['dark'], pal['accent']
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        t = x / max(1, w - 1)
        if t < 0.18:
            c = lerp(mid, light, (0.18 - t) / 0.18)
        elif t < 0.55:
            seg = (t - 0.18) / 0.37
            seg = seg * seg * (3 - 2 * seg)
            c = lerp(light, mid, seg)
        else:
            seg = (t - 0.55) / 0.45
            seg = seg * seg * (3 - 2 * seg)
            c = lerp(mid, dark, seg)
        pygame.draw.line(surf, c, (x, 0), (x, h - 1))

    # Warm accent stripe on sunlit side
    accent_s = pygame.Surface((3, h), pygame.SRCALPHA)
    accent_s.fill((*accent, 110))
    surf.blit(accent_s, (max(2, int(w * 0.14)), 0))

    rng = random.Random(seed * 7919 + w * 13 + h)

    # Vertical erosion striations
    for _ in range(6):
        gx = rng.randint(2, max(3, w - 3))
        col = (max(0, dark[0] - 15), max(0, dark[1] - 15), max(0, dark[2] - 15))
        pygame.draw.line(surf, col, (gx, 0), (gx, h - 1), 1)

    # Horizontal erosion cracks
    crack_step = 70
    ystart = rng.randint(15, crack_step)
    for cy in range(ystart, h - 8, crack_step):
        jit = rng.randint(-3, 3)
        y = cy + jit
        if glow_cracks:
            # Emissive lava vein: dark-orange core + pale gold highlight
            pygame.draw.line(surf, (255, 80, 32), (3, y), (w - 4, y + rng.randint(-1, 1)), 2)
            pygame.draw.line(surf, (255, 224, 144), (3, y), (w - 4, y + rng.randint(-1, 1)), 1)
        else:
            col = (max(0, dark[0] - 25), max(0, dark[1] - 25), max(0, dark[2] - 25))
            pygame.draw.line(surf, col, (3, y), (w - 4, y + rng.randint(-1, 1)), 1)

    # Natural patches (only for non-glow variants)
    if not glow_cracks:
        for _ in range(rng.randint(4, 6)):
            ex = rng.randint(4, max(5, w - 14))
            ey = rng.randint(15, max(20, h - 25))
            col = rng.choice(pal.get('patches', [(170, 95, 60), (150, 175, 120)]))
            s = pygame.Surface((14, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (*col, 100), s.get_rect())
            surf.blit(s, (ex, ey))

    return surf


def silhouette_blit(target, body, polygon, top_left, outline_col, shadow=True):
    w, h = body.get_size()
    if shadow:
        sh_surf = pygame.Surface((w + 8, h + 6), pygame.SRCALPHA)
        pygame.draw.polygon(sh_surf, (0, 0, 0, 110), [(p[0] + 4, p[1] + 3) for p in polygon])
        target.blit(sh_surf, (top_left[0] - 2, top_left[1] + 1))
    masked = body.copy()
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), polygon)
    masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    target.blit(masked, top_left)
    pygame.draw.polygon(target, outline_col,
                        [(p[0] + top_left[0], p[1] + top_left[1]) for p in polygon], 1)


# ── Canopy (pine-shape, recolorable) ─────────────────────────────────────────

def draw_canopy(surf, root_x, root_y, height, canopy_pal,
                lean=0, direction='up', layers=5, trunk_col=(60, 42, 28)):
    sign = -1 if direction == 'up' else 1
    tip_x = root_x + lean
    tip_y = root_y + sign * height
    pygame.draw.line(surf, trunk_col, (root_x, root_y), (tip_x, tip_y), 2)
    dk, mid, lt = canopy_pal
    for i in range(layers):
        t = i / max(1, layers - 1)
        layer_w = int(height * (0.55 - t * 0.40))
        if layer_w < 4:
            layer_w = 4
        pos_t = 0.30 + t * 0.70
        cx = int(root_x + (tip_x - root_x) * pos_t)
        cy = int(root_y + (tip_y - root_y) * pos_t)
        offset = int(height * 0.10 * (1 if i % 2 == 0 else -1))
        rect = pygame.Rect(cx - layer_w + offset, cy - 4, layer_w * 2, 8)
        pygame.draw.ellipse(surf, dk, rect.inflate(2, 2))
        pygame.draw.ellipse(surf, mid, rect)
        pygame.draw.ellipse(surf, lt, rect.inflate(-6, -4))


def draw_snag(surf, root_x, root_y, height, lean=0, direction='up'):
    """Charred dead-tree silhouette: bare twisted trunk with a few crooked
    branches. Used for Emberforge."""
    sign = -1 if direction == 'up' else 1
    tip_x = root_x + lean
    tip_y = root_y + sign * height
    pygame.draw.line(surf, (25, 18, 18), (root_x, root_y), (tip_x, tip_y), 3)
    # Crooked branches
    for i, frac in enumerate((0.35, 0.55, 0.75)):
        bx = int(root_x + (tip_x - root_x) * frac)
        by = int(root_y + (tip_y - root_y) * frac)
        ex = bx + (10 if i % 2 == 0 else -10)
        ey = by + sign * 6
        pygame.draw.line(surf, (25, 18, 18), (bx, by), (ex, ey), 2)
        pygame.draw.line(surf, (60, 30, 20), (ex, ey),
                         (ex + (4 if i % 2 == 0 else -4), ey + sign * 4), 1)


# ── Halo base (color-tunable) ────────────────────────────────────────────────

def draw_halo(surf, cx, base_y, width, color, base_alpha=110):
    layers = [(width * 4, 36, int(base_alpha * 1.00)),
              (width * 3, 22, int(base_alpha * 1.36)),
              (width * 2, 14, int(base_alpha * 1.82))]
    for w, h, a in layers:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*color, min(255, a)), s.get_rect())
        surf.blit(s, (cx - w // 2, base_y - h // 2 + 4))


# ── Silhouette polygons (reused across all three options) ────────────────────

def top_poly(pw):
    return [
        (0, 0), (pw, 0),
        (pw - 4, TOP_H - 50),
        (pw - 14, TOP_H - 22),
        (pw // 2 + 10, TOP_H - 5),
        (pw // 2 - 6, TOP_H),
        (pw // 2 - 18, TOP_H - 8),
        (16, TOP_H - 22),
        (4, TOP_H - 50),
    ]


def bot_poly(pw, bot_h):
    return [
        (pw // 2 - 8, 0),
        (pw // 2 + 12, 0),
        (pw - 18, 18),
        (pw - 6, 40),
        (pw - 4, 80),
        (pw, 130),
        (pw, bot_h),
        (0, bot_h),
        (0, 130),
        (8, 80),
        (14, 40),
        (24, 18),
    ]


# ── Option 1: Aurora Crystal ─────────────────────────────────────────────────

AURORA = dict(
    light=(200, 218, 255),
    mid=(107, 139, 224),
    dark=(42, 47, 110),
    accent=(155, 255, 240),
    patches=[(140, 200, 255), (180, 170, 255)],
)
AURORA_CANOPY = ((20, 50, 90), (80, 140, 200), (160, 220, 255))
AURORA_HALO = (184, 232, 255)
AURORA_OUTLINE = (180, 230, 255)


def draw_tip_gem(surf, tip_x, tip_y, direction='up'):
    """Faceted amethyst/quartz gem cluster with additive glow."""
    sign = -1 if direction == 'up' else 1
    # Glow halo behind gem
    glow = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(glow, (180, 240, 255, 90), (20, 20), 18)
    pygame.draw.circle(glow, (210, 250, 255, 140), (20, 20), 11)
    surf.blit(glow, (tip_x - 20, tip_y - 20))
    # Three overlapping faceted triangles
    facets = [
        ((tip_x - 6, tip_y), (tip_x - 2, tip_y + sign * 16), (tip_x + 2, tip_y)),
        ((tip_x, tip_y - sign * 2), (tip_x + 4, tip_y + sign * 14), (tip_x + 10, tip_y)),
        ((tip_x - 10, tip_y), (tip_x - 6, tip_y + sign * 12), (tip_x - 2, tip_y - sign * 1)),
    ]
    colors = [(120, 180, 240), (180, 230, 255), (220, 250, 255)]
    for pts, col in zip(facets, colors):
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, (60, 80, 150), pts, 1)


def render_aurora(surf, col_idx):
    cx = COL_W * col_idx + COL_W // 2
    pw = 90

    # Top pillar
    body = stone_body(pw, TOP_H, AURORA, seed=col_idx * 11 + 1)
    silhouette_blit(surf, body, top_poly(pw), (cx - pw // 2, 0), AURORA_OUTLINE)
    # Tip gem hanging down
    draw_tip_gem(surf, cx - 4, TOP_H - 4, direction='down')

    # Bottom pillar
    bot_h = GROUND_Y - BOT_TOP
    body2 = stone_body(pw, bot_h, AURORA, seed=col_idx * 11 + 2)
    silhouette_blit(surf, body2, bot_poly(pw, bot_h), (cx - pw // 2, BOT_TOP), AURORA_OUTLINE)
    # Crystal cluster at peak
    draw_tip_gem(surf, cx + 2, BOT_TOP + 4, direction='up')
    # Small slim pine at base to anchor scale
    draw_canopy(surf, cx - pw // 2 + 12, BOT_TOP + 70, 30,
                AURORA_CANOPY, lean=-4, direction='up', layers=4)
    # Cool cyan halo
    draw_halo(surf, cx, GROUND_Y - 4, pw, AURORA_HALO, base_alpha=120)


# ── Option 2: Sakura Cascade ────────────────────────────────────────────────

SAKURA_STONE = dict(
    light=(240, 216, 184),
    mid=(196, 154, 120),
    dark=(107, 70, 56),
    accent=(255, 230, 190),
    patches=[(170, 95, 60), (150, 175, 120), (110, 165, 90)],
)
SAKURA_CANOPY = ((184, 78, 128), (245, 145, 184), (255, 220, 235))
SAKURA_OUTLINE = (107, 70, 56)


def draw_petals(surf, cx, x_min, x_max, y_min, y_max, seed):
    rng = random.Random(seed)
    for _ in range(18):
        px = rng.randint(x_min, x_max)
        py = rng.randint(y_min, y_max)
        sz = rng.choice((3, 3, 4, 5))
        a = rng.randint(140, 220)
        color = rng.choice([(255, 200, 222), (255, 170, 205), (255, 235, 245)])
        s = pygame.Surface((sz * 2, sz), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*color, a), s.get_rect())
        rot = rng.randint(-30, 30)
        s = pygame.transform.rotate(s, rot)
        surf.blit(s, (px, py))


def render_sakura(surf, col_idx):
    cx = COL_W * col_idx + COL_W // 2
    pw = 90

    # Top pillar — sandstone body + hanging pink canopy at tip
    body = stone_body(pw, TOP_H, SAKURA_STONE, seed=col_idx * 17 + 1)
    silhouette_blit(surf, body, top_poly(pw), (cx - pw // 2, 0), SAKURA_OUTLINE)
    draw_canopy(surf, cx - 4, TOP_H - 4, 40, SAKURA_CANOPY,
                lean=-10, direction='down', layers=5)

    # Bottom pillar — big pink blossom canopy on the peak
    bot_h = GROUND_Y - BOT_TOP
    body2 = stone_body(pw, bot_h, SAKURA_STONE, seed=col_idx * 17 + 2)
    silhouette_blit(surf, body2, bot_poly(pw, bot_h), (cx - pw // 2, BOT_TOP), SAKURA_OUTLINE)
    draw_canopy(surf, cx + 2, BOT_TOP + 2, 80, SAKURA_CANOPY,
                lean=16, direction='up', layers=6)
    draw_canopy(surf, cx - pw // 2 + 10, BOT_TOP + 40, 32, SAKURA_CANOPY,
                lean=-4, direction='up', layers=4)

    # Halo — standard pale-pink tinted white
    draw_halo(surf, cx, GROUND_Y - 4, pw, (255, 230, 240), base_alpha=110)

    # Drifting petals in the gap and around canopy
    col_left = COL_W * col_idx + 10
    col_right = COL_W * (col_idx + 1) - 10
    draw_petals(surf, cx, col_left, col_right, 40, GROUND_Y - 20, seed=col_idx * 991)


# ── Option 3: Emberforge ────────────────────────────────────────────────────

EMBER = dict(
    light=(74, 58, 56),
    mid=(34, 24, 28),
    dark=(10, 6, 8),
    accent=(255, 177, 74),
)
EMBER_HALO = (255, 140, 60)
EMBER_OUTLINE = (255, 120, 40)


def render_ember(surf, col_idx):
    cx = COL_W * col_idx + COL_W // 2
    pw = 90

    # Top pillar
    body = stone_body(pw, TOP_H, EMBER, seed=col_idx * 23 + 1, glow_cracks=True)
    silhouette_blit(surf, body, top_poly(pw), (cx - pw // 2, 0), EMBER_OUTLINE)

    # Bottom pillar
    bot_h = GROUND_Y - BOT_TOP
    body2 = stone_body(pw, bot_h, EMBER, seed=col_idx * 23 + 2, glow_cracks=True)
    silhouette_blit(surf, body2, bot_poly(pw, bot_h), (cx - pw // 2, BOT_TOP), EMBER_OUTLINE)

    # Charred dead snag on the peak
    draw_snag(surf, cx + 2, BOT_TOP + 2, 62, lean=12, direction='up')

    # Amber glowing halo
    draw_halo(surf, cx, GROUND_Y - 4, pw, EMBER_HALO, base_alpha=170)


# ── Label ────────────────────────────────────────────────────────────────────

def label(surf, col_idx, text, font):
    cx = COL_W * col_idx + COL_W // 2
    box = font.render(text, True, (20, 20, 30))
    pad = 8
    bg = pygame.Surface((box.get_width() + pad * 2, box.get_height() + pad), pygame.SRCALPHA)
    bg.fill((255, 255, 255, 225))
    surf.blit(bg, (cx - bg.get_width() // 2, 16))
    surf.blit(box, (cx - box.get_width() // 2, 16 + pad // 2))


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    surf = pygame.Surface((W, H))
    paint_sky(surf)
    paint_mountains(surf)
    paint_ground(surf)

    font = pygame.font.SysFont("arial", 22, bold=True)

    render_aurora(surf, 0)
    render_sakura(surf, 1)
    render_ember(surf, 2)

    label(surf, 0, "1. Aurora Crystal", font)
    label(surf, 1, "2. Sakura Cascade", font)
    label(surf, 2, "3. Emberforge", font)

    out = "/home/user/Claude_test/docs/sketches/vivid_pillars.png"
    pygame.image.save(surf, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
