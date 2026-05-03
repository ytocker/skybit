"""Five red-top witch-hat variants — round 6.

User picked the pink-red witch-hat from round 4 (commit 6b4e310 — the
Liberty-Cap silhouette) and asked for "a few variants around that
style with red top." Round 5 (commit f3656ca) explored the same
silhouette in 5 different hues; this round narrows back to RED but
pushes the variation through tone, finish, and ornament.

Shared style: tall pointy conical cap, scalloped curled rim, slim
elongated bulbed stem, soft halo, 4 ornaments scattered down the cone.

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


CAP_W = 22
CAP_H = 24

# Cone outline / body / highlight polygon vertex helpers — shared by all
# variants so the silhouette stays identical.
def _cone_outline_pts():
    return [
        (CAP_W // 2 * SS, 0),
        (int(CAP_W * 0.86 * SS), int(CAP_H * 0.78 * SS)),
        (int(CAP_W * 0.95 * SS), int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.05 * SS), int(CAP_H * 0.92 * SS)),
        (int(CAP_W * 0.14 * SS), int(CAP_H * 0.78 * SS)),
    ]

def _cone_body_pts():
    return [
        (CAP_W // 2 * SS, 1 * SS),
        (int(CAP_W * 0.82 * SS), int(CAP_H * 0.78 * SS)),
        (int(CAP_W * 0.91 * SS), int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.09 * SS), int(CAP_H * 0.90 * SS)),
        (int(CAP_W * 0.18 * SS), int(CAP_H * 0.78 * SS)),
    ]

def _cone_hi_pts():
    return [
        (CAP_W // 2 * SS - 1 * SS,           1 * SS),
        (int(CAP_W * 0.32 * SS),             int(CAP_H * 0.55 * SS)),
        (int(CAP_W * 0.22 * SS),             int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.34 * SS),             int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.42 * SS),             int(CAP_H * 0.55 * SS)),
    ]


def _draw_cone_solid(big, outline, body, hi_stripe, rim_hi,
                     rim_count=5, rim_outline=None,
                     rim_body=None):
    """Standard solid-colour cone + rim. `rim_body` defaults to `body`,
    `rim_outline` defaults to `outline` so the rim matches the cone."""
    rim_body    = rim_body    or body
    rim_outline = rim_outline or outline
    pygame.draw.polygon(big, outline, _cone_outline_pts())
    pygame.draw.polygon(big, body,    _cone_body_pts())
    pygame.draw.polygon(big, hi_stripe, _cone_hi_pts())
    rim_w = int(CAP_W * 0.86 * SS)
    rim_x = int(CAP_W * 0.07 * SS)
    curl_w = rim_w // rim_count
    for i in range(rim_count):
        center = (rim_x + i * curl_w + curl_w // 2,
                  int(CAP_H * 0.93 * SS))
        pygame.draw.circle(big, rim_body,    center, curl_w // 2)
        pygame.draw.circle(big, rim_outline, center, curl_w // 2, SS)
        pygame.draw.circle(big, rim_hi,
                           (center[0] - curl_w // 5, center[1] - curl_w // 5),
                           max(1, curl_w // 4))


ORNAMENT_SLOTS = (
    (0.50, 0.18),
    (0.62, 0.42),
    (0.40, 0.62),
    (0.70, 0.72),
)


def _white_spot(big, fx_frac, fy_frac, r=2.0, halo=(220, 200, 210)):
    fx = int(CAP_W * fx_frac * SS)
    fy = int(CAP_H * fy_frac * SS)
    pygame.draw.circle(big, halo, (fx, fy), int((r + 0.4) * SS))
    pygame.draw.circle(big, (255, 255, 255), (fx, fy), int(r * SS))


# ── V1 — CLASSIC CRIMSON (Mario-red witch-hat) ─────────────────────────────
def draw_v1_classic(surf, cx, cy, pulse=0.0):
    """Saturated Mario red cap, white spots, soft pink halo, ivory stem.
    The most direct 'witch-hat-shaped Mario mushroom.'"""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.4)
    _draw_halo(surf, cx, cy, (255, 130, 130), pulse_t)
    _draw_slim_stem(surf, cx, cy + 2)

    big = _ss(CAP_W, CAP_H + 4)
    _draw_cone_solid(
        big,
        outline=( 130,  20,  30),
        body=(   220,  40,  45),
        hi_stripe=(255, 100,  90),
        rim_hi=(255, 200, 180),
    )
    for fx, fy in ORNAMENT_SLOTS:
        _white_spot(big, fx, fy, r=2.0)
    _ss_blit(big, surf, cx - CAP_W // 2, cy - CAP_H + 2, CAP_W, CAP_H + 4)


# ── V2 — ROYAL CRIMSON (deep red + gold stars + gold rim) ──────────────────
def draw_v2_royal(surf, cx, cy, pulse=0.0):
    """Deep crimson cone, gold 5-point stars instead of spots, gold-trim
    scalloped rim. Royal/regal feel."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.3)
    _draw_halo(surf, cx, cy, (220, 100, 130), pulse_t)
    _draw_slim_stem(surf, cx, cy + 2)

    big = _ss(CAP_W, CAP_H + 4)

    # Cone with deep crimson palette. Manually draw so the rim can use
    # gold instead of inheriting the cone colour.
    pygame.draw.polygon(big, ( 90,  10,  30), _cone_outline_pts())
    pygame.draw.polygon(big, (160,  25,  50), _cone_body_pts())
    pygame.draw.polygon(big, (210,  60,  80), _cone_hi_pts())

    # Gold scalloped rim
    rim_w = int(CAP_W * 0.86 * SS)
    rim_x = int(CAP_W * 0.07 * SS)
    rim_count = 5
    curl_w = rim_w // rim_count
    for i in range(rim_count):
        center = (rim_x + i * curl_w + curl_w // 2,
                  int(CAP_H * 0.93 * SS))
        pygame.draw.circle(big, (140,  90,  20), center, curl_w // 2)
        pygame.draw.circle(big, (255, 220,  80), center, max(1, curl_w // 2 - SS))
        pygame.draw.circle(big, (255, 250, 200),
                           (center[0] - curl_w // 5, center[1] - curl_w // 5),
                           max(1, curl_w // 4))

    # Gold stars
    for fx_frac, fy_frac in ORNAMENT_SLOTS:
        fx = int(CAP_W * fx_frac * SS)
        fy = int(CAP_H * fy_frac * SS)
        _star(big, fx, fy, int(2.4 * SS), int(1.0 * SS), (140,  85,  20))
        _star(big, fx, fy, int(2.0 * SS), int(0.8 * SS), (255, 220,  80))
        pygame.draw.circle(big, (255, 250, 200),
                           (fx - SS // 2, fy - SS // 2), max(1, SS // 2))

    _ss_blit(big, surf, cx - CAP_W // 2, cy - CAP_H + 2, CAP_W, CAP_H + 4)


# ── V3 — CHERRY CANDY (glossy bright red + diagonal sheen + white spots) ───
def draw_v3_candy(surf, cx, cy, pulse=0.0):
    """Bright candy-cherry red cap with a glossy diagonal sheen swatch
    suggesting a polished candy finish, white spots, pink halo."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.5)
    _draw_halo(surf, cx, cy, (255, 150, 170), pulse_t)
    _draw_slim_stem(surf, cx, cy + 2)

    big = _ss(CAP_W, CAP_H + 4)
    _draw_cone_solid(
        big,
        outline=( 140,  20,  40),
        body=(   240,  60,  80),
        hi_stripe=(255, 130, 150),
        rim_hi=(255, 220, 220),
    )

    # Glossy diagonal candy sheen — bright white wedge across the cap.
    cone_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(cone_mask, (255, 255, 255, 255), _cone_body_pts())
    sheen = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(sheen, (255, 255, 255, 200), [
        (int(CAP_W * 0.40 * SS), int(CAP_H * 0.10 * SS)),
        (int(CAP_W * 0.50 * SS), int(CAP_H * 0.10 * SS)),
        (int(CAP_W * 0.30 * SS), int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.22 * SS), int(CAP_H * 0.85 * SS)),
    ])
    pygame.draw.polygon(sheen, (255, 255, 255, 120), [
        (int(CAP_W * 0.55 * SS), int(CAP_H * 0.25 * SS)),
        (int(CAP_W * 0.60 * SS), int(CAP_H * 0.25 * SS)),
        (int(CAP_W * 0.45 * SS), int(CAP_H * 0.85 * SS)),
        (int(CAP_W * 0.41 * SS), int(CAP_H * 0.85 * SS)),
    ])
    sheen.blit(cone_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    # White spots
    for fx, fy in ORNAMENT_SLOTS:
        _white_spot(big, fx, fy, r=2.0, halo=(255, 200, 210))

    _ss_blit(big, surf, cx - CAP_W // 2, cy - CAP_H + 2, CAP_W, CAP_H + 4)


# ── V4 — FIERY RED (hot gradient + ember sparks) ──────────────────────────
def draw_v4_fiery(surf, cx, cy, pulse=0.0):
    """Hot-red→deep-red vertical gradient cone with white spots, intense
    orange-red halo, and ember sparks rising from the cap. Reads as
    glowing/on-fire while still clearly red."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 2.0)
    _draw_halo(surf, cx, cy, (255, 130,  80), pulse_t)
    _draw_slim_stem(surf, cx, cy + 2,
                    hi=(255, 240, 210))

    big = _ss(CAP_W, CAP_H + 4)

    # Outline
    pygame.draw.polygon(big, (110, 15, 20), _cone_outline_pts())

    # Build cone body via vertical gradient masked to the cone polygon.
    cone_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(cone_mask, (255, 255, 255, 255), _cone_body_pts())
    grad = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    h = CAP_H * SS
    for yy in range(h):
        t = yy / max(1, h - 1)
        if t < 0.45:
            u = t / 0.45
            col = (int(255), int(140 + ( 70 - 140) * u), int(60 + (40 - 60) * u))
        else:
            u = (t - 0.45) / 0.55
            col = (int(255 + (190 - 255) * u),
                   int( 70 + ( 25 -  70) * u),
                   int( 40 + ( 20 -  40) * u))
        pygame.draw.line(grad, col, (0, yy), (big.get_width(), yy))
    grad.blit(cone_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(grad, (0, 0))

    # Highlight stripe
    pygame.draw.polygon(big, (255, 200, 130), _cone_hi_pts())

    # Rim
    rim_w = int(CAP_W * 0.86 * SS)
    rim_x = int(CAP_W * 0.07 * SS)
    rim_count = 5
    curl_w = rim_w // rim_count
    for i in range(rim_count):
        center = (rim_x + i * curl_w + curl_w // 2,
                  int(CAP_H * 0.93 * SS))
        pygame.draw.circle(big, (220,  40,  30), center, curl_w // 2)
        pygame.draw.circle(big, (110,  15,  20), center, curl_w // 2, SS)
        pygame.draw.circle(big, (255, 200, 130),
                           (center[0] - curl_w // 5, center[1] - curl_w // 5),
                           max(1, curl_w // 4))

    # White spots
    for fx, fy in ORNAMENT_SLOTS:
        _white_spot(big, fx, fy, r=2.0, halo=(255, 220, 200))

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


# ── V5 — VELVET MAROON (deep wine + cream spots + soft sheen) ──────────────
def draw_v5_velvet(surf, cx, cy, pulse=0.0):
    """Deep wine/maroon cone with cream-butter spots — elegant,
    velvet-textured tone. Soft warm halo. Dark cap, light spots."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.2)
    _draw_halo(surf, cx, cy, (180,  90, 110), pulse_t)
    _draw_slim_stem(surf, cx, cy + 2,
                    body=(245, 230, 200),
                    outline=(150, 120,  90))

    big = _ss(CAP_W, CAP_H + 4)
    _draw_cone_solid(
        big,
        outline=( 60,  15,  25),
        body=(   125,  30,  45),
        hi_stripe=(180,  60,  75),
        rim_hi=(220, 120, 130),
    )

    # Subtle velvet inner sheen — diffuse highlight blob near the top.
    cone_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(cone_mask, (255, 255, 255, 255), _cone_body_pts())
    sheen = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (220, 130, 150, 130),
                        pygame.Rect(int(CAP_W * 0.34 * SS),
                                    int(CAP_H * 0.18 * SS),
                                    int(CAP_W * 0.20 * SS),
                                    int(CAP_H * 0.40 * SS)))
    sheen.blit(cone_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    # Cream-butter spots (NOT white — to push the elegance)
    for fx_frac, fy_frac in ORNAMENT_SLOTS:
        fx = int(CAP_W * fx_frac * SS)
        fy = int(CAP_H * fy_frac * SS)
        pygame.draw.circle(big, (195, 165, 110), (fx, fy), int(2.4 * SS))
        pygame.draw.circle(big, (255, 235, 175), (fx, fy), int(1.9 * SS))
        pygame.draw.circle(big, (255, 250, 220),
                           (fx - SS // 2, fy - SS // 2), max(1, SS // 2))

    _ss_blit(big, surf, cx - CAP_W // 2, cy - CAP_H + 2, CAP_W, CAP_H + 4)


VARIANTS = {
    1: ("1 — classic",  draw_v1_classic),
    2: ("2 — royal",    draw_v2_royal),
    3: ("3 — candy",    draw_v3_candy),
    4: ("4 — fiery",    draw_v4_fiery),
    5: ("5 — velvet",   draw_v5_velvet),
}
