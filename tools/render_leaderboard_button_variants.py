"""Render 5 design variants of a trophy button placed next to the BEST
score panel on the main menu. Each variant is rendered as a full-menu
PNG so the variants can be compared in context (and the user can pick
one before any game code changes).

Writes:
  docs/leaderboard_button/v1_compact_square.png
  docs/leaderboard_button/v2_round_medallion.png
  docs/leaderboard_button/v3_twin_panel.png
  docs/leaderboard_button/v4_integrated.png
  docs/leaderboard_button/v5_floating_trophy.png
  docs/leaderboard_button/contact_sheet.png   (2x3 grid for side-by-side)

Run headless from the repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
      python3 tools/render_leaderboard_button_variants.py
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

pygame.init()
pygame.font.init()

from game.config import W, H  # noqa: E402
from game.hud import (  # noqa: E402
    HUD,
    _outlined_text,
    _pill_btn,
    _dark_panel,
    _draw_overlay_stars,
    _draw_mountain_silhouette,
    _draw_trophy,
    _font,
    _GOLD_BRIGHT,
    _GOLD_MUTED,
    _ORANGE_BORDER,
    _PANEL_DARK,
)
from game.draw import rounded_rect, WHITE  # noqa: E402


# ── Shared menu backdrop (everything except the BEST row) ────────────────────

def render_menu_base(t: float = 0.0) -> pygame.Surface:
    """Paint title + pills + sky + mountains. The BEST row is variant-specific
    so it's drawn by each render_vN function on top of this canvas."""
    surf = pygame.Surface((W, H))
    surf.fill((6, 1, 21))

    hud = HUD()
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 110))
    surf.blit(dim, (0, 0))

    _draw_overlay_stars(surf, hud._stars, t)
    _draw_mountain_silhouette(surf, alpha=180)

    pulse = 1.0 + math.sin(t * 2.4) * 0.04
    float_y = int(7 * math.sin(t * 1.8))
    _outlined_text(surf, "SKYBIT", (W // 2, 126 + float_y),
                   size=int(72 * pulse), px=3)
    _outlined_text(surf, "POCKET SKY FLYER", (W // 2, 184),
                   size=22, px=2, shadow_offset=(2, 3))
    pygame.draw.line(surf, (*_ORANGE_BORDER, 120),
                     (W // 2 - 70, 208), (W // 2 + 70, 208), 1)

    def _pill_h(text: str, size: int) -> int:
        return _font(size, True).render(text, True, WHITE).get_height() + 22

    GAP = 12
    h_start = _pill_h("TAP TO START", 22)
    h_howto = _pill_h("HOW TO PLAY", 18)
    h_power = _pill_h("POWER-UPS", 18)
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

    return surf


def _draw_best_panel(surf, cx, cy, best, panel_w=144):
    """Helper: draw the BEST score panel centered on (cx, cy)."""
    hi_rect = pygame.Rect(cx - panel_w // 2, cy - 24, panel_w, 48)
    _dark_panel(surf, hi_rect, radius=14, alpha=190)
    lf = _font(12, False)
    lbl = lf.render("B E S T", True, _GOLD_MUTED)
    lbl.set_alpha(180)
    surf.blit(lbl, lbl.get_rect(center=(cx, cy - 12)))
    vf = _font(22, True)
    val = vf.render(str(best), True, _GOLD_BRIGHT)
    surf.blit(val, val.get_rect(center=(cx, cy + 8)))
    return hi_rect


# ── V1 — Compact square button on the right ──────────────────────────────────
def render_v1(t=0.0, best=42):
    """Minimalist 48x48 dark square with trophy icon. Matches the
    top-corner pause-button language; sits flush against the BEST panel
    with 8px gap. The pair is centered on screen."""
    surf = render_menu_base(t)
    btn_size = 48
    gap = 8
    best_w = 144
    total_w = best_w + gap + btn_size
    left_x = (W - total_w) // 2
    cy = H - 86
    _draw_best_panel(surf, left_x + best_w // 2, cy, best)
    bx = left_x + best_w + gap
    btn_rect = pygame.Rect(bx, cy - btn_size // 2, btn_size, btn_size)
    rounded_rect(surf, btn_rect, 12, _PANEL_DARK, 190)
    border = pygame.Surface((btn_size, btn_size), pygame.SRCALPHA)
    pygame.draw.rect(border, (*_ORANGE_BORDER, 120),
                     (0, 0, btn_size, btn_size),
                     border_radius=12, width=1)
    surf.blit(border, btn_rect.topleft)
    _draw_trophy(surf, btn_rect.centerx, btn_rect.centery, 10)
    return surf


# ── V2 — Round gold-rim medallion ────────────────────────────────────────────
def render_v2(t=0.0, best=42):
    """Circular dark button with a thick gold outer ring + thin orange
    inner ring. Feels like a 'medal' — the trophy sits a touch larger
    inside the disc."""
    surf = render_menu_base(t)
    radius = 26
    gap = 10
    best_w = 144
    total_w = best_w + gap + radius * 2
    left_x = (W - total_w) // 2
    cy = H - 86
    _draw_best_panel(surf, left_x + best_w // 2, cy, best)
    btn_cx = left_x + best_w + gap + radius
    # Soft drop shadow disc
    shadow = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
    pygame.draw.circle(shadow, (0, 0, 0, 80),
                       (radius + 3, radius + 3), radius + 1)
    surf.blit(shadow, (btn_cx - radius - 3, cy - radius - 1))
    # Outer gold ring → dark inside → thin orange detail ring
    pygame.draw.circle(surf, _GOLD_BRIGHT, (btn_cx, cy), radius)
    pygame.draw.circle(surf, _PANEL_DARK, (btn_cx, cy), radius - 3)
    pygame.draw.circle(surf, _ORANGE_BORDER, (btn_cx, cy), radius - 4, 1)
    _draw_trophy(surf, btn_cx, cy, 11)
    return surf


# ── V3 — Twin matching panels (BEST | TOP 10) ───────────────────────────────
def render_v3(t=0.0, best=42):
    """Two same-style panels side by side. Right panel mirrors BEST's
    label/value layout: 'T O P  10' label on top, trophy icon below
    in the value slot. Symmetric and reads as a pair."""
    surf = render_menu_base(t)
    panel_w = 132
    gap = 8
    total_w = panel_w * 2 + gap
    left_x = (W - total_w) // 2
    cy = H - 86
    best_cx = left_x + panel_w // 2
    top_cx = left_x + panel_w + gap + panel_w // 2
    _draw_best_panel(surf, best_cx, cy, best, panel_w=panel_w)
    # TOP 10 panel
    top_rect = pygame.Rect(top_cx - panel_w // 2, cy - 24, panel_w, 48)
    _dark_panel(surf, top_rect, radius=14, alpha=190)
    lf = _font(12, False)
    lbl = lf.render("T O P  10", True, _GOLD_MUTED)
    lbl.set_alpha(180)
    surf.blit(lbl, lbl.get_rect(center=(top_cx, cy - 12)))
    _draw_trophy(surf, top_cx, cy + 10, 9)
    return surf


# ── V4 — Integrated wide panel: trophy | divider | BEST ──────────────────────
def render_v4(t=0.0, best=42):
    """One unified panel that fuses the trophy and BEST score behind a
    single dark plate, separated by a slim orange divider. The trophy
    section is the clickable hot-zone; the whole thing reads as one
    UI element."""
    surf = render_menu_base(t)
    panel_w = 204
    panel_h = 48
    panel_x = (W - panel_w) // 2
    cy = H - 86
    rect = pygame.Rect(panel_x, cy - panel_h // 2, panel_w, panel_h)
    _dark_panel(surf, rect, radius=14, alpha=200)
    # Left section: trophy
    trophy_section_w = 60
    trophy_cx = panel_x + trophy_section_w // 2
    _draw_trophy(surf, trophy_cx, cy, 12)
    # Slim divider
    div_x = panel_x + trophy_section_w
    pygame.draw.line(surf, (*_ORANGE_BORDER, 100),
                     (div_x, cy - 16), (div_x, cy + 16), 1)
    # Right section: BEST + score
    best_section_cx = div_x + (panel_w - trophy_section_w) // 2
    lf = _font(12, False)
    lbl = lf.render("B E S T", True, _GOLD_MUTED)
    lbl.set_alpha(180)
    surf.blit(lbl, lbl.get_rect(center=(best_section_cx, cy - 12)))
    vf = _font(22, True)
    val = vf.render(str(best), True, _GOLD_BRIGHT)
    surf.blit(val, val.get_rect(center=(best_section_cx, cy + 8)))
    return surf


# ── V5 — Floating decorative trophy with glow halo ───────────────────────────
def render_v5(t=0.0, best=42):
    """No rectangular container — just a larger trophy floating in a
    soft gold halo with a tiny 'TOP 10' caption beneath. Most
    decorative of the five; reads as a 'monument' rather than a button."""
    surf = render_menu_base(t)
    badge_w = 64
    gap = 14
    best_w = 144
    total_w = best_w + gap + badge_w
    left_x = (W - total_w) // 2
    cy = H - 86
    _draw_best_panel(surf, left_x + best_w // 2, cy, best)
    btn_cx = left_x + best_w + gap + badge_w // 2
    # Halo: stacked translucent gold discs that fade outward
    halo = pygame.Surface((80, 80), pygame.SRCALPHA)
    hcx = hcy = 40
    for r, a in ((34, 16), (30, 28), (26, 44), (22, 64), (18, 92)):
        pygame.draw.circle(halo, (*_GOLD_BRIGHT, a), (hcx, hcy), r)
    surf.blit(halo, (btn_cx - 40, cy - 40 - 4))
    # Trophy slightly above center to leave room for caption
    _draw_trophy(surf, btn_cx, cy - 6, 13)
    # Small caption under trophy
    cf = _font(9, True)
    cap = cf.render("TOP 10", True, _GOLD_BRIGHT)
    surf.blit(cap, cap.get_rect(center=(btn_cx, cy + 18)))
    return surf


# ── Output ───────────────────────────────────────────────────────────────────

def _label_strip(width: int, height: int, text: str) -> pygame.Surface:
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    s.fill((10, 6, 28, 230))
    f = _font(14, True)
    img = f.render(text, True, _GOLD_BRIGHT)
    s.blit(img, img.get_rect(center=(width // 2, height // 2)))
    return s


def render_contact_sheet(variants) -> pygame.Surface:
    """2-cols x 3-rows grid; last cell is left blank for spacing. Each
    cell shows a half-scale (180x320) variant with its caption above."""
    cell_w, cell_h = W // 2, H // 2
    label_h = 22
    cols, rows = 2, 3
    sheet = pygame.Surface((cols * cell_w, rows * (cell_h + label_h)))
    sheet.fill((4, 2, 14))
    for i, (name, fn, caption) in enumerate(variants):
        r = i // cols
        c = i % cols
        x = c * cell_w
        y = r * (cell_h + label_h)
        sheet.blit(_label_strip(cell_w, label_h, caption), (x, y))
        thumb = pygame.transform.smoothscale(fn(t=0.0, best=42), (cell_w, cell_h))
        sheet.blit(thumb, (x, y + label_h))
    return sheet


def main() -> int:
    out_dir = os.path.join(_REPO_ROOT, "docs", "leaderboard_button")
    os.makedirs(out_dir, exist_ok=True)
    variants = [
        ("v1_compact_square.png", render_v1, "V1 — Compact square"),
        ("v2_round_medallion.png", render_v2, "V2 — Round medallion"),
        ("v3_twin_panel.png", render_v3, "V3 — Twin panel"),
        ("v4_integrated.png", render_v4, "V4 — Integrated"),
        ("v5_floating_trophy.png", render_v5, "V5 — Floating trophy"),
    ]
    for name, fn, _ in variants:
        surf = fn(t=0.0, best=42)
        path = os.path.join(out_dir, name)
        pygame.image.save(surf, path)
        print(f"  wrote {path}")

    sheet = render_contact_sheet(variants)
    sheet_path = os.path.join(out_dir, "contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"  wrote {sheet_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
