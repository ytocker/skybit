"""Five halo-size variations of the refined velvet witch-hat — round 8.

User picked V1 'refined' from round 7 (commit 9fbe9bf) and asked for
"the halo larger. Again 5 versions."

The cap, stem, ornaments, and inner sheen are identical across all
five — only the halo (size, intensity, single- vs two-tone) varies.
This makes it easy to pick the size by direct comparison.

Each function has the same signature as `PowerUp._draw_mushroom`:

    fn(surf, cx, cy, pulse=0.0)

Imported by `tools/render_grow_gameplay.py`. Does NOT modify game code.
"""
import math
import pygame


SS = 5  # supersample factor — same as round 7


# ── Helpers ────────────────────────────────────────────────────────────────
def _ss(w, h):
    return pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)


def _ss_blit(big, dst, x, y, w, h):
    dst.blit(pygame.transform.smoothscale(big, (w, h)), (x, y))


def _draw_smooth_halo(surf, cx, cy, color_rgb, radius, max_alpha,
                      falloff=2.2, peak_y_off=-2):
    """~60 concentric circles with quadratic alpha falloff → continuous
    radial gradient with no banding. Steps scale with radius so larger
    halos stay just as smooth as smaller ones."""
    steps = max(60, radius * 2)
    w = radius * 2 + 4
    halo = pygame.Surface((w, w), pygame.SRCALPHA)
    hcx = hcy = w // 2
    for i in range(steps):
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


def _cone_mask():
    m = _ss(CAP_W, CAP_H + 4)
    pygame.draw.polygon(m, (255, 255, 255, 255), _cone_body_pts())
    return m


VELVET_OUTLINE = ( 60,  15,  25)
VELVET_BODY    = (125,  30,  45)
VELVET_HI      = (180,  60,  75)
VELVET_RIM_HI  = (220, 120, 130)


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


def _draw_velvet_body(surf, cx, cy):
    """The refined-velvet body: stem + cone + sheen + cream spots.
    Identical across all five variants in this round so the halo is
    the only visual variable."""
    _draw_slim_stem(surf, cx, cy + 2)

    big = _ss(CAP_W, CAP_H + 4)
    pygame.draw.polygon(big, VELVET_OUTLINE,   _cone_outline_pts())
    pygame.draw.polygon(big, VELVET_BODY,      _cone_body_pts())
    pygame.draw.polygon(big, VELVET_HI,        _cone_hi_pts())

    rim_w = int(CAP_W * 0.86 * SS)
    rim_x = int(CAP_W * 0.07 * SS)
    rim_count = 5
    curl_w = rim_w // rim_count
    for i in range(rim_count):
        center = (rim_x + i * curl_w + curl_w // 2,
                  int(CAP_H * 0.93 * SS))
        pygame.draw.circle(big, VELVET_BODY,    center, curl_w // 2)
        pygame.draw.circle(big, VELVET_OUTLINE, center, curl_w // 2, SS)
        pygame.draw.circle(big, VELVET_RIM_HI,
                           (center[0] - curl_w // 5, center[1] - curl_w // 5),
                           max(1, curl_w // 4))

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


# ── 5 halo variations ──────────────────────────────────────────────────────
# Reference: round-7 V1 used radius=27, max_alpha≈170, color (180, 90, 110).
# Halo "centre" sits a bit above the cap base (peak_y_off=-2).

HALO_PINK     = (180,  90, 110)
HALO_PEACH    = (220, 160, 130)


def draw_v1_halo_34(surf, cx, cy, pulse=0.0):
    """+25% larger halo (radius 34). Modest size bump."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.2)
    _draw_smooth_halo(surf, cx, cy, HALO_PINK,
                      radius=34, max_alpha=int(155 + 25 * pulse_t))
    _draw_velvet_body(surf, cx, cy)


def draw_v2_halo_40(surf, cx, cy, pulse=0.0):
    """+50% larger halo (radius 40). Medium size bump."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.2)
    _draw_smooth_halo(surf, cx, cy, HALO_PINK,
                      radius=40, max_alpha=int(150 + 25 * pulse_t))
    _draw_velvet_body(surf, cx, cy)


def draw_v3_halo_46(surf, cx, cy, pulse=0.0):
    """+70% larger halo (radius 46). Big spread."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.2)
    _draw_smooth_halo(surf, cx, cy, HALO_PINK,
                      radius=46, max_alpha=int(140 + 25 * pulse_t))
    _draw_velvet_body(surf, cx, cy)


def draw_v4_halo_54(surf, cx, cy, pulse=0.0):
    """+100% larger halo (radius 54). Very large gentle aura."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.2)
    _draw_smooth_halo(surf, cx, cy, HALO_PINK,
                      radius=54, max_alpha=int(125 + 25 * pulse_t),
                      falloff=2.4)
    _draw_velvet_body(surf, cx, cy)


def draw_v5_halo_two_tone(surf, cx, cy, pulse=0.0):
    """Two-stage halo: warm peach outer ring (radius 50) softly fading
    out, with a tighter pink core (radius 32) on top. Reads as a
    layered glow rather than a single soft cloud."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.2)
    # Outer warm peach (large + soft)
    _draw_smooth_halo(surf, cx, cy, HALO_PEACH,
                      radius=50, max_alpha=int(95 + 20 * pulse_t),
                      falloff=2.6)
    # Inner pink (tighter + brighter)
    _draw_smooth_halo(surf, cx, cy, HALO_PINK,
                      radius=32, max_alpha=int(155 + 30 * pulse_t),
                      falloff=2.0)
    _draw_velvet_body(surf, cx, cy)


VARIANTS = {
    1: ("1 — halo r34",  draw_v1_halo_34),
    2: ("2 — halo r40",  draw_v2_halo_40),
    3: ("3 — halo r46",  draw_v3_halo_46),
    4: ("4 — halo r54",  draw_v4_halo_54),
    5: ("5 — two-tone",  draw_v5_halo_two_tone),
}
