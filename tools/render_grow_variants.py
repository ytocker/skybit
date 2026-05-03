"""Five witch-hat-family mushroom variants — round 5.

Round 4 (commit 6b4e310) shipped a wacky-silhouette set; user picked
the witch-hat (tall conical Liberty-Cap) as the favourite style and
asked for 5 more in the same family.

Shared style across this round:
- Tall pointy conical cap (NOT a dome).
- Curled scalloped rim of half-circle bumps along the cap base.
- Slim elongated stem with a slight bulb at the bottom.
- Soft theme-coloured outer halo.
- Spots / pattern scattered DOWN the cone (4 each, varied per theme).

What changes per variant: cap palette (gradient), rim+halo tint, spot
shape (star / crescent / snowflake / ember / diamond), stem accents.

Each function has the same signature as `PowerUp._draw_mushroom`:

    fn(surf, cx, cy, pulse=0.0)

Imported by `tools/render_grow_gameplay.py`. Does NOT modify game code.
"""
import math
import pygame


SS = 3


# ── Helpers ────────────────────────────────────────────────────────────────
def _ss(w, h):
    return pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)


def _ss_blit(big, dst, x, y, w, h):
    dst.blit(pygame.transform.smoothscale(big, (w, h)), (x, y))


def _star(surf, cx, cy, r_out, r_in, color, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = rot + i * (math.pi / n)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    pygame.draw.polygon(surf, color, pts)


def _diamond(surf, cx, cy, w, h, color):
    pygame.draw.polygon(surf, color, [
        (cx, cy - h), (cx + w, cy), (cx, cy + h), (cx - w, cy),
    ])


def _snowflake(surf, cx, cy, r, color):
    for k in range(3):
        a = k * math.pi / 3
        dx = math.cos(a) * r
        dy = math.sin(a) * r
        pygame.draw.line(surf, color,
                         (cx - dx, cy - dy), (cx + dx, cy + dy), 1)
    pygame.draw.circle(surf, color, (cx, cy), 1)


def _draw_halo(surf, cx, cy, color_rgb, pulse_t=1.0,
               size=(40, 56), peak_y_off=0):
    w, h = size
    halo = pygame.Surface((w, h), pygame.SRCALPHA)
    hcx, hcy = w // 2, h // 2 + peak_y_off
    for r, a in ((22, int(28 + 16 * pulse_t)),
                 (17, int(50 + 30 * pulse_t)),
                 (13, int(80 + 40 * pulse_t))):
        pygame.draw.ellipse(halo, (*color_rgb, a),
                            pygame.Rect(hcx - r, hcy - r, r * 2, r * 2))
    surf.blit(halo, (cx - w // 2, cy - h // 2 + peak_y_off + 4))


def _draw_slim_stem(surf, cx, cy_top,
                    body=(250, 235, 215),
                    outline=(170, 145, 110),
                    hi=(255, 250, 230)):
    """Slim elongated witch-hat stem with a bulbed base.
    `cy_top` is where the cap sits on the stem (top edge)."""
    W = _ss(20, 22)
    pts = [
        (8 * SS,  0 * SS),
        (12 * SS, 0 * SS),
        (13 * SS, 12 * SS),
        (15 * SS, 18 * SS),
        (10 * SS, 21 * SS),
        ( 5 * SS, 18 * SS),
        ( 7 * SS, 12 * SS),
    ]
    pygame.draw.polygon(W, body, pts)
    pygame.draw.polygon(W, outline, pts, width=SS)
    pygame.draw.line(W, hi, (9 * SS, 2 * SS), (9 * SS, 18 * SS), SS)
    _ss_blit(W, surf, cx - 10, cy_top, 20, 22)


def _draw_witch_hat_cone(big, cap_w, cap_h,
                         outline, body, hi_stripe,
                         rim_count=5, rim_hi=None):
    """Draws the cone body + side highlight + scalloped rim onto `big`.
    Caller adds the spots / extras after."""
    cone_outline = [
        (cap_w // 2 * SS, 0),
        (int(cap_w * 0.86 * SS), int(cap_h * 0.78 * SS)),
        (int(cap_w * 0.95 * SS), int(cap_h * 0.92 * SS)),
        (int(cap_w * 0.05 * SS), int(cap_h * 0.92 * SS)),
        (int(cap_w * 0.14 * SS), int(cap_h * 0.78 * SS)),
    ]
    pygame.draw.polygon(big, outline, cone_outline)
    cone_body = [
        (cap_w // 2 * SS, 1 * SS),
        (int(cap_w * 0.82 * SS), int(cap_h * 0.78 * SS)),
        (int(cap_w * 0.91 * SS), int(cap_h * 0.90 * SS)),
        (int(cap_w * 0.09 * SS), int(cap_h * 0.90 * SS)),
        (int(cap_w * 0.18 * SS), int(cap_h * 0.78 * SS)),
    ]
    pygame.draw.polygon(big, body, cone_body)
    # Vertical highlight stripe on the left side
    pygame.draw.polygon(big, hi_stripe, [
        (cap_w // 2 * SS - 1 * SS,           1 * SS),
        (int(cap_w * 0.32 * SS),             int(cap_h * 0.55 * SS)),
        (int(cap_w * 0.22 * SS),             int(cap_h * 0.85 * SS)),
        (int(cap_w * 0.34 * SS),             int(cap_h * 0.85 * SS)),
        (int(cap_w * 0.42 * SS),             int(cap_h * 0.55 * SS)),
    ])
    # Curled scalloped rim
    rim_w = int(cap_w * 0.86 * SS)
    rim_x = int(cap_w * 0.07 * SS)
    curl_w = rim_w // rim_count
    rim_hi = rim_hi or hi_stripe
    for i in range(rim_count):
        center = (rim_x + i * curl_w + curl_w // 2,
                  int(cap_h * 0.93 * SS))
        pygame.draw.circle(big, body,    center, curl_w // 2)
        pygame.draw.circle(big, outline, center, curl_w // 2, SS)
        pygame.draw.circle(big, rim_hi,
                           (center[0] - curl_w // 5, center[1] - curl_w // 5),
                           max(1, curl_w // 4))


# Canonical cap dimensions for this round.
CAP_W = 22
CAP_H = 24


# Where on the supersampled cap to drop the 4 ornaments — fractions of
# (cap_w, cap_h) so each variant can pick its own ornament shape.
ORNAMENT_SLOTS = (
    (0.50, 0.18),
    (0.62, 0.42),
    (0.40, 0.62),
    (0.70, 0.72),
)


# ── V1 — STARGAZER (indigo + gold 5-point stars) ───────────────────────────
def draw_v1_stargazer(surf, cx, cy, pulse=0.0):
    """Deep indigo/violet cone cap with a soft cyan-violet halo, gold
    five-pointed stars scattered down the cone, ivory stem."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.3)
    _draw_halo(surf, cx, cy, (160, 140, 240), pulse_t)
    _draw_slim_stem(surf, cx, cy + 2)

    big = _ss(CAP_W, CAP_H + 4)
    _draw_witch_hat_cone(
        big, CAP_W, CAP_H,
        outline=( 30,  20,  70),
        body=(   60,  50, 150),
        hi_stripe=(120, 130, 220),
        rim_hi=(180, 190, 255),
    )

    # Tiny background sparkles within the cone (faint)
    for fx_frac, fy_frac in ((0.32, 0.30), (0.62, 0.55),
                             (0.50, 0.78), (0.70, 0.30)):
        fx = int(CAP_W * fx_frac * SS)
        fy = int(CAP_H * fy_frac * SS)
        pygame.draw.circle(big, (200, 200, 255, 200), (fx, fy), max(1, SS // 2))

    # Gold stars
    for fx_frac, fy_frac in ORNAMENT_SLOTS:
        fx = int(CAP_W * fx_frac * SS)
        fy = int(CAP_H * fy_frac * SS)
        _star(big, fx, fy, int(2.4 * SS), int(1.0 * SS), (180, 110, 30))
        _star(big, fx, fy, int(2.0 * SS), int(0.8 * SS), (255, 220,  80))
        pygame.draw.circle(big, (255, 250, 200),
                           (fx - SS // 2, fy - SS // 2), max(1, SS // 2))

    _ss_blit(big, surf, cx - CAP_W // 2, cy - CAP_H + 2, CAP_W, CAP_H + 4)


# ── V2 — FOREST (emerald cap, cream spots, mossy stem with vine) ───────────
def draw_v2_forest(surf, cx, cy, pulse=0.0):
    """Emerald-green cone cap with cream-butter spots, soft green halo,
    ivory stem with green moss tufts at the base + a curling vine."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.4)
    _draw_halo(surf, cx, cy, (130, 220, 140), pulse_t)
    _draw_slim_stem(surf, cx, cy + 2)

    # Vine wrapping the stem — drawn after stem so it overlays
    vine_col_dk = ( 60, 130,  60)
    vine_col_lt = (130, 200,  90)
    for k in range(5):
        t = k / 4
        ang = math.pi * t * 1.5
        vx = cx - 5 + int(math.sin(ang) * 5)
        vy = cy + 4 + k * 3
        pygame.draw.circle(surf, vine_col_dk, (vx, vy), 2)
        pygame.draw.circle(surf, vine_col_lt, (vx, vy), 1)
    # Tiny leaves at the stem base
    for lx, ly, dx in ((cx - 7, cy + 19, -3), (cx + 7, cy + 19, 3)):
        pygame.draw.polygon(surf, vine_col_dk, [
            (lx, ly), (lx + dx, ly - 4), (lx + dx * 2, ly - 1),
        ])
        pygame.draw.polygon(surf, vine_col_lt, [
            (lx + dx // 2, ly - 1), (lx + dx, ly - 3),
            (lx + int(dx * 1.5), ly - 1),
        ])

    big = _ss(CAP_W, CAP_H + 4)
    _draw_witch_hat_cone(
        big, CAP_W, CAP_H,
        outline=( 25,  70,  35),
        body=(   45, 150,  70),
        hi_stripe=(120, 220, 130),
        rim_hi=(180, 240, 200),
    )

    # Cream spots
    for fx_frac, fy_frac in ORNAMENT_SLOTS:
        fx = int(CAP_W * fx_frac * SS)
        fy = int(CAP_H * fy_frac * SS)
        pygame.draw.circle(big, (200, 180, 130), (fx, fy), int(2.0 * SS))
        pygame.draw.circle(big, (255, 240, 200), (fx, fy), int(1.6 * SS))
        pygame.draw.circle(big, (255, 255, 240),
                           (fx - SS // 2, fy - SS // 2), max(1, SS // 2))

    _ss_blit(big, surf, cx - CAP_W // 2, cy - CAP_H + 2, CAP_W, CAP_H + 4)


# ── V3 — SUNSET / EMBER (orange-yellow gradient cap, white spots, embers) ──
def draw_v3_sunset(surf, cx, cy, pulse=0.0):
    """Orange-to-yellow gradient cone cap, warm orange halo, white
    spots, tiny ember sparks rising from the cap."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.6)
    _draw_halo(surf, cx, cy, (255, 170,  80), pulse_t)
    _draw_slim_stem(surf, cx, cy + 2,
                    hi=(255, 240, 200))

    big = _ss(CAP_W, CAP_H + 4)

    # Outline cone (dark amber)
    cone_outline = [
        (CAP_W // 2 * SS, 0),
        (int(CAP_W * 0.86 * SS), int(CAP_H * 0.78 * SS)),
        (int(CAP_W * 0.95 * SS), int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.05 * SS), int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.14 * SS), int(CAP_H * 0.78 * SS)),
    ]
    pygame.draw.polygon(big, (140, 50, 20), cone_outline)

    # Build inset cone shape, then mask a vertical gradient onto it.
    cone_body_pts = [
        (CAP_W // 2 * SS, 1 * SS),
        (int(CAP_W * 0.82 * SS), int(CAP_H * 0.78 * SS)),
        (int(CAP_W * 0.91 * SS), int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.09 * SS), int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.18 * SS), int(CAP_H * 0.78 * SS)),
    ]
    cone_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(cone_mask, (255, 255, 255, 255), cone_body_pts)
    grad = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    h = CAP_H * SS
    for yy in range(h):
        t = yy / max(1, h - 1)
        if t < 0.5:
            u = t / 0.5
            col = (int(255), int(220 + (140 - 220) * u), int(80 + (40 - 80) * u))
        else:
            u = (t - 0.5) / 0.5
            col = (int(255 + (220 - 255) * u),
                   int(140 + ( 60 - 140) * u),
                   int( 40 + ( 30 -  40) * u))
        pygame.draw.line(grad, col, (0, yy), (big.get_width(), yy))
    grad.blit(cone_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(grad, (0, 0))

    # Side highlight + scalloped rim using helper colours
    pygame.draw.polygon(big, (255, 240, 160), [
        (CAP_W // 2 * SS - 1 * SS,           1 * SS),
        (int(CAP_W * 0.32 * SS),             int(CAP_H * 0.55 * SS)),
        (int(CAP_W * 0.22 * SS),             int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.34 * SS),             int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.42 * SS),             int(CAP_H * 0.55 * SS)),
    ])
    rim_w = int(CAP_W * 0.86 * SS)
    rim_x = int(CAP_W * 0.07 * SS)
    rim_count = 5
    curl_w = rim_w // rim_count
    for i in range(rim_count):
        center = (rim_x + i * curl_w + curl_w // 2,
                  int(CAP_H * 0.93 * SS))
        pygame.draw.circle(big, (235, 90, 40), center, curl_w // 2)
        pygame.draw.circle(big, (140, 50, 20), center, curl_w // 2, SS)
        pygame.draw.circle(big, (255, 200, 130),
                           (center[0] - curl_w // 5, center[1] - curl_w // 5),
                           max(1, curl_w // 4))

    # White spots
    for fx_frac, fy_frac in ORNAMENT_SLOTS:
        fx = int(CAP_W * fx_frac * SS)
        fy = int(CAP_H * fy_frac * SS)
        pygame.draw.circle(big, (255, 220, 200), (fx, fy), int(2.0 * SS))
        pygame.draw.circle(big, (255, 255, 255), (fx, fy), int(1.6 * SS))

    _ss_blit(big, surf, cx - CAP_W // 2, cy - CAP_H + 2, CAP_W, CAP_H + 4)

    # Rising ember sparks above the cap
    for i in range(3):
        phase = pulse * 1.7 + i * 1.6
        rise = phase % 2.0
        if rise < 1.4:
            ex = cx + (i - 1) * 5 + int(math.sin(phase * 1.2) * 4)
            ey = cy - CAP_H + 2 - int(rise * 6)
            a = int(255 * (1 - rise / 1.4))
            es = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(es, (255, 200, 80, a), (2, 2), 2)
            pygame.draw.circle(es, (255, 240, 200, a), (2, 2), 1)
            surf.blit(es, (ex - 2, ey - 2))


# ── V4 — FROST / ICE (pale ice-blue cap, snowflake spots, frost halo) ──────
def draw_v4_frost(surf, cx, cy, pulse=0.0):
    """Pale ice-blue cone cap, cool cyan halo, snowflake-shaped ornaments
    instead of dots, frosty pale stem with crystal flecks."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.2)
    _draw_halo(surf, cx, cy, (180, 230, 255), pulse_t)
    _draw_slim_stem(surf, cx, cy + 2,
                    body=(235, 245, 255),
                    outline=(140, 180, 220),
                    hi=(255, 255, 255))

    # Frost crystal flecks on stem
    for fx, fy in ((cx - 4, cy + 6), (cx + 5, cy + 11), (cx - 3, cy + 14)):
        pygame.draw.circle(surf, (200, 230, 255), (fx, fy), 1)

    big = _ss(CAP_W, CAP_H + 4)
    _draw_witch_hat_cone(
        big, CAP_W, CAP_H,
        outline=( 80, 130, 180),
        body=(  170, 215, 245),
        hi_stripe=(230, 245, 255),
        rim_hi=(255, 255, 255),
    )

    # Snowflake ornaments — 6-arm crystal spikes
    for fx_frac, fy_frac in ORNAMENT_SLOTS:
        fx = int(CAP_W * fx_frac * SS)
        fy = int(CAP_H * fy_frac * SS)
        # halo background
        pygame.draw.circle(big, (220, 240, 255), (fx, fy), int(2.4 * SS))
        # 6-spoke flake
        for k in range(3):
            a = k * math.pi / 3
            dx = int(math.cos(a) * 2.0 * SS)
            dy = int(math.sin(a) * 2.0 * SS)
            pygame.draw.line(big, (90, 140, 200),
                             (fx - dx, fy - dy), (fx + dx, fy + dy), SS)
        for k in range(3):
            a = k * math.pi / 3
            dx = int(math.cos(a) * 1.6 * SS)
            dy = int(math.sin(a) * 1.6 * SS)
            pygame.draw.line(big, (255, 255, 255),
                             (fx - dx, fy - dy), (fx + dx, fy + dy), max(1, SS - 1))
        pygame.draw.circle(big, (255, 255, 255), (fx, fy), max(1, SS - 1))

    _ss_blit(big, surf, cx - CAP_W // 2, cy - CAP_H + 2, CAP_W, CAP_H + 4)

    # Floating snowflake sparkle next to the cap
    for i, (dx, dy) in enumerate(((-13, -10), (12, -8), (8, -16))):
        phase = pulse * 1.0 + i * 1.7
        if math.sin(phase) > 0:
            sx = cx + dx
            sy = cy - CAP_H + 4 + dy + int(math.sin(phase) * -2)
            _snowflake(surf, sx, sy, 2, (220, 240, 255))


# ── V5 — JESTER (curled-tip striped cap with gold belt) ────────────────────
def draw_v5_jester(surf, cx, cy, pulse=0.0):
    """Multi-stripe (red/yellow/blue) witch-hat cap whose tip flops over
    to one side like a gnome cap. Slim stem with a gold-buckle belt at
    the middle. Fairy-tale jester vibe."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.5)
    _draw_halo(surf, cx, cy, (255, 180, 140), pulse_t)

    _draw_slim_stem(surf, cx, cy + 2)

    # Gold belt ring at mid-stem
    belt_y = cy + 10
    pygame.draw.rect(surf, (140,  90,  20),
                     pygame.Rect(cx - 6, belt_y, 12, 4))
    pygame.draw.rect(surf, (255, 220,  80),
                     pygame.Rect(cx - 5, belt_y + 1, 10, 2))
    # Buckle square
    pygame.draw.rect(surf, (255, 250, 200),
                     pygame.Rect(cx - 2, belt_y, 4, 4))
    pygame.draw.rect(surf, (140,  90,  20),
                     pygame.Rect(cx - 2, belt_y, 4, 4), width=1)

    # Cap — the tip is FLOPPED OVER. Build the main cone but truncate
    # the tip; then draw a separate flopped triangle off to the right
    # ending in a small gold bell.
    big = _ss(CAP_W + 8, CAP_H + 6)
    big_w = (CAP_W + 8) * SS

    # Truncated cone: replace top vertex with a horizontal cut at ~0.30
    truncate_y = int(CAP_H * 0.28 * SS)
    cut_left  = int(CAP_W * 0.36 * SS)
    cut_right = int(CAP_W * 0.64 * SS)
    cone_outline = [
        (cut_left + 2 * SS,                  truncate_y),
        (cut_right + 2 * SS,                 truncate_y),
        (int(CAP_W * 0.86 * SS) + 2 * SS,    int(CAP_H * 0.78 * SS)),
        (int(CAP_W * 0.95 * SS) + 2 * SS,    int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.05 * SS) + 2 * SS,    int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.14 * SS) + 2 * SS,    int(CAP_H * 0.78 * SS)),
    ]
    pygame.draw.polygon(big, (60, 30, 50), cone_outline)

    # Inset cone (the body)
    cone_body_pts = [
        (cut_left + 2 * SS,                  truncate_y + SS),
        (cut_right + 2 * SS,                 truncate_y + SS),
        (int(CAP_W * 0.82 * SS) + 2 * SS,    int(CAP_H * 0.78 * SS)),
        (int(CAP_W * 0.91 * SS) + 2 * SS,    int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.09 * SS) + 2 * SS,    int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.18 * SS) + 2 * SS,    int(CAP_H * 0.78 * SS)),
    ]
    # Stripes — 3 horizontal bands across the cone (red / yellow / blue).
    cone_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(cone_mask, (255, 255, 255, 255), cone_body_pts)
    bands = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    band_h = (int(CAP_H * 0.90 * SS) - truncate_y) // 3
    for i, col in enumerate(((220, 50, 60),
                             (255, 210, 80),
                             ( 70, 130, 220))):
        y0 = truncate_y + i * band_h
        y1 = truncate_y + (i + 1) * band_h
        pygame.draw.rect(bands, col, pygame.Rect(0, y0, big.get_width(), y1 - y0))
    bands.blit(cone_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(bands, (0, 0))

    # Side highlight stripe
    pygame.draw.polygon(big, (255, 240, 220, 140), [
        (cut_left + 4 * SS,                  truncate_y + SS),
        (int(CAP_W * 0.32 * SS) + 2 * SS,    int(CAP_H * 0.55 * SS)),
        (int(CAP_W * 0.22 * SS) + 2 * SS,    int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.34 * SS) + 2 * SS,    int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.42 * SS) + 2 * SS,    int(CAP_H * 0.55 * SS)),
    ])

    # Scalloped rim (alternating colours)
    rim_w = int(CAP_W * 0.86 * SS)
    rim_x = int(CAP_W * 0.07 * SS) + 2 * SS
    rim_count = 5
    curl_w = rim_w // rim_count
    rim_cols = ((220, 50, 60), (255, 210, 80), (70, 130, 220),
                (255, 210, 80), (220, 50, 60))
    for i in range(rim_count):
        center = (rim_x + i * curl_w + curl_w // 2,
                  int(CAP_H * 0.93 * SS))
        pygame.draw.circle(big, rim_cols[i],   center, curl_w // 2)
        pygame.draw.circle(big, ( 60, 30, 50), center, curl_w // 2, SS)
        pygame.draw.circle(big, (255, 250, 220),
                           (center[0] - curl_w // 5, center[1] - curl_w // 5),
                           max(1, curl_w // 4))

    # Flopped tip — a curled triangle off to the right, ending in a
    # tiny gold bell.
    bob = int(math.sin(pulse * 1.7) * SS)
    flop_root = (cut_right + 2 * SS, truncate_y + SS)
    flop_mid  = (cut_right + 5 * SS, truncate_y - 2 * SS + bob)
    flop_tip  = (cut_right + 9 * SS, truncate_y + 2 * SS + bob)
    flop_curl = (cut_right + 11 * SS, truncate_y + 5 * SS + bob)
    # outline
    pygame.draw.lines(big, (60, 30, 50), False,
                      [flop_root, flop_mid, flop_tip, flop_curl], SS * 2)
    # body
    pygame.draw.lines(big, (220, 50, 60), False,
                      [flop_root, flop_mid, flop_tip, flop_curl], SS)
    # gold bell at the tip
    bell_cx = flop_curl[0]
    bell_cy = flop_curl[1] + 2 * SS
    pygame.draw.circle(big, (140,  90,  20), (bell_cx, bell_cy), int(2.0 * SS))
    pygame.draw.circle(big, (255, 220,  80), (bell_cx, bell_cy), int(1.5 * SS))
    pygame.draw.circle(big, (255, 250, 200),
                       (bell_cx - SS // 2, bell_cy - SS // 2), max(1, SS // 2))

    _ss_blit(big, surf,
             cx - CAP_W // 2 - 2, cy - CAP_H + 2,
             CAP_W + 8, CAP_H + 6)


VARIANTS = {
    1: ("1 — stargazer", draw_v1_stargazer),
    2: ("2 — forest",    draw_v2_forest),
    3: ("3 — sunset",    draw_v3_sunset),
    4: ("4 — frost",     draw_v4_frost),
    5: ("5 — jester",    draw_v5_jester),
}
