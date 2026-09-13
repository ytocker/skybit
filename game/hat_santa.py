"""Procedural Santa hat for Skybit's coin Store — side profile.

`draw_hat(surf, cx, base_y, head_w, facing=1)` paints a festive Santa hat
sized for a round head of width `head_w` centred at `cx`, with the white
fur-trim line at `base_y`. The soft red cone rises above the trim and flops
toward the front (right at facing=1), ending in a round white pom-pom.

All geometry is derived from (cx, base_y, head_w) so the same call reads
correctly from a tiny store icon (head_w≈18) up to a hero product shot
(head_w≈80). Caller owns the outer outline; we only add subtle 1px edges.
"""
import math
import pygame

# Bright Santa red with shaded tones for soft cone volume, plus warm-white
# fur so the trim/pom never look grey against a dark navy backdrop.
RED        = (208,  38,  46)
RED_DK     = (158,  24,  34)
RED_HI     = (236,  84,  88)
FUR_WHITE  = (248, 248, 252)
FUR_SHADE  = (210, 212, 224)
FUR_HI     = (255, 255, 255)
FUR_DAPPLE = (224, 226, 238)


def _lerp(a, b, t):
    return a + (b - a) * t


def _bezier(p0, p1, p2, t):
    """Quadratic Bézier — the cone's spine sweeps up from the trim then
    floppily curls over toward the front via a single control point."""
    u = 1.0 - t
    x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
    y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
    return x, y


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile SANTA HAT sized for a head of width head_w,
    centered at cx, fur-trim line at base_y."""
    r = head_w * 0.5
    s = head_w / 80.0          # scale factor; tuned at the hero size
    f = 1 if facing >= 0 else -1

    # ── geometry of the floppy cone ───────────────────────────────────────────
    # The cone leaves the head near the back/top, arcs forward and droops, so
    # the spine is a Bézier from the base anchor, through a raised control
    # point, down to the drooping tip out front.
    base_anchor = (cx - f * r * 0.36, base_y - r * 0.42)
    apex_ctrl   = (cx + f * r * 0.30, base_y - r * 1.18)
    tip         = (cx + f * r * 1.18, base_y - r * 0.30)

    # Cone half-width tapers from a fat base to the slim pom neck.
    base_half = r * 0.62
    tip_half  = max(1.2, r * 0.12)

    steps = max(14, int(20 * max(s, 0.5)))
    spine = []
    for i in range(steps + 1):
        t = i / steps
        sx, sy = _bezier(base_anchor, apex_ctrl, tip, t)
        half = _lerp(base_half, tip_half, t)
        # Perpendicular direction along the spine to give the ribbon width.
        t2 = min(1.0, t + 0.01)
        nx, ny = _bezier(base_anchor, apex_ctrl, tip, t2)
        dx, dy = nx - sx, ny - sy
        dlen = math.hypot(dx, dy) or 1.0
        px, py = -dy / dlen, dx / dlen
        spine.append((sx, sy, half, px, py))

    # Build left/right edges of the cone ribbon.
    left_edge, right_edge = [], []
    for sx, sy, half, px, py in spine:
        left_edge.append((sx + px * half, sy + py * half))
        right_edge.append((sx - px * half, sy - py * half))

    cone_poly = left_edge + right_edge[::-1]

    # Drop shadow of the cone onto the head, offset down a touch.
    shadow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    sh_poly = [(x, y + r * 0.10) for (x, y) in cone_poly]
    pygame.draw.polygon(shadow, (0, 0, 0, 55), sh_poly)
    surf.blit(shadow, (0, 0))

    # Cone body — dark base fill, then the bright red on top inset slightly.
    pygame.draw.polygon(surf, RED_DK, cone_poly)

    inset = []
    for sx, sy, half, px, py in spine:
        h2 = max(0.0, half - max(1.0, s * 1.4))
        inset.append((sx + px * h2, sy + py * h2))
    inset_r = []
    for sx, sy, half, px, py in spine:
        h2 = max(0.0, half - max(1.0, s * 1.4))
        inset_r.append((sx - px * h2, sy - py * h2))
    pygame.draw.polygon(surf, RED, inset + inset_r[::-1])

    # Upper-edge sheen ribbon — a thin bright-red highlight tracing the top
    # of the flop gives the soft fabric some roundness.
    hi_line = []
    for i, (sx, sy, half, px, py) in enumerate(spine):
        hh = half * 0.55
        hi_line.append((sx + px * hh, sy + py * hh))
    if len(hi_line) >= 2:
        pygame.draw.lines(surf, RED_HI, False, hi_line, max(1, int(round(s * 2))))

    # ── fur trim band ─────────────────────────────────────────────────────────
    # A thick fluffy white band wrapping the head along base_y, curved on its
    # underside to seat on the round head. Drawn as a fat rounded ellipse.
    trim_w = head_w * 1.06
    trim_h = max(5.0, r * 0.46)
    trim_rect = pygame.Rect(0, 0, trim_w, trim_h)
    trim_rect.center = (cx, base_y)

    pygame.draw.ellipse(surf, FUR_SHADE,
                        (trim_rect.x, trim_rect.y + max(1, s * 1.2),
                         trim_rect.w, trim_rect.h))
    pygame.draw.ellipse(surf, FUR_WHITE, trim_rect)
    # Top sheen on the trim.
    pygame.draw.ellipse(surf, FUR_HI,
                        (trim_rect.x + trim_rect.w * 0.10,
                         trim_rect.y + 1,
                         trim_rect.w * 0.80, max(2.0, trim_rect.h * 0.45)))

    # Fuzzy dappling on the trim — a scatter of tiny soft blobs so the fur
    # reads as fluffy, not a smooth plastic band. Deterministic placement.
    n_dap = max(3, int(7 * max(s, 0.45)))
    dap_r = max(1.0, trim_h * 0.20)
    for i in range(n_dap):
        t = (i + 0.5) / n_dap
        dx = trim_rect.x + trim_rect.w * (0.08 + 0.84 * t)
        dy = trim_rect.centery + math.sin(t * math.pi * 3.0 + 1.3) * trim_h * 0.18
        col = FUR_DAPPLE if (i % 2 == 0) else FUR_HI
        pygame.draw.circle(surf, col, (int(dx), int(dy)), int(dap_r))

    # ── pom-pom ───────────────────────────────────────────────────────────────
    px_tip, py_tip = tip
    pom_r = max(2.5, r * 0.30)
    # Nudge the pom outward along the tip direction so it caps the flop.
    pom_cx = px_tip + f * pom_r * 0.18
    pom_cy = py_tip

    pygame.draw.circle(surf, FUR_SHADE, (int(pom_cx), int(pom_cy + s * 1.2)),
                       int(pom_r))
    pygame.draw.circle(surf, FUR_WHITE, (int(pom_cx), int(pom_cy)), int(pom_r))
    # Fuzzy edge dapples + a bright highlight for a soft round read.
    n_pdap = max(4, int(7 * max(s, 0.5)))
    for i in range(n_pdap):
        a = (i / n_pdap) * math.tau
        ex = pom_cx + math.cos(a) * pom_r * 0.82
        ey = pom_cy + math.sin(a) * pom_r * 0.82
        pygame.draw.circle(surf, FUR_DAPPLE, (int(ex), int(ey)),
                           max(1, int(pom_r * 0.28)))
    pygame.draw.circle(surf, FUR_HI,
                       (int(pom_cx - pom_r * 0.28), int(pom_cy - pom_r * 0.30)),
                       max(1, int(pom_r * 0.34)))
