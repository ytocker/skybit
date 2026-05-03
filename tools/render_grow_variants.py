"""Five distinctive grow (mushroom) icon variants — preview only.

User feedback: the current Mario-style mushroom looks "too simple."
Each variant is a draw function with the same signature as
`PowerUp._draw_mushroom`:

    fn(surf, cx, cy, pulse=0.0)

POWERUP_R = 14 → 28 px diameter footprint. Centred on (cx, cy).

Imported by `tools/render_grow_gameplay.py`. Does NOT modify any game
module.
"""
import math
import pygame


# ── Palette (mirrors game/draw.py MUSH_*) ───────────────────────────────────
POWERUP_R = 14
MUSH_CAP    = (220,  30,  30)
MUSH_CAP2   = (255,  70,  50)
MUSH_SPOT   = (255, 255, 255)
MUSH_STEM   = (245, 225, 195)

CAP_OUTLINE_DK = (130, 10, 20)
SPOT_HALO      = (220, 190, 200)
SPOT_SHADOW    = (160,   0,  10)


# ── Shared helpers ─────────────────────────────────────────────────────────
def _rounded_rect(surf, rect, radius, color):
    pygame.draw.rect(surf, color, rect, border_radius=radius)


def _stem(surf, cx, cy, color=MUSH_STEM, hi=(255, 255, 230), sh=(200, 180, 145),
          width=14, height=13):
    stem = pygame.Rect(cx - width // 2, cy, width, height)
    _rounded_rect(surf, stem, 5, color)
    pygame.draw.line(surf, hi, (cx - width // 2 + 3, cy + 2),
                     (cx - width // 2 + 3, cy + height - 2), 2)
    pygame.draw.line(surf, sh, (cx + width // 2 - 4, cy + 2),
                     (cx + width // 2 - 4, cy + height - 2), 1)


# ── V1 — polished Mario (gradient + raised-emboss spots) ───────────────────
def draw_v1_polished(surf, cx, cy, pulse=0.0):
    """Same Mario silhouette, but with proper depth: vertical gradient on
    the cap, slightly thicker outline, raised-emboss spots (each spot has
    a tiny shadow ring underneath for 3D)."""
    _stem(surf, cx, cy)

    SS = 4
    cap_w = (POWERUP_R + 1) * 2
    cap_h = POWERUP_R + 5
    cap_x = cx - POWERUP_R - 1
    cap_y = cy - POWERUP_R + 2

    big = pygame.Surface((cap_w * SS, cap_h * SS), pygame.SRCALPHA)
    bcw, bch = cap_w * SS, cap_h * SS

    # Outline — thicker dark crimson
    pygame.draw.ellipse(big, CAP_OUTLINE_DK, big.get_rect())
    # Vertical gradient body
    grad = pygame.Surface((bcw, bch), pygame.SRCALPHA)
    for yy in range(bch):
        t = yy / max(1, bch - 1)
        if t < 0.5:
            u = t / 0.5
            col = (
                int(MUSH_CAP2[0] + (MUSH_CAP[0] - MUSH_CAP2[0]) * u),
                int(MUSH_CAP2[1] + (MUSH_CAP[1] - MUSH_CAP2[1]) * u),
                int(MUSH_CAP2[2] + (MUSH_CAP[2] - MUSH_CAP2[2]) * u),
            )
        else:
            u = (t - 0.5) / 0.5
            col = (
                int(MUSH_CAP[0] + (CAP_OUTLINE_DK[0] - MUSH_CAP[0]) * u * 0.6),
                int(MUSH_CAP[1] + (CAP_OUTLINE_DK[1] - MUSH_CAP[1]) * u * 0.6),
                int(MUSH_CAP[2] + (CAP_OUTLINE_DK[2] - MUSH_CAP[2]) * u * 0.6),
            )
        pygame.draw.line(grad, col, (0, yy), (bcw, yy))
    mask = pygame.Surface((bcw, bch), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255),
                        mask.get_rect().inflate(-2 * SS, -2 * SS))
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(grad, (0, 0))

    # Specular crescent
    sp = pygame.Surface((bcw, bch), pygame.SRCALPHA)
    pygame.draw.ellipse(sp, (255, 230, 220, 200),
                        (4 * SS, 3 * SS, bcw - 14 * SS, 4 * SS))
    sp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sp, (0, 0))

    cap = pygame.transform.smoothscale(big, (cap_w, cap_h))
    surf.blit(cap, (cap_x, cap_y))

    # Raised-emboss spots — each has dark shadow ring underneath, then
    # white body, then a tiny bright highlight on top.
    for sx, sy, sr in ((cx - 7, cy - 5, 3),
                       (cx + 6, cy - 7, 4),
                       (cx + 2, cy + 1, 3),
                       (cx - 3, cy + 2, 2)):
        pygame.draw.circle(surf, SPOT_SHADOW, (sx, sy + 1), sr + 1)
        pygame.draw.circle(surf, MUSH_SPOT, (sx, sy), sr)
        pygame.draw.circle(surf, (255, 250, 240), (sx - 1, sy - 1), max(1, sr // 2))


# ── V2 — glowing magical (halo + sparkles) ─────────────────────────────────
def draw_v2_glowing(surf, cx, cy, pulse=0.0):
    """Mario shape + a soft pink-red outer halo + tiny sparkle pricks
    around the cap that twinkle with `pulse`. Reads as 'magical
    powerup'."""
    # Halo first — diffuse pink ring stamped multiple times.
    halo_t = 0.5 + 0.5 * math.sin(pulse * 1.6)
    halo = pygame.Surface((POWERUP_R * 4, POWERUP_R * 4), pygame.SRCALPHA)
    hcx, hcy = halo.get_width() // 2, halo.get_height() // 2 - 4
    for r, a in ((POWERUP_R + 8, int(28 * halo_t)),
                 (POWERUP_R + 5, int(50 * halo_t)),
                 (POWERUP_R + 3, int(85 * halo_t))):
        pygame.draw.circle(halo, (255, 110, 130, a), (hcx, hcy), r)
    halo_rect = halo.get_rect(center=(cx, cy - 4))
    surf.blit(halo, halo_rect.topleft)

    # Body — same Mario layout (using the polished version's gradient)
    _stem(surf, cx, cy)
    cap_rect = pygame.Rect(cx - POWERUP_R - 1, cy - POWERUP_R + 2,
                           (POWERUP_R + 1) * 2, POWERUP_R + 5)
    pygame.draw.ellipse(surf, CAP_OUTLINE_DK, cap_rect.inflate(2, 2))
    pygame.draw.ellipse(surf, MUSH_CAP, cap_rect)
    hi = pygame.Rect(cap_rect.x + 3, cap_rect.y + 2, cap_rect.width - 6, 7)
    pygame.draw.ellipse(surf, MUSH_CAP2, hi)
    sh2 = pygame.Surface((cap_rect.width - 14, 3), pygame.SRCALPHA)
    pygame.draw.ellipse(sh2, (255, 230, 220, 200), sh2.get_rect())
    surf.blit(sh2, (cap_rect.x + 7, cap_rect.y + 3))
    for sx, sy, sr in ((cx - 7, cy - 5, 3),
                       (cx + 6, cy - 7, 4),
                       (cx + 2, cy + 1, 3),
                       (cx - 3, cy + 2, 2)):
        pygame.draw.circle(surf, SPOT_HALO, (sx, sy), sr + 1)
        pygame.draw.circle(surf, MUSH_SPOT, (sx, sy), sr)

    # Sparkles — 3 small twinkles around the cap, alpha-pulsing per sparkle.
    for i, (dx, dy) in enumerate(((-POWERUP_R - 4, -POWERUP_R + 2),
                                  (POWERUP_R + 3, -POWERUP_R - 1),
                                  (0, -POWERUP_R - 4))):
        phase = pulse * 2.5 + i * (math.tau / 3)
        t = 0.5 + 0.5 * math.sin(phase)
        if t > 0.55:
            a = int(255 * (t - 0.55) / 0.45)
            spark = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.line(spark, (255, 240, 220, a), (3, 0), (3, 5), 1)
            pygame.draw.line(spark, (255, 240, 220, a), (0, 3), (5, 3), 1)
            pygame.draw.circle(spark, (255, 255, 255, a), (3, 3), 1)
            surf.blit(spark, (cx + dx - 3, cy + dy - 3))


# ── V3 — natural toadstool (cream spots, gilled hint) ──────────────────────
def draw_v3_toadstool(surf, cx, cy, pulse=0.0):
    """Fly-agaric / forest toadstool: warmer crimson cap, cream-butter
    spots instead of pure white, hint of gilled underside as a darker
    crescent under the cap, slightly tan-gradient stem."""
    NAT_CAP_DK    = (155, 35, 25)
    NAT_CAP_MAIN  = (190, 45, 35)
    NAT_CAP_HI    = (220, 70, 55)
    NAT_SPOT      = (255, 235, 180)
    NAT_SPOT_DK   = (200, 160, 100)
    STEM_TOP      = (250, 230, 200)
    STEM_BOT      = (210, 180, 140)
    STEM_GILL     = ( 75,  35,  25)

    # Stem — vertical gradient
    stem_w, stem_h = 14, 13
    stem_x = cx - stem_w // 2
    for yy in range(stem_h):
        t = yy / max(1, stem_h - 1)
        col = (
            int(STEM_TOP[0] + (STEM_BOT[0] - STEM_TOP[0]) * t),
            int(STEM_TOP[1] + (STEM_BOT[1] - STEM_TOP[1]) * t),
            int(STEM_TOP[2] + (STEM_BOT[2] - STEM_TOP[2]) * t),
        )
        pygame.draw.line(surf, col,
                         (stem_x + 1, cy + yy), (stem_x + stem_w - 2, cy + yy))
    # Round corners — re-blit a small mask to approximate
    for yy in (0, 1, stem_h - 1, stem_h - 2):
        pygame.draw.line(surf, (0, 0, 0, 0),
                         (stem_x, cy + yy), (stem_x + 1, cy + yy))
    pygame.draw.line(surf, (255, 245, 220),
                     (stem_x + 3, cy + 2), (stem_x + 3, cy + stem_h - 2), 2)

    # Gilled-underside hint — a darker crescent just below the cap
    gill = pygame.Surface(((POWERUP_R + 2) * 2, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(gill, (*STEM_GILL, 200), gill.get_rect())
    surf.blit(gill, (cx - POWERUP_R - 2, cy - 2))

    # Cap — multi-layer warm crimson
    cap_rect = pygame.Rect(cx - POWERUP_R - 1, cy - POWERUP_R + 2,
                           (POWERUP_R + 1) * 2, POWERUP_R + 5)
    pygame.draw.ellipse(surf, (90, 15, 10), cap_rect.inflate(2, 2))
    pygame.draw.ellipse(surf, NAT_CAP_DK, cap_rect)
    body_rect = cap_rect.inflate(-2, -1)
    pygame.draw.ellipse(surf, NAT_CAP_MAIN, body_rect)
    hi = pygame.Rect(cap_rect.x + 4, cap_rect.y + 2, cap_rect.width - 8, 6)
    pygame.draw.ellipse(surf, NAT_CAP_HI, hi)

    # Cream/butter spots, slightly fewer + bigger
    for sx, sy, sr in ((cx - 6, cy - 5, 3),
                       (cx + 7, cy - 6, 4),
                       (cx, cy - 1, 3)):
        pygame.draw.circle(surf, NAT_SPOT_DK, (sx, sy + 1), sr + 1)
        pygame.draw.circle(surf, NAT_SPOT, (sx, sy), sr)


# ── V4 — chunky cartoon (mega-thick outline, ground shadow) ────────────────
def draw_v4_chunky(surf, cx, cy, pulse=0.0):
    """Bigger, bolder. 2-px black outlines on every shape, fewer + bigger
    spots, drop-shadow ellipse on the ground beneath the stem. Reads as
    'MEGA' cartoon mushroom."""
    BLACK   = (12, 8, 14)
    CAP_LT  = (250, 90, 80)
    CAP_MID = (225, 35, 35)
    CAP_DK  = (160, 20, 20)
    STEM_LT = (255, 240, 215)
    STEM_DK = (200, 175, 135)

    # Ground drop shadow
    sh = pygame.Surface(((POWERUP_R + 2) * 2, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 110), sh.get_rect())
    surf.blit(sh, (cx - POWERUP_R - 2, cy + 12))

    # Stem — wider, with thick outline
    stem_w, stem_h = 16, 14
    stem_rect = pygame.Rect(cx - stem_w // 2, cy, stem_w, stem_h)
    pygame.draw.rect(surf, BLACK, stem_rect.inflate(2, 2), border_radius=6)
    pygame.draw.rect(surf, STEM_LT, stem_rect, border_radius=5)
    pygame.draw.rect(surf, STEM_DK,
                     pygame.Rect(stem_rect.right - 4, stem_rect.y + 2,
                                 3, stem_rect.height - 4),
                     border_radius=2)

    # Cap — larger, rounder, with thick outline + gradient
    cap_w = (POWERUP_R + 2) * 2
    cap_h = POWERUP_R + 7
    cap_rect = pygame.Rect(cx - cap_w // 2, cy - POWERUP_R, cap_w, cap_h)
    pygame.draw.ellipse(surf, BLACK, cap_rect.inflate(2, 2))
    pygame.draw.ellipse(surf, CAP_DK, cap_rect)
    pygame.draw.ellipse(surf, CAP_MID, cap_rect.inflate(-2, -3))
    hi = pygame.Rect(cap_rect.x + 4, cap_rect.y + 2, cap_rect.width - 8, 6)
    pygame.draw.ellipse(surf, CAP_LT, hi)

    # 3 large spots, each with thick black outline
    for sx, sy, sr in ((cx - 7, cy - 5, 3),
                       (cx + 6, cy - 6, 4),
                       (cx, cy + 2, 3)):
        pygame.draw.circle(surf, BLACK, (sx, sy), sr + 1)
        pygame.draw.circle(surf, MUSH_SPOT, (sx, sy), sr)


# ── V5 — grow arrow (Mario silhouette + gold up-arrow accent) ──────────────
def draw_v5_arrow(surf, cx, cy, pulse=0.0):
    """Mario mushroom + a small gold up-arrow accent overlaid on the cap
    so the 'grow' semantic is literal. The arrow sits between two spots
    and pulses subtly with `pulse`."""
    GOLD_LT  = (255, 232, 130)
    GOLD     = (255, 200,  50)
    GOLD_DK  = (160, 100,  20)

    # Body — same Mario layout
    _stem(surf, cx, cy)
    cap_rect = pygame.Rect(cx - POWERUP_R - 1, cy - POWERUP_R + 2,
                           (POWERUP_R + 1) * 2, POWERUP_R + 5)
    pygame.draw.ellipse(surf, CAP_OUTLINE_DK, cap_rect.inflate(2, 2))
    pygame.draw.ellipse(surf, MUSH_CAP, cap_rect)
    hi = pygame.Rect(cap_rect.x + 3, cap_rect.y + 2, cap_rect.width - 6, 7)
    pygame.draw.ellipse(surf, MUSH_CAP2, hi)
    sh2 = pygame.Surface((cap_rect.width - 14, 3), pygame.SRCALPHA)
    pygame.draw.ellipse(sh2, (255, 230, 220, 200), sh2.get_rect())
    surf.blit(sh2, (cap_rect.x + 7, cap_rect.y + 3))

    # Spots — 2 only (left + right of arrow) so arrow has clean centre
    for sx, sy, sr in ((cx - 8, cy - 4, 3),
                       (cx + 7, cy - 5, 3)):
        pygame.draw.circle(surf, SPOT_HALO, (sx, sy), sr + 1)
        pygame.draw.circle(surf, MUSH_SPOT, (sx, sy), sr)

    # Gold up-arrow accent — small pulsing badge on the cap centre.
    bob = math.sin(pulse * 2.0) * 0.6
    ay = cy - 3 + int(bob)
    arrow_pts_outline = [
        (cx,     ay - 5),
        (cx - 4, ay - 1),
        (cx - 2, ay - 1),
        (cx - 2, ay + 3),
        (cx + 2, ay + 3),
        (cx + 2, ay - 1),
        (cx + 4, ay - 1),
    ]
    arrow_pts_fill = [
        (cx,     ay - 4),
        (cx - 3, ay - 1),
        (cx - 1, ay - 1),
        (cx - 1, ay + 2),
        (cx + 1, ay + 2),
        (cx + 1, ay - 1),
        (cx + 3, ay - 1),
    ]
    pygame.draw.polygon(surf, GOLD_DK, arrow_pts_outline)
    pygame.draw.polygon(surf, GOLD, arrow_pts_fill)
    pygame.draw.line(surf, GOLD_LT, (cx, ay - 3), (cx, ay - 1), 1)


VARIANTS = {
    1: ("1 — polished",    draw_v1_polished),
    2: ("2 — glowing",     draw_v2_glowing),
    3: ("3 — toadstool",   draw_v3_toadstool),
    4: ("4 — chunky",      draw_v4_chunky),
    5: ("5 — grow arrow",  draw_v5_arrow),
}
