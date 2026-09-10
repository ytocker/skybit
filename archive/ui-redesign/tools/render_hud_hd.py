"""High-resolution preview of the final HUD design.

The first preview was pixelated because it smoothscaled a 360×640 frame
up to 1080×1920 — fine for the backdrop but soft on the HUD edges. Here
the backdrop is still rendered at game native and upscaled, but the HUD
elements are drawn DIRECTLY on the 1080×1920 canvas at 3× the game's
coordinates (fonts, radii, stroke widths all 3× too), so circles, pause
bars, text, and pill borders stay crisp.

Output:
  docs/screenshots/hud_variants/final_hd.png   1080 × 1920

The chosen design — locked in:
  - Score:  cream face + 2 px deep-gold rim on a glass pill, y=92
  - BEST:   low-alpha dark slab + gold hairline + star + gold value
  - Coins:  matching slab with the in-game coin face + gold count
  - Pause:  dark disc + double gold ring (bright outer + deep inner) +
            gold bars. No crest.

Run from the repo root:

    PYTHONPATH=. python tools/render_hud_hd.py
"""
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))
from render_hud_variants import draw_bg, draw_pillar_context  # noqa: E402


SCORE = 127
BEST  = 842
COINS = 23
S     = 3   # HD scale — every coord, font size, radius, stroke is × S


def draw_score(canvas, score):
    from game.config import W
    from game.hud import _PANEL_DARK, _GOLD_BRIGHT, _GOLD_DEEP, _font
    from game.draw import NEAR_BLACK
    Ws = W * S
    txt = str(score)
    cf = _font(48 * S, True)
    img = cf.render(txt, True, (252, 244, 220))
    rim = cf.render(txt, True, _GOLD_DEEP)
    sh  = cf.render(txt, True, NEAR_BLACK)
    r = img.get_rect(center=(Ws // 2, 92 * S))

    back_w = max(r.width + 56 * S, 96 * S)
    back_h = 56 * S
    back = pygame.Surface((back_w, back_h), pygame.SRCALPHA)
    pygame.draw.rect(back, (*_PANEL_DARK, 120), (0, 0, back_w, back_h),
                     border_radius=back_h // 2)
    pygame.draw.rect(back, (*_GOLD_BRIGHT, 160), (0, 0, back_w, back_h),
                     border_radius=back_h // 2, width=max(1, S))
    sheen = pygame.Surface((back_w, back_h), pygame.SRCALPHA)
    half = back_h // 2
    for yy in range(half):
        a = int(20 * (1 - yy / half))
        pygame.draw.line(sheen, (255, 245, 220, a),
                         (8 * S, yy + 2 * S),
                         (back_w - 8 * S, yy + 2 * S))
    back.blit(sheen, (0, 0))
    canvas.blit(back, (Ws // 2 - back_w // 2, 92 * S - back_h // 2))

    rim_px = 2 * S
    for ox, oy in ((-rim_px, 0), (rim_px, 0), (0, -rim_px), (0, rim_px),
                   (-rim_px, -rim_px), (rim_px, -rim_px),
                   (-rim_px, rim_px), (rim_px, rim_px)):
        canvas.blit(rim, (r.x + ox, r.y + oy))
    sh.set_alpha(180)
    canvas.blit(sh, (r.x + 2 * S, r.y + 4 * S))
    canvas.blit(img, r.topleft)


def draw_coins_pill(canvas, coins):
    """Compact coins pill — coin face + bold gold count. Sits alone on
    the left at (10, 14). BEST was retired from gameplay since the main
    menu and game-over screens already surface it."""
    from game.hud import _PANEL_DARK, _GOLD_BRIGHT, _coin_icon, _font
    w, h = 60 * S, 30 * S
    cp = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(cp, (*_PANEL_DARK, 140), (0, 0, w, h), border_radius=8 * S)
    pygame.draw.rect(cp, (*_GOLD_BRIGHT, 110), (0, 0, w, h),
                     border_radius=8 * S, width=max(1, S))
    _coin_icon(cp, 13 * S, 15 * S, 8 * S)
    cv = _font(16 * S, True).render(f"x{coins}", True, _GOLD_BRIGHT)
    cp.blit(cv, cv.get_rect(center=(38 * S, 15 * S)))
    canvas.blit(cp, (10 * S, 14 * S))


def draw_pause(canvas):
    """Truly gentle pause — much smaller (38 px vs 46 px), faint disc,
    barely-there hairline, muted gold bars instead of bright. Should
    read as quiet 'tap to pause' affordance, not a feature button."""
    from game.config import W
    from game.hud import _PANEL_DARK, _GOLD_BRIGHT, _GOLD_MUTED
    size = 38 * S
    px = W * S - size - 12 * S
    py = 14 * S
    cx, cy = px + size // 2, py + size // 2
    # Very translucent disc + barely-there gold hairline.
    disc = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(disc, (*_PANEL_DARK, 100),
                       (size // 2, size // 2), size // 2)
    pygame.draw.circle(disc, (*_GOLD_BRIGHT, 80),
                       (size // 2, size // 2), size // 2, max(1, S))
    canvas.blit(disc, (px, py))
    # Muted gold bars — slimmer and quieter than the previous pass.
    pygame.draw.rect(canvas, _GOLD_MUTED,
                     (cx - 5 * S, cy - 7 * S, 3 * S, 14 * S), border_radius=2 * S)
    pygame.draw.rect(canvas, _GOLD_MUTED,
                     (cx + 2 * S, cy - 7 * S, 3 * S, 14 * S), border_radius=2 * S)


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    from game.config import W, H
    pygame.display.set_mode((W, H))

    # Backdrop at game native, then smoothscaled up to HD. Slight softness
    # in the sky/pillars is fine — they have soft edges anyway.
    bg_native = pygame.Surface((W, H))
    palette = draw_bg(bg_native, scroll=120.0, phase=0.62)
    draw_pillar_context(bg_native, palette)
    canvas = pygame.transform.smoothscale(bg_native, (W * S, H * S))

    # HUD drawn natively at HD coordinates → crisp circles, bars, text.
    draw_score(canvas, SCORE)
    draw_coins_pill(canvas, COINS)
    draw_pause(canvas)

    out_dir = os.path.join("docs", "screenshots", "hud_variants")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "final_hd.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({W * S}x{H * S})")


if __name__ == "__main__":
    sys.exit(main() or 0)
