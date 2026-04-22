"""
Render three Zhangjiajie-pillar design templates side-by-side for visual review.

Run:
    python tools/pillar_preview.py
Output:
    docs/screenshots/pillar_preview.png   (1200x720, three columns)

This script is standalone — it does NOT modify the game's draw.py / entities.py.
Once a template is chosen, that code path will be lifted into the game.
"""
import os, math, random, sys
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

# ── Day-biome palette (matches game/biome.py DAY keyframe) ───────────────────
SKY_TOP    = (40, 110, 200)
SKY_MID    = (90, 170, 230)
SKY_BOT    = (170, 220, 245)
HORIZON    = (255, 240, 200)
GROUND_T   = (80, 200, 80)
GROUND_M   = (40, 150, 40)
GROUND_B   = (60, 100, 50)

STONE_LT   = (225, 195, 155)
STONE_MID  = (175, 140, 105)
STONE_DK   = (95, 70, 55)
STONE_ACC  = (255, 220, 170)
RUST       = (170, 95, 60)
LICHEN     = (150, 175, 120)
MOSS       = (110, 165, 90)

PINE_DK    = (25, 70, 45)
PINE_MID   = (60, 130, 70)
PINE_LT    = (140, 210, 120)
TRUNK      = (60, 42, 28)

FOG        = (255, 255, 255)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# ── Background ───────────────────────────────────────────────────────────────

def paint_sky(surf):
    for y in range(H):
        t = y / (H - 1)
        if t < 0.45:
            c = lerp(SKY_TOP, SKY_MID, t / 0.45)
        else:
            c = lerp(SKY_MID, SKY_BOT, (t - 0.45) / 0.55)
        pygame.draw.line(surf, c, (0, y), (W - 1, y))
    # Horizon glow
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
    # A faint rear silhouette across the whole canvas
    pts = [(0, GROUND_Y)]
    for x in range(0, W + 1, 8):
        h = int(60 + math.sin(x * 0.012) * 26 + math.sin(x * 0.04) * 12)
        pts.append((x, GROUND_Y - h))
    pts.append((W, GROUND_Y))
    pygame.draw.polygon(surf, (90, 110, 150), pts)


# ── Stone body (cached vertical-shaded surface) ──────────────────────────────

def stone_body(w, h, seed=0):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        t = x / max(1, w - 1)
        if t < 0.18:
            c = lerp(STONE_MID, STONE_LT, (0.18 - t) / 0.18)
        elif t < 0.55:
            seg = (t - 0.18) / 0.37
            seg = seg * seg * (3 - 2 * seg)
            c = lerp(STONE_LT, STONE_MID, seg)
        else:
            seg = (t - 0.55) / 0.45
            seg = seg * seg * (3 - 2 * seg)
            c = lerp(STONE_MID, STONE_DK, seg)
        pygame.draw.line(surf, c, (x, 0), (x, h - 1))

    # Subtle warm accent stripe on the sunlit side
    accent = pygame.Surface((3, h), pygame.SRCALPHA)
    accent.fill((*STONE_ACC, 90))
    surf.blit(accent, (max(2, int(w * 0.14)), 0))

    rng = random.Random(seed * 7919 + w * 13 + h)
    # Vertical erosion striations
    for _ in range(6):
        gx = rng.randint(2, max(3, w - 3))
        col = (max(0, STONE_DK[0] - 15), max(0, STONE_DK[1] - 15), max(0, STONE_DK[2] - 15))
        pygame.draw.line(surf, col, (gx, 0), (gx, h - 1), 1)
    # Horizontal erosion cracks
    crack_step = 70
    ystart = rng.randint(15, crack_step)
    for cy in range(ystart, h - 8, crack_step):
        jit = rng.randint(-3, 3)
        col = (max(0, STONE_DK[0] - 25), max(0, STONE_DK[1] - 25), max(0, STONE_DK[2] - 25))
        pygame.draw.line(surf, col, (3, cy + jit), (w - 4, cy + jit + rng.randint(-1, 1)), 1)
    # Rust + lichen patches
    for _ in range(rng.randint(4, 6)):
        ex = rng.randint(4, max(5, w - 14))
        ey = rng.randint(15, max(20, h - 25))
        col = rng.choice([RUST, LICHEN, MOSS])
        s = pygame.Surface((14, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*col, 100), s.get_rect())
        surf.blit(s, (ex, ey))
    return surf


def silhouette_blit(target, body, polygon, top_left, shadow=True):
    """Mask `body` to `polygon` (local coords) and blit to `target` at top_left,
    optionally drawing a soft drop shadow first."""
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
    # Reinforce the silhouette outline
    pygame.draw.polygon(target, STONE_DK,
                        [(p[0] + top_left[0], p[1] + top_left[1]) for p in polygon], 1)


# ── Wuling pine ──────────────────────────────────────────────────────────────

def draw_pine(surf, root_x, root_y, height, lean=0, direction='up', layers=5):
    """Stylised Wuling pine — narrow trunk + horizontal peacock-tail canopy.
    direction='up' grows upward from root_y, 'down' grows downward."""
    sign = -1 if direction == 'up' else 1
    tip_x = root_x + lean
    tip_y = root_y + sign * height
    # Trunk
    pygame.draw.line(surf, TRUNK, (root_x, root_y), (tip_x, tip_y), 2)
    # Layered canopy: each layer is a horizontal ellipse, narrowing toward the tip
    for i in range(layers):
        t = i / max(1, layers - 1)
        # Asymmetric peacock-tail — wider on alternating sides
        layer_w = int(height * (0.55 - t * 0.40))
        if layer_w < 4:
            layer_w = 4
        # Position along the trunk, biased toward the tip
        pos_t = 0.30 + t * 0.70
        cx = int(root_x + (tip_x - root_x) * pos_t)
        cy = int(root_y + (tip_y - root_y) * pos_t)
        offset = int(height * 0.10 * (1 if i % 2 == 0 else -1))
        rect = pygame.Rect(cx - layer_w + offset, cy - 4, layer_w * 2, 8)
        pygame.draw.ellipse(surf, PINE_DK, rect.inflate(2, 2))
        pygame.draw.ellipse(surf, PINE_MID, rect)
        pygame.draw.ellipse(surf, PINE_LT, rect.inflate(-6, -4))


# ── Misty base ───────────────────────────────────────────────────────────────

def draw_mist(surf, cx, base_y, width):
    layers = [(width * 4, 36, 110), (width * 3, 22, 150), (width * 2, 14, 200)]
    for w, h, a in layers:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*FOG, a), s.get_rect())
        surf.blit(s, (cx - w // 2, base_y - h // 2 + 4))


# ── Templates ────────────────────────────────────────────────────────────────

PILLAR_W = 90  # generous, lets us draw irregular outlines


def template_A(surf, col_idx, label_font):
    """A — SPIRE: tall, narrowing, single sharp peak, one dramatic pine."""
    cx = COL_W * col_idx + COL_W // 2
    pw = PILLAR_W

    # Top (hanging) pillar — tapered toward its bottom tip
    body = stone_body(pw, TOP_H, seed=col_idx * 11 + 1)
    poly = [
        (0, 0), (pw, 0),
        (pw - 4, TOP_H - 50),
        (pw - 14, TOP_H - 22),
        (pw // 2 + 10, TOP_H - 5),
        (pw // 2 - 6, TOP_H),
        (pw // 2 - 18, TOP_H - 8),
        (16, TOP_H - 22),
        (4, TOP_H - 50),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, 0))
    # Hanging pine clinging to the tip
    tip = (cx - 4, TOP_H - 4)
    draw_pine(surf, tip[0], tip[1], 38, lean=-12, direction='down', layers=4)

    # Bottom pillar — tapers to a single sharp peak
    bot_h = GROUND_Y - BOT_TOP
    body2 = stone_body(pw, bot_h, seed=col_idx * 11 + 2)
    poly2 = [
        (pw // 2 - 8, 0),         # peak left
        (pw // 2 + 12, 0),        # peak right (asymmetric)
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
    silhouette_blit(surf, body2, poly2, (cx - pw // 2, BOT_TOP))
    # Single dominant Wuling pine on the peak
    peak_x = cx + 2
    peak_y = BOT_TOP + 2
    draw_pine(surf, peak_x, peak_y, 78, lean=18, direction='up', layers=6)
    # A smaller secondary pine on a side ledge
    draw_pine(surf, cx - pw // 2 + 8, BOT_TOP + 38, 32, lean=-6, direction='up', layers=4)
    # Misty base
    draw_mist(surf, cx, GROUND_Y - 4, pw)
    # Label
    _label(surf, "A — Slender Spire", col_idx, label_font)


def template_B(surf, col_idx, label_font):
    """B — TWIN CRAG: top splits into two uneven rocky peaks, pine on each."""
    cx = COL_W * col_idx + COL_W // 2
    pw = PILLAR_W

    # Top pillar — bottom splits into two downward fangs
    body = stone_body(pw, TOP_H, seed=col_idx * 17 + 3)
    poly = [
        (0, 0), (pw, 0),
        (pw - 5, TOP_H - 70),
        (pw - 14, TOP_H - 35),
        (pw // 2 + 18, TOP_H - 10),
        (pw // 2 + 14, TOP_H),       # right fang tip
        (pw // 2 + 4,  TOP_H - 20),
        (pw // 2 - 6,  TOP_H - 28),
        (pw // 2 - 16, TOP_H - 8),
        (pw // 2 - 22, TOP_H - 4),   # left fang tip (longer)
        (pw // 2 - 30, TOP_H - 20),
        (16, TOP_H - 35),
        (5, TOP_H - 70),
    ]
    silhouette_blit(surf, body, poly, (cx - pw // 2, 0))
    # Hanging vines from the bigger fang
    for _, dx in enumerate((-26, -22, -18)):
        x0 = cx + dx
        for i in range(18):
            yy = TOP_H + i
            jitter = int(math.sin(i * 0.5 + dx) * 1.2)
            col = lerp(PINE_DK, PINE_MID, i / 18)
            pygame.draw.line(surf, col, (x0 + jitter, yy), (x0 + jitter, yy + 1), 1)

    # Bottom pillar — TWIN PEAKS (left taller than right)
    bot_h = GROUND_Y - BOT_TOP
    body2 = stone_body(pw, bot_h, seed=col_idx * 17 + 4)
    poly2 = [
        (pw // 2 - 26, 6),   # left peak tip (taller)
        (pw // 2 - 18, 0),
        (pw // 2 - 8,  4),
        (pw // 2 - 2,  22),  # cleft bottom
        (pw // 2 + 6,  18),
        (pw // 2 + 18, 14),
        (pw // 2 + 26, 22),  # right peak tip (shorter)
        (pw // 2 + 32, 30),
        (pw - 6, 50),
        (pw, 90),
        (pw, bot_h),
        (0, bot_h),
        (0, 90),
        (6, 50),
        (pw // 2 - 30, 24),
    ]
    silhouette_blit(surf, body2, poly2, (cx - pw // 2, BOT_TOP))
    # Pine on each peak
    draw_pine(surf, cx - 26, BOT_TOP + 8, 60, lean=-14, direction='up', layers=5)
    draw_pine(surf, cx + 26, BOT_TOP + 22, 44, lean=10, direction='up', layers=4)
    # Small shrub in the cleft
    pygame.draw.ellipse(surf, PINE_DK, (cx - 8, BOT_TOP + 16, 18, 8))
    pygame.draw.ellipse(surf, PINE_MID, (cx - 6, BOT_TOP + 17, 14, 6))
    # Misty base
    draw_mist(surf, cx, GROUND_Y - 4, pw)
    _label(surf, "B — Twin-Peak Crag", col_idx, label_font)


def template_C(surf, col_idx, label_font):
    """C — FORESTED MESA: pillar widens at the top into an irregular plateau
    crowded with pines; hanging moss cascades over the edge."""
    cx = COL_W * col_idx + COL_W // 2
    pw = PILLAR_W
    plate_w = pw + 30  # the plateau juts outward

    # Top pillar — bottom flares into a wide bumpy ledge
    body = stone_body(plate_w, TOP_H, seed=col_idx * 23 + 5)
    poly = [
        (15, 0), (plate_w - 15, 0),
        (plate_w - 12, TOP_H - 60),
        (plate_w - 4,  TOP_H - 24),
        (plate_w,      TOP_H - 8),
        (plate_w - 14, TOP_H),
        (plate_w // 2 + 14, TOP_H - 6),
        (plate_w // 2 - 14, TOP_H - 4),
        (14, TOP_H),
        (0,  TOP_H - 8),
        (4,  TOP_H - 24),
        (12, TOP_H - 60),
    ]
    silhouette_blit(surf, body, poly, (cx - plate_w // 2, 0))
    # Cascading moss / vines from the ledge edge
    for dx in range(-plate_w // 2 + 6, plate_w // 2 - 4, 8):
        x0 = cx + dx
        h = random.Random(col_idx * 31 + dx).randint(14, 28)
        for i in range(h):
            yy = TOP_H + i
            jitter = int(math.sin(i * 0.45 + dx * 0.1) * 1)
            col = lerp(PINE_DK, MOSS, i / h)
            pygame.draw.line(surf, col, (x0 + jitter, yy), (x0 + jitter, yy + 1), 1)
        # Bulb at the tip
        pygame.draw.circle(surf, PINE_MID, (x0, TOP_H + h), 3)

    # Bottom pillar — narrow trunk that flares to a wide forested plateau
    bot_h = GROUND_Y - BOT_TOP
    body2 = stone_body(plate_w, bot_h, seed=col_idx * 23 + 6)
    poly2 = [
        (14, 8), (plate_w // 2 - 16, 0),
        (plate_w // 2 + 14, 4),
        (plate_w - 14, 0),
        (plate_w, 18),
        (plate_w - 6, 36),
        (plate_w - 20, 58),
        (plate_w - 14, 90),
        (plate_w - 14, bot_h),
        (14, bot_h),
        (14, 90),
        (20, 58),
        (6, 36),
        (0, 18),
    ]
    silhouette_blit(surf, body2, poly2, (cx - plate_w // 2, BOT_TOP))
    # Multiple narrow conifers on the plateau
    plateau_y = BOT_TOP + 6
    for dx, h, lean in (
        (-26, 50, -6),
        (-10, 64, -2),
        (8,   58,  4),
        (24,  46,  8),
    ):
        draw_pine(surf, cx + dx, plateau_y, h, lean=lean, direction='up', layers=4)
    # Low shrubs along the plateau edge
    for dx in (-32, 30):
        pygame.draw.ellipse(surf, PINE_DK, (cx + dx - 8, plateau_y - 4, 18, 9))
        pygame.draw.ellipse(surf, PINE_MID, (cx + dx - 6, plateau_y - 4, 14, 7))
    draw_mist(surf, cx, GROUND_Y - 4, plate_w)
    _label(surf, "C — Forested Mesa", col_idx, label_font)


def _label(surf, text, col_idx, font):
    cx = COL_W * col_idx + COL_W // 2
    box = font.render(text, True, (20, 20, 30))
    pad = 8
    bg = pygame.Surface((box.get_width() + pad * 2, box.get_height() + pad), pygame.SRCALPHA)
    bg.fill((255, 255, 255, 220))
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
    template_A(surf, 0, font)
    template_B(surf, 1, font)
    template_C(surf, 2, font)

    out = "/home/user/Claude_test/docs/screenshots/pillar_preview.png"
    pygame.image.save(surf, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
