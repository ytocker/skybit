"""Render the two finalist "Power-ups" explainer screens at 1080x1920.

Native 3x render — every coordinate, font size, padding, and stroke
width is multiplied by SCALE so text edges and rounded corners stay
crisp. Both screens reuse the welcome-screen visual language: gold-on-
red outlined title, deep-purple panels with faint orange accent,
twinkling stars, and the exact in-world powerup sprites.

Run from repo root:
    python3 tools/render_powerup_screen_candidates.py
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
import random

import pygame
pygame.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import W, H
from game.draw import (
    rounded_rect, lerp_color,
    UI_CREAM, NEAR_BLACK, WHITE,
)
from game.hud import (
    _font, _draw_overlay_stars,
    _GOLD_BRIGHT, _GOLD_MUTED, _ORANGE_BORDER, _RED_OUTLINE, _PANEL_DARK,
)
from game.entities import PowerUp

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "screenshots", "powerup_screen_candidates")
os.makedirs(OUT_DIR, exist_ok=True)

# Duration is reported once in the footer, never per-row.
POWERUPS = [
    ("triple",   "TRIPLE",   "Coins are worth 3x"),
    ("magnet",   "MAGNET",   "Pulls nearby coins"),
    ("slowmo",   "SLOW-MO",  "Slows the world, jumps are the same"),
    ("kfc",      "KFC",      "Fried chicken theme"),
    ("ghost",    "GHOST",    "Go through pillars safely"),
    ("grow",     "GROW",     "1.5x larger"),
    ("surprise", "SURPRISE", "Picks random from above"),
]

SCALE = 3   # 360x640 → 1080x1920


# ── Hi-res primitives (everything multiplies internal padding/stroke by s) ──
def _gradient_bg(surf):
    TOP = (8, 4, 32)
    MID = (16, 8, 50)
    BOT = (24, 14, 70)
    h = surf.get_height()
    for y in range(h):
        t = y / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(TOP, MID, t * 2)
        else:
            c = lerp_color(MID, BOT, (t - 0.5) * 2)
        pygame.draw.line(surf, c, (0, y), (surf.get_width() - 1, y))


def _seeded_stars(seed, n, sw, sh, top, bot):
    rng = random.Random(seed)
    return [
        (rng.randint(8 * SCALE, sw - 8 * SCALE),
         rng.randint(top, bot),
         rng.choice((1, 1, 1, 2)) * SCALE,
         rng.uniform(0, 6.28))
        for _ in range(n)
    ]


def _outlined_title(surf, txt, center, size, px, shadow_offset):
    f = _font(size, True)
    img = f.render(txt, True, _GOLD_BRIGHT)
    out = f.render(txt, True, _RED_OUTLINE)
    sh = f.render(txt, True, NEAR_BLACK)
    r = img.get_rect(center=center)
    for ox, oy in ((-px, 0), (px, 0), (0, -px), (0, px),
                   (-px, -px), (px, -px), (-px, px), (px, px)):
        surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(170)
    surf.blit(sh, (r.x + shadow_offset[0], r.y + shadow_offset[1]))
    surf.blit(img, r.topleft)


def _dark_panel(surf, rect, radius, alpha):
    rounded_rect(surf, rect, radius, _PANEL_DARK, alpha)
    accent = pygame.Surface((rect.width - radius * 2, 2 * SCALE),
                            pygame.SRCALPHA)
    accent.fill((*_ORANGE_BORDER, 80))
    surf.blit(accent, (rect.x + radius, rect.y + 3 * SCALE))


def _powerup_icon(surf, kind, cx, cy, size_px):
    """Render the in-world PowerUp sprite at native ~28px footprint, then
    smoothscale up to the requested size_px so the procedural detail stays
    pixel-true and edges smooth at high resolution."""
    small = pygame.Surface((64, 64), pygame.SRCALPHA)
    p = PowerUp(32, 32, kind)
    p.pulse = 1.6
    p.draw(small)
    big = pygame.transform.smoothscale(small, (size_px, size_px))
    surf.blit(big, big.get_rect(center=(cx, cy)))


def _wrap(font_obj, blurb, max_w):
    words = blurb.split()
    cur = ""
    lines = []
    for w in words:
        test = (cur + " " + w).strip()
        if font_obj.size(test)[0] <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


def _footer_duration(surf, sw, sh):
    s = SCALE
    pygame.draw.line(surf, (*_ORANGE_BORDER, 110),
                     (sw // 2 - 80 * s, sh - 36 * s),
                     (sw // 2 + 80 * s, sh - 36 * s), s)
    foot = _font(12 * s, True).render("EFFECTS LAST 8 SECONDS",
                                      True, _GOLD_BRIGHT)
    foot.set_alpha(230)
    surf.blit(foot, foot.get_rect(center=(sw // 2, sh - 22 * s)))


def _save(surf, name, sw, sh):
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(surf, path)
    print(f"  saved {os.path.relpath(path)}  ({sw}x{sh})")


# ── Candidate 1: Vertical list ──────────────────────────────────────────────
def candidate_1():
    s = SCALE
    sw, sh = W * s, H * s
    surf = pygame.Surface((sw, sh))
    _gradient_bg(surf)

    _draw_overlay_stars(surf, _seeded_stars(11, 55, sw, sh, 8 * s, sh - 30 * s),
                        t=0.7)

    # Mountain silhouette (scaled).
    mtn = pygame.Surface((sw, sh), pygame.SRCALPHA)
    far = [(0, sh), (0, 490 * s), (60 * s, 420 * s), (120 * s, 450 * s),
           (200 * s, 375 * s), (280 * s, 430 * s),
           (360 * s, 360 * s), (sw, 400 * s), (sw, sh)]
    near = [(0, sh), (0, 530 * s), (80 * s, 505 * s), (160 * s, 520 * s),
            (240 * s, 490 * s), (320 * s, 510 * s), (sw, 495 * s), (sw, sh)]
    pygame.draw.polygon(mtn, (14, 26, 12, 140), far)
    pygame.draw.polygon(mtn, (10, 18, 8, 140), near)
    surf.blit(mtn, (0, 0))

    _outlined_title(surf, "POWER-UPS", (sw // 2, 50 * s),
                    size=38 * s, px=2 * s, shadow_offset=(2 * s, 3 * s))
    sub = _font(11 * s, False).render("GRAB ONE FROM A PILLAR GAP",
                                      True, _GOLD_MUTED)
    sub.set_alpha(190)
    surf.blit(sub, sub.get_rect(center=(sw // 2, 80 * s)))
    pygame.draw.line(surf, (*_ORANGE_BORDER, 110),
                     (sw // 2 - 80 * s, 92 * s),
                     (sw // 2 + 80 * s, 92 * s), s)

    row_h = 58 * s
    row_w = sw - 24 * s
    base_x = 12 * s
    base_y = 108 * s
    icon_size = 40 * s

    for i, (kind, name, blurb) in enumerate(POWERUPS):
        ry = base_y + i * (row_h + 4 * s)
        rect = pygame.Rect(base_x, ry, row_w, row_h)
        _dark_panel(surf, rect, radius=12 * s, alpha=205)

        icon_pad = 8 * s
        icon_rect = pygame.Rect(rect.x + icon_pad,
                                rect.y + (row_h - icon_size) // 2,
                                icon_size, icon_size)
        rounded_rect(surf, icon_rect, 8 * s, (15, 25, 60), 215)
        _powerup_icon(surf, kind,
                      icon_rect.centerx, icon_rect.centery, icon_size)

        text_x = icon_rect.right + 12 * s
        name_img = _font(15 * s, True).render(name, True, _GOLD_BRIGHT)
        surf.blit(name_img, (text_x, rect.y + 8 * s))

        # Bold + slightly larger explanation
        f = _font(13 * s, True)
        max_w = rect.right - text_x - 8 * s
        for li, line in enumerate(_wrap(f, blurb, max_w)[:2]):
            img = f.render(line, True, UI_CREAM)
            surf.blit(img, (text_x, rect.y + 28 * s + li * 16 * s))

    _footer_duration(surf, sw, sh)
    _save(surf, "candidate_1_list.png", sw, sh)


# ── Candidate 2: Card grid (2x3 + surprise footer card) ─────────────────────
def candidate_2():
    s = SCALE
    sw, sh = W * s, H * s
    surf = pygame.Surface((sw, sh))
    _gradient_bg(surf)

    _draw_overlay_stars(surf, _seeded_stars(22, 60, sw, sh, 8 * s, sh - 30 * s),
                        t=1.4)

    _outlined_title(surf, "POWER-UPS", (sw // 2, 46 * s),
                    size=36 * s, px=2 * s, shadow_offset=(2 * s, 3 * s))
    sub = _font(11 * s, False).render("SIX BOOSTS PLUS A WILD CARD",
                                      True, _GOLD_MUTED)
    sub.set_alpha(190)
    surf.blit(sub, sub.get_rect(center=(sw // 2, 76 * s)))

    grid_top = 96 * s
    card_w = 162 * s
    card_h = 124 * s
    gap = 8 * s
    base_x = (sw - (card_w * 2 + gap)) // 2

    six = POWERUPS[:6]
    for idx, (kind, name, blurb) in enumerate(six):
        col = idx % 2
        row = idx // 2
        x = base_x + col * (card_w + gap)
        y = grid_top + row * (card_h + gap)
        card = pygame.Rect(x, y, card_w, card_h)
        _dark_panel(surf, card, radius=14 * s, alpha=215)

        _powerup_icon(surf, kind, card.centerx, card.y + 32 * s, 48 * s)
        nimg = _font(14 * s, True).render(name, True, _GOLD_BRIGHT)
        surf.blit(nimg, nimg.get_rect(center=(card.centerx, card.y + 66 * s)))

        f = _font(12 * s, True)
        for li, line in enumerate(_wrap(f, blurb, card_w - 16 * s)[:3]):
            img = f.render(line, True, UI_CREAM)
            surf.blit(img,
                      img.get_rect(center=(card.centerx,
                                           card.y + 84 * s + li * 14 * s)))

    sy = grid_top + 3 * (card_h + gap) + 4 * s
    surprise_card = pygame.Rect(base_x, sy, card_w * 2 + gap, 64 * s)
    _dark_panel(surf, surprise_card, radius=14 * s, alpha=220)
    _powerup_icon(surf, "surprise",
                  surprise_card.x + 40 * s, surprise_card.centery, 50 * s)
    nimg = _font(15 * s, True).render("SURPRISE", True, _GOLD_BRIGHT)
    surf.blit(nimg, (surprise_card.x + 80 * s, surprise_card.y + 10 * s))

    f = _font(12 * s, True)
    blurb = POWERUPS[-1][2]
    text_left = surprise_card.x + 80 * s
    text_right = surprise_card.right - 12 * s
    for li, line in enumerate(_wrap(f, blurb, text_right - text_left)[:2]):
        img = f.render(line, True, UI_CREAM)
        surf.blit(img, (text_left, surprise_card.y + 32 * s + li * 14 * s))

    _footer_duration(surf, sw, sh)
    _save(surf, "candidate_2_grid.png", sw, sh)


def main():
    candidate_1()
    candidate_2()
    print(f"\nDone. Output dir: {OUT_DIR}")


if __name__ == "__main__":
    main()
