"""Render BEST + TOP 10 panels side-by-side at 8× zoom so I can dial in
the trophy y-offset until its visible bottom aligns with the '842'
baseline on the BEST panel."""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


def render(out_path, y_offset, size):
    pygame.init()
    pygame.font.init()
    from game.hud import (
        _volume_panel, _draw_trophy, _GOLD_PALE, _GOLD_BRIGHT, _font,
    )

    PAD_X, PAD_Y = 40, 40
    PANEL_W, PANEL_H = 132, 48
    GAP = 8
    W = PANEL_W * 2 + GAP + PAD_X * 2
    Ht = PANEL_H + PAD_Y * 2

    surf = pygame.Surface((W, Ht))
    surf.fill((20, 14, 40))

    best_rect = pygame.Rect(PAD_X, PAD_Y, PANEL_W, PANEL_H)
    top_rect = pygame.Rect(PAD_X + PANEL_W + GAP, PAD_Y, PANEL_W, PANEL_H)
    _volume_panel(surf, best_rect, radius=14)
    _volume_panel(surf, top_rect, radius=14)

    cx_b, cy_b = best_rect.center
    cx_t, cy_t = top_rect.center
    lf = _font(13, True)
    vf = _font(24, True)

    # BEST panel
    lbl = lf.render("B E S T", True, _GOLD_PALE); lbl.set_alpha(230)
    surf.blit(lbl, lbl.get_rect(center=(cx_b, cy_b - 12)))
    val = vf.render("842", True, _GOLD_BRIGHT)
    surf.blit(val, val.get_rect(center=(cx_b, cy_b + 9)))

    # TOP 10 panel
    tl = lf.render("T O P  10", True, _GOLD_PALE); tl.set_alpha(230)
    surf.blit(tl, tl.get_rect(center=(cx_t, cy_t - 12)))
    _draw_trophy(surf, cx_t, cy_t + y_offset, size)

    # 8× nearest-neighbour zoom
    big = pygame.transform.scale(surf, (W * 8, Ht * 8))

    # Red horizontal guide at the BEST text visual bottom — by sampling
    # the rendered numeral pixels.
    val_rect = val.get_rect(center=(cx_b, cy_b + 9))
    # Find lowest non-transparent pixel of the value glyph by scanning
    # downward in the actual surface.
    base_y_native = val_rect.bottom - 1
    # Liberation Sans Bold tends to have a few px of descender space
    # below baseline; tighten by scanning the rendered glyph surface.
    for yy in range(val.get_height() - 1, -1, -1):
        row_has = False
        for xx in range(val.get_width()):
            if val.get_at((xx, yy))[3] > 30:
                row_has = True
                break
        if row_has:
            base_y_native = val_rect.y + yy
            break

    guide_y = base_y_native * 8
    pygame.draw.line(big, (255, 60, 60), (0, guide_y),
                     (big.get_width(), guide_y), 2)

    # Trophy bottom — scan a narrow central column of the TOP 10 panel
    # so we don't hit the gold panel border (which is also _GOLD_BRIGHT).
    trophy_bot = None
    cx_strip = (top_rect.x + top_rect.right) // 2
    strip = range(cx_strip - 8, cx_strip + 8)
    # Also stay clear of the bottom panel border (3 px inset).
    for yy in range(top_rect.bottom - 4, top_rect.y, -1):
        for xx in strip:
            px = surf.get_at((xx, yy))
            if px[0] >= 200 and px[1] >= 150 and px[2] <= 100:
                trophy_bot = yy
                break
        if trophy_bot is not None:
            break
    if trophy_bot is not None:
        gy = trophy_bot * 8
        pygame.draw.line(big, (60, 200, 255), (0, gy),
                         (big.get_width(), gy), 2)

    pygame.image.save(big, out_path)
    print(f"saved {out_path}  text bottom y={base_y_native}  trophy bot y={trophy_bot}")


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        y_off = int(sys.argv[1])
        size = int(sys.argv[2])
        name = sys.argv[3] if len(sys.argv) > 3 else f"panels_y{y_off}_s{size}.png"
        render(os.path.join("/tmp", name), y_off, size)
    else:
        for y in [5, 6, 7, 8, 9, 10]:
            render(f"/tmp/panels_y{y}_s9.png", y, 9)
