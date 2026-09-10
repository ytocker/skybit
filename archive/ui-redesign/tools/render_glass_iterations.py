"""Three refined iterations of the 'Glass' HUD treatment.

Goals over the first pass:
1. Fix the y-overlap between the centre score pill and the side pills
   (top row ends at y=46; score backdrop now starts at y=64).
2. Make the score number bolder — three different treatments to pick
   between (cream-with-gold-rim, gold-on-cream, white-with-deep-shadow).
3. Output at 3× resolution (1080×1920) via smoothscale so reviewing the
   PNGs on a desktop browser doesn't pixelate.

Output:
  docs/screenshots/hud_variants/glass_a.png   cream + gold rim score
  docs/screenshots/hud_variants/glass_b.png   gold-faced score
  docs/screenshots/hud_variants/glass_c.png   white + deep shadow score
  docs/screenshots/hud_variants/glass_compare.png   3-up labelled strip

Run from the repo root:

    PYTHONPATH=. python tools/render_glass_iterations.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

# Reuse the proven dusk backdrop + pillar context from the first pass.
sys.path.insert(0, os.path.dirname(__file__))
from render_hud_variants import draw_bg, draw_pillar_context  # noqa: E402


SCORE = 127
BEST  = 842
COINS = 23

# Layout — top-row bottom is y=46, score band starts at y=64 (18 px gap).
TOP_ROW_Y      = 14
TOP_ROW_H      = 32
SCORE_CENTER_Y = 92
SCORE_BACK_H   = 56  # backdrop height → spans y=64..y=120 with 18 px gap


def _common_glass_pills(surf, best, coins):
    """BEST + coins slabs + glass pause disc, shared by every iteration."""
    from game.config import W
    from game.hud import _PANEL_DARK, _GOLD_BRIGHT, _GOLD_PALE, _coin_icon, _font
    from game.draw import WHITE

    # ── BEST: low-alpha slab + tiny star glyph + gold value
    bp = pygame.Surface((92, TOP_ROW_H), pygame.SRCALPHA)
    pygame.draw.rect(bp, (*_PANEL_DARK, 140), (0, 0, 92, TOP_ROW_H), border_radius=8)
    pygame.draw.rect(bp, (*_GOLD_BRIGHT, 110), (0, 0, 92, TOP_ROW_H),
                     border_radius=8, width=1)
    star = [(11, 8), (13, 13), (18, 13), (14, 16), (16, 21),
            (11, 18), (6, 21), (8, 16), (4, 13), (9, 13)]
    pygame.draw.polygon(bp, (*_GOLD_BRIGHT, 220), star)
    lf = _font(10, True).render("BEST", True, (235, 230, 215))
    bp.blit(lf, lf.get_rect(center=(56, 9)))
    vf = _font(15, True).render(str(best), True, _GOLD_BRIGHT)
    bp.blit(vf, vf.get_rect(center=(56, 21)))
    surf.blit(bp, (10, TOP_ROW_Y))

    # ── Coins: matching slab
    cp = pygame.Surface((86, TOP_ROW_H), pygame.SRCALPHA)
    pygame.draw.rect(cp, (*_PANEL_DARK, 140), (0, 0, 86, TOP_ROW_H), border_radius=8)
    pygame.draw.rect(cp, (*_GOLD_BRIGHT, 110), (0, 0, 86, TOP_ROW_H),
                     border_radius=8, width=1)
    _coin_icon(cp, 14, 16, 9)
    cv = _font(16, True).render(f"x{coins}", True, _GOLD_BRIGHT)
    cp.blit(cv, cv.get_rect(center=(52, 16)))
    surf.blit(cp, (W - 154, TOP_ROW_Y))

    # ── Pause: round glass disc
    px, py = W - 56, 12
    cx, cy = px + 22, py + 22
    disc = pygame.Surface((44, 44), pygame.SRCALPHA)
    pygame.draw.circle(disc, (*_PANEL_DARK, 130), (22, 22), 22)
    pygame.draw.circle(disc, (*_GOLD_BRIGHT, 150), (22, 22), 22, 1)
    pygame.draw.arc(disc, (*_GOLD_PALE, 90),
                    (3, 3, 38, 38), math.pi * 1.1, math.pi * 1.9, 1)
    surf.blit(disc, (px, py))
    pygame.draw.rect(surf, WHITE, (cx - 7, cy - 8, 4, 16), border_radius=2)
    pygame.draw.rect(surf, WHITE, (cx + 3, cy - 8, 4, 16), border_radius=2)


def _glass_score_back(surf, w):
    """Shared score backdrop — translucent dark pill, gold hairline.
    Sized to enclose the numerals; positioned so its top is y≥64 (clear
    of the top-row pills which end at y=46)."""
    from game.config import W
    from game.hud import _PANEL_DARK, _GOLD_BRIGHT
    back = pygame.Surface((w, SCORE_BACK_H), pygame.SRCALPHA)
    pygame.draw.rect(back, (*_PANEL_DARK, 120), (0, 0, w, SCORE_BACK_H),
                     border_radius=SCORE_BACK_H // 2)
    pygame.draw.rect(back, (*_GOLD_BRIGHT, 160), (0, 0, w, SCORE_BACK_H),
                     border_radius=SCORE_BACK_H // 2, width=1)
    # Subtle inner highlight arc on the top half for a glass sheen
    sheen = pygame.Surface((w, SCORE_BACK_H), pygame.SRCALPHA)
    for yy in range(SCORE_BACK_H // 2):
        a = int(20 * (1 - yy / (SCORE_BACK_H / 2)))
        pygame.draw.line(sheen, (255, 245, 220, a), (8, yy + 2), (w - 8, yy + 2))
    back.blit(sheen, (0, 0))
    surf.blit(back, (W // 2 - w // 2, SCORE_CENTER_Y - SCORE_BACK_H // 2))


# ── Iteration A: cream face + gold rim ───────────────────────────────────────
# Bold cream numerals with a 2 px gold rim and a deep shadow. Reads as
# bright + warm, sits comfortably in the glass theme without shouting.

def render_glass_a(surf, score, best, coins):
    from game.config import W
    from game.hud import _GOLD_BRIGHT, _GOLD_DEEP, _font
    from game.draw import NEAR_BLACK

    score_txt = str(score)
    f = _font(48, True)
    img = f.render(score_txt, True, (252, 244, 220))   # warm cream face
    rim = f.render(score_txt, True, _GOLD_DEEP)        # deep gold rim
    sh  = f.render(score_txt, True, NEAR_BLACK)
    r = img.get_rect(center=(W // 2, SCORE_CENTER_Y))

    back_w = max(r.width + 56, 96)
    _glass_score_back(surf, back_w)

    # 2 px gold rim — 8 directions
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)):
        surf.blit(rim, (r.x + ox, r.y + oy))
    sh.set_alpha(180)
    surf.blit(sh, (r.x + 2, r.y + 4))
    surf.blit(img, r.topleft)
    _common_glass_pills(surf, best, coins)


# ── Iteration B: gold face ───────────────────────────────────────────────────
# Score numerals are gold (same value family as BEST and coin x-count),
# with a thin dark outline + drop shadow. Most "in-theme" with the rest
# of the glass HUD since every numeric value reads as gold.

def render_glass_b(surf, score, best, coins):
    from game.config import W
    from game.hud import _GOLD_BRIGHT, _GOLD_DEEP, _font
    from game.draw import NEAR_BLACK

    score_txt = str(score)
    f = _font(48, True)
    img = f.render(score_txt, True, _GOLD_BRIGHT)
    out = f.render(score_txt, True, _GOLD_DEEP)
    sh  = f.render(score_txt, True, NEAR_BLACK)
    r = img.get_rect(center=(W // 2, SCORE_CENTER_Y))

    back_w = max(r.width + 56, 96)
    _glass_score_back(surf, back_w)

    # 1 px deep-gold rim + a stronger 2 px black behind so the gold pops
    # against bright skies.
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        sh.set_alpha(220)
        surf.blit(sh, (r.x + ox, r.y + oy))
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(150)
    surf.blit(sh, (r.x + 2, r.y + 3))
    surf.blit(img, r.topleft)
    _common_glass_pills(surf, best, coins)


# ── Iteration C: white face + deep shadow ────────────────────────────────────
# Keeps the high-contrast white of the original pass but adds a 2 px dark
# outline + soft glow ring underneath so the numerals never blur into
# bright clouds. Bolder than plain white without changing the colour.

def render_glass_c(surf, score, best, coins):
    from game.config import W
    from game.hud import _GOLD_BRIGHT, _font
    from game.draw import WHITE, NEAR_BLACK

    score_txt = str(score)
    f = _font(50, True)
    img = f.render(score_txt, True, WHITE)
    out = f.render(score_txt, True, NEAR_BLACK)
    rim = f.render(score_txt, True, _GOLD_BRIGHT)
    r = img.get_rect(center=(W // 2, SCORE_CENTER_Y))

    back_w = max(r.width + 56, 96)
    _glass_score_back(surf, back_w)

    # Soft dark halo behind the text — a low-alpha bloom that reads as a
    # contact shadow without a hard edge.
    halo = pygame.Surface((r.width + 28, r.height + 18), pygame.SRCALPHA)
    pygame.draw.ellipse(halo, (0, 0, 20, 110), halo.get_rect())
    surf.blit(halo, (r.x - 14, r.y - 6))

    # 2 px dark outline + tiny 1 px gold accent for warmth
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)):
        surf.blit(out, (r.x + ox, r.y + oy))
    for ox, oy in ((-1, -2), (1, -2), (-1, 2), (1, 2)):
        rim.set_alpha(160)
        surf.blit(rim, (r.x + ox, r.y + oy))
    surf.blit(img, r.topleft)
    _common_glass_pills(surf, best, coins)


# ── Main ─────────────────────────────────────────────────────────────────────

ITERATIONS = [
    ("glass_a", "A · cream + gold rim", render_glass_a),
    ("glass_b", "B · gold face",        render_glass_b),
    ("glass_c", "C · white + halo",     render_glass_c),
]

UPSCALE = 3   # 360 × 640 → 1080 × 1920


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    from game.config import W, H
    pygame.display.set_mode((W, H))

    out_dir = os.path.join("docs", "screenshots", "hud_variants")
    os.makedirs(out_dir, exist_ok=True)

    frames: "list[tuple[str, str, pygame.Surface]]" = []

    for slug, label, render in ITERATIONS:
        surf = pygame.Surface((W, H))
        palette = draw_bg(surf, scroll=120.0, phase=0.62)
        draw_pillar_context(surf, palette)
        render(surf, SCORE, BEST, COINS)

        # Upscale for screenshot clarity. smoothscale gives a cleaner
        # output than nearest, which would look pixel-doubled.
        big = pygame.transform.smoothscale(surf, (W * UPSCALE, H * UPSCALE))
        out_path = os.path.join(out_dir, f"{slug}.png")
        pygame.image.save(big, out_path)
        print(f"saved {out_path}  ({W * UPSCALE}x{H * UPSCALE})")
        frames.append((slug, label, big))

    # ── Compare strip: 3 frames tiled horizontally with labels
    GAP = 24
    LABEL_H = 56
    PAD = 32
    cell_w = W * UPSCALE
    cell_h = H * UPSCALE
    n = len(frames)
    canvas_w = cell_w * n + GAP * (n - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((22, 18, 32))
    font = pygame.font.SysFont(None, 56, bold=True)
    for i, (_slug, label, fr) in enumerate(frames):
        x = PAD + i * (cell_w + GAP)
        y = PAD
        pygame.draw.rect(canvas, (200, 170, 90),
                         pygame.Rect(x - 4, y - 4, cell_w + 8, cell_h + 8),
                         width=4)
        canvas.blit(fr, (x, y))
        lbl = font.render(label, True, (240, 210, 130))
        canvas.blit(lbl, (x + (cell_w - lbl.get_width()) // 2, y + cell_h + 12))

    cmp_path = os.path.join(out_dir, "glass_compare.png")
    pygame.image.save(canvas, cmp_path)
    print(f"saved {cmp_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    sys.exit(main() or 0)
