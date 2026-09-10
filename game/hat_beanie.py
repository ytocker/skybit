import math
import pygame

# Warm knit colorway: burgundy body keeps the beanie cozy and reads at any
# size, cream cuff/pom give the high-contrast cues that survive when shrunk.
_BODY_DARK = (110, 28, 44)
_BODY      = (148, 40, 60)
_BODY_LIT  = (182, 66, 88)
_CREAM     = (244, 232, 206)
_CREAM_LIT = (255, 248, 230)
_CREAM_SHD = (208, 192, 162)


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile knit BEANIE sized for a head of width head_w, centered at cx, cuff line at base_y."""
    r = head_w / 2.0
    # Dome rises a bit taller than a pure hemisphere so the knit looks slouchy
    # rather than skin-tight; underside curves to seat on the round head.
    dome_h = r * 1.18

    # Texture/rib ticks vanish below this head size — only silhouette survives.
    detail = head_w >= 22

    # ── snug dome hugging the round head ────────────────────────────────────
    # Built as stacked horizontal spans so the left/right edges follow a
    # rounded-ellipse profile and the bottom curve seats on the head sphere.
    top_y = base_y - dome_h
    steps = max(14, int(dome_h))
    for i in range(steps):
        t = i / (steps - 1)
        y = top_y + t * dome_h
        # Half-width tapers as an ellipse toward the crown.
        ang = (1.0 - t) ** 0.5
        hw = r * math.sin(min(1.0, t + 0.04) * math.pi * 0.5)
        hw = max(hw, r * 0.18)
        # Knit body shading: lighter toward the lit (facing) side & crown.
        shade = t
        col = _lerp(_BODY_LIT, _BODY_DARK, shade * 0.85)
        x0 = cx - hw
        x1 = cx + hw
        pygame.draw.line(surf, col, (x0, y), (x1, y))

    # Rounded crown cap so the top of the dome stays smooth at all sizes.
    pygame.draw.circle(surf, _BODY_LIT, (int(cx), int(top_y + r * 0.32)), max(2, int(r * 0.34)))

    # ── subtle vertical knit texture lines on the dome ──────────────────────
    if detail:
        n_knit = 5
        for k in range(n_knit):
            f = (k - (n_knit - 1) / 2) / ((n_knit - 1) / 2)  # -1..1 across dome
            lx = cx + f * r * 0.66
            ky0 = base_y - dome_h * (0.92 - abs(f) * 0.30)
            ky1 = base_y - dome_h * 0.10
            shade = _lerp(_BODY_DARK, _BODY, 0.5)
            pygame.draw.line(surf, shade, (lx, ky0), (lx, ky1), 1)

    # ── folded ribbed cuff wrapping the head around base_y ──────────────────
    cuff_h = max(4.0, r * 0.42)
    cuff_w = r * 1.04  # slightly wider than the dome — the fold flares out
    cuff_top = base_y - cuff_h * 0.5
    cuff_bot = base_y + cuff_h * 0.55
    cuff_rect = pygame.Rect(int(cx - cuff_w), int(cuff_top),
                            int(cuff_w * 2), int(cuff_bot - cuff_top))
    # The cuff underside curves up at the ends to sit on the round head.
    pygame.draw.ellipse(surf, _CREAM, cuff_rect)
    # Top lip highlight + bottom shadow give the fold thickness.
    lip = cuff_rect.inflate(0, -cuff_h * 0.9)
    lip.top = cuff_rect.top
    pygame.draw.ellipse(surf, _CREAM_LIT, lip)
    shd = cuff_rect.inflate(-cuff_w * 0.12, -cuff_h * 0.9)
    shd.bottom = cuff_rect.bottom
    pygame.draw.ellipse(surf, _CREAM_SHD, shd)

    # Short vertical rib ticks across the cuff — the knit signature.
    if detail:
        n_rib = max(7, int(cuff_w / 4))
        for k in range(n_rib):
            f = (k - (n_rib - 1) / 2) / ((n_rib - 1) / 2)
            rx = cx + f * cuff_w * 0.9
            # Rib height tapers toward the rounded ends of the cuff.
            taper = (1.0 - abs(f) ** 2)
            rh = cuff_h * 0.5 * (0.45 + 0.55 * taper)
            ry = base_y - rh * 0.5
            col = _CREAM_SHD if (k % 2 == 0) else _CREAM_LIT
            pygame.draw.line(surf, col, (rx, ry), (rx, ry + rh), 1)

    # ── fuzzy cream pom-pom on top ──────────────────────────────────────────
    pom_r = max(2.5, r * 0.30)
    pom_cy = top_y - pom_r * 0.55
    # Outer fuzz: scattered short radial spokes so the edge looks fluffy.
    if detail:
        n_fuzz = 16
        for k in range(n_fuzz):
            a = (k / n_fuzz) * math.tau
            r_out = pom_r * (1.18 + 0.18 * math.sin(a * 3.0))
            x1 = cx + math.cos(a) * r_out
            y1 = pom_cy + math.sin(a) * r_out
            pygame.draw.line(surf, _CREAM_SHD, (cx, pom_cy), (x1, y1), 1)
    # Core ball with a soft highlight toward the facing side.
    pygame.draw.circle(surf, _CREAM, (int(cx), int(pom_cy)), int(pom_r))
    hl = (cx + facing * pom_r * 0.30, pom_cy - pom_r * 0.30)
    pygame.draw.circle(surf, _CREAM_LIT, (int(hl[0]), int(hl[1])), max(1, int(pom_r * 0.5)))


def _lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))
