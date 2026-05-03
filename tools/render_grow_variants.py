"""Five VELVET-family witch-hat variants — round 7, hi-res.

User picked the velvet variant from round 6 (commit 6412b97) and
requested:
  - smooth, gradual background-halo gradient (no stepped rings)
  - higher resolution icon
  - 5 variants of the velvet style

Changes vs. round 6:
  - SS bumped 3 → 5 for crisper supersampled curves at the same draw size.
  - `_draw_smooth_halo` replaces the 3-stamp halo with ~60 concentric
    circles in a quadratic falloff, producing a continuous radial
    gradient with no visible banding.
  - All 5 variants share the wine/maroon velvet palette but vary one
    feature each: tone, sheen, rim trim, ornament colour, glossiness.

Each function has the same signature as `PowerUp._draw_mushroom`:

    fn(surf, cx, cy, pulse=0.0)

Imported by `tools/render_grow_gameplay.py`. Does NOT modify game code.
"""
import math
import pygame


SS = 5  # ↑ from 3 — higher resolution for the icon's curves and fine details


# ── Helpers ────────────────────────────────────────────────────────────────
def _ss(w, h):
    return pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)


def _ss_blit(big, dst, x, y, w, h):
    dst.blit(pygame.transform.smoothscale(big, (w, h)), (x, y))


def _draw_smooth_halo(surf, cx, cy, color_rgb, radius=27, max_alpha=180,
                      falloff=2.2, steps=60, peak_y_off=-2):
    """Smooth radial halo: ~60 concentric circles with a quadratic
    alpha falloff, producing a continuous gradient with no banding.

    `falloff` shapes the decay — higher = tighter centre. 2.2 gives a
    soft glow that fades naturally to the background.
    """
    w = radius * 2 + 4
    halo = pygame.Surface((w, w), pygame.SRCALPHA)
    hcx = hcy = w // 2
    for i in range(steps):
        # i=0 → outer (alpha=0), i=steps-1 → inner (alpha=max).
        # Drawing largest first so smaller (higher-alpha) circles
        # naturally overwrite the inner part of larger ones.
        r = max(0, radius - (i * radius) // steps)
        if r <= 0:
            break
        t = i / max(1, steps - 1)
        a = int(max_alpha * (t ** falloff))
        if a > 0:
            pygame.draw.circle(halo, (*color_rgb, a), (hcx, hcy), r)
    surf.blit(halo, (cx - hcx, cy - hcy + peak_y_off))


def _draw_slim_stem(surf, cx, cy_top,
                    body=(245, 230, 200),
                    outline=(150, 120,  90),
                    hi=(255, 250, 230)):
    """Slim elongated witch-hat stem with a bulbed base. Drawn
    supersampled for clean edges."""
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


def _draw_cone(big, outline, body, hi_stripe, rim_body, rim_outline, rim_hi,
               rim_count=5):
    """Outline + body + side highlight + scalloped curled rim, all on `big`."""
    pygame.draw.polygon(big, outline,   _cone_outline_pts())
    pygame.draw.polygon(big, body,      _cone_body_pts())
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


def _cone_mask():
    m = _ss(CAP_W, CAP_H + 4)
    pygame.draw.polygon(m, (255, 255, 255, 255), _cone_body_pts())
    return m


ORNAMENT_SLOTS = (
    (0.50, 0.18),
    (0.62, 0.42),
    (0.40, 0.62),
    (0.70, 0.72),
)


def _ornament(big, fx_frac, fy_frac, body, halo, hi=(255, 250, 220),
              r_body=2.0, r_halo_extra=0.4):
    fx = int(CAP_W * fx_frac * SS)
    fy = int(CAP_H * fy_frac * SS)
    pygame.draw.circle(big, halo, (fx, fy), int((r_body + r_halo_extra) * SS))
    pygame.draw.circle(big, body, (fx, fy), int(r_body * SS))
    pygame.draw.circle(big, hi,
                       (fx - SS // 2, fy - SS // 2), max(1, SS // 2))


# Velvet base palette — shared by all 5.
VELVET_OUTLINE = ( 60,  15,  25)
VELVET_BODY    = (125,  30,  45)
VELVET_HI      = (180,  60,  75)
VELVET_RIM_HI  = (220, 120, 130)


# ── V1 — VELVET REFINED (smooth halo + hi-res, the cleaned-up base) ────────
def draw_v1_velvet_refined(surf, cx, cy, pulse=0.0):
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.2)
    _draw_smooth_halo(surf, cx, cy, (180,  90, 110), radius=27,
                      max_alpha=int(155 + 25 * pulse_t))
    _draw_slim_stem(surf, cx, cy + 2)

    big = _ss(CAP_W, CAP_H + 4)
    _draw_cone(big,
               outline=VELVET_OUTLINE,
               body=VELVET_BODY,
               hi_stripe=VELVET_HI,
               rim_body=VELVET_BODY,
               rim_outline=VELVET_OUTLINE,
               rim_hi=VELVET_RIM_HI)

    # Subtle inner-velvet sheen blob near the top
    sheen = _ss(CAP_W, CAP_H + 4)
    pygame.draw.ellipse(sheen, (220, 130, 150, 130),
                        pygame.Rect(int(CAP_W * 0.34 * SS),
                                    int(CAP_H * 0.16 * SS),
                                    int(CAP_W * 0.20 * SS),
                                    int(CAP_H * 0.42 * SS)))
    sheen.blit(_cone_mask(), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    for fx, fy in ORNAMENT_SLOTS:
        _ornament(big, fx, fy,
                  body=(255, 235, 175),
                  halo=(195, 165, 110))

    _ss_blit(big, surf, cx - CAP_W // 2, cy - CAP_H + 2, CAP_W, CAP_H + 4)


# ── V2 — BLACK-CHERRY (deeper, almost-black wine + bright cream spots) ─────
def draw_v2_black_cherry(surf, cx, cy, pulse=0.0):
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.2)
    _draw_smooth_halo(surf, cx, cy, (140,  40,  70), radius=27,
                      max_alpha=int(155 + 25 * pulse_t))
    _draw_slim_stem(surf, cx, cy + 2)

    big = _ss(CAP_W, CAP_H + 4)
    _draw_cone(big,
               outline=( 30,   8,  18),
               body=(   75,  18,  35),
               hi_stripe=(125,  35,  55),
               rim_body=(  65,  15,  30),
               rim_outline=( 30,  8,  18),
               rim_hi=(155,  60,  75))

    # Velvet sheen — even subtler since the base is darker
    sheen = _ss(CAP_W, CAP_H + 4)
    pygame.draw.ellipse(sheen, (180,  80, 100, 110),
                        pygame.Rect(int(CAP_W * 0.34 * SS),
                                    int(CAP_H * 0.16 * SS),
                                    int(CAP_W * 0.20 * SS),
                                    int(CAP_H * 0.42 * SS)))
    sheen.blit(_cone_mask(), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    # Brighter cream spots so they pop against the very dark cap
    for fx, fy in ORNAMENT_SLOTS:
        _ornament(big, fx, fy,
                  body=(255, 240, 195),
                  halo=(180, 150, 100),
                  r_body=2.1)

    _ss_blit(big, surf, cx - CAP_W // 2, cy - CAP_H + 2, CAP_W, CAP_H + 4)


# ── V3 — VELVET WITH GOLD RIM (wine cap + gold scalloped rim) ──────────────
def draw_v3_gold_rim(surf, cx, cy, pulse=0.0):
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.3)
    _draw_smooth_halo(surf, cx, cy, (200, 130, 110), radius=27,
                      max_alpha=int(155 + 25 * pulse_t))
    _draw_slim_stem(surf, cx, cy + 2)

    big = _ss(CAP_W, CAP_H + 4)

    # Wine cone body
    pygame.draw.polygon(big, VELVET_OUTLINE, _cone_outline_pts())
    pygame.draw.polygon(big, VELVET_BODY,    _cone_body_pts())
    pygame.draw.polygon(big, VELVET_HI,      _cone_hi_pts())

    # Velvet inner sheen
    sheen = _ss(CAP_W, CAP_H + 4)
    pygame.draw.ellipse(sheen, (220, 130, 150, 130),
                        pygame.Rect(int(CAP_W * 0.34 * SS),
                                    int(CAP_H * 0.16 * SS),
                                    int(CAP_W * 0.20 * SS),
                                    int(CAP_H * 0.42 * SS)))
    sheen.blit(_cone_mask(), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    # GOLD scalloped rim
    rim_w = int(CAP_W * 0.86 * SS)
    rim_x = int(CAP_W * 0.07 * SS)
    rim_count = 5
    curl_w = rim_w // rim_count
    for i in range(rim_count):
        center = (rim_x + i * curl_w + curl_w // 2,
                  int(CAP_H * 0.93 * SS))
        pygame.draw.circle(big, (140,  90,  20), center, curl_w // 2)
        pygame.draw.circle(big, (255, 220,  80),
                           center, max(1, curl_w // 2 - SS))
        pygame.draw.circle(big, (255, 250, 200),
                           (center[0] - curl_w // 5, center[1] - curl_w // 5),
                           max(1, curl_w // 4))

    # Cream ornaments (matching the original velvet)
    for fx, fy in ORNAMENT_SLOTS:
        _ornament(big, fx, fy,
                  body=(255, 235, 175),
                  halo=(195, 165, 110))

    _ss_blit(big, surf, cx - CAP_W // 2, cy - CAP_H + 2, CAP_W, CAP_H + 4)


# ── V4 — VELVET WITH GOLD SPOTS (wine cap, polished gold ornaments) ────────
def draw_v4_gold_spots(surf, cx, cy, pulse=0.0):
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.3)
    _draw_smooth_halo(surf, cx, cy, (220, 150, 110), radius=27,
                      max_alpha=int(155 + 25 * pulse_t))
    _draw_slim_stem(surf, cx, cy + 2)

    big = _ss(CAP_W, CAP_H + 4)
    _draw_cone(big,
               outline=VELVET_OUTLINE,
               body=VELVET_BODY,
               hi_stripe=VELVET_HI,
               rim_body=VELVET_BODY,
               rim_outline=VELVET_OUTLINE,
               rim_hi=VELVET_RIM_HI)

    # Velvet sheen
    sheen = _ss(CAP_W, CAP_H + 4)
    pygame.draw.ellipse(sheen, (220, 130, 150, 130),
                        pygame.Rect(int(CAP_W * 0.34 * SS),
                                    int(CAP_H * 0.16 * SS),
                                    int(CAP_W * 0.20 * SS),
                                    int(CAP_H * 0.42 * SS)))
    sheen.blit(_cone_mask(), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    # Polished gold ornament dots
    for fx_frac, fy_frac in ORNAMENT_SLOTS:
        fx = int(CAP_W * fx_frac * SS)
        fy = int(CAP_H * fy_frac * SS)
        pygame.draw.circle(big, (110,  60,  10), (fx, fy), int(2.4 * SS))
        pygame.draw.circle(big, (255, 200,  60), (fx, fy), int(2.0 * SS))
        pygame.draw.circle(big, (255, 230, 130), (fx, fy), int(1.4 * SS))
        pygame.draw.circle(big, (255, 250, 220),
                           (fx - SS // 2, fy - SS // 2), max(1, SS // 2))

    _ss_blit(big, surf, cx - CAP_W // 2, cy - CAP_H + 2, CAP_W, CAP_H + 4)


# ── V5 — VELVET GLOSSY (wine cap with strong silk/satin specular streak) ───
def draw_v5_glossy(surf, cx, cy, pulse=0.0):
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.4)
    _draw_smooth_halo(surf, cx, cy, (200, 110, 130), radius=27,
                      max_alpha=int(165 + 25 * pulse_t))
    _draw_slim_stem(surf, cx, cy + 2)

    big = _ss(CAP_W, CAP_H + 4)
    _draw_cone(big,
               outline=VELVET_OUTLINE,
               body=VELVET_BODY,
               hi_stripe=VELVET_HI,
               rim_body=VELVET_BODY,
               rim_outline=VELVET_OUTLINE,
               rim_hi=VELVET_RIM_HI)

    cone_mask = _cone_mask()

    # SILK/SATIN diagonal specular streak — soft bright wedge sweeping
    # down the left side of the cone.
    streak = _ss(CAP_W, CAP_H + 4)
    pygame.draw.polygon(streak, (255, 220, 230, 230), [
        (int(CAP_W * 0.40 * SS), int(CAP_H * 0.08 * SS)),
        (int(CAP_W * 0.50 * SS), int(CAP_H * 0.08 * SS)),
        (int(CAP_W * 0.30 * SS), int(CAP_H * 0.86 * SS)),
        (int(CAP_W * 0.20 * SS), int(CAP_H * 0.86 * SS)),
    ])
    pygame.draw.polygon(streak, (255, 230, 240, 150), [
        (int(CAP_W * 0.55 * SS), int(CAP_H * 0.22 * SS)),
        (int(CAP_W * 0.62 * SS), int(CAP_H * 0.22 * SS)),
        (int(CAP_W * 0.42 * SS), int(CAP_H * 0.86 * SS)),
        (int(CAP_W * 0.36 * SS), int(CAP_H * 0.86 * SS)),
    ])
    streak.blit(cone_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(streak, (0, 0))

    for fx, fy in ORNAMENT_SLOTS:
        _ornament(big, fx, fy,
                  body=(255, 235, 175),
                  halo=(195, 165, 110))

    _ss_blit(big, surf, cx - CAP_W // 2, cy - CAP_H + 2, CAP_W, CAP_H + 4)


VARIANTS = {
    1: ("1 — refined",     draw_v1_velvet_refined),
    2: ("2 — black-cherry", draw_v2_black_cherry),
    3: ("3 — gold rim",    draw_v3_gold_rim),
    4: ("4 — gold spots",  draw_v4_gold_spots),
    5: ("5 — glossy",      draw_v5_glossy),
}
