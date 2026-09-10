"""Render 5 power-up strip variants for the run-summary screen.

Each variant produces a full 720x1280 (2x) screenshot of the run
summary, varying only the styling of the POWER-UPS USED strip so
the player can pick which treatment lands. A contact sheet stitches
all five together for side-by-side comparison.

Run headless from the repo root:

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/gen_powerup_variants.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from game.config import W, H  # noqa: E402
from game.draw import lerp_color, NEAR_BLACK  # noqa: E402
from game.hud import (  # noqa: E402
    _font,
    _outlined_text,
    _score_plaque,
    _stat_tile_chunky,
    _outline_pill_btn,
    _pill_btn,
    _draw_overlay_stars,
    _draw_mountain_silhouette,
    _GOLD_BRIGHT,
    _GOLD_MUTED,
    _PANEL_DARK,
    _PANEL_LIGHTER,
    _NIGHT_DEEP,
)
from game.powerup_help import _powerup_icon  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "docs", "run_summary_redesign")
SCALE = 2


class FakeWorld:
    score = 23
    time_alive = 87.0
    coin_count = 11
    coins_spawned = 18
    coins: list = []
    pillars_passed = 23
    flap_count = 127
    powerups_picked = {
        "triple": 3, "magnet": 2, "slowmo": 1, "kfc": 1, "ghost": 1,
        "grow": 0, "reverse": 0, "surprise": 0,
    }


# ── helpers shared by the variants ───────────────────────────────────────────

def _caption(surf, y):
    cap = _font(13, True).render(
        "P O W E R - U P S   U S E D", True, _GOLD_MUTED)
    cap.set_alpha(230)
    surf.blit(cap, cap.get_rect(center=(W // 2, y)))


def _count_with_shadow(surf, text, center, size=14, color=_GOLD_BRIGHT,
                       shadow_alpha=200, shadow_offset=(1, 1)):
    cf = _font(size, True).render(text, True, color)
    cs = _font(size, True).render(text, True, NEAR_BLACK)
    cs.set_alpha(shadow_alpha)
    cr = cf.get_rect(center=center)
    surf.blit(cs, (cr.x + shadow_offset[0], cr.y + shadow_offset[1]))
    surf.blit(cf, cr)


# ── variant A: Bumped Uniform ────────────────────────────────────────────────

def draw_strip_a(surf, pu, cap_y):
    """Same row layout, bigger icons (+30%), bolder count w/ shadow."""
    _caption(surf, cap_y)
    icon_logical = 28
    icon_box = icon_logical * 2
    gap = 6
    pitch = icon_box + gap
    row_w = len(pu) * icon_box + max(0, len(pu) - 1) * gap
    sx = (W - row_w) // 2 + icon_box // 2
    icon_cy = cap_y + 36
    for i, (kind, count) in enumerate(pu):
        cx = sx + i * pitch
        _powerup_icon(surf, kind, cx, icon_cy, int(icon_logical * 1.7))
        _count_with_shadow(
            surf, f"x{count}",
            (cx, icon_cy + int(icon_logical * 1.18)),
            size=14)


# ── variant B: Big Icon + Corner Badge ───────────────────────────────────────

def draw_strip_b(surf, pu, cap_y):
    """Larger icons; count as a navy gold-bordered badge clipped to
    the bottom-right of each icon."""
    _caption(surf, cap_y)
    icon_logical = 30
    icon_box = icon_logical * 2
    gap = 6
    pitch = icon_box + gap
    row_w = len(pu) * icon_box + max(0, len(pu) - 1) * gap
    sx = (W - row_w) // 2 + icon_box // 2
    icon_cy = cap_y + 44
    for i, (kind, count) in enumerate(pu):
        cx = sx + i * pitch
        _powerup_icon(surf, kind, cx, icon_cy, int(icon_logical * 1.7))
        bw, bh = 30, 20
        bx = cx + icon_logical - 6
        by = icon_cy + icon_logical - 4
        body = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.rect(body, (*_PANEL_DARK, 250),
                         (0, 0, bw, bh), border_radius=bh // 2)
        pygame.draw.rect(body, _GOLD_BRIGHT, (0, 0, bw, bh),
                         width=1, border_radius=bh // 2)
        surf.blit(body, (bx - bw // 2, by - bh // 2))
        cf = _font(13, True).render(f"x{count}", True, _GOLD_BRIGHT)
        surf.blit(cf, cf.get_rect(center=(bx, by)))


# ── variant C: Horizontal Pill Chips ─────────────────────────────────────────

def draw_strip_c(surf, pu, cap_y):
    """Each power-up rendered as a navy/gold horizontal pill: icon
    on the left, ×N on the right. Strong text legibility."""
    _caption(surf, cap_y)
    chip_h = 40
    icon_size = 30
    chip_radius = chip_h // 2
    pad_l, pad_r = 4, 10
    chips = []
    for kind, count in pu:
        tf = _font(16, True).render(f"x{count}", True, _GOLD_BRIGHT)
        chip_w = pad_l + icon_size + 4 + tf.get_width() + pad_r
        chips.append((kind, count, chip_w, tf))
    gap = 6
    total = sum(c[2] for c in chips) + gap * (len(chips) - 1)
    sx = (W - total) // 2
    y = cap_y + 38
    for kind, count, chip_w, tf in chips:
        body = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
        for yy in range(chip_h):
            t = yy / max(1, chip_h - 1)
            c = lerp_color(_PANEL_LIGHTER, _PANEL_DARK, t)
            pygame.draw.line(body, (*c, 245), (0, yy), (chip_w, yy))
        mask = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         (0, 0, chip_w, chip_h),
                         border_radius=chip_radius)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        pygame.draw.rect(body, _GOLD_BRIGHT, (0, 0, chip_w, chip_h),
                         width=1, border_radius=chip_radius)
        surf.blit(body, (sx, y - chip_h // 2))
        _powerup_icon(surf, kind,
                      sx + pad_l + icon_size // 2 + 2, y,
                      int(icon_size * 1.5))
        surf.blit(tf, tf.get_rect(midright=(sx + chip_w - pad_r, y)))
        sx += chip_w + gap


# ── variant D: Tile Cards ────────────────────────────────────────────────────

def draw_strip_d(surf, pu, cap_y):
    """Mini stat-tile per power-up — visually consistent with the
    TIME/COINS/PILLARS/FLAPS tiles above. Each card has the same
    gradient/border/bevel."""
    _caption(surf, cap_y)
    tile_w, tile_h = 50, 64
    gap = 6
    total = len(pu) * tile_w + (len(pu) - 1) * gap
    sx = (W - total) // 2
    y = cap_y + 18
    for i, (kind, count) in enumerate(pu):
        r = pygame.Rect(sx + i * (tile_w + gap), y, tile_w, tile_h)
        body = pygame.Surface(r.size, pygame.SRCALPHA)
        for yy in range(r.h):
            t = yy / max(1, r.h - 1)
            c = lerp_color(_PANEL_LIGHTER, _PANEL_DARK, t)
            pygame.draw.line(body, (*c, 245), (0, yy), (r.w, yy))
        mask = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         (0, 0, r.w, r.h), border_radius=8)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        pygame.draw.rect(body, (*_GOLD_BRIGHT, 160), (0, 0, r.w, r.h),
                         width=1, border_radius=8)
        surf.blit(body, r.topleft)
        _powerup_icon(surf, kind, r.centerx, r.y + 22, int(26 * 1.5))
        _count_with_shadow(surf, f"x{count}",
                           (r.centerx, r.y + r.h - 14),
                           size=15)


# ── variant E: Bold Outlined Stack ───────────────────────────────────────────

def draw_strip_e(surf, pu, cap_y):
    """Big icons + outlined gold-on-red ×N matching the RUN SUMMARY
    title treatment. Loudest variant — the count visually anchors."""
    _caption(surf, cap_y)
    icon_logical = 28
    icon_box = icon_logical * 2
    gap = 6
    pitch = icon_box + gap
    row_w = len(pu) * icon_box + max(0, len(pu) - 1) * gap
    sx = (W - row_w) // 2 + icon_box // 2
    icon_cy = cap_y + 40
    for i, (kind, count) in enumerate(pu):
        cx = sx + i * pitch
        _powerup_icon(surf, kind, cx, icon_cy, int(icon_logical * 1.7))
        _outlined_text(surf, f"x{count}",
                       (cx, icon_cy + icon_logical + 12),
                       size=17, px=2, shadow_offset=(1, 2))


VARIANTS = [
    ("a_bumped_uniform",  "A — Bumped Uniform",     draw_strip_a),
    ("b_corner_badge",    "B — Big + Corner Badge", draw_strip_b),
    ("c_horizontal_pill", "C — Horizontal Pills",   draw_strip_c),
    ("d_tile_cards",      "D — Tile Cards",         draw_strip_d),
    ("e_bold_outlined",   "E — Bold Outlined",      draw_strip_e),
]


# ── full screen ──────────────────────────────────────────────────────────────

def render_run_summary(strip_drawer, world, best=42, new_best=False):
    """Reproduce the in-game draw_stats layout from scratch but with
    the variant's power-up strip in place of the live one. Returns a
    720x1280 surface (2x upscale)."""
    surf = pygame.Surface((W, H))
    surf.fill(NEAR_BLACK)
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((*_NIGHT_DEEP, 190))
    surf.blit(dim, (0, 0))
    rng = random.Random(42)
    stars = [(rng.randint(0, W), rng.randint(0, int(H * 0.7)),
              rng.random(), rng.random() * math.tau)
             for _ in range(60)]
    _draw_overlay_stars(surf, stars, 0.5)
    _draw_mountain_silhouette(surf, alpha=160)

    _outlined_text(surf, "RUN  SUMMARY", (W // 2, 56),
                   size=34, px=3, shadow_offset=(3, 5))

    plaque = pygame.Rect(18, 104, W - 36, 156)
    _score_plaque(surf, plaque, world.score, best, new_best)

    mins = int(world.time_alive) // 60
    secs = int(world.time_alive) % 60
    time_str = f"{mins}:{secs:02d}" if mins else f"{secs}s"
    coins_encountered = max(0, world.coins_spawned - len(world.coins))
    coins_pct = (round(world.coin_count / coins_encountered * 100)
                 if coins_encountered > 0 else None)
    coins_sub = f"{coins_pct}%" if coins_pct is not None else None
    tiles = [
        ("time",   time_str,                       "TIME",    None),
        ("coin",   str(world.coin_count),          "COINS",   coins_sub),
        ("pillar", str(world.pillars_passed),      "PILLARS", None),
        ("flap",   str(world.flap_count),          "FLAPS",   None),
    ]
    tile_w = 78
    tile_h = 104
    tile_gap = 8
    total_w = len(tiles) * tile_w + (len(tiles) - 1) * tile_gap
    start_x = (W - total_w) // 2
    tile_y = 282
    for i, (kind, val, lbl, sub) in enumerate(tiles):
        r = pygame.Rect(start_x + i * (tile_w + tile_gap), tile_y,
                        tile_w, tile_h)
        _stat_tile_chunky(surf, r, kind, val, lbl, subline=sub)

    pu = [(k, c) for k, c in world.powerups_picked.items() if c > 0]
    if pu:
        strip_drawer(surf, pu, cap_y=414)

    _pill_btn(surf, (W // 2, 568), "PLAY  AGAIN",
              size=22, alpha=255, min_width=240, primary=True)
    _outline_pill_btn(surf, (W // 2, 618), "MAIN MENU",
                      size=14, min_width=130)

    big = pygame.transform.smoothscale(surf, (W * SCALE, H * SCALE))
    return big


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    world = FakeWorld()
    images = []
    for slug, label, drawer in VARIANTS:
        img = render_run_summary(drawer, world)
        path = os.path.join(OUT_DIR, f"powerup_{slug}.png")
        pygame.image.save(img, path)
        print(f"wrote {path}")
        images.append((label, img))

    # Contact sheet — five 720x1280 panes side-by-side, downscaled so
    # the file weighs <300 KB. Top strip carries the variant label.
    n = len(images)
    pane_w = W * SCALE
    pane_h = H * SCALE
    header_h = 56
    gap = 8
    sheet_w = n * pane_w + (n - 1) * gap
    sheet_h = pane_h + header_h
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(NEAR_BLACK)
    for i, (label, img) in enumerate(images):
        x = i * (pane_w + gap)
        tf = pygame.font.Font(None, 36).render(label, True, _GOLD_BRIGHT)
        sheet.blit(tf, tf.get_rect(center=(x + pane_w // 2, header_h // 2)))
        sheet.blit(img, (x, header_h))
    target_w = 2400
    if sheet_w > target_w:
        new_h = int(sheet_h * (target_w / sheet_w))
        sheet = pygame.transform.smoothscale(sheet, (target_w, new_h))
    contact = os.path.join(OUT_DIR, "powerup_contact_sheet.png")
    pygame.image.save(sheet, contact)
    print(f"wrote {contact}")


if __name__ == "__main__":
    main()
