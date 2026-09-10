"""Render the main-menu BEST + TOP 10 panels in four treatments so the
user can pick which one to wire into ``HUD.draw_menu``.

Output:
  docs/screenshots/menu_variants/v0_current.png    today's look (baseline)
  docs/screenshots/menu_variants/v1_emboss.png     heavier alpha + emboss
  docs/screenshots/menu_variants/v2_scarlet.png    scarlet gradient cards
  docs/screenshots/menu_variants/v3_bronze.png     double border + rivets
  docs/screenshots/menu_variants/menu_compare.png  4-up labelled strip

The rest of the menu (sky, stars, mountains, title, buttons) is
reproduced from ``HUD.draw_menu`` so the panels appear in real context.

Run from the repo root:

    PYTHONPATH=. python tools/render_menu_panels.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))
from render_hud_variants import draw_bg  # noqa: E402


BEST = 842
UPSCALE = 3


# ── Backdrop + menu chrome (everything except the two bottom panels) ────────

def render_menu_chrome(surf, hud):
    from game.config import W, H
    from game.hud import (
        _outlined_text, _pill_btn, _font,
        _draw_overlay_stars, _draw_mountain_silhouette,
        _ORANGE_BORDER,
    )
    from game.draw import WHITE

    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 110))
    surf.blit(dim, (0, 0))
    _draw_overlay_stars(surf, hud._stars, hud.title_t)
    _draw_mountain_silhouette(surf, alpha=180)

    pulse = 1.0 + math.sin(hud.title_t * 2.4) * 0.04
    float_y = int(7 * math.sin(hud.title_t * 1.8))
    _outlined_text(surf, "SKYBIT", (W // 2, 126 + float_y),
                   size=int(72 * pulse), px=3)
    _outlined_text(surf, "POCKET  SKY  FLYER", (W // 2, 184),
                   size=22, px=2, shadow_offset=(2, 3))
    pygame.draw.line(surf, (*_ORANGE_BORDER, 120),
                     (W // 2 - 70, 208), (W // 2 + 70, 208), 1)

    def _pill_h(text, size):
        return _font(size, True).render(text, True, WHITE).get_height() + 22

    GAP = 12
    h_start = _pill_h("START", 22)
    h_howto = _pill_h("HOW TO PLAY", 18)
    h_power = _pill_h("POWER-UPS", 18)
    y_power = (H - 110) - 14 - h_power // 2
    y_howto = y_power - h_power // 2 - GAP - h_howto // 2
    y_start = y_howto - h_howto // 2 - GAP - h_start // 2

    btn_alpha = int(225 + math.sin(hud.title_t * 3.6) * 30)
    _pill_btn(surf, (W // 2, y_start), "START",
              size=22, alpha=btn_alpha, min_width=220, primary=True, dim=True)
    _pill_btn(surf, (W // 2, y_howto), "HOW TO PLAY",
              size=18, alpha=230, min_width=220, dim=True)
    _pill_btn(surf, (W // 2, y_power), "POWER-UPS",
              size=18, alpha=230, min_width=220, dim=True)


# ── Panel layout (same across variants) ──────────────────────────────────────

PANEL_W = 132
PANEL_H = 48
GAP     = 8


def panel_rects():
    from game.config import W, H
    total_w = PANEL_W * 2 + GAP
    left_x = (W - total_w) // 2
    cy = H - 86
    best_rect = pygame.Rect(left_x, cy - PANEL_H // 2, PANEL_W, PANEL_H)
    top_rect  = pygame.Rect(left_x + PANEL_W + GAP, cy - PANEL_H // 2,
                            PANEL_W, PANEL_H)
    return best_rect, top_rect, cy


# ── V0 · Current (baseline) ──────────────────────────────────────────────────

def render_v0_current(surf, best):
    from game.hud import _dark_panel, _draw_trophy, _GOLD_MUTED, _GOLD_BRIGHT, _font
    br, tr, cy = panel_rects()
    lf = _font(12, True)
    vf = _font(22, True)
    _dark_panel(surf, br, radius=14, alpha=190)
    lbl = lf.render("B E S T", True, _GOLD_MUTED); lbl.set_alpha(180)
    surf.blit(lbl, lbl.get_rect(center=(br.centerx, cy - 12)))
    val = vf.render(str(best), True, _GOLD_BRIGHT)
    surf.blit(val, val.get_rect(center=(br.centerx, cy + 8)))
    _dark_panel(surf, tr, radius=14, alpha=190)
    tl = lf.render("T O P  10", True, _GOLD_MUTED); tl.set_alpha(180)
    surf.blit(tl, tl.get_rect(center=(tr.centerx, cy - 12)))
    _draw_trophy(surf, tr.centerx, cy + 10, 9)


# ── V1 · Heavier emboss ──────────────────────────────────────────────────────
# Same dark-navy panel but pushed up: alpha 235, 2 px gold border, inner
# top highlight, inner bottom shadow, prominent drop shadow. Reads as a
# solid embossed plaque.

def render_v1_emboss(surf, best):
    from game.hud import (
        _PANEL_DARK, _PANEL_LIGHTER, _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE,
        _GOLD_MUTED, _draw_trophy, _font,
    )

    def card(rect):
        # Heavy drop shadow
        sh = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
        for k in range(4):
            a = 80 - k * 16
            pygame.draw.rect(sh, (0, 0, 0, a),
                             (k, k * 2, rect.width + 8 - k * 2,
                              rect.height + 8 - k * 2),
                             border_radius=14)
        surf.blit(sh, (rect.x - 4, rect.y + 2))
        # Body
        pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
        # Gradient from PANEL_LIGHTER (top) to PANEL_DARK (bottom)
        for yy in range(rect.height):
            t = yy / max(1, rect.height - 1)
            r = int(_PANEL_LIGHTER[0] * (1 - t) + _PANEL_DARK[0] * t)
            g = int(_PANEL_LIGHTER[1] * (1 - t) + _PANEL_DARK[1] * t)
            b = int(_PANEL_LIGHTER[2] * (1 - t) + _PANEL_DARK[2] * t)
            pygame.draw.line(pnl, (r, g, b, 235),
                             (0, yy), (rect.width - 1, yy))
        # Rounded mask
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         (0, 0, rect.width, rect.height), border_radius=14)
        pnl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # 2 px gold border
        pygame.draw.rect(pnl, _GOLD_BRIGHT, (0, 0, rect.width, rect.height),
                         width=2, border_radius=14)
        # Inner top highlight + bottom shadow for emboss
        pygame.draw.line(pnl, (*_GOLD_PALE, 140), (10, 3), (rect.width - 10, 3), 1)
        pygame.draw.line(pnl, (0, 0, 0, 80),
                         (10, rect.height - 4),
                         (rect.width - 10, rect.height - 4), 1)
        surf.blit(pnl, rect.topleft)

    br, tr, cy = panel_rects()
    lf = _font(13, True)
    vf = _font(24, True)
    card(br)
    lbl = lf.render("B E S T", True, _GOLD_PALE); lbl.set_alpha(230)
    surf.blit(lbl, lbl.get_rect(center=(br.centerx, cy - 12)))
    val = vf.render(str(best), True, _GOLD_BRIGHT)
    surf.blit(val, val.get_rect(center=(br.centerx, cy + 9)))
    card(tr)
    tl = lf.render("T O P  10", True, _GOLD_PALE); tl.set_alpha(230)
    surf.blit(tl, tl.get_rect(center=(tr.centerx, cy - 12)))
    # Match the position wired into HUD.draw_menu so this preview stays
    # in sync with the live menu.
    _draw_trophy(surf, tr.centerx, cy + 6, 9)


# ── V2 · Scarlet cards ───────────────────────────────────────────────────────
# Borrow the scarlet gradient pill body from the menu buttons but in
# rectangular card form. Bold and cohesive with the START button.

def render_v2_scarlet(surf, best):
    from game.hud import (
        _SCARLET_TOP, _SCARLET_BOT, _SCARLET_SHADOW,
        _GOLD_BRIGHT, _GOLD_PALE, _draw_trophy, _font,
    )
    from game.draw import lerp_color

    def card(rect):
        # Drop shadow
        sh = pygame.Surface((rect.width + 4, rect.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 110),
                         (0, 0, rect.width + 4, rect.height + 6),
                         border_radius=14)
        surf.blit(sh, (rect.x - 2, rect.y + 4))
        # Scarlet gradient body
        pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
        for yy in range(rect.height):
            c = lerp_color(_SCARLET_TOP, _SCARLET_BOT, yy / max(1, rect.height - 1))
            pygame.draw.line(pnl, c, (0, yy), (rect.width - 1, yy))
        # Cream frost on the top half
        frost = pygame.Surface(rect.size, pygame.SRCALPHA)
        for yy in range(rect.height // 2):
            a = int(48 * (1 - yy / (rect.height / 2)))
            pygame.draw.line(frost, (255, 245, 220, a),
                             (0, yy), (rect.width, yy))
        pnl.blit(frost, (0, 0))
        # Rounded mask
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         (0, 0, rect.width, rect.height), border_radius=14)
        pnl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # Gold border + thin inner accent
        pygame.draw.rect(pnl, _GOLD_BRIGHT, (0, 0, rect.width, rect.height),
                         width=2, border_radius=14)
        pygame.draw.line(pnl, (*_GOLD_BRIGHT, 130),
                         (12, 4), (rect.width - 12, 4), 1)
        surf.blit(pnl, rect.topleft)

    br, tr, cy = panel_rects()
    lf = _font(13, True)
    vf = _font(24, True)

    def cream_text(text, font, center, color=(255, 245, 220)):
        img = font.render(text, True, color)
        sh  = font.render(text, True, _SCARLET_SHADOW); sh.set_alpha(220)
        r = img.get_rect(center=center)
        surf.blit(sh, (r.x + 1, r.y + 1))
        surf.blit(img, r.topleft)

    card(br)
    cream_text("B E S T", lf, (br.centerx, cy - 12), _GOLD_PALE)
    cream_text(str(best), vf, (br.centerx, cy + 9))
    card(tr)
    cream_text("T O P  10", lf, (tr.centerx, cy - 12), _GOLD_PALE)
    _draw_trophy(surf, tr.centerx, cy + 11, 10)


# ── V3 · Bronze with rivets ──────────────────────────────────────────────────
# High-alpha dark panel + double gold border (bright outer + deep inner)
# + four corner rivets. Reads as an engraved bronze plaque.

def render_v3_bronze(surf, best):
    from game.hud import (
        _PANEL_DARK, _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE,
        _draw_trophy, _font,
    )

    def card(rect):
        # Heavy drop shadow
        sh = pygame.Surface((rect.width + 6, rect.height + 8), pygame.SRCALPHA)
        for k in range(3):
            a = 95 - k * 25
            pygame.draw.rect(sh, (0, 0, 0, a),
                             (k, k + 2, rect.width + 6 - k * 2,
                              rect.height + 8 - k * 2),
                             border_radius=12)
        surf.blit(sh, (rect.x - 3, rect.y + 3))
        # Body
        pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(pnl, (*_PANEL_DARK, 235),
                         (0, 0, rect.width, rect.height), border_radius=12)
        # Double gold border
        pygame.draw.rect(pnl, _GOLD_BRIGHT, (0, 0, rect.width, rect.height),
                         width=2, border_radius=12)
        pygame.draw.rect(pnl, _GOLD_DEEP,
                         (4, 4, rect.width - 8, rect.height - 8),
                         width=1, border_radius=8)
        # Inner sheen line just under the top edge
        pygame.draw.line(pnl, (*_GOLD_PALE, 150),
                         (10, 8), (rect.width - 10, 8), 1)
        # Four corner rivets (inside the inner border)
        for (rx, ry) in ((9, 9), (rect.width - 10, 9),
                         (9, rect.height - 10), (rect.width - 10, rect.height - 10)):
            pygame.draw.circle(pnl, _GOLD_BRIGHT, (rx, ry), 2)
            pygame.draw.circle(pnl, _GOLD_DEEP, (rx, ry), 2, 1)
        surf.blit(pnl, rect.topleft)

    br, tr, cy = panel_rects()
    lf = _font(13, True)
    vf = _font(24, True)
    card(br)
    lbl = lf.render("B E S T", True, _GOLD_PALE); lbl.set_alpha(235)
    surf.blit(lbl, lbl.get_rect(center=(br.centerx, cy - 11)))
    val = vf.render(str(best), True, _GOLD_BRIGHT)
    surf.blit(val, val.get_rect(center=(br.centerx, cy + 10)))
    card(tr)
    tl = lf.render("T O P  10", True, _GOLD_PALE); tl.set_alpha(235)
    surf.blit(tl, tl.get_rect(center=(tr.centerx, cy - 11)))
    _draw_trophy(surf, tr.centerx, cy + 12, 10)


# ── Main ─────────────────────────────────────────────────────────────────────

VARIANTS = [
    ("v0_current", "V0 · current",      render_v0_current),
    ("v1_emboss",  "V1 · heavy emboss", render_v1_emboss),
    ("v2_scarlet", "V2 · scarlet card", render_v2_scarlet),
    ("v3_bronze",  "V3 · bronze rivets", render_v3_bronze),
]


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    from game.config import W, H
    from game.hud import HUD
    pygame.display.set_mode((W, H))

    out_dir = os.path.join("docs", "screenshots", "menu_variants")
    os.makedirs(out_dir, exist_ok=True)

    frames: "list[tuple[str, str, pygame.Surface]]" = []

    for slug, label, render in VARIANTS:
        random.seed(42)
        surf = pygame.Surface((W, H))
        draw_bg(surf, scroll=120.0, phase=0.62)
        hud = HUD()
        hud.title_t = 0.0
        render_menu_chrome(surf, hud)
        render(surf, BEST)

        big = pygame.transform.smoothscale(surf, (W * UPSCALE, H * UPSCALE))
        out_path = os.path.join(out_dir, f"{slug}.png")
        pygame.image.save(big, out_path)
        print(f"saved {out_path}  ({W * UPSCALE}x{H * UPSCALE})")
        frames.append((slug, label, big))

    # Compare strip
    GAP_PX = 24
    LABEL_H = 56
    PAD = 32
    cell_w = W * UPSCALE
    cell_h = H * UPSCALE
    n = len(frames)
    canvas_w = cell_w * n + GAP_PX * (n - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((22, 18, 32))
    font = pygame.font.SysFont(None, 56, bold=True)
    for i, (_slug, label, fr) in enumerate(frames):
        x = PAD + i * (cell_w + GAP_PX)
        y = PAD
        pygame.draw.rect(canvas, (200, 170, 90),
                         pygame.Rect(x - 4, y - 4, cell_w + 8, cell_h + 8), width=4)
        canvas.blit(fr, (x, y))
        lbl = font.render(label, True, (240, 210, 130))
        canvas.blit(lbl, (x + (cell_w - lbl.get_width()) // 2, y + cell_h + 12))

    cmp_path = os.path.join(out_dir, "menu_compare.png")
    pygame.image.save(canvas, cmp_path)
    print(f"saved {cmp_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    sys.exit(main() or 0)
