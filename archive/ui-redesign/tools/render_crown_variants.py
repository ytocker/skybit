"""Render 5 variant crown designs that all live inside the original
24 × 28 bbox so the crown isn't any wider than the live game's version.
Pick one to wire into _crown_draw_e3_narrow.

Output:
  docs/screenshots/menu_variants/crown_v1_compact.png    5 peaks, mild outer lean
  docs/screenshots/menu_variants/crown_v2_steep.png      5 peaks, steep outer lean
  docs/screenshots/menu_variants/crown_v3_spikes.png     3 peaks + 2 slim diagonal spikes
  docs/screenshots/menu_variants/crown_v4_tiered.png     3 tall peaks + 2 short leaning peaks
  docs/screenshots/menu_variants/crown_v5_flames.png     3 peaks + 2 leaf/flame diagonals
  docs/screenshots/menu_variants/crown_compare.png       5-up labelled strip on a leaderboard row

Run from the repo root:

    PYTHONPATH=. python tools/render_crown_variants.py
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))


# ── Shared scaffolding (aura / band / sheen / central gem) ──────────────────

def _scaffold(big, s, central_ruby=True):
    from game.hud import (
        _crown_aura, _crown_band, _crown_sheen, _crown_outlined_gem,
        _CROWN_RUBY, _CROWN_RUBY_HI,
    )
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2
    _crown_aura(big, cx, bh - 9 * s,
                radii=[9 * s, 6 * s, 4 * s],
                alphas=[40, 65, 95])
    band_h = 6 * s
    band_top = bh - band_h
    band_bot = bh
    band_l = 1 * s
    band_r = bw - 1 * s
    _crown_band(big, s, band_l, band_top, band_r, band_bot)
    _crown_sheen(big, s, band_top, band_bot, band_l, band_r)
    if central_ruby:
        band_cy = (band_top + band_bot) // 2
        _crown_outlined_gem(big, cx, band_cy, int(1.2 * s),
                            _CROWN_RUBY, _CROWN_RUBY_HI)
    return cx, band_top, band_h


def _sparkles(big, s):
    from game.hud import _CROWN_WHITE_HI
    bw, bh = big.get_width(), big.get_height()
    cx_pix = bw // 2
    cy_pix = bh // 2
    for x_frac, y_frac in [(-0.85, -0.55), (0.85, -0.55),
                            (-0.70,  0.25), (0.70,  0.25)]:
        sx = int(cx_pix + x_frac * (bw // 2))
        sy = int(cy_pix + y_frac * (bh // 2))
        sx = max(2, min(bw - 2, sx))
        sy = max(2, min(bh - 2, sy))
        pygame.draw.line(big, _CROWN_WHITE_HI,
                         (sx - int(1.5 * s), sy),
                         (sx + int(1.5 * s), sy),
                         max(1, s // 2))
        pygame.draw.line(big, _CROWN_WHITE_HI,
                         (sx, sy - int(1.5 * s)),
                         (sx, sy + int(1.5 * s)),
                         max(1, s // 2))


def _peak_triangle(big, s, base_x, base_pw, tip_x, tip_y, gem_col, gem_hi,
                   gem_half_w=1.3):
    from game.hud import (
        _crown_outlined_polygon, _CROWN_GOLD, _CROWN_GOLD_HI, _CROWN_WHITE_HI,
    )
    l = (base_x - base_pw, big.get_height() - 6 * s)
    r = (base_x + base_pw, big.get_height() - 6 * s)
    tip = (tip_x, tip_y)
    _crown_outlined_polygon(big, [tip, l, r], _CROWN_GOLD, _CROWN_GOLD_HI)
    gem_top   = (tip_x, tip_y - int(2.5 * s))
    gem_bot   = (tip_x, tip_y - int(0.3 * s))
    gem_left  = (tip_x - int(gem_half_w * s), tip_y - int(1.4 * s))
    gem_right = (tip_x + int(gem_half_w * s), tip_y - int(1.4 * s))
    _crown_outlined_polygon(big, [gem_top, gem_right, gem_bot, gem_left],
                            gem_col, gem_hi)
    pygame.draw.line(big, _CROWN_WHITE_HI,
                     (gem_top[0] - 1, gem_top[1] + 1),
                     (gem_top[0] - 1, gem_top[1] + int(1.5 * s)),
                     max(1, s // 2))


# ── V1 · compact 5-peak with mild outer lean ────────────────────────────────

def draw_v1_compact(big, s):
    from game.hud import (
        _CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI, _CROWN_RUBY, _CROWN_RUBY_HI,
    )
    cx, band_top, band_h = _scaffold(big, s)
    bh = big.get_height()
    peak_h = bh - band_h - 5 * s
    tip_y = band_top - peak_h

    peak_xs    = [cx - 9 * s, cx - 5 * s, cx, cx + 5 * s, cx + 9 * s]
    tip_dx     = [-2 * s, 0, 0, 0, 2 * s]
    pw         = max(2, int(0.9 * s))
    gem_w      = 0.9
    cols       = [(_CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI),
                  (_CROWN_RUBY,     _CROWN_RUBY_HI),
                  (_CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI),
                  (_CROWN_RUBY,     _CROWN_RUBY_HI),
                  (_CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI)]
    for px, dx, (gc, gh) in zip(peak_xs, tip_dx, cols):
        _peak_triangle(big, s, px, pw, px + dx, tip_y, gc, gh, gem_w)
    _sparkles(big, s)


# ── V2 · steep outer lean ───────────────────────────────────────────────────

def draw_v2_steep(big, s):
    from game.hud import (
        _CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI, _CROWN_RUBY, _CROWN_RUBY_HI,
    )
    cx, band_top, band_h = _scaffold(big, s)
    bh = big.get_height()
    peak_h = bh - band_h - 5 * s
    tip_y = band_top - peak_h

    peak_xs    = [cx - 8 * s, cx - 4 * s, cx, cx + 4 * s, cx + 8 * s]
    tip_dx     = [-3 * s, 0, 0, 0, 3 * s]
    pw         = max(2, int(0.9 * s))
    gem_w      = 0.85
    cols       = [(_CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI),
                  (_CROWN_RUBY,     _CROWN_RUBY_HI),
                  (_CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI),
                  (_CROWN_RUBY,     _CROWN_RUBY_HI),
                  (_CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI)]
    for px, dx, (gc, gh) in zip(peak_xs, tip_dx, cols):
        _peak_triangle(big, s, px, pw, px + dx, tip_y, gc, gh, gem_w)
    _sparkles(big, s)


# ── V3 · 3 vertical peaks + 2 outer slim diagonal spikes ────────────────────

def draw_v3_spikes(big, s):
    from game.hud import (
        _crown_outlined_polygon, _CROWN_GOLD, _CROWN_GOLD_HI,
        _CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI, _CROWN_RUBY, _CROWN_RUBY_HI,
        _CROWN_WHITE_HI,
    )
    cx, band_top, band_h = _scaffold(big, s)
    bh = big.get_height()
    peak_h = bh - band_h - 5 * s
    tip_y = band_top - peak_h

    # 3 vertical main peaks
    cols = [(_CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI),
            (_CROWN_RUBY,     _CROWN_RUBY_HI),
            (_CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI)]
    for px, (gc, gh) in zip([cx - 6 * s, cx, cx + 6 * s], cols):
        _peak_triangle(big, s, px, max(2, int(1.4 * s)),
                       px, tip_y, gc, gh, 1.2)

    # 2 outer slim diagonal SPIKES — no gems, narrower body, leans 4s
    spike_pw = max(1, s // 2)
    for sign in (-1, 1):
        base_x = cx + sign * 10 * s
        tip_xx = cx + sign * 13 * s
        tip_yy = tip_y + int(2 * s)   # spikes a touch shorter
        l = (base_x - spike_pw, band_top)
        r = (base_x + spike_pw, band_top)
        _crown_outlined_polygon(big, [(tip_xx, tip_yy), l, r],
                                _CROWN_GOLD, _CROWN_GOLD_HI)

    _sparkles(big, s)


# ── V4 · 3 tall vertical + 2 shorter outer leaning peaks ────────────────────

def draw_v4_tiered(big, s):
    from game.hud import (
        _CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI, _CROWN_RUBY, _CROWN_RUBY_HI,
    )
    cx, band_top, band_h = _scaffold(big, s)
    bh = big.get_height()
    full_peak_h = bh - band_h - 5 * s
    short_peak_h = int(full_peak_h * 0.62)
    full_tip_y = band_top - full_peak_h
    short_tip_y = band_top - short_peak_h

    # 3 vertical tall main peaks
    cols = [(_CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI),
            (_CROWN_RUBY,     _CROWN_RUBY_HI),
            (_CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI)]
    for px, (gc, gh) in zip([cx - 6 * s, cx, cx + 6 * s], cols):
        _peak_triangle(big, s, px, max(2, int(1.4 * s)),
                       px, full_tip_y, gc, gh, 1.2)

    # 2 outer shorter peaks, leaning outward, with smaller sapphire gems
    for sign in (-1, 1):
        base_x = cx + sign * 9 * s
        tip_xx = cx + sign * 11 * s
        _peak_triangle(big, s, base_x, max(2, int(1.0 * s)),
                       tip_xx, short_tip_y,
                       _CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI, 0.7)

    _sparkles(big, s)


# ── V5 · 3 vertical peaks + 2 outer leaf/flame diagonals ────────────────────

def draw_v5_flames(big, s):
    from game.hud import (
        _crown_outlined_polygon, _CROWN_GOLD, _CROWN_GOLD_HI,
        _CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI, _CROWN_RUBY, _CROWN_RUBY_HI,
        _CROWN_WHITE_HI,
    )
    cx, band_top, band_h = _scaffold(big, s)
    bh = big.get_height()
    peak_h = bh - band_h - 5 * s
    tip_y = band_top - peak_h

    # 3 vertical main peaks
    cols = [(_CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI),
            (_CROWN_RUBY,     _CROWN_RUBY_HI),
            (_CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI)]
    for px, (gc, gh) in zip([cx - 6 * s, cx, cx + 6 * s], cols):
        _peak_triangle(big, s, px, max(2, int(1.4 * s)),
                       px, tip_y, gc, gh, 1.2)

    # Two outer LEAF / FLAME shapes — quadrilateral that curves outward
    # from the band's outer end to a slimmer outer-leaning tip.
    for sign in (-1, 1):
        base_inner_x = cx + sign * 8 * s
        base_outer_x = cx + sign * 10 * s
        bend_x       = cx + sign * 12 * s
        tip_x        = cx + sign * 11 * s
        tip_yy       = tip_y + int(1 * s)
        bend_y       = band_top - peak_h // 2
        # Outer leaf: band → outer bend → tip → inner bend
        pts = [
            (base_inner_x, band_top),
            (base_outer_x, band_top),
            (bend_x, bend_y),
            (tip_x, tip_yy),
        ]
        _crown_outlined_polygon(big, pts, _CROWN_GOLD, _CROWN_GOLD_HI)

    _sparkles(big, s)


# ── Main ─────────────────────────────────────────────────────────────────────

VARIANTS = [
    ("crown_v1_compact", "V1 · compact",  draw_v1_compact),
    ("crown_v2_steep",   "V2 · steep",    draw_v2_steep),
    ("crown_v3_spikes",  "V3 · spikes",   draw_v3_spikes),
    ("crown_v4_tiered",  "V4 · tiered",   draw_v4_tiered),
    ("crown_v5_flames",  "V5 · flames",   draw_v5_flames),
]

UPSCALE = 14   # for the isolated zoom; final composite uses smoothscale


def render_isolated(draw_fn, slug):
    pygame.init()
    pygame.font.init()
    import game.hud as h
    bw, bh = 24, 28
    big = pygame.Surface((bw * h._CROWN_OS, bh * h._CROWN_OS), pygame.SRCALPHA)
    draw_fn(big, h._CROWN_OS)
    big2 = pygame.transform.scale(big, (big.get_width() * UPSCALE,
                                         big.get_height() * UPSCALE))
    canvas = pygame.Surface((big2.get_width() + 60, big2.get_height() + 60))
    canvas.fill((30, 20, 50))
    canvas.blit(big2, (30, 30))
    out_dir = os.path.join("docs", "screenshots", "menu_variants")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{slug}.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas.get_width()}x{canvas.get_height()})")
    return canvas


def render_on_badge(draw_fn):
    """Render the variant on a sample rank-1 leaderboard row."""
    import game.hud as h
    from game.config import W
    bw, bh = 24, 28
    big = pygame.Surface((bw * h._CROWN_OS, bh * h._CROWN_OS), pygame.SRCALPHA)
    draw_fn(big, h._CROWN_OS)
    small = pygame.transform.smoothscale(big, (bw, bh))
    crown_with_shadow = h._crown_with_shadow(small)

    # Mini row: gold gradient pill with a #1 badge + this crown
    row_h = 42
    row_radius = row_h // 2
    pnl = h._medal_row_pill(W - 28, row_h, row_radius, 1)
    canvas = pygame.Surface((W, row_h + 50), pygame.SRCALPHA)
    canvas.fill((22, 14, 40))
    canvas.blit(pnl, (14, 25))

    badge_cx = 14 + 24
    row_cy = 25 + row_h // 2
    pygame.draw.circle(canvas, h._GOLD_BRIGHT, (badge_cx, row_cy), 13)
    pygame.draw.circle(canvas, (32, 24, 8), (badge_cx, row_cy), 13, 1)
    nf = h._font(13, True).render("1", True, (32, 24, 8))
    canvas.blit(nf, nf.get_rect(center=(badge_cx, row_cy)))

    c_w, c_h = crown_with_shadow.get_size()
    canvas.blit(crown_with_shadow,
                (badge_cx - c_w // 2, row_cy - 7 - c_h))
    return canvas


def main():
    pygame.init()
    pygame.font.init()

    from game.config import W, H
    pygame.display.set_mode((W, H))

    isolated_frames = []
    row_frames = []
    for slug, label, fn in VARIANTS:
        iso = render_isolated(fn, slug)
        isolated_frames.append((slug, label, iso))
        row_frames.append((slug, label, render_on_badge(fn)))

    # Compose comparison strip: each variant gets its isolated zoom +
    # a real leaderboard-row sample below, in a column. 5 columns wide.
    iso_w, iso_h = isolated_frames[0][2].get_size()
    row_w, row_h = row_frames[0][2].get_size()
    GAP = 24
    LABEL_H = 56
    PAD = 32
    cell_w = max(iso_w, row_w)
    cell_h = iso_h + 24 + row_h
    n = len(VARIANTS)
    canvas_w = cell_w * n + GAP * (n - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((18, 14, 32))
    font = pygame.font.SysFont(None, 48, bold=True)
    for i, ((_slug, label, iso), (_, _, row)) in enumerate(
            zip(isolated_frames, row_frames)):
        x = PAD + i * (cell_w + GAP)
        y = PAD
        canvas.blit(iso, (x + (cell_w - iso_w) // 2, y))
        canvas.blit(row, (x + (cell_w - row_w) // 2, y + iso_h + 24))
        lbl = font.render(label, True, (240, 210, 130))
        canvas.blit(lbl, (x + (cell_w - lbl.get_width()) // 2,
                          y + cell_h + 12))

    out_dir = os.path.join("docs", "screenshots", "menu_variants")
    cmp_path = os.path.join(out_dir, "crown_compare.png")
    pygame.image.save(canvas, cmp_path)
    print(f"saved {cmp_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    sys.exit(main() or 0)
