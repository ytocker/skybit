"""Render 5 outline-variant ghost icons for visual comparison.

Standalone — does not import any game code, so the script keeps working
across branches even if the in-code variant logic isn't present. Outputs
docs/ghost_variants.png — all 5 variants side-by-side at 6x scale on a
dark plate, each labelled. Run from the repo root:

    python tools/render_ghost_variants.py
"""
import math
import os
import sys

import pygame

VARIANTS = {
    1: {"thickness": 1.0, "color": ( 40,  50,  90), "mode": "outset", "halo": False, "label": "1 — thin solid"},
    2: {"thickness": 1.0, "color": ( 40,  50,  90), "mode": "outset", "halo": True,  "label": "2 — thin + halo"},
    3: {"thickness": 2.0, "color": ( 90, 110, 160), "mode": "outset", "halo": False, "label": "3 — light navy"},
    4: {"thickness": 0.0, "color": ( 40,  50,  90), "mode": "none",   "halo": False, "label": "4 — no outline"},
    5: {"thickness": 1.0, "color": ( 40,  50,  90), "mode": "inset",  "halo": False, "label": "5 — inset thin"},
}

# Reference (V0) = the current in-game look (2 px navy outset). Included so
# the user can see the starting point next to the proposed thinner versions.
REFERENCE = {"thickness": 2.0, "color": (40, 50, 90), "mode": "outset", "halo": False, "label": "0 — current"}


def build_ghost(cfg) -> pygame.Surface:
    SS = 16
    PAD = 2
    GW, GH = (28 + PAD * 2), (36 + PAD * 2)
    sw, sh = GW * SS, GH * SS
    big = pygame.Surface((sw, sh), pygame.SRCALPHA)

    gcx = (14 + PAD) * SS
    gcy = (12 + PAD) * SS
    hr  = 12 * SS
    body_y2 = (26 + PAD) * SS

    perimeter = []
    n_arc = 64
    for i in range(n_arc + 1):
        theta = math.pi - i * math.pi / n_arc
        x = gcx + hr * math.cos(theta)
        y = gcy - hr * math.sin(theta)
        perimeter.append((int(x), int(y)))
    perimeter.append((gcx + hr, body_y2))
    bump_y   = (GH - 4) * SS
    indent_y = body_y2 + 4 * SS
    x_left   = (1 + PAD) * SS
    x_right  = (28 - 2 + PAD) * SS
    span_x   = x_right - x_left
    scallop_lr = [
        (x_left + i * span_x // 6,
         body_y2 if i in (0, 6) else (bump_y if i % 2 == 1 else indent_y))
        for i in range(7)
    ]
    perimeter.extend(reversed(scallop_lr))
    perimeter.append((gcx - hr, gcy))

    line_thick = cfg["thickness"]
    line_color = cfg["color"]
    mode       = cfg["mode"]
    do_halo    = cfg["halo"]
    t_big      = int(line_thick * SS)

    if do_halo:
        halo_canvas = pygame.Surface((sw, sh), pygame.SRCALPHA)
        halo_t = int(2.5 * SS)
        halo_color = (60, 80, 130, 110)
        for i in range(len(perimeter)):
            p1 = perimeter[i]
            p2 = perimeter[(i + 1) % len(perimeter)]
            pygame.draw.line(halo_canvas, halo_color, p1, p2, halo_t * 2)
        for p in perimeter:
            pygame.draw.circle(halo_canvas, halo_color, p, halo_t)
        big.blit(halo_canvas, (0, 0))

    if mode == "outset" and t_big > 0:
        for i in range(len(perimeter)):
            p1 = perimeter[i]
            p2 = perimeter[(i + 1) % len(perimeter)]
            pygame.draw.line(big, line_color, p1, p2, t_big * 2)
        for p in perimeter:
            pygame.draw.circle(big, line_color, p, t_big)

    mask = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), perimeter)

    stops = [
        (0.00, (240, 215, 255)),
        (0.30, (255, 220, 240)),
        (0.55, (220, 240, 255)),
        (0.80, (215, 255, 235)),
        (1.00, (245, 245, 220)),
    ]
    diag_len = sw + sh
    strip_g = pygame.Surface((diag_len, 1), pygame.SRCALPHA)
    for xx in range(diag_len):
        t = xx / max(1, diag_len - 1)
        if t <= stops[0][0]:
            col = stops[0][1]
        elif t >= stops[-1][0]:
            col = stops[-1][1]
        else:
            col = stops[-1][1]
            for i in range(len(stops) - 1):
                a_pos, a_col = stops[i]
                b_pos, b_col = stops[i + 1]
                if a_pos <= t <= b_pos:
                    u = (t - a_pos) / max(1e-6, b_pos - a_pos)
                    col = (
                        int(a_col[0] + (b_col[0] - a_col[0]) * u),
                        int(a_col[1] + (b_col[1] - a_col[1]) * u),
                        int(a_col[2] + (b_col[2] - a_col[2]) * u),
                    )
                    break
        strip_g.set_at((xx, 0), col + (245,))
    grad = pygame.Surface((sw, sh), pygame.SRCALPHA)
    for yy in range(sh):
        slice_rect = pygame.Rect(yy, 0, sw, 1)
        grad.blit(strip_g, (0, yy), area=slice_rect)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(grad, (0, 0))

    sheen = pygame.Surface((sw, sh), pygame.SRCALPHA)
    sy0 = gcy - hr
    sy1 = gcy + int(hr * 0.5)
    for yy in range(sy0, sy1):
        t = (yy - sy0) / max(1, sy1 - sy0)
        a = int(150 * (1.0 - t) ** 1.5)
        if a > 0:
            pygame.draw.line(sheen, (255, 255, 255, a), (0, yy), (sw, yy))
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    if mode == "inset" and t_big > 0:
        ink = pygame.Surface((sw, sh), pygame.SRCALPHA)
        for i in range(len(perimeter)):
            p1 = perimeter[i]
            p2 = perimeter[(i + 1) % len(perimeter)]
            pygame.draw.line(ink, line_color, p1, p2, t_big * 2)
        for p in perimeter:
            pygame.draw.circle(ink, line_color, p, t_big)
        ink.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        big.blit(ink, (0, 0))

    EYE_W    = (252, 254, 255, 255)
    EYE_IRIS = (50, 110, 220, 255)
    EYE_PUP  = (12,  18,  60, 255)
    for ex_off in (-5, 5):
        ex = gcx + ex_off * SS
        ey = gcy - 1 * SS
        pygame.draw.circle(big, EYE_W,    (ex,        ey       ), int(3.5 * SS))
        pygame.draw.circle(big, EYE_IRIS, (ex + SS,   ey + SS   ), int(2.5 * SS))
        pygame.draw.circle(big, EYE_PUP,  (ex + SS,   ey + SS   ), max(1, SS))
        pygame.draw.circle(big, (255, 255, 255, 220),
                           (ex - SS,    ey - 2 * SS), max(1, SS // 2))

    return pygame.transform.smoothscale(big, (GW, GH))


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    pygame.font.init()

    GW, GH = 32, 40
    SCALE = 6
    SHOW_W, SHOW_H = GW * SCALE, GH * SCALE
    GAP_X = 30
    LABEL_H = 32
    PAD = 28
    cells = [REFERENCE] + [VARIANTS[i] for i in (1, 2, 3, 4, 5)]
    n = len(cells)

    total_w = SHOW_W * n + GAP_X * (n - 1) + PAD * 2
    total_h = SHOW_H + LABEL_H + PAD * 2

    canvas = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
    canvas.fill((24, 30, 56, 255))

    font = pygame.font.SysFont(None, 22, bold=True)

    for i, cfg in enumerate(cells):
        spr = build_ghost(cfg)
        upscaled = pygame.transform.scale(spr, (SHOW_W, SHOW_H))
        x = PAD + i * (SHOW_W + GAP_X)
        y = PAD
        # Per-cell darker plate so the ghost reads the same regardless of
        # whether it has a halo bleeding into the gap.
        cell_plate = pygame.Rect(x - 8, y - 8, SHOW_W + 16, SHOW_H + 16)
        pygame.draw.rect(canvas, (16, 22, 44, 255), cell_plate, border_radius=12)
        canvas.blit(upscaled, (x, y))

        label = font.render(cfg["label"], True, (245, 245, 245))
        canvas.blit(label, (x + (SHOW_W - label.get_width()) // 2,
                            y + SHOW_H + 10))

    out = "docs/ghost_variants.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print(f"saved {out}  ({total_w}x{total_h})")


if __name__ == "__main__":
    sys.exit(main() or 0)
