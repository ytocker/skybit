"""Render a static PNG mockup of the redesigned main-menu screen.

This script does NOT modify the game. It builds one 360x640 frame using
the exact helpers from `game.hud` (so the colours, fonts, and pill style
match the live game one-for-one), and writes the image to
`docs/menu_preview/menu_v1.png` for review.

Layout under review:
  * SKYBIT title + subtitle + divider — unchanged from the current menu.
  * Three stacked pill buttons in place of today's single CTA pill:
      1) TAP TO START   (largest / breathing alpha)
      2) HOW TO PLAY    (plays the intro tutorial on demand)
      3) POWERUPS       (replaces the corner `?` button)
  * BEST score panel — unchanged.
  * No `?` button in the top-left corner.

Run headless:
    SDL_VIDEODRIVER=dummy python3 tools/render_menu_preview.py
"""
import os
import sys

# Headless SDL so this can render in CI / containers with no display.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

# Make `import game.hud` resolve when running from the repo root.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

pygame.init()
pygame.font.init()

# Imported after pygame.init so font loading inside hud.py succeeds.
from game.config import W, H  # noqa: E402
from game.hud import (  # noqa: E402
    HUD,
    _outlined_text,
    _pill_btn,
    _dark_panel,
    _draw_overlay_stars,
    _draw_mountain_silhouette,
    _font,
    _GOLD_BRIGHT,
    _GOLD_MUTED,
    _ORANGE_BORDER,
)

import math  # noqa: E402


def render_menu_mockup(t: float = 0.0, best: int = 42) -> pygame.Surface:
    """Paint one frame of the proposed menu onto a 360x640 surface."""
    surf = pygame.Surface((W, H))
    # Match the in-game backdrop: deep night-blue base, then star + mountain
    # overlay, then the night-sky tint that draw_menu uses.
    surf.fill((6, 1, 21))

    hud = HUD()  # only used for its pre-seeded star list
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 110))
    surf.blit(dim, (0, 0))

    _draw_overlay_stars(surf, hud._stars, t)
    _draw_mountain_silhouette(surf, alpha=180)

    # Title + subtitle + divider — identical to draw_menu (game/hud.py:551-563).
    pulse = 1.0 + math.sin(t * 2.4) * 0.04
    float_y = int(7 * math.sin(t * 1.8))
    _outlined_text(surf, "SKYBIT", (W // 2, 126 + float_y),
                   size=int(72 * pulse), px=3)
    _outlined_text(surf, "POCKET SKY FLYER", (W // 2, 184),
                   size=22, px=2, shadow_offset=(2, 3))
    pygame.draw.line(surf, (*_ORANGE_BORDER, 120),
                     (W // 2 - 70, 208), (W // 2 + 70, 208), 1)

    # ── Three stacked pills (the redesign) ────────────────────────────────
    # Shared min_width = 220 keeps all three buttons the same visual width.
    # Centres are computed from actual pill heights + a fixed inter-pill gap
    # so the white space between buttons is even regardless of font metrics.
    def _pill_h(text: str, size: int) -> int:
        return _font(size, True).render(text, True, (255, 255, 255)).get_height() + 22

    GAP = 12
    h_start = _pill_h("TAP TO START", 22)
    h_howto = _pill_h("HOW TO PLAY", 18)
    h_power = _pill_h("POWER-UPS", 18)

    # Anchor the block by its bottom edge, leaving a 14 px buffer above the
    # BEST score panel (which sits at y = H - 110). Centres cascade upward
    # with one shared GAP between every pair.
    y_power = (H - 110) - 14 - h_power // 2
    y_howto = y_power - h_power // 2 - GAP - h_howto // 2
    y_start = y_howto - h_howto // 2 - GAP - h_start // 2

    btn_alpha = int(225 + math.sin(t * 3.6) * 30)
    _pill_btn(surf, (W // 2, y_start), "TAP TO START",
              size=22, alpha=btn_alpha, min_width=220)
    _pill_btn(surf, (W // 2, y_howto), "HOW TO PLAY",
              size=18, alpha=230, min_width=220)
    _pill_btn(surf, (W // 2, y_power), "POWER-UPS",
              size=18, alpha=230, min_width=220)

    # BEST score panel — unchanged from draw_menu (game/hud.py:573-581).
    hi_rect = pygame.Rect(W // 2 - 72, H - 110, 144, 48)
    _dark_panel(surf, hi_rect, radius=14, alpha=190)
    lf = _font(12, False)
    lbl = lf.render("B E S T", True, _GOLD_MUTED)
    lbl.set_alpha(180)
    surf.blit(lbl, lbl.get_rect(center=(W // 2, H - 98)))
    vf = _font(22, True)
    val = vf.render(str(best), True, _GOLD_BRIGHT)
    surf.blit(val, val.get_rect(center=(W // 2, H - 78)))

    return surf


def main() -> int:
    out_dir = os.path.join(_REPO_ROOT, "docs", "menu_preview")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "menu_v1.png")

    surf = render_menu_mockup(t=0.0, best=42)
    pygame.image.save(surf, out_path)
    print(f"wrote {out_path} ({surf.get_width()}x{surf.get_height()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
