"""Narrow E3 — Diamond Trio sized to fit INSIDE the gold #1 badge.

User picked E3 (Diamond Trio — 3 peaks with kite-cut sapphire/ruby/
sapphire) but rejected the size: the crown was wider than the badge
it perches on. The badge has radius 13 (= 26 px wide). This variant
drops bbox to 24 × 28 so the crown silhouette tucks inside the
badge width with a 1-px margin on each side.

Run:
  python3 tools/preview_crown_e3_narrow.py

Output:
  tools/screenshots/crown_e3_narrow.png
"""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
import pygame

pygame.init()
pygame.font.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import W, H
from tools.preview_crown_variants import (
    draw_leaderboard_variant, draw_bg, SCORES,
)
from tools.preview_crown_grandiose import (
    GOLD_HI, GOLD, GOLD_LO,
    RUBY, RUBY_HI, SAPPHIRE, SAPPHIRE_HI,
    WHITE_HI, _with_shadow, _aura,
)
from tools.preview_crown_kings import (
    NEAR_BLACK,
    _oversampled2, _band_outlined,
    _outlined_polygon, _outlined_gem,
)
from tools.preview_crown_elegant import (
    _sheen, _blit_anchored,
)


def _draw_e3_narrow(big, s):
    """Narrow Diamond Trio: 3 tight peaks + kite-cut gems, sized so
    the crown fits within a 24 px bbox (1 px narrower than the badge
    on each side)."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    # Aura — tighter radii so the glow stays close to the crown
    _aura(big, cx, bh - 9 * s,
          radii=[9 * s, 6 * s, 4 * s],
          alphas=[40, 65, 95])

    # Thinner band for the narrow form
    band_h = 6 * s
    band_top = bh - band_h
    band_bot = bh
    band_l = 1 * s
    band_r = bw - 1 * s
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)
    _sheen(big, s, band_top, band_bot, band_l, band_r)

    # Single central ruby on the band (small — narrow crown)
    band_cy = (band_top + band_bot) // 2
    _outlined_gem(big, cx, band_cy, int(1.2 * s), RUBY, RUBY_HI)

    # Three peaks tucked tight — span ~12 px in target coords
    peak_xs = [cx - 6 * s, cx, cx + 6 * s]
    peak_pw = max(2, int(1.7 * s))
    peak_h = bh - band_h - 5 * s
    gem_cols = [(SAPPHIRE, SAPPHIRE_HI), (RUBY, RUBY_HI),
                (SAPPHIRE, SAPPHIRE_HI)]
    for px, (gc, gh) in zip(peak_xs, gem_cols):
        tip = (px, band_top - peak_h)
        l   = (px - peak_pw, band_top)
        r   = (px + peak_pw, band_top)
        _outlined_polygon(big, [tip, l, r], GOLD, GOLD_HI)
        # Kite-cut gem above each peak
        gem_top   = (px, tip[1] - int(2.5 * s))
        gem_bot   = (px, tip[1] - int(0.3 * s))
        gem_left  = (px - int(1.3 * s), tip[1] - int(1.4 * s))
        gem_right = (px + int(1.3 * s), tip[1] - int(1.4 * s))
        _outlined_polygon(big,
                          [gem_top, gem_right, gem_bot, gem_left],
                          gc, gh)
        # Glint
        pygame.draw.line(big, WHITE_HI,
                         (gem_top[0] - 1, gem_top[1] + 1),
                         (gem_top[0] - 1, gem_top[1] + int(1.5 * s)),
                         max(1, s // 2))

    # Tighter sparkles — kept inside the bbox so they don't extend
    # past the badge perimeter
    cx_pix = bw // 2
    cy_pix = bh // 2
    tight_pos = [(-0.85, -0.55), (0.85, -0.55),
                 (-0.70,  0.25), (0.70,  0.25)]
    for x_frac, y_frac in tight_pos:
        sx = int(cx_pix + x_frac * (bw // 2))
        sy = int(cy_pix + y_frac * (bh // 2))
        sx = max(2, min(bw - 2, sx))
        sy = max(2, min(bh - 2, sy))
        pygame.draw.line(big, WHITE_HI,
                         (sx - int(1.5 * s), sy),
                         (sx + int(1.5 * s), sy),
                         max(1, s // 2))
        pygame.draw.line(big, WHITE_HI,
                         (sx, sy - int(1.5 * s)),
                         (sx, sy + int(1.5 * s)),
                         max(1, s // 2))


def draw_crown_e3_narrow(surf, cx, cy):
    bw, bh = 24, 28
    img = _with_shadow(_oversampled2(_draw_e3_narrow, bw, bh))
    _blit_anchored(surf, img, cx, cy, bw, bh)


OUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    screen = pygame.Surface((W, H))
    draw_bg(screen)
    draw_leaderboard_variant(
        screen, title_t=1.4, scores=SCORES,
        player_rank=6, variant=6, crown_drawer=draw_crown_e3_narrow)
    out = os.path.join(OUT_DIR, "crown_e3_narrow.png")
    pygame.image.save(screen, out)
    print(f"saved {out}")


if __name__ == "__main__":
    main()
