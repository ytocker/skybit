"""Master sheet: EVERY Pagoda Warren route we designed, in one figure, sorted
into a difficulty ladder with a 1-10 challenge rating beside each name.

Pulls the routes straight from the five route scripts so this stays in sync with
them. No game/ files are touched.

    PYTHONPATH=. python tools/render_warren_all.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import PIPE_W, GROUND_Y, H
from game.parrot import get_parrot
from game.pillar_pagodas import draw_pillar_pair
from tools.render_warren_mockup import (
    shaped_palette, draw_sky_ground, draw_corridor_glow, draw_flight_path,
    _path_y_at,
)

import tools.render_warren_routes as R1
import tools.render_warren_routes2 as R2
import tools.render_warren_routes3 as R3
import tools.render_warren_routes4 as R4
import tools.render_warren_routes5 as R5

DAY = 0.05
SP_PAD = 72

# Difficulty ratings (1-10), in the SAME ORDER each module's build_routes returns.
TIERS = [
    ("Base — teaching routes", R1.build_routes, [2, 3, 3, 4, 4, 6, 6, 5, 6, 8]),
    ("Advanced — creative",    R2.build_routes, [6, 6, 7, 7, 8, 6, 7, 8, 7, 10]),
    ("Serious drop",           R3.build_routes, [6, 6, 7, 7, 6]),
    ("Aggressive drop",        R4.build_routes, [9, 9, 10, 8, 9]),
    ("Smaller drop (fair)",    R5.build_routes, [4, 4, 5, 4, 5]),
]


def get_pagodas(route):
    p = route.pagodas
    return p() if callable(p) else p


def render_strip(pagodas):
    native_w = pagodas[-1][0] + SP_PAD + 40
    palette = shaped_palette(DAY, dense=False)
    surf = pygame.Surface((native_w, H))
    draw_sky_ground(surf, native_w, H, palette)
    for idx, (x, cy, gap_h, seed) in enumerate(pagodas):
        top_h = cy - gap_h / 2
        bot_y = cy + gap_h / 2
        top_rect = pygame.Rect(int(x - PIPE_W / 2), 0, PIPE_W, int(top_h))
        bot_rect = pygame.Rect(int(x - PIPE_W / 2), int(bot_y),
                               PIPE_W, int(GROUND_Y - bot_y))
        draw_pillar_pair(surf, top_rect, bot_rect, palette, seed,
                         phase=DAY, is_rush=False, pillar_index=idx + 1)
    draw_corridor_glow(surf, pagodas, DAY, dense=False)
    draw_flight_path(surf, pagodas)
    bx = pagodas[min(3, len(pagodas) - 1)][0]
    by = _path_y_at(pagodas, bx)
    nxt = _path_y_at(pagodas, bx + 24)
    bird = get_parrot(1, -12 if nxt > by else 12)
    surf.blit(bird, (int(bx - bird.get_width() / 2),
                     int(by - bird.get_height() / 2)))
    return surf, native_w


def diff_color(d):
    # 1 = green, 5-6 = amber, 10 = red
    if d <= 5:
        t = (d - 1) / 4.0
        return (int(70 + t * 165), int(180 - t * 10), 70)
    t = (d - 5) / 5.0
    return (235, int(170 - t * 130), int(70 - t * 40))


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((360, 640))

    # Collect every route with its tier + rating, then sort into a ladder.
    rows = []
    for tier, build, ratings in TIERS:
        routes = build()
        assert len(routes) == len(ratings), f"{tier}: rating count mismatch"
        for route, d in zip(routes, ratings):
            pg = get_pagodas(route)
            rows.append((d, route.name, tier, route.n, route.duration, pg))
    rows.sort(key=lambda r: (r[0], r[3]))   # by difficulty, then length

    max_native = max(pg[-1][0] + SP_PAD + 40 for *_, pg in rows)
    CONTENT_W = 1820
    factor = min(0.30, CONTENT_W / max_native)
    row_h = int(H * factor)

    PAD, LEFT, ROW_GAP, TITLE_H = 24, 360, 10, 92
    canvas_w = PAD + LEFT + int(max_native * factor) + PAD
    canvas_h = TITLE_H + len(rows) * (row_h + ROW_GAP) + PAD
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((18, 20, 28))

    f_title = pygame.font.SysFont(None, 44, bold=True)
    f_sub = pygame.font.SysFont(None, 24, bold=True)
    f_rate = pygame.font.SysFont(None, 40, bold=True)
    f_name = pygame.font.SysFont(None, 30, bold=True)
    f_tier = pygame.font.SysFont(None, 20, bold=True)
    f_meta = pygame.font.SysFont(None, 20, bold=True)

    canvas.blit(f_title.render(
        f"PAGODA WARREN — all {len(rows)} routes, by challenge", True,
        (245, 245, 250)), (PAD, PAD - 2))
    canvas.blit(f_sub.render(
        "difficulty 1-10 (left)  ·  one full route per row, uniform scale  ·  "
        "easiest at top", True, (170, 200, 235)), (PAD, PAD + 40))

    y = TITLE_H
    for (d, name, tier, n, dur, pg) in rows:
        strip, native_w = render_strip(pg)
        disp_w = int(native_w * factor)
        scaled = pygame.transform.smoothscale(strip, (disp_w, row_h))
        rx = PAD + LEFT
        canvas.blit(scaled, (rx, y))
        pygame.draw.rect(canvas, (60, 68, 88),
                         pygame.Rect(rx - 1, y - 1, disp_w + 2, row_h + 2), 1)

        # Left gutter: rating chip + bar, name, tier, length.
        col = diff_color(d)
        chip = f_rate.render(f"{d}", True, (15, 17, 22))
        cw = 56
        pygame.draw.rect(canvas, col, pygame.Rect(PAD, y + 6, cw, 40),
                         border_radius=8)
        canvas.blit(chip, (PAD + (cw - chip.get_width()) // 2, y + 11))
        canvas.blit(f_meta.render("/10", True, col), (PAD + cw + 4, y + 24))

        canvas.blit(f_name.render(name, True, (240, 230, 170)),
                    (PAD + cw + 40, y + 4))
        canvas.blit(f_tier.render(tier, True, (150, 160, 175)),
                    (PAD + cw + 40, y + 30))
        # difficulty bar
        bar_x, bar_w = PAD + cw + 40, LEFT - cw - 64
        pygame.draw.rect(canvas, (40, 44, 56),
                         pygame.Rect(bar_x, y + 50, bar_w, 7), border_radius=3)
        pygame.draw.rect(canvas, col,
                         pygame.Rect(bar_x, y + 50, int(bar_w * d / 10), 7),
                         border_radius=3)
        canvas.blit(f_meta.render(f"{n}p · ~{dur:.0f}s", True, (170, 195, 175)),
                    (bar_x + bar_w + 8, y + 48))

        y += row_h + ROW_GAP

    out_dir = os.path.join("docs", "pagoda_warren")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "routes_all.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})  scale={factor:.3f}  "
          f"{len(rows)} routes")


if __name__ == "__main__":
    main()
