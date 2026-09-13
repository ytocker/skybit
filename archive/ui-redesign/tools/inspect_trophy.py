"""Render the TOP 10 panel in isolation at 12× nearest-neighbour zoom
so I can see exactly where the trophy edges sit relative to the panel
border. Iterating on this until the trophy clears the bottom edge."""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


def render(out_path, y_offset, size, draw_label=True):
    pygame.init()
    pygame.font.init()
    from game.hud import _volume_panel, _draw_trophy, _GOLD_PALE, _font
    from game.config import H

    PAD_X, PAD_Y = 40, 40
    panel_w, panel_h = 132, 48
    W = panel_w + PAD_X * 2
    Ht = panel_h + PAD_Y * 2

    surf = pygame.Surface((W, Ht))
    surf.fill((20, 14, 40))

    rect = pygame.Rect(PAD_X, PAD_Y, panel_w, panel_h)
    _volume_panel(surf, rect, radius=14)

    cx, cy = rect.center
    if draw_label:
        lbl = _font(13, True).render("T O P  10", True, _GOLD_PALE)
        lbl.set_alpha(230)
        surf.blit(lbl, lbl.get_rect(center=(cx, cy - 12)))
    _draw_trophy(surf, cx, cy + y_offset, size)

    # 12× nearest-neighbour so individual pixels are crisp.
    big = pygame.transform.scale(surf, (W * 12, Ht * 12))

    # Draw thin red guide lines at the panel's top/bottom edges so I can
    # see whether the trophy overhangs.
    top_y = PAD_Y * 12
    bot_y = (PAD_Y + panel_h) * 12
    pygame.draw.line(big, (255, 60, 60), (0, top_y), (big.get_width(), top_y), 1)
    pygame.draw.line(big, (255, 60, 60), (0, bot_y - 1),
                     (big.get_width(), bot_y - 1), 1)

    pygame.image.save(big, out_path)
    print(f"saved {out_path}  ({big.get_width()}x{big.get_height()})")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        # default sweep
        for y_off, size in [(11, 10), (3, 9), (0, 8), (-2, 8), (-3, 7)]:
            name = f"trophy_y{y_off}_s{size}.png"
            render(os.path.join("/tmp", name), y_off, size)
    else:
        y_off = int(args[0])
        size = int(args[1])
        name = args[2] if len(args) > 2 else f"trophy_y{y_off}_s{size}.png"
        render(os.path.join("/tmp", name), y_off, size)
