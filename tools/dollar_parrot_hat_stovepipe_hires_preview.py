"""Render the high-resolution stovepipe hat preview.

The parrot is rendered at native res (with its outline), upscaled 5×, then
the hat is drawn DIRECTLY at preview scale using smooth gradients and
oversampled anti-aliased ellipses. This avoids the pixelation that comes
from upscaling a small native sprite — only the parrot itself stays
chunky-pixel; the hat is crisp.

Run:
    python tools/dollar_parrot_hat_stovepipe_hires_preview.py
"""
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.parrot import _build_frame, _add_outline, _WING_ANGLES
from game.dollar_parrot_hat import (
    draw_stovepipe_hires,
    COMPOSITE_W, COMPOSITE_H, PARROT_DY, HAT_HX, HAT_HY,
)
from game.draw import UI_GOLD, NEAR_BLACK, lerp_color

OUT = pathlib.Path(__file__).parent.parent / "docs" / "dollar_parrot_hat_stovepipe_hires.png"

S        = 5            # preview scale
WING_IDX = 2
PAD      = 24


def _font(size):
    asset_dir = pathlib.Path(__file__).parent.parent / "game" / "assets"
    return pygame.font.Font(str(asset_dir / "LiberationSans-Bold.ttf"), size)


def _draw_centered(surf, text, center, size, color):
    f   = _font(size)
    img = f.render(text, True, color)
    sh  = f.render(text, True, NEAR_BLACK)
    r   = img.get_rect(center=center)
    surf.blit(sh,  (r.x + 2, r.y + 2))
    surf.blit(img, r.topleft)


def render() -> pygame.Surface:
    # Build the normal parrot at native res (with original aviator sunglasses)
    parrot_native = _add_outline(_build_frame(_WING_ANGLES[WING_IDX]))
    pn_w, pn_h    = parrot_native.get_size()    # 68 × 64 after outline padding

    # Upscale parrot → pixelated, matches the in-game rendering style
    parrot_scaled = pygame.transform.scale(parrot_native, (pn_w * S, pn_h * S))
    psw, psh      = parrot_scaled.get_size()    # 340 × 320

    # Composite canvas at preview scale (large enough for the tall hat)
    canvas_w = COMPOSITE_W * S    # 320
    canvas_h = COMPOSITE_H * S    # 400
    canvas   = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)

    # Blit the upscaled parrot. The outline added 2 px padding, so the
    # "true" parrot top-left in the outlined surface is (2,2). To position
    # the parrot correctly on the composite we offset by (-2 * S).
    parrot_x = (0 - 2) * S          # -10
    parrot_y = (PARROT_DY - 2) * S  # 90
    canvas.blit(parrot_scaled, (parrot_x, parrot_y))

    # Hat at preview scale (smooth gradients + oversampled ellipses)
    draw_stovepipe_hires(canvas, HAT_HX * S, HAT_HY * S, S=S)

    # Final preview frame with navy backdrop and label
    out_w = canvas_w + PAD * 2
    out_h = canvas_h + PAD * 2 + 50
    surf  = pygame.Surface((out_w, out_h))
    for y in range(out_h):
        t = y / max(1, out_h - 1)
        c = lerp_color((18, 28, 64), (8, 14, 36), t)
        pygame.draw.line(surf, c, (0, y), (out_w - 1, y))
    surf.blit(canvas, (PAD, PAD))
    _draw_centered(surf, "STOVEPIPE — hi-res hat",
                   (out_w // 2, out_h - 24), 20, UI_GOLD)
    return surf


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    surf = render()
    pygame.image.save(surf, OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
